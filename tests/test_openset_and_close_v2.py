"""Open-set evidence answers "was this contract open at this moment", and the close says why nothing came after.

The distinction these tests defend is the one that decides whether a close is real: a contract the exchange
pulled 38 minutes before kickoff has a legitimate close at its last live quote, while a contract missing because
its series fetch half-failed has no evidence at all. After the fact the two are identical in the quote files, so
the open set has to be recorded at capture time and it has to be replayable exactly.
"""
import gzip
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.evaluation import close as C                                       # noqa: E402
from nfl_edge.evaluation import openset as OS                                     # noqa: E402

T0 = datetime(2026, 9, 13, 9, 0, tzinfo=timezone.utc)
KICK = datetime(2026, 9, 13, 17, 0, tzinfo=timezone.utc)
SERIES = "KXNFLGAME"
TICK = "KXNFLGAME-26SEP13AB-A"


def run_id(i):
    return (T0 + timedelta(minutes=10 * i)).strftime("%Y%m%dT%H%M%SZ")


def run_at(i):
    return T0 + timedelta(minutes=10 * i)


class Capture:
    """A capture tree written the way scripts/kalshi/capture.py writes one."""

    def __init__(self, root):
        self.root = root
        self.day = os.path.join(root, "2026-09-13")
        os.makedirs(self.day, exist_ok=True)
        self.state = {"last_seen": {}}

    def run(self, i, open_tickers, *, series_complete=True, series=(SERIES,), quotes=None, polled=True):
        rid, obs = run_id(i), run_at(i)
        smap = {s: {"n": len(open_tickers), "complete": series_complete, "tier": "FULL_MICROSTRUCTURE",
                    "observed_at": obs.isoformat()} for s in (series if polled else ())}
        man = {"run_id": rid, "started_at": obs.isoformat(), "finished_at": obs.isoformat(), "series": smap,
               "partial": not series_complete, "schema_version": "capture-1.1.0"}
        man["openset"] = OS.record_open_set(self.day, rid, obs.isoformat(), open_tickers, self.state)
        for t in open_tickers:
            self.state["last_seen"][t] = rid
        json.dump(man, open(os.path.join(self.day, f"{rid}.manifest.json"), "w"))
        if quotes:
            with open(os.path.join(self.day, f"{rid}.quotes.jsonl"), "w") as fh:
                for q in quotes:
                    fh.write(json.dumps({"run_id": rid, "observed_at": obs.isoformat(), "series_ticker": SERIES,
                                         "game_id": "2026_01_A_B", "kickoff_utc": KICK.isoformat(), "status": "active",
                                         "yes_bid_dollars": "0.4000", "yes_ask_dollars": "0.4400",
                                         "no_bid_dollars": "0.5600", "no_ask_dollars": "0.6000",
                                         "close_time": (KICK + timedelta(hours=6)).isoformat().replace("+00:00", "Z"),
                                         **q}) + "\n")
        return rid


@pytest.fixture
def cap():
    with tempfile.TemporaryDirectory() as d:
        yield Capture(d)


# ---------------------------------------------------------------------------------- the ledger itself
def test_the_replayed_open_set_matches_the_hash_the_capture_recorded(cap):
    cap.run(0, ["A", "B", "C"])
    cap.run(1, ["A", "B", "C", "D"])
    cap.run(2, ["A", "D"])
    cap.run(3, ["A", "D", "E"])
    v = OS.OpenSetLedger(cap.root).verify()
    assert v["runs"] == 4 and v["verified"] == 4 and not v["mismatched"] and not v["chain_breaks"]


def test_a_ticker_open_only_in_the_middle_is_open_only_there(cap):
    cap.run(0, ["A"])
    cap.run(1, ["A", "B"])
    cap.run(2, ["A", "B"])
    cap.run(3, ["A"])
    led = OS.OpenSetLedger(cap.root)
    assert [led.open_at("B", run_id(i)) for i in range(4)] == [False, True, True, False]
    assert led.last_open_run("B") == run_id(2)


