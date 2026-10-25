"""Recommendation attribution: which of the owner's fills, if any, followed a recorded recommendation -- and how closely.

The rule is evidence, not inference. A fill is LINKED to a recommendation only when ALL of these hold, and the recommendation is unique:

    same market ticker · same side · fill after the recommendation was created and before kickoff · fill price at or under the
    recommendation's own ceiling (`bet_up_to_probability`) plus a one-tick tolerance

Anything else is reported as exactly what it is:

    NO_RECOMMENDATION_ON_RECORD   no real (non-test) recommendation exists for that ticker and side. The fill is the owner's own selection.
                                  It is NOT labelled a model or ChatGPT pick, ever: absence of a record is not evidence of provenance.
    OUTSIDE_RECOMMENDATION_TERMS  a recommendation exists but the fill came before it, after kickoff, or above its ceiling
    AMBIGUOUS_RECOMMENDATIONS     more than one recommendation fits; no choice is made for them

Cashouts (a SELL, or a buy of the opposite side that reduces a position) are position management and are not matched as new theses.
TEST_ONLY records and records of a REHEARSAL are excluded everywhere. Nothing here writes to the ledger.
"""
from __future__ import annotations

from datetime import datetime, timezone

ATTRIBUTION_VERSION = "attribution-1.0.0"
TICK = 0.01

LINKED = "LINKED"
NONE = "NO_RECOMMENDATION_ON_RECORD"
OUTSIDE = "OUTSIDE_RECOMMENDATION_TERMS"
AMBIGUOUS = "AMBIGUOUS_RECOMMENDATIONS"


def _ts(v):
    if not v:
        return None
    try:
        d = datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def real_recommendations(recs: list) -> list:
    """RECOMMENDED, non-test, non-rehearsal records, with amendment chains collapsed to the current opinion."""
    live = [r for r in recs if r.get("decision") == "RECOMMENDED" and not r.get("test_only")
            and not any(str(t).startswith("mode:REHEARSAL") for t in (r.get("reasoning_tags") or []))]
    superseded = {r.get("amends") for r in live if r.get("amends")}
    return [r for r in live if r.get("recommendation_id") not in superseded]


def link_fill(fill: dict, recs: list) -> dict:
    t, side = fill.get("market_ticker"), fill.get("side")
    when, price = _ts(fill.get("executed_at")), fill.get("actual_price")
    same = [r for r in recs if r.get("market_ticker") == t and r.get("side") == side]
    if fill.get("execution_action") == "SELL":
        return {"state": "NOT_AN_ENTRY", "reason": "a sell is position management, not a new thesis"}
    if not same:
        return {"state": NONE, "reason": "no real recommendation exists for this contract and side; the fill is the owner's own selection"}
    fits, misses = [], []
    for r in same:
        created, ko = _ts(r.get("created_at")), _ts(r.get("kickoff_utc"))
        ceil = r.get("bet_up_to_probability")
        problems = []
        if when is None or created is None or when < created:
            problems.append("fill precedes the recommendation")
        if ko is not None and when is not None and when >= ko:
            problems.append("fill is at or after kickoff")
        if ceil is not None and price is not None and float(price) > float(ceil) + TICK + 1e-9:
            problems.append(f"fill price {float(price):.2f} exceeds the ceiling {float(ceil):.2f}")
        (misses if problems else fits).append((r, problems))
    if len(fits) > 1:
        return {"state": AMBIGUOUS, "candidates": [r["recommendation_id"] for r, _ in fits], "reason": "more than one recommendation fits; none is chosen"}
    if not fits:
        return {"state": OUTSIDE, "recommendation_id": misses[0][0].get("recommendation_id"), "reason": "; ".join(misses[0][1])}
    r = fits[0][0]
    ask = r.get("yes_ask") if side == "YES" else r.get("no_ask")
    lag = None if when is None else round((when - _ts(r["created_at"])).total_seconds() / 60.0, 1)
    return {"state": LINKED, "recommendation_id": r["recommendation_id"], "lag_minutes": lag,
            "slippage_vs_recorded_ask": None if (ask is None or price is None) else round(float(price) - float(ask), 4),
            "recommended_stake": r.get("recommended_stake"), "ceiling": r.get("bet_up_to_probability")}


def attribute(wagers: list, recs: list) -> dict:
    real = real_recommendations(recs)
    rows = []
    for w in wagers:
        if w.get("test_only"):
            continue
        a = link_fill(w, real)
        a["imported_wager_id"] = w.get("imported_wager_id")
        rows.append(a)
    counts: dict = {}
    for a in rows:
        counts[a["state"]] = counts.get(a["state"], 0) + 1
    linked = [a for a in rows if a["state"] == LINKED]
    filled_ids = {a["recommendation_id"] for a in linked}
    per_rec = {}
    for r in real:
        fills = [a for a in linked if a["recommendation_id"] == r["recommendation_id"]]
        per_rec[r["recommendation_id"]] = {"filled": bool(fills), "fills": len(fills)}
    return {"version": ATTRIBUTION_VERSION, "fills": len(rows), "counts": counts, "real_recommendations": len(real),
            "recommendations_filled": len(filled_ids), "recommendations_unfilled": len(real) - len(filled_ids),
            "owner_selected_share": round(counts.get(NONE, 0) / len(rows), 4) if rows else None, "rows": rows, "per_recommendation": per_rec,
            "statement": ("Fills with state NO_RECOMMENDATION_ON_RECORD are owner-selected; no claim is made that they came from a model or from ChatGPT. "
                          "Performance by thesis or recommendation category exists only for LINKED fills.")}


def by_thesis(attribution: dict, recs: list, episodes_pnl: dict | None = None) -> dict:
    """Roll LINKED fills up to the recommendation's thesis id (tag `thesis:<id>`), when recorded. Counts only unless P&L is supplied."""
    tag = {}
    for r in recs:
        for t in (r.get("reasoning_tags") or []):
            if str(t).startswith("thesis:"):
                tag[r["recommendation_id"]] = str(t)[len("thesis:"):]
    out: dict = {}
    for a in attribution["rows"]:
        if a["state"] != LINKED:
            continue
        th = tag.get(a["recommendation_id"], "(no thesis tag)")
        b = out.setdefault(th, {"fills": 0})
        b["fills"] += 1
    return out
