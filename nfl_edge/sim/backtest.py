"""Walk-forward evaluation of the simulation layer.

For each evaluation season Y the bundle is fitted on seasons < Y (``training.fit_bundle``), every game of
Y is simulated with the consensus closing line as the centre (the market stand-in the historical record
supports), and one row per (game, player, statistic) is written with the predictive mean, standard
deviation, 50 quantiles and the integer pmf, together with the realised value.  ``evaluate`` then scores:

  * point accuracy: MAE, RMSE, signed bias, against a naive prior-only baseline (EWMA share x EWMA team
    volume, EWMA rate x count) -- the primitives the user asked to see separately;
  * distribution quality: CRPS from the quantiles, central 50% / 90% interval coverage, PIT histogram;
  * ladder Brier at a fixed threshold grid per statistic.

Nothing about Y enters the bundle, the features, or the eligible sets except what was known before each
game (features are strictly prior, eligibility uses that week's roster/depth chart/report).
"""
from __future__ import annotations

import json
import os
import time

import numpy as np
import pandas as pd

from . import data as D
from . import inputs as I
from . import simulate as S
from . import training as T

QLEVELS = np.round(np.arange(0.01, 1.0, 0.02), 4)          # 50 quantile levels
STAT_GRID = {"rush_yards": 300, "rec_yards": 300, "pass_yards": 600, "carries": 50, "targets": 30, "receptions": 25,
             "attempts": 75, "completions": 55, "pass_td": 8, "any_td": 6, "rush_td": 5, "rec_td": 5}
LADDERS = {"rush_yards": list(range(10, 160, 10)), "rec_yards": list(range(10, 160, 10)), "pass_yards": list(range(150, 426, 25)),
           "carries": list(range(4, 31, 2)), "targets": list(range(2, 15)), "receptions": list(range(1, 12)),
           "attempts": list(range(15, 56, 5)), "completions": list(range(10, 41, 5)), "pass_td": [1, 2, 3, 4], "any_td": [1, 2]}
TEAM_STATS = ["points", "plays", "pass_att", "rush_att", "targets", "pass_yards", "rush_yards", "off_td", "pass_td", "rush_td", "dropbacks"]
PLAYER_STATS = ["carries", "rush_yards", "targets", "receptions", "rec_yards", "attempts", "completions", "pass_yards", "pass_td",
                "rush_td", "rec_td", "any_td"]
OUT = os.path.join(D.ROOT, "research", "simulation_engine")


def _pmf(x: np.ndarray, n_max: int) -> np.ndarray:
    xi = np.clip(np.round(x), 0, n_max).astype(int)
    return np.bincount(xi, minlength=n_max + 1) / len(xi)


def _rows_for_game(res: S.SimResult, gi: S.GameInput, actual_players: pd.DataFrame, actual_teams: pd.DataFrame) -> tuple[list, list]:
    prow, trow = [], []
    for pid, v in res.player.items():
        if pid.startswith("OTHER:"):
            continue
        a = actual_players[actual_players["player_id"] == pid]
        played = bool(len(a)) and bool(a.iloc[0].get("offense_snaps", 0) > 0 or a[["carries", "targets", "attempts"]].sum().sum() > 0)
        team = v["team"]
        for st in PLAYER_STATS:
            if st not in v:
                continue
            x = np.asarray(v[st], float)
            actual = float(a.iloc[0][st]) if len(a) else 0.0
            prow.append({"game_id": gi.game_id, "season": gi.season, "week": gi.week, "team": team, "player_id": pid, "stat": st,
                         "mean": float(x.mean()), "sd": float(x.std()), "p_active": float(np.mean(v["active"])),
                         "quantiles": np.quantile(x, QLEVELS).astype(np.float32).tolist(),
                         "pmf": _pmf(x, STAT_GRID[st]).astype(np.float32).tolist(),
                         "actual": actual, "played": played})
    for team, Tm in res.team.items():
        at = actual_teams[actual_teams["team"] == team]
        for st in TEAM_STATS:
            x = np.asarray(Tm[st], float)
            trow.append({"game_id": gi.game_id, "season": gi.season, "week": gi.week, "team": team, "stat": st,
                         "mean": float(x.mean()), "sd": float(x.std()), "quantiles": np.quantile(x, QLEVELS).astype(np.float32).tolist(),
                         "actual": float(at.iloc[0][st]) if len(at) else np.nan})
    return prow, trow


