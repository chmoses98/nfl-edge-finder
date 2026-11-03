"""PR #232: the postmortem safeguards are WIRED into the real-money path (gates.py / preflight.py / card.py) and RUN NFL.

Everything here is offline: the card fixtures, a synthetic capture tree, no network, no wall clock.
Owner-approved scope: restriction-only guards, fee-inclusive ceiling check, $75-unit exposure FLAGS ($375/game, $1,125/day).
"""
import ast
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from card_fixtures import AS_OF, GAME, schedule_text, thesis
from nfl_edge.execution.fees import load_fee_schedule
from nfl_edge.handicap import card as C
from nfl_edge.handicap import gates as G
from nfl_edge.handicap import preflight as PF
from nfl_edge.postmortem import fairvalue as FV
from nfl_edge.postmortem import integration as PM

pytestmark = pytest.mark.owner_policy        # the card/entry-point tests use the REAL owner policy (same as tests/test_card.py)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "handicap", "run_card.py")
NOW = datetime(2026, 10, 25, 9, 0, tzinfo=timezone.utc)
KO = NOW + timedelta(hours=4)


# ------------------------------------------------------------------------------------------------ constants
def test_unit_and_flag_thresholds_are_the_owners_numbers():
    assert PM.UNIT_DOLLARS == 75.0 and C.UNIT == 75
    assert PM.GAME_FLAG_DOLLARS == 375.0 and PM.DAILY_FLAG_DOLLARS == 1125.0


def test_an_individual_bet_is_capped_at_5u_which_is_375_dollars_by_the_owner_policy():
    """Owner 2026-11-02: 1U = $75, maximum 5U per individual bet. The cap already lives in the owner risk policy (risk.py clamps to it and
    discloses the clamp); this pins it so a policy edit cannot silently raise it. Combined exposure above 5U/game or 15U/day is only FLAGGED."""
    pol = json.load(open(os.path.join(ROOT, "config", "risk_policy.json")))
    assert pol["max_stake_per_position_units"] == 5 and pol["fixed_unit_dollars"] == 75
    assert pol["max_stake_per_position_units"] * pol["fixed_unit_dollars"] == 375


# ------------------------------------------------------------------------------------------------ exposure flags
SF = [{"ticker": "KXNFLSPREAD-26OCT26SFATL-SF3", "side": "YES", "stake": 225.0, "game_id": "g1", "game_date": "2026-10-26"},
      {"ticker": "KXNFLSPREAD-26OCT26SFATL-SF7", "side": "YES", "stake": 175.0, "game_id": "g1", "game_date": "2026-10-26"}]


def test_two_sf_spread_rungs_are_one_thesis_flagged_at_5_33_units():
    out = PM.exposure_flags(SF, game_dates={"g1": "2026-10-26"})
    kinds = {f["kind"] for f in out["flags"]}
    assert {"GROUP_OVER_LIMIT", "GAME_OVER_LIMIT"} <= kinds
    game = next(f for f in out["flags"] if f["kind"] == "GAME_OVER_LIMIT")
    assert game["dollars"] == 400.0 and round(game["units"], 2) == 5.33 and game["limit_dollars"] == 375.0
    assert "no cap" in out["policy_note"]


@pytest.mark.parametrize("dollars,flagged", [(375.0, False), (375.01, True), (150.0, False)])
def test_game_flag_is_strictly_above_375(dollars, flagged):
    out = PM.exposure_flags([{"ticker": "KXNFLTOTAL-26OCT26SFATL-45", "side": "YES", "stake": dollars, "game_id": "g1", "game_date": "2026-10-26"}],
                            game_dates={"g1": "2026-10-26"})
    assert any(f["kind"] == "GAME_OVER_LIMIT" for f in out["flags"]) is flagged


