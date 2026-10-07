"""The canonical publication rolls to the next slate (incident 2026-10-06/07).

The board at `handicap-reports/app/latest` stopped at the week-4 MNF pregame build (2026-10-06T00:14Z) and kept
ATL@NO "SCHEDULED" a day after kickoff. Three breaks, each pinned here:

1. nflverse dropped the uncompressed `schedules/games.csv` release asset (404 from ~19:47Z on 2026-10-06; the
   release now carries `games.csv.gz`). Every schedule reader -- the horizon gate, the conductor, the bronze
   download behind shadow-price / RUN NFL -- failed closed on the 404.
2. Jobs that check out the ~52 GB market-data worktree died with "No space left on device".
3. Nothing owned the rollover: horizons open T-24h before a cluster and the 2-hourly shadow-price refresh has
   not built a report since 2026-09-30 (its capture is always 50-60 min old against a 45 min gate), so the
   finished week stayed published for ~48 hours after every Monday game.
"""
import gzip
import importlib.util
import io
import json
import os
import subprocess
import sys
import urllib.error
from datetime import datetime, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.data import nfl_calendar as CAL                  # noqa: E402
from nfl_edge.handicap.horizons import rollover_due             # noqa: E402


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# The real week-4 tail and week-5 head of the 2026 schedule (nflverse games.csv columns the calendar reads).
SCHEDULE = (
    "game_id,season,game_type,week,gameday,weekday,gametime,away_team,away_score,home_team,home_score,result\n"
    "2026_04_DET_CAR,2026,REG,4,2026-10-04,Sunday,20:20,DET,26,CAR,32,6\n"
    "2026_04_ATL_NO,2026,REG,4,2026-10-05,Monday,20:15,ATL,45,NO,24,-21\n"
    "2026_05_TB_DAL,2026,REG,5,2026-10-08,Thursday,20:15,TB,,DAL,,\n"
    "2026_05_CHI_GB,2026,REG,5,2026-10-11,Sunday,13:00,CHI,,GB,,\n"
    "2026_05_BUF_LA,2026,REG,5,2026-10-12,Monday,20:15,BUF,,LA,,\n"
)
# The instant the incident was measured: a day after ATL@NO kicked off, two days before week 5's first game.
INCIDENT = datetime(2026, 10, 7, 0, 28, tzinfo=timezone.utc)
WEEK4_MANIFEST = {"season": 2026, "week": 4, "season_type": "REG", "slate_id": "2026-REG-04"}
WEEK5_MANIFEST = {"season": 2026, "week": 5, "season_type": "REG", "slate_id": "2026-REG-05"}


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _http(url, code):
    return urllib.error.HTTPError(url, code, "status", {}, None)


# ===================================================================== 1. the schedule source
def test_the_gzip_release_asset_is_the_first_source_and_is_decoded():
    calls = []

    def opener(req, timeout=None):
        calls.append(req.full_url)
        return _Resp(gzip.compress(SCHEDULE.encode()))

    text, url = CAL.fetch_schedule_text(_urlopen=opener)
    assert url == CAL.SCHEDULE_URL and url.endswith("/schedules/games.csv.gz")
    assert calls == [CAL.SCHEDULE_URL]
    assert text == SCHEDULE


def test_a_removed_asset_falls_back_to_the_next_name_only_on_404():
    calls = []

    def opener(req, timeout=None):
        calls.append(req.full_url)
        if req.full_url == CAL.SCHEDULE_URL:
            raise _http(req.full_url, 404)
        return _Resp(SCHEDULE.encode())

    text, url = CAL.fetch_schedule_text(_urlopen=opener)
    assert url == CAL.LEGACY_SCHEDULE_URL and calls == list(CAL.SCHEDULE_URLS) and text == SCHEDULE


@pytest.mark.parametrize("err", [_http(CAL.SCHEDULE_URL, 503), OSError("connection reset by peer")])
def test_any_other_failure_is_raised_at_once_so_the_retry_bound_still_holds(err):
    calls = []

    def opener(req, timeout=None):
        calls.append(req.full_url)
        raise err

    with pytest.raises(type(err)):
        CAL.fetch_schedule_text(_urlopen=opener)
    assert calls == [CAL.SCHEDULE_URL]


