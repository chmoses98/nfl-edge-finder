"""Prospective integrity of the three-arm snapshot: gates, identity, idempotency, isolation from the incumbent."""
import glob
import gzip
import json
import os
from datetime import datetime, timedelta, timezone

import numpy as np
import polars as pl
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from nfl_edge.arms import data_only as D, records as REC, registry as R                     # noqa: E402
from nfl_edge.arms.snapshot import build_snapshot                                             # noqa: E402
from nfl_edge.pricing.game_env import simulate_game                            # noqa: E402
from nfl_edge.shadow.ledger import Observation                                                # noqa: E402
from test_three_arm_data_only import synthetic_team_games                                     # noqa: E402

KICKOFF = datetime(2026, 9, 13, 17, 0, tzinfo=timezone.utc)
OBSERVED = datetime(2026, 9, 12, 17, 0, tzinfo=timezone.utc)


def schedule(seed=0):
    """A synthetic schedule: enough settled 2016-2025 games for a residual bank, plus the 2026 slate."""
    rng = np.random.default_rng(seed)
    rows = []
    for s in range(2016, 2026):
        for w in range(1, 19):
            for i in range(4):
                sp = float(rng.choice([-7, -3.5, -3, -1.5, 0, 1, 2.5, 3, 3.5, 7])); tl = float(rng.choice([41.5, 44, 45.5, 47, 49.5]))
                h, a = int(rng.poisson(23)), int(rng.poisson(21))
                rows.append({"game_id": f"{s}_{w:02d}_X{i}_Y{i}", "season": s, "week": w, "game_type": "REG", "gameday": f"{s}-10-01",
                             "gametime": "13:00", "home_team": "A", "away_team": "B", "home_score": h, "away_score": a, "result": h - a,
                             "total": h + a, "overtime": 0, "spread_line": sp, "total_line": tl, "home_rest": 7, "away_rest": 7,
                             "div_game": 0, "location": "Home", "roof": "outdoors", "home_moneyline": -120, "away_moneyline": 100})
    # the synthetic team-game league's own games, so the cutoff rule finds them final
    tg = synthetic_team_games().filter(pl.col("is_home")).unique(subset=["game_id"], maintain_order=True)
    for r in tg.iter_rows(named=True):
        rows.append({"game_id": r["game_id"], "season": r["season"], "week": r["week"], "game_type": "REG", "gameday": f"{r['season']}-10-01",
                     "gametime": "13:00", "home_team": r["team"], "away_team": r["opp"], "home_score": 24, "away_score": 20, "result": 4,
                     "total": 44, "overtime": 0, "spread_line": 2.5, "total_line": 44.5, "home_rest": 7, "away_rest": 7, "div_game": 0,
                     "location": "Home", "roof": "outdoors", "home_moneyline": -120, "away_moneyline": 100})
    for gid, h, a in (("2026_02_B_A", "A", "B"), ("2026_02_D_C", "C", "D")):
        rows.append({"game_id": gid, "season": 2026, "week": 2, "game_type": "REG", "gameday": "2026-09-13", "gametime": "13:00",
                     "home_team": h, "away_team": a, "home_score": None, "away_score": None, "result": None, "total": None,
                     "overtime": None, "spread_line": 3.0, "total_line": 44.5, "home_rest": 7, "away_rest": 7, "div_game": 1,
                     "location": "Home", "roof": "dome", "home_moneyline": -150, "away_moneyline": 130})
    return pl.DataFrame(rows)


def env(games, *, kickoff=KICKOFF, observed=OBSERVED):
    return {"run_id": observed.strftime("%Y%m%dT%H%M%SZ"), "capture_finished_at": observed.isoformat(), "target_season": 2026,
            "game_env_version": "game_env-0.2.0", "n_sims": R.N_SIMS,
            "residual_bank": {"season_lo": 2016, "halflife_seasons": 3.0, "n_pairs": int(games.filter(pl.col("result").is_not_null()).height)},
            "games": {gid: {"spread_home": 3.0, "total": 44.5, "source": "kalshi_implied", "kalshi_implied_spread": 3.0,
                            "kalshi_implied_total": 44.5, "implied_diag": {"n_liquid_rungs": 12}, "fallback_reason": None,
                            "consensus_spread_line": 3.0, "consensus_total_line": 44.5, "home": h, "away": a, "season": 2026,
                            "week": 2, "kickoff_utc": kickoff.isoformat(), "n_sims": R.N_SIMS}
                      for gid, h, a in (("2026_02_B_A", "A", "B"), ("2026_02_D_C", "C", "D"))},
            "games_without_environment": {}}


