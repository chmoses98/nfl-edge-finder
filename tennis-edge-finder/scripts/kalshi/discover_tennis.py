#!/usr/bin/env python3
"""Kalshi TENNIS market-universe discovery (bronze capture). Read-only public GETs.

Runs inside GitHub Actions (the dev sandbox cannot reach Kalshi). Saves RAW API responses
verbatim so nothing is normalized away. Everything is written under --out
(default data/kalshi/discovery/<run_id>/):

  series_all.json            every series on the exchange (unfiltered, with product metadata)
  series_tennis.json         tennis-classified series with evidence
  series_detail/<S>.json     GET /series/{S}
  events/<S>.json            events per tennis series (all statuses)
  markets/<S>.json           markets per tennis series, per status (open/unopened/closed/settled)
  historical_markets/<S>.json  archived tier markets per series
  candles/<S>/<T>.json       60-min lifetime candles + 1-min last-6h candles per market (budgeted)
  trades/<S>/<T>.json        per-market trades (budgeted)
  rules/<S>.pdf              contract terms PDFs (assets.kalshi.com), when downloadable
  probes.json, summary.json  endpoint probes, counts, fail-closed flags

Phase 1 (catalogue, events, markets, historical markets) always completes first and is
published; phase 2 (candles/trades) is bounded by --budget-minutes and publishes
incrementally so a runner timeout never loses everything.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, PROJ)
from tennis_edge.kalshi.client import KalshiClient  # noqa: E402
from tennis_edge.kalshi.taxonomy import tennis_series  # noqa: E402

STATUSES = ("open", "unopened", "closed", "settled")
# families whose price history matters most for CLV/close research; captured first
PRIORITY_PREFIXES = ("KXATPMATCH", "KXWTAMATCH", "KXATPCHALLENGERMATCH", "KXWTACHALLENGERMATCH", "KXCHALLENGERMATCH",
                     "KXITFMATCH", "KXITFWMATCH", "KXATPGTOTAL", "KXWTAGTOTAL", "KXATPGAMETOTAL", "KXATPGSPREAD",
                     "KXATPGAMESPREAD", "KXATPSETWINNER", "KXWTASETWINNER", "KXATPEXACTMATCH", "KXWTAEXACTMATCH",
                     "KXATPDOUBLES", "KXWTADOUBLES", "KXITFDOUBLES", "KXITFWDOUBLES", "KXATPCHALLENGERDOUBLES",
                     "KXMIXEDDOUBLESMATCH", "KXATPTOTALSETS", "KXATPSSPREAD", "KXATPGAME", "KXWTAGAME")


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".part"
    with open(tmp, "w") as f:
        json.dump(obj, f, separators=(",", ":"), default=str)
    os.replace(tmp, path)


def ts(s):
    if not s:
        return None
    try:
        return int(datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())
    except Exception:
        return None


def publish(out_root, message):
    """Best-effort incremental publish of the discovery directory to the data branch."""
    if os.environ.get("TENNIS_PUBLISH", "0") != "1":
        return
    rel = os.path.relpath(out_root, os.path.abspath(os.path.join(PROJ, "..")))
    cmd = [sys.executable, os.path.join(PROJ, "scripts", "ci", "publish_branch.py"), "--src", rel, "--message", message,
           "--repo", os.path.abspath(os.path.join(PROJ, ".."))]
    print("+ publish:", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ap.add_argument("--rps", type=float, default=5.0)
    ap.add_argument("--statuses", default=",".join(STATUSES))
    ap.add_argument("--budget-minutes", type=float, default=200.0, help="phase-2 (candles/trades) wall budget")
    ap.add_argument("--max-history-markets", type=int, default=25000)
    ap.add_argument("--publish-every-minutes", type=float, default=25.0)
    ap.add_argument("--skip-phase2", action="store_true")
    a = ap.parse_args()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = a.out or os.path.join(PROJ, "data", "kalshi", "discovery", run_id)
    os.makedirs(out, exist_ok=True)
    c = KalshiClient(rps=a.rps)
    summary = {"run_id": run_id, "started_at": datetime.now(timezone.utc).isoformat(), "failures": [], "complete": True}
    st, err = c.try_get("exchange/status")
    summary["exchange_status"] = st or {"error": err}

    # ---- 1. full catalogue, unfiltered
    series, complete, info = c.series_list(include_product_metadata=True, limit=1000)
    if not complete or not series:
        series2, complete2, info2 = c.series_list(limit=1000)
        if len(series2) > len(series):
            series, complete, info = series2, complete2, info2
    summary["series_total"] = len(series); summary["series_complete"] = complete; summary["series_info"] = info
    if not complete:
        summary["failures"].append({"stage": "series_list", "info": info}); summary["complete"] = False
    dump(os.path.join(out, "series_all.json"), series)
    ten = tennis_series(series)
    dump(os.path.join(out, "series_tennis.json"), ten)
    summary["series_tennis"] = len(ten)
    summary["series_tennis_tickers"] = [s["ticker"] for s in ten]
    print(f"tennis series: {len(ten)}", flush=True)

    # ---- 2. per-series detail, events, markets by status, historical markets
    statuses = [x for x in a.statuses.split(",") if x]
    per_series = {}
    all_markets = []  # (series, market) for phase 2
    for s in ten:
        tk = s["ticker"]
        rec = {"ticker": tk}
        detail, err = c.try_get(f"series/{tk}")
        dump(os.path.join(out, "series_detail", f"{tk}.json"), detail if detail else {"error": err})
        evs, ok, inf = c.events(series_ticker=tk, limit=200, max_pages=100)
        rec["events_n"] = len(evs); rec["events_complete"] = ok
        if not ok:
            summary["failures"].append({"stage": "events", "series": tk, "info": inf}); summary["complete"] = False
        dump(os.path.join(out, "events", f"{tk}.json"), evs)
        mk = {}
        for status in statuses:
            items, ok2, inf2 = c.markets(series_ticker=tk, status=status, limit=1000, max_pages=200)
            mk[status] = {"n": len(items), "complete": ok2, "info": inf2, "markets": items}
            if not ok2:
                summary["failures"].append({"stage": "markets", "series": tk, "status": status, "info": inf2}); summary["complete"] = False
            for m in items:
                all_markets.append((tk, status, m))
        dump(os.path.join(out, "markets", f"{tk}.json"), mk)
        rec["markets_by_status"] = {k: v["n"] for k, v in mk.items()}
        hm, ok3, inf3 = c.historical_markets(series_ticker=tk, limit=1000, max_pages=60)
        rec["historical_markets_n"] = len(hm); rec["historical_complete"] = ok3
        dump(os.path.join(out, "historical_markets", f"{tk}.json"), {"n": len(hm), "complete": ok3, "info": inf3, "markets": hm})
        for m in hm:
            all_markets.append((tk, "historical", m))
        per_series[tk] = rec
        print(json.dumps(rec), flush=True)
    summary["per_series"] = per_series
    summary["markets_total_live"] = sum(1 for x in all_markets if x[1] != "historical")
    summary["markets_total_historical"] = sum(1 for x in all_markets if x[1] == "historical")

    # ---- 3. rules PDFs (contract terms) -- best effort, small
    n_pdf = 0
    for s in ten:
        for key in ("contract_terms_url", "contract_url"):
            url = s.get(key)
            if not url or not url.lower().endswith(".pdf"):
                continue
            dest = os.path.join(out, "rules", f"{s['ticker']}.{key}.pdf")
            if os.path.exists(dest):
                continue
            try:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                req = urllib.request.Request(url, headers={"User-Agent": "tennis-edge-finder/0.1 research"})
                with urllib.request.urlopen(req, timeout=30) as r, open(dest, "wb") as f:
                    f.write(r.read())
                n_pdf += 1
            except Exception as e:  # noqa: BLE001
                summary["failures"].append({"stage": "rules_pdf", "series": s["ticker"], "error": str(e)[:200]})
    summary["rules_pdfs"] = n_pdf

    # ---- probes
    probes = {"historical_cutoff": c.try_get("historical/cutoff")}
    sweep, ok, inf = c.markets(status="open", limit=1000, max_pages=60)
    probes["global_open_sweep"] = {"n": len(sweep), "complete": ok, "info": inf}
    known = set(per_series)
    import re
    extra = [m for m in sweep if re.search(r"\b(tennis|ATP|WTA|ITF)\b", (m.get("title") or ""), re.I)
             and (m.get("series_ticker") or m["ticker"].split("-")[0]) not in known]
    probes["global_open_sweep_extra_tennis_like"] = {"n": len(extra), "series": sorted({(m.get("series_ticker") or m["ticker"].split("-")[0]) for m in extra}), "sample": extra[:20]}
    dump(os.path.join(out, "probes.json"), probes)
    summary["phase1_finished_at"] = datetime.now(timezone.utc).isoformat()
    summary["client_stats"] = c.stats.to_dict()
    dump(os.path.join(out, "summary.json"), summary)
    publish(os.path.dirname(out), f"kalshi tennis discovery phase1 {run_id}")

    if a.skip_phase2:
        return 0 if summary["complete"] else 2

    # ---- 4. phase 2: price history per market, budgeted, priority families + most recent first
    def prio(x):
        tk, status, m = x
        p = 0 if tk.startswith(PRIORITY_PREFIXES) else 1
        settled = 0 if status in ("settled", "historical", "closed") else 1
        ct = ts(m.get("close_time")) or 0
        return (settled, p, -ct)
    todo = sorted(all_markets, key=prio)[: a.max_history_markets]
    t_end = time.time() + a.budget_minutes * 60
    last_pub = time.time()
    n_c = n_t = 0
    for i, (tk, status, m) in enumerate(todo):
        if time.time() > t_end:
            summary["phase2_truncated_at_index"] = i
            break
        t = m["ticker"]
        open_ts = ts(m.get("open_time")) or ts(m.get("created_time")) or int(time.time()) - 30 * 86400
        close_ts = ts(m.get("close_time")) or int(time.time())
        close_ts = min(close_ts, int(time.time()))
        rec = {"ticker": t, "series_ticker": tk, "status_at_discovery": status, "captured_at": datetime.now(timezone.utc).isoformat()}
        if status == "historical":
            rec["candles_60"] = c.try_get(f"historical/markets/{t}/candlesticks", {"start_ts": open_ts, "end_ts": close_ts, "period_interval": 60})
            rec["candles_1_last6h"] = c.try_get(f"historical/markets/{t}/candlesticks", {"start_ts": max(open_ts, close_ts - 6 * 3600), "end_ts": close_ts, "period_interval": 1})
            tr, okt, inft = c.historical_trades(ticker=t, limit=1000, max_pages=5)
        else:
            rec["candles_60"] = c.try_get(f"series/{tk}/markets/{t}/candlesticks", {"start_ts": open_ts, "end_ts": close_ts, "period_interval": 60})
            rec["candles_1_last6h"] = c.try_get(f"series/{tk}/markets/{t}/candlesticks", {"start_ts": max(open_ts, close_ts - 6 * 3600), "end_ts": close_ts, "period_interval": 1})
            tr, okt, inft = c.trades(ticker=t, limit=1000, max_pages=5)
        dump(os.path.join(out, "candles", tk, f"{t}.json"), rec)
        dump(os.path.join(out, "trades", tk, f"{t}.json"), {"ticker": t, "n": len(tr), "complete": okt, "info": inft, "trades": tr})
        n_c += 1; n_t += len(tr)
        if time.time() - last_pub > a.publish_every_minutes * 60:
            summary["phase2_progress"] = {"markets_done": n_c, "trades": n_t, "at": datetime.now(timezone.utc).isoformat()}
            dump(os.path.join(out, "summary.json"), summary)
            publish(os.path.dirname(out), f"kalshi tennis discovery phase2 progress {run_id} ({n_c} markets)")
            last_pub = time.time()
    summary["phase2"] = {"markets_with_history": n_c, "trades_rows": n_t, "todo_total": len(todo)}
    summary["client_stats"] = c.stats.to_dict()
    summary["finished_at"] = datetime.now(timezone.utc).isoformat()
    dump(os.path.join(out, "summary.json"), summary)
    publish(os.path.dirname(out), f"kalshi tennis discovery final {run_id}")
    print(json.dumps({k: v for k, v in summary.items() if k not in ("per_series", "series_tennis_tickers")}, indent=1, default=str))
    return 0 if summary["complete"] else 2


if __name__ == "__main__":
    sys.exit(main())
