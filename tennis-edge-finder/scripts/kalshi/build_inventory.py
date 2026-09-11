#!/usr/bin/env python3
"""Build the canonical machine-readable Kalshi tennis inventory from a discovery snapshot.

Output: config/kalshi_tennis_series.json (series-level inventory + family mapping + counts)
        and a coverage summary used by health gates TENNIS-1/2/3.
"""
from __future__ import annotations
import argparse, collections, glob, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, PROJ)
from tennis_edge.kalshi.families import SERIES, FAMILIES, unknown_series  # noqa: E402
from tennis_edge.kalshi.markets import parse_market  # noqa: E402


def latest_discovery(root):
    runs = sorted(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)))
    if not runs:
        raise SystemExit("no discovery runs")
    return os.path.join(root, runs[-1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--discovery", default=None)
    ap.add_argument("--out", default=os.path.join(PROJ, "config", "kalshi_tennis_series.json"))
    a = ap.parse_args()
    d = a.discovery or latest_discovery(os.path.join(PROJ, "data", "kalshi", "discovery"))
    series = json.load(open(os.path.join(d, "series_tennis.json")))
    summary = json.load(open(os.path.join(d, "summary.json")))
    inv = {"snapshot_run_id": summary["run_id"], "snapshot_started_at": summary["started_at"], "series_total_on_exchange": summary["series_total"],
           "tennis_series": [], "families": FAMILIES, "unknown_series": unknown_series([s["ticker"] for s in series]), "coverage": {}}
    stat = collections.Counter(); fam_counts = collections.Counter()
    active_stat = collections.Counter()
    for s in series:
        tk = s["ticker"]
        fam = SERIES.get(tk)
        rec = {"ticker": tk, "title": s.get("title"), "category": s.get("category"), "tags": s.get("tags"), "frequency": s.get("frequency"),
               "fee_type": s.get("fee_type"), "fee_multiplier": s.get("fee_multiplier"), "contract_terms_url": s.get("contract_terms_url"),
               "settlement_sources": s.get("settlement_sources"), "product_metadata": s.get("product_metadata"),
               "family": fam[0] if fam else "UNKNOWN", "tour": fam[1] if fam else None, "level": fam[2] if fam else None,
               "discipline": fam[3] if fam else None, "projectable": FAMILIES[fam[0]]["projectable"] if fam else False,
               "classification_evidence": s.get("_classification", {}).get("evidence")}
        ps = summary["per_series"].get(tk, {})
        rec["markets_by_status"] = ps.get("markets_by_status", {})
        rec["historical_markets"] = ps.get("historical_markets_n", 0)
        rec["events"] = ps.get("events_n", 0)
        # parse coverage per series
        mk_path = os.path.join(d, "markets", f"{tk}.json")
        cov = collections.Counter()
        if os.path.exists(mk_path):
            for st, blk in json.load(open(mk_path)).items():
                for m in blk.get("markets") or []:
                    pm = parse_market(m)
                    cov[pm.status] += 1
                    stat[pm.status] += 1
                    fam_counts[pm.family] += 1
                    if st == "open":
                        active_stat[pm.status] += 1
        rec["parse_coverage_live"] = dict(cov)
        inv["tennis_series"].append(rec)
    inv["coverage"] = {"live_markets_by_parse_status": dict(stat), "open_markets_by_parse_status": dict(active_stat), "live_markets_by_family": dict(fam_counts)}
    with open(a.out, "w") as f:
        json.dump(inv, f, indent=1)
    print(json.dumps(inv["coverage"], indent=1)); print("unknown:", inv["unknown_series"])


if __name__ == "__main__":
    main()
