"""Long-term scorecard for the handicap experiment.

The question the ledger exists to answer:

    does  DATA + MODEL + MARKET + CHATGPT HANDICAP  beat  MODEL ALONE  or  RAW DISAGREEMENT ALONE ?

So every metric is computed for three forecasters on the identical set of resolved recommendations -- model,
market, handicapper -- and never for one alone. A handicapper Brier score with nothing to compare it against
answers no question at all.

Two deliberate refusals:

  * TEST_ONLY records never enter any number here.
  * With no resolved recommendations the report says so and returns empty breakdowns. It does not print
    zeros, which read like measurements. There is currently no history by construction: the ledger begins
    prospectively and nothing is backfilled.

PASS records are carried through the same pipeline as RECOMMENDED ones. The comparison of what was taken
against what was declined is the most informative thing this ledger will ever produce, and it only works if
passes are evaluated with equal rigour.
"""
from __future__ import annotations

from collections import defaultdict


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return None if not xs else sum(xs) / len(xs)


def _brier(prob, realised):
    return None if prob is None or realised is None else (prob - realised) ** 2


def _forecast_metrics(pairs):
    """pairs: [(probability, realised 0/1)] -> Brier, log loss, mean error, n."""
    import math
    ps = [(p, r) for p, r in pairs if p is not None and r is not None]
    if not ps:
        return {"n": 0}
    br = _mean([(p - r) ** 2 for p, r in ps])
    ll = _mean([-(r * math.log(max(p, 1e-9)) + (1 - r) * math.log(max(1 - p, 1e-9))) for p, r in ps])
    return {"n": len(ps), "brier": round(br, 6), "log_loss": round(ll, 6),
            "mean_signed_error": round(_mean([p - r for p, r in ps]), 6)}


def build_scorecard(recommendations: list, evaluations: list, executions: list) -> dict:
    ev_by_rec = {e["recommendation_id"]: e for e in evaluations}
    ex_by_rec = defaultdict(list)
    for x in executions:
        ex_by_rec[x["recommendation_id"]].append(x)

    resolved, unresolved = [], []
    for r in recommendations:
        e = ev_by_rec.get(r["recommendation_id"])
        if e and e.get("settlement") is not None:
            resolved.append((r, e))
        else:
            unresolved.append((r, e))

    out = {
        "n_recommendations": len(recommendations),
        "n_evaluated": len(evaluations),
        "n_resolved": len(resolved),
        "n_unresolved": len(unresolved),
        "n_executions": len(executions),
        "by_decision": dict(_count(r.get("decision") for r in recommendations)),
    }
    if not resolved:
        out["status"] = "NO RESOLVED RECOMMENDATIONS"
        out["note"] = ("The ledger begins prospectively and nothing is backfilled, so there is no history "
                       "to score yet. Breakdowns are withheld rather than reported as zeros.")
        out["breakdowns"] = {}
        return out

    out["status"] = "RESOLVED SAMPLE PRESENT"
    out["headline"] = _headline(resolved, ex_by_rec)
    out["forecaster_comparison"] = _forecasters(resolved)
    out["breakdowns"] = _breakdowns(resolved, ex_by_rec)
    out["recommended_vs_pass"] = _rec_vs_pass(resolved)
    return out


def _count(it):
    c = defaultdict(int)
    for x in it:
        c[x] += 1
    return c


def _realised(r, e):
    """1 if the position won, 0 if it lost -- from the position's point of view, not the contract's."""
    s = e.get("settlement")
    if s is None:
        return None
    return 1.0 if ((s >= 0.5) if r.get("side", "YES") == "YES" else (s < 0.5)) else 0.0


def _side_prob(p, side):
    return None if p is None else (p if side == "YES" else 1.0 - p)


def _headline(resolved, ex_by_rec):
    taken = [(r, e) for r, e in resolved if r.get("decision") == "RECOMMENDED"]
    wins = sum(1 for r, e in taken if e.get("outcome") == "WIN")
    clv = [e.get("clv") for _, e in taken]
    clv_x = [e.get("clv_executable") for _, e in taken]
    staked = pnl = 0.0
    for r, e in taken:
        for x in ex_by_rec.get(r["recommendation_id"], []):
            staked += x.get("stake") or 0
            if e.get("pnl") is not None:
                pnl += e["pnl"]
    return {
        "recommendations_resolved": len(taken),
        "wins": wins, "losses": len(taken) - wins,
        "win_rate": None if not taken else round(wins / len(taken), 4),
        "mean_clv": None if not clv else round(_mean(clv) or 0, 5),
        "mean_clv_executable": None if not clv_x else round(_mean(clv_x) or 0, 5),
        "positive_clv_rate": None if not clv else round(
            sum(1 for c in clv if c is not None and c > 0) / max(len([c for c in clv if c is not None]), 1), 4),
        "dollars_staked": round(staked, 2),
        "pnl": round(pnl, 2),
        "roi": None if staked <= 0 else round(pnl / staked, 4),
        "note": ("CLV and ROI are reported without fees, matching the price basis the user actually sees. "
                 "Fee-aware analysis is separate."),
    }


