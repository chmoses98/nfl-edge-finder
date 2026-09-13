"""Season settlement settles only what the league's own output proves, and refuses everything else.

The three families here (wins through week W, division winner, playoff qualification) were the last projections
in v2 carrying a probability with no settlement path. Two of them are decided by the NFL tie-breaking procedure
that this repo deliberately does not reproduce, so the tests below exist mainly to prove the NEGATIVES: an
unresolved division, an unfinished bracket, a tie whose value the rules never pinned and a truncated schedule
must all refuse rather than guess.
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.engines.season import DIVISIONS as ENGINE_DIVISIONS                # noqa: E402
from nfl_edge.settlement import season_settlement as SS                          # noqa: E402
from nfl_edge.settlement.results import FINAL, NOT_FINAL, GameResult             # noqa: E402

SEASON = 2026
TEAMS = [t for ts in SS.DIVISIONS.values() for t in ts]


def g(gid, week, home, away, hs=None, aws=None, *, gtype="REG", final=True, season=SEASON):
    r = GameResult(game_id=gid, season=season, week=week, game_type=gtype, home_team=home, away_team=away,
                   home_score=hs, away_score=aws)
    r.status = FINAL if (final and hs is not None) else NOT_FINAL
    return r


def season_of(results_by_week, team="BUF", opp_cycle=("MIA", "NE", "NYJ")):
    """One team's schedule: week -> (points_for, points_against) or None for 'scheduled, not played'."""
    out = []
    for wk, res in sorted(results_by_week.items()):
        opp = opp_cycle[wk % len(opp_cycle)]
        if res is None:
            out.append(g(f"{SEASON}_{wk:02d}_{opp}_{team}", wk, team, opp, final=False))
        else:
            pf, pa = res
            out.append(g(f"{SEASON}_{wk:02d}_{opp}_{team}", wk, team, opp, pf, pa))
    return out


def q_wins(k, week, op=">="):
    return {"kind": "THRESHOLD", "stat": "wins_through_week", "op": op, "k": k, "notes": (f"through_week={week}",)}


# ---------------------------------------------------------------------------------- TEAM_WINS_BY_WEEK
def test_wins_through_week_settles_once_every_game_through_the_week_is_final():
    led = SS.SeasonLedger(season_of({1: (24, 10), 2: (17, 20), 3: (30, 27), 4: (13, 14)}), SEASON)
    r = SS.settle_wins_through_week("BUF", SEASON, q_wins(2, 4), led)
    assert r["status"] == "SETTLED" and r["settled_yes"] == 1.0 and r["evidence"]["wins"] == 2
    assert SS.settle_wins_through_week("BUF", SEASON, q_wins(3, 4), led)["settled_yes"] == 0.0


def test_wins_through_week_settles_early_when_no_remaining_game_can_change_the_answer():
    """Three wins already banked answers `>= 2` with two games still to play; it cannot answer `>= 4` yet."""
    led = SS.SeasonLedger(season_of({1: (24, 10), 2: (28, 20), 3: (30, 27), 4: None, 5: None}), SEASON)
    early = SS.settle_wins_through_week("BUF", SEASON, q_wins(2, 5), led)
    assert early["status"] == "SETTLED" and early["settled_yes"] == 1.0 and early["evidence"]["pending"] == 2
    impossible = SS.settle_wins_through_week("BUF", SEASON, q_wins(6, 5), led)
    assert impossible["status"] == "SETTLED" and impossible["settled_yes"] == 0.0, "3 wins + 2 games cannot reach 6"
    open_q = SS.settle_wins_through_week("BUF", SEASON, q_wins(4, 5), led)
    assert open_q["status"] == "REFUSED" and "not final" in open_q["reason"]


