"""SEASON ENGINE (foundation): schedule-level Monte Carlo for football-modelable season markets.

State: the remaining regular-season schedule; per-game home-win probabilities from a team-strength source
(default: the DATA_ONLY ratings margin through the historical margin residual; alternatively the market-implied
spread per game where a Kalshi game market exists). Each simulated season yields wins per team, division
winners, playoff qualifiers (7 per conference) and seeds under an APPROXIMATE tie-break (win percentage, then
head-to-head, then points differential proxy, then random) -- the official procedure is not fully reproduced,
which is why every seed / playoff question is LIKELY at best and the engine is shadow-only.

Questions answered from one set of simulated seasons: SEASON_WINS (>= K), SEASON_WINS_EXACT, TEAM_WINS_BY_WEEK,
MAKE_PLAYOFFS, DIVISION_WINNER, SEASON_SEED (approximate). Conference / Super Bowl winners need a playoff bracket
simulation on top (single-game win probabilities from the same strength source; neutral site for the final) and
are provided at LIKELY semantics with the bracket approximated.

News / speculation families (coach, retirement, next team) never enter this engine.
"""
from __future__ import annotations

import hashlib

import numpy as np

ENGINE_VERSION = "season-engine-1.0.0"
DIVISIONS = {
    "AFC_EAST": ["BUF", "MIA", "NE", "NYJ"], "AFC_NORTH": ["BAL", "CIN", "CLE", "PIT"], "AFC_SOUTH": ["HOU", "IND", "JAX", "TEN"],
    "AFC_WEST": ["DEN", "KC", "LAC", "LV"], "NFC_EAST": ["DAL", "NYG", "PHI", "WAS"], "NFC_NORTH": ["CHI", "DET", "GB", "MIN"],
    "NFC_SOUTH": ["ATL", "CAR", "NO", "TB"], "NFC_WEST": ["ARI", "LA", "SEA", "SF"],
}
TEAM_DIV = {t: d for d, ts in DIVISIONS.items() for t in ts}
CONF = {t: d.split("_")[0] for t, d in TEAM_DIV.items()}
MARGIN_SD = 13.0                # residual sd of the margin around a centre (docs/DRIFT.md: 12.7 pooled 2016-2025)
HOME_FIELD = 1.5                # points, applied when a rating source has no home term


def win_probability(margin_center: float, sd: float = MARGIN_SD) -> float:
    from math import erf, sqrt
    return 0.5 * (1.0 + erf(margin_center / (sd * sqrt(2.0))))


