"""MARKET COHERENCE ENGINE: a model-free structural audit of mutually exclusive / exhaustive contract groups.

An event's outcomes (the seven margin buckets of a game; home / away / tie of a period; the 32 division-winner
strikes across eight events; the sixteen seeds) partition a sample space, so their probabilities must sum to
one. The market need not: each contract is quoted on its own. This engine groups contracts by the semantics
engine's questions, decides what kind of set the group is, and computes

    research incoherence      sum of the midpoints (a probability statement, not an economic one)
    executable bounds         sum of the YES bids (what selling every leg pays) and sum of the YES asks (what buying
                              every leg costs), with the exchange fee applied ONCE per leg through the committed
                              schedule; the executable opportunity exists only if buying all legs costs < 1 or
                              selling all legs pays > 1 AFTER fees, with every leg quoted two-sided at the same instant

Nothing is called "arbitrage" unless the executable economics justify it; a group whose legs are missing or
whose set kind is PARTIAL / AMBIGUOUS is reported as such and never as an opportunity.
"""
from __future__ import annotations

from collections import defaultdict

from nfl_edge.execution import fees as F
from nfl_edge.semantics.questions import EVENT, RANGE, Question

ENGINE_VERSION = "coherence-engine-1.0.0"
MUTUALLY_EXCLUSIVE, COLLECTIVELY_EXHAUSTIVE, PARTIAL_SET, AMBIGUOUS = "MUTUALLY_EXCLUSIVE", "COLLECTIVELY_EXHAUSTIVE", "PARTIAL_SET", "AMBIGUOUS"

# how a family's event ticker maps to an outcome group and what a complete group looks like
GROUP_RULES = {
    "WIN_MARGIN_BUCKET": {"key": "event", "complete": "margin_partition"},
    "GAME_WINNER": {"key": "event", "complete": "two_teams_plus_optional_tie"},
    "PERIOD_WINNER": {"key": "event", "complete": "two_teams_plus_tie"},
    "FIRST_TD_TEAM": {"key": "event", "complete": "two_teams_plus_none"},
    "RACE_TO_N": {"key": "event", "complete": "two_teams_plus_none"},
    "HALF_FULL_RESULT": {"key": "event", "complete": "nine_cells"},
    "DIVISION_WINNER": {"key": "event", "complete": "four_teams"},
    "CONFERENCE_WINNER": {"key": "event", "complete": "sixteen_teams"},
    "SUPER_BOWL_WINNER": {"key": "event", "complete": "thirty_two_teams"},
    "SEASON_SEED": {"key": "event", "complete": "sixteen_teams"},
    "SEASON_WINS_EXACT": {"key": "event", "complete": "wins_0_17"},
    "FIRST_TD_SCORER": {"key": "event", "complete": "open_roster_plus_none"},
}


def _f(x):
    try:
        return None if x is None else float(x)
    except (TypeError, ValueError):
        return None


