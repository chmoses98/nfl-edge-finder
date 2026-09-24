"""The owner's actual wagers: per-row receipts, conflicts, ledger validation and the actual-wager postmortem.

Week 2 of 2026 lost every NFL wager the owner placed -- not in this repository, but because kalshi-bet-router's
scheduled delivery had no NFL destination and counted those orders as "no destination importer, by design".
One reason NFL was never activated: this importer returned COUNTS, which the router's auto-merge gate cannot
read, so a delivery could never land unattended. The properties pinned here are what make it landable and
self-checking:

  * one receipt per payload row, carrying the router's key, this ledger's id and a verdict the router's gate
    understands (NEW / DUPLICATE_NOOP / CONFLICT / REFUSED) -- and never economics;
  * "already filed" is not "agrees": a re-delivery that disagrees about money or week is a CONFLICT, refused
    and never rewritten; a terminal settlement can never be regressed;
  * the whole ledger validates against this repository's own rules (the router's gate runs this);
  * the postmortem never states a headline it cannot establish, never infers a close, and keeps its log clean.
"""
from __future__ import annotations

import gzip
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts", "handicap"))

from nfl_edge.handicap import store  # noqa: E402
from nfl_edge.handicap import actual_wager_postmortem as PM  # noqa: E402
from nfl_edge.handicap.import_routed_settlements import import_rows as import_settlements  # noqa: E402
from nfl_edge.handicap.import_routed_wagers import import_rows as import_wagers  # noqa: E402
from nfl_edge.handicap.import_routed_wagers import mint_imported_wager_id  # noqa: E402

import actual_wager_postmortem as PM_SCRIPT  # noqa: E402
import import_routed_settlements as SETTLE_SCRIPT  # noqa: E402
import import_routed_wagers as WAGER_SCRIPT  # noqa: E402
import validate_routed_ledger as VALIDATE  # noqa: E402

KEY = "kalshi:v1:aaaa"
KEY2 = "kalshi:v1:bbbb"
TICKER = "KXNFLGAME-26SEP20CARATL-CAR"
TICKER2 = "KXNFLTOTAL-26SEP20CARATL-44"
GAMES = [
    {"game_id": "2026_02_CAR_ATL", "season": 2026, "week": 2, "game_type": "REG", "gameday": "2026-09-20",
     "away_team": "CAR", "home_team": "ATL", "kickoff_utc": None, "has_result": True},
    {"game_id": "2026_03_ATL_GB", "season": 2026, "week": 3, "game_type": "REG", "gameday": "2026-09-24",
     "away_team": "ATL", "home_team": "GB", "kickoff_utc": None, "has_result": False},
]
WAGER = {
    "source_bet_key": KEY, "import_batch_id": "kalshi-router-v1", "entry_method": "IMPORTED_RECEIPT",
    "game_date": "2026-09-20", "market_ticker": TICKER, "side": "YES", "executed_at": "2026-09-20T15:00:00Z",
    "contracts": 10.0, "actual_price": 0.50, "stake": 5.10, "fees_paid": 0.10, "fees_are_estimated": False,
    "fee_state": "ACTUAL_API_FILL", "venue": "kalshi",
}
WAGER2 = dict(WAGER, source_bet_key=KEY2, market_ticker=TICKER2, side="NO", actual_price=0.40, stake=4.07,
              fees_paid=0.07)
SETTLEMENT = {"source_bet_key": KEY, "market_ticker": TICKER, "side": "YES", "settlement_status": "SETTLED",
              "settled_at": "2026-09-21T00:00:00Z", "result": "WON", "gross_return": 10.0, "net_profit_loss": 4.85,
              "refusals": []}


def verdicts(result):
    return [r["status"] for r in result["receipts"]]


# ------------------------------------------------------------------------------------------ wager receipts

