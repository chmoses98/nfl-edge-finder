#!/usr/bin/env python3
"""Rebuild the deterministic RESEARCH TABLE (one row per frozen projection, joined by record_id to close, CLV,
settlement, context and autopsy) and the scorecard v3 from the immutable corpora. Derived; rebuildable; never
writes into the corpora.

    python3 scripts/shadow_v2/research_export_v2.py --market-data /tmp/md [--projections <root>]* --out data/shadow/v2/research --season 2026 [--week 1]

MEMORY SCALES WITH THE WEEK. `--season` / `--week` select games from the projection index and are pushed into
the streaming reader, so the weekly run never opens a file that holds no row of the week and never materialises
another week's rows. Each game is then processed on its own: its evaluation corpora (close, CLV, settlement,
autopsy, cross-check) are indexed for that game only, its projections are streamed from exactly the files that
hold them, every research row is serialised as soon as it is built, and only a fixed-slot summary of each row
(nfl_edge/evaluation/research_slim.py) is kept for the week-level scorecard, health and coverage blocks. The
derived tables (execution sizes, availability events, coverage audits) are accumulated, not listed.

`--week 0` is an explicit rebuild over every week present, including the season-market rows that carry no
week; it is bounded by one game at a time plus the slim rows of the whole export, and is not what the scheduled
workflow runs.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import resource
import sys
import tempfile
import time
from array import array
from collections import Counter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.evaluation import availability_events as AE                            # noqa: E402
from nfl_edge.evaluation import coverage as CV                                       # noqa: E402
from nfl_edge.evaluation import execution_depth as XD                                # noqa: E402
from nfl_edge.evaluation import research_record as RR, scorecard_v3 as S3            # noqa: E402
from nfl_edge.evaluation import research_parts as RP                                 # noqa: E402
from nfl_edge.evaluation.research_slim import Interner, slim                         # noqa: E402
from nfl_edge.projection.store import INDEX_DIRNAME, ProjectionIndex, ScanStats, SidecarCache, iter_projections  # noqa: E402
from nfl_edge.research import hypothesis_registry_v2 as HR                            # noqa: E402
from nfl_edge.settlement import crosscheck as XC                                      # noqa: E402
from nfl_edge.settlement import settle_v2 as S2                                        # noqa: E402
from nfl_edge.shadow import evaluation_store as ST                                    # noqa: E402

NO_GAME = ""                                     # the unit that holds season-market rows (no game_id)
# what ExecutionResearchAccumulator reads off a research row; kept per row until the game's rows are sorted
EXEC_SOURCE_FIELDS = ("depth", "record_id", "ticker", "model_arm", "market_family", "game_id", "horizon_label",
                      "contract_value", "h_mid", "h_yes_ask", "h_no_ask", "disagreement_band")


def log(*a):
    print(*a, flush=True)


def _rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def _median(vals):
    vals = sorted(v for v in vals if v is not None)
    return None if not vals else vals[len(vals) // 2]


def corpus_index(root_local: str, root_md: str, suffix: str, game_id: str | None = None, rank=None) -> dict:
    """One evaluation per prediction, chosen deterministically when a prediction has more than one.

    The corpus is keyed by (prediction_id, evaluation_version) precisely because a prediction can be evaluated
    again under a newer rule, and both readings are kept. Indexing by prediction alone let dict insertion order
    decide which one the research table showed -- so a rebuild could silently change a published row without a
    single byte of evidence changing. The highest evaluation_version wins, and the choice is recorded on the row
    (`evaluation_version_*`) so a reader can see which reading they are looking at.

    `rank` overrides that ordering for a corpus whose versions are not a single ascending rule. Two are: the
    exchange cross-check (nfl_edge/settlement/crosscheck.py) and the season-scoped settlements
    (`S2.season_rank`). Both file evidence TIERS rather than successive rules, so a terminal verdict outranks
    every provisional observation of the same prediction no matter which was written first -- and plain string
    ordering would do the opposite, since `settle-2.0.0+provisional.<vintage>` sorts above `settle-2.0.0`.

    `game_id` scopes the read to one game directory (a `*` suffix, e.g. "SEASON*", to a directory family), so
    the export holds one game's evaluations at a time rather than the whole corpus.
    """
    c = ST.EvaluationCorpus(root_local, read_roots=[root_md], suffix=suffix)
    key = rank or (lambda row: str(row.get("evaluation_version")))
    out: dict = {}
    for row, _f in c.iter_rows(game_id):
        pid, k = row.get("prediction_id"), key(row)
        cur = out.get(pid)
        if cur is None or k > cur[0]:
            out[pid] = (k, row)
    return {pid: row for pid, (_k, row) in out.items()}


def build_rows(projections: list, sidecars: dict, closes: dict, clvs: dict, settlements: dict, autopsies: dict,
               crosschecks: dict | None = None, depth_index: "XD.DepthIndex | None" = None) -> list:
    """One research row per frozen projection.

    The dedicated depth sweep is joined HERE and nowhere else. Its rows are not aligned to any projection -- the
    sweep has its own cadence -- so the join is a selection under the two rules in `DepthIndex.pair`, and it
    happens in the derived export so that a frozen projection record is never mutated by evidence that arrived
    after it was written. A record with no qualifying observation keeps a named reason, not a silent null.
    """
    get = sidecars.get if hasattr(sidecars, "get") else (lambda _s: None)
    out = [research_row(p, get(p.get("snapshot_id")), closes, clvs, settlements, autopsies, crosschecks, depth_index)
           for p in projections]
    out.sort(key=sort_key)
    return out


def research_row(p: dict, sidecar, closes: dict, clvs: dict, settlements: dict, autopsies: dict, crosschecks, depth_index) -> dict:
    rid = p["record_id"]
    pair = None
    if depth_index is not None and depth_index.n_rows:
        pair = XD.pair_and_walk(depth_index, p, fair=p.get("contract_value"))
    return RR.research_row(p, close=closes.get(rid), clv=clvs.get(rid), settlement=settlements.get(rid),
                           autopsy=autopsies.get(rid), sidecar=sidecar, crosscheck=(crosschecks or {}).get(rid), depth_pair=pair)


def sort_key(r: dict):
    return (r.get("game_id") or "", r.get("snapshot_id") or "", r.get("ticker") or "", r.get("model_arm") or "")


class ExecutionResearchAccumulator:
    """execution_research(), one research row at a time: the per-row table goes to `sink` (a callable taking the
    row) as it is built, and only the three float series the summary quantiles need are retained."""

    def __init__(self, sink=None):
        self.sink = sink
        self.n = self.sized = 0
        self.s10, self.s50, self.tops = array("d"), array("d"), array("d")
        self.partial_50 = 0

    def add(self, r: dict) -> dict:
        d = r.get("depth") or {}
        st = d.get("state")
        base = {"record_id": r.get("record_id"), "ticker": r.get("ticker"), "model_arm": r.get("model_arm"),
                "market_family": r.get("market_family"), "game_id": r.get("game_id"), "horizon_label": r.get("horizon_label"),
                "side": d.get("side"), "contract_value": r.get("contract_value"), "mid": r.get("h_mid"),
                "yes_ask": r.get("h_yes_ask"), "no_ask": r.get("h_no_ask"), "depth_state": st or "DEPTH_NOT_CAPTURED",
                "depth_reason": d.get("why"), "disagreement_band": r.get("disagreement_band")}
        self.n += 1
        if st not in ("DEPTH_CAPTURED", "DEPTH_STALE"):
            row = {**base, "top_size": None, "contracts_available": None}
        else:
            self.sized += 1
            v1, v10, v50 = d.get("vwap1"), d.get("vwap10"), d.get("vwap50")
            row = {**base, "top_size": d.get("top_size"), "levels": d.get("levels"),
                   "contracts_available": d.get("avail"), "book_age_minutes": d.get("age_min"),
                   "vwap_1": v1, "vwap_10": v10, "vwap_50": v50,
                   "slippage_1_to_10": (None if v1 is None or v10 is None else round(v10 - v1, 6)),
                   "slippage_1_to_50": (None if v1 is None or v50 is None else round(v50 - v1, 6)),
                   "fill_state_10": d.get("fill10", "FILLED"), "fill_state_50": d.get("fill50", "FILLED"),
                   "size_to_exhaust_edge": d.get("edge_size")}
        for series, key in ((self.s10, "slippage_1_to_10"), (self.s50, "slippage_1_to_50"), (self.tops, "top_size")):
            if row.get(key) is not None:
                series.append(float(row[key]))
        if row.get("fill_state_50") not in (None, "FILLED"):
            self.partial_50 += 1
        if self.sink is not None:
            self.sink(row)
        return row

    def summary(self) -> dict:
        def q(vals, p):
            vals = sorted(vals)
            return vals[min(int(p * len(vals)), len(vals) - 1)] if vals else None
        return {"depth_version": XD.DEPTH_VERSION, "sizes": list(XD.SIZES), "n": self.n, "n_with_depth": self.sized,
                "top_of_book_size": {"p10": q(self.tops, 0.10), "median": q(self.tops, 0.50), "p90": q(self.tops, 0.90),
                                     "under_10_contracts": sum(1 for t in self.tops if t < 10)},
                "slippage_1_to_10": {"median": q(self.s10, 0.50), "p90": q(self.s10, 0.90), "over_1c": sum(1 for x in self.s10 if x > 0.01)},
                "slippage_1_to_50": {"median": q(self.s50, 0.50), "p90": q(self.s50, 0.90), "over_1c": sum(1 for x in self.s50 if x > 0.01)},
                "partial_fill_at_50": self.partial_50,
                "note": "CLV is untouched by this table: canonical top-of-book CLV keeps its own definition and sign convention"}


def execution_research(rows) -> dict:
    """Size-adjusted execution, derived from the depth frozen on each record. Never estimated where absent.

    The frozen block carries the volume-weighted entry at 1 / 10 / 50 contracts, so this table answers the
    profitability question the top-of-book numbers cannot: how much size was there, what did the walk cost, and
    how much of the modelled edge is left. Rows with no captured book contribute to the denominator and to no
    statistic -- a market whose depth was never observed must not be summarised as if it were deep.
    """
    out = []
    acc = ExecutionResearchAccumulator(sink=out.append)
    for r in rows:
        acc.add(r)
    return {**acc.summary(), "rows": out}


def flat_row(row: dict, types: dict) -> dict:
    """The research row with nested values json-encoded (the parquet's column contract, unchanged), noting the
    Python type of every value so the parquet schema can be fixed before a single row group is written."""
    out = {}
    for k, v in row.items():
        if isinstance(v, (dict, list)):
            v = json.dumps(v)
        out[k] = v
        s = types.get(k)
        if s is None:
            s = types[k] = set()
        s.add(type(v).__name__)
    return out


def write_parquet_in_chunks(flat_path: str, out: str, label: str, types: dict, *, chunk_rows: int = 10000) -> dict:
    """The parquet from the flat ndjson, one row group at a time, under a schema fixed from the observed types.

    polars' ndjson sink materialises the whole file (about 1.6x its size in memory) whatever the schema, which
    put the week-1 export back on the archive's scale. pyarrow writes row groups from bounded chunks instead.
    A column whose values were only ever null is a string column; a column mixing numbers and strings is
    written as strings (str() of the value), which polars would have refused outright.

    Written in PARTS, rolled between row groups, because the remote refuses any file over 100 MB and this one
    grows with the slate -- 45 MB through week 1, 77 MB once week 2's Sunday games were settled
    (nfl_edge/evaluation/research_parts.py).
    """
    import pyarrow as pa
    import pyarrow.parquet as pq

    def arrow_type(ts: set):
        ts = ts - {"NoneType"}
        if not ts:
            return pa.string()
        if ts <= {"bool"}:
            return pa.bool_()
        if ts <= {"int"}:
            return pa.int64()
        if ts <= {"int", "float"}:
            return pa.float64()
        return pa.string()

    schema = pa.schema([(k, arrow_type(v)) for k, v in types.items()])
    coerce = [k for k, v in types.items() if arrow_type(v) == pa.string() and (v - {"NoneType"}) - {"str"}]
    roll = RP.RollingWriter(out, label, "parquet",
                            open_part=lambda p: pq.ParquetWriter(p, schema),
                            close_part=lambda w: w.close())
    chunk, n, groups = [], 0, 0

    def flush():
        nonlocal groups
        if chunk:
            roll.w.write_table(pa.Table.from_pylist(chunk, schema=schema))
            chunk.clear()
            groups += 1
            roll.maybe_roll()          # between row groups only: a row group is never split across parts
    try:
        with open(flat_path) as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                for k in coerce:
                    if r.get(k) is not None:
                        r[k] = str(r[k])
                chunk.append(r)
                n += 1
                if len(chunk) >= chunk_rows:
                    flush()
        flush()
    finally:
        paths = roll.close()
    return {"rows": n, "row_groups": groups, "columns": len(schema), "coerced_to_string": sorted(coerce),
            "parts": [os.path.basename(p) for p in paths]}


def _ae_record(p: dict) -> dict:
    """What availability_events reads off a projection: the context and the instants, not the whole record."""
    return {k: p.get(k) for k in ("subject_id", "game_id", "observed_at", "horizon_label", "snapshot_id",
                                  "minutes_to_kickoff", "player_context")}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", required=True)
    ap.add_argument("--projections", action="append", default=[])
    ap.add_argument("--staging", default=os.path.join(ROOT, "data", "shadow", "v2"), help="local staging root holding closes/clv/settlements/autopsy written this job")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "shadow", "v2", "research"))
    ap.add_argument("--season", type=int, default=2026)
    ap.add_argument("--week", type=int, default=0, help="0 = every week present")
    ap.add_argument("--game", action="append", default=[], help="export exactly these games")
    ap.add_argument("--label", default="")
    ap.add_argument("--hypotheses", default="", help="automatic hypothesis registry (default <staging>/hypotheses/hypotheses.jsonl, "
                                                     "seeded from the market-data copy)")
    ap.add_argument("--depth-root", action="append", default=[],
                    help="dedicated depth-sweep roots (repeatable); default: <market-data>/data/shadow/v2/depth")
    a = ap.parse_args(argv)
    t0 = time.time()
    md = os.path.join(a.market_data, "data", "shadow", "v2")
    roots = a.projections or [os.path.join(md, "projections")]
    index = ProjectionIndex(roots, index_roots=[os.path.join(a.staging, INDEX_DIRNAME), os.path.join(md, INDEX_DIRNAME)],
                            write_root=os.path.join(a.staging, INDEX_DIRNAME))
    isum = index.summary()
    # ---- the units of work: games of the requested week (from the index), or every game plus the no-game rows
    games = index.games()
    if a.game:
        units = list(dict.fromkeys(a.game))
    elif a.week:
        units = sorted(g for g, e in games.items() if e.get("season") == a.season and e.get("week") == a.week)
    else:
        units = [NO_GAME] + sorted(games)
    log(f"projection index: {isum['files']} files, {isum['rows_total']} rows over {isum['games']} games; "
        f"{len(units)} unit(s) selected for season {a.season} week {a.week or 'all'} (rss {_rss_mb():.0f} MB)")
    depth_index = XD.DepthIndex(a.depth_root or [os.path.join(md, "depth"), os.path.join(a.staging, "depth")])
    log(f"dedicated depth sweep: {depth_index.n_rows} observation(s) over {len(depth_index.by_ticker)} ticker(s)")
    sidecars = SidecarCache(roots)
    label = a.label or (f"{a.season}_wk{a.week:02d}" if a.week else f"{a.season}_all")
    os.makedirs(a.out, exist_ok=True)
    tmpdir = tempfile.mkdtemp(prefix="research_export_", dir=a.out)
    flat_path = os.path.join(tmpdir, "flat.ndjson")               # nested values json-encoded, for the parquet sink
    exec_path = os.path.join(tmpdir, "execution_rows.ndjson")
    intern = Interner()
    flat_types: dict = {}
    slim_rows: list = []
    events: list = []
    exec_tmp = open(exec_path, "w")
    exec_acc = ExecutionResearchAccumulator(sink=lambda row: exec_tmp.write(json.dumps(row, default=str) + "\n"))
    aud_player, aud_exec = CV.AuditAccumulator(), CV.AuditAccumulator(CV.EXECUTION_FIELDS, label="execution_context")
    depth_cov = CV.DepthCoverageAccumulator()
    inj_states = CV.StateBreakdownAccumulator("player_context", "injury_state")
    av_states = CV.StateBreakdownAccumulator("player_context", "availability_state")
    scan = ScanStats()
    n_rows = n_prob = n_players = 0
    per_unit = []
    # The research rows go out in parts: one file per week grew past the 100 MB the remote will accept, and
    # took the week's settlement evidence down with it (nfl_edge/evaluation/research_parts.py).
    jl_roll = RP.RollingWriter(a.out, label, "jsonl.gz",
                               open_part=lambda p: gzip.GzipFile(p, "wb", mtime=0),
                               close_part=lambda w: w.close())
    with open(flat_path, "w") as flat:
        for unit in units:
            if unit == NO_GAME:
                files = index.files_with_no_game_rows()
                closes = corpus_index(os.path.join(a.staging, "closes"), os.path.join(md, "closes"), "closes_v2", "SEASON")
                clvs = {}
                settlements = corpus_index(os.path.join(a.staging, "settlements"), os.path.join(md, "settlements"), "settlements_v2", "SEASON_*", rank=S2.season_rank)
                autopsies = {}
                crosschecks = corpus_index(os.path.join(a.staging, "crosscheck"), os.path.join(md, "crosscheck"), "crosscheck_v2", "SEASON", rank=XC.rank)
                stream = (p for p in iter_projections(files=files, stats=scan) if not p.get("game_id"))
            else:
                files = index.files_for_game(unit)
                closes = corpus_index(os.path.join(a.staging, "closes"), os.path.join(md, "closes"), "closes_v2", unit)
                clvs = corpus_index(os.path.join(a.staging, "clv"), os.path.join(md, "clv"), "clv_v2", unit)
                settlements = corpus_index(os.path.join(a.staging, "settlements"), os.path.join(md, "settlements"), "settlements_v2", unit, rank=S2.season_rank)
                autopsies = corpus_index(os.path.join(a.staging, "autopsy"), os.path.join(md, "autopsy"), "autopsy_v2", unit)
                crosschecks = corpus_index(os.path.join(a.staging, "crosscheck"), os.path.join(md, "crosscheck"), "crosscheck_v2", unit, rank=XC.rank)
                stream = iter_projections(files=files, game_ids=[unit], season=(a.season if a.week else None),
                                          week=(a.week or None), stats=scan)
            # one game: build every research row, keep (sort key, serialised row, execution row, slim row)
            built, ae_records, ae_seen, u_rows, u_players = [], [], set(), 0, 0
            for p in stream:
                row = research_row(p, sidecars.get(p.get("snapshot_id")), closes, clvs, settlements, autopsies, crosschecks, depth_index)
                u_rows += 1
                built.append((sort_key(row), json.dumps(row, sort_keys=True, separators=(",", ":"), default=str).encode(),
                              json.dumps(flat_row(row, flat_types), default=str),
                              slim(row, intern), {k: row.get(k) for k in EXEC_SOURCE_FIELDS}))
                # derived, rebuildable research tables over the PROJECTIONS (never captured evidence)
                if (p.get("flags") or {}).get("has_probability"):
                    n_prob += 1
                    aud_exec.add(p); depth_cov.add(p)
                if p.get("subject_kind") == "player":
                    u_players += 1
                    aud_player.add(p); inj_states.add(p); av_states.add(p)
                    k = (p.get("subject_id"), p.get("game_id"), p.get("horizon_label") or "CYCLE", p.get("observed_at"))
                    if k[0] and k[1] and k not in ae_seen:       # transitions keep the first record per (player, game, horizon, instant)
                        ae_seen.add(k)
                        ae_records.append(_ae_record(p))
            built.sort(key=lambda t: t[0])
            for _key, line, flat_line, s, exec_src in built:
                jl_roll.w.write(line + b"\n")
                flat.write(flat_line + "\n")
                slim_rows.append(s)
                exec_acc.add(exec_src)
            jl_roll.maybe_roll()       # at unit boundaries: one game's rows stay together in one part
            events.extend(AE.transitions(ae_records))
            n_rows += u_rows; n_players += u_players
            per_unit.append({"unit": unit or "NO_GAME", "rows": u_rows, "players": u_players, "files": len(files),
                             "closes": len(closes), "clv": len(clvs), "settlements": len(settlements), "autopsies": len(autopsies)})
            log(f"  {unit or 'NO_GAME'}: {u_rows} rows from {len(files)} file(s); joined closes {len(closes)}, clv {len(clvs)}, "
                f"settlements {len(settlements)}, autopsies {len(autopsies)} (rss {_rss_mb():.0f} MB)")
            del built, closes, clvs, settlements, autopsies, crosschecks, ae_records
    jl_parts = jl_roll.close()
    jl = jl_parts[0] if jl_parts else RP.part_path(a.out, label, "jsonl.gz", 1)
    log(f"research rows: {len(jl_parts)} part(s) -> {', '.join(f'{os.path.basename(p)} {os.path.getsize(p) / 2**20:.0f} MB' for p in jl_parts)}")
    exec_tmp.close()
    rows = slim_rows
    pq, pq_info = None, None
    try:
        pq_info = write_parquet_in_chunks(flat_path, a.out, label, flat_types)
        pq = RP.part_path(a.out, label, "parquet", 1)
        log(f"parquet: {pq_info['rows']} rows in {pq_info['row_groups']} row groups, {pq_info['columns']} columns, "
            f"{len(pq_info['parts'])} part(s) (rss {_rss_mb():.0f} MB)")
    except Exception as e:  # noqa: BLE001
        log(f"parquet export skipped: {e}")
        pq = None
    sc = S3.build(rows)
    json.dump(sc, open(os.path.join(a.out, f"{label}.scorecard_v3.json"), "w"), indent=1, default=str)
    open(os.path.join(a.out, f"{label}.SCORECARD_V3.md"), "w").write(S3.render(sc, title=f"Shadow v2 scorecard v3 — {label}"))
    cands = HR.candidates_from_scorecard(sc, season=a.season, week=(a.week or 0), path_out=os.path.join(a.out, f"{label}.hypothesis_candidates.json"))
    # WS3: candidates enter the append-only registry as GENERATED -- and only GENERATED. The registry is part of
    # the published tree (data/shadow/v2/hypotheses on market-data), seeded from the published copy first so
    # this week's lines extend the history instead of replacing it. A multi-week export (no --week) has no single
    # generation window, so it registers nothing.
    hyp_path = a.hypotheses or os.path.join(a.staging, "hypotheses", "hypotheses.jsonl")
    hyp_seed = HR.seed_registry(hyp_path, os.path.join(md, "hypotheses", "hypotheses.jsonl"))
    hyp_reg = (HR.register_candidates(cands, path=hyp_path) if a.week else
               {"added": [], "skipped_existing": [], "refused": [], "note": "no --week: no single generation window"})
    log(f"hypothesis registry {hyp_path} ({hyp_seed}): added {len(hyp_reg['added'])}, already registered "
        f"{len(hyp_reg['skipped_existing'])}, refused {len(hyp_reg['refused'])}")
    # ---- derived, rebuildable research tables. None of these is captured evidence; all are recomputed from the
    # frozen records, so a change of method never silently rewrites what was observed.
    exec_summary = exec_acc.summary()
    audit = {"player_context": aud_player.finish(), "execution_context": aud_exec.finish(), "depth": depth_cov.finish(),
             "injury_states": inj_states.finish(), "availability_states": av_states.finish()}
    # the per-row execution table is one row per record and compresses ~20x; the summaries stay plain json
    with gzip.GzipFile(os.path.join(a.out, f"{label}.execution_sizes.json.gz"), "wb", mtime=0) as fh:
        fh.write((json.dumps(exec_summary, default=str)[:-1] + ', "rows": [').encode())
        with open(exec_path) as ef:
            first = True
            for line in ef:
                line = line.strip()
                if not line:
                    continue
                fh.write((b"" if first else b", ") + line.encode())
                first = False
        fh.write(b"]}")
    for name, blob in (("execution_summary", exec_summary),
                       ("availability_events", {"events": events, "summary": AE.summarize(events)}),
                       ("coverage_audit", audit)):
        json.dump(blob, open(os.path.join(a.out, f"{label}.{name}.json"), "w"), indent=1, default=str)
    for p in (flat_path, exec_path):
        try:
            os.remove(p)
        except OSError:
            pass
    try:
        os.rmdir(tmpdir)
    except OSError:
        pass
    log(f"execution table: {exec_summary['n_with_depth']} rows with captured depth of {exec_summary['n']}; "
        f"availability transitions: {len(events)}; weakest context fields: {audit['player_context']['weakest_fields']}")
    cov = {"rows": len(rows), "with_probability": sum(1 for r in rows if r.get("contract_value") is not None),
           "depth_coverage": audit["depth"]["captured_pct"], "availability_events": len(events),
           "execution_sized_rows": exec_summary["n_with_depth"],
           "context_fields_below_50_pct": audit["player_context"]["fields_below_50_pct"],
           "close_paired": sum(1 for r in rows if r.get("close_status") in ("CLOSE_OK", "CLOSE_ONE_SIDED")),
           "clv_ok": sum(1 for r in rows if r.get("clv_status") == "CLV_OK"), "settled": sum(1 for r in rows if r.get("settled_yes") is not None),
           "autopsied": sum(1 for r in rows if r.get("autopsy_classification")), "by_evidence_class": dict(Counter(r.get("evidence_class") for r in rows)),
           "dedicated_depth": {"observations": depth_index.n_rows, "tickers": len(depth_index.by_ticker),
                               "rows_paired": sum(1 for r in rows if r.get("depth_pair_state") not in (None, "DEPTH_NOT_CAPTURED")),
                               "pair_reasons": dict(Counter(r.get("depth_pair_reason") for r in rows if r.get("depth_pair_state") == "DEPTH_NOT_CAPTURED")),
                               "horizon_quality": dict(Counter(r.get("depth_pair_horizon_quality") for r in rows if r.get("depth_pair_horizon_quality"))),
                               "pair_age_minutes_median": _median([r.get("depth_pair_age_min") for r in rows])},
           # synchronized vs asynchronous, reported separately and never as one number
           "synchronization": {
               "counts": dict(Counter(r.get("synchronization_state") or "UNKNOWN_TIMING" for r in rows)),
               "with_probability": dict(Counter((r.get("synchronization_state") or "UNKNOWN_TIMING")
                                                for r in rows if r.get("contract_value") is not None)),
               "skew_seconds_median": _median([r.get("information_skew_seconds") for r in rows]),
               "skew_seconds_max": max([r.get("information_skew_seconds") for r in rows
                                        if r.get("information_skew_seconds") is not None] or [None],
                                       default=None),
               "excluded_from_synchronized_edge_research": sum(
                   1 for r in rows if r.get("contract_value") is not None
                   and (r.get("synchronization_state") or "UNKNOWN_TIMING") != "SYNCHRONIZED")},
           "hypothesis_candidates": len(cands),
           "hypothesis_registration": {"path": hyp_path, "seed": hyp_seed, "added": len(hyp_reg["added"]),
                                       "skipped_existing": len(hyp_reg["skipped_existing"]), "refused": hyp_reg["refused"][:20]},
           "scope": {"season": a.season, "week": a.week or None, "units": len(units), "per_unit": per_unit,
                     "projection_scan": scan.to_dict(), "scan_reconciles": scan.reconciles(), "index": isum,
                     "sidecars": sidecars.stats(), "projection_rows": n_rows, "probability_rows": n_prob, "player_rows": n_players},
           "perf": {"seconds": round(time.time() - t0, 1), "max_rss_mb": round(_rss_mb(), 1)},
           "files": {"jsonl": jl, "parquet": pq, "parquet_info": pq_info,
                     "jsonl_parts": [os.path.basename(x) for x in jl_parts],
                     "parquet_parts": (pq_info or {}).get("parts") or []}}
    json.dump(cov, open(os.path.join(a.out, f"{label}.export_summary.json"), "w"), indent=1, default=str)
    log(json.dumps({k: v for k, v in cov.items() if k != "scope"}, indent=1, default=str))
    log(json.dumps({"scope": {k: v for k, v in cov["scope"].items() if k != "per_unit"}}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
