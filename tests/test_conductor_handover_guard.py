"""A horizon-conductor link never hands over to its successor on top of a horizon trigger.

Readiness audit 2026-09-26: the chain's projected hand-off on Sunday ~23:51Z lands on the SNF T-30m trigger at
23:50Z. Between one link exiting and its successor's first pass there is a 1-2 minute gap, plus up to one pass
interval. The guard only ever moves a link's end EARLIER, to GUARD_BEFORE minutes before the trigger.
"""
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts", "handicap"))

from nfl_edge.handicap.conductor import (  # noqa: E402
    HANDOVER_GUARD_AFTER_MIN, HANDOVER_GUARD_BEFORE_MIN, handover_end,
)

import horizon_conductor as HC  # noqa: E402

UTC = timezone.utc
SNF_T30 = datetime(2026, 9, 27, 23, 50, tzinfo=UTC).timestamp()


def test_the_projected_sunday_night_handover_is_moved_ahead_of_the_snf_t30_trigger():
    natural_end = datetime(2026, 9, 27, 23, 51, tzinfo=UTC).timestamp()
    now = natural_end - 5 * 3600
    end, why = handover_end(natural_end, [SNF_T30], now)
    assert end == SNF_T30 - HANDOVER_GUARD_BEFORE_MIN * 60 and why


def test_an_end_well_clear_of_every_trigger_is_untouched():
    natural_end = SNF_T30 - 30 * 60
    assert handover_end(natural_end, [SNF_T30], natural_end - 3600) == (natural_end, None)
    after = SNF_T30 + (HANDOVER_GUARD_AFTER_MIN + 1) * 60
    assert handover_end(after, [SNF_T30], after - 3600) == (after, None)


def test_the_end_is_never_moved_later():
    for offset_min in range(-20, 21):
        natural_end = SNF_T30 + offset_min * 60
        end, _ = handover_end(natural_end, [SNF_T30], natural_end - 3 * 3600)
        assert end <= natural_end


def test_a_moved_end_that_lands_on_an_earlier_trigger_moves_again():
    t2 = SNF_T30
    t1 = SNF_T30 - 10 * 60                   # a second trigger ten minutes earlier
    end, why = handover_end(t2 + 60, [t1, t2], t2 - 5 * 3600)
    assert end == t1 - HANDOVER_GUARD_BEFORE_MIN * 60 and why


def test_when_the_safe_instant_has_already_passed_the_natural_end_is_kept():
    natural_end = SNF_T30 + 60
    now = SNF_T30 - HANDOVER_GUARD_BEFORE_MIN * 60 + 30     # already inside the guard window
    assert handover_end(natural_end, [SNF_T30], now) == (natural_end, None)


def test_the_conductor_derives_every_horizon_trigger_of_the_active_slate():
    ko = datetime(2026, 9, 28, 0, 20, tzinfo=UTC)
    games = [{"game_id": "2026_03_LA_DEN", "season": 2026, "week": 3, "game_type": "REG", "gameday": "2026-09-27",
              "away_team": "LA", "home_team": "DEN", "kickoff_utc": ko, "has_result": False}]
    trig = HC.horizon_trigger_epochs(games, "test", ko - timedelta(hours=10))
    expected = {(ko - timedelta(minutes=m)).timestamp() for m in (1440, 360, 90, 30)}
    assert set(trig) == expected
