"""H1 + H2: vintage selection across the roots PRODUCTION actually uses, and vintage persistence across runs.

The existing freeze tests all run against a SINGLE root, and every one of them passed while the production
topology was broken -- which is precisely why the defect survived. Production has two roots:

    LOCAL      data/raw/ on an ephemeral CI runner. Git-ignored. Empty at the start of every run; holds only
               what THIS run downloaded and registered.
    PUBLISHED  a checkout of the `market-data` branch, passed as `extra_roots`. The durable history.

Two failures lived in the gap between them.

H1  `ensure_snapshot` consulted only the LOCAL index, so a runner that re-downloaded an unchanged injury file
    found no match and registered those bytes again under TODAY's retrieval time. `read_index` then deduped by
    content first-root-wins with LOCAL first, so the fresh row shadowed the published one. A vintage retrieved
    on the 10th started claiming it was retrieved on the 12th -- it moved FORWARD past cutoffs it legitimately
    preceded -- and `pick_vintage` returned an OLDER vintage, or none, for a projection entitled to the newer.

H2  Only `shadow-v2-horizons.yml` published the vintage store. `shadow-v2-project.yml` downloaded the same
    mutable file every two hours, snapshotted it, and discarded it with the runner.

These tests model both roots and the publish step between runs. Nothing here is a stub: real parquet bytes,
real sha256 content addressing, the real `resolve_injuries` entry point the projector calls.
"""
import json
import os
import shutil

import polars as pl
import pytest

from nfl_edge.shadow_v2 import vintage_snapshots as VS

REL = os.path.join("data", "raw", "nflverse", "injuries", "injuries_2026.parquet")
SEASON = 2026

T1 = "2026-09-10T12:00:00+00:00"      # V1 retrieved: the victim is ABSENT from the report
T2 = "2026-09-11T12:00:00+00:00"      # V2 retrieved: the victim is Doubtful / DNP
T3 = "2026-09-12T14:00:00+00:00"      # a later run re-downloads bytes IDENTICAL to V2

BETWEEN_T1_T2 = "2026-09-10T18:00:00+00:00"
BETWEEN_T2_T3 = "2026-09-12T04:00:00+00:00"
BEFORE_T1 = "2026-09-01T00:00:00+00:00"

V1_ROWS = [{"gsis_id": "00-0000001", "week": 2, "team": "KC", "report_status": "Questionable",
            "practice_status": "Limited", "report_primary_injury": "Knee", "practice_primary_injury": "Knee"}]
V2_ROWS = V1_ROWS + [{"gsis_id": "00-VICTIM", "week": 2, "team": "KC", "report_status": "Doubtful",
                      "practice_status": "DNP", "report_primary_injury": "Hamstring",
                      "practice_primary_injury": "Hamstring"}]


def _root(tmp_path, name):
    r = tmp_path / name
    (r / os.path.dirname(REL)).mkdir(parents=True, exist_ok=True)
    return str(r)


def _write(root, rows):
    pl.DataFrame(rows).write_parquet(os.path.join(root, REL))


def _publish(local, published, run_id):
    """What the publish step does: shard the index, then overlay the tree onto the published store."""
    VS.shard_indexes(local, run_id)
    src = os.path.join(local, "data", "raw", "nflverse", VS.VINTAGE_DIRNAME)
    dst = os.path.join(published, "data", "raw", "nflverse", VS.VINTAGE_DIRNAME)
    if not os.path.isdir(src):
        return
    for d, _sub, files in os.walk(src):
        rel = os.path.relpath(d, src)
        os.makedirs(os.path.join(dst, rel), exist_ok=True)
        for fn in files:
            shutil.copy2(os.path.join(d, fn), os.path.join(dst, rel, fn))


def _ids(path):
    return sorted(pl.read_parquet(path)["gsis_id"].to_list())


@pytest.fixture()
def production(tmp_path):
    """PUBLISHED holds V1 and V2, registered by two earlier runs exactly as production would."""
    published, local = _root(tmp_path, "published"), _root(tmp_path, "local")
    for rows, at, run in ((V1_ROWS, T1, "run_a"), (V2_ROWS, T2, "run_b")):
        stage = _root(tmp_path, f"stage_{run}")
        _write(stage, rows)
        VS.ensure_snapshot(stage, REL, retrieved_at=at, season=SEASON, extra_roots=(published,))
        _publish(stage, published, run)
    # the mutable file this run finds on disk: nflverse has NOT changed it, so its bytes are V2's
    _write(local, V2_ROWS)
    return {"published": published, "local": local}


