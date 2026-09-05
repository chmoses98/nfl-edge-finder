"""Concise football profiles for the handicap packet.

Two layers, kept apart because they answer different questions and have different reliability:

  ADJUSTED   opponent-adjusted, ridge-shrunk, recency-weighted ratings from nfl_edge.research.team_ratings.
             Leakage-free by construction (only games strictly before the snapshot week). This is the layer
             to reason from.
  RAW        unadjusted season and recent-form splits. Useful for describing what actually happened, and
             deliberately labelled raw so nobody mistakes a soft schedule for a good offence.

A hard honesty constraint drives the design: **at Week 1 there is no current-season football.** No 2026 snap
has been played, so every profile is 2025-based. The packet says so in `basis` rather than presenting a prior
season as current form, and `recent` is null rather than silently falling back to the same season number.
Tiny-sample overreaction is handled the same way -- a split with fewer than MIN_GAMES games is reported as
null, not as a number with a caveat nobody reads.
"""
from __future__ import annotations

import glob
import os

import polars as pl

from nfl_edge.research import team_ratings as TR

MIN_GAMES = 4                 # below this a split is not reported at all
RECENT_GAMES = 6

# Raw descriptive columns surfaced per side. Chosen for handicapping value, not completeness.
OFF_COLS = [
    "off_epa_play", "off_success_rate", "off_dropback_epa", "off_rush_epa", "off_early_down_epa",
    "off_epa_play_ng", "off_proe_early_ng", "off_rz_epa", "off_cpoe", "off_adot",
    "off_no_huddle_rate", "off_shotgun_rate",
]
DEF_COLS = [
    "def_epa_play", "def_success_rate", "def_dropback_epa", "def_rush_epa", "def_early_down_epa",
    "def_epa_play_ng", "def_rz_epa",
]


def _load_team_game(root: str, seasons) -> pl.DataFrame:
    frames = []
    for s in seasons:
        p = os.path.join(root, "data", "silver", f"team_game_{s}.parquet")
        if os.path.exists(p):
            frames.append(pl.read_parquet(p))
    if not frames:
        return pl.DataFrame()
    return pl.concat(frames, how="diagonal_relaxed")


def _derived(tg: pl.DataFrame) -> pl.DataFrame:
    """Rates the silver table stores as counts. Guarded against zero denominators."""
    return tg.with_columns([
        ((pl.col("off_explosive_passes") + pl.col("off_explosive_runs"))
         / pl.col("off_plays").clip(1)).alias("off_explosive_rate"),
        ((pl.col("def_explosive_passes") + pl.col("def_explosive_runs"))
         / pl.col("def_plays").clip(1)).alias("def_explosive_rate"),
        (pl.col("off_sacks") / pl.col("off_dropbacks").clip(1)).alias("off_sack_rate_allowed"),
        (pl.col("def_sacks") / pl.col("def_dropbacks").clip(1)).alias("def_sack_rate"),
        (pl.col("def_qb_hits") / pl.col("def_dropbacks").clip(1)).alias("def_qb_hit_rate"),
        (pl.col("off_turnovers") / pl.col("off_plays").clip(1)).alias("off_turnover_rate"),
        (pl.col("def_turnovers") / pl.col("def_plays").clip(1)).alias("def_takeaway_rate"),
        (pl.col("td_drives") / pl.col("n_drives").clip(1)).alias("off_td_drive_rate"),
        (pl.col("off_plays") / pl.col("n_drives").clip(1)).alias("off_plays_per_drive"),
    ])


RATE_COLS = ["off_explosive_rate", "def_explosive_rate", "off_sack_rate_allowed", "def_sack_rate",
             "def_qb_hit_rate", "off_turnover_rate", "def_takeaway_rate", "off_td_drive_rate",
             "off_plays_per_drive"]


def _split(tg: pl.DataFrame, cols: list) -> dict:
    """Mean of each column over the given rows, or None when the sample is too small to mean anything."""
    if tg.height < MIN_GAMES:
        return {"n_games": tg.height, "insufficient_sample": True}
    out = {"n_games": tg.height, "insufficient_sample": False}
    for c in cols:
        if c in tg.columns:
            v = tg[c].mean()
            out[c] = None if v is None else round(float(v), 5)
    return out


