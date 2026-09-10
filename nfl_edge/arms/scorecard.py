"""Scorecard over the arm-evaluation corpus: paired comparisons on identical games and contracts.

Three rules the incumbent scorecard already enforces, kept here:

  * a repeated snapshot is not an independent observation -- every block names its sample unit and prints
    rows / contracts / games / weeks beside every number;
  * event probabilities and contract values are scored in different spaces;
  * an empty set reports its size and no metrics.

And three the experiment adds:

  * every comparison is PAIRED: an arm is scored only on the games/contracts where the arm it is compared with
    also has a value, from the same snapshot and the same draws;
  * uncertainty is clustered at the GAME: standard errors on game-level metrics use games as units, and
    contract-level paired differences use a game-clustered bootstrap (deterministic seed);
  * no verdict before MIN_GAMES_FOR_VERDICT distinct games. Below it every headline is INSUFFICIENT_EVIDENCE.
    Above it the label is EVIDENCE_ACCUMULATING with an interval; there is no "winner" banner in this module.
"""
from __future__ import annotations

import math
from collections import defaultdict

import numpy as np

from nfl_edge.arms import registry as R
from nfl_edge.shadow.eval_scorecard import horizon_view, latest_pregame_view

ARMS = list(R.PRIMARY_ARMS)
ARM_ATTR = {R.CURRENT: "current", R.DATA_ONLY: "data_only", R.HYBRID: "hybrid"}
PAIRS = ((R.DATA_ONLY, R.CURRENT), (R.HYBRID, R.CURRENT), (R.HYBRID, R.DATA_ONLY))
INSUFFICIENT = "INSUFFICIENT_EVIDENCE"
ACCUMULATING = "EVIDENCE_ACCUMULATING"
BOOTSTRAP_B = 1000


def _mean(xs):
    xs = [float(x) for x in xs if x is not None]
    return None if not xs else sum(xs) / len(xs)


def _se(xs):
    xs = [float(x) for x in xs if x is not None]
    if len(xs) < 2:
        return None
    return float(np.std(xs, ddof=1) / math.sqrt(len(xs)))


def counts(rows) -> dict:
    return {"n_rows": len(rows),
            "n_unique_contracts": len({(r.get("game_id"), r.get("ticker")) for r in rows if r.get("ticker")}),
            "n_games": len({r.get("game_id") for r in rows if r.get("game_id")}),
            "n_weeks": len({(r.get("season"), r.get("week")) for r in rows if r.get("week") is not None})}


def evidence_label(n_games: int) -> str:
    return INSUFFICIENT if n_games < R.MIN_GAMES_FOR_VERDICT else ACCUMULATING


# ======================================================================================================
# sample units (one row per game / per contract, by the incumbent's documented horizon rule)
# ======================================================================================================

def views(rows: list) -> dict:
    """raw, T-24h .. T-30m, latest_pregame. Game rows carry no ticker, so the key is the game itself."""
    out = {"raw": (rows, {"note": "every pregame snapshot; repeated, correlated; diagnostics only"})}
    for target in R.PRIMARY_HORIZONS_MIN:
        out[R.HORIZON_LABELS[target]] = horizon_view(rows, float(target))
    out["latest_pregame"] = latest_pregame_view(rows)
    return out


# ======================================================================================================
# game-centre accuracy
# ======================================================================================================

def _usable(row, arm):
    a = (row.get("arms") or {}).get(arm) or {}
    ok = a.get("status") == R.OK and a.get("margin_error") is not None and a.get("total_error") is not None
    if arm == R.CURRENT and row.get("reproduction_ok") is False:
        ok = False
    return ok


