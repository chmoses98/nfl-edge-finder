#!/usr/bin/env python3
"""Why does PURE_PLAYER_V1 trail DATA_PLAYER_V4? Error decomposition on the matched held-out player-games (research only).

Population: the PURE_PLAYER_V1 held-out comparison (2024 + 2025 regular season, each season forecast by models fitted
strictly before it), restricted to the (player, game, statistic) rows that every arm forecasts. One row per
player-game-statistic; MAE of the forecast mean; paired, game-clustered bootstrap (B = 1000, seed 20261010).

    1. component Shapley split of each paired gap (nfl_edge/research/pure_gap.py): volume / snap / usage / efficiency
    2. arm ladder: PURE -> V4_MEF_NO_AVAIL (V4 structure, no availability, no market) -> V4_MEF_AS_IS (+ injury report /
       roster / vacated-role features) -> V4_MARKET_CLOSE (+ closing spread / total)
    3. oracle split of each arm's own MAE (realised components substituted)
    4. availability strata (realised teammate absences / returns, own reduced role, own injury-report listing)
    5. opponent: gap by opponent-strength tercile, and residual opponent signal left in each arm (cross-season fit)

    python3 scripts/research/pure_gap_decomposition.py --arms <cache>/pure_gap_arms_2024_2025.pkl --data-root <root> \
        --out research/pure_gap
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.engines.player.pure_v1 import MODEL_NAME as PURE                       # noqa: E402
from nfl_edge.engines.player.pure_v1 import BASELINE_NAME as BASE                     # noqa: E402
from nfl_edge.engines.player.pure_v1_2 import features as F12                         # noqa: E402
from nfl_edge.research import pure_gap as G                                           # noqa: E402

V4_MKT, V4_MEF, V4_NOAV = "V4_MARKET_CLOSE", "V4_MEF_AS_IS", "V4_MEF_NO_AVAIL"
ARMS = [PURE, V4_NOAV, V4_MEF, V4_MKT]
STATS = ["snap_share", "targets", "receptions", "receiving_yards", "carries", "rushing_yards", "passing_attempts", "completions",
         "passing_yards"]
PAIRS = {"PURE_minus_V4_MARKET_CLOSE": (PURE, V4_MKT), "PURE_minus_V4_MEF_AS_IS": (PURE, V4_MEF),
         "PURE_minus_V4_MEF_NO_AVAIL": (PURE, V4_NOAV),
         "availability_features__V4_NO_AVAIL_minus_V4_MEF": (V4_NOAV, V4_MEF),
         "market_environment__V4_MEF_minus_V4_MKT": (V4_MEF, V4_MKT)}
OPP_FEATURE = {"targets": "o_rate_allowed", "receptions": "o_cmp_allowed", "receiving_yards": "o_ypt_allowed", "carries": "o_ra_allowed",
               "rushing_yards": "o_ypc_allowed", "passing_attempts": "o_rate_allowed", "completions": "o_cmp_allowed",
               "passing_yards": "o_ypa_allowed"}


def r6(x):
    return None if x is None or not np.isfinite(x) else round(float(x), 6)


# ------------------------------------------------------------------------------------------------ assembly
def wide(arms: dict, stat: str) -> pd.DataFrame:
    """Matched rows of `stat`: y, each arm's mean / opportunity mean / volume / snap, realised components, context."""
    k = ["game_id", "player_id"]
    L = arms["long"]; P = arms["pure_inter"]
    base = L[PURE][L[PURE].statistic == stat][k + ["season", "pgroup", "team", "opponent_team", "actual"]].rename(columns={"actual": "y"})
    opp = G.OPPORTUNITY.get(stat)
    for a in ARMS:
        m = L[a][L[a].statistic == stat][k + ["mean"]].rename(columns={"mean": f"mean_{a}"})
        base = base.merge(m, on=k, how="inner")
        if opp:
            o = L[a][L[a].statistic == opp][k + ["mean", "actual"]].rename(columns={"mean": f"opp_{a}", "actual": f"oppact_{a}"})
            base = base.merge(o, on=k, how="inner")
        inter = P[k + ["vol_pa", "vol_ra", "snap_mean"]] if a == PURE else arms["inter"][a][k + ["vol_pa", "vol_ra", "snap_mean"]]
        base = base.merge(inter.drop_duplicates(k).rename(columns={c: f"{c}_{a}" for c in ("vol_pa", "vol_ra", "snap_mean")}), on=k, how="left")
    ctx = P[k + ["pa", "ra", "snap_share", "e_snap_share", "gap_gt0", "o_cmp_allowed", "o_ypt_allowed", "o_ypc_allowed", "o_ypa_allowed",
                 "o_rate_allowed", "week", "kickoff"]].drop_duplicates(k)
    base = base.merge(ctx, on=k, how="left")
    base = base.merge(arms["teams"][["team", "game_id", "o_ra_allowed", "o_pa_allowed"]], on=["team", "game_id"], how="left")
    if opp:
        base["opp_act"] = base[f"oppact_{PURE}"]
    return base.reset_index(drop=True)


