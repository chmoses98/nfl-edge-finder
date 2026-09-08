"""Both write paths are held to the same standard, or the stricter one is decoration.

There are exactly two ways a record reaches the immutable ledger, and one way a candidate reaches a HUMAN
before it ever becomes a record:

    scripts/handicap/preflight_candidate.py       the pre-trade check, BEFORE anything is shown as a bet
    scripts/handicap/sync_airtable.py             the unattended Airtable bridge
    scripts/handicap/validate_recommendations.py  the manual / engineering fallback

All three consume the same gates through the same assembly (`preflight.build_context`) and the same
cumulative portfolio arithmetic (`risk.report_for_batch`). The pre-trade path is where the check is USEFUL;
the other two are where it is RECORDED.

The bridge was hardened first. If the manual path had stayed permissive it would be a hole straight through
every protection the bridge applies -- documented in the runbook, reachable by anyone who read it, and
indistinguishable in the ledger from a properly gated write. These tests exist so the two paths cannot drift
apart again.

The property is not "the same code runs" -- it is "the same record is refused".
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nfl_edge.handicap import schema as S  # noqa: E402

SCRIPT = os.path.join(ROOT, "scripts", "handicap", "validate_recommendations.py")
NOW = datetime.now(timezone.utc)
KICKOFF = (NOW + timedelta(days=3)).isoformat()


def rec(**kw):
    d = dict(
        recommendation_id="rec_wp0000000000000001", schema_version=S.HANDICAP_SCHEMA_VERSION,
        created_at=NOW.isoformat(), handicap_run_id="20260907T160000Z", packet_sha="abc",
        season=2026, week=1, game_id="2026_01_NE_SEA", kickoff_utc=KICKOFF,
        market_ticker="KXNFLGAME-26SEP09NESEA-SEA", market_family="GAME_WINNER", side="YES",
        yes_bid=0.60, yes_ask=0.62, no_bid=0.36, no_ask=0.40, mid=0.61,
        market_timestamp=NOW.isoformat(), minutes_to_kickoff=4320.0,
        support_state=S.SUPPORT_SUPPORTED, model_version="shadow-0.4.0", artifact_hash="cafe",
        model_probability=0.64,
        probability_low=0.70, probability_mid=0.78, probability_high=0.86,
        decision=S.RECOMMENDED, grade="B", bet_up_to_probability=0.65,
        proposed_stake=10, recommended_stake=10, bankroll_snapshot=2000.0,
        primary_thesis="thesis", key_supporting_factors=["a"], counterarguments=["b"],
        uncertainties=["c"], source_freshness={"shadow_snapshot": NOW.isoformat()},
    )
    d.update(kw)
    return d


def run_cli(tmp_path, records, *extra):
    payload = tmp_path / "payload.json"
    payload.write_text(json.dumps(records))
    ledger = tmp_path / "ledger"
    ledger.mkdir(exist_ok=True)
    r = subprocess.run(
        [sys.executable, SCRIPT, str(payload), "--write", "--handicap-root", str(ledger), *extra],
        capture_output=True, text=True, cwd=ROOT)
    return r, ledger


def ledger_files(ledger, kind="recommendations"):
    base = ledger / "data" / kind
    if not base.exists():
        return []
    return sorted(p.name for p in base.rglob("*.json"))


def capture_tree(tmp_path, ask=0.62, minutes_ago=3.0, depth=100000.0):
    """A minimal but REAL capture tree, so the gate reads evidence rather than a stub.

    Timestamps are relative to NOW, which is also this fixture's `created_at`: the gates evaluate as of the
    decision, so a fixture whose capture sits before the decision by `minutes_ago` is what the gate sees.
    """
    when = NOW - timedelta(minutes=minutes_ago)
    rid = when.strftime("%Y%m%dT%H%M%SZ")
    day = tmp_path / "md" / "data" / "kalshi" / "capture" / when.strftime("%Y-%m-%d")
    day.mkdir(parents=True, exist_ok=True)
    (day / f"{rid}.manifest.json").write_text(json.dumps({
        "run_id": rid, "started_at": when.isoformat(), "finished_at": when.isoformat(),
        "series": {"KXNFLGAME": {"n": 40, "complete": True, "tier": "FULL",
                                 "observed_at": when.isoformat()}}, "partial": False}))
    (day / f"{rid}.quotes.jsonl").write_text(json.dumps({
        "ticker": "KXNFLGAME-26SEP09NESEA-SEA", "series_ticker": "KXNFLGAME",
        "observed_at": when.isoformat(), "status": "active",
        "yes_bid": 0.60, "yes_ask": ask, "no_bid": 1 - ask - 0.02, "no_ask": 0.40}) + "\n")
    (day / f"{rid}.books.jsonl").write_text(json.dumps({
        "run_id": rid, "observed_at": when.isoformat(), "ticker": "KXNFLGAME-26SEP09NESEA-SEA",
        "orderbook_fp": {"no_dollars": [[f"{1 - ask:.4f}", f"{depth}"]],
                         "yes_dollars": [["0.5000", "10"]]}}) + "\n")
    return str(tmp_path / "md")


# ---- the bypass this file exists to close ----------------------------------------------------------

def test_the_manual_writer_refuses_a_real_recommendation_without_market_data(tmp_path):
    """THE hole. Without this the runbook's fallback writes real bets with no gate at all."""
    r, ledger = run_cli(tmp_path, [rec()])
    assert r.returncode == 2, r.stdout + r.stderr
    assert "--market-data was not given" in r.stderr
    assert ledger_files(ledger) == [], "nothing may be written"


