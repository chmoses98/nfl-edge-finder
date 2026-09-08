"""The secrets have to reach the PROCESS, not merely exist in the repository.

The reviewed defect lived entirely in YAML and was invisible to every unit test in this suite, because the
unit tests inject `signing_key=` directly and so always have one:

    - name: Check the approval signing secret is configured     <- proves the secret EXISTS
      env:
        PREFLIGHT_SIGNING_KEY: ${{ secrets.PREFLIGHT_SIGNING_KEY }}
      run: ...

    - name: Sync pending handicap runs                          <- runs the importer WITHOUT it
      env:
        AIRTABLE_TOKEN: ${{ secrets.AIRTABLE_TOKEN }}
      run: python3 scripts/handicap/sync_airtable.py ...

A step's `env:` is scoped to that step. The workflow could therefore prove the key existed, start a new step
without it, and have the importer conclude that no signing key was available -- refusing a correctly signed,
gate-passing recommendation because the runner was wired wrong. A check in an earlier step is not evidence
about a later one, and this file is what says so.

Two halves, both necessary:

  * the STRUCTURAL half reads the actual YAML and asserts each script gets the environment it reads;
  * the BEHAVIOURAL half asserts that when it does not, a good row survives to be imported later.

Neither is redundant. Structure without behaviour would have let the importer condemn the row anyway;
behaviour without structure is what let the wiring bug ship.

The follow-up review found the same lesson one step earlier: the importer's per-row disposition -- defer the
real recommendation, still import the passes -- is unreachable unless the importer RUNS. The sync workflow's
preliminary signing-key check exited 1, so in production the job stopped before any of that logic. Section E
executes the check steps' actual shell bodies: the pre-trade WORKER hard-fails without a key (it can sign
nothing), the ARCHIVAL IMPORTER only warns (a pass needs no approval), and AIRTABLE_TOKEN stays a hard
prerequisite for both because nothing can be read without it.
"""
import glob
import json
import os
import re
import subprocess
import sys

import pytest
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts", "handicap"))

from nfl_edge.handicap import airtable_bridge as AB   # noqa: E402
from nfl_edge.handicap import approval as APPROVAL    # noqa: E402
from nfl_edge.handicap import store                   # noqa: E402
import sync_airtable                                  # noqa: E402

from tests.test_airtable_bridge import (               # noqa: E402
    FakeAirtable, approved_row, gate_ctx, ledger, rec, run_sync, _real, SIGNING_KEY,
)

_ = ledger  # re-exported pytest fixture; imported for use, not decoration

WORKFLOWS = os.path.join(ROOT, ".github", "workflows")
SYNC_YML = os.path.join(WORKFLOWS, "sync-handicap-airtable.yml")
PREFLIGHT_YML = os.path.join(WORKFLOWS, "preflight.yml")

TOKEN_ENV = "AIRTABLE_TOKEN"
KEY_ENV = APPROVAL.SIGNING_KEY_ENV          # "PREFLIGHT_SIGNING_KEY"


def _doc(path):
    with open(path) as f:
        return yaml.safe_load(f)


def _steps(doc):
    for job_name, job in (doc.get("jobs") or {}).items():
        for step in (job.get("steps") or []):
            yield job_name, step


def _step_calling(doc, script):
    """The step that actually RUNS the script -- not a step that merely mentions the secret."""
    hits = [s for _job, s in _steps(doc) if script in (s.get("run") or "")]
    assert len(hits) == 1, f"expected exactly one step running {script}, found {len(hits)}"
    return hits[0]


def _env_of(step):
    return step.get("env") or {}


# ---- A. the pre-trade worker gets both secrets --------------------------------------------------------

def test_A_the_preflight_worker_step_receives_both_secrets():
    """preflight_airtable.py reads AIRTABLE_TOKEN and signs with PREFLIGHT_SIGNING_KEY."""
    step = _step_calling(_doc(PREFLIGHT_YML), "scripts/handicap/preflight_airtable.py")
    env = _env_of(step)
    for name in (TOKEN_ENV, KEY_ENV):
        assert name in env, (
            f"the preflight worker step does not declare {name}. Without it the worker cannot sign an "
            "approval, and an unsigned approval can never be archived.")
        assert f"secrets.{name}" in str(env[name]), \
            f"{name} must come from the repository secret, not a literal"