def comps(w: pd.DataFrame, stat: str, a: str) -> dict:
    if stat == "snap_share":
        return G.factorize(stat, w[f"mean_{a}"], None, None, None)
    vol = G.VOLUME[stat]
    return G.factorize(stat, w[f"mean_{a}"], w[f"opp_{a}"], w[f"{vol}_{a}"], w[f"snap_mean_{a}"])


def comps_actual(w: pd.DataFrame, stat: str, model_comp: dict) -> dict:
    if stat == "snap_share":
        return {"snap": w["y"].to_numpy(float)}
    vol = G.ACTUAL_VOLUME[G.VOLUME[stat]]
    return G.factorize_actual(stat, w["y"], w["opp_act"], w[vol], w["snap_share"], model_comp)


# ------------------------------------------------------------------------------------------------ analyses
def gap_shapley(w, stat, a, b, B):
    ca, cb = comps(w, stat, a), comps(w, stat, b)
    names = G.components(stat)
    phi = G.shapley_abs_error(w["y"], ca, cb, names)
    g = w["game_id"].to_numpy()
    ea = np.abs(w[f"mean_{a}"] - w["y"]).to_numpy(); eb = np.abs(w[f"mean_{b}"] - w["y"]).to_numpy()
    exact = float(np.max(np.abs(phi["_total"] - (ea - eb))))
    return {"n": int(len(w)), "n_games": int(len(set(g))), "mae_a": r6(ea.mean()), "mae_b": r6(eb.mean()),
            "gap": G.summarize(ea - eb, g, B), "components": {k: G.summarize(phi[k], g, B) for k in names},
            "max_abs_factorisation_error": r6(exact)}, phi


def oracle_split(w, stat, a, B):
    ca = comps(w, stat, a)
    cact = comps_actual(w, stat, ca)
    names = G.components(stat)
    phi = G.shapley_abs_error(w["y"], ca, cact, names)
    g = w["game_id"].to_numpy()
    resid = np.abs(phi["_total"] - np.abs(w[f"mean_{a}"] - w["y"]).to_numpy())   # v(all actual) should be ~0
    return {"mae": r6(np.abs(w[f"mean_{a}"] - w["y"]).mean()), "components": {k: G.summarize(phi[k], g, B) for k in names},
            "share_of_mae": {k: r6(phi[k].mean() / max(np.abs(w[f"mean_{a}"] - w["y"]).mean(), 1e-9)) for k in names},
            "unexplained_after_all_oracles": r6(resid.mean())}


