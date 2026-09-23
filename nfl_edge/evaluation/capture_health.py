"""CAPTURE HEALTH: was every decision horizon actually delivered, and how late?

The weekly report counted markers whose status was MISSED -- but a missed horizon, by construction, never
writes a marker (nfl_edge/projection/horizons.py), so that count was always 0. On 2026 week 2 the 1pm cluster's
T-90m freeze simply never happened and the report said `missed_markers: 0`.

Delivery is therefore computed against the SCHEDULE, per kickoff cluster and horizon:

    NOT_YET_DUE        the trigger instant has not arrived
    DUE                trigger passed, kickoff not yet: still owed (the gate will serve it)
    DELIVERED_ON_TIME  the freeze's snapshot was observed <= 10 min after the trigger
    DELIVERED_LATE     10-45 min after (LATE_ACCEPTABLE in the record's own horizon_quality)
    DELIVERED_DEGRADED more than 45 min after (LATE_DEGRADED): the market it froze is not the intended one
    MISSED             kickoff passed with no freeze: never reconstructed

Lateness is snapshot time minus trigger, i.e. what the record's `horizon_lateness_min` measures, computed from the
marker's own snapshot id so it needs no projection rows. Scheduler attribution (the workflow simply was not
started in time, as on 2026-09-20 when GitHub fired the */15 horizon cron at 05:26, 09:54, 13:49 and 17:08) is
given when the caller supplies workflow start times; otherwise the cause is left UNATTRIBUTED, never guessed.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from nfl_edge.handicap.horizons import HORIZONS_MIN, cluster_kickoffs, horizon_id

CAPTURE_HEALTH_VERSION = "capture-health-1.0.0"
ON_TIME_MIN, ACCEPTABLE_MIN = 10.0, 45.0


def _dt(s):
    if s is None:
        return None
    if isinstance(s, datetime):
        return s if s.tzinfo else s.replace(tzinfo=timezone.utc)
    s = str(s)
    if len(s) == 16 and s[8] == "T" and s.endswith("Z"):             # 20260920T133947Z
        return datetime.strptime(s, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def horizon_delivery(slate_id: str, games: list, markers: list, now: datetime, *, workflow_starts=None,
                     horizons_min=None) -> dict:
    """games: [{game_id, kickoff_utc}]; markers: the marker JSON documents (horizon_id, snapshot_id, captured_at);
    workflow_starts: optional list of horizon-workflow start instants for scheduler attribution."""
    by_id = {m.get("horizon_id"): m for m in markers if m.get("horizon_id")}
    starts = sorted(_dt(s) for s in (workflow_starts or []) if s)
    rows = []
    for c in cluster_kickoffs(games):
        ko = _dt(c["kickoff_utc"])
        for h in sorted(horizons_min or HORIZONS_MIN, reverse=True):
            hid = horizon_id(slate_id, c["cluster_key"], h)
            trig = ko - timedelta(minutes=h)
            m = by_id.get(hid)
            row = {"horizon_id": hid, "cluster_key": c["cluster_key"], "horizon_min": h, "trigger_utc": trig.isoformat(),
                   "kickoff_utc": ko.isoformat(), "n_games": len(c.get("game_ids") or [])}
            if m:
                snap = _dt(m.get("snapshot_id"))
                late = (snap - trig).total_seconds() / 60.0 if snap else None
                row.update(snapshot_id=m.get("snapshot_id"), lateness_min=(round(late, 1) if late is not None else None),
                           status=("DELIVERED_ON_TIME" if late is not None and late <= ON_TIME_MIN else
                                   "DELIVERED_LATE" if late is not None and late <= ACCEPTABLE_MIN else "DELIVERED_DEGRADED"))
            elif now < trig:
                row["status"] = "NOT_YET_DUE"
            elif now < ko:
                row["status"] = "DUE"
            else:
                row["status"] = "MISSED"
            if row["status"] in ("DELIVERED_DEGRADED", "MISSED") and starts:
                window_end = min(ko, trig + timedelta(minutes=ACCEPTABLE_MIN))
                started = [s for s in starts if trig <= s <= window_end]
                row["cause"] = ("SCHEDULER_GAP: the horizon workflow was not started between the trigger and "
                                f"{window_end.isoformat()}" if not started else "RAN_BUT_NOT_DELIVERED: a run started in the window")
            elif row["status"] in ("DELIVERED_DEGRADED", "MISSED"):
                row["cause"] = "UNATTRIBUTED (no workflow start times supplied)"
            rows.append(row)
    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    owed = [r for r in rows if r["status"] not in ("NOT_YET_DUE", "DUE")]
    delivered = [r for r in owed if r["status"].startswith("DELIVERED")]
    return {"capture_health_version": CAPTURE_HEALTH_VERSION, "slate_id": slate_id, "as_of": now.isoformat(),
            "counts": counts, "owed": len(owed), "delivered": len(delivered),
            "delivered_pct": (round(100.0 * len(delivered) / len(owed), 1) if owed else None),
            "on_time_pct": (round(100.0 * counts.get("DELIVERED_ON_TIME", 0) / len(owed), 1) if owed else None),
            "missed": [r["horizon_id"] for r in rows if r["status"] == "MISSED"], "rows": rows}
