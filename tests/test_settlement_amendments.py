"""Append-only settlement amendments: a corrected figure sits BESIDE the immutable original, never over it.

The router's settlement economics v1 subtracted the position's trading fee a second time. v2 settlements for
wagers already settled under v1 are admitted only as amendments the destination can re-derive itself
(net == gross_return - stake of the wager it holds); anything else about them is a conflict.
"""
from __future__ import annotations

import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts", "handicap"))

from nfl_edge.handicap import actual_wager_postmortem as PM  # noqa: E402
from nfl_edge.handicap import settlement_amendments as AM  # noqa: E402
from nfl_edge.handicap import store  # noqa: E402
from nfl_edge.handicap.import_routed_settlements import import_rows as import_settlements  # noqa: E402
from nfl_edge.handicap.import_routed_settlements import mint_settlement_id  # noqa: E402
from nfl_edge.handicap.import_routed_wagers import import_rows as import_wagers  # noqa: E402

import validate_routed_ledger as VALIDATE  # noqa: E402

KEY = "kalshi:v1:amend-a"
TICKER = "KXNFLGAME-26SEP20CARATL-CAR"
GAMES = [{"game_id": "2026_02_CAR_ATL", "season": 2026, "week": 2, "game_type": "REG", "gameday": "2026-09-20",
          "away_team": "CAR", "home_team": "ATL", "kickoff_utc": None, "has_result": True}]
WAGER = {"source_bet_key": KEY, "import_batch_id": "kalshi-router-v1", "entry_method": "IMPORTED_RECEIPT",
         "game_date": "2026-09-20", "market_ticker": TICKER, "side": "YES", "executed_at": "2026-09-20T15:00:00Z",
         "contracts": 10.0, "actual_price": 0.50, "stake": 5.10, "fees_paid": 0.10, "fees_are_estimated": False,
         "fee_state": "ACTUAL_API_FILL", "venue": "kalshi"}
V1 = {"source_bet_key": KEY, "market_ticker": TICKER, "side": "YES", "settlement_status": "SETTLED",
      "settled_at": "2026-09-21T00:00:00Z", "result": "WON", "gross_return": 10.0, "net_profit_loss": 4.80,
      "refusals": []}                                   # 10.00 - 5.10 - 0.10: the entry fee a second time
V2 = dict(V1, net_profit_loss=4.90, economics_version=AM.ECONOMICS_V2)


def seeded(tmp_path):
    root = str(tmp_path)
    import_wagers(root, [WAGER], games=GAMES)
    assert import_settlements(root, [V1])["receipts"][0]["status"] == "NEW"
    return root


def settlement_file(root):
    return store.record_path(root, "wager_settlements", 2026, 2, mint_settlement_id(KEY))


def statuses(result):
    return [r["status"] for r in result["receipts"]]


def test_a_v2_correction_is_filed_beside_the_original_which_is_untouched(tmp_path):
    root = seeded(tmp_path)
    before = open(settlement_file(root), "rb").read()
    r = import_settlements(root, [V2])
    assert statuses(r) == ["CORRECTED"]
    assert open(settlement_file(root), "rb").read() == before                      # immutable original
    [amd] = [a for lst in AM.read_amendments(root).values() for a in lst]
    assert amd["amends"] == mint_settlement_id(KEY) and amd["reason_code"] == "FEE_DOUBLE_COUNT_CORRECTION"
    assert amd["superseded_fields"] == {"net_profit_loss": {"prior": 4.8, "corrected": 4.9}}
    assert amd["prior_economics_version"] == AM.ECONOMICS_V1
    assert amd["original_record_sha256"] == AM.record_sha256(settlement_file(root))


def test_a_repeated_correction_is_a_no_op_and_the_ledger_stays_valid(tmp_path):
    root = seeded(tmp_path)
    import_settlements(root, [V2])
    assert statuses(import_settlements(root, [V2])) == ["DUPLICATE_NOOP"]
    assert VALIDATE.validate_tree(root)["problems"] == 0


def test_a_competing_correction_for_the_same_settlement_fails_closed(tmp_path):
    root = seeded(tmp_path)
    import_settlements(root, [V2])
    [amd_path] = [os.path.join(d, n) for d, _s, ns in os.walk(os.path.join(root, "data", AM.KIND)) for n in ns]
    doc = json.load(open(amd_path))
    doc["superseded_fields"]["net_profit_loss"]["corrected"] = 4.95            # someone else's "correction"
    with open(amd_path, "w") as f:
        json.dump(doc, f)
    assert statuses(import_settlements(root, [V2])) == ["CONFLICT"]


