"""PR #241 (2026-11-03): the QB-dependency requirement and the guard with VERIFIED player identity (nfl_edge/postmortem/player_identity.py)."""
from datetime import timedelta

import pytest

from nfl_edge.postmortem import guards as GD
from nfl_edge.postmortem import player_identity as PI
from nfl_edge.postmortem import qb_dependency as QD
from test_qb_dependency import DEC, GATED, INDIRECT, NOT_GATED, auto_ident, both, cand, confirmed, ident, req

pytestmark = pytest.mark.owner_policy

RUSH = "KXNFLRSHYDS-26OCT25AAABBB-AAARB1-70"
RECV = "KXNFLRECYDS-26OCT25AAABBB-AAAWR1-60"
PASS = "KXNFLPASSYDS-26OCT25AAABBB-AAAQB1-250"


def test_a_verified_quarterbacks_rushing_prop_is_qb_gated_on_his_own_team_and_names_the_starter_it_needs():
    r = req(RUSH, teams=["AAA", "BBB"], player=ident("AAA", "QB", "00-AAA"))
    assert r.classification == GATED and r.rule == QD.RULE_QB_OWN_PROP and r.scope == QD.SCOPE_OWN and r.teams_required == ("AAA",)
    assert r.starter_player_id == "00-AAA" and r.starter_team == "AAA" and r.player_position_group == "QB" and r.identity_block is None
    assert r.requires_confirmation


def test_the_same_ticker_for_a_verified_running_back_is_not_gated():
    r = req(RUSH, teams=["AAA", "BBB"], player=ident("AAA", "RB"))
    assert r.classification == NOT_GATED and r.teams_required == () and not r.requires_confirmation


@pytest.mark.parametrize("pos", ["RB", "WR", "TE", "K", "LB", "DE", "CB"])
def test_every_other_verified_position_keeps_the_class_the_table_gives_the_statistic(pos):
    assert req(RUSH, teams=["AAA", "BBB"], player=ident("AAA", pos)).classification == NOT_GATED
    r = req(RECV, teams=["AAA", "BBB"], player=ident("BBB", pos))
    assert r.classification == INDIRECT and r.teams_required == ("BBB",)               # the VERIFIED team, not the ticker's


def test_a_quarterbacks_passing_prop_needs_both_quarterbacks_and_him_as_his_teams_starter():
    r = req(PASS, teams=["AAA", "BBB"], player=ident("AAA", "QB", "00-AAA"))
    assert r.classification == GATED and r.teams_required == ("AAA", "BBB") and r.starter_player_id == "00-AAA" and r.starter_team == "AAA"


@pytest.mark.parametrize("player", [None, {}, {"verified": False, "reason": "POSITION_UNKNOWN"}, "RB", [], {"verified": True}])
@pytest.mark.parametrize("ticker", [RUSH, RECV, PASS, "KXNFLFG-26OCT25AAABBB-AAAK1-2", "KXNFLTKL-26OCT25AAABBB-BBBLB1-8", "KXNFLANYTD-26OCT25AAABBB-AAAWR1"])
def test_a_player_prop_without_an_accepted_verified_identity_is_blocked_outright(ticker, player):
    r = req(ticker, teams=["AAA", "BBB"], player=player)
    assert r.identity_block and r.classification == GATED and r.requires_confirmation and r.teams_required == ("AAA", "BBB")
    out = GD.guard_candidate(cand(ticker, both(), player=player))                     # BOTH quarterbacks confirmed: still blocked
    assert not out["actionable"] and any(b.startswith("PLAYER_IDENTITY_UNVERIFIED:") for b in out["blocks"])