@pytest.mark.parametrize("per_game,flagged", [(375.0, False), (376.0, True)])
def test_daily_flag_is_strictly_above_1125_and_open_exposure_counts(per_game, flagged):
    pos = [{"ticker": f"KXNFLTOTAL-26OCT26AA{c}BB{c}-45", "side": "YES", "stake": 375.0, "game_id": f"g{i}", "game_date": "2026-10-26"} for i, c in enumerate("ABC")]
    open_units = {"g9": (per_game - 375.0) / 75.0} if per_game > 375 else {}
    dates = {p["game_id"]: "2026-10-26" for p in pos} | {"g9": "2026-10-26"}
    out = PM.exposure_flags(pos, open_units_by_game=open_units, game_dates=dates)
    assert out["per_day_units"]["2026-10-26"] == pytest.approx(15.0 + (per_game - 375.0) / 75.0, abs=1e-3)
    assert any(f["kind"] == "DAY_OVER_LIMIT" for f in out["flags"]) is flagged


def test_open_exposure_on_an_undated_game_is_reported_not_added_to_a_day():
    out = PM.exposure_flags([], open_units_by_game={"gX": 20.0}, game_dates={})
    assert out["per_day_units"] == {} and out["undated_units_not_in_daily_totals"] == 20.0
    assert any(f["kind"] == "GAME_OVER_LIMIT" for f in out["flags"]) and not any(f["kind"] == "DAY_OVER_LIMIT" for f in out["flags"])


def test_flags_never_change_a_stake():
    before = [dict(p) for p in SF]
    PM.exposure_flags(SF, game_dates={"g1": "2026-10-26"})
    assert SF == before


# ------------------------------------------------------------------------------------------------ PIT gate (unit)
def _rec(**over):
    pit = {"projection_as_of": (NOW - timedelta(minutes=10)).isoformat(), "injuries_as_of": (NOW - timedelta(minutes=10)).isoformat(),
           "qb": {t: {"status": "CONFIRMED_STARTER", "confirmed_at": (NOW - timedelta(minutes=20)).isoformat(), "source": "HEAD_COACH_STATEMENT_ON_RECORD"} for t in ("AAA", "BBB")},
           "teams": ["BBB", "AAA"]}
    pit.update(over.pop("pit", {}))
    rec = {"market_ticker": "KXNFLSPREAD-26OCT25AAABBB-BBB3", "side": "YES", "kickoff_utc": KO.isoformat(), "pit_evidence": pit}
    rec.update(over)
    return rec


DQ = SimpleNamespace(is_actionable=True, executable_price=0.5, confirmed_at=(NOW - timedelta(minutes=2)).isoformat())
DR = SimpleNamespace(is_executable=True, contracts_required=150)


def test_clean_evidence_passes():
    st, why, ev = PM.pit_gate(_rec(), dq=DQ, dr=DR, as_of=NOW)
    assert st == "PASS", (why, ev)


@pytest.mark.parametrize("over,code", [
    ({"pit": {"projection_as_of": (NOW - timedelta(minutes=181)).isoformat()}}, "STALE_PROJECTION"),
    ({"pit": {"projection_as_of": None}}, "MISSING_PROJECTION_AS_OF"),
    ({"pit": {"injuries_as_of": (NOW - timedelta(minutes=181)).isoformat()}}, "STALE_INJURIES"),
    ({"pit": {"injuries_as_of": None}}, "MISSING_INJURY_SNAPSHOT"),
    ({"pit": {"qb": {}}}, "QB_UNKNOWN:AAA"),
    ({"pit": {"qb": {"AAA": {"status": "ACTIVE_DEPTH_CHART"}, "BBB": {"status": "CONFIRMED_STARTER", "confirmed_at": (NOW - timedelta(minutes=5)).isoformat()}}}}, "QB_NOT_CONFIRMED:AAA"),
    ({"pit": {"qb": {t: {"status": "CONFIRMED_STARTER", "confirmed_at": (NOW + timedelta(minutes=5)).isoformat()} for t in ("AAA", "BBB")}}}, "QB_CONFIRMED_AFTER_DECISION:AAA"),
    ({"kickoff_utc": (NOW - timedelta(minutes=1)).isoformat()}, "AFTER_KICKOFF"),
    ({"kickoff_utc": None}, "MISSING_KICKOFF"),
])
def test_each_pit_failure_blocks_with_its_own_reason(over, code):
    st, why, ev = PM.pit_gate(_rec(**over), dq=DQ, dr=DR, as_of=NOW)
    assert st == "FAIL" and code in ev["blocks"], (why, ev)


