"""Period engine: quarter extraction is contradiction-aware, the joint quarter simulation is coherent, questions route."""
import os
import sys

import numpy as np
import polars as pl
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.engines import period as PE                                                    # noqa: E402
from nfl_edge.semantics.questions import EVENT, GAME, PERIOD, RANGE, THRESHOLD, COMPOSITE, PROVEN, Question  # noqa: E402
from nfl_edge.settlement.period_results import PeriodBook                                   # noqa: E402


def _pbp(tmp_path, rows):
    """A tiny play-by-play parquet: (game_id, play_id, qtr, posteam, home, away, post scores, finals)."""
    recs = []
    for gid, plays, hf, af in rows:
        for pid, qtr, pos, hp, ap in plays:
            recs.append({"game_id": gid, "play_id": pid, "qtr": qtr, "posteam": pos, "home_team": "H", "away_team": "A",
                         "posteam_score_post": (hp if pos == "H" else ap), "defteam_score_post": (ap if pos == "H" else hp),
                         "home_score": hf, "away_score": af, "season_type": "REG", "season": 2024, "week": 1})
    p = tmp_path / "pbp.parquet"
    pl.DataFrame(recs).write_parquet(p)
    return str(p)


def test_quarter_extraction_reproduces_final_and_flags_contradictions(tmp_path):
    good = ("2024_01_A_H", [(1, 1, "H", 7, 0), (2, 2, "A", 7, 3), (3, 3, "H", 14, 3), (4, 4, "A", 14, 10)], 14, 10)
    bad = ("2024_01_B_H", [(1, 1, "H", 7, 0), (2, 2, "A", 7, 3), (3, 3, "H", 14, 3), (4, 4, "A", 14, 10)], 17, 10)   # schedule says 17
    path = _pbp(tmp_path, [good, bad])
    w = PE.quarter_scores_from_pbp(path)
    r = {x["game_id"]: x for x in w.iter_rows(named=True)}
    assert (r["2024_01_A_H"]["hq1"], r["2024_01_A_H"]["hq2"], r["2024_01_A_H"]["hq3"], r["2024_01_A_H"]["hq4"]) == (7, 0, 7, 0)
    assert r["2024_01_A_H"]["home_reg"] == 14 and r["2024_01_A_H"]["away_reg"] == 10
    book = PeriodBook()
    book.load_pbp(path, finals={"2024_01_A_H": (14, 10, 0), "2024_01_B_H": (17, 10, 0)})
    assert book.get("2024_01_A_H").inconsistency is None
    assert "schedule final is 17-10" in book.get("2024_01_B_H").inconsistency
    assert book.get("2024_01_A_H").period_points("1H", "home") == 7 and book.get("2024_01_A_H").period_points("2H", "away") == 7


def test_overtime_game_is_not_flagged_when_regulation_differs_from_final(tmp_path):
    ot = ("2024_01_C_H", [(1, 1, "H", 7, 0), (2, 2, "A", 7, 7), (3, 3, "H", 7, 7), (4, 4, "A", 7, 7), (5, 5, "H", 10, 7)], 10, 7)
    book = PeriodBook()
    book.load_pbp(_pbp(tmp_path, [ot]), finals={"2024_01_C_H": (10, 7, 1)})
    pr = book.get("2024_01_C_H")
    assert pr.complete and pr.inconsistency is None and pr.home_reg == 7


def _bank(n=400, seed=0):
    rng = np.random.default_rng(seed)
    spread = rng.choice(np.arange(-10, 10.5, 0.5), n); total = rng.choice(np.arange(38, 54, 0.5), n)
    hi, ai = (total + spread) / 2, (total - spread) / 2
    q = {}
    for side, base in (("h", hi), ("a", ai)):
        for k in range(1, 5):
            q[f"{side}q{k}"] = np.clip(np.round(rng.normal(base / 4, 4.5)), 0, None)
    d = {"season": rng.choice([2021, 2022, 2023], n), "spread_line": spread, "total_line": total, "overtime": np.zeros(n),
         "home_implied": hi, "away_implied": ai, **q}
    d["result"] = sum(q[f"hq{k}"] for k in range(1, 5)) - sum(q[f"aq{k}"] for k in range(1, 5))
    return PE.PeriodBank(pl.DataFrame(d), ref_season=2024)


