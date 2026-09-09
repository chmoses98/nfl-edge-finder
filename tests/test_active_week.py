"""Active-week resolution: the fact that made RUN NFL a manual chore, tested at its boundaries.

`run_nfl.py` defaulted to `--season 2026 --week 1`, so a workflow that called it in October would have
confidently rebuilt September's slate. Automating the report means nothing unless the question "which week
is live?" has an answer that is derived, boundary-correct and willing to say "none".

The cases below are the ones that actually go wrong: the Thursday before kickoff, the Sunday afternoon
mid-slate, the small hours of Monday when Sunday's games are over but Monday night's is not, the rollover
after a week completes, the playoffs (which nflverse numbers as weeks 19-22 and which must never come back
labelled as regular-season week 19), and the offseason.
"""
import os
import sys
from datetime import datetime, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.data.nfl_calendar import (  # noqa: E402
    eastern_offset_hours, kickoff_utc, parse_schedule, resolve_active_week, season_type_of, week_blocks,
)

HEADER = "game_id,season,game_type,week,gameday,weekday,gametime,away_team,home_team,result\n"


def csv(rows):
    out = HEADER
    for r in rows:
        out += ",".join(str(x) for x in r) + "\n"
    return out


def week(n, day, time="13:00", away="AAA", home="BBB", season=2026, gt="REG", result=""):
    return (f"{season}_{n:02d}_{away}_{home}", season, gt, n, day, "Sunday", time, away, home, result)


# One tidy two-week regular season plus a playoff round, with the shapes that matter: a Thursday opener, a
# Sunday cluster, a Monday nighter.
SCHEDULE = csv([
    week(1, "2026-09-10", "20:15", "AAA", "BBB"),          # Thu 2026-09-11 00:15Z
    week(1, "2026-09-13", "13:00", "CCC", "DDD"),          # Sun 17:00Z
    week(1, "2026-09-13", "13:00", "EEE", "FFF"),
    week(1, "2026-09-14", "20:15", "GGG", "HHH"),          # Mon 2026-09-15 00:15Z
    week(2, "2026-09-17", "20:15", "AAA", "CCC"),          # Thu 2026-09-18 00:15Z
    week(2, "2026-09-20", "13:00", "BBB", "DDD"),
    (2026 and "2026_19_III_JJJ", 2026, "WC", 19, "2027-01-09", "Saturday", "16:30", "III", "JJJ", ""),
])


def at(iso):
    return datetime.fromisoformat(iso.replace("Z", "+00:00"))


def resolve(iso, text=SCHEDULE):
    return resolve_active_week(parse_schedule(text), at(iso))


# ---------------------------------------------------------------------------------- time conversion

def test_eastern_offset_follows_dst():
    assert eastern_offset_hours(datetime(2026, 9, 13, 13, 0)) == 4      # EDT
    assert eastern_offset_hours(datetime(2026, 12, 13, 13, 0)) == 5     # EST
    assert eastern_offset_hours(datetime(2027, 1, 9, 16, 30)) == 5      # EST, playoff Saturday


def test_kickoff_converts_eastern_to_utc():
    assert kickoff_utc("2026-09-09", "20:20") == datetime(2026, 9, 10, 0, 20, tzinfo=timezone.utc)
    assert kickoff_utc("2026-09-09", "") is None
    assert kickoff_utc("", "20:20") is None


# ---------------------------------------------------------------------------------- resolution

def test_before_the_first_kickoff_resolves_to_that_upcoming_week():
    r = resolve("2026-09-08T12:00:00Z")
    assert (r["status"], r["season"], r["week"], r["season_type"]) == ("OK", 2026, 1, "REG")
    assert r["minutes_to_first_kickoff"] > 0
    assert r["games_started"] == 0 and r["games_upcoming"] == 4


def test_between_the_opener_and_sunday_it_is_still_that_week():
    r = resolve("2026-09-11T18:00:00Z")     # opener played; Sunday and Monday still to come
    assert (r["week"], r["slate_in_progress"]) == (1, True)
    assert r["games_started"] == 1


