# Game Script Discovery Lab: report (RESEARCH_ONLY)

Reproduce: `python scripts/sim/gsdl_tournament.py run && python scripts/sim/gsdl_stats.py` (about 1 minute after the nflverse pbp and schedules download). Per-game scores are cached in `cache/`; every number below comes from `results.json`.

**Verdict: REJECT (no candidate qualifies; do not promote anything to prospective shadow).** 36 candidates were scored (A0 + A1/A2 cell-level references + 11 feature families + 6 interactions + 16 distribution variants; 132 candidate x primary-metric tests in the multiplicity set).

Baseline A0 (the incumbent market-centred residual bank, evaluated exactly on the integer lattice, 1,424 games 2021-2025): margin CRPS 7.086, total CRPS 7.344, six-class script log loss 1.672, nine-cell log loss 1.923, nine-cell Brier 0.8217. It reproduces the published `SCRIPT_CALIBRATION_5Y` numbers (Brier 0.8215, log loss 1.9226; prior-only references 0.8286 / 1.9469 reproduced to 4 decimals).

See the chat summary for the top five, calibration, key-number and limitation tables.