def run_season(season: int, frames: dict, *, n_sims: int = 10000, limit: int | None = None, verbose=print,
               bundle: dict | None = None) -> dict:
    """Simulate every completed game of ``season`` with a bundle fitted on earlier seasons only."""
    os.makedirs(OUT, exist_ok=True)
    b = bundle or T.fit_bundle(season, frames, verbose=verbose)
    g = D.schedule().to_pandas()
    g = g[(g["season"] == season) & g["home_score"].notna() & g["spread_line"].notna() & g["total_line"].notna()
          & g["game_type"].isin(["REG", "WC", "DIV", "CON", "SB"])].sort_values(["week", "game_id"])
    if limit:
        g = g.head(limit)
    bank = I.historical_bank(season)
    pg = D.load("player_games", [season]).to_pandas(); tg = D.load("team_games", [season]).to_pandas()
    tg["off_td"] = tg["pass_td"] + tg["rush_td"]
    prow, trow = [], []
    t0 = time.time()
    for i, r in enumerate(g.itertuples()):
        try:
            gi = I.historical_game_input(frames, r.game_id, spread_home=r.spread_line, total_line=r.total_line)
        except KeyError as e:
            verbose(f"skip {r.game_id}: {e}"); continue
        res = S.simulate(gi, b, n=n_sims, bank=bank, seed=11 + i)
        coh = S.coherence_report(res)
        if not coh["ok"]:
            raise RuntimeError(f"coherence failure on {r.game_id}: {coh}")
        p, t = _rows_for_game(res, gi, pg[pg["game_id"] == r.game_id], tg[tg["game_id"] == r.game_id])
        prow += p; trow += t
        if (i + 1) % 25 == 0:
            verbose(f"{season}: {i + 1}/{len(g)} games, {time.time() - t0:.0f}s")
    P = pd.DataFrame(prow); Tt = pd.DataFrame(trow)
    P.to_parquet(os.path.join(OUT, f"player_dists_{season}.parquet")); Tt.to_parquet(os.path.join(OUT, f"team_dists_{season}.parquet"))
    with open(os.path.join(OUT, f"bundle_{season}.json"), "w") as f:
        json.dump(b, f)
    return {"season": season, "games": int(len(g)), "player_rows": int(len(P)), "team_rows": int(len(Tt)), "seconds": time.time() - t0}


# ----------------------------------------------------------------------------------------- scoring
def crps_from_quantiles(q: np.ndarray, y: float, levels: np.ndarray = QLEVELS) -> float:
    """CRPS approximated as 2 x the mean pinball loss over the stored quantile levels."""
    diff = y - q
    pin = np.where(diff >= 0, levels * diff, (levels - 1) * diff)
    return float(2.0 * pin.mean())


def _baseline(frames: dict, season: int) -> pd.DataFrame:
    """Naive prior-only baseline for the point estimates: EWMA share x EWMA team volume; EWMA rate x that."""
    e = frames["eligible"]; e = e[e["season"] == season]
    tf = frames["team"][["game_id", "team", "off_rush_att", "off_pass_att"]]
    d = e.merge(tf, on=["game_id", "team"], how="left").reset_index(drop=True)
    rows = []
    car = d["sh_carry_l"].fillna(0) * d["off_rush_att"]
    tgt = d["sh_target_l"].fillna(0) * d["off_pass_att"] * 0.96
    att = np.where(d["position"] == "QB", d["sh_attempt_l"].fillna(0) * d["off_pass_att"], 0.0)
    base = {"carries": car, "rush_yards": car * d["rt_ypc"], "targets": tgt, "receptions": tgt * d["rt_catch_rate"],
            "rec_yards": tgt * d["rt_ypt"], "attempts": att, "pass_yards": att * d["rt_ypa"], "completions": att * d["rt_comp_rate"]}
    base = {k: np.asarray(v, float) for k, v in base.items()}
    for st, v in base.items():
        rows.append(pd.DataFrame({"game_id": d["game_id"], "player_id": d["player_id"], "stat": st, "baseline": np.asarray(v, float)}))
    return pd.concat(rows, ignore_index=True)


