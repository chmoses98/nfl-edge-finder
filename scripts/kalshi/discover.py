#!/usr/bin/env python3
"""Kalshi NFL market-universe discovery (bronze capture).

Runs inside GitHub Actions (the dev sandbox cannot reach Kalshi). Saves RAW
API responses verbatim so nothing is normalized away (MLB lesson: strike,
result, settlement fields were dropped by early ingestion and it cost a
settlement-semantics bug).

Outputs under --out (default data/kalshi/discovery/<run_id>/):
  series_all.json          every series on the exchange (unfiltered)
  series_nfl.json          NFL-candidate series with match evidence
  markets/<SERIES>.json    all markets per candidate series, per status
  events/<SERIES>.json     events per candidate series
  probes.json              endpoint probes (historical tier, orderbook, trades, candles)
  summary.json             counts, client stats, failures (fail-closed flags)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.kalshi.client import KalshiClient  # noqa: E402

NFL_TICKER_RE = re.compile(r"^KX(NFL|SB|SUPERBOWL|AFC|NFC|MVP|OPOY|DPOY|OROY|DROY|PROBOWL|NFLDRAFT|HEISMAN)", re.I)
NFL_TITLE_RE = re.compile(r"\b(NFL|Super Bowl|AFC|NFC|Pro Bowl|Lombardi|NFL Draft)\b", re.I)
EXCLUDE_RE = re.compile(r"\b(NCAA|College|CFB|CFP|Heisman|XFL|UFL|CFL|Arena|flag football)\b", re.I)
FOOTBALL_RE = re.compile(r"\bfootball\b", re.I)
STATUSES = ("open", "unopened", "closed", "settled")


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, separators=(",", ":"), default=str)


def classify_series(s):
    t = s.get("ticker") or ""
    title = s.get("title") or ""
    cat = s.get("category") or ""
    tags = " ".join(s.get("tags") or []) if isinstance(s.get("tags"), list) else str(s.get("tags") or "")
    ev = []
    if NFL_TICKER_RE.search(t):
        ev.append("ticker_prefix")
    if NFL_TITLE_RE.search(title) and not EXCLUDE_RE.search(title):
        ev.append("title_nfl")
    if re.search(r"\bNFL\b", tags, re.I):
        ev.append("tag_nfl")
    if FOOTBALL_RE.search(title) and not EXCLUDE_RE.search(title) and not ev:
        ev.append("title_football_ambiguous")
    return ev


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ap.add_argument("--rps", type=float, default=4.0)
    ap.add_argument("--max-series", type=int, default=0, help="debug cap")
    ap.add_argument("--statuses", default=",".join(STATUSES))
    ap.add_argument("--skip-markets", action="store_true")
    a = ap.parse_args()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = a.out or os.path.join(ROOT, "data", "kalshi", "discovery", run_id)
    os.makedirs(out, exist_ok=True)
    c = KalshiClient(rps=a.rps)
    summary = {"run_id": run_id, "started_at": datetime.now(timezone.utc).isoformat(), "failures": [], "complete": True}

    st, err = c.try_get("exchange/status")
    summary["exchange_status"] = st or {"error": err}

    # 1. full series catalogue, unfiltered (MLB lesson: category filters miss things)
    series, complete, info = c.series_list(include_product_metadata=True, limit=1000)
    if not complete or not series:
        # retry without product metadata in case the param is rejected
        series2, complete2, info2 = c.series_list(limit=1000)
        if len(series2) > len(series):
            series, complete, info = series2, complete2, info2
    summary["series_total"] = len(series)
    summary["series_complete"] = complete
    summary["series_info"] = info
    if not complete:
        summary["failures"].append({"stage": "series_list", "info": info}); summary["complete"] = False
    dump(os.path.join(out, "series_all.json"), series)

    # also probe category-filtered listing to learn category taxonomy
    cats = {}
    for s in series:
        cats[s.get("category") or "?"] = cats.get(s.get("category") or "?", 0) + 1
    summary["series_by_category"] = cats

    nfl = []
    for s in series:
        ev = classify_series(s)
        if ev:
            nfl.append({**s, "_evidence": ev})
    nfl.sort(key=lambda s: s.get("ticker") or "")
    dump(os.path.join(out, "series_nfl.json"), nfl)
    summary["series_nfl_candidates"] = len(nfl)
    summary["series_nfl_tickers"] = [s["ticker"] for s in nfl]

    # 2. per-series detail, events, markets by status
    per_series = {}
    todo = [s for s in nfl if "title_football_ambiguous" not in s["_evidence"] or len(s["_evidence"]) > 1]
    if a.max_series:
        todo = todo[: a.max_series]
    statuses = [x for x in a.statuses.split(",") if x]
    for s in todo:
        tk = s["ticker"]
        rec = {"ticker": tk}
        detail, err = c.try_get(f"series/{tk}")
        rec["detail"] = detail if detail else {"error": err}
        evs, ok, inf = c.events(series_ticker=tk, limit=200)
        rec["events_n"] = len(evs); rec["events_complete"] = ok
        dump(os.path.join(out, "events", f"{tk}.json"), evs)
        if not a.skip_markets:
            mk = {}
            for status in statuses:
                items, ok2, inf2 = c.markets(series_ticker=tk, status=status, limit=1000, max_pages=200)
                mk[status] = {"n": len(items), "complete": ok2, "info": inf2, "markets": items}
                if not ok2:
                    summary["failures"].append({"stage": "markets", "series": tk, "status": status, "info": inf2}); summary["complete"] = False
            dump(os.path.join(out, "markets", f"{tk}.json"), mk)
            rec["markets_by_status"] = {k: v["n"] for k, v in mk.items()}
        per_series[tk] = rec
        print(json.dumps({k: v for k, v in rec.items() if k != "detail"}), flush=True)
    summary["per_series"] = per_series

    # 3. endpoint probes -------------------------------------------------
    probes = {}
    probes["historical_cutoff"] = c.try_get("historical/cutoff")
    # pick sample markets: one open (prefer KXNFLGAME), one settled
    sample_open = sample_settled = None
    for tk, rec in per_series.items():
        p = os.path.join(out, "markets", f"{tk}.json")
        if not os.path.exists(p):
            continue
        mk = json.load(open(p))
        if sample_open is None and mk.get("open", {}).get("markets"):
            sample_open = mk["open"]["markets"][0]
        if sample_settled is None and mk.get("settled", {}).get("markets"):
            sample_settled = mk["settled"]["markets"][0]
        if sample_open and sample_settled:
            break
    for label, m in (("open", sample_open), ("settled", sample_settled)):
        if not m:
            probes[f"sample_{label}"] = None
            continue
        t = m["ticker"]; s_tk = m.get("series_ticker") or t.split("-")[0]
        now = int(time.time())
        pr = {"ticker": t, "series_ticker": s_tk}
        pr["market_detail"] = c.try_get(f"markets/{t}")
        pr["orderbook"] = c.try_get(f"markets/{t}/orderbook", {"depth": 10})
        tr, ok, inf = c.trades(ticker=t, limit=200, max_pages=2)
        pr["trades"] = {"n": len(tr), "complete": ok, "sample": tr[:5]}
        pr["candles_60"] = c.try_get(f"series/{s_tk}/markets/{t}/candlesticks", {"start_ts": now - 7 * 86400, "end_ts": now, "period_interval": 60})
        pr["candles_1"] = c.try_get(f"series/{s_tk}/markets/{t}/candlesticks", {"start_ts": now - 86400, "end_ts": now, "period_interval": 1})
        pr["candles_1440"] = c.try_get(f"series/{s_tk}/markets/{t}/candlesticks", {"start_ts": now - 120 * 86400, "end_ts": now, "period_interval": 1440})
        pr["historical_market"] = c.try_get(f"historical/markets/{t}")
        pr["historical_candles"] = c.try_get(f"historical/markets/{t}/candlesticks", {"start_ts": now - 120 * 86400, "end_ts": now, "period_interval": 60})
        htr, ok, inf = c.historical_trades(ticker=t, limit=200, max_pages=2)
        pr["historical_trades"] = {"n": len(htr), "complete": ok, "info": inf, "sample": htr[:5]}
        probes[f"sample_{label}"] = pr
    for tk in ("KXNFLGAME", "KXNFLSPREAD", "KXNFLTOTAL"):
        hm, ok, inf = c.historical_markets(series_ticker=tk, limit=1000, max_pages=3)
        probes[f"historical_markets_{tk}"] = {"n": len(hm), "complete": ok, "info": inf, "sample": hm[:3]}
    # global markets sweep by text, to catch NFL tickers under non-NFL series prefixes
    sweep, ok, inf = c.markets(status="open", limit=1000, max_pages=30)
    probes["global_open_sweep"] = {"n": len(sweep), "complete": ok, "info": inf}
    extra = [m for m in sweep if (NFL_TITLE_RE.search(m.get("title") or "") or NFL_TICKER_RE.search(m.get("ticker") or "")) and (m.get("series_ticker") or m["ticker"].split("-")[0]) not in per_series]
    probes["global_open_sweep_extra_nfl"] = {"n": len(extra), "series": sorted({(m.get("series_ticker") or m["ticker"].split("-")[0]) for m in extra}), "sample": extra[:10]}
    dump(os.path.join(out, "probes.json"), probes)

    summary["client_stats"] = c.stats.to_dict()
    summary["finished_at"] = datetime.now(timezone.utc).isoformat()
    dump(os.path.join(out, "summary.json"), summary)
    print(json.dumps({k: v for k, v in summary.items() if k not in ("per_series",)}, indent=1, default=str))
    return 0 if summary["complete"] else 2


if __name__ == "__main__":
    sys.exit(main())
