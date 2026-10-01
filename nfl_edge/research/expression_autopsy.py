"""EXPRESSION AUTOPSY: was the THESIS wrong, or the MARKET chosen to express it, or the PRICE paid, or the SIZE?
RESEARCH ONLY; reads the owner's position episodes, never writes them.

The unit is the POSITION EPISODE (`handicap/position_lifecycle.py`): an order is a transaction, a cashout is the
same position closing, never a second wager.

THESIS (inferred, never claimed). Imported wagers carry no thesis (episodes say UNKNOWN_THESIS). Each episode is
placed in a deterministic THESIS BUCKET -- game x beneficiary x polarity -- by what the contract pays on:

    SPREAD / GAME_WINNER team X, YES     -> (X, +)  margin thesis
    TEAM_TOTAL team X, YES               -> (X, +)  offence thesis
    PLAYER_STAT of X's player, YES       -> (X, +)  offence / volume thesis (that player)
    TOTAL / BOTH_TEAMS_SCORE, YES        -> (GAME, +) scoring thesis
    the NO side of any of these          -> the same subject, polarity -

so PHI spread + Hurts attempts + three Hurts passing rungs are ONE bucket (PHI, +): one script, five positions.
Where the handicap record supplies a thesis (`thesis_metadata`), it is used instead and labelled OWNER.

SCRIPT IS JUDGED BY THE GAME, NOT BY THE WAGER. A bucket component is right when the HEADLINE rung (the
two-sided rung nearest 50c at latest pregame) of the subject's own ladder settled on the bucket's side: the team
beat the market's median margin / points, the player beat the market's median line. A wager on an alternate rung
can lose while the script was right (EXPRESSION_WRONG), or win while it was wrong (SCRIPT_WRONG, won anyway).
Nothing here reads the episode's P&L to decide the script.

Classifications: SCRIPT_RIGHT/EXPRESSION_RIGHT, SCRIPT_RIGHT/EXPRESSION_WRONG, SCRIPT_PARTIAL/EXPRESSION_RIGHT,
SCRIPT_PARTIAL/EXPRESSION_WRONG, SCRIPT_WRONG, SCRIPT_UNJUDGEABLE; flags PRICE_ERROR (paid 5c+ worse than the
close on the held side), ROLE_ERROR / VOLUME_ERROR / EFFICIENCY_ERROR / VARIANCE_ONLY (a lost player position, from
the player autopsy's miss layer), CORRELATED_STACK (3+ positions on one bucket).
"""
from __future__ import annotations

from collections import Counter, defaultdict

EXPRESSION_AUTOPSY_VERSION = "expression-autopsy-1.0.0"
PRICE_ERROR_CENTS = 0.05
STACK_MIN = 3

SCRIPT_RIGHT, SCRIPT_PARTIAL, SCRIPT_WRONG, SCRIPT_UNJUDGEABLE = "SCRIPT_RIGHT", "SCRIPT_PARTIAL", "SCRIPT_WRONG", "SCRIPT_UNJUDGEABLE"
LAYER_TO_ERROR = {"GAME_SCRIPT_DROVE_TEAM_VOLUME": "VOLUME_ERROR", "TEAM_VOLUME_NOT_EXPLAINED_BY_SCRIPT": "VOLUME_ERROR",
                  "PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION": "ROLE_ERROR", "ROLE_UNCERTAINTY": "ROLE_ERROR",
                  "AVAILABILITY": "ROLE_ERROR", "EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION": "EFFICIENCY_ERROR",
                  "VARIANCE_ONLY": "VARIANCE_ONLY", "NO_LARGE_MISS": "VARIANCE_ONLY"}


def _f(x):
    try:
        return None if x is None else float(x)
    except (TypeError, ValueError):
        return None


