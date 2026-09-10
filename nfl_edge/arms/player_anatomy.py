"""Player-projection anatomy: the REAL intermediates of every incumbent player projection, in a separate corpus.

The incumbent ledger (schema 1.0.0, frozen Week-1 lineage) records P(stat >= K) and the contract value and
nothing of how they were produced. The frozen pricer and the frozen model module must not be edited to record
more. So this module REPLAYS the incumbent's player path -- the same loaders, the same feature routine, the
same fitted bundle, the same branch logic, imported from the frozen modules and executed in the same order --
and freezes, per supported player-stat ledger row, the quantities that path computes on its way to the price:

    mu                     the projected statistic mean            (pdist.predict_mean on the mean model)
    muo                    the projected opportunity mean          (pdist.predict_mean on the opportunity model)
    efficiency feature     the EWMA ratio the family conditions on (ypc, ypt, catch_rate, ...), when the spec has one
    family                 the fitted distribution family
    model quantiles        p05 / p25 / p50 / p75 / p95 of the fitted lattice distribution
    EWMA inputs            the stat and opportunity EWMAs, prior-game count, shrink weight, consensus implied total
    availability branches  state, P(plays), P(active, no snap), P(inactive), sources, staleness, fair price used
    identity / lineage     GSIS id, game, ticker, threshold, run, bundle version and hash, feature cutoff

and the REPRODUCED probability and contract value, which are reconciled against the ledger row for the same
ticker and run. The tolerance is strict (RECONCILE_TOL, 1e-9): the replay runs in the same job on the same
inputs, so anything but equality means the anatomy is not describing the ledger's number. A row outside it is
`REPRODUCTION_MISMATCH` and is never authoritative autopsy evidence; the ledger itself is never touched.

Corpus: data/shadow/player_anatomy/<game_id>/anatomy-1.0.0.<run_id>.anatomy.jsonl.gz, write-once, keyed by
the ledger prediction_id, through the same store the evaluation corpus uses.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import numpy as np
import polars as pl

from nfl_edge.research import player_distributions as pdist
from nfl_edge.settlement import semantics as sem_mod
from nfl_edge.settlement.availability import AvailabilityBook
from nfl_edge.shadow.models import KALSHI_STAT_TO_SPEC, fit_bundle
from nfl_edge.shadow.prospective import build_prospective_rows, upcoming_from_markets
from nfl_edge.features import opportunity

ANATOMY_VERSION = "anatomy-1.0.0"
SUFFIX = "anatomy"
RECONCILE_TOL = 1e-9
OK = "OK"
MISMATCH = "REPRODUCTION_MISMATCH"
MODEL_VERSION_DEFAULT = "shadow-0.4.0"          # the frozen pricer's default, mirrored (pinned by test)


# ------------------------------------------------------------------ read-only helpers over the frozen model
def survival_quantiles(grid: np.ndarray, S: np.ndarray, probs=(0.05, 0.25, 0.50, 0.75, 0.95)) -> dict:
    """Quantiles of a lattice distribution given S[g] = P(Y >= grid[g]): the smallest grid value whose CDF reaches p."""
    cdf = 1.0 - np.concatenate([S[1:], [0.0]])          # P(Y <= grid[g]) = 1 - P(Y >= grid[g+1])
    out = {}
    for p in probs:
        i = int(np.searchsorted(cdf, p - 1e-12, side="left"))
        out[f"p{int(round(p * 100)):02d}"] = float(grid[min(i, len(grid) - 1)])
    return out


def intermediates(sm, rows) -> dict:
    """The quantities StatModel.survival computes on its way to S, recomputed read-only from its public parts."""
    spec = pdist.STAT_SPECS[sm.spec_name]
    mu = pdist.predict_mean(sm.mean_model, rows, spec, spec.col, pdist.MU_FLOOR[spec.kind])
    muo = pdist.predict_mean(sm.opp_model, rows, spec, spec.opp, 0.1)
    eff = rows[spec.eff].to_numpy(dtype=float) if spec.eff and spec.eff in rows.columns else None
    return {"mu": mu, "muo": muo, "eff": eff, "efficiency_feature": spec.eff, "stat_col": spec.col,
            "opp_col": spec.opp, "family": sm.family_name}


def _f(x):
    try:
        return None if x is None else float(x)
    except (TypeError, ValueError):
        return None


# ------------------------------------------------------------------ the replay of the incumbent's player path
def replay_player_models(root: str, market_data: str, quotes: dict, run_ts: datetime, games: pl.DataFrame,
                         target_season: int, *, model_version: str = MODEL_VERSION_DEFAULT,
                         role_features: bool = False, max_availability_age_min: float = 600.0, verbose=lambda *_: None) -> dict:
    """price_slate's identity, availability and player-model blocks, call for call, on the same inputs."""
    import glob
    sched = games.filter(pl.col("season") == target_season)
    gidx = {r["game_id"]: r for r in sched.to_dicts()}
    pmap = pl.read_parquet(os.path.join(root, "data/silver/kalshi_player_map.parquet"))
    resolved = pmap.filter(pl.col("gsis_id").is_not_null() & pl.col("status").is_in(
        ["RESOLVED", "RESOLVED_TEAM_UNCONFIRMED", "RESOLVED_PLAYERS_TABLE", "RESOLVED_JERSEY_MISMATCH"]))
    player_map = dict(zip(resolved["kalshi_player_id"].to_list(), resolved["gsis_id"].to_list()))
    not_player = set(pmap.filter(pl.col("status") == "NOT_A_PLAYER")["kalshi_player_id"].to_list())
    players_tbl = pl.read_parquet(os.path.join(root, "data/raw/nflverse/players/players.parquet")).select("gsis_id", "position")
    positions = dict(zip(players_tbl["gsis_id"].to_list(), players_tbl["position"].to_list()))

    ctx_root = os.path.join(market_data, "data", "context")
    book_av = AvailabilityBook(run_ts, max_staleness_minutes=max_availability_age_min)
    xw = pl.read_parquet(os.path.join(root, "data/silver/player_crosswalk.parquet"))
    sleeper_xw = {str(s): g for s, g in zip(xw["sleeper_id"].to_list(), xw["gsis_id"].to_list()) if s}
    espn_xw = {str(s): g for s, g in zip(xw["espn_id"].to_list(), xw["gsis_id"].to_list()) if s}
    for pat, loader in ((f"{ctx_root}/*/*.sleeper.json", book_av.load_sleeper), (f"{ctx_root}/*/*.espn_injuries.json", book_av.load_espn)):
        fs = sorted(glob.glob(pat))
        if fs:
            loader(fs[-1], sleeper_xw if "sleeper" in pat else espn_xw)
    rost = os.path.join(root, "data/raw/nflverse/weekly_rosters", f"roster_weekly_{target_season}.parquet")
    if os.path.exists(rost):
        r = pl.read_parquet(rost)
        wk = int(sched["week"].min()) if sched.height else 1
        book_av.load_roster(r.filter(pl.col("week") == wk).select("gsis_id", "status").to_dicts(), f"week{wk}")
    book_av.finalize()

    hist = pdist.load_player_games(root, range(2013, target_season))
    cfg = json.load(open(os.path.join(root, "research/player_distributions/results.json")))["config"]
    priors = pdist.position_priors(hist, range(2013, 2016))
    qb_ids = {}
    for gid, row in gidx.items():
        s = set()
        for c in ("home_qb_id", "away_qb_id"):
            v = row.get(c)
            if isinstance(v, str) and v:
                s.add(v)
        qb_ids[gid] = s
    rows = list(quotes.values())
    upcoming = upcoming_from_markets([r for r in rows if r.get("player_kalshi_id")], player_map, sched, target_season, positions, qb_ids)
    bundle = feat = None
    role_attached = False
    if len(upcoming):
        combined = build_prospective_rows(hist, upcoming)
        combined = pdist.add_ewma_features(combined, halflife=cfg["halflife"], season_carry=cfg["season_carry"],
                                           shrink_k=cfg["shrink_k"], priors=priors)
        try:
            combined = opportunity.attach_role_features(combined, halflife=cfg["halflife"],
                                                        season_carry=cfg["season_carry"], shrink_k=cfg["shrink_k"])
            role_attached = pdist.has_role_features(combined)
        except FileNotFoundError:
            role_attached = False
        feat = combined[combined.is_prospective == True].copy()   # noqa: E712
        histf = combined[combined.is_prospective != True].copy()  # noqa: E712
        bundle = fit_bundle(histf, target_season, model_version,
                            {"ewma": cfg, "min_train_season": 2016, "use_role_features": role_features}, verbose=verbose)
        from nfl_edge.shadow.models import CHOSEN_FAMILY as _CF
        _CF_backup = dict(_CF); _CF["anytime_td"] = "negbin"
        cnt_bundle = fit_bundle(histf, target_season, model_version + "-tdcount",
                                {"ewma": cfg, "min_train_season": 2016, "use_role_features": role_features},
                                stats=["anytime_td"], verbose=lambda *_: None)
        _CF.clear(); _CF.update(_CF_backup)
        if "anytime_td" in cnt_bundle.stat_models:
            bundle.stat_models["anytime_td_count"] = cnt_bundle.stat_models["anytime_td"]
    return {"bundle": bundle, "feat": feat, "book_av": book_av, "player_map": player_map, "not_player": not_player,
            "positions": positions, "gidx": gidx, "cfg": cfg, "role_features_attached": role_attached,
            "availability_sources": book_av.source_meta, "n_upcoming": int(len(upcoming))}


