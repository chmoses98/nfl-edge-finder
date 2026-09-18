"""The Shadow v2 postgame path is memory-bounded by the game being processed, not by the projection archive.

`Shadow v2 settlement & scorecard` run 35377140702 got past its fetch step and was then killed by the runner
after 17 minutes with no output: `settle_v2.py` began with `read_projections(roots)` over every projection file
ever published (1.5 million records of ~8 KB), and `pair_closes_v2.py` / `research_export_v2.py` did the same.
A local reproduction passed 12 GB before the first log line.

These tests pin the replacement architecture rather than only its outputs:

  * the store yields one record at a time from gzip and applies game / week filters before parsing;
  * a driver decides which games to work on from the schedule and the corpus, and opens only the files the
    projection index says hold those games -- never a file of a game that is already settled or paired;
  * sidecars are loaded only for the snapshots the autopsy references;
  * every probability-carrying record examined is accounted for and `silently_dropped` is zero;
  * and the streamed outputs equal what the whole-archive implementation produced on the same fixture.
"""
from __future__ import annotations

import glob
import gzip
import hashlib
import importlib
import importlib.util
import json
import os
import sys
import tracemalloc
from datetime import datetime, timedelta, timezone

import pytest
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.evaluation import scorecard_v2 as SC, scorecard_v3 as S3                 # noqa: E402
from nfl_edge.evaluation.research_slim import Interner, SLIM_FIELDS, slim              # noqa: E402
from nfl_edge.projection import store as PS                                             # noqa: E402
from nfl_edge.semantics import question_from_market                                      # noqa: E402
from nfl_edge.settlement import reachability as RE                                       # noqa: E402
from nfl_edge.settlement.results import result_book_from_records                         # noqa: E402
from nfl_edge.shadow import evaluation_store as ST                                       # noqa: E402

FIX = json.load(open(os.path.join(ROOT, "tests", "fixtures", "postgame", "dal_phi_2025_w1.results.json")))
G1, G2, G3 = "2026_01_ATL_PIT", "2026_02_DET_BUF", "2026_03_KC_LAC"
CODE = {G1: "26SEP13ATLPIT", G2: "26SEP17DETBUF", G3: "26SEP27KCLAC"}
KO = {G1: "2026-09-13T17:00:00+00:00", G2: "2026-09-18T00:15:00+00:00", G3: "2026-09-27T20:25:00+00:00"}
WEEK = {G1: 1, G2: 2, G3: 3}
NOW = "2026-09-20T12:00:00+00:00"
S1, S2, S3_, S4 = "20260912T150000Z", "20260913T120000Z", "20260917T200000Z", "20260918T100000Z"


# --------------------------------------------------------------------------------------------- fixtures
def load_script(name):
    path = os.path.join(ROOT, "scripts", "shadow_v2", f"{name}.py")
    spec = importlib.util.spec_from_file_location(f"_postgame_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def schedule_csv():
    header = FIX["schedule_csv"].splitlines()[0]
    h = header.split(",")

    def row(gid, wk, day, time_, hs, aws):
        r = {k: "" for k in h}
        r.update({"game_id": gid, "season": "2026", "game_type": "REG", "week": str(wk), "gameday": day, "gametime": time_,
                  "away_team": gid.split("_")[2], "home_team": gid.split("_")[3],
                  "away_score": "" if aws is None else str(aws), "home_score": "" if hs is None else str(hs),
                  "result": "" if hs is None else str(hs - aws), "total": "" if hs is None else str(hs + aws), "overtime": "0"})
        return ",".join(r[k] for k in h)
    return "\n".join([header, row(G1, 1, "2026-09-13", "13:00", 27, 20), row(G2, 2, "2026-09-17", "20:15", 41, 31),
                      row(G3, 3, "2026-09-27", "16:25", None, None)])


def result_book(*, g1_score=(27, 20)):
    csv = schedule_csv()
    if g1_score != (27, 20):
        lines = csv.splitlines()
        h = lines[0].split(",")
        out = [lines[0]]
        for line in lines[1:]:
            c = line.split(",")
            if c[0] == G1:
                c[h.index("home_score")], c[h.index("away_score")] = str(g1_score[0]), str(g1_score[1])
                c[h.index("result")], c[h.index("total")] = str(g1_score[0] - g1_score[1]), str(sum(g1_score))
            out.append(",".join(c))
        csv = "\n".join(out)
    return result_book_from_records({"schedule_csv": csv, "players": [], "snaps": [], "games_with_player_stats": [G1, G2],
                                     "games_with_snaps": [G1, G2]}, min_hours_after_kickoff=0)


def proj(gid, snapshot, arm, k, p, *, engine="GAME", family_ticker="KXNFLTOTAL", subject_kind=None, **extra):
    """A frozen projection of `TOTAL > k-0.5` for `gid`, or a season-market / keyless row when `gid` is None."""
    if gid:
        m = {"ticker": f"{family_ticker}-{CODE[gid]}-{k}", "event_ticker": f"{family_ticker}-{CODE[gid]}", "series_ticker": family_ticker,
             "strike_type": "greater", "floor_strike": k - 0.5, "title": ""}
        sem, q = question_from_market(m)
        base = {"question": q.to_dict(), "market_family": sem.family, "period": sem.period or "FULL", "game_id": gid,
                "semantic_confidence": q.semantic_confidence, "subject_id": q.subject, "stat_family": sem.stat,
                "ticker": m["ticker"], "event_ticker": m["event_ticker"], "series_ticker": m["series_ticker"],
                "season": 2026, "week": WEEK[gid], "kickoff_utc": KO[gid]}
    else:
        base = {"question": {"kind": "THRESHOLD", "op": ">=", "k": float(k)}, "market_family": extra.pop("market_family", "SEASON_WINS"),
                "period": "FULL", "game_id": None, "semantic_confidence": "PROVEN", "subject_id": extra.pop("subject_id", "ATL"),
                "stat_family": None, "ticker": f"KXNFLWINS-27-ATL-{k}", "event_ticker": "KXNFLWINS-27-ATL", "series_ticker": "KXNFLWINS",
                "season": extra.pop("season", 2026), "week": None, "kickoff_utc": None}
    mid = 0.5
    r = {**base, "snapshot_id": snapshot, "model_arm": arm, "engine": engine, "p_yes": p, "contract_value": p,
         "yes_bid": mid - 0.02, "yes_ask": mid + 0.02, "no_bid": 1 - mid - 0.02, "no_ask": 1 - mid + 0.02, "mid": mid, "quote_width": 0.04,
         "liquidity": 250.0, "volume": 100.0, "observed_at": snapshot[:4] + "-" + snapshot[4:6] + "-" + snapshot[6:8] + "T" + snapshot[9:11] + ":" + snapshot[11:13] + ":00+00:00",
         "generated_at": None, "horizon_label": "CYCLE", "minutes_to_kickoff": 300.0, "identity_confidence": "HIGH",
         "evidence_class": "PROSPECTIVE_FROZEN", "support_state": "PRICED" if p is not None else "CAPTURE_ONLY",
         "flags": {"has_probability": p is not None}, "subject_kind": subject_kind,
         "player_context": ({"player_context_id": f"pc-{snapshot}", "availability_state": "EXPECTED_ACTIVE", "injury_state": "NOT_LISTED"}
                            if subject_kind == "player" else {}),
         "feature_lineage": {}, "projection_lineage": {}, "distribution_summary": {}, "information_sync": {}}
    r.update(extra)
    r["record_id"] = hashlib.sha1(f"{snapshot}|{r['ticker']}|{arm}|{engine}".encode()).hexdigest()[:20]
    return r


def write_projection_file(root, snapshot, arm, rows):
    day = snapshot[:4] + "-" + snapshot[4:6] + "-" + snapshot[6:8]
    d = os.path.join(root, day)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, f"{snapshot}.{arm}.projections.jsonl.gz")
    with gzip.GzipFile(p, "wb", mtime=0) as raw:
        for r in rows:
            raw.write((json.dumps(r, separators=(",", ":"), sort_keys=True, default=str) + "\n").encode())
    json.dump({"status": "WRITTEN", "snapshot_id": snapshot, "model_arm": arm, "n_rows": len(rows)},
              open(p.replace(".projections.jsonl.gz", ".projections_manifest.json"), "w"))
    return p


