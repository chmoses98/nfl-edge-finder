# Role features for player opportunity (Milestone F groundwork)

`scripts/research/role_features_study.py`. Walk-forward 2018–2024 (train on prior seasons), WR/TE targets and RB carries,
players with ≥3 prior games. Baseline: log-ridge on the player's own EWMA (half-life 6 games). Role model adds
prior-game offensive snap share, EWMA snap share, weekly depth-chart rank (1/2 dummies; pre-2025 NFL weekly charts) and
team target-volume EWMA. Point-in-time: every feature uses only games strictly before the game (depth chart of that week).

| target | season | MAE EWMA-only | MAE with role | gain |
|---|---|---|---|---|
| targets (WR/TE) | 2018–2024 | 1.77–1.93 | 1.72–1.87 | −2.7% to −3.2% every season |
| carries (RB) | 2018–2024 | 3.53–3.96 | 3.39–3.74 | −3.5% to −7.1% every season |

Both gains are consistent in sign in all seven test seasons. Snap share is the dominant addition (usage the box score
does not show); depth-chart rank adds little once snap share is present. This confirms the design choice that the
opportunity model must be driven by *snaps/routes/role*, with the box-score EWMA as a prior.

Reallocation when the team's top target-share player is absent: only 15 qualifying player-games were detected (the
snap-count join via PFR ids misses players, and "absent" was measured from same-game snaps, so this is descriptive
only). Teammates at depth ranks 2–3 gained +3.5 to +4.3 targets vs their EWMA while rank-1 players gained +0.3 — the
expected shape, far from a validated redistribution model. Next: a proper availability-driven reallocation study using
weekly roster status (RES/IR/OUT) as the pregame absence signal and hierarchical team-level redistribution priors.
