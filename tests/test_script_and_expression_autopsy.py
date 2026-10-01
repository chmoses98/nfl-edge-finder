"""Realized-script autopsy, the player-miss layer chain, the expression autopsy, thesis metadata and weekly-report
reproducibility. Synthetic inputs only."""
import inspect
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.research import expression_autopsy as EA      # noqa: E402
from nfl_edge.research import script_autopsy as SA          # noqa: E402
from nfl_edge.research import thesis as TH                  # noqa: E402
from nfl_edge.research import weekly_reports as WR          # noqa: E402


def play(q, h, a, pos="H", pt="pass", **kw):
    d = {"qtr": q, "total_home_score": h, "total_away_score": a, "posteam": pos, "play_type": pt, "pass_attempt": 1 if pt == "pass" else 0,
         "rush_attempt": 1 if pt == "run" else 0, "qb_dropback": 1 if pt == "pass" else 0, "sack": 0, "qb_scramble": 0,
         "passer_player_id": "QB_H" if pos == "H" else "QB_A", "rusher_player_id": None}
    d.update(kw)
    return d


def game_plays(quarters):
    """quarters: [(home, away) at the end of each quarter]; one pass + one run per side per quarter."""
    out = []
    for q, (h, a) in enumerate(quarters, start=1):
        for pos in ("H", "A"):
            out.append(play(q, h, a, pos, "pass"))
            out.append(play(q, h, a, pos, "run", rusher_player_id="RB"))
    return out


# ------------------------------------------------------------------------------------------------ realized script
def test_volume_counts_from_play_by_play():
    p = [play(1, 0, 0, "H", "pass"), play(1, 0, 0, "H", "pass", sack=1, pass_attempt=1), play(1, 0, 0, "H", "run", rusher_player_id="QB_H"),
         play(1, 0, 0, "H", "run", qb_scramble=1, qb_dropback=1), play(1, 0, 0, "H", "qb_kneel", rush_attempt=1)]
    v = SA.team_volume_from_pbp(p)["H"]
    assert v["plays"] == 5 and v["pass_att"] == 1 and v["sacks"] == 1 and v["scrambles"] == 1
    assert v["designed_rush"] == 1 and v["qb_designed_runs"] == 1 and v["kneels"] == 1


def test_labels_are_deterministic_and_documented():
    flow = SA.game_flow(game_plays([(3, 0), (17, 3), (31, 6), (38, 13)]), "H", "A")
    assert flow["final_margin"] == 25 and flow["margin_half"] == 14
    vol = {"H": {"plays": 60, "pass_att": 30, "designed_rush": 34}, "A": {"plays": 64, "pass_att": 45, "designed_rush": 15}}
    lab = SA.realized_labels(flow, vol, home="H", away="A", market_favorite="H", market_total=44.5)
    assert lab == ["FAVORITE_CONTROL", "EARLY_BLOWOUT", "RUN_HEAVY_CONTROL"] and SA.primary_label(lab) == "EARLY_BLOWOUT"
    close = SA.game_flow(game_plays([(7, 3), (10, 10), (13, 17), (20, 17)]), "H", "A")
    assert "COMPETITIVE_THROUGHOUT" in SA.realized_labels(close, {}, home="H", away="A", market_favorite="A", market_total=44.5)
    assert "UPSET" in SA.realized_labels(close, {}, home="H", away="A", market_favorite="A", market_total=44.5)


def test_script_labels_cannot_depend_on_any_wager():
    params = set(inspect.signature(SA.realized_labels).parameters)
    assert params == {"flow", "volume", "home", "away", "market_favorite", "market_total"}
    assert not any(w in " ".join(params) for w in ("wager", "bet", "pnl", "position", "stake"))


def test_team_volume_expectation_prefers_the_frozen_simulation_then_the_market_then_the_prior():
    prior = {"basis": "prior games this season", "n": 2, "plays": 62, "pass_att": 33, "designed_rush": 25}
    e = SA.team_expectation("H", prior=prior, market_qb_attempts=36.5, sim_team={"volume": {"plays": {"mean": 64}}})
    assert e["plays"]["source"] == "SIM_SCRIPT" and e["pass_att"]["source"].startswith("MARKET_LADDER")
    assert e["designed_rush"]["source"].startswith("PRIOR_MEAN")


def test_prior_means_never_read_the_game_or_later_games():
    sched = [{"game_id": f"G{w}", "season": 2026, "week": w, "home": "H", "away": f"X{w}"} for w in (1, 2, 3)]
    vols = {"G1": {"H": {"plays": 60}}, "G2": {"H": {"plays": 70}}, "G3": {"H": {"plays": 999}}}
    assert SA.prior_means(vols, sched, "G3", "H")["plays"] == 65.0
    assert SA.prior_means(vols, sched, "G1", "H")["n"] == 0