def build_market_data(tmp_path, *, with_capture=True):
    """A market-data tree: four snapshots over three games, plus season / keyless / refusal rows and sidecars."""
    md = tmp_path / "md"
    proot = str(md / "data" / "shadow" / "v2" / "projections")
    files = {}
    # S1 (2026-09-12): G1 in BOARD_V2 and DATA_PLAYER_DIST; a season row; a keyless GAME row; a refusal; a G3 row
    files["S1.B"] = write_projection_file(proot, S1, "BOARD_V2",
                                          [proj(G1, S1, "BOARD_V2", k, 0.55 + 0.02 * i) for i, k in enumerate((44, 46, 48))]
                                          + [proj(None, S1, "BOARD_V2", 9, 0.4, engine="SEASON"),
                                             proj(None, S1, "BOARD_V2", 3, 0.3, engine="GAME", market_family="TOTAL", subject_id=None),
                                             proj(G1, S1, "BOARD_V2", 50, None),
                                             proj(G3, S1, "BOARD_V2", 40, 0.5)])
    files["S1.D"] = write_projection_file(proot, S1, "DATA_PLAYER_DIST",
                                          [proj(G1, S1, "DATA_PLAYER_DIST", k, 0.5, subject_kind="player", engine="GAME") for k in (44, 46)])
    # S2 (2026-09-13): G1 again, and G3
    files["S2.B"] = write_projection_file(proot, S2, "BOARD_V2",
                                          [proj(G1, S2, "BOARD_V2", k, 0.6) for k in (44, 46, 48)] + [proj(G3, S2, "BOARD_V2", 40, 0.5)])
    # S3 (2026-09-17): G2 in both arms, and G3
    files["S3.B"] = write_projection_file(proot, S3_, "BOARD_V2",
                                          [proj(G2, S3_, "BOARD_V2", k, 0.45 + 0.05 * i) for i, k in enumerate((70, 72, 74))] + [proj(G3, S3_, "BOARD_V2", 40, 0.5)])
    files["S3.D"] = write_projection_file(proot, S3_, "DATA_PLAYER_DIST",
                                          [proj(G2, S3_, "DATA_PLAYER_DIST", k, 0.5, subject_kind="player", engine="GAME") for k in (70, 72)])
    # S4 (2026-09-18): G3 only
    files["S4.B"] = write_projection_file(proot, S4, "BOARD_V2", [proj(G3, S4, "BOARD_V2", k, 0.5) for k in (40, 42)])
    for s in (S1, S2, S3_, S4):
        PS.write_sidecar(proot, s, {"lineage": {"snapshot": s}, "player_contexts": {f"pc-{s}": {"player_ewma": {"ewma_targets": 8.0, "ewma_receptions": 5.0}}},
                                   "game_contexts": {}})
    if with_capture:
        cap = md / "data" / "kalshi" / "capture"
        for gid in (G1, G2):
            ko = datetime.fromisoformat(KO[gid])
            for i, (mins, yb) in enumerate(((300, 0.45), (50, 0.50))):
                obs = ko - timedelta(minutes=mins)
                run = obs.strftime("%Y%m%dT%H%M%SZ")
                day = cap / obs.date().isoformat()
                day.mkdir(parents=True, exist_ok=True)
                with open(day / f"{run}.quotes.jsonl", "a") as f:
                    for k in (44, 46, 48, 70, 72, 74):
                        t = f"KXNFLTOTAL-{CODE[gid]}-{k}"
                        f.write(json.dumps({"run_id": run, "observed_at": obs.isoformat(), "ticker": t, "series_ticker": "KXNFLTOTAL", "game_id": gid,
                                            "kickoff_utc": KO[gid], "status": "active", "yes_bid_dollars": f"{yb:.4f}", "yes_ask_dollars": f"{yb + 0.04:.4f}",
                                            "no_bid_dollars": f"{1 - yb - 0.04:.4f}", "no_ask_dollars": f"{1 - yb:.4f}", "volume_fp": "10", "liquidity_dollars": "5"}) + "\n")
                json.dump({"run_id": run, "finished_at": obs.isoformat(), "partial": False,
                           "series": {"KXNFLTOTAL": {"complete": True, "observed_at": obs.isoformat()}}}, open(day / f"{run}.manifest.json", "w"))
    return str(md), proot, files