def build_profiles(root: str, season: int, week: int, lookback_seasons: int = 3) -> dict:
    """team -> profile. Uses only games strictly before (season, week)."""
    seasons = list(range(season - lookback_seasons, season + 1))
    tg = _load_team_game(root, seasons)
    if tg.is_empty():
        return {"_meta": {"basis": "NO_DATA", "adjusted_available": False}}
    tg = _derived(tg)
    prior = tg.filter((pl.col("season") < season) | ((pl.col("season") == season) & (pl.col("week") < week)))
    if prior.is_empty():
        return {"_meta": {"basis": "NO_PRIOR_GAMES", "adjusted_available": False}}

    # The most recent season that actually has completed games. At Week 1 this is the PRIOR season, and the
    # packet must not present it as current form.
    cur = int(prior["season"].max())
    cur_rows = prior.filter(pl.col("season") == cur)
    basis_season = cur
    basis = "current_season" if cur == season else f"prior_season_{cur}_no_games_played_in_{season}"

    # opponent-adjusted ratings from the validated solver (ridge + recency + HFA, leakage-free)
    adjusted = {}
    try:
        rows = TR.prepare_rows(tg)
        snap = TR.snapshot_ratings(rows, season=season, week=week)
        if snap is not None and not snap.is_empty():
            for r in snap.to_dicts():
                adjusted[r["team"]] = {k: (None if v is None else round(float(v), 5))
                                       for k, v in r.items() if k not in ("team", "season", "week")}
    except Exception as e:                                   # never let a ratings failure kill the packet
        adjusted = {}
        basis += f" (adjusted ratings unavailable: {type(e).__name__})"

    profiles = {}
    all_cols = OFF_COLS + DEF_COLS + RATE_COLS
    for team in sorted(set(prior["team"].to_list())):
        t_cur = cur_rows.filter(pl.col("team") == team).sort(["season", "week"])
        t_all = prior.filter(pl.col("team") == team).sort(["season", "week"])
        profiles[team] = {
            "team": team,
            "basis": basis,
            "basis_season": basis_season,
            "season_split": _split(t_cur, all_cols),
            "recent_split": _split(t_cur.tail(RECENT_GAMES), all_cols) if t_cur.height >= MIN_GAMES else
                            {"n_games": min(t_cur.height, RECENT_GAMES), "insufficient_sample": True},
            "long_baseline": _split(t_all.tail(34), all_cols),
            "adjusted": adjusted.get(team),
        }
    profiles["_meta"] = {
        "basis": basis,
        "basis_season": basis_season,
        "adjusted_available": bool(adjusted),
        "min_games_for_a_split": MIN_GAMES,
        "recent_window_games": RECENT_GAMES,
        "note": ("Adjusted ratings are opponent-adjusted, ridge-shrunk and recency-weighted using only games "
                 "before the snapshot week. Raw splits are unadjusted and describe what happened, not how "
                 "good a team is."),
    }
    return profiles


def league_ranks(profiles: dict, key: str, split: str = "season_split", higher_is_better: bool = True) -> dict:
    """team -> 1-based rank on one metric. Ranks make a raw EPA number legible at a glance."""
    vals = []
    for t, p in profiles.items():
        if t == "_meta" or not isinstance(p, dict):
            continue
        v = (p.get(split) or {}).get(key)
        if v is not None:
            vals.append((t, v))
    vals.sort(key=lambda x: -x[1] if higher_is_better else x[1])
    return {t: i + 1 for i, (t, _) in enumerate(vals)}


# ======================================================================================================
# quarterback profiles
# ======================================================================================================

QB_MIN_DROPBACKS = 100          # below this, per-dropback rates are noise dressed as measurement


