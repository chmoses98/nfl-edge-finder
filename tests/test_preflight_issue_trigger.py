"""The free trigger: a GitHub issue may START the preflight worker, and may do nothing else.

Airtable's free tier has no "Run script" Automation action, so the paid path that used to call
`workflow_dispatch` is unavailable, and ChatGPT's GitHub integration can open an issue but cannot dispatch a
workflow. So an issue became the trigger signal. That is a security question before it is a convenience one:

**this repository is public, and anyone can open an issue.** Without a guard, a stranger could make the real
Airtable worker run -- spending the free-tier request allowance the archival importer depends on, and
starting a job that holds `AIRTABLE_TOKEN` and `PREFLIGHT_SIGNING_KEY`. The job-level `if` is the boundary,
and a skipped job never starts, so an outsider's issue costs nothing and touches nothing.

The second rule is that the issue is a SIGNAL, not a message. Nothing in it is read as input: not the body,
not the labels, not the title beyond the prefix. Airtable stays the transport and the only place a verdict
lives, so a trigger can influence *that* the worker runs and never *what it decides*.

These tests evaluate the workflow's ACTUAL `if:` expression rather than grepping for its text, so a rewrite
that changes the meaning fails even when it keeps the words.
"""
import os
import re
import sys

import pytest
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nfl_edge.handicap import preflight_trigger as T   # noqa: E402

PREFLIGHT = os.path.join(ROOT, ".github", "workflows", "preflight.yml")
OWNER = "chmoses98"
PREFIX = "[PREFLIGHT NFL]"
BARE = "PREFLIGHT NFL"


def doc():
    with open(PREFLIGHT) as f:
        return yaml.safe_load(f)


def job():
    return doc()["jobs"]["preflight"]


def triggers():
    d = doc()
    return d.get(True, d.get("on"))


# ----------------------------------------------------------------------------------------------------
# A deliberately tiny evaluator for the subset of the GitHub expression language this guard uses. It
# raises on anything it does not recognise, so a guard rewritten with an unsupported operator fails these
# tests loudly instead of being waved through.
# ----------------------------------------------------------------------------------------------------

_TOKEN = re.compile(r"""\s*(\(|\)|\|\||&&|==|!=|,|'[^']*'|[0-9]+|[A-Za-z_][A-Za-z0-9_.]*)""")


def _lex(src):
    pos, out = 0, []
    while pos < len(src):
        m = _TOKEN.match(src, pos)
        if not m:
            if src[pos].isspace():
                pos += 1
                continue
            raise ValueError(f"unsupported token at {src[pos:pos + 20]!r}")
        out.append(m.group(1))
        pos = m.end()
    return out


class _Eval:
    """`||` and `&&` over `==`/`!=` comparisons, `startsWith(a, b)` and context lookups."""

    def __init__(self, tokens, ctx):
        self.t, self.i, self.ctx = tokens, 0, ctx

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def take(self, expect=None):
        tok = self.t[self.i]
        if expect and tok != expect:
            raise ValueError(f"expected {expect!r}, got {tok!r}")
        self.i += 1
        return tok

    def parse(self):
        v = self.or_()
        if self.i != len(self.t):
            raise ValueError(f"trailing tokens: {self.t[self.i:]}")
        return bool(v)

    def or_(self):
        v = self.and_()
        while self.peek() == "||":
            self.take()
            v = bool(self.and_()) or bool(v)
        return v

    def and_(self):
        v = self.cmp_()
        while self.peek() == "&&":
            self.take()
            v = bool(self.cmp_()) and bool(v)
        return v

    def cmp_(self):
        # Returns the RAW value when there is no comparison operator. Coercing to bool here would turn a
        # function argument into `True` before startsWith ever saw it, and every title would match.
        left = self.atom()
        if self.peek() in ("==", "!="):
            op = self.take()
            right = self.atom()
            # GitHub compares strings case-insensitively.
            a = left.lower() if isinstance(left, str) else left
            b = right.lower() if isinstance(right, str) else right
            return (a == b) if op == "==" else (a != b)
        return left

    def atom(self):
        tok = self.peek()
        if tok == "(":
            self.take()
            v = self.or_()
            self.take(")")
            return v
        tok = self.take()
        if tok.startswith("'"):
            return tok[1:-1]
        # The comment doorbell compares an issue NUMBER and tests an object for absence, so the evaluator
        # grew integer literals and `null`. Both are real GitHub expression syntax; neither widens what the
        # evaluator will accept elsewhere, and unknown tokens still raise.
        if tok.isdigit():
            return int(tok)
        if tok == "null":
            return None
        if tok == "startsWith":
            self.take("(")
            a = self.or_()
            self.take(",")
            b = self.or_()
            self.take(")")
            # GitHub's string functions are case-insensitive, like its comparisons.
            return str(a).lower().startswith(str(b).lower())
        if tok == "always":
            self.take("(")
            self.take(")")
            return True
        return self.lookup(tok)

    def lookup(self, dotted):
        cur = self.ctx
        for part in dotted.split("."):
            if not isinstance(cur, dict) or part not in cur:
                return None
            cur = cur[part]
        return cur