# ---- B. the importer gets both secrets ----------------------------------------------------------------

def test_B_the_sync_step_receives_both_secrets():
    """THE REGRESSION. sync_airtable.py verifies the approval signature; it needs the same key."""
    step = _step_calling(_doc(SYNC_YML), "scripts/handicap/sync_airtable.py")
    env = _env_of(step)
    for name in (TOKEN_ENV, KEY_ENV):
        assert name in env, (
            f"the sync step does not declare {name}, so the importer runs without it. This is the exact "
            "defect: a valid, signed, gate-passing recommendation would be refused because the RUNNER was "
            "misconfigured.")
        assert f"secrets.{name}" in str(env[name]), \
            f"{name} must come from the repository secret, not a literal"


@pytest.mark.parametrize("path,script", [
    (SYNC_YML, "scripts/handicap/sync_airtable.py"),
    (PREFLIGHT_YML, "scripts/handicap/preflight_airtable.py"),
], ids=["sync", "preflight"])
def test_every_secret_the_script_reads_is_declared_on_the_step_that_runs_it(path, script):
    """Derived from the SCRIPT, not from a hand-written list, so a newly read secret cannot be forgotten.

    Whatever `os.environ.get("X")` the script reads at module or main level must appear in the env of the
    step that invokes it. This is the general form of the defect above.
    """
    src = open(os.path.join(ROOT, script)).read()
    read = set(re.findall(r"os\.environ(?:\.get)?[\(\[]\s*[\"']([A-Z][A-Z0-9_]+)[\"']", src))
    # The signing key is read one level down, in approval.signing_key(); the script calls it by name.
    if f"{APPROVAL.__name__.split('.')[-1].upper()}.signing_key()" in src or "signing_key()" in src:
        read.add(KEY_ENV)
    env = _env_of(_step_calling(_doc(path), script))
    missing = sorted(name for name in read if name not in env)
    assert not missing, (
        f"{os.path.basename(path)}: the step running {script} does not pass {missing}, but the script reads "
        f"them from its own environment")


# ---- C. neither secret is ever placed on argv ---------------------------------------------------------

@pytest.mark.parametrize("path", sorted(glob.glob(os.path.join(WORKFLOWS, "*.yml"))),
                         ids=lambda p: os.path.basename(p))
def test_C_no_secret_is_passed_on_a_command_line(path):
    """argv is world-readable on the runner; `env:` is not. Secrets are passed one way only.

    This checks the `run:` bodies of every workflow, not just these two: a secret interpolated into a shell
    command is visible to every other process on the machine and can end up in a log through `set -x`.
    """
    doc = _doc(path)
    offenders = []
    for job_name, step in _steps(doc):
        run = step.get("run") or ""
        for line in run.splitlines():
            if "secrets." in line and "${{" in line:
                offenders.append(f"{job_name}/{step.get('name', '<unnamed>')}: {line.strip()[:90]}")
    assert not offenders, (
        f"{os.path.basename(path)}: a secret is interpolated into a shell command line; pass it through "
        f"`env:` instead: {offenders}")


def test_C_the_secrets_are_never_echoed_or_written_to_disk():
    """The value must not reach a log or a file -- only the fact of its presence may."""
    for path in (SYNC_YML, PREFLIGHT_YML):
        src = open(path).read()
        for name in (TOKEN_ENV, KEY_ENV):
            for pattern in (f'echo "${{{name}}}"', f"echo ${name}", f"echo \"${name}\"",
                            f"> ${{{name}}}", f"${{{name}}} >"):
                assert pattern not in src, f"{os.path.basename(path)} leaks {name} via {pattern!r}"
        # A presence check compares against empty and prints a sentence, never the value.
        assert 'echo "AIRTABLE_TOKEN is present (value never printed)."' in src or \
               "is present (value never printed)" in src


# ---- D. the presence check is not evidence about later steps -----------------------------------------

