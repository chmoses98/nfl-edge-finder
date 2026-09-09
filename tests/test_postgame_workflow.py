"""The postgame workflow's safety properties, checked as text because that is all a workflow is until it runs.

The general workflow tests (tests/test_workflows_parse.py) already prove every file parses, has pipefail where
it pipes, and calls scripts that exist. These are the properties specific to a job that publishes to an
immutable corpus:

  * the expensive steps are behind the cheap gate, or a 3-hourly poll downloads parquet to learn nothing;
  * nothing is published before it is validated;
  * the git identity exists before the first publish (the failure that silently lost shocks for days);
  * a conflict fails the run rather than being reported as a success with zero rows;
  * the job never writes to the ledger it reads.
"""
import os
import re

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, ".github", "workflows", "postgame-settle.yml")


def doc():
    with open(PATH) as f:
        return yaml.safe_load(f)


def steps():
    return doc()["jobs"]["settle"]["steps"]


def step_index(pattern):
    for i, s in enumerate(steps()):
        if re.search(pattern, (s.get("run") or "") + " " + str(s.get("uses") or "")):
            return i
    return None


def test_the_workflow_polls_on_a_schedule_and_can_be_run_by_hand():
    d = doc()
    on = d.get(True, d.get("on"))
    crons = [c["cron"] for c in on["schedule"]]
    assert crons == ["19 */3 * * *"], (
        "a 3-hourly poll settles a slate the same evening; the offset keeps it off the hour with every other job")
    assert "workflow_dispatch" in on
    inputs = on["workflow_dispatch"]["inputs"]
    assert {"games", "lookback_days", "dry_run"} <= set(inputs), "manual recovery needs to name games"


def test_the_job_has_concurrency_protection_and_pipefail():
    d = doc()
    assert d["concurrency"]["group"] == "postgame-settle"
    assert d["concurrency"]["cancel-in-progress"] is False, (
        "cancelling a run mid-publish would leave a batch written and unpublished")
    assert "pipefail" in d["defaults"]["run"]["shell"]


def test_expensive_steps_run_only_when_the_gate_found_work():
    """Otherwise every 3-hourly poll downloads player statistics to discover no game finished."""
    gated = []
    for s in steps():
        run = s.get("run") or ""
        if "stats_player" in run or "settle_games.py" in run:
            gated.append(s)
    assert gated, "the heavy steps were not found"
    for s in gated:
        cond = s.get("if") or ""
        assert "steps.gate.outputs.work" in cond, f"step {s.get('name')!r} is not behind the gate"


def test_the_gate_itself_downloads_only_the_schedule():
    gate = steps()[step_index("settle_gate.py")]
    assert "--only schedules" in gate["run"]
    assert "stats_player" not in gate["run"] and "pbp" not in gate["run"]


def test_nothing_is_published_before_it_is_validated():
    v = step_index("validate_evaluations.py")
    p = step_index("publish_market_data.py --src data/shadow/evaluations")
    assert v is not None and p is not None
    assert v < p, "validation must run before the publish, not after it"
    validate = steps()[v]
    assert "--market-data" in validate["run"], "the ledger's immutability is part of what is validated"
    assert "--require-rows" in validate["run"], "validating zero rows must not count as a pass"


def test_the_git_identity_is_configured_before_the_first_publish():
    identity = step_index("git config user.name")
    publishes = [i for i, s in enumerate(steps()) if "publish_market_data" in (s.get("run") or "")]
    assert identity is not None and publishes
    assert identity < min(publishes)


def test_the_publish_steps_are_reached_only_after_something_was_written():
    for s in steps():
        if "publish_market_data" in (s.get("run") or ""):
            assert "steps.settle.outputs.status == 'WROTE'" in (s.get("if") or ""), s.get("name")
            assert "dry_run" in (s.get("if") or ""), "a dry run must never publish"


def test_a_conflict_fails_the_run():
    outcome = steps()[-1]
    assert outcome.get("if") == "always()"
    assert "CONFLICT" in outcome["run"] and "exit 1" in outcome["run"], (
        "a contradicted evaluation must fail the run, not be reported as a green no-op")


def test_the_job_never_writes_to_the_ledger_or_the_capture():
    """A settle run reads the published ledger. Any publish of those paths from here would be a rewrite."""
    src = open(PATH).read()
    for path in ("--src data/shadow/ledger", "--src data/kalshi", "--src data/shocks"):
        assert path not in src, f"the postgame job must not publish {path}"
    assert "--src data/shadow/evaluations" in src and "--src data/shadow/scorecards" in src


def test_the_immutable_product_is_published_before_the_derived_report():
    evaluations = step_index(r"publish_market_data\.py --src data/shadow/evaluations")
    report = step_index("eval_report.py")
    scorecards = step_index(r"publish_market_data\.py --src data/shadow/scorecards")
    assert evaluations < report < scorecards, (
        "the corpus is the product; the scorecard is derived from it and can always be rebuilt")
    assert steps()[report].get("continue-on-error") is True, (
        "a report failure must not fail a run whose corpus is already published")
    assert steps()[evaluations].get("continue-on-error") is not True, (
        "a failure to publish the corpus is a real failure")


def test_the_run_reports_what_it_did_even_when_it_did_nothing():
    outcome = steps()[-1]["run"]
    for token in ("gate work=", "settle status=", "written=", "deferred="):
        assert token in outcome, token
    assert "::notice::" in outcome, "a no-work run should say so rather than looking like a failure"
