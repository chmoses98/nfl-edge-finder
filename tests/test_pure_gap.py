"""Tests for the PURE gap decomposition helpers (nfl_edge/research/pure_gap.py) and the dependency table."""
from __future__ import annotations

import json
import os
import re

import numpy as np
import pytest

from nfl_edge.research import pure_gap as G

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _arm(rng, n, stat):
    vol = rng.uniform(25, 45, n); snap = rng.uniform(0.2, 1.0, n); opp = rng.uniform(0.0, 9.0, n)
    mean = opp * rng.uniform(5, 12, n) if "yards" in stat else opp * rng.uniform(0.5, 0.8, n) if stat == "receptions" else opp
    return mean, opp, vol, snap


@pytest.mark.parametrize("stat", ["snap_share", "targets", "receptions", "receiving_yards", "carries", "rushing_yards",
                                  "passing_attempts", "completions", "passing_yards"])
def test_factorisation_reproduces_mean_and_shapley_is_exact(stat):
    rng = np.random.default_rng(1)
    n = 500
    a = _arm(rng, n, stat); b = _arm(rng, n, stat)
    if stat == "snap_share":
        a = (rng.uniform(0, 1, n),) * 4; b = (rng.uniform(0, 1, n),) * 4
    ca = G.factorize(stat, *a); cb = G.factorize(stat, *b)
    names = G.components(stat)
    assert set(ca) == set(names)
    prod = np.ones(n)
    for k in names:
        prod = prod * ca[k]
    assert np.allclose(prod, a[0])
    y = rng.uniform(0, 1, n) if stat == "snap_share" else rng.poisson(5, n).astype(float)
    phi = G.shapley_abs_error(y, ca, cb, names)
    tot = sum(phi[k] for k in names)
    assert np.allclose(tot, np.abs(a[0] - y) - np.abs(b[0] - y))
    assert np.allclose(phi["_total"], tot)


def test_shapley_attributes_only_the_component_that_differs():
    rng = np.random.default_rng(2)
    n = 300
    mean, opp, vol, snap = _arm(rng, n, "receiving_yards")
    ca = G.factorize("receiving_yards", mean, opp, vol, snap)
    cb = {k: v.copy() for k, v in ca.items()}
    cb["volume"] = ca["volume"] * 1.2                     # B differs from A only in team volume
    y = rng.poisson(40, n).astype(float)
    phi = G.shapley_abs_error(y, ca, cb, G.components("receiving_yards"))
    for k in ("snap", "usage", "efficiency"):
        assert np.allclose(phi[k], 0.0)
    assert np.allclose(phi["volume"], phi["_total"])


def test_oracle_with_all_realised_components_has_zero_error():
    rng = np.random.default_rng(3)
    n = 200
    mean, opp, vol, snap = _arm(rng, n, "rushing_yards")
    ca = G.factorize("rushing_yards", mean, opp, vol, snap)
    opp_act = rng.poisson(10, n).astype(float)
    y = np.where(opp_act > 0, opp_act * rng.uniform(2, 6, n), 0.0)
    snap_act = np.where(rng.uniform(size=n) < 0.1, np.nan, rng.uniform(0.1, 1, n))
    act = G.factorize_actual("rushing_yards", y, opp_act, rng.uniform(20, 35, n), snap_act, ca)
    prod = np.ones(n)
    for k in G.components("rushing_yards"):
        prod = prod * act[k]
    assert np.allclose(prod, y)


def test_cluster_bootstrap_contains_mean_and_contribution_adds_up():
    rng = np.random.default_rng(4)
    games = np.repeat(np.arange(100), 10)
    diff = rng.normal(0.3, 1.0, len(games))
    lo, hi = G.cluster_boot(diff, games, 500)
    assert lo < diff.mean() < hi
    mask = rng.uniform(size=len(diff)) < 0.3
    c1 = G.contribution(diff, mask, games, 200)["contribution_to_pooled_gap"]["mean"]
    c2 = G.contribution(diff, ~mask, games, 200)["contribution_to_pooled_gap"]["mean"]
    assert abs(c1 + c2 - diff.mean()) < 1e-5


# ------------------------------------------------------------------------------------------------ dependency table
TABLE = os.path.join(ROOT, "research", "pure_gap", "dependency_table.json")


@pytest.mark.skipif(not os.path.exists(TABLE), reason="dependency table not generated")
def test_dependency_table_is_consistent_with_the_pure_v1_source():
    t = json.load(open(TABLE))
    assert t["schema"] == "pure_gap.dependency_table.v1"
    src = ""
    d = os.path.join(ROOT, "nfl_edge", "engines", "player", "pure_v1")
    for f in sorted(os.listdir(d)):
        if f.endswith(".py") and f != "mutation.py":            # mutation.py names market columns to randomise them
            src += open(os.path.join(d, f)).read()
    for row in t["features"]:
        assert row["market_dependency"] in ("DIRECT", "INDIRECT_VERIFIED", "NONE_VERIFIED", "UNVERIFIED")
        assert isinstance(row["pure_v1_uses"], bool) and isinstance(row["v4_uses"], bool)
        assert row["evidence"], row["feature"]
        if not row["pure_v1_uses"]:
            for tok in row.get("source_tokens", []):
                assert not re.search(rf"\b{re.escape(tok)}\b", src), (row["feature"], tok)
        if row["pure_v1_uses"]:
            assert row["market_dependency"] == "NONE_VERIFIED", row
    assert t["pure_v1_verdict"]["indirect_market_dependency_found"] is False