def thesis_component(row: dict, direction: str, player_team: dict) -> dict | None:
    """(bucket subject, polarity, thesis type, ladder id) of one contract held LONG_YES / LONG_NO."""
    sign = 1 if direction == "LONG_YES" else -1 if direction == "LONG_NO" else 0
    if not row or not sign:
        return None
    fam, period = row.get("family"), row.get("period") or "FULL"
    if fam in ("SPREAD", "GAME_WINNER") and row.get("team"):
        subj, kind = row["team"], "MARGIN"
    elif fam == "TEAM_TOTAL" and row.get("team"):
        subj, kind = row["team"], "OFFENSE"
    elif fam == "PLAYER_STAT":
        subj, kind = player_team.get(row.get("player_gsis_id")) or row.get("team") or "UNKNOWN_TEAM", f"PLAYER:{row.get('stat')}"
    elif fam in ("TOTAL", "BOTH_TEAMS_SCORE_N", "BOTH_TEAMS_SCORE"):
        subj, kind = "GAME", "SCORING"
    else:
        subj, kind = (row.get("team") or "GAME"), f"OTHER:{fam}"
    if period != "FULL":
        kind = f"{kind}:{period}"
    return {"bucket": f"{row.get('game_id')}|{subj}|{'+' if sign > 0 else '-'}", "subject": subj, "polarity": sign,
            "thesis_type": kind, "ladder_id": row.get("ladder_id")}


def headline_outcome(ladder_rows: list):
    """Settled YES (1/0) of the ladder's headline rung at latest pregame, or None."""
    main = [r for r in ladder_rows if r.get("is_main_rung") and r.get("settled_yes") is not None]
    if not main:
        return None
    return float(main[0]["settled_yes"])


def classify_bucket(components: list) -> str:
    rights = [c["right"] for c in components if c.get("right") is not None]
    if not rights:
        return SCRIPT_UNJUDGEABLE
    if all(rights):
        return SCRIPT_RIGHT
    if not any(rights):
        return SCRIPT_WRONG
    return SCRIPT_PARTIAL


