"""RUN NFL validation: every SCORE-determined game-level family the card can emit is QB-gated, not only four of them.

`guards.guard_candidate` used to require confirmed quarterbacks only for GAME_WINNER / SPREAD / TOTAL / TEAM_TOTAL, but the card
derives and prices BOTH_TEAMS_SCORE_N (and an analyst can name WIN_MARGIN_BUCKET, RACE_TO_N or period BTTS/TD/full-time tickers).
Those settle on the score exactly like a total does, so with an unknown quarterback they were approved as bets while the same game's
spread was blocked QB_UNKNOWN. Player props and non-score markets stay untouched (owner: unknown QB blocks only game-level lines).
"""
import json
import pathlib
from datetime import timedelta

import numpy as np
import pytest

from card_fixtures import AS_OF, CENTER, GAME, KICK, _row, build_run, qb_records, qb_rows, schedule_text, thesis
from nfl_edge.handicap import card as C
from nfl_edge.handicap import fairvalue as FV
from nfl_edge.postmortem import guards as GD
from test_postmortem_wiring import ROOT, _run_entry_point
import test_card as T

pytestmark = pytest.mark.owner_policy

DEC = AS_OF
KO = AS_OF + timedelta(hours=4)


def _cand(ticker, qb=None):
    return {"ticker": ticker, "side": "YES", "decision_time": DEC, "kickoff_utc": KO,
            "projection_as_of": DEC - timedelta(minutes=5), "injuries_as_of": DEC - timedelta(minutes=5),
            "qb": qb or {}, "teams": ["AAA", "BBB"],
            "quote": {"price": 0.5, "captured_at": DEC - timedelta(minutes=1), "kind": "EXECUTABLE_ASK", "depth": 1000}, "contracts": 10}


SCORE_TICKERS = [
    "KXNFLGAME-26OCT25AAABBB-BBB", "KXNFLSPREAD-26OCT25AAABBB-BBB3", "KXNFLTOTAL-26OCT25AAABBB-45", "KXNFLTEAMTOTAL-26OCT25AAABBB-BBB24",
    "KXNFL1HSPREAD-26OCT25AAABBB-AAA3", "KXNFL1HWINNER-26OCT25AAABBB-AAA",
    # the ones that used to escape:
    "KXNFLBOTH-26OCT25AAABBB-20", "KXNFLWINMARGIN-26OCT25AAABBB-BBB1", "KXNFLRACE-26OCT25AAABBB-BBB10",
    "KXNFL1HBTTS-26OCT25AAABBB-Y", "KXNFL1HFT-26OCT25AAABBB-AAAAAA", "KXNFL2QTD-26OCT25AAABBB-1",
]


@pytest.mark.parametrize("ticker", SCORE_TICKERS)
def test_every_score_determined_family_requires_both_quarterbacks(ticker):
    out = GD.guard_candidate(_cand(ticker))
    assert "QB_UNKNOWN:AAA" in out["blocks"] and "QB_UNKNOWN:BBB" in out["blocks"], (ticker, out["blocks"])


@pytest.mark.parametrize("ticker", SCORE_TICKERS)
def test_confirmed_quarterbacks_still_let_the_family_through(ticker):
    qb = {t: {"status": "CONFIRMED_STARTER", "confirmed_at": DEC - timedelta(minutes=20)} for t in ("AAA", "BBB")}
    assert GD.guard_candidate(_cand(ticker, qb))["actionable"], ticker


@pytest.mark.parametrize("ticker", ["KXNFLRECYDS-26OCT25AAABBB-AAAWR1-60", "KXNFLANYTD-26OCT25AAABBB-AAAWR1"])
def test_player_props_are_never_qb_blocked(ticker):
    assert not [b for b in GD.guard_candidate(_cand(ticker))["blocks"] if b.startswith("QB_")]


# ---- through the REAL entry point: scripts/handicap/run_card.py -------------------------------------------------------------
N = 20


def _both_teams_score_tree(tmp):
    """The standard one-game capture plus a KXNFLBOTH rung priced at the simulation's own probability; a +7..9 total shift makes it the best line."""
    bank, _ = FV.bank_from_schedule(schedule_text(), 2026)
    sim = FV.GameSim(bank, "BBB", "AAA", CENTER[0], CENTER[1]).draw(0, 0)
    p = float(np.mean(np.minimum(sim["home"], sim["away"]) >= N))
    build_run(tmp / "a")
    shard = tmp / "a" / "analysis" / "games" / f"{GAME}.json"
    d = json.load(open(shard))
    ticker = f"KXNFLBOTH-26OCT25AAABBB-{N}"
    d["rows"].append(_row(ticker, "BOTH_TEAMS_SCORE_N", None, float(N), p, stat="min_team_points", meaning=f"YES iff both teams score >= {N}"))
    json.dump(d, open(shard, "w"))
    pk = json.load(open(tmp / "a" / "packet.json"))
    pk["games"][0]["markets"].append({"ticker": ticker, "movement": {"total_move_since_first_capture": 0.0}, "book_depth_yes": 500000.0, "book_depth_no": 500000.0})
    json.dump(pk, open(tmp / "a" / "packet.json", "w"))
    th = thesis(families=["BOTH_TEAMS_SCORE_N"], shift_margin=(0.0, 0.0), shift_total=(7.0, 9.0))
    run = C.load_reports(str(tmp / "a"))
    run["qb_confirmations"] = {GAME: qb_rows(AS_OF - timedelta(minutes=5), KICK)}
    first = C.run_card(run=run, theses=[th], schedule_text=schedule_text(), root=ROOT, as_of=AS_OF, mode=C.LIVE, draws=20000)
    line = first["lines"][0]
    assert line["ticker"] == ticker, "the fixture must make the both-teams-score rung the chosen line"
    row = next(r for r in d["rows"] if r["ticker"] == ticker)
    md = T._capture_for(tmp, row, line["side"])
    (tmp / "ledger" / "data").mkdir(parents=True)
    from nfl_edge.handicap import bankroll as BK
    (tmp / "bankroll.json").write_text(json.dumps({"bankroll": 5000, "observedAt": (AS_OF - timedelta(minutes=5)).isoformat(), "valueType": BK.VALUE_TYPE}))
    (tmp / "theses.json").write_text(json.dumps([th]))
    (tmp / "schedule.csv").write_text(schedule_text())
    return md


def test_run_nfl_entry_point_blocks_a_both_teams_score_line_when_the_quarterbacks_are_unknown(tmp_path):
    _both_teams_score_tree(tmp_path)
    card, _ = _run_entry_point(tmp_path, "noqb")
    line = card["lines"][0]
    assert line["ticker"].startswith("KXNFLBOTH")
    assert line["status"] == "BLOCKED", line["status"]
    assert any("QB_UNKNOWN:AAA" in r and "QB_UNKNOWN:BBB" in r for r in line["preflight"]["blocking_reasons"]), line["preflight"]["blocking_reasons"]


def test_run_nfl_entry_point_still_bets_a_both_teams_score_line_when_both_quarterbacks_are_confirmed(tmp_path):
    _both_teams_score_tree(tmp_path)
    qb = tmp_path / "qb.json"
    from nfl_edge.postmortem import qb_confirmations as QBC
    qb.write_text(json.dumps({"schema": QBC.SCHEMA, "records": qb_records(AS_OF, minutes_before_cap=6)}))
    card, _ = _run_entry_point(tmp_path, "ok", "--qb-confirmations", str(qb))
    line = card["lines"][0]
    assert line["ticker"].startswith("KXNFLBOTH") and line["status"] == "BET (preflight approved)", line["preflight"]["blocking_reasons"]
