#!/usr/bin/env python3
"""Recover PRE-START trade tape past the old 10,000-print cap, resumably, with an audited completeness status per ticker (#246).

Reads ``data/kalshi/backfill/markets/<SERIES>.jsonl`` (settled archived markets), anchors each ticker at KICKOFF (nflverse schedule: classifier join, else the (date,away,home) encoded in the ticker when it matches exactly one
game; recorded as ``anchor_kind``). A ticker with no kickoff anchor is NEVER fetched (market close_time can be days after the game, which would put
in-game prints in a 'pre-start' tape); it is listed under tape_state.json ``unanchored`` instead. Pages ``GET /historical/trades?ticker&max_ts=<anchor>`` newest->oldest until the
cursor is exhausted, and writes ADDITIVE files only (the published ``trades/`` feed is untouched):
  data/kalshi/backfill/trades_v2/<SERIES>/<TICKER>.jsonl    de-duplicated pre-start prints, append-only
  data/kalshi/backfill/tape_meta.jsonl                      one audit row per attempt (status, pages, cursor, oldest/newest, candle check, source gap)
  data/kalshi/backfill/tape_state.json                      resume cursors (a failed page is retried, never skipped)
Tiers: historical/trades first; an empty first page falls back to the live markets/trades (recorded as ``tier`` / ``tiers_checked``).
Efficiency / ordering: only the tickers a run actually touches are restored from market-data (``--restore-ref``; lazy, per ticker) and only those files are
published (``publish_manifest.txt``).  Order: legacy tapes capped at 10,000 prints first (``legacy_manifest.json``), then contracts that have a two-sided pre-start
quote (the only ones Alpha can evaluate), round-robin across families by least coverage, contracts with no quote last (``--per-series`` caps a family per run).
Candles (h60 + last-24h m1) are stored in ``candles_v2/`` for contracts with no legacy candle file, so non-moneyline families are evaluable.
Bounded: ``--budget`` HTTP requests per run, ``--page-budget`` pages per ticker per run; exit 3 when work remains (workflow may chain).
Read-only: public GET endpoints only; no order surface.
"""
from __future__ import annotations
import argparse, glob, json, os, re, subprocess, sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.kalshi import tape as T                      # noqa: E402

OUT = os.path.join(ROOT, "data", "kalshi", "backfill")
HIST, LIVE = "historical/trades", "markets/trades"        # Kalshi serves archived markets from historical/*, recent ones only from the live tier
MAX_THROTTLE = 8                  # 429 + 5xx responses tolerated in one run before it stops (rc 5, never chained)
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


def _is_done(st):
    return st.get("status") in ("COMPLETE", "COMPLETE_WITH_SOURCE_GAP")


def order_todo(todo, state, manifest=None, quotes=None, per_series=0):
    """Pure ordering of ``todo`` = [(series, market, anchor, kind)].  1) legacy tapes capped at 10,000 prints (manifest), 2) contracts with a two-sided
    pre-start quote, interleaved across families, least-covered family first, 3) contracts with no quote.  ``per_series`` caps a family in groups 2+3 (not 1)."""
    manifest = manifest or {}
    def close(x):
        return -(T.to_ts(x[1].get("close_time")) or 0)
    capped = sorted((x for x in todo if (manifest.get(x[1]["ticker"]) or {}).get("capped")), key=close)
    rest = [x for x in todo if not (manifest.get(x[1]["ticker"]) or {}).get("capped")]
    total, got = {}, {}
    for s_, m_, _a, _k in todo:
        total[s_] = total.get(s_, 0) + 1
    for t, st in state["tickers"].items():
        if _is_done(st) and st.get("n"):
            got[t.split("-")[0]] = got.get(t.split("-")[0], 0) + 1
    ratio = lambda s_: got.get(s_, 0) / float(got.get(s_, 0) + total.get(s_, 1))
    def groups(has_quote):
        by = {}
        for x in sorted((y for y in rest if (quotes is None or (y[1]["ticker"] in quotes) == has_quote)), key=close):
            by.setdefault(x[0], []).append(x)
        return by
    out = list(capped)
    taken = {}
    for has_quote in ([True, False] if quotes is not None else [True]):
        by = groups(has_quote)
        fams = sorted(by, key=lambda f: (ratio(f), PRIORITY.index(f) if f in PRIORITY else 99))
        i = 0
        while any(by[f] for f in fams):
            for f in fams:
                if by[f]:
                    x = by[f].pop(0)
                    if per_series and taken.get(f, 0) >= per_series:
                        by[f].clear(); continue
                    taken[f] = taken.get(f, 0) + 1
                    out.append(x)
            i += 1
    return out


