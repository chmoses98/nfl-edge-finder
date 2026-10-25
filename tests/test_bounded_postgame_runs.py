"""The postgame drivers do BOUNDED, RESUMABLE, IDEMPOTENT work, and the close/CLV evidence can no longer be starved.

From 2026-10-23 (run #258) to 2026-10-25 (#269) every scheduled `Shadow v2 settlement & scorecard` run ended CANCELLED
at the 120-minute job limit. Measured on run 40144005725 (the settle log):

    projection index                                  15 min   (750 files re-indexed: the index only rides with a publish that never ran)
    settling 2026_04_ATL_NO (111,644 rows)            23 min
    every later game, 434-707 rows each              ~4 min    (each game re-decompressed the ~750 files that hold it)
    33 games owed, 15 reached before the limit

so the close/CLV step (`pair_closes_v2.py`), the evidence publish and the research export were skipped, and market-data
held closes only through week 4. These tests pin the repair:

  * a GROUP of games is streamed in ONE pass over the files and every game receives exactly what a stand-alone stream
    would have given it (so the batches are byte-identical to the one-game-at-a-time implementation);
  * a run attempts at most --max-games games, oldest kickoff first, stops starting groups when its time budget cannot
    hold the next one, reports what it postponed, and the next run resumes by skipping what now holds a batch;
  * running twice produces no new file and changes no byte of an existing write-once file;
  * the step outputs the publish gate reads are written BEFORE the whole-corpus rebuild, and that rebuild is its own
    phase, throttled while nothing changed;
  * the workflow runs closes first, publishes them before settlement starts, and bounds every derived step.
"""
from __future__ import annotations

import glob
import gzip
import hashlib
import json
import os
import sys

import pytest
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

from nfl_edge.projection import store as PS                                             # noqa: E402
from nfl_edge.settlement import work_plan as WP                                          # noqa: E402
from test_postgame_memory_v2 import (G1, G2, NOW, S1, S2, S3_, build_market_data, load_script, proj, result_book,  # noqa: E402
                                     run_settle, trailing_json, write_projection_file)

WORKFLOW = os.path.join(ROOT, ".github", "workflows", "shadow-v2-settle.yml")


# =============================================================================================== the work plan
GAMES = {
    "2026_02_B": {"kickoff_utc": "2026-09-20T17:00:00+00:00", "prob": 10, "n": 12, "files": ["f2", "f3"]},
    "2026_01_A": {"kickoff_utc": "2026-09-13T17:00:00+00:00", "prob": 10, "n": 12, "files": ["f1", "f2"]},
    "2026_03_C": {"kickoff_utc": "2026-09-27T17:00:00+00:00", "prob": 500, "n": 600, "files": ["f3", "f4"]},
    "2026_03_D": {"kickoff_utc": "2026-09-27T20:00:00+00:00", "prob": 10, "n": 12, "files": ["f3", "f4"]},
    "2026_09_X": {"kickoff_utc": None, "prob": 1, "n": 1, "files": ["f9"]},
}


def test_games_are_taken_oldest_kickoff_first_and_unknown_kickoffs_last():
    assert WP.oldest_first(GAMES, list(GAMES)) == ["2026_01_A", "2026_02_B", "2026_03_C", "2026_03_D", "2026_09_X"]
    assert WP.oldest_first(GAMES, ["2026_03_D", "2026_01_A", "2026_03_D"]) == ["2026_01_A", "2026_03_D"], "duplicates collapse"


def test_partition_bounds_the_rows_held_by_a_group_and_keeps_order():
    order = WP.oldest_first(GAMES, list(GAMES))
    assert WP.partition(order, GAMES, max_rows=100) == [["2026_01_A", "2026_02_B"], ["2026_03_C"], ["2026_03_D", "2026_09_X"]]
    assert WP.partition(order, GAMES, max_rows=1) == [[g] for g in order], "max_rows=1 is the one-game-at-a-time behaviour"
    assert WP.partition(order, GAMES, max_rows=10 ** 9) == [order]
    assert WP.partition([], GAMES, max_rows=5) == []
    assert WP.partition(order, GAMES, max_rows=100, row_key="n") == [["2026_01_A", "2026_02_B"], ["2026_03_C"], ["2026_03_D", "2026_09_X"]]


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def _selection(budget_minutes, max_games, *, max_rows=100):
    clock = FakeClock()
    budget = WP.Budget(budget_minutes, clock=clock)
    groups = WP.partition(WP.oldest_first(GAMES, list(GAMES)), GAMES, max_rows=max_rows)
    return clock, WP.select_groups(groups, GAMES, budget, max_games=max_games)


