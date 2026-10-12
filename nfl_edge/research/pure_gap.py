"""Error decomposition helpers for the PURE_PLAYER_V1 vs DATA_PLAYER_V4 gap study (research only).

Every forecast mean of a player statistic is written as a product of components that each arm exposes:

    snap_share                      = snap
    targets                         = V_pa  x snap x usage            usage = targets / (V_pa x snap)
    receptions / receiving_yards    = V_pa  x snap x usage x eff      eff   = mean / targets
    carries                         = V_ra  x snap x usage
    rushing_yards                   = V_ra  x snap x usage x eff
    passing_attempts                = V_pa  x usage                   (starting QB; snap ~ 1)
    completions / passing_yards     = V_pa  x usage x eff

`V` is the arm's predicted team pass (rush) attempts, `snap` its predicted snap share, `usage` the opportunities
per team play while on the field, `eff` the statistic per opportunity. The product reproduces each arm's scored
mean exactly, so a hybrid that takes some components from arm A and the rest from arm B is a well-defined forecast,
and the Shapley value of each component over all 2^K hybrids splits the paired MAE gap A - B into parts that sum to
it exactly (per row, hence also per bootstrap replicate). The same machinery with B = the realised components
("oracle") splits an arm's own MAE into the error that comes from each component.

Nothing here reads a market quantity; the arms' forecasts are inputs.
"""
from __future__ import annotations

from itertools import combinations
from math import factorial

import numpy as np

OPPORTUNITY = {"targets": "targets", "receptions": "targets", "receiving_yards": "targets", "carries": "carries",
               "rushing_yards": "carries", "passing_attempts": "passing_attempts", "completions": "passing_attempts",
               "passing_yards": "passing_attempts"}
VOLUME = {"targets": "vol_pa", "receptions": "vol_pa", "receiving_yards": "vol_pa", "carries": "vol_ra", "rushing_yards": "vol_ra",
          "passing_attempts": "vol_pa", "completions": "vol_pa", "passing_yards": "vol_pa"}
ACTUAL_VOLUME = {"vol_pa": "pa", "vol_ra": "ra"}


def components(stat: str) -> list[str]:
    if stat == "snap_share":
        return ["snap"]
    if stat in ("passing_attempts",):
        return ["volume", "usage"]
    if stat in ("completions", "passing_yards"):
        return ["volume", "usage", "efficiency"]
    if stat in ("targets", "carries"):
        return ["volume", "snap", "usage"]
    return ["volume", "snap", "usage", "efficiency"]


SNAP_FLOOR, VOL_FLOOR, OPP_FLOOR = 0.01, 1.0, 1e-6


def factorize(stat: str, mean, opp, vol, snap) -> dict:
    """Arm forecast -> component arrays whose product is `mean` (exactly, up to the floors on zero divisors)."""
    mean = np.asarray(mean, float)
    if stat == "snap_share":
        return {"snap": mean}
    vol = np.maximum(np.asarray(vol, float), VOL_FLOOR)
    opp = np.asarray(opp, float)
    out = {"volume": vol}
    if "snap" in components(stat):
        sn = np.maximum(np.asarray(snap, float), SNAP_FLOOR)
        out["snap"] = sn
        out["usage"] = opp / (vol * sn)
    else:
        out["usage"] = opp / vol
    if "efficiency" in components(stat):
        out["efficiency"] = np.where(opp > OPP_FLOOR, mean / np.maximum(opp, OPP_FLOOR), 0.0)
    return out


def factorize_actual(stat: str, y, opp_act, vol_act, snap_act, model_comp: dict) -> dict:
    """Realised components. Where a realised component is undefined (no snap count; zero opportunities, so no
    realised efficiency) the arm's own component is used, so that row attributes nothing to it."""
    y = np.asarray(y, float)
    if stat == "snap_share":
        return {"snap": y}
    vol = np.maximum(np.asarray(vol_act, float), VOL_FLOOR)
    opp = np.asarray(opp_act, float)
    out = {"volume": vol}
    if "snap" in model_comp:
        sa = np.asarray(snap_act, float)
        sn = np.where(np.isfinite(sa), np.maximum(sa, SNAP_FLOOR), model_comp["snap"])
        out["snap"] = sn
        out["usage"] = opp / (vol * sn)
    else:
        out["usage"] = opp / vol
    if "efficiency" in model_comp:
        out["efficiency"] = np.where(opp > 0, y / np.maximum(opp, OPP_FLOOR), model_comp["efficiency"])
    return out


def shapley_weights(k: int) -> dict:
    return {s: factorial(s) * factorial(k - s - 1) / factorial(k) for s in range(k)}


def shapley_abs_error(y, comp_a: dict, comp_b: dict, names: list[str]) -> dict:
    """Per-row Shapley contribution of each component to |mean_A - y| - |mean_B - y|.

    v(S) = |prod_{k in S} A_k * prod_{k not in S} B_k - y|; phi_k = sum_{S not containing k} w(|S|) [v(S+k) - v(S)].
    The contributions sum, row by row, to v(all) - v(none)."""
    y = np.asarray(y, float)
    K = len(names)
    w = shapley_weights(K)
    cache: dict = {}

    def v(S: frozenset):
        if S not in cache:
            m = np.ones_like(y)
            for k in names:
                m = m * (comp_a[k] if k in S else comp_b[k])
            cache[S] = np.abs(m - y)
        return cache[S]

    phi = {}
    for k in names:
        rest = [x for x in names if x != k]
        acc = np.zeros_like(y)
        for r in range(K):
            for S in combinations(rest, r):
                S = frozenset(S)
                acc += w[r] * (v(S | {k}) - v(S))
        phi[k] = acc
    phi["_total"] = v(frozenset(names)) - v(frozenset())
    return phi


def cluster_boot(values, games, B: int = 1000, seed: int = 20261010):
    """Paired, game-clustered bootstrap 95% percentile interval of the mean of `values` (rows clustered by game)."""
    values = np.asarray(values, float)
    codes, inv = np.unique(np.asarray(games), return_inverse=True)
    G = len(codes)
    if G < 3:
        return None
    sums = np.bincount(inv, weights=values, minlength=G)
    cnt = np.bincount(inv, minlength=G).astype(float)
    rng = np.random.default_rng(seed)
    out = np.empty(B)
    for i in range(0, B, 200):
        idx = rng.integers(0, G, size=(min(200, B - i), G))
        out[i:i + idx.shape[0]] = sums[idx].sum(1) / cnt[idx].sum(1)
    return [round(float(np.quantile(out, 0.025)), 6), round(float(np.quantile(out, 0.975)), 6)]


def summarize(values, games, B: int = 1000) -> dict:
    values = np.asarray(values, float)
    return {"n": int(len(values)), "n_games": int(len(set(np.asarray(games).tolist()))),
            "mean": round(float(values.mean()), 6) if len(values) else None,
            "ci95": cluster_boot(values, games, B) if len(values) else None}


def contribution(diff, mask, games, B: int = 1000) -> dict:
    """Share of a pooled paired gap that sits in the rows of `mask`: mean over ALL rows of diff * mask (so the
    flagged and unflagged contributions add to the pooled gap), with its clustered CI, plus the within-stratum gap."""
    diff = np.asarray(diff, float); mask = np.asarray(mask, bool)
    return {"n_rows": int(mask.sum()), "share_of_rows": round(float(mask.mean()), 4),
            "within_stratum_gap": summarize(diff[mask], np.asarray(games)[mask], B) if mask.any() else None,
            "contribution_to_pooled_gap": summarize(np.where(mask, diff, 0.0), games, B)}
