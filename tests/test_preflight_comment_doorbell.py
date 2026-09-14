"""The comment doorbell wakes the worker and can never create work for it.

`tests/test_preflight_issue_trigger.py` covers WHO may ring -- author, object, prefix, action -- by
evaluating the workflow's own guard. This file covers what ringing can and cannot CAUSE:

  * the comment cannot bring a candidate into being, because nothing in this repository can;
  * nothing written in the comment reaches a decision;
  * the worker a doorbell wakes is byte-for-byte the one Phase 4H accepted, with its batching, its
    cumulative exposure semantics and its concurrency group unchanged;
  * no schedule is required for normal operation, which is the whole point -- an idle poll would spend
    Airtable's Free-workspace allowance on finding nothing.
"""
import os
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts", "handicap"))

from nfl_edge.handicap import airtable_bridge as AB      # noqa: E402
from nfl_edge.handicap import preflight_trigger as T     # noqa: E402
import preflight_airtable as PA                          # noqa: E402

PREFLIGHT = os.path.join(ROOT, ".github", "workflows", "preflight.yml")


def doc():
    with open(PREFLIGHT) as f:
        return yaml.safe_load(f)


def triggers():
    d = doc()
    return d.get("on") if "on" in d else d.get(True)


class _Client:
    """Only `list_by_status`. A write is an outright failure, never a silent no-op."""

    def __init__(self, rows=(), boom=None):
        self.rows, self.boom, self.calls = list(rows), boom, []

    def list_by_status(self, status, sport=AB.SPORT_NFL):
        self.calls.append((status, sport))
        if self.boom:
            raise self.boom
        return [r for r in self.rows if r["fields"].get(AB.F_STATUS) == status]

    def set_status(self, *a, **k):        # pragma: no cover
        raise AssertionError("a write was attempted")

    def write_fields(self, *a, **k):      # pragma: no cover
        raise AssertionError("a write was attempted")


# ---- the doorbell cannot create work ----------------------------------------------------------------

def test_a_comment_cannot_create_an_airtable_row_because_nothing_can():
    """Not a policy -- an absence. There is no create path for any trigger to reach.

    This is the load-bearing claim of the whole design: the doorbell is safe to expose to a public
    conversation precisely because waking the worker and authorising a candidate are different powers, and
    the second one has no implementation.
    """
    src = open(os.path.join(ROOT, "nfl_edge", "handicap", "airtable_bridge.py")).read()
    assert '"POST"' not in src and "'POST'" not in src, "a record-create path appeared in the bridge"
    assert '"GET"' in src and '"PATCH"' in src, "the two verbs the bridge is supposed to have"

    # The worker never PUTS a row INTO the requested state either -- it only ever answers one already
    # there. Reading the constant is fine and necessary: it is the query filter, and it appears again in
    # the line that logs how many rows came back. What must never happen is the constant appearing in a
    # WRITE, so the check is stated that way round rather than as an allowlist of accepted read shapes.
    worker = open(os.path.join(ROOT, "scripts", "handicap", "preflight_airtable.py")).read()
    uses = [ln.strip() for ln in worker.splitlines()
            if "STATUS_PREFLIGHT_REQUESTED" in ln and not ln.strip().startswith("#")]
    assert uses, "the worker must still filter on the requested status"
    for line in uses:
        for write in ("set_status", "write_fields", f"{AB.F_STATUS}:"):
            assert write not in line, f"the requested status is being written: {line!r}"


def test_the_guard_reads_only_the_comments_prefix_and_never_its_content():
    """`comment_is_trigger` looks at a prefix. Everything after it is ignored by construction."""
    assert T.comment_is_trigger("PREFLIGHT NFL") is True
    assert T.comment_is_trigger("preflight nfl anything at all after this") is True
    assert T.comment_is_trigger("not a doorbell") is False
    for junk in (None, 17, [], {}):
        assert T.comment_is_trigger(junk) is False


