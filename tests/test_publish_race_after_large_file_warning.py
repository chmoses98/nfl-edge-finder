"""A large-file WARNING is not a refusal, and a race that follows one is still retried.

Run 35936325143 (shadow-v2-settle #59, 2026-09-24) failed at "Publish the research export, scorecard v3 and
weekly report" with this, the whole of the publisher's reading of it:

    push failed: commended maximum file size of 50.00 MB
    remote: warning: GH001: Large files detected. You may want to try Git Large File Storage - ...
     ! [remote rejected]   market-data -> market-data (cannot lock ref 'refs/heads/market-data':
       is at 79d6ba98... but expected 49e436bc...)
    REFUSED BY THE REMOTE, and no retry can change it: a file in the commit exceeds GitHub's 100 MB file size limit

Nothing exceeded 100 MB. GitHub WARNS at its recommended 50 MB and accepts the push; what refused it was the
ref lock, because a Kalshi capture publisher moved market-data between this job's fetch and its push. That is
a race, the case the fetch-rebase-retry loop was written for, and the bare `GH001` needle -- present in the
warning as well as in the real 100 MB error -- sent it down the no-retry path instead.
"""
from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tests"))

from test_publish_evidence_before_derived import (git, load_publisher, origin_and_repo,  # noqa: E402,F401
                                                  run_publisher)

RUN_59_STDERR = (
    "remote: warning: See https://gh.io/lfs for more information.\n"
    "remote: warning: File data/shadow/v2/research/2026_wk02.research.parquet is 50.61 MB; this is larger than "
    "GitHub's recommended maximum file size of 50.00 MB\n"
    "remote: warning: GH001: Large files detected. You may want to try Git Large File Storage - "
    "https://git-lfs.github.com.\n"
    "To https://github.com/chmoses98/nfl-edge-finder\n"
    " ! [remote rejected]   market-data -> market-data (cannot lock ref 'refs/heads/market-data': is at "
    "79d6ba9858fc879df31248c68bb922bee48c50eb but expected 49e436bc74b24dfa4a0a8174fbe0592cdf439c84)\n"
    "error: failed to push some refs to 'https://github.com/chmoses98/nfl-edge-finder'\n"
)


def test_the_run_59_rejection_is_a_race_not_a_refusal():
    mod = load_publisher()
    assert mod.rejected_for_good(RUN_59_STDERR) is None


def test_the_hard_limit_is_still_fatal_when_it_arrives_beside_a_warning():
    mod = load_publisher()
    hard = ("remote: warning: GH001: Large files detected.\n"
            "remote: error: File x.gz is 160.92 MB; this exceeds GitHub's file size limit of 100.00 MB\n"
            "remote: error: GH001: Large files detected. You may want to try Git Large File Storage\n"
            " ! [remote rejected] market-data -> market-data (pre-receive hook declined)\n")
    assert mod.rejected_for_good(hard)


def test_a_ref_lock_race_after_a_large_file_warning_is_retried_and_publishes(origin_and_repo):
    """End to end against a real bare remote: the first push prints GitHub's 50 MB warning and loses the ref
    lock to a concurrent writer (the hook moves market-data mid-push, which is what a racing capture publisher
    does); the publisher must fetch, rebase and publish on the next attempt, keeping the other writer's file."""
    origin, repo = origin_and_repo
    # the "other publisher's" commit, parked on the remote under a side ref for the hook to advance to
    other = repo.parent / "other"
    subprocess.run(["git", "clone", "-q", "-b", "market-data", str(origin), str(other)], check=True)
    for k, v in (("user.name", "t"), ("user.email", "t@e"), ("commit.gpgsign", "false")):
        git("config", k, v, cwd=other)
    (other / "capture.jsonl").write_text("kalshi capture\n")
    git("add", "-A", cwd=other)
    git("commit", "-q", "-m", "kalshi capture (conductor pass 19)", cwd=other)
    git("push", "-q", "origin", "HEAD:refs/heads/racer", cwd=other)

    marker = origin / "raced-once"
    hook = origin / "hooks" / "pre-receive"
    hook.parent.mkdir(exist_ok=True)
    hook.write_text(
        "#!/bin/sh\n"
        "echo \"warning: File data/shadow/v2/research/x.parquet is 50.61 MB; this is larger than GitHub's"
        " recommended maximum file size of 50.00 MB\" >&2\n"
        "echo 'warning: GH001: Large files detected. You may want to try Git Large File Storage' >&2\n"
        f"if [ ! -e '{marker}' ]; then\n"
        f"  touch '{marker}'\n"
        # step outside the push quarantine to move the ref, exactly as a second pusher would
        "  env -u GIT_QUARANTINE_PATH -u GIT_OBJECT_DIRECTORY -u GIT_ALTERNATE_OBJECT_DIRECTORIES \\\n"
        "      git update-ref refs/heads/market-data refs/heads/racer\n"
        "fi\n"
        "exit 0\n")
    hook.chmod(0o755)

    r = run_publisher(repo, extra=("--attempts", "3"))
    out = r.stdout + r.stderr
    assert "no retry can change it" not in out, out
    assert r.returncode == 0, out
    assert marker.exists(), "the race was never staged, so the test proved nothing"
    listed = subprocess.run(["git", "ls-tree", "-r", "--name-only", "market-data"], cwd=origin,
                            text=True, capture_output=True).stdout
    assert "data/shadow/v2/settlements.txt" in listed
    assert "capture.jsonl" in listed, "the racing publisher's commit was overwritten"
