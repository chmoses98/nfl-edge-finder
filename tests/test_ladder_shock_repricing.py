"""The margin-distribution reconstruction, pinned.

Three things can silently corrupt a structural repricing study and none of them raise: composing the away
side without complementing it, letting a stale quote stand in for "the price at t", and reading a quote from
after the timestamp being reconstructed. Each is tested directly.
"""
import importlib.util
import os
import sys

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
_spec = importlib.util.spec_from_file_location(
    "lsr", os.path.join(ROOT, "scripts", "research", "ladder_shock_repricing.py"))
lsr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lsr)


def _flat(price, ts_list):
    return [(t, price) for t in ts_list]


def test_away_rungs_enter_as_complements():
    """An away rung at strike s is P(-M > s); on the home axis that is S(-s) = 1 - quote."""
    ts = [1000]
    rungs = [("HOME", 3.5, _flat(0.60, ts)), ("AWAY", 3.5, _flat(0.25, ts))]
    xs, S = lsr.survival_curve(rungs + [("HOME", 6.5, _flat(0.40, ts)),
                                        ("AWAY", 6.5, _flat(0.10, ts)),
                                        ("HOME", 9.5, _flat(0.30, ts)),
                                        ("AWAY", 9.5, _flat(0.05, ts))], "HOME", 1000)
    d = dict(zip(xs.tolist(), S.tolist()))
    assert d[3.5] == pytest.approx(0.60)
    assert d[-3.5] == pytest.approx(0.75), "away quote 0.25 must appear as S(-3.5) = 0.75"
    assert d[-9.5] == pytest.approx(0.95)


def test_curve_is_monotone_decreasing():
    ts = [1000]
    # deliberately non-monotone input: S(6.5) quoted above S(3.5)
    rungs = [("HOME", 3.5, _flat(0.40, ts)), ("HOME", 6.5, _flat(0.55, ts)),
             ("HOME", 9.5, _flat(0.20, ts)), ("AWAY", 3.5, _flat(0.30, ts)),
             ("AWAY", 6.5, _flat(0.15, ts)), ("AWAY", 9.5, _flat(0.05, ts))]
    xs, S = lsr.survival_curve(rungs, "HOME", 1000)
    assert np.all(np.diff(S) <= 1e-12), f"survival curve is not monotone decreasing: {S}"


def test_quote_at_never_looks_forward():
    series = [(100, 0.10), (200, 0.90)]
    assert lsr.quote_at(series, 150) == pytest.approx(0.10), "used a quote from the future"
    assert lsr.quote_at(series, 99) is None


def test_stale_quotes_are_refused():
    series = [(0, 0.42)]
    assert lsr.quote_at(series, lsr.MAX_STALE_S - 1) == pytest.approx(0.42)
    assert lsr.quote_at(series, lsr.MAX_STALE_S + 1) is None, "a stale quote stood in for the price at t"


def test_thin_ladders_are_refused():
    ts = [1000]
    rungs = [("HOME", 3.5, _flat(0.5, ts)), ("HOME", 6.5, _flat(0.4, ts))]
    assert lsr.survival_curve(rungs, "HOME", 1000) is None, \
        f"a {len(rungs)}-rung ladder cannot pin location, scale and tail"


def test_summarise_recovers_a_symmetric_distribution():
    """A curve centred on zero must give location 0, and a positive interquartile width."""
    xs = np.array([-13.5, -9.5, -6.5, -3.5, 3.5, 6.5, 9.5, 13.5])
    S = np.array([0.95, 0.85, 0.72, 0.60, 0.40, 0.28, 0.15, 0.05])
    out = lsr.summarise((xs, S))
    assert out["location"] == pytest.approx(0.0, abs=1e-9)
    assert out["scale"] > 0
    assert out["tail"] == pytest.approx(0.05 + (1 - 0.95))


def test_tail_is_not_extrapolated_beyond_quoted_strikes():
    """If no rung reaches the blowout threshold the tail is unknown, not guessed."""
    xs = np.array([-6.5, -3.5, 3.5, 6.5])
    S = np.array([0.80, 0.62, 0.38, 0.20])
    out = lsr.summarise((xs, S))
    assert out["location"] == pytest.approx(0.0, abs=1e-9)
    assert out["tail"] is None, "tail was extrapolated past the widest quoted strike"


def test_preregistered_gate_is_strict_enough_to_block_the_2025_sample():
    """2025 offers ~14 treated and 4 control games. The gate must refuse to draw a verdict from that."""
    assert lsr.MIN_TREATED_GAMES >= 40 and lsr.MIN_CONTROL_GAMES >= 40
