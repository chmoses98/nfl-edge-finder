#!/usr/bin/env python3
"""Milestone F: which distribution family gives calibrated P(Y >= k) for player-prop ladders?

Walk-forward (train seasons < S, test season S, S = 2020..2025) comparison of distribution
families for QB / RB / WR / TE game stats conditional on a weak, leakage-free EWMA projection.
Hyperparameters (EWMA half-life, season carry, shrinkage pseudo-games) are chosen on
2016-2019 only.  Outputs research/player_distributions/{results.json, tables.md,
research_table.parquet}.  RESULTS.md (narrative) is written from these.
"""
from __future__ import annotations
import json, os, sys, time
import numpy as np, pandas as pd
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.research import player_distributions as pdst  # noqa

OUT = os.path.join(ROOT, "research", "player_distributions")
os.makedirs(OUT, exist_ok=True)
WARMUP = range(2013, 2016)          # position priors + EWMA warm-up only; never evaluated
TEST_SEASONS = list(range(2020, 2026))
TUNE_SEASONS = (2016, 2019)         # hyperparameter selection window (inclusive)
NSIMS = int(os.environ.get("NSIMS", 4000))
STATS = sys.argv[1:] or list(pdst.STAT_SPECS)
T0 = time.time()
log = lambda *a: print(f"[{time.time()-T0:6.0f}s]", *a, flush=True)

df = pdst.load_player_games(ROOT, range(2013, 2026))
priors = pdst.position_priors(df, WARMUP)
log("player-games", df.shape, "zero rows added", df.attrs["n_zero_rows"])

# ------------------------------------------------------------------ 1. hyperparameter selection (<= 2019)
TUNE_STATS = [("receiving_yards", "REC", 3.0, "targets"), ("targets", "REC", 3.0, "targets"), ("receptions", "REC", 3.0, "targets"),
              ("rushing_yards", "RB", 6.0, "carries"), ("carries", "RB", 6.0, "carries"),
              ("passing_yards", "QB", 0.0, "attempts"), ("attempts", "QB", 0.0, "attempts"), ("passing_tds", "QB", 0.0, "attempts")]
grid = [(hl, carry, k) for hl in (3.0, 4.0, 6.0, 9.0) for carry in (0.35, 0.6) for k in (2.0, 5.0)]
tune_rows = []
for hl, carry, k in grid:
    d = pdst.add_ewma_features(df, hl, carry, k, priors)
    sub = d[(d.season >= TUNE_SEASONS[0]) & (d.season <= TUNE_SEASONS[1])]
    rec = {"halflife": hl, "season_carry": carry, "shrink_k": k}
    for stat, pop, min_opp, opp in TUNE_STATS:
        m = pdst.population_mask(sub, pop) & (sub[f"ewma_{opp}"].to_numpy() >= min_opp)
        y = np.clip(sub.loc[m, stat].to_numpy(float), 0, None); mu = sub.loc[m, f"ewma_{stat}"].to_numpy()
        rec[f"mae_{stat}"] = float(np.mean(np.abs(y - mu)))
    tune_rows.append(rec)
tune = pd.DataFrame(tune_rows)
mae_cols = [c for c in tune.columns if c.startswith("mae_")]
tune["score"] = (tune[mae_cols] / tune[mae_cols].min()).mean(axis=1)   # mean relative MAE across stats
best = tune.sort_values("score").iloc[0]
HL, CARRY, K = float(best.halflife), float(best.season_carry), float(best.shrink_k)
log("hyperparameters chosen on 2016-2019:", dict(halflife=HL, season_carry=CARRY, shrink_k=K))
print(tune.sort_values("score").to_string(index=False))

# ------------------------------------------------------------------ 2. research table
d = pdst.add_ewma_features(df, HL, CARRY, K, priors)
d = d[d.season >= 2016].reset_index(drop=True)
d.to_parquet(os.path.join(OUT, "research_table.parquet"))
data_summary = {
    "rows_2016_2025": int(len(d)), "zero_rows_added_2016_2025": int(d.zero_row.sum()),
    "rows_by_position": d.position.value_counts().to_dict(),
    "qb_starter_rows": int((d.qb_starter & (d.position == "QB")).sum()),
    "negative_yardage_rows_clipped": {"rushing_yards_RB": int(((d.position == "RB") & (d.rushing_yards < 0)).sum()),
                                      "receiving_yards_REC": int((d.position.isin(["RB", "WR", "TE"]) & (d.receiving_yards < 0)).sum())},
    "first_game_rows_full_prior": int((d.n_prior == 0).sum()),
    "mean_shrink_w_by_position": d.groupby("position").shrink_w.mean().round(3).to_dict(),
}
log("research table", d.shape)

# ------------------------------------------------------------------ 3. walk-forward family comparison
results = {"config": {"halflife": HL, "season_carry": CARRY, "shrink_k": K, "nsims": NSIMS, "test_seasons": TEST_SEASONS,
                      "tuning_table": tune.round(4).to_dict(orient="records"), "warmup_seasons": [2013, 2015],
                      "tune_seasons": list(TUNE_SEASONS)},
           "data": data_summary, "stats": {}}
