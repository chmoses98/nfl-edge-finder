"""A validated lattice distribution: the single object every player ladder is derived from.

`LatticeDistribution` is a pmf on the integers 0..N. Its survival function S(k) = P(Y >= k) prices every
"K+" rung; range questions and quantiles come from the same pmf; the mean, variance, zero mass and upper tail
are readable so a chosen family can be checked against what it must reproduce. Validity (non-negative, sums to
one, survival monotone) is checked at construction and again by `check_valid`, so an invalid distribution
cannot reach a projection record.
"""
from __future__ import annotations

import numpy as np

TOL = 1e-9


class InvalidDistribution(ValueError):
    pass


class LatticeDistribution:
    __slots__ = ("pmf", "grid", "meta")

    def __init__(self, pmf, grid=None, meta: dict | None = None, normalize: bool = False):
        p = np.asarray(pmf, float)
        if p.ndim != 1 or len(p) == 0:
            raise InvalidDistribution("pmf must be a non-empty 1-d array")
        if np.any(~np.isfinite(p)):
            raise InvalidDistribution("pmf carries non-finite mass")
        if np.any(p < -TOL):
            raise InvalidDistribution(f"negative density at {int(np.argmin(p))}: {p.min()}")
        p = np.clip(p, 0.0, None)
        s = p.sum()
        if normalize:
            if s <= 0:
                raise InvalidDistribution("pmf sums to zero")
            p = p / s
        elif abs(s - 1.0) > 1e-6:
            raise InvalidDistribution(f"pmf sums to {s}, not 1")
        self.pmf = p
        self.grid = np.arange(len(p)) if grid is None else np.asarray(grid)
        self.meta = dict(meta or {})

    # ---------------------------------------------------------------- constructors
    @classmethod
    def from_cdf(cls, cdf, meta=None):
        F = np.asarray(cdf, float)
        F = np.clip(F, 0.0, 1.0)
        F = np.maximum.accumulate(F)
        pmf = np.diff(np.concatenate([[0.0], F]))
        pmf[-1] += max(0.0, 1.0 - F[-1])              # mass above the grid is folded into the last cell
        return cls(pmf, meta=meta, normalize=True)

    @classmethod
    def from_survival(cls, S, meta=None):
        """S[k] = P(Y >= k) on the integer grid 0..N (S[0] = 1)."""
        S = np.clip(np.asarray(S, float), 0.0, 1.0)
        S = np.minimum.accumulate(S)
        F = 1.0 - np.concatenate([S[1:], [0.0]])
        return cls.from_cdf(F, meta)

    @classmethod
    def from_samples(cls, x, n_max: int, meta=None):
        x = np.clip(np.round(np.asarray(x, float)), 0, n_max).astype(int)
        pmf = np.bincount(x, minlength=n_max + 1).astype(float)
        return cls(pmf, meta=meta, normalize=True)

    # ---------------------------------------------------------------- queries
    @property
    def n(self):
        return len(self.pmf) - 1

    def cdf(self):
        return np.cumsum(self.pmf)

    def survival_curve(self):
        """S[k] = P(Y >= k) for k on the grid."""
        return 1.0 - np.concatenate([[0.0], np.cumsum(self.pmf)[:-1]])

    def survival(self, k: float) -> float:
        """P(Y >= k) for any real k (integer outcomes)."""
        kk = int(np.ceil(k - 1e-12))
        if kk <= 0:
            return 1.0
        if kk > self.n:
            return 0.0
        return float(self.pmf[kk:].sum())

    def prob_greater(self, floor: float) -> float:
        return self.survival(np.floor(floor) + 1)

    def range_prob(self, lo: float, hi: float | None) -> float:
        lo_i = max(0, int(np.ceil(lo - 1e-12)))
        if hi is None:
            return float(self.pmf[lo_i:].sum()) if lo_i <= self.n else 0.0
        hi_i = min(self.n, int(np.floor(hi + 1e-12)))
        return float(self.pmf[lo_i:hi_i + 1].sum()) if hi_i >= lo_i else 0.0

    def ladder(self, ks) -> dict:
        return {float(k): self.survival(k) for k in ks}

    def mean(self) -> float:
        return float((self.grid * self.pmf).sum())

    def var(self) -> float:
        m = self.mean()
        return float(((self.grid - m) ** 2 * self.pmf).sum())

    def p_zero(self) -> float:
        return float(self.pmf[0])

    def quantile(self, p: float) -> float:
        F = self.cdf()
        return float(self.grid[min(int(np.searchsorted(F, p - 1e-12, side="left")), self.n)])

    def summary(self) -> dict:
        return {"mean": self.mean(), "sd": float(np.sqrt(self.var())), "p_zero": self.p_zero(),
                "p05": self.quantile(0.05), "p25": self.quantile(0.25), "p50": self.quantile(0.5), "p75": self.quantile(0.75),
                "p95": self.quantile(0.95), "n_max": int(self.n)}

    def check_valid(self) -> tuple[bool, str | None]:
        if np.any(self.pmf < 0):
            return False, "negative density"
        if abs(self.pmf.sum() - 1.0) > 1e-6:
            return False, "does not sum to one"
        S = self.survival_curve()
        if np.any(np.diff(S) > TOL):
            return False, "survival not monotone"
        return True, None

    # ---------------------------------------------------------------- transforms
    def shifted_to_mean(self, target_mean: float, method: str = "scale") -> "LatticeDistribution":
        """Re-locate the distribution so its mean equals `target_mean`, keeping its SHAPE.

        `scale` stretches the support (Y -> Y * c), which keeps the coefficient of variation and the zero mass:
        the right transform for yardage-like stats. Integer mass is redistributed by linear interpolation of the
        CDF on the new support.
        """
        m = self.mean()
        if m <= 1e-9 or target_mean <= 1e-9:
            return LatticeDistribution(self.pmf.copy(), meta={**self.meta, "shift": "none"})
        c = target_mean / m
        F = self.cdf()
        x_new = self.grid * c
        F_new = np.interp(self.grid + 0.5, np.concatenate([[-0.5 * c], x_new + 0.5 * c]), np.concatenate([[0.0], F]), left=0.0, right=1.0)
        out = LatticeDistribution.from_cdf(F_new, meta={**self.meta, "shift": f"scale x{c:.4f}"})
        return out

    def mixture(self, other: "LatticeDistribution", w_self: float) -> "LatticeDistribution":
        n = max(self.n, other.n)
        a = np.zeros(n + 1); b = np.zeros(n + 1)
        a[: self.n + 1] = self.pmf; b[: other.n + 1] = other.pmf
        return LatticeDistribution(w_self * a + (1.0 - w_self) * b, meta={"mixture": w_self}, normalize=True)

    def to_dict(self, ladder_ks=None) -> dict:
        d = self.summary()
        if ladder_ks is not None:
            d["ladder"] = {str(k): round(v, 6) for k, v in self.ladder(ladder_ks).items()}
        return d
