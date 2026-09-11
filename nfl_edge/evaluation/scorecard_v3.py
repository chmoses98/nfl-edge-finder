"""SCORECARD v3 over research rows: model vs market at the horizon, model vs close, CLV, executable P&L, per segment.

Every block is labelled with an EVIDENCE TYPE (Part 22):
    DESCRIPTIVE            counts, coverage, means with no inference claimed
    HYPOTHESIS_GENERATING  any slice cut after the fact (bands, subgroups) -- never an edge, never confirmatory
    PREREGISTERED_TEST     a slice named in the hypothesis registry BEFORE its evaluation window (none exist for Week 1)
    CONFIRMATORY           a preregistered test evaluated on its future window (none exist for Week 1)

Standard errors of paired differences are clustered by game. HISTORICAL_RESEARCH and PROSPECTIVE_FROZEN rows are
scored separately and never pooled. CLV IS NOT PROFIT; the sign convention is printed on every report.
"""
from __future__ import annotations

import math
from collections import defaultdict

from nfl_edge.evaluation.clv import SIGN_CONVENTION

SCORECARD_VERSION = "scorecard-3.0.0"
DESCRIPTIVE, HYPOTHESIS_GENERATING, PREREGISTERED_TEST, CONFIRMATORY = "DESCRIPTIVE", "HYPOTHESIS_GENERATING", "PREREGISTERED_TEST", "CONFIRMATORY"
SEGMENTS = ("horizon_label", "horizon_quality", "engine", "model_arm", "family_group", "market_family", "stat_family", "player_position", "probability_band",
            "price_band", "disagreement_band", "width_band", "liquidity_band", "ctx_availability_state", "ctx_injury_state", "close_quality", "ladder_identification",
            "semantic_confidence", "support_state", "model_side")
EPS = 1e-6


def _f(x):
    try:
        return None if x is None else float(x)
    except (TypeError, ValueError):
        return None


def _mean(xs):
    return (sum(xs) / len(xs)) if xs else None


