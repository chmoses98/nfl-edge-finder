#!/usr/bin/env python3
"""Publish captured files onto the orphan `market-data` branch.

Why an orphan branch: market observations grow by tens of MB per week and
must never bloat `main` (the MLB repo's data/ reached ~1 GB on main). Code
branches gitignore data/kalshi/; this script moves files into a worktree of
`market-data` and pushes with fetch+rebase retries.

Conflict policy: publishers write NEW files per run (discovery/<run_id>/,
capture/<date>/<run_id>.jsonl) so rebases never touch the same path; if a
conflict still appears we abort and fail loudly (exit 3) rather than
committing conflict markers (MLB lesson: `git rebase --autostash` exits 0
with markers on disk).

Usage: publish_market_data.py --src data/kalshi --message "..." [--branch market-data]
"""
from __future__ import annotations
import argparse, os, shutil, subprocess, sys, time

# A push the remote will refuse however many times it is retried. A racing publisher is a retry; a file the
# server will not accept, or a hook that declines, is not -- retrying it eight times only delays the report.
FATAL_PUSH_ERRORS = (
    ("GH001", "a file in the commit exceeds GitHub's 100 MB file size limit"),
    ("exceeds GitHub's file size limit", "a file in the commit exceeds GitHub's 100 MB file size limit"),
    ("pre-receive hook declined", "the remote's pre-receive hook declined the push"),
    ("protected branch", "the branch is protected against this push"),
    ("permission denied", "the token cannot write to this branch"),
)


def rejected_for_good(stderr: str) -> str | None:
    """The reason a push can never succeed on retry, or None if it might be a race.

    Only the remote's ERRORS are read, never its warnings. GitHub prints `remote: warning: GH001: Large files
    detected` for any file over its RECOMMENDED 50 MB -- a push that goes on to succeed. Run 35936325143 (#59)
    pushed a derived commit carrying such a file, lost a ref-lock race to a concurrent capture publisher
    (`cannot lock ref 'refs/heads/market-data': is at 79d6ba98 but expected 49e436bc`), and the bare `GH001`
    needle in the warning line turned an ordinary race -- the one thing the retry loop exists for -- into
    "REFUSED BY THE REMOTE, and no retry can change it". The hard 100 MB refusal arrives as `remote: error:`,
    and that is still fatal.
    """
    lines = [ln for ln in (stderr or "").lower().splitlines() if "warning:" not in ln]
    low = "\n".join(lines)
    for needle, why in FATAL_PUSH_ERRORS:
        if needle.lower() in low:
            return why
    return None


def unpushed(wt: str, branch: str) -> int:
    """Commits this worktree holds that origin does not. Never 0 after a rejected push."""
    r = subprocess.run(["git", "rev-list", "--count", f"origin/{branch}..HEAD"], cwd=wt, text=True, capture_output=True)
    try:
        return int((r.stdout or "").strip() or 0)
    except ValueError:
        return 1                      # cannot tell: assume there is something to push rather than claim success