def autopsy(episodes: list, *, board_latest: dict, board_by_ladder: dict, player_links: dict, player_team: dict,
            thesis_metadata: dict | None = None) -> dict:
    """`board_latest`: ticker -> latest-pregame board row; `board_by_ladder`: ladder_id -> its latest-pregame rows;
    `player_links`: (game_id, player_gsis_id, stat) -> script-autopsy player link; `thesis_metadata`:
    position_episode_id or ticker -> owner-supplied thesis fields (optional)."""
    thesis_metadata = thesis_metadata or {}
    recs = []
    for ep in episodes:
        t = ep.get("market_ticker")
        row = board_latest.get(t)
        comp = thesis_component(row, ep.get("direction"), player_team) if row else None
        meta = thesis_metadata.get(ep.get("position_episode_id")) or thesis_metadata.get(t) or {}
        rec = {"position_episode_id": ep.get("position_episode_id"), "market_ticker": t, "week": ep.get("week"),
               "direction": ep.get("direction"), "entry_cost": _f(ep.get("entry_cost")), "opened_quantity": _f(ep.get("opened_quantity")),
               "total_episode_pnl": _f(ep.get("total_episode_pnl")), "closed_by": ep.get("closed_by"),
               "settlement_state": ep.get("settlement_state"), "opening_phase": ep.get("opening_phase"),
               "game_id": (row or {}).get("game_id"), "family": (row or {}).get("family"), "stat": (row or {}).get("stat"),
               "player_name": (row or {}).get("player_name"), "threshold": (row or {}).get("rung_value"),
               "thesis_source": "OWNER" if meta.get("primary_thesis_id") else "INFERRED",
               "thesis_bucket": meta.get("primary_thesis_id") or (comp or {}).get("bucket"),
               "thesis_type": (comp or {}).get("thesis_type"), "flags": []}
        if comp and comp.get("ladder_id"):
            ho = headline_outcome(board_by_ladder.get(comp["ladder_id"]) or [])
            rec["headline_rung_settled_yes"] = ho
            rec["component_right"] = None if ho is None else ((ho == 1.0) == (comp["polarity"] > 0))
        else:
            rec["component_right"] = None
        # price paid vs the canonical close on the held side (pregame entries only)
        qty, cost = rec["opened_quantity"], rec["entry_cost"]
        cm = _f((row or {}).get("close_mid"))
        if qty and cost and cm is not None and ep.get("opening_phase") in ("PRE_GAME", "UNKNOWN"):
            paid = cost / qty
            held_close = cm if ep.get("direction") == "LONG_YES" else 1.0 - cm
            rec["paid_per_contract"], rec["held_side_close_mid"] = round(paid, 4), round(held_close, 4)
            rec["paid_minus_close"] = round(paid - held_close, 4)
            if paid - held_close >= PRICE_ERROR_CENTS:
                rec["flags"].append("PRICE_ERROR")
        recs.append(rec)
    # bucket-level script judgment, from the components' headline rungs (never the P&L)
    buckets = defaultdict(list)
    for r in recs:
        if r.get("thesis_bucket"):
            buckets[r["thesis_bucket"]].append(r)
    bsum = {}
    for b, rs in buckets.items():
        comps = {}
        for r in rs:
            key = (r.get("thesis_type"), r.get("player_name"))
            if r.get("component_right") is not None:
                comps[key] = {"right": r["component_right"]}
        verdict = classify_bucket(list(comps.values()))
        stake = sum(r["entry_cost"] or 0 for r in rs)
        pnl = sum(r["total_episode_pnl"] or 0 for r in rs if r["total_episode_pnl"] is not None)
        bsum[b] = {"bucket": b, "positions": len(rs), "script": verdict, "stake": round(stake, 2), "pnl": round(pnl, 2),
                   "thesis_types": sorted({r.get("thesis_type") or "?" for r in rs}), "week": rs[0].get("week"),
                   "correlated_stack": len(rs) >= STACK_MIN}
        for r in rs:
            r["bucket_script"] = verdict
            if len(rs) >= STACK_MIN:
                r["flags"].append("CORRELATED_STACK")
    for r in recs:
        won = (r["total_episode_pnl"] or 0) > 0
        s = r.get("bucket_script") or SCRIPT_UNJUDGEABLE
        if s == SCRIPT_WRONG:
            r["classification"] = SCRIPT_WRONG
            if won:
                r["flags"].append("WON_DESPITE_WRONG_SCRIPT")
        elif s in (SCRIPT_RIGHT, SCRIPT_PARTIAL):
            r["classification"] = f"{s}/{'EXPRESSION_RIGHT' if won else 'EXPRESSION_WRONG'}"
        else:
            r["classification"] = SCRIPT_UNJUDGEABLE
        if not won and r.get("family") == "PLAYER_STAT":
            link = player_links.get((r.get("game_id"), (board_latest.get(r["market_ticker"]) or {}).get("player_gsis_id"), r.get("stat")))
            if link:
                r["player_miss_layer"] = link.get("miss_layer")
                err = LAYER_TO_ERROR.get(link.get("miss_layer"))
                if err:
                    r["flags"].append(err)
    cls = Counter(r["classification"] for r in recs)
    flags = Counter(f for r in recs for f in r["flags"])
    pnl_by = defaultdict(float)
    for r in recs:
        pnl_by[r["classification"]] += r["total_episode_pnl"] or 0.0
    return {"expression_autopsy_version": EXPRESSION_AUTOPSY_VERSION, "n_positions": len(recs),
            "n_independent_theses": len(bsum), "classifications": dict(cls.most_common()), "flags": dict(flags.most_common()),
            "pnl_by_classification": {k: round(v, 2) for k, v in pnl_by.items()},
            "buckets": sorted(bsum.values(), key=lambda b: (str(b["week"]), -b["positions"], b["bucket"])),
            "positions": recs,
            "caution": "thesis buckets are INFERRED from what each contract pays on unless the handicap record supplied one; "
                       "script is judged from the headline rung of each thesis ladder, never from the wager's result"}
