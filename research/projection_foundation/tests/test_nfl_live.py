"""Tests for the NFL live shadow operation (research/projection_foundation/nfl/live).

All inputs are REAL recorded payloads of one game - 2026 week-6 Thursday night, SEA @ DEN, kickoff 2026-10-16T00:15Z -
trimmed to the two teams (tests/fixtures/nfl_live, see PROVENANCE.json): ESPN injuries captured by the repo's PIT capture at
18:16Z and 23:15Z (T-60 min), Sleeper players, the shadow-0.4.0 ledger and player anatomy, nflverse rows, final stats.
Where a forecast of OUR model is needed (it needs the 280 MB walk-forward state, which CI does not have) a clearly named
stand-in distribution is used to exercise the plumbing; those tests assert behaviour (idempotency, void, corrections), not
accuracy. The full chain on the real state is nfl/live/smoke.py.
"""
import gzip
import json
import os
import shutil
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest

PF = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, PF)

from pf_core import availability as av, dists, prospective as pr  # noqa: E402
from nfl.live import availability as LA, ledger as LG, results as RS, score as SC  # noqa: E402
from nfl.live import run as RUN  # noqa: E402

FX = os.path.join(os.path.dirname(__file__), "fixtures", "nfl_live")
GAME = "2026_06_SEA_DEN"
START = "2026-10-16T00:15:00Z"
EVENT = {"event_id": GAME, "start_utc": START, "home": "DEN", "away": "SEA", "season": 2026, "week": 6}


@pytest.fixture(scope="module")
def ids():
    return LA.IdMaps(pd.read_parquet(f"{FX}/nflverse/players/players.parquet"),
                     pd.read_parquet(f"{FX}/nflverse/weekly_rosters/roster_weekly_2026.parquet"), 2026)


def espn(tag):
    return json.load(gzip.open(f"{FX}/recorded/espn_injuries_{tag}.json.gz"))


def sleeper(tag):
    j = json.load(open(f"{FX}/recorded/sleeper_{tag}.json"))
    return j["players"], {"retrieved_at": j["retrieved_at"], "url": LA.SLEEPER_URL}


def rows_of(obs):
    return [o.__dict__ for o in obs]


# ----------------------------------------------------------------------------------------------- availability parsers
def test_espn_injuries_real_payload(ids):
    rec = espn("20261015T231527Z")
    obs, st = LA.espn_injury_observations(rec["payload"], rec["meta"], [EVENT], ids)
    assert len(obs) == 29 and st == {"OUT": 7, "ACTIVE": 22}
    assert all(not o.validate() for o in obs)
    assert {o.certainty for o in obs} == {"REPORTED"} and {o.kind for o in obs} == {"injury"}
    # every observation: source, URL, OUR capture time, the source's own time (never later than ours), event + start, entity, team
    for o in obs:
        assert o.source == "espn_injuries" and o.source_url.startswith("https://site.api.espn.com")
        assert o.captured_utc == "2026-10-15T23:15:27Z" and o.event_id == GAME and o.event_start_utc == START
        assert o.entity_id.startswith("00-") and o.team in ("SEA", "DEN")
        assert o.source_updated_utc is None or av._ts(o.source_updated_utc) <= av._ts(o.captured_utc)
    assert {"Jalen Milroe", "Sam Ehlinger", "Dallen Bentley", "Robert Henry Jr.", "Montorie Foster Jr."} <= \
        {o.entity_name for o in obs if o.status == "OUT"}


def test_sleeper_real_payload_maps_ids_through_the_roster(ids):
    players, meta = sleeper("20261015T213956Z")
    obs, st = LA.sleeper_observations(players, meta, [EVENT], ids)
    assert obs and set(st) <= {"OUT", "QUESTIONABLE", "DOUBTFUL", "UNKNOWN", "unmapped_id"}
    assert all(o.entity_id.startswith("00-") and o.certainty == "REPORTED" and o.source == "sleeper_players" for o in obs)
    assert all(not o.validate() for o in obs)


