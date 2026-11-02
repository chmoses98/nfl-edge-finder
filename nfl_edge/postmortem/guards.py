"""Point-in-time evidence guards for GAME-LEVEL markets. RESTRICTION-ONLY: a guard can only turn actionable -> blocked.

The existing real-money gates (nfl_edge/handicap/gates.py) already enforce decision-before-kickoff, 15-minute quote
and book freshness, fee-schedule verification, depth and net EV, and an availability gate for PLAYER markets only.
What was not enforced for spreads, alternates, 1Q/1H/team totals and totals is that the PROJECTION behind the number,
the injury snapshot and the QUARTERBACK status were fresh, point-in-time, and confirmed. Those are added here, plus a
price-provenance check (a captured mid is not an executable ask).

NOT WIRED into handicap/gates.py or preflight.py in this change: both are hash-pinned real-money sources
(tests/test_incumbent_unchanged.py). Wiring is a one-line call to ``guard_candidate`` plus a deliberate pin update and
needs the owner's explicit authorization (see the PR). Until then these verdicts are advisory evidence in reports.

Every time argument is explicit: there is no wall-clock default, and naive timestamps are refused (None).
"""
from __future__ import annotations

from .common import MAX_INJURY_AGE_MIN, MAX_PROJECTION_AGE_MIN, MAX_QUOTE_AGE_MIN, num, parse_ts
from .ontology import classify_ticker

EXECUTABLE_KINDS = ("EXECUTABLE_ASK",)
CAPTURED_ONLY_KINDS = ("CAPTURED_MID", "CAPTURED_LAST", "CAPTURED_BID", "CLOSE_MID", "MODEL_IMPLIED")
QB_CONFIRMED = "CONFIRMED_STARTER"


def _age_min(decision, then):
    return None if decision is None or then is None else (decision - then).total_seconds() / 60.0


def guard_candidate(c: dict, *, max_projection_age_min=MAX_PROJECTION_AGE_MIN, max_injury_age_min=MAX_INJURY_AGE_MIN,
                    max_quote_age_min=MAX_QUOTE_AGE_MIN, require_qb_for=("GAME_WINNER", "SPREAD", "TOTAL", "TEAM_TOTAL")) -> dict:
    """c keys: ticker, side, decision_time, kickoff_utc, projection_as_of, injuries_as_of, qb {TEAM: {status, confirmed_at}},
    teams [home, away], quote {price, captured_at, kind, depth}, contracts. Returns {actionable, blocks[], warnings[]}."""
    blocks, warns = [], []
    ont = classify_ticker(c.get("ticker"))
    dec, ko = parse_ts(c.get("decision_time")), parse_ts(c.get("kickoff_utc"))
    if dec is None:
        blocks.append("MISSING_DECISION_TIME")
    if ko is None:
        blocks.append("MISSING_KICKOFF")           # a market whose kickoff is unknown cannot be shown pregame
    elif dec is not None and dec >= ko:
        blocks.append("AFTER_KICKOFF")

    # --- projection
    pa = parse_ts(c.get("projection_as_of"))
    if pa is None:
        blocks.append("MISSING_PROJECTION_AS_OF")
    elif dec is not None:
        age = _age_min(dec, pa)
        if age < 0:
            blocks.append("PROJECTION_AFTER_DECISION")
        elif age > max_projection_age_min:
            blocks.append("STALE_PROJECTION")

    # --- injuries (game-level markets depend on who plays)
    ia = parse_ts(c.get("injuries_as_of"))
    if ia is None:
        blocks.append("MISSING_INJURY_SNAPSHOT")
    elif dec is not None:
        age = _age_min(dec, ia)
        if age < 0:
            blocks.append("INJURIES_AFTER_DECISION")
        elif age > max_injury_age_min:
            blocks.append("STALE_INJURIES")

    # --- confirmed quarterbacks for both teams (score-based markets)
    if ont.family in require_qb_for:
        qb = c.get("qb") or {}
        teams = list(c.get("teams") or [])
        if len(teams) != 2:
            blocks.append("MISSING_TEAMS_FOR_QB_CHECK")
        for team in teams:
            row = qb.get(team)
            if not row:
                blocks.append(f"QB_UNKNOWN:{team}")
                continue
            if row.get("status") != QB_CONFIRMED:
                blocks.append(f"QB_NOT_CONFIRMED:{team}")
                continue
            ct = parse_ts(row.get("confirmed_at"))
            if ct is None:
                blocks.append(f"QB_CONFIRMATION_TIME_MISSING:{team}")
            elif dec is not None and ct > dec:
                blocks.append(f"QB_CONFIRMED_AFTER_DECISION:{team}")

    # --- quote freshness and provenance
    q = c.get("quote") or {}
    qa = parse_ts(q.get("captured_at"))
    if not q or num(q.get("price")) is None:
        blocks.append("MISSING_QUOTE")
    else:
        if qa is None:
            blocks.append("MISSING_QUOTE_TIME")
        elif dec is not None:
            age = _age_min(dec, qa)
            if age < 0:
                blocks.append("QUOTE_AFTER_DECISION")
            elif age > max_quote_age_min:
                blocks.append("STALE_QUOTE")
        kind = q.get("kind")
        if kind in EXECUTABLE_KINDS:
            depth, need = num(q.get("depth")), num(c.get("contracts"))
            if depth is None:
                warns.append("DEPTH_UNKNOWN")
            elif need is not None and depth < need:
                blocks.append("INSUFFICIENT_DEPTH")
        elif kind in CAPTURED_ONLY_KINDS:
            blocks.append("PRICE_NOT_EXECUTABLE")   # captured is evidence about the market; only an ask is a price you can pay
        else:
            blocks.append("PRICE_PROVENANCE_UNKNOWN")
    return {"ticker": c.get("ticker"), "actionable": not blocks, "blocks": sorted(set(blocks)), "warnings": warns}


def guard_candidates(cands: list, **kw) -> list:
    """Order-preserving; never reorders, adds or drops a candidate."""
    return [guard_candidate(c, **kw) for c in cands]
