#!/usr/bin/env python3
"""Experiment 1 (RESEARCH_ONLY): do pregame-known coaching / offensive tendencies improve the incumbent's
team plays, pass-rate and dropback forecasts?

Reuses the incumbent unchanged: data.team_games, features.team_features / fit_priors, models.fit_game_env
with its research-arm hooks (plays_extra / pass_rate_extra / opponent_def).  Writes only under
research/coaching_tendencies_exp1/.  Touches no production artifact.

Usage: python scripts/sim/coaching_tendencies_exp1.py [--seasons 2021,2022,2023,2024,2025]
"""
from __future__ import annotations
import argparse, json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
import numpy as np
import pandas as pd
import polars as pl
from math import erf, sqrt, pi
from nfl_edge.sim import data as D, features as F, models as M
from nfl_edge.sim.training import WARMUP_SEASONS

OUT = os.path.join(ROOT, "research", "coaching_tendencies_exp1")
CFG = F.FEATURE_CONFIG
HISTORY_START = 2016
K = CFG.team_shrink_k
MIN_PRIOR = 4          # the incumbent's own filter (fit_game_env: team_n_prior >= 4)

# ----------------------------------------------------------------------------------- extra per-game columns
def extra_team_games(season: int) -> pd.DataFrame:
    """Per team-game counts the incumbent does not carry: early-down neutral passes, no-huddle plays."""
    path = os.path.join(D.RAW, "pbp", f"play_by_play_{season}.parquet")
    cols = ["game_id", "posteam", "play_type", "pass_attempt", "sack", "qb_scramble", "qtr", "wp", "score_differential",
            "down", "no_huddle", "season_type"]
    d = pl.read_parquet(path, columns=cols).filter(pl.col("posteam").is_not_null()
                                                    & pl.col("season_type").is_in(["REG", "POST"])
                                                    & pl.col("play_type").is_in(["run", "pass", "qb_kneel", "qb_spike"]))
    d = d.with_columns(pl.col("posteam").replace(D.TEAM_FIX).alias("team"))
    pas = ((pl.col("pass_attempt").fill_null(0) == 1) | (pl.col("sack").fill_null(0) == 1)
           | (pl.col("qb_scramble").fill_null(0) == 1))
    neutral = (pl.col("qtr") <= 3) & pl.col("wp").is_between(0.2, 0.8) & (pl.col("score_differential").abs() <= 8)
    ed = neutral & ((pl.col("down") == 1) | (pl.col("down") == 2))
    g = d.group_by(["game_id", "team"]).agg([
        (pas & ed).sum().alias("ed_pass_n"), ed.sum().alias("ed_n"),
        ((pl.col("no_huddle").fill_null(0) == 1) & neutral).sum().alias("nh_n"), neutral.sum().alias("neu_n")])
    return g.to_pandas()


def load_coaches() -> pd.DataFrame:
    g = pd.read_csv(os.path.join(D.RAW, "schedules", "games.csv"),
                    usecols=["game_id", "home_team", "away_team", "home_coach", "away_coach", "spread_line", "total_line"])
    for c in ("home_team", "away_team"):
        g[c] = g[c].replace(D.TEAM_FIX)
    h = g.rename(columns={"home_team": "team", "home_coach": "coach"})[["game_id", "team", "coach", "spread_line", "total_line"]]
    h["margin_line"] = h["spread_line"]
    a = g.rename(columns={"away_team": "team", "away_coach": "coach"})[["game_id", "team", "coach", "spread_line", "total_line"]]
    a["margin_line"] = -a["spread_line"]
    return pd.concat([h, a], ignore_index=True)[["game_id", "team", "coach", "margin_line", "total_line"]]


# ----------------------------------------------------------------------------------------- challenger features
def _ewma(df: pd.DataFrame, group: str, cols: list[str], halflife: float):
    """Prior-only decayed sums grouped by ``group`` (rows are re-sorted; result aligned back to df.index)."""
    s = df.sort_values([group, "season", "week", "game_id"])
    X = s[cols].to_numpy(float)
    S, N, n = F.decayed_prior_sums(s[group].to_numpy(), None, s["season"].to_numpy(), X, halflife, CFG.team_season_carry)
    return s.index, S, N, n


def _shrunk_rate(S_num, S_den, prior_rate, prior_den):
    den_prior = K * prior_den
    return (S_num + prior_rate * den_prior) / (S_den + den_prior)


