"""PR #241 (2026-11-03): the QB-dependency TABLE. Every market family the card can emit or an analyst can name has an explicit classification,
unknown fails closed, and each classification behaves as documented at the guard, the gate and the RUN NFL entry point.
"""
import json
from datetime import timedelta
from types import SimpleNamespace

import pytest

from card_fixtures import AS_OF, GAME
from nfl_edge.handicap import fairvalue as HFV
from nfl_edge.handicap import gates as G
from nfl_edge.handicap import packet as PK
from nfl_edge.handicap import schema as S
from nfl_edge.kalshi import classifier as K
from nfl_edge.postmortem import guards as GD
from nfl_edge.postmortem import player_identity as PI
from nfl_edge.postmortem import ontology as ONT
from nfl_edge.postmortem import qb_confirmations as QBC
from nfl_edge.postmortem import qb_dependency as QD

pytestmark = pytest.mark.owner_policy

DEC = AS_OF
KO = AS_OF + timedelta(hours=4)
GATED, INDIRECT, NOT_GATED = QD.QB_GATED, QD.QB_INDIRECT, QD.NOT_GATED


def confirmed(team, *, game_id=GAME, minutes_before_decision=20, **over):
    """A resolved CONFIRMED_STARTER row the way the resolver produces it (source, provenance, game_id, clocks)."""
    obs = (DEC - timedelta(minutes=minutes_before_decision)).isoformat()
    row = {"status": "CONFIRMED_STARTER", "confirmed_at": obs, "observed_at": obs, "captured_at": obs, "source": "HEAD_COACH_STATEMENT_ON_RECORD",
           "source_ref": "https://example.org/x", "record_id": f"r-{team}", "qb_player_id": f"00-{team}", "reason": None, "game_id": game_id, "team": team,
           "as_of": DEC.isoformat(), "kickoff_utc": KO.isoformat()}
    row.update(over)
    return row


# ---------------------------------------------------------------------------------------------------------------- verified player identity helpers
def ident(team, pos, gsis=None, *, teams=("AAA", "BBB"), as_of=DEC, **over):
    """A VERIFIED identity block produced by the real verifier from an inline players table (never hand-built)."""
    g = gsis or f"00-P{team}"
    book = PI.book_from_rows(players=[{"gsis_id": g, "position": pos, "latest_team": team, "display_name": "P"}], season=2026)
    r = PI.verify(book, player_id=g, game_teams=list(teams), game_week=7, as_of=as_of)
    assert r["verified"], r
    return r | over


def auto_ident(ticker, teams=("AAA", "BBB"), as_of=DEC):
    """The identity a market on ``ticker`` would carry if its player were looked up correctly: position from the series, team from the subject."""
    if not ticker or not QD.is_player_scoped(ticker):
        return None
    team = QD.own_team(ticker, list(teams)) or teams[0]
    series = ticker.split("-")[0]
    if "PASS" in series:
        return ident(team, "QB", f"00-{team}", teams=teams, as_of=as_of)
    pos = "RB" if "RSH" in series else "K" if "FG" in series else "LB" if ("TKL" in series or "SACK" in series) else "WR"
    return ident(team, pos, teams=teams, as_of=as_of)


def req(ticker, *, family=None, teams=None, player="auto", decision_time=DEC):
    if player == "auto":
        player = auto_ident(ticker, tuple(teams)) if teams and len(teams) == 2 else None
    return QD.requirement(ticker, family=family, teams=teams, player=player, decision_time=decision_time)


def cand(ticker, qb=None, *, family=None, game_id=GAME, teams=("AAA", "BBB"), player="auto"):
    return {"ticker": ticker, "family": family, "game_id": game_id, "side": "YES", "decision_time": DEC, "kickoff_utc": KO,
            "projection_as_of": DEC - timedelta(minutes=5), "injuries_as_of": DEC - timedelta(minutes=5), "qb": qb or {}, "teams": list(teams),
            "player": auto_ident(ticker, teams) if player == "auto" else player,
            "quote": {"price": 0.5, "captured_at": DEC - timedelta(minutes=1), "kind": "EXECUTABLE_ASK", "depth": 1000}, "contracts": 10}