def test_depth_chart_uses_the_newest_snapshot_not_after_capture():
    dc = pd.read_parquet(f"{FX}/nflverse/depth_charts/depth_charts_2026.parquet")
    obs, st = LA.nflverse_depth_observations(dc, {"retrieved_at": "2026-10-15T23:00:00Z", "url": "u"}, [EVENT])
    assert st["snapshots"] == 1 and all(o.certainty == "PROJECTED" for o in obs)
    assert {o.source_updated_utc for o in obs} == {"2026-10-15T12:37:05Z"}          # the 12:37Z snapshot
    qb1 = {o.entity_name for o in obs if o.kind == "starter"}
    assert qb1 == {"Bo Nix", "Sam Darnold"}                                             # QB1 -> kind starter
    # a capture BEFORE that snapshot cannot see it (it falls back to the previous one)
    early, _ = LA.nflverse_depth_observations(dc, {"retrieved_at": "2026-10-15T07:00:00Z", "url": "u"}, [EVENT])
    assert {o.source_updated_utc for o in early} == {"2026-10-15T06:02:57Z"} or all(
        av._ts(o.source_updated_utc) <= av._ts("2026-10-15T07:00:00Z") for o in early)


def test_roster_inactive_list_is_confirmed_only_when_visibly_posted():
    ro = pd.read_parquet(f"{FX}/nflverse/weekly_rosters/roster_weekly_2026.parquet")
    obs, st = LA.nflverse_roster_observations(ro, {"retrieved_at": "2026-10-15T23:40:00Z", "url": "u", "last_modified_iso": None}, [EVENT])
    assert st["list_posted:True"] == 2 and st["INACTIVE"] == 5
    assert {o.entity_name.replace(".", "") for o in obs if o.status == "INACTIVE"} == \
        {"Jalen Milroe", "Sam Ehlinger", "Dallen Bentley", "Robert Henry Jr", "Montorie Foster Jr"}
    assert all(o.certainty == "CONFIRMED" for o in obs if o.status in ("INACTIVE", "ACTIVE") and o.detail.get("team_ina") is not None)
    # fewer than 3 INA rows for a team = the list is not visibly posted: nothing is read as confirmed
    thin = ro.copy()
    thin.loc[thin.status == "INA", "status"] = "ACT"
    obs2, st2 = LA.nflverse_roster_observations(thin, {"retrieved_at": "2026-10-15T23:40:00Z", "url": "u"}, [EVENT])
    assert st2["list_posted:False"] == 2 and not [o for o in obs2 if o.certainty == "CONFIRMED"]


def test_the_espn_feed_flips_to_out_exactly_for_the_official_inactives(ids):
    """Measured on the real payloads: between the 18:16Z and 23:15Z captures ESPN flips five skill players to Out, and they
    are exactly the five skill players on nflverse's INA (official inactive) list for the game."""
    a, _ = LA.espn_injury_observations(espn("20261015T181653Z")["payload"], espn("20261015T181653Z")["meta"], [EVENT], ids)
    b, _ = LA.espn_injury_observations(espn("20261015T231527Z")["payload"], espn("20261015T231527Z")["meta"], [EVENT], ids)
    out_a = {o.entity_id for o in a if o.status == "OUT"}
    out_b = {o.entity_id for o in b if o.status == "OUT"}
    ro = pd.read_parquet(f"{FX}/nflverse/weekly_rosters/roster_weekly_2026.parquet")
    ina = set(ro[(ro.status == "INA") & ro.position.isin(LA.SKILL)].gsis_id)
    assert ina and ina <= out_b and ina.isdisjoint(out_a)


# ----------------------------------------------------------------------------------------------- as-of resolution
def _all_rows(ids):
    rows = []
    for tag, cap in (("20261015T181653Z", None), ("20261015T231527Z", None)):
        rec = espn(tag)
        rows += rows_of(LA.espn_injury_observations(rec["payload"], rec["meta"], [EVENT], ids)[0])
    dc = pd.read_parquet(f"{FX}/nflverse/depth_charts/depth_charts_2026.parquet")
    rows += rows_of(LA.nflverse_depth_observations(dc, {"retrieved_at": "2026-10-15T18:00:00Z", "url": "u"}, [EVENT])[0])
    return rows


