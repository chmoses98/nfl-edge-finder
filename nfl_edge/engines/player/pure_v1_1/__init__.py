"""PURE_PLAYER_V1_1: PURE_PLAYER_V1 plus point-in-time availability features (one preregistered ablation).

Preregistration: docs/research/PURE_PLAYER_V1_1_PREREGISTRATION.md (commit 4441249, frozen before holdout scoring).
PURE_PLAYER_V1 (nfl_edge/engines/player/pure_v1, frozen at 0441dfc) is imported, never edited. The only additions are
own-status / practice flags and teammate vacated-share features from the CERTIFIED nflverse injury report (rows whose
`date_modified` precedes kickoff - 90 min; nfl_edge.availability_pit.loaders.injuries_certified), entering the
snap-share, target-share and carry-share stages. Football data only; no market input of any kind.
"""
MODEL_NAME = "PURE_PLAYER_V1_1"
VERSION = "pure-player-v1.1.0"
