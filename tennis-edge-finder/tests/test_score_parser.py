import math

import pytest

from tennis_edge.rules.score_parser import (
    COMPLETED, DEFAULT, RETIRED, UNFINISHED, UNKNOWN, WALKOVER, ScoreParse, is_valid_score, parse_score,
)


# (raw, outcome, completed, sets_w, sets_l, games_w, games_l, tiebreaks, parse_error)
CASES = [
    ("6-4 6-4", COMPLETED, True, 2, 0, 12, 8, 0, False),
    ("7-6(5) 3-6 6-3", COMPLETED, True, 2, 1, 16, 15, 1, False),
    ("6-7(7) 7-6(3) 7-6(10)", COMPLETED, True, 2, 1, 20, 19, 3, False),
    ("6-4 3-6 [10-8]", COMPLETED, True, 2, 1, 9, 10, 0, False),
    ("6-3 RET", RETIRED, False, 1, 0, 6, 3, 0, False),
    ("3-6 6-4 2-1 RET", RETIRED, False, 1, 1, 11, 11, 0, False),
    ("W/O", WALKOVER, False, 0, 0, 0, 0, 0, False),
    ("DEF", DEFAULT, False, 0, 0, 0, 0, 0, False),
    ("6-4 6-4 6-4", COMPLETED, True, 3, 0, 18, 12, 0, False),
    ("4-6 6-3 6-4 ret.", RETIRED, False, 2, 1, 16, 13, 0, False),
    ("Walkover", WALKOVER, False, 0, 0, 0, 0, 0, False),
    ("6-0 6-0", COMPLETED, True, 2, 0, 12, 0, 0, False),
    ("7-5 6-7(10) 7-6(4)", COMPLETED, True, 2, 1, 20, 18, 2, False),
    ("6-4 6-4 (retired)", RETIRED, False, 2, 0, 12, 8, 0, False),
    ("", UNKNOWN, False, 0, 0, 0, 0, 0, False),
    ("In Progress", UNFINISHED, False, 0, 0, 0, 0, 0, False),
    ("UNP", UNKNOWN, False, 0, 0, 0, 0, 0, False),
    ("UNK", UNKNOWN, False, 0, 0, 0, 0, 0, False),
    ("2-6 6-3 7-6(12)", COMPLETED, True, 2, 1, 15, 15, 1, False),
    ("ABN", UNFINISHED, False, 0, 0, 0, 0, 0, False),
    ("abandoned", UNFINISHED, False, 0, 0, 0, 0, 0, False),
    ("Played and unfinished", UNFINISHED, False, 0, 0, 0, 0, 0, False),
    ("6-3 2-1 unfinished", UNFINISHED, False, 1, 0, 8, 4, 0, False),
    ("6-4 7-6", COMPLETED, True, 2, 0, 13, 10, 1, False),           # tiebreak detail omitted (older data)
    ("7-6(11-9) 6-3", COMPLETED, True, 2, 0, 13, 9, 1, False),       # both players' tiebreak points
    ("6-3 2-1 DEF", DEFAULT, False, 1, 0, 8, 4, 0, False),
    ("6-6(3) RET", RETIRED, False, 0, 0, 6, 6, 1, False),            # tiebreak in progress at retirement
    ("6-4, 6-4", COMPLETED, True, 2, 0, 12, 8, 0, False),            # comma separated
    ("7-6 (5) 6-2", COMPLETED, True, 2, 0, 13, 8, 1, False),         # space before tiebreak parenthesis
    ("6–4 6–4", COMPLETED, True, 2, 0, 12, 8, 0, False),   # en-dash
    # invalid / impossible
    ("6-4 6-5", UNKNOWN, False, 1, 0, 12, 9, 0, True),
    ("6-4 4-6 6-4 4-6", UNKNOWN, False, 2, 2, 20, 20, 0, True),
    ("6-4 6-4 4-6", UNKNOWN, False, 2, 1, 16, 14, 0, True),           # superfluous set after decision
    ("6-2 6-2 6-2 6-2", UNKNOWN, False, 4, 0, 24, 8, 0, True),
    ("6-4(3) 6-2", UNKNOWN, False, 1, 0, 12, 6, 0, True),             # tiebreak on a non-tiebreak set
    ("9-6 6-4", UNKNOWN, False, 1, 0, 15, 10, 0, True),               # >7 with margin != 2
    ("Jun 27", UNKNOWN, False, 0, 0, 0, 0, 0, True),
    ("6-4 2-1 6-3", UNKNOWN, False, 2, 0, 14, 8, 0, True),            # incomplete set that is not last
]


