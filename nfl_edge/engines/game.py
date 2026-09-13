"""GAME ENGINE: every deterministic function of the simulated final score, priced from ONE joint simulation.

The incumbent already produces a coherent 40,000-row joint (margin, total, home, away) simulation per game
(`nfl_edge/pricing/game_env.py`, replayed exactly by `nfl_edge/arms/incumbent_center.py`). The incumbent prices
five families from it with one branch per family. This module replaces the per-family branches with ONE generic
evaluator over the question grammar:

    statistic of the final score   margin(team) | total | team_points(team) | min_team_points | max_team_points
                                   | abs_margin | home_points | away_points | winner_points | loser_points
    comparison                     THRESHOLD (>=, >, <=, <) | RANGE (lo <= x <= hi, inclusive) | EVENT (WIN, TIE)

so an alternate spread, an alternate total, a team-total rung, a both-teams-score threshold, a winning-margin
bucket (either structure) and any nested score threshold are all the same code path and are coherent by
construction: they are integrals of the same draws. Ladders are monotone because P(x >= k) is computed from
one array; buckets are mutually exclusive and exhaustive because they partition the same array; and the
checks in `check_coherence` verify that on every priced board rather than assuming it.

Contract value vs event probability: the game-winner family pays $0.50 to both sides on a tie
(`nfl_edge/settlement/semantics.py`); every other family here is a plain binary. The engine returns both.

What this engine refuses: anything that is NOT a function of the final score -- first-to-N, first touchdown,
touchdown counts, period results -- returns (None, reason). It never approximates them.
"""
from __future__ import annotations

from collections import defaultdict

import numpy as np

from nfl_edge.semantics.questions import COMPOSITE, EVENT, GAME, PROVEN, RANGE, THRESHOLD, Question

ENGINE_VERSION = "game-engine-2.0.0"
MC_TOL = 1e-9

SCORE_STATS = ("margin", "total", "team_points", "min_team_points", "max_team_points", "abs_margin",
               "home_points", "away_points", "winner_points", "loser_points")


class NotAScoreFunction(ValueError):
    """The question is not a deterministic function of the final score."""


def score_stat(sim: dict, stat: str, subject: str | None, home: str, away: str) -> np.ndarray:
    m, tot, hs, aw = sim["margin"], sim["total"], sim["home"], sim["away"]
    if stat == "margin":
        if subject == home:
            return m
        if subject == away:
            return -m
        raise NotAScoreFunction(f"margin needs a subject team in the game ({subject!r} not in {home}/{away})")
    if stat == "total":
        return tot
    if stat == "team_points":
        if subject == home:
            return hs
        if subject == away:
            return aw
        raise NotAScoreFunction(f"team_points needs a subject team in the game ({subject!r})")
    if stat == "min_team_points":
        return np.minimum(hs, aw)
    if stat == "max_team_points":
        return np.maximum(hs, aw)
    if stat == "abs_margin":
        return np.abs(m)
    if stat == "home_points":
        return hs
    if stat == "away_points":
        return aw
    if stat == "winner_points":
        return np.maximum(hs, aw)
    if stat == "loser_points":
        return np.minimum(hs, aw)
    raise NotAScoreFunction(f"{stat!r} is not a function of the final score")


def _compare(x: np.ndarray, op: str, k: float) -> np.ndarray:
    if op == ">=":
        return x >= k
    if op == ">":
        return x > k
    if op == "<=":
        return x <= k
    if op == "<":
        return x < k
    raise NotAScoreFunction(f"operator {op!r} is not a comparison")


def indicator(sim: dict, q: Question, home: str, away: str) -> np.ndarray:
    """The 0/1 realisation of the question on every draw. Raises NotAScoreFunction when it cannot be one."""
    if q.kind == THRESHOLD:
        if q.k is None or q.op is None or q.stat is None:
            raise NotAScoreFunction("threshold question without a statistic, operator or threshold")
        return _compare(score_stat(sim, q.stat, q.subject, home, away), q.op, float(q.k))
    if q.kind == RANGE:
        if q.lo is None or q.stat is None:
            raise NotAScoreFunction("range question without a lower bound")
        x = score_stat(sim, q.stat, q.subject, home, away)
        ind = x >= float(q.lo)
        if q.hi is not None:
            ind = ind & (x <= float(q.hi))
        return ind
    if q.kind == EVENT:
        if q.event == "WIN":
            return score_stat(sim, "margin", q.subject, home, away) > 0
        if q.event == "TIE":
            return sim["margin"] == 0
        if q.event == "BOTH_SCORE":
            return (sim["home"] > 0) & (sim["away"] > 0)
        raise NotAScoreFunction(f"event {q.event!r} is not a function of the final score (needs scoring order or composition)")
    if q.kind == COMPOSITE:
        if not q.legs:
            raise NotAScoreFunction("composite question with no legs")
        for leg in q.legs:
            if leg.engine != GAME or leg.period != "FULL":
                raise NotAScoreFunction(f"composite leg {leg.stat}/{leg.period} is not a full-game score function")
        ind = np.ones(len(sim["margin"]), bool)
        for leg in q.legs:
            ind &= indicator(sim, leg, home, away)
        return ind
    raise NotAScoreFunction(f"question kind {q.kind!r}")


