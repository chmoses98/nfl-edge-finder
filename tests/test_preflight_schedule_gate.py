"""When preflight polling may spend an Airtable request -- derived from the real schedule, never from folklore.

The windows exist for one reason: the owner's Airtable workspace allows 1,000 Web API requests a month, and
a ten-minute poll that ran all day would spend four times that discovering nothing. So a GitHub wake is not
an Airtable call, and this file pins the boundary between them.

Two properties carry the whole design and both are tested adversarially:

  * NOTHING here knows that football is played on Sunday at 1pm. Every window comes from clustering the
    ACTUAL kickoffs, so Thursday, Saturday, Wednesday, Thanksgiving, Christmas, an international morning,
    the postseason and any reschedule work because they are all just kickoffs in the file. The tests build
    synthetic schedules for each and assert the shape that falls out, rather than asserting a weekday.

  * OVERLAPPING WINDOWS UNION. One wake can never authorise more than one Airtable request, however many
    clusters happen to be open. Un-merged, a three-cluster Sunday would triple the bill.

An unreadable schedule is SCHEDULE_ERROR and a non-zero exit -- never a quiet "no window", which would be
indistinguishable from a healthy Tuesday while rows went unanswered.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.data import nfl_calendar as CAL          # noqa: E402
from nfl_edge.handicap import preflight_window as PW   # noqa: E402

GATE = os.path.join(ROOT, "scripts", "handicap", "preflight_window_gate.py")

CSV_HEAD = "game_id,season,game_type,week,gameday,weekday,gametime,away_team,home_team,result\n"


def game(gid, gameday, gametime, *, gtype="REG", week=1, season=2026):
    return f"{gid},{season},{gtype},{week},{gameday},X,{gametime},AAA,BBB,\n"


def sched(rows):
    """A schedule as the loader sees it, built from nflverse-shaped CSV so nothing is faked in memory."""
    return CAL.parse_schedule(CSV_HEAD + "".join(rows))


def at(iso):
    return datetime.fromisoformat(iso).replace(tzinfo=timezone.utc)


def et(gameday, hhmm):
    """The UTC instant of an Eastern wall-clock kickoff, using the repo's own conversion."""
    return CAL.kickoff_utc(gameday, hhmm)


# ---- calendar shapes: every one of these comes from the schedule, not from a weekday rule -------------

def test_a_standalone_thursday_game_gets_the_full_primary_window():
    games = sched([game("g1", "2026-09-10", "20:20")])
    (start, end), = PW.windows(games)
    ko = et("2026-09-10", "20:20")
    assert start == ko - timedelta(minutes=180)
    assert end == ko - timedelta(minutes=10)


def test_a_standalone_monday_game_gets_the_full_primary_window():
    games = sched([game("g1", "2026-09-14", "20:15")])
    (start, end), = PW.windows(games)
    assert (end - start) == timedelta(minutes=170)


@pytest.mark.parametrize("gameday,label", [
    ("2026-09-12", "Saturday"), ("2026-09-16", "Wednesday"), ("2026-09-11", "Friday"),
    ("2026-11-26", "Thanksgiving"), ("2026-12-25", "Christmas"),
])
def test_an_unusual_weekday_is_supported_because_the_schedule_is_authoritative(gameday, label):
    """No weekday is special-cased anywhere, so these need no code of their own to work."""
    games = sched([game("g1", gameday, "13:00")])
    (start, end), = PW.windows(games)
    assert (end - start) == timedelta(minutes=170), label


def test_the_sunday_primary_cluster_is_chosen_by_game_count():
    """Ten 1pm games and one 8:20pm game: the ten-game cluster is the slate, and gets the longer window."""
    rows = [game(f"g{i}", "2026-09-13", "13:00") for i in range(10)]
    rows.append(game("snf", "2026-09-13", "20:20"))
    spans = PW.windows(sched(rows))
    one_pm, snf = et("2026-09-13", "13:00"), et("2026-09-13", "20:20")
    assert (one_pm - timedelta(minutes=180), one_pm - timedelta(minutes=10)) in spans
    assert (snf - timedelta(minutes=120), snf - timedelta(minutes=10)) in spans