def both(**kw):
    return {t: confirmed(t, **kw) for t in ("AAA", "BBB")}


# ---------------------------------------------------------------------------------------------------------------- the table is complete
def _classifier_family_stats():
    pairs = set()
    for series, (fam, scope, period, stat) in K.SERIES_FAMILY.items():
        pairs.add((fam, stat, scope))
    return pairs


def test_every_family_and_statistic_the_classifier_recognises_has_an_explicit_entry():
    missing = []
    for fam, stat, scope in sorted(_classifier_family_stats(), key=str):
        c, rule, why = QD.lookup(fam, stat)
        if rule == QD.RULE_UNCLASSIFIED:
            missing.append((fam, stat))
        assert c in QD.CLASSIFICATIONS and why
    assert not missing, f"families/statistics the classifier knows but the QB table does not (they would fail closed, but must be classified on purpose): {missing}"


def test_every_period_family_the_classifier_derives_has_an_entry():
    kinds = {"WINNER": "PERIOD_WINNER", "SPREAD": "SPREAD", "TOTAL": "TOTAL", "TEAMTOTAL": "TEAM_TOTAL", "BTTS": "BOTH_TEAMS_SCORE",
             "TD": "PERIOD_TD", "FT": "HALF_FULL_RESULT"}
    for kind, fam in kinds.items():
        assert QD.lookup(fam, None)[1] != QD.RULE_UNCLASSIFIED, fam
        series = f"KXNFL1H{'' if kind == 'WINNER' else kind}"
        assert K.PERIOD_RE.match(series)
        assert req(f"{series}-26OCT25AAABBB-AAA", teams=["AAA", "BBB"]).classification == GATED, series


def test_every_dynamic_family_the_classifier_can_assign_has_an_entry():
    for fam in ("SEASON_LEADER", "DIVISION_WINNER", "DRAFT", "SUPER_BOWL_EVENT", "GAME_PLAYER_LEADER", K.UNKNOWN, "NOT_NFL", "NOT_NFL_OR_UNKNOWN"):
        if fam == "GAME_PLAYER_LEADER":
            for stat in set(K.GAME_MOST_STATS.values()):
                assert QD.lookup(fam, stat)[1] == QD.RULE_STAT, stat
        else:
            assert QD.lookup(fam, None)[1] in (QD.RULE_FAMILY, QD.RULE_OUT_OF_SCOPE), fam


def test_every_family_the_card_packet_schema_and_ontology_name_has_an_entry():
    names = set(HFV.DERIVABLE) | set(PK.GAME_FAMILIES) | set(PK.PLAYER_FAMILIES) | set(S.PLAYER_MARKET_FAMILIES) | {"PERIOD_OTHER"}
    names |= {f for f in (ONT._series_info(s)[0] for s in list(K.SERIES_FAMILY) + ["KXNFL1HBTTS", "KXNFL1HTD", "KXNFL1HFT"]) if f}
    for fam in sorted(names):
        if fam == "PERIOD_OTHER":                       # the ontology's bucket for period BTTS / TD / full-time; the real names are in the classifier
            continue
        if fam in QD.STAT_LEVEL_FAMILIES:
            assert any(f == fam for f, _ in QD.STAT_TABLE), fam
        else:
            assert fam in QD.FAMILY_TABLE, f"{fam} has no QB-dependency entry"


def test_the_table_only_uses_the_three_classifications_and_gives_a_reason_for_each_entry():
    for key, (c, why) in list(QD.FAMILY_TABLE.items()) + list(QD.STAT_TABLE.items()):
        assert c in QD.CLASSIFICATIONS and len(why) > 15, key


