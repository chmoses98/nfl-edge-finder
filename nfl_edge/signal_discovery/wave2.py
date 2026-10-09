"""Football Signal Discovery Lab, Wave 2 (NFL): prospective confirmation. RESEARCH ONLY. PURE.

Frozen in docs/research/FOOTBALL_SIGNAL_DISCOVERY_WAVE2_PROTOCOL.md and research/signal_discovery_wave2/candidates.json:

* NFL-PROP-PROS-001 RB_RECEPTIONS_NO_STRUCTURE -- NO on the natural KXNFLREC rung of eligible RB ladders.
* NFL-PROP-PROS-002 ROLE_CHANGE_MODEL_ADVANTAGE -- frozen Wave-1 projection vs the ladder median, ROLE_CHANGE only.
* NFL-GAME-PROS-001 TOTALS_DISAGREEMENT_WF -- the frozen WF-TOTAL fold against the Kalshi total ladder at
  NFL_PRIMARY_60_180.

Pure functions of captured rows and frozen artifacts. Records are write-once (OBSERVATION before kickoff, ENTRY from
pre-kickoff quotes, SETTLEMENT after the final). No probability, fair price, stake or recommendation is produced and
no verdict beyond the frozen research states exists; EDGE_CONFIRMED is never one of them.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import math
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import numpy as np

from nfl_edge.signal_discovery.markets import MAX_WIDTH, ladder_median

CANDIDATES_PATH = Path("research/signal_discovery_wave2/candidates.json")
MODELS_DIR = Path("research/signal_discovery_wave2/models")
#: pinned at registration (191230a8) and artifact (e2016ee8) commits; never edit the files
CANDIDATES_SHA256 = "5f31bd3b7c45316eadb4eb754dd4ca2e2b51981ec6ffca89835704a38e0f3436"
WF_TOTAL_SHA256 = "37baf8ec94b569350f011cf0eefa5f1dcbff06bc45bfb8eb13083b07c786fe98"
PROP_MODELS_SHA256 = "7e308d26c3e042dd811857c3c400fe6a6e05eab2f77e459823c16045ba83c6f9"
CLASSIFIER_SHA256 = "eeec37774ca4309c018205aa0d4a7a3f3d122f86f197e4e98ac845b05936a981"
VERSION = "nfl-signal-discovery-wave2/1.0.0"
SPORT = "NFL"
SEASON = 2026
WEEK_ON_OR_AFTER = 6

PROP_001 = "NFL-PROP-PROS-001"
PROP_002 = "NFL-PROP-PROS-002"
GAME_001 = "NFL-GAME-PROS-001"
STREAMS = (PROP_001, PROP_002, GAME_001)
RB_FAMILY = "RB_receptions"
ROLE_FAMILIES = (
    "QB_pass_yards", "QB_attempts", "QB_completions", "RB_carries", "RB_rush_yards", "RB_receptions", "RB_rec_yards",
    "WR_receptions", "WR_rec_yards", "TE_receptions", "TE_rec_yards",
)
TOTAL_SERIES = "KXNFLTOTAL"
#: the Kalshi capture stats any stream reads (RB receptions + the eleven ROLE_CHANGE families' kalshi_stat)
STREAM_KALSHI_STATS = ("passing_yards", "attempts", "completions", "carries", "rushing_yards", "receptions", "receiving_yards")

OBSERVE_FROM_MIN, OBSERVE_UNTIL_MIN = 300.0, 20.0
PRIMARY_OPEN_MIN, PRIMARY_CLOSE_MIN = 180.0, 60.0
PROP_CHECKPOINT_HOURS = 24.0
TOTAL_THRESHOLD = 2.0
WAVE1_ECON_MARGIN = 0.10  # Wave-1 prop economic rule (secondary for ROLE_CHANGE only)
ACCEPTED_IDENTITY = ("RESOLVED_NAME_TEAM", "RESOLVED_NAME_TEAM_JERSEY")
SETTLEMENT_GIVE_UP_HOURS = 168.0

PENDING = "PENDING"
ELIGIBLE = "ELIGIBLE"
ENTRY_UNAVAILABLE = "ENTRY_UNAVAILABLE"
MARKET_NOT_OFFERED = "MARKET_NOT_OFFERED"
ORIENTATION_FAILURE = "ORIENTATION_FAILURE"
IDENTITY_FAILURE = "IDENTITY_FAILURE"
FEE_UNAVAILABLE = "FEE_UNAVAILABLE"
SETTLEMENT_PENDING = "SETTLEMENT_PENDING"
SETTLED = "SETTLED"
EXCLUDED_PROTOCOL = "EXCLUDED_PROTOCOL"
SYSTEM_FAILURE = "SYSTEM_FAILURE"
ROW_STATUSES = (PENDING, ELIGIBLE, ENTRY_UNAVAILABLE, MARKET_NOT_OFFERED, ORIENTATION_FAILURE, IDENTITY_FAILURE,
                FEE_UNAVAILABLE, SETTLEMENT_PENDING, SETTLED, EXCLUDED_PROTOCOL, SYSTEM_FAILURE)
PROSPECTIVE_TRACKING = "PROSPECTIVE_TRACKING"
EARLY_READ = "EARLY_READ"
INTERIM = "INTERIM"
PRIMARY_REVIEW = "PRIMARY_REVIEW"
REJECTED = "REJECTED"
REVIEW_REQUIRED = "REVIEW_REQUIRED"
VERDICT_STATES = (PROSPECTIVE_TRACKING, EARLY_READ, INTERIM, PRIMARY_REVIEW, REJECTED, REVIEW_REQUIRED)
READS: dict[str, dict[int, str]] = {
    PROP_001: {50: EARLY_READ, 100: INTERIM, 200: INTERIM, 300: PRIMARY_REVIEW},
    PROP_002: {50: EARLY_READ, 100: INTERIM, 200: PRIMARY_REVIEW},
    GAME_001: {25: EARLY_READ, 50: INTERIM, 100: INTERIM, 200: PRIMARY_REVIEW},
}
NO_SETTLED_SAMPLE = "NO SETTLED SAMPLE"
N_BOOT = 4000
SEED = 20261015
RECORD_PREFIX = "data/research/signal_lab_wave2"
OBSERVATION, ENTRY, SETTLEMENT = "OBSERVATION", "ENTRY", "SETTLEMENT"
RECORD_DIRS = {OBSERVATION: "observations", ENTRY: "entries", SETTLEMENT: "settlements"}


class FrozenMismatch(RuntimeError):
    """A pre-registered file or artifact is not the registered one."""


def canonical_sha(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def load_frozen(root: Path) -> dict[str, Any]:
    """Candidates + both model artifacts + the classifier source, each checked against its pinned hash."""
    cand = json.loads((root / CANDIDATES_PATH).read_text())
    if cand.get("status") != "PRE-REGISTERED" or canonical_sha(cand) != CANDIDATES_SHA256:
        raise FrozenMismatch("candidates are not the registered file")
    if cand["population"]["week_on_or_after"] != WEEK_ON_OR_AFTER or tuple(cand["row_statuses"]) != ROW_STATUSES:
        raise FrozenMismatch("population or statuses differ from the registration")
    if cand["streams"][PROP_002]["families"] != list(ROLE_FAMILIES):
        raise FrozenMismatch("ROLE_CHANGE families differ from the registration")
    for sid, reads in READS.items():
        if {int(k): v.split(" ")[0] for k, v in cand["streams"][sid]["reads"].items()} != reads:
            raise FrozenMismatch(f"{sid} reads differ from the registration")
    total = json.loads((root / MODELS_DIR / "wf_total_2026.json").read_text())
    props = json.loads((root / MODELS_DIR / "prop_models_2026.json").read_text())
    if canonical_sha(total) != WF_TOTAL_SHA256 or canonical_sha(props) != PROP_MODELS_SHA256:
        raise FrozenMismatch("a model artifact differs from the committed, hashed one")
    if total["pick_threshold_points"] != TOTAL_THRESHOLD:
        raise FrozenMismatch("WF-TOTAL threshold differs")
    if classifier_sha() != CLASSIFIER_SHA256:
        raise FrozenMismatch("the ROLE_STABILITY classifier source changed")
    return {"candidates": cand, "wf_total": total, "props": props}


def classifier_sha() -> str:
    from nfl_edge.signal_discovery import player_features as P

    return hashlib.sha256((inspect.getsource(P._primary_share) + inspect.getsource(P._role_stability)).encode()).hexdigest()


# --------------------------------------------------------------------------- ladders


def valid(bid: float | None, ask: float | None) -> bool:
    """Wave-1 `markets._valid`: 0 < bid <= ask < 1 and width <= 0.10."""
    return bid is not None and ask is not None and 0 < bid <= ask < 1 and (ask - bid) <= MAX_WIDTH


def executable(price: float | None) -> bool:
    if price is None:
        return False
    cents = round(price * 100)
    return abs(price * 100 - cents) <= 1e-6 and 1 <= cents <= 99


def ladder(rungs: list[dict[str, Any]]) -> dict[str, Any]:
    """rungs: {threshold, yes_bid, yes_ask, no_bid, no_ask, ticker, ...} at the checkpoint.

    Market median = Wave-1 ladder_median over valid mids; natural rung = smallest |mid - 0.5|, TIE -> lowest
    threshold (frozen in Wave 2). Missing stays missing."""
    pts = [(float(r["threshold"]), (r["yes_bid"] + r["yes_ask"]) / 2, r) for r in rungs if r.get("threshold") is not None and valid(r.get("yes_bid"), r.get("yes_ask"))]
    med = ladder_median([(t, p) for t, p, _ in pts]) if pts else None
    nat = None
    if pts:
        t, p, r = min(pts, key=lambda x: (abs(x[1] - 0.5), x[0]))
        nat = {"threshold": t, "mid": p, "ticker": r["ticker"], "yes_ask": r.get("yes_ask"), "no_ask": r.get("no_ask"),
               "yes_bid": r.get("yes_bid"), "no_bid": r.get("no_bid"), "confirmed_at": r.get("confirmed_at")}
    return {"rungs": len(rungs), "valid_rungs": len(pts), "market_median": med, "natural": nat,
            "rungs_used": [{"threshold": t, "mid": round(p, 6), "ticker": r["ticker"]} for t, p, r in sorted(pts, key=lambda x: x[0])]}


def contract(nat: dict[str, Any] | None, side: str, fee_fn) -> dict[str, Any]:
    """`side` 'yes'|'no' on the natural rung at its OWN captured ask (NO is never 1 - YES)."""
    if nat is None:
        return {"status": ENTRY_UNAVAILABLE, "reason": "NO_VALID_RUNG"}
    ask = nat["yes_ask"] if side == "yes" else nat["no_ask"]
    base = {"ticker": nat["ticker"], "threshold": nat["threshold"], "contract_side": side, "ask": ask,
            "quote_confirmed_at": nat.get("confirmed_at")}
    if not executable(ask):
        return {**base, "status": ENTRY_UNAVAILABLE, "reason": "QUOTE_NOT_EXECUTABLE", "fee": None}
    fee, state = fee_fn(ask)
    if fee is None:
        return {**base, "status": FEE_UNAVAILABLE, "reason": f"FEE_{state}", "fee": None}
    return {**base, "status": ELIGIBLE, "reason": None, "fee": float(fee)}


def contract_pays_by_stat(c: dict[str, Any], value: float) -> bool:
    """Threshold t means stat >= t (floor t - 0.5): YES iff value >= t, NO iff value < t. No push."""
    return value >= c["threshold"] if c["contract_side"] == "yes" else value < c["threshold"]


def contract_value_by_exchange(c: dict[str, Any], yes_payout: float) -> float:
    """Settlement value of the bought side from the exchange's exact YES payout (binary or published scalar)."""
    return yes_payout if c["contract_side"] == "yes" else 1.0 - yes_payout


