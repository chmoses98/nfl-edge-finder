"""Settlement must be proven or refused, on real final results.

Every number asserted here comes from the nflverse release for 2025 week 1, Dallas at Philadelphia (DAL 20,
PHI 24, no overtime) -- see tests/fixtures/postgame/dal_phi_2025_w1.results.json. Nothing is invented, so a
test that passes is evidence about real settlement rather than about a mock.

The refusals matter as much as the settlements. A pipeline that guesses a 0 where it cannot prove one produces
a corpus whose calibration numbers are quietly wrong forever, and no later test can find that.
"""
import copy
import json
import os

import pytest

from nfl_edge.settlement import settle as S
from nfl_edge.settlement.final_status import ESPN_SCOREBOARD, FinalAttestation, POSTGAME_TABLES
from nfl_edge.settlement.results import (
    DEFER_FINAL_UNPROVEN, DEFER_NOT_FINAL, DEFER_SNAPS_PENDING, DEFER_STATS_PENDING, DEGRADED_INCONSISTENT,
    FINAL, READY, PlayerGameResult, games_from_schedule_text, result_book_from_records,
)

GAME = "2025_01_DAL_PHI"
FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "postgame", "dal_phi_2025_w1.results.json")
HURTS = "00-0036389"
BARKLEY = "00-0034844"
LAMB = "00-0036358"
CALCATERRA = "00-0037086"          # 37 offensive snaps, no statistics row: a proven zero
NOT_IN_GAME = "00-0000001"


@pytest.fixture
def records():
    with open(FIXTURE) as f:
        rec = json.load(f)
    rec["game_id"] = GAME
    return rec


@pytest.fixture
def book(records):
    return result_book_from_records(records)


def obs(**kw):
    d = {"prediction_id": "p", "ticker": "T", "game_id": GAME, "family": "PLAYER_STAT", "period": "FULL",
         "direction": "YES", "operator": ">="}
    d.update(kw)
    return d


# ---------------------------------------------------------------- the game itself
def test_the_fixture_is_the_real_final_result(book):
    g = book.games[GAME]
    assert (g.status, g.away_team, g.away_score, g.home_team, g.home_score) == (FINAL, "DAL", 20.0, "PHI", 24.0)
    assert g.total_points == 44.0 and g.margin_for("PHI") == 4.0 and g.margin_for("DAL") == -4.0
    assert g.kickoff_utc == "2025-09-05T00:20:00+00:00", "20:20 US-Eastern on 2025-09-04 is 00:20 UTC"


def test_an_unplayed_game_is_never_final(book):
    assert book.games["2026_01_NE_SEA"].status != FINAL
    state, reason = book.readiness("2026_01_NE_SEA", needs_player_stats=True)
    assert state == DEFER_NOT_FINAL and "no final score" in reason


def test_readiness_defers_when_player_tables_are_not_published_yet(records):
    """The dangerous case: the score is out, the statistics are not. Nothing may be written."""
    no_stats = dict(records, games_with_player_stats=[])
    assert result_book_from_records(no_stats).readiness(GAME, needs_player_stats=True)[0] == DEFER_STATS_PENDING
    no_snaps = dict(records, games_with_snaps=[])
    assert result_book_from_records(no_snaps).readiness(GAME, needs_player_stats=True)[0] == DEFER_SNAPS_PENDING
    # A game whose predictions are all team markets does not wait for player STATISTICS -- but it still needs
    # something independent to attest that the game is complete, and the postgame tables are that attestation.
    assert result_book_from_records(no_stats).readiness(GAME, needs_player_stats=False)[0] == DEFER_FINAL_UNPROVEN


def test_a_game_is_not_ready_until_it_has_plausibly_finished(records):
    from datetime import datetime, timedelta, timezone
    book = result_book_from_records(records, min_hours_after_kickoff=4.0)
    ko = datetime.fromisoformat(book.games[GAME].kickoff_utc)
    assert book.readiness(GAME, needs_player_stats=True, now=ko + timedelta(hours=1))[0] == DEFER_NOT_FINAL
    assert book.readiness(GAME, needs_player_stats=True, now=ko + timedelta(hours=5))[0] == READY


