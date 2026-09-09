"""Read the captured quote history for one game, so a close can be CHOSEN rather than assumed.

The 2-hourly shadow ledger is not the right source for a closing price: its last snapshot before a game can be
two hours old. The 10-minutely Kalshi capture on `market-data` is, and it is already immutable. This module
reads it, and nothing else.

Two properties of the capture the reader must respect:

* **It is change-suppressed.** A market whose price did not move writes no row. So the newest row for a ticker
  is the last time the price MOVED, not the last time it was looked at. That makes the last pregame row the
  best available statement of the closing price, and it makes "minutes since the price changed" a real
  microstructure quantity rather than staleness. Both are recorded.
* **A row is only a close if it is complete.** A row with a missing yes_bid or yes_ask cannot produce a
  midpoint, and half a quote is not a close.

`observed_ts` is the epoch second of `observed_at`, added here so the close selector can compare against
kickoff without re-parsing timestamps for every candidate.
"""
from __future__ import annotations

import glob
import json
import os
from datetime import datetime, timedelta, timezone

# Fields lifted out of a capture row, with the dollar-string columns converted to floats.
_FLOAT_FIELDS = {
    "yes_bid": "yes_bid_dollars", "yes_ask": "yes_ask_dollars", "no_bid": "no_bid_dollars",
    "no_ask": "no_ask_dollars", "last_price": "last_price_dollars", "liquidity": "liquidity_dollars",
    "volume": "volume_fp", "open_interest": "open_interest_fp",
    "yes_bid_size": "yes_bid_size_fp", "yes_ask_size": "yes_ask_size_fp",
}


def _f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _ts(s):
    if not s:
        return None
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.timestamp()


def normalise_quote(row: dict) -> dict:
    q = {"ticker": row.get("ticker"), "run_id": row.get("run_id"), "observed_at": row.get("observed_at"),
         "observed_ts": _ts(row.get("observed_at")), "status": row.get("status"),
         "pregame": row.get("pregame"), "kickoff_utc": row.get("kickoff_utc"),
         "minutes_to_kickoff": row.get("minutes_to_kickoff"), "game_id": row.get("game_id")}
    for out, src in _FLOAT_FIELDS.items():
        q[out] = _f(row.get(src))
    q["mid"] = (q["yes_bid"] + q["yes_ask"]) / 2.0 if (q["yes_bid"] is not None and q["yes_ask"] is not None) else None
    q["quote_width"] = (q["yes_ask"] - q["yes_bid"]) if (q["yes_bid"] is not None and q["yes_ask"] is not None) else None
    return q


def capture_days(capture_root: str, kickoff_utc: str | None, days_back: int = 14) -> list:
    """Capture day directories that could hold a pregame quote for a game kicking off at `kickoff_utc`.

    Bounded on purpose: reading every capture day for every settled game would grow linearly with the season
    for no gain, because a quote after kickoff can never be a close and a quote from three weeks earlier
    cannot be the LAST one before it. Days are still read whole -- the bound is on which days, never on which
    rows within a day.
    """
    days = sorted(d for d in glob.glob(os.path.join(capture_root, "*")) if os.path.isdir(d))
    if not kickoff_utc:
        return days
    try:
        ko = datetime.fromisoformat(kickoff_utc)
    except ValueError:
        return days
    lo = (ko - timedelta(days=days_back)).date().isoformat()
    hi = ko.date().isoformat()          # the kickoff day itself; later days cannot hold a pregame quote
    return [d for d in days if lo <= os.path.basename(d) <= hi]


