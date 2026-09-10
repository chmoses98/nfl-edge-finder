"""Arm evaluation records: what each arm said, what happened, and what the market said at the snapshot and at the close.

Two record kinds, both write-once under `data/shadow/arm_evaluations/<game_id>/`:

    arm_game_evaluations      one per three-arm GAME record: centre errors per arm, market-at-snapshot, the
                              closing market centre, deviations and movement toward the close
    arm_contract_evaluations  one per three-arm CONTRACT record: the three probabilities, the incumbent's own
                              number, the settlement proven by the incumbent engine, the strict pregame close

The pregame values are copied VERBATIM from the arm records (never recomputed), the settlement comes from
`nfl_edge.settlement.settle.settle_observation` (the same engine the incumbent corpus uses), and the close is
`nfl_edge.shadow.evaluation.pick_close` (strictly before kickoff, or MISSING_CLOSE). The closing market CENTRE
is the incumbent's own `implied_game_lines` fit over the closing quotes, so "the market at close" is measured
the way the incumbent measures "the market at a snapshot".

Both records keep `prediction_id` (= the arm record id) so the generic write-once store applies unchanged.
"""
from __future__ import annotations

from datetime import datetime, timezone

import numpy as np

from nfl_edge.arms import registry as R
from nfl_edge.pricing.game_env import simulate_game
from nfl_edge.pricing.market_implied import implied_game_lines
from nfl_edge.settlement import settle as S
from nfl_edge.shadow.evaluation import (
    CLOSE_INCOMPLETE, CLOSE_MAX_STALENESS_S, CLOSE_OK, CLOSE_OK_STALE, MISSING_CLOSE, close_staleness, pick_close,
)

GAME_SUFFIX = "arm_game_evaluations"
CONTRACT_SUFFIX = "arm_contract_evaluations"
ARM_ATTR = {R.CURRENT: "current", R.DATA_ONLY: "data_only", R.HYBRID: "hybrid"}


def disagreement_band(points):
    if points is None:
        return None
    x = abs(float(points))
    for edge, label in R.DISAGREEMENT_BANDS_POINTS:
        if x <= edge:
            return label
    return R.DISAGREEMENT_BANDS_POINTS[-1][1]


def movement(arm_center, market_center, close_center, tol=1e-9):
    """Did the challenger's deviation from the snapshot market point toward where the market closed?"""
    if arm_center is None or market_center is None:
        return "no_view"
    if close_center is None:
        return "no_close"
    view = arm_center - market_center
    move = close_center - market_center
    if abs(view) <= tol:
        return "no_view"
    if abs(move) <= tol:
        return "unchanged"
    return "toward" if (view > 0) == (move > 0) else "away"


def closing_center(close_quotes: dict, contracts: list, bank, home: str, away: str, *, nsims: int = 12000) -> dict:
    """The market's closing (spread, total) as the incumbent would measure it: `implied_game_lines` over the last
    complete pregame quote of each liquid winner/spread/total contract."""
    by_ticker = {c["ticker"]: c for c in contracts}
    rows, n_used = [], 0
    for t, q in close_quotes.items():
        c = by_ticker.get(t)
        if not c or q is None:
            continue
        rows.append({"family": c.get("family"), "period": c.get("period"), "team": c.get("team"),
                     "threshold": c.get("threshold"), "floor_strike": c.get("floor_strike"),
                     "yes_bid": q.get("yes_bid"), "yes_ask": q.get("yes_ask"), "volume": q.get("volume")})
        n_used += 1
    if not rows:
        return {"status": MISSING_CLOSE, "reason": "no closing quotes for this game's contracts", "n_quotes": 0}
    s, t, diag = implied_game_lines(rows, bank, simulate_game, home, away, nsims=nsims)
    if s is None:
        return {"status": MISSING_CLOSE, "reason": diag.get("reason"), "n_quotes": n_used, "diag": diag}
    obs = [q.get("observed_ts") for q in close_quotes.values() if q]
    return {"status": CLOSE_OK, "margin": float(s), "total": float(t), "n_quotes": n_used, "diag": diag,
            "method": "implied_game_lines over the last complete pregame quotes (incumbent estimator)",
            "latest_quote_observed_ts": max(obs) if obs else None}


