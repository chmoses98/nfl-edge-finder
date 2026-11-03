"""Point-in-time evidence guards for GAME-LEVEL markets. RESTRICTION-ONLY: a guard can only turn actionable -> blocked.

The existing real-money gates (nfl_edge/handicap/gates.py) already enforce decision-before-kickoff, 15-minute quote
and book freshness, fee-schedule verification, depth and net EV, and an availability gate for PLAYER markets only.
What was not enforced for spreads, alternates, 1Q/1H/team totals and totals is that the PROJECTION behind the number,
the injury snapshot and the QUARTERBACK status were fresh, point-in-time, and confirmed. Those are added here, plus a
price-provenance check (a captured mid is not an executable ask).

WIRED into handicap/gates.py (G_PIT) through integration.pit_gate / pit_applies, owner-approved on PR #232. Which markets need which
quarterbacks is decided by the explicit table in qb_dependency.py (PR #241); what counts as a valid confirmation for a game is decided by
qb_confirmations.resolve_team and re-checked here (_qb_blocks), so a row that arrives by any other road is judged again.

Every time argument is explicit: there is no wall-clock default, and naive timestamps are refused (None).
"""
from __future__ import annotations

from .common import MAX_INJURY_AGE_MIN, MAX_PROJECTION_AGE_MIN, MAX_QUOTE_AGE_MIN, num, parse_ts
from . import qb_confirmations as QBC
from . import qb_dependency as QD
from .ontology import classify_ticker

EXECUTABLE_KINDS = ("EXECUTABLE_ASK",)
CAPTURED_ONLY_KINDS = ("CAPTURED_MID", "CAPTURED_LAST", "CAPTURED_BID", "CLOSE_MID", "MODEL_IMPLIED")
QB_CONFIRMED = "CONFIRMED_STARTER"

#: Compat view: the family NAMES whose table entry is QB_GATED. The gate no longer consults a list of gated families: it asks
#: ``qb_dependency.requirement`` (every recognised family has an explicit entry; anything unrecognised is gated). See qb_dependency.py.
QB_GATED_FAMILIES = QD.gated_family_names()


def _age_min(decision, then):
    return None if decision is None or then is None else (decision - then).total_seconds() / 60.0


def _qb_blocks(team, row, *, dec, ko, game_id, max_age, max_lead) -> list:
    """Every reason one team's quarterback row does not establish a CONFIRMED starter for THIS game at THIS decision. Defence in depth: the
    resolver already applies these rules, but a row that arrives by any other road (a hand-built dict, an old record) is re-judged here."""
    if not row or not isinstance(row, dict):
        return [f"QB_UNKNOWN:{team}"]
    out = []
    if row.get("status") != QB_CONFIRMED:
        out.append(f"QB_NOT_CONFIRMED:{team}")
        if row.get("reason"):
            out.append(f"QB_REASON:{team}:{row['reason']}")
        return out
    if row.get("source") not in QBC.CONFIRMING_SOURCE_TYPES:
        out.append(f"QB_SOURCE_NOT_ACCEPTED:{team}")          # a depth chart / roster / injury report / model, or no source at all
    if game_id is not None and row.get("game_id") != game_id:
        out.append(f"QB_WRONG_GAME:{team}")                   # a confirmation for another game (or one that does not say which) is not this game's
    if row.get("team") is not None and row.get("team") != team:
        out.append(f"QB_WRONG_TEAM:{team}")
    ct = parse_ts(row.get("confirmed_at"))
    if ct is None:
        out.append(f"QB_CONFIRMATION_TIME_MISSING:{team}")
    else:
        if dec is not None:
            if ct > dec:
                out.append(f"QB_CONFIRMED_AFTER_DECISION:{team}")
            elif (dec - ct).total_seconds() / 60.0 > max_age:
                out.append(f"QB_CONFIRMATION_STALE:{team}")
        if ko is not None:
            if ct >= ko:
                out.append(f"QB_CONFIRMED_AT_OR_AFTER_KICKOFF:{team}")
            elif (ko - ct).total_seconds() / 60.0 > max_lead:
                out.append(f"QB_CONFIRMATION_TOO_EARLY_BEFORE_KICKOFF:{team}")
    return out


def guard_candidate(c: dict, *, max_projection_age_min=MAX_PROJECTION_AGE_MIN, max_injury_age_min=MAX_INJURY_AGE_MIN,
                    max_quote_age_min=MAX_QUOTE_AGE_MIN, max_qb_age_min=QBC.MAX_AGE_AT_DECISION_MIN,
                    max_qb_lead_min=QBC.MAX_LEAD_BEFORE_KICKOFF_MIN, require_qb_for=()) -> dict:
    """c keys: ticker, family (optional: the record's market_family), game_id (optional), side, decision_time, kickoff_utc, projection_as_of,
    injuries_as_of, qb {TEAM: row}, teams [home, away], quote {price, captured_at, kind, depth}, contracts.
    Returns {actionable, blocks[], warnings[], qb_requirement, qb_provenance}.

    ``require_qb_for`` can only ADD ontology families to the table's requirement (it can never switch the check off)."""
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

    # --- confirmed quarterbacks (table-driven: qb_dependency.requirement; unknown family -> gated)
    teams = list(c.get("teams") or [])
    req = QD.requirement(c.get("ticker"), family=c.get("family"), teams=teams)
    extra = ont.family in require_qb_for
    need_qb = req.requires_confirmation or extra
    qb_prov = {}
    if need_qb:
        qb = c.get("qb") or {}
        if len(teams) != 2:
            blocks.append("MISSING_TEAMS_FOR_QB_CHECK")
        required = list(req.teams_required) if (req.requires_confirmation and req.teams_required) else teams
        for team in required:
            row = qb.get(team)
            blocks.extend(_qb_blocks(team, row, dec=dec, ko=ko, game_id=c.get("game_id"), max_age=max_qb_age_min, max_lead=max_qb_lead_min))
            if isinstance(row, dict):
                qb_prov[team] = {k: row.get(k) for k in ("status", "reason", "source", "source_ref", "record_id", "qb_player_id", "observed_at",
                                                         "captured_at", "confirmed_at", "as_of", "kickoff_utc", "game_id")}

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
    return {"ticker": c.get("ticker"), "actionable": not blocks, "blocks": sorted(set(blocks)), "warnings": warns,
            "qb_requirement": req.to_dict(), "qb_provenance": qb_prov}


def guard_candidates(cands: list, **kw) -> list:
    """Order-preserving; never reorders, adds or drops a candidate."""
    return [guard_candidate(c, **kw) for c in cands]
