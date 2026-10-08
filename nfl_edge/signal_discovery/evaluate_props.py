"""Locked evaluation of the pre-registered NFL player-prop hypotheses. RESEARCH ONLY.

For every prop family (position x stat) it answers, out of sample (walk-forward by season: train on
2016..Y-1, test Y):

  A. which pregame football variables predict the stat    -> feature-GROUP ablation (MAE without the group
                                                              minus MAE with it; game-clustered bootstrap CI)
  B. which interactions add information                    -> the same ablation for pre-registered products
  C. does the opportunity model beat simple baselines      -> MAE vs season average, EWMA, usage-only
  D. does it explain the residual vs the offered line      -> Kalshi ladders: slope of (actual - market median)
                                                              on (model median - market median) and on each
                                                              signal feature; who is closer
  E. economic underpricing after price and fee             -> pre-registered natural-rung rule at the
                                                              captured executable ask, fee-adjusted ROI
  F. stability across seasons                               -> per-fold signs / deltas
  G. concentration                                          -> top-player / top-team shares, leave-top-out

All rows are CONDITIONAL ON THE PLAYER APPEARING (see player_features).
"""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

import numpy as np
import pandas as pd

from nfl_edge.signal_discovery import stats
from nfl_edge.signal_discovery.markets import kalshi_fee

TEST_SEASONS = tuple(range(2018, 2027))
TRAIN_FIRST = 2016


def _num(df: pd.DataFrame, col: str) -> np.ndarray:
    return pd.to_numeric(df[col], errors="coerce").to_numpy(float) if col in df.columns else np.full(len(df), np.nan)


def add_baselines(pf: pd.DataFrame, families: list[dict]) -> pd.DataFrame:
    """Point-in-time baselines: same-season prior average, decayed EWMA, usage-only projection."""
    from nfl_edge.sim.features import decayed_prior_sums

    pf = pf.sort_values(["player_id", "season", "week", "game_id"]).reset_index(drop=True)
    stats_cols = sorted({f["stat"] for f in families})
    X = pf[stats_cols].to_numpy(float)
    S, N, _ = decayed_prior_sums(pf["player_id"].to_numpy(), None, pf["season"].to_numpy(), X, 10.0, 0.5)
    for j, c in enumerate(stats_cols):
        pf[f"b_ewma.{c}"] = np.where(N[:, j] > 0, S[:, j] / np.maximum(N[:, j], 1e-9), np.nan)
    # same-season prior average (strictly earlier games of this season)
    g = pf.groupby(["player_id", "season"])
    for c in stats_cols:
        cs = g[c].cumsum() - pf[c]
        cn = g.cumcount()
        pf[f"b_season.{c}"] = np.where(cn > 0, cs / cn.clip(lower=1), np.nan)
    # usage-only: share x team volume EWMA x per-touch rate (all PIT)
    pa = _num(pf, "off_pass_att")
    ra = _num(pf, "off_rush_att")
    tr = _num(pf, "off_target_rate")
    usage = {
        "attempts": _num(pf, "sh_attempt_l") * pa,
        "carries": _num(pf, "sh_carry_l") * ra,
        "targets": _num(pf, "sh_target_l") * pa * tr,
    }
    usage["completions"] = usage["attempts"] * _num(pf, "rt_comp_rate")
    usage["pass_yards"] = usage["attempts"] * _num(pf, "rt_ypa")
    usage["pass_td"] = usage["attempts"] * _num(pf, "rt_pass_td_rate")
    usage["ints"] = usage["attempts"] * _num(pf, "rt_int_rate")
    usage["rush_yards"] = usage["carries"] * _num(pf, "rt_ypc")
    usage["receptions"] = usage["targets"] * _num(pf, "rt_catch_rate")
    usage["rec_yards"] = usage["targets"] * _num(pf, "rt_ypt")
    for c in stats_cols:
        pf[f"b_usage.{c}"] = usage.get(c, np.full(len(pf), np.nan))
    return pf


def family_rows(pf: pd.DataFrame, fam: dict) -> pd.DataFrame:
    d = pf[pf["position"].isin(fam["positions"])].copy()
    share = _num(d, fam["share_col"])
    d = d[(share >= fam["min_share"]) & (d["n_prior"] >= 3) & d[f"b_season.{fam['stat']}"].notna()]
    return d


def _design(d: pd.DataFrame, fam: dict, features: list[str], interactions: list[tuple[str, str]]) -> np.ndarray:
    cols = [np.ones(len(d))]
    for f in features:
        cols.append(_num(d, f))
    for a, b in interactions:
        cols.append(_num(d, a) * _num(d, b))
    return np.column_stack(cols)