def test_participation_evolves_with_the_clock_and_never_uses_the_future(ids):
    rows = _all_rows(ids)
    ent = next(o["entity_id"] for o in rows if o["entity_name"] == "Jalen Milroe" and o["source"] == "espn_injuries")
    p1 = LA.resolve(rows, "2026-10-15T18:30:00Z", GAME, ent)          # only the 18:16Z capture is visible
    p2 = LA.resolve(rows, "2026-10-15T23:20:00Z", GAME, ent)          # the 23:15Z capture says Out
    assert p1.status == av.LIKELY_ACTIVE and p2.status == av.CONFIRMED_OUT and p2.source == "espn_injuries"
    # after kickoff nothing captured at/after the start counts, whatever the cut-off
    late = rows + [av.Observation(sport="NFL", event_id=GAME, event_start_utc=START, entity_id=ent, entity_name="x", team="SEA",
                                  kind="injury", status="ACTIVE", certainty="CONFIRMED", source="espn_injuries",
                                  captured_utc="2026-10-16T00:30:00Z").__dict__]
    assert LA.resolve(late, "2026-10-16T05:00:00Z", GAME, ent).status == av.CONFIRMED_OUT
    # nobody observed -> UNVERIFIED, never active
    assert LA.resolve(rows, "2026-10-15T23:20:00Z", GAME, "00-0000000").status == av.UNVERIFIED


def test_injury_sources_are_merged_by_severity_within_the_window():
    base = dict(sport="NFL", event_id=GAME, event_start_utc=START, entity_id="00-1", entity_name="x", team="SEA", kind="injury",
                certainty="REPORTED")
    q = av.Observation(**base, status="QUESTIONABLE", source="espn_injuries", captured_utc="2026-10-15T20:00:00Z").__dict__
    o = av.Observation(**base, status="OUT", source="sleeper_players", captured_utc="2026-10-15T20:30:00Z").__dict__
    lat = LA.merged_asof([q, o], "2026-10-15T21:00:00Z")
    assert lat[(GAME, "00-1", "injury")]["status"] == "OUT"
    # a clearance (ACTIVE) from the newest source beats an older, outside-the-window Questionable
    old = av.Observation(**base, status="QUESTIONABLE", source="sleeper_players", captured_utc="2026-10-15T10:00:00Z").__dict__
    new = av.Observation(**base, status="ACTIVE", source="espn_injuries", captured_utc="2026-10-15T20:00:00Z").__dict__
    assert LA.merged_asof([old, new], "2026-10-15T21:00:00Z")[(GAME, "00-1", "injury")]["status"] == "ACTIVE"
    # practice-only (UNKNOWN) rows never override a real designation
    unk = av.Observation(**base, status="UNKNOWN", source="nflverse_injuries", captured_utc="2026-10-15T20:45:00Z").__dict__
    assert LA.merged_asof([q, unk], "2026-10-15T21:00:00Z")[(GAME, "00-1", "injury")]["status"] == "QUESTIONABLE"


def test_injury_table_for_the_availability_rung(ids):
    rows = _all_rows(ids)
    lat = LA.merged_asof(rows, "2026-10-15T23:20:00Z")
    t = LA.injury_table(lat, 2026, 6)
    assert set(t.report_status) == {"Out"} and len(t) >= 5 and set(t.season) == {2026} and set(t.week) == {6}


def test_coverage_counts_unobserved_players(ids):
    rows = _all_rows(ids)
    ents = sorted({r["entity_id"] for r in rows})[:5] + ["00-9999999"]
    cov = LA.coverage(rows, {GAME: ents}, [EVENT], "2026-10-15T23:20:00Z")
    assert cov["events"][GAME]["observed"] == 5 and cov["events"][GAME]["expected"] == 6
    assert cov["participation_status"]["UNVERIFIED"] == 1


