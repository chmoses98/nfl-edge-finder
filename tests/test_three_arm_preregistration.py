"""H-20260910-026 is preregistered. Its arms, weight, horizons, metrics and sample gate must not drift.

The value of a preregistered challenger is that nobody -- including us, after a bad Sunday -- can quietly move
the hybrid weight, add a subgroup, relax the game floor or redefine a metric until it looks better. The code's
constants live in ONE module (nfl_edge/arms/registry.py); these tests pin them to the registry entry.
"""
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from nfl_edge.arms import registry as R  # noqa: E402

H = json.load(open(os.path.join(ROOT, "research/hypothesis_registry/H-20260910-026.json")))
ARM_SOURCES = sorted(glob.glob(os.path.join(ROOT, "nfl_edge", "arms", "*.py")))


def test_hypothesis_is_registered_prospective_and_untested():
    assert H["status"] == "REGISTERED_PROSPECTIVE"
    assert H["oos_result"] is None
    assert H["result"].startswith("UNTESTED")


def test_the_three_primary_arms_are_exactly_these():
    assert R.PRIMARY_ARMS == ("CURRENT_MARKET_PRIOR", "DATA_ONLY", "HYBRID_30_DATA")
    for arm in R.PRIMARY_ARMS:
        assert arm in H["rationale"] or arm in H["features"]


def test_the_hybrid_weight_is_seventy_thirty_and_sums_to_one():
    assert R.HYBRID_WEIGHT_MARKET == 0.70 and R.HYBRID_WEIGHT_DATA == 0.30
    assert abs(R.HYBRID_WEIGHT_MARKET + R.HYBRID_WEIGHT_DATA - 1.0) < 1e-12
    assert "0.70" in H["features"] and "0.30" in H["features"]


def test_the_primary_horizons_and_the_verdict_floor_are_pinned():
    assert R.PRIMARY_HORIZONS_MIN == (1440, 360, 90, 30)
    assert "T-24h, T-6h, T-90m, T-30m" in H["target"]
    assert R.MIN_GAMES_FOR_VERDICT == 64
    assert "64 distinct games" in H["test_plan"]


def test_forty_thousand_simulation_rows_are_the_standard():
    assert R.N_SIMS == 40000


def test_the_primary_metrics_are_named_in_the_registry():
    pre = R.preregistration()
    for m in ("margin_rmse", "margin_mae", "total_rmse", "total_mae"):
        assert m in pre["primary_game_center_metrics"]
    assert "RMSE" in H["target"] and "MAE" in H["target"] and "Brier" in H["target"] and "close" in H["target"]


def test_the_preregistration_hash_is_stable():
    """Any change to a preregistered constant changes this hash; the manifest of every snapshot records it."""
    assert R.preregistration_sha() == "ef0a095ace1ec698"


def test_no_hybrid_weight_grid_or_optimiser_exists_in_the_arms_package():
    """No sweep of weights, no optimiser, no per-game weight: the blend is one constant read from the registry."""
    import ast
    for path in ARM_SOURCES:
        src = open(path).read()
        assert "scipy.optimize" not in src and "minimize(" not in src, path
        if os.path.basename(path) == "registry.py":
            continue
        assert not re.search(r"weight[s]?\s*=\s*\[", src), f"{path} defines a list of weights"
        assert "linspace" not in src, f"{path} sweeps a grid"
        # no arithmetic with a literal blend weight anywhere in CODE (string literals such as the recorded formula are prose)
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
                for side in (node.left, node.right):
                    if isinstance(side, ast.Constant) and isinstance(side.value, float) and side.value in (0.3, 0.7, 0.30, 0.70):
                        raise AssertionError(f"{path}:{node.lineno} multiplies by a literal blend weight")


def test_the_evaluator_cannot_write_any_model_or_policy_artifact():
    """MEASURE, REPORT, DIAGNOSE -- never modify. The evaluation side opens nothing for writing under config/,
    research/ or the artifact path, and imports no gate, risk, or bridge module."""
    for name in ("scorecard.py", "evaluation.py", "report.py"):
        src = open(os.path.join(ROOT, "nfl_edge", "arms", name)).read()
        assert 'open(' not in src.replace("json.load(open(", ""), f"{name} opens a file"
        for forbidden in ("nfl_edge.handicap.gates", "nfl_edge.handicap.risk", "airtable", "config/risk_policy"):
            assert forbidden not in src, f"{name} references {forbidden}"


def test_the_already_completed_opener_is_excluded_by_the_registry_text():
    assert "2026_01_NE_SEA" in H["test_plan"] and "NOT challenger evidence" in H["test_plan"]