def test_405_and_425_are_one_cluster_under_the_existing_thirty_minute_tolerance():
    rows = [game("a", "2026-09-13", "16:05"), game("b", "2026-09-13", "16:25")]
    spans = PW.windows(sched(rows))
    assert len(spans) == 1, "two kickoffs 20 minutes apart must not buy two windows"
    early = et("2026-09-13", "16:05")
    assert spans[0][1] == early - timedelta(minutes=10), "the cluster is keyed by its EARLIEST kickoff"


def test_an_international_morning_is_a_secondary_cluster_of_its_own_game_day():
    rows = [game("intl", "2026-10-04", "09:30")] + \
           [game(f"g{i}", "2026-10-04", "13:00") for i in range(8)]
    spans = PW.windows(sched(rows))
    intl = et("2026-10-04", "09:30")
    assert (intl - timedelta(minutes=120), intl - timedelta(minutes=10)) in spans


def test_a_sunday_night_game_belongs_to_sunday_not_to_monday():
    """It kicks off after 00:00 UTC. Using the schedule's own `gameday` is what keeps it on Sunday.

    This is not cosmetic. Attributed to Monday it would be that day's only cluster, become PRIMARY, and take
    a 3-hour window instead of 2 -- inflating the monthly bill on every single Sunday of the season.
    """
    rows = [game(f"g{i}", "2026-09-13", "13:00") for i in range(9)]
    rows.append(game("snf", "2026-09-13", "20:20"))
    games = sched(rows)
    snf = [c for c in PW.clusters(games) if c["games"] == 1][0]
    assert snf["kickoff_utc"].date().isoformat() == "2026-09-14", "it really is the next UTC day"
    assert snf["game_day"] == "2026-09-13", "but the schedule says Sunday, and the schedule wins"
    ko = snf["kickoff_utc"]
    assert (ko - timedelta(minutes=120), ko - timedelta(minutes=10)) in PW.windows(games)


def test_thanksgiving_and_christmas_multi_cluster_days_get_one_primary_and_the_rest_secondary():
    rows = [game("a", "2026-11-26", "12:30"), game("b", "2026-11-26", "16:30"),
            game("c1", "2026-11-26", "20:20"), game("c2", "2026-11-26", "20:20")]
    spans = PW.windows(sched(rows))
    assert len(spans) == 3
    primary = et("2026-11-26", "20:20")          # the two-game cluster
    assert (primary - timedelta(minutes=180), primary - timedelta(minutes=10)) in spans


def test_a_tie_on_game_count_is_broken_by_the_earliest_kickoff():
    rows = [game("a", "2026-12-25", "13:00"), game("b", "2026-12-25", "16:30")]
    spans = PW.windows(sched(rows))
    early = et("2026-12-25", "13:00")
    assert (early - timedelta(minutes=180), early - timedelta(minutes=10)) in spans


def test_the_postseason_is_just_more_kickoffs():
    games = sched([game("wc", "2027-01-09", "16:30", gtype="WC", week=19)])
    (start, end), = PW.windows(games)
    assert (end - start) == timedelta(minutes=170)


def test_preseason_never_opens_a_window():
    assert PW.windows(sched([game("p", "2026-08-08", "13:00", gtype="PRE", week=1)])) == []


def test_a_game_with_no_kickoff_time_opens_no_window():
    assert PW.windows(sched([game("tbd", "2026-09-13", "")])) == []


def test_a_degenerate_configuration_yields_no_window_rather_than_an_inverted_one():
    """A lead shorter than the close offset must produce nothing, not a span that starts after it ends.

    Found by mutation: dropping the `start < end` guard changed no test, because the real constants never
    invert. An inverted span is not merely useless -- it would corrupt the merge and the budget simulator's
    ordered walk, both of which assume start <= end.
    """
    games = sched([game("g1", "2026-09-13", "13:00")])
    assert PW.windows(games, primary_lead_min=5, close_lead_min=10) == []
    for start, end in PW.windows(games):
        assert start < end


