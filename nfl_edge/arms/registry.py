"""Preregistered constants of the three-arm experiment. Frozen here, mirrored in the hypothesis registry.

Everything the evaluation could be tempted to redefine after seeing outcomes is a named constant in this one
module, and `tests/test_three_arm_preregistration.py` pins each of them against
`research/hypothesis_registry/H-20260910-026.json`. Changing a weight, a horizon, a metric or the sample gate
is therefore a visible edit to a preregistration, never a quiet drift in a report.
"""
from __future__ import annotations

import hashlib

ARMS_VERSION = "three-arm-1.0.0"          # identity of the record schema + arm definitions
CRN_VERSION = "crn-1.0.0"                 # identity of the common-random-number simulator
DATA_ONLY_VERSION = "data_only-1.0.0"     # identity of the football-only centre model
ARM_EVALUATION_VERSION = "arm-eval-1.0.0"
AUTOPSY_VERSION = "autopsy-1.0.0"
FUNNEL_VERSION = "funnel-1.0.0"
HYPOTHESIS_ID = "H-20260910-026"

# ---- the three primary arms -----------------------------------------------------------------------
CURRENT = "CURRENT_MARKET_PRIOR"
DATA_ONLY = "DATA_ONLY"
HYBRID = "HYBRID_30_DATA"
PRIMARY_ARMS = (CURRENT, DATA_ONLY, HYBRID)

# The ONE preregistered hybrid. Not optimised on 2026, not searched, not game-dependent, not dynamic.
HYBRID_WEIGHT_MARKET = 0.70
HYBRID_WEIGHT_DATA = 0.30

# ---- simulation -----------------------------------------------------------------------------------
N_SIMS = 40000                            # the incumbent's own standard (scripts/shadow/price_slate.py)
CENTER_GRID = 0.5                         # challenger centres are placed on the half-point grid the residual bank keys on

# ---- horizons and sample units ---------------------------------------------------------------------
PRIMARY_HORIZONS_MIN = (1440, 360, 90, 30)          # T-24h, T-6h, T-90m, T-30m
HORIZON_LABELS = {1440: "T-24h", 360: "T-6h", 90: "T-90m", 30: "T-30m"}

# Centre-disagreement bands, in points of |challenger centre - market centre|. Descriptive cuts of ONE sample,
# never independent studies.
DISAGREEMENT_BANDS_POINTS = ((1.0, "<=1"), (2.0, "1-2"), (3.0, "2-3"), (5.0, "3-5"), (float("inf"), ">5"))

# No verdict of any kind is printed before this many DISTINCT GAMES have a scored latest-pregame record. Four
# full regular-season weeks. Below it every comparison is labelled INSUFFICIENT_EVIDENCE.
MIN_GAMES_FOR_VERDICT = 64

# ---- prospective integrity ---------------------------------------------------------------------------
# A challenger forecast is prospective only if it was GENERATED before kickoff from a market snapshot OBSERVED
# before kickoff. A snapshot generated later than this many minutes after the capture it prices is refused:
# nothing legitimate takes longer, and a long gap is what a reconstruction looks like.
MAX_GENERATION_LAG_MIN = 240.0
FIRST_2026_KICKOFF_UTC = "2026-09-10T00:20:00+00:00"

# The families every arm prices from the joint game simulation. Same set the incumbent prices coherently.
GAME_FAMILIES_PRICED = ("GAME_WINNER", "SPREAD", "TOTAL", "TEAM_TOTAL", "BOTH_TEAMS_SCORE_N")

# Statuses of one arm inside one game record.
OK = "OK"
DEGRADED = "DEGRADED"
UNAVAILABLE = "UNAVAILABLE"
POST_KICKOFF_EXCLUDED = "POST_KICKOFF_EXCLUDED"


def preregistration() -> dict:
    """The machine-readable preregistration, as the registry entry and the tests read it."""
    return {
        "hypothesis_id": HYPOTHESIS_ID,
        "arms": list(PRIMARY_ARMS),
        "hybrid_weight_market": HYBRID_WEIGHT_MARKET,
        "hybrid_weight_data": HYBRID_WEIGHT_DATA,
        "n_sims": N_SIMS,
        "primary_horizons_min": list(PRIMARY_HORIZONS_MIN),
        "primary_game_center_metrics": ["margin_rmse", "margin_mae", "total_rmse", "total_mae"],
        "primary_market_pricing_metrics": ["paired_brier_vs_current", "paired_payout_mse_vs_market_at_snapshot",
                                           "movement_toward_close"],
        "min_games_for_verdict": MIN_GAMES_FOR_VERDICT,
        "disagreement_bands_points": [b[1] for b in DISAGREEMENT_BANDS_POINTS],
        "arms_version": ARMS_VERSION,
        "data_only_version": DATA_ONLY_VERSION,
        "crn_version": CRN_VERSION,
    }


def preregistration_sha() -> str:
    import json
    return hashlib.sha256(json.dumps(preregistration(), sort_keys=True).encode()).hexdigest()[:16]
