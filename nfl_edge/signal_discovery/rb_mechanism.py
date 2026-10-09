"""Football Signal Discovery Lab, Wave 2B (NFL): RB receptions market-mechanism study. RESEARCH ONLY. PURE.

docs/research/RB_RECEPTIONS_MECHANISM_PROTOCOL.md (pre-registered at a5f18324). Explanatory diagnostics of why YES on the
RB-receptions natural rung settled below its price in the (discovery-contaminated) 2025 and 2026 samples. Nothing here
is a rule, filter, probability for trading, stake or recommendation; the frozen Wave-2 rule is imported, never
restated (`W.ladder`, `W.valid`, `W.contract`). Population membership is decided by functions that take no outcome.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable
from typing import Any

import numpy as np

from nfl_edge.signal_discovery import wave2 as W

VERSION = "nfl_rb_receptions_mechanism/1.0.0"
PROTOCOL_COMMIT = "a5f18324bdb0f7b5b6f2840af9a000dd3a9eedc0"
PROTOCOL_SHA256 = "aa7f6bb46841d3e55760f83bb9d200d160d7f0e81ff71718313ac26c8a2a41f8"
SEED, N_BOOT = W.SEED, W.N_BOOT

CAPTURED_NO_ASK = "CAPTURED_NO_ASK"
RECONSTRUCTED_NO_ASK = "RECONSTRUCTED_NO_ASK"
NOT_AVAILABLE_2025 = "NOT_AVAILABLE_2025"
SETTLEMENT_UNAVAILABLE = "SETTLEMENT_UNAVAILABLE"
NON_BINARY_SETTLEMENT = "NON_BINARY_SETTLEMENT"

POPULATIONS = ("P1", "P2", "P3", "P4", "P5")
#: protocol section 2, matched-control support (fixed before results)
MATCH = {"yes_ask_lo": 0.30, "yes_ask_hi": 0.70, "max_spread": 0.03, "min_valid_rungs": 3, "max_checkpoint_age_min": 90.0}
NO_ASK_BUCKETS = [(0.20, 0.30), (0.30, 0.40), (0.40, 0.50), (0.50, 0.60), (0.60, 0.70), (0.70, 0.80)]
YES_ASK_BUCKETS = [(0.0, 0.30), (0.30, 0.40), (0.40, 0.50), (0.50, 0.60), (0.60, 0.70), (0.70, 1.0)]
DIST_BUCKETS = [(0.0, 0.05), (0.05, 0.15), (0.15, 0.30), (0.30, 0.51)]
REL_BINS = ("<=t-3", "t-2", "t-1", "t", "t+1", "t+2", ">=t+3")
PMF_BINS = ("<=t-2", "t-1", "t", "t+1", ">=t+2")
CONCENTRATED_BACKFIELD = 0.60


class MechanismIntegrityError(RuntimeError):
    """A study output would touch the prospective store, or a frozen invariant does not hold."""


def assert_not_prospective(path: str) -> None:
    text = str(path).replace("\\", "/")
    if "signal_lab_wave2" in text or "data/research/wave2" in text or text.rstrip("/").endswith("market-data") or "/md/" in text:
        raise MechanismIntegrityError(f"mechanism outputs may not be written into a prospective / market-data tree: {text}")


# --------------------------------------------------------------------------- prices


def _f(x) -> float | None:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(v) else v


def representations(yes_bid, yes_ask, no_bid, no_ask) -> dict[str, float | None]:
    """A YES ask, B YES mid, C YES mid / (YES mid + NO mid); D (repo canonical fair estimator) does not exist."""
    yb, ya, nb, na = (_f(v) for v in (yes_bid, yes_ask, no_bid, no_ask))
    ymid = (yb + ya) / 2 if yb is not None and ya is not None else None
    nmid = (nb + na) / 2 if nb is not None and na is not None else None
    norm = ymid / (ymid + nmid) if ymid is not None and nmid is not None and (ymid + nmid) > 0 else None
    return {
        "A_yes_ask": ya,
        "B_yes_mid": ymid,
        "C_norm_mid": norm,
        "no_mid": nmid,
        "ask_sum": round(ya + na, 4) if ya is not None and na is not None else None,
        "yes_spread": round(ya - yb, 4) if ya is not None and yb is not None else None,
        "no_spread": round(na - nb, 4) if na is not None and nb is not None else None,
    }


# --------------------------------------------------------------------------- populations (outcome-blind)


def natural_and_rungs(rungs: list[dict[str, Any]]) -> dict[str, Any]:
    """The frozen ladder (W.ladder) plus each valid rung's offset from the natural rung. No outcome is read."""
    lad = W.ladder(rungs)
    valid = sorted((r for r in rungs if r.get("threshold") is not None and W.valid(r.get("yes_bid"), r.get("yes_ask"))),
                   key=lambda r: float(r["threshold"]))
    nat = lad["natural"]
    idx = None
    if nat is not None:
        idx = next(i for i, r in enumerate(valid) if r["ticker"] == nat["ticker"])
    out = []
    for i, r in enumerate(valid):
        mid = (r["yes_bid"] + r["yes_ask"]) / 2
        out.append({**r, "threshold": float(r["threshold"]), "offset": None if idx is None else i - idx,
                    "is_natural": idx is not None and i == idx, "dist_half": abs(mid - 0.5)})
    return {"natural": nat, "market_median": lad["market_median"], "valid_rungs": out, "n_rungs": len(rungs),
            "n_valid": len(valid)}