def _fit_predict(tr: pd.DataFrame, te: pd.DataFrame, fam: dict, features: list[str], inter: list[tuple[str, str]]):
    y = _num(tr, fam["stat"])
    Xtr = _design(tr, fam, features, inter)
    Xte = _design(te, fam, features, inter)
    # impute missing features with the TRAINING mean (no test information), then standardise on training
    mu = np.nanmean(Xtr, axis=0)
    mu = np.where(np.isfinite(mu), mu, 0.0)
    Xtr = np.where(np.isfinite(Xtr), Xtr, mu)
    Xte = np.where(np.isfinite(Xte), Xte, mu)
    sd = Xtr.std(axis=0)
    sd[0] = 1.0
    sd = np.where(sd > 0, sd, 1.0)
    Ztr, Zte = (Xtr - mu * (np.arange(len(mu)) > 0)) / sd, (Xte - mu * (np.arange(len(mu)) > 0)) / sd
    lam = 1.0
    pen = np.eye(Ztr.shape[1]) * lam
    pen[0, 0] = 0.0
    beta = np.linalg.solve(Ztr.T @ Ztr + pen, Ztr.T @ y)
    resid = y - Ztr @ beta
    return Zte @ beta, beta, resid


def walk_forward_family(pf: pd.DataFrame, fam: dict, spec: dict) -> dict[str, Any]:
    d = family_rows(pf, fam)
    stat = fam["stat"]
    base_feats = spec["model_features"]
    groups = spec["groups"]
    inters = spec["interactions"].get(fam["id"], [])
    out_rows = []
    coefs = defaultdict(list)
    for test in TEST_SEASONS:
        tr = d[(d["season"] >= TRAIN_FIRST) & (d["season"] < test)]
        te = d[d["season"] == test]
        if len(tr) < 300 or len(te) == 0:
            continue
        full, beta, resid = _fit_predict(tr, te, fam, base_feats, [(a, b) for a, b, _ in inters])
        rec = te[["game_id", "season", "week", "player_id", "team", "position", "role_stability", stat,
                  f"b_season.{stat}", f"b_ewma.{stat}", f"b_usage.{stat}"]].copy()
        rec["pred"] = full
        rec["median_offset"] = float(np.median(resid))
        q = np.quantile(resid, [0.1, 0.25, 0.75, 0.9])
        rec["pi50_lo"], rec["pi50_hi"] = full + q[1], full + q[2]
        rec["pi80_lo"], rec["pi80_hi"] = full + q[0], full + q[3]
        for gname, gfeats in groups.items():
            keep = [f for f in base_feats if f not in gfeats]
            p, _, _ = _fit_predict(tr, te, fam, keep, [(a, b) for a, b, _ in inters if a not in gfeats and b not in gfeats])
            rec[f"pred_wo.{gname}"] = p
        for a, b, name in inters:
            p, _, _ = _fit_predict(tr, te, fam, base_feats, [(x, y) for x, y, n in inters if n != name])
            rec[f"pred_wo.{name}"] = p
        for i, f in enumerate(base_feats):
            coefs[f].append((test, float(beta[i + 1])))
        out_rows.append(rec)
    if not out_rows:
        return {"n": 0}
    R = pd.concat(out_rows, ignore_index=True)
    y = R[stat].to_numpy(float)
    res: dict[str, Any] = {"n": len(R), "players": int(R["player_id"].nunique()), "test_seasons": sorted(R["season"].unique().tolist())}
    maes = {}
    for name, col in (("SEASON_AVG", f"b_season.{stat}"), ("EWMA", f"b_ewma.{stat}"), ("USAGE", f"b_usage.{stat}"), ("MODEL", "pred")):
        p = R[col].to_numpy(float)
        ok = np.isfinite(p)
        maes[name] = float(np.mean(np.abs(y[ok] - p[ok]))) if ok.any() else None
        res[f"mae.{name}"] = maes[name]
        res[f"n_ok.{name}"] = int(ok.sum())
    best_base = min((k for k in ("SEASON_AVG", "EWMA", "USAGE") if maes[k] is not None), key=lambda k: maes[k])
    res["best_baseline"] = best_base
    res["mae_gain_vs_best_baseline"] = _gain(R, y, {"SEASON_AVG": f"b_season.{stat}", "EWMA": f"b_ewma.{stat}", "USAGE": f"b_usage.{stat}"}[best_base], "pred")
    res["by_season_gain_vs_best"] = {str(s): _mean_abs_diff(g, stat, {"SEASON_AVG": f"b_season.{stat}", "EWMA": f"b_ewma.{stat}", "USAGE": f"b_usage.{stat}"}[best_base], "pred")
                                     for s, g in R.groupby("season")}
    res["groups"] = {}
    for gname in list(groups) + [n for _, _, n in inters]:
        gain = _gain(R, y, f"pred_wo.{gname}", "pred")
        by_season = {str(s): _mean_abs_diff(g, stat, f"pred_wo.{gname}", "pred") for s, g in R.groupby("season")}
        gain["seasons_positive"] = sum(1 for v in by_season.values() if v is not None and v > 0)
        gain["seasons"] = len(by_season)
        gain["by_season"] = by_season
        res["groups"][gname] = gain
    res["coef_by_season"] = {f: v for f, v in coefs.items()}
    res["coef_sign_share"] = {f: (sum(1 for _, b in v if b > 0) / len(v)) for f, v in coefs.items()}
    # interval coverage
    res["pi50_coverage"] = float(np.mean((y >= R["pi50_lo"]) & (y <= R["pi50_hi"])))
    res["pi80_coverage"] = float(np.mean((y >= R["pi80_lo"]) & (y <= R["pi80_hi"])))
    # distribution of the stat and of model residuals
    res["stat_distribution"] = {"mean": float(np.mean(y)), "sd": float(np.std(y)), **stats.quantiles(y.tolist())}
    res["resid_distribution"] = stats.quantiles((y - R["pred"].to_numpy(float)).tolist())
    # role stability slices
    res["by_role"] = {k: {"n": len(g), "mae_model": float(np.mean(np.abs(g[stat] - g["pred"]))),
                          "mae_best_base": float(np.nanmean(np.abs(g[stat] - g[{"SEASON_AVG": f"b_season.{stat}", "EWMA": f"b_ewma.{stat}", "USAGE": f"b_usage.{stat}"}[best_base]])))}
                      for k, g in R.groupby("role_stability")}
    # concentration: gain without the 10 players with the largest contribution
    contrib = (np.abs(R[{"SEASON_AVG": f"b_season.{stat}", "EWMA": f"b_ewma.{stat}", "USAGE": f"b_usage.{stat}"}[best_base]] - R[stat]) - np.abs(R["pred"] - R[stat])).groupby(R["player_id"]).sum()
    top = set(contrib.sort_values(ascending=False).index[:10])
    rest = R[~R["player_id"].isin(top)]
    res["gain_without_top10_players"] = _mean_abs_diff(rest, stat, {"SEASON_AVG": f"b_season.{stat}", "EWMA": f"b_ewma.{stat}", "USAGE": f"b_usage.{stat}"}[best_base], "pred")
    return {"summary": res, "rows": R}


