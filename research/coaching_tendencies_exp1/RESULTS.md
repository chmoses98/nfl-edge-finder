# Experiment 1: coaching and offensive tendencies vs the incumbent volume model (RESEARCH_ONLY)

Reproduce: `python scripts/sim/coaching_tendencies_exp1.py` (writes `results.json`; ~10 s; needs `pbp` + `schedules` from
`scripts/data/nflverse_download.py --only pbp,schedules --seasons 2016-2025`). Nothing here touches a production artifact.

Design: walk-forward 2021-2025 (train 2018..Y-1, incumbent `fit_game_env` ridge, `team_n_prior>=4`, identical 2,848
test team-games for every arm). Mode A = incumbent specification (conditions on realised margin/total, as the simulator
does per row). Mode P = pregame variant (consensus line margin/total substituted in train and test). CRPS is a Gaussian
predictive with the training-residual sd (the ridge model has no native distribution). 2021-2025 are historical research
evidence, not untouched validation.

Arms: B0 incumbent; B1 team tendencies (early-down neutral pass rate, neutral no-huddle rate, short-minus-long neutral
pass-rate shift); B2 head-coach-tenure PROXIES (coach-keyed EWMA vs team EWMA, new-coach flag, tenure; play-caller identity
is NOT available); B3 opponent-keyed defensive response (induced neutral pass rate / pace relative to the offence's own
prior level; early-down neutral pass rate allowed); CTL_A4 control (incumbent train/serve skew repaired); B3_ON_A4 post-hoc
attribution arm. B4 not run (no individual signal in B1/B2).

See `results.json` for every metric, bootstrap interval (game-clustered, 2,000 reps) and per-season value.
