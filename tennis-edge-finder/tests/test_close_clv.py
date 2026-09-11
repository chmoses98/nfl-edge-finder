import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from datetime import datetime, timedelta, timezone
from tennis_edge.ledger.close import Quote, canonical_close, clv
from tennis_edge.ledger.truth import SportsTruth, ExchangeTruth, reconcile

T0 = datetime(2026, 9, 9, 18, 30, tzinfo=timezone.utc)


def q(minutes, bid, ask, source="market_record"):
    return Quote(T0 + timedelta(minutes=minutes), bid, ask, source=source)


def test_close_is_last_executable_strictly_before_first_ball():
    quotes = [q(-60, 0.60, 0.63), q(-10, 0.61, 0.64), q(-1, 0.62, 0.65), q(0, 0.70, 0.72), q(5, 0.80, 0.82)]
    cc = canonical_close(quotes, scheduled_start=T0, actual_first_ball=T0)
    assert cc.close_basis == "ACTUAL_FIRST_BALL" and cc.quote.ts == T0 - timedelta(minutes=1)
    # a quote exactly AT first ball is not strictly before
    assert cc.quote.yes_bid == 0.62


def test_scheduled_fallback_uses_margin_and_is_labelled():
    quotes = [q(-60, 0.60, 0.63), q(-4, 0.61, 0.64)]
    cc = canonical_close(quotes, scheduled_start=T0, actual_first_ball=None)
    assert cc.close_basis == "SCHEDULED_MINUS_MARGIN" and cc.quote.ts == T0 - timedelta(minutes=60)


def test_no_synthetic_close():
    assert canonical_close([q(-1, None, 0.6), q(-2, 0.7, 0.6)], T0, T0).quote is None   # one-sided / crossed are not executable
    assert canonical_close([], T0, T0).quote is None
    assert canonical_close([q(-3, 0.5, 0.52, source="trade")], T0, T0).quote is None   # trades are never quotes


def test_clv_signs():
    decision = q(-120, 0.55, 0.58)
    cc = canonical_close([q(-1, 0.62, 0.65)], T0, T0)
    c = clv(decision, cc)
    assert abs(c.midpoint_clv - (0.635 - 0.58)) < 1e-12
    assert abs(c.executable_clv - (0.62 - 0.58)) < 1e-12
    assert abs(c.raw_prob_movement - (0.635 - 0.565)) < 1e-12


def test_truth_reconciliation():
    s = SportsTruth("m1", "A", "B", "RETIRED", "6-3 2-1 RET", confidence=0.95)
    e_yes = ExchangeTruth("t", "finalized", "yes", 1.0, None)
    e_scalar = ExchangeTruth("t", "finalized", "scalar", 0.55, None)
    assert reconcile(s, e_yes, True)["consistent"]
    assert not reconcile(s, e_yes, False)["consistent"]
    assert not reconcile(s, e_scalar, True)["consistent"]
    wo = SportsTruth("m1", "A", "B", "WALKOVER", "W/O", confidence=0.95)
    assert reconcile(wo, e_scalar, True)["consistent"]
    assert not wo.gradeable_binary and s.gradeable_binary
