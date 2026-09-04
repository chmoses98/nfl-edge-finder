#!/usr/bin/env python3
"""Prospective Kalshi NFL market capture (runs in GitHub Actions every ~10 min).

Design (see docs/KALSHI_CAPTURE.md):
  * Universe = config/kalshi_nfl_series.json (reviewed registry). Series in the
    registry are polled per tier; unknown new series are noticed by the daily
    discovery job, not here (capture must stay cheap and predictable).
  * Every run: GET /markets?series_ticker=S&status=open for every FULL + LIGHT
    series (DAILY series only in the first run after 09:00 UTC). One request per
    series per page; ~130 requests/run.
  * Quote rows are CHANGE-SUPPRESSED: a row is written only when the price
    fingerprint (yes_bid, yes_ask, last, volume, open_interest, status) differs
    from the last one in state.json. Unchanged markets are counted in the run
    manifest so the universe is still reconstructible.
  * Order books (depth 10) are captured for FULL-tier markets whose game
    (from the event ticker date + nflverse schedule kickoff) is within
    BOOK_WINDOW_HOURS of kickoff and not yet started -- the pregame dataset.
    Post-kickoff observations are flagged `live=true` and written to a separate
    file (live-market research table) and never mixed into pregame rows.
  * Trades: the global tape GET /markets/trades?min_ts=<last run> paginated,
    filtered to registry series -> every NFL trade exchange-wide, no per-ticker
    polling.
  * Output (append-only, one file set per run):
      data/kalshi/capture/<YYYY-MM-DD>/<run_id>.quotes.jsonl
      data/kalshi/capture/<YYYY-MM-DD>/<run_id>.books.jsonl
      data/kalshi/capture/<YYYY-MM-DD>/<run_id>.live.jsonl
      data/kalshi/capture/<YYYY-MM-DD>/<run_id>.trades.jsonl
      data/kalshi/capture/<YYYY-MM-DD>/<run_id>.manifest.json
      data/kalshi/capture/state.json   (fingerprints + trade cursor)
  A failed series fetch is recorded in the manifest as PARTIAL; it is never an
  empty universe.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, os, sys, time, urllib.request
from datetime import datetime, timezone, timedelta

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.kalshi.client import KalshiClient  # noqa
from nfl_edge.kalshi.classifier import classify, KALSHI_TO_NFLVERSE  # noqa

REG_PATH = os.path.join(ROOT, "config", "kalshi_nfl_series.json")
OUT_ROOT = os.path.join(ROOT, "data", "kalshi", "capture")
SCHEDULE_URL = "https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv"
BOOK_WINDOW_HOURS = 72.0
QUOTE_FIELDS = ["yes_bid_dollars", "yes_ask_dollars", "no_bid_dollars", "no_ask_dollars", "last_price_dollars", "volume_fp",
                "open_interest_fp", "liquidity_dollars", "yes_bid_size_fp", "yes_ask_size_fp", "status", "result", "close_time"]
ET = timezone(timedelta(hours=-4))  # nflverse gametime is US/Eastern; EDT during Sep-early Nov, EST after. Handled below.


def now_utc():
    return datetime.now(timezone.utc)


def load_schedule(cache_path):
    """Kickoff times (UTC) keyed by (date, away_nflverse, home_nflverse). Falls back to cache if download fails."""
    txt = None
    try:
        req = urllib.request.Request(SCHEDULE_URL, headers={"User-Agent": "nfl-edge-finder capture"})
        with urllib.request.urlopen(req, timeout=60) as r:
            txt = r.read().decode()
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        open(cache_path, "w").write(txt)
        src = "download"
    except Exception as e:  # noqa
        if os.path.exists(cache_path):
            txt = open(cache_path).read(); src = "cache"
        else:
            return {}, "unavailable"
    ko = {}
    for row in csv.DictReader(io.StringIO(txt)):
        if not row.get("gametime"):
            continue
        try:
            d = datetime.strptime(row["gameday"] + " " + row["gametime"], "%Y-%m-%d %H:%M")
        except ValueError:
            continue
        # US Eastern offset: DST ends first Sunday of November
        year = d.year
        nov1 = datetime(year, 11, 1)
        dst_end = nov1 + timedelta(days=(6 - nov1.weekday()) % 7)
        mar1 = datetime(year, 3, 1)
        dst_start = mar1 + timedelta(days=(6 - mar1.weekday()) % 7 + 7)
        offset = 4 if dst_start <= d < dst_end else 5
        kickoff = (d + timedelta(hours=offset)).replace(tzinfo=timezone.utc)
        ko[(row["gameday"], row["away_team"], row["home_team"])] = {"kickoff_utc": kickoff.isoformat(), "game_id": row["game_id"], "season": row["season"], "week": row["week"]}
    return ko, src


def fingerprint(m):
    return hashlib.sha1("|".join(str(m.get(k)) for k in QUOTE_FIELDS).encode()).hexdigest()[:16]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rps", type=float, default=5.0)
    ap.add_argument("--book-window-hours", type=float, default=BOOK_WINDOW_HOURS)
    ap.add_argument("--max-books", type=int, default=2500)
    ap.add_argument("--force-daily", action="store_true")
    ap.add_argument("--trigger-source", default=os.environ.get("TRIGGER_SOURCE", "unknown"))
    a = ap.parse_args()
    t_start = now_utc(); run_id = t_start.strftime("%Y%m%dT%H%M%SZ")
    day_dir = os.path.join(OUT_ROOT, t_start.strftime("%Y-%m-%d")); os.makedirs(day_dir, exist_ok=True)
    state_path = os.path.join(OUT_ROOT, "state.json")
    state = json.load(open(state_path)) if os.path.exists(state_path) else {"fingerprints": {}, "trades_cursor_ts": None, "last_daily_run": None}
    reg = json.load(open(REG_PATH))["series"]
    sched, sched_src = load_schedule(os.path.join(OUT_ROOT, "schedule_cache.csv"))
    c = KalshiClient(rps=a.rps)
    manifest = {"run_id": run_id, "started_at": t_start.isoformat(), "trigger_source": a.trigger_source, "schedule_source": sched_src,
                "series": {}, "partial": False, "errors": []}
    do_daily = a.force_daily or (state.get("last_daily_run") or "")[:10] != t_start.strftime("%Y-%m-%d")
    quotes_f = open(os.path.join(day_dir, f"{run_id}.quotes.jsonl"), "w")
    books_f = open(os.path.join(day_dir, f"{run_id}.books.jsonl"), "w")
    live_f = open(os.path.join(day_dir, f"{run_id}.live.jsonl"), "w")
    trades_f = open(os.path.join(day_dir, f"{run_id}.trades.jsonl"), "w")
    n_quotes = n_unchanged = n_books = n_live = n_trades = 0
    book_candidates = []
    seen_now = set()
    for tk, rec in reg.items():
        tier = rec.get("tier", "LIGHT")
        if tier == "NOT_CAPTURED":
            continue
        if tier == "DAILY" and not do_daily:
            continue
        items, complete, info = c.markets(series_ticker=tk, status="open", limit=1000, max_pages=20)
        manifest["series"][tk] = {"n": len(items), "complete": complete, "tier": tier}
        if not complete:
            manifest["partial"] = True; manifest["errors"].append({"series": tk, "info": info})
        obs_ts = now_utc().isoformat()
        for m in items:
            sem = classify(m)
            fp = fingerprint(m)
            seen_now.add(m["ticker"])
            kick = None
            if sem.game_date and sem.away_team and sem.home_team:
                kick = sched.get((sem.game_date, sem.away_team, sem.home_team))
            minutes_to_kick = None
            if kick:
                minutes_to_kick = (datetime.fromisoformat(kick["kickoff_utc"]) - now_utc()).total_seconds() / 60.0
            row = {"run_id": run_id, "observed_at": obs_ts, "ticker": m["ticker"], "event_ticker": m.get("event_ticker"), "series_ticker": tk,
                   "family": sem.family, "period": sem.period, "stat": sem.stat, "team": sem.team, "player_name": sem.player_name,
                   "player_kalshi_id": sem.player_kalshi_id, "threshold": sem.threshold, "operator": sem.operator, "floor_strike": sem.floor_strike,
                   "game_id": kick["game_id"] if kick else None, "kickoff_utc": kick["kickoff_utc"] if kick else None,
                   "minutes_to_kickoff": round(minutes_to_kick, 1) if minutes_to_kick is not None else None,
                   "pregame": (minutes_to_kick is None) or (minutes_to_kick > 0),
                   "fingerprint": fp, "changed": state["fingerprints"].get(m["ticker"]) != fp,
                   **{k: m.get(k) for k in QUOTE_FIELDS}, "open_time": m.get("open_time"), "expected_expiration_time": m.get("expected_expiration_time")}
            if row["changed"]:
                quotes_f.write(json.dumps(row, separators=(",", ":")) + "\n"); n_quotes += 1
                state["fingerprints"][m["ticker"]] = fp
            else:
                n_unchanged += 1
            if tier == "FULL_MICROSTRUCTURE" and minutes_to_kick is not None and minutes_to_kick <= a.book_window_hours * 60:
                book_candidates.append((minutes_to_kick, m["ticker"], row["pregame"]))
    # order books: closest kickoffs first, capped per run
    book_candidates.sort()
    for minutes_to_kick, ticker, pregame in book_candidates[: a.max_books]:
        body, err = c.try_get(f"markets/{ticker}/orderbook", {"depth": 10})
        obs = {"run_id": run_id, "observed_at": now_utc().isoformat(), "ticker": ticker, "minutes_to_kickoff": round(minutes_to_kick, 1),
               "orderbook_fp": (body or {}).get("orderbook_fp"), "error": err}
        if pregame:
            books_f.write(json.dumps(obs, separators=(",", ":")) + "\n"); n_books += 1
        else:
            live_f.write(json.dumps(obs, separators=(",", ":")) + "\n"); n_live += 1
    manifest["books_requested"] = min(len(book_candidates), a.max_books); manifest["books_candidates"] = len(book_candidates)
    # trades: global tape since last cursor (bounded), keep NFL series
    min_ts = state.get("trades_cursor_ts") or int((t_start - timedelta(minutes=30)).timestamp())
    trades, complete, info = c.trades(min_ts=min_ts, limit=1000, max_pages=40)
    manifest["trades"] = {"fetched": len(trades), "complete": complete, "min_ts": min_ts}
    max_seen = min_ts
    for t in trades:
        series = (t.get("ticker") or "").split("-")[0]
        try:
            ts = int(datetime.fromisoformat(t["created_time"].replace("Z", "+00:00")).timestamp())
        except Exception:
            ts = None
        if ts and ts > max_seen:
            max_seen = ts
        if series in reg:
            trades_f.write(json.dumps({"run_id": run_id, **t}, separators=(",", ":")) + "\n"); n_trades += 1
    if complete:
        state["trades_cursor_ts"] = max_seen
    # markets that vanished from `open` since last run (closed/settled): drop fingerprint so a reappearance is written
    for tk in list(state["fingerprints"]):
        if tk not in seen_now and not do_daily:
            pass  # keep; the daily discovery job records settlements. Fingerprints are cheap.
    if do_daily:
        state["last_daily_run"] = t_start.isoformat()
    for f in (quotes_f, books_f, live_f, trades_f):
        f.close()
    for name, n in (("quotes", n_quotes), ("books", n_books), ("live", n_live), ("trades", n_trades)):
        p = os.path.join(day_dir, f"{run_id}.{name}.jsonl")
        if n == 0 and os.path.exists(p):
            os.remove(p)
    manifest.update({"quotes_written": n_quotes, "quotes_unchanged": n_unchanged, "books_written": n_books, "live_books_written": n_live,
                     "trades_written": n_trades, "daily_tier_included": do_daily, "client_stats": c.stats.to_dict(),
                     "finished_at": now_utc().isoformat(), "seconds": (now_utc() - t_start).total_seconds()})
    json.dump(manifest, open(os.path.join(day_dir, f"{run_id}.manifest.json"), "w"), separators=(",", ":"))
    json.dump(state, open(state_path, "w"), separators=(",", ":"))
    print(json.dumps({k: v for k, v in manifest.items() if k != "series"}, default=str))
    return 0 if not manifest["partial"] else 2


if __name__ == "__main__":
    sys.exit(main())
