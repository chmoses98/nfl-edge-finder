"""Who may wake the real-money preflight worker, as a function rather than as YAML string logic.

WHY THIS IS A MODULE
--------------------
On 2026-09-13 the owner opened an issue titled

    PREFLIGHT NFL

The workflow's guard required the title to begin with `[PREFLIGHT NFL]`, so the `issues` event created
Actions run 34770096817 and the job was SKIPPED. A skipped job is silent by design -- that is what makes the
guard a safe boundary against strangers -- so the owner saw nothing, waited, and then dispatched preflight by
hand. The manual run started at 16:59:34Z for a 17:00:00Z kickoff and answered at 17:01:30Z, after kickoff.

The routing half of that guard was brittle and the security half was not. So the two are separated here:

    AUTHORISATION   the issue's AUTHOR is the repository owner. Non-negotiable, and the only security
                    control. This repository is public; anybody can open an issue.
    ROUTING         the title says this issue is a preflight doorbell rather than a bug report. A convenience
                    that exists so an ordinary issue from the owner does not spend a preflight run.

Relaxing routing costs nothing an attacker can use: an outsider with a perfect title is still refused, and an
owner with a sloppy title now gets the run they meant to ask for instead of silence. Tightening routing, by
contrast, costs a kickoff.

WHY A PYTHON FUNCTION FOR A YAML EXPRESSION
-------------------------------------------
The guard's real home is `jobs.preflight.if` in `.github/workflows/preflight.yml`, because a job that never
starts is the only boundary that cannot leak a secret. This module is the same rule, written once, so the
behaviour can be pinned by tests -- and `tests/test_preflight_issue_trigger.py` evaluates the ACTUAL workflow
expression and asserts it agrees with this function on every case. Neither copy can drift without failing.

GITHUB'S STRING SEMANTICS
-------------------------
`startsWith()` and `==` in the GitHub expression language are CASE-INSENSITIVE, so `[preflight nfl]` from the
owner already triggered before this change. That is recorded rather than fought: the author check is the
security control, a case variant typed by the owner is still the owner, and enforcing exact case would have
to happen inside a step -- which turns a mis-cased owner issue into a RED run instead of no run. This
function matches those semantics exactly, including for the login comparison, because a guard whose Python
copy is stricter than its YAML copy is a guard nobody can reason about.
"""
from __future__ import annotations

# Both accepted title forms. The bracketed one is the documented convention and stays first; the bare one is
# what a human actually types when they are in a hurry, which is the only time this doorbell is ever rung.
#
# These are PREFIXES, matched case-insensitively, exactly as `startsWith` matches them in the workflow. A
# title is routing and nothing else: no part of it -- and no part of the issue body, labels or number --
# reaches the worker, which answers every pending Airtable row regardless of what the trigger said.
ACCEPTED_TITLE_PREFIXES = ("[PREFLIGHT NFL]", "PREFLIGHT NFL")

# Triggers that may start the worker. An ALLOWLIST: an `on:` entry added later without thinking about
# authorisation is inert rather than open.
DISPATCH_EVENTS = ("workflow_dispatch", "repository_dispatch")

# ---- the comment doorbell ----------------------------------------------------------------------------
# THE NORMAL OPERATING TRIGGER. ChatGPT can write Airtable and can comment on GitHub; it cannot dispatch a
# workflow or run a script. So after it writes the candidate rows it rings a doorbell by commenting on one
# designated pull request, and the worker wakes immediately.
#
# WHY NOT A SCHEDULE. A five-minute poll costs one Airtable request per wake-up whether or not anything is
# waiting -- roughly 6,500 a month against a Free workspace allowance of 1,000. Even a fifteen-minute poll
# exceeds it. An event-driven doorbell costs ZERO when idle: Airtable usage scales with actual requests
# rather than with elapsed clock time, which is the only shape that fits inside the allowance at all.
#
# ONE FIXED OBJECT, BY NUMBER. The doorbell is a specific merged pull request, named here and asserted
# against the workflow. Pinning it means a comment anywhere else in the repository -- another PR, an issue,
# a discussion -- cannot start the worker even from the owner, so the blast radius of the new trigger is one
# conversation rather than every conversation.
DOORBELL_PR_NUMBER = 18

