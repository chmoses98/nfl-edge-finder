"""UNIVERSAL SCORECARD v2: every settled projection of every engine on one set of proper scores.

Input rows are settled v2 projection records (a projection joined to a Settlement): p_yes, contract_value, mid,
yes_bid/yes_ask, settled_yes, engine, model_arm, market_family, period, stat_family, horizon_label,
identity_confidence, market_identification, availability_state, liquidity, quote_width, evidence_class.

Metrics (all on the CONTRACT VALUE against the settled payout unless named otherwise):
    brier, log_loss, n, base_rate; mean model-vs-market Brier difference with a GAME-CLUSTERED standard error
    (rows of one game are not independent; the cluster is the game, or the ticker's event when there is none);
    calibration (reliability bins, ECE); sharpness (mean |p - 0.5|); directional hit rate against the mid;
    market Brier on the mid for the same rows (the benchmark the model must beat); and the executable side:
    net EV of the trades the model's own probabilities would have taken at the ask, fees applied once.

Rows whose evidence_class is HISTORICAL_RESEARCH are NEVER pooled with PROSPECTIVE_FROZEN rows: the scorecard
is built per evidence class and the report labels each block.
"""
from __future__ import annotations

import math
from collections import defaultdict

SCORECARD_VERSION = "scorecard-2.0.0"
SEGMENTS = ("engine", "model_arm", "market_family", "period", "stat_family", "horizon_label", "identity_confidence",
            "market_identification", "availability_state", "liquidity_band", "width_band", "semantic_confidence", "support_state")
WIDTH_BANDS = ((0.02, "<=2c"), (0.05, "3-5c"), (0.10, "6-10c"), (float("inf"), ">10c"))
LIQUIDITY_BANDS = ((1e-9, "none"), (100.0, "<$100"), (1000.0, "$100-1k"), (float("inf"), ">$1k"))
EPS = 1e-6


def _f(x):
    try:
        return None if x is None else float(x)
    except (TypeError, ValueError):
        return None


def _band(v, bands):
    v = _f(v)
    if v is None:
        return "unknown"
    for lim, name in bands:
        if v <= lim:
            return name
    return bands[-1][1]


def _brier(p, y):
    return (p - y) ** 2


def _logloss(p, y):
    p = min(max(p, EPS), 1 - EPS)
    return -(y * math.log(p) + (1 - y) * math.log(1 - p))


def _cluster_mean_se(values: list, clusters: list) -> tuple[float | None, float | None, int]:
    """Mean of per-row values with a cluster-robust standard error (clusters = games)."""
    if not values:
        return None, None, 0
    n = len(values); mean = sum(values) / n
    by = defaultdict(list)
    for v, c in zip(values, clusters):
        by[c].append(v)
    G = len(by)
    if G < 2:
        return mean, None, G
    # cluster sums of residuals
    s = sum((sum(v - mean for v in vs)) ** 2 for vs in by.values())
    se = math.sqrt(s) / n * math.sqrt(G / (G - 1))
    return mean, se, G


def _calibration(pairs, width=0.1):
    bins = defaultdict(lambda: [0, 0.0, 0.0])
    for p, y in pairs:
        b = min(int(p / width), int(round(1 / width)) - 1)
        bins[b][0] += 1; bins[b][1] += p; bins[b][2] += y
    out, ece, n = [], 0.0, len(pairs)
    for b in sorted(bins):
        c, sp, sy = bins[b]
        out.append({"bin": f"{b*width:.1f}-{(b+1)*width:.1f}", "n": c, "mean_p": sp / c, "mean_y": sy / c})
        ece += c / n * abs(sp / c - sy / c)
    return {"bins": out, "ece": ece}


