"""Full-position executability. The top of book is not a position price.

    approved stake   $50
    best ask         56c for 1 contract
    next liquidity   59c, then 60c

Calling that a "56c position" is false, and false in the flattering direction: the displayed price is the
cheapest contract you will buy and every other one costs more. A desk that sizes against top-of-book pays
more than it recorded, systematically, on exactly the thin books where it thought it had found something.

These tests pin the walk, the fail-closed cases, and -- most importantly -- the book orientation, which was
established empirically rather than assumed.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nfl_edge.execution import depth as D  # noqa: E402

AS_OF = datetime(2026, 9, 9, 13, 0, tzinfo=timezone.utc)
TICKER = "KXNFLGAME-26SEP09NESEA-SEA"


def book(yes_asks, observed=None, yes_bids=(("0.5000", "10"),)):
    """A capture-shaped book from a YES ask ladder. Asks are stored as the NO bids the exchange returns."""
    return {"ticker": TICKER, "run_id": "run",
            "observed_at": (observed or AS_OF - timedelta(minutes=2)).isoformat(),
            "orderbook_fp": {"no_dollars": [[f"{1 - p:.4f}", f"{s}"] for p, s in
                                            sorted(yes_asks, key=lambda x: -x[0])],
                             "yes_dollars": [list(b) for b in yes_bids]}}


class FakeIndex:
    def __init__(self, row):
        self.row = row

    def latest_book(self, ticker, as_of):
        if self.row is None:
            return None
        ts = datetime.fromisoformat(self.row["observed_at"])
        return None if ts > as_of else self.row


# ---- orientation, established empirically -----------------------------------------------------------

def test_the_yes_ask_ladder_is_derived_from_the_no_bids():
    """Kalshi returns resting BIDS per side. A NO bid at q is a YES ask at 1-q.

    Verified against 126 tickers from one real capture run: reconstructing yes_bid and yes_ask this way
    reproduces the separately-captured quote row. Getting this backwards would price every position at the
    wrong end of the book.
    """
    ob = {"no_dollars": [["0.3800", "500"], ["0.4400", "10"]],     # ascending, best (highest) LAST
          "yes_dollars": [["0.5000", "40"], ["0.5600", "20"]]}
    yes = D.ask_ladder(ob, "YES")
    assert yes[0] == (0.56, 10.0), "best NO bid 0.44 -> cheapest YES ask 0.56"
    assert yes[1] == (0.62, 500.0)
    no = D.ask_ladder(ob, "NO")
    assert no[0] == (0.44, 20.0), "best YES bid 0.56 -> cheapest NO ask 0.44"


def test_the_ladder_is_ordered_cheapest_first():
    lad = D.ask_ladder({"no_dollars": [["0.1000", "5"], ["0.4000", "5"], ["0.3000", "5"]]}, "YES")
    assert [p for p, _s in lad] == sorted(p for p, _s in lad)


def test_an_empty_book_yields_an_empty_ladder():
    assert D.ask_ladder({}, "YES") == []
    assert D.ask_ladder({"no_dollars": []}, "YES") == []


# ---- the walk ----------------------------------------------------------------------------------------

def test_the_worked_example_from_the_review():
    """$50 against 56c(1) / 59c(50) / 60c(deep). The position is not a 56c position."""
    lad = D.ask_ladder(book([(0.56, 1), (0.59, 50), (0.60, 100)])["orderbook_fp"], "YES")
    w = D.walk_book(lad, 50.0)
    assert w["filled"] is True
    assert w["vwap"] == pytest.approx(0.5936, abs=0.0005), "the real full-position price, not 0.56"
    assert w["worst_price"] == pytest.approx(0.60)
    assert w["spent"] == pytest.approx(50.0)
    assert len(w["levels_consumed"]) == 3


def test_a_deep_top_level_fills_at_the_top_ask():
    lad = D.ask_ladder(book([(0.56, 100000)])["orderbook_fp"], "YES")
    w = D.walk_book(lad, 50.0)
    assert w["vwap"] == pytest.approx(0.56)
    assert w["worst_price"] == pytest.approx(0.56)
    assert w["contracts"] == pytest.approx(50 / 0.56)


def test_the_walk_budgets_dollars_not_contracts():
    """Contracts are an OUTPUT: later contracts cost more, so `stake / top_ask` would overstate demand."""
    lad = D.ask_ladder(book([(0.50, 10), (0.90, 1000)])["orderbook_fp"], "YES")
    w = D.walk_book(lad, 50.0)
    assert w["spent"] == pytest.approx(50.0)
    naive_contracts = 50 / 0.50
    assert w["contracts"] < naive_contracts, "sizing at the top ask would have demanded more contracts"


def test_a_partial_book_reports_what_it_could_absorb():
    lad = D.ask_ladder(book([(0.56, 10), (0.60, 5)])["orderbook_fp"], "YES")
    w = D.walk_book(lad, 500.0)
    assert w["filled"] is False
    assert w["fillable_stake"] == pytest.approx(0.56 * 10 + 0.60 * 5)


# ---- the gate ----------------------------------------------------------------------------------------

def resolve(row, stake=50.0, **kw):
    return D.resolve_full_position(FakeIndex(row), TICKER, "YES", stake, as_of=AS_OF, **kw)


def test_a_deep_book_is_executable():
    r = resolve(book([(0.56, 100000)]))
    assert r.is_executable and r.state == D.EXECUTABLE
    assert r.top_ask == pytest.approx(0.56) and r.vwap == pytest.approx(0.56)
    assert r.slippage_dollars == pytest.approx(0.0)


def test_a_thin_book_records_the_slippage_it_costs():
    r = resolve(book([(0.56, 1), (0.59, 50), (0.60, 100)]))
    assert r.is_executable
    assert r.top_ask == pytest.approx(0.56)
    assert r.size_at_top_ask == pytest.approx(1.0)
    assert r.vwap > r.top_ask
    assert r.worst_price == pytest.approx(0.60)
    assert r.slippage_probability == pytest.approx(r.vwap - r.top_ask)
    assert r.slippage_dollars > 0


def test_a_book_too_thin_for_the_stake_fails_closed():
    r = resolve(book([(0.56, 10)]), stake=500.0)
    assert not r.is_executable and r.state == D.INSUFFICIENT_DEPTH
    assert "can absorb only" in r.reason


def test_a_walk_above_the_ceiling_fails_closed():
    """Filling the stake would pay more than the record authorises, even though the top ask does not."""
    r = resolve(book([(0.56, 1), (0.70, 10000)]), bet_up_to=0.59)
    assert not r.is_executable and r.state == D.INSUFFICIENT_DEPTH
    assert "above bet_up_to_probability" in r.reason


def test_a_walk_that_stays_under_the_ceiling_passes():
    r = resolve(book([(0.56, 1), (0.58, 10000)]), bet_up_to=0.59)
    assert r.is_executable and r.worst_price <= 0.59


def test_no_book_fails_closed_rather_than_using_top_of_book():
    r = resolve(None)
    assert r.state == D.NO_BOOK and not r.is_executable
    assert "not a substitute" in r.reason


def test_a_book_captured_after_the_decision_is_invisible():
    r = resolve(book([(0.56, 100000)], observed=AS_OF + timedelta(minutes=5)))
    assert r.state == D.NO_BOOK, "post-decision depth is not evidence the decision could have used"


def test_a_stale_book_fails_closed():
    r = resolve(book([(0.56, 100000)], observed=AS_OF - timedelta(minutes=45)))
    assert r.state == D.STALE_BOOK and not r.is_executable
    assert r.book_age_minutes == pytest.approx(45.0, abs=0.1)


def test_book_age_is_measured_from_the_decision_not_wall_clock():
    r = resolve(book([(0.56, 100000)], observed=AS_OF - timedelta(minutes=3)))
    assert r.book_age_minutes == pytest.approx(3.0, abs=0.1)
    assert r.as_of == AS_OF.isoformat()


def test_the_book_uses_its_own_observed_at_not_the_runs():
    """Books are fetched after quotes within a run -- in all 126 cases of the run this was verified against
    -- so a run-level timestamp would claim the book existed before it did."""
    row = book([(0.56, 100000)], observed=AS_OF - timedelta(minutes=1))
    row["run_id"] = "20260909T124000Z"          # run started 20 minutes before the book was fetched
    r = resolve(row)
    assert r.book_age_minutes == pytest.approx(1.0, abs=0.1)
    assert r.book_observed_at == row["observed_at"]


# ---- what the record shows ---------------------------------------------------------------------------

def test_the_record_distinguishes_top_ask_from_vwap_from_worst():
    """The display can stay 'Current: 56%'. The record must not pretend that is the position price."""
    r = resolve(book([(0.56, 1), (0.59, 50), (0.60, 100)]))
    d = r.to_dict()
    for k in ("top_ask", "vwap", "worst_price", "size_at_top_ask", "contracts_required",
              "slippage_dollars", "levels_consumed"):
        assert k in d and d[k] is not None, f"the depth record must carry {k}"
    assert d["top_ask"] < d["vwap"] < d["worst_price"]
