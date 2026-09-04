#!/usr/bin/env python3
"""Does decomposing production into team volume x player share beat an EWMA of raw counts?

Baseline (what the platform uses today): project a player's targets as an EWMA of his prior targets.
Decomposition: project the team's dropbacks from the team's own prior volume plus the pre-game market line,
project the player's share of those dropbacks from his prior shares, and multiply.

Walk-forward: for each evaluation season S, everything is fit on seasons < S only. Errors are reported on the
prop-relevant population (players with a real projected role), because a model that is excellent at
predicting zero for third-string tight ends is not useful for pricing ladders.
"""
import json, os, sys

import numpy as np
import polars as pl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.features import opportunity as O  # noqa: E402

OUT = os.path.join(ROOT, "research", "opportunity"); os.makedirs(OUT, exist_ok=True)
SEASONS = list(range(2016, 2026))
EVAL = list(range(2019, 2026))
TEAM_VOL = ["team_dropbacks", "team_rush_att", "team_plays", "team_rz_dropbacks", "team_rz_rush", "team_i5_rush"]


def ridge(X, y, lam=1.0):
    X = np.column_stack([np.ones(len(X)), X])
    A = X.T @ X + lam * np.eye(X.shape[1]); A[0, 0] -= lam
    return np.linalg.solve(A, X.T @ y)


def predict(b, X):
    return np.column_stack([np.ones(len(X)), X]) @ b


