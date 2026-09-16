#!/usr/bin/env python3
"""Project a week's Kalshi board from the coherent game simulation (shadow only).

Usage:
  python scripts/sim/project_week.py --season 2026 --week 2 --market-data /home/user/_market_data_wt \
      [--cutoff 2026-09-16T12:00:00Z] [--n-sims 20000] [--out data/shadow/sim] [--bundle research/simulation_engine/bundle_2026.json]

Reads the newest incumbent ledger snapshot at or before the cutoff for the market universe and quotes,
builds point-in-time inputs (rosters, depth chart, injuries, Sleeper availability, play-by-play history
through the last completed game), fits (or loads) the season bundle on earlier seasons, simulates every
game not yet kicked off, prices every FULL-period contract of the supported families and writes one
write-once projections file plus a manifest.  It never touches the incumbent ledger, the arms corpus or
the recommendation ledger.
"""
from __future__ import annotations
import argparse, json, os, sys
from datetime import datetime, timezone
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
import polars as pl
from nfl_edge.sim import SIM_VERSION, features as F, prospective as P, training as T, backtest as B, reconcile as R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--season", type=int, required=True)
    ap.add_argument("--week", type=int, required=True)
    ap.add_argument("--market-data", default="/home/user/_market_data_wt")
    ap.add_argument("--cutoff", default=None, help="ISO instant; default now")
    ap.add_argument("--n-sims", type=int, default=20000)
    ap.add_argument("--out", default=ROOT)
    ap.add_argument("--bundle", default=None)
    ap.add_argument("--weights", default=os.path.join(B.OUT, "reconciliation_weights.json"))
    a = ap.parse_args()
    cutoff = datetime.fromisoformat(a.cutoff.replace("Z", "+00:00")) if a.cutoff else datetime.now(timezone.utc)
    generated_at = datetime.now(timezone.utc)
    ledger_rows, man, run_id = P.latest_ledger(a.market_data, at_or_before=cutoff)
    observed_at = max((r.get("observed_at") or "") for r in ledger_rows)
    print(f"ledger {run_id}: {len(ledger_rows)} rows, market observed through {observed_at}")
    bundle_path = a.bundle or os.path.join(B.OUT, f"bundle_{a.season}.json")
    if os.path.exists(bundle_path):
        bundle = json.load(open(bundle_path))
    else:
        bundle = T.fit_bundle(a.season)
        os.makedirs(os.path.dirname(bundle_path), exist_ok=True)
        json.dump(bundle, open(bundle_path, "w"))
    if not bundle.get("priors"):
        raise SystemExit(f"{bundle_path} carries no frozen priors; refit it with the current training code")
    priors = F.PriorSet.from_dict(bundle["priors"])
    if max(priors.fit_seasons) >= a.season:
        raise SystemExit(f"bundle priors were fitted on {priors.fit_seasons}, which reaches season {a.season}")
    weights = R.load_weights(a.weights) if os.path.exists(a.weights) else None
    pmap = pl.read_parquet(os.path.join(ROOT, "data", "silver", "kalshi_player_map.parquet"))
    pmap = pmap.filter(pl.col("gsis_id").is_not_null() & pl.col("status").str.starts_with("RESOLVED"))
    player_map = dict(zip(pmap["kalshi_player_id"].to_list(), pmap["gsis_id"].to_list()))
    slate = P.slate_inputs(a.season, a.week, cutoff, a.market_data, ledger_rows=ledger_rows, priors=priors)
    print("sources", json.dumps(slate["sources"], default=str))
    rows = P.price_slate(slate, ledger_rows, bundle, weights, n_sims=a.n_sims, run_id=run_id, observed_at=observed_at,
                         generated_at=generated_at, player_map=player_map)
    from collections import Counter
    c = Counter((r["family"], r["support_state"]) for r in rows)
    print(json.dumps({f"{k[0]}|{k[1]}": v for k, v in c.most_common()}, indent=0))
    manifest = {"run_id": run_id, "sim_version": SIM_VERSION, "season": a.season, "week": a.week, "cutoff": cutoff.isoformat(),
                "generated_at": generated_at.isoformat(), "market_observed_at": observed_at, "ledger_manifest": {k: man.get(k) for k in ("run_id", "written_at")},
                "bundle": bundle_path, "bundle_train_seasons": bundle.get("train_seasons"),
                "priors_fit_seasons": list(priors.fit_seasons), "priors_version": priors.version,
                "weights": a.weights if weights else None,
                "deployed_weights": {k: v.get("weight") for k, v in ((weights or {}).get("fitted") or {}).items()},
                "sources": slate["sources"], "n_rows": len(rows), "counts": {f"{k[0]}|{k[1]}": v for k, v in c.items()},
                "games": {gid: {"center_source": G["input"].center_source, "spread_home": G["input"].spread_home,
                                "total": G["input"].total_line, "kickoff": G["kickoff"].isoformat()} for gid, G in slate["games"].items()}}
    path = P.write_records(a.out, run_id, rows, manifest)
    print("wrote", path)


if __name__ == "__main__":
    main()
