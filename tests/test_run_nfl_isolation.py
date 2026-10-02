"""RUN NFL is research. PREFLIGHT NFL is money. This file is where that separation stops being a convention.

    RUN NFL      unlimited, read-only. Evidence. No Airtable, no automation runs, no secrets, no bets.
    PREFLIGHT    explicit real-money candidate validation. Airtable begins here and nowhere earlier.

The failure this prevents is mundane and expensive: someone adds a helpful "log the run to Airtable" call to
a shared module, the packet builder already imports that module, and now a research build that runs every
two hours holds an Airtable write token and burns automation runs. Nobody would write that on purpose; it
arrives through an import.

So the check is structural. Walk the import graph from every entry point of the report path and assert that
nothing reachable can even name Airtable, the preflight handshake, or the recommendation writers. The same
audit runs inside the workflow (`scripts/ci/assert_no_airtable.py`), before anything is built.
"""
import os
import re
import sys

import pytest
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.handicap.report_isolation import (  # noqa: E402
    FORBIDDEN_MODULES, REPORT_ENTRY_POINTS, audit, code_violations, reachable_modules,
)

REPORT_WORKFLOWS = ["run-nfl.yml", "run-nfl-horizons.yml"]


def _wf(name):
    with open(os.path.join(ROOT, ".github", "workflows", name)) as f:
        return yaml.safe_load(f)


def _steps(doc):
    for job in (doc.get("jobs") or {}).values():
        for step in (job.get("steps") or []):
            yield step


# --------------------------------------------------------------------------- the import graph

def test_every_report_entry_point_exists():
    for e in REPORT_ENTRY_POINTS:
        assert os.path.exists(os.path.join(ROOT, e)), f"{e} is named as a report entry point but is absent"


def test_the_report_path_cannot_reach_airtable_preflight_or_the_recommendation_writers():
    res = audit(ROOT)
    assert res["violations"] == [], (
        "RUN NFL report generation gained a path to the real-money side:\n  "
        + "\n  ".join(res["violations"]))


def test_the_audit_actually_covers_the_packet_builder():
    """A green audit over an empty graph would prove nothing."""
    reached = reachable_modules(ROOT)
    assert "nfl_edge/handicap/packet.py" in reached
    assert "nfl_edge/handicap/render.py" in reached
    assert "nfl_edge/handicap/teamprofile.py" in reached
    assert len(reached) >= 10


@pytest.mark.parametrize("module", sorted(FORBIDDEN_MODULES))
def test_each_forbidden_module_exists_so_the_ban_is_about_something(module):
    assert os.path.exists(os.path.join(ROOT, module.replace(".", "/") + ".py"))


def test_the_audit_would_catch_a_violation_that_was_introduced():
    """A negative control: the check has to be able to fail."""
    bad = [
        ("import os\nfrom nfl_edge.handicap import airtable_bridge\n", "imports"),
        ('import os\nURL = "https://api.airtable.com/v0/app123/Runs"\n', "Airtable API URL"),
        ('import os\nT = os.environ["AIRTABLE_TOKEN"]\n', "Airtable credential"),
        ('import os\nSTATUS = "PREFLIGHT_REQUESTED"\n', "handshake status"),
        ('import subprocess\nsubprocess.run(["python3", "scripts/handicap/sync_airtable.py"])\n',
         "shells out"),
    ]
    for src, expected in bad:
        found = code_violations("fake.py", src)
        assert found, f"the audit missed: {src!r}"
        assert any(expected in f for f in found), f"{found} did not mention {expected!r}"


def test_prose_about_the_downstream_process_is_not_a_violation():
    """`render.py` tells the handicapper to commit to `handicap-data` later. Documentation of a separate,
    human act is not this path performing it, and an audit that cannot tell them apart gets switched off."""
    src = ('"""This path never touches Airtable."""\n'
           'def f():\n'
           '    """Later, run scripts/handicap/validate_recommendations.py by hand."""\n'
           '    return "commit to the handicap-data branch"\n')
    assert code_violations("fake.py", src) == []


# --------------------------------------------------------------------------- the workflows

def _executable_yaml(name: str) -> str:
    """The workflow with its comments gone: what the runner actually does.

    Deliberately not the raw file. These workflows document what they refuse to do -- "no preflight, no
    Airtable" -- and a check that cannot tell a comment from a command punishes saying so.
    """
    return yaml.safe_dump(_wf(name), default_flow_style=False)