def main():
    cache = os.path.join(OUT, "player_usage.parquet")
    if os.path.exists(cache):
        usage = pl.read_parquet(cache); team = pl.read_parquet(os.path.join(OUT, "team_volume.parquet"))
    else:
        usage, team = O.build_usage(SEASONS, out_dir=OUT)
    print(f"usage rows {usage.height}, team-games {team.height}", flush=True)

    res = pl.read_parquet(os.path.join(ROOT, "research", "player_distributions", "research_table.parquet"))
    res = res.with_columns(pl.col("season").cast(pl.Int64), pl.col("week").cast(pl.Int64))

    # ---- team volume: point-in-time EWMA of the team's own prior games, plus the pre-game line
    sched = res.select(["game_id", "team", "season", "week", "spread_team", "total_line", "home", "implied_total"]).unique(
        subset=["game_id", "team"])
    T = team.join(sched.drop("season"), on=["game_id", "team"], how="inner").sort(["team", "season", "week"])
    T = T.with_columns(position=pl.lit("TEAM"))
    # Shrink toward the league's own pre-window mean, not toward zero. With priors=None the recursion pulls
    # early-season team volume toward 0 plays a game, which is why an unshrunk EWMA of team dropbacks scored
    # worse (MAE 15.4) than simply guessing the league average (6.9).
    tpri = O.group_priors(T.filter(pl.col("season") < 2019), TEAM_VOL, list(range(2016, 2019)), key="position")
    T = O.point_in_time_ewma(T, TEAM_VOL, key="team", halflife=6.0, season_carry=0.35, shrink_k=4.0,
                             priors=tpri, prior_key="position", prefix="pit_")

    tv_report = {}
    T = T.with_columns([pl.lit(np.nan).alias(f"proj_{c}") for c in ("team_dropbacks", "team_rush_att")])
    proj = {c: np.full(T.height, np.nan) for c in ("team_dropbacks", "team_rush_att")}
    season_arr = T["season"].to_numpy()
    feats = ["pit_team_dropbacks", "pit_team_rush_att", "spread_team", "total_line", "home"]
    Xall = T.select(feats).to_numpy().astype(float)
    Xall = np.nan_to_num(Xall, nan=0.0)
    for tgt in ("team_dropbacks", "team_rush_att"):
        yall = T[tgt].to_numpy().astype(float)
        for S in EVAL:
            tr = season_arr < S; te = season_arr == S
            if tr.sum() < 500 or te.sum() == 0:
                continue
            b = ridge(Xall[tr], yall[tr], lam=5.0)
            proj[tgt][te] = predict(b, Xall[te])
        ok = np.isfinite(proj[tgt]) & np.isin(season_arr, EVAL)
        base = T["pit_" + tgt].to_numpy().astype(float)
        tv_report[tgt] = {
            "n": int(ok.sum()),
            "mae_market_plus_form": float(np.abs(proj[tgt][ok] - yall[ok]).mean()),
            "mae_form_only": float(np.abs(base[ok] - yall[ok]).mean()),
            "mae_season_mean": float(np.abs(np.nanmean(yall[season_arr < min(EVAL)]) - yall[ok]).mean()),
        }
    for tgt in ("team_dropbacks", "team_rush_att"):
        T = T.with_columns(pl.Series(f"proj_{tgt}", proj[tgt]))
    print("\nTEAM VOLUME PROJECTION (MAE, plays per game)")
    for k, v in tv_report.items():
        print(f"  {k:16s} n={v['n']:5d}  form+market {v['mae_market_plus_form']:.3f}   form only "
              f"{v['mae_form_only']:.3f}   constant {v['mae_season_mean']:.3f}")

    # ---- player shares
    P = res.join(usage.drop("usage_team"), on=["game_id", "player_id"], how="left")
    P = P.with_columns([pl.col(c).fill_null(0) for c in
                        ["pbp_snaps", "routes", "rush_snaps", "rz_routes", "rz_snaps", "rz_targets",
                         "i10_targets", "rz_carries", "i5_carries", "air_yards"]])
    P = P.drop([c for c in ("targets_right", "carries_right") if c in P.columns])
    P = P.join(team.drop("season"), on=["game_id", "team"], how="inner")
    P = O.attach_shares(P.drop([c for c in P.columns if c.endswith("_right")]), team.drop("season").head(0).clear()) \
        if False else P
    e = 1e-6
    P = P.with_columns(
        route_share=pl.col("routes") / (pl.col("team_dropbacks") + e),
        target_share=pl.col("targets") / (pl.col("team_dropbacks") + e),
        tprr=pl.col("targets") / (pl.col("routes") + e),
        carry_share=pl.col("carries") / (pl.col("team_rush_att") + e),
        rz_target_share=pl.col("rz_targets") / (pl.col("team_rz_dropbacks") + e),
        rz_carry_share=pl.col("rz_carries") / (pl.col("team_rz_rush") + e),
        i5_carry_share=pl.col("i5_carries") / (pl.col("team_i5_rush") + e),
        snap_share=pl.col("pbp_snaps") / (pl.col("team_plays") + e),
        adot=pl.col("air_yards") / (pl.col("targets") + e),
    )
    share_cols = ["route_share", "target_share", "tprr", "carry_share", "rz_target_share", "rz_carry_share",
                  "i5_carry_share", "snap_share", "adot"]
    P = P.with_columns([pl.col(c).clip(0, 5).fill_nan(0).fill_null(0) for c in share_cols])
    priors = O.group_priors(P.filter(pl.col("season") < 2019), share_cols, list(range(2016, 2019)), key="position")
    P = O.point_in_time_ewma(P, share_cols, key="player_id", halflife=5.0, season_carry=0.5, shrink_k=3.0,
                             priors=priors, prior_key="position", prefix="pit_")
    P = P.join(T.select(["game_id", "team", "proj_team_dropbacks", "proj_team_rush_att",
                         "pit_team_dropbacks", "pit_team_rush_att"]), on=["game_id", "team"], how="left")
    P = P.with_columns(
        proj_targets_decomp=pl.col("proj_team_dropbacks") * pl.col("pit_target_share"),
        proj_carries_decomp=pl.col("proj_team_rush_att") * pl.col("pit_carry_share"),
        proj_targets_route=pl.col("proj_team_dropbacks") * pl.col("pit_route_share") * pl.col("pit_tprr"),
    )
    P.write_parquet(os.path.join(OUT, "opportunity_features.parquet"))

    print("\nPLAYER OPPORTUNITY PROJECTION, walk-forward on prop-relevant players")
    report = {"team_volume": tv_report, "player": {}}
    for tgt, decomp, route, base in (("targets", "proj_targets_decomp", "proj_targets_route", "ewma_targets"),
                                     ("carries", "proj_carries_decomp", None, "ewma_carries")):
        rows = []
        for S in EVAL:
            d = P.filter((pl.col("season") == S) & pl.col(decomp).is_not_null() &
                         pl.col("position").is_in(["RB", "WR", "TE"]))
            # prop-relevant: the baseline itself expects a real role, so neither model is judged on scrubs
            d = d.filter(pl.col(base) >= (2.0 if tgt == "targets" else 2.0))
            if d.height < 200:
                continue
            y = d[tgt].to_numpy().astype(float)
            r = {"season": S, "n": d.height,
                 "mae_decomp": float(np.abs(d[decomp].to_numpy() - y).mean()),
                 "mae_baseline": float(np.abs(d[base].to_numpy() - y).mean())}
            if route:
                r["mae_route"] = float(np.abs(d[route].to_numpy() - y).mean())
            rows.append(r)
        report["player"][tgt] = rows
        print(f"  {tgt}")
        for r in rows:
            extra = f"  routes x TPRR {r['mae_route']:.3f}" if "mae_route" in r else ""
            print(f"    {r['season']}  n={r['n']:5d}  decomposition {r['mae_decomp']:.3f}   "
                  f"raw EWMA {r['mae_baseline']:.3f}{extra}   delta {r['mae_decomp']-r['mae_baseline']:+.3f}")
        if rows:
            w = sum(r["n"] for r in rows)
            md = sum(r["mae_decomp"] * r["n"] for r in rows) / w
            mb = sum(r["mae_baseline"] * r["n"] for r in rows) / w
            print(f"    ALL   n={w:5d}  decomposition {md:.3f}   raw EWMA {mb:.3f}   delta {md-mb:+.3f}")
            report["player"][tgt + "_pooled"] = {"n": w, "mae_decomp": md, "mae_baseline": mb}
    # ---- two pre-specified subgroup tests, fixed before looking at any subgroup result.
    # The decomposition's premise is that it helps when this game's team volume differs from the volume the
    # player's raw history was accumulated in, and when his role is unstable. If it cannot win in those two
    # places it cannot win anywhere, and no third subgroup will be tried.
    print("\nPRE-SPECIFIED SUBGROUP TESTS (both defined before any subgroup result was seen)")
    P = P.with_columns(
        vol_gap=(pl.col("proj_team_dropbacks") - pl.col("pit_team_dropbacks")).abs(),
        role_instability=(pl.col("pit_shrink_w")),
    )
    sub = {}
    for name, col, tgt, decomp, base in (("team volume unusual for this player", "vol_gap", "targets",
                                          "proj_targets_decomp", "ewma_targets"),
                                         ("role still unsettled (high shrinkage)", "role_instability", "targets",
                                          "proj_targets_decomp", "ewma_targets")):
        rows = []
        for S in EVAL:
            d = P.filter((pl.col("season") == S) & pl.col(decomp).is_not_null() &
                         pl.col("position").is_in(["RB", "WR", "TE"]) & (pl.col(base) >= 2.0))
            if d.height < 300:
                continue
            cut = d[col].quantile(0.75)
            d = d.filter(pl.col(col) >= cut)
            y = d[tgt].to_numpy().astype(float)
            rows.append({"season": S, "n": d.height,
                         "mae_decomp": float(np.abs(d[decomp].to_numpy() - y).mean()),
                         "mae_baseline": float(np.abs(d[base].to_numpy() - y).mean())})
        if rows:
            w = sum(r["n"] for r in rows)
            md = sum(r["mae_decomp"] * r["n"] for r in rows) / w
            mb = sum(r["mae_baseline"] * r["n"] for r in rows) / w
            wins = sum(1 for r in rows if r["mae_decomp"] < r["mae_baseline"])
            sub[name] = {"n": w, "mae_decomp": md, "mae_baseline": mb, "seasons_won": wins, "seasons": len(rows),
                         "by_season": rows}
            print(f"  top quartile, {name}: n={w} decomposition {md:.3f} vs raw EWMA {mb:.3f} "
                  f"(delta {md-mb:+.3f}); decomposition wins in {wins}/{len(rows)} seasons")
    report["subgroups"] = sub

    # ---- The multiplicative reconstruction fails. That does not settle whether the route/red-zone data
    # carries information the raw-count EWMA lacks -- only whether it should REPLACE it. Here the share
    # features are added ALONGSIDE the baseline in one ridge, walk-forward, on the full population.
    print("\nDO THE ROUTE AND RED-ZONE FEATURES ADD ANYTHING ON TOP OF THE BASELINE?")
    combo = {}
    for tgt, base, extra in (
        ("targets", "ewma_targets",
         ["pit_route_share", "pit_tprr", "pit_snap_share", "pit_rz_target_share", "pit_adot",
          "proj_team_dropbacks", "pit_shrink_w", "implied_total", "spread_team"]),
        ("carries", "ewma_carries",
         ["pit_carry_share", "pit_snap_share", "pit_rz_carry_share", "pit_i5_carry_share",
          "proj_team_rush_att", "pit_shrink_w", "implied_total", "spread_team"]),
    ):
        d = P.filter(pl.col("position").is_in(["RB", "WR", "TE"]) & pl.col("proj_team_dropbacks").is_not_null())
        sa = d["season"].to_numpy()
        y = d[tgt].to_numpy().astype(float)
        Xb = np.nan_to_num(d.select([base]).to_numpy().astype(float), nan=0.0)
        Xf = np.nan_to_num(d.select([base] + extra).to_numpy().astype(float), nan=0.0)
        pb = np.full(len(y), np.nan); pf = np.full(len(y), np.nan)
        for S in EVAL:
            tr = sa < S; te = sa == S
            if tr.sum() < 1000 or te.sum() == 0:
                continue
            pb[te] = predict(ridge(Xb[tr], y[tr], lam=5.0), Xb[te])
            pf[te] = predict(ridge(Xf[tr], y[tr], lam=5.0), Xf[te])
        rel = d[base].to_numpy() >= 2.0
        ok = np.isfinite(pb) & np.isfinite(pf) & rel
        combo[tgt] = {"n": int(ok.sum()),
                      "mae_baseline_only": float(np.abs(pb[ok] - y[ok]).mean()),
                      "mae_with_role_features": float(np.abs(pf[ok] - y[ok]).mean()),
                      "by_season": []}
        for S in EVAL:
            m = ok & (sa == S)
            if m.sum() < 200:
                continue
            combo[tgt]["by_season"].append({"season": S, "n": int(m.sum()),
                                            "base": float(np.abs(pb[m] - y[m]).mean()),
                                            "full": float(np.abs(pf[m] - y[m]).mean())})
        c = combo[tgt]
        wins = sum(1 for r in c["by_season"] if r["full"] < r["base"])
        c["seasons_won"] = wins
        print(f"  {tgt}: n={c['n']}  baseline alone {c['mae_baseline_only']:.4f}  "
              f"+ role features {c['mae_with_role_features']:.4f}  "
              f"(delta {c['mae_with_role_features']-c['mae_baseline_only']:+.4f}); "
              f"improves in {wins}/{len(c['by_season'])} seasons")
        for r in c["by_season"]:
            print(f"      {r['season']} n={r['n']:5d}  {r['base']:.4f} -> {r['full']:.4f}  ({r['full']-r['base']:+.4f})")
    report["role_features_on_top"] = combo
    json.dump(report, open(os.path.join(OUT, "results.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
