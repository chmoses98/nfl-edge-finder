"""PURE shadow collector: freezing, point-in-time and write-once guards, market isolation, immutability.

Synthetic nflverse-shaped inputs (no network). These prove properties of the CODE PATH; the collected evidence is the
store on the market-data branch, never these fixtures.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nfl_edge.engines.player.pure_v1 import BASELINE_NAME, MODEL_NAME  # noqa: E402
from nfl_edge.engines.player.pure_v1 import data as PD  # noqa: E402
from nfl_edge.engines.player.pure_v1 import features as PF  # noqa: E402
from nfl_edge.engines.player.pure_v1 import pipeline as PP  # noqa: E402
from nfl_edge.shadow_pure import collect as C  # noqa: E402
from nfl_edge.shadow_pure import evaluate as E  # noqa: E402
from nfl_edge.shadow_pure import frozen, prospective, store  # noqa: E402
from test_pure_player_v1 import _box, _schedule  # noqa: E402

LAST_SEASON, LAST_WEEK = 2017, 10


# ------------------------------------------------------------------------------------------------ fixtures
@pytest.fixture(scope="module")
def world():
    rng = np.random.default_rng(23)
    sched = _schedule(rng)
    stats, snaps = _box(sched, rng)
    return sched, stats, snaps


def _pq(df, path):
    """Write parquet through polars (CI installs no pyarrow)."""
    import polars as pl
    pl.DataFrame({c: df[c].tolist() for c in df.columns}).write_parquet(path)


def _write_root(root, sched, stats, snaps, *, fetched_at, future_week=(LAST_SEASON, LAST_WEEK)):
    """An nflverse-shaped data root whose last week is unplayed, plus the downloader's provenance manifest."""
    s, w = future_week
    sched = sched.copy()
    fut = (sched.season == s) & (sched.week == w)
    sched.loc[fut, ["home_score", "away_score"]] = np.nan
    stats = stats[~stats.game_id.isin(sched.loc[fut, "game_id"])].copy()
    snaps = snaps[~snaps.game_id.isin(sched.loc[fut, "game_id"])].copy()
    nv = os.path.join(root, "data", "raw", "nflverse")
    for d in ("schedules", "stats_player", "snap_counts", "players"):
        os.makedirs(os.path.join(nv, d), exist_ok=True)
    paths = []
    p = os.path.join(nv, "schedules", "games.csv"); sched.to_csv(p, index=False); paths.append(p)
    stats = stats.assign(season_type="REG")
    sn = snaps.assign(game_type="REG", pfr_player_id="pfr_" + snaps.player_id, player=snaps.player_display_name,
                      opponent=snaps.opponent_team)
    for season in sorted(sched.season.unique()):
        p = os.path.join(nv, "stats_player", f"stats_player_week_{season}.parquet")
        _pq(stats[stats.season == season], p); paths.append(p)
        p = os.path.join(nv, "snap_counts", f"snap_counts_{season}.parquet")
        _pq(sn[sn.season == season][["pfr_player_id", "player", "position", "season", "week", "game_id", "team", "opponent",
                                     "offense_snaps", "game_type"]], p); paths.append(p)
    ids = sorted(set(stats.player_id) | set(snaps.player_id))
    p = os.path.join(nv, "players", "players.parquet")
    _pq(pd.DataFrame({"gsis_id": ids, "pfr_id": ["pfr_" + i for i in ids]}), p); paths.append(p)
    with open(os.path.join(nv, "_manifest.jsonl"), "w") as fh:
        for p in paths:
            rel = os.path.relpath(p, root).replace(os.sep, "/")
            fh.write(json.dumps({"path": rel, "url": f"https://example.invalid/{os.path.basename(p)}", "retrieved_at": fetched_at.isoformat(),
                                 "sha256": store.sha256_file(p), "status": 200}) + "\n")
    return sched


def _kick(sched, s=LAST_SEASON, w=LAST_WEEK):
    g = PD.sports_schedule(sched)
    return g[(g.season == s) & (g.week == w)].kickoff.min()


@pytest.fixture(scope="module")
def root(tmp_path_factory, world):
    sched, stats, snaps = world
    r = str(tmp_path_factory.mktemp("nflroot"))
    k = _kick(sched)
    sch = _write_root(r, sched, stats, snaps, fetched_at=(k - pd.Timedelta(hours=10)).to_pydatetime())
    return r, sch, k


def _gate():
    return C.gate()


