"""Thesis-conditioned fair value for the FULL-GAME contract families, from ONE coherent distribution.

A football thesis about a game ("PIT is better than the market has it by 1 to 2.5 points", "the total is 2 points too low")
is a statement about where the final margin and total are centred. This module turns such a statement into a probability for
every full-game contract that the statement bears on -- moneyline, every spread rung, every total rung, both teams' team totals,
winning-margin buckets and both-teams-score-N -- from the incumbent's own market-centred joint simulation
(`nfl_edge.pricing.game_env`: the market's implied margin and total, plus historical (margin, total) residual pairs with their
key-number mass, regulation-tie handling and overtime model). So the expressions of one thesis are priced consistently and
cannot contradict each other.

WHAT THIS IS, AND IS NOT
------------------------
* It is NOT a forecast. The centre is the market's; the SHIFT is the thesis, supplied as a RANGE by the analyst, never by a
  model. Nothing here knows who will win.
* The unshifted simulation is checked against the market's own ladder (`baseline_check`). Where it disagrees with the market's
  mid with no thesis at all, that gap is model noise, and it is carried into the fair-value range as an uncertainty buffer: an
  "edge" smaller than the engine's own disagreement with an unopinionated market is not an edge.
* Player props, period markets (1H/quarters), first-TD, race-to-N and one-off events are NOT derivable from a full-game margin
  and total. They return `None` with a reason and are priced only when the analyst supplies an explicit fair range.
* Determinism: the residual bank is seeded, every draw re-seeds it, and a shift re-uses the same seed, so the same inputs give
  the same numbers and two shifts are compared on common random numbers.
"""
from __future__ import annotations

import csv
import io
import math

import numpy as np

from nfl_edge.pricing.game_env import ResidualBank, simulate_game

FAIRVALUE_VERSION = "fairvalue-1.0.0"
BANK_SEASON_LO = 2016
BANK_HALFLIFE = 3.0
BANK_SEED = 11
DEFAULT_DRAWS = 60000

DERIVABLE = ("GAME_WINNER", "SPREAD", "TOTAL", "TEAM_TOTAL", "WIN_MARGIN_BUCKET", "BOTH_TEAMS_SCORE_N")


def bank_from_schedule(text: str, target_season: int) -> tuple:
    """The incumbent's residual bank (REG games, 2016+, with a result and both lines) from nflverse games.csv text."""
    marg, tot, seas, sl, tl, ot, res = [], [], [], [], [], [], []
    for r in csv.DictReader(io.StringIO(text)):
        try:
            if r.get("game_type") != "REG" or int(r["season"]) < BANK_SEASON_LO:
                continue
            result, spread, total, total_line = (float(r[k]) for k in ("result", "spread_line", "total", "total_line"))
        except (KeyError, TypeError, ValueError):
            continue
        marg.append(result - spread); tot.append(total - total_line); seas.append(float(r["season"]))
        sl.append(spread); tl.append(total_line); res.append(result)
        try:
            ot.append(int(float(r.get("overtime") or 0)))
        except ValueError:
            ot.append(0)
    if len(marg) < 500:
        raise ValueError(f"only {len(marg)} usable historical games in the schedule table; the residual bank needs a real history")
    bank = ResidualBank(marg, tot, seas, ref_season=target_season, spread_lines=sl, total_lines=tl, overtime=ot, results=res,
                        halflife=BANK_HALFLIFE, rng=np.random.default_rng(BANK_SEED))
    return bank, {"pairs": len(marg), "season_lo": int(min(seas)), "season_hi": int(max(seas)), "halflife_seasons": BANK_HALFLIFE,
                  "seed": BANK_SEED, "version": FAIRVALUE_VERSION}


class GameSim:
    """One game's market-centred simulation, re-drawn at a shifted centre on common random numbers."""

    def __init__(self, bank: ResidualBank, home: str, away: str, center_home_margin: float, center_total: float, draws: int = DEFAULT_DRAWS):
        self.bank, self.home, self.away = bank, home, away
        self.m0, self.t0, self.n = float(center_home_margin), float(center_total), int(draws)
        self._cache: dict = {}

    def draw(self, d_home_margin: float = 0.0, d_total: float = 0.0) -> dict:
        key = (round(float(d_home_margin), 4), round(float(d_total), 4))
        if key not in self._cache:
            self.bank.rng = np.random.default_rng(BANK_SEED + 1)          # common random numbers across shifts
            self._cache[key] = simulate_game(self.m0 + key[0], self.t0 + key[1], self.bank, n=self.n)
        return self._cache[key]


def contract_event(row: dict, sim: dict, home: str, away: str):
    """(boolean array over the draws on which the contract's YES pays, None) or (None, why not derivable)."""
    fam, period = row.get("family"), row.get("period")
    if period != "FULL":
        return None, f"{fam} {period}: a period market is not a function of the full-game margin and total"
    m, t, h, a = sim["margin"], sim["total"], sim["home"], sim["away"]
    subj, thr = row.get("subject"), row.get("threshold")

    def margin_for(team):
        return m if team == home else (-m if team == away else None)

    if fam == "GAME_WINNER":
        mm = margin_for(subj)
        return (mm > 0, None) if mm is not None else (None, "winner subject not one of the two teams (tie leg)")
    if fam == "SPREAD" and thr is not None:
        mm = margin_for(subj)
        return (mm > float(thr), None) if mm is not None else (None, "spread subject unresolved")
    if fam == "TOTAL" and thr is not None:
        return t >= float(thr), None
    if fam == "TEAM_TOTAL" and thr is not None:
        pts = h if subj == home else a if subj == away else None
        return (pts >= float(thr), None) if pts is not None else (None, "team-total subject unresolved")
    if fam == "BOTH_TEAMS_SCORE_N" and thr is not None:
        return np.minimum(h, a) >= float(thr), None
    if fam == "WIN_MARGIN_BUCKET":
        return None, "winning-margin bucket bounds are not carried on the row; not derived"
    return None, f"{fam}: not derivable from the full-game margin and total"


