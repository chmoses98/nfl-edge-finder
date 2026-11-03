"""PR #241 (2026-11-03): game-specific confirmation validity, the stake clamp, and the unchanged safeguards, THROUGH scripts/handicap/run_card.py."""
import importlib
import json
import os
import sys
from datetime import timedelta

import pytest

import test_card as T
from card_fixtures import AS_OF, GAME, build_run, qb_records, schedule_text, thesis
from nfl_edge.handicap import card as C
from nfl_edge.handicap import gates as G
from nfl_edge.handicap import staking as ST
from nfl_edge.postmortem import qb_confirmations as Q
from test_postmortem_wiring import ROOT, _live_inputs, _run_entry_point

pytestmark = pytest.mark.owner_policy

BET = "BET (preflight approved)"
H = timedelta(hours=1)


def _file(tmp_path, records, name="qb.json"):
    p = tmp_path / name
    p.write_text(json.dumps({"schema": Q.SCHEMA, "records": records}))
    return str(p)


def _run(tmp_path, records, name="out"):
    _live_inputs(tmp_path)
    card, _ = _run_entry_point(tmp_path, name, "--qb-confirmations", _file(tmp_path, records))
    return card


def _blocks(card):
    return " | ".join(card["lines"][0]["preflight"]["blocking_reasons"])


def _rec(team, qb, *, observed, status="CONFIRMED_STARTER", source="HEAD_COACH_STATEMENT_ON_RECORD", captured=None, rid=None, game=GAME, **kw):
    r = {"record_id": rid or f"r-{team}-{qb}-{status}-{observed.isoformat()}", "game_id": game, "team": team, "qb_player_id": qb, "status": status,
         "source_type": source, "source_ref": "https://example.org/s", "observed_at": observed.isoformat(), "captured_at": (captured or observed).isoformat(),
         "captured_by": "t"}
    r.update(kw)
    return r


def _ok(team, **kw):
    return _rec(team, f"00-{team}", observed=kw.pop("observed", AS_OF - timedelta(minutes=10)), **kw)


# ---- the windows, through the card ---------------------------------------------------------------------------------------------
@pytest.mark.parametrize("age_h,bet", [(23.0, True), (23.9, True), (24.5, False), (30.0, False)])
def test_age_at_decision_through_the_entry_point(tmp_path, age_h, bet):
    obs = AS_OF - timedelta(hours=age_h)
    card = _run(tmp_path, [_ok("AAA", observed=obs), _ok("BBB", observed=obs)])
    assert (card["lines"][0]["status"] == BET) is bet, _blocks(card)
    if not bet:
        assert "QB_NOT_CONFIRMED:AAA" in _blocks(card) and "QB_REASON:AAA:STALE_CONFIRMATION" in _blocks(card)


def test_a_confirmation_from_before_the_final_report_window_is_too_early_even_when_it_is_fresh(tmp_path):
    """Kickoff 60 h out and a confirmation 1 h old: fresh for the decision, but it predates the last 48 h in which the starter can still change."""
    kick = AS_OF + timedelta(hours=60)
    first = T.run(tmp_path / "a", [thesis()], mode=C.LIVE, kick=kick)
    ln = first["lines"][0]
    row = next(r for r in json.load(open(tmp_path / "a" / "analysis" / "games" / f"{GAME}.json"))["rows"] if r["ticker"] == ln["ticker"])
    md = T._capture_for(tmp_path, row, ln["side"])
    (tmp_path / "ledger" / "data").mkdir(parents=True)
    from nfl_edge.handicap import bankroll as BK
    (tmp_path / "bankroll.json").write_text(json.dumps({"bankroll": 5000, "observedAt": (AS_OF - timedelta(minutes=5)).isoformat(), "valueType": BK.VALUE_TYPE}))
    (tmp_path / "theses.json").write_text(json.dumps([thesis()]))
    (tmp_path / "schedule.csv").write_text(schedule_text())
    obs = AS_OF - H
    card, _ = _run_entry_point(tmp_path, "out", "--qb-confirmations", _file(tmp_path, [_ok("AAA", observed=obs), _ok("BBB", observed=obs)]))
    assert card["lines"][0]["status"] == "BLOCKED"
    assert "QB_REASON:AAA:OBSERVED_TOO_EARLY_BEFORE_KICKOFF" in _blocks(card) and "QB_REASON:BBB:OBSERVED_TOO_EARLY_BEFORE_KICKOFF" in _blocks(card)


# ---- game / team / time / source / supersession --------------------------------------------------------------------------------
def test_a_record_for_another_game_or_a_team_not_in_this_game_confirms_nothing(tmp_path):
    card = _run(tmp_path, [_ok("AAA", game="2026_07_OTHER_GAME"), _ok("BBB", game="2026_07_OTHER_GAME"), _ok("ZZZ")])
    assert card["lines"][0]["status"] == "BLOCKED" and "QB_UNKNOWN:AAA" in _blocks(card) and "QB_UNKNOWN:BBB" in _blocks(card)


def test_a_record_captured_after_the_decision_is_invisible_to_a_decision_made_before_it(tmp_path):
    obs = AS_OF - timedelta(minutes=10)
    late = AS_OF + timedelta(minutes=1)
    card = _run(tmp_path, [_rec("AAA", "00-AAA", observed=obs, captured=late), _rec("BBB", "00-BBB", observed=obs, captured=late)])
    assert card["lines"][0]["status"] == "BLOCKED" and "QB_UNKNOWN:AAA" in _blocks(card)