def eligible(*, event_name, author=None, title=None, body=None, action=None,
             comment_author=None, comment_body=None, issue_number=None, is_pull_request=False,
             gate_result=None, gate_active=None):
    """Evaluate the WORKFLOW'S OWN expression, then assert the Python copy of the rule agrees.

    Two copies of a security guard that can disagree is worse than one, so every case in this file is run
    through both. `nfl_edge/handicap/preflight_trigger.py` exists because the 2026-09-13 failure was a
    routing bug living only in a YAML string, where nothing could test it.
    """
    ctx = {
        "github": {
            "event_name": event_name,
            "repository_owner": OWNER,
            "event": {"action": action,
                      "issue": {"user": {"login": author}, "title": title, "body": body,
                                "number": issue_number,
                                # GitHub puts a `pull_request` object on the issue only when the comment is
                                # on a PR; its ABSENCE is how an issue comment is told from a PR comment.
                                **({"pull_request": {"url": "..."}} if is_pull_request else {})},
                      "comment": {"user": {"login": comment_author}, "body": comment_body}},
        },
        # A scheduled run reaches the worker only through the gate JOB, so the guard reads its result and
        # its output. For every other trigger the gate is skipped and neither is set, which is why the
        # schedule branch is false by default here.
        "needs": {"schedule_gate": {"result": gate_result,
                                    "outputs": {"active": gate_active}}},
    }
    from_yaml = bool(_Eval(_lex(job()["if"]), ctx).parse())
    from_python = T.may_start_worker(event_name=event_name, action=action, author=author,
                                     repository_owner=OWNER, title=title,
                                     comment_author=comment_author, comment_body=comment_body,
                                     issue_number=issue_number, is_pull_request=is_pull_request,
                                     gate_result=gate_result, gate_active=gate_active)
    assert from_yaml == from_python, (
        f"the workflow guard and preflight_trigger.may_start_worker disagree on "
        f"event={event_name!r} author={author!r} title={title!r}: {from_yaml} vs {from_python}")
    return from_yaml


def test_the_evaluator_rejects_syntax_it_does_not_understand():
    """A guard rewritten with an operator this evaluator cannot read must fail, not silently pass."""
    with pytest.raises(ValueError):
        _Eval(_lex("github.event_name"), {}).parse() if False else _lex("a > b")


# ------------------------------------------------------------------ A-E: who may start the worker

def test_A_the_owner_with_the_exact_prefix_starts_the_worker():
    assert eligible(event_name="issues", author=OWNER, title=f"{PREFIX} 2026-09-09 batch") is True


def test_B_an_outsider_with_a_perfect_looking_trigger_is_refused():
    """The repository is public. This is the case that matters."""
    for outsider in ("attacker", "chmoses", "chmoses981", "notchmoses98", "github-actions[bot]"):
        assert eligible(event_name="issues", author=outsider, title=f"{PREFIX} run it") is False, outsider


def test_A2_the_owner_with_the_BARE_prefix_starts_the_worker():
    """The 2026-09-13 incident, pinned.

    The owner opened `PREFLIGHT NFL`. The guard wanted `[PREFLIGHT NFL]`, the job was silently SKIPPED, and
    the manual run that followed answered a 17:00:00Z kickoff at 17:01:30Z. Both forms now route.
    """
    assert eligible(event_name="issues", author=OWNER, title=BARE) is True
    assert eligible(event_name="issues", author=OWNER, title="PREFLIGHT NFL 2026-09-13 BAL/IND") is True