def test_the_manual_writer_accepts_a_gated_real_recommendation(tmp_path):
    md = capture_tree(tmp_path)
    r, ledger = run_cli(tmp_path, [rec()], "--market-data", md)
    assert r.returncode == 0, r.stdout + r.stderr
    assert ledger_files(ledger) == ["rec_wp0000000000000001.json"]


def test_the_manual_writer_records_the_gate_evidence_too(tmp_path):
    """Gate evidence lands beside the record it justifies, in the same commit, on both paths."""
    md = capture_tree(tmp_path)
    _r, ledger = run_cli(tmp_path, [rec()], "--market-data", md)
    gates = ledger_files(ledger, "decision_gates")
    assert len(gates) == 1
    body = json.loads((ledger / "data" / "decision_gates" / "2026" / "week_01" / gates[0]).read_text())
    assert body["overall"] == "PASS"
    assert body["decision_quote"]["executable_price"] == 0.62


# ---- the same refusals, on both paths --------------------------------------------------------------

def test_a_stale_price_is_refused_by_the_manual_writer_too(tmp_path):
    md = capture_tree(tmp_path, minutes_ago=45)
    r, ledger = run_cli(tmp_path, [rec()], "--market-data", md)
    assert r.returncode == 4, r.stdout + r.stderr
    assert ledger_files(ledger) == []


def test_a_live_ask_above_the_ceiling_is_refused_by_the_manual_writer_too(tmp_path):
    md = capture_tree(tmp_path, ask=0.80)
    r, ledger = run_cli(tmp_path, [rec()], "--market-data", md)
    assert r.returncode == 4
    assert ledger_files(ledger) == []


def test_an_oversized_stake_is_refused_by_the_manual_writer_too(tmp_path):
    """The risk policy binds on both paths or it binds on neither."""
    md = capture_tree(tmp_path)
    r, ledger = run_cli(tmp_path, [rec(proposed_stake=900, recommended_stake=900)], "--market-data", md)
    assert r.returncode == 4
    assert ledger_files(ledger) == []


def test_a_ceiling_below_the_recorded_ask_is_refused_before_any_gate_runs(tmp_path):
    """Structural. It does not need the world, so it must fail without --market-data too."""
    r, ledger = run_cli(tmp_path, [rec(bet_up_to_probability=0.50)])
    assert r.returncode == 1
    assert "NOT ACTIONABLE" in r.stdout
    assert ledger_files(ledger) == []


# ---- what is deliberately NOT gated ----------------------------------------------------------------

def test_a_pass_needs_no_market_data(tmp_path):
    """A PASS costs nothing, and a stale price is frequently the reason for it."""
    r, ledger = run_cli(tmp_path, [rec(decision=S.PASS, grade="PASS", bet_up_to_probability=None,
                                       recommended_stake=None, proposed_stake=None)])
    assert r.returncode == 0, r.stdout + r.stderr
    assert ledger_files(ledger) == ["rec_wp0000000000000001.json"]
    assert ledger_files(ledger, "decision_gates") == [], "a PASS generates no gate record"


