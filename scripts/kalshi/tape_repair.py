#!/usr/bin/env python3
"""Recover PRE-START trade tape past the old 10,000-print cap, resumably, with an audited completeness status per ticker (#246).

Reads ``data/kalshi/backfill/markets/<SERIES>.jsonl`` (settled archived markets), anchors each ticker at KICKOFF (nflverse schedule: classifier join, else the (date,away,home) encoded in the ticker when it matches exactly one
game; recorded as ``anchor_kind``). A ticker with no kickoff anchor is NEVER fetched (market close_time can be days after the game, which would put
in-game prints in a 'pre-start' tape); it is listed under tape_state.json ``unanchored`` instead. Pages ``GET /historical/trades?ticker&max_ts=<anchor>`` newest->oldest until the
cursor is exhausted, and writes ADDITIVE files only (the published ``trades/`` feed is untouched):
  data/kalshi/backfill/trades_v2/<SERIES>/<TICKER>.jsonl    de-duplicated pre-start prints, append-only
  data/kalshi/backfill/tape_meta.jsonl                      one audit row per attempt (status, pages, cursor, oldest/newest, candle check, source gap)
  data/kalshi/backfill/tape_state.json                      resume cursors (a failed page is retried, never skipped)
Bounded: ``--budget`` HTTP requests per run, ``--page-budget`` pages per ticker per run; exit 3 when work remains (workflow may chain).
Read-only: public GET endpoints only; no order surface.
"""
from __future__ import annotations
import argparse, json, os, re, sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.kalshi import tape as T                      # noqa: E402

OUT = os.path.join(ROOT, "data", "kalshi", "backfill")
PRIORITY = ["KXNFLGAME", "KXNFLSPREAD", "KXNFLTOTAL", "KXNFLTEAMTOTAL", "KXNFL1HSPREAD", "KXNFL1HTOTAL", "KXNFL1HWINNER", "KXNFLPASSYDS", "KXNFLRECYDS", "KXNFLRSHYDS", "KXNFLTD"]


def existing_ids(path):
    ids = set()
    if os.path.exists(path):
        for l in open(path):
            try:
                ids.add(json.loads(l)["trade_id"])
            except (ValueError, KeyError):
                pass
    return ids


