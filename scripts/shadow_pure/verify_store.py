#!/usr/bin/env python3
"""Immutability check of the PURE shadow store. Exit 1 on any violation.

    python3 scripts/shadow_pure/verify_store.py --store <dir>                       hash chain + every listed sha256
    python3 scripts/shadow_pure/verify_store.py --store <dir> --published <dir>     pre-publish: local tree only ADDS
    python3 scripts/shadow_pure/verify_store.py --git-repo <checkout> --prefix data/shadow_pure [--ref HEAD]
                                                                                    history: no commit modified,
                                                                                    deleted or renamed a record
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.shadow_pure import store as S  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--store")
    ap.add_argument("--published")
    ap.add_argument("--git-repo")
    ap.add_argument("--prefix", default="data/shadow_pure")
    ap.add_argument("--ref", default="HEAD")
    ap.add_argument("--since", default=None)
    a = ap.parse_args(argv)
    problems = []
    if a.store:
        problems += [{"check": "hash_chain", **p} for p in S.verify_store(a.store)]
        if a.published:
            problems += [{"check": "additive_publish", **p} for p in S.check_publish_is_additive(a.store, a.published)]
    if a.git_repo:
        problems += [{"check": "git_history", **p} for p in S.scan_git_history(a.git_repo, a.prefix, a.ref, a.since)]
    print(json.dumps({"violations": problems, "n": len(problems)}, indent=1))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
