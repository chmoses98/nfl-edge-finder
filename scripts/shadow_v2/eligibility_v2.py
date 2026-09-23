#!/usr/bin/env python3
"""PRODUCTION ELIGIBILITY document: every model arm and family, its status and the evidence behind it.

    python3 scripts/shadow_v2/eligibility_v2.py --reports data/shadow/v2/reports --market-data /tmp/md \
        --out data/shadow/v2/eligibility

Combines every week's `<label>.eligibility_inputs.json` (written by weekly_report_v2.py; per-game sums, no rows),
from the staging directory first and the published evidence branch second (one file per week; the staging copy
wins because it was just rebuilt), and writes:

    <out>/<stamp>.eligibility.json    write-once, the document as of this run
    <out>/latest.json                 the same document, the path consumers read (RUN NFL, handicap packet)

Policy, thresholds and the unit of evidence are in nfl_edge/evaluation/eligibility.py and
docs/PRODUCTION_ELIGIBILITY.md. Nothing here can promote an arm listed as a known defect.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.evaluation import eligibility as EL          # noqa: E402

LATEST = "latest.json"


def input_files(roots) -> dict:
    """label -> path, the first root that has the label winning."""
    out = {}
    for root in roots:
        if not root or not os.path.isdir(root):
            continue
        for p in sorted(glob.glob(os.path.join(root, "*.eligibility_inputs.json"))):
            label = os.path.basename(p).split(".")[0]
            out.setdefault(label, p)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--reports", default=os.path.join(ROOT, "data", "shadow", "v2", "reports"))
    ap.add_argument("--market-data", default="")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "shadow", "v2", "eligibility"))
    ap.add_argument("--now", default="")
    a = ap.parse_args(argv)
    now = datetime.fromisoformat(a.now) if a.now else datetime.now(timezone.utc)
    roots = [a.reports] + ([os.path.join(a.market_data, "data", "shadow", "v2", "reports")] if a.market_data else [])
    files = input_files(roots)
    acc = EL.Accumulator()
    for label, p in sorted(files.items()):
        doc = json.load(open(p))
        acc.merge(EL.Accumulator.from_json(doc.get("games") or []))
    doc = EL.build(acc, as_of=now.isoformat(), sources=sorted(files))
    os.makedirs(a.out, exist_ok=True)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    path = os.path.join(a.out, f"{stamp}.eligibility.json")
    if not os.path.exists(path):
        json.dump(doc, open(path, "w"), indent=1, default=str)
    json.dump(doc, open(os.path.join(a.out, LATEST), "w"), indent=1, default=str)
    print(json.dumps({"as_of": doc["as_of"], "sources": doc["sources"], "arms": doc["arms"]}, indent=1))
    return 0


def load_latest(market_data: str | None = None, root: str | None = None) -> dict | None:
    """The newest eligibility document a consumer can find: a local build first, then the evidence branch."""
    for base in ([root] if root else []) + ([os.path.join(market_data, "data", "shadow", "v2", "eligibility")] if market_data else []):
        p = os.path.join(base, LATEST)
        if os.path.exists(p):
            try:
                return json.load(open(p))
            except (OSError, ValueError):
                continue
    return None


if __name__ == "__main__":
    sys.exit(main())