def test_a_schedule_row_that_contradicts_itself_is_refused_not_settled(records):
    """`result` is home - away. If the source disagrees with its own scores, nothing is settled from it."""
    rec = copy.deepcopy(records)
    rows = rec["schedule_csv"].splitlines()
    header = rows[0].split(",")
    i_result = header.index("result")
    fixed = []
    for line in rows[1:]:
        cells = line.split(",")
        if cells[0] == GAME:
            cells[i_result] = "99"
        fixed.append(",".join(cells))
    rec["schedule_csv"] = "\n".join([rows[0]] + fixed)
    book = result_book_from_records(rec)
    assert book.readiness(GAME, needs_player_stats=False)[0] == DEGRADED_INCONSISTENT
    st = S.settle_observation(obs(family="TOTAL", threshold=40), book)
    assert st.status == S.REFUSED_RESULT_INCONSISTENT and st.settled_yes is None


# ---------------------------------------------------------------- team families
def test_game_winner_settles_from_the_margin(book):
    assert S.settle_observation(obs(family="GAME_WINNER", operator="event", team="PHI"), book).settled_yes == 1.0
    assert S.settle_observation(obs(family="GAME_WINNER", operator="event", team="DAL"), book).settled_yes == 0.0


def test_a_tied_game_pays_fifty_cents_to_both_sides(records):
    """Documented from Kalshi's rules and confirmed by the 2025 archive (GB at DAL, week 4)."""
    rec = copy.deepcopy(records)
    rows = rec["schedule_csv"].splitlines()
    h = rows[0].split(",")
    ia, ih, ir, it = h.index("away_score"), h.index("home_score"), h.index("result"), h.index("total")
    out = []
    for line in rows[1:]:
        c = line.split(",")
        if c[0] == GAME:
            c[ia] = c[ih] = "20"
            c[ir] = "0"
            c[it] = "40"
        out.append(",".join(c))
    book = result_book_from_records({**rec, "schedule_csv": "\n".join([rows[0]] + out)})
    for team in ("PHI", "DAL"):
        st = S.settle_observation(obs(family="GAME_WINNER", operator="event", team=team), book)
        assert (st.settled_yes, st.kind) == (0.5, S.KIND_TIE_SPLIT)


def test_spread_uses_more_than_the_floor_so_the_exact_floor_loses(book):
    """"wins by more than 3.5" and "more than 4" are different contracts on a 4-point win."""
    won_by_more = S.settle_observation(obs(family="SPREAD", operator=">", team="PHI", floor_strike=3.5), book)
    assert won_by_more.settled_yes == 1.0
    exact = S.settle_observation(obs(family="SPREAD", operator=">", team="PHI", floor_strike=4.0), book)
    assert exact.settled_yes == 0.0, "a 4-point win is not 'more than 4'"
    assert S.settle_observation(obs(family="SPREAD", operator=">", team="DAL", floor_strike=-7.5),
                               book).settled_yes == 1.0, "DAL -4 beats a +7.5 cushion"


def test_total_and_team_total_and_both_teams_score(book):
    assert S.settle_observation(obs(family="TOTAL", threshold=44), book).settled_yes == 1.0
    assert S.settle_observation(obs(family="TOTAL", threshold=45), book).settled_yes == 0.0
    assert S.settle_observation(obs(family="TOTAL", operator=">", floor_strike=43.5), book).settled_yes == 1.0
    assert S.settle_observation(obs(family="TEAM_TOTAL", team="PHI", threshold=24), book).settled_yes == 1.0
    assert S.settle_observation(obs(family="TEAM_TOTAL", team="DAL", threshold=21), book).settled_yes == 0.0
    assert S.settle_observation(obs(family="BOTH_TEAMS_SCORE_N", threshold=20), book).settled_yes == 1.0
    assert S.settle_observation(obs(family="BOTH_TEAMS_SCORE_N", threshold=21), book).settled_yes == 0.0


