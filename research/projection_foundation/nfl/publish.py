#!/usr/bin/env python3
"""Publish NFL projection-foundation outputs to the orphan branch `projection-data` (CI only).

Layout (uniform across SIFT sports):
  projections/nfl/latest.json                 sift.projections.v1
  projections/nfl/<YYYY-MM-DDTHHMMZ>.json     timestamped copy, written only when the payload changed (append-only)
  summary/nfl/latest.json                     sift.projection_foundation.sport_summary.v1

Idempotent: payloads are compared without their generation timestamps; nothing is committed when nothing changed.
The branch is created as an orphan on first run. Pushes retry with 2/4/8/16 s backoff. Never touches any other branch.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

BRANCH = "projection-data"
VOLATILE = {"generated_utc", "code_sha", "data_asof_utc"}


def sh(*a, cwd=None, check=True):
    return subprocess.run(list(a), cwd=cwd, check=check, text=True, capture_output=True)


def _strip(o):
    if isinstance(o, dict):
        return {k: _strip(v) for k, v in o.items() if k not in VOLATILE}
    if isinstance(o, list):
        return [_strip(v) for v in o]
    return o


def same(a: str, b: str) -> bool:
    if not os.path.exists(b):
        return False
    try:
        return _strip(json.load(open(a))) == _strip(json.load(open(b)))
    except Exception:
        return False


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--projections", required=True)
    ap.add_argument("--summary", required=True)
    ap.add_argument("--sport", default="nfl")
    ap.add_argument("--repo", default=".")
    a = ap.parse_args(argv)
    repo = os.path.abspath(a.repo)
    wt = tempfile.mkdtemp(prefix="projection-data-")
    exists = sh("git", "ls-remote", "--exit-code", "--heads", "origin", BRANCH, cwd=repo, check=False).returncode == 0
    if exists:
        sh("git", "fetch", "--depth=1", "origin", f"{BRANCH}:refs/remotes/origin/{BRANCH}", cwd=repo)
        sh("git", "worktree", "add", "-f", "-B", BRANCH, wt, f"origin/{BRANCH}", cwd=repo)
    else:
        sh("git", "worktree", "add", "--detach", wt, cwd=repo)
        sh("git", "checkout", "--orphan", BRANCH, cwd=wt)
        sh("git", "rm", "-rf", "--quiet", ".", cwd=wt, check=False)
        for f in os.listdir(wt):
            if f != ".git":
                p = os.path.join(wt, f)
                shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    sp = a.sport.lower()
    pdir, sdir = os.path.join(wt, "projections", sp), os.path.join(wt, "summary", sp)
    os.makedirs(pdir, exist_ok=True)
    os.makedirs(sdir, exist_ok=True)
    changed = []
    if not same(a.projections, os.path.join(pdir, "latest.json")):
        stamp = time.strftime("%Y-%m-%dT%H%MZ", time.gmtime())
        shutil.copy(a.projections, os.path.join(pdir, f"{stamp}.json"))
        shutil.copy(a.projections, os.path.join(pdir, "latest.json"))
        changed.append("projections")
    if not same(a.summary, os.path.join(sdir, "latest.json")):
        shutil.copy(a.summary, os.path.join(sdir, "latest.json"))
        changed.append("summary")
    if not changed:
        print("projection-data: nothing changed; no commit")
        return 0
    sh("git", "add", "-A", ".", cwd=wt)
    sh("git", "commit", "-m", f"{sp} projection foundation: {', '.join(changed)} {time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime())}", cwd=wt)
    for i, delay in enumerate((0, 2, 4, 8, 16)):
        time.sleep(delay)
        r = sh("git", "push", "origin", f"HEAD:refs/heads/{BRANCH}", cwd=wt, check=False)
        if r.returncode == 0:
            print(f"projection-data: pushed ({', '.join(changed)})")
            return 0
        print(f"push attempt {i + 1} failed: {r.stderr.strip()[:300]}", file=sys.stderr)
        # a concurrent writer may have advanced the branch: rebase onto it and retry
        sh("git", "fetch", "origin", BRANCH, cwd=wt, check=False)
        sh("git", "rebase", f"origin/{BRANCH}", cwd=wt, check=False)
    print("projection-data: push failed after retries", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
