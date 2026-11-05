#!/usr/bin/env python3
"""Independent audit of the recovered pre-kickoff tapes (``trades_v2/``), run BEFORE publishing.

The collector's own anchor is never trusted: every file is checked against a kickoff recomputed here from the nflverse schedule (classifier join, else the
ticker's (date, away, home)), for (1) no print after kickoff, (2) no duplicate trade_id, (3) newest-first order, (4) the collector's stored anchor equals the
independently computed kickoff.  A file that fails is MOVED (never deleted) to ``trades_v2_quarantine/<series>/<ticker>.verify-<n>.jsonl`` and its state is
reset so the next run refetches it; the failure is recorded in ``tape_verify.json``.  Tickers with no independent kickoff are reported UNVERIFIABLE, not passed.

usage: tape_verify.py --out data/kalshi/backfill [--all]   (default: only files listed in publish_manifest.txt)"""
from __future__ import annotations
import argparse, json, os, sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "scripts", "kalshi"))


def _ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def independent_kickoff(ticker, market, kickoffs, classify):
    sem = classify(market) if market else None
    if sem is not None and sem.game_date and sem.away_team and sem.home_team:
        k = kickoffs.get((sem.game_date, sem.away_team, sem.home_team))
        if k:
            return k[0]
    import tape_repair as TR
    r = TR.kickoff_from_ticker(ticker, kickoffs)
    return r[0] if r else None


def check_file(path, kickoff, stored_anchor):
    ids, n, dup, post, order, prev = set(), 0, 0, 0, 0, None
    with open(path) as f:
        for line in f:
            r = json.loads(line); n += 1
            if r["trade_id"] in ids:
                dup += 1
            ids.add(r["trade_id"])
            c = _ts(r["created_time"])
            post += c > kickoff
            order += prev is not None and c > prev + 1
            prev = c if prev is None else min(prev, c)
    return dict(prints=n, duplicates=dup, post_kickoff=post, order_violations=order, anchor_matches=(stored_anchor == kickoff))


def verify(out, markets, kickoffs, classify, only=None):
    state_path = os.path.join(out, "tape_state.json")
    state = json.load(open(state_path)) if os.path.exists(state_path) else {"tickers": {}, "runs": []}
    files = []
    for s in sorted(os.listdir(os.path.join(out, "trades_v2"))) if os.path.isdir(os.path.join(out, "trades_v2")) else []:
        for fn in sorted(os.listdir(os.path.join(out, "trades_v2", s))):
            rel = os.path.join("trades_v2", s, fn)
            if only is None or rel in only:
                files.append((s, fn[:-6], rel))
    rep = dict(checked=0, passed=0, unverifiable=[], quarantined=[], at=datetime.now(timezone.utc).isoformat())
    for s, t, rel in files:
        path = os.path.join(out, rel)
        st = state["tickers"].get(t, {})
        k = independent_kickoff(t, markets.get(t), kickoffs, classify)
        if k is None:
            rep["unverifiable"].append(t); continue
        res = check_file(path, k, st.get("anchor_ts"))
        rep["checked"] += 1
        if res["duplicates"] or res["post_kickoff"] or res["order_violations"] or not res["anchor_matches"]:
            qd = os.path.join(out, "trades_v2_quarantine", s); os.makedirs(qd, exist_ok=True)
            i = 1
            while os.path.exists(os.path.join(qd, f"{t}.verify-{i}.jsonl")):
                i += 1
            qp = os.path.join(qd, f"{t}.verify-{i}.jsonl")
            os.replace(path, qp)
            state["tickers"].pop(t, None)                      # forces a clean refetch; the audit history in tape_meta.jsonl stays
            rep["quarantined"].append(dict(ticker=t, independent_kickoff=k, stored_anchor=st.get("anchor_ts"), quarantine_path=os.path.relpath(qp, out), **res))
        else:
            rep["passed"] += 1
    json.dump(state, open(state_path, "w"), separators=(",", ":"))
    return rep


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    from nfl_edge.kalshi.classifier import classify
    from backfill_quotes import load_kickoffs
    only = None
    mp = os.path.join(a.out, "publish_manifest.txt")
    if not a.all and os.path.exists(mp):
        only = {l.strip() for l in open(mp) if l.strip().startswith("trades_v2/")}
    markets = {}
    mdir = os.path.join(a.out, "markets")
    for fn in (os.listdir(mdir) if os.path.isdir(mdir) else []):
        for l in open(os.path.join(mdir, fn)):
            m = json.loads(l); markets[m["ticker"]] = m
    rep = verify(a.out, markets, load_kickoffs(), classify, only)
    json.dump(rep, open(os.path.join(a.out, "tape_verify.json"), "w"), indent=1)
    print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in rep.items()}))
    # quarantined files change the published set: list them so the publish step ships the move
    if rep["quarantined"]:
        with open(mp, "a") as f:
            for q in rep["quarantined"]:
                f.write(q["quarantine_path"] + "\n")
                f.write(os.path.join("trades_v2", q["quarantine_path"].split("/")[1], q["ticker"] + ".jsonl") + "\n")
        with open(os.path.join(a.out, "publish_remove.txt"), "w") as f:
            for q in rep["quarantined"]:
                f.write(os.path.join("trades_v2", q["quarantine_path"].split("/")[1], q["ticker"] + ".jsonl") + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
