#!/usr/bin/env python3
"""Close-price coverage by week: how many close records are a TRUE close, an earlier-quote PROXY, or MISSING.

    python3 scripts/shadow_v2/close_coverage.py --closes data/shadow/v2 [--json OUT] [--summary FILE]

Reads the write-once `*.closes_v2.jsonl.gz` batches under --closes and counts, per week and in total, the close
records by the repository's own quality tier (nfl_edge/evaluation/close.py):

    EXCELLENT  confirmed live within 20 minutes of kickoff   -> TRUE_CLOSE
    GOOD       within 90 minutes of kickoff                   -> TRUE_CLOSE
    STALE      older than 90 minutes, up to 24 hours          -> EARLIER_QUOTE_PROXY (never a close)
    MISSING    no valid pre-kickoff observation               -> MISSING
    NOT_APPLICABLE  season markets have no kickoff            -> excluded from the denominator

A proxy is reported as a proxy. Nothing here fills a missing close. The week is read from the game id
(`2026_08_CHI_SEA` -> 8); a record with no parseable game id is counted under `unknown`.
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import os
import re
import sys
from collections import Counter, defaultdict

TRUE_CLOSE, PROXY, MISSING, NOT_APPLICABLE = "TRUE_CLOSE", "EARLIER_QUOTE_PROXY", "MISSING", "NOT_APPLICABLE"
TIER_TO_KIND = {"EXCELLENT": TRUE_CLOSE, "GOOD": TRUE_CLOSE, "STALE": PROXY,
                "MISSING": MISSING, "NOT_APPLICABLE": NOT_APPLICABLE}
_GAME = re.compile(r"^(\d{4})_(\d{1,2})_")


def classify(row: dict) -> str:
    """The kind of close a record carries. An unrecognised or absent quality is MISSING, never TRUE_CLOSE."""
    return TIER_TO_KIND.get(str(row.get("close_quality") or "").upper(), MISSING)


def week_of(game_id) -> str:
    m = _GAME.match(str(game_id or ""))
    return f"{int(m.group(2)):02d}" if m else "unknown"


def iter_rows(root: str):
    for path in sorted(glob.glob(os.path.join(root, "**", "*.closes_v2.jsonl.gz"), recursive=True)):
        with gzip.open(path, "rt") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    yield json.loads(line)


def coverage(rows) -> dict:
    by_week: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        kind = classify(row)
        if kind == NOT_APPLICABLE:
            continue
        by_week[week_of(row.get("game_id"))][kind] += 1
    total: Counter = Counter()
    weeks = {}
    for week in sorted(by_week):
        c = by_week[week]
        n = sum(c.values())
        total.update(c)
        weeks[week] = {"records": n, TRUE_CLOSE: c[TRUE_CLOSE], PROXY: c[PROXY], MISSING: c[MISSING],
                       "true_close_share": round(c[TRUE_CLOSE] / n, 4) if n else None}
    n = sum(total.values())
    return {"weeks": weeks,
            "total": {"records": n, TRUE_CLOSE: total[TRUE_CLOSE], PROXY: total[PROXY], MISSING: total[MISSING],
                      "true_close_share": round(total[TRUE_CLOSE] / n, 4) if n else None}}


def markdown(report: dict) -> str:
    lines = ["### Close coverage (TRUE_CLOSE = confirmed within 90 min of kickoff; proxies are not closes)", "",
             "| week | records | true close | earlier-quote proxy | missing | true-close share |", "|---|---|---|---|---|---|"]
    for week, c in report["weeks"].items():
        share = "n/a" if c["true_close_share"] is None else f"{c['true_close_share']:.1%}"
        lines.append(f"| {week} | {c['records']} | {c[TRUE_CLOSE]} | {c[PROXY]} | {c[MISSING]} | {share} |")
    t = report["total"]
    share = "n/a" if t["true_close_share"] is None else f"{t['true_close_share']:.1%}"
    lines.append(f"| **all** | {t['records']} | {t[TRUE_CLOSE]} | {t[PROXY]} | {t[MISSING]} | {share} |")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--closes", required=True)
    ap.add_argument("--json", default="")
    ap.add_argument("--summary", default="", help="append the markdown table to this file (e.g. $GITHUB_STEP_SUMMARY)")
    a = ap.parse_args(argv)
    report = coverage(iter_rows(a.closes))
    text = markdown(report)
    print(text)
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(report, fh, indent=2, sort_keys=True)
    if a.summary:
        with open(a.summary, "a") as fh:
            fh.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
