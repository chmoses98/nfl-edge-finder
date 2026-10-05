"""RISK1 -- does GAME SCRIPT V2 script robustness / thesis concentration predict betting-quality differences
PROSPECTIVELY? RESEARCH_ONLY. It never changes a probability, a stake or an authority.

Preregistered in research/game_script_v2/wave2/PREREGISTRATION.md, section 6.

Everything here reads FROZEN prediction-time artifacts (the GAME SCRIPT V2 document and the projection rows written by
the same simulation run) and settled outcomes. Nothing is re-simulated: every robustness number, entropy, primary
script and world fingerprint is a pure function of what was written before kickoff, so a settlement can never change
one (pinned by test).
"""
from __future__ import annotations

import glob
import gzip
import json
import os
from datetime import datetime, timezone
from types import SimpleNamespace

import numpy as np
import pandas as pd

from . import script_v2 as V

RISK1_VERSION = "risk1-1.0.0"
PROSPECTIVE_CUTOFF = "2026-10-05T16:14:02+00:00"     # committer time of the Wave-2 preregistration (0aea50f)
MEASURES = (("p55", +1), ("floor", +1), ("hhi", -1), ("failure_mass", -1))   # (column, hypothesised sign)
THESIS_JACCARD = 0.80
B, SEED = 2000, 20261005