def test_a_net_the_destination_cannot_reproduce_is_refused(tmp_path):
    root = seeded(tmp_path)
    r = import_settlements(root, [dict(V2, net_profit_loss=5.25)])
    assert statuses(r) == ["CONFLICT"] and "reproduce" in r["receipts"][0]["reason"]
    assert AM.read_amendments(root) == {}


@pytest.mark.parametrize("field,value", [("result", "LOST"), ("gross_return", 0.0), ("settled_at", "2026-09-22T00:00:00Z")])
def test_anything_but_economics_differing_is_a_conflict_not_an_amendment(tmp_path, field, value):
    root = seeded(tmp_path)
    assert statuses(import_settlements(root, [dict(V2, **{field: value})])) == ["CONFLICT"]
    assert AM.read_amendments(root) == {}


def test_a_v2_row_for_a_new_wager_is_simply_written_as_v2(tmp_path):
    root = str(tmp_path)
    import_wagers(root, [WAGER], games=GAMES)
    assert statuses(import_settlements(root, [V2])) == ["NEW"]
    rec = json.load(open(settlement_file(root)))
    assert rec["economics_version"] == AM.ECONOMICS_V2 and rec["net_profit_loss"] == 4.9


def test_a_v1_record_keeps_its_exact_bytes_no_version_field_is_added(tmp_path):
    root = seeded(tmp_path)
    assert "economics_version" not in json.load(open(settlement_file(root)))


def test_a_previously_refused_net_becomes_established_through_an_amendment(tmp_path):
    """Week 1's shape: v1 refused a shared-position fee; v2 reconciles it."""
    root = str(tmp_path)
    import_wagers(root, [WAGER], games=GAMES)
    import_settlements(root, [dict(V1, net_profit_loss=None, refusals=["shared_position_fee"])])
    assert statuses(import_settlements(root, [V2])) == ["CORRECTED"]
    [amd] = [a for lst in AM.read_amendments(root).values() for a in lst]
    assert set(amd["superseded_fields"]) == {"net_profit_loss", "refusals"}


def test_an_amendment_to_a_later_rewritten_original_is_caught_by_the_validator(tmp_path):
    root = seeded(tmp_path)
    import_settlements(root, [V2])
    doc = json.load(open(settlement_file(root)))
    doc["net_profit_loss"] = 7.0
    with open(settlement_file(root), "w") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
    cats = VALIDATE.validate_tree(root)["problem_categories"]
    assert "amendment:ORIGINAL_RECORD_CHANGED_SINCE_AMENDED" in cats


def test_an_amendment_to_no_settlement_is_caught(tmp_path):
    root = seeded(tmp_path)
    import_settlements(root, [V2])
    os.remove(settlement_file(root))
    assert "amendment:AMENDS_NO_SUCH_SETTLEMENT" in VALIDATE.validate_tree(root)["problem_categories"]


def test_reports_show_canonical_by_default_and_keep_the_recorded_figure(tmp_path):
    root = seeded(tmp_path)
    import_settlements(root, [V2])
    wagers = store.read_kind(root, "imported_wagers")
    settlements = store.read_kind(root, "wager_settlements")
    doc = PM.build(wagers, settlements, [], season=2026, amendments=AM.read_amendments(root))
    row = doc["wagers"][0]
    assert row["net_profit_loss"] == 4.9 and row["recorded_net_profit_loss"] == 4.8
    assert row["amendment_status"] == "AMENDED" and row["economics_version"] == AM.ECONOMICS_V2
    assert row["net_canonical"] == 4.9
    assert doc["totals"]["net_profit_loss"] == 4.9 and doc["totals"]["recorded"]["net_profit_loss"] == 4.8
    assert "As ORIGINALLY RECORDED" in PM.render(doc)


def test_canonical_view_replays_deterministically_and_refuses_competing_versions():
    s = dict(V1, settlement_id="stl-x")
    a = {"amendment_id": AM.mint_amendment_id("stl-x", AM.ECONOMICS_V2), "amends": "stl-x",
         "amended_economics_version": AM.ECONOMICS_V2,
         "superseded_fields": {"net_profit_loss": {"prior": 4.8, "corrected": 4.9}}}
    assert AM.canonical_settlement(s, [a]) == AM.canonical_settlement(s, [a])
    assert AM.canonical_settlement(s, [a])["net_profit_loss"] == 4.9
    with pytest.raises(AM.AmendmentRefused):
        AM.canonical_settlement(s, [a, dict(a)])
