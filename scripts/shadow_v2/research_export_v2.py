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
    cov = {"rows": len(rows), "with_probability": sum(1 for r in rows if r.get("contract_value") is not None),
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