def test_a_missing_or_unactionable_executable_quote_is_a_provenance_failure_not_a_pass():
    st, _, ev = PM.pit_gate(_rec(), dq=None, dr=None, as_of=NOW)
    assert st == "FAIL" and "NO_EXECUTABLE_QUOTE_FOR_PROVENANCE" in ev["blocks"]
    dq = SimpleNamespace(is_actionable=False, executable_price=0.5, confirmed_at=None)
    assert PM.pit_gate(_rec(), dq=dq, dr=DR, as_of=NOW)[0] == "FAIL"


def test_a_stale_executable_quote_is_blocked():
    dq = SimpleNamespace(is_actionable=True, executable_price=0.5, confirmed_at=(NOW - timedelta(minutes=16)).isoformat())
    st, _, ev = PM.pit_gate(_rec(), dq=dq, dr=DR, as_of=NOW)
    assert st == "FAIL" and "STALE_QUOTE" in ev["blocks"]


# ------------------------------------------------------------------------------------------------ ceiling gate (unit)
@pytest.fixture(scope="module")
def schedule():
    return load_fee_schedule(ROOT)


def _crec(**over):
    r = {"probability_low": 0.58, "probability_high": 0.66, "recommended_stake": 150.0, "bet_up_to_probability": 0.50}
    r.update(over)
    return r


def test_ceiling_within_the_whole_order_bound_passes(schedule):
    st, why, ev = PM.ceiling_gate(_crec(), fee_schedule=schedule, series="KXNFLSPREAD", as_of=NOW)
    assert st == "PASS", (why, ev)
    assert ev["basis"] == "ANALYST_DECLARED_UNCALIBRATED" and ev["calibrated"] is False and ev["calibrated_bet_up_to_cents"] is None


def test_a_ceiling_above_the_fee_inclusive_bound_fails_and_is_never_raised(schedule):
    st, why, ev = PM.ceiling_gate(_crec(bet_up_to_probability=0.58), fee_schedule=schedule, series="KXNFLSPREAD", as_of=NOW)
    assert st == "FAIL" and ev["order_size_bound_cents"] < 58 and "never raised" in why


@pytest.mark.parametrize("missing", ["probability_low", "probability_high", "recommended_stake", "bet_up_to_probability"])
def test_missing_inputs_make_the_check_unavailable_and_invent_nothing(schedule, missing):
    st, _, ev = PM.ceiling_gate(_crec(**{missing: None}), fee_schedule=schedule, series="KXNFLSPREAD", as_of=NOW)
    assert st == "UNAVAILABLE" and "order_size_bound_cents" not in ev


def test_unknown_fee_schedule_is_unavailable_never_zero_fee():
    st, why, ev = PM.ceiling_gate(_crec(), fee_schedule=None, series="KXNFLSPREAD", as_of=NOW)
    assert st == "UNAVAILABLE" and "never zero" in why and "order_size_bound_cents" not in ev


def test_no_calibrated_bet_up_to_exists_without_calibration_evidence():
    fair = FV.fair_probability(0.6, None)
    out = FV.bet_up_to(fair, 150.0, lambda p, c: 1.0)
    assert out["bet_up_to_cents"] is None and "MISSING_CALIBRATION" in out["flags"]


# ------------------------------------------------------------------------------------------------ gate wiring + history
def _bare_ctx():
    return G.GateContext()


def test_records_without_pit_evidence_are_not_rejudged():
    rec = {"decision": "RECOMMENDED", "created_at": NOW.isoformat(), "market_ticker": "KXNFLSPREAD-26OCT25AAABBB-BBB3", "market_family": "SPREAD", "side": "YES",
           "kickoff_utc": KO.isoformat()}
    rep = G.evaluate_gates(rec, _bare_ctx())
    assert rep.gates[G.G_PIT].status == G.NOT_APPLICABLE and rep.gates[G.G_ORDER_CEILING].status == G.NOT_APPLICABLE


