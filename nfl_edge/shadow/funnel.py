"""The rejection funnel: where every listed market leaves the existing decision pipeline, and why.

The question this answers is the owner's: "did we get one recommendation because only one contract was truly
good enough, or because most markets failed mapping or model coverage?" It is an ACCOUNTING of the gates that
already exist, replayed mechanically over one shadow snapshot. It introduces no threshold, lowers no gate,
selects nothing, and carries no authority: a contract this module labels BET has cleared the mechanical gates
the pre-trade preflight would apply to a handicap that happened to equal the model's own contract value. It is
still not a recommendation -- that requires a human handicap and the signed preflight -- and nothing here can
reach Airtable, the preflight worker or the recommendation ledger (`tests/test_run_nfl_isolation.py`).

Stages, in the order the existing system applies them:

    discovered           every ticker in the capture snapshot the ledger priced from
    mapped               joined to a scheduled game (game_id)
    supported            the pricer priced it (support_state SUPPORTED); everything else names its refusal
    priced               a contract value exists
    raw_disagreement     model value beats the EXECUTABLE ask on one side (YES ask, or NO ask), not the mid
    tradable_book        the packet's own tradability rule: width <= MAX_DISAGREEMENT_WIDTH and a real market
    data_quality         no quality flag; player markets: availability not blocking / UNKNOWN / stale, and not
                         unresolved inside the T-90m window (the schema's own RECOMMENDED rules)
    executable_price     the ask is at or below the WATCH ceiling -- the highest price at which one contract
                         still has net executable EV > 0 after the committed fee schedule, computed with the
                         same `net_executable_ev` the preflight gate uses. Above it: WATCH, ceiling recorded
    liquidity            observed depth on the side (books are captured only inside 72h of kickoff; outside
                         that window the gate is UNAVAILABLE and the existing system fails closed -> PASS)
    -> BET | WATCH | PASS

Not replayed, and said so: the risk policy needs a stake and a bankroll snapshot, and the decision-time
freshness gate needs a decision timestamp; both are NOT_APPLICABLE to a snapshot accounting.
"""
from __future__ import annotations

from collections import Counter

from nfl_edge.execution import fees as F
from nfl_edge.handicap import schema as S
from nfl_edge.handicap.packet import MAX_DISAGREEMENT_WIDTH, NO_REAL_MARKET_WIDTH
from nfl_edge.settlement.availability import BLOCKING_STATES, UNKNOWN

FUNNEL_VERSION = "funnel-1.0.0"
BET, WATCH, PASS = "BET", "WATCH", "PASS"
STAGES = ("discovered", "mapped", "supported", "priced", "raw_disagreement", "tradable_book", "data_quality",
          "executable_price", "liquidity")
AUTHORITY = "NONE: an accounting of existing gates over the model's own number; not a recommendation"


def watch_ceiling(fair: float, schedule, series: str | None, as_of, contracts: float = 1.0, step: float = 0.01):
    """Highest executable price (cent grid) at which `contracts` bought at that price keep net EV > 0.

    Uses the preflight's own `net_executable_ev`, as of the SNAPSHOT time (the fee schedule is versioned by
    effective window, exactly as the gate requires). Returns (ceiling, fee_state, reason); ceiling None when
    the fee is not KNOWN (the gate blocks on an unknown cost, and so does this)."""
    if fair is None or fair <= 0:
        return None, "NO_FAIR", "no fair probability"
    price = round(int(fair / step) * step, 2)
    best, state, reason = None, None, None
    while price >= step:
        nev = F.net_executable_ev(float(fair), float(price), contracts, schedule, series_ticker=series, as_of=as_of)
        state, reason = nev.fee_state, nev.reason
        if not nev.is_known:
            return None, state, reason
        if nev.net_ev_dollars is not None and nev.net_ev_dollars > 0:
            best = price
            break
        price = round(price - step, 2)
    return best, state, reason


def _side_view(row: dict):
    """Which side the model favours against the EXECUTABLE price, and the raw disagreement on that side."""
    cv = row.get("model_contract_value")
    ya, na = row.get("yes_ask"), row.get("no_ask")
    if cv is None:
        return None, None, None, None
    cand = []
    if ya is not None:
        cand.append(("YES", cv - ya, ya, cv))
    if na is not None:
        cand.append(("NO", (1.0 - cv) - na, na, 1.0 - cv))
    if not cand:
        return None, None, None, None
    side, dis, ask, fair = max(cand, key=lambda c: c[1])
    return side, dis, ask, fair


