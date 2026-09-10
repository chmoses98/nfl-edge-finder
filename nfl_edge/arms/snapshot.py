"""Build one three-arm snapshot from one incumbent ledger snapshot. The incumbent is read, never rerun.

Inputs (all already on disk when the pricer has just run):
    <ledger_dir>/<day>/<run>.<model>.observations.jsonl.gz   the market the incumbent saw, and its own prices
    <ledger_dir>/<day>/<run>.<model>.game_env.json           the EXACT centre each game was priced from
    data/silver/{team_game,games}.parquet + bronze pbp        the football data DATA_ONLY rates teams from
    research/three_arm/data_only_artifact_<season>.json      the frozen football-only model

For every game with a pregame market snapshot:
    CURRENT      centre from the sidecar (Kalshi-implied, or the documented consensus fallback)
    DATA_ONLY    centre from ratings at the capture cutoff through the frozen artifact -- or UNAVAILABLE
    HYBRID_30    0.70 x CURRENT + 0.30 x DATA_ONLY                             -- or UNAVAILABLE
then ONE set of uniforms, three simulations of N_SIMS draws, and every game contract the incumbent priced is
priced again under each arm. The incumbent's own number for the same ticker is carried alongside and the
CURRENT arm is checked against it (a reproduction check, Monte Carlo tolerance).

The prekickoff gate is unconditional: a game whose kickoff is not strictly after both the capture time and
the wall clock is written as POST_KICKOFF_EXCLUDED with no forecast at all.
"""
from __future__ import annotations

import glob
import gzip
import json
import math
import os
import subprocess
from datetime import datetime, timedelta, timezone

import numpy as np
import polars as pl

from nfl_edge.arms import crn, data_only as DO, pricing as P, records as REC, registry as R
from nfl_edge.pricing.game_env import ResidualBank


def _dt(s):
    if not s:
        return None
    d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def code_sha(root: str) -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        return None


def find_ledger_snapshot(ledger_dir: str, run_id: str | None = None) -> dict:
    """The newest (or the named) ledger snapshot that HAS a game_env sidecar. No sidecar, no experiment."""
    files = sorted(glob.glob(os.path.join(ledger_dir, "*", "*.observations.jsonl.gz")))
    if run_id:
        files = [f for f in files if os.path.basename(f).startswith(run_id + ".")]
    if not files:
        raise FileNotFoundError(f"no ledger snapshot under {ledger_dir}" + (f" for run {run_id}" if run_id else ""))
    path = files[-1]
    stem = os.path.basename(path).replace(".observations.jsonl.gz", "")
    env_path = os.path.join(os.path.dirname(path), f"{stem}.game_env.json")
    man_path = os.path.join(os.path.dirname(path), f"{stem}.ledger_manifest.json")
    if not os.path.exists(env_path):
        raise FileNotFoundError(f"ledger snapshot {stem} carries no game_env sidecar; the incumbent centre is "
                                "unknown and the three-arm snapshot refuses to guess it")
    return {"observations": path, "game_env": json.load(open(env_path)),
            "manifest": json.load(open(man_path)) if os.path.exists(man_path) else {},
            "stem": stem, "run_id": stem.split(".")[0], "model_version": ".".join(stem.split(".")[1:])}


