#!/usr/bin/env python3
"""Milestone F: do point-in-time ROLE signals (prior-game snap share, weekly depth-chart rank, teammate absence)
add information about a player's opportunity (targets, carries) beyond an EWMA of his own history?
Walk-forward 2018-2024 (weekly depth charts exist through 2024 with `depth_team`; 2025+ switches to ESPN daily).
Model: Poisson-ish via log-link ridge on log(1+EWMA), snap share, depth rank dummies, team pass-attempt EWMA.
Also descriptive: reallocation when the team's prior top-target player is absent (0 offensive snaps).
"""
import json, os, numpy as np, polars as pl
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW = os.path.join(ROOT, "data/raw/nflverse"); OUT = os.path.join(ROOT, "research/role_features"); os.makedirs(OUT, exist_ok=True)
xw = pl.read_parquet(os.path.join(ROOT, "data/silver/player_crosswalk.parquet")).select("gsis_id", pl.col("pfr_id")).filter(pl.col("pfr_id").is_not_null()).unique("pfr_id")
games = pl.read_parquet(os.path.join(ROOT, "data/silver/games.parquet")).select("game_id", "season", "week", "home_team", "away_team", "gameday")
frames = []
for s in range(2016, 2025):
    st = pl.read_parquet(f"{RAW}/stats_player/stats_player_week_{s}.parquet").filter((pl.col("season_type") == "REG") & pl.col("position").is_in(["WR", "TE", "RB"]))
    st = st.select("player_id", "player_display_name", "position", "season", "week", "team", "game_id", "targets", "receptions", "receiving_yards", "carries", "rushing_yards")
    sc = pl.read_parquet(f"{RAW}/snap_counts/snap_counts_{s}.parquet").filter(pl.col("game_type") == "REG").select("game_id", "pfr_player_id", "team", "offense_snaps", "offense_pct")
    sc = sc.join(xw, left_on="pfr_player_id", right_on="pfr_id", how="inner").rename({"gsis_id": "player_id"}).select("game_id", "player_id", "offense_snaps", "offense_pct")
    dc = pl.read_parquet(f"{RAW}/depth_charts/depth_charts_{s}.parquet")
    dc = dc.filter((pl.col("game_type") == "REG") & pl.col("gsis_id").is_not_null() & pl.col("position").is_in(["WR", "TE", "RB"])).select(
        pl.col("season"), pl.col("week"), pl.col("gsis_id").alias("player_id"), pl.col("depth_team").cast(pl.Int64, strict=False).alias("depth_rank")).group_by(["season", "week", "player_id"]).agg(pl.col("depth_rank").min())
    st = st.join(sc, on=["game_id", "player_id"], how="left").join(dc, on=["season", "week", "player_id"], how="left")
    frames.append(st)
df = pl.concat(frames).sort(["player_id", "season", "week"])
df = df.with_columns(pl.col("team").replace({"OAK": "LV", "SD": "LAC", "STL": "LA", "LAR": "LA"}))
# team pass attempts per game (opportunity pool)
tp = df.group_by(["game_id", "team"]).agg(pl.col("targets").sum().alias("team_targets"), pl.col("carries").sum().alias("team_carries"))
df = df.join(tp, on=["game_id", "team"], how="left")
# prior-game features (strictly previous game for the player), EWMA of targets/carries (halflife 6 games) within & across seasons
def ewma_prior(col, hl=6.0):
    a = 1 - 0.5 ** (1 / hl)
    return pl.col(col).shift(1).over("player_id").ewm_mean(alpha=a, adjust=True, ignore_nulls=True).over("player_id")