def _mean_abs_diff(g: pd.DataFrame, stat: str, a: str, b: str) -> float | None:
    pa, pb, y = g[a].to_numpy(float), g[b].to_numpy(float), g[stat].to_numpy(float)
    ok = np.isfinite(pa) & np.isfinite(pb)
    if not ok.any():
        return None
    return float(np.mean(np.abs(y[ok] - pa[ok]) - np.abs(y[ok] - pb[ok])))


def _gain(R: pd.DataFrame, y: np.ndarray, base_col: str, model_col: str) -> dict[str, Any]:
    pa, pb = R[base_col].to_numpy(float), R[model_col].to_numpy(float)
    ok = np.isfinite(pa) & np.isfinite(pb)
    diff = np.abs(y[ok] - pa[ok]) - np.abs(y[ok] - pb[ok])  # > 0: the model (with the group) is closer
    lo, hi = stats.cluster_bootstrap_mean_ci(diff.tolist(), R.loc[ok, "game_id"].tolist())
    mt = stats.mean_test(diff.tolist())
    mae_b = float(np.mean(np.abs(y[ok] - pa[ok])))
    return {"n": int(ok.sum()), "mae_delta": float(diff.mean()), "ci_game_cluster": [lo, hi], "p": mt["p"],
            "rel_gain_pct": 100.0 * float(diff.mean()) / mae_b if mae_b else None}


