"""Durable, append-only storage for pre-trade evidence. An approval that outlives its runner.

WHY A STORE AND NOT A VARIABLE
------------------------------
The live preflight path fetches a market and an order book, decides, and answers Airtable. If that is all it
does, the evidence a real-money approval rested on exists only in the memory of a runner that is deleted
minutes later. Months afterwards the ledger would hold "this was approved" and nothing that could be
independently re-checked -- and "trust the signed Airtable row" is an authentication claim, not a replay.

So the evidence is written down FIRST, read BACK, and only then may an approval be issued. The ordering is
the control: a store that accepted the write and lost it, a push that failed, a path that already existed
with different bytes -- each of those raises, the row is answered PREFLIGHT_ERROR, and an errored request is
not an approval.

APPEND-ONLY, AND ENFORCED
-------------------------
Every path carries the retrieval instant and the ticker, so a second request never lands on a first one's
file. If it somehow does, the store compares bytes: identical content is an idempotent replay and is fine;
DIFFERENT content at an existing path is a rewrite of history and raises. Nothing here deletes and nothing
here overwrites.

TWO BACKENDS, ONE CONTRACT
--------------------------
    GitBranchEvidenceStore    production. A worktree of the orphan `preflight-evidence` branch, committed and
                              pushed, returning the commit SHA the approval cites.
    DirectoryEvidenceStore    a plain directory. Used by tests and by an operator replaying locally; its
                              reference is a content digest over the batch rather than a commit, and it says
                              so, because calling a local directory a commit would be a lie in an audit
                              trail.

Both expose `stage` / `publish` / `read`, and `read` is what the worker uses to rebuild its gate indexes --
so the gates always run against the bytes that are actually stored, never against the ones in memory.

WHAT MAY BE STORED HERE
-----------------------
Public market data only: a market object and an order book from unauthenticated GET endpoints. No account
data, no credentials, no positions, no fills, no stakes, no theses. The branch is public and permanent, and
that is only acceptable because of what is on it.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time

# The one branch the production store may write. An allowlist rather than a parameter with a default,
# because "publish the evidence to `main`" must be a change somebody has to argue for, not a typo.
EVIDENCE_BRANCH = "preflight-evidence"
ALLOWED_BRANCHES = (EVIDENCE_BRANCH,)

# Every stored path must live under here. A ticker or a record id that tried to climb out of the tree is
# already neutralised by `live_evidence.evidence_relpath`, and this is the second, independent check.
EVIDENCE_PREFIX = "data/preflight_evidence/"

STORAGE_GIT = "git"
STORAGE_DIRECTORY = "directory"

README = """# preflight-evidence

Append-only, public market evidence for NFL PRE-TRADE PREFLIGHT.

Each file is one candidate's live Kalshi market object and depth-10 order book, with the timestamps at which
each was retrieved, hashed so an approval can cite it and a later replay can prove it has not changed.

