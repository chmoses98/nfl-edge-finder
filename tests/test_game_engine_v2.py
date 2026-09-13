"""Game engine v2: generic score-derived pricing is coherent and refuses what is not a score function."""
import os
import sys

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.engines import game as G  # noqa: E402
from nfl_edge.semantics.questions import PROVEN, Question  # noqa: E402


def _sim(n=20000, seed=0):
    rng = np.random.default_rng(seed)
    home = rng.poisson(24, n).astype(float); away = rng.poisson(20, n).astype(float)
    return {"margin": home - away, "total": home + away, "home": home, "away": away}


def _q(kind, stat, **kw):
    return Question(kind=kind, engine="GAME", stat=stat, period="FULL", semantic_confidence=PROVEN, **kw)


def test_incumbent_family_answers_reproduce_the_five_branches():
    sim = _sim()
    m, t, h, a = sim["margin"], sim["total"], sim["home"], sim["away"]
    assert G.answer(sim, _q("THRESHOLD", "margin", subject="H", op=">", k=7.5), "H", "A")["p_yes"] == pytest.approx(np.mean(m > 7.5))
    assert G.answer(sim, _q("THRESHOLD", "margin", subject="A", op=">", k=-3.5), "H", "A")["p_yes"] == pytest.approx(np.mean(-m > -3.5))
    assert G.answer(sim, _q("THRESHOLD", "total", op=">=", k=45), "H", "A")["p_yes"] == pytest.approx(np.mean(t >= 45))
    assert G.answer(sim, _q("THRESHOLD", "team_points", subject="A", op=">=", k=21), "H", "A")["p_yes"] == pytest.approx(np.mean(a >= 21))
    assert G.answer(sim, _q("THRESHOLD", "min_team_points", op=">=", k=17), "H", "A")["p_yes"] == pytest.approx(np.mean((h >= 17) & (a >= 17)))
    win = G.answer(sim, _q("EVENT", "margin", subject="H", event="WIN", tie_rule="HALF_PAYOUT"), "H", "A")
    assert win["p_yes"] == pytest.approx(np.mean(m > 0)) and win["contract_value"] == pytest.approx(np.mean(m > 0) + 0.5 * np.mean(m == 0))


def test_margin_buckets_partition_and_sum_to_one():
    sim = _sim()
    qs = {"H16": _q("RANGE", "margin", subject="H", lo=1, hi=6), "H714": _q("RANGE", "margin", subject="H", lo=7, hi=14),
          "H15": _q("RANGE", "margin", subject="H", lo=15, hi=None), "A16": _q("RANGE", "margin", subject="A", lo=1, hi=6),
          "A714": _q("RANGE", "margin", subject="A", lo=7, hi=14), "A15": _q("RANGE", "margin", subject="A", lo=15, hi=None),
          "TIE": _q("EVENT", "margin", event="TIE")}
    ans = G.price_questions(sim, qs, "H", "A")
    assert sum(v["p_yes"] for v in ans.values()) == pytest.approx(1.0, abs=1e-12)
    mass = G.bucket_partition_mass(sim, "H", "A", qs)
    assert mass["collectively_exhaustive"]
    assert G.check_coherence(qs, ans)["ok"]
    # the 2025 either-team structure on the same simulation
    either = {"E13": _q("RANGE", "abs_margin", lo=1, hi=3), "E46": _q("RANGE", "abs_margin", lo=4, hi=6)}
    a2 = G.price_questions(sim, either, "H", "A")
    assert a2["E13"]["p_yes"] == pytest.approx(np.mean((np.abs(sim["margin"]) >= 1) & (np.abs(sim["margin"]) <= 3)))


def test_ladders_are_monotone_and_the_checker_catches_violations():
    sim = _sim()
    qs = {f"T{k}": _q("THRESHOLD", "total", op=">=", k=k) for k in range(30, 70)}
    ans = G.price_questions(sim, qs, "H", "A")
    ps = [ans[f"T{k}"]["p_yes"] for k in range(30, 70)]
    assert all(a >= b for a, b in zip(ps, ps[1:]))
    assert G.check_coherence(qs, ans)["ok"]
    broken = dict(ans); broken["T50"] = dict(ans["T50"], p_yes=ans["T49"]["p_yes"] + 0.05)
    rep = G.check_coherence(qs, broken)
    assert not rep["ok"] and rep["problems"][0]["type"] == "ladder_non_monotone"


def test_refuses_questions_that_are_not_score_functions():
    sim = _sim()
    for q in (_q("EVENT", "race", subject="H", event="RACE_FIRST", k=10), _q("EVENT", "first_td", subject="H", event="FIRST_TD_TEAM"),
              _q("THRESHOLD", "total_touchdowns", op=">=", k=5)):
        a = G.answer(sim, q, "H", "A")
        assert a["p_yes"] is None and a["reason"]
    period = Question(kind="THRESHOLD", engine="PERIOD", stat="total", period="1H", op=">=", k=20, semantic_confidence=PROVEN)
    assert G.answer(sim, period, "H", "A")["p_yes"] is None


def test_composite_legs_are_integrated_jointly_not_multiplied():
    sim = _sim()
    a = _q("THRESHOLD", "total", op=">=", k=45); b = _q("THRESHOLD", "margin", subject="H", op=">", k=3.5)
    comp = Question(kind="COMPOSITE", engine="JOINT", period="FULL", legs=(a, b), semantic_confidence=PROVEN)
    joint = G.answer(sim, comp, "H", "A")["p_yes"]
    pa = G.answer(sim, a, "H", "A")["p_yes"]; pb = G.answer(sim, b, "H", "A")["p_yes"]
    assert joint == pytest.approx(np.mean((sim["total"] >= 45) & (sim["margin"] > 3.5)))
    assert joint != pytest.approx(pa * pb, abs=1e-3)      # the legs are dependent on this simulation


def test_probabilities_are_in_unit_interval_and_subject_must_be_in_game():
    sim = _sim()
    a = G.answer(sim, _q("THRESHOLD", "margin", subject="X", op=">", k=0), "H", "A")
    assert a["p_yes"] is None
    for q in (_q("THRESHOLD", "total", op=">=", k=-5), _q("THRESHOLD", "total", op=">=", k=500)):
        p = G.answer(sim, q, "H", "A")["p_yes"]
        assert 0.0 <= p <= 1.0
