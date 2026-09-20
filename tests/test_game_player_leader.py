"""KXNFLMOSTRECYDS / KXNFLMOSTRSHYDS are GAME markets, not season leaders.

The classifier read these two series from their TITLE -- "Pro Football Most Receiving Yards" -- and filed
them under SEASON_LEADER / SEASON. Every event is one game (`KXNFLMOSTRECYDS-26SEP20CINHOU`), every market
reads "<player>: most receiving yards in the CIN vs HOU game", and `rules_primary` names the game and the
comparison set explicitly. The consequences of the misclassification were not cosmetic: the contracts never
joined a scheduled game, so they could not be marked POST_KICKOFF, could not reach a settlement branch, and
carried the catalog reason "season / week aggregate read from the title" -- a statement about a market that
does not exist.

These tests pin the four things that were wrong, and the negative controls that keep the fix honest:

  1. the family, scope and period come from the EVENT TICKER, not from the series title;
  2. a genuinely week-scoped sibling (`KXNFLWEEKMOSTRECYDS-26W2`) is NOT swept up by the same rule;
  3. the question is an order statistic with a 1/N tie rule and PROVEN semantics;
  4. settlement is the argmax over every player in the game, refuses an incomplete stats release, and
     splits a tie -- and the catalog still says JOINT_MODEL_REQUIRED, because settlement being solved does
     not make the probability solved.
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.kalshi.classifier import classify  # noqa: E402
from nfl_edge.semantics.catalog import catalog_entry  # noqa: E402
from nfl_edge.semantics.questions import contract_question  # noqa: E402
from nfl_edge.settlement import settle_v2 as S2  # noqa: E402
from nfl_edge.settlement.reachability import DISPATCHABLE, reachability  # noqa: E402
from nfl_edge.settlement.results import result_book_from_records  # noqa: E402

RULES = ("If Ja'Marr Chase records the most Receiving Yards among all players in the game for the "
         "Cincinnati vs Houston Pro Football game originally scheduled for Sep 20, 2026, then the market "
         "resolves to Yes.")
RULES2 = ("If Ja'Marr Chase does not participate in the game the market will resolve to No. If multiple "
          "players tie for the most yards, the markets will resolve to 1/N, where N is the number of "
          "players tied for the highest value.")


def market(ticker="KXNFLMOSTRECYDS-26SEP20CINHOU-CINJCHASE1",
           event="KXNFLMOSTRECYDS-26SEP20CINHOU", series="KXNFLMOSTRECYDS", **kw):
    m = {"ticker": ticker, "event_ticker": event, "series_ticker": series,
         "title": "Ja'Marr Chase: most receiving yards in the CIN vs HOU game",
         "yes_sub_title": "Ja'Marr Chase", "rules_primary": RULES, "rules_secondary": RULES2,
         "custom_strike": {"football_player": "uuid-chase", "football_team": "uuid-cin"}}
    m.update(kw)
    return m


# ---------------------------------------------------------------- 1. taxonomy

def test_the_game_leader_series_are_game_scoped_not_season_leaders():
    s = classify(market())
    assert s.family == "GAME_PLAYER_LEADER"
    assert (s.scope, s.period) == ("GAME", "FULL")
    assert s.stat == "receiving_yards"
    # the thing that was actually broken: it now joins a scheduled game
    assert (s.game_date, s.away_team, s.home_team) == ("2026-09-20", "CIN", "HOU")
    assert s.player_kalshi_id == "uuid-chase"


def test_the_rushing_sibling_is_classified_the_same_way():
    s = classify(market(ticker="KXNFLMOSTRSHYDS-26SEP20CINHOU-CINCBROWN30",
                        event="KXNFLMOSTRSHYDS-26SEP20CINHOU", series="KXNFLMOSTRSHYDS"))
    assert (s.family, s.scope, s.period, s.stat) == ("GAME_PLAYER_LEADER", "GAME", "FULL", "rushing_yards")


def test_the_weekly_leader_sibling_is_NOT_swept_up_by_the_game_rule():
    """`KXNFLWEEKMOSTRECYDS-26W2` really is week-scoped: "most receiving yards in Pro Football Week 2".

    The negative control for the generic KXNFLMOST* rule. Scope is decided by the event ticker, and `26W2`
    is not a game, so this must keep WEEK_LEADER / WEEK.
    """
    s = classify(market(ticker="KXNFLWEEKMOSTRECYDS-26W2-WASTMCLAURIN17",
                        event="KXNFLWEEKMOSTRECYDS-26W2", series="KXNFLWEEKMOSTRECYDS"))
    assert s.family == "WEEK_LEADER" and s.scope == "WEEK"


def test_an_unlisted_KXNFLMOST_series_with_a_game_event_is_still_game_scoped():
    """The rule that stops the next one Kalshi lists from being read off its title the way these two were."""
    s = classify(market(ticker="KXNFLMOSTPASSYDS-26SEP20CINHOU-CINJBURROW9",
                        event="KXNFLMOSTPASSYDS-26SEP20CINHOU", series="KXNFLMOSTPASSYDS"))
    assert (s.family, s.scope, s.period, s.stat) == ("GAME_PLAYER_LEADER", "GAME", "FULL", "passing_yards")


def test_an_unlisted_KXNFLMOST_series_with_a_NON_game_event_is_not_claimed():
    s = classify(market(ticker="KXNFLMOSTSACKS-27-XYZ", event="KXNFLMOSTSACKS-27", series="KXNFLMOSTSACKS"))
    assert s.family != "GAME_PLAYER_LEADER"


# ---------------------------------------------------------------- 2. the question

def test_the_question_is_an_order_statistic_with_a_one_over_n_tie_rule():
    m = market()
    q = contract_question(classify(m), m)
    assert q.kind == "EVENT" and q.event == "GAME_STAT_LEADER"
    assert q.engine == "JOINT", "an argmax over players is not a function of one player's marginal"
    assert q.semantic_confidence == "PROVEN"
    assert q.tie_rule == "SPLIT_1_OVER_N"
    assert q.period == "FULL" and q.subject_kind == "player"


def test_the_catalog_proves_the_semantics_and_still_refuses_to_price_it():
    e = catalog_entry("GAME_PLAYER_LEADER", "FULL", "receiving_yards")
    assert e is not None
    assert e.semantic_confidence == "PROVEN"
    assert e.settlement == "SUPPORTED", "settlement is the argmax over a table we already load"
    assert e.model_support == "JOINT_MODEL_REQUIRED", (
        "solving settlement must not be mistaken for solving the probability: the question is an order "
        "statistic over every player in the game and no engine carries the full participating set")
    assert "order statistic" in e.reason


def test_a_leader_record_is_settlement_dispatchable():
    r = reachability({"market_family": "GAME_PLAYER_LEADER", "engine": "JOINT", "game_id": "2026_02_CIN_HOU",
                      "subject_id": "00-0036900", "p_yes": None, "support_state": "JOINT_MODEL_REQUIRED"})
    # no probability to settle, so the record says so rather than claiming a branch it will never use
    assert r["state"] in (DISPATCHABLE, "NO_PROBABILITY")
    r2 = reachability({"market_family": "GAME_PLAYER_LEADER", "engine": "JOINT", "game_id": "2026_02_CIN_HOU",
                       "subject_id": "00-0036900", "p_yes": 0.4, "support_state": "PROJECTABLE_NOT_YET_VALIDATED"})
    assert r2["state"] == DISPATCHABLE, r2
    r3 = reachability({"market_family": "GAME_PLAYER_LEADER", "engine": "JOINT", "game_id": "2026_02_CIN_HOU",
                       "subject_id": None, "p_yes": 0.4, "support_state": "PROJECTABLE_NOT_YET_VALIDATED"})
    assert r3["state"] != DISPATCHABLE, "an unresolved player cannot be compared against the field"


# ---------------------------------------------------------------- 3. settlement

SCHEDULE = (
    "game_id,season,game_type,week,gameday,gametime,away_team,home_team,away_score,home_score,result,total,overtime,espn\n"
    "2026_02_CIN_HOU,2026,REG,2,2026-09-20,13:00,CIN,HOU,20,24,4,44,0,401\n")


def _book(players, *, stats_complete=True):
    return result_book_from_records({
        "schedule_csv": SCHEDULE,
        "players": [{"player_id": p, "game_id": "2026_02_CIN_HOU", "team": "CIN",
                     "stats": {"receiving_yards": v}} for p, v in players],
        "snaps": [{"player_id": p, "game_id": "2026_02_CIN_HOU", "offense_snaps": 30}
                  for p, _ in players],
        "games_with_player_stats": ["2026_02_CIN_HOU"] if stats_complete else [],
        "games_with_snaps": ["2026_02_CIN_HOU"],
        "source": {"schedules": "test"},
    }, min_hours_after_kickoff=0.0)


def _record(subject):
    m = market()
    q = contract_question(classify(m), m)
    return {"question": q.to_dict(), "market_family": "GAME_PLAYER_LEADER", "period": "FULL",
            "game_id": "2026_02_CIN_HOU", "semantic_confidence": "PROVEN",
            "stat_family": "receiving_yards", "subject_id": subject, "season": 2026}


def test_the_leader_settles_yes_and_everyone_else_settles_no():
    book = _book([("A", 110.0), ("B", 64.0), ("C", 0.0)])
    assert S2.settle_projection(_record("A"), book).settled_yes == 1.0
    assert S2.settle_projection(_record("B"), book).settled_yes == 0.0
    assert S2.settle_projection(_record("C"), book).settled_yes == 0.0


def test_a_tie_pays_one_over_n_to_each_tied_player():
    book = _book([("A", 110.0), ("B", 110.0), ("C", 64.0)])
    a = S2.settle_projection(_record("A"), book)
    assert a.settled_yes == pytest.approx(0.5) and a.kind == S2.KIND_TIE_SPLIT
    assert S2.settle_projection(_record("C"), book).settled_yes == 0.0
    three = _book([("A", 70.0), ("B", 70.0), ("C", 70.0)])
    assert S2.settle_projection(_record("B"), three).settled_yes == pytest.approx(1 / 3)


def test_a_player_with_no_stats_row_settles_no_rather_than_refusing():
    """The rules' own NO branch: "if the player does not participate ... resolve to No"."""
    book = _book([("A", 110.0), ("B", 64.0)])
    s = S2.settle_projection(_record("NOBODY"), book)
    assert s.is_settled and s.settled_yes == 0.0


