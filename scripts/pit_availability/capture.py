#!/usr/bin/env python3
"""Append-only capture of NFL availability sources with our own retrieval times (research only).

    python3 scripts/pit_availability/capture.py --store data/pit_availability/nfl [--season 2026] [--dry-run]

Downloads are done beforehand by scripts/data/nflverse_download.py (injuries, depth_charts); this command stores
new injury-file content, a per-snapshot digest of the depth-chart file, the ESPN injuries endpoint and, for games
within [T-240m, T+30m], the ESPN per-event rosters (inactive-list evidence). Exit 0 unless the store itself fails.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.availability_pit import capture as C  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--store", required=True)
    ap.add_argument("--season", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    now = datetime.now(timezone.utc)
    season = a.season or (now.year if now.month >= 3 else now.year - 1)
    s = C.run(a.root, a.store, season=season, now=now, dry_run=a.dry_run)
    print(json.dumps(s, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