def center_metrics(rows, arm) -> dict:
    use = [r for r in rows if _usable(r, arm)]
    if not use:
        return {"n_games": 0, "excluded": len(rows)}
    a = [r["arms"][arm] for r in use]
    out = {**counts(use), "excluded_not_usable": len(rows) - len(use),
           "status_counts": _tally([((r.get("arms") or {}).get(arm) or {}).get("status") for r in rows])}
    for q in ("margin", "total"):
        err = [x[f"{q}_error"] for x in a]
        out[q] = {"mae": _mean([abs(e) for e in err]), "rmse": math.sqrt(_mean([e * e for e in err])),
                  "bias": _mean(err), "se_mae": _se([abs(e) for e in err]), "se_bias": _se(err)}
    hb = [x.get("home_win_brier") for x in a if x.get("home_win_brier") is not None]
    if hb:
        out["home_win"] = {"n": len(hb), "brier": _mean(hb),
                           "log_loss": _mean([x.get("home_win_log_loss") for x in a if x.get("home_win_log_loss") is not None])}
    hs = [x.get("home_score_error") for x in a if x.get("home_score_error") is not None]
    if hs:
        out["implied_scores"] = {"home_mae": _mean([abs(e) for e in hs]),
                                 "away_mae": _mean([abs(x["away_score_error"]) for x in a if x.get("away_score_error") is not None])}
    return out


def _market_usable(row, key):
    m = row.get(key) or {}
    return m.get("margin_error") is not None and m.get("total_error") is not None


def market_center_metrics(rows, key="market_at_snapshot") -> dict:
    use = [r for r in rows if _market_usable(r, key)]
    if not use:
        return {"n_games": 0}
    out = {**counts(use)}
    for q in ("margin", "total"):
        err = [r[key][f"{q}_error"] for r in use]
        out[q] = {"mae": _mean([abs(e) for e in err]), "rmse": math.sqrt(_mean([e * e for e in err])), "bias": _mean(err)}
    return out


def paired_center(rows, arm_a, arm_b) -> dict:
    """Paired difference in error, arm_a minus arm_b, on the games where BOTH arms are usable. Negative favours A."""
    use = [r for r in rows if _usable(r, arm_a) and _usable(r, arm_b)]
    out = {"arm": arm_a, "versus": arm_b, **counts(use), "evidence": evidence_label(len({r["game_id"] for r in use}))}
    if len(use) < 2:
        return out
    for q in ("margin", "total"):
        da = [abs(r["arms"][arm_a][f"{q}_error"]) - abs(r["arms"][arm_b][f"{q}_error"]) for r in use]
        ds = [r["arms"][arm_a][f"{q}_sq_error"] - r["arms"][arm_b][f"{q}_sq_error"] for r in use]
        out[q] = {"mean_diff_abs_error": _mean(da), "se": _se(da),
                  "ci95": _ci(da), "effect_size_d": _effect(da),
                  "mean_diff_sq_error": _mean(ds), "se_sq": _se(ds), "share_a_closer": _mean([1.0 if d < 0 else 0.0 for d in da])}
    hb = [(r["arms"][arm_a].get("home_win_brier"), r["arms"][arm_b].get("home_win_brier")) for r in use]
    hb = [(x, y) for x, y in hb if x is not None and y is not None]
    if hb:
        d = [x - y for x, y in hb]
        out["home_win_brier"] = {"n": len(d), "mean_diff": _mean(d), "se": _se(d), "ci95": _ci(d)}
    return out


def _ci(xs):
    m, se = _mean(xs), _se(xs)
    return None if m is None or se is None else [m - 1.96 * se, m + 1.96 * se]


def _effect(xs):
    xs = [float(x) for x in xs]
    if len(xs) < 2:
        return None
    sd = float(np.std(xs, ddof=1))
    return None if sd == 0 else float(np.mean(xs) / sd)


def paired_vs_market(rows, arm, key="market_at_snapshot") -> dict:
    """Challenger centre error minus the market centre error (snapshot or close) on the same games."""
    use = [r for r in rows if _usable(r, arm) and _market_usable(r, key)]
    out = {"arm": arm, "versus": key, **counts(use), "evidence": evidence_label(len({r["game_id"] for r in use}))}
    if len(use) < 2:
        return out
    for q in ("margin", "total"):
        d = [abs(r["arms"][arm][f"{q}_error"]) - abs(r[key][f"{q}_error"]) for r in use]
        out[q] = {"mean_diff_abs_error": _mean(d), "se": _se(d), "ci95": _ci(d), "share_arm_closer": _mean([1.0 if x < 0 else 0.0 for x in d])}
    return out


