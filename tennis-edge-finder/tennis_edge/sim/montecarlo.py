"""Point-by-point Monte Carlo match simulator.

Used for (1) validating the exact engine in tennis_edge.sim.analytic and (2) path-dependent
quantities the DP does not track (e.g. "A wins set 1 AND loses the match", in-match states).
Vectorised over simulations with numpy; a bo3 match at 200k paths takes a few seconds.

Every simulation returns arrays: winner (1 if A), sets per player, games per player per set,
tiebreaks played, and the set-by-set score matrix. Monte Carlo standard error is reported by
`summarize` so nobody mistakes simulation noise for signal.
"""
from __future__ import annotations

import numpy as np

from tennis_edge.rules.formats import MatchFormat, TOUR_SINGLES_BO3


def _sim_games(rng, n, p_point, no_ad):
    """Simulate n independent games where the server wins each point with prob p_point[n]. Returns bool array: server won."""
    a = np.zeros(n, dtype=np.int16)
    b = np.zeros(n, dtype=np.int16)
    done = np.zeros(n, dtype=bool)
    won = np.zeros(n, dtype=bool)
    # bound loop: cap at 200 points; the deuce tail beyond that has negligible mass (p^100)
    for _ in range(400):
        active = ~done
        if not active.any():
            break
        r = rng.random(n) < p_point
        a[active & r] += 1
        b[active & ~r] += 1
        if no_ad:
            w = (a >= 4)
            l = (b >= 4)
        else:
            w = (a >= 4) & (a - b >= 2)
            l = (b >= 4) & (b - a >= 2)
        newly = active & (w | l)
        won[newly & w] = True
        done |= newly
    return won


def _sim_tiebreak(rng, n, pa, pb, a_first, to):
    a = np.zeros(n, dtype=np.int16)
    b = np.zeros(n, dtype=np.int16)
    done = np.zeros(n, dtype=bool)
    won = np.zeros(n, dtype=bool)
    for k in range(600):
        active = ~done
        if not active.any():
            break
        first = (k == 0) or (((k + 1) // 2) % 2 == 0)
        a_serving = np.where(a_first, first, not first)
        p = np.where(a_serving, pa, pb)
        r = rng.random(n) < p
        a[active & r] += 1
        b[active & ~r] += 1
        w = (a >= to) & (a - b >= 2)
        l = (b >= to) & (b - a >= 2)
        newly = active & (w | l)
        won[newly & w] = True
        done |= newly
    return won


def simulate(pa: float, pb: float, fmt: MatchFormat = TOUR_SINGLES_BO3, n: int = 100_000, seed: int = 0,
             a_serves_first: bool | None = None):
    rng = np.random.default_rng(seed)
    n_win = fmt.sets_to_win
    fs_at, fs_to = fmt.final_set_rule()
    sets_a = np.zeros(n, dtype=np.int16)
    sets_b = np.zeros(n, dtype=np.int16)
    games_a = np.zeros((n, fmt.best_of), dtype=np.int16)
    games_b = np.zeros((n, fmt.best_of), dtype=np.int16)
    tiebreaks = np.zeros(n, dtype=np.int16)
    if a_serves_first is None:
        a_first = rng.random(n) < 0.5
    else:
        a_first = np.full(n, bool(a_serves_first))
    match_done = np.zeros(n, dtype=bool)
    for s in range(fmt.best_of):
        is_final = (s == fmt.best_of - 1)
        active_set = ~match_done
        if not active_set.any():
            break
        if is_final and fmt.final_set == "MATCH_TB10":
            w = _sim_tiebreak(rng, n, pa, pb, a_first, 10)
            games_a[active_set & w, s] = 1
            games_b[active_set & ~w, s] = 1
            tiebreaks[active_set] += 1
            sets_a[active_set & w] += 1
            sets_b[active_set & ~w] += 1
            match_done |= active_set
            break
        tb_at = fs_at if is_final else fmt.tiebreak_at
        tb_to = fs_to if is_final else fmt.tiebreak_to
        ga = np.zeros(n, dtype=np.int16)
        gb = np.zeros(n, dtype=np.int16)
        set_done = ~active_set
        for g in range(400):
            live = ~set_done
            if not live.any():
                break
            a_serving = np.where(a_first, g % 2 == 0, g % 2 == 1)
            if tb_at is not None:
                tb_now = live & (ga == tb_at) & (gb == tb_at)
                if tb_now.any():
                    w = _sim_tiebreak(rng, n, pa, pb, a_serving, tb_to)
                    ga[tb_now & w] += 1
                    gb[tb_now & ~w] += 1
                    tiebreaks[tb_now] += 1
                    set_done |= tb_now
                    live = ~set_done
            p_server = np.where(a_serving, pa, 1.0 - pb)  # server's point-win prob
            server_won = _sim_games(rng, n, p_server, fmt.no_ad)
            a_won_game = np.where(a_serving, server_won, ~server_won)
            ga[live & a_won_game] += 1
            gb[live & ~a_won_game] += 1
            fin = live & (((ga >= 6) & (ga - gb >= 2)) | ((gb >= 6) & (gb - ga >= 2)))
            set_done |= fin
        games_a[active_set, s] = ga[active_set]
        games_b[active_set, s] = gb[active_set]
        a_won_set = ga > gb
        sets_a[active_set & a_won_set] += 1
        sets_b[active_set & ~a_won_set] += 1
        # next set first server flips iff odd number of games
        odd = ((ga + gb) % 2 == 1)
        a_first = np.where(active_set & odd, ~a_first, a_first)
        match_done |= (sets_a == n_win) | (sets_b == n_win)
    return {"winner_a": sets_a > sets_b, "sets_a": sets_a, "sets_b": sets_b, "games_a": games_a, "games_b": games_b,
            "tiebreaks": tiebreaks, "n": n}


def summarize(sim: dict) -> dict:
    n = sim["n"]
    w = sim["winner_a"].mean()
    tg = sim["games_a"].sum(1) + sim["games_b"].sum(1)
    diff = sim["games_a"].sum(1) - sim["games_b"].sum(1)
    ss = {}
    for a, b in zip(sim["sets_a"], sim["sets_b"]):
        ss[(int(a), int(b))] = ss.get((int(a), int(b)), 0) + 1
    return {"p_match": float(w), "se_p_match": float(np.sqrt(w * (1 - w) / n)),
            "set_score": {k: v / n for k, v in ss.items()},
            "total_games_mean": float(tg.mean()), "total_games": {int(k): float(v) / n for k, v in zip(*np.unique(tg, return_counts=True))},
            "game_diff": {int(k): float(v) / n for k, v in zip(*np.unique(diff, return_counts=True))},
            "tiebreaks": {int(k): float(v) / n for k, v in zip(*np.unique(sim["tiebreaks"], return_counts=True))},
            "set1_a": float(np.mean(sim["games_a"][:, 0] > sim["games_b"][:, 0]))}
