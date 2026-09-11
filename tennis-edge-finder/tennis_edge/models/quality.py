"""DATA_QUALITY_SCORE for a projection: how much evidence stands behind the number.

The score is a bounded product of evidence factors so that any single missing pillar drags it down:
  * experience: matches in the rating history for each player (min of the two), saturating at 60
  * serve/return evidence: serve points observed for each player (min), saturating at 3000 points
  * recency: days since each player's last recorded match (max of the two), penalised beyond 90 days
  * level familiarity: fraction of the players' recent matches at the same level as this match
  * identity confidence: min mapping confidence of the two players to canonical ids (1.0 for exact ids)
  * format known: 1 if the scoring format resolved from the registry, else 0 (fail closed elsewhere)
The output is in [0, 1]; the pillars are returned too so the WHY panel can name the weak spot.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class QualityInputs:
    n_matches_a: int
    n_matches_b: int
    serve_points_a: float
    serve_points_b: float
    days_since_last_a: float | None
    days_since_last_b: float | None
    level_familiarity: float          # 0..1
    identity_confidence: float        # 0..1
    format_known: bool


def _sat(x: float, k: float) -> float:
    return 1.0 - math.exp(-max(x, 0.0) / k)


def data_quality(q: QualityInputs) -> dict:
    exp = _sat(min(q.n_matches_a, q.n_matches_b), 20.0)
    sr = _sat(min(q.serve_points_a, q.serve_points_b), 1000.0)
    days = max([d for d in (q.days_since_last_a, q.days_since_last_b) if d is not None] or [365.0])
    rec = 1.0 if days <= 90 else math.exp(-(days - 90) / 180.0)
    lvl = min(max(q.level_familiarity, 0.0), 1.0)
    idc = min(max(q.identity_confidence, 0.0), 1.0)
    fmt = 1.0 if q.format_known else 0.0
    # geometric blend; serve/return evidence is a soft pillar (Elo-only projections are still usable)
    score = fmt * idc * (exp ** 0.35) * ((0.4 + 0.6 * sr) ** 0.5) * (rec ** 0.5) * ((0.5 + 0.5 * lvl) ** 0.5)
    grade = "A" if score >= 0.8 else "B" if score >= 0.6 else "C" if score >= 0.4 else "D" if score > 0.2 else "F"
    return {"data_quality_score": round(score, 4), "grade": grade,
            "pillars": {"experience": round(exp, 3), "serve_return_evidence": round(sr, 3), "recency": round(rec, 3),
                        "level_familiarity": round(lvl, 3), "identity_confidence": round(idc, 3), "format_known": fmt},
            "inputs": asdict(q)}