def anatomy_row(obs: dict, q: dict, rep: dict, *, run_id: str, feature_cutoff: str, now: datetime | None = None) -> dict | None:
    """One SUPPORTED PLAYER_STAT ledger observation -> its anatomy, reproduced through the incumbent's own branch logic."""
    now = now or datetime.now(timezone.utc)
    bundle, feat, book_av = rep["bundle"], rep["feat"], rep["book_av"]
    gsis, gid = obs.get("player_id"), obs.get("game_id")
    out = {"prediction_id": obs["prediction_id"], "evaluation_version": ANATOMY_VERSION, "evaluated_at": now.isoformat(),
           "anatomy_status": OK, "reason": None, "run_id": run_id, "observed_at": obs.get("observed_at"),
           "feature_cutoff": feature_cutoff, "model_version": obs.get("model_version"), "model_artifact_sha": obs.get("model_artifact_sha"),
           "bundle_artifact_sha": bundle.artifact_sha if bundle else None,
           "ticker": obs.get("ticker"), "game_id": gid, "season": obs.get("season"), "week": obs.get("week"), "team": obs.get("team"),
           "player_id": gsis, "player_name": obs.get("player_name"), "player_kalshi_id": obs.get("player_kalshi_id"),
           "stat": obs.get("stat"), "threshold": obs.get("threshold"), "kickoff_utc": obs.get("kickoff_utc"),
           "minutes_to_kickoff": obs.get("minutes_to_kickoff"),
           "ledger_event_probability": obs.get("model_event_probability"), "ledger_contract_value": obs.get("model_contract_value"),
           "mid": obs.get("mid"), "yes_ask": obs.get("yes_ask"), "yes_bid": obs.get("yes_bid"),
           "reproduced_event_probability": None, "reproduced_contract_value": None,
           "stat_spec": None, "distribution_family": None, "projected_stat_mean": None, "projected_opportunity_mean": None,
           "projected_efficiency": None, "efficiency_feature": None, "efficiency_decomposition": None, "model_quantiles": None,
           "ewma_stat": None, "ewma_opportunity": None, "feature_n_prior": None, "feature_shrink_w": None,
           "implied_total_input": None, "qb_starter": None, "availability_state": None, "p_plays": None,
           "p_active_no_snap": None, "p_inactive": None, "fair_price_used": None, "availability_sources": None,
           "availability_stale_minutes": None}
    if bundle is None or feat is None or not gsis or not gid:
        out["anatomy_status"], out["reason"] = MISMATCH, "no fitted bundle or identity to reproduce from"
        return out
    pos = rep["positions"].get(gsis)
    spec_name = KALSHI_STAT_TO_SPEC.get((q.get("stat"), "QB" if pos == "QB" else None)) or KALSHI_STAT_TO_SPEC.get((q.get("stat"), None))
    if q.get("stat") == "rushing_yards" and pos == "QB":
        spec_name = "qb_rushing_yards"
    if spec_name is None:
        out["anatomy_status"], out["reason"] = MISMATCH, f"no model for stat {q.get('stat')}"
        return out
    sub = feat[(feat.player_id == gsis) & (feat.game_id == gid)]
    if not len(sub):
        out["anatomy_status"], out["reason"] = MISMATCH, "no prospective feature row for this player-game"
        return out
    av = book_av.get(gsis)
    out.update({"stat_spec": spec_name, "availability_state": av.state, "p_plays": av.p_plays, "p_active_no_snap": av.p_active_no_snap,
                "p_inactive": av.p_inactive, "availability_stale_minutes": av.stale_minutes,
                "availability_sources": {k: v.get("state") for k, v in (av.sources or {}).items()},
                "feature_n_prior": int(sub["n_prior"].iloc[0]) if "n_prior" in sub.columns else None,
                "feature_shrink_w": _f(sub["shrink_w"].iloc[0]) if "shrink_w" in sub.columns else None,
                "implied_total_input": _f(sub["implied_total"].iloc[0]) if "implied_total" in sub.columns else None,
                "qb_starter": bool(sub["qb_starter"].iloc[0]) if "qb_starter" in sub.columns else None})
    mid = obs.get("mid")
    if spec_name == "anytime_td":
        if bundle.td_model is None:
            out["anatomy_status"], out["reason"] = MISMATCH, "TD model unavailable"
            return out
        p1 = float(bundle.td_model.predict(sub)[0])
        kk = float(q.get("threshold") or 1)
        if kk <= 1:
            p = p1
        else:
            cnt = bundle.stat_models.get("anytime_td_count")
            if cnt is None:
                out["anatomy_status"], out["reason"] = MISMATCH, "count-shape model not fitted"
                return out
            grid, S, _mu = cnt.survival(sub)
            i1 = int(np.searchsorted(grid, 1.0, side="left")); ik = int(np.searchsorted(grid, kk, side="left"))
            base = float(S[0][min(i1, len(S[0]) - 1)])
            p = p1 * (float(S[0][min(ik, len(S[0]) - 1)]) / base) if base > 1e-9 else 0.0
        out.update({"distribution_family": "direct_binary", "efficiency_decomposition": "none", "projected_stat_mean": p1,
                    "projected_opportunity_mean": _f(sub["ewma_touches"].iloc[0]) if "ewma_touches" in sub.columns else None,
                    "ewma_stat": _f(sub["ewma_any_td"].iloc[0]) if "ewma_any_td" in sub.columns else None})
        out["ewma_opportunity"] = out["projected_opportunity_mean"]
    else:
        sm = bundle.stat_models.get(spec_name)
        if sm is None:
            out["anatomy_status"], out["reason"] = MISMATCH, f"no fitted model for {spec_name}"
            return out
        grid, S, mu = sm.survival(sub)
        S0 = S[0]
        k = float(q["threshold"])
        idx = int(np.searchsorted(grid, k, side="left"))
        p = float(S0[min(idx, len(S0) - 1)]) if k <= grid[-1] else 0.0
        im = intermediates(sm, sub)
        out.update({"distribution_family": im["family"], "projected_stat_mean": float(mu[0]), "projected_opportunity_mean": _f(im["muo"][0]),
                    "projected_efficiency": _f(im["eff"][0]) if im["eff"] is not None else None,
                    "efficiency_feature": im["efficiency_feature"],
                    "efficiency_decomposition": "opportunity_x_efficiency" if im["eff"] is not None else "none",
                    "model_quantiles": survival_quantiles(grid, S0),
                    "ewma_stat": _f(sub[f"ewma_{im['stat_col']}"].iloc[0]) if f"ewma_{im['stat_col']}" in sub.columns else None,
                    "ewma_opportunity": _f(sub[f"ewma_{im['opp_col']}"].iloc[0]) if f"ewma_{im['opp_col']}" in sub.columns else None})
    cv = sem_mod.player_prop_contract_value(p, av.p_plays, av.p_active_no_snap, mid)
    out.update({"reproduced_event_probability": p, "reproduced_contract_value": cv.contract_value, "fair_price_used": cv.fair_price_used})
    return reconcile(out)


