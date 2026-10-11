"""Input provenance: every nflverse file a capture reads, with url, fetched_at, sha256 and HTTP last-modified.

The files are downloaded by the repository's own bronze downloader (scripts/data/nflverse_download.py), which
appends one manifest row per download to data/raw/nflverse/_manifest.jsonl. This module takes the newest row
per path, RE-HASHES the file on disk and refuses if the bytes differ from what the downloader recorded -- a file
whose provenance cannot be stated is not an input.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from nfl_edge.shadow_pure.store import sha256_file

NFLVERSE = os.path.join("data", "raw", "nflverse")


class ProvenanceError(RuntimeError):
    pass


def _utc(s) -> datetime:
    d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def required_files(seasons) -> list[str]:
    out = [os.path.join(NFLVERSE, "schedules", "games.csv"), os.path.join(NFLVERSE, "players", "players.parquet")]
    for s in seasons:
        out.append(os.path.join(NFLVERSE, "stats_player", f"stats_player_week_{s}.parquet"))
        out.append(os.path.join(NFLVERSE, "snap_counts", f"snap_counts_{s}.parquet"))
    return out


def source_id_of(path: str) -> str:
    p = path.replace("\\", "/")
    if "/stats_player/" in p:
        return "nflverse_stats_player_week"
    if "/snap_counts/" in p:
        return "nflverse_snap_counts"
    if "/players/" in p:
        return "nflverse_players_crosswalk"
    if "/schedules/" in p:
        return "nflverse_schedule_nonmarket_columns"
    raise ProvenanceError(f"unknown input {path}")


def load_manifest(root: str) -> dict:
    p = os.path.join(root, NFLVERSE, "_manifest.jsonl")
    if not os.path.exists(p):
        raise ProvenanceError(f"no download manifest at {p}: inputs have no recorded provenance")
    out = {}
    for line in open(p):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("path"):
            out[r["path"].replace("\\", "/")] = r
    return out


def input_provenance(root: str, seasons, *, as_of: datetime) -> list[dict]:
    """One provenance row per required file. Refuses a missing file, a hash mismatch or a fetch at/after as_of."""
    man = load_manifest(root)
    rows = []
    for rel in required_files(seasons):
        key = rel.replace("\\", "/")
        full = os.path.join(root, rel)
        if not os.path.exists(full):
            # a season file nflverse has not published (e.g. a future season) is simply absent; report it
            rows.append({"path": key, "source_id": source_id_of(key), "status": "ABSENT"})
            continue
        meta = man.get(key)
        if not meta:
            raise ProvenanceError(f"{key} is on disk but not in the download manifest")
        sha = sha256_file(full)
        if meta.get("sha256") and meta["sha256"] != sha:
            raise ProvenanceError(f"{key}: bytes on disk differ from the download manifest (sha256)")
        fetched = _utc(meta["retrieved_at"])
        if not fetched < as_of:
            raise ProvenanceError(f"{key} fetched at {fetched.isoformat()} is not before as_of {as_of.isoformat()}")
        row = {"path": key, "source_id": source_id_of(key), "status": "PRESENT", "fetched_at": fetched.isoformat(),
               "sha256": sha, "bytes": os.path.getsize(full), "url": meta.get("url"),
               "last_modified": meta.get("last_modified"), "etag": meta.get("etag")}
        if meta.get("derived_from"):
            parent = man.get(meta["derived_from"].replace("\\", "/")) or {}
            row.update({"derived_from": meta["derived_from"], "url": parent.get("url"),
                        "parent_sha256": parent.get("sha256"), "last_modified": parent.get("last_modified")})
        rows.append(row)
    return rows


def sources_block(prov: list[dict]) -> dict:
    """source_id -> (max fetched_at, uri, combined snapshot sha256 over that source's files)."""
    import hashlib
    agg: dict[str, dict] = {}
    for r in prov:
        if r.get("status") != "PRESENT":
            continue
        a = agg.setdefault(r["source_id"], {"fetched": [], "shas": [], "urls": []})
        a["fetched"].append(_utc(r["fetched_at"])); a["shas"].append(r["path"] + ":" + r["sha256"]); a["urls"].append(r.get("url") or "")
    out = {}
    for sid, a in agg.items():
        out[sid] = {"max_observed_at": max(a["fetched"]),
                    "snapshot_sha256": hashlib.sha256("\n".join(sorted(a["shas"])).encode()).hexdigest(),
                    "uri": "https://github.com/nflverse/nflverse-data/releases"}
    return out
