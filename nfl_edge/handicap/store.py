"""Paths and readers for the handicap-data branch.

Layout -- one immutable file per record, so a ChatGPT write is a file CREATE and two writers never touch the
same file:

    data/
      recommendations/<season>/week_<NN>/<recommendation_id>.json
      executions/<season>/week_<NN>/<execution_id>.json
      evaluations/<season>/week_<NN>/<evaluation_id>.json
      postmortems/<season>/week_<NN>/<postmortem_id>.json
      runs/<season>/week_<NN>/<handicap_run_id>.json      packet provenance for a run
      import_receipts/<season>/week_<NN>/<airtable_record_id>.json   transport provenance for a bridged run

Batching is supported at the level of a COMMIT, not a file: a handicap run writes many single-record files in
one commit. That keeps the conflict surface at zero while still being one reviewable change.

Collector writes never land here. `market-data` holds captures, quotes and the shadow ledger; this branch
holds judgement. Mixing them would make the collector's high-frequency commits fight with a human-paced
decision log, and would make it impossible to say when a decision was recorded versus when a price was.
"""
from __future__ import annotations

import glob
import json
import os

BRANCH = "handicap-data"
# `import_receipts` is transport provenance, not a decision record: it says which Airtable row carried a
# batch and what its payload hashed to. It shares the layout so there is one place that knows where a
# season/week file lives, but nothing in the scorecard reads it and a receipt never stands in for a
# recommendation.
KINDS = ("recommendations", "executions", "evaluations", "postmortems", "runs", "import_receipts")


def week_dir(root: str, kind: str, season: int, week: int) -> str:
    if kind not in KINDS:
        raise ValueError(f"unknown record kind {kind!r}; expected one of {KINDS}")
    return os.path.join(root, "data", kind, str(season), f"week_{int(week):02d}")


def record_path(root: str, kind: str, season: int, week: int, record_id: str) -> str:
    return os.path.join(week_dir(root, kind, season, week), f"{record_id}.json")


def read_kind(root: str, kind: str, season: int | None = None, week: int | None = None,
              include_test: bool = False) -> list:
    """Every record of a kind. TEST_ONLY records are excluded unless explicitly requested.

    That default is the guard that keeps mock data out of every performance number: a report has to ask for
    test records on purpose, so it can never include them by accident.
    """
    pat = os.path.join(root, "data", kind,
                       "*" if season is None else str(season),
                       "*" if week is None else f"week_{int(week):02d}", "*.json")
    out = []
    for p in sorted(glob.glob(pat)):
        try:
            d = json.load(open(p))
        except json.JSONDecodeError as e:
            raise ValueError(f"{p} is not valid JSON: {e}") from e
        if d.get("test_only") and not include_test:
            continue
        d["_path"] = p
        out.append(d)
    return out


def index_by(records: list, key: str) -> dict:
    out = {}
    for r in records:
        out.setdefault(r.get(key), []).append(r)
    return out


def latest_amendment_chain(recs: list) -> list:
    """Collapse amendment chains to the current opinion, preserving the originals in the returned records.

    A record that has been superseded is not deleted and not hidden -- it is simply not counted twice. The
    chain is available on each surviving record as `_superseded_ids`.
    """
    by_id = {r["recommendation_id"]: r for r in recs}
    superseded = {}
    for r in recs:
        if r.get("amends"):
            superseded.setdefault(r["amends"], []).append(r["recommendation_id"])
    out = []
    for r in recs:
        if r["recommendation_id"] in superseded:
            continue                      # an amended record is represented by its amendment
        chain, cur = [], r
        while cur.get("amends") and cur["amends"] in by_id:
            chain.append(cur["amends"])
            cur = by_id[cur["amends"]]
        r = dict(r)
        r["_superseded_ids"] = chain
        out.append(r)
    return out
