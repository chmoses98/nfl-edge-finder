"""PR #232: replay the ACTUAL RUN NFL card entry point (scripts/handicap/run_card.py) with different confirmed-starter inputs.

Shows, on the same live-like capture: confirmed quarterbacks do NOT universally block game-level recommendations; unknown,
one-sided, stale, wrongly-sourced or other-game confirmations do; and on a two-game packet only the unconfirmed game is blocked.
Offline; real owner policy; the card's own preflight (depth walk, fees, quote age).
"""
import json
import os
from datetime import timedelta

import pytest

from card_fixtures import AS_OF, GAME, qb_records
from nfl_edge.handicap import gates as G
from nfl_edge.postmortem import qb_confirmations as Q
from test_postmortem_wiring import _live_inputs, _run_entry_point

pytestmark = pytest.mark.owner_policy


def _file(tmp_path, records, name="qb.json"):
    p = tmp_path / name
    p.write_text(json.dumps({"schema": Q.SCHEMA, "records": records}))
    return str(p)


def _run(tmp_path, records=None, name="out"):
    _live_inputs(tmp_path)
    extra = ["--qb-confirmations", _file(tmp_path, records)] if records is not None else []
    card, md = _run_entry_point(tmp_path, name, *extra)
    return card, md


def _blocks(card):
    return card["lines"][0]["preflight"]["blocking_reasons"]


def test_both_quarterbacks_confirmed_the_game_level_line_is_a_bet_not_universally_blocked(tmp_path):
    card, _ = _run(tmp_path, qb_records(AS_OF, minutes_before_cap=6))
    line = card["lines"][0]
    assert line["status"] == "BET (preflight approved)", _blocks(card)
    assert line["preflight"]["gates"][G.G_PIT]["status"] == "PASS"
    cov = json.load(open(tmp_path / "out" / "qb_coverage.json"))
    assert cov["games"] == 1 and cov["games_both_qbs_confirmed"] == 1 and cov["records_valid"] == 2 and cov["records_rejected"] == 0


def test_no_confirmation_source_blocks_with_an_explicit_reason_and_the_coverage_says_zero(tmp_path):
    card, md = _run(tmp_path, None)
    assert card["lines"][0]["status"] == "BLOCKED"
    assert any("QB_UNKNOWN:AAA" in r and "QB_UNKNOWN:BBB" in r for r in _blocks(card))
    cov = json.load(open(tmp_path / "out" / "qb_coverage.json"))
    assert cov["source_supplied"] is False and cov["games_both_qbs_confirmed"] == 0


def test_one_confirmed_quarterback_is_not_enough(tmp_path):
    card, _ = _run(tmp_path, qb_records(AS_OF, teams=("AAA",), minutes_before_cap=6))
    assert card["lines"][0]["status"] == "BLOCKED"
    reasons = " ".join(_blocks(card))
    assert "QB_UNKNOWN:BBB" in reasons and "QB_UNKNOWN:AAA" not in reasons


def test_a_depth_chart_cannot_confirm_so_the_run_stays_blocked_and_the_file_reports_the_rejection(tmp_path):
    recs = qb_records(AS_OF, source_type="DEPTH_CHART", minutes_before_cap=6)            # CONFIRMED_STARTER claimed from a depth chart
    card, _ = _run(tmp_path, recs)
    assert card["lines"][0]["status"] == "BLOCKED" and any("QB_UNKNOWN" in r for r in _blocks(card))
    cov = json.load(open(tmp_path / "out" / "qb_coverage.json"))
    assert cov["records_valid"] == 0 and cov["rejections_by_code"] == {Q.R_NONCONFIRMING_CANNOT_CONFIRM: 2}


def test_an_expected_starter_from_a_depth_chart_is_visible_but_still_blocks(tmp_path):
    recs = qb_records(AS_OF, source_type="DEPTH_CHART", minutes_before_cap=6)
    for r in recs:
        r["status"] = Q.EXPECTED_UNCONFIRMED
    card, _ = _run(tmp_path, recs)
    assert card["lines"][0]["status"] == "BLOCKED" and any("QB_NOT_CONFIRMED" in r for r in _blocks(card))


def test_a_stale_confirmation_blocks(tmp_path):
    recs = qb_records(AS_OF, minutes_before_cap=Q.CONFIRMATION_MAX_AGE_MIN + 30)
    card, _ = _run(tmp_path, recs)
    assert card["lines"][0]["status"] == "BLOCKED" and any("QB_NOT_CONFIRMED" in r for r in _blocks(card))