def test_unknown_families_statistics_tickers_and_empty_input_fail_closed():
    for t in ("KXNFLBRANDNEWSERIES-26OCT25AAABBB-X", "KXZZZ-26OCT25AAABBB-X", "KXMVECROSSCATEGORY-26OCT25-ABC", "KXNFLNOVELPROP-26OCT25AAABBB-AAAWR1-5"):
        r = req(t, teams=["AAA", "BBB"])
        assert r.classification == GATED and r.requires_confirmation and r.teams_required == ("AAA", "BBB"), (t, r)
    for none in (None, "", "   "):
        r = req(none, teams=["AAA", "BBB"])
        assert r.classification == GATED and r.rule == QD.RULE_NO_TICKER
    r = req(None, family="NEVER_HEARD_OF_IT", teams=["AAA", "BBB"])
    assert r.classification == GATED
    assert QD.lookup("PLAYER_STAT", "brand_new_stat")[0] == GATED and QD.lookup("PLAYER_STAT", "brand_new_stat")[1] == QD.RULE_UNCLASSIFIED
    assert QD.lookup("TOTALLY_NEW_FAMILY")[0] == GATED


def test_the_records_own_family_can_only_tighten_never_loosen():
    # the ticker says kicker (NOT_GATED); a record that calls itself a total is still gated
    assert req("KXNFLFG-26OCT25AAABBB-AAAK1-2", teams=["AAA", "BBB"]).classification == NOT_GATED
    assert req("KXNFLFG-26OCT25AAABBB-AAAK1-2", family="TOTAL", teams=["AAA", "BBB"]).classification == GATED
    # the record says SPREAD, the ticker says anytime-TD: strictest wins
    assert req("KXNFLANYTD-26OCT25AAABBB-AAAWR1", family="SPREAD", teams=["AAA", "BBB"]).classification == GATED


