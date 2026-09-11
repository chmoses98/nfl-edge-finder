#!/usr/bin/env python3
"""Automated settlement: join immutable ledger rows with captured exchange settlements and candle histories,
derive SportsTruth (from the exchange's expiration_value / result until a results feed is wired), the canonical
close (last executable quote before the cutoff) and CLV, and write an append-only settlement table + scorecard.

Never edits ledger rows. Output: data/research/settlements/<run>.jsonl (one row per settled prediction) and
data/research/settlements/SCORECARD.md. Feeds health gates TENNIS-8/9/10.
"""
from __future__ import annotations
import argparse, glob, gzip, json, os, sys
from datetime import datetime, timezone, timedelta
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, PROJ)
from tennis_edge.ledger.predictions import PredictionLedger
from tennis_edge.ledger.truth import ExchangeTruth, SportsTruth
from tennis_edge.ledger.close import Quote, canonical_close, clv
from tennis_edge.eval.metrics import summary

PREGAME_HOURS = 7.0


def load_stream(kind):
    out = []
    for f in sorted(glob.glob(os.path.join(PROJ, "data", "kalshi", "capture", "*", f"*.{kind}*.jsonl.gz"))):
        with gzip.open(f, "rt") as fh:
            for line in fh:
                out.append(json.loads(line))
    return out


def quotes_from_candles(rec):
    qs = []
    for c in (rec.get("candles_60") or []):
        if not isinstance(c, dict):
            continue
        try:
            qs.append(Quote(datetime.fromtimestamp(c["end_period_ts"], tz=timezone.utc), float(c["yes_bid"]["close_dollars"]), float(c["yes_ask"]["close_dollars"]), source="candle_bidask"))
        except (KeyError, TypeError, ValueError):
            pass
    return qs


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--ledger", default=os.path.join(PROJ, "data", "research", "ledger")); a = ap.parse_args()
    rows = list(PredictionLedger(a.ledger).rows()) if os.path.isdir(a.ledger) else []
    settlements = {s["ticker"]: s for s in load_stream("settlements")}
    candles = {c["ticker"]: c for c in load_stream("candles")}
    out_dir = os.path.join(PROJ, "data", "research", "settlements"); os.makedirs(out_dir, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    done = set()
    for f in glob.glob(os.path.join(out_dir, "*.jsonl")):
        for line in open(f):
            done.add(json.loads(line)["prediction_id"])
    settled = []
    for r in rows:
        if r["prediction_id"] in done or r["ticker"] not in settlements:
            continue
        s = settlements[r["ticker"]]
        ex = ExchangeTruth.from_market({**s, "ticker": r["ticker"]}, s.get("run_id", ""))
        if not ex.terminal:
            continue
        # sports truth from the exchange result for MATCH_WINNER only (a results feed should replace this)
        st = None
        if r["family"] == "MATCH_WINNER" and ex.binary:
            subj_won = ex.result == "yes"
            st = SportsTruth(r["match_id"], r["player_a_id"] if subj_won == (r["subject"] == r["player_a"]) else r["player_b_id"], None, "COMPLETED", "", source="kalshi_result", confidence=0.9)
        close_t = datetime.fromisoformat(s["close_time"].replace("Z", "+00:00")) if s.get("close_time") else None
        sched = datetime.fromisoformat(r["scheduled_start"].replace("Z", "+00:00")) if r.get("scheduled_start") else None
        cutoff_sched = min(sched, close_t - timedelta(hours=PREGAME_HOURS)) if (sched and close_t) else sched
        cc = canonical_close(quotes_from_candles(candles.get(r["ticker"], {})), cutoff_sched, None) if cutoff_sched else None
        dq = r["market_quote"]
        decision = Quote(datetime.fromisoformat(r["generated_at_utc"]), dq.get("yes_bid"), dq.get("yes_ask"))
        c = clv(decision, cc) if cc else None
        settled.append({"prediction_id": r["prediction_id"], "ticker": r["ticker"], "family": r["family"], "generated_at_utc": r["generated_at_utc"],
                        "exchange": ex.to_dict(), "sports": st.to_dict() if st else None, "gradeable": bool(ex.binary),
                        "y_yes": 1.0 if ex.result == "yes" else (0.0 if ex.result == "no" else None), "fair_yes": r["models"].get("ELO_DP_FAIR"),
                        "market_mid_at_decision": r["models"].get("MARKET_MID"), "close": {"basis": cc.close_basis if cc else "NONE", "mid": cc.quote.mid if (cc and cc.quote) else None,
                        "bid": cc.quote.yes_bid if (cc and cc.quote) else None, "ask": cc.quote.yes_ask if (cc and cc.quote) else None, "seconds_to_cutoff": cc.seconds_to_cutoff if cc else None},
                        "clv": c.__dict__ if c else None, "start_basis": r.get("start_basis"), "settled_run": run_id})
    if settled:
        with open(os.path.join(out_dir, f"{run_id}.jsonl"), "a") as f:
            for x in settled:
                f.write(json.dumps(x, default=str) + "\n")
    # scorecard over everything settled so far
    allrows = []
    for f in sorted(glob.glob(os.path.join(out_dir, "*.jsonl"))):
        allrows += [json.loads(l) for l in open(f)]
    grad = [x for x in allrows if x["gradeable"] and x["fair_yes"] is not None and x["market_mid_at_decision"] is not None]
    L = [f"# Prospective scorecard ({datetime.now(timezone.utc).isoformat()})", "", f"ledger rows: {len(rows)}; settled rows: {len(allrows)}; gradeable binary with market mid: {len(grad)}", ""]
    if len(grad) >= 30:
        import numpy as np
        y = np.array([x["y_yes"] for x in grad]); pm = np.array([x["fair_yes"] for x in grad]); mk = np.array([x["market_mid_at_decision"] for x in grad])
        L += ["| forecaster | n | brier | log_loss | cal_slope |", "|---|---|---|---|---|"]
        for name, p in (("market mid at decision", mk), ("model fair", pm)):
            s = summary(y, p); L.append(f"| {name} | {s['n']} | {s['brier']:.4f} | {s['log_loss']:.4f} | {s['cal_slope']:.3f} |")
        cl = [x["clv"]["executable_clv"] for x in grad if x.get("clv") and x["clv"].get("executable_clv") is not None]
        L += ["", f"executable CLV rows: {len(cl)}; mean {np.mean(cl):+.4f}" if cl else "no CLV rows (no canonical close yet)"]
    else:
        L.append("Fewer than 30 gradeable settled predictions: no scores reported (multiple-testing discipline).")
    L += ["", f"close basis counts: { {b: sum(1 for x in allrows if x['close']['basis'] == b) for b in set(x['close']['basis'] for x in allrows)} }" if allrows else ""]
    open(os.path.join(out_dir, "SCORECARD.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L)); print("newly settled", len(settled))


if __name__ == "__main__":
    main()