def test_a_confirmation_for_another_game_does_not_unblock_this_one(tmp_path):
    card, _ = _run(tmp_path, qb_records(AS_OF, game_id="2026_07_OTHER_GAME", minutes_before_cap=6))
    assert card["lines"][0]["status"] == "BLOCKED" and any("QB_UNKNOWN" in r for r in _blocks(card))


def test_a_later_withdrawal_blocks_a_previously_confirmed_game(tmp_path):
    recs = qb_records(AS_OF, minutes_before_cap=30)
    obs = (AS_OF - timedelta(minutes=10)).isoformat()
    recs.append({"record_id": "qbc-out", "game_id": GAME, "team": "AAA", "qb_player_id": "00-QBAAA", "status": Q.OUT,
                 "source_type": "INJURY_REPORT", "source_ref": "https://example.org/report", "observed_at": obs, "captured_at": obs, "captured_by": "t"})
    card, _ = _run(tmp_path, recs)
    assert card["lines"][0]["status"] == "BLOCKED" and any("QB_NOT_CONFIRMED:AAA" in r for r in _blocks(card))


def test_an_unreadable_or_old_shape_file_is_refused_not_treated_as_no_confirmations(tmp_path, capsys):
    import importlib
    import sys

    from test_postmortem_wiring import ROOT
    md, ledger, bk = _live_inputs(tmp_path)
    sys.path.insert(0, os.path.join(ROOT, "scripts", "handicap"))
    rc = importlib.import_module("run_card")
    old = tmp_path / "old.json"
    old.write_text(json.dumps({"AAA": {"status": "CONFIRMED_STARTER", "confirmed_at": AS_OF.isoformat(), "source": "x"}}))
    code = rc.main(["--reports-dir", str(tmp_path / "a"), "--theses", str(tmp_path / "theses.json"), "--allow-unreviewed",
                    "--schedule-csv", str(tmp_path / "schedule.csv"), "--handicap-root", ledger, "--market-data", md, "--bankroll-file", bk,
                    "--mode", "LIVE", "--as-of", AS_OF.isoformat(), "--qb-confirmations", str(old), "--out", str(tmp_path / "refused")])
    assert code == 2 and "refused" in capsys.readouterr().err and not (tmp_path / "refused" / "card.json").exists()


def _two_game_packet(tmp_path):
    """Add a second, unconfirmed game to the packet the first run built (no markets of its own: it is coverage only)."""
    pp = tmp_path / "a" / "packet.json"
    packet = json.load(open(pp))
    g2 = json.loads(json.dumps(packet["games"][0]))
    g2.update({"game_id": "2026_07_CCC_DDD", "home_team": "DDD", "away_team": "CCC", "markets": []})
    packet["games"].append(g2)
    json.dump(packet, open(pp, "w"))


def test_mixed_slate_only_the_unconfirmed_game_is_blocked_and_the_confirmed_game_still_bets(tmp_path):
    _live_inputs(tmp_path)
    _two_game_packet(tmp_path)
    card, _ = _run_entry_point(tmp_path, "mixed", "--qb-confirmations", _file(tmp_path, qb_records(AS_OF, minutes_before_cap=6)))
    assert card["lines"][0]["status"] == "BET (preflight approved)"
    cov = json.load(open(tmp_path / "mixed" / "qb_coverage.json"))
    by_game = {g["game_id"]: g["both_confirmed"] for g in cov["per_game"]}
    assert by_game == {GAME: True, "2026_07_CCC_DDD": False} and cov["games_both_qbs_confirmed"] == 1 and cov["games_blocked_qb"] == 1


def test_mixed_slate_confirming_only_the_other_game_leaves_this_game_blocked(tmp_path):
    _live_inputs(tmp_path)
    _two_game_packet(tmp_path)
    recs = qb_records(AS_OF, game_id="2026_07_CCC_DDD", teams=("CCC", "DDD"), minutes_before_cap=6)
    card, _ = _run_entry_point(tmp_path, "mixed2", "--qb-confirmations", _file(tmp_path, recs))
    assert card["lines"][0]["status"] == "BLOCKED"
    cov = json.load(open(tmp_path / "mixed2" / "qb_coverage.json"))
    assert {g["game_id"]: g["both_confirmed"] for g in cov["per_game"]} == {GAME: False, "2026_07_CCC_DDD": True}
