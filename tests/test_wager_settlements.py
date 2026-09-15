"""A settlement is a LATER and SEPARATE observation than the wager it settles.

`imported_wagers` is immutable, and the append-only guard covers it, because a
record of money that already moved may not be rewritten. That reasoning does not
stop applying because the new information is welcome.
"""
from __future__ import annotations

import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts", "handicap"))

from nfl_edge.handicap import imported_wager_report as report  # noqa: E402
from nfl_edge.handicap import store, wager_settlements  # noqa: E402
from nfl_edge.handicap.import_routed_settlements import (  # noqa: E402
    SettlementRefused,
    build_record,
    import_rows,
    mint_settlement_id,
)
from nfl_edge.handicap.import_routed_wagers import import_rows as import_wagers  # noqa: E402

KEY = "kalshi:v1:f84706dea7af2740bb0f6f61d3b5e6598f71aeadbbed75cd1db08163d5f4a9cf"
TICKER = "KXNFLGAME-26SEP14KCBUF-KC"

GAMES = [
    {"game_id": "2026_02_KC_BUF", "season": 2026, "week": 2, "game_type": "REG",
     "gameday": "2026-09-14", "away_team": "KC", "home_team": "BUF",
     "kickoff_utc": None, "has_result": False},
]

WAGER_ROW = {
    "source_bet_key": KEY, "import_batch_id": "batch",
    "entry_method": "IMPORTED_RECEIPT", "game_date": "2026-09-14",
    "market_ticker": TICKER, "side": "YES", "executed_at": "2026-09-14T20:40:11Z",
    "contracts": 40.0, "actual_price": 0.61, "stake": 24.68, "fees_paid": 0.28,
    "fees_are_estimated": False, "fee_state": "ACTUAL_API_FILL", "venue": "kalshi",
}

#: Exactly the shape kalshi_router.settlement.WagerSettlement produces.
ROUTER_ROW = {
    "source_bet_key": KEY,
    "market_ticker": TICKER,
    "side": "YES",
    "settlement_status": "SETTLED",
    "settled_at": "2026-09-15T02:00:00Z",
    "result": "WON",
    "gross_return": 40.0,
    "net_profit_loss": 15.32,
    "refusals": [],
}


def seeded(tmp_path, **overrides):
    import_wagers(str(tmp_path), [dict(WAGER_ROW, **overrides)], games=GAMES)
    return str(tmp_path)


def wager_of(root):
    return store.read_kind(root, "imported_wagers")[0]


# ------------------------------------------------------------- the record

def test_the_exact_exchange_numbers_survive(tmp_path):
    record = build_record(ROUTER_ROW, wager_of(seeded(tmp_path)))

    assert record.result == "WON"
    assert record.gross_return == 40.0
    assert record.net_profit_loss == 15.32
    assert record.schema_version == "nfl_wager_settlement.v1"


def test_the_season_and_week_come_from_the_wager_not_from_the_row(tmp_path):
    """The wager resolved them against the real schedule. A settlement filed in
    a different week from its own wager would make both weekly reports wrong at
    once."""
    record = build_record(ROUTER_ROW, wager_of(seeded(tmp_path)))

    assert (record.season, record.week) == (2026, 2)


def test_the_id_comes_from_the_wagers_key_not_from_the_payout():
    base = mint_settlement_id(KEY)

    assert mint_settlement_id(KEY) == base
    assert base != mint_settlement_id("kalshi:v1:other")
    assert base.startswith("stl-")


def test_the_minted_id_is_a_safe_record_filename():
    from nfl_edge.handicap import schema

    assert schema._ID_RE.match(mint_settlement_id(KEY))


def test_no_model_provenance_is_fabricated(tmp_path):
    record = build_record(ROUTER_ROW, wager_of(seeded(tmp_path))).to_dict()

    for field in wager_settlements.FORBIDDEN_PROVENANCE_FIELDS:
        assert field not in record


def test_a_pending_record_is_refused_outright(tmp_path):
    """A PENDING record would have to be superseded when the market settled, in
    a ledger whose whole guarantee is that records are not."""
    with pytest.raises(SettlementRefused, match="having no settlement record"):
        build_record(dict(ROUTER_ROW, settlement_status="PENDING"),
                     wager_of(seeded(tmp_path)))


def test_a_missing_figure_must_carry_its_reason(tmp_path):
    with pytest.raises(SettlementRefused, match="no refusal recorded"):
        build_record(dict(ROUTER_ROW, net_profit_loss=None),
                     wager_of(seeded(tmp_path)))


def test_a_refusal_alongside_a_complete_figure_is_itself_refused(tmp_path):
    with pytest.raises(SettlementRefused, match="nothing to refuse"):
        build_record(dict(ROUTER_ROW, refusals=["no_settlement_price"]),
                     wager_of(seeded(tmp_path)))


# -------------------------------------------------------------- the import

def test_a_settlement_for_a_known_wager_is_written(tmp_path):
    root = seeded(tmp_path)
    result = import_rows(root, [ROUTER_ROW])

    assert (result["written"], result["refused"]) == (1, 0)
    records = store.read_kind(root, "wager_settlements")
    assert len(records) == 1 and records[0]["result"] == "WON"


