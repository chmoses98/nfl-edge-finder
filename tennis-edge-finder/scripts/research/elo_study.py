#!/usr/bin/env python3
"""Walk-forward Elo study on the canonical match table (no leakage: every prediction uses only earlier matches).

Variants: naive (rank-based), standard Elo, surface-blended Elo, level-aware K, level prior.
Evaluation window: seasons >= --eval-from (default 2015) after warm-up from --min-year. Report Brier / log-loss /
calibration per variant, per tour-level and per surface, with paired bootstrap vs the plain Elo baseline.
Writes research/elo_study/RESULTS.md and predictions parquet for downstream (hybrid / market comparison).
"""
from __future__ import annotations
import argparse, json, os, sys, time
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, PROJ)
from tennis_edge.models.elo import Elo, EloConfig, match_sort_key
from tennis_edge.eval.metrics import summary, bootstrap_diff


def rank_baseline(m: pd.DataFrame) -> np.ndarray:
    """P(winner) from log-rank difference with a fixed, non-fitted slope (documented naive baseline)."""
    wr = pd.to_numeric(m["winner_rank"], errors="coerce").astype(float).fillna(1500).clip(lower=1)
    lr = pd.to_numeric(m["loser_rank"], errors="coerce").astype(float).fillna(1500).clip(lower=1)
    x = np.log(lr.to_numpy()) - np.log(wr.to_numpy())          # >0 when winner better ranked
    return np.nan_to_num(1 / (1 + np.exp(-0.9 * x)), nan=0.5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matches", default=os.path.join(PROJ, "data", "processed", "matches.parquet"))
    ap.add_argument("--tour", default="ATP")
    ap.add_argument("--eval-from", type=int, default=2015)
    ap.add_argument("--out", default=os.path.join(PROJ, "research", "elo_study"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    m = pd.read_parquet(a.matches)
    m = m[(m.tour == a.tour) & (m.outcome_type != "WALKOVER") & m.tourney_date.notna() & (m.id_system == "sackmann")].copy()
    m["tourney_date"] = pd.to_datetime(m["tourney_date"]).dt.date
    m = match_sort_key(m)
    ev = (m["season"] >= a.eval_from).to_numpy()
    y = np.ones(int(ev.sum()))          # rows are winner-first; p = P(winner)
    variants = {
        "elo_plain": EloConfig(use_surface=False, use_level_k=False, use_level_prior=False),
        "elo_levelprior": EloConfig(use_surface=False, use_level_k=False, use_level_prior=True),
        "elo_surface": EloConfig(use_surface=True, use_level_k=False, use_level_prior=True),
        "elo_surface_levelk": EloConfig(use_surface=True, use_level_k=True, use_level_prior=True),
        "elo_surface_k_hi": EloConfig(k0=350, use_surface=True, use_level_k=True, use_level_prior=True),
        "elo_surface_k_lo": EloConfig(k0=180, use_surface=True, use_level_k=True, use_level_prior=True),
    }
    preds = pd.DataFrame({"match_key": m["match_key"].to_numpy()[ev], "season": m["season"].to_numpy()[ev], "level": m["level_canonical"].to_numpy()[ev],
                          "surface": m["surface"].to_numpy()[ev], "round": m["round"].to_numpy()[ev]})
    preds["p_rank"] = rank_baseline(m)[ev]
    results = {}
    for name, cfg in variants.items():
        t0 = time.time()
        r = Elo(cfg).run(m)
        p = r["p_winner"].to_numpy()[ev]
        preds[f"p_{name}"] = p
        preds[f"n_min_{name}"] = np.minimum(r["n_w"].to_numpy()[ev], r["n_l"].to_numpy()[ev])
        results[name] = summary(y, p); results[name]["seconds"] = round(time.time() - t0, 1)
        print(name, results[name], flush=True)
    results["rank_baseline"] = summary(y, preds["p_rank"].to_numpy())
    # symmetric evaluation: randomise orientation so accuracy/calibration are not trivially 'winner-first'
    rng = np.random.default_rng(0); flip = rng.random(len(preds)) < 0.5
    ysym = (~flip).astype(float)
    sym = {}
    for c in [c for c in preds.columns if c.startswith("p_")]:
        p = preds[c].to_numpy(); ps = np.where(flip, 1 - p, p)
        sym[c[2:]] = summary(ysym, ps)
    # bootstrap vs plain elo
    boots = {}
    base = preds["p_elo_plain"].to_numpy()
    for c in [c for c in preds.columns if c.startswith("p_") and c != "p_elo_plain"]:
        boots[c[2:]] = bootstrap_diff(y, preds[c].to_numpy(), base, n_boot=300)
    # breakdowns
    best = min(sym, key=lambda k: sym[k]["log_loss"])
    by_level = {}; by_surface = {}; by_season = {}
    pbest = np.where(flip, 1 - preds[f"p_{best}"], preds[f"p_{best}"]); pbase = np.where(flip, 1 - preds["p_elo_plain"], preds["p_elo_plain"])
    for key, col, store in (("level", "level", by_level), ("surface", "surface", by_surface), ("season", "season", by_season)):
        for v, g in preds.groupby(col).groups.items():
            idx = np.asarray(list(g))
            if len(idx) < 200:
                continue
            store[str(v)] = {"n": int(len(idx)), f"{best}": summary(ysym[idx], pbest[idx]), "elo_plain": summary(ysym[idx], pbase[idx])}
    preds.to_parquet(os.path.join(a.out, f"predictions_{a.tour}.parquet"), index=False)
    out = {"tour": a.tour, "eval_from": a.eval_from, "n_eval": int(ev.sum()), "n_total": int(len(m)), "variants": {k: v.__dict__ for k, v in variants.items()},
           "winner_first_scores": results, "symmetric_scores": sym, "bootstrap_vs_elo_plain": boots, "best_by_logloss": best,
           "by_level": by_level, "by_surface": by_surface, "by_season": by_season}
    json.dump(out, open(os.path.join(a.out, f"results_{a.tour}.json"), "w"), indent=1, default=str)
    lines = [f"# Elo walk-forward study ({a.tour})", "", f"Matches: {len(m)} from {m.season.min()}; evaluated {int(ev.sum())} matches in seasons >= {a.eval_from}.",
             "Orientation randomised (symmetric scores). Ratings use only matches strictly before each prediction (chronological replay).", "",
             "| variant | n | brier | log_loss | accuracy | ECE | cal_slope | cal_intercept |", "|---|---|---|---|---|---|---|---|"]
    for k, v in sorted(sym.items(), key=lambda kv: kv[1]["log_loss"]):
        lines.append(f"| {k} | {v['n']} | {v['brier']:.4f} | {v['log_loss']:.4f} | {v['accuracy']:.4f} | {v['ece']:.4f} | {v['cal_slope']:.3f} | {v['cal_intercept']:.3f} |")
    lines += ["", "## Paired bootstrap (Brier diff vs elo_plain; negative = better)", "", "| variant | diff | 95% CI | P(better) |", "|---|---|---|---|"]
    for k, v in boots.items():
        lines.append(f"| {k} | {v['diff']:+.5f} | [{v['ci_low']:+.5f}, {v['ci_high']:+.5f}] | {v['p_better']:.2f} |")
    for title, store in (("By level", by_level), ("By surface", by_surface), ("By season", by_season)):
        lines += ["", f"## {title} (log_loss: {best} vs elo_plain)", "", "| group | n | best | elo_plain |", "|---|---|---|---|"]
        for k, v in sorted(store.items()):
            lines.append(f"| {k} | {v['n']} | {v[best]['log_loss']:.4f} | {v['elo_plain']['log_loss']:.4f} |")
    open(os.path.join(a.out, f"RESULTS_{a.tour}.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
