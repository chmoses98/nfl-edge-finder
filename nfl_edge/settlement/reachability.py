"""SETTLEMENT REACHABILITY: can this record actually be settled, measured on the record, not on the catalog.

The previous "zero probability records without a settlement path" claim was circular. It was computed from
`flags.settlement_supported`, which is derived from the family catalog:

    settlement_supported = (catalog entry says SUPPORTED)

so editing the catalog to mark three families SUPPORTED flipped the flag on 1,336 season records that the
settlement driver never even looked at -- it buckets by `game_id`, and every season record has none. The metric
measured a catalog edit rather than a code path.

Reachability is therefore defined here, once, as a property of the RECORD:

    a settlement branch exists for this family  AND  the record carries the keys that branch needs

and the same function is used by the projection flags, the settlement driver and the coverage matrix. A record
that is not dispatchable says so, with the specific key it lacks; nothing is silently dropped.

SCOPES
------
    GAME    every game-scoped family: needs `game_id`, and settles once that game is proven final
    PLAYER  as GAME, plus a resolved `subject_id` (a GSIS id)
    SEASON  needs `season` and `subject_id` (a team); has no kickoff and never will

THE SEASON YEAR
---------------
Season markets carry a two-digit year in the event ticker (`KXNFLAFCEAST-27-NYJ`) and it is NOT the nflverse
season: the division markets expire 2027-01-11 and the conference markets 2027-02-08, i.e. the end of the 2026
NFL season. So Kalshi's N means nflverse season N-1. Rather than trust one reading, both signals are taken --
the ticker's year and the contract's own expiration year -- and a disagreement REFUSES rather than picks.

Version: reachability-1.0.0.
"""
from __future__ import annotations

import re

REACHABILITY_VERSION = "reachability-1.0.0"

DISPATCHABLE = "DISPATCHABLE"                     # a branch exists and the record carries its keys
MISSING_KEYS = "MISSING_SETTLEMENT_KEYS"          # a branch exists; the record cannot reach it
NO_BRANCH = "NO_SETTLEMENT_BRANCH"                # no settlement branch for this family
NO_PROBABILITY = "NO_PROBABILITY"                 # nothing to settle

GAME, PLAYER, SEASON = "GAME", "PLAYER", "SEASON"

# Families the v2 settlement dispatcher actually implements, and the scope each needs.
SEASON_FAMILIES = ("SEASON_WINS", "SEASON_WINS_EXACT", "TEAM_WINS_BY_WEEK", "MAKE_PLAYOFFS", "DIVISION_WINNER")
GAME_FAMILIES = ("GAME_WINNER", "SPREAD", "TOTAL", "TEAM_TOTAL", "BOTH_TEAMS_SCORE_N", "WIN_MARGIN_BUCKET",
                 "PERIOD_WINNER", "BOTH_TEAMS_SCORE", "HALF_FULL_RESULT")
PLAYER_FAMILIES = ("PLAYER_STAT",)

_YEAR_RE = re.compile(r"-(\d{2})-")


def _year_from_ticker(ticker: str | None, event_ticker: str | None):
    for s in (event_ticker or "", ticker or ""):
        m = _YEAR_RE.search(s)
        if m:
            return 2000 + int(m.group(1))
    return None


def season_of(rec: dict):
    """The nflverse season a season-scoped contract is about, or (None, reason).

    Two independent readings must agree: the ticker's two-digit year and the contract's own expiration year,
    each meaning "the season ENDING in that year", i.e. nflverse season = year - 1.
    """
    if rec.get("season") is not None:
        return int(rec["season"]), None
    ticket_year = _year_from_ticker(rec.get("ticker"), rec.get("event_ticker"))
    exp = rec.get("expected_expiration_time") or rec.get("close_time")
    exp_year = None
    if exp:
        m = re.match(r"(\d{4})-", str(exp))
        if m:
            exp_year = int(m.group(1))
    if ticket_year is None and exp_year is None:
        return None, "no season year in the ticker and no expiration to cross-check"
    if ticket_year is not None and exp_year is not None and ticket_year != exp_year:
        return None, (f"season year disagrees: ticker says {ticket_year}, expiration says {exp_year}; "
                      "refusing rather than choosing")
    year = ticket_year if ticket_year is not None else exp_year
    return year - 1, None