def metric_block(rows: list) -> dict:
    """rows: settled records with contract_value, settled_yes; optional mid, yes_ask, game_id."""
    pairs, mpairs, diffs, clusters, hits, tie_kind = [], [], [], [], [], 0
    for r in rows:
        cv, y = _f(r.get("contract_value")), _f(r.get("settled_yes"))
        if cv is None or y is None:
            continue
        cl = r.get("game_id") or r.get("event_ticker") or r.get("ticker")
        pairs.append((cv, y)); clusters.append(cl)
        mid = _f(r.get("mid"))
        if mid is not None:
            mpairs.append((mid, y)); diffs.append(_brier(cv, y) - _brier(mid, y))
            if abs(cv - mid) > 1e-9:
                hits.append(1.0 if (cv > mid) == (y > mid) else 0.0)
        if r.get("settlement_kind") == "tie_split":
            tie_kind += 1
    if not pairs:
        return {"n": 0}
    n = len(pairs)
    out = {"n": n, "n_games": len(set(clusters)), "base_rate": sum(y for _, y in pairs) / n,
           "brier": sum(_brier(p, y) for p, y in pairs) / n, "log_loss": sum(_logloss(p, y) for p, y in pairs) / n,
           "sharpness": sum(abs(p - 0.5) for p, _ in pairs) / n, "calibration": _calibration(pairs), "n_tie_split": tie_kind}
    if mpairs:
        m = len(mpairs)
        out["market_n"] = m
        out["market_brier"] = sum(_brier(p, y) for p, y in mpairs) / m
        out["market_log_loss"] = sum(_logloss(p, y) for p, y in mpairs) / m
        mean, se, G = _cluster_mean_se(diffs, [c for c, r in zip(clusters, rows) if _f(r.get("mid")) is not None and _f(r.get("contract_value")) is not None and _f(r.get("settled_yes")) is not None])
        out["brier_minus_market"] = mean; out["brier_minus_market_se_clustered"] = se; out["clusters"] = G
        out["brier_minus_market_z"] = (mean / se) if (se and se > 0) else None
        out["directional_hit_rate"] = (sum(hits) / len(hits)) if hits else None
        out["n_directional"] = len(hits)
    return out


def executable_block(rows: list, schedule=None, as_of=None, *, edge_min: float = 0.05) -> dict:
    """What taking the model's own edges at the ASK would have paid, fees once. No mid anywhere."""
    from nfl_edge.execution import fees as F
    taken, pnl, unknown = 0, 0.0, 0
    for r in rows:
        cv, y = _f(r.get("contract_value")), _f(r.get("settled_yes"))
        ya, na = _f(r.get("yes_ask")), _f(r.get("no_ask"))
        if cv is None or y is None:
            continue
        side = None
        if ya is not None and 0 < ya < 1 and cv - ya >= edge_min:
            side, price, payout = "YES", ya, y
        elif na is not None and 0 < na < 1 and (1 - cv) - na >= edge_min:
            side, price, payout = "NO", na, 1.0 - y
        if side is None:
            continue
        fee = 0.0
        if schedule is not None:
            try:
                q = F.net_executable_ev(price, price, 1.0, schedule, series_ticker=r.get("series_ticker"), as_of=as_of)
                if not q.is_known:
                    unknown += 1; continue
                fee = -float(q.net_ev_dollars)
            except Exception:  # noqa: BLE001
                unknown += 1; continue
        taken += 1
        pnl += payout - price - fee
    return {"n_taken": taken, "pnl_per_contract": (pnl / taken) if taken else None, "pnl_total": pnl, "n_fee_unknown": unknown,
            "edge_min": edge_min, "note": "executable price = ask at observation; fee applied once per contract; no slippage model"}


def segment(rows, key, min_n=1):
    by = defaultdict(list)
    for r in rows:
        v = r.get(key)
        if key == "liquidity_band":
            v = _band(r.get("liquidity"), LIQUIDITY_BANDS)
        elif key == "width_band":
            v = _band(r.get("quote_width"), WIDTH_BANDS)
        by[str(v)].append(r)
    return {k: metric_block(v) for k, v in sorted(by.items()) if len(v) >= min_n}


def build_scorecard(rows: list, *, schedule=None, as_of=None, min_segment_n: int = 5) -> dict:
    by_class = defaultdict(list)
    for r in rows:
        by_class[r.get("evidence_class") or "UNKNOWN"].append(r)
    out = {"version": SCORECARD_VERSION, "n_rows": len(rows), "by_evidence_class": {}}
    for cls, rs in by_class.items():
        settled = [r for r in rs if _f(r.get("settled_yes")) is not None and _f(r.get("contract_value")) is not None]
        block = {"n_settled": len(settled), "n_unsettled": len(rs) - len(settled), "overall": metric_block(settled),
                 "executable": executable_block(settled, schedule, as_of), "segments": {k: segment(settled, k, min_segment_n) for k in SEGMENTS}}
        # arm-vs-arm on the same contracts (paired), per stat family
        block["paired_arms"] = paired_arms(settled)
        out["by_evidence_class"][cls] = block
    return out