def test_D_the_secret_check_step_is_not_treated_as_evidence_for_later_steps():
    """A `-z` check in its own step proves existence and passes nothing on.

    Pinning the SHAPE of the mistake: a workflow where the only step declaring the signing key is the one
    that checks it is exactly the broken workflow, whatever its later steps assume.
    """
    doc = _doc(SYNC_YML)
    declaring = [(job, s.get("name", "<unnamed>")) for job, s in _steps(doc) if KEY_ENV in _env_of(s)]
    assert len(declaring) >= 2, (
        f"{KEY_ENV} is declared on only {declaring}; a presence check alone does not put the secret into "
        "the importer's process")

    checkers = [s for _job, s in _steps(doc)
                if KEY_ENV in _env_of(s) and f'-z "${{{KEY_ENV}}}"' in (s.get("run") or "")]
    users = [s for _job, s in _steps(doc)
             if KEY_ENV in _env_of(s) and "sync_airtable.py" in (s.get("run") or "")]
    assert checkers, "the configuration check step is gone; it is what makes a missing secret legible"
    assert users, "no step both declares the signing key AND runs the importer"
    assert checkers[0] is not users[0], "the check and the run are different steps, by construction"


def test_D_the_importer_reads_the_key_from_its_own_environment_not_from_a_workflow_claim():
    """The only thing that puts a key into `sync` is `os.environ` in this process."""
    src = open(os.path.join(ROOT, "scripts", "handicap", "sync_airtable.py")).read()
    assert "APPROVAL.signing_key()" in src, "the importer must resolve the key itself"
    key_src = open(os.path.join(ROOT, "nfl_edge", "handicap", "approval.py")).read()
    assert "os.environ" in key_src


# ---- E. the two workflows gate on the key DIFFERENTLY, on purpose ------------------------------------
#
# The importer's per-row disposition -- defer the real recommendation, still import the passes -- only ever
# happens if the importer RUNS. A whole-job precheck that exits before it would make that logic unreachable
# and turn "some work done, one thing to fix" into a hard failure. So:
#
#   preflight.yml               HARD. The worker can issue NOTHING without a key; answering requests it
#                               cannot sign would only produce rows that look approved and can never be
#                               archived.
#   sync-handicap-airtable.yml  WARN. A PASS/WATCHLIST row needs no authenticated approval and must still
#                               reach the ledger. The script decides per row.
#
# These run the check steps' actual shell bodies, so the assertion is about what the runner would do.


def _check_step(doc, name):
    """The step whose shell body tests the named secret for emptiness."""
    hits = [s for _job, s in _steps(doc) if f'-z "${{{name}}}"' in (s.get("run") or "")]
    assert len(hits) == 1, f"expected exactly one step checking {name}, found {len(hits)}"
    return hits[0]


def _run_check(step, **env):
    """Execute the check step's body exactly as the runner would: bash -eo pipefail, env-scoped secrets."""
    return subprocess.run(["bash", "-eo", "pipefail", "-c", step["run"]],
                          env={**os.environ, **env}, capture_output=True, text=True)


def test_E_the_preflight_worker_hard_fails_without_a_signing_key():
    """No key, no signature, no approval worth issuing. Fail before pretending to answer anything."""
    step = _check_step(_doc(PREFLIGHT_YML), KEY_ENV)
    r = _run_check(step, **{KEY_ENV: ""})
    assert r.returncode != 0, (
        "preflight.yml must stop when the signing key is missing; a worker that cannot sign can only "
        f"produce rows that look approved and can never be archived. Output: {r.stdout}")
    assert "::error::" in r.stdout


def test_E_the_importer_precheck_only_warns_without_a_signing_key():
    """THE FIX. Exiting here would stop the importer before it could import the passes.

    The reviewed inconsistency: the script's per-row deferral was correct and unreachable in production,
    because a preliminary step exited 1 and the job never got to it.
    """
    step = _check_step(_doc(SYNC_YML), KEY_ENV)
    r = _run_check(step, **{KEY_ENV: ""})
    assert r.returncode == 0, (
        "sync-handicap-airtable.yml must NOT exit when the signing key is missing: a PASS/WATCHLIST row "
        f"needs no approval and must still be archived. Output: {r.stdout}{r.stderr}")
    assert "::warning::" in r.stdout, "a missing key must still be legible in the run summary"
    assert "::error::" not in r.stdout
    assert "DEFERRED" in r.stdout and "READY_FOR_SYNC" in r.stdout,         "the warning must say what actually happens to the rows"