def test_a_record_captured_at_or_after_kickoff_is_not_pregame_evidence(tmp_path):
    ko = AS_OF + timedelta(hours=4)
    card = _run(tmp_path, [_rec(t, f"00-{t}", observed=AS_OF - timedelta(minutes=10), captured=ko) for t in ("AAA", "BBB")])
    assert card["lines"][0]["status"] == "BLOCKED" and "QB_UNKNOWN:AAA" in _blocks(card)


@pytest.mark.parametrize("source", sorted(Q.NON_CONFIRMING_SOURCE_TYPES))
def test_a_non_accepted_source_claiming_confirmation_is_rejected_and_blocks(tmp_path, source):
    card = _run(tmp_path, [_ok(t, source=source) for t in ("AAA", "BBB")])
    assert card["lines"][0]["status"] == "BLOCKED" and "QB_UNKNOWN:AAA" in _blocks(card)
    cov = json.load(open(tmp_path / "out" / "qb_coverage.json"))
    assert cov["records_valid"] == 0 and cov["rejections_by_code"] == {Q.R_NONCONFIRMING_CANNOT_CONFIRM: 2}


def test_two_different_confirmed_quarterbacks_conflict_and_block_with_both_record_ids(tmp_path):
    a = _rec("AAA", "00-A1", observed=AS_OF - 3 * H, rid="a1")
    b = _rec("AAA", "00-A2", observed=AS_OF - 2 * H, rid="a2")
    card = _run(tmp_path, [a, b, _ok("BBB")])
    assert card["lines"][0]["status"] == "BLOCKED"
    assert "QB_NOT_CONFIRMED:AAA" in _blocks(card) and "QB_REASON:AAA:CONFLICTING_CONFIRMATIONS" in _blocks(card)


def test_a_deliberate_supersession_restores_the_bet(tmp_path):
    a = _rec("AAA", "00-A1", observed=AS_OF - 3 * H, rid="a1")
    b = _rec("AAA", "00-A2", observed=AS_OF - 2 * H, rid="a2", supersedes=["a1"])
    card = _run(tmp_path, [a, b, _ok("BBB")])
    assert card["lines"][0]["status"] == BET, _blocks(card)


def test_a_later_out_blocks_and_the_record_carries_the_provenance_of_why(tmp_path):
    out = _rec("AAA", "00-AAA", observed=AS_OF - timedelta(minutes=5), status="OUT", source="INACTIVE_LIST", rid="out1")
    card = _run(tmp_path, [_ok("AAA", observed=AS_OF - 2 * H), _ok("BBB"), out])
    line = card["lines"][0]
    assert line["status"] == "BLOCKED" and "QB_REASON:AAA:WITHDRAWN_BY_LATER_OUT" in _blocks(card)
    rec = json.load(open(tmp_path / "out" / "records" / f"{line['recommendation_id']}.json"))
    row = rec["pit_evidence"]["qb"]["AAA"]
    assert row["status"] == "OUT" and row["record_id"] == "out1" and row["source"] == "INACTIVE_LIST" and row["reason"] == "WITHDRAWN_BY_LATER_OUT"
    assert row["as_of"] == AS_OF.isoformat() and row["observed_at"] and row["game_id"] == GAME
    assert rec["pit_evidence"]["qb_policy"]["max_age_at_decision_min"] == 1440


def test_a_bet_record_carries_the_confirmation_provenance_it_rested_on(tmp_path):
    card = _run(tmp_path, [_ok("AAA"), _ok("BBB")])
    line = card["lines"][0]
    assert line["status"] == BET
    rec = json.load(open(tmp_path / "out" / "records" / f"{line['recommendation_id']}.json"))
    for t in ("AAA", "BBB"):
        row = rec["pit_evidence"]["qb"][t]
        assert row["status"] == "CONFIRMED_STARTER" and row["source"] == "HEAD_COACH_STATEMENT_ON_RECORD" and row["source_ref"] and row["game_id"] == GAME
        assert row["observed_at"] and row["captured_at"] and row["as_of"] == AS_OF.isoformat() and row["kickoff_utc"]


def test_no_wall_clock_is_assigned_to_history_a_rehearsal_replay_uses_its_own_as_of(tmp_path):
    """A confirmation observed 10 minutes before the stated decision time is valid for THAT decision time; the same file judged at a later
    as-of is stale. Nothing here reads the real clock."""
    recs = [_ok("AAA"), _ok("BBB")]
    _live_inputs(tmp_path)
    sys.path.insert(0, os.path.join(ROOT, "scripts", "handicap"))
    rc = importlib.import_module("run_card")
    f = _file(tmp_path, recs)
    cov = {}
    for name, as_of in (("early", AS_OF), ("later", AS_OF + timedelta(hours=30))):
        md, ledger, bk = str(tmp_path / "md"), str(tmp_path / "ledger"), str(tmp_path / "bankroll.json")
        rc.main(["--reports-dir", str(tmp_path / "a"), "--theses", str(tmp_path / "theses.json"), "--allow-unreviewed", "--schedule-csv", str(tmp_path / "schedule.csv"),
                 "--handicap-root", ledger, "--market-data", md, "--bankroll-file", bk, "--mode", "REHEARSAL", "--as-of", as_of.isoformat(), "--qb-confirmations", f,
                 "--out", str(tmp_path / name)])
        cov[name] = json.load(open(tmp_path / name / "qb_coverage.json"))
    assert cov["early"]["games_both_qbs_confirmed"] == 1
    assert cov["later"]["games"] == 1 and cov["later"]["games_both_qbs_confirmed"] == 0     # decision after kickoff: nothing usable
    assert cov["early"]["max_age_at_decision_min"] == 1440 and cov["early"]["max_lead_before_kickoff_min"] == 2880