def test_an_incomplete_stats_release_refuses_instead_of_taking_a_partial_maximum():
    """THE failure mode of an order statistic: a maximum over a SUBSET settles confidently and wrongly.

    Two refusals, on purpose. The outer dispatcher never reaches the leader branch at all when the stats
    release is missing, because a game absent from the postgame tables is not independently proven complete
    -- defence in depth that exists for every family. The branch's own guard is asserted directly, so it
    still refuses if that outer proof is ever loosened or a caller reaches it another way.
    """
    book = _book([("A", 110.0), ("B", 64.0)], stats_complete=False)
    outer = S2.settle_projection(_record("A"), book)
    assert not outer.is_settled and outer.status == S2.REFUSED_NOT_FINAL

    q = _record("A")["question"]
    inner = S2._settle_game_player_leader(_record("A"), q, book, "2026_02_CIN_HOU",
                                          book.games["2026_02_CIN_HOU"])
    assert not inner.is_settled
    assert inner.status == S2.REFUSED_STATS_INCOMPLETE
    assert "cannot be taken from an incomplete table" in inner.reason


def test_a_game_where_nobody_recorded_the_statistic_is_refused_not_guessed():
    book = _book([("A", 0.0), ("B", 0.0)])
    s = S2.settle_projection(_record("A"), book)
    assert not s.is_settled and "not pinned by the rules text" in s.reason


