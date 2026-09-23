"""The three 2026-09-22 'cancelled' runs were three different events; the classifier names each one."""
import importlib.util
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("_wo", os.path.join(ROOT, "scripts", "ops", "workflow_outcomes.py"))
WO = importlib.util.module_from_spec(spec); spec.loader.exec_module(WO)


def run(concl, status="completed", updated="2026-09-22T01:48:21Z"):
    return {"status": status, "conclusion": concl, "updated_at": updated}


def job(start, end, steps=()):
    return {"started_at": start, "completed_at": end, "steps": list(steps)}


def test_timeout_reported_as_cancelled_is_named_a_timeout():
    c = WO.classify(run("cancelled"), [job("2026-09-22T00:17:55Z", "2026-09-22T01:48:21Z")], 90)
    assert c["outcome"] == "TIMED_OUT"


def test_a_mid_run_cancel_is_external():
    c = WO.classify(run("cancelled"), [job("2026-09-22T17:19:02Z", "2026-09-22T17:27:00Z")], 90)
    assert c["outcome"] == "EXTERNALLY_CANCELLED" and "8.0 min" in c["detail"]


def test_a_pending_run_superseded_by_concurrency():
    assert WO.classify(run("cancelled"), [], 358)["outcome"] == "CANCELLED_BY_CONCURRENCY"


def test_failures_are_split_into_code_and_publication():
    j = job("a", "b", [{"name": "Settle", "conclusion": "success"}, {"name": "Publish the evidence", "conclusion": "failure"}])
    assert WO.classify(run("failure"), [dict(j, started_at="2026-09-22T00:00:00Z", completed_at="2026-09-22T00:05:00Z")], 90)["outcome"] == "PUBLICATION_FAILED"
    j2 = job("2026-09-22T00:00:00Z", "2026-09-22T00:05:00Z", [{"name": "Settle every ready game", "conclusion": "failure"}])
    assert WO.classify(run("failure"), [j2], 90)["outcome"] == "FAILED_BY_CODE"
    assert WO.classify(run("success"), [], 90)["outcome"] == "SUCCESS"


def test_the_timeout_is_read_from_the_workflow_file():
    assert WO.job_timeout_minutes("jobs:\n  a:\n    timeout-minutes: 10\n  b:\n    timeout-minutes: 90\n") == 90.0