def test_an_unbounded_run_takes_every_group_and_postpones_nothing():
    _, sel = _selection(0, 0)
    assert [g for g in sel] == [["2026_01_A", "2026_02_B"], ["2026_03_C"], ["2026_03_D", "2026_09_X"]]
    assert sel.postponed == [] and sel.reason is None


def test_the_game_cap_trims_a_group_and_postpones_the_rest_in_order():
    _, sel = _selection(0, 3)
    taken = list(sel)
    assert [g for grp in taken for g in grp] == ["2026_01_A", "2026_02_B", "2026_03_C"]
    assert sel.postponed == ["2026_03_D", "2026_09_X"] and "game cap 3" in sel.reason
    _, sel = _selection(0, 1)
    assert [g for grp in sel for g in grp] == ["2026_01_A"] and sel.postponed == ["2026_02_B", "2026_03_C", "2026_03_D", "2026_09_X"]


def test_the_first_group_always_runs_and_later_groups_wait_for_a_budget_that_can_hold_them():
    clock, sel = _selection(1, 0)                       # one minute; each group is estimated at 0.8 s per file + 7 ms per row
    it = iter(sel)
    first = next(it)
    assert first == ["2026_01_A", "2026_02_B"]
    clock.t = 59.0                                      # 1 s left: the 500-row game needs ~3.5 s of rows alone
    assert list(it) == [] and sel.postponed == ["2026_03_C", "2026_03_D", "2026_09_X"] and "time budget" in sel.reason
    # a budget of zero minutes still attempts the first group: one huge game can never be starved forever
    clock2 = FakeClock()
    tiny = WP.Budget(0.0001, clock=clock2)
    clock2.t = 10.0
    sel2 = WP.select_groups([["2026_03_C"]], GAMES, tiny)
    assert list(sel2) == [["2026_03_C"]]
    # and with time to spare every group runs
    clock3, sel3 = _selection(600, 0)
    assert len(list(sel3)) == 3 and sel3.postponed == []


# =============================================================================================== the store
def _archive(tmp_path):
    root = str(tmp_path / "p")
    ga, gb, gc = G1, G2, "2026_03_KC_LAC"
    files = []
    files.append(write_projection_file(root, S1, "BOARD_V2", [proj(ga, S1, "BOARD_V2", k, 0.5) for k in (44, 46)]
                                       + [proj(gb, S1, "BOARD_V2", 70, None)]
                                       + [proj(None, S1, "BOARD_V2", 9, 0.4, engine="SEASON")]))
    files.append(write_projection_file(root, S2, "BOARD_V2", [proj(ga, S2, "BOARD_V2", k, 0.6) for k in (44, 46, 48)]
                                       + [proj(gc, S2, "BOARD_V2", 40, 0.5)]))
    dup = proj(ga, S2, "DATA_PLAYER_DIST", 44, 0.7)
    files.append(write_projection_file(root, S2, "DATA_PLAYER_DIST", [dup, dict(dup, p_yes=0.1)]))       # same record_id twice
    files.append(write_projection_file(root, S3_, "BOARD_V2", [proj(gb, S3_, "BOARD_V2", k, 0.45) for k in (70, 72)]
                                       + [proj(ga, S3_, "BOARD_V2", 44, 0.5)]))
    return root, sorted(files)


def test_a_group_stream_gives_every_game_exactly_what_its_own_stream_would(tmp_path):
    root, files = _archive(tmp_path)
    for prob in (None, True):
        group = list(PS.iter_projections_by_game(files, [G1, G2], has_probability=prob))
        for gid in (G1, G2):
            alone = [r["record_id"] for r in PS.iter_projections(files=files, game_ids=[gid], has_probability=prob)]
            assert [r["record_id"] for g, r in group if g == gid] == alone and alone, (gid, prob)
        assert {g for g, _ in group} == {G1, G2}, "a game that was not asked for never appears"
    st = PS.ScanStats()
    rows = list(PS.iter_projections_by_game(files, [G1], stats=st))
    assert st.reconciles() and st.rows_yielded == len(rows) and st.rows_duplicate == 1
    assert st.rows_prefiltered_out > 0, "other games' lines are rejected before json.loads"
    assert list(PS.iter_projections_by_game(files, [])) == []


