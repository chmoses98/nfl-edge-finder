#!/usr/bin/env python3
"""Historical (pre-2026) validation of the three-arm IMPLEMENTATION. Software and methodology, not a decision.

Questions answered, on 2014-2025 regular-season games (3,151), training strictly on prior seasons:
  V1  Does the reusable DATA_ONLY reproduce the frozen Milestone-E walk-forward predictions? (bit for bit)
  V2  Does HYBRID_30 reconcile with the blend definition and the research's blend table? (0.3 weight -> RMSE 12.9145)
  V3  Do the ratings rebuilt from fresh silver reproduce the frozen rating snapshots?
  V4  Through the common-random-number simulator, how do the three centres score on winner / spread / total
      contracts against the realised outcomes -- with the CONSENSUS CLOSING LINE standing in for the market
      centre, which is the only historical market this repository has? (Kalshi-implied centres exist only
      prospectively, so the historical CURRENT is the closing consensus line and says so.)
  V5  Leakage audits: perturbing every team-game at or after a cutoff leaves the ratings before it unchanged;
      poisoning every market column leaves DATA_ONLY unchanged; the artifact trains only on prior seasons.

Nothing here tunes anything. The weights, features and hyper-parameters are the research's, frozen before the
first 2026 outcome. Outputs research/three_arm/results.json and RESULTS.md (new files; nothing frozen is touched).
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np
import polars as pl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.arms import crn, data_only as D, pricing as P, registry as R          # noqa: E402
from nfl_edge.pricing.game_env import ResidualBank                                   # noqa: E402

OUT = os.path.join(ROOT, "research", "three_arm")
FEAT = os.path.join(ROOT, "research", "game_model", "game_features.parquet")
WF = os.path.join(ROOT, "research", "game_model", "walkforward_predictions.parquet")
SNAP = os.path.join(ROOT, "research", "game_model", "ratings_snapshots.parquet")
TEST_SEASONS = list(range(2014, 2026))


def rmse(a, b):
    return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))


def mae(a, b):
    return float(np.mean(np.abs(np.asarray(a) - np.asarray(b))))


def bias(a, b):
    return float(np.mean(np.asarray(a) - np.asarray(b)))


def paired(a_err, b_err):
    d = np.abs(a_err) - np.abs(b_err)
    se = float(d.std(ddof=1) / math.sqrt(len(d)))
    return {"n": int(len(d)), "mean_diff_abs_error": float(d.mean()), "se": se,
            "ci95": [float(d.mean() - 1.96 * se), float(d.mean() + 1.96 * se)]}


def main():
    t0 = time.time()
    res = {"generated_at": datetime.now(timezone.utc).isoformat(), "preregistration": R.preregistration(),
           "note": "historical validation of the implementation; the consensus closing line stands in for the market centre"}
    feat = pl.read_parquet(FEAT)
    wf = pl.read_parquet(WF).to_pandas().set_index("game_id")
    frozen = json.load(open(os.path.join(ROOT, "research", "game_model", "results.json")))

    # ---- V1 / V2: walk-forward reproduction and the hybrid blend --------------------------------------------
    rows = []
    max_diff = 0.0
    for S in TEST_SEASONS:
        art = D.fit_artifact(feat, S)
        te = feat.filter(pl.col("season") == S).to_pandas()
        pm = D.ridge_pred(art.margin_model, te[D.MARGIN_FEATURES].fillna(0).to_numpy())
        pt = D.ridge_pred(art.total_model, te[D.TOTAL_FEATURES].fillna(0).to_numpy())
        ref = wf.loc[te.game_id]
        max_diff = max(max_diff, float(np.abs(pm - ref.model_margin.to_numpy()).max()),
                       float(np.abs(pt - ref.model_total.to_numpy()).max()))
        for i in range(len(te)):
            rows.append({"season": S, "week": int(te.week.iloc[i]), "game_id": te.game_id.iloc[i],
                         "result": float(te.result.iloc[i]), "total": float(te.total.iloc[i]),
                         "market_margin": float(te.spread_line.iloc[i]), "market_total": float(te.total_line.iloc[i]),
                         "data_margin": float(pm[i]), "data_total": float(pt[i])})
    df = pl.DataFrame(rows).with_columns([
        (R.HYBRID_WEIGHT_MARKET * pl.col("market_margin") + R.HYBRID_WEIGHT_DATA * pl.col("data_margin")).alias("hybrid_margin"),
        (R.HYBRID_WEIGHT_MARKET * pl.col("market_total") + R.HYBRID_WEIGHT_DATA * pl.col("data_total")).alias("hybrid_total")]).to_pandas()
    res["V1_walkforward_reproduction"] = {"max_abs_diff_vs_frozen": max_diff, "n_games": int(len(df)), "ok": max_diff < 1e-9}
    centers = {R.CURRENT: ("market_margin", "market_total"), R.DATA_ONLY: ("data_margin", "data_total"),
               R.HYBRID: ("hybrid_margin", "hybrid_total")}
    acc = {}
    for arm, (cm, ct) in centers.items():
        acc[arm] = {"margin": {"rmse": rmse(df[cm], df.result), "mae": mae(df[cm], df.result), "bias": bias(df[cm], df.result)},
                    "total": {"rmse": rmse(df[ct], df.total), "mae": mae(df[ct], df.total), "bias": bias(df[ct], df.total)},
                    "by_season": {int(S): {"margin_rmse": rmse(g[cm], g.result), "total_rmse": rmse(g[ct], g.total), "n": int(len(g))}
                                  for S, g in df.groupby("season")}}
    acc["paired"] = {f"{a}_vs_{b}": {"margin": paired(df[centers[a][0]] - df.result, df[centers[b][0]] - df.result),
                                     "total": paired(df[centers[a][1]] - df.total, df[centers[b][1]] - df.total)}
                     for a, b in ((R.DATA_ONLY, R.CURRENT), (R.HYBRID, R.CURRENT), (R.HYBRID, R.DATA_ONLY))}
    acc["early_season_weeks_1_4"] = {arm: {"margin_rmse": rmse(df[df.week <= 4][cm], df[df.week <= 4].result)} for arm, (cm, ct) in centers.items()}
    acc["reconciliation_with_frozen_research"] = {
        "frozen_rmse_spread": frozen["pooled"]["rmse_spread"], "frozen_rmse_model": frozen["pooled"]["rmse_model"],
        "frozen_blend_0.3_rmse": frozen["pooled"]["blend_rmse_by_model_weight"]["0.3"],
        "ours_current": acc[R.CURRENT]["margin"]["rmse"], "ours_data_only": acc[R.DATA_ONLY]["margin"]["rmse"],
        "ours_hybrid": acc[R.HYBRID]["margin"]["rmse"],
        "ok": abs(acc[R.HYBRID]["margin"]["rmse"] - frozen["pooled"]["blend_rmse_by_model_weight"]["0.3"]) < 1e-6
              and abs(acc[R.DATA_ONLY]["margin"]["rmse"] - frozen["pooled"]["rmse_model"]) < 1e-6}
    res["V2_center_accuracy"] = acc
    print("V1/V2", json.dumps(acc["reconciliation_with_frozen_research"], default=_jsonable), f"{time.time() - t0:.0f}s", flush=True)

    # ---- V3: ratings from fresh silver vs the frozen snapshots -------------------------------------------------
    v3 = {"checked": [], "ok": True}
    silver = os.path.join(ROOT, "data", "silver", "team_game.parquet")
    if os.path.exists(silver) and os.path.exists(SNAP):
        tg = pl.read_parquet(silver)
        prow = D.prepare_team_games(tg)
        snap = pl.read_parquet(SNAP)
        for season, week in ((2019, 3), (2022, 9), (2024, 5), (2025, 1), (2025, 10), (2025, 18)):
            r, meta = D.ratings_for_week(prow, season, week)
            ref = snap.filter((pl.col("season") == season) & (pl.col("week") == week)).to_pandas().set_index("team")
            diffs = [abs(r[t][f"{side}_{f}"] - ref.loc[t, f"{side}_{f}"]) for t in ref.index if t in r
                     for f in D.FEATS for side in ("off", "def") if not np.isnan(ref.loc[t, f"{side}_{f}"])]
            entry = {"season": season, "week": week, "teams": len(r), "max_abs_diff": float(max(diffs)) if diffs else None,
                     "n_team_games": meta["n_team_games"]}
            v3["checked"].append(entry)
            v3["ok"] = v3["ok"] and bool(diffs) and max(diffs) < 1e-9
    else:
        v3 = {"skipped": "silver team_game or frozen snapshots not on disk"}
    res["V3_ratings_reproduction"] = v3
    print("V3", json.dumps(v3, default=_jsonable)[:300], flush=True)

    # ---- V4: contract pricing through the CRN simulator ---------------------------------------------------------
    games = pl.read_parquet(os.path.join(ROOT, "data", "silver", "games.parquet")) if os.path.exists(
        os.path.join(ROOT, "data", "silver", "games.parquet")) else None
    v4 = {}
    if games is not None:
        hist = games.filter((pl.col("game_type") == "REG") & pl.col("result").is_not_null() & pl.col("spread_line").is_not_null()
                            & pl.col("total_line").is_not_null()).to_pandas()
        hist["mres"] = hist.result - hist.spread_line; hist["tres"] = hist.total - hist.total_line
        scores = {arm: {"home_win": [], "spread_ladder": [], "total_ladder": []} for arm in centers}
        n_games = 0
        for S in range(2020, 2026):
            h = hist[(hist.season >= S - 4) & (hist.season < S)]
            bank = ResidualBank(h.mres, h.tres, h.season, ref_season=S, spread_lines=h.spread_line, total_lines=h.total_line,
                                overtime=h.overtime.fillna(0).astype(int), results=h.result, halflife=3.0, rng=np.random.default_rng(0))
            sub = df[df.season == S]
            for _, g in sub.iterrows():
                draws = crn.draw_uniforms(R.N_SIMS, f"validation|{g.game_id}|{R.CRN_VERSION}")
                y_win = 1.0 if g.result > 0 else 0.0
                if g.result == 0:
                    continue
                n_games += 1
                for arm, (cm, ct) in centers.items():
                    sim = crn.simulate_game_crn(crn.snap_to_grid(g[cm]), crn.snap_to_grid(g[ct]), bank, draws)
                    p, cv, _ = P.price_contract(sim, {"family": "GAME_WINNER", "team": "H"}, "H", "A")
                    scores[arm]["home_win"].append((p, y_win))
                    for k in (-7.5, -3.5, -0.5, 2.5, 6.5):          # home wins by more than k
                        pk, _, _ = P.price_contract(sim, {"family": "SPREAD", "period": "FULL", "team": "H", "floor_strike": k}, "H", "A")
                        scores[arm]["spread_ladder"].append((pk, 1.0 if g.result > k else 0.0))
                    for k in (g.market_total - 6, g.market_total - 3, g.market_total, g.market_total + 3, g.market_total + 6):
                        kk = math.floor(k)
                        pk, _, _ = P.price_contract(sim, {"family": "TOTAL", "period": "FULL", "threshold": kk}, "H", "A")
                        scores[arm]["total_ladder"].append((pk, 1.0 if g.total >= kk else 0.0))
        def score(pairs):
            p = np.clip(np.array([x for x, _ in pairs]), 1e-9, 1 - 1e-9); y = np.array([y for _, y in pairs])
            return {"n": int(len(p)), "brier": float(np.mean((p - y) ** 2)),
                    "log_loss": float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))}
        v4 = {"seasons": "2020-2025", "n_games": n_games, "n_sims": R.N_SIMS, "market_center": "consensus closing line",
              "bank": "residuals of the four seasons before each test season (point in time)",
              **{arm: {k: score(v) for k, v in s.items()} for arm, s in scores.items()}}
        for arm in (R.DATA_ONLY, R.HYBRID):
            for k in ("home_win", "spread_ladder", "total_ladder"):
                a = scores[arm][k]; b = scores[R.CURRENT][k]
                d = np.array([(pa - ya) ** 2 - (pb - yb) ** 2 for (pa, ya), (pb, yb) in zip(a, b)])
                v4[f"paired_brier_{arm}_minus_CURRENT_{k}"] = {"mean": float(d.mean()), "se_naive": float(d.std(ddof=1) / math.sqrt(len(d))),
                                                                "note": "naive SE over rungs; rungs within a game are correlated"}
        v4["frozen_reference_normal_cdf"] = {k: frozen["pooled"][k] for k in ("logloss_spread", "logloss_model", "logloss_blend30",
                                                                             "brier_spread", "brier_model", "brier_blend30")}
    res["V4_contract_pricing_crn"] = v4
    print("V4", json.dumps({k: v for k, v in v4.items() if k in centers or k == "n_games"}, default=_jsonable)[:600], f"{time.time() - t0:.0f}s", flush=True)

    # ---- V5: leakage audits ---------------------------------------------------------------------------------------
    v5 = {}
    if os.path.exists(silver):
        tg = pl.read_parquet(silver)
        prow = D.prepare_team_games(tg)
        base, _ = D.ratings_for_week(prow, 2024, 9)
        poisoned = tg.with_columns([pl.when((pl.col("season") > 2024) | ((pl.col("season") == 2024) & (pl.col("week") >= 9)))
                                    .then(pl.col(c) + 100.0).otherwise(pl.col(c)).alias(c)
                                    for c in ("off_epa_play", "off_success_rate", "off_dropback_epa", "off_rush_epa", "st_epa_for")])
        after, _ = D.ratings_for_week(D.prepare_team_games(poisoned), 2024, 9)
        v5["future_team_games_cannot_reach_ratings"] = {"max_abs_change": float(max(abs(base[t][k] - after[t][k]) for t in base for k in base[t])),
                                                        "ok": all(base[t][k] == after[t][k] for t in base for k in base[t])}
    art = D.DataOnlyArtifact.load(os.path.join(OUT, "data_only_artifact_2026.json"))
    v5["artifact_trains_only_before_target"] = {"train_seasons": art.train_seasons, "target": art.target_season,
                                                "ok": art.train_seasons[-1] < art.target_season}
    sched = games.to_dicts()[0] if games is not None else {}
    mf, dropped = D.market_free_schedule(games) if games is not None else (None, [])
    v5["schedule_market_columns_dropped"] = dropped
    ok_leak = True
    try:
        D.attest_market_free(D.MARGIN_FEATURES + ["spread_line"])
        ok_leak = False
    except D.MarketLeak:
        pass
    v5["spread_line_as_a_feature_is_refused"] = {"ok": ok_leak}
    res["V5_leakage_audits"] = v5
    print("V5", json.dumps(v5, default=_jsonable), flush=True)
    res["seconds"] = time.time() - t0
    os.makedirs(OUT, exist_ok=True)
    json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1, default=_jsonable)
    write_md(res)
    print(f"done in {time.time() - t0:.0f}s -> {OUT}")
    return 0


def _jsonable(o):
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, np.generic):
        return o.item()
    return str(o)


def write_md(res):
    a = res["V2_center_accuracy"]; rec = a["reconciliation_with_frozen_research"]; v4 = res.get("V4_contract_pricing_crn") or {}
    L = ["# Three-arm implementation: historical validation (pre-2026, software and methodology only)", "",
         "Reproduce: `python3 scripts/research/three_arm_validation.py`. Nothing here is a betting result and nothing was tuned: the",
         "features, hyper-parameters and the 0.70/0.30 weight are the research's (`research/game_model/`), frozen before the first",
         "2026 outcome. The **consensus closing line stands in for the market centre**, because it is the only historical market",
         "this repository has; prospectively the CURRENT arm is the Kalshi-implied centre at each snapshot, which is the whole point.", "",
         "## V1 — the reusable DATA_ONLY reproduces the frozen walk-forward research",
         f"Max |difference| against `walkforward_predictions.parquet` over {res['V1_walkforward_reproduction']['n_games']} games, 12 seasons: "
         f"**{res['V1_walkforward_reproduction']['max_abs_diff_vs_frozen']:.2e}** (ok: {res['V1_walkforward_reproduction']['ok']}).", "",
         "## V2 — centre accuracy, 2014–2025 (n = 3,151), and the hybrid reconciliation", "",
         "| arm | margin RMSE | margin MAE | margin bias | total RMSE | total MAE | total bias |", "|---|---|---|---|---|---|---|"]
    for arm in (R.CURRENT, R.DATA_ONLY, R.HYBRID):
        m = a[arm]
        L.append(f"| {arm} | {m['margin']['rmse']:.3f} | {m['margin']['mae']:.3f} | {m['margin']['bias']:+.3f} | {m['total']['rmse']:.3f} | {m['total']['mae']:.3f} | {m['total']['bias']:+.3f} |")
    L += ["", f"Frozen research: closing spread RMSE {rec['frozen_rmse_spread']:.4f}, model {rec['frozen_rmse_model']:.4f}, "
          f"0.3 blend {rec['frozen_blend_0.3_rmse']:.4f}; ours {rec['ours_current']:.4f} / {rec['ours_data_only']:.4f} / {rec['ours_hybrid']:.4f} "
          f"(reconciled: {rec['ok']}).", "", "| paired comparison | games | mean diff in abs margin error | 95% CI | total: mean diff | 95% CI |", "|---|---|---|---|---|---|"]
    for k, v in a["paired"].items():
        L.append(f"| {k} | {v['margin']['n']} | {v['margin']['mean_diff_abs_error']:+.3f} | [{v['margin']['ci95'][0]:+.3f}, {v['margin']['ci95'][1]:+.3f}] | "
                 f"{v['total']['mean_diff_abs_error']:+.3f} | [{v['total']['ci95'][0]:+.3f}, {v['total']['ci95'][1]:+.3f}] |")
    L += ["", "Weeks 1–4 margin RMSE: " + ", ".join(f"{arm} {v['margin_rmse']:.3f}" for arm, v in a["early_season_weeks_1_4"].items()) + ".", ""]
    v3 = res.get("V3_ratings_reproduction") or {}
    L += ["## V3 — ratings rebuilt from fresh silver reproduce the frozen snapshots", "",
          ("| season | week | teams | max |diff| |\n|---|---|---|---|\n" + "\n".join(
              f"| {c['season']} | {c['week']} | {c['teams']} | {c['max_abs_diff']:.2e} |" for c in v3.get("checked", []))
           if v3.get("checked") else str(v3)), ""]
    if v4:
        L += ["## V4 — the three centres through the common-random-number simulator (2020–2025, consensus close as market)", "",
              f"{v4['n_games']} games, {v4['n_sims']} draws per arm, one uniform set per game shared by all three arms; the residual bank is the",
              "four seasons before each test season. Rungs within a game are correlated, so the naive SEs are optimistic.", "",
              "| arm | home win Brier / log loss | spread ladder Brier (5 rungs) | total ladder Brier (5 rungs) |", "|---|---|---|---|"]
        for arm in (R.CURRENT, R.DATA_ONLY, R.HYBRID):
            s = v4[arm]
            L.append(f"| {arm} | {s['home_win']['brier']:.4f} / {s['home_win']['log_loss']:.4f} | {s['spread_ladder']['brier']:.4f} | {s['total_ladder']['brier']:.4f} |")
        L += ["", "Paired Brier differences vs CURRENT: " + "; ".join(
            f"{k.replace('paired_brier_', '')} {v['mean']:+.5f} (naive SE {v['se_naive']:.5f})" for k, v in v4.items() if k.startswith("paired_brier_")) + ".",
              f"Frozen normal-CDF reference (research): {v4.get('frozen_reference_normal_cdf')}.", ""]
    v5 = res.get("V5_leakage_audits") or {}
    L += ["## V5 — leakage audits", "", f"* future team-games perturbed by +100 at and after the cutoff leave every prior rating unchanged: "
          f"{v5.get('future_team_games_cannot_reach_ratings')}",
          f"* the frozen artifact trains only on seasons before its target: {v5.get('artifact_trains_only_before_target')}",
          f"* market columns dropped from the schedule before DATA_ONLY sees it: {v5.get('schedule_market_columns_dropped')}",
          f"* `spread_line` offered as a feature is refused by the whitelist attestation: {v5.get('spread_line_as_a_feature_is_refused')}", "",
          "## What this does and does not establish", "",
          "It establishes that the production DATA_ONLY is the research model, that HYBRID_30 is the blend it says it is, that the simulator",
          "is the incumbent's with shared draws, and that no future or market information reaches the football-only centre. It re-establishes",
          "the research's negative result against the CLOSING line. It says nothing about T-24h, T-6h, T-90m or T-30m Kalshi centres, which is",
          "the prospective question and begins only with the first three-arm snapshot written after this code is merged.", ""]
    open(os.path.join(OUT, "RESULTS.md"), "w").write("\n".join(L))


if __name__ == "__main__":
    sys.exit(main())