def trailing_json(text: str) -> dict:
    """The driver prints its summary as the last JSON block."""
    i = text.rfind("\n{\n")
    return json.loads(text[i + 1:])


class FakePeriodBook:
    def __init__(self):
        self.games = {}

    def load_pbp(self, *a, **k):
        return None


def run_settle(mod, monkeypatch, md, out, *extra, book=None):
    monkeypatch.setattr(mod, "build_result_book", lambda *a, **k: book or result_book())
    monkeypatch.setattr(mod, "PeriodBook", FakePeriodBook)
    return mod.main(["--market-data", md, "--out", str(out), "--target-season", "2026", "--now", NOW, *extra])


def spy_files(monkeypatch, mod):
    """Record which projection files each streaming call opened."""
    opened = []
    real = mod.iter_projections

    def wrapped(*a, **k):
        files = list(k.get("files") or [])
        k["files"] = files
        opened.append(files)
        return real(*a, **k)
    monkeypatch.setattr(mod, "iter_projections", wrapped)
    return opened


# --------------------------------------------------------------------------------------------- the store
def test_the_streaming_iterator_never_materialises_a_file(tmp_path, monkeypatch):
    md, proot, files = build_market_data(tmp_path, with_capture=False)
    monkeypatch.setattr(PS, "read_rows", lambda *a, **k: (_ for _ in ()).throw(AssertionError("read_rows() must not be used by the stream")))
    st = PS.ScanStats()
    seen = []
    for r in PS.iter_projections([proot], stats=st):
        seen.append(r["record_id"])
    assert len(seen) == st.rows_yielded == st.rows_read == st.rows_parsed == 21
    assert st.reconciles()
    # a big file streams with a small footprint: peak allocations stay near one row, far below the file
    big = tmp_path / "big"
    rows = [proj(G1, S1, "BOARD_V2", 44, 0.5, ticker_suffix=i, note="x" * 1500) for i in range(4000)]
    for i, r in enumerate(rows):
        r["record_id"] = f"rid{i:06d}"
    write_projection_file(str(big), S1, "BOARD_V2", rows)
    raw_bytes = sum(len(json.dumps(r)) for r in rows)
    tracemalloc.start()
    n = sum(1 for _ in PS.iter_projections([str(big)]))
    _cur, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert n == 4000
    assert peak < raw_bytes / 4, f"peak {peak} bytes for a {raw_bytes}-byte file: the stream is holding rows"


def test_game_id_filtering_happens_while_streaming_before_parsing(tmp_path, monkeypatch):
    md, proot, files = build_market_data(tmp_path, with_capture=False)
    parsed = []
    real_loads = json.loads
    monkeypatch.setattr(PS.json, "loads", lambda s: (parsed.append(1), real_loads(s))[1])
    st = PS.ScanStats()
    got = list(PS.iter_projections([proot], game_ids=[G2], stats=st))
    assert {r["game_id"] for r in got} == {G2} and len(got) == 5
    assert st.rows_read == 21 and st.rows_prefiltered_out >= 21 - 5, "rows of other games are rejected before json.loads"
    assert len(parsed) == st.rows_parsed <= 5 + 0, "only lines that can hold the game are parsed"
    assert st.reconciles()


def test_week_filtering_happens_while_streaming(tmp_path):
    md, proot, files = build_market_data(tmp_path, with_capture=False)
    st = PS.ScanStats()
    got = list(PS.iter_projections([proot], season=2026, week=2, stats=st))
    assert {(r["season"], r["week"]) for r in got} == {(2026, 2)} and len(got) == 5
    assert st.rows_parsed < st.rows_read, "week-1 and week-3 lines were rejected before parsing"
    assert st.rows_prefiltered_out + st.rows_filtered_out + st.rows_yielded == st.rows_read


def test_duplicate_record_ids_keep_the_first_occurrence_exactly_as_before(tmp_path):
    root = str(tmp_path / "p")
    a = proj(G1, S1, "BOARD_V2", 44, 0.5)
    b = dict(a, p_yes=0.9, contract_value=0.9)                  # same record_id, a later file claims a different number
    write_projection_file(root, S1, "BOARD_V2", [a])
    write_projection_file(root, S2, "BOARD_V2", [b, proj(G1, S2, "BOARD_V2", 46, 0.5)])
    st = PS.ScanStats()
    got = list(PS.iter_projections([root], stats=st))
    assert [r["p_yes"] for r in got] == [0.5, 0.5] and st.rows_duplicate == 1
    assert [r["record_id"] for r in got] == [r["record_id"] for r in PS.read_projections(root)]
    assert list(PS.iter_projections([root], dedupe=False)).__len__() == 3


def test_read_projections_is_the_stream_materialised(tmp_path):
    md, proot, files = build_market_data(tmp_path, with_capture=False)
    assert PS.read_projections(proot) == list(PS.iter_projections([proot]))
    assert PS.read_projections(proot, game_ids=[G1]) == list(PS.iter_projections([proot], game_ids=[G1]))


