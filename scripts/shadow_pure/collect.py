#!/usr/bin/env python3
"""PURE shadow collector (research only). Captures what is due, write-once, into the store.

    python3 scripts/shadow_pure/collect.py --store data/shadow_pure/nfl [--market-data /tmp/md] \
        [--player-map data/silver/kalshi_player_map.parquet] [--adhoc ALL|game_id,...] [--dry-run]

Exit codes: 0 captured or nothing due; 2 a guard refused (frozen model changed, provenance, post-kickoff, gate).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.shadow_pure import collect as C  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=ROOT, help="repository root holding data/raw/nflverse (downloaded beforehand)")
    ap.add_argument("--store", default=None)
    ap.add_argument("--market-data", default=None, help="checkout (sparse is fine) of the market-data branch; read-only")
    ap.add_argument("--player-map", default=None)
    ap.add_argument("--adhoc", default=None, help="ALL or comma-separated game ids: capture now as ADHOC")
    ap.add_argument("--dry-run", action="store_true", help="label the run a dry run (the workflow does not publish it)")
    ap.add_argument("--summary-out", default=None)
    ap.add_argument("--github-output", default=None)
    ap.add_argument("--check-windows", action="store_true",
                    help="only report whether any capture window is open now (schedule only); writes open=true|false")
    a = ap.parse_args(argv)
    if a.check_windows:
        w = C.windows_open(a.root)
        print(json.dumps({"open_windows": w}))
        if a.github_output:
            with open(a.github_output, "a") as fh:
                fh.write(f"open={'true' if w else 'false'}\n")
        return 0
    if not a.store:
        ap.error("--store is required")
    adhoc = None if a.adhoc is None else ("ALL" if a.adhoc == "ALL" else [g for g in a.adhoc.split(",") if g])
    try:
        s = C.run_capture(a.root, a.store, md_root=a.market_data, map_path=a.player_map, adhoc_games=adhoc, dry_run=a.dry_run)
    except Exception as exc:                       # every guard is a refusal, reported loudly
        print(f"REFUSED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    txt = json.dumps(s, indent=1, default=str, sort_keys=True)
    print(txt[:6000])
    if a.summary_out:
        with open(a.summary_out, "w") as fh:
            fh.write(txt + "\n")
    if a.github_output:
        with open(a.github_output, "a") as fh:
            fh.write(f"state={s.get('state', 'CAPTURED')}\nrun_id={s.get('run_id', '')}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
