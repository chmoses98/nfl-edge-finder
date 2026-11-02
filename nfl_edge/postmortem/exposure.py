"""Game-thesis correlation aggregation and aggregate game / daily exposure, in units. FLAGS ONLY, NEVER CAPS.

docs/NFL_OPERATING_POLICY.md deliberately has no per-game or per-slate cap (commit febfe43) and a strict 5U budget per
correlation group. This module reports, after the fact or before a bet, how much money sat on one football view:

* PRIMARY AXIS of every single-game score position (one axis each, so nothing is double counted inside a group):
    MARGIN:<team>        spread / alternate spread / moneyline, any period (1Q, 1H, full), either side encoding
                         (YES on X's spread == NO on the opponent's spread == a view that X does better)
    TOTAL:OVER|UNDER     game total ladders, any period
    TEAMSCORE:<team>:OVER|UNDER   team-total ladders, any period
  Rungs of one ladder (SF3, SF4, SF7...) therefore share an axis and cannot be mistaken for independent bets.
* CROSS-AXIS LINKS (reported, not merged): a team total OVER for X leans on the same game state as MARGIN:X and
  TOTAL:OVER. They are listed as ``linked_groups`` with combined units so a reviewer sees the thesis, without
  silently merging separate theses the policy treats as independent.
* GAME total = every position on the game, plus decoded combos that touch it. Flag when > GAME_EXPOSURE_FLAG_UNITS.
* DAY total = every position (undecodable combos included) by game date. Flag when > DAILY_EXPOSURE_FLAG_UNITS.

Stake already includes the entry fee (router-settlement-economics.v2). Units use the fixed $75 unit.
Opposing positions on one axis are reported GROSS (what was at risk) and NET (directional lean).
"""
from __future__ import annotations

import re
from collections import defaultdict

from .common import DAILY_EXPOSURE_FLAG_UNITS, GAME_EXPOSURE_FLAG_UNITS, UNIT_DOLLARS, num, parse_ts
from .ontology import COMBO_DECODED, COMBO_UNDECODED, SINGLE, ContractOntology, classify_ticker, spread_team_and_line

_TEAM_NUM = re.compile(r"^([A-Z]+?)(\d+(?:\.\d+)?)$")


def _split_teams(token: str | None, team: str):
    """Opponent code inside an event teams token (SFATL, team SF -> ATL). None when the token is ambiguous."""
    if not token or not team or team not in token:
        return None
    if token.startswith(team):
        return token[len(team):] or None
    if token.endswith(team):
        return token[:-len(team)] or None
    return None


def axis_of(ont: ContractOntology, side: str):
    """(axis_key, lean) for a single-game score position, or (None, reason)."""
    if ont.kind != SINGLE or ont.family not in ("GAME_WINNER", "SPREAD", "TOTAL", "TEAM_TOTAL"):
        return None, "NOT_A_SCORE_POSITION"
    if side not in ("YES", "NO"):
        return None, "MISSING_SIDE"
    if ont.family == "TOTAL":
        return "TOTAL:" + ("OVER" if side == "YES" else "UNDER"), "total"
    if ont.family == "TEAM_TOTAL":
        m = _TEAM_NUM.match(ont.subject or "")
        if not m:
            return None, "UNPARSEABLE_TEAM_TOTAL_SUBJECT"
        return f"TEAMSCORE:{m.group(1)}:" + ("OVER" if side == "YES" else "UNDER"), "team_total"
    # margin axis
    if ont.family == "SPREAD":
        parsed = spread_team_and_line(ont)
        team = parsed[0] if parsed else None
    else:
        team = (ont.subject or "").strip() or None
    if not team:
        return None, "UNPARSEABLE_MARGIN_SUBJECT"
    if side == "YES":
        return f"MARGIN:{team}", "margin"
    opp = _split_teams(ont.teams_token, team)
    if not opp:
        return None, "OPPONENT_AMBIGUOUS"
    return f"MARGIN:{opp}", "margin"


def _linked_axes(axis: str):
    """Other axes that lean on the same game state (documented, owner-adjustable)."""
    kind = axis.split(":")[0]
    if kind == "TEAMSCORE":
        _, team, direction = axis.split(":")
        return [f"MARGIN:{team}"] if direction == "OVER" else [], ["TOTAL:" + direction]
    return [], []


def position_units(pos: dict):
    stake = num(pos.get("stake"))
    return None if stake is None else stake / UNIT_DOLLARS