def simulate_seasons(schedule: list, played: dict, centers: dict, *, n: int = 20000, seed_key: str = "season", sd: float = MARGIN_SD) -> dict:
    """schedule: remaining games [{game_id, home, away, week}]; played: team -> (wins, losses, ties) so far;
    centers: game_id -> expected home margin (points). Returns per-simulation wins and derived events."""
    teams = sorted(TEAM_DIV)
    ti = {t: i for i, t in enumerate(teams)}
    rng = np.random.default_rng(int.from_bytes(hashlib.sha256(seed_key.encode()).digest()[:8], "big"))
    wins = np.zeros((n, len(teams))); ties = np.zeros((n, len(teams))); pd_ = np.zeros((n, len(teams)))
    for t, (w, l, tie) in played.items():
        if t in ti:
            wins[:, ti[t]] += w; ties[:, ti[t]] += tie
    wins_by_week = {}
    wins_initial = wins.copy()
    games = sorted(schedule, key=lambda g: (g.get("week") or 0, g["game_id"]))
    for g in games:
        h, a = g["home"], g["away"]
        if h not in ti or a not in ti:
            continue
        m = rng.normal(centers.get(g["game_id"], HOME_FIELD), sd, n)
        m = np.round(m)
        hw = m > 0; aw = m < 0; tie = m == 0
        wins[:, ti[h]] += hw; wins[:, ti[a]] += aw
        ties[:, ti[h]] += tie; ties[:, ti[a]] += tie
        pd_[:, ti[h]] += m; pd_[:, ti[a]] -= m
        wins_by_week[g.get("week")] = wins.copy()
    # division winners and playoff seeds with an approximate tie-break
    pct = wins + 0.5 * ties
    key = pct * 1000.0 + pd_ * 0.001 + rng.random(pct.shape) * 1e-6
    div_winner = np.zeros((n, len(teams)), bool)
    for d, ts in DIVISIONS.items():
        idx = [ti[t] for t in ts]
        best = np.argmax(key[:, idx], axis=1)
        for j, i in enumerate(idx):
            div_winner[:, i] = best == j
    playoffs = np.zeros((n, len(teams)), bool); seed = np.zeros((n, len(teams)), int)
    for conf in ("AFC", "NFC"):
        idx = [ti[t] for t in teams if CONF[t] == conf]
        k = key[:, idx].copy()
        dw = div_winner[:, idx]
        # division winners take seeds 1-4 by key; then the three best remaining
        k_dw = np.where(dw, k, -np.inf); k_wc = np.where(dw, -np.inf, k)
        order_dw = np.argsort(-k_dw, axis=1)[:, :4]
        order_wc = np.argsort(-k_wc, axis=1)[:, :3]
        for s in range(4):
            rows = np.arange(n); cols = order_dw[:, s]
            seed[rows, np.array(idx)[cols]] = s + 1; playoffs[rows, np.array(idx)[cols]] = True
        for s in range(3):
            rows = np.arange(n); cols = order_wc[:, s]
            seed[rows, np.array(idx)[cols]] = s + 5; playoffs[rows, np.array(idx)[cols]] = True
    return {"teams": teams, "wins": wins, "ties": ties, "div_winner": div_winner, "playoffs": playoffs, "seed": seed,
            "n": n, "engine_version": ENGINE_VERSION, "wins_by_week": wins_by_week, "wins_initial": wins_initial}


def answer(sim: dict, q) -> dict:
    ti = {t: i for i, t in enumerate(sim["teams"])}
    t = q.subject
    if t not in ti:
        return {"p_yes": None, "reason": f"team {t!r} unknown"}
    i = ti[t]
    if q.stat == "season_wins" and q.kind == "THRESHOLD":
        x = sim["wins"][:, i]
        p = float(np.mean({">=": x >= q.k, ">": x > q.k, "<=": x <= q.k, "<": x < q.k}[q.op]))
    elif q.stat == "wins_through_week" and q.kind == "THRESHOLD":
        note = next((n for n in (q.notes or ()) if str(n).startswith("through_week=")), None)
        try:
            wk = int(str(note).split("=")[1])
        except (TypeError, ValueError, IndexError):
            return {"p_yes": None, "reason": "week not carried on the question"}
        W = sim.get("wins_by_week") or {}
        if wk in W:
            x = W[wk][:, i]
        elif W and wk < min(W):
            x = sim["wins_initial"][:, i]                      # every game through that week is already played
        elif W and wk > max(W):
            x = sim["wins"][:, i]
        else:
            return {"p_yes": None, "reason": f"week {wk} outside the simulated schedule"}
        p = float(np.mean({">=": x >= q.k, ">": x > q.k, "<=": x <= q.k, "<": x < q.k}[q.op]))
    elif q.stat == "season_wins" and q.event == "EXACT_WINS":
        p = float(np.mean(sim["wins"][:, i] == q.k))
    elif q.event == "MAKE_PLAYOFFS":
        p = float(np.mean(sim["playoffs"][:, i]))
    elif q.event == "DIVISION_WINNER":
        p = float(np.mean(sim["div_winner"][:, i]))
    elif q.event == "SEED":
        return {"p_yes": None, "reason": "seed number not carried on the question (AMBIGUOUS grammar)"}
    else:
        return {"p_yes": None, "reason": f"season question {q.stat}/{q.event} not answered by this engine"}
    return {"p_yes": p, "contract_value": p, "n_draws": int(sim["n"]), "engine_version": ENGINE_VERSION, "reason": None}
