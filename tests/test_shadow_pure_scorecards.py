"""PURE shadow scorecards: accuracy_scorecard and the dry-run value_scorecard through the real settle_and_evaluate path.

Synthetic nflverse-shaped inputs and a synthetic market-data dir (no network). These prove the CODE PATH: both
populations, every arm role, nothing dropped silently, zero matured rows, strike / unit mapping, the market-informed
flag. The collected evidence is the store on the market-data branch, never these fixtures.
"""
from __future__ import annotations

import gzip
import json
import os
import sys
from datetime import timedelta

import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nfl_edge.engines.player.pure_v1 import BASELINE_NAME, MODEL_NAME  # noqa: E402
from nfl_edge.engines.player.pure_v1 import data as PD  # noqa: E402
from nfl_edge.shadow_pure import collect as C  # noqa: E402
from nfl_edge.shadow_pure import evaluate as E  # noqa: E402
from nfl_edge.shadow_pure import scorecards as SC  # noqa: E402
from nfl_edge.shadow_pure import store  # noqa: E402
from test_shadow_pure import LAST_SEASON, LAST_WEEK, _md_root, _write_root, root, world  # noqa: E402,F401


def _upcoming(sched):
    g = PD.sports_schedule(sched)
    return g[(g.season == LAST_SEASON) & (g.week == LAST_WEEK)]


def _player_map(tmp, sched):
    import polars as pl
    up = _upcoming(sched)
    p = os.path.join(tmp, "kalshi_player_map.parquet")
    pl.DataFrame({"kalshi_player_id": [f"k-{h}-WR0" for h in up.home_team],
                  "gsis_id": [f"{h}-WR0" for h in up.home_team]}).write_parquet(p)
    return p


def _incumbents(md, sched, as_of):
    """DATA_PLAYER_V4 records without p10/p90 (as published today) and DATA_PLAYER_V5 records with them."""
    up = _upcoming(sched)
    snap = (as_of - timedelta(hours=2)).strftime("%Y%m%dT%H%M%SZ")
    d = os.path.join(md, "data", "shadow", "v2", "projections", as_of.strftime("%Y-%m-%d"))
    os.makedirs(d, exist_ok=True)
    for arm in ("DATA_PLAYER_V4", "DATA_PLAYER_V5"):
        rows = []
        for x in up.itertuples():
            ds = {"mean": 3.6, "p05": 1.0, "p50": 3.0, "p95": 7.0, "quantiles": {"p05": 1.0, "p50": 3.0, "p95": 7.0}}
            if arm == "DATA_PLAYER_V5":
                ds = {**ds, "p10": 1.0, "p90": 6.0}
            for k, p in ((3, 0.62), (4, 0.45), (5, 0.30)):
                rows.append({"game_id": x.game_id, "stat_family": "receptions", "subject_id": f"{x.home_team}-WR0",
                             "snapshot_id": snap, "data_cutoff": (as_of - timedelta(hours=2)).isoformat(),
                             "kickoff_utc": pd.Timestamp(x.kickoff).isoformat(), "engine_version": arm.lower(),
                             "distribution_summary": ds, "threshold": k, "p_yes": p, "feature_lineage": {"env_source": "kalshi"}})
        with gzip.open(os.path.join(d, f"{snap}.{arm}.projections.jsonl.gz"), "wt") as fh:
            for r in rows:
                fh.write(json.dumps(r) + "\n")


def _read(st, suffix):
    return [json.load(open(os.path.join(dp, f))) for dp, _d, fs in os.walk(os.path.join(st, "evaluations")) for f in fs
            if f.endswith(suffix)]


def test_zero_matured_rows_give_insufficient_sample_not_an_error(root, tmp_path):
    r, sched, k = root
    now = (k - pd.Timedelta(hours=1)).to_pydatetime()
    st = str(tmp_path / "st")
    C.run_capture(r, st, now=now, md_root=_md_root(str(tmp_path), sched, now), log=lambda *_: None)
    s = E.settle_and_evaluate(r, st, C.gate(), now=now + timedelta(minutes=5), bootstrap=20)
    assert s["state"] == "NO_MATURED_ROWS"
    sc = s["scorecards_not_written"]
    assert sc["accuracy_scorecard"]["conditional_on_playing"] == {"full_eligible": "INSUFFICIENT_SAMPLE",
                                                                  "pregame_market_listed": "INSUFFICIENT_SAMPLE"}
    assert sc["value_scorecard"]["mode"] == "DRY_RUN_DIAGNOSTIC"
    assert sc["value_scorecard"]["primary"]["verdict"] == "INSUFFICIENT_SAMPLE"
    assert not _read(st, ".accuracy_scorecard.json") and store.verify_store(st) == []


