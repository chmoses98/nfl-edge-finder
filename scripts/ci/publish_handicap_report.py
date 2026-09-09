#!/usr/bin/env python3
"""Publish a RUN NFL report to the browsable `handicap-reports` branch.

    python3 scripts/ci/publish_handicap_report.py --src data/handicap_report --message "..."

Why a dedicated orphan branch:

* `main` is code. A 12MB `packet.json` every two hours would make the repository unusable in a season, and
  the packet is a build artifact regenerable from the immutable ledger -- `.gitignore` already says so.
* `handicap-data` is the canonical **recommendation** ledger, append-only and immutable. A research report
  is not a decision record, and mixing a mutable `latest/` tree into it would blur exactly the line this
  project spends the most effort keeping sharp.
* `market-data` is append-only observations. `latest/` is deliberately *replaced*, which is the opposite
  contract.

So `handicap-reports` holds one thing: the newest good report, at a stable path anyone can click to.

    latest/manifest.json          what it is made of and how old every ingredient was
    latest/slate.md               read this first
    latest/packet.json            the full machine record
    latest/games/<game_id>.md     the full canonical per-game document
    state/horizons.json           which decision horizons have been captured (idempotency)
    history/index.jsonl           one manifest line per published run -- traceability without the bloat

**`latest/` is replaced atomically**: the whole tree is removed and rewritten in a single commit, so a
reader never sees this run's `slate.md` beside last run's `games/`. Nothing here is published unless the
build already verified its own outputs, so a failed run leaves the previous report in place wearing its own
`built_at` -- an old report is allowed to be old; it is never allowed to look new.

**The branch carries exactly one commit.** `latest/packet.json` is ~25MB. Committing a replacement on top
of the previous one every two hours would add ~300MB of history per day and roughly 2GB per NFL week --
which is the "hundreds of duplicate large packet snapshots" this design exists to avoid, merely arrived at
by replacement rather than by accumulation. So every publish rewrites the branch as a fresh root commit
carrying `history/index.jsonl` and `state/horizons.json` forward. The branch stays one snapshot in size
forever.

That is a force-push, and it is safe here for a reason that does not generalise: this branch is a *replaced
surface*, not a ledger. `market-data` and `handicap-data` are append-only and are never rewritten. The
immutable history of reports is the GitHub Actions artifact, one per run, retained 90 days; this branch
keeps only the manifest line per run, which is enough to trace an artifact back to its workflow run, source
SHAs, model version and packet SHA.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time

BRANCH = "handicap-reports"
README = """# handicap-reports

Generated RUN NFL handicap packets. **Never merge into `main`.**

* `latest/` — the newest successful report, replaced atomically on every successful run.
  * `latest/slate.md` — read this first.
  * `latest/games/<game_id>.md` — the full canonical per-game document.
  * `latest/manifest.json` — freshness: when it was built and how old the ledger, Kalshi capture and
    context captures were at that moment.
* `state/horizons.json` — which decision horizons (T-24h / T-6h / T-90m / T-30m) have been captured.
* `history/index.jsonl` — one manifest line per published run, for tracing an Actions artifact back to its
  source SHAs, model version and packet SHA.

