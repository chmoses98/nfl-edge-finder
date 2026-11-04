"""Legacy NFL v1 double-fee backfill: append-only, verified, idempotent, counts-only."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "handicap"))
import backfill_v1_settlement_amendments as BACKFILL  # noqa: E402
from nfl_edge.handicap import settlement_amendments as AM, store  # noqa: E402


def put(root, kind, season, week, record_id, payload):
    path = Path(store.record_path(str(root), kind, season, week, record_id))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")
    return path


def add_pair(root, key, ticker, *, stake=5.20, fees=0.20, gross=10.0,
             old_net=None, fee_estimated=False, week=1, net_missing=False):
    wager = {
        "imported_wager_id": "routed-" + key, "source_bet_key": key,
        "season": 2026, "week": week, "market_ticker": ticker,
        "stake": stake, "fees_paid": fees, "fees_are_estimated": fee_estimated,
    }
    settlement = {
        "settlement_id": "stl-" + key, "source_bet_key": key, "season": 2026,
        "week": week, "market_ticker": ticker, "side": "YES",
        "settlement_status": "SETTLED", "settled_at": "2026-09-14T00:00:00Z",
        "result": "WON", "gross_return": gross,
        "net_profit_loss": None if net_missing else (old_net if old_net is not None else gross - stake - fees),
        "refusals": ["FEE_UNESTABLISHED"] if net_missing else [], "venue": "kalshi",
    }
    put(root, "imported_wagers", 2026, week, wager["imported_wager_id"], wager)
    settlement_path = put(root, "wager_settlements", 2026, week, settlement["settlement_id"], settlement)
    return settlement_path


def test_fifty_cent_market_fee_double_count_is_corrected_once(tmp_path):
    path = add_pair(tmp_path, "synthetic-a", "KXNFLTOTAL-SYNTH", stake=5.20,
                    fees=0.20, gross=10.0, old_net=4.60)
    before = path.read_bytes()
    planned, report = BACKFILL.plan(str(tmp_path), 2026)
    assert report["verified_amendments_planned"] == 1
    assert report["reason_counts"] == {}
    amend_path, record = planned[0]
    assert record["superseded_fields"]["net_profit_loss"]["corrected"] == pytest.approx(4.80)
    assert record["superseded_fields"]["net_profit_loss"]["prior"] == pytest.approx(4.60)
    assert record["original_record_sha256"] == AM.record_sha256(str(path))
    assert BACKFILL.main(["--handicap-root", str(tmp_path), "--season", "2026"]) == 0
    assert not Path(amend_path).exists(), "dry-run never modifies the tree"
    assert BACKFILL.main(["--handicap-root", str(tmp_path), "--season", "2026", "--apply"]) == 0
    assert path.read_bytes() == before, "the exchange's original settlement is immutable"
    assert Path(amend_path).exists()
    assert AM.canonical_settlement(json.loads(path.read_text()), [json.loads(Path(amend_path).read_text())])[
        "net_profit_loss"
    ] == pytest.approx(4.80)
    assert BACKFILL.plan(str(tmp_path), 2026)[1]["reason_counts"]["ALREADY_AMENDED"] == 1
    assert BACKFILL.main(["--handicap-root", str(tmp_path), "--season", "2026", "--apply"]) == 0
    assert len(list(tmp_path.glob("data/wager_settlement_amendments/**/*.json"))) == 1


def test_shared_position_reconciles_market_fee_not_just_one_leg(tmp_path):
    # Two orders on the SAME ticker: v1's market-wide fee equals $0.30, not
    # the $0.10 or $0.20 fee of either individual order.
    add_pair(tmp_path, "synthetic-a", "KXNFLGAME-PAIR", stake=5.10,
             fees=0.10, gross=10.0, old_net=4.60)
    add_pair(tmp_path, "synthetic-b", "KXNFLGAME-PAIR", stake=4.20,
             fees=0.20, gross=0.0, old_net=-4.50)
    planned, report = BACKFILL.plan(str(tmp_path), 2026)
    assert report["verified_amendments_planned"] == 2
    assert all(row["reason_code"] == AM.REASON_FEE_DOUBLE_COUNT for _path, row in planned)


def test_refuses_unreconciled_fee_or_unknown_exchange_fee(tmp_path):
    add_pair(tmp_path, "synthetic-a", "KXNFLTOTAL-SYNTH", stake=5.20,
             fees=0.20, gross=10.0, old_net=4.00)
    assert BACKFILL.plan(str(tmp_path), 2026)[1]["reason_counts"] == {
        "SETTLEMENT_FEE_NOT_RECONCILED": 1
    }
    path = store.record_path(str(tmp_path), "imported_wagers", 2026, 1, "routed-synthetic-a")
    wager = json.loads(Path(path).read_text())
    wager["fees_are_estimated"] = True
    Path(path).write_text(json.dumps(wager))
    assert BACKFILL.plan(str(tmp_path), 2026)[1]["reason_counts"] == {
        "ACTUAL_MARKET_FEES_UNESTABLISHED": 1
    }


def test_null_legacy_net_needs_independent_exchange_correction(tmp_path):
    add_pair(tmp_path, "synthetic-a", "KXNFLTOTAL-SYNTH", net_missing=True)
    planned, report = BACKFILL.plan(str(tmp_path), 2026)
    assert planned == []
    assert report["reason_counts"] == {"LEGACY_ECONOMICS_UNESTABLISHED": 1}


def test_non_v1_or_zero_fee_never_mints_spurious_correction(tmp_path):
    old = add_pair(tmp_path, "synthetic-a", "KXNFLTOTAL-SYNTH", stake=5.0,
                   fees=0.0, gross=10.0, old_net=5.0)
    assert BACKFILL.plan(str(tmp_path), 2026)[1]["reason_counts"] == {
        "NO_EXTRA_FEE_TO_CORRECT": 1
    }
    doc = json.loads(old.read_text())
    doc["economics_version"] = AM.ECONOMICS_V2
    old.write_text(json.dumps(doc))
    assert BACKFILL.plan(str(tmp_path), 2026)[1]["reason_counts"] == {"ALREADY_V2": 1}