def test_a_test_only_recommendation_needs_no_market_data(tmp_path):
    """The TEST_ONLY E2E must keep working without depending on a live market."""
    r, ledger = run_cli(tmp_path, [rec(test_only=True)], "--allow-test")
    assert r.returncode == 0, r.stdout + r.stderr
    assert ledger_files(ledger) == ["rec_wp0000000000000001.json"]


def test_a_test_only_record_still_needs_the_full_structural_record(tmp_path):
    """TEST_ONLY skips the world, never the schema. That is what the E2E is actually proving."""
    r, ledger = run_cli(tmp_path, [rec(test_only=True, packet_sha=None)], "--allow-test")
    assert r.returncode == 1
    assert "packet_sha" in r.stdout
    assert ledger_files(ledger) == []


# ---- immutability is not path-dependent ------------------------------------------------------------

def test_the_manual_writer_still_refuses_to_overwrite(tmp_path):
    md = capture_tree(tmp_path)
    r1, ledger = run_cli(tmp_path, [rec()], "--market-data", md)
    assert r1.returncode == 0
    before = (ledger / "data" / "recommendations" / "2026" / "week_01" /
              "rec_wp0000000000000001.json").read_text()

    payload = tmp_path / "payload.json"
    payload.write_text(json.dumps([rec(bet_up_to_probability=0.64, primary_thesis="revised")]))
    r2 = subprocess.run(
        [sys.executable, SCRIPT, str(payload), "--write", "--handicap-root", str(ledger),
         "--market-data", md], capture_output=True, text=True, cwd=ROOT)
    assert r2.returncode == 3, r2.stdout + r2.stderr
    after = (ledger / "data" / "recommendations" / "2026" / "week_01" /
             "rec_wp0000000000000001.json").read_text()
    assert before == after, "the original record was modified"


# ---- the paths agree about which fields are mandatory ----------------------------------------------

@pytest.mark.parametrize("missing", ["packet_sha", "market_timestamp", "support_state",
                                     "source_freshness", "probability_mid", "yes_ask"])
def test_every_required_field_is_required_on_the_manual_path_too(tmp_path, missing):
    r, ledger = run_cli(tmp_path, [rec(**{missing: None})])
    assert r.returncode == 1, f"{missing} was accepted"
    assert ledger_files(ledger) == []


# ---- the third path: pre-trade, before the ledger is involved at all --------------------------------

def test_the_pre_trade_path_refuses_the_same_records_the_writers_refuse(tmp_path):
    """Whatever the ledger would refuse, the owner must never have been shown as a bet in the first place.

    This is the property that makes the twelve-hour importer an AUDIT rather than the first line of defence.
    """
    from nfl_edge.handicap import preflight as P              # noqa: PLC0415

    md = capture_tree(tmp_path)
    ledger = tmp_path / "ledger3"
    ledger.mkdir(exist_ok=True)

    cases = [
        ("sound", rec(), True),
        ("stale price", rec(), False),
        ("thin book", rec(proposed_stake=100, recommended_stake=100), False),
        ("ask above the ceiling", rec(bet_up_to_probability=0.61, yes_ask=0.62), False),
    ]
    stale_md = capture_tree(tmp_path / "stale", minutes_ago=400.0)
    thin_md = capture_tree(tmp_path / "thin", depth=3.0)

    for i, (label, candidate, expect_bet) in enumerate(cases):
        market = {"stale price": stale_md, "thin book": thin_md}.get(label, md)
        try:
            result = P.preflight(candidate, market_data_root=market, ledger_root=str(ledger), root=ROOT,
                                 approval_as_of=NOW)
            got = result.may_be_shown_as_a_bet
        except S.ValidationError:
            got = False
        assert got is expect_bet, f"{label}: preflight said may_be_shown_as_a_bet={got}"

        payload = tmp_path / f"p_{i}.json"
        payload.write_text(json.dumps([candidate]))
        target = tmp_path / f"l4_{i}"
        target.mkdir(exist_ok=True)
        r = subprocess.run(
            [sys.executable, SCRIPT, str(payload), "--write", "--handicap-root", str(target),
             "--market-data", market],
            capture_output=True, text=True, cwd=ROOT)
        wrote = r.returncode == 0
        assert wrote is expect_bet, f"{label}: the writer and the pre-trade path disagree\n{r.stdout}"


