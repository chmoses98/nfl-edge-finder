"""Quantiles and the line ladder of the NFL projection pmfs (nfl/live/distribution.py).

The real-data cases use pmfs ARCHIVED by the live run (projection-data branch) for the WAS @ SF Monday-night slate, together with the rows the
feed published from them (tests/fixtures/nfl_dist): Kittle and McCaffrey receptions, Purdy and Daniels completions. Each pmf reproduces its
published mean and threshold probabilities exactly, so the quantiles asserted here are computed from the same distribution the feed already
prices from.
"""
import json
import os
import sys

import numpy as np
import pytest

PF = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, PF)

from pf_core import dists  # noqa: E402
from nfl.live import distribution as DI  # noqa: E402

FX = json.load(open(os.path.join(os.path.dirname(__file__), "fixtures", "nfl_dist", "real_pmfs_was_sf.json")))
REAL = {(r["forecast"]["entity_name"], r["forecast"]["family"]): r for r in FX["rows"]}


def batch(fc):
    return dists.DistBatch(fc["lo"], np.array([fc["probs"]]))


def built_row(entry):
    """The summary of a real forecast as the artifact builder reads it: scalar fields, quantiles, then the ladder."""
    fc, pub = entry["forecast"], entry["published_row"]
    d = batch(fc)
    study = {int(k): d.prob_ge(int(k)) for k in pub["thresholds"]}
    row = {"mean": round(float(d.mean[0]), 3), "median": int(d.median[0]), "p10": int(d.quantile(0.1)[0]), "p90": int(d.quantile(0.9)[0]),
           "thresholds": DI.row_thresholds(DI.survival_arrays(d, "count"), study, 0), "quantiles": DI.row_quantiles(DI.quantile_arrays(d), 0)}
    return row, d


@pytest.mark.parametrize("key", sorted(REAL))
def test_real_pmf_reproduces_the_published_row(key):
    row, _ = built_row(REAL[key])
    pub = REAL[key]["published_row"]
    for f in ("mean", "median", "p10", "p90"):
        assert row[f] == pub[f], f
    # the study's three rungs are published unchanged; the ladder adds the other integer lines from the same pmf
    assert {k: row["thresholds"][k] for k in pub["thresholds"]} == pub["thresholds"]
    assert len(row["thresholds"]) > len(pub["thresholds"])


@pytest.mark.parametrize("key", sorted(REAL))
def test_real_quantiles_come_from_the_same_pmf_and_cohere(key):
    row, d = built_row(REAL[key])
    q = row["quantiles"]
    assert list(q) == list(DI.KEYS)
    assert q["p50"] == row["median"] and q["p10"] == row["p10"] and q["p90"] == row["p90"]
    assert all(isinstance(v, int) and v >= 0 for v in q.values())
    vals = list(q.values())
    assert vals == sorted(vals)
    assert DI.validate_row(row) == []
    # independent recomputation straight from the pmf
    p = np.array(REAL[key]["forecast"]["probs"])
    cdf = np.cumsum(p)
    lo = REAL[key]["forecast"]["lo"]
    for name, lvl in DI.LEVELS:
        x = q[name]
        assert cdf[x - lo] >= lvl - 1e-9
        assert x - lo == 0 or cdf[x - lo - 1] < lvl


def test_known_real_values_kittle_and_mccaffrey_receptions():
    k, _ = built_row(REAL[("George Kittle", "receptions")])
    m, _ = built_row(REAL[("Christian McCaffrey", "receptions")])
    assert k["quantiles"] == {"p05": 1, "p10": 2, "p25": 3, "p50": 5, "p75": 7, "p90": 8, "p95": 10}
    assert m["quantiles"] == {"p05": 1, "p10": 2, "p25": 3, "p50": 5, "p75": 6, "p90": 8, "p95": 9}
    # the live feed's own p10 / median / p90 for these rows (2026-10-19T01:34Z)
    assert (k["p10"], k["median"], k["p90"]) == (2, 5, 8) and (m["p10"], m["median"], m["p90"]) == (2, 5, 8)


def test_completions_distribution_is_wide_enough_and_ordered():
    for name in ("Brock Purdy", "Jayden Daniels"):
        row, _ = built_row(REAL[(name, "completions")])
        assert DI.validate_row(row) == []
        assert row["quantiles"]["p05"] < row["quantiles"]["p50"] < row["quantiles"]["p95"]


