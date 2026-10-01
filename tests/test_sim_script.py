"""The game-script summary (nfl_edge/sim/script.py): environment -> team volume -> player opportunity -> efficiency,
read from the same simulated rows the contracts are priced from. Synthetic frames only (tests/sim_fixtures.py)."""
import copy
import os
import sys

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nfl_edge.pricing.game_env import ResidualBank  # noqa: E402
from nfl_edge.sim import simulate as S  # noqa: E402
from nfl_edge.sim.script import SCRIPT_VERSION, script_summary  # noqa: E402
import sim_fixtures as FX  # noqa: E402


@pytest.fixture(scope="module")
def sim():
    b, tf, pf = FX.synthetic_bundle(seed=1)
    rng = np.random.default_rng(3)
    n = 600
    bank = ResidualBank(rng.normal(0, 13, n), rng.normal(0, 13, n), np.repeat([2020, 2021, 2022], n // 3), ref_season=2023,
                        spread_lines=np.where(rng.random(n) < 0.5, 3.0, 2.5), total_lines=np.where(rng.random(n) < 0.5, 44.0, 44.5),
                        overtime=rng.random(n) < 0.06, results=rng.normal(0, 13, n), rng=np.random.default_rng(1))
    gi = FX.game_input(tf, pf)
    res = S.simulate(gi, b, n=6000, bank=bank)
    return gi, res


def test_the_summary_draws_no_random_number_and_changes_nothing(sim):
    gi, res = sim
    before = copy.deepcopy({k: {s: np.asarray(v).copy() for s, v in d.items() if hasattr(v, "__len__")} for k, d in res.team.items()})
    state = np.random.get_state()
    a = script_summary(res, gi, S.coherence_report(res))
    b = script_summary(res, gi, S.coherence_report(res))
    assert a == b, "deterministic"
    assert np.random.get_state()[1].tolist() == state[1].tolist(), "no global RNG consumed"
    for team, d in before.items():
        for s, v in d.items():
            assert np.array_equal(v, np.asarray(res.team[team][s])), "the simulated rows are untouched"


def test_the_hierarchy_is_complete(sim):
    gi, res = sim
    out = script_summary(res, gi, S.coherence_report(res))
    assert out["script_version"] == SCRIPT_VERSION and out["betting_authorized"] is False
    env = out["environment"]
    assert {"home_margin", "total", "p_one_score", "p_blowout_17plus", "p_home_win"} <= set(env)
    assert 0.0 <= env["p_blowout_17plus"] <= 1.0 and env["score_state_paths"].startswith("NOT_SIMULATED")
    for team, t in out["teams"].items():
        assert {"plays", "pass_att", "rush_att", "dropbacks"} <= set(t["volume"])
        assert t["players"], "player opportunity is reported"
        p = t["players"][0]
        assert {"targets", "carries", "target_share", "carry_share", "opportunity_cv"} <= set(p)


def test_the_score_state_proxy_is_conditional_on_the_final_margin(sim):
    """The volume model passes less when leading: the summary must show it, from the same rows."""
    gi, res = sim
    out = script_summary(res, gi, S.coherence_report(res))
    for team, t in out["teams"].items():
        lead, trail = t["by_final_margin"]["lead14+"], t["by_final_margin"]["trail14+"]
        if "pass_rate_mean" in lead and "pass_rate_mean" in trail:
            assert lead["pass_rate_mean"] < trail["pass_rate_mean"]


def test_shares_sum_to_at_most_one_per_team(sim):
    gi, res = sim
    out = script_summary(res, gi, S.coherence_report(res), top_players=50)
    for team, t in out["teams"].items():
        assert sum((p["target_share"] or {}).get("mean", 0) for p in t["players"]) <= 1.0 + 1e-6
        assert 0.0 <= t["target_concentration_hhi"] <= 1.0