# ------------------------------------------------------------------ H1: selection across both roots
def test_the_published_history_is_visible_from_an_empty_local_root(production):
    rows = VS.read_index(production["local"], "injuries", "injuries_2026", extra_roots=(production["published"],))
    assert len(rows) == 2, "both published vintages must be visible from a runner that registered nothing"
    assert sorted(r["retrieved_at"] for r in rows) == [T1, T2]


def test_a_cutoff_between_t2_and_t3_selects_v2_not_v1(production):
    """THE H1 REGRESSION. The re-adopted bytes must not displace V2's real retrieval instant."""
    path, vintage, why = VS.resolve_injuries(
        production["local"], SEASON, BETWEEN_T2_T3,
        manifest={REL: {"retrieved_at": T3}}, extra_roots=(production["published"],))
    assert path is not None, why
    assert vintage["retrieved_at"] == T2, f"selected {vintage['retrieved_at']}, expected V2 at {T2}"
    assert "00-VICTIM" in _ids(path)


def test_a_cutoff_between_t1_and_t2_selects_v1(production):
    path, vintage, why = VS.resolve_injuries(
        production["local"], SEASON, BETWEEN_T1_T2,
        manifest={REL: {"retrieved_at": T3}}, extra_roots=(production["published"],))
    assert path is not None, why
    assert vintage["retrieved_at"] == T1
    assert "00-VICTIM" not in _ids(path), "the victim was not on the report at T1 and must not appear"


def test_a_cutoff_before_every_vintage_is_source_unavailable_and_never_reads_the_mutable_file(production):
    path, vintage, why = VS.resolve_injuries(
        production["local"], SEASON, BEFORE_T1,
        manifest={REL: {"retrieved_at": T3}}, extra_roots=(production["published"],))
    assert path is None and vintage is None
    assert "never captured" in why
    assert os.path.exists(os.path.join(production["local"], REL)), "the mutable file is present and still unused"


def test_re_adopting_identical_bytes_changes_none_of_the_three_answers(production):
    """Idempotence with respect to historical point-in-time truth, not merely to the file count."""
    cuts = (BETWEEN_T2_T3, BETWEEN_T1_T2, BEFORE_T1)
    def answers():
        out = []
        for c in cuts:
            p, v, _ = VS.resolve_injuries(production["local"], SEASON, c, manifest={REL: {"retrieved_at": T3}},
                                          extra_roots=(production["published"],))
            out.append((None if v is None else v["retrieved_at"], None if p is None else tuple(_ids(p))))
        return out
    first = answers()
    for _ in range(5):                                   # adoption runs on every projection; it must not drift
        assert answers() == first
    assert [a[0] for a in first] == [T2, T1, None]


def test_identical_bytes_never_acquire_a_newer_retrieval_time(production):
    VS.resolve_injuries(production["local"], SEASON, BETWEEN_T2_T3, manifest={REL: {"retrieved_at": T3}},
                        extra_roots=(production["published"],))
    rows = VS.read_index(production["local"], "injuries", "injuries_2026", extra_roots=(production["published"],))
    v2 = [r for r in rows if r.get("n_rows") == 2][0]
    assert v2["retrieved_at"] == T2, "V2's observation time moved forward; evidence may never move forward in time"
    assert T3 not in (v2.get("retrieved_at_history") or []) or v2["retrieved_at"] == T2


def test_an_undated_local_row_can_never_erase_a_published_retrieval_time(tmp_path):
    """The manifest can be missing. An undated adoption must not make a real vintage unusable."""
    published, local = _root(tmp_path, "pub"), _root(tmp_path, "loc")
    stage = _root(tmp_path, "stage")
    _write(stage, V1_ROWS)
    VS.ensure_snapshot(stage, REL, retrieved_at=T1, season=SEASON)
    _publish(stage, published, "run_a")
    _write(local, V1_ROWS)
    VS.ensure_snapshot(local, REL, retrieved_at=None, season=SEASON)          # no manifest entry
    row, why = VS.pick_vintage(local, "injuries", "injuries_2026", T2, extra_roots=(published,))
    assert row is not None, why
    assert row["retrieved_at"] == T1


