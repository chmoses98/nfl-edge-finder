"""The immutable evaluation corpus: one truth per (prediction, evaluation version), written once.

Layout, parallel to the shadow ledger (which partitions by capture day because that is when a prediction was
made). Evaluations partition by GAME, because that is when a truth becomes knowable:

    data/shadow/evaluations/<game_id>/<eval_version>.<batch_id>.evaluations.jsonl.gz
    data/shadow/evaluations/<game_id>/<eval_version>.<batch_id>.evaluation_manifest.json

Why batch files rather than one file per game: a file that is appended to is a file that is rewritten, and a
rewritten file cannot be proven unchanged. Each run writes a NEW batch containing only rows the corpus does
not already have, so every published file is write-once and the corpus is the union of its batches. Republishing
touches no existing path, which is also what keeps the `market-data` publisher's rebase conflict-free.

THE THREE OUTCOMES OF A RERUN
-----------------------------
    NEW         this (prediction_id, evaluation_version) has no row yet          -> written
    NO-OP       a row exists and its content hash is identical                   -> nothing written
    CONFLICT    a row exists and the new truth differs                           -> raise, write nothing

CONFLICT is the important one. It means two runs disagree about what happened -- a changed settlement source, a
corrected statistic, a different close -- and the corpus must not quietly hold both or silently prefer one. The
run fails, names every conflicting field, and a human decides (usually by bumping `evaluation_version`, which
makes the new reading a NEW truth alongside the old one rather than a replacement of it).

`evaluated_at` is excluded from the content hash: the wall-clock time a row was computed is not part of what it
claims. Everything that IS a claim -- the settlement, the close, every derived number -- is inside the hash.
"""
from __future__ import annotations

import glob
import gzip
import hashlib
import json
import os
from datetime import datetime, timezone

EVALUATIONS_DIRNAME = "evaluations"
# File suffix of a batch. The incumbent corpus is `<stem>.evaluations.jsonl.gz` with `<stem>.evaluation_manifest.json`;
# a derived corpus (arm evaluations, player autopsies) reuses this store under its own suffix and root, so the
# write-once / no-op / conflict discipline is shared rather than reimplemented.
DEFAULT_SUFFIX = "evaluations"


def manifest_suffix(suffix: str) -> str:
    return "evaluation_manifest" if suffix == DEFAULT_SUFFIX else f"{suffix}_manifest"
# Fields that describe WHEN a row was produced rather than WHAT it claims. Excluded from the content hash so a
# rerun of identical evidence is a no-op instead of a conflict.
VOLATILE_FIELDS = ("evaluated_at",)


class EvaluationConflict(Exception):
    """A rerun produced a different truth for a prediction that already has one."""

    def __init__(self, conflicts: list):
        self.conflicts = conflicts
        lines = []
        for c in conflicts[:20]:
            diffs = ", ".join(f"{k}: existing={v[0]!r} new={v[1]!r}" for k, v in list(c["fields"].items())[:6])
            lines.append(f"  {c['prediction_id']} ({c['evaluation_version']}) in {c['existing_file']}: {diffs}")
        super().__init__(
            f"{len(conflicts)} evaluation(s) contradict an already-published truth; nothing was written.\n"
            + "\n".join(lines)
            + "\nBump the evaluation version to record a NEW reading, or fix the input that changed.")


def content_hash(row: dict) -> str:
    payload = {k: v for k, v in row.items() if k not in VOLATILE_FIELDS and k != "content_hash"}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()[:20]


def evaluation_id(prediction_id: str, evaluation_version: str) -> str:
    """Deterministic identity: the same prediction under the same evaluation version is the same record."""
    return hashlib.sha1(f"{prediction_id}|{evaluation_version}".encode()).hexdigest()[:20]


def batch_id(now=None) -> str:
    return (now or datetime.now(timezone.utc)).strftime("%Y%m%dT%H%M%SZ")


def stamp(row: dict) -> dict:
    """Attach the deterministic identity and content hash a row is stored under."""
    row = dict(row)
    row["evaluation_id"] = evaluation_id(row["prediction_id"], row.get("evaluation_version") or "")
    row["content_hash"] = content_hash(row)
    return row


