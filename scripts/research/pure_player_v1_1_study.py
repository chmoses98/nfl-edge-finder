#!/usr/bin/env python3
"""PURE_PLAYER_V1_1 vs PURE_PLAYER_V1 vs PURE_EWM_BASELINE (preregistration: docs/research/PURE_PLAYER_V1_1_PREREGISTRATION.md,
commit 4441249). Writes research/pure_player_v1_1/<label>.json.

    python3 scripts/research/pure_player_v1_1_study.py --seasons 2022 --label dev_2022            # bugs only
    python3 scripts/research/pure_player_v1_1_study.py --seasons 2023,2024 --label holdout_2023_2024
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import timedelta

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.availability_pit.loaders import injuries_certified  # noqa: E402
from nfl_edge.engines.player.pure_v1 import BASELINE_NAME, MODEL_NAME  # noqa: E402
from nfl_edge.engines.player.pure_v1 import data as D  # noqa: E402
from nfl_edge.engines.player.pure_v1 import features as F  # noqa: E402
from nfl_edge.engines.player.pure_v1 import model as M  # noqa: E402
from nfl_edge.engines.player.pure_v1 import pipeline as PP  # noqa: E402
from nfl_edge.engines.player.pure_v1_1 import MODEL_NAME as V11  # noqa: E402
from nfl_edge.engines.player.pure_v1_1 import features as F11  # noqa: E402
from nfl_edge.engines.player.pure_v1_1 import model as M11  # noqa: E402

KEY = ["game_id", "player_id", "statistic"]
B, SEED = 1000, 20261011
QS = (0.1, 0.5, 0.9)


def crps3(df, y):
    q = {0.1: df["p10"].to_numpy(float), 0.5: df["median"].to_numpy(float), 0.9: df["p90"].to_numpy(float)}
    tot = 0.0
    for a, v in q.items():
        tot = tot + np.where(y >= v, a * (y - v), (1 - a) * (v - y))
    return 2.0 * tot / 3.0


def rung(row_thr, k):
    for a, p in row_thr:
        if a == k:
            return p
    return np.nan


def per_row_metrics(df: pd.DataFrame, ref_thr: pd.Series) -> pd.DataFrame:
    """Row-level losses for one arm; the representative rung is V1's rung closest to 0.5 (outcome-blind)."""
    y = df["actual"].to_numpy(float)
    mu = df["mean"].to_numpy(float)
    out = pd.DataFrame({"abs": np.abs(mu - y), "sq": (mu - y) ** 2, "err": mu - y,
                        "cov": ((df["p10"].to_numpy(float) <= y) & (y <= df["p90"].to_numpy(float))).astype(float),
                        "crps": crps3(df, y)}, index=df.index)
    k = ref_thr.to_numpy()
    p = np.array([rung(t, kk) for t, kk in zip(df["thresholds"], k)], float)
    hit = (y >= k).astype(float)
    pc = np.clip(p, 1e-6, 1 - 1e-6)
    out["brier"] = (p - hit) ** 2
    out["logloss"] = -(hit * np.log(pc) + (1 - hit) * np.log(1 - pc))
    return out


def boot(delta: np.ndarray, games: np.ndarray, *, stat="mean") -> list:
    """Paired, game-clustered percentile bootstrap of mean(delta)."""
    gi, gid = np.unique(games, return_inverse=True)
    sums = np.bincount(gid, weights=delta, minlength=len(gi)); cnt = np.bincount(gid, minlength=len(gi)).astype(float)
    rng = np.random.default_rng(SEED)
    w = rng.multinomial(len(gi), np.full(len(gi), 1.0 / len(gi)), size=B).astype(float)
    est = (w @ sums) / (w @ cnt)
    return [round(float(np.percentile(est, 2.5)), 6), round(float(np.percentile(est, 97.5)), 6)]


def boot_cov(c_a, c_b, games):
    """Δ|coverage - 0.8| (b - a), game-clustered."""
    gi, gid = np.unique(games, return_inverse=True)
    sa = np.bincount(gid, weights=c_a, minlength=len(gi)); sb = np.bincount(gid, weights=c_b, minlength=len(gi))
    n = np.bincount(gid, minlength=len(gi)).astype(float)
    rng = np.random.default_rng(SEED)
    w = rng.multinomial(len(gi), np.full(len(gi), 1.0 / len(gi)), size=B).astype(float)
    est = np.abs((w @ sb) / (w @ n) - 0.8) - np.abs((w @ sa) / (w @ n) - 0.8)
    return [round(float(np.percentile(est, 2.5)), 6), round(float(np.percentile(est, 97.5)), 6)]


