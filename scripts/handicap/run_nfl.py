#!/usr/bin/env python3
"""RUN NFL -- build the handicap packet for a slate.

    python3 scripts/handicap/run_nfl.py --season 2026 --week 1

INPUTS (all read-only; this command writes nothing outside --out)
  --market-data   a checkout/worktree of the `market-data` branch. Supplies the shadow ledger (model view +
                  every listed market at one snapshot), the context captures (injuries, weather) and the
                  capture quote history used for movement.
  repo root       silver team-game rows and play-by-play for team and quarterback profiles.

FRESHNESS. The packet is only as current as the newest published ledger snapshot. That snapshot is produced
by the 2-hourly `shadow-price` workflow; if it is stale, this command reports the age rather than pretending
otherwise, and `--max-ledger-age-min` will make it fail instead of emitting a confidently stale packet.

OUTPUTS (under --out, default data/handicap/<run_id>/)
  packet.json            complete machine-readable record -- every market, every ladder, every flag
  slate.md               the document to read first: summary, priority ranking, one compact block per game
  games/<game_id>.md     one full document per game, for the games the priority ranking says to open

FAILURE MODES
  no ledger              exits 2 -- run scripts/shadow/price_slate.py, or point --market-data at a real
                         worktree. Never emits an empty packet.
  ledger too old         exits 3 when --max-ledger-age-min is set and exceeded.
  no rows for the week   exits 4 -- the slate is not listed yet, which is different from having no markets.
  per-game problems      never fatal. They appear as granular `data_health` flags on that game; one broken
                         prop does not discard a game and one broken game does not discard a slate.

This command recommends nothing. It produces the evidence a handicapper reasons from.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.handicap.packet import build_packet, load_latest_ledger  # noqa: E402
from nfl_edge.handicap.render import render_game_markdown, render_markdown  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="RUN NFL -- build the slate handicap packet")
    ap.add_argument("--market-data", default="/home/user/_market_data_wt",
                    help="worktree of the market-data branch")
    ap.add_argument("--season", type=int, default=2026)
    ap.add_argument("--week", type=int, default=1)
    ap.add_argument("--out", default=None, help="output directory (default data/handicap/<run_id>)")
    ap.add_argument("--movement-files", type=int, default=None,
                    help="cap on capture files scanned for movement (default: all)")
    ap.add_argument("--max-ledger-age-min", type=float, default=None,
                    help="fail if the newest ledger snapshot is older than this")
    ap.add_argument("--no-game-files", action="store_true", help="skip per-game markdown")
    a = ap.parse_args()

    t0 = time.time()
    now = datetime.now(timezone.utc)

    try:
        rows, manifest, _, ledger_path = load_latest_ledger(a.market_data)
    except FileNotFoundError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 2

    written = manifest.get("written_at")
    age_min = None
    if written:
        try:
            age_min = (now - datetime.fromisoformat(written)).total_seconds() / 60.0
        except ValueError:
            pass
    print(f"ledger: {os.path.basename(ledger_path)}  rows={len(rows)}  "
          f"age={'unknown' if age_min is None else f'{age_min:.0f}m'}")
    if a.max_ledger_age_min is not None and age_min is not None and age_min > a.max_ledger_age_min:
        print(f"FAIL: ledger is {age_min:.0f}m old, limit {a.max_ledger_age_min:.0f}m. "
              "Run the shadow-price workflow before handicapping.", file=sys.stderr)
        return 3

    try:
        packet = build_packet(a.market_data, ROOT, a.season, a.week,
                              movement_files=a.movement_files, now=now)
    except ValueError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 4

    out = a.out or os.path.join(ROOT, "data", "handicap", packet["handicap_run_id"])
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "packet.json"), "w") as f:
        json.dump(packet, f, indent=1, default=str)
    with open(os.path.join(out, "slate.md"), "w") as f:
        f.write(render_markdown(packet, compact=True))
    n_game_files = 0
    if not a.no_game_files:
        gdir = os.path.join(out, "games")
        os.makedirs(gdir, exist_ok=True)
        for g in packet["games"]:
            with open(os.path.join(gdir, f"{g['game_id']}.md"), "w") as f:
                f.write(render_game_markdown(g))
            n_game_files += 1

    s = packet["slate_summary"]
    print(f"\nRUN NFL complete in {time.time() - t0:.1f}s")
    print(f"  season {packet['season']} week {packet['week']}  run_id {packet['handicap_run_id']}  "
          f"packet_sha {packet['packet_sha']}")
    print(f"  games {s['games']}  markets {s['markets_listed_slate']}  "
          f"model-supported {s['markets_supported_slate']}")
    print(f"  new/changed injuries {len(s['new_or_changed_injuries'])}  "
          f"skill players out {len(s['major_skill_injuries_out'])}  "
          f"weather flagged {len(s['weather_concerns'])}")
    blocked = s["blocking_data_issues"]
    print(f"  blocking data issues: {len(blocked)}" + (f"  {blocked}" if blocked else ""))
    print(f"  written to {out}  (packet.json, slate.md, {n_game_files} game files)")
    print("\n  top priority for handicap:")
    for g in s["game_priority_for_handicap"][:5]:
        print(f"    {g['rank']}. {g['game_id']}  score {g['priority_score']}  {'; '.join(g['reasons'][:3])}")
    print("\n  REAL-MONEY STATUS: " + packet["real_money_status"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
