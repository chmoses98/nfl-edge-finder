"""Best-market-expression engine: given a football thesis, which contract expresses it best, and at what price does it stop being worth it?

A thesis is a claim about the game ("PIT is worth 1 to 2.5 points more than the market has it"). Many contracts express it -- the
moneyline, every spread rung, the team total, an alternate total, a player's line -- and they are NOT equal: they pay under different
scripts, cost different fees, carry different spreads and depth, and sit at different distances from fair. This module prices every
expression it honestly can on ONE footing, compares them, and says why the winner won and why each loser lost.

TWO KINDS OF FAIR VALUE, KEPT APART
-----------------------------------
1. DERIVED (`fairvalue.py`): full-game moneyline / spread / total / team-total contracts, from the market-centred simulation shifted by the
   thesis's RANGE, widened by the engine's own noise against the unopinionated market. Reproducible; consistent across expressions.
2. DECLARED: the analyst states an explicit fair range for a contract that cannot be derived (a player prop, a period market) and
   names its basis. It is recorded as the analyst's range, never as a model probability.
A contract with neither has `NO_DEFENSIBLE_FAIR_ESTIMATE`: it is shown for context and CANNOT be ranked, staked or recommended. No number
is invented to fill the column. A research arm (Shadow v2, coherent simulation, DATA_PLAYER_*) may be cited as context beside a row; it
never becomes its fair value.

Everything is evaluated at the EXECUTABLE ask of the side taken (YES -> yes_ask, NO -> no_ask), after the Kalshi taker fee for that series
from the versioned fee schedule. A midpoint is never a price.
"""
from __future__ import annotations

import math

from nfl_edge.execution import fees as F
from nfl_edge.handicap import fairvalue as FV
from nfl_edge.handicap import ladder_fair as LF

EXPRESSION_VERSION = "expression-1.0.0"
MIN_NET_EDGE = 0.02             # per contract at the conservative end of the fair range; the 1U requirement in staking.py
MAX_WIDTH = 0.08                # an executable book wider than 8c is not a price to build a position on
MAX_SPREAD_FOR_RANK = 0.06
SCAN_CONTRACTS = 100.0          # fees and edge are normalised per contract on a 100-lot; the stake-sized walk happens in preflight


def series_of(ticker: str) -> str:
    return str(ticker).split("-", 1)[0]


#: Nicknames, so a team code can never be read as a YES/NO side ("NO" is New Orleans; "NO" is also a side).
NICK = {"ARI": "Cardinals", "ATL": "Falcons", "BAL": "Ravens", "BUF": "Bills", "CAR": "Panthers", "CHI": "Bears", "CIN": "Bengals", "CLE": "Browns",
        "DAL": "Cowboys", "DEN": "Broncos", "DET": "Lions", "GB": "Packers", "HOU": "Texans", "IND": "Colts", "JAX": "Jaguars", "KC": "Chiefs",
        "LA": "Rams", "LAC": "Chargers", "LV": "Raiders", "MIA": "Dolphins", "MIN": "Vikings", "NE": "Patriots", "NO": "Saints", "NYG": "Giants",
        "NYJ": "Jets", "PHI": "Eagles", "PIT": "Steelers", "SEA": "Seahawks", "SF": "49ers", "TB": "Buccaneers", "TEN": "Titans", "WAS": "Commanders"}


def nick(code):
    return NICK.get(code, code)


def _fmt(x: float) -> str:
    return f"{x:+g}" if x != 0 else "PK"