def test_records_with_pit_evidence_are_judged_and_fail_closed_with_nothing_supplied():
    rec = {"decision": "RECOMMENDED", "created_at": NOW.isoformat(), "market_ticker": "KXNFLSPREAD-26OCT25AAABBB-BBB3", "market_family": "SPREAD", "side": "YES",
           "kickoff_utc": KO.isoformat(), "pit_evidence": {"teams": ["BBB", "AAA"], "qb": {}}}
    rep = G.evaluate_gates(rec, _bare_ctx())
    assert rep.gates[G.G_PIT].status == G.FAIL and rep.gates[G.G_ORDER_CEILING].status == G.UNAVAILABLE and rep.overall == G.FAIL


def test_player_markets_keep_their_own_availability_gate():
    # 2026-11-03 (PR #241): the fixture is a RUSHING prop. A receiving-yards prop is QB_INDIRECT in the QB-dependency table and IS now judged by
    # G_PIT on its own team's quarterback (tests/test_qb_dependency.py); props that do not depend on the quarterback keep only their own gate.
    rec = {"decision": "RECOMMENDED", "created_at": NOW.isoformat(), "market_ticker": "KXNFLRSHYDS-26OCT25AAABBB-AAARB1-60", "market_family": "PLAYER_STAT",
           "side": "YES", "kickoff_utc": KO.isoformat(), "pit_evidence": {"teams": ["BBB", "AAA"], "qb": {}}}
    rep = G.evaluate_gates(rec, _bare_ctx())
    assert rep.gates[G.G_PIT].status == G.NOT_APPLICABLE


# ------------------------------------------------------------------------------------------------ the card + RUN NFL entry point
def _live_inputs(tmp_path):
    """A real capture tree for the card's chosen line (same construction test_card uses) plus a bankroll file."""
    import test_card as T
    first = T.run(tmp_path / "a", [thesis()], mode=C.LIVE)
    ln = first["lines"][0]
    row = next(r for r in json.load(open(tmp_path / "a" / "analysis" / "games" / f"{GAME}.json"))["rows"] if r["ticker"] == ln["ticker"])
    md = T._capture_for(tmp_path, row, ln["side"])
    ledger = tmp_path / "ledger"
    (ledger / "data").mkdir(parents=True)
    from nfl_edge.handicap import bankroll as BK
    bk = tmp_path / "bankroll.json"
    bk.write_text(json.dumps({"bankroll": 5000, "observedAt": (AS_OF - timedelta(minutes=5)).isoformat(), "valueType": BK.VALUE_TYPE}))
    (tmp_path / "theses.json").write_text(json.dumps([thesis()]))
    (tmp_path / "schedule.csv").write_text(schedule_text())
    return md, str(ledger), str(bk)


def _run_entry_point(tmp_path, name, *extra):
    sys.path.insert(0, os.path.join(ROOT, "scripts", "handicap"))
    import importlib
    rc = importlib.import_module("run_card")
    md, ledger, bk = _live_inputs(tmp_path) if not (tmp_path / "theses.json").exists() else (str(tmp_path / "md"), str(tmp_path / "ledger"), str(tmp_path / "bankroll.json"))
    out = tmp_path / name
    code = rc.main(["--reports-dir", str(tmp_path / "a"), "--theses", str(tmp_path / "theses.json"), "--allow-unreviewed", "--schedule-csv", str(tmp_path / "schedule.csv"),
                    "--handicap-root", ledger, "--market-data", md, "--bankroll-file", bk, "--mode", "LIVE", "--as-of", AS_OF.isoformat(), "--out", str(out), *extra])
    assert code in (0, None)
    return json.load(open(out / "card.json")), (out / "CARD.md").read_text()


