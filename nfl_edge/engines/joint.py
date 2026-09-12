"""JOINT / CORRELATION ENGINE: composite contracts mapped to shared simulations, or JOINT_MODEL_REQUIRED.

A pre-packaged parlay or a half/full double result is a COMPOSITE question (`nfl_edge/semantics/questions.py`).
Marginal probabilities are never multiplied: the legs of one game are dependent. The only way this engine prices
a composite is by evaluating every leg on the SAME draws of one simulation:

    every leg a full-game score function      -> the game engine's joint simulation (indicator AND across draws)
    every leg a period / full-game score fn   -> the period engine's joint quarter simulation (it carries the full
                                                 game as the sum of its quarters plus overtime)
    any leg a player / season / other question -> JOINT_MODEL_REQUIRED (the future coupled simulation of game
                                                 environment, team scoring, QB state, player opportunity and
                                                 production is architected in docs/SHADOW_V2.md and not built here)

Composite contracts priced here are SHADOW only.
"""
from __future__ import annotations

from nfl_edge.engines import game as GE, period as PE
from nfl_edge.semantics.questions import COMPOSITE, GAME, PERIOD, Question

ENGINE_VERSION = "joint-engine-1.0.0"
JOINT_MODEL_REQUIRED = "JOINT_MODEL_REQUIRED"


def classify_legs(q: Question) -> dict:
    if q.kind != COMPOSITE or not q.legs:
        return {"route": None, "reason": "not a composite question"}
    engines = {l.engine for l in q.legs}
    periods = {l.period for l in q.legs}
    if engines <= {GAME} and periods <= {"FULL"}:
        return {"route": "game", "reason": "every leg is a full-game score function"}
    if engines <= {GAME, PERIOD} and periods <= set(PE.PERIOD_QUARTERS):
        return {"route": "period", "reason": "legs are period / full-game score functions; the quarter simulation carries both"}
    return {"route": JOINT_MODEL_REQUIRED, "reason": f"legs span engines {sorted(engines)}; dependence between them is not modelled",
            "legs": [{"engine": l.engine, "stat": l.stat, "period": l.period, "subject": l.subject} for l in q.legs]}


def answer(q: Question, *, game_sim: dict | None, period_sim: dict | None, home: str, away: str) -> dict:
    route = classify_legs(q)
    if route["route"] == "game":
        if game_sim is None:
            return {"p_yes": None, "contract_value": None, "reason": "no game simulation", "route": route}
        a = GE.answer(game_sim, q, home, away)
        a["route"] = route; a["engine_version"] = ENGINE_VERSION
        return a
    if route["route"] == "period":
        if period_sim is None:
            return {"p_yes": None, "contract_value": None, "reason": "no period simulation", "route": route}
        a = PE.answer(period_sim, q, home, away)
        a["route"] = route; a["engine_version"] = ENGINE_VERSION
        return a
    return {"p_yes": None, "contract_value": None, "reason": route["reason"], "route": route, "status": JOINT_MODEL_REQUIRED}


def independence_product(q: Question, marginals: dict) -> dict:
    """The product of marginals, computed ONLY as a diagnostic against the joint answer -- never returned as a price."""
    ps = [marginals.get(i) for i in range(len(q.legs))]
    if any(p is None for p in ps):
        return {"product": None}
    prod = 1.0
    for p in ps:
        prod *= p
    return {"product": prod, "note": "diagnostic only: assumes independence, which the legs violate"}
