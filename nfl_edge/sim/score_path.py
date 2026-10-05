"""SCORE-PATH research arm P1 (preregistered: research/game_script_v2/PREREGISTRATION.md, section 7). RESEARCH_ONLY.

The simulator draws a FINAL margin and total, never a scoring sequence. This arm asks whether the simulated final
state carries usable information about the PATH -- half-time and Q3 margins, who leads at the half / entering Q4,
early blowouts, late comebacks, lead changes -- beyond a plain historical baseline. It is not part of GAME SCRIPT
V2 and V2 does not depend on it.

P1 (conditional path bank, no random draw): for a simulated row with final home margin m and scoring cell s
(section 2 of the preregistration), P(path event | m, s) is a Gaussian-kernel (bandwidth 3 points) average over
TRAINING games in the same scoring cell; the game's probability is the mean over its rows. The predictive
distribution of a quarter-end margin is the same kernel mixture over training games' realised margins.

Baseline: the event frequency / margin distribution among TRAINING games in the same signed closing-spread bucket.

Path definitions are exactly ``research.script_autopsy.game_flow`` / ``realized_labels`` (shared thresholds).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import polars as pl

from . import data as D
from . import script_v2 as V
from nfl_edge.research import script_autopsy as SA

BANDWIDTH = 3.0
SIGNED_BUCKETS = (-np.inf, -7.0, -3.0, 0.0, 0.0, 3.0, 7.0, np.inf)   # <=-7, (-7,-3], (-3,0), 0, (0,3), [3,7), >=7
EVENTS = ("home_leads_half", "home_leads_q3", "early_blowout", "late_comeback", "lead_changes_2plus")
MARGINS = ("margin_half", "margin_q3")


def signed_bucket(spread: float) -> int:
    s = float(spread)
    if s <= -7: return 0
    if s <= -3: return 1
    if s < 0: return 2
    if s == 0: return 3
    if s < 3: return 4
    if s < 7: return 5
    return 6


def path_table(seasons) -> pd.DataFrame:
    """One row per game: quarter-end margins and path events from play-by-play via script_autopsy.game_flow."""
    sched = D.schedule().to_pandas()
    sched = sched[sched["season"].isin(list(seasons)) & sched["result"].notna() & sched["spread_line"].notna() & sched["total_line"].notna()]
    rows = []
    for s in sorted(set(sched["season"])):
        p = pl.read_parquet(f"{D.RAW}/pbp/play_by_play_{s}.parquet", columns=["game_id", "play_id", "qtr", "total_home_score", "total_away_score"])
        p = p.sort(["game_id", "play_id"])
        for gid, grp in p.group_by("game_id", maintain_order=True):
            gid = gid[0] if isinstance(gid, tuple) else gid
            flow = SA.game_flow(grp.to_dicts(), "H", "A")
            if not flow or flow.get("margin_half") is None or flow.get("margin_q3") is None:
                continue
            rows.append({"game_id": gid, **{k: flow.get(k) for k in ("margin_q1", "margin_half", "margin_q3", "final_margin", "final_total", "lead_changes")}})
    f = pd.DataFrame(rows).merge(sched[["game_id", "season", "week", "spread_line", "total_line", "result", "total"]], on="game_id")
    f["home_leads_half"] = f["margin_half"] > 0
    f["home_leads_q3"] = f["margin_q3"] > 0
    big = (f["margin_q3"].abs() >= SA.BLOWOUT_MARGIN) | (f["result"].abs() >= SA.BLOWOUT_MARGIN)
    f["early_blowout"] = big & (f["margin_half"].abs() >= SA.EARLY_BLOWOUT_HALF)
    q3 = f["margin_q3"]; fm = f["result"]
    f["late_comeback"] = (q3 != 0) & (q3.abs() >= 7) & ((fm == 0) | ((fm > 0) != (q3 > 0)))
    f["lead_changes_2plus"] = f["lead_changes"] >= 2
    f["scoring"] = [int(V.scoring_index(np.array([t]), tl)[0]) for t, tl in zip(f["total"], f["total_line"])]
    f["bucket"] = [signed_bucket(s) for s in f["spread_line"]]
    # the play-by-play final must be the schedule's final (overtime included); a mismatch is reported, not hidden
    f["pbp_final_matches"] = (f["final_margin"] == f["result"]) & (f["final_total"] == f["total"])
    return f


def _crps_weighted(x: np.ndarray, w: np.ndarray, y: float) -> float:
    """CRPS of a weighted empirical distribution: E|X - y| - 0.5 E|X - X'|."""
    w = w / w.sum()
    order = np.argsort(x); x = x[order]; w = w[order]
    a = float(np.sum(w * np.abs(x - y)))
    cw = np.cumsum(w); cxw = np.cumsum(w * x)
    # E|X-X'| = 2 * sum_i w_i (x_i F(x_i-) - sum_{j<i} w_j x_j)
    b = 2.0 * float(np.sum(w * (x * (cw - w) - (cxw - w * x))))
    return a - 0.5 * b