Public read-only market data only. No account data, no credentials, no positions, no fills, no stakes, no
theses. Never merge into main; see docs/PREFLIGHT.md on main.
"""


class EvidenceStoreError(RuntimeError):
    """Evidence could not be durably stored. Blocks approval; it is never a verdict on the bet."""


def _check_relpath(relpath: str) -> str:
    rel = str(relpath or "").replace("\\", "/").lstrip("/")
    if not rel.startswith(EVIDENCE_PREFIX):
        raise EvidenceStoreError(
            f"refusing to store {relpath!r}: preflight evidence lives under {EVIDENCE_PREFIX} and nowhere "
            "else")
    if ".." in rel.split("/"):
        raise EvidenceStoreError(f"refusing to store {relpath!r}: the path escapes the evidence tree")
    return rel


class _BaseStore:
    """Staging, byte-comparison and the append-only refusal, shared by both backends."""

    storage = "unknown"

    def __init__(self, root: str):
        self.root = os.path.abspath(root)
        self._staged: list[str] = []

    def _abs(self, relpath: str) -> str:
        return os.path.join(self.root, _check_relpath(relpath))

    def stage(self, relpath: str, payload: str) -> None:
        """Write one document into the working tree. Refuses to change anything already there."""
        rel = _check_relpath(relpath)
        path = self._abs(rel)
        data = payload.encode("utf-8")
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    existing = f.read()
            except OSError as e:
                raise EvidenceStoreError(f"existing evidence at {rel} is unreadable: {e}") from None
            if existing != data:
                raise EvidenceStoreError(
                    f"APPEND-ONLY VIOLATION: {rel} already holds different bytes. Preflight evidence is "
                    "immutable once written; an approval that rewrote its own evidence would be "
                    "unauditable.")
            self._staged.append(rel)
            return
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = None
        try:
            fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".part")
            with os.fdopen(fd, "wb") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, path)
            tmp = None
        except OSError as e:
            raise EvidenceStoreError(f"could not write preflight evidence to {rel}: {e}") from None
        finally:
            if tmp and os.path.exists(tmp):
                os.unlink(tmp)
        self._staged.append(rel)

    def read(self, relpath: str) -> str:
        """Read a stored document back from disk. The worker gates against THIS, not against memory."""
        path = self._abs(relpath)
        try:
            with open(path, "rb") as f:
                return f.read().decode("utf-8")
        except OSError as e:
            raise EvidenceStoreError(
                f"preflight evidence at {relpath} could not be read back after storing it: {e}. An approval "
                "is not issued on evidence we cannot prove is there.") from None

    def publish(self, message: str) -> str:
        raise NotImplementedError


class DirectoryEvidenceStore(_BaseStore):
    """A plain directory. Durable for as long as the directory is, and honest about being a directory.

    Its reference is a digest over the batch's paths and hashes rather than a commit SHA, because there is no
    commit. An audit trail that called a local folder a commit would be worse than one that admits what it
    is.
    """

    storage = STORAGE_DIRECTORY

    def publish(self, message: str) -> str:  # noqa: ARG002 - the message has nowhere to go here
        import hashlib                                                          # noqa: PLC0415
        h = hashlib.sha256()
        for rel in sorted(set(self._staged)):
            h.update(rel.encode("utf-8"))
            h.update(b"\0")
            h.update(hashlib.sha256(self.read(rel).encode("utf-8")).hexdigest().encode("utf-8"))
            h.update(b"\n")
        return h.hexdigest()


class GitBranchEvidenceStore(_BaseStore):
    """A worktree of the orphan `preflight-evidence` branch: commit, push, return the commit SHA.

    The branch is created on first use, orphaned, holding nothing but a README and the evidence. It is never
    merged, never rebased onto anything, and nothing on it is ever rewritten -- every publisher writes NEW
    paths, so a concurrent push is resolved by fetching and replaying the new files on top rather than by
    resolving a conflict.

    A push that cannot be made to land raises. That is the point: the caller must not be able to interpret a
    failed publish as anything other than "do not approve".
    """

    storage = STORAGE_GIT

    def __init__(self, repo_root: str, *, branch: str = EVIDENCE_BRANCH, worktree: str | None = None,
                 remote: str = "origin", attempts: int = 5, push: bool = True,
                 allow_any_branch: bool = False):
        if not allow_any_branch and branch not in ALLOWED_BRANCHES:
            raise EvidenceStoreError(
                f"refusing to publish preflight evidence to {branch!r}. Evidence goes to "
                f"{EVIDENCE_BRANCH!r} and nowhere else; this store is not a general-purpose publisher.")
        self.repo_root = os.path.abspath(repo_root)
        self.branch = branch
        self.remote = remote
        self.attempts = max(1, int(attempts))
        self.push = push
        self._wt = os.path.abspath(
            worktree or os.path.join(os.path.dirname(self.repo_root), "_preflight_evidence_wt"))
        self._prepared = False
        super().__init__(self._wt)

    # ---- git plumbing ------------------------------------------------------------------------
    def _git(self, args, cwd=None, check=True):
        r = subprocess.run(["git", *args], cwd=cwd or self.repo_root, text=True, capture_output=True)
        if check and r.returncode != 0:
            raise EvidenceStoreError(
                f"git {' '.join(args)} failed ({r.returncode}): {(r.stderr or r.stdout)[-400:]}")
        return r

    def _remote_has_branch(self) -> bool:
        r = self._git(["ls-remote", "--exit-code", "--heads", self.remote, self.branch], check=False)
        return r.returncode == 0

    def prepare(self) -> "GitBranchEvidenceStore":
        """Make the worktree exist and sit on the branch tip. Cheap: the branch holds kilobytes."""
        if self._prepared:
            return self
        if os.path.exists(self._wt):
            shutil.rmtree(self._wt, ignore_errors=True)
            self._git(["worktree", "prune"], check=False)
        if self._remote_has_branch():
            self._git(["fetch", "--depth=1", self.remote, self.branch])
            self._git(["worktree", "add", "-f", self._wt, f"{self.remote}/{self.branch}"])
            self._git(["checkout", "-B", self.branch, f"{self.remote}/{self.branch}"], cwd=self._wt)
        else:
            self._git(["worktree", "add", "--detach", self._wt])
            self._git(["checkout", "--orphan", self.branch], cwd=self._wt)
            self._git(["rm", "-rf", "-q", "."], cwd=self._wt, check=False)
            with open(os.path.join(self._wt, "README.md"), "w") as f:
                f.write(README)
            self._git(["add", "README.md"], cwd=self._wt)
            self._git(["commit", "-q", "-m", f"init {self.branch} orphan branch"], cwd=self._wt)
        self._prepared = True
        return self

    def stage(self, relpath: str, payload: str) -> None:
        self.prepare()
        super().stage(relpath, payload)

    def publish(self, message: str) -> str:
        """Commit the staged evidence and push it. Returns the commit SHA the approval will cite."""
        self.prepare()
        if not self._staged:
            raise EvidenceStoreError("nothing staged: there is no evidence to publish and none to approve on")
        last = ""
        for attempt in range(1, self.attempts + 1):
            self._git(["add", "-A", "--", EVIDENCE_PREFIX.rstrip("/")], cwd=self._wt)
            if self._git(["diff", "--cached", "--quiet"], cwd=self._wt, check=False).returncode != 0:
                self._git(["commit", "-q", "-m", message], cwd=self._wt)
            sha = self._git(["rev-parse", "HEAD"], cwd=self._wt).stdout.strip()
            if not self.push:
                return sha
            r = self._git(["push", "-u", self.remote, self.branch], cwd=self._wt, check=False)
            if r.returncode == 0:
                return sha
            last = (r.stderr or r.stdout)[-400:]
            # Somebody else published between our fetch and our push. Every publisher writes NEW paths, so
            # replaying ours on top of theirs cannot conflict; if it somehow does, we abort rather than
            # resolve anything on an append-only branch.
            self._git(["fetch", self.remote, self.branch], cwd=self._wt, check=False)
            rb = self._git(["rebase", f"{self.remote}/{self.branch}"], cwd=self._wt, check=False)
            unmerged = self._git(["diff", "--name-only", "--diff-filter=U"], cwd=self._wt,
                                 check=False).stdout.strip()
            if rb.returncode != 0 or unmerged:
                self._git(["rebase", "--abort"], cwd=self._wt, check=False)
                raise EvidenceStoreError(
                    f"publishing preflight evidence conflicted on {unmerged or 'unknown paths'}. The "
                    "evidence branch is append-only and nothing here resolves a conflict on it.")
            time.sleep(min(0.5 * attempt, 3.0))
        raise EvidenceStoreError(
            f"could not publish preflight evidence to {self.branch} after {self.attempts} attempts: {last}. "
            "No approval is issued on evidence that is not durably present.")


def store_batch(store, documents, *, message: str) -> dict:
    """Store a batch of evidence documents, publish, READ BACK, and return what the approval may cite.

    The read-back is not belt and braces. It is the difference between "we asked a store to keep this" and
    "this is kept": the returned entries carry the hash of the bytes that came back off disk, and the caller
    rebuilds its gate indexes from those same bytes. An approval therefore cannot rest on a document that was
    only ever in memory.

    `documents` is an iterable of `(relpath, canonical_json_text, sha256)` -- the hash is supplied rather
    than recomputed here so that a mismatch between what the collector hashed and what the store returns is
    visible as a mismatch rather than quietly re-derived into agreement.
    """
    import hashlib                                                              # noqa: PLC0415

    staged = []
    for relpath, text, sha in documents:
        store.stage(relpath, text)
        staged.append((relpath, text, sha))
    if not staged:
        raise EvidenceStoreError("no preflight evidence to store; there is nothing to approve against")

    commit = store.publish(message)

    entries = []
    for relpath, _text, sha in staged:
        back = store.read(relpath)
        actual = hashlib.sha256(back.encode("utf-8")).hexdigest()
        if actual != sha:
            raise EvidenceStoreError(
                f"stored preflight evidence at {relpath} reads back as {actual} but was collected as {sha}; "
                "the evidence on disk is not the evidence that was fetched")
        entries.append({"path": relpath, "sha256": actual, "text": back})
    return {"storage": store.storage, "commit": commit, "entries": entries}


def write_run_note(path: str, body: dict) -> None:
    """Small helper for operators: dump a JSON note beside a local evidence tree. Never used in gating."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as f:
        json.dump(body, f, indent=1, sort_keys=True, default=str)
