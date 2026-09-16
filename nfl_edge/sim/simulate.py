"""The Monte Carlo game engine.

``simulate(game, bundle, n)`` draws ``n`` games on a common set of rows.  Row ``r`` of every output array
is the SAME simulated game, which is what makes the outputs coherent:

  (margin, total) ---> home/away points ---> touchdowns given points ---> pass/rush TD split
        |
        +--> team plays and pass rate, conditional on that row's margin and total (game script)
                  |
                  +--> dropbacks, sacks, scrambles, pass attempts, targets, designed rushes
                            |
                            +--> Dirichlet-multinomial allocation of carries and targets over the players
                                 who are available on that row (questionable players sit out on the rows
                                 where their availability draw says so, and the others absorb the share)
                                        |
                                        +--> per-touch outcomes from the empirical banks at the player's
                                             expected efficiency (opponent-adjusted), summed per player
                                                   |
                                                   +--> touchdown allocation inside the team's TD count

Invariants (checked by ``coherence_report``): sum of player carries == team rush attempts; sum of targets
== team targets; QB passing yards == sum of receiving yards; completions == receptions; TDs reconcile with
the team count; every count is a non-negative integer; ladders are monotone by construction.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from . import models as M
from nfl_edge.pricing.game_env import ResidualBank, simulate_game
from nfl_edge.settlement.availability import STATE_PLAY_RATES

ENGINE_VERSION = "sim-engine-1.0.0"


@dataclass
class TeamInput:
    team: str
    home: bool
    features: dict                      # the prior-only team feature row (off_*, def_* of THIS team)
    opp_features: dict                  # the opponent's row (its def_* are what this offence faces)
    players: pd.DataFrame               # eligible players with feature columns (see training.assemble)
    qb1: str | None = None


@dataclass
class GameInput:
    game_id: str
    season: int
    week: int
    home: TeamInput
    away: TeamInput
    spread_home: float                  # centre: expected home margin (home - away)
    total_line: float                   # centre: expected total
    center_source: str = "unspecified"


@dataclass
class SimResult:
    game_id: str
    n: int
    margin: np.ndarray
    total: np.ndarray
    home_points: np.ndarray
    away_points: np.ndarray
    team: dict = field(default_factory=dict)     # team -> {stat: array}
    player: dict = field(default_factory=dict)   # player_id -> {stat: array}
    meta: dict = field(default_factory=dict)


# ------------------------------------------------------------------------------------- helpers
def _interp_quantiles(q: np.ndarray, u: np.ndarray) -> np.ndarray:
    """Inverse-CDF sampling from 201 stored quantiles."""
    return np.interp(u * 200.0, np.arange(201), q)


def _multinomial_rows(rng, n_total: np.ndarray, w: np.ndarray) -> np.ndarray:
    """Row-wise multinomial: n_total (N,) trials with probabilities w (N, m) -> counts (N, m)."""
    N, m = w.shape
    out = np.zeros((N, m), dtype=np.int64)
    remaining = n_total.astype(np.int64).copy()
    wrem = w.sum(axis=1)
    for j in range(m):
        p = np.where(wrem > 1e-12, w[:, j] / np.maximum(wrem, 1e-12), 0.0)
        p = np.clip(p, 0.0, 1.0)
        c = rng.binomial(remaining, p)
        out[:, j] = c
        remaining -= c
        wrem = wrem - w[:, j]
    # numerical leftovers go to the largest-weight player
    if remaining.any():
        j = np.argmax(w, axis=1)
        out[np.arange(N), j] += remaining
    return out


def _dirichlet_multinomial(rng, n_total: np.ndarray, p: np.ndarray, alpha: float, active: np.ndarray) -> np.ndarray:
    """Counts (N, m) from a Dirichlet-multinomial with mean shares p (m,) and concentration alpha, where
    ``active`` (N, m) zeroes a player's share on the rows he does not play."""
    N = len(n_total)
    a = np.maximum(alpha * p, 1e-6)
    G = rng.gamma(a, 1.0, size=(N, len(p))) * active
    S = G.sum(axis=1, keepdims=True)
    W = np.where(S > 0, G / np.maximum(S, 1e-12), 0.0)
    return _multinomial_rows(rng, n_total, W)


