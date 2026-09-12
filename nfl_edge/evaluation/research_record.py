"""THE RESEARCH RECORD: one row per frozen projection, joined by immutable identity to its horizon market, its
canonical close, its CLV, its settlement, its point-in-time context and its autopsy.

Join key: `record_id` (sha of snapshot | ticker | arm | engine version | distribution version) -- never a title.
Each arm of the same contract at the same snapshot is its own row; the same contract across horizons is a row
per horizon. The row is DERIVED and rebuildable from the immutable corpora (projections + sidecars, closes, clv,
settlements, autopsy); nothing here writes back into them.

Bands (Part 9) are fixed here so every report cuts the same way:
    disagreement_band   |model_cv - horizon_mid| in probability points
    probability_band    model contract value in tenths
    price_band          horizon mid in tenths
    width_band          quote width
    liquidity_band      dollars resting
"""
from __future__ import annotations

DISAGREEMENT_BANDS = ((0.5, "0-0.5pp"), (1.0, "0.5-1pp"), (2.0, "1-2pp"), (3.0, "2-3pp"), (5.0, "3-5pp"), (10.0, "5-10pp"), (float("inf"), ">10pp"))
WIDTH_BANDS = ((0.02, "<=2c"), (0.05, "3-5c"), (0.10, "6-10c"), (0.20, "11-20c"), (float("inf"), ">20c"))
LIQUIDITY_BANDS = ((1e-9, "none"), (100.0, "<$100"), (1000.0, "$100-1k"), (10000.0, "$1k-10k"), (float("inf"), ">$10k"))
RECORD_VERSION = "research-record-1.0.0"


def _f(x):
    try:
        return None if x is None else float(x)
    except (TypeError, ValueError):
        return None


def band(v, bands, unknown="unknown"):
    v = _f(v)
    if v is None:
        return unknown
    for lim, name in bands:
        if v <= lim:
            return name
    return bands[-1][1]


def disagreement_band(pp):
    return band(abs(pp) if pp is not None else None, DISAGREEMENT_BANDS)


def tenth_band(p):
    p = _f(p)
    if p is None:
        return "unknown"
    i = min(int(p * 10), 9)
    return f"{i/10:.1f}-{(i+1)/10:.1f}"


def family_group(r: dict) -> str:
    """The market-family segmentation of Part 11: period markets and player statistics get their own groups."""
    fam, period, stat = r.get("market_family"), r.get("period") or "FULL", r.get("stat_family")
    if fam == "PLAYER_STAT":
        return f"player_{stat}"
    if period not in ("FULL", None, "SEASON", "EVENT"):
        return f"period_{fam.lower()}_{period}" if fam in ("SPREAD", "TOTAL", "TEAM_TOTAL", "PERIOD_WINNER", "BOTH_TEAMS_SCORE") else f"period_{fam.lower()}"
    if r.get("engine") == "SEASON":
        return "season"
    if r.get("engine") == "JOINT" or (r.get("question") or {}).get("kind") == "COMPOSITE":
        return "joint"
    return {"GAME_WINNER": "game_winner", "SPREAD": "spread", "TOTAL": "total", "TEAM_TOTAL": "team_total", "WIN_MARGIN_BUCKET": "margin_bucket",
            "BOTH_TEAMS_SCORE_N": "both_teams_score"}.get(fam, f"other_{fam}".lower())


