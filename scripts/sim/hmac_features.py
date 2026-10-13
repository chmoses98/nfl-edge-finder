"""Historical Model Architecture Championship (RESEARCH_ONLY): point-in-time game frame, 2001-2025.

Reuses ``gsdl_features.build_season_frame`` (strictly-prior EWMA team features, QB / coach / rest / residual-history
families) re-pointed at an earlier history start, and adds what the football-first and possession architectures need:
sequential Elo (opponent-adjusted strength incl. strength of schedule), turnover rate, drives per game, touchdown /
field-goal rate per drive.  Every statistic for a game uses only games strictly before it; every league constant is fitted
on seasons strictly before the frame's evaluation season Y.
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd
import polars as pl
from nfl_edge.sim import data as D, features as F
from scripts.sim import gsdl_features as GF

GF.HISTORY_START = 2001
GF.CACHE = os.path.join(D.ROOT, "data", "cache", "hmac")
CFG = F.FEATURE_CONFIG
K = CFG.team_shrink_k
ELO_K, ELO_HFA, ELO_CARRY = 0.07, 2.0, 0.7      # fixed a priori constants (not tuned)
GAME_TYPES = ["REG", "WC", "DIV", "CON", "SB"]


def _drive_stats(season: int) -> pd.DataFrame:
    path = os.path.join(D.RAW, "pbp", f"play_by_play_{season}.parquet")
    d = pl.read_parquet(path, columns=["game_id", "posteam", "fixed_drive", "fixed_drive_result", "interception", "fumble_lost",
                                       "play_type", "season_type"])
    d = d.filter(pl.col("posteam").is_not_null() & pl.col("season_type").is_in(["REG", "POST"]))
    d = d.with_columns(pl.col("posteam").replace(D.TEAM_FIX).alias("team"))
    dr = d.group_by(["game_id", "team", "fixed_drive"]).agg(pl.col("fixed_drive_result").first().alias("res"))
    a = dr.group_by(["game_id", "team"]).agg([pl.len().alias("drives"), (pl.col("res") == "Touchdown").sum().alias("td_drives"),
                                              (pl.col("res") == "Field goal").sum().alias("fg_drives")])
    t = (d.filter(pl.col("play_type").is_in(["run", "pass"]))
         .group_by(["game_id", "team"]).agg(((pl.col("interception").fill_null(0) == 1) | (pl.col("fumble_lost").fill_null(0) == 1)).sum().alias("turnovers")))
    return a.join(t, on=["game_id", "team"], how="left").to_pandas()


def elo_table(g_all: pd.DataFrame) -> pd.DataFrame:
    """Pregame margin-Elo difference (home minus away, HFA excluded) for every game, from games strictly before it."""
    g = g_all.sort_values(["season", "week", "gameday", "game_id"]).reset_index(drop=True)
    r = {}; out = np.zeros(len(g)); last = None
    for i, x in enumerate(g.itertuples(index=False)):
        if x.season != last:
            r = {k: v * ELO_CARRY for k, v in r.items()}; last = x.season
        rh, ra = r.get(x.home_team, 0.0), r.get(x.away_team, 0.0)
        out[i] = rh - ra
        if x.result == x.result:                       # played
            err = float(x.result) - (rh - ra + ELO_HFA)
            r[x.home_team] = rh + ELO_K * err; r[x.away_team] = ra - ELO_K * err
    return pd.DataFrame({"game_id": g["game_id"], "f_elo": out})


def build(Y: int, verbose=print) -> pd.DataFrame:
    path = os.path.join(GF.CACHE, f"hmac_{Y}.parquet")
    if os.path.exists(path):
        return pd.read_parquet(path)
    g = GF.build_season_frame(Y, verbose=lambda *_: None).copy()
    yrs = list(range(GF.HISTORY_START, Y + 1)); fit = [s for s in yrs if s < Y]
    sch = GF.schedule_frame(); sch = sch[sch["season"].isin(yrs) & sch["game_type"].isin(GAME_TYPES)]
    g = g.merge(elo_table(sch), on="game_id", how="left")
    ds = pd.concat([_drive_stats(s) for s in yrs], ignore_index=True)
    tg = D.load("team_games", yrs).to_pandas()[["game_id", "team", "opp", "season", "week", "plays"]]
    d = tg.merge(ds, on=["game_id", "team"], how="left").sort_values(["team", "season", "week", "game_id"]).reset_index(drop=True)
    for c in ("drives", "td_drives", "fg_drives", "turnovers"):
        d[c] = d[c].fillna(0.0)
    fm = d["season"].isin(fit)
    stats = {"td_rate": ("td_drives", "drives"), "fg_rate": ("fg_drives", "drives"), "to_rate": ("turnovers", "drives")}
    for name, (num, den) in stats.items():
        pr = d.loc[fm, num].sum() / max(1.0, d.loc[fm, den].sum()); pd_ = d.loc[fm, den].mean()
        for group, pre in (("team", "off_"), ("opp", "def_")):
            idx, S, N, n = GF._ewma(d, group, [num, den], CFG.team_halflife)
            d.loc[idx, pre + name] = (S[:, 0] + pr * K * pd_) / (S[:, 1] + K * pd_)
    p_dr = d.loc[fm, "drives"].mean()
    for group, pre in (("team", "off_"), ("opp", "def_")):
        idx, S, N, n = GF._ewma(d, group, ["drives"], CFG.team_halflife)
        d.loc[idx, pre + "drives"] = (S[:, 0] + p_dr * K) / (N[:, 0] + K)
    cols = [f"{p}{s}" for p in ("off_", "def_") for s in ("td_rate", "fg_rate", "to_rate", "drives")]
    for s_, tcol in (("h", "home_team"), ("a", "away_team")):
        t = d[["game_id", "team"] + cols].rename(columns={c: f"{s_}_{c}" for c in cols}).rename(columns={"team": tcol})
        g = g.merge(t, on=["game_id", tcol], how="left")
    new = {}
    for x in ("td_rate", "fg_rate", "to_rate", "drives"):
        hm = (g[f"h_off_{x}"] + g[f"a_def_{x}"]) / 2; am = (g[f"a_off_{x}"] + g[f"h_def_{x}"]) / 2
        new[f"mf_{x}"] = hm - am; new[f"sf_{x}"] = hm + am; new[f"hm_{x}"] = hm; new[f"am_{x}"] = am
    g = pd.concat([g, pd.DataFrame(new, index=g.index)], axis=1)
    # moneyline-implied home win probability (de-vigged), when quoted
    ph = np.where(g["home_moneyline"] < 0, -g["home_moneyline"] / (-g["home_moneyline"] + 100), 100 / (g["home_moneyline"] + 100))
    pa = np.where(g["away_moneyline"] < 0, -g["away_moneyline"] / (-g["away_moneyline"] + 100), 100 / (g["away_moneyline"] + 100))
    g["mkt_pwin"] = np.where(g["home_moneyline"].notna() & g["away_moneyline"].notna(), ph / (ph + pa), np.nan)
    g = g.copy(); g.to_parquet(path); verbose(f"hmac {Y}: {g.shape}")
    return g