_TICKER = re.compile(r"^[A-Z0-9]+-(\d\d)([A-Z]{3})(\d\d)([A-Z]+)(?:-|$)")
_ALIAS = {"JAC": "JAX"}          # Kalshi ticker code -> nflverse code
_MON = {m: i for i, m in enumerate("JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split(), 1)}


def kickoff_from_ticker(ticker, kickoffs):
    """Kickoff for ``KXNFLGAME-26JAN25LASEA-SEA`` from the (date, away, home) in the ticker, when EXACTLY ONE split of the team letters matches a scheduled
    game on that date (else the day before: Kalshi dates by UTC, so late games carry the next day).  The shared classifier cannot split ambiguous codes
    like ``LASEA`` (LA vs LAC).  Returns (kickoff_epoch, "kickoff_ticker_parse") or None; never guesses between candidates."""
    m = _TICKER.match(ticker or "")
    if not m or m.group(2) not in _MON:
        return None
    from datetime import date, timedelta
    d0 = date(2000 + int(m.group(1)), _MON[m.group(2)], int(m.group(3)))
    letters = m.group(4)
    for d in (d0, d0 - timedelta(days=1)):
        hits = {(d.isoformat(), _ALIAS.get(letters[:i], letters[:i]), _ALIAS.get(letters[i:], letters[i:])) for i in range(2, len(letters) - 1)} & set(kickoffs)
        if len(hits) == 1:
            return kickoffs[hits.pop()][0], "kickoff_ticker_parse"
        if len(hits) > 1:
            return None
    return None


def anchor_for(m, kickoffs, classify):
    """(anchor_ts, anchor_kind) at KICKOFF, or (None, None) when no kickoff can be established -- never market close_time."""
    sem = classify(m)
    if sem.game_date and sem.away_team and sem.home_team:
        k = kickoffs.get((sem.game_date, sem.away_team, sem.home_team))
        if k:
            return k[0], "kickoff"
    r = kickoff_from_ticker(m.get("ticker"), kickoffs)
    return r if r else (None, None)


def _nonempty(path):
    return os.path.exists(path) and os.path.getsize(path) > 0


def run(client, *, out, series, markets_by_series, kickoffs, classify, budget, page_budget, max_tickers=0, limit=1000):
    state_path = os.path.join(out, "tape_state.json")
    state = T.load_state(state_path)
    todo, unanchored = [], {}
    for s in series:
        for m in markets_by_series.get(s, []):
            if m.get("result") not in ("yes", "no"):
                continue
            t = m["ticker"]
            anchor, kind = anchor_for(m, kickoffs, classify)
            if anchor is None:
                unanchored[t] = "no_kickoff_anchor"            # not fetched: a close_time anchor would admit post-kickoff prints
                continue
            prev = state["tickers"].get(t, {})
            if prev.get("anchor_ts") not in (None, anchor) and _nonempty(os.path.join(out, "trades_v2", s, f"{t}.jsonl")):
                unanchored[t] = "anchor_changed_with_data_on_disk"      # never mix tapes cut at two different anchors
                continue
            # a result recorded under a close_time anchor (earlier collector) is not trusted as pregame: redo it at the kickoff anchor
            if prev.get("status") in ("COMPLETE", "COMPLETE_WITH_SOURCE_GAP") and prev.get("anchor_kind") != "close_time" and prev.get("anchor_ts") in (None, anchor):
                continue
            todo.append((s, m, anchor, kind))
    todo.sort(key=lambda x: (PRIORITY.index(x[0]) if x[0] in PRIORITY else 99, -(T.to_ts(x[1].get("close_time")) or 0)))
    run_rec = dict(started_at=datetime.now(timezone.utc).isoformat(), todo=len(todo), no_kickoff_anchor=len(unanchored), tickers_attempted=0, complete=0, incomplete=0, trades_written=0)
    os.makedirs(out, exist_ok=True)
    for s, m, anchor, kind in todo:
        if client.stats.requests >= budget - 3 or (max_tickers and run_rec["tickers_attempted"] >= max_tickers):
            break
        t = m["ticker"]
        open_ts = T.to_ts(m.get("open_time") or m.get("created_time"))
        d = os.path.join(out, "trades_v2", s); os.makedirs(d, exist_ok=True)
        fpath = os.path.join(d, f"{t}.jsonl")
        prev = state["tickers"].get(t, {})
        r = T.fetch_tape(client, t, anchor_ts=anchor, market_open_ts=open_ts, resume_cursor=(prev.get("cursor") if prev.get("anchor_ts") == anchor else None), page_budget=page_budget,
                         limit=limit, known_ids=existing_ids(fpath))
        with open(fpath, "a") as f:
            for x in r.trades:
                f.write(json.dumps(x, separators=(",", ":")) + "\n")
        # candle verification needs the WHOLE tape: only when this run completed it
        ver = None
        if r.tape_complete:
            cpath = os.path.join(out, "candles", s, f"{t}.json")
            candles = (json.load(open(cpath)).get("h60") if os.path.exists(cpath) else None)
            if candles is None:
                body, _ = client.try_get(f"historical/markets/{t}/candlesticks", {"start_ts": open_ts, "end_ts": anchor, "period_interval": 60})
                candles = (body or {}).get("candlesticks")
            alltr = [json.loads(l) for l in open(fpath)]
            ver = T.hourly_candle_vs_tape(candles or [], alltr, anchor)
        row = T.final_status(r, ver)
        row.update(series=s, anchor_kind=kind, run_started_at=run_rec["started_at"], total_prints_on_disk=sum(1 for _ in open(fpath)))
        with open(os.path.join(out, "tape_meta.jsonl"), "a") as f:
            f.write(json.dumps(row, separators=(",", ":")) + "\n")
        state["tickers"][t] = dict(status=row["status"], cursor=r.cursor, n=row["total_prints_on_disk"], oldest_ts=r.oldest_ts or prev.get("oldest_ts"),
                                   newest_ts=r.newest_ts or prev.get("newest_ts"), anchor_ts=anchor, anchor_kind=kind)
        run_rec["tickers_attempted"] += 1; run_rec["trades_written"] += len(r.trades)
        run_rec["complete" if r.tape_complete else "incomplete"] += 1
        T.save_state(state_path, state)          # after EVERY ticker: a killed runner loses at most the current ticker
    run_rec["finished_at"] = datetime.now(timezone.utc).isoformat(); run_rec["client_stats"] = client.stats.to_dict()
    remaining = sum(1 for s, m, _a, _k in todo if state["tickers"].get(m["ticker"], {}).get("status") not in ("COMPLETE", "COMPLETE_WITH_SOURCE_GAP"))
    run_rec["remaining"] = remaining
    state["unanchored"] = unanchored
    state["runs"].append(run_rec)
    T.save_state(state_path, state)
    return run_rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", default=",".join(PRIORITY[:4]))
    ap.add_argument("--budget", type=int, default=20000); ap.add_argument("--page-budget", type=int, default=200)
    ap.add_argument("--rps", type=float, default=5.0); ap.add_argument("--max-tickers", type=int, default=0)
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    from nfl_edge.kalshi.client import KalshiClient
    from nfl_edge.kalshi.classifier import classify
    sys.path.insert(0, os.path.join(ROOT, "scripts", "kalshi"))
    from backfill_quotes import load_kickoffs
    series = [s for s in a.series.split(",") if s]
    mk = {}
    for s in series:
        p = os.path.join(a.out, "markets", f"{s}.jsonl")
        mk[s] = [json.loads(l) for l in open(p)] if os.path.exists(p) else []
    if not any(mk.values()):
        print(json.dumps(dict(error="MARKETS_MISSING", detail=f"no settled-market files for {series} under {a.out}/markets; nothing to repair "
                                    "(restore markets/ from market-data first)")))
        return 2
    rec = run(KalshiClient(rps=a.rps), out=a.out, series=series, markets_by_series=mk, kickoffs=load_kickoffs(), classify=classify,
              budget=a.budget, page_budget=a.page_budget, max_tickers=a.max_tickers)
    print(json.dumps(rec, default=str))
    return 3 if rec["remaining"] else 0


if __name__ == "__main__":
    sys.exit(main())