def set_kind(family: str, legs: list) -> tuple[str, str]:
    """Decide ME / CE / PARTIAL / AMBIGUOUS for one group from its parsed questions."""
    rule = GROUP_RULES.get(family)
    if rule is None:
        return AMBIGUOUS, "family has no group rule"
    n = len(legs)
    if family == "WIN_MARGIN_BUCKET":
        teams = defaultdict(list); tie = 0
        for l in legs:
            q = l["question"]
            if q.kind == EVENT and q.event == "TIE":
                tie += 1
            elif q.kind == RANGE and q.stat == "margin":
                teams[q.subject].append((q.lo, q.hi))
            elif q.kind == RANGE and q.stat == "abs_margin":
                teams["EITHER"].append((q.lo, q.hi))
        for t, rs in teams.items():
            rs.sort(key=lambda r: (r[0], r[1] if r[1] is not None else 1e9))
            for (lo1, hi1), (lo2, _) in zip(rs, rs[1:]):
                if hi1 is None or lo2 <= hi1:
                    return AMBIGUOUS, f"overlapping buckets for {t}"
        if "EITHER" in teams:
            rs = teams["EITHER"]
            ce = tie == 1 and rs[0][0] == 1 and rs[-1][1] is None and all(a[1] is not None and b[0] == a[1] + 1 for a, b in zip(rs, rs[1:]))
            return (COLLECTIVELY_EXHAUSTIVE if ce else PARTIAL_SET), "either-team buckets" + ("" if ce else " (gaps, no tie, or capped top)")
        ce = tie == 1 and len(teams) == 2 and all(rs[0][0] == 1 and rs[-1][1] is None and all(a[1] is not None and b[0] == a[1] + 1 for a, b in zip(rs, rs[1:])) for rs in teams.values())
        return (COLLECTIVELY_EXHAUSTIVE if ce else (MUTUALLY_EXCLUSIVE if teams else AMBIGUOUS)), ("both teams' buckets tile 1..inf plus a tie leg" if ce else "buckets exclusive but the set is incomplete")
    if family in ("GAME_WINNER", "PERIOD_WINNER"):
        teams = {l["question"].subject for l in legs if l["question"].event == "WIN"}
        tie = any(l["question"].event == "TIE" for l in legs)
        if len(teams) == 2 and (tie or family == "GAME_WINNER"):
            return COLLECTIVELY_EXHAUSTIVE, ("two teams + tie leg" if tie else "two teams; a tie pays $0.50 per side so the pair sums to one in expectation")
        return (MUTUALLY_EXCLUSIVE if teams else AMBIGUOUS), f"{len(teams)} team legs, tie={tie}"
    if family in ("FIRST_TD_TEAM", "RACE_TO_N"):
        teams = {l["question"].subject for l in legs if l["question"].subject}
        none = any(l["question"].event in ("NO_TD", "RACE_NONE") for l in legs)
        return (COLLECTIVELY_EXHAUSTIVE if (len(teams) == 2 and none) else MUTUALLY_EXCLUSIVE), f"{len(teams)} teams, none-leg={none}"
    if family == "HALF_FULL_RESULT":
        return (COLLECTIVELY_EXHAUSTIVE if n == 9 else PARTIAL_SET), f"{n} of 9 cells"
    if family == "DIVISION_WINNER":
        return (COLLECTIVELY_EXHAUSTIVE if n == 4 else PARTIAL_SET), f"{n} of 4 teams"
    if family in ("CONFERENCE_WINNER", "SEASON_SEED"):
        return (COLLECTIVELY_EXHAUSTIVE if n == 16 else PARTIAL_SET), f"{n} of 16 teams"
    if family == "SUPER_BOWL_WINNER":
        return (COLLECTIVELY_EXHAUSTIVE if n == 32 else PARTIAL_SET), f"{n} of 32 teams"
    if family == "SEASON_WINS_EXACT":
        ks = sorted(l["question"].k for l in legs if l["question"].k is not None)
        return (COLLECTIVELY_EXHAUSTIVE if ks == list(range(0, 18)) else PARTIAL_SET), f"{len(ks)} exact-win legs"
    if family == "FIRST_TD_SCORER":
        return PARTIAL_SET, "open roster; the NONE leg completes it only with every eligible scorer listed"
    return AMBIGUOUS, "unhandled"


