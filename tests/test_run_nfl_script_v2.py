"""RUN NFL: GAME SCRIPT V2 is RESEARCH_ONLY context.

It must never move a decision field, must load only from the simulation run the packet attached, must fail open,
must not change a single projection when it is computed, refuses an incoherent game, and grades nothing with an
adjective. Synthetic simulation (tests/sim_fixtures.py) plus the packet fixtures of test_run_nfl_script_context."""
import copy
import gzip
import json
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nfl_edge.handicap import render as RD, script_block as SB  # noqa: E402
from nfl_edge.pricing.game_env import ResidualBank  # noqa: E402
from nfl_edge.sim import simulate as S, script_v2 as V  # noqa: E402
import sim_fixtures as FX  # noqa: E402
import test_run_nfl_script_context as CTX  # noqa: E402


def _bank():
    rng = np.random.default_rng(3); n = 600
    return ResidualBank(rng.normal(0, 13, n), rng.normal(0, 13, n), np.repeat([2020, 2021, 2022], n // 3), ref_season=2023,
                        spread_lines=np.where(rng.random(n) < 0.5, 3.0, 2.5), total_lines=np.where(rng.random(n) < 0.5, 44.0, 44.5),
                        overtime=rng.random(n) < 0.06, results=rng.normal(0, 13, n), rng=np.random.default_rng(1))


@pytest.fixture(scope="module")
def doc():
    b, tf, pf = FX.synthetic_bundle(seed=1)
    gi = FX.game_input(tf, pf)
    res = S.simulate(gi, b, n=4000, bank=_bank())
    home, away = gi.home.team, gi.away.team
    contracts = [{"ticker": "TOT-44", "family": "TOTAL", "threshold": 44.5},
                 {"ticker": "SP-SEA3", "family": "SPREAD", "team": home, "floor_strike": 3.5},
                 {"ticker": "TT-SEA31", "family": "TEAM_TOTAL", "team": home, "threshold": 31},
                 {"ticker": "GW-A", "family": "GAME_WINNER", "team": away}]
    return V.game_document(res, gi, S.coherence_report(res), contracts, {}), res, gi


def test_v2_cannot_move_any_decision_field(doc):
    d, _, _ = doc
    base = CTX.build()
    rich = CTX.build(script_v2=d, script_v2_source="x.scripts_v2.json.gz")
    assert rich["game_script_v2"]["state"] == "OK" and rich["game_script_v2"]["primary_scripts"]
    for k in CTX.DECISION_KEYS + ("game_script_inputs",):
        assert json.dumps(base.get(k), sort_keys=True, default=str) == json.dumps(rich.get(k), sort_keys=True, default=str), k
    for a, b in zip(base["markets"], rich["markets"]):
        for k in CTX.MARKET_DECISION_KEYS:
            assert a.get(k) == b.get(k), k


def test_v2_view_numbers_come_from_the_document(doc):
    d, _, _ = doc
    g = CTX.build(script_v2=d, script_v2_source="s")
    v = g["game_script_v2"]
    assert abs(sum(p["probability"] for p in v["primary_scripts"]) + v["other_probability"] - 1) < 1e-9
    c = {x["ticker"]: x for x in v["candidates"]}
    assert "TOT-44" in c, "each game line's headline rung is detailed"
    tot = c["TOT-44"]
    assert tot["reconciled_probability"] is None and "not validated" in tot["reconciled_note"]
    assert abs(sum(r["p_script"] * (r["p_cash_given_script"] or 0) for r in tot["matrix"]) - tot["football_probability"]) < 1e-3


def test_no_betting_path_module_reads_game_script_v2():
    for name in ("gates.py", "preflight.py", "risk.py", "wager_risk.py", "approval.py", "evaluate.py", "scorecard.py",
                 "preflight_trigger.py", "position_lifecycle.py", "analysis.py", "evidence_store.py"):
        src = open(os.path.join(ROOT, "nfl_edge", "handicap", name)).read()
        for key in ("game_script_v2", "script_v2", "script_robustness", "major_script_floor"):
            assert key not in src, f"{name} reads {key}"


def test_v2_loads_only_from_the_attached_run_and_fails_open(tmp_path, doc):
    d, _, _ = doc
    dd = tmp_path / "data" / "shadow" / "sim" / "2026-10-04"
    dd.mkdir(parents=True)
    with gzip.open(dd / "20261004T110000Z.sim-1.1.0.scripts_v2.json.gz", "wt") as f:
        json.dump({"games": {"G": d}}, f, default=float)
    got, src = SB.load_scripts_v2([str(tmp_path)], {"run_id": "20261004T110000Z"})
    assert got["G"]["state"] == "OK" and src.startswith("20261004T110000Z")
    assert SB.load_scripts_v2([str(tmp_path)], {"run_id": "20261004T120000Z"})[0] is None
    assert SB.load_scripts_v2([str(tmp_path)], None)[0] is None
    absent = CTX.build()
    assert absent["game_script_v2"]["state"] == "UNAVAILABLE"
    broken = CTX.build(script_v2={"state": "OK", "summary": None, "contracts": "not a list"}, script_v2_source="s")
    assert broken["game_script_v2"]["state"] in ("OK", "UNAVAILABLE")
    assert broken["counts"] == absent["counts"]


def test_rendered_v2_is_numbers_only(doc):
    d, _, _ = doc
    g = CTX.build(script_v2=d, script_v2_source="s")
    text = "\n".join(RD._game_script_v2_section(g["game_script_v2"], compact=False))
    assert "GAME SCRIPT V2 (RESEARCH_ONLY" in text and "PRIMARY PLAUSIBLE SCRIPTS" in text and "SCRIPT ROBUSTNESS" in text
    assert "MARKET_CENTRED_GAME" in text
    for word in ("LOCK", "SAFE", "SURE", "STRONG BET", "BEST BET", "GUARANTEE"):
        assert word not in text.upper().replace("SAFE_", ""), word


def test_an_incoherent_game_gets_no_script_numbers(doc):
    _, res, gi = doc
    d = V.game_document(res, gi, {"ok": False}, [{"ticker": "TOT", "family": "TOTAL", "threshold": 44}], {})
    assert d["state"] == "UNSUPPORTED_COHERENCE" and "summary" not in d and "contracts" not in d
    v = SB.game_script_v2_view({}, d, source="s")
    assert v["state"] == "UNSUPPORTED_COHERENCE" and "candidates" not in v


def test_pricing_is_identical_with_and_without_v2(monkeypatch):
    from nfl_edge.sim import inputs as I, prospective as P
    b, tf, pf = FX.synthetic_bundle(seed=1)
    gi = FX.game_input(tf, pf)
    monkeypatch.setattr(I, "historical_bank", lambda season, seed=11: _bank())
    pid = next(p for p in gi.home.players["player_id"])
    ledger = [{"ticker": "TOT", "family": "TOTAL", "threshold": 44, "game_id": gi.game_id, "period": "FULL", "mid": 0.5},
              {"ticker": "GW", "family": "GAME_WINNER", "team": gi.home.team, "game_id": gi.game_id, "period": "FULL", "mid": 0.5},
              {"ticker": "PL", "family": "PLAYER_STAT", "stat": "receptions", "player_kalshi_id": "k", "operator": ">=",
               "threshold": 3, "game_id": gi.game_id, "period": "FULL", "mid": 0.5}]
    slate = {"games": {gi.game_id: {"input": gi, "kickoff": None}}}
    kw = dict(n_sims=3000, run_id="20260101T000000Z", observed_at="x", generated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
              player_map={"k": pid}, verbose=lambda *a: None)
    plain = P.price_slate(copy.deepcopy(slate), ledger, b, None, **kw)
    docs = {}
    wx = [{"game_id": gi.game_id, "retrieved_at": "2025-12-31T00:00:00+00:00", "wind_speed_10m": 25.0},
          {"game_id": gi.game_id, "retrieved_at": "2026-01-02T00:00:00+00:00", "wind_speed_10m": 3.0}]
    rich = P.price_slate(copy.deepcopy(slate), ledger, b, None, scripts_v2=docs, weather_vintages=wx, **kw)
    assert json.dumps(plain, sort_keys=True, default=str) == json.dumps(rich, sort_keys=True, default=str)
    d = docs[gi.game_id]
    assert d["state"] == "OK", d
    assert d["summary"]["weather"]["wind_speed_10m"] == 25.0, "the forecast retrieved AFTER the cutoff never enters"