def _sum_draws(rng, counts: np.ndarray, sampler, max_cap: int = 60) -> np.ndarray:
    """Sum of ``counts[r]`` iid draws per row r using a (N, C) uniform grid; ``sampler(u)`` maps uniforms to
    outcomes.  Rows with more than ``max_cap`` touches use the mean of the excess (they are extremely rare)."""
    N = len(counts)
    C = int(min(max_cap, counts.max())) if N else 0
    if C == 0:
        return np.zeros(N)
    U = rng.random((N, C))
    Y = sampler(U)
    mask = np.arange(C)[None, :] < counts[:, None]
    out = (Y * mask).sum(axis=1)
    over = counts - C
    if (over > 0).any():
        out += over.clip(min=0) * Y.mean(axis=1)
    return out


# ------------------------------------------------------------------------------- team volume
def _team_env_rows(ti: TeamInput, margin_team: np.ndarray, total: np.ndarray) -> np.ndarray:
    f = ti.features; o = ti.opp_features
    cols = {"off_plays": f["off_plays"], "def_plays": o["def_plays"], "off_sec_per_play": f["off_sec_per_play"],
            "def_sec_per_play": o["def_sec_per_play"], "off_neutral_pass_rate": f["off_neutral_pass_rate"],
            "off_pass_rate": f["off_pass_rate"], "off_proe": f["off_proe"], "def_pass_rate": o["def_pass_rate"],
            "def_neutral_pass_rate": o["def_neutral_pass_rate"], "home": float(ti.home)}
    N = len(margin_team)
    X = {k: np.full(N, float(v)) for k, v in cols.items()}
    X["game_total"] = total.astype(float); X["team_margin"] = margin_team.astype(float)
    X["abs_margin"] = np.abs(margin_team).astype(float); X["team_margin_sq"] = margin_team.astype(float) ** 2
    return X


def _design(X: dict, feats: list[str]) -> np.ndarray:
    return np.column_stack([X[c] for c in feats])


