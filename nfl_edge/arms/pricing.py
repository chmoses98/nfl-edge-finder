"""Price one game contract from one arm's joint simulation, with the incumbent's semantics.

This is a challenger-side copy of the game-family branches in `scripts/shadow/price_slate.py`, kept separate so
the incumbent is never refactored for the experiment's convenience. `tests/test_three_arm_pricing.py` holds
the two to the same answers on a shared simulation.
"""
from __future__ import annotations

import numpy as np

from nfl_edge.settlement import semantics as sem_mod


def price_contract(sim: dict, q: dict, home: str, away: str):
    """Returns (event_probability, contract_value, reason). Probabilities are None when the contract is not
    one this simulation can price; the reason says why."""
    fam, period = q.get("family"), q.get("period")
    m, tot, hs, aw = sim["margin"], sim["total"], sim["home"], sim["away"]
    if fam == "GAME_WINNER":
        team = q.get("team")
        if team not in (home, away):
            return None, None, "game-winner leg carries no team (tie leg)"
        p_win = float(np.mean(m > 0)) if team == home else float(np.mean(m < 0))
        cv = sem_mod.game_winner_contract_value(p_win, float(np.mean(m == 0)))
        return cv.event_probability, cv.contract_value, None
    if fam == "SPREAD" and period == "FULL":
        if q.get("floor_strike") is None or q.get("team") not in (home, away):
            return None, None, "spread contract without a floor strike or team"
        x = m if q.get("team") == home else -m
        p = float(np.mean(x > float(q["floor_strike"])))
        return p, p, None
    if fam == "TOTAL" and period == "FULL":
        if q.get("threshold") is None:
            return None, None, "total contract without a threshold"
        p = float(np.mean(tot >= float(q["threshold"])))
        return p, p, None
    if fam == "TEAM_TOTAL" and period == "FULL":
        if q.get("threshold") is None or q.get("team") not in (home, away):
            return None, None, "team-total contract without a threshold or team"
        x = hs if q.get("team") == home else aw
        p = float(np.mean(x >= float(q["threshold"])))
        return p, p, None
    if fam == "BOTH_TEAMS_SCORE_N":
        if q.get("threshold") is None:
            return None, None, "both-teams-score contract without a threshold"
        k = float(q["threshold"])
        p = float(np.mean((hs >= k) & (aw >= k)))
        return p, p, None
    return None, None, f"family {fam} period {period} is not priced from the joint game simulation"
