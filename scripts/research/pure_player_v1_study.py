#!/usr/bin/env python3
"""PURE_PLAYER_V1 held-out evaluation (preregistered: docs/research/PURE_PLAYER_V1_PREREGISTRATION.md).

Arms, all scored on the SAME matched player-game-statistic rows (one row each, never ladder rungs):

    PURE_EWM_BASELINE   simplest sports-only arm: the player's / team's own prior-only EWM
    PURE_PLAYER_V1      the challenger (nfl_edge/engines/player/pure_v1)
    V4_MEF_AS_IS        DATA_PLAYER_V4 with market_env=False exactly as it stands (its VolumeModel still filters the
                        training team-games on implied_total.notna(); its frame carries injury / roster statuses)
    V4_MARKET_CLOSE     DATA_PLAYER_V4 with market_env=True on the consensus closing line -- the "price of
                        independence" DIAGNOSTIC only, never a PURE arm, never used to choose anything
    DATA_ONLY_GAME      the repository's existing football-only game model (research/game_model walk-forward), team
                        points only (no sports-only player challenger exists in the repository)

    python3 scripts/research/pure_player_v1_study.py --data-root <dir with data/raw/nflverse + data/silver> \
        --seasons 2024,2025,2026 --cache <scratch dir> --out research/pure_player_v1

Writes results.json, RESULTS.md, the kit sidecars (PURE + baseline forecasts and outcomes, gzip) and the gate output.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import subprocess
import sys
import time

import numpy as np
import pandas as pd
from scipy import stats as sstats

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.engines.player.pure_v1 import BASELINE_NAME, BASELINE_VERSION, MODEL_NAME, VERSION   # noqa: E402
from nfl_edge.engines.player.pure_v1 import data as PD                                            # noqa: E402
from nfl_edge.engines.player.pure_v1 import features as PF                                        # noqa: E402
from nfl_edge.engines.player.pure_v1 import model as PM                                           # noqa: E402
from nfl_edge.engines.player.pure_v1 import pipeline as PP                                        # noqa: E402

V4_MEF, V4_MKT, DATA_ONLY = "V4_MEF_AS_IS", "V4_MARKET_CLOSE", "DATA_ONLY_GAME"
PRIMARY_SEASONS = (2024, 2025)
V4_STAT = {"receptions": "receptions", "receiving_yards": "receiving_yards", "carries": "carries", "rushing_yards": "rushing_yards",
           "passing_attempts": "attempts", "completions": "completions", "passing_yards": "passing_yards"}


# ------------------------------------------------------------------------------------------------ arms
def pure_frames(data_root: str, cache: str, last_season: int):
    p = os.path.join(cache, f"pure_frames_{last_season}.pkl")
    if os.path.exists(p):
        return pd.read_pickle(p)
    pg = PD.load_player_games(data_root, range(2013, last_season + 1))
    rows, t = PF.build(pg)
    pd.to_pickle((rows, t), p)
    return rows, t


def v4_frame(data_root: str, cache: str, last_season: int) -> pd.DataFrame:
    """The V4 research frame built by the repository's own builder (scripts/research/player_engine_v4_frame.py)."""
    p = os.path.join(cache, f"v4_frame_{last_season}.pkl")
    if os.path.exists(p):
        return pd.read_pickle(p)
    from nfl_edge.engines.player import data_dist as DD
    from nfl_edge.engines.player.features_v2 import add_v2_features
    from nfl_edge.engines.player.features_v3 import add_v3_features
    from nfl_edge.engines.player.v4 import features as F4
    from nfl_edge.research import player_distributions as pdist
    cfg = json.load(open(os.path.join(ROOT, "research/player_distributions/results.json")))["config"]
    raw = pdist.load_player_games(data_root, range(2013, last_season + 1))
    priors = pdist.position_priors(raw, range(2013, 2016))
    d = pdist.add_ewma_features(raw, halflife=cfg["halflife"], season_carry=cfg["season_carry"], shrink_k=cfg["shrink_k"], priors=priors)
    d = add_v2_features(d, halflife=cfg["halflife"], season_carry=cfg["season_carry"], shrink_k=cfg["shrink_k"])
    d = add_v3_features(DD.ensure_columns(d))
    d = F4.add_recency_features(d)
    d = F4.add_absence_features(d, F4.StatusBook(F4.status_frame(data_root, range(2013, last_season + 1))))
    d.to_pickle(p)
    return d


