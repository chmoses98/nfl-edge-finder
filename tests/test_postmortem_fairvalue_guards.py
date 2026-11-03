"""Issue #231: fee-inclusive pricing, calibrated fair value with uncertainty, bet-up-to, PIT guards."""
import math
import os
from datetime import datetime, timezone

from nfl_edge.execution.fees import load_fee_schedule
from nfl_edge.handicap import gates as G
from nfl_edge.postmortem import common as C
from nfl_edge.postmortem import fairvalue as FV
from nfl_edge.postmortem import guards as GD

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def std_fee(price, contracts):          # ceil(0.07*C*P*(1-P)) to a cent: the documented quadratic taker fee
    return math.ceil(round(0.07 * contracts * price * (1 - price) * 100, 9)) / 100


def test_break_even_is_price_plus_whole_order_fee_per_contract():
    assert FV.break_even_per_contract(0.50, 100, std_fee) == 0.50 + 1.75 / 100
    assert FV.break_even_per_contract(0.50, 100, lambda p, c: None) is None      # unknown fee never becomes zero
    assert FV.break_even_per_contract(1.0, 100, std_fee) is None


def test_matches_the_real_schedule_through_the_repo_fee_engine():
    s = load_fee_schedule(ROOT)
    fee = FV.fee_fn_from_schedule(s, "KXNFLSPREAD", datetime(2026, 10, 25, 15, tzinfo=timezone.utc))
    assert fee(0.5, 100) == 1.75 and abs(FV.break_even_per_contract(0.5, 100, fee) - 0.5175) < 1e-12


def test_contracts_for_budget_is_fee_inclusive():
    c = FV.contracts_for_budget(0.40, 100.0, std_fee)
    assert abs(c * 0.40 + std_fee(0.40, c) - 100.0) < 0.05


def test_no_calibration_means_no_fair_probability_and_no_bet_up_to():
    f = FV.fair_probability(0.62, None)
    assert f.p is None and f.low is None and not f.calibrated and "MISSING_CALIBRATION" in f.flags
    assert FV.bet_up_to(f, 75, std_fee)["bet_up_to_cents"] is None


def test_thin_cell_is_refused():
    ev = FV.CalibrationEvidence("TEAM_TOTAL", ((0.5, 0.6, 10, 6),), "split-x")
    f = FV.fair_probability(0.55, ev)
    assert f.p is None and "CALIBRATION_CELL_TOO_THIN" in f.flags


def test_calibrated_fair_has_uncertainty_and_bet_up_to_uses_conservative_low():
    ev = FV.CalibrationEvidence("SPREAD", ((0.5, 0.6, 400, 220),), "heldout-2024")
    f = FV.fair_probability(0.55, ev)
    assert f.calibrated and f.low < f.p < f.high and f.n_evidence == 400
    b = FV.bet_up_to(f, 75, std_fee)
    cents = b["bet_up_to_cents"]
    assert cents is not None and b["break_even_at_limit"] <= f.low
    nxt = FV.contracts_for_budget((cents + 1) / 100, 75, std_fee)
    assert FV.break_even_per_contract((cents + 1) / 100, nxt, std_fee) > f.low        # one cent higher fails
    e = FV.edge_summary(cents / 100, b["contracts_at_limit"], std_fee, f)
    assert e["clears_conservatively"] and e["edge_low"] >= 0


def test_declared_range_is_never_presented_as_calibrated():
    f = FV.fair_probability(None, None, declared=(0.55, 0.60))
    b = FV.bet_up_to(f, 75, std_fee)
    assert not f.calibrated and "UNCALIBRATED_FAIR" in b["flags"]


def test_fit_bins_counts():
    bins = FV.fit_bins([0.1, 0.15, 0.55, 0.9], [0, 1, 1, 1], [0, 0.5, 1.0])
    assert bins == ((0, 0.5, 2, 1), (0.5, 1.0, 2, 2))


# ------------------------------------------------------------------ guards
NOW = "2026-10-25T16:00:00+00:00"
KO = "2026-10-25T17:00:00+00:00"