def test_the_dedupe_is_per_game_so_a_shared_record_id_cannot_drop_another_games_row(tmp_path):
    root = str(tmp_path / "p")
    a, b = proj(G1, S1, "BOARD_V2", 44, 0.5), proj(G2, S1, "BOARD_V2", 70, 0.5)
    b["record_id"] = a["record_id"]
    f = write_projection_file(root, S1, "BOARD_V2", [a, b])
    assert sorted(g for g, _ in PS.iter_projections_by_game([f], [G1, G2])) == [G1, G2]


def test_the_season_line_filters_reject_only_lines_that_cannot_hold_the_rows_they_select(tmp_path):
    root, files = _archive(tmp_path)
    # a record without a game_id key at all, and one with a null kickoff, both must survive the filters
    snap = "20260914T000000Z"
    odd = proj(G1, snap, "BOARD_V2", 44, 0.5)
    del odd["game_id"]
    nokick = proj(G1, snap, "BOARD_V2", 46, 0.5, kickoff_utc=None)
    f = write_projection_file(str(tmp_path / "q"), snap, "BOARD_V2", [odd, nokick, proj(G1, snap, "BOARD_V2", 48, 0.5)])
    allfiles = files + [f]
    unfiltered = [r["record_id"] for r in PS.iter_projections(files=allfiles) if not r.get("game_id")]
    filtered = [r["record_id"] for r in PS.iter_projections(files=allfiles, line_filter=PS.may_lack_game) if not r.get("game_id")]
    assert filtered == unfiltered and len(unfiltered) == 2          # the season row and the key-less row
    want = [r["record_id"] for r in PS.iter_projections(files=allfiles) if not (r.get("game_id") and r.get("kickoff_utc"))]
    got = [r["record_id"] for r in PS.iter_projections(files=allfiles, line_filter=PS.may_lack_game_or_kickoff)
           if not (r.get("game_id") and r.get("kickoff_utc"))]
    assert got == want and len(want) == 3
    st = PS.ScanStats()
    list(PS.iter_projections(files=allfiles, line_filter=PS.may_lack_game, stats=st))
    assert st.reconciles() and st.rows_prefiltered_out >= 8, "game rows are rejected without being parsed"


def test_a_parallel_index_build_equals_the_sequential_one_and_writes_the_same_files(tmp_path):
    root = str(tmp_path / "p")
    for i in range(6):
        snap = f"2026091{i}T120000Z"
        write_projection_file(root, snap, "BOARD_V2", [proj(G1, snap, "BOARD_V2", k, 0.5) for k in (44, 46)] + [proj(G2, snap, "BOARD_V2", 70, None)])
    seq = PS.ProjectionIndex([root], write_root=str(tmp_path / "i1"), workers=1)
    par = PS.ProjectionIndex([root], write_root=str(tmp_path / "i2"), workers=3)
    assert seq.built == par.built == 6 and seq.written == par.written == 6
    assert seq.entries == par.entries and list(seq.entries) == list(par.entries)
    a = {os.path.relpath(p, tmp_path / "i1"): open(p).read() for p in glob.glob(str(tmp_path / "i1" / "*" / "*.json"))}
    b = {os.path.relpath(p, tmp_path / "i2"): open(p).read() for p in glob.glob(str(tmp_path / "i2" / "*" / "*.json"))}
    assert a == b and len(a) == 6
    again = PS.ProjectionIndex([root], index_roots=[str(tmp_path / "i2")])
    assert again.built == 0 and again.reused == 6


# =============================================================================================== settle_v2
def batch_bytes(root, *kinds):
    """sha256 of every write-once batch file under `root`'s kinds (manifests carry wall-clock stamps, so are compared by name)."""
    out = {}
    for kind in kinds:
        for p in glob.glob(os.path.join(str(root), kind, "**", "*"), recursive=True):
            if os.path.isfile(p):
                rel = os.path.relpath(p, str(root))
                out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest() if p.endswith(".jsonl.gz") else None
    return out


def settle(tmp_path, monkeypatch, md, out, *extra, capsys=None, book=None):
    mod = load_script("settle_v2")
    assert run_settle(mod, monkeypatch, md, out, *extra, book=book) == 0
    return mod, (trailing_json(capsys.readouterr().out) if capsys is not None else None)


