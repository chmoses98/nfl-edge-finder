"""Failure semantics of the recurring workflows: red only for something a person must act on.

Each test pins one behaviour change made after reading the Actions history of 2026-09-11 .. 2026-10-02:

  * shadow-v2-settle: the DERIVED research rebuild ran into the 90-minute job limit on ~28 consecutive runs
    (2026-09-27 .. 10-01, e.g. 36937919712) after the write-once settlement evidence was already published, so
    every run ended TIMED_OUT. The step now has its own limit; a rebuild that fails or overruns is DEGRADED.
  * context-capture: a single source failing closed in one 3-hourly run (36382280662) turned the collector red
    while the rest of the capture was published. Partial = DEGRADED; nothing captured or a crash = FAILED.
  * horizon gates: one dropped connection to the nflverse schedule release made a gate red with exit 6
    (34770263696, 36464087768). The download is now retried a bounded number of times, then fails closed.
  * shadow-price: an artifact-service 403 on the report artifact (35668066839) failed the pricing job whose
    ledger was already published, contrary to the workflow's own "nothing below can fail the pricing job".

Everything here is deterministic: no network, no clock, no committed market data.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import subprocess
import sys

import pytest
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.data import nfl_calendar as CAL                                    # noqa: E402
from nfl_edge.handicap.automation import HEALTH_STATES, classify_shadow_v2_settle  # noqa: E402

WF = os.path.join(ROOT, ".github", "workflows")


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _wf(name):
    with open(os.path.join(WF, name)) as f:
        return yaml.safe_load(f)


def _steps(name, job):
    return _wf(name)["jobs"][job]["steps"]


def _step(name, job, step_name):
    return next(s for s in _steps(name, job) if s.get("name") == step_name)


# ===================================================================== schedule download: bounded retry
SCHEDULE_CSV = ("game_id,season,week,game_type,gameday,gametime,away_team,home_team,result\n"
                "2026_05_KC_BUF,2026,5,REG,2026-10-04,13:00,KC,BUF,\n")


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _opener(failures: int, calls: list):
    def opener(req, timeout=None):
        calls.append(req.full_url)
        if len(calls) <= failures:
            raise OSError("connection reset by peer")
        return _Resp(SCHEDULE_CSV.encode())
    return opener


def test_a_transient_schedule_download_failure_is_retried_then_succeeds(tmp_path):
    calls, slept = [], []
    games, src = CAL.load_schedule(str(tmp_path), allow_download=True, download_attempts=3, retry_wait_s=10,
                                   _urlopen=_opener(2, calls), _sleep=slept.append)
    assert src == CAL.SCHEDULE_URL
    assert [g["game_id"] for g in games] == ["2026_05_KC_BUF"]
    assert len(calls) == 3 and slept == [10, 20], "bounded, growing backoff between attempts"


def test_a_persistent_schedule_outage_still_fails_closed_after_the_last_attempt(tmp_path):
    calls, slept = [], []
    with pytest.raises(OSError):
        CAL.load_schedule(str(tmp_path), allow_download=True, download_attempts=3,
                          _urlopen=_opener(99, calls), _sleep=slept.append)
    assert len(calls) == 3, "never more than the bound"
    assert len(slept) == 2, "no sleep after the final attempt"


def test_the_default_is_still_a_single_attempt(tmp_path):
    calls = []
    with pytest.raises(OSError):
        CAL.load_schedule(str(tmp_path), allow_download=True, _urlopen=_opener(1, calls), _sleep=lambda s: None)
    assert len(calls) == 1, "callers that did not opt in (e.g. the packet builder) keep their timing"


def test_a_local_schedule_never_touches_the_network(tmp_path):
    p = tmp_path / "data" / "raw" / "nflverse" / "schedules"
    p.mkdir(parents=True)
    (p / "games.csv").write_text(SCHEDULE_CSV)

    def opener(*a, **k):
        raise AssertionError("downloaded although a schedule was on disk")
    games, src = CAL.load_schedule(str(tmp_path), allow_download=True, download_attempts=3, _urlopen=opener)
    assert src.endswith("games.csv") and len(games) == 1


@pytest.mark.parametrize("script", ["scripts/handicap/horizon_gate.py", "scripts/shadow/three_arm_horizon_gate.py",
                                    "scripts/shadow_v2/horizon_gate_v2.py"])
def test_every_horizon_gate_opts_into_the_bounded_retry(script):
    src = open(os.path.join(ROOT, script)).read()
    assert "download_attempts=3" in src, f"{script} would go red on one dropped schedule download"
    assert "return 6" in src, f"{script} must still fail closed when the schedule cannot be read at all"


# ===================================================================== context capture: HEALTHY / DEGRADED / FAILED
CC = _load("scripts/data/context_capture.py", "_context_capture_under_test")


def _man(failed=(), ok=("schedule", "sleeper_players", "espn_injuries")):
    sources = {s: {"status": 200 if s in ok else 503} for s in CC.PRIMARY_SOURCES}
    return {"sources": sources, "failed_closed": list(failed)}


def test_capture_health_classification():
    assert CC.capture_health(_man()) == "HEALTHY"
    assert CC.capture_health(_man(["espn injuries unavailable"], ok=("schedule", "sleeper_players"))) == "DEGRADED"
    assert CC.capture_health(_man(["schedule unavailable: no weather rows written"],
                                  ok=("sleeper_players", "espn_injuries"))) == "DEGRADED"
    assert CC.capture_health(_man(["schedule unavailable: no weather rows written", "sleeper unavailable",
                                   "espn injuries unavailable"], ok=())) == "FAILED"


def _fake_try_get(fail: set):
    def try_get(url, timeout=60):
        name = ("schedule" if "games.csv" in url else "sleeper_players" if "players/nfl" in url
                else "sleeper_state" if "state/nfl" in url else "espn_injuries" if "injuries" in url else url)
        if name in fail:
            return None, {"status": 503, "error": "unavailable", "retrieved_at": "2026-10-02T00:00:00+00:00"}
        body = {"schedule": b"game_id,season,week,gameday,gametime,home_team,away_team,result\n",
                "sleeper_players": b"{}", "sleeper_state": b"{}", "espn_injuries": b'{"injuries": []}'}[name]
        return body, {"status": 200, "bytes": len(body), "retrieved_at": "2026-10-02T00:00:00+00:00"}
    return try_get


@pytest.mark.parametrize("fail,health,rc", [
    (set(), "HEALTHY", 0),
    ({"espn_injuries"}, "DEGRADED", 2),
    ({"schedule", "sleeper_players", "sleeper_state", "espn_injuries"}, "FAILED", 2),
])
def test_the_capture_records_its_health_and_keeps_its_exit_code(tmp_path, monkeypatch, fail, health, rc):
    """The exit code is unchanged (2 on any failed-closed source): RUN NFL's fresh capture relies on it."""
    monkeypatch.setattr(CC, "OUT", str(tmp_path / "context"))
    monkeypatch.setattr(CC, "try_get", _fake_try_get(fail))
    out = tmp_path / "gh_output"
    assert CC.main(["--github-output", str(out)]) == rc
    lines = dict(ln.split("=", 1) for ln in out.read_text().splitlines())
    assert lines["health"] == health
    manifests = list((tmp_path / "context").glob("*/*.manifest.json"))
    assert len(manifests) == 1 and json.loads(manifests[0].read_text())["health"] == health