def build_qb_profiles(root: str, season: int, week: int, lookback_seasons: int = 2) -> dict:
    """gsis_id -> quarterback profile from play-by-play, using only plays before (season, week).

    Split into pressure and clean-pocket performance because they are different skills and the market
    prices them differently when an offensive line changes. Rates below QB_MIN_DROPBACKS dropbacks are
    returned as null: a 40-dropback CPOE is not a measurement.
    """
    import polars as pl  # local import keeps the module importable without a pbp corpus present

    frames = []
    for s in range(season - lookback_seasons, season + 1):
        p = os.path.join(root, "data", "raw", "nflverse", "pbp", f"play_by_play_{s}.parquet")
        if not os.path.exists(p):
            continue
        cols = ["season", "week", "passer_player_id", "passer_player_name", "posteam", "qb_dropback",
                "qb_epa", "epa", "success", "cpoe", "complete_pass", "air_yards", "sack", "interception",
                "qb_hit", "rush", "yards_gained", "touchdown", "pass"]
        lf = pl.scan_parquet(p)
        have = [c for c in cols if c in lf.collect_schema().names()]
        frames.append(lf.select(have).collect())
    if not frames:
        return {"_meta": {"available": False, "reason": "no play-by-play found"}}
    pbp = pl.concat(frames, how="diagonal_relaxed")
    pbp = pbp.filter((pl.col("season") < season) | ((pl.col("season") == season) & (pl.col("week") < week)))
    db = pbp.filter((pl.col("qb_dropback") == 1) & pl.col("passer_player_id").is_not_null())
    if db.is_empty():
        return {"_meta": {"available": False, "reason": "no dropbacks before this week"}}

    latest = int(db["season"].max())
    db = db.filter(pl.col("season") == latest)

    def agg(frame):
        return frame.group_by("passer_player_id").agg([
            pl.len().alias("dropbacks"),
            pl.first("passer_player_name").alias("name"),
            pl.last("posteam").alias("team"),
            pl.mean("qb_epa").alias("epa_per_dropback"),
            pl.mean("success").alias("success_rate"),
            pl.mean("cpoe").alias("cpoe"),
            pl.mean("air_yards").alias("adot"),
            (pl.col("sack").sum() / pl.len()).alias("sack_rate"),
            (pl.col("interception").sum() / pl.len()).alias("int_rate"),
            (pl.col("qb_hit").sum() / pl.len()).alias("pressure_rate_proxy"),
            (pl.col("air_yards").ge(20).sum() / pl.len()).alias("deep_rate"),
        ])

    overall = agg(db)
    pressured = agg(db.filter((pl.col("qb_hit") == 1) | (pl.col("sack") == 1)))
    clean = agg(db.filter((pl.col("qb_hit") != 1) & (pl.col("sack") != 1)))
    recent = agg(db.sort(["season", "week"]).group_by("passer_player_id").tail(200))

    scrambles = pbp.filter((pl.col("rush") == 1) & pl.col("passer_player_id").is_not_null()) \
        .group_by("passer_player_id").agg([pl.len().alias("qb_rushes"),
                                           pl.mean("yards_gained").alias("qb_rush_ypc")]) \
        if "rush" in pbp.columns else None

    def as_map(frame, keep):
        out = {}
        if frame is None or frame.is_empty():
            return out
        for r in frame.to_dicts():
            out[r["passer_player_id"]] = {k: (None if r.get(k) is None else round(float(r[k]), 5))
                                          for k in keep if k in r}
        return out

    rate_keys = ["epa_per_dropback", "success_rate", "cpoe", "adot", "sack_rate", "int_rate",
                 "pressure_rate_proxy", "deep_rate"]
    o_map, p_map, c_map, r_map = (as_map(overall, rate_keys), as_map(pressured, rate_keys),
                                  as_map(clean, rate_keys), as_map(recent, rate_keys))
    scr = as_map(scrambles, ["qb_rushes", "qb_rush_ypc"])

    counts = {r["passer_player_id"]: (r["dropbacks"], r["name"], r["team"]) for r in overall.to_dicts()}
    prof = {}
    for pid, (n, name, team) in counts.items():
        thin = n < QB_MIN_DROPBACKS
        prof[pid] = {
            "player_id": pid, "name": name, "team": team,
            "basis_season": latest,
            "dropbacks": int(n),
            "insufficient_sample": thin,
            "overall": None if thin else o_map.get(pid),
            "under_pressure": None if thin else p_map.get(pid),
            "clean_pocket": None if thin else c_map.get(pid),
            "recent_200_dropbacks": None if thin else r_map.get(pid),
            "rushing": scr.get(pid),
        }
    prof["_meta"] = {
        "available": True, "basis_season": latest, "min_dropbacks": QB_MIN_DROPBACKS,
        "note": ("Rates come from the most recent season with completed games. At week 1 that is the PRIOR "
                 "season; a quarterback on a new team carries his old context with him and the packet does "
                 "not adjust for that."),
    }
    return prof
