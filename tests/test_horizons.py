"""Decision-horizon gating: fire once per horizon, cluster the Sunday slate, and never lose one to a late cron.

The guarantee being tested is "a FRESH packet exists at T-24h, T-6h, T-90m and T-30m". Three ways to break
it, all of which have obvious-looking implementations:

  * fire the expensive build on every wake, which is the same cost as not gating at all;
  * fire once per GAME, so a nine-game Sunday cluster produces nine identical full-slate builds;
  * use a strict window, so a GitHub cron that fires eleven minutes late silently deletes the horizon.

And one way to break it that is worse than all three: consume the horizon in the gate, before knowing
whether the build worked. Then a flaky runner permanently costs a decision moment. Capture is recorded only
by `mark_captured`, which the workflow calls after a verified build.
"""
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.handicap.horizons import (  # noqa: E402
    HORIZONS_MIN, cluster_kickoffs, due_horizons, horizon_id, mark_captured, parse_horizon_id, prune,
)

SLATE = "2026-REG-01"
SUNDAY_EARLY = "2026-09-13T17:00:00+00:00"          # nine games at 1:00pm ET
SUNDAY_LATE_A = "2026-09-13T20:05:00+00:00"         # 4:05pm ET
SUNDAY_LATE_B = "2026-09-13T20:25:00+00:00"         # 4:25pm ET -- same decision moment
SUNDAY_NIGHT = "2026-09-14T00:20:00+00:00"


def at(iso):
    return datetime.fromisoformat(iso.replace("Z", "+00:00"))


def games(*specs):
    return [{"game_id": gid, "kickoff_utc": ko} for gid, ko in specs]


SLATE_GAMES = games(
    *[(f"2026_01_G{i}", SUNDAY_EARLY) for i in range(9)],
    ("2026_01_LATE_A", SUNDAY_LATE_A),
    ("2026_01_LATE_B", SUNDAY_LATE_B),
    ("2026_01_SNF", SUNDAY_NIGHT),
)


# ------------------------------------------------------------------------------------- clustering

def test_a_shared_kickoff_is_one_cluster_not_nine_runs():
    clusters = cluster_kickoffs(SLATE_GAMES)
    keys = [c["cluster_key"] for c in clusters]
    assert keys == ["20260913T1700Z", "20260913T2005Z", "20260914T0020Z"]
    assert clusters[0]["games"] == 9


def test_the_405_and_425_windows_are_one_decision_moment():
    clusters = cluster_kickoffs(games(("a", SUNDAY_LATE_A), ("b", SUNDAY_LATE_B)))
    assert len(clusters) == 1
    assert clusters[0]["cluster_key"] == "20260913T2005Z"      # keyed by the EARLIEST kickoff
    assert clusters[0]["games"] == 2


def test_kickoffs_hours_apart_are_separate_clusters():
    assert len(cluster_kickoffs(games(("a", SUNDAY_EARLY), ("b", SUNDAY_LATE_A)))) == 2


def test_games_without_a_kickoff_have_no_horizon():
    assert cluster_kickoffs([{"game_id": "x", "kickoff_utc": None}]) == []


# ------------------------------------------------------------------------------------- triggering

def test_nothing_is_due_long_before_the_first_horizon():
    r = due_horizons(SLATE, SLATE_GAMES, at("2026-09-10T00:00:00Z"), {})
    assert r["should_run"] is False
    assert r["next_pending"]["horizon_min"] == 24 * 60


def test_the_24_hour_horizon_becomes_due_on_time():
    trigger = at(SUNDAY_EARLY) - timedelta(minutes=24 * 60)
    before = due_horizons(SLATE, SLATE_GAMES, trigger - timedelta(minutes=1), {})
    after = due_horizons(SLATE, SLATE_GAMES, trigger + timedelta(minutes=1), {})
    assert before["should_run"] is False
    assert after["should_run"] is True
    assert after["due"][0]["horizon_id"] == horizon_id(SLATE, "20260913T1700Z", 1440)


def test_one_build_satisfies_every_due_horizon_for_a_cluster():
    """A conductor that has been down since Friday wakes at T-25m. It owes one report, not four."""
    r = due_horizons(SLATE, games(("g", SUNDAY_EARLY)), at("2026-09-13T16:35:00Z"), {})
    assert r["should_run"] is True
    assert [d["horizon_min"] for d in r["due"]] == [30, 90, 360, 1440]
    assert r["due"][0]["horizon_min"] == 30, "the tightest horizon is the reason to run"


def test_a_late_cron_still_captures_the_horizon():
    """T-90m evaluated 11 minutes late is still the T-90m capture. A strict window would drop it."""
    now = at(SUNDAY_EARLY) - timedelta(minutes=79)
    r = due_horizons(SLATE, games(("g", SUNDAY_EARLY)), now, {})
    due = {d["horizon_min"]: d for d in r["due"]}
    assert 90 in due
    assert due[90]["late_by_min"] == 11.0


