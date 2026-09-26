"""Autonomous postgame, explicit automation state, and a dead-chain alarm.

Thursday 2026-09-24/25 ATL@GB (kickoff 00:15Z, final ~03:30Z): postgame-settle ran at 05:01Z only because the owner
dispatched it (the cron's deliveries were 21:35Z and 05:05Z); in the router, settle-wagers (05:03Z, 05:21Z) and
deliver-wagers (05:11Z) were dispatched by hand too. Pinned here:

  * the horizon conductor starts the postgame workflows at fixed offsets after each kickoff cluster, once per
    tick set, never stacking a run, retrying a FAILED run a bounded number of times, never repeating a green one;
  * a finished postgame run states WAITING_FOR_SOURCE / PARTIAL_COMPLETE / COMPLETE / BLOCKED, and CONFLICT is
    BLOCKED (stays red);
  * workflow-health goes red, and restarts once, when a conductor chain has no link queued or running.
"""
import os
import sys
from datetime import datetime, timedelta, timezone

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts", "handicap"))
sys.path.insert(0, os.path.join(ROOT, "scripts", "ops"))

from nfl_edge.handicap.automation import (  # noqa: E402
    POSTGAME_MAX_ATTEMPTS, POSTGAME_OFFSETS_MIN, POSTGAME_RETRY_MIN, POSTGAME_WORKFLOWS, STATES, chain_health,
    classify_postgame, decide_postgame, postgame_ticks, record_dispatch,
)

import automation_state as AS  # noqa: E402
import conductor_health as CH  # noqa: E402
import horizon_conductor as HC  # noqa: E402

UTC = timezone.utc
TNF = datetime(2026, 9, 25, 0, 15, tzinfo=UTC)
GAMES = [{"game_id": "2026_03_ATL_GB", "kickoff_utc": TNF},
         {"game_id": "2026_03_CAR_CLE", "kickoff_utc": datetime(2026, 9, 27, 17, 0, tzinfo=UTC)},
         {"game_id": "2026_03_KC_MIA", "kickoff_utc": datetime(2026, 9, 27, 17, 0, tzinfo=UTC)}]


# ---------------------------------------------------------------- ticks

def test_the_first_tick_after_thursdays_game_is_due_before_the_owner_had_to_dispatch():
    at = TNF + timedelta(minutes=POSTGAME_OFFSETS_MIN[0])                 # 04:15Z
    ticks = postgame_ticks(GAMES, at)
    assert [t["tick_id"] for t in ticks] == ["POST|20260925T0015Z|+240m"]
    assert at < datetime(2026, 9, 25, 5, 1, tzinfo=UTC)
    assert postgame_ticks(GAMES, at - timedelta(minutes=1)) == []


def test_every_offset_opens_a_tick_and_a_cluster_is_one_tick_not_one_per_game():
    ko = datetime(2026, 9, 27, 17, 0, tzinfo=UTC)
    for off in POSTGAME_OFFSETS_MIN:
        ticks = postgame_ticks(GAMES, ko + timedelta(minutes=off + 1))
        assert len(ticks) == 1 and ticks[0]["games"] == ["2026_03_CAR_CLE", "2026_03_KC_MIA"]


def test_ticks_are_computed_from_kickoffs_not_from_the_active_week():
    """MNF's later ticks fall after the calendar has moved to the next week; they must still fire."""
    mnf = [{"game_id": "2026_03_PHI_CHI", "kickoff_utc": datetime(2026, 9, 29, 0, 15, tzinfo=UTC)}]
    assert postgame_ticks(mnf, datetime(2026, 9, 29, 13, 20, tzinfo=UTC))      # +13h tick, Tuesday morning


# ---------------------------------------------------------------- decisions (idempotency + retries)

T0 = TNF + timedelta(minutes=241)
TICK = postgame_ticks(GAMES, T0)


def test_a_new_tick_is_dispatched_once_and_an_active_run_is_never_stacked():
    att = {}
    assert decide_postgame(TICK, att, T0, 0, None)[0] is True
    record_dispatch(att, TICK, T0)
    assert decide_postgame(TICK, att, T0 + timedelta(minutes=30), 0, "success")[0] is False
    assert decide_postgame(TICK, {}, T0, 1, None)[0] is False


