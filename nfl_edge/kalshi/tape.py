"""Trade-tape recovery with a TRUTHFUL completeness status (nfl-edge-finder #246).  Read-only; no order surface.

Root cause of the 10,000-print truncation (found by code audit, not assumed): ``scripts/kalshi/backfill.py`` called
``historical_trades(ticker, limit=1000, max_pages=10)``.  The cap is **self-imposed by the collector**, not an API limit, and the per-ticker
``complete`` flag it stored (``ok and not e1``) ignored it, so a capped tape was recorded as complete.  The API pages by ``cursor``, newest first.

This module pages until the cursor is exhausted (or a per-run page budget / error stops it), persists the cursor so the next run RESUMES backwards, and
returns an explicit stop reason.  ``tape_complete`` is True only when the cursor was exhausted with no error: never inferred from a count.
Pre-start only: callers pass ``max_ts`` (the anchor, i.e. kickoff), and every returned print is re-checked against it (no post-anchor lookahead).
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone

EXHAUSTED, PAGE_BUDGET, ERROR, EMPTY_PAGE = "CURSOR_EXHAUSTED", "PAGE_BUDGET", "ERROR", "EMPTY_PAGE_NO_CURSOR"


def to_ts(s) -> int | None:
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return int(s)
    return int(datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp())


@dataclass
class TapeResult:
    ticker: str
    n: int = 0
    pages: int = 0
    stop_reason: str = ""
    error: str | None = None
    cursor: str | None = None          # cursor to resume from (None when exhausted)
    oldest_ts: int | None = None
    newest_ts: int | None = None
    duplicates_dropped: int = 0
    post_anchor_dropped: int = 0
    out_of_order: int = 0
    anchor_ts: int | None = None
    market_open_ts: int | None = None
    tape_complete: bool = False
    unfetched_window: list | None = None       # [market_open, oldest fetched]: NOT yet covered (resumable); becomes a source gap only via final_status
    trades: list = field(default_factory=list)

    def meta(self) -> dict:
        d = asdict(self)
        d.pop("trades")
        return d


def fetch_tape(client, ticker: str, *, anchor_ts: int | None, market_open_ts: int | None = None, path: str = "historical/trades",
               resume_cursor: str | None = None, page_budget: int = 200, limit: int = 1000, known_ids: set | None = None) -> TapeResult:
    """Page trades newest->oldest.  ``anchor_ts`` (inclusive upper bound, e.g. kickoff) is sent as ``max_ts`` AND enforced client-side."""
    r = TapeResult(ticker=ticker, anchor_ts=anchor_ts, market_open_ts=market_open_ts)
    seen = set(known_ids or ())
    cursor = resume_cursor
    prev_ts = None
    while True:
        if r.pages >= page_budget:
            r.stop_reason, r.cursor = PAGE_BUDGET, cursor
            break
        params = {"ticker": ticker, "limit": limit, "max_ts": anchor_ts}
        if cursor:
            params["cursor"] = cursor
        body, err = client.try_get(path, params)
        if body is None:
            r.stop_reason, r.error, r.cursor = ERROR, err, cursor        # cursor of the page that FAILED: resume there, never skip it
            break
        r.pages += 1
        page = body.get("trades") or []
        for t in page:
            tid = t.get("trade_id")
            c = to_ts(t.get("created_time"))
            if tid in seen:
                r.duplicates_dropped += 1
                continue
            if anchor_ts is not None and c is not None and c > anchor_ts:
                r.post_anchor_dropped += 1          # defence against a server that ignores max_ts: never keep post-start prints
                continue
            if prev_ts is not None and c is not None and c > prev_ts + 1:
                r.out_of_order += 1                 # newest-first contract violated (reported, still kept)
            if c is not None:
                prev_ts = c if prev_ts is None else min(prev_ts, c)
                r.oldest_ts = c if r.oldest_ts is None else min(r.oldest_ts, c)
                r.newest_ts = c if r.newest_ts is None else max(r.newest_ts, c)
            seen.add(tid)
            r.trades.append(t)
        r.n = len(r.trades)
        cursor = body.get("cursor") or None
        if not cursor:
            r.stop_reason = EXHAUSTED if page else EMPTY_PAGE
            r.cursor = None
            break
    # complete only if the cursor ran out with no error; an empty first page with no cursor is a genuinely empty (but complete) tape
    r.tape_complete = r.stop_reason in (EXHAUSTED, EMPTY_PAGE)
    if not r.tape_complete and r.oldest_ts is not None and market_open_ts is not None and r.oldest_ts > market_open_ts:
        r.unfetched_window = [market_open_ts, r.oldest_ts]
    return r


def hourly_candle_vs_tape(candles_h60: list, trades: list, anchor_ts: int, tol: float = 0.5) -> dict:
    """Verify exchange hourly candles against the tape on hours that END before the anchor.  A candle period is compared only when the tape is complete;
    callers must not call this for a truncated tape.  Candle ``price.low/high`` (dollars) and ``volume`` must equal the tape's min/max/sum."""
    by = {}
    for t in trades:
        c = to_ts(t.get("created_time"))
        if c is None or c >= anchor_ts:
            continue
        end = (c // 3600 + 1) * 3600
        yes = round(float(t["yes_price_dollars"]) * 100)
        by.setdefault(end, []).append((yes, float(t["count_fp"])))
    checked = ok_low = ok_high = ok_vol = missing_candle = 0
    ends = {int(c["end_period_ts"]): c for c in candles_h60 or []}
    for end, L in by.items():
        if end > anchor_ts:
            continue
        c = ends.get(end)
        if c is None or (c.get("price") or {}).get("low") is None:
            missing_candle += 1
            continue
        checked += 1
        ok_low += round(float(c["price"]["low"]) * 100) == min(p for p, _ in L)
        ok_high += round(float(c["price"]["high"]) * 100) == max(p for p, _ in L)
        ok_vol += abs(float(c["volume"]) - sum(q for _, q in L)) <= tol
    # hours the exchange says traded (candle volume > 0) but for which the tape holds LESS volume: a recoverable-or-not gap, found independently of counts
    short = sorted(e for e, c in ends.items() if e <= anchor_ts and float(c.get("volume") or 0) > tol
                   and sum(q for _, q in by.get(e, [])) + tol < float(c.get("volume") or 0))
    pre_vol = sum(float(c.get("volume") or 0) for e, c in ends.items() if e <= anchor_ts)
    return dict(candles_returned=len(ends), candle_volume_pre_anchor=pre_vol, hours_with_prints=len(by), hours_checked=checked, low_ok=ok_low, high_ok=ok_high, volume_ok=ok_vol, hours_missing_candle=missing_candle,
                hours_candle_volume_not_in_tape=len(short), first_uncovered_hour_end=short[0] if short else None, last_uncovered_hour_end=short[-1] if short else None,
                verified=bool(checked) and checked == ok_low == ok_high == ok_vol and missing_candle == 0 and not short)


def final_status(r: TapeResult, verification: dict | None) -> dict:
    """Per-ticker audit row.  ``irrecoverable_window`` is set only when the cursor is EXHAUSTED (the source has nothing older) yet candles prove volume
    traded earlier: the source's retention, not our cap."""
    status = "COMPLETE" if r.tape_complete else ("INCOMPLETE_RESUMABLE" if r.stop_reason == PAGE_BUDGET else "INCOMPLETE_ERROR")
    irr = None
    if r.tape_complete and verification and verification.get("hours_candle_volume_not_in_tape"):
        irr = [verification["first_uncovered_hour_end"] - 3600, verification["last_uncovered_hour_end"]]
        status = "COMPLETE_WITH_SOURCE_GAP"
    return dict(**r.meta(), status=status, candle_check=verification, irrecoverable_window=irr)


# ------------------------------------------------------------------ persistence (append-only data, small resumable state)
def load_state(path: str) -> dict:
    return json.load(open(path)) if os.path.exists(path) else {"tickers": {}, "runs": []}


def save_state(path: str, state: dict) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, separators=(",", ":"))
    os.replace(tmp, path)


