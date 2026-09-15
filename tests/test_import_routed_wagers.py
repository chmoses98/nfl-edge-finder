"""The kalshi-bet-router contract, exercised against this repository's importer.

ROUTER_ROW is captured verbatim from `kalshi_router.production.to_nfl_import_row`,
so this is a genuine cross-repository contract test rather than a hand-written
guess at what the router emits. If the router changes its shape, this stops
matching.

The MLB ledger learned this lesson expensively on 2026-09-15: the router emitted
execution economics in a shape that importer never read, the import succeeded,
and the wager was recorded with a stake and a price and no contracts, no fees and
no cash. Nothing failed. A test that runs the real payload through the real
importer and asserts the numbers survive is what would have caught it.
"""

from __future__ import annotations

import os

import pytest

from nfl_edge.handicap import store
from nfl_edge.handicap.import_routed_wagers import (
    ImportRefused,
    build_record,
    import_rows,
    mint_imported_wager_id,
    resolve_season_week,
)

#: Exactly what the router sends -- no identity, no season, no week.
ROUTER_ROW = {
    "source_bet_key": "kalshi:v1:f84706dea7af2740bb0f6f61d3b5e6598f71aeadbbed75cd1db08163d5f4a9cf",
    "import_batch_id": "kalshi-gap-backfill-2026-09-12-through-production-cutover-v1",
    "entry_method": "IMPORTED_RECEIPT",
    "game_date": "2026-09-14",
    "market_ticker": "KXNFLGAME-26SEP14KCBUF-KC",
    "side": "YES",
    "executed_at": "2026-09-14T20:40:11Z",
    "contracts": 40.0,
    "actual_price": 0.61,
    "stake": 24.68,
    "fees_paid": 0.28,
    "fees_are_estimated": False,
    "fee_state": "ACTUAL_API_FILL",
    "venue": "kalshi",
}

#: A minimal schedule in the shape `nfl_calendar.parse_schedule` produces.
GAMES = [
    {"game_id": "2026_02_KC_BUF", "season": 2026, "week": 2, "game_type": "REG",
     "gameday": "2026-09-14", "away_team": "KC", "home_team": "BUF",
     "kickoff_utc": None, "has_result": False},
    {"game_id": "2026_03_SF_LAR", "season": 2026, "week": 3, "game_type": "REG",
     "gameday": "2026-09-21", "away_team": "SF", "home_team": "LAR",
     "kickoff_utc": None, "has_result": False},
]


def test_the_exact_exchange_numbers_survive_the_import():
    """The assertion that would have caught the hollow MLB row."""
    record = build_record(ROUTER_ROW, GAMES)

    assert record.contracts == 40.0
    assert record.actual_price == 0.61
    assert record.stake == 24.68
    assert record.fees_paid == 0.28
    assert record.fees_are_estimated is False
    assert record.fee_state == "ACTUAL_API_FILL"
    assert record.market_ticker == "KXNFLGAME-26SEP14KCBUF-KC"
    assert record.side == "YES"
    assert record.executed_at == "2026-09-14T20:40:11Z"


def test_the_week_comes_from_the_schedule_not_from_the_date():
    """2026-09-14 is week 2 because a scheduled game says so."""
    assert resolve_season_week("2026-09-14", GAMES) == (2026, 2)
    assert resolve_season_week("2026-09-21", GAMES) == (2026, 3)


def test_a_date_with_no_scheduled_game_is_refused():
    """Fail closed. A wager filed under a guessed week is counted in a week it
    did not happen in AND missing from the one it did -- two wrong numbers from
    one guess. One honest gap is better."""
    with pytest.raises(ImportRefused, match="no scheduled REG game"):
        resolve_season_week("2026-12-25", GAMES)


def test_a_date_spanning_two_weeks_is_refused_rather_than_picked():
    """An ambiguous answer is not an answer."""
    ambiguous = GAMES + [
        {"game_id": "2026_03_X", "season": 2026, "week": 3, "game_type": "REG",
         "gameday": "2026-09-14", "away_team": "X", "home_team": "Y",
         "kickoff_utc": None, "has_result": False},
    ]
    with pytest.raises(ImportRefused, match="more than one season/week"):
        resolve_season_week("2026-09-14", ambiguous)