def test_every_payload_row_gets_a_receipt_with_both_identities(tmp_path):
    bad = dict(WAGER, source_bet_key="kalshi:v1:cccc", game_date="2026-12-25")
    r = import_wagers(str(tmp_path), [WAGER, bad], games=GAMES)
    assert verdicts(r) == ["NEW", "REFUSED"]
    assert r["receipts"][0]["source_bet_key"] == KEY
    assert r["receipts"][0]["imported_wager_id"] == mint_imported_wager_id(KEY)
    assert r["receipts"][1]["source_bet_key"] == "kalshi:v1:cccc" and r["receipts"][1]["success"] is False


def test_an_identical_redelivery_is_a_duplicate_noop(tmp_path):
    import_wagers(str(tmp_path), [WAGER], games=GAMES)
    again = import_wagers(str(tmp_path), [dict(WAGER, import_batch_id="some-other-batch")], games=GAMES)
    assert verdicts(again) == ["DUPLICATE_NOOP"]


def test_a_redelivery_that_disagrees_about_money_is_a_conflict_and_nothing_is_rewritten(tmp_path):
    import_wagers(str(tmp_path), [WAGER], games=GAMES)
    before = store.read_kind(str(tmp_path), "imported_wagers")
    r = import_wagers(str(tmp_path), [dict(WAGER, stake=6.0, fees_paid=0.2)], games=GAMES)
    assert verdicts(r) == ["CONFLICT"] and r["refused"] == 1
    assert [f["field"] for f in r["receipts"][0]["conflicting_fields"]] == ["stake", "fees_paid"]
    assert store.read_kind(str(tmp_path), "imported_wagers") == before


def test_the_same_order_resolving_to_a_different_week_is_a_conflict_not_a_second_record(tmp_path):
    import_wagers(str(tmp_path), [WAGER], games=GAMES)
    r = import_wagers(str(tmp_path), [dict(WAGER, game_date="2026-09-24")], games=GAMES)
    assert verdicts(r) == ["CONFLICT"]
    assert len(store.read_kind(str(tmp_path), "imported_wagers")) == 1


def test_the_wager_script_writes_row_receipts_without_economics(tmp_path):
    payload = tmp_path / "NFL.json"
    payload.write_text(json.dumps({"importBatchId": "kalshi-router-v1", "rows": [WAGER]}))
    sched = tmp_path / "games.csv"
    sched.write_text("game_id,season,game_type,week,gameday,gametime,away_team,home_team,result\n"
                     "2026_02_CAR_ATL,2026,REG,2,2026-09-20,13:00,CAR,ATL,3\n")
    out = tmp_path / "receipts.json"
    hd = tmp_path / "hd"
    (hd / "data").mkdir(parents=True)
    assert WAGER_SCRIPT.main(["--payload", str(payload), "--handicap-root", str(hd), "--schedule", str(sched),
                              "--receipts-out", str(out)]) == WAGER_SCRIPT.EXIT_OK
    doc = json.load(open(out))
    assert doc["rows"][0]["status"] == "NEW" and doc["rows"][0]["source_bet_key"] == KEY
    text = out.read_text()
    for sensitive in (TICKER, "5.1", "0.5"):
        assert sensitive not in text


# ------------------------------------------------------------------------------------------ settlement receipts

def test_settlement_receipts_new_duplicate_and_orphan(tmp_path):
    import_wagers(str(tmp_path), [WAGER], games=GAMES)
    orphan = dict(SETTLEMENT, source_bet_key="kalshi:v1:ghost")
    first = import_settlements(str(tmp_path), [SETTLEMENT, orphan])
    assert verdicts(first) == ["NEW", "REFUSED"]
    assert import_settlements(str(tmp_path), [SETTLEMENT])["receipts"][0]["status"] == "DUPLICATE_NOOP"