def _beta_summary(mean, sd, ladder):
    var = np.minimum(sd ** 2, 0.9 * mean * (1 - mean))
    phi = mean * (1 - mean) / np.maximum(var, 1e-6) - 1.0
    a, b = mean * phi, (1 - mean) * phi
    surv = np.column_stack([sstats.beta.sf(k, a, b) for k in ladder])
    return sstats.beta.ppf(0.5, a, b), sstats.beta.ppf(0.1, a, b), sstats.beta.ppf(0.9, a, b), surv


def v4_forecasts(frame: pd.DataFrame, teams: pd.DataFrame, season: int, keys: pd.DataFrame, config: dict, name: str) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """V4 forecasts for the PURE population's (player, game) keys of `season`, in the long format of the other arms."""
    from nfl_edge.engines.player.v4 import model as M
    b = M.fit_bundle(frame, season, config, teams=teams, verbose=lambda *x: None)
    rows = frame[(frame.season == season)].merge(keys[["player_id", "game_id"]].drop_duplicates(), on=["player_id", "game_id"], how="inner")
    I = b.intermediates(rows, teams)
    recs = []
    for r in I.to_dict("records"):
        base = {"game_id": r["game_id"], "player_id": r["player_id"]}
        # snap share (Beta(mean, sd), as the V4 snap model defines it)
        if np.isfinite(r.get("snap_mean", np.nan)):
            med, p10, p90, surv = _beta_summary(np.array([r["snap_mean"]]), np.array([r["snap_sd"] if np.isfinite(r.get("snap_sd", np.nan)) else 0.2]),
                                                PM.LADDERS["snap_share"])
            recs.append({**base, "statistic": "snap_share", "mean": r["snap_mean"], "median": med[0], "p10": p10[0], "p90": p90[0],
                         "thresholds": list(zip(PM.LADDERS["snap_share"], surv[0]))})
        # targets: V4's latent negative binomial for targets (mu_targets, r from its own dispersion model)
        if r["pgroup"] in M.TARGET_GROUPS and np.isfinite(r.get("mu_targets", np.nan)):
            rr = b._r("targets", r["pgroup"], r["cv2_targets"]); mu = r["mu_targets"]; p = rr / (rr + mu)
            recs.append({**base, "statistic": "targets", "mean": mu, "median": sstats.nbinom.ppf(0.5, rr, p), "p10": sstats.nbinom.ppf(0.1, rr, p),
                         "p90": sstats.nbinom.ppf(0.9, rr, p), "thresholds": [(k, sstats.nbinom.sf(k - 1, rr, p)) for k in PM.LADDERS["targets"]]})
        D = b.distributions(r, stats=list(set(V4_STAT.values())))
        for stat, vs in V4_STAT.items():
            dist = D.get(vs)
            if dist is None:
                continue
            recs.append({**base, "statistic": stat, "mean": dist.mean(), "median": dist.quantile(0.5), "p10": dist.quantile(0.1),
                         "p90": dist.quantile(0.9), "thresholds": [(k, dist.survival(k)) for k in PM.LADDERS[stat]]})
    L = pd.DataFrame(recs)
    tt = teams[(teams.season == season) & teams.pa.notna()]
    v = b.volume.predict(tt)
    T = tt[["team", "game_id"]].assign(vol_pa=v.vol_pa.to_numpy(), vol_ra=v.vol_ra.to_numpy())
    T["vol_plays"] = T.vol_pa + T.vol_ra
    return L, T, {"arm": name, "config": b.config, "bundle_sha": b.artifact_sha, "volume": b.volume.info}


# ------------------------------------------------------------------------------------------------ metrics
def boot_ci(diff: np.ndarray, games: np.ndarray, B: int, seed: int = 20261010):
    """Paired, game-clustered bootstrap 95% CI of the mean difference."""
    codes, inv = np.unique(games, return_inverse=True)
    sums = np.bincount(inv, weights=diff); cnt = np.bincount(inv).astype(float)
    G = len(codes)
    if G < 3:
        return None
    rng = np.random.default_rng(seed)
    out = np.empty(B)
    for i in range(0, B, 200):
        idx = rng.integers(0, G, size=(min(200, B - i), G))
        out[i:i + idx.shape[0]] = sums[idx].sum(1) / cnt[idx].sum(1)
    return [round(float(np.quantile(out, 0.025)), 6), round(float(np.quantile(out, 0.975)), 6)]