def load_game_quotes(capture_root: str, game_id: str, tickers=None, *, kickoff_utc: str | None = None,
                     days_back: int = 14) -> tuple[dict, dict]:
    """Every captured quote for one game, keyed by ticker and sorted oldest-first.

    Returns `(by_ticker, stats)`. The line-level prefilter matches the capture's own `game_id` field, so no
    ticker-naming convention is relied on and nothing is silently missed by a pattern that stopped matching.
    """
    want = set(tickers) if tickers else None
    # A cheap substring prefilter over raw lines, then the parsed field decides. The prefilter is the bare
    # game_id rather than a JSON fragment on purpose: a needle like '"game_id":"..."' silently matches nothing
    # the day the writer emits a space after the colon, and a filter that stops matching loses quotes without
    # any error at all.
    needle = game_id
    by_ticker: dict[str, list] = {}
    stats = {"files_read": 0, "rows_matched": 0, "days": []}
    for day in capture_days(capture_root, kickoff_utc, days_back):
        for path in sorted(glob.glob(os.path.join(day, "*.quotes.jsonl"))):
            stats["files_read"] += 1
            with open(path) as fh:
                for line in fh:
                    if needle not in line:
                        continue
                    row = json.loads(line)
                    if row.get("game_id") != game_id:
                        continue
                    t = row.get("ticker")
                    if want is not None and t not in want:
                        continue
                    by_ticker.setdefault(t, []).append(normalise_quote(row))
                    stats["rows_matched"] += 1
        stats["days"].append(os.path.basename(day))
    for t in by_ticker:
        by_ticker[t].sort(key=lambda q: (q["observed_ts"] is None, q["observed_ts"]))
    return by_ticker, stats


def load_kalshi_settlements(capture_root: str, game_id: str, tickers=None, *, kickoff_utc: str | None = None,
                            days_forward: int = 4) -> dict:
    """Kalshi's OWN recorded settlement per ticker, from post-game capture rows.

    The capture writes each market's `status` and `result` on every pass, so once Kalshi settles a market the
    next capture preserves it. That makes the exchange's actual payout available for free -- and it is worth
    having, because it is the only independent check on our reading of the rules.

    It is NEVER the settlement this project records. Two reasons, both observed in the 2025 archive: Kalshi
    settled four markets in a December sweep in ways that contradict the games' own final scores, and on
    2025-09-07 it paid the no-snap fair price to twelve players who had taken offensive snaps. A corpus that
    took Kalshi's word would have inherited those. So this is written to a separate cross-check artifact and
    disagreements are surfaced for a human.
    """
    want = set(tickers) if tickers else None
    needle = game_id                 # see load_game_quotes on why this is not a JSON fragment
    out: dict[str, dict] = {}
    if not kickoff_utc:
        return out
    try:
        ko = datetime.fromisoformat(kickoff_utc)
    except ValueError:
        return out
    lo, hi = ko.date().isoformat(), (ko + timedelta(days=days_forward)).date().isoformat()
    for day in sorted(glob.glob(os.path.join(capture_root, "*"))):
        if not (lo <= os.path.basename(day) <= hi):
            continue
        for path in sorted(glob.glob(os.path.join(day, "*.quotes.jsonl"))):
            with open(path) as fh:
                for line in fh:
                    if needle not in line:
                        continue
                    row = json.loads(line)
                    t = row.get("ticker")
                    if row.get("game_id") != game_id or (want is not None and t not in want):
                        continue
                    res = (row.get("result") or "").strip().lower()
                    if not res:
                        continue
                    ts = _ts(row.get("observed_at"))
                    prev = out.get(t)
                    if prev is None or (ts or 0) > (prev.get("observed_ts") or 0):
                        out[t] = {"ticker": t, "result": res, "status": row.get("status"),
                                  "observed_at": row.get("observed_at"), "observed_ts": ts,
                                  "last_price": _f(row.get("last_price_dollars"))}
    return out


def kalshi_yes_payout(row: dict):
    """Kalshi's recorded result as a YES payout, or None when it is not a payout we can read.

    `scalar` carries no value in the capture schema (only `result`), so it is reported as a scalar branch
    without a number rather than being invented.
    """
    res = (row or {}).get("result")
    if res == "yes":
        return 1.0, "binary"
    if res == "no":
        return 0.0, "binary"
    if res == "scalar":
        return None, "scalar"
    return None, res or "unknown"
