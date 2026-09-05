#!/usr/bin/env python3
"""Historical passive-execution study: TOUCH-BASED UPPER BOUND, never a fill.

The 2025 archive has minute candles (quoted yes_bid/yes_ask) and the full trade feed with price, size, time
and which side of the book the taker hit, for 1,007 KXNFLGAME and KXNFLSPREAD markets. Both of those series
charge MAKER fees (`quadratic_with_maker_fees`), so they are exactly the markets where passive entry is
least free -- and exactly the ones this project would trade.

What is measured, for a hypothetical resting order placed at each decision time:

  touch rate            the quoted book later reached our level
  trade-at-level rate   a trade printed at/through our level with the taker hitting our side
  volume at/through     how much traded there, the only observable bound on how much of it could be ours
  markout               midpoint at +1/+5/+10/+30/+60 minutes and at the close, from the fill instant
  settlement            what the contract actually did

Queue position is NOT observable in the historical feed, so every rate here is an UPPER BOUND on our own
fill rate, and is labelled as such everywhere it appears. The decisive question is not the rate but the
markout: if a passive order is reachable mainly when the price is about to move against it, price improvement
is an illusion and the strategy is buying adverse selection at a discount.
"""
import argparse, glob, gzip, json, os, sys
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.execution.fees import MAKER_FEE_SWEEP, load_fee_schedule  # noqa: E402
from nfl_edge.execution.passive import markout, scan_quotes_for_touch, scan_trades_for_level  # noqa: E402
from nfl_edge.execution.ticks import passive_levels  # noqa: E402
from nfl_edge.research.clv import clustered_se  # noqa: E402

OUT = os.path.join(ROOT, "research", "passive"); os.makedirs(OUT, exist_ok=True)
MARKOUTS_S = [60, 300, 600, 1800, 3600]
REST_HORIZON_S = 1800          # how long the hypothetical order rests before being cancelled
DECISION_OFFSETS_S = [3 * 3600, 90 * 60, 60 * 60, 30 * 60]   # before kickoff


