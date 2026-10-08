"""Football Signal Discovery Lab -- Wave 1 (NFL). RESEARCH ONLY.

Protocol: docs/research/FOOTBALL_SIGNAL_DISCOVERY_WAVE1_PROTOCOL.md

Layers, kept in separate modules so the wall between them can be tested:

  game_features.py    market-blind, outcome-blind team ratings and game features at every (season, week)
                      snapshot, solved on STRICTLY EARLIER games with the repository's preregistered
                      opponent-adjustment solver (``nfl_edge.sim.opponent_adjust.solve``, sim-oppadj-1.0.0).
  player_features.py  point-in-time player opportunity / efficiency / role features (reuses
                      ``nfl_edge.sim.features`` with frozen priors) joined to the team context.
  markets.py          the market side: nflverse schedule closing lines and Kalshi player-prop ladders.
                      Never imported by the two feature modules.
  evaluate_*.py       the only place features, markets and outcomes meet, gated on frozen hypothesis hashes.

Nothing here changes RUN NFL, Shadow v2, the incumbent pricer, the sim engine, board, handicap gates,
settlement, app export, router behaviour or any workflow.
"""

SIGNAL_DISCOVERY_VERSION = "nfl-signal-discovery-wave1/1.0.0"