def test_simulation_is_integer_nonnegative_and_full_game_is_the_sum_of_quarters_plus_overtime():
    b = _bank()
    sim = b.simulate(3.0, 44.5, n=5000, rng=np.random.default_rng(1))
    for c in PE.COLS:
        assert np.all(sim[c] >= 0) and np.all(sim[c] == np.round(sim[c]))
    assert np.allclose(sim["home_reg"], sum(sim["h" + q] for q in PE.QUARTERS))
    reg_tied = (sim["home_reg"] == sim["away_reg"])
    assert np.all(sim["home"][~reg_tied] == sim["home_reg"][~reg_tied]), "overtime only touches regulation ties"
    assert abs(np.mean(sim["margin"]) - 3.0) < 1.5 and abs(np.mean(sim["total"]) - 44.5) < 4.0


def test_period_winner_partition_sums_to_one_and_ladders_are_monotone():
    sim = _bank().simulate(-2.5, 47.0, n=6000, rng=np.random.default_rng(2))
    win_h = PE.answer(sim, Question(kind=EVENT, engine=PERIOD, stat="margin", period="1H", subject="H", subject_kind="team", event="WIN", semantic_confidence=PROVEN), "H", "A")
    win_a = PE.answer(sim, Question(kind=EVENT, engine=PERIOD, stat="margin", period="1H", subject="A", subject_kind="team", event="WIN", semantic_confidence=PROVEN), "H", "A")
    tie = PE.answer(sim, Question(kind=EVENT, engine=PERIOD, stat="margin", period="1H", event="TIE", semantic_confidence=PROVEN), "H", "A")
    assert win_h["p_yes"] + win_a["p_yes"] + tie["p_yes"] == pytest.approx(1.0)
    ps = [PE.answer(sim, Question(kind=THRESHOLD, engine=PERIOD, stat="total", period="1Q", op=">=", k=k, semantic_confidence=PROVEN), "H", "A")["p_yes"] for k in range(3, 25)]
    assert all(a >= b for a, b in zip(ps, ps[1:]))
    bucket = PE.answer(sim, Question(kind=RANGE, engine=PERIOD, stat="margin", period="1H", subject="H", lo=1, hi=6, semantic_confidence=PROVEN), "H", "A")
    assert 0 < bucket["p_yes"] < win_h["p_yes"]


def test_period_engine_refuses_game_engine_questions_and_unknown_periods():
    sim = _bank().simulate(0.0, 44.0, n=1000)
    assert PE.answer(sim, Question(kind=THRESHOLD, engine=GAME, stat="total", period="FULL", op=">=", k=44, semantic_confidence=PROVEN), "H", "A")["p_yes"] is None
    assert PE.answer(sim, Question(kind=THRESHOLD, engine=PERIOD, stat="total", period="OT", op=">=", k=3, semantic_confidence=PROVEN), "H", "A")["p_yes"] is None


def test_composite_half_full_is_evaluated_on_shared_draws_not_multiplied():
    sim = _bank().simulate(6.0, 45.0, n=8000, rng=np.random.default_rng(3))
    l1 = Question(kind=EVENT, engine=PERIOD, stat="margin", period="1H", subject="H", event="WIN", semantic_confidence=PROVEN)
    l2 = Question(kind=EVENT, engine=GAME, stat="margin", period="FULL", subject="H", event="WIN", semantic_confidence=PROVEN)
    joint = PE.answer(sim, Question(kind=COMPOSITE, engine="JOINT", legs=(l1, l2), semantic_confidence=PROVEN), "H", "A")["p_yes"]
    p1, p2 = PE.answer(sim, l1, "H", "A")["p_yes"], float(np.mean(PE.indicator(sim, l2, "H", "A")))
    assert joint > p1 * p2 + 0.02, "a favourite leading at the half and winning are positively dependent; the product understates it"
    assert joint <= min(p1, p2) + 1e-12


def test_cross_engine_gap_reports_both_sides():
    b = _bank()
    sim = b.simulate(3.0, 44.5, n=2000)
    gap = PE.cross_engine_gap(sim, {"margin": sim["margin"], "total": sim["total"]})
    assert set(gap) == {"period_engine", "game_engine", "diff"} and gap["diff"]["mean_margin"] == pytest.approx(0.0)