@pytest.fixture(scope="module")
def settled(root, world, tmp_path_factory):
    r, sched, k = root
    tmp = str(tmp_path_factory.mktemp("sc"))
    now = (k - pd.Timedelta(hours=1)).to_pydatetime()            # FINAL_T90 window
    md = _md_root(tmp, sched, now)
    _incumbents(md, sched, now)
    pmap = _player_map(tmp, sched)
    st = os.path.join(tmp, "st")
    cap = C.run_capture(r, st, now=now, md_root=md, map_path=pmap, log=lambda *_: None)
    assert cap["market_status"]["n_capture_rows"] > 0 and cap["incumbent_status"]["state"] == "OK"
    _, stats, snaps = world
    r2 = os.path.join(tmp, "root2")
    later = (k + pd.Timedelta(days=1)).to_pydatetime()
    _write_root(r2, world[0], stats, snaps, fetched_at=later - timedelta(hours=1), future_week=(0, 0))
    s = E.settle_and_evaluate(r2, st, C.gate(), now=later, bootstrap=50)
    return st, s, _read(st, ".accuracy_scorecard.json"), _read(st, ".value_scorecard.json")


def test_accuracy_scorecard_both_populations_and_arm_roles(settled):
    st, s, accs, _ = settled
    assert len(accs) == 1 and s["scorecards_written"]["accuracy_scorecard"]
    acc = accs[0]
    assert acc["record"] == "accuracy_scorecard" and acc["status"] == "DESCRIPTIVE_ONLY_NOT_AUTOMATIC_PROMOTION"
    rep = acc["scorecards"]["conditional_on_playing"]["scorecard"]
    assert set(rep["populations"]) == {"full_eligible", "pregame_market_listed"}
    arms = rep["config"]["arms"]
    assert arms[MODEL_NAME]["role"] == "challenger" and arms[BASELINE_NAME]["role"] == "statistical_baseline"
    assert arms["DATA_PLAYER_V5_market_informed"] == {"role": "market_informed_benchmark", "contract": "projection_only"}
    assert "DATA_PLAYER_V4_market_informed" not in arms       # p05/p50/p95 only: counted, never approximated
    assert acc["market_informed_benchmark"]["counts"]["not_scoreable_missing_mean_p10_p50_p90"] > 0
    full = rep["populations"]["full_eligible"]
    a = full["accounting"]["arms"][MODEL_NAME]
    assert a["scored_rows"] > 50 and a["eligible_identities"] >= a["identities_with_forecast"]
    for key in ("missing_forecast", "forecast_rows_missing_outcome", "conditional_dnp_excluded"):
        assert key in acc["scorecards"]["conditional_on_playing"]["sample_state"]["full_eligible"]
    h2h = next(iter(full["by_statistic"].values()))["head_to_head"]
    assert h2h[BASELINE_NAME]["role"] == "statistical_baseline"
    rec = full["by_statistic"]["NFL:receptions"]["head_to_head"]["DATA_PLAYER_V5_market_informed"]
    assert rec["n_pairs"] > 0 and "PRICE_OF_INDEPENDENCE" in rec["note"]
    cohort = rep["populations"]["pregame_market_listed"]["accounting"]["arms"][MODEL_NAME]
    assert 0 < cohort["scored_rows"] < a["scored_rows"]           # only the listed home WR0 receptions
    assert set(rep["config"]["breakdowns"]) == {"capture_kind", "position_group", "capture_window"}
    assert acc["collection_accounting"]["missed_capture_windows"] == 0
    assert store.verify_store(st) == []


