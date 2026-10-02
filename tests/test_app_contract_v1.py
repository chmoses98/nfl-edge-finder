"""The Edge Finder app export (scripts/app_export.py) against the vendored contract.

Everything here is about the ADAPTER: the vendored contract stays byte-identical, the export runs end to end
on records shaped exactly like the committed ones, the output is deterministic, a failure never damages the
last good payload, stale inputs are reported as stale, naive timestamps never leave, no secret-shaped string
leaks, and the wager -> settlement accounting equals the ledger's own sums. Nothing here touches a model.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import shutil
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (ROOT, os.path.join(ROOT, "contract")):
    if p not in sys.path:
        sys.path.insert(0, p)

from edge_finder_contract import publish, sync  # noqa: E402
from scripts import app_export  # noqa: E402

NOW = "2026-10-02T00:30:00Z"
BUILT_AT = "2026-10-02T00:06:36.244692+00:00"
QUERIED_AT = "2026-10-01T23:42:47+00:00"
WRITTEN_AT = "2026-10-02T00:05:18.908995+00:00"
GAME = "2026_04_PIT_CLE"
KICKOFF = "2026-10-02T00:15:00+00:00"
SECRET_SHAPES = ("PRIVATE KEY", "ghp_", "github_pat_", "Bearer ", "AIRTABLE")


# ------------------------------------------------------------------------------------------- fixtures

def _row(ticker, **over):
    base = {
        "analysis_state": "MODEL_PRICED", "bucket": "A", "coherent_simulation": None, "executable": True,
        "family": "GAME_WINNER", "flags": [],
        "incumbent": {"disagreement_vs_mid": 0.02, "model_probability": 0.61, "model_uncertainty": None,
                      "support_reason": None, "support_state": "SUPPORTED"},
        "manual_review_reason": None, "mid": 0.59, "minutes_since_price_change": 13.1777, "minutes_to_kickoff": 45.4,
        "no_ask": 0.42, "no_bid": 0.4, "no_real_market": False, "open_interest": 4988.5, "operator": "event",
        "period": "FULL", "player_id": None, "reason": "priced",
        "shadow_v2": {"contract_value": None, "engine": "GAME", "p_yes": 0.62, "primary_arm": "BOARD_V2",
                      "provenance": "v2p25", "semantic_confidence": "PROVEN", "settlement_reachability": "DISPATCHABLE",
                      "support_reason": None, "support_state": "PRICED"},
        "stat": None, "subject": "PIT", "subject_kind": "team", "threshold": None, "ticker": ticker,
        "volume": 5109.8, "width": 0.02, "yes_ask": 0.6, "yes_bid": 0.58, "yes_meaning": f"YES iff PIT wins [{ticker}]",
    }
    base.update(over)
    return base


def make_report(root):
    """A RUN NFL report directory shaped like latest/ on handicap-reports (manifest + analysis shards)."""
    reports = os.path.join(root, "report")
    os.makedirs(os.path.join(reports, "analysis", "games"))
    manifest = {
        "report_status": "SUCCESS", "built_at": BUILT_AT, "handicap_run_id": "20261002T000636Z",
        "season": 2026, "week": 4, "season_type": "REG", "slate_id": "2026-REG-04", "model_version": "shadow-0.4.0",
        "trigger": "horizon", "packet_sha": "84bef22ef95c22a6ed3d",
        "real_money_status": "NOT VALIDATED -- this packet recommends nothing and authorises nothing",
        "sources": {"main_sha": "054ecb282070334dbe6ea607485b4da79ec56907", "market_data_sha": "8db99ee0317b40bb",
                    "workflow_run_id": "36942566784"},
        "vintages": {"shadow_pricing": {"ledger_run_id": "20261001T234247Z", "written_at": WRITTEN_AT, "age_min": 1.3},
                     "kalshi_capture": {"snapshot_run_id": "20261001T234247Z", "queried_at": QUERIED_AT, "age_min": 23.8},
                     "context": {"run_id": "20261001T234647Z", "captured_at": "2026-10-01T23:46:47+00:00"},
                     "simulation": {"generated_at": "2026-10-02T00:05:20.790238+00:00"}},
        "kickoffs": [{"game_id": GAME, "kickoff_utc": KICKOFF, "minutes_to_kickoff": 8.4, "game_state": "PREGAME",
                      "file": f"games/{GAME}.md"}],
        "counts": {"games": 1},
    }
    shard = {
        "schema_version": "analysis-1.0.0", "game_id": GAME, "away_team": "PIT", "home_team": "CLE",
        "kickoff_utc": KICKOFF, "game_state": "PREGAME", "season": 2026, "week": 4, "minutes_to_kickoff": 8.4,
        "capture": {"ledger_run_id": "20261001T234247Z", "incumbent_model_version": "shadow-0.4.0"},
        "coverage": {"buckets": {"A": {"n": 2, "meaning": "validated"}, "B": {"n": 1, "meaning": "research"}}},
        "authority_notes": {"coherent_simulation": "RESEARCH."}, "shadow_v2": {"authority": "RESEARCH ONLY."},
        "rows": [
            _row("KXNFLGAME-26OCT01PITCLE-PIT"),
            _row("KXNFLGAME-26OCT01PITCLE-CLE", subject="CLE", mid=0.41, yes_bid=0.4, yes_ask=0.42, no_bid=0.58,
                 no_ask=0.6, incumbent={"disagreement_vs_mid": -0.02, "model_probability": 0.39,
                                        "model_uncertainty": None, "support_reason": None, "support_state": "SUPPORTED"},
                 yes_meaning="YES iff CLE wins"),
            _row("KXNFLSPREAD-26OCT01PITCLE-CLE4", family="SPREAD", stat="margin", operator=">", threshold=3.5,
                 subject="CLE", analysis_state="SHADOW_V2_PROJECTED", bucket="B",
                 incumbent={"disagreement_vs_mid": None, "model_probability": None, "model_uncertainty": None,
                            "support_reason": "family SPREAD not priced", "support_state": "UNSUPPORTED_MODEL"},
                 coherent_simulation={"football_disagreement_vs_mid": None, "p_football": 0.5, "p_market": 0.48,
                                      "p_reconciled": 0.48, "ranked": False, "reconcile_weight": 0.0,
                                      "reconciled_disagreement_vs_mid": None, "support_reason": None,
                                      "support_state": "RECONCILED"},
                 mid=0.48, yes_bid=0.47, yes_ask=0.49, no_bid=0.51, no_ask=0.53, yes_meaning="YES iff CLE margin > 3.5"),
            _row("KXNFLRECYDS-26OCT01PITCLE-PITGPICKENS14-60", family="PLAYER_STAT", stat="receiving_yards",
                 operator=">=", threshold=60.0, subject="PIT", subject_kind="player", player_id="00-0038428",
                 analysis_state="MANUAL_HANDICAP", bucket="C",
                 incumbent={"disagreement_vs_mid": None, "model_probability": None, "model_uncertainty": None,
                            "support_reason": "no model for stat", "support_state": "UNSUPPORTED_MODEL"},
                 mid=0.55, yes_bid=0.54, yes_ask=0.56, no_bid=0.44, no_ask=0.46, yes_meaning="YES iff receiving_yards >= 60"),
        ],
    }
    analysis = {"schema_version": "analysis-manifest-1.0.0", "built_at": BUILT_AT, "handicap_run_id": "20261002T000636Z",
                "season": 2026, "week": 4, "games": [{"game_id": GAME, "path": f"games/{GAME}.json", "rows": 4}],
                "models": {"incumbent": {"model_version": "shadow-0.4.0", "ledger_run_id": "20261001T234247Z"}},
                "real_money_status": "NOT VALIDATED -- this packet recommends nothing and authorises nothing"}
    json.dump(manifest, open(os.path.join(reports, "manifest.json"), "w"), indent=1)
    json.dump(analysis, open(os.path.join(reports, "analysis", "manifest.json"), "w"), indent=1)
    json.dump(shard, open(os.path.join(reports, "analysis", "games", f"{GAME}.json"), "w"))
    return reports


KEY_A = "kalshi:v1:ec8f1195ec0ac0435fd776512412096cb6445c3940beff0e49b4950e327fa959"
KEY_B = "kalshi:v1:6c3f858b27074e142964c77d4b7a99640fd8f4725b2df72a02158c47c5c3ebfa"


def make_ledger(root):
    """A handicap-data checkout: recommendations, imported wagers, settlements and one economics amendment,
    each shaped exactly like the committed records (imported_wager.v1, nfl_wager_settlement.v1, ...)."""
    hd = os.path.join(root, "handicap-data")

    def put(kind, season, week, rid, doc):
        d = os.path.join(hd, "data", kind, str(season), f"week_{week:02d}")
        os.makedirs(d, exist_ok=True)
        json.dump(doc, open(os.path.join(d, f"{rid}.json"), "w"), indent=1)

    rec = {"recommendation_id": "rec_20261001_230000_001", "schema_version": "1.1.0",
           "created_at": "2026-10-01T23:00:00+00:00", "handicap_run_id": "20261001T224233Z", "packet_sha": "abc",
           "season": 2026, "week": 4, "game_id": GAME, "kickoff_utc": KICKOFF,
           "market_ticker": "KXNFLGAME-26OCT01PITCLE-PIT", "market_family": "GAME_WINNER", "side": "YES",
           "yes_bid": 0.58, "yes_ask": 0.6, "no_bid": 0.4, "no_ask": 0.42, "mid": 0.59,
           "market_timestamp": "2026-10-01T22:42:33+00:00", "support_state": "SUPPORTED", "model_version": "shadow-0.4.0",
           "model_probability": 0.61, "probability_low": 0.6, "probability_mid": 0.65, "probability_high": 0.7,
           "bet_up_to_probability": 0.62, "grade": "B", "proposed_stake": 50, "recommended_stake": 40,
           "decision": "RECOMMENDED", "primary_thesis": "Rested defence against a backup quarterback.",
           "key_supporting_factors": ["backup QB"], "counterarguments": ["short week"], "uncertainties": [],
           "reasoning_tags": ["ROLE_EXPANSION"], "test_only": False}
    put("recommendations", 2026, 4, rec["recommendation_id"], rec)
    passed = dict(rec, recommendation_id="rec_20261001_230000_002", market_ticker="KXNFLSPREAD-26OCT01PITCLE-CLE4",
                  decision="PASS", grade="PASS", recommended_stake=None, proposed_stake=None, bet_up_to_probability=None)
    put("recommendations", 2026, 4, passed["recommendation_id"], passed)
    test_only = dict(rec, recommendation_id="rec_e2e_test", test_only=True,
                     primary_thesis="TEST_ONLY bridge verification. Not a real betting decision.")
    put("recommendations", 2026, 4, test_only["recommendation_id"], test_only)

    wager_a = {"actual_price": 0.59, "contracts": 247.14, "entry_method": "IMPORTED_RECEIPT", "event_refs": {},
               "executed_at": "2026-10-01T23:52:22Z", "execution_action": "BUY", "fee_state": "ACTUAL_API_FILL",
               "fees_are_estimated": False, "fees_paid": 4.1849, "game_date": "2026-10-01", "gross_return": None,
               "import_batch_id": "kalshi-router-v1", "imported_wager_id": "routed-f1640b6c182f1b4907509f28",
               "market_ticker": "KXNFLGAME-26OCT01PITCLE-PIT", "net_profit_loss": None, "notes": "", "result": None,
               "schema_version": "imported_wager.v1", "season": 2026, "settlement_status": None, "side": "YES",
               "source_bet_key": KEY_A, "stake": 150.0, "test_only": False, "venue": "kalshi", "week": 4}
    put("imported_wagers", 2026, 4, wager_a["imported_wager_id"], wager_a)
    wager_b = dict(wager_a, imported_wager_id="routed-01726fe2b7b38164f2f52445", source_bet_key=KEY_B,
                   market_ticker="KXNFLMOSTRECYDS-26SEP13BUFHOU-HOUNCOLLINS12", executed_at="2026-09-13T16:08:21Z",
                   actual_price=0.43, contracts=111.81, stake=49.9967, fees_paid=1.9184, game_date="2026-09-13", week=1)
    wager_b.pop("execution_action")
    put("imported_wagers", 2026, 1, wager_b["imported_wager_id"], wager_b)

    stl_a = {"economics_version": "router-settlement-economics.v2", "gross_return": 247.14,
             "market_ticker": wager_a["market_ticker"], "net_profit_loss": 97.14, "refusals": [], "result": "WON",
             "schema_version": "nfl_wager_settlement.v1", "season": 2026, "settled_at": "2026-10-02T03:49:24.877876Z",
             "settlement_id": "stl-f1640b6c182f1b4907509f28", "settlement_status": "SETTLED", "side": "YES",
             "source_bet_key": KEY_A, "venue": "kalshi", "week": 4}
    put("wager_settlements", 2026, 4, stl_a["settlement_id"], stl_a)
    stl_b = {"gross_return": 0.0, "market_ticker": wager_b["market_ticker"], "net_profit_loss": -51.9151,
             "refusals": [], "result": "LOST", "schema_version": "nfl_wager_settlement.v1", "season": 2026,
             "settled_at": "2026-09-14T04:00:00Z", "settlement_id": "stl-01726fe2b7b38164f2f52445",
             "settlement_status": "SETTLED", "side": "YES", "source_bet_key": KEY_B, "venue": "kalshi", "week": 1}
    put("wager_settlements", 2026, 1, stl_b["settlement_id"], stl_b)
    amendment = {"amendment_id": "amd-e88e74686111d6e106d3958e", "amends": stl_b["settlement_id"],
                 "amends_kind": "wager_settlements", "amended_economics_version": "router-settlement-economics.v2",
                 "prior_economics_version": "router-settlement-economics.v1", "reason_code": "FEE_DOUBLE_COUNT_CORRECTION",
                 "schema_version": "nfl_wager_settlement_amendment.v1", "season": 2026, "week": 1,
                 "source_bet_key": KEY_B, "provenance": "kalshi-bet-router settle-wagers",
                 "superseded_fields": {"net_profit_loss": {"recorded": -51.9151, "corrected": -49.9967}},
                 "original_record_sha256": "0" * 64}
    put("wager_settlement_amendments", 2026, 1, amendment["amendment_id"], amendment)
    return hd


def run_export(reports, hd, out, *, now=NOW, extra=()):
    return app_export.main(["--reports-dir", reports, "--handicap-root", hd, "--out", out, "--now", now,
                            "--commit-sha", "deadbeef", "--workflow-run-id", "1", *extra])


def _tree_digests(root):
    out = {}
    for d, _, names in os.walk(root):
        for n in names:
            p = os.path.join(d, n)
            out[os.path.relpath(p, root)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def _doc(out, name):
    return json.load(open(os.path.join(out, f"{name}.json")))


@pytest.fixture
def fixture_root(tmp_path):
    return make_report(str(tmp_path)), make_ledger(str(tmp_path))


# ------------------------------------------------------------------------------------------- 1. the contract

def test_the_vendored_contract_is_intact():
    assert sync.check() == []


# ------------------------------------------------------------------------------------------- 2. end to end

def test_export_runs_end_to_end_and_verifies(fixture_root, tmp_path):
    reports, hd = fixture_root
    out = str(tmp_path / "app")
    assert run_export(reports, hd, out) == 0
    assert publish.verify_published(out) == []
    man = _doc(out, "manifest")
    assert man["counts"] == {"board": 2, "events": 2, "markets": 5, "model_prices": 2, "recommendations": 2,
                             "runs": 1, "settlements": 2, "theses": 1, "wagers": 2}
    events = {e["source_ids"]["nflverse_game_id"]: e for e in _doc(out, "events")["items"]}
    assert GAME in events and events[GAME]["status"] == "SCHEDULED"
    assert events[GAME]["start_time_confidence"] == "SCHEDULED"
    # the week-1 wager's game is off the board: identity derived from the ticker's teams and the ledger's
    # season/week, kickoff a PLACEHOLDER date because no schedule root was given
    assert events["2026_01_BUF_HOU"]["start_time_confidence"] == "PLACEHOLDER"
    markets = {m["kalshi_ticker"]: m for m in _doc(out, "markets")["items"]}
    assert markets["KXNFLGAME-26OCT01PITCLE-PIT"]["market_status"] == "OPEN"
    assert markets["KXNFLGAME-26OCT01PITCLE-PIT"]["side"] == "AWAY"
    assert markets["KXNFLSPREAD-26OCT01PITCLE-CLE4"]["threshold"] == 3.5
    assert markets["KXNFLRECYDS-26OCT01PITCLE-PITGPICKENS14-60"]["player_id"].startswith("prt_")
    assert markets["KXNFLRECYDS-26OCT01PITCLE-PITGPICKENS14-60"]["extensions"]["gsis_id"] == "00-0038428"
    stub = markets["KXNFLMOSTRECYDS-26SEP13BUFHOU-HOUNCOLLINS12"]
    assert stub["source"] == "handicap-data" and stub["yes_bid"] is None
    prices = _doc(out, "model_prices")["items"]
    assert {p["fair_probability"] for p in prices} == {0.61, 0.39}
    assert all(p["data_quality_status"] == "OK" and p["support_status"] == "SUPPORTED" for p in prices)
    assert all(p["extensions"]["shadow_v2"]["p_yes"] == 0.62 for p in prices)
    recs = {r["source_ids"]["recommendation_id"]: r for r in _doc(out, "recommendations")["items"]}
    assert "rec_e2e_test" not in recs, "test_only ledger records never reach the app"
    assert recs["rec_20261001_230000_001"]["status"] == "RECOMMENDED"
    assert recs["rec_20261001_230000_001"]["authority"] == "MANUAL"
    assert recs["rec_20261001_230000_001"]["research_only"] is False
    assert recs["rec_20261001_230000_001"]["stake_dollars"] == 40
    assert recs["rec_20261001_230000_001"]["fair_probability"] == 0.65
    assert recs["rec_20261001_230000_001"]["current_price"] == 0.6
    assert recs["rec_20261001_230000_002"]["status"] == "PASS"
    health = _doc(out, "health")
    assert health["bet_authority"] == "MANUAL" and health["overall_status"] == "HEALTHY"
    assert health["thresholds"]["market_data"] == {"fresh_after_seconds": 1800, "stale_after_seconds": 10800}
    assert health["thresholds"]["model"] == {"fresh_after_seconds": 7200, "stale_after_seconds": 86400}
    assert health["last_market_capture"] == "2026-10-01T23:42:47Z"
    assert health["last_model_generated"] == "2026-10-02T00:05:18Z"
    run = _doc(out, "runs")["items"][0]
    assert run["source_ids"]["native_run_id"] == "20261002T000636Z" and run["commit_sha"] == "deadbeef"
    assert run["markets_discovered"] == 4 and run["markets_priced"] == 2


def test_wagers_link_temporally_and_settle_with_the_ledgers_canonical_economics(fixture_root, tmp_path):
    reports, hd = fixture_root
    out = str(tmp_path / "app")
    assert run_export(reports, hd, out) == 0
    wagers = {w["source_ids"]["imported_wager_id"]: w for w in _doc(out, "wagers")["items"]}
    settlements = {s["wager_id"]: s for s in _doc(out, "settlements")["items"]}
    a = wagers["routed-f1640b6c182f1b4907509f28"]
    assert a["source"] == "KALSHI_ROUTER" and a["side"] == "BUY" and a["fees"] == 4.1849
    assert a["average_price"] == 0.59 and a["selection"] == "YES"
    # placed at 23:52:22, after the 23:42:47 capture the model price was priced from -> linked; the
    # recommendation was created at 23:00 for the same market and side -> linked
    assert a["model_price_id"] and a["recommendation_id"]
    assert a["linkage"]["model_inputs_as_of"] == "2026-10-01T23:42:47Z"
    assert a["settlement_status"] == "SETTLED" and a["settlement_id"] == settlements[a["wager_id"]]["settlement_id"]
    assert settlements[a["wager_id"]]["result"] == "WON" and settlements[a["wager_id"]]["net_pnl"] == 97.14
    assert settlements[a["wager_id"]]["verification_status"] == "EXCHANGE_CONFIRMED"
    b = wagers["routed-01726fe2b7b38164f2f52445"]
    assert b["side"] is None and b["model_price_id"] is None and b["recommendation_id"] is None
    sb = settlements[b["wager_id"]]
    assert sb["result"] == "LOST" and sb["winning_side"] == "NO"
    assert sb["net_pnl"] == -49.9967, "the newest admissible economics amendment wins"
    assert sb["extensions"]["amendment_status"] == "AMENDED"
    assert sb["extensions"]["recorded_net_profit_loss"] == -51.9151
    # 9. cross reference + P&L totals equal the ledger's own canonical sums
    for w in wagers.values():
        assert w["settlement_id"] == settlements[w["wager_id"]]["settlement_id"] and settlements[w["wager_id"]]["market_id"] == w["market_id"]
    perf = _doc(out, "performance")
    assert perf["totals"]["net_pnl"] == round(97.14 - 49.9967, 4)
    assert perf["totals"]["gross_payout"] == 247.14
    assert perf["totals"]["stake"] == round(150.0 + 49.9967, 4)
    assert perf["totals"]["settled"] == 2 and perf["totals"]["won"] == 1 and perf["totals"]["lost"] == 1


# ------------------------------------------------------------------------------------------- 3. determinism

def test_two_runs_on_the_same_inputs_are_byte_identical(fixture_root, tmp_path):
    reports, hd = fixture_root
    a, b = str(tmp_path / "a"), str(tmp_path / "b")
    assert run_export(reports, hd, a) == 0 and run_export(reports, hd, b) == 0
    assert _tree_digests(a) == _tree_digests(b)
    man = _doc(a, "manifest")
    for name, entry in man["files"].items():
        assert hashlib.sha256(open(os.path.join(a, entry["path"]), "rb").read()).hexdigest() == entry["sha256"], name


# ------------------------------------------------------------------------------------------- 4. failure safety

def test_a_broken_input_leaves_the_previous_payload_untouched_and_marks_health(fixture_root, tmp_path):
    reports, hd = fixture_root
    out = str(tmp_path / "app")
    assert run_export(reports, hd, out) == 0
    before = _tree_digests(out)
    previous_run = _doc(out, "manifest")["run_id"]
    with open(os.path.join(reports, "analysis", "games", f"{GAME}.json"), "w") as f:
        f.write("{not json")
    assert run_export(reports, hd, out, now="2026-10-02T01:00:00Z") == 1
    after = _tree_digests(out)
    assert {k: v for k, v in after.items() if k != "health.json"} == {k: v for k, v in before.items() if k != "health.json"}
    health = _doc(out, "health")
    assert health["overall_status"] in ("DEGRADED", "UNAVAILABLE")
    assert health["components"]["export"]["status"] == "DEGRADED"
    assert health["payload_run_id"] == previous_run and health["errors"]
    assert publish.verify_published(out) == [], "the previous payload is still a consistent publication"


def test_a_failed_first_export_writes_health_only(fixture_root, tmp_path):
    reports, hd = fixture_root
    out = str(tmp_path / "app")
    os.remove(os.path.join(reports, "analysis", "manifest.json"))
    assert run_export(reports, hd, out) == 1
    assert sorted(os.listdir(out)) == ["health.json"]
    health = _doc(out, "health")
    assert health["overall_status"] == "UNAVAILABLE" and health["payload_run_id"] is None


# ------------------------------------------------------------------------------------------- 5. stale data

def test_far_future_now_reports_stale(fixture_root, tmp_path):
    reports, hd = fixture_root
    out = str(tmp_path / "app")
    assert run_export(reports, hd, out, now="2026-10-09T00:30:00Z") == 0
    health = _doc(out, "health")
    assert health["overall_status"] == "STALE"
    assert health["market_data_status"] == "STALE" and health["model_status"] == "STALE"
    board = _doc(out, "board")
    assert board["overall_status"] == "STALE"


# ------------------------------------------------------------------------------------------- 6. naive timestamps

def test_a_naive_timestamp_in_the_ledger_is_refused_not_emitted(fixture_root, tmp_path):
    reports, hd = fixture_root
    out = str(tmp_path / "app")
    assert run_export(reports, hd, out) == 0
    before = _tree_digests(out)
    p = os.path.join(hd, "data", "imported_wagers", "2026", "week_04", "routed-f1640b6c182f1b4907509f28.json")
    doc = json.load(open(p))
    doc["executed_at"] = "2026-10-01T23:52:22"
    json.dump(doc, open(p, "w"))
    assert run_export(reports, hd, out, now="2026-10-02T01:00:00Z") == 1
    assert "zone" in " ".join(_doc(out, "health")["errors"]).lower() or "naive" in " ".join(_doc(out, "health")["errors"]).lower()
    after = _tree_digests(out)
    assert {k: v for k, v in after.items() if k != "health.json"} == {k: v for k, v in before.items() if k != "health.json"}


def test_every_emitted_timestamp_is_canonical_utc(fixture_root, tmp_path):
    reports, hd = fixture_root
    out = str(tmp_path / "app")
    assert run_export(reports, hd, out) == 0
    stamp = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
    canonical = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?Z$")

    def walk(o, path):
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, f"{path}.{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{path}[{i}]")
        elif isinstance(o, str) and stamp.match(o) and ".extensions." not in path:
            assert canonical.match(o), f"{path}: {o!r} is not canonical UTC"

    for d, _, names in os.walk(out):
        for n in names:
            walk(json.load(open(os.path.join(d, n))), n)


# ------------------------------------------------------------------------------------------- 8. no secrets

def test_no_secret_shaped_string_in_any_output(fixture_root, tmp_path):
    reports, hd = fixture_root
    out = str(tmp_path / "app")
    assert run_export(reports, hd, out) == 0
    for d, _, names in os.walk(out):
        for n in names:
            text = open(os.path.join(d, n), encoding="utf-8").read()
            for shape in SECRET_SHAPES:
                assert shape not in text, f"{n} carries {shape!r}"


# ------------------------------------------------------------------------------------------- isolation

def test_the_exporter_reaches_neither_the_bridge_nor_preflight_and_stays_stdlib_only():
    from nfl_edge.handicap.report_isolation import FORBIDDEN_MODULES, reachable_modules
    from test_ci_dependencies import reachable_third_party

    reached = reachable_modules(ROOT, ["scripts/app_export.py"])
    dotted = {rel[:-3].replace("/", ".") for rel in reached}
    # the ledger READER is the one forbidden-for-the-report module the export legitimately needs
    assert not (dotted & (FORBIDDEN_MODULES - {"nfl_edge.handicap.store"})), sorted(dotted & FORBIDDEN_MODULES)
    assert reachable_third_party([os.path.join(ROOT, "scripts", "app_export.py")], precise=True) == {}


# ------------------------------------------------------------------------------------------- the publisher

def test_publish_script_stages_app_latest_beside_the_report(tmp_path):
    from scripts.ci import publish_handicap_report as pub

    wt, src, app = tmp_path / "wt", tmp_path / "src", tmp_path / "app"
    for d in (wt, src, app / "event_detail"):
        d.mkdir(parents=True)
    (src / "slate.md").write_text("slate")
    (wt / "app" / "latest").mkdir(parents=True)
    (wt / "app" / "latest" / "old.json").write_text("{}")
    (app / "manifest.json").write_text("{}")
    (app / "health.json").write_text("{}")
    pub.stage(str(wt), str(src), {}, None, replace_latest=True, app_src=str(app))
    assert (wt / "app" / "latest" / "manifest.json").exists()
    assert not (wt / "app" / "latest" / "old.json").exists(), "app/latest is replaced wholesale"
    # a run that does not replace latest/ does not replace app/latest either
    (app / "manifest.json").write_text('{"v": 2}')
    pub.stage(str(wt), str(src), {}, None, replace_latest=False, app_src=str(app))
    assert (wt / "app" / "latest" / "manifest.json").read_text() == "{}"
    # an empty staging directory is not a payload; the branch's own app/latest is carried forward
    empty = tmp_path / "empty"
    empty.mkdir()
    pub.stage(str(wt), str(src), {}, None, replace_latest=True, app_src=str(empty))
    assert (wt / "app" / "latest" / "manifest.json").exists()
    assert not pub.app_src_is_publishable(str(empty)) and pub.app_src_is_publishable(str(app))


@pytest.mark.parametrize("name", ["run-nfl.yml", "shadow-price.yml"])
def test_the_workflows_export_before_they_publish_and_cannot_block_the_report(name):
    import yaml

    doc = yaml.safe_load(open(os.path.join(ROOT, ".github", "workflows", name)))
    steps = [s for job in doc["jobs"].values() for s in job["steps"]]
    export_at = next(i for i, s in enumerate(steps) if "scripts/app_export.py" in (s.get("run") or ""))
    publish_at = next(i for i, s in enumerate(steps) if "publish_handicap_report.py" in (s.get("run") or ""))
    assert export_at < publish_at
    assert steps[export_at].get("continue-on-error") is True, "a failed export must not block the report publish"
    assert "--app-src" in steps[publish_at]["run"]
    fail = next(s for s in steps if "app_export.outcome == 'failure'" in str(s.get("if")))
    assert "exit 1" in fail["run"]
    assert "--handicap-root" in steps[export_at]["run"] and "git archive origin/handicap-data" in steps[export_at]["run"]
    assert "git push" not in steps[export_at]["run"] and "worktree" not in steps[export_at]["run"]


# ------------------------------------------------------------------------------------------- 7. real data

def _real_roots():
    reports = os.environ.get("NFL_APP_EXPORT_REPORTS_DIR") or os.path.join(ROOT, "data", "handicap_report")
    hd = os.environ.get("NFL_APP_EXPORT_HANDICAP_ROOT")
    md = os.environ.get("NFL_APP_EXPORT_MARKET_DATA_ROOT")
    if not os.path.exists(os.path.join(reports, "analysis", "manifest.json")):
        pytest.skip("no RUN NFL report checked out: latest/ lives on the handicap-reports branch "
                    "(set NFL_APP_EXPORT_REPORTS_DIR to a `git archive origin/handicap-reports latest` extract)")
    if not hd or not os.path.isdir(os.path.join(hd, "data")):
        pytest.skip("no handicap-data checkout: set NFL_APP_EXPORT_HANDICAP_ROOT to a read-only extract of the branch")
    return reports, hd, md


def test_real_data_smoke(tmp_path):
    reports, hd, md = _real_roots()
    out = str(tmp_path / "app")
    extra = ["--market-data-root", md] if md else []
    assert app_export.main(["--reports-dir", reports, "--handicap-root", hd, "--out", out, *extra]) == 0
    assert publish.verify_published(out) == []
    man = _doc(out, "manifest")
    assert man["counts"]["events"] >= 1 and man["counts"]["markets"] >= 1 and man["counts"]["model_prices"] >= 1
    health = _doc(out, "health")
    assert health["bet_authority"] == "MANUAL" and health["payload_run_id"] == man["run_id"]
    wagers, settlements = _doc(out, "wagers")["items"], _doc(out, "settlements")["items"]
    by_id = {s["settlement_id"]: s for s in settlements}
    for w in wagers:
        if w["settlement_status"] == "SETTLED":
            assert w["settlement_id"] in by_id and w["profit_loss"] == by_id[w["settlement_id"]]["net_pnl"]
    for d, _, names in os.walk(out):
        for n in names:
            text = open(os.path.join(d, n), encoding="utf-8").read()
            assert not any(shape in text for shape in SECRET_SHAPES), n