def paired_arms(rows: list) -> dict:
    """Brier per arm on exactly the contracts every arm priced (same snapshot + ticker), by stat family."""
    by_key = defaultdict(dict)
    for r in rows:
        by_key[(r.get("snapshot_id"), r.get("ticker"))][r.get("model_arm")] = r
    arms = sorted({r.get("model_arm") for r in rows if r.get("model_arm")})
    out = {}
    for fam_key in sorted({(r.get("engine"), r.get("stat_family") or r.get("market_family")) for r in rows}):
        common = [d for d in by_key.values() if all(a in d for a in arms) and (next(iter(d.values())).get("engine"), next(iter(d.values())).get("stat_family") or next(iter(d.values())).get("market_family")) == fam_key]
        if len(common) < 5 or len(arms) < 2:
            continue
        res = {"n": len(common)}
        for a in arms:
            res[a] = sum(_brier(_f(d[a]["contract_value"]), _f(d[a]["settled_yes"])) for d in common) / len(common)
        mids = [d[arms[0]] for d in common if _f(d[arms[0]].get("mid")) is not None]
        if mids:
            res["market_mid"] = sum(_brier(_f(d["mid"]), _f(d["settled_yes"])) for d in mids) / len(mids)
        out["/".join(str(x) for x in fam_key)] = res
    return out


def _fmt(v, nd=4):
    return "-" if v is None else (f"{v:.{nd}f}" if isinstance(v, float) else str(v))


def render(sc: dict, title="Shadow v2 scorecard") -> str:
    L = [f"# {title}", "", f"scorecard {sc['version']}; rows {sc['n_rows']}", ""]
    for cls, b in sc["by_evidence_class"].items():
        o = b["overall"]
        L += [f"## Evidence class: {cls}", "", f"settled {b['n_settled']}, unsettled {b['n_unsettled']}", ""]
        if o.get("n"):
            L += ["| metric | model | market (mid) |", "|---|---|---|",
                  f"| n | {o['n']} | {o.get('market_n', '-')} |", f"| Brier | {_fmt(o['brier'])} | {_fmt(o.get('market_brier'))} |",
                  f"| log loss | {_fmt(o['log_loss'])} | {_fmt(o.get('market_log_loss'))} |",
                  f"| Brier - market (clustered by game) | {_fmt(o.get('brier_minus_market'))} ± {_fmt(o.get('brier_minus_market_se_clustered'))} (z {_fmt(o.get('brier_minus_market_z'), 2)}) | |",
                  f"| ECE | {_fmt(o['calibration']['ece'])} | |", f"| sharpness | {_fmt(o['sharpness'])} | |",
                  f"| directional hit rate vs mid | {_fmt(o.get('directional_hit_rate'))} (n={o.get('n_directional')}) | |", ""]
            e = b["executable"]
            L += [f"executable (ask, fees once, edge >= {e['edge_min']}): taken {e['n_taken']}, P&L/contract {_fmt(e['pnl_per_contract'])}, fee-unknown {e['n_fee_unknown']}", ""]
            for seg in ("engine", "model_arm", "market_family", "stat_family", "horizon_label", "market_identification", "availability_state", "liquidity_band"):
                s = b["segments"].get(seg) or {}
                if not s:
                    continue
                L += [f"### by {seg}", "", "| value | n | Brier | market | diff ± se (z) |", "|---|---|---|---|---|"]
                for k, m in s.items():
                    L.append(f"| {k} | {m.get('n')} | {_fmt(m.get('brier'))} | {_fmt(m.get('market_brier'))} | {_fmt(m.get('brier_minus_market'))} ± {_fmt(m.get('brier_minus_market_se_clustered'))} ({_fmt(m.get('brier_minus_market_z'), 2)}) |")
                L.append("")
            if b["paired_arms"]:
                L += ["### paired arms (same contracts)", ""]
                for k, m in b["paired_arms"].items():
                    L.append(f"- {k}: n={m['n']}; " + ", ".join(f"{a} {_fmt(v)}" for a, v in m.items() if a != "n"))
                L.append("")
        else:
            L += ["no settled rows", ""]
    return "\n".join(L)
