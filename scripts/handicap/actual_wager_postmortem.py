#!/usr/bin/env python3
"""Write the OWNER ACTUAL PLACED WAGERS postmortem (season and per week). Prints COUNTS ONLY.

    python3 scripts/handicap/actual_wager_postmortem.py --handicap-root /tmp/hd \
        --closes-root /tmp/md/data/shadow/v2/closes --season 2026 --out data/handicap/actual_wagers \
        --fail-on-overdue-days 3

Reads `imported_wagers` and `wager_settlements` from a handicap-data checkout and the canonical closes published
under `data/shadow/v2/closes/<game_id>/*.closes_v2.jsonl.gz`, and writes one JSON + Markdown document for the
season and one per week (nfl_edge/handicap/actual_wager_postmortem.py).

The documents carry the owner's economics. They are written to FILES for the branch the workflow publishes to;
this script's stdout -- which lands in a public Actions log -- carries counts and states only, never a stake, a
price, a return or a ticker.

SETTLEMENT OVERDUE is the destination-side reconciliation: a wager whose game date is more than N days past with
no settlement record means a settlement was not delivered (or was refused) -- the one failure the ledger can
detect on its own. `--fail-on-overdue-days N` turns that into a red run.
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import os
import sys
from datetime import date, datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.handicap import store  # noqa: E402
from nfl_edge.handicap.actual_wager_postmortem import build, render  # noqa: E402


KEEP = ("ticker", "game_id", "close_status", "close_reason", "close_quality", "close_id", "mid", "no_mid",
        "confirmed_at", "kickoff_utc")


def read_closes(closes_root: str | None, season: int, tickers) -> list:
    """Canonical close rows for the WAGERED tickers only. The published files hold one row per model prediction
    (hundreds of thousands a week), so rows are streamed, filtered on a cheap substring first and reduced to the
    fields CLV needs."""
    want = set(t for t in tickers if t)
    rows = []
    if not closes_root or not os.path.isdir(closes_root) or not want:
        return rows
    for path in sorted(glob.glob(os.path.join(closes_root, f"{season}_*", "*.closes_v2.jsonl.gz"))):
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            for line in handle:
                if not any(t in line for t in want):
                    continue
                row = json.loads(line)
                if row.get("ticker") in want:
                    rows.append({k: row.get(k) for k in KEEP})
    return rows


def overdue(wagers: list, settlements: list, today: date, days: int) -> list:
    settled = {s.get("source_bet_key") for s in settlements}
    out = []
    for w in wagers:
        try:
            gd = date.fromisoformat(str(w.get("game_date")))
        except ValueError:
            continue
        if w.get("source_bet_key") not in settled and (today - gd).days > days:
            out.append(w.get("imported_wager_id"))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--handicap-root", required=True)
    ap.add_argument("--closes-root", default=None)
    ap.add_argument("--season", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--today", default=None)
    ap.add_argument("--fail-on-overdue-days", type=int, default=None)
    a = ap.parse_args(argv)

    if not os.path.isdir(os.path.join(a.handicap_root, "data")):
        print(f"{a.handicap_root} is not a handicap-data checkout", file=sys.stderr)
        return 2
    wagers = store.read_kind(a.handicap_root, "imported_wagers", season=a.season)
    settlements = store.read_kind(a.handicap_root, "wager_settlements", season=a.season)
    closes = read_closes(a.closes_root, a.season, [w.get("market_ticker") for w in wagers])

    os.makedirs(a.out, exist_ok=True)
    season_dir = os.path.join(a.out, str(a.season))
    os.makedirs(season_dir, exist_ok=True)
    docs = {"season": build(wagers, settlements, closes, season=a.season)}
    for wk in sorted({w.get("week") for w in wagers if isinstance(w.get("week"), int)}):
        docs[f"week_{wk:02d}"] = build(wagers, settlements, closes, season=a.season, week=wk)
    for name, doc in docs.items():
        with open(os.path.join(season_dir, f"{name}.actual_wagers.json"), "w") as f:
            json.dump(doc, f, indent=1, sort_keys=True)
        with open(os.path.join(season_dir, f"{name}.ACTUAL_WAGERS.md"), "w") as f:
            f.write(render(doc))

    # COUNTS ONLY from here on.
    print(f"owner actual wagers, season {a.season}: {len(wagers)} wager(s), {len(settlements)} settlement(s), "
          f"{len(closes)} canonical close row(s) read")
    for name, doc in docs.items():
        t = doc["totals"]
        print(f"  {name}: wagers {t['wagers']}, settled {t['settled']}, pending {t['pending']}, "
              f"P&L established {t['pl_established']}, unestablished {t['pl_unestablished']}, "
              f"CLV valid {t['clv']['valid']}, CLV states {t['clv']['states']}")
    today = date.fromisoformat(a.today) if a.today else datetime.now(timezone.utc).date()
    if a.fail_on_overdue_days is not None:
        late = overdue(wagers, settlements, today, a.fail_on_overdue_days)
        print(f"settlement overdue (> {a.fail_on_overdue_days} days after game date, no settlement record): {len(late)}")
        if late:
            print("::error::wagers are past their game date with no settlement record; the settlement delivery "
                  "has not landed (see kalshi-bet-router settle-wagers)")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