def rows_for(gid, home, away, observed=OBSERVED, kickoff=KICKOFF, incumbent_cv=None):
    mtk = (kickoff - observed).total_seconds() / 60
    base = dict(run_id=observed.strftime("%Y%m%dT%H%M%SZ"), observed_at=observed.isoformat(), game_id=gid, kickoff_utc=kickoff.isoformat(),
                minutes_to_kickoff=mtk, support_state="SUPPORTED", period="FULL", direction="YES", yes_bid=0.5, yes_ask=0.52, no_bid=0.48,
                no_ask=0.5, mid=0.51, quote_width=0.02, volume=100.0, open_interest=50.0, liquidity=10.0)
    out = [dict(base, ticker=f"W-{gid}-{home}", family="GAME_WINNER", team=home, operator="event", prediction_id="p1"),
           dict(base, ticker=f"S-{gid}-{home}3", family="SPREAD", team=home, floor_strike=3.5, operator=">", prediction_id="p2"),
           dict(base, ticker=f"T-{gid}-45", family="TOTAL", threshold=45, operator=">=", prediction_id="p3"),
           dict(base, ticker=f"TT-{gid}-{away}21", family="TEAM_TOTAL", team=away, threshold=21, operator=">=", prediction_id="p4"),
           dict(base, ticker=f"P-{gid}-x", family="PLAYER_STAT", stat="receptions", threshold=4, prediction_id="p5"),
           dict(base, ticker=f"S1H-{gid}", family="SPREAD", team=home, floor_strike=1.5, period="1H", support_state="UNSUPPORTED_MODEL", prediction_id="p6")]
    if incumbent_cv:
        for r in out:
            r["model_contract_value"] = incumbent_cv.get(r["family"])
    return out


def inputs_for(games):
    return {"rows": D.prepare_team_games(synthetic_team_games()), "games": games, "unavailable": [],
            "team_game_history_sha": "x", "games_sha": "y", "current_season_pbp_sha": None, "current_season_team_games": 0}


def ledger_for(games, rows, e=None):
    return {"observations": None, "rows": rows, "game_env": e or env(games), "manifest": {}, "stem": "t", "run_id": (e or env(games))["run_id"],
            "model_version": "test"}


def build(games=None, rows=None, now=None, **kw):
    games = games if games is not None else schedule()
    rows = rows if rows is not None else rows_for("2026_02_B_A", "A", "B") + rows_for("2026_02_D_C", "C", "D")
    return build_snapshot(root=ROOT, ledger=ledger_for(games, rows, kw.pop("env", None)), now=now or OBSERVED + timedelta(minutes=5),
                          target_season=2026, n_sims=kw.pop("n_sims", 4000), inputs=inputs_for(games), verbose=lambda *_: None, **kw)


def test_a_snapshot_observed_after_kickoff_is_excluded_with_no_forecast():
    games = schedule()
    e = env(games, observed=KICKOFF + timedelta(minutes=1))
    snap = build(games, rows_for("2026_02_B_A", "A", "B", observed=KICKOFF + timedelta(minutes=1)), env=e,
                 now=KICKOFF + timedelta(minutes=6))
    assert {g["status"] for g in snap["games"]} == {R.POST_KICKOFF_EXCLUDED}
    assert all(not g["arms"] and not g["prekickoff"] for g in snap["games"]) and snap["contracts"] == []


