"""Post-freeze candidate corrections: fitted on development, evaluated on validation, NOT adopted into the frozen selection
(the 2024-25 holdout had already been scored when these defects were diagnosed). They are pre-registered for prospective
evaluation on the next untouched data (2026 weeks >= 5 accuracy, then 2027).

C1 new-team tenure: mu x exp(theta_k) for the player's k-th game with his current team (k = 0, 1, 2-3), theta fitted on dev.
C2 backup-tier regression: mu x exp(theta_tier) for RB2+/TE2+/WR3+ (within-team rank of PIT target share), theta on dev.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pf_core import metrics

from . import diagnostics as DG
from . import evaluate as EV
from . import gate_eval as GE
from . import ladder as L
from . import pipeline as P


def tenure(pf: pd.DataFrame) -> np.ndarray:
    d = pf[["player_id", "team", "kickoff_utc"]].copy()
    d = d.sort_values(["player_id", "kickoff_utc"])
    # games with the current team before this one (spells: a return to a former team restarts the count)
    spell = (d.team != d.groupby("player_id").team.shift(1)).cumsum()
    d["k"] = d.groupby(spell).cumcount()
    return d.k.reindex(pf.index).to_numpy()


def run(S, frozen, corr) -> dict:
    pf = S["pf"]
    k = tenure(pf)
    tier, _ = DG._tiers(pf)
    first_season_game = pf.games_in_season_before.to_numpy() == 0
    out = {"tenure_bias": {}, "C1": {}, "C2": {}}
    dev = (pf.split == "development").to_numpy() & pf.y_observed.to_numpy()
    val = (pf.split == "validation").to_numpy() & pf.y_observed.to_numpy()
    kb = np.select([k == 0, k == 1, k <= 3, k <= 8], ["0", "1", "2-3", "4-8"], "9+")
    for fam in ("targets", "receptions", "receiving_yards", "carries", "rushing_yards", "anytime_td"):
        s = P.PLAYER_FAMILIES[fam]
        pop = S["pops"][s["pop"]]
        mu = GE.model_mean(S, corr, fam, frozen[fam]["model"], "validation")
        y = pf[s["y"]].to_numpy(float)
        rows = []
        for b in ("0", "1", "2-3", "4-8", "9+"):
            for nm, msk in (("dev", dev), ("val", val)):
                m = pop & msk & (kb == b) & ~(first_season_game & (b == "0") & (pf.team_changed.to_numpy() == 0))
                if m.sum() >= 30:
                    rows.append({"games_with_team": b, "split": nm, "n": int(m.sum()), "mean_pred": float(mu[m].mean()),
                                 "mean_actual": float(y[m].mean()), "rel_bias": float(mu[m].mean() / y[m].mean() - 1)})
        out["tenure_bias"][fam] = rows
        link = "bernoulli" if fam == "anytime_td" else "poisson"
        base = -np.log(1 - np.clip(mu, 1e-4, 0.999)) if fam == "anytime_td" else mu
        for cname, X in (("C1", np.column_stack([(kb == "0"), (kb == "1"), (kb == "2-3")]).astype(float)),
                         ("C2", np.column_stack([np.isin(tier, ["RB2+", "TE2+"]), tier == "WR3+"]).astype(float))):
            beta = L.fit_loglinear(np.clip(y, 0, None), base, X, dev & pop, link=link)
            adj = L.apply_loglinear(base, X, beta)
            new = 1 - np.exp(-adj) if fam == "anytime_td" else adj
            m = val & pop & np.isfinite(mu)
            prm = frozen[fam]["dist_params"]
            d0, d1 = EV.make(prm, mu[m]), EV.make(prm, new[m])
            r = EV.diff(d1.crps(y[m]), d0.crps(y[m]), pf.game_id.to_numpy()[m])
            seg = m & (X.sum(axis=1) > 0)
            rs = EV.diff(EV.make(prm, new[seg]).crps(y[seg]), EV.make(prm, mu[seg]).crps(y[seg]), pf.game_id.to_numpy()[seg]) if seg.sum() > 50 else None
            out[cname][fam] = {"beta_dev": beta.tolist(), "val_crps_diff_all": r, "val_crps_diff_segment": rs, "n_segment_val": int(seg.sum())}
    return out