def evaluate(season: int, frames: dict | None = None, min_mean: dict | None = None) -> dict:
    """Score a simulated season.  Rows are restricted to players whose predictive mean is above a small
    floor per statistic (a fourth-string back with mean 0.3 carries is not a market anyone quotes)."""
    P = pd.read_parquet(os.path.join(OUT, f"player_dists_{season}.parquet"))
    Tt = pd.read_parquet(os.path.join(OUT, f"team_dists_{season}.parquet"))
    floors = min_mean or {"carries": 3.0, "rush_yards": 12.0, "targets": 2.0, "receptions": 1.5, "rec_yards": 12.0,
                          "attempts": 15.0, "completions": 10.0, "pass_yards": 100.0, "pass_td": 0.5, "any_td": 0.1, "rush_td": 0.1, "rec_td": 0.1}
    out = {"season": season, "player": {}, "team": {}}
    if frames is not None:
        base = _baseline(frames, season)
        P = P.merge(base, on=["game_id", "player_id", "stat"], how="left")
    for st, grp in P.groupby("stat"):
        g = grp[grp["mean"] >= floors.get(st, 0.0)]
        if g.empty:
            continue
        q = np.vstack(g["quantiles"].to_numpy()); y = g["actual"].to_numpy(float); mu = g["mean"].to_numpy(float)
        lo50, hi50 = q[:, np.argmin(np.abs(QLEVELS - 0.25))], q[:, np.argmin(np.abs(QLEVELS - 0.75))]
        lo90, hi90 = q[:, np.argmin(np.abs(QLEVELS - 0.05))], q[:, np.argmin(np.abs(QLEVELS - 0.95))]
        pit = (q <= y[:, None]).mean(axis=1)
        rec = {"n": int(len(g)), "mae": float(np.mean(np.abs(mu - y))), "rmse": float(np.sqrt(np.mean((mu - y) ** 2))),
               "bias": float(np.mean(mu - y)), "mean_pred": float(mu.mean()), "mean_actual": float(y.mean()),
               "crps": float(np.mean([crps_from_quantiles(q[i], y[i]) for i in range(len(y))])),
               "cover50": float(np.mean((y >= lo50) & (y <= hi50))), "cover90": float(np.mean((y >= lo90) & (y <= hi90))),
               "pit_hist": np.histogram(pit, bins=10, range=(0, 1))[0].tolist()}
        if "baseline" in g.columns and g["baseline"].notna().any():
            bl = g["baseline"].to_numpy(float); ok = np.isfinite(bl)
            rec["baseline_mae"] = float(np.mean(np.abs(bl[ok] - y[ok]))); rec["baseline_bias"] = float(np.mean(bl[ok] - y[ok]))
            rec["mae_vs_baseline_pct"] = float(100 * (rec["mae"] / rec["baseline_mae"] - 1)) if rec["baseline_mae"] > 0 else None
        if st in LADDERS:
            pm = np.vstack(g["pmf"].to_numpy())
            surv = 1.0 - np.cumsum(pm, axis=1)              # P(Y > k) at index k -> P(Y >= k+1)
            ladder = {}
            for k in LADDERS[st]:
                p = surv[:, k - 1] if k >= 1 else np.ones(len(g))
                yk = (y >= k).astype(float)
                ladder[str(k)] = {"n": int(len(g)), "mean_p": float(p.mean()), "rate": float(yk.mean()), "brier": float(np.mean((p - yk) ** 2))}
            rec["ladder"] = ladder
            rec["ladder_brier"] = float(np.mean([v["brier"] for v in ladder.values()]))
        out["player"][st] = rec
    for st, g in Tt.groupby("stat"):
        y = g["actual"].to_numpy(float); mu = g["mean"].to_numpy(float); ok = np.isfinite(y)
        q = np.vstack(g["quantiles"].to_numpy())
        lo90, hi90 = q[:, np.argmin(np.abs(QLEVELS - 0.05))], q[:, np.argmin(np.abs(QLEVELS - 0.95))]
        out["team"][st] = {"n": int(ok.sum()), "mae": float(np.mean(np.abs(mu[ok] - y[ok]))), "rmse": float(np.sqrt(np.mean((mu[ok] - y[ok]) ** 2))),
                           "bias": float(np.mean(mu[ok] - y[ok])), "cover90": float(np.mean((y[ok] >= lo90[ok]) & (y[ok] <= hi90[ok]))),
                           "crps": float(np.mean([crps_from_quantiles(q[i], y[i]) for i in np.flatnonzero(ok)]))}
    return out
