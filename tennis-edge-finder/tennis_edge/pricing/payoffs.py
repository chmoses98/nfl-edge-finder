"""Price parsed Kalshi tennis markets as payoff functions of ONE coherent match distribution.

A MatchDistribution (tennis_edge.sim.analytic) is computed once per match from (pa, pb, format);
every market on that match is a functional of it, so the family prices are internally consistent
by construction: the match-winner probability equals the sum of the winning exact-score paths,
total-game ladders are monotone, spread ladders are monotone, set-winner probabilities respect the
sets-played mass, etc. Health gate TENNIS-11 re-checks those invariants on the produced prices.

Settlement semantics that matter for pricing (from rules_primary / rules_secondary, verified on
real records, see docs/KALSHI_MARKET_TAXONOMY.md):
  * MATCH_WINNER: "after a ball has been played" -> a retirement after the first point settles to the
    player declared winner; a walkover before the first ball settles to a FAIR PRICE scalar. Our
    pregame fair value is P(win | match starts) -- the walkover branch is a settlement event we cannot
    price and is excluded by the ledger's canonical-close logic (exchange truth vs sports truth).
  * TOTAL_GAMES: "number of completed games in the full match" -- if a player retires, completed games
    count; incomplete-scope markets resolve to fair price per Kalshi rules. We price the completed-
    match distribution and flag the retirement-mass as a documented modelling gap (RISK_RETIREMENT).
  * SET_WINNER for a set that is never played (match ends earlier): exchange resolves per its rules
    (typically fair price / scalar). Our fair value is P(subject wins set n AND set n is played); the
    conditional P(win | played) is exposed too so the settlement layer can pick the right one once the
    rule for that series is byte-verified.
"""
from __future__ import annotations

from dataclasses import dataclass

from tennis_edge.kalshi.markets import ParsedMarket
from tennis_edge.sim.analytic import MatchDistribution


class PricingError(ValueError):
    """Raised when a parsed market cannot be priced from the distribution (fail closed)."""


@dataclass
class Price:
    ticker: str
    family: str
    fair_yes: float
    method: str
    notes: str = ""
    conditional_yes: float | None = None   # e.g. P(win set n | set n played)
    p_played: float | None = None


def _orient(dist_prob_a: float, subject_is_a: bool) -> float:
    return dist_prob_a if subject_is_a else 1.0 - dist_prob_a


