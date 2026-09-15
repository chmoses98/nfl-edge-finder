"""Imported wagers are accounting. They must never become model evidence.

The danger is not that these records are wrong. It is that they are RIGHT --
real wagers, real money -- and get read by something that reports how well the
NFL model did. A Kalshi execution proves the owner placed a bet. It proves
nothing about what recommended it.
"""
from __future__ import annotations

import ast
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nfl_edge.handicap import store
from nfl_edge.handicap.imported_wagers import (
    ENTRY_METHOD_IMPORTED_RECEIPT,
    FORBIDDEN_PROVENANCE_FIELDS,
    SCHEMA_VERSION,
    ImportedWager,
    validate,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def wager(**overrides):
    base = dict(
        imported_wager_id="iw-1",
        schema_version=SCHEMA_VERSION,
        source_bet_key="kalshi:v1:abc123",
        import_batch_id="kalshi-gap-backfill-v1",
        entry_method=ENTRY_METHOD_IMPORTED_RECEIPT,
        season=2026,
        week=2,
        game_date="2026-09-13",
        market_ticker="KXNFLGAME-26SEP13BUFNYJ-BUF",
        side="YES",
        executed_at="2026-09-13T17:02:11Z",
        contracts=10.0,
        actual_price=0.53,
        stake=5.37,
    )
    base.update(overrides)
    return ImportedWager(**base).to_dict()


# ---------------------------------------------------------------------------
# The record cannot claim provenance it does not have.
# ---------------------------------------------------------------------------


def test_a_valid_imported_wager_passes():
    assert validate(wager()) == []


@pytest.mark.parametrize("field_name", FORBIDDEN_PROVENANCE_FIELDS)
def test_every_recommendation_field_is_refused(field_name):
    """Synthesising one would manufacture exactly the provenance this record is
    supposed to lack -- and would then be indistinguishable, downstream, from a
    bet this system actually called."""
    record = wager()
    record[field_name] = "invented"

    problems = validate(record)

    assert any(field_name in p for p in problems), problems


def test_the_dataclass_itself_has_no_recommendation_field():
    """Validation catches a dict. This catches the schema growing one."""
    for field_name in FORBIDDEN_PROVENANCE_FIELDS:
        assert field_name not in ImportedWager.__dataclass_fields__


def test_entry_method_must_say_imported_receipt():
    assert validate(wager(entry_method="MANUAL")) != []


def test_side_must_be_proven_not_defaulted():
    assert validate(wager(side="")) != []
    assert validate(wager(side="MAYBE")) != []


def test_a_realised_pl_may_not_be_stated_from_estimated_fees():
    """A modelled fee is a fine input to an estimate and an unacceptable input
    to a realised-P/L claim. The schema distinguishes them; this refuses the
    combination that hides it."""
    record = wager(fees_are_estimated=True, net_profit_loss=12.34)

    problems = validate(record)

    assert any("estimated fees" in p for p in problems), problems


def test_an_estimated_fee_without_a_pl_claim_is_fine():
    assert validate(wager(fees_are_estimated=True, fees_paid=0.07)) == []


def test_validate_reports_every_problem_not_just_the_first():
    """So a batch reports what is wrong with it once, not over several tries."""
    record = wager(side="MAYBE", entry_method="MANUAL")
    record["recommendation_id"] = "x"

    assert len(validate(record)) >= 3


# ---------------------------------------------------------------------------
# The kind exists, and nothing that measures the model reads it.
# ---------------------------------------------------------------------------


def test_the_store_knows_the_kind():
    assert "imported_wagers" in store.KINDS
    path = store.record_path("/root", "imported_wagers", 2026, 2, "iw-1")
    assert path.endswith("data/imported_wagers/2026/week_02/iw-1.json")


def _modules_reading(kind: str) -> set[str]:
    """Every source file that names this record kind, found by parsing rather
    than grepping prose, so a mention in a docstring does not count."""
    found = set()
    for base, _dirs, files in os.walk(ROOT):
        if any(part in base for part in (".git", "__pycache__", "/tests")):
            continue
        for name in files:
            if not name.endswith(".py"):
                continue
            path = os.path.join(base, name)
            try:
                tree = ast.parse(open(path).read())
            except (SyntaxError, UnicodeDecodeError):
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and node.value == kind:
                    found.add(os.path.relpath(path, ROOT))
    return found


def test_nothing_that_measures_model_performance_reads_imported_wagers():
    """THE test. These are real wagers the model never called, so a scorecard
    that counted them would report the model's record as including bets it had
    no part in.

    `executions` is listed for contrast: it IS read by the scorecard and the
    risk ledger, which is precisely why imported wagers are a separate kind.
    """
    readers = _modules_reading("imported_wagers")

    forbidden = {
        "scripts/handicap/scorecard.py",
        "nfl_edge/handicap/scorecard.py",
        "nfl_edge/handicap/evaluate.py",
        "nfl_edge/handicap/risk.py",
        "scripts/handicap/attach_evaluations.py",
    }
    assert not (readers & forbidden), (
        f"model-performance code reads imported_wagers: {sorted(readers & forbidden)}"
    )


def test_the_scorecard_really_does_read_executions():
    """Guards the test above against passing because the detector is broken:
    if this cannot find a known reader, the negative result means nothing.
    """
    readers = _modules_reading("executions")

    assert any("scorecard" in r for r in readers), readers
