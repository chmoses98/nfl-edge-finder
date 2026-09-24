"""LEAN projection records for the V4 arms: same schema, same readers, the duplicated blocks replaced by references.

A Shadow v2 player record is ~8.2 KB of JSON (DATA_PLAYER_V3, 2026-09-23T22:46 snapshot, 16,177 records, 5.1 MB
gzipped per arm per snapshot). Most of it is not about the arm at all:

    player_context   1.5 KB  identical for every record of the player in the snapshot, and already written in full
                             to the snapshot's context sidecar (`<snapshot>.contexts.json.gz`) under its id
    lineage          1.4 KB  identical for every record of the snapshot (run lineage + point-in-time ledger)
    market_state     1.0 KB  a property of the quote, identical across every arm pricing that ticker
    game_context     0.6 KB  identical for every record of the game, in the sidecar under its id

Writing all of that again for two more arms would add ~10 MB per snapshot to a projection archive that is already
1.17 GB. A lean record keeps every field the readers use -- settlement (question, identity, thresholds), the
research record and scorecards (the context fields they segment on, synchronization, point-in-time cutoffs,
ladder identification), eligibility and RUN NFL (probability, abstention, provenance) -- and replaces the rest
with the ids that resolve them in the immutable sidecar. `storage.lean` says so on the record, with the version.

Nothing here edits a record that was already written; lean applies to V4 arm records at write time only.
"""
from __future__ import annotations

LEAN_VERSION = "lean-record-1.0.0"
# the compact player-context keys the research record / scorecard / health gate / run summary read (research_record.py,
# research_slim.py, scorecard_v3.SEGMENTS, weekly_report_v2 health, project_slate_v2.context_coverage)
PLAYER_CONTEXT_KEEP = ("player_context_id", "position", "team", "availability_state", "injury_state", "injury_report_maturity",
                       "injury_report_rows_for_week", "role_certainty", "role_class", "depth_chart_rank", "depth_chart_group_rank",
                       "weather_state", "official_inactive_state", "official_inactive_observed_at", "team_pass_attempts",
                       "qb_depth_chart", "qb_schedule")
GAME_CONTEXT_KEEP = ("game_context_id",)
LADDER_KEEP = ("identification", "n_rungs_quoted", "median_width", "raw_violations")
PIT_KEEP = ("data_cutoff", "information_frontier", "max_skew_seconds", "outcome_leak_refused", "pit_version")
LINEAGE_KEEP = ("lineage_id", "sidecar", "capture_run", "bundle_sha", "discovery_run")


# a REFUSAL (no probability) is never scored: it keeps its identity, contract, timing, state and reason -- what the
# accounting and the board reports read -- and nothing else
REFUSAL_KEEP = ("record_id", "snapshot_id", "ticker", "series_ticker", "event_ticker", "model_arm", "engine", "engine_version",
                "distribution_version", "model_version", "schema_version", "evidence_class", "market_family", "period", "stat_family",
                "question", "threshold", "range_lo", "range_hi", "operator", "semantic_confidence", "settlement_rule_version", "game_id",
                "season", "week", "home_team", "away_team", "subject_kind", "subject_id", "subject_kalshi_id", "subject_name",
                "identity_confidence", "observed_at", "generated_at", "kickoff_utc", "minutes_to_kickoff", "data_cutoff", "horizon_label",
                "horizon_target_min", "horizon_lateness_min", "horizon_id", "yes_bid", "yes_ask", "no_bid", "no_ask", "mid", "quote_width",
                "support_state", "support_reason", "p_yes", "contract_value", "flags", "settlement_reachability", "content_hash")
# what a hybrid record keeps of the data arm's intermediates: the availability inputs its contract value used
HYBRID_FEATURE_KEEP = ("availability_state", "p_plays", "p_active_no_snap", "inputs_version")


def lean(row: dict, *, intermediates: bool = True) -> dict:
    """A lean copy of one finished record dict (the caller recomputes content_hash afterwards).

    intermediates=False (the hybrid arm): the model intermediates are on the DATA_PLAYER_V4 record of the same snapshot
    and ticker, and are referenced rather than copied."""
    if row.get("p_yes") is None:
        r = {k: row[k] for k in REFUSAL_KEEP if k in row}
        # the run summary's last-trade coverage is computed over every record, refusals included
        r["market_state"] = {"last_trade_at": (row.get("market_state") or {}).get("last_trade_at")}
        r["storage"] = {"lean": LEAN_VERSION, "refusal": True}
        return r
    r = dict(row)
    pc = r.get("player_context") or {}
    r["player_context"] = {k: pc[k] for k in PLAYER_CONTEXT_KEEP if k in pc}
    gc = r.get("game_context") or {}
    r["game_context"] = {k: gc[k] for k in GAME_CONTEXT_KEEP if k in gc}
    ms = r.get("market_state") or {}
    lad = ms.get("ladder") or {}
    r["market_state"] = {"last_trade_at": ms.get("last_trade_at"), "ladder": {k: lad[k] for k in LADDER_KEEP if k in lad}}
    lin = r.get("lineage") or {}
    pit = lin.get("point_in_time") or {}
    r["lineage"] = {**{k: lin[k] for k in LINEAGE_KEEP if k in lin}, "point_in_time": {k: pit[k] for k in PIT_KEEP if k in pit}}
    dq = r.get("data_quality") or {}
    r["data_quality"] = {k: v for k, v in dq.items() if k != "availability_sources"}
    if not intermediates:
        fl = r.get("feature_lineage") or {}
        r["feature_lineage"] = {**{k: fl[k] for k in HYBRID_FEATURE_KEEP if k in fl}, "intermediates": "DATA_PLAYER_V4 record, same snapshot and ticker"}
    # the catalog's YES rule text is a property of the contract (identical on every arm's record of the ticker) and no
    # reader uses it; the synchronization REASON of a SYNCHRONIZED record is one constant sentence
    r.pop("yes_semantics", None)
    sy = r.get("information_sync") or {}
    if sy.get("synchronization_state") == "SYNCHRONIZED":
        r["information_sync"] = {k: v for k, v in sy.items() if k != "synchronization_reason"}
    r["storage"] = {"lean": LEAN_VERSION}
    return r


# How each block a lean record drops is resolved (docs/PLAYER_V4.md). Kept here, once, not on every record.
RESOLVES = {"player_context": "sidecar player_contexts[player_context_id]",
            "game_context": "sidecar game_contexts[game_context_id]",
            "lineage": "sidecar lineage (run lineage + point-in-time ledger)",
            "market_state": "the MARKET_PLAYER_DIST record of the same snapshot and ticker",
            "yes_semantics": "the catalog entry of (market_family, period, stat_family), or any other arm's record of the ticker",
            "information_sync.synchronization_reason": "pit.synchronization(): constant for SYNCHRONIZED",
            "refusal": "a record without a probability keeps REFUSAL_KEEP only (identity, contract, timing, state, reason)",
            "hybrid feature_lineage": "the DATA_PLAYER_V4 record of the same snapshot and ticker"}


def is_lean(row: dict) -> bool:
    return bool((row.get("storage") or {}).get("lean"))