def test_deltas_stay_small_and_an_anchor_restates_the_whole_set(cap):
    cap.run(0, [f"T{i}" for i in range(50)])
    cap.run(1, [f"T{i}" for i in range(50)] + ["NEW"])
    first = json.load(open(os.path.join(cap.day, f"{run_id(0)}.openset.json")))
    second = json.load(open(os.path.join(cap.day, f"{run_id(1)}.openset.json")))
    assert first["full"] is not None and first["base_run_id"] == first["run_id"], "the first run must anchor"
    assert second["full"] is None and second["added"] == ["NEW"] and second["removed"] == []
    assert second["base_run_id"] == first["run_id"] and second["prev_run_id"] == first["run_id"]


def test_a_delta_bigger_than_half_the_set_re_anchors_instead(cap):
    cap.run(0, [f"T{i}" for i in range(10)])
    cap.run(1, [f"U{i}" for i in range(10)])
    second = json.load(open(os.path.join(cap.day, f"{run_id(1)}.openset.json")))
    assert second["full"] is not None and second["base_run_id"] == second["run_id"]


# ---------------------------------------------------------------------------------- the six presence states
def test_partial_series_fetch_is_never_read_as_a_delisting(cap):
    cap.run(0, [TICK])
    cap.run(1, [], series_complete=False)
    led = OS.OpenSetLedger(cap.root)
    p = led.presence(TICK, run_id(1), series_ticker=SERIES)
    assert p["state"] == OS.PARTIAL_FETCH and "absence is not evidence" in p["reason"]
    assert p["state"] not in OS.MARKET_STATES, "a capture failure is not a market event"


def test_an_unpolled_series_is_distinguished_from_a_delisting(cap):
    cap.run(0, [TICK])
    cap.run(1, [], polled=False)
    p = OS.OpenSetLedger(cap.root).presence(TICK, run_id(1), series_ticker=SERIES)
    assert p["state"] == OS.SERIES_NOT_POLLED


def test_a_contract_pulled_before_its_close_time_is_delisted(cap):
    cap.run(0, [TICK])
    cap.run(1, [])
    p = OS.OpenSetLedger(cap.root).presence(TICK, run_id(1), series_ticker=SERIES,
                                            close_time=(KICK + timedelta(hours=6)).isoformat())
    assert p["state"] == OS.DELISTED and "had not been reached" in p["reason"]


def test_absence_after_the_contracts_own_close_time_is_closed_not_delisted(cap):
    cap.run(0, [TICK])
    cap.run(1, [])
    p = OS.OpenSetLedger(cap.root).presence(TICK, run_id(1), series_ticker=SERIES,
                                            close_time=(T0 - timedelta(hours=1)).isoformat())
    assert p["state"] == OS.CLOSED


def test_a_run_with_no_open_set_record_is_unknown_not_absent(cap):
    cap.run(0, [TICK])
    led = OS.OpenSetLedger(cap.root)
    p = led.presence(TICK, "20990101T000000Z", series_ticker=SERIES)
    assert p["state"] == OS.UNKNOWN and led.open_at(TICK, "20990101T000000Z") is None


def test_a_relisted_contract_is_open_again_not_permanently_gone(cap):
    cap.run(0, [TICK])
    cap.run(1, [])
    cap.run(2, [TICK])
    led = OS.OpenSetLedger(cap.root)
    assert [led.open_at(TICK, run_id(i)) for i in range(3)] == [True, False, True]
    assert led.last_open_run(TICK) == run_id(2)
    assert led.verify()["verified"] == 3


# ---------------------------------------------------------------------------------- close hardening
def build_close(cap, **kw):
    led = OS.OpenSetLedger(cap.root)
    runs = C.CaptureRuns(cap.root)
    idx = C.CloseIndex(cap.root, "2026_01_A_B", KICK.isoformat(), runs=runs, days_back=30, openset=led)
    return idx.select(TICK, series_ticker=SERIES, **kw)


