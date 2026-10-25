#!/usr/bin/env python3
"""Plan / rehearse moving owner-private wager records out of the public handicap-data branch. Reads the source; never modifies it; never pushes.

    python3 scripts/handicap/plan_private_ledger.py --ledger /path/to/handicap-data-checkout                    # the plan (counts + manifest hash, no contents)
    python3 scripts/handicap/plan_private_ledger.py --ledger L --copy-to /path/to/PRIVATE-repo-checkout           # copy + verify (target must be provably private)
    python3 scripts/handicap/plan_private_ledger.py --ledger L --copy-to /tmp/scratch --allow-local-target         # rehearsal into a scratch folder
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.request

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from nfl_edge.handicap import ledger_privacy as LP  # noqa: E402


def _origin_is_private(dst: str) -> bool:
    try:
        url = subprocess.run(["git", "-C", dst, "remote", "get-url", "origin"], capture_output=True, text=True, check=True).stdout.strip()
        slug = url.replace("git@github.com:", "").replace("https://github.com/", "").removesuffix(".git").strip("/")
        req = urllib.request.Request(f"https://api.github.com/repos/{slug}", headers={"Authorization": "Bearer " + os.environ["GITHUB_TOKEN"]} if os.environ.get("GITHUB_TOKEN") else {})
        return bool(json.load(urllib.request.urlopen(req, timeout=20)).get("private"))
    except Exception:
        return False


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--copy-to", default=None)
    ap.add_argument("--allow-local-target", action="store_true")
    a = ap.parse_args(argv)
    p = LP.plan(a.ledger)
    p.pop("private_files")
    print(json.dumps(p, indent=1))
    if a.copy_to:
        r = LP.copy_private(a.ledger, a.copy_to, allow_local_target=a.allow_local_target, target_is_private=_origin_is_private)
        print(json.dumps(r, indent=1))
        return 0 if not r["hash_mismatches"] else 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
