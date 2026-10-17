#!/usr/bin/env python3
"""Forward projections (sift.projections.v1) for the next unplayed NFL week, from the validated frozen models.

Candidate players for an upcoming game: QB/RB/WR/TE who played for that team in one of its previous 3 games and are on
its current weekly roster (status ACT/INA/RES is a roster fact; RES players are dropped). Players designated OUT on the
week's injury report are still written (gate BLOCK, so the app can explain the withholding). Every number comes from the
same functions as the walk-forward backtest: upcoming games are rows with NaN outcomes in the same frame.

If no unplayed week exists (offseason), the most recent completed week is re-projected using only prior data and labelled
`mode: "replay_most_recent_week"`.

Usage: python -m nfl.project   (from research/projection_foundation; needs the stage-1 cache from run_walkforward)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PF_ROOT = os.path.dirname(HERE)
sys.path.insert(0, PF_ROOT)

from pf_core import VERSION as PF_VERSION  # noqa: E402
from pf_core import gate  # noqa: E402

from nfl import data as D  # noqa: E402
from nfl import evaluate as EV  # noqa: E402
from nfl import gate_nfl as G  # noqa: E402
from nfl import pipeline as P  # noqa: E402

RESULTS = os.path.join(PF_ROOT, "results")


def upcoming_block(sched: pd.DataFrame) -> tuple[int | None, str]:
    """Next block with an unplayed regular-season game in the latest season; else the latest played block (replay)."""
    s = sched[sched.season == sched.season.max()]
    un = s[s.home_score.isna()]
    if len(un):
        return int(un.block.min()), "upcoming_week"
    return int(s.block.max()), "replay_most_recent_week"


def upcoming_rows(sched: pd.DataFrame, pg: pd.DataFrame, block: int, mode: str) -> pd.DataFrame:
    tg = D.team_games(sched)
    games = tg[(tg.block == block) & (~tg.played if mode == "upcoming_week" else True)]
    if mode == "replay_most_recent_week":
        pg = pg[pg.block < block]
    hist = pg[pg.block < block].sort_values("kickoff_utc")
    roster = D.weekly_roster()
    season, week = block // 100, block % 100
    ros = roster[(roster.season == season) & (roster.week == week)]
    if ros.empty:   # roster for the week not published yet: use the latest week available
        ros = roster[roster.season == season]
        ros = ros[ros.week == ros.week.max()]
    rows = []
    for _, g in games.iterrows():
        th = hist[hist.team == g.team]
        last3 = th.drop_duplicates("game_id").sort_values("kickoff_utc").game_id.unique()[-3:]
        cand = th[th.game_id.isin(last3)].sort_values("kickoff_utc").drop_duplicates("player_id", keep="last")
        on = ros[(ros.team == g.team) & ros.status.isin(["ACT", "INA"])].gsis_id
        cand = cand[cand.player_id.isin(set(on))]
        for _, c in cand.iterrows():
            rows.append({"player_id": c.player_id, "player_display_name": c.player_display_name, "position": c.position,
                         "season": g.season, "week": g.week, "game_id": g.game_id, "team": g.team, "opponent_team": g.opp,
                         "block": g.block, "kickoff_utc": g.kickoff_utc, "gameday": g.gameday, "opp": g.opp, "home": g.home,
                         "spread_team": g.spread_team, "total_line": g.total_line, "implied_total": g.implied_total,
                         "indoor": g.indoor, "qb_id": g.qb_id, "wind": np.nan, "zero_row": False,
                         "rookie_season": c.rookie_season, "draft_round": c.draft_round, "is_rookie": int(c.rookie_season == g.season),
                         "qb_starter": bool(c.position == "QB" and c.player_id == g.qb_id)})
    up = pd.DataFrame(rows)
    for col in D.STAT_COLS + ["any_td", "n_td", "touches", "target_share", "carry_share", "pass_share", "tm_attempts",
                              "tm_carries", "tm_targets", "points", "offense_snaps", "offense_pct"]:
        up[col] = np.nan
    return up


def _asof():
    man = os.path.join(D.RAW, "_manifest.jsonl")
    ts = []
    if os.path.exists(man):
        for line in open(man):
            r = json.loads(line)
            if any(k in r.get("path", "") for k in ("stats_player_week_2026", "injuries_2026", "schedules/games.csv", "roster_weekly_2026")):
                ts.append(r.get("retrieved_at"))
    return max(ts) if ts else None


def _sha():
    try:
        return subprocess.check_output(["git", "-C", PF_ROOT, "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def build(S, frozen: dict, summary: dict | None, corr: dict, out_path: str, now_utc: str | None = None) -> dict:
    from nfl import gate_eval as GE
    pf, tf = S["pf"], S["tf"]
    fwd = (pf.split == "forward").to_numpy()
    mode = S.get("forward_mode", "upcoming_week")
    asof = _asof() or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    now_utc = now_utc or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    readiness = {f["family"]: f for f in (summary or {}).get("families", [])}
    fams_out = {}
    for fam, fz in frozen.items():
        r = readiness.get(fam, {})
        fams_out[fam] = {"readiness": r.get("readiness", "SHADOW VALIDATION"), "model": fz["model"],
                         "reason": r.get("readiness_reason", "")}
    pf_h = G.add_histories(pf, GE.HIST_COLS).merge(G.opp_season_games(tf), on=["game_id", "team"], how="left")
    inj = D.injuries()
    blk = int(pf.loc[fwd, "block"].min()) if fwd.any() else None
    des = pf.loc[fwd, ["season", "week", "player_id"]].merge(
        inj.rename(columns={"gsis_id": "player_id"})[["season", "week", "player_id", "report_status"]],
        on=["season", "week", "player_id"], how="left").report_status.fillna("None").to_numpy()
    status_map = {"None": "ACTIVE", "Questionable": "QUESTIONABLE", "Doubtful": "DOUBTFUL", "Out": "OUT", "Note": "ACTIVE"}
    vac = None
    try:
        from nfl import diagnostics as DG
        vac = DG._vacated(S)["vac"]
    except Exception:
        pass
    # ---- games / team families
    games = []
    tfw = tf[(tf.split == "forward")]
    for gid, gg in tfw.groupby("game_id"):
        g0 = gg.iloc[0]
        teams = []
        for _, t in gg.iterrows():
            for fam in P.TEAM_FAMILIES:
                fz = frozen[fam]
                mu = GE.model_mean(S, corr, fam, fz["model"], "forward")[t.name]
                d = EV.make(fz["dist_params"], np.array([mu]))
                teams.append({"team": t.team, "family": fam, "mean": round(float(mu), 2),
                              "p10": int(d.quantile(0.1)[0]), "p90": int(d.quantile(0.9)[0])})
        home = gg[gg.home == 1].team.iloc[0] if (gg.home == 1).any() else None
        away = gg[gg.home == 0].team.iloc[0] if (gg.home == 0).any() else None
        games.append({"game_id": gid, "start_utc": pd.Timestamp(g0.kickoff_utc).isoformat(), "home": home, "away": away,
                      "closing_spread_home": float(-gg[gg.home == 1].spread_team.iloc[0]) if home else None,
                      "total_line": float(g0.total_line) if pd.notna(g0.total_line) else None, "teams": teams})
    # ---- players
    players = []
    idx_fwd = np.where(fwd)[0]
    pos_in_fwd = {i: k for k, i in enumerate(idx_fwd)}
    for fam, s in P.PLAYER_FAMILIES.items():
        fz = frozen[fam]
        m = fwd & S["pops"][s["pop"]]
        mu_all = GE.model_mean(S, corr, fam, fz["model"], "forward")
        m &= np.isfinite(mu_all)
        idx = np.where(m)[0]
        if not len(idx):
            continue
        mu = mu_all[idx]
        dist = EV.make(fz["dist_params"], mu)
        oppfam = {"receptions": "targets", "receiving_yards": "targets", "rushing_yards": "carries", "completions": "passing_attempts",
                  "passing_yards": "passing_attempts", "passing_tds": "passing_attempts"}.get(fam)
        if fam == "anytime_td":
            opp_mu = (GE.model_mean(S, corr, "targets", frozen["targets"]["model"], "forward") +
                      GE.model_mean(S, corr, "carries", frozen["carries"]["model"], "forward"))[idx]
            od = None
        else:
            of_ = oppfam or fam
            opp_mu = GE.model_mean(S, corr, of_, frozen[of_]["model"], "forward")[idx]
            od = EV.make(frozen[of_]["dist_params"], opp_mu) if oppfam else None
        of = GE.opp_factor(S, fam)
        injs = [status_map.get(des[pos_in_fwd[i]], "ACTIVE") for i in idx]
        res = G.run(fam, pf_h.iloc[idx], mu, dist, s["y"], opp_mean=opp_mu, opp_factor=(of[idx] if of is not None else None),
                    injury=injs, rungs=s["rungs"], now_utc=now_utc)
        rungs = sorted(set(s["rungs"] + ([1] if fam == "anytime_td" else [])))
        thr = {k: dist.prob_ge(k) for k in rungs}
        for j, i in enumerate(idx):
            r = pf.iloc[i]
            adj = []
            if fz["model"] in ("D", "F", "D_vac", "F_vac", "E"):
                adj.append(f"Team volume uses the closing line (spread {r.spread_team:+.1f}, total {r.total_line:.1f}) and the opponent's "
                           f"schedule-adjusted defensive rating.")
            if of is not None and abs(np.log(max(of[i], 1e-6))) > 0.02:
                adj.append(f"Opponent efficiency factor x{of[i]:.2f} (fitted elasticity on 2016-2021).")
            if vac is not None and fz["model"].endswith("_vac"):
                v = vac.iloc[i]
                if v.vac_tpa_inj > 0.02 or v.vac_cs_inj > 0.02:
                    adj.append(f"Teammates listed OUT/DOUBTFUL vacate {v.vac_tpa_inj:.0%} of team targets / {v.vac_cs_inj:.0%} of carries; "
                               f"shares renormalised.")
            if r.career_games < 3:
                adj.append("Fewer than 3 career games: projection leans on the positional prior.")
            gate_res = res[j]
            players.append({
                "player_id": r.player_id, "name": r.player_display_name, "team": r.team, "opponent": r.opp, "game_id": r.game_id,
                "position": r.position, "family": fam, "mean": round(float(mu[j]), 3), "median": int(dist.median[j]),
                "p10": int(dist.quantile(0.1)[j]), "p90": int(dist.quantile(0.9)[j]),
                "thresholds": {str(k): round(float(thr[k][j]), 4) for k in rungs},
                "opportunity": ({"family": oppfam, "mean": round(float(opp_mu[j]), 2), "p10": int(od.quantile(0.1)[j]),
                                 "p90": int(od.quantile(0.9)[j])} if od is not None else
                                {"family": "touches" if fam == "anytime_td" else fam, "mean": round(float(opp_mu[j]), 2)}),
                "opponent_adjustment": {"factor": round(float(of[i]), 3) if of is not None else 1.0,
                                        "sample_games": int(r.opp_games_season) if "opp_games_season" in r and pd.notna(r.opp_games_season) else None},
                "adjustments": adj, "injury_designation": des[pos_in_fwd[i]],
                "readiness": fams_out[fam]["readiness"],
                "gate": {"status": gate_res["status"], "findings": [
                    {k: f[k] for k in ("check", "severity", "what", "category", "action")} for f in gate_res["findings"]]},
                "data_asof_utc": asof})
    # team reconciliation for the forward slate
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
    out = {"schema": "sift.projections.v1", "sport": "NFL", "generated_utc": now_utc, "data_asof_utc": asof,
           "mode": mode, "season": int(blk // 100) if blk else None, "week": int(blk % 100) if blk else None,
           "model": {"id": "pf-nfl", "version": f"pf-{PF_VERSION}+{_sha()}", "authority": "research_only"},
           "conditioning": "Player projections are CONDITIONAL ON THE PLAYER PARTICIPATING (DNP = void), the prop-settlement convention. "
                           "OUT players are written with gate BLOCK; QUESTIONABLE/DOUBTFUL with REVIEW.",
           "families": fams_out, "games": games, "players": players, "team_reconciliation": recon,
           "gate_summary": gate.summarize([{"status": p["gate"]["status"], "findings": p["gate"]["findings"]} for p in players])}
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    json.dump(out, open(out_path, "w"), indent=1, default=str)
    return out


def main():
    from nfl import run_walkforward as R
    from nfl import diagnostics as DG
    S = R.stage1(False)
    frozen = json.load(open(R.FROZEN))["families"]
    summ_p = os.path.join(RESULTS, "summary.json")
    summary = json.load(open(summ_p)) if os.path.exists(summ_p) else None
    corr = DG.corrections(S)["preds"]
    o = build(S, frozen, summary, corr, os.path.join(RESULTS, "projections_latest.json"))
    print(f"wrote {len(o['players'])} player projections for {len(o['games'])} games ({o['mode']}); gate {o['gate_summary']['status_counts']}")


if __name__ == "__main__":
    main()