def membership_key(row: dict[str, Any]) -> tuple:
    """The identity of a population row: never includes an outcome field."""
    return (row["pop"], row["game_id"], row["player_id"], row["stat"], row["ticker"])


OUTCOME_FIELDS = ("actual", "result", "settlement_value", "y", "no_pnl", "yes_pnl", "no_win", "settle_source")


def strip_outcomes(row: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in row.items() if k not in OUTCOME_FIELDS}


# --------------------------------------------------------------------------- settlement


def settle(row: dict[str, Any], exchange: dict[str, Any] | None, nfl_actual: float | None) -> dict[str, Any]:
    """Attach the exchange result (binary) and the nflverse stat. YES iff stat >= t; a non-binary exchange value (an
    active player who never took a snap settles at the pre-game fair price) is flagged and kept out of binary tables."""
    res = (exchange or {}).get("result")
    val = _f((exchange or {}).get("settlement_value_dollars"))
    out = {"result": res, "settlement_value": val, "actual": nfl_actual}
    if res in ("yes", "no") and (val is None or val in (0.0, 1.0)):
        out["y"] = 1 if res == "yes" else 0
        out["settle_source"] = "EXCHANGE"
    elif val is not None and 0.0 < val < 1.0:
        out["y"] = None
        out["settle_source"] = NON_BINARY_SETTLEMENT
    else:
        out["y"] = None
        out["settle_source"] = SETTLEMENT_UNAVAILABLE
    if out["y"] is not None and nfl_actual is not None:
        out["stat_agrees"] = (nfl_actual >= row["threshold"]) == (out["y"] == 1)
    else:
        out["stat_agrees"] = None
    return out


def economics_row(row: dict[str, Any]) -> dict[str, Any]:
    """Fee-adjusted P/L of NO at the NO ask and YES at the YES ask (each side's own fee)."""
    out = {}
    y = row.get("y")
    if y is None:
        return out
    for side in ("no", "yes"):
        ask, fee = row.get(f"{side}_ask"), row.get(f"fee_{side}")
        if ask is None or fee is None or not W.executable(ask):
            continue
        win = (y == 0) if side == "no" else (y == 1)
        out[f"{side}_win"] = win
        out[f"{side}_outlay"] = ask + fee
        out[f"{side}_pnl"] = (1.0 if win else 0.0) - ask - fee
    return out


# --------------------------------------------------------------------------- bootstrap


def _cluster_index(clusters: list[str]) -> tuple[list[str], dict[str, list[int]]]:
    by: dict[str, list[int]] = defaultdict(list)
    for i, c in enumerate(clusters):
        by[c].append(i)
    return sorted(by), by