def movement_summary(rows, arm) -> dict:
    use = [r for r in rows if _usable(r, arm) and arm != R.CURRENT]
    out = {"arm": arm, **counts(use)}
    for q in ("margin", "total"):
        c = _tally([r["arms"][arm].get(f"{q}_movement_vs_close") for r in use])
        directional = c.get("toward", 0) + c.get("away", 0)
        out[q] = {"counts": c, "n_directional": directional,
                  "toward_share": (c.get("toward", 0) / directional) if directional else None,
                  "closer_than_market_share": _mean([1.0 if r["arms"][arm].get(f"{q}_closer_than_market") else 0.0
                                                     for r in use if r["arms"][arm].get(f"{q}_closer_than_market") is not None]),
                  "mean_deviation_from_market": _mean([r["arms"][arm].get(f"{q}_minus_market") for r in use]),
                  "mean_abs_deviation_from_market": _mean([abs(r["arms"][arm].get(f"{q}_minus_market") or 0) for r in use])}
    return out


def band_table(rows, arm, q="margin") -> dict:
    groups = defaultdict(list)
    for r in rows:
        if _usable(r, arm) and arm != R.CURRENT:
            groups[r["arms"][arm].get(f"{q}_disagreement_band")].append(r)
    out = {}
    for band in [b[1] for b in R.DISAGREEMENT_BANDS_POINTS]:
        rs = groups.get(band, [])
        if not rs:
            out[band] = {"n_games": 0}
            continue
        out[band] = {**counts(rs), f"{q}_mae_arm": _mean([abs(r["arms"][arm][f"{q}_error"]) for r in rs]),
                     f"{q}_mae_market": _mean([abs((r.get("market_at_snapshot") or {}).get(f"{q}_error")) for r in rs
                                               if (r.get("market_at_snapshot") or {}).get(f"{q}_error") is not None]),
                     "toward_share": movement_summary(rs, arm)[q]["toward_share"]}
    return out


# ======================================================================================================
# contract-level (event probabilities and contract values)
# ======================================================================================================

def _event_rows(rows, arm):
    k = f"p_{ARM_ATTR[arm]}"
    return [r for r in rows if r.get("event_binary_valid") and r.get("settled_yes") in (0.0, 1.0, 0, 1)
            and r.get(k) is not None and (r.get("arm_status") or {}).get(arm) == R.OK]


def _payout_rows(rows, arm):
    k = f"cv_{ARM_ATTR[arm]}"
    return [r for r in rows if r.get("settlement_status") == "SETTLED" and r.get("exact_payout_known")
            and r.get("settled_yes") is not None and r.get(k) is not None and (r.get("arm_status") or {}).get(arm) == R.OK]


def _brier(p, y):
    return (float(p) - float(y)) ** 2


def _logloss(p, y):
    p = min(max(float(p), 1e-9), 1 - 1e-9)
    return -(float(y) * math.log(p) + (1 - float(y)) * math.log(1 - p))


def contract_metrics(rows, arm) -> dict:
    er, pr = _event_rows(rows, arm), _payout_rows(rows, arm)
    pk, ck = f"p_{ARM_ATTR[arm]}", f"cv_{ARM_ATTR[arm]}"
    out = {"arm": arm, "event": {**counts(er)}, "payout": {**counts(pr)}}
    if er:
        out["event"].update({"brier": _mean([_brier(r[pk], r["settled_yes"]) for r in er]),
                             "log_loss": _mean([_logloss(r[pk], r["settled_yes"]) for r in er]),
                             "mean_predicted": _mean([r[pk] for r in er]), "actual_rate": _mean([r["settled_yes"] for r in er]),
                             "mean_signed_error": _mean([r[pk] - r["settled_yes"] for r in er])})
    if pr:
        out["payout"].update({"mse": _mean([(r[ck] - r["settled_yes"]) ** 2 for r in pr]),
                              "mae": _mean([abs(r[ck] - r["settled_yes"]) for r in pr]),
                              "mean_signed": _mean([r[ck] - r["settled_yes"] for r in pr])})
        mk = [r for r in pr if r.get("mid_t") is not None]
        out["payout"]["market_at_snapshot_mse"] = _mean([(r["mid_t"] - r["settled_yes"]) ** 2 for r in mk]) if mk else None
        cl = [r for r in pr if r.get("close_status") == "OK" and r.get("close_mid") is not None]
        out["payout"]["market_at_close_mse"] = _mean([(r["close_mid"] - r["settled_yes"]) ** 2 for r in cl]) if cl else None
        out["payout"]["n_with_close"] = len(cl)
    return out


