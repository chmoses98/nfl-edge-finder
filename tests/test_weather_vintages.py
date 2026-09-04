"""Weather forecast vintages: the point-in-time replacement for observed wind.

The existing wind result (H-006) used wind observed during the game, which cannot be known beforehand. These
tests cover the vintage extractor that makes a prospective version possible, and pin the capture window that
determines whether long-lead vintages exist at all.
"""
import os
import re

from nfl_edge.context.weather_vintages import kickoff_forecast, latest_before

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rec(run_id="20260904T121643Z", kickoff="2026-09-10T00:20:00+00:00", times=None, wind=None):
    times = times or ["2026-09-09T22:00", "2026-09-09T23:00", "2026-09-10T00:00", "2026-09-10T01:00"]
    wind = wind or [5.0, 6.0, 7.0, 8.0]
    return {"run_id": run_id, "game_id": "2026_01_NE_SEA", "kickoff_utc": kickoff, "roof": "outdoors",
            "open_meteo": {"hourly": {"time": times, "wind_speed_10m": wind,
                                      "temperature_2m": [70.0] * len(times)}}}


def test_picks_the_hour_containing_kickoff():
    f = kickoff_forecast(rec())
    assert f["forecast_hour"] == "2026-09-10T00:00"
    assert f["wind_speed_10m"] == 7.0


def test_lead_hours_is_measured_from_the_capture_not_from_now():
    f = kickoff_forecast(rec())
    assert 131 < f["lead_hours"] < 133, "lead time must come from run_id, so a vintage is self-describing"


def test_a_forecast_that_does_not_reach_kickoff_is_refused():
    """Better no vintage than one silently taken from hours away from kickoff."""
    assert kickoff_forecast(rec(times=["2026-09-08T00:00"], wind=[5.0])) is None


def test_dome_games_with_no_hourly_data_yield_nothing():
    r = rec(); r["open_meteo"]["hourly"] = {"time": [], "wind_speed_10m": []}
    assert kickoff_forecast(r) is None


def test_point_in_time_accessor_never_returns_a_later_vintage():
    early = kickoff_forecast(rec(run_id="20260901T120000Z"))
    late = kickoff_forecast(rec(run_id="20260908T120000Z", wind=[9.0, 9.0, 20.0, 9.0]))
    got = latest_before([early, late], "2026_01_NE_SEA", "2026-09-04T00:00:00Z")
    assert got["run_id"] == "20260901T120000Z", "a study must not see a forecast issued after its cutoff"
    got2 = latest_before([early, late], "2026_01_NE_SEA", "2026-09-09T00:00:00Z")
    assert got2["run_id"] == "20260908T120000Z"


def test_capture_window_reaches_a_full_week_before_sunday_games():
    """A 7-day window captured 2 of Week 1's 16 games; a Sunday game is 9-10 days out on the prior Sunday."""
    src = open(os.path.join(ROOT, "scripts", "data", "context_capture.py")).read()
    m = re.search(r"WEATHER_LOOKAHEAD_DAYS\s*=\s*(\d+)", src)
    assert m and int(m.group(1)) >= 9, "lookahead too short to record a 7-day-lead vintage for Sunday games"
    fd = re.search(r"forecast_days=(\d+)", src)
    assert fd and int(fd.group(1)) >= int(m.group(1)), \
        "open-meteo forecast_days must cover the whole capture window or kickoff falls outside the response"