def sh(cmd, cwd=None, check=True, capture=False):
    print("+", " ".join(cmd), flush=True)
    r = subprocess.run(cmd, cwd=cwd, check=False, text=True, capture_output=capture)
    if check and r.returncode != 0:
        if capture:
            print(r.stdout, r.stderr)
        raise SystemExit(f"command failed ({r.returncode}): {' '.join(cmd)}")
    return r

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="directory (relative to repo) whose contents to publish at the same relative path")
    ap.add_argument("--message", required=True)
    ap.add_argument("--branch", default="market-data")
    ap.add_argument("--repo", default=os.getcwd())
    ap.add_argument("--attempts", type=int, default=8)
    a = ap.parse_args()
    repo = os.path.abspath(a.repo)
    src = os.path.join(repo, a.src)
    if not os.path.isdir(src) or not any(os.scandir(src)):
        print("nothing to publish (source empty)"); return 0
    wt = os.path.join(os.path.dirname(repo), "_market_data_wt")
    if os.path.exists(wt):
        shutil.rmtree(wt, ignore_errors=True)
        sh(["git", "worktree", "prune"], cwd=repo)
    exists = subprocess.run(["git", "ls-remote", "--exit-code", "--heads", "origin", a.branch], cwd=repo, capture_output=True).returncode == 0
    if exists:
        sh(["git", "fetch", "--depth=1", "origin", a.branch], cwd=repo)
        sh(["git", "worktree", "add", "-f", wt, f"origin/{a.branch}"], cwd=repo)
        sh(["git", "checkout", "-B", a.branch, f"origin/{a.branch}"], cwd=wt)
    else:
        sh(["git", "worktree", "add", "--detach", wt], cwd=repo)
        sh(["git", "checkout", "--orphan", a.branch], cwd=wt)
        sh(["git", "rm", "-rf", "-q", "."], cwd=wt, check=False)
        with open(os.path.join(wt, "README.md"), "w") as f:
            f.write("# market-data\n\nOrphan branch holding immutable Kalshi market observations for nfl-edge-finder.\nNever merge into main. See docs/MARKET_DATA_BRANCH.md on main.\n")
        sh(["git", "add", "README.md"], cwd=wt)
        sh(["git", "commit", "-q", "-m", "init market-data orphan branch"], cwd=wt)
    for attempt in range(1, a.attempts + 1):
        dest = os.path.join(wt, a.src)
        os.makedirs(dest, exist_ok=True)
        # copy (append-only: new files; existing files are overwritten with identical content)
        for root, dirs, files in os.walk(src):
            rel = os.path.relpath(root, src)
            os.makedirs(os.path.join(dest, rel), exist_ok=True)
            for fn in files:
                if fn.endswith(".part"):
                    continue
                shutil.copy2(os.path.join(root, fn), os.path.join(dest, rel, fn))
        sh(["git", "add", "-A", "--", a.src], cwd=wt)
        staged = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=wt).returncode != 0
        if staged:
            sh(["git", "commit", "-q", "-m", a.message], cwd=wt)
        elif not unpushed(wt, a.branch):
            print("no changes to publish"); return 0
        # else: a commit from an earlier attempt is still unpushed. Falling through to push it again is the
        # whole point of the retry; returning 0 here reported a REJECTED push as a successful publish. That is
        # how 413,128 settlement rows -- the entire 2026 week-2 Sunday slate -- were staged, committed,
        # refused by the remote for an oversized file, and then announced as published by a green job.
        r = subprocess.run(["git", "push", "-u", "origin", a.branch], cwd=wt, text=True, capture_output=True)
        if r.returncode == 0:
            print("published", a.branch); return 0
        print("push failed:", r.stderr[-500:])
        fatal = rejected_for_good(r.stderr)
        if fatal:
            print(f"REFUSED BY THE REMOTE, and no retry can change it: {fatal}")
            return 4
        if not exists:
            time.sleep(3 * attempt); continue
        sh(["git", "fetch", "origin", a.branch], cwd=wt)
        rb = subprocess.run(["git", "rebase", f"origin/{a.branch}"], cwd=wt, text=True, capture_output=True)
        unmerged = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"], cwd=wt, text=True, capture_output=True).stdout.strip()
        if rb.returncode != 0 or unmerged:
            print("rebase conflict on:", unmerged)
            sh(["git", "rebase", "--abort"], cwd=wt, check=False)
            sh(["git", "reset", "-q", "--hard", f"origin/{a.branch}"], cwd=wt)
            # retry from the fresh tip: re-copy and commit again
            continue
        time.sleep(2 * attempt)
        # rebased cleanly; try pushing again in next loop iteration (files already in tree)
        r = subprocess.run(["git", "push", "-u", "origin", a.branch], cwd=wt, text=True, capture_output=True)
        if r.returncode == 0:
            print("published after rebase", a.branch); return 0
        print("push failed:", r.stderr[-500:])
        fatal = rejected_for_good(r.stderr)
        if fatal:
            print(f"REFUSED BY THE REMOTE, and no retry can change it: {fatal}")
            return 4
    print("FAILED to publish after retries"); return 3

if __name__ == "__main__":
    sys.exit(main())
