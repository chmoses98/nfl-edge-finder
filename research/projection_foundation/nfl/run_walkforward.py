#!/usr/bin/env python3
"""NFL Projection Foundation walk-forward entry point.

Stages (run in order; each writes under research/projection_foundation/results/):
  select   development + validation: model ladder A..F, incumbents, distribution families, corrections;
           freezes the per-family winner in results/nfl_frozen_selection.json (never overwritten unless --refreeze)
  holdout  scores the FROZEN winners (and baseline A, incumbents) on 2024-2025 and the read-only 2026 weeks 1-4 check.
           Refuses to run without the frozen selection. 2026 weeks >= 5 are never scored (market holdout embargo).
  gate     Projection Quality Gate on validation/holdout projections + team reconciliation
  report   writes results/summary.json (sift.projection_foundation.sport_summary.v1) and RESULTS_NFL.md

Usage: python -m nfl.run_walkforward [--stage all|select|holdout|gate|report] [--rebuild]
(run from research/projection_foundation)
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PF_ROOT = os.path.dirname(HERE)
sys.path.insert(0, PF_ROOT)

from pf_core import metrics, registry  # noqa: E402

from nfl import data as D  # noqa: E402
from nfl import evaluate as EV  # noqa: E402
from nfl import incumbent as INC  # noqa: E402
from nfl import ladder as L  # noqa: E402
from nfl import pipeline as P  # noqa: E402

RESULTS = os.path.join(PF_ROOT, "results")
EXP_DIR = os.path.join(RESULTS, "experiments")
FROZEN = os.path.join(RESULTS, "nfl_frozen_selection.json")
WF = os.path.join(RESULTS, "nfl_walkforward.json")
STAGE1 = os.path.join(D.CACHE, "stage1.pkl")
LADDER_MODELS = ["A", "B", "C", "D", "E", "F"]
TEAM_EXTRA = ["D_opp"]
INC_VERSIONS = {"INC_0.4.0": "shadow-0.4.0", "INC_0.5.0": "shadow-0.5.0"}
MODEL_NAMES = {"A": "A_season_avg_shrunk", "B": "B_ewma_shrunk", "C": "C_opportunity_x_efficiency",
               "D": "D_opp_env_adjusted", "D_opp": "D_opp_adjusted_only", "E": "E_lightgbm_walkforward", "F": "F_stack",
               "MKT": "MKT_closing_implied_total", "INC_0.4.0": "incumbent_shadow-0.4.0", "INC_0.5.0": "challenger_shadow-0.5.0",
               "D_vac": "D_plus_vacated_opportunity", "F_vac": "F_plus_vacated_opportunity"}


def log(*a):
    print(*a, flush=True)


# ------------------------------------------------------------------------------------------------ build
def stage1(rebuild=False):
    if os.path.exists(STAGE1) and not rebuild:
        return pickle.load(open(STAGE1, "rb"))
    t0 = time.time()
    from nfl import project as PR
    sched = D.load_schedule()
    pg = D.cached("player_games", lambda: D.player_games(sched), force=rebuild)
    D.cached("team_games", lambda: D.team_games(sched), force=rebuild)
    blk, mode = PR.upcoming_block(sched)
    up = PR.upcoming_rows(sched, pg, blk, mode) if mode == "upcoming_week" else None
    log(f"forward block {blk} ({mode}): {0 if up is None else len(up)} candidate player rows")
    tf, tpreds, tparams, pf = P.build_frames(up, blk if mode == "upcoming_week" else None, log=log, force=rebuild)
    if mode != "upcoming_week":
        pf.loc[pf.block == blk, "split"] = "forward"
        tf.loc[tf.block == blk, "split"] = "forward"
    preds, params, pops = P.player_ladder(pf, log=log)
    out = {"forward_mode": mode, "forward_block": blk, "tf": tf, "tpreds": tpreds, "tparams": tparams, "pf": pf, "preds": preds, "params": params, "pops": pops,
           "seconds": time.time() - t0}
    pickle.dump(out, open(STAGE1, "wb"))
    return out


def incumbent_table(pf, fam):
    """Incumbent means + pmfs aligned to pf rows (NaN where the incumbent has no row)."""
    stat = P.INC_STAT[fam]
    out = {}
    for name, ver in INC_VERSIONS.items():
        mp = os.path.join(D.CACHE, f"incumbent_{ver}.parquet")
        if not os.path.exists(mp):
            continue
        m = pd.read_parquet(mp)
        m = m[m.stat == stat].drop_duplicates(["player_id", "game_id"])
        key = pf[["player_id", "game_id"]].merge(m[["player_id", "game_id", "mu"]], on=["player_id", "game_id"], how="left")
        mu = key.mu.to_numpy()
        Pm = None
        if fam != "anytime_td":
            z = INC.load(ver, stat)
            if z is not None:
                k, Pz = z
                idx = pd.Series(np.arange(len(k)), index=pd.MultiIndex.from_frame(k))
                pos = idx.reindex(pd.MultiIndex.from_frame(pf[["player_id", "game_id"]])).to_numpy()
                Pm = (pos, Pz)
        out[name] = (mu, Pm)
    return out


# ------------------------------------------------------------------------------------------------ helpers
def _dist_for(fam_kind, params, mu, lo, K):
    return EV.make(params, mu)


def model_eval(y, mu, dist, clusters, rungs):
    return EV.score(y, mu, dist, clusters, rungs)


def _inc_dist(Pm, rows_mask):
    pos, Pz = Pm
    sel = pos[rows_mask]
    ok = np.isfinite(sel)
    Pr = np.zeros((len(sel), Pz.shape[1]))
    Pr[ok] = Pz[sel[ok].astype(int)]
    from pf_core.dists import DistBatch
    return DistBatch(0, Pr), ok


def family_frames(S):
    """Yield (family, kind, frame with y/game/split/pop, preds DataFrame, spec, incumbents)."""
    tf, pf = S["tf"], S["pf"]
    for fam, s in P.TEAM_FAMILIES.items():
        df = tf[["game_id", "team", "season", "week", "split", "played"]].copy()
        df["y"] = tf[s["y"]]
        df["pop"] = tf.played.to_numpy()
        yield fam, ("count"), df, S["tpreds"][fam], {"lo": 0, "K": s["K"], "rungs": None, "unit": "team-game",
                                                      "pop_text": P.POP_TEXT["TEAM"], "opp": None}, {}
    for fam, s in P.PLAYER_FAMILIES.items():
        df = pf[["game_id", "team", "player_id", "season", "week", "split", "position"]].copy()
        df["y"] = pf[s["y"]].to_numpy(float)
        df["pop"] = S["pops"][s["pop"]] & pf.y_observed.to_numpy()
        yield fam, s["kind"], df, S["preds"][fam], {"lo": s["lo"], "K": s["K"], "rungs": s["rungs"], "unit": "player-game",
                                                     "pop_text": P.POP_TEXT[s["pop"]], "opp": s["opp"]}, incumbent_table(pf, fam)


# ------------------------------------------------------------------------------------------------ select
def select(S, corrections=None):
    res = {"families": {}, "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    frozen = {}
    corrections = corrections or {}
    for fam, kind, df, preds, spec, incs in family_frames(S):
        t0 = time.time()
        preds = preds.copy()
        for cname, cser in corrections.get(fam, {}).items():
            preds[cname] = cser
        dev = (df.split == "development").to_numpy() & df["pop"].to_numpy()
        val = (df.split == "validation").to_numpy() & df["pop"].to_numpy()
        y = df.y.to_numpy(float)
        models = [m for m in preds.columns if m not in ("F_holdout",) and preds[m].notna().any()]
        fr = {"kind": kind, "unit": spec["unit"], "population": spec["pop_text"], "opportunity_family": spec["opp"],
              "models": {}, "dist_selection": {}}
        cand = EV.DIST_CANDIDATES[kind if kind != "count" or fam not in ("team_points",) else "count"]
        if fam == "team_points":
            cand = ["poisson", "nb", "empirical_resid", "normal_binned"]
        loss_val = {}
        for m in models:
            mu = preds[m].to_numpy(float)
            okd = dev & np.isfinite(mu)
            okv = val & np.isfinite(mu)
            if okv.sum() < 50:
                continue
            best = None
            dsel = {}
            for dk in cand:
                try:
                    prm = EV.fit_dist(dk, kind, y[okd], mu[okd], spec["lo"], spec["K"])
                    dv = EV.make(prm, mu[okv])
                    c = float(dv.crps(y[okv]).mean())
                    ls = float(-dv.logpmf(y[okv]).mean())
                except Exception as e:  # noqa: BLE001
                    log(f"    dist {dk} failed for {fam}/{m}: {e}")
                    continue
                dsel[dk] = {"val_crps": c, "val_log_score": ls}
                if best is None or c < best[0]:
                    best = (c, dk, prm)
            fr["dist_selection"][m] = dsel
            prm = best[2]
            out = {"dist": best[1]}
            for split, ok in (("development", okd), ("validation", okv)):
                dd = EV.make(prm, mu[ok])
                out[split] = model_eval(y[ok], mu[ok], dd, df.game_id.to_numpy()[ok], spec["rungs"])
                if split == "validation":
                    loss_val[m] = (np.where(okv)[0], dd.crps(y[ok]), np.abs(mu[ok] - y[ok]))
            out["dist_params"] = prm
            fr["models"][m] = out
        # incumbents: their own pmf (or Bernoulli for anytime TD)
        for name, (mu_i, Pm) in incs.items():
            for split, base in (("development", dev), ("validation", val)):
                ok = base & np.isfinite(mu_i)
                if ok.sum() < 50:
                    continue
                if Pm is not None:
                    dd, okp = _inc_dist(Pm, ok)
                else:
                    dd = EV.make({"kind": "bernoulli"}, mu_i[ok])
                fr["models"].setdefault(name, {"dist": "incumbent_own"})[split] = model_eval(
                    y[ok], mu_i[ok], dd, df.game_id.to_numpy()[ok], spec["rungs"])
                if split == "validation":
                    loss_val[name] = (np.where(ok)[0], dd.crps(y[ok]), np.abs(mu_i[ok] - y[ok]))
        # comparisons on the validation rows common to both (paired, game-clustered)
        gid = df.game_id.to_numpy()

        def paired(a, b):
            ia, la, ea = loss_val[a]
            ib, lb, eb = loss_val[b]
            common = np.intersect1d(ia, ib)
            if len(common) < 50:
                return None
            sa = pd.Series(la, index=ia).loc[common].to_numpy()
            sb = pd.Series(lb, index=ib).loc[common].to_numpy()
            ma = pd.Series(ea, index=ia).loc[common].to_numpy()
            mb = pd.Series(eb, index=ib).loc[common].to_numpy()
            r = EV.diff(sa, sb, gid[common])
            r["mae_diff"] = EV.diff(ma, mb, gid[common])
            r["n_common"] = int(len(common))
            return r
        ladder = [m for m in fr["models"] if not m.startswith("INC") and m != "MKT" and "validation" in fr["models"][m]]
        best_m = min(ladder, key=lambda m: fr["models"][m]["validation"]["crps"])
        for m in fr["models"]:
            if m not in loss_val:
                continue
            fr["models"][m]["vs_baseline"] = paired(m, "A") if m != "A" else None
            fr["models"][m]["vs_incumbent"] = paired(m, "INC_0.4.0") if "INC_0.4.0" in loss_val and m != "INC_0.4.0" else None
            fr["models"][m]["vs_challenger_0_5_0"] = paired(m, "INC_0.5.0") if "INC_0.5.0" in loss_val and m != "INC_0.5.0" else None
            fr["models"][m]["vs_best"] = paired(m, best_m) if m != best_m else None
        fr["best_model"] = best_m
        frozen[fam] = {"model": best_m, "dist": fr["models"][best_m]["dist"], "dist_params": fr["models"][best_m]["dist_params"],
                       "lo": spec["lo"], "K": spec["K"], "rungs": spec["rungs"], "kind": kind,
                       "baseline_dist_params": fr["models"]["A"]["dist_params"]}
        res["families"][fam] = fr
        log(f"[select] {fam}: best={best_m} val CRPS " + ", ".join(
            f"{m}={fr['models'][m]['validation']['crps']:.4f}" for m in fr["models"] if "validation" in fr["models"][m])
            + f"  ({time.time() - t0:.0f}s)")
    return res, frozen


# ------------------------------------------------------------------------------------------------ holdout
def holdout(S, frozen, corrections=None):
    out = {}
    corrections = corrections or {}
    for fam, kind, df, preds, spec, incs in family_frames(S):
        preds = preds.copy()
        for cname, cser in corrections.get(fam, {}).items():
            preds[cname] = cser
        fz = frozen[fam]
        y = df.y.to_numpy(float)
        gid = df.game_id.to_numpy()
        fo = {}
        for split in ("holdout", "check2026"):
            base = (df.split == split).to_numpy() & df["pop"].to_numpy()
            if base.sum() < 30:
                continue
            col = fz["model"]
            if col == "F" and "F_holdout" in preds.columns:
                col = "F_holdout"          # pre-declared: stack weights refitted on development+validation
            mu = preds[col].to_numpy(float)
            muA = preds["A"].to_numpy(float)
            ok = base & np.isfinite(mu) & np.isfinite(muA)
            dbest = EV.make(fz["dist_params"], mu[ok])
            dA = EV.make(fz["baseline_dist_params"], muA[ok])
            r = model_eval(y[ok], mu[ok], dbest, gid[ok], spec["rungs"])
            r["model"] = fz["model"]
            rA = model_eval(y[ok], muA[ok], dA, gid[ok], spec["rungs"])
            r["baseline_A"] = {k: rA[k] for k in ("n_obs", "mae", "rmse", "bias", "crps", "cover_80")}
            r["vs_baseline"] = EV.diff(dbest.crps(y[ok]), dA.crps(y[ok]), gid[ok])
            r["vs_baseline"]["mae_diff"] = EV.diff(np.abs(mu[ok] - y[ok]), np.abs(muA[ok] - y[ok]), gid[ok])
            r["threshold_reliability"] = EV.threshold_reliability(y[ok], dbest, spec["rungs"]) if spec["rungs"] else []
            for name, (mu_i, Pm) in incs.items():
                oki = ok & np.isfinite(mu_i)
                if oki.sum() < 30:
                    continue
                if Pm is not None:
                    di, _ = _inc_dist(Pm, oki)
                else:
                    di = EV.make({"kind": "bernoulli"}, mu_i[oki])
                sub = np.isin(np.where(ok)[0], np.where(oki)[0])
                ri = model_eval(y[oki], mu_i[oki], di, gid[oki], spec["rungs"])
                r[name] = {k: ri[k] for k in ("n_obs", "mae", "rmse", "bias", "crps", "cover_80")}
                r[f"vs_{name}"] = EV.diff(dbest.crps(y[ok])[sub], di.crps(y[oki]), gid[oki])
                r[f"vs_{name}"]["mae_diff"] = EV.diff(np.abs(mu[oki] - y[oki]), np.abs(mu_i[oki] - y[oki]), gid[oki])
            fo[split] = r
        out[fam] = fo
        h = fo.get("holdout", {})
        if h:
            log(f"[holdout] {fam}: {fz['model']} CRPS {h['crps']:.4f} vs A {h['baseline_A']['crps']:.4f} "
                f"diff {h['vs_baseline']['mean_diff']:+.4f} {np.round(h['vs_baseline']['ci95'], 4)}"
                + (f" | vs INC0.4 {h['vs_INC_0.4.0']['mean_diff']:+.4f} {np.round(h['vs_INC_0.4.0']['ci95'], 4)}" if "vs_INC_0.4.0" in h else ""))
    return out


def write_records(sel, hold):
    os.makedirs(EXP_DIR, exist_ok=True)
    for fam, fr in sel["families"].items():
        for m, r in fr["models"].items():
            if "validation" not in r:
                continue
            v = r["validation"]
            rec = registry.ExperimentRecord(
                experiment_id=f"nfl_{fam}_{m}_validation", sport="NFL", family=fam, model=MODEL_NAMES.get(m, m),
                model_version="pf-nfl-1.0", question=f"How accurate is {MODEL_NAMES.get(m, m)} for {fam}?",
                hypothesis="beats the season-average baseline A on validation CRPS", split="validation",
                train_period="2012-2021 (features from 2012; tuning 2016-2021; E refit each season on all earlier seasons)",
                eval_period="2022-2023 regular seasons", features=[], hyperparameters={"dist": r.get("dist")},
                data_provenance=["nflverse stats_player/stats_team/snap_counts/schedules/injuries release files (data/raw/nflverse/_manifest.jsonl)"],
                n_obs=v["n_obs"], n_independent=v["n_obs"], n_clusters=v["n_clusters"],
                point={k: v[k] for k in ("mae", "rmse", "bias", "corr")},
                distribution={k: v[k] for k in ("crps", "log_score", "cover_50", "cover_80", "cover_90", "pit_var_ratio")},
                vs_baseline=r.get("vs_baseline") or {}, vs_incumbent=r.get("vs_incumbent") or {},
                limitations=["conditional on participation (DNP rows excluded)", "injury designations untimestamped"],
                verdict="best" if m == fr["best_model"] else ("incumbent" if m.startswith("INC") else ("baseline" if m == "A" else "candidate")))
            registry.write_record(rec, EXP_DIR)
    for fam, fo in (hold or {}).items():
        h = fo.get("holdout")
        if not h:
            continue
        rec = registry.ExperimentRecord(
            experiment_id=f"nfl_{fam}_frozen_holdout", sport="NFL", family=fam, model=MODEL_NAMES.get(h["model"], h["model"]),
            model_version="pf-nfl-1.0", question=f"Does the frozen {fam} winner hold up out of sample?",
            hypothesis="validation advantage over baseline persists on 2024-2025", split="holdout",
            train_period="<= previous season (walk-forward)", eval_period="2024-2025 regular seasons", features=[],
            hyperparameters={}, data_provenance=["nflverse release files"], n_obs=h["n_obs"], n_independent=h["n_obs"],
            n_clusters=h["n_clusters"], point={k: h[k] for k in ("mae", "rmse", "bias")},
            distribution={k: h[k] for k in ("crps", "log_score", "cover_80", "pit_var_ratio")},
            vs_baseline=h["vs_baseline"], vs_incumbent=h.get("vs_INC_0.4.0") or {}, verdict="holdout (frozen)")
        registry.write_record(rec, EXP_DIR)


def _json(o):
    return registry._json_default(o)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="all")
    ap.add_argument("--rebuild", action="store_true")
    ap.add_argument("--refreeze", action="store_true", help="overwrite the frozen selection (development work only)")
    a = ap.parse_args(argv)
    os.makedirs(RESULTS, exist_ok=True)
    S = stage1(a.rebuild)
    from nfl import diagnostics as DG
    wf = json.load(open(WF)) if os.path.exists(WF) else {}
    corr = DG.corrections(S)
    if a.stage in ("all", "select"):
        sel, frozen = select(S, corr["preds"])
        wf["select"] = sel
        wf["corrections"] = corr["summary"]
        if not os.path.exists(FROZEN) or a.refreeze:
            json.dump({"frozen_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "families": frozen},
                      open(FROZEN, "w"), indent=1, default=_json)
            log(f"froze selection -> {FROZEN}")
        wf["diagnostics"] = DG.run_all(S, json.load(open(FROZEN))["families"])
        json.dump(wf, open(WF, "w"), indent=1, default=_json)
    if a.stage in ("all", "holdout"):
        if not os.path.exists(FROZEN):
            raise SystemExit("no frozen selection: run --stage select first")
        frozen = json.load(open(FROZEN))["families"]
        wf["holdout"] = holdout(S, frozen, corr["preds"])
        json.dump(wf, open(WF, "w"), indent=1, default=_json)
        write_records(wf["select"], wf["holdout"])
    if a.stage in ("all", "gate"):
        from nfl import gate_eval
        wf["gate"] = gate_eval.run(S, json.load(open(FROZEN))["families"], corr["preds"])
        json.dump(wf, open(WF, "w"), indent=1, default=_json)
    if a.stage in ("all", "report"):
        from nfl import report
        report.write(wf, json.load(open(FROZEN)), S)


if __name__ == "__main__":
    main()
