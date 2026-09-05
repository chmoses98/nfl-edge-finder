"""A surprise inactive must be surprising.

The 2025 detector originally called every non-Out inactive a `surprise_inactive`. That flagged Tommy DeVito
20 times, Stetson Bennett 20 and Philip Rivers once -- third-string quarterbacks whose inactivity is their
expected weekly state. 696 of 1,243 inactives were preceded by another inactive week, so the "precisely
timed news" population was 56% noise (72% at QB), and the session-3 latency result was measured on it.

These tests pin the expectation gate: prior-week ACT is required, only ACT/INA count as evidence, and the
gate may never look forward.
"""
import os
import sys

import polars as pl
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nfl_edge.shocks import detect_2025_availability_shocks  # noqa: E402

pytestmark = pytest.mark.skipif(
    not os.path.exists(os.path.join(ROOT, "data/raw/nflverse/weekly_rosters/roster_weekly_2025.parquet")),
    reason="2025 weekly rosters not present")


@pytest.fixture(scope="module")
def shocks():
    return detect_2025_availability_shocks(ROOT).to_frame()


def test_repeat_inactives_are_not_surprises(shocks):
    """The specific failure: a player inactive in his most recent prior week is routine, never a surprise."""
    surprise = shocks.filter(pl.col("shock_type") == "surprise_inactive")
    assert surprise.height, "no surprise inactives at all -- the gate has over-fired"
    bad = surprise.filter(pl.col("prior_state") == "INA")
    assert bad.height == 0, f"{bad.height} surprises whose prior state was already inactive"


def test_every_surprise_was_active_in_its_prior_week(shocks):
    surprise = shocks.filter(pl.col("shock_type") == "surprise_inactive")
    assert set(surprise["prior_state"].to_list()) <= {"ACT", "Questionable", "Doubtful", "not_on_report"}, \
        "surprise prior_state carries a value the gate should have excluded"


def test_no_career_backup_dominates_the_surprise_set(shocks):
    """A single name appearing 20 times is the signature of the bug, not of a season of news."""
    surprise = shocks.filter(pl.col("shock_type") == "surprise_inactive")
    top = surprise["entity_name"].value_counts().sort("count", descending=True).head(1)
    n = int(top["count"][0])
    assert n <= 8, f"{top['entity_name'][0]!r} appears {n} times; expectation gate is not holding"


def test_routine_and_unknown_are_not_timed_exact(shocks):
    """Only the surprise group has by-rule timing. Nothing else may leak into a latency population."""
    other = shocks.filter(pl.col("shock_type").is_in(["routine_inactive", "unknown_expectation"]))
    assert other.height, "expected some routine/unknown inactives"
    assert set(other["timing_basis"].to_list()) == {"unknown"}, \
        "a non-surprise inactive is claiming exact timing"


def test_ruled_out_stays_calendar_inferred(shocks):
    out = shocks.filter(pl.col("shock_type") == "ruled_out_on_report")
    assert set(out["timing_basis"].to_list()) == {"calendar_inferred"}


def test_week_one_cannot_be_a_surprise(shocks):
    """Week 1 has no prior ACT/INA week, so expectation is unestablished -- it must not be guessed."""
    surprise = shocks.filter(pl.col("shock_type") == "surprise_inactive")
    wk = surprise.with_columns(pl.col("game_id").str.split("_").list.get(1).cast(pl.Int64).alias("week"))
    assert wk.filter(pl.col("week") == 1).height == 0, "a week-1 inactive was called a surprise"
