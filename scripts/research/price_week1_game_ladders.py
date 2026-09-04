#!/usr/bin/env python3
"""Full-universe pricing demo (game markets only): price every captured 2026 week-1 KXNFL spread/total/team-total/
win-margin/both-teams/winner rung from the market-as-prior joint game environment, centred on the nflverse consensus
line (the only pre-kickoff reference line we have today), and compare with Kalshi's executable quotes.

Output: research/full_universe/week1_game_ladders.parquet + summary. This is a SHADOW exercise: the prior is a
consensus line of unknown vintage, quotes are five days out and many are wide. Deviations are relative-value
CANDIDATES for research, not recommendations.
"""
import json, os, sys, glob, numpy as np, polars as pl
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.pricing.game_env import ResidualBank, simulate_game
from nfl_edge.pricing.ladder import price_yes
from nfl_edge.kalshi.classifier import classify
MD = sys.argv[1] if len(sys.argv) > 1 else "/home/user/_md"
games = pl.read_parquet(os.path.join(ROOT, "data/silver/games.parquet"))
hist = games.filter((games["game_type"] == "REG") & games["result"].is_not_null() & games["spread_line"].is_not_null() & (games["season"] >= 2016)).to_pandas()
hist["mres"] = hist.result - hist.spread_line; hist["tres"] = hist.total - hist.total_line
bank = ResidualBank(hist.mres, hist.tres, hist.season, ref_season=2026, spread_lines=hist.spread_line, total_lines=hist.total_line,
                    overtime=hist.overtime.fillna(0).astype(int), results=hist.result, halflife=3.0, rng=np.random.default_rng(7))
wk1 = games.filter((pl.col("season") == 2026) & (pl.col("week") == 1)).to_pandas()
# latest quote per ticker from captures
q = {}
for f in sorted(glob.glob(os.path.join(MD, "data/kalshi/capture/*/*.quotes.jsonl"))):
    for l in open(f):
        r = json.loads(l); q[r["ticker"]] = r
# --- Kalshi-implied lines: invert P(home win) from the KXNFLGAME mid, and the total from the rung where the total ladder mid crosses 0.5
from scipy.optimize import brentq
def implied_lines_ls(g):
    """Least-squares implied (spread, total): the grid point whose coherent-distribution rung probabilities best match
    the mids of all liquid full-game winner/spread/total rungs (weights: 1/quote width)."""
    liq = [r for r in q.values() if r.get("game_id") == g.game_id and r.get("period") in ("FULL", None) and r["family"] in ("GAME_WINNER", "SPREAD", "TOTAL")
           and r["yes_bid_dollars"] and r["yes_ask_dollars"] and float(r["volume_fp"] or 0) > 0 and (float(r["yes_ask_dollars"]) - float(r["yes_bid_dollars"])) <= 0.06]
    if len(liq) < 6:
        return None, None
    dm, dt = bank.sample(20000, spread=g.spread_line, total=g.total_line)
    best = (1e9, None, None)
    for s_ in np.arange(-17, 17.5, 0.5):
        m = np.round(s_ + dm); m = np.where(m == 0, np.where(np.random.default_rng(3).random(len(m)) < 0.5, 3.0, -3.0), m)
        for t_ in np.arange(34, 62, 0.5):
            t = np.round(t_ + dt)
            err = 0.0; w = 0.0
            for r in liq:
                mid = (float(r["yes_bid_dollars"]) + float(r["yes_ask_dollars"])) / 2; wt = 1.0 / max(0.01, float(r["yes_ask_dollars"]) - float(r["yes_bid_dollars"]))
                if r["family"] == "GAME_WINNER":
                    pm = np.mean(m > 0) if r.get("team") == g.home_team else np.mean(m < 0)
                elif r["family"] == "SPREAD":
                    x = m if r.get("team") == g.home_team else -m; pm = np.mean(x > float(r["floor_strike"]))
                else:
                    pm = np.mean(t >= float(r["threshold"]))
                err += wt * (pm - mid) ** 2; w += wt
            if err / w < best[0]:
                best = (err / w, s_, t_)
    return best[1], best[2]
