"""Decision-time evidence digests, the join to the router's execution rows, and the QB source probe (reports only)."""
import importlib.util
import json
import os
import re

import pytest

from card_fixtures import AS_OF, qb_records
from nfl_edge.postmortem import decision_evidence as DE
from test_postmortem_wiring import _live_inputs, _run_entry_point

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HEX32 = re.compile(r"^[0-9a-f]{32}$")

pytestmark = pytest.mark.owner_policy


def _rec(**kw):
    base = {"decision": "RECOMMENDED", "recommendation_id": "rec_abc", "market_ticker": "KXNFLSPREAD-X", "side": "YES",
            "created_at": "2026-11-03T15:00:00+00:00", "handicap_run_id": "run1", "packet_sha": "sha1",
            "source_freshness": {"ledger_feature_cutoff": "2026-11-03T14:00:00+00:00"}}
    base.update(kw)
    return base


# ----------------------------------------------------------------------------------------------------- digests
def test_digests_are_domain_separated_deterministic_and_32_hex():
    a = DE.ref_digest("recommendation", "x")
    assert HEX32.match(a) and a == DE.ref_digest("recommendation", "x")
    assert a != DE.ref_digest("model_run", "x")                      # same value, different domain
    with pytest.raises(ValueError):
        DE.ref_digest("order", "x")


def test_a_candidate_carries_digests_and_no_raw_id():
    c = DE.candidates_from_records([_rec()])["candidates"][0]
    assert HEX32.match(c["recommendation_ref"]) and HEX32.match(c["model_run_ref"])
    assert "rec_abc" not in json.dumps(c) and "run1" not in json.dumps(c)
    assert c["model_as_of"].startswith("2026-11-03T14:00:00")


@pytest.mark.parametrize("override,reason", [
    ({"decision": "PASS"}, "NOT_A_RECOMMENDATION"),
    ({"market_ticker": None}, "MISSING_MARKET_TICKER"),
    ({"side": ""}, "MISSING_SIDE"),
    ({"created_at": "garbled"}, "MISSING_CREATED_AT"),
    ({"source_freshness": {}}, "MISSING_MODEL_AS_OF"),
    ({"handicap_run_id": None, "packet_sha": None}, "MISSING_MODEL_RUN_ID"),
])
def test_an_incomplete_record_is_skipped_with_a_reason_never_completed(override, reason):
    out = DE.candidates_from_records([_rec(**override)])
    assert out["candidates"] == [] and out["skipped"] == {reason: 1}


def test_writing_is_append_only_and_idempotent(tmp_path):
    p = str(tmp_path / "c.jsonl")
    cands = DE.candidates_from_records([_rec(), _rec(recommendation_id="rec_def", market_ticker="KXNFLTOTAL-Y")])["candidates"]
    assert DE.write_candidates(p, cands[:1]) == {"written": 1, "already_present": 0}
    before = open(p).read()
    assert DE.write_candidates(p, cands) == {"written": 1, "already_present": 1}
    assert open(p).read().startswith(before)                          # the first line is untouched
    assert DE.write_candidates(p, cands) == {"written": 0, "already_present": 2}
    assert len(DE.read_candidates(p)) == 2


# ------------------------------------------------------------------------------------------------- the join
def _exec(first_fill_ts, ticker="KXNFLSPREAD-X", side="YES"):
    return {"source_bet_key": "kalshi:v1:" + "a" * 64, "first_fill_ts": first_fill_ts, "market_ticker": ticker, "side": side}


def _cands(*recs):
    return DE.candidates_from_records(list(recs))["candidates"]


def test_exact_unique_match_links():
    c = _cands(_rec())
    ts = c[0]["created_at_ts"] + 600
    row = DE.link_executions([_exec(ts)], c)[0]
    assert row["status"] == "LINKED" and row["recommendation_ref"] == c[0]["recommendation_ref"]


