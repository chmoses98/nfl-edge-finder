"""Doubles projection interface (schema + baseline + explicit gap).

Kalshi lists doubles at every level (KXATPDOUBLES, KXWTADOUBLES, KXATPCHALLENGERDOUBLES, KXITFDOUBLES,
KXITFWDOUBLES, KXMIXEDDOUBLESMATCH: 9,800 markets in the 2026-09-11 snapshot). Historical doubles truth in
the free corpus is thin: Sackmann's atp_matches_doubles files stop around 2019-2020 and carry no serve
stats; WTA doubles history is not in the free corpus; ITF doubles is absent. Therefore tonight:

  * TeamKey identity: sorted pair of canonical player ids (order-free), so "Krawietz / Puetz" and
    "Puetz / Krawietz" are one team.
  * DoublesBaseline: team strength = mean of the two players' doubles Elo (updated from doubles results
    where available) shrunk toward the mean of their singles Elo with weight w_singles = 0.3 -- a documented
    PRIOR, not a fitted parameter, because there is no walk-forward doubles benchmark yet. Pair-experience
    bonus is NOT applied (unvalidated).
  * The projection carries data_quality grade capped at "C" and `unvalidated=True` so the decision layer
    can never rate a doubles market above LEAN until a prospective doubles track record exists.
"""
from __future__ import annotations

from dataclasses import dataclass

from tennis_edge.models.elo import expected


def team_key(p1: str, p2: str) -> str:
    return "|".join(sorted([str(p1), str(p2)]))


@dataclass
class DoublesBaseline:
    w_singles: float = 0.3
    doubles_elo: dict = None
    singles_elo: dict = None

    def __post_init__(self):
        self.doubles_elo = self.doubles_elo or {}
        self.singles_elo = self.singles_elo or {}

    def team_rating(self, p1: str, p2: str) -> tuple[float, dict]:
        d = [self.doubles_elo.get(p, None) for p in (p1, p2)]
        s = [self.singles_elo.get(p, None) for p in (p1, p2)]
        d_mean = sum(x for x in d if x is not None) / max(1, sum(x is not None for x in d)) if any(x is not None for x in d) else None
        s_mean = sum(x for x in s if x is not None) / max(1, sum(x is not None for x in s)) if any(x is not None for x in s) else None
        if d_mean is None and s_mean is None:
            return 1500.0, {"basis": "PRIOR_ONLY", "doubles_known": 0, "singles_known": 0}
        if d_mean is None:
            return s_mean, {"basis": "SINGLES_ONLY", "doubles_known": 0, "singles_known": sum(x is not None for x in s)}
        if s_mean is None:
            return d_mean, {"basis": "DOUBLES_ONLY", "doubles_known": sum(x is not None for x in d), "singles_known": 0}
        return (1 - self.w_singles) * d_mean + self.w_singles * s_mean, {"basis": "BLEND", "doubles_known": sum(x is not None for x in d), "singles_known": sum(x is not None for x in s)}

    def predict(self, team_a: tuple[str, str], team_b: tuple[str, str]) -> dict:
        ra, ia = self.team_rating(*team_a)
        rb, ib = self.team_rating(*team_b)
        return {"p_a": expected(ra, rb), "rating_a": ra, "rating_b": rb, "basis_a": ia, "basis_b": ib, "unvalidated": True,
                "quality_grade_cap": "C", "note": "doubles baseline is a documented prior; no walk-forward validation yet"}