def build_bank(games: pl.DataFrame, target_season: int, env: dict) -> tuple[ResidualBank, dict]:
    """The incumbent's residual population, rebuilt from the same silver table with the same rule."""
    rb = env.get("residual_bank") or {}
    lo = rb.get("season_lo") or 2016
    # Sorted, so the bank -- and therefore every residual index and its fingerprint -- is identical however the
    # silver rows happen to be ordered on disk. The distribution is the incumbent's either way.
    g = games.filter((pl.col("game_type") == "REG") & pl.col("result").is_not_null()
                     & pl.col("spread_line").is_not_null() & (pl.col("season") >= lo)).sort(["season", "week", "game_id"]).to_pandas()
    g["mres"] = g.result - g.spread_line
    g["tres"] = g.total - g.total_line
    bank = ResidualBank(g.mres, g.tres, g.season, ref_season=target_season, spread_lines=g.spread_line,
                        total_lines=g.total_line, overtime=g.overtime.fillna(0).astype(int), results=g.result,
                        halflife=float(rb.get("halflife_seasons") or 3.0), rng=np.random.default_rng(0))
    fp = crn.bank_fingerprint(bank, seasons_lo=int(g.season.min()), seasons_hi=int(g.season.max()),
                              halflife=float(rb.get("halflife_seasons") or 3.0),
                              extra={"incumbent_n_pairs": rb.get("n_pairs"), "n_pairs_match": rb.get("n_pairs") == len(g)})
    return bank, fp


def _arm_center(arm_id, version, *, margin, total, source, uses_market, status=R.OK, reason=None, **detail):
    a = REC.ArmCenter(arm_id=arm_id, arm_version=version, status=status, unavailable_reason=reason,
                      center_source=source, uses_market_information=uses_market)
    if margin is not None and total is not None and status != R.UNAVAILABLE:
        a.projected_home_margin = float(margin); a.projected_total = float(total)
        a.simulation_center_margin = crn.snap_to_grid(margin, R.CENTER_GRID)
        a.simulation_center_total = crn.snap_to_grid(total, R.CENTER_GRID)
        a.implied_home_score = float((total + margin) / 2.0); a.implied_away_score = float((total - margin) / 2.0)
    a.detail = detail
    return a


