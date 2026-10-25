#!/usr/bin/env python3
"""Diagnose the owner's actual placed wagers (nfl_edge/handicap/wager_diagnostics.py). Prints COUNTS ONLY.

    python3 scripts/handicap/wager_diagnostics.py --handicap-root /tmp/hd --closes-root /tmp/md/data/shadow/v2/closes \
        --schedule-csv /tmp/md/data/kalshi/capture/schedule_cache.csv --capture-git-dir /tmp/md --season 2026 \
        --out-private /secure/diag --out-public data/handicap/diagnostics

The full document (stakes, P&L, per-position rows) goes to --out-private and is NEVER to be committed: the repository is
public. --out-public receives the redacted form (ratios, counts, z-scores; no dollars, tickers, games or episode ids).
Accounting and diagnosis only: nothing here reads a model or feeds a stake.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts", "handicap"))
from nfl_edge.handicap import settlement_amendments as AM  # noqa: E402
from nfl_edge.handicap import store  # noqa: E402
from nfl_edge.handicap import schedule_kickoffs as SK  # noqa: E402
from nfl_edge.handicap import wager_diagnostics as WD  # noqa: E402
from nfl_edge.handicap.actual_wager_postmortem import build  # noqa: E402
from nfl_edge.handicap.position_lifecycle import CaptureQuoteLookup  # noqa: E402
import actual_wager_postmortem as AWP  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--handicap-root", required=True)
    ap.add_argument("--closes-root", default=None)
    ap.add_argument("--schedule-csv", default=None)
    ap.add_argument("--capture-git-dir", default=None, help="market-data clone (blobless is fine): live-exit benchmarks and the capture CLV fallback")
    ap.add_argument("--capture-ref", default="origin/market-data")
    ap.add_argument("--season", type=int, required=True)
    ap.add_argument("--out-private", default=None)
    ap.add_argument("--out-public", default=None)
    ap.add_argument("--n-boot", type=int, default=4000)
    a = ap.parse_args(argv)

    if not os.path.isdir(os.path.join(a.handicap_root, "data")):
        print(f"{a.handicap_root} is not a handicap-data checkout", file=sys.stderr)
        return 2
    wagers = store.read_kind(a.handicap_root, "imported_wagers", season=a.season)
    settlements = store.read_kind(a.handicap_root, "wager_settlements", season=a.season)
    amendments = AM.read_amendments(a.handicap_root)
    closes = AWP.read_closes(a.closes_root, a.season, [w.get("market_ticker") for w in wagers])
    sched = {}
    if a.schedule_csv and os.path.exists(a.schedule_csv):
        with open(a.schedule_csv, encoding="utf-8") as f:
            sched = SK.kickoffs_from_schedule(f.read(), a.season)
    quote_at = AWP.git_quote_lookup(a.capture_git_dir, a.capture_ref)
    doc = build(wagers, settlements, closes, season=a.season, amendments=amendments, quote_at=quote_at, schedule_kickoffs=sched)

    # The fallback close needs a deeper look-back than the live-exit benchmark: runs, not minutes, before kickoff.
    deep = None
    if a.capture_git_dir and os.path.isdir(a.capture_git_dir):
        base = AWP.git_quote_lookup(a.capture_git_dir, a.capture_ref)
        deep = CaptureQuoteLookup(base.list_runs, base.read, runs_back=8)
    diag = WD.build_diagnostics(doc, quote_at=deep, n_boot=a.n_boot)

    if a.out_private:
        os.makedirs(a.out_private, exist_ok=True)
        with open(os.path.join(a.out_private, "wager_diagnostics.json"), "w") as f:
            json.dump(diag, f, indent=1, default=str)
        with open(os.path.join(a.out_private, "WAGER_DIAGNOSIS.md"), "w") as f:
            f.write(WD.render(diag))
    if a.out_public:
        os.makedirs(a.out_public, exist_ok=True)
        with open(os.path.join(a.out_public, f"{a.season}.wager_diagnostics.redacted.json"), "w") as f:
            json.dump(WD.redact(diag), f, indent=1, sort_keys=True, default=str)

    i, t = diag["integrity"], diag["totals"]
    print(f"wager diagnostics, season {a.season}: orders {i['orders']}, settlements {i['settlements']}, episodes "
          f"{i['independent_position_episodes']}, pending {i['pending']}, unestablished {i['unestablished_pnl']}, "
          f"unknown phase {i['unknown_phase_positions']}")
    c = diag["clv"]
    print(f"  canonical CLV n={c['canonical'].get('n')}, capture fallback n={c['capture_fallback'].get('n')}, pregame without any close "
          f"{c['pregame_without_any_close']}; hypotheses " + ", ".join(f"{h['id']}={h['verdict']}" for h in diag["hypotheses"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
