#!/usr/bin/env python3
"""Tests the hypotheses pre-registered in research/circumstances/PREREGISTRATION.md (C1-C7), unchanged.

Usage: python scripts/research/circumstance_study.py <evaluations_dir> <out.json> [--challenger-pickle path]
`<evaluations_dir>` = data/shadow/evaluations extracted from the market-data branch.
"""
from __future__ import annotations
import glob, gzip, json, os, sys
import numpy as np, pandas as pd
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.dirname(__file__))
import mean_defect_study as M                                   # noqa: E402

FEE = lambda p: np.ceil(0.07 * p * (1 - p) * 100 - 1e-9) / 100


def circumstance_features(pg: pd.DataFrame) -> pd.DataFrame:
    """Point-in-time features keyed by (player_id, game_id); every value uses games strictly before that game."""
    pg = pg.sort_values(["player_id", "season", "week"]).copy()
    pg["recent3"] = pg.groupby("player_id").targets.transform(lambda s: s.shift(1).rolling(3, min_periods=2).mean())
    pg["trend3"] = pg.recent3 - pg.ewma_targets
    # targets allowed by each defence per game (to RB/WR/TE), then its trailing EWMA BEFORE the game
    dg = (pg[pg.position.isin(["RB", "WR", "TE"])].groupby(["opponent_team", "season", "week", "game_id"], as_index=False).targets.sum()
          .rename(columns={"opponent_team": "def", "targets": "allowed"}).sort_values(["def", "season", "week"]))
    d = 0.5 ** (1 / 6.0)
    vals = []
    for _, g in dg.groupby("def"):
        S = W = 0.0; last = None; out = []
        for s, a in zip(g.season, g.allowed):
            if last is not None and s != last:
                S *= 0.5; W *= 0.5
            last = s
            out.append(S / W if W > 0 else np.nan)
            S = S * d + a; W = W * d + 1.0
        vals.append(pd.Series(out, index=g.index))
    dg["allowed_ewma"] = pd.concat(vals)
    dg["opp_soft_rank"] = dg.groupby(["season", "week"]).allowed_ewma.rank(pct=True)
    dg["opp_tercile"] = pd.cut(dg.opp_soft_rank, [0, 1 / 3, 2 / 3, 1.0001], labels=[1, 2, 3])
    games = pd.read_parquet(os.path.join(ROOT, "data/silver/games.parquet"))[["game_id", "spread_line"]]
    f = pg[["player_id", "game_id", "team", "opponent_team", "home", "trend3", "implied_total", "ewma_targets", "n_prior"]].merge(
        dg[["game_id", "def", "opp_tercile"]], left_on=["game_id", "opponent_team"], right_on=["game_id", "def"], how="left").merge(games, on="game_id", how="left")
    f["spread_team"] = np.where(f.home, f.spread_line, -f.spread_line)
    return f.drop(columns=["def"])


def load_contracts(eval_dir):
    rows = []
    for fpath in sorted(glob.glob(f"{eval_dir}/*/*.evaluations.jsonl.gz")):
        for line in gzip.open(fpath):
            r = json.loads(line)
            if r.get("family") == "PLAYER_STAT" and r.get("stat") in ("receptions", "receiving_yards"):
                rows.append({k: r.get(k) for k in ["ticker", "game_id", "player_id", "stat", "threshold", "week", "observed_at", "kickoff_utc",
                                                   "yes_bid_t", "yes_ask_t", "no_ask_t", "mid_t", "width_t", "model_event_probability",
                                                   "settled_yes", "settlement_kind"]})
    d = pd.DataFrame(rows)
    d = d[pd.to_datetime(d.observed_at) < pd.to_datetime(d.kickoff_utc)]
    d = d.sort_values(["ticker", "observed_at"]).groupby("ticker").tail(1)
    d = d[(d.settlement_kind == "binary") & d.settled_yes.notna() & (d.width_t <= 0.10) & (d.yes_bid_t > 0) & (d.yes_ask_t < 1)]
    d["y"] = d.settled_yes.astype(float)
    d["cl"] = d.game_id + "|" + d.player_id.astype(str) + "|" + d.stat
    return d.reset_index(drop=True)


def cluster_stat(x, cl):
    x = np.asarray(x, float); m = ~np.isnan(x); x, c = x[m], np.asarray(cl)[m]
    codes, u = pd.factorize(c); n, g = len(x), len(u)
    mu = x.mean(); se = np.sqrt((np.bincount(codes, weights=x - mu) ** 2).sum() * g / (g - 1)) / n if g > 1 else np.nan
    return dict(mean=float(mu), se=float(se), z=float(mu / se) if se and se > 0 else np.nan, n=int(n), clusters=int(g))


def main(eval_dir, out):
    pg = M.frame()
    feats = circumstance_features(pg)
    d = load_contracts(eval_dir).merge(feats, on=["player_id", "game_id"], how="left")
    d["mid"] = d.mid_t
    d["gap_model"] = np.nan
    chal = os.environ.get("CHALLENGER_PICKLE")
    if chal and os.path.exists(chal):
        c = pd.read_pickle(chal)[["ticker", "challenger_v2"]]
        d = d.merge(c, on="ticker", how="left"); d["gap_model"] = d.challenger_v2 - d.mid
    d["ev_yes"] = d.y - d.yes_ask_t - FEE(d.yes_ask_t)
    d["ev_no"] = (1 - d.y) - d.no_ask_t - FEE(d.no_ask_t)
    d["resid"] = d.y - d.mid
    tests = {
        "C1": (d.trend3 >= 1.5, "up"), "C2": (d.trend3 <= -1.5, "down"), "C3": (d.opp_tercile == 3, "up"), "C4": (d.opp_tercile == 1, "down"),
        "C5": (d.implied_total >= 26, "up"), "C6": (d.spread_team <= -7, "up"),
        "C7": ((d.gap_model >= 0.05) & (d.trend3 >= 1.5), "ev"),
    }
    res = {"alpha_bonferroni": 0.05 / 14, "z_needed": 2.69, "population_clusters": int(d.cl.nunique()), "population_contracts": int(len(d)), "tests": {}}
    for hid, (mask, direction) in tests.items():
        for stat in ("receptions", "receiving_yards"):
            g = d[mask.fillna(False) & (d.stat == stat)]
            if direction == "ev":
                st = cluster_stat(g.ev_yes.to_numpy(), g.cl.to_numpy()); st["quantity"] = "EV of buying YES at ask after fee"
            else:
                st = cluster_stat(g.resid.to_numpy(), g.cl.to_numpy()); st["quantity"] = "mean(y - mid)"
                sign = 1 if direction == "up" else -1
                st["z_in_predicted_direction"] = st["z"] * sign
                st["ev_buying_predicted_side_at_ask"] = cluster_stat((g.ev_yes if direction == "up" else g.ev_no).to_numpy(), g.cl.to_numpy())
            z = st.get("z_in_predicted_direction", st["z"])
            st["status"] = "DISCOVERY_SUPPORTED" if (z >= 2.69 and (st.get("ev_buying_predicted_side_at_ask", st)["mean"] > 0)) else "NOT_SUPPORTED"
            res["tests"][f"{hid}|{stat}"] = st
    json.dump(res, open(out, "w"), indent=1, default=float)
    for k, v in res["tests"].items():
        ev = v.get("ev_buying_predicted_side_at_ask", v)
        print(f"{k:22s} clusters={v['clusters']:4d} {v['quantity'][:12]:12s} mean={v['mean']:+.3f} z_pred={v.get('z_in_predicted_direction', v['z']):+.2f} EV@ask={ev['mean']:+.3f} -> {v['status']}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