def test_mid_sunday_slate_stays_on_the_week_it_is_playing():
    r = resolve("2026-09-13T19:00:00Z")     # 1pm games in progress, Monday night ahead
    assert r["week"] == 1
    assert r["next_kickoff_utc"] == "2026-09-15T00:15:00+00:00"


def test_monday_night_in_progress_does_not_roll_over_early():
    """00:20Z Tuesday is three hours into Monday Night Football. Rolling to week 2 there would hand a
    packet builder the wrong slate while a game is still being played."""
    r = resolve("2026-09-15T03:00:00Z")
    assert r["week"] == 1


def test_once_the_week_is_complete_it_rolls_to_the_next_one():
    r = resolve("2026-09-15T06:00:00Z")     # last kickoff + >4h
    assert (r["status"], r["week"]) == ("OK", 2)
    assert r["games_scheduled"] == 2


def test_rollover_is_exactly_at_last_kickoff_plus_the_runtime_allowance():
    just_before = resolve("2026-09-15T04:14:00Z")
    just_after = resolve("2026-09-15T04:16:00Z")
    assert (just_before["week"], just_after["week"]) == (1, 2)


def test_postseason_is_never_reported_as_a_regular_season_week():
    r = resolve("2027-01-08T12:00:00Z")
    assert r["season_type"] == "POST"
    assert r["week"] == 19                       # nflverse numbering is preserved ...
    assert "postseason" in r["label"]            # ... but the label can never be mistaken for REG 19
    assert r["round"] == "Wild Card"
    assert r["slate_id"] == "2026-POST-19"


def test_regular_and_post_season_week_19_are_distinct_slates():
    blocks = {b["slate_id"] for b in week_blocks(parse_schedule(csv([
        week(19, "2026-12-27", "13:00"),
        ("2026_19_III_JJJ", 2026, "WC", 19, "2027-01-09", "Saturday", "16:30", "III", "JJJ", ""),
    ])))}
    assert blocks == {"2026-REG-19", "2026-POST-19"}


def test_the_offseason_refuses_rather_than_guessing():
    r = resolve("2027-06-01T12:00:00Z")
    assert r["status"] == "NO_SLATE"
    assert r["season"] is None and r["week"] is None
    assert "offseason" in r["reason"]


def test_an_empty_schedule_refuses():
    r = resolve_active_week([], at("2026-09-08T12:00:00Z"))
    assert r["status"] == "NO_SLATE" and r["reason"]


def test_a_week_whose_kickoff_times_are_not_published_refuses_to_guess():
    """nflverse publishes a season's games before all of their times. A block with no kickoff at all is
    'not scheduled yet', which is a refusal -- not a licence to assume Sunday at one o'clock."""
    text = csv([
        week(1, "2026-09-13", "13:00"),
        ("2026_02_XXX_YYY", 2026, "REG", 2, "2026-09-20", "Sunday", "", "XXX", "YYY", ""),
    ])
    r = resolve("2026-09-14T06:00:00Z", text)
    assert r["status"] == "NO_SLATE"
    assert "no kickoff times are published" in r["reason"]
    assert r["week"] == 2                       # it says WHICH week it cannot schedule
    assert r["season_type"] == "REG"


def test_preseason_is_excluded_by_default():
    text = csv([
        ("2026_01_PPP_QQQ", 2026, "PRE", 1, "2026-08-08", "Saturday", "19:00", "PPP", "QQQ", ""),
        week(1, "2026-09-13", "13:00"),
    ])
    r = resolve("2026-08-01T12:00:00Z", text)
    assert (r["status"], r["week"], r["season_type"]) == ("OK", 1, "REG")


@pytest.mark.parametrize("game_type,expected", [
    ("REG", "REG"), ("WC", "POST"), ("DIV", "POST"), ("CON", "POST"), ("SB", "POST"), ("PRE", "PRE"),
])
def test_season_type_mapping(game_type, expected):
    assert season_type_of(game_type) == expected


def test_the_resolution_lists_the_slate_with_kickoffs_in_order():
    r = resolve("2026-09-08T12:00:00Z")
    kicks = [g["kickoff_utc"] for g in r["games"]]
    assert kicks == sorted(kicks)
    assert r["games"][0]["game_id"] == "2026_01_AAA_BBB"
