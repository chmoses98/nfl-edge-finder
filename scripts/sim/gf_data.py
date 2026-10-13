"""Historical Game Flow Intelligence Championship (RESEARCH_ONLY): reconstruct game trajectories from play-by-play.

Exact outcome definitions (home perspective, regular-season games, regulation clock unless stated; margin = home - away):
  ht_m / ht_t   margin / total after the last first-half play.            q3_m: margin after the last third-quarter play.
  comp4q        |q3_m| <= 8 (within one score entering the fourth quarter).
  lead14        at ANY play, either team led by >= 14 (max over post-play margins, whole game incl. OT).
  comeback10    one team trailed by >= 10 at ANY play and WON the game (final score incl. OT).
  lc4           >= 1 lead change in the fourth quarter (strict sign change among non-zero margins, counting the last non-zero
                margin before the quarter).
  drought20     the longest regulation stretch without any points by either team is >= 1200 clock seconds.
  home_lead7_ht / away_lead7_ht   leads by >= 7 at halftime.
Scores are the nflverse `total_home_score / total_away_score` columns, which are POST-play (verified on 2019_01_GB_CHI: the
final row equals the final score and a touchdown row already carries the 6 points).  Every reconstructed game is checked:
final play score == official final score, quarter scores sum to the half/final.
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd
import polars as pl
from nfl_edge.sim import data as D

CACHE = os.path.join(D.ROOT, "data", "cache", "gf")
_SWAP: dict = {}
COLS = ["game_id", "play_id", "qtr", "game_half", "game_seconds_remaining", "posteam", "home_team", "away_team", "total_home_score", "total_away_score",
        "home_score", "away_score", "play_type", "pass_attempt", "qb_dropback", "rush_attempt", "qb_scramble", "qb_kneel", "qb_spike", "score_differential",
        "fixed_drive", "season_type", "yardline_100"]


def _one_game(g: pd.DataFrame) -> dict | None:
    g = g.sort_values("play_id"); g = g[g.total_home_score.notna() & g.total_away_score.notna() & g.qtr.notna()]
    if len(g) < 80:
        return None
    h, a = g.total_home_score.to_numpy(float), g.total_away_score.to_numpy(float); m = h - a; q = g.qtr.to_numpy(float)
    gsr = g.game_seconds_remaining.to_numpy(float); elapsed = np.where(q <= 4, 3600 - gsr, 3600 + (600 - g.game_seconds_remaining.clip(upper=600).to_numpy(float)))
    fin_h, fin_a = float(g.home_score.iloc[-1]), float(g.away_score.iloc[-1])
    swapped = (h[-1] == fin_a) and (a[-1] == fin_h) and (h[-1] != fin_h)
    if swapped:          # nflverse swaps total_home/away_score for some relocated-franchise code mismatches (JAC/JAX, OAK/LV): repair, flagged
        h, a = a, h
    m = h - a
    ok_final = (h[-1] == fin_h) and (a[-1] == fin_a)
    first = g.game_half.to_numpy() == "Half1"
    if not first.any() or not (q == 3).any():
        return None
    i_ht = np.where(first)[0][-1]; i_q3 = np.where(q == 3)[0][-1]; i_q1 = np.where(q == 1)[0][-1]; i_q2 = np.where(q == 2)[0][-1]
    reg = q <= 4; i_q4 = np.where(reg)[0][-1]
    mx_h, mx_a = float(np.max(np.r_[0, m])), float(np.max(np.r_[0, -m]))
    won = np.sign(fin_h - fin_a)
    trailed_h10, trailed_a10 = float(np.max(np.r_[0, -m])) >= 10, float(np.max(np.r_[0, m])) >= 10   # home trailed by 10 <=> m <= -10
    comeback = bool((trailed_h10 and won > 0) or (trailed_a10 and won < 0))
    # fourth-quarter lead changes
    lastnz = [x for x in m[:i_q3 + 1] if x != 0]; prev = np.sign(lastnz[-1]) if lastnz else 0; lc = 0
    for x in m[(q == 4)]:
        s = np.sign(x)
        if s != 0:
            if prev != 0 and s != prev:
                lc += 1
            prev = s
    # scoring times (regulation)
    pts = np.r_[0.0, np.abs(np.diff(h + a))]; tt = np.r_[0.0, elapsed[reg]][: 0]
    tot = h + a; chg = np.r_[False, np.diff(tot) > 0]; times = elapsed[chg & reg]
    pts_ts = np.r_[0.0, np.sort(times), 3600.0]; drought = float(np.max(np.diff(pts_ts)))
    qpts = lambda i0, i1: (h[i1] - (h[i0] if i0 is not None else 0.0), a[i1] - (a[i0] if i0 is not None else 0.0))
    q1h, q1a = h[i_q1], a[i_q1]; q2h, q2a = h[i_q2] - h[i_q1], a[i_q2] - a[i_q1]; q3h, q3a = h[i_q3] - h[i_q2], a[i_q3] - a[i_q2]; q4h, q4a = h[i_q4] - h[i_q3], a[i_q4] - a[i_q3]
    qt = np.array([q1h + q1a, q2h + q2a, q3h + q3a, q4h + q4a])
    _SWAP[g.game_id.iloc[0]] = bool(swapped)
    return {"game_id": g.game_id.iloc[0], "ht_m": m[i_ht], "ht_t": tot[i_ht], "q1_m": m[i_q1], "q3_m": m[i_q3], "reg_m": m[i_q4], "reg_t": tot[i_q4], "final_m": fin_h - fin_a,
            "final_t": fin_h + fin_a, "max_lead_home": mx_h, "max_lead_away": mx_a, "lead14": float(max(mx_h, mx_a) >= 14), "comeback10": float(comeback),
            "comp4q": float(abs(m[i_q3]) <= 8), "lc4_n": lc, "lc4": float(lc >= 1), "drought_max_s": drought, "drought20": float(drought >= 1200),
            "home_lead7_ht": float(m[i_ht] >= 7), "away_lead7_ht": float(m[i_ht] <= -7), "h1_home": h[i_ht], "h1_away": a[i_ht],
            "h2_home": h[i_q4] - h[i_ht], "h2_away": a[i_q4] - a[i_ht], 
            "ok_final": bool(ok_final), "repaired_swap": bool(swapped), "ok_sum": bool(abs((q1h + q2h + q3h + q4h) - h[i_q4]) < 1e-9 and abs(h[i_ht] - (q1h + q2h)) < 1e-9)}


def _drives(g: pd.DataFrame, swapped: bool) -> list[dict]:
    """Regulation drives with the net score change over each drive (home perspective) and the clock interval it occupies."""
    g = g.sort_values("play_id"); g = g[g.total_home_score.notna() & g.qtr.notna()].reset_index(drop=True)
    h, a = g.total_home_score.to_numpy(float), g.total_away_score.to_numpy(float)
    if swapped:
        h, a = a, h
    m, tot = h - a, h + a; q = g.qtr.to_numpy(float); el = 3600 - g.game_seconds_remaining.to_numpy(float)
    home = g.home_team.iloc[0]; out = []; prev_idx = -1
    ok = g.fixed_drive.notna() & g.posteam.notna() & (q <= 4)
    idxs = {}
    for i in np.where(ok.to_numpy())[0]:
        idxs.setdefault(g.fixed_drive.iat[i], []).append(i)
    ordered = sorted(idxs.values(), key=lambda v: v[0])
    for k, ix in enumerate(ordered):
        i0, i1 = ix[0], ix[-1]; start = float(el[i0]); half = 0 if start < 1800 else 1
        nxt = float(el[ordered[k + 1][0]]) if k + 1 < len(ordered) else (1800.0 if half == 0 else 3600.0)
        nxt_half = 0 if nxt < 1800 else 1
        end = min(nxt, 1800.0) if (half == 0 and (nxt_half == 1 or nxt > 1800)) else min(nxt, 3600.0)
        if end < start:
            end = start
        mb = float(m[i0 - 1]) if i0 > 0 else 0.0; tb = float(tot[i0 - 1]) if i0 > 0 else 0.0
        out.append({"game_id": g.game_id.iloc[0], "k": k, "side": 0 if g.posteam.iat[i0] == home else 1, "start": start, "dur": end - start,
                    "m_before": mb, "dm": float(m[i1] - mb), "dtot": float(tot[i1] - tb), "half": half})
    return out


def _team_flow(g: pd.DataFrame) -> list[dict]:
    g = g[g.posteam.notna() & g.play_type.isin(["run", "pass", "qb_kneel", "qb_spike"]) & (g.qtr <= 4)].copy()
    g["pass_play"] = ((g.pass_attempt == 1) | (g.sack == 1 if "sack" in g else False) | (g.qb_scramble == 1)).astype(int)
    g["db"] = (g.qb_dropback == 1).astype(int); g["rush"] = (g.rush_attempt == 1).astype(int)
    g["designed_rush"] = ((g.rush_attempt == 1) & (g.qb_scramble == 0) & (g.qb_kneel == 0)).astype(int)
    out = []
    for team, x in g.groupby("posteam"):
        half1 = x.qtr <= 2; lead7 = x.score_differential >= 7; trail7 = x.score_differential <= -7
        row = {"game_id": x.game_id.iloc[0], "team": team, "plays": len(x), "dropbacks": int(x.db.sum()), "rushes": int(x.rush.sum()), "drives": int(x.fixed_drive.nunique())}
        for nm, msk in (("h1", half1), ("h2", ~half1), ("trail7", trail7), ("lead7", lead7)):
            s = x[msk]; row[f"db_{nm}"] = int(s.db.sum()); row[f"dr_{nm}"] = int(s.designed_rush.sum()); row[f"n_{nm}"] = len(s)
        out.append(row)
    return out


def recon_ok(G: pd.DataFrame) -> pd.Series:
    """Reliable reconstruction: final play score equals the official final, OR an overtime game whose last play row lacks the
    OT score (regulation tied, official result decided by <= 8 in OT).  Season >= 2003 only (2001-2002 pbp has garbled games)."""
    ot_missing = (G.reg_m == 0) & (G.final_m != 0) & (G.final_m.abs() <= 8) & (G.reg_t <= G.final_t)
    return (G.ok_final | ot_missing) & G.ok_sum & (G.season >= 2003)


def build(seasons=range(2001, 2026)) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    os.makedirs(CACHE, exist_ok=True); gp, tp = os.path.join(CACHE, "games_flow.parquet"), os.path.join(CACHE, "team_flow.parquet")
    if os.path.exists(gp) and os.path.exists(tp):
        import json
        return pd.read_parquet(gp), pd.read_parquet(tp), json.load(open(os.path.join(CACHE, "coverage.json")))
    games, teams, drives, bad = [], [], [], {"no_reconstruction": 0, "final_mismatch": 0, "sum_mismatch": 0, "games": 0}
    for s in seasons:
        d = pl.read_parquet(os.path.join(D.RAW, "pbp", f"play_by_play_{s}.parquet"), columns=COLS + ["sack"]).filter(pl.col("season_type") == "REG").to_pandas()
        d["posteam"] = d.posteam.replace(D.TEAM_FIX)
        for gid, g in d.groupby("game_id"):
            bad["games"] += 1; r = _one_game(g)
            if r is None:
                bad["no_reconstruction"] += 1; continue
            bad["final_mismatch"] += int(not r["ok_final"]); bad["sum_mismatch"] += int(not r["ok_sum"])
            r["season"] = s; games.append(r)
            for t in _team_flow(g):
                t["season"] = s; teams.append(t)
            for dr in _drives(g, _SWAP.get(gid, False)):
                dr["season"] = s; drives.append(dr)
    G, T = pd.DataFrame(games), pd.DataFrame(teams); G.to_parquet(gp); T.to_parquet(tp); pd.DataFrame(drives).to_parquet(os.path.join(CACHE, "drives.parquet"))
    import json; json.dump(bad, open(os.path.join(CACHE, "coverage.json"), "w")); return G, T, bad
