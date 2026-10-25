#!/usr/bin/env python3
"""Write the analyst's submission out of a trigger issue: card_from_issue.py --issue issue.json --comments comments.json --owner OWNER --out submission.json

Exit 0 and a file on success; exit 4 with the reasons on stdout (the workflow posts them back to the issue) when there is no valid owner-authored block."""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from nfl_edge.handicap import issue_submission as IS  # noqa: E402
from nfl_edge.handicap import submission as SB  # noqa: E402


def _load_pages(path):
    """`gh api --paginate` prints one JSON array per page, back to back. Accept that (or a single array)."""
    if not path or not os.path.exists(path):
        return []
    text, dec, i, out = open(path).read().strip(), json.JSONDecoder(), 0, []
    while i < len(text):
        o, i = dec.raw_decode(text, i)
        out += o if isinstance(o, list) else [o]
        while i < len(text) and text[i].isspace():
            i += 1
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue", required=True)
    ap.add_argument("--comments", default=None)
    ap.add_argument("--owner", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    issue = json.load(open(a.issue))
    comments = _load_pages(a.comments)
    if (issue.get("user") or {}).get("login") != a.owner or not str(issue.get("title", "")).startswith("NFL CARD"):
        print(json.dumps({"ok": False, "errors": ["the issue must be authored by the repository owner and titled `NFL CARD ...`"], "ignored_foreign_blocks": 0}))
        return 4
    r = IS.extract(issue, comments, a.owner)
    errs = list(r["errors"])
    if r["submission"] is not None:
        errs += SB.validate_structure(r["submission"])
    if r["submission"] is None or errs:
        print(json.dumps({"ok": False, "errors": errs, "ignored_foreign_blocks": r["ignored_foreign_blocks"]}))
        return 4
    with open(a.out, "w") as f:
        json.dump(r["submission"], f)
    print(json.dumps({"ok": True, "source": r["source"], "reviews": len(r["submission"]["reviews"]), "theses": len(r["submission"]["theses"]),
                      "packet_sha": r["submission"].get("packet_sha"), "ignored_foreign_blocks": r["ignored_foreign_blocks"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