def boot_stat(rows: list[dict[str, Any]], stat: Callable[[list[dict[str, Any]]], float | None], cluster: str = "game_id",
              n_boot: int = N_BOOT, seed: int = SEED) -> dict[str, Any]:
    """Cluster bootstrap of an arbitrary statistic; 95 % percentile interval and a two-sided p-value for 0."""
    est = stat(rows)
    if est is None or len(rows) < 2:
        return {"est": est, "ci95": None, "p_two_sided": None, "n": len(rows)}
    keys, by = _cluster_index([str(r.get(cluster)) for r in rows])
    if len(keys) < 2:
        return {"est": est, "ci95": None, "p_two_sided": None, "n": len(rows)}
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(keys), size=(n_boot, len(keys)))
    vals = []
    for d in draws:
        sample = [rows[i] for k in d for i in by[keys[k]]]
        v = stat(sample)
        if v is not None and np.isfinite(v):
            vals.append(v)
    if not vals:
        return {"est": est, "ci95": None, "p_two_sided": None, "n": len(rows)}
    a = np.asarray(vals)
    p = 2 * min((a <= 0).mean(), (a >= 0).mean())
    return {"est": est, "ci95": [float(np.quantile(a, 0.025)), float(np.quantile(a, 0.975))], "p_two_sided": float(min(1.0, p)),
            "n": len(rows), "clusters": len(keys)}


def mean_of(field: str) -> Callable[[list[dict[str, Any]]], float | None]:
    def f(rows):
        v = [r[field] for r in rows if r.get(field) is not None]
        return float(np.mean(v)) if v else None
    return f


def roi_of(side: str) -> Callable[[list[dict[str, Any]]], float | None]:
    def f(rows):
        rs = [r for r in rows if r.get(f"{side}_pnl") is not None]
        o = sum(r[f"{side}_outlay"] for r in rs)
        return sum(r[f"{side}_pnl"] for r in rs) / o if o else None
    return f


def bh(pvals: dict[str, float | None]) -> dict[str, float | None]:
    """Benjamini-Hochberg q-values over the non-missing p-values."""
    items = sorted(((k, p) for k, p in pvals.items() if p is not None), key=lambda x: x[1])
    m = len(items)
    q: dict[str, float | None] = {k: None for k in pvals}
    prev = 1.0
    for rank in range(m, 0, -1):
        k, p = items[rank - 1]
        prev = min(prev, p * m / rank)
        q[k] = prev
    return q


def wilson(k: int, n: int) -> list[float] | None:
    return W.wilson(k, n)


# --------------------------------------------------------------------------- summaries


def residual_fields(row: dict[str, Any]) -> dict[str, Any]:
    y = row.get("y")
    out = {}
    for rep in ("A_yes_ask", "B_yes_mid", "C_norm_mid"):
        p = row.get(rep)
        out[f"r_{rep[0]}"] = None if y is None or p is None else y - p
    return out


def calib_summary(rows: list[dict[str, Any]], cluster: str = "game_id") -> dict[str, Any]:
    rows = [r for r in rows if r.get("y") is not None]
    n = len(rows)
    if not n:
        return {"n": 0}
    ys = sum(r["y"] for r in rows)
    out: dict[str, Any] = {"n": n, "games": len({r["game_id"] for r in rows}), "players": len({r["player_id"] for r in rows}),
                           "yes_rate": ys / n, "yes_rate_ci95": wilson(ys, n)}
    for rep in ("A_yes_ask", "B_yes_mid", "C_norm_mid"):
        ps = [r.get(rep) for r in rows]
        if any(p is None for p in ps):
            have = [r for r in rows if r.get(rep) is not None]
            if not have:
                out[rep] = None
                continue
        else:
            have = rows
        out[rep] = {"n": len(have), "mean_p": float(np.mean([r[rep] for r in have])),
                    "residual": boot_stat(have, mean_of(f"r_{rep[0]}"), cluster)}
    out["no_roi"] = boot_stat(rows, roi_of("no"), cluster)
    out["yes_roi"] = boot_stat(rows, roi_of("yes"), cluster)
    nw = [r for r in rows if r.get("no_win") is not None]
    out["no_record"] = f"{sum(1 for r in nw if r['no_win'])}-{sum(1 for r in nw if not r['no_win'])}"
    out["mean_no_ask"] = float(np.mean([r["no_ask"] for r in rows if r.get("no_ask") is not None])) if any(r.get("no_ask") is not None for r in rows) else None
    return out


