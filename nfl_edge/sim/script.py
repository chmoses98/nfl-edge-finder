"""GAME-SCRIPT SUMMARY: what one coherent simulated game says about environment, team volume, player opportunity
and efficiency -- the inputs a handicapper builds a thesis from. Derived; research context; no authority.

The Weeks 1-3 autopsy put 64% of meaningful player-projection misses upstream of efficiency (opportunity and team
volume). The simulator already draws, on every row, the hierarchy that matters:

    GAME ENVIRONMENT (margin, total)  ->  TEAM VOLUME (plays, pass rate | that row's margin and total)
      ->  PLAYER OPPORTUNITY (carries, targets over the available players)  ->  EFFICIENCY (yards per touch)

but it persisted only contract probabilities. `script_summary` reads the SAME arrays the contracts were priced
from and summarises them. It is a pure function of the `SimResult`: it draws no random number, so writing it can
never change a projection (pinned by test).

What it cannot say, and says so. The simulator draws FINAL margin and total, not a scoring sequence: there is no
score-state path, no lead-change count and no time-leading. The nearest valid proxy is reported instead -- the
team's pass rate and volume CONDITIONAL on the final margin bucket of the row (leading by 14+, within one score,
trailing by 14+), which is exactly the script dependence the volume model encodes. Red-zone, route and snap
counts are not simulated and are absent rather than estimated.
"""
from __future__ import annotations

import numpy as np

SCRIPT_VERSION = "sim-script-1.0.0"
QS = (0.05, 0.25, 0.5, 0.75, 0.95)
MARGIN_STATES = (("lead14+", 14, None), ("lead7-13", 7, 13), ("within6", -6, 6), ("trail7-13", -13, -7), ("trail14+", None, -14))


def _q(arr) -> dict:
    a = np.asarray(arr, float)
    if a.size == 0:
        return {}
    out = {"mean": round(float(a.mean()), 3), "sd": round(float(a.std()), 3)}
    for q in QS:
        out[f"p{int(q * 100):02d}"] = round(float(np.quantile(a, q)), 3)
    return out


def _share(num, den):
    num, den = np.asarray(num, float), np.asarray(den, float)
    ok = den > 0
    if not ok.any():
        return None
    s = num[ok] / den[ok]
    return {"mean": round(float(s.mean()), 4), "sd": round(float(s.std()), 4),
            "p10": round(float(np.quantile(s, 0.10)), 4), "p90": round(float(np.quantile(s, 0.90)), 4)}


def _state_mask(margin_team, lo, hi):
    m = np.asarray(margin_team, float)
    mask = np.ones(m.shape, bool)
    if lo is not None:
        mask &= m >= lo
    if hi is not None:
        mask &= m <= hi
    return mask


def _names(ti) -> dict:
    df = getattr(ti, "players", None)
    out = {}
    if df is None or not hasattr(df, "columns"):
        return out
    idc = next((c for c in ("player_id", "gsis_id") if c in df.columns), None)
    if idc is None:
        return out
    for _, r in df.iterrows():
        out[r[idc]] = {"name": r.get("player_name") or r.get("player_display_name"), "position": r.get("position")}
    return out