def cluster_bootstrap(values, clusters, B: int = BOOTSTRAP_B, seed: int = 0) -> dict:
    """Mean of `values` with a game-clustered bootstrap: resample CLUSTERS (games) with replacement."""
    values = np.asarray(values, float)
    clusters = np.asarray(clusters)
    if len(values) == 0:
        return {"n": 0}
    ids = np.unique(clusters)
    if len(ids) < 2:
        return {"n": int(len(values)), "n_clusters": int(len(ids)), "mean": float(values.mean()), "se": None, "ci95": None}
    by = {c: values[clusters == c] for c in ids}
    rng = np.random.default_rng(seed)
    means = []
    for _ in range(B):
        pick = rng.choice(ids, size=len(ids), replace=True)
        s = np.concatenate([by[c] for c in pick])
        means.append(s.mean())
    means = np.asarray(means)
    return {"n": int(len(values)), "n_clusters": int(len(ids)), "mean": float(values.mean()),
            "se": float(means.std(ddof=1)), "ci95": [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))],
            "bootstrap": {"B": B, "seed": seed, "unit": "game"}}


def paired_contract(rows, arm_a, arm_b) -> dict:
    """Brier (event space) and payout MSE (contract space) differences, A minus B, game-clustered."""
    ea = {(r["game_id"], r["ticker"]): r for r in _event_rows(rows, arm_a)}
    eb = {(r["game_id"], r["ticker"]): r for r in _event_rows(rows, arm_b)}
    keys = sorted(set(ea) & set(eb))
    pa, pb = f"p_{ARM_ATTR[arm_a]}", f"p_{ARM_ATTR[arm_b]}"
    d = [_brier(ea[k][pa], ea[k]["settled_yes"]) - _brier(eb[k][pb], eb[k]["settled_yes"]) for k in keys]
    dl = [_logloss(ea[k][pa], ea[k]["settled_yes"]) - _logloss(eb[k][pb], eb[k]["settled_yes"]) for k in keys]
    games = [k[0] for k in keys]
    out = {"arm": arm_a, "versus": arm_b, "event": {"n_contracts": len(keys), "n_games": len(set(games)),
                                                   "brier_diff": cluster_bootstrap(d, games), "log_loss_diff": cluster_bootstrap(dl, games)},
           "evidence": evidence_label(len(set(games)))}
    xa = {(r["game_id"], r["ticker"]): r for r in _payout_rows(rows, arm_a)}
    xb = {(r["game_id"], r["ticker"]): r for r in _payout_rows(rows, arm_b)}
    keys = sorted(set(xa) & set(xb))
    ca, cb = f"cv_{ARM_ATTR[arm_a]}", f"cv_{ARM_ATTR[arm_b]}"
    d = [(xa[k][ca] - xa[k]["settled_yes"]) ** 2 - (xb[k][cb] - xb[k]["settled_yes"]) ** 2 for k in keys]
    out["payout"] = {"n_contracts": len(keys), "n_games": len({k[0] for k in keys}), "mse_diff": cluster_bootstrap(d, [k[0] for k in keys])}
    return out


def paired_contract_vs_market(rows, arm, which="mid_t") -> dict:
    """Payout MSE of the arm's contract value minus the market's (snapshot mid or closing mid), same contracts."""
    pr = [r for r in _payout_rows(rows, arm) if r.get(which) is not None
          and (which != "close_mid" or r.get("close_status") == "OK")]
    ck = f"cv_{ARM_ATTR[arm]}"
    d = [(r[ck] - r["settled_yes"]) ** 2 - (r[which] - r["settled_yes"]) ** 2 for r in pr]
    games = [r["game_id"] for r in pr]
    return {"arm": arm, "versus": "market_at_snapshot" if which == "mid_t" else "market_at_close",
            "n_contracts": len(pr), "n_games": len(set(games)), "mse_diff": cluster_bootstrap(d, games),
            "evidence": evidence_label(len(set(games)))}


