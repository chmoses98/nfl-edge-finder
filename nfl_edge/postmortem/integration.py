"""The thin, RESTRICTION-ONLY bridge between the real-money path (handicap/card.py, gates.py, preflight.py) and the
postmortem safeguards. All logic lives HERE (unpinned, unit-tested); the three hash-pinned files only call it.

Owner-approved 2026-11-02 (PR #232 comments): wire point-in-time guards, the fee-inclusive order-size ceiling check and
exposure flags into RUN NFL. 1U = $75; FLAG above 5U/game ($375) and 15U/day ($1,125). Flags are not caps.

What this can do:   turn an APPROVED candidate into a BLOCKED one, and add flags.
What this cannot:   add a candidate, raise a stake, raise a ceiling, re-rank anything, or supply a missing fact.

Honesty rules (each is tested):
* A quarterback is CONFIRMED only when ``qb_confirmations.py`` resolves a validated record from an allowlisted source that
  NAMES the starter (team announcement, head-coach statement on record, official lineup) observed before the decision and
  before kickoff and not stale (``run["qb_confirmations"]`` is {game_id: {team: row}}). A depth chart, active roster,
  inactive list or injury-report status is NOT a confirmation and can never become one. A team with no usable record blocks
  every market the QB-dependency table gates (qb_dependency.py: score-determined lines, team/game stats, events, QB passing props, and
  anything unclassified; pass-catcher props need only their own team's QB) ``QB_UNKNOWN:<team>``; a conflicting, stale, too-early or
  withdrawn one blocks ``QB_NOT_CONFIRMED:<team>`` with a ``QB_REASON`` code. Games whose required quarterbacks are confirmed are evaluated
  normally; markets the table marks NOT_GATED (kicker, defender, running-back rushing props) are never blocked by this logic.
* The ceiling check compares the record's ``bet_up_to_probability`` with a whole-order, fee-inclusive bound derived from
  the analyst's DECLARED fair range. That range is uncalibrated, so the bound is labelled ``ANALYST_DECLARED_UNCALIBRATED``;
  a CALIBRATED bet-up-to is reported as ``None`` (MISSING_CALIBRATION) because no held-out calibration cells exist for
  thesis-conditioned fair values. The check can only tighten (FAIL), never loosen or invent a ceiling.
* Records WITHOUT a ``pit_evidence`` block (every record written before this change) are NOT re-judged: replaying history
  must not change a historical verdict. Every record the card now produces carries the block.
"""
from __future__ import annotations

from datetime import datetime, timezone

from . import exposure as EXP
from .common import DAILY_EXPOSURE_FLAG_UNITS, GAME_EXPOSURE_FLAG_UNITS, UNIT_DOLLARS, num
from .fairvalue import bet_up_to, fair_probability, fee_fn_from_schedule
from . import qb_confirmations as QBC
from . import player_identity as PI
from . import qb_dependency as QD
from .guards import guard_candidate

INTEGRATION_VERSION = "nfl-postmortem-integration-1.0.0"
PIT_SCHEMA = "nfl-pit-evidence.v1"

#: $ thresholds the owner stated; derived from the single unit constant so they cannot drift apart.
GAME_FLAG_DOLLARS = GAME_EXPOSURE_FLAG_UNITS * UNIT_DOLLARS      # 375.0
DAILY_FLAG_DOLLARS = DAILY_EXPOSURE_FLAG_UNITS * UNIT_DOLLARS    # 1125.0

#: Net-edge floor the existing ceiling already embeds (handicap/expression.MIN_NET_EDGE = 2.0c). The order-size check
#: uses the same margin so it verifies the existing policy rather than imposing a second one.
EXISTING_CEILING_MARGIN = 0.02

#: Guard codes about the QUOTE are decided at preflight from the resolved executable ask, never from a card-time capture.
QUOTE_BLOCK_PREFIXES = ("MISSING_QUOTE", "QUOTE_AFTER_DECISION", "STALE_QUOTE", "PRICE_", "INSUFFICIENT_DEPTH")

