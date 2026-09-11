"""Append-only projection store: write-once per (snapshot, arm); identical rerun no-op; contradiction fails closed.

Layout (parallel to the incumbent ledger and the three-arm corpus, never inside either):

    data/shadow/v2/projections/<day>/<snapshot_id>.<model_arm>.projections.jsonl.gz
    data/shadow/v2/projections/<day>/<snapshot_id>.<model_arm>.projections_manifest.json

`day` is the capture day of the snapshot (when the prediction was made). One file per arm per snapshot so
that adding an arm later adds a file and never rewrites one.
"""
from __future__ import annotations

import glob
import gzip
import hashlib
import json
import os
from datetime import datetime, timezone

from nfl_edge.projection.record import VOLATILE_FIELDS, content_hash

DIRNAME = os.path.join("shadow", "v2", "projections")


class ProjectionConflict(Exception):
    pass


def _day_of(snapshot_id: str) -> str:
    return snapshot_id[:4] + "-" + snapshot_id[4:6] + "-" + snapshot_id[6:8]


def read_rows(path: str) -> list:
    with gzip.open(path, "rt") as f:
        return [json.loads(line) for line in f if line.strip()]


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class ProjectionStore:
    def __init__(self, root: str):
        self.root = root

    def path(self, snapshot_id: str, model_arm: str) -> str:
        return os.path.join(self.root, _day_of(snapshot_id), f"{snapshot_id}.{model_arm}.projections.jsonl.gz")

    def manifest_path(self, snapshot_id: str, model_arm: str) -> str:
        return self.path(snapshot_id, model_arm).replace(".projections.jsonl.gz", ".projections_manifest.json")

    def plan(self, snapshot_id: str, model_arm: str, rows: list) -> dict:
        rows = [dict(r) for r in rows]
        for r in rows:
            if r.get("content_hash") != content_hash(r):
                raise ValueError(f"row {r.get('record_id')} carries a content hash that does not match its content")
        ids = [r["record_id"] for r in rows]
        if len(ids) != len(set(ids)):
            raise ProjectionConflict("duplicate record ids inside one snapshot")
        p = self.path(snapshot_id, model_arm)
        if not os.path.exists(p):
            return {"status": "NEW", "rows": rows, "conflicts": []}
        prev = {r["record_id"]: r for r in read_rows(p)}
        new = {r["record_id"]: r for r in rows}
        conflicts = []
        if set(prev) != set(new):
            conflicts.append(f"record set differs ({len(prev)} existing vs {len(new)} new)")
        for rid, r in new.items():
            if rid in prev and prev[rid].get("content_hash") != r["content_hash"]:
                diff = sorted(k for k in set(prev[rid]) | set(r) if k not in VOLATILE_FIELDS and k != "content_hash"
                              and prev[rid].get(k) != r.get(k))
                conflicts.append(f"{rid} differs in {diff[:8]}")
        return {"status": "CONFLICT" if conflicts else "NO_OP", "rows": rows, "conflicts": conflicts}

    def write(self, snapshot_id: str, model_arm: str, rows: list, manifest_extra: dict | None = None) -> dict:
        plan = self.plan(snapshot_id, model_arm, rows)
        if plan["status"] == "CONFLICT":
            raise ProjectionConflict("the same snapshot/arm would be rewritten with different content; nothing written:\n  "
                                     + "\n  ".join(plan["conflicts"][:20]))
        if plan["status"] == "NO_OP":
            man = json.load(open(self.manifest_path(snapshot_id, model_arm)))
            man["status"] = "NO_OP"
            return man
        p = self.path(snapshot_id, model_arm)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with gzip.GzipFile(p, "wb", mtime=0) as raw:
            for r in plan["rows"]:
                raw.write((json.dumps(r, separators=(",", ":"), sort_keys=True, default=str) + "\n").encode())
        by_state, by_family = {}, {}
        for r in plan["rows"]:
            by_state[r.get("support_state")] = by_state.get(r.get("support_state"), 0) + 1
            key = f"{r.get('market_family')}|{r.get('period')}"
            by_family[key] = by_family.get(key, 0) + 1
        man = {"status": "WRITTEN", "snapshot_id": snapshot_id, "model_arm": model_arm, "schema_version": plan["rows"][0].get("schema_version") if plan["rows"] else None,
               "written_at": datetime.now(timezone.utc).isoformat(), "n_rows": len(plan["rows"]),
               "by_support_state": by_state, "by_family": by_family, "file": os.path.basename(p), "sha256": _sha(p),
               "content_hashes_sha256": hashlib.sha256("\n".join(sorted(r["content_hash"] for r in plan["rows"])).encode()).hexdigest()}
        man.update(manifest_extra or {})
        with open(self.manifest_path(snapshot_id, model_arm), "w") as f:
            json.dump(man, f, indent=1, default=str)
        return man


def read_projections(roots, *, day_lo: str | None = None, day_hi: str | None = None, game_ids=None, arms=None) -> list:
    """Every projection row under the roots, de-duplicated by record_id (first occurrence wins; identical by construction)."""
    if isinstance(roots, str):
        roots = [roots]
    want = set(game_ids) if game_ids else None
    out, seen = [], set()
    for root in roots:
        for d in sorted(glob.glob(os.path.join(root, "*"))):
            day = os.path.basename(d)
            if not os.path.isdir(d) or (day_lo and day < day_lo) or (day_hi and day > day_hi):
                continue
            for path in sorted(glob.glob(os.path.join(d, "*.projections.jsonl.gz"))):
                arm = os.path.basename(path).split(".")[1]
                if arms and arm not in arms:
                    continue
                for r in read_rows(path):
                    if want is not None and r.get("game_id") not in want:
                        continue
                    if r["record_id"] in seen:
                        continue
                    seen.add(r["record_id"])
                    out.append(r)
    return out


def verify(roots) -> dict:
    problems, n = [], 0
    if isinstance(roots, str):
        roots = [roots]
    for root in roots:
        for path in sorted(glob.glob(os.path.join(root, "*", "*.projections.jsonl.gz"))):
            rows = read_rows(path)
            n += len(rows)
            seen = set()
            for r in rows:
                if r.get("content_hash") != content_hash(r):
                    problems.append(f"{path}: {r.get('record_id')} content hash mismatch")
                if r.get("record_id") in seen:
                    problems.append(f"{path}: duplicate {r.get('record_id')}")
                seen.add(r.get("record_id"))
            mp = path.replace(".projections.jsonl.gz", ".projections_manifest.json")
            if not os.path.exists(mp):
                problems.append(f"{path}: no manifest")
            else:
                man = json.load(open(mp))
                if man.get("sha256") != _sha(path):
                    problems.append(f"{path}: sha256 differs from manifest")
                if man.get("n_rows") != len(rows):
                    problems.append(f"{path}: manifest says {man.get('n_rows')} rows, file holds {len(rows)}")
    return {"rows": n, "problems": problems, "ok": not problems}