# ------------------------------------------------------------------------------------------------ vendoring / freezing
def test_vendored_gate_matches_its_pinned_hashes():
    vf = open(os.path.join(ROOT, "tools", "pure_gate", "VENDORED_FROM")).read()
    for rel in ("pure_gate.py", "schema/pure_forecast.v1.schema.json"):
        got = hashlib.sha256(open(os.path.join(ROOT, "tools", "pure_gate", rel), "rb").read()).hexdigest()
        assert f"{got}  {rel}" in vf, f"vendored {rel} was edited (sha256 {got})"


def test_pure_v1_code_is_the_frozen_code(monkeypatch):
    assert frozen.assert_frozen().startswith("sha256:")
    monkeypatch.setattr(frozen, "PURE_V1_CODE_SHA256", "0" * 64)
    with pytest.raises(frozen.FrozenModelChanged):
        frozen.assert_frozen()


# ------------------------------------------------------------------------------------------------ store
def test_write_once_refuses_overwrite(tmp_path):
    w = store.RunWriter(str(tmp_path), "20260101T000000Z")
    w.write("a/x.json", b"1")
    with pytest.raises(store.ImmutableStoreError):
        w.write("a/x.json", b"2")
    w.seal()
    with pytest.raises(store.ImmutableStoreError):
        store.RunWriter(str(tmp_path), "20260101T000000Z").seal()


def test_hash_chain_detects_modification_deletion_and_unlisted(tmp_path):
    r = str(tmp_path)
    for i, run in enumerate(("20260101T000000Z", "20260102T000000Z")):
        w = store.RunWriter(r, run); w.write(f"p/{run}.json", f"{i}".encode()); w.seal()
    assert store.verify_store(r) == []
    m2 = json.load(open(os.path.join(r, "manifests", "20260102T000000Z.manifest.json")))
    assert m2["prev_manifest_sha256"] == store.sha256_file(os.path.join(r, "manifests", "20260101T000000Z.manifest.json"))
    open(os.path.join(r, "p", "20260101T000000Z.json"), "w").write("tampered")
    os.remove(os.path.join(r, "p", "20260102T000000Z.json"))
    open(os.path.join(r, "p", "sneaky.json"), "w").write("x")
    probs = {p["path"]: p["problem"] for p in store.verify_store(r)}
    assert probs["p/20260101T000000Z.json"].startswith("MODIFIED")
    assert probs["p/20260102T000000Z.json"].startswith("DELETED")
    assert probs["p/sneaky.json"].startswith("UNLISTED")
    # editing an older manifest breaks the chain of the next one
    p1 = os.path.join(r, "manifests", "20260101T000000Z.manifest.json")
    open(p1, "a").write(" ")
    assert any("chain broken" in p["problem"] for p in store.verify_store(r))


def test_publish_must_be_additive(tmp_path):
    loc, pub = tmp_path / "loc", tmp_path / "pub"
    (loc / "a").mkdir(parents=True); (pub / "a").mkdir(parents=True)
    (loc / "a" / "same").write_text("1"); (pub / "a" / "same").write_text("1")
    (loc / "a" / "new").write_text("n")
    assert store.check_publish_is_additive(str(loc), str(pub)) == []
    (loc / "a" / "same").write_text("2")
    assert store.check_publish_is_additive(str(loc), str(pub))[0]["path"] == os.path.join("a", "same")


def test_git_history_scan_catches_modify_and_delete(tmp_path):
    def sh(c):
        subprocess.run(c, cwd=tmp_path, shell=True, check=True, capture_output=True)
    sh("git init -q && git config user.email t@t && git config user.name t")
    os.makedirs(tmp_path / "data" / "shadow_pure")
    (tmp_path / "data" / "shadow_pure" / "a.json").write_text("1"); (tmp_path / "data" / "shadow_pure" / "b.json").write_text("1")
    sh("git add -A && git commit -q -m add")
    assert store.scan_git_history(str(tmp_path), "data/shadow_pure") == []
    (tmp_path / "data" / "shadow_pure" / "a.json").write_text("2"); os.remove(tmp_path / "data" / "shadow_pure" / "b.json")
    sh("git add -A && git commit -q -m edit")
    st = sorted(v["status"] for v in store.scan_git_history(str(tmp_path), "data/shadow_pure"))
    assert st == ["D", "M"]


