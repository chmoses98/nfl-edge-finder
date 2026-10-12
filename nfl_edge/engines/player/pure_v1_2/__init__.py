"""PURE_PLAYER_V1_2: a sports-only research challenger to the frozen PURE_PLAYER_V1 (research only, never wired).

Separate package. PURE_PLAYER_V1 (`nfl_edge/engines/player/pure_v1`, pure-player-v1.0.0) is imported read-only and
never modified: V1_2 reuses its data path, features, estimators, distribution machinery and pipeline helpers, and
adds three football-only, point-in-time feature families aimed at the error sources measured in
docs/research/PURE_GAP_DECOMPOSITION.md:

    (A) environment-conditioned efficiency   PURE's own football-only team points / margin forecast enters the
                                             catch-rate, yards-per-target, yards-per-carry, completion-rate and
                                             yards-per-attempt models (the sports-only analogue of the channel through
                                             which V4's market-implied total helps its yardage forecasts)
    (B) positional opponent adjustment       what the opponent allowed to the player's position group, as levels and
                                             over expected (features.defence_by_group)
    (C) available-pool opportunity           the team's opportunity pool after its previous game: how much recent
                                             share is still active and the player's share of it (features.available_pool)

Point-in-time injury reports are NOT used: the only certified historical source covers 2010-2024 and 2025 is
rejected (docs/research/NFL_PIT_AVAILABILITY_CERTIFICATION.md, PR #137), so they cannot be used on this
challenger's held-out window. Preregistration: docs/research/PURE_PLAYER_V1_2_PREREGISTRATION.md.
"""
MODEL_NAME = "PURE_PLAYER_V1_2"
VERSION = "pure-player-v1.2.0"
