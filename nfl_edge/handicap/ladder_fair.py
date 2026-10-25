"""Fair value for ANY monotone contract ladder -- player stats, period markets, alternate lines -- from the market's own ladder and an analyst shift.

The full-game families (`fairvalue.py`) are priced from a joint margin/total simulation. Player statistics and period markets have no such
engine here (and the research arms that do project them are not validated), but they share a structure the market itself supplies: a LADDER of
thresholds whose prices trace a survival curve S(k) = P(X >= k). A football thesis about such a quantity is a statement that X is larger or
smaller than the market has it by some amount -- "this back's receptions are 0.4 to 1.0 below the market's", "this passer's attempts are 2 to 5
above". That is exactly a SHIFT of the curve:

    P(X + d >= k) = S(k - d)

so every rung of the ladder, on both sides (YES = the over, NO = the under), gets a fair-probability RANGE from the shift range [d_lo, d_hi], on one
footing and consistent across rungs (alternate lines cannot contradict each other).

WHAT THIS IS, AND IS NOT
------------------------
* The CENTRE is the market's (isotonic-fitted mids of two-sided, traded, not-too-wide books). The SHIFT is the analyst's, as a range with a named basis
  and cited evidence. Nothing here estimates it; no research model supplies it.
* The range is widened by a stated uncertainty buffer (constants below; larger for player statistics, whose rungs are sparse and whose outcomes
  are more dispersed than the market's smoothing suggests). The buffer is not fitted to this data; it exists so that a small shift cannot clear a fee.
* A rung whose shifted position falls outside the ladder's priced range is NOT derivable (no tail extrapolation) and says so.
* Piecewise-linear interpolation between rungs approximates the curve between them (25-yard passing rungs are the coarsest); that error is inside
  the buffer for ladders with up to 25-unit spacing and is why wide spacing is disclosed on the evaluation.
"""
from __future__ import annotations

import math

import numpy as np

LADDER_VERSION = "ladder-fair-1.0.0"

#: Minimum uncertainty added to each side of a derived range, by what the ladder measures. Constants, stated, not fitted.
BUFFER_PLAYER = 0.030
BUFFER_PERIOD = 0.025
BUFFER_OTHER = 0.020
MAX_BUILD_WIDTH = 0.10        # a rung wider than this is not used to build the curve
MIN_RUNGS = 3


def buffer_for(row: dict) -> float:
    if row.get("family") == "PLAYER_STAT":
        return BUFFER_PLAYER
    if row.get("period") not in (None, "FULL"):
        return BUFFER_PERIOD
    return BUFFER_OTHER


def ladder_key(row: dict) -> tuple:
    return (row.get("family"), row.get("period") or "FULL", row.get("subject"), row.get("stat"), row.get("operator"))


def _usable(r: dict) -> bool:
    return (r.get("threshold") is not None and r.get("mid") is not None and not r.get("no_real_market") and r.get("executable") is not False
            and (r.get("width") is None or float(r["width"]) <= MAX_BUILD_WIDTH) and 0.0 < float(r["mid"]) < 1.0)


def _pav_desc(y: np.ndarray) -> np.ndarray:
    """Non-increasing isotonic fit (pool adjacent violators), unit weights."""
    blocks = [[float(v), 1.0, 1] for v in y]
    i = 0
    while i < len(blocks) - 1:
        if blocks[i][0] < blocks[i + 1][0] - 1e-12:
            m1, w1, n1 = blocks[i]
            m2, w2, n2 = blocks[i + 1]
            blocks[i:i + 2] = [[(m1 * w1 + m2 * w2) / (w1 + w2), w1 + w2, n1 + n2]]
            i = max(i - 1, 0)
        else:
            i += 1
    out = []
    for m, _w, n in blocks:
        out.extend([m] * n)
    return np.clip(np.asarray(out, float), 0.0, 1.0)


