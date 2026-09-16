"""Assemble training frames and fit the full model bundle for a target season.

``assemble(seasons)`` builds, for every team-game in ``seasons``:
  * the point-in-time ELIGIBLE set (weekly roster status, depth chart of that week, injury designations),
    with the realised share of the team's designed carries / targets for every eligible player -- zero for
    the eligible who received none, which is what the opportunity model must learn;
  * per-carry and per-target rows joined with the runner's / receiver's prior-only features and the
    opponent's and own team's prior-only features.

``fit_bundle(target_season)`` fits everything on seasons strictly before ``target_season`` (the first two
seasons of history are warm-up only) and returns the artifact used for that season's projections.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import polars as pl

from . import data as D
from . import features as F
from . import models as M

CACHE = D.CACHE
WARMUP_SEASONS = 2


def _season_sources(season: int):
    depth_all = pl.read_parquet(os.path.join(D.RAW, "depth_charts", f"depth_charts_{season}.parquet"))
    daily = "dt" in depth_all.columns
    ros = F.weekly_roster  # per week
    inj_path = os.path.join(D.RAW, "injuries", f"injuries_{season}.parquet")
    return depth_all, daily, ros, inj_path


def eligible_frame(seasons, verbose=print) -> pd.DataFrame:
    """One row per (game, team, eligible player) with position, dc_rank, avail_state.  Cached per season."""
    os.makedirs(CACHE, exist_ok=True)
    frames = []
    games = D.schedule().to_pandas()
    for season in seasons:
        path = os.path.join(CACHE, f"eligible_{season}.parquet")
        if os.path.exists(path):
            frames.append(pd.read_parquet(path)); continue
        g = games[(games["season"] == season) & games["game_type"].isin(["REG", "WC", "DIV", "CON", "SB"])]
        g = g[g["home_score"].notna() | (season >= 2026)]
        dc_path = os.path.join(D.RAW, "depth_charts", f"depth_charts_{season}.parquet")
        daily = "dt" in pl.scan_parquet(dc_path).collect_schema().names()
        hist = D.load("player_games", [season - 1]).to_pandas()[["team", "player_id"]].drop_duplicates() if season > 2016 else None
        rows = []
        for week in sorted(g["week"].unique()):
            gw = g[g["week"] == week]
            if daily:
                # the earliest kickoff of the week, at 00:00 UTC that day: a chart published on game day is
                # still "before the game", one published after the game is not
                day = pd.Timestamp(gw["gameday"].min()).tz_localize("UTC")
                depth = F.depth_chart(season, cutoff=day.to_pydatetime())
            else:
                depth = F.depth_chart(season, week=int(week))
            roster = F.weekly_roster(season, int(week))
            if roster.empty:  # postseason weeks sometimes absent: use the last published week
                roster = F.weekly_roster(season, int(g["week"].max()))
            inj = F.injury_designations(season, int(week))
            for r in gw.itertuples():
                for team in (r.home_team, r.away_team):
                    e = F.eligible_players(season, int(week), team, depth=depth, roster=roster, injuries=inj,
                                           history=None)
                    if e.empty:
                        continue
                    e["game_id"] = r.game_id; e["season"] = season; e["week"] = int(week)
                    rows.append(e)
            verbose(f"eligible {season} w{week}: {sum(len(x) for x in rows)} rows so far")
        f = pd.concat(rows, ignore_index=True)
        f.to_parquet(path)
        frames.append(f)
    return pd.concat(frames, ignore_index=True)


def assemble(seasons, cfg: F.FeatureConfig = F.FEATURE_CONFIG, verbose=print) -> dict:
    """Frames with features for the seasons: team, player (real + phantom), eligible-with-shares, carries, targets."""
    tg = D.load("team_games", seasons).to_pandas()
    pg = D.load("player_games", seasons).to_pandas()
    elig = eligible_frame(seasons, verbose=verbose)
    elig = elig[elig["avail_state"].isin(["EXPECTED_ACTIVE", "QUESTIONABLE"])]
    tf = F.team_features(tg, cfg)
    pf = F.player_features(pg, tg, cfg, phantom_rows=elig)
    # eligible rows with realised shares
    keep = ["game_id", "team", "player_id", "position", "dc_rank", "avail_state", "season", "week"]
    e = elig[keep].merge(pf.drop(columns=["position", "season", "week", "team"]), on=["game_id", "player_id"], how="left")
    e["designed_carries"] = e["designed_carries"].fillna(0); e["targets"] = e["targets"].fillna(0)
    e["team_designed_rush"] = e["team_designed_rush"].fillna(0); e["team_targets"] = e["team_targets"].fillna(0)
    e["y_share_carry"] = np.where(e["team_designed_rush"] > 0, e["designed_carries"] / e["team_designed_rush"].clip(lower=1), np.nan)
    e["y_share_target"] = np.where(e["team_targets"] > 0, e["targets"] / e["team_targets"].clip(lower=1), np.nan)
    # share of the team's volume that went OUTSIDE the eligible set, by team-game
    tot = e.groupby(["game_id", "team"]).agg(elig_carries=("designed_carries", "sum"), elig_targets=("targets", "sum"),
                                            team_designed_rush=("team_designed_rush", "first"), team_targets=("team_targets", "first")).reset_index()
    # per-touch rows
    tf_off = tf[["game_id", "team", "off_ypc", "off_ypa", "off_comp_rate", "margin", "home"]].rename(columns={"margin": "team_margin"})
    tf_def = tf[["game_id", "team", "def_ypc", "def_ypa", "def_comp_rate"]].rename(columns={"team": "opp"})
    pfeat = pf[~pf["phantom"]][["game_id", "player_id", "position", "rt_ypc", "prior_ypc", "rt_explosive_rate", "rt_ypc_n",
                                "rt_ypt", "prior_ypt", "rt_catch_rate", "rt_adot", "rt_ypt_n"]]
    car = D.load("carries", seasons).to_pandas()
    car = car.merge(pfeat, on=["game_id", "player_id"], how="inner").merge(tf_off, on=["game_id", "team"], how="inner") \
             .merge(tf_def, on=["game_id", "opp"], how="inner")
    tar = D.load("targets", seasons).to_pandas()
    tar = tar.merge(pfeat, on=["game_id", "player_id"], how="inner").merge(tf_off, on=["game_id", "team"], how="inner") \
             .merge(tf_def, on=["game_id", "opp"], how="inner")
    return {"team": tf, "player": pf, "eligible": e, "outside": tot, "carries": car, "targets": tar}


def fit_bundle(target_season: int, frames: dict | None = None, history_start: int = 2016,
               cfg: F.FeatureConfig = F.FEATURE_CONFIG, verbose=print) -> dict:
    """Fit every primitive on seasons < target_season (after the warm-up seasons) and return the bundle."""
    seasons = list(range(history_start, target_season))
    if frames is None:
        frames = assemble(range(history_start, target_season + 1), cfg, verbose=verbose)
    train = [s for s in seasons if s >= history_start + WARMUP_SEASONS]
    tf = frames["team"]; tf = tf[tf["season"].isin(train)]
    e = frames["eligible"]; e = e[e["season"].isin(train)]
    car = frames["carries"]; car = car[car["season"].isin(train)]
    tar = frames["targets"]; tar = tar[tar["season"].isin(train)]
    verbose(f"fit {target_season}: train seasons {train}, team rows {len(tf)}, eligible rows {len(e)}, carries {len(car)}, targets {len(tar)}")
    game_env = M.fit_game_env(tf)
    ec = e[e["y_share_carry"].notna()].rename(columns={"y_share_carry": "y_share"})
    et = e[e["y_share_target"].notna()].rename(columns={"y_share_target": "y_share"})
    carry_share = M.fit_share_model(ec, "carry")
    target_share = M.fit_share_model(et, "target")
    carry = M.fit_carry_model(car)
    target = M.fit_target_model(tar)
    pf_train = frames["player"]; pf_train = pf_train[pf_train["season"].isin(train) & ~pf_train["phantom"]]
    td = M.fit_td_weights(pf_train)
    o = frames["outside"]; o = o[o["game_id"].str[:4].astype(int).isin(train)]
    other_share = {"carry": float(1 - o["elig_carries"].sum() / max(1, o["team_designed_rush"].sum())),
                   "target": float(1 - o["elig_targets"].sum() / max(1, o["team_targets"].sum()))}
    qb_share = M.fit_qb_share(e)
    b = M.bundle(game_env, carry_share, target_share, carry, target, td, train_seasons=train,
                 feature_config=cfg.to_dict(), other_share=other_share, qb_share=qb_share)
    b["target_season"] = target_season
    return b