def aggregate(positions: list, *, legs_by_ticker: dict | None = None,
              game_flag_units: float = GAME_EXPOSURE_FLAG_UNITS, daily_flag_units: float = DAILY_EXPOSURE_FLAG_UNITS,
              group_flag_units: float = GAME_EXPOSURE_FLAG_UNITS) -> dict:
    """positions: dicts with ticker, side, stake (dollars, fee-inclusive), game_date and/or executed_at.
    Returns a plain-dict report. Never raises on bad rows: they appear under ``unprocessed`` with a reason."""
    legs_by_ticker = legs_by_ticker or {}
    games = defaultdict(lambda: {"singles": [], "combos": []})
    days = defaultdict(lambda: {"units": 0.0, "n": 0, "undecoded_combo_units": 0.0, "flags": set()})
    unprocessed, flags = [], []
    for i, pos in enumerate(positions):
        u = position_units(pos)
        if u is None or u < 0:
            unprocessed.append({"index": i, "reason": "MISSING_STAKE"})
            continue
        ont = classify_ticker(pos.get("ticker") or pos.get("market_ticker"), legs=legs_by_ticker.get(pos.get("ticker") or pos.get("market_ticker")))
        day = (str(pos.get("game_date"))[:10] if pos.get("game_date") else None)
        day_flag = None
        if not day and ont.date_token:
            day, day_flag = ont.date_token, "DAY_FROM_TICKER_TOKEN"
        if not day:
            ts = parse_ts(pos.get("executed_at"))
            if ts:
                day, day_flag = ts.date().isoformat(), "DAY_FROM_EXECUTION_TIME"
        if not day:
            day, day_flag = "UNKNOWN_DAY", "MISSING_DAY"
        d = days[day]
        d["units"] += u
        d["n"] += 1
        if day_flag:
            d["flags"].add(day_flag)
        side = pos.get("side")
        if ont.kind == COMBO_UNDECODED:
            d["undecoded_combo_units"] += u
            games["UNATTRIBUTED_COMBOS"]["combos"].append({"units": u, "ticker_series": ont.series, "flags": list(ont.flags)})
            continue
        if ont.kind == COMBO_DECODED:
            for g in ont.games or ("UNATTRIBUTED_COMBOS",):
                games[g]["combos"].append({"units": u, "ticker_series": ont.series, "attribution": "FULL_STAKE_PER_GAME"})
            continue
        axis, lean = axis_of(ont, side)
        if ont.game_key is None:
            unprocessed.append({"index": i, "reason": "NO_GAME_EVENT_TOKEN"})
            continue
        games[ont.game_key]["singles"].append({"units": u, "axis": axis, "axis_problem": None if axis else lean,
                                              "ticker": ont.ticker, "side": side, "family": ont.family, "period": ont.period})
    game_out = {}
    for g, bundle in sorted(games.items()):
        single_units = sum(s["units"] for s in bundle["singles"])
        combo_units = sum(c["units"] for c in bundle["combos"])
        by_axis = defaultdict(lambda: {"gross_units": 0.0, "n": 0, "rungs": set(), "periods": set()})
        loose = 0.0
        for s in bundle["singles"]:
            if s["axis"] is None:
                loose += s["units"]
                continue
            a = by_axis[s["axis"]]
            a["gross_units"] += s["units"]
            a["n"] += 1
            a["rungs"].add(s["ticker"])
            a["periods"].add(s["period"])
        groups = []
        for axis, a in sorted(by_axis.items()):
            margin_links, total_links = _linked_axes(axis)
            linked = [x for x in margin_links + total_links if x in by_axis]
            groups.append({"axis": axis, "gross_units": round(a["gross_units"], 4), "n_positions": a["n"],
                           "n_distinct_contracts": len(a["rungs"]), "periods": sorted(a["periods"]),
                           "flag_over_group_limit": a["gross_units"] > group_flag_units,
                           "linked_axes": linked,
                           "linked_combined_units": round(a["gross_units"] + sum(by_axis[x]["gross_units"] for x in linked), 4)})
        total = single_units + combo_units
        game_out[g] = {"units_total": round(total, 4), "single_units": round(single_units, 4), "combo_units": round(combo_units, 4),
                       "unclassified_axis_units": round(loose, 4), "groups": groups,
                       "flag_over_game_limit": g != "UNATTRIBUTED_COMBOS" and total > game_flag_units,
                       "game_limit_units": game_flag_units}
        if game_out[g]["flag_over_game_limit"]:
            flags.append({"kind": "GAME_OVER_LIMIT", "game": g, "units": round(total, 4), "limit": game_flag_units})
        for grp in groups:
            if grp["flag_over_group_limit"]:
                flags.append({"kind": "GROUP_OVER_LIMIT", "game": g, "axis": grp["axis"], "units": grp["gross_units"], "limit": group_flag_units})
    day_out = {}
    for day, d in sorted(days.items()):
        day_out[day] = {"units_total": round(d["units"], 4), "n_positions": d["n"],
                        "undecoded_combo_units": round(d["undecoded_combo_units"], 4), "flags": sorted(d["flags"]),
                        "flag_over_daily_limit": d["units"] > daily_flag_units, "daily_limit_units": daily_flag_units}
        if day_out[day]["flag_over_daily_limit"]:
            flags.append({"kind": "DAY_OVER_LIMIT", "day": day, "units": round(d["units"], 4), "limit": daily_flag_units})
    return {"unit_dollars": UNIT_DOLLARS, "policy_note": "flags only; no cap is applied or implied (NFL_OPERATING_POLICY section 1)",
            "games": game_out, "days": day_out, "flags": flags, "unprocessed": unprocessed}