class Ladder:
    """One quantity's survival curve S(k)=P(YES-event at threshold k), built from its rungs' mids."""

    def __init__(self, rows: list):
        use = sorted((r for r in rows if _usable(r)), key=lambda r: float(r["threshold"]))
        self.ks = np.array([float(r["threshold"]) for r in use])
        raw = np.array([float(r["mid"]) for r in use])
        self.s = _pav_desc(raw) if len(use) else raw
        self.n = len(use)
        self.operator = rows[0].get("operator") if rows else None
        self.spacing = float(np.median(np.diff(self.ks))) if len(self.ks) > 1 else None

    @property
    def ok(self) -> bool:
        return self.n >= MIN_RUNGS

    def at(self, k: float):
        """S(k) by linear interpolation, or None outside the priced range."""
        if not self.ok or k < self.ks[0] - 1e-9 or k > self.ks[-1] + 1e-9:
            return None
        return float(np.interp(k, self.ks, self.s))

    def median(self):
        """The threshold where S crosses 0.5 (interpolated); None if the ladder does not bracket it."""
        if not self.ok or self.s[0] < 0.5 or self.s[-1] > 0.5:
            return None
        return float(np.interp(0.5, self.s[::-1], self.ks[::-1]))


def build_ladders(rows: list) -> dict:
    groups: dict = {}
    for r in rows:
        if r.get("threshold") is None or r.get("operator") not in (">=", ">"):
            continue
        groups.setdefault(ladder_key(r), []).append(r)
    return {k: Ladder(v) for k, v in groups.items()}


def fair_range_for_row(row: dict, ladder: Ladder, shift: tuple, buffer: float | None = None) -> dict:
    """YES fair-probability range for one rung under a shift RANGE (units of the quantity; positive = larger than the market has it)."""
    if not ladder.ok:
        return {"state": "NOT_DERIVABLE", "reason": f"only {ladder.n} usable rung(s) on this ladder (need {MIN_RUNGS}); no curve to shift"}
    thr = float(row["threshold"])
    vals = []
    for d in sorted(set(float(x) for x in shift)):
        s = ladder.at(thr - d)
        if s is None:
            return {"state": "NOT_DERIVABLE", "reason": f"threshold {thr:g} shifted by {d:+g} falls outside the priced range "
                                                         f"[{ladder.ks[0]:g}, {ladder.ks[-1]:g}]; the tail is not extrapolated"}
        vals.append(s)
    buf = buffer_for(row) if buffer is None else buffer
    lo, hi = min(vals), max(vals)
    return {"state": "DERIVED", "p_low": round(max(0.0, lo - buf), 4), "p_high": round(min(1.0, hi + buf), 4), "p_central": round(float(np.mean(vals)), 4),
            "buffer": buf, "shift": list(shift), "ladder_rungs": ladder.n, "ladder_spacing": ladder.spacing,
            "basis": "MARKET_LADDER_SHIFTED_BY_ANALYST_RANGE"}


def select(rows: list, selector: dict) -> list:
    """Rows matching an analyst selector: {family, period (default FULL), subject (player name or team), stat}. Unspecified keys match anything."""
    out = []
    for r in rows:
        if r.get("family") != selector.get("family"):
            continue
        if (r.get("period") or "FULL") != selector.get("period", "FULL"):
            continue
        if selector.get("subject") is not None and r.get("subject") != selector["subject"]:
            continue
        if selector.get("stat") is not None and r.get("stat") != selector["stat"]:
            continue
        if selector.get("subject_kind") and r.get("subject_kind") != selector["subject_kind"]:
            continue
        out.append(r)
    return out


def script_summary(script_results: dict | None) -> dict:
    """Turn the analyst's per-margin-state result (WIN / MIXED / LOSE for FAVORITE_CONTROL, COMPETITIVE, UNDERDOG_CONTROL) into the script fields the
    challenge and the stake ladder read. Three scoring variants sit inside each margin state, so a WIN state covers three of the nine scripts."""
    if not script_results:
        return {"basis": "NONE", "declared": None, "matrix": [], "winning_scripts": 0, "major_scripts": 9, "single_script_dependent": None, "script_neutral": False}
    states = ("FAVORITE_CONTROL", "COMPETITIVE", "UNDERDOG_CONTROL")
    res = {s: str(script_results.get(s, "LOSE")).upper() for s in states}
    wins = [s for s, v in res.items() if v == "WIN"]
    mixed = [s for s, v in res.items() if v == "MIXED"]
    winning = 3 * len(wins) + len(mixed)
    single = (len(wins) + len(mixed)) == 1
    share = (round(1.0 / len(wins), 3) if wins else (1.0 if mixed else None))
    return {"basis": "ANALYST_DECLARED", "declared": res, "matrix": [], "winning_scripts": winning, "major_scripts": 9,
            "single_script_dependent": single, "max_script_share_of_wins": share, "script_neutral": False}
