import numpy as np

from card_fixtures import CENTER, GAME, build_run, schedule_text
from nfl_edge.handicap import dossier as DS
from nfl_edge.handicap import fairvalue as FV


def gsim(draws=30000):
    bank, meta = FV.bank_from_schedule(schedule_text(), 2026)
    return FV.GameSim(bank, "BBB", "AAA", CENTER[0], CENTER[1], draws=draws)


def test_the_bank_needs_a_real_history():
    import pytest
    with pytest.raises(ValueError):
        FV.bank_from_schedule("game_id,season,game_type,result,spread_line,total,total_line,overtime\n", 2026)


def test_same_inputs_same_numbers_and_shifts_use_common_random_numbers():
    a, b = gsim(), gsim()
    row = {"family": "SPREAD", "subject": "BBB", "threshold": -2.5, "period": "FULL"}
    pa = FV.contract_probability(row, a.draw(0, 0), "BBB", "AAA")[0]
    assert pa == FV.contract_probability(row, b.draw(0, 0), "BBB", "AAA")[0]
    ps = [FV.contract_probability(row, a.draw(d, 0), "BBB", "AAA")[0] for d in (0, 1, 2, 3)]
    assert ps == sorted(ps), "a better home team can only raise a home spread cover"


def test_each_family_is_priced_from_the_one_distribution():
    g = gsim()
    s = g.draw(0, 0)
    ml = FV.contract_probability({"family": "GAME_WINNER", "subject": "BBB", "period": "FULL"}, s, "BBB", "AAA")[0]
    cover = FV.contract_probability({"family": "SPREAD", "subject": "BBB", "threshold": 0.5, "period": "FULL"}, s, "BBB", "AAA")[0]
    assert abs(ml - cover) < 1e-9                                   # margin > 0 and margin > 0.5 are the same event on integer margins
    over = FV.contract_probability({"family": "TOTAL", "threshold": 44.0, "period": "FULL"}, s, "BBB", "AAA")[0]
    team = FV.contract_probability({"family": "TEAM_TOTAL", "subject": "BBB", "threshold": 20.0, "period": "FULL"}, s, "BBB", "AAA")[0]
    assert 0.3 < over < 0.7 and 0.2 < team < 0.8


def test_period_player_and_event_markets_are_not_derived():
    s = gsim().draw(0, 0)
    for fam, per in (("SPREAD", "1H"), ("TOTAL", "1Q"), ("PLAYER_STAT", "FULL"), ("FIRST_TD_SCORER", "FULL"), ("WIN_MARGIN_BUCKET", "FULL")):
        p, why = FV.contract_probability({"family": fam, "period": per, "subject": "X", "threshold": 1.0}, s, "BBB", "AAA")
        assert p is None and why


def test_the_unshifted_engine_reproduces_a_market_built_from_itself_and_the_range_is_widened_by_noise(tmp_path):
    run = build_run(tmp_path)
    rows = [r for r in __import__("json").load(open(tmp_path / "analysis" / "games" / f"{GAME}.json"))["rows"]]
    g = gsim()
    noise = FV.baseline_check(rows, g.draw(0, 0), "BBB", "AAA")
    assert noise["SPREAD"]["rms_gap"] < 0.03 and noise["TOTAL"]["rms_gap"] < 0.03
    row = next(r for r in rows if r["family"] == "SPREAD" and r["subject"] == "BBB" and r["period"] == "FULL")
    fr = FV.fair_range(row, g, (1.0, 2.0), (0.0, 0.0), noise)
    assert fr["state"] == "DERIVED" and fr["p_low"] < fr["p_central"] < fr["p_high"] and fr["buffer"] >= 0.01
    assert FV.fair_range({"family": "PLAYER_STAT", "period": "FULL"}, g, (0, 0), (0, 0), noise)["state"] == "NOT_DERIVABLE"


def test_script_cells_partition_the_draws_and_match_the_packet_definitions():
    g = gsim()
    s = g.draw(0, 0)
    sc = FV.script_cells(s, "BBB", "AAA", CENTER[0], CENTER[1])
    assert sc["favorite"] == "AAA"                                   # BBB is a 3-point home underdog
    total = sum(m.sum() for m in sc["cells"].values())
    assert total == len(s["margin"]) and len(sc["cells"]) == 9
    ev = s["margin"] > 0
    mat = FV.script_matrix(ev, s, "BBB", "AAA", CENTER[0], CENTER[1])
    assert abs(sum(c["p_script"] for c in mat) - 1.0) < 1e-6


def test_dossier_matchup_sign_and_unavailable_list():
    game = {"game_id": "g", "kickoff_utc": "2026-10-25T17:00:00+00:00", "home_team": "H", "away_team": "A",
            "team_profiles": {"H": {"adjusted": {"off_db_epa": 0.10, "def_db_epa": -0.10, "off_sack_rate": 0.0, "def_sack_rate": 0.0}, "season_split": {"n_games": 6}},
                              "A": {"adjusted": {"off_db_epa": 0.0, "def_db_epa": -0.10, "off_sack_rate": 0.0, "def_sack_rate": 0.0}, "season_split": {"n_games": 6}}}}
    d = DS.build_dossier(game, {}, None)
    hv = next(x for x in d["team_matchups"]["H offence v A defence"] if x["matchup"] == "pass offence v pass defence")
    assert hv["advantage_to_offence"] == 0.0                        # +0.10 offence against a defence that allows 0.10 less than average
    joined = " ".join(d["unavailable"])
    for must in ("coverage", "blitz", "slot", "inside versus outside", "pass-block", "travel"):
        assert must in joined
    assert d["rest"] == {"status": "UNAVAILABLE"}


def test_triage_orders_but_never_removes():
    game = {"game_id": "g", "kickoff_utc": "x", "counts": {}, "coverage": {"totals": {"executable": 900}}}
    d = {"availability": {"by_team": {"A": [{"new_since_previous_capture": True}]}}, "qb_pressure": {"A": {"qb_status": "Out"}}, "market": {"model_spread_incumbent": 5.0, "implied_home_margin_median": -1.0},
         "team_matchups": {}, "weather": {"material": True}, "rest": {}, "sample": {"A": {"insufficient_sample": True}}}
    t = DS.triage(game, d)
    assert t["score"] > 0 and any("quarterback" in r for r in t["reasons"]) and any("weather" in r for r in t["reasons"]) and any("thin sample" in r for r in t["reasons"])


def test_a_quarterback_source_conflict_is_surfaced_not_resolved():
    game = {"game_id": "g", "kickoff_utc": "2026-10-25T17:00:00+00:00", "home_team": "H", "away_team": "A", "team_profiles": {"H": {}, "A": {}},
            "quarterbacks": {"H": [{"player": "Q One", "depth_chart_order": 1, "status": "Active", "profile": {}}], "A": []},
            "injuries": {"records": [{"team": "H", "player": "Q One", "position": "QB", "state": "Out", "espn_report_date": "2026-10-23"}], "summary": {}}}
    d = DS.build_dossier(game, {}, None)
    assert d["qb_pressure"]["H"]["qb_status"] == "CONFLICT" and "Out" in d["qb_pressure"]["H"]["conflict"]
    assert DS.triage(game, d)["score"] >= 3.0