def test_run_nfl_entry_point_with_confirmed_qbs_is_still_a_bet_and_carries_the_new_evidence(tmp_path):
    from card_fixtures import qb_records
    from nfl_edge.postmortem import qb_confirmations as QBC
    qb = tmp_path / "qb.json"
    qb.write_text(json.dumps({"schema": QBC.SCHEMA, "records": qb_records(AS_OF, minutes_before_cap=6)}))
    _live_inputs(tmp_path)
    card, md = _run_entry_point(tmp_path, "out_ok", "--qb-confirmations", str(qb))
    line = card["lines"][0]
    assert line["status"] == "BET (preflight approved)", line["preflight"]["blocking_reasons"]
    gates = line["preflight"]["gates"]
    assert gates[G.G_PIT]["status"] == "PASS" and gates[G.G_ORDER_CEILING]["status"] == "PASS"
    assert card["exposure_flags"]["unit_dollars"] == 75.0 and card["exposure_flags"]["game_flag_dollars"] == 375.0
    rec = json.load(open(tmp_path / "out_ok" / "records" / f"{line['recommendation_id']}.json"))
    pit = rec["pit_evidence"]
    assert pit["bet_up_to_provenance"]["calibrated_bet_up_to_cents"] is None and pit["bet_up_to_provenance"]["ceiling_is_calibrated"] is False
    kn = pit["key_number_distribution"]
    assert kn["used_by_card"] is False and kn["provenance"]["calibrated_on_seasons"] == [2022, 2023] and kn["provenance"]["tested_on_seasons"] == [2024, 2025]
    assert "CLOSING_LINE" in kn["provenance"]["centre"]


def test_run_nfl_entry_point_without_qb_confirmations_blocks_game_level_lines_fail_closed(tmp_path):
    _live_inputs(tmp_path)
    card, md = _run_entry_point(tmp_path, "out_noqb")
    line = card["lines"][0]
    assert line["status"] == "BLOCKED" and line["preflight"]["verdict"] == "BLOCKED"
    assert any(r.startswith("game_level_pit_evidence") and "QB_UNKNOWN" in r for r in line["preflight"]["blocking_reasons"]), line["preflight"]["blocking_reasons"]
    assert "Candidates BLOCKED by preflight" in md


def test_a_depth_chart_is_never_relabelled_as_a_confirmation():
    game = {"home_team": "BBB", "away_team": "AAA", "data_freshness": {"ledger_feature_cutoff": NOW.isoformat(), "context_capture": NOW.strftime("%Y%m%dT%H%M%SZ")},
            "quarterbacks": {"AAA": [{"player": "A QB", "status": "Active", "injury_status": None}], "BBB": [{"player": "B QB", "status": "Active", "injury_status": None}]}}
    pit = PM.build_pit_evidence(run={}, game=game, ev={"fair_basis": "x"})
    assert pit["qb"] == {} and pit["injuries_as_of"] == NOW.isoformat() and pit["projection_as_of"] == NOW.isoformat()


def test_public_redaction_withholds_exposure_amounts():
    xf = PM.exposure_flags(SF, open_units_by_game={"g1": 3.0}, game_dates={"g1": "2026-10-26"})
    card = {"mode": "LIVE", "owner_open_exposure": {"state": "OK", "by_game": {"g1": 225.0}}, "exposure_flags": xf, "theses": [], "portfolio": None}
    pub = C.redact_public(card)
    shown = pub["exposure_flags"]
    assert all(set(f) == {"kind", "game", "day", "axis"} for f in shown["flags"])      # kind and location only: no units, no dollars
    assert not ({"per_game_units", "per_day_units", "groups"} & set(shown)) and shown["game_flag_dollars"] == 375.0 and shown["daily_flag_dollars"] == 1125.0
    assert {f["kind"] for f in pub["exposure_flags"]["flags"]} >= {"GAME_OVER_LIMIT"}