def test_every_asset_gone_still_fails_closed():
    def opener(req, timeout=None):
        raise _http(req.full_url, 404)

    with pytest.raises(urllib.error.HTTPError):
        CAL.load_schedule("/nonexistent", allow_download=True, download_attempts=1, _urlopen=opener)


def test_the_downloaded_schedule_resolves_the_next_week_after_the_last_game():
    def opener(req, timeout=None):
        if req.full_url != CAL.SCHEDULE_URL:
            raise AssertionError("asked the legacy asset although the gzip one answered")
        return _Resp(gzip.compress(SCHEDULE.encode()))

    games, src = CAL.load_schedule("/nonexistent", allow_download=True, _urlopen=opener)
    week = CAL.resolve_active_week(games, INCIDENT, schedule_source=src)
    assert (week["status"], week["slate_id"], week["games_upcoming"]) == ("OK", "2026-REG-05", 3)


def test_no_downloader_names_the_removed_asset_any_more():
    """Every reader goes through nfl_calendar.SCHEDULE_URLS; a hard-coded games.csv URL is how this broke."""
    offenders = []
    for base in ("nfl_edge", "scripts"):
        for dirpath, _, files in os.walk(os.path.join(ROOT, base)):
            for f in files:
                if not f.endswith(".py") or f == "nfl_calendar.py":
                    continue
                p = os.path.join(dirpath, f)
                if "releases/download/schedules/games.csv\"" in open(p).read():
                    offenders.append(os.path.relpath(p, ROOT))
    assert offenders == []


def test_the_bronze_download_writes_games_csv_from_the_gzip_asset(tmp_path):
    DL = _load("scripts/data/nflverse_download.py", "_nflverse_download_under_test")
    d = tmp_path / "schedules"
    d.mkdir()
    (d / "games.csv.gz").write_bytes(gzip.compress(SCHEDULE.encode()))
    row = DL.derive_schedule_csv(str(d))
    assert (d / "games.csv").read_text() == SCHEDULE
    assert row["status"] == "derived" and row["derived_from"].endswith("games.csv.gz") and row["bytes"] == len(SCHEDULE)
    assert DL.catalog([2026])["schedules"] == ["games.csv.gz"]


def test_context_capture_reads_the_gzip_schedule():
    CC = _load("scripts/data/context_capture.py", "_context_capture_rollover")
    assert CC.SCHEDULE_URLS == CAL.SCHEDULE_URLS
    assert CC.decode_schedule_bytes(gzip.compress(b"a,b\n1,2\n")) == "a,b\n1,2\n"


# ===================================================================== 3. the rollover owner
def _week(now=INCIDENT):
    return CAL.resolve_active_week(CAL.parse_schedule(SCHEDULE), now)


def test_a_published_earlier_week_is_a_rollover_owed_now():
    r = rollover_due(_week(), WEEK4_MANIFEST)
    assert r["rollover_id"] == "2026-REG-05|ROLLOVER"
    assert (r["published_slate_id"], r["active_slate_id"]) == ("2026-REG-04", "2026-REG-05")


def test_once_the_active_week_is_published_nothing_is_owed():
    assert rollover_due(_week(), WEEK5_MANIFEST) is None


def test_a_later_pinned_build_is_left_alone():
    assert rollover_due(_week(), {"season": 2026, "week": 6, "slate_id": "2026-REG-06"}) is None


@pytest.mark.parametrize("published", [None, {}, {"season": "x"}])
def test_no_readable_published_report_is_owed(published):
    assert rollover_due(_week(), published)["published_slate_id"] is None


def test_the_rollover_waits_until_the_last_game_of_the_week_has_finished():
    during_mnf = datetime(2026, 10, 6, 2, 0, tzinfo=timezone.utc)      # ATL@NO kicked off 00:15Z
    assert _week(during_mnf)["slate_id"] == "2026-REG-04"
    assert rollover_due(_week(during_mnf), WEEK4_MANIFEST) is None


def test_off_season_owes_nothing():
    assert rollover_due({"status": "NO_SLATE", "reason": "offseason"}, WEEK4_MANIFEST) is None


