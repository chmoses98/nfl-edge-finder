"""WHEN preflight polling is worth an Airtable request. Not what it decides -- only when it may look.

THE CONSTRAINT THAT SHAPES THIS. The owner's Airtable workspace is on the Free plan: 1,000 Web API requests
per calendar month, shared with the archival bridge, ChatGPT's own reads and writes, retries and tests. A
poll that wakes every ten minutes all day would spend ~4,300 requests a month discovering nothing. So GitHub
may wake as often as it likes, and this module answers the cheap question first: is NOW inside a window when
an NFL preflight request could plausibly be waiting? Only then is an Airtable request spent.

A GITHUB WAKE IS NOT AN AIRTABLE CALL. That distinction is the whole design. The gate reads a CSV already on
disk, uses the standard library only, and needs no secret of any kind.

WINDOWS COME FROM THE REAL SCHEDULE, NEVER FROM WEEKDAY FOLKLORE. Nothing here knows that football is
usually played on Sunday at 1pm. It clusters the ACTUAL kickoffs from the canonical nflverse schedule using
`horizons.cluster_kickoffs` -- the same 30-minute single-linkage clustering the horizon machinery already
uses -- so Thanksgiving, Christmas, a Saturday in week 16, a Friday, a Wednesday, an international morning,
the postseason and any reschedule are all supported because they are all just kickoffs in the file.

PRIMARY AND SECONDARY. Within one US-Eastern calendar date, the cluster with the MOST games is the primary
one -- the main slate, where a batch of candidates is most likely to be waiting -- and it opens three hours
before its earliest kickoff. Every other cluster that day opens two hours before its own earliest kickoff.
Both close ten minutes before kickoff, because a request that cannot be answered before the ball is snapped
is not worth an Airtable request: `decision_before_kickoff` would refuse it anyway.

THE UNION IS LOAD-BEARING. Overlapping windows are merged, so the gate's answer is ACTIVE or INACTIVE and
never "three clusters are open". Three simultaneous windows must cost ONE Airtable request per wake, not
three -- that is the difference between fitting in the Free allowance and not.

FAIL CLOSED, LOUDLY. An unreadable schedule is `SCHEDULE_ERROR`, never `OUTSIDE_PREFLIGHT_WINDOW`. Not
knowing whether a window is open is not permission to open one, and it is not a quiet success either: the
caller is expected to fail the run so the silence gets noticed.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from nfl_edge.data import nfl_calendar as CAL
from nfl_edge.handicap import horizons as H

# How long before kickoff each kind of cluster starts accepting polls, and when every one stops.
#
# The primary cluster gets longer because it is where a whole slate's worth of candidates lands at once, and
# the owner works up to it over a morning. A secondary cluster is usually one or two games decided nearer
# the time. CLOSE_LEAD_MIN is not a safety control -- `decision_before_kickoff` is -- it just stops us
# spending requests on a question whose answer is already fixed.
PRIMARY_LEAD_MIN = 180
SECONDARY_LEAD_MIN = 120
CLOSE_LEAD_MIN = 10

# The canonical clustering, reused rather than reimplemented, so a change to the horizon machinery's notion
# of "one kickoff cluster" moves this with it instead of leaving two definitions to drift apart.
TOLERANCE_MIN = H.CLUSTER_TOLERANCE_MIN

STATUS_ACTIVE = "ACTIVE"
STATUS_INACTIVE = "OUTSIDE_PREFLIGHT_WINDOW"
STATUS_ERROR = "SCHEDULE_ERROR"


class ScheduleUnavailable(RuntimeError):
    """The calendar could not be read. Deliberately NOT a quiet 'no window' -- see the module docstring."""


def _playable(games: list) -> list:
    """Scheduled, non-preseason games. A game with no kickoff time cannot define a window."""
    return [g for g in games
            if g.get("kickoff_utc") and (g.get("game_type") or "REG").upper() not in CAL.PRESEASON_TYPES]


def clusters(games: list, *, tolerance_min: float = TOLERANCE_MIN) -> list:
    """Kickoff clusters, each tagged with the US-Eastern calendar date the schedule itself gives it.

    The date comes from the row's `gameday`, not from converting the UTC kickoff back to Eastern. That is
    exact by construction and avoids the one genuinely awkward case: an offset lookup near a DST boundary
    needs to know the local time to decide the offset that would produce the local time.
    """
    playable = _playable(games)
    day_of = {g.get("game_id"): g.get("gameday") for g in playable}
    out = []
    for c in H.cluster_kickoffs(playable, tolerance_min=tolerance_min):
        days = [day_of.get(gid) for gid in c["game_ids"] if day_of.get(gid)]
        c = dict(c)
        # The earliest kickoff keys the cluster, so its game-day is the one that game is played on.
        c["game_day"] = days[0] if days else None
        out.append(c)
    return out


def primary_cluster(day_clusters: list) -> dict:
    """The main slate for one Eastern date: most games, ties broken by the earliest kickoff."""
    return min(day_clusters, key=lambda c: (-int(c.get("games") or 0), c["kickoff_utc"]))


def windows(games: list, *, tolerance_min: float = TOLERANCE_MIN,
            primary_lead_min: int = PRIMARY_LEAD_MIN,
            secondary_lead_min: int = SECONDARY_LEAD_MIN,
            close_lead_min: int = CLOSE_LEAD_MIN) -> list:
    """Every polling window the season implies, MERGED. `[(start_utc, end_utc), ...]`, sorted.

    Merging is not tidiness. Un-merged, a day with three open clusters would invite three Airtable requests
    per wake; merged, the gate can only ever say yes once.
    """
    by_day: dict = {}
    for c in clusters(games, tolerance_min=tolerance_min):
        by_day.setdefault(c["game_day"], []).append(c)

    spans = []
    for day_clusters in by_day.values():
        primary = primary_cluster(day_clusters)
        for c in day_clusters:
            lead = primary_lead_min if c["cluster_key"] == primary["cluster_key"] else secondary_lead_min
            ko = c["kickoff_utc"]
            start, end = ko - timedelta(minutes=lead), ko - timedelta(minutes=close_lead_min)
            if start < end:
                spans.append((start, end))

    spans.sort()
    merged: list = []
    for start, end in spans:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def evaluate(games: list, now: datetime, *, tolerance_min: float = TOLERANCE_MIN,
             primary_lead_min: int = PRIMARY_LEAD_MIN,
             secondary_lead_min: int = SECONDARY_LEAD_MIN,
             close_lead_min: int = CLOSE_LEAD_MIN) -> dict:
    """Is NOW inside a polling window? One ACTIVE/INACTIVE answer, plus context for the Actions log.

    Boundaries are INCLUSIVE at both ends: a wake landing exactly on T-180 or exactly on T-10 is inside.
    Half-open would be defensible; inclusive is chosen because the cost of one extra poll is one request and
    the cost of missing the opening wake is a batch that waits ten more minutes against a 30-minute
    request-age limit.
    """
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    spans = windows(games, tolerance_min=tolerance_min, primary_lead_min=primary_lead_min,
                    secondary_lead_min=secondary_lead_min, close_lead_min=close_lead_min)
    here = [(s, e) for s, e in spans if s <= now <= e]

    out = {
        "status": STATUS_ACTIVE if here else STATUS_INACTIVE,
        "active": bool(here),
        "now_utc": now.isoformat(),
        "active_window_start_utc": here[0][0].isoformat() if here else None,
        "active_window_end_utc": here[0][1].isoformat() if here else None,
        # How many merged windows contain NOW. It is 1 whenever the gate says yes -- merging guarantees it --
        # and the field exists so a regression that stopped merging would be visible rather than merely
        # expensive.
        "active_window_count": len(here),
        "total_windows": len(spans),
    }

    # Which clusters this window was built from, for the log only. Never used to decide anything.
    if here:
        start, end = here[0]
        members = [c for c in clusters(games, tolerance_min=tolerance_min)
                   if start <= c["kickoff_utc"] - timedelta(minutes=close_lead_min) <= end
                   or start <= c["kickoff_utc"] <= end + timedelta(minutes=close_lead_min)]
        out["active_cluster_count"] = len(members)
        if members:
            first = min(members, key=lambda c: c["kickoff_utc"])
            out["game_day"] = first.get("game_day")
            out["primary_cluster_utc"] = first["kickoff_utc"].isoformat()
    else:
        out["active_cluster_count"] = 0
        nxt = [s for s, _e in spans if s > now]
        out["next_window_start_utc"] = min(nxt).isoformat() if nxt else None
    return out