def test_streaming_a_slate_as_one_group_writes_the_same_bytes_as_one_game_at_a_time(tmp_path, monkeypatch, capsys):
    md, _, _ = build_market_data(tmp_path, with_capture=False)
    _, one = settle(tmp_path, monkeypatch, md, tmp_path / "grouped", capsys=capsys)
    _, two = settle(tmp_path, monkeypatch, md, tmp_path / "single", "--max-group-rows", "1", capsys=capsys)
    assert one["games_ready"] == two["games_ready"] == [G1, G2]
    assert one["per_game"][0]["group_size"] == 2 and two["per_game"][0]["group_size"] == 1
    a, b = batch_bytes(tmp_path / "grouped", "settlements", "autopsy"), batch_bytes(tmp_path / "single", "settlements", "autopsy")
    assert a == b and any(k.endswith(".jsonl.gz") for k in a), "byte-identical batches"
    assert one["accounting"]["silently_dropped"] == two["accounting"]["silently_dropped"] == 0


def test_a_capped_run_settles_the_oldest_game_and_the_next_run_resumes_then_a_third_is_a_no_op(tmp_path, monkeypatch, capsys):
    md, _, _ = build_market_data(tmp_path, with_capture=False)
    out = tmp_path / "out"
    _, s1 = settle(tmp_path, monkeypatch, md, out, "--max-games", "1", capsys=capsys)
    assert s1["games_ready"] == [G1], "the earliest kickoff first (G1 kicked off 2026-09-13, G2 on 09-18)"
    assert s1["games_postponed"] == [G2] and "game cap 1" in s1["postponed_reason"]
    assert glob.glob(str(out / "settlements" / G1 / "*.jsonl.gz")) and not glob.glob(str(out / "settlements" / G2 / "*"))
    first = batch_bytes(out, "settlements", "autopsy")

    _, s2 = settle(tmp_path, monkeypatch, md, out, "--max-games", "1", capsys=capsys)
    assert s2["games_skipped_already_settled"] == [G1] and s2["games_ready"] == [G2] and s2["games_postponed"] == []
    second = batch_bytes(out, "settlements", "autopsy")
    assert all(second[k] == v for k, v in first.items()), "no byte of an existing write-once file changed"
    assert len(second) > len(first)

    _, s3 = settle(tmp_path, monkeypatch, md, out, capsys=capsys)
    assert s3["written"] == 0 and s3["games_ready"] == [] and s3["games_skipped_already_settled"] == [G1, G2]
    assert batch_bytes(out, "settlements", "autopsy") == second, "an idle rerun creates no file and rewrites none"


def test_a_final_game_with_no_probability_row_is_reported_and_never_occupies_a_slot(tmp_path, monkeypatch, capsys):
    """2026_01_NE_SEA and 2026_01_SF_LA had projection rows but none with a probability: no batch could ever be written
    for them, so they were 'owed' (and re-streamed over ~750 files) on every run, and as the OLDEST kickoffs they would
    take the first slots of a capped run for ever."""
    proot = str(tmp_path / "md" / "data" / "shadow" / "v2" / "projections")
    write_projection_file(proot, S1, "BOARD_V2", [proj(G1, S1, "BOARD_V2", 44, 0.55), proj(G2, S1, "BOARD_V2", 70, None)])
    PS.write_sidecar(proot, S1, {"lineage": {}, "player_contexts": {}, "game_contexts": {}})
    md = str(tmp_path / "md")
    mod = load_script("settle_v2")
    opened = []
    real = mod.iter_projections_by_game
    monkeypatch.setattr(mod, "iter_projections_by_game", lambda files, games, **k: (opened.append(list(games)), real(files, games, **k))[1])
    assert run_settle(mod, monkeypatch, md, tmp_path / "out", "--max-games", "1") == 0
    s = trailing_json(capsys.readouterr().out)
    assert s["games_ready"] == [G1] and s["games_postponed"] == []
    assert s["games_without_probability_rows"] == [G2]
    assert opened == [[G1]], "the game that cannot dispatch anything is never streamed"
    assert run_settle(mod, monkeypatch, md, tmp_path / "out", "--game", G2) == 0       # a forced game is still examined
    assert trailing_json(capsys.readouterr().out)["games_ready"] == [G2]


def test_bounded_and_unbounded_runs_converge_on_the_same_corpus(tmp_path, monkeypatch, capsys):
    md, _, _ = build_market_data(tmp_path, with_capture=False)
    settle(tmp_path, monkeypatch, md, tmp_path / "drip", "--max-games", "1", capsys=capsys)
    settle(tmp_path, monkeypatch, md, tmp_path / "drip", "--max-games", "1", capsys=capsys)
    settle(tmp_path, monkeypatch, md, tmp_path / "all", capsys=capsys)
    drip, whole = batch_bytes(tmp_path / "drip", "settlements", "autopsy"), batch_bytes(tmp_path / "all", "settlements", "autopsy")
    assert {k: v for k, v in drip.items() if v} == {k: v for k, v in whole.items() if v}