def test_snapshot_is_write_once_and_idempotent(ids, tmp_path):
    rec = espn("20261015T231527Z")
    obs, _ = LA.espn_injury_observations(rec["payload"], rec["meta"], [EVENT], ids)
    r1 = av.write_snapshot(obs, str(tmp_path), "NFL", "2026-10-15T23:20:00Z")
    r2 = av.write_snapshot(obs, str(tmp_path), "NFL", "2026-10-15T23:25:00Z")
    assert r1["written"] == len(obs) and r2["duplicate"] and r2["written"] == 0
    assert len(av.load_snapshots(str(tmp_path), "NFL")) == len(obs)


# ----------------------------------------------------------------------------------------------- incumbent ledger (read-only)
def test_ledger_reader_picks_the_run_before_now_and_never_a_started_game():
    r = LG.DirReader(f"{FX}/market-data")
    assert LG.latest_run(r, LG.INCUMBENT, "2026-10-15T12:00:00Z") is None            # nothing priced yet
    assert LG.latest_run(r, LG.INCUMBENT, "2026-10-15T18:30:00Z")[0] == "20261015T170741Z"
    assert LG.latest_run(r, LG.INCUMBENT, "2026-10-15T23:20:00Z")[0] == "20261015T213127Z"
    out = LG.incumbent_forecasts(r, "2026-10-15T23:20:00Z", {GAME})
    assert out["records"] and out["run_id"] == "20261015T213127Z"
    for x in out["records"]:
        assert x["model_role"] == "incumbent" and x["model_id"] == "shadow-0.4.0" and x["probs"] == [] and x["game_id"] == GAME
        assert x["family"] in LG.FAMILY.values() and x["ladder"] and av._ts(x["generated_utc"]) < av._ts(x["game_start_utc"])
    assert any(x["family"] == "passing_attempts" and x.get("anatomy_run") for x in out["records"])      # mean from the anatomy
    # after kickoff the same snapshot yields nothing (contracts for a started game are not forecasts)
    assert LG.incumbent_forecasts(r, "2026-10-16T00:30:00Z", {GAME})["records"] == []


# ----------------------------------------------------------------------------------------------- results -> settle -> score
def _sched_row():
    g = pd.read_csv(f"{FX}/nflverse/schedules/games.csv")
    g["kickoff_utc"] = pd.Timestamp(START)
    return g


def _stand_in_challenger(inc, name_by_ent):
    """NOT our model: a Poisson/normal pmf around the incumbent mean, to exercise archive/settle/score plumbing."""
    recs = []
    for x in inc:
        if x["family"] == "anytime_td":
            d = dists.DistBatch(0, np.array([[1 - x["mean"], x["mean"]]]))
        elif x["family"].endswith("yards"):
            from scipy.stats import norm
            grid = np.arange(-20, 400)
            sd = max(x["mean"] * 0.6, 8.0)
            pm = np.diff(norm.cdf(np.append(grid, grid[-1] + 1) - 0.5, x["mean"], sd))
            d = dists.DistBatch(-20, (pm / pm.sum())[None, :])
        else:
            d = dists.poisson(np.array([x["mean"]]), K=80)
        recs.append({**{k: x[k] for k in ("sport", "family", "game_id", "game_start_utc", "entity_id", "entity_name", "team")},
                     "model_id": "pf-nfl", "model_role": "challenger", "model_version": "stand-in", "generated_utc": "2026-10-15T23:20:00Z",
                     "data_asof_utc": "2026-10-15T23:15:00Z", "mean": float(d.mean[0]), "lo": int(d.lo), "probs": [float(p) for p in d.P[0]],
                     "gate_status": "PASS", "participation": "LIKELY_ACTIVE", "readiness": "SHADOW VALIDATION",
                     "segments": {"new_team_first4": False, "tier": "WR1", "backup": False, "rookie": False}})
    return recs


