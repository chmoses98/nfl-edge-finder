"""PR #241 (2026-11-03): the owner safeguards that must NOT move, exercised THROUGH scripts/handicap/run_card.py (the RUN NFL entry point):
1U = $75, 5U maximum per bet (including the 8U -> 5U clamp), exposure review flags (not caps), no blanket daily cap, no bet at or after kickoff,
15-minute quote freshness, fee-inclusive break-even.
"""
import importlib
import json
import os
import sys
from datetime import timedelta

import pytest

import test_card as T
from card_fixtures import AS_OF, GAME, build_run, qb_records, schedule_text, thesis
from nfl_edge.handicap import card as C
from nfl_edge.handicap import staking as ST
from nfl_edge.postmortem import qb_confirmations as Q
from test_postmortem_wiring import ROOT, _live_inputs, _run_entry_point

pytestmark = pytest.mark.owner_policy
BET = "BET (preflight approved)"


def _qb(tmp_path):
    p = tmp_path / "qb.json"
    p.write_text(json.dumps({"schema": Q.SCHEMA, "records": qb_records(AS_OF, minutes_before_cap=6)}))
    return ["--qb-confirmations", str(p)]


def test_the_real_card_never_sizes_above_2u_without_independent_corroboration(tmp_path):
    _live_inputs(tmp_path)
    card, _ = _run_entry_point(tmp_path, "out", *_qb(tmp_path))
    line = card["lines"][0]
    assert line["status"] == BET and line["stake_units"] <= 2 and line["stake_dollars"] == line["stake_units"] * 75
    assert card["exposure_flags"]["unit_dollars"] == 75.0


def test_an_8u_proposal_is_clamped_to_5u_through_the_card_by_the_depth_cover_and_then_by_the_owner_risk_policy(tmp_path, monkeypatch):
    """The card's own ladder tops out at 5U and a thesis cannot ask for a stake, so an 8U proposal is FORCED here: the staking ladder is made to
    answer 8U, the book depth is made to cover 8U (otherwise the depth cover cuts it first) and the bankroll is large enough that the 3 %-of-bankroll
    guard does not bind first. What is left is exactly the owner's 5U per-position cap in config/risk_policy.json, applied by risk.py inside the card."""
    monkeypatch.setattr(ST, "decide", lambda x: ST.StakeDecision(8, "8U"))
    monkeypatch.setattr(C, "_depth_units", lambda pm, e: 10)
    monkeypatch.setitem(C.UNITS_TO_GRADE, 8, "A+")
    _live_inputs(tmp_path)
    from nfl_edge.handicap import bankroll as BK
    (tmp_path / "bankroll.json").write_text(json.dumps({"bankroll": 40000, "observedAt": (AS_OF - timedelta(minutes=5)).isoformat(), "valueType": BK.VALUE_TYPE}))
    card, _ = _run_entry_point(tmp_path, "out", *_qb(tmp_path))
    line = card["lines"][0]
    assert line["status"] == BET and line["stake_units"] == 5 and line["stake_dollars"] == 375, line
    sel = next(t["selected"] for t in card["theses"] if t.get("selected"))
    assert sel["stake_units"] == 8 and sel["final_units"] == 5
    v = sel["portfolio"]
    assert v["status"] == "CAPPED" and v["proposed_stake"] == 600.0 and v["approved_stake"] == 375.0 and v["binding_limit"] == "max_stake_per_position_units"
    rec = json.load(open(tmp_path / "out" / "records" / f"{line['recommendation_id']}.json"))
    assert rec["proposed_stake"] == 600 and rec["recommended_stake"] == 375