def test_the_canonical_row_keeps_every_observation_instant_it_was_ever_given(production):
    stage = os.path.join(production["local"])
    VS.ensure_snapshot(stage, REL, retrieved_at=T3, season=SEASON)            # local-only, no extra roots
    rows = VS.read_index(stage, "injuries", "injuries_2026", extra_roots=(production["published"],))
    v2 = [r for r in rows if r.get("n_rows") == 2][0]
    assert v2["retrieved_at"] == T2
    assert T2 in v2["retrieved_at_history"] and T3 in v2["retrieved_at_history"], \
        "the merge must be auditable: every instant ever recorded for this content is kept"


def test_ensure_snapshot_does_not_re_register_content_published_elsewhere(production):
    before = len(VS.read_index(production["local"], "injuries", "injuries_2026",
                               extra_roots=(production["published"],)))
    VS.ensure_snapshot(production["local"], REL, retrieved_at=T3, season=SEASON,
                       extra_roots=(production["published"],))
    after = VS.read_index(production["local"], "injuries", "injuries_2026", extra_roots=(production["published"],))
    assert len(after) == before == 2
    local_index = os.path.join(VS.vintage_dir(production["local"], "injuries", "injuries_2026"), VS.INDEX_FILE)
    assert not os.path.exists(local_index), "known content must not be written into the local index at all"


# ------------------------------------------------------------------ H2: vintages survive across runs
def test_two_sequential_project_runs_leave_two_immutable_vintages(tmp_path):
    """Run A downloads content A, run B downloads content B. Both must survive their runners."""
    published = _root(tmp_path, "published")
    for rows, at, run in ((V1_ROWS, T1, "runA"), (V2_ROWS, T2, "runB")):
        local = _root(tmp_path, f"local_{run}")                              # a fresh, empty runner each time
        _write(local, rows)
        VS.ensure_snapshot(local, REL, retrieved_at=at, season=SEASON, extra_roots=(published,))
        _publish(local, published, run)
    rows = VS.read_index(published, "injuries", "injuries_2026")
    assert sorted(r["retrieved_at"] for r in rows) == [T1, T2]
    assert all(os.path.exists(os.path.join(r["_root"], r["snapshot_path"])) for r in rows)


def test_a_cutoff_after_a_but_before_b_selects_a_and_after_b_selects_b(tmp_path):
    published = _root(tmp_path, "published")
    for rows, at, run in ((V1_ROWS, T1, "runA"), (V2_ROWS, T2, "runB")):
        local = _root(tmp_path, f"local_{run}")
        _write(local, rows)
        VS.ensure_snapshot(local, REL, retrieved_at=at, season=SEASON, extra_roots=(published,))
        _publish(local, published, run)
    fresh = _root(tmp_path, "local_runC")
    _write(fresh, V2_ROWS)
    a, va, _ = VS.resolve_injuries(fresh, SEASON, BETWEEN_T1_T2, manifest={REL: {"retrieved_at": T3}},
                                   extra_roots=(published,))
    b, vb, _ = VS.resolve_injuries(fresh, SEASON, BETWEEN_T2_T3, manifest={REL: {"retrieved_at": T3}},
                                   extra_roots=(published,))
    assert va["retrieved_at"] == T1 and "00-VICTIM" not in _ids(a)
    assert vb["retrieved_at"] == T2 and "00-VICTIM" in _ids(b)


def test_run_c_with_bytes_identical_to_b_does_not_rewrite_bs_observation_time(tmp_path):
    published = _root(tmp_path, "published")
    for rows, at, run in ((V1_ROWS, T1, "runA"), (V2_ROWS, T2, "runB")):
        local = _root(tmp_path, f"local_{run}")
        _write(local, rows)
        VS.ensure_snapshot(local, REL, retrieved_at=at, season=SEASON, extra_roots=(published,))
        _publish(local, published, run)
    runC = _root(tmp_path, "local_runC")
    _write(runC, V2_ROWS)                                                    # unchanged upstream
    VS.ensure_snapshot(runC, REL, retrieved_at=T3, season=SEASON, extra_roots=(published,))
    _publish(runC, published, "runC")
    rows = VS.read_index(published, "injuries", "injuries_2026")
    assert sorted(r["retrieved_at"] for r in rows) == [T1, T2], "run C invented a third vintage or re-dated B"
    _, v, _ = VS.resolve_injuries(runC, SEASON, BETWEEN_T2_T3, manifest={REL: {"retrieved_at": T3}},
                                  extra_roots=(published,))
    assert v["retrieved_at"] == T2