def test_final_results_participation_and_settle_once(tmp_path):
    inc = LG.incumbent_forecasts(LG.DirReader(f"{FX}/market-data"), "2026-10-15T23:20:00Z", {GAME})["records"]
    ch = _stand_in_challenger(inc, {})
    # one forecast for a player who was on the inactive list (a DNP) and one for a team total
    milroe = "00-0042071"
    ro = pd.read_parquet(f"{FX}/nflverse/weekly_rosters/roster_weekly_2026.parquet")
    milroe = ro[ro.full_name == "Jalen Milroe"].gsis_id.iloc[0]
    dnp = {**ch[0], "entity_id": milroe, "entity_name": "Jalen Milroe", "family": "carries", "team": "SEA"}
    d = dists.poisson(np.array([2.0]), K=30)
    dnp.update(mean=2.0, lo=0, probs=[float(p) for p in d.P[0]], model_role="challenger")
    root = str(tmp_path)
    s0 = pr.archive_forecasts(ch + inc + [dnp], root, now_utc="2026-10-15T23:21:00Z")
    assert s0["written"] == len(ch) + len(inc) + 1 and s0["late_rejected"] == 0
    # nothing can be archived once the game has started, even if it was generated before
    late = pr.archive_forecasts([{**ch[0], "generated_utc": "2026-10-15T23:40:00Z"}], root, now_utc="2026-10-16T00:20:00Z")
    assert late["late_rejected"] == 1 and late["written"] == 0
    rows, st = RS.build_outcomes(root, "2026-10-17T22:30:00Z", _sched_row(), raw_base=f"{FX}/nflverse", silver_base=f"{FX}/silver")
    assert st["games_final"] == 1 and st["outcomes_new_or_changed"] > 0
    byk = {(r["entity_id"], r["family"]): r for r in rows}
    assert byk[(milroe, "carries")]["participated"] is False                      # on the inactive list -> DNP -> void
    assert any(r["participated"] for r in rows)
    w = pr.archive_outcomes(rows, root, "NFL", now_utc="2026-10-17T22:31:00Z")
    assert w["written"] == len(rows)
    s1 = pr.settle(root, "NFL", now_utc="2026-10-17T22:32:00Z")
    assert s1["void"] >= 1 and s1["settled"] > 0 and s1["corrections"] == 0
    # idempotent: results find nothing new, settle settles nothing again
    rows2, st2 = RS.build_outcomes(root, "2026-10-17T23:00:00Z", _sched_row(), raw_base=f"{FX}/nflverse", silver_base=f"{FX}/silver")
    assert rows2 == [] and st2["outcomes_unchanged"] > 0
    s2 = pr.settle(root, "NFL", now_utc="2026-10-17T23:01:00Z")
    assert s2["settled"] == 0 and s2["void"] == 0 and s2["corrections"] == 0 and s2["already_settled"] > 0
    # a stat correction: ONE correction record, the original settlement untouched
    k = next(r for r in rows if r["participated"] and r["family"] == "receiving_yards")
    pr.archive_outcomes([{**k, "actual": k["actual"] + 7}], root, "NFL", now_utc="2026-10-18T10:00:00Z")
    s3 = pr.settle(root, "NFL", now_utc="2026-10-18T10:05:00Z")
    sett = pr.load_settlements(root, "NFL")
    n_fc = int(((sett.entity_id == k["entity_id"]) & (sett.family == "receiving_yards")).sum())     # one forecast per model
    assert s3["corrections"] == n_fc >= 1                                           # one correction record per settled forecast
    corr = pr._read(root, "corrections", "NFL")
    assert len({c["forecast_id"] for c in corr}) == len(corr) == n_fc and all(c["previous_actual"] == k["actual"] for c in corr)
    assert float(sett[(sett.entity_id == k["entity_id"]) & (sett.family == "receiving_yards") & (sett.model_role == "challenger")].actual.iloc[0]) == k["actual"]
    assert pr.settle(root, "NFL", now_utc="2026-10-18T10:10:00Z")["corrections"] == 0
    # the scorecard + NFL monitoring lines build from the same archive
    cards = SC.build_cards(root, "2026-10-18T11:00:00Z", {"families": []})
    assert set(cards) == {"daily", "weekly", "season"}
    md = SC.render_nfl_markdown(cards["season"])
    assert "NFL monitoring lines" in md
    assert "Rung Brier" in md or cards["season"]["nfl"]["incumbent_ladder"]["families"] == {}
    seg = cards["season"]["nfl"]["segment_drift"]["families"]
    assert seg and all("none_of_the_three" in v for v in seg.values())
    assert cards["season"]["nfl"]["participation_vs_dnp"]["LIKELY_ACTIVE"]["dnp_rate"] > 0


