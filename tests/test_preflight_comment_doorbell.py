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

def test_no_schedule_is_required_for_normal_operation():
    """An idle poll would spend the Free-workspace Airtable allowance to discover nothing.

    Free is 1,000 API calls/workspace/month. A five-minute poll is ~6,500/month and a fifteen-minute poll
    ~2,200 -- both over. The doorbell costs zero when idle, so usage tracks requests rather than clock time.
    """
    assert "schedule" not in triggers(), "routine polling must not be the normal trigger"
    src = open(PREFLIGHT).read()
    assert "cron" not in src


def test_no_scheduler_lag_code_survives():
    """It existed only to observe polling, and its minute arithmetic crashed at :00 and :01."""
    src = open(PREFLIGHT).read()
    for dead in ("scheduler_delay", "scheduled_slot", "github.event.schedule"):
        assert dead not in src, f"dead polling telemetry remains: {dead}"


def test_the_three_fallbacks_survive():
    t = triggers()
    assert "workflow_dispatch" in t
    assert t["repository_dispatch"] == {"types": ["preflight"]}
    assert t["issues"] == {"types": ["opened", "edited"]}


def test_concurrency_is_unchanged():
    assert doc()["concurrency"] == {"group": "nfl-preflight", "cancel-in-progress": False}


def test_the_allowlist_is_still_an_allowlist():
    expr = " ".join(doc()["jobs"]["preflight"]["if"].split())
    for ev in ("workflow_dispatch", "repository_dispatch", "issue_comment", "issues"):
        assert f"github.event_name == '{ev}'" in expr, ev
    assert "always()" not in expr and "success()" not in expr
    assert "github.event_name != " not in expr, "an allowlist never reasons by exclusion"
