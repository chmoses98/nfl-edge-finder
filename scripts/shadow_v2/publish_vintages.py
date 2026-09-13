#!/usr/bin/env python3
"""Persist the immutable nflverse vintages this run downloaded. ONE helper, called by every v2 data run.

WHY THIS EXISTS AS A SHARED COMMAND

`data/raw/nflverse/injuries/injuries_<season>.parquet` is rebuilt in place by nflverse as designations are
filed, and `data/raw/` is git-ignored, so the version a CI run downloaded exists only on that ephemeral runner.
`nflverse_download.py` already snapshots it content-addressably the moment it lands -- but a snapshot that is
never published dies with the runner.

Only `shadow-v2-horizons.yml` published them. `shadow-v2-project.yml` runs every two hours, downloads the same
mutable injury file, snapshots it, and threw the snapshot away. Horizons only fire at T-24h / T-6h / T-90m /
T-30m before a kickoff cluster, so the Wednesday, Thursday and Friday practice-report states -- the ones that
actually move a player's availability -- were downloaded, snapshotted, and permanently lost, every week.

The fix is wiring, not a second mechanism. This command is the single place that knows how vintages become
durable, and both workflows call it. Adding a third v2 data run means adding this one step, not copying a
publish block and hoping it stays in sync.

WHAT IT DOES

  1. ensure_snapshot() over the mutable releases present on disk, passing --market-data as an extra root so
     content already published is recognised and NEVER re-dated (that re-dating was the H1 defect). This is a
     belt-and-braces pass: the downloader normally did it already, and it is idempotent on content.
  2. shard_indexes() -- rename each live index.jsonl to index.<run_id>.jsonl so two runs publishing
     concurrently write different paths and neither can overwrite the other's lines.
  3. publish the tree to the `market-data` branch through the ordinary publisher.

FAIL BEHAVIOUR, EXPLICITLY

Losing a vintage is bad; losing a projection run is worse. This command is therefore FAIL-SOFT BY DEFAULT: it
reports what happened on stdout as JSON and exits 0 even when publishing fails, so the caller can run it with
`if: always()` without a failed publish masking the run's real result. Pass --strict to exit non-zero instead.
Nothing here ever reads or writes the mutable parquet, and nothing falls back to it.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.shadow_v2 import vintage_snapshots as VS  # noqa: E402

VINTAGE_SRC = os.path.join("data", "raw", "nflverse", VS.VINTAGE_DIRNAME)


def nflverse_manifest(root: str) -> dict:
    """path -> download metadata, last line wins (the newest download of that path)."""
    p = os.path.join(root, "data", "raw", "nflverse", "_manifest.jsonl")
    out = {}
    if os.path.exists(p):
        for line in open(p):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("path"):
                out[r["path"]] = r
    return out


def snapshot_present_releases(root: str, market_data: str | None, seasons) -> list:
    """Register whatever mutable-release files are on disk. Idempotent on content across every root."""
    man = nflverse_manifest(root)
    extra = (market_data,) if market_data else ()
    done = []
    for release in VS.SNAPSHOT_RELEASES if hasattr(VS, "SNAPSHOT_RELEASES") else ("injuries",):
        for season in seasons:
            rel = os.path.join("data", "raw", "nflverse", release, f"{release}_{season}.parquet")
            if not os.path.exists(os.path.join(root, rel)):
                continue
            meta = man.get(rel) or {}
            try:
                row = VS.ensure_snapshot(root, rel, retrieved_at=meta.get("retrieved_at"),
                                         source_url=meta.get("url"), season=season, extra_roots=extra)
            except BaseException as exc:                                   # noqa: BLE001
                done.append({"path": rel, "error": f"{type(exc).__name__}: {exc}"})
                continue
            if row:
                done.append({"path": rel, "sha256": (row.get("sha256") or "")[:16],
                             "retrieved_at": row.get("retrieved_at"),
                             "already_registered": row.get("_root") is not None and row.get("_root") != root})
    return done


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--market-data", default=None,
                    help="a checkout of the market-data branch; read as an extra vintage root so already-published "
                         "content is never re-dated")
    ap.add_argument("--seasons", default="", help="comma-separated seasons to snapshot (default: this year and last)")
    ap.add_argument("--run-id", default=None, help="index shard suffix; defaults to a UTC timestamp")
    ap.add_argument("--message", default=None)
    ap.add_argument("--no-publish", action="store_true", help="snapshot and shard only; do not push")
    ap.add_argument("--strict", action="store_true", help="exit non-zero if publishing fails")
    a = ap.parse_args(argv)

    now = datetime.now(timezone.utc)
    run_id = a.run_id or now.strftime("%Y%m%dT%H%M%SZ")
    if a.seasons.strip():
        seasons = [int(x) for x in a.seasons.split(",") if x.strip()]
    else:
        seasons = [now.year, now.year - 1]

    out = {"vintage_publish_version": "1.0.0", "run_id": run_id, "at": now.isoformat(),
           "market_data_root": a.market_data, "seasons": seasons}
    out["snapshotted"] = snapshot_present_releases(a.root, a.market_data, seasons)

    src_abs = os.path.join(a.root, VINTAGE_SRC)
    if not os.path.isdir(src_abs) or not any(os.scandir(src_abs)):
        out["status"] = "NOTHING_TO_PUBLISH"
        out["reason"] = "no vintage store on this runner: nothing was downloaded, or nothing new was registered"
        print(json.dumps(out, indent=1, default=str))
        return 0

    out["shards"] = [os.path.relpath(p, a.root) for p in VS.shard_indexes(a.root, run_id)]
    if a.no_publish:
        out["status"] = "SHARDED_NOT_PUBLISHED"
        print(json.dumps(out, indent=1, default=str))
        return 0

    msg = a.message or f"nflverse immutable vintages (injury report snapshots) {run_id}"
    cmd = [sys.executable, os.path.join(a.root, "scripts", "ci", "publish_market_data.py"),
           "--src", VINTAGE_SRC, "--message", msg, "--repo", a.root]
    r = subprocess.run(cmd, cwd=a.root, text=True, capture_output=True)
    out["publish_rc"] = r.returncode
    out["publish_tail"] = (r.stdout or "")[-600:] + (r.stderr or "")[-600:]
    out["status"] = "PUBLISHED" if r.returncode == 0 else "PUBLISH_FAILED"
    print(json.dumps(out, indent=1, default=str))
    if r.returncode != 0:
        print(f"::warning::vintage publish failed (rc={r.returncode}); the snapshots exist on this runner only",
              flush=True)
        return 1 if a.strict else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