def test_a_comment_carrying_candidate_data_changes_no_decision():
    """A comment MAY be generic; this proves it is also HARMLESS if someone pastes something into one.

    The guard consumes a prefix and the worker takes its candidates from Airtable, so a ticker or a price
    written in a comment is inert text on a public PR -- which is exactly why the documented trigger is
    generic and carries none.
    """
    noisy = "PREFLIGHT NFL ticker=KXNFLGAME-FAKE price=0.99 stake=500 p=0.88 thesis=nonsense"
    assert T.may_start_worker(event_name="issue_comment", action="created", comment_author="owner",
                              repository_owner="owner", comment_body=noisy,
                              issue_number=T.DOORBELL_PR_NUMBER, is_pull_request=True) is True
    # ...and the worker's inputs are unchanged by it: it still reads rows, and only rows.
    client = _Client([])
    assert PA.run(client, ledger_root=ROOT, signing_key=b"k") == 0
    assert client.calls == [(AB.STATUS_PREFLIGHT_REQUESTED, AB.SPORT_NFL)]


# ---- the worker behind the doorbell is the accepted one ----------------------------------------------

def test_zero_pending_rows_is_the_workers_own_no_work_path(capsys):
    """No probe, no special case -- the worker already returns cleanly when Airtable has nothing."""
    client = _Client([])
    assert PA.run(client, ledger_root=ROOT, signing_key=b"k") == 0
    assert "nothing to preflight" in capsys.readouterr().out


def test_an_airtable_read_failure_is_not_no_work():
    client = _Client(boom=AB.TransientError("airtable is down"))
    assert PA.run(client, ledger_root=ROOT, signing_key=b"k") == 3, \
        "an unreadable Airtable must not exit 0"


def test_terminal_rows_are_never_rediscovered():
    """The server-side status filter is what makes a finished row invisible to the next doorbell."""
    rows = [{"id": s, "createdTime": "2026-09-14T15:00:00.000Z",
             "fields": {AB.F_STATUS: s, AB.F_SPORT: AB.SPORT_NFL}}
            for s in (AB.STATUS_PREFLIGHT_APPROVED, AB.STATUS_PREFLIGHT_BLOCKED,
                      AB.STATUS_PREFLIGHT_ERROR, AB.STATUS_READY, AB.STATUS_SYNCED)]
    client = _Client(rows)
    assert PA.run(client, ledger_root=ROOT, signing_key=b"k") == 0
    assert client.calls == [(AB.STATUS_PREFLIGHT_REQUESTED, AB.SPORT_NFL)]


def test_one_doorbell_still_batches_every_pending_row():
    """Six candidates cost one run, priced against ONE cumulative view of outstanding exposure.

    Splitting them across runs would let each candidate see the portfolio as it was before the others,
    which is how a cumulative cap is bypassed without any single decision looking wrong.
    """
    src = open(os.path.join(ROOT, "scripts", "handicap", "preflight_airtable.py")).read()
    assert "for row in rows:" in src, "the worker still walks the whole batch in one pass"
    assert "list_by_status(AB.STATUS_PREFLIGHT_REQUESTED" in src


def test_the_doorbell_runs_the_exact_phase_4H_worker():
    steps = doc()["jobs"]["preflight"]["steps"]
    worker = [s for s in steps if "preflight_airtable.py" in (s.get("run") or "")]
    assert len(worker) == 1, "there is exactly one worker invocation, as Phase 4H accepted"
    run = worker[0]["run"]
    assert "--handicap-root ../ledger" in run
    assert "--fee-observations ../fees" in run
    assert "--market-data" not in run, "the live path does not read the capture stream"
    assert "--probe" not in run, "no polling fast path survives"


# ---- no polling ---------------------------------------------------------------------------------------