# ----------------------------------------------------------------------------------- the engine
def simulate(g: GameInput, bundle: dict, n: int = 20000, seed: int = 11, bank: ResidualBank | None = None,
             game_draws: dict | None = None) -> SimResult:
    rng = np.random.default_rng(seed)
    ge = bundle["game_env"]
    # 1. score
    if game_draws is None:
        if bank is None:
            raise ValueError("a ResidualBank or precomputed game_draws is required")
        gs = simulate_game(g.spread_home, g.total_line, bank, n=n)
    else:
        gs = game_draws
    margin = gs["margin"]; total = gs["total"]; hp = gs["home"]; ap = gs["away"]
    n = len(margin)
    res = SimResult(g.game_id, n, margin, total, hp, ap, meta={"engine_version": ENGINE_VERSION, "seed": seed,
                                                                 "center": {"spread_home": g.spread_home, "total_line": g.total_line,
                                                                            "source": g.center_source}})
    # 2. team volume, jointly for the two teams (residual correlation on plays and pass rate)
    sides = ((g.home, margin, hp), (g.away, -margin, ap))
    Xs = [_team_env_rows(ti, mt, total) for ti, mt, _ in sides]
    mu_plays = [M.ridge_predict(ge["plays"], _design(X, M.PLAYS_FEATURES)) for X in Xs]
    mu_pr = [M.ridge_predict(ge["pass_rate"], _design(X, M.PASS_RATE_FEATURES)) for X in Xs]
    z = rng.standard_normal((n, 2)); rho = ge["rho_plays"]
    e_plays = np.column_stack([z[:, 0], rho * z[:, 0] + np.sqrt(1 - rho ** 2) * z[:, 1]]) * ge["plays"]["resid_sd"]
    z = rng.standard_normal((n, 2)); rho = ge["rho_pass_rate"]
    e_pr = np.column_stack([z[:, 0], rho * z[:, 0] + np.sqrt(1 - rho ** 2) * z[:, 1]]) * ge["pass_rate"]["resid_sd"]
    team_out = {}
    for i, (ti, mt, pts) in enumerate(sides):
        plays = np.round(np.clip(mu_plays[i] + e_plays[:, i], 35, 100)).astype(np.int64)
        pass_rate = np.clip(mu_pr[i] + e_pr[:, i], 0.2, 0.9)
        dropbacks = np.round(plays * pass_rate).astype(np.int64)
        f, o = ti.features, ti.opp_features
        p_sack = float(np.clip(f["off_sack_rate"] + o["def_sack_rate"] - ge["league"]["sack_rate"], 0.01, 0.2))
        sacks = rng.binomial(dropbacks, p_sack)
        qb_scr = None
        if ti.qb1 is not None and ti.qb1 in set(ti.players["player_id"]):
            row = ti.players[ti.players["player_id"] == ti.qb1].iloc[0]
            qb_scr = float(row.get("rt_scramble_rate", np.nan))
        p_scr = float(np.clip(qb_scr if qb_scr is not None and np.isfinite(qb_scr) else f["off_scramble_rate"], 0.005, 0.25))
        scrambles = rng.binomial(np.maximum(dropbacks - sacks, 0), p_scr)
        pass_att = np.maximum(dropbacks - sacks - scrambles, 0)
        targets = rng.binomial(pass_att, float(np.clip(f["off_target_rate"], 0.85, 0.995)))
        kneel_rate = np.where(mt > 0, ge["league"]["kneels_leading"], ge["league"]["kneels_trailing"])
        kneels = np.minimum(rng.poisson(kneel_rate), np.maximum(plays - dropbacks, 0))
        designed = np.maximum(plays - dropbacks - kneels, 0)
        rush_att = designed + kneels + scrambles
        # touchdowns given points, then the pass/rush split
        tbl = np.asarray(ge["td_given_points"]); pidx = np.clip(pts.astype(int), 0, 79)
        cum = np.cumsum(tbl[pidx], axis=1); u = rng.random(n)
        off_td = (u[:, None] > cum).sum(axis=1).astype(np.int64)
        Xt = np.column_stack([np.full(n, f["off_pass_td_share"]), np.full(n, o["def_pass_td_share"]), pass_rate, mt.astype(float)])
        p_pass_td = M.logistic_predict(ge["pass_td_share"], Xt)
        pass_td = rng.binomial(off_td, np.clip(p_pass_td, 0.02, 0.98))
        rush_td = off_td - pass_td
        team_out[ti.team] = {"points": pts, "plays": plays, "pass_rate": pass_rate, "dropbacks": dropbacks, "sacks": sacks,
                             "scrambles": scrambles, "pass_att": pass_att, "targets": targets, "kneels": kneels,
                             "designed_rush": designed, "rush_att": rush_att, "off_td": off_td, "pass_td": pass_td,
                             "rush_td": rush_td, "margin": mt}
    res.team = team_out
    # 3. players
    for ti, mt, pts in sides:
        _simulate_players(rng, ti, team_out[ti.team], bundle, res, mt, total)
    return res


def _play_prob(state: str) -> float:
    rates = STATE_PLAY_RATES.get(state)
    return float(rates[0]) if rates else 0.9


