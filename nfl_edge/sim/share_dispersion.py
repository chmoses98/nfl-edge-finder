"""S1 -- concentration-conditioned opportunity dispersion. RESEARCH_ONLY.

Preregistered in research/game_script_v2/wave2/PREREGISTRATION.md, section 2.

The incumbent draws a team-game's carries / targets from a Dirichlet-multinomial whose single concentration alpha
was fitted by moments on REALISED shares, `Var(share) = p(1-p)/(alpha+1)`. A realised share already contains the
multinomial noise of the team's N opportunities, so the simulator's multinomial layer counts it a second time
(predictive variance inflated by (N+alpha)/N). S1 fits alpha by the Dirichlet-multinomial LIKELIHOOD of the realised
COUNT vectors instead, and lets it depend on pregame features of the team-game's expected-share structure.

Only the concentration changes: the Dirichlet mean is the expected share vector, so expected shares, team totals,
the OTHER bucket and per-row availability are untouched, and the simulator consumes exactly the same random draws.

  S1-0  log alpha = b0                       (N-corrected constant)
  S1-1  log alpha = b0 + b . z(features)     (ridge 1.0 on b; features below, standardised on the fit rows)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import digamma, gammaln

S1_VERSION = "sim-s1-1.0.0"
FEATURES = ("hhi", "top1", "top2", "n_meaningful", "other_share", "entropy", "share_no_history", "starter_unavailable",
            "role_instability")
RIDGE = 1.0
FAMILY_POSITIONS = {"carry": ("RB",), "target": ("WR", "TE")}
SHARE_COLS = {"carry": ("sh_carry_s", "sh_carry_l"), "target": ("sh_target_s", "sh_target_l")}


def expected_shares(p_raw: np.ndarray, other: float) -> np.ndarray:
    """The simulator's share vector (simulate._simulate_players): players renormalised to 1 - other, OTHER appended,
    then floored at zero the way the Dirichlet parameters max(alpha p, 1e-6) effectively treat a negative OTHER."""
    p = np.clip(np.asarray(p_raw, float), 0.0, None)
    pc = np.append(p / max(p.sum(), 1e-9) * (1 - other), other)
    pc = np.clip(pc, 0.0, None)
    return pc / pc.sum()


def team_features(P: pd.DataFrame, pc: np.ndarray, kind: str) -> dict:
    """Pregame features of one team-game. ``P`` = eligible players (incumbent feature columns), ``pc`` = their
    expected shares with OTHER last."""
    p = np.asarray(pc[:-1], float)
    srt = np.sort(p)[::-1]
    pos = P["position"].astype(str).to_numpy()
    rank = P["dc_rank"].astype(float).to_numpy()
    fam = np.isin(pos, FAMILY_POSITIONS[kind])
    has_chart = np.isfinite(rank[fam]).any() if fam.any() else False
    s_col, l_col = SHARE_COLS[kind]
    top = np.argsort(-p)[:3]
    ss = P[s_col].astype(float).to_numpy()[top]; ll = P[l_col].astype(float).to_numpy()[top]
    ok = np.isfinite(ss) & np.isfinite(ll)
    nz = p[p > 0]
    return {"hhi": float((p ** 2).sum()), "top1": float(srt[0]) if len(srt) else 0.0, "top2": float(srt[:2].sum()),
            "n_meaningful": float((p >= 0.05).sum()), "other_share": float(pc[-1]),
            "entropy": float(-(nz * np.log(nz)).sum()),
            "share_no_history": float(p[(P["n_prior"].fillna(0).to_numpy() == 0)].sum()),
            "starter_unavailable": float(bool(has_chart) and not ((rank[fam] == 1).any())),
            "role_instability": float(np.abs(ss[ok] - ll[ok]).mean()) if ok.any() else 0.0}


# -------------------------------------------------------------------------------------- likelihood
def dm_loglik(counts: list, shares: list, alpha: np.ndarray) -> np.ndarray:
    """Per team-game Dirichlet-multinomial log likelihood (up to the multinomial coefficient)."""
    out = np.empty(len(counts))
    for g, (c, p) in enumerate(zip(counts, shares)):
        a = alpha[g]; ap = np.maximum(a * p, 1e-6); N = c.sum()
        out[g] = gammaln(a) - gammaln(N + a) + (gammaln(c + ap) - gammaln(ap)).sum()
    return out


def _dll_dalpha(counts, shares, alpha):
    out = np.empty(len(counts))
    for g, (c, p) in enumerate(zip(counts, shares)):
        a = alpha[g]; ap = np.maximum(a * p, 1e-6); N = c.sum()
        out[g] = digamma(a) - digamma(N + a) + (p * (digamma(c + ap) - digamma(ap))).sum()
    return out


def fit(counts: list, shares: list, X: np.ndarray | None, ridge: float = RIDGE) -> dict:
    """Maximum likelihood for log alpha = b0 (+ b . z(X)); returns the artifact the simulator reads."""
    if X is None:
        Z = np.zeros((len(counts), 0)); mu = np.zeros(0); sd = np.ones(0)
    else:
        X = np.asarray(X, float); mu = np.nanmean(X, axis=0); sd = np.nanstd(X, axis=0); sd[sd == 0] = 1.0
        Z = (np.where(np.isfinite(X), X, mu) - mu) / sd
    k = Z.shape[1]

    def nll(th):
        a = np.exp(np.clip(th[0] + Z @ th[1:], -5, 9))
        ll = dm_loglik(counts, shares, a)
        g = _dll_dalpha(counts, shares, a) * a
        grad = -np.concatenate([[g.sum()], Z.T @ g]) + np.concatenate([[0.0], ridge * th[1:]])
        return -ll.sum() + 0.5 * ridge * (th[1:] ** 2).sum(), grad

    r = minimize(nll, np.r_[np.log(10.0), np.zeros(k)], jac=True, method="L-BFGS-B")
    return {"version": S1_VERSION, "form": "S1-0" if k == 0 else "S1-1", "b0": float(r.x[0]), "beta": r.x[1:].tolist(),
            "mu": mu.tolist(), "sd": sd.tolist(), "features": [] if k == 0 else list(FEATURES), "ridge": ridge,
            "converged": bool(r.success), "n_team_games": int(len(counts))}


def alpha_of(model: dict, feats: dict | None) -> float:
    """The concentration for one team-game (what the simulator calls)."""
    if not model.get("features"):
        return float(np.exp(model["b0"]))
    x = np.array([feats[f] for f in model["features"]], float)
    z = (x - np.asarray(model["mu"])) / np.asarray(model["sd"])
    return float(np.exp(np.clip(model["b0"] + z @ np.asarray(model["beta"]), -5, 9)))


# -------------------------------------------------------------------------------------- data
def team_game_units(elig: pd.DataFrame, share_model: dict, other: float, kind: str):
    """Per team-game: realised count vector (eligible players + OTHER), the simulator's expected shares under
    ``share_model`` (an incumbent `fit_share_model` artifact), and the pregame features."""
    from . import models as M
    cnt_col = "designed_carries" if kind == "carry" else "targets"
    tot_col = "team_designed_rush" if kind == "carry" else "team_targets"
    X = M.share_design(elig, kind, share_model["priors"])
    pr = np.clip(M.ridge_predict(share_model["ridge"], X), 0.0, None)
    e = elig.assign(_p=pr)
    counts, shares, feats, keys = [], [], [], []
    for (gid, team), g in e.groupby(["game_id", "team"], sort=True):
        tot = float(g[tot_col].iloc[0])
        if not np.isfinite(tot) or tot <= 0:
            continue
        c = g[cnt_col].fillna(0).to_numpy(float)
        oc = max(tot - c.sum(), 0.0)
        pc = expected_shares(g["_p"].to_numpy(), other)
        counts.append(np.append(c, oc)); shares.append(pc)
        feats.append(team_features(g, pc, kind)); keys.append((gid, team))
    F = pd.DataFrame(feats)[list(FEATURES)].to_numpy(float) if feats else np.zeros((0, len(FEATURES)))
    return counts, shares, F, keys


def fit_for_bundle(elig_train: pd.DataFrame, other: float, kind: str, form: str = "S1-1") -> dict:
    """The selected form fitted on a bundle's training seasons, with expected shares CROSS-FITTED by season (each
    season's shares from a share ridge fitted on the other training seasons)."""
    from . import models as M
    col = "y_share_carry" if kind == "carry" else "y_share_target"
    seasons = sorted(int(s) for s in elig_train["season"].unique())
    if len(seasons) < 2:
        raise ValueError("S1 cross-fitting needs at least two training seasons")
    cnt, shr, F = [], [], []
    for s in seasons:
        tr = elig_train[(elig_train["season"] != s) & elig_train[col].notna()].rename(columns={col: "y_share"})
        sm = M.fit_share_model(tr, kind)
        c, p, f, _ = team_game_units(elig_train[elig_train["season"] == s], sm, other, kind)
        cnt += c; shr += p; F.append(f)
    out = fit(cnt, shr, np.vstack(F) if form == "S1-1" else None)
    out["train_seasons"] = seasons
    return out