def test_two_distinct_recommendations_are_ambiguous_not_resolved_by_picking_the_nearest():
    c = _cands(_rec(), _rec(recommendation_id="rec_other", created_at="2026-11-03T15:05:00+00:00"))
    row = DE.link_executions([_exec(c[0]["created_at_ts"] + 900)], c)[0]
    assert row["status"] == "AMBIGUOUS" and "recommendation_ref" not in row


def test_wrong_side_wrong_market_after_the_fill_or_outside_the_window_is_missing():
    c = _cands(_rec())
    t0 = c[0]["created_at_ts"]
    assert DE.link_executions([_exec(t0 + 60, side="NO")], c)[0]["status"] == "MISSING"
    assert DE.link_executions([_exec(t0 + 60, ticker="KXOTHER")], c)[0]["status"] == "MISSING"
    assert DE.link_executions([_exec(t0 - 60)], c)[0]["status"] == "MISSING"                    # fill BEFORE the recommendation
    assert DE.link_executions([_exec(t0 + DE.DEFAULT_LINK_WINDOW_SECONDS + 1)], c)[0]["status"] == "MISSING"


def test_a_non_positive_window_is_refused_there_is_no_hidden_default():
    with pytest.raises(ValueError):
        DE.link_executions([_exec(1.0)], [], window_seconds=0)


# ----------------------------------------------------------------------------- the real RUN NFL entry point
def test_run_card_writes_digest_only_decision_candidates_beside_the_card(tmp_path):
    from test_qb_replay_run_nfl import _file
    _live_inputs(tmp_path)
    card, _ = _run_entry_point(tmp_path, "out", "--qb-confirmations", _file(tmp_path, qb_records(AS_OF, minutes_before_cap=6)))
    assert card["lines"][0]["status"] == "BET (preflight approved)"
    out = tmp_path / "out"
    cands = DE.read_candidates(str(out / "decision_candidates.jsonl"))
    assert len(cands) == 1
    rid = [f[:-5] for f in os.listdir(out / "records")][0]
    assert cands[0]["recommendation_ref"] == DE.ref_digest("recommendation", rid)
    assert rid not in (out / "decision_candidates.jsonl").read_text()
    assert json.load(open(out / "decision_candidates_skipped.json")) == {}


# ---------------------------------------------------------------------------------------------- source probe
def _probe():
    spec = importlib.util.spec_from_file_location("qb_source_probe", os.path.join(ROOT, "scripts", "handicap", "qb_source_probe.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_probe_reports_candidate_paths_and_sets_depth_charts_and_inactives_aside():
    P = _probe()
    payload = {"athletes": [{"depthChart": {"starter": True}, "inactive": True, "name": "x"}],
               "game": {"startingLineup": [{"pos": "QB"}], "probables": []}}
    r = P.analyse("fake", payload, fetched_at="t")
    assert any(p.endswith("startingLineup") for p in r["starter_designation_candidates"])
    assert not any("depthChart" in p for p in r["starter_designation_candidates"])
    assert any("depthChart" in p for p in r["set_aside_paths"])
    assert r["verdict"] == "CANDIDATE_FIELDS_PRESENT_REVIEW_BY_A_HUMAN"


def test_probe_with_no_designation_field_says_so():
    r = _probe().analyse("fake", {"events": [{"id": "1", "name": "A at B"}]}, fetched_at="t")
    assert r["verdict"] == "NO_STARTER_DESIGNATION_FIELD" and r["starter_designation_candidates"] == []


def test_probe_never_raises_on_an_unreachable_source_and_never_writes_confirmations():
    P = _probe()

    def down(url, timeout=30):
        raise OSError("tunnel failed 403")
    rep = P.run(fetcher=down)
    assert rep["writes_confirmations"] is False
    assert all(r["answered"] is False for r in rep["results"])
    assert {r["reason"] for r in rep["results"]} <= {"OSError", "NO_EVENT_ID_FROM_SCOREBOARD"}


def test_probe_output_holds_key_paths_and_counts_only():
    P = _probe()
    secret = "SOME-PLAYER-NAME-OR-TEXT"
    r = P.analyse("fake", {"lineup": {"note": secret}}, fetched_at="t")
    assert secret not in json.dumps(r)
