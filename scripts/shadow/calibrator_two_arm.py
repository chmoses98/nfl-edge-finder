#!/usr/bin/env python3
"""The LadderCalibrator two-arm experiment (H-20260904-015), scored on IDENTICAL populations.

ARM A  the frozen Week-1 model, raw
ARM B  the same model with the pre-existing LadderCalibrator applied

The calibrator is NOT deployed and this script does not deploy it. It scores both arms so the prospective
comparison can be read when 2026 outcomes exist.

**The population rule is the point.** In session 2 a study filtered "live rungs" by each arm's own predicted
probability, so the two arms were scored on different contract sets -- mean predicted 0.257 against 0.291 on
base rates 0.235 against 0.272 -- and the comparison measured the change of subset rather than the change of
skill. It reported the opposite of the truth. Here the scored population is fixed ONCE, from arm-independent
facts (support state, quote presence, book width), and both arms are scored on exactly that set. The script
asserts the two arms have identical n and identical contract ids before reporting anything.
"""
import argparse, glob, gzip, json, math, os, sys
from collections import defaultdict

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.pricing.calibration import LadderCalibrator  # noqa: E402
from nfl_edge.research.clv import clustered_se  # noqa: E402

OUT = os.path.join(ROOT, "research", "tail_calibration")
MAX_WIDTH = 0.10


def fee(p):
    return math.ceil(0.07 * p * (1 - p) * 100) / 100.0 if 0 < p < 1 else 0.0


def load_calibrator():
    """Fit the calibrator on the most recent completed season the frozen model did not train on."""
    import polars as pl
    p = os.path.join(ROOT, "research/model_vs_market/prop_probs_2025_both_arms.parquet")
    if not os.path.exists(p):
        return None
    d = pl.read_parquet(p)
    return LadderCalibrator().fit(d["p_base"].to_numpy(), d["y"].to_numpy())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default=os.path.join(ROOT, "data/shadow/ledger"))
    ap.add_argument("--model-version", default="shadow-0.3.0")
    a = ap.parse_args()

    cal = load_calibrator()
    if cal is None or cal.knots_ is None:
        print("no calibrator could be fitted"); return 1
    print(f"calibrator fitted on {cal.n_fit_} settled 2025 rungs, {len(cal.knots_)} knots")

    files = sorted(glob.glob(os.path.join(a.ledger, "*", f"*{a.model_version}*.observations.jsonl.gz")))
    if not files:
        print(f"no ledger snapshot for {a.model_version}"); return 1
    rows = [json.loads(l) for l in gzip.open(files[-1], "rt")]
    print(f"snapshot {os.path.basename(files[-1])}: {len(rows)} observations")

    # POPULATION FIXED ONCE, from arm-independent facts only
    pop = [r for r in rows
           if r.get("support_state") == "SUPPORTED"
           and r.get("family") == "PLAYER_STAT"
           and r.get("model_event_probability") is not None
           and r.get("yes_bid") is not None and r.get("yes_ask") is not None
           and (r["yes_ask"] - r["yes_bid"]) <= MAX_WIDTH]
    ids = [r["prediction_id"] for r in pop]
    print(f"scored population (fixed once, arm-independent): {len(pop)} contracts")

    raw = np.array([r["model_event_probability"] for r in pop])
    calibrated = cal.transform(raw)
    # the invariant that session 2 broke
    assert len(raw) == len(calibrated) == len(ids), "arms differ in size"
    assert len(set(ids)) == len(ids), "duplicate contracts in the scored population"
    print("IDENTICAL-POPULATION CHECK: both arms scored on the same "
          f"{len(ids)} contract ids -- OK")

    mid = np.array([(r["yes_bid"] + r["yes_ask"]) / 2.0 for r in pop])
    cl = [r.get("game_id") or r["ticker"] for r in pop]
    print(f"\n{'arm':10s} {'n':>6s} {'mean p':>8s} {'vs mid':>9s} {'se':>8s} "
          f"{'p<0.20 n':>9s} {'mean p<0.20':>12s}")
    res = {"snapshot": os.path.basename(files[-1]), "n": len(pop), "arms": {}}
    for name, p in (("A raw", raw), ("B calibrated", calibrated)):
        d = p - mid
        se = clustered_se(d, cl)
        lo = p < 0.20
        res["arms"][name] = {"n": int(len(p)), "mean_p": float(p.mean()),
                             "mean_vs_mid": float(d.mean()), "se": se,
                             "n_low": int(lo.sum()), "mean_p_low": float(p[lo].mean()) if lo.any() else None}
        print(f"{name:10s} {len(p):6d} {p.mean():8.4f} {d.mean():+9.4f} {se:8.4f} "
              f"{int(lo.sum()):9d} {(p[lo].mean() if lo.any() else float('nan')):12.4f}")

    # how many disagreements each arm would generate, on the same contracts
    print(f"\n{'arm':10s} {'clears ask':>11s} {'clears bid':>11s} {'inside spread':>14s}")
    for name, p in (("A raw", raw), ("B calibrated", calibrated)):
        ask = np.array([r["yes_ask"] for r in pop]); bid = np.array([r["yes_bid"] for r in pop])
        f_ask = np.array([fee(x) for x in ask]); f_bid = np.array([fee(1 - x) for x in bid])
        yes = int(((p > ask + f_ask)).sum()); no = int((((1 - p) > (1 - bid) + f_bid)).sum())
        inside = int(((p >= bid) & (p <= ask)).sum())
        res["arms"][name].update({"clears_ask": yes, "clears_bid": no, "inside_spread": inside})
        print(f"{name:10s} {yes:11d} {no:11d} {inside:14d}")

    print("\nNo outcomes exist yet (first 2026 kickoff 2026-09-09). Scoring on Brier, log loss, calibration")
    print("bins, market-relative score and CLV runs once contracts settle. Deployment remains PROHIBITED;")
    print("the frozen Week-1 arm is untouched and H-20260904-015 stands as registered.")
    json.dump(res, open(os.path.join(OUT, "two_arm_status.json"), "w"), indent=1, default=float)
    return 0


if __name__ == "__main__":
    sys.exit(main())