def classify(row: dict, book: dict | None, schedule, as_of) -> dict:
    """One contract's exit point. `row` is a ledger observation; `book` its book summary (or None)."""
    out = {"ticker": row.get("ticker"), "family": row.get("family"), "game_id": row.get("game_id"),
           "support_state": row.get("support_state"), "stage_reached": "discovered", "state": PASS,
           "reasons": [], "side": None, "executable_ask": None, "fair": None, "raw_disagreement": None,
           "watch_ceiling": None, "fee_state": None}
    if not row.get("game_id"):
        out["reasons"].append("unmapped: market did not join a scheduled game")
        return out
    out["stage_reached"] = "mapped"
    if row.get("support_state") != "SUPPORTED":
        out["reasons"].append(f"{row.get('support_state')}: {row.get('support_reason')}")
        return out
    out["stage_reached"] = "supported"
    if row.get("model_contract_value") is None:
        out["reasons"].append("no contract value on a supported row")
        return out
    out["stage_reached"] = "priced"
    side, dis, ask, fair = _side_view(row)
    out.update({"side": side, "executable_ask": ask, "fair": fair, "raw_disagreement": dis})
    if side is None or dis is None or dis <= 0:
        out["reasons"].append("no positive disagreement against either executable ask")
        return out
    out["stage_reached"] = "raw_disagreement"
    w, vol, oi = row.get("quote_width"), row.get("volume") or 0.0, row.get("open_interest") or 0.0
    no_real = w is not None and (w >= NO_REAL_MARKET_WIDTH or (w >= 0.10 and vol <= 0.0 and oi <= 0.0))
    if w is None or w > MAX_DISAGREEMENT_WIDTH or no_real:
        out["reasons"].append(f"book not tradable for ranking: width {w}, volume {vol:.0f}, open interest {oi:.0f}")
        return out
    out["stage_reached"] = "tradable_book"
    if row.get("quality_flags"):
        out["reasons"].append(f"quality flags {row['quality_flags']}")
    if row.get("family") in S.PLAYER_MARKET_FAMILIES:
        av, stale, mtk = row.get("availability_state"), row.get("availability_stale_minutes"), row.get("minutes_to_kickoff")
        if av is None or av == UNKNOWN:
            out["reasons"].append("availability unknown")
        elif side == "YES" and av in BLOCKING_STATES:
            out["reasons"].append(f"availability {av} blocks a YES prop")
        elif av in ("QUESTIONABLE", "DOUBTFUL") and mtk is not None and mtk <= S.UNRESOLVED_STATUS_GATE_MIN:
            out["reasons"].append(f"availability {av} unresolved inside T-{S.UNRESOLVED_STATUS_GATE_MIN:.0f}m")
        if stale is not None and stale > S.MAX_AVAILABILITY_STALE_MIN:
            out["reasons"].append(f"availability {stale:.0f} min stale")
    if out["reasons"]:
        return out
    out["stage_reached"] = "data_quality"
    series = str(row.get("ticker") or "").split("-")[0] or None
    ceiling, fee_state, fee_reason = watch_ceiling(fair, schedule, series, as_of)
    out["fee_state"], out["watch_ceiling"] = fee_state, ceiling
    if ceiling is None:
        out["reasons"].append(f"fee schedule not KNOWN for {series}: {fee_reason}")
        return out
    if ask > ceiling + 1e-9:
        out["state"] = WATCH
        out["reasons"].append(f"ask {ask:.2f} above the zero-net-EV ceiling {ceiling:.2f}")
        return out
    out["stage_reached"] = "executable_price"
    depth = None if book is None else book.get("book_depth_yes" if side == "YES" else "book_depth_no")
    if depth is None:
        out["reasons"].append("no order book observed for this ticker (books are captured inside 72h of kickoff)")
        return out
    if depth <= 0:
        out["reasons"].append(f"no {side} depth in the observed book")
        return out
    out["stage_reached"] = "liquidity"
    out["state"] = BET
    return out


def build_funnel(rows: list, books: dict | None, schedule, *, as_of, run_id: str | None = None) -> dict:
    """The whole funnel for one snapshot: stage counts, terminal states, reasons, and the BET/WATCH rows."""
    books = books or {}
    stage_counts = Counter()
    states, reasons, by_family = Counter(), Counter(), {}
    watch_rows, bet_rows = [], []
    for r in rows:
        c = classify(r, books.get(r.get("ticker")), schedule, as_of)
        reached = STAGES.index(c["stage_reached"])
        for st in STAGES[: reached + 1]:
            stage_counts[st] += 1
        states[c["state"]] += 1
        fam = str(r.get("family"))
        by_family.setdefault(fam, Counter())[c["state"]] += 1
        for why in c["reasons"]:
            reasons[why.split(":")[0][:60]] += 1
        if c["state"] == WATCH:
            watch_rows.append(c)
        elif c["state"] == BET:
            bet_rows.append(c)
    n = len(rows)
    return {"funnel_version": FUNNEL_VERSION, "run_id": run_id, "as_of": getattr(as_of, "isoformat", lambda: as_of)(), "authority": AUTHORITY,
            "n_markets": n, "stages": [{"stage": st, "n": stage_counts[st]} for st in STAGES],
            "terminal_states": dict(states), "by_family": {k: dict(v) for k, v in sorted(by_family.items())},
            "top_rejection_reasons": [{"reason": k, "n": v} for k, v in reasons.most_common(25)],
            "not_replayed": ["portfolio_risk_policy (needs a stake and bankroll)",
                             "decision_time_quote_freshness (needs a decision timestamp; the snapshot's own "
                             "confirmation is the STALE_DATA support state)"],
            "watch": sorted(watch_rows, key=lambda c: (-(c["raw_disagreement"] or 0), c["ticker"]))[:200],
            "bet": sorted(bet_rows, key=lambda c: (-(c["raw_disagreement"] or 0), c["ticker"]))[:200]}
