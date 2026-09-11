import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from tennis_edge.eval.metrics import brier, log_loss, calibration_slope_intercept, ece, bootstrap_diff, summary


def test_scores_basic():
    y = np.array([1, 0, 1, 0]); p = np.array([0.9, 0.1, 0.6, 0.4])
    assert abs(brier(y, p) - np.mean([0.01, 0.01, 0.16, 0.16])) < 1e-12
    assert log_loss(y, np.full(4, 0.5)) > log_loss(y, p)


def test_calibration_recovers_perfect():
    rng = np.random.default_rng(0)
    p = rng.uniform(0.05, 0.95, 20000)
    y = (rng.uniform(size=20000) < p).astype(float)
    b, a = calibration_slope_intercept(y, p)
    assert abs(b - 1) < 0.05 and abs(a) < 0.05
    assert ece(y, p) < 0.02
    # over-confident model -> slope < 1
    logit = np.log(p / (1 - p)) * 2
    q = 1 / (1 + np.exp(-logit))
    b2, _ = calibration_slope_intercept(y, q)
    assert b2 < 0.7


def test_bootstrap_sign():
    rng = np.random.default_rng(1)
    p = rng.uniform(0.1, 0.9, 5000); y = (rng.uniform(size=5000) < p).astype(float)
    noisy = np.clip(p + rng.normal(0, 0.15, 5000), 0.01, 0.99)
    r = bootstrap_diff(y, p, noisy, n_boot=200)
    assert r["diff"] < 0 and r["ci_high"] < 0