def test_the_index_names_the_files_that_hold_each_game_and_is_reused_by_hash(tmp_path):
    md, proot, files = build_market_data(tmp_path, with_capture=False)
    cache = str(tmp_path / "index")
    idx = PS.ProjectionIndex([proot], write_root=cache)
    assert idx.built == 6 and idx.written == 6 and idx.reused == 0
    assert sorted(os.path.basename(p) for p in idx.files_for_game(G2)) == sorted(os.path.basename(files[k]) for k in ("S3.B", "S3.D"))
    assert idx.game(G2)["n"] == 5 and idx.game(G2)["prob"] == 5 and idx.game(G2)["kickoff_utc"] == KO[G2] and idx.game(G2)["week"] == 2
    assert idx.game(G1)["prob"] == idx.game(G1)["n"] - 1, "the refusal is counted but carries no probability"
    assert idx.game(G1)["player_prob"] == 0 and idx.game(G2)["player_prob"] == 0
    assert [os.path.basename(p) for p in idx.files_with_no_game_rows(prob_only=True)] == [os.path.basename(files["S1.B"])]
    again = PS.ProjectionIndex([proot], index_roots=[cache])
    assert again.reused == 6 and again.built == 0
    # a rewritten file (different content, same name) is re-indexed rather than trusted
    write_projection_file(proot, S4, "BOARD_V2", [proj(G3, S4, "BOARD_V2", k, 0.5) for k in (40, 42, 44)])
    third = PS.ProjectionIndex([proot], index_roots=[cache])
    assert third.reused == 5 and third.built == 1 and third.game(G3)["n"] == 3 + 1 + 1 + 1


def test_the_sidecar_cache_loads_only_what_is_asked_for(tmp_path):
    md, proot, files = build_market_data(tmp_path, with_capture=False)
    c = PS.SidecarCache([proot], max_items=2)
    assert c.get(S1)["lineage"]["snapshot"] == S1 and c.get(S1) and c.loads == 1 and c.hits == 1
    assert c.get("20260101T000000Z") is None and c.misses == 1
    c.get(S2); c.get(S3_)
    assert c.loads == 3 and len(c._items) == 2, "a window of two snapshots"
    assert PS.read_sidecars(proot, snapshot_ids=[S4]).keys() == {S4}


# --------------------------------------------------------------------------------------------- the corpus
def test_the_planner_holds_ids_and_hashes_not_rows(tmp_path):
    corpus = ST.EvaluationCorpus(str(tmp_path / "c"), suffix="settlements_v2")
    rows = [{"prediction_id": f"p{i}", "evaluation_version": "v1", "settled_yes": 1.0, "big": "x" * 500} for i in range(50)]
    p = corpus.planner(G1)
    for r in rows:
        assert p.offer(r) == ST.NEW
    man = corpus.write_batch(G1, [], evaluation_version="v1", batch="B1", plan=p.plan())
    assert man["written"] == 50 and man["unchanged"] == 0
    p2 = corpus.planner(G1)
    assert all(isinstance(v, tuple) and len(v) == 2 and len(v[0]) == 20 for v in p2.existing.values()), "index entries are (hash, file)"
    for r in rows:
        assert p2.offer(dict(r, evaluated_at="later")) == ST.NOOP
    assert p2.counts() == {"new": 0, "unchanged": 50, "conflicts": 0, "repeated": 0, "existing": 50}
    assert corpus.write_batch(G1, [], evaluation_version="v1", batch="B2", plan=p2.plan())["status"] == "NO_OP"
    p3 = corpus.planner(G1)
    assert p3.offer(dict(rows[0], settled_yes=0.0)) == ST.CONFLICT and p3.conflicts[0]["fields"] == {"settled_yes": (1.0, 0.0)}
    assert corpus.has_batch(G1, "v1") and not corpus.has_batch(G1, "v2") and corpus.batch_versions(G1) == {"v1"}
    # the list API is unchanged for its callers
    plan = corpus.plan(rows[:3], G1)
    assert len(plan["noop"]) == 3 and plan["new"] == [] and plan["conflicts"] == []


# --------------------------------------------------------------------------------------------- settle_v2
def test_the_settle_driver_reads_only_the_files_of_the_games_it_settles_and_skips_settled_games(tmp_path, monkeypatch, capsys):
    md, proot, files = build_market_data(tmp_path, with_capture=False)
    mod = load_script("settle_v2")
    opened = spy_files(monkeypatch, mod)
    out = tmp_path / "out"
    assert run_settle(mod, monkeypatch, md, out) == 0
    s = trailing_json(capsys.readouterr().out)
    assert s["games_ready"] == [G1, G2] and s["games_skipped_already_settled"] == []
    assert s["games_not_final_with_projections"] == [G3]
    for call in opened:
        names = {os.path.basename(p) for p in call}
        assert not names & {os.path.basename(files["S4.B"])}, "S4 holds only the unfinished game and must never be opened"
    g2_calls = [c for c in opened if {os.path.basename(p) for p in c} == {os.path.basename(files["S3.B"]), os.path.basename(files["S3.D"])}]
    assert len(g2_calls) == 1, "one settlement pass over exactly the two files that hold DET @ BUF, and no second pass"
    assert [g for g in s["per_game"] if g["game_id"] == G2][0]["needs_player_tables"] is False, "no PLAYER-engine row: the index says so without a probe"
    assert s["accounting"]["silently_dropped"] == 0
    # second run: both games are settled; their files are not opened again, and nothing is written
    del opened[:]
    before = sorted(glob.glob(str(out / "**" / "*"), recursive=True))
    assert run_settle(mod, monkeypatch, md, out) == 0
    s2 = trailing_json(capsys.readouterr().out)
    assert s2["games_skipped_already_settled"] == [G1, G2] and s2["games_ready"] == [] and s2["written"] == 0
    for call in opened:
        assert not ({os.path.basename(p) for p in call} & {os.path.basename(files[k]) for k in ("S1.D", "S2.B", "S3.B", "S3.D")}), \
            "a settled game's files are never re-read"
    assert sorted(glob.glob(str(out / "**" / "*"), recursive=True)) == before
    assert s2["accounting"]["silently_dropped"] == 0 and s2["dispatch"]["season_scoped"] == 1, "season rows are still examined every run"
    # a forced game is examined even though its batch exists, and is a no-op
    assert run_settle(mod, monkeypatch, md, out, "--game", G1) == 0
    s3 = trailing_json(capsys.readouterr().out)
    assert s3["games_ready"] == [G1] and s3["written"] == 0 and s3["per_game"][0]["settlement"]["unchanged"] == 8