def test_without_the_flag_nothing_is_written_to_a_github_output(tmp_path, monkeypatch):
    """RUN NFL runs the script inside its own steps; it must not receive extra step outputs implicitly."""
    gh = tmp_path / "gh_output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(gh))
    monkeypatch.setattr(CC, "OUT", str(tmp_path / "context"))
    monkeypatch.setattr(CC, "try_get", _fake_try_get(set()))
    assert CC.main([]) == 0
    assert not gh.exists()


def _run_enforcement(tmp_path, health, failed_closed="", outcome="failure"):
    run = _step("context-capture.yml", "context", "Capture health")["run"]
    summary = tmp_path / "summary.md"
    env = {**os.environ, "HEALTH": health, "FAILED_CLOSED": failed_closed, "CAP_OUTCOME": outcome,
           "GITHUB_STEP_SUMMARY": str(summary)}
    p = subprocess.run(["bash", "-eo", "pipefail", "-c", run], env=env, capture_output=True, text=True)
    return p.returncode, p.stdout, summary.read_text() if summary.exists() else ""


def test_context_capture_workflow_is_green_when_healthy(tmp_path):
    rc, out, summary = _run_enforcement(tmp_path, "HEALTHY", outcome="success")
    assert rc == 0 and "HEALTHY" in summary and "::warning::" not in out