def cand(**over):
    c = {"ticker": "KXNFLSPREAD-26OCT25SFATL-SF3", "side": "YES", "decision_time": NOW, "kickoff_utc": KO,
         "projection_as_of": "2026-10-25T15:00:00+00:00", "injuries_as_of": "2026-10-25T15:30:00+00:00", "teams": ["SF", "ATL"],
         # 2026-11-03 (PR #241): a confirmed row must now name an accepted source (the guard re-judges it); the fixture had none.
         "qb": {t: {"status": GD.QB_CONFIRMED, "confirmed_at": "2026-10-25T15:45:00+00:00", "source": "HEAD_COACH_STATEMENT_ON_RECORD"} for t in ("SF", "ATL")},
         "quote": {"price": 0.5, "captured_at": "2026-10-25T15:55:00+00:00", "kind": "EXECUTABLE_ASK", "depth": 500}, "contracts": 100}
    c.update(over)
    return c


def test_clean_candidate_is_actionable_and_policy_constants_match_existing_gates():
    assert GD.guard_candidate(cand())["actionable"]
    assert C.MAX_QUOTE_AGE_MIN == G.Q.DEFAULT_MAX_QUOTE_AGE_MIN


def test_each_stale_or_missing_input_blocks():
    cases = {
        "AFTER_KICKOFF": cand(decision_time="2026-10-25T17:00:00+00:00", projection_as_of="2026-10-25T16:30:00+00:00",
                              injuries_as_of="2026-10-25T16:30:00+00:00", quote={"price": .5, "captured_at": "2026-10-25T16:55:00+00:00", "kind": "EXECUTABLE_ASK", "depth": 500}),
        "STALE_PROJECTION": cand(projection_as_of="2026-10-24T12:00:00+00:00"),
        "STALE_INJURIES": cand(injuries_as_of="2026-10-24T12:00:00+00:00"),
        "STALE_QUOTE": cand(quote={"price": .5, "captured_at": "2026-10-25T15:30:00+00:00", "kind": "EXECUTABLE_ASK", "depth": 500}),
        "MISSING_KICKOFF": cand(kickoff_utc=None),
        "MISSING_PROJECTION_AS_OF": cand(projection_as_of=None),
        "MISSING_INJURY_SNAPSHOT": cand(injuries_as_of=None),
        "PRICE_NOT_EXECUTABLE": cand(quote={"price": .5, "captured_at": "2026-10-25T15:55:00+00:00", "kind": "CAPTURED_MID"}),
        "INSUFFICIENT_DEPTH": cand(quote={"price": .5, "captured_at": "2026-10-25T15:55:00+00:00", "kind": "EXECUTABLE_ASK", "depth": 10}),
        "PROJECTION_AFTER_DECISION": cand(projection_as_of="2026-10-25T16:10:00+00:00"),
        "MISSING_DECISION_TIME": cand(decision_time="2026-10-25T16:00:00"),      # naive timestamp refused
    }
    for code, c in cases.items():
        v = GD.guard_candidate(c)
        assert not v["actionable"] and code in v["blocks"], (code, v)


def test_qb_must_be_confirmed_for_both_teams_before_the_decision():
    c = cand()
    c["qb"]["ATL"] = {"status": "PROBABLE", "confirmed_at": None}
    assert "QB_NOT_CONFIRMED:ATL" in GD.guard_candidate(c)["blocks"]
    c = cand(); del c["qb"]["SF"]
    assert "QB_UNKNOWN:SF" in GD.guard_candidate(c)["blocks"]
    c = cand(); c["qb"]["SF"]["confirmed_at"] = "2026-10-25T16:30:00+00:00"
    assert "QB_CONFIRMED_AFTER_DECISION:SF" in GD.guard_candidate(c)["blocks"]


def test_guards_never_reorder_or_add():
    cs = [cand(ticker="KXNFLTOTAL-26OCT25SFATL-45"), cand(projection_as_of=None)]
    out = GD.guard_candidates(cs)
    assert [o["ticker"] for o in out] == [c["ticker"] for c in cs] and [o["actionable"] for o in out] == [True, False]