def reconcile(row: dict, tol: float = RECONCILE_TOL) -> dict:
    """Mark the row OK only when the reproduced probability AND contract value equal the ledger's within `tol`."""
    lp, lc = row.get("ledger_event_probability"), row.get("ledger_contract_value")
    rp, rc = row.get("reproduced_event_probability"), row.get("reproduced_contract_value")
    if None in (lp, lc, rp, rc):
        row["anatomy_status"], row["reason"] = MISMATCH, row.get("reason") or "a probability is missing on one side"
        return row
    dp, dc = abs(float(lp) - float(rp)), abs(float(lc) - float(rc))
    row["reconciliation"] = {"abs_diff_event_probability": dp, "abs_diff_contract_value": dc, "tolerance": tol}
    if dp > tol or dc > tol:
        row["anatomy_status"] = MISMATCH
        row["reason"] = f"reproduced p/cv differ from the ledger by {dp:.3g}/{dc:.3g} (tolerance {tol:g})"
    return row


def collect(ledger_rows: list, quotes: dict, rep: dict, *, run_id: str, feature_cutoff: str, now=None) -> list:
    """Anatomy rows for every SUPPORTED PLAYER_STAT ledger observation of this run."""
    out = []
    for obs in ledger_rows:
        if obs.get("family") != "PLAYER_STAT" or obs.get("support_state") != "SUPPORTED" or obs.get("run_id") != run_id:
            continue
        q = quotes.get(obs["ticker"]) or {"stat": obs.get("stat"), "threshold": obs.get("threshold")}
        row = anatomy_row(obs, q, rep, run_id=run_id, feature_cutoff=feature_cutoff, now=now)
        if row is not None:
            out.append(row)
    return out
