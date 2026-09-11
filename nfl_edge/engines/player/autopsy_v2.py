"""PLAYER AUTOPSY v2: which component of a v2 player projection missed, in the order the projection was built.

A DATA_PLAYER_DIST record carries its decomposition (`distribution_summary` / `feature_lineage`): the availability
state and P(plays), the projected team volume (pass attempts or carries), the player's projected share of it, the
projected snap share, the QB-environment flag, the opportunity mean, the efficiency and the fitted distribution's
quantiles. Postgame, every component is placed against the box score and the FIRST component out of range in the
causal chain is the classification:

    AVAILABILITY_MISS           expected to play, provably did not (or the reverse)
    SNAP_SHARE_MISS             played, but the offence-snap share was outside range of the projection
    ROUTE_PARTICIPATION_MISS    route share outside range  -- routes are not in free nflverse data, so this is
                                INSUFFICIENT_DATA unless the record carries a route projection AND the result book a
                                route count (it currently never does; the code path exists so the label is honest)
    TARGET_SHARE_MISS           target share of team attempts outside range
    CARRY_SHARE_MISS            carry share of team carries outside range
    TEAM_VOLUME_MISS            team attempts / carries outside range of the projection (share was right)
    QB_ENVIRONMENT_MISS         a different quarterback threw the team's attempts than the one the projection assumed
    EFFICIENCY_MISS             opportunity right, yards / receptions / TDs per opportunity outside range
    TAIL_SHAPE_MISS             every component within range, but the actual sat beyond the model's 2.5/97.5 band:
                                the location was right and the fitted family's tail was wrong
    UNEXPLAINED_VARIANCE        large standardised miss with no component out of range and inside the tail band
    NO_LARGE_MISS               |robust z| below the large-miss threshold and no component off
    INSUFFICIENT_DATA           participation unproven, no decomposition, or no quantiles

Deterministic, threshold-driven, feeds nothing. Thresholds are named once below.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone

from nfl_edge.settlement.results import ResultBook
from nfl_edge.shadow.player_autopsy import IQR_FLOOR, LOG_RATIO_LARGE, TEAM_VOLUME_LOG_RATIO, Z_LARGE, _percentile, team_volume

AUTOPSY_VERSION = "autopsy-2.0.0"
SHARE_ABS_LARGE = 0.10               # absolute share miss (targets/carries/snaps) that counts as "off"
SHARE_LOG_LARGE = math.log(1.5)
TAIL_LO, TAIL_HI = "p025", "p975"

AVAILABILITY_MISS = "AVAILABILITY_MISS"
SNAP_SHARE_MISS = "SNAP_SHARE_MISS"
ROUTE_PARTICIPATION_MISS = "ROUTE_PARTICIPATION_MISS"
TARGET_SHARE_MISS = "TARGET_SHARE_MISS"
CARRY_SHARE_MISS = "CARRY_SHARE_MISS"
TEAM_VOLUME_MISS = "TEAM_VOLUME_MISS"
QB_ENVIRONMENT_MISS = "QB_ENVIRONMENT_MISS"
EFFICIENCY_MISS = "EFFICIENCY_MISS"
TAIL_SHAPE_MISS = "TAIL_SHAPE_MISS"
UNEXPLAINED_VARIANCE = "UNEXPLAINED_VARIANCE"
NO_LARGE_MISS = "NO_LARGE_MISS"
INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
CLASSES = (AVAILABILITY_MISS, SNAP_SHARE_MISS, ROUTE_PARTICIPATION_MISS, TARGET_SHARE_MISS, CARRY_SHARE_MISS, TEAM_VOLUME_MISS,
           QB_ENVIRONMENT_MISS, EFFICIENCY_MISS, TAIL_SHAPE_MISS, UNEXPLAINED_VARIANCE, NO_LARGE_MISS, INSUFFICIENT_DATA)

OPPORTUNITY_OF = {"passing_yards": "attempts", "completions": "attempts", "passing_tds": "attempts", "interceptions": "attempts",
                  "attempts": "attempts", "rushing_yards": "carries", "carries": "carries", "receiving_yards": "targets",
                  "receptions": "targets", "touchdowns": "touches", "rush_rec_yards": "touches", "qb_rushing_yards": "carries"}
SHARE_KIND = {"targets": "target", "carries": "carry", "attempts": None, "touches": None}


def _f(x):
    try:
        return None if x is None else float(x)
    except (TypeError, ValueError):
        return None


def _off(actual, projected, *, abs_tol=None, log_tol=None):
    if actual is None or projected is None:
        return None, None
    if abs_tol is not None:
        d = actual - projected
        return abs(d) > abs_tol, d
    lr = math.log((actual + 0.5) / (projected + 0.5))
    return abs(lr) > log_tol, lr


def _team_attempts_by_passer(book: ResultBook, game_id: str, team: str) -> dict:
    """Pass attempts per passer on one team in one game, from the player rows already in the result book."""
    out = {}
    for (gid, pid), pr in book.players.items():
        if gid != game_id or pr.team != team:
            continue
        a = pr.stats.get("attempts")
        if a:
            out[pid] = float(a)
    return out


def _team_offense_snaps(book: ResultBook, game_id: str, team: str) -> float | None:
    """The team's offensive snap count in one game: the most snaps any of its players took (a lineman plays them all)."""
    vals = [pr.offense_snaps for (gid, _), pr in book.players.items() if gid == game_id and pr.team == team and pr.offense_snaps is not None]
    return float(max(vals)) if vals else None


