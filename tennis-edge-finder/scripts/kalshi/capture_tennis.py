#!/usr/bin/env python3
"""Prospective Kalshi TENNIS market capture (one pass). Read-only public GETs. Append-only outputs.

What one pass records (all raw API objects, stamped with run_id and retrieval time):
  quotes.jsonl       every OPEN tennis market (per registered series): the full market record incl. yes/no
                     bid/ask, sizes, last price, volume, OI, liquidity, status, times. A row is written only
                     when the quote fingerprint changed since the last pass (state.json) OR on the hourly
                     full snapshot, so silence never means "unchanged" only when the fingerprint says so.
  books.jsonl        orderbook (depth 10) for open MATCH-scope markets whose scheduled start is within
                     --book-horizon-hours (budgeted, nearest start first).
  trades.jsonl       the GLOBAL trade tape since the last cursor, filtered to tennis tickers -- every tennis
                     trade on the exchange, no per-ticker polling.
  events.jsonl       events first seen this pass (event ticker, title, product_metadata) for lifecycle tracking.
  settlements.jsonl  (hourly sweep) markets settled in the last 3 days per series: ticker, result,
                     settlement_value_dollars, settlement_ts, expiration_value -- EXCHANGE TRUTH, verbatim.
  candles.jsonl      (hourly sweep) for newly-settled match-scope markets: 60-min lifetime candles and 1-min
                     candles for the final 6h before close, so the pre-start quote path is preserved even if
                     the 10-minute polling missed it.
  manifest.json      counts, client stats, incomplete flags (fail-closed reporting).

State (state.json) carries: quote fingerprints, trades cursor, settled tickers already candled, last hourly
sweep time, last discovery time. It is republished with the data so the next runner continues.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, PROJ)
from tennis_edge.kalshi.client import KalshiClient  # noqa: E402
from tennis_edge.kalshi.families import SERIES, FAMILIES  # noqa: E402

MATCH_SCOPE_SERIES = [tk for tk, (fam, *_r) in SERIES.items() if FAMILIES[fam]["scope"] == "MATCH"]
ALL_SERIES = list(SERIES)


def now_utc():
    return datetime.now(timezone.utc)


def ts(s):
    if not s:
        return None
    try:
        return int(datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())
    except Exception:
        return None


def fingerprint(m):
    keys = ("yes_bid_dollars", "yes_ask_dollars", "no_bid_dollars", "no_ask_dollars", "last_price_dollars", "yes_bid_size_fp",
            "yes_ask_size_fp", "volume_fp", "open_interest_fp", "status", "close_time", "liquidity_dollars")
    return hashlib.sha1("|".join(str(m.get(k)) for k in keys).encode()).hexdigest()[:16]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(PROJ, "data", "kalshi", "capture"))
    ap.add_argument("--rps", type=float, default=5.0)
    ap.add_argument("--book-horizon-hours", type=float, default=6.0)
    ap.add_argument("--book-budget", type=int, default=400)
    ap.add_argument("--force-hourly", action="store_true")
    ap.add_argument("--candle-budget", type=int, default=4000, help="max newly-settled markets candled per hourly sweep")
    a = ap.parse_args()
    run_id = now_utc().strftime("%Y%m%dT%H%M%SZ")
    day = run_id[:8]
    day_dir = os.path.join(a.out, f"{day[:4]}-{day[4:6]}-{day[6:]}")
    os.makedirs(day_dir, exist_ok=True)
    state_path = os.path.join(a.out, "state.json")
    state = json.load(open(state_path)) if os.path.exists(state_path) else {}
    state.setdefault("fingerprints", {}); state.setdefault("trades_cursor_ts", None); state.setdefault("candled", {})
    state.setdefault("last_hourly_ts", 0); state.setdefault("events_seen", {})
    c = KalshiClient(rps=a.rps)
    t_now = int(time.time())
    manifest = {"run_id": run_id, "started_at": now_utc().isoformat(), "incomplete": [], "counts": {}}
    hourly = a.force_hourly or (t_now - state["last_hourly_ts"] >= 3600)

    # gzip every stream: a 60-min + 1-min candle dump for a day of settled markets reached 163 MB raw and was
    # rejected by GitHub's 100 MB file limit, which silently lost 5.7 hours of capture on 2026-09-11.
    files = {k: gzip.open(os.path.join(day_dir, f"{run_id}.{k}.jsonl.gz"), "wt", compresslevel=6) for k in ("quotes", "books", "trades", "events", "settlements", "candles")}
    candle_shard = {"n": 0, "idx": 0}

    def w(kind, obj):
        files[kind].write(json.dumps({"run_id": run_id, "captured_at": now_utc().isoformat(), **obj}, separators=(",", ":"), default=str) + "\n")

    # ---- 1. open markets per registered tennis series (quotes)
    open_markets = []
    n_q = n_unch = 0
    for tk in ALL_SERIES:
        items, ok, info = c.markets(series_ticker=tk, status="open", limit=1000, max_pages=20)
        if not ok:
            manifest["incomplete"].append({"stage": "open_markets", "series": tk, "info": info})
        for m in items:
            open_markets.append(m)
            fp = fingerprint(m)
            if hourly or state["fingerprints"].get(m["ticker"]) != fp:
                w("quotes", {"snapshot_kind": "full" if hourly else "changed", **m}); n_q += 1
                state["fingerprints"][m["ticker"]] = fp
            else:
                n_unch += 1
    manifest["counts"]["open_markets"] = len(open_markets); manifest["counts"]["quotes_written"] = n_q; manifest["counts"]["quotes_unchanged"] = n_unch
    # forget fingerprints of markets no longer open (keeps state small)
    live = {m["ticker"] for m in open_markets}
    for t in [t for t in state["fingerprints"] if t not in live]:
        del state["fingerprints"][t]

    # ---- 2. new events
    n_e = 0
    for m in open_markets:
        ev = m.get("event_ticker")
        if ev and ev not in state["events_seen"]:
            body, err = c.try_get(f"events/{ev}", {"with_nested_markets": "false"})
            rec = (body or {}).get("event") or body or {"error": err}
            w("events", {"event_ticker": ev, "event": rec}); n_e += 1
            state["events_seen"][ev] = run_id
    # prune events older than 30 days from state
    cutoff = (now_utc() - timedelta(days=30)).strftime("%Y%m%dT%H%M%SZ")
    for ev in [e for e, r in state["events_seen"].items() if r < cutoff]:
        del state["events_seen"][ev]
    manifest["counts"]["events_new"] = n_e

    # ---- 3. orderbooks for match-scope markets starting soon
    horizon = t_now + int(a.book_horizon_hours * 3600)
    cands = []
    for m in open_markets:
        s_tk = m.get("series_ticker") or m["ticker"].split("-")[0]
        if s_tk not in MATCH_SCOPE_SERIES:
            continue
        start = ts(m.get("occurrence_datetime")) or ts(m.get("expected_expiration_time")) or 0
        if start and start <= horizon:
            cands.append((start, m["ticker"]))
    cands.sort()
    n_b = 0
    for start, t in cands[: a.book_budget]:
        body, err = c.try_get(f"markets/{t}/orderbook", {"depth": 10})
        if body:
            w("books", {"ticker": t, "scheduled_start": start, "orderbook": body})
            n_b += 1
        else:
            manifest["incomplete"].append({"stage": "orderbook", "ticker": t, "error": err})
    manifest["counts"]["books"] = n_b; manifest["counts"]["book_candidates"] = len(cands)

    # ---- 4. global trade tape since cursor, filtered to tennis
    min_ts = state["trades_cursor_ts"] or (t_now - 3600)
    trades, ok, info = c.trades(min_ts=min_ts, max_ts=t_now, limit=1000, max_pages=40)
    if not ok:
        manifest["incomplete"].append({"stage": "trades", "info": info})
    prefixes = tuple(s + "-" for s in ALL_SERIES)
    n_t = 0
    for tr in trades:
        if (tr.get("ticker") or "").startswith(prefixes):
            w("trades", tr); n_t += 1
    if ok:
        state["trades_cursor_ts"] = t_now
    manifest["counts"]["trades_tennis"] = n_t; manifest["counts"]["trades_global_scanned"] = len(trades)

    # ---- 5. hourly: settlements + candles for newly settled match-scope markets
    n_s = n_c = 0
    if hourly:
        since = t_now - 3 * 86400
        for tk in ALL_SERIES:
            items, ok, info = c.markets(series_ticker=tk, status="settled", min_close_ts=since, limit=1000, max_pages=10)
            if not ok:
                manifest["incomplete"].append({"stage": "settled", "series": tk, "info": info})
            for m in items:
                key = m["ticker"]
                if state["candled"].get(key):
                    continue
                w("settlements", {k: m.get(k) for k in ("ticker", "event_ticker", "series_ticker", "status", "result", "expiration_value",
                                                         "settlement_value_dollars", "settlement_ts", "close_time", "open_time",
                                                         "occurrence_datetime", "expected_expiration_time", "volume_fp", "open_interest_fp", "last_price_dollars")})
                n_s += 1
                if tk in MATCH_SCOPE_SERIES and n_c < a.candle_budget:
                    o = ts(m.get("open_time")) or since; cl = min(ts(m.get("close_time")) or t_now, t_now)
                    c60, e1 = c.try_get(f"series/{tk}/markets/{key}/candlesticks", {"start_ts": o, "end_ts": cl, "period_interval": 60})
                    c1, e2 = c.try_get(f"series/{tk}/markets/{key}/candlesticks", {"start_ts": max(o, cl - 3 * 3600), "end_ts": cl, "period_interval": 1})
                    # keep only the candle arrays (drop per-response _meta noise) to bound size
                    rec = {"ticker": key, "series_ticker": tk, "open_ts": o, "close_ts": cl,
                           "candles_60": (c60 or {}).get("candlesticks", {"error": e1}), "candles_1_last3h": (c1 or {}).get("candlesticks", {"error": e2})}
                    w("candles", rec)
                    n_c += 1
                    candle_shard["n"] += 1
                    if candle_shard["n"] >= 1500:   # ~1500 markets per shard keeps each gz file far below 100 MB
                        files["candles"].close(); candle_shard["idx"] += 1; candle_shard["n"] = 0
                        files["candles"] = gzip.open(os.path.join(day_dir, f"{run_id}.candles.{candle_shard['idx']}.jsonl.gz"), "wt", compresslevel=6)
                state["candled"][key] = run_id
        # prune candled older than 10 days
        cut = (now_utc() - timedelta(days=10)).strftime("%Y%m%dT%H%M%SZ")
        for k in [k for k, r in state["candled"].items() if r < cut]:
            del state["candled"][k]
        state["last_hourly_ts"] = t_now
    manifest["counts"]["settlements"] = n_s; manifest["counts"]["candles"] = n_c; manifest["hourly_sweep"] = hourly

    for f in files.values():
        f.close()
    for fn in os.listdir(day_dir):
        if fn.startswith(run_id) and fn.endswith(".jsonl.gz"):
            p = os.path.join(day_dir, fn)
            with gzip.open(p, "rb") as g:
                empty = g.read(1) == b""
            if empty:
                os.remove(p)
    manifest["client_stats"] = c.stats.to_dict(); manifest["finished_at"] = now_utc().isoformat()
    with open(os.path.join(day_dir, f"{run_id}.manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    with open(state_path, "w") as f:
        json.dump(state, f, separators=(",", ":"))
    print(json.dumps({k: v for k, v in manifest.items() if k != "client_stats"}, default=str))
    return 0 if not manifest["incomplete"] else 2


if __name__ == "__main__":
    sys.exit(main())