def test_capping_is_an_answer_before_the_trade_and_a_refusal_after_it(tmp_path):
    """The one place the pre-trade path and the writer legitimately differ, and why.

    An oversized proposal is not a rejection before the trade: the risk policy's job is to say what size IS
    allowed, and telling the owner "$10, not $500" is the useful answer. At write time the same record is
    refused, because a filed recommendation must carry the size that was approved rather than the size that
    was wanted -- otherwise the ledger would record a bet nobody was allowed to take.

    The paths agree on the thing that matters: what preflight approves is exactly what the writer accepts.
    """
    from nfl_edge.handicap import preflight as P              # noqa: PLC0415

    md = capture_tree(tmp_path)
    ledger = tmp_path / "ledgerC"
    ledger.mkdir(exist_ok=True)
    oversized = rec(proposed_stake=500, recommended_stake=500)

    pre = P.preflight(oversized, market_data_root=md, ledger_root=str(ledger), root=ROOT,
                      approval_as_of=NOW)
    assert pre.may_be_shown_as_a_bet, "the pre-trade answer is a SIZE, not a refusal"
    assert pre.approved_stake == 10 and pre.proposed_stake == 500

    as_wanted = tmp_path / "wanted.json"
    as_wanted.write_text(json.dumps([oversized]))
    r = subprocess.run([sys.executable, SCRIPT, str(as_wanted), "--write",
                        "--handicap-root", str(tmp_path / "lw"), "--market-data", md],
                       capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 4, "the ledger refuses a record carrying the unapproved size"
    assert "does not match the stake the risk policy approved" in r.stdout + r.stderr

    as_approved = tmp_path / "approved.json"
    as_approved.write_text(json.dumps([dict(oversized, recommended_stake=pre.approved_stake)]))
    ok = subprocess.run([sys.executable, SCRIPT, str(as_approved), "--write",
                         "--handicap-root", str(tmp_path / "la"), "--market-data", md],
                        capture_output=True, text=True, cwd=ROOT)
    assert ok.returncode == 0, ok.stdout + ok.stderr


def test_the_pre_trade_cli_exits_five_on_a_blocked_candidate(tmp_path):
    """A blocked candidate is not an error in the pipeline. It has its own exit code so a caller can tell."""
    md = capture_tree(tmp_path, depth=2.0)
    ledger = tmp_path / "ledger5"
    ledger.mkdir(exist_ok=True)
    payload = tmp_path / "cand.json"
    payload.write_text(json.dumps([rec(proposed_stake=500, recommended_stake=500)]))
    cli = os.path.join(ROOT, "scripts", "handicap", "preflight_candidate.py")
    r = subprocess.run([sys.executable, cli, str(payload), "--market-data", md,
                        "--handicap-root", str(ledger)], capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 5, r.stdout + r.stderr
    assert "NOT A BET" in r.stdout
    assert "must NOT be surfaced as a bet" in r.stderr


def test_the_pre_trade_cli_approves_a_sound_candidate(tmp_path):
    md = capture_tree(tmp_path)
    ledger = tmp_path / "ledger6"
    ledger.mkdir(exist_ok=True)
    payload = tmp_path / "ok.json"
    payload.write_text(json.dumps([rec()]))
    cli = os.path.join(ROOT, "scripts", "handicap", "preflight_candidate.py")
    r = subprocess.run([sys.executable, cli, str(payload), "--market-data", md,
                        "--handicap-root", str(ledger)], capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.startswith("BET")
    assert "places nothing" in r.stdout


def test_the_pre_trade_cli_refuses_to_guess_at_a_missing_ledger(tmp_path):
    """Without the ledger the caps are not cumulative, and a non-cumulative cap is not a cap."""
    md = capture_tree(tmp_path)
    payload = tmp_path / "ok.json"
    payload.write_text(json.dumps([rec()]))
    cli = os.path.join(ROOT, "scripts", "handicap", "preflight_candidate.py")
    r = subprocess.run([sys.executable, cli, str(payload), "--market-data", md,
                        "--handicap-root", str(tmp_path / "nope")], capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 2
    assert "outstanding portfolio exposure" in r.stderr