def test_a_terminal_settlement_can_never_be_regressed_or_rewritten(tmp_path):
    import_wagers(str(tmp_path), [WAGER], games=GAMES)
    import_settlements(str(tmp_path), [SETTLEMENT])
    before = store.read_kind(str(tmp_path), "wager_settlements")
    flipped = dict(SETTLEMENT, result="LOST", gross_return=0.0, net_profit_loss=-5.10)
    r = import_settlements(str(tmp_path), [flipped])
    assert verdicts(r) == ["CONFLICT"]
    assert {f["field"] for f in r["receipts"][0]["conflicting_fields"]} == {"result", "gross_return", "net_profit_loss"}
    assert store.read_kind(str(tmp_path), "wager_settlements") == before


def test_the_settlement_script_writes_row_receipts(tmp_path):
    import_wagers(str(tmp_path), [WAGER], games=GAMES)
    payload = tmp_path / "NFL-settlements.json"
    payload.write_text(json.dumps({"settlements": [SETTLEMENT]}))
    out = tmp_path / "r.json"
    assert SETTLE_SCRIPT.main(["--payload", str(payload), "--handicap-root", str(tmp_path),
                               "--receipts-out", str(out)]) == SETTLE_SCRIPT.EXIT_OK
    row = json.load(open(out))["rows"][0]
    assert row["status"] == "NEW" and row["source_bet_key"] == KEY and row["settlement_id"].startswith("stl-")


# ------------------------------------------------------------------------------------------ ledger validator

def _seed(tmp_path):
    import_wagers(str(tmp_path), [WAGER, WAGER2], games=GAMES)
    import_settlements(str(tmp_path), [SETTLEMENT])
    return str(tmp_path)


def test_a_ledger_built_by_the_importers_validates_clean(tmp_path):
    r = VALIDATE.validate_tree(_seed(tmp_path))
    assert (r["wagers"], r["settlements"], r["problems"]) == (2, 1, 0)


def test_a_record_filed_in_the_wrong_week_is_caught(tmp_path):
    root = _seed(tmp_path)
    src = store.record_path(root, "imported_wagers", 2026, 2, mint_imported_wager_id(KEY2))
    dst = store.record_path(root, "imported_wagers", 2026, 3, mint_imported_wager_id(KEY2))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    os.rename(src, dst)
    assert "wager:FILED_IN_THE_WRONG_WEEK" in VALIDATE.validate_tree(root)["problem_categories"]


def test_an_orphan_settlement_and_a_duplicate_order_are_caught(tmp_path):
    root = _seed(tmp_path)
    wpath = store.record_path(root, "imported_wagers", 2026, 2, mint_imported_wager_id(KEY))
    os.remove(wpath)
    cats = VALIDATE.validate_tree(root)["problem_categories"]
    assert "settlement:ORPHAN_NO_SUCH_WAGER" in cats
    root2 = str(tmp_path / "second")
    import_wagers(root2, [WAGER], games=GAMES)
    doc = json.load(open(store.record_path(root2, "imported_wagers", 2026, 2, mint_imported_wager_id(KEY))))
    doc["imported_wager_id"] = "manual-1"
    with open(store.record_path(root2, "imported_wagers", 2026, 2, "manual-1"), "w") as f:
        json.dump(doc, f)
    assert "wager:MORE_THAN_ONE_RECORD_FOR_ONE_ORDER" in VALIDATE.validate_tree(root2)["problem_categories"]


def test_the_validator_exits_nonzero_on_a_problem_and_prints_no_wager(tmp_path, capsys):
    root = _seed(tmp_path)
    with open(os.path.join(root, "data", "imported_wagers", "2026", "week_02", "junk.json"), "w") as f:
        f.write("{not json")
    assert VALIDATE.main(["--handicap-root", root]) == 1
    printed = capsys.readouterr().out
    assert TICKER not in printed and KEY not in printed and "UNPARSEABLE" in printed


# ------------------------------------------------------------------------------------------ postmortem