def bet_names(row: dict, home: str, away: str) -> dict:
    """Exact bet names and settlement meaning for BOTH sides of a row: {'YES': {...}, 'NO': {...}}."""
    fam, subj, thr, per = row.get("family"), row.get("subject"), row.get("threshold"), row.get("period")
    opp = away if subj == home else home if subj == away else None
    subj, opp = (nick(subj) if subj in NICK else subj), (nick(opp) if opp else opp)
    tag = "" if per in (None, "FULL") else f" [{per}]"
    yes_meaning = row.get("yes_meaning") or ""
    out = {"YES": {"name": None, "settles": f"YES pays if: {yes_meaning}"},
           "NO": {"name": None, "settles": f"NO pays if the YES condition is NOT met ({yes_meaning})"}}
    if fam == "GAME_WINNER" and subj:
        out["YES"]["name"] = f"{subj} moneyline{tag}"
        out["NO"]["name"] = f"{subj} to NOT win outright (opponent win or tie)" + tag
    elif fam == "SPREAD" and thr is not None and subj and opp:
        out["YES"]["name"] = f"{subj} {_fmt(-float(thr))}{tag}"
        out["NO"]["name"] = f"{opp} {_fmt(float(thr))}{tag}"
    elif fam in ("TOTAL",) and thr is not None:
        line = float(thr) - 0.5
        out["YES"]["name"] = f"Game total Over {line:g}{tag}"
        out["NO"]["name"] = f"Game total Under {line:g}{tag}"
    elif fam == "TEAM_TOTAL" and thr is not None and subj:
        line = float(thr) - 0.5
        out["YES"]["name"] = f"{subj} team total Over {line:g}{tag}"
        out["NO"]["name"] = f"{subj} team total Under {line:g}{tag}"
    elif fam == "PLAYER_STAT" and thr is not None and subj:
        line = float(thr) - 0.5
        stat = str(row.get("stat", "")).replace("_", " ")
        out["YES"]["name"] = f"{subj} {stat} Over {line:g}"
        out["NO"]["name"] = f"{subj} {stat} Under {line:g}"
    else:
        out["YES"]["name"] = f"{yes_meaning or row.get('ticker')} (YES)"
        out["NO"]["name"] = f"{yes_meaning or row.get('ticker')} (NO)"
    return out


def side_prices(row: dict, side: str) -> dict:
    ask = row.get("yes_ask") if side == "YES" else row.get("no_ask")
    bid = row.get("yes_bid") if side == "YES" else row.get("no_bid")
    return {"ask": None if ask is None else float(ask), "bid": None if bid is None else float(bid)}


def executable_book(row: dict, side: str, max_width: float = MAX_WIDTH) -> tuple:
    """(ok, reason). An executable pregame book: both sides quoted, ask below 1, not an untraded 0.00/0.99 book, width bounded."""
    if not row.get("executable"):
        return False, "NOT_EXECUTABLE (row is not an executable pregame book)"
    if row.get("no_real_market"):
        return False, "NO_REAL_MARKET (untraded placeholder book)"
    p = side_prices(row, side)
    if p["ask"] is None or p["ask"] <= 0 or p["ask"] >= 1:
        return False, f"NO_{side}_ASK"
    w = row.get("width")
    if w is not None and float(w) > max_width:
        return False, f"BOOK_TOO_WIDE ({float(w) * 100:.0f}c > {max_width * 100:.0f}c)"
    return True, None


def net_edge(fair_p: float, ask: float, schedule, ticker: str, as_of=None) -> dict:
    """Per-contract net edge: fair probability minus price minus the entry fee, via the versioned fee schedule. Never zero-fee by default."""
    ev = F.net_executable_ev(fair_p, ask, SCAN_CONTRACTS, schedule, series_of(ticker), as_of=as_of)
    if not ev.is_known:
        return {"net_edge": None, "fee_per_contract": None, "fee_state": ev.state, "reason": ev.reason}
    return {"net_edge": round(ev.net_ev_dollars / SCAN_CONTRACTS, 5), "fee_per_contract": round(ev.estimated_fees / SCAN_CONTRACTS, 5),
            "fee_state": ev.state, "reason": None}


def ceiling_cents(fair_low: float, schedule, ticker: str, as_of=None, min_net: float = MIN_NET_EDGE):
    """The highest ask, in whole cents, at which the CONSERVATIVE fair value still clears `min_net` after fees. None if no price does."""
    for c in range(99, 0, -1):
        e = net_edge(fair_low, c / 100.0, schedule, ticker, as_of)
        if e["net_edge"] is not None and e["net_edge"] >= min_net:
            return c
    return None


def _side_range(fair_yes: tuple, side: str) -> tuple:
    lo, hi = fair_yes
    return (lo, hi) if side == "YES" else (round(1 - hi, 4), round(1 - lo, 4))