def economics(c: dict[str, Any], value: float | None) -> dict[str, Any]:
    if c.get("status") != ELIGIBLE:
        return {"available": False, "reason": c.get("reason") or c.get("status")}
    if value is None:
        return {"available": False, "reason": SETTLEMENT_PENDING}
    outlay = c["ask"] + c["fee"]
    return {"available": True, "entry_price": c["ask"], "fee": c["fee"], "outlay": round(outlay, 6),
            "settlement_value": value, "fee_adjusted_pnl": round(value - outlay, 6)}


def clv(close: dict[str, Any] | None, c: dict[str, Any]) -> dict[str, Any]:
    """Side-aware CLV of a contract: the SAME ticker's SAME-side ask at the canonical close (close-2.1.0) minus the
    entry ask. A missing or non-executable close stays missing (never 0)."""
    if c.get("status") != ELIGIBLE or not close or close.get("close_status") not in ("CLOSE_OK", "CLOSE_ONE_SIDED"):
        return {"clv": None, "close_ask": None, "reason": "CLV_CLOSE_MISSING" if c.get("status") == ELIGIBLE else c.get("status")}
    ask = close.get("yes_ask") if c["contract_side"] == "yes" else close.get("no_ask")
    if not executable(ask):
        return {"clv": None, "close_ask": None, "reason": "CLOSE_SIDE_NOT_EXECUTABLE"}
    return {"clv": round(ask - c["ask"], 6), "close_ask": ask, "close_confirmed_at": close.get("confirmed_at"),
            "close_quality": close.get("close_quality"), "reason": None}


