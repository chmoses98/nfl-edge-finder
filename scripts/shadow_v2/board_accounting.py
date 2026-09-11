#!/usr/bin/env python3
"""Board Accounting v1 + drift report over the latest discovery run.

    python3 scripts/shadow_v2/board_accounting.py --market-data /tmp/md [--projections data/shadow/v2/projections]
        [--ledger-observations <incumbent .observations.jsonl.gz>] --out research/board_v2

Reads (never writes) the discovery run, the reviewed registry, the provisional list, the capture state, the
schedule and the identity map, and writes:

    <out>/<run>.board.json / .BOARD.md       every contract's stages + terminal state, counts, percentages
    <out>/<run>.drift.json / .DRIFT.md       NEW_SERIES / NEW_MARKET_STRUCTURES / UNCLASSIFIED / REGISTRY_LAG / CAPTURE_GAP
    <out>/<run>.provisional.json             the provisional records for series outside the registry (input to capture v2)
    <out>/<run>.before_after.json            the incumbent ledger's support states at the same capture vs the v2 accounting
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.board import accounting as A, drift as D, provisional as P          # noqa: E402
from nfl_edge.projection.store import read_projections                            # noqa: E402


def latest_discovery(market_data: str) -> str:
    ds = sorted(d for d in glob.glob(os.path.join(market_data, "data", "kalshi", "discovery", "*")) if os.path.isdir(os.path.join(d, "markets")))
    if not ds:
        raise FileNotFoundError("no discovery run with a markets/ directory under " + market_data)
    return ds[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", required=True)
    ap.add_argument("--discovery-dir", default="")
    ap.add_argument("--projections", default="", help="v2 projection root (local staging and/or market-data)")
    ap.add_argument("--snapshot-id", default="", help="reference snapshot id for PROJECTED (default: latest under --projections)")
    ap.add_argument("--ledger-observations", default="", help="incumbent ledger file for the before/after comparison")
    ap.add_argument("--out", default=os.path.join(ROOT, "research", "board_v2"))
    ap.add_argument("--now", default="")
    ap.add_argument("--assume-provisional-capture", action="store_true",
                    help="ARCHITECTURE view: count provisional series as captured at their safe tier (what capture v2 will do). "
                         "Default is the AS-IS view: only the reviewed registry and the actual capture confirmations count.")
    a = ap.parse_args()
    now = datetime.fromisoformat(a.now.replace("Z", "+00:00")) if a.now else datetime.now(timezone.utc)
    ddir = a.discovery_dir or latest_discovery(a.market_data)
    disc = D.load_discovery(ddir)
    registry = json.load(open(os.path.join(ROOT, "config", "kalshi_nfl_series.json")))["series"]
    cap_root = os.path.join(a.market_data, "data", "kalshi", "capture")
    state_path = os.path.join(cap_root, "state.json")
    capture_state = json.load(open(state_path)) if os.path.exists(state_path) else None
    prov_prev = P.load_provisional(os.path.join(cap_root, P.PROVISIONAL_FILE))
    first_seen = D.first_seen_index(os.path.join(a.market_data, "data", "kalshi", "discovery"))
    # ---- drift
    fixture = os.path.join(ROOT, "tests", "fixtures", "kalshi_market_samples.json")
    known = D.known_structures_from_fixture(fixture) if os.path.exists(fixture) else None
    drift = D.drift_report(disc, registry, capture_state=capture_state, first_seen=first_seen, known_structures=known, now=now)
    # ---- provisional list for every NEW_SERIES
    series_by = {s["ticker"]: s for s in disc["series_nfl"]}
    prov_records = [P.provisional_record(series_by[r["series"]], r["open_markets"], first_seen=r["first_seen_run"], now=now)
                    for r in drift["NEW_SERIES"] if r["series"] in series_by]
    prov = P.merge_provisional(prov_prev, prov_records, registry, now=now)
    # ---- identity + schedule
    kick = A.load_kickoffs(os.path.join(cap_root, "schedule_cache.csv")) if os.path.exists(os.path.join(cap_root, "schedule_cache.csv")) else {}
    if not kick:
        p = os.path.join(ROOT, "data", "raw", "nflverse", "schedules", "games.csv")
        kick = A.load_kickoffs(p) if os.path.exists(p) else {}
    player_status = {}
    pm = os.path.join(ROOT, "data", "silver", "kalshi_player_map.parquet")
    if os.path.exists(pm):
        import polars as pl
        d = pl.read_parquet(pm)
        player_status = dict(zip(d["kalshi_player_id"].to_list(), d["status"].to_list()))
    # ---- projections
    projections = None
    if a.projections:
        rows = read_projections([a.projections])
        if rows:
            sid = a.snapshot_id or max(r["snapshot_id"] for r in rows)
            projections = [r for r in rows if r["snapshot_id"] == sid]
    prov_tiers = {t: {"tier": tier} for t, tier in P.capturable_provisional(prov, registry).items()} if a.assume_provisional_capture else {}
    cs_for_board = capture_state
    if a.assume_provisional_capture and capture_state is not None:
        # the architecture view asks what the tiers reach, not what one run happened to confirm
        cs_for_board = None
    board = A.build_board(disc, registry_series=registry, provisional=prov_tiers, capture_state=cs_for_board, kickoffs=kick,
                          player_status=player_status, projections=projections, now=now)
    board["view"] = "ARCHITECTURE (provisional series assumed captured)" if a.assume_provisional_capture else "AS-IS (reviewed registry + actual capture confirmations)"
    # ---- before: the incumbent's ledger at the same capture
    before = None
    if a.ledger_observations and os.path.exists(a.ledger_observations):
        led = [json.loads(l) for l in gzip.open(a.ledger_observations, "rt")]
        st = Counter(r.get("support_state") for r in led)
        board_tickers = {r["ticker"] for r in board["rows"] if "NFL_BOARD" in r["stages"]}
        led_tickers = {r["ticker"] for r in led}
        before = {"ledger_file": os.path.basename(a.ledger_observations), "ledger_rows": len(led), "by_support_state": dict(st),
                  "priced_supported": st.get("SUPPORTED", 0),
                  "board_contracts_in_ledger": len(board_tickers & led_tickers),
                  "board_contracts_absent_from_ledger": len(board_tickers - led_tickers),
                  "pct_of_board_priced_by_incumbent": round(100.0 * sum(1 for r in led if r.get("support_state") == "SUPPORTED" and r["ticker"] in board_tickers) / max(1, len(board_tickers)), 2),
                  "pct_of_board_with_explicit_state_in_ledger": round(100.0 * len(board_tickers & led_tickers) / max(1, len(board_tickers)), 2)}
    os.makedirs(a.out, exist_ok=True)
    run = disc["run_id"] + ("" if not a.assume_provisional_capture else ".architecture")
    slim = {k: v for k, v in board.items() if k != "rows"}
    json.dump({**slim, "rows": board["rows"]}, open(os.path.join(a.out, f"{run}.board.json"), "w"), default=str)
    open(os.path.join(a.out, f"{run}.BOARD.md"), "w").write(A.render_board(board) + "\n")
    json.dump(drift, open(os.path.join(a.out, f"{run}.drift.json"), "w"), indent=1, default=str)
    open(os.path.join(a.out, f"{run}.DRIFT.md"), "w").write(D.render_drift(drift) + "\n")
    json.dump(prov, open(os.path.join(a.out, f"{run}.provisional.json"), "w"), indent=1, default=str)
    json.dump({"before_incumbent_ledger": before, "after_v2_accounting": {"denominator": board["denominator"], "stages": board["stages"],
               "terminal_states": board["terminal_states"], "unexplained": board["unexplained"]}},
              open(os.path.join(a.out, f"{run}.before_after.json"), "w"), indent=1, default=str)
    print(json.dumps({"discovery_run": run, "view": board["view"], "denominator": board["denominator"], "stages": {k: v["n"] for k, v in board["stages"].items()},
                      "terminal": {k: v["n"] for k, v in board["terminal_states"].items() if v["n"]},
                      "unexplained": board["unexplained"]["n"], "drift_totals": drift["totals"], "before": before}, indent=1, default=str))
    return 0 if board["unexplained"]["n"] == 0 else 3


if __name__ == "__main__":
    sys.exit(main())
