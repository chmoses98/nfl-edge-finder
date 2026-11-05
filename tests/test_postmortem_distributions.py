"""Issue #231: key-number-aware distributions and their scoring (synthetic; the real held-out run is dist_eval)."""
import numpy as np

from nfl_edge.postmortem import distributions as DS


def margins(n, seed=0):
    """A margin world with a real spike at exactly 3 and 7 (as football has) on top of a smooth bulk."""
    rng = np.random.default_rng(seed)
    smooth = np.round(rng.normal(0, 13, n)).astype(int)
    spike = rng.random(n) < 0.30
    return np.where(spike, rng.choice([3, 7, -3, -7], n), smooth).astype(float)


def test_kernel_pmf_is_a_distribution_with_the_requested_mean_and_keeps_key_number_mass():
    y = margins(6000)
    mu_tr = np.zeros(len(y))
    sup, pmf, info = DS.kernel_pmf(mu_tr, y, np.full(len(y), 2023), 0.0, 2024, 2.0, lo=-60, hi=60)
    assert abs(pmf.sum() - 1) < 1e-12 and abs((sup * pmf).sum()) < 0.2
    spike = pmf[sup == 3].sum()
    assert spike > 0.05                                           # the empirical spike survives
    smooth = DS._norm_cdf((3.5 - 0) / 13) - DS._norm_cdf((2.5 - 0) / 13)
    assert spike > 2 * smooth                                     # a continuous residual would give ~0.03


def test_unseen_scores_keep_nonzero_mass_and_log_score_is_floored():
    y = np.full(200, 20.0)
    sup, pmf, _ = DS.kernel_pmf(np.full(200, 20.0), y, np.full(200, 2023), 20.0, 2024, 1.0, lo=0, hi=50)
    assert pmf[sup == 22].sum() > 0 and DS.log_score(sup, pmf, 22) > np.log(DS.LOG_FLOOR)      # never seen in training, still priced
    assert DS.log_score(sup, pmf, 500) == np.log(DS.LOG_FLOOR)


def test_tilt_moves_the_mean_to_the_location_prediction():
    rng = np.random.default_rng(1)
    mu_tr = rng.normal(22, 3, 4000); y = np.round(mu_tr + rng.normal(0, 7, 4000)).clip(0)
    sup, pmf, _ = DS.kernel_pmf(mu_tr, y, np.full(4000, 2023), 26.0, 2024, 1.5, lo=0, hi=70)
    assert abs((sup * pmf).sum() - 26.0) < 0.35


def test_a_better_location_scores_better_than_the_market_only_location():
    rng = np.random.default_rng(2); n = 4000
    signal = rng.normal(0, 3, n); market = rng.normal(22, 3, n)
    y = np.round(market + signal + rng.normal(0, 6, n)).clip(0)
    tr, te = slice(0, 3000), slice(3000, n)
    def mean_ls(mu):
        out = []
        for i in range(3000, n, 4):
            s, p, _ = DS.kernel_pmf(mu[tr], y[tr], np.full(3000, 2023), float(mu[i]), 2024, 2.0, lo=0, hi=70)
            out.append(DS.log_score(s, p, y[i]))
        return np.mean(out)
    assert mean_ls(market + signal) > mean_ls(market) + 0.02


def test_emergent_keys_come_from_data_and_are_not_imposed():
    keys = DS.emergent_keys(margins(8000), absolute=True)
    assert 3 in keys and 7 in keys
    assert DS.emergent_keys(np.round(np.random.default_rng(3).normal(0, 13, 8000)), absolute=True)[:1] in ([], [0], [1], [2])


def test_ridge_leaves_market_columns_unpenalised():
    rng = np.random.default_rng(4); X = np.column_stack([np.ones(500), rng.normal(size=500), rng.normal(size=500)])
    y = 2 + 3 * X[:, 1] + rng.normal(0, .1, 500)
    b = DS.fit_ridge(X, y, [0, 0, 1e6])
    assert abs(b[1] - 3) < 0.05 and abs(b[2]) < 1e-3


def test_ladder_events_and_reliability_are_coherent():
    sup = np.arange(0, 60); pmf = np.exp(-0.5 * ((sup - 22) / 7) ** 2); pmf /= pmf.sum()
    ev = DS.ladder_events(sup, pmf, 22.0, 24.0)
    assert all(0 <= p <= 1 for p, _ in ev) and ev[0][0] > ev[-1][0]
    assert all(o in (0.0, 1.0) for _, o in ev)
    rel, ece = DS.reliability(ev)
    assert rel and 0 <= ece <= 1


def test_paired_bootstrap_groups_rows_by_game():
    d = np.r_[np.full(50, 0.1), np.full(50, 0.1)]
    ci = DS.paired_bootstrap_ci(d, np.repeat(np.arange(50), 2), B=200)
    assert abs(ci["mean"] - 0.1) < 1e-9 and ci["n_groups"] == 50 and ci["lo"] <= 0.1 + 1e-9 <= ci["hi"] + 2e-9


def test_committed_evaluation_report_never_overclaims():
    import json, os
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "research", "postmortem_2026-11-02", "distribution_eval.json")
    r = json.load(open(p))
    assert r["splits"]["test"] == [2024, 2025] and r["splits"]["calibration"] == [2022, 2023]
    for name, t in r["targets"].items():
        d = t["paired_log_score_diff"]["candidate_minus_market_only"]
        if t["verdict_vs_market_only"] == "EVIDENCE_IMPROVES":
            assert d["lo"] > 0 and all(v > 0 for v in t["season_diffs"].values()), name
        if d["lo"] <= 0:
            assert t["verdict_vs_market_only"] != "EVIDENCE_IMPROVES", name
