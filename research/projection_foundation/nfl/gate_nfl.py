"""NFL wiring of the Projection Quality Gate (pf_core.gate) + team reconciliation.

Role-aware inputs: opportunity_history = the player's own previous 8 games of the opportunity stat (targets for
receiving families, carries for rushing, pass attempts for QB families, touches for anytime TD); stat_history = his
previous 8 games of the projected stat; opponent sample = the opponent's games already played this season.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pf_core import gate

OPP_STAT = {"targets": "targets", "receptions": "targets", "receiving_yards": "targets", "carries": "carries",
            "rushing_yards": "carries", "passing_attempts": "attempts", "completions": "attempts", "passing_yards": "attempts",
            "passing_tds": "attempts", "anytime_td": "touches"}
OPP_PRED = {"targets": "targets", "receptions": "targets", "receiving_yards": "targets", "carries": "carries",
            "rushing_yards": "carries", "passing_attempts": "passing_attempts", "completions": "passing_attempts",
            "passing_yards": "passing_attempts", "passing_tds": "passing_attempts", "anytime_td": None}
GATE_FAMILY = {"passing_attempts": "passing_attempts", "anytime_td": "anytime_td"}


def add_histories(pf: pd.DataFrame, cols, n=8) -> pd.DataFrame:
    pf = pf.sort_values(["player_id", "kickoff_utc"]).copy()
    g = pf.groupby("player_id", sort=False)
    for c in cols:
        lags = np.column_stack([g[c].shift(i).to_numpy(float) for i in range(1, n + 1)])
        pf[f"_hist_{c}"] = list(lags[:, ::-1])          # oldest .. most recent
    return pf.sort_index()


def opp_season_games(tf: pd.DataFrame) -> pd.DataFrame:
    """For every (game, team): how many games the OPPONENT had already played this season."""
    t = tf[["game_id", "team", "opp", "season", "kickoff_utc"]].sort_values("kickoff_utc").copy()
    t["n_season"] = t.groupby(["team", "season"]).cumcount()
    o = t[["game_id", "team", "n_season"]].rename(columns={"team": "opp", "n_season": "opp_games_season"})
    return t[["game_id", "team", "opp"]].merge(o, on=["game_id", "opp"], how="left")[["game_id", "team", "opp_games_season"]]


def run(fam: str, rows: pd.DataFrame, mean, dist, ycol: str, opp_mean=None, opp_factor=None, injury=None, now_utc=None,
        rungs=None, team_verified=True, participation=None, participation_reasons=None, data_asof_utc=None) -> list[dict]:
    """rows: player frame rows (with _hist_ columns, kickoff_utc, career_games, opp_games_season).
    participation / participation_reasons (live operation): per-row pf_core participation class and reasons (None = the
    study's behaviour: no point-in-time availability feed)."""
    res = []
    P = dist.P
    lo = dist.lo
    sd = np.sqrt(np.maximum(dist.var, 0))
    oc = OPP_STAT[fam]
    sc = ycol
    thr = {k: dist.prob_ge(k) for k in (rungs or [])}
    for i, (_, r) in enumerate(rows.iterrows()):
        th = {str(k): float(thr[k][i]) for k in rungs} if rungs else None
        ko = r.kickoff_utc
        gi = gate.GateInput(
            sport="NFL", family=GATE_FAMILY.get(fam, fam), entity_id=r.player_id, entity_name=r.get("player_display_name"),
            team=r.team, game_id=r.game_id, game_start_utc=ko.isoformat() if pd.notna(ko) else None,
            mean=float(mean[i]), team_verified=team_verified, data_asof_utc=(data_asof_utc or ((ko - pd.Timedelta(hours=20)).isoformat() if pd.notna(ko) else None)),
            injury_status=(injury[i] if injury is not None else None),
            expected_opportunity=(float(opp_mean[i]) if opp_mean is not None else None),
            opportunity_history=list(r[f"_hist_{oc}"]) if f"_hist_{oc}" in rows.columns else None,
            stat_history=list(r[f"_hist_{sc}"]) if sc and f"_hist_{sc}" in rows.columns else None,
            opponent_sample_games=int(r.opp_games_season) if pd.notna(r.get("opp_games_season")) else None,
            opponent_factor=(float(opp_factor[i]) if opp_factor is not None else None),
            support_lo=lo, probs=P[i], thresholds=th, sd=float(sd[i]), model_n_obs=int(r.career_games),
            participation=(participation[i] if participation is not None else None),
            participation_reasons=(participation_reasons[i] if participation_reasons is not None else None))
        res.append(gate.evaluate(gi, now_utc=now_utc or (ko - pd.Timedelta(hours=19)).isoformat()))
    return res


def team_recon(player_sum: pd.Series, team_mean: pd.Series, label: str) -> list[dict]:
    return [gate.team_reconciliation(float(a), float(b), label) for a, b in zip(player_sum, team_mean)]