def scope_of(family: str | None, engine: str | None = None) -> str | None:
    if not family:
        return None
    if family in SEASON_FAMILIES or (engine == "SEASON"):
        return SEASON
    if family in PLAYER_FAMILIES or (engine == "PLAYER"):
        return PLAYER
    if family in GAME_FAMILIES or (engine in ("GAME", "PERIOD", "JOINT")):
        return GAME
    return None


def reachability(rec: dict) -> dict:
    """Is this record dispatchable to a real settlement branch? One answer, used by every consumer."""
    out = {"reachability_version": REACHABILITY_VERSION, "scope": None, "state": None, "reason": None,
           "missing": [], "season": rec.get("season")}
    if rec.get("p_yes") is None and rec.get("contract_value") is None:
        return {**out, "state": NO_PROBABILITY, "reason": "record carries no probability"}
    fam, engine = rec.get("market_family"), rec.get("engine")
    scope = scope_of(fam, engine)
    out["scope"] = scope
    if scope is None:
        return {**out, "state": NO_BRANCH, "reason": f"no settlement branch for family {fam!r}"}
    if scope == SEASON:
        if fam not in SEASON_FAMILIES:
            return {**out, "state": NO_BRANCH, "reason": f"season-scoped family {fam!r} has no settlement branch"}
        season, why = season_of(rec)
        missing = []
        if season is None:
            missing.append("season")
        if not rec.get("subject_id"):
            missing.append("subject_id")
        if missing:
            return {**out, "state": MISSING_KEYS, "missing": missing,
                    "reason": why or f"season record lacks {', '.join(missing)}"}
        return {**out, "state": DISPATCHABLE, "season": season,
                "reason": f"season {season} team {rec['subject_id']} dispatches to the season settlement branch"}
    missing = []
    if not rec.get("game_id"):
        missing.append("game_id")
    if scope == PLAYER and not rec.get("subject_id"):
        missing.append("subject_id")
    if missing:
        return {**out, "state": MISSING_KEYS, "missing": missing,
                "reason": f"{scope.lower()}-scoped record lacks {', '.join(missing)}"}
    return {**out, "state": DISPATCHABLE, "reason": f"{scope.lower()}-scoped record dispatches on game {rec['game_id']}"}


def is_reachable(rec: dict) -> bool:
    return reachability(rec)["state"] == DISPATCHABLE


def summarize(records) -> dict:
    """The honest settlement-coverage metric: measured on dispatchability, never on catalog metadata."""
    by_state, by_family, missing = {}, {}, {}
    n_prob = 0
    for r in records:
        rr = reachability(r)
        st = rr["state"]
        by_state[st] = by_state.get(st, 0) + 1
        if st == NO_PROBABILITY:
            continue
        n_prob += 1
        fam = r.get("market_family") or "UNKNOWN"
        d = by_family.setdefault(fam, {"n": 0, DISPATCHABLE: 0, MISSING_KEYS: 0, NO_BRANCH: 0})
        d["n"] += 1
        d[st] = d.get(st, 0) + 1
        for k in rr["missing"]:
            missing[k] = missing.get(k, 0) + 1
    reach = by_state.get(DISPATCHABLE, 0)
    return {"reachability_version": REACHABILITY_VERSION, "probability_carrying": n_prob,
            "dispatchable": reach, "not_dispatchable": n_prob - reach,
            "dispatchable_pct": round(100.0 * reach / n_prob, 2) if n_prob else None,
            "by_state": by_state, "missing_keys": missing,
            "families_not_dispatchable": sorted(f for f, d in by_family.items() if d[DISPATCHABLE] < d["n"]),
            "by_family": by_family}