def test_a_contract_delisted_before_kickoff_still_has_a_close_and_says_so(cap):
    cap.run(0, [TICK], quotes=[{"ticker": TICK}])
    cap.run(1, [TICK])
    cap.run(2, [])                                   # pulled ~7h before kickoff
    cap.run(3, [])
    rec = build_close(cap)
    assert rec["close_status"] == "CLOSE_OK"
    assert "DELISTED_BEFORE_KICKOFF" in rec["flags"] and rec["absence_explained"] is True
    assert rec["close_disappearance"]["first_non_open"]["state"] == OS.DELISTED


def test_a_gap_caused_by_a_failed_series_fetch_is_flagged_as_unexplained(cap):
    cap.run(0, [TICK], quotes=[{"ticker": TICK}])
    cap.run(1, [], series_complete=False)
    cap.run(2, [], series_complete=False)
    rec = build_close(cap)
    assert rec["close_status"] == "CLOSE_OK", "the price row is real; only the absence after it is unproven"
    assert "ABSENCE_UNEXPLAINED" in rec["flags"] and rec["absence_explained"] is False


def test_a_contract_open_all_the_way_to_kickoff_has_no_disappearance_to_explain(cap):
    for i in range(4):
        cap.run(i, [TICK], quotes=[{"ticker": TICK}] if i == 0 else None)
    rec = build_close(cap)
    assert rec["close_disappearance"]["first_non_open"] is None
    assert rec["close_disappearance"]["still_open_at_last_run"] is True
    assert not ({"DELISTED_BEFORE_KICKOFF", "ABSENCE_UNEXPLAINED"} & set(rec["flags"]))
    assert rec["close_presence"]["state"] == OS.OPEN


def test_confirmation_never_stands_on_a_run_the_open_set_says_was_closed(cap):
    """The manifest says the series was fetched completely at run 3, but this ticker was not in it."""
    cap.run(0, [TICK], quotes=[{"ticker": TICK}])
    cap.run(1, [TICK])
    cap.run(2, [])
    cap.run(3, [])
    rec = build_close(cap)
    assert "CONFIRMATION_RETREATED" in rec["flags"]
    assert rec["close_source_snapshot"] == run_id(1), "the claim retreats to the last provably open run"
    assert rec["close_presence"]["state"] == OS.OPEN


def test_the_close_is_unchanged_when_no_open_set_evidence_exists(cap):
    """Captures written before open-set evidence existed must still produce exactly the close they did."""
    cap.run(0, [TICK], quotes=[{"ticker": TICK}])
    cap.run(1, [TICK])
    for p in os.listdir(cap.day):
        if p.endswith(".openset.json"):
            os.remove(os.path.join(cap.day, p))
    idx = C.CloseIndex(cap.root, "2026_01_A_B", KICK.isoformat(), days_back=30, openset=None)
    rec = idx.select(TICK, series_ticker=SERIES)
    assert rec["close_status"] == "CLOSE_OK" and rec["close_presence"]["state"] == OS.UNKNOWN
    assert rec["close_disappearance"] is None and rec["absence_explained"] is None


def test_the_rule_version_moved_so_old_and_new_closes_are_never_silently_compared():
    assert C.CLOSE_RULE_VERSION == "close-2.1.0" and OS.OPENSET_VERSION == "openset-1.0.0"


def test_the_writer_never_raises_into_the_capture(cap):
    """An unwritable directory must cost the run its open set and nothing else."""
    r = OS.record_open_set(os.path.join(cap.root, "does", "not", "exist"), run_id(9), T0.isoformat(), ["A"], {})
    assert r["written"] is False and "error" in r


def test_the_capture_calls_the_writer_before_it_folds_the_run_into_last_seen():
    """The previous open set is derived from `last_seen`, so the order of those two steps is the contract."""
    src = open(os.path.join(ROOT, "scripts", "kalshi", "capture.py")).read()
    i_write = src.index("OS.record_open_set(")
    i_fold = src.index('state["last_seen"][tk] = run_id')
    assert i_write < i_fold, "recording the open set after last_seen is updated would diff the run against itself"
