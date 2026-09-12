"""A future source must not change an earlier frozen projection.

Every test here plants evidence on disk that post-dates the cutoff AND would materially change the answer if it
were selected. That second half matters: a test where the future file happens to carry the same value proves
nothing. The audit found four unbounded loaders next to four correctly bounded ones, so the rule is tested per
source rather than trusted once.
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

from nfl_edge.evaluation import execution_depth as XD                          # noqa: E402
from nfl_edge.settlement import reachability as RE                             # noqa: E402
from nfl_edge.shadow_v2 import capture_io as CIO                               # noqa: E402
from nfl_edge.shadow_v2 import pit                                             # noqa: E402

T0 = datetime(2026, 9, 13, 12, 0, tzinfo=timezone.utc)
CUTOFF = datetime(2026, 9, 13, 14, 0, tzinfo=timezone.utc)
FUTURE = datetime(2026, 9, 13, 16, 0, tzinfo=timezone.utc)
KICK = datetime(2026, 9, 13, 17, 0, tzinfo=timezone.utc)


def rid(dt):
    return dt.strftime("%Y%m%dT%H%M%SZ")


# ---------------------------------------------------------------------------------------------- the primitive
def test_selection_takes_the_newest_evidence_at_or_before_the_cutoff_not_the_newest():
    paths = [f"/x/{rid(T0)}.a.json", f"/x/{rid(CUTOFF)}.a.json", f"/x/{rid(FUTURE)}.a.json"]
    got, v = pit.pick_at_or_before(paths, CUTOFF)
    assert got.endswith(f"{rid(CUTOFF)}.a.json") and v == CUTOFF
    assert pit.pick_at_or_before(paths, T0)[0].endswith(f"{rid(T0)}.a.json")
    assert pit.pick_at_or_before([paths[-1]], CUTOFF) == (None, None), "only-future evidence selects nothing"


def test_a_row_without_an_observation_instant_is_refused_not_admitted():
    assert pit.row_at_or_before({"observed_at": None}, CUTOFF) is False
    assert pit.row_at_or_before({}, CUTOFF) is False
    assert pit.row_at_or_before({"observed_at": T0.isoformat()}, CUTOFF) is True


def test_pregame_is_judged_on_the_rows_own_instant_never_on_its_filename():
    assert pit.strictly_before_kickoff({"observed_at": (KICK - timedelta(minutes=1)).isoformat()}, KICK)
    assert not pit.strictly_before_kickoff({"observed_at": KICK.isoformat()}, KICK), "exactly at kickoff is not pregame"
    assert not pit.strictly_before_kickoff({"observed_at": (KICK + timedelta(minutes=1)).isoformat()}, KICK)


# ---------------------------------------------------------------------------------------------- the ledger
def test_a_source_dated_after_the_run_itself_fails_closed():
    led = pit.VintageLedger(CUTOFF)
    led.record("injuries", FUTURE, kind="nflverse")
    with pytest.raises(pit.PointInTimeViolation):
        led.assert_not_from_the_future(CUTOFF)
    led2 = pit.VintageLedger(CUTOFF)
    led2.record("injuries", T0, kind="nflverse")
    led2.assert_not_from_the_future(CUTOFF)


def test_skew_short_of_kickoff_is_recorded_but_an_outcome_leak_is_refused():
    """The distinction the whole contract rests on: a later fetch is normal, a post-kickoff fetch is fiction."""
    led = pit.VintageLedger(CUTOFF)
    led.record("injuries", CUTOFF + timedelta(minutes=37), kind="nflverse")   # normal operation
    assert led.skews()[0]["skew_seconds"] == pytest.approx(2220.0)
    assert led.outcome_leak(KICK) == [], "a source before kickoff is not an outcome leak"
    led.record("results", KICK + timedelta(hours=3), kind="nflverse")         # post-game
    leak = led.outcome_leak(KICK)
    assert len(leak) == 1 and leak[0]["name"] == "results"


def test_a_static_source_must_declare_why_it_is_safe_and_never_counts_as_a_leak():
    led = pit.VintageLedger(CUTOFF)
    led.record_static("divisions", "the eight divisions cannot encode a game outcome")
    assert led.outcome_leak(KICK) == [] and led.skews() == []
    assert led.to_block()["sources"][0]["static_reason"]


# ---------------------------------------------------------------------------------------------- quotes / books
def write_capture(root, run_dt, *, tickers, finished=None, kind="quotes", extra=None):
    day = os.path.join(root, run_dt.strftime("%Y-%m-%d"))
    os.makedirs(day, exist_ok=True)
    r = rid(run_dt)
    fin = (finished or run_dt).isoformat()
    json.dump({"run_id": r, "finished_at": fin, "series": {"S": {"complete": True, "tier": "FULL_MICROSTRUCTURE",
                                                                 "observed_at": fin}}},
              open(os.path.join(day, f"{r}.manifest.json"), "w"))
    with open(os.path.join(day, f"{r}.{kind}.jsonl"), "w") as fh:
        for t, payload in tickers.items():
            fh.write(json.dumps({"run_id": r, "observed_at": (extra or {}).get("observed_at", fin),
                                 "ticker": t, "series_ticker": "S", **payload}) + "\n")
    return r


@pytest.fixture
def cap():
    with tempfile.TemporaryDirectory() as d:
        yield d


def test_a_quote_row_from_a_later_run_never_reaches_an_earlier_snapshot(cap):
    write_capture(cap, CUTOFF, tickers={"T": {"yes_bid_dollars": "0.40", "yes_ask_dollars": "0.44"}})
    write_capture(cap, FUTURE, tickers={"T": {"yes_bid_dollars": "0.90", "yes_ask_dollars": "0.94"}})
    q, run_ts, _ages, _c, _m = CIO.load_latest_quotes(cap, snapshot_id=rid(CUTOFF))
    assert q["T"]["yes_bid_dollars"] == "0.40", "the future run's price must not win"
    assert run_ts == CUTOFF


def test_a_straddling_run_cannot_leak_its_later_rows(cap):
    """A run whose id sorts before the cutoff but whose rows were written after it."""
    write_capture(cap, CUTOFF, tickers={"T": {"yes_bid_dollars": "0.40"}})
    day = os.path.join(cap, T0.strftime("%Y-%m-%d"))
    os.makedirs(day, exist_ok=True)
    with open(os.path.join(day, f"{rid(T0)}.quotes.jsonl"), "w") as fh:      # run id BEFORE the cutoff ...
        fh.write(json.dumps({"run_id": rid(T0), "observed_at": FUTURE.isoformat(),   # ... row observed AFTER it
                             "ticker": "T2", "yes_bid_dollars": "0.99"}) + "\n")
    q, _rt, _a, _c, _m = CIO.load_latest_quotes(cap, snapshot_id=rid(CUTOFF))
    assert "T2" not in q, "a row observed after the cutoff must be refused even from an earlier-named run"


def test_a_book_observed_after_the_cutoff_is_not_used(cap):
    write_capture(cap, CUTOFF, tickers={"T": {"orderbook_fp": {"no_dollars": [["0.60", "100"]], "yes_dollars": []}}}, kind="books")
    write_capture(cap, FUTURE, tickers={"T": {"orderbook_fp": {"no_dollars": [["0.10", "100"]], "yes_dollars": []}}}, kind="books")
    books = CIO.load_books(cap, cutoff=CUTOFF)
    assert books["T"]["orderbook_fp"]["no_dollars"][0][0] == "0.60"


def test_a_post_kickoff_book_is_rejected_even_from_a_books_file(cap):
    """The corpus defect the audit measured: books.jsonl provably contains rows fetched after kickoff."""
    write_capture(cap, KICK - timedelta(minutes=5), tickers={"T": {"orderbook_fp": {"no_dollars": [["0.60", "100"]], "yes_dollars": []}}}, kind="books")
    write_capture(cap, KICK + timedelta(minutes=5), tickers={"T": {"orderbook_fp": {"no_dollars": [["0.10", "100"]], "yes_dollars": []}}}, kind="books")
    late = CIO.load_books(cap, cutoff=KICK + timedelta(hours=1))
    assert late["T"]["orderbook_fp"]["no_dollars"][0][0] == "0.10", "without a kickoff the later book wins"
    guarded = CIO.load_books(cap, cutoff=KICK + timedelta(hours=1), kickoffs={"T": KICK})
    assert guarded["T"]["orderbook_fp"]["no_dollars"][0][0] == "0.60", "with a kickoff the post-kickoff book is refused"


def test_discovery_is_bounded_by_the_cutoff(cap):
    for dt in (T0, CUTOFF, FUTURE):
        d = os.path.join(cap, "data", "kalshi", "discovery", rid(dt))
        os.makedirs(d, exist_ok=True)
        json.dump({"run_id": rid(dt)}, open(os.path.join(d, "summary.json"), "w"))
    assert os.path.basename(CIO.latest_discovery_dir(cap, cutoff=CUTOFF)) == rid(CUTOFF)
    assert os.path.basename(CIO.latest_discovery_dir(cap)) == rid(FUTURE), "unbounded still takes the newest"


# ---------------------------------------------------------------------------------------------- depth pairing
def write_depth(root, run_dt, ticker, price, *, kickoff=KICK):
    day = os.path.join(root, run_dt.strftime("%Y-%m-%d"))
    os.makedirs(day, exist_ok=True)
    with gzip.open(os.path.join(day, f"{rid(run_dt)}.depth.jsonl.gz"), "wt") as fh:
        fh.write(json.dumps({"run_id": rid(run_dt), "observed_at": run_dt.isoformat(), "ticker": ticker,
                             "kickoff_utc": kickoff.isoformat(),
                             "minutes_to_kickoff": (kickoff - run_dt).total_seconds() / 60.0,
                             "orderbook_fp": {"no_dollars": [[price, "500"]], "yes_dollars": []}}) + "\n")


def test_depth_observed_after_the_projection_cutoff_cannot_describe_its_entry(cap):
    write_depth(cap, T0, "T", "0.60")
    write_depth(cap, FUTURE, "T", "0.10")
    idx = XD.DepthIndex([cap])
    row, why = idx.pair("T", cutoff=CUTOFF, kickoff=KICK)
    assert row["observed_at"] == T0.isoformat() and why == "paired"
    only_future = XD.DepthIndex([cap]).pair("T", cutoff=T0 - timedelta(hours=1), kickoff=KICK)
    assert only_future[0] is None and "after this projection's cutoff" in only_future[1]


def test_depth_observed_after_kickoff_is_never_pregame_entry_evidence(cap):
    write_depth(cap, KICK + timedelta(minutes=10), "T", "0.10")
    row, why = XD.DepthIndex([cap]).pair("T", cutoff=KICK + timedelta(hours=2), kickoff=KICK)
    assert row is None and "before kickoff" in why or row is None


def test_missing_qualifying_depth_stays_not_captured_and_fabricates_nothing(cap):
    idx = XD.DepthIndex([cap])
    out = XD.pair_and_walk(idx, {"ticker": "T", "data_cutoff": CUTOFF.isoformat(), "kickoff_utc": KICK.isoformat()})
    assert out["state"] == XD.DEPTH_NOT_CAPTURED and "rows" not in out


# ---------------------------------------------------------------------------------------------- reachability
def test_a_season_record_is_dispatchable_and_cannot_silently_disappear():
    rec = {"market_family": "DIVISION_WINNER", "engine": "SEASON", "ticker": "KXNFLAFCEAST-27-NYJ",
           "event_ticker": "KXNFLAFCEAST-27", "subject_id": "NYJ", "p_yes": 0.2,
           "expected_expiration_time": "2027-01-11T15:00:00Z"}
    rr = RE.reachability(rec)
    assert rr["state"] == RE.DISPATCHABLE and rr["scope"] == RE.SEASON
    assert rr["season"] == 2026, "Kalshi's -27 is the season ENDING in 2027, i.e. nflverse 2026"


def test_a_season_record_without_a_resolvable_season_says_so_rather_than_guessing():
    rr = RE.reachability({"market_family": "MAKE_PLAYOFFS", "engine": "SEASON", "ticker": "X", "subject_id": "KC", "p_yes": 0.5})
    assert rr["state"] == RE.MISSING_KEYS and "season" in rr["missing"]


def test_disagreeing_season_years_refuse_rather_than_choose():
    rr = RE.reachability({"market_family": "DIVISION_WINNER", "engine": "SEASON", "ticker": "KXNFLAFCEAST-27-NYJ",
                          "event_ticker": "KXNFLAFCEAST-27", "subject_id": "NYJ", "p_yes": 0.2,
                          "expected_expiration_time": "2029-01-11T15:00:00Z"})
    assert rr["state"] == RE.MISSING_KEYS and "disagrees" in rr["reason"]


def test_reachability_is_measured_on_the_record_not_on_the_catalog():
    """The defect that produced a false 'zero records without a settlement path'."""
    catalog_says_supported = {"market_family": "TEAM_WINS_BY_WEEK", "engine": "SEASON", "p_yes": 0.4,
                              "ticker": "T", "subject_id": None}
    assert RE.reachability(catalog_says_supported)["state"] != RE.DISPATCHABLE
    s = RE.summarize([catalog_says_supported])
    assert s["dispatchable"] == 0 and s["probability_carrying"] == 1


def test_every_probability_record_receives_exactly_one_reachability_verdict():
    recs = [{"market_family": "GAME_WINNER", "engine": "GAME", "game_id": "G", "p_yes": 0.5},
            {"market_family": "PLAYER_STAT", "engine": "PLAYER", "game_id": "G", "subject_id": "00-1", "p_yes": 0.5},
            {"market_family": "SEASON_WINS", "engine": "SEASON", "subject_id": "KC", "season": 2026, "p_yes": 0.5},
            {"market_family": "AWARD", "engine": "NONE", "p_yes": 0.5},
            {"market_family": "GAME_WINNER", "engine": "GAME"}]
    s = RE.summarize(recs)
    assert s["probability_carrying"] == 4 and s["dispatchable"] == 3
    assert sum(s["by_state"].values()) == len(recs), "every record is accounted for exactly once"


# ------------------------------------------------- depth reaches research through the EXPORT, never the record
def _export_module():
    import importlib.util
    p = os.path.join(ROOT, "scripts", "shadow_v2", "research_export_v2.py")
    spec = importlib.util.spec_from_file_location("research_export_v2", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _proj(**kw):
    return {"record_id": "R1", "snapshot_id": rid(CUTOFF), "ticker": "T", "model_arm": "BOARD_V2",
            "kickoff_utc": KICK.isoformat(), "observed_at": CUTOFF.isoformat(),
            "yes_bid": 0.38, "yes_ask": 0.40, "no_bid": 0.60, "no_ask": 0.62, "mid": 0.39,
            "contract_value": 0.62, "p_yes": 0.62,
            "lineage": {"point_in_time": {"data_cutoff": CUTOFF.isoformat()}}, **kw}


def test_the_export_pairs_dedicated_depth_by_timestamp_and_records_the_age(cap):
    """The frozen record is never mutated: the join happens in the derived export and carries its own age."""
    write_depth(cap, T0, "T", "0.60")
    m = _export_module()
    proj = _proj()
    rows = m.build_rows([proj], {}, {}, {}, {}, {}, None, XD.DepthIndex([cap]))
    r = rows[0]
    assert r["depth_pair_state"] in (XD.DEPTH_CAPTURED, XD.DEPTH_STALE), "an old-but-qualifying book pairs, flagged stale"
    assert r["depth_pair_observed_at"] == T0.isoformat()
    assert r["depth_pair_age_min"] == pytest.approx((CUTOFF - T0).total_seconds() / 60.0, abs=1e-3)
    assert r["depth_pair_minutes_to_kickoff"] == pytest.approx((KICK - T0).total_seconds() / 60.0, abs=1e-3)
    assert "point_in_time" in (proj.get("lineage") or {}) and "depth_pair" not in proj, "the record must not be mutated"


def test_the_export_refuses_depth_that_postdates_the_record_and_says_why(cap):
    write_depth(cap, FUTURE, "T", "0.10")
    m = _export_module()
    rows = m.build_rows([_proj()], {}, {}, {}, {}, {}, None, XD.DepthIndex([cap]))
    r = rows[0]
    assert r["depth_pair_state"] == XD.DEPTH_NOT_CAPTURED
    assert "after this projection's cutoff" in r["depth_pair_reason"]
    assert r["depth_pair_age_min"] is None and r["depth_pair_observed_at"] is None


def test_with_no_dedicated_sweep_at_all_the_pairing_columns_are_absent_not_guessed():
    m = _export_module()
    rows = m.build_rows([_proj()], {}, {}, {}, {}, {}, None, XD.DepthIndex([]))
    assert rows[0]["depth_pair_state"] is None and rows[0]["depth_pair_version"] is None