def test_windows_cross_a_dst_boundary_and_a_year_boundary_without_special_casing():
    # US DST ended 2026-11-01; both of these are resolved by the repo's own Eastern conversion.
    for gameday, hhmm in (("2026-11-01", "13:00"), ("2027-01-03", "13:00")):
        (start, end), = PW.windows(sched([game("g", gameday, hhmm)]))
        ko = et(gameday, hhmm)
        assert (start, end) == (ko - timedelta(minutes=180), ko - timedelta(minutes=10))


# ---- the gate's ACTIVE / INACTIVE answer --------------------------------------------------------------

@pytest.fixture
def one_game():
    return sched([game("g1", "2026-09-13", "13:00")])


def test_exactly_at_the_primary_opening_boundary_is_active(one_game):
    ko = et("2026-09-13", "13:00")
    assert PW.evaluate(one_game, ko - timedelta(minutes=180))["active"] is True


def test_one_minute_before_opening_is_inactive(one_game):
    ko = et("2026-09-13", "13:00")
    assert PW.evaluate(one_game, ko - timedelta(minutes=181))["active"] is False


def test_exactly_at_the_closing_boundary_is_active(one_game):
    ko = et("2026-09-13", "13:00")
    assert PW.evaluate(one_game, ko - timedelta(minutes=10))["active"] is True


def test_after_the_closing_boundary_is_inactive(one_game):
    ko = et("2026-09-13", "13:00")
    for delta in (9, 1, 0, -30):
        assert PW.evaluate(one_game, ko - timedelta(minutes=delta))["active"] is False, delta


def test_exactly_at_a_secondary_opening_boundary_is_active():
    rows = [game(f"g{i}", "2026-09-13", "13:00") for i in range(5)]
    rows.append(game("snf", "2026-09-13", "20:20"))
    games = sched(rows)
    snf = et("2026-09-13", "20:20")
    assert PW.evaluate(games, snf - timedelta(minutes=120))["active"] is True
    assert PW.evaluate(games, snf - timedelta(minutes=121))["active"] is False


def test_a_quiet_tuesday_is_inactive_and_says_when_the_next_window_opens(one_game):
    out = PW.evaluate(one_game, at("2026-09-08T12:00:00"))
    assert out["active"] is False
    assert out["status"] == PW.STATUS_INACTIVE
    assert out["next_window_start_utc"] is not None


def test_an_empty_schedule_is_inactive_rather_than_an_error():
    """No games is a KNOWN answer -- the season is over. Only an unREADABLE schedule is an error."""
    out = PW.evaluate(sched([]), at("2026-07-04T12:00:00"))
    assert out["active"] is False and out["status"] == PW.STATUS_INACTIVE


# ---- the union: one wake, at most one Airtable request ------------------------------------------------

def test_overlapping_windows_are_unioned_into_one():
    """Three clusters close together must not mean three chances to spend a request."""
    rows = [game("a", "2026-09-13", "13:00"), game("b", "2026-09-13", "14:00"),
            game("c", "2026-09-13", "15:00")]
    spans = PW.windows(sched(rows))
    assert len(spans) == 1, f"expected one merged window, got {spans}"


def test_one_wake_can_never_authorise_more_than_one_poll():
    """Whatever the schedule, the number of merged windows containing NOW is never more than one."""
    rows = ([game(f"m{i}", "2026-11-26", "12:30") for i in range(3)] +
            [game(f"n{i}", "2026-11-26", "13:00") for i in range(3)] +
            [game("o", "2026-11-26", "16:30"), game("p", "2026-11-26", "20:20")])
    games = sched(rows)
    t = et("2026-11-26", "12:30") - timedelta(hours=6)
    seen = set()
    while t <= et("2026-11-26", "20:20"):
        out = PW.evaluate(games, t)
        assert out["active_window_count"] <= 1, (t, out)
        seen.add(out["active_window_count"])
        t += timedelta(minutes=10)
    assert 1 in seen, "the sweep never entered a window, so it proved nothing"