def evaluate_contract(row: dict, side: str, fair_yes: dict, schedule, as_of, home: str, away: str, *,
                      gsim: FV.GameSim | None = None, shift: dict | None = None, noise: dict | None = None,
                      depth_hint: float | None = None, stake_dollars: float = 75.0) -> dict:
    """Everything the comparison needs about ONE contract-side. `fair_yes` = {"low","high","basis","state"} for the YES event."""
    tk = row["ticker"]
    names = bet_names(row, home, away)[side]
    ok, why = executable_book(row, side)
    prices = side_prices(row, side)
    out = {"ticker": tk, "side": side, "name": names["name"], "settles": names["settles"], "family": row.get("family"),
           "period": row.get("period"), "yes_meaning": row.get("yes_meaning"), "ask": prices["ask"], "ask_cents": None if prices["ask"] is None else round(prices["ask"] * 100),
           "bid": prices["bid"], "width": row.get("width"), "executable": ok, "reject": None if ok else why,
           "volume": row.get("volume"), "minutes_since_price_change": row.get("minutes_since_price_change"),
           "fair_basis": fair_yes.get("basis") if fair_yes else None, "fair_state": (fair_yes or {}).get("state", "NONE")}
    if not fair_yes or fair_yes.get("state") not in ("DERIVED", "DECLARED"):
        out.update(status="NO_DEFENSIBLE_FAIR_ESTIMATE", rankable=False,
                   reject=out["reject"] or (fair_yes or {}).get("reason") or "no derivable or declared fair range")
        return out
    lo, hi = _side_range((fair_yes["p_low"], fair_yes["p_high"]), side)
    out.update(fair_low=lo, fair_high=hi, fair_mid=round((lo + hi) / 2, 4))
    if prices["ask"] is not None:
        e_low = net_edge(lo, prices["ask"], schedule, tk, as_of)
        e_mid = net_edge(out["fair_mid"], prices["ask"], schedule, tk, as_of)
        out.update(net_edge_low=e_low["net_edge"], net_edge_mid=e_mid["net_edge"], fee_per_contract=e_low["fee_per_contract"],
                   fee_state=e_low["fee_state"], breakeven_price=None if e_low["fee_per_contract"] is None else round(prices["ask"] + e_low["fee_per_contract"], 4),
                   ceiling_cents=ceiling_cents(lo, schedule, tk, as_of))
        out["roi_low"] = None if e_low["net_edge"] is None else round(e_low["net_edge"] / (prices["ask"] + (e_low["fee_per_contract"] or 0)), 4)
        pm = out["fair_mid"]
        out["edge_per_sd"] = None if e_low["net_edge"] is None else round(e_low["net_edge"] / math.sqrt(max(pm * (1 - pm), 1e-4)), 4)
    else:
        out.update(net_edge_low=None, ceiling_cents=None, roi_low=None)

    # script behaviour: derived contracts use the same draws as the fair value; declared ones carry the analyst's table
    out["scripts"] = {"basis": "NONE", "matrix": [], "winning_scripts": 0, "single_script_dependent": None, "script_neutral": False}
    if gsim is not None and shift is not None and fair_yes.get("state") == "DERIVED":
        dm = sum(shift["home_margin"]) / 2.0
        dt = sum(shift["total"]) / 2.0
        sim = gsim.draw(dm, dt)
        ev, _ = FV.contract_event(row, sim, home, away)
        if ev is not None:
            ev = ev if side == "YES" else ~ev
            mat = FV.script_matrix(ev, sim, home, away, gsim.m0 + dm, gsim.t0 + dt)
            be = out.get("breakeven_price") or (prices["ask"] or 1.0)
            major = [c for c in mat if c["p_script"] >= 0.03 and c["p_win_given_script"] is not None]
            winning = [c for c in major if c["p_win_given_script"] >= be]
            contrib = [c["p_script"] * c["p_win_given_script"] for c in major]
            tot = sum(contrib) or 1.0
            out["scripts"] = {"basis": "MARKET_CENTRED_SIM_AT_THESIS_CENTRE (same draws as the fair value)", "matrix": mat,
                              "winning_scripts": len(winning), "major_scripts": len(major),
                              "max_script_share_of_wins": round(max(contrib) / tot, 3) if contrib else None,
                              "single_script_dependent": bool(contrib) and (max(contrib) / tot) > 0.40,
                              "script_neutral": False}
    return out


def scan_derivable(rows: list, gsim: FV.GameSim, shift: dict, noise: dict, schedule, as_of, home: str, away: str) -> list:
    """Evaluate EVERY derivable full-game contract, BOTH sides, under the thesis shift range. The raw material for the comparison."""
    out = []
    for r in rows:
        if r.get("family") not in FV.DERIVABLE or r.get("period") != "FULL":
            continue
        fr = FV.fair_range(r, gsim, tuple(shift["home_margin"]), tuple(shift["total"]), noise)
        if fr["state"] != "DERIVED":
            continue
        for side in ("YES", "NO"):
            out.append(evaluate_contract(r, side, fr, schedule, as_of, home, away, gsim=gsim, shift=shift, noise=noise))
    return out


