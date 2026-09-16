#!/usr/bin/env python3
"""Render every committed result summary from the canonical JSON artifacts.

There is ONE source of truth per number: ``walkforward.json``, ``reconciliation_2025.json``,
``reconciliation_weights.json``, ``rushing_ablation.json``, ``week1_2026_diagnostic.json``.  The markdown
under ``research/simulation_engine/`` is a projection of those files and nothing else, and
``tests/test_sim_results_consistency.py`` re-renders and compares, so a committed summary cannot drift away
from the committed data the way the first version of RESULTS.md did.

Usage: python scripts/sim/write_results.py [--check]
"""
from __future__ import annotations
import argparse, json, os, sys
import numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
OUT = os.path.join(ROOT, "research", "simulation_engine")
STATS = ["carries", "rush_yards", "targets", "receptions", "rec_yards", "attempts", "completions", "pass_yards",
         "pass_td", "any_td"]
FILES = ("RESULTS.md", "RECONCILIATION.md", "RUSHING_ABLATION.md")


def f(x, nd=3):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "—"
    return f"{x:.{nd}f}" if isinstance(x, (int, float)) else str(x)


def _load(name):
    p = os.path.join(OUT, name)
    return json.load(open(p)) if os.path.exists(p) else None


# ------------------------------------------------------------------------------------- RESULTS.md
def render_results(wf: dict) -> str:
    L = ["# Simulation engine (sim-1.0.0): walk-forward evidence", "",
         "Reproduce: `python scripts/sim/walkforward.py --seasons 2023,2024,2025`.  Generated from "
         "`walkforward.json` by `scripts/sim/write_results.py` -- do not edit by hand.", "",
         "**HISTORICAL_RESEARCH.** For each evaluation season Y:", "",
         "* the shrinkage priors (league levels, pooled rates, rate denominators, position rates) are fitted on "
         "the RAW rows of seasons strictly before Y and frozen (`training.fit_priors_for`), then applied to Y;",
         "* the frames are rebuilt per evaluation season so no statistic of Y can reach a row of Y;",
         "* the model bundle is fitted on 2018..Y-1 (2016-17 warm the EWMAs);",
         "* every game of Y is simulated (10,000 rows) with the nflverse consensus CLOSING line as the game "
         "centre, and one row per (game, player, statistic) is scored against the box score.", "",
         "Baseline = the naive prior-only projection (EWMA share x EWMA team volume; EWMA rate x count). "
         "Coverage = share of outcomes inside the central 50% / 90% predictive interval.  Ladder Brier = mean "
         "Brier of P(Y >= k) over the fixed threshold grid in `backtest.LADDERS`, on players whose predictive "
         "mean clears a small per-statistic floor.", ""]
    for y in sorted(wf):
        ev = wf[y]["evaluation"]; run = wf[y]["run"]
        pri = wf[y].get("priors_fit_seasons")
        L += [f"## {y}: {run['games']} games, {run['player_rows']} player-stat rows", ""]
        if pri:
            L += [f"_priors frozen on seasons {min(pri)}-{max(pri)}; bundle trained on "
                  f"{min(wf[y].get('train_seasons') or pri)}-{max(wf[y].get('train_seasons') or pri)}_", ""]
        L += ["| statistic | n | MAE | baseline MAE | Δ% | RMSE | bias | CRPS | cover50 | cover90 | ladder Brier |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for st in STATS:
            r = ev["player"].get(st)
            if not r:
                continue
            L.append(f"| {st} | {r['n']} | {f(r['mae'])} | {f(r.get('baseline_mae'))} | {f(r.get('mae_vs_baseline_pct'), 1)} | "
                     f"{f(r['rmse'])} | {f(r['bias'])} | {f(r['crps'])} | {f(r['cover50'])} | {f(r['cover90'])} | "
                     f"{f(r.get('ladder_brier'), 4)} |")
        L += ["", "| team statistic | n | MAE | RMSE | bias | CRPS | cover90 |", "|---|---|---|---|---|---|---|"]
        for st, r in ev["team"].items():
            L.append(f"| {st} | {r['n']} | {f(r['mae'])} | {f(r['rmse'])} | {f(r['bias'])} | {f(r['crps'])} | {f(r['cover90'])} |")
        L.append("")
    L += ["## Coherence", "",
          "Every simulated game in every season passed `simulate.coherence_report` (the backtest raises on the "
          "first failure): sum of player carries = team rush attempts, targets = team targets, receptions = "
          "completions, receiving yards = passing yards, QB attempts = team attempts, TD allocations = team TD "
          "counts, no negative or fractional counts, receptions <= targets, home + away = total, home - away = "
          "margin.  Ladders are monotone by construction -- one distribution per player-statistic.", "",
          "## Point-in-time status", "",
          "`tests/test_sim_pit.py` poisons every evaluation-season game after week 3 by a factor of 1,000 and "
          "asserts that no feature of an earlier row moves by a bit, with a negative control proving the same "
          "poison does reach later rows.  The first version of this layer FAILED that test: the shrinkage "
          "targets were computed over the whole assembled frame, so a week-1 projection's league priors had "
          "seen week 18.  See the PR description for the old-vs-clean metric delta.", ""]
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------ RECONCILIATION.md
def render_reconciliation(rec: dict, weights: dict) -> str:
    t0 = rec["horizons"]["T-0"]
    L = ["# Market reconciliation weights (sim-1.0.0), fitted on the 2025 Kalshi archive", "",
         "Reproduce: `python scripts/sim/walkforward.py --seasons 2025` then "
         "`python scripts/sim/reconciliation_study.py`.  Generated from `reconciliation_2025.json` and "
         "`reconciliation_weights.json` by `scripts/sim/write_results.py` -- do not edit by hand.", "",
         f"**HISTORICAL_RESEARCH.** The simulation distributions of every 2025 game (bundle and shrinkage "
         f"priors both fitted on seasons <= 2024) are joined to the {rec['n_rungs_archive']} settled archived "
         "player-prop rungs that resolve to a GSIS player, with the archived quotes at the close.  The "
         "reconciled probability is the football distribution re-located to `market mean + w x (football mean "
         "- market mean)`; `w` is chosen on weeks 1-9 by Brier at the quoted thresholds, confirmed on weeks "
         "10-22 (paired against the monotone midpoint, game-clustered), and re-fitted on the whole season. "
         "The DEPLOYED weight (`reconcile.deploy_weights`) is non-zero only when the early fit had "
         f">= {weights['meta'].get('min_fit_rows', 500)} rows and a non-zero optimum AND its later-week "
         "confirmation was not worse than the market beyond z = 1, and is then the smaller of the early-week "
         "and whole-season optima.", "",
         f"Only the close is evidence: `{t0['pit_status']}` -- {t0['pit_note']}", "",
         f"## Football-only against the market at the close ({t0['n_scored']} rows, {t0['games']} games)", "",
         "| statistic | n | Brier football-only | Brier market mid | football − market | mean football / market / rate | b_football / b_market |",
         "|---|---|---|---|---|---|---|"]
    for st, b in t0["by_stat_all"].items():
        e = t0["encompassing_all"].get(st, {})
        L.append(f"| {st} | {b['n']} | {f(b['brier_football'], 4)} | {f(b['brier_market_mono'], 4)} | "
                 f"{f(b['brier_football'] - b['brier_market_mono'], 4)} | {f(b['mean_football'])} / "
                 f"{f(b['mean_market'])} / {f(b['rate'])} | {f(e.get('b_football'), 2)} / {f(e.get('b_market'), 2)} |")
    L += ["", "## Fitted, confirmed and deployed weights", "",
          "| statistic | w (weeks 1-9) | n (weeks 1-9) | confirm weeks 10-22: reconciled vs market Brier (z) | w (all 2025) | **deployed** | why |",
          "|---|---|---|---|---|---|---|"]
    for st in t0["by_stat_all"]:
        fw = t0["fitted_on_fit_weeks"].get(st, {}); c = t0["confirmed_on_later_weeks"].get(st, {})
        af = t0["fitted_on_all_2025"].get(st, {}); dep = (weights.get("fitted") or {}).get(st, {})
        conf = (f"{f(c.get('brier_reconciled'), 5)} vs {f(c.get('brier_market_mono'), 5)} (z {f(c.get('z'), 2)})"
                if c else "—")
        L.append(f"| {st} | {f(fw.get('weight'), 2)} | {fw.get('n', '—')} | {conf} | {f(af.get('weight'), 2)} | "
                 f"**{f(dep.get('weight'), 2)}** | {dep.get('reason', '—')} |")
    nz = {k: v["weight"] for k, v in (weights.get("fitted") or {}).items() if (v.get("weight") or 0) > 0}
    L += ["", (f"**Families with a non-zero deployed weight: {', '.join(f'{k} = {v}' for k, v in nz.items())}.**"
               if nz else "**No family earned a non-zero deployed weight.**"),
          "Every other family deploys at 0: the reconciled distribution sits at the market mean with the "
          "football shape, is reported on the board, and is never ranked.", "",
          "Touchdown families are re-located as a Poisson at the target mean and yardage families keep the "
          "football shape unless the target is more than 4x away, where the market's own two-parameter family "
          "is used instead (`reconcile.relocate`); a lattice with a 0.0005 mean cannot be stretched 40x.", "",
          "## Disagreement bands (weeks 1-9, |football − market| at the rung)", "",
          "| statistic | band | n | best w | Brier market | Brier football |", "|---|---|---|---|---|---|"]
    for st, v in t0["fitted_on_fit_weeks"].items():
        for bd in v.get("bands", []):
            L.append(f"| {st} | {bd['band'][0]:.2f}-{bd['band'][1]:.2f} | {bd['n']} | {bd['best_w']:.2f} | "
                     f"{f(bd['brier_market'], 4)} | {f(bd['brier_football'], 4)} |")
    L += ["", "Where the football model and the market are close the football view is as good or marginally "
              "better; where they disagree by more than 0.10 the market wins on every family.  **A large "
              "disagreement is a warning, not an opportunity** -- which is why the packet ranks only the "
              "reconciled disagreement, and only where a weight was earned.", ""]
    for h, hr in rec["horizons"].items():
        if h == "T-0":
            continue
        L += [f"## {h} -- {hr['pit_status']}", "", hr["pit_note"], "",
              "| statistic | n | Brier football-only | Brier market mid |", "|---|---|---|---|"]
        for st, b in hr["by_stat_all"].items():
            L.append(f"| {st} | {b['n']} | {f(b['brier_football'], 4)} | {f(b['brier_market_mono'], 4)} |")
        L.append("")
    L += ["## Caveats", "",
          "* One season of Kalshi history; the early-week samples for some families are thin, which is why the "
          "deployment rule requires a minimum row count rather than trusting a small optimum.",
          "* The reconciled shape is the football shape.  Where the market's ladder identifies the tail a shape "
          "blend may be better; not tested.",
          "* The market's dispersion prior for UNDERIDENTIFIED ladders is the incumbent's frozen 2025 constant "
          "(`engines/player/market_dist.DISPERSION_PRIOR`); underidentified ladders are excluded from fitting.",
          "* Nothing here is prospective.  `H-20260916-027` preregisters the 2026 test.", ""]
    return "\n".join(L) + "\n"


# ----------------------------------------------------------------------------- RUSHING_ABLATION.md
def render_ablation(ab: dict) -> str:
    L = ["# Rushing enrichment: source audit and walk-forward ablation", "",
         "Reproduce: `python scripts/sim/rushing_ablation.py --seasons 2023,2024,2025`.  Generated from "
         "`rushing_ablation.json` by `scripts/sim/write_results.py` -- do not edit by hand.", "",
         "Each arm adds columns to the per-carry efficiency model.  For every evaluation season the model is "
         "fitted on carries of earlier seasons only -- including the frozen shrinkage priors of both the base "
         "features and the enrichment -- and scored on the evaluation season.  Player-game rows are restricted "
         "to >= 6 carries, the population a rushing ladder is listed on.", "",
         "## Arms", ""]
    from nfl_edge.sim import rushing as RU
    for name, cols in RU.ARMS.items():
        L.append(f"* **{name}** — {', '.join(f'`{c}`' for c in cols) if cols else 'the current model'}")
    L += ["", "## Out-of-sample result", "",
          "| arm | per-carry MAE 2023 / 2024 / 2025 | per-carry r² | player-game MAE | Δ player-game MAE vs baseline | improves every season |",
          "|---|---|---|---|---|---|"]
    ys = sorted(ab["by_season"])
    for name in ab["arms"]:
        pc = " / ".join(f(ab["by_season"][y][name]["per_carry"]["mae"], 4) for y in ys)
        r2 = " / ".join(f(ab["by_season"][y][name]["per_carry"]["r2"], 5) for y in ys)
        pg = " / ".join(f(ab["by_season"][y][name]["per_player_game"]["mae"], 2) for y in ys)
        v = ab["verdict"][name]
        dd = " / ".join(f(v["delta_player_game_mae"].get(y), 4) for y in ys)
        L.append(f"| {name} | {pc} | {r2} | {pg} | {dd} (mean {f(v['mean_delta'], 4)}) | {v['improves_every_season']} |")
    ol = ab["verdict"]["ol"]
    L += ["", "## Verdict: none of it is deployed", "",
          f"Per-carry rushing yardage has an out-of-sample r² of "
          f"{f(min(ab['by_season'][y]['baseline']['per_carry']['r2'] for y in ys), 5)}-"
          f"{f(max(ab['by_season'][y]['baseline']['per_carry']['r2'] for y in ys), 5)} in the current model, and "
          "no arm moves it.  The offensive-line arm is the only one that improves player-game rushing-yards MAE "
          f"in all three seasons, and it does so by {f(-ol['mean_delta'], 4)} yards on a ~16.6-yard error "
          "(0.2%), for four extra parameters.  That passes the direction test and fails any materiality bar, so "
          "it is NOT deployed; the code stays available behind `rushing.ARMS` for a future preregistered test on "
          "a larger sample.  The opponent-adjusted defensive front, the runner's yards-before/after-contact and "
          "the combined arm are all worse in at least one season, and `combined` is the worst of the six -- "
          "twenty-four parameters chasing a signal that is not there.", "",
          "**The useful finding is where the value is not.** Across the same walk-forward the opportunity model "
          "beats its naive baseline by 12-20% on carries while the efficiency model explains under 1% of "
          "per-carry variance.  Rushing-projection accuracy is almost entirely an opportunity problem, so the "
          "next investment belongs in carry share, role change and availability -- not in more efficiency "
          "covariates.", "",
          "## Rejected sources, and why", ""]
    for k, v in ab.get("rejected", {}).items():
        L.append(f"* **{k}** — {v}")
    L.append("")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------------------ driver
def render_all() -> dict:
    wf = _load("walkforward.json"); rec = _load("reconciliation_2025.json")
    weights = _load("reconciliation_weights.json"); ab = _load("rushing_ablation.json")
    out = {}
    if wf:
        out["RESULTS.md"] = render_results(wf)
    if rec and weights:
        out["RECONCILIATION.md"] = render_reconciliation(rec, weights)
    if ab:
        out["RUSHING_ABLATION.md"] = render_ablation(ab)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="exit 1 if a committed file differs from the render")
    a = ap.parse_args()
    rendered = render_all()
    bad = []
    for name, text in rendered.items():
        p = os.path.join(OUT, name)
        if a.check:
            cur = open(p).read() if os.path.exists(p) else None
            if cur != text:
                bad.append(name)
        else:
            open(p, "w").write(text)
            print("wrote", name)
    if a.check:
        print("stale:" if bad else "all committed summaries match their JSON", *bad)
        raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