def diagnose(rec: dict, book: ResultBook, *, now: datetime | None = None) -> dict:
    """One settled v2 PLAYER projection record (DATA arm) -> one autopsy record."""
    now = now or datetime.now(timezone.utc)
    gid, pid, stat, team = rec.get("game_id"), rec.get("subject_id"), rec.get("stat_family"), rec.get("team") or rec.get("subject_team")
    ds, fl = rec.get("distribution_summary") or {}, rec.get("feature_lineage") or {}
    out = {"record_id": rec.get("record_id"), "autopsy_version": AUTOPSY_VERSION, "evaluated_at": now.isoformat(), "snapshot_id": rec.get("snapshot_id"),
           "game_id": gid, "player_id": pid, "player_name": rec.get("subject_name"), "team": team, "stat": stat, "model_arm": rec.get("model_arm"),
           "ticker": rec.get("ticker"), "threshold": rec.get("threshold"), "horizon_label": rec.get("horizon_label"),
           "projected": {"p_plays": _f(fl.get("p_plays")), "availability_state": fl.get("availability_state"), "team_volume": _f(fl.get("projected_team_volume")),
                         "share": _f(fl.get("projected_share")), "snap_share": _f(fl.get("projected_snap_share")), "route_share": _f(fl.get("projected_route_share")),
                         "qb_id": fl.get("projected_qb_id"), "opportunity": _f(ds.get("mu_opp")), "stat_mean": _f(ds.get("mu")),
                         "efficiency": (None if not ds.get("mu_opp") else _f(ds.get("mu")) / _f(ds.get("mu_opp"))), "quantiles": ds.get("quantiles")},
           "actual": {}, "components": {}, "robust_z": None, "percentile": None, "large_miss": None,
           "classification": INSUFFICIENT_DATA, "evidence": []}
    pj = out["projected"]
    pr = book.player(gid, pid) if gid and pid else None
    if pj["opportunity"] is None and pj["stat_mean"] is None:
        out["evidence"].append("record carries no decomposition (not a DATA arm record?)"); return out
    if pr is None:
        if pj["p_plays"] is not None and pj["p_plays"] >= 0.5 and gid in book.games_with_snaps and gid in book.games_with_player_stats:
            out["classification"] = AVAILABILITY_MISS; out["evidence"].append("expected to play, absent from complete usage tables")
        else:
            out["evidence"].append("player has neither a statistics row nor a snap row for this game")
        return out
    if pr.played is None:
        out["evidence"].append("participation unproven from free data"); return out
    actual = pr.stat_value(stat) if stat != "rush_rec_yards" else ((pr.stats.get("rushing_yards") or 0.0) + (pr.stats.get("receiving_yards") or 0.0))
    if actual is None and pr.played:
        actual = 0.0
    a = out["actual"]
    a.update({"played": pr.played, "stat": actual, "snaps": pr.offense_snaps, "targets": pr.stats.get("targets"), "carries": pr.stats.get("carries"),
              "attempts": pr.stats.get("attempts")})
    # 1. availability
    if pr.played is False:
        out["classification"] = AVAILABILITY_MISS if (pj["p_plays"] is None or pj["p_plays"] >= 0.5) else NO_LARGE_MISS
        out["evidence"].append(f"active, never took a snap; P(plays) was {pj['p_plays']}"); return out
    # standardised surprise from the record's own quantiles
    q = pj["quantiles"] or {}
    p50, p25, p75 = _f(q.get("p50")), _f(q.get("p25")), _f(q.get("p75"))
    if actual is not None and None not in (p50, p25, p75):
        out["robust_z"] = (actual - p50) / max((p75 - p25) / 1.349, IQR_FLOOR)
        out["percentile"] = _percentile(q, actual)
    z = out["robust_z"]
    out["large_miss"] = bool(z is not None and abs(z) >= Z_LARGE)
    opp_col = OPPORTUNITY_OF.get(stat)
    tv = team_volume(book, gid, team, "attempts" if opp_col in ("attempts", "targets") else ("carries" if opp_col == "carries" else None)) if team else None
    team_actual = _f(tv.get("actual")) if tv else None
    a["team_volume"] = team_actual
    comps = out["components"]
    # 2. snap share
    team_snaps = _team_offense_snaps(book, gid, team) if team else None
    if pj["snap_share"] is not None and pr.offense_snaps is not None and team_snaps:
        a["snap_share"] = pr.offense_snaps / team_snaps
        comps["snap_share"] = _off(a["snap_share"], pj["snap_share"], abs_tol=SHARE_ABS_LARGE)
    # 3. route participation: only when both sides exist
    if pj["route_share"] is not None and pr.stats.get("routes") is not None and team_actual:
        a["route_share"] = float(pr.stats["routes"]) / team_actual
        comps["route_share"] = _off(a["route_share"], pj["route_share"], abs_tol=SHARE_ABS_LARGE)
    # 4. share of team volume
    kind = SHARE_KIND.get(opp_col)
    if kind and pj["share"] is not None and team_actual:
        mine = _f(pr.stats.get("targets" if kind == "target" else "carries"))
        if mine is not None:
            a[f"{kind}_share"] = mine / team_actual
            comps[f"{kind}_share"] = _off(a[f"{kind}_share"], pj["share"], abs_tol=SHARE_ABS_LARGE)
    # 5. team volume
    if pj["team_volume"] is not None and team_actual is not None:
        comps["team_volume"] = _off(team_actual, pj["team_volume"], log_tol=TEAM_VOLUME_LOG_RATIO)
    # 6. QB environment
    if pj["qb_id"] and team and gid:
        by = _team_attempts_by_passer(book, gid, team)
        if by:
            top = max(by, key=by.get)
            a["qb_id"] = top; a["qb_attempt_share"] = by[top] / sum(by.values())
            comps["qb_environment"] = (top != pj["qb_id"] and a["qb_attempt_share"] >= 0.5, None)
    # 7. opportunity and efficiency
    if opp_col == "touches":
        t, c = pr.stats.get("targets"), pr.stats.get("carries")
        a["opportunity"] = None if t is None and c is None else float((t or 0) + (c or 0))
    elif opp_col:
        a["opportunity"] = _f(pr.stats.get(opp_col))
    if a.get("opportunity") is not None and pj["opportunity"] is not None:
        comps["opportunity"] = _off(a["opportunity"], pj["opportunity"], log_tol=LOG_RATIO_LARGE)
    if a.get("opportunity") and actual is not None and pj["efficiency"]:
        a["efficiency"] = actual / a["opportunity"]
        comps["efficiency"] = (abs(math.log((a["efficiency"] + 1e-6) / (pj["efficiency"] + 1e-6))) > LOG_RATIO_LARGE,
                               math.log((a["efficiency"] + 1e-6) / (pj["efficiency"] + 1e-6)))
    # ---- classification: first component off in causal order
    order = [("snap_share", SNAP_SHARE_MISS), ("route_share", ROUTE_PARTICIPATION_MISS), ("qb_environment", QB_ENVIRONMENT_MISS),
             ("team_volume", TEAM_VOLUME_MISS), ("target_share", TARGET_SHARE_MISS), ("carry_share", CARRY_SHARE_MISS),
             ("opportunity", None), ("efficiency", EFFICIENCY_MISS)]
    if not out["large_miss"] and not any(v and v[0] for v in comps.values()):
        out["classification"] = NO_LARGE_MISS if z is not None else INSUFFICIENT_DATA
        if z is None:
            out["evidence"].append("no quantiles to standardise the miss and no component out of range")
        return out
    for key, label in order:
        v = comps.get(key)
        if v and v[0]:
            if key == "opportunity":
                # opportunity off with the shares and volume inside range: attribute by whichever share/volume is more off
                tvv = comps.get("team_volume"); sh = comps.get("target_share") or comps.get("carry_share")
                if tvv and tvv[1] is not None and (sh is None or abs(tvv[1]) >= abs(sh[1] or 0)):
                    out["classification"] = TEAM_VOLUME_MISS
                elif sh:
                    out["classification"] = TARGET_SHARE_MISS if "target_share" in comps else CARRY_SHARE_MISS
                else:
                    out["classification"] = TEAM_VOLUME_MISS if opp_col == "attempts" else UNEXPLAINED_VARIANCE
                out["evidence"].append(f"projected opportunity {pj['opportunity']:.1f}, actual {a['opportunity']:.0f}")
            else:
                out["classification"] = label
                out["evidence"].append(f"{key}: projected {pj.get(key if key != 'target_share' and key != 'carry_share' else 'share')}, actual {a.get(key)}")
            return out
    # nothing off but a large miss: tail vs unexplained
    lo, hi = _f(q.get(TAIL_LO)), _f(q.get(TAIL_HI))
    if actual is not None and lo is not None and hi is not None and (actual < lo or actual > hi):
        out["classification"] = TAIL_SHAPE_MISS
        out["evidence"].append(f"components within range; actual {actual:g} outside the model's [{lo:g}, {hi:g}] band")
    else:
        out["classification"] = UNEXPLAINED_VARIANCE
        out["evidence"].append("components within range; the outcome sits inside the model's tail band but far from the median")
    return out


def rank(records: list) -> list:
    return sorted(records, key=lambda r: (-(abs(r["robust_z"]) if r.get("robust_z") is not None else -1), r.get("game_id") or "", r.get("player_id") or "", r.get("stat") or ""))


def summarize(records: list) -> dict:
    by = {}
    for r in records:
        by[r["classification"]] = by.get(r["classification"], 0) + 1
    by_stat = {}
    for r in records:
        by_stat.setdefault(r.get("stat"), {}).setdefault(r["classification"], 0)
        by_stat[r.get("stat")][r["classification"]] += 1
    return {"n": len(records), "by_classification": by, "by_stat": by_stat, "version": AUTOPSY_VERSION}