def test_value_scorecard_is_a_preregistered_dry_run_and_flags_market_informed(settled):
    _, s, _, vals = settled
    v = vals[0]
    assert v["mode"] == "DRY_RUN_DIAGNOSTIC" and "no order" in v["wagering"]
    assert v["preregistration"]["file_sha256"] == SC.file_sha256(SC.PREREG_PATH)
    pr = SC.load_prereg()
    prim = v["evaluations"][f"{MODEL_NAME}/FINAL_T90"]
    assert prim["role"] == "primary" and prim["eligible_for_independent_value_verdict"] and not prim["market_informed_source"]
    assert prim["verdict"] == "INSUFFICIENT_SAMPLE"                 # a handful of decisions << 200 / 40 games
    rep = prim["report"]
    assert rep["preregistration"]["thresholds"] == {"min_decisions": 200, "min_games": 40, "min_roi_ci_lower": 0.0}
    assert rep["config"]["fees"]["role"] == "taker" and rep["config"]["fees"]["slippage_per_contract"] == pr["slippage"]
    assert rep["config"]["dnp_policy"] == "settle_by_actual"
    assert rep["accounting"]["rungs_with_entry_quote"] > 0          # threshold 4 -> the at_least 4 rung, dollars
    for name in ("DATA_PLAYER_V4/FINAL_T90", "DATA_PLAYER_V5/FINAL_T90"):
        e = v["evaluations"][name]
        assert e["market_informed_source"] and e["verdict"] == "NOT_INDEPENDENT_EVIDENCE"
        assert not e["eligible_for_independent_value_verdict"]
    assert not v["evaluations"][f"{BASELINE_NAME}/FINAL_T90"]["eligible_for_independent_value_verdict"]
    sens = v["evaluations"][f"{MODEL_NAME}/FINAL_T90/dnp_void"]
    assert sens["role"] == "dnp_sensitivity" and sens["report"]["config"]["dnp_policy"] == "void"
    assert [k for k, e in v["evaluations"].items() if e["verdict_counts_toward_preregistered_decision"]] == [
        f"{MODEL_NAME}/FINAL_T90"]


def test_strike_and_quote_mapping():
    assert SC.kalshi_at_least(50, ">=") == 50.0                      # "50+" is P(X >= 50): the integer rung 50
    assert SC.kalshi_at_least(49.5, ">") == 50.0                     # "> 49.5" on an integer statistic
    assert SC.kalshi_at_least(50, ">=", integer_ladder=False) == 49.5
    assert SC.kalshi_at_least(50, "<") is None and SC.kalshi_at_least(None) is None
    at = pd.Timestamp("2026-10-11T16:00:00Z").to_pydatetime()
    base = {"game_id": "g", "gsis_id": "p", "statistic": "receptions", "open_time": "2026-10-10T00:00:00Z",
            "ticker": "KXNFLREC-X-4", "threshold": 4, "source": "kalshi_capture"}
    rows = [(at, {**base, "observed_at": "2026-10-11T15:00:00+00:00", "yes_bid": "0.40", "yes_ask": "0.45"}),
            (at, {**base, "observed_at": "2026-10-11T15:00:00+00:00", "yes_bid": "0.40", "yes_ask": "0.45"}),   # dup
            (at, {**base, "observed_at": "2026-10-11T16:30:00+00:00", "yes_bid": "0.40", "yes_ask": "0.45"}),   # after
            (at, {**base, "observed_at": "2026-10-11T15:10:00+00:00", "yes_bid": "0.50", "yes_ask": "0.45"}),   # crossed
            (at, {**base, "gsis_id": None, "observed_at": "2026-10-11T15:00:00+00:00"})]
    cohort, quotes, c = SC.market_family(rows, {"g": "2026-10-11T17:00:00Z"})
    assert len(quotes) == 1 and quotes[0]["at_least"] == 4.0 and quotes[0]["price_unit"] == "dollars"
    assert quotes[0]["yes_ask"] == 0.45 and quotes[0]["market"] == "KXNFLREC"
    assert c["quote_duplicate_across_captures"] == 1 and c["dropped_observed_after_capture_as_of"] == 1
    assert c["quote_dropped_crossed"] == 1 and c["dropped_unmapped_player"] == 1 and len(cohort) == 3


def test_a_scorecard_failure_is_recorded_and_never_stops_the_collector(monkeypatch):
    def boom(*a, **k):
        raise ValueError("synthetic")
    monkeypatch.setattr(SC, "build", boom)
    acc, val = SC.build_safe("x", {}, {}, set(), evaluated_at=pd.Timestamp("2026-10-12T00:00:00Z").to_pydatetime(),
                             run_id="r")
    assert acc["state"] == val["state"] == "ERROR" and "synthetic" in acc["error"]
    assert SC.summary_safe(acc, val)["scorecards_state"] == "ERROR"


def test_scorecards_module_touches_no_wagering_surface():
    src = open(os.path.join(ROOT, "nfl_edge", "shadow_pure", "scorecards.py")).read()
    imports = [x.strip() for x in src.splitlines() if x.startswith(("import ", "from "))]
    assert all(x.split()[1].split(".")[0] in {"__future__", "glob", "hashlib", "importlib", "json", "math", "os", "sys",
                                              "collections", "datetime", "nfl_edge"} for x in imports), imports
    assert not [x for x in imports if any(b in x for b in ("execution", "staking", "routing", "wager", "order", "kalshi"))]