def price_market(pm: ParsedMarket, d: MatchDistribution) -> Price:
    """Fair YES probability for a MATCH-scope parsed market given the match distribution for
    (player_a, player_b) in rules-text order (player_a is 'A' in the distribution)."""
    if pm.status != "PARSED":
        raise PricingError(f"{pm.ticker}: market not parsed ({pm.status}: {pm.reason})")
    if pm.scope != "MATCH":
        raise PricingError(f"{pm.ticker}: scope {pm.scope} is not match-scope")
    fam = pm.family
    if fam == "MATCH_WINNER":
        if pm.subject_is_a is None:
            raise PricingError(f"{pm.ticker}: subject side unknown")
        return Price(pm.ticker, fam, _orient(d.p_match, pm.subject_is_a), "dp_match", "P(win | match starts)")
    if fam == "SET_WINNER":
        sw = d.set_winner.get(pm.set_index)
        if sw is None:
            raise PricingError(f"{pm.ticker}: set {pm.set_index} impossible under format")
        joint = sw["a"] if pm.subject_is_a else sw["b"]
        cond = joint / sw["played"] if sw["played"] > 0 else None
        return Price(pm.ticker, fam, joint, "dp_set_joint", "P(win set n AND played); conditional exposed", cond, sw["played"])
    if fam == "EXACT_SET_SCORE":
        x, y = pm.exact_score
        key = (x, y) if pm.subject_is_a else (y, x)
        p = d.set_score.get(key, 0.0)
        return Price(pm.ticker, fam, p, "dp_set_score")
    if fam == "GAME_SPREAD":
        # YES iff (games_subject - games_opponent) > line
        if pm.subject_is_a:
            p = sum(v for k, v in d.game_diff.items() if k > pm.line)
        else:
            p = sum(v for k, v in d.game_diff.items() if -k > pm.line)
        return Price(pm.ticker, fam, p, "dp_game_diff", "completed-match distribution; retirement mass not modelled")
    if fam == "TOTAL_GAMES":
        return Price(pm.ticker, fam, d.total_games_over(pm.line), "dp_total_games", "completed-match distribution; retirement mass not modelled")
    if fam == "TOTAL_SETS":
        return Price(pm.ticker, fam, sum(v for k, v in d.sets_played.items() if k > pm.line), "dp_sets_played")
    if fam == "SET_SPREAD":
        p = 0.0
        for (sa, sb), v in d.set_score.items():
            diff = (sa - sb) if pm.subject_is_a else (sb - sa)
            if diff > pm.line:
                p += v
        return Price(pm.ticker, fam, p, "dp_set_diff")
    if fam == "TIEBREAK_OCCURS":
        return Price(pm.ticker, fam, 1.0 - d.tiebreaks.get(0, 0.0), "dp_tiebreaks")
    if fam == "ANY_SET_WINNER":
        # P(subject wins at least one set) = 1 - P(straight-sets loss)
        n = max(k[0] + k[1] for k in d.set_score) if d.set_score else 0
        lose_straight = sum(v for (sa, sb), v in d.set_score.items() if (sa == 0 if pm.subject_is_a else sb == 0))
        return Price(pm.ticker, fam, 1.0 - lose_straight, "dp_any_set")
    raise PricingError(f"{pm.ticker}: family {fam} has no match-scope payoff")


def check_consistency(prices: list[Price], parsed: dict[str, ParsedMarket], tol: float = 1e-9) -> list[str]:
    """Invariant checks across the prices of one match (TENNIS-11). Returns violation strings."""
    v = []
    by_fam: dict[str, list] = {}
    for p in prices:
        by_fam.setdefault(p.family, []).append(p)
    # match winner: the two sides sum to 1
    mw = by_fam.get("MATCH_WINNER", [])
    if len(mw) == 2 and abs(mw[0].fair_yes + mw[1].fair_yes - 1) > 1e-6:
        v.append(f"match-winner sides sum to {mw[0].fair_yes + mw[1].fair_yes:.6f}")
    # exact scores sum to 1 across all listed scores when the ladder is complete
    ex = by_fam.get("EXACT_SET_SCORE", [])
    if ex:
        s = sum(p.fair_yes for p in ex)
        if s > 1 + 1e-6:
            v.append(f"exact-score probabilities sum to {s:.6f} > 1")
    # totals ladder monotone (higher line -> lower P(over))
    for fam in ("TOTAL_GAMES", "TOTAL_SETS"):
        rows = sorted((parsed[p.ticker].line, p.fair_yes) for p in by_fam.get(fam, []))
        for (l1, p1), (l2, p2) in zip(rows, rows[1:]):
            if l2 > l1 and p2 > p1 + tol:
                v.append(f"{fam} not monotone: line {l1}->{p1:.4f}, {l2}->{p2:.4f}")
    # spreads monotone per subject
    for fam in ("GAME_SPREAD", "SET_SPREAD"):
        per = {}
        for p in by_fam.get(fam, []):
            per.setdefault(parsed[p.ticker].subject, []).append((parsed[p.ticker].line, p.fair_yes))
        for subj, rows in per.items():
            rows.sort()
            for (l1, p1), (l2, p2) in zip(rows, rows[1:]):
                if l2 > l1 and p2 > p1 + tol:
                    v.append(f"{fam} {subj} not monotone: {l1}->{p1:.4f}, {l2}->{p2:.4f}")
    return v
