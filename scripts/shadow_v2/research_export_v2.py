#!/usr/bin/env python3
"""Rebuild the deterministic RESEARCH TABLE (one row per frozen projection, joined by record_id to close, CLV,
settlement, context and autopsy) and the scorecard v3 from the immutable corpora. Derived; rebuildable; never
writes into the corpora.

    python3 scripts/shadow_v2/research_export_v2.py --market-data /tmp/md [--projections <root>]* --out data/shadow/v2/research --season 2026 [--week 1]
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import resource
import sys
import time
from collections import Counter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.evaluation import availability_events as AE                            # noqa: E402
from nfl_edge.evaluation import coverage as CV                                       # noqa: E402
from nfl_edge.evaluation import execution_depth as XD                                # noqa: E402
from nfl_edge.evaluation import research_record as RR, scorecard_v3 as S3            # noqa: E402
from nfl_edge.projection.store import read_projections, read_sidecars                # noqa: E402
from nfl_edge.research import hypothesis_registry_v2 as HR                            # noqa: E402
from nfl_edge.shadow import evaluation_store as ST                                    # noqa: E402


def log(*a):
    print(*a, flush=True)


def corpus_index(root_local: str, root_md: str, suffix: str) -> dict:
    c = ST.EvaluationCorpus(root_local, read_roots=[root_md], suffix=suffix)
    return {pid: row for (pid, _ver), (row, _f) in c.load().items()}


def build_rows(projections: list, sidecars: dict, closes: dict, clvs: dict, settlements: dict, autopsies: dict) -> list:
    out = []
    for p in projections:
        rid = p["record_id"]
        out.append(RR.research_row(p, close=closes.get(rid), clv=clvs.get(rid), settlement=settlements.get(rid), autopsy=autopsies.get(rid), sidecar=sidecars.get(p.get("snapshot_id"))))
    out.sort(key=lambda r: (r.get("game_id") or "", r.get("snapshot_id") or "", r.get("ticker") or "", r.get("model_arm") or ""))
    return out


def execution_research(rows) -> dict:
    """Size-adjusted execution, derived from the depth frozen on each record. Never estimated where absent.

    The frozen block carries the volume-weighted entry at 1 / 10 / 50 contracts, so this table answers the
    profitability question the top-of-book numbers cannot: how much size was there, what did the walk cost, and
    how much of the modelled edge is left. Rows with no captured book contribute to the denominator and to no
    statistic -- a market whose depth was never observed must not be summarised as if it were deep.
    """
    out, sized = [], 0
    for r in rows:
        d = r.get("depth") or {}
        st = d.get("state")
        base = {"record_id": r.get("record_id"), "ticker": r.get("ticker"), "model_arm": r.get("model_arm"),
                "market_family": r.get("market_family"), "game_id": r.get("game_id"), "horizon_label": r.get("horizon_label"),
                "side": d.get("side"), "contract_value": r.get("contract_value"), "mid": r.get("mid"),
                "yes_ask": r.get("yes_ask"), "no_ask": r.get("no_ask"), "depth_state": st or "DEPTH_NOT_CAPTURED",
                "depth_reason": d.get("why"), "disagreement_band": r.get("disagreement_band")}
        if st not in ("DEPTH_CAPTURED", "DEPTH_STALE"):
            out.append({**base, "top_size": None, "contracts_available": None})
            continue
        sized += 1
        v1, v10, v50 = d.get("vwap1"), d.get("vwap10"), d.get("vwap50")
        out.append({**base, "top_size": d.get("top_size"), "levels": d.get("levels"),
                    "contracts_available": d.get("avail"), "book_age_minutes": d.get("age_min"),
                    "vwap_1": v1, "vwap_10": v10, "vwap_50": v50,
                    "slippage_1_to_10": (None if v1 is None or v10 is None else round(v10 - v1, 6)),
                    "slippage_1_to_50": (None if v1 is None or v50 is None else round(v50 - v1, 6)),
                    "fill_state_10": d.get("fill10", "FILLED"), "fill_state_50": d.get("fill50", "FILLED"),
                    "size_to_exhaust_edge": d.get("edge_size")})
    def q(vals, p):
        vals = sorted(v for v in vals if v is not None)
        return vals[min(int(p * len(vals)), len(vals) - 1)] if vals else None
    s10 = [r.get("slippage_1_to_10") for r in out]
    s50 = [r.get("slippage_1_to_50") for r in out]
    tops = [r.get("top_size") for r in out]
    return {"depth_version": XD.DEPTH_VERSION, "sizes": list(XD.SIZES), "n": len(out), "n_with_depth": sized,
            "top_of_book_size": {"p10": q(tops, 0.10), "median": q(tops, 0.50), "p90": q(tops, 0.90),
                                 "under_10_contracts": sum(1 for t in tops if t is not None and t < 10)},
            "slippage_1_to_10": {"median": q(s10, 0.50), "p90": q(s10, 0.90), "over_1c": sum(1 for x in s10 if x is not None and x > 0.01)},
            "slippage_1_to_50": {"median": q(s50, 0.50), "p90": q(s50, 0.90), "over_1c": sum(1 for x in s50 if x is not None and x > 0.01)},
            "partial_fill_at_50": sum(1 for r in out if r.get("fill_state_50") not in (None, "FILLED")),
            "note": "CLV is untouched by this table: canonical top-of-book CLV keeps its own definition and sign convention",
            "rows": out}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", required=True)
    ap.add_argument("--projections", action="append", default=[])
    ap.add_argument("--staging", default=os.path.join(ROOT, "data", "shadow", "v2"), help="local staging root holding closes/clv/settlements/autopsy written this job")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "shadow", "v2", "research"))
    ap.add_argument("--season", type=int, default=2026)
    ap.add_argument("--week", type=int, default=0, help="0 = every week present")
    ap.add_argument("--label", default="")
    a = ap.parse_args(argv)
    t0 = time.time()
    md = os.path.join(a.market_data, "data", "shadow", "v2")
    roots = a.projections or [os.path.join(md, "projections")]
    projections = read_projections(roots)
    if a.week:
        projections = [p for p in projections if p.get("week") == a.week and p.get("season") == a.season]
    sidecars = read_sidecars(roots)
    closes = corpus_index(os.path.join(a.staging, "closes"), os.path.join(md, "closes"), "closes_v2")
    clvs = corpus_index(os.path.join(a.staging, "clv"), os.path.join(md, "clv"), "clv_v2")
    settlements = corpus_index(os.path.join(a.staging, "settlements"), os.path.join(md, "settlements"), "settlements_v2")
    autopsies = corpus_index(os.path.join(a.staging, "autopsy"), os.path.join(md, "autopsy"), "autopsy_v2")
    rows = build_rows(projections, sidecars, closes, clvs, settlements, autopsies)
    label = a.label or (f"{a.season}_wk{a.week:02d}" if a.week else f"{a.season}_all")
    os.makedirs(a.out, exist_ok=True)
    jl = os.path.join(a.out, f"{label}.research.jsonl.gz")
    with gzip.GzipFile(jl, "wb", mtime=0) as raw:
        for r in rows:
            raw.write((json.dumps(r, sort_keys=True, separators=(",", ":"), default=str) + "\n").encode())
    pq = None
    try:
        import polars as pl
        pq = os.path.join(a.out, f"{label}.research.parquet")
        pl.DataFrame([{k: (json.dumps(v) if isinstance(v, (dict, list)) else v) for k, v in r.items()} for r in rows], infer_schema_length=None).write_parquet(pq)
    except Exception as e:  # noqa: BLE001
        log(f"parquet export skipped: {e}")
    sc = S3.build(rows)
    json.dump(sc, open(os.path.join(a.out, f"{label}.scorecard_v3.json"), "w"), indent=1, default=str)
    open(os.path.join(a.out, f"{label}.SCORECARD_V3.md"), "w").write(S3.render(sc, title=f"Shadow v2 scorecard v3 — {label}"))
    cands = HR.candidates_from_scorecard(sc, season=a.season, week=(a.week or 0), path_out=os.path.join(a.out, f"{label}.hypothesis_candidates.json"))
    # ---- derived, rebuildable research tables. None of these is captured evidence; all are recomputed from the
    # frozen records, so a change of method never silently rewrites what was observed.
    prob = [r for r in projections if (r.get("flags") or {}).get("has_probability")]
    players = [r for r in projections if r.get("subject_kind") == "player"]
    exec_table = execution_research(rows)
    events = AE.transitions(players)
    audit = {"player_context": CV.audit(players), "execution_context": CV.audit(prob, CV.EXECUTION_FIELDS, label="execution_context"),
             "depth": CV.depth_coverage(prob),
             "injury_states": CV.state_breakdown(players, "player_context", "injury_state"),
             "availability_states": CV.state_breakdown(players, "player_context", "availability_state")}
    # the per-row execution table is one row per record and compresses ~20x; the summaries stay plain json
    with gzip.GzipFile(os.path.join(a.out, f"{label}.execution_sizes.json.gz"), "wb", mtime=0) as fh:
        fh.write(json.dumps(exec_table, default=str).encode())
    for name, blob in (("execution_summary", {k: v for k, v in exec_table.items() if k != "rows"}),
                       ("availability_events", {"events": events, "summary": AE.summarize(events)}),
                       ("coverage_audit", audit)):
        json.dump(blob, open(os.path.join(a.out, f"{label}.{name}.json"), "w"), indent=1, default=str)
    log(f"execution table: {exec_table['n_with_depth']} rows with captured depth of {exec_table['n']}; "
        f"availability transitions: {len(events)}; weakest context fields: {audit['player_context']['weakest_fields']}")
    cov = {"rows": len(rows), "with_probability": sum(1 for r in rows if r.get("contract_value") is not None),
           "depth_coverage": audit["depth"]["captured_pct"], "availability_events": len(events),
           "execution_sized_rows": exec_table["n_with_depth"],
           "context_fields_below_50_pct": audit["player_context"]["fields_below_50_pct"],
           "close_paired": sum(1 for r in rows if r.get("close_status") in ("CLOSE_OK", "CLOSE_ONE_SIDED")),
           "clv_ok": sum(1 for r in rows if r.get("clv_status") == "CLV_OK"), "settled": sum(1 for r in rows if r.get("settled_yes") is not None),
           "autopsied": sum(1 for r in rows if r.get("autopsy_classification")), "by_evidence_class": dict(Counter(r.get("evidence_class") for r in rows)),
           "hypothesis_candidates": len(cands), "perf": {"seconds": time.time() - t0, "max_rss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0},
           "files": {"jsonl": jl, "parquet": pq}}
    json.dump(cov, open(os.path.join(a.out, f"{label}.export_summary.json"), "w"), indent=1, default=str)
    log(json.dumps(cov, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