def test_a_failed_run_is_retried_after_the_wait_and_at_most_the_limit():
    att = {}
    record_dispatch(att, TICK, T0)
    assert decide_postgame(TICK, att, T0 + timedelta(minutes=5), 0, "failure")[0] is False
    t = T0
    for _ in range(POSTGAME_MAX_ATTEMPTS - 1):
        t += timedelta(minutes=POSTGAME_RETRY_MIN + 1)
        go, why = decide_postgame(TICK, att, t, 0, "failure")
        assert go and "retry" in why
        record_dispatch(att, TICK, t)
    go, why = decide_postgame(TICK, att, t + timedelta(minutes=POSTGAME_RETRY_MIN + 1), 0, "failure")
    assert go is False and "left red" in why


def test_the_postgame_pass_dispatches_each_workflow_once_per_tick():
    att, sent = {}, []

    def disp(wf, ref):
        sent.append((wf, ref))
        return True, "ok"
    kw = dict(active=lambda wf: 0, conclusion=lambda wf: "success", dispatcher=disp)
    lines = HC.postgame_pass(GAMES, T0, att, **kw)
    assert sorted(w for w, _ in sent) == sorted(POSTGAME_WORKFLOWS) and all(r == "main" for _, r in sent)
    assert all(ln["decision"] == "dispatch" for ln in lines)
    sent.clear()
    HC.postgame_pass(GAMES, T0 + timedelta(minutes=4), att, **kw)          # the next conductor pass
    assert sent == [], "a green postgame run was dispatched again for the same tick"
    # the next tick is a new decision moment
    HC.postgame_pass(GAMES, TNF + timedelta(minutes=POSTGAME_OFFSETS_MIN[1] + 1), att, **kw)
    assert len(sent) == len(POSTGAME_WORKFLOWS)


def test_a_refused_dispatch_is_not_recorded_so_the_next_pass_tries_again():
    att = {}
    HC.postgame_pass(GAMES, T0, att, active=lambda wf: 0, conclusion=lambda wf: None,
                     dispatcher=lambda wf, ref: (False, "HTTP 500"))
    assert att == {"postgame-settle.yml": {}, "actual-wagers.yml": {}, "shadow-v2-settle.yml": {}}


# ---------------------------------------------------------------- states

def test_states_of_a_finished_postgame_run():
    assert set(STATES) == {"WAITING_FOR_SOURCE", "RUNNING", "PARTIAL_COMPLETE", "COMPLETE", "BLOCKED"}
    c = classify_postgame
    assert c(gate_work="false", settle_status="", written="", deferred="")["state"] == "COMPLETE"
    assert c(gate_work="true", settle_status="NO_OP", written="0", deferred="1")["state"] == "WAITING_FOR_SOURCE"
    assert c(gate_work="true", settle_status="WROTE", written="40", deferred="1")["state"] == "PARTIAL_COMPLETE"
    assert c(gate_work="true", settle_status="WROTE", written="40", deferred="0")["state"] == "COMPLETE"
    assert c(gate_work="true", settle_status="CONFLICT", written="0", deferred="0")["state"] == "BLOCKED"
    assert c(gate_work="false", settle_status="", written="", deferred="", arms_status="CONFLICT")["state"] == "BLOCKED"
    assert c(gate_work="true", settle_status="", written="", deferred="", job_status="failure")["state"] == "BLOCKED"


def test_the_state_script_reads_the_step_outputs_and_never_fails(tmp_path):
    env = {"GATE_WORK": "true", "SETTLE_STATUS": "WROTE", "WRITTEN": "12", "DEFERRED": "2", "JOB_STATUS": "success",
           "GITHUB_EVENT_NAME": "workflow_dispatch", "GITHUB_TRIGGERING_ACTOR": "github-actions[bot]"}
    doc = AS.postgame_state(env)
    assert doc["state"] == "PARTIAL_COMPLETE" and doc["actor"] == "github-actions[bot]"
    summary = tmp_path / "s.md"
    old = dict(os.environ)
    try:
        os.environ.update(env)
        assert AS.main(["postgame", "--summary", str(summary)]) == 0
    finally:
        os.environ.clear()
        os.environ.update(old)
    assert "Automation state: **PARTIAL_COMPLETE**" in summary.read_text()


