"""Coherence audit (mid is research, executable is bid/ask after ONE fee), joint mapping, season Monte Carlo."""
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.engines import coherence as CE, game as GE, joint as JE, season as SE   # noqa: E402
from nfl_edge.execution import fees as F                                              # noqa: E402
from nfl_edge.semantics.questions import (COMPOSITE, EVENT, GAME, PLAYER, PROVEN, RANGE, THRESHOLD, Question)  # noqa: E402

AS_OF = datetime(2026, 9, 12, 12, tzinfo=timezone.utc)


def margin_legs(mids, width=0.02):
    legs, ks = [], [(1, 6), (7, 14), (15, None)]
    for team in ("H", "A"):
        for (lo, hi), m in zip(ks, mids[team]):
            legs.append({"ticker": f"{team}{lo}", "series_ticker": "KXNFLWINMARGIN", "yes_bid": m - width / 2, "yes_ask": m + width / 2,
                         "question": Question(kind=RANGE, engine=GAME, stat="margin", subject=team, lo=lo, hi=hi, semantic_confidence=PROVEN)})
    legs.append({"ticker": "TIE", "series_ticker": "KXNFLWINMARGIN", "yes_bid": mids["TIE"] - width / 2, "yes_ask": mids["TIE"] + width / 2,
                 "question": Question(kind=EVENT, engine=GAME, stat="margin", event="TIE", semantic_confidence=PROVEN)})
    return legs


def test_margin_partition_is_collectively_exhaustive_and_mid_sum_is_research_only():
    sched = F.load_fee_schedule(ROOT)
    legs = margin_legs({"H": [0.20, 0.22, 0.15], "A": [0.18, 0.15, 0.10], "TIE": 0.02})   # sums to 1.02
    r = CE.audit_group("WIN_MARGIN_BUCKET", "E", legs, sched, AS_OF)
    assert r["set_kind"] == CE.COLLECTIVELY_EXHAUSTIVE and r["research_incoherence"] == pytest.approx(0.02)
    assert r["executable_opportunity"] is None, "a 2c mid overround is not an executable opportunity"
    assert r["cost_buy_all_after_fees"] > r["sum_ask"] and r["pay_sell_all_after_fees"] < r["sum_bid"], "fees move both sides the right way"


def test_fee_is_applied_exactly_once_per_leg():
    sched = F.load_fee_schedule(ROOT)
    legs = margin_legs({"H": [0.20, 0.22, 0.15], "A": [0.18, 0.15, 0.10], "TIE": 0.02})
    r = CE.audit_group("WIN_MARGIN_BUCKET", "E", legs, sched, AS_OF)
    expect = sum(-float(F.net_executable_ev(l["yes_ask"], l["yes_ask"], 1.0, sched, series_ticker="KXNFLWINMARGIN", as_of=AS_OF).net_ev_dollars) for l in legs)
    assert r["fees_buy_all"] == pytest.approx(expect)
    assert r["cost_buy_all_after_fees"] == pytest.approx(r["sum_ask"] + expect)


def test_executable_opportunity_only_when_buying_every_leg_costs_under_a_dollar_after_fees():
    sched = F.load_fee_schedule(ROOT)
    legs = margin_legs({"H": [0.10, 0.10, 0.10], "A": [0.10, 0.10, 0.10], "TIE": 0.02})   # asks sum to ~0.69
    r = CE.audit_group("WIN_MARGIN_BUCKET", "E", legs, sched, AS_OF)
    assert r["executable_opportunity"] == "BUY_ALL" and r["cost_buy_all_after_fees"] < 1.0
    legs[0]["yes_ask"] = None                                                                 # one leg loses its ask
    r2 = CE.audit_group("WIN_MARGIN_BUCKET", "E", legs, sched, AS_OF)
    assert r2["executable_opportunity"] is None and "two-sided" in r2["executable_reason"]


