"""Exact (dynamic-programming) tennis match probabilities from point-win probabilities.

Inputs are the two structural quantities every model in this project ultimately produces:

    pa = P(player A wins a point when A serves)
    pb = P(player A wins a point when B serves)        (so B's serve-point win prob is 1 - pb)

Everything else -- game, tiebreak, set, match, and the full distributions over set scores, total
games, game differential, tiebreak counts -- is computed EXACTLY by recursion under a MatchFormat.
Monte Carlo (tennis_edge.sim.montecarlo) is used only for path-dependent quantities and to validate
this module; tests assert agreement.

Modelling assumptions (documented, testable):
  * points are i.i.d. given the server (the classic O'Malley / Barnett-Clarke setup);
  * the serve alternates by game, and inside a tiebreak by the 1-2-2-2... pattern, so any pair of
    consecutive tiebreak points starting at an even index is one point on each serve;
  * the player who received in the last game of a set serves first in the next set (equivalently:
    next-set first server = the set's first server iff the set had an even number of games, counting
    a tiebreak as one game);
  * the next set after a set is served first by the player who did NOT serve the tiebreak's first point.

All distributions are returned as plain dicts / numpy arrays keyed from player A's perspective.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from tennis_edge.rules.formats import MatchFormat, TOUR_SINGLES_BO3

_EPS = 1e-12


def _clip(p: float) -> float:
    return min(max(float(p), _EPS), 1.0 - _EPS)


# ----------------------------------------------------------------------------- game
def game_win_prob(p: float, no_ad: bool = False) -> float:
    """P(server wins a game | server wins each point with prob p)."""
    p = _clip(p)
    q = 1.0 - p
    if no_ad:
        # first to 4 points; at 3-3 one deciding point. P = sum_{k=0..2} C(3+k,k) p^4 q^k + C(6,3) p^3 q^3 * p
        return p ** 4 * (1 + 4 * q + 10 * q ** 2) + 20 * p ** 3 * q ** 3 * p
    # standard: win 4-0,4-1,4-2 directly, or reach deuce (3-3) then p^2/(p^2+q^2)
    deuce = p * p / (p * p + q * q)
    return p ** 4 * (1 + 4 * q + 10 * q ** 2) + 20 * p ** 3 * q ** 3 * deuce


# ----------------------------------------------------------------------------- tiebreak
def tiebreak_win_prob(pa: float, pb: float, to: int = 7, a_serves_first: bool = True) -> float:
    """P(A wins a tiebreak to `to` points, win by 2). pa/pb as in the module docstring."""
    pa, pb = _clip(pa), _clip(pb)
    # from any tie at or beyond (to-1, to-1) the next two points are one on each serve
    tie = pa * pb / (pa * pb + (1 - pa) * (1 - pb))

    @lru_cache(maxsize=None)
    def rec(a: int, b: int) -> float:
        if a >= to and a - b >= 2:
            return 1.0
        if b >= to and b - a >= 2:
            return 0.0
        if a >= to - 1 and b >= to - 1 and a == b:
            return tie
        k = a + b
        # serving pattern: point 0 by first server, then pairs alternate
        first = (k == 0) or (((k + 1) // 2) % 2 == 0)
        a_serving = first if a_serves_first else not first
        p = pa if a_serving else pb
        return p * rec(a + 1, b) + (1 - p) * rec(a, b + 1)

    return rec(0, 0)


# ----------------------------------------------------------------------------- set
def set_distribution(pa: float, pb: float, tiebreak_at: int | None, tiebreak_to: int, no_ad: bool,
                     a_serves_first: bool, max_adv_games: int = 40) -> dict[tuple[int, int], float]:
    """Distribution over final set scores (games_a, games_b) for one set.

    tiebreak_at=None means an advantage set; its tail (win-by-two beyond 6-6) is truncated at
    `max_adv_games` games each with the residual mass folded into the boundary states (the residual
    is < 1e-6 for any realistic serve strengths; tests check the sum is 1 within 1e-9).
    """
    ga = game_win_prob(pa, no_ad)          # P(A holds)
    gb = 1.0 - game_win_prob(1.0 - pb, no_ad)  # P(A breaks) = 1 - P(B holds); B's point prob on own serve is 1-pb
    out: dict[tuple[int, int], float] = {}

    def add(k, v):
        out[k] = out.get(k, 0.0) + v

    # forward DP over (a, b); server of game g = a+b (0-indexed) is first server iff g even
    from collections import defaultdict
    layer = {(0, 0): 1.0}
    while layer:
        nxt = defaultdict(float)
        for (a, b), pr in layer.items():
            if pr <= 0:
                continue
            g = a + b
            a_serving = ((g % 2) == 0) == a_serves_first
            p_a_wins_game = ga if a_serving else gb
            for da, db, q in ((1, 0, p_a_wins_game), (0, 1, 1 - p_a_wins_game)):
                na, nb, m = a + da, b + db, pr * q
                if m <= 0:
                    continue
                # set over?
                if tiebreak_at is not None and na == tiebreak_at and nb == tiebreak_at:
                    # tiebreak: first point served by whoever is due game index na+nb
                    tb_first_a = (((na + nb) % 2) == 0) == a_serves_first
                    t = tiebreak_win_prob(pa, pb, tiebreak_to, tb_first_a)
                    add((na + 1, nb), m * t)
                    add((na, nb + 1), m * (1 - t))
                    continue
                if na >= 6 and na - nb >= 2:
                    add((na, nb), m); continue
                if nb >= 6 and nb - na >= 2:
                    add((na, nb), m); continue
                if tiebreak_at is None and na >= max_adv_games and nb >= max_adv_games:
                    # truncate the advantage tail: split residual by the two-game tie formula
                    tie = ga * (1 - gb) / (ga * (1 - gb) + (1 - ga) * gb) if (ga * (1 - gb) + (1 - ga) * gb) > 0 else 0.5
                    add((na + 2, nb), m * tie); add((na, nb + 2), m * (1 - tie)); continue
                nxt[(na, nb)] += m
        layer = nxt
    return out


def set_win_prob(pa: float, pb: float, tiebreak_at: int | None = 6, tiebreak_to: int = 7, no_ad: bool = False,
                 a_serves_first: bool = True) -> float:
    d = set_distribution(pa, pb, tiebreak_at, tiebreak_to, no_ad, a_serves_first)
    return sum(v for (a, b), v in d.items() if a > b)


# ----------------------------------------------------------------------------- match
class MatchDistribution:
    """Container for everything the pricing layer needs, from player A's perspective."""

    def __init__(self):
        self.p_match = 0.0
        self.set_score = {}           # (sets_a, sets_b) -> prob
        self.total_games = {}         # int -> prob (tiebreak counts as one game; match tiebreak counts as one game)
        self.game_diff = {}           # games_a - games_b -> prob
        self.games_a = {}
        self.games_b = {}
        self.set_winner = {}          # set index (1-based) -> {'a': P(A wins that set AND it is played), 'b': ..., 'played': P(played)}
        self.tiebreaks = {}           # number of tiebreaks (incl. match tiebreak) -> prob
        self.sets_played = {}         # total sets -> prob
        self.set_games = {}           # set index -> {(ga, gb): prob (joint with being played)}

    def total_games_over(self, line: float) -> float:
        return sum(v for k, v in self.total_games.items() if k > line)

    def game_diff_over(self, line: float) -> float:
        """P(games_a - games_b > line). Spread 'A -3.5' is P(diff > 3.5); 'A +3.5' is P(diff > -3.5)."""
        return sum(v for k, v in self.game_diff.items() if k > line)

    def cdf_total_games(self):
        ks = sorted(self.total_games)
        return ks, np.cumsum([self.total_games[k] for k in ks])

    def as_dict(self):
        return {"p_match": self.p_match,
                "set_score": {f"{a}-{b}": v for (a, b), v in sorted(self.set_score.items())},
                "total_games": {int(k): v for k, v in sorted(self.total_games.items())},
                "game_diff": {int(k): v for k, v in sorted(self.game_diff.items())},
                "set_winner": self.set_winner, "tiebreaks": {int(k): v for k, v in sorted(self.tiebreaks.items())},
                "sets_played": {int(k): v for k, v in sorted(self.sets_played.items())}}


