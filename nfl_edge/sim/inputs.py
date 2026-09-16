"""Build ``GameInput`` objects from the assembled frames (historical backtests) or from point-in-time
sources at a cutoff (prospective projection).

The centre (expected home margin and total) is an INPUT here, never derived: the backtest passes the
consensus closing line as a stand-in for the market, the prospective path passes the Kalshi-implied lines
or the consensus line, and the market-free arm passes the DATA_ONLY centre.  Which one was used is
recorded on the result.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import data as D
from . import features as F
from .simulate import GameInput, TeamInput

PLAYER_COLS_NEEDED = ["player_id", "position", "dc_rank", "avail_state", "n_prior", "gap_weeks",
                      "sh_carry_s", "sh_carry_l", "last_sh_carry", "sh_carry_s_w", "sh_rz_carry_l",
                      "sh_target_s", "sh_target_l", "last_sh_target", "sh_target_s_w", "sh_rz_target_l",
                      "snap_share_s", "snap_share_l", "sh_attempt_l",
                      "rt_ypc", "prior_ypc", "rt_explosive_rate", "rt_ypc_n", "rt_ypt", "prior_ypt", "rt_catch_rate",
                      "rt_adot", "rt_ypt_n", "rt_scramble_rate", "rt_rz_carry_rate", "rt_ez_target_rate",
                      "rt_rush_td_rate", "rt_rec_td_rate"]


def _team_row(tf: pd.DataFrame, game_id: str, team: str) -> dict:
    r = tf[(tf["game_id"] == game_id) & (tf["team"] == team)]
    if r.empty:
        raise KeyError(f"no team feature row for {team} in {game_id}")
    return r.iloc[0].to_dict()


def _qb1(players: pd.DataFrame) -> str | None:
    q = players[players["position"] == "QB"]
    if q.empty:
        return None
    q = q.sort_values(["dc_rank", "sh_attempt_l"], ascending=[True, False], na_position="last")
    return str(q.iloc[0]["player_id"])


def historical_game_input(frames: dict, game_id: str, *, spread_home: float, total_line: float,
                          center_source: str = "consensus_close") -> GameInput:
    tf = frames["team"]; e = frames["eligible"]
    g = D.schedule().to_pandas(); row = g[g["game_id"] == game_id].iloc[0]
    home, away = row["home_team"], row["away_team"]
    teams = {}
    for team, is_home in ((home, True), (away, False)):
        other = away if is_home else home
        pl = e[(e["game_id"] == game_id) & (e["team"] == team)].copy()
        cols = [c for c in PLAYER_COLS_NEEDED if c in pl.columns]
        pl = pl[cols].reset_index(drop=True)
        teams[team] = TeamInput(team=team, home=is_home, features=_team_row(tf, game_id, team),
                                opp_features=_team_row(tf, game_id, other), players=pl, qb1=_qb1(pl))
    return GameInput(game_id=game_id, season=int(row["season"]), week=int(row["week"]), home=teams[home], away=teams[away],
                     spread_home=float(spread_home), total_line=float(total_line), center_source=center_source)


def historical_bank(target_season: int, seed: int = 11):
    """The incumbent's residual bank built from seasons strictly before ``target_season`` (the closing
    consensus line is the anchor; those games are settled, so nothing is hindsight for a later season)."""
    from nfl_edge.pricing.game_env import ResidualBank
    g = D.schedule().to_pandas()
    h = g[(g["season"] < target_season) & (g["season"] >= 2016) & g["result"].notna() & g["spread_line"].notna()
          & g["total_line"].notna() & (g["game_type"] == "REG")].copy()
    h["mres"] = h["result"] - h["spread_line"]; h["tres"] = h["total"] - h["total_line"]
    return ResidualBank(h["mres"], h["tres"], h["season"], ref_season=target_season, spread_lines=h["spread_line"],
                        total_lines=h["total_line"], overtime=h["overtime"].fillna(0).astype(int), results=h["result"],
                        halflife=3.0, rng=np.random.default_rng(seed))
