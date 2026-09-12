"""H3: a mined hypothesis is qualified, sized and bounded by OUTCOME evidence, never by row count.

`candidates_from_scorecard` applied its `min_n` threshold to the slice's total row count and reported that
same number as `sample_size`, with `n_games` as `game_count`. Both counts include probability-bearing rows
that never settled and never can -- an unresolved player identity, a family with no settlement branch -- and
`n_games` counts every distinct game in the slice rather than the games the effect was actually computed
over. A slice of forty rows carrying four graded outcomes therefore cleared a threshold of thirty and was
written out as `sample_size: 40, game_count: 40, uncertainty: 0.0`.

For a programme trying to detect one- to two-point edges against a sharp market, a candidate that overstates
its evidence by 10x and claims zero uncertainty is not a weak result, it is a false one.

The cases below are the audit's, reproduced as regressions.
"""
import random

import pytest

from nfl_edge.evaluation import scorecard_v3 as SC
from nfl_edge.research import hypothesis_registry_v2 as HR

MIN_N = 30


def row(i, *, family, settled, sync=True, game=None, model_edge=0.0, rng=None):
    """A research row with genuine variance, so a standard error is a real estimate and not a degenerate zero."""
    rng = rng or random.Random(i)
    y = float(i % 2)
    noise = rng.uniform(-0.08, 0.08)
    market = 0.5 + (0.25 if y else -0.25) + noise           # the market is informative
    model = market - (model_edge if y else -model_edge) + rng.uniform(-0.05, 0.05)
    clamp = lambda v: min(max(v, 0.02), 0.98)
    return {"evidence_class": "PROSPECTIVE_FROZEN",
            "synchronization_state": "SYNCHRONIZED" if sync else "ASYNC_MODEL_NEWER_THAN_MARKET",
            "information_skew_seconds": 0.0 if sync else 2234.0,
            "market_family": family,
            "game_id": game if game is not None else f"G{i}",
            "ticker": f"T{i}",
            "contract_value": clamp(model), "h_mid": clamp(market), "c_mid": clamp(market),
            "settled_yes": (y if settled else None),
            "settlement_reachability": "DISPATCHABLE" if settled else "MISSING_SETTLEMENT_KEYS",
            "clv_status": "NO_VIEW"}


def mine(rows, min_n=MIN_N):
    return HR.candidates_from_scorecard(SC.build(rows, min_segment_n=5), season=2026, week=1, min_n=min_n)


def slice_of(rows, family):
    sc = SC.build(rows, min_segment_n=5)
    return sc["by_synchronization"]["PROSPECTIVE_FROZEN"]["SYNCHRONIZED"]["segments"]["market_family"][family]


def for_family(cands, family):
    return [c for c in cands if c["id"].endswith(f"-{family}")]


# --------------------------------------------------------------------------------- CASE A
def test_case_a_forty_rows_with_four_outcomes_produces_no_candidate():
    """THE AUDIT'S REPRODUCTION: 40 total rows, 4 graded outcomes, min_n=30 -> nothing may be promoted."""
    rng = random.Random(1)
    rows = [row(i, family="THIN", settled=(i < 4), model_edge=0.30, rng=rng) for i in range(40)]
    m = slice_of(rows, "THIN")
    assert m["segment_rows_total"] == 40
    assert m["outcome_n"] == 4, "fixture must really carry only four gradable outcomes"
    assert mine(rows) == [], "a four-outcome slice cleared a thirty-outcome threshold"


def test_case_a_the_old_denominator_would_have_passed():
    """Guards the guard: the fixture genuinely trips the OLD rule, so this test cannot pass vacuously."""
    rng = random.Random(1)
    rows = [row(i, family="THIN", settled=(i < 4), model_edge=0.30, rng=rng) for i in range(40)]
    m = slice_of(rows, "THIN")
    assert m["n"] >= MIN_N > m["outcome"]["model_minus_market_n"]


# --------------------------------------------------------------------------------- CASE B
def test_case_b_eligibility_and_sample_size_come_from_the_thirty_five_outcomes():
    rng = random.Random(2)
    rows = [row(i, family="REAL", settled=(i < 35), model_edge=0.30, rng=rng) for i in range(100)]
    m = slice_of(rows, "REAL")
    assert (m["segment_rows_total"], m["outcome_n"]) == (100, 35)
    cands = for_family(mine(rows), "REAL")
    assert len(cands) == 1
    c = cands[0]
    assert c["sample_size"] == 35, f"sample_size {c['sample_size']} is not the outcome count"
    assert c["segment_rows_total"] == 100 and c["outcome_n"] == 35
    assert c["minimum_sample"] == MIN_N and c["sample_basis"].startswith("model_minus_market_n")