def test_partial_and_ambiguous_sets_never_claim_incoherence():
    sched = F.load_fee_schedule(ROOT)
    legs = margin_legs({"H": [0.20, 0.22, 0.15], "A": [0.18, 0.15, 0.10], "TIE": 0.02})[:-1]   # no tie leg
    r = CE.audit_group("WIN_MARGIN_BUCKET", "E", legs, sched, AS_OF)
    assert r["set_kind"] == CE.MUTUALLY_EXCLUSIVE and r["executable_opportunity"] is None
    legs[1]["question"] = Question(kind=RANGE, engine=GAME, stat="margin", subject="H", lo=3, hi=14, semantic_confidence=PROVEN)   # overlaps 1-6
    r = CE.audit_group("WIN_MARGIN_BUCKET", "E", legs, sched, AS_OF)
    assert r["set_kind"] == CE.AMBIGUOUS and r["research_incoherence"] is None


def test_joint_routes_score_legs_to_the_shared_simulation_and_refuses_player_legs():
    rng = np.random.default_rng(0)
    margin = np.round(rng.normal(3, 13, 20000)); total = np.round(rng.normal(45, 13, 20000))
    sim = {"margin": margin, "total": total, "home": (total + margin) / 2, "away": (total - margin) / 2}
    l1 = Question(kind=EVENT, engine=GAME, stat="margin", period="FULL", subject="H", event="WIN", semantic_confidence=PROVEN)
    l2 = Question(kind=THRESHOLD, engine=GAME, stat="margin", period="FULL", subject="H", op=">", k=6.5, semantic_confidence=PROVEN)
    q = Question(kind=COMPOSITE, engine="JOINT", legs=(l1, l2), semantic_confidence=PROVEN)
    assert JE.classify_legs(q)["route"] == "game"
    a = JE.answer(q, game_sim=sim, period_sim=None, home="H", away="A")
    p2 = GE.answer(sim, l2, "H", "A")["p_yes"]
    assert a["p_yes"] == pytest.approx(p2), "winning by 7+ implies winning: the joint is the tighter leg, not the product"
    prod = JE.independence_product(q, {0: GE.answer(sim, l1, "H", "A")["p_yes"], 1: p2})["product"]
    assert prod < a["p_yes"]
    lp = Question(kind=THRESHOLD, engine=PLAYER, stat="receiving_yards", subject="00-001", op=">=", k=50, semantic_confidence=PROVEN)
    r = JE.answer(Question(kind=COMPOSITE, engine="JOINT", legs=(l1, lp), semantic_confidence=PROVEN), game_sim=sim, period_sim=None, home="H", away="A")
    assert r["status"] == JE.JOINT_MODEL_REQUIRED and r["p_yes"] is None


def test_season_simulation_conserves_wins_and_seeds_seven_per_conference():
    sched = [{"game_id": f"g{i}", "home": h, "away": a, "week": 1 + i % 17} for i, (h, a) in enumerate(
        [(x, y) for x in SE.TEAM_DIV for y in SE.TEAM_DIV if x < y][:200])]
    sim = SE.simulate_seasons(sched, {}, {}, n=500, seed_key="t")
    assert np.all(sim["wins"].sum(axis=1) + 0.5 * sim["ties"].sum(axis=1) == len(sched))
    teams = sim["teams"]
    for conf in ("AFC", "NFC"):
        idx = [i for i, t in enumerate(teams) if SE.CONF[t] == conf]
        assert np.all(sim["playoffs"][:, idx].sum(axis=1) == 7)
    for d, ts in SE.DIVISIONS.items():
        idx = [teams.index(t) for t in ts]
        assert np.all(sim["div_winner"][:, idx].sum(axis=1) == 1)
    q = Question(kind=THRESHOLD, engine="SEASON", stat="season_wins", subject="KC", op=">=", k=1, semantic_confidence="LIKELY")
    a = SE.answer(sim, q)
    assert 0 <= a["p_yes"] <= 1
    assert SE.answer(sim, Question(kind=EVENT, engine="SEASON", stat="season_wins", subject="XXX", event="MAKE_PLAYOFFS"))["p_yes"] is None
    again = SE.simulate_seasons(sched, {}, {}, n=500, seed_key="t")
    assert np.array_equal(again["wins"], sim["wins"]), "deterministic for a given seed key"