def test_a_snapshot_generated_after_kickoff_is_excluded_even_from_a_pregame_capture():
    """The wall clock is a gate too: a pregame capture built after kickoff is a reconstruction."""
    snap = build(now=KICKOFF + timedelta(minutes=1), max_lag_min=10 ** 6)
    assert {g["status"] for g in snap["games"]} == {R.POST_KICKOFF_EXCLUDED}
    assert all("generated after kickoff" in g["status_reason"] for g in snap["games"])


def test_a_capture_far_older_than_the_generation_lag_is_refused_as_a_reconstruction():
    with pytest.raises(ValueError, match="reconstruction"):
        build(now=OBSERVED + timedelta(hours=5))


def test_the_completed_opener_cannot_be_inserted_after_the_fact():
    games = schedule()
    ko = datetime.fromisoformat(R.FIRST_2026_KICKOFF_UTC)
    e = env(games, kickoff=ko, observed=ko - timedelta(hours=2))
    with pytest.raises(ValueError):                       # generated now, observed before an old kickoff: refused outright
        build(games, rows_for("2026_02_B_A", "A", "B", observed=ko - timedelta(hours=2), kickoff=ko), env=e,
              now=datetime(2026, 9, 12, tzinfo=timezone.utc))
    snap = build(games, rows_for("2026_02_B_A", "A", "B", observed=ko - timedelta(hours=2), kickoff=ko), env=e,
                 now=datetime(2026, 9, 12, tzinfo=timezone.utc), max_lag_min=10 ** 9)
    assert {g["status"] for g in snap["games"]} == {R.POST_KICKOFF_EXCLUDED}


def test_all_three_arms_are_simulated_on_one_set_of_draws_with_forty_thousand_rows():
    snap = build(n_sims=R.N_SIMS)
    g = snap["games"][0]
    assert g["simulation"]["n_sims"] == 40000
    shas = {a["simulation"]["residual_idx_sha"] for a in g["arms"].values() if a["status"] != R.UNAVAILABLE}
    classes = {tuple(a["simulation"]["fractional_class"]) for a in g["arms"].values() if a["status"] != R.UNAVAILABLE}
    assert len(shas) == len(classes), "arms in the same fractional class must share residual draws exactly"
    assert g["simulation"]["uniform_draws_sha"] and g["simulation"]["seed_key"].endswith(R.CRN_VERSION)


def test_the_hybrid_is_seventy_thirty_in_the_home_minus_away_convention():
    snap = build()
    for g in snap["games"]:
        cur, do, hy = (g["arms"][a] for a in R.PRIMARY_ARMS)
        assert hy["projected_home_margin"] == pytest.approx(0.7 * cur["projected_home_margin"] + 0.3 * do["projected_home_margin"])
        assert hy["projected_total"] == pytest.approx(0.7 * cur["projected_total"] + 0.3 * do["projected_total"])
        assert hy["detail"]["weight_market"] == 0.7 and hy["detail"]["weight_data"] == 0.3
        assert cur["implied_home_score"] - cur["implied_away_score"] == pytest.approx(cur["projected_home_margin"])


def test_a_missing_data_only_stays_missing_and_takes_the_hybrid_with_it():
    snap = build(artifact_path="/nonexistent/artifact.json")
    for g in snap["games"]:
        assert g["arms"][R.DATA_ONLY]["status"] == R.UNAVAILABLE and g["arms"][R.DATA_ONLY]["projected_home_margin"] is None
        assert g["arms"][R.HYBRID]["status"] == R.UNAVAILABLE and "no fallback" in g["arms"][R.HYBRID]["unavailable_reason"]
        assert g["arms"][R.CURRENT]["status"] == R.OK
    for c in snap["contracts"]:
        assert c["p_current"] is not None and c["p_data_only"] is None and c["p_hybrid"] is None
        assert c["arm_status"][R.DATA_ONLY] == R.UNAVAILABLE


def test_the_contract_universe_is_the_incumbents_supported_game_contracts_only():
    snap = build()
    fams = {c["family"] for c in snap["contracts"]}
    assert fams == {"GAME_WINNER", "SPREAD", "TOTAL", "TEAM_TOTAL"}
    assert all(c["period"] in ("FULL", None) for c in snap["contracts"])
    assert snap["games"][0]["contract_skip_reasons"] == {"UNSUPPORTED_MODEL": 1}


