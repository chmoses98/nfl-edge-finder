import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pytest
from tennis_edge.futures.draw import simulate_draw, check_invariants, DrawError


def elo_p(r):
    def p(a, b, rnd):
        return 1.0 / (1.0 + 10 ** ((r[b] - r[a]) / 400.0))
    return p


def test_bracket_dp_invariants_and_bye():
    slots = ["A", None, "C", "D", "E", "F", "G", "H"]
    r = {"A": 2200, "C": 2000, "D": 1900, "E": 2100, "F": 1800, "G": 1950, "H": 1700}
    res = simulate_draw(slots, elo_p(r))
    assert check_invariants(res) == []
    assert abs(res["reach"]["A"]["SF"] - 1.0) < 1e-12 or abs(res["reach"]["A"].get("SF", 0) - 1.0) < 1e-12 or res["reach"]["A"]["QF"] == 1.0
    assert res["title"]["A"] == max(res["title"].values())
    assert abs(sum(res["title"].values()) - 1) < 1e-12


def test_withdrawal_and_tbd():
    slots = ["A", "B", "C", "D"]
    r = {"A": 2000, "B": 2000, "C": 2000, "D": 2000}
    res = simulate_draw(slots, elo_p(r), withdrawals={"B"})
    assert "B" not in res["title"] and abs(res["reach"]["A"]["F"] - 1.0) < 1e-12
    with pytest.raises(DrawError):
        simulate_draw(["A", "TBD", "C", "D"], elo_p(r))
    with pytest.raises(DrawError):
        simulate_draw(["A", "B", "C"], elo_p(r))


def test_matches_brute_force_two_rounds():
    slots = ["A", "B", "C", "D"]
    r = {"A": 2100, "B": 1900, "C": 2000, "D": 2050}
    p = elo_p(r)
    res = simulate_draw(slots, p)
    pa = p("A", "B", "SF") * (p("C", "D", "SF") * p("A", "C", "F") + p("D", "C", "SF") * p("A", "D", "F"))
    assert abs(res["title"]["A"] - pa) < 1e-12
