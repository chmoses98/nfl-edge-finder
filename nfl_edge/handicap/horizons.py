"""Decision-horizon gate: when does a slate deserve a *fresh* handicap packet?

The 2-hourly shadow-pricing cycle already refreshes the report as a side effect, which is the right default
cadence for a Tuesday. It is the wrong cadence near a kickoff: a packet built 119 minutes before a game is
not a T-30m packet, and the difference between those two is the whole point of a decision horizon.

So a cheap scheduled conductor wakes often, asks this module whether any game has crossed a horizon it has
not already captured, and only then pays for a full fresh build. Blindly running the expensive path every
thirty minutes all season would cost the same as this and tell us nothing new for most of it.

Design notes worth keeping:

* **Kickoff clusters, not games.** The report is a whole-slate document. Nine games kicking off at 17:00Z
  share one T-90m moment; firing nine identical full-slate builds would be nine copies of one packet.
  Kickoffs within `CLUSTER_TOLERANCE_MIN` of each other are one cluster, keyed by the EARLIEST kickoff in
  it -- measuring the horizon to the earliest game is the conservative choice.

* **Idempotent identity.** A horizon is `<slate_id>|<cluster kickoff>|T-<minutes>m`. It is derived from the
  schedule, not from a run counter, so two conductors that wake in the same minute compute the same id and
  the second one finds it already captured.

* **Late is captured, not lost.** GitHub cron is best-effort and routinely fires minutes late; a strict
  window would drop a horizon permanently for being ten minutes tardy. Instead every horizon whose trigger
  moment has passed and whose kickoff has not is *due*. One run satisfies all of a cluster's due horizons at
  once and marks them captured together -- a T-30m packet is strictly fresher than the T-90m packet it
  stands in for, so there is nothing left to go back for.

* **After kickoff, nothing.** A horizon whose kickoff has passed uncaptured is recorded as MISSED. It is
  never a reason to build a pregame packet for a game that has started.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

# Minutes before kickoff at which a fresh snapshot is guaranteed.
HORIZONS_MIN = [24 * 60, 6 * 60, 90, 30]

# Kickoffs this close together are one decision moment (the 16:05 and 16:25 Sunday windows).
CLUSTER_TOLERANCE_MIN = 30.0


def _dt(x):
    if isinstance(x, datetime):
        return x if x.tzinfo else x.replace(tzinfo=timezone.utc)
    if not x:
        return None
    try:
        return datetime.fromisoformat(str(x).replace("Z", "+00:00"))
    except ValueError:
        return None


def cluster_kickoffs(games: list, tolerance_min: float = CLUSTER_TOLERANCE_MIN) -> list:
    """Group games into kickoff clusters. Single-linkage on time; the cluster key is its earliest kickoff.

    `games` are dicts with `kickoff_utc` and `game_id`. Games without a kickoff are ignored -- an unscheduled
    game cannot have a decision horizon.
    """
    dated = []
    for g in games:
        ko = _dt(g.get("kickoff_utc"))
        if ko:
            dated.append((ko, g.get("game_id")))
    dated.sort()
    clusters = []
    for ko, gid in dated:
        if clusters and (ko - clusters[-1]["latest"]) <= timedelta(minutes=tolerance_min):
            clusters[-1]["game_ids"].append(gid)
            clusters[-1]["latest"] = ko
        else:
            clusters.append({"kickoff_utc": ko, "latest": ko, "game_ids": [gid]})
    for c in clusters:
        c["cluster_key"] = c["kickoff_utc"].strftime("%Y%m%dT%H%MZ")
        c["latest_kickoff_utc"] = c["latest"].isoformat()
        c["games"] = len(c["game_ids"])
        del c["latest"]
    return clusters


def horizon_id(slate_id: str, cluster_key: str, horizon_min: int) -> str:
    return f"{slate_id}|{cluster_key}|T-{int(horizon_min)}m"


def parse_horizon_id(hid: str) -> dict:
    """`<slate_id>|<YYYYmmddTHHMMZ>|T-<n>m` -> its parts, so a workflow can pass ids alone between jobs."""
    parts = str(hid).split("|")
    if len(parts) != 3 or not parts[2].startswith("T-") or not parts[2].endswith("m"):
        raise ValueError(f"not a horizon id: {hid!r}")
    slate, cluster_key, hpart = parts
    horizon_min = int(hpart[2:-1])
    ko = datetime.strptime(cluster_key, "%Y%m%dT%H%MZ").replace(tzinfo=timezone.utc)
    return {"horizon_id": hid, "slate_id": slate, "cluster_key": cluster_key,
            "horizon_min": horizon_min, "kickoff_utc": ko.isoformat(),
            "trigger_utc": (ko - timedelta(minutes=horizon_min)).isoformat()}


def due_horizons(slate_id: str, games: list, now: datetime, state: dict, *,
                 horizons_min=None, tolerance_min: float = CLUSTER_TOLERANCE_MIN) -> dict:
    """Which horizons are due now, which have gone missed, and whether a fresh build is warranted.

    `state` is the persisted capture record: `{"captured": {horizon_id: {...}}}`. It is never mutated here;
    the caller marks horizons captured only after a build actually succeeded, so a failed run leaves the
    horizon due for the next wake instead of silently consuming it.
    """
    horizons = sorted(horizons_min or HORIZONS_MIN, reverse=True)
    captured = (state or {}).get("captured") or {}
    due, missed, upcoming = [], [], []

    for c in cluster_kickoffs(games, tolerance_min):
        ko = c["kickoff_utc"]
        for h in horizons:
            hid = horizon_id(slate_id, c["cluster_key"], h)
            if hid in captured:
                continue
            trigger = ko - timedelta(minutes=h)
            rec = {"horizon_id": hid, "horizon_min": h, "cluster_key": c["cluster_key"],
                   "kickoff_utc": ko.isoformat(), "trigger_utc": trigger.isoformat(),
                   "games": c["games"], "game_ids": c["game_ids"],
                   "late_by_min": round((now - trigger).total_seconds() / 60.0, 1)}
            if now >= ko:
                rec["status"] = "MISSED"
                missed.append(rec)
            elif now >= trigger:
                rec["status"] = "DUE"
                due.append(rec)
            else:
                rec["status"] = "PENDING"
                rec["minutes_until_trigger"] = round((trigger - now).total_seconds() / 60.0, 1)
                upcoming.append(rec)

    due.sort(key=lambda r: r["horizon_min"])          # tightest horizon is the reason to run
    upcoming.sort(key=lambda r: r["minutes_until_trigger"])
    return {
        "slate_id": slate_id,
        "now": now.isoformat(),
        "should_run": bool(due),
        "due": due,
        "missed": missed,
        "next_pending": upcoming[0] if upcoming else None,
        "reason": (
            f"{due[0]['horizon_id']} is due ({due[0]['late_by_min']:.0f}m after its trigger); "
            f"{len(due)} horizon(s) satisfied by one build" if due
            else ("no horizon due" + (
                f"; next is {upcoming[0]['horizon_id']} in {upcoming[0]['minutes_until_trigger']:.0f}m"
                if upcoming else "; nothing left before kickoff"))),
    }


def mark_captured(state: dict, records: list, *, run_id=None, status: str = "CAPTURED",
                  now: datetime | None = None) -> dict:
    """Return a NEW state with `records` recorded as captured. Called only after a successful build."""
    now = now or datetime.now(timezone.utc)
    out = dict(state or {})
    captured = dict(out.get("captured") or {})
    for r in records:
        captured[r["horizon_id"]] = {
            "status": status,
            "captured_at": now.isoformat(),
            "horizon_min": r["horizon_min"],
            "kickoff_utc": r["kickoff_utc"],
            "trigger_utc": r["trigger_utc"],
            "late_by_min": r.get("late_by_min"),
            "workflow_run_id": run_id,
        }
    out["captured"] = captured
    out["updated_at"] = now.isoformat()
    return out


def prune(state: dict, now: datetime, keep_days: int = 45) -> dict:
    """Drop capture records for kickoffs long past. The file is a ledger of intent, not history."""
    cutoff = now - timedelta(days=keep_days)
    out = dict(state or {})
    out["captured"] = {k: v for k, v in (out.get("captured") or {}).items()
                       if (_dt(v.get("kickoff_utc")) or now) >= cutoff}
    return out