# ---------------------------------------------------------------------------------------------------------------- the classification itself
# (ticker, classification, expected teams required for teams=[AAA, BBB]).  One row per family / statistic the card can emit or an analyst can name.
BOTH_T = ("AAA", "BBB")
TABLE = [
    # game winner, spread, total, team total, alternates (rungs of the same series)
    ("KXNFLGAME-26OCT25AAABBB-BBB", GATED, BOTH_T),
    ("KXNFLSPREAD-26OCT25AAABBB-BBB3", GATED, BOTH_T),
    ("KXNFLSPREAD-26OCT25AAABBB-AAA10", GATED, BOTH_T),
    ("KXNFLTOTAL-26OCT25AAABBB-45", GATED, BOTH_T),
    ("KXNFLTOTAL-26OCT25AAABBB-61", GATED, BOTH_T),
    ("KXNFLTEAMTOTAL-26OCT25AAABBB-BBB24", GATED, BOTH_T),
    # periods: 1H / 2H / quarters
    ("KXNFL1HWINNER-26OCT25AAABBB-AAA", GATED, BOTH_T), ("KXNFL1HSPREAD-26OCT25AAABBB-AAA3", GATED, BOTH_T),
    ("KXNFL1HTOTAL-26OCT25AAABBB-24", GATED, BOTH_T), ("KXNFL1HTEAMTOTAL-26OCT25AAABBB-AAA13", GATED, BOTH_T),
    ("KXNFL2HTOTAL-26OCT25AAABBB-22", GATED, BOTH_T), ("KXNFL1QSPREAD-26OCT25AAABBB-AAA1", GATED, BOTH_T),
    ("KXNFL2QTOTAL-26OCT25AAABBB-10", GATED, BOTH_T), ("KXNFL3QWINNER-26OCT25AAABBB-BBB", GATED, BOTH_T),
    ("KXNFL4QTEAMTOTAL-26OCT25AAABBB-BBB7", GATED, BOTH_T),
    ("KXNFL1HBTTS-26OCT25AAABBB-Y", GATED, BOTH_T), ("KXNFL2QTD-26OCT25AAABBB-1", GATED, BOTH_T), ("KXNFL1HFT-26OCT25AAABBB-AAAAAA", GATED, BOTH_T),
    # score-shaped specials
    ("KXNFLBOTH-26OCT25AAABBB-20", GATED, BOTH_T), ("KXNFLWINMARGIN-26OCT25AAABBB-BBB1", GATED, BOTH_T),
    ("KXNFLRACE-26OCT25AAABBB-10-BBB", GATED, BOTH_T), ("KXNFLTOTALTD-26OCT25AAABBB-5", GATED, BOTH_T),
    # touchdown / field-goal counts, first-TD team and time
    ("KXNFLTEAMTD-26OCT25AAABBB-AAA3", GATED, BOTH_T), ("KXNFLTEAMFG-26OCT25AAABBB-AAA2", GATED, BOTH_T), ("KXNFLGAMEFG-26OCT25AAABBB-5", GATED, BOTH_T),
    ("KXNFLGAMETD-26OCT25AAABBB-5", GATED, BOTH_T), ("KXNFLFIRSTTDTEAM-26OCT25AAABBB-AAA", GATED, BOTH_T), ("KXNFLTEAMFIRSTTD-26OCT25AAABBB-AAA", GATED, BOTH_T),
    ("KXNFLFIRSTTDTIME-26OCT25AAABBB-10", GATED, BOTH_T),
    # team statistics
    ("KXNFLTEAMYDS-26OCT25AAABBB-AAA300", GATED, BOTH_T), ("KXNFLTEAM1STDOWNS-26OCT25AAABBB-AAA20", GATED, BOTH_T),
    ("KXNFLTEAMSACK-26OCT25AAABBB-AAA3", GATED, BOTH_T), ("KXNFLTEAMTO-26OCT25AAABBB-AAA2", GATED, BOTH_T), ("KXNFLGAMESACK-26OCT25AAABBB-6", GATED, BOTH_T),
    ("KXNFLGAMETO-26OCT25AAABBB-4", GATED, BOTH_T),
    # game events
    ("KXNFLOT-26OCT25AAABBB-Y", GATED, BOTH_T), ("KXNFLOTWIN-26OCT25AAABBB-AAA", GATED, BOTH_T), ("KXNFLSAFETY-26OCT25AAABBB-Y", GATED, BOTH_T),
    ("KXNFL2PTCONV-26OCT25AAABBB-Y", GATED, BOTH_T), ("KXNFLLEADCHANGE-26OCT25AAABBB-3", GATED, BOTH_T), ("KXNFLCOMEBACK-26OCT25AAABBB-Y", GATED, BOTH_T),
    ("KXNFLNONQBPASS-26OCT25AAABBB-Y", GATED, BOTH_T), ("KXNFLTIES-26OCT25AAABBB-Y", GATED, BOTH_T), ("KXNFLDSTTD-26OCT25AAABBB-Y", GATED, BOTH_T),
    ("KXNFLLONGESTTD-26OCT25AAABBB-60", GATED, BOTH_T), ("KXNFLLONGESTREC-26OCT25AAABBB-60", GATED, BOTH_T), ("KXNFLSHORTESTTD-26OCT25AAABBB-1", GATED, BOTH_T),
    # combos / parlays (legs not readable from the ticker)
    ("KXNFLCOMBO-26OCT25AAABBB-X", GATED, BOTH_T), ("KXNFLPREPACKSGP-26OCT25AAABBB-X", GATED, BOTH_T), ("KXMVENFLSINGLEGAME-26OCT25AAABBB-X", GATED, BOTH_T),
    ("KXMVECROSSCATEGORY-26OCT25-ABC", GATED, BOTH_T),
    # quarterbacks' passing props and the team passing volume
    ("KXNFLPASSYDS-26OCT25AAABBB-AAAQB1-250", GATED, BOTH_T), ("KXNFLPASSTDS-26OCT25AAABBB-AAAQB1-2", GATED, BOTH_T),
    ("KXNFLPASSATT-26OCT25AAABBB-AAAQB1-30", GATED, BOTH_T), ("KXNFLPASSCOMP-26OCT25AAABBB-AAAQB1-20", GATED, BOTH_T),
    ("KXNFLPASSINT-26OCT25AAABBB-AAAQB1-1", GATED, BOTH_T), ("KXNFLINT-26OCT25AAABBB-AAAQB1-1", GATED, BOTH_T),
    ("KXNFLFFPTS-26OCT25AAABBB-AAAQB1-20", GATED, BOTH_T), ("KXNFLPASSYDSH2H-26OCT25AAABBB-X", GATED, BOTH_T), ("KXNFLRECYDSH2H-26OCT25AAABBB-X", GATED, BOTH_T),
    ("KXNFLFFH2H-26OCT25AAABBB-X", GATED, BOTH_T), ("KXNFLMOSTRECYDS-26OCT25AAABBB-AAAWR1", GATED, BOTH_T),
    # QB_INDIRECT: pass-catcher / scorer props, own team only
    ("KXNFLRECYDS-26OCT25AAABBB-AAAWR1-60", INDIRECT, ("AAA",)), ("KXNFLRECYDS-26OCT25AAABBB-BBBWR1-60", INDIRECT, ("BBB",)),
    ("KXNFLREC-26OCT25AAABBB-AAAWR1-5", INDIRECT, ("AAA",)), ("KXNFLRRYDS-26OCT25AAABBB-BBBRB1-80", INDIRECT, ("BBB",)),
    ("KXNFLLONGREC-26OCT25AAABBB-AAAWR1-30", INDIRECT, ("AAA",)), ("KXNFLANYTD-26OCT25AAABBB-BBBWR1", INDIRECT, ("BBB",)),
    ("KXNFLTD-26OCT25AAABBB-AAARB1", INDIRECT, ("AAA",)), ("KXNFL2TD-26OCT25AAABBB-AAARB1", INDIRECT, ("AAA",)),
    ("KXNFLFIRSTTD-26OCT25AAABBB-AAAWR1", INDIRECT, ("AAA",)), ("KXNFLNEXTTD-26OCT25AAABBB-BBBWR1", INDIRECT, ("BBB",)),
    # NOT_GATED: unrelated to the quarterback
    ("KXNFLRSHYDS-26OCT25AAABBB-AAARB1-70", NOT_GATED, ()), ("KXNFLRSHATT-26OCT25AAABBB-AAARB1-15", NOT_GATED, ()),
    ("KXNFLLONGRSH-26OCT25AAABBB-AAARB1-20", NOT_GATED, ()), ("KXNFLSACK-26OCT25AAABBB-BBBDE1-1", NOT_GATED, ()),
    ("KXNFLTKL-26OCT25AAABBB-BBBLB1-8", NOT_GATED, ()), ("KXNFLFG-26OCT25AAABBB-AAAK1-2", NOT_GATED, ()),
    ("KXNFLLONGFG-26OCT25AAABBB-50", NOT_GATED, ()), ("KXNFLLONGESTFG-26OCT25AAABBB-50", NOT_GATED, ()), ("KXNFLRSHYDSH2H-26OCT25AAABBB-X", GATED, BOTH_T),            # 2026-11-03: either player may be a QB
    ("KXNFLMOSTRSHYDS-26OCT25AAABBB-AAARB1", GATED, BOTH_T),         # 2026-11-03: the game's rushing leader can be a QB; field spans both teams
    # season / week / event scope: not a RUN NFL single-game contract, cannot be satisfied by a game confirmation
    ("KXSB-27-KC", GATED, BOTH_T), ("KXNFLWINS-27IND-9", GATED, BOTH_T), ("KXNFLMVP-27-X", GATED, BOTH_T), ("KXNFLDRAFTPICK-27-X", GATED, BOTH_T),
    ("KXNFLWEEKMOSTPASSYDS-26W7-X", GATED, BOTH_T),
]


