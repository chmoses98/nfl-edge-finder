"""Exact, integer-support discrete outcome distributions that keep key numbers, plus the scoring that judges them.
RESEARCH_ONLY: nothing here is wired into any pricer, card, gate or model registry.

WHY NOT A CONTINUOUS RESIDUAL. The incumbent adds a historical residual to a target spread; that convolution is
translation-invariant and smears the integer structure of football scores (the M1-K note in sim/key_numbers.py measured
7.9% simulated vs 15.4% realised final margins of exactly 3). Here the predictive distribution is built from REAL
historical outcomes of games whose predicted location was close to the new game's, so every mass point is a score that
actually happened (3, 7, 10, 14 ... keep their weight, 1Q/1H totals keep their zeros), then tilted so the mean equals the
location prediction. No key number is imposed or hard-coded: ``emergent_keys`` reports them from TRAINING data only.

THE ONLY THING THAT DIFFERS between baseline and candidate is the location ``mu`` (market-only vs market + opponent-
adjusted matchup evidence). The same kernel, tilt, recency weighting and smoothing blend are applied to both, so a score
difference is attributable to the evidence and not to the shape machinery.
"""
from __future__ import annotations

import math

import numpy as np

LOG_FLOOR = 1e-4
BLEND = 0.02                    # share of a discretised normal mixed in so unseen scores keep non-zero mass; same for every model
HALFLIFE_SEASONS = 3.0          # same recency weighting as the incumbent bank (pricing/game_env.py)
MIN_EFF_N = 150                 # bandwidth doubles until the kernel sample is at least this large (M1-S uses the same floor)


def _norm_cdf(x):
    return 0.5 * (1.0 + np.vectorize(math.erf)(np.asarray(x, float) / math.sqrt(2.0)))


def fit_ridge(X, y, penalty):
    """Ridge with a per-column penalty vector (0 = unpenalised). X must already include the intercept column."""
    X, y = np.asarray(X, float), np.asarray(y, float)
    A = X.T @ X + np.diag(np.asarray(penalty, float))
    return np.linalg.solve(A + 1e-9 * np.eye(len(A)), X.T @ y)


def standardize_fit(X):
    X = np.asarray(X, float)
    mu, sd = X.mean(axis=0), X.std(axis=0)
    return mu, np.where(sd > 1e-12, sd, 1.0)


def _tilt_theta(y, w, mu, iters=60):
    """theta so that sum(q*y)=mu for q ~ w*exp(theta*(y-mu)); 0 when the target is outside the support."""
    d = y - mu
    if d.min() >= 0 or d.max() <= 0:
        return 0.0
    th = 0.0
    for _ in range(iters):
        a = np.log(np.maximum(w, 1e-300)) + th * d
        q = np.exp(a - a.max()); q /= q.sum()
        g = float(q @ d)
        if abs(g) < 1e-10:
            break
        v = float(q @ (d * d) - g * g) + 1e-9
        th -= g / v if abs(g / v) < 5 else 5 * np.sign(g / v)
    return th


def kernel_pmf(mu_train, y_train, season_train, mu_new, ref_season, h, *, halflife=HALFLIFE_SEASONS, min_eff=MIN_EFF_N,
               lo=None, hi=None, blend=BLEND):
    """PMF on integers lo..hi. Returns (support, pmf, info)."""
    mu_t, y_t, s_t = (np.asarray(a, float) for a in (mu_train, y_train, season_train))
    rec = 0.5 ** ((ref_season - s_t) / halflife)
    hh = float(h)
    for _ in range(8):
        w = np.exp(-0.5 * ((mu_t - mu_new) / hh) ** 2) * rec
        eff = w.sum() ** 2 / max((w ** 2).sum(), 1e-300)
        if eff >= min_eff:
            break
        hh *= 2
    th = _tilt_theta(y_t, w, mu_new)
    a = np.log(np.maximum(w, 1e-300)) + th * (y_t - mu_new)
    q = np.exp(a - a.max()); q /= q.sum()
    lo = int(np.floor(y_t.min())) if lo is None else lo
    hi = int(np.ceil(y_t.max())) if hi is None else hi
    support = np.arange(lo, hi + 1)
    emp = np.zeros(len(support))
    idx = np.clip(np.round(y_t).astype(int) - lo, 0, len(support) - 1)
    np.add.at(emp, idx, q)
    sigma = max(float(np.sqrt(q @ (y_t - mu_new) ** 2)), 1.0)
    gauss = _norm_cdf((support + 0.5 - mu_new) / sigma) - _norm_cdf((support - 0.5 - mu_new) / sigma)
    gauss = gauss / gauss.sum()
    pmf = (1 - blend) * emp + blend * gauss
    return support, pmf / pmf.sum(), {"h": hh, "eff_n": float(1.0 / (q ** 2).sum()), "theta": float(th), "sigma": sigma}