def evaluate_game(rec: dict, game, close_center_info: dict, *, evaluation_version: str = R.ARM_EVALUATION_VERSION,
                  now: datetime | None = None) -> dict:
    """One arm game record + the proven result + the closing centre -> one immutable evaluation row."""
    now = now or datetime.now(timezone.utc)
    hs, aws = game.home_score, game.away_score
    am = None if hs is None or aws is None else float(hs - aws)
    at = None if hs is None or aws is None else float(hs + aws)
    cur = (rec.get("arms") or {}).get(R.CURRENT) or {}
    market = {"margin": cur.get("projected_home_margin"), "total": cur.get("projected_total"),
              "source": cur.get("center_source"), "data_quality_state": cur.get("data_quality_state")}
    close_m = close_center_info.get("margin"); close_t = close_center_info.get("total")
    out = {"prediction_id": rec["record_id"], "record_kind": "game", "evaluation_version": evaluation_version,
           "evaluated_at": now.isoformat(), "arms_version": rec.get("arms_version"), "run_id": rec.get("run_id"),
           "observed_at": rec.get("observed_at"), "minutes_to_kickoff": rec.get("minutes_to_kickoff"),
           "game_id": rec.get("game_id"), "season": rec.get("season"), "week": rec.get("week"),
           "home_team": rec.get("home_team"), "away_team": rec.get("away_team"), "kickoff_at": rec.get("kickoff_at"),
           "prekickoff": rec.get("prekickoff"), "record_status": rec.get("status"),
           "reproduction_ok": (rec.get("reproduction_check") or {}).get("ok"),
           "actual": {"home_score": hs, "away_score": aws, "margin": am, "total": at, "overtime": game.overtime,
                      "home_won": None if am is None else bool(am > 0), "final_proofs": list(game.final_proofs),
                      "source": game.source},
           "market_at_snapshot": market,
           "close": {k: v for k, v in close_center_info.items() if k != "diag"},
           "arms": {}}
    for arm_id, a in (rec.get("arms") or {}).items():
        m, t = a.get("projected_home_margin"), a.get("projected_total")
        row = {"status": a.get("status"), "unavailable_reason": a.get("unavailable_reason"),
               "projected_home_margin": m, "projected_total": t,
               "simulation_center_margin": a.get("simulation_center_margin"),
               "simulation_center_total": a.get("simulation_center_total"),
               "implied_home_score": a.get("implied_home_score"), "implied_away_score": a.get("implied_away_score"),
               "center_source": a.get("center_source"), "data_quality_state": a.get("data_quality_state"),
               "p_home_win": (a.get("simulation") or {}).get("p_home_win"),
               "p_tie": (a.get("simulation") or {}).get("p_tie")}
        if m is not None and am is not None:
            row.update({"margin_error": m - am, "margin_abs_error": abs(m - am), "margin_sq_error": (m - am) ** 2})
        if t is not None and at is not None:
            row.update({"total_error": t - at, "total_abs_error": abs(t - at), "total_sq_error": (t - at) ** 2})
        if a.get("implied_home_score") is not None and hs is not None:
            row["home_score_error"] = a["implied_home_score"] - float(hs)
            row["away_score_error"] = a["implied_away_score"] - float(aws)
        if row.get("p_home_win") is not None and am is not None and am != 0:
            y = 1.0 if am > 0 else 0.0
            p = min(max(float(row["p_home_win"]), 1e-9), 1 - 1e-9)
            row["home_win_brier"] = (p - y) ** 2
            row["home_win_log_loss"] = -(y * np.log(p) + (1 - y) * np.log(1 - p))
        if arm_id != R.CURRENT and m is not None and market["margin"] is not None:
            dm = m - market["margin"]; dt = t - market["total"]
            row.update({"margin_minus_market": dm, "total_minus_market": dt,
                        "margin_disagreement_band": disagreement_band(dm), "total_disagreement_band": disagreement_band(dt),
                        "margin_movement_vs_close": movement(m, market["margin"], close_m),
                        "total_movement_vs_close": movement(t, market["total"], close_t)})
            if am is not None:
                row["margin_closer_than_market"] = abs(m - am) < abs(market["margin"] - am)
                row["total_closer_than_market"] = abs(t - at) < abs(market["total"] - at)
        out["arms"][arm_id] = row
    if close_m is not None and am is not None:
        out["close"]["margin_error"] = close_m - am; out["close"]["margin_abs_error"] = abs(close_m - am)
        out["close"]["total_error"] = close_t - at; out["close"]["total_abs_error"] = abs(close_t - at)
    if market["margin"] is not None and am is not None:
        out["market_at_snapshot"].update({"margin_error": market["margin"] - am, "margin_abs_error": abs(market["margin"] - am),
                                          "margin_sq_error": (market["margin"] - am) ** 2,
                                          "total_error": market["total"] - at, "total_abs_error": abs(market["total"] - at),
                                          "total_sq_error": (market["total"] - at) ** 2})
    return out


