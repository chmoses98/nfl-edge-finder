"""RUN NFL: GAME SCRIPT INPUTS and HISTORICAL RESEARCH TAGS are context only.

They must never create a BET state, bypass preflight, or change an edge, a threshold, a stake or a model
probability, and RUN NFL must work exactly as before when the research layer is absent."""
import ast
import copy
import gzip
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.handicap import packet as P, render as RD, script_block as SB  # noqa: E402

NOW = datetime(2026, 10, 4, 12, tzinfo=timezone.utc)


def row(**kw):
    d = dict(ticker="T", family="TOTAL", period="FULL", threshold=44.5, mid=0.5, yes_bid=0.49, yes_ask=0.51, no_bid=0.49,
             no_ask=0.51, quote_width=0.02, volume=100.0, open_interest=100.0, support_state="SUPPORTED",
             model_contract_value=0.55, team=None, home_team="SEA", away_team="NE", game_id="G",
             kickoff_utc="2026-10-04T17:00:00+00:00", season=2026, week=4)
    d.update(kw)
    return d


ROWS = [row(ticker="TOT-44", threshold=44.5, mid=0.5),
        row(ticker="SP-SEA3", family="SPREAD", team="SEA", threshold=3.5, floor_strike=3.5, operator=">", mid=0.15,
            yes_bid=0.14, yes_ask=0.16, no_bid=0.84, no_ask=0.86),
        row(ticker="TT-SEA31", family="TEAM_TOTAL", team="SEA", threshold=31, mid=0.04, yes_bid=0.03, yes_ask=0.05,
            no_bid=0.95, no_ask=0.97, model_contract_value=0.04)]


def hyps():
    rows, note = SB.load_research_hypotheses(ROOT)
    assert rows, note
    return rows, note


SCRIPT = {"environment": {"home_margin": {"mean": 3.1, "p05": -14, "p25": -4, "p75": 10, "p95": 20},
                          "total": {"mean": 44.6, "p25": 37, "p75": 52, "p05": 29, "p95": 61},
                          "p_one_score": 0.52, "p_blowout_17plus": 0.17, "p_home_win": 0.58,
                          "score_state_paths": "NOT_SIMULATED: final margin/total only"},
          "teams": {"SEA": {"volume": {"plays": {"mean": 63, "p25": 59, "p75": 67}, "pass_att": {"mean": 34, "p25": 30, "p75": 38}},
                            "by_final_margin": {"lead14+": {"pass_rate_mean": 0.51}, "trail14+": {"pass_rate_mean": 0.66}},
                            "players": [{"name": "WR One", "position": "WR", "p_active": 1.0, "targets": {"mean": 8.1, "p25": 6, "p75": 10},
                                         "carries": {"mean": 0}, "target_share": {"mean": 0.24}, "carry_share": None, "opportunity_cv": 0.33}]}},
          "not_simulated": ["score-state paths / lead changes"]}


def build(**kw):
    return P.build_game("G", copy.deepcopy(ROWS), profiles={}, qb_profiles={}, context_runs=[], movement=None, now=NOW,
                        implied={}, **kw)


DECISION_KEYS = ("counts", "market_implied", "model_view", "largest_disagreements", "disagreement_ranking_basis",
                 "best_expressions", "correlation_groups", "key_questions", "coverage", "tail_rungs", "largest_moves")
MARKET_DECISION_KEYS = ("support_state", "model_probability", "disagreement_vs_mid", "disagreement_yes_executable",
                        "disagreement_no_executable", "tradable_for_disagreement_ranking", "analysis", "flags", "mid",
                        "yes_ask", "no_ask")


def test_run_nfl_is_unchanged_when_the_research_layer_is_absent():
    g = build()
    assert g["game_script_inputs"]["state"] == "PARTIAL"
    assert g["game_script_inputs"]["game_environment"]["state"] == "UNAVAILABLE"
    assert all(m["research_tags"] == [] for m in g["markets"])


