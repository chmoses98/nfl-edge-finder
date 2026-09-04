#!/usr/bin/env python3
"""Historical Kalshi quote reconstruction: one compact row per settled archived market.

Why not raw candles: 48k settled NFL markets x 1-minute candles is ~70M rows. What the market-efficiency map
actually needs is the executable quote at a set of time-to-kickoff horizons. So per market we make TWO requests
  GET /historical/markets/{t}/candlesticks?period_interval=60  (whole life, capped at 14 days before close)
  GET /historical/markets/{t}/candlesticks?period_interval=1   (final 3 hours)
and keep, for each horizon, the LAST candle at or before that instant: yes_bid/yes_ask close, price close,
volume and open interest. Everything else is discarded.

Anchor: nflverse kickoff when the event ticker joins a scheduled game, else the market's close_time
(`anchor` records which, and every snapshot carries its true `age_min` = how stale the candle is).

Sharding: --shard i --shards n partitions settled markets by a stable hash of the ticker so parallel Actions
runs never touch the same output file. Each shard appends to horizons/<shard>.jsonl and keeps its own state,
so a killed runner loses at most the current chunk.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, os, sys, time, urllib.request
from datetime import datetime, timezone, timedelta

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.kalshi.client import KalshiClient  # noqa
from nfl_edge.kalshi.classifier import classify  # noqa

OUT = os.path.join(ROOT, "data", "kalshi", "backfill")
HORIZ_DIR = os.path.join(OUT, "horizons")
REG_PATH = os.path.join(ROOT, "config", "kalshi_nfl_series.json")
SCHEDULE_URL = "https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv"
# minutes before the anchor
HORIZONS = [("T-168h", 168 * 60), ("T-72h", 72 * 60), ("T-48h", 48 * 60), ("T-24h", 24 * 60), ("T-12h", 12 * 60),
            ("T-6h", 6 * 60), ("T-3h", 180), ("T-90m", 90), ("T-30m", 30), ("T-0", 0)]
PRIORITY = ["KXNFLRECYDS", "KXNFLREC", "KXNFLRSHYDS", "KXNFLPASSYDS", "KXNFLANYTD", "KXNFLTD", "KXNFLPASSTDS", "KXNFLFIRSTTD",
            "KXNFLSPREAD", "KXNFLTOTAL", "KXNFLGAME", "KXNFLTEAMTOTAL", "KXNFLWINMARGIN", "KXNFL1HSPREAD", "KXNFL1HTOTAL"]


def ts(s):
    return int(datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())


def load_kickoffs():
    """(gameday, away, home) -> (kickoff_utc_epoch, game_id, season, week). Cached on disk for offline reruns."""
    cache = os.path.join(OUT, "schedule_cache.csv")
    txt = None
    try:
        req = urllib.request.Request(SCHEDULE_URL, headers={"User-Agent": "nfl-edge-finder backfill"})
        with urllib.request.urlopen(req, timeout=60) as r:
            txt = r.read().decode()
        os.makedirs(OUT, exist_ok=True); open(cache, "w").write(txt)
    except Exception:
        if os.path.exists(cache):
            txt = open(cache).read()
    ko = {}
    if not txt:
        return ko
    for row in csv.DictReader(io.StringIO(txt)):
        if not row.get("gametime"):
            continue
        try:
            d = datetime.strptime(row["gameday"] + " " + row["gametime"], "%Y-%m-%d %H:%M")
        except ValueError:
            continue
        nov1 = datetime(d.year, 11, 1); dst_end = nov1 + timedelta(days=(6 - nov1.weekday()) % 7)
        mar1 = datetime(d.year, 3, 1); dst_start = mar1 + timedelta(days=(6 - mar1.weekday()) % 7 + 7)
        off = 4 if dst_start <= d < dst_end else 5
        k = (d + timedelta(hours=off)).replace(tzinfo=timezone.utc)
        ko[(row["gameday"], row["away_team"], row["home_team"])] = (int(k.timestamp()), row["game_id"], row["season"], row["week"])
    return ko


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def snapshot(candle):
    if not candle:
        return None
    yb = (candle.get("yes_bid") or {}); ya = (candle.get("yes_ask") or {}); pr = (candle.get("price") or {})
    return {"bid": _num(yb.get("close_dollars")), "ask": _num(ya.get("close_dollars")), "last": _num(pr.get("close_dollars")),
            "mean": _num(pr.get("mean_dollars")), "vol": _num(candle.get("volume_fp")), "oi": _num(candle.get("open_interest_fp")),
            "ts": candle.get("end_period_ts")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=6000)
    ap.add_argument("--rps", type=float, default=5.0)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--shards", type=int, default=1)
    ap.add_argument("--series", default="")
    ap.add_argument("--max-life-days", type=int, default=14)
    a = ap.parse_args()
    os.makedirs(HORIZ_DIR, exist_ok=True)
    state_path = os.path.join(HORIZ_DIR, f"state_{a.shard}.json")
    state = json.load(open(state_path)) if os.path.exists(state_path) else {"done": {}, "runs": []}
    out_path = os.path.join(HORIZ_DIR, f"{a.shard}.jsonl")
    reg = json.load(open(REG_PATH))["series"]
    ko = load_kickoffs()
    series = [s for s in reg if reg[s].get("tier") == "FULL_MICROSTRUCTURE"]
    if a.series:
        series = [s for s in a.series.split(",") if s]
    series = [s for s in PRIORITY if s in series] + sorted(s for s in series if s not in PRIORITY)
    c = KalshiClient(rps=a.rps)
    run = {"shard": a.shard, "started_at": datetime.now(timezone.utc).isoformat(), "written": 0, "skipped": 0, "errors": 0}
    todo = []
    for s in series:
        p = os.path.join(OUT, "markets", f"{s}.jsonl")
        if not os.path.exists(p):
            continue
        for line in open(p):
            m = json.loads(line)
            if m.get("result") not in ("yes", "no"):
                continue
            t = m["ticker"]
            if int(hashlib.md5(t.encode()).hexdigest(), 16) % a.shards != a.shard or t in state["done"]:
                continue
            todo.append((m.get("close_time") or "", s, m))
    todo.sort(reverse=True)      # newest first
    run["todo"] = len(todo)
    print(json.dumps({"shard": a.shard, "todo": len(todo), "done_already": len(state["done"])}), flush=True)
    fout = open(out_path, "a")
    for _ct, s, m in todo:
        if c.stats.requests >= a.budget - 3:
            break
        t = m["ticker"]
        sem = classify(m)
        try:
            t_close = ts(m.get("close_time") or m.get("expiration_time"))
            t_open = ts(m.get("open_time") or m.get("created_time"))
        except Exception:
            state["done"][t] = "no_times"; run["skipped"] += 1; continue
        anchor, game_id, season, week = t_close, None, None, None
        anchor_kind = "close_time"
        if sem.game_date and sem.away_team and sem.home_team:
            k = ko.get((sem.game_date, sem.away_team, sem.home_team))
            if k:
                anchor, game_id, season, week = k[0], k[1], k[2], k[3]
                anchor_kind = "kickoff"
        start = max(t_open, anchor - a.max_life_days * 86400)
        h60, e1 = c.try_get(f"historical/markets/{t}/candlesticks", {"start_ts": start, "end_ts": t_close, "period_interval": 60})
        m1, e2 = c.try_get(f"historical/markets/{t}/candlesticks", {"start_ts": max(start, anchor - 3 * 3600), "end_ts": t_close, "period_interval": 1})
        cands = sorted(((h60 or {}).get("candlesticks") or []) + ((m1 or {}).get("candlesticks") or []), key=lambda x: x.get("end_period_ts") or 0)
        if e1 and e2:
            run["errors"] += 1
            state["done"][t] = "error"
            continue
        snaps = {}
        for name, mins in HORIZONS:
            cut = anchor - mins * 60
            prior = [x for x in cands if (x.get("end_period_ts") or 0) <= cut]
            if not prior:
                continue
            sn = snapshot(prior[-1])
            if sn is None:
                continue
            sn["age_min"] = round((cut - sn["ts"]) / 60.0, 1)
            snaps[name] = sn
        row = {"ticker": t, "series": s, "family": sem.family, "period": sem.period, "stat": sem.stat, "team": sem.team,
               "player_name": sem.player_name, "player_kalshi_id": sem.player_kalshi_id, "threshold": sem.threshold,
               "floor_strike": sem.floor_strike, "operator": sem.operator, "game_date": sem.game_date,
               "home_team": sem.home_team, "away_team": sem.away_team, "game_id": game_id, "season": season, "week": week,
               "anchor_ts": anchor, "anchor_kind": anchor_kind, "open_ts": t_open, "close_ts": t_close,
               "result": m.get("result"), "expiration_value": m.get("expiration_value"),
               "final_volume": _num(m.get("volume_fp")), "final_oi": _num(m.get("open_interest_fp")),
               "n_candles": len(cands), "snaps": snaps}
        fout.write(json.dumps(row, separators=(",", ":")) + "\n")
        state["done"][t] = 1
        run["written"] += 1
        if run["written"] % 500 == 0:
            fout.flush(); json.dump(state, open(state_path, "w"), separators=(",", ":"))
            print(json.dumps({"shard": a.shard, "written": run["written"], "requests": c.stats.requests}), flush=True)
    fout.close()
    run["finished_at"] = datetime.now(timezone.utc).isoformat(); run["client_stats"] = c.stats.to_dict()
    run["remaining"] = max(0, len(todo) - run["written"] - run["skipped"])
    state["runs"] = (state.get("runs") or [])[-20:] + [run]
    json.dump(state, open(state_path, "w"), separators=(",", ":"))
    print(json.dumps(run, default=str))
    return 3 if run["remaining"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