def _close(ticker, mid, no_mid, status="CLOSE_OK", quality="EXCELLENT", cid="c1"):
    return {"ticker": ticker, "game_id": "2026_02_CAR_ATL", "close_status": status, "close_quality": quality,
            "close_id": cid, "mid": mid, "no_mid": no_mid}


def test_no_headline_is_stated_while_any_figure_is_unestablished():
    wagers = [dict(WAGER, season=2026, week=2, imported_wager_id="w1"),
              dict(WAGER2, season=2026, week=2, imported_wager_id="w2")]
    doc = PM.build(wagers, [SETTLEMENT], [], season=2026)
    t = doc["totals"]
    assert t["pending"] == 1 and t["complete"] is False
    assert t["net_profit_loss"] is None and t["roi"] is None
    assert t["established_subset"]["net_profit_loss"] == 4.85
    assert "ESTABLISHED SUBSET ONLY" in PM.render(doc)


def test_a_fully_established_period_states_gross_net_roi_and_the_settlement_fee():
    doc = PM.build([dict(WAGER, season=2026, week=2, imported_wager_id="w1")], [SETTLEMENT], [], season=2026)
    t = doc["totals"]
    assert t["complete"] and t["gross_return"] == 10.0 and t["net_profit_loss"] == 4.85
    assert t["roi"] == round(4.85 / 5.10, 6)
    assert t["settlement_fees_established"] == round(10.0 - 5.10 - 4.85, 4)


def test_clv_uses_the_side_held_and_never_infers_a_close():
    wagers = [dict(WAGER, season=2026, week=2, imported_wager_id="w1"),
              dict(WAGER2, season=2026, week=2, imported_wager_id="w2"),
              dict(WAGER, source_bet_key="k3", market_ticker="KXNFLSPREAD-26SEP20CARATL-ATL3", season=2026, week=2,
                   imported_wager_id="w3")]
    closes = [_close(TICKER, 0.55, 0.45), _close(TICKER2, 0.62, 0.38)]
    rows = {r["imported_wager_id"]: r for r in PM.build(wagers, [], closes, season=2026)["wagers"]}
    assert rows["w1"]["clv_per_contract"] == 0.05 and rows["w1"]["clv_state"] == "CLV_VALID"      # YES: 0.55-0.50
    assert rows["w2"]["clv_per_contract"] == -0.02                                                  # NO: 0.38-0.40
    assert rows["w3"]["clv_state"] == "NO_CANONICAL_CLOSE" and rows["w3"]["clv_per_contract"] is None
    assert rows["w1"]["family"] == "game_winner" and rows["w2"]["family"] == "total"


def test_stale_one_sided_or_conflicting_closes_are_named_not_averaged():
    wagers = [dict(WAGER, season=2026, week=2, imported_wager_id="w1"),
              dict(WAGER2, season=2026, week=2, imported_wager_id="w2")]
    closes = [_close(TICKER, 0.55, 0.45, quality="STALE"), _close(TICKER2, None, None, status="CLOSE_ONE_SIDED"),
              _close(TICKER, 0.70, 0.30, cid="c2")]
    doc = PM.build(wagers, [], closes, season=2026)
    states = {r["imported_wager_id"]: r["clv_state"] for r in doc["wagers"]}
    assert states == {"w1": "CLOSE_CONFLICT", "w2": "CLOSE_ONE_SIDED"}
    assert doc["totals"]["clv"]["valid"] == 0 and doc["totals"]["clv"]["mean_per_contract"] is None