def test_E_the_airtable_token_stays_a_hard_prerequisite_in_both():
    """Nothing can be read at all without it, so there is no partial work to protect."""
    for path in (SYNC_YML, PREFLIGHT_YML):
        step = _check_step(_doc(path), TOKEN_ENV)
        r = _run_check(step, **{TOKEN_ENV: ""})
        assert r.returncode != 0, f"{os.path.basename(path)} must stop without {TOKEN_ENV}: {r.stdout}"
        assert "::error::" in r.stdout


def test_E_both_check_steps_pass_when_the_secrets_are_present():
    """The warning path must not be a check that has quietly stopped checking."""
    for path in (SYNC_YML, PREFLIGHT_YML):
        doc = _doc(path)
        for name in (TOKEN_ENV, KEY_ENV):
            r = _run_check(_check_step(doc, name), **{name: "x" * 64})
            assert r.returncode == 0, f"{os.path.basename(path)}/{name}: {r.stdout}{r.stderr}"
            assert "::error::" not in r.stdout and "::warning::" not in r.stdout
            assert "x" * 64 not in r.stdout, "the value itself must never be printed"


def test_E_a_pass_row_survives_the_production_sequence_with_no_key(ledger):
    """End to end through the STEPS, not just the script: precheck, then importer, both without a key.

    This is the test the reviewed inconsistency would have failed: the precheck exited 1, so the importer
    never ran and the pass never landed.
    """
    from tests.test_airtable_bridge import a_pass, row as plain_row      # noqa: PLC0415

    precheck = _run_check(_check_step(_doc(SYNC_YML), KEY_ENV), **{KEY_ENV: ""})
    assert precheck.returncode == 0, "the job would have stopped here"

    fake = FakeAirtable([{"records": [plain_row([a_pass("rec_pass_prod", test_only=False)],
                                                rid="recPRODPASS00001")]}])
    code, pushes, _c = run_sync(fake, ledger, gate_context=gate_ctx(), signing_key=None)
    assert code == 0
    assert fake.status_updates == {"recPRODPASS00001": AB.STATUS_SYNCED}
    assert [r["recommendation_id"] for r in store.read_kind(ledger, "recommendations")] == \
        ["rec_pass_prod"]
    assert len(pushes) == 1


def test_E_a_real_row_survives_the_production_sequence_with_no_key(ledger):
    """Same sequence, real recommendation: deferred, never ERROR, configuration exit."""
    precheck = _run_check(_check_step(_doc(SYNC_YML), KEY_ENV), **{KEY_ENV: ""})
    assert precheck.returncode == 0

    row_obj = _approved_row_for(rid="recPRODREAL00001")
    fake = FakeAirtable([{"records": [row_obj]}])
    code, pushes, _c = run_sync(fake, ledger, gate_context=gate_ctx(), signing_key=None)
    assert code == 2
    assert fake.status_updates == {}, "left READY_FOR_SYNC"
    assert store.read_kind(ledger, "recommendations") == []
    assert pushes == []


# ---- the behaviour the wiring protects ----------------------------------------------------------------
#
# A misconfigured runner must not be able to destroy a good recommendation. These run the real importer
# against a real signed row, with and without the key.

def _approved_row_for(rid="recWIRING0000001"):
    return approved_row([_real(rec)], rid=rid)


