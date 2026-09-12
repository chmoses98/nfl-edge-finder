"""EXECUTABLE SIZE: what the book would actually have filled, and what that would have cost.

A 1.2-point edge on a top-of-book quote means nothing if only four contracts were resting there. Every
statistical result in this system is computed on ONE price per contract -- the best ask -- and that price is a
claim about the first contract only. This module turns a captured order book into the thing the profitability
question actually needs: for a hypothetical 1 / 5 / 10 / 25 / 50 / 100 contracts, what the volume-weighted entry
would have been, what the worst fill was, what the exchange's own fee arithmetic charges on those exact fills,
and what is left of the modelled edge afterwards.

Three rules hold everywhere here, and the tests exist mostly to defend them:

    NO BOOK, NO NUMBER.     A missing book yields DEPTH_NOT_CAPTURED with a reason and every numeric field
                            None. It never yields an estimate, never extrapolates the top level down the
                            ladder, and never assumes the quoted size repeats. A depth record that is absent
                            must be distinguishable from a market that was absent.
    PARTIAL FILLS ARE SAID SO. If the book holds 37 contracts and the question asked for 100, the row reports
                            37 filled, the shortfall, and PARTIAL -- it does not price 100.
    CLV IS NOT TOUCHED.     Canonical top-of-book CLV keeps its definition and its sign convention exactly
                            (nfl_edge/evaluation/clv.py). Size-adjusted execution lives in its own block and is
                            never allowed to overwrite it; the two answer different questions and the research
                            needs both side by side.

Fees are the exchange's real per-fill quadratic, carried across the fills of one order through
`nfl_edge.execution.fees.net_executable_ev(..., fills=...)`, so a 100-contract walk is not charged as if it were
a hundred separate one-contract orders. An unknown fee stays unknown and never becomes zero.

Version: depth-research-1.0.0.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone

from nfl_edge.execution import depth as D

DEPTH_VERSION = "depth-research-1.0.0"
SIZES = (1, 5, 10, 25, 50, 100)

DEPTH_CAPTURED = "DEPTH_CAPTURED"
DEPTH_NOT_CAPTURED = "DEPTH_NOT_CAPTURED"
DEPTH_EMPTY_SIDE = "DEPTH_EMPTY_SIDE"
DEPTH_STALE = "DEPTH_STALE"
FILLED, PARTIAL, UNFILLED = "FILLED", "PARTIAL", "UNFILLED"

DEFAULT_MAX_AGE_MIN = 30.0        # a book older than this is preserved and labelled, never silently used as current

# why a contract has no depth record. Recorded on the projection so research can condition on it.
NOT_CAPTURED_REASONS = {
    "NO_BOOK_IN_WINDOW": "no order book was captured for this ticker at or before the horizon",
    "SERIES_TIER_NOT_FULL": "the series is not captured at FULL_MICROSTRUCTURE tier, which is the only tier books are fetched for",
    "OUTSIDE_BOOK_WINDOW": "the game was outside the book capture window when the horizon was taken",
    "DROPPED_BY_BUDGET": "the ticker lost the deterministic book priority under the per-run cap",
    "NOT_PROBABILITY_CARRYING": "no model probability, so no execution question to ask",
}


def _f(x):
    try:
        return None if x in (None, "") else float(x)
    except (TypeError, ValueError):
        return None


def _dt(s):
    if not s:
        return None
    if isinstance(s, datetime):
        return s if s.tzinfo else s.replace(tzinfo=timezone.utc)
    d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def ladder(orderbook_fp: dict, side: str) -> list:
    """Ascending (price, size) the buyer of `side` would consume. Delegates to the verified reconstruction."""
    return D.ask_ladder(orderbook_fp or {}, side)


def ladder_summary(orderbook_fp: dict, side: str) -> dict:
    lad = ladder(orderbook_fp, side)
    if not lad:
        return {"levels": 0, "top_price": None, "top_size": None, "contracts_available": 0.0, "notional_available": 0.0}
    return {"levels": len(lad), "top_price": lad[0][0], "top_size": lad[0][1],
            "contracts_available": round(sum(s for _, s in lad), 4),
            "notional_available": round(sum(p * s for p, s in lad), 4)}


def walk_contracts(lad: list, n: float) -> dict:
    """Consume `n` contracts from the cheapest level up. Reports a shortfall rather than inventing liquidity."""
    want, got, cost, fills = float(n), 0.0, 0.0, []
    for price, size in lad:
        if got >= want:
            break
        take = min(size, want - got)
        if take <= 0:
            continue
        fills.append((price, round(take, 6)))
        got += take
        cost += price * take
    state = FILLED if got >= want - 1e-9 else (PARTIAL if got > 0 else UNFILLED)
    return {"requested": want, "filled": round(got, 6), "shortfall": round(max(0.0, want - got), 6),
            "fill_state": state, "levels_consumed": len(fills), "fills": fills,
            "cost_dollars": round(cost, 6) if fills else None,
            "vwap": round(cost / got, 6) if got > 0 else None,
            "worst_price": fills[-1][0] if fills else None,
            "top_price": lad[0][0] if lad else None,
            "slippage_vs_top": round(fills[-1][0] - lad[0][0], 6) if fills else None}


def execution_row(lad: list, n: float, *, fair=None, schedule=None, series_ticker=None, as_of=None) -> dict:
    """One hypothetical size: what it fills, what it costs, what the fee is, what edge survives."""
    w = walk_contracts(lad, n)
    row = {"size": n, **{k: w[k] for k in ("filled", "shortfall", "fill_state", "levels_consumed", "vwap",
                                           "worst_price", "cost_dollars", "slippage_vs_top")},
           "fee_dollars": None, "fee_state": "UNKNOWN", "net_ev_dollars": None, "net_edge_per_contract": None,
           "break_even_probability": None}
    if w["fill_state"] == UNFILLED or w["vwap"] is None:
        row["fee_state"] = "NOT_APPLICABLE"
        return row
    if schedule is None:
        row["fee_state"] = "UNKNOWN"
        row["fee_reason"] = "no fee schedule supplied"
        return row
    try:
        from nfl_edge.execution import fees as F
        q = F.net_executable_ev(fair if fair is not None else w["vwap"], w["vwap"], w["filled"], schedule,
                                series_ticker=series_ticker, as_of=as_of, fills=w["fills"])
        row["fee_state"] = q.state if not q.is_known else "KNOWN"
        if q.estimated_fees is not None:
            row["fee_dollars"] = round(float(q.estimated_fees), 6)
            # what the position must be worth per contract just to come out flat on cost plus fee
            row["break_even_probability"] = round(w["vwap"] + float(q.estimated_fees) / max(w["filled"], 1e-9), 6)
        if q.is_known and fair is not None:
            row["net_ev_dollars"] = round(float(q.net_ev_dollars), 6)
            row["net_edge_per_contract"] = round(float(q.net_ev_dollars) / max(w["filled"], 1e-9), 6)
        if not q.is_known:
            row["fee_reason"] = q.reason
    except Exception as exc:                                     # noqa: BLE001 -- a fee failure is never a number
        row["fee_state"], row["fee_reason"] = "UNKNOWN", f"{type(exc).__name__}: {str(exc)[:100]}"
    return row


def execution_table(book_row: dict | None, side: str, *, fair=None, schedule=None, series_ticker=None,
                    as_of=None, sizes=SIZES, max_age_minutes: float = DEFAULT_MAX_AGE_MIN,
                    not_captured_reason: str | None = None) -> dict:
    """The whole size ladder for one contract and one side, or an explicit refusal with its reason."""
    base = {"depth_version": DEPTH_VERSION, "side": side, "sizes": list(sizes), "rows": [],
            "book_observed_at": None, "book_age_minutes": None, "book_run_id": None}
    if not book_row or not (book_row.get("orderbook_fp") or {}):
        why = not_captured_reason or "NO_BOOK_IN_WINDOW"
        return {**base, "state": DEPTH_NOT_CAPTURED, "reason": NOT_CAPTURED_REASONS.get(why, why), "reason_code": why}
    obs = _dt(book_row.get("observed_at"))
    ref = _dt(as_of)
    age = ((ref - obs).total_seconds() / 60.0) if (obs and ref) else None
    base.update(book_observed_at=obs.isoformat() if obs else None, book_age_minutes=round(age, 3) if age is not None else None,
                book_run_id=book_row.get("run_id"))
    lad = ladder(book_row.get("orderbook_fp"), side)
    summ = ladder_summary(book_row.get("orderbook_fp"), side)
    if not lad:
        return {**base, "state": DEPTH_EMPTY_SIDE, "reason": f"the book carries no resting size a buyer of {side} could take",
                "reason_code": "DEPTH_EMPTY_SIDE", "ladder": summ}
    state = DEPTH_CAPTURED
    reason = None
    if age is not None and age > max_age_minutes:
        state, reason = DEPTH_STALE, f"book is {age:.1f} minutes older than the horizon (ceiling {max_age_minutes:g})"
    rows = [execution_row(lad, n, fair=fair, schedule=schedule, series_ticker=series_ticker, as_of=as_of) for n in sizes]
    return {**base, "state": state, "reason": reason, "reason_code": None, "ladder": summ, "rows": rows,
            "contracts_available": summ["contracts_available"],
            "size_to_exhaust_edge": _size_to_exhaust(rows)}


def _size_to_exhaust(rows) -> float | None:
    """The largest hypothetical size whose net edge is still positive -- None when no row has a known net edge."""
    best = None
    for r in rows:
        if r.get("net_edge_per_contract") is not None and r["net_edge_per_contract"] > 0 and r["fill_state"] == FILLED:
            best = r["size"]
    return best


def compact(table: dict, *, keep=(1, 10, 50)) -> dict:
    """The block frozen onto a projection record: enough to reconstruct from, small enough to carry per contract."""
    if not table or table.get("state") in (None, DEPTH_NOT_CAPTURED):
        return {"state": DEPTH_NOT_CAPTURED, "reason_code": (table or {}).get("reason_code"), "reason": (table or {}).get("reason"),
                "depth_version": DEPTH_VERSION}
    rows = {str(r["size"]): {"vwap": r["vwap"], "filled": r["filled"], "fill_state": r["fill_state"],
                             "net_edge_per_contract": r.get("net_edge_per_contract")}
            for r in (table.get("rows") or []) if r["size"] in keep}
    lad = table.get("ladder") or {}
    return {"state": table.get("state"), "depth_version": DEPTH_VERSION, "side": table.get("side"),
            "book_run_id": table.get("book_run_id"), "book_observed_at": table.get("book_observed_at"),
            "book_age_minutes": table.get("book_age_minutes"), "levels": lad.get("levels"),
            "top_size": lad.get("top_size"), "contracts_available": lad.get("contracts_available"),
            "size_to_exhaust_edge": table.get("size_to_exhaust_edge"), "sizes": rows}


def record_block(table: dict) -> dict:
    """The smallest honest depth summary to carry on every projection record.

    The book itself is already persisted by the capture, and the full size table is derived and rebuildable, so
    what has to travel with a frozen record is only what pins WHICH book was used and how deep it was. A record
    with no depth still carries the reason -- that is the field that stops `absent` from being read as `thin`.
    """
    if not table or table.get("state") in (None, DEPTH_NOT_CAPTURED):
        return {"state": DEPTH_NOT_CAPTURED, "why": (table or {}).get("reason_code") or "NO_BOOK_IN_WINDOW"}
    lad = table.get("ladder") or {}
    rows = {r["size"]: r for r in (table.get("rows") or [])}
    out = {"state": table.get("state"), "side": table.get("side"), "run": table.get("book_run_id"),
           "age_min": table.get("book_age_minutes"),
           "levels": lad.get("levels"), "top_size": lad.get("top_size"), "avail": lad.get("contracts_available")}
    for n in (1, 10, 50):
        r = rows.get(n)
        if r:
            out[f"vwap{n}"] = r.get("vwap")
            if r.get("fill_state") != FILLED:
                out[f"fill{n}"] = r.get("fill_state")
    if table.get("size_to_exhaust_edge") is not None:
        out["edge_size"] = table["size_to_exhaust_edge"]
    return out


# ---------------------------------------------------------------------------------------------- pairing
DEPTH_PAIR_VERSION = "depth-pair-1.0.0"


class DepthIndex:
    """Full-book observations from the dedicated depth sweep, indexed per ticker and ordered by observation.

    The sweep runs on its own cadence, so its rows are not aligned to any projection. Pairing is therefore a
    SELECTION, made under two rules that cannot be relaxed:

        observed_at <= projection.data_cutoff    a book observed after the projection was frozen describes a
                                                 market the projection could not have traded against. It may be
                                                 kept for market-path research, but it can never describe that
                                                 projection's entry executability.
        observed_at <  kickoff                   nothing observed after the game started is pregame evidence.

    The latest observation satisfying both is chosen, and its exact age and horizon quality travel with it. The
    frozen projection record is never mutated: pairing happens in the research export, which is derived and
    rebuildable, so a change of pairing rule can never rewrite what was observed.
    """

    def __init__(self, roots=()):
        import glob as _glob
        import gzip as _gzip
        import json as _json
        self.by_ticker: dict = {}
        self.n_rows = 0
        for root in roots:
            for p in sorted(_glob.glob(os.path.join(root, "*", "*.depth.jsonl.gz"))):
                try:
                    with _gzip.open(p, "rt") as fh:
                        for line in fh:
                            r = _json.loads(line)
                            t = r.get("ticker")
                            if not t or not r.get("orderbook_fp"):
                                continue
                            self.by_ticker.setdefault(t, []).append(r)
                            self.n_rows += 1
                except (OSError, ValueError):
                    continue
        for t in self.by_ticker:
            self.by_ticker[t].sort(key=lambda r: str(r.get("observed_at") or ""))

    def pair(self, ticker: str, *, cutoff, kickoff=None) -> tuple[dict | None, str]:
        """The latest full book this projection could legitimately have seen, or (None, reason)."""
        rows = self.by_ticker.get(ticker)
        if not rows:
            return None, "no full-book observation for this ticker"
        cut, ko = _dt(cutoff), _dt(kickoff)
        best = None
        for r in rows:
            v = _dt(r.get("observed_at"))
            if v is None:
                continue
            if cut is not None and v > cut:
                continue                                   # after the projection was frozen: never entry evidence
            if ko is not None and v >= ko:
                continue                                   # after kickoff: never pregame
            if best is None or v > _dt(best["observed_at"]):
                best = r
        if best is None:
            later = sum(1 for r in rows if _dt(r.get("observed_at")) and cut and _dt(r["observed_at"]) > cut)
            return None, (f"all {len(rows)} observation(s) fall after this projection's cutoff"
                          if later == len(rows) else "no observation at or before the cutoff and before kickoff")
        return best, "paired"


def pair_and_walk(index: "DepthIndex", rec: dict, *, fair=None, schedule=None, as_of=None, sizes=SIZES) -> dict:
    """Pair a frozen projection with the newest book it could have seen, then walk that book. Derived, not frozen."""
    cutoff = (((rec.get("lineage") or {}).get("point_in_time") or {}).get("data_cutoff")
              or rec.get("data_cutoff") or rec.get("observed_at"))
    row, why = index.pair(rec.get("ticker"), cutoff=cutoff, kickoff=rec.get("kickoff_utc"))
    if row is None:
        return {"state": DEPTH_NOT_CAPTURED, "reason": why, "reason_code": "NO_QUALIFYING_FULL_BOOK",
                "depth_pair_version": DEPTH_PAIR_VERSION}
    side = (rec.get("depth") or {}).get("side") or "YES"
    t = execution_table(row, side, fair=fair, schedule=schedule, series_ticker=rec.get("series_ticker"),
                        as_of=cutoff, sizes=sizes)
    age = None
    a, b = _dt(cutoff), _dt(row.get("observed_at"))
    if a and b:
        age = round((a - b).total_seconds() / 60.0, 3)
    return {**t, "depth_pair_version": DEPTH_PAIR_VERSION, "paired_observed_at": row.get("observed_at"),
            "paired_age_min": age, "paired_minutes_to_kickoff": row.get("minutes_to_kickoff"),
            "paired_target_horizon": row.get("target_horizon"), "paired_horizon_quality": row.get("horizon_quality"),
            "paired_ladder_complete": row.get("ladder_complete"), "paired_run_id": row.get("run_id")}


# ---------------------------------------------------------------------------------------------- CLV after depth
def clv_after_depth(entry_table: dict | None, close_table: dict | None, *, sizes=SIZES) -> dict:
    """Did the apparent move survive realistic size?

    Canonical CLV compares two top-of-book prices. This compares what it would have COST to buy the model's
    side at the horizon with what the same purchase would have cost at the close, for each hypothetical size.
    The sign convention is the canonical one and is not redefined here: POSITIVE means the market subsequently
    moved TOWARD the side the frozen model would have bought, i.e. the same purchase became more expensive.

    Both sides must be genuinely captured. A missing book on either end yields no number at all.
    """
    out = {"depth_version": DEPTH_VERSION, "state": None, "reason": None, "by_size": {}}
    e_ok = bool(entry_table) and entry_table.get("state") in (DEPTH_CAPTURED, DEPTH_STALE)
    c_ok = bool(close_table) and close_table.get("state") in (DEPTH_CAPTURED, DEPTH_STALE)
    if not (e_ok and c_ok):
        out["state"] = DEPTH_NOT_CAPTURED
        out["reason"] = ("no captured book at the horizon" if not e_ok else "") + \
                        ("; " if not e_ok and not c_ok else "") + ("no captured book at the close" if not c_ok else "")
        return out
    er = {r["size"]: r for r in (entry_table.get("rows") or [])}
    cr = {r["size"]: r for r in (close_table.get("rows") or [])}
    for n in sizes:
        a, b = er.get(n), cr.get(n)
        if not a or not b or a.get("vwap") is None or b.get("vwap") is None:
            out["by_size"][str(n)] = {"clv_exec_after_depth": None, "reason": "a side could not be filled at this size"}
            continue
        out["by_size"][str(n)] = {"clv_exec_after_depth": round(b["vwap"] - a["vwap"], 6),
                                  "entry_vwap": a["vwap"], "close_vwap": b["vwap"],
                                  "entry_fill_state": a["fill_state"], "close_fill_state": b["fill_state"]}
    out["state"] = DEPTH_CAPTURED
    return out