def test_C_the_owner_with_the_wrong_title_is_refused():
    for title in ("Bug: packet renders oddly",
                  "please run [PREFLIGHT NFL]",          # prefix, but not at the start
                  "please run PREFLIGHT NFL",
                  "[PREFLIGHT] NFL",
                  "[PREFLIGHT MLB] wrong sport",
                  "PREFLIGHT MLB",
                  "NFL PREFLIGHT",                       # the words, in the wrong order
                  ""):
        assert eligible(event_name="issues", author=OWNER, title=title) is False, title


def test_relaxing_the_title_gives_an_outsider_nothing():
    """Routing was relaxed; AUTHORISATION was not. This is the test that says so."""
    for outsider in ("attacker", "chmoses", "chmoses981", "notchmoses98", "github-actions[bot]"):
        for title in (PREFIX + " x", BARE, BARE.lower(), "[preflight nfl] x"):
            assert eligible(event_name="issues", author=outsider, title=title) is False, (outsider, title)


def test_the_prefix_match_is_case_insensitive_and_that_is_deliberate():
    """GitHub's `startsWith` is case-insensitive, so `[preflight nfl]` from the OWNER also triggers.

    Recorded rather than fought: the title is routing, the author check is the security control, and a
    case variant typed by the owner is still the owner. Enforcing exact case would have to happen in a
    step, which means a mis-cased owner issue would show as a RED run instead of no run -- worse, not
    better. An outsider gains nothing from it either way (see test B)."""
    assert eligible(event_name="issues", author=OWNER, title="[preflight nfl] batch") is True
    assert eligible(event_name="issues", author="attacker", title="[preflight nfl] batch") is False


def test_C2_a_missing_author_or_title_is_refused():
    assert eligible(event_name="issues", author=None, title=f"{PREFIX} x") is False
    assert eligible(event_name="issues", author=OWNER, title=None) is False


def test_D_workflow_dispatch_is_unaffected():
    assert eligible(event_name="workflow_dispatch") is True


def test_E_repository_dispatch_is_unaffected():
    assert eligible(event_name="repository_dispatch") is True


def test_an_unlisted_event_cannot_start_the_worker():
    """The guard is an allowlist: an `on:` entry added later without thinking is inert, not open."""
    for ev in ("push", "pull_request", "fork", "watch", "workflow_run"):
        assert eligible(event_name=ev, author=OWNER, title=f"{PREFIX} x") is False, ev


# ---- the scheduled path, which exists only behind the window gate ------------------------------------

def test_H1_a_schedule_reaches_the_worker_only_when_the_gate_succeeded_and_said_active():
    assert eligible(event_name="schedule", gate_result="success", gate_active="true") is True


def test_H2_an_inactive_gate_never_starts_the_worker():
    """The quota boundary. Most wakes land here, and they must cost zero Airtable requests."""
    assert eligible(event_name="schedule", gate_result="success", gate_active="false") is False
    assert eligible(event_name="schedule", gate_result="success", gate_active=None) is False


def test_H3_a_failed_gate_never_starts_the_worker():
    """FAIL CLOSED. An unreadable schedule is an unknown, and unknown is not permission.

    This is the single most important assertion about the new structure: `always()` on the worker job means
    the guard is EVALUATED even when the gate failed, so the gate's result has to be checked explicitly.
    Drop that check and a broken calendar would start spending Airtable requests.
    """
    for result in ("failure", "cancelled", "skipped", None):
        assert eligible(event_name="schedule", gate_result=result, gate_active="true") is False, result


def test_H4_a_bare_schedule_with_no_gate_at_all_is_refused():
    assert eligible(event_name="schedule") is False


# ---- the comment doorbell: the normal operating trigger ----------------------------------------------

DOORBELL = T.DOORBELL_PR_NUMBER
COMMENT = "PREFLIGHT NFL"


def ring(**kw):
    """A well-formed doorbell, with one field overridable per test."""
    kw = {"event_name": "issue_comment", "action": "created", "comment_author": OWNER,
          "comment_body": COMMENT, "issue_number": DOORBELL, "is_pull_request": True, **kw}
    return eligible(**kw)


def test_G1_the_owners_doorbell_comment_starts_the_worker():
    assert ring() is True
    assert ring(comment_body="PREFLIGHT NFL — week 2 slate") is True


