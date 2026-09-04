#!/usr/bin/env python3
"""Historical Kalshi NFL backfill from the official historical tier.

Kalshi archives markets settled before `GET /historical/cutoff` (observed
2026-07-05): the whole 2025 season lives ONLY in /historical/*. This job is
resumable: a state file lists what has been fetched so a run with a request
budget can be chained until done.

Stage 1  markets   GET /historical/markets?series_ticker=S  (all archived markets, with result/settlement)
Stage 2  per market: GET /historical/markets/{t}/candlesticks (period 60 over the market's life, then 1-min
                     for the final 24h before close) and GET /historical/trades?ticker=t
Order of stage 2: single-game families first (GAME, SPREAD, TOTAL, TEAMTOTAL, props), most recent first.

Outputs (append-only):
  data/kalshi/backfill/markets/<SERIES>.jsonl          one line per archived market (raw)
  data/kalshi/backfill/candles/<SERIES>/<TICKER>.json   {"h60": [...], "m1": [...]}
  data/kalshi/backfill/trades/<SERIES>/<TICKER>.jsonl
  data/kalshi/backfill/state.json
Known limitation: no historical order books exist in the API (only trades and
bid/ask candlesticks) -- which is why prospective capture started on day one.
"""
from __future__ import annotations
import argparse, json, os, sys, time
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.kalshi.client import KalshiClient  # noqa
from nfl_edge.kalshi.classifier import classify  # noqa

OUT = os.path.join(ROOT, "data", "kalshi", "backfill")
REG_PATH = os.path.join(ROOT, "config", "kalshi_nfl_series.json")
PRIORITY = ["KXNFLGAME", "KXNFLSPREAD", "KXNFLTOTAL", "KXNFLTEAMTOTAL", "KXNFLPASSYDS", "KXNFLRECYDS", "KXNFLRSHYDS", "KXNFLREC", "KXNFLTD",
            "KXNFLANYTD", "KXNFLPASSTDS", "KXNFLFIRSTTD", "KXNFLWINMARGIN", "KXNFL1HSPREAD", "KXNFL1HTOTAL", "KXNFL1H", "KXNFLPASSATT",
            "KXNFLPASSCOMP", "KXNFLRSHATT", "KXNFLPASSINT", "KXNFLTOTALTD", "KXNFLBOTH", "KXNFLRACE"]


def ts(s):
    return int(datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=12000, help="max HTTP requests this run")
    ap.add_argument("--rps", type=float, default=5.0)
    ap.add_argument("--stage", default="all", choices=["markets", "detail", "all"])
    ap.add_argument("--series", default="", help="comma list to restrict")
    a = ap.parse_args()
    os.makedirs(os.path.join(OUT, "markets"), exist_ok=True)
    state_path = os.path.join(OUT, "state.json")
    state = json.load(open(state_path)) if os.path.exists(state_path) else {"markets_done": {}, "detail_done": {}, "runs": []}
    reg = json.load(open(REG_PATH))["series"]
    series = [s for s in reg if reg[s]["tier"] != "NOT_CAPTURED"]
    if a.series:
        series = [s for s in a.series.split(",") if s]
    ordered = [s for s in PRIORITY if s in series] + [s for s in series if s not in PRIORITY]
    c = KalshiClient(rps=a.rps)
    run = {"started_at": datetime.now(timezone.utc).isoformat(), "budget": a.budget, "markets_fetched": 0, "details_fetched": 0, "errors": []}

    def budget_left():
        return a.budget - c.stats.requests

    # ---------------- stage 1: archived market lists
    if a.stage in ("markets", "all"):
        for s in ordered:
            if budget_left() < 50:
                break
            done = state["markets_done"].get(s)
            if done and done.get("complete"):
                continue
            items, complete, info = c.historical_markets(series_ticker=s, limit=1000, max_pages=max(1, budget_left() // 2))
            path = os.path.join(OUT, "markets", f"{s}.jsonl")
            with open(path, "w") as f:
                for m in items:
                    f.write(json.dumps(m, separators=(",", ":")) + "\n")
            state["markets_done"][s] = {"n": len(items), "complete": complete, "fetched_at": datetime.now(timezone.utc).isoformat(), "info": info}
            run["markets_fetched"] += len(items)
            print(json.dumps({"series": s, "n": len(items), "complete": complete}), flush=True)
            if not complete:
                run["errors"].append({"series": s, "stage": "markets", "info": info})
    # ---------------- stage 2: candles + trades per market (priority order, newest first)
    if a.stage in ("detail", "all"):
        for s in ordered:
            path = os.path.join(OUT, "markets", f"{s}.jsonl")
            if not os.path.exists(path) or budget_left() < 10:
                continue
            fam_tier = reg.get(s, {}).get("tier")
            if fam_tier != "FULL_MICROSTRUCTURE":
                continue  # detail backfill only for single-game families (cost control); lists are kept for all
            mk = [json.loads(l) for l in open(path)]
            mk.sort(key=lambda m: m.get("close_time") or "", reverse=True)
            done = state["detail_done"].setdefault(s, {})
            os.makedirs(os.path.join(OUT, "candles", s), exist_ok=True); os.makedirs(os.path.join(OUT, "trades", s), exist_ok=True)
            for m in mk:
                if budget_left() < 6:
                    break
                t = m["ticker"]
                if t in done:
                    continue
                try:
                    t0 = ts(m.get("open_time") or m.get("created_time")); t1 = ts(m.get("close_time") or m.get("expiration_time"))
                except Exception:
                    done[t] = {"skipped": "no times"}; continue
                rec = {}
                h60, e1 = c.try_get(f"historical/markets/{t}/candlesticks", {"start_ts": t0, "end_ts": t1, "period_interval": 60})
                m1, e2 = c.try_get(f"historical/markets/{t}/candlesticks", {"start_ts": max(t0, t1 - 86400), "end_ts": t1, "period_interval": 1})
                tr, ok, info = c.historical_trades(ticker=t, limit=1000, max_pages=10)
                json.dump({"ticker": t, "h60": (h60 or {}).get("candlesticks"), "m1": (m1 or {}).get("candlesticks"), "errors": [e1, e2]},
                          open(os.path.join(OUT, "candles", s, f"{t}.json"), "w"), separators=(",", ":"))
                with open(os.path.join(OUT, "trades", s, f"{t}.jsonl"), "w") as f:
                    for x in tr:
                        f.write(json.dumps(x, separators=(",", ":")) + "\n")
                done[t] = {"h60": len((h60 or {}).get("candlesticks") or []), "m1": len((m1 or {}).get("candlesticks") or []), "trades": len(tr), "complete": ok and not e1}
                run["details_fetched"] += 1
            print(json.dumps({"series": s, "detail_done": len(done), "of": len(mk)}), flush=True)
    run["finished_at"] = datetime.now(timezone.utc).isoformat(); run["client_stats"] = c.stats.to_dict()
    remaining = sum(1 for s in ordered if reg.get(s, {}).get("tier") == "FULL_MICROSTRUCTURE" and os.path.exists(os.path.join(OUT, "markets", f"{s}.jsonl"))
                    and len(state["detail_done"].get(s, {})) < sum(1 for _ in open(os.path.join(OUT, "markets", f"{s}.jsonl"))))
    run["series_with_detail_remaining"] = remaining
    state["runs"].append(run)
    json.dump(state, open(state_path, "w"), separators=(",", ":"))
    print(json.dumps(run, default=str))
    # exit 3 => more work remains (workflow may chain another run)
    return 3 if remaining else 0


if __name__ == "__main__":
    sys.exit(main())