def test_a_spent_time_budget_postpones_the_games_it_cannot_hold(tmp_path, monkeypatch, capsys):
    md, _, _ = build_market_data(tmp_path, with_capture=False)
    out = tmp_path / "out"
    # one group per game; the budget (~6 ms) cannot hold a second group (>= 0.8 s per file), the first is always attempted
    _, s = settle(tmp_path, monkeypatch, md, out, "--max-group-rows", "1", "--time-budget-minutes", "0.0001", capsys=capsys)
    assert s["games_ready"] == [G1] and s["games_postponed"] == [G2] and "time budget" in s["postponed_reason"]
    _, s2 = settle(tmp_path, monkeypatch, md, out, "--max-group-rows", "1", "--time-budget-minutes", "0.0001", capsys=capsys)
    assert s2["games_ready"] == [G2] and s2["games_postponed"] == [], "the next run resumes with the remainder"


def test_the_publish_gate_outputs_exist_before_the_whole_corpus_rebuild_and_survive_its_death(tmp_path, monkeypatch, capsys):
    md, _, _ = build_market_data(tmp_path, with_capture=False)
    mod = load_script("settle_v2")

    def boom(*a, **k):
        raise RuntimeError("the scorecard rebuild ran past its limit")
    monkeypatch.setattr(mod, "rebuild_derived", boom)
    gh = tmp_path / "gh.txt"
    with pytest.raises(RuntimeError):
        run_settle(mod, monkeypatch, md, tmp_path / "out", "--github-output", str(gh))
    out = dict(line.split("=", 1) for line in gh.read_text().splitlines())
    assert out["status"] == "WROTE" and int(out["written"]) > 0 and out["games_postponed"] == "0"
    assert glob.glob(str(tmp_path / "out" / "settlements" / G1 / "*.jsonl.gz")), "and the evidence is on disk"


def test_the_settle_phase_never_rebuilds_the_scorecard_and_the_derived_phase_is_throttled(tmp_path, monkeypatch, capsys):
    md, _, _ = build_market_data(tmp_path, with_capture=False)
    out = tmp_path / "out"
    gh = tmp_path / "gh.txt"
    _, s = settle(tmp_path, monkeypatch, md, out, "--phase", "settle", "--github-output", str(gh), capsys=capsys)
    assert s["phase"] == "settle" and s["written"] > 0
    assert not (out / "scorecards").exists() and not (out / "crosscheck").exists(), "the settle phase leaves the whole-corpus products alone"
    sc = out / "scorecards"

    def derived(*extra, now=None):
        mod = load_script("settle_v2")
        args = ["--market-data", md, "--out", str(out), "--target-season", "2026", "--phase", "derived", "--github-output", str(gh),
                "--now", now or NOW, *extra]
        assert mod.main(args) == 0
        return trailing_json(capsys.readouterr().out)

    d1 = derived("--derived-min-interval-hours", "6")
    assert d1["status"] == "REBUILT" and (sc / "scorecard_v2.json").exists() and (sc / "derived_state.json").exists()
    state = json.load(open(sc / "derived_state.json"))
    before = {p: open(p, "rb").read() for p in glob.glob(str(sc / "*"))}
    xc = batch_bytes(out, "crosscheck")

    d2 = derived("--derived-min-interval-hours", "6", now="2026-09-20T13:00:00+00:00")           # one hour later, nothing new
    assert d2["status"] == "SKIPPED_UNCHANGED" and "published scorecard stands" in d2["reason"]
    assert {p: open(p, "rb").read() for p in glob.glob(str(sc / "*"))} == before, "a skipped rebuild rewrites nothing"
    assert batch_bytes(out, "crosscheck") == xc
    assert gh.read_text().splitlines()[-1] == "derived=SKIPPED_UNCHANGED"

    d3 = derived("--derived-min-interval-hours", "6", now="2026-09-20T19:00:00+00:00")           # seven hours later: the age bound
    assert d3["status"] == "REBUILT" and "old" in d3["reason"]
    assert batch_bytes(out, "crosscheck") == xc, "an unchanged corpus owes no new cross-check batch: the rebuild is idempotent"
    assert json.load(open(sc / "derived_state.json"))["signature"] == state["signature"]

    d4 = derived()                                                                              # throttle off: the old behaviour
    assert d4["status"] == "REBUILT" and "throttle off" in d4["reason"]

    # a newly settled game changes the corpus signature, so the very next derived run rebuilds even inside the interval
    settle(tmp_path, monkeypatch, md, tmp_path / "out2", "--phase", "settle", "--max-games", "1", capsys=capsys)
    out2 = tmp_path / "out2"
    mod = load_script("settle_v2")
    common = ["--market-data", md, "--out", str(out2), "--phase", "derived", "--derived-min-interval-hours", "6"]
    assert mod.main([*common, "--now", NOW]) == 0
    assert trailing_json(capsys.readouterr().out)["status"] == "REBUILT"
    assert mod.main([*common, "--now", "2026-09-20T12:30:00+00:00"]) == 0
    assert trailing_json(capsys.readouterr().out)["status"] == "SKIPPED_UNCHANGED"
    run_settle(load_script("settle_v2"), monkeypatch, md, out2, "--phase", "settle")
    capsys.readouterr()
    assert mod.main([*common, "--now", "2026-09-20T12:31:00+00:00"]) == 0
    got = trailing_json(capsys.readouterr().out)
    assert got["status"] == "REBUILT" and "corpus changed" in got["reason"]


