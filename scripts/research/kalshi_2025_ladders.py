#!/usr/bin/env python3
"""H-003: Kalshi 2025-season settled ladders — market calibration, monotonicity and time-to-close structure from the
historical backfill (market lists with `result`, plus 60-min / 1-min bid-ask candlesticks per market).

For every archived single-game market with a result:
  * classify (family, threshold, team/player), join nflverse game via (date, away, home) for kickoff time;
  * take the last pre-kickoff candle (yes_bid/yes_ask close) at horizons T-24h, T-6h, T-1h, T-10m (nearest earlier candle);
  * market probability = mid of yes bid/ask; outcome = result == "yes".
Report: Brier/log-loss and reliability by family × horizon, by threshold distance, by favourite/underdog side,
ladder monotonicity violations at each horizon, and a comparison to the market-prior game environment for spreads/totals.
Usage: kalshi_2025_ladders.py --market-data-dir /home/user/_md
"""
import argparse, glob, json, os, sys, csv
from datetime import datetime, timezone, timedelta
import numpy as np, polars as pl
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.kalshi.classifier import classify
OUT = os.path.join(ROOT, "research", "kalshi_2025"); os.makedirs(OUT, exist_ok=True)
HORIZONS = {"T-72h": 72 * 60, "T-24h": 24 * 60, "T-6h": 6 * 60, "T-1h": 60, "T-10m": 10}