def test_after_kickoff_a_horizon_is_missed_not_due():
    r = due_horizons(SLATE, games(("g", SUNDAY_EARLY)), at("2026-09-13T17:30:00Z"), {})
    assert r["should_run"] is False
    assert {m["horizon_min"] for m in r["missed"]} == set(HORIZONS_MIN)


def test_a_slate_with_no_scheduled_kickoff_never_triggers():
    r = due_horizons(SLATE, [{"game_id": "x", "kickoff_utc": None}], at("2026-09-13T16:00:00Z"), {})
    assert r["should_run"] is False and r["due"] == []


# ------------------------------------------------------------------------------------- idempotency

def test_a_captured_horizon_does_not_fire_again():
    now = at(SUNDAY_EARLY) - timedelta(minutes=85)
    first = due_horizons(SLATE, games(("g", SUNDAY_EARLY)), now, {})
    state = mark_captured({}, first["due"], run_id="1", now=now)
    second = due_horizons(SLATE, games(("g", SUNDAY_EARLY)), now + timedelta(minutes=5), state)
    assert first["should_run"] is True
    assert second["should_run"] is False, "the same horizons fired twice"


def test_capture_is_recorded_only_by_mark_captured_not_by_the_gate():
    """The gate must be side-effect free: a failed build has to leave the horizon due."""
    state = {}
    now = at(SUNDAY_EARLY) - timedelta(minutes=85)
    due_horizons(SLATE, games(("g", SUNDAY_EARLY)), now, state)
    assert state == {}, "the gate mutated the capture state"
    again = due_horizons(SLATE, games(("g", SUNDAY_EARLY)), now, state)
    assert again["should_run"] is True


def test_the_horizon_id_is_derived_and_stable():
    a = due_horizons(SLATE, SLATE_GAMES, at("2026-09-13T15:35:00Z"), {})
    b = due_horizons(SLATE, list(reversed(SLATE_GAMES)), at("2026-09-13T15:36:00Z"), {})
    assert {d["horizon_id"] for d in a["due"]} == {d["horizon_id"] for d in b["due"]}


def test_horizon_ids_round_trip_between_workflow_jobs():
    hid = horizon_id(SLATE, "20260913T1700Z", 90)
    p = parse_horizon_id(hid)
    assert p["slate_id"] == SLATE and p["horizon_min"] == 90
    assert p["kickoff_utc"] == "2026-09-13T17:00:00+00:00"
    assert p["trigger_utc"] == "2026-09-13T15:30:00+00:00"


def test_a_later_cluster_is_unaffected_by_an_earlier_capture():
    now = at(SUNDAY_EARLY) - timedelta(minutes=85)
    state = mark_captured({}, due_horizons(SLATE, SLATE_GAMES, now, {})["due"], now=now)
    later = due_horizons(SLATE, SLATE_GAMES, at(SUNDAY_LATE_A) - timedelta(minutes=88), state)
    assert later["should_run"] is True
    # The 1pm cluster is captured and silent; the 4:05 cluster's T-90m is what is owed now, and the
    # Sunday-night game's T-24h rides along on the same build rather than costing a second one.
    assert later["due"][0]["cluster_key"] == "20260913T2005Z"
    assert later["due"][0]["horizon_min"] == 90
    assert "20260913T1700Z" not in {d["cluster_key"] for d in later["due"]}


def test_pruning_drops_old_kickoffs_and_keeps_current_ones():
    now = at("2026-11-01T00:00:00Z")
    state = mark_captured({}, [
        {"horizon_id": "old|20260913T1700Z|T-30m", "horizon_min": 30,
         "kickoff_utc": SUNDAY_EARLY, "trigger_utc": SUNDAY_EARLY},
        {"horizon_id": "new|20261101T1700Z|T-30m", "horizon_min": 30,
         "kickoff_utc": "2026-11-01T17:00:00+00:00", "trigger_utc": "2026-11-01T16:30:00+00:00"},
    ], now=now)
    kept = prune(state, now, keep_days=30)["captured"]
    assert list(kept) == ["new|20261101T1700Z|T-30m"]


def test_a_full_sunday_produces_one_run_per_cluster_per_horizon_and_no_more():
    """The count that matters: 12 games, 3 clusters, 4 horizons -> 12 builds across the day, not 48."""
    state, builds = {}, 0
    t = at(SUNDAY_EARLY) - timedelta(hours=30)
    end = at(SUNDAY_NIGHT)
    while t <= end:
        r = due_horizons(SLATE, SLATE_GAMES, t, state)
        if r["should_run"]:
            builds += 1
            state = mark_captured(state, r["due"], now=t)
        t += timedelta(minutes=15)
    assert builds == 12, f"expected 3 clusters x 4 horizons = 12 builds, got {builds}"
    assert len(state["captured"]) == 12