#: The key-number distribution is RESEARCH. This is the provenance any future consumer must carry; the card does not use it.
KEY_NUMBER_DISTRIBUTION_PROVENANCE = {
    "module": "nfl_edge.postmortem.distributions",
    "status": "RESEARCH_ONLY_NOT_USED_BY_CARD",
    "calibrated_on_seasons": [2022, 2023],
    "tested_on_seasons": [2024, 2025],
    "centre": "CLOSING_LINE (no historical Kalshi 1Q/1H/team-total quotes exist): tests shape and location, not profit",
    "opponent_adjusted_evidence": "NOT_DEMONSTRATED (EPA, pace, schedule, special teams added nothing over the market-only location)",
    "source": "PR #232 held-out evaluation (docs/research/POSTMORTEM_2026-11-02.md)",
}


def _iso(dt):
    return None if dt is None else dt.astimezone(timezone.utc).isoformat()


def build_pit_evidence(*, run: dict, game: dict, ev: dict) -> dict:
    """The point-in-time facts a record rests on, as the packet states them. Missing stays None; nothing is inferred."""
    fresh = game.get("data_freshness") or {}
    ctx_raw = fresh.get("context_capture")
    injuries_as_of = None
    try:
        injuries_as_of = _iso(datetime.strptime(str(ctx_raw), "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc))
    except (TypeError, ValueError):
        pass
    teams = [game.get("home_team"), game.get("away_team")]
    # ``run["qb_confirmations"]`` is {game_id: {team: row}} RESOLVED by qb_confirmations.resolve_slate from validated,
    # allowlisted, timestamped records (scripts/handicap/run_card.py). The old team-keyed shape carried no provenance and is gone.
    supplied = (run.get("qb_confirmations") or {}).get(game.get("game_id")) or {}
    qb = {}
    for t in teams:
        row = supplied.get(t)
        if isinstance(row, dict):
            # full provenance travels with the row so the record can show WHY a quarterback was or was not confirmed
            qb[t] = {k: row.get(k) for k in ("status", "confirmed_at", "source", "source_ref", "record_id", "qb_player_id", "reason", "game_id",
                                             "team", "observed_at", "captured_at", "as_of", "kickoff_utc", "conflicts", "withdrawn_record_ids")}
    # A contract about ONE named player: resolve who he is and what position he plays from the repository's own player data
    # (run["player_identity_book"], built by scripts/handicap/run_card.py from --raw-root). Unresolvable -> an UNVERIFIED block, which blocks.
    player_identity = None
    if QD.is_player_scoped(ev.get("ticker"), ev.get("family")):
        pm = next((m for m in game.get("markets", []) if m.get("ticker") == ev.get("ticker")), None) or {}
        player_identity = PI.verify(run.get("player_identity_book"), player_id=pm.get("player_id"), game_teams=teams, game_week=game.get("week"),
                                    ticker_team=QD.own_team(ev.get("ticker") or "", [t for t in teams if t]), as_of=run.get("decision_time"))
    return {
        "schema": PIT_SCHEMA,
        "integration_version": INTEGRATION_VERSION,
        "player_identity": player_identity,
        "projection_as_of": fresh.get("ledger_feature_cutoff"),
        "injuries_as_of": injuries_as_of,
        "qb": qb,
        "teams": teams,
        "game_id": game.get("game_id"),
        "qb_policy": {"table_version": QD.TABLE_VERSION, "player_identity_version": PI.IDENTITY_VERSION, "max_age_at_decision_min": QBC.MAX_AGE_AT_DECISION_MIN,
                      "max_lead_before_kickoff_min": QBC.MAX_LEAD_BEFORE_KICKOFF_MIN},
        "bet_up_to_provenance": {
            "ceiling_basis": ev.get("fair_basis"),
            "ceiling_is_calibrated": False,
            "calibrated_bet_up_to_cents": None,
            "calibrated_reason": "MISSING_CALIBRATION: no held-out calibration cells exist for thesis-conditioned fair values",
        },
        "key_number_distribution": {"used_by_card": False, "provenance": KEY_NUMBER_DISTRIBUTION_PROVENANCE},
    }


def _is_quote_block(code: str) -> bool:
    return code.startswith(QUOTE_BLOCK_PREFIXES)


def pit_applies(rec: dict, *, as_of=None) -> tuple[bool, str]:
    """Whether G_PIT / G_ORDER_CEILING judge this record, and if not, why. A record without a ``pit_evidence`` block predates the gate and is
    not re-judged. A PLAYER market keeps its own availability gate and is judged here ONLY when the QB-dependency table says its production
    depends on the quarterback (QB_GATED passing props, QB_INDIRECT pass-catcher / scorer props); an unrelated prop (kicker, defender,
    running-back rushing) is not blocked by an unknown quarterback."""
    from nfl_edge.handicap import schema as S
    if rec.get("pit_evidence") is None:
        return False, "record predates the pit_evidence block; its historical verdict is not re-judged"
    if rec.get("market_family") in S.PLAYER_MARKET_FAMILIES:
        pit = rec.get("pit_evidence") or {}
        req = QD.requirement(rec.get("market_ticker"), family=rec.get("market_family"), teams=pit.get("teams"), player=pit.get("player_identity"),
                             decision_time=as_of or rec.get("created_at"))
        if not req.requires_confirmation:
            return False, f"player market: gated by player_availability_resolved; {req.classification} in the QB-dependency table ({req.rationale})"
    return True, ""


def pit_gate(rec: dict, *, dq, dr, as_of: datetime) -> tuple[str, str, dict]:
    """(status, reason, evidence). status is PASS or FAIL. ``dq`` is the gate's resolved decision-time quote (or None),
    ``dr`` the resolved full-position depth (or None). Quote provenance is judged from those, not from a capture."""
    pit = rec.get("pit_evidence") or {}
    quote = None
    if dq is not None and getattr(dq, "is_actionable", False):
        depth = None
        if dr is not None and getattr(dr, "is_executable", False):
            depth = num(getattr(dr, "contracts_required", None))
        quote = {"price": dq.executable_price, "captured_at": dq.confirmed_at, "kind": "EXECUTABLE_ASK", "depth": depth}
    cand = {
        "ticker": rec.get("market_ticker"), "family": rec.get("market_family"), "game_id": pit.get("game_id") or rec.get("game_id"),
        "side": rec.get("side"), "decision_time": as_of, "kickoff_utc": rec.get("kickoff_utc"),
        "projection_as_of": pit.get("projection_as_of"), "injuries_as_of": pit.get("injuries_as_of"),
        "qb": pit.get("qb") or {}, "teams": pit.get("teams") or [], "player": pit.get("player_identity"),
        "quote": quote or {}, "contracts": None if quote is None else quote.get("depth"),
    }
    out = guard_candidate(cand)
    blocks = list(out["blocks"])
    if quote is None:
        # No actionable executable quote: the freshness gate already FAILED/UNAVAILABLE on that and says why; do not
        # double-report it as a provenance failure, but never let a missing executable ask pass silently either.
        blocks = [b for b in blocks if not _is_quote_block(b)] + ["NO_EXECUTABLE_QUOTE_FOR_PROVENANCE"]
    evidence = {"blocks": sorted(set(blocks)), "warnings": out["warnings"], "guard_version": INTEGRATION_VERSION,
                "qb_requirement": out.get("qb_requirement"), "qb_provenance": out.get("qb_provenance"),
                "quote_kind": None if quote is None else quote["kind"],
                "policy": "restriction-only; CONFIRMED_STARTER requires a supplied confirmation with a time"}
    if blocks:
        return "FAIL", "point-in-time evidence not established: " + ", ".join(sorted(set(blocks))), evidence
    return "PASS", "projection, injuries, both quarterbacks and the executable quote are point-in-time and confirmed", evidence


def ceiling_gate(rec: dict, *, fee_schedule, series: str | None, as_of: datetime) -> tuple[str, str, dict]:
    """Whole-order, fee-inclusive check of the record's ceiling. Can only FAIL a ceiling that is too high."""
    lo, hi = num(rec.get("probability_low")), num(rec.get("probability_high"))
    stake = num(rec.get("recommended_stake"))
    ceiling = num(rec.get("bet_up_to_probability"))
    ev = {"basis": "ANALYST_DECLARED_UNCALIBRATED", "calibrated": False, "record_ceiling": ceiling,
          "calibrated_bet_up_to_cents": None, "calibrated_reason": "MISSING_CALIBRATION"}
    if None in (lo, hi, stake, ceiling) or stake <= 0:
        return "UNAVAILABLE", "the record lacks a declared fair range, a stake or a ceiling, so no order-size bound exists (none is invented)", ev
    if fee_schedule is None:
        return "UNAVAILABLE", "no fee schedule: the order-size fee is unknown, so no bound is computed (an unknown fee is never zero)", ev
    fair = fair_probability(None, declared=(lo, hi))
    res = bet_up_to(fair, stake, fee_fn_from_schedule(fee_schedule, series, as_of), min_margin=EXISTING_CEILING_MARGIN)
    cents = res.get("bet_up_to_cents")
    ev.update({"order_size_bound_cents": cents, "stake": stake, "flags": res.get("flags", []), "min_margin": EXISTING_CEILING_MARGIN})
    if cents is None:
        return "FAIL", f"no price clears the fee-inclusive break-even at the order size ({','.join(res.get('flags', []))}); the record's ceiling has no support", ev
    if ceiling * 100 > cents + 1e-6:
        return "FAIL", (f"the record's ceiling {ceiling * 100:.1f}c is ABOVE the whole-order fee-inclusive bound {cents}c "
                        f"at ${stake:.2f}; the ceiling is not honoured here (never raised, only refused)"), ev
    return "PASS", f"ceiling {ceiling * 100:.1f}c <= whole-order fee-inclusive bound {cents}c at ${stake:.2f}", ev


def exposure_flags(positions: list, *, open_units_by_game: dict | None = None, game_dates: dict | None = None) -> dict:
    """Flags for ONE slate's selected positions plus the owner's already-open units. FLAGS ONLY.

    positions: dicts with ticker, side, stake (fee-inclusive dollars), game_id, game_date. open_units_by_game: {game_id: units}
    already outstanding. Per-game and per-day totals combine both; axis groups (spread ladders, totals, team totals) come
    from ``exposure.aggregate`` so two SF spread rungs are one thesis."""
    open_units_by_game = open_units_by_game or {}
    game_dates = game_dates or {}
    agg = EXP.aggregate(positions)
    per_game, per_day = {}, {}
    for p in positions:
        gid = p.get("game_id")
        u = (num(p.get("stake")) or 0.0) / UNIT_DOLLARS
        per_game[gid] = per_game.get(gid, 0.0) + u
    for gid, ou in open_units_by_game.items():
        per_game[gid] = per_game.get(gid, 0.0) + (num(ou) or 0.0)
    undated_open_units = 0.0
    for gid, u in per_game.items():
        if not game_dates.get(gid):
            # Open exposure on a game whose date this call was not given cannot be placed on a day. It still counts toward
            # its game; it is reported, never silently added to (or dropped from) a daily total.
            undated_open_units += u
            continue
        day = str(game_dates[gid])[:10]
        per_day[day] = per_day.get(day, 0.0) + u
    flags = [f for f in agg["flags"] if f["kind"] == "GROUP_OVER_LIMIT"]
    for gid, u in sorted(per_game.items(), key=lambda kv: str(kv[0])):
        if u > GAME_EXPOSURE_FLAG_UNITS:
            flags.append({"kind": "GAME_OVER_LIMIT", "game": gid, "units": round(u, 4), "dollars": round(u * UNIT_DOLLARS, 2),
                          "limit_units": GAME_EXPOSURE_FLAG_UNITS, "limit_dollars": GAME_FLAG_DOLLARS})
    for day, u in sorted(per_day.items()):
        if u > DAILY_EXPOSURE_FLAG_UNITS:
            flags.append({"kind": "DAY_OVER_LIMIT", "day": day, "units": round(u, 4), "dollars": round(u * UNIT_DOLLARS, 2),
                          "limit_units": DAILY_EXPOSURE_FLAG_UNITS, "limit_dollars": DAILY_FLAG_DOLLARS})
    return {"unit_dollars": UNIT_DOLLARS, "game_flag_dollars": GAME_FLAG_DOLLARS, "daily_flag_dollars": DAILY_FLAG_DOLLARS,
            "policy_note": "flags only; no cap is applied or implied (docs/NFL_OPERATING_POLICY.md)",
            "per_game_units": {str(k): round(v, 4) for k, v in per_game.items()},
            "per_day_units": {k: round(v, 4) for k, v in per_day.items()},
            "undated_units_not_in_daily_totals": round(undated_open_units, 4),
            "groups": agg["games"], "flags": flags, "unprocessed": agg["unprocessed"]}
