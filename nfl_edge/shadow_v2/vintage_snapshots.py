"""Content-addressed snapshots of the nflverse files that are REBUILT IN PLACE.

The problem this exists to solve, stated exactly.

`data/raw/nflverse/injuries/injuries_<season>.parquet` is mutable. nflverse republishes it as designations are
filed, and the download overwrites the previous contents. The file carries no per-row timestamp that would let a
reader bound it -- `date_modified` is present in `injuries_2024.parquet` and ABSENT from 2025 and 2026 -- so
there is no way to ask the current file what it said an hour ago.

The consequence was a real point-in-time breach. Re-running a projection at an OLD cutoff, with a NEWER file on
disk, produced a different frozen context: a player who was `NOT_LISTED_AT_THIS_VINTAGE` when the projection was
first made came back `LISTED / Doubtful / DNP`. The recorded vintage was honest; the CONTENT was not
reproducible. A research row whose context can change after the fact is not evidence.

The fix is the only one available when the source has no row-level time: keep every distinct version of the
file, addressed by its content, with the instant it was retrieved. A historical lookup then selects the latest
snapshot whose `retrieved_at <= information_frontier` and reads THAT, never the mutable file.

    data/raw/nflverse/_vintages/injuries/injuries_2026/
        index.jsonl                      one row per distinct version, append-only
        <sha256[:16]>.parquet            the bytes, immutable, never rewritten

Each index row records what the mission requires of a vintage: `retrieved_at`, `source_url`, `season`,
`sha256`, the immutable `snapshot_path`, `n_rows`, `weeks` and `teams`.

Two rules keep this honest:

  * adoption is not reconstruction. When a file has never been snapshotted, `ensure_snapshot` registers the
    bytes that are on disk NOW under the retrieval time the download manifest records for them. That is a
    statement about the current file, not a guess about an older one.
  * a lookup that finds no qualifying snapshot returns nothing. It never falls back to the mutable file,
    because falling back is precisely the breach. The caller reports the absence.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
from datetime import datetime, timezone

VINTAGE_VERSION = "vintage-snapshots-1.0.0"
VINTAGE_DIRNAME = "_vintages"
INDEX_FILE = "index.jsonl"


def _utc(v):
    if v is None or v == "" or v == "UNKNOWN":
        return None
    if isinstance(v, datetime):
        return v if v.tzinfo else v.replace(tzinfo=timezone.utc)
    try:
        d = datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def vintage_dir(root: str, release: str, stem: str) -> str:
    return os.path.join(root, "data", "raw", "nflverse", VINTAGE_DIRNAME, release, stem)


def read_index(root: str, release: str, stem: str, *, extra_roots=()) -> list:
    """Every registered vintage, across the local tree and any published stores handed in.

    `data/raw/` is git-ignored and a CI runner is ephemeral, so the local store holds only what THIS run
    downloaded. The durable copy lives in the published evidence branch, and both are read: a vintage is
    identified by content, so the same version appearing in both places is one vintage, not two.
    """
    out, seen = [], set()
    for r in (root, *extra_roots):
        if not r:
            continue
        p = os.path.join(vintage_dir(r, release, stem), INDEX_FILE)
        if not os.path.exists(p):
            continue
        with open(p) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                key = row.get("sha256")
                if key and key in seen:
                    continue
                if key:
                    seen.add(key)
                out.append({**row, "_root": r})
    return out


def describe_injuries(path: str) -> dict:
    """Row, week and team census of an injury parquet, so a vintage can be judged without opening it again."""
    try:
        import polars as pl
        d = pl.read_parquet(path)
    except Exception as exc:                                       # noqa: BLE001
        return {"n_rows": None, "weeks": None, "teams": None, "describe_error": f"{type(exc).__name__}: {exc}"}
    weeks, teams, per_week = set(), set(), {}
    for r in d.iter_rows(named=True):
        wk = r.get("week")
        wk = int(wk) if wk is not None else None
        weeks.add(wk)
        t = r.get("team")
        if t:
            teams.add(t)
        w = per_week.setdefault(wk, {"rows": 0, "teams": set()})
        w["rows"] += 1
        if t:
            w["teams"].add(t)
    return {"n_rows": d.height,
            "weeks": sorted(w for w in weeks if w is not None),
            "teams": sorted(teams),
            "n_teams": len(teams),
            "rows_by_week": {str(k): {"rows": v["rows"], "teams": len(v["teams"])}
                             for k, v in sorted(per_week.items(), key=lambda kv: (kv[0] is None, kv[0]))}}


def ensure_snapshot(root: str, rel_path: str, *, retrieved_at, source_url=None, season=None,
                    describe=describe_injuries) -> dict | None:
    """Register the bytes currently at `rel_path` as an immutable vintage. Idempotent on content.

    Returns the index row, or None when the file does not exist. A file whose sha256 is already indexed is not
    copied again and its ORIGINAL `retrieved_at` is kept -- re-downloading identical bytes does not create a
    newer vintage, because no new information arrived.
    """
    src = os.path.join(root, rel_path)
    if not os.path.exists(src):
        return None
    release = os.path.basename(os.path.dirname(rel_path))
    stem = os.path.splitext(os.path.basename(rel_path))[0]
    digest = sha256_of(src)
    vdir = vintage_dir(root, release, stem)
    for row in read_index(root, release, stem):
        if row.get("sha256") == digest:
            return row
    os.makedirs(vdir, exist_ok=True)
    ext = os.path.splitext(rel_path)[1] or ".bin"
    snap_name = f"{digest[:16]}{ext}"
    snap_abs = os.path.join(vdir, snap_name)
    if not os.path.exists(snap_abs):
        tmp = snap_abs + ".part"
        shutil.copyfile(src, tmp)
        os.replace(tmp, snap_abs)
    ra = _utc(retrieved_at)
    row = {"vintage_version": VINTAGE_VERSION, "release": release, "stem": stem, "season": season,
           "source_path": rel_path, "source_url": source_url,
           "retrieved_at": ra.isoformat() if ra else None,
           "sha256": digest, "bytes": os.path.getsize(src),
           "snapshot_path": os.path.relpath(snap_abs, root),
           "registered_at": datetime.now(timezone.utc).isoformat(),
           **(describe(src) if describe else {})}
    with open(os.path.join(vdir, INDEX_FILE), "a") as fh:
        fh.write(json.dumps(row, sort_keys=True, default=str) + "\n")
    return row


def pick_vintage(root: str, release: str, stem: str, frontier, *, extra_roots=()) -> tuple[dict | None, str]:
    """The newest immutable vintage retrieved at or before `frontier`, and why when there is none.

    NEVER falls back to the mutable file. A caller with no qualifying vintage has no injury report for that
    instant, which is a fact to report rather than a gap to fill from today's rebuild.
    """
    rows = read_index(root, release, stem, extra_roots=extra_roots)
    if not rows:
        return None, "no immutable vintage has been registered for this file"
    cut = _utc(frontier)
    dated = [(v, r) for r in rows for v in [_utc(r.get("retrieved_at"))] if v is not None]
    if not dated:
        return None, "every registered vintage lacks a retrieval time"
    if cut is None:
        v, r = max(dated, key=lambda vr: vr[0])
        return r, "no frontier given: newest vintage"
    ok = [(v, r) for v, r in dated if v <= cut]
    if not ok:
        first = min(v for v, _ in dated)
        return None, (f"the earliest registered vintage was retrieved at {first.isoformat()}, after this "
                      f"cutoff ({cut.isoformat()}): the report as it stood then was never captured")
    v, r = max(ok, key=lambda vr: vr[0])
    return r, "selected"


def resolve_injuries(root: str, season: int, frontier, *, manifest: dict | None = None,
                     adopt: bool = True, extra_roots=()) -> tuple[str | None, dict | None, str]:
    """The parquet a projection at `frontier` may legitimately read, its vintage row, and the reason.

    `adopt` registers the current mutable file when it has never been snapshotted, under the retrieval time the
    download manifest records for it. That makes the FIRST run after this change behave correctly instead of
    reporting a gap it could have closed; it does not invent a vintage, because the manifest time is a real
    measurement of the bytes on disk.
    """
    rel = os.path.join("data", "raw", "nflverse", "injuries", f"injuries_{season}.parquet")
    stem = f"injuries_{season}"
    if adopt and os.path.exists(os.path.join(root, rel)):
        meta = (manifest or {}).get(rel) or {}
        ensure_snapshot(root, rel, retrieved_at=meta.get("retrieved_at"), source_url=meta.get("url"), season=season)
    row, why = pick_vintage(root, "injuries", stem, frontier, extra_roots=extra_roots)
    if row is None:
        return None, None, why
    return os.path.join(row.get("_root") or root, row["snapshot_path"]), row, why