@pytest.mark.parametrize("ticker,cls,teams_required", TABLE, ids=[t[0] for t in TABLE])
def test_classification_of_each_family(ticker, cls, teams_required):
    r = req(ticker, teams=["AAA", "BBB"])
    assert r.classification == cls, (ticker, r)
    assert r.teams_required == teams_required, (ticker, r)
    assert r.requires_confirmation is (cls != NOT_GATED)
    assert r.rationale


def test_a_pass_catchers_team_is_read_through_kalshi_codes_for_jacksonville_and_the_rams():
    # nflverse JAX / LA appear as JAC / LAR in Kalshi tickers
    assert req("KXNFLRECYDS-26OCT25LARJAC-JACWR1-60", teams=["LA", "JAX"]).teams_required == ("JAX",)
    assert req("KXNFLRECYDS-26OCT25LARJAC-LARWR1-60", teams=["LA", "JAX"]).teams_required == ("LA",)
    assert req("KXNFLRECYDS-26OCT25LACLAR-LACWR1-60", teams=["LAC", "LA"]).teams_required == ("LAC",)


def test_an_indirect_prop_whose_player_is_not_verified_is_blocked_and_one_whose_team_the_ticker_hides_uses_the_verified_team():
    # 2026-11-03: the team now comes from the VERIFIED identity (table), not the ticker; an unverified player is blocked outright
    r = req("KXNFLRECYDS-26OCT25AAABBB-WR1-60", teams=["AAA", "BBB"], player=None)
    assert r.identity_block and r.teams_required == ("AAA", "BBB") and r.requires_confirmation
    r = req("KXNFLRECYDS-26OCT25AAABBB-WR1-60", teams=["AAA", "BBB"], player=ident("BBB", "WR"))
    assert r.teams_required == ("BBB",) and r.identity_block is None
    assert req("KXNFLRECYDS-26OCT25AAABBB-AAAWR1-60", teams=[], player=None).teams_required == ()      # no teams at all: the guard blocks MISSING_TEAMS