def implied_lines(g):
    hw = [r for r in q.values() if r.get("game_id") == g.game_id and r["family"] == "GAME_WINNER" and r.get("team") == g.home_team and r["yes_bid_dollars"] and r["yes_ask_dollars"]]
    s_imp = None
    if hw:
        mid = (float(hw[0]["yes_bid_dollars"]) + float(hw[0]["yes_ask_dollars"])) / 2
        if 0.03 < mid < 0.97:
            f = lambda s: float(np.mean(simulate_game(s, g.total_line, bank, n=20000)["margin"] > 0)) - mid
            try:
                s_imp = round(brentq(f, -25, 25, xtol=0.25) * 2) / 2
            except ValueError:
                s_imp = None
    tot = sorted([(float(r["threshold"]), (float(r["yes_bid_dollars"]) + float(r["yes_ask_dollars"])) / 2) for r in q.values()
                  if r.get("game_id") == g.game_id and r["family"] == "TOTAL" and r.get("period") == "FULL" and float(r["volume_fp"] or 0) > 0])
    t_imp = None
    for (k1, p1), (k2, p2) in zip(tot, tot[1:]):
        if p1 >= 0.5 >= p2 and p1 != p2:
            t_imp = round((k1 + (p1 - 0.5) / (p1 - p2) * (k2 - k1) - 0.5) * 2) / 2; break
    return s_imp, t_imp
rows = []
for _, g in wk1.iterrows():
    s_imp, t_imp = implied_lines_ls(g)
    s_use = s_imp if s_imp is not None else g.spread_line
    t_use = t_imp if t_imp is not None else g.total_line
    print(g.game_id, "consensus", g.spread_line, g.total_line, "kalshi-implied", s_imp, t_imp)
    sim = simulate_game(s_use, t_use, bank, n=40000)
    m, t, h, aw = sim["margin"], sim["total"], sim["home"], sim["away"]
    for tk, r in q.items():
        if r.get("game_id") != g.game_id or r["family"] not in ("SPREAD", "TOTAL", "TEAM_TOTAL", "WIN_MARGIN_BUCKET", "BOTH_TEAMS_SCORE_N", "GAME_WINNER") or (r.get("period") not in ("FULL", None)):
            continue
        sem = classify(r | {"strike_type": r.get("strike_type"), "custom_strike": None})
        fam = r["family"]; team = r.get("team")
        if fam == "SPREAD":
            x = m if team == g.home_team else -m
            p = float(np.mean(x > float(r["floor_strike"])))
        elif fam == "TOTAL":
            p = float(np.mean(t >= float(r["threshold"])))
        elif fam == "TEAM_TOTAL":
            x = h if team == g.home_team else aw
            p = float(np.mean(x >= float(r["threshold"])))
        elif fam == "GAME_WINNER":
            p = float(np.mean(m > 0)) if team == g.home_team else float(np.mean(m < 0))
        elif fam == "BOTH_TEAMS_SCORE_N":
            p = float(np.mean((h >= float(r["threshold"])) & (aw >= float(r["threshold"]))))
        else:
            continue
        bid = float(r["yes_bid_dollars"] or 0); ask = float(r["yes_ask_dollars"] or 1)
        rows.append({"game_id": g.game_id, "ticker": tk, "family": fam, "team": team, "threshold": r.get("threshold"), "floor_strike": r.get("floor_strike"),
                     "model_p": p, "yes_bid": bid, "yes_ask": ask, "mid": (bid + ask) / 2, "spread": ask - bid, "volume": float(r["volume_fp"] or 0),
                     "edge_buy_yes": p - ask, "edge_buy_no": (1 - p) - (1 - bid), "observed_at": r["observed_at"], "prior_spread": s_use, "prior_total": t_use, "consensus_spread": g.spread_line, "consensus_total": g.total_line})
d = pl.DataFrame(rows)
d.write_parquet(os.path.join(ROOT, "research/full_universe/week1_game_ladders.parquet"))
liquid = d.filter((pl.col("spread") <= 0.05) & (pl.col("volume") > 0))
print("priced rungs:", d.height, " liquid (spread<=5c, traded):", liquid.height)
print(liquid.group_by("family").agg(pl.len(), (pl.col("model_p") - pl.col("mid")).abs().mean().alias("mean_abs_dev"), (pl.col("model_p") - pl.col("mid")).mean().alias("mean_dev"),
                                    pl.col("edge_buy_yes").max().alias("max_edge_yes"), pl.col("edge_buy_no").max().alias("max_edge_no")).sort("family"))
top = liquid.with_columns(pl.max_horizontal("edge_buy_yes", "edge_buy_no").alias("best_edge")).sort("best_edge", descending=True).head(12)
print(top.select("ticker", "model_p", "yes_bid", "yes_ask", "volume", "edge_buy_yes", "edge_buy_no", "prior_spread", "prior_total"))
summary = {"priced": d.height, "liquid": liquid.height, "by_family": liquid.group_by("family").agg(pl.len().alias("n"), (pl.col("model_p") - pl.col("mid")).abs().mean().alias("mean_abs_dev")).to_dicts(),
           "share_liquid_with_abs_dev_gt_5c": float((liquid["model_p"] - liquid["mid"]).abs().gt(0.05).mean()) if liquid.height else None}
json.dump(summary, open(os.path.join(ROOT, "research/full_universe/week1_summary.json"), "w"), indent=1)