def _forecasters(resolved):
    model, market, hand = [], [], []
    for r, e in resolved:
        y = _realised(r, e)
        side = r.get("side", "YES")
        model.append((_side_prob(r.get("model_probability"), side), y))
        market.append((_side_prob(r.get("mid"), side), y))
        hand.append((_side_prob(r.get("probability_mid"), side), y))
    return {
        "model": _forecast_metrics(model),
        "market": _forecast_metrics(market),
        "chatgpt_handicap": _forecast_metrics(hand),
        "interpretation": ("Lower Brier and log loss are better. The market is the benchmark: the experiment "
                           "succeeds only if the handicap layer beats BOTH the model and the market on the "
                           "same contracts."),
    }


def _breakdowns(resolved, ex_by_rec):
    def bucket(fn):
        groups = defaultdict(list)
        for r, e in resolved:
            k = fn(r, e)
            if k is not None:
                groups[str(k)].append((r, e))
        return {k: _headline(v, ex_by_rec) for k, v in sorted(groups.items())}

    def mtk(r, _):
        m = r.get("minutes_to_kickoff")
        if m is None:
            return None
        for lim, lab in ((60, "T-60m or less"), (180, "T-3h"), (720, "T-12h"), (1440, "T-24h"),
                         (4320, "T-72h")):
            if m <= lim:
                return lab
        return "more than T-72h"

    def price_bucket(r, _):
        side = r.get("side", "YES")
        p = r.get("yes_ask") if side == "YES" else r.get("no_ask")
        if p is None:
            return None
        for lim in (0.10, 0.20, 0.35, 0.50, 0.65, 0.80, 0.90):
            if p < lim:
                return f"<{lim:.2f}"
        return ">=0.90"

    def agreement(r, _):
        m, k = r.get("model_probability"), r.get("mid")
        if m is None or k is None:
            return None
        d = m - k
        return "model above market" if d > 0.02 else ("model below market" if d < -0.02 else "model agrees")

    def driver(r, _):
        tags = set(r.get("reasoning_tags") or [])
        if tags & {"INJURY_REPLACEMENT", "QB_CHANGE", "OL_INJURY"}:
            return "injury-driven"
        if tags & {"ROLE_EXPANSION", "ROLE_CONTRACTION"}:
            return "role-driven"
        if tags & {"WEATHER_WIND", "WEATHER_PRECIP"}:
            return "weather-driven"
        return "other"

    def market_type(r, _):
        fam = r.get("market_family") or ""
        return "player" if fam in ("PLAYER_STAT", "FIRST_TD_SCORER", "ANYTIME_TD") else "game"

    return {
        "by_grade": bucket(lambda r, e: r.get("grade")),
        "by_market_family": bucket(lambda r, e: r.get("market_family")),
        "by_player_statistic": bucket(lambda r, e: r.get("threshold") is not None and
                                      (r.get("market_family") == "PLAYER_STAT") and r.get("player_name") and
                                      (r.get("market_ticker") or "").split("-")[0]),
        "by_reasoning_tag": _by_tag(resolved, ex_by_rec),
        "by_time_to_kickoff": bucket(mtk),
        "by_price_bucket": bucket(price_bucket),
        "by_model_agreement": bucket(agreement),
        "by_driver": bucket(driver),
        "by_market_type": bucket(market_type),
        "by_calibration_bucket": bucket(lambda r, e: e.get("calibration_bucket")),
    }


def _by_tag(resolved, ex_by_rec):
    groups = defaultdict(list)
    for r, e in resolved:
        for t in (r.get("reasoning_tags") or ["<untagged>"]):
            groups[t].append((r, e))
    return {k: _headline(v, ex_by_rec) for k, v in sorted(groups.items())}


def _rec_vs_pass(resolved):
    """The comparison that decides whether the handicapper's judgement adds anything."""
    out = {}
    for decision in ("RECOMMENDED", "PASS", "WATCHLIST"):
        grp = [(r, e) for r, e in resolved if r.get("decision") == decision]
        if not grp:
            out[decision] = {"n": 0}
            continue
        clv = [e.get("clv") for _, e in grp if e.get("clv") is not None]
        wins = sum(1 for _, e in grp if e.get("outcome") == "WIN")
        out[decision] = {
            "n": len(grp),
            "win_rate": round(wins / len(grp), 4),
            "mean_clv": None if not clv else round(sum(clv) / len(clv), 5),
        }
    out["interpretation"] = (
        "If PASS records show CLV as good as RECOMMENDED ones, the handicap layer is not selecting -- it is "
        "labelling. That is the null hypothesis this ledger is built to reject or confirm.")
    return out
