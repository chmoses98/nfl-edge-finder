"""Root-cause analysis and targeted corrections (development-fitted, validated chronologically).

corrections(S)  builds candidate corrected predictions that the selection stage evaluates like any other model:
  D_vac / F_vac  teammate availability: a player's share is renormalised for the opportunity vacated by teammates
                 listed OUT/DOUBTFUL on the final injury report: share x (1 - vacated)^(-gamma), gamma fitted on
                 development (gamma = 1 is proportional redistribution, 0 = ignore). Propagated to receptions, yards, TDs.
run_all(S, frozen)  segment error tables (role tier, RB committee, early season, rookies, team change, QB change,
                 injury designation, vacated volume), targets-bias anatomy, tails.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pf_core import metrics

from . import data as D
from . import evaluate as EV
from . import features as F
from . import ladder as L
from . import pipeline as P

_CACHE = {}


def _vacated(S):
    if "vac" in _CACHE:
        return _CACHE["vac"]
    pf = S["pf"]
    inj = D.injuries()
    v = F.teammate_availability(pf[pf.y_observed], inj)
    m = pf[["team", "block"]].merge(v, on=["team", "block"], how="left").fillna(0)
    inj2 = inj.rename(columns={"gsis_id": "player_id"})[["season", "week", "player_id", "report_status"]]
    des = pf[["season", "week", "player_id"]].merge(inj2, on=["season", "week", "player_id"], how="left").report_status
    out = {"vac": m, "designation": des.fillna("None").replace({"Note": "None"}).to_numpy(), "inj": inj}
    _CACHE["vac"] = out
    return out


def corrections(S) -> dict:
    pf, preds = S["pf"], S["preds"]
    V = _vacated(S)
    vac = V["vac"]
    dev = pf.season.between(*L.DEV).to_numpy() & pf.y_observed.to_numpy()
    pops = S["pops"]
    xt = -np.log(1 - vac.vac_tpa_inj.clip(0, 0.6).to_numpy())
    xc = -np.log(1 - vac.vac_cs_inj.clip(0, 0.6).to_numpy())
    xt_or = -np.log(1 - vac.vac_tpa_oracle.clip(0, 0.6).to_numpy())
    xc_or = -np.log(1 - vac.vac_cs_oracle.clip(0, 0.6).to_numpy())
    out, summ = {}, {}
    gam = {}
    for base in ("D", "F"):
        for fam, x, pop, xo in (("targets", xt, "REC", xt_or), ("carries", xc, "RUSH", xc_or)):
            y = pf[P.PLAYER_FAMILIES[fam]["y"]].to_numpy(float)
            mu = preds[fam][base].to_numpy(float)
            g = float(L.fit_loglinear(y, mu, x[:, None], dev & pops[pop])[0])
            go = float(L.fit_loglinear(y, mu, xo[:, None], dev & pops[pop])[0])
            gam[(base, fam)] = g
            summ[f"gamma_{base}_{fam}"] = g
            summ[f"gamma_oracle_{base}_{fam}"] = go
            out.setdefault(fam, {})[f"{base}_vac"] = pd.Series(mu * np.exp(g * x), index=pf.index)
            out[fam][f"{base}_oracle_avail"] = pd.Series(mu * np.exp(go * xo), index=pf.index)
        ft = np.exp(gam[(base, "targets")] * xt)
        fc = np.exp(gam[(base, "carries")] * xc)
        for fam in ("receptions", "receiving_yards"):
            out.setdefault(fam, {})[f"{base}_vac"] = preds[fam][base] * ft
        out.setdefault("rushing_yards", {})[f"{base}_vac"] = preds["rushing_yards"][base] * fc
        # anytime TD: scale the intensity by the touch-weighted factor
        p = preds["anytime_td"][base].clip(1e-4, 0.999).to_numpy()
        lam = -np.log(1 - p)
        tshare = (pf.targets_ewm8 / (pf.targets_ewm8 + pf.carries_ewm8)).fillna(0.5).to_numpy()
        fac = tshare * ft + (1 - tshare) * fc
        out.setdefault("anytime_td", {})[f"{base}_vac"] = pd.Series(1 - np.exp(-lam * fac), index=pf.index).clip(0.001, 0.999)
    summ["share_player_games_with_vacated_targets>0.05"] = float((vac.vac_tpa_inj > 0.05).mean())
    summ["share_player_games_with_vacated_carries>0.10"] = float((vac.vac_cs_inj > 0.10).mean())
    return {"preds": out, "summary": summ}


def _tiers(pf):
    t = pf[["game_id", "team", "position"]].copy()
    t["tpa"] = pf.tgt_per_att_ewm4.fillna(0)
    t["rank"] = t.groupby(["game_id", "team", "position"]).tpa.rank(ascending=False, method="first")
    tier = np.where(t.position == "WR", "WR" + t["rank"].clip(upper=3).astype(int).astype(str),
                    np.where(t.position == "TE", np.where(t["rank"] == 1, "TE1", "TE2+"),
                             np.where(t.position == "RB", np.where(t["rank"] == 1, "RB1", "RB2+"), "QB")))
    tier = pd.Series(tier).str.replace("WR3", "WR3+")
    cs = pf.carry_share_ewm4.fillna(0)
    rb = np.where(pf.position != "RB", "n/a", np.where(cs >= 0.6, "workhorse(cs>=.6)", np.where(cs >= 0.35, "committee(.35-.6)", "change-of-pace(<.35)")))
    return tier.to_numpy(), rb


def run_all(S, frozen) -> dict:
    pf, preds = S["pf"], S["preds"]
    V = _vacated(S)
    tier, rb = _tiers(pf)
    # QB change: the team's starter differs from its previous game's starter (pregame-known: starters are announced)
    tq = pf[["team", "block", "qb_id"]].drop_duplicates(["team", "block"]).sort_values(["team", "block"])
    tq["qb_changed"] = (tq.groupby("team").qb_id.shift(1) != tq.qb_id) & tq.groupby("team").qb_id.shift(1).notna()
    qbc = pf[["team", "block"]].merge(tq[["team", "block", "qb_changed"]], on=["team", "block"], how="left").qb_changed.fillna(False).to_numpy()
    seg = pd.DataFrame({
        "tier": tier, "rb_role": rb,
        "season_phase": np.where(pf.week <= 3, "wk1-3", np.where(pf.week <= 9, "wk4-9", "wk10-18")),
        "rookie": np.where(pf.is_rookie == 1, "rookie", "veteran"),
        "career_games": pd.cut(pf.career_games, [-1, 3, 8, 16, 1000], labels=["<=3", "4-8", "9-16", "17+"]).astype(str),
        "team_changed": np.where(pf.team_changed == 1, "new team (1st game)", "same team"),
        "qb_changed": np.where(qbc, "QB changed", "same QB"),
        "designation": V["designation"],
        "vacated_targets": pd.cut(V["vac"].vac_tpa_inj, [-1, 0.0001, 0.1, 0.25, 9], labels=["0", "0-0.10", "0.10-0.25", ">0.25"]).astype(str),
        "spread_bucket": pd.cut(pf.spread_team, [-40, -7, -3, 3, 7, 40], labels=["dog 7+", "dog 3-7", "pk +-3", "fav 3-7", "fav 7+"]).astype(str),
    }, index=pf.index)
    out = {"segments": {}, "targets_bias": {}, "tails": {}}
    for fam, fz in frozen.items():
        if fam not in P.PLAYER_FAMILIES:
            continue
        s = P.PLAYER_FAMILIES[fam]
        m = fz["model"]
        col = m if m in preds[fam].columns else None
        mu = preds[fam][col] if col else S.get("_corr", {}).get(fam, {}).get(m)
        if mu is None:
            from . import diagnostics as _d  # corrected model: rebuild
            mu = corrections(S)["preds"][fam][m]
        df = seg.copy()
        df["y"] = pf[s["y"]].to_numpy(float)
        df["mu"] = np.asarray(mu, float)
        df["B"] = preds[fam]["B"].to_numpy(float)
        msk = S["pops"][s["pop"]] & pf.split.isin(["development", "validation"]).to_numpy()
        d = df[msk]
        out["segments"][fam] = {c: metrics.segment_table(d, c, "y", "mu", min_n=100) for c in seg.columns}
    # targets bias anatomy (mean_defect follow-up): realised / projected by week bucket and usage tier, dev only
    for fam in ("targets", "receptions"):
        s = P.PLAYER_FAMILIES[fam]
        m = frozen[fam]["model"]
        mu = preds[fam][m] if m in preds[fam].columns else corrections(S)["preds"][fam][m]
        d = pd.DataFrame({"y": pf[s["y"]], "mu": mu, "week": pf.week, "split": pf.split, "ewm": pf.targets_ewm4,
                          "pos": pf.position})
        d = d[S["pops"][s["pop"]] & pf.y_observed.to_numpy()]
        rows = []
        for sp in ("development", "validation", "check2026"):
            for wk, wm in (("wk1-6", d.week <= 6), ("wk7+", d.week >= 7)):
                for ut, um in (("ewm<3", d.ewm < 3), ("ewm3-6", d.ewm.between(3, 6)), ("ewm6+", d.ewm > 6)):
                    g = d[(d.split == sp) & wm & um]
                    if len(g) >= 50:
                        rows.append({"split": sp, "weeks": wk, "usage": ut, "n": int(len(g)), "mean_pred": float(g.mu.mean()),
                                     "mean_actual": float(g.y.mean()), "realised_over_pred": float(g.y.mean() / g.mu.mean())})
        out["targets_bias"][fam] = rows
    return out
