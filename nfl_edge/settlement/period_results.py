"""Proven PERIOD results from free play-by-play: end-of-quarter scores, with the evidence that proves them.

The free schedule feed carries no period scores, which is why the incumbent refuses every period contract. The
nflverse play-by-play does carry them: the post-play score of the last play of each quarter reproduces the
final score of every non-overtime game (256/256 in 2024, 2,489/2,495 across 2016-2025). This module extracts them
for one season, and it is CONTRADICTION-AWARE: a game whose regulation quarters do not sum to its schedule final
(overtime excluded) is marked inconsistent and refused, never repaired.

    PeriodResult(game_id, hq1..hq4, aq1..aq4, home_reg, away_reg, complete, inconsistency)
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

from nfl_edge.engines.period import COLS, quarter_scores_from_pbp

PERIODS = {"1Q": ("q1",), "2Q": ("q2",), "3Q": ("q3",), "4Q": ("q4",), "1H": ("q1", "q2"), "2H": ("q3", "q4")}


@dataclass
class PeriodResult:
    game_id: str
    scores: dict = field(default_factory=dict)      # hq1..aq4
    home_reg: float | None = None
    away_reg: float | None = None
    complete: bool = False
    inconsistency: str | None = None
    source: str | None = None

    def period_points(self, period: str, side: str) -> float | None:
        if not self.complete:
            return None
        qs = PERIODS[period]
        return float(sum(self.scores[("h" if side == "home" else "a") + q] for q in qs))

    def evidence(self, period: str | None = None) -> dict:
        ev = {"game_id": self.game_id, "period_scores": dict(self.scores), "home_reg": self.home_reg, "away_reg": self.away_reg,
              "complete": self.complete, "source": self.source}
        if self.inconsistency:
            ev["inconsistency"] = self.inconsistency
        if period and self.complete:
            ev["period"] = period
            ev["home_period_points"] = self.period_points(period, "home")
            ev["away_period_points"] = self.period_points(period, "away")
        return ev


class PeriodBook:
    def __init__(self):
        self.games: dict[str, PeriodResult] = {}
        self.sources: list = []

    def load_pbp(self, path: str, finals: dict | None = None) -> int:
        """`finals`: game_id -> (home_score, away_score, overtime) from the schedule, for the contradiction check."""
        w = quarter_scores_from_pbp(path)
        n = 0
        for r in w.iter_rows(named=True):
            scores = {c: r.get(c) for c in COLS}
            pr = PeriodResult(game_id=r["game_id"], scores=scores, home_reg=r.get("home_reg"), away_reg=r.get("away_reg"),
                              source=os.path.relpath(path) if os.path.isabs(path) else path)
            pr.complete = all(v is not None for v in scores.values())
            if pr.complete and finals and r["game_id"] in finals:
                hs, aws, ot = finals[r["game_id"]]
                if hs is not None and aws is not None and not ot and (pr.home_reg != hs or pr.away_reg != aws):
                    pr.inconsistency = f"regulation quarters sum to {pr.home_reg}-{pr.away_reg} but the schedule final is {hs}-{aws} with no overtime"
            self.games[r["game_id"]] = pr
            n += 1
        self.sources.append({"path": path, "games": n})
        return n

    def get(self, game_id: str) -> PeriodResult | None:
        return self.games.get(game_id)