def test_a_game_with_many_files_reads_only_the_files_that_hold_it(tmp_path, monkeypatch, capsys):
    proot = str(tmp_path / "md" / "data" / "shadow" / "v2" / "projections")
    held = set()
    for i in range(24):
        snap = f"202609{10 + i // 6:02d}T{(i % 6) * 4:02d}0000Z"
        gid = G1 if i % 8 == 0 else G3
        p = write_projection_file(proot, snap, "BOARD_V2", [proj(gid, snap, "BOARD_V2", 44 + 2 * j, 0.5) for j in range(3)])
        if gid == G1:
            held.add(os.path.basename(p))
    assert len(held) == 3
    mod = load_script("settle_v2")
    opened = spy_files(monkeypatch, mod)
    assert run_settle(mod, monkeypatch, str(tmp_path / "md"), tmp_path / "out") == 0
    s = trailing_json(capsys.readouterr().out)
    assert s["games_ready"] == [G1]
    g1_calls = [c for c in opened if c]
    assert all({os.path.basename(p) for p in c} == held for c in g1_calls), f"opened {[[os.path.basename(p) for p in c] for c in opened]}"
    assert s["accounting"]["projection_scan"]["files_scanned"] == 3
    assert s["index"]["files"] == 24


def test_sidecars_are_loaded_only_for_snapshots_the_autopsy_references(tmp_path, monkeypatch, capsys):
    md, proot, files = build_market_data(tmp_path, with_capture=False)
    mod = load_script("settle_v2")
    assert run_settle(mod, monkeypatch, md, tmp_path / "out") == 0
    s = trailing_json(capsys.readouterr().out)
    # DATA_PLAYER_DIST rows live in S1 and S3 only; S2 and S4 sidecars exist and must never be decompressed
    assert s["sidecars"]["sidecar_loads"] == 2 and s["sidecars"]["sidecar_missing"] == 0
    au = ST.read_corpus([str(tmp_path / "out" / "autopsy")], suffix="autopsy_v2")
    assert len(au) == 4 and {r["snapshot_id"] for r in au} == {S1, S3_}


def test_every_probability_row_examined_is_accounted_for(tmp_path, monkeypatch, capsys):
    md, proot, files = build_market_data(tmp_path, with_capture=False)
    mod = load_script("settle_v2")
    assert run_settle(mod, monkeypatch, md, tmp_path / "out") == 0
    s = trailing_json(capsys.readouterr().out)
    a = s["accounting"]
    # G1: 3+2+3 = 8 game rows; G2: 3+2 = 5; season: 1; keyless GAME row: 1 unreachable. The refusal is not examined.
    assert a["game_scoped_dispatched"] == 13 and a["season_scoped_dispatched"] == 1 and a["unreachable"] == 1
    assert a["probability_rows_examined"] == 15 and a["silently_dropped"] == 0
    assert a["rows_without_probability_not_examined"] == 1
    assert a["scan_reconciles"] is True
    assert s["dispatch"]["unreachable_detail"][0]["reachability"]["state"] == RE.MISSING_KEYS
    assert s["dispatch"]["unreachable_detail"][0]["reachability"]["missing"] == ["game_id"]
    assert a["season_pass_game_rows_deferred_to_game_passes"] == 4, "S1.B's four probability game rows met in the season pass belong to their game passes"


def test_the_streamed_settlement_equals_the_whole_archive_implementation(tmp_path, monkeypatch, capsys):
    """The oracle is the first version's loop, run in-test over read_projections(): same rows, same statuses,
    same scorecard, from a driver that never held the archive."""
    md, proot, files = build_market_data(tmp_path, with_capture=False)
    mod = load_script("settle_v2")
    out = tmp_path / "out"
    assert run_settle(mod, monkeypatch, md, out) == 0
    capsys.readouterr()
    book, now = result_book(), datetime.fromisoformat(NOW)
    from nfl_edge.settlement import season_settlement as SS, settle_v2 as S2
    ledgers = {s: SS.SeasonLedger(book.games, s) for s in sorted({g.season for g in book.games.values() if g.season})}
    expected = {}
    for r in PS.read_projections(proot):
        if r.get("p_yes") is None:
            continue
        rr = RE.reachability(r)
        if rr["state"] != RE.DISPATCHABLE:
            continue
        if rr["scope"] == RE.SEASON:
            row = mod.settlement_row(r, S2.settle_projection(r, book, None, season_ledger=ledgers), now, season_scope=True)
        elif book.readiness(r["game_id"], needs_player_stats=False, now=now)[0] == "READY":
            row = mod.settlement_row(r, S2.settle_projection(r, book, FakePeriodBook(), season_ledger=ledgers), now)
        else:
            continue
        expected[row["prediction_id"]] = {k: v for k, v in row.items() if k != "evaluated_at"}
    got = {r["prediction_id"]: {k: v for k, v in r.items() if k not in ("evaluated_at", "evaluation_id", "content_hash")}
           for r in ST.read_corpus([str(out / "settlements")], suffix="settlements_v2")}
    assert got == expected
    old_sc = SC.build_scorecard(list(got.values()))
    new_sc = json.load(open(out / "scorecards" / "scorecard_v2.json"))
    _approx_equal(new_sc, old_sc)


def _approx_equal(a, b, path=""):
    if isinstance(a, dict):
        assert isinstance(b, dict) and set(a) == set(b), (path, set(a) ^ set(b) if isinstance(b, dict) else b)
        for k in a:
            _approx_equal(a[k], b[k], f"{path}/{k}")
    elif isinstance(a, list):
        assert isinstance(b, list) and len(a) == len(b), (path, a, b)
        for i, (x, y) in enumerate(zip(a, b)):
            _approx_equal(x, y, f"{path}[{i}]")
    elif isinstance(a, float) or isinstance(b, float):
        assert a == pytest.approx(b, rel=1e-9, abs=1e-12), (path, a, b)
    else:
        assert a == b, (path, a, b)