# =============================================================================================== pair_closes_v2
def pair(mod, md, out, *extra):
    return mod.main(["--market-data", md, "--out", str(out), "--now", NOW, *extra])


def test_closes_are_bounded_resumable_and_idempotent(tmp_path, capsys):
    md, _, _ = build_market_data(tmp_path)
    mod = load_script("pair_closes_v2")
    out = tmp_path / "out"
    gh = tmp_path / "gh.txt"
    assert pair(mod, md, out, "--max-games", "1", "--github-output", str(gh)) == 0
    s1 = trailing_json(capsys.readouterr().out)
    assert s1["games_postponed"] == [G2] and "game cap 1" in s1["postponed_reason"]
    paired = sorted(g for g in os.listdir(out / "closes") if g != "SEASON")
    assert paired == [G1], "the earliest kickoff is paired first"
    outputs = dict(line.split("=", 1) for line in gh.read_text().splitlines())
    assert outputs["status"] == "WROTE" and outputs["games_postponed"] == "1" and "index_written" in outputs
    first = batch_bytes(out, "closes", "clv")

    assert pair(mod, md, out, "--max-games", "1") == 0
    s2 = trailing_json(capsys.readouterr().out)
    assert s2["games_skipped_already_paired"] == [G1] and s2["games_postponed"] == []
    second = batch_bytes(out, "closes", "clv")
    assert all(second[k] == v for k, v in first.items() if v), "no byte of an existing close/CLV batch changed"
    assert sorted(g for g in os.listdir(out / "closes") if g != "SEASON") == [G1, G2]

    assert pair(mod, md, out) == 0
    s3 = trailing_json(capsys.readouterr().out)
    assert s3["written_closes"] == 0 and s3["written_clv"] == 0 and s3["games_skipped_already_paired"] == [G1, G2]
    assert batch_bytes(out, "closes", "clv") == second, "a second full run is a no-op on disk"


def test_a_game_whose_closes_exist_and_that_can_never_have_a_clv_is_not_restreamed(tmp_path, capsys):
    proot = str(tmp_path / "md" / "data" / "shadow" / "v2" / "projections")
    write_projection_file(proot, S1, "BOARD_V2", [proj(G1, S1, "BOARD_V2", 44, None), proj(G1, S1, "BOARD_V2", 46, None)])
    md = str(tmp_path / "md")
    mod = load_script("pair_closes_v2")
    out = tmp_path / "out"
    assert pair(mod, md, out) == 0
    s1 = trailing_json(capsys.readouterr().out)
    assert s1["written_closes"] == 2 and s1["written_clv"] == 0 and s1["games_skipped_already_paired"] == []
    assert pair(mod, md, out) == 0
    s2 = trailing_json(capsys.readouterr().out)
    assert s2["games_skipped_already_paired"] == [G1] and s2["written_closes"] == 0


def test_a_slate_of_closes_streamed_as_one_group_equals_one_game_at_a_time(tmp_path, capsys):
    md, _, _ = build_market_data(tmp_path)
    mod = load_script("pair_closes_v2")
    assert pair(mod, md, tmp_path / "grouped") == 0
    g = trailing_json(capsys.readouterr().out)
    assert pair(mod, md, tmp_path / "single", "--max-group-rows", "1") == 0
    s = trailing_json(capsys.readouterr().out)
    a, b = batch_bytes(tmp_path / "grouped", "closes", "clv"), batch_bytes(tmp_path / "single", "closes", "clv")
    assert a == b and len([k for k, v in a.items() if v]) >= 3
    assert (g["written_closes"], g["written_clv"], g["close_status"]) == (s["written_closes"], s["written_clv"], s["close_status"])