def _surv_at(th, k):
    for a, p in th:
        if abs(float(a) - float(k)) < 1e-9:
            return float(p)
    return np.nan


def compare(A: pd.DataFrame, Bf: pd.DataFrame, rung: pd.DataFrame, nboot: int) -> dict:
    """A = challenger, Bf = reference; both long tables with actual. Matched on (game_id, player_id, statistic)."""
    k = ["game_id", "player_id", "statistic"]
    m = A.merge(Bf[k + ["mean", "p10", "p90", "thresholds"]], on=k, suffixes=("_a", "_b")).merge(rung, on=k, how="left")
    out = {}
    for stat, s in m.groupby("statistic"):
        if not len(s):
            continue
        y = s["actual"].to_numpy(float); g = s["game_id"].to_numpy()
        ea, eb = s["mean_a"].to_numpy(float) - y, s["mean_b"].to_numpy(float) - y
        da = np.abs(ea) - np.abs(eb); dq = ea ** 2 - eb ** 2
        hit = (y >= s["rung"].to_numpy(float)).astype(float)
        pa = np.array([_surv_at(th, kk) for th, kk in zip(s["thresholds_a"], s["rung"])])
        pb = np.array([_surv_at(th, kk) for th, kk in zip(s["thresholds_b"], s["rung"])])
        ok = np.isfinite(pa) & np.isfinite(pb)
        bd = (pa - hit) ** 2 - (pb - hit) ** 2
        out[stat] = {
            "n_player_games": int(len(s)), "n_games": int(len(set(g))),
            "mae_a": round(float(np.abs(ea).mean()), 4), "mae_b": round(float(np.abs(eb).mean()), 4),
            "delta_mae": round(float(da.mean()), 4), "delta_mae_ci95": boot_ci(da, g, nboot),
            "rmse_a": round(float(np.sqrt((ea ** 2).mean())), 4), "rmse_b": round(float(np.sqrt((eb ** 2).mean())), 4),
            "delta_mse": round(float(dq.mean()), 4), "delta_mse_ci95": boot_ci(dq, g, nboot),
            "bias_a": round(float(ea.mean()), 4), "bias_b": round(float(eb.mean()), 4),
            "cov80_a": round(float(((s.p10_a <= y) & (y <= s.p90_a)).mean()), 4), "cov80_b": round(float(((s.p10_b <= y) & (y <= s.p90_b)).mean()), 4),
            "n_brier": int(ok.sum()),
            "brier_a": round(float(((pa[ok] - hit[ok]) ** 2).mean()), 5) if ok.any() else None,
            "brier_b": round(float(((pb[ok] - hit[ok]) ** 2).mean()), 5) if ok.any() else None,
            "delta_brier": round(float(bd[ok].mean()), 5) if ok.any() else None,
            "delta_brier_ci95": boot_ci(bd[ok], g[ok], nboot) if ok.sum() > 10 else None,
        }
    return out


def team_compare(A: pd.DataFrame, Bf: pd.DataFrame, nboot: int, layers=("pa", "ra", "plays", "pts")) -> dict:
    m = A.merge(Bf[["team", "game_id"] + [f"vol_{x}" for x in layers if f"vol_{x}" in Bf.columns]], on=["team", "game_id"], suffixes=("_a", "_b"))
    out = {}
    for x in layers:
        if f"vol_{x}_b" not in m.columns or f"vol_{x}_a" not in m.columns:
            continue
        s = m[m[f"vol_{x}_a"].notna() & m[f"vol_{x}_b"].notna() & m[x].notna()]
        if not len(s):
            continue
        y = s[x].to_numpy(float); g = s["game_id"].to_numpy()
        ea, eb = s[f"vol_{x}_a"].to_numpy(float) - y, s[f"vol_{x}_b"].to_numpy(float) - y
        da = np.abs(ea) - np.abs(eb); dq = ea ** 2 - eb ** 2
        out[x] = {"n_team_games": int(len(s)), "n_games": int(len(set(g))), "mae_a": round(float(np.abs(ea).mean()), 4),
                  "mae_b": round(float(np.abs(eb).mean()), 4), "delta_mae": round(float(da.mean()), 4), "delta_mae_ci95": boot_ci(da, g, nboot),
                  "rmse_a": round(float(np.sqrt((ea ** 2).mean())), 4), "rmse_b": round(float(np.sqrt((eb ** 2).mean())), 4),
                  "delta_mse": round(float(dq.mean()), 4), "delta_mse_ci95": boot_ci(dq, g, nboot),
                  "bias_a": round(float(ea.mean()), 4), "bias_b": round(float(eb.mean()), 4)}
    return out