def test_the_scorecard_accumulator_matches_build_scorecard_including_paired_arms():
    import random
    random.seed(11)
    rows = []
    for g in range(5):
        for s in range(3):
            for t in range(8):
                for arm in ("A", "B", "C"):
                    if random.random() < 0.1:
                        continue
                    cv = random.random(); y = float(random.random() < cv)
                    rows.append({"game_id": f"G{g}", "snapshot_id": f"s{s}", "ticker": f"T{g}-{t}", "model_arm": arm, "engine": "GAME" if t % 2 else "PLAYER",
                                 "stat_family": None if t % 2 else "rec", "market_family": "TOTAL", "contract_value": cv,
                                 "settled_yes": None if random.random() < 0.2 else y, "mid": None if random.random() < 0.1 else cv * 0.9 + 0.05,
                                 "yes_ask": 0.5, "no_ask": 0.5, "evidence_class": random.choice(["PROSPECTIVE_FROZEN", "HISTORICAL_RESEARCH"]),
                                 "period": "FULL", "horizon_label": "CYCLE", "liquidity": random.choice([None, 50, 5000]), "quote_width": 0.03,
                                 "settlement_kind": random.choice(["binary", "tie_split"])})
    acc = SC.ScorecardAccumulator()
    for r in rows:
        acc.add(r)
    _approx_equal(acc.finish(), SC.build_scorecard(rows))
    # an arm that appears only in the LAST game invalidates every earlier fold; the reread callback repairs it exactly
    late = [dict(r, model_arm="D") for r in rows if r["game_id"] == "G4"]
    rows2 = rows + late
    by_game = {}
    for r in rows2:
        by_game.setdefault(r["game_id"], []).append(r)
    acc2 = SC.ScorecardAccumulator()
    for g in sorted(by_game):
        for r in by_game[g]:
            acc2.add(r, game=g)
        acc2.end_game()
    with pytest.raises(RuntimeError):
        SC.ScorecardAccumulator.finish(_copy_acc(acc2))
    _approx_equal(acc2.finish(reread=lambda g: iter(by_game[g])), SC.build_scorecard(rows2))


def _copy_acc(acc):
    import copy
    return copy.deepcopy(acc)


def test_a_rerun_with_contradicting_evidence_fails_with_a_conflict_and_writes_nothing(tmp_path, monkeypatch, capsys):
    md, proot, files = build_market_data(tmp_path, with_capture=False)
    mod = load_script("settle_v2")
    out = tmp_path / "out"
    assert run_settle(mod, monkeypatch, md, out) == 0
    before = {p: hashlib.sha256(open(p, "rb").read()).hexdigest() for p in glob.glob(str(out / "settlements" / "**" / "*"), recursive=True) if os.path.isfile(p)}
    with pytest.raises(ST.EvaluationConflict):
        run_settle(mod, monkeypatch, md, out, "--game", G1, book=result_book(g1_score=(20, 27)))
    after = {p: hashlib.sha256(open(p, "rb").read()).hexdigest() for p in glob.glob(str(out / "settlements" / "**" / "*"), recursive=True) if os.path.isfile(p)}
    assert after == before


# --------------------------------------------------------------------------------------------- pair_closes_v2
def test_pair_closes_processes_only_kicked_off_unpaired_games_and_reads_only_their_files(tmp_path, monkeypatch, capsys):
    md, proot, files = build_market_data(tmp_path)
    mod = load_script("pair_closes_v2")
    opened = spy_files(monkeypatch, mod)
    out = tmp_path / "out"
    assert mod.main(["--market-data", md, "--out", str(out), "--now", NOW]) == 0
    s = trailing_json(capsys.readouterr().out)
    assert s["games_skipped_not_kicked_off"] == [G3] and s["games_skipped_already_paired"] == []
    assert s["written_closes"] == 9 + 5 + 1 and s["written_clv"] == 8 + 5, "every row of G1 and G2 has a close; probability rows a CLV; the season row its explicit record"
    assert s["close_status"]["CLOSE_NOT_APPLICABLE_SEASON"] == 1 and s["close_status"]["CLOSE_OK"] == 13
    assert s["close_status"]["CLV_CLOSE_MISSING"] == 1, "the refused k=50 contract was never quoted: its close is missing, with a reason, not invented"
    assert s["rows_no_game_not_season"] == 1, "the keyless GAME row has no close question and is reported, not dropped"
    for call in opened:
        assert not ({os.path.basename(p) for p in call} & {os.path.basename(files["S4.B"])}), "the unfinished game's only file is never opened"
    closes = ST.read_corpus([str(out / "closes")], suffix="closes_v2")
    assert {r["close_status"] for r in closes if r.get("game_id")} == {"CLOSE_OK", "CLV_CLOSE_MISSING"}
    season = [r for r in closes if r["close_status"] == "CLOSE_NOT_APPLICABLE_SEASON"]
    assert len(season) == 1 and season[0]["game_id"] is None and season[0]["flags"] == ["SEASON_SCOPED"]
    clv = ST.read_corpus([str(out / "clv")], suffix="clv_v2")
    assert len(clv) == 13 and {r["game_id"] for r in clv} == {G1, G2}
    from nfl_edge.evaluation import clv as CV
    assert s["sign_convention"] == CV.SIGN_CONVENTION
    # rerun: both games are paired; their files are not re-read; nothing is written
    del opened[:]
    assert mod.main(["--market-data", md, "--out", str(out), "--now", NOW]) == 0
    s2 = trailing_json(capsys.readouterr().out)
    assert s2["games_skipped_already_paired"] == [G1, G2] and s2["written_closes"] == 0 and s2["written_clv"] == 0
    assert all(not ({os.path.basename(p) for p in c} & {os.path.basename(files[k]) for k in ("S1.D", "S2.B", "S3.B", "S3.D")}) for c in opened)
    assert s2["season_rows_not_applicable_plan"]["unchanged"] == 1


