"""Packet-construction invariants.

Two of these tests exist because the bug they pin was actually shipped and found in the dry run: pooling
Kalshi's period ladders produced an "implied total" of 7.7 points for an NFL game, and untraded 0.00/0.99
books took every top slot in the disagreement ranking because their midpoint is a quoting artefact.
"""
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nfl_edge.handicap import packet as P  # noqa: E402


def _row(**kw):
    d = dict(ticker="T", family="TOTAL", period="FULL", threshold=44.5, mid=0.5,
             yes_bid=0.49, yes_ask=0.51, no_bid=0.49, no_ask=0.51, quote_width=0.02,
             volume=100.0, open_interest=100.0, support_state="SUPPORTED",
             model_contract_value=0.55, team=None, home_team="SEA", away_team="NE")
    d.update(kw)
    return d


# ---- period scoping --------------------------------------------------------------------------------

def test_period_ladders_are_never_pooled():
    """A quarter total and a full-game total sit on different scales; pooling them is nonsense."""
    rows = []
    for k, p in ((37.5, 0.80), (44.5, 0.50), (51.5, 0.20)):
        rows.append(_row(family="TOTAL", period="FULL", threshold=k, mid=p))
    for k, p in ((6.5, 0.75), (10.5, 0.35)):
        rows.append(_row(family="TOTAL", period="1Q", threshold=k, mid=p))
    full = P.game_market_implied(rows, "SEA", "NE", "FULL")
    assert 40 < full["implied_total_median"] < 50, \
        f"full-game total {full['implied_total_median']} was contaminated by quarter ladders"


def test_away_spread_rungs_enter_as_complements():
    """An away rung at strike s is P(-M > s); on the home axis that is S(-s) = 1 - quote."""
    rows = [_row(family="SPREAD", team="SEA", threshold=3.5, mid=0.50),
            _row(family="SPREAD", team="SEA", threshold=7.5, mid=0.30),
            _row(family="SPREAD", team="NE", threshold=3.5, mid=0.30)]
    out = P.game_market_implied(rows, "SEA", "NE", "FULL")
    xs, S = out["margin_distribution"]["thresholds"], None
    assert "-3.5" in xs and xs["-3.5"] == pytest.approx(0.70), \
        "an away quote of 0.30 must appear as S(-3.5) = 0.70"


# ---- untraded books --------------------------------------------------------------------------------

def test_untraded_book_is_not_treated_as_a_price():
    m = P.market_row(_row(yes_bid=0.0, yes_ask=0.99, no_bid=0.01, no_ask=1.0, mid=0.495,
                          quote_width=0.99, volume=0.0, open_interest=0.0))
    assert m["no_real_market"] is True
    assert m["tradable_for_disagreement_ranking"] is False
    assert any("no real market" in f for f in m["flags"])


def test_tight_traded_book_is_rankable():
    m = P.market_row(_row())
    assert m["no_real_market"] is False
    assert m["tradable_for_disagreement_ranking"] is True


def test_wide_book_with_real_volume_is_shown_but_not_ranked():
    """Width alone does not make a book fake -- but it does make its midpoint unfit for ranking."""
    m = P.market_row(_row(yes_bid=0.45, yes_ask=0.94, quote_width=0.49, volume=1500.0, open_interest=1500.0))
    assert m["tradable_for_disagreement_ranking"] is False
    assert m["model_probability"] is not None, "the market must still be present with its model view"


def test_disagreement_is_never_called_edge():
    m = P.market_row(_row())
    assert "DISAGREEMENT" in m["disagreement_label"]
    assert not any(k.startswith("edge") for k in m), "no field may be named edge"


# ---- survival summaries ----------------------------------------------------------------------------

def test_ladder_mean_is_labelled_a_lower_bound():
    out = P._survival_summary([(10, 0.9), (20, 0.6), (30, 0.3), (40, 0.1)])
    assert "mean_lower_bound" in out and "mean" not in out, \
        "a truncated ladder cannot yield a mean, only a lower bound"


def test_survival_is_monotonised():
    out = P._survival_summary([(10, 0.5), (20, 0.8), (30, 0.2)])
    ps = list(out["thresholds"].values())
    assert all(b <= a for a, b in zip(ps, ps[1:])), f"survival not monotone: {ps}"
    assert out["monotonicity_violations"] == 1, "the violation should be reported, not hidden"


def test_thin_ladder_is_refused():
    assert P._survival_summary([(10, 0.5)])["insufficient_ladder"] is True


# ---- movement --------------------------------------------------------------------------------------

def _now():
    return datetime(2026, 9, 8, 12, 0, tzinfo=timezone.utc)


def test_movement_distinguishes_not_captured_from_not_yet_reached():
    kickoff = _now() + timedelta(hours=36)
    series = {"T": [((_now() - timedelta(hours=2)).isoformat(), 0.50, 0.49, 0.51)]}
    mv = P.movement_for("T", series, kickoff, _now())
    # T-72h is before our first capture AND already in the past -> not captured
    assert mv["horizons"]["T-72h"]["reason"] == "no capture before this horizon"
    # T-24h has not happened yet (kickoff is 36h away)
    assert mv["horizons"]["T-24h"]["reason"] == "horizon not yet reached"


def test_movement_never_interpolates():
    kickoff = _now() + timedelta(hours=1)
    series = {"T": [((_now() - timedelta(hours=10)).isoformat(), 0.40, 0.39, 0.41),
                    ((_now() - timedelta(minutes=5)).isoformat(), 0.60, 0.59, 0.61)]}
    mv = P.movement_for("T", series, kickoff, _now())
    for h in mv["horizons"].values():
        if h.get("observed"):
            assert h["mid"] in (0.40, 0.60), f"{h['mid']} is not an observed value"


def test_first_observation_is_not_called_the_open():
    kickoff = _now() + timedelta(hours=1)
    series = {"T": [((_now() - timedelta(hours=3)).isoformat(), 0.4, 0.39, 0.41)]}
    mv = P.movement_for("T", series, kickoff, _now())
    assert "not the market open" in mv["first_observed"]["label"]


# ---- availability vocabularies ---------------------------------------------------------------------

def test_feed_vocabularies_are_reconciled():
    """ESPN 'Injured Reserve' and Sleeper 'IR' are the same fact; so are 'Out' and 'PUP'."""
    assert P._canon_availability("Injured Reserve") == P._canon_availability("IR") == "OUT"
    assert P._canon_availability("Out") == P._canon_availability("PUP") == "OUT"
    assert P._canon_availability("Questionable") == "QUESTIONABLE"
    assert P._canon_availability("Active") == "ACTIVE"
    assert P._canon_availability("something else") == "UNKNOWN"
