"""Synthetic frames for the simulation-layer tests.  No data files: CI has none.  The frames carry every
column the fit functions read, generated from a seeded RNG with plausible NFL magnitudes, so the tests
exercise the real fit -> bundle -> simulate path and pin its invariants rather than its numbers."""
from __future__ import annotations

import numpy as np
import pandas as pd

from nfl_edge.sim import models as M
from nfl_edge.sim.simulate import GameInput, TeamInput

TEAMS = ["AAA", "BBB", "CCC", "DDD"]


def team_frame(rng, n_games=120, seasons=(2020, 2021, 2022)) -> pd.DataFrame:
    rows = []
    gid = 0
    for s in seasons:
        for w in range(1, n_games // len(seasons) // 2 + 1):
            for h, a in ((TEAMS[0], TEAMS[1]), (TEAMS[2], TEAMS[3])):
                gid += 1
                g = f"{s}_{w:02d}_{a}_{h}"
                margin = rng.normal(0, 13); total = rng.normal(45, 13)
                for team, opp, home, m in ((h, a, True, margin), (a, h, False, -margin)):
                    plays = int(np.clip(rng.normal(62 + 0.2 * m, 6), 40, 90))
                    pr = float(np.clip(0.6 - 0.004 * m + rng.normal(0, 0.07), 0.3, 0.85))
                    drop = int(plays * pr); sacks = rng.binomial(drop, 0.06); scr = rng.binomial(drop, 0.04)
                    pass_att = drop - sacks - scr; targets = rng.binomial(pass_att, 0.96)
                    kneels = rng.poisson(0.7); designed = max(plays - drop - kneels, 0); rush_att = designed + kneels + scr
                    pts = max(0, int(round((total + m) / 2))); td = min(int(pts // 7), 9); ptd = rng.binomial(td, 0.55)
                    rows.append(dict(game_id=g, team=team, opp=opp, home=home, season=s, week=w, season_type="REG", home_team=h, away_team=a,
                                     plays=plays, dropbacks=drop, pass_att=pass_att, sacks=sacks, scrambles=scr, rush_att=rush_att,
                                     designed_rush=designed, kneels=kneels, targets=targets, completions=int(targets * 0.65),
                                     pass_yards=float(pass_att * 7.2), rush_yards=float(rush_att * 4.3), pass_td=ptd, rush_td=td - ptd,
                                     ints=rng.binomial(pass_att, 0.025), rz_rush=rng.poisson(6), i5_rush=rng.poisson(2), rz_pass=rng.poisson(7),
                                     xpass_mean=0.6, proe=rng.normal(0, 0.05), frac_lead4=0.4, frac_trail4=0.4, frac_lead8=0.2, frac_trail8=0.2,
                                     mean_lead=m / 2, drives=11, epa_play=rng.normal(0, 0.1), success_rate=0.45, neutral_pass_rate=pr,
                                     neutral_plays=30, neutral_proe=0.0, sec_per_play=rng.normal(28, 2), rz_trips=3, fga=2, fgm=2,
                                     home_score=pts if home else max(0, int(round((total - margin) / 2))),
                                     away_score=max(0, int(round((total - margin) / 2))) if home else pts,
                                     points=pts, opp_points=max(0, int(round((total - m) / 2))), margin=m, total=total, pass_rate=pr,
                                     off_td=td))
    return pd.DataFrame(rows)


def player_frame(rng, tg: pd.DataFrame) -> pd.DataFrame:
    """Five skill players per team-game with counts that add up to the team's volume."""
    rows = []
    for r in tg.itertuples():
        roster = [("QB", f"{r.team}_QB", 1), ("RB", f"{r.team}_RB1", 1), ("RB", f"{r.team}_RB2", 2), ("WR", f"{r.team}_WR1", 1), ("TE", f"{r.team}_TE1", 1)]
        cshare = np.array([0.08, 0.6, 0.27, 0.05, 0.0]); tshare = np.array([0.0, 0.15, 0.08, 0.5, 0.27])
        c = rng.multinomial(int(r.designed_rush), cshare); t = rng.multinomial(int(r.targets), tshare)
        for (pos, pid, rank), ci, ti in zip(roster, c, t):
            rec = int(ti * 0.65); rows.append(dict(
                game_id=r.game_id, team=r.team, opp=r.opp, home=r.home, season=r.season, week=r.week, season_type="REG",
                player_id=pid, position=pos, carries=int(ci + (r.scrambles + r.kneels if pos == "QB" else 0)),
                designed_carries=int(ci), rush_yards=float(ci * 4.2 + rng.normal(0, 8)), rush_td=int(rng.binomial(1, 0.15) if ci > 5 else 0),
                scrambles=int(r.scrambles if pos == "QB" else 0), rz_carries=int(rng.binomial(ci, 0.2)), i5_carries=int(rng.binomial(ci, 0.05)),
                rush_10plus=int(rng.binomial(ci, 0.1)), targets=int(ti), receptions=rec, rec_yards=float(rec * 11 + rng.normal(0, 10)),
                rec_td=int(rng.binomial(1, 0.2) if ti > 4 else 0), air_yards=float(ti * 8), rz_targets=int(rng.binomial(ti, 0.2)),
                ez_targets=int(rng.binomial(ti, 0.05)), attempts=int(r.pass_att if pos == "QB" else 0),
                completions=int(r.completions if pos == "QB" else 0), pass_yards=float(r.pass_yards if pos == "QB" else 0),
                pass_td=int(r.pass_td if pos == "QB" else 0), ints=int(r.ints if pos == "QB" else 0), sacks_taken=int(r.sacks if pos == "QB" else 0),
                offense_snaps=float(60 * (1.0 if rank == 1 else 0.4)), offense_pct=(1.0 if rank == 1 else 0.4), player_name=pid,
                home_team=r.home_team, away_team=r.away_team, any_td=0, dc_rank=rank, avail_state="EXPECTED_ACTIVE", phantom=False))
    df = pd.DataFrame(rows)
    df["any_td"] = df["rush_td"] + df["rec_td"]
    return df


def eligible_frame(pf_feat: pd.DataFrame) -> pd.DataFrame:
    e = pf_feat.copy()
    e["y_share_carry"] = np.where(e["team_designed_rush"] > 0, e["designed_carries"] / e["team_designed_rush"].clip(lower=1), np.nan)
    e["y_share_target"] = np.where(e["team_targets"] > 0, e["targets"] / e["team_targets"].clip(lower=1), np.nan)
    return e


def synthetic_bundle(seed=0):
    from nfl_edge.sim import features as F
    rng = np.random.default_rng(seed)
    tg = team_frame(rng)
    pg = player_frame(rng, tg)
    tf = F.team_features(tg)
    pf = F.player_features(pg, tg)
    pf["dc_rank"] = pf["player_id"].str[-1].map({"B": 1, "1": 1, "2": 2}).fillna(1)
    pf["avail_state"] = "EXPECTED_ACTIVE"
    e = eligible_frame(pf)
    ge = M.fit_game_env(tf)
    cs = M.fit_share_model(e[e["y_share_carry"].notna()].rename(columns={"y_share_carry": "y_share"}), "carry")
    ts = M.fit_share_model(e[e["y_share_target"].notna()].rename(columns={"y_share_target": "y_share"}), "target")
    # per-touch rows
    tf_off = tf[["game_id", "team", "off_ypc", "off_ypa", "off_comp_rate", "margin", "home"]].rename(columns={"margin": "team_margin"})
    tf_def = tf[["game_id", "team", "def_ypc", "def_ypa", "def_comp_rate"]].rename(columns={"team": "opp"})
    feat = pf[["game_id", "player_id", "position", "rt_ypc", "prior_ypc", "rt_explosive_rate", "rt_ypc_n", "rt_ypt", "prior_ypt",
               "rt_catch_rate", "rt_adot", "rt_ypt_n", "team"]]
    opp_map = tf[["game_id", "team", "opp"]].drop_duplicates()
    def _touch_rows(kind):
        rows = []
        for r in feat.itertuples():
            for _ in range(3):
                if kind == "carry":
                    rows.append(dict(game_id=r.game_id, player_id=r.player_id, yards=float(rng.standard_t(3) * 4 + 4), qb_scramble=0, qb_kneel=0))
                else:
                    c = int(rng.random() < 0.65)
                    rows.append(dict(game_id=r.game_id, player_id=r.player_id, complete=c, yards=float(c * max(0, rng.normal(11, 8))), air_yards=8.0))
        d = pd.DataFrame(rows).merge(feat, on=["game_id", "player_id"]).merge(opp_map, on=["game_id", "team"])
        d = d.merge(tf_off, on=["game_id", "team"]).merge(tf_def, on=["game_id", "opp"])
        return d
    car = _touch_rows("carry"); car.loc[:5, "qb_scramble"] = 1
    tar = _touch_rows("target")
    carry = M.fit_carry_model(car); target = M.fit_target_model(tar)
    td = M.fit_td_weights(pf)
    b = M.bundle(ge, cs, ts, carry, target, td, train_seasons=[2020, 2021, 2022], feature_config={}, other_share={"carry": 0.01, "target": 0.01})
    return b, tf, pf


def game_input(tf: pd.DataFrame, pf: pd.DataFrame, game_id: str | None = None) -> GameInput:
    from nfl_edge.sim.inputs import PLAYER_COLS_NEEDED
    game_id = game_id or tf["game_id"].iloc[-1]
    rows = tf[tf["game_id"] == game_id]
    home = rows[rows["home"]].iloc[0]; away = rows[~rows["home"]].iloc[0]
    def ti(row, other, is_home):
        pl = pf[(pf["game_id"] == game_id) & (pf["team"] == row["team"])].copy()
        cols = [c for c in PLAYER_COLS_NEEDED if c in pl.columns]
        pl = pl[cols].reset_index(drop=True)
        qb = pl[pl["position"] == "QB"]["player_id"].iloc[0]
        return TeamInput(team=row["team"], home=is_home, features=row.to_dict(), opp_features=other.to_dict(), players=pl, qb1=qb)
    return GameInput(game_id=game_id, season=int(home["season"]), week=int(home["week"]), home=ti(home, away, True),
                     away=ti(away, home, False), spread_home=-2.5, total_line=44.5, center_source="test")
