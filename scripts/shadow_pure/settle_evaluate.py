#!/usr/bin/env python3
"""PURE shadow: write outcomes for matured rows, reconcile, and score (append-only; research only).

    python3 scripts/shadow_pure/settle_evaluate.py --store data/shadow_pure/nfl [--market-data /tmp/md] \
        [--player-map data/silver/kalshi_player_map.parquet] [--bootstrap 1000] [--force]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.shadow_pure import collect as C  # noqa: E402
from nfl_edge.shadow_pure import evaluate as E  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--store", required=True)
    ap.add_argument("--market-data", default=None)
    ap.add_argument("--player-map", default=None)
    ap.add_argument("--bootstrap", type=int, default=1000)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    try:
        s = E.settle_and_evaluate(a.root, a.store, C.gate(), md_root=a.market_data, map_path=a.player_map,
                                  bootstrap=a.bootstrap, force=a.force)
    except Exception as exc:
        print(f"REFUSED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(s, indent=1, default=str, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
