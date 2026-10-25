"""Independent challenge: nothing reaches the card until it has survived these ten questions, and PASS is a real outcome.

Each item is answered one of CLEAR / FLAG / OPEN / FAIL / NOT_APPLICABLE:

  CLEAR   answered, and any automatic check agrees
  FLAG    answered and allowed through, but the reader should see the caveat (it is printed on the card line)
  OPEN    the analyst has not answered, or the evidence the answer rests on is missing -> NOT cleared
  FAIL    an automatic check contradicts the thesis -> NOT cleared
  NOT_APPLICABLE  the question does not bear on this kind of contract

A candidate is `cleared` only when no item is OPEN or FAIL. The automatic checks are deliberately blunt: they exist so that a missing
answer or an unfavourable fact stops the line, not so that a good answer gets argued down.

Questions 2, 3, 4 and 5 need the analyst's words and are checked only for presence and for the facts they must be consistent with; the
others are computed from the packet, the expression engine and the ledger.
"""
from __future__ import annotations

CHALLENGE_VERSION = "challenge-1.0.0"

QUESTIONS = (
    ("C1", "What would make this thesis fail?"),
    ("C2", "Has the market already incorporated the advantage?"),
    ("C3", "Is our reading of the matchup wrong?"),
    ("C4", "Are the underlying matchup statistics opponent-adjusted?"),
    ("C5", "Is the projected player usage realistic?"),
    ("C6", "Does it depend on one unusually specific game script?"),
    ("C7", "Does the price compensate for the uncertainty?"),
    ("C8", "Is another contract a superior expression of this thesis?"),
    ("C9", "Are the quote and the book current?"),
    ("C10", "Does it duplicate exposure already on the book?"),
)

MAX_QUOTE_AGE_MIN = 15.0
SUPERIOR_RATIO = 1.15
PRICE_MOVE_FLAG = 0.03
PRICE_MOVE_OPEN = 0.06
SINGLE_SCRIPT_FAIL_SHARE = 0.70
BAD_AVAILABILITY = ("OUT", "DOUBTFUL", "IR", "PUP", "SUSPENDED", "INACTIVE")
UNRESOLVED_AVAILABILITY = ("QUESTIONABLE", "UNKNOWN", None)


def _present(x, n: int = 1) -> bool:
    if isinstance(x, (list, tuple)):
        return len([i for i in x if str(i).strip()]) >= n
    return bool(str(x or "").strip())


def _item(i, status, finding, auto=True):
    return {"id": i, "question": dict(QUESTIONS)[i], "status": status, "finding": finding, "auto": auto}