def test_concurrent_publishers_cannot_overwrite_each_others_index(tmp_path):
    """Two runs publishing at once write different shard paths, so neither loses the other's lines."""
    published = _root(tmp_path, "published")
    locals_ = []
    for rows, at, run in ((V1_ROWS, T1, "runA"), (V2_ROWS, T2, "runB")):
        local = _root(tmp_path, f"local_{run}")
        _write(local, rows)
        VS.ensure_snapshot(local, REL, retrieved_at=at, season=SEASON)       # neither can see the other
        locals_.append((local, run))
    for local, run in locals_:                                               # both publish, last copy wins per path
        _publish(local, published, run)
    rows = VS.read_index(published, "injuries", "injuries_2026")
    assert sorted(r["retrieved_at"] for r in rows) == [T1, T2], "a concurrent publish lost a vintage"


def test_the_downloaders_own_call_shape_cannot_move_a_published_vintage_forward(tmp_path):
    """THE EXACT PRODUCTION PATH, using only the API that existed before the fix.

    `scripts/data/nflverse_download.py` calls `ensure_snapshot(ROOT, rel, retrieved_at=...)` with NO extra
    roots -- it has no market-data checkout to hand it. So the local index legitimately gains a row for bytes
    that are already published. What must never happen is that row winning the merge and dragging the
    vintage's observation instant forward to today. This test uses no new parameter anywhere, so it fails on
    BEHAVIOUR against the pre-fix implementation rather than on a signature.
    """
    def overlay(src_root, dst_root):
        """A plain tree overlay -- exactly what publish_market_data.py does, and no new API at all."""
        src = os.path.join(src_root, "data", "raw", "nflverse", VS.VINTAGE_DIRNAME)
        dst = os.path.join(dst_root, "data", "raw", "nflverse", VS.VINTAGE_DIRNAME)
        for d, _sub, files in os.walk(src):
            rel = os.path.relpath(d, src)
            os.makedirs(os.path.join(dst, rel), exist_ok=True)
            for fn in files:
                shutil.copy2(os.path.join(d, fn), os.path.join(dst, rel, fn))

    published, local = _root(tmp_path, "pub"), _root(tmp_path, "loc")
    for rows, at, run in ((V1_ROWS, T1, "runA"), (V2_ROWS, T2, "runB")):
        stage = _root(tmp_path, f"stage_{run}")
        _write(stage, rows)
        VS.ensure_snapshot(stage, REL, retrieved_at=at, season=SEASON)
        overlay(stage, published)

    _write(local, V2_ROWS)                                   # upstream unchanged: today's bytes ARE V2's
    VS.ensure_snapshot(local, REL, retrieved_at=T3, season=SEASON)   # the downloader, verbatim

    row, why = VS.pick_vintage(local, "injuries", "injuries_2026", BETWEEN_T2_T3, extra_roots=(published,))
    assert row is not None, f"the newest eligible vintage vanished: {why}"
    assert row["retrieved_at"] == T2, (
        f"vintage moved forward to {row['retrieved_at']}: a projection at {BETWEEN_T2_T3} was entitled to V2")
    assert row.get("n_rows") == 2


# ============================================================ V1: time and location are separate facts
#
# The canonical record used to be built by copying the EARLIEST-dated row wholesale. That conflated two
# different facts: WHEN the content was first observed, and WHERE its bytes can be read. An index line
# carrying a retrieval instant but no `snapshot_path` -- truncated, or hand-edited on the evidence branch --
# therefore became canonical purely by being oldest, erased a perfectly good path recorded for the SAME bytes,
# and `resolve_injuries` raised `KeyError: 'snapshot_path'` instead of reporting an absence.
#
# No writer in this repo emits such a row, so this is corruption-handling rather than a live path. It is still
# a regression the remediation introduced, and a crash inside the projector is not an acceptable way to meet a
# malformed input.