# ---------------------------------------------------------------------------------------- market tests
def market_tests(R: pd.DataFrame, fam: dict, ladders: pd.DataFrame, pf: pd.DataFrame, spec: dict) -> dict[str, Any]:
    """Join OOS model rows to Kalshi ladders for the family's Kalshi stat; residual, information and economics."""
    kstat = fam.get("kalshi_stat")
    if not kstat:
        return {"status": "NO_KALSHI_MARKET_FOR_FAMILY"}
    lad = ladders[(ladders["stat"] == kstat)].copy()
    stat = fam["stat"]
    m = R.merge(lad, left_on=["game_id", "player_id"], right_on=["game_id", "gsis_id"], how="inner", suffixes=("", "_m"))
    if "minutes_to_kickoff" in m.columns:
        pass
    m = m[m["market_median"].notna()].copy()
    out: dict[str, Any] = {"ladders_matched": int(len(m)), "by_season": m["season"].value_counts().sort_index().to_dict()}
    if len(m) < 30:
        out["status"] = "INSUFFICIENT_MARKET_ROWS"
        return out
    y = m[stat].to_numpy(float)
    med = m["market_median"].to_numpy(float)
    model_med = m["pred"].to_numpy(float) + m["median_offset"].to_numpy(float)
    resid = y - med
    out["market_residual"] = {"mean": float(resid.mean()), "median": float(np.median(resid)), **stats.quantiles(resid.tolist()),
                              "share_over_market_median": float(np.mean(y > med)),
                              "ci_game_cluster": list(stats.cluster_bootstrap_mean_ci(resid.tolist(), m["game_id"].tolist()))}
    out["mae_market_median"] = float(np.mean(np.abs(y - med)))
    out["mae_model_median"] = float(np.mean(np.abs(y - model_med)))
    gap = model_med - med
    X = np.column_stack([np.ones(len(m)), gap])
    o = stats.ols(resid, X, clusters=m["game_id"].tolist())
    out["residual_on_model_gap"] = {"beta": o["beta"][1], "se": o["se"][1], "p": o["p"][1], "n": o["n"],
                                    "interpretation": "beta>0: the football model carries information the line lacks"}
    sig = {}
    for gname, feats in spec["groups"].items():
        for f in feats[:1]:
            x = pd.to_numeric(m[f], errors="coerce").to_numpy(float) if f in m.columns else None
            if x is None:
                continue
            ok = np.isfinite(x)
            if ok.sum() < 30 or x[ok].std() == 0:
                continue
            z = (x[ok] - x[ok].mean()) / x[ok].std()
            oo = stats.ols(resid[ok], np.column_stack([np.ones(ok.sum()), z]), clusters=m.loc[ok, "game_id"].tolist())
            sig[gname] = {"feature": f, "beta_per_sd": oo["beta"][1], "se": oo["se"][1], "p": oo["p"][1], "n": int(ok.sum())}
    out["signal_feature_vs_residual"] = sig
    # economics: natural rung, pre-registered rule
    delta = spec["economic_rule"]["relative_margin"]
    bets = []
    for row, mm in zip(m.itertuples(index=False), model_med, strict=False):
        nat = row.natural
        if not isinstance(nat, dict) or nat.get("threshold") is None:
            continue
        t = float(nat["threshold"])
        side = None
        if mm >= t * (1 + delta) + 1e-9:
            side, price = "YES", nat.get("yes_ask")
        elif mm <= t * (1 - delta) - 1e-9:
            side, price = "NO", nat.get("no_ask")
        if side is None or price is None or not (0 < price < 1):
            continue
        actual = getattr(row, stat)
        win = (actual >= t) if side == "YES" else (actual < t)
        fee = kalshi_fee(float(price))
        bets.append({"game_id": row.game_id, "player_id": row.player_id, "team": row.team, "season": row.season, "side": side,
                     "price": float(price), "fee": fee, "win": bool(win), "pl": (1.0 if win else 0.0) - float(price) - fee,
                     "outlay": float(price) + fee})
    if bets:
        B = pd.DataFrame(bets)
        lo, hi = stats.bootstrap_ratio_ci(B["pl"].tolist(), B["outlay"].tolist())
        out["economics"] = {"rule": f"natural rung; YES if model median >= t*(1+{delta}), NO if <= t*(1-{delta}); executable ask; taker fee",
                            "n": len(B), "yes": int((B["side"] == "YES").sum()), "no": int((B["side"] == "NO").sum()),
                            "win_rate": float(B["win"].mean()), "mean_price": float(B["price"].mean()), "fees": float(B["fee"].sum()),
                            "pl": float(B["pl"].sum()), "roi": float(B["pl"].sum() / B["outlay"].sum()), "roi_ci_boot": [lo, hi],
                            "break_even": float(B["outlay"].mean()),
                            "by_season": {str(s): {"n": len(g), "roi": float(g["pl"].sum() / g["outlay"].sum())} for s, g in B.groupby("season")},
                            "top5_player_share": float(B["player_id"].value_counts().head(5).sum() / len(B)),
                            "top_team_share": float(B["team"].value_counts().iloc[0] / len(B))}
    else:
        out["economics"] = {"n": 0}
    out["status"] = "EVALUATED"
    out["contamination"] = "2025 rungs: archive already mined by prior studies (efficiency_map, model_vs_market); 2026 wks 1-3 used for board discovery"
    return out


