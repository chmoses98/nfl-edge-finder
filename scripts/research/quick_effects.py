#!/usr/bin/env python3
"""Edge-lab quick effect-size checks against the closing line (descriptive, not confirmatory).
H-005 QB change: games where a team's starting QB differs from its previous game's starter.
H-006 Weather: observed wind/temperature (post hoc!) vs total residual and passing volume.
Rest/travel: rest-day differences, Thursday games, international sites.
For each: mean closing-line residual with bootstrap CI, n. If the close already reflects the factor, residual ~ 0.
"""
import json, os, numpy as np, polars as pl
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
g = pl.read_parquet(os.path.join(ROOT, "data/silver/games.parquet")).filter((pl.col("game_type") == "REG") & pl.col("result").is_not_null() & pl.col("spread_line").is_not_null() & (pl.col("season") >= 2010))
g = g.with_columns((pl.col("result") - pl.col("spread_line")).alias("res"), (pl.col("total") - pl.col("total_line")).alias("tres"))
rng = np.random.default_rng(0)
def ci(x):
    x = np.asarray(x, float); x = x[~np.isnan(x)]
    if len(x) < 5: return None
    b = [rng.choice(x, len(x)).mean() for _ in range(2000)]
    return {"n": int(len(x)), "mean": float(x.mean()), "ci95": [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))], "sd": float(x.std())}
out = {}
# ---- QB change: long format
long = []
for side, opp in (("home", "away"), ("away", "home")):
    d = g.select(pl.col("season"), pl.col("week"), pl.col("game_id"), pl.col(f"{side}_team").alias("team"), pl.col(f"{side}_qb_id").alias("qb"), pl.col("res").alias("res_home"), pl.col("tres"), pl.lit(side).alias("side"))
    long.append(d)
L = pl.concat(long).sort(["team", "season", "week"])
L = L.with_columns(pl.col("qb").shift(1).over(["team", "season"]).alias("prev_qb"))
L = L.with_columns(((pl.col("qb") != pl.col("prev_qb")) & pl.col("prev_qb").is_not_null()).alias("qb_change"),
                   pl.when(pl.col("side") == "home").then(pl.col("res_home")).otherwise(-pl.col("res_home")).alias("res_team"))
out["qb_change_team_residual"] = ci(L.filter(pl.col("qb_change"))["res_team"].to_numpy())
out["no_qb_change_team_residual"] = ci(L.filter(~pl.col("qb_change") & pl.col("prev_qb").is_not_null())["res_team"].to_numpy())
out["qb_change_total_residual"] = ci(L.filter(pl.col("qb_change"))["tres"].to_numpy())
# ---- weather (outdoors only; observed wind is post hoc)
o = g.filter(pl.col("roof").is_in(["outdoors", "open"]) & pl.col("wind").is_not_null())
for lo, hi in ((0, 5), (5, 10), (10, 15), (15, 20), (20, 99)):
    sub = o.filter((pl.col("wind") >= lo) & (pl.col("wind") < hi))
    out[f"wind_{lo}_{hi}_total_residual"] = ci(sub["tres"].to_numpy())
    out[f"wind_{lo}_{hi}_total_line_mean"] = float(sub["total_line"].mean()) if sub.height else None
for lo, hi in ((-99, 32), (32, 50), (50, 70), (70, 120)):
    sub = o.filter((pl.col("temp") >= lo) & (pl.col("temp") < hi))
    out[f"temp_{lo}_{hi}_total_residual"] = ci(sub["tres"].to_numpy())
# ---- rest / schedule
g2 = g.with_columns((pl.col("home_rest") - pl.col("away_rest")).alias("rest_diff"))
out["rest_diff_ge4_home_residual"] = ci(g2.filter(pl.col("rest_diff") >= 4)["res"].to_numpy())
out["rest_diff_le_-4_home_residual"] = ci(g2.filter(pl.col("rest_diff") <= -4)["res"].to_numpy())
out["thursday_total_residual"] = ci(g.filter(pl.col("weekday") == "Thursday")["tres"].to_numpy())
out["international_home_residual"] = ci(g.filter(pl.col("location") == "Neutral")["res"].to_numpy())
out["div_game_total_residual"] = ci(g.filter(pl.col("div_game") == 1)["tres"].to_numpy())
out["home_residual_all"] = ci(g["res"].to_numpy())
json.dump(out, open(os.path.join(ROOT, "research/edge_lab/quick_effects.json"), "w"), indent=1)
for k, v in out.items():
    print(f"{k:38s}", v if not isinstance(v, dict) else f"n={v['n']:5d} mean={v['mean']:+.2f} ci=[{v['ci95'][0]:+.2f},{v['ci95'][1]:+.2f}]")
