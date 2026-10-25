import pytest

from nfl_edge.handicap import challenge as CH
from nfl_edge.handicap import expression as EX
from nfl_edge.handicap import staking as ST


def inp(**kw):
    d = dict(net_edge_low=0.03, fair_low=0.55, fair_high=0.65, challenge_clear=True, full_stake_executable=True, price_within_ceiling=True,
             winning_scripts=4, single_script_dependent=False, corroborations=(), family_eligibility="WATCH", model_market_gap=None)
    d.update(kw)
    return ST.StakeInputs(**d)


def test_ladder_tiers_and_what_stops_the_next_one():
    assert ST.decide(inp(net_edge_low=0.021)).units == 1
    assert ST.decide(inp(net_edge_low=0.05)).units == 2
    assert ST.decide(inp(net_edge_low=0.06, corroborations=("LINE_MOVE_TOWARD_US",))).units == 3
    d = ST.decide(inp(net_edge_low=0.08, corroborations=("LINE_MOVE_TOWARD_US", "INCUMBENT_AGREES"), family_eligibility="LIMITED"))
    assert d.units == 4
    assert ST.decide(inp(net_edge_low=0.12, corroborations=("LINE_MOVE_TOWARD_US", "INCUMBENT_AGREES", "TACTICAL_DATA"), family_eligibility="WATCH")).units == 3


def test_five_units_is_unreachable_without_a_trusted_family():
    best = ST.decide(inp(net_edge_low=0.20, corroborations=ST.CORROBORATIONS, family_eligibility="LIMITED"))
    assert best.units == 4 and any("TRUSTED" in u for u in best.unmet)
    assert ST.decide(inp(net_edge_low=0.20, corroborations=ST.CORROBORATIONS, family_eligibility="TRUSTED")).units == 5


def test_disagreement_alone_never_buys_a_stake_and_a_huge_gap_caps_at_1U():
    assert ST.decide(inp(flags=("DISAGREEMENT_ONLY",))).units == 0
    d = ST.decide(inp(net_edge_low=0.15, model_market_gap=0.25, corroborations=("LINE_MOVE_TOWARD_US", "INCUMBENT_AGREES")))
    assert d.units == 1 and any("0.10" in n for n in d.notes)


def test_blockers_give_zero_units_and_a_reason():
    assert ST.decide(inp(challenge_clear=False)).units == 0
    assert ST.decide(inp(full_stake_executable=False)).units == 0
    assert ST.decide(inp(price_within_ceiling=False)).units == 0
    assert ST.decide(inp(net_edge_low=0.01)).units == 0 and ST.decide(inp(net_edge_low=None, fair_low=None)).units == 0


def test_single_script_dependence_and_wide_ranges_limit_the_tier():
    assert ST.decide(inp(net_edge_low=0.06, single_script_dependent=True)).units == 1
    assert ST.decide(inp(net_edge_low=0.06, fair_low=0.45, fair_high=0.75)).units == 1          # width 0.30 steps 2U down to 1U


def test_units_are_dollars_at_75():
    assert ST.decide(inp(net_edge_low=0.05)).dollars == 150


def row(**kw):
    d = {"ticker": "KXNFLSPREAD-26OCT25AAABBB-BBB3", "family": "SPREAD", "subject": "BBB", "threshold": 2.5, "period": "FULL", "yes_ask": 0.50, "yes_bid": 0.48,
         "no_ask": 0.52, "no_bid": 0.50, "mid": 0.49, "width": 0.02, "executable": True, "yes_meaning": "YES iff BBB margin (FULL) > 2.5", "stat": "margin"}
    d.update(kw)
    return d


def test_bet_names_are_exact_and_side_correct():
    n = EX.bet_names(row(), "BBB", "AAA")
    assert n["YES"]["name"] == "BBB -2.5" or n["YES"]["name"].endswith("-2.5")           # BBB must win by 3+
    assert "+2.5" in n["NO"]["name"]                                                     # NO = the other team getting 2.5
    t = EX.bet_names(row(family="TOTAL", subject=None, threshold=44.0, yes_meaning="YES iff total_points (FULL) >= 44.0"), "BBB", "AAA")
    assert t["YES"]["name"] == "Game total Over 43.5" and t["NO"]["name"] == "Game total Under 43.5"
    ml = EX.bet_names(row(family="GAME_WINNER", threshold=None, subject="NO"), "NO", "PIT")
    assert "Saints" in ml["YES"]["name"]           # a team code can never be read as a YES/NO side


