"""Availability (participation) study: how much does conditioning on 'played' matter, and how well does pregame
information predict it?

Candidate set (pregame-definable): for every team-game, the RB/WR/TE who played in at least one of the team's previous
3 games with a role (>= 2 targets or >= 4 carries per game over their last 4 games played), and who are still on that
team (same team on their most recent game). Outcome: did the player record an offensive snap / stat line (POST-game).
Pregame predictor: final injury-report designation for that week (Out / Doubtful / Questionable / none), which is
near-pregame (published Friday; nflverse has no per-row timestamp, so we flag it rather than assert it).

Three quantities:
 1. P(play | designation) fitted on development, scored on validation (Brier).
 2. Conditional bias: do players who play through a 'Questionable' tag under-produce their projection?
 3. Cost of the conditional convention: CRPS of 'assume he plays' vs the participation hurdle on the full candidate
    population (DNP scored as 0) -- what a consumer would see if voids were not voids.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pf_core import dists, metrics

from . import ladder as L


def candidates(pf: pd.DataFrame, inj: pd.DataFrame) -> pd.DataFrame:
    p = pf[pf.position.isin(["RB", "WR", "TE"]) & pf.y_observed].copy()
    p = p.sort_values(["player_id", "kickoff_utc"])
    g = p.groupby("player_id", sort=False)
    # role entering the NEXT game = rolling mean INCLUDING this game (computed from rows up to and including it)
    p["post_tgt_r4"] = g["targets"].transform(lambda s: s.rolling(4, min_periods=1).mean())
    p["post_car_r4"] = g["carries"].transform(lambda s: s.rolling(4, min_periods=1).mean())
    p["post_tgt_ewm"] = g["targets"].transform(lambda s: s.ewm(halflife=4).mean())
    tgi = pf[pf.y_observed][["team", "block", "game_id"]].drop_duplicates(["team", "block"]).sort_values(["team", "block"])
    tgi["tidx"] = tgi.groupby("team").cumcount()
    p = p.merge(tgi[["team", "block", "tidx"]], on=["team", "block"], how="left")
    # latest appearance per player up to each team game: for lags 1..3 take the most recent
    rows = []
    for lag in (1, 2, 3):
        x = p[["player_id", "team", "tidx", "post_tgt_r4", "post_car_r4", "post_tgt_ewm", "position"]].copy()
        x["tidx"] = x.tidx + lag
        x["lag"] = lag
        rows.append(x)
    c = pd.concat(rows).sort_values("lag").drop_duplicates(["player_id", "team", "tidx"], keep="first")
    c = c.merge(tgi, on=["team", "tidx"], how="inner")
    c = c[(c.post_tgt_r4 >= 2) | (c.post_car_r4 >= 4)]
    # still on this team: his most recent appearance before this block was for this team
    last_team = p[["player_id", "block", "team"]].rename(columns={"team": "last_team", "block": "lb"}).sort_values("lb")
    c["block"] = c.block.astype(float)
    c = c.sort_values("block")
    c = pd.merge_asof(c, last_team.rename(columns={"lb": "block"}).assign(block=lambda d: d.block + 0.5).sort_values("block"),
                      on="block", by="player_id", direction="backward")
    c["block"] = c.block.astype(int)
    c = c[c.last_team == c.team]
    played = p.set_index(["player_id", "block"])[["targets"]]
    c = c.merge(p[["player_id", "block", "targets"]], on=["player_id", "block"], how="left")
    c["played"] = c.targets.notna()
    c["season"] = c.block // 100
    c["week"] = c.block % 100
    inj2 = inj.rename(columns={"gsis_id": "player_id"})[["season", "week", "player_id", "report_status"]]
    c = c.merge(inj2, on=["season", "week", "player_id"], how="left")
    c["designation"] = c.report_status.fillna("None").replace({"Note": "None"})
    c["split"] = L.split_of(c.season, c.week)
    return c


def study(pf: pd.DataFrame, inj: pd.DataFrame) -> dict:
    c = candidates(pf, inj)
    c = c[c.season >= 2016]
    dev = c[c.split == "development"]
    val = c[c.split == "validation"]
    rates = dev.groupby("designation").played.agg(["mean", "size"])
    p_play = rates["mean"].to_dict()
    out = {"candidate_definition": "RB/WR/TE with >=2 targets or >=4 carries per game over last 4 played, appeared in one of the team's last 3 games, same team",
           "dev_play_rate_by_designation": {k: {"p_play": float(v["mean"]), "n": int(v["size"])} for k, v in rates.iterrows()}}
    for name, d in (("validation", val), ("development", dev)):
        pr = d.designation.map(p_play).fillna(p_play.get("None", 0.95)).to_numpy()
        o = d.played.astype(float).to_numpy()
        base = np.full(len(d), dev.played.mean())
        out[f"{name}_participation"] = {
            "n": int(len(d)), "dnp_rate": float(1 - o.mean()),
            "brier_designation_model": float(np.mean((pr - o) ** 2)),
            "brier_constant": float(np.mean((base - o) ** 2)),
            "dnp_rate_by_designation": d.groupby("designation").played.apply(lambda s: float(1 - s.mean())).to_dict(),
            "share_of_dnp_with_no_designation": float(((d.designation == "None") & ~d.played).sum() / max(1, (~d.played).sum())),
        }
        # cost of the conditional convention on targets (DNP scored as 0)
        mu = d.post_tgt_ewm.to_numpy()
        y = d.targets.fillna(0).to_numpy()
        nb = dists.negbin(mu, 0.15, K=40)
        hur = dists.hurdle(1 - pr, dists.negbin(mu, 0.15, K=40))
        # projections a consumer would publish: only for players NOT listed Out
        m = (d.designation != "Out").to_numpy()
        out[f"{name}_targets_unconditional"] = {
            "n_published(not Out)": int(m.sum()), "dnp_among_published": float(1 - d.played.to_numpy()[m].mean()),
            "crps_assume_plays": float(nb.subset(m).crps(y[m]).mean()),
            "crps_participation_hurdle": float(hur.subset(m).crps(y[m]).mean()),
            "bias_assume_plays": float((mu[m] - y[m]).mean()),
            "bias_hurdle": float((hur.subset(m).mean - y[m]).mean()),
        }
    # conditional bias of players who play with a designation (dev + val, played only)
    pl = c[c.played & c.split.isin(["development", "validation"])]
    out["played_through_designation_bias"] = {
        k: {"n": int(len(g)), "mean_proj": float(g.post_tgt_ewm.mean()), "mean_actual": float(g.targets.mean()),
            "ratio_actual_to_proj": float(g.targets.mean() / g.post_tgt_ewm.mean())}
        for k, g in pl.groupby("designation")}
    return out
