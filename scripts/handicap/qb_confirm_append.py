#!/usr/bin/env python3
"""Append ONE confirmed-starter quarterback record to the append-only ledger (``qb_confirmations/<season>.jsonl``).

    python3 scripts/handicap/qb_confirm_append.py --ledger-dir qb/qb_confirmations --packet hr/latest/packet.json \
        --game-id 2026_09_SF_ATL --team SF --qb-player-id 00-0033873 --status CONFIRMED_STARTER \
        --source-type HEAD_COACH_STATEMENT_ON_RECORD --source-ref https://example.org/press-conference --observed-at 2026-11-04T18:30:00Z

This is the human-attested intake for the point-in-time quarterback gate (docs/QB_CONFIRMATIONS.md). It records what a source SAID,
when; it does not fetch anything and cannot verify the source. Refusals (exit 2), each with a code and nothing written:
  * the record fails ``qb_confirmations.validate_records`` (missing field, bad status/source, a depth chart/roster/inactive list
    claiming CONFIRMED_STARTER, observed after captured, naive timestamps);
  * the game or team is not in the packet, or the capture time is not before kickoff (a post-kickoff capture is no pregame fact);
  * observed_at is in the future of the capture clock.
The ledger is append-only: the file is only ever opened for append. The same assertion (game, team, QB, status, source type,
observed time) always maps to the same ``record_id``, so re-submitting it is a DUPLICATE_NOOP (exit 0), never a second line.
``--now`` exists for tests and replays; in the workflow the capture clock is the runner's UTC clock.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.postmortem import qb_confirmations as QBC  # noqa: E402
from nfl_edge.postmortem.common import parse_ts  # noqa: E402


def record_id(game_id, team, qb_player_id, status, source_type, observed_at_iso) -> str:
    key = "|".join([game_id, team, qb_player_id, status, source_type, observed_at_iso])
    return "qbc-" + hashlib.sha256(key.encode()).hexdigest()[:20]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ledger-dir", required=True)
    ap.add_argument("--packet", required=True, help="the RUN NFL packet.json the game and team are checked against")
    ap.add_argument("--game-id", required=True)
    ap.add_argument("--team", required=True)
    ap.add_argument("--qb-player-id", required=True)
    ap.add_argument("--qb-name", default=None)
    ap.add_argument("--status", required=True, choices=QBC.STATUSES)
    ap.add_argument("--source-type", required=True)
    ap.add_argument("--source-ref", required=True, help="where the source said it (a URL or a precise citation)")
    ap.add_argument("--observed-at", required=True, help="when the SOURCE said it (aware ISO-8601, e.g. 2026-11-04T18:30:00Z)")
    ap.add_argument("--captured-by", required=True)
    ap.add_argument("--supersedes", default="", help="comma-separated record ids this deliberately replaces (a change of mind)")
    ap.add_argument("--now", default=None, help="capture clock (tests/replays); default: current UTC time")
    a = ap.parse_args(argv)

    now = parse_ts(a.now) if a.now else datetime.now(timezone.utc)
    if now is None:
        print("refused: --now must be an aware ISO-8601 time", file=sys.stderr)
        return 2
    obs = parse_ts(a.observed_at)
    if obs is None:
        print("refused: BAD_TIMESTAMP:observed_at (must be an aware ISO-8601 time)", file=sys.stderr)
        return 2
    packet = json.load(open(a.packet))
    game = next((g for g in packet.get("games", []) if g.get("game_id") == a.game_id), None)
    if game is None:
        print(f"refused: GAME_NOT_IN_PACKET:{a.game_id}", file=sys.stderr)
        return 2
    if a.team not in (game.get("home_team"), game.get("away_team")):
        print(f"refused: TEAM_NOT_IN_GAME:{a.team}", file=sys.stderr)
        return 2
    ko = parse_ts(game.get("kickoff_utc"))
    if ko is None or now >= ko:
        print("refused: CAPTURE_AT_OR_AFTER_KICKOFF (a post-kickoff capture is not a pregame fact)", file=sys.stderr)
        return 2
    if obs > now:
        print("refused: OBSERVED_IN_THE_FUTURE", file=sys.stderr)
        return 2

    rid = record_id(a.game_id, a.team, a.qb_player_id, a.status, a.source_type, obs.isoformat())
    rec = QBC.new_record(record_id=rid, game_id=a.game_id, team=a.team, qb_player_id=a.qb_player_id, status=a.status,
                         source_type=a.source_type, source_ref=a.source_ref, observed_at=obs.isoformat(), captured_at=now,
                         captured_by=a.captured_by, qb_name=a.qb_name, supersedes=[s for s in a.supersedes.split(",") if s.strip()])
    _, rejected = QBC.validate_records([rec])
    if rejected:
        print("refused: " + ",".join(r["code"] for r in rejected), file=sys.stderr)
        return 2

    season = str(game.get("season") or a.game_id.split("_")[0])
    os.makedirs(a.ledger_dir, exist_ok=True)
    path = os.path.join(a.ledger_dir, f"{season}.jsonl")
    existing = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            existing = [json.loads(line) for line in fh if line.strip()]
    ids = {r.get("record_id") for r in existing}
    if rid in ids:
        print(f"DUPLICATE_NOOP {rid}")
        return 0
    unknown_sup = [s for s in rec.get("supersedes", []) if s not in ids]
    if unknown_sup:
        print("refused: SUPERSEDES_UNKNOWN_RECORD:" + ",".join(unknown_sup), file=sys.stderr)
        return 2
    with open(path, "a", encoding="utf-8") as fh:               # append-only: never opened for write or truncate
        fh.write(json.dumps(rec, sort_keys=True) + "\n")
    print(f"APPENDED {rid} {a.game_id} {a.team} {a.status} ({a.source_type})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