def script_summary(res, gi, coherence: dict | None = None, *, top_players: int = 8) -> dict:
    """Environment, team volume, player opportunity and efficiency of one simulated game, from its own rows."""
    margin, total = np.asarray(res.margin, float), np.asarray(res.total, float)
    env = {"home_margin": _q(margin), "total": _q(total), "home_points": _q(res.home_points), "away_points": _q(res.away_points),
           "p_home_win": round(float(np.mean(margin > 0) + 0.5 * np.mean(margin == 0)), 4),
           "p_one_score": round(float(np.mean(np.abs(margin) <= 8)), 4),
           "p_within_3": round(float(np.mean(np.abs(margin) <= 3)), 4),
           "p_blowout_17plus": round(float(np.mean(np.abs(margin) >= 17)), 4),
           "p_total_10_over_centre": round(float(np.mean(total >= gi.total_line + 10)), 4),
           "p_total_10_under_centre": round(float(np.mean(total <= gi.total_line - 10)), 4),
           "centre": {"home_margin": gi.spread_home, "total": gi.total_line, "source": gi.center_source},
           "score_state_paths": "NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy"}
    teams = {}
    for ti in (gi.home, gi.away):
        T = res.team.get(ti.team) or {}
        if not T:
            continue
        mt = T.get("margin", margin if ti.home else -margin)
        vol = {k: _q(T[k]) for k in ("plays", "dropbacks", "pass_att", "designed_rush", "rush_att", "sacks", "scrambles", "targets", "points")
               if k in T}
        vol["pass_rate"] = _q(T["pass_rate"]) if "pass_rate" in T else None
        by_state = {}
        for name, lo, hi in MARGIN_STATES:
            msk = _state_mask(mt, lo, hi)
            if msk.sum() < 200:
                by_state[name] = {"share_of_rows": round(float(msk.mean()), 4), "n_rows": int(msk.sum()), "note": "too few rows"}
                continue
            by_state[name] = {"share_of_rows": round(float(msk.mean()), 4),
                              "pass_rate_mean": round(float(np.asarray(T["pass_rate"])[msk].mean()), 4),
                              "pass_att_mean": round(float(np.asarray(T["pass_att"])[msk].mean()), 2),
                              "rush_att_mean": round(float(np.asarray(T["rush_att"])[msk].mean()), 2),
                              "plays_mean": round(float(np.asarray(T["plays"])[msk].mean()), 2)}
        names = _names(ti)
        pl = []
        for pid, P in res.player.items():
            if P.get("team") != ti.team or str(pid).startswith("OTHER"):
                continue
            tg, ca = np.asarray(P.get("targets", 0), float), np.asarray(P.get("carries", 0), float)
            if tg.mean() + ca.mean() < 0.5:
                continue
            act = np.asarray(P.get("active", np.ones_like(tg)), bool)
            rec_y, rush_y = np.asarray(P.get("rec_yards", np.zeros_like(tg)), float), np.asarray(P.get("rush_yards", np.zeros_like(ca)), float)
            rec = {"player_id": pid, **names.get(pid, {}), "p_active": round(float(act.mean()), 4),
                   "targets": _q(tg), "carries": _q(ca), "receptions": _q(P.get("receptions", np.zeros_like(tg))),
                   "target_share": _share(tg, T["targets"]), "carry_share": _share(P.get("designed_carries", ca), T["designed_rush"]),
                   "yards_per_target": round(float(rec_y.sum() / tg.sum()), 3) if tg.sum() > 0 else None,
                   "yards_per_carry": round(float(rush_y.sum() / ca.sum()), 3) if ca.sum() > 0 else None}
            if "attempts" in P:
                rec["pass_attempts"] = _q(P["attempts"])
            # role certainty from the simulation itself: how wide the opportunity distribution is relative to its mean
            opp = tg + ca
            rec["opportunity_cv"] = round(float(opp.std() / opp.mean()), 3) if opp.mean() > 0 else None
            pl.append(rec)
        pl.sort(key=lambda r: -((r["targets"] or {}).get("mean", 0) + (r["carries"] or {}).get("mean", 0)))
        shares = [((r.get("target_share") or {}).get("mean") or 0.0) for r in pl]
        teams[ti.team] = {"home": ti.home, "volume": vol, "by_final_margin": by_state,
                          "target_concentration_hhi": round(float(sum(s * s for s in shares)), 4) if shares else None,
                          "players": pl[:top_players], "n_players_with_opportunity": len(pl)}
    return {"script_version": SCRIPT_VERSION, "game_id": res.game_id, "n_rows": int(res.n), "environment": env, "teams": teams,
            "coherence_ok": bool((coherence or {}).get("ok", True)),
            "not_simulated": ["score-state paths / lead changes", "red-zone trips", "routes and snaps", "drive counts"],
            "betting_authorized": False}
