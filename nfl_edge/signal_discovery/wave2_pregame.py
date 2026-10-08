"""Wave-2 pregame features for upcoming NFL games: the Wave-1 builders, run with PHANTOM rows. RESEARCH ONLY.

Market-blind and outcome-blind. For the week's upcoming games this reproduces, at a cutoff before kickoff:

* the Wave-1 game rows (`game_features.game_rows`, the frozen 2026 lambdas of the Wave-1 manifest; the snapshot
  reads only earlier weeks, exactly as in Wave 1);
* the Wave-1 player rows (`player_features.build`): `nfl_edge.sim.features` with priors fitted on 2012-2015 only,
  the team-perspective context (`CONTEXT_MAP`), `_role_stability` (unchanged; its injury input is the newest
  injury-report vintage at or before the cutoff), and `evaluate_props.add_baselines`.

A phantom row is a player the repository's own eligibility rule (`features.eligible_players`: active roster or depth
chart at a skill position, not Out/Doubtful on the vintage report) puts in the game. Its features come from strictly
earlier games only -- the row itself is masked inside `decayed_prior_sums` and has no outcome to read.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import polars as pl

from nfl_edge.signal_discovery import evaluate_props as EP
from nfl_edge.signal_discovery import game_features as G
from nfl_edge.signal_discovery import player_features as P
from nfl_edge.sim import data as D
from nfl_edge.sim import features as F

ROOT = Path(__file__).resolve().parents[2]
W1_MANIFEST = ROOT / "research" / "signal_discovery_wave1" / "game_features_manifest.json"


def frozen_lambdas(season: int) -> dict[str, float]:
    return json.loads(W1_MANIFEST.read_text())["lambdas"][str(season)]


def game_rows(season: int, week: int, game_ids: list[str], mt: pd.DataFrame | None = None) -> pd.DataFrame:
    """Wave-1 game rows for the listed games (snapshot on weeks < `week`)."""
    if mt is None:
        mt = G.metric_table(range(2012, season + 1))
    sched = pd.DataFrame(D.schedule().to_dicts())
    wk = sched[(sched["season"] == season) & (sched["week"] == week) & (sched["game_id"].isin(game_ids))]
    return G.game_rows(mt, wk, [season], {season: frozen_lambdas(season)})


def _kickoffs(sched: pd.DataFrame) -> pd.Series:
    t = sched["gametime"].fillna("13:00")
    return pd.to_datetime(sched["gameday"] + " " + t).dt.tz_localize("America/New_York").dt.tz_convert("UTC")


def _injury_frame(path: str | None, season: int) -> pd.DataFrame:
    if not path:
        return pd.DataFrame(columns=["season", "week", "gsis_id", "team", "report_status"])
    i = pl.read_parquet(path, columns=["season", "week", "gsis_id", "team", "report_status"]).filter(pl.col("gsis_id").is_not_null())
    return pd.DataFrame(i.to_dicts())


def player_rows(
    season: int,
    week: int,
    game_rows_df: pd.DataFrame,
    cutoff: datetime,
    market_data: str | None,
    families: list[dict],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Phantom player rows for the games in `game_rows_df`, with Wave-1 features, role and baselines."""
    from nfl_edge.sim.prospective import injury_vintage

    sched = pd.DataFrame(D.schedule().to_dicts())
    sched["kickoff"] = _kickoffs(sched)
    games = sched[sched["game_id"].isin(game_rows_df["game_id"])]
    done = sched[sched["home_score"].notna() & (sched["kickoff"] + pd.Timedelta(hours=4) <= cutoff)]
    ok_games = set(done["game_id"])
    seasons = list(P.PRIOR_SEASONS) + [s for s in P.PLAYER_SEASONS if s <= season]
    priors_t = pd.DataFrame(D.load("team_games", P.PRIOR_SEASONS).to_dicts())
    priors_p = pd.DataFrame(D.load("player_games", P.PRIOR_SEASONS).to_dicts())
    priors = F.fit_priors(priors_t, priors_p, fit_seasons=P.PRIOR_SEASONS)
    tg = pd.DataFrame(D.load("team_games", seasons).to_dicts())
    pg = pd.DataFrame(D.load("player_games", seasons).to_dicts())
    tg = tg[tg["game_id"].isin(ok_games)]
    pg = pg[pg["game_id"].isin(ok_games)]
    ph_team = []
    for r in games.itertuples():
        for team, opp, home in ((r.home_team, r.away_team, True), (r.away_team, r.home_team, False)):
            ph_team.append({"game_id": r.game_id, "team": team, "opp": opp, "home": home, "season": season, "week": week,
                            "season_type": "REG", "home_team": r.home_team, "away_team": r.away_team})
    tf = F.team_features(pd.concat([tg, pd.DataFrame(ph_team)], ignore_index=True, sort=False), F.FEATURE_CONFIG, priors)
    # eligibility (the repository's rule, point-in-time inputs)
    depth = F.depth_chart(season, cutoff=cutoff)
    roster = F.weekly_roster(season, week)
    inj_path, inj_row, inj_why = injury_vintage(D.ROOT, season, cutoff, extra_roots=(market_data,) if market_data else ())
    inj = F.injury_designations(season, week, root=inj_path) if inj_path else pd.DataFrame(
        columns=["player_id", "report_status", "practice_status"])
    elig = []
    for r in games.itertuples():
        for team in (r.home_team, r.away_team):
            e = F.eligible_players(season, week, team, depth=depth, roster=roster, injuries=inj)
            if e.empty:
                continue
            e["game_id"], e["season"], e["week"] = r.game_id, season, week
            elig.append(e)
    elig_df = pd.concat(elig, ignore_index=True) if elig else pd.DataFrame(columns=["game_id", "team", "player_id", "position", "season", "week"])
    pf = F.player_features(pg, tg, F.FEATURE_CONFIG, phantom_rows=elig_df, priors=priors)
    pf.loc[pf["phantom"], "season_type"] = "REG"
    pf = pf[pf["season"].isin(P.PLAYER_SEASONS) & pf["position"].isin(P.POSITIONS) & (pf["season_type"] == "REG")].copy()
    team_cols = ["game_id", "team"] + [c for c in tf.columns if c.startswith(("off_", "def_")) and not c.startswith("off_td")]
    pf = pf.merge(tf[team_cols].drop_duplicates(["game_id", "team"]), on=["game_id", "team"], how="left")
    # team-perspective game context, exactly as player_features.build attaches it (market-blind)
    gf = game_rows_df.set_index("game_id")
    ctx: dict[str, list] = {k: [] for k in P.CONTEXT_MAP}
    script, home_flag = [], []
    for gid, team in zip(pf["game_id"], pf["team"], strict=False):
        if gid not in gf.index:
            for k in P.CONTEXT_MAP:
                ctx[k].append(np.nan)
            script.append(np.nan)
            home_flag.append(np.nan)
            continue
        g = gf.loc[gid]
        is_home = g["home_team"] == team
        home_flag.append(bool(is_home))
        for k, (hs, as_) in P.CONTEXT_MAP.items():
            v = g[hs] if is_home else g[as_]
            ctx[k].append(np.nan if v is None else float(v))
        bm = g["baseline.home_margin"]
        script.append(np.nan if bm is None else (float(bm) if is_home else -float(bm)))
    for k, v in ctx.items():
        pf[k] = v
    pf["ctx.expected_script"] = script
    pf["ctx.is_home"] = home_flag
    # ROLE_STABILITY: the unchanged Wave-1 classifier on this season's rows; its injury input is the vintage
    cur = pf[pf["season"] == season].copy().reset_index(drop=True)
    original = P._injuries
    try:
        P._injuries = lambda s: _injury_frame(inj_path, s) if s == season else original(s)
        cur = P._role_stability(cur)
    finally:
        P._injuries = original
    # baselines over the full history of these players; phantom outcomes are unknown -> 0 placeholder for the
    # running sums (the phantom is each player's LAST row, and every baseline excludes the row itself)
    stats_cols = sorted({f["stat"] for f in families})
    hist = pf[pf["player_id"].isin(set(cur.loc[cur["phantom"], "player_id"]))].copy()
    hist = hist.merge(cur[["game_id", "player_id", "role_stability", "inj.status", "inj.teammate_out"]],
                      on=["game_id", "player_id"], how="left")
    phm = hist["phantom"].to_numpy(bool)
    for c in stats_cols:
        if c not in hist.columns:
            hist[c] = np.nan
        hist.loc[phm, c] = 0.0
    hist = EP.add_baselines(hist, families)
    out = hist[hist["phantom"]].copy()
    for c in stats_cols:
        out[c] = np.nan
    meta = {
        "cutoff": cutoff.isoformat(),
        "history_games": len(ok_games),
        "latest_history_game": max(ok_games) if ok_games else None,
        "depth_chart_vintage": depth["dc_vintage"].iloc[0] if len(depth) and "dc_vintage" in depth.columns else None,
        "injury_vintage": {"resolved": inj_path is not None, "snapshot_path": (inj_row or {}).get("snapshot_path"),
                           "sha256": (inj_row or {}).get("sha256"), "retrieved_at": (inj_row or {}).get("retrieved_at"),
                           "reason": inj_why},
        "phantom_players": len(out),
        "priors_fit_seasons": list(P.PRIOR_SEASONS),
    }
    return out.reset_index(drop=True), meta