def test_a_missing_key_leaves_a_real_approved_row_ready_for_sync(ledger):
    fake = FakeAirtable([{"records": [_approved_row_for()]}])
    code, pushes, _c = run_sync(fake, ledger, gate_context=gate_ctx(), signing_key=None)

    assert code == 2, "configuration exit, not a row failure"
    assert fake.status_updates == {}, \
        f"the row's status was changed to {fake.status_updates}; it must stay READY_FOR_SYNC"
    assert AB.STATUS_ERROR not in fake.status_updates.values()
    assert store.read_kind(ledger, "recommendations") == [], "nothing written"
    assert store.read_kind(ledger, "decision_gates") == [], "no gate record either"
    assert pushes == [], "nothing to commit, so nothing to push"


def test_the_same_row_imports_unchanged_once_the_key_is_wired(ledger):
    """The retry is the whole point: the operator fixes the YAML, not the recommendation."""
    row_obj = _approved_row_for()

    first = FakeAirtable([{"records": [row_obj]}])
    assert run_sync(first, ledger, gate_context=gate_ctx(), signing_key=None)[0] == 2

    # The SAME row object, byte for byte. Nothing about it was rewritten to make the retry work.
    second = FakeAirtable([{"records": [row_obj]}])
    code, pushes, _c = run_sync(second, ledger, gate_context=gate_ctx(), signing_key=SIGNING_KEY)

    assert code == 0, "with the key present the row imports"
    assert second.status_updates == {row_obj["id"]: AB.STATUS_SYNCED}
    written = store.read_kind(ledger, "recommendations")
    assert [r["recommendation_id"] for r in written] == ["rec_bridge0000000000001"]
    assert len(pushes) == 1


def test_a_deferred_row_does_not_block_a_pass_in_the_same_run(ledger):
    """PASS/WATCHLIST rows need no authenticated approval, so a missing key must not hold them up."""
    from tests.test_airtable_bridge import a_pass, row as plain_row      # noqa: PLC0415

    fake = FakeAirtable([{"records": [
        _approved_row_for(rid="recWIRINGREAL001"),
        plain_row([a_pass("rec_pass_wiring", test_only=False)], rid="recWIRINGPASS001"),
    ]}])
    code, _pushes, _c = run_sync(fake, ledger, gate_context=gate_ctx(), signing_key=None)

    assert code == 2
    assert fake.status_updates == {"recWIRINGPASS001": AB.STATUS_SYNCED}, \
        "the pass lands; the real recommendation waits for the configuration to be fixed"
    assert [r["recommendation_id"] for r in store.read_kind(ledger, "recommendations")] == \
        ["rec_pass_wiring"]


def test_a_configuration_failure_is_not_a_bridge_error():
    """The class separation IS the fix; anything that re-parents it re-creates the defect."""
    assert not issubclass(AB.ConfigurationError, AB.BridgeError), \
        "a ConfigurationError caught as a BridgeError would mark the row ERROR again"
    assert not issubclass(AB.ConfigurationError, AB.TransientError), \
        "keep it distinct from the wire so the exit code stays actionable"
    src = open(os.path.join(ROOT, "scripts", "handicap", "sync_airtable.py")).read()
    assert src.index("except AB.ConfigurationError") < src.index("except AB.BridgeError"), \
        "the configuration handler must come first, or BridgeError would shadow nothing but still confuse"


def test_a_genuinely_bad_row_is_still_condemned(ledger):
    """The retryable path must not become a way for real data problems to be retried forever."""
    bad = _approved_row_for(rid="recWIRINGBAD0001")
    body = json.loads(bad["fields"][AB.F_PREFLIGHT_RESULT])
    body["approval_signature"] = "0" * 64
    bad["fields"][AB.F_PREFLIGHT_RESULT] = json.dumps(body)

    fake = FakeAirtable([{"records": [bad]}])
    code, _pushes, _c = run_sync(fake, ledger, gate_context=gate_ctx(), signing_key=SIGNING_KEY)
    assert code == 1
    assert fake.status_updates == {"recWIRINGBAD0001": AB.STATUS_ERROR}
    assert store.read_kind(ledger, "recommendations") == []


def test_the_exit_codes_are_documented_where_an_operator_will_read_them():
    doc = sync_airtable.__doc__
    assert "2 a configuration problem" in doc.replace("\n", " ").replace("  ", " ") or \
        "configuration problem on THIS RUNNER" in doc
    assert "READY_FOR_SYNC" in doc