def test_G2_an_outsiders_identical_comment_is_refused():
    """The security control, unchanged in kind from the issue path: the AUTHOR is what is checked.

    This repository is public and anybody can comment on a merged pull request, so the identical text from
    a stranger must do nothing at all -- no run, no Airtable request, no log line.
    """
    assert ring(comment_author="a-stranger") is False
    assert ring(comment_author=None) is False


def test_G3_a_comment_on_any_other_object_is_refused():
    """The doorbell is ONE pinned pull request, so the new trigger's blast radius is one conversation."""
    assert ring(issue_number=DOORBELL + 1) is False
    assert ring(issue_number=1) is False
    assert ring(issue_number=None) is False


def test_G4_an_ordinary_owner_comment_on_the_doorbell_is_refused():
    """Routing. The owner must be able to talk on that PR without spending a preflight run."""
    assert ring(comment_body="looks good to me") is False
    assert ring(comment_body="") is False
    assert ring(comment_body=None) is False
    assert ring(comment_body="please run PREFLIGHT NFL") is False, "the prefix must LEAD the comment"


def test_G5_an_issue_comment_that_is_not_on_a_pull_request_is_refused():
    """`issue_comment` fires for issues too; only the designated PR is the doorbell."""
    assert ring(is_pull_request=False) is False


def test_G6_only_a_new_comment_rings():
    """An edit is not a doorbell: re-reading edits would let one comment ring over and over."""
    assert ring(action="edited") is False
    assert ring(action="deleted") is False
    assert set(T.COMMENT_ACTIONS) == {"created"}


def test_G7_the_workflow_listens_for_created_comments_only():
    assert triggers()["issue_comment"] == {"types": ["created"]}


def test_G8_the_doorbell_number_in_the_yaml_matches_the_python_copy():
    """Two places name the PR; a silent drift between them would open or close the door unnoticed."""
    assert f"github.event.issue.number == {DOORBELL}" in " ".join(job()["if"].split())


def test_G9_the_comment_trigger_never_closes_or_comments_on_the_doorbell():
    """The cleanup step belongs to the ISSUE path. A doorbell PR that closed itself would be absurd."""
    cleanup = next(s for s in job()["steps"] if "Close the trigger issue" in (s.get("name") or ""))
    assert cleanup["if"] == "always() && github.event_name == 'issues'"


def test_G10_nothing_from_the_comment_reaches_the_worker():
    """The comment is a SIGNAL, not a message -- the same rule the issue path already obeys.

    The worker's command line is fixed. There is no argument by which a ticker, price, stake, probability or
    thesis written in a comment could reach a decision, which is why the comment is allowed to be generic.
    """
    worker = next(s for s in job()["steps"] if "preflight_airtable.py" in (s.get("run") or ""))
    for leak in ("github.event.comment", "github.event.issue.body", "github.event.issue.title"):
        assert leak not in worker["run"], f"the worker invocation reads {leak}"
    assert set(worker["env"]) == {"AIRTABLE_TOKEN", "PREFLIGHT_SIGNING_KEY", "PREFLIGHT_TRIGGER"}


def test_the_workflow_listens_for_opened_and_edited_issues():
    """`edited` exists because a silently-skipped trigger is invisible to the person who rang the doorbell.

    On 2026-09-13 the owner's malformed title produced a skipped job and no feedback; correcting the title
    did nothing, and the repair was a manual dispatch that answered after kickoff. Editing a title must be
    able to start the worker.

    It widens nothing. `github.event.issue.user.login` is the issue's AUTHOR, not whoever edited it, so an
    outsider renaming an old owner issue -- which GitHub does not permit them to do anyway -- would still be
    measured against the author check, and an outsider's own issue is refused whatever it is renamed to.
    """
    assert triggers()["issues"] == {"types": ["opened", "edited"]}
    assert set(T.ISSUE_ACTIONS) == {"opened", "edited"}


def test_D2_a_corrected_title_on_an_edit_starts_the_worker():
    assert eligible(event_name="issues", action="edited", author=OWNER, title=PREFIX + " fixed") is True
    assert eligible(event_name="issues", action="edited", author=OWNER, title=BARE) is True
    assert eligible(event_name="issues", action="edited", author=OWNER, title="still wrong") is False