def game_script_effects(pf: pd.DataFrame, tg: pd.DataFrame) -> dict[str, Any]:
    """Section 18: how the REALISED game environment moves player volume (descriptive, post-hoc), next to how the
    PREGAME expected script does (predictive). Both on the same player-game rows."""
    t = tg[["game_id", "team", "frac_lead8", "frac_trail8", "plays"]].rename(columns={"plays": "realised_team_plays"})
    d = pf.merge(t, on=["game_id", "team"], how="left")
    out = {}
    pairs = [("QB", "attempts", "sh_attempt_l", 0.5), ("QB", "completions", "sh_attempt_l", 0.5), ("QB", "pass_yards", "sh_attempt_l", 0.5),
             ("RB", "carries", "sh_carry_l", 0.3), ("RB", "receptions", "sh_target_l", 0.05),
             ("WR", "receptions", "sh_target_l", 0.12), ("WR", "rec_yards", "sh_target_l", 0.12),
             ("TE", "receptions", "sh_target_l", 0.10)]
    for pos, stat, share, mn in pairs:
        g = d[(d["position"] == pos) & (pd.to_numeric(d[share], errors="coerce") >= mn)].copy()
        g["realised_script"] = g["frac_lead8"] - g["frac_trail8"]
        y = g[stat].to_numpy(float)
        res = {}
        for name, col in (("realised_lead_minus_trail_share", "realised_script"), ("realised_team_plays", "realised_team_plays"),
                          ("pregame_expected_script", "ctx.expected_script"), ("pregame_expected_plays", "ctx.team_plays")):
            x = pd.to_numeric(g[col], errors="coerce").to_numpy(float)
            ok = np.isfinite(x) & np.isfinite(y)
            if ok.sum() < 100:
                continue
            z = (x[ok] - x[ok].mean()) / x[ok].std()
            X = np.column_stack([np.ones(ok.sum()), z, pd.to_numeric(g.loc[ok, f"b_ewma.{stat}"], errors="coerce").fillna(np.nanmean(y)).to_numpy(float)])
            o = stats.ols(y[ok], X, clusters=g.loc[ok, "game_id"].tolist())
            res[name] = {"beta_per_sd": o["beta"][1], "se": o["se"][1], "p": o["p"][1], "n": int(ok.sum()),
                         "pct_of_mean": 100 * o["beta"][1] / float(np.mean(y[ok])) if np.mean(y[ok]) else None}
        out[f"{pos}.{stat}"] = res
    return out


def correlations(R_by_family: dict[str, pd.DataFrame]) -> dict[str, Any]:
    """Section 47: correlation of OOS model residuals between prop families in the same team-game."""
    def team_resid(fid: str, agg: str = "sum"):
        R = R_by_family.get(fid)
        if R is None or not len(R):
            return None
        stat = [c for c in R.columns if c in ("attempts", "completions", "pass_yards", "carries", "rush_yards", "receptions", "rec_yards")][0]
        R = R.assign(resid=R[stat] - R["pred"])
        return R.groupby(["game_id", "team"])["resid"].sum()
    out = {}
    for a, b in (("QB_attempts", "WR_receptions"), ("QB_pass_yards", "WR_rec_yards"), ("QB_attempts", "RB_carries"),
                 ("QB_pass_yards", "TE_rec_yards"), ("RB_carries", "RB_rush_yards"), ("QB_completions", "RB_receptions")):
        ra, rb = team_resid(a), team_resid(b)
        if ra is None or rb is None:
            continue
        j = pd.concat([ra.rename("a"), rb.rename("b")], axis=1).dropna()
        if len(j) > 50:
            out[f"{a}~{b}"] = {"n_team_games": len(j), "corr": float(np.corrcoef(j["a"], j["b"])[0, 1])}
    return out


def status_for(fam_res: dict, group: str, expected: int, q: float | None) -> str:
    g = fam_res["summary"]["groups"].get(group)
    if g is None:
        return "NOT_TESTED"
    if q is not None and q < 0.05 and g["mae_delta"] > 0 and g["seasons_positive"] >= math.ceil(0.6 * g["seasons"]):
        return "FOOTBALL_VALIDATED"
    if q is not None and q < 0.10 and g["mae_delta"] > 0:
        return "DISCOVERY_ONLY"
    return "REJECTED"