def test_context_capture_workflow_is_green_with_a_warning_when_degraded(tmp_path):
    rc, out, summary = _run_enforcement(tmp_path, "DEGRADED", "espn injuries unavailable")
    assert rc == 0, "a partial capture is published and retried; it is not a red run"
    assert "::warning::" in out and "espn injuries unavailable" in out
    assert "DEGRADED" in summary


@pytest.mark.parametrize("health", ["FAILED", ""])
def test_context_capture_workflow_is_red_when_nothing_was_captured_or_the_capture_crashed(tmp_path, health):
    rc, out, summary = _run_enforcement(tmp_path, health)
    assert rc == 1 and "::error::" in out and "FAILED" in summary


def test_context_capture_workflow_has_one_enforcement_step():
    steps = _steps("context-capture.yml", "context")
    cap = next(s for s in steps if s.get("id") == "cap")
    assert cap.get("continue-on-error") is True, "a partial capture must still reach the publish step"
    assert '--github-output "$GITHUB_OUTPUT"' in cap["run"]
    exits = [s.get("name") for s in steps if "exit 1" in (s.get("run") or "")]
    assert exits == ["Capture health"], f"exactly one step may fail the run, found {exits}"
    assert _step("context-capture.yml", "context", "Capture health")["if"] == "always()"


# ===================================================================== shadow-v2-settle: derived rebuild is bounded
def test_shadow_v2_settle_health_states():
    assert set(HEALTH_STATES) == {"HEALTHY", "DEGRADED", "FAILED", "NOT_APPLICABLE"}
    c = classify_shadow_v2_settle
    # the 2026-09-27..10-01 shape: evidence published, derived rebuild killed/overran
    assert c(settle_status="WROTE", closes_status="WROTE", evidence_publish="success", research="failure",
             research_publish="", job_status="success")["health"] == "DEGRADED"
    # nothing new owed, derived rebuild overran (36553751963: evidence publish skipped)
    assert c(settle_status="NOTHING_TO_DO", closes_status="NOTHING_TO_DO", index_written="0",
             evidence_publish="skipped", research="failure", research_publish="skipped",
             job_status="success")["health"] == "DEGRADED"
    assert c(settle_status="WROTE", closes_status="NOTHING_TO_DO", evidence_publish="success", research="success",
             research_publish="success", job_status="success")["health"] == "HEALTHY"
    assert c(settle_status="NOTHING_TO_DO", closes_status="NOTHING_TO_DO", index_written="0",
             evidence_publish="skipped", research="success", research_publish="success",
             job_status="success")["health"] == "NOT_APPLICABLE"


@pytest.mark.parametrize("kw", [
    dict(settle_status="WROTE", evidence_publish="failure", research="", research_publish="", job_status="failure"),
    dict(settle_status="", evidence_publish="", research="", research_publish="", job_status="failure"),
    dict(settle_status="WROTE", evidence_publish="success", research="success", research_publish="failure",
         job_status="failure"),
])
def test_shadow_v2_settle_evidence_or_publish_failures_stay_failed(kw):
    assert classify_shadow_v2_settle(closes_status="", **kw)["health"] == "FAILED"