def test_case_b_is_refused_once_the_outcome_count_drops_below_the_threshold():
    rng = random.Random(2)
    rows = [row(i, family="REAL", settled=(i < 29), model_edge=0.30, rng=rng) for i in range(100)]
    assert for_family(mine(rows), "REAL") == []


# --------------------------------------------------------------------------------- CASE C
def test_case_c_async_rows_cannot_lift_twenty_synchronized_outcomes_over_the_threshold():
    rng = random.Random(3)
    rows = ([row(i, family="MIX", settled=True, sync=False, model_edge=0.30, rng=rng) for i in range(200)]
            + [row(i + 1000, family="MIX", settled=True, sync=True, model_edge=0.30, rng=rng) for i in range(20)])
    assert mine(rows) == [], "asynchronous rows padded a synchronized slice over its threshold"


# --------------------------------------------------------------------------------- CASE D
def test_case_d_forty_settled_plus_forty_six_unsettleable_reports_exactly_forty():
    rng = random.Random(4)
    clean = [row(i, family="D", settled=True, model_edge=0.30, rng=rng) for i in range(40)]
    dirty = clean + [row(i + 5000, family="D", settled=False, model_edge=0.30, rng=rng) for i in range(46)]

    c_clean = for_family(mine(clean), "D")
    c_dirty = for_family(mine(dirty), "D")
    assert len(c_clean) == len(c_dirty) == 1
    a, b = c_clean[0], c_dirty[0]

    assert b["sample_size"] == 40, f"the 46 unsettleable rows padded n to {b['sample_size']}"
    assert b["game_count"] == a["game_count"] == 40
    assert b["effect_size"] == a["effect_size"]
    assert b["uncertainty"] == a["uncertainty"]
    assert b["segment_rows_total"] == 86, "coverage is still reported honestly"


def test_case_d_the_forty_six_move_no_outcome_statistic():
    rng = random.Random(4)
    clean = [row(i, family="D", settled=True, model_edge=0.30, rng=rng) for i in range(40)]
    dirty = clean + [row(i + 5000, family="D", settled=False, model_edge=0.30, rng=rng) for i in range(46)]
    oa, ob = slice_of(clean, "D")["outcome"], slice_of(dirty, "D")["outcome"]
    for k in ("n", "model_n", "market_n", "model_minus_market_n", "settled_game_count", "clusters",
              "brier_model", "model_minus_market_brier", "model_minus_market_se", "base_rate"):
        assert oa[k] == ob[k], f"{k} moved when unsettleable rows were added"


# --------------------------------------------------------------------------------- CASE E
def test_case_e_game_count_is_independent_games_not_repeated_contracts():
    """Ten contracts on each of six games is six independent observations, not sixty."""
    rng = random.Random(5)
    rows = [row(i, family="CLUSTER", settled=True, game=f"G{i % 6}", model_edge=0.30, rng=rng) for i in range(60)]
    c = for_family(mine(rows), "CLUSTER")
    assert len(c) == 1
    assert c[0]["sample_size"] == 60
    assert c[0]["game_count"] == 6, f"game_count {c[0]['game_count']} counted rows, not games"
    assert c[0]["settled_game_count"] == 6


# --------------------------------------------------------------------------------- uncertainty honesty
def test_a_degenerate_zero_standard_error_is_refused_rather_than_published():
    """Every paired difference identical is a degenerate estimate, not certainty; z would be infinite."""
    rows = []
    for i in range(40):
        r = row(i, family="DEGEN", settled=True, rng=random.Random(0))
        r.update({"contract_value": 0.9 if r["settled_yes"] else 0.1, "h_mid": 0.5, "c_mid": 0.5})
        rows.append(r)
    m = slice_of(rows, "DEGEN")
    assert m["outcome"]["model_minus_market_se"] < HR.SE_FLOOR, "fixture must really be degenerate"
    assert for_family(mine(rows), "DEGEN") == []


def test_a_single_game_slice_has_no_usable_uncertainty_and_is_refused():
    rng = random.Random(7)
    rows = [row(i, family="ONEGAME", settled=True, game="G-ONLY", model_edge=0.30, rng=rng) for i in range(40)]
    assert slice_of(rows, "ONEGAME")["outcome"]["clusters"] == 1
    assert for_family(mine(rows), "ONEGAME") == []


def test_no_candidate_is_ever_emitted_with_a_zero_or_missing_uncertainty():
    rng = random.Random(8)
    rows = ([row(i, family="A", settled=True, model_edge=0.30, rng=rng) for i in range(60)]
            + [row(i + 100, family="B", settled=(i < 4), model_edge=0.30, rng=rng) for i in range(50)]
            + [row(i + 300, family="C", settled=True, game="G-ONE", model_edge=0.30, rng=rng) for i in range(40)])
    for c in mine(rows):
        assert c["uncertainty"] is not None and c["uncertainty"] >= HR.SE_FLOOR
        assert c["sample_size"] >= MIN_N and c["game_count"] >= 2