def audit_group(family: str, group_key: str, legs: list, schedule, as_of) -> dict:
    """legs: dicts with ticker, question, yes_bid, yes_ask, volume, liquidity, series_ticker."""
    kind, why = set_kind(family, legs)
    mids, bids, asks = [], [], []
    quoted, missing_quote, fee_unknown = 0, 0, 0
    fee_buy_total, fee_sell_total = 0.0, 0.0
    for l in legs:
        b, a = _f(l.get("yes_bid")), _f(l.get("yes_ask"))
        if b is None or a is None or not (0 <= b <= a <= 1):
            missing_quote += 1
            continue
        quoted += 1
        mids.append((a + b) / 2.0); bids.append(b); asks.append(a)
        # fee applied exactly once per leg, on the executable price, through the committed schedule
        try:
            fb = F.net_executable_ev(a, a, 1.0, schedule, series_ticker=l.get("series_ticker"), as_of=as_of)
            fs = F.net_executable_ev(1.0 - b, 1.0 - b, 1.0, schedule, series_ticker=l.get("series_ticker"), as_of=as_of)
            if not (fb.is_known and fs.is_known):
                fee_unknown += 1
            else:
                fee_buy_total += -float(fb.net_ev_dollars)          # net EV at fair == price is minus the fee
                fee_sell_total += -float(fs.net_ev_dollars)
        except Exception:  # noqa: BLE001
            fee_unknown += 1
    two_sided = quoted == len(legs) and quoted > 0
    out = {"family": family, "group": group_key, "n_legs": len(legs), "n_quoted": quoted, "n_missing_quote": missing_quote,
           "set_kind": kind, "set_reason": why, "sum_mid": (sum(mids) if mids else None),
           "sum_bid": (sum(bids) if bids else None), "sum_ask": (sum(asks) if asks else None),
           "fees_buy_all": fee_buy_total if not fee_unknown else None, "fees_sell_all": fee_sell_total if not fee_unknown else None,
           "fee_unknown_legs": fee_unknown, "liquidity_min": min((_f(l.get("liquidity")) or 0.0) for l in legs) if legs else None,
           "volume_min": min((_f(l.get("volume")) or 0.0) for l in legs) if legs else None,
           "research_incoherence": None, "executable_opportunity": None, "executable_reason": None}
    if kind in (COLLECTIVELY_EXHAUSTIVE,) and mids and two_sided:
        out["research_incoherence"] = sum(mids) - 1.0
    if kind == COLLECTIVELY_EXHAUSTIVE and two_sided and not fee_unknown:
        cost_buy_all = sum(asks) + fee_buy_total          # pays exactly $1 at settlement
        pay_sell_all = sum(bids) - fee_sell_total         # owes exactly $1 at settlement
        if cost_buy_all < 1.0 - 1e-9:
            out.update(executable_opportunity="BUY_ALL", executable_reason=f"buying every leg costs {cost_buy_all:.4f} incl. fees for a certain $1")
        elif pay_sell_all > 1.0 + 1e-9:
            out.update(executable_opportunity="SELL_ALL", executable_reason=f"selling every leg pays {pay_sell_all:.4f} net of fees against a certain $1 liability")
        else:
            out.update(executable_opportunity=None, executable_reason=f"buy-all {cost_buy_all:.4f} >= 1 and sell-all {pay_sell_all:.4f} <= 1 after fees")
        out["cost_buy_all_after_fees"] = cost_buy_all; out["pay_sell_all_after_fees"] = pay_sell_all
    elif kind == COLLECTIVELY_EXHAUSTIVE and not two_sided:
        out["executable_reason"] = "not every leg is two-sided at this instant; no executable statement"
    elif kind == COLLECTIVELY_EXHAUSTIVE and fee_unknown:
        out["executable_reason"] = "fee schedule not KNOWN for a leg; no executable statement"
    elif kind == MUTUALLY_EXCLUSIVE and mids and two_sided:
        # exclusive but not exhaustive: only the SELL side has a certain bound (at most one leg pays)
        out["research_incoherence"] = max(0.0, sum(mids) - 1.0) or None
        if not fee_unknown and sum(bids) - fee_sell_total > 1.0 + 1e-9:
            out.update(executable_opportunity="SELL_ALL", executable_reason="exclusive legs whose bids sum above one after fees")
    return out


def group_contracts(rows: list, questions: dict) -> dict:
    """rows: capture-shaped dicts with ticker/event_ticker/series_ticker/family + quotes; questions: ticker -> Question."""
    groups = defaultdict(list)
    for r in rows:
        fam = r.get("family")
        if fam not in GROUP_RULES:
            continue
        q = questions.get(r.get("ticker"))
        if q is None:
            continue
        key = r.get("event_ticker")
        if fam == "RACE_TO_N":
            key = r.get("event_ticker")                       # KXNFLRACE-<game>-<N> already carries N
        groups[(fam, key)].append({**r, "question": q})
    return groups


def audit_board(rows: list, questions: dict, schedule, as_of) -> dict:
    groups = group_contracts(rows, questions)
    results = [audit_group(fam, key, legs, schedule, as_of) for (fam, key), legs in sorted(groups.items())]
    n_ce = sum(1 for r in results if r["set_kind"] == COLLECTIVELY_EXHAUSTIVE)
    inco = [r for r in results if r["research_incoherence"] is not None]
    opp = [r for r in results if r["executable_opportunity"]]
    return {"engine_version": ENGINE_VERSION, "n_groups": len(results), "by_kind": _count(results, "set_kind"),
            "n_collectively_exhaustive": n_ce, "n_with_research_incoherence": len(inco),
            "n_abs_incoherence_gt_2c": sum(1 for r in inco if abs(r["research_incoherence"]) > 0.02),
            "n_abs_incoherence_gt_5c": sum(1 for r in inco if abs(r["research_incoherence"]) > 0.05),
            "n_executable_opportunities": len(opp), "executable": opp[:50], "groups": results}


def _count(rows, key):
    c = defaultdict(int)
    for r in rows:
        c[str(r.get(key))] += 1
    return dict(c)
