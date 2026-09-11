"""Read one capture snapshot the way the incumbent pricer does, plus the discovery record for static semantics.

The incumbent's loaders live inside `scripts/shadow/price_slate.py`, which is pinned; the same logic is repeated
here (not imported, so the frozen script is never executed by v2) with one addition: the discovery run's market
records, keyed by ticker, so the semantics engine can read strike_type / custom_strike / rules text for captures
written before capture-1.1.0 carried them.
"""
from __future__ import annotations

import glob
import json
import os
from datetime import datetime

from nfl_edge.board.drift import load_discovery


def latest_discovery_dir(market_data: str) -> str | None:
    ds = sorted(d for d in glob.glob(os.path.join(market_data, "data", "kalshi", "discovery", "*")) if os.path.isfile(os.path.join(d, "summary.json")))
    return ds[-1] if ds else None


def load_latest_quotes(capture_root: str, *, snapshot_id: str | None = None):
    """Latest quote row per ticker up to (and including) the chosen manifest; series confirmed complete in that run."""
    files = sorted(glob.glob(os.path.join(capture_root, "*", "*.quotes.jsonl")))
    mans = sorted(glob.glob(os.path.join(capture_root, "*", "*.manifest.json")))
    if not files or not mans:
        return {}, None, {}, set(), None
    if snapshot_id:
        mans = [m for m in mans if os.path.basename(m).startswith(snapshot_id)]
        if not mans:
            raise FileNotFoundError(f"no capture manifest for snapshot {snapshot_id}")
        files = [f for f in files if os.path.basename(f)[:16] <= snapshot_id]
    man = json.load(open(mans[-1]))
    run_ts = datetime.fromisoformat(man["finished_at"])
    confirmed = {s for s, v in (man.get("series") or {}).items() if isinstance(v, dict) and v.get("complete")}
    quotes = {}
    for f in reversed(files):
        for line in open(f):
            r = json.loads(line)
            t = r["ticker"]
            if t not in quotes:
                quotes[t] = r
    ages = {t: (run_ts - datetime.fromisoformat(r["observed_at"])).total_seconds() / 60.0 for t, r in quotes.items()}
    return quotes, run_ts, ages, confirmed, man


def load_books(capture_root: str) -> dict:
    books = {}
    for f in sorted(glob.glob(os.path.join(capture_root, "*", "*.books.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            books[r["ticker"]] = r
    return books


def discovery_markets_by_ticker(discovery_dir: str) -> dict:
    disc = load_discovery(discovery_dir)
    out = {}
    for st, mk in disc["markets"].items():
        for state in ("open", "closed", "settled"):
            for m in ((mk.get(state) or {}).get("markets") or []):
                out.setdefault(m.get("ticker"), m)
    return out


def static_market(q: dict, disc_markets: dict) -> dict:
    """The market dict the semantics engine reads: discovery record when known, else the capture row's own fields."""
    m = disc_markets.get(q["ticker"])
    if m is not None:
        return m
    return {"ticker": q["ticker"], "event_ticker": q.get("event_ticker"), "series_ticker": q.get("series_ticker"),
            "title": q.get("player_name") or "", "strike_type": q.get("strike_type"), "floor_strike": q.get("floor_strike"),
            "cap_strike": q.get("cap_strike"), "custom_strike": (json.loads(q["custom_strike"]) if isinstance(q.get("custom_strike"), str) and q["custom_strike"].startswith("{") else None),
            "rules_primary": ""}


def fnum(x):
    try:
        return None if x is None or x == "" else float(x)
    except (TypeError, ValueError):
        return None