def game_dir(root: str, game_id: str) -> str:
    return os.path.join(root, game_id)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class EvaluationCorpus:
    """Reader/writer over one or more roots holding the same corpus.

    `read_roots` is a list because a run reads the PUBLISHED corpus (a market-data worktree) and writes into a
    local staging directory that the publisher then copies. Both are consulted for duplicate detection, so a
    second run inside the same job cannot duplicate what the first one staged.
    """

    def __init__(self, write_root: str, read_roots=None, suffix: str = DEFAULT_SUFFIX):
        self.write_root = write_root
        self.read_roots = [r for r in ([write_root] + list(read_roots or [])) if r]
        self.suffix = suffix

    # ------------------------------------------------------------------ reading
    def batch_files(self, game_id: str | None = None) -> list:
        out = []
        for root in self.read_roots:
            pattern = os.path.join(root, game_id or "*", f"*.{self.suffix}.jsonl.gz")
            out.extend(sorted(glob.glob(pattern)))
        return out

    def load(self, game_id: str | None = None) -> dict:
        """(prediction_id, evaluation_version) -> (row, file). Later files never overwrite earlier ones."""
        existing = {}
        for path in self.batch_files(game_id):
            for row in read_rows(path):
                key = (row.get("prediction_id"), row.get("evaluation_version"))
                existing.setdefault(key, (row, path))
        return existing

    def games(self) -> list:
        seen = set()
        for root in self.read_roots:
            if not os.path.isdir(root):
                continue
            for name in os.listdir(root):
                if os.path.isdir(os.path.join(root, name)) and glob.glob(
                        os.path.join(root, name, f"*.{self.suffix}.jsonl.gz")):
                    seen.add(name)
        return sorted(seen)

    def evaluated_prediction_ids(self, game_id: str, evaluation_version: str | None = None) -> set:
        return {pid for (pid, ver) in self.index(game_id)
                if evaluation_version is None or ver == evaluation_version}

    # ------------------------------------------------------------------ streaming reads
    def iter_rows(self, game_id: str | None = None):
        """(row, file) one at a time, in load()'s order and with its first-file-wins de-duplication.

        Only the keys already yielded are retained, so a pass over the whole corpus holds one row at a time
        plus one small tuple per row seen. load() materialises every row; drivers that only aggregate use this.
        """
        seen = set()
        for path in self.batch_files(game_id):
            with gzip.open(path, "rt") as f:
                for line in f:
                    if not line.strip():
                        continue
                    row = json.loads(line)
                    key = (row.get("prediction_id"), row.get("evaluation_version"))
                    if key in seen:
                        continue
                    seen.add(key)
                    yield row, path

    def index(self, game_id: str | None = None) -> dict:
        """(prediction_id, evaluation_version) -> (content_hash, file). Ids and hashes only, never rows.

        This is what planning needs: whether a truth exists and whether it is the same truth. The row itself
        is fetched only when a conflict must be described (see BatchPlanner)."""
        out = {}
        for row, path in self.iter_rows(game_id):
            h = row.get("content_hash") or content_hash(row)
            out[(row.get("prediction_id"), row.get("evaluation_version"))] = (h, path)
        return out

    def batch_versions(self, game_id: str) -> set:
        """Evaluation versions that already have a written batch for this game, from file names alone."""
        out = set()
        for path in self.batch_files(game_id):
            out.add(os.path.basename(path).split(".")[0])
        return out

    def has_batch(self, game_id: str, evaluation_version: str) -> bool:
        """Does an immutable batch under this evaluation version already exist for the game (any root)?"""
        for root in self.read_roots:
            if glob.glob(os.path.join(root, game_id, f"{evaluation_version}.*.{self.suffix}.jsonl.gz")):
                return True
        return False

    def planner(self, game_id: str | None = None) -> "BatchPlanner":
        return BatchPlanner(self, game_id)

    # ------------------------------------------------------------------ planning
    def plan(self, rows: list, game_id: str | None = None) -> dict:
        """Split incoming rows into new / unchanged / conflicting, WITHOUT writing anything."""
        p = self.planner(game_id)
        noop = []
        for row in rows:
            row = stamp(row)
            if p.offer(row, stamped=True) == NOOP:
                noop.append(row)
        out = p.plan()
        out["noop"] = noop                      # callers count len(plan["noop"]); the rows are what they always got
        return out


    # ------------------------------------------------------------------ writing
    def write_batch(self, game_id: str, rows: list, *, evaluation_version: str, batch: str,
                    manifest_extra: dict | None = None, plan: dict | None = None) -> dict:
        """Write ONE new batch for one game. Refuses to overwrite an existing batch path.

        Returns the manifest. Writes nothing and returns a `status: NO_OP` manifest when there is nothing new,
        so an idle rerun leaves the corpus byte-identical.
        """
        plan = plan if plan is not None else self.plan(rows, game_id)
        if plan["conflicts"]:
            raise EvaluationConflict(plan["conflicts"])
        if not plan["new"]:
            return {"status": "NO_OP", "game_id": game_id, "evaluation_version": evaluation_version,
                    "written": 0, "unchanged": _n(plan["noop"])}
        d = game_dir(self.write_root, game_id)
        os.makedirs(d, exist_ok=True)
        stem = f"{evaluation_version}.{batch}"
        path = os.path.join(d, f"{stem}.{self.suffix}.jsonl.gz")
        if os.path.exists(path):
            raise FileExistsError(f"evaluation batch already exists (write-once, never rewritten): {path}")
        # mtime=0 so an identical batch compresses to identical bytes; the gzip header must not carry the
        # wall clock into a file whose whole purpose is being provably unchanged.
        with gzip.GzipFile(path, "wb", mtime=0) as raw:
            for row in plan["new"]:
                raw.write((json.dumps(row, separators=(",", ":"), sort_keys=True, default=str) + "\n").encode())
        man = {"status": "WRITTEN", "game_id": game_id, "evaluation_version": evaluation_version,
               "batch_id": batch, "schema_version": (plan["new"][0].get("schema_version") if plan["new"] else None),
               "written_at": datetime.now(timezone.utc).isoformat(),
               "written": len(plan["new"]), "unchanged": _n(plan["noop"]),
               "evaluations_file": os.path.basename(path),
               "evaluations_sha256": sha256_file(path),
               "prediction_ids_sha256": hashlib.sha256(
                   "\n".join(sorted(r["prediction_id"] for r in plan["new"])).encode()).hexdigest(),
               "content_hashes_sha256": hashlib.sha256(
                   "\n".join(sorted(r["content_hash"] for r in plan["new"])).encode()).hexdigest(),
               "by_settlement_status": _count(plan["new"], "settlement_status"),
               "by_settlement_kind": _count(plan["new"], "settlement_kind"),
               "by_close_status": _count(plan["new"], "close_status"),
               "by_family": _count(plan["new"], "family"),
               "by_model_version": _count(plan["new"], "model_version")}
        man.update(manifest_extra or {})
        with open(os.path.join(d, f"{stem}.{manifest_suffix(self.suffix)}.json"), "w") as f:
            json.dump(man, f, indent=1, default=str)
        return man