def _simulate_players(rng, ti: TeamInput, T: dict, bundle: dict, res: SimResult, margin_team: np.ndarray, total: np.ndarray):
    P = ti.players.reset_index(drop=True)
    n = len(margin_team); m = len(P)
    if m == 0:
        return
    # availability per row
    p_play = np.array([_play_prob(s) for s in P["avail_state"]])
    active = rng.random((n, m)) < p_play[None, :]
    # expected shares
    cs, ts = bundle["carry_share"], bundle["target_share"]
    Xc = M.share_design(P, "carry", cs["priors"]); Xt = M.share_design(P, "target", ts["priors"])
    p_carry = np.clip(M.ridge_predict(cs["ridge"], Xc), 0.0, None)
    p_target = np.clip(M.ridge_predict(ts["ridge"], Xt), 0.0, None)
    other_c, other_t = bundle["other_share"]["carry"], bundle["other_share"]["target"]
    # append an OTHER pseudo-player absorbing the share that historically went outside the eligible set
    pc = np.append(p_carry / max(p_carry.sum(), 1e-9) * (1 - other_c), other_c)
    pt = np.append(p_target / max(p_target.sum(), 1e-9) * (1 - other_t), other_t)
    act = np.column_stack([active, np.ones(n, dtype=bool)])
    carries = _dirichlet_multinomial(rng, T["designed_rush"], pc, cs["alpha"], act)
    targets = _dirichlet_multinomial(rng, T["targets"], pt, ts["alpha"], act)
    # QB: scrambles and kneels belong to the starter
    qb_idx = None
    if ti.qb1 is not None:
        hit = np.flatnonzero(P["player_id"].to_numpy() == ti.qb1)
        qb_idx = int(hit[0]) if len(hit) else None
    # efficiency: expected per-carry yards per row (depends on the row's margin)
    cm = bundle["carry"]; tm = bundle["target"]
    f, o = ti.features, ti.opp_features
    base = {"def_ypc": o["def_ypc"], "off_ypc": f["off_ypc"], "def_ypa": o["def_ypa"], "off_ypa": f["off_ypa"],
            "def_comp_rate": o["def_comp_rate"], "off_comp_rate": f["off_comp_rate"], "home": float(ti.home)}
    Pd = P.copy()
    for k, v in base.items():
        Pd[k] = v
    Pd["team_margin"] = 0.0
    Xcar = M._eff_design(Pd, M.CARRY_FEATURES); Xtar = M._eff_design(Pd, M.TARGET_FEATURES)
    # margin enters linearly: mu(row) = mu(0) + beta_margin * margin / sd_margin
    def _with_margin(model, X, feats):
        mu0 = M.ridge_predict(model, X)
        j = feats.index("team_margin")
        slope = model["beta"][j] / model["sd"][j]
        return mu0[None, :] + slope * margin_team[:, None]
    mu_c = _with_margin(cm["ridge"], Xcar, M.CARRY_FEATURES)                      # (n, m)
    def _with_margin_logit(model, X, feats):
        mu = np.asarray(model["mu"]); sd = np.asarray(model["sd"])
        Z = (np.where(np.isfinite(X), X, mu) - mu) / sd
        eta0 = model["intercept"] + Z @ np.asarray(model["beta"])
        j = feats.index("team_margin"); slope = model["beta"][j] / sd[j]
        return 1 / (1 + np.exp(-(eta0[None, :] + slope * margin_team[:, None])))
    p_catch = np.clip(_with_margin_logit(tm["catch"], Xtar, M.TARGET_FEATURES), 0.2, 0.95)   # (n, m)
    mu_t = _with_margin(tm["ypt"], Xtar, M.TARGET_FEATURES)                                 # (n, m)
    edges = np.asarray(cm["edges"]); banks = cm["banks"]
    bank_q = np.array([b["quantiles"] for b in banks]); bank_mean = np.array([b["mean"] for b in banks])
    c_edges = np.asarray(tm["c_edges"]); y_edges = np.asarray(tm["y_edges"])
    cell_q = {k: np.asarray(v["yc_quantiles"]) for k, v in tm["cells"].items()}
    cell_ypr = {k: v["ypr"] for k, v in tm["cells"].items()}
    scr_q = np.asarray(cm["scramble_quantiles"])
    tau_c = np.sqrt(cm["tau2"]); tau_t = np.sqrt(tm["tau2"])
    ids = list(P["player_id"]) + ["OTHER"]
    for j, pid in enumerate(ids):
        c = carries[:, j]; t = targets[:, j]
        if pid == "OTHER":
            mu_cj = np.full(n, float(bank_mean[len(banks) // 2])); pcj = np.full(n, 0.65); mu_tj = np.full(n, 6.5)
        else:
            mu_cj = mu_c[:, j]; pcj = p_catch[:, j]; mu_tj = mu_t[:, j]
        # rushing: bin by expected per-carry yards, draw from the bank, shift to the expectation
        b = np.clip(np.searchsorted(edges, mu_cj, side="right"), 0, len(banks) - 1)
        shift = mu_cj - bank_mean[b]

        def carry_sampler(U, b=b, shift=shift):
            Y = np.empty_like(U)
            for k in range(len(banks)):
                mk = b == k
                if mk.any():
                    Y[mk] = _interp_quantiles(bank_q[k], U[mk])
            return Y + shift[:, None]
        ry = _sum_draws(rng, c, carry_sampler)
        if tau_c > 0:
            ry += rng.standard_normal(n) * tau_c * c
        rush_yards = np.round(ry)
        # receiving: complete with the player's catch probability; yards | complete from the cell, rescaled
        cb = np.clip(np.searchsorted(c_edges, pcj, side="right"), 0, 2)
        yb = np.clip(np.searchsorted(y_edges, mu_tj, side="right"), 0, 3)
        ypr_j = mu_tj / np.maximum(pcj, 0.05)
        keys = [f"{a}_{bb}" for a, bb in zip(cb, yb)]
        scale = ypr_j / np.array([cell_ypr[k] for k in keys])
        cell_arr = np.array([int(k[0]) * 4 + int(k[2]) for k in keys])
        qtab = np.array([cell_q[f"{i}_{jj}"] for i in range(3) for jj in range(4)])
        C = int(min(60, t.max())) if n else 0
        if C > 0:
            U1 = rng.random((n, C)); U2 = rng.random((n, C))
            comp = (U1 < pcj[:, None])
            Yc = np.empty((n, C))
            for cidx in range(12):
                mk = cell_arr == cidx
                if mk.any():
                    Yc[mk] = _interp_quantiles(qtab[cidx], U2[mk])
            Yc = Yc * scale[:, None] * comp
            mask = np.arange(C)[None, :] < t[:, None]
            receptions = (comp & mask).sum(axis=1)
            rec_yards = (Yc * mask).sum(axis=1)
            over = t - C
            if (over > 0).any():
                receptions += (over.clip(min=0) * pcj).round().astype(np.int64)
                rec_yards += over.clip(min=0) * mu_tj
            if tau_t > 0:
                rec_yards += rng.standard_normal(n) * tau_t * t
            rec_yards = np.round(rec_yards)
        else:
            receptions = np.zeros(n, dtype=np.int64); rec_yards = np.zeros(n)
        res.player[pid if pid != "OTHER" else f"OTHER:{ti.team}"] = {
            "team": ti.team, "designed_carries": c, "carries": c.copy(), "rush_yards": rush_yards, "targets": t,
            "receptions": receptions, "rec_yards": rec_yards, "active": act[:, j],
        }
    # QB extras: scrambles, kneels, attempts, passing = sum of receiving
    if qb_idx is not None:
        qb = res.player[ids[qb_idx]]
        scr = T["scrambles"]
        sy = _sum_draws(rng, scr, lambda U: _interp_quantiles(scr_q, U))
        qb["carries"] = qb["carries"] + scr + T["kneels"]
        qb["rush_yards"] = qb["rush_yards"] + np.round(sy) - T["kneels"]
        qb["scrambles"] = scr
    team_rec_yards = sum(v["rec_yards"] for v in res.player.values() if v["team"] == ti.team)
    team_receptions = sum(v["receptions"] for v in res.player.values() if v["team"] == ti.team)
    T["pass_yards"] = team_rec_yards; T["completions"] = team_receptions
    T["rush_yards"] = sum(v["rush_yards"] for v in res.player.values() if v["team"] == ti.team)
    if qb_idx is not None:
        qb = res.player[ids[qb_idx]]
        qb["attempts"] = T["pass_att"]; qb["completions"] = team_receptions; qb["pass_yards"] = team_rec_yards
        qb["pass_td"] = T["pass_td"]
    # touchdown allocation
    td = bundle["td"]
    gam_r, gam_p = td["rush"]["gamma"], td["pass"]["gamma"]
    rel_r = (P[td["rush"]["rate"]] / td["rush"]["pooled_rate"]).fillna(1.0).clip(0.2, 5.0).to_numpy()
    rel_p = (P[td["pass"]["rate"]] / td["pass"]["pooled_rate"]).fillna(1.0).clip(0.2, 5.0).to_numpy()
    # official carries (scrambles included) carry the rushing-TD weight
    official = np.column_stack([res.player[pid]["carries"] for pid in ids[:m]]) if m else carries[:, :m]
    w_r = official * (rel_r ** gam_r)[None, :]
    w_p = targets[:, :m] * (rel_p ** gam_p)[None, :]
    w_r = np.column_stack([w_r, carries[:, m] * 1.0]); w_p = np.column_stack([w_p, targets[:, m] * 1.0])
    rtd = _multinomial_rows(rng, T["rush_td"], np.where(w_r.sum(axis=1, keepdims=True) > 0, w_r, 1.0))
    ptd = _multinomial_rows(rng, T["pass_td"], np.where(w_p.sum(axis=1, keepdims=True) > 0, w_p, 1.0))
    for j, pid in enumerate(ids):
        key = pid if pid != "OTHER" else f"OTHER:{ti.team}"
        res.player[key]["rush_td"] = rtd[:, j]; res.player[key]["rec_td"] = ptd[:, j]
        res.player[key]["any_td"] = rtd[:, j] + ptd[:, j]


# ------------------------------------------------------------------------------ coherence checks
def coherence_report(res: SimResult, tol: int = 0) -> dict:
    """Every identity the engine promises, checked on the rows.  Returns a dict of max absolute violations
    (all should be 0) and a boolean ``ok``."""
    out = {}
    for team, T in res.team.items():
        pl = [v for k, v in res.player.items() if v["team"] == team]
        out[f"{team}:carries==rush_att"] = int(np.abs(sum(v["carries"] for v in pl) - T["rush_att"]).max())
        out[f"{team}:targets==targets"] = int(np.abs(sum(v["targets"] for v in pl) - T["targets"]).max())
        out[f"{team}:receptions==completions"] = int(np.abs(sum(v["receptions"] for v in pl) - T["completions"]).max())
        out[f"{team}:rec_yards==pass_yards"] = float(np.abs(sum(v["rec_yards"] for v in pl) - T["pass_yards"]).max())
        out[f"{team}:rush_td==rush_td"] = int(np.abs(sum(v["rush_td"] for v in pl) - T["rush_td"]).max())
        out[f"{team}:rec_td==pass_td"] = int(np.abs(sum(v["rec_td"] for v in pl) - T["pass_td"]).max())
        out[f"{team}:pass_att+sacks+scrambles==dropbacks"] = int(np.abs(T["pass_att"] + T["sacks"] + T["scrambles"] - T["dropbacks"]).max())
        out[f"{team}:dropbacks+rush_plays==plays"] = int(np.abs(T["dropbacks"] + T["designed_rush"] + T["kneels"] - T["plays"]).max())
        out[f"{team}:negative_counts"] = int(sum(int((v[c] < 0).sum()) for v in pl for c in ("carries", "targets", "receptions", "rush_td", "rec_td")))
        out[f"{team}:receptions<=targets"] = int(sum(int((v["receptions"] > v["targets"]).sum()) for v in pl))
    out["home+away==total"] = float(np.abs(res.home_points + res.away_points - res.total).max())
    out["home-away==margin"] = float(np.abs(res.home_points - res.away_points - res.margin).max())
    out["ok"] = all(v <= max(tol, 1e-9) for k, v in out.items() if k != "ok")
    return out


def summarize(arr: np.ndarray, qs=(0.05, 0.25, 0.5, 0.75, 0.95)) -> dict:
    return {"mean": float(np.mean(arr)), "sd": float(np.std(arr)), **{f"q{int(q * 100):02d}": float(np.quantile(arr, q)) for q in qs}}