def test_research_tags_and_script_inputs_cannot_move_any_decision_field():
    base = build()
    hs, note = hyps()
    rich = build(script=SCRIPT, script_source="x.scripts.json.gz", research_hyps=hs, research_note=note)
    assert any(m["research_tags"] for m in rich["markets"]), "the fixture must actually produce tags"
    for k in DECISION_KEYS:
        assert json.dumps(base.get(k), sort_keys=True, default=str) == json.dumps(rich.get(k), sort_keys=True, default=str), k
    for a, b in zip(base["markets"], rich["markets"]):
        for k in MARKET_DECISION_KEYS:
            assert a.get(k) == b.get(k), k


def test_tags_follow_the_registered_locators():
    hs, _ = hyps()
    g = build(research_hyps=hs, research_note="n")
    by = {m["ticker"]: {(t["hypothesis"], t["side"]) for t in m["research_tags"]} for m in g["markets"]}
    assert ("H-20261001-B01", "YES") in by["SP-SEA3"], "full-game YES at a 15c mid sits in B01's 10-30c band"
    assert ("H-20261001-B03", "NO") in by["TT-SEA31"], "a 97c NO sits in B03's 90c+ band"
    assert not any(h in ("H-20261001-B05", "H-20261001-B06", "H-20261001-B07", "H-20261001-B04")
                   for t in by.values() for h, _ in t), "paired / game-level / T-24h metrics never tag a single contract"
    for m in g["markets"]:
        for t in m["research_tags"]:
            assert t["authority"] == "NONE (context only)" and t["status"] in SB.UNDER_TEST


def test_no_betting_path_module_reads_the_research_context():
    for name in ("gates.py", "preflight.py", "risk.py", "wager_risk.py", "approval.py", "evaluate.py", "scorecard.py",
                 "preflight_trigger.py", "position_lifecycle.py"):
        src = open(os.path.join(ROOT, "nfl_edge", "handicap", name)).read()
        for key in ("research_tags", "game_script_inputs", "script_block", "board_hypotheses", "board_miner"):
            assert key not in src, f"{name} reads {key}"


def test_the_script_block_is_stdlib_only():
    tree = ast.parse(open(os.path.join(ROOT, "nfl_edge", "handicap", "script_block.py")).read())
    mods = {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module} | \
           {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    assert mods <= {"__future__", "glob", "gzip", "json", "os"}, mods


def test_scripts_load_only_from_the_attached_simulation_run(tmp_path):
    d = tmp_path / "data" / "shadow" / "sim" / "2026-10-04"
    d.mkdir(parents=True)
    with gzip.open(d / "20261004T110000Z.sim-1.1.0.scripts.json.gz", "wt") as f:
        json.dump({"games": {"G": SCRIPT}}, f)
    with gzip.open(d / "20261004T090000Z.sim-1.1.0.scripts.json.gz", "wt") as f:
        json.dump({"games": {"G": {"environment": {"p_one_score": 0.0}}}}, f)
    got, src = SB.load_scripts([str(tmp_path)], {"run_id": "20261004T110000Z"})
    assert got["G"]["environment"]["p_one_score"] == 0.52 and src.startswith("20261004T110000Z")
    assert SB.load_scripts([str(tmp_path)], {"run_id": "20261004T120000Z"})[0] is None
    assert SB.load_scripts([str(tmp_path)], None)[0] is None


def test_the_rendered_game_says_context_only():
    hs, note = hyps()
    g = build(script=SCRIPT, script_source="s", research_hyps=hs, research_note=note)
    text = "\n".join(RD._game_script_section(g["game_script_inputs"], g, compact=False))
    assert "GAME SCRIPT INPUTS (context only — authorises nothing)" in text
    assert "NOT evidence, NOT a signal" in text and "WR One" in text
    absent = "\n".join(RD._game_script_section(build()["game_script_inputs"], g, compact=False))
    assert "UNAVAILABLE" in absent


def test_a_broken_research_layer_fails_open():
    g = build(research_hyps=[{"id": "bad", "status": "PREREGISTERED", "locator": {"kind": "BOARD_CELL", "metric": "MID_BIAS", "filter": None}}])
    assert all(m["research_tags"] == [] for m in g["markets"])
    assert g["counts"] == build()["counts"]