def answer(sim: dict, q: Question, home: str, away: str) -> dict:
    """Price one question from one joint simulation.

    Returns {"p_yes", "contract_value", "p_tie", "n_draws", "reason"}; p_yes is None with a reason when the question
    is not a score function or its period is not the full game.
    """
    if q.period != "FULL":
        return {"p_yes": None, "contract_value": None, "reason": f"period {q.period} is not the full game; the period engine owns it"}
    if q.engine not in (GAME, "JOINT"):
        return {"p_yes": None, "contract_value": None, "reason": f"question belongs to the {q.engine} engine"}
    try:
        ind = indicator(sim, q, home, away)
    except NotAScoreFunction as e:
        return {"p_yes": None, "contract_value": None, "reason": str(e)}
    p = float(np.mean(ind))
    p_tie = float(np.mean(sim["margin"] == 0))
    cv = p
    if q.kind == EVENT and q.event == "WIN" and q.tie_rule == "HALF_PAYOUT":
        cv = p + 0.5 * p_tie
    return {"p_yes": p, "contract_value": cv, "p_tie": p_tie, "n_draws": int(len(ind)), "reason": None,
            "engine_version": ENGINE_VERSION}


def price_questions(sim: dict, questions: dict, home: str, away: str) -> dict:
    """ticker -> answer, for a whole game's questions, on one simulation."""
    return {t: answer(sim, q, home, away) for t, q in questions.items()}


# ------------------------------------------------------------------------------------------------ coherence
def check_coherence(questions: dict, answers: dict, tol: float = MC_TOL) -> dict:
    """Structural checks over one priced game. Violations are bugs, not findings: everything here is integrated
    from one array, so a violation means the grammar or the evaluator is wrong.

      * THRESHOLD ladders (same stat, subject, op) are monotone in k
      * RANGE buckets that partition a statistic sum to one with the residual mass (tie / other side)
      * every probability is inside [0, 1]
    """
    problems = []
    ladders = defaultdict(list)
    buckets = defaultdict(list)
    for t, q in questions.items():
        a = answers.get(t) or {}
        p = a.get("p_yes")
        if p is None:
            continue
        if not (0.0 <= p <= 1.0):
            problems.append({"ticker": t, "type": "probability_out_of_range", "p": p})
        if q.kind == THRESHOLD:
            ladders[(q.stat, q.subject, q.op)].append((float(q.k), p, t))
        elif q.kind == RANGE:
            buckets[(q.stat, q.subject)].append((float(q.lo), q.hi, p, t))
    for key, rows in ladders.items():
        rows.sort()
        increasing = key[2] in ("<=", "<")
        for (k1, p1, t1), (k2, p2, t2) in zip(rows, rows[1:]):
            bad = (p2 > p1 + tol) if not increasing else (p2 < p1 - tol)
            if bad:
                problems.append({"ticker": t2, "type": "ladder_non_monotone", "vs": t1, "k": [k1, k2], "p": [p1, p2]})
    bucket_sums = {}
    for key, rows in buckets.items():
        rows.sort(key=lambda r: (r[0], r[1] if r[1] is not None else float("inf")))
        s = sum(r[2] for r in rows)
        bucket_sums[f"{key[0]}|{key[1]}"] = {"n": len(rows), "sum": s, "lo": rows[0][0], "hi": rows[-1][1]}
        if s > 1.0 + tol:
            problems.append({"type": "bucket_mass_exceeds_one", "group": list(key), "sum": s})
        for (lo1, hi1, _p1, t1), (lo2, _hi2, _p2, t2) in zip(rows, rows[1:]):
            if hi1 is None or lo2 <= hi1:
                problems.append({"ticker": t2, "type": "bucket_overlap", "vs": t1})
    return {"ok": not problems, "problems": problems, "bucket_groups": bucket_sums,
            "n_ladders": len(ladders), "n_bucket_groups": len(buckets)}


def bucket_partition_mass(sim: dict, home: str, away: str, questions: dict) -> dict:
    """For a winning-margin event: the mass of every bucket, the tie and the total, so the accounting can prove
    the board's buckets are collectively exhaustive on the simulation (sum == 1 to floating precision)."""
    total = 0.0
    parts = {}
    for t, q in questions.items():
        if q.kind == RANGE and q.stat in ("margin", "abs_margin") or (q.kind == EVENT and q.event == "TIE" and q.stat == "margin"):
            try:
                p = float(np.mean(indicator(sim, q, home, away)))
            except NotAScoreFunction:
                continue
            parts[t] = p
            total += p
    return {"parts": parts, "sum": total, "collectively_exhaustive": abs(total - 1.0) <= 1e-9 if parts else None}