def contract_probability(row: dict, sim: dict, home: str, away: str):
    """(probability YES, reason) for a FULL-game analysis row on one simulated draw. (None, why) when not derivable."""
    ev, why = contract_event(row, sim, home, away)
    return (float(np.mean(ev)), None) if ev is not None else (None, why)


#: Script cells, defined exactly as the packet's Game Script v2 defines them (favourite-oriented margin; total against the centre).
SCRIPT_ONE_SCORE = 8.0
SCRIPT_TOTAL_BAND = 10.0
SCRIPT_LABELS = {"FAVORITE_CONTROL": "favourite controls", "COMPETITIVE": "competitive throughout", "UNDERDOG_CONTROL": "underdog outperforms",
                 "HIGH_SCORING": "high scoring", "NORMAL_SCORING": "normal scoring", "LOW_SCORING": "low scoring"}


def script_cells(sim: dict, home: str, away: str, centre_home_margin: float, centre_total: float) -> dict:
    """{cell id -> boolean mask} for the nine margin-state x scoring-state scripts, plus the favourite's code."""
    fav_is_home = centre_home_margin >= 0
    fav_margin = sim["margin"] if fav_is_home else -sim["margin"]
    marg = {"FAVORITE_CONTROL": fav_margin > SCRIPT_ONE_SCORE, "UNDERDOG_CONTROL": fav_margin < -SCRIPT_ONE_SCORE,
            "COMPETITIVE": np.abs(fav_margin) <= SCRIPT_ONE_SCORE}
    tot = {"HIGH_SCORING": sim["total"] >= centre_total + SCRIPT_TOTAL_BAND, "LOW_SCORING": sim["total"] <= centre_total - SCRIPT_TOTAL_BAND}
    tot["NORMAL_SCORING"] = ~(tot["HIGH_SCORING"] | tot["LOW_SCORING"])
    cells = {f"{mk}|{tk}": mv & tv for mk, mv in marg.items() for tk, tv in tot.items()}
    return {"cells": cells, "favorite": home if fav_is_home else away}


def script_matrix(event, sim: dict, home: str, away: str, centre_home_margin: float, centre_total: float) -> list:
    """For one contract's win event: P(script) and P(win | script) in each of the nine scripts, from the SAME draws."""
    sc = script_cells(sim, home, away, centre_home_margin, centre_total)
    out = []
    for cell, mask in sc["cells"].items():
        n = int(mask.sum())
        mk, tk = cell.split("|")
        out.append({"cell": cell, "label": f"{SCRIPT_LABELS[mk]} / {SCRIPT_LABELS[tk]}", "p_script": round(n / len(mask), 4),
                    "p_win_given_script": round(float(event[mask].mean()), 4) if n >= 200 else None,
                    "n_draws": n})
    return out


def baseline_check(rows: list, sim0: dict, home: str, away: str, *, lo: float = 0.05, hi: float = 0.95) -> dict:
    """How far the UNSHIFTED simulation sits from the market's own mid, by family: the engine's noise floor.

    Only executable, two-sided, non-extreme books count. The mid is the market's view, so a persistent signed gap here is the
    engine's bias, not information."""
    by: dict = {}
    for r in rows:
        if not r.get("executable") or r.get("mid") is None or not (lo <= float(r["mid"]) <= hi):
            continue
        p, why = contract_probability(r, sim0, home, away)
        if p is None:
            continue
        by.setdefault(r["family"], []).append(p - float(r["mid"]))
    out = {}
    for fam, d in by.items():
        d = np.asarray(d)
        out[fam] = {"n": int(len(d)), "mean_gap": round(float(d.mean()), 4), "rms_gap": round(float(np.sqrt((d ** 2).mean())), 4),
                    "p90_abs_gap": round(float(np.quantile(np.abs(d), 0.9)), 4)}
    return out


def fair_range(row: dict, gsim: GameSim, shift_margin: tuple, shift_total: tuple, noise: dict) -> dict:
    """The YES fair-probability range of a derivable contract for a thesis shift RANGE.

    `shift_margin`/`shift_total` are (low, high) shifts of the HOME margin and the total, in points. Probability is monotone in each
    shift for these families, so the range endpoints are probabilities at the shift extremes (all four corners are evaluated and the
    min/max taken, so a mis-signed assumption cannot hide a worse corner). The family's baseline noise (rms gap vs the market with
    no thesis) widens the range on both sides.
    """
    corners = []
    for dm in sorted(set(shift_margin)):
        for dt in sorted(set(shift_total)):
            p, why = contract_probability(row, gsim.draw(dm, dt), gsim.home, gsim.away)
            if p is None:
                return {"state": "NOT_DERIVABLE", "reason": why}
            corners.append(p)
    buf = max(0.01, float((noise.get(row["family"]) or {}).get("rms_gap", 0.02)))
    lo, hi = min(corners), max(corners)
    return {"state": "DERIVED", "p_low": round(max(0.0, lo - buf), 4), "p_high": round(min(1.0, hi + buf), 4),
            "p_central": round(float(np.mean(corners)), 4), "buffer": round(buf, 4),
            "shift_margin": list(shift_margin), "shift_total": list(shift_total), "basis": "MARKET_CENTRED_SIM_SHIFTED_BY_THESIS_RANGE"}
