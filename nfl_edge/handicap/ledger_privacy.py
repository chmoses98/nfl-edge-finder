"""Plan and rehearse moving the OWNER'S private wager records out of the public `handicap-data` branch -- without touching the source and without pushing anything.

WHAT IS PUBLIC TODAY (verified anonymously, see docs/PRIVATE_LEDGER_MIGRATION.md): `handicap-data` of the public repository holds the owner's imported fills
(price, contracts, fees, execution time), their settlements and amendments. Anyone can read them without credentials, and so can every clone and cache.

WHAT THIS MODULE DOES. It (1) classifies every record by kind, (2) produces a content-hash manifest (paths and sha256, never contents), (3) lists the consumers that read
the branch and would need a credential for a private repository, and (4) can COPY the private kinds into a checkout of a PRIVATE repository the owner created, verifying each
file by hash. It never deletes or rewrites the source, never pushes, and refuses a target it cannot show to be private. Removing the data from public history is a separate,
irreversible owner decision documented in the migration guide; nothing here performs it.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil

PRIVATE_KINDS = ("imported_wagers", "wager_settlements", "wager_settlement_amendments", "import_receipts", "executions")
REVIEW_KINDS = ("decision_gates", "postmortems")          # may carry stakes or P&L: read before deciding
PUBLIC_OK_KINDS = ("recommendations", "evaluations", "runs")

CONSUMERS = (
    ("actual-wagers.yml", "reads fills and settlements to write the diagnosis; needs read access to the private store"),
    ("preflight.yml", "folds the owner's open exposure into the caps; an unreadable ledger BLOCKS every approval, so the credential must exist before cutover"),
    ("nfl-thesis-card.yml", "owner open exposure per game (the card redacts it in its public output)"),
    ("sync-handicap-airtable.yml", "writes imported wagers/receipts"),
    ("run-nfl.yml", "reads recommendations/runs (public-OK kinds)"),
    ("shadow-price.yml", "reads recommendations (public-OK kinds)"),
    ("weekly-research.yml", "reads the ledger for the weekly study"),
)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def classify(kind: str) -> str:
    return "OWNER_PRIVATE" if kind in PRIVATE_KINDS else ("REVIEW" if kind in REVIEW_KINDS else ("PUBLIC_OK" if kind in PUBLIC_OK_KINDS else "UNKNOWN"))


def inventory(root: str) -> dict:
    """{kind: [(relpath, sha256)]} for every record file under <root>/data/<kind>/."""
    base = os.path.join(root, "data")
    out: dict = {}
    if not os.path.isdir(base):
        return out
    for kind in sorted(os.listdir(base)):
        kd = os.path.join(base, kind)
        if not os.path.isdir(kd):
            continue
        files = []
        for dp, _dn, fn in os.walk(kd):
            for f in sorted(fn):
                p = os.path.join(dp, f)
                files.append((os.path.relpath(p, root).replace(os.sep, "/"), sha256_file(p)))
        out[kind] = sorted(files)
    return out


def plan(root: str) -> dict:
    inv = inventory(root)
    per_kind = {k: {"class": classify(k), "files": len(v)} for k, v in inv.items()}
    private_files = [(p, h) for k, v in inv.items() if classify(k) == "OWNER_PRIVATE" for p, h in v]
    man = hashlib.sha256(json.dumps(private_files, sort_keys=True).encode()).hexdigest()
    return {"per_kind": per_kind, "owner_private_files": len(private_files), "owner_private_manifest_sha256": man,
            "review_kinds_present": [k for k in inv if classify(k) == "REVIEW"], "unknown_kinds": [k for k in inv if classify(k) == "UNKNOWN"],
            "consumers": [{"workflow": w, "note": n} for w, n in CONSUMERS],
            "does_not_do": ["delete or rewrite the public branch", "push anywhere", "change any workflow"],
            "private_files": private_files}


def copy_private(src_root: str, dst_root: str, *, allow_local_target: bool = False, target_is_private=None) -> dict:
    """Copy OWNER_PRIVATE record files into a checkout of a private repository, verifying each by hash. Refuses a target not shown to be private.

    `target_is_private` is a callable(dst_root) -> bool supplied by the CLI (it asks the GitHub API about the checkout's origin); tests pass a stub. A bare local
    directory with no remote is allowed only with `allow_local_target` (a dry rehearsal into a scratch folder)."""
    if not os.path.isdir(dst_root):
        raise ValueError(f"target {dst_root!r} is not a directory")
    if os.path.abspath(dst_root) == os.path.abspath(src_root):
        raise ValueError("target is the source")
    private_ok = bool(target_is_private(dst_root)) if target_is_private else False
    if not private_ok and not allow_local_target:
        raise PermissionError("refusing: the target is not shown to be a PRIVATE repository (pass a verified private checkout, or --allow-local-target for a scratch rehearsal)")
    p = plan(src_root)
    copied, mismatches = 0, []
    for rel, h in p["private_files"]:
        dst = os.path.join(dst_root, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(os.path.join(src_root, rel), dst)
        if sha256_file(dst) != h:
            mismatches.append(rel)
        copied += 1
    manifest = {"copied": copied, "hash_mismatches": mismatches, "manifest_sha256": p["owner_private_manifest_sha256"], "source_modified": False}
    with open(os.path.join(dst_root, "MIGRATION_MANIFEST.json"), "w") as f:
        json.dump({k: v for k, v in manifest.items()} | {"files": [{"path": a, "sha256": b} for a, b in p["private_files"]]}, f, indent=1)
    return manifest
