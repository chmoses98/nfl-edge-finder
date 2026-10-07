"""The app-publication alarm fires on the 2026-10-06/07 incident and stays quiet on healthy and off-season boards."""
import importlib.util
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nfl_edge.data.nfl_calendar import parse_schedule  # noqa: E402

spec = importlib.util.spec_from_file_location("_aph", os.path.join(ROOT, "scripts", "ops", "app_publication_health.py"))
APH = importlib.util.module_from_spec(spec)
spec.loader.exec_module(APH)

GAMES = parse_schedule(
    "game_id,season,game_type,week,gameday,gametime,away_team,home_team,result\n"
    "2026_04_ATL_NO,2026,REG,4,2026-10-05,20:15,ATL,NO,-21\n"
    "2026_05_TB_DAL,2026,REG,5,2026-10-08,20:15,TB,DAL,\n"
    "2026_05_BUF_LA,2026,REG,5,2026-10-12,20:15,BUF,LA,\n")
NOW = datetime(2026, 10, 7, 0, 28, tzinfo=timezone.utc)
W4 = {"season": 2026, "week": 4, "slate_id": "2026-REG-04"}
W5 = {"season": 2026, "week": 5, "slate_id": "2026-REG-05"}
STALE_BOARD = {"generated_at": "2026-10-06T00:14:18Z",
               "items": [{"event_id": "evt_atl_no", "status": "SCHEDULED", "start_time_utc": "2026-10-06T00:15:00Z"}]}
FRESH_BOARD = {"generated_at": "2026-10-07T00:10:00Z",
               "items": [{"event_id": "evt_atl_no", "status": "UNKNOWN", "start_time_utc": "2026-10-06T00:15:00Z"},
                         {"event_id": "evt_tb_dal", "status": "SCHEDULED", "start_time_utc": "2026-10-09T00:15:00Z"}]}


def rules(out):
    return sorted(f["rule"] for f in out["findings"])


def test_the_incident_board_is_red():
    out = APH.evaluate(STALE_BOARD, W4, GAMES, NOW)
    assert out["status"] == "STALE" and rules(out) == ["DANGLING_EVENT", "ROLLOVER_OVERDUE"]


def test_a_rolled_over_board_is_quiet():
    assert APH.evaluate(FRESH_BOARD, W5, GAMES, NOW)["findings"] == []


def test_the_rollover_has_a_grace_after_the_last_game():
    just_done = datetime(2026, 10, 6, 5, 0, tzinfo=timezone.utc)  # MNF finished 04:15Z, 45 min ago
    board = dict(STALE_BOARD, generated_at="2026-10-06T00:14:18Z")
    assert "ROLLOVER_OVERDUE" not in rules(APH.evaluate(board, W4, GAMES, just_done))


def test_an_old_board_while_a_slate_is_active_is_red_but_off_season_is_not():
    old = dict(FRESH_BOARD, generated_at="2026-10-03T00:00:00Z")
    assert rules(APH.evaluate(old, W5, GAMES, NOW)) == ["BOARD_TOO_OLD"]
    after_season = datetime(2026, 10, 20, tzinfo=timezone.utc)
    final_board = {"generated_at": "2026-10-12T23:45:00Z",
                   "items": [{"event_id": "evt_buf_la", "status": "UNKNOWN", "start_time_utc": "2026-10-13T00:15:00Z"}]}
    assert APH.evaluate(final_board, W5, GAMES, after_season)["findings"] == []


def test_the_feed_declaring_its_source_stale_is_red():
    idx = {"status": "STALE_PUBLICATION", "publications": [{"reasons": ["ATL@NO still SCHEDULED"]}]}
    assert rules(APH.evaluate(FRESH_BOARD, W5, GAMES, NOW, idx)) == ["FEED_SOURCE_STALE"]
    assert APH.evaluate(FRESH_BOARD, W5, GAMES, NOW, {"status": "NO_CURRENT_GAMES"})["findings"] == []


def test_workflow_health_runs_it_and_goes_red_on_it():
    y = open(os.path.join(ROOT, ".github", "workflows", "workflow-health.yml")).read()
    assert "scripts/ops/app_publication_health.py" in y and "steps.app_publication.outcome == 'failure'" in y