def test_the_id_is_derived_only_from_the_venue_key():
    """Identity is not economics.

    Correcting a fee on an already-imported wager must land on the SAME record,
    and the same order noticed by a second backfill is the same wager -- so the
    id may not move when the money or the batch does.
    """
    base = mint_imported_wager_id(ROUTER_ROW["source_bet_key"])

    richer = dict(ROUTER_ROW, stake=999.0, fees_paid=9.99,
                  import_batch_id="some-other-batch")
    assert mint_imported_wager_id(richer["source_bet_key"]) == base
    assert base != mint_imported_wager_id("kalshi:v1:some-other-order")


def test_the_minted_id_is_a_safe_record_filename():
    from nfl_edge.handicap import schema

    assert schema._ID_RE.match(mint_imported_wager_id(ROUTER_ROW["source_bet_key"]))


def test_no_model_provenance_is_fabricated():
    """A Kalshi execution proves the owner placed the bet, not that this system
    called it."""
    record = build_record(ROUTER_ROW, GAMES).to_dict()

    for field in ("recommendation_id", "evaluation_id", "model_fair_probability",
                  "model_supported", "edge", "expected_value"):
        assert field not in record
    assert record["entry_method"] == "IMPORTED_RECEIPT"


def test_a_router_field_this_ledger_does_not_model_is_refused():
    """Not dropped quietly. The sender believes a field it sent was recorded, so
    silently discarding one is how a ledger ends up disagreeing with its source
    while both sides report success."""
    with pytest.raises(ImportRefused, match="unknown field"):
        build_record(dict(ROUTER_ROW, model_supported=True), GAMES)


def test_importing_writes_the_record(tmp_path):
    result = import_rows(str(tmp_path), [ROUTER_ROW], games=GAMES)

    assert result["written"] == 1
    assert result["already_present"] == 0
    assert result["refused"] == 0
    records = store.read_kind(str(tmp_path), "imported_wagers")
    assert len(records) == 1
    assert records[0]["season"] == 2026 and records[0]["week"] == 2
    assert records[0]["contracts"] == 40.0


def test_a_second_identical_import_writes_nothing(tmp_path):
    """Re-running a backfill has to be boring.

    `schema.write_record` REFUSES to clobber -- that is the immutability
    guarantee -- so already-present has to be detected before writing rather
    than caught afterwards. Asking it to write blindly would raise, not no-op.
    """
    first = import_rows(str(tmp_path), [ROUTER_ROW], games=GAMES)
    second = import_rows(str(tmp_path), [ROUTER_ROW], games=GAMES)

    assert (first["written"], first["already_present"]) == (1, 0)
    assert (second["written"], second["already_present"]) == (0, 1)
    assert len(store.read_kind(str(tmp_path), "imported_wagers")) == 1


def test_an_unresolvable_wager_is_reported_rather_than_dropped(tmp_path):
    """Refused is a COUNT and a REASON, not silence."""
    result = import_rows(
        str(tmp_path), [dict(ROUTER_ROW, game_date="2026-12-25")], games=GAMES
    )

    assert result["written"] == 0
    assert result["refused"] == 1
    assert "no scheduled REG game" in result["refusals"][0][1]
    assert store.read_kind(str(tmp_path), "imported_wagers") == []


def test_one_refused_row_does_not_stop_the_others(tmp_path):
    other = dict(ROUTER_ROW,
                 source_bet_key="kalshi:v1:second-order",
                 game_date="2026-09-21")
    result = import_rows(
        str(tmp_path),
        [dict(ROUTER_ROW, game_date="2026-12-25"), other],
        games=GAMES,
    )

    assert result["written"] == 1
    assert result["refused"] == 1
    assert len(store.read_kind(str(tmp_path), "imported_wagers")) == 1


def test_the_record_lands_in_its_own_week_directory(tmp_path):
    import_rows(str(tmp_path), [ROUTER_ROW], games=GAMES)

    expected = store.week_dir(str(tmp_path), "imported_wagers", 2026, 2)
    assert os.path.isdir(expected)
    assert len(os.listdir(expected)) == 1
