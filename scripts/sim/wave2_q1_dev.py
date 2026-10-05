#!/usr/bin/env python3
"""Wave 2 / Q1 development selection on seasons <= 2020 ONLY (preregistration section 3).

Fit the regime model on 2018-2019 simulated-QB1 rows, score multiclass log loss on 2020 against the unconditional
regime frequencies (and, descriptively, against the regime frequencies implied by the incumbent's share quantiles).
Output: data/cache/game_script_v2/wave2/q1_dev.json.
"""
from __future__ import annotations
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
import numpy as np
import pandas as pd
from nfl_edge.sim import models as M, qb_regimes as QR, training as T

OUT = os.path.join(ROOT, "data", "cache", "game_script_v2", "wave2", "q1_dev.json")
B, SEED = 2000, 20261005


def boot(x):
    x = np.asarray(x, float); i = np.random.default_rng(SEED).integers(0, len(x), (B, len(x))); b = x[i].mean(1)
    return {"mean": float(x.mean()), "lo": float(np.quantile(b, .025)), "hi": float(np.quantile(b, .975)), "n": int(len(x))}


def main():
    frames = QR.attach_features(T.assemble(range(2016, 2021), verbose=lambda *x: None, priors=T.fit_priors_for(2020)))
    e = frames["eligible"]
    q = QR.label_errors(QR.qb1_rows(e[e["season"] >= 2018]))
    tr, te = q[q["season"].isin([2018, 2019])], q[q["season"] == 2020]
    cond, unc = QR.fit(tr, True), QR.fit(tr, False)
    y = te["regime"].to_numpy(int)
    Pc = QR.probabilities(cond, te[list(QR.FEATURES)].to_numpy(float)); Pu = QR.probabilities(unc, np.zeros((len(te), 0)))
    inc_q = np.asarray(M.fit_qb_share(e[e["season"].isin([2018, 2019])])["quantiles"])
    inc_freq = np.array([np.mean(inc_q >= QR.FULL_MIN), np.mean((inc_q >= QR.LOW_MAX) & (inc_q < QR.FULL_MIN)), np.mean(inc_q < QR.LOW_MAX)])
    inc_freq = np.clip(inc_freq, 1e-4, 1); inc_freq /= inc_freq.sum()
    ll = lambda P: -np.log(np.clip(P[np.arange(len(y)), y], 1e-6, 1))
    lc, lu, li = ll(Pc), ll(Pu), ll(np.tile(inc_freq, (len(y), 1)))
    d = boot(lc - lu)
    res = {"evidence": "DEVELOPMENT (<= 2020 only)", "fit_seasons": [2018, 2019], "score_season": 2020,
           "n_train": int(len(tr)), "n_score": int(len(te)),
           "regime_frequency": {"train": np.bincount(tr["regime"], minlength=3).tolist(), "2020": np.bincount(y, minlength=3).tolist()},
           "identification_error_rate": {"train": float(tr["identification_error"].mean()), "2020": float(te["identification_error"].mean())},
           "exit_partial_rate": {"train": float(tr["exit_partial"].mean()), "2020": float(te["exit_partial"].mean())},
           "incumbent_implied_regime_frequency": inc_freq.tolist(),
           "log_loss_2020": {"conditional": float(lc.mean()), "unconditional": float(lu.mean()), "incumbent_implied": float(li.mean())},
           "conditional_minus_unconditional": d, "unconditional_minus_incumbent_implied": boot(lu - li),
           "model_conditional": cond, "model_unconditional": unc}
    res["selected"] = "Q1" if d["hi"] < 0 else "Q1-0"
    json.dump(res, open(OUT, "w"), indent=1, default=float)
    print(json.dumps({k: res[k] for k in ("regime_frequency", "identification_error_rate", "exit_partial_rate", "incumbent_implied_regime_frequency",
                                          "log_loss_2020", "conditional_minus_unconditional", "selected")}, indent=0, default=float))


if __name__ == "__main__":
    main()