def test_a_team_that_is_not_in_the_game_is_an_identity_refusal(book):
    st = S.settle_observation(obs(family="TEAM_TOTAL", team="KC", threshold=20), book)
    assert st.status == S.REFUSED_TEAM_IDENTITY and st.settled_yes is None


def test_a_missing_threshold_is_refused_rather_than_assumed(book):
    st = S.settle_observation(obs(family="TOTAL", threshold=None), book)
    assert st.status == S.REFUSED_AMBIGUOUS_SEMANTICS and st.settled_yes is None


# ---------------------------------------------------------------- player statistics
@pytest.mark.parametrize("stat,k,expected", [
    ("passing_yards", 150, 1.0), ("passing_yards", 175, 0.0),      # Hurts threw for 152
    ("attempts", 20, 1.0), ("attempts", 25, 0.0),                  # 23 attempts
    ("completions", 19, 1.0), ("completions", 20, 0.0),            # 19 completions
    ("passing_tds", 1, 0.0),                                       # none
    ("interceptions", 1, 0.0),                                     # none
    ("rushing_yards", 50, 1.0), ("rushing_yards", 75, 0.0),        # 62 rushing yards
    ("touchdowns", 1, 1.0),                                        # two rushing touchdowns
])
def test_quarterback_statistics_settle_from_the_official_line(book, stat, k, expected):
    st = S.settle_observation(obs(stat=stat, threshold=k, player_id=HURTS, player_name="Jalen Hurts"), book)
    assert st.status == S.SETTLED and st.kind == S.KIND_BINARY
    assert st.settled_yes == expected, f"{stat} >= {k}: {st.reason}"


@pytest.mark.parametrize("pid,stat,k,expected", [
    (BARKLEY, "rushing_yards", 60, 1.0), (BARKLEY, "rushing_yards", 61, 0.0),   # 60 rushing yards
    (BARKLEY, "carries", 18, 1.0), (BARKLEY, "carries", 19, 0.0),               # 18 carries
    (BARKLEY, "receptions", 4, 1.0), (BARKLEY, "touchdowns", 1, 1.0),
    (LAMB, "receptions", 7, 1.0), (LAMB, "receptions", 8, 0.0),                 # 7 receptions
    (LAMB, "receiving_yards", 100, 1.0), (LAMB, "receiving_yards", 111, 0.0),   # 110 yards
    (LAMB, "touchdowns", 1, 0.0),
])
def test_skill_player_statistics_settle_from_the_official_line(book, pid, stat, k, expected):
    st = S.settle_observation(obs(stat=stat, threshold=k, player_id=pid), book)
    assert st.status == S.SETTLED and st.settled_yes == expected, st.reason


def test_a_player_with_snaps_and_no_statistics_row_recorded_a_proven_zero(book):
    """Grant Calcaterra took 37 offensive snaps and is absent from a published statistics table.

    nflverse only lists players who recorded something, so absence from a COMPLETE table is a zero, not a
    missing value. Without this the low rungs of every ladder would be unsettleable.
    """
    st = S.settle_observation(obs(stat="receptions", threshold=1, player_id=CALCATERRA), book)
    assert st.status == S.SETTLED and st.settled_yes == 0.0
    assert "zero_row" in st.evidence


def test_a_player_absent_from_a_complete_snap_table_is_refused_not_settled_no(book):
    """Inactive settles $0.00; active-but-never-played settles at the pregame fair price. Absence cannot tell
    which, and they are different payouts, so nothing is settled."""
    st = S.settle_observation(obs(stat="receptions", threshold=1, player_id=NOT_IN_GAME), book)
    assert st.status == S.REFUSED_PARTICIPATION_UNPROVEN and st.settled_yes is None
    assert st.evidence.get("snap_table_complete") is True
    assert "INACTIVE" in st.reason and "fair price" in st.reason


def _dressed(book):
    book.add_player(PlayerGameResult(player_id="00-0009999", game_id=GAME, team="PHI", has_snap_row=True,
                                    offense_snaps=0.0, defense_snaps=0.0, st_snaps=0.0, player_name="Dressed"))
    return obs(stat="receptions", threshold=1, player_id="00-0009999")