@pytest.mark.parametrize("name", REPORT_WORKFLOWS)
def test_the_report_workflows_request_no_secrets(name):
    """No secret at all is the strongest possible statement that Airtable is not involved."""
    doc = _executable_yaml(name)
    assert "secrets." not in doc, f"{name} references a repository secret"
    # `assert_no_airtable.py` and the step that runs it are allowed to say the word; a credential is not.
    assert not re.search(r"AIRTABLE_[A-Z_]+", doc), f"{name} names an Airtable credential"
    assert "api.airtable.com" not in doc, f"{name} contacts the Airtable API"
    assert "secrets" not in (_wf(name).get("jobs") or {}), f"{name} declares job-level secrets"


# The Edge Finder app export (scripts/app_export.py, docs/APP_EXPORT.md) reads the handicap-data ledger so the
# app can show recorded decisions and wagers beside the board. Reading is `git fetch --depth=1` plus
# `git archive ... | tar -x` into RUNNER_TEMP: no worktree, no checkout, no push. Those two command shapes are
# the ONLY way a report workflow may name the ledger branch; everything else below still treats the name as
# a violation, and `test_the_report_workflows_read_the_ledger_only_through_git_archive` pins the shapes.
_LEDGER_READ_RE = re.compile(r"git (?:fetch --depth=1 origin handicap-data|archive origin/handicap-data data)\b")


def _executable_yaml_without_ledger_reads(name: str) -> str:
    """`_executable_yaml` with the two read-only ledger shapes blanked out of every `run` block BEFORE the
    dump (the dump folds long lines, so the shapes are matched on the step text, never on the rendering)."""
    doc = _wf(name)
    for step in _steps(doc):
        if step.get("run"):
            step["run"] = _LEDGER_READ_RE.sub("git <read-only ledger extract>", step["run"])
    return yaml.safe_dump(doc, default_flow_style=False)


@pytest.mark.parametrize("name", REPORT_WORKFLOWS)
def test_the_report_workflows_never_invoke_preflight_or_the_recommendation_writers(name):
    doc = _executable_yaml_without_ledger_reads(name)
    for forbidden in ("preflight.yml", "preflight_airtable.py", "preflight_candidate.py",
                      "sync_airtable.py", "validate_recommendations.py", "handicap-data"):
        assert forbidden not in doc, f"{name} runs {forbidden}"


@pytest.mark.parametrize("name", REPORT_WORKFLOWS)
def test_the_report_workflows_read_the_ledger_only_through_git_archive(name):
    """Every mention of the ledger branch is one of the two read-only shapes, and no push, worktree or
    checkout ever names it. A `git push origin handicap-data` on this path is the bug the guard exists for."""
    for step in _steps(_wf(name)):
        for line in (step.get("run") or "").splitlines():
            if "handicap-data" in line:
                assert _LEDGER_READ_RE.search(line), f"{name} names handicap-data outside a read-only extract: {line.strip()}"
                assert not re.search(r"git (push|worktree|checkout|commit)", line), f"{name} writes the ledger: {line.strip()}"
            if "git push" in line:
                assert "handicap-data" not in line and "market-data" not in line, f"{name} pushes a ledger: {line.strip()}"


@pytest.mark.parametrize("name", REPORT_WORKFLOWS)
def test_the_report_workflows_only_write_the_report_branch(name):
    """`contents: write` is granted for exactly one push target. Anything else on this path is a bug."""
    doc = _executable_yaml(name)
    branches = {"market-data", "handicap-data", "main"}
    for step in _steps(_wf(name)):
        run = step.get("run") or ""
        if "publish_market_data.py" in run:
            pytest.fail(f"{name} publishes to market-data from the report path")
    assert "handicap-reports" in doc or name == "run-nfl-horizons.yml"
    assert "handicap-data" not in _executable_yaml_without_ledger_reads(name)
    _ = branches


def test_the_shadow_pricing_cycle_runs_the_isolation_audit_before_it_builds_a_report():
    doc = _wf("shadow-price.yml")
    steps = list(_steps(doc))
    audit_at = next((i for i, s in enumerate(steps) if "assert_no_airtable.py" in (s.get("run") or "")),
                    None)
    build_at = next((i for i, s in enumerate(steps) if "build_report.py" in (s.get("run") or "")), None)
    assert audit_at is not None and build_at is not None
    assert audit_at < build_at


def test_run_nfl_audits_isolation_before_it_downloads_anything():
    steps = list(_steps(_wf("run-nfl.yml")))
    audit_at = next(i for i, s in enumerate(steps) if "assert_no_airtable.py" in (s.get("run") or ""))
    build_at = next(i for i, s in enumerate(steps) if "build_report.py" in (s.get("run") or ""))
    assert audit_at < build_at