# ------------------------------------------------------------------------------------------------ prospective path
def test_prospective_path_reproduces_the_backtest_forecasts(world):
    sched, stats, snaps = world
    pg = PD.build_player_games(stats, snaps, PD.sports_schedule(sched))
    rows, t = PF.build(pg)
    bt = PP.run(rows, t, LAST_SEASON, weeks=[LAST_WEEK])
    g = PD.sports_schedule(sched)
    wk = g[(g.season == LAST_SEASON) & (g.week == LAST_WEEK)]
    as_of = wk.kickoff.min() - pd.Timedelta(hours=2)
    games = prospective.upcoming_games(g, as_of.to_pydatetime())
    syn = prospective.candidates(pg, games, as_of)
    r2, t2 = prospective.build(pg, syn, as_of)
    m, b = prospective.fit(r2, t2, LAST_SEASON)
    fc = prospective.forecast(r2, t2, m, b, as_of)
    for arm in (MODEL_NAME, BASELINE_NAME):
        j = bt["player"][arm].merge(fc["arms"][arm], on=["game_id", "player_id", "statistic"], suffixes=("_b", "_p"))
        assert len(j) > 100
        assert np.allclose(j.mean_b, j.mean_p, rtol=0, atol=1e-9)


def test_forecast_refuses_rows_at_or_after_kickoff(world):
    sched, stats, snaps = world
    pg = PD.build_player_games(stats, snaps, PD.sports_schedule(sched))
    g = PD.sports_schedule(sched)
    wk = g[(g.season == LAST_SEASON) & (g.week == LAST_WEEK)]
    as_of = wk.kickoff.min() - pd.Timedelta(hours=2)
    syn = prospective.candidates(pg, prospective.upcoming_games(g, as_of.to_pydatetime()), as_of)
    r2, t2 = prospective.build(pg, syn, as_of)
    m, b = prospective.fit(r2, t2, LAST_SEASON)
    with pytest.raises(prospective.PreKickoffError):
        prospective.forecast(r2, t2, m, b, wk.kickoff.max() + pd.Timedelta(minutes=1))


def test_only_each_teams_next_game_is_forecast(world):
    sched, _, _ = world
    g = PD.sports_schedule(sched)
    as_of = g[(g.season == LAST_SEASON) & (g.week == LAST_WEEK - 1)].kickoff.min() - pd.Timedelta(hours=2)
    up = prospective.upcoming_games(g, as_of.to_pydatetime(), horizon_hours=24 * 30)
    assert set(up.week) == {LAST_WEEK - 1}


# ------------------------------------------------------------------------------------------------ end to end
def _md_root(tmp, sched, as_of, mode="normal"):
    """A market-data-shaped dir: one capture quote file for the upcoming games (normal / randomised)."""
    if mode == "removed":
        return None
    d = os.path.join(tmp, f"md_{mode}", "data", "kalshi", "capture", as_of.strftime("%Y-%m-%d"))
    os.makedirs(d, exist_ok=True)
    rng = np.random.default_rng(5 if mode == "normal" else 99)
    g = PD.sports_schedule(sched)
    up = g[(g.season == LAST_SEASON) & (g.week == LAST_WEEK)]
    run = (as_of - timedelta(minutes=30)).strftime("%Y%m%dT%H%M%SZ")
    with open(os.path.join(d, f"{run}.quotes.jsonl"), "w") as fh:
        for x in up.itertuples():
            fh.write(json.dumps({"run_id": run, "observed_at": (as_of - timedelta(minutes=30)).isoformat(), "family": "PLAYER_STAT",
                                 "stat": "receptions", "game_id": x.game_id, "ticker": f"T-{x.game_id}-4", "threshold": 4,
                                 "player_kalshi_id": f"k-{x.home_team}-WR0", "open_time": (as_of - timedelta(days=1)).isoformat(),
                                 "yes_bid_dollars": f"{rng.uniform(0, .5):.2f}", "yes_ask_dollars": f"{rng.uniform(.5, 1):.2f}"}) + "\n")
    return os.path.join(tmp, f"md_{mode}")


def _pure_bytes(store_root):
    out = {}
    for dp, _d, fs in os.walk(os.path.join(store_root, "projections")):
        for f in fs:
            out[f.split(".", 1)[1]] = gzip.open(os.path.join(dp, f)).read()
    return out