def _seed_one_vintage(tmp_path, name, rows, at):
    """One published vintage, returned with its real index row."""
    stage = _root(tmp_path, f"stage_{name}")
    _write(stage, rows)
    row = VS.ensure_snapshot(stage, REL, retrieved_at=at, season=SEASON)
    pub = _root(tmp_path, f"pub_{name}")
    _publish(stage, pub, name)
    return pub, row


def _index_path(root, shard):
    return os.path.join(VS.vintage_dir(root, "injuries", "injuries_2026"), shard)


def test_v1_case1_an_earlier_row_without_a_path_does_not_erase_a_later_valid_one(tmp_path):
    """CASE 1. Earliest time is kept; the READABLE path comes from the row that has one."""
    pub, good = _seed_one_vintage(tmp_path, "c1", V2_ROWS, T2)
    with open(_index_path(pub, "index.truncated.jsonl"), "w") as fh:      # same sha, EARLIER, no path
        fh.write(json.dumps({"sha256": good["sha256"], "retrieved_at": T1}) + "\n")

    rows = VS.read_index(pub, "injuries", "injuries_2026")
    assert len(rows) == 1, "same content must stay one vintage"
    assert rows[0]["retrieved_at"] == T1, "historical availability begins at the earliest legitimate instant"
    assert rows[0]["snapshot_path"] == good["snapshot_path"], "the readable path must survive"
    assert rows[0]["snapshot_bytes_present"] is True

    local = _root(tmp_path, "c1_local")
    path, vintage, why = VS.resolve_injuries(local, SEASON, "2026-09-30T00:00:00+00:00",
                                             manifest={}, adopt=False, extra_roots=(pub,))
    assert path is not None and os.path.exists(path), why
    assert vintage["retrieved_at"] == T1
    assert "00-VICTIM" in _ids(path), "the content itself must still be readable"


def test_v1_case2_an_earlier_row_whose_bytes_are_gone_does_not_erase_a_present_one(tmp_path):
    """CASE 2. A recorded-but-missing path loses to a path whose bytes are actually on disk."""
    pub, good = _seed_one_vintage(tmp_path, "c2", V2_ROWS, T2)
    with open(_index_path(pub, "index.stale.jsonl"), "w") as fh:
        fh.write(json.dumps({"sha256": good["sha256"], "retrieved_at": T1,
                             "snapshot_path": "data/raw/nflverse/_vintages/injuries/injuries_2026/gone.parquet"}) + "\n")
    rows = VS.read_index(pub, "injuries", "injuries_2026")
    assert rows[0]["retrieved_at"] == T1
    assert rows[0]["snapshot_path"] == good["snapshot_path"], "the present bytes must win over a dangling path"
    local = _root(tmp_path, "c2_local")
    path, _v, why = VS.resolve_injuries(local, SEASON, "2026-09-30T00:00:00+00:00",
                                        manifest={}, adopt=False, extra_roots=(pub,))
    assert path is not None and os.path.exists(path), why


def test_v1_case3_no_usable_path_at_all_fails_closed_without_raising(tmp_path):
    """CASE 3. SOURCE_UNAVAILABLE, no exception, and never the mutable file."""
    pub = _root(tmp_path, "c3_pub")
    os.makedirs(VS.vintage_dir(pub, "injuries", "injuries_2026"), exist_ok=True)
    with open(_index_path(pub, "index.jsonl"), "w") as fh:
        fh.write(json.dumps({"sha256": "deadbeef", "retrieved_at": T1}) + "\n")

    local = _root(tmp_path, "c3_local")
    _write(local, V2_ROWS)                                   # a mutable file IS present and must be ignored
    path, vintage, why = VS.resolve_injuries(local, SEASON, "2026-09-30T00:00:00+00:00",
                                             manifest={}, adopt=False, extra_roots=(pub,))
    assert path is None and vintage is None
    assert "no usable snapshot path" in why and "NOT a substitute" in why
    assert os.path.exists(os.path.join(local, REL)), "the mutable file was available and was refused"


