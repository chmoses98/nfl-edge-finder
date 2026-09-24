"""DATA_PLAYER_V5 in production: V4's inputs at the cutoff, with the starting quarterback resolved point in time.

Everything V4 bounds at the cutoff is bounded the same way here, by calling the same functions (prospective_v3 for
the market-implied environment, completed current-season games and usable rows; V4's `target_week_overrides` and
StatusBook for teammate statuses). The one input that differs is the projected starting quarterback:

    V4   `DepthChartBook.qb1(team)` -- first QB on the newest chart at or before the cutoff, whatever his status
    V5   `qb_resolution.resolve_team_qb` over that same chart, with the availability evidence that existed at the
         cutoff:
             injury report   the point-in-time vintage the context layer resolved (`ctx.injuries`), the game's week
                             only, stamped with the vintage's retrieved_at
             availability    the run's own sleeper / espn / weekly-roster captures (AvailabilityBook, the same
                             combined state V4's overrides read)
             inactives       the official inactive observations the run loaded (`ctx.inactives`; the loader already
                             keeps only observations made at or before the cutoff and before kickoff), matched by the
                             charted player's name, each carrying its own observed_at

The resolution is frozen per team-game (`P.v5_qb`) and its five fields ride on every V5 record of that team:
depth_chart_qb1, effective_projected_qb, qb_availability_state, qb_resolution_reason, qb_resolution_certainty.

A game without an environment gets no V5 distribution (a refusal, never a zero-point team). This module never raises
into the caller for a data problem; project_slate_v2 still wraps it, so a V5 failure refuses V5 records and costs
nothing else.
"""
from __future__ import annotations

import time

import numpy as np

from nfl_edge.context import qb_resolution as QR
from nfl_edge.engines.player import data_dist as DD
from nfl_edge.engines.player import prospective_v3 as PV3
from nfl_edge.engines.player.features_v2 import add_v2_features
from nfl_edge.engines.player.features_v3 import add_v3_features
from nfl_edge.engines.player.v4 import features as F4
from nfl_edge.engines.player.v4 import prospective as PV4
from nfl_edge.engines.player.v4.volume import team_game_table
from nfl_edge.engines.player.v5 import INPUTS_VERSION, VERSION
from nfl_edge.engines.player.v5 import model as M5
from nfl_edge.engines.player.v5 import qb_features as QF
from nfl_edge.research import player_distributions as pdist
from nfl_edge.shadow.prospective import build_prospective_rows, upcoming_from_markets

QB_FIELDS = ("depth_chart_qb1", "effective_projected_qb", "qb_availability_state", "qb_resolution_reason", "qb_resolution_certainty")
LEAN_KEYS = PV4.LEAN_KEYS + tuple(c for c in QF.QB_ID_COLS if c != "qb_projected_id") + QB_FIELDS + ("qb_dependent_abstain",)
SLOTS = {"data_v5": dict, "feat_v5": dict, "v5_inter": dict, "v5_refusal": dict, "v5_qb": dict, "v5_info": dict}


def ensure_slots(P) -> None:
    for k, f in SLOTS.items():
        if not isinstance(getattr(P, k, None), dict):
            setattr(P, k, f())
    if not hasattr(P, "bundle_v5"):
        P.bundle_v5 = None


# --------------------------------------------------------------------------------------------- evidence
def team_evidence(qbs, *, ctx, avail, week: int, game_id: str, book=None) -> tuple[list, bool]:
    """The QbEvidence available at the run's cutoff for these quarterbacks, and whether the team's status was known
    at all (an injury-report vintage or an availability capture)."""
    ev, known = [], False
    inj = getattr(ctx, "injuries", None) if ctx is not None else None
    if inj and not inj.get("no_vintage_at_cutoff"):
        known = True
        at = (inj.get("meta") or {}).get("retrieved_at")
        at = None if at in (None, "UNKNOWN") else at
        rows = inj.get("rows") or {}
        for q in qbs:
            r = rows.get((q, int(week)))
            if r and r.get("report_status"):
                ev.append(QR.QbEvidence(q, str(r["report_status"]), QR.SRC_INJURY_REPORT, at))
    by = (getattr(avail, "by_gsis", None) or {}) if avail is not None else {}
    if by:
        known = True
        stamps = [m.get("retrieved_at") for m in (getattr(avail, "source_meta", None) or {}).values() if isinstance(m, dict) and m.get("retrieved_at")]
        at = max(stamps) if stamps else None
        for q in qbs:
            a = by.get(q)
            if a is not None and getattr(a, "state", None):
                ev.append(QR.QbEvidence(q, a.state, QR.SRC_AVAILABILITY, at))
    ina = getattr(ctx, "inactives", None) if ctx is not None else None
    if ina is not None and book is not None:
        for q in qbs:
            e = book.entry(q)
            st = ina.state(game_id, player_name=(e.name if e else None)) if e and e.name else {}
            if st.get("official_inactive_state") == "INACTIVE_CONFIRMED":
                ev.append(QR.QbEvidence(q, "INACTIVE_CONFIRMED", QR.SRC_OFFICIAL_INACTIVES, st.get("observed_at")))
    return ev, known