# ------------------------------------------------------------------------------------------------ the miss-layer chain
def test_opportunity_and_team_volume_classification_chain():
    trailing = SA.script_explains("pass_att", 0.4, -21, 130)
    assert trailing and not SA.script_explains("pass_att", 0.4, +21, 130)
    tv = {"classification": "TEAM_VOLUME_MISS", "opportunity_log_ratio": 0.5}
    assert SA.miss_layer(tv, team_err_lr=0.4, explained=True, role_low=False) == SA.LAYER_SCRIPT_VOLUME
    assert SA.miss_layer(tv, team_err_lr=0.4, explained=False, role_low=False) == SA.LAYER_TEAM_VOLUME
    share = {"classification": "OPPORTUNITY_MISS", "opportunity_log_ratio": -0.7}
    assert SA.miss_layer(share, team_err_lr=0.02, explained=False, role_low=False) == SA.LAYER_SHARE
    assert SA.miss_layer(share, team_err_lr=0.02, explained=False, role_low=True) == SA.LAYER_ROLE
    assert SA.miss_layer({"classification": "EFFICIENCY_MISS"}, team_err_lr=None, explained=False, role_low=False) == SA.LAYER_EFFICIENCY
    assert SA.miss_layer({"classification": "NO_LARGE_MISS"}, team_err_lr=None, explained=False, role_low=False) == SA.LAYER_NO_MISS


def test_connect_players_marks_only_script_driven_misses_as_preventable():
    games = [{"game_id": "G", "primary_label": "BLOWOUT", "labels": ["BLOWOUT"],
              "teams": {"H": {"final_margin": -21, "volume_vs_expectation": {"pass_att": {"log_ratio": 0.4, "script_explains": True, "source": "PRIOR_MEAN"}}}}}]
    aut = [{"game_id": "G", "week": 1, "team": "H", "player_id": "P", "stat": "receiving_yards", "classification": "TEAM_VOLUME_MISS",
            "opportunity_log_ratio": 0.6}]
    link = SA.connect_players(aut, games)[0]
    assert link["miss_layer"] == SA.LAYER_SCRIPT_VOLUME and link["better_game_script_could_have_helped"]


# ------------------------------------------------------------------------------------------------ expression autopsy
def _row(ticker, fam, team=None, stat=None, gsis=None, ladder=None, main=False, settled=None, rung=None, close=0.5, game="G"):
    return {"ticker": ticker, "game_id": game, "family": fam, "period": "FULL", "team": team, "stat": stat, "player_gsis_id": gsis,
            "ladder_id": ladder, "is_main_rung": main, "settled_yes": settled, "rung_value": rung, "close_mid": close, "player_name": gsis}


def _ep(eid, ticker, pnl, direction="LONG_YES", cost=50.0, qty=100.0):
    return {"position_episode_id": eid, "market_ticker": ticker, "direction": direction, "total_episode_pnl": pnl, "entry_cost": cost,
            "opened_quantity": qty, "week": 3, "opening_phase": "PRE_GAME", "closed_by": "HELD_TO_SETTLEMENT", "settlement_state": "SETTLED"}


def test_script_right_expression_wrong_is_judged_by_the_game_not_the_bet():
    """LV-NO: the Saints' scoring thesis was right (team-total headline paid), the spread expression lost."""
    rows = {"SPR": _row("SPR", "SPREAD", team="NO", ladder="L-spr", rung=3.5),
            "SPRMAIN": _row("SPRMAIN", "SPREAD", team="NO", ladder="L-spr", main=True, settled=0.0, rung=1.5),
            "TT": _row("TT", "TEAM_TOTAL", team="NO", ladder="L-tt", main=True, settled=1.0, rung=25)}
    lad = {"L-spr": [rows["SPR"], rows["SPRMAIN"]], "L-tt": [rows["TT"]]}
    doc = EA.autopsy([_ep("e1", "SPR", -50), _ep("e2", "TT", +50)], board_latest=rows, board_by_ladder=lad, player_links={}, player_team={})
    by = {p["market_ticker"]: p for p in doc["positions"]}
    assert by["SPR"]["thesis_bucket"] == by["TT"]["thesis_bucket"] == "G|NO|+"
    assert by["SPR"]["classification"] == "SCRIPT_PARTIAL/EXPRESSION_WRONG"
    assert by["TT"]["classification"] == "SCRIPT_PARTIAL/EXPRESSION_RIGHT"


def test_a_won_wager_does_not_make_the_script_right():
    rows = {"ALT": _row("ALT", "SPREAD", team="H", ladder="L", rung=-2.5), "MAIN": _row("MAIN", "SPREAD", team="H", ladder="L", main=True, settled=0.0, rung=3.5)}
    doc = EA.autopsy([_ep("e", "ALT", +30)], board_latest=rows, board_by_ladder={"L": list(rows.values())}, player_links={}, player_team={})
    p = doc["positions"][0]
    assert p["classification"] == "SCRIPT_WRONG" and "WON_DESPITE_WRONG_SCRIPT" in p["flags"]


