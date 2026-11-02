#!/usr/bin/env python3
"""Check *read-time* freshness of handicap-reports/latest (not freshness at publication).

Usage:
  python3 scripts/handicap/check_published_freshness.py --manifest /tmp/hr/latest/manifest.json

Exit 0 means CURRENT_RESEARCH, not a current/executable Kalshi quote.
Exit 2 means stale, missing, invalid, or uncertain; historical research is still readable,
but must NOT be represented as current betting input.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from nfl_edge.handicap.report_freshness import published_report_status  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--max-report-age-min", type=float, default=120.0)
    ap.add_argument("--max-market-age-min", type=float, default=90.0)
    a = ap.parse_args()
    try:
        with open(a.manifest) as f:
            manifest = json.load(f)
        status = published_report_status(manifest, datetime.now(timezone.utc),
                                         max_report_age_min=a.max_report_age_min,
                                         max_market_age_min=a.max_market_age_min)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        status = {"status": "STALE_RESEARCH", "can_use_as_current_research": False,
                  "problems": [f"Cannot establish report freshness: {exc}"]}
    print(json.dumps(status, indent=2))
    return 0 if status["can_use_as_current_research"] else 2


if __name__ == "__main__":
    sys.exit(main())