for name in STATS:
    spec = pdst.STAT_SPECS[name]
    log("==", name, spec.pop, spec.kind, "thresholds", spec.thresholds)
    r = pdst.run_stat_walkforward(d, spec, TEST_SEASONS, nsims=NSIMS, verbose=log)
    fams = {}
    for fam, subs in r["per_season"].items():
        if not subs["all"]:
            continue
        fams[fam] = {"all": pdst.aggregate(subs["all"]), "elig": pdst.aggregate(subs["elig"])}
    # choice rule: lowest ladder Brier on the prop-relevant subset; ties (<0.1% rel.) broken by tail bucket ratio, then CRPS
    cand = [f for f in fams if f != "climatology"]
    def key(f):
        e = fams[f]["elig"]; tail = e["buckets"].get("tail", {"ratio": 1.0})["ratio"]
        return (round(e["brier"], 4), abs(np.log(max(tail, 1e-3))), e["crps"])
    order = sorted(cand, key=key)
    results["stats"][name] = {"spec": {"col": spec.col, "pop": spec.pop, "kind": spec.kind, "opp": spec.opp, "eff": spec.eff,
                                       "thresholds": spec.thresholds, "elig_min_opp": spec.elig_min_opp},
                              "families": fams, "chosen": order[0], "ranking_by_elig_brier": order, "params": r["params"]}
    with open(os.path.join(OUT, "results.json"), "w") as f:
        json.dump(results, f, indent=1, default=float)
    e = fams[order[0]]["elig"]
    log(f"   chosen {order[0]}: elig brier {e['brier']:.4f} crps {e['crps']:.3f} tail ratio {e['buckets'].get('tail', {}).get('ratio')}")

# ------------------------------------------------------------------ 4. markdown tables
def fmt(x, nd=3):
    return "" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{nd}f}"

lines = []
lines.append(f"Hyperparameters chosen on {TUNE_SEASONS[0]}-{TUNE_SEASONS[1]}: half-life={HL} games, season carry={CARRY}, shrink k={K} pseudo-games. "
             f"Test seasons {TEST_SEASONS[0]}-{TEST_SEASONS[-1]}, MC sims={NSIMS}.\n")
lines.append("## Tuning table (mean relative MAE of raw EWMA vs outcome, 2016-2019)\n")
tt = tune.sort_values("score")
lines.append("| halflife | carry | k | score | " + " | ".join(c[4:] for c in mae_cols) + " |")
lines.append("|---|---|---|---|" + "---|" * len(mae_cols))
for _, row in tt.iterrows():
    lines.append(f"| {row.halflife:g} | {row.season_carry:g} | {row.shrink_k:g} | {row.score:.4f} | " + " | ".join(f"{row[c]:.2f}" for c in mae_cols) + " |")
lines.append("")
for name, R in results["stats"].items():
    sp = R["spec"]
    for sub, label in (("elig", "prop-relevant subset"), ("all", "all population rows")):
        n = next(iter(R["families"].values()))[sub]["n"]
        lines.append(f"### {name} ({sp['pop']}, {sp['kind']}) - {label}, n={n}, test {TEST_SEASONS[0]}-{TEST_SEASONS[-1]}\n")
        lines.append("| family | CRPS | log score | PIT KS | PIT chi2 p | ladder Brier | rel. slope | rel. intercept | ECE | low pred/obs | mid pred/obs | tail pred/obs |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for fam in R["ranking_by_elig_brier"] + ["climatology"]:
            e = R["families"][fam][sub]; b = e["buckets"]
            def po(k):
                return f"{b[k]['pred']:.3f}/{b[k]['obs']:.3f}" if k in b else "-"
            mark = "**" if fam == R["chosen"] else ""
            lines.append(f"| {mark}{fam}{mark} | {fmt(e['crps'])} | {fmt(e['logscore'])} | {fmt(e['pit_ks'])} | {fmt(e['pit_chi2_p'],3)} | {fmt(e['brier'],4)} | "
                         f"{fmt(e['rel_slope'],2)} | {fmt(e['rel_intercept'],3)} | {fmt(e['ece'])} | {po('low')} | {po('mid')} | {po('tail')} |")
        lines.append("")
    # per-threshold table (elig): predicted vs observed for each family
    lines.append(f"#### {name}: per-rung P(Y>=k) predicted / observed (prop-relevant subset)\n")
    fams = R["ranking_by_elig_brier"]
    lines.append("| k | obs | " + " | ".join(fams) + " |")
    lines.append("|---|---|" + "---|" * len(fams))
    ths = R["families"][fams[0]]["elig"]["thresholds"]
    for i, t in enumerate(ths):
        lines.append(f"| {t['k']} | {t['obs']:.3f} | " + " | ".join(f"{R['families'][f]['elig']['thresholds'][i]['pred']:.3f}" for f in fams) + " |")
    lines.append("")
    lines.append(f"CRPS by test season (prop-relevant): " + "; ".join(
        f"{f}: " + ", ".join(f"{s}={v}" for s, v in R["families"][f]["elig"]["crps_by_season"].items()) for f in fams[:3]) + "\n")
with open(os.path.join(OUT, "tables.md"), "w") as f:
    f.write("\n".join(lines))
log("done")