def test_a_tie_only_blocks_settlement_when_the_two_readings_disagree():
    led = SS.SeasonLedger(season_of({1: (24, 10), 2: (20, 20), 3: (30, 27)}), SEASON)
    amb = SS.settle_wins_through_week("BUF", SEASON, q_wins(2.5, 3), led)
    assert amb["status"] == "REFUSED" and "tie" in amb["reason"], "2 wins vs 2.5 with a tie: the readings disagree"
    assert SS.settle_wins_through_week("BUF", SEASON, q_wins(2, 3), led)["settled_yes"] == 1.0
    assert SS.settle_wins_through_week("BUF", SEASON, q_wins(4, 3), led)["settled_yes"] == 0.0


def test_a_truncated_schedule_refuses_rather_than_counting_the_games_it_can_see():
    """Weeks 1 and 5 present, 2-4 missing: two games through week 5 is not 4 or 5, so the count is untrustworthy."""
    led = SS.SeasonLedger(season_of({1: (24, 10), 5: (28, 20)}), SEASON)
    r = SS.settle_wins_through_week("BUF", SEASON, q_wins(2, 5), led)
    assert r["status"] == "REFUSED" and "not complete enough" in r["reason"]


def test_a_contract_without_a_stated_week_is_refused():
    led = SS.SeasonLedger(season_of({1: (24, 10)}), SEASON)
    r = SS.settle_wins_through_week("BUF", SEASON, {"kind": "THRESHOLD", "op": ">=", "k": 1, "notes": ()}, led)
    assert r["status"] == "REFUSED" and r["reason"] == SS.R_NO_WEEK


# ---------------------------------------------------------------------------------- bracket helpers
def full_regular_season(records: dict, weeks: int = 17):
    """Every team plays `weeks` games; `records` gives wins per team and the rest are losses."""
    games = []
    for t in TEAMS:
        w = records.get(t, 8)
        for i in range(weeks):
            hs, aws = (30, 10) if i < w else (10, 30)
            games.append(g(f"{SEASON}_{i + 1:02d}_X_{t}_{i}", i + 1, t, "OPP", hs, aws))
    return games


def bracket(afc_hosts, afc_bye, nfc_hosts, nfc_bye, afc_visitors, nfc_visitors, *, gtype="WC"):
    out = []
    for i, (h, a) in enumerate(list(zip(afc_hosts, afc_visitors)) + list(zip(nfc_hosts, nfc_visitors))):
        out.append(g(f"{SEASON}_19_{a}_{h}", 19, h, a, 24, 20, gtype=gtype))
    for i, b in enumerate([afc_bye, nfc_bye]):
        if b:
            out.append(g(f"{SEASON}_20_DIV_{b}", 20, b, afc_visitors[0] if i == 0 else nfc_visitors[0], 27, 24, gtype="DIV"))
    return out


AFC_HOSTS, AFC_BYE, AFC_VIS = ["BUF", "BAL", "HOU"], "KC", ["PIT", "IND", "DEN"]
NFC_HOSTS, NFC_BYE, NFC_VIS = ["PHI", "DET", "TB"], "SF", ["DAL", "GB", "LA"]
WINNERS = set(AFC_HOSTS + [AFC_BYE] + NFC_HOSTS + [NFC_BYE])
RECORDS = {**{t: 13 for t in WINNERS}, **{t: 10 for t in AFC_VIS + NFC_VIS}}


def complete_ledger():
    return SS.SeasonLedger(full_regular_season(RECORDS) + bracket(AFC_HOSTS, AFC_BYE, NFC_HOSTS, NFC_BYE, AFC_VIS, NFC_VIS), SEASON)


# ---------------------------------------------------------------------------------- DIVISION_WINNER
def test_division_winners_are_the_wild_card_hosts_plus_the_bye_teams():
    led = complete_ledger()
    b = led.bracket()
    assert b["division_winners_complete"] and set(b["derived_division_winners"]) == WINNERS
    for t in sorted(WINNERS):
        assert SS.settle_division_winner(t, SEASON, led)["settled_yes"] == 1.0
    for t in ("PIT", "DAL", "NYJ", "CHI"):
        r = SS.settle_division_winner(t, SEASON, led)
        assert r["status"] == "SETTLED" and r["settled_yes"] == 0.0