def test_the_close_step_publishes_its_outputs_before_the_season_pass(tmp_path, monkeypatch, capsys):
    md, _, _ = build_market_data(tmp_path)
    mod = load_script("pair_closes_v2")
    gh = tmp_path / "gh.txt"
    real = mod.iter_projections

    def die_in_the_season_pass(*a, **k):
        if k.get("line_filter") is not None:
            raise RuntimeError("killed in the season pass")
        return real(*a, **k)
    monkeypatch.setattr(mod, "iter_projections", die_in_the_season_pass)
    with pytest.raises(RuntimeError):
        pair(mod, md, tmp_path / "out", "--github-output", str(gh))
    out = dict(line.split("=", 1) for line in gh.read_text().splitlines())
    assert out["status"] == "WROTE" and int(out["written"]) > 0, "the games' evidence is announced even though the season pass never finished"
    assert glob.glob(str(tmp_path / "out" / "closes" / G1 / "*.jsonl.gz"))


# =============================================================================================== the workflow
def wf():
    return yaml.safe_load(open(WORKFLOW))


def steps_by_id():
    return {s["id"]: s for s in wf()["jobs"]["settle"]["steps"] if s.get("id")}


def names():
    return [s.get("name") for s in wf()["jobs"]["settle"]["steps"]]


def test_the_live_sunday_workflow_keeps_its_schedule_concurrency_and_permissions():
    doc = yaml.safe_load(open(WORKFLOW))
    triggers = doc.get("on") or doc.get(True)
    assert triggers["schedule"] == [{"cron": "49 */3 * * *"}] and "workflow_dispatch" in triggers
    assert doc["concurrency"] == {"group": "shadow-v2-settle", "cancel-in-progress": False}
    assert doc["permissions"] == {"contents": "write"}
    job = doc["jobs"]["settle"]
    assert job["timeout-minutes"] == 120, "the job limit is NOT the fix; the work is partitioned instead"
    assert job["if"] == "github.ref == 'refs/heads/main'"


def test_close_and_clv_evidence_runs_first_and_is_published_before_settlement_starts():
    n = names()
    closes = n.index("Pair every kicked-off projection with its canonical close and compute CLV")
    pub_closes = n.index("Publish the close and CLV batches and the projection index")
    settle_i = n.index("Settle every ready game and diagnose the data arm")
    pub_ev = n.index("Publish the settlement, close and CLV batches, autopsies and scorecard")
    scorecard = n.index("Rebuild the scorecard and exchange cross-check from the whole corpus")
    research = n.index("Rebuild the research export, scorecard v3, weekly report and health gate")
    assert closes < pub_closes < settle_i < pub_ev < scorecard < research
    by = steps_by_id()
    assert "publish_market_data.py" in by["publish_closes"]["run"] and "--src data/shadow/v2" in by["publish_closes"]["run"]
    assert "--sparse" not in by["publish_closes"]["run"] + by["publish_evidence"]["run"], "publish semantics unchanged"
    # settlement runs even if the closes step failed, and the closes are published even if that step was killed part-way
    assert "!cancelled()" in by["settle"]["if"] and "closes" not in by["settle"]["if"]
    cond = by["publish_closes"]["if"]
    assert "!cancelled()" in cond and "steps.closes.outcome == 'failure'" in cond and "steps.closes.outputs.status" in cond
    ev = by["publish_evidence"]["if"]
    assert "steps.settle.outcome == 'failure'" in ev and "steps.closes.outputs.status" in ev and "index_written" in ev
    assert "research" not in ev and "scorecard" not in ev, "no derived step can gate the evidence publish"


def test_every_evidence_driver_is_bounded_per_run_and_the_job_limit_still_holds():
    by = steps_by_id()
    for sid, driver in (("closes", "pair_closes_v2.py"), ("settle", "settle_v2.py")):
        run = by[sid]["run"]
        assert driver in run and "--max-games" in run and "--time-budget-minutes" in run, f"{sid} must bound its own work"
        assert "| tail" not in run and "tee" in run, "live logs"
    assert "--phase settle" in by["settle"]["run"], "the whole-corpus scorecard is not part of the evidence step"
    hard = sum(int(by[i]["timeout-minutes"]) for i in ("fetch", "closes", "publish_closes", "settle", "publish_evidence"))
    assert hard <= 120, f"hard limits of the evidence path sum to {hard} minutes"
    soft = lambda sid: int(__import__("re").search(r"--time-budget-minutes (\d+)", by[sid]["run"]).group(1))  # noqa: E731
    assert 15 + soft("closes") + 4 + soft("settle") + 4 + int(by["research"]["timeout-minutes"]) + 10 <= 120