def test_an_edit_by_anyone_does_not_change_who_the_author_is():
    """The only identity the guard reads is the issue's author, on `opened` and on `edited` alike."""
    assert eligible(event_name="issues", action="edited", author="attacker", title=PREFIX) is False
    src = open(PREFLIGHT).read()
    assert "github.event.sender" not in src, "the editor's identity must not become an input"


def test_an_issue_action_the_workflow_does_not_listen_for_is_refused_by_the_helper():
    for action in ("reopened", "closed", "labeled", "assigned", "transferred"):
        assert T.may_start_worker(event_name="issues", action=action, author=OWNER,
                                  repository_owner=OWNER, title=PREFIX) is False, action


def test_the_dispatch_triggers_are_still_declared():
    on = triggers()
    assert "workflow_dispatch" in on
    assert on["repository_dispatch"] == {"types": ["preflight"]}
    assert "dry_run" in (on["workflow_dispatch"] or {})["inputs"]


# ------------------------------------------------------------------ F-G: permissions

def test_F_contents_write_exists_only_to_publish_append_only_public_evidence():
    """`contents: write` is a real widening and it buys a real property, so it is pinned to its reason.

    A pre-trade approval must be replayable after the runner is gone, which means the market evidence it was
    computed from has to be committed somewhere. `evidence_store.GitBranchEvidenceStore` refuses every
    branch but `preflight-evidence`, so this grant cannot reach main, market-data or handicap-data.
    """
    from nfl_edge.handicap import evidence_store as ES   # noqa: PLC0415
    assert doc()["permissions"]["contents"] == "write"
    assert ES.ALLOWED_BRANCHES == ("preflight-evidence",)
    with pytest.raises(ES.EvidenceStoreError):
        ES.GitBranchEvidenceStore(ROOT, branch="main")
    for branch in ("market-data", "handicap-data", "main"):
        with pytest.raises(ES.EvidenceStoreError):
            ES.GitBranchEvidenceStore(ROOT, branch=branch)


def test_G_only_issues_write_is_added():
    perms = doc()["permissions"]
    assert perms == {"contents": "write", "issues": "write"}, (
        f"preflight.yml permissions are {perms}; nothing beyond contents and issues is granted")
    for forbidden in ("pull-requests", "actions", "packages", "id-token", "deployments"):
        assert forbidden not in perms


def test_the_job_does_not_widen_permissions_for_itself():
    assert "permissions" not in job(), "a job-level permissions block would bypass the workflow-level grant"


# ------------------------------------------------------------------ H: cleanup

def _cleanup():
    return next(s for s in job()["steps"] if "gh issue close" in (s.get("run") or ""))


def test_H_the_trigger_issue_is_closed_even_when_the_worker_fails():
    cond = _cleanup()["if"]
    assert "always()" in cond, "cleanup is not unconditional, so a failed worker leaves its trigger open"
    assert "github.event_name == 'issues'" in cond, (
        "cleanup must not fire for workflow_dispatch or repository_dispatch, which have no issue")


def test_the_cleanup_only_acts_on_an_issues_event():
    ctx_ok = {"github": {"event_name": "issues"}}
    ctx_no = {"github": {"event_name": "workflow_dispatch"}}
    assert _Eval(_lex(_cleanup()["if"]), ctx_ok).parse() is True
    assert _Eval(_lex(_cleanup()["if"]), ctx_no).parse() is False


def test_the_cleanup_comment_reveals_nothing():
    """The Airtable row is the only place the verdict lives. A comment that leaked a candidate, a price or
    a verdict would put betting data in a public issue."""
    run = _cleanup()["run"]
    banned = ["approved", "blocked", "verdict:", "stake", "probability", "ticker", "thesis", "price",
              "payload", "kxnfl", "preflight_result", "airtable_token", "signing"]
    low = run.lower()
    for word in banned:
        if word == "approved":
            # "not an approval" is the disclaimer, and is the opposite of a leak.
            assert "not an approval" in low
            continue
        assert word not in low, f"the cleanup comment mentions {word!r}"


def test_a_failed_close_does_not_fail_the_run():
    """The issue carries no data, so a stale open trigger is harmless -- but a cleanup that failed the job
    would turn a successful preflight into a red run and invite a needless re-request."""
    assert "|| echo" in _cleanup()["run"]


# ------------------------------------------------------------------ I: the issue is never input