# ------------------------------------------------------------------------------------------------ key-number provenance
def test_the_real_money_path_does_not_consume_the_research_distribution():
    for rel in ("nfl_edge/handicap/card.py", "nfl_edge/handicap/gates.py", "nfl_edge/handicap/preflight.py", "nfl_edge/postmortem/integration.py"):
        tree = ast.parse(open(os.path.join(ROOT, rel)).read())
        mods = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module} | \
               {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        names = {a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) for a in n.names}
        assert not any(m.endswith(("postmortem.distributions", "postmortem.dist_eval")) for m in mods), rel
        assert not ({"distributions", "dist_eval"} & names), rel


# ------------------------------------------------------------------------------------------------ pin guard
# Every file whose behaviour the wired gates depend on, and which is NOT already in tests/test_incumbent_unchanged.SOURCE_PINS.
# Changing any of them without updating this table fails the suite: that is the "no unreviewed change" property.
WIRING_PINS = {
    "nfl_edge/handicap/card.py": "PIN_CARD",
    "nfl_edge/postmortem/integration.py": "PIN_INTEGRATION",
    "nfl_edge/postmortem/guards.py": "PIN_GUARDS",
    "nfl_edge/postmortem/fairvalue.py": "PIN_FAIRVALUE",
    "nfl_edge/postmortem/exposure.py": "PIN_EXPOSURE",
    "nfl_edge/postmortem/common.py": "PIN_COMMON",
    "nfl_edge/postmortem/ontology.py": "PIN_ONTOLOGY",
    "nfl_edge/postmortem/qb_confirmations.py": "PIN_QB_CONFIRMATIONS",
    "nfl_edge/postmortem/qb_dependency.py": "PIN_QB_DEPENDENCY",
}


def _sha16(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()[:16]


def test_wired_safeguard_sources_are_pinned_and_a_change_without_a_pin_update_fails():
    from wiring_pins import PINS      # tests/wiring_pins.py: the one place a reviewer updates these, in the same commit as the edit
    assert set(PINS) == set(WIRING_PINS)
    moved = {rel: _sha16(rel) for rel, pin in PINS.items() if _sha16(rel) != pin}
    assert not moved, f"wired safeguard source changed without a pin update: {moved}. Update tests/wiring_pins.py deliberately, with the reason."


# ------------------------------------------------------------------------------------------------ router ids tolerated when they appear
@pytest.mark.parametrize("extra", [{"order_id": "o1"}, {"kalshi_order_id": "o1"}, {"fill_ids": ["f1"]}, {"kalshi_fill_ids": ["f1", "f2"]}, {"fill_id": "f1"}])
def test_any_router_order_or_fill_id_clears_the_missing_flag(extra):
    from nfl_edge.postmortem import reconcile as R
    w = {"source_bet_key": "k1", "market_ticker": "KXNFLSPREAD-26OCT25SFATL-SF3", "side": "YES", "actual_price": 0.5, "contracts": 100, "stake": 51.75,
         "fees_paid": 1.75, "fees_are_estimated": False, "executed_at": "2026-10-25T15:04:44Z", "game_date": "2026-10-25", **extra}
    base = {k: v for k, v in w.items() if k not in extra}
    assert "MISSING_ORDER_FILL_DETAIL" in R.reconcile([base], [], [])[0].flags
    assert "MISSING_ORDER_FILL_DETAIL" not in R.reconcile([w], [], [])[0].flags
    assert R.ORDER_FILL_KEYS and all(k in R.ORDER_FILL_KEYS for k in extra)


def test_empty_id_lists_do_not_count_as_ids():
    from nfl_edge.postmortem import reconcile as R
    w = {"source_bet_key": "k1", "market_ticker": "KXNFLSPREAD-26OCT25SFATL-SF3", "side": "YES", "actual_price": 0.5, "contracts": 100, "stake": 51.75,
         "fees_paid": 1.75, "executed_at": "2026-10-25T15:04:44Z", "game_date": "2026-10-25", "kalshi_fill_ids": [], "kalshi_order_id": None}
    assert "MISSING_ORDER_FILL_DETAIL" in R.reconcile([w], [], [])[0].flags
