"""Pull the analyst's submission out of a GitHub issue (and its comments), for the doorbell workflow.

ChatGPT's GitHub integration can open issues and comment; it cannot dispatch a workflow. The submission is therefore carried in the ISSUE: a fenced ```json block
in the body or in a later comment (a long submission can be split across comments -- the LAST valid block wins, and a later block replaces an earlier one whole).

TRUST. The workflow only runs for an issue whose AUTHOR is the repository owner (the job-level `if`). This module enforces the same rule on COMMENTS: a block in a
comment by anyone else is ignored and counted. The content is data: it is validated by `submission.validate_structure` and every number in it still has to
survive the engine; nothing in it is executed, and nothing in it reaches a shell.
"""
from __future__ import annotations

import json
import re

FENCE = re.compile(r"```(?:json|JSON)?\s*\n(.*?)\n```", re.S)
MAX_BYTES = 900_000


def extract(issue: dict, comments: list, owner: str) -> dict:
    """{submission|None, source, ignored_foreign_blocks, errors}. `issue` and `comments` are GitHub API objects."""
    blocks, ignored, errors = [], 0, []
    cands = [("issue body", (issue.get("user") or {}).get("login"), issue.get("body") or "")]
    cands += [(f"comment {c.get('id')}", (c.get("user") or {}).get("login"), c.get("body") or "") for c in comments or []]
    for src, author, text in cands:
        for m in FENCE.finditer(text):
            raw = m.group(1)
            if '"submission_version"' not in raw:
                continue
            if author != owner:
                ignored += 1
                continue
            if len(raw.encode()) > MAX_BYTES:
                errors.append(f"{src}: submission block exceeds {MAX_BYTES} bytes")
                continue
            try:
                blocks.append((src, json.loads(raw)))
            except ValueError as e:
                errors.append(f"{src}: not valid JSON ({e})")
    if not blocks:
        return {"submission": None, "source": None, "ignored_foreign_blocks": ignored, "errors": errors or ["no ```json block containing submission_version was found from the repository owner"]}
    src, sub = blocks[-1]
    return {"submission": sub, "source": src, "ignored_foreign_blocks": ignored, "errors": errors}
