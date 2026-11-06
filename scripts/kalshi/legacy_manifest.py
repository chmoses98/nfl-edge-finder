#!/usr/bin/env python3
"""Immutable baseline of the LEGACY trade tapes (``trades/<SERIES>/<TICKER>.jsonl``): exact line count, bytes, sha256, oldest/newest print, whether a legacy
candle file exists.  ``capped`` = exactly the collector's 10,000-print cap (``lines >= 10000``).  Used (a) to prioritise recovery of capped tapes and (b) as the
"before" side of the coverage report without downloading the ~52 GB branch on every run.  Read-only on the inputs; writes one JSON file.

usage: legacy_manifest.py --backfill data/kalshi/backfill --out legacy_manifest.json"""
from __future__ import annotations
import argparse, glob, hashlib, json, os, re
from datetime import datetime, timezone

CAP = 10000


_CT = re.compile(rb'"created_time"\s*:\s*"([^"]+)"')


def scan(path):
    h, n, lo, hi = hashlib.sha256(), 0, None, None
    with open(path, "rb") as f:
        for line in f:
            h.update(line); n += 1
            m = _CT.search(line)
            if m:
                t = m.group(1).decode()
                lo = t if lo is None or t < lo else lo
                hi = t if hi is None or t > hi else hi
    return dict(lines=n, bytes=os.path.getsize(path), sha256=h.hexdigest(), oldest_created=lo, newest_created=hi)


def build(backfill):
    out = {}
    for p in sorted(glob.glob(os.path.join(backfill, "trades", "*", "*.jsonl"))):
        s, t = os.path.basename(os.path.dirname(p)), os.path.basename(p)[:-6]
        e = scan(p)
        e.update(series=s, capped=e["lines"] >= CAP, empty=e["lines"] == 0, has_candles=os.path.exists(os.path.join(backfill, "candles", s, t + ".json")))
        out[t] = e
    return dict(version="nfl-legacy-tape-manifest/1", cap=CAP, built_at=datetime.now(timezone.utc).isoformat(), tickers=out,
                totals=dict(files=len(out), capped=sum(e["capped"] for e in out.values()), empty=sum(e["empty"] for e in out.values()),
                            size_band_ge_2_9MB=sum(e["bytes"] >= 2_900_000 for e in out.values())))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--backfill", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    m = build(a.backfill)
    json.dump(m, open(a.out, "w"), separators=(",", ":"), sort_keys=True)
    print(json.dumps(m["totals"]))


if __name__ == "__main__":
    main()
