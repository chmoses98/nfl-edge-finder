"""Live forward projections: the frozen models + as-of availability + gate with participation + forecast records.

Same numbers as `nfl.project.build` (same frozen models, same distributions, same gate) with these live additions:
  * only games that have not started at `now` (inside the horizon) are projected; nothing is generated for a started game;
  * the week's injury designations come from AS-OF observations (not the untimestamped nflverse final report) and drive
    the study's own availability rung (`diagnostics.corrections(S, inj)`: teammates OUT/DOUBTFUL vacate opportunity;
    own Questionable tag) and the gate's `participation` field;
  * every player row carries `participation{status,certainty,source,captured_utc,reasons}` and `role: "shadow"`;
  * forecast records (pf_core.prospective.FORECAST_FIELDS) are returned for archiving; segment tags for the monitoring
    scorecard (new team first 4 games, backup tiers, rookies) ride along as extra fields;
  * `authority: research_only` always. passing_tds is NEEDS IMPROVEMENT (the frozen winner lost to the incumbent on
    holdout): it is published labelled `NEEDS IMPROVEMENT` (and archived, which is exactly the prospective test of that
    finding); SIFT must not present it as a production number.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PF_ROOT = os.path.dirname(os.path.dirname(HERE))
if PF_ROOT not in sys.path:
    sys.path.insert(0, PF_ROOT)

from pf_core import VERSION as PF_VERSION  # noqa: E402
from pf_core import availability as av  # noqa: E402
from pf_core import gate  # noqa: E402

from nfl import data as D  # noqa: E402
from nfl import diagnostics as DG  # noqa: E402
from nfl import evaluate as EV  # noqa: E402
from nfl import gate_eval as GE  # noqa: E402
from nfl import gate_nfl as G  # noqa: E402
from nfl import pipeline as P  # noqa: E402
from nfl import project as PR  # noqa: E402
from nfl.live import availability as LA  # noqa: E402

MODEL_ID = "pf-nfl"
OPP_FAMILY = {"receptions": "targets", "receiving_yards": "targets", "rushing_yards": "carries", "completions": "passing_attempts",
              "passing_yards": "passing_attempts", "passing_tds": "passing_attempts"}


def _sha() -> str:
    return PR._sha()


def segments_for(S: dict) -> pd.DataFrame:
    """Monitoring tags for every pf row (computed from point-in-time history): first four games with a new team, backup
    tiers (RB2+/TE2+/WR3+ by the team's EWMA target-per-attempt rank), rookies."""
    pf = S["pf"]
    tier, _rb = DG._tiers(pf)
    key = pf[["player_id", "kickoff_utc", "team", "y_observed"]].copy()
    key["_i"] = np.arange(len(pf))
    key = key.sort_values(["player_id", "kickoff_utc"])
    games_with_team = np.zeros(len(pf), int)
    ever_other = np.zeros(len(pf), bool)
    for _pid, g in key.groupby("player_id", sort=False):
        teams = g.team.to_numpy()
        idx = g._i.to_numpy()
        run = 0
        other = False
        for j in range(len(g)):
            if j > 0 and teams[j] != teams[j - 1]:
                run = 0
                other = True
            games_with_team[idx[j]] = run          # games with the CURRENT team before this one
            ever_other[idx[j]] = other
            run += 1
    seg = pd.DataFrame({
        "new_team_first4": (ever_other & (games_with_team < 4)),
        "games_with_team_before": games_with_team,
        "tier": tier,
        "backup": np.isin(tier, ["RB2+", "TE2+", "WR3+"]),
        "rookie": (pf.is_rookie == 1).to_numpy(),
    }, index=pf.index)
    return seg


def participation_for(rows: list[dict], now_utc: str, pfr: pd.DataFrame, latest: dict) -> list[dict]:
    """One participation call per forward player row (pf_core resolve + the QB-starter cross-check)."""
    qb1 = LA.depth_qb1(latest)
    out = []
    for _, r in pfr.iterrows():
        p = av.resolve_participation(latest, r.game_id, r.player_id, now_utc)
        d = {"status": p.status, "certainty": p.certainty, "source": p.source, "captured_utc": p.captured_utc,
             "age_minutes": None if p.age_minutes is None else round(p.age_minutes, 1), "reasons": list(p.reasons)}
        if r.position == "QB":
            top = qb1.get((r.game_id, r.team))
            if top and top != r.player_id and d["status"] not in (av.CONFIRMED_OUT, av.LIKELY_OUT):
                d["status"] = av.UNCERTAIN
                d["reasons"].append(f"depth chart (PROJECTED) lists {top} as QB1, not the modelled starter")
            elif top == r.player_id:
                d["reasons"].append("depth chart (PROJECTED) lists him as QB1")
        out.append(d)
    return out


def _live_inj(rows_latest: dict, season: int, week: int) -> pd.DataFrame:
    hist = D.injuries()
    hist = hist[~((hist.season == season) & (hist.week == week))]
    live = LA.injury_table(rows_latest, season, week)
    return pd.concat([hist, live], ignore_index=True)


def build(S: dict, frozen: dict, summary: dict | None, now_utc: str, events: list[dict], obs_rows: list[dict],
          coverage: dict | None = None, state_info: dict | None = None) -> dict:
    """Returns {"doc": sift.projections.v1 payload, "forecasts": [records], "stats": {...}}."""
    pf, tf = S["pf"], S["tf"]
    ev_ids = {e["event_id"]: e for e in events}
    fwd_all = (pf.split == "forward").to_numpy()
    in_window = pf.game_id.isin(ev_ids).to_numpy()
    fwd = fwd_all & in_window
    stats = {"forward_rows_total": int(fwd_all.sum()), "forward_rows_in_window": int(fwd.sum()),
             "skipped_not_in_window": int((fwd_all & ~in_window).sum())}
    blk = int(pf.loc[fwd_all, "block"].min()) if fwd_all.any() else None
    season, week = (blk // 100, blk % 100) if blk else (None, None)
    if not fwd.any():
        stats["note"] = "no forward rows inside the horizon (nothing to project: all games started, out of window, or state is a replay)"
        return {"doc": None, "forecasts": [], "stats": stats}
    latest = LA.merged_asof(obs_rows, now_utc)
    pfr = pf.loc[fwd]
    parts = participation_for(obs_rows, now_utc, pfr, latest)
    part_by_idx = dict(zip(pfr.index, parts))
    inj = _live_inj(latest, season, week) if season else None
    corr = DG.corrections(S, inj)["preds"] if inj is not None else {}
    readiness = {f["family"]: f for f in (summary or {}).get("families", [])}
    fams_out = {}
    for fam, fz in frozen.items():
        r = readiness.get(fam, {})
        fams_out[fam] = {"readiness": r.get("readiness", "SHADOW VALIDATION"), "model": fz["model"], "reason": r.get("readiness_reason", ""),
                         "role": "shadow"}
    asof_state = S.get("data_asof_utc") or S.get("built_utc") or now_utc
    cap_times = [p["captured_utc"] for p in parts if p["captured_utc"]]
    newest_input = max([asof_state] + cap_times, key=lambda x: av._ts(x))
    data_asof = av.iso(min(av._ts(now_utc), av._ts(newest_input)))
    pf_h = G.add_histories(pf, GE.HIST_COLS).merge(G.opp_season_games(tf), on=["game_id", "team"], how="left")
    seg = segments_for(S)
    vac = DG._vacated(S, inj)["vac"] if inj is not None else None
    # ---- games / team families
    games, forecasts = [], []
    tfw = tf[(tf.split == "forward") & tf.game_id.isin(ev_ids)]
    for gid, gg in tfw.groupby("game_id"):
        g0 = gg.iloc[0]
        teams = []
        for _, t in gg.iterrows():
            for fam in P.TEAM_FAMILIES:
                fz = frozen[fam]
                mu = GE.model_mean(S, corr, fam, fz["model"], "forward")[t.name]
                if not np.isfinite(mu):
                    stats["team_skipped_no_inputs"] = stats.get("team_skipped_no_inputs", 0) + 1
                    continue
                d = EV.make(fz["dist_params"], np.array([mu]))
                teams.append({"team": t.team, "family": fam, "mean": round(float(mu), 2),
                              "p10": int(d.quantile(0.1)[0]), "p90": int(d.quantile(0.9)[0])})
                forecasts.append(_record(fam, fz, d, 0, gid, ev_ids[gid]["start_utc"], t.team, t.team, t.team, now_utc, data_asof,
                                         fams_out[fam]["readiness"], None, None))
        home = gg[gg.home == 1].team.iloc[0] if (gg.home == 1).any() else None
        away = gg[gg.home == 0].team.iloc[0] if (gg.home == 0).any() else None
        games.append({"game_id": gid, "start_utc": ev_ids[gid]["start_utc"], "home": home, "away": away,
                      "closing_spread_home": float(-gg[gg.home == 1].spread_team.iloc[0]) if home and pd.notna(gg[gg.home == 1].spread_team.iloc[0]) else None,
                      "total_line": float(g0.total_line) if pd.notna(g0.total_line) else None, "teams": teams})
    # ---- players
    players = []
    idx_fwd = np.where(fwd)[0]
    pos_in_fwd = {i: k for k, i in enumerate(idx_fwd)}
    for fam, s in P.PLAYER_FAMILIES.items():
        fz = frozen[fam]
        m = fwd & S["pops"][s["pop"]]
        mu_all = GE.model_mean(S, corr, fam, fz["model"], "forward")
        nan_inputs = int((m & ~np.isfinite(mu_all)).sum())
        if nan_inputs:
            stats.setdefault("player_skipped_no_inputs", {})[fam] = nan_inputs
        m &= np.isfinite(mu_all)
        idx = np.where(m)[0]
        if not len(idx):
            continue
        mu = mu_all[idx]
        dist = EV.make(fz["dist_params"], mu)
        mu = dist.mean
        oppfam = OPP_FAMILY.get(fam)
        if fam == "anytime_td":
            opp_mu = (GE.model_mean(S, corr, "targets", frozen["targets"]["model"], "forward") +
                      GE.model_mean(S, corr, "carries", frozen["carries"]["model"], "forward"))[idx]
            od = None
        else:
            of_ = oppfam or fam
            opp_mu = GE.model_mean(S, corr, of_, frozen[of_]["model"], "forward")[idx]
            od = EV.make(frozen[of_]["dist_params"], opp_mu) if oppfam else None
            if od is not None:
                opp_mu = od.mean
        of = GE.opp_factor(S, fam)
        pp = [part_by_idx[pf.index[i]] for i in idx]
        res = G.run(fam, pf_h.iloc[idx], mu, dist, s["y"], opp_mean=opp_mu, opp_factor=(of[idx] if of is not None else None),
                    injury=[_gate_injury(p["status"]) for p in pp], rungs=s["rungs"], now_utc=now_utc,
                    participation=[p["status"] for p in pp], participation_reasons=[p["reasons"] for p in pp],
                    data_asof_utc=data_asof)
        rungs = sorted(set(s["rungs"] + ([1] if fam == "anytime_td" else [])))
        thr = {k: dist.prob_ge(k) for k in rungs}
        for j, i in enumerate(idx):
            r = pf.iloc[i]
            rh = pf_h.iloc[i]
            adj = []
            if fz["model"] in ("D", "F", "D_vac", "F_vac", "E", "F_av", "D_av", "F_qs", "D_qs"):
                adj.append(f"Team volume uses the market line (spread {r.spread_team:+.1f}, total {r.total_line:.1f}) and the opponent's "
                           f"schedule-adjusted defensive rating.")
            if of is not None and abs(np.log(max(of[i], 1e-6))) > 0.02:
                adj.append(f"Opponent efficiency factor x{of[i]:.2f} (fitted elasticity on 2016-2021).")
            if vac is not None and fz["model"].endswith(("_vac", "_av")):
                v = vac.iloc[i]
                if v.vac_tpa_inj > 0.02 or v.vac_cs_inj > 0.02:
                    adj.append(f"Teammates listed OUT/DOUBTFUL vacate {v.vac_tpa_inj:.0%} of team targets / {v.vac_cs_inj:.0%} of carries; "
                               f"shares renormalised.")
            if r.career_games < 3:
                adj.append("Fewer than 3 career games: projection leans on the positional prior.")
            part = pp[j]
            gate_res = res[j]
            sg = seg.iloc[i]
            segd = {"new_team_first4": bool(sg.new_team_first4), "tier": str(sg.tier), "backup": bool(sg.backup), "rookie": bool(sg.rookie)}
            players.append({
                "player_id": r.player_id, "name": r.player_display_name, "team": r.team, "opponent": r.opp, "game_id": r.game_id,
                "position": r.position, "family": fam, "mean": round(float(mu[j]), 3), "median": int(dist.median[j]),
                "p10": int(dist.quantile(0.1)[j]), "p90": int(dist.quantile(0.9)[j]),
                "thresholds": {str(k): round(float(thr[k][j]), 4) for k in rungs},
                "opportunity": ({"family": oppfam, "mean": round(float(opp_mu[j]), 2), "p10": int(od.quantile(0.1)[j]),
                                 "p90": int(od.quantile(0.9)[j])} if od is not None else
                                {"family": "touches" if fam == "anytime_td" else fam, "mean": round(float(opp_mu[j]), 2)}),
                "opponent_adjustment": {"factor": round(float(of[i]), 3) if of is not None else 1.0,
                                        "sample_games": int(rh.opp_games_season) if pd.notna(rh.opp_games_season) else None},
                "adjustments": adj, "participation": part, "role": "shadow",
                "readiness": fams_out[fam]["readiness"],
                "gate": {"status": gate_res["status"], "findings": [
                    {k: f[k] for k in ("check", "severity", "what", "category", "action")} for f in gate_res["findings"]]},
                "segments": segd, "data_asof_utc": data_asof})
            forecasts.append(_record(fam, fz, None, 0, r.game_id,
                                     ev_ids[r.game_id]["start_utc"], r.player_id, r.player_display_name, r.team, now_utc, data_asof,
                                     fams_out[fam]["readiness"], gate_res["status"], part["status"], segd, part,
                                     dist_row=(dist, j), position=r.position))
    # team reconciliation for the slate
    recon = []
    tgt = [p for p in players if p["family"] == "targets"]
    if tgt:
        tdf = pd.DataFrame(tgt).groupby(["game_id", "team"])["mean"].sum()
        tg_rate = float((tf.tm_targets / tf.tm_attempts)[tf.season.between(2016, 2021)].mean())
        for (gid, team), v in tdf.items():
            tm = [t for g in games if g["game_id"] == gid for t in g["teams"] if t["team"] == team and t["family"] == "team_pass_attempts"]
            if tm:
                rr = gate.team_reconciliation(float(v), tm[0]["mean"] * tg_rate, f"{team} projected targets (listed population) vs team")
                recon.append({"game_id": gid, "team": team, "status": rr["status"], "ratio": rr.get("ratio"),
                              "note": "population players only (WR/TE/RB with role); ratio < 1 is expected"})
    stats["players"] = len(players)
    stats["games"] = len(games)
    stats["gate_status"] = gate.summarize([{"status": p["gate"]["status"], "findings": p["gate"]["findings"]} for p in players])["status_counts"] if players else {}
    stats["participation"] = _count(p["participation"]["status"] for p in players)
    stats["participation_certainty"] = _count(p["participation"]["certainty"] for p in players)
    qb_mis = [(p["name"], p["team"]) for p in players if p["family"] == "passing_attempts" and
              any("not the modelled starter" in r for r in p["participation"]["reasons"])]
    stats["qb_starter_mismatch"] = qb_mis
    doc = {"schema": "sift.projections.v1", "sport": "NFL", "generated_utc": av.iso(av._ts(now_utc)), "data_asof_utc": data_asof,
           "mode": "live_upcoming", "season": season, "week": week,
           "model": {"id": MODEL_ID, "version": f"pf-{PF_VERSION}+{_sha()}", "authority": "research_only"},
           "role": "shadow",
           "conditioning": "Player projections are CONDITIONAL ON THE PLAYER PARTICIPATING (DNP = void), the prop-settlement convention. "
                           "Each row carries the point-in-time participation call (status, certainty, source, capture time). OUT players are "
                           "written with gate BLOCK (numbers withheld by SIFT); QUESTIONABLE/DOUBTFUL/UNVERIFIED with REVIEW. "
                           "passing_tds is NEEDS IMPROVEMENT (the frozen winner lost to the incumbent on holdout): shadow-only, not for display.",
           "families": fams_out, "games": games, "players": players, "team_reconciliation": recon,
           "availability": coverage or {}, "state": state_info or {},
           "gate_summary": gate.summarize([{"status": p["gate"]["status"], "findings": p["gate"]["findings"]} for p in players])}
    return {"doc": doc, "forecasts": forecasts, "stats": stats}


def _count(it):
    from collections import Counter
    return dict(Counter(it))


def _gate_injury(status: str) -> str:
    return {av.CONFIRMED_OUT: "OUT", av.LIKELY_OUT: "DOUBTFUL", av.UNCERTAIN: "QUESTIONABLE", av.LIKELY_ACTIVE: "PROBABLE",
            av.CONFIRMED_ACTIVE: "ACTIVE", av.UNVERIFIED: "UNKNOWN"}[status]


def _record(fam, fz, dist, _unused, game_id, start_utc, entity_id, name, team, now_utc, data_asof, readiness, gate_status,
            participation, segments=None, part=None, dist_row=None, position=None) -> dict:
    d, j = (dist_row if dist_row is not None else (dist, 0))
    probs = d.P[j]
    rec = {"sport": "NFL", "family": fam, "model_id": MODEL_ID, "model_role": "challenger", "model_version": f"pf-{PF_VERSION}+{_sha()}",
           "game_id": game_id, "game_start_utc": start_utc, "entity_id": entity_id, "entity_name": name, "team": team,
           "generated_utc": av.iso(av._ts(now_utc)), "data_asof_utc": data_asof, "mean": float(d.mean[j]), "lo": int(d.lo),
           "probs": [float(x) for x in probs], "gate_status": gate_status, "participation": participation, "readiness": readiness,
           "role": "shadow", "authority": "research_only", "frozen_model": fz["model"]}
    if segments is not None:
        rec["segments"] = segments
    if part is not None:
        rec["participation_certainty"] = part["certainty"]
        rec["participation_source"] = part["source"]
        rec["participation_captured_utc"] = part["captured_utc"]
    if position:
        rec["position"] = position
    return rec
