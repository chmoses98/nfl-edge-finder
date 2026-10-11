"""PURE_PLAYER_V1: a strictly market-independent NFL player-stat forecaster (research only).

A separate, versioned arm. It reads ONLY football data (nflverse box scores, snap counts and the schedule's
non-market columns) and never a spread, total, moneyline, odds, implied quantity, Kalshi quote or market ticker
inventory -- not as a feature, not as a training-sample filter and not as a population selector. The football
data path is enforced by column allowlists (`data.SCHEDULE_ALLOWLIST`, `data.PLAYER_ALLOWLIST`) and proved at
runtime by rerunning the whole pipeline with the market columns removed and randomised
(tests/test_pure_player_v1.py, scripts/research/pure_player_v1_mutation.py).

Nothing here edits, imports the fitted state of, or replaces V3 / V4 / V5, their records or the market-centred
simulation. See docs/research/PURE_PLAYER_V1_DEPENDENCY_AUDIT.md and docs/research/PURE_PLAYER_V1_PREREGISTRATION.md.
"""
MODEL_NAME = "PURE_PLAYER_V1"
VERSION = "pure-player-v1.0.0"
BASELINE_NAME = "PURE_EWM_BASELINE"
BASELINE_VERSION = "pure-ewm-baseline-1.0.0"