def challenge(thesis: dict, cand: dict, ev: dict, ranked_alternatives: list, *, packet_market: dict | None, player_injury: dict | None,
              quote_age_min: float | None, mode: str, owner_open_units: float, game_cap_units: float = 8.0) -> dict:
    """`thesis` is the analyst's thesis record; `cand` the analyst's candidate entry; `ev` the engine's evaluation of it;
    `ranked_alternatives` the engine's ranked evaluations of the OTHER contracts for the same thesis."""
    ch = thesis.get("challenge") or {}
    items = []

    # C1
    fm = ch.get("fail_modes")
    items.append(_item("C1", "CLEAR" if _present(fm, 2) else "OPEN",
                       "; ".join(fm[:3]) if _present(fm, 2) else "fewer than two concrete failure modes were written down", auto=False))

    # C2: answer required; the price history must be consistent with it
    moved = None
    if packet_market:
        mv = (packet_market.get("movement") or {})
        tot = mv.get("total_move_since_first_capture")
        if tot is not None:
            moved = float(tot) if ev["side"] == "YES" else -float(tot)
    ans = ch.get("market_already_priced")
    if not _present(ans):
        items.append(_item("C2", "OPEN", "no statement of why the market has not already priced this", auto=False))
    elif moved is not None and moved >= PRICE_MOVE_OPEN:
        items.append(_item("C2", "OPEN", f"the price has already moved {moved * 100:+.0f}c toward this side since the first capture; the answer must explain the remaining edge", auto=True))
    elif moved is not None and moved >= PRICE_MOVE_FLAG:
        items.append(_item("C2", "FLAG", f"price already moved {moved * 100:+.0f}c toward this side since first capture. {ans}", auto=True))
    else:
        items.append(_item("C2", "CLEAR", ans + ("" if moved is None else f" (price move toward this side since first capture: {moved * 100:+.0f}c)"), auto=False))

    # C3 / C4
    measured = (thesis.get("evidence") or {}).get("measured") or []
    mc = ch.get("matchup_check")
    items.append(_item("C3", "CLEAR" if (_present(mc) and measured) else "OPEN",
                       mc if (_present(mc) and measured) else "no matchup self-check, or no MEASURED evidence cited", auto=False))
    unadj = [m for m in measured if m.get("opponent_adjusted") is False]
    if not measured:
        items.append(_item("C4", "OPEN", "no measured evidence cited, so nothing can be shown to be opponent-adjusted"))
    elif unadj:
        items.append(_item("C4", "FAIL", "raw (unadjusted) statistics cited as evidence: " + "; ".join(str(m.get("claim", ""))[:70] for m in unadj)))
    elif all(m.get("opponent_adjusted") is True for m in measured):
        items.append(_item("C4", "CLEAR", f"{len(measured)} measured item(s), all opponent-adjusted"))
    else:
        items.append(_item("C4", "OPEN", "measured evidence does not state whether it is opponent-adjusted"))

    # C5
    if ev.get("family") == "PLAYER_STAT":
        u = cand.get("usage") or thesis.get("usage") or {}
        need = ("projected_opportunity", "recent_usage", "role_stability", "teammate_context")
        miss = [k for k in need if not _present(u.get(k))]
        st = (player_injury or {}).get("status")
        if st is not None and str(st).upper() in BAD_AVAILABILITY:
            items.append(_item("C5", "FAIL", f"player availability is {st}"))
        elif st is None or str(st).upper() in ("QUESTIONABLE", "UNKNOWN"):
            items.append(_item("C5", "OPEN", f"player availability is {st or 'unresolved'}: the inactive list (about 90 minutes before kickoff) resolves it and the option value of waiting is not spent"))
        elif miss:
            items.append(_item("C5", "OPEN", "usage record incomplete: missing " + ", ".join(miss), auto=False))
        else:
            items.append(_item("C5", "CLEAR", f"availability {st}; usage record complete (opportunity, recent usage, role stability, teammate context)", auto=False))
    else:
        items.append(_item("C5", "NOT_APPLICABLE", "not a player-usage contract"))

    # C6
    sc = ev.get("scripts") or {}
    share = sc.get("max_script_share_of_wins")
    if sc.get("script_neutral"):
        items.append(_item("C6", "CLEAR", "script-neutral by construction"))
    elif not sc.get("matrix") and not sc.get("declared"):
        items.append(_item("C6", "OPEN", "no script analysis for this contract"))
    elif sc.get("single_script_dependent") and share is not None and share >= SINGLE_SCRIPT_FAIL_SHARE:
        items.append(_item("C6", "FAIL", f"{share:.0%} of this contract's winning mass sits in a single script"))
    elif sc.get("single_script_dependent"):
        items.append(_item("C6", "FLAG", f"leans on one script ({share:.0%} of winning mass); wins in {sc.get('winning_scripts')} of {sc.get('major_scripts')} major scripts; 2U and above are unavailable"))
    else:
        items.append(_item("C6", "CLEAR", f"wins (is +EV) in {sc.get('winning_scripts')} of {sc.get('major_scripts', '?')} major scripts; largest share of winning mass {share if share is None else format(share, '.0%')}"))

    # C7
    ne = ev.get("net_edge_low")
    if ne is None:
        items.append(_item("C7", "FAIL", "net edge unknown (no defensible fair range or fees not established)"))
    elif ne >= 0.02:
        items.append(_item("C7", "CLEAR", f"net edge at the conservative end of the range {ne * 100:+.1f}c per contract after fees; ceiling {ev.get('ceiling_cents')}c vs ask {ev.get('ask_cents')}c"))
    else:
        items.append(_item("C7", "FAIL", f"net edge at the conservative end {ne * 100:+.1f}c per contract is under the 2.0c floor"))

    # C8
    my = ev.get("edge_per_sd")
    best = next((a for a in ranked_alternatives if a is not ev and (a.get("net_edge_low") or -1) >= 0.02 and a.get("executable")), None)
    if my is None:
        items.append(_item("C8", "OPEN", "cannot compare: no risk/reward figure"))
    elif best is not None and best.get("edge_per_sd") and best["edge_per_sd"] > my * SUPERIOR_RATIO:
        items.append(_item("C8", "FAIL", f"superior expression of the same thesis: {best['name']} ({best['side']}) at {best['ask_cents']}c, "
                                         f"edge per unit of payoff risk {best['edge_per_sd']:.3f} vs {my:.3f}"))
    else:
        items.append(_item("C8", "CLEAR", "no other contract for this thesis offers materially better conservative risk/reward"
                           + ("" if best is None else f" (closest: {best['name']} {best['side']} at {best['ask_cents']}c)")))

    # C9
    if quote_age_min is None:
        items.append(_item("C9", "FAIL", "quote age unknown"))
    elif quote_age_min > MAX_QUOTE_AGE_MIN:
        if mode == "REHEARSAL":
            items.append(_item("C9", "FLAG", f"REHEARSAL: quote is {quote_age_min:.0f} min old (> {MAX_QUOTE_AGE_MIN:.0f}); a live run would be BLOCKED here"))
        else:
            items.append(_item("C9", "FAIL", f"quote is {quote_age_min:.0f} minutes old (limit {MAX_QUOTE_AGE_MIN:.0f})"))
    elif not ev.get("executable"):
        items.append(_item("C9", "FAIL", ev.get("reject") or "book not executable"))
    else:
        items.append(_item("C9", "CLEAR", f"capture {quote_age_min:.0f} min old; book two-sided, width {float(ev.get('width') or 0) * 100:.0f}c. The depth walk for the staked size is done by preflight"))

    # C10
    if owner_open_units >= game_cap_units:
        items.append(_item("C10", "FAIL", f"{owner_open_units:.1f}U already open on this game (game cap {game_cap_units:g}U)"))
    elif owner_open_units > 0:
        items.append(_item("C10", "FLAG", f"{owner_open_units:.1f}U already open on this game; the stake below is the room left under the game cap, counted together"))
    else:
        items.append(_item("C10", "CLEAR", "no open owner position on this game in the ledger"))

    bad = [i for i in items if i["status"] in ("OPEN", "FAIL")]
    return {"version": CHALLENGE_VERSION, "cleared": not bad, "items": items,
            "open": [i["id"] for i in items if i["status"] == "OPEN"], "failed": [i["id"] for i in items if i["status"] == "FAIL"],
            "flags": [i["id"] for i in items if i["status"] == "FLAG"]}