def build_snapshot(*, root: str, ledger: dict, now: datetime, target_season: int, n_sims: int = R.N_SIMS,
                   artifact_path: str | None = None, max_lag_min: float = R.MAX_GENERATION_LAG_MIN,
                   inputs: dict | None = None, verbose=print) -> dict:
    env = ledger["game_env"]
    run_id = ledger["run_id"]
    observed_at = _dt(env.get("capture_finished_at"))
    if observed_at is None:
        raise ValueError("the game_env sidecar carries no capture_finished_at; the snapshot time is unknown")
    lag = (now - observed_at).total_seconds() / 60.0
    if lag > max_lag_min:
        raise ValueError(f"the capture was observed {lag:.0f} min before this run, beyond the "
                         f"{max_lag_min:.0f} min limit: a snapshot built this long after its market is a "
                         "reconstruction, not a forecast")
    if lag < -5:
        raise ValueError(f"the capture is {-lag:.0f} min in the future of the wall clock; refusing")

    rows = ledger.get("rows")
    if rows is None:
        rows = [json.loads(l) for l in gzip.open(ledger["observations"], "rt")]
    center_provenance = env.get("center_provenance") or "incumbent_sidecar"
    by_game = {}
    for r in rows:
        if r.get("game_id"):
            by_game.setdefault(r["game_id"], []).append(r)

    # ---- inputs ------------------------------------------------------------------------------------
    inputs = inputs if inputs is not None else DO.load_inputs(root, target_season)
    games_df = inputs.get("games")
    if games_df is None:
        raise FileNotFoundError("silver games.parquet is required (the residual bank is built from it)")
    bank, bank_fp = build_bank(games_df, target_season, env)
    artifact_path = artifact_path or os.path.join(root, "research", "three_arm", f"data_only_artifact_{target_season}.json")
    artifact, artifact_problem = None, None
    if os.path.exists(artifact_path):
        try:
            artifact = DO.DataOnlyArtifact.load(artifact_path)
        except Exception as e:  # noqa: BLE001
            artifact_problem = f"artifact unreadable: {type(e).__name__}: {e}"
    else:
        artifact_problem = f"no frozen DATA_ONLY artifact at {artifact_path}"
    ratings, rmeta, cutoff_meta = {}, {}, {}
    if inputs.get("rows") is not None:
        allowed, cutoff_meta = DO.final_game_ids_before(games_df, observed_at)
        ratings, rmeta = DO.ratings_at_cutoff(inputs["rows"], target_season, allowed)
    mf_games, dropped = DO.market_free_schedule(games_df)
    mf_rows = {r["game_id"]: r for r in mf_games.to_dicts()}
    data_only_manifest = {k: v for k, v in inputs.items() if k not in ("rows", "games")}
    data_only_manifest["schedule_market_columns_dropped"] = dropped
    data_only_manifest["ratings"] = rmeta
    data_only_manifest["artifact_path"] = os.path.relpath(artifact_path, root) if artifact_path.startswith(root) else artifact_path

    generated_at = now.isoformat()
    sha = code_sha(root)
    game_records, contract_records = [], []
    repro_diffs = []
    for gid, ge in sorted(env.get("games", {}).items()):
        kickoff = _dt(ge.get("kickoff_utc"))
        mtk = None if kickoff is None else (kickoff - observed_at).total_seconds() / 60.0
        base = dict(record_id=REC.game_record_id(run_id, gid), schema_version=REC.SCHEMA_VERSION,
                    arms_version=R.ARMS_VERSION, run_id=run_id, observed_at=observed_at.isoformat(),
                    generated_at=generated_at, code_sha=sha, season=ge.get("season"), week=ge.get("week"),
                    game_id=gid, home_team=ge.get("home"), away_team=ge.get("away"),
                    kickoff_at=kickoff.isoformat() if kickoff else None, minutes_to_kickoff=mtk,
                    market_snapshot_id=run_id,
                    incumbent_ledger_file=os.path.basename(ledger["observations"]) if ledger.get("observations") else None,
                    incumbent_model_version=ledger["model_version"],
                    incumbent_game_env_version=env.get("game_env_version"))
        # ---- the prekickoff gate: BOTH the market snapshot and this run must precede kickoff ---------
        if kickoff is None or observed_at >= kickoff or now >= kickoff:
            # The reason names the CAPTURE time, never the wall clock: the wall clock lives in the volatile
            # generated_at, and a reason that changed between identical reruns would be a false conflict.
            why = ("no kickoff time" if kickoff is None else
                   ("capture " + observed_at.isoformat() + " is not strictly before kickoff " + kickoff.isoformat()
                    if observed_at >= kickoff else "generated after kickoff " + kickoff.isoformat()))
            game_records.append(REC.GameArmRecord(prekickoff=False, status=R.POST_KICKOFF_EXCLUDED, status_reason=why, **base).to_dict())
            continue
        home, away = ge.get("home"), ge.get("away")
        # ---- CURRENT: the exact centre the incumbent priced from --------------------------------------
        cur = _arm_center(R.CURRENT, "incumbent:" + str(env.get("game_env_version")),
                          margin=ge["spread_home"], total=ge["total"], source=ge.get("source"), uses_market=True,
                          kalshi_implied_spread=ge.get("kalshi_implied_spread"), kalshi_implied_total=ge.get("kalshi_implied_total"),
                          implied_diag=ge.get("implied_diag"), fallback_reason=ge.get("fallback_reason"),
                          consensus_spread_line=ge.get("consensus_spread_line"), consensus_total_line=ge.get("consensus_total_line"))
        cur.market_snapshot_id = run_id
        cur.detail["center_provenance"] = center_provenance
        cur.data_quality_state = "kalshi_implied" if ge.get("source") == "kalshi_implied" else "consensus_fallback"
        cur.feature_cutoff = {"market_observed_at": observed_at.isoformat()}
        # ---- DATA_ONLY: football only, or UNAVAILABLE with a reason. Never the market. -----------------
        if artifact is None:
            do = _arm_center(R.DATA_ONLY, R.DATA_ONLY_VERSION, margin=None, total=None, source="football_only",
                             uses_market=False, status=R.UNAVAILABLE, reason=artifact_problem)
        elif not ratings:
            do = _arm_center(R.DATA_ONLY, R.DATA_ONLY_VERSION, margin=None, total=None, source="football_only",
                             uses_market=False, status=R.UNAVAILABLE,
                             reason="no point-in-time ratings: " + "; ".join(inputs.get("unavailable") or ["unknown"]))
        elif gid not in mf_rows:
            do = _arm_center(R.DATA_ONLY, R.DATA_ONLY_VERSION, margin=None, total=None, source="football_only",
                             uses_market=False, status=R.UNAVAILABLE, reason="game not in the silver schedule")
        else:
            pj = DO.project_game(artifact, ratings, mf_rows[gid], home, away)
            do = _arm_center(R.DATA_ONLY, R.DATA_ONLY_VERSION, margin=pj.get("projected_home_margin"),
                             total=pj.get("projected_total"), source="football_only", uses_market=False,
                             status=pj["status"], reason=pj.get("unavailable_reason") or pj.get("degraded_reason"),
                             features=pj.get("features"), missing_metrics=pj.get("missing_metrics"),
                             attestation=pj.get("attestation"), unavailable_inputs=list(inputs.get("unavailable") or [])
                             + ["quarterback identity (no validated coefficient)", "weather (no validated coefficient)",
                                "injuries/availability (no validated coefficient)"])
            do.model_artifact_sha = artifact.artifact_sha
            do.model_training_seasons = list(artifact.train_seasons)
            do.training_cutoff = f"season {artifact.train_seasons[-1]}"
            do.feature_cutoff = dict(cutoff_meta)
            do.input_data_manifest = data_only_manifest
            do.data_quality_state = pj["status"]
        # ---- HYBRID_30: the one preregistered blend ------------------------------------------------------
        if do.status == R.UNAVAILABLE or do.projected_home_margin is None:
            hy = _arm_center(R.HYBRID, R.ARMS_VERSION, margin=None, total=None, source="blend", uses_market=True,
                             status=R.UNAVAILABLE, reason=f"DATA_ONLY unavailable ({do.unavailable_reason}); no fallback to the market")
        else:
            hm = R.HYBRID_WEIGHT_MARKET * cur.projected_home_margin + R.HYBRID_WEIGHT_DATA * do.projected_home_margin
            ht = R.HYBRID_WEIGHT_MARKET * cur.projected_total + R.HYBRID_WEIGHT_DATA * do.projected_total
            hy = _arm_center(R.HYBRID, R.ARMS_VERSION, margin=hm, total=ht, source="blend", uses_market=True,
                             status=(R.DEGRADED if do.status == R.DEGRADED else R.OK),
                             reason=(do.unavailable_reason if do.status == R.DEGRADED else None),
                             weight_market=R.HYBRID_WEIGHT_MARKET, weight_data=R.HYBRID_WEIGHT_DATA,
                             current_center={"margin": cur.projected_home_margin, "total": cur.projected_total},
                             data_only_center={"margin": do.projected_home_margin, "total": do.projected_total},
                             formula="hybrid = 0.70 * current_market_center + 0.30 * data_only_center")
            hy.market_snapshot_id = run_id
            hy.model_artifact_sha = do.model_artifact_sha
            hy.feature_cutoff = {**do.feature_cutoff, "market_observed_at": observed_at.isoformat()}
        arms = {R.CURRENT: cur, R.DATA_ONLY: do, R.HYBRID: hy}
        # ---- one set of draws, three simulations -----------------------------------------------------------
        key = f"{run_id}|{gid}|{R.CRN_VERSION}"
        draws = crn.draw_uniforms(n_sims, key)
        sims = {}
        for arm_id, a in arms.items():
            if a.status == R.UNAVAILABLE or a.simulation_center_margin is None:
                continue
            sims[arm_id] = crn.simulate_game_crn(a.simulation_center_margin, a.simulation_center_total, bank, draws)
            a.simulation = {**crn.sim_summary(sims[arm_id]),
                            "fractional_class": list(sims[arm_id]["fractional_class"]),
                            "residual_idx_sha": crn.hashlib.sha256(sims[arm_id]["residual_idx"].tobytes()).hexdigest()[:16]}
        # ---- price the SAME contract universe under each arm ----------------------------------------------
        n_priced, skipped = 0, {}
        cur_vs_incumbent = []
        for r in sorted(by_game.get(gid, []), key=lambda x: x.get("ticker") or ""):
            if r.get("family") not in R.GAME_FAMILIES_PRICED:
                continue
            if r.get("support_state") != "SUPPORTED":
                skipped[r.get("support_state")] = skipped.get(r.get("support_state"), 0) + 1
                continue
            q = {k: r.get(k) for k in ("family", "period", "team", "threshold", "floor_strike", "operator")}
            c = REC.ContractArmRecord(
                record_id=REC.contract_record_id(run_id, r["ticker"]), game_record_id=base["record_id"],
                schema_version=REC.SCHEMA_VERSION, arms_version=R.ARMS_VERSION, run_id=run_id,
                observed_at=observed_at.isoformat(), generated_at=generated_at, game_id=gid,
                season=ge.get("season"), week=ge.get("week"), home_team=home, away_team=away,
                kickoff_at=base["kickoff_at"], minutes_to_kickoff=mtk, ticker=r["ticker"],
                event_ticker=r.get("event_ticker"), series_ticker=r.get("series_ticker"), family=r.get("family"),
                period=r.get("period"), threshold=r.get("threshold"), floor_strike=r.get("floor_strike"),
                operator=r.get("operator"), team=r.get("team"), direction=r.get("direction") or "YES",
                incumbent_prediction_id=r.get("prediction_id"), incumbent_contract_value=r.get("model_contract_value"),
                incumbent_event_probability=r.get("model_event_probability"),
                yes_bid=r.get("yes_bid"), yes_ask=r.get("yes_ask"), no_bid=r.get("no_bid"), no_ask=r.get("no_ask"),
                mid=r.get("mid"), quote_width=r.get("quote_width"), volume=r.get("volume"),
                open_interest=r.get("open_interest"), liquidity=r.get("liquidity"),
                book_depth_yes=r.get("book_depth_yes"), book_depth_no=r.get("book_depth_no"),
                minutes_since_price_change=r.get("minutes_since_price_change"))
            unpriceable = None
            for arm_id, attr in ((R.CURRENT, "current"), (R.DATA_ONLY, "data_only"), (R.HYBRID, "hybrid")):
                a = arms[arm_id]
                if arm_id not in sims:
                    c.arm_status[arm_id] = a.status
                    continue
                p, cv, why = P.price_contract(sims[arm_id], q, home, away)
                if p is None:
                    unpriceable = why
                    c.arm_status[arm_id] = "UNPRICEABLE"
                    continue
                setattr(c, f"p_{attr}", p); setattr(c, f"cv_{attr}", cv)
                c.arm_status[arm_id] = a.status
            if unpriceable:
                skipped[unpriceable] = skipped.get(unpriceable, 0) + 1
                continue
            if c.cv_current is not None and r.get("model_contract_value") is not None:
                cur_vs_incumbent.append(c.cv_current - float(r["model_contract_value"]))
            contract_records.append(c.to_dict())
            n_priced += 1
        # ---- reproduction check: the harness's CURRENT arm against the incumbent's own draws -------------
        tol_each = 3.0 * math.sqrt(2.0 * 0.25 / n_sims)          # two independent 40k simulations at p=0.5
        diffs = np.asarray(cur_vs_incumbent, float)
        repro = {"n_contracts": int(len(diffs)), "tolerance_per_contract": round(tol_each, 5),
                 "max_abs_diff": (float(np.abs(diffs).max()) if len(diffs) else None),
                 "mean_signed_diff": (float(diffs.mean()) if len(diffs) else None),
                 "n_outside_tolerance": int((np.abs(diffs) > tol_each).sum()) if len(diffs) else 0}
        repro["ok"] = bool(len(diffs) == 0 or (repro["n_outside_tolerance"] <= max(1, int(0.01 * len(diffs)))
                                                 and abs(repro["mean_signed_diff"]) <= 0.005))
        repro["available"] = bool(len(diffs))
        if not len(diffs):
            repro["reason"] = ("no incumbent ledger prices at this snapshot (centre re-derived with the incumbent estimator)"
                               if center_provenance != "incumbent_sidecar" else "no priced game contracts to compare")
        if not repro["ok"] and cur.status == R.OK:
            cur.status = R.DEGRADED
            cur.unavailable_reason = f"reproduction check failed: {repro}"
            for c in contract_records:
                if c["game_id"] == gid:
                    c["arm_status"][R.CURRENT] = R.DEGRADED
        repro_diffs.extend(diffs.tolist())
        rec = REC.GameArmRecord(prekickoff=True, status=R.OK, **base)
        rec.simulation = {"n_sims": n_sims, "seed_key": key, "crn_version": R.CRN_VERSION,
                          "uniform_draws_sha": draws["sha"], "residual_bank": bank_fp}
        rec.arms = {k: v.to_dict() for k, v in arms.items()}
        rec.reproduction_check = repro
        rec.n_contracts_priced = n_priced
        rec.n_contracts_skipped = sum(skipped.values())
        rec.contract_skip_reasons = skipped
        game_records.append(rec.to_dict())
        verbose(f"  {gid}: CURRENT {cur.projected_home_margin:+.1f}/{cur.projected_total:.1f} ({cur.center_source}) | "
                f"DATA_ONLY {('%+.2f/%.2f' % (do.projected_home_margin, do.projected_total)) if do.projected_home_margin is not None else do.status} | "
                f"HYBRID {('%+.2f/%.2f' % (hy.projected_home_margin, hy.projected_total)) if hy.projected_home_margin is not None else hy.status} | "
                f"{n_priced} contracts, repro max|d|={repro['max_abs_diff']}")
    for gid, why in (env.get("games_without_environment") or {}).items():
        game_records.append(REC.GameArmRecord(
            record_id=REC.game_record_id(run_id, gid), schema_version=REC.SCHEMA_VERSION, arms_version=R.ARMS_VERSION,
            run_id=run_id, observed_at=observed_at.isoformat(), generated_at=generated_at, code_sha=sha, season=None,
            week=None, game_id=gid, home_team=None, away_team=None, kickoff_at=None, minutes_to_kickoff=None,
            prekickoff=False, status=R.UNAVAILABLE, status_reason=f"incumbent had no game environment: {why}",
            market_snapshot_id=run_id).to_dict())
    return {"run_id": run_id, "observed_at": observed_at.isoformat(), "generated_at": generated_at,
            "games": game_records, "contracts": contract_records,
            "manifest_extra": {"incumbent_ledger_file": os.path.basename(ledger["observations"]) if ledger.get("observations") else None,
                               "center_provenance": center_provenance,
                               "incumbent_model_version": ledger["model_version"],
                               "capture_to_generation_lag_min": round(lag, 1), "code_sha": sha,
                               "data_only": data_only_manifest, "data_only_artifact_sha": artifact.artifact_sha if artifact else None,
                               "data_only_problem": artifact_problem, "residual_bank": bank_fp,
                               "n_sims": n_sims, "reproduction_check": {
                                   "n_contracts": len(repro_diffs),
                                   "max_abs_diff": float(np.max(np.abs(repro_diffs))) if repro_diffs else None,
                                   "mean_signed_diff": float(np.mean(repro_diffs)) if repro_diffs else None}}}
