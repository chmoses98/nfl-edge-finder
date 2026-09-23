"""HYBRID_PLAYER_DIST: a preregistered latent-level blend of the market and data distributions (research arm).

Two blend structures are defined and compared historically (scripts/research/player_engine_v2_study.py):

    LOCATION_BLEND(w)   the DATA distribution re-located so its mean is w x market mean + (1 - w) x data mean,
                        keeping the data family's SHAPE (a scale transform of the lattice). This is a blend of the
                        latent location parameter, never of threshold probabilities.
    MIXTURE(w)          the pmf mixture w x market + (1 - w) x data. Coherent (a valid pmf, monotone survival)
                        but it is a probability average and is kept only as a comparator.

`w` is preregistered from the historical study (2025 weeks 1-9 to choose, 10-18 to confirm), never fitted on the
season being scored. The blend is UNAVAILABLE -- never a silent fallback to one side -- when either input is
missing or the market side is UNDERIDENTIFIED / NONE.
"""
from __future__ import annotations

from nfl_edge.engines.player.dist import LatticeDistribution

VERSION = "hybrid-player-dist-1.0.0"
LOCATION_BLEND = "LOCATION_BLEND"
MIXTURE = "MIXTURE"
# Set by the study (research/player_engine_v2/RESULTS.md). The preregistered selection on 2025 weeks 1-9 at T-90m
# chose the MARKET distribution outright: NO hybrid beat the monotone market ladder on the confirmation weeks 10-18
# (closest: pmf MIXTURE at w=0.7, +0.00091 +/- 0.00056 Brier, z 1.6). The HYBRID arm therefore stays a RESEARCH arm
# whose prospective records exist to accumulate evidence, not a candidate for authority; its default is the
# confirmed-closest structure so that the prospective test is of the best-known blend, not a straw man.
DEFAULT_STRUCTURE = MIXTURE
DEFAULT_WEIGHT_MARKET = 0.7
STUDY_VERDICT = "market_mono selected; no hybrid beat the market (2025 confirmation weeks 10-18)"


def hybrid(data: LatticeDistribution | None, market: LatticeDistribution | None, *, market_identification: str | None,
           w_market: float = DEFAULT_WEIGHT_MARKET, structure: str = DEFAULT_STRUCTURE) -> dict:
    if data is None:
        return {"status": "UNAVAILABLE", "reason": "no data distribution", "dist": None}
    if market is None or market_identification in (None, "NONE", "UNDERIDENTIFIED"):
        return {"status": "UNAVAILABLE", "reason": f"market distribution {market_identification or 'missing'}; no fallback to one side", "dist": None}
    if structure == LOCATION_BLEND:
        target = w_market * market.mean() + (1.0 - w_market) * data.mean()
        d = data.shifted_to_mean(target)
        d.meta.update({"structure": structure, "w_market": w_market, "market_mean": market.mean(), "data_mean": data.mean(), "target_mean": target})
    elif structure == MIXTURE:
        d = market.mixture(data, w_market)
        d.meta.update({"structure": structure, "w_market": w_market})
    else:
        return {"status": "UNAVAILABLE", "reason": f"unknown structure {structure}", "dist": None}
    ok, why = d.check_valid()
    if not ok:
        return {"status": "UNAVAILABLE", "reason": f"blend invalid: {why}", "dist": None}
    return {"status": "OK", "dist": d, "structure": structure, "w_market": w_market, "version": VERSION}


# HYBRID_PLAYER_V3: the same preregistered structure over DATA_PLAYER_V3 (data-player-dist-3.0.0). Its weight is
# chosen by the same protocol (2025 weeks 1-9 select, weeks 10-18 confirm; research/player_engine_v3/RESULTS.md)
# and is never fitted on the season being scored.
VERSION_V3 = "hybrid-player-dist-2.0.0"
V3_STRUCTURE = MIXTURE
# Selection (2025 weeks 1-9, T-90m) among the hybrids {0.5, 0.7, 0.85}: 0.85 (+0.00049 +/- 0.00054 vs market);
# confirmation (weeks 10-18): +0.00009 +/- 0.00027 -- indistinguishable from the market, never better. Including
# the market itself in the candidate set, the protocol selects the MARKET. The hybrid is therefore research: it
# exists to learn prospectively whether a small data component ever adds information, not as an input.
V3_WEIGHT_MARKET = 0.85
V3_STUDY_VERDICT = "market selected; best hybrid (0.85 market) indistinguishable from the market on 2025 weeks 10-18"