# ---------------------------------------------------------------------------------------------------------------- the guard, per family
GATED_TICKERS = [t for t, c, _ in TABLE if c == GATED and not t.startswith(("KXSB", "KXNFLWINS", "KXNFLMVP", "KXNFLDRAFT", "KXNFLWEEK"))]
INDIRECT_TICKERS = [t for t, c, _ in TABLE if c == INDIRECT and "NONE" not in t]
NOT_GATED_TICKERS = [t for t, c, _ in TABLE if c == NOT_GATED]


@pytest.mark.parametrize("ticker", GATED_TICKERS)
def test_gated_family_with_unknown_quarterbacks_is_blocked_for_both_teams(ticker):
    out = GD.guard_candidate(cand(ticker))
    assert {"QB_UNKNOWN:AAA", "QB_UNKNOWN:BBB"} <= set(out["blocks"]) and not out["actionable"], (ticker, out["blocks"])
    assert out["qb_requirement"]["classification"] == GATED


@pytest.mark.parametrize("ticker", GATED_TICKERS)
def test_gated_family_with_both_quarterbacks_confirmed_is_actionable_and_carries_provenance(ticker):
    out = GD.guard_candidate(cand(ticker, both(game_id="G1"), game_id="G1"))
    assert out["actionable"], (ticker, out["blocks"])
    assert set(out["qb_provenance"]) == {"AAA", "BBB"} and out["qb_provenance"]["AAA"]["source"] == "HEAD_COACH_STATEMENT_ON_RECORD"


@pytest.mark.parametrize("ticker", GATED_TICKERS)
def test_gated_family_with_only_one_quarterback_confirmed_is_blocked(ticker):
    qb = {"AAA": confirmed("AAA")}
    out = GD.guard_candidate(cand(ticker, qb))
    assert "QB_UNKNOWN:BBB" in out["blocks"] and "QB_UNKNOWN:AAA" not in out["blocks"]