def arm_forecast(margins: np.ndarray, totals: np.ndarray, spread: float, total_line: float, train: pd.DataFrame) -> dict:
    """P1: the kernel conditional averaged over the simulated rows of one game. Deterministic."""
    s_idx = V.scoring_index(totals, total_line)
    combos, counts = np.unique(np.stack([margins, s_idx]), axis=1, return_counts=True)
    tw = np.zeros(len(train))
    tm = train["result"].to_numpy(float); ts = train["scoring"].to_numpy(int)
    for (m, s), c in zip(combos.T, counts):
        same = ts == s
        k = np.where(same, np.exp(-0.5 * ((tm - m) / BANDWIDTH) ** 2), 0.0)
        if k.sum() <= 0:
            k = np.exp(-0.5 * ((tm - m) / BANDWIDTH) ** 2)
        tw += c * k / k.sum()
    tw /= tw.sum()
    return {"weights": tw, **{e: float(np.sum(tw * train[e].to_numpy(float))) for e in EVENTS}}


def baseline_forecast(spread: float, train: pd.DataFrame) -> dict:
    b = signed_bucket(spread)
    sub = train[train["bucket"] == b]
    if len(sub) < 20:
        sub = train
    w = np.zeros(len(train)); w[train.index.get_indexer(sub.index)] = 1.0 / len(sub)
    return {"weights": w, **{e: float(sub[e].mean()) for e in EVENTS}}


def evaluate(rows_by_season: dict, path: pd.DataFrame, seasons) -> pd.DataFrame:
    """Per held-out game: arm and baseline Brier per event and CRPS per margin, training on seasons < Y."""
    out = []
    for y in seasons:
        train = path[(path["season"] < y)].reset_index(drop=True)
        test = path[path["season"] == y].set_index("game_id")
        rows = rows_by_season[y]
        for gid in rows.files:
            if gid not in test.index:
                out.append({"game_id": gid, "season": y, "missing_path": True})
                continue
            r = test.loc[gid]; R = rows[gid]
            a = arm_forecast(R[0].astype(float), R[1].astype(float), r["spread_line"], r["total_line"], train)
            b = baseline_forecast(r["spread_line"], train)
            rec = {"game_id": gid, "season": y, "missing_path": False}
            for e in EVENTS:
                yv = float(r[e])
                rec[f"arm_{e}"] = (a[e] - yv) ** 2; rec[f"base_{e}"] = (b[e] - yv) ** 2
                rec[f"p_arm_{e}"] = a[e]; rec[f"p_base_{e}"] = b[e]; rec[f"y_{e}"] = yv
            for mcol in MARGINS:
                x = train[mcol].to_numpy(float)
                rec[f"arm_{mcol}"] = _crps_weighted(x, a["weights"].copy(), float(r[mcol]))
                nz = b["weights"] > 0
                rec[f"base_{mcol}"] = _crps_weighted(x[nz], b["weights"][nz].copy(), float(r[mcol]))
            out.append(rec)
    return pd.DataFrame(out)


def summarize(ev: pd.DataFrame, seasons) -> dict:
    from .script_backtest import boot_diff
    ok = ev[~ev["missing_path"]]
    res = {"by_season": {}, "pooled": {}, "missing_path_games": ev.loc[ev["missing_path"], "game_id"].tolist()}
    def block(t):
        b = {}
        for e in EVENTS + MARGINS:
            b[e] = {"n": int(len(t)), "arm": float(t[f"arm_{e}"].mean()), "baseline": float(t[f"base_{e}"].mean()),
                    "arm_minus_baseline": boot_diff(t[f"arm_{e}"].to_numpy(), t[f"base_{e}"].to_numpy()),
                    "metric": "CRPS" if e in MARGINS else "Brier"}
            if e in EVENTS:
                b[e]["rate"] = float(t[f"y_{e}"].mean()); b[e]["mean_p_arm"] = float(t[f"p_arm_{e}"].mean())
                b[e]["mean_p_base"] = float(t[f"p_base_{e}"].mean())
        return b
    for y in seasons:
        res["by_season"][str(y)] = block(ok[ok["season"] == y])
    res["pooled"] = block(ok)
    wins = {e: res["pooled"][e]["arm_minus_baseline"]["hi"] < 0 for e in EVENTS + MARGINS}
    res["verdict"] = {"beats_baseline_by_target": wins,
                      "verdict": "ACCEPTED_FOR_FURTHER_RESEARCH" if all(wins.values()) else "REJECTED"}
    return res
