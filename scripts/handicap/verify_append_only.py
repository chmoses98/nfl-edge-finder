#!/usr/bin/env python3
"""Verify that the handicap-data history is append-only. Fails loudly if a decision record was rewritten.

    python3 scripts/handicap/verify_append_only.py --handicap-root /path/to/handicap-wt
    python3 scripts/handicap/verify_append_only.py --handicap-root . --since 2026-09-01

The git history of `handicap-data` IS the scientific record. Its value rests entirely on a claim that cannot
be verified by reading the current tree: that no recommendation was ever edited after the fact. A ledger
whose contents can be silently improved after settlement proves nothing at all, and the tree looks identical
either way.

`schema.write_record` enforces immutability in the APPLICATION -- it refuses to overwrite a path. That is the
right first line and it is not sufficient on its own, because it only constrains code that goes through it. A
`git commit --amend`, a force-push, or somebody editing a JSON file by hand all bypass it completely.

Server-side branch protection is the proper second line, and it has to be configured on the GitHub account
(see docs/OPERATIONS.md for the exact ruleset). This script is the third: it reads the actual commit history
and checks the property directly, so a rewrite is DETECTED even where it was not PREVENTED.

WHAT IT CHECKS
--------------
  1. No commit MODIFIES (M) a file under an immutable kind. Records are created once and never touched.
  2. No commit DELETES (D) one. A decision that becomes inconvenient is superseded with `amends`, not
     removed.
  3. No commit RENAMES (R) one. A record's path is its identity.
  4. Every recommendation file's content still parses and still carries the id its filename claims, so a
     rewrite that preserved the path is caught too.

Exit codes: 0 clean, 1 a violation was found, 2 the history could not be read.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

# Kinds whose records are evidence and must never change after they are written. `runs` is included: it is
# the packet provenance a decision points at, and rewriting it would change what the decision was made from.
IMMUTABLE_KINDS = ("recommendations", "executions", "evaluations", "postmortems", "import_receipts",
                   "decision_gates", "runs")


def git(args, cwd):
    r = subprocess.run(["git"] + args, cwd=cwd, text=True, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr.strip()[:300]}")
    return r.stdout


def immutable_path(path: str) -> bool:
    parts = path.split("/")
    return len(parts) > 1 and parts[0] == "data" and parts[1] in IMMUTABLE_KINDS


def scan_history(root: str, since: str | None = None, ref: str = "HEAD") -> list:
    """Every non-additive change to an immutable record, with the commit that made it.

    `--diff-filter=MDR` asks git for exactly the three operations that are forbidden. Additions are what the
    ledger is made of and are not reported.
    """
    args = ["log", "--no-merges", "--diff-filter=MDR", "--name-status", "--format=%x00%H%x00%an%x00%aI%x00%s"]
    if since:
        args += [f"--since={since}"]
    args += [ref, "--", "data/"]
    out = git(args, root)

    violations, commit = [], None
    for line in out.splitlines():
        if line.startswith("\x00"):
            _, sha, author, when, subject = line.split("\x00", 4)
            commit = {"sha": sha, "author": author, "date": when, "subject": subject}
            continue
        if not line.strip() or commit is None:
            continue
        parts = line.split("\t")
        status, paths = parts[0], parts[1:]
        for p in paths:
            if immutable_path(p):
                violations.append({**commit, "status": status, "path": p})
    return violations


def scan_contents(root: str) -> list:
    """A record whose filename no longer matches the id inside it was rewritten in place."""
    bad = []
    base = os.path.join(root, "data", "recommendations")
    for dirpath, _dirs, files in os.walk(base):
        for fn in files:
            if not fn.endswith(".json"):
                continue
            path = os.path.join(dirpath, fn)
            try:
                with open(path) as f:
                    d = json.load(f)
            except (OSError, ValueError) as e:
                bad.append({"path": os.path.relpath(path, root), "problem": f"unreadable: {e}"})
                continue
            if d.get("recommendation_id") != fn[:-len(".json")]:
                bad.append({"path": os.path.relpath(path, root),
                            "problem": f"filename claims {fn[:-5]!r} but the record says "
                                       f"{d.get('recommendation_id')!r}"})
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--handicap-root", required=True, help="checkout of the handicap-data branch")
    ap.add_argument("--since", help="only inspect commits after this date (default: the whole history)")
    ap.add_argument("--ref", default="HEAD")
    a = ap.parse_args()

    root = os.path.abspath(a.handicap_root)
    if not os.path.isdir(os.path.join(root, ".git")):
        print(f"{root} is not a git checkout; the history cannot be verified", file=sys.stderr)
        return 2

    try:
        violations = scan_history(root, a.since, a.ref)
    except RuntimeError as e:
        print(f"could not read history: {e}", file=sys.stderr)
        return 2

    content_problems = scan_contents(root)
    n_records = sum(len([f for f in fs if f.endswith(".json")])
                    for k in IMMUTABLE_KINDS
                    for _d, _s, fs in os.walk(os.path.join(root, "data", k)))

    print(f"{n_records} record(s) across {len(IMMUTABLE_KINDS)} immutable kinds")
    print(f"history scanned: {a.ref}" + (f" since {a.since}" if a.since else " (full)"))

    if not violations and not content_problems:
        print("\nAPPEND-ONLY: no immutable record has ever been modified, deleted or renamed.")
        return 0

    print(f"\nAPPEND-ONLY VIOLATED: {len(violations)} history change(s), "
          f"{len(content_problems)} content mismatch(es)")
    for v in violations[:50]:
        print(f"  {v['status']}  {v['path']}\n      {v['sha'][:12]} {v['date']} {v['author']}: "
              f"{v['subject'][:80]}")
    for c in content_problems[:50]:
        print(f"  CONTENT  {c['path']}: {c['problem']}")
    print("\nThis branch's entire scientific value rests on records never changing after they are written. "
          "Investigate before trusting any number derived from this ledger, and see docs/OPERATIONS.md for "
          "the branch ruleset that prevents this server-side.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