def test_I_the_issue_body_is_never_read():
    src = open(PREFLIGHT).read()
    assert "event.issue.body" not in src, "the issue body is consumed somewhere; it is a trigger, not input"
    for field in ("event.issue.labels", "event.issue.user.id", "event.issue.state"):
        assert field not in src


def test_the_issue_never_reaches_the_worker():
    step = next(s for s in job()["steps"] if "preflight_airtable.py" in (s.get("run") or ""))
    # `github.event_name` is fine -- it is which trigger fired. `github.event.` is the payload, and no part
    # of an issue may reach the worker's command line or environment.
    assert "github.event." not in step["run"], "issue payload is passed into the worker invocation"
    for key in (step.get("env") or {}):
        assert "ISSUE" not in key.upper()


def test_no_run_id_is_parsed_out_of_the_issue():
    """Airtable stays the source of truth: the worker answers every pending row, so batching survives and
    two triggers arriving together cost one run."""
    src = open(PREFLIGHT).read()
    assert "--run-id" not in src
    assert not re.search(r"Run ID", src, re.I)


def test_the_issue_number_is_used_only_for_cleanup():
    steps_using_issue = [s.get("name") for s in job()["steps"]
                         if "issue.number" in yaml.safe_dump(s)]
    assert steps_using_issue == ["Close the trigger issue"]


# ------------------------------------------------------------------ J-K: nothing else moved

def test_J_the_worker_invocation_reads_the_ledger_and_the_fees_and_not_the_capture_stream():
    """FIX 4, pinned: the live decision path must not ask for a full market-data checkout again.

    On 2026-09-13 that checkout fetched for ~57s and wrote ~17,491 files for another ~43s, to answer a
    question about ONE ticker. The worker now fetches that ticker from the venue directly.
    """
    step = next(s for s in job()["steps"] if "preflight_airtable.py" in (s.get("run") or ""))
    run = step["run"]
    assert "python3 scripts/handicap/preflight_airtable.py" in run
    assert "--handicap-root ../ledger" in run
    assert "--fee-observations ../fees" in run
    assert "--market-data" not in run, "the live path no longer reads the capture stream"
    assert step["working-directory"] == "code"
    # dry-run stays a workflow_dispatch-only affordance; an issue can never ask for --no-write, and it
    # could not weaken anything if it did.
    assert "github.event_name == 'workflow_dispatch' && inputs.dry_run" in run


def test_K_the_secret_wiring_is_unchanged():
    step = next(s for s in job()["steps"] if "preflight_airtable.py" in (s.get("run") or ""))
    # PREFLIGHT_TRIGGER is which event fired -- a string GitHub already puts in the public log. The two
    # secrets are still the only secrets.
    assert set(step["env"]) == {"AIRTABLE_TOKEN", "PREFLIGHT_SIGNING_KEY", "PREFLIGHT_TRIGGER"}
    src = open(PREFLIGHT).read()
    assert "AIRTABLE_TOKEN is not configured" in src
    assert "PREFLIGHT_SIGNING_KEY is not configured" in src


def test_the_fail_closed_secret_checks_still_run_before_the_worker():
    names = [s.get("name", "") for s in job()["steps"]]
    assert names.index("Check the Airtable secret is configured") < names.index(
        "Answer pending preflight requests")
    assert names.index("Check the approval signing secret is configured") < names.index(
        "Answer pending preflight requests")


def test_no_secret_is_exposed_to_the_cleanup_step():
    env = _cleanup().get("env") or {}
    assert "AIRTABLE_TOKEN" not in env and "PREFLIGHT_SIGNING_KEY" not in env
    assert env["GH_TOKEN"] == "${{ github.token }}", "cleanup must use the job token, not a PAT"


def test_two_triggers_arriving_together_stay_serialised():
    c = doc()["concurrency"]
    assert c["group"] == "nfl-preflight"
    assert c["cancel-in-progress"] is False


def test_the_workflow_still_never_writes_a_ledger_or_market_data_branch():
    src = open(PREFLIGHT).read()
    assert "publish_market_data" not in src, "preflight does not publish captures"
    assert "git push" not in src, "the workflow never pushes; the evidence store does, to its own branch"
    for branch in ("handicap-data", "market-data"):
        assert f"origin {branch}" not in src and f"origin/{branch}" not in src
