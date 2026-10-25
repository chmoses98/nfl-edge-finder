#!/usr/bin/env python3
"""Compose the issue comment for the NFL thesis-card workflow.  compose_card_reply.py --extract-rc N --card-rc N --run-url U --extract extract.json --card out/CARD.md --out reply.md"""
import argparse
import json
import os

LIMIT = 60000


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--extract-rc", default="")
    ap.add_argument("--card-rc", default="")
    ap.add_argument("--run-url", required=True)
    ap.add_argument("--extract", default=None)
    ap.add_argument("--card", default=None)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if a.extract_rc not in ("", "0"):
        try:
            errs = json.load(open(a.extract)).get("errors", [])
        except Exception:
            errs = ["no readable extract result"]
        body = ("**NFL CARD: no submission was read.**\n\n" + "\n".join(f"* {x}" for x in errs) +
                f"\n\nThe file is a json block from the repository owner containing `submission_version`; see `dossiers/ANALYST_GUIDE.md`. Run: {a.run_url}\n")
    elif a.card and os.path.exists(a.card):
        body = open(a.card).read() + f"\n---\nPlaced nothing; read-only. Run: {a.run_url} (card.json and the live venue evidence are in the run artifact)\n"
    else:
        body = f"**NFL CARD: the card could not be built** (rc {a.card_rc}). Nothing is authorized. Run: {a.run_url}\n"
    if len(body) > LIMIT:
        body = body[:LIMIT - 1000] + "\n\n... (truncated; the full CARD.md is in the run artifact)\n"
    with open(a.out, "w") as f:
        f.write(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
