"""The latent projection engines of SHADOW v2.

    game       one joint final-score simulation prices every deterministic function of the final score
    period     one joint quarter-score simulation prices every period market (research + shadow)
    player     one lattice distribution per (player, statistic) prices the whole ladder; three arms
    season     schedule-level Monte Carlo (foundation)
    joint      parlay / composite legs mapped to shared simulations, else JOINT_MODEL_REQUIRED
    coherence  model-free structural audit of mutually exclusive event groups

Kalshi contracts are questions (`nfl_edge/semantics/questions.py`) asked of these distributions. No engine
here has any betting authority; every output is a research/shadow projection.
"""