@pytest.mark.parametrize("ticker", INDIRECT_TICKERS)
def test_indirect_family_needs_only_its_own_teams_quarterback(ticker):
    own = req(ticker, teams=["AAA", "BBB"]).teams_required
    assert len(own) == 1
    assert not GD.guard_candidate(cand(ticker, {own[0]: confirmed(own[0])}))["blocks"], ticker
    blocked = GD.guard_candidate(cand(ticker))
    assert f"QB_UNKNOWN:{own[0]}" in blocked["blocks"] and not blocked["actionable"]
    other = "BBB" if own[0] == "AAA" else "AAA"
    assert f"QB_UNKNOWN:{other}" not in blocked["blocks"], "the opponent's quarterback is second-order for a pass-catcher and is not required"


@pytest.mark.parametrize("ticker", NOT_GATED_TICKERS)
def test_not_gated_family_is_never_blocked_by_an_unknown_quarterback(ticker):
    out = GD.guard_candidate(cand(ticker))
    assert not any(b.startswith("QB_") for b in out["blocks"]) and out["actionable"], (ticker, out["blocks"])
    assert out["qb_requirement"]["classification"] == NOT_GATED and out["qb_provenance"] == {}


@pytest.mark.parametrize("ticker", ["KXNFLBRANDNEWSERIES-26OCT25AAABBB-X", "KXMVECROSSCATEGORY-26OCT25-ABC", "KXNFLNOVELPROP-26OCT25AAABBB-AAAWR1-5", "", None])
def test_unclassified_input_is_blocked_not_waved_through(ticker):
    out = GD.guard_candidate(cand(ticker))
    assert not out["actionable"] and "QB_UNKNOWN:AAA" in out["blocks"] and "QB_UNKNOWN:BBB" in out["blocks"]


def test_the_legacy_require_qb_for_argument_can_only_add_requirements():
    t = "KXNFLFG-26OCT25AAABBB-AAAK1-2"
    assert GD.guard_candidate(cand(t))["actionable"]
    assert "QB_UNKNOWN:AAA" in GD.guard_candidate(cand(t), require_qb_for=("PLAYER_STAT",))["blocks"]      # the ontology family of a kicker prop
    # an explicit empty tuple does NOT switch the check off for a gated family
    assert not GD.guard_candidate(cand("KXNFLTOTAL-26OCT25AAABBB-45"), require_qb_for=())["actionable"]


def test_the_compat_gated_family_names_cover_every_score_family():
    for fam in ("GAME_WINNER", "SPREAD", "TOTAL", "TEAM_TOTAL", "WIN_MARGIN_BUCKET", "BOTH_TEAMS_SCORE_N", "RACE_TO_N", "TOTAL_TD", "BOTH_TEAMS_SCORE",
                "PERIOD_WINNER", "PERIOD_TD", "HALF_FULL_RESULT", "FIRST_TD_TEAM", "GAME_EVENT", "TEAM_STAT"):
        assert fam in GD.QB_GATED_FAMILIES, fam


# ---------------------------------------------------------------------------------------------------------------- the real gate (gates.evaluate_gates)
def _rec(ticker, family, qb=None, teams=("AAA", "BBB"), player="auto"):
    return {"decision": "RECOMMENDED", "created_at": DEC.isoformat(), "market_ticker": ticker, "market_family": family, "side": "YES",
            "kickoff_utc": KO.isoformat(), "game_id": "G1",
            "pit_evidence": {"teams": list(teams), "game_id": "G1", "qb": qb or {}, "player_identity": auto_ident(ticker, teams) if player == "auto" else player, "projection_as_of": (DEC - timedelta(minutes=5)).isoformat(),
                             "injuries_as_of": (DEC - timedelta(minutes=5)).isoformat()}}