def test_the_state_line_warns_on_degraded_and_never_fails(tmp_path, monkeypatch, capsys):
    AS = _load("scripts/ops/automation_state.py", "_automation_state_under_test")
    for k, v in {"SETTLE_STATUS": "WROTE", "CLOSES_STATUS": "WROTE", "INDEX_WRITTEN": "3",
                 "EVIDENCE_PUBLISH": "success", "RESEARCH": "failure", "RESEARCH_PUBLISH": "",
                 "JOB_STATUS": "success"}.items():
        monkeypatch.setenv(k, v)
    summary, out = tmp_path / "summary.md", tmp_path / "state.json"
    assert AS.main(["shadow-v2-settle", "--summary", str(summary), "--out", str(out)]) == 0
    printed = capsys.readouterr().out
    assert "::warning::shadow-v2-settle DEGRADED" in printed
    doc = json.loads(out.read_text())
    assert doc["pipeline"] == "shadow-v2-settle" and doc["health"] == doc["state"] == "DEGRADED"
    assert "DEGRADED" in summary.read_text()


def test_the_postgame_state_line_is_unchanged(monkeypatch, capsys):
    AS = _load("scripts/ops/automation_state.py", "_automation_state_under_test2")
    for k in ("GATE_WORK", "SETTLE_STATUS", "WRITTEN", "DEFERRED", "ARMS_STATUS", "AUTOPSY_STATUS", "JOB_STATUS",
              "INPUT_GAMES"):
        monkeypatch.delenv(k, raising=False)
    assert AS.main(["postgame"]) == 0
    assert json.loads(capsys.readouterr().out.splitlines()[0])["state"] == "COMPLETE"


def test_shadow_v2_settle_bounds_the_derived_rebuild_inside_the_job_budget():
    job = _wf("shadow-v2-settle.yml")["jobs"]["settle"]
    research = next(s for s in job["steps"] if s.get("id") == "research")
    assert research.get("continue-on-error") is True
    step_limit = int(research["timeout-minutes"])
    # observed evidence path (fetch + settle + closes + publish) peaked at ~46 min; derived publish ~4 min
    assert 46 + step_limit + 4 + 10 <= int(job["timeout-minutes"]), (
        "the derived rebuild's own limit must end before the JOB limit can, or the run is TIMED_OUT again")
    names = [s.get("name") for s in job["steps"]]
    assert names.index("Publish the settlement, close and CLV batches, autopsies and scorecard") < \
        names.index("Rebuild the research export, scorecard v3, weekly report and health gate")


def test_shadow_v2_settle_reports_its_health_on_every_run():
    steps = _steps("shadow-v2-settle.yml", "settle")
    health = steps[-1]
    assert health["name"] == "Run health" and health["if"] == "always()"
    assert "automation_state.py shadow-v2-settle" in health["run"]
    env = health["env"]
    assert env["RESEARCH"] == "${{ steps.research.outcome }}"
    assert env["RESEARCH_PUBLISH"] == "${{ steps.research_publish.outcome }}"
    assert env["EVIDENCE_PUBLISH"] == "${{ steps.publish_evidence.outcome }}"
    assert any(s.get("id") == "research_publish" and "continue-on-error" not in s for s in steps), (
        "a derived export that cannot be published stays a red run")


# ===================================================================== shadow-price: the report artifact is not fatal
def test_shadow_price_report_artifact_upload_cannot_fail_the_pricing_job():
    steps = _steps("shadow-price.yml", "price")
    upload = next(s for s in steps if s.get("name") == "Upload the report artifact")
    assert upload.get("id") == "upload_report" and upload.get("continue-on-error") is True
    latest = next(s for s in steps if s.get("name") == "Publish the browsable latest report")
    assert "steps.upload_report.outcome == 'success'" in latest["if"], (
        "latest/ names the artifact in its manifest; it must not be replaced by a packet whose artifact is missing")
    outcome = next(s for s in steps if s.get("name") == "Report outcome")
    assert "steps.upload_report.outcome" in outcome["run"] and "::warning::" in outcome["run"]
    ledger = [s.get("name") for s in steps].index("Publish ledger")
    assert "continue-on-error" not in steps[ledger], "the ledger publish itself must stay fatal"