@pytest.mark.parametrize("raw,outcome,completed,sw,sl,gw,gl,tb,err", CASES, ids=[c[0] or "<empty>" for c in CASES])
def test_parse_cases(raw, outcome, completed, sw, sl, gw, gl, tb, err):
    r = parse_score(raw)
    assert isinstance(r, ScoreParse)
    assert r.outcome_type == outcome
    assert r.completed is completed
    assert (r.sets_w, r.sets_l) == (sw, sl)
    assert (r.games_w, r.games_l) == (gw, gl)
    assert r.tiebreaks_played == tb
    assert r.parse_error is err
    assert r.winner_is_first is True


def test_set_scores_and_tiebreak_points():
    r = parse_score("7-6(5) 3-6 6-3")
    assert r.set_scores == ((7, 6), (3, 6), (6, 3))
    assert r.tiebreak_loser_points == (5, None, None)
    assert r.raw == "7-6(5) 3-6 6-3"


def test_match_tiebreak_flags_and_games():
    r = parse_score("6-4 3-6 [10-8]")
    assert r.match_tiebreak_played is True
    assert r.match_tiebreak_flags == (False, False, True)
    assert r.set_scores[-1] == (10, 8)
    # games exclude the match tiebreak
    assert (r.games_w, r.games_l) == (9, 10)


def test_advantage_sets():
    assert parse_score("8-6 6-4").advantage_set is True
    assert parse_score("70-68 6-4").advantage_set is True
    assert parse_score("70-68 6-4").completed is True
    assert parse_score("6-4 6-4").advantage_set is False
    assert parse_score("9-6 6-4").parse_error is True


def test_incomplete_last_set_flags():
    r = parse_score("3-6 6-4 2-1 RET")
    assert r.last_set_incomplete is True
    assert parse_score("6-4 6-4").last_set_incomplete is False


def test_none_and_nan_inputs():
    assert parse_score(None).outcome_type == UNKNOWN
    assert parse_score(float("nan")).outcome_type == UNKNOWN
    assert parse_score(None).parse_error is False
    assert "EMPTY_SCORE" in parse_score("   ").notes


def test_error_reason_is_informative():
    assert parse_score("6-4 6-5").error_reason.startswith("INCOMPLETE_SET_WITHOUT_STATUS")
    assert parse_score("Jun 27").error_reason.startswith("UNPARSEABLE_TOKEN")
    assert parse_score("6-4(3) 6-2").error_reason.startswith("TIEBREAK_ON_NON_TIEBREAK_SET")


def test_is_valid_score_predicate():
    assert is_valid_score("6-4 6-4")
    assert is_valid_score("")
    assert is_valid_score("W/O")
    assert not is_valid_score("6-4 6-5")


def test_walkover_with_sets_is_noted():
    r = parse_score("6-4 W/O")
    assert r.outcome_type == WALKOVER
    assert "WALKOVER_WITH_SETS" in r.notes


def test_result_is_frozen():
    r = parse_score("6-4 6-4")
    with pytest.raises(Exception):
        r.sets_w = 3  # type: ignore[misc]


def test_games_are_finite_ints():
    r = parse_score("6-7(7) 7-6(3) 7-6(10)")
    assert all(isinstance(x, int) and math.isfinite(x) for x in (r.games_w, r.games_l, r.sets_w, r.sets_l))