def test_capture_end_to_end_validates_is_idempotent_and_market_independent(root, tmp_path):
    r, sched, k = root
    now = (k - pd.Timedelta(hours=5)).to_pydatetime()         # MORNING_OF window
    stores, market = {}, {}
    for mode in ("normal", "removed", "randomized"):
        st = str(tmp_path / f"store_{mode}")
        s = C.run_capture(r, st, now=now, md_root=_md_root(str(tmp_path), sched, now, mode), log=lambda *_: None)
        assert s["rows"][MODEL_NAME]["validate"]["passed"] and s["rows"][MODEL_NAME]["n"] > 50
        assert {c["kind"] for c in s["captured"]} == {"MORNING_OF"}
        assert store.verify_store(st) == []
        stores[mode] = _pure_bytes(st)
        market[mode] = [x for x in E.store.read_jsonl(next(
            os.path.join(dp, f) for dp, _d, fs in os.walk(os.path.join(st, "market")) for f in fs if "kalshi_listings" in f))]
    # PURE projection files are byte-identical with market inputs present, removed and randomised ...
    assert stores["normal"] == stores["removed"] == stores["randomized"]
    # ... while the separate market family responds to the same mutations (the test has power)
    assert market["normal"] and not market["removed"] and market["normal"] != market["randomized"]
    # idempotent: the same window is not captured twice
    assert C.run_capture(r, str(tmp_path / "store_normal"), now=now + timedelta(seconds=1))["state"] == "NOTHING_DUE"


def test_capture_refuses_inputs_fetched_after_as_of(root, tmp_path):
    r, sched, k = root
    early = (k - pd.Timedelta(hours=26)).to_pydatetime()      # DAY_BEFORE window, but files were fetched at k - 10h
    with pytest.raises(Exception, match="not before as_of"):
        C.run_capture(r, str(tmp_path / "s"), now=early, log=lambda *_: None)


def test_nothing_is_captured_at_or_after_kickoff(root, tmp_path):
    r, sched, k = root
    now = (k + pd.Timedelta(minutes=1)).to_pydatetime()       # the early games have kicked off, the late ones not
    s = C.run_capture(r, str(tmp_path / "s"), now=now, adhoc_games="ALL", log=lambda *_: None)
    assert s["captured"] and all(pd.Timestamp(c["kickoff"]) > pd.Timestamp(now) for c in s["captured"])
    rows = [x for dp, _d, fs in os.walk(tmp_path / "s" / "projections") for f in fs for x in store.read_jsonl(os.path.join(dp, f))]
    assert rows and all(pd.Timestamp(x["kickoff"]) > pd.Timestamp(x["as_of"]) >= pd.Timestamp(x["source_max_observed_at"]) for x in rows)
    late = PD.sports_schedule(sched).kickoff.max() + pd.Timedelta(minutes=1)
    assert C.run_capture(r, str(tmp_path / "s2"), now=late.to_pydatetime(), adhoc_games="ALL")["state"] in ("NOTHING_DUE", "NO_UPCOMING_GAMES")
    assert not os.path.exists(tmp_path / "s2" / "projections")


def test_pure_modules_never_import_the_market_families():
    for mod in ("prospective.py", "records.py", "frozen.py", "inputs.py"):
        src = open(os.path.join(ROOT, "nfl_edge", "shadow_pure", mod)).read().lower()
        assert "shadow_pure import market" not in src and "kalshi" not in src.replace("kalshi-free", ""), mod


def test_settle_and_evaluate_scores_full_population_and_listed_cohort(root, tmp_path, world):
    r, sched, k = root
    now = (k - pd.Timedelta(hours=1)).to_pydatetime()         # FINAL_T90 window
    st = str(tmp_path / "st")
    C.run_capture(r, st, now=now, md_root=_md_root(str(tmp_path), sched, now), log=lambda *_: None)
    # the games are played: publish the full box scores into a second root (fetched after the games)
    _, stats, snaps = world
    r2 = str(tmp_path / "root2")
    later = (k + pd.Timedelta(days=1)).to_pydatetime()
    _write_root(r2, world[0], stats, snaps, fetched_at=later - timedelta(hours=1), future_week=(0, 0))
    s = E.settle_and_evaluate(r2, st, _gate(), now=later, bootstrap=50)
    assert s["new_outcomes"] > 50
    ev = json.load(open(next(os.path.join(dp, f) for dp, _d, fs in os.walk(os.path.join(st, "evaluations")) for f in fs)))
    full = ev["scorecards"]["FINAL_T90/full_eligible_population"]
    assert full["coverage"]["settled_with_both_forecasts"] > 50
    assert "FINAL_T90/pregame_market_listed_cohort" in ev["scorecards"]
    assert store.verify_store(st) == []
    assert E.settle_and_evaluate(r2, st, _gate(), now=later + timedelta(hours=1))["state"] == "NOTHING_NEW"
