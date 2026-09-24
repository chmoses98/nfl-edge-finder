"""DATA_PLAYER_V4 in production: the same inputs as v3 at the cutoff, plus point-in-time teammate statuses.

Everything v3 bounds at the cutoff is bounded the same way here (prospective_v3 is reused, not copied): the market-
implied game environment of the snapshot, completed current-season games (kicked off >= 4 h before the cutoff), and
the depth-chart QB1. V4 adds the pregame status of every teammate, and it takes the TARGET WEEK's statuses only from
evidence available at the cutoff:

    injury report   the point-in-time vintage the context layer resolved for this run (`ctx.injuries`), never the
                    freshest file on disk (which, on a replay, would carry the future)
    availability    the run's own sleeper / espn captures (AvailabilityBook), the more severe of the two readings;
                    INACTIVE_CONFIRMED (official inactives, T-90m) counts as out -- information the model may use
                    once it exists, and never before

A game without an environment gets no V4 distribution (a refusal, never a zero-point team).
"""
from __future__ import annotations

import time

import numpy as np

from nfl_edge.engines.player import prospective_v3 as PV3
from nfl_edge.engines.player.features_v2 import add_v2_features
from nfl_edge.engines.player.features_v3 import add_v3_features
from nfl_edge.engines.player import data_dist as DD
from nfl_edge.engines.player.v4 import INPUTS_VERSION, VERSION
from nfl_edge.engines.player.v4 import features as F4
from nfl_edge.engines.player.v4 import model as M
from nfl_edge.engines.player.v4.volume import team_game_table
from nfl_edge.research import player_distributions as pdist
from nfl_edge.shadow.prospective import build_prospective_rows, upcoming_from_markets

SEVERITY = {"QUESTIONABLE": 1, "DOUBTFUL": 2, "OUT": 3}
AVAIL_TO_REPORT = {"OUT": "OUT", "EXPECTED_OUT": "OUT", "INACTIVE_CONFIRMED": "OUT", "DOUBTFUL": "DOUBTFUL", "QUESTIONABLE": "QUESTIONABLE"}
# what each V4 record keeps of the model's intermediates (the full chain is reproducible from the bundle + inputs)
LEAN_KEYS = ("team", "pgroup", "snap_mean", "snap_sd", "vol_pa", "vol_ra", "share_t", "share_c", "mu_targets", "mu_carries",
             "mu_receptions", "r_cr", "r_ypr", "r_ypc", "mu_attempts", "mu_any_td", "vac_same_t", "vac_same_c", "ret_same_t",
             "ret_same_c", "self_frac_t", "self_frac_c", "own_q", "own_d", "self_new", "self_returning", "changed_team",
             "n_cur_season", "implied_total", "spread_team", "env_source", "qb_starter", "recon_t_sum", "recon_c_sum")


def target_week_overrides(ctx, avail, season: int, weeks) -> dict:
    """(season, week, gsis) -> OUT / DOUBTFUL / QUESTIONABLE from the run's point-in-time evidence."""
    out = {}
    inj = getattr(ctx, "injuries", None) if ctx is not None else None
    if inj and not inj.get("no_vintage_at_cutoff"):
        for (gsis, wk), r in (inj.get("rows") or {}).items():
            st = str(r.get("report_status") or "").upper()
            if st in SEVERITY and int(wk) in weeks:
                out[(season, int(wk), gsis)] = st
    for gsis, av in ((getattr(avail, "by_gsis", None) or {}).items() if avail is not None else []):
        st = AVAIL_TO_REPORT.get(getattr(av, "state", None))
        if not st:
            continue
        for wk in weeks:
            k = (season, int(wk), gsis)
            if SEVERITY[st] > SEVERITY.get(out.get(k), 0):
                out[k] = st
    return out