def _ts(x) -> datetime:
    d = datetime.fromisoformat(str(x).replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


# ------------------------------------------------------------------------------------- frozen features
def derived(doc: dict, contract: dict) -> dict:
    """Quantities RISK1 reads from one frozen contract record (and its game's frozen script probabilities)."""
    ps = np.asarray(doc["p_script"], float)
    pc = np.array([np.nan if x is None else x for x in contract["p_cash_given_script"]], float)
    with np.errstate(divide="ignore", invalid="ignore"):
        ent = float(-np.sum(np.where(ps > 0, ps * np.log(ps), 0.0)))
    win_contrib = np.where(np.isfinite(pc), ps * pc, 0.0)
    fail_contrib = np.where(np.isfinite(pc), ps * (1 - pc), 0.0)
    rob = contract.get("script_robustness") or {}
    return {"p_cash": contract.get("p_cash"), "p50": rob.get("0.50"), "p55": rob.get("0.55"), "p60": rob.get("0.60"),
            "floor": contract.get("major_script_floor"), "failure_mass": contract.get("failure_script_mass"),
            "hhi": contract.get("win_contribution_hhi"), "script_entropy": ent,
            "primary_winning_script": doc["cells"][int(np.argmax(win_contrib))],
            "primary_failing_script": doc["cells"][int(np.argmax(fail_contrib))]}


def capture_index(sim_root: str) -> pd.DataFrame:
    """Every frozen GAME SCRIPT V2 capture under a market-data tree: run, game, generation time."""
    rows = []
    for p in sorted(glob.glob(os.path.join(sim_root, "data", "shadow", "sim", "*", "*.scripts_v2.json.gz"))):
        run = os.path.basename(p)[:16]
        with gzip.open(p, "rt") as f:
            doc = json.load(f)
        for gid, g in (doc.get("games") or {}).items():
            rows.append({"run_id": run, "game_id": gid, "path": p, "generated_at": g.get("generated_at"), "state": g.get("state")})
    return pd.DataFrame(rows)


def select_captures(idx: pd.DataFrame, kickoffs: dict, cutoff: str = PROSPECTIVE_CUTOFF) -> pd.DataFrame:
    """Per prospective game, the LAST capture generated before kickoff. Games kicking off before the cutoff, and
    captures generated at or after kickoff, are never used."""
    c = _ts(cutoff)
    keep = []
    for gid, g in idx[idx["state"] == "OK"].groupby("game_id"):
        ko = kickoffs.get(gid)
        if ko is None or _ts(ko) <= c:
            continue
        pre = g[[_ts(t) < _ts(ko) for t in g["generated_at"]]]
        if len(pre):
            keep.append(pre.sort_values("generated_at").iloc[-1])
    return pd.DataFrame(keep)


def observations(doc: dict, proj_rows: list) -> pd.DataFrame:
    """One row per contract with a frozen script matrix, football probability and a two-sided quote."""
    by = {r["ticker"]: r for r in proj_rows}
    out = []
    for c in doc.get("contracts") or []:
        if c.get("p_cash") is None:
            continue
        r = by.get(c["ticker"]) or {}
        mid = r.get("mid")
        if mid is None or r.get("yes_bid") is None or r.get("yes_ask") is None or not (0 < mid < 1):
            continue
        w = r.get("reconcile_weight") or 0
        p_model = r.get("p_reconciled") if (w > 0 and r.get("p_reconciled") is not None) else r.get("p_football")
        if p_model is None:
            continue
        out.append({"ticker": c["ticker"], "game_id": doc["game_id"], "family": c.get("family"), "stat": c.get("stat"),
                    "mid": float(mid), "p_model": float(p_model), "p_football": r.get("p_football"),
                    "p_reconciled": r.get("p_reconciled"), "reconcile_weight": w,
                    "edge": float(p_model - mid), **derived(doc, c)})
    return pd.DataFrame(out)


# ------------------------------------------------------------------------------------------ outcomes
def realized_cash(contract: dict, game: dict, player_stats: dict) -> float | None:
    """The settled value of a contract under the PRICER's semantics (`script_v2.contract_cash`) applied to the
    realised game: a one-row SimResult of the final box score."""
    res = SimpleNamespace(margin=np.array([game["home_score"] - game["away_score"]], float),
                          total=np.array([game["home_score"] + game["away_score"]], float),
                          home_points=np.array([game["home_score"]], float), away_points=np.array([game["away_score"]], float),
                          player={pid: {"team": st.get("team"), "active": np.array([True]), **{k: np.array([v], float)
                                        for k, v in st.items() if k != "team"}} for pid, st in player_stats.items()},
                          game_id=game["game_id"])
    gi = SimpleNamespace(game_id=game["game_id"], home=SimpleNamespace(team=game["home_team"]), away=SimpleNamespace(team=game["away_team"]))
    v, state, _ = V.contract_cash(contract, res, gi, game.get("player_map") or {})
    return None if v is None else float(v[0])


# ------------------------------------------------------------------------------------------ the tests
def _logit(p):
    p = np.clip(np.asarray(p, float), 1e-4, 1 - 1e-4)
    return np.log(p / (1 - p))


def _design(d: pd.DataFrame, measure: str) -> np.ndarray:
    fam = pd.get_dummies(d["family"].astype(str), drop_first=True, dtype=float)
    z = d.groupby("family")[measure].transform(lambda x: (x - x.mean()) / (x.std() if x.std() > 0 else 1.0))
    return np.column_stack([_logit(d["mid"]), _logit(d["p_model"]), z.fillna(0.0).to_numpy(float), fam.to_numpy(float)])


def _fit_coef(X, y) -> float:
    from . import models as M
    m = M.logistic_fit(X, y, lam=1e-6)
    return float(m["beta"][2] / m["sd"][2]) if m["sd"][2] > 0 else float("nan")


def primary_test(d: pd.DataFrame, B_: int = B, seed: int = SEED) -> dict:
    """Coefficient on each robustness measure (within-family z) in a logistic model of the outcome that already
    contains the market and the model; game-clustered bootstrap; Holm across the four measures."""
    d = d.dropna(subset=["y"]).reset_index(drop=True)
    out = {}
    for meas, sign in MEASURES:
        dd = d.dropna(subset=[meas]).reset_index(drop=True)
        if len(dd) < 50 or dd["game_id"].nunique() < 10:
            out[meas] = {"n": int(len(dd)), "status": "INSUFFICIENT_DATA"}
            continue
        y = dd["y"].to_numpy(float)
        est = _fit_coef(_design(dd, meas), y)
        keys = sorted(dd["game_id"].unique())
        pos = [np.flatnonzero(dd["game_id"].to_numpy() == g) for g in keys]
        rng = np.random.default_rng(seed)               # same seed per measure: comparable resamples
        bs = []
        for _ in range(B_):
            ix = np.concatenate([pos[i] for i in rng.integers(0, len(keys), len(keys))])
            sub = dd.iloc[ix]
            try:
                bs.append(_fit_coef(_design(sub, meas), sub["y"].to_numpy(float)))
            except Exception:                      # noqa: BLE001 -- a degenerate resample is skipped, and counted
                continue
        bs = np.asarray([b for b in bs if np.isfinite(b)])
        p_one_sided = float(np.mean(sign * bs <= 0)) if len(bs) else 1.0
        out[meas] = {"n": int(len(dd)), "n_games": int(dd["game_id"].nunique()), "coef": est, "hypothesised_sign": sign,
                     "lo": float(np.quantile(bs, 0.025)) if len(bs) else None, "hi": float(np.quantile(bs, 0.975)) if len(bs) else None,
                     "p_one_sided": p_one_sided, "valid_resamples": int(len(bs))}
    tested = sorted([(v["p_one_sided"], k) for k, v in out.items() if "p_one_sided" in v])
    m = len(tested)
    for i, (p, k) in enumerate(tested):
        out[k]["holm_threshold"] = 0.05 / (m - i)
    stop = False
    for i, (p, k) in enumerate(tested):
        out[k]["supports_hypothesis"] = (not stop) and p <= 0.05 / (m - i)
        if not out[k]["supports_hypothesis"]:
            stop = True
    return out


def tercile_table(d: pd.DataFrame, measure: str = "p55") -> list:
    """Descriptive: mean (outcome - p_model) for top vs bottom robustness tercile inside family x model-probability
    quintile x |edge| band cells."""
    d = d.dropna(subset=["y", measure]).copy()
    d["pq"] = pd.qcut(d["p_model"], 5, labels=False, duplicates="drop")
    d["eb"] = pd.cut(d["edge"].abs(), [-1e-9, 0.03, 0.08, 1.0], labels=["<0.03", "0.03-0.08", ">0.08"])
    rows = []
    for (fam, pq, eb), g in d.groupby(["family", "pq", "eb"], observed=True):
        if len(g) < 30:
            continue
        t = pd.qcut(g[measure].rank(method="first"), 3, labels=False)
        lo, hi = g[t == 0], g[t == 2]
        rows.append({"family": fam, "p_quintile": int(pq), "edge_band": str(eb), "n": int(len(g)),
                     "resid_top": float((hi["y"] - hi["p_model"]).mean()), "resid_bottom": float((lo["y"] - lo["p_model"]).mean())})
    return rows


# ----------------------------------------------------------------------------------------- portfolios
def thesis_groups(fingerprints: dict, threshold: float = THESIS_JACCARD) -> list:
    """Group positions whose winning simulated worlds overlap (Jaccard of winning rows >= threshold) into one thesis
    (union-find). Identical settlement worlds under different tickers are one thesis."""
    keys = sorted(fingerprints)
    parent = {k: k for k in keys}

    def find(k):
        while parent[k] != k:
            parent[k] = parent[parent[k]]; k = parent[k]
        return k
    cash = {k: V.decode_fingerprint(fingerprints[k]) if isinstance(fingerprints[k], dict) else np.asarray(fingerprints[k], float)
            for k in keys}
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if cash[a].shape != cash[b].shape:
                continue
            j = V.pair_dependency(cash[a], cash[b])["jaccard_winning_rows"]
            if j is not None and j >= threshold:
                parent[find(a)] = find(b)
    groups = {}
    for k in keys:
        groups.setdefault(find(k), []).append(k)
    return sorted(groups.values(), key=lambda g: (-len(g), g))


def effective_theses(stakes: dict, groups: list) -> dict:
    """1 / sum w_i^2 over thesis risk shares (stake share of each thesis group)."""
    tot = sum(stakes.values())
    if tot <= 0:
        return {"effective_theses": None, "n_positions": len(stakes), "n_theses": len(groups)}
    w = np.array([sum(stakes.get(k, 0.0) for k in g) / tot for g in groups])
    return {"effective_theses": float(1.0 / np.sum(w ** 2)), "n_positions": len(stakes), "n_theses": len(groups),
            "max_thesis_share": float(w.max())}