# --------------------------------------------------------------------------------------------------- property: any pmf
@pytest.mark.parametrize("make", [
    lambda: dists.negbin(np.array([0.3, 1.2, 4.9, 6.1, 22.0, 41.5]), 0.25),
    lambda: dists.poisson(np.array([0.05, 0.8, 3.3, 12.0, 30.0])),
])
def test_every_pmf_yields_a_coherent_row(make):
    d = make()
    qa = DI.quantile_arrays(d)
    surv = DI.survival_arrays(d, "count")
    for j in range(len(d)):
        row = {"mean": round(float(d.mean[j]), 3), "median": int(d.median[j]), "p10": int(d.quantile(0.1)[j]), "p90": int(d.quantile(0.9)[j]),
               "quantiles": DI.row_quantiles(qa, j), "thresholds": DI.row_thresholds(surv, {}, j)}
        assert DI.validate_row(row) == [], row


# --------------------------------------------------------------------------------------------------- invalid inputs
@pytest.fixture
def good():
    row, _ = built_row(REAL[("George Kittle", "receptions")])
    return row


def mutate(row, **kw):
    r = json.loads(json.dumps(row))
    for k, v in kw.items():
        if k == "q":
            r["quantiles"].update(v)
        else:
            r[k] = v
    return r


def test_a_row_without_quantiles_has_nothing_to_validate(good):
    assert DI.validate_row({k: v for k, v in good.items() if k != "quantiles"}) == []


@pytest.mark.parametrize("bad,needle", [
    ({"q": {"p25": 99}}, "non-decreasing"),
    ({"q": {"p05": -1}}, "negative"),
    ({"q": {"p50": 5.5}}, "integer"),
    ({"q": {"p50": float("nan")}}, "finite"),
    ({"q": {"p75": None}}, "finite"),
    ({"q": {"p50": 4}}, "median"),
    ({"q": {"p10": 1}}, "disagrees"),
    ({"q": {"p90": 9}}, "disagrees"),
    ({"mean": -1.0}, "mean"),
    ({"mean": float("inf")}, "mean"),
    ({"thresholds": {"3": 0.5, "5": 0.9}}, "survival"),
    ({"thresholds": {"3": 1.2}}, "probability"),
    ({"thresholds": {"9": 0.4}}, "too high"),      # k=9 is above p90=8, so P(X>=9) can be at most 0.10
    ({"thresholds": {"2": 0.05}}, "too low"),      # k=2 is at or below p10=2, so P(X>=2) must exceed 0.90
])
def test_incoherent_rows_are_reported(good, bad, needle):
    probs = DI.validate_row(mutate(good, **bad))
    assert any(needle in p for p in probs), probs


def test_quantiles_must_have_every_level_and_nothing_extra(good):
    r = mutate(good)
    del r["quantiles"]["p25"]
    assert any("p25" in p for p in DI.validate_row(r))
    r = mutate(good)
    r["quantiles"]["p99"] = 20
    assert any("unexpected" in p for p in DI.validate_row(r))
    assert DI.validate_row(mutate(good, quantiles=[1, 2])) == ["quantiles is not an object"]


# --------------------------------------------------------------------------------------------------- the ladder
@pytest.mark.parametrize("key", sorted(REAL))
def test_count_ladder_covers_every_line_the_distribution_spreads_over(key):
    row, d = built_row(REAL[key])
    ks = sorted(int(k) for k in row["thresholds"])
    assert ks == list(range(ks[0], ks[-1] + 1)), "no gaps: every integer line between the first and last"
    ps = [row["thresholds"][str(k)] for k in ks]
    assert ps == sorted(ps, reverse=True), "one survival function"
    assert ps[0] <= 1 - DI.LADDER_MIN + 1e-4 and ps[-1] >= DI.LADDER_MIN - 1e-4
    p = np.array(REAL[key]["forecast"]["probs"])
    lo = REAL[key]["forecast"]["lo"]
    for k in ks:
        assert row["thresholds"][str(k)] == round(float(p[max(k - lo, 0):].sum()), 4)


def test_kittle_main_line_is_priced_from_the_published_ladder():
    """The Kalshi receptions ladder for Kittle (live 2026-10-19) lists 3+ ... 13+; the 6+ line used to be missing from the feed."""
    row, _ = built_row(REAL[("George Kittle", "receptions")])
    for k in range(3, 11):
        assert str(k) in row["thresholds"], k
    assert row["thresholds"]["6"] < row["thresholds"]["5"]


def test_yardage_families_keep_the_study_rungs():
    d = dists.negbin(np.array([60.0]), 0.2, K=330)
    study = {40: d.prob_ge(40), 60: d.prob_ge(60)}
    assert DI.survival_arrays(d, "yards") == {}
    assert DI.row_thresholds({}, study, 0).keys() == {"40", "60"}


def test_a_binary_family_publishes_only_its_one_line():
    d = dists.DistBatch(0, np.array([[0.4, 0.6]]))
    surv = DI.survival_arrays(d, "binary")
    assert DI.row_thresholds(surv, {1: d.prob_ge(1)}, 0) == {"1": 0.6}