def _median(xs):
    if not xs:
        return None
    s = sorted(xs)
    return s[len(s) // 2]


def _cluster(values, clusters):
    if not values:
        return None, None, 0
    n = len(values); mean = sum(values) / n
    by = defaultdict(list)
    for v, c in zip(values, clusters):
        by[c].append(v - mean)
    G = len(by)
    if G < 2:
        return mean, None, G
    se = math.sqrt(sum(sum(v) ** 2 for v in by.values())) / n * math.sqrt(G / (G - 1))
    return mean, se, G


def _logloss(p, y):
    p = min(max(p, EPS), 1 - EPS)
    return -(y * math.log(p) + (1 - y) * math.log(1 - p))


def _calibration(pairs, width=0.1):
    bins = defaultdict(lambda: [0, 0.0, 0.0])
    for p, y in pairs:
        b = min(int(p / width), 9)
        bins[b][0] += 1; bins[b][1] += p; bins[b][2] += y
    n = len(pairs)
    ece = sum(c / n * abs(sp / c - sy / c) for c, sp, sy in bins.values()) if n else None
    return {"ece": ece, "bins": [{"bin": f"{b/10:.1f}-{(b+1)/10:.1f}", "n": c, "mean_p": sp / c, "mean_y": sy / c} for b, (c, sp, sy) in sorted(bins.items())]}


def _resolution(pairs):
    """Murphy resolution: variance of the bin outcome rates around the base rate (weighted)."""
    if not pairs:
        return None
    base = sum(y for _, y in pairs) / len(pairs)
    bins = defaultdict(list)
    for p, y in pairs:
        bins[min(int(p * 10), 9)].append(y)
    return sum(len(v) / len(pairs) * (sum(v) / len(v) - base) ** 2 for v in bins.values())


def outcome_block(rows: list) -> dict:
    """Model, horizon market and close market against the OUTCOME (settled rows only)."""
    m, h, c, dmh, dmc, cl = [], [], [], [], [], []
    for r in rows:
        y, cv = _f(r.get("settled_yes")), _f(r.get("contract_value"))
        if y is None or cv is None:
            continue
        m.append((cv, y)); g = r.get("game_id") or r.get("ticker")
        hm, cm = _f(r.get("h_mid")), _f(r.get("c_mid"))
        if hm is not None:
            h.append((hm, y)); dmh.append(((cv - y) ** 2 - (hm - y) ** 2, g))
        if cm is not None:
            c.append((cm, y)); dmc.append(((cv - y) ** 2 - (cm - y) ** 2, g))
    if not m:
        return {"n": 0, "evidence_type": DESCRIPTIVE}
    out = {"evidence_type": DESCRIPTIVE, "n": len(m), "n_games": len({r.get("game_id") for r in rows if _f(r.get("settled_yes")) is not None}), "base_rate": _mean([y for _, y in m]),
           "brier_model": _mean([(p - y) ** 2 for p, y in m]), "log_loss_model": _mean([_logloss(p, y) for p, y in m]), "calibration": _calibration(m),
           "resolution": _resolution(m), "sharpness": _mean([abs(p - 0.5) for p, _ in m])}
    if h:
        out["brier_market_horizon"] = _mean([(p - y) ** 2 for p, y in h]); out["n_market_horizon"] = len(h)
        mean, se, G = _cluster([d for d, _ in dmh], [g for _, g in dmh])
        out["model_minus_market_brier"] = mean; out["model_minus_market_se"] = se; out["model_minus_market_z"] = (mean / se if se else None); out["clusters"] = G
    if c:
        out["brier_market_close"] = _mean([(p - y) ** 2 for p, y in c]); out["n_market_close"] = len(c)
        mean, se, G = _cluster([d for d, _ in dmc], [g for _, g in dmc])
        out["model_minus_close_brier"] = mean; out["model_minus_close_se"] = se; out["model_minus_close_z"] = (mean / se if se else None)
    return out


def clv_block(rows: list) -> dict:
    ok = [r for r in rows if r.get("clv_status") == "CLV_OK"]
    mids = [_f(r["clv_mid_toward_model"]) for r in ok if r.get("clv_mid_toward_model") is not None]
    ex = [_f(r["clv_exec_toward_model"]) for r in ok if r.get("clv_exec_toward_model") is not None]
    net = [_f(r["clv_net_of_fee"]) for r in ok if r.get("clv_net_of_fee") is not None]
    mv = [r.get("movement") for r in ok]
    closer = [r.get("model_closer_than_horizon") for r in ok if r.get("model_closer_than_horizon") is not None]
    mean, se, G = _cluster(mids, [r.get("game_id") for r in ok if r.get("clv_mid_toward_model") is not None])
    return {"evidence_type": DESCRIPTIVE, "sign_convention": SIGN_CONVENTION, "n_rows": len(rows), "n_clv_ok": len(ok),
            "n_close_missing": sum(1 for r in rows if r.get("clv_status") == "CLV_CLOSE_MISSING"), "n_no_view": sum(1 for r in rows if r.get("clv_status") == "NO_VIEW"),
            "mean_clv_mid": mean, "se_clv_mid_clustered": se, "median_clv_mid": _median(mids), "positive_clv_rate": (_mean([1.0 if x > 0 else 0.0 for x in mids]) if mids else None),
            "clv_distribution": ({"p10": sorted(mids)[int(0.1 * (len(mids) - 1))], "p25": sorted(mids)[int(0.25 * (len(mids) - 1))], "p75": sorted(mids)[int(0.75 * (len(mids) - 1))], "p90": sorted(mids)[int(0.9 * (len(mids) - 1))]} if mids else None),
            "mean_clv_exec": _mean(ex), "mean_clv_net_of_fee": _mean(net),
            "movement_toward_rate": (_mean([1.0 if x == "toward" else 0.0 for x in mv if x in ("toward", "away")]) if any(x in ("toward", "away") for x in mv) else None),
            "model_closer_to_close_rate": _mean([1.0 if x else 0.0 for x in closer]) if closer else None,
            "by_close_quality": {q: sum(1 for r in rows if r.get("close_quality") == q) for q in ("EXCELLENT", "GOOD", "STALE", "MISSING")}}


def executable_block(rows: list) -> dict:
    g = [_f(r["exec_pnl_gross"]) for r in rows if r.get("exec_pnl_gross") is not None]
    n = [_f(r["exec_pnl_net"]) for r in rows if r.get("exec_pnl_net") is not None]
    return {"evidence_type": DESCRIPTIVE, "n_taken": len(g), "pnl_gross_per_contract": _mean(g), "pnl_net_per_contract": _mean(n), "n_fee_known": len(n),
            "note": "entry at the horizon ask on the model's side, one contract, fee once; no slippage, no size; CLV/P&L is not proven EV"}


def metric_block(rows: list) -> dict:
    return {"n": len(rows), "n_games": len({r.get("game_id") for r in rows}), "outcome": outcome_block(rows), "clv": clv_block(rows), "executable": executable_block(rows),
            "mean_width": _mean([_f(r["h_width"]) for r in rows if r.get("h_width") is not None]), "mean_liquidity": _mean([_f(r["h_liquidity"]) for r in rows if r.get("h_liquidity") is not None])}


def segment(rows, key, min_n=5):
    by = defaultdict(list)
    for r in rows:
        by[str(r.get(key))].append(r)
    return {k: {**metric_block(v), "evidence_type": HYPOTHESIS_GENERATING} for k, v in sorted(by.items()) if len(v) >= min_n}


def build(rows: list, *, min_segment_n: int = 5) -> dict:
    by_cls = defaultdict(list)
    for r in rows:
        by_cls[r.get("evidence_class") or "UNKNOWN"].append(r)
    out = {"version": SCORECARD_VERSION, "sign_convention": SIGN_CONVENTION, "n_rows": len(rows), "by_evidence_class": {}}
    for cls, rs in by_cls.items():
        with_p = [r for r in rs if r.get("contract_value") is not None]
        out["by_evidence_class"][cls] = {"n_rows": len(rs), "n_with_probability": len(with_p), "overall": metric_block(with_p),
                                         "segments": {k: segment(with_p, k, min_segment_n) for k in SEGMENTS},
                                         "arm_by_family": _arm_by_family(with_p), "candidate_slices_considered": sum(len(segment(with_p, k, 1)) for k in SEGMENTS)}
    return out


def _arm_by_family(rows):
    """Which arm best predicted the outcome, the close, and the movement direction, per family group (Part 10)."""
    by = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by[r.get("family_group")][r.get("model_arm")].append(r)
    out = {}
    for fam, arms in by.items():
        res = {}
        for arm, rs in arms.items():
            o, c = outcome_block(rs), clv_block(rs)
            res[arm] = {"n": len(rs), "brier_model": o.get("brier_model"), "model_minus_market_brier": o.get("model_minus_market_brier"), "model_minus_close_brier": o.get("model_minus_close_brier"),
                        "mean_clv_mid": c.get("mean_clv_mid"), "movement_toward_rate": c.get("movement_toward_rate"), "model_closer_to_close_rate": c.get("model_closer_to_close_rate")}
        def best(key, lower=True):
            cands = [(a, v[key]) for a, v in res.items() if v.get(key) is not None]
            if not cands:
                return None
            return (min if lower else max)(cands, key=lambda x: x[1])[0]
        out[fam] = {"arms": res, "best_outcome_arm": best("brier_model"), "best_close_arm": best("model_minus_close_brier"), "best_movement_arm": best("movement_toward_rate", lower=False),
                    "evidence_type": HYPOTHESIS_GENERATING}
    return out


def _fmt(v, nd=4):
    return "-" if v is None else (f"{v:.{nd}f}" if isinstance(v, float) else str(v))


def render(sc: dict, title="Shadow v2 scorecard v3") -> str:
    L = [f"# {title}", "", f"scorecard {sc['version']}; rows {sc['n_rows']}", "", f"**CLV sign convention:** {sc['sign_convention']}. CLV is not profit.", ""]
    for cls, b in sc["by_evidence_class"].items():
        o, c, e = b["overall"]["outcome"], b["overall"]["clv"], b["overall"]["executable"]
        L += [f"## Evidence class: {cls} (rows {b['n_rows']}, with probability {b['n_with_probability']})", "",
              "| metric | value |", "|---|---|",
              f"| settled n / games | {o.get('n', 0)} / {o.get('n_games', 0)} |", f"| Brier model / market@horizon / market@close | {_fmt(o.get('brier_model'))} / {_fmt(o.get('brier_market_horizon'))} / {_fmt(o.get('brier_market_close'))} |",
              f"| model - market Brier (clustered) | {_fmt(o.get('model_minus_market_brier'))} ± {_fmt(o.get('model_minus_market_se'))} (z {_fmt(o.get('model_minus_market_z'), 2)}) |",
              f"| model - close Brier (clustered) | {_fmt(o.get('model_minus_close_brier'))} ± {_fmt(o.get('model_minus_close_se'))} (z {_fmt(o.get('model_minus_close_z'), 2)}) |",
              f"| log loss / ECE / resolution | {_fmt(o.get('log_loss_model'))} / {_fmt((o.get('calibration') or {}).get('ece'))} / {_fmt(o.get('resolution'))} |",
              f"| CLV ok / close missing / no view | {c['n_clv_ok']} / {c['n_close_missing']} / {c['n_no_view']} |",
              f"| mean / median CLV (mid, toward model) | {_fmt(c.get('mean_clv_mid'))} ± {_fmt(c.get('se_clv_mid_clustered'))} / {_fmt(c.get('median_clv_mid'))} |",
              f"| positive-CLV rate / toward-rate / model closer to close | {_fmt(c.get('positive_clv_rate'), 3)} / {_fmt(c.get('movement_toward_rate'), 3)} / {_fmt(c.get('model_closer_to_close_rate'), 3)} |",
              f"| executable P&L gross / net per contract (n) | {_fmt(e.get('pnl_gross_per_contract'))} / {_fmt(e.get('pnl_net_per_contract'))} ({e['n_taken']}) |", ""]
        for seg in ("horizon_label", "model_arm", "family_group", "disagreement_band", "close_quality", "horizon_quality", "ladder_identification", "ctx_availability_state", "width_band", "liquidity_band"):
            s = b["segments"].get(seg) or {}
            if not s:
                continue
            L += [f"### by {seg}  (HYPOTHESIS_GENERATING)", "", "| value | n | games | Brier model | market@h | model-market ± se | mean CLV | +CLV rate | toward rate | P&L net |", "|---|---|---|---|---|---|---|---|---|---|"]
            for k, m in s.items():
                o2, c2, e2 = m["outcome"], m["clv"], m["executable"]
                L.append(f"| {k} | {m['n']} | {m['n_games']} | {_fmt(o2.get('brier_model'))} | {_fmt(o2.get('brier_market_horizon'))} | {_fmt(o2.get('model_minus_market_brier'))} ± {_fmt(o2.get('model_minus_market_se'))} | "
                         f"{_fmt(c2.get('mean_clv_mid'))} | {_fmt(c2.get('positive_clv_rate'), 3)} | {_fmt(c2.get('movement_toward_rate'), 3)} | {_fmt(e2.get('pnl_net_per_contract'))} |")
            L.append("")
        if b["arm_by_family"]:
            L += ["### arm by family (HYPOTHESIS_GENERATING)", "", "| family | best vs outcome | best vs close | best movement | arms |", "|---|---|---|---|---|"]
            for fam, v in sorted(b["arm_by_family"].items()):
                L.append(f"| {fam} | {v['best_outcome_arm']} | {v['best_close_arm']} | {v['best_movement_arm']} | " + ", ".join(f"{a} n={x['n']} B={_fmt(x['brier_model'])} clv={_fmt(x['mean_clv_mid'])}" for a, x in v["arms"].items()) + " |")
            L.append("")
        L.append(f"candidate slices considered in this block: {b['candidate_slices_considered']} (multiple-comparison context for any subgroup finding)")
        L.append("")
    return "\n".join(L)