def test_an_8u_proposal_the_book_cannot_cover_is_cut_to_5u_by_the_depth_cover_first(tmp_path, monkeypatch):
    monkeypatch.setattr(ST, "decide", lambda x: ST.StakeDecision(8, "8U"))
    monkeypatch.setitem(C.UNITS_TO_GRADE, 8, "A+")
    _live_inputs(tmp_path)
    from nfl_edge.handicap import bankroll as BK
    (tmp_path / "bankroll.json").write_text(json.dumps({"bankroll": 40000, "observedAt": (AS_OF - timedelta(minutes=5)).isoformat(), "valueType": BK.VALUE_TYPE}))
    card, _ = _run_entry_point(tmp_path, "out", *_qb(tmp_path))
    line = card["lines"][0]
    sel = next(t["selected"] for t in card["theses"] if t.get("selected"))
    assert line["stake_units"] == 5 and line["stake_dollars"] == 375 and sel["stake_units"] == 5      # _depth_units caps at min(5, ...)
    assert any("stake cut from 8U to 5U" in n for n in sel["stake"]["notes"])


def test_the_3_percent_bankroll_guard_still_binds_below_the_5u_cap(tmp_path, monkeypatch):
    monkeypatch.setattr(ST, "decide", lambda x: ST.StakeDecision(5, "5U"))
    _live_inputs(tmp_path)                                            # bankroll 5000 -> 3 % = $150 = 2U
    card, _ = _run_entry_point(tmp_path, "out", *_qb(tmp_path))
    assert card["lines"][0]["stake_dollars"] == 150


def test_no_bet_at_or_after_kickoff_through_the_entry_point(tmp_path):
    _live_inputs(tmp_path)
    sys.path.insert(0, os.path.join(ROOT, "scripts", "handicap"))
    rc = importlib.import_module("run_card")
    ko = AS_OF + timedelta(hours=4)
    for name, as_of in (("at", ko), ("after", ko + timedelta(minutes=1))):
        rc.main(["--reports-dir", str(tmp_path / "a"), "--theses", str(tmp_path / "theses.json"), "--allow-unreviewed", "--schedule-csv", str(tmp_path / "schedule.csv"),
                 "--handicap-root", str(tmp_path / "ledger"), "--market-data", str(tmp_path / "md"), "--bankroll-file", str(tmp_path / "bankroll.json"), "--mode", "LIVE",
                 "--as-of", as_of.isoformat(), *_qb(tmp_path), "--out", str(tmp_path / name)])
        card = json.load(open(tmp_path / name / "card.json"))
        assert not any(l["status"] == BET for l in card["lines"]), name


def test_a_quote_older_than_15_minutes_at_the_decision_is_not_a_bet(tmp_path, monkeypatch):
    first = T.run(tmp_path / "a", [thesis()], mode=C.LIVE)
    ln = first["lines"][0]
    row = next(r for r in json.load(open(tmp_path / "a" / "analysis" / "games" / f"{GAME}.json"))["rows"] if r["ticker"] == ln["ticker"])
    monkeypatch.setattr(T, "AS_OF", AS_OF - timedelta(minutes=14))     # the capture is stamped 17 minutes before the decision
    T._capture_for(tmp_path, row, ln["side"])
    monkeypatch.undo()
    (tmp_path / "ledger" / "data").mkdir(parents=True)
    from nfl_edge.handicap import bankroll as BK
    (tmp_path / "bankroll.json").write_text(json.dumps({"bankroll": 5000, "observedAt": (AS_OF - timedelta(minutes=5)).isoformat(), "valueType": BK.VALUE_TYPE}))
    (tmp_path / "theses.json").write_text(json.dumps([thesis()]))
    (tmp_path / "schedule.csv").write_text(schedule_text())
    card, _ = _run_entry_point(tmp_path, "out", *_qb(tmp_path))
    line = card["lines"][0]
    assert line["status"] == "BLOCKED" and any(r.startswith("decision_time_quote_freshness") for r in line["preflight"]["blocking_reasons"]), line["preflight"]["blocking_reasons"]


def test_the_card_has_no_blanket_daily_cap_and_flags_are_not_caps():
    import json as _j
    pol = _j.load(open(os.path.join(ROOT, "config", "risk_policy.json")))
    assert pol["max_slate_exposure_units"] is None and pol["max_exposure_per_game_units"] is None
    assert pol["max_stake_per_position_units"] == 5 and pol["fixed_unit_dollars"] == 75
