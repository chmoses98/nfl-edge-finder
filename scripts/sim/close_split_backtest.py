"""CLOSE-GAME SPLIT CALIBRATION (sim-script-1.1.0 ``by_close_result``). RESEARCH_ONLY; no authority.

``within6`` pooled every simulated game decided by six points or fewer, whichever team won. sim-script-1.1.0
attributes those rows to a winner. This walk-forward asks whether the attribution is calibrated on real games
before Sift shows it as two scripts.

The simulated final margin is the closing-line centre plus the incumbent's residual bank (``pricing/game_env``),
with regulation ties resolved by the bank's overtime model; ``nfl_edge.sim.simulate`` draws it the same way. So the
margin distribution of every past game is reproduced exactly here from the schedule alone: for season Y the bank is
built from REG games of 2016..Y-1 (``sim.inputs.historical_bank``), and each game of Y is simulated at its closing
spread and total. Nothing of season Y enters its own bank.

Six favourite-oriented classes, exhaustive and mutually exclusive over integer margins:
    FAV_14+  FAV_7-13  FAV_1-6  TIE  DOG_1-6  DOG_7+
(a pick'em closing line is oriented on the home team). The 1.0.0 scripts are FAV_14+, FAV_7-13, CLOSE (= FAV_1-6 +
TIE + DOG_1-6) and DOG_7+; the question is only how CLOSE splits.

Baseline B1 (as in ``script_backtest``): class frequencies within the game's absolute closing-spread bucket, from
training seasons only, Laplace +1. Inference is clustered at the game (one number per game; the bootstrap resamples
games).

    python scripts/sim/close_split_backtest.py [path/to/games.csv|games.parquet]

Writes research/game_script_v2/close_split_calibration.json and CLOSE_SPLIT_CALIBRATION.md.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from nfl_edge.pricing.game_env import ResidualBank, simulate_game  # noqa: E402

CLASSES = ("FAV_14+", "FAV_7-13", "FAV_1-6", "TIE", "DOG_1-6", "DOG_7+")
SEASONS = (2021, 2022, 2023, 2024, 2025)
SPREAD_BUCKETS = (0.0, 3.0, 7.0, 10.0, np.inf)
N_SIMS = 20000
B = 2000
SEED = 20261011
OUT_DIR = os.path.join(ROOT, "research", "game_script_v2")


def load_schedule(path: str | None) -> pd.DataFrame:
    path = path or os.path.join(ROOT, "data", "silver", "games.parquet")
    g = pd.read_parquet(path) if path.endswith(".parquet") else pd.read_csv(path)
    return g[g["result"].notna() & g["spread_line"].notna() & g["total_line"].notna()].copy()


def bank_for(g: pd.DataFrame, season: int, seed: int = 11) -> ResidualBank:
    """Identical to ``nfl_edge.sim.inputs.historical_bank`` (which reads the parquet schedule)."""
    h = g[(g["season"] < season) & (g["season"] >= 2016) & (g["game_type"] == "REG")].copy()
    h["mres"] = h["result"] - h["spread_line"]
    h["tres"] = h["total"] - h["total_line"]
    return ResidualBank(h["mres"], h["tres"], h["season"], ref_season=season, spread_lines=h["spread_line"],
                        total_lines=h["total_line"], overtime=h["overtime"].fillna(0).astype(int), results=h["result"],
                        halflife=3.0, rng=np.random.default_rng(seed))


def classify(fav_margin) -> np.ndarray:
    """Index into CLASSES of each favourite-oriented margin."""
    m = np.asarray(fav_margin, float)
    return np.select([m >= 14, m >= 7, m > 0, m == 0, m >= -6], [0, 1, 2, 3, 4], default=5).astype(np.int8)


def orient(spread_home: float) -> int:
    return -1 if spread_home < 0 else 1


def spread_bucket(spread) -> np.ndarray:
    return np.clip(np.searchsorted(np.asarray(SPREAD_BUCKETS), np.abs(np.asarray(spread, float)), side="right") - 1,
                   0, len(SPREAD_BUCKETS) - 2)


def season_rows(g: pd.DataFrame, season: int) -> list[dict]:
    bank = bank_for(g, season)
    rows = []
    for r in g[g["season"] == season].sort_values(["week", "game_id"]).itertuples():
        sim = simulate_game(float(r.spread_line), float(r.total_line), bank, n=N_SIMS)
        s = orient(float(r.spread_line))
        p = np.bincount(classify(s * sim["margin"]), minlength=len(CLASSES)) / N_SIMS
        rows.append({"game_id": r.game_id, "season": int(r.season), "week": int(r.week), "game_type": r.game_type,
                     "spread_line": float(r.spread_line), "pickem": float(r.spread_line) == 0.0,
                     "realized": int(classify([s * float(r.result)])[0]), "p": p.round(5).tolist()})
    return rows


def b1(g: pd.DataFrame, season: int) -> np.ndarray:
    """(n_buckets, n_classes) training frequencies within the absolute closing-spread bucket, Laplace +1."""
    t = g[(g["season"] < season) & (g["season"] >= 2016)]
    k = classify(np.where(t["spread_line"] < 0, -1, 1) * t["result"].to_numpy(float))
    b = spread_bucket(t["spread_line"])
    out = np.ones((len(SPREAD_BUCKETS) - 1, len(CLASSES)))
    np.add.at(out, (b, k), 1)
    return out / out.sum(1, keepdims=True)


def boot_ci(x: np.ndarray, rng) -> list[float]:
    idx = rng.integers(0, len(x), size=(B, len(x)))
    m = x[idx].mean(1)
    return [round(float(np.quantile(m, 0.025)), 5), round(float(np.quantile(m, 0.975)), 5)]


def evaluate(rows: list[dict], base: dict[int, np.ndarray]) -> dict:
    rng = np.random.default_rng(SEED)
    P = np.array([r["p"] for r in rows])
    y = np.zeros_like(P)
    y[np.arange(len(rows)), [r["realized"] for r in rows]] = 1
    Q = np.array([base[r["season"]][spread_bucket([r["spread_line"]])[0]] for r in rows])
    out = {"games": len(rows), "classes": {}}
    for j, c in enumerate(CLASSES):
        bm, bb = (P[:, j] - y[:, j]) ** 2, (Q[:, j] - y[:, j]) ** 2
        rate = float(y[:, j].mean())
        se = np.sqrt(max(rate * (1 - rate), 1e-12) / len(rows))
        out["classes"][c] = {"mean_p": round(float(P[:, j].mean()), 4), "realized": round(rate, 4),
                             "b1_mean_p": round(float(Q[:, j].mean()), 4),
                             "calibration_in_large": round(float(P[:, j].mean() - rate), 4),
                             "z": round(float((P[:, j].mean() - rate) / se), 2),
                             "brier_model": round(float(bm.mean()), 5), "brier_b1": round(float(bb.mean()), 5),
                             "model_minus_b1": round(float((bm - bb).mean()), 5), "ci95": boot_ci(bm - bb, rng)}
    # the 1.0.0 scripts vs the 1.1.0 scripts, scored as multiclass Brier on the same games
    merge = [[0], [1], [2, 3, 4], [5]]
    P4 = np.stack([P[:, k].sum(1) for k in merge], 1)
    y4 = np.stack([y[:, k].sum(1) for k in merge], 1)
    out["multiclass_brier"] = {"scripts_1_0_0_four": round(float(((P4 - y4) ** 2).sum(1).mean()), 5),
                               "scripts_1_1_0_six": round(float(((P - y) ** 2).sum(1).mean()), 5),
                               "b1_six": round(float(((Q - y) ** 2).sum(1).mean()), 5)}
    # THE QUESTION: given the game ended within one score with a winner, who won it?
    close = (y[:, 2] + y[:, 4]) > 0
    pc = P[:, 2] / np.maximum(P[:, 2] + P[:, 4], 1e-12)
    qc = Q[:, 2] / np.maximum(Q[:, 2] + Q[:, 4], 1e-12)
    yc = y[:, 2]
    bins = np.clip((pc[close] * 10).astype(int), 0, 9)
    rel = []
    for b in range(10):
        k = bins == b
        if k.sum():
            rel.append({"bin": f"{b / 10:.1f}-{(b + 1) / 10:.1f}", "n": int(k.sum()), "mean_p": round(float(pc[close][k].mean()), 3),
                        "realized": round(float(yc[close][k].mean()), 3)})
    dm = (pc[close] - yc[close]) ** 2 - (qc[close] - yc[close]) ** 2
    rate = float(yc[close].mean())
    out["favorite_wins_given_close"] = {
        "n_close_games_with_winner": int(close.sum()), "mean_p": round(float(pc[close].mean()), 4), "realized": round(rate, 4),
        "b1_mean_p": round(float(qc[close].mean()), 4),
        "z": round(float((pc[close].mean() - rate) / np.sqrt(rate * (1 - rate) / close.sum())), 2),
        "brier_model": round(float(((pc[close] - yc[close]) ** 2).mean()), 5),
        "brier_b1": round(float(((qc[close] - yc[close]) ** 2).mean()), 5),
        "model_minus_b1": round(float(dm.mean()), 5), "ci95": boot_ci(dm, rng), "reliability": rel}
    return out


def verdict(pooled: dict) -> dict:
    """Preregistered in the module docstring of this file before the first run:
    SHOW_SPLIT        the split is no worse than B1 for who wins a close game (model − B1 Brier CI upper bound <= 0.002)
                      and FAV_1-6 / DOG_1-6 are each no worse than B1 (CI upper bound <= 0.002);
    SHARE_IS_BIASED   reported, not gating: |z| >= 3 calibration-in-the-large for either close class (the bank's known
                      one-score under-forecast, SCRIPT_CALIBRATION_5Y.md)."""
    fw = pooled["favorite_wins_given_close"]
    ok_split = fw["ci95"][1] <= 0.002
    ok_cls = all(pooled["classes"][c]["ci95"][1] <= 0.002 for c in ("FAV_1-6", "DOG_1-6"))
    biased = [c for c in ("FAV_1-6", "TIE", "DOG_1-6") if abs(pooled["classes"][c]["z"]) >= 3]
    return {"show_split": bool(ok_split and ok_cls), "split_no_worse_than_b1": bool(ok_split),
            "close_classes_no_worse_than_b1": bool(ok_cls), "share_biased_classes": biased}


def markdown(res: dict) -> str:
    p = res["pooled"]
    L = ["# Close-game split calibration (sim-script-1.1.0 `by_close_result`), 2021-2025", "",
         "Generated by `scripts/sim/close_split_backtest.py` -- do not edit by hand. **RESEARCH_ONLY: no betting authority.**", "",
         "The simulated final margin is the closing-line centre plus the incumbent's residual bank with its overtime model, "
         "reproduced exactly per game (bank from 2016..Y-1 REG games; 20,000 rows per game). B1 = training-season class "
         "frequencies within the absolute closing-spread bucket. 95% CIs are game-clustered bootstraps.", "",
         f"## Verdict: **{'SHOW SPLIT' if res['verdict']['show_split'] else 'DO NOT SHOW SPLIT'}**", ""]
    for k, v in res["verdict"].items():
        L.append(f"- {k}: **{v}**")
    fw = p["favorite_wins_given_close"]
    L += ["", "## Who wins a close game (games decided by 1-6 points)", "",
          "| games | favourite wins: model mean p | B1 mean p | realized | z | Brier model / B1 | model − B1 [95% CI] |", "|---|---|---|---|---|---|---|",
          f"| {fw['n_close_games_with_winner']} | {fw['mean_p']:.3f} | {fw['b1_mean_p']:.3f} | {fw['realized']:.3f} | {fw['z']:+.1f} | "
          f"{fw['brier_model']:.4f} / {fw['brier_b1']:.4f} | {fw['model_minus_b1']:+.4f} [{fw['ci95'][0]:+.4f}, {fw['ci95'][1]:+.4f}] |", "",
          "| P(favourite wins \\| close) bin | n | mean p | realized |", "|---|---|---|---|"]
    L += [f"| {r['bin']} | {r['n']} | {r['mean_p']:.3f} | {r['realized']:.3f} |" for r in fw["reliability"]]
    L += ["", "## Six classes (pooled)", "",
          "| class | model mean p | B1 mean p | realized | mean p − rate | z | Brier model / B1 | model − B1 [95% CI] |", "|---|---|---|---|---|---|---|---|"]
    for c in CLASSES:
        x = p["classes"][c]
        L.append(f"| {c} | {x['mean_p']:.3f} | {x['b1_mean_p']:.3f} | {x['realized']:.3f} | {x['calibration_in_large']:+.3f} | {x['z']:+.1f} | "
                 f"{x['brier_model']:.4f} / {x['brier_b1']:.4f} | {x['model_minus_b1']:+.4f} [{x['ci95'][0]:+.4f}, {x['ci95'][1]:+.4f}] |")
    mb = p["multiclass_brier"]
    L += ["", f"Multiclass Brier on the same games: 1.0.0 four scripts {mb['scripts_1_0_0_four']:.4f}; 1.1.0 six classes "
          f"{mb['scripts_1_1_0_six']:.4f} (B1 six classes {mb['b1_six']:.4f}). The two are not comparable as a score (more classes); "
          "the split is judged by the conditional table above.", "", "## By season", "",
          "| season | games | close games | fav wins \\| close: model / realized | model − B1 | FAV_1-6 model / realized | DOG_1-6 model / realized |",
          "|---|---|---|---|---|---|---|"]
    for s, x in res["by_season"].items():
        f = x["favorite_wins_given_close"]
        L.append(f"| {s} | {x['games']} | {f['n_close_games_with_winner']} | {f['mean_p']:.3f} / {f['realized']:.3f} | {f['model_minus_b1']:+.4f} | "
                 f"{x['classes']['FAV_1-6']['mean_p']:.3f} / {x['classes']['FAV_1-6']['realized']:.3f} | "
                 f"{x['classes']['DOG_1-6']['mean_p']:.3f} / {x['classes']['DOG_1-6']['realized']:.3f} |")
    L += ["", "## What this does and does not change", "",
          "- No probability moves. `by_final_margin` (five states) is unchanged; `by_close_result` re-attributes the `within6` rows to a winner, and its shares sum to `within6`.",
          "- The close-game shares inherit the bank's known one-score under-forecast (`SCRIPT_CALIBRATION_5Y.md`, post-hoc margin shape). Consumers label them simulation shares, not calibrated probabilities.",
          "- Ties are the overtime model's tie share; they are reported, not folded into either winner."]
    return "\n".join(L) + "\n"


def main(path: str | None = None) -> dict:
    g = load_schedule(path)
    rows, base = [], {}
    for s in SEASONS:
        base[s] = b1(g, s)
        rows += season_rows(g, s)
        print(f"season {s}: {sum(r['season'] == s for r in rows)} games", flush=True)
    pooled = evaluate(rows, base)
    res = {"meta": {"script_version": "sim-script-1.1.0", "n_sims": N_SIMS, "seasons": list(SEASONS), "classes": list(CLASSES),
                    "provenance": "MARKET_CENTRED_GAME", "authority": "RESEARCH_ONLY"},
           "pooled": pooled, "by_season": {s: evaluate([r for r in rows if r["season"] == s], base) for s in SEASONS}}
    res["verdict"] = verdict(pooled)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "close_split_calibration.json"), "w") as f:
        json.dump(res, f, indent=1, sort_keys=True)
    with open(os.path.join(OUT_DIR, "CLOSE_SPLIT_CALIBRATION.md"), "w") as f:
        f.write(markdown(res))
    return res


if __name__ == "__main__":
    r = main(sys.argv[1] if len(sys.argv) > 1 else None)
    print(json.dumps({"verdict": r["verdict"], "favorite_wins_given_close": {k: v for k, v in r["pooled"]["favorite_wins_given_close"].items() if k != "reliability"}}, indent=1))