def match_distribution(pa: float, pb: float, fmt: MatchFormat = TOUR_SINGLES_BO3, a_serves_first: bool | None = None) -> MatchDistribution:
    """Exact joint distribution of a match under `fmt`.

    a_serves_first=None averages over the coin toss (each player 50%). Per-set distributions are
    keyed by which player serves first in that set, which the recursion tracks exactly.
    """
    if a_serves_first is None:
        d1 = match_distribution(pa, pb, fmt, True)
        d2 = match_distribution(pa, pb, fmt, False)
        return _average(d1, d2)
    pa, pb = _clip(pa), _clip(pb)
    n_win = fmt.sets_to_win
    fs_at, fs_to = fmt.final_set_rule()

    # per-set score distributions, keyed by (is_final, a_first)
    cache: dict = {}

    def set_dist(is_final: bool, a_first: bool):
        key = (is_final, a_first)
        if key not in cache:
            if is_final and fmt.final_set == "MATCH_TB10":
                t = tiebreak_win_prob(pa, pb, 10, a_first)
                cache[key] = {(1, 0): t, (0, 1): 1 - t}   # a match tiebreak counts as ONE game (1-0)
            elif is_final:
                cache[key] = set_distribution(pa, pb, fs_at, fs_to, fmt.no_ad, a_first)
            else:
                cache[key] = set_distribution(pa, pb, fmt.tiebreak_at, fmt.tiebreak_to, fmt.no_ad, a_first)
        return cache[key]

    def is_tiebreak_score(ga, gb, is_final):
        if is_final and fmt.final_set == "MATCH_TB10":
            return True
        at = fs_at if is_final else fmt.tiebreak_at
        return at is not None and ((ga == at + 1 and gb == at) or (gb == at + 1 and ga == at))

    out = MatchDistribution()
    # state: (sets_a, sets_b, a_first_in_next_set, games_a, games_b, tiebreaks) -> prob
    from collections import defaultdict
    layer = {(0, 0, a_serves_first, 0, 0, 0): 1.0}
    set_idx = 1
    while layer:
        nxt = defaultdict(float)
        sw = {"a": 0.0, "b": 0.0, "played": 0.0}
        sg = defaultdict(float)
        is_final = (set_idx == fmt.best_of)
        for (sa, sb, a_first, Ga, Gb, tb), pr in layer.items():
            sw["played"] += pr
            for (ga, gb), q in set_dist(is_final, a_first).items():
                m = pr * q
                if m <= 0:
                    continue
                sg[(ga, gb)] += m
                a_won = ga > gb
                n_games = ga + gb
                # next set first server: same as this set's first server iff even number of games
                next_first = a_first if (n_games % 2 == 0) else (not a_first)
                ntb = tb + (1 if is_tiebreak_score(ga, gb, is_final) else 0)
                nsa, nsb = sa + (1 if a_won else 0), sb + (0 if a_won else 1)
                if a_won:
                    sw["a"] += m
                else:
                    sw["b"] += m
                NGa, NGb = Ga + ga, Gb + gb
                if nsa == n_win or nsb == n_win:
                    if nsa == n_win:
                        out.p_match += m
                    out.set_score[(nsa, nsb)] = out.set_score.get((nsa, nsb), 0.0) + m
                    out.total_games[NGa + NGb] = out.total_games.get(NGa + NGb, 0.0) + m
                    out.game_diff[NGa - NGb] = out.game_diff.get(NGa - NGb, 0.0) + m
                    out.games_a[NGa] = out.games_a.get(NGa, 0.0) + m
                    out.games_b[NGb] = out.games_b.get(NGb, 0.0) + m
                    out.tiebreaks[ntb] = out.tiebreaks.get(ntb, 0.0) + m
                    out.sets_played[set_idx] = out.sets_played.get(set_idx, 0.0) + m
                else:
                    nxt[(nsa, nsb, next_first, NGa, NGb, ntb)] += m
        out.set_winner[set_idx] = sw
        out.set_games[set_idx] = dict(sg)
        layer = nxt
        set_idx += 1
    return out


