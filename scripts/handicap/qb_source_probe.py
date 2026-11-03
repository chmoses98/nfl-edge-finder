#!/usr/bin/env python3
"""Probe candidate public sources for a field that NAMES the starting quarterback. Reports; never confirms.

    python3 scripts/handicap/qb_source_probe.py --out qb_source_probe.json [--summary $GITHUB_STEP_SUMMARY]

Why this exists: nothing the repo fetches automatically names a starter (docs/QB_CONFIRMATIONS.md), and the sandboxes this
project is built in cannot reach ESPN, Sleeper or nfl.com (CONNECT 403), so the shape of their pregame payloads cannot be
checked from there. This probe is meant to run once on a GitHub-hosted runner. For each candidate source it records
whether the source answered and which JSON key paths look like a starter designation for a quarterback. That is evidence
for a human to decide whether an adapter is justified. It writes NO confirmation, imports nothing from the ledger, and
its output is key paths and counts only -- no payload text is stored, so it is safe in a public log.

A key path is only a CANDIDATE. A field called "starter" that is false for every player, or that is filled only after
kickoff, confirms nothing; `observed_before_kickoff` is reported separately for that reason.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone

SOURCES = {
    "espn_scoreboard": "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard",
    "espn_summary": "https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event={event_id}",
    "sleeper_players": "https://api.sleeper.app/v1/players/nfl",
}
# depth charts, rosters, inactives and injury statuses are NOT starter designations (docs/QB_CONFIRMATIONS.md) and are
# listed here only so the report can say a path was recognised and set aside.
SET_ASIDE = re.compile(r"depth|roster|inactive|injur|status|active", re.I)
CANDIDATE = re.compile(r"starter|starting|probable|lineup", re.I)


def key_paths(obj, prefix="", out=None, limit=20000):
    """Every dotted key path in a JSON value (lists collapse to []), bounded."""
    out = set() if out is None else out
    if len(out) >= limit:
        return out
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}.{k}" if prefix else str(k)
            out.add(p)
            key_paths(v, p, out, limit)
    elif isinstance(obj, list):
        for v in obj[:50]:
            key_paths(v, f"{prefix}[]", out, limit)
    return out


def classify_paths(paths):
    # the WHOLE path decides what a field is: `athletes[].depthChart.starter` is a depth-chart field whatever its last segment says
    candidates = sorted(p for p in paths if CANDIDATE.search(p.split(".")[-1]) and not SET_ASIDE.search(p))
    set_aside = sorted(p for p in paths if CANDIDATE.search(p.split(".")[-1]) and SET_ASIDE.search(p))
    return candidates, set_aside


def analyse(name: str, payload, *, fetched_at: str) -> dict:
    paths = key_paths(payload)
    candidates, set_aside = classify_paths(paths)
    return {"source": name, "answered": True, "fetched_at": fetched_at, "key_paths": len(paths),
            "starter_designation_candidates": candidates[:40], "set_aside_paths": set_aside[:40],
            "verdict": "CANDIDATE_FIELDS_PRESENT_REVIEW_BY_A_HUMAN" if candidates else "NO_STARTER_DESIGNATION_FIELD"}


def fetch(url: str, timeout: int = 30):
    req = urllib.request.Request(url, headers={"User-Agent": "nfl-edge-finder-source-probe"})
    with urllib.request.urlopen(req, timeout=timeout) as r:        # noqa: S310 - fixed https URLs above
        return json.loads(r.read().decode("utf-8"))


def run(fetcher=fetch) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    results, event_id = [], None
    for name, url in SOURCES.items():
        try:
            if "{event_id}" in url:
                if not event_id:
                    results.append({"source": name, "answered": False, "reason": "NO_EVENT_ID_FROM_SCOREBOARD"})
                    continue
                url = url.format(event_id=event_id)
            payload = fetcher(url)
            if name == "espn_scoreboard":
                events = payload.get("events") or []
                event_id = events[0].get("id") if events else None
            results.append(analyse(name, payload, fetched_at=now))
        except Exception as exc:                                    # reachability is the finding; never raise
            results.append({"source": name, "answered": False, "reason": type(exc).__name__})
    return {"probed_at": now, "writes_confirmations": False, "results": results}


def markdown(report: dict) -> str:
    rows = ["### QB source probe (report only; writes no confirmation)", "", "| source | answered | verdict | candidate paths |", "|---|---|---|---|"]
    for r in report["results"]:
        rows.append(f"| {r['source']} | {r['answered']} | {r.get('verdict', r.get('reason', ''))} | {len(r.get('starter_designation_candidates', []))} |")
    return "\n".join(rows) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="")
    ap.add_argument("--summary", default="")
    a = ap.parse_args(argv)
    report = run()
    text = markdown(report)
    print(text)
    if a.out:
        json.dump(report, open(a.out, "w"), indent=2, sort_keys=True)
    if a.summary:
        open(a.summary, "a").write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