def build_features(tf: pd.DataFrame, ex: pd.DataFrame, coaches: pd.DataFrame, fit_seasons: list[int]) -> pd.DataFrame:
    """Add the challenger columns to the incumbent's team-feature frame.  Every league constant is fitted on
    raw rows of ``fit_seasons`` (strictly before the evaluation season)."""
    d = tf.merge(ex, on=["game_id", "team"], how="left").merge(coaches, on=["game_id", "team"], how="left")
    d["ed_rate"] = d["ed_pass_n"] / d["ed_n"].where(d["ed_n"] > 0)
    d["nh_rate"] = d["nh_n"] / d["neu_n"].where(d["neu_n"] > 0)
    fit = d[d["season"].isin(fit_seasons)]
    p_ed = fit["ed_pass_n"].sum() / max(1.0, fit["ed_n"].sum()); p_ed_den = fit["ed_n"].mean()
    p_nh = fit["nh_n"].sum() / max(1.0, fit["neu_n"].sum()); p_nh_den = fit["neu_n"].mean()
    p_np = fit["neutral_pass_rate"].mean(); p_sec = fit["sec_per_play"].mean()
    d = d.sort_values(["team", "season", "week", "game_id"]).reset_index(drop=True)

    # ---- family A: the team's own tendencies (long window = incumbent halflife; short window = identity shift)
    for hl, tag in ((CFG.team_halflife, "L"), (3.0, "S")):
        idx, S, N, n = _ewma(d, "team", ["ed_pass_n", "ed_n", "nh_n", "neu_n", "neutral_pass_rate"], hl)
        z = pd.DataFrame(index=idx)
        z[f"ed_{tag}"] = _shrunk_rate(S[:, 0], S[:, 1], p_ed, p_ed_den)
        z[f"nh_{tag}"] = _shrunk_rate(S[:, 2], S[:, 3], p_nh, p_nh_den)
        z[f"np_{tag}"] = (S[:, 4] + p_np * K) / (N[:, 4] + K)
        for c in z.columns:
            d.loc[z.index, c] = z[c].to_numpy()
    d["a_ed_pass"] = d["ed_L"]
    d["a_nohuddle"] = d["nh_L"]
    d["a_np_shift"] = d["np_S"] - d["np_L"]               # recent change in offensive identity (short minus long)

    # ---- family B: head-coach tenure proxies (the head coach is NOT assumed to call plays)
    d["coach"] = d["coach"].fillna("UNKNOWN")
    d["coach_team"] = d["coach"] + "|" + d["team"]
    idx, S, N, n = _ewma(d, "coach", ["neutral_pass_rate", "sec_per_play"], CFG.team_halflife)
    d.loc[idx, "c_np"] = (S[:, 0] + p_np * K) / (N[:, 0] + K)
    d.loc[idx, "c_sec"] = (S[:, 1] + p_sec * K) / (N[:, 1] + K)
    d.loc[idx, "c_games"] = n
    idx, S, N, n = _ewma(d, "coach_team", ["neutral_pass_rate"], CFG.team_halflife)
    d.loc[idx, "c_team_games"] = n
    unk = d["coach"] == "UNKNOWN"
    d["b_new"] = ((d["c_team_games"] < 8) & ~unk).astype(float)
    d["b_logten"] = np.log1p(d["c_team_games"].clip(upper=100)).where(~unk, 0.0)
    d["b_np_gap"] = (d["c_np"] - d["np_L"]).where(~unk, 0.0)      # coach's own history vs the team's history
    d["b_sec_gap"] = (d["c_sec"] - d["sec_per_play_L"] if "sec_per_play_L" in d else d["c_sec"] - d["off_sec_per_play"]).where(~unk, 0.0)
    d["b_np_gap_new"] = d["b_np_gap"] * d["b_new"]
    d["b_sec_gap_new"] = d["b_sec_gap"] * d["b_new"]

    # ---- family C: the opponent's defensive response (opponent-keyed; opp-adjusted by the offence's own prior level)
    d["ind_np"] = d["neutral_pass_rate"] - d["off_neutral_pass_rate"]
    d["ind_sec"] = d["sec_per_play"] - d["off_sec_per_play"]
    idx, S, N, n = _ewma(d, "opp", ["ind_np", "ind_sec", "ed_pass_n", "ed_n"], CFG.team_halflife)
    d.loc[idx, "c_ind_np"] = S[:, 0] / (N[:, 0] + K)               # shrunk toward 0: no induced shift
    d.loc[idx, "c_ind_sec"] = S[:, 1] / (N[:, 1] + K)
    d.loc[idx, "c_ed_allowed"] = _shrunk_rate(S[:, 2], S[:, 3], p_ed, p_ed_den)
    return d