def _average(d1: MatchDistribution, d2: MatchDistribution) -> MatchDistribution:
    out = MatchDistribution()
    out.p_match = 0.5 * (d1.p_match + d2.p_match)
    for name in ("set_score", "total_games", "game_diff", "games_a", "games_b", "tiebreaks", "sets_played"):
        a, b = getattr(d1, name), getattr(d2, name)
        merged = {k: 0.5 * (a.get(k, 0.0) + b.get(k, 0.0)) for k in set(a) | set(b)}
        setattr(out, name, merged)
    for i in set(d1.set_winner) | set(d2.set_winner):
        x, y = d1.set_winner.get(i, {}), d2.set_winner.get(i, {})
        out.set_winner[i] = {k: 0.5 * (x.get(k, 0.0) + y.get(k, 0.0)) for k in ("a", "b", "played")}
        sx, sy = d1.set_games.get(i, {}), d2.set_games.get(i, {})
        out.set_games[i] = {k: 0.5 * (sx.get(k, 0.0) + sy.get(k, 0.0)) for k in set(sx) | set(sy)}
    return out


def match_win_prob(pa: float, pb: float, fmt: MatchFormat = TOUR_SINGLES_BO3) -> float:
    """Fast exact P(A wins match) (no distributions)."""
    pa, pb = _clip(pa), _clip(pb)
    fs_at, fs_to = fmt.final_set_rule()
    n_win = fmt.sets_to_win
    # set win probs by first server; average over next-set server via the game-count parity
    def set_out(is_final, a_first):
        if is_final and fmt.final_set == "MATCH_TB10":
            t = tiebreak_win_prob(pa, pb, 10, a_first)
            return {(True, not a_first): t, (False, not a_first): 1 - t}
        d = set_distribution(pa, pb, fs_at if is_final else fmt.tiebreak_at, fs_to if is_final else fmt.tiebreak_to, fmt.no_ad, a_first)
        r = {}
        for (ga, gb), q in d.items():
            nf = a_first if ((ga + gb) % 2 == 0) else (not a_first)
            k = (ga > gb, nf)
            r[k] = r.get(k, 0.0) + q
        return r
    cache = {}

    @lru_cache(maxsize=None)
    def rec(sa, sb, a_first):
        if sa == n_win:
            return 1.0
        if sb == n_win:
            return 0.0
        is_final = (sa + sb + 1 == fmt.best_of)
        key = (is_final, a_first)
        if key not in cache:
            cache[key] = set_out(is_final, a_first)
        tot = 0.0
        for (a_won, nf), q in cache[key].items():
            tot += q * rec(sa + (1 if a_won else 0), sb + (0 if a_won else 1), nf)
        return tot
    return 0.5 * (rec(0, 0, True) + rec(0, 0, False))


# ----------------------------------------------------------------------------- inversion
def point_probs_from_match_prob(target: float, spw_sum: float = 1.28, fmt: MatchFormat = TOUR_SINGLES_BO3,
                                tol: float = 1e-7) -> tuple[float, float]:
    """Find (pa, pb) with pa + (1 - pb) = spw_sum (both players' serve-point win probs sum to a tour/surface
    average) such that P(A wins match) == target. Bisection on the serve-strength gap.

    Used to price derivative markets consistently from a match-winner probability produced by a model
    that has no serve/return decomposition (Elo, market). spw_sum ~ 1.28 for ATP hard (0.64 each),
    ~1.20 for WTA; the caller should pass the surface/tour-specific figure.
    """
    target = _clip(target)
    lo, hi = -0.5, 0.5

    def f(delta):
        pa = spw_sum / 2 + delta          # A's serve point win prob
        pb_serve = spw_sum / 2 - delta    # B's serve point win prob
        return match_win_prob(_clip(pa), _clip(1 - pb_serve), fmt)

    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if f(mid) < target:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    d = 0.5 * (lo + hi)
    return _clip(spw_sum / 2 + d), _clip(1 - (spw_sum / 2 - d))
