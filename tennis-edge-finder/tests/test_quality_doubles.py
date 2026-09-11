import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tennis_edge.models.quality import QualityInputs, data_quality
from tennis_edge.doubles.model import DoublesBaseline, team_key


def test_quality_ordering():
    rich = data_quality(QualityInputs(200, 150, 8000, 6000, 5, 10, 1.0, 1.0, True))
    poor = data_quality(QualityInputs(9, 4, 0, 0, 120, 200, 0.2, 0.9, True))
    assert rich["data_quality_score"] > 0.8 > poor["data_quality_score"]
    assert data_quality(QualityInputs(200, 150, 8000, 6000, 5, 10, 1.0, 1.0, False))["data_quality_score"] == 0.0
    assert rich["grade"] == "A" and poor["grade"] in ("D", "F")


def test_doubles_interface():
    assert team_key("b", "a") == team_key("a", "b") == "a|b"
    m = DoublesBaseline(doubles_elo={"a": 1600, "b": 1500}, singles_elo={"c": 1700})
    r = m.predict(("a", "b"), ("c", "d"))
    assert 0 < r["p_a"] < 1 and r["unvalidated"] and r["basis_b"]["basis"] == "SINGLES_ONLY"