# --------------------------------------------------------------------------- checkpoints


def prop_checkpoint_ok(close: dict[str, Any], kickoff_ts: float) -> bool:
    """LAST_VALID_PREKICK_QUOTE_24H acceptance of a close-2.1.0 record."""
    if close.get("close_status") not in ("CLOSE_OK", "CLOSE_ONE_SIDED"):
        return False
    from datetime import datetime

    ca = close.get("confirmed_at")
    if not ca:
        return False
    t = datetime.fromisoformat(str(ca).replace("Z", "+00:00")).timestamp()
    return kickoff_ts - PROP_CHECKPOINT_HOURS * 3600 < t < kickoff_ts


# --------------------------------------------------------------------------- WF-TOTAL translation


def total_prediction(artifact: dict[str, Any], football: dict[str, Any], market_total: float | None) -> float | None:
    """p = artifact(features) with m.total := market_implied_total (gap.total = baseline.total - market total)."""
    from nfl_edge.signal_discovery.wave2_models import predict_wf_total

    if market_total is None or football.get("baseline.total") is None:
        return None
    feats = {**football, "gap.total": float(football["baseline.total"]) - float(market_total)}
    return predict_wf_total(artifact, feats)


# --------------------------------------------------------------------------- statistics and verdicts


def _cluster_boot(values: list[float], clusters: list[str], ratio_den: list[float] | None = None) -> list[float] | None:
    if len(values) < 2:
        return None
    ids = sorted(set(clusters))
    if len(ids) < 2:
        return None
    idx = {c: [i for i, k in enumerate(clusters) if k == c] for c in ids}
    v = np.asarray(values, float)
    d = np.asarray(ratio_den, float) if ratio_den is not None else None
    rng = np.random.default_rng(SEED)
    out = []
    for _ in range(N_BOOT):
        pick = rng.integers(0, len(ids), size=len(ids))
        rows = [i for j in pick for i in idx[ids[j]]]
        out.append(v[rows].sum() / d[rows].sum() if d is not None else v[rows].mean())
    return [float(np.quantile(out, 0.025)), float(np.quantile(out, 0.975))]