def test_an_active_player_who_never_took_a_snap_settles_at_the_exchanges_exact_value(book):
    o = _dressed(book)
    st = S.settle_observation(o, book, exact_scalar_payout=0.12,
                             exact_scalar_source="kalshi_settlement_snapshot")
    assert (st.status, st.settled_yes, st.kind) == (S.SETTLED, 0.12, S.KIND_SCALAR_EXACT)
    assert st.evidence["participation_branch"] == "active_no_snap_proven"
    assert st.evidence["exact_scalar_source"] == "kalshi_settlement_snapshot"


def test_the_no_snap_branch_is_refused_when_the_exchange_value_is_unavailable(book):
    """The hard rule: participation proven, payout not. No price of any kind may stand in for the payout."""
    o = _dressed(book)
    st = S.settle_observation(o, book)
    assert st.status == S.REFUSED_EXACT_SCALAR_PAYOUT_UNAVAILABLE and st.settled_yes is None
    assert st.evidence["participation_branch"] == "active_no_snap_proven"
    assert st.evidence["exact_scalar_payout_available"] is False
    assert "midpoint" in st.reason and "not the payout" in st.reason


def test_there_is_no_way_to_pass_a_price_into_settlement(book):
    """A midpoint cannot become a settlement by accident, because no parameter accepts one."""
    import inspect
    params = set(inspect.signature(S.settle_observation).parameters)
    for forbidden in ("fair_price", "mid", "midpoint", "close_mid", "price", "last_price"):
        assert forbidden not in params, f"settle_observation must not accept {forbidden}"
    o = _dressed(book)
    with pytest.raises(TypeError):
        S.settle_observation(o, book, fair_price=0.12)


def test_an_out_of_range_exchange_value_is_refused(book):
    o = _dressed(book)
    st = S.settle_observation(o, book, exact_scalar_payout=1.7)
    assert st.status == S.REFUSED_EXACT_SCALAR_PAYOUT_UNAVAILABLE and st.settled_yes is None


def test_an_unresolved_player_identity_is_refused(book):
    st = S.settle_observation(obs(stat="receptions", threshold=1, player_id=None), book)
    assert st.status == S.REFUSED_PLAYER_IDENTITY and st.settled_yes is None


def test_a_statistic_with_no_established_settlement_column_is_refused(book):
    for stat in ("sacks", "tackles", "longest_reception", "fantasy_points", "rush_rec_yards"):
        st = S.settle_observation(obs(stat=stat, threshold=1, player_id=HURTS), book)
        assert st.status == S.REFUSED_UNSUPPORTED_STAT, stat
        assert st.settled_yes is None


def test_a_touchdown_is_a_touchdown_however_it_was_scored(book):
    """The 2025 archive settled YES for players whose only touchdown was a fumble recovered in the end zone
    (Woody Marks, Tyler Lockett) or a return. A reading limited to rushing and receiving would call Kalshi's
    correct settlement wrong."""
    book.add_player(PlayerGameResult(
        player_id="00-0008888", game_id=GAME, has_stats_row=True, player_name="End-zone recovery",
        stats={"rushing_tds": 0.0, "receiving_tds": 0.0, "special_teams_tds": 0.0, "def_tds": 0.0,
               "fumble_recovery_tds": 1.0}))
    assert S.settle_observation(obs(stat="touchdowns", threshold=1, player_id="00-0008888"),
                               book).settled_yes == 1.0
    book.add_player(PlayerGameResult(
        player_id="00-0008887", game_id=GAME, has_stats_row=True, player_name="Kick returner",
        stats={"rushing_tds": 0.0, "receiving_tds": 0.0, "special_teams_tds": 1.0, "def_tds": 0.0,
               "fumble_recovery_tds": 0.0}))
    assert S.settle_observation(obs(stat="touchdowns", threshold=1, player_id="00-0008887"),
                               book).settled_yes == 1.0


