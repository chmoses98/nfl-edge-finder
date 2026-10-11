"""Append-only, write-once storage with a per-run sha256 manifest hash chain (same contract as the PURE shadow store).

Three independent guards, because each one alone can be bypassed:

  1. `RunWriter.write` refuses to create a path that already exists (application level).
  2. Every run writes `manifests/<run_id>.manifest.json`: every file it wrote with its sha256, plus the sha256 of
     the newest manifest that already existed (`prev_manifest_sha256`). `verify_store` re-hashes every listed file
     and walks the chain, so a file edited or deleted after the fact -- by any route, including a hand edit or a
     force-push -- no longer matches its manifest (content level).
  3. `scan_git_history` reads the actual commit history of the branch that holds the store and reports any commit
     that MODIFIED, DELETED or RENAMED a path under it (history level; see scripts/shadow_pure/verify_store.py).

`check_publish_is_additive` is the pre-publish guard: a local tree may only ADD paths to the published store, or
re-send byte-identical ones.
"""
from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
import subprocess
from datetime import datetime, timezone

MANIFEST_DIR = "manifests"
MANIFEST_SUFFIX = ".manifest.json"


class ImmutableStoreError(RuntimeError):
    pass


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def jsonl_gz_bytes(rows) -> bytes:
    """Deterministic gzip (mtime 0, no file name) of sorted-key JSON lines."""
    raw = "".join(json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n" for r in rows).encode()
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0, filename="") as gz:
        gz.write(raw)
    return buf.getvalue()


def read_jsonl(path: str) -> list[dict]:
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as fh:
        return [json.loads(x) for x in fh if x.strip()]


def _manifests(root: str) -> list[str]:
    d = os.path.join(root, MANIFEST_DIR)
    if not os.path.isdir(d):
        return []
    return sorted(os.path.join(d, f) for f in os.listdir(d) if f.endswith(MANIFEST_SUFFIX))


def latest_manifest_sha(root: str) -> str | None:
    ms = _manifests(root)
    return sha256_file(ms[-1]) if ms else None


class RunWriter:
    """Writes one run's files under `root`, write-once, and seals them with a chained manifest."""

    def __init__(self, root: str, run_id: str, *, meta: dict | None = None):
        self.root, self.run_id, self.meta = root, run_id, dict(meta or {})
        self.files: list[dict] = []
        self.sealed = False
        os.makedirs(root, exist_ok=True)

    def write(self, relpath: str, data: bytes) -> str:
        if self.sealed:
            raise ImmutableStoreError("run already sealed")
        if relpath.startswith(MANIFEST_DIR + "/"):
            raise ImmutableStoreError("manifests are written by seal() only")
        path = os.path.join(self.root, relpath)
        if os.path.lexists(path):
            raise ImmutableStoreError(f"refusing to overwrite an existing record: {relpath}")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".part"
        with open(tmp, "xb") as fh:
            fh.write(data)
        os.link(tmp, path)          # fails if `path` appeared meanwhile: never clobbers
        os.remove(tmp)
        digest = sha256_bytes(data)
        self.files.append({"path": relpath, "sha256": digest, "bytes": len(data)})
        return digest

    def write_json(self, relpath: str, obj) -> str:
        return self.write(relpath, (json.dumps(obj, sort_keys=True, indent=1, default=str) + "\n").encode())

    def write_jsonl_gz(self, relpath: str, rows) -> str:
        return self.write(relpath, jsonl_gz_bytes(rows))

    def seal(self) -> dict:
        prev = latest_manifest_sha(self.root)
        man = {"run_id": self.run_id, "sealed_at": datetime.now(timezone.utc).isoformat(),
               "prev_manifest_sha256": prev, "files": sorted(self.files, key=lambda f: f["path"]), **self.meta}
        rel = f"{MANIFEST_DIR}/{self.run_id}{MANIFEST_SUFFIX}"
        path = os.path.join(self.root, rel)
        if os.path.lexists(path):
            raise ImmutableStoreError(f"manifest exists: {rel}")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "x") as fh:
            fh.write(json.dumps(man, sort_keys=True, indent=1) + "\n")
        self.sealed = True
        return man


def verify_store(root: str) -> list[dict]:
    """Every listed file present with its recorded sha256; every stored file listed; the chain links resolve."""
    problems: list[dict] = []
    if not os.path.isdir(root):
        return problems
    listed: set[str] = set()
    shas: dict[str, str] = {}
    ms = _manifests(root)
    for m in ms:
        shas[sha256_file(m)] = os.path.basename(m)
    for i, m in enumerate(ms):
        man = json.load(open(m))
        prev = man.get("prev_manifest_sha256")
        if i == 0 and prev is not None and prev not in shas:
            problems.append({"path": os.path.relpath(m, root), "problem": "first manifest points at a missing predecessor"})
        if i > 0 and prev is None:
            problems.append({"path": os.path.relpath(m, root), "problem": "chain broken: no predecessor recorded"})
        if prev is not None and prev not in shas:
            problems.append({"path": os.path.relpath(m, root), "problem": "chain broken: predecessor manifest missing or edited"})
        for f in man.get("files", []):
            listed.add(f["path"])
            p = os.path.join(root, f["path"])
            if not os.path.exists(p):
                problems.append({"path": f["path"], "problem": "DELETED (listed in a manifest, absent)"})
            elif sha256_file(p) != f["sha256"]:
                problems.append({"path": f["path"], "problem": "MODIFIED (sha256 differs from its manifest)"})
    for dirpath, _d, files in os.walk(root):
        for fn in files:
            rel = os.path.relpath(os.path.join(dirpath, fn), root)
            if rel.startswith(MANIFEST_DIR + os.sep) or rel.startswith(MANIFEST_DIR + "/"):
                continue
            if rel not in listed:
                problems.append({"path": rel, "problem": "UNLISTED (in the store but in no manifest)"})
    return problems


def check_publish_is_additive(local_root: str, published_root: str) -> list[dict]:
    """A local tree about to be copied over the published store may only add paths (or resend identical bytes)."""
    bad = []
    for dirpath, _d, files in os.walk(local_root):
        for fn in files:
            rel = os.path.relpath(os.path.join(dirpath, fn), local_root)
            pub = os.path.join(published_root, rel)
            if os.path.exists(pub) and sha256_file(pub) != sha256_file(os.path.join(dirpath, fn)):
                bad.append({"path": rel, "problem": "would OVERWRITE a published record with different bytes"})
    return bad


def scan_git_history(repo: str, prefix: str, ref: str = "HEAD", since: str | None = None) -> list[dict]:
    """Commits on `ref` that modified (M), deleted (D), renamed (R) or type-changed (T) a path under `prefix`."""
    cmd = ["git", "log", ref, "--no-renames", "--format=@@%H|%cI", "--name-status", "--diff-filter=MDRT"]
    if since:
        cmd.append(f"--since={since}")
    cmd += ["--", prefix]
    r = subprocess.run(cmd, cwd=repo, text=True, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git log failed: {r.stderr.strip()}")
    out, commit = [], None
    for line in r.stdout.splitlines():
        if line.startswith("@@"):
            sha, date = line[2:].split("|", 1)
            commit = {"sha": sha, "date": date}
        elif line.strip() and commit:
            status, path = line.split("\t", 1)
            out.append({**commit, "status": status, "path": path})
    return out