def ts_of(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def load_market(candle_path, trade_path):
    d = json.load(open(candle_path))
    path = []
    for c in sorted((d.get("h60") or []) + (d.get("m1") or []), key=lambda x: x.get("end_period_ts") or 0):
        yb = (c.get("yes_bid") or {}).get("close")
        ya = (c.get("yes_ask") or {}).get("close")
        try:
            yb = float(yb) if yb is not None else None
            ya = float(ya) if ya is not None else None
        except (TypeError, ValueError):
            yb = ya = None
        if yb is not None and ya is not None and 0 <= yb <= ya <= 1 and not (yb <= 0 and ya >= 1):
            path.append((float(c["end_period_ts"]), yb, ya))
    trades = []
    if os.path.exists(trade_path):
        for line in open(trade_path):
            try:
                t = json.loads(line)
                trades.append((ts_of(t["created_time"]), float(t["yes_price_dollars"]),
                               float(t["count_fp"]), t.get("taker_book_side")))
            except (KeyError, ValueError, TypeError):
                continue
        trades.sort()
    return path, trades


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", default="/home/user/_md")
    ap.add_argument("--horizons", default="/home/user/_md/data/kalshi/backfill/horizons/*.jsonl")
    a = ap.parse_args()

    fs = load_fee_schedule(ROOT)
    meta = {}
    for f in glob.glob(a.horizons):
        for line in open(f):
            r = json.loads(line)
            if r.get("anchor_kind") == "kickoff" and r.get("result") in ("yes", "no"):
                meta[r["ticker"]] = {"anchor": r["anchor_ts"], "y": 1.0 if r["result"] == "yes" else 0.0,
                                     "game_id": r.get("game_id"), "series": r.get("series"),
                                     "family": r.get("family")}
    cdir = os.path.join(a.md, "data/kalshi/backfill/candles")
    tdir = os.path.join(a.md, "data/kalshi/backfill/trades")
    files = sorted(glob.glob(os.path.join(cdir, "*", "*.json")))
    print(f"markets with cached candles: {len(files)};  with kickoff+settlement metadata: "
          f"{sum(1 for f in files if os.path.basename(f)[:-5] in meta)}")

    rows = []
    n_used = 0
    for cf in files:
        ticker = os.path.basename(cf)[:-5]
        m = meta.get(ticker)
        if not m:
            continue
        series = ticker.split("-")[0]
        tf = os.path.join(tdir, series, ticker + ".jsonl")
        path, trades = load_market(cf, tf)
        if len(path) < 20:
            continue
        n_used += 1
        anchor = float(m["anchor"])
        close_mid = None
        for ts, yb, ya in path:
            if ts <= anchor:
                close_mid = (yb + ya) / 2.0
        for off in DECISION_OFFSETS_S:
            t0 = anchor - off
            book = None
            for ts, yb, ya in path:
                if ts <= t0:
                    book = (ts, yb, ya)
                elif ts > t0:
                    break
            if book is None:
                continue
            _bts, yb, ya = book
            if (ya - yb) < 0.02:
                continue                    # a one-cent book leaves no passive level to improve into
            for side in ("yes", "no"):
                lv = passive_levels(yb, ya, side)
                for lname, level in lv.items():
                    t_end = min(t0 + REST_HORIZON_S, anchor)
                    if t_end <= t0:
                        continue
                    touch = scan_quotes_for_touch(path, level, side, t0, t_end)
                    hits, vol, first = scan_trades_for_level(trades, level, side, t0, t_end)
                    mk = markout(path, first, MARKOUTS_S) if first else {}
                    entry_mid = (yb + ya) / 2.0
                    cost = level if side == "yes" else level          # what we pay per contract
                    payoff = m["y"] if side == "yes" else (1.0 - m["y"])
                    rows.append({
                        "ticker": ticker, "series": series, "game_id": m["game_id"], "family": m["family"],
                        "offset_s": off, "side": side, "level_name": lname, "level": level,
                        "entry_mid": entry_mid, "spread": ya - yb,
                        "touched": touch is not None,
                        "time_to_touch_s": (touch - t0) if touch else None,
                        "trade_at_level": first is not None,
                        "time_to_trade_s": (first - t0) if first else None,
                        "volume_at_or_through": vol, "n_trades": hits,
                        "close_mid": close_mid, "settled_yes": m["y"],
                        "gross_pnl": payoff - cost,
                        **{f"markout_{o}": mk.get(o) for o in MARKOUTS_S},
                    })
    print(f"markets used: {n_used};  hypothetical passive orders: {len(rows)}")
    if not rows:
        print("no orders generated"); return 1
    import polars as pl
    D = pl.DataFrame(rows)
    D.write_parquet(os.path.join(OUT, "passive_orders_2025.parquet"))

    res = {"n_orders": D.height, "n_markets": n_used, "rest_horizon_s": REST_HORIZON_S}
    print(f"\nTOUCH-BASED UPPER BOUND -- NOT FILLS (queue position is unobservable historically)")
    print(f"  {'level':14s} {'orders':>7s} {'touch %':>8s} {'trade@lvl %':>12s} {'med vol':>9s} "
          f"{'med s to trade':>15s}")
    for lname in ("join_bid", "improve_bid"):
        d = D.filter(pl.col("level_name") == lname)
        if d.height < 50:
            continue
        t = float(d["touched"].mean()); tr = float(d["trade_at_level"].mean())
        vv = d.filter(pl.col("trade_at_level"))["volume_at_or_through"].to_numpy()
        tt = d.filter(pl.col("trade_at_level"))["time_to_trade_s"].to_numpy()
        res.setdefault("levels", {})[lname] = {"n": d.height, "touch_rate": t, "trade_at_level_rate": tr,
                                               "median_volume": float(np.median(vv)) if len(vv) else None,
                                               "median_s_to_trade": float(np.median(tt)) if len(tt) else None}
        print(f"  {lname:14s} {d.height:7d} {t:8.1%} {tr:12.1%} "
              f"{(np.median(vv) if len(vv) else float('nan')):9.0f} "
              f"{(np.median(tt) if len(tt) else float('nan')):15.0f}")

    print(f"\nADVERSE SELECTION: markout from the trade instant (midpoint change, our direction)")
    print(f"  {'level':14s} {'n':>6s} " + "".join(f"{'+' + str(o // 60) + 'm':>9s}" for o in MARKOUTS_S) +
          f"{'close':>9s}")
    for lname in ("join_bid", "improve_bid"):
        d = D.filter((pl.col("level_name") == lname) & pl.col("trade_at_level"))
        if d.height < 50:
            continue
        sgn = np.where(np.array(d["side"].to_list()) == "yes", 1.0, -1.0)
        lvl = d["level"].to_numpy()
        entry = np.where(sgn > 0, lvl, 1.0 - lvl)          # our position's YES-equivalent entry
        line = f"  {lname:14s} {d.height:6d} "
        row = {}
        for o in MARKOUTS_S:
            mo = d[f"markout_{o}"].to_numpy().astype(float)
            ok = np.isfinite(mo)
            v = (mo[ok] - entry[ok]) * sgn[ok]
            row[o] = float(v.mean()) if ok.sum() else float("nan")
            line += f"{row[o]:+9.4f}"
        cm = d["close_mid"].to_numpy().astype(float)
        ok = np.isfinite(cm)
        cv = (cm[ok] - entry[ok]) * sgn[ok]
        line += f"{cv.mean():+9.4f}"
        res.setdefault("markout", {})[lname] = {"by_offset": row, "close": float(cv.mean())}
        print(line)

    print(f"\nFILL-CONDITIONED SETTLEMENT BIAS: is a reachable order reachable because we are wrong?")
    print(f"  {'level':14s} {'group':16s} {'n':>7s} {'gross P&L':>11s} {'se':>8s} {'z':>7s}")
    for lname in ("join_bid", "improve_bid"):
        base = D.filter(pl.col("level_name") == lname)
        if base.height < 100:
            continue
        for gname, d in (("trade-at-level", base.filter(pl.col("trade_at_level"))),
                         ("NOT reachable", base.filter(~pl.col("trade_at_level")))):
            if d.height < 30:
                continue
            g = d["gross_pnl"].to_numpy()
            cl = d["game_id"].to_list()
            se = clustered_se(g, cl)
            res.setdefault("fill_conditioned", {}).setdefault(lname, {})[gname] = {
                "n": d.height, "gross": float(g.mean()), "se": se}
            print(f"  {lname:14s} {gname:16s} {d.height:7d} {g.mean():+11.4f} {se:8.4f} "
                  f"{(g.mean()/se if se else float('nan')):+7.2f}")

    print(f"\nECONOMICS AT THE UPPER BOUND (gross, then net of the maker fee -- these series charge one)")
    print(f"  maker fee sweep, per contract: {MAKER_FEE_SWEEP}")
    print(f"  {'level':14s} {'n':>7s} {'gross':>9s} " +
          "".join(f"{'net@' + format(m, '.4f'):>11s}" for m in MAKER_FEE_SWEEP))
    for lname in ("join_bid", "improve_bid"):
        d = D.filter((pl.col("level_name") == lname) & pl.col("trade_at_level"))
        if d.height < 50:
            continue
        g = d["gross_pnl"].to_numpy()
        line = f"  {lname:14s} {d.height:7d} {g.mean():+9.4f} "
        nets = {}
        for mf in MAKER_FEE_SWEEP:
            nets[mf] = float((g - mf).mean())
            line += f"{nets[mf]:+11.4f}"
        res.setdefault("economics", {})[lname] = {"gross": float(g.mean()), "net_by_maker_fee": nets}
        print(line)
    print(f"\n  fee context: {fs.describe('KXNFLGAME')}")
    print(f"                {fs.describe('KXNFLSPREAD')}")
    json.dump(res, open(os.path.join(OUT, "passive_results.json"), "w"), indent=1, default=float)
    return 0


if __name__ == "__main__":
    sys.exit(main())