# ---- the gate CLI -------------------------------------------------------------------------------------

def run_gate(tmp_path, rows, now, extra=()):
    csv = tmp_path / "games.csv"
    csv.write_text(CSV_HEAD + "".join(rows))
    out = tmp_path / "ghout"
    r = subprocess.run([sys.executable, GATE, "--schedule", str(csv), "--now", now,
                        "--github-output", str(out), "--json", *extra],
                       capture_output=True, text=True)
    return r, (out.read_text() if out.exists() else "")


def test_the_gate_reports_active_and_sets_the_job_output(tmp_path):
    r, ghout = run_gate(tmp_path, [game("g1", "2026-09-13", "13:00")], "2026-09-13T15:00:00+00:00")
    assert r.returncode == 0
    assert "status=ACTIVE" in r.stdout and "active=true" in r.stdout
    assert "active=true" in ghout


def test_the_gate_reports_inactive_with_zero_airtable_calls(tmp_path):
    r, ghout = run_gate(tmp_path, [game("g1", "2026-09-13", "13:00")], "2026-09-08T12:00:00+00:00")
    assert r.returncode == 0
    assert f"status={PW.STATUS_INACTIVE}" in r.stdout
    assert "active=false" in r.stdout and "airtable_calls=0" in r.stdout
    assert "result=NO_WORK_WINDOW" in r.stdout
    assert "active=false" in ghout


def test_an_unreadable_schedule_fails_closed_and_non_zero(tmp_path):
    out = tmp_path / "ghout"
    r = subprocess.run([sys.executable, GATE, "--schedule", str(tmp_path / "nope.csv"),
                        "--now", "2026-09-13T15:00:00+00:00", "--github-output", str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 2, "an unknown calendar must not exit 0"
    assert f"status={PW.STATUS_ERROR}" in r.stdout
    assert PW.STATUS_INACTIVE not in r.stdout, "an error must never be reported as 'no window'"
    assert "active=false" in out.read_text()


def test_the_gate_prints_nothing_private(tmp_path):
    """It is a clock question. It has no candidate to leak and must never grow one."""
    r, _ = run_gate(tmp_path, [game("g1", "2026-09-13", "13:00")], "2026-09-13T15:00:00+00:00")
    low = r.stdout.lower()
    for leak in ("ticker", "player", "price", "probability", "stake", "thesis", "airtable_token",
                 "signing"):
        assert leak not in low, f"the gate printed {leak!r}"


def test_the_gate_needs_no_secret_and_no_network(tmp_path):
    src = open(GATE).read()
    for forbidden in ("AIRTABLE_TOKEN", "PREFLIGHT_SIGNING_KEY", "KalshiClient", "list_by_status"):
        assert forbidden not in src, f"the gate references {forbidden}"
    # It runs with a completely empty environment.
    csv = tmp_path / "g.csv"
    csv.write_text(CSV_HEAD + game("g1", "2026-09-13", "13:00"))
    r = subprocess.run([sys.executable, GATE, "--schedule", str(csv),
                        "--now", "2026-09-13T15:00:00+00:00"],
                       capture_output=True, text=True, env={"PATH": os.environ.get("PATH", "")})
    assert r.returncode == 0 and "active=true" in r.stdout


def test_the_gate_result_is_machine_readable(tmp_path):
    r, _ = run_gate(tmp_path, [game("g1", "2026-09-13", "13:00")], "2026-09-13T15:00:00+00:00")
    payload = json.loads(r.stdout.strip().splitlines()[-1])
    for key in ("status", "active", "active_window_start_utc", "active_window_end_utc",
                "active_cluster_count", "game_day", "primary_cluster_utc"):
        assert key in payload, key
