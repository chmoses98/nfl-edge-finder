"""Football Signal Discovery Lab, Wave 2A (NFL): retrospective replay of the frozen Wave-2 streams. RESEARCH ONLY. PURE.

docs/research/FOOTBALL_SIGNAL_DISCOVERY_WAVE2A_PROTOCOL.md. The 2026 replay runs the Wave-2 job's own stages
(scripts/research/signal_lab_wave2a.py drives them); this module only reads the records they wrote, labels them,
and computes the descriptive replay statistics, the baselines and the robustness tables. Every rule and constant is
imported from `nfl_edge.signal_discovery.wave2` (frozen) -- nothing is restated, refit or re-chosen.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

import numpy as np

from nfl_edge.signal_discovery import wave2 as W

VERSION = "nfl-signal-discovery-wave2a/1.0.0"
FREEZE_UTC = "2026-10-08T22:30:58Z"  # Wave-2 pre-registration commit 191230a8
EVIDENCE_HISTORY = "RETROSPECTIVE_DISCOVERY_CORPUS"
EVIDENCE_2026 = "RETROSPECTIVE_2026_REPLAY"
EVIDENCE_PROSPECTIVE = "PROSPECTIVE_WAVE2"
REPLAY_WEEKS = (1, 2, 3, 4, 5)
OBSERVE_MINUTES_BEFORE = 300  # the earliest instant the frozen job may observe
ENTER_MINUTES_AFTER = 5
SETTLE_DAYS_AFTER = 8

HISTORICAL_REPLAY_UNAVAILABLE = "HISTORICAL_REPLAY_UNAVAILABLE"
INJURY_VINTAGE_UNAVAILABLE = "INJURY_VINTAGE_UNAVAILABLE"
SETTLEMENT_SOURCE_ARCHIVE = "EXCHANGE_RESULT_FROM_DISCOVERY_ARCHIVE"
ROSTER_NEAR_PIT = "ROSTER_NEAR_PIT"

#: independence of 2026 weeks 1-5 per stream (protocol section 2; audited in the results)
INDEPENDENCE = {
    W.PROP_001: "RETROSPECTIVE_DISCOVERY_CONTAMINATED",
    W.PROP_002: "PARTIALLY_INDEPENDENT",
    W.GAME_001: "OUT_OF_TIME_REPLAY",
}

# replay exclusion codes (the prompt's vocabulary); NOT_ELIGIBLE is a rule outcome, not an exclusion
EXCLUSION_FOR = {
    ("MARKET_NOT_OFFERED", None): "NO_MARKET",
    ("ENTRY_UNAVAILABLE", "NO_LADDER_AT_CHECKPOINT"): "NO_EXECUTABLE_QUOTE",
    ("ENTRY_UNAVAILABLE", "NO_VALID_RUNG"): "NO_EXECUTABLE_QUOTE",
    ("ENTRY_UNAVAILABLE", "NO_MARKET_MEDIAN"): "NO_EXECUTABLE_QUOTE",
    ("ENTRY_UNAVAILABLE", "NO_TOTAL_QUOTE_IN_PRIMARY_60_180"): "NO_PRIMARY_WINDOW_CAPTURE",
    ("ENTRY_UNAVAILABLE", "NO_MARKET_IMPLIED_TOTAL"): "NO_EXECUTABLE_QUOTE",
    ("ENTRY_UNAVAILABLE", "QUOTE_NOT_EXECUTABLE"): "NO_EXECUTABLE_QUOTE",
    ("FEE_UNAVAILABLE", None): "FEE_UNAVAILABLE",
    ("EXCLUDED_PROTOCOL", "ABS_PREDICTION_BELOW_2"): "NOT_ELIGIBLE",
    ("EXCLUDED_PROTOCOL", "FOOTBALL_FEATURE_MISSING"): "FEATURE_HISTORY_UNAVAILABLE",
    ("EXCLUDED_PROTOCOL", "DID_NOT_PLAY"): "SETTLEMENT_UNAVAILABLE",
    ("SYSTEM_FAILURE", "INJURY_VINTAGE_UNAVAILABLE"): INJURY_VINTAGE_UNAVAILABLE,
    ("SYSTEM_FAILURE", "NO_OBSERVATION_BEFORE_KICKOFF"): "RULE_NOT_RECONSTRUCTABLE",
    ("SETTLEMENT_PENDING", None): "SETTLEMENT_UNAVAILABLE",
}


class ReplayIntegrityError(RuntimeError):
    """A replay would write the prospective store or read a post-kickoff input."""


def exclusion(status: str, reason: str | None) -> str | None:
    if status in (W.ELIGIBLE, W.SETTLED, W.PENDING):
        return None
    return EXCLUSION_FOR.get((status, reason)) or EXCLUSION_FOR.get((status, None)) or "RULE_NOT_RECONSTRUCTABLE"


def assert_not_prospective_publish(path: str) -> None:
    """Replay records may live in a scratch directory or under research/signal_discovery_wave2a only -- never in a
    market-data checkout (whose data/research/signal_lab_wave2/ tree is the prospective store)."""
    text = str(path).replace("\\", "/")
    if "/.git/" in text or text.rstrip("/").endswith("market-data") or "/md/data/research" in text:
        raise ReplayIntegrityError(f"replay output may not be written into a market-data tree: {text}")


# --------------------------------------------------------------------------- statistics


def _boot_ratio(pnl: list[float], outlay: list[float], clusters: list[str]) -> list[float] | None:
    """Game-clustered bootstrap of sum(pnl)/sum(outlay), the Wave-2 seed and draw count."""
    if len(pnl) < 2:
        return None
    by: dict[str, list[int]] = defaultdict(list)
    for i, c in enumerate(clusters):
        by[c].append(i)
    keys = sorted(by)
    rng = np.random.default_rng(W.SEED)
    p, o = np.asarray(pnl, float), np.asarray(outlay, float)
    ps = np.array([p[by[k]].sum() for k in keys])
    os_ = np.array([o[by[k]].sum() for k in keys])
    draws = rng.integers(0, len(keys), size=(W.N_BOOT, len(keys)))
    r = ps[draws].sum(axis=1) / os_[draws].sum(axis=1)
    return [float(np.quantile(r, 0.025)), float(np.quantile(r, 0.975))]


def _boot_mean(values: list[float], clusters: list[str]) -> list[float] | None:
    if len(values) < 2:
        return None
    by: dict[str, list[float]] = defaultdict(list)
    for v, c in zip(values, clusters, strict=True):
        by[c].append(v)
    keys = sorted(by)
    sums = np.array([sum(by[k]) for k in keys])
    ns = np.array([len(by[k]) for k in keys])
    rng = np.random.default_rng(W.SEED)
    draws = rng.integers(0, len(keys), size=(W.N_BOOT, len(keys)))
    m = sums[draws].sum(axis=1) / ns[draws].sum(axis=1)
    return [float(np.quantile(m, 0.025)), float(np.quantile(m, 0.975))]


def economics_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """rows: {pnl, outlay, win, price, game_id, ...} with a KNOWN fee. NO SETTLED SAMPLE when empty."""
    rows = [r for r in rows if r.get("pnl") is not None and r.get("outlay")]
    n = len(rows)
    if n == 0:
        return {"n": 0, "display": W.NO_SETTLED_SAMPLE}
    pnl = [r["pnl"] for r in rows]
    out = [r["outlay"] for r in rows]
    wins = sum(1 for r in rows if r["win"])
    return {
        "n": n,
        "wins": wins,
        "win_rate": wins / n,
        "win_rate_ci95": W.wilson(wins, n),
        "mean_price": float(np.mean([r["price"] for r in rows])),
        "mean_fee": float(np.mean([r["fee"] for r in rows])),
        "outlay": round(sum(out), 4),
        "fee_adjusted_pnl": round(sum(pnl), 4),
        "roi": sum(pnl) / sum(out),
        "roi_ci95_game_cluster": _boot_ratio(pnl, out, [r["game_id"] for r in rows]),
        "games": len({r["game_id"] for r in rows}),
    }


def roi_by(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    out = {}
    for g in sorted({str(r.get(key)) for r in rows}):
        sub = [r for r in rows if str(r.get(key)) == g]
        pnl, outl = sum(r["pnl"] for r in sub), sum(r["outlay"] for r in sub)
        out[g] = {"n": len(sub), "wins": sum(1 for r in sub if r["win"]), "pnl": round(pnl, 4), "roi": pnl / outl if outl else None}
    return out


def roi_without(rows: list[dict[str, Any]], key: str, top: int = 1) -> dict[str, Any] | None:
    """ROI after removing the `top` groups of `key` with the largest P/L (the best contributors)."""
    tot: dict[str, float] = defaultdict(float)
    for r in rows:
        tot[str(r.get(key))] += r["pnl"]
    if len(tot) <= top:
        return None
    best = sorted(tot, key=lambda g: (-tot[g], g))[:top]
    rest = [r for r in rows if str(r.get(key)) not in best]
    pnl, outl = sum(r["pnl"] for r in rest), sum(r["outlay"] for r in rest)
    return {"removed": best, "n": len(rest), "roi": pnl / outl if outl else None}


def leave_one_out_roi(rows: list[dict[str, Any]], key: str) -> dict[str, Any] | None:
    groups = sorted({str(r.get(key)) for r in rows})
    if len(groups) < 2:
        return None
    res = {}
    for g in groups:
        rest = [r for r in rows if str(r.get(key)) != g]
        o = sum(r["outlay"] for r in rest)
        res[g] = sum(r["pnl"] for r in rest) / o if o else None
    lo = min(res, key=lambda k: res[k])
    hi = max(res, key=lambda k: res[k])
    return {"min": res[lo], "min_without": lo, "max": res[hi], "max_without": hi}


def concentration_roi(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"display": W.NO_SETTLED_SAMPLE}
    pc = Counter(r["player_id"] for r in rows)
    tc = Counter(r["team"] for r in rows)
    return {
        "by_week": roi_by(rows, "week"),
        "leave_one_week_out": leave_one_out_roi(rows, "week"),
        "leave_one_team_out": leave_one_out_roi(rows, "team"),
        "without_top_player": roi_without(rows, "player_id", 1),
        "without_top5_players": roi_without(rows, "player_id", 5),
        "without_top_team": roi_without(rows, "team", 1),
        "without_top5_teams": roi_without(rows, "team", 5),
        "top_player_share": max(pc.values()) / len(rows),
        "top5_player_share": sum(v for _, v in pc.most_common(5)) / len(rows),
        "top_team_share": max(tc.values()) / len(rows),
    }


def paired_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """ROLE_CHANGE paired error, one averaged d per player-game (the frozen W.summarize unit)."""
    if not rows:
        return {"n": 0, "display": W.NO_SETTLED_SAMPLE}
    by: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        by[(r["game_id"], r["player_id"])].append(r)
    units = []
    for (gid, pid), rs in sorted(by.items()):
        units.append(
            {
                "game_id": gid,
                "player_id": pid,
                "team": rs[0].get("team"),
                "d": float(np.mean([r["d"] for r in rs])),
                "model_ae": float(np.mean([abs(r["model_median"] - r["actual"]) for r in rs])),
                "market_ae": float(np.mean([abs(r["market_median"] - r["actual"]) for r in rs])),
            }
        )
    d = [u["d"] for u in units]
    return {
        "n_player_games": len(units),
        "n_ladders": len(rows),
        "model_mae": float(np.mean([u["model_ae"] for u in units])),
        "market_mae": float(np.mean([u["market_ae"] for u in units])),
        "mean_d": float(np.mean(d)),
        "median_d": float(np.median(d)),
        "ci95_game_cluster": _boot_mean(d, [u["game_id"] for u in units]),
        "share_model_better": sum(1 for x in d if x > 0) / len(d),
        "share_tied": sum(1 for x in d if x == 0) / len(d),
        "units": units,
    }


def paired_without(units: list[dict[str, Any]], key: str, top: int) -> dict[str, Any] | None:
    tot: dict[str, float] = defaultdict(float)
    for u in units:
        tot[str(u.get(key))] += u["d"]
    if len(tot) <= top:
        return None
    best = sorted(tot, key=lambda g: (-tot[g], g))[:top]
    rest = [u["d"] for u in units if str(u.get(key)) not in best]
    return {"removed": best, "n": len(rest), "mean_d": float(np.mean(rest)) if rest else None}


def signed_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Totals: s * (actual - market_implied_total) per game."""
    if not rows:
        return {"n": 0, "display": W.NO_SETTLED_SAMPLE}
    res = [r["signed_residual"] for r in rows]
    hits = sum(1 for x in res if x > 0)
    losses = sum(1 for x in res if x < 0)
    return {
        "n": len(rows),
        "mean_signed_residual": float(np.mean(res)),
        "median_signed_residual": float(np.median(res)),
        "ci95_game_bootstrap": _boot_mean(res, [r["game_id"] for r in rows]),
        "hits": hits,
        "misses": losses,
        "pushes": len(rows) - hits - losses,
        "hit_rate": hits / (hits + losses) if hits + losses else None,
        "hit_rate_ci95": W.wilson(hits, hits + losses),
        "over_under": dict(Counter(r["side"] for r in rows)),
    }


