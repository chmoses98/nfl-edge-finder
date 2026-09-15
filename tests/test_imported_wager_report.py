"""The summary is about a BANKROLL, and must not be readable as a model result.

A won-lost record computed from `imported_wagers` is indistinguishable, at a
glance, from the number the scorecard produces for the model. The difference is
that the model had no part in any of these bets -- and a difference that exists
only in a docstring is one that gets lost the first time somebody pastes the
output into a weekly summary.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts", "handicap"))

from nfl_edge.handicap import imported_wager_report as report  # noqa: E402


def wager(**overrides):
    row = {
        "imported_wager_id": "routed-abc",
        "source_bet_key": "kalshi:v1:a",
        "season": 2026,
        "week": 2,
        "market_ticker": "KXNFLGAME-26SEP14KCBUF-KC",
        "side": "YES",
        "contracts": 40.0,
        "actual_price": 0.61,
        "stake": 24.68,
        "fees_paid": 0.28,
        "fees_are_estimated": False,
    }
    row.update(overrides)
    return row


def test_the_warning_is_data_and_is_printed_before_any_number():
    summary = report.summarize([wager()], 2026)

    assert "not evidence about the NFL model" in summary.not_model_evidence
    assert report.render(summary).startswith(report.NOT_MODEL_EVIDENCE)


def test_the_money_is_the_ledgers_money():
    summary = report.summarize([wager(), wager(source_bet_key="kalshi:v1:b")], 2026)

    assert summary.wagers == 2
    assert summary.contracts == 80.0
    assert round(summary.staked, 2) == 49.36
    assert round(summary.fees_paid, 2) == 0.56


def test_weeks_are_reported_because_the_reports_are_read_by_week():
    summary = report.summarize(
        [wager(), wager(week=3), wager(week=3)], 2026
    )

    assert summary.by_week == {2: 1, 3: 2}
    assert "week 3: 2" in report.render(summary)


def test_an_unsettled_wager_is_counted_as_unsettled_not_as_a_loss():
    """Unknown counted as a loss would overstate a drawdown that never
    happened."""
    summary = report.summarize([wager()], 2026)

    assert (summary.settled, summary.unsettled) == (0, 1)
    assert (summary.won, summary.lost) == (0, 0)


def test_a_partial_profit_and_loss_is_never_stated_as_the_seasons():
    """A total covering three of twenty-four wagers, printed beside "wagers
    recorded: 24", will be read as covering all of them."""
    rows = [
        wager(settlement_status="SETTLED", result="WON", net_profit_loss=5.00),
        wager(source_bet_key="kalshi:v1:b"),
    ]
    summary = report.summarize(rows, 2026)

    assert summary.profit_loss_is_complete is False
    rendered = report.render(summary)
    assert "UNESTABLISHED for 1 of 2 wagers" in rendered
    assert "+5.00" not in rendered, rendered


def test_a_complete_profit_and_loss_is_stated():
    """The positive control: otherwise the test above passes against a renderer
    that never prints a total at all."""
    rows = [
        wager(settlement_status="SETTLED", result="WON", net_profit_loss=5.00),
        wager(source_bet_key="kalshi:v1:b", settlement_status="SETTLED",
              result="LOST", net_profit_loss=-24.68),
    ]
    summary = report.summarize(rows, 2026)

    assert summary.profit_loss_is_complete is True
    assert "-19.68 (every wager established)" in report.render(summary)


def test_an_estimated_fee_is_called_out():
    """The schema already refuses a realised P&L built on a modelled fee. This
    makes the modelled fee visible even where no P&L is claimed."""
    summary = report.summarize([wager(fees_are_estimated=True)], 2026)

    assert summary.fees_estimated_on == 1
    assert "fees ESTIMATED on 1 wager(s)" in report.render(summary)


def test_two_wagers_on_one_market_and_side_are_visible():
    """A Kalshi settlement is per market and per position, not per order, so
    where two orders share a market and side one payout covers both. The count
    has to be visible before anyone states a per-wager return."""
    summary = report.summarize([wager(), wager(source_bet_key="kalshi:v1:b")], 2026)

    assert summary.wagers == 2
    assert len(summary.markets) == 1


def test_the_report_is_not_read_by_anything_that_grades_the_model():
    """The kind's own invariant, re-asserted now that a reader finally exists.

    Adding the first reader of `imported_wagers` is exactly when this could be
    broken by accident.
    """
    from tests.test_imported_wager_accounting import _modules_reading

    readers = _modules_reading("imported_wagers")
    forbidden = {
        "scripts/handicap/scorecard.py",
        "nfl_edge/handicap/scorecard.py",
        "nfl_edge/handicap/evaluate.py",
        "nfl_edge/handicap/risk.py",
        "scripts/handicap/attach_evaluations.py",
    }

    assert not (readers & forbidden), sorted(readers & forbidden)
    assert "scripts/handicap/report_imported_wagers.py" in readers, (
        "the accounting report should be a reader; if it is not, the detector "
        "is broken and the assertion above proves nothing"
    )


def test_a_kind_that_was_never_written_is_not_a_season_with_no_wagers(tmp_path, capsys):
    import report_imported_wagers as script

    assert script.main([
        "--handicap-root", str(tmp_path), "--season", "2026",
    ]) == 1
    assert "no imported_wagers records" in capsys.readouterr().err
