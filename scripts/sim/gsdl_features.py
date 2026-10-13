"""Game Script Discovery Lab (RESEARCH_ONLY): point-in-time game-level feature matrix.

Everything is a strictly-prior EWMA from raw rows (reusing ``nfl_edge.sim.features.decayed_prior_sums`` and
``team_features``), shrunk toward constants fitted on seasons strictly before the evaluation season.  One frame per
evaluation season Y is built from priors fitted on seasons < Y (the repo's convention) and cached.
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd
import polars as pl
from nfl_edge.sim import data as D, features as F

ROOT = D.ROOT
CACHE = os.path.join(ROOT, "data", "cache", "gsdl")
CFG = F.FEATURE_CONFIG
HISTORY_START = 2016
K = CFG.team_shrink_k

# ratio stats the incumbent team frame does not carry: name -> (numerator, denominator)
NEW_RATIOS = {"pass_epa": ("pass_epa_sum", "db_n"), "rush_epa": ("rush_epa_sum", "rush_n"),
              "expl_pass": ("expl_pass_n", "db_n"), "expl_rush": ("expl_rush_n", "rush_n"), "hit": ("hit_n", "db_n")}
# stats taken from the incumbent frame (off_<x> / def_<x> already exist)
BASE_STATS = ["epa_play", "points", "success_rate", "plays", "sec_per_play", "neutral_pass_rate", "ypa", "ypc", "sack_rate"]
ALL_STATS = BASE_STATS + list(NEW_RATIOS)


def _pbp_extra(season: int) -> pd.DataFrame:
    path = os.path.join(D.RAW, "pbp", f"play_by_play_{season}.parquet")
    cols = ["game_id", "posteam", "play_type", "rush_attempt", "qb_scramble", "qb_kneel", "qb_dropback", "epa",
            "yards_gained", "qb_hit", "complete_pass", "season_type", "passer_player_id"]
    d = pl.read_parquet(path, columns=cols).filter(pl.col("posteam").is_not_null()
                                                   & pl.col("season_type").is_in(["REG", "POST"]))
    d = d.with_columns(pl.col("posteam").replace(D.TEAM_FIX).alias("team"))
    db = pl.col("qb_dropback").fill_null(0) == 1
    rush = (pl.col("rush_attempt").fill_null(0) == 1) & (pl.col("qb_scramble").fill_null(0) == 0) & (pl.col("qb_kneel").fill_null(0) == 0)
    cp = pl.col("complete_pass").fill_null(0) == 1
    g = d.group_by(["game_id", "team"]).agg([
        db.sum().alias("db_n"), pl.when(db).then(pl.col("epa")).otherwise(0.0).sum().alias("pass_epa_sum"),
        rush.sum().alias("rush_n"), pl.when(rush).then(pl.col("epa")).otherwise(0.0).sum().alias("rush_epa_sum"),
        (db & cp & (pl.col("yards_gained") >= 20)).sum().alias("expl_pass_n"),
        (rush & (pl.col("yards_gained") >= 10)).sum().alias("expl_rush_n"),
        (db & (pl.col("qb_hit").fill_null(0) == 1)).sum().alias("hit_n")])
    q = (d.filter(db & pl.col("passer_player_id").is_not_null()).group_by(["game_id", "passer_player_id"])
         .agg([pl.len().alias("qb_db"), pl.col("epa").sum().alias("qb_epa_sum")]))
    return g.to_pandas(), q.to_pandas()


def _ewma(df, group, cols, halflife, carry=None):
    s = df.sort_values([group, "season", "week", "game_id"])
    S, N, n = F.decayed_prior_sums(s[group].to_numpy(), None, s["season"].to_numpy(), s[cols].to_numpy(float), halflife,
                                   CFG.team_season_carry if carry is None else carry)
    return s.index, S, N, n


def schedule_frame() -> pd.DataFrame:
    g = pd.read_csv(os.path.join(D.RAW, "schedules", "games.csv"))
    for c in ("home_team", "away_team"):
        g[c] = g[c].replace(D.TEAM_FIX)
    return g


def build_season_frame(Y: int, verbose=print) -> pd.DataFrame:
    """One row per game of seasons HISTORY_START..Y with pregame features (priors fitted on seasons < Y)."""
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"games_{Y}.parquet")
    if os.path.exists(path):
        return pd.read_parquet(path)
    yrs = list(range(HISTORY_START, Y + 1)); fit = [s for s in yrs if s < Y]
    tg = D.load("team_games", yrs).to_pandas()
    empty = pd.DataFrame({"position": [], **{c: [] for c in sum([list(v) for v in F.PLAYER_RATES.values()], [])}})
    priors = F.fit_priors(tg[tg["season"].isin(fit)], empty, fit_seasons=fit)
    tf = F.team_features(tg, CFG, priors)
    ex, qb = zip(*[_pbp_extra(s) for s in yrs]); ex = pd.concat(ex, ignore_index=True); qb = pd.concat(qb, ignore_index=True)
    d = tf.merge(ex, on=["game_id", "team"], how="left").sort_values(["team", "season", "week", "game_id"]).reset_index(drop=True)
    fitm = d["season"].isin(fit)
    for name, (num, den) in NEW_RATIOS.items():
        p_rate = d.loc[fitm, num].sum() / max(1.0, d.loc[fitm, den].sum()); p_den = d.loc[fitm, den].mean()
        for group, pre in (("team", "off_"), ("opp", "def_")):
            idx, S, N, n = _ewma(d, group, [num, den], CFG.team_halflife)
            d.loc[idx, pre + name] = (S[:, 0] + p_rate * K * p_den) / (S[:, 1] + K * p_den)

    # ---- game-level frame
    g = schedule_frame(); g = g[g["season"].isin(yrs) & g["game_type"].isin(["REG", "WC", "DIV", "CON", "SB"]) & g["result"].notna()
                                & g["spread_line"].notna() & g["total_line"].notna()].copy()
    cols = [f"off_{x}" for x in ALL_STATS] + [f"def_{x}" for x in ALL_STATS] + ["team_n_prior"]
    side = {}
    for s, tcol in (("h", "home_team"), ("a", "away_team")):
        t = d[["game_id", "team"] + cols].rename(columns={c: f"{s}_{c}" for c in cols}).rename(columns={"team": tcol})
        g = g.merge(t, on=["game_id", tcol], how="left")
    for x in ALL_STATS:
        hm = (g[f"h_off_{x}"] + g[f"a_def_{x}"]) / 2; am = (g[f"a_off_{x}"] + g[f"h_def_{x}"]) / 2
        g[f"mf_{x}"] = hm - am; g[f"sf_{x}"] = hm + am

    # ---- market-residual history (team EWMA of margin / total residual vs the closing line)
    g["mres"] = g["result"] - g["spread_line"]; g["tres"] = g["total"] - g["total_line"]
    rows = pd.concat([
        pd.DataFrame({"game_id": g["game_id"], "team": g["home_team"], "season": g["season"], "week": g["week"], "m": g["mres"], "t": g["tres"]}),
        pd.DataFrame({"game_id": g["game_id"], "team": g["away_team"], "season": g["season"], "week": g["week"], "m": -g["mres"], "t": g["tres"]})],
        ignore_index=True)
    idx, S, N, n = _ewma(rows, "team", ["m", "t"], CFG.team_halflife)
    rows.loc[idx, "ats"] = S[:, 0] / (N[:, 0] + K); rows.loc[idx, "ou"] = S[:, 1] / (N[:, 1] + K)
    for s, tcol in (("h", "home_team"), ("a", "away_team")):
        g = g.merge(rows[["game_id", "team", "ats", "ou"]].rename(columns={"team": tcol, "ats": f"{s}_ats", "ou": f"{s}_ou"}),
                    on=["game_id", tcol], how="left")
    g["f_ats_diff"] = g["h_ats"] - g["a_ats"]; g["f_ou_mean"] = (g["h_ou"] + g["a_ou"]) / 2

    # ---- QB availability / quality (starter = games.csv id: public ~90 min before kickoff, the same T-0 horizon as the line)
    qb["qb_db"] = qb["qb_db"].astype(float)
    fq = qb[qb["game_id"].str[:4].astype(int) < Y]
    p_qb = fq["qb_epa_sum"].sum() / max(1.0, fq["qb_db"].sum()); K_DB = 150.0
    tl = []
    for s, side in (("h", "home"), ("a", "away")):
        tl.append(pd.DataFrame({"game_id": g["game_id"], "qb": g[f"{side}_qb_id"], "team": g[f"{side}_team"],
                                "season": g["season"], "week": g["week"], "side": s}))
    st = pd.concat(tl, ignore_index=True).merge(qb.rename(columns={"passer_player_id": "qb"}), on=["game_id", "qb"], how="left")
    st[["qb_db", "qb_epa_sum"]] = st[["qb_db", "qb_epa_sum"]].fillna(0.0)
    st["one"] = 1.0
    idx, S, N, n = _ewma(st, "qb", ["qb_db", "qb_epa_sum", "one"], 16.0, carry=0.7)
    st.loc[idx, "qb_epa"] = (S[:, 1] + p_qb * K_DB) / (S[:, 0] + K_DB); st.loc[idx, "qb_starts"] = n
    st = st.sort_values(["team", "season", "week", "game_id"]).reset_index(drop=True)
    prev = st.groupby("team")["qb"].shift(1); prev_season = st.groupby("team")["season"].shift(1)
    st["qb_change"] = ((prev.notna()) & (prev != st["qb"]) & (prev_season == st["season"])).astype(float)
    st["qb_new"] = (st["qb_starts"] <= 3).astype(float)
    for s in ("h", "a"):
        t = st[st["side"] == s][["game_id", "qb_epa", "qb_change", "qb_new", "qb_starts"]].rename(
            columns={c: f"{s}_{c}" for c in ["qb_epa", "qb_change", "qb_new", "qb_starts"]})
        g = g.merge(t, on="game_id", how="left")
    g["f_qb_epa_diff"] = g["h_qb_epa"] - g["a_qb_epa"]; g["f_qb_epa_sum"] = g["h_qb_epa"] + g["a_qb_epa"]
    g["f_qb_change_diff"] = g["h_qb_change"] - g["a_qb_change"]; g["f_qb_change_sum"] = g["h_qb_change"] + g["a_qb_change"]
    g["f_qb_new_diff"] = g["h_qb_new"] - g["a_qb_new"]; g["f_qb_new_sum"] = g["h_qb_new"] + g["a_qb_new"]

    # ---- coaching tenure PROXIES (head coach only; play-caller identity is not available)
    c = pd.concat([pd.DataFrame({"game_id": g["game_id"], "team": g["home_team"], "coach": g["home_coach"], "season": g["season"], "week": g["week"], "side": "h"}),
                   pd.DataFrame({"game_id": g["game_id"], "team": g["away_team"], "coach": g["away_coach"], "season": g["season"], "week": g["week"], "side": "a"})], ignore_index=True)
    c["ct"] = c["coach"].fillna("UNK") + "|" + c["team"]; c["one"] = 1.0
    idx, S, N, n = _ewma(c, "ct", ["one"], 1e9, carry=1.0); c.loc[idx, "ten"] = n
    c["new"] = (c["ten"] < 8).astype(float); c["logten"] = np.log1p(c["ten"].clip(upper=100))
    for s in ("h", "a"):
        t = c[c["side"] == s][["game_id", "new", "logten"]].rename(columns={"new": f"{s}_cnew", "logten": f"{s}_clog"})
        g = g.merge(t, on="game_id", how="left")
    g["f_cnew_diff"] = g["h_cnew"] - g["a_cnew"]; g["f_cnew_sum"] = g["h_cnew"] + g["a_cnew"]
    g["f_clog_diff"] = g["h_clog"] - g["a_clog"]; g["f_clog_sum"] = g["h_clog"] + g["a_clog"]

    # ---- rest / venue / schedule (known pregame) and observed weather (NON_PIT: game-time observation)
    g["f_rest_diff"] = (g["home_rest"] - g["away_rest"]).clip(-7, 7); g["f_rest_min"] = np.minimum(g["home_rest"], g["away_rest"]).clip(3, 14)
    g["f_short"] = ((g["home_rest"] <= 5) | (g["away_rest"] <= 5)).astype(float)
    g["f_div"] = g["div_game"].astype(float); g["f_dome"] = g["roof"].isin(["dome", "closed"]).astype(float)
    outdoor = g["roof"].isin(["outdoors", "open"])
    g["w_temp"] = np.where(outdoor, g["temp"], 70.0); g["w_wind"] = np.where(outdoor, g["wind"], 0.0)
    g["w_temp"] = g["w_temp"].fillna(60.0); g["w_wind"] = g["w_wind"].fillna(5.0)
    g["f_spread"] = g["spread_line"]; g["f_spread_sq"] = g["spread_line"] ** 2; g["f_total_line"] = g["total_line"]
    g["f_abs_spread"] = g["spread_line"].abs()

    # ---- centred interaction terms (centres are means over FIT seasons only)
    fg = g["season"].isin(fit) & (g["season"] >= HISTORY_START + 2)
    def cen(col): return g[col] - g.loc[fg, col].mean()
    for nm, x in (("pass", "pass_epa"), ("rush", "rush_epa"), ("expl", "expl_pass")):
        ho, hd, ao, ad = cen(f"h_off_{x}"), cen(f"h_def_{x}"), cen(f"a_off_{x}"), cen(f"a_def_{x}")
        g[f"i_{nm}_m"] = ho * ad - ao * hd; g[f"i_{nm}_s"] = ho * ad + ao * hd
    g["i_pace_s"] = cen("h_off_sec_per_play") * cen("a_off_sec_per_play")
    g["i_pace_m"] = cen("h_off_sec_per_play") * cen("a_def_sec_per_play") - cen("a_off_sec_per_play") * cen("h_def_sec_per_play")
    g["i_press_m"] = cen("h_qb_epa") * cen("a_def_hit") - cen("a_qb_epa") * cen("h_def_hit")
    g["i_press_s"] = cen("h_qb_epa") * cen("a_def_hit") + cen("a_qb_epa") * cen("h_def_hit")
    g["i_coach_m"] = g["h_cnew"] * cen("a_def_neutral_pass_rate") - g["a_cnew"] * cen("h_def_neutral_pass_rate")
    g["i_coach_s"] = g["h_cnew"] * cen("a_def_neutral_pass_rate") + g["a_cnew"] * cen("h_def_neutral_pass_rate")
    g = g.sort_values(["season", "week", "game_id"]).reset_index(drop=True)
    g.to_parquet(path)
    verbose(f"features {Y}: {len(g)} games, {g.shape[1]} cols")
    return g