METRICS = ("abs", "sq", "crps", "brier", "logloss")


def compare(m: pd.DataFrame, a: str, b: str) -> dict:
    """b - a, per statistic."""
    res = {}
    for st, s in m.groupby("statistic"):
        g = s["game_id"].to_numpy()
        r = {"n": int(len(s)), "games": int(len(set(g)))}
        for met in METRICS:
            x, z = s[f"{met}_{a}"].to_numpy(float), s[f"{met}_{b}"].to_numpy(float)
            ok = np.isfinite(x) & np.isfinite(z)
            r[f"{met}_{a}"] = round(float(x[ok].mean()), 6); r[f"{met}_{b}"] = round(float(z[ok].mean()), 6)
            r[f"d_{met}"] = round(float((z[ok] - x[ok]).mean()), 6)
            r[f"d_{met}_ci95"] = boot(z[ok] - x[ok], g[ok])
        r[f"bias_{a}"] = round(float(s[f"err_{a}"].mean()), 4); r[f"bias_{b}"] = round(float(s[f"err_{b}"].mean()), 4)
        r[f"cov80_{a}"] = round(float(s[f"cov_{a}"].mean()), 4); r[f"cov80_{b}"] = round(float(s[f"cov_{b}"].mean()), 4)
        r["d_abs_cov_minus_0.8"] = round(abs(r[f"cov80_{b}"] - 0.8) - abs(r[f"cov80_{a}"] - 0.8), 6)
        r["d_abs_cov_minus_0.8_ci95"] = boot_cov(s[f"cov_{a}"].to_numpy(float), s[f"cov_{b}"].to_numpy(float), g)
        res[st] = r
    return res