def evaluate_contract(rec: dict, book, close: dict | None, kickoff_ts, *, evaluation_version: str = R.ARM_EVALUATION_VERSION,
                      close_candidates_seen: int | None = None, now: datetime | None = None,
                      max_close_staleness_s: float = CLOSE_MAX_STALENESS_S) -> dict:
    """One arm contract record -> settlement (incumbent engine) + strict pregame close + the three arms verbatim."""
    now = now or datetime.now(timezone.utc)
    obs = {k: rec.get(k) for k in ("ticker", "family", "period", "game_id", "team", "threshold", "operator",
                                   "floor_strike", "direction")}
    st = S.settle_observation(obs, book)
    out = {"prediction_id": rec["record_id"], "record_kind": "contract", "evaluation_version": evaluation_version,
           "evaluated_at": now.isoformat(), "game_record_id": rec.get("game_record_id"), "arms_version": rec.get("arms_version"),
           "run_id": rec.get("run_id"), "observed_at": rec.get("observed_at"), "minutes_to_kickoff": rec.get("minutes_to_kickoff"),
           "game_id": rec.get("game_id"), "season": rec.get("season"), "week": rec.get("week"), "kickoff_at": rec.get("kickoff_at"),
           "ticker": rec.get("ticker"), "family": rec.get("family"), "period": rec.get("period"), "team": rec.get("team"),
           "threshold": rec.get("threshold"), "floor_strike": rec.get("floor_strike"), "operator": rec.get("operator"),
           "arm_status": rec.get("arm_status"),
           "p_current": rec.get("p_current"), "p_data_only": rec.get("p_data_only"), "p_hybrid": rec.get("p_hybrid"),
           "cv_current": rec.get("cv_current"), "cv_data_only": rec.get("cv_data_only"), "cv_hybrid": rec.get("cv_hybrid"),
           "incumbent_contract_value": rec.get("incumbent_contract_value"),
           "yes_bid_t": rec.get("yes_bid"), "yes_ask_t": rec.get("yes_ask"), "mid_t": rec.get("mid"),
           "width_t": rec.get("quote_width"), "volume_t": rec.get("volume"), "liquidity_t": rec.get("liquidity"),
           "settlement_status": st.status, "settled_yes": st.settled_yes, "settlement_kind": st.kind,
           "settlement_reason": st.reason, "settlement_evidence": st.evidence,
           "event_binary_valid": st.kind == S.KIND_BINARY,
           "exact_payout_known": st.kind in (S.KIND_BINARY, S.KIND_TIE_SPLIT, S.KIND_SCALAR_EXACT),
           "close_status": MISSING_CLOSE, "close_mid": None, "close_yes_bid": None, "close_yes_ask": None,
           "close_observed_at": None, "close_minutes_to_kickoff": None, "close_is_stale": None,
           "close_candidates_seen": close_candidates_seen}
    if not close:
        return out
    cb, ca = close.get("yes_bid"), close.get("yes_ask")
    if cb is None or ca is None:
        out["close_status"] = CLOSE_INCOMPLETE
        return out
    gap_s, stale = close_staleness(close, kickoff_ts, max_close_staleness_s)
    out.update({"close_status": CLOSE_OK_STALE if stale else CLOSE_OK, "close_is_stale": stale,
                "close_yes_bid": cb, "close_yes_ask": ca, "close_mid": (cb + ca) / 2.0,
                "close_observed_at": close.get("observed_at"),
                "close_minutes_to_kickoff": (gap_s / 60.0) if gap_s is not None else close.get("minutes_to_kickoff")})
    return out