ARMS = {
    "B0": {},
    "B1": {"plays_extra": ["a_nohuddle", "a_ed_pass"], "pass_rate_extra": ["a_ed_pass", "a_nohuddle", "a_np_shift"]},
    "B2": {"plays_extra": ["b_sec_gap", "b_sec_gap_new", "b_new", "b_logten"],
           "pass_rate_extra": ["b_np_gap", "b_np_gap_new", "b_new", "b_logten"]},
    "B3": {"plays_extra": ["c_ind_sec", "c_ind_np"], "pass_rate_extra": ["c_ind_np", "c_ed_allowed"]},
    "CTL_A4": {"opponent_def": True},     # control: the incumbent's train/serve skew repaired (arm A4, already rejected)
    # POST-HOC attribution arm (added after B3 beat B0 by more than the control explained): B3 features on top of the repair
    "B3_ON_A4": {"opponent_def": True, "plays_extra": ["c_ind_sec", "c_ind_np"], "pass_rate_extra": ["c_ind_np", "c_ed_allowed"]},
}
ALL_NEW = ["a_nohuddle", "a_ed_pass", "a_np_shift", "b_sec_gap", "b_sec_gap_new", "b_new", "b_logten", "b_np_gap",
           "b_np_gap_new", "c_ind_sec", "c_ind_np", "c_ed_allowed"]


# ------------------------------------------------------------------------------------------------ evaluation
def fit_predict(train: pd.DataFrame, test: pd.DataFrame, arm: dict) -> pd.DataFrame:
    pf = M.PLAYS_FEATURES + list(arm.get("plays_extra", []))
    prf = M.PASS_RATE_FEATURES + list(arm.get("pass_rate_extra", []))
    od = bool(arm.get("opponent_def"))
    env = M.fit_game_env(train, plays_features=pf, pass_rate_features=prf, opponent_def=od)
    def design(t):
        return M._env_design(M._with_opponent_def(t) if od else t)
    dtr = design(train[train["team_n_prior"] >= MIN_PRIOR]); dte = design(test)
    out = {}
    for nm, feats, key in (("plays", pf, "plays"), ("pr", prf, "pass_rate")):
        m = env["plays"] if nm == "plays" else env["pass_rate"]
        tr_res = dtr[key].to_numpy(float) - M.ridge_predict(m, dtr[feats].to_numpy(float))
        out[nm] = M.ridge_predict(m, dte[feats].to_numpy(float)); out[nm + "_sd"] = float(np.std(tr_res))
    # sigma for the derived dropback forecast: training residual of plays_hat * pr_hat
    dr_tr = M.ridge_predict(env["plays"], dtr[pf].to_numpy(float)) * M.ridge_predict(env["pass_rate"], dtr[prf].to_numpy(float))
    sd_db = float(np.std(dtr["dropbacks"].to_numpy(float) - dr_tr))
    ratio_att = float(dtr["pass_att"].sum() / dtr["dropbacks"].sum())
    r = test[["game_id", "team", "season", "plays", "pass_rate", "dropbacks", "pass_att"]].copy()
    r["plays_hat"] = out["plays"]; r["pr_hat"] = out["pr"]
    r["db_hat"] = r["plays_hat"] * r["pr_hat"]; r["att_hat"] = r["db_hat"] * ratio_att
    r["sd_plays"] = out["plays_sd"]; r["sd_pr"] = out["pr_sd"]; r["sd_db"] = sd_db
    return r.reset_index(drop=True)


def _crps_gauss(y, mu, sd):
    z = (y - mu) / sd
    pdf = np.exp(-0.5 * z ** 2) / sqrt(2 * pi)
    cdf = 0.5 * (1 + np.vectorize(erf)(z / sqrt(2)))
    return sd * (z * (2 * cdf - 1) + 2 * pdf - 1 / sqrt(pi))


TARGETS = {"plays": ("plays", "plays_hat", "sd_plays"), "pass_rate": ("pass_rate", "pr_hat", "sd_pr"),
           "dropbacks": ("dropbacks", "db_hat", "sd_db")}