def test_results_wait_for_final_data():
    g = _sched_row()
    open_ = g.iloc[0].copy()
    open_["home_score"] = np.nan
    r = RS.game_results(GAME, 2026, open_, "2026-10-17T22:30:00Z", f"{FX}/nflverse", f"{FX}/silver")
    assert not r["final"] and "score" in r["reason"]
    # snap counts missing and the game is recent: wait; four days later: stats-only, flagged
    tmp = os.path.join(os.path.dirname(FX), "_tmp_raw")
    shutil.rmtree(tmp, ignore_errors=True)
    shutil.copytree(f"{FX}/nflverse", tmp)
    os.remove(f"{tmp}/snap_counts/snap_counts_2026.parquet")
    try:
        recent = RS.game_results(GAME, 2026, g.iloc[0], "2026-10-16T10:00:00Z", tmp, f"{FX}/silver")
        assert not recent["final"] and "snap counts" in recent["reason"]
        old = RS.game_results(GAME, 2026, g.iloc[0], "2026-10-25T10:00:00Z", tmp, f"{FX}/silver")
        assert old["final"] and old["basis"] == "stats_only"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_upcoming_events_window():
    sched = pd.DataFrame({"game_id": ["a", "b", "c"], "home_team": ["X"] * 3, "away_team": ["Y"] * 3, "season": [2026] * 3, "week": [6] * 3,
                          "kickoff_utc": pd.to_datetime(["2026-10-16T00:15:00Z", "2026-10-18T17:00:00Z", "2026-10-30T17:00:00Z"], utc=True)})
    ev = LA.upcoming_events(sched, "2026-10-17T12:00:00Z", 120)
    assert [e["event_id"] for e in ev] == ["b"]                      # 'a' started, 'c' is beyond the horizon


def test_new_versions_dedupe(tmp_path):
    rec = {"sport": "NFL", "family": "targets", "model_id": "pf-nfl", "model_role": "challenger", "game_id": GAME, "game_start_utc": START,
           "entity_id": "p", "entity_name": "p", "team": "SEA", "generated_utc": "2026-10-15T18:00:00Z", "data_asof_utc": "2026-10-15T18:00:00Z",
           "mean": 3.0, "lo": 0, "probs": [0.1, 0.2, 0.3, 0.4], "gate_status": None, "participation": None, "readiness": "READY"}
    pr.archive_forecasts([rec], str(tmp_path), now_utc="2026-10-15T18:01:00Z")
    same = {**rec, "generated_utc": "2026-10-15T20:00:00Z"}
    changed = {**rec, "generated_utc": "2026-10-15T20:00:00Z", "mean": 3.5, "entity_id": "p"}
    assert RUN._new_versions([same], str(tmp_path)) == []                       # NaN/None-safe: unchanged content is not re-archived
    assert RUN._new_versions([changed], str(tmp_path)) == [changed]


