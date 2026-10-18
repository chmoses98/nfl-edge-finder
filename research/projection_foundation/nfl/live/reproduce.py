#!/usr/bin/env python3
"""Reproducibility check for the frozen NFL evaluation (run in CI after a FRESH state build).

Rebuilds nothing by itself: it loads the state that `nfl.live.run` just built from the freshly downloaded nflverse data (the
full walk-forward, pf_core 1.2.0), re-scores the FROZEN winners on the 2024-25 holdout with the study's own `holdout` stage
and compares family by family with the committed results/summary.json. The holdout rows are in the past, so the numbers do
not depend on when the check runs. Differences larger than rounding fail the step.

    python -m nfl.live.reproduce [--state PATH] [--tol 5e-4] [--summary-out FILE]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PF_ROOT = os.path.dirname(os.path.dirname(HERE))
if PF_ROOT not in sys.path:
    sys.path.insert(0, PF_ROOT)

from nfl import diagnostics as DG  # noqa: E402
from nfl import run_walkforward as R  # noqa: E402
from nfl.live import state as ST  # noqa: E402


STACK_TOL = 1e-2     # relative tolerance for families whose mean includes the walk-forward LightGBM rung (see compare)


def compare(S: dict, tol: float) -> tuple[list[dict], bool]:
    """Two tiers. Families with no LightGBM rung (the formula models: passing_tds D_qb_starts_env) and the team stacks must
    reproduce the committed numbers to rounding (`tol`). Families whose frozen winner stacks the LightGBM rung E (F_*) are
    held to STACK_TOL: the committed run predates the pf_core 1.1.0 / earlier-only prior-fallback fixes (the 328 warm-up rows
    the study documents), which shift E's training features slightly. For those the check also requires the conclusion to
    be unchanged (the game-clustered 95% CI of the CRPS difference vs baseline A excludes 0 in the same direction)."""
    frozen = json.load(open(R.FROZEN))["families"]
    summ = json.load(open(os.path.join(PF_ROOT, "results", "summary.json")))
    corr = DG.corrections(S)
    hold = R.holdout(S, frozen, corr["preds"])
    rows, ok = [], True
    for f in summ["families"]:
        fam, ref = f["family"], f["holdout"]
        new = hold[fam]["holdout"]
        d = {k: (ref.get(k), new.get(k)) for k in ("n_obs", "mae", "crps", "bias", "cover_80")}
        diffs = {k: (None if a is None or b is None else abs(b - a)) for k, (a, b) in d.items()}
        stack = fam not in ("passing_tds",) and ("F" in str(ref.get("model", "")))
        t = STACK_TOL if stack and not fam.startswith("team_") else tol
        # bias is a small difference of large quantities: judge it on the scale of the MAE, not of itself
        scale = {"mae": max(1.0, abs(d["mae"][0] or 0)), "crps": max(1.0, abs(d["crps"][0] or 0)), "bias": max(1.0, abs(d["mae"][0] or 0))}
        rel = {k: (diffs[k] or 0) / scale[k] for k in ("mae", "crps", "bias")}
        ci_old, ci_new = ref["vs_baseline"].get("ci95"), new["vs_baseline"]["ci95"]
        sig = lambda ci: None if not ci else (ci[1] < 0) - (ci[0] > 0)       # noqa: E731  -1 better, 0 not significant, +1 worse
        same_conclusion = sig(ci_old) == sig(ci_new)
        good = (diffs["n_obs"] == 0 and all(v <= t for v in rel.values()) and (diffs["cover_80"] or 0) <= (0.01 if stack else 2e-3)
                and same_conclusion)
        ok &= good
        rows.append({"family": fam, "model": ref.get("model"), "n": d["n_obs"][1], "tier": "stack" if t == STACK_TOL else "exact",
                     "crps_committed": d["crps"][0], "crps_rebuilt": d["crps"][1], "max_rel_diff": max(rel.values()),
                     "same_conclusion_vs_baseline": bool(same_conclusion), "n_equal": diffs["n_obs"] == 0, "ok": bool(good)})
    return rows, bool(ok)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default=ST.STATE_FILE)
    ap.add_argument("--tol", type=float, default=5e-4, help="relative tolerance (committed summary.json is rounded to ~5 significant digits)")
    ap.add_argument("--summary-out", default=None)
    a = ap.parse_args(argv)
    S = ST.load_state(a.state)
    if S is None:
        print("no state to check")
        return 2
    rows, ok = compare(S, a.tol)
    md = ["### Reproducibility: frozen holdout re-scored from the freshly rebuilt walk-forward state", "",
          f"State built {S.get('built_utc')} ({round(S.get('seconds', 0))}s) with pf_core {__import__('pf_core').VERSION}.", "",
          "| family | model | n | tier | CRPS committed | CRPS rebuilt | max rel diff (MAE/CRPS/bias) | same conclusion vs A | ok |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['family']} | {r['model']} | {r['n']} | {r['tier']} | {r['crps_committed']:.6f} | {r['crps_rebuilt']:.6f} | "
                  f"{r['max_rel_diff']:.2e} | {'yes' if r['same_conclusion_vs_baseline'] else 'NO'} | {'yes' if r['ok'] else 'NO'} |")
    import lightgbm, numpy, pandas
    md += ["", f"lightgbm {lightgbm.__version__}, numpy {numpy.__version__}, pandas {pandas.__version__}; tolerance exact {a.tol}, stack {STACK_TOL}."]
    text = "\n".join(md)
    print(text)
    p = os.environ.get("GITHUB_STEP_SUMMARY")
    if p:
        open(p, "a").write(text + "\n")
    if a.summary_out:
        json.dump({"ok": ok, "rows": rows, "tol": a.tol, "built_utc": S.get("built_utc")}, open(a.summary_out, "w"), indent=1)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
