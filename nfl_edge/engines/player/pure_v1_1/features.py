"""PIT availability features for PURE_PLAYER_V1_1 (definitions fixed by the preregistration)."""
from __future__ import annotations

import numpy as np
import pandas as pd

OWN = ["own_q", "own_d", "own_lim", "own_dnp"]
OUT_LIKE = ("Out", "Doubtful")
TARGET_POS = ("RB", "WR", "TE", "FB", "HB")
CARRY_POS = ("RB", "FB", "HB")


def _recent_shares(rows: pd.DataFrame) -> pd.DataFrame:
    """Per played player-game: mean target / carry share over that game and his previous <= 2 played games."""
    p = rows[rows["played"] & rows["target_share"].notna()].sort_values(["player_id", "kickoff", "game_id"], kind="mergesort")
    g = p.groupby("player_id", sort=False)
    out = p[["player_id", "kickoff"]].copy()
    out["r3_t"] = g["target_share"].transform(lambda x: x.rolling(3, min_periods=1).mean())
    out["r3_c"] = g["carry_share"].transform(lambda x: x.rolling(3, min_periods=1).mean())
    return out


def add(rows: pd.DataFrame, t: pd.DataFrame, inj: pd.DataFrame) -> pd.DataFrame:
    """rows: V1 feature rows (features.add_player_features output); t: V1 team table; inj: certified injury rows
    (season, week, team, gsis_id, report_status, practice_status, position, kickoff). Returns rows + feature columns."""
    d = rows.copy()
    inj = inj.copy()
    inj["report_status"] = inj["report_status"].fillna("").astype(str)
    inj["practice_status"] = inj["practice_status"].fillna("").astype(str)
    own = inj.rename(columns={"gsis_id": "player_id"})[["season", "week", "team", "player_id", "report_status", "practice_status"]]
    own = own.drop_duplicates(["season", "week", "team", "player_id"])
    d = d.merge(own, on=["season", "week", "team", "player_id"], how="left")
    rs, ps = d["report_status"].fillna(""), d["practice_status"].fillna("")
    d["own_q"] = (rs == "Questionable").astype(float)
    d["own_d"] = (rs == "Doubtful").astype(float)
    d["own_lim"] = ps.str.contains("Limited", regex=False).astype(float)
    d["own_dnp"] = ps.str.contains("Did Not Participate", regex=False).astype(float)
    d = d.drop(columns=["report_status", "practice_status"])

    # teammates listed Out / Doubtful: their recent shares as of before the target game
    out = inj[inj["report_status"].isin(OUT_LIKE)][["season", "week", "team", "gsis_id", "position", "kickoff"]].dropna(subset=["gsis_id"])
    rec = _recent_shares(rows).rename(columns={"player_id": "gsis_id", "kickoff": "hist_kickoff"})
    d["vac_t"] = 0.0
    d["vac_c"] = 0.0
    if len(out):
        o = out.copy()
        o["kickoff"] = pd.to_datetime(o["kickoff"], utc=True)
        rec["hist_kickoff"] = pd.to_datetime(rec["hist_kickoff"], utc=True)
        o = o.sort_values("kickoff"); rec = rec.sort_values("hist_kickoff")
        m = pd.merge_asof(o, rec, left_on="kickoff", right_on="hist_kickoff", by="gsis_id", allow_exact_matches=False, direction="backward")
        m["vt"] = np.where(m["position"].isin(TARGET_POS), m["r3_t"].fillna(0.0), 0.0)
        m["vc"] = np.where(m["position"].isin(CARRY_POS), m["r3_c"].fillna(0.0), 0.0)
        team_sum = m.groupby(["season", "week", "team"], as_index=False).agg(_st=("vt", "sum"), _sc=("vc", "sum"))
        self_c = m.rename(columns={"gsis_id": "player_id"})[["season", "week", "team", "player_id", "vt", "vc"]]
        self_c = self_c.groupby(["season", "week", "team", "player_id"], as_index=False)[["vt", "vc"]].sum()
        d = d.drop(columns=["vac_t", "vac_c"]).merge(team_sum, on=["season", "week", "team"], how="left")
        d = d.merge(self_c, on=["season", "week", "team", "player_id"], how="left")
        # teammates only: a listed player never vacates his own share
        d["vac_t"] = (d["_st"].fillna(0.0) - d["vt"].fillna(0.0)).clip(lower=0.0)
        d["vac_c"] = (d["_sc"].fillna(0.0) - d["vc"].fillna(0.0)).clip(lower=0.0)
        d = d.drop(columns=["_st", "_sc", "vt", "vc"])
    # previous-game starter listed Out / Doubtful
    s = t.sort_values(["team", "kickoff", "game_id"], kind="mergesort")
    prev = s.assign(prev_starter=s.groupby("team")["starter"].shift(1))[["team", "game_id", "prev_starter", "season", "week"]]
    od = set(zip(out["season"], out["week"], out["team"], out["gsis_id"])) if len(out) else set()
    prev["qb1_out"] = [float((se, wk, tm, ps_) in od) for se, wk, tm, ps_ in zip(prev["season"], prev["week"], prev["team"], prev["prev_starter"])]
    d = d.merge(prev[["team", "game_id", "qb1_out"]], on=["team", "game_id"], how="left")
    d["qb1_out"] = d["qb1_out"].fillna(0.0)
    return d.set_index(rows.index)
