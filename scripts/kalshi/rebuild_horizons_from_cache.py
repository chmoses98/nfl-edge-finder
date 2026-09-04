#!/usr/bin/env python3
"""Rebuild horizon quote snapshots from locally cached raw candles, no network.

An earlier pass cached full h60+m1 candle histories for the KXNFLGAME and KXNFLSPREAD series. Those files
hold real prices, so the fixed parser can reconstruct their horizon quotes immediately instead of waiting on
the network refetch. Market metadata (result, kickoff anchor, semantics) is joined in from an existing
horizon file, which was always correct -- only the prices were null.
"""
import argparse, glob, importlib.util, json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
spec = importlib.util.spec_from_file_location("bq", os.path.join(ROOT, "scripts", "kalshi", "backfill_quotes.py"))
bq = importlib.util.module_from_spec(spec); spec.loader.exec_module(bq)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candles", required=True)
    ap.add_argument("--meta", required=True, help="jsonl of horizon rows to take metadata from")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    meta = {}
    for line in open(a.meta):
        r = json.loads(line)
        meta[r["ticker"]] = r
    n = miss = quoted = 0
    with open(a.out, "w") as fout:
        for f in glob.glob(os.path.join(a.candles, "*", "*.json")):
            d = json.load(open(f))
            row = meta.get(d["ticker"])
            if not row:
                miss += 1
                continue
            cands = sorted((d.get("h60") or []) + (d.get("m1") or []), key=lambda x: x.get("end_period_ts") or 0)
            anchor = row["anchor_ts"]
            snaps = {}
            for name, mins in bq.HORIZONS:
                cut = anchor - mins * 60
                prior = [x for x in cands if (x.get("end_period_ts") or 0) <= cut]
                if not prior:
                    continue
                sn = bq.snapshot(prior[-1])
                if sn is None:
                    continue
                sn["age_min"] = round((cut - sn["ts"]) / 60.0, 1)
                snaps[name] = sn
            row = dict(row); row["snaps"] = snaps; row["n_candles"] = len(cands); row["source"] = "candle_cache"
            fout.write(json.dumps(row, separators=(",", ":")) + "\n")
            n += 1
            if any(v.get("bid") is not None for v in snaps.values()):
                quoted += 1
    print(json.dumps({"written": n, "with_quotes": quoted, "meta_missing": miss}))


if __name__ == "__main__":
    sys.exit(main())
