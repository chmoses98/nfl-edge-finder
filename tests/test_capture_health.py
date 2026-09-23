"""Horizon delivery is measured against the schedule: a horizon that never fired is MISSED (it has no marker by
construction, so counting MISSED markers always said 0), and lateness comes from the freeze's own snapshot."""
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nfl_edge.evaluation import capture_health as CH            # noqa: E402

SLATE = "2026-REG-02"
GAMES = [{"game_id": "g1", "kickoff_utc": "2026-09-20T17:00:00+00:00"}, {"game_id": "g2", "kickoff_utc": "2026-09-20T17:00:00+00:00"},
         {"game_id": "g3", "kickoff_utc": "2026-09-21T00:20:00+00:00"}]


def marker(cluster, h, snap):
    return {"horizon_id": f"{SLATE}|{cluster}|T-{h}m", "snapshot_id": snap, "status": "CAPTURED"}


def test_the_week2_sunday_shape_is_reported_as_it_happened():
    # 17:00Z cluster: T-24h on time, T-6h served at 13:39 (159 min late), T-90m never served
    markers = [marker("20260920T1700Z", 1440, "20260919T170500Z"), marker("20260920T1700Z", 360, "20260920T133947Z")]
    starts = ["2026-09-20T05:26:03Z", "2026-09-20T09:54:54Z", "2026-09-20T13:49:02Z", "2026-09-20T17:08:31Z"]
    now = datetime(2026, 9, 20, 18, 0, tzinfo=timezone.utc)
    out = CH.horizon_delivery(SLATE, GAMES, markers, now, workflow_starts=starts)
    by = {(r["cluster_key"], r["horizon_min"]): r for r in out["rows"]}
    assert by[("20260920T1700Z", 1440)]["status"] == "DELIVERED_ON_TIME"
    t6 = by[("20260920T1700Z", 360)]
    assert t6["status"] == "DELIVERED_DEGRADED" and t6["lateness_min"] == 159.8 and t6["cause"].startswith("SCHEDULER_GAP")
    t90 = by[("20260920T1700Z", 90)]
    assert t90["status"] == "MISSED" and t90["cause"].startswith("SCHEDULER_GAP")
    assert out["missed"] == [f"{SLATE}|20260920T1700Z|T-90m", f"{SLATE}|20260920T1700Z|T-30m"]
    # the night game: T-24h missing but its kickoff has not passed -> still DUE, never MISSED early
    assert by[("20260921T0020Z", 1440)]["status"] == "DUE"
    assert by[("20260921T0020Z", 90)]["status"] == "NOT_YET_DUE"


def test_without_workflow_times_the_cause_is_not_guessed():
    out = CH.horizon_delivery(SLATE, GAMES, [], datetime(2026, 9, 22, tzinfo=timezone.utc))
    assert out["delivered"] == 0 and out["owed"] == 8
    assert all(r["cause"].startswith("UNATTRIBUTED") for r in out["rows"])
