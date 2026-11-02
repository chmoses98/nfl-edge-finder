"""Issue #231: ontology + correlated exposure. Synthetic positions only (no owner stakes)."""
from nfl_edge.postmortem import exposure as X
from nfl_edge.postmortem.common import DAILY_EXPOSURE_FLAG_UNITS, GAME_EXPOSURE_FLAG_UNITS, UNIT_DOLLARS
from nfl_edge.postmortem.ontology import COMBO_DECODED, COMBO_UNDECODED, SINGLE, classify_ticker


def pos(t, side, units, day="2026-10-25"):
    return {"ticker": t, "side": side, "stake": units * UNIT_DOLLARS, "game_date": day}


def test_cross_category_combo_without_legs_is_undecoded_not_a_game():
    o = classify_ticker("KXMVECROSSCATEGORY0-S2026XXXX-ABC")
    assert o.kind == COMBO_UNDECODED and "MISSING_COMBO_LEGS" in o.flags and o.game_key is None


def test_combo_decodes_only_from_supplied_legs():
    legs = [{"ticker": "KXNFLSPREAD-26OCT25SFATL-SF3", "side": "YES"}, {"ticker": "KXNFLTOTAL-26OCT25SFATL-45", "side": "NO"}]
    o = classify_ticker("KXMVECROSSCATEGORY0-S2026XXXX-ABC", legs=legs)
    assert o.kind == COMBO_DECODED and o.games == ("26OCT25SFATL",)
    bad = classify_ticker("KXMVECROSSCATEGORY0-S2026XXXX-ABC", legs=[{"ticker": "", "side": "YES"}])
    assert bad.kind == COMBO_UNDECODED


def test_period_and_family_ontology():
    assert classify_ticker("KXNFL1HSPREAD-26OCT25SFATL-SF3").period == "1H"
    assert classify_ticker("KXNFL1QTOTAL-26OCT25SFATL-10").family == "TOTAL"
    assert classify_ticker("KXNFLTEAMTOTAL-26OCT25SFATL-SF24").family == "TEAM_TOTAL"
    o = classify_ticker("KXNOTATHING-26OCT25SFATL-X")
    assert o.kind != SINGLE and "SERIES_NOT_IN_TAXONOMY" in o.flags


def test_same_team_spread_ladder_groups_and_flags_over_five_units():
    r = X.aggregate([pos("KXNFLSPREAD-26OCT25SFATL-SF3", "YES", 3.34), pos("KXNFLSPREAD-26OCT25SFATL-SF4", "YES", 2.0)])
    g = r["games"]["26OCT25SFATL"]
    assert [x["axis"] for x in g["groups"]] == ["MARGIN:SF"] and g["groups"][0]["n_distinct_contracts"] == 2
    assert g["flag_over_game_limit"] and g["groups"][0]["flag_over_group_limit"]
    assert {f["kind"] for f in r["flags"]} == {"GAME_OVER_LIMIT", "GROUP_OVER_LIMIT"}


def test_no_on_opponent_spread_is_the_same_thesis_and_1h_shares_the_axis():
    r = X.aggregate([pos("KXNFLSPREAD-26OCT25SFATL-ATL3", "NO", 2.0), pos("KXNFL1HSPREAD-26OCT25SFATL-SF3", "YES", 1.0)])
    (grp,) = r["games"]["26OCT25SFATL"]["groups"]
    assert grp["axis"] == "MARGIN:SF" and grp["gross_units"] == 3.0 and grp["periods"] == ["1H", "FULL"]


def test_independent_theses_are_not_merged_and_exactly_five_is_not_flagged():
    r = X.aggregate([pos("KXNFLSPREAD-26OCT25SFATL-SF3", "YES", 3.0), pos("KXNFLTOTAL-26OCT25SFATL-45", "YES", 2.0)])
    g = r["games"]["26OCT25SFATL"]
    assert len(g["groups"]) == 2 and g["units_total"] == 5.0 and not g["flag_over_game_limit"] and r["flags"] == []


def test_team_total_over_is_linked_to_its_teams_margin_but_not_merged():
    r = X.aggregate([pos("KXNFLSPREAD-26OCT25SFATL-SF3", "YES", 2.0), pos("KXNFLTEAMTOTAL-26OCT25SFATL-SF24", "YES", 2.0)])
    by = {g["axis"]: g for g in r["games"]["26OCT25SFATL"]["groups"]}
    assert by["TEAMSCORE:SF:OVER"]["linked_axes"] == ["MARGIN:SF"] and by["TEAMSCORE:SF:OVER"]["linked_combined_units"] == 4.0
    assert by["MARGIN:SF"]["gross_units"] == 2.0


def test_daily_flag_includes_undecoded_combos_and_is_not_a_cap():
    ps = [pos("KXNFLSPREAD-26OCT25SFATL-SF3", "YES", 5.0), pos("KXNFLSPREAD-26OCT25DENKC-KC3", "YES", 5.0),
          pos("KXNFLSPREAD-26OCT25NYGDAL-DAL3", "YES", 4.0), pos("KXMVECROSSCATEGORY0-S2026XXXX-ABC", "YES", 2.0)]
    r = X.aggregate(ps)
    d = r["days"]["2026-10-25"]
    assert d["units_total"] == 16.0 and d["flag_over_daily_limit"] and d["undecoded_combo_units"] == 2.0
    assert DAILY_EXPOSURE_FLAG_UNITS == 15.0 and GAME_EXPOSURE_FLAG_UNITS == 5.0
    assert "UNATTRIBUTED_COMBOS" in r["games"] and not r["games"]["UNATTRIBUTED_COMBOS"]["flag_over_game_limit"]


def test_bad_rows_are_reported_not_raised():
    r = X.aggregate([{"ticker": "KXNFLSPREAD-26OCT25SFATL-SF3", "side": "YES"}])
    assert r["unprocessed"] == [{"index": 0, "reason": "MISSING_STAKE"}]
