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
# sim-1.1.0 adds the DISTRIBUTION SUMMARY to every player/stat row: the football distribution's own
# p05/p25/p50/p75/p95 (and the market's and the reconciled one's median) read straight off the
# LatticeDistribution that priced the ladder, plus the ledger player name for identity.  Nothing about the
# engine, the models, the reconciliation weights or any probability changed -- sim-1.0.0 already computed
# these quantiles internally and simply never persisted them, so a reader had a mean and an sd and no
# median.  The bump is a minor one because the addition is purely additive: every sim-1.0.0 field keeps its
# name and its meaning, and a sim-1.0.0 artifact stays readable (its quantiles are reported as unavailable
# rather than inferred -- see `handicap.sim_block`).
SIM_VERSION = "sim-1.1.0"
