#!/usr/bin/env python3
"""Wave 2B (NFL): RB receptions market-mechanism study -- analysis. RESEARCH ONLY. EXPLANATORY ONLY.

Reads only the committed build artifacts in research/rb_receptions_mechanism/ (deterministic; no network, no
market-data) and writes the versioned artifact `mechanism_report.json` (nfl_rb_receptions_mechanism/1.0.0) and
`TABLES.md`. Every analysis follows docs/research/RB_RECEPTIONS_MECHANISM_PROTOCOL.md (a5f18324); anything not
pre-registered is labelled POST_HOC. No rule, filter, stake or recommendation is produced.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402

from nfl_edge.signal_discovery import rb_mechanism as R  # noqa: E402
from nfl_edge.signal_discovery import wave2 as W  # noqa: E402

OUT = ROOT / "research" / "rb_receptions_mechanism"
REPS = ("A_yes_ask", "B_yes_mid", "C_norm_mid")


def read_gz(p: Path) -> list[dict]:
    with gzip.open(p, "rt") as fh:
        return [json.loads(line) for line in fh]


def _default(o):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return None if np.isnan(o) else float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return str(o)


def mean(v):
    v = [x for x in v if x is not None]
    return float(np.mean(v)) if v else None


# --------------------------------------------------------------------------- sections


def populations(r26, r25) -> dict[str, list[dict]]:
    pops = defaultdict(list)
    for r in r26:
        pops[r["pop"]].append(r)
    for r in r25:
        key = r["pop"] if r["checkpoint"] == "T-90m" else f"{r['pop']}@T-0"
        pops[key].append(r)
    return pops


def settlement_counts(rows) -> dict[str, Any]:
    return {"n": len(rows), "settle_source": dict(Counter(r.get("settle_source") for r in rows)),
            "binary": sum(1 for r in rows if r.get("y") is not None)}


def negative_controls(pops) -> dict[str, Any]:
    cells = defaultdict(list)
    for r in pops["P4"]:
        cells[f"{r['position']}|receptions"].append(r)
    for r in pops["P5"]:
        cells[f"{r['position']}|{r['stat']}"].append(r)
    out = {}
    for k, rows in sorted(cells.items()):
        out[k] = {"raw": R.calib_summary(rows), "matched": R.calib_summary([r for r in rows if matched(r)])}
    return out


def matched(r) -> bool:
    m = R.MATCH
    return (r.get("yes_ask") is not None and m["yes_ask_lo"] <= r["yes_ask"] <= m["yes_ask_hi"]
            and (r.get("yes_spread") or 1) <= m["max_spread"] + 1e-9 and (r.get("n_valid") or 0) >= m["min_valid_rungs"]
            and r.get("checkpoint_age_min") is not None and r["checkpoint_age_min"] <= m["max_checkpoint_age_min"])


def diff_test(a_rows, b_rows, field="r_B") -> dict[str, Any]:
    """Mean(field | A) - mean(field | B), game-clustered bootstrap over the union of games."""
    rows = [{**r, "_grp": "A"} for r in a_rows if r.get(field) is not None] + [{**r, "_grp": "B"} for r in b_rows if r.get(field) is not None]

    def stat(rs):
        a = [r[field] for r in rs if r["_grp"] == "A"]
        b = [r[field] for r in rs if r["_grp"] == "B"]
        return float(np.mean(a) - np.mean(b)) if a and b else None

    return {**R.boot_stat(rows, stat), "n_a": sum(1 for r in rows if r["_grp"] == "A"), "n_b": sum(1 for r in rows if r["_grp"] == "B")}


def calibration_tables(rows) -> dict[str, Any]:
    rows = [r for r in rows if r.get("y") is not None]
    out = {"yes_by_yes_ask": R.table_by(rows, lambda r: R.bucket_label(r.get("yes_ask"), R.YES_ASK_BUCKETS)),
           "no_by_no_ask": no_table(rows),
           "scores": {rep: R.scores(rows, rep) for rep in REPS},
           "no_scores": no_scores(rows)}
    return out


def no_table(rows) -> dict[str, Any]:
    out = {}
    groups = defaultdict(list)
    for r in rows:
        b = R.bucket_label(r.get("no_ask"), R.NO_ASK_BUCKETS)
        if b:
            groups[b].append(r)
    for b, rs in sorted(groups.items()):
        n = len(rs)
        wins = sum(1 - r["y"] for r in rs)
        no_mid = [r["no_mid"] for r in rs if r.get("no_mid") is not None]
        out[b] = {**R.compact(rs), "no_rate": wins / n, "mean_no_ask": mean([r["no_ask"] for r in rs]),
                  "mean_no_mid": mean(no_mid), "no_resid_vs_ask": wins / n - mean([r["no_ask"] for r in rs]),
                  "no_resid_vs_mid": (wins / n - mean(no_mid)) if no_mid else None}
    return out


def no_scores(rows) -> dict[str, Any]:
    """NO-side calibration: realized NO vs NO ask, NO mid (2026) and 1 - YES mid."""
    out = {}
    for name, f in (("no_ask", lambda r: r.get("no_ask")), ("no_mid", lambda r: r.get("no_mid")),
                    ("one_minus_yes_mid", lambda r: None if r.get("B_yes_mid") is None else 1 - r["B_yes_mid"])):
        rs = [{**r, "_p": f(r), "_res": (1 - r["y"]) - f(r)} for r in rows if f(r) is not None]
        if rs:
            out[name] = {"n": len(rs), "mean_p": mean([r["_p"] for r in rs]), "no_rate": mean([1 - r["y"] for r in rs]),
                         "residual": R.boot_stat(rs, R.mean_of("_res"))}
    return out


def ladder_shape(ladders, label) -> dict[str, Any]:
    n_viol = Counter()
    spacing = Counter()
    nat_pos = Counter()
    for lad in ladders:
        rs = sorted(tuple(x) for x in lad["rungs"])
        v = R.monotone_violations(rs)
        n_viol["ladders_with_violation" if v else "monotone"] += 1
        n_viol["violations"] += v
        for (t1, _), (t2, _) in zip(rs, rs[1:], strict=False):
            spacing[str(t2 - t1)] += 1
        ts = [t for t, _ in rs]
        if lad["natural_t"] in ts:
            i = ts.index(lad["natural_t"])
            nat_pos[f"{i} of {len(ts)} (0 = lowest)"] += 1
    return {"population": label, "ladders": len(ladders), "monotonicity": dict(n_viol), "adjacent_spacing": dict(spacing),
            "natural_position": dict(nat_pos.most_common(12))}


def implied_vs_realized(ladders, rep_key="rungs") -> dict[str, Any]:
    """Market-implied mass around the natural threshold vs realized (protocol M-27), per ladder then aggregated."""
    units, skipped, neg = [], Counter(), 0
    pmf_full = []
    for lad in ladders:
        if lad.get("actual") is None or lad.get(rep_key) is None:
            skipped["NO_ACTUAL_OR_PRICES"] += 1
            continue
        pts = [tuple(x) for x in lad[rep_key] if x[1] is not None]
        S = R.survival_from_rungs(pts)
        t = int(round(lad["natural_t"]))
        ib = R.implied_bins(S, t)
        if ib is None:
            skipped["RUNGS_T-1..T+2_NOT_ALL_VALID"] += 1
            continue
        if any(v < -1e-9 for v in ib.values()):
            neg += 1
        rb = R.realized_bins(lad["actual"], t)
        units.append({"game_id": lad["game_id"], "player_id": lad["player_id"], "t": t, "actual": lad["actual"],
                      **{f"imp_{k}": v for k, v in ib.items()}, **{f"real_{k}": v for k, v in rb.items()},
                      **{f"d_{k}": ib[k] - rb[k] for k in R.PMF_BINS}, "S_t": S.get(t, 1.0 if t <= 0 else None),
                      "y_t": 1.0 if lad["actual"] >= t else 0.0})
        full = R.implied_pmf(S)
        if full.get("covered"):
            pmf_full.append({**full, "actual": lad["actual"]})
    agg = {}
    for k in R.PMF_BINS:
        agg[k] = {"implied": mean([u[f"imp_{k}"] for u in units]), "realized": mean([u[f"real_{k}"] for u in units]),
                  "implied_minus_realized": R.boot_stat(units, R.mean_of(f"d_{k}"))}
    # P(X=0) where the ladder starts at 1
    zero = [(f["pmf"].get("<1"), 1.0 if f["actual"] == 0 else 0.0) for f in pmf_full if f.get("lo") == 1]
    means = [(f["implied_mean_lb"], f["actual"]) for f in pmf_full if f.get("implied_mean_lb") is not None]
    return {"ladders_used": len(units), "skipped": dict(skipped), "ladders_with_negative_bin_mass": neg, "bins": agg,
            "S_t_mean": mean([u["S_t"] for u in units]), "realized_P_ge_t": mean([u["y_t"] for u in units]),
            "zero_mass_ladders_from_1": {"n": len(zero), "implied_P0": mean([z[0] for z in zero]), "realized_P0": mean([z[1] for z in zero])},
            "implied_mean_vs_actual": {"n": len(means), "implied_mean_lb": mean([m[0] for m in means]),
                                       "actual_mean": mean([m[1] for m in means])},
            "units": units}


def realized_distribution(rows) -> dict[str, Any]:
    rows = [r for r in rows if r.get("y") is not None and r.get("actual") is not None]
    n = len(rows)
    if not n:
        return {"n": 0}
    bins = Counter(R.rel_bin(r["actual"], r["threshold"]) for r in rows)
    miss = Counter(R.miss_class(r["actual"], r["threshold"], r["y"], r.get("settle_source")) for r in rows)
    counts = Counter(int(r["actual"]) for r in rows)
    return {"n": n, "rel_bins": {b: {"n": bins.get(b, 0), "share": bins.get(b, 0) / n} for b in R.REL_BINS},
            "P_ge_t": mean([1.0 if r["actual"] >= r["threshold"] else 0.0 for r in rows]),
            "P_eq_t_minus_1": mean([1.0 if r["actual"] == r["threshold"] - 1 else 0.0 for r in rows]),
            "P_eq_t": mean([1.0 if r["actual"] == r["threshold"] else 0.0 for r in rows]),
            "P_le_t_minus_1": mean([1.0 if r["actual"] <= r["threshold"] - 1 else 0.0 for r in rows]),
            "mean_B": mean([r["B_yes_mid"] for r in rows]), "mean_actual": mean([r["actual"] for r in rows]),
            "mean_threshold": mean([r["threshold"] for r in rows]),
            "miss_classes": dict(miss), "actual_counts": {str(k): counts[k] for k in sorted(counts)}}


def distribution_models(rows, ladders, corpus) -> dict[str, Any]:
    """M5: Poisson fitted to each ladder's survival points; NB2 with the 2016-2025 dispersion at that mean; market;
    realized. Probabilities at the natural t."""
    disp = R.dispersion_by_bin([(c["b_ewma"], c["actual"]) for c in corpus if c.get("b_ewma") is not None])
    by_lad = {(l["game_id"], l["player_id"]): l for l in ladders}

    def alpha_at(mu):
        if not disp:
            return 0.0
        best = min(disp, key=lambda d: abs(d["mean"] - mu))
        return best["alpha_nb2"]

    units = []
    for r in rows:
        if r.get("y") is None or r.get("actual") is None:
            continue
        lad = by_lad.get((r["game_id"], r["player_id"]))
        if not lad:
            continue
        lam = R.fit_poisson_to_ladder([tuple(x) for x in lad["rungs"]])
        if lam is None:
            continue
        t = int(round(r["threshold"]))
        a = alpha_at(lam)
        pois = {"P_ge_t": R.poisson_sf(t, lam), "P_eq_t-1": R.poisson_sf(t - 1, lam) - R.poisson_sf(t, lam),
                "P_le_t-2": 1 - R.poisson_sf(t - 1, lam), "P0": 1 - R.poisson_sf(1, lam)}
        nb = {"P_ge_t": R.nb_sf(t, lam, a), "P_eq_t-1": R.nb_pmf(t - 1, lam, a) if t >= 1 else 0.0,
              "P_le_t-2": 1 - R.nb_sf(t - 1, lam, a), "P0": R.nb_pmf(0, lam, a)}
        act = r["actual"]
        real = {"P_ge_t": float(act >= t), "P_eq_t-1": float(act == t - 1), "P_le_t-2": float(act <= t - 2), "P0": float(act == 0)}
        units.append({"game_id": r["game_id"], "lam": lam, "alpha": a, "B": r["B_yes_mid"],
                      **{f"pois_{k}": v for k, v in pois.items()}, **{f"nb_{k}": v for k, v in nb.items()},
                      **{f"real_{k}": v for k, v in real.items()}})
    keys = ("P_ge_t", "P_eq_t-1", "P_le_t-2", "P0")
    summ = {k: {"poisson_fit_to_ladder": mean([u[f"pois_{k}"] for u in units]), "nb_same_mean": mean([u[f"nb_{k}"] for u in units]),
                "realized": mean([u[f"real_{k}"] for u in units])} for k in keys}
    summ["P_ge_t"]["market_B"] = mean([u["B"] for u in units])
    return {"n": len(units), "mean_lambda": mean([u["lam"] for u in units]), "summary": summ,
            "history_dispersion_2016_2025": disp}


def split(rows, key, label=None) -> dict[str, Any]:
    out = R.table_by([r for r in rows if r.get("y") is not None], key)
    return {"label": label, "cells": out}


def tercile_key(rows, field):
    v = [r[field] for r in rows if r.get(field) is not None]
    if len(v) < 3:
        return lambda r: None
    lo, hi = np.quantile(v, [1 / 3, 2 / 3])

    def k(r):
        x = r.get(field)
        if x is None:
            return None
        return "T1_low" if x <= lo else ("T3_high" if x > hi else "T2_mid")
    return k


def median_key(rows, field, lo_name="below_median", hi_name="above_median"):
    v = [r[field] for r in rows if r.get(field) is not None]
    if not v:
        return lambda r: None
    m = float(np.median(v))
    return lambda r: None if r.get(field) is None else (hi_name if r[field] > m else lo_name)


def role_analysis(rows, season) -> dict[str, Any]:
    pre = "pre_" if season == 2026 else ""
    rs = [r for r in rows if r.get("y") is not None]
    out = {
        "role_stability": split(rs, lambda r: r.get(f"{pre}role_stability")),
        "backfield": split(rs, lambda r: None if r.get("h_backfield_top_share") is None else
                           ("concentrated" if r["h_backfield_top_share"] >= R.CONCENTRATED_BACKFIELD else "committee")),
        "player_is_backfield_leader": split(rs, lambda r: None if r.get("h_player_backfield_share") is None or r.get("h_backfield_top_share") is None
                                            else ("leader" if abs(r["h_player_backfield_share"] - r["h_backfield_top_share"]) < 1e-9 else "not_leader")),
        "target_share_volatility": split(rs, median_key(rs, "h_target_share_sd6", "stable", "unstable")),
        "injury_designation": split(rs, lambda r: r.get(f"{pre}inj_status") or "NONE"),
        "snap_share_l_tercile": split(rs, tercile_key(rs, f"{pre}snap_share_l")),
        "target_share_l_tercile": split(rs, tercile_key(rs, f"{pre}sh_target_l")),
        "route_participation": "UNAVAILABLE: nflverse publishes no 2026 participation file; 2025 routes not in the Wave-1 rows",
    }
    return out


def recency(rows, corpus, season) -> dict[str, Any]:
    """M14: relative weight on last-game receptions -- market vs historical outcomes."""
    rs = [{**r, "last1": r.get("h_last1"), "long16": r.get("h_long16") if (r.get("h_n_hist") or 0) >= 6 else None}
          for r in rows if r.get("y") is not None]
    hist = [c for c in corpus if c.get("last1") is not None and c.get("long16") is not None]
    w_mkt = R.last_game_weight(rs, "market_median")
    w_out = R.last_game_weight(hist, "actual")
    # bootstrap market side by game, outcome side by game (independent samples)
    mk = R.boot_stat([r for r in rs if r.get("last1") is not None and r.get("long16") is not None],
                     lambda s: R.last_game_weight(s, "market_median"))
    ho = R.boot_stat(hist, lambda s: R.last_game_weight(s, "actual"), n_boot=400)
    diff = None
    if mk.get("ci95") and ho.get("ci95") and w_mkt is not None and w_out is not None:
        diff = {"est": w_mkt - w_out, "ci95_approx": [mk["ci95"][0] - ho["ci95"][1], mk["ci95"][1] - ho["ci95"][0]]}
        # p-value from the market bootstrap distribution shifted by the outcome point estimate (outcome n >> market n)
        rng_rows = [r for r in rs if r.get("last1") is not None and r.get("long16") is not None]
        keys = sorted({r["game_id"] for r in rng_rows})
        by = defaultdict(list)
        for r in rng_rows:
            by[r["game_id"]].append(r)
        rng = np.random.default_rng(R.SEED)
        draws = rng.integers(0, len(keys), size=(R.N_BOOT, len(keys)))
        vals = []
        for d in draws:
            s = [r for k in d for r in by[keys[k]]]
            v = R.last_game_weight(s, "market_median")
            if v is not None and np.isfinite(v):
                vals.append(v - w_out)
        a = np.asarray(vals)
        diff["p_two_sided"] = float(min(1.0, 2 * min((a <= 0).mean(), (a >= 0).mean())))
    spike = [r for r in rs if r.get("last1") is not None and r.get("long16") is not None]
    return {"market_last_game_weight": mk, "outcome_last_game_weight_2016_2025": {**ho, "n": len(hist)},
            "T14_market_minus_outcome": diff,
            "spike_split": split(spike, lambda r: "spike_last_ge_long_plus_2" if r["last1"] >= r["long16"] + 2 else
                                 ("dip_last_le_long_minus_2" if r["last1"] <= r["long16"] - 2 else "normal"))}


def mean_vs_median(rows) -> dict[str, Any]:
    rs = [r for r in rows if r.get("y") is not None and (r.get("h_n_hist") or 0) >= 6]
    if not rs:
        return {"n": 0}
    line = lambda r: r["threshold"] - 0.5  # noqa: E731
    closer = Counter()
    for r in rs:
        d = {"mean16": abs(line(r) - r["h_long16"]), "median16": abs(line(r) - r["h_median16"]), "last3": abs(line(r) - r["h_last3"])}
        closer[min(d, key=d.get)] += 1
    phist = [r for r in rs if r.get("h_phist_ge_t") is not None]
    return {"n": len(rs), "mean_line": mean([line(r) for r in rs]), "mean_hist_mean16": mean([r["h_long16"] for r in rs]),
            "mean_hist_median16": mean([r["h_median16"] for r in rs]), "mean_hist_mode16": mean([r.get("h_mode16") for r in rs]),
            "mean_last3": mean([r["h_last3"] for r in rs]), "mean_b_usage": mean([r.get("pre_b_usage", r.get("b_usage")) for r in rs]),
            "share_right_skewed_mean_gt_median": mean([1.0 if r["h_long16"] > r["h_median16"] else 0.0 for r in rs]),
            "line_closest_to": dict(closer),
            "market_B_minus_phist": R.boot_stat([{**r, "_d": r["B_yes_mid"] - r["h_phist_ge_t"]} for r in phist], R.mean_of("_d")),
            "mean_phist_ge_t": mean([r["h_phist_ge_t"] for r in phist]), "mean_B": mean([r["B_yes_mid"] for r in phist]),
            "realized_yes": mean([r["y"] for r in phist]),
            "by_line_vs_mean": split(rs, lambda r: "line_above_mean16" if line(r) > r["h_long16"] + 0.25 else
                                     ("line_below_mean16" if line(r) < r["h_long16"] - 0.25 else "line_near_mean16"))}


def model_vs_market(rows, season) -> dict[str, Any]:
    if season == 2026:
        rs = [r for r in rows if r.get("y") is not None and r.get("pre_model_median") is not None]
        med = lambda r: r["pre_model_median"]  # noqa: E731
        label = "frozen RB_receptions ridge (prop_models_2026.json) + median_offset, pregame rebuild at kickoff-300m"
    else:
        rs = [r for r in rows if r.get("y") is not None and r.get("pred_oos_wave1") is not None]
        med = lambda r: r["pred_oos_wave1"]  # noqa: E731
        label = "Wave-1 walk-forward OOS ridge prediction (2025 fold; mean, no median offset stored)"
    if not rs:
        return {"n": 0, "label": label}
    out = {"label": label, "n": len(rs),
           "mean_model_minus_t": mean([med(r) - r["threshold"] for r in rs]),
           "mean_model_minus_market_median": mean([med(r) - r["market_median"] for r in rs]),
           "model_mean_error": mean([r["actual"] - med(r) for r in rs if r.get("actual") is not None]),
           "share_actual_ge_model": mean([1.0 if r["actual"] >= med(r) else 0.0 for r in rs if r.get("actual") is not None]),
           "market_mean_error_vs_median": mean([r["actual"] - r["market_median"] for r in rs if r.get("actual") is not None]),
           "model_side": split(rs, lambda r: "model_below_t-0.5" if med(r) < r["threshold"] - 0.5 else "model_at_or_above_t-0.5"),
           "agreement": split(rs, lambda r: "agree_within_0.5" if abs(med(r) - r["market_median"]) <= 0.5 else
                              ("model_lower" if med(r) < r["market_median"] else "model_higher"))}
    if season == 2026:
        q = [-2.0011410493887944, -1.3006531303096456, None, 1.006448557093193, 2.430070865000213]

        def band(r):
            x = r["threshold"] - 0.5 - (r["pre_pred"])
            qs = [q[0], q[1], -0.30829267564634244, q[3], q[4]]
            labels = ["below_q10", "q10-q25", "q25-q50", "q50-q75", "q75-q90", "above_q90"]
            for i, b in enumerate(qs):
                if x < b:
                    return labels[i]
            return labels[-1]
        out["model_band_of_t"] = split(rs, band)
        out["band_note"] = "quantile interval of the frozen global residual band that t - 0.5 falls in; no model PMF is fabricated"
    return out


def environment(rows) -> dict[str, Any]:
    rs = [r for r in rows if r.get("y") is not None]
    return {"favourite": split(rs, lambda r: None if r.get("ctx_team_fav_points") is None else
                               ("favourite" if r["ctx_team_fav_points"] > 0 else "underdog_or_pk")),
            "team_implied_total": split(rs, median_key(rs, "ctx_team_implied_total")),
            "expected_script_sign": split(rs, lambda r: None if r.get("pre_ctx.expected_script", r.get("ctx.expected_script")) is None
                                          else ("positive" if (r.get("pre_ctx.expected_script", r.get("ctx.expected_script")) or 0) > 0 else "non_positive")),
            "opp_rb_rec_allowed_prev": split(rs, tercile_key(rs, "ctx_opp_rb_rec_allowed_prev")),
            "pace_pressure": "only through the frozen team features (ctx.expected_script); no separate pace/pressure split"}


def public_proxies(rows) -> dict[str, Any]:
    rs = [r for r in rows if r.get("y") is not None]
    return {"ppr_rank_prev": split(rs, lambda r: None if r.get("ctx_ppr_rank_prev") is None else
                                   ("top12" if r["ctx_ppr_rank_prev"] <= 12 else "13-24" if r["ctx_ppr_rank_prev"] <= 24 else "25+")),
            "ppr_rank_missing": sum(1 for r in rs if r.get("ctx_ppr_rank_prev") is None),
            "rec_per_game_prev": split(rs, tercile_key(rs, "ctx_rec_per_game_prev")),
            "listed_rungs": split(rs, lambda r: f"{r.get('n_rungs')}"),
            "volume_at_checkpoint": split(rs, tercile_key(rs, "ckpt_volume")),
            "open_interest_at_checkpoint": split(rs, tercile_key(rs, "ckpt_open_interest")),
            "prime_time": split(rs, lambda r: None if r.get("ctx_prime_time") is None else ("prime_time" if r["ctx_prime_time"] else "day"))}


def microstructure(rows, season) -> dict[str, Any]:
    rs = [r for r in rows if r.get("y") is not None]
    out = {"residual_by_representation": {rep: R.boot_stat([r for r in rs if r.get(rep) is not None], R.mean_of(f"r_{rep[0]}"))
                                          for rep in REPS},
           "yes_spread": split(rs, lambda r: None if r.get("yes_spread") is None else ("1c" if r["yes_spread"] <= 0.0100001 else ">1c")),
           "n_valid_rungs": split(rs, lambda r: r.get("n_valid")),
           "dist_from_half": split(rs, lambda r: R.bucket_label(r.get("dist_half"), R.DIST_BUCKETS))}
    if season == 2026:
        out.update({"ask_sum": split(rs, lambda r: None if r.get("ask_sum") is None else ("<=1.01" if r["ask_sum"] <= 1.0100001 else ">1.01")),
                    "checkpoint_age": split(rs, lambda r: None if r.get("checkpoint_age_min") is None else
                                            ("<=20m" if r["checkpoint_age_min"] <= 20 else "20-90m" if r["checkpoint_age_min"] <= 90 else ">90m")),
                    "staleness": split(rs, tercile_key(rs, "staleness_min")),
                    "top_of_book_yes_ask_size": split(rs, tercile_key(rs, "ckpt_yes_ask_size")),
                    "spread_distribution": dict(Counter(f"{r.get('yes_spread'):.2f}" for r in rs if r.get("yes_spread") is not None)),
                    "ask_sum_distribution": dict(Counter(f"{r.get('ask_sum'):.2f}" for r in rs if r.get("ask_sum") is not None)),
                    "history_quote_matches_checkpoint": dict(Counter(str(r.get("history_quote_matches_checkpoint")) for r in rs))})
    return out


def timing_2026(rows) -> dict[str, Any]:
    labs = ["earliest", "T-24h", "T-6h", "T-3h", "T-90m", "T-60m", "checkpoint"]
    out = {}
    rs = [r for r in rows if r.get("y") is not None and r.get("timeline")]
    for lab in labs:
        have = [(r, r["timeline"].get(lab)) for r in rs if r["timeline"].get(lab) and r["timeline"][lab].get("yes_bid") is not None
                and r["timeline"][lab].get("yes_ask") is not None]
        if not have:
            out[lab] = {"n": 0}
            continue
        u = [{"game_id": r["game_id"], "mid": (q["yes_bid"] + q["yes_ask"]) / 2, "y": r["y"], "res": r["y"] - (q["yes_bid"] + q["yes_ask"]) / 2,
              "no_ask": q.get("no_ask"), "spread": q["yes_ask"] - q["yes_bid"]} for r, q in have]
        out[lab] = {"n": len(u), "mean_mid": mean([x["mid"] for x in u]), "mean_spread": mean([x["spread"] for x in u]),
                    "realized_yes": mean([x["y"] for x in u]), "residual": R.boot_stat(u, R.mean_of("res")),
                    "mean_no_ask": mean([x["no_ask"] for x in u])}
    # same-row change: checkpoint mid - T-24h mid, and - earliest
    for a, b in (("earliest", "checkpoint"), ("T-24h", "checkpoint"), ("T-6h", "checkpoint"), ("T-90m", "checkpoint")):
        d = []
        for r in rs:
            qa, qb = r["timeline"].get(a), r["timeline"].get(b)
            if qa and qb and None not in (qa.get("yes_bid"), qa.get("yes_ask"), qb.get("yes_bid"), qb.get("yes_ask")):
                d.append({"game_id": r["game_id"], "chg": (qb["yes_bid"] + qb["yes_ask"]) / 2 - (qa["yes_bid"] + qa["yes_ask"]) / 2,
                          "y": r["y"]})
        out[f"change_{a}_to_{b}"] = {"n": len(d), "mean_mid_change": R.boot_stat(d, R.mean_of("chg")),
                                     "share_up": mean([1.0 if x["chg"] > 0 else 0.0 for x in d]),
                                     "share_down": mean([1.0 if x["chg"] < 0 else 0.0 for x in d]),
                                     "moved_toward_outcome": mean([1.0 if (x["chg"] > 0) == (x["y"] == 1) else 0.0 for x in d if x["chg"] != 0])}
    out["earliest_hours_before_kickoff"] = mean([r["timeline"]["earliest"]["hours_before"] for r in rs if r["timeline"].get("earliest")])
    return out


def timing_2025_impl(rows) -> dict[str, Any]:
    labs = ("T-48h", "T-24h", "T-12h", "T-6h", "T-3h", "T-90m", "T-30m", "T-0")
    out = {}
    rs = [r for r in rows if r.get("y") is not None and r.get("timeline")]
    for lab in labs:
        u = []
        for r in rs:
            s = r["timeline"].get(lab)
            if not s or s.get("bid") is None or s.get("ask") is None or s.get("book_empty"):
                continue
            if not W.valid(s["bid"], s["ask"]):
                continue
            m = (s["bid"] + s["ask"]) / 2
            u.append({"game_id": r["game_id"], "mid": m, "y": r["y"], "res": r["y"] - m, "spread": s["ask"] - s["bid"]})
        out[lab] = {"n": len(u), "mean_mid": mean([x["mid"] for x in u]), "mean_spread": mean([x["spread"] for x in u]),
                    "realized_yes": mean([x["y"] for x in u]), "residual": R.boot_stat(u, R.mean_of("res")) if u else None,
                    "note": "valid (W.valid) YES quotes only; RECONSTRUCTED basis"}
    return out


def settlement_audit(r26, r25) -> dict[str, Any]:
    rec26 = [r for r in r26 if r["stat"] == "receptions" and r["pop"] in ("P1", "P3", "P4")]
    uniq26 = {r["ticker"]: r for r in rec26}.values()
    rec25 = {r["ticker"]: r for r in r25 if r["checkpoint"] == "T-90m"}.values()
    mism26 = [{"ticker": r["ticker"], "threshold": r["threshold"], "actual": r.get("actual"), "result": r.get("result"),
               "note": r.get("actual_note")} for r in uniq26 if r.get("stat_agrees") is False]
    mism25 = [{"ticker": r["ticker"], "threshold": r["threshold"], "actual": r.get("actual"), "result": r.get("result")}
              for r in rec25 if r.get("stat_agrees") is False]
    allp = [r for r in r26 if r["pop"] in ("P1", "P3", "P4", "P5")]
    non_binary = sorted({(r["ticker"], r.get("settlement_value")) for r in allp if r.get("settle_source") == R.NON_BINARY_SETTLEMENT})
    # positive controls
    comp_fail = sum(1 for r in allp if r.get("no_win") is not None and r.get("yes_win") is not None and r["no_win"] == r["yes_win"])
    return {"rules_primary_example": next((r.get("rules_primary") for r in r26 if r["pop"] == "P1" and r.get("rules_primary")), None),
            "strike_type": dict(Counter(r.get("strike_type") for r in uniq26)),
            "floor_strike_minus_threshold": dict(Counter(str(round((r.get("floor_strike") or 0) - r["threshold"], 3)) for r in uniq26 if r.get("floor_strike") is not None)),
            "semantics": "YES iff stat >= t (floor_strike = t - 0.5, strike_type 'greater'); no push. rules_secondary: an active player "
                         "who never takes a snap settles at the pre-game fair price (non-binary).",
            "non_binary_settlements_2026": {"n": len(non_binary), "examples": non_binary[:20]},
            "exchange_vs_nflverse_2026": {"rungs_compared": sum(1 for r in uniq26 if r.get("stat_agrees") is not None),
                                          "mismatches": len(mism26), "rows": mism26[:50]},
            "exchange_vs_nflverse_2025": {"rungs_compared": sum(1 for r in rec25 if r.get("stat_agrees") is not None),
                                          "mismatches": len(mism25), "rows": mism25[:50]},
            "unsettled_2026": dict(Counter(f"{r['pop']}|{r.get('settle_source')}" for r in allp if r.get("y") is None)),
            "yes_no_complement_failures": comp_fail}


def positive_controls(ladders26, r26) -> dict[str, Any]:
    ordered_fail, mono_fail = 0, 0
    for lad in ladders26:
        ts = [x[0] for x in lad["rungs"]]
        if ts != sorted(ts):
            ordered_fail += 1
        ys = [(float(t), v) for t, v in lad.get("y_by_t", {}).items() if v is not None]
        ys.sort()
        if any(b[1] > a[1] for a, b in zip(ys, ys[1:], strict=False)):
            mono_fail += 1
    p3 = [r for r in r26 if r["pop"] == "P3" and r.get("y") is not None]
    by_t = defaultdict(list)
    for r in p3:
        by_t[r["threshold"]].append(r["y"])
    rate = {str(t): {"n": len(v), "yes_rate": float(np.mean(v))} for t, v in sorted(by_t.items())}
    return {"ladders": len(ladders26), "threshold_order_failures": ordered_fail, "realized_monotonicity_failures": mono_fail,
            "P3_yes_rate_by_threshold": rate}


def case_studies(p1) -> dict[str, Any]:
    sel = R.case_study_selection(p1)
    out = {}
    for side in ("top", "bottom"):
        out[side] = []
        for pid in sel[side]:
            rs = sorted([r for r in p1 if r["player_id"] == pid], key=lambda r: r["game_id"])
            out[side].append({"player_id": pid, "name": rs[0].get("player_name"), "team": rs[0].get("team"),
                              "summed_no_pnl": round(sum(r["no_pnl"] for r in rs), 4), "rows": [case_row(r) for r in rs]})
    return {"selection_rule": "players ranked by summed P1 NO P/L after P1 was fixed; ties -> more rows, then player id", **out}


def case_row(r) -> dict[str, Any]:
    tl = r.get("timeline") or {}
    mid = lambda q: None if not q or q.get("yes_bid") is None or q.get("yes_ask") is None else round((q["yes_bid"] + q["yes_ask"]) / 2, 3)  # noqa: E731
    t, a = r["threshold"], r.get("actual")
    if a is None:
        why = "no nflverse stat"
    elif r["y"] == 0:
        why = "YES lost: " + ("zero receptions" if a == 0 else "one short (near miss)" if a == t - 1 else f"{int(t - a)} short (low-volume game)")
    else:
        why = "YES won: " + ("exactly at the threshold" if a == t else f"{int(a - t)} above the threshold")
    return {"game_id": r["game_id"], "opp": r.get("opp"), "threshold": t, "yes_ask": r["yes_ask"], "no_ask": r["no_ask"],
            "actual": a, "no_pnl": round(r["no_pnl"], 4), "role_stability": r.get("pre_role_stability"),
            "inj_status": r.get("pre_inj_status"), "snap_share_l": r.get("pre_snap_share_l"), "sh_target_l": r.get("pre_sh_target_l"),
            "last1_rec": r.get("h_last1"), "last3_rec": r.get("h_last3"), "long16_rec": r.get("h_long16"),
            "last_targets": r.get("h_last_targets"), "model_median": r.get("pre_model_median"),
            "backfield_top_share": r.get("h_backfield_top_share"), "player_backfield_share": r.get("h_player_backfield_share"),
            "backfield_teammates": r.get("h_backfield_teammates"),
            "mid_earliest": mid(tl.get("earliest")), "mid_T-24h": mid(tl.get("T-24h")), "mid_checkpoint": mid(tl.get("checkpoint")),
            "data_only_reading": why}


def team_scheme(rows) -> dict[str, Any]:
    rs = [r for r in rows if r.get("no_pnl") is not None]
    return {"team": R.concentration(rs, "team"),
            "game_qb": {k: v for k, v in R.concentration(rs, "ctx_game_qb").items() if k != "table"},
            "qb_mobility_prev": split(rs, lambda r: None if r.get("ctx_qb_mobile") is None else ("mobile_top_tercile" if r["ctx_qb_mobile"] else "other")),
            "team_rb_target_share_prev": split(rs, tercile_key(rs, "ctx_team_rb_target_share_prev")),
            "backfield_team_season": {k: v for k, v in R.concentration([{**r, "_bf": f"{r['team']}-{r['season']}"} for r in rs], "_bf").items()
                                      if k != "table"},
            "offensive_coordinator": "UNAVAILABLE: no reliable timestamped OC/scheme source in the repository"}


def headline(rows) -> dict[str, Any]:
    rs = [r for r in rows if r.get("y") is not None]
    c = R.calib_summary(rs)
    c["no_roi_player_cluster"] = R.boot_stat(rs, R.roi_of("no"), cluster="player_id")
    c["resid_B_player_cluster"] = R.boot_stat(rs, R.mean_of("r_B"), cluster="player_id")
    return c


def main() -> int:
    build = json.loads((OUT / "build_manifest.json").read_text())
    r26 = read_gz(OUT / "rows_2026.jsonl.gz")
    r25 = read_gz(OUT / "rows_2025.jsonl.gz")
    l26 = read_gz(OUT / "ladders_2026.jsonl.gz")
    l25 = read_gz(OUT / "ladders_2025.jsonl.gz")
    corpus = read_gz(OUT / "rb_history_2016_2025.jsonl.gz")
    pops = populations(r26, r25)
    p1, p2, p3, p4, p5 = pops["P1"], pops["P2"], pops["P3"], pops["P4"], pops["P5"]
    l_p1 = [l for l in l26 if l["pop"] == "P1"]
    l_p2 = [l for l in l25 if l["checkpoint"] == "T-90m" and l["in_p2"]]
    controls_nat = [r for r in p4 + p5 if r.get("y") is not None]
    # ---- formal tests (protocol section 5)
    T2 = diff_test(p1, controls_nat)
    T2_matched = diff_test(p1, [r for r in controls_nat if matched(r)])
    T3 = diff_test([r for r in p3 if r["is_natural"]], [r for r in p3 if not r["is_natural"]])
    ivr_p1 = implied_vs_realized(l_p1)
    ivr_p1_C = implied_vs_realized(l_p1, "rungs_C")
    ivr_p2 = implied_vs_realized(l_p2)
    T27_tm1 = ivr_p1["bins"]["t-1"]["implied_minus_realized"]
    T27_le = ivr_p1["bins"]["<=t-2"]["implied_minus_realized"]
    conc = R.concentration(p1, "player_id")
    rec26 = recency(p1, corpus, 2026)
    tests = {"T2": T2, "T3": T3, "T5": T27_le, "T14": rec26["T14_market_minus_outcome"], "T27_t-1": T27_tm1, "T27_le_t-2": T27_le}
    pv = {k: (v or {}).get("p_two_sided") for k, v in tests.items()}
    q = R.bh(pv)
    formal = {k: {"est": (v or {}).get("est"), "ci95": (v or {}).get("ci95") or (v or {}).get("ci95_approx"), "p": pv[k], "q_bh": q[k]}
              for k, v in tests.items()}
    formal["T12_top5_share_of_pnl"] = {"est": conc["top5_share_of_pnl"], "note": "a share; no null test (protocol section 5)"}
    formal["note"] = "T5 and T27(<=t-2) are the same statistic by construction (both pre-registered); both kept in the BH family (conservative)."
    report = {
        "schema": R.VERSION,
        "protocol": {"commit": R.PROTOCOL_COMMIT, "sha256": R.PROTOCOL_SHA256,
                     "sha256_now": hashlib.sha256((ROOT / "docs/research/RB_RECEPTIONS_MECHANISM_PROTOCOL.md").read_bytes()).hexdigest()},
        "source_commit_build": build.get("code_sha"),
        "market_data_commit": build.get("market_data_commit"),
        "discovery_run": build.get("discovery_run"),
        "build": {k: build[k] for k in ("checks_2026", "observe_reproduction", "status_2025", "hashes", "exchange_settled_markets")},
        "wave2_pins": {"candidates": W.CANDIDATES_SHA256, "prop_models": W.PROP_MODELS_SHA256, "classifier": W.CLASSIFIER_SHA256,
                       "wf_total": W.WF_TOTAL_SHA256},
        "populations": {k: settlement_counts(v) for k, v in sorted(pops.items())},
        "headline": {"P1": headline(p1), "P2_T-90m": headline(p2), "P2_T-0": headline(pops["P2@T-0"]), "P3_every_valid_rung": headline(p3),
                     "P2_every_valid_rung_T-90m": headline(pops["P2_ALL_RUNGS"]),
                     "RB_receptions_outside_frozen_family_POST_HOC": headline(pops.get("RB_REC_OUTSIDE_FAMILY", []))},
        "formal_tests": formal,
        "M1_M2_controls": {"P1": R.calib_summary(p1), "P4_P5_pooled": R.calib_summary(controls_nat),
                           "P4_P5_pooled_matched": R.calib_summary([r for r in controls_nat if matched(r)]),
                           "T2_matched_POST_HOC_variant": T2_matched, "cells": negative_controls(pops)},
        "calibration": {"P1": calibration_tables(p1), "P2": calibration_tables(p2)},
        "microstructure": {"P1": microstructure(p1, 2026), "P2": microstructure(p2, 2025)},
        "M3_ladder": {"P3_by_offset": split(p3, lambda r: r.get("offset")), "P3_by_dist": split(p3, lambda r: R.bucket_label(r.get("dist_half"), R.DIST_BUCKETS)),
                      "P2_all_rungs_by_offset": split(pops["P2_ALL_RUNGS"], lambda r: r.get("offset")), "T3": T3},
        "ladder_shape": {"P1": ladder_shape(l_p1, "P1"), "P2": ladder_shape(l_p2, "P2"),
                         "all_2026_receptions": ladder_shape([l for l in l26 if l["stat"] == "receptions"], "2026 receptions")},
        "implied_distribution": {"P1_B": {k: v for k, v in ivr_p1.items() if k != "units"},
                                 "P1_C": {k: v for k, v in ivr_p1_C.items() if k != "units"},
                                 "P2_B": {k: v for k, v in ivr_p2.items() if k != "units"}},
        "realized_distribution": {"P1": realized_distribution(p1), "P2": realized_distribution(p2)},
        "distribution_models": {"P1": distribution_models(p1, l_p1, corpus), "P2": distribution_models(p2, l_p2, corpus)},
        "role": {"P1": role_analysis(p1, 2026), "P2": role_analysis(p2, 2025)},
        "recency": {"P1": rec26, "P2": recency(p2, corpus, 2025)},
        "mean_vs_median": {"P1": mean_vs_median(p1), "P2": mean_vs_median(p2)},
        "model_vs_market": {"P1": model_vs_market(p1, 2026), "P2": model_vs_market(p2, 2025)},
        "price_buckets": {"P1": no_table([r for r in p1 if r.get("y") is not None]), "P2": no_table([r for r in p2 if r.get("y") is not None])},
        "thresholds": {"P1": split(p1, lambda r: f"{int(r['threshold'])}+"), "P2": split(p2, lambda r: f"{int(r['threshold'])}+")},
        "concentration": {"P1": conc, "P2": R.concentration(p2, "player_id")},
        "team_scheme": {"P1": team_scheme(p1), "P2": team_scheme(p2)},
        "public": {"P1": public_proxies(p1), "P2": public_proxies(p2)},
        "environment": {"P1": environment(p1), "P2": environment(p2)},
        "timing": {"P1": timing_2026(p1), "P2": timing_2025_impl(p2)},
        "settlement": settlement_audit(r26, r25),
        "positive_controls": positive_controls([l for l in l26 if l["stat"] == "receptions"], r26),
        "case_studies": case_studies(p1),
        "statistics": {"seed": R.SEED, "n_boot": R.N_BOOT, "cluster": "game_id (player_id where stated)"},
    }
    pc = report["positive_controls"]
    st = report["settlement"]
    if pc["threshold_order_failures"] or st["yes_no_complement_failures"]:
        raise R.MechanismIntegrityError(f"positive control failed: {pc} {st['yes_no_complement_failures']}")
    payload = json.dumps(report, indent=1, sort_keys=True, default=_default) + "\n"
    (OUT / "mechanism_report.json").write_text(payload)
    print("mechanism_report.json sha256", hashlib.sha256(payload.encode()).hexdigest())
    print(json.dumps({"formal": formal, "P1": {k: report["headline"]["P1"].get(k) for k in ("n", "yes_rate", "no_record")}}, indent=1, default=_default))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