def losses(r: pd.DataFrame) -> pd.DataFrame:
    o = r[["game_id", "season"]].copy()
    for t, (y, h, s) in TARGETS.items():
        e = r[y] - r[h]
        o[f"{t}_ae"] = e.abs(); o[f"{t}_se"] = e ** 2; o[f"{t}_crps"] = _crps_gauss(r[y].to_numpy(float), r[h].to_numpy(float), r[s].to_numpy(float))
        o[f"{t}_c50"] = (e.abs() <= 0.6745 * r[s]).astype(float); o[f"{t}_c90"] = (e.abs() <= 1.6449 * r[s]).astype(float)
        o[f"{t}_bias"] = e
    o["rate_wse"] = r["plays"] * (r["pass_rate"] - r["pr_hat"]) ** 2     # play-weighted Brier component for pass rate
    o["att_ae"] = (r["pass_att"] - r["att_hat"]).abs()
    return o


def rel(base: pd.DataFrame, arm: pd.DataFrame, col: str, rmse=False) -> float:
    a, b = arm[col].sum(), base[col].sum()
    return float(np.sqrt(a / b) - 1) if rmse else float(a / b - 1)


def boot(base: pd.DataFrame, arm: pd.DataFrame, col: str, rmse=False, reps=2000, seed=7):
    gb = base.groupby("game_id")[col].sum(); ga = arm.groupby("game_id")[col].sum().reindex(gb.index)
    rng = np.random.default_rng(seed); n = len(gb); a = ga.to_numpy(); b = gb.to_numpy()
    idx = rng.integers(0, n, size=(reps, n))
    ra = a[idx].sum(1); rb = b[idx].sum(1)
    v = np.sqrt(ra / rb) - 1 if rmse else ra / rb - 1
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def pit_check(tf_fn, tg, ex, coaches, fit_seasons, season) -> dict:
    """Perturb one mid-season game's raw outcome columns by x1000 and confirm no challenger feature of that game
    or any earlier row moves, while a later row of the same team does (negative control)."""
    base = tf_fn(tg, ex)
    g = tg[(tg["season"] == season) & (tg["week"] == 10)].iloc[0]
    gid, team = g["game_id"], g["team"]
    tg2, ex2 = tg.copy(), ex.copy()
    cols = ["neutral_pass_rate", "sec_per_play", "plays", "pass_rate", "proe", "neutral_proe", "dropbacks"]
    m = tg2["game_id"] == gid
    tg2.loc[m, cols] = tg2.loc[m, cols].to_numpy(float) * 1000
    m2 = ex2["game_id"] == gid
    ex2.loc[m2, ["ed_pass_n", "ed_n", "nh_n", "neu_n"]] *= 1000
    pert = tf_fn(tg2, ex2)
    key = base[["game_id", "team", "season", "week"]]
    cur = (key["season"] < season) | ((key["season"] == season) & (key["week"] <= 10))
    same = {}
    for c in ALL_NEW:
        a, b = base[c].to_numpy(float), pert[c].to_numpy(float)
        # a game's own feature and every earlier row of ANY team must not move, EXCEPT the opposing side's
        # defensive-response features (opp-keyed) for the perturbed game's own row is the offence's, not its history
        moved = ~np.isclose(a, b, equal_nan=True) & cur.to_numpy()
        # the perturbed game may legitimately change features of rows AFTER it only; rows at <= week 10: none
        moved &= ~((key["game_id"] == gid).to_numpy() & False)
        same[c] = int(moved.sum())
    later = ((key["season"] > season) | ((key["season"] == season) & (key["week"] > 10)))
    ctrl = {c: int((~np.isclose(base[c].to_numpy(float), pert[c].to_numpy(float), equal_nan=True) & later.to_numpy()).sum())
            for c in ALL_NEW}
    return {"game": gid, "rows_moved_at_or_before": same, "rows_moved_after_control": ctrl}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--seasons", default="2021,2022,2023,2024,2025")
    ap.add_argument("--no-pit", action="store_true")
    args = ap.parse_args(); seasons = [int(s) for s in args.seasons.split(",")]
    os.makedirs(OUT, exist_ok=True)
    coaches = load_coaches()
    ex_all = pd.concat([extra_team_games(s) for s in range(HISTORY_START, max(seasons) + 1)], ignore_index=True)
    res = {"meta": {"seasons": seasons, "history_start": HISTORY_START, "train_start": HISTORY_START + WARMUP_SEASONS,
                    "min_prior_games": MIN_PRIOR, "arms": ARMS}, "rows": {}, "pit": None}
    per_game_losses = {"A": {}, "P": {}}
    empty_pg = pd.DataFrame({"position": [], **{c: [] for c in sum([list(v) for v in F.PLAYER_RATES.values()], [])}})
    for Y in seasons:
        yrs = list(range(HISTORY_START, Y + 1)); fit_seasons = list(range(HISTORY_START, Y))
        tg = D.load("team_games", yrs).to_pandas()
        priors = F.fit_priors(tg[tg["season"].isin(fit_seasons)], empty_pg, fit_seasons=fit_seasons)
        def make(tg_, ex_):
            tf_ = F.team_features(tg_, CFG, priors)
            return build_features(tf_, ex_, coaches, fit_seasons)
        tf = make(tg, ex_all[ex_all["game_id"].str[:4].astype(int) <= Y])
        if Y == seasons[len(seasons) // 2] and not args.no_pit:
            exY = ex_all[ex_all["game_id"].str[:4].astype(int) <= Y]
            res["pit"] = {"season": Y, **pit_check(make, tg, exY, coaches, fit_seasons, Y)}
        # sanity: the incumbent's own team features must be reproduced exactly by the wrapped frame
        train = tf[tf["season"].isin(range(HISTORY_START + WARMUP_SEASONS, Y))]
        test = tf[(tf["season"] == Y) & (tf["team_n_prior"] >= MIN_PRIOR)]
        for mode in ("A", "P"):
            tr, te = train.copy(), test.copy()
            if mode == "P":   # pregame variant: realised margin/total replaced by the (near-close) consensus line
                for t_ in (tr, te):
                    t_["margin"] = t_["margin_line"]; t_["total"] = t_["total_line"]
                tr = tr[tr["margin_line"].notna() & tr["total_line"].notna()]; te = te[te["margin_line"].notna() & te["total_line"].notna()]
            for name, arm in ARMS.items():
                r = fit_predict(tr, te, arm)
                per_game_losses[mode].setdefault(name, []).append(losses(r))
        print(f"{Y}: train rows {len(train[train['team_n_prior'] >= MIN_PRIOR])}, test rows {len(test)}", flush=True)

    rows = res["rows"]
    for mode in ("A", "P"):
        L = {n: pd.concat(v, ignore_index=True) for n, v in per_game_losses[mode].items()}
        base = L["B0"]
        rows[mode] = {}
        for n, l in L.items():
            e = {"n": int(len(l))}
            for t in TARGETS:
                e[t] = {"MAE": float(l[f"{t}_ae"].mean()), "RMSE": float(np.sqrt(l[f"{t}_se"].mean())),
                        "CRPS_gauss": float(l[f"{t}_crps"].mean()), "cov50": float(l[f"{t}_c50"].mean()),
                        "cov90": float(l[f"{t}_c90"].mean()), "bias": float(l[f"{t}_bias"].mean())}
            e["rate_wMSE"] = float(l["rate_wse"].sum() / 1.0 / max(1, len(l)))
            e["att_MAE"] = float(l["att_ae"].mean())
            if n != "B0":
                d = {}
                for t in TARGETS:
                    d[t] = {"rel_MAE": rel(base, l, f"{t}_ae"), "rel_RMSE": rel(base, l, f"{t}_se", True),
                            "rel_CRPS": rel(base, l, f"{t}_crps"), "CRPS_ci95": boot(base, l, f"{t}_crps"),
                            "MAE_ci95": boot(base, l, f"{t}_ae"),
                            "by_season_rel_CRPS": {int(s): rel(base[base.season == s], l[l.season == s], f"{t}_crps")
                                                   for s in sorted(l.season.unique())}}
                d["rate_wMSE_rel"] = rel(base, l, "rate_wse"); d["att_MAE_rel"] = rel(base, l, "att_ae")
                e["vs_B0"] = d
            if n in ("B3", "B3_ON_A4") and "CTL_A4" in L:
                ctl = L["CTL_A4"]
                e["vs_CTL_A4"] = {t: {"rel_MAE": rel(ctl, l, f"{t}_ae"), "rel_RMSE": rel(ctl, l, f"{t}_se", True),
                                      "rel_CRPS": rel(ctl, l, f"{t}_crps"), "CRPS_ci95": boot(ctl, l, f"{t}_crps"),
                                      "by_season_rel_CRPS": {int(s): rel(ctl[ctl.season == s], l[l.season == s], f"{t}_crps")
                                                             for s in sorted(l.season.unique())}} for t in TARGETS}
            rows[mode][n] = e
    with open(os.path.join(OUT, "results.json"), "w") as f:
        json.dump(res, f, indent=1, default=str)
    print("wrote", os.path.join(OUT, "results.json"))


if __name__ == "__main__":
    main()