@pytest.mark.parametrize("ticker,family", [("KXNFLPASSYDS-26OCT25AAABBB-AAAQB1-250", "PLAYER_STAT"), ("KXNFLPASSATT-26OCT25AAABBB-AAAQB1-30", "PLAYER_STAT"),
                                           ("KXNFLRECYDS-26OCT25AAABBB-AAAWR1-60", "PLAYER_STAT"), ("KXNFLANYTD-26OCT25AAABBB-AAAWR1", "PLAYER_STAT"),
                                           ("KXNFLFIRSTTD-26OCT25AAABBB-AAAWR1", "FIRST_TD_SCORER")])
def test_qb_dependent_player_props_are_judged_by_the_pit_gate(ticker, family):
    rep = G.evaluate_gates(_rec(ticker, family), G.GateContext())
    assert rep.gates[G.G_PIT].status == G.FAIL and "QB_UNKNOWN:AAA" in rep.gates[G.G_PIT].evidence["blocks"]
    assert rep.gates[G.G_ORDER_CEILING].status == G.NOT_APPLICABLE            # the order-size ceiling stays game-level only
    assert rep.gates[G.G_PIT].evidence["qb_requirement"]["table_version"] == QD.TABLE_VERSION


@pytest.mark.parametrize("ticker", ["KXNFLRSHYDS-26OCT25AAABBB-AAARB1-70", "KXNFLFG-26OCT25AAABBB-AAAK1-2", "KXNFLTKL-26OCT25AAABBB-BBBLB1-8",
                                    "KXNFLSACK-26OCT25AAABBB-BBBDE1-1"])
def test_unrelated_player_props_keep_only_their_own_gate(ticker):
    rep = G.evaluate_gates(_rec(ticker, "PLAYER_STAT"), G.GateContext())
    assert rep.gates[G.G_PIT].status == G.NOT_APPLICABLE and "player_availability_resolved" in rep.gates[G.G_PIT].reason


def test_a_qb_dependent_prop_passes_the_pit_gate_when_its_own_quarterback_is_confirmed():
    from nfl_edge.postmortem import integration as PM
    dq = SimpleNamespace(is_actionable=True, executable_price=0.5, confirmed_at=(DEC - timedelta(minutes=2)).isoformat())
    dr = SimpleNamespace(is_executable=True, contracts_required=100)
    rec = _rec("KXNFLRECYDS-26OCT25AAABBB-AAAWR1-60", "PLAYER_STAT", qb={"AAA": confirmed("AAA", game_id="G1")})
    st, why, ev = PM.pit_gate(rec, dq=dq, dr=dr, as_of=DEC)
    assert st == "PASS", (why, ev)
    assert ev["qb_provenance"]["AAA"]["record_id"] == "r-AAA" and set(ev["qb_provenance"]) == {"AAA"}


def test_unclassifiable_player_family_record_is_judged_not_skipped():
    rec = _rec("KXNFLNOVELPROP-26OCT25AAABBB-AAAWR1-5", "PLAYER_STAT")
    assert G.evaluate_gates(rec, G.GateContext()).gates[G.G_PIT].status == G.FAIL


def test_old_records_without_pit_evidence_are_still_not_rejudged():
    rec = _rec("KXNFLPASSYDS-26OCT25AAABBB-AAAQB1-250", "PLAYER_STAT")
    rec.pop("pit_evidence")
    assert G.evaluate_gates(rec, G.GateContext()).gates[G.G_PIT].status == G.NOT_APPLICABLE


def test_the_table_is_serialisable_and_versioned():
    d = req("KXNFLRECYDS-26OCT25AAABBB-AAAWR1-60", teams=["AAA", "BBB"]).to_dict()
    json.dumps(d)
    assert d["table_version"] == QD.TABLE_VERSION and d["classification"] == INDIRECT and d["scope"] == QD.SCOPE_OWN


def test_qbc_constants_are_what_the_docs_say():
    assert QBC.MAX_AGE_AT_DECISION_MIN == 24 * 60 and QBC.MAX_LEAD_BEFORE_KICKOFF_MIN == 48 * 60