def availability_flags(arms: dict, w: pd.DataFrame, data_root: str) -> pd.DataFrame:
    """Realised (hindsight) availability events per row -- DIAGNOSTIC strata, never model inputs."""
    rows, t = arms["rows"], arms["teams"]
    pl_ = rows[rows["played"]][["player_id", "team", "game_id", "pgroup", "kickoff", "target_share", "carry_share", "e_target_share",
                                "e_carry_share", "gap_gt0"]].copy()
    pl_ = pl_.merge(t[["team", "game_id", "team_seq", "season", "starter"]], on=["team", "game_id"], how="left")
    pl_ = pl_.sort_values(["player_id", "kickoff"])
    gp = pl_.groupby("player_id")
    pl_["r3_t"] = gp["target_share"].transform(lambda x: x.rolling(3, min_periods=1).mean())
    pl_["r3_c"] = gp["carry_share"].transform(lambda x: x.rolling(3, min_periods=1).mean())
    tg = t[["team", "game_id", "team_seq", "season", "starter"]]
    cur = w[["player_id", "game_id", "team", "pgroup"]].merge(tg, on=["team", "game_id"], how="left")
    prev = tg.rename(columns={"game_id": "prev_game", "team_seq": "prev_seq", "season": "prev_season", "starter": "prev_starter"})
    cur["prev_seq"] = cur["team_seq"] - 1
    cur = cur.merge(prev, on=["team", "prev_seq"], how="left")
    played_g = set(zip(pl_.player_id, pl_.team, pl_.game_id))
    # teammates who played the previous team-game with a recent share, and are absent from this game
    prevp = pl_[["player_id", "team", "game_id", "pgroup", "r3_t", "r3_c"]].rename(columns={"game_id": "prev_game", "player_id": "mate",
                                                                                         "pgroup": "mate_group"})
    tm = cur[["player_id", "game_id", "team", "pgroup", "prev_game", "season", "prev_season"]].merge(prevp, on=["team", "prev_game"], how="inner")
    tm = tm[(tm.mate != tm.player_id) & (tm.season == tm.prev_season)]
    tm["absent"] = [(m, tt, g) not in played_g for m, tt, g in zip(tm.mate, tm.team, tm.game_id)]
    tm = tm[tm.absent]
    same = tm[tm.mate_group == tm.pgroup]
    va_t = same.groupby(["player_id", "game_id"])["r3_t"].sum(); va_c = same.groupby(["player_id", "game_id"])["r3_c"].sum()
    # teammates of the same group who return this game after missing the previous team-game (prior-only share >= .10)
    ret = pl_[(pl_.gap_gt0 > 0)][["player_id", "team", "game_id", "pgroup", "e_target_share", "e_carry_share"]].rename(
        columns={"player_id": "mate", "pgroup": "mate_group"})
    rt = cur[["player_id", "game_id", "team", "pgroup"]].merge(ret, on=["team", "game_id"], how="inner")
    rt = rt[(rt.mate != rt.player_id) & (rt.mate_group == rt.pgroup)]
    rt_t = rt.groupby(["player_id", "game_id"])["e_target_share"].sum(); rt_c = rt.groupby(["player_id", "game_id"])["e_carry_share"].sum()
    f = w[["player_id", "game_id"]].copy()
    key = list(zip(f.player_id, f.game_id))
    f["vac_t"] = [va_t.get(x, 0.0) for x in key]; f["vac_c"] = [va_c.get(x, 0.0) for x in key]
    f["ret_t"] = [rt_t.get(x, 0.0) for x in key]; f["ret_c"] = [rt_c.get(x, 0.0) for x in key]
    cur = cur.set_index(["player_id", "game_id"])
    qb_change = (cur["starter"] != cur["prev_starter"]) & cur["prev_starter"].notna() & (cur["season"] == cur["prev_season"])
    f["team_qb_change"] = [bool(qb_change.get(x, False)) for x in key]
    # own injury-report designation (nflverse injuries, final weekly report; 2024 certified PIT, 2025 NOT -- label only)
    inj = []
    for s in sorted(w.season.unique()):
        p = os.path.join(data_root, "data/raw/nflverse/injuries", f"injuries_{s}.parquet")
        if os.path.exists(p):
            d = pd.read_parquet(p, columns=["season", "week", "gsis_id", "report_status", "game_type"])
            inj.append(d[d.game_type == "REG"])
    inj = pd.concat(inj) if inj else pd.DataFrame(columns=["season", "week", "gsis_id", "report_status"])
    inj = inj.dropna(subset=["gsis_id"]).drop_duplicates(["season", "week", "gsis_id"], keep="last")
    st = w[["player_id", "season", "week"]].merge(inj.rename(columns={"gsis_id": "player_id"}), on=["player_id", "season", "week"], how="left")
    f["own_listed"] = st["report_status"].astype(str).str.lower().isin(["questionable", "doubtful"]).to_numpy()
    return f