def test_the_postmortem_script_logs_counts_only_and_flags_overdue_settlements(tmp_path, capsys):
    root = str(tmp_path / "hd")
    import_wagers(root, [WAGER, WAGER2], games=GAMES)
    import_settlements(root, [SETTLEMENT])
    closes = tmp_path / "closes" / "2026_02_CAR_ATL"
    closes.mkdir(parents=True)
    with gzip.open(closes / "close-2.1.0.x.closes_v2.jsonl.gz", "wt") as f:
        f.write(json.dumps(_close(TICKER, 0.55, 0.45)) + "\n")
    rc = PM_SCRIPT.main(["--handicap-root", root, "--closes-root", str(tmp_path / "closes"), "--season", "2026",
                         "--out", str(tmp_path / "out"), "--today", "2026-09-30", "--fail-on-overdue-days", "3"])
    assert rc == 1                                   # WAGER2 has no settlement 10 days after its game
    printed = capsys.readouterr().out
    for sensitive in (TICKER, TICKER2, "5.1", "4.85", "10.0", KEY):
        assert sensitive not in printed, sensitive
    assert os.path.exists(tmp_path / "out" / "2026" / "week_02.ACTUAL_WAGERS.md")
    assert os.path.exists(tmp_path / "out" / "2026" / "season.actual_wagers.json")


def test_nothing_that_measures_model_performance_reads_the_postmortem():
    offenders = []
    for base in ("nfl_edge/evaluation", "nfl_edge/engines", "nfl_edge/arms", "nfl_edge/research"):
        for d, _s, names in os.walk(os.path.join(ROOT, base)):
            for n in names:
                if n.endswith(".py") and "actual_wager_postmortem" in open(os.path.join(d, n)).read():
                    offenders.append(os.path.join(d, n))
    assert offenders == []


def test_a_settlement_fee_equal_to_the_entry_fees_is_reconciled_not_rewritten():
    """fee_cost equal to the entry fee already in the stake is the position's trading fee, not a second one."""
    w = dict(WAGER, season=2026, week=2, imported_wager_id="w1")                      # stake 5.10 incl. fee 0.10
    s = dict(SETTLEMENT, gross_return=10.0, net_profit_loss=round(10.0 - 5.10 - 0.10, 6))
    doc = PM.build([w], [s], [], season=2026)
    r = doc["wagers"][0]
    assert r["net_profit_loss"] == 4.8                         # recorded, untouched
    assert r["fee_reconciliation"] == "FEE_EQUALS_ENTRY_FEES" and r["net_fee_reconciled"] == 4.9
    fr = doc["totals"]["fee_reconciled"]
    assert fr["complete"] and fr["net_profit_loss"] == 4.9 and fr["double_counted_fees"] == 0.1


def test_a_yes_no_pair_reconciles_against_both_legs_entry_fees():
    a = dict(WAGER, season=2026, week=2, imported_wager_id="a", fees_paid=0.10, stake=5.10)
    b = dict(WAGER2, season=2026, week=2, imported_wager_id="b", market_ticker=TICKER, fees_paid=0.20, stake=4.20)
    sa = dict(SETTLEMENT, gross_return=10.0, net_profit_loss=round(10.0 - 5.10 - 0.30, 6))
    sb = dict(SETTLEMENT, source_bet_key=KEY2, side="NO", result="LOST", gross_return=0.0,
              net_profit_loss=round(0.0 - 4.20 - 0.30, 6))
    rows = {r["imported_wager_id"]: r for r in PM.build([a, b], [sa, sb], [], season=2026)["wagers"]}
    assert rows["a"]["fee_reconciliation"] == rows["b"]["fee_reconciliation"] == "FEE_EQUALS_ENTRY_FEES"
    assert rows["b"]["net_fee_reconciled"] == -4.2


def test_an_unexplained_settlement_fee_gets_no_reconciled_figure():
    w = dict(WAGER, season=2026, week=2, imported_wager_id="w1")
    s = dict(SETTLEMENT, gross_return=10.0, net_profit_loss=round(10.0 - 5.10 - 0.55, 6))
    doc = PM.build([w], [s], [], season=2026)
    assert doc["wagers"][0]["fee_reconciliation"] == "UNRECONCILED"
    assert doc["totals"]["fee_reconciled"]["net_profit_loss"] is None