def test_a_wide_or_untraded_book_is_not_executable():
    assert EX.executable_book(row(width=0.12), "YES")[0] is False
    assert EX.executable_book(row(no_real_market=True), "YES")[0] is False
    assert EX.executable_book(row(yes_ask=None), "YES")[0] is False
    assert EX.executable_book(row(), "NO")[0] is True


def test_prices_are_the_side_specific_ask_never_the_mid():
    assert EX.side_prices(row(), "YES")["ask"] == 0.50 and EX.side_prices(row(), "NO")["ask"] == 0.52


def test_no_fair_estimate_means_unrankable():
    e = EX.evaluate_contract(row(), "YES", {"state": "NONE"}, None, None, "BBB", "AAA")
    assert e["status"] == "NO_DEFENSIBLE_FAIR_ESTIMATE" and e["rankable"] is False
    ranked = EX.rank([e])
    assert "no defensible fair-value estimate" in EX.reason_rejected(ranked[0], None)


def ev(**kw):
    d = {"side": "YES", "family": "SPREAD", "name": "x", "ticker": "T", "ask_cents": 50, "executable": True, "net_edge_low": 0.04, "ceiling_cents": 54,
         "edge_per_sd": 0.08, "width": 0.02, "scripts": {"matrix": [1], "winning_scripts": 4, "major_scripts": 6, "single_script_dependent": False,
                                                          "max_script_share_of_wins": 0.3}}
    d.update(kw)
    return d


def th(**kw):
    t = {"challenge": {"fail_modes": ["a", "b"], "market_already_priced": "has not moved", "matchup_check": "adjusted"},
         "evidence": {"measured": [{"claim": "c", "opponent_adjusted": True}]}}
    t.update(kw)
    return t


def call(e, alts=(), mode="LIVE", age=3.0, open_units=0.0, market=None, inj=None, thesis=None):
    return CH.challenge(thesis or th(), {}, e, list(alts), packet_market=market, player_injury=inj, quote_age_min=age, mode=mode, owner_open_units=open_units)


def test_a_clean_candidate_clears_all_ten_items():
    r = call(ev())
    assert r["cleared"] and len(r["items"]) == 10 and not r["open"] and not r["failed"]


def test_stale_quote_fails_live_but_is_only_flagged_in_rehearsal():
    assert call(ev(), age=40.0)["failed"] == ["C9"]
    r = call(ev(), age=40.0, mode="REHEARSAL")
    assert r["cleared"] and "C9" in r["flags"]


def test_a_superior_expression_fails_the_inferior_one():
    better = ev(name="better", edge_per_sd=0.20)
    assert "C8" in call(ev(), alts=[better])["failed"]


def test_price_already_moved_toward_us_opens_c2():
    r = call(ev(), market={"movement": {"total_move_since_first_capture": 0.07}})
    assert "C2" in r["open"] and not r["cleared"]


def test_single_script_dependence_fails_when_extreme_and_flags_when_moderate():
    assert "C6" in call(ev(scripts={"matrix": [1], "single_script_dependent": True, "max_script_share_of_wins": 0.85, "winning_scripts": 1, "major_scripts": 6}))["failed"]
    r = call(ev(scripts={"matrix": [1], "single_script_dependent": True, "max_script_share_of_wins": 0.55, "winning_scripts": 2, "major_scripts": 6}))
    assert "C6" in r["flags"] and r["cleared"]


def test_player_usage_requires_a_resolved_active_player_and_a_usage_record():
    p = ev(family="PLAYER_STAT")
    assert "C5" in call(p, inj={"status": "Questionable"})["open"]
    assert "C5" in call(p, inj={"status": "Out"})["failed"]
    assert "C5" in call(p, inj={"status": "Active"})["open"]                 # active but no usage record
    cand = {"usage": {"projected_opportunity": "8", "recent_usage": "9", "role_stability": "WR1", "teammate_context": "WR2 out"}}
    r = CH.challenge(th(), cand, p, [], packet_market=None, player_injury={"status": "Active"}, quote_age_min=3.0, mode="LIVE", owner_open_units=0.0)
    assert "C5" not in r["open"] + r["failed"]


def test_existing_exposure_is_flagged_and_a_full_game_cap_fails():
    assert "C10" in call(ev(), open_units=2.0)["flags"]
    assert "C10" in call(ev(), open_units=8.0)["failed"]


def test_missing_adjusted_evidence_blocks():
    t = th(evidence={"measured": []})
    r = call(ev(), thesis=t)
    assert "C4" in r["open"] and "C3" in r["open"]
