"""RESEARCH ONLY. Decompose the frozen DATA_ONLY (data_only-1.0.0) centre for 2026_03_ATL_GB into additive
per-feature contributions, from the archived three-arm snapshot rows on market-data. No refit, no tuning.

The model is a standardised ridge: pred = ym + sum_i beta_i * (x_i - xm_i) / xs_i, so the decomposition is exact.
We report each feature's contribution relative to (a) the training mean (the model's own baseline, ym) and
(b) a league-average matchup (x_i = 0 for d_* features; rest/div/neutral as recorded), which is the
football-meaningful zero. Usage: python decompose_data_only.py <dir with *.arm_games.jsonl.gz> <artifact.json> <out.json>
"""
import glob, gzip, json, os, sys

GAME = "2026_03_ATL_GB"
HORIZONS = {"T-24h": "20260924T012615Z", "T-6h": "20260924T180036Z", "T-90m": "20260924T224601Z",
            "T-30m": "20260924T234509Z"}


def contribs(model, feats, x):
    out = {}
    for f, b, m, s in zip(feats, model["beta"], model["xm"], model["xs"]):
        v = 0.0 if x.get(f) is None else float(x[f])
        out[f] = {"x": v, "beta_std": b, "xm": m, "xs": s,
                  "contrib_vs_train_mean": b * (v - m) / s,
                  "contrib_vs_zero": b * v / s}
    return out


def main(d, art_path, out_path):
    art = json.load(open(art_path))
    rows = {}
    for p in sorted(glob.glob(os.path.join(d, "*.arm_games.jsonl.gz"))):
        for line in gzip.open(p, "rt"):
            r = json.loads(line)
            if r.get("game_id") == GAME:
                rows[r["run_id"]] = r
    timeline, horizons = [], {}
    for run, r in sorted(rows.items()):
        a = r.get("arms") or {}
        if "DATA_ONLY" not in a or "CURRENT_MARKET_PRIOR" not in a:
            timeline.append({"run_id": run, "status": r.get("status"), "status_reason": r.get("status_reason")})
            continue
        cur, do, hy = a["CURRENT_MARKET_PRIOR"], a["DATA_ONLY"], a["HYBRID_30_DATA"]
        timeline.append({"run_id": run, "observed_at": r["observed_at"], "minutes_to_kickoff": round(r["minutes_to_kickoff"], 1),
                         "current_margin": cur.get("projected_home_margin"), "current_total": cur.get("projected_total"),
                         "current_source": cur.get("center_source"),
                         "consensus_spread": (cur.get("detail") or {}).get("consensus_spread_line"),
                         "consensus_total": (cur.get("detail") or {}).get("consensus_total_line"),
                         "data_only_margin": do.get("projected_home_margin"), "data_only_total": do.get("projected_total"),
                         "hybrid_margin": hy.get("projected_home_margin"), "hybrid_total": hy.get("projected_total"),
                         "latest_included_kickoff": (do.get("feature_cutoff") or {}).get("latest_included_kickoff_utc"),
                         "current_season_team_games": (do.get("input_data_manifest") or {}).get("current_season_team_games"),
                         "p_home_win": {k: (a[k].get("simulation") or {}).get("p_home_win") for k in a}})
    for h, run in HORIZONS.items():
        r = rows.get(run)
        if not r:
            horizons[h] = {"run_id": run, "status": "SNAPSHOT_NOT_FOUND"}
            continue
        do = r["arms"]["DATA_ONLY"]; x = do["detail"]["features"]
        cm = contribs(art["margin_model"], art["margin_features"], x)
        ct = contribs(art["total_model"], art["total_features"], x)
        pm = art["margin_model"]["ym"] + sum(c["contrib_vs_train_mean"] for c in cm.values())
        pt = art["total_model"]["ym"] + sum(c["contrib_vs_train_mean"] for c in ct.values())
        # league-average matchup baseline: all d_*/m_* = 0, context as recorded
        base_m = art["margin_model"]["ym"] + sum(c["contrib_vs_train_mean"] - c["contrib_vs_zero"] for c in cm.values())
        mkt = r["arms"]["CURRENT_MARKET_PRIOR"]["projected_home_margin"]
        horizons[h] = {"run_id": run, "recorded_margin": do["projected_home_margin"], "recomputed_margin": pm,
                       "recorded_total": do["projected_total"], "recomputed_total": pt,
                       "margin_intercept_ym": art["margin_model"]["ym"], "total_intercept_ym": art["total_model"]["ym"],
                       "league_average_matchup_margin": base_m,
                       "market_margin": mkt, "gap_vs_market": do["projected_home_margin"] - mkt,
                       "margin_contributions": cm, "total_contributions": ct}
    json.dump({"game_id": GAME, "artifact_sha": art["artifact_sha"], "horizons": horizons, "timeline": timeline},
              open(out_path, "w"), indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:4])
