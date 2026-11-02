#!/usr/bin/env python3
"""Window postmortem over a local checkout of the handicap-data branch. Redacted JSON/markdown by default."""
import argparse
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
from nfl_edge.postmortem import report as RP  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger-root", required=True, help="checkout of the handicap-data branch (contains data/imported_wagers ...)")
    ap.add_argument("--start", default="2026-10-22")
    ap.add_argument("--end", default="2026-11-01")
    ap.add_argument("--out", default=os.path.join(REPO, "research/postmortem_2026-11-02/window_report.redacted.json"))
    ap.add_argument("--dashboard", default=os.path.join(REPO, "research/postmortem_2026-11-02/DASHBOARD.md"))
    ap.add_argument("--private-out", help="full per-position detail; MUST be outside the repository tree")
    a = ap.parse_args(argv)
    ledger = RP.load_ledger(a.ledger_root)
    rep = RP.build(ledger, a.start, a.end, redact=not a.private_out)
    if a.private_out:
        if os.path.realpath(a.private_out).startswith(os.path.realpath(REPO) + os.sep):
            sys.exit("refusing to write private detail inside the repository tree")
        with open(a.private_out, "w") as f:
            json.dump(rep, f, indent=1, sort_keys=True, default=str)
        rep.pop("private", None)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(rep, f, indent=1, sort_keys=True)
    with open(a.dashboard, "w") as f:
        f.write(RP.dashboard(rep))
    print("wrote", a.out, a.dashboard)


if __name__ == "__main__":
    main()