def test_a_scheduled_wake_reaches_airtable_only_through_the_window_gate():
    """Polling returned, but a WAKE is still not an Airtable CALL -- and that is what this pins.

    This test previously asserted no `schedule:` trigger existed at all, because the doorbell was meant to
    be the only trigger. ChatGPT's GitHub integration turned out not to be able to post the doorbell
    (403 Resource not accessible by integration), so scheduling came back -- but the quota argument that
    motivated the doorbell did not go away. The answer is the cheap gate: GitHub may wake every ten minutes
    and Airtable is touched only inside a schedule-derived window.
    """
    assert "schedule" in triggers()
    jobs = doc()["jobs"]
    assert "schedule_gate" in jobs, "a scheduled wake must pass a gate before the worker exists"
    # The scheduled path into the worker requires a SUCCESSFUL, ACTIVE gate. Both halves matter.
    expr = " ".join(jobs["preflight"]["if"].split())
    assert "needs.schedule_gate.result == 'success'" in expr
    assert "needs.schedule_gate.outputs.active == 'true'" in expr
    assert jobs["preflight"].get("needs") == ["schedule_gate"]


def test_the_gate_job_runs_for_scheduled_wakes_only():
    """A dispatch or a doorbell must not pay for a gate whose answer it does not consult.

    Found by mutation: removing the gate job's own `if` changed nothing any other test could see, because
    the worker's guard only reads the gate on the schedule branch. The cost is a wasted runner on every
    manual trigger, and the confusion is worse -- a gate that ran and said INACTIVE while the worker
    correctly ignored it looks, in the log, exactly like a bug.
    """
    assert doc()["jobs"]["schedule_gate"]["if"] == "github.event_name == 'schedule'"


def test_the_gate_job_holds_no_secret_so_an_inactive_wake_cannot_touch_airtable():
    """Structural, not procedural: the job that COULD reach Airtable is never created when INACTIVE."""
    gate = doc()["jobs"]["schedule_gate"]
    assert gate["permissions"] == {"contents": "read"}
    for step in gate["steps"]:
        assert not step.get("env"), f"the gate step {step.get('name')!r} declares an environment"
        assert "secrets." not in (step.get("run") or ""), "the gate references a secret"
    runs = " ".join(s.get("run") or "" for s in gate["steps"])
    for forbidden in ("preflight_airtable", "AIRTABLE", "PREFLIGHT_SIGNING_KEY"):
        assert forbidden not in runs, f"the gate job mentions {forbidden}"


def test_no_scheduler_lag_code_survives():
    """The old telemetry's minute arithmetic crashed at :00 and :01; it is not coming back."""
    src = open(PREFLIGHT).read()
    for dead in ("scheduler_delay", "scheduled_slot", "now.minute"):
        assert dead not in src, f"dead polling telemetry remains: {dead}"


def test_the_three_fallbacks_survive():
    t = triggers()
    assert "workflow_dispatch" in t
    assert t["repository_dispatch"] == {"types": ["preflight"]}
    assert t["issues"] == {"types": ["opened", "edited"]}


def test_concurrency_is_unchanged():
    assert doc()["concurrency"] == {"group": "nfl-preflight", "cancel-in-progress": False}


def test_the_allowlist_is_still_an_allowlist():
    """Every permitted event is named. `always()` is mechanics, not permission -- see below.

    This used to assert `always()` was absent. It is now required: the worker job `needs:` the gate job, and
    a `needs:` dependency on a SKIPPED job skips the dependent, which would break every non-scheduled
    trigger. `always()` restores the job's eligibility to be evaluated; the expression inside it is the same
    explicit allowlist, and the schedule branch additionally demands the gate SUCCEEDED and said active.
    So `always()` widens when the guard is CONSULTED, never what it permits -- and
    test_a_failed_gate_never_starts_the_worker proves the distinction holds.
    """
    expr = " ".join(doc()["jobs"]["preflight"]["if"].split())
    for ev in ("workflow_dispatch", "repository_dispatch", "schedule", "issue_comment", "issues"):
        assert f"github.event_name == '{ev}'" in expr, ev
    assert "success()" not in expr
    assert "github.event_name != " not in expr, "an allowlist never reasons by exclusion"
    # `always()` may appear ONLY as the outer guard on the whole allowlist, never inside a branch.
    assert expr.startswith("always() && ("), expr[:60]
    assert expr.count("always()") == 1