def resolve_slate(team_games, *, ctx, avail, kick: dict, cutoff) -> dict:
    """(team, game_id) -> resolution, for every (team, game_id, week) in `team_games`."""
    book = (getattr(ctx, "depth", None) or {}).get("book") if ctx is not None else None
    out = {}
    for team, gid, week in team_games:
        qbs = [e.gsis_id for e in ((book.by_team.get(team) or {}).get("QB") or [])] if book else []
        ev, known = team_evidence(qbs, ctx=ctx, avail=avail, week=week, game_id=gid, book=book)
        out[(team, gid)] = QR.resolve_team_qb(team=team, chart_qbs=qbs, cutoff=cutoff, evidence=ev,
                                              chart_vintage=(book.vintage.get(team) if book else None),
                                              kickoff=kick.get(gid), status_known=known)
    return out


# --------------------------------------------------------------------------------------------- build
def build(P, *, root, target_season, prows, player_map, sched, positions, envs, kick, run_ts, ledger, ctx, cfg, priors, log=print):
    """Fill P.data_v5 / P.feat_v5 / P.bundle_v5 / P.v5_info / P.v5_refusal / P.v5_qb. Raises only on a programming
    error; the caller catches everything so a V5 failure never costs the run its other arms."""
    ensure_slots(P)
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
    upcoming = upcoming_from_markets(prows, player_map, sched, target_season, positions, {})
    if not len(upcoming):
        P.v5_info = {**info, "n_upcoming": 0, "version": VERSION}
        return
    upcoming = PV3.attach_market_environment(upcoming, envs)
    tgs = sorted({(r.team, r.game_id, int(r.week)) for r in upcoming.itertuples()})
    P.v5_qb = resolve_slate(tgs, ctx=ctx, avail=getattr(P, "avail", None), kick=kick, cutoff=run_ts)
    starters = {k: v.get("effective_projected_qb") for k, v in P.v5_qb.items()}
    upcoming = QF.apply_starters(upcoming.assign(qb_starter=False), starters)
    for r in upcoming.itertuples():
        if not r.env_known:
            P.v5_refusal[(r.player_id, r.game_id)] = "no market-implied game environment at the cutoff: v5 refuses rather than price a zero-point team"
    combined = build_prospective_rows(hist, upcoming)
    combined = pdist.add_ewma_features(combined, halflife=cfg["halflife"], season_carry=cfg["season_carry"], shrink_k=cfg["shrink_k"], priors=priors)
    combined = add_v2_features(combined, halflife=cfg["halflife"], season_carry=cfg["season_carry"], shrink_k=cfg["shrink_k"])
    combined = add_v3_features(DD.ensure_columns(combined))
    combined = F4.add_recency_features(combined)
    weeks = sorted({int(w) for w in upcoming.week})
    frame = F4.status_frame(root, range(2013, target_season + 1))
    tw = (frame.season == target_season) & frame.week.isin(weeks)
    frame.loc[tw, "report"] = None
    overrides = PV4.target_week_overrides(ctx, getattr(P, "avail", None), target_season, set(weeks))
    status = F4.StatusBook(frame, overrides=overrides, override_weeks=[(target_season, w) for w in weeks])
    combined = F4.add_absence_features(combined, status)
    pro_keys = {(t, g) for t, g, _ in tgs}
    combined = QF.add_qb_identity_features(combined, {k: v for k, v in starters.items() if k in pro_keys})
    teams = team_game_table(combined)
    P.bundle_v5 = M5.fit_bundle(combined, target_season, teams=teams, verbose=log)
    feat = combined[combined.is_prospective == True].reset_index(drop=True)   # noqa: E712
    ok = PV3.usable_rows(feat)
    n_dist = 0
    if ok.any():
        I = P.bundle_v5.intermediates(feat[ok], teams)
        for r in I.to_dict("records"):
            key = (r["player_id"], r["game_id"])
            res = P.v5_qb.get((r["team"], r["game_id"])) or {}
            r.update(QR.compact(res), qb_dependent_abstain=bool(res.get("qb_dependent_abstain")))
            P.feat_v5[key] = {k: PV4._plain(r.get(k)) for k in LEAN_KEYS}
            for stat, d in P.bundle_v5.distributions(r).items():
                P.data_v5[(r["player_id"], r["game_id"], stat)] = d
                n_dist += 1
            P.v5_inter[key] = {k: PV4._plain(v) for k, v in r.items() if isinstance(v, (int, float, np.floating, np.integer, bool, str)) or v is None}
    reasons = {}
    for v in P.v5_qb.values():
        reasons[v["qb_resolution_reason"]] = reasons.get(v["qb_resolution_reason"], 0) + 1
    P.v5_info = {**info, "version": VERSION, "inputs_version": INPUTS_VERSION, "qb_resolution_version": QR.QB_RESOLUTION_VERSION,
                 "n_upcoming": int(len(upcoming)), "n_env_known": int(upcoming.env_known.sum()), "n_distributions": n_dist,
                 "bundle_sha": P.bundle_v5.artifact_sha, "n_status_overrides": len(overrides), "target_weeks": weeks,
                 "qb_resolution": {"team_games": len(P.v5_qb), "by_reason": reasons,
                                   "substitutions": sorted(f"{t}:{v['depth_chart_qb1']}->{v['effective_projected_qb']}"
                                                           for (t, _g), v in P.v5_qb.items()
                                                           if v.get("qb_resolution_reason") == QR.QB1_OUT_PROMOTED_NEXT)},
                 "seconds": round(time.time() - t0, 1),
                 "injury_vintage": ((getattr(ctx, "injuries", None) or {}).get("meta") or {}).get("retrieved_at") if ctx else None}
    log(f"v5: {n_dist} distributions (bundle {P.bundle_v5.artifact_sha}) in {P.v5_info['seconds']}s; QB resolution {reasons}")
