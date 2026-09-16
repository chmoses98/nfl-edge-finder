"""Point-in-time features for the simulation layer.

Every feature on a (subject, game) row is computed from rows STRICTLY BEFORE that game in time.  The one
primitive is ``decayed_prior_sums``: for each row it returns the exponentially decayed sums of a set of
columns over the subject's earlier rows, with the sums taken BEFORE the row's own values are added.
Rates (yards per carry, catch rate, share of team carries) are then ratios of two such sums, shrunk toward
a prior with ``k`` pseudo-observations -- an exposure-weighted estimate, so a back with 200 prior carries
is trusted more than one with 12.

The hyperparameters are named once (``FEATURE_CONFIG``) and recorded on every fitted artifact.

Depth charts, weekly rosters and injury reports are read with an explicit cutoff or week, never "latest".
"""
from __future__ import annotations

import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import polars as pl

from . import data as D

ROOT = D.ROOT
RAW = D.RAW

SKILL = ("QB", "RB", "WR", "TE", "FB")


@dataclass(frozen=True)
class FeatureConfig:
    player_halflife_short: float = 3.0     # games; recent role
    player_halflife_long: float = 10.0     # games; established role / efficiency
    player_season_carry: float = 0.5       # multiply sums at a season boundary
    team_halflife: float = 8.0
    team_season_carry: float = 0.5
    rate_shrink_k: float = 40.0            # pseudo-touches toward the position prior for per-touch rates
    share_shrink_k: float = 2.0            # pseudo-games toward the depth-rank prior for shares
    team_shrink_k: float = 4.0             # pseudo-games toward the league mean for team rates
    version: str = "features-1.0.0"

    def to_dict(self):
        return asdict(self)


FEATURE_CONFIG = FeatureConfig()
PRIORS_VERSION = "sim-priors-1.0.0"


class MissingPriors(ValueError):
    """Raised when a feature build is asked to invent its own shrinkage targets.

    Every shrinkage target is a statistic of a POPULATION, and a population that includes the games being
    predicted is a leak: a week-1 projection whose league play-volume prior was computed over the whole
    season has seen week 18.  So priors are a fitted artifact, frozen on seasons strictly before the
    evaluation period, carried on the bundle, and passed in here explicitly.  There is no default.
    """


@dataclass(frozen=True)
class PriorSet:
    """The shrinkage targets a feature build is allowed to use, fitted on rows strictly earlier than every
    row it will be applied to.

    ``team_level``   column -> league mean of that team-game level (used for own-offence AND opponent-allowed
                     columns: over the league the multiset of allowed_X equals the multiset of X).
    ``team_rate``    rate name -> pooled numerator/denominator over the fit seasons.
    ``team_den``     denominator column -> league mean, which sets how many pseudo-games the prior is worth.
    ``player_rate``  "POS|rate" -> pooled rate for that position; ``player_rate_all`` is the fallback for a
                     position the fit seasons never saw.
    """
    team_level: dict
    team_rate: dict
    team_den: dict
    player_rate: dict
    player_rate_all: dict
    fit_seasons: tuple
    version: str = PRIORS_VERSION

    def to_dict(self) -> dict:
        return {"team_level": self.team_level, "team_rate": self.team_rate, "team_den": self.team_den,
                "player_rate": self.player_rate, "player_rate_all": self.player_rate_all,
                "fit_seasons": list(self.fit_seasons), "version": self.version}

    @classmethod
    def from_dict(cls, d: dict) -> "PriorSet":
        return cls(team_level=d["team_level"], team_rate=d["team_rate"], team_den=d["team_den"],
                   player_rate=d["player_rate"], player_rate_all=d["player_rate_all"],
                   fit_seasons=tuple(d["fit_seasons"]), version=d.get("version", PRIORS_VERSION))

    def player_prior(self, position, rate: str) -> np.ndarray:
        pos = np.asarray(position, dtype=object)
        out = np.full(len(pos), float(self.player_rate_all[rate]))
        for p in np.unique(pos):
            v = self.player_rate.get(f"{p}|{rate}")
            if v is not None:
                out[pos == p] = float(v)
        return out