SINGLE_SCRIPT_PENALTY = 0.7


def risk_reward(e: dict):
    """Conservative net edge per standard deviation of one contract's payoff, discounted when the win depends on a single script.

    Ranking by ROI alone crowns the longest shot (a 16c alternate spread shows a bigger ROI than a 45c one on the same thesis while
    winning in fewer worlds); edge per unit of payoff risk is the like-for-like comparison. The raw ROI stays on the row."""
    v = e.get("edge_per_sd")
    if v is None:
        return None
    return v * (SINGLE_SCRIPT_PENALTY if (e.get("scripts") or {}).get("single_script_dependent") else 1.0)


def scan_ladders(rows: list, ladder_shifts: list, schedule, as_of, home: str, away: str) -> list:
    """Evaluate every rung, BOTH sides, of each ladder the analyst gave a shift for (player statistics, period markets, alternate lines).

    The shift is the analyst's; the centre is the market's own ladder (`ladder_fair.py`). A rung that cannot be derived is simply absent here (it is
    reported by the caller as such); nothing is invented for it."""
    ladders = LF.build_ladders(rows)
    out = []
    for i, ls in enumerate(ladder_shifts or []):
        sel, shift = ls["selector"], tuple(float(x) for x in ls["shift"])
        sc = LF.script_summary(ls.get("script_results"))
        matched = LF.select(rows, sel)
        for r in matched:
            lad = ladders.get(LF.ladder_key(r))
            fr = LF.fair_range_for_row(r, lad, shift) if lad else {"state": "NOT_DERIVABLE", "reason": "no ladder"}
            if fr["state"] != "DERIVED":
                continue
            fr = dict(fr, basis=f"{fr['basis']}: {ls.get('basis', '')}".strip(": "))
            for side in ("YES", "NO"):
                e = evaluate_contract(r, side, fr, schedule, as_of, home, away)
                e["scripts"] = dict(sc)
                e["ladder_thesis"] = {"index": i, "selector": sel, "shift": list(shift), "rungs": fr["ladder_rungs"], "spacing": fr["ladder_spacing"]}
                if ls.get("usage"):
                    e["usage"] = ls["usage"]
                out.append(e)
    return out


def best_by_family(ranked: list) -> list:
    """The best executable, fee-clearing expression in EACH contract family, in rank order: the like-for-like comparison of how one thesis can be expressed."""
    seen, out = set(), []
    for e in ranked:
        if not (e.get("executable") and (e.get("net_edge_low") or -1) >= MIN_NET_EDGE):
            continue
        k = (e.get("family"), e.get("period") or "FULL")
        if k in seen:
            continue
        seen.add(k)
        out.append(e)
    return out


def rank(evals: list) -> list:
    """Executable, fee-clearing candidates first by risk/reward; everything else after, each with its reason code."""
    def key(e):
        clears = e.get("rankable", True) and e.get("executable") and (e.get("net_edge_low") or -1) >= MIN_NET_EDGE
        rr = risk_reward(e)
        return (0 if clears else 1, -(rr if rr is not None else -9), e.get("width") or 1.0)
    return sorted(evals, key=key)


def reason_rejected(e: dict, best: dict | None) -> str:
    if e.get("status") == "NO_DEFENSIBLE_FAIR_ESTIMATE":
        return "no defensible fair-value estimate (not derivable and none declared)"
    if not e.get("executable"):
        return e.get("reject") or "not executable"
    if e.get("net_edge_low") is None:
        return f"fee state {e.get('fee_state')}: net edge unknown"
    if e["net_edge_low"] < MIN_NET_EDGE:
        return (f"net edge at the conservative end is {e['net_edge_low'] * 100:+.1f}c per contract after fees "
                f"(needs >= {MIN_NET_EDGE * 100:.1f}c); ceiling would be {e.get('ceiling_cents')}c vs ask {e['ask_cents']}c")
    if best is not None and e is not best:
        return (f"clears the edge floor but ranks below {best['name']} on conservative edge per unit of payoff risk "
                f"({risk_reward(e) or 0:.3f} vs {risk_reward(best) or 0:.3f}; ROI {(e.get('roi_low') or 0) * 100:.1f}% vs "
                f"{(best.get('roi_low') or 0) * 100:.1f}%"
                + ("; wins mainly in a single script" if (e.get('scripts') or {}).get('single_script_dependent') else "") + ")")
    return "selected"