def calibration(rows, arm, width=0.1) -> list:
    er = _event_rows(rows, arm)
    pk = f"p_{ARM_ATTR[arm]}"
    b = defaultdict(list)
    for r in er:
        p = min(max(float(r[pk]), 0.0), 1.0)
        lo = min(int(p / width) * width, 1.0 - width)
        b[f"{lo:.2f}-{lo + width:.2f}"].append(r)
    return [{"band": k, "n": len(v), "mean_predicted": _mean([r[pk] for r in v]), "actual_rate": _mean([r["settled_yes"] for r in v])}
            for k, v in sorted(b.items())]


def _tally(vals):
    out = defaultdict(int)
    for v in vals:
        out[str(v)] += 1
    return dict(sorted(out.items()))


# ======================================================================================================
# assembly
# ======================================================================================================

def game_block(rows) -> dict:
    blk = {**counts(rows), "arms": {a: center_metrics(rows, a) for a in ARMS},
           "market_at_snapshot": market_center_metrics(rows, "market_at_snapshot"),
           "market_at_close": market_center_metrics(rows, "close"),
           "paired": [paired_center(rows, a, b) for a, b in PAIRS],
           "paired_vs_market_at_snapshot": [paired_vs_market(rows, a, "market_at_snapshot") for a in ARMS],
           "paired_vs_close": [paired_vs_market(rows, a, "close") for a in ARMS],
           "movement": {a: movement_summary(rows, a) for a in (R.DATA_ONLY, R.HYBRID)},
           "disagreement_bands": {a: {"margin": band_table(rows, a, "margin"), "total": band_table(rows, a, "total")}
                                  for a in (R.DATA_ONLY, R.HYBRID)},
           "by_center_source": _tally([(r.get("market_at_snapshot") or {}).get("source") for r in rows]),
           "by_data_quality_state": {a: _tally([((r.get("arms") or {}).get(a) or {}).get("data_quality_state") for r in rows]) for a in ARMS},
           "close_center_status": _tally([(r.get("close") or {}).get("status") for r in rows])}
    blk["evidence"] = evidence_label(blk["n_games"])
    return blk


def contract_block(rows) -> dict:
    return {**counts(rows), "arms": {a: contract_metrics(rows, a) for a in ARMS},
            "paired": [paired_contract(rows, a, b) for a, b in PAIRS],
            "paired_vs_market": [paired_contract_vs_market(rows, a, w) for a in ARMS for w in ("mid_t", "close_mid")],
            "calibration": {a: calibration(rows, a) for a in ARMS},
            "by_family": _tally([r.get("family") for r in rows]),
            "by_settlement_status": _tally([r.get("settlement_status") for r in rows]),
            "by_close_status": _tally([r.get("close_status") for r in rows]),
            "evidence": evidence_label(counts(rows)["n_games"])}


def build_arm_scorecard(game_rows: list, contract_rows: list, *, evaluation_version: str | None = None) -> dict:
    if evaluation_version:
        game_rows = [r for r in game_rows if r.get("evaluation_version") == evaluation_version]
        contract_rows = [r for r in contract_rows if r.get("evaluation_version") == evaluation_version]
    gv, cv = views(game_rows), views(contract_rows)
    sc = {"preregistration": R.preregistration(), "preregistration_sha": R.preregistration_sha(),
          "evaluation_version": evaluation_version, "primary_sample_unit": "latest_pregame",
          "min_games_for_verdict": R.MIN_GAMES_FOR_VERDICT,
          "sample_units": {k: {**counts(rows), **{kk: vv for kk, vv in meta.items() if kk != "unavailable_examples"}}
                           for k, (rows, meta) in gv.items()},
          "contract_sample_units": {k: {**counts(rows)} for k, (rows, _m) in cv.items()},
          "games": {k: game_block(rows) for k, (rows, _m) in gv.items()},
          "contracts": {k: contract_block(rows) for k, (rows, _m) in cv.items()},
          "no_automatic_learning": ("this scorecard measures, reports and diagnoses; it changes no weight, feature, "
                                    "threshold or gate, and promotion requires a separate owner-approved project")}
    primary = sc["games"]["latest_pregame"]
    sc["headline_evidence"] = primary["evidence"]
    sc["headline_n_games"] = primary["n_games"]
    return sc
