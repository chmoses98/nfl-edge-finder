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
from nfl_edge.shadow_v2 import pit


def latest_discovery_dir(market_data: str, *, cutoff=None) -> str | None:
    """The newest discovery run at or before the cutoff.

    Discovery supplies strike_type / custom_strike / rules text to the semantics engine, so a discovery run
    taken AFTER the snapshot can resolve a question the snapshot itself could not -- flipping support_state on
    a record that is supposed to describe an earlier instant. Mostly static data, but "mostly" is not a cutoff.
    """
    ds = [d for d in glob.glob(os.path.join(market_data, "data", "kalshi", "discovery", "*"))
          if os.path.isfile(os.path.join(d, "summary.json"))]
    if cutoff is None:
        return sorted(ds)[-1] if ds else None
    best, _v = pit.pick_at_or_before(ds, cutoff, vintage=lambda d: pit.as_utc(os.path.basename(d.rstrip("/"))))
    return best


def load_latest_quotes(capture_root: str, *, snapshot_id: str | None = None):
    """Latest quote row per ticker at or before the chosen snapshot; series confirmed complete in that run.

    Bounded on BOTH axes, because either one alone leaks. A capture run's id is its START and the snapshot is
    a run's FINISH, so a run whose id sorts before the snapshot can still be writing rows after it: file-level
    bounding admits those rows. And a run in flight has written its quote file but not yet its manifest, so on
    an unbounded path `reversed(files)` prefers exactly the file whose rows post-date the cutoff the record
    then declares. Rows are therefore filtered by their own `observed_at`, and a row without one is refused.
    """
    mans = sorted(glob.glob(os.path.join(capture_root, "*", "*.manifest.json")))
    if not mans:
        return {}, None, {}, set(), None
    if snapshot_id:
        picked = [m for m in mans if os.path.basename(m).startswith(snapshot_id)]
        if not picked:
            raise FileNotFoundError(f"no capture manifest for snapshot {snapshot_id}")
        man = json.load(open(picked[-1]))
    else:
        man = json.load(open(mans[-1]))
    run_ts = datetime.fromisoformat(man["finished_at"])
    cutoff = pit.as_utc(run_ts)
    confirmed = {s for s, v in (man.get("series") or {}).items() if isinstance(v, dict) and v.get("complete")}
    # files whose run id is at or before the cutoff; then every row re-checked on its own instant
    files = pit.files_at_or_before(os.path.join(capture_root, "*", "*.quotes.jsonl"), cutoff)
    quotes = {}
    for f in reversed(files):
        for line in open(f):
            r = json.loads(line)
            if not pit.row_at_or_before(r, cutoff):
                continue
            t = r["ticker"]
            if t not in quotes:
                quotes[t] = r
    ages = {t: (run_ts - datetime.fromisoformat(r["observed_at"])).total_seconds() / 60.0 for t, r in quotes.items()}
    return quotes, run_ts, ages, confirmed, man


def load_books(capture_root: str, *, snapshot_id: str | None = None, cutoff=None, kickoffs: dict | None = None) -> dict:
    """Latest order book per ticker at or before the cutoff, and strictly before its game's kickoff.

    Two separate guards, because they defend against two different things.

    The CUTOFF guard keeps a book observed after the projection instant out of a frozen record. It is applied
    to the row's own `observed_at`, not to the file name -- the previous version claimed row-level bounding in
    its docstring and implemented run-id bounding in its body, which is the narrower check: a run's id is its
    start, so a straddling run passed both filters and contributed rows observed after the snapshot.

    The KICKOFF guard defends against a defect in the corpus itself. The incumbent capture decides `pregame`
    when it builds its candidate list and fetches books minutes later, so `books.jsonl` provably contains rows
    observed after kickoff -- 646 of 677,253 measured, worst 3.9 minutes past. Trusting the filename inherits
    that; checking the row does not. `kickoffs` maps ticker -> kickoff instant; tickers absent from it are
    subject only to the cutoff.
    """
    cut = pit.as_utc(cutoff) or pit.as_utc(snapshot_id)
    books, best = {}, {}
    for f in pit.files_at_or_before(os.path.join(capture_root, "*", "*.books.jsonl"), cut):
        for line in open(f):
            r = json.loads(line)
            if not pit.row_at_or_before(r, cut):
                continue
            ko = (kickoffs or {}).get(r.get("ticker"))
            if ko is not None and not pit.strictly_before_kickoff(r, ko):
                continue                                   # observed at or after kickoff: never pregame depth
            v = pit.as_utc(r.get("observed_at"))
            t = r["ticker"]
            if t not in best or v > best[t]:
                best[t], books[t] = v, r
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
