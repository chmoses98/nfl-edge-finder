"""Gate validation: run the Projection Quality Gate on frozen-winner projections (validation + holdout) and test
whether REVIEW / BLOCK projections actually carry larger errors. Plus team reconciliation.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pf_core import gate

from . import diagnostics as DG
from . import evaluate as EV
from . import gate_nfl as G
from . import ladder as L
from . import pipeline as P

HIST_COLS = ["targets", "carries", "attempts", "touches", "receptions", "receiving_yards", "rushing_yards", "completions",
             "passing_yards", "passing_tds", "any_td"]


def model_mean(S, corr, fam, model, split):
    preds = S["preds"][fam] if fam in S["preds"] else S["tpreds"][fam]
    late = split in ("holdout", "check2026", "forward")
    if late and f"{model}_holdout" in preds.columns:
        return preds[f"{model}_holdout"].to_numpy(float)
    if model in preds.columns:
        return preds[model].to_numpy(float)
    c = corr.get(fam, {})
    if late and f"{model}_holdout" in c:
        return np.asarray(c[f"{model}_holdout"], float)
    return np.asarray(c[model], float)


def opp_factor(S, fam):
    """Multiplicative opponent adjustment actually applied by the D-type efficiency term (None for volume families)."""
    prm = S["params"].get(fam, {})
    facs = prm.get("D_factors")
    if not facs:
        return None
    pf = S["pf"]
    f0 = facs[0]
    if f0 not in pf.columns:
        return None
    return np.exp(prm["D_beta"][0] * np.log(pf[f0].clip(0.5, 2.0).fillna(1.0).to_numpy()))


def run(S, frozen, corr, splits=("validation", "holdout"), max_rows_per_family=None, publish_pmf_mean=True):
    pf = S["pf"]
    pf_h = G.add_histories(pf, HIST_COLS)
    og = G.opp_season_games(S["tf"])
    pf_h = pf_h.merge(og, on=["game_id", "team"], how="left")
    des = DG._vacated(S)["designation"]
    status_map = {"None": "ACTIVE", "Questionable": "QUESTIONABLE", "Doubtful": "DOUBTFUL", "Out": "OUT"}
    out = {"by_family": {}, "error_by_status": {}, "pooled": {}}
    pooled = []
    for fam, s in P.PLAYER_FAMILIES.items():
        fz = frozen[fam]
        oppfam = {"receptions": "targets", "receiving_yards": "targets", "rushing_yards": "carries", "completions": "passing_attempts",
                  "passing_yards": "passing_attempts", "passing_tds": "passing_attempts"}.get(fam, fam)
        of = opp_factor(S, fam) if fz["model"] in ("D", "D_vac", "F", "F_vac") else None
        for split in splits:
            m = S["pops"][s["pop"]] & (pf.split == split).to_numpy() & pf.y_observed.to_numpy()
            mu = model_mean(S, corr, fam, fz["model"], split)
            m &= np.isfinite(mu)
            idx = np.where(m)[0]
            if max_rows_per_family:
                idx = idx[:max_rows_per_family]
            dist = EV.make(fz["dist_params"], mu[idx])
            # published mean = the pmf's own mean (one coherent object); the raw model mean is kept for the 'naive' variant
            pub = dist.mean if publish_pmf_mean else mu[idx]
            if fam == "anytime_td":
                opp = (model_mean(S, corr, "targets", frozen["targets"]["model"], split) +
                       model_mean(S, corr, "carries", frozen["carries"]["model"], split))[idx]
            else:
                opp = model_mean(S, corr, oppfam, frozen[oppfam]["model"], split)[idx]
            res = G.run(fam, pf_h.iloc[idx], pub, dist, s["y"], opp_mean=opp,
                        opp_factor=(of[idx] if of is not None else None),
                        injury=[status_map.get(x, "ACTIVE") for x in des[idx]], rungs=s["rungs"])
            y = pf[s["y"]].to_numpy(float)[idx]
            crps = dist.crps(y)
            st = np.array([r["status"] for r in res])
            fam_mean = crps.mean()
            row = {"n": len(res), "summary": gate.summarize(res)}
            row["error_by_status"] = {k: {"n": int((st == k).sum()), "mae": float(np.abs(pub - y)[st == k].mean()),
                                          "crps": float(crps[st == k].mean()), "rel_crps": float(crps[st == k].mean() / fam_mean),
                                          "cover_80": float(np.mean([(lo <= yy <= hi) for lo, hi, yy in zip(
                                              dist.subset(st == k).interval(0.8)[0], dist.subset(st == k).interval(0.8)[1], y[st == k])]))}
                                      for k in ("PASS", "REVIEW", "BLOCK") if (st == k).sum() > 0}
            # by check (any finding of that check)
            checks = {}
            for c in sorted({f["check"] for r in res for f in r["findings"]}):
                hit = np.array([any(f["check"] == c for f in r["findings"]) for r in res])
                checks[c] = {"n": int(hit.sum()), "rel_crps": float(crps[hit].mean() / fam_mean),
                             "rel_crps_others": float(crps[~hit].mean() / fam_mean) if (~hit).any() else None}
            row["error_by_check"] = checks
            out["by_family"].setdefault(fam, {})[split] = row
            pooled.append(pd.DataFrame({"fam": fam, "split": split, "status": st, "rel": crps / fam_mean}))
    pdf = pd.concat(pooled)
    for split in splits:
        d = pdf[pdf.split == split]
        out["pooled"][split] = {k: {"n": int((d.status == k).sum()), "share": float((d.status == k).mean()),
                                    "rel_crps": float(d.rel[d.status == k].mean())} for k in ("PASS", "REVIEW", "BLOCK")
                                if (d.status == k).any()}
    out["team_reconciliation"] = reconcile(S, frozen, corr, splits)
    return out


def reconcile(S, frozen, corr, splits):
    pf, tf = S["pf"], S["tf"]
    out = {}
    played = pf.y_observed.to_numpy()
    tg_rate = (tf.tm_targets / tf.tm_attempts)[tf.season.between(*L.DEV)].mean()
    for split in splits:
        m = (pf.split == split).to_numpy() & played
        d = pf.loc[m, ["game_id", "team"]].copy()
        # population-aware: the frozen model inside its training population, B (EWMA, shrunk) for everyone else.
        # The naive version (frozen model for every participant) is kept to document the extrapolation defect.
        tin = S["pops"]["REC"][m]
        cin = S["pops"]["RUSH"][m]
        tf_ = model_mean(S, corr, "targets", frozen["targets"]["model"], split)[m]
        cf_ = model_mean(S, corr, "carries", frozen["carries"]["model"], split)[m]
        d["tgt"] = np.where(tin, tf_, S["preds"]["targets"]["B"].to_numpy()[m])
        d["car"] = np.where(cin, cf_, S["preds"]["carries"]["B"].to_numpy()[m])
        d["tgt_naive"] = tf_
        d["car_naive"] = cf_
        d["tgt_act"] = pf.targets.to_numpy()[m]
        d["car_act"] = pf.carries.to_numpy()[m]
        ps = d.groupby(["game_id", "team"]).sum(numeric_only=True).reset_index()
        tm = tf[["game_id", "team", "split", "tm_targets", "tm_carries"]].copy()
        tm["team_tgt"] = model_mean(S, corr, "team_pass_attempts", frozen["team_pass_attempts"]["model"], split) * tg_rate
        tm["team_car"] = model_mean(S, corr, "team_rush_attempts", frozen["team_rush_attempts"]["model"], split)
        j = ps.merge(tm, on=["game_id", "team"], how="inner")
        res_t = G.team_recon(j.tgt, j.team_tgt, "targets vs team pass attempts")
        res_c = G.team_recon(j.car, j.team_car, "carries vs team rush attempts")
        out[split] = {
            "n_team_games": int(len(j)),
            "targets": {"status": pd.Series([r["status"] for r in res_t]).value_counts().to_dict(),
                        "mean_ratio_proj": float((j.tgt / j.team_tgt).mean()), "mean_ratio_actual": float((j.tgt_act / j.tm_targets).mean())},
            "carries": {"status": pd.Series([r["status"] for r in res_c]).value_counts().to_dict(),
                        "mean_ratio_proj": float((j.car / j.team_car).mean()), "mean_ratio_actual": float((j.car_act / j.tm_carries).mean())},
            "naive_frozen_model_for_all_participants": {
                "targets_ratio": float((j.tgt_naive / j.team_tgt).mean()), "carries_ratio": float((j.car_naive / j.team_car).mean()),
                "targets_status": pd.Series([r["status"] for r in G.team_recon(j.tgt_naive, j.team_tgt, "t")]).value_counts().to_dict(),
                "carries_status": pd.Series([r["status"] for r in G.team_recon(j.car_naive, j.team_car, "c")]).value_counts().to_dict()},
            "note": "player sums are over players who PLAYED (conditional projections), so the projected ratio is expected to sit "
                    "near the realised ratio (QB/RB/WR/TE only, fullbacks excluded), not exactly at 1.",
        }
    return out