def test_the_settlement_evidence_names_the_comparison_set():
    book = _book([("A", 110.0), ("B", 64.0)])
    ev = S2.settle_projection(_record("A"), book).evidence
    assert ev["players_compared"] == 2 and ev["max_value"] == 110.0 and ev["winners"] == ["A"]
    assert ev["stat"] == "receiving_yards"
    assert "every player" in ev["comparison_set"]


# ---------------------------------------------------------------- 4. the archive, end to end

FIXTURE = os.path.join(ROOT, "tests", "fixtures", "postgame", "ne_sea_2026_w1_game_leaders.json")


def _archive():
    import json
    with open(FIXTURE) as f:
        return json.load(f)


def test_every_settled_leader_leg_of_a_real_game_reproduces_the_exchanges_own_result():
    """The whole claim, against the exchange: 32 legs of 2026_01_NE_SEA, settled from nflverse alone.

    This is the evidence that the semantics are PROVEN rather than plausible. The fixture carries the real
    player stats for the game and Kalshi's own `result` for every KXNFLMOSTRECYDS / KXNFLMOSTRSHYDS leg;
    the settlement engine never sees the result. Over the whole 2026 archive the same check is 290 legs of
    32 events with zero disagreements -- the remaining 54 legs of that archive refuse on an unresolved
    Kalshi player id, which is a fail-closed refusal and not a settlement error.
    """
    fx = _archive()
    book = result_book_from_records(fx, min_hours_after_kickoff=0.0)
    checked = refused = 0
    for leg in fx["kalshi_legs"]:
        if not leg.get("gsis_id"):
            refused += 1
            continue
        sem = classify(leg)
        q = contract_question(sem, leg)
        assert sem.family == "GAME_PLAYER_LEADER" and q.semantic_confidence == "PROVEN", leg["ticker"]
        rec = {"question": q.to_dict(), "market_family": sem.family, "period": sem.period,
               "game_id": fx["game_id"], "semantic_confidence": q.semantic_confidence,
               "stat_family": sem.stat, "subject_id": leg["gsis_id"], "season": 2026}
        s = S2.settle_projection(rec, book)
        assert s.is_settled, f"{leg['ticker']}: {s.status} {s.reason}"
        want = 1.0 if leg["result"] == "yes" else 0.0
        assert s.settled_yes == pytest.approx(want), (
            f"{leg['ticker']}: engine {s.settled_yes} vs exchange {leg['result']} -- {s.reason}")
        checked += 1
    assert checked >= 25, f"only {checked} legs were checkable (refused {refused})"


