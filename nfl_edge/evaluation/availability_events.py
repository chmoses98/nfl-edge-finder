"""AVAILABILITY CHANGE EVENTS: what changed about a player between one horizon and the next.

The frozen horizons already hold the raw state at each instant -- T-24h questionable, T-6h questionable, T-90m
inactive. What they do not hold is the CHANGE, and the change is likely to be the most informative player
research dimension the first week produces: a market that has not yet moved on a downgrade, a teammate removed
at the 90-minute list, a quarterback swapped on the Saturday depth chart.

Transitions are DERIVED, never captured separately. Each horizon's raw states stay exactly as frozen, and this
module reads them in order, so the derivation can be rebuilt from the records at any time and cannot contradict
them. Deriving rather than capturing also removes the obvious hindsight risk: a transition is only ever computed
between two records that both already exist, each with its own observation instant, and the ordering is taken
from those instants rather than from the order rows happen to appear in a file.

Two rules keep the output honest:

    UNKNOWN IS NOT A CHANGE.  A player who was EXPECTED_ACTIVE at T-24h and UNKNOWN at T-6h has not been
    downgraded; the source simply went quiet. Transitions into or out of UNKNOWN are labelled
    EVIDENCE_LOST / EVIDENCE_GAINED and never counted as availability movement.

    DIRECTION IS RANKED, NOT GUESSED.  States are ordered by how much they threaten participation, so a
    QUESTIONABLE -> OUT move is a DOWNGRADE and OUT -> QUESTIONABLE is an UPGRADE, whatever order the strings
    sort in.

Version: availability-events-1.0.0.
"""
from __future__ import annotations

AVAILABILITY_EVENTS_VERSION = "availability-events-1.0.0"

# Ordered by how much the state threatens participation. UNKNOWN is deliberately outside the ladder.
SEVERITY = {"EXPECTED_ACTIVE": 0, "PROBABLE": 1, "QUESTIONABLE": 2, "DOUBTFUL": 3, "EXPECTED_OUT": 4,
            "OUT": 5, "INACTIVE_CONFIRMED": 6}
UNKNOWN = "UNKNOWN"
NO_CHANGE, UPGRADE, DOWNGRADE = "NO_CHANGE", "UPGRADE", "DOWNGRADE"
EVIDENCE_LOST, EVIDENCE_GAINED = "EVIDENCE_LOST", "EVIDENCE_GAINED"
HORIZON_ORDER = ("T-24h", "T-6h", "T-90m", "T-30m", "CYCLE")


def _sev(state):
    return SEVERITY.get(str(state or UNKNOWN).upper())


def direction(prev, cur) -> str:
    a, b = _sev(prev), _sev(cur)
    if a is None and b is None:
        return NO_CHANGE
    if a is None:
        return EVIDENCE_GAINED
    if b is None:
        return EVIDENCE_LOST
    if b > a:
        return DOWNGRADE
    if b < a:
        return UPGRADE
    return NO_CHANGE


def _key(rec):
    pc = rec.get("player_context") or {}
    return (rec.get("subject_id") or pc.get("player_id"), rec.get("game_id"))


def _order(rec):
    """Sort by the observation instant, falling back to the horizon's nominal position."""
    return (str(rec.get("observed_at") or ""), HORIZON_ORDER.index(rec.get("horizon_label"))
            if rec.get("horizon_label") in HORIZON_ORDER else len(HORIZON_ORDER))


def transitions(records) -> list:
    """One row per (player, game, consecutive horizon pair) that carries any change worth keeping."""
    by = {}
    for r in records:
        k = _key(r)
        if k[0] and k[1]:
            by.setdefault(k, []).append(r)
    out = []
    for (pid, gid), rows in by.items():
        rows = sorted(rows, key=_order)
        seen = set()
        chain = []
        for r in rows:                                       # one record per horizon; arms repeat the same context
            h = r.get("horizon_label") or "CYCLE"
            if (h, r.get("observed_at")) in seen:
                continue
            seen.add((h, r.get("observed_at")))
            chain.append(r)
        for prev, cur in zip(chain, chain[1:]):
            ev = _pair(pid, gid, prev, cur)
            if ev:
                out.append(ev)
    return out