NEW, NOOP, CONFLICT, REPEAT = "NEW", "NOOP", "CONFLICT", "REPEAT"


# How many conflicts are described field by field. The COUNT is always exact and every conflict is always
# raised; beyond this many, the identity and the file are recorded without the diff. EvaluationConflict prints
# 20, so nothing a human reads is lost, and a storm cannot hold tens of thousands of evidence dicts in memory.
CONFLICT_DETAIL_KEEP = 200


class BatchPlanner:
    """plan() one row at a time, holding the corpus as ids + hashes and the batch as its NEW rows only.

    Unchanged rows are counted, not kept. That is what lets a driver settle a game of tens of thousands of
    records, or examine every season-scoped record on every run, with memory that scales with what is new.

    A HASH MISMATCH MUST NOT COST A FILE RE-READ. Deciding a mismatch needs the stored row itself: either to
    rescue it as a no-op (a hash written before a hashing change) or to name the fields that differ. Fetching
    that row by scanning its batch file made the cost of disagreement quadratic -- one full gzip re-parse per
    conflicting row -- and a real conflict storm therefore never reached its own error message. Week 2 of 2026
    hit exactly that: 11,662 season-scoped rows conflicting against a 21,888-row batch cost 0.44s each, 86
    minutes of pure re-parsing, so the job was killed by its 90-minute timeout before the raise and the run
    looked like it had simply published nothing. Each batch file is now parsed at most ONCE per planner, and
    only when a mismatch actually needs it -- the reconciling path (`new` / `noop`) still reads no rows at all.
    """

    def __init__(self, corpus: EvaluationCorpus, game_id: str | None):
        self.corpus, self.game_id = corpus, game_id
        self.existing = corpus.index(game_id)
        self.new: list = []
        self.noop = 0
        self.conflicts: list = []
        self.repeated = 0
        self._seen: set = set()
        self._rows_by_file: dict = {}        # path -> {(prediction_id, evaluation_version): row}, built on demand

    def _stored_row(self, path: str, key: tuple) -> dict:
        """The row a batch file holds under this identity, parsing that file at most once per planner."""
        idx = self._rows_by_file.get(path)
        if idx is None:
            idx = self._rows_by_file[path] = {}
            for row in read_rows(path):
                idx.setdefault((row.get("prediction_id"), row.get("evaluation_version")), row)
        return idx.get(key) or {}

    def offer(self, row: dict, *, stamped: bool = False) -> str:
        row = row if stamped else stamp(row)
        key = (row["prediction_id"], row.get("evaluation_version"))
        if key in self._seen:
            self.repeated += 1               # the same prediction offered twice in one batch is one row
            return REPEAT
        self._seen.add(key)
        prior = self.existing.get(key)
        if prior is None:
            self.new.append(row)
            return NEW
        prev_hash, prev_file = prior
        if prev_hash == row["content_hash"]:
            self.noop += 1
            return NOOP
        prev_row = self._stored_row(prev_file, key)
        if content_hash(prev_row) == row["content_hash"]:
            self.noop += 1                   # a stored hash that predates a hashing change; the content agrees
            return NOOP
        fields = ({k: (prev_row.get(k), row.get(k)) for k in sorted(set(prev_row) | set(row))
                   if k not in VOLATILE_FIELDS and k != "content_hash" and prev_row.get(k) != row.get(k)}
                  if len(self.conflicts) < CONFLICT_DETAIL_KEEP else {})
        self.conflicts.append({"prediction_id": row["prediction_id"],
                               "evaluation_version": row.get("evaluation_version"),
                               "existing_file": os.path.relpath(prev_file, os.path.dirname(prev_file) or "."),
                               "existing_path": prev_file, "fields": fields})
        return CONFLICT

    def plan(self) -> dict:
        return {"new": self.new, "noop": self.noop, "conflicts": self.conflicts}

    def counts(self) -> dict:
        return {"new": len(self.new), "unchanged": self.noop, "conflicts": len(self.conflicts), "repeated": self.repeated,
                "existing": len(self.existing)}