def git_restorer(ref, out, root=ROOT):
    """fetch_existing(rel) -> bool: materialise ONE published file (path relative to ``out``) from ``ref`` if it is not on disk yet."""
    def restore(rel):
        dst = os.path.join(out, rel)
        if os.path.exists(dst):
            return True
        r = subprocess.run(["git", "show", f"{ref}:{os.path.relpath(dst, root)}"], cwd=root, capture_output=True)
        if r.returncode != 0:
            return False
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "wb") as f:
            f.write(r.stdout)
        return True
    return restore


def fetch_candles(client, s, t, open_ts, anchor, tier):
    """(h60 list|None, m1 list|None) from the tier's candlestick route (historical/* 404s for live-tier markets, so try both, own tier first)."""
    routes = [f"historical/markets/{t}/candlesticks", f"series/{s}/markets/{t}/candlesticks"]
    out = {}
    for name, per, start in (("h60", 60, open_ts), ("m1", 1, max(open_ts or 0, anchor - 86400))):
        out[name] = None
        for route in (routes if tier == "historical" else routes[::-1]):
            body, _ = client.try_get(route, {"start_ts": start, "end_ts": anchor, "period_interval": per})
            if (body or {}).get("candlesticks") is not None:
                out[name] = body["candlesticks"]
                break
    return out["h60"], out["m1"]