def strata(w, flags, stat, B):
    kind = "c" if stat in ("carries", "rushing_yards") else "t"
    masks = {
        "teammate_new_absence_same_group_ge_0.10": flags[f"vac_{kind}"].to_numpy() >= 0.10,
        "teammate_return_same_group_ge_0.10": flags[f"ret_{kind}"].to_numpy() >= 0.10,
        "own_return_after_missed_games": w["gap_gt0"].fillna(0).to_numpy() > 0,
        "own_injury_report_Q_or_D": flags["own_listed"].to_numpy(bool),
        "own_reduced_role_realised_snap_lt_half_prior": ((w["snap_share"] < 0.5 * w["e_snap_share"]) & (w["e_snap_share"] >= 0.4)).fillna(False).to_numpy(),
        "team_starting_qb_changed": flags["team_qb_change"].to_numpy(bool),
    }
    anym = np.zeros(len(w), bool)
    for m in masks.values():
        anym |= m
    masks["any_availability_event"] = anym
    masks["no_availability_event"] = ~anym
    g = w["game_id"].to_numpy()
    out = {}
    for pname, (a, b) in PAIRS.items():
        diff = (np.abs(w[f"mean_{a}"] - w["y"]) - np.abs(w[f"mean_{b}"] - w["y"])).to_numpy()
        out[pname] = {"pooled_gap": G.summarize(diff, g, B), **{k: G.contribution(diff, m, g, B) for k, m in masks.items()}}
    return out


def opponent_terciles(w, stat, B):
    col = OPP_FEATURE.get(stat)
    if col is None:
        return None
    x = w[col].to_numpy(float)
    q = np.nanquantile(x, [1 / 3, 2 / 3])
    lab = np.where(x <= q[0], "allows_least", np.where(x <= q[1], "middle", "allows_most"))
    g = w["game_id"].to_numpy()
    out = {"feature": col, "cuts": [r6(q[0]), r6(q[1])]}
    for pname in ("PURE_minus_V4_MARKET_CLOSE", "PURE_minus_V4_MEF_AS_IS"):
        a, b = PAIRS[pname]
        diff = (np.abs(w[f"mean_{a}"] - w["y"]) - np.abs(w[f"mean_{b}"] - w["y"])).to_numpy()
        out[pname] = {t: G.contribution(diff, lab == t, g, B) for t in ("allows_least", "middle", "allows_most")}
    out["mean_bias"] = {t: {x: r6((w[f"mean_{x}"] - w["y"])[lab == t].mean()) for x in ARMS} for t in ("allows_least", "middle", "allows_most")}
    return out


def oracle_opponent(arms):
    """Hindsight opponent quality: each defence's allowed-to-group rates over the WHOLE season excluding the target game
    (uses future games -- an upper bound on what better opponent estimation could recover; diagnostic only)."""
    rows, t = arms["rows"], arms["teams"]
    tg = F12._group_totals(rows, t)
    num = [f"{c}_{g}" for g in F12.POS_GROUPS for c in F12.DEF_NUM] + ["pa", "ra"]
    s = tg.groupby(["opponent", "season"])[num].transform("sum")
    loo = s - tg[num]
    out = tg[["opponent", "game_id"]].rename(columns={"opponent": "opponent_team"}).copy()
    for g in F12.POS_GROUPS:
        out[f"or_tsh_{g}"] = loo[f"tgt_{g}"] / loo["pa"].clip(lower=1)
        out[f"or_cr_{g}"] = loo[f"rec_{g}"] / loo[f"tgt_{g}"].clip(lower=1)
        out[f"or_ypt_{g}"] = loo[f"ryd_{g}"] / loo[f"tgt_{g}"].clip(lower=1)
        out[f"or_csh_{g}"] = loo[f"car_{g}"] / loo["ra"].clip(lower=1)
        out[f"or_ypc_{g}"] = loo[f"rsh_{g}"] / loo[f"car_{g}"].clip(lower=1)
    return out


def _grp(w, table, pre):
    m = w[["opponent_team", "game_id", "pgroup"]].merge(table, on=["opponent_team", "game_id"], how="left")
    res = {}
    for r in ("tsh", "cr", "ypt", "csh", "ypc"):
        v = np.full(len(w), np.nan)
        for grp in F12.POS_GROUPS:
            c = f"{pre}{r}_{grp}"
            if c in m.columns:
                ix = (m["pgroup"] == grp).to_numpy()
                v[ix] = m.loc[ix, c].to_numpy(float)
        res[r] = v
    return res