def pmf_from_draws(draws, lo, hi, blend=BLEND):
    """Incumbent-style simulated draws as a PMF with the SAME smoothing blend, for a like-for-like comparison."""
    d = np.round(np.asarray(draws, float)).astype(int)
    support = np.arange(lo, hi + 1)
    emp = np.bincount(np.clip(d - lo, 0, len(support) - 1), minlength=len(support)).astype(float)
    emp /= emp.sum()
    mu, sigma = float(d.mean()), max(float(d.std()), 1.0)
    gauss = _norm_cdf((support + 0.5 - mu) / sigma) - _norm_cdf((support - 0.5 - mu) / sigma)
    gauss = gauss / gauss.sum()
    pmf = (1 - blend) * emp + blend * gauss
    return support, pmf / pmf.sum()


def log_score(support, pmf, y):
    i = int(round(y)) - int(support[0])
    p = pmf[i] if 0 <= i < len(pmf) else 0.0
    return math.log(max(float(p), LOG_FLOOR))


def survival(support, pmf, k):
    """P(Y > k) for a half-point or integer threshold k."""
    return float(pmf[support > k].sum())


def ladder_events(support, pmf, mu, y, offsets=tuple(np.arange(-10.5, 11.0, 1.0))):
    """[(P(Y>k), 1{y>k})] on half-point thresholds around floor(mu): the contracts Kalshi lists."""
    base = math.floor(mu)
    return [(survival(support, pmf, base + o), float(y > base + o)) for o in offsets]


def brier(pairs):
    p = np.array([a for a, _ in pairs]); o = np.array([b for _, b in pairs])
    return float(np.mean((p - o) ** 2))


def reliability(pairs, n_bins=10):
    p = np.array([a for a, _ in pairs]); o = np.array([b for _, b in pairs])
    edges = np.linspace(0, 1, n_bins + 1)
    rows, ece = [], 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (p >= lo) & ((p < hi) | (hi >= 1.0))
        if m.sum():
            rows.append({"lo": float(lo), "hi": float(hi), "n": int(m.sum()), "mean_pred": float(p[m].mean()), "obs_rate": float(o[m].mean())})
            ece += m.sum() / len(p) * abs(p[m].mean() - o[m].mean())
    return rows, float(ece)


def key_mass(support, pmf, keys):
    return float(sum(pmf[support == k].sum() for k in keys))


def emergent_keys(values, *, h=2.0, z=2.0, top=8, absolute=False):
    """Values whose TRAINING frequency exceeds a Gaussian-smoothed copy of the same histogram by > z binomial SEs.
    Reported from data, never imposed on a distribution."""
    v = np.round(np.asarray(values, float)).astype(int)
    if absolute:
        v = np.abs(v)
    lo = v.min()
    f = np.bincount(v - lo) / len(v)
    sup = np.arange(len(f))
    K = np.exp(-0.5 * ((sup[:, None] - sup[None, :]) / h) ** 2)
    sm = (K @ f) / K.sum(axis=1)
    out = []
    for i, fi in enumerate(f):
        se = math.sqrt(max(sm[i] * (1 - sm[i]), 1e-12) / len(v))
        zi = (fi - sm[i]) / se
        if zi > z:
            out.append((int(i + lo), float(zi)))
    out.sort(key=lambda t: -t[1])
    return [k for k, _ in out[:top]]


def paired_bootstrap_ci(diffs, groups, *, B=2000, seed=20261102, alpha=0.10):
    """Mean of paired per-row differences with a GROUP bootstrap (rows of one game are resampled together)."""
    d = np.asarray(diffs, float)
    g = np.asarray(groups)
    uniq, inv = np.unique(g, return_inverse=True)
    sums = np.bincount(inv, weights=d, minlength=len(uniq)); cnt = np.bincount(inv, minlength=len(uniq)).astype(float)
    rng = np.random.default_rng(seed)
    means = np.empty(B)
    for b in range(B):
        pick = rng.integers(0, len(uniq), len(uniq))
        means[b] = sums[pick].sum() / cnt[pick].sum()
    return {"mean": float(d.mean()), "lo": float(np.quantile(means, alpha / 2)), "hi": float(np.quantile(means, 1 - alpha / 2)), "n_rows": int(len(d)), "n_groups": int(len(uniq))}