def test_a_wild_card_visitor_is_never_called_a_division_winner():
    led = complete_ledger()
    assert SS.settle_division_winner("PIT", SEASON, led)["settled_yes"] == 0.0, "PIT hosted nothing and had no bye"


def test_an_unfinished_bracket_refuses_instead_of_guessing_from_the_standings():
    """The regular season is over and eight teams clearly lead, but no postseason game exists yet."""
    led = SS.SeasonLedger(full_regular_season(RECORDS), SEASON)
    r = SS.settle_division_winner("BUF", SEASON, led)
    assert r["status"] == "REFUSED" and SS.R_BRACKET_INCOMPLETE in r["reason"]
    assert SS.settle_make_playoffs("NYJ", SEASON, led)["status"] == "REFUSED", "absence is not elimination without a complete bracket"


def test_a_half_scheduled_bracket_refuses():
    partial = bracket(AFC_HOSTS[:2], None, NFC_HOSTS[:1], None, AFC_VIS[:2], NFC_VIS[:1])
    led = SS.SeasonLedger(full_regular_season(RECORDS) + partial, SEASON)
    assert SS.settle_division_winner("BUF", SEASON, led)["status"] == "REFUSED"


def test_a_derived_winner_beaten_inside_its_own_division_is_a_contradiction_not_a_settlement():
    """CLE finishing ahead of BAL while BAL is derived as the AFC North winner means the bracket was misread."""
    recs = {**RECORDS, "CLE": 16}
    led = SS.SeasonLedger(full_regular_season(recs) + bracket(AFC_HOSTS, AFC_BYE, NFC_HOSTS, NFC_BYE, AFC_VIS, NFC_VIS), SEASON)
    r = SS.settle_division_winner("BAL", SEASON, led)
    assert r["status"] == "REFUSED" and SS.R_BRACKET_CONTRADICTS in r["reason"] and "CLE" in r["reason"]


def test_a_neutral_site_wild_card_game_refuses_the_derivation():
    games = full_regular_season(RECORDS) + bracket(AFC_HOSTS, AFC_BYE, NFC_HOSTS, NFC_BYE, AFC_VIS, NFC_VIS)
    wc = next(x for x in games if (x.game_type or "") == "WC")
    led = SS.SeasonLedger(games, SEASON, locations={wc.game_id: "Neutral"})
    r = SS.settle_division_winner("BUF", SEASON, led)
    assert r["status"] == "REFUSED" and "neutral" in r["reason"].lower()


# ---------------------------------------------------------------------------------- MAKE_PLAYOFFS
def test_playoff_qualification_is_proven_by_appearing_in_the_bracket():
    led = complete_ledger()
    for t in sorted(WINNERS | set(AFC_VIS) | set(NFC_VIS)):
        r = SS.settle_make_playoffs(t, SEASON, led)
        assert r["status"] == "SETTLED" and r["settled_yes"] == 1.0, t
    assert len(led.bracket()["participants"]) == 14


def test_elimination_needs_a_structurally_complete_bracket():
    led = complete_ledger()
    r = SS.settle_make_playoffs("NYJ", SEASON, led)
    assert r["status"] == "SETTLED" and r["settled_yes"] == 0.0 and "complete 14-team" in r["reason"]
    short = SS.SeasonLedger(full_regular_season(RECORDS) + bracket(AFC_HOSTS, AFC_BYE, NFC_HOSTS, None, AFC_VIS, NFC_VIS), SEASON)
    assert SS.settle_make_playoffs("NYJ", SEASON, short)["status"] == "REFUSED", "13 participants is not a bracket"