def test_the_postgame_workflow_reports_its_state_without_being_able_to_change_its_colour():
    wf = yaml.safe_load(open(os.path.join(ROOT, ".github", "workflows", "postgame-settle.yml")))
    steps = wf["jobs"]["settle"]["steps"]
    st = next(s for s in steps if "automation_state.py postgame" in (s.get("run") or ""))
    assert st["if"] == "always()" and st.get("continue-on-error") is True
    assert st["env"]["JOB_STATUS"] == "${{ job.status }}"
    names = [s.get("name") for s in steps]
    assert names.index(st["name"]) < names.index("Report outcome")


# ---------------------------------------------------------------- dead-chain alarm

NOW = datetime(2026, 9, 27, 12, 0, tzinfo=UTC)


def r(status="completed", conclusion="success", ended_min_ago=1):
    t = (NOW - timedelta(minutes=ended_min_ago)).isoformat()
    return {"status": status, "conclusion": conclusion, "createdAt": t, "updatedAt": t}


def test_chain_health():
    assert chain_health([r("in_progress", None)], NOW)["status"] == "ALIVE"
    assert chain_health([r("pending", None), r(ended_min_ago=400)], NOW)["status"] == "ALIVE"
    assert chain_health([r(ended_min_ago=2)], NOW)["status"] == "ALIVE"          # mid hand-off
    assert chain_health([r(conclusion="cancelled", ended_min_ago=90)], NOW)["status"] == "DEAD"
    assert chain_health([], NOW)["status"] == "DEAD"
    assert chain_health(None, NOW)["status"] == "ABSENT"


def test_a_dead_required_chain_is_red_and_restarted_once_an_optional_one_never_red():
    restarted = []
    runs = {"horizon-conductor.yml": [r(ended_min_ago=60)], "kalshi-conductor.yml": [r("in_progress", None)],
            "router-conductor.yml": None}
    rows, red = CH.evaluate(["horizon-conductor.yml", "kalshi-conductor.yml"],
                            ["chmoses98/kalshi-bet-router:router-conductor.yml"], NOW,
                            lister=lambda wf, repo=None: runs[wf],
                            restarter=lambda wf: (restarted.append(wf) or (True, "ok")), do_restart=True)
    assert red is True and restarted == ["horizon-conductor.yml"]
    by = {x["workflow"]: x for x in rows}
    assert by["chmoses98/kalshi-bet-router:router-conductor.yml"]["status"] == "ABSENT"
    rows, red = CH.evaluate(["kalshi-conductor.yml"], ["chmoses98/kalshi-bet-router:router-conductor.yml"], NOW,
                            lister=lambda wf, repo=None: runs[wf], restarter=lambda wf: (True, ""), do_restart=True)
    assert red is False


def test_workflow_health_wires_the_alarm_and_the_conductor_starts_the_postgame_target():
    wh = yaml.safe_load(open(os.path.join(ROOT, ".github", "workflows", "workflow-health.yml")))
    steps = wh["jobs"]["outcomes"]["steps"]
    chains = next(s for s in steps if s.get("id") == "chains")
    assert "--workflow horizon-conductor.yml" in chains["run"] and "--workflow kalshi-conductor.yml" in chains["run"]
    assert "--restart" in chains["run"] and chains.get("continue-on-error") is True
    red = next(s for s in steps if s.get("if") == "steps.chains.outcome == 'failure'")
    assert "exit 1" in red["run"]
    assert wh["permissions"]["actions"] == "write"
    hc = open(os.path.join(ROOT, ".github", "workflows", "horizon-conductor.yml")).read()
    assert "--targets RUN_NFL,THREE_ARM,POSTGAME" in hc
    for wf in POSTGAME_WORKFLOWS:
        doc = yaml.safe_load(open(os.path.join(ROOT, ".github", "workflows", wf)))
        on = doc.get(True, doc.get("on"))
        assert "workflow_dispatch" in on, f"{wf} cannot be started by the conductor"
        assert doc["concurrency"]["cancel-in-progress"] is False, f"{wf}: a duplicate start must queue, not cancel"