def run(client, *, out, series, markets_by_series, kickoffs, classify, budget, page_budget, max_tickers=0, limit=1000, per_series=0, manifest=None, quotes=None,
        fetch_existing=None, max_throttle=MAX_THROTTLE, max_candle_jobs=40):
    state_path = os.path.join(out, "tape_state.json")
    state = T.load_state(state_path)
    todo, unanchored, candle_jobs = [], {}, []
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
            # a result recorded under a close_time anchor (earlier collector) is not trusted as pregame: redo it at the kickoff anchor
            empty_unchecked = prev.get("n") == 0 and "live" not in (prev.get("tiers_checked") or [])      # complete-and-empty seen by the historical tier only
            if prev.get("status") in ("COMPLETE", "COMPLETE_WITH_SOURCE_GAP") and prev.get("anchor_kind") != "close_time" and prev.get("anchor_ts") in (None, anchor) and not empty_unchecked:
                if prev.get("n") and not prev.get("candles") and not (manifest or {}).get(t, {}).get("has_candles"):
                    candle_jobs.append((s, m, anchor, kind))      # tape done, but no quotes stored for it yet: a 2-request candle-only job
                continue
            todo.append((s, m, anchor, kind))
    todo = order_todo(todo, state, manifest, quotes, per_series)
    run_rec = dict(started_at=datetime.now(timezone.utc).isoformat(), todo=len(todo), no_kickoff_anchor=len(unanchored), tickers_attempted=0, complete=0, incomplete=0, trades_written=0, restore_failed=0, candle_only=0, stopped=None)
    touched = []
    os.makedirs(out, exist_ok=True)
    for s, m, anchor, kind in candle_jobs[:max_candle_jobs]:
        if client.stats.requests >= budget - 3 or getattr(client.stats, "http_429", 0) + getattr(client.stats, "http_5xx", 0) >= max_throttle:
            break
        t = m["ticker"]; prev = state["tickers"][t]
        open_ts = T.to_ts(m.get("open_time") or m.get("created_time"))
        h60, m1 = fetch_candles(client, s, t, open_ts, anchor, prev.get("tier") or "historical")
        if h60 or m1:
            cdir = os.path.join(out, "candles_v2", s); os.makedirs(cdir, exist_ok=True)
            with open(os.path.join(cdir, f"{t}.json"), "w") as f:
                json.dump(dict(ticker=t, series=s, anchor_ts=anchor, tier=prev.get("tier") or "historical", h60=h60, m1=m1), f, separators=(",", ":"))
            touched.append(os.path.join("candles_v2", s, f"{t}.json"))
        prev["candles"] = "v2" if (h60 or m1) else "none"
        run_rec["candle_only"] += 1
        T.save_state(state_path, state)
    for s, m, anchor, kind in todo:
        if client.stats.requests >= budget - 3 or (max_tickers and run_rec["tickers_attempted"] >= max_tickers):
            break
        if getattr(client.stats, "http_429", 0) + getattr(client.stats, "http_5xx", 0) >= max_throttle:
            run_rec["stopped"] = "throttled"          # pause: never push through a rate limit or an outage
            break
        t = m["ticker"]
        open_ts = T.to_ts(m.get("open_time") or m.get("created_time"))
        d = os.path.join(out, "trades_v2", s); os.makedirs(d, exist_ok=True)
        fpath = os.path.join(d, f"{t}.jsonl")
        prev = state["tickers"].get(t, {})
        rel = os.path.join("trades_v2", s, f"{t}.jsonl")
        if prev.get("n") and not _nonempty(fpath):
            # lazy per-ticker restore of the ONE file this run extends.  Appending to a file that lost its earlier prints would corrupt the tape, so a
            # ticker that cannot be restored is skipped and reported, never started over.
            if not (fetch_existing and fetch_existing(rel) and _nonempty(fpath)):
                run_rec["restore_failed"] += 1
                continue
        reanchored = None
        if prev.get("anchor_ts") not in (None, anchor) and _nonempty(fpath):
            # The tape on disk was cut at a different anchor (e.g. close_time, which can be hours AFTER kickoff, so it holds in-game prints).
            # Never mix anchors and never delete: move it to trades_v2_quarantine/ (kept for audit, excluded from research) and refetch from scratch.
            qd = os.path.join(out, "trades_v2_quarantine", s); os.makedirs(qd, exist_ok=True)
            qp = os.path.join(qd, f"{t}.anchor{prev['anchor_ts']}.jsonl")
            k = 1
            while os.path.exists(qp):
                qp = os.path.join(qd, f"{t}.anchor{prev['anchor_ts']}.{k}.jsonl"); k += 1
            reanchored = dict(old_anchor_ts=prev["anchor_ts"], old_anchor_kind=prev.get("anchor_kind"), quarantined_prints=prev.get("n"), quarantine_path=os.path.relpath(qp, out))
            os.replace(fpath, qp)
            touched += [rel, os.path.relpath(qp, out)]
            prev = {}
        tier = prev.get("tier") if prev.get("anchor_ts") == anchor and prev.get("tier") in ("historical", "live") else "historical"
        checked = [tier]
        kw = dict(anchor_ts=anchor, market_open_ts=open_ts, page_budget=page_budget, limit=limit, known_ids=existing_ids(fpath))
        r = T.fetch_tape(client, t, path=LIVE if tier == "live" else HIST, resume_cursor=(prev.get("cursor") if prev.get("anchor_ts") == anchor else None), **kw)
        if tier == "historical" and r.stop_reason == T.EMPTY_PAGE and r.pages == 1 and not prev.get("cursor"):
            # empty first page: the market may still live only in the LIVE tier (historical/* 404s or is empty for it). Ask the live endpoint before
            # recording a tape as complete-and-empty.  Adopt the live result only if it holds prints or errored (an error must be retried, not hidden).
            checked.append("live")
            r2 = T.fetch_tape(client, t, path=LIVE, resume_cursor=None, **kw)
            if r2.n or r2.stop_reason == T.ERROR or r2.cursor:
                r, tier = r2, "live"
        touched.append(rel)
        with open(fpath, "a") as f:
            for x in r.trades:
                f.write(json.dumps(x, separators=(",", ":")) + "\n")
        # candle verification needs the WHOLE tape: only when this run completed it
        ver = None
        cflag = prev.get("candles") if prev.get("anchor_ts") == anchor else None
        if r.tape_complete:
            cpath = os.path.join(out, "candles", s, f"{t}.json")
            candles = (json.load(open(cpath)).get("h60") if os.path.exists(cpath) else None)
            if candles is None:
                h60, m1 = fetch_candles(client, s, t, open_ts, anchor, tier)
                candles = h60
                cflag = "none"
                if (h60 or m1) and not (manifest or {}).get(t, {}).get("has_candles"):
                    cflag = "v2"
                    # no legacy candle file for this contract: keep what we fetched (quotes at any instant), so the engine can evaluate it
                    cdir = os.path.join(out, "candles_v2", s); os.makedirs(cdir, exist_ok=True)
                    with open(os.path.join(cdir, f"{t}.json"), "w") as f:
                        json.dump(dict(ticker=t, series=s, anchor_ts=anchor, tier=tier, h60=h60, m1=m1), f, separators=(",", ":"))
                    touched.append(os.path.join("candles_v2", s, f"{t}.json"))
            alltr = [json.loads(l) for l in open(fpath)]
            ver = T.hourly_candle_vs_tape(candles or [], alltr, anchor)
        if r.tape_complete and (manifest or {}).get(t, {}).get("has_candles"):
            cflag = "legacy"
        row = T.final_status(r, ver)
        row.update(series=s, anchor_kind=kind, reanchored=reanchored, tier=tier, tiers_checked=checked, run_started_at=run_rec["started_at"], total_prints_on_disk=sum(1 for _ in open(fpath)))
        with open(os.path.join(out, "tape_meta.jsonl"), "a") as f:
            f.write(json.dumps(row, separators=(",", ":")) + "\n")
        state["tickers"][t] = dict(status=row["status"], cursor=r.cursor, n=row["total_prints_on_disk"], oldest_ts=r.oldest_ts or prev.get("oldest_ts"),
                                   newest_ts=r.newest_ts or prev.get("newest_ts"), anchor_ts=anchor, anchor_kind=kind, tier=tier, tiers_checked=checked, candles=cflag)
        run_rec["tickers_attempted"] += 1; run_rec["trades_written"] += len(r.trades)
        run_rec["complete" if r.tape_complete else "incomplete"] += 1
        T.save_state(state_path, state)          # after EVERY ticker: a killed runner loses at most the current ticker
    with open(os.path.join(out, "publish_manifest.txt"), "w") as f:
        f.write("".join(p + "\n" for p in sorted(set(touched))))
    run_rec["finished_at"] = datetime.now(timezone.utc).isoformat(); run_rec["client_stats"] = client.stats.to_dict()
    remaining = sum(1 for s, m, _a, _k in todo if state["tickers"].get(m["ticker"], {}).get("status") not in ("COMPLETE", "COMPLETE_WITH_SOURCE_GAP"))
    run_rec["remaining"] = remaining
    # per-series merge: a run for one family must not erase what earlier runs recorded for the others (run 42054083681 did)
    kept = {t: v for t, v in (state.get("unanchored") or {}).items() if t.split("-")[0] not in set(series)}
    state["unanchored"] = {**kept, **unanchored}
    state["runs"].append(run_rec)
    T.save_state(state_path, state)
    return run_rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", default=",".join(PRIORITY[:4]))
    ap.add_argument("--budget", type=int, default=20000); ap.add_argument("--page-budget", type=int, default=200)
    ap.add_argument("--rps", type=float, default=5.0); ap.add_argument("--max-tickers", type=int, default=0)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--per-series", type=int, default=0, help="max tickers per family per run outside the capped-legacy group (0 = no cap)")
    ap.add_argument("--restore-ref", default=None, help="git ref (e.g. origin/market-data) to restore the touched tickers' existing tapes from, lazily")
    ap.add_argument("--max-throttle", type=int, default=MAX_THROTTLE)
    a = ap.parse_args()
    from nfl_edge.kalshi.client import KalshiClient
    from nfl_edge.kalshi.classifier import classify
    sys.path.insert(0, os.path.join(ROOT, "scripts", "kalshi"))
    from backfill_quotes import load_kickoffs
    series = [s for s in a.series.split(",") if s]
    if series == ["auto"]:
        series = list(PRIORITY)
    mk = {}
    for s in series:
        p = os.path.join(a.out, "markets", f"{s}.jsonl")
        mk[s] = [json.loads(l) for l in open(p)] if os.path.exists(p) else []
    if not any(mk.values()):
        print(json.dumps(dict(error="MARKETS_MISSING", detail=f"no settled-market files for {series} under {a.out}/markets; nothing to repair "
                                    "(restore markets/ from market-data first)")))
        return 2
    mp = os.path.join(a.out, "legacy_manifest.json")
    manifest = json.load(open(mp)).get("tickers") if os.path.exists(mp) else None
    quotes = None
    try:
        from tape_coverage_report import two_sided
        quotes = set()
        for hp in sorted(glob.glob(os.path.join(a.out, "horizons", "[0-9]*.jsonl"))):
            for l in open(hp):
                r = json.loads(l)
                if any(two_sided(x) for x in (r.get("snaps") or {}).values()):
                    quotes.add(r["ticker"])
    except (ImportError, OSError):
        quotes = None
    rec = run(KalshiClient(rps=a.rps), out=a.out, series=series, markets_by_series=mk, kickoffs=load_kickoffs(), classify=classify,
              budget=a.budget, page_budget=a.page_budget, max_tickers=a.max_tickers, per_series=a.per_series, manifest=manifest, quotes=quotes,
              fetch_existing=git_restorer(a.restore_ref, a.out) if a.restore_ref else None, max_throttle=a.max_throttle)
    print(json.dumps(rec, default=str))
    if rec.get("stopped") == "throttled":
        return 5          # throttled: progress is saved, but the workflow must NOT chain another run
    return 3 if rec["remaining"] else 0


if __name__ == "__main__":
    sys.exit(main())
