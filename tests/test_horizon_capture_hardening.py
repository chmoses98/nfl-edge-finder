"""Horizon capture hardening: a conductor that does not depend on cron, and records that cannot flatter.

Measured before this existed: GitHub started the */15 RUN NFL gate on ~7% of its ticks, 105-417 minutes apart,
and weeks 1-2 lost 15 of 45 RUN NFL horizons (four of them "captured" by builds that finished after kickoff)
with none on time. The properties pinned here:

  * the conductor dispatches exactly when a horizon is owed and no run is already serving it, retries a
    failed build after a bounded wait, and never stacks runs;
  * it chains its own successor once, near its end, so continuity does not hang on its cron;
  * one horizon id is one canonical capture -- a second marking never moves it;
  * a capture's lateness is recorded, labelled toward late, and a post-kickoff build is MISSED, never
    "delivered";
  * capture health splits history from the current system and never reports a missed horizon as absent.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts", "handicap"))

from nfl_edge.evaluation.capture_health import horizon_delivery  # noqa: E402
from nfl_edge.handicap.conductor import REDISPATCH_MIN, decide, should_chain  # noqa: E402
from nfl_edge.handicap.horizons import due_horizons, mark_captured, parse_horizon_id  # noqa: E402

import horizon_capture_health as HCH  # noqa: E402
import horizon_conductor as HC  # noqa: E402

UTC = timezone.utc
KO = datetime(2026, 9, 25, 0, 15, tzinfo=UTC)                  # 2026 week 3 TNF
SLATE = "2026-REG-03"
GAMES = [{"game_id": "2026_03_ATL_GB", "kickoff_utc": KO}]


def _schedule_games():
    """The shape `nfl_calendar.parse_schedule` produces, for resolve_active_week / week_blocks."""
    return [{"game_id": "2026_03_ATL_GB", "season": 2026, "week": 3, "game_type": "REG", "gameday": "2026-09-24",
             "away_team": "ATL", "home_team": "GB", "kickoff_utc": KO, "has_result": False},
            {"game_id": "2026_02_X_Y", "season": 2026, "week": 2, "game_type": "REG", "gameday": "2026-09-20",
             "away_team": "X", "home_team": "Y", "kickoff_utc": datetime(2026, 9, 20, 17, 0, tzinfo=UTC),
             "has_result": True}]


# ------------------------------------------------------------------------------------------ decide / chain

def test_nothing_due_means_no_dispatch():
    assert decide([], {}, KO, 0) == (False, "nothing due")


def test_an_active_run_serves_what_is_due_and_is_never_stacked():
    go, why = decide(["h"], {}, KO, active_runs=1)
    assert go is False and "already queued or running" in why


def test_a_failed_build_is_retried_after_the_redispatch_window_not_before():
    t0 = KO - timedelta(minutes=90)
    sent = {frozenset(["h"]): t0}
    assert decide(["h"], sent, t0 + timedelta(minutes=REDISPATCH_MIN - 1), 0)[0] is False
    assert decide(["h"], sent, t0 + timedelta(minutes=REDISPATCH_MIN + 1), 0)[0] is True


def test_a_new_horizon_set_dispatches_immediately():
    t0 = KO - timedelta(minutes=90)
    assert decide(["a", "b"], {frozenset(["a"]): t0}, t0 + timedelta(minutes=1), 0)[0] is True


def test_the_successor_is_chained_once_near_the_end():
    end = 10_000.0
    assert should_chain(end - 60 * 60, end, False) is False
    assert should_chain(end - 5 * 60, end, False) is True
    assert should_chain(end - 5 * 60, end, True) is False


# ------------------------------------------------------------------------------------------ one conductor pass

class _Calls:
    def __init__(self, active=0, ok=True):
        self.dispatched, self.active, self.ok = [], active, ok

    def dispatcher(self, wf, ref):
        self.dispatched.append((wf, ref))
        return self.ok, "ok" if self.ok else "HTTP 500"

    def active_runs(self, wf):
        return self.active


def _pass(now, state_run_nfl=None, calls=None, dispatched=None, targets=("RUN_NFL", "THREE_ARM")):
    calls = calls or _Calls()
    readers = {"RUN_NFL": lambda: state_run_nfl or {}, "THREE_ARM": lambda: {}}
    lines = HC.one_pass(list(targets), _schedule_games(), "test", now, dispatched if dispatched is not None else {},
                        state_readers=readers, active=calls.active_runs, dispatcher=calls.dispatcher)
    return lines, calls


def test_the_conductor_dispatches_both_horizon_workflows_when_t6h_is_due():
    lines, calls = _pass(KO - timedelta(minutes=358))
    assert [ln["decision"] for ln in lines] == ["dispatch", "dispatch"]
    assert {wf for wf, _ in calls.dispatched} == {"run-nfl-horizons.yml", "three-arm-horizons.yml"}
    assert all(ref == "main" for _, ref in calls.dispatched)


def test_a_captured_horizon_is_not_dispatched_again():
    now = KO - timedelta(minutes=358)
    due = due_horizons(SLATE, GAMES, now, {})["due"]
    state = mark_captured({}, due, run_id="1", now=now)
    lines, calls = _pass(now + timedelta(minutes=4), state_run_nfl=state, targets=("RUN_NFL",))
    assert lines[0]["decision"] == "wait" and calls.dispatched == []


def test_a_refused_dispatch_is_retried_on_the_next_pass():
    now = KO - timedelta(minutes=88)
    dispatched = {}
    _pass(now, calls=_Calls(ok=False), dispatched=dispatched, targets=("RUN_NFL",))
    lines, calls = _pass(now + timedelta(minutes=4), dispatched=dispatched, targets=("RUN_NFL",))
    assert lines[0]["decision"] == "dispatch" and len(calls.dispatched) == 1


def test_after_kickoff_the_conductor_reports_missed_and_dispatches_nothing():
    lines, calls = _pass(KO + timedelta(minutes=1), targets=("RUN_NFL",))
    # resolve_active_week keeps the in-progress slate active; nothing pregame is owed any more.
    assert calls.dispatched == []
    assert all(ln["decision"] in ("wait", "idle") for ln in lines)


def test_the_conductor_workflow_chains_itself_and_keeps_a_cron_backstop():
    wf = open(os.path.join(ROOT, ".github", "workflows", "horizon-conductor.yml")).read()
    assert "--chain-workflow horizon-conductor.yml" in wf
    assert "cron:" in wf and "group: horizon-conductor" in wf and "cancel-in-progress: false" in wf
    assert "actions: write" in wf and "if: github.ref == 'refs/heads/main'" in wf
    assert "--targets RUN_NFL,THREE_ARM" in wf


@pytest.mark.parametrize("name", ["kalshi-conductor.yml", "shadow-v2-horizon-conductor.yml"])
def test_the_other_conductors_chain_their_successor(name):
    wf = open(os.path.join(ROOT, ".github", "workflows", name)).read()
    assert f"gh workflow run {name} --ref main" in wf
    assert "actions: write" in wf


# ------------------------------------------------------------------------------------------ canonical capture

def _records(now):
    return due_horizons(SLATE, GAMES, now, {})["due"]


def test_lateness_is_recorded_from_the_trigger_even_when_ids_travel_alone():
    trigger = KO - timedelta(minutes=360)
    rec = parse_horizon_id(f"{SLATE}|20260925T0015Z|T-360m")
    state = mark_captured({}, [rec], now=trigger + timedelta(minutes=17))
    r = state["captured"][rec["horizon_id"]]
    assert r["late_by_min"] == 17.0 and r["delivery"] == "LATE" and r["status"] == "CAPTURED"


@pytest.mark.parametrize("minutes,label", [(5, "ON_TIME"), (10, "ON_TIME"), (30, "LATE"), (46, "LATE_DEGRADED")])
def test_delivery_labels_never_err_toward_on_time(minutes, label):
    rec = parse_horizon_id(f"{SLATE}|20260925T0015Z|T-1440m")
    trigger = KO - timedelta(minutes=1440)
    state = mark_captured({}, [rec], now=trigger + timedelta(minutes=minutes))
    assert state["captured"][rec["horizon_id"]]["delivery"] == label


def test_a_build_that_finished_after_kickoff_is_missed_not_captured():
    rec = parse_horizon_id(f"{SLATE}|20260925T0015Z|T-30m")
    state = mark_captured({}, [rec], now=KO + timedelta(minutes=2))
    r = state["captured"][rec["horizon_id"]]
    assert r["status"] == "MISSED" and r["delivery"] == "MISSED" and "kickoff" in r["reason"]
    # and it is still consumed: nothing will try to build a pregame packet for a started game
    assert due_horizons(SLATE, GAMES, KO + timedelta(minutes=3), state)["due"] == []


def test_one_horizon_id_is_one_canonical_capture_a_retry_cannot_move_it():
    now = KO - timedelta(minutes=355)
    first = mark_captured({}, _records(now), run_id="A", now=now)
    again = mark_captured(first, _records(now), run_id="B", now=now + timedelta(minutes=40))
    assert again["captured"] == first["captured"]


# ------------------------------------------------------------------------------------------ capture health

def _marker(hid, at, status=None):
    return {"horizon_id": hid, "snapshot_id": at.isoformat(), "status": status}


def test_a_marker_observed_after_kickoff_is_missed_in_capture_health():
    hid = f"{SLATE}|20260925T0015Z|T-30m"
    hd = horizon_delivery(SLATE, GAMES, [_marker(hid, KO + timedelta(minutes=1))], KO + timedelta(hours=1))
    row = next(r for r in hd["rows"] if r["horizon_id"] == hid)
    assert row["status"] == "MISSED" and row["cause"].startswith("CAPTURED_AT_OR_AFTER_KICKOFF")
    assert hid in hd["missed"]


def test_a_horizon_with_no_record_is_missed_never_absent():
    hd = horizon_delivery(SLATE, GAMES, [], KO + timedelta(hours=1))
    assert hd["owed"] == 4 and hd["counts"] == {"MISSED": 4} and hd["delivered"] == 0


def test_capture_health_splits_history_from_the_current_system():
    games = _schedule_games()
    now = KO + timedelta(hours=4)
    wk3 = [f"{SLATE}|20260925T0015Z|T-{h}m" for h in (1440, 360, 90, 30)]
    markers = [_marker(wk3[0], KO - timedelta(minutes=1440 - 19)),         # before the conductor, late
               _marker(wk3[1], KO - timedelta(minutes=360 - 6)),           # after, on time
               _marker(wk3[2], KO - timedelta(minutes=90 - 8))]            # after, on time; T-30m missed
    out = HCH.season_health(games, markers, now, season=2026,
                            deployed=datetime(2026, 9, 24, 12, 0, tzinfo=UTC))
    after = out["summary"]["AFTER_CONDUCTOR"]
    before = out["summary"]["BEFORE_CONDUCTOR"]
    assert after["owed"] == 3 and after["delivered"] == 2 and after["missed_ids"] == [wk3[3]]
    assert after["counts"].get("DELIVERED_ON_TIME") == 2
    # week 2 (no markers at all) and week 3's T-24h stay in history, unimproved
    assert before["missed"] == 4 and before["counts"].get("DELIVERED_LATE") == 1


def test_capture_health_goes_red_on_a_fresh_miss_under_the_conductor(tmp_path, monkeypatch):
    games = _schedule_games()
    monkeypatch.setattr(HCH, "load_schedule", lambda *a, **k: (games, "test"))
    state = tmp_path / "s.json"
    state.write_text(json.dumps({"captured": {}}))
    rc = HCH.main(["--run-nfl-state", str(state), "--out", str(tmp_path / "o"), "--season", "2026",
                   "--now", (KO + timedelta(hours=2)).isoformat(), "--fail-on-recent-miss-hours", "48"])
    assert rc == 1
    doc = json.load(open(tmp_path / "o" / "2026.capture_health.json"))
    assert doc["targets"]["RUN_NFL"]["summary"]["AFTER_CONDUCTOR"]["missed"] == 3