def test_a_multi_touchdown_threshold_is_refused_when_the_count_could_double_count(book):
    """A defensive end-zone fumble recovery can appear in both def_tds and fumble_recovery_tds, so the COUNT is
    ambiguous even though "did he score at all" is not."""
    book.add_player(PlayerGameResult(
        player_id="00-0008886", game_id=GAME, has_stats_row=True,
        stats={"def_tds": 1.0, "fumble_recovery_tds": 1.0, "rushing_tds": 0.0, "receiving_tds": 0.0,
               "special_teams_tds": 0.0}))
    one = S.settle_observation(obs(stat="touchdowns", threshold=1, player_id="00-0008886"), book)
    assert one.settled_yes == 1.0, "one or more is unaffected by how the two columns overlap"
    two = S.settle_observation(obs(stat="touchdowns", threshold=2, player_id="00-0008886"), book)
    assert two.status == S.REFUSED_AMBIGUOUS_SEMANTICS and two.settled_yes is None


# ---------------------------------------------------------------- what is deliberately not settled
def test_families_without_established_settlement_are_refused_with_a_reason(book):
    for family in ("WIN_MARGIN_BUCKET", "TOTAL_TD", "PERIOD_WINNER", "FIRST_TD_SCORER", "FIRST_TD_TEAM",
                   "RACE_TO_N", "HALF_FULL_RESULT", "PARLAY", "COMBO", "TEAM_STAT", "GAME_STAT"):
        st = S.settle_observation(obs(family=family, threshold=1, team="PHI"), book)
        assert st.status == S.REFUSED_UNSUPPORTED_FAMILY, family
        assert st.settled_yes is None and st.reason


def test_period_markets_are_refused_because_period_scores_are_not_published(book):
    for period in ("1H", "2H", "1Q", "4Q"):
        st = S.settle_observation(obs(family="TOTAL", period=period, threshold=20), book)
        assert st.status == S.REFUSED_UNSUPPORTED_PERIOD and st.settled_yes is None


def test_a_market_with_no_game_is_refused(book):
    assert S.settle_observation(obs(family="TOTAL", threshold=40, game_id=None), book).status == S.REFUSED_GAME_IDENTITY
    assert S.settle_observation(obs(family="TOTAL", threshold=40, game_id="2025_01_XX_YY"),
                               book).status == S.REFUSED_GAME_IDENTITY


def test_no_refusal_anywhere_carries_a_payout(book):
    """One invariant over every refusal path: a refusal is never a number."""
    cases = [obs(family="PARLAY"), obs(family="TOTAL", period="1H", threshold=20),
             obs(stat="sacks", threshold=1, player_id=HURTS), obs(stat="receptions", threshold=1, player_id=None),
             obs(stat="receptions", threshold=1, player_id=NOT_IN_GAME),
             obs(family="TOTAL", threshold=None), obs(family="GAME_WINNER", operator="event", team=None),
             obs(family="SPREAD", operator="event", team="PHI"), obs(direction="NO", family="TOTAL", threshold=40),
             _dressed(book)]
    for c in cases:
        st = S.settle_observation(c, book)
        assert not st.is_settled and st.settled_yes is None, c


def test_the_original_observation_is_never_mutated(book):
    o = obs(stat="passing_yards", threshold=150, player_id=HURTS)
    before = copy.deepcopy(o)
    S.settle_observation(o, book, exact_scalar_payout=0.3)
    assert o == before


def test_needs_player_stats_only_when_a_player_market_is_present():
    assert S.needs_player_stats([{"family": "TOTAL"}, {"family": "PLAYER_STAT"}]) is True
    assert S.needs_player_stats([{"family": "TOTAL"}, {"family": "SPREAD"}]) is False


def test_the_schedule_parser_reads_scores_and_leaves_unplayed_games_blank(records):
    games = {g.game_id: g for g in games_from_schedule_text(records["schedule_csv"])}
    assert games[GAME].status == FINAL
    assert games["2026_01_NE_SEA"].home_score is None and games["2026_01_NE_SEA"].away_score is None