def research_row(proj: dict, *, close: dict | None, clv: dict | None, settlement: dict | None, autopsy: dict | None,
                 sidecar: dict | None, crosscheck: dict | None = None, depth_pair: dict | None = None) -> dict:
    pc, gc, ms, hq, fl, dp = (proj.get(k) or {} for k in ("player_context", "game_context", "market_state", "horizon_quality", "flags", "depth"))
    sy = proj.get("information_sync") or {}
    h_mid = proj.get("mid")
    cv = proj.get("contract_value")
    dis_pp = (100.0 * (cv - h_mid)) if (cv is not None and h_mid is not None) else None
    full_pc = ((sidecar or {}).get("player_contexts") or {}).get(pc.get("player_context_id")) if pc else None
    full_gc = ((sidecar or {}).get("game_contexts") or {}).get(gc.get("game_context_id")) if gc else None
    row = {"record_version": RECORD_VERSION,
           # identity
           "record_id": proj.get("record_id"), "snapshot_id": proj.get("snapshot_id"), "ticker": proj.get("ticker"), "event_ticker": proj.get("event_ticker"),
           "series_ticker": proj.get("series_ticker"), "model_arm": proj.get("model_arm"), "engine": proj.get("engine"), "engine_version": proj.get("engine_version"),
           "model_version": proj.get("model_version"), "evidence_class": proj.get("evidence_class"),
           # contract
           "market_family": proj.get("market_family"), "family_group": family_group(proj), "period": proj.get("period"), "stat_family": proj.get("stat_family"),
           "threshold": proj.get("threshold"), "operator": proj.get("operator"), "semantic_confidence": proj.get("semantic_confidence"),
           "game_id": proj.get("game_id"), "season": proj.get("season"), "week": proj.get("week"), "home_team": proj.get("home_team"), "away_team": proj.get("away_team"),
           "subject_kind": proj.get("subject_kind"), "subject_id": proj.get("subject_id"), "subject_name": proj.get("subject_name"), "identity_confidence": proj.get("identity_confidence"),
           "player_position": pc.get("position"),
           # time / horizon
           "kickoff_utc": proj.get("kickoff_utc"), "observed_at": proj.get("observed_at"), "generated_at": proj.get("generated_at"), "minutes_to_kickoff": proj.get("minutes_to_kickoff"),
           "horizon_label": proj.get("horizon_label"), "horizon_id": proj.get("horizon_id"), "horizon_quality": hq.get("horizon_quality"),
           "observation_lateness_min": hq.get("observation_lateness_min"), "snapshot_reused": hq.get("snapshot_reused"),
           # horizon market
           "h_yes_bid": proj.get("yes_bid"), "h_yes_ask": proj.get("yes_ask"), "h_no_bid": proj.get("no_bid"), "h_no_ask": proj.get("no_ask"), "h_mid": h_mid,
           "h_width": proj.get("quote_width"), "h_volume": proj.get("volume"), "h_open_interest": proj.get("open_interest"), "h_liquidity": proj.get("liquidity"),
           "market_confirmed": proj.get("market_confirmed"), "last_trade_at": ms.get("last_trade_at"),
           "ladder_identification": ((ms.get("ladder") or {}).get("identification")), "ladder_n_rungs": ((ms.get("ladder") or {}).get("n_rungs_quoted")),
           "ladder_median_width": ((ms.get("ladder") or {}).get("median_width")), "ladder_raw_violations": ((ms.get("ladder") or {}).get("raw_violations")),
           # model
           "support_state": proj.get("support_state"), "support_reason": proj.get("support_reason"), "p_yes": proj.get("p_yes"), "contract_value": cv,
           "p_yes_low": proj.get("p_yes_low"), "p_yes_high": proj.get("p_yes_high"), "disagreement_pp": dis_pp, "disagreement_band": disagreement_band(dis_pp),
           "probability_band": tenth_band(cv), "price_band": tenth_band(h_mid), "width_band": band(proj.get("quote_width"), WIDTH_BANDS), "liquidity_band": band(proj.get("liquidity"), LIQUIDITY_BANDS),
           "dist_mean": (proj.get("distribution_summary") or {}).get("mean"), "dist_sd": (proj.get("distribution_summary") or {}).get("sd"),
           # flags
           **{f"flag_{k}": v for k, v in fl.items()},
           # player / game context (compact) + sidecar ids
           **{f"ctx_{k}": v for k, v in pc.items() if k != "player_context_id"}, "player_context_id": pc.get("player_context_id"),
           **{f"game_{k}": v for k, v in gc.items() if k != "game_context_id"}, "game_context_id": gc.get("game_context_id"),
           "context_in_sidecar": bool(full_pc or full_gc),
           # ---- queryability the audit found missing: a researcher must be able to exclude a family the
           # exchange contradicted, read a RANGE contract's bounds, and trace a settled row back to its Kalshi id
           "crosscheck_agreement": (crosscheck or {}).get("agreement"),
           "crosscheck_hard_warning": bool((crosscheck or {}).get("hard_warning")),
           "crosscheck_exchange_result": (crosscheck or {}).get("exchange_result"),
           "crosscheck_exchange_payout": (crosscheck or {}).get("exchange_payout"),
           "crosscheck_reason": (crosscheck or {}).get("reason"),
           "range_lo": proj.get("range_lo"), "range_hi": proj.get("range_hi"),
           "subject_kalshi_id": proj.get("subject_kalshi_id"),
           "dist_p25": (proj.get("distribution_summary") or {}).get("p25"),
           "dist_p50": (proj.get("distribution_summary") or {}).get("p50"),
           "dist_p75": (proj.get("distribution_summary") or {}).get("p75"),
           "settlement_reachability": (proj.get("settlement_reachability") or {}).get("state"),
           "settlement_reachability_reason": (proj.get("settlement_reachability") or {}).get("reason"),
           "injury_report_maturity": pc.get("injury_report_maturity"),
           "injury_report_rows_for_week": pc.get("injury_report_rows_for_week"),
           "official_inactive_state": pc.get("official_inactive_state"),
           "official_inactive_observed_at": pc.get("official_inactive_observed_at"),
           "evaluation_version_close": (close or {}).get("evaluation_version"),
           "evaluation_version_settlement": (settlement or {}).get("evaluation_version"),
           "evaluation_version_autopsy": (autopsy or {}).get("evaluation_version"),
           # MARKET/MODEL SYNCHRONIZATION -- first-class, filterable, and not only in lineage. A row whose model
           # information runs later than the market it is scored against cannot carry a model-edge claim on its
           # own, because "we read something the quote had not priced" explains the disagreement more cheaply.
           "synchronization_state": sy.get("synchronization_state", "UNKNOWN_TIMING"),
           "information_skew_seconds": sy.get("information_skew_seconds"),
           "market_observed_at": sy.get("market_observed_at") or proj.get("observed_at"),
           "market_observable_through": sy.get("market_observable_through"),
           "model_information_frontier": sy.get("model_information_frontier"),
           "generation_time": sy.get("generation_time") or proj.get("generated_at"),
           "synchronization_reason": sy.get("synchronization_reason"),
           "pit_data_cutoff": ((proj.get("lineage") or {}).get("point_in_time") or {}).get("data_cutoff"),
           "pit_information_frontier": ((proj.get("lineage") or {}).get("point_in_time") or {}).get("information_frontier"),
           # executable depth at this horizon: the state and the reason travel together, so an unobserved book
           # can never be read as a thin market. Canonical CLV above is untouched by any of this.
           "depth": dp, "depth_state": dp.get("state", "DEPTH_NOT_CAPTURED"), "depth_reason": dp.get("why"),
           "depth_side": dp.get("side"), "depth_top_size": dp.get("top_size"), "depth_levels": dp.get("levels"),
           "depth_contracts_available": dp.get("avail"), "depth_book_age_min": dp.get("age_min"),
           "exec_vwap_1": dp.get("vwap1"), "exec_vwap_10": dp.get("vwap10"), "exec_vwap_50": dp.get("vwap50"),
           "exec_slippage_1_to_50": (None if dp.get("vwap1") is None or dp.get("vwap50") is None else round(dp["vwap50"] - dp["vwap1"], 6)),
           "exec_size_to_exhaust_edge": dp.get("edge_size"),
           # the DEDICATED depth sweep, paired to this record in the export rather than frozen onto it. The
           # sweep runs on its own cadence, so the pairing is a selection under `observed_at <= data_cutoff` and
           # `observed_at < kickoff`; the target horizon it was aiming at and the observation it actually made
           # are separate columns, because a single sweep of a clustered slate cannot be at one horizon.
           "depth_pair_version": (depth_pair or {}).get("depth_pair_version"),
           "depth_pair_state": (depth_pair or {}).get("state"),
           "depth_pair_reason": (depth_pair or {}).get("reason"),
           "depth_pair_observed_at": (depth_pair or {}).get("paired_observed_at"),
           "depth_pair_age_min": (depth_pair or {}).get("paired_age_min"),
           "depth_pair_minutes_to_kickoff": (depth_pair or {}).get("paired_minutes_to_kickoff"),
           "depth_pair_target_horizon": (depth_pair or {}).get("paired_target_horizon"),
           "depth_pair_horizon_quality": (depth_pair or {}).get("paired_horizon_quality"),
           "depth_pair_ladder_complete": (depth_pair or {}).get("paired_ladder_complete"),
           "depth_pair_run_id": (depth_pair or {}).get("paired_run_id"),
           # close + clv
           "close_status": (close or {}).get("close_status", "CLV_CLOSE_MISSING" if close is None else None), "close_reason": (close or {}).get("close_reason"),
           "close_quality": (close or {}).get("close_quality", "MISSING"), "close_id": (close or {}).get("close_id"), "close_age_seconds": (close or {}).get("close_age_seconds"),
           "close_source_snapshot": (close or {}).get("close_source_snapshot"), "close_flags": (close or {}).get("flags"),
           "c_yes_bid": (close or {}).get("yes_bid"), "c_yes_ask": (close or {}).get("yes_ask"), "c_no_bid": (close or {}).get("no_bid"), "c_no_ask": (close or {}).get("no_ask"),
           "c_mid": (close or {}).get("mid"), "c_width": (close or {}).get("quote_width"), "c_volume": (close or {}).get("volume"), "c_liquidity": (close or {}).get("liquidity"),
           "clv_status": (clv or {}).get("clv_status"), "model_side": (clv or {}).get("model_side"), "movement": (clv or {}).get("movement"),
           "move_yes_mid": (clv or {}).get("move_yes_mid"), "move_no_mid": (clv or {}).get("move_no_mid"), "move_yes_ask": (clv or {}).get("move_yes_ask"), "move_no_ask": (clv or {}).get("move_no_ask"),
           "model_to_close": (clv or {}).get("model_to_close"), "model_closer_than_horizon": (clv or {}).get("model_closer_than_horizon"),
           "clv_mid_toward_model": (clv or {}).get("clv_mid_toward_model"), "clv_exec_toward_model": (clv or {}).get("clv_exec_toward_model"), "clv_net_of_fee": (clv or {}).get("clv_net_of_fee"),
           "entry_executable_price": (clv or {}).get("entry_executable_price"), "entry_fee_per_contract": (clv or {}).get("entry_fee_per_contract"), "entry_break_even": (clv or {}).get("entry_break_even"),
           # settlement
           "settlement_status": (settlement or {}).get("settlement_status"), "settled_yes": (settlement or {}).get("settled_yes"), "settlement_kind": (settlement or {}).get("settlement_kind"),
           "settlement_reason": (settlement or {}).get("settlement_reason"), "settlement_rule_version": (settlement or {}).get("settlement_rule_version"),
           # autopsy
           "autopsy_classification": (autopsy or {}).get("classification"), "autopsy_robust_z": (autopsy or {}).get("robust_z"), "autopsy_percentile": (autopsy or {}).get("percentile"),
           "autopsy_version": (autopsy or {}).get("autopsy_version")}
    y = row["settled_yes"]
    if y is not None and cv is not None:
        row["brier_model"] = (cv - y) ** 2
        row["brier_market_h"] = ((h_mid - y) ** 2) if h_mid is not None else None
        row["brier_market_close"] = ((row["c_mid"] - y) ** 2) if row["c_mid"] is not None else None
        # executable YES/NO taken at the horizon ask on the model's side; payout net of the entry fee when known (fee once)
        side, ask = row["model_side"], row["entry_executable_price"]
        if side in ("YES", "NO") and ask is not None:
            payout = y if side == "YES" else 1.0 - y
            row["exec_pnl_gross"] = payout - ask
            row["exec_pnl_net"] = (payout - ask - row["entry_fee_per_contract"]) if row["entry_fee_per_contract"] is not None else None
    return row