def _lad(X, y, iters: int = 60):
    """Least-absolute-deviation regression by iteratively reweighted least squares (tiny ridge for stability)."""
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    for _ in range(iters):
        r = y - X @ beta
        w = 1.0 / np.maximum(np.abs(r), 1e-3)
        XtW = X.T * w
        new = np.linalg.solve(XtW @ X + 1e-8 * np.eye(X.shape[1]), XtW @ y)
        if np.max(np.abs(new - beta)) < 1e-9:
            return new
        beta = new
    return beta


def residual_signal(w, stat, feats: dict, B):
    """Cross-season linear correction of each arm's residual on opponent features (fit 2024 -> apply 2025 and back).
    Regressors mean * [1, z_1..z_k] (z standardised on the fitting season), fitted by least absolute deviations (the
    metric is MAE). Reports MAE(corrected with the feature set) - MAE(corrected with the scale term alone), clustered
    CI: < 0 means opponent signal the arm left on the table."""
    seasons = sorted(w.season.unique())
    if len(seasons) < 2:
        return None
    g = w["game_id"].to_numpy(); y = w["y"].to_numpy(float)
    out = {}
    for a in (PURE, V4_MKT, V4_MEF):
        mu = w[f"mean_{a}"].to_numpy(float)
        res = {}
        for fname, X in feats.items():
            corr = np.full(len(w), np.nan); corr0 = np.full(len(w), np.nan)
            for s in seasons:
                tr = (w.season != s).to_numpy(); te = ~tr
                Z = np.column_stack(X) if len(X) else np.zeros((len(w), 0))
                mz = np.nanmean(Z[tr], axis=0) if Z.shape[1] else np.zeros(0); sz = np.nanstd(Z[tr], axis=0) if Z.shape[1] else np.zeros(0)
                sz = np.where(sz > 1e-9, sz, 1.0)
                Zs = np.nan_to_num((Z - mz) / sz)
                D = np.column_stack([mu, mu[:, None] * Zs]) if Zs.shape[1] else mu[:, None]
                ok = tr & np.isfinite(y)
                beta = _lad(D[ok], (y - mu)[ok])
                corr[te] = mu[te] + D[te] @ beta
                b0 = _lad(mu[ok][:, None], (y - mu)[ok])
                corr0[te] = mu[te] * (1 + b0[0])
            lo = 0.0 if stat == "snap_share" else None
            if lo is not None:
                corr = np.clip(corr, 0, 1); corr0 = np.clip(corr0, 0, 1)
            else:
                corr = np.maximum(corr, 0); corr0 = np.maximum(corr0, 0)
            d_feat = np.abs(corr - y) - np.abs(corr0 - y)
            res[fname] = G.summarize(d_feat, g, B)
        out[a] = res
    return out


