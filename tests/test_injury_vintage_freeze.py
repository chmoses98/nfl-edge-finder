"""The injury report is REBUILT IN PLACE, so its content must be snapshotted or history rewrites itself.

The breach these tests exist to prevent, in full:

    a projection is frozen at T1, when the player is not on the report
    nflverse republishes the file at T2 and the player is now Doubtful
    the T1 projection is replayed -- and comes back saying the model knew "Doubtful" at T1

Nothing about that is recoverable after the fact. The file carries no per-row timestamp (`date_modified` is in
`injuries_2024.parquet` and absent from 2025 on), so the only defence is to keep the bytes.
"""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.shadow_v2 import context as CX                                   # noqa: E402
from nfl_edge.shadow_v2 import vintage_snapshots as VS                         # noqa: E402

pl = pytest.importorskip("polars")

T1 = "2026-09-13T15:00:00+00:00"
T2 = "2026-09-13T16:00:00+00:00"
SEASON = 2026
ABSENT, LISTED = "00-0000001", "00-0000002"
SCHEMA = {"gsis_id": pl.Utf8, "week": pl.Int64, "team": pl.Utf8, "report_status": pl.Utf8,
          "practice_status": pl.Utf8, "report_primary_injury": pl.Utf8, "practice_primary_injury": pl.Utf8}


def _row(gsis, status, practice, team="KC", week=2):
    return {"gsis_id": gsis, "week": week, "team": team, "report_status": status,
            "practice_status": practice, "report_primary_injury": "Knee", "practice_primary_injury": "Knee"}


def _refile(root, rows):
    d = os.path.join(root, "data", "raw", "nflverse", "injuries")
    os.makedirs(d, exist_ok=True)
    pl.DataFrame(rows, schema=SCHEMA).write_parquet(os.path.join(d, f"injuries_{SEASON}.parquet"))
    return os.path.join("data", "raw", "nflverse", "injuries", f"injuries_{SEASON}.parquet")


def _manifest(root, retrieved_at):
    """The download manifest as `nflverse_download.py` writes it."""
    rel = os.path.join("data", "raw", "nflverse", "injuries", f"injuries_{SEASON}.parquet")
    p = os.path.join(root, "data", "raw", "nflverse", "_manifest.jsonl")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "a") as fh:
        fh.write(json.dumps({"path": rel, "url": f"https://x/injuries/injuries_{SEASON}.parquet",
                             "retrieved_at": retrieved_at, "sha256": "x" * 64}) + "\n")


def _block(root, as_of, gsis):
    src = CX.ContextSources(root, root, SEASON, CX._dt(as_of), log=lambda *a: None)
    return src.injury_block(gsis, 2)


@pytest.fixture
def two_vintages(tmp_path):
    """Vintage A at T1 (the player is absent), then the SAME FILE rebuilt at T2 with the player Doubtful."""
    root = str(tmp_path)
    rel = _refile(root, [_row(LISTED, "Questionable", "Limited")])
    VS.ensure_snapshot(root, rel, retrieved_at=T1, source_url="https://x/a", season=SEASON)
    _manifest(root, T1)
    rel = _refile(root, [_row(LISTED, "Questionable", "Limited"), _row(ABSENT, "Doubtful", "DNP")])
    VS.ensure_snapshot(root, rel, retrieved_at=T2, source_url="https://x/b", season=SEASON)
    _manifest(root, T2)
    return root


# ------------------------------------------------------------------- the mission's four-step test, exactly
def test_a_later_injury_file_cannot_change_an_already_frozen_cutoff(two_vintages):
    """Snapshot A at T1 (absent) -> project at T1 -> snapshot B at T2 (Doubtful) -> replay T1. Must not move."""
    root = two_vintages
    at_t1 = _block(root, T1, ABSENT)
    assert at_t1["state"] == CX.NOT_LISTED_AT_VINTAGE, "the T1 report did not list this player"
    assert at_t1["report_status"] is None and at_t1["practice_status"] is None
    # the newer file is on disk and is the one a naive reader would open
    live = pl.read_parquet(os.path.join(root, "data", "raw", "nflverse", "injuries", f"injuries_{SEASON}.parquet"))
    assert ABSENT in live["gsis_id"].to_list(), "the fixture must genuinely have been rebuilt in place"
    replay = _block(root, T1, ABSENT)
    assert replay == at_t1, "replaying the T1 cutoff after the file was rebuilt changed what the model knew"


def test_the_same_cutoff_at_t2_does_see_the_newer_designation(two_vintages):
    """The freeze must not become a refusal to ever learn anything: at T2 the newer vintage is correct."""
    b = _block(two_vintages, T2, ABSENT)
    assert b["state"] == "LISTED" and b["report_status"] == "Doubtful" and b["practice_status"] == "DNP"


def test_a_cutoff_before_every_vintage_reports_absence_and_never_reads_the_live_file(tmp_path):
    root = str(tmp_path)
    rel = _refile(root, [_row(ABSENT, "Doubtful", "DNP")])
    VS.ensure_snapshot(root, rel, retrieved_at=T2, source_url="https://x/b", season=SEASON)
    _manifest(root, T2)
    b = _block(root, T1, ABSENT)                       # T1 is BEFORE the only vintage
    assert b["state"] == CX.SOURCE_UNAVAILABLE, "no vintage at this cutoff must not silently read today's file"
    assert b["report_status"] is None and "never captured" in b["reason"]


def test_maturity_is_reported_from_the_selected_vintage_not_the_live_file(two_vintages):
    a = _block(two_vintages, T1, LISTED)
    b = _block(two_vintages, T2, LISTED)
    assert a["report_rows_for_week"] == 1 and b["report_rows_for_week"] == 2
    assert a["source_sha256"] != b["source_sha256"], "two vintages must be distinguishable by content"


# ------------------------------------------------------------------------------- the store's own invariants
def test_identical_bytes_do_not_create_a_second_vintage(tmp_path):
    root = str(tmp_path)
    rel = _refile(root, [_row(LISTED, "Questionable", "Limited")])
    first = VS.ensure_snapshot(root, rel, retrieved_at=T1, season=SEASON)
    again = VS.ensure_snapshot(root, rel, retrieved_at=T2, season=SEASON)
    assert first["sha256"] == again["sha256"]
    assert again["retrieved_at"] == T1, "re-downloading identical bytes is not new information"
    assert len(VS.read_index(root, "injuries", f"injuries_{SEASON}")) == 1


def test_a_vintage_row_carries_everything_the_contract_requires(tmp_path):
    root = str(tmp_path)
    rel = _refile(root, [_row(LISTED, "Questionable", "Limited"), _row(ABSENT, "Out", "DNP", team="BUF")])
    v = VS.ensure_snapshot(root, rel, retrieved_at=T1, source_url="https://x/a", season=SEASON)
    for k in ("retrieved_at", "source_url", "season", "sha256", "snapshot_path", "n_rows", "weeks", "teams"):
        assert v.get(k) is not None, f"vintage row is missing {k}"
    assert v["n_rows"] == 2 and v["weeks"] == [2] and sorted(v["teams"]) == ["BUF", "KC"]
    assert os.path.exists(os.path.join(root, v["snapshot_path"]))


def test_the_snapshot_survives_deletion_of_the_mutable_file(two_vintages):
    root = two_vintages
    os.remove(os.path.join(root, "data", "raw", "nflverse", "injuries", f"injuries_{SEASON}.parquet"))
    b = _block(root, T1, ABSENT)
    assert b["state"] == CX.NOT_LISTED_AT_VINTAGE, "the vintage, not the mutable file, is the source of truth"
