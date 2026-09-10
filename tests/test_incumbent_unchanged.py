"""The incumbent is the control. This PR must not have moved it, and this file is how a reviewer can tell.

Two kinds of pin. GOLDEN OUTPUTS: the incumbent simulator and pricer on a fixed synthetic bank and seed produce
exactly these numbers (computed on `main` before the three-arm work). SOURCE HASHES: the modules that hold the
incumbent's game centre, settlement semantics and the real-money gates are byte-identical to `main`. A future
change to any of them is legitimate only as a deliberate, reviewed edit that updates the pin beside it.
"""
import hashlib
import os

import numpy as np

from nfl_edge.pricing.game_env import ResidualBank, price_game_markets, simulate_game

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GOLDEN = {"margin_sha": "cbb761cb4325c794", "total_sha": "199dba761099c280",
          "home_win": 0.75335, "total_ge_45": 0.428475, "teamtotal_SEA_ge_24": 0.546975}
SOURCE_PINS = {
    "nfl_edge/pricing/game_env.py": "b880dc755311d928",          # the residual bank + 40,000-row joint simulation
    "nfl_edge/pricing/market_implied.py": "81c47febf9a96a6d",    # the Kalshi-implied centre estimator
    "nfl_edge/settlement/semantics.py": "e877fba94b93a122",      # contract value vs event probability
    "nfl_edge/handicap/gates.py": "00f51f86f39eda17",            # the real-money gates
    "nfl_edge/handicap/risk.py": "e8ba8fd37f0d01a3",             # the risk policy engine
    "nfl_edge/handicap/schema.py": "1ea7b6c31b15d03e",           # recommendation schema, availability rules, ceilings
    "nfl_edge/handicap/preflight.py": "7910ea5b70ce8d38",        # the pre-trade check
    "config/risk_policy.json": "11d24fbea908f9ed",               # risk limits
}


def _bank():
    rng = np.random.default_rng(0); n = 4000
    seasons = rng.integers(2016, 2026, n); spreads = rng.choice([-7, -3.5, -3, -1.5, 0, 1, 2.5, 3, 3.5, 7], n)
    totals = rng.choice([41.5, 44, 45.5, 47, 49.5], n); home = rng.poisson(23, n); away = rng.poisson(21, n); result = home - away
    overtime = (np.abs(result) <= 3) & (rng.random(n) < 0.15)
    return ResidualBank(result - spreads, home + away - totals, seasons, ref_season=2026, spread_lines=spreads, total_lines=totals,
                        overtime=overtime, results=result, halflife=3.0, rng=np.random.default_rng(11))


def test_the_incumbent_game_centre_simulation_is_bit_identical_to_main():
    sim = simulate_game(3.5, 44.5, _bank(), n=40000)
    assert hashlib.sha256(sim["margin"].tobytes()).hexdigest()[:16] == GOLDEN["margin_sha"]
    assert hashlib.sha256(sim["total"].tobytes()).hexdigest()[:16] == GOLDEN["total_sha"]
    p = price_game_markets(sim, "SEA", "NE")
    for k in ("home_win", "total_ge_45", "teamtotal_SEA_ge_24"):
        assert round(p[k], 6) == GOLDEN[k]


def test_the_incumbent_centre_settlement_and_gate_sources_are_unchanged():
    for rel, pin in SOURCE_PINS.items():
        got = hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()[:16]
        assert got == pin, f"{rel} changed ({got} != {pin}); the incumbent/recommendation policy must not move in this PR"


def test_the_pricer_still_uses_forty_thousand_rows_and_the_same_bank_rule():
    src = open(os.path.join(ROOT, "scripts", "shadow", "price_slate.py")).read()
    assert "sim = simulate_game(s_use, t_use, bank, n=40000)" in src
    assert "halflife=3.0, rng=np.random.default_rng(11)" in src
    assert "nsims=12000" in src and "np.arange(-17, 17.5, 0.5)" in src