def scores(rows: list[dict[str, Any]], rep: str) -> dict[str, Any]:
    """Brier, log loss and (when supported) logistic calibration intercept/slope of y on logit(p)."""
    have = [r for r in rows if r.get("y") is not None and r.get(rep) is not None and 0 < r[rep] < 1]
    if not have:
        return {"n": 0}
    y = np.array([r["y"] for r in have], float)
    p = np.array([r[rep] for r in have], float)
    out = {"n": len(have), "brier": float(np.mean((p - y) ** 2)),
           "log_loss": float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))),
           "brier_baserate": float(np.mean((y.mean() - y) ** 2))}
    if len(have) >= 60 and y.sum() >= 15 and (1 - y).sum() >= 15:
        out["logistic"] = logistic_calibration(y, p)
    else:
        out["logistic"] = "NOT_SUPPORTED (n < 60 or < 15 per outcome)"
    return out


def logistic_calibration(y: np.ndarray, p: np.ndarray) -> dict[str, float]:
    """Newton-Raphson logit(P(y=1)) = a + b * logit(p). Perfect calibration: a = 0, b = 1."""
    x = np.log(p / (1 - p))
    X = np.column_stack([np.ones_like(x), x])
    beta = np.zeros(2)
    for _ in range(50):
        eta = X @ beta
        mu = 1 / (1 + np.exp(-eta))
        w = mu * (1 - mu)
        H = X.T @ (X * w[:, None])
        g = X.T @ (y - mu)
        step = np.linalg.solve(H + 1e-9 * np.eye(2), g)
        beta = beta + step
        if np.max(np.abs(step)) < 1e-10:
            break
    cov = np.linalg.inv(H)
    se = np.sqrt(np.diag(cov))
    # calibration-in-the-large: intercept with slope fixed at 1 (offset model)
    a = 0.0
    for _ in range(50):
        mu = 1 / (1 + np.exp(-(a + x)))
        step = (y - mu).sum() / (mu * (1 - mu)).sum()
        a += step
        if abs(step) < 1e-12:
            break
    return {"intercept": float(beta[0]), "slope": float(beta[1]), "intercept_se": float(se[0]), "slope_se": float(se[1]),
            "calibration_in_the_large": float(a)}


def bucket_label(v: float | None, buckets: list[tuple[float, float]]) -> str | None:
    if v is None:
        return None
    for lo, hi in buckets:
        if lo <= v < hi - 1e-12 or (hi >= 1.0 and lo <= v <= hi):
            return f"{lo:.2f}-{hi - 0.01:.2f}"
    return None


def table_by(rows: list[dict[str, Any]], key: Callable[[dict[str, Any]], Any]) -> dict[str, Any]:
    groups: dict[str, list] = defaultdict(list)
    for r in rows:
        k = key(r)
        if k is not None:
            groups[str(k)].append(r)
    return {k: compact(v) for k, v in sorted(groups.items())}