def wilson(k: int, n: int) -> list[float] | None:
    if n == 0:
        return None
    z = 1.959963984540054
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [c - h, c + h]


def verdict(stream: str, n: int, primary_value: float | None) -> str:
    state = PROSPECTIVE_TRACKING
    for k in sorted(READS[stream]):
        if n >= k:
            state = READS[stream][k]
    if state != PRIMARY_REVIEW:
        return state
    return REJECTED if primary_value is not None and primary_value <= 0 else REVIEW_REQUIRED


def next_read(stream: str, n: int) -> dict[str, Any] | None:
    for k in sorted(READS[stream]):
        if n < k:
            return {"at_n": k, "state": READS[stream][k], "remaining": k - n}
    return None


def summarize(stream: str, rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Cumulative read of one stream from its SETTLED rows. n 0 is NO SETTLED SAMPLE, never 0."""
    rows = [r for r in rows if r["signal_id"] == stream and r["status"] == SETTLED]
    if stream == PROP_001:
        priced = [r for r in rows if r["economics"].get("available")]
        n = len(priced)
        if n == 0:
            return {"n": 0, "display": NO_SETTLED_SAMPLE, "verdict": PROSPECTIVE_TRACKING, "next_read": next_read(stream, 0)}
        pnl = [r["economics"]["fee_adjusted_pnl"] for r in priced]
        out = [r["economics"]["outlay"] for r in priced]
        roi = sum(pnl) / sum(out)
        played = [r for r in priced if r.get("played")]
        res = {
            "n": n,
            "roi_on_outlay": roi,
            "roi_ci95_game_cluster": _cluster_boot(pnl, [r["game_id"] for r in priced], out),
            "hit_rate": sum(1 for r in priced if r["economics"]["settlement_value"] >= 0.999) / n,
            "mean_price": float(np.mean([r["economics"]["entry_price"] for r in priced])),
            "break_even": float(np.mean(out)),
            "played_only": {"n": len(played), "roi_on_outlay": (sum(r["economics"]["fee_adjusted_pnl"] for r in played) / sum(r["economics"]["outlay"] for r in played)) if played else None},
            "top5_player_share": _top_share([r["player_id"] for r in priced], 5),
        }
        res["verdict"] = verdict(stream, n, roi)
        res["next_read"] = next_read(stream, n)
        return res
    if stream == PROP_002:
        by_pg: dict[tuple[str, str], list[float]] = {}
        for r in rows:
            by_pg.setdefault((r["game_id"], r["player_id"]), []).append(r["d"])
        n = len(by_pg)
        if n == 0:
            return {"n": 0, "display": NO_SETTLED_SAMPLE, "verdict": PROSPECTIVE_TRACKING, "next_read": next_read(stream, 0)}
        keys = sorted(by_pg)
        vals = [float(np.mean(by_pg[k])) for k in keys]
        mean_d = float(np.mean(vals))
        err_m = [abs(r["market_median"] - r["actual"]) for r in rows]
        err_p = [abs(r["model_median"] - r["actual"]) for r in rows]
        res = {
            "n": n,
            "n_ladders": len(rows),
            "mean_d_per_player_game": mean_d,
            "ci95_game_cluster": _cluster_boot(vals, [k[0] for k in keys]),
            "share_player_games_model_better": sum(1 for v in vals if v > 0) / n,
            "mae_market": float(np.mean(err_m)), "mae_model": float(np.mean(err_p)),
            "rmse_market": float(np.sqrt(np.mean(np.square(err_m)))), "rmse_model": float(np.sqrt(np.mean(np.square(err_p)))),
            "median_abs_error_market": float(np.median(err_m)), "median_abs_error_model": float(np.median(err_p)),
            "signed_residual_market": float(np.mean([r["actual"] - r["market_median"] for r in rows])),
            "signed_residual_model": float(np.mean([r["actual"] - r["model_median"] for r in rows])),
            "by_family": _by(rows, "family"),
            "by_position": _by(rows, "position"),
            "top5_player_share": _top_share([r["player_id"] for r in rows], 5),
            "top_team_share": _top_share([r["team"] for r in rows], 1),
        }
        res["verdict"] = verdict(stream, n, mean_d)
        res["next_read"] = next_read(stream, n)
        return res
    n = len(rows)
    if n == 0:
        return {"n": 0, "display": NO_SETTLED_SAMPLE, "verdict": PROSPECTIVE_TRACKING, "next_read": next_read(stream, 0)}
    sr = [r["signed_residual"] for r in rows]
    wins = sum(1 for v in sr if v > 0)
    decided = sum(1 for v in sr if v != 0)
    priced = [r for r in rows if r["economics"].get("available")]
    res = {
        "n": n,
        "mean_signed_residual": float(np.mean(sr)),
        "median_signed_residual": float(np.median(sr)),
        "ci95_bootstrap": _cluster_boot(sr, [r["game_id"] for r in rows]),
        "ats_like_rate": wins / decided if decided else None,
        "ats_like_ci95": wilson(wins, decided),
        "by_side": {s: sum(1 for r in rows if r["side"] == s) for s in ("OVER", "UNDER")},
        "economics": ({"n": len(priced), "roi_on_outlay": sum(r["economics"]["fee_adjusted_pnl"] for r in priced) / sum(r["economics"]["outlay"] for r in priced)}
                      if priced else {"n": 0, "display": NO_SETTLED_SAMPLE}),
    }
    res["verdict"] = verdict(stream, n, res["mean_signed_residual"])
    res["next_read"] = next_read(stream, n)
    return res


def _by(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k in sorted({r[key] for r in rows}):
        g = [r for r in rows if r[key] == k]
        out[k] = {"n": len(g), "mean_d": float(np.mean([r["d"] for r in g]))}
    return out


def _top_share(values: list[str], k: int) -> float | None:
    if not values:
        return None
    from collections import Counter

    return sum(c for _, c in Counter(values).most_common(k)) / len(values)