def build(P, *, root, target_season, prows, player_map, sched, positions, envs, kick, run_ts, ledger, ctx, cfg, priors, log=print):
    """Fill P.data_v4 / P.feat_v4 / P.bundle_v4 / P.v4_info / P.v4_refusal. Raises only on a programming error; the
    caller catches everything so a V4 failure never costs the run its other arms."""
    t0 = time.time()
    try:
        hist_all = pdist.load_player_games(root, range(2013, target_season + 1))
        cur_state = "loaded"
    except (FileNotFoundError, OSError) as exc:
        hist_all = pdist.load_player_games(root, range(2013, target_season))
        cur_state = f"unavailable: {type(exc).__name__}"
    pregame = PV3.pregame_games(kick, run_ts)
    prows = [q for q in prows if q.get("game_id") in pregame]
    hist, info = PV3.completed_current_season(hist_all, target_season, kick, run_ts, exclude_games=pregame)
    info["current_season_state"] = cur_state
    book = (ctx.depth or {}).get("book") if ctx else None
    qb1 = {t: book.qb1(t) for t in (book.by_team if book else {})} if book else {}
    upcoming = upcoming_from_markets(prows, player_map, sched, target_season, positions, {})
    if not len(upcoming):
        P.v4_info = {**info, "n_upcoming": 0, "version": VERSION}
        return
    upcoming = PV3.attach_market_environment(upcoming, envs)
    upcoming = PV3.depth_qb_starters(upcoming, qb1)
    for r in upcoming.itertuples():
        if not r.env_known:
            P.v4_refusal[(r.player_id, r.game_id)] = "no market-implied game environment at the cutoff: v4 refuses rather than price a zero-point team"
    combined = build_prospective_rows(hist, upcoming.drop(columns=["qb1_known"]))
    combined = pdist.add_ewma_features(combined, halflife=cfg["halflife"], season_carry=cfg["season_carry"], shrink_k=cfg["shrink_k"], priors=priors)
    combined = add_v2_features(combined, halflife=cfg["halflife"], season_carry=cfg["season_carry"], shrink_k=cfg["shrink_k"])
    combined = add_v3_features(DD.ensure_columns(combined))
    combined = F4.add_recency_features(combined)
    weeks = sorted({int(w) for w in upcoming.week})
    frame = F4.status_frame(root, range(2013, target_season + 1))
    # the target weeks' reports come ONLY from the point-in-time overlay; the file's rows for them are dropped
    tw = (frame.season == target_season) & frame.week.isin(weeks)
    frame.loc[tw, "report"] = None
    overrides = target_week_overrides(ctx, P.avail, target_season, set(weeks))
    status = F4.StatusBook(frame, overrides=overrides, override_weeks=[(target_season, w) for w in weeks])
    combined = F4.add_absence_features(combined, status)
    teams = team_game_table(combined)
    P.bundle_v4 = M.fit_bundle(combined, target_season, teams=teams, verbose=log)
    feat = combined[combined.is_prospective == True].reset_index(drop=True)   # noqa: E712
    ok = PV3.usable_rows(feat)
    n_dist = 0
    if ok.any():
        I = P.bundle_v4.intermediates(feat[ok], teams)
        for r in I.to_dict("records"):
            key = (r["player_id"], r["game_id"])
            P.feat_v4[key] = {k: _plain(r.get(k)) for k in LEAN_KEYS}
            for stat, d in P.bundle_v4.distributions(r).items():
                P.data_v4[(r["player_id"], r["game_id"], stat)] = d
                n_dist += 1
            P.v4_inter[key] = {k: _plain(v) for k, v in r.items() if isinstance(v, (int, float, np.floating, np.integer, bool, str)) or v is None}
    P.v4_info = {**info, "version": VERSION, "inputs_version": INPUTS_VERSION, "n_upcoming": int(len(upcoming)),
                 "n_env_known": int(upcoming.env_known.sum()), "n_distributions": n_dist, "bundle_sha": P.bundle_v4.artifact_sha,
                 "n_status_overrides": len(overrides), "target_weeks": weeks, "seconds": round(time.time() - t0, 1),
                 "injury_vintage": ((getattr(ctx, "injuries", None) or {}).get("meta") or {}).get("retrieved_at") if ctx else None}
    log(f"v4: {n_dist} distributions (bundle {P.bundle_v4.artifact_sha}) in {P.v4_info['seconds']}s; "
        f"{len(overrides)} point-in-time status overrides for weeks {weeks}")


def _plain(v):
    if isinstance(v, (np.floating,)):
        v = float(v)
    if isinstance(v, (np.integer,)):
        v = int(v)
    if isinstance(v, (np.bool_,)):
        v = bool(v)
    if isinstance(v, float) and not np.isfinite(v):
        return None
    if isinstance(v, float):
        return round(v, 5)
    return v