def _gate(tmp_path, manifest):
    sched = tmp_path / "games.csv"
    sched.write_text(SCHEDULE)
    args = [sys.executable, os.path.join(ROOT, "scripts", "handicap", "horizon_gate.py"), "--schedule", str(sched),
            "--now", INCIDENT.isoformat(), "--github-output", str(tmp_path / "out")]
    if manifest is not None:
        (tmp_path / "published.json").write_text(json.dumps(manifest))
        args += ["--published-manifest", str(tmp_path / "published.json")]
    r = subprocess.run(args, capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stderr
    return dict(line.split("=", 1) for line in (tmp_path / "out").read_text().splitlines())


def test_the_run_nfl_gate_runs_a_rollover_build_with_no_horizon_to_mark(tmp_path):
    out = _gate(tmp_path, WEEK4_MANIFEST)
    assert out["should_run"] == "true" and out["rollover"] == "true"
    assert out["week"] == "5" and out["horizon_ids"] == "", "a rollover is not a decision horizon; nothing is marked"
    assert out["reason"].startswith("rollover:")


def test_the_run_nfl_gate_is_quiet_once_the_week_is_published(tmp_path):
    out = _gate(tmp_path, WEEK5_MANIFEST)
    assert out["should_run"] == "false" and out["rollover"] == "false"


def test_without_a_published_manifest_the_gate_is_horizons_only(tmp_path):
    out = _gate(tmp_path, None)
    assert out["should_run"] == "false" and out["rollover"] == "false"


def test_the_conductor_dispatches_run_nfl_for_a_rollover():
    HC = _load("scripts/handicap/horizon_conductor.py", "_hc_rollover")
    games = CAL.parse_schedule(SCHEDULE)
    sent = []
    lines = HC.one_pass(["RUN_NFL"], games, "fixture", INCIDENT, {}, state_readers={"RUN_NFL": lambda: {}},
                        active=lambda wf: 0, dispatcher=lambda wf, ref: (sent.append(wf) or True, "ok"),
                        published_reader=lambda: WEEK4_MANIFEST)
    assert sent == ["run-nfl-horizons.yml"]
    assert lines[0]["due"] == ["2026-REG-05|ROLLOVER"] and lines[0]["decision"] == "dispatch"
    # published: nothing more is owed; and callers that pass no reader keep the horizons-only behaviour
    for reader in (lambda: WEEK5_MANIFEST, None):
        sent.clear()
        HC.one_pass(["RUN_NFL"], games, "fixture", INCIDENT, {}, state_readers={"RUN_NFL": lambda: {}},
                    active=lambda wf: 0, dispatcher=lambda wf, ref: (sent.append(wf) or True, "ok"),
                    published_reader=reader)
        assert sent == []


def test_the_horizon_workflow_feeds_the_gate_the_published_manifest():
    y = open(os.path.join(ROOT, ".github", "workflows", "run-nfl-horizons.yml")).read()
    assert "origin/handicap-reports:latest/manifest.json > /tmp/hz/published.json" in y
    assert "--published-manifest /tmp/hz/published.json" in y
    assert "rollover: ${{ steps.gate.outputs.rollover }}" in y
    src = open(os.path.join(ROOT, "scripts", "handicap", "horizon_conductor.py")).read()
    assert "published_reader=run_nfl_published" in src


# ===================================================================== 2. runner disk
@pytest.mark.parametrize("wf", ["run-nfl.yml", "shadow-price.yml"])
def test_the_publication_writers_free_disk_before_the_market_data_worktree(wf):
    y = open(os.path.join(ROOT, ".github", "workflows", wf)).read()
    free, fetch = y.find("bash scripts/ci/free_runner_disk.sh"), y.find("git fetch --depth=1 origin market-data")
    assert 0 <= free < fetch


def test_the_disk_step_never_removes_the_python_toolcache_and_never_fails():
    s = open(os.path.join(ROOT, "scripts", "ci", "free_runner_disk.sh")).read()
    assert "/opt/hostedtoolcache/Python" not in s and "hostedtoolcache/CodeQL" in s
    assert s.rstrip().endswith("exit 0")
