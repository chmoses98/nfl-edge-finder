"""Universal projection record: immutable, append-only, prospective-only, mid never executable."""
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.projection import ProjectionConflict, ProjectionRecord, ProjectionStore, read_projections, record_id  # noqa: E402
from nfl_edge.projection.record import PRICED, CAPTURE_ONLY, prospective_check  # noqa: E402
from nfl_edge.projection import horizons as H  # noqa: E402
from nfl_edge.projection.store import verify  # noqa: E402


def _rec(snapshot="20260913T150000Z", ticker="KXNFLTOTAL-26SEP13ATLPIT-48", p=0.55, state=PRICED, arm="GAME_MARKET_PRIOR", **kw):
    base = dict(record_id=record_id(snapshot, ticker, arm, "game-engine-2.0.0", "residual-bank-0.2.0"), snapshot_id=snapshot,
                ticker=ticker, model_arm=arm, engine="GAME", engine_version="game-engine-2.0.0", distribution_version="residual-bank-0.2.0",
                model_version="shadow-v2-0.1.0", market_family="TOTAL", period="FULL", game_id="2026_01_ATL_PIT",
                observed_at="2026-09-13T15:00:00+00:00", generated_at="2026-09-13T15:03:00+00:00", kickoff_utc="2026-09-13T17:00:00+00:00",
                yes_bid=0.50, yes_ask=0.53, no_bid=0.47, no_ask=0.50, p_yes=p, contract_value=p, support_state=state)
    base.update(kw)
    r = ProjectionRecord(**base)
    if state == CAPTURE_ONLY:
        r.p_yes = None; r.contract_value = None
    return r.finalize()


def test_record_derives_mid_as_research_only_and_hashes_content():
    r = _rec()
    assert r.mid == pytest.approx(0.515) and r.quote_width == pytest.approx(0.03)
    assert r.model_market_disagreement_mid == pytest.approx(0.55 - 0.515)
    assert r.yes_ask_disagreement == pytest.approx(0.55 - 0.53)
    assert r.content_hash and len(r.content_hash) == 20
    d = r.to_dict()
    assert "mid" in d and d["mid"] != d["yes_ask"], "the mid must never stand in for the executable ask"


def test_record_refuses_invalid_probability_or_state_mismatch():
    with pytest.raises(ValueError):
        _rec(p=1.2)
    with pytest.raises(ValueError):
        ProjectionRecord(record_id="x", snapshot_id="s", ticker="t", model_arm="a", engine="GAME", engine_version="e", distribution_version="d",
                         model_version="m", p_yes=0.4, support_state=CAPTURE_ONLY).finalize()
    with pytest.raises(ValueError):
        ProjectionRecord(record_id="x", snapshot_id="s", ticker="t", model_arm="a", engine="GAME", engine_version="e", distribution_version="d",
                         model_version="m", p_yes=None, support_state=PRICED).finalize()


def test_store_is_write_once_noop_and_conflict(tmp_path):
    st = ProjectionStore(str(tmp_path))
    rows = [_rec().to_dict(), _rec(ticker="KXNFLTOTAL-26SEP13ATLPIT-49", p=0.5).to_dict()]
    man = st.write("20260913T150000Z", "GAME_MARKET_PRIOR", rows)
    assert man["status"] == "WRITTEN" and man["n_rows"] == 2
    again = st.write("20260913T150000Z", "GAME_MARKET_PRIOR", [dict(r, generated_at="2026-09-13T15:09:00+00:00") for r in rows])
    assert again["status"] == "NO_OP"
    with pytest.raises(ProjectionConflict):
        st.write("20260913T150000Z", "GAME_MARKET_PRIOR", [_rec(p=0.56).to_dict(), rows[1]])
    assert verify(str(tmp_path))["ok"]
    got = read_projections(str(tmp_path))
    assert len(got) == 2 and {r["ticker"] for r in got} == {r["ticker"] for r in rows}


def test_store_rejects_tampered_hash(tmp_path):
    st = ProjectionStore(str(tmp_path))
    r = _rec().to_dict(); r["p_yes"] = 0.9
    with pytest.raises(ValueError):
        st.write("20260913T150000Z", "GAME_MARKET_PRIOR", [r])


def test_prospective_check_requires_both_timestamps_before_kickoff():
    ok, why = prospective_check(_rec())
    assert ok
    late = _rec(generated_at="2026-09-13T17:00:01+00:00")
    assert prospective_check(late)[0] is False
    late2 = _rec(observed_at="2026-09-13T17:00:00+00:00")
    assert prospective_check(late2)[0] is False


def test_horizon_labels_record_lateness_and_refuse_post_kickoff():
    ko = datetime(2026, 9, 13, 17, 0, tzinfo=timezone.utc)
    hid = "2026-REG-01|20260913T1700Z|T-90m"
    lab = H.label_snapshot(ko - timedelta(minutes=80), ko, hid)
    assert lab["horizon_label"] == "T-90m" and lab["horizon_target_min"] == 90.0 and lab["horizon_lateness_min"] == pytest.approx(10.0)
    cyc = H.label_snapshot(ko - timedelta(hours=5), ko, None)
    assert cyc["horizon_label"] == "CYCLE" and cyc["minutes_to_kickoff"] == pytest.approx(300.0)
    with pytest.raises(ValueError):
        H.label_snapshot(ko, ko, hid)


def test_missed_horizons_are_reported_never_reconstructed(tmp_path):
    ko = datetime(2026, 9, 13, 17, 0, tzinfo=timezone.utc)
    games = [{"game_id": "g1", "kickoff_utc": ko.isoformat()}]
    rep = H.missed_report("2026-REG-01", games, ko + timedelta(minutes=5), [])
    assert rep["n_missed"] == 4 and rep["n_captured"] == 0
    d = H.due("2026-REG-01", games, ko - timedelta(minutes=100), [])
    assert [r["horizon_min"] for r in d["due"]] == [360, 1440] and d["should_run"]
    paths = H.write_markers(str(tmp_path), [r["horizon_id"] for r in d["due"]], snapshot_id="s", status="WRITTEN", now=ko - timedelta(minutes=100))
    names = [os.path.basename(p) for p in paths]
    d2 = H.due("2026-REG-01", games, ko - timedelta(minutes=100), names)
    assert not d2["should_run"]
    # markers are append-only
    before = open(paths[0]).read()
    H.write_markers(str(tmp_path), [d["due"][0]["horizon_id"]], snapshot_id="other", status="WRITTEN")
    assert open(paths[0]).read() == before
