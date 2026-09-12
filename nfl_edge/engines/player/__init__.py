"""PLAYER ENGINE v2: one lattice distribution per (player, statistic) prices the whole ladder.

    dist          LatticeDistribution -- a validated pmf on the integers; every rung is an integral of it
    market_dist   MARKET_PLAYER_DIST  -- the market's own distribution inferred from a quoted ladder, with an
                                        identification status and executable bounds
    features_v2   opportunity / share / team-volume / QB-environment features, point-in-time
    data_dist     DATA_PLAYER_DIST    -- the football/data distribution, opportunity x efficiency, walk-forward
    hybrid_dist   HYBRID_PLAYER_DIST  -- a preregistered latent-level blend, research arm

None of these arms has betting authority. The incumbent player model is untouched; this package is a new
research architecture that must earn weight prospectively.
"""
