#!/usr/bin/env python3
"""Auditable family-level coverage of the NFL backfill (#246).  Denominators are explicit and never mixed: UNIQUE CONTRACTS (tickers) != horizon rows != games.
usage: tape_coverage_report.py --backfill data/kalshi/backfill [--out report.json] [--md report.md]
Per series: archived contracts, settled (result join), horizon rows & rows with a two-sided pre-start quote (per horizon), detailed candles, legacy tape
(``trades/``: exactly 10,000 lines = CAPPED), recovered tape (``trades_v2/`` + ``tape_meta.jsonl`` status), hashes of every input file."""
from __future__ import annotations
import argparse, collections, glob, hashlib, json, os

HORIZONS = ["T-168h", "T-72h", "T-48h", "T-24h", "T-6h", "T-90m", "T-0"]
CAP = 10000


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()[:16]


def two_sided(sn):
    return bool(sn) and sn.get("bid") is not None and sn.get("ask") is not None and 0 < sn["bid"] < sn["ask"] < 1 and not sn.get("book_empty")


def nlines(p):
    with open(p, "rb") as f:
        return sum(1 for _ in f)


def report(backfill):
    out = dict(version="nfl-tape-coverage/1", backfill=os.path.basename(os.path.abspath(backfill)), series={}, inputs={})
    mk, settled, ids = {}, collections.Counter(), collections.defaultdict(set)
    for p in sorted(glob.glob(os.path.join(backfill, "markets", "*.jsonl"))):
        s = os.path.basename(p)[:-6]
        seen = set(); dup = 0; res = 0; tot = 0
        for l in open(p):
            m = json.loads(l); tot += 1
            if m["ticker"] in seen:
                dup += 1
            seen.add(m["ticker"]); res += m.get("result") in ("yes", "no")
        mk[s] = dict(contracts_listed=tot, unique_contracts=len(seen), duplicate_rows=dup, settled=res)
        ids[s] = seen
        out["inputs"][f"markets/{s}.jsonl"] = sha(p)
    hz = collections.defaultdict(dict)
    for p in sorted(glob.glob(os.path.join(backfill, "horizons", "[0-9]*.jsonl"))):
        out["inputs"][f"horizons/{os.path.basename(p)}"] = sha(p)
        for l in open(p):
            r = json.loads(l)
            hz[r["series"]][r["ticker"]] = r
    meta = {}
    mp = os.path.join(backfill, "tape_meta.jsonl")
    if os.path.exists(mp):
        for l in open(mp):
            r = json.loads(l); meta[r["ticker"]] = r        # last attempt per ticker wins
    for s in sorted(set(mk) | set(hz)):
        rows = hz.get(s, {})
        per_h = {h: sum(two_sided((r.get("snaps") or {}).get(h)) for r in rows.values()) for h in HORIZONS}
        anchored = [r for r in rows.values() if r.get("anchor_kind") == "kickoff"]
        legacy = sorted(glob.glob(os.path.join(backfill, "trades", s, "*.jsonl")))
        lc = [nlines(p) for p in legacy]
        v2 = [meta[t] for t in ids.get(s, ()) if t in meta]
        e = dict(**mk.get(s, {}), horizon_rows=len(rows), horizon_rows_with_any_two_sided_prestart_quote=sum(any(two_sided(x) for x in (r.get("snaps") or {}).values()) for r in rows.values()),
                 two_sided_prestart_quote_by_horizon=per_h, horizon_rows_anchored_to_kickoff=len(anchored), games_with_horizon_rows=len({r.get("game_id") for r in anchored if r.get("game_id")}),
                 candle_files=len(glob.glob(os.path.join(backfill, "candles", s, "*.json"))),
                 legacy_tape_files=len(legacy), legacy_tape_capped_at_10000=sum(c >= CAP for c in lc), legacy_tape_empty=sum(c == 0 for c in lc),
                 recovered_tape=dict(attempted=len(v2), status=dict(collections.Counter(x["status"] for x in v2)),
                                     anchor_kind=dict(collections.Counter(x.get("anchor_kind") for x in v2)),
                                     candle_verified=sum(bool((x.get("candle_check") or {}).get("verified")) for x in v2),
                                     with_source_gap=sum(bool(x.get("irrecoverable_window")) for x in v2),
                                     prints=sum(x.get("total_prints_on_disk", 0) for x in v2)))
        out["series"][s] = e
    tot = collections.Counter()
    for e in out["series"].values():
        for k in ("unique_contracts", "settled", "horizon_rows", "horizon_rows_with_any_two_sided_prestart_quote", "candle_files", "legacy_tape_files", "legacy_tape_capped_at_10000"):
            tot[k] += e.get(k, 0)
        tot["recovered_complete"] += e["recovered_tape"]["status"].get("COMPLETE", 0) + e["recovered_tape"]["status"].get("COMPLETE_WITH_SOURCE_GAP", 0)
    out["totals"] = dict(tot)
    return out


def md(rep):
    L = ["# NFL backfill coverage (unique contracts; not snapshots, not games)", "", "| series | contracts | settled | horizon rows | with 2-sided pre-start quote | T-24h quote | candle files | legacy tape (capped) | recovered tape complete/attempted |", "|---|---|---|---|---|---|---|---|---|"]
    for s, e in sorted(rep["series"].items(), key=lambda kv: -kv[1].get("settled", 0))[:40]:
        rt = e["recovered_tape"]; c = rt["status"].get("COMPLETE", 0) + rt["status"].get("COMPLETE_WITH_SOURCE_GAP", 0)
        L.append(f"| {s} | {e.get('unique_contracts', 0)} | {e.get('settled', 0)} | {e['horizon_rows']} | {e['horizon_rows_with_any_two_sided_prestart_quote']} | {e['two_sided_prestart_quote_by_horizon']['T-24h']} | {e['candle_files']} | {e['legacy_tape_files']} ({e['legacy_tape_capped_at_10000']}) | {c}/{rt['attempted']} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backfill", default="data/kalshi/backfill"); ap.add_argument("--out"); ap.add_argument("--md")
    a = ap.parse_args()
    rep = report(a.backfill)
    if a.out:
        json.dump(rep, open(a.out, "w"), indent=1, sort_keys=True)
    if a.md:
        open(a.md, "w").write(md(rep))
    print(json.dumps(rep["totals"]))


if __name__ == "__main__":
    main()
