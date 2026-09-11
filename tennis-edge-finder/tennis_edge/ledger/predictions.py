"""Append-only prospective prediction ledger.

One JSONL row per (prediction_id). Rows are written once and never rewritten: the writer refuses to
open an existing daily file in any mode but append, refuses duplicate prediction_ids, and every row
carries a content hash chained to the previous row's hash so a rewritten history is detectable
(health gate TENNIS-12 recomputes the chain).

Fields (see docs/PROSPECTIVE_RESEARCH_PROTOCOL.md): prediction_id, generated_at_utc, match_id, ticker,
feature_snapshot_id, data_source_versions, model_version, git_sha, market quote at prediction time
(yes_bid/yes_ask/mid/ts), all model probabilities, uncertainty fields, quality flags, scheduled_start,
seconds_to_scheduled_start, actual_start (null until learned -- filled in a SEPARATE settlement table,
never in this row), prev_hash, row_hash.
"""
from __future__ import annotations

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone

REQUIRED = ("match_id", "ticker", "family", "model_version", "git_sha", "feature_snapshot_id", "data_source_versions",
            "models", "quality", "scheduled_start", "market_quote")


class LedgerError(RuntimeError):
    pass


def _hash(obj: dict) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


class PredictionLedger:
    def __init__(self, root: str):
        self.root = root
        os.makedirs(root, exist_ok=True)

    def _path(self, day: str) -> str:
        return os.path.join(self.root, f"{day}.jsonl")

    def _last_hash(self, day: str) -> str:
        p = self._path(day)
        if not os.path.exists(p):
            return "GENESIS"
        last = None
        with open(p) as f:
            for line in f:
                if line.strip():
                    last = json.loads(line)
        return last["row_hash"] if last else "GENESIS"

    def existing_ids(self) -> set[str]:
        ids = set()
        for fn in os.listdir(self.root):
            if fn.endswith(".jsonl"):
                with open(os.path.join(self.root, fn)) as f:
                    for line in f:
                        if line.strip():
                            ids.add(json.loads(line)["prediction_id"])
        return ids

    def append(self, row: dict) -> dict:
        missing = [k for k in REQUIRED if k not in row]
        if missing:
            raise LedgerError(f"missing fields {missing}")
        now = datetime.now(timezone.utc)
        row = dict(row)
        row.setdefault("prediction_id", str(uuid.uuid4()))
        row["generated_at_utc"] = now.isoformat()
        if row["prediction_id"] in self.existing_ids():
            raise LedgerError(f"duplicate prediction_id {row['prediction_id']}")
        day = now.strftime("%Y-%m-%d")
        row["prev_hash"] = self._last_hash(day)
        body = {k: v for k, v in row.items() if k != "row_hash"}
        row["row_hash"] = _hash(body)
        with open(self._path(day), "a") as f:
            f.write(json.dumps(row, separators=(",", ":"), default=str) + "\n")
        return row

    def verify_chain(self) -> list[str]:
        """Recompute every row hash and chain link. Returns a list of violations (empty == intact)."""
        v = []
        for fn in sorted(os.listdir(self.root)):
            if not fn.endswith(".jsonl"):
                continue
            prev = "GENESIS"
            with open(os.path.join(self.root, fn)) as f:
                for i, line in enumerate(f):
                    if not line.strip():
                        continue
                    r = json.loads(line)
                    body = {k: val for k, val in r.items() if k != "row_hash"}
                    if r.get("prev_hash") != prev:
                        v.append(f"{fn}:{i}: prev_hash mismatch")
                    if _hash(body) != r.get("row_hash"):
                        v.append(f"{fn}:{i}: row_hash mismatch (row modified)")
                    prev = r.get("row_hash")
        return v

    def rows(self):
        for fn in sorted(os.listdir(self.root)):
            if fn.endswith(".jsonl"):
                with open(os.path.join(self.root, fn)) as f:
                    for line in f:
                        if line.strip():
                            yield json.loads(line)