def test_the_derived_steps_cannot_block_cancel_or_outlive_the_evidence():
    by = steps_by_id()
    for sid in ("scorecard", "research"):
        assert by[sid].get("continue-on-error") is True and "!cancelled()" in by[sid]["if"]
        assert "JOB_DEADLINE_EPOCH" in by[sid]["run"], f"{sid} is bounded by the job clock"
    assert 'timeout "${LEFT}s"' in by["scorecard"]["run"] and "--phase derived" in by["scorecard"]["run"]
    assert "--derived-min-interval-hours" in by["scorecard"]["run"]
    # the export is throttled by the scorecard step's verdict, except on a manual dispatch
    run = by["research"]["run"]
    assert "SKIPPED_UNCHANGED" in run and "workflow_dispatch" in run and "exit 0" in run
    assert by["publish_scorecard"]["if"].count("REBUILT") == 1
    clock = next(s for s in wf()["jobs"]["settle"]["steps"] if s.get("name") == "Start the job clock")
    assert "108 * 60" in clock["run"] and "GITHUB_ENV" in clock["run"]
    # all of them publish through the unchanged publisher
    for sid in ("publish_closes", "publish_evidence", "publish_scorecard", "research_publish"):
        assert "scripts/ci/publish_market_data.py --src data/shadow/v2" in by[sid]["run"]


def test_run_health_still_reads_every_step_it_always_read():
    by = steps_by_id()
    health = [s for s in wf()["jobs"]["settle"]["steps"] if s.get("name") == "Run health"][0]
    env = health["env"]
    assert env["SETTLE_STATUS"] == "${{ steps.settle.outputs.status }}" and env["CLOSES_STATUS"] == "${{ steps.closes.outputs.status }}"
    assert env["EVIDENCE_PUBLISH"] == "${{ steps.publish_evidence.outcome }}" and env["RESEARCH"] == "${{ steps.research.outcome }}"
    assert health["if"] == "always()" and "publish_closes" in by


# =============================================================================================== the autopsy's scans
def _book_with_players():
    from nfl_edge.settlement.results import PlayerGameResult, ResultBook
    book = ResultBook()
    n = 0
    for gid in ("2026_01_A_B", "2026_02_A_C", "2026_02_D_E"):
        for team in ("A", "B", "C", None):
            for k in range(4):
                n += 1
                book.add_player(PlayerGameResult(player_id=f"p{n}", game_id=gid, team=team, offense_snaps=None if k == 3 else 10.0 * k + n % 7,
                                                 has_stats_row=bool(k % 2), stats={"attempts": float(k * 3 % 5), "carries": float(k + 1)}))
    return book


def test_the_team_game_index_returns_exactly_what_the_full_scan_returned_in_the_same_order():
    from nfl_edge.settlement.team_game_index import team_game_items
    book = _book_with_players()
    for gid in ("2026_01_A_B", "2026_02_A_C", "2026_02_D_E", "2026_09_NONE"):
        for team in ("A", "B", "C", "Z", None):
            naive = [(pid, p) for (g, pid), p in book.players.items() if g == gid and p.team == team]
            assert team_game_items(book, gid, team) == naive
    # the autopsy helpers answer as the scans did
    from nfl_edge.engines.player import autopsy_v2 as AU
    for gid in ("2026_01_A_B", "2026_02_A_C"):
        for team in ("A", "B"):
            snaps = [p.offense_snaps for (g, _), p in book.players.items() if g == gid and p.team == team and p.offense_snaps is not None]
            assert AU._team_offense_snaps(book, gid, team) == (float(max(snaps)) if snaps else None)
            att = {pid: float(p.stats["attempts"]) for (g, pid), p in book.players.items() if g == gid and p.team == team and p.stats.get("attempts")}
            assert AU._team_attempts_by_passer(book, gid, team) == att


def test_the_team_game_index_sees_rows_added_after_it_was_built():
    from nfl_edge.settlement.results import PlayerGameResult
    from nfl_edge.settlement.team_game_index import team_game_items
    book = _book_with_players()
    before = len(team_game_items(book, "2026_01_A_B", "A"))
    book.add_player(PlayerGameResult(player_id="late", game_id="2026_01_A_B", team="A", has_stats_row=True))
    assert len(team_game_items(book, "2026_01_A_B", "A")) == before + 1