Evidence only. Nothing on this branch is a bet, a recommendation, or a real-money authority, and no part of
producing it touches Airtable. See `docs/RUN_NFL.md` on `main`.
"""


def sh(cmd, cwd=None, check=True, capture=False):
    print("+", " ".join(cmd), flush=True)
    r = subprocess.run(cmd, cwd=cwd, check=False, text=True, capture_output=capture)
    if check and r.returncode != 0:
        if capture:
            print(r.stdout, r.stderr)
        raise SystemExit(f"command failed ({r.returncode}): {' '.join(cmd)}")
    return r


def remote_sha(repo, branch):
    r = subprocess.run(["git", "ls-remote", "--heads", "origin", branch], cwd=repo, text=True,
                       capture_output=True)
    line = (r.stdout or "").strip().split("\n")[0]
    return line.split()[0] if line and r.returncode == 0 else None


def prepare_worktree(repo, wt, branch):
    if os.path.exists(wt):
        shutil.rmtree(wt, ignore_errors=True)
        sh(["git", "worktree", "prune"], cwd=repo)
    exists = subprocess.run(["git", "ls-remote", "--exit-code", "--heads", "origin", branch],
                            cwd=repo, capture_output=True).returncode == 0
    if exists:
        sh(["git", "fetch", "--depth=1", "origin", branch], cwd=repo)
        sh(["git", "worktree", "add", "-f", wt, f"origin/{branch}"], cwd=repo)
        sh(["git", "checkout", "-B", branch, f"origin/{branch}"], cwd=wt)
    else:
        sh(["git", "worktree", "add", "--detach", wt], cwd=repo)
        sh(["git", "checkout", "--orphan", branch], cwd=wt)
        sh(["git", "rm", "-rf", "-q", "."], cwd=wt, check=False)
        with open(os.path.join(wt, "README.md"), "w") as f:
            f.write(README)
        sh(["git", "add", "README.md"], cwd=wt)
        sh(["git", "commit", "-q", "-m", f"init {branch} orphan branch"], cwd=wt)
    return exists


def stage(wt, src, manifest, horizon_state):
    """Write latest/, append the history line and refresh the state file. Returns paths touched."""
    latest = os.path.join(wt, "latest")
    if os.path.exists(latest):
        shutil.rmtree(latest)
    shutil.copytree(src, latest)
    readme = os.path.join(wt, "README.md")
    if not os.path.exists(readme):
        with open(readme, "w") as f:
            f.write(README)
    if manifest:
        hist_dir = os.path.join(wt, "history")
        os.makedirs(hist_dir, exist_ok=True)
        line = {k: manifest.get(k) for k in
                ("built_at", "trigger", "season", "week", "season_type", "slate_id", "handicap_run_id",
                 "packet_sha", "model_version", "artifact_name", "horizon_ids")}
        line["sources"] = manifest.get("sources")
        line["counts"] = manifest.get("counts")
        line["vintages"] = {k: {kk: vv for kk, vv in (manifest["vintages"].get(k) or {}).items()
                                if kk in ("run_id", "ledger_run_id", "written_at", "captured_at",
                                          "age_min")}
                            for k in ("shadow_pricing", "kalshi_capture", "context")}
        with open(os.path.join(hist_dir, "index.jsonl"), "a") as f:
            f.write(json.dumps(line, sort_keys=True) + "\n")
    if horizon_state is not None:
        sdir = os.path.join(wt, "state")
        os.makedirs(sdir, exist_ok=True)
        with open(os.path.join(sdir, "horizons.json"), "w") as f:
            json.dump(horizon_state, f, indent=1, sort_keys=True)


def main():
    ap = argparse.ArgumentParser(description="publish a handicap report to the handicap-reports branch")
    ap.add_argument("--src", required=True, help="verified report directory to become latest/")
    ap.add_argument("--message", required=True)
    ap.add_argument("--branch", default=BRANCH)
    ap.add_argument("--repo", default=os.getcwd())
    ap.add_argument("--horizon-state", default=None,
                    help="JSON file to write to state/horizons.json (already marked by the caller)")
    ap.add_argument("--attempts", type=int, default=6)
    ap.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT"))
    a = ap.parse_args()

    repo = os.path.abspath(a.repo)
    src = os.path.abspath(a.src)
    manifest_path = os.path.join(src, "manifest.json")
    # Fail closed: publishing a directory with no manifest would put a report on the branch that nobody can
    # date, which is the exact failure this whole change exists to remove.
    if not os.path.isdir(src) or not os.path.exists(manifest_path):
        print(f"FAIL: {src} is not a verified report directory (no manifest.json)", file=sys.stderr)
        return 2
    manifest = json.load(open(manifest_path))
    if manifest.get("report_status") != "SUCCESS":
        print(f"FAIL: refusing to publish a report whose status is "
              f"{manifest.get('report_status')!r}", file=sys.stderr)
        return 2
    for rel in ("slate.md", "packet.json"):
        if not os.path.exists(os.path.join(src, rel)):
            print(f"FAIL: {rel} missing from {src}", file=sys.stderr)
            return 2
    horizon_state = json.load(open(a.horizon_state)) if a.horizon_state else None

    wt = os.path.join(os.path.dirname(repo), "_handicap_reports_wt")
    exists = prepare_worktree(repo, wt, a.branch)

    for attempt in range(1, a.attempts + 1):
        expected = remote_sha(repo, a.branch) if exists else None
        stage(wt, src, manifest, horizon_state)
        # One root commit per publish: the tree is the whole state, so nothing is lost by dropping the
        # parent, and the branch does not accumulate a 25MB packet every two hours.
        sh(["git", "checkout", "-q", "--orphan", "_publish"], cwd=wt)
        sh(["git", "add", "-A"], cwd=wt)
        sh(["git", "commit", "-q", "-m", a.message], cwd=wt)
        sh(["git", "branch", "-q", "-M", a.branch], cwd=wt)
        push = ["git", "push", "-u", "origin", a.branch]
        if expected:
            # Not a bare --force: a concurrent publisher's commit must make this fail so we re-read their
            # history/index.jsonl and re-stage on top, rather than deleting their line.
            push.insert(2, f"--force-with-lease=refs/heads/{a.branch}:{expected}")
        r = subprocess.run(push, cwd=wt, text=True, capture_output=True)
        if r.returncode == 0:
            print("published", a.branch)
            break
        print("push failed:", r.stderr[-500:])
        if not exists:
            time.sleep(3 * attempt)
            exists = remote_sha(repo, a.branch) is not None
            continue
        # `latest/` is a replace-target: a concurrent publish is resolved by taking THEIR tip and
        # re-staging ours on it, so the last successful run wins and their manifest line survives.
        sh(["git", "fetch", "origin", a.branch], cwd=wt)
        sh(["git", "checkout", "-q", "-B", a.branch, f"origin/{a.branch}"], cwd=wt)
        sh(["git", "reset", "-q", "--hard", f"origin/{a.branch}"], cwd=wt)
        time.sleep(2 * attempt)
    else:
        print("FAILED to publish after retries", file=sys.stderr)
        return 3

    url = None
    if os.environ.get("GITHUB_SERVER_URL") and os.environ.get("GITHUB_REPOSITORY"):
        url = (f"{os.environ['GITHUB_SERVER_URL']}/{os.environ['GITHUB_REPOSITORY']}"
               f"/tree/{a.branch}/latest")
        print("browsable report:", url)
    if a.github_output and url:
        with open(a.github_output, "a") as f:
            f.write(f"report_url={url}\n")
            f.write(f"report_branch={a.branch}\n")
    if os.environ.get("GITHUB_STEP_SUMMARY") and url:
        focus = manifest.get("focus_game_file")
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
            f.write(f"\n### Browsable latest report\n\n* [{a.branch}/latest]({url})\n"
                    f"* [slate.md]({url}/slate.md)\n")
            if focus:
                f.write(f"* [{focus}]({url}/{focus})\n")
            f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