def test_a_settlement_for_a_wager_this_ledger_never_saw_is_refused(tmp_path):
    """THE test."""
    root = seeded(tmp_path)
    result = import_rows(root, [dict(ROUTER_ROW, source_bet_key="kalshi:v1:ghost")])

    assert (result["written"], result["refused"]) == (0, 1)
    assert "no imported wager with this source_bet_key" in result["refusals"][0][1]
    assert store.read_kind(root, "wager_settlements") == []


def test_running_the_settlement_pass_twice_writes_one_record(tmp_path):
    """`write_record` REFUSES to clobber, so already-present has to be detected
    before writing rather than caught afterwards."""
    root = seeded(tmp_path)
    first = import_rows(root, [ROUTER_ROW])
    second = import_rows(root, [ROUTER_ROW])

    assert (first["written"], first["already_present"]) == (1, 0)
    assert (second["written"], second["already_present"]) == (0, 1)
    assert len(store.read_kind(root, "wager_settlements")) == 1


def test_the_wager_record_itself_is_never_touched(tmp_path):
    root = seeded(tmp_path)
    path = wager_of(root)["_path"]
    before = open(path, "rb").read()

    import_rows(root, [ROUTER_ROW])

    assert open(path, "rb").read() == before


def test_the_settlement_lands_in_its_wagers_own_week_directory(tmp_path):
    root = seeded(tmp_path)
    import_rows(root, [ROUTER_ROW])

    expected = store.week_dir(root, "wager_settlements", 2026, 2)
    assert os.path.isdir(expected)
    assert len(os.listdir(expected)) == 1


# -------------------------------------------------------------- the report

def test_the_report_joins_settlements_to_wagers(tmp_path):
    root = seeded(tmp_path)
    import_rows(root, [ROUTER_ROW])

    summary = report.summarize(
        store.read_kind(root, "imported_wagers"), 2026,
        settlements=store.read_kind(root, "wager_settlements"),
    )

    assert (summary.settled, summary.unsettled) == (1, 0)
    assert summary.won == 1
    assert summary.profit_loss_is_complete is True
    assert round(summary.realized_profit_loss, 2) == 15.32


def test_a_wager_with_no_settlement_record_is_unsettled(tmp_path):
    root = seeded(tmp_path)

    summary = report.summarize(store.read_kind(root, "imported_wagers"), 2026,
                               settlements=[])

    assert (summary.settled, summary.unsettled) == (0, 1)


def test_a_settled_wager_whose_pl_was_refused_is_settled_but_unestablished(tmp_path):
    """Both facts at once, and the report must not collapse them."""
    root = seeded(tmp_path)
    import_rows(root, [dict(ROUTER_ROW, net_profit_loss=None,
                            refusals=["shared_position_fee"])])

    summary = report.summarize(
        store.read_kind(root, "imported_wagers"), 2026,
        settlements=store.read_kind(root, "wager_settlements"),
    )

    assert summary.settled == 1 and summary.won == 1
    assert summary.profit_loss_unestablished == 1


# ------------------------------------------------------------- the invariant

def test_nothing_that_measures_model_performance_reads_wager_settlements():
    """For the same reason nothing may read `imported_wagers`: the model had no
    part in these bets, so their OUTCOMES are not its record either."""
    from tests.test_imported_wager_accounting import _modules_reading

    readers = _modules_reading("wager_settlements")
    forbidden = {
        "scripts/handicap/scorecard.py",
        "nfl_edge/handicap/scorecard.py",
        "nfl_edge/handicap/evaluate.py",
        "nfl_edge/handicap/risk.py",
        "scripts/handicap/attach_evaluations.py",
    }

    assert not (readers & forbidden), sorted(readers & forbidden)
    assert readers, "the detector found no reader at all; it proves nothing"


def test_the_new_kind_is_covered_by_the_append_only_guard():
    """A settlement that can be edited after the fact is not evidence either.

    The repository's own guard test caught `imported_wagers` the moment it was
    registered; this asserts the same coverage rather than waiting for it.
    """
    from scripts.handicap import verify_append_only as guard

    assert "wager_settlements" in guard.IMMUTABLE_KINDS
    assert "wager_settlements" in store.KINDS


# -------------------------------------------------------------- the script

def test_the_script_prints_no_payout(tmp_path, capsys):
    import import_routed_settlements as script

    root = seeded(tmp_path)
    payload = tmp_path / "NFL-settlements.json"
    payload.write_text(json.dumps({"settlements": [ROUTER_ROW]}), encoding="utf-8")

    assert script.main(["--payload", str(payload), "--handicap-root", root]) == script.EXIT_OK

    printed = capsys.readouterr().out
    assert "written:         1" in printed
    for sensitive in (TICKER, "40.0", "15.32", KEY):
        assert sensitive not in printed, printed


def test_the_script_fails_when_a_settlement_is_refused(tmp_path):
    import import_routed_settlements as script

    root = seeded(tmp_path)
    payload = tmp_path / "NFL-settlements.json"
    payload.write_text(
        json.dumps({"settlements": [dict(ROUTER_ROW, source_bet_key="kalshi:v1:ghost")]}),
        encoding="utf-8",
    )

    assert script.main([
        "--payload", str(payload), "--handicap-root", root,
    ]) == script.EXIT_REFUSED