def test_a_forged_or_stale_verified_block_is_rejudged_and_refused():
    ok = ident("AAA", "RB")
    assert GD.guard_candidate(cand(RUSH, player=ok))["actionable"]
    for bad, why in ((ok | {"sources": []}, "IDENTITY_WITHOUT_PROVENANCE"), (ok | {"team": "ZZZ"}, "TEAM_NOT_IN_GAME"),
                     (ok | {"as_of": (DEC - timedelta(hours=30)).isoformat()}, "IDENTITY_STALE"),
                     (ok | {"as_of": (DEC + timedelta(minutes=5)).isoformat()}, "IDENTITY_AFTER_DECISION"),
                     (ok | {"position_group": "QB", "is_qb": True}, None)):
        out = GD.guard_candidate(cand(RUSH, player=bad))
        if why:
            assert f"PLAYER_IDENTITY_UNVERIFIED:{why}" in out["blocks"], (why, out["blocks"])
        else:                                    # relabelling him a QB (with provenance intact) makes the prop MORE gated, never less
            assert "QB_UNKNOWN:AAA" in out["blocks"]


def test_the_confirmed_starter_must_be_the_player_for_a_quarterback_prop():
    qb = ident("AAA", "QB", "00-AAA")
    assert GD.guard_candidate(cand(RUSH, {"AAA": confirmed("AAA")}, player=qb))["actionable"]
    backup = ident("AAA", "QB", "00-BACKUP")
    out = GD.guard_candidate(cand(RUSH, {"AAA": confirmed("AAA")}, player=backup))
    assert "QB_PLAYER_NOT_CONFIRMED_STARTER:AAA" in out["blocks"] and not out["actionable"]
    assert out["qb_requirement"]["starter_player_id"] == "00-BACKUP"
    # a QB under a running-back ticker, with the OPPOSING quarterback confirmed only
    out = GD.guard_candidate(cand(RUSH, {"BBB": confirmed("BBB")}, player=qb))
    assert "QB_UNKNOWN:AAA" in out["blocks"] and "QB_UNKNOWN:BBB" not in out["blocks"]


def test_a_confirmation_that_is_not_confirmed_never_satisfies_the_starter_check_it_only_adds_its_own_block():
    qb = ident("AAA", "QB", "00-AAA")
    out = GD.guard_candidate(cand(RUSH, {"AAA": confirmed("AAA", status="OUT", reason="WITHDRAWN_BY_LATER_OUT")}, player=qb))
    assert "QB_NOT_CONFIRMED:AAA" in out["blocks"] and "QB_REASON:AAA:WITHDRAWN_BY_LATER_OUT" in out["blocks"]


@pytest.mark.parametrize("ticker", ["KXNFLRSHYDSH2H-26OCT25AAABBB-X", "KXNFLMOSTRSHYDS-26OCT25AAABBB-AAARB1", "KXNFLMOSTRSHTD-26OCT25AAABBB-AAARB1"])
def test_field_markets_that_a_quarterback_can_win_are_gated_on_both_teams(ticker):
    r = req(ticker, teams=["AAA", "BBB"])
    assert r.classification == GATED and r.teams_required == ("AAA", "BBB"), ticker


def test_unknown_market_families_stay_fail_closed_with_or_without_an_identity():
    for t in ("KXNFLBRANDNEWSERIES-26OCT25AAABBB-X", "KXNFLNOVELPROP-26OCT25AAABBB-AAAWR1-5", "KXZZZ-26OCT25AAABBB-X"):
        for p in (None, ident("AAA", "RB")):
            r = QD.requirement(t, teams=["AAA", "BBB"], player=p, decision_time=DEC)
            assert r.classification == GATED and r.teams_required == ("AAA", "BBB"), (t, p is None)
            assert not GD.guard_candidate(cand(t, player=p))["actionable"]


def test_the_record_family_cannot_loosen_a_player_contract():
    r = QD.requirement(RUSH, family="TOTAL", teams=["AAA", "BBB"], player=ident("AAA", "RB"), decision_time=DEC, market_player_id="00-PAAA")
    assert r.classification == GATED and r.identity_block is None             # the strictest view (a total) still wins; the identity does not relax it