def _n(x) -> int:
    return x if isinstance(x, int) else len(x)

def read_rows(path: str) -> list:
    with gzip.open(path, "rt") as f:
        return [json.loads(line) for line in f if line.strip()]


def read_corpus(roots, game_id: str | None = None, suffix: str = DEFAULT_SUFFIX) -> list:
    """Every evaluation row under `roots`, de-duplicated by (prediction_id, evaluation_version)."""
    if isinstance(roots, str):
        roots = [roots]
    out, seen = [], set()
    for root in roots:
        for path in sorted(glob.glob(os.path.join(root, game_id or "*", f"*.{suffix}.jsonl.gz"))):
            for row in read_rows(path):
                key = (row.get("prediction_id"), row.get("evaluation_version"))
                if key in seen:
                    continue
                seen.add(key)
                out.append(row)
    return out


def verify_batches(roots, *, game_id: str | None = None, suffix: str = DEFAULT_SUFFIX) -> dict:
    """Re-derive every manifest's checksums from the files on disk. Used before publishing.

    Checks that each batch file's sha256 and row-level content hashes match the manifest, that every row's
    content hash matches its own content, and that no (prediction_id, evaluation_version) appears twice with
    different content across batches.
    """
    if isinstance(roots, str):
        roots = [roots]
    problems, batches, rows_seen = [], 0, {}
    for root in roots:
        for path in sorted(glob.glob(os.path.join(root, game_id or "*", f"*.{suffix}.jsonl.gz"))):
            batches += 1
            man_path = path.replace(f".{suffix}.jsonl.gz", f".{manifest_suffix(suffix)}.json")
            if not os.path.exists(man_path):
                problems.append(f"{path}: no manifest alongside the batch")
            else:
                man = json.load(open(man_path))
                digest = sha256_file(path)
                if man.get("evaluations_sha256") and man["evaluations_sha256"] != digest:
                    problems.append(f"{path}: sha256 {digest[:12]} != manifest {man['evaluations_sha256'][:12]}")
            rows = read_rows(path)
            if os.path.exists(man_path):
                man = json.load(open(man_path))
                if man.get("written") is not None and man["written"] != len(rows):
                    problems.append(f"{path}: manifest says {man['written']} rows, file holds {len(rows)}")
            for row in rows:
                if row.get("content_hash") and row["content_hash"] != content_hash(row):
                    problems.append(f"{path}: row {row.get('prediction_id')} content hash does not match its content")
                key = (row.get("prediction_id"), row.get("evaluation_version"))
                prev = rows_seen.get(key)
                if prev is None:
                    rows_seen[key] = (row.get("content_hash"), path)
                elif prev[0] != row.get("content_hash"):
                    problems.append(f"{key[0]} appears in {prev[1]} and {path} with different content")
    return {"batches": batches, "rows": len(rows_seen), "problems": problems, "ok": not problems}


def _count(rows, key):
    out = {}
    for r in rows:
        v = r.get(key)
        out[str(v)] = out.get(str(v), 0) + 1
    return dict(sorted(out.items()))