def kickoffs():
    g = pl.read_parquet(os.path.join(ROOT, "data/silver/games.parquet")).filter(pl.col("season") >= 2024).to_pandas()
    ko = {}
    for _, r in g.iterrows():
        if not isinstance(r.gametime, str):
            continue
        d = datetime.strptime(f"{r.gameday} {r.gametime}", "%Y-%m-%d %H:%M")
        nov1 = datetime(d.year, 11, 1); dst_end = nov1 + timedelta(days=(6 - nov1.weekday()) % 7)
        mar1 = datetime(d.year, 3, 1); dst_start = mar1 + timedelta(days=(6 - mar1.weekday()) % 7 + 7)
        off = 4 if dst_start <= d < dst_end else 5
        ko[(r.gameday, r.away_team, r.home_team)] = (d + timedelta(hours=off)).replace(tzinfo=timezone.utc), r.game_id, r.spread_line, r.total_line, r.result, r.total
    return ko


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--market-data-dir", default="/home/user/_md"); a = ap.parse_args()
    MD = os.path.join(a.market_data_dir, "data/kalshi/backfill")
    ko = kickoffs()
    rows = []; n_no_candles = 0; n_markets = 0
    for f in sorted(glob.glob(os.path.join(MD, "markets", "*.jsonl"))):
        series = os.path.basename(f)[:-6]
        for line in open(f):
            m = json.loads(line); n_markets += 1
            if m.get("result") not in ("yes", "no"):
                continue
            s = classify(m)
            if not s.game_date:
                continue
            k = ko.get((s.game_date, s.away_team, s.home_team))
            if not k:
                # Kalshi date is the US game date; try +1 day mismatch (late games in UTC) handled by classifier date = local
                continue
            kick, game_id, spread_line, total_line, result, total = k
            cp = os.path.join(MD, "candles", series, f"{m['ticker']}.json")
            if not os.path.exists(cp):
                n_no_candles += 1; continue
            c = json.load(open(cp))
            candles = (c.get("h60") or []) + (c.get("m1") or [])
            if not candles:
                n_no_candles += 1; continue
            candles.sort(key=lambda x: x["end_period_ts"])
            base = {"ticker": m["ticker"], "series": series, "family": s.family, "period": s.period, "stat": s.stat, "team": s.team, "player": s.player_name,
                    "threshold": s.threshold, "floor_strike": s.floor_strike, "operator": s.operator, "game_id": game_id, "kickoff": kick.isoformat(),
                    "y": 1.0 if m["result"] == "yes" else 0.0, "spread_line": spread_line, "total_line": total_line, "home_team": s.home_team, "away_team": s.away_team,
                    "volume_fp": float(m.get("volume_fp") or 0), "open_interest_fp": float(m.get("open_interest_fp") or 0)}
            for hname, mins in HORIZONS.items():
                cutoff = (kick - timedelta(minutes=mins)).timestamp()
                prior = [x for x in candles if x["end_period_ts"] <= cutoff]
                if not prior:
                    continue
                x = prior[-1]
                try:
                    bid = float(x["yes_bid"]["close_dollars"]); ask = float(x["yes_ask"]["close_dollars"])
                except (KeyError, TypeError, ValueError):
                    continue
                if not (0 <= bid <= ask <= 1) or ask - bid > 0.20:
                    continue
                rows.append({**base, "horizon": hname, "bid": bid, "ask": ask, "mid": (bid + ask) / 2, "width": ask - bid,
                             "candle_age_min": round((cutoff - x["end_period_ts"]) / 60, 1), "oi_at": float(x.get("open_interest_fp") or 0)})
    d = pl.DataFrame(rows)
    d.write_parquet(os.path.join(OUT, "settled_rungs_by_horizon.parquet"))
    print("archived markets:", n_markets, "rows:", d.height, "no candles:", n_no_candles)
    if not d.height:
        return
    def metrics(df):
        p = df["mid"].to_numpy(); y = df["y"].to_numpy(); pc = np.clip(p, 1e-3, 1 - 1e-3)
        return {"n": int(len(y)), "brier": float(np.mean((p - y) ** 2)), "logloss": float(-np.mean(y * np.log(pc) + (1 - y) * np.log(1 - pc))), "mean_mid": float(p.mean()), "obs": float(y.mean()), "median_width": float(np.median(df["width"].to_numpy()))}
    res = {"by_family_horizon": {}, "reliability": {}}
    for (fam, per, h), sub in d.group_by(["family", "period", "horizon"]):
        res["by_family_horizon"][f"{fam}|{per}|{h}"] = metrics(sub)
    # reliability by mid bucket at T-1h, per family
    for fam, sub in d.filter(pl.col("horizon") == "T-1h").group_by("family"):
        p = sub["mid"].to_numpy(); y = sub["y"].to_numpy(); b = np.minimum((p * 10).astype(int), 9)
        res["reliability"][fam[0]] = [{"bin": int(i), "mid": float(p[b == i].mean()), "obs": float(y[b == i].mean()), "n": int((b == i).sum())} for i in range(10) if (b == i).sum() >= 20]
    # monotonicity violations per ladder at each horizon (mid non-monotone by > 2c)
    viol = {}
    lad = d.filter(pl.col("threshold").is_not_null() | pl.col("floor_strike").is_not_null())
    for (fam, per, h), sub in lad.group_by(["family", "period", "horizon"]):
        n_l = 0; n_v = 0
        for (_ev, _team, _pl), L in sub.group_by([pl.col("ticker").str.split("-").list.slice(0, 2).list.join("-"), "team", "player"]):
            if L.height < 3:
                continue
            n_l += 1
            L = L.sort(pl.coalesce([pl.col("threshold"), pl.col("floor_strike")]))
            mids = L["mid"].to_numpy()
            if np.any(np.diff(mids) > 0.02):
                n_v += 1
        viol[f"{fam}|{per}|{h}"] = {"ladders": n_l, "violations": n_v}
    res["monotonicity"] = viol
    json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1)
    for k, v in sorted(res["by_family_horizon"].items()):
        if v["n"] >= 100:
            print(f"{k:40s} n={v['n']:5d} brier={v['brier']:.4f} mean_mid={v['mean_mid']:.3f} obs={v['obs']:.3f} width={v['median_width']:.3f}")


if __name__ == "__main__":
    main()