def test_is_player_scoped():
    assert QD.is_player_scoped(RUSH) and QD.is_player_scoped(None, "FIRST_TD_SCORER") and QD.is_player_scoped("KXNFLANYTD-26OCT25AAABBB-AAAWR1")
    assert not QD.is_player_scoped("KXNFLTOTAL-26OCT25AAABBB-45") and not QD.is_player_scoped(None) and not QD.is_player_scoped("KXNFLLONGFG-26OCT25AAABBB-50", "GAME_STAT")


def test_the_auto_identity_helper_agrees_with_the_verifier():
    assert auto_ident(RUSH)["position_group"] == "RB" and auto_ident(PASS)["position_group"] == "QB" and auto_ident("KXNFLTOTAL-26OCT25AAABBB-45") is None


# ---------------------------------------------------------------------------------------------------------------- binding to the market's own player id
def test_a_verified_block_for_another_player_than_the_markets_is_refused():
    ok = ident("AAA", "RB", "00-PAAA")
    out = GD.guard_candidate(cand(RUSH, player=ok) | {"player_id": "00-SOMEONE-ELSE"})
    assert "PLAYER_IDENTITY_UNVERIFIED:PLAYER_ID_MISMATCH" in out["blocks"] and not out["actionable"]
    out = GD.guard_candidate(cand(RUSH, player=ok) | {"player_id": None})
    assert "PLAYER_IDENTITY_UNVERIFIED:NO_PLAYER_ID" in out["blocks"]


# ---------------------------------------------------------------------------------------------------------------- the quarterback a confirmation names is cross-checked
def _qb_row(**chk):
    return confirmed("AAA") | {"qb_identity_check": chk}


@pytest.mark.parametrize("reason", ["PLAYER_NOT_IN_IDENTITY_SOURCE", "NAMED_STARTER_NOT_A_QUARTERBACK", "NAMED_STARTER_ON_ANOTHER_TEAM"])
def test_a_confirmed_starter_the_player_tables_do_not_show_as_a_qb_on_that_team_blocks(reason):
    out = GD.guard_candidate(cand("KXNFLTOTAL-26OCT25AAABBB-45", {"AAA": _qb_row(checked=True, ok=False, reason=reason), "BBB": confirmed("BBB")}))
    assert f"QB_NAMED_STARTER_NOT_VERIFIED:AAA:{reason}" in out["blocks"] and not out["actionable"]


def test_an_unchecked_cross_check_does_not_block_and_a_passed_one_does_not_either():
    for chk in ({"checked": False, "ok": None, "reason": "NO_IDENTITY_SOURCE"}, {"checked": True, "ok": True, "reason": None}):
        assert GD.guard_candidate(cand("KXNFLTOTAL-26OCT25AAABBB-45", {"AAA": _qb_row(**chk), "BBB": confirmed("BBB")}))["actionable"]


def test_verify_qb_against_a_real_book():
    book = PI.book_from_rows(players=[{"gsis_id": "00-Q", "position": "QB", "latest_team": "AAA", "display_name": "Q"},
                                      {"gsis_id": "00-R", "position": "RB", "latest_team": "AAA", "display_name": "R"},
                                      {"gsis_id": "00-O", "position": "QB", "latest_team": "BBB", "display_name": "O"}], season=2026)
    kw = dict(team="AAA", game_teams=["AAA", "BBB"], game_week=7, as_of=DEC)
    assert PI.verify_qb(book, qb_player_id="00-Q", **kw) == {"checked": True, "ok": True, "reason": None}
    assert PI.verify_qb(book, qb_player_id="00-R", **kw)["reason"] == "NAMED_STARTER_NOT_A_QUARTERBACK"
    assert PI.verify_qb(book, qb_player_id="00-O", **kw)["reason"] == "NAMED_STARTER_ON_ANOTHER_TEAM"
    assert PI.verify_qb(book, qb_player_id="00-X", **kw)["reason"] == "PLAYER_NOT_IN_IDENTITY_SOURCE"
    assert PI.verify_qb(PI.IdentityBook(), qb_player_id="00-Q", **kw)["checked"] is False and PI.verify_qb(None, qb_player_id="00-Q", **kw)["ok"] is None