def test_pair_closes_equals_the_whole_archive_implementation(tmp_path, monkeypatch, capsys):
    md, proot, files = build_market_data(tmp_path)
    mod = load_script("pair_closes_v2")
    out = tmp_path / "out"
    assert mod.main(["--market-data", md, "--out", str(out), "--now", NOW]) == 0
    capsys.readouterr()
    from nfl_edge.evaluation import clv as CV, close as CL, openset as OS
    from nfl_edge.execution.fees import load_fee_schedule
    now = datetime.fromisoformat(NOW)
    cap = os.path.join(md, "data", "kalshi", "capture")
    runs, oset = CL.CaptureRuns(cap), OS.OpenSetLedger(cap)
    oset = oset if oset.runs else None
    sched = load_fee_schedule(ROOT)
    exp_close, exp_clv = {}, {}
    by_game = {}
    for r in PS.read_projections(proot):
        if r.get("game_id") and r.get("kickoff_utc"):
            by_game.setdefault(r["game_id"], []).append(r)
        elif RE.scope_of(r.get("market_family"), r.get("engine")) == RE.SEASON:
            exp_close[r["record_id"]] = mod.not_applicable_row(r, now)
    for gid, recs in by_game.items():
        ko = datetime.fromisoformat(recs[0]["kickoff_utc"])
        if now < ko:
            continue
        idx = CL.CloseIndex(cap, gid, ko.isoformat(), runs=runs, days_back=14, openset=oset)
        for r in recs:
            c = idx.select(r["ticker"], series_ticker=r.get("series_ticker"), projection_kickoff_utc=r.get("kickoff_utc"))
            exp_close[r["record_id"]] = {"prediction_id": r["record_id"], "evaluation_version": CL.CLOSE_RULE_VERSION, "evaluated_at": now.isoformat(),
                                         "record_id": r["record_id"], "snapshot_id": r.get("snapshot_id"), "model_arm": r.get("model_arm"), "horizon_label": r.get("horizon_label"), **c}
            if r.get("p_yes") is not None:
                v = CV.clv_record(r, c, schedule=sched, as_of=datetime.fromisoformat(r["observed_at"]))
                exp_clv[r["record_id"]] = {"prediction_id": r["record_id"], "evaluation_version": CV.CLV_VERSION, "evaluated_at": now.isoformat(), "game_id": gid,
                                           "snapshot_id": r.get("snapshot_id"), **v}
    strip = lambda rows: {r["prediction_id"]: {k: v for k, v in r.items() if k not in ("evaluated_at", "evaluation_id", "content_hash")} for r in rows}
    assert strip(ST.read_corpus([str(out / "closes")], suffix="closes_v2")) == strip(exp_close.values())
    assert strip(ST.read_corpus([str(out / "clv")], suffix="clv_v2")) == strip(exp_clv.values())


# --------------------------------------------------------------------------------------------- research_export_v2
def _run_all(tmp_path, monkeypatch, capsys):
    md, proot, files = build_market_data(tmp_path)
    out = tmp_path / "out"
    settle = load_script("settle_v2")
    assert run_settle(settle, monkeypatch, md, out) == 0
    closes = load_script("pair_closes_v2")
    assert closes.main(["--market-data", md, "--out", str(out), "--now", NOW]) == 0
    capsys.readouterr()
    return md, proot, files, out


def test_research_export_for_week_2_never_loads_week_1_rows(tmp_path, monkeypatch, capsys):
    md, proot, files, out = _run_all(tmp_path, monkeypatch, capsys)
    mod = load_script("research_export_v2")
    opened = spy_files(monkeypatch, mod)
    research = out / "research"
    assert mod.main(["--market-data", md, "--staging", str(out), "--out", str(research), "--season", "2026", "--week", "2"]) == 0
    capsys.readouterr()
    cov = json.load(open(research / "2026_wk02.export_summary.json"))
    assert cov["rows"] == 5 and cov["scope"]["units"] == 1 and cov["scope"]["per_unit"][0]["unit"] == G2
    scan = cov["scope"]["projection_scan"]
    assert scan["files_scanned"] == 2 and scan["rows_parsed"] == 5 and scan["rows_yielded"] == 5, "only S3's two files, only DET @ BUF's lines"
    for call in opened:
        assert {os.path.basename(p) for p in call} <= {os.path.basename(files["S3.B"]), os.path.basename(files["S3.D"])}
    rows = [json.loads(l) for l in gzip.open(research / "2026_wk02.research.jsonl.gz", "rt") if l.strip()]
    assert {r["game_id"] for r in rows} == {G2} and {r["week"] for r in rows} == {2}
    assert all(r["settled_yes"] is not None for r in rows) and all(r["close_status"] == "CLOSE_OK" for r in rows)
    assert cov["settled"] == 5 and cov["close_paired"] == 5
    assert cov["clv_ok"] == 2 and sum(1 for r in rows if r["clv_status"] == "NO_VIEW") == 3, "three rows priced exactly at the mid carry no view"


def test_research_export_equals_the_whole_archive_implementation(tmp_path, monkeypatch, capsys):
    md, proot, files, out = _run_all(tmp_path, monkeypatch, capsys)
    mod = load_script("research_export_v2")
    research = out / "research"
    assert mod.main(["--market-data", md, "--staging", str(out), "--out", str(research), "--season", "2026", "--week", "1"]) == 0
    assert mod.main(["--market-data", md, "--staging", str(out), "--out", str(research), "--season", "2026", "--week", "0"]) == 0
    capsys.readouterr()
    from nfl_edge.evaluation import execution_depth as XD
    mdv2 = os.path.join(md, "data", "shadow", "v2")
    staging = str(out)
    ci = lambda name, suffix: mod.corpus_index(os.path.join(staging, name), os.path.join(mdv2, name), suffix)
    joins = (ci("closes", "closes_v2"), ci("clv", "clv_v2"), ci("settlements", "settlements_v2"), ci("autopsy", "autopsy_v2"), ci("crosscheck", "crosscheck_v2"))
    sidecars = PS.read_sidecars(proot)
    for week, label in ((1, "2026_wk01"), (0, "2026_all")):
        projections = PS.read_projections(proot)
        if week:
            projections = [p for p in projections if p.get("week") == week and p.get("season") == 2026]
        expected = mod.build_rows(projections, sidecars, *joins, XD.DepthIndex([os.path.join(mdv2, "depth"), os.path.join(staging, "depth")]))
        got = [json.loads(l) for l in gzip.open(research / f"{label}.research.jsonl.gz", "rt") if l.strip()]
        assert got == expected, label
        old_sc = S3.build(expected)
        new_sc = json.load(open(research / f"{label}.scorecard_v3.json"))
        _approx_equal(new_sc, old_sc)
        old_exec = mod.execution_research(expected)
        new_exec = json.load(gzip.open(research / f"{label}.execution_sizes.json.gz", "rt"))
        assert new_exec == old_exec
    all_rows = [json.loads(l) for l in gzip.open(research / "2026_all.research.jsonl.gz", "rt") if l.strip()]
    assert len(all_rows) == 21 and sum(1 for r in all_rows if r["game_id"] is None) == 2, "an explicit all-weeks rebuild keeps the season-market rows"
    try:                                                  # optional: the suite's requirements do not carry pyarrow; the workflow installs it
        pq = importlib.import_module("pyarrow.parquet")
    except ImportError:
        pq = None
    if pq is not None:
        t = pq.read_table(research / "2026_all.research.parquet")
        assert t.num_rows == 21 and "record_id" in t.column_names and "player_context_id" in t.column_names
        summary = json.load(open(research / "2026_all.export_summary.json"))
        assert summary["files"]["parquet_info"]["rows"] == 21