def compact(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Descriptive cell: n, realized YES rate, mean A/B/C, mean residual (B), NO record / ROI / break-even."""
    rows = [r for r in rows if r.get("y") is not None]
    n = len(rows)
    if not n:
        return {"n": 0}
    out: dict[str, Any] = {"n": n, "yes_rate": sum(r["y"] for r in rows) / n}
    for rep in ("A_yes_ask", "B_yes_mid", "C_norm_mid"):
        v = [r[rep] for r in rows if r.get(rep) is not None]
        out[f"mean_{rep[0]}"] = float(np.mean(v)) if v else None
    rb = [r["r_B"] for r in rows if r.get("r_B") is not None]
    out["resid_B"] = float(np.mean(rb)) if rb else None
    nr = [r for r in rows if r.get("no_pnl") is not None]
    if nr:
        o = sum(r["no_outlay"] for r in nr)
        w = sum(1 for r in nr if r["no_win"])
        out.update({"no_n": len(nr), "no_wins": w, "no_win_rate": w / len(nr), "mean_no_ask": float(np.mean([r["no_ask"] for r in nr])),
                    "no_breakeven": float(np.mean([r["no_outlay"] for r in nr])), "no_pnl": round(sum(r["no_pnl"] for r in nr), 4),
                    "no_roi": sum(r["no_pnl"] for r in nr) / o})
    yr = [r for r in rows if r.get("yes_pnl") is not None]
    if yr:
        o = sum(r["yes_outlay"] for r in yr)
        out["yes_roi"] = sum(r["yes_pnl"] for r in yr) / o
    return out


# --------------------------------------------------------------------------- discrete / distribution


def rel_bin(actual: float, t: float) -> str:
    d = int(round(actual - t))
    if d <= -3:
        return "<=t-3"
    if d >= 3:
        return ">=t+3"
    return {-2: "t-2", -1: "t-1", 0: "t", 1: "t+1", 2: "t+2"}[d]


def miss_class(actual: float, t: float, y: int | None, settle_source: str | None) -> str:
    if settle_source == NON_BINARY_SETTLEMENT:
        return "NO_SNAP_NON_BINARY"
    if y == 0:  # YES lost / NO won
        if actual is None:
            return "YES_LOSS_STAT_MISSING"
        if actual == 0:
            return "YES_LOSS_ZERO"
        if actual == t - 1:
            return "YES_LOSS_NEAR_MISS"
        return "YES_LOSS_LOW_VOLUME"
    if y == 1:
        if actual is None:
            return "NO_LOSS_STAT_MISSING"
        if actual == t:
            return "NO_LOSS_AT_T"
        if actual == t + 1:
            return "NO_LOSS_T+1"
        return "NO_LOSS_T+2_OR_MORE"
    return "UNSETTLED"


def survival_from_rungs(rungs: list[tuple[float, float]]) -> dict[int, float]:
    """S(k) = P(X >= k) at integer thresholds from valid-rung probabilities (k <= 0 -> 1). Not repaired."""
    s = {int(round(t)): p for t, p in rungs if abs(t - round(t)) < 1e-9}
    return s


def implied_bins(S: dict[int, float], t: int) -> dict[str, float] | None:
    """Market-implied mass in PMF_BINS around t; needs S at t-1 .. t+2 (S(k)=1 for k <= 0). None if not covered."""
    def s(k):
        if k <= 0:
            return 1.0
        return S.get(k)
    need = [s(t - 1), s(t), s(t + 1), s(t + 2)]
    if any(v is None for v in need):
        return None
    a, b, c, d = need
    return {"<=t-2": 1.0 - a, "t-1": a - b, "t": b - c, "t+1": c - d, ">=t+2": d}


def realized_bins(actual: float, t: int) -> dict[str, float]:
    d = int(round(actual)) - t
    lab = "<=t-2" if d <= -2 else ">=t+2" if d >= 2 else {-1: "t-1", 0: "t", 1: "t+1"}[d]
    return {b: 1.0 if b == lab else 0.0 for b in PMF_BINS}


def implied_pmf(S: dict[int, float]) -> dict[str, Any]:
    """Full implied PMF over the contiguous covered range; negative masses (monotonicity violations) are kept."""
    ks = sorted(k for k in S if k >= 1)
    if not ks:
        return {"covered": False}
    lo, hi = ks[0], ks[-1]
    contiguous = ks == list(range(lo, hi + 1))
    if not contiguous:
        return {"covered": False, "reason": "NON_CONTIGUOUS"}
    pmf = {f"<{lo}": 1.0 - S[lo]}
    for k in range(lo, hi):
        pmf[str(k)] = S[k] - S[k + 1]
    pmf[f">={hi}"] = S[hi]
    mean = None
    if lo <= 2 and S[hi] <= 0.10:
        # lower-bound style mean: lower tail at lo-1 (or 0), upper tail at hi
        m = (lo - 1 if lo >= 1 else 0) * (1.0 - S[lo]) + sum(k * (S[k] - S[k + 1]) for k in range(lo, hi)) + hi * S[hi]
        mean = m
    return {"covered": True, "lo": lo, "hi": hi, "pmf": pmf, "implied_mean_lb": mean,
            "negative_mass": [k for k, v in pmf.items() if v < -1e-9]}


def monotone_violations(rungs: list[tuple[float, float]]) -> int:
    rs = sorted(rungs)
    return sum(1 for (t1, p1), (t2, p2) in zip(rs, rs[1:], strict=False) if p2 > p1 + 1e-9)


def poisson_sf(k: int, lam: float) -> float:
    """P(X >= k), X ~ Poisson(lam)."""
    if k <= 0:
        return 1.0
    p, c = math.exp(-lam), 0.0
    for i in range(k):
        c += p
        p *= lam / (i + 1)
    return max(0.0, 1.0 - c)


def nb_pmf(k: int, mu: float, alpha: float) -> float:
    """NB2 with mean mu, Var = mu + alpha mu^2 (alpha -> 0: Poisson)."""
    if alpha <= 1e-9:
        return math.exp(-mu + k * math.log(mu) - math.lgamma(k + 1)) if mu > 0 else (1.0 if k == 0 else 0.0)
    r = 1.0 / alpha
    p = r / (r + mu)
    return math.exp(math.lgamma(k + r) - math.lgamma(r) - math.lgamma(k + 1) + r * math.log(p) + k * math.log(1 - p))


def nb_sf(k: int, mu: float, alpha: float) -> float:
    if k <= 0:
        return 1.0
    return max(0.0, 1.0 - sum(nb_pmf(i, mu, alpha) for i in range(k)))


def fit_poisson_to_ladder(rungs: list[tuple[float, float]]) -> float | None:
    """Least-squares Poisson mean to a ladder's survival points S(k) (grid + refine). Explanatory only."""
    pts = [(int(round(t)), p) for t, p in rungs if abs(t - round(t)) < 1e-9 and t >= 1]
    if not pts:
        return None
    best, bl = None, None
    for lam in np.arange(0.05, 15.0, 0.01):
        loss = sum((poisson_sf(k, lam) - p) ** 2 for k, p in pts)
        if bl is None or loss < bl:
            best, bl = float(lam), loss
    return best


def dispersion_by_bin(values: list[tuple[float, float]], n_bins: int = 10) -> list[dict[str, float]]:
    """(baseline, outcome) pairs -> per-quantile-bin mean, variance, P(0), NB2 alpha (moments)."""
    if not values:
        return []
    b = np.array([v[0] for v in values], float)
    y = np.array([v[1] for v in values], float)
    edges = np.quantile(b, np.linspace(0, 1, n_bins + 1))
    out = []
    for i in range(n_bins):
        m = (b >= edges[i]) & ((b < edges[i + 1]) if i < n_bins - 1 else (b <= edges[i + 1]))
        if m.sum() < 30:
            continue
        mu, var = float(y[m].mean()), float(y[m].var(ddof=1))
        alpha = max(0.0, (var - mu) / mu ** 2) if mu > 0 else 0.0
        out.append({"lo": float(edges[i]), "hi": float(edges[i + 1]), "n": int(m.sum()), "mean": mu, "var": var,
                    "var_over_mean": var / mu if mu > 0 else None, "p0": float((y[m] == 0).mean()),
                    "p0_poisson": math.exp(-mu), "alpha_nb2": alpha, "p0_nb": nb_pmf(0, mu, alpha)})
    return out


# --------------------------------------------------------------------------- concentration


def player_table(rows: list[dict[str, Any]], key: str = "player_id") -> list[dict[str, Any]]:
    by: dict[str, list] = defaultdict(list)
    for r in rows:
        if r.get("no_pnl") is not None:
            by[str(r.get(key))].append(r)
    tot = sum(r["no_pnl"] for v in by.values() for r in v)
    out = []
    for k, rs in by.items():
        pnl = sum(r["no_pnl"] for r in rs)
        o = sum(r["no_outlay"] for r in rs)
        out.append({key: k, "name": rs[0].get("player_name"), "team": rs[0].get("team"), "n": len(rs),
                    "thresholds": [r["threshold"] for r in rs], "no_asks": [r["no_ask"] for r in rs],
                    "actual": [r.get("actual") for r in rs], "record": f"{sum(1 for r in rs if r['no_win'])}-{sum(1 for r in rs if not r['no_win'])}",
                    "pnl": round(pnl, 4), "roi": pnl / o if o else None, "share_of_total_pnl": pnl / tot if tot else None})
    return sorted(out, key=lambda d: (-d["pnl"], -d["n"], d[key]))


def roi_without_top(rows: list[dict[str, Any]], key: str, top: int) -> dict[str, Any] | None:
    """Wave-2A convention: remove the `top` groups with the largest summed P/L (ties by key)."""
    tot: dict[str, float] = defaultdict(float)
    for r in rows:
        if r.get("no_pnl") is not None:
            tot[str(r.get(key))] += r["no_pnl"]
    if len(tot) <= top:
        return None
    best = sorted(tot, key=lambda g: (-tot[g], g))[:top]
    rest = [r for r in rows if r.get("no_pnl") is not None and str(r.get(key)) not in best]
    o = sum(r["no_outlay"] for r in rest)
    return {"removed": best, "n": len(rest), "roi": sum(r["no_pnl"] for r in rest) / o if o else None,
            "resid_B": float(np.mean([r["r_B"] for r in rest if r.get("r_B") is not None])) if rest else None}


def leave_one_out(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    groups = sorted({str(r.get(key)) for r in rows if r.get("no_pnl") is not None})
    vals = {}
    for g in groups:
        rest = [r for r in rows if r.get("no_pnl") is not None and str(r.get(key)) != g]
        o = sum(r["no_outlay"] for r in rest)
        vals[g] = sum(r["no_pnl"] for r in rest) / o if o else None
    v = np.array([x for x in vals.values() if x is not None])
    return {"n_groups": len(groups), "min": float(v.min()), "p10": float(np.quantile(v, 0.1)), "median": float(np.median(v)),
            "p90": float(np.quantile(v, 0.9)), "max": float(v.max()), "share_positive": float((v > 0).mean()),
            "min_without": min(vals, key=lambda k: vals[k]), "max_without": max(vals, key=lambda k: vals[k])}


def herfindahl(shares: Iterable[float]) -> float:
    s = np.asarray(list(shares), float)
    return float((s ** 2).sum()) if len(s) else 0.0


def concentration(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    rows = [r for r in rows if r.get("no_pnl") is not None]
    if not rows:
        return {"n": 0}
    tab = player_table(rows, key)
    tot = sum(d["pnl"] for d in tab)
    obs = Counter(str(r.get(key)) for r in rows)
    abs_tot = sum(abs(d["pnl"]) for d in tab)
    return {
        "n": len(rows), "groups": len(tab), "total_pnl": round(tot, 4),
        "without_top": {str(k): roi_without_top(rows, key, k) for k in (1, 3, 5, 10)},
        "leave_one_out": leave_one_out(rows, key),
        "top5_share_of_pnl": sum(d["pnl"] for d in tab[:5]) / tot if tot else None,
        "top5_share_of_obs": sum(d["n"] for d in tab[:5]) / len(rows),
        "herfindahl_obs": herfindahl(v / len(rows) for v in obs.values()),
        "herfindahl_abs_pnl": herfindahl(abs(d["pnl"]) / abs_tot for d in tab) if abs_tot else None,
        "table": tab,
    }


def case_study_selection(p1_rows: list[dict[str, Any]], k: int = 5) -> dict[str, list[str]]:
    """Protocol section 4: AFTER P1 is fixed, rank players by summed NO P/L; ties by more rows, then player id."""
    tab = player_table(p1_rows, "player_id")
    top = [d["player_id"] for d in tab[:k]]
    bottom = [d["player_id"] for d in sorted(tab, key=lambda d: (d["pnl"], -d["n"], d["player_id"]))[:k]]
    return {"top": top, "bottom": bottom}


# --------------------------------------------------------------------------- regression helper


def ols(y: list[float], X: list[list[float]]) -> dict[str, Any] | None:
    Y, M = np.asarray(y, float), np.asarray(X, float)
    if len(Y) < M.shape[1] + 2:
        return None
    M1 = np.column_stack([np.ones(len(Y)), M])
    beta, *_ = np.linalg.lstsq(M1, Y, rcond=None)
    return {"intercept": float(beta[0]), "coef": [float(b) for b in beta[1:]], "n": len(Y)}


def last_game_weight(rows: list[dict[str, Any]], target: str, l1: str = "last1", long: str = "long16") -> float | None:
    """Relative weight on last-game receptions: b_last / (b_last + b_long) in target ~ last1 + long16."""
    rs = [r for r in rows if r.get(target) is not None and r.get(l1) is not None and r.get(long) is not None]
    fit = ols([r[target] for r in rs], [[r[l1], r[long]] for r in rs])
    if not fit:
        return None
    b1, b2 = fit["coef"]
    return b1 / (b1 + b2) if (b1 + b2) != 0 else None