# --------------------------------------------------------------------------- interpretation (protocol section 5)


def classify_prop001(econ: dict[str, Any]) -> str:
    n = econ.get("n", 0)
    if n < 30:
        return "INSUFFICIENT_REPLAY_DATA"
    roi, ci = econ["roi"], econ.get("roi_ci95_game_cluster")
    if roi > 0 and ci and ci[0] > 0:
        return "STRONGLY_SUPPORTIVE"
    if roi > 0:
        return "SUPPORTIVE"
    if ci and ci[1] < 0:
        return "UNSUPPORTIVE"
    return "MIXED"


def classify_prop002(p: dict[str, Any]) -> str:
    n = p.get("n_player_games", 0)
    if n < 30:
        return "INSUFFICIENT_REPLAY_DATA"
    ci = p.get("ci95_game_cluster")
    if p["mean_d"] > 0 and ci and ci[0] > 0:
        return "STRONGLY_SUPPORTIVE"
    if p["mean_d"] > 0 and p["share_model_better"] >= 0.5:
        return "SUPPORTIVE"
    if p["mean_d"] <= 0 and p["share_model_better"] < 0.5:
        return "UNSUPPORTIVE"
    return "MIXED"


def classify_game001(s: dict[str, Any]) -> str:
    n = s.get("n", 0)
    if n < 10:
        return "INSUFFICIENT_REPLAY_DATA"
    ci, rate, mean = s.get("ci95_game_bootstrap"), s.get("hit_rate"), s["mean_signed_residual"]
    if mean > 0 and ci and ci[0] > 0 and rate is not None and rate >= 0.524:
        return "STRONGLY_SUPPORTIVE"
    if mean > 0 and rate is not None and rate >= 0.5:
        return "SUPPORTIVE"
    if mean <= 0 and rate is not None and rate < 0.5:
        return "UNSUPPORTIVE"
    return "MIXED"


# --------------------------------------------------------------------------- baselines (descriptive)


def rung_pays_no(threshold: float, actual: float) -> bool:
    """NO on 'stat >= t' pays iff actual < t (the frozen contract_pays_by_stat convention)."""
    return actual < threshold


def no_every_valid_rung(ladder_rungs: list[dict[str, Any]], actual: float, fee_fn) -> list[dict[str, Any]]:
    """ALWAYS_NO_EVERY_VALID_RUNG for one ladder: NO at each valid rung's own captured NO ask."""
    out = []
    for r in ladder_rungs:
        if not W.valid(r.get("yes_bid"), r.get("yes_ask")):
            continue
        c = W.contract({**r, "threshold": r["threshold"]}, "no", fee_fn)
        if c["status"] != W.ELIGIBLE:
            continue
        win = rung_pays_no(float(r["threshold"]), actual)
        out.append(
            {
                "threshold": float(r["threshold"]),
                "price": c["ask"],
                "fee": c["fee"],
                "outlay": c["ask"] + c["fee"],
                "win": win,
                "pnl": (1.0 if win else 0.0) - c["ask"] - c["fee"],
            }
        )
    return out