def test_the_reproduction_check_flags_an_incumbent_the_harness_cannot_reproduce():
    games = schedule()
    from nfl_edge.arms import incumbent_center as IC
    bank, _meta = IC.incumbent_bank(games, 2026)
    bank.rng = np.random.default_rng(5)
    sim = simulate_game(3.0, 44.5, bank, n=40000)
    honest = {"GAME_WINNER": float(np.mean(sim["margin"] > 0)) + 0.5 * float(np.mean(sim["margin"] == 0)),
              "SPREAD": float(np.mean(sim["margin"] > 3.5)), "TOTAL": float(np.mean(sim["total"] >= 45)),
              "TEAM_TOTAL": float(np.mean(sim["away"] >= 21))}
    ok = build(games, rows_for("2026_02_B_A", "A", "B", incumbent_cv=honest), n_sims=40000)
    assert ok["games"][0]["reproduction_check"]["ok"] and ok["games"][0]["arms"][R.CURRENT]["status"] == R.OK
    liar = {k: v + 0.2 for k, v in honest.items()}
    bad = build(games, rows_for("2026_02_B_A", "A", "B", incumbent_cv=liar), n_sims=40000)
    assert not bad["games"][0]["reproduction_check"]["ok"] and bad["games"][0]["arms"][R.CURRENT]["status"] == R.DEGRADED


def test_rerun_is_a_no_op_and_a_contradiction_fails_closed(tmp_path):
    snap = build()
    w = REC.ArmsWriter(str(tmp_path), snap["run_id"])
    assert w.write(snap["games"], snap["contracts"])["status"] == "WRITTEN"
    digest = {p: open(p, "rb").read() for p in glob.glob(str(tmp_path / "**" / "*"), recursive=True) if os.path.isfile(p)}
    again = build()                                       # a fresh build, different wall clock, same claims
    assert REC.ArmsWriter(str(tmp_path), again["run_id"]).write(again["games"], again["contracts"])["status"] == "NO_OP"
    assert {p: open(p, "rb").read() for p in digest} == digest
    again["games"][0]["arms"][R.DATA_ONLY]["projected_home_margin"] += 1.0
    with pytest.raises(REC.ArmsConflict):
        REC.ArmsWriter(str(tmp_path), again["run_id"]).write(again["games"], again["contracts"])
    assert {p: open(p, "rb").read() for p in digest} == digest
    assert REC.verify_snapshots([str(tmp_path)])["ok"]


def test_a_missed_horizon_is_never_reconstructed():
    from nfl_edge.arms.horizons import captured_state
    from nfl_edge.handicap.horizons import due_horizons
    games = [{"game_id": "g", "kickoff_utc": KICKOFF.isoformat()}]
    out = due_horizons("2026-REG-02", games, KICKOFF + timedelta(minutes=1), captured_state([]))
    assert not out["should_run"] and len(out["missed"]) == 4 and not out["due"]
    out = due_horizons("2026-REG-02", games, KICKOFF - timedelta(minutes=40), captured_state(["2026-REG-02__20260913T1700Z__T-90m.json"]))
    assert [d["horizon_min"] for d in out["due"]] == [360, 1440], "late horizons stay due until kickoff, never after"
    markers = [f"2026-REG-02__20260913T1700Z__T-{h}m.json" for h in (1440, 360, 90)]
    out = due_horizons("2026-REG-02", games, KICKOFF - timedelta(minutes=25), captured_state(markers))
    assert [d["horizon_min"] for d in out["due"]] == [30]


def test_existing_incumbent_ledger_rows_remain_valid_under_the_new_schema():
    files = sorted(glob.glob(os.path.join(ROOT, "data", "shadow", "ledger", "*", "*.observations.jsonl.gz")))
    assert files, "the repository carries no committed ledger snapshot to check against"
    n = 0
    for line in gzip.open(files[0], "rt"):
        row = json.loads(line)
        o = Observation(**row)                     # the frozen 1.0.0 schema, untouched by this branch
        d = o.to_dict()
        assert all(d[k] == v for k, v in row.items())
        n += 1
        if n > 200:
            break
    assert n > 0