def test_a_lopsided_bracket_is_refused_even_at_the_right_total():
    """Fourteen participants that are not seven per conference means the postseason rows were misparsed."""
    games = full_regular_season(RECORDS) + bracket(AFC_HOSTS, AFC_BYE, NFC_HOSTS, NFC_BYE, AFC_VIS, NFC_VIS)
    games.append(g(f"{SEASON}_19_NYJ_NE", 19, "NE", "NYJ", 20, 17, gtype="WC"))
    led = SS.SeasonLedger(games, SEASON)
    b = led.bracket()
    assert not b["qualification_complete"] or not b["division_winners_complete"]
    assert SS.settle_make_playoffs("CHI", SEASON, led)["status"] == "REFUSED"


def test_an_unknown_franchise_is_refused_everywhere():
    led = complete_ledger()
    for fn in (lambda: SS.settle_make_playoffs("XXX", SEASON, led), lambda: SS.settle_division_winner("XXX", SEASON, led),
               lambda: SS.settle_wins_through_week("XXX", SEASON, q_wins(1, 3), led)):
        assert fn()["status"] == "REFUSED"


# ---------------------------------------------------------------------------------- wiring + invariants
def test_the_settlement_division_map_matches_the_projection_engines():
    assert {d: tuple(ts) for d, ts in ENGINE_DIVISIONS.items()} == {d: tuple(ts) for d, ts in SS.DIVISIONS.items()}
    assert len(SS.TEAM_DIVISION) == 32 and set(SS.TEAM_CONFERENCE.values()) == {"AFC", "NFC"}


def test_settle_v2_routes_the_three_families_and_the_catalog_now_calls_them_supported():
    from nfl_edge.semantics import catalog as CAT
    from nfl_edge.settlement import settle_v2 as S2
    from nfl_edge.settlement.results import ResultBook
    for fam in ("TEAM_WINS_BY_WEEK", "MAKE_PLAYOFFS", "DIVISION_WINNER"):
        assert CAT.catalog_entry(fam, "SEASON").settlement == CAT.SETTLE_SUPPORTED
    led = complete_ledger()
    book = ResultBook()
    rec = {"market_family": "MAKE_PLAYOFFS", "season": SEASON, "subject_id": "BUF", "semantic_confidence": "LIKELY",
           "question": {"kind": "EVENT", "event": "MAKE_PLAYOFFS"}}
    s = S2.settle_projection(rec, book, None, season_ledger=led)
    assert s.is_settled and s.settled_yes == 1.0
    miss = S2.settle_projection({**rec, "subject_id": "NYJ"}, book, None, season_ledger=led)
    assert miss.is_settled and miss.settled_yes == 0.0
    wins = S2.settle_projection({"market_family": "TEAM_WINS_BY_WEEK", "season": SEASON, "subject_id": "BUF",
                                 "semantic_confidence": "LIKELY", "question": q_wins(5, 10)}, book, None, season_ledger=led)
    assert wins.is_settled and wins.settled_yes == 1.0


def test_nothing_settles_from_an_empty_book():
    led = SS.SeasonLedger([], SEASON)
    assert SS.settle_make_playoffs("BUF", SEASON, led)["status"] == "REFUSED"
    assert SS.settle_division_winner("BUF", SEASON, led)["status"] == "REFUSED"
    assert SS.settle_wins_through_week("BUF", SEASON, q_wins(1, 3), led)["status"] == "REFUSED"


@pytest.mark.parametrize("op,k,expect", [(">=", 2, 1.0), (">", 2, 0.0), ("<=", 2, 1.0), ("<", 2, 0.0)])
def test_every_comparison_operator_is_settled_not_just_the_common_one(op, k, expect):
    led = SS.SeasonLedger(season_of({1: (24, 10), 2: (28, 20), 3: (10, 27)}), SEASON)
    r = SS.settle_wins_through_week("BUF", SEASON, q_wins(k, 3, op=op), led)
    assert r["status"] == "SETTLED" and r["settled_yes"] == expect