def test_ladder_rungs_of_one_thesis_are_one_bucket_and_a_stack_is_flagged():
    rows = {f"P{k}": _row(f"P{k}", "PLAYER_STAT", stat="passing_yards", gsis="QB1", ladder="LQ", rung=k, main=(k == 225), settled=0.0)
            for k in (200, 225, 250)}
    rows["SP"] = _row("SP", "SPREAD", team="PHI", ladder="LS", main=True, settled=0.0, rung=3.5)
    lad = {"LQ": [rows[f"P{k}"] for k in (200, 225, 250)], "LS": [rows["SP"]]}
    eps = [_ep(f"e{t}", t, -40) for t in ("P200", "P225", "P250", "SP")]
    doc = EA.autopsy(eps, board_latest=rows, board_by_ladder=lad, player_links={}, player_team={"QB1": "PHI"})
    assert doc["n_positions"] == 4 and doc["n_independent_theses"] == 1, "four positions, ONE thesis"
    assert all("CORRELATED_STACK" in p["flags"] for p in doc["positions"])


def test_price_error_is_against_the_close_on_the_held_side():
    rows = {"T": _row("T", "TOTAL", ladder="L", main=True, settled=1.0, rung=44.5, close=0.40)}
    doc = EA.autopsy([_ep("e", "T", +40, cost=50.0, qty=100.0)], board_latest=rows, board_by_ladder={"L": [rows["T"]]}, player_links={}, player_team={})
    assert "PRICE_ERROR" in doc["positions"][0]["flags"] and doc["positions"][0]["paid_minus_close"] == 0.1


def test_lost_player_positions_carry_the_autopsy_layer():
    rows = {"R": _row("R", "PLAYER_STAT", stat="rushing_yards", gsis="RB1", ladder="L", main=True, settled=0.0, rung=50)}
    links = {("G", "RB1", "rushing_yards"): {"miss_layer": SA.LAYER_SHARE}}
    doc = EA.autopsy([_ep("e", "R", -50)], board_latest=rows, board_by_ladder={"L": [rows["R"]]}, player_links=links, player_team={"RB1": "H"})
    assert "ROLE_ERROR" in doc["positions"][0]["flags"]


# ------------------------------------------------------------------------------------------------ thesis metadata
def test_thesis_metadata_is_optional_and_backward_compatible(tmp_path):
    old = {"recommendation_id": "r", "ticker": "T", "primary_thesis": "", "reasoning_tags": []}
    assert TH.from_recommendation(old) == {}
    rich = {"ticker": "T", "game_id": "G", "primary_thesis": "Rams offence moves the ball", "correlation_group": "LAR-offence",
            "bet_up_to_probability": 0.55, "reasoning_tags": ["script:SHOOTOUT", "expression:team total over spread", "noise", 7]}
    m = TH.from_recommendation(rich)
    assert m["correlation_bucket"] == "LAR-offence" and m["script_dependency"] == "SHOOTOUT" and m["hard_bet_up_to"] == 0.55
    assert m["primary_thesis_id"] == TH.thesis_id("rams  offence moves THE ball", "G"), "normalised, stable"
    assert TH.load_owner_file(str(tmp_path), 2026, 4) == ({}, []), "an absent owner file is normal"
    d = tmp_path / "data" / "handicap" / "theses" / "2026"
    d.mkdir(parents=True)
    (d / "week_04.json").write_text('{"T": {"failure_mode": "QB_EXIT", "bogus": 1, "hard_bet_up_to": 2}}')
    got, warns = TH.load_owner_file(str(tmp_path), 2026, 4)
    assert got == {"T": {"failure_mode": "QB_EXIT", "hard_bet_up_to": 2}} and any("bogus" in w for w in warns)
    assert any("outside" in w for w in warns), "a bad value warns; it never blocks"


# ------------------------------------------------------------------------------------------------ reproducibility
def test_report_rendering_is_reproducible_and_says_it_authorises_nothing():
    doc = {"scope_title": "t", "attention": ["a"], "do_not_change": ["b"], "hypotheses": [], "expression": None, "limitations": ["c"]}
    one, two = WR.render_thesis(doc), WR.render_thesis(dict(doc))
    assert one == two and "RESEARCH ONLY" in one and "authorises" in one


def test_a_rebuild_of_the_same_evidence_is_byte_identical(tmp_path, monkeypatch):
    import importlib.util
    spec = importlib.util.spec_from_file_location("_wr", os.path.join(ROOT, "scripts", "research", "weekly_research.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod.WR, "render_board_edge", lambda d: "edge\n")
    monkeypatch.setattr(mod.WR, "render_script_autopsy", lambda d: "script\n")
    monkeypatch.setattr(mod.WR, "render_thesis", lambda d: "thesis\n")
    docs = ({"a": 1}, {"b": [2, 3]}, {"c": None}, [{"d": 4}])
    mod.write_scope(str(tmp_path / "one"), *docs)
    import time
    time.sleep(1.1)                                             # a different wall-clock second
    mod.write_scope(str(tmp_path / "two"), *docs)
    for name in ("BOARD_EDGE_DISCOVERY.md", "SCRIPT_AUTOPSY.md", "THESIS_IMPROVEMENT.md", "research.json.gz"):
        assert (tmp_path / "one" / name).read_bytes() == (tmp_path / "two" / name).read_bytes(), name
