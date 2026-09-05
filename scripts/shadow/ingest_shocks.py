#!/usr/bin/env python3
"""Persist timestamped live shocks from the capture stream to the market-data branch.

Append-only: shocks already recorded keep their original first_seen_at. A shock is only ever added, never
restamped, because the record is meant to answer "what did we know and when did we know it".
"""
import argparse, json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.shocks.live import ingest_context_dir  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", default="/home/user/_md")
    ap.add_argument("--out", default="data/shocks")
    a = ap.parse_args()
    canonical, observations = ingest_context_dir(os.path.join(a.md, "data/context"))
    out_dir = os.path.join(ROOT, a.out)
    os.makedirs(out_dir, exist_ok=True)

    existing = {}
    cpath = os.path.join(out_dir, "canonical_shocks.jsonl")
    if os.path.exists(cpath):
        for line in open(cpath):
            try:
                r = json.loads(line)
                existing[r["canonical_id"]] = r
            except json.JSONDecodeError:
                continue
    added = 0
    for s in canonical:
        d = s.to_dict()
        if d["canonical_id"] in existing:
            continue                                   # never restamp an already-recorded event
        existing[d["canonical_id"]] = d
        added += 1
    with open(cpath, "w") as f:
        for r in sorted(existing.values(), key=lambda x: x.get("first_seen_at") or ""):
            f.write(json.dumps(r, separators=(",", ":")) + "\n")

    opath = os.path.join(out_dir, "shock_observations.jsonl")
    seen = set()
    if os.path.exists(opath):
        for line in open(opath):
            try:
                seen.add(json.loads(line)["shock_id"])
            except (json.JSONDecodeError, KeyError):
                continue
    with open(opath, "a") as f:
        for s in observations:
            d = s.to_dict()
            if d["shock_id"] in seen:
                continue
            seen.add(d["shock_id"])
            f.write(json.dumps(d, separators=(",", ":")) + "\n")
    print(json.dumps({"canonical_total": len(existing), "canonical_added": added,
                      "observations_total": len(seen)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