def _pair(pid, gid, prev, cur) -> dict | None:
    p, c = prev.get("player_context") or {}, cur.get("player_context") or {}
    d = direction(p.get("availability_state"), c.get("availability_state"))
    inj = (p.get("injury_state"), c.get("injury_state"))
    rep = (p.get("report_status"), c.get("report_status"))
    qb = (p.get("qb_schedule") or p.get("qb_depth_chart"), c.get("qb_schedule") or c.get("qb_depth_chart"))
    rank = (p.get("depth_chart_rank"), c.get("depth_chart_rank"))
    mates = (p.get("teammates_out_or_doubtful"), c.get("teammates_out_or_doubtful"))
    off = (p.get("official_inactive_state"), c.get("official_inactive_state"))
    changed = {
        "availability_changed_since_prior_horizon": d not in (NO_CHANGE,),
        "availability_direction": d,
        "injury_listing_changed": inj[0] != inj[1],
        "report_status_changed": rep[0] != rep[1],
        "qb_status_changed": bool(qb[0]) and bool(qb[1]) and qb[0] != qb[1],
        "depth_chart_role_changed": rank[0] is not None and rank[1] is not None and rank[0] != rank[1],
        "key_teammate_removed": (mates[0] is not None and mates[1] is not None and mates[1] > mates[0]),
        "official_inactive_confirmed": off[1] == "INACTIVE_CONFIRMED" and off[0] != "INACTIVE_CONFIRMED",
    }
    if not any(v for k, v in changed.items() if k != "availability_direction"):
        return None
    return {"availability_events_version": AVAILABILITY_EVENTS_VERSION, "player_id": pid, "game_id": gid,
            "from_horizon": prev.get("horizon_label"), "to_horizon": cur.get("horizon_label"),
            "from_observed_at": prev.get("observed_at"), "to_observed_at": cur.get("observed_at"),
            "from_record_id": prev.get("record_id"), "to_record_id": cur.get("record_id"),
            "minutes_to_kickoff_from": prev.get("minutes_to_kickoff"), "minutes_to_kickoff_to": cur.get("minutes_to_kickoff"),
            # raw states are kept on both sides: the derivation never replaces what was frozen
            "availability_from": p.get("availability_state"), "availability_to": c.get("availability_state"),
            "injury_state_from": inj[0], "injury_state_to": inj[1],
            "report_status_from": rep[0], "report_status_to": rep[1],
            "qb_from": qb[0], "qb_to": qb[1], "depth_rank_from": rank[0], "depth_rank_to": rank[1],
            "teammates_out_from": mates[0], "teammates_out_to": mates[1],
            "official_inactive_from": off[0], "official_inactive_to": off[1], **changed}


def summarize(events) -> dict:
    by_dir, by_kind, by_hop = {}, {}, {}
    flags = ("injury_listing_changed", "report_status_changed", "qb_status_changed", "depth_chart_role_changed",
             "key_teammate_removed", "official_inactive_confirmed")
    for e in events:
        by_dir[e["availability_direction"]] = by_dir.get(e["availability_direction"], 0) + 1
        hop = f"{e.get('from_horizon')}->{e.get('to_horizon')}"
        by_hop[hop] = by_hop.get(hop, 0) + 1
        for f in flags:
            if e.get(f):
                by_kind[f] = by_kind.get(f, 0) + 1
    return {"availability_events_version": AVAILABILITY_EVENTS_VERSION, "n_events": len(events),
            "by_direction": dict(sorted(by_dir.items())), "by_kind": dict(sorted(by_kind.items())),
            "by_horizon_hop": dict(sorted(by_hop.items())),
            "downgrades": by_dir.get(DOWNGRADE, 0), "upgrades": by_dir.get(UPGRADE, 0),
            "note": "EVIDENCE_LOST / EVIDENCE_GAINED are source outages, not availability movement"}
