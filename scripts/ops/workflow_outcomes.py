#!/usr/bin/env python3
"""WORKFLOW OUTCOMES: say what actually happened to every recent run, in words a human can act on.

GitHub reports four very different events as `cancelled`: a job that hit its `timeout-minutes`, a pending run
superseded by a newer one in the same concurrency group, an explicit cancel request, and a runner that lost its
host. The 2026-09-22 investigation needed an hour of log reading to tell them apart:

    35671357660  Shadow v2 settle   job ran 90.4 min against timeout-minutes 90         -> TIMED_OUT
    35759870759  Shadow v2 settle   "The operation was canceled." after 4 minutes          -> EXTERNALLY_CANCELLED
    35769703895  capture conductor  cancelled with no job ever started                     -> CANCELLED_BY_CONCURRENCY

Classes (one per run):

    SUCCESS                    completed, success (or skipped by its own gate)
    FAILED_BY_CODE             a step failed (not a publish step)
    PUBLICATION_FAILED         the failing step is a publish step (the evidence may exist only on the runner)
    TIMED_OUT                  cancelled at or beyond its job timeout
    CANCELLED_BY_CONCURRENCY   cancelled before any job started (superseded while pending)
    EXTERNALLY_CANCELLED       cancelled mid-run, well before the timeout (a cancel request or a lost runner)
    IN_PROGRESS / QUEUED       not finished

    python3 scripts/ops/workflow_outcomes.py --repo owner/name --hours 48 --out data/ops/workflow_outcomes
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

OUTCOMES_VERSION = "workflow-outcomes-1.0.0"
API = "https://api.github.com"


def _dt(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def job_timeout_minutes(workflow_text: str | None) -> float | None:
    """The largest `timeout-minutes:` in a workflow file (the job that can run longest)."""
    if not workflow_text:
        return None
    vals = [float(x) for x in re.findall(r"timeout-minutes:\s*(\d+)", workflow_text)]
    return max(vals) if vals else None


def classify(run: dict, jobs: list, timeout_min: float | None) -> dict:
    """One run + its jobs -> {outcome, detail}. Pure: no network."""
    status, concl = run.get("status"), run.get("conclusion")
    if status in ("queued", "waiting", "requested", "pending"):
        return {"outcome": "QUEUED", "detail": status}
    if status == "in_progress":
        return {"outcome": "IN_PROGRESS", "detail": "running"}
    if concl in ("success", "skipped", "neutral"):
        return {"outcome": "SUCCESS", "detail": concl}
    started_jobs = [j for j in jobs if j.get("started_at")]
    if concl == "cancelled":
        if not started_jobs:
            return {"outcome": "CANCELLED_BY_CONCURRENCY", "detail": "cancelled before any job started (superseded while pending)"}
        dur = max(((_dt(j.get("completed_at")) or _dt(run.get("updated_at"))) - _dt(j["started_at"])).total_seconds() / 60.0
                  for j in started_jobs)
        if timeout_min is not None and dur >= timeout_min - 1.0:
            return {"outcome": "TIMED_OUT", "detail": f"job ran {dur:.1f} min against timeout-minutes {timeout_min:.0f}"}
        return {"outcome": "EXTERNALLY_CANCELLED", "detail": f"cancelled after {dur:.1f} min" +
                (f" (timeout {timeout_min:.0f})" if timeout_min else "") + ": a cancel request or a lost runner"}
    if concl in ("failure", "timed_out", "startup_failure", "action_required"):
        if concl == "timed_out":
            return {"outcome": "TIMED_OUT", "detail": "conclusion timed_out"}
        failed = [s for j in jobs for s in (j.get("steps") or []) if s.get("conclusion") == "failure"]
        name = failed[0]["name"] if failed else None
        if name and name.lower().startswith("publish"):
            return {"outcome": "PUBLICATION_FAILED", "detail": f"failed step: {name}"}
        return {"outcome": "FAILED_BY_CODE", "detail": f"failed step: {name}" if name else concl}
    return {"outcome": "UNKNOWN", "detail": f"{status}/{concl}"}


def _get(path, token):
    req = urllib.request.Request(API + path, headers={"Accept": "application/vnd.github+json", "User-Agent": "nfl-edge-finder ops",
                                                      **({"Authorization": f"Bearer {token}"} if token else {})})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    ap.add_argument("--hours", type=float, default=48.0)
    ap.add_argument("--out", default="data/ops/workflow_outcomes")
    ap.add_argument("--workflows-dir", default=".github/workflows")
    ap.add_argument("--summary", default=os.environ.get("GITHUB_STEP_SUMMARY", ""))
    a = ap.parse_args(argv)
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    now = datetime.now(timezone.utc)
    since = now - timedelta(hours=a.hours)
    runs, page = [], 1
    while page <= 10:
        d = _get(f"/repos/{a.repo}/actions/runs?per_page=100&page={page}", token)
        batch = d.get("workflow_runs") or []
        runs += [r for r in batch if _dt(r["created_at"]) >= since]
        if not batch or _dt(batch[-1]["created_at"]) < since:
            break
        page += 1
    timeouts = {}
    for fn in os.listdir(a.workflows_dir) if os.path.isdir(a.workflows_dir) else []:
        timeouts[os.path.join(a.workflows_dir, fn)] = job_timeout_minutes(open(os.path.join(a.workflows_dir, fn)).read())
    rows = []
    for r in runs:
        jobs = []
        if r.get("conclusion") not in ("success", "skipped"):
            jobs = (_get(f"/repos/{a.repo}/actions/runs/{r['id']}/jobs", token).get("jobs") or [])
        c = classify(r, jobs, timeouts.get(r.get("path")))
        rows.append({"run_id": r["id"], "workflow": r.get("name"), "event": r.get("event"), "created_at": r.get("created_at"),
                     "updated_at": r.get("updated_at"), "head_sha": (r.get("head_sha") or "")[:12], **c})
    counts = {}
    for x in rows:
        counts.setdefault(x["workflow"], {}).setdefault(x["outcome"], 0)
        counts[x["workflow"]][x["outcome"]] += 1
    doc = {"outcomes_version": OUTCOMES_VERSION, "as_of": now.isoformat(), "hours": a.hours, "repo": a.repo,
           "counts": counts, "runs": rows}
    os.makedirs(a.out, exist_ok=True)
    json.dump(doc, open(os.path.join(a.out, f"{now.strftime('%Y%m%dT%H%M%SZ')}.workflow_outcomes.json"), "w"), indent=1)
    lines = [f"## Workflow outcomes, last {a.hours:.0f} h", "", "| workflow | outcome | runs |", "|---|---|---|"]
    for wf, cs in sorted(counts.items()):
        for k, v in sorted(cs.items()):
            lines.append(f"| {wf} | {k} | {v} |")
    bad = [x for x in rows if x["outcome"] not in ("SUCCESS", "IN_PROGRESS", "QUEUED")]
    if bad:
        lines += ["", "| run | workflow | outcome | detail |", "|---|---|---|---|"]
        lines += [f"| {x['run_id']} | {x['workflow']} | {x['outcome']} | {x['detail']} |" for x in bad[:60]]
    text = "\n".join(lines) + "\n"
    print(text)
    if a.summary:
        with open(a.summary, "a") as f:
            f.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
