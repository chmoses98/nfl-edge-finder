"""Derived evaluation records: enrich a prediction with what the market did next, WITHOUT touching it.

The ledger is append-only and a written observation is immutable. Closing-line value, markouts and
settlement are therefore recorded as separate derived rows keyed by `prediction_id`, so a snapshot can be
re-evaluated as later quotes arrive while the original prediction stays exactly as it was made.

`MISSING_CLOSE` is a real, recorded outcome. A post-kickoff quote is never substituted for a pregame close.
"""
from __future__ import annotations

import gzip
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

MISSING_CLOSE = "MISSING_CLOSE"
CLOSE_MAX_STALENESS_S = 3600.0     # a "close" more than an hour before kickoff is reported, not silently used


@dataclass
class Evaluation:
    prediction_id: str
    run_id: str
    ticker: str
    model_version: str
    evaluated_at: str
    # state at prediction time, copied for self-containment
    model_p: float | None = None
    yes_bid_t: float | None = None
    yes_ask_t: float | None = None
    no_bid_t: float | None = None
    no_ask_t: float | None = None
    mid_t: float | None = None
    model_direction: str | None = None          # yes | no | none
    # later state
    close_mid: float | None = None
    close_yes_bid: float | None = None
    close_yes_ask: float | None = None
    close_observed_at: str | None = None
    close_minutes_to_kickoff: float | None = None
    close_status: str = MISSING_CLOSE
    # derived
    signed_clv_mid: float | None = None
    signed_clv_executable: float | None = None
    movement: str | None = None                 # toward | away | unchanged | no_view
    width_t: float | None = None
    width_close: float | None = None
    width_change: float | None = None
    liquidity_change: float | None = None
    settled_yes: float | None = None
    notes: str = ""

    def to_dict(self):
        return asdict(self)


def model_direction(model_p, mid, tol=1e-9):
    if model_p is None or mid is None:
        return "none"
    if abs(model_p - mid) <= tol:
        return "none"
    return "yes" if model_p > mid else "no"


def evaluate(pred: dict, close: dict | None, settled_yes: float | None = None) -> Evaluation:
    """Build the derived record. `pred` is a ledger row; `close` is the chosen pregame close, or None."""
    yb, ya = pred.get("yes_bid"), pred.get("yes_ask")
    mid = (yb + ya) / 2.0 if yb is not None and ya is not None else None
    p = pred.get("model_contract_value", pred.get("model_event_probability"))
    ev = Evaluation(
        prediction_id=pred["prediction_id"], run_id=pred.get("run_id"), ticker=pred.get("ticker"),
        model_version=pred.get("model_version"),
        evaluated_at=datetime.now(timezone.utc).isoformat(),
        model_p=p, yes_bid_t=yb, yes_ask_t=ya, no_bid_t=pred.get("no_bid"), no_ask_t=pred.get("no_ask"),
        mid_t=mid, model_direction=model_direction(p, mid),
        width_t=(ya - yb) if yb is not None and ya is not None else None,
        settled_yes=settled_yes)
    if not close:
        ev.notes = "no valid pregame close available"
        return ev
    cb, ca = close.get("yes_bid"), close.get("yes_ask")
    if cb is None or ca is None:
        ev.notes = "close quote incomplete"
        return ev
    ev.close_status = "OK"
    ev.close_yes_bid, ev.close_yes_ask = cb, ca
    ev.close_mid = (cb + ca) / 2.0
    ev.close_observed_at = close.get("observed_at")
    ev.close_minutes_to_kickoff = close.get("minutes_to_kickoff")
    ev.width_close = ca - cb
    if ev.width_t is not None:
        ev.width_change = ev.width_close - ev.width_t
    if close.get("liquidity") is not None and pred.get("liquidity") is not None:
        ev.liquidity_change = close["liquidity"] - pred["liquidity"]
    if mid is not None and p is not None:
        d = ev.close_mid - mid
        view = p - mid
        if abs(d) <= 1e-9:
            ev.movement = "unchanged"
        elif abs(view) <= 1e-9:
            ev.movement = "no_view"
        else:
            ev.movement = "toward" if (d > 0) == (view > 0) else "away"
        ev.signed_clv_mid = d * (1.0 if view > 0 else (-1.0 if view < 0 else 0.0))
        # executable CLV: we would have crossed at the ask (yes) or 1-bid (no); compare to the same side later
        if ev.model_direction == "yes" and ya is not None:
            ev.signed_clv_executable = ca - ya
        elif ev.model_direction == "no" and yb is not None:
            ev.signed_clv_executable = (1 - cb) - (1 - yb)
        else:
            ev.signed_clv_executable = 0.0
    return ev


def pick_close(quotes, kickoff_ts):
    """Strict pregame close: the latest complete valid quote strictly before kickoff.

    Never returns a post-kickoff quote. Returns None when no valid pregame quote exists, which the caller
    records as MISSING_CLOSE rather than filling in.
    """
    best = None
    for q in quotes:
        ts = q.get("observed_ts")
        if ts is None or kickoff_ts is None or ts >= kickoff_ts:
            continue
        if q.get("yes_bid") is None or q.get("yes_ask") is None:
            continue
        if best is None or ts > best["observed_ts"]:
            best = q
    return best


def write_evaluations(path, evals):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.open(path, "wt") as f:
        for e in evals:
            f.write(json.dumps(e.to_dict(), separators=(",", ":")) + "\n")
    return len(evals)