def test_slim_rows_give_the_same_scorecard_and_health_as_full_rows(tmp_path, monkeypatch, capsys):
    md, proot, files, out = _run_all(tmp_path, monkeypatch, capsys)
    mod = load_script("research_export_v2")
    research = out / "research"
    assert mod.main(["--market-data", md, "--staging", str(out), "--out", str(research), "--season", "2026", "--week", "0"]) == 0
    capsys.readouterr()
    full = [json.loads(l) for l in gzip.open(research / "2026_all.research.jsonl.gz", "rt") if l.strip()]
    intern = Interner()
    slims = [slim(r, intern) for r in full]
    assert S3.build(slims) == S3.build(full)
    report = load_script("weekly_report_v2")
    assert report.health(slims, [], [], 2026, 0) == report.health(full, [], [], 2026, 0)
    def body(rows):
        text = report.render(S3.build(rows), report.health(rows, [], [], 2026, 0), rows, "x")
        return [line for line in text.splitlines() if not line.startswith("report ")]      # the wall-clock line
    assert body(slims) == body(full)
    assert set(S3.SEGMENTS) <= set(SLIM_FIELDS)
    assert report.main(["--market-data", md, "--research", str(research), "--out", str(out / "reports"), "--season", "2026", "--week", "1"]) == 0
    assert os.path.exists(out / "reports" / "2026_wk01.WEEKLY_REPORT.md") and os.path.exists(out / "reports" / "2026_wk01.health.json")


# --------------------------------------------------------------------------------------------- memory
def test_settling_one_game_costs_a_fraction_of_materialising_the_archive(tmp_path, monkeypatch, capsys):
    """Three games of 3,000 rows each, one of them final. The driver's peak Python allocation must be well under
    what read_projections() needs for the archive, and must not grow with the two games it does not settle."""
    md = tmp_path / "md"
    proot = str(md / "data" / "shadow" / "v2" / "projections")
    for gid, snap in ((G1, S1), (G3, S2), (G3, S3_)):
        rows = [proj(gid, snap, "BOARD_V2", 44, 0.5, pad="p" * 800) for _ in range(3000)]
        for i, r in enumerate(rows):
            r["ticker"] = f"KXNFLTOTAL-{CODE[gid]}-{i}"; r["record_id"] = f"{snap}-{i:05d}"
        write_projection_file(proot, snap, "BOARD_V2", rows)
    tracemalloc.start()
    archive = PS.read_projections(proot)
    _c, materialised = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert len(archive) == 9000
    del archive
    mod = load_script("settle_v2")
    tracemalloc.start()
    assert run_settle(mod, monkeypatch, str(md), tmp_path / "out") == 0
    _c, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    s = trailing_json(capsys.readouterr().out)
    assert s["games_ready"] == [G1] and s["accounting"]["game_scoped_dispatched"] == 3000
    assert peak < materialised / 2, f"settle peak {peak / 2**20:.1f} MB vs archive materialised {materialised / 2**20:.1f} MB"


# --------------------------------------------------------------------------------------------- the workflow
def test_the_settle_workflow_keeps_live_logs_and_publishes_the_index():
    doc = yaml.safe_load(open(os.path.join(ROOT, ".github", "workflows", "shadow-v2-settle.yml")))
    steps = {s.get("name"): s for s in doc["jobs"]["settle"]["steps"]}
    for name in ("Settle every ready game, diagnose, rebuild the scorecard",
                 "Pair every kicked-off projection with its canonical close and compute CLV",
                 "Rebuild the research export, scorecard v3, weekly report and health gate"):
        run = steps[name]["run"]
        assert "| tail" not in run, f"{name!r} still hides its output until exit"
        assert "tee" in run and "$RUNNER_TEMP" in run
    assert "Show where a failed driver died" in steps
    assert "index_written" in steps["Publish the settlement, close and CLV batches, autopsies, scorecard, research export and report"]["if"]
    assert doc["jobs"]["settle"]["timeout-minutes"] >= 60


def test_the_index_counts_exactly_the_rows_the_readiness_probe_would_have_found(tmp_path):
    """needs_player_tables() is the settlement driver's old probe predicate, so readiness never changes."""
    root = str(tmp_path / "p")
    rows = [proj(G1, S1, "BOARD_V2", 44, 0.5),                                       # GAME engine: no
            proj(G1, S1, "BOARD_V2", 46, 0.5, engine="PLAYER", subject_id="00-0001"),  # PLAYER, dispatchable: yes
            proj(G1, S1, "BOARD_V2", 48, None, engine="PLAYER"),                      # no probability: no
            proj(G1, S1, "BOARD_V2", 50, 0.5, engine="PLAYER", subject_id=None),      # PLAYER scope without a subject: unreachable, no
            proj(G1, S1, "BOARD_V2", 52, 0.5, engine="PLAYER", market_family="SEASON_WINS")]   # season family: season scope, no
    write_projection_file(root, S1, "BOARD_V2", rows)
    idx = PS.ProjectionIndex([root])
    probe = sum(1 for r in PS.iter_projections([root], game_ids=[G1], has_probability=True)
                if (rr := RE.reachability(r))["state"] == RE.DISPATCHABLE and rr["scope"] != RE.SEASON and r.get("engine") == "PLAYER")
    assert idx.game(G1)["player_prob"] == probe == 1