df = df.with_columns([
    ewma_prior("targets").alias("ewma_targets"), ewma_prior("carries").alias("ewma_carries"),
    pl.col("offense_pct").shift(1).over("player_id").alias("prev_snap_pct"),
    pl.col("offense_pct").shift(1).over("player_id").ewm_mean(alpha=0.2, adjust=True, ignore_nulls=True).over("player_id").alias("ewma_snap_pct"),
    pl.col("team_targets").shift(1).over("player_id").ewm_mean(alpha=0.15, adjust=True, ignore_nulls=True).over("player_id").alias("ewma_team_targets"),
    pl.col("targets").shift(1).over("player_id").cum_count().over("player_id").alias("games_prior"),
])
# top-target teammate absent: identify each team-game's prior-season-to-date top target-share player and whether he had 0 snaps in this game
share = df.with_columns((pl.col("targets") / pl.col("team_targets").clip(1)).alias("tshare"))
share = share.with_columns(pl.col("tshare").shift(1).over("player_id").ewm_mean(alpha=0.2, adjust=True, ignore_nulls=True).over("player_id").alias("ewma_tshare"))
top = share.filter(pl.col("ewma_tshare").is_not_null()).sort("ewma_tshare", descending=True).group_by(["game_id", "team"]).first().select("game_id", "team", pl.col("player_id").alias("top_pid"), pl.col("offense_snaps").alias("top_snaps"), pl.col("ewma_tshare").alias("top_share"))
share = share.join(top, on=["game_id", "team"], how="left").with_columns(((pl.col("top_snaps").fill_null(1) == 0) & (pl.col("player_id") != pl.col("top_pid"))).alias("top_absent"))
# NOTE: top_absent uses this game's snaps of the teammate -> only a *descriptive* reallocation measure, not a pregame feature.
d = share.filter(pl.col("games_prior") >= 3 & pl.col("ewma_targets").is_not_null()).to_pandas()
d["prev_snap_pct"] = d["prev_snap_pct"].fillna(d["ewma_snap_pct"]); d = d.dropna(subset=["prev_snap_pct", "ewma_team_targets"])
d["depth_rank"] = d["depth_rank"].fillna(4).clip(1, 4)
import numpy as np
def fit_ridge(X, y, lam=1.0):
    Xm = X.mean(0); Xs = X.std(0) + 1e-9; ym = y.mean(); Xc = (X - Xm) / Xs
    b = np.linalg.solve(Xc.T @ Xc + lam * np.eye(X.shape[1]), Xc.T @ (y - ym)); return b, Xm, Xs, ym
def pred(m, X): b, Xm, Xs, ym = m; return ((X - Xm) / Xs) @ b + ym
res = {}
for target, ew in (("targets", "ewma_targets"), ("carries", "ewma_carries")):
    sub = d[d.position.isin(["WR", "TE"]) if target == "targets" else d.position.eq("RB")].copy()
    sub = sub.dropna(subset=[ew])
    base = np.column_stack([np.log1p(sub[ew])])
    role = np.column_stack([np.log1p(sub[ew]), sub["prev_snap_pct"], sub["ewma_snap_pct"].fillna(sub["prev_snap_pct"]), (sub["depth_rank"] == 1).astype(float), (sub["depth_rank"] == 2).astype(float), np.log1p(sub["ewma_team_targets"])])
    y = sub[target].to_numpy().astype(float)
    per = {}
    for S in range(2018, 2025):
        tr = (sub.season < S).to_numpy(); te = (sub.season == S).to_numpy()
        mb = fit_ridge(base[tr], np.log1p(y[tr])); mr = fit_ridge(role[tr], np.log1p(y[tr]))
        pb = np.expm1(pred(mb, base[te])); pr = np.expm1(pred(mr, role[te]))
        per[S] = {"n": int(te.sum()), "mae_ewma_only": float(np.mean(np.abs(pb - y[te]))), "mae_with_role": float(np.mean(np.abs(pr - y[te]))), "mae_raw_ewma": float(np.mean(np.abs(sub[ew].to_numpy()[te] - y[te])))}
    res[target] = per
    print(target, {k: (round(v["mae_ewma_only"], 3), round(v["mae_with_role"], 3)) for k, v in per.items()})
# reallocation descriptive: when top target-share teammate absent, how do the others' targets compare to their EWMA?
rec = d[d.position.isin(["WR", "TE", "RB"])]
ab = rec[rec.top_absent]; pr_ = rec[~rec.top_absent]
res["reallocation"] = {"top_absent_player_games": int(len(ab)), "mean_targets_minus_ewma_when_top_absent": float((ab.targets - ab.ewma_targets).mean()),
                       "mean_targets_minus_ewma_otherwise": float((pr_.targets - pr_.ewma_targets).mean()),
                       "by_depth_rank_when_top_absent": {int(k): float(v) for k, v in (ab.targets - ab.ewma_targets).groupby(ab.depth_rank).mean().items()},
                       "n_by_depth_rank": {int(k): int(v) for k, v in ab.groupby("depth_rank").size().items()},
                       "mean_top_share_absent": float(ab.top_share.mean())}
print(res["reallocation"])
json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1)