def test_exactly_one_leg_of_each_leader_event_settled_yes():
    """One winner per event per statistic: the structural property an argmax must have."""
    fx = _archive()
    book = result_book_from_records(fx, min_hours_after_kickoff=0.0)
    yes_by_series = {}
    for leg in fx["kalshi_legs"]:
        if not leg.get("gsis_id"):
            continue
        sem = classify(leg)
        q = contract_question(sem, leg)
        rec = {"question": q.to_dict(), "market_family": sem.family, "period": sem.period,
               "game_id": fx["game_id"], "semantic_confidence": q.semantic_confidence,
               "stat_family": sem.stat, "subject_id": leg["gsis_id"], "season": 2026}
        s = S2.settle_projection(rec, book)
        if s.settled_yes:
            yes_by_series.setdefault(leg["series_ticker"], []).append(leg["ticker"])
    assert sorted(yes_by_series) == ["KXNFLMOSTRECYDS", "KXNFLMOSTRSHYDS"]
    for series, winners in yes_by_series.items():
        assert len(winners) == 1, f"{series} settled {len(winners)} legs YES: {winners}"


# ---------------------------------------------------------------- 5. the refusal says what is missing

def test_the_joint_engine_refuses_a_population_order_statistic_and_says_why():
    """A game leader is not a composite of enumerable legs, and it must not be handed to the period engine.

    It was: Shadow v2's dispatcher sent every non-composite JOINT question to the period engine, which
    replied "event 'GAME_STAT_LEADER' is not a period score function" -- a parser fault, where the truth is
    a modelling gap. 165 leader contracts of the 2026 week 2 board carried RESEARCH_REQUIRED ("no engine
    yet") instead of JOINT_MODEL_REQUIRED ("the dependence is not modelled"), which are different research
    problems and only one of them tells a reader what would have to be built.
    """
    from nfl_edge.engines import joint as JE
    m = market()
    q = contract_question(classify(m), m)
    route = JE.classify_legs(q)
    assert route["route"] is None
    assert "population" in route["reason"] and "composite" in route["reason"]
    ans = JE.answer(q, game_sim=None, period_sim=None, home="HOU", away="CIN")
    assert ans["p_yes"] is None
    assert ans["status"] == JE.JOINT_MODEL_REQUIRED


def test_the_catalog_decides_the_support_state_when_no_engine_answered():
    """`JOINT_MODEL_REQUIRED` in the catalog survives whatever the engine dispatch happened to try."""
    import scripts.shadow_v2.project_slate_v2 as P2
    m = market()
    q = contract_question(classify(m), m)
    entry = catalog_entry("GAME_PLAYER_LEADER", "FULL", "receiving_yards")
    state, reason, p, cv = P2.support_state(
        q, entry, pregame=True, confirmed=True, generated_before_kickoff=True, allow_historical=False,
        answer={"p_yes": None, "reason": "event 'GAME_STAT_LEADER' is not a period score function"})
    assert state == "JOINT_MODEL_REQUIRED", state
    assert "order statistic" in reason
    assert p is None and cv is None