def test_archive_guard_blocks_edits_of_immutable_files(tmp_path):
    d = str(tmp_path)
    subprocess.run(["git", "init", "-q", d], check=True)
    pr.archive_forecasts([{"sport": "NFL", "family": "targets", "model_id": "m", "model_role": "challenger", "game_id": GAME,
                           "game_start_utc": START, "entity_id": "p", "entity_name": "p", "team": "SEA",
                           "generated_utc": "2026-10-15T18:00:00Z", "data_asof_utc": "2026-10-15T18:00:00Z", "mean": 1.0, "lo": 0,
                           "probs": [0.5, 0.5], "gate_status": None, "participation": None, "readiness": None}], d, now_utc="2026-10-15T18:01:00Z")
    subprocess.run(["git", "-C", d, "add", "."], check=True)
    subprocess.run(["git", "-C", d, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "x"], check=True)
    from pf_core import archive_guard
    assert archive_guard.violations(d) == []
    f = next(os.path.join(dp, fn) for dp, _, fs in os.walk(os.path.join(d, "forecasts")) for fn in fs)
    open(f, "wb").write(b"tampered")
    assert archive_guard.violations(d)


# ----------------------------------------------------------------------------------------------- segment monitoring math
def test_segment_drift_reports_bias_with_n():
    rng = np.random.default_rng(1)
    n = 120
    recs = []
    for i in range(n):
        seg = {"new_team_first4": i % 3 == 0, "backup": i % 4 == 0, "rookie": i % 10 == 0, "tier": "WR3+"}
        actual = float(rng.poisson(5))
        over = 1.3 if seg["new_team_first4"] else 1.0
        recs.append({"forecast_id": f"f{i}", "model_role": "challenger", "game_id": f"g{i % 12}", "entity_id": f"p{i}", "family": "targets",
                     "mean": 5.0 * over, "actual": actual, "segments": seg})
    s = pd.DataFrame(recs)
    f = pd.DataFrame({"forecast_id": s.forecast_id, "segments": s.segments})
    out = SC.segment_drift(s, f)
    r = out["families"]["targets"]
    assert r["new_team_first4"]["n"] == 40 and r["new_team_first4"]["relative_bias"] > 0.15
    assert r["new_team_first4"]["status"] == "WATCH" and abs(r["none_of_the_three"]["relative_bias"]) < 0.2
    assert "bias_ci95" in r["new_team_first4"]


def test_nfl_gate_blocks_confirmed_out_and_reviews_unverified():
    """The NFL gate wrapper the live projector calls (gate_nfl.run) turns participation into gate status: CONFIRMED_OUT is
    BLOCK (SIFT withholds the number), UNVERIFIED / UNCERTAIN are REVIEW, a likely-active player with clean inputs is not
    blocked. The TNF replay game has no projected player who was ruled out, so the BLOCK path is pinned here."""
    from nfl import gate_nfl as G
    ko = pd.Timestamp("2026-10-16T00:15:00Z")
    hist = [5.0, 7.0, 6.0, 8.0, 6.0, 7.0, 5.0, 6.0]
    rows = pd.DataFrame([{"player_id": f"00-00{i}", "player_display_name": f"P{i}", "team": "SEA", "game_id": "2026_06_SEA_DEN",
                          "kickoff_utc": ko, "career_games": 40, "opp_games_season": 5,
                          "_hist_targets": hist, "_hist_receptions": [4.0, 5.0, 4.0, 6.0, 4.0, 5.0, 3.0, 4.0]} for i in range(4)])
    mean = np.array([4.5, 4.5, 4.5, 4.5])
    dist = dists.poisson(mean)
    part = [av.CONFIRMED_OUT, av.UNVERIFIED, av.UNCERTAIN, av.LIKELY_ACTIVE]
    res = G.run("receptions", rows, mean, dist, "receptions", opp_mean=np.full(4, 6.5), rungs=[3, 5],
                now_utc="2026-10-15T23:20:00Z", participation=part, participation_reasons=[["r"]] * 4,
                data_asof_utc="2026-10-15T23:00:00Z")
    st = [r["status"] for r in res]
    assert st[0] == "BLOCK"
    assert st[1] == "REVIEW" and st[2] == "REVIEW"
    assert st[3] != "BLOCK"