def verdict(cmp: dict, coverage_ok: bool) -> dict:
    if not coverage_ok:
        return {"verdict": "BLOCKED_DATA"}
    worse = [(st, met) for st, r in cmp.items() for met in ("abs", "sq", "crps", "brier", "logloss", "abs_cov_minus_0.8")
             if r[f"d_{met}_ci95"][0] > 0]
    better = [st for st, r in cmp.items() if r["d_abs_ci95"][1] < 0]
    if worse:
        v = "REJECTED"
    elif len(better) >= 4:
        v = "ACCEPTED_CHALLENGER"
    else:
        v = "INCONCLUSIVE"
    return {"verdict": v, "significantly_worse": worse, "mae_ci_below_zero": better,
            "rule": "REJECTED if any preregistered metric worse with CI > 0; ACCEPTED if none worse and dMAE CI < 0 on >= 4 of 9"}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--seasons", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--out-dir", default=os.path.join(ROOT, "research", "pure_player_v1_1"))
    a = ap.parse_args(argv)
    seasons = [int(s) for s in a.seasons.split(",")]
    last = max(seasons)
    pg = D.load_player_games(a.root, range(2013, last + 1))
    rows, t = F.build(pg)
    inj, inj_rep = injuries_certified(a.root, range(2013, last + 1), lead=timedelta(minutes=90))
    rows11 = F11.add(rows, t, inj)
    # BLOCKED_DATA criterion: share of holdout REG team-weeks with >= 1 certified injury row
    tw = rows[rows.season.isin(seasons)][["season", "week", "team"]].drop_duplicates()
    have = set(zip(inj.season, inj.week, inj.team))
    tw_cov = float(np.mean([(s, w, tm) in have for s, w, tm in tw.itertuples(index=False)]))
    long, info = [], {"seasons": {}}
    for S in seasons:
        out = PP.run(rows, t, S)
        m11 = M11.fit(rows11, t, S)
        te = rows11[(rows11.season == S) & rows11.played].reset_index(drop=True)
        PP.check_point_in_time(te)
        d = m11.intermediates(te, t)
        l11 = PP._long(d, m11.dist, m11.means(d), M.LINEAGE)
        aff = d.assign(affected=(d["vac_t"] + d["vac_c"] > 0) | (d["qb1_out"] > 0))[["game_id", "player_id", "affected", "own_q", "own_d", "own_lim", "own_dnp", "vac_t", "vac_c", "qb1_out"]]
        arms = {"v1": out["player"][MODEL_NAME], "base": out["player"][BASELINE_NAME], "v11": l11}
        j = None
        for name, L in arms.items():
            L = L.reset_index(drop=True)
            keep = L[KEY + ["season", "pgroup", "actual", "mean", "median", "p10", "p90", "thresholds"]]
            j = keep.rename(columns={c: f"{c}_{name}" for c in ("mean", "median", "p10", "p90", "thresholds", "actual")}) if j is None else \
                j.merge(keep[KEY + ["mean", "median", "p10", "p90", "thresholds", "actual"]].rename(columns={c: f"{c}_{name}" for c in ("mean", "median", "p10", "p90", "thresholds", "actual")}), on=KEY, how="inner")
        assert np.allclose(j["actual_v1"], j["actual_v11"]) and np.allclose(j["actual_v1"], j["actual_base"])
        j = j.merge(aff.drop_duplicates(["game_id", "player_id"]), on=["game_id", "player_id"], how="left")
        info["seasons"][S] = {"rows_v1": int(len(arms["v1"])), "rows_v11": int(len(l11)), "rows_matched": int(len(j)), "v11_model_info": m11.info}
        long.append(j)
    j = pd.concat(long, ignore_index=True)
    # V1's representative rung: closest to 0.5 (outcome-blind)
    ref = [min(t, key=lambda ap_: (abs(ap_[1] - 0.5), ap_[0]))[0] if len(t) else np.nan for t in j["thresholds_v1"]]
    ref = pd.Series(ref, index=j.index)
    for name in ("v1", "base", "v11"):
        sub = pd.DataFrame({"mean": j[f"mean_{name}"], "median": j[f"median_{name}"], "p10": j[f"p10_{name}"], "p90": j[f"p90_{name}"],
                            "thresholds": j[f"thresholds_{name}"], "actual": j["actual_v1"]})
        pm = per_row_metrics(sub, ref)
        for c in pm.columns:
            j[f"{c}_{name}"] = pm[c].to_numpy()
    res = {"preregistration": "docs/research/PURE_PLAYER_V1_1_PREREGISTRATION.md @ 4441249", "label": a.label, "seasons": seasons,
           "bootstrap": {"B": B, "seed": SEED, "cluster": "game_id"}, "injury_loader_report": inj_rep,
           "holdout_team_week_injury_coverage": round(tw_cov, 4), "info": info,
           "rows_affected_share": round(float(j["affected"].mean()), 4),
           "feature_nonzero_share": {c: round(float((j[c] > 0).mean()), 4) for c in ("own_q", "own_d", "own_lim", "own_dnp", "vac_t", "vac_c", "qb1_out")},
           "v11_vs_v1": compare(j, "v1", "v11"), "v11_vs_baseline": compare(j, "base", "v11"), "v1_vs_baseline": compare(j, "base", "v1")}
    res["decision"] = verdict(res["v11_vs_v1"], tw_cov >= 0.9)
    res["subgroups_v11_vs_v1_dMAE"] = {}
    for lab, mask in (("affected", j["affected"].fillna(False).astype(bool)), ("unaffected", ~j["affected"].fillna(False).astype(bool))):
        res["subgroups_v11_vs_v1_dMAE"][lab] = {st: {"n": int(len(s)), "d_mae": round(float((s.abs_v11 - s.abs_v1).mean()), 5),
                                                      "ci95": boot((s.abs_v11 - s.abs_v1).to_numpy(float), s.game_id.to_numpy())}
                                                 for st, s in j[mask].groupby("statistic")}
    for key, col in (("by_season", "season"), ("by_position_group", "pgroup")):
        res[f"{key}_v11_vs_v1_dMAE"] = {f"{k[0]}|{k[1]}": {"n": int(len(s)), "d_mae": round(float((s.abs_v11 - s.abs_v1).mean()), 5),
                                                          "ci95": boot((s.abs_v11 - s.abs_v1).to_numpy(float), s.game_id.to_numpy())}
                                        for k, s in j.groupby([col, "statistic"])}
    os.makedirs(a.out_dir, exist_ok=True)
    p = os.path.join(a.out_dir, f"{a.label}.json")
    with open(p, "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=True, default=str)
    print(json.dumps({"decision": res["decision"], "coverage": tw_cov, "affected": res["rows_affected_share"],
                      "v11_vs_v1": {st: (r["n"], r["d_abs"], r["d_abs_ci95"]) for st, r in res["v11_vs_v1"].items()}}, indent=1, default=str))


if __name__ == "__main__":
    main()