PLAYER_RATES = {"ypc": ("rush_yards", "carries"), "rush_td_rate": ("rush_td", "carries"),
                "explosive_rate": ("rush_10plus", "carries"), "ypt": ("rec_yards", "targets"),
                "catch_rate": ("receptions", "targets"), "adot": ("air_yards", "targets"),
                "rec_td_rate": ("rec_td", "targets"), "ypa": ("pass_yards", "attempts"),
                "pass_td_rate": ("pass_td", "attempts"), "int_rate": ("ints", "attempts"),
                "comp_rate": ("completions", "attempts"), "sack_rate": ("sacks_taken", "attempts"),
                "scramble_rate": ("scrambles", "attempts"), "rz_carry_rate": ("rz_carries", "carries"),
                "ez_target_rate": ("ez_targets", "targets")}


def fit_priors(tg_fit: pd.DataFrame, pg_fit: pd.DataFrame, fit_seasons=None) -> PriorSet:
    """Fit every shrinkage target from RAW team-game and player-game rows of the fit seasons only.

    Called with seasons strictly before the period the features will be used to predict.  Nothing here
    touches a feature column, so there is no recursion and no way for a later row to enter."""
    tg = tg_fit.copy()
    tg["off_td"] = tg["pass_td"] + tg["rush_td"]
    seasons = tuple(sorted(int(s) for s in tg["season"].unique())) if fit_seasons is None else tuple(sorted(fit_seasons))
    team_level = {c: float(np.nanmean(tg[c].to_numpy(dtype=float))) for c in TEAM_LEVEL_COLS}
    team_rate, team_den = {}, {}
    for name, (num, den) in TEAM_RATE_NUM_DEN.items():
        n = float(np.nansum(tg[num].to_numpy(dtype=float))); d = float(np.nansum(tg[den].to_numpy(dtype=float)))
        team_rate[name] = n / max(1.0, d)
    for den in sorted({d for _, d in TEAM_RATE_NUM_DEN.values()}):
        team_den[den] = float(np.nanmean(tg[den].to_numpy(dtype=float)))
    pg = pg_fit
    player_rate, player_rate_all = {}, {}
    pos = pg["position"].to_numpy(dtype=object)
    for name, (num, den) in PLAYER_RATES.items():
        nv = pg[num].to_numpy(dtype=float); dv = pg[den].to_numpy(dtype=float)
        player_rate_all[name] = float(np.nansum(nv) / max(1.0, np.nansum(dv)))
        for p in np.unique(pos):
            m = pos == p
            player_rate[f"{p}|{name}"] = float(np.nansum(nv[m]) / max(1.0, np.nansum(dv[m])))
    return PriorSet(team_level=team_level, team_rate=team_rate, team_den=team_den, player_rate=player_rate,
                    player_rate_all=player_rate_all, fit_seasons=seasons)