def test_the_packet_and_the_settle_job_can_never_read_a_three_arm_file(tmp_path):
    """The challengers live in data/shadow/arms with their own suffixes; the ledger globs cannot match them."""
    from nfl_edge.handicap.packet import load_latest_ledger
    md = tmp_path / "md"
    (md / "data" / "shadow" / "arms" / "2026-09-12").mkdir(parents=True)
    for suffix in ("arm_games", "arm_contracts"):
        with gzip.open(md / "data" / "shadow" / "arms" / "2026-09-12" / f"20260912T170000Z.three-arm-1.0.0.{suffix}.jsonl.gz", "wt") as f:
            f.write("{}\n")
    with pytest.raises(FileNotFoundError):
        load_latest_ledger(str(md))
    import importlib.util
    spec = importlib.util.spec_from_file_location("_sg", os.path.join(ROOT, "scripts", "shadow", "settle_games.py"))
    sg = importlib.util.module_from_spec(spec); spec.loader.exec_module(sg)
    assert sg.ledger_files(str(md)) == []


def test_an_exact_replay_of_the_incumbent_simulation_is_verified_and_a_wrong_one_is_flagged():
    """The CURRENT centre's provenance claim is checked, never asserted: the replayed 40,000-row simulation must
    reproduce the incumbent's ledger price exactly; a replay that does not is `replay_mismatch` and DEGRADED."""
    from nfl_edge.arms import incumbent_center as IC
    games = schedule()
    bank, _meta = IC.incumbent_bank(games, 2026)
    bank.rng = np.random.default_rng(IC.BANK_SEED)
    sim = simulate_game(3.0, 44.5, bank, n=40000)
    ledger_cv = {"GAME_WINNER": float(np.mean(sim["margin"] > 0)) + 0.5 * float(np.mean(sim["margin"] == 0)),
                 "SPREAD": float(np.mean(sim["margin"] > 3.5)), "TOTAL": float(np.mean(sim["total"] >= 45)),
                 "TEAM_TOTAL": float(np.mean(sim["away"] >= 21))}
    rows = rows_for("2026_02_B_A", "A", "B", incumbent_cv=ledger_cv)
    e = env(games)
    ledger = dict(ledger_for(games, rows, e), sims={"2026_02_B_A": sim}, bank=bank)
    snap = build_snapshot(root=ROOT, ledger=ledger, now=OBSERVED + timedelta(minutes=5), target_season=2026, n_sims=4000,
                          inputs=inputs_for(games), verbose=lambda *_: None)
    g = snap["games"][0]
    assert g["reproduction_check"]["replay"]["quality"] == IC.EXACT_VERIFIED
    assert g["reproduction_check"]["replay"]["max_abs_diff"] == 0.0
    assert g["arms"][R.CURRENT]["detail"]["reproduction_quality"] == IC.EXACT_VERIFIED
    wrong = dict(ledger, sims={"2026_02_B_A": simulate_game(3.0, 44.5, bank, n=40000)})    # a different stream
    snap = build_snapshot(root=ROOT, ledger=wrong, now=OBSERVED + timedelta(minutes=5), target_season=2026, n_sims=4000,
                          inputs=inputs_for(games), verbose=lambda *_: None)
    g = snap["games"][0]
    assert g["reproduction_check"]["replay"]["quality"] == IC.MISMATCH and g["arms"][R.CURRENT]["status"] == R.DEGRADED
    nolegder = dict(ledger, rows=rows_for("2026_02_B_A", "A", "B"))
    g = build_snapshot(root=ROOT, ledger=nolegder, now=OBSERVED + timedelta(minutes=5), target_season=2026, n_sims=4000,
                       inputs=inputs_for(games), verbose=lambda *_: None)["games"][0]
    assert g["reproduction_check"]["replay"]["quality"] == IC.EXACT_UNVERIFIED
