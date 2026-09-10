#!/usr/bin/env python3
"""Diagnose every settled, instrumented player projection of FINAL games into an immutable autopsy corpus.

    python3 scripts/shadow/player_autopsy.py --market-data /tmp/md --out data/shadow/player_autopsy [--game G]

Reads the published player-anatomy corpus (the ledger is never read for intermediates and never written), uses
the same result book and readiness gate as settlement
(player statistics AND snap counts must be published; a game is deferred whole otherwise), and writes
`data/shadow/player_autopsy/<game_id>/<version>.<batch>.autopsy.jsonl.gz` under the write-once store.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.settlement.nflverse_results import build_result_book                    # noqa: E402
from nfl_edge.settlement.results import READY                                         # noqa: E402
from nfl_edge.shadow import evaluation_store as ST                                     # noqa: E402
from nfl_edge.shadow import player_autopsy as PA                                       # noqa: E402


def _emit(path, values):
    if not path:
        return
    with open(path, "a") as f:
        for k, v in values.items():
            f.write(f"{k}={v}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", required=True)
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "shadow", "player_autopsy"))
    ap.add_argument("--anatomy-root", action="append", default=[], help="extra anatomy roots (local staging)")
    ap.add_argument("--season", type=int, default=0)
    ap.add_argument("--game", action="append", default=[])
    ap.add_argument("--lookback-days", type=float, default=10.0)
    ap.add_argument("--min-hours-after-kickoff", type=float, default=4.0)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--github-output", default="")
    a = ap.parse_args()
    now = datetime.now(timezone.utc)
    seasons = [a.season] if a.season else sorted({now.year, now.year - 1})
    book = build_result_book(ROOT, seasons, min_hours_after_kickoff=a.min_hours_after_kickoff)
    if a.game:
        candidates = sorted(set(a.game))
    else:
        candidates = sorted(g for g, gr in book.games.items() if gr.status == "FINAL" and gr.kickoff_utc
                            and now - timedelta(days=a.lookback_days) <= datetime.fromisoformat(gr.kickoff_utc) <= now)
    published = os.path.join(a.market_data, "data", "shadow", "player_autopsy")
    corpus = ST.EvaluationCorpus(a.out, read_roots=[published], suffix=PA.SUFFIX)
    anatomy_roots = [os.path.join(a.market_data, "data", "shadow", "player_anatomy")] + list(a.anatomy_root)
    by_game = PA.load_anatomy(anatomy_roots, candidates) if candidates else {}
    batch = ST.batch_id(now)
    written = unchanged = conflicts = 0
    deferred, done = [], []
    for gid in sorted(by_game):
        state, reason = book.readiness(gid, needs_player_stats=True, now=now)
        if state != READY:
            deferred.append({"game_id": gid, "state": state, "reason": reason}); print(f"  DEFER {gid}: {state} -- {reason}"); continue
        recs = PA.autopsy_game(by_game[gid], book, now=now)
        plan = corpus.plan(recs, gid)
        if plan["conflicts"]:
            conflicts += len(plan["conflicts"]); print(f"::error::{gid}: {len(plan['conflicts'])} autopsy conflict(s)"); continue
        from collections import Counter
        c = Counter(r["classification"] for r in recs)
        print(f"  {gid}: {len(recs)} projections diagnosed {dict(c)}; new {len(plan['new'])}, unchanged {len(plan['noop'])}", flush=True)
        unchanged += len(plan["noop"])
        if a.dry_run:
            continue
        m = corpus.write_batch(gid, recs, evaluation_version=PA.AUTOPSY_VERSION, batch=batch, plan=plan,
                               manifest_extra={"game_evidence": book.games[gid].evidence(), "result_sources": book.sources,
                                               "thresholds": {"z_large": PA.Z_LARGE, "log_ratio_large": PA.LOG_RATIO_LARGE,
                                                              "team_volume_log_ratio": PA.TEAM_VOLUME_LOG_RATIO,
                                                              "market_diff_large": PA.MARKET_DIFF_LARGE}})
        written += m.get("written", 0); done.append(gid)
    status = "CONFLICT" if conflicts else ("WROTE" if written else "NO_OP")
    print(json.dumps({"batch_id": batch, "games_done": done, "deferred": deferred, "written": written, "unchanged": unchanged,
                      "conflicts": conflicts, "status": status}, indent=1, default=str))
    _emit(a.github_output, {"status": status, "written": written, "batch_id": batch, "games_deferred": len(deferred)})
    return 4 if conflicts else 0


if __name__ == "__main__":
    sys.exit(main())