def test_v1_case3b_a_recorded_path_whose_bytes_vanished_still_never_raises(tmp_path):
    """The other shape of 'no usable path': the row is well formed, the bytes are gone."""
    pub, good = _seed_one_vintage(tmp_path, "c3b", V2_ROWS, T2)
    os.remove(os.path.join(pub, good["snapshot_path"]))
    local = _root(tmp_path, "c3b_local")
    _write(local, V2_ROWS)
    path, _v, _why = VS.resolve_injuries(local, SEASON, "2026-09-30T00:00:00+00:00",
                                         manifest={}, adopt=False, extra_roots=(pub,))
    assert path is None or not os.path.exists(path), "a vanished vintage must not resolve to readable content"
    assert os.path.exists(os.path.join(local, REL)), "and must not be replaced by the mutable file"


def test_v1_case4_two_valid_paths_in_two_roots_resolve_deterministically(tmp_path):
    """CASE 4. The same vintage in two roots resolves identically whatever order the roots arrive in."""
    p1, _ = _seed_one_vintage(tmp_path, "c4a", V2_ROWS, T2)
    p2, _ = _seed_one_vintage(tmp_path, "c4b", V2_ROWS, T1)      # same bytes, different root, different time
    local = _root(tmp_path, "c4_local")
    forward = VS.read_index(local, "injuries", "injuries_2026", extra_roots=(p1, p2))
    reverse = VS.read_index(local, "injuries", "injuries_2026", extra_roots=(p2, p1))
    assert len(forward) == len(reverse) == 1
    for k in ("sha256", "retrieved_at", "snapshot_path", "retrieved_at_history"):
        assert forward[0][k] == reverse[0][k], f"{k} depends on root enumeration order"
    assert forward[0]["retrieved_at"] == T1, "earliest across roots"
    a = VS.resolve_injuries(local, SEASON, "2026-09-30T00:00:00+00:00", manifest={}, adopt=False, extra_roots=(p1, p2))
    b = VS.resolve_injuries(local, SEASON, "2026-09-30T00:00:00+00:00", manifest={}, adopt=False, extra_roots=(p2, p1))
    assert _ids(a[0]) == _ids(b[0]), "the resolved CONTENT must not depend on root order"


def test_v1_case5_different_content_hashes_stay_distinct_vintages(tmp_path):
    """CASE 5. Merging by content must not merge DIFFERENT content."""
    pub = _root(tmp_path, "c5_pub")
    for rows, at, run in ((V1_ROWS, T1, "a"), (V2_ROWS, T2, "b")):
        stage = _root(tmp_path, f"c5_{run}")
        _write(stage, rows)
        VS.ensure_snapshot(stage, REL, retrieved_at=at, season=SEASON)
        _publish(stage, pub, run)
    rows = VS.read_index(pub, "injuries", "injuries_2026")
    assert len(rows) == 2
    assert len({r["sha256"] for r in rows}) == 2
    assert sorted(r["retrieved_at"] for r in rows) == [T1, T2]


def test_v1_the_proven_cutoff_behaviour_is_unchanged_by_the_robustness_fix(tmp_path):
    """The H1 guarantee itself must survive: before T1 unavailable, T1-T2 -> V1, after T2 -> V2."""
    pub = _root(tmp_path, "keep_pub")
    for rows, at, run in ((V1_ROWS, T1, "a"), (V2_ROWS, T2, "b")):
        stage = _root(tmp_path, f"keep_{run}")
        _write(stage, rows)
        VS.ensure_snapshot(stage, REL, retrieved_at=at, season=SEASON)
        _publish(stage, pub, run)
    local = _root(tmp_path, "keep_local")
    _write(local, V2_ROWS)
    VS.ensure_snapshot(local, REL, retrieved_at=T3, season=SEASON)        # republish identical bytes later
    def at(cut):
        return VS.resolve_injuries(local, SEASON, cut, manifest={REL: {"retrieved_at": T3}}, extra_roots=(pub,))
    assert at(BEFORE_T1)[1] is None
    assert at(BETWEEN_T1_T2)[1]["retrieved_at"] == T1 and "00-VICTIM" not in _ids(at(BETWEEN_T1_T2)[0])
    assert at(BETWEEN_T2_T3)[1]["retrieved_at"] == T2 and "00-VICTIM" in _ids(at(BETWEEN_T2_T3)[0])
