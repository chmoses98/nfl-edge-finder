#!/usr/bin/env python3
"""NFL SYSTEM health summary from local bronze manifests and the market-data worktree.

Usage: health.py [--market-data-dir /path/to/market-data checkout]
Prints the observability block (DATA / KALSHI / MARKETS DISCOVERED / PRICED / UNSUPPORTED / MODEL / CALIBRATION /
LAST SNAPSHOT / SOURCE FAILURES / RECOMMENDATIONS). Fail-closed: anything missing is reported as degraded, never assumed healthy.
"""
import argparse, glob, json, os, sys
from datetime import datetime, timezone, timedelta
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--market-data-dir", default="/home/user/_md"); a = ap.parse_args()
    now = datetime.now(timezone.utc)
    out = {"time": now.isoformat()}
    # DATA: bronze manifest freshness
    man = os.path.join(ROOT, "data/raw/nflverse/_manifest.jsonl")
    if os.path.exists(man):
        rows = [json.loads(l) for l in open(man)]
        ok = [r for r in rows if r.get("status") == 200]
        latest = max(r["retrieved_at"] for r in ok)
        age_h = (now - datetime.fromisoformat(latest)).total_seconds() / 3600
        out["DATA"] = f"{'healthy' if age_h < 48 else 'degraded'} ({len(ok)} nflverse files, last retrieval {age_h:.1f}h ago, 404s={sum(1 for r in rows if r.get('status')==404)}, failed={sum(1 for r in rows if r.get('status')=='failed')})"
    else:
        out["DATA"] = "degraded (no bronze manifest)"
    # KALSHI: latest capture manifest
    caps = sorted(glob.glob(os.path.join(a.market_data_dir, "data/kalshi/capture/*/*.manifest.json")))
    if caps:
        j = json.load(open(caps[-1]))
        age_m = (now - datetime.fromisoformat(j["finished_at"])).total_seconds() / 60
        state = "healthy" if (age_m < 30 and not j.get("partial")) else "degraded"
        out["KALSHI"] = f"{state} (last capture {age_m:.0f} min ago, run {j['run_id']}, trigger {j.get('trigger_source')}, partial={j.get('partial')}, 429s={j['client_stats'].get('http_429')}, quotes changed {j.get('quotes_written')} / unchanged {j.get('quotes_unchanged')}, books {j.get('books_written')}, trades {j.get('trades_written')})"
        out["LAST SNAPSHOT"] = j["finished_at"]
        out["MARKETS OBSERVED (open)"] = j.get("quotes_written", 0) + j.get("quotes_unchanged", 0)
        out["SOURCE FAILURES"] = j.get("errors") or "none"
        # capture cadence over last 3 hours
        recent = [json.load(open(c)) for c in caps if (now - datetime.fromisoformat(os.path.basename(c)[:15].replace("T", "T") + "+00:00" if False else json.load(open(c))["finished_at"])).total_seconds() < 3 * 3600]
        out["CAPTURE PASSES last 3h"] = f"{len(recent)} (target 18)"
    else:
        out["KALSHI"] = "degraded (no capture manifests found)"
    disc = sorted(glob.glob(os.path.join(a.market_data_dir, "data/kalshi/discovery/*/summary.json")))
    if disc:
        s = json.load(open(disc[-1]))
        n_mk = sum(sum(v.get("markets_by_status", {}).values()) for v in s.get("per_series", {}).values())
        out["MARKETS DISCOVERED (last discovery)"] = f"{n_mk} across {len(s.get('per_series', {}))} series, run {s['run_id']}, complete={s.get('complete')}"
    reg = json.load(open(os.path.join(ROOT, "config/kalshi_nfl_series.json")))
    out["UNSUPPORTED (registry families unclassified)"] = sum(1 for v in reg["series"].values() if v["family"] in ("NFL_MISC_UNCLASSIFIED", "UNKNOWN_NEEDS_CLASSIFICATION"))
    out["MODEL"] = "none promoted (research only: game_env v0.1 market-prior, player_distributions v0.1)"
    out["CALIBRATION"] = "none (no prospective 2026 outcomes yet)"
    out["RECOMMENDATIONS"] = 0
    out["REAL-MONEY STATUS"] = "NOT AUTHORIZED / NOT VALIDATED"
    print("NFL SYSTEM")
    for k, v in out.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
