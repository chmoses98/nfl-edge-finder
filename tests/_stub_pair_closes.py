"""Stand-in for scripts/shadow_v2/pair_closes_v2.py used by tests/test_closes_recovery.py (argument- and file-compatible).

STUB_MODE: ok (default) | proxy_as_true (a 5 h old quote tiered EXCELLENT) | fail_after_1 (exit 3 after the first game)
STUB_QUALITY: comma list of tiers cycled over the rows, default EXCELLENT,GOOD,STALE,MISSING
"""
import argparse
import gzip
import json
import os
import sys

ap = argparse.ArgumentParser()
ap.add_argument("--market-data")
ap.add_argument("--out")
ap.add_argument("--game", action="append", default=[])
ap.add_argument("--summary-json", default="")
ap.add_argument("--now")
ap.add_argument("--dry-run", action="store_true")
ap.add_argument("--no-season-pass", action="store_true")
ap.add_argument("--time-budget-minutes", default="0")
a = ap.parse_args()
mode = os.environ.get("STUB_MODE", "ok")
tiers = os.environ.get("STUB_QUALITY", "EXCELLENT,GOOD,STALE,MISSING").split(",")
AGE = {"EXCELLENT": 300.0, "GOOD": 3000.0, "STALE": 20000.0, "MISSING": None}
if mode == "proxy_as_true":
    tiers, AGE = ["EXCELLENT"], {"EXCELLENT": 18000.0}
paired, missing = [], []
for n, gid in enumerate(a.game):
    if gid.endswith("_NOP"):
        missing.append(gid)
        continue
    if mode == "fail_after_1" and n >= 1:
        sys.exit(3)
    rows = []
    for i in range(8):
        q = tiers[i % len(tiers)]
        age = AGE[q]
        r = {"game_id": gid, "ticker": f"{gid}-T{i % 4}", "close_quality": q, "close_age_seconds": age,
             "close_status": "CLV_CLOSE_MISSING" if q == "MISSING" else "CLOSE_OK", "prediction_id": f"{gid}-{i}"}
        if q != "MISSING":
            r.update(close_id=f"c{gid}{i % 4}", yes_bid=0.4, yes_ask=0.5)
        rows.append(r)
    if not a.dry_run:
        for sub, suf in (("closes", "closes_v2"), ("clv", "clv_v2")):
            d = os.path.join(a.out, sub, gid)
            os.makedirs(d, exist_ok=True)
            stem = f"close-2.1.0.{a.now[:19].replace('-', '').replace(':', '')}Z"
            with gzip.GzipFile(os.path.join(d, f"{stem}.{suf}.jsonl.gz"), "wb", mtime=0) as g:
                for r in rows:
                    g.write((json.dumps(r, sort_keys=True) + "\n").encode())
        idx = os.path.join(a.out, "projection_index", "2026-10-01")
        os.makedirs(idx, exist_ok=True)
        with open(os.path.join(idx, "idx.json"), "w") as f:
            f.write("{}")
    print(f"  {gid}: {len(rows)} records, closes {len(rows)} (new {len(rows)}, unchanged 0)", flush=True)
    paired.append({"game_id": gid, "records": len(rows), "closes": len(rows), "first_file_day": "2026-09-30",
                   "tickers_by_quality": {t: 1 for t in set(tiers)}})
if a.summary_json:
    json.dump({"games_paired": paired, "games_without_kickoff": missing}, open(a.summary_json, "w"))