# ------------------------------------------------------------------ live-capture gap bookkeeping (scripts/kalshi/capture.py)
def plan_after_fetch(min_ts: int, fetched_ts: list, complete: bool, run_id: str):
    """Live capture pages newest-first with a small page cap.  If the cap is hit, the OLD cursor kept the same ``min_ts`` and every later run re-fetched the same
    newest prints, so the older ones in the window were never recovered (and nothing recorded that).  Returns (next_cursor, gap|None): the cursor always
    advances past what was seen, and the unseen older part is recorded as an explicit gap [from, to] to be filled later."""
    seen = [t for t in fetched_ts if t is not None]
    max_seen = max(seen) if seen else min_ts
    if complete:
        return max_seen + 1, None
    if not seen:
        return min_ts, None                       # nothing fetched at all (error): keep the cursor, nothing to bound a gap with
    return max_seen + 1, dict(**{"from": min_ts, "to": min(seen), "run_id": run_id})


def shrink_gap(gap: dict, fetched_ts: list, complete: bool):
    """Result of a gap-fill fetch with min_ts=gap.from, max_ts=gap.to (newest first).  None = gap closed; else the remaining older gap."""
    seen = [t for t in fetched_ts if t is not None]
    if complete or not seen:
        return None if complete else gap
    nxt = min(seen)
    return None if nxt <= gap["from"] else dict(gap, to=nxt)