# Only a NEW comment. An edited comment is deliberately not a doorbell: re-reading an edit would let one
# comment ring repeatedly, and there is no reason to need that when posting another costs nothing.
COMMENT_ACTIONS = ("created",)

# The routing prefix for a comment, matched case-insensitively exactly as `startsWith` matches it. Only the
# bare form: a comment is a fresh affordance with no legacy convention to honour, so it gets one spelling
# rather than two. The bracketed form remains accepted on the ISSUE path, where it is the documented one.
COMMENT_TRIGGER_PREFIX = "PREFLIGHT NFL"

# `opened` is the doorbell. `edited` exists because of the incident: when the title is wrong the job is
# silently skipped, and the natural human repair is to fix the title -- which, without this, does nothing and
# costs another round trip while the quote ages. Editing cannot widen the boundary: `issue.user.login` is the
# issue's AUTHOR, not whoever edited it, and only the owner or a collaborator can edit a title at all.
ISSUE_ACTIONS = ("opened", "edited")


def title_is_trigger(title) -> bool:
    """Does this issue title route to preflight? Case-insensitive prefix match, like `startsWith`."""
    if not isinstance(title, str):
        return False
    low = title.lower()
    return any(low.startswith(p.lower()) for p in ACCEPTED_TITLE_PREFIXES)


def _same_login(a, b) -> bool:
    """GitHub's `==` is case-insensitive on strings, and this mirrors it rather than being stricter.

    A missing login is never equal to anything: `None` on both sides must not read as a match, or an event
    payload with no author would authorise itself.
    """
    if not isinstance(a, str) or not isinstance(b, str) or not a or not b:
        return False
    return a.lower() == b.lower()


def comment_is_trigger(body) -> bool:
    """Does this comment body route to preflight? Case-insensitive prefix, like `startsWith`.

    The prefix is all that is ever read. Nothing after it reaches the worker, and nothing in it could: the
    worker takes its candidates from Airtable and has no parameter by which a comment could name a ticker,
    a price, a stake or a probability even if one were written there.
    """
    if not isinstance(body, str):
        return False
    return body.lower().startswith(COMMENT_TRIGGER_PREFIX.lower())


def may_start_worker(*, event_name, action=None, author=None, repository_owner=None, title=None,
                     comment_author=None, comment_body=None, issue_number=None,
                     is_pull_request=False) -> bool:
    """The whole guard: may this event start the Airtable preflight worker?

    `workflow_dispatch` and `repository_dispatch` are already authenticated by GitHub -- both require a token
    with write access to this repository -- so they need no further check here.

    An `issue_comment` needs FIVE things, and it is the normal operating trigger: the comment is new, it is
    on the one designated doorbell pull request, that object really is a pull request, its AUTHOR is the
    repository owner, and its body carries the routing prefix. The author check is the security control and
    the rest is routing, exactly as on the issue path. An outsider commenting the identical text is refused,
    and so is the owner commenting anywhere else or saying anything else.

    An `issues` event needs BOTH halves: the author is the repository owner (authorisation) and the title
    carries an accepted prefix (routing). Any other event is refused, including one whose `on:` entry someone
    adds later without revisiting this function.

    None of this authorises a DECISION. Every trigger here wakes the same worker, whose entire input is
    PREFLIGHT_REQUESTED rows that already exist in Airtable; `airtable_bridge` speaks only GET and PATCH and
    has no record-create path, so no trigger can bring a candidate into being.
    """
    if event_name in DISPATCH_EVENTS:
        return True
    if event_name == "issue_comment":
        if action is not None and action not in COMMENT_ACTIONS:
            return False
        if issue_number != DOORBELL_PR_NUMBER:
            return False
        if not is_pull_request:
            return False
        return _same_login(comment_author, repository_owner) and comment_is_trigger(comment_body)
    if event_name != "issues":
        return False
    # `action` is checked only when supplied. The workflow's `on:` block is what filters actions in
    # production, and duplicating that filter in the guard would let the two disagree about, say, `reopened`.
    if action is not None and action not in ISSUE_ACTIONS:
        return False
    return _same_login(author, repository_owner) and title_is_trigger(title)