# ------------------------------------------------------------------------------------------ primitive
def decayed_prior_sums(group: np.ndarray, order: np.ndarray, season: np.ndarray, X: np.ndarray,
                       halflife: float, season_carry: float,
                       phantom: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Exponentially decayed sums of X over each subject's strictly earlier rows.

    Rows must be sorted by (group, order).  Returns (S, N, n_prior): S[i] = sum_j d^(age) X[j] over prior
    rows j of the same group, N[i] = sum_j d^(age) (the decayed count, NaN-aware per column), n_prior[i]
    = the raw number of prior rows.  Age advances one unit per prior ROW of that subject (a game), and the
    sums are multiplied by ``season_carry`` once per season boundary crossed.  A NaN in X[j] contributes
    nothing to S or N for that column.  X[i] itself is NEVER in S[i]: the test suite perturbs a row's
    outcome and asserts its own feature does not move.

    ``phantom[i]`` marks a row that is a READ of the state (a game the subject was eligible for but did
    not appear in): it receives the current sums and leaves them untouched -- no decay, no count."""
    n, m = X.shape
    d = 0.5 ** (1.0 / halflife)
    S = np.zeros((n, m)); N = np.zeros((n, m)); n_prior = np.zeros(n, dtype=np.int32)
    s = np.zeros(m); w = np.zeros(m); cur = None; last_season = None; cnt = 0
    for i in range(n):
        g = group[i]
        if g != cur:
            cur = g; s = np.zeros(m); w = np.zeros(m); cnt = 0; last_season = season[i]
        elif season[i] != last_season:
            c = season_carry ** max(1, int(season[i] - last_season))
            s = s * c; w = w * c; last_season = season[i]
        S[i] = s; N[i] = w; n_prior[i] = cnt
        if phantom is not None and phantom[i]:
            continue
        v = X[i]; ok = np.isfinite(v)
        s = s * d; w = w * d
        s[ok] += v[ok]; w[ok] += 1.0
        cnt += 1
    return S, N, n_prior


def _sorted(df: pd.DataFrame, group: str) -> pd.DataFrame:
    return df.sort_values([group, "season", "week", "game_id"]).reset_index(drop=True)


# ------------------------------------------------------------------------------------------ team side
TEAM_RATE_NUM_DEN = {
    # name: (numerator column, denominator column)  -- offence, per team-game
    "ypc": ("rush_yards", "rush_att"), "ypa": ("pass_yards", "pass_att"), "sack_rate": ("sacks", "dropbacks"),
    "scramble_rate": ("scrambles", "dropbacks"), "target_rate": ("targets", "pass_att"),
    "comp_rate": ("completions", "targets"), "pass_td_share": ("pass_td", "off_td"),
    "td_per_drive": ("off_td", "drives"), "int_rate": ("ints", "pass_att"),
}
TEAM_LEVEL_COLS = ["plays", "neutral_pass_rate", "pass_rate", "proe", "neutral_proe", "sec_per_play", "points",
                   "off_td", "epa_play", "success_rate", "rz_trips", "drives", "rush_att", "pass_att", "dropbacks"]


def team_features(tg: pd.DataFrame, cfg: FeatureConfig = FEATURE_CONFIG, priors: PriorSet | None = None) -> pd.DataFrame:
    """Prior-only EWMA features for every team-game: the team's own offence (``off_*``) and what its
    opponents have done against it (``def_*``), both shrunk toward FROZEN league targets fitted on seasons
    strictly before the rows being predicted (``priors``).  Returns the frame with feature columns added,
    sorted by (team, season, week)."""
    if priors is None:
        raise MissingPriors("team_features needs a PriorSet fitted on earlier seasons (features.fit_priors)")
    tg = tg.copy()
    tg["off_td"] = tg["pass_td"] + tg["rush_td"]
    # defensive view: the opponent's offensive line becomes the defence's 'allowed' row
    rate_cols = sorted({c for nd in TEAM_RATE_NUM_DEN.values() for c in nd})
    opp_cols = list(dict.fromkeys(TEAM_LEVEL_COLS + rate_cols))
    opp = tg[["game_id", "team"] + opp_cols].copy()
    opp = opp.rename(columns={c: f"allowed_{c}" for c in opp.columns if c not in ("game_id", "team")})
    opp = opp.rename(columns={"team": "opp"})
    tg = tg.merge(opp, on=["game_id", "opp"], how="left")
    tg = _sorted(tg, "team")
    level_cols = TEAM_LEVEL_COLS + [f"allowed_{c}" for c in TEAM_LEVEL_COLS]
    rate_cols_all = rate_cols + [f"allowed_{c}" for c in rate_cols]
    X = tg[level_cols + rate_cols_all].to_numpy(dtype=float)
    S, N, n_prior = decayed_prior_sums(tg["team"].to_numpy(), None, tg["season"].to_numpy(), X,
                                       cfg.team_halflife, cfg.team_season_carry)
    tg["team_n_prior"] = n_prior
    tg["priors_version"] = priors.version
    # The shrink targets are the FROZEN league means of the fit seasons.  An own-offence column and its
    # opponent-allowed twin share one target: over the league the multiset of allowed_X is the multiset of X.
    k = cfg.team_shrink_k
    for j, c in enumerate(level_cols):
        base = c.replace("allowed_", "")
        prior = priors.team_level[base]
        name = f"def_{base}" if c.startswith("allowed_") else f"off_{base}"
        tg[name] = (S[:, j] + k * prior) / (N[:, j] + k)
    off = len(level_cols)
    idx = {c: off + i for i, c in enumerate(rate_cols_all)}
    for name, (num, den) in TEAM_RATE_NUM_DEN.items():
        prior = priors.team_rate[name]
        # exposure-weighted: decayed numerator over decayed denominator, k pseudo-games of the prior
        den_prior = k * priors.team_den[den]
        for side, pre in (("", "off_"), ("allowed_", "def_")):
            jn, jd = idx[side + num], idx[side + den]
            tg[pre + name] = (S[:, jn] + prior * den_prior) / (S[:, jd] + den_prior)
    return tg


# ---------------------------------------------------------------------------------------- player side
PLAYER_COUNT_COLS = ["carries", "designed_carries", "rush_yards", "rush_td", "scrambles", "rz_carries", "i5_carries",
                     "rush_10plus", "targets", "receptions", "rec_yards", "rec_td", "air_yards", "rz_targets", "ez_targets",
                     "attempts", "completions", "pass_yards", "pass_td", "ints", "sacks_taken", "offense_snaps"]


def _attach_team_volume(pg: pd.DataFrame, tg: pd.DataFrame) -> pd.DataFrame:
    vol = tg[["game_id", "team", "plays", "designed_rush", "rush_att", "targets", "pass_att", "dropbacks", "rz_rush",
              "rz_pass", "i5_rush", "pass_td", "rush_td", "points", "margin", "total", "pass_rate"]].rename(
        columns={"plays": "team_plays", "designed_rush": "team_designed_rush", "rush_att": "team_rush_att",
                 "targets": "team_targets", "pass_att": "team_pass_att", "dropbacks": "team_dropbacks",
                 "rz_rush": "team_rz_rush", "rz_pass": "team_rz_pass", "i5_rush": "team_i5_rush",
                 "pass_td": "team_pass_td", "rush_td": "team_rush_td", "points": "team_points",
                 "margin": "team_margin", "total": "game_total", "pass_rate": "team_pass_rate"})
    return pg.merge(vol, on=["game_id", "team"], how="left")


def player_features(pg: pd.DataFrame, tg: pd.DataFrame, cfg: FeatureConfig = FEATURE_CONFIG,
                    phantom_rows: pd.DataFrame | None = None, priors: PriorSet | None = None) -> pd.DataFrame:
    """Prior-only features for every player-game.

    Shares (``sh_*``) are the player's share of the team's official volume in each prior game, averaged
    with two half-lives; rates (``rt_*``) are exposure-weighted (decayed yards over decayed carries)
    and shrunk toward the FROZEN position prior (``priors``, fitted on earlier seasons) with
    ``rate_shrink_k`` pseudo-touches.  ``last_*`` is the previous game's share, ``gap_weeks`` the weeks
    since the player's previous appearance."""
    if priors is None:
        raise MissingPriors("player_features needs a PriorSet fitted on earlier seasons (features.fit_priors)")
    pg = pg.copy(); pg["phantom"] = False
    if phantom_rows is not None and len(phantom_rows):
        ph = phantom_rows[["game_id", "team", "player_id", "position", "season", "week"]].copy()
        ph["phantom"] = True
        # a phantom row must not duplicate a real appearance
        key = set(zip(pg["game_id"], pg["player_id"]))
        ph = ph[[k not in key for k in zip(ph["game_id"], ph["player_id"])]]
        pg = pd.concat([pg, ph], ignore_index=True, sort=False)
    pg = _attach_team_volume(pg, tg)
    pg = pg[pg["position"].isin(SKILL)].copy()
    pg["snap_share"] = pg["offense_pct"].astype(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        pg["sh_carry"] = pg["designed_carries"] / pg["team_designed_rush"].clip(lower=1)
        pg["sh_target"] = pg["targets"] / pg["team_targets"].clip(lower=1)
        pg["sh_rz_carry"] = np.where(pg["team_rz_rush"] > 0, pg["rz_carries"] / pg["team_rz_rush"].clip(lower=1), np.nan)
        pg["sh_rz_target"] = np.where(pg["team_rz_pass"] > 0, pg["rz_targets"] / pg["team_rz_pass"].clip(lower=1), np.nan)
        pg["sh_attempt"] = pg["attempts"] / pg["team_pass_att"].clip(lower=1)
    pg = _sorted(pg, "player_id")
    share_cols = ["sh_carry", "sh_target", "sh_rz_carry", "sh_rz_target", "sh_attempt", "snap_share"]
    Xs = np.array(pg[share_cols].to_numpy(dtype=float), copy=True)
    grp = pg["player_id"].to_numpy(); sea = pg["season"].to_numpy(); phantom = pg["phantom"].to_numpy(bool)
    Xs[phantom] = np.nan
    for tag, hl in (("s", cfg.player_halflife_short), ("l", cfg.player_halflife_long)):
        S, N, n_prior = decayed_prior_sums(grp, None, sea, Xs, hl, cfg.player_season_carry, phantom=phantom)
        for j, c in enumerate(share_cols):
            pg[f"{c}_{tag}"] = np.where(N[:, j] > 0, S[:, j] / np.maximum(N[:, j], 1e-9), np.nan)
            pg[f"{c}_{tag}_w"] = N[:, j]
    pg["n_prior"] = n_prior
    # last game's shares and the gap since it
    real = ~phantom
    for c in share_cols:
        v = pg[c].where(real)
        pg[f"last_{c}"] = v.groupby(pg["player_id"]).transform(lambda x: x.shift(1).ffill())
    ps = pg["season"].where(real).groupby(pg["player_id"]).transform(lambda x: x.shift(1).ffill())
    pw = pg["week"].where(real).groupby(pg["player_id"]).transform(lambda x: x.shift(1).ffill())
    pg["gap_weeks"] = np.where(ps.isna(), np.nan, np.where(ps == pg["season"], pg["week"] - pw, 99))
    # exposure-weighted rates
    Xc = np.array(pg[PLAYER_COUNT_COLS].to_numpy(dtype=float), copy=True)
    Xc[phantom] = np.nan
    Sc, Nc, _ = decayed_prior_sums(grp, None, sea, Xc, cfg.player_halflife_long, cfg.player_season_carry, phantom=phantom)
    ci = {c: i for i, c in enumerate(PLAYER_COUNT_COLS)}
    pos = pg["position"].to_numpy(dtype=object)
    pg["priors_version"] = priors.version
    for name, (num, den) in PLAYER_RATES.items():
        jn, jd = ci[num], ci[den]
        # position prior: FROZEN, fitted on earlier seasons; a later game cannot move it
        prior = priors.player_prior(pos, name)
        k = cfg.rate_shrink_k
        pg[f"rt_{name}"] = (Sc[:, jn] + k * prior) / (Sc[:, jd] + k)
        pg[f"rt_{name}_n"] = Sc[:, jd]
        pg[f"prior_{name}"] = prior
    return pg


# --------------------------------------------------------------------------- depth charts / rosters
def depth_chart(season: int, week: int | None = None, cutoff: datetime | None = None) -> pd.DataFrame:
    """Depth-chart rank per (team, player) at a point in time.

    2016-2024 files are weekly (season, week, game_type=REG); 2025+ files are daily snapshots stamped
    ``dt`` and the latest snapshot at or before ``cutoff`` is used.  Returns columns
    team, player_id, dc_pos, dc_rank, dc_vintage."""
    p = os.path.join(RAW, "depth_charts", f"depth_charts_{season}.parquet")
    d = pl.read_parquet(p)
    if "dt" in d.columns:
        if cutoff is None:
            raise ValueError("daily depth charts need a cutoff")
        vint = sorted(v for v in d["dt"].unique().to_list() if v and datetime.strptime(v, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) <= cutoff)
        if not vint:
            return pd.DataFrame(columns=["team", "player_id", "dc_pos", "dc_rank", "dc_vintage"])
        latest = vint[-1]
        sub = d.filter((pl.col("dt") == latest) & pl.col("pos_abb").is_in(list(SKILL)) & pl.col("gsis_id").is_not_null())
        out = sub.select([pl.col("team"), pl.col("gsis_id").alias("player_id"), pl.col("pos_abb").alias("dc_pos"),
                          pl.col("pos_rank").cast(pl.Int32).alias("dc_rank")]).to_pandas()
        out = out.sort_values("dc_rank").drop_duplicates(["team", "player_id"])
        out["dc_vintage"] = latest
        return out
    if week is None:
        raise ValueError("weekly depth charts need a week")
    sub = d.filter((pl.col("week") == week) & (pl.col("game_type") == "REG") & pl.col("gsis_id").is_not_null()
                   & pl.col("position").is_in(list(SKILL)) & (pl.col("formation") == "Offense"))
    out = sub.select([pl.col("club_code").replace(D.TEAM_FIX).alias("team"), pl.col("gsis_id").alias("player_id"),
                      pl.col("position").alias("dc_pos"), pl.col("depth_team").cast(pl.Int32).alias("dc_rank")]).to_pandas()
    out = out.sort_values("dc_rank").drop_duplicates(["team", "player_id"])
    out["dc_vintage"] = f"{season}-W{week:02d}"
    return out


def weekly_roster(season: int, week: int) -> pd.DataFrame:
    """Players on an active roster (status ACT) for the week, with position.  Weekly rosters are published
    ahead of the week (the 2026 week-2 file exists on 2026-09-16); they say who is ON the roster, not who is
    active on game day."""
    p = os.path.join(RAW, "weekly_rosters", f"roster_weekly_{season}.parquet")
    r = pl.read_parquet(p, columns=["season", "team", "position", "gsis_id", "status", "week", "game_type", "full_name"])
    r = r.filter((pl.col("week") == week) & pl.col("gsis_id").is_not_null())
    r = r.with_columns(pl.col("team").replace(D.TEAM_FIX).alias("team"))
    out = r.select(["team", pl.col("gsis_id").alias("player_id"), "position", "status", pl.col("full_name").alias("player_name")]).to_pandas()
    return out.drop_duplicates(["team", "player_id"])


def injury_designations(season: int, week: int, root: str | None = None) -> pd.DataFrame:
    """Final injury-report designation per player for the week (Out / Doubtful / Questionable).  The nflverse
    file is rebuilt in place, so for a PROSPECTIVE run the caller must resolve a dated vintage through
    ``nfl_edge.shadow_v2.vintage_snapshots.resolve_injuries`` and pass its path via ``root``; for
    historical backtests the final report is what was known at kickoff."""
    p = root or os.path.join(RAW, "injuries", f"injuries_{season}.parquet")
    if not os.path.exists(p):
        return pd.DataFrame(columns=["player_id", "report_status", "practice_status"])
    i = pl.read_parquet(p).filter((pl.col("week") == week) & pl.col("gsis_id").is_not_null())
    if "game_type" in i.columns:
        i = i.filter(pl.col("game_type") == "REG") if season < 2025 or i.filter(pl.col("game_type") == "REG").height else i
    out = i.select([pl.col("gsis_id").alias("player_id"), "report_status", "practice_status"]).to_pandas()
    return out.drop_duplicates("player_id")


def eligible_players(season: int, week: int, team: str, *, depth: pd.DataFrame, roster: pd.DataFrame,
                     injuries: pd.DataFrame, history: pd.DataFrame | None = None) -> pd.DataFrame:
    """The set of players the simulator allocates opportunity to for one team-game, with the reason each
    is in or out.  Rules (all point-in-time inputs):
      * on the weekly roster with status ACT at a skill position, or on the offensive depth chart;
      * not designated Out or Doubtful on the week's report;
      * Questionable players stay in (their share is reduced through the play-probability layer).
    Returns team, player_id, position, dc_rank (NaN if unlisted), avail_state."""
    ros_all = roster[(roster["team"] == team)]
    not_active = set(ros_all[ros_all["status"] != "ACT"]["player_id"])
    ros = ros_all[ros_all["position"].isin(SKILL) & (ros_all["status"] == "ACT")]
    dc = depth[depth["team"] == team]
    ids = set(ros["player_id"]) | set(dc["player_id"])
    if history is not None:
        ids |= set(history[(history["team"] == team)]["player_id"])
    rows = []
    inj = injuries.set_index("player_id")["report_status"].to_dict() if len(injuries) else {}
    posmap = dict(zip(ros["player_id"], ros["position"]))
    posmap.update({r.player_id: r.dc_pos for r in dc.itertuples()})
    rankmap = dict(zip(dc["player_id"], dc["dc_rank"]))
    on_roster = set(ros["player_id"])
    for pid in ids:
        st = inj.get(pid)
        pos = posmap.get(pid)
        if pos not in SKILL:
            continue
        if pid in not_active:
            continue  # on the roster file with a non-active status (RES/INA/CUT/DEV): not available
        if pid not in on_roster and pid not in rankmap:
            continue  # history only, no longer on this roster
        if st in ("Out", "Doubtful"):
            state = "OUT" if st == "Out" else "DOUBTFUL"
        elif st == "Questionable":
            state = "QUESTIONABLE"
        else:
            state = "EXPECTED_ACTIVE"
        rows.append({"team": team, "player_id": pid, "position": pos, "dc_rank": rankmap.get(pid, np.nan),
                     "avail_state": state, "on_roster": pid in on_roster})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------------------- assembly
def build_frames(seasons, cfg: FeatureConfig = FEATURE_CONFIG, priors: PriorSet | None = None,
                 prior_seasons=None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(team frame with features, player frame with features) for the seasons.

    Features on a row use only earlier rows of the same subject AND frozen priors.  ``priors`` must be
    fitted on seasons strictly before anything that will be predicted; ``prior_seasons`` is a convenience
    that fits them here from those seasons' raw rows."""
    tg = D.load("team_games", seasons).to_pandas()
    pg = D.load("player_games", seasons).to_pandas()
    if priors is None:
        if prior_seasons is None:
            raise MissingPriors("build_frames needs priors= or prior_seasons=")
        priors = fit_priors(D.load("team_games", prior_seasons).to_pandas(),
                            D.load("player_games", prior_seasons).to_pandas(), fit_seasons=prior_seasons)
    tf = team_features(tg, cfg, priors)
    pf = player_features(pg, tg, cfg, priors=priors)
    return tf, pf