def representative_rung(base: pd.DataFrame) -> pd.DataFrame:
    """One rung per player-game-stat: the baseline's ladder rung closest to 50% (a pregame choice, outcome-blind)."""
    r = [min(th, key=lambda t: (abs(t[1] - 0.5), t[0]))[0] for th in base["thresholds"]]
    return base[["game_id", "player_id", "statistic"]].assign(rung=r)


# ------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", required=True)
    ap.add_argument("--seasons", default="2024,2025,2026")
    ap.add_argument("--cache", required=True)
    ap.add_argument("--out", default=os.path.join(ROOT, "research", "pure_player_v1"))
    ap.add_argument("--bootstrap", type=int, default=1000)
    ap.add_argument("--kit-gate", default=None, help="path to the kit's prop_projection_gate.py (validate / compare)")
    ap.add_argument("--no-v4", action="store_true")
    ap.add_argument("--last-season", type=int, default=None, help="last season loaded into the frames (default: max of --seasons)")
    a = ap.parse_args()
    t0 = time.time()
    seasons = [int(x) for x in a.seasons.split(",")]
    os.makedirs(a.out, exist_ok=True); os.makedirs(a.cache, exist_ok=True)
    last = a.last_season or max(seasons)
    rows, t = pure_frames(a.data_root, a.cache, last)
    log = lambda *x: print(f"[{time.time() - t0:6.0f}s]", *x, flush=True)   # noqa: E731
    log("pure frames", rows.shape, t.shape)
    frame = teams4 = None
    if not a.no_v4:
        from nfl_edge.engines.player.v4.volume import team_game_table
        frame = v4_frame(a.data_root, a.cache, last)
        teams4 = team_game_table(frame)
        log("v4 frame", frame.shape)
    wf = pd.read_parquet(os.path.join(ROOT, "research/game_model/walkforward_predictions.parquet"))
    sched = PD.sports_schedule(PD.read_schedule(a.data_root))
    # closing lines are read ONLY here, for the separate price-of-independence diagnostic, never by a PURE arm
    lines = pd.read_csv(os.path.join(a.data_root, "data/raw/nflverse/schedules/games.csv"), usecols=["game_id", "home_team", "spread_line", "total_line"])
    lines["home_team"] = lines["home_team"].replace(PD.TEAM_FIX)

    player_long = {}; team_long = {}; info = {"seasons": {}}
    for S in seasons:
        out = PP.run(rows, t, S)
        L = {k: v.assign(season=S) for k, v in out["player"].items()}
        T = {k: v for k, v in out["team"].items()}
        si = {"pure_model": out["model"].info, "n_rows": {k: int(len(v)) for k, v in L.items()},
              "population_forecast_counts": out["population_counts"],
              "scored_counts": L[MODEL_NAME].groupby("statistic").size().to_dict()}
        if frame is not None:
            keys = L[MODEL_NAME][["player_id", "game_id"]]
            for name, cfg in ((V4_MEF, {"market_env": False}), (V4_MKT, {})):
                l4, t4, i4 = v4_forecasts(frame, teams4, S, keys, cfg, name)
                act = L[BASELINE_NAME][["game_id", "player_id", "statistic", "season", "week", "pgroup", "actual", "played", "kickoff"]]
                L[name] = l4.merge(act, on=["game_id", "player_id", "statistic"], how="inner")
                T[name] = T[BASELINE_NAME][["team", "game_id", "season", "week", "pa", "ra", "plays", "pts"]].merge(t4, on=["team", "game_id"], how="left")
                si[name] = i4
            # the training-sample selection of V4's VolumeModel: rows the implied_total filter keeps vs every team-game
            tr = teams4[(teams4.season < S) & teams4.pa.notna()]
            si["v4_volume_training_selection"] = {"team_games_with_box_score": int(len(tr)),
                                                  "kept_by_implied_total_filter": int(tr.implied_total.notna().sum()),
                                                  "pure_team_games_used": int(out["model"].info["n_team_games"])}
            log(S, "v4 arms", {k: len(v) for k, v in L.items()})
        # existing football-only game model (team points), and the closing-line implied team total (diagnostic)
        w = wf[wf.season == S][["game_id", "model_margin", "model_total"]]
        tp = T[BASELINE_NAME][["team", "game_id", "season", "week", "pa", "ra", "plays", "pts"]].merge(
            sched[["game_id", "home_team"]], on="game_id", how="left")
        home = (tp.team == tp.home_team).to_numpy()
        ww = tp.merge(w, on="game_id", how="left")
        T[DATA_ONLY] = tp.assign(vol_pts=np.where(home, (ww.model_total + ww.model_margin) / 2, (ww.model_total - ww.model_margin) / 2))
        ll = tp.merge(lines[["game_id", "spread_line", "total_line"]], on="game_id", how="left")
        T["CLOSING_IMPLIED_TOTAL"] = tp.assign(vol_pts=np.where(home, (ll.total_line + ll.spread_line) / 2, (ll.total_line - ll.spread_line) / 2))
        for k, v in L.items():
            player_long.setdefault(k, []).append(v)
        for k, v in T.items():
            team_long.setdefault(k, []).append(v.assign(season=S))
        info["seasons"][S] = si
        log(S, "done")
    P = {k: pd.concat(v, ignore_index=True) for k, v in player_long.items()}
    TT = {k: pd.concat(v, ignore_index=True) for k, v in team_long.items()}
    for k in P:
        P[k]["pgroup"] = P[k]["pgroup"].fillna("NA")
    rung = representative_rung(P[BASELINE_NAME])

    def scope(df, mask_fn):
        return df[mask_fn(df)]

    scopes = {"primary_2024_2025": lambda d: d.season.isin(PRIMARY_SEASONS)}
    for S in seasons:
        scopes[f"season_{S}"] = (lambda S: lambda d: d.season == S)(S)
    results = {"protocol": {"preregistration": "docs/research/PURE_PLAYER_V1_PREREGISTRATION.md", "primary_seasons": list(PRIMARY_SEASONS),
                            "seasons": seasons, "bootstrap": a.bootstrap, "cluster": "game_id",
                            "metric_policy": "one row per player-game-statistic; representative rung = baseline ladder rung closest to 50%",
                            "versions": {MODEL_NAME: VERSION, BASELINE_NAME: BASELINE_VERSION}}, "info": info}
    pairs = [(MODEL_NAME, BASELINE_NAME)]
    if frame is not None:
        pairs += [(V4_MEF, BASELINE_NAME), (MODEL_NAME, V4_MEF), (MODEL_NAME, V4_MKT), (V4_MKT, BASELINE_NAME)]
    results["player"] = {}
    for sc, fn in scopes.items():
        results["player"][sc] = {f"{x}__vs__{y}": compare(scope(P[x], fn), scope(P[y], fn), rung, a.bootstrap) for x, y in pairs}
    # by position group, primary scope, PURE vs baseline
    results["player_by_group"] = {}
    for grp in ("QB", "RB", "WR", "TE"):
        fn = (lambda grp: lambda d: d.season.isin(PRIMARY_SEASONS) & (d.pgroup == grp))(grp)
        results["player_by_group"][grp] = compare(scope(P[MODEL_NAME], fn), scope(P[BASELINE_NAME], fn), rung, a.bootstrap)
    tpairs = [(MODEL_NAME, BASELINE_NAME), (MODEL_NAME, DATA_ONLY), (DATA_ONLY, BASELINE_NAME), (MODEL_NAME, "CLOSING_IMPLIED_TOTAL")]
    if frame is not None:
        tpairs += [(V4_MEF, BASELINE_NAME), (MODEL_NAME, V4_MEF), (MODEL_NAME, V4_MKT)]
    results["team"] = {}
    for sc, fn in scopes.items():
        results["team"][sc] = {f"{x}__vs__{y}": team_compare(TT[x][fn(TT[x])], TT[y][fn(TT[y])], a.bootstrap) for x, y in tpairs}
    # market ticker inventory vs the full sports population (2025): the evaluated-population selection effect
    lad = pd.read_parquet(os.path.join(ROOT, "research/signal_discovery_wave1/prop_ladders.parquet"))
    listed = set(zip(lad.gsis_id, lad.game_id))
    sel = {}
    for name in (MODEL_NAME, BASELINE_NAME):
        d = P[name][P[name].season == 2025].copy()
        d["listed"] = [(p, g) in listed for p, g in zip(d.player_id, d.game_id)]
        sel[name] = {st: {"n_all": int(len(s)), "n_market_listed": int(s.listed.sum()),
                          "mae_all": round(float(np.abs(s["mean"] - s.actual).mean()), 4),
                          "mae_market_listed": round(float(np.abs(s[s.listed]["mean"] - s[s.listed].actual).mean()), 4) if s.listed.any() else None,
                          "mae_not_listed": round(float(np.abs(s[~s.listed]["mean"] - s[~s.listed].actual).mean()), 4) if (~s.listed).any() else None,
                          "bias_market_listed": round(float((s[s.listed]["mean"] - s[s.listed].actual).mean()), 4) if s.listed.any() else None,
                          "bias_not_listed": round(float((s[~s.listed]["mean"] - s[~s.listed].actual).mean()), 4) if (~s.listed).any() else None}
                     for st, s in d.groupby("statistic")}
    results["market_inventory_selection_2025"] = {"listed_player_games_any_stat": len(listed), "by_arm": sel,
                                                  "source": "research/signal_discovery_wave1/prop_ladders.parquet (Kalshi 2025 horizon archive), read only for this diagnostic"}
    # coverage / exclusions
    elig = rows[rows.season.isin(seasons)]
    results["coverage"] = {str(S): {"player_games_in_sports_data": int((elig.season == S).sum()),
                                    "played": int(((elig.season == S) & elig.played).sum()),
                                    "rows_by_stat": P[MODEL_NAME][P[MODEL_NAME].season == S].groupby("statistic").size().to_dict(),
                                    "v4_matched_rows_by_stat": (P[V4_MEF][P[V4_MEF].season == S].groupby("statistic").size().to_dict() if V4_MEF in P else None)}
                           for S in seasons}
    # sidecars (kit interim format) + gate
    side = os.path.join(a.out, "sidecars"); os.makedirs(side, exist_ok=True)
    gate_out = {}
    for name, ver in ((MODEL_NAME, VERSION), (BASELINE_NAME, BASELINE_VERSION)):
        d = P[name][P[name].season.isin(seasons)]
        through = {S: str(rows.loc[rows.season < S, "kickoff"].max()) for S in seasons}
        fc, oc = [], []
        for S in seasons:
            f, o = PP.sidecar_rows(d[d.season == S], ver, through[S])
            fc += f; oc += o
        fp = os.path.join(a.cache, f"{name}.forecasts.jsonl")
        with open(fp, "w") as fh:
            fh.writelines(json.dumps(r, sort_keys=True) + "\n" for r in fc)
        with gzip.open(os.path.join(side, f"{name}.forecasts.jsonl.gz"), "wt") as fh:
            fh.writelines(json.dumps(r, sort_keys=True) + "\n" for r in fc)
        if name == BASELINE_NAME:
            op = os.path.join(a.cache, "outcomes.jsonl")
            with open(op, "w") as fh:
                fh.writelines(json.dumps(r, sort_keys=True) + "\n" for r in oc)
            with gzip.open(os.path.join(side, "outcomes.jsonl.gz"), "wt") as fh:
                fh.writelines(json.dumps(r, sort_keys=True) + "\n" for r in oc)
    if a.kit_gate:
        for name in (MODEL_NAME, BASELINE_NAME):
            r = subprocess.run([sys.executable, "-I", a.kit_gate, "validate", "--forecasts", os.path.join(a.cache, f"{name}.forecasts.jsonl")],
                               capture_output=True, text=True)
            gate_out[f"validate_{name}"] = {"returncode": r.returncode, "stdout": json.loads(r.stdout) if r.stdout.strip() else None, "stderr": r.stderr[-2000:]}
        cp = os.path.join(a.out, "gate_compare.json")
        r = subprocess.run([sys.executable, "-I", a.kit_gate, "compare", "--champion", os.path.join(a.cache, f"{BASELINE_NAME}.forecasts.jsonl"),
                            "--challenger", os.path.join(a.cache, f"{MODEL_NAME}.forecasts.jsonl"), "--outcomes", os.path.join(a.cache, "outcomes.jsonl"),
                            "--bootstrap", "500", "--output", cp], capture_output=True, text=True)
        gate_out["compare"] = {"returncode": r.returncode, "output": os.path.relpath(cp, ROOT), "stderr": r.stderr[-2000:]}
    results["kit_gate"] = gate_out
    results["seconds"] = round(time.time() - t0, 1)
    with open(os.path.join(a.out, "results.json"), "w") as fh:
        json.dump(results, fh, indent=1, sort_keys=True, default=str)
    log("wrote", os.path.join(a.out, "results.json"))


if __name__ == "__main__":
    main()