def team_layer(arms, B):
    T = arms["team"]
    act = T[PURE][["team", "game_id", "season", "pa", "ra"]]
    out = {}
    for layer in ("pa", "ra"):
        res = {}
        for a in (PURE, BASE, V4_NOAV, V4_MEF, V4_MKT):
            m = act.merge(T[a][["team", "game_id", f"vol_{layer}"]], on=["team", "game_id"], how="inner")
            res[a] = m
        k = res[PURE][["team", "game_id"]]
        for a in res:
            k = k.merge(res[a][["team", "game_id"]], on=["team", "game_id"])
        out[layer] = {}
        base = act.merge(k, on=["team", "game_id"])
        for a in res:
            base = base.merge(res[a][["team", "game_id", f"vol_{layer}"]].rename(columns={f"vol_{layer}": a}), on=["team", "game_id"])
        g = base["game_id"].to_numpy(); y = base[layer].to_numpy(float)
        out[layer]["n_team_games"] = int(len(base))
        out[layer]["mae"] = {a: r6(np.abs(base[a] - y).mean()) for a in res}
        out[layer]["bias"] = {a: r6((base[a] - y).mean()) for a in res}
        for pname, (a, b) in PAIRS.items():
            out[layer][pname] = G.summarize(np.abs(base[a] - y) - np.abs(base[b] - y), g, B)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", required=True)
    ap.add_argument("--data-root", required=True)
    ap.add_argument("--out", default=os.path.join(ROOT, "research", "pure_gap"))
    ap.add_argument("--bootstrap", type=int, default=1000)
    a = ap.parse_args()
    t0 = time.time()
    log = lambda *x: print(f"[{time.time() - t0:6.0f}s]", *x, flush=True)   # noqa: E731
    arms = pd.read_pickle(a.arms)
    B = a.bootstrap
    dg = F12.defence_by_group(arms["rows"], arms["teams"])
    orc = oracle_opponent(arms)
    res = {"protocol": {"population": "PURE_PLAYER_V1 held-out rows 2024+2025 matched across PURE, V4_MEF_NO_AVAIL, V4_MEF_AS_IS, V4_MARKET_CLOSE",
                        "metric": "MAE of the forecast mean, one row per player-game-statistic", "bootstrap": B, "cluster": "game_id",
                        "seed": 20261010, "pairs": {k: list(v) for k, v in PAIRS.items()},
                        "components": {s: G.components(s) for s in STATS},
                        "note": "availability strata and the opponent oracle use realised / hindsight information as DIAGNOSTIC labels only"},
           "team_layer": team_layer(arms, B), "player": {}}
    log("team layer")
    for stat in STATS:
        w = wide(arms, stat)
        r = {"n": int(len(w)), "n_games": int(w.game_id.nunique()), "by_season_n": w.groupby("season").size().to_dict(),
             "mae": {x: r6(np.abs(w[f"mean_{x}"] - w["y"]).mean()) for x in ARMS},
             "bias": {x: r6((w[f"mean_{x}"] - w["y"]).mean()) for x in ARMS}}
        r["shapley"] = {}
        for pname, (x, y) in PAIRS.items():
            r["shapley"][pname], _ = gap_shapley(w, stat, x, y, B)
        # by position group (PURE vs V4_MKT and PURE vs V4_MEF)
        r["shapley_by_group"] = {}
        for grp in ("QB", "RB", "WR", "TE"):
            sub = w[w.pgroup == grp].reset_index(drop=True)
            if len(sub) >= 100:
                r["shapley_by_group"][grp] = {p: gap_shapley(sub, stat, *PAIRS[p], B)[0] for p in ("PURE_minus_V4_MARKET_CLOSE", "PURE_minus_V4_MEF_AS_IS")}
        r["shapley_by_season"] = {int(s): {p: gap_shapley(w[w.season == s].reset_index(drop=True), stat, *PAIRS[p], B)[0]["gap"]
                                           for p in PAIRS} for s in sorted(w.season.unique())}
        r["oracle"] = {x: oracle_split(w, stat, x, B) for x in (PURE, V4_MKT, V4_MEF)}
        flags = availability_flags(arms, w, a.data_root)
        r["availability"] = strata(w, flags, stat, B)
        r["opponent_terciles"] = opponent_terciles(w, stat, B)
        if stat != "snap_share":
            lv = _grp(w, dg, "dg_"); oe = _grp(w, dg, "dgoe_"); orr = _grp(w, orc, "or_")
            pick = {"targets": ("tsh",), "receptions": ("tsh", "cr"), "receiving_yards": ("tsh", "cr", "ypt"), "carries": ("csh",),
                    "rushing_yards": ("csh", "ypc"), "passing_attempts": (), "completions": (), "passing_yards": ()}[stat]
            v1 = [w[c].to_numpy(float) for c in ("o_cmp_allowed", "o_ypt_allowed", "o_ypc_allowed", "o_ypa_allowed", "o_rate_allowed")]
            feats = {"pure_v1_opponent_features": v1}
            if pick and not (w.pgroup == "QB").all():
                feats["positional_prior_only"] = [lv[p] for p in pick]
                feats["positional_over_expected_prior_only"] = [oe[p] for p in pick]
                feats["ORACLE_positional_full_season_loo"] = [orr[p] for p in pick]
            r["opponent_residual_signal"] = residual_signal(w, stat, feats, B)
        res["player"][stat] = r
        log(stat, r["n"], r["mae"])
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "decomposition.json"), "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=True, default=str)
    log("wrote", os.path.join(a.out, "decomposition.json"))


if __name__ == "__main__":
    main()
