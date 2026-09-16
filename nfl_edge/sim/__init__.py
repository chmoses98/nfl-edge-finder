"""Coherent game-simulation projection layer (sim-1.x).

One simulated football game feeds every market: the score, team play volume, the pass/rush split under
the simulated game script, every player's opportunity share, per-touch efficiency and touchdowns are drawn
on the SAME Monte Carlo rows, so a player's carries reconcile with the team's rush attempts, receiving
yards reconcile with passing yards, and one rushing-yard distribution prices the entire Kalshi ladder.

Layout
  data.py        bronze -> tidy point-in-time tables (team-game, player-game, per-carry, per-target)
  features.py    strictly-prior EWMA features, depth-chart rank at a cutoff, availability
  models.py      the fitted primitives: game environment, opportunity shares, efficiency
  simulate.py    the Monte Carlo engine and its coherence checks
  kalshi.py      one distribution -> every threshold; projection rows with football / market / reconciled p
  reconcile.py   market reconciliation weights (fitted out of sample, never a constant pulled from the air)
  backtest.py    walk-forward evaluation of the primitives and of the final distributions

Shadow only. Nothing here writes the incumbent ledger, the three-arm corpus or the recommendation ledger.
"""
SIM_VERSION = "sim-1.0.0"
