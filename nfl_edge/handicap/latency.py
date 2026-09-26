"""SNAPSHOT vs PACKET latency: four numbers that used to be one.

`late_by_min` on a RUN NFL horizon record was the time from the horizon trigger to the moment the capture was
RECORDED -- after a ~20 minute build. Thursday 2026-09-24 ATL@GB read 22-23 minutes late on every horizon while its
snapshots were frozen on time (three-arm freeze +0.1 to +1.0 min). "Late" conflated two different failures: a
scheduler that did not start us, and a pipeline that takes twenty minutes. They are now reported separately:

    SNAPSHOT_CAPTURE_LATENCY        snapshot_frozen_at - trigger_utc
                                    how long after the horizon the evidence was frozen
    PIPELINE_PROCESSING_TIME        published_at - snapshot_frozen_at
                                    pricing + packet build + publication, after the freeze
    PACKET_PUBLISH_LATENCY          published_at - trigger_utc          (== the old late_by_min)
    TIME_REMAINING_TO_KICKOFF_AT_PUBLICATION
                                    kickoff_utc - published_at

so SNAPSHOT_CAPTURE_LATENCY + PIPELINE_PROCESSING_TIME == PACKET_PUBLISH_LATENCY by construction.

WHAT "FROZEN" MEANS FOR A RUN NFL PACKET. The instant the last input the packet reads was fixed: the later of the
Kalshi capture the ledger was priced from (`queried_at`) and this run's fresh context capture (its last source
retrieval; the run-id stamp when retrievals are unrecorded). A market capture that predates the trigger does not
make the snapshot "early": the freeze is the later of the two, and each component is recorded beside it.

REPORTING ONLY. Nothing here gates, reorders or rewrites a packet or a capture record.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

LATENCY_VERSION = "publication-latency-1.0.0"

METRICS = ("snapshot_capture_latency_min", "pipeline_processing_min", "packet_publish_latency_min",
           "time_remaining_to_kickoff_at_publication_min")


def _dt(x):
    if x is None or x == "":
        return None
    if isinstance(x, datetime):
        return x if x.tzinfo else x.replace(tzinfo=timezone.utc)
    s = str(x)
    try:
        if len(s) == 16 and s[8] == "T" and s.endswith("Z"):                 # 20260926T201218Z
            return datetime.strptime(s, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _min(a, b):
    return None if a is None or b is None else round((a - b).total_seconds() / 60.0, 1)


def context_frozen_at(context_manifest_path: str | None, run_id: str | None = None):
    """When this run's context capture finished retrieving: the latest `retrieved_at` among its sources."""
    best = None
    if context_manifest_path and os.path.exists(context_manifest_path):
        try:
            man = json.load(open(context_manifest_path))
        except (OSError, ValueError):
            man = {}
        for src in (man.get("sources") or {}).values():
            if isinstance(src, dict):
                t = _dt(src.get("retrieved_at"))
                if t and (best is None or t > best):
                    best = t
    return best or _dt(run_id)


def snapshot_frozen_at(kalshi_queried_at=None, context_frozen=None):
    """The later of the two input vintages; None when neither is known."""
    ts = [t for t in (_dt(kalshi_queried_at), _dt(context_frozen)) if t is not None]
    return max(ts) if ts else None


def publication_latency(*, trigger_utc, kickoff_utc, snapshot_frozen, published_at) -> dict:
    """The four metrics for one horizon. Any unknown instant leaves only the metrics that depend on it null."""
    trig, ko, frz, pub = _dt(trigger_utc), _dt(kickoff_utc), _dt(snapshot_frozen), _dt(published_at)
    return {
        "snapshot_frozen_at": frz.isoformat() if frz else None,
        "published_at": pub.isoformat() if pub else None,
        "snapshot_capture_latency_min": _min(frz, trig),
        "pipeline_processing_min": _min(pub, frz),
        "packet_publish_latency_min": _min(pub, trig),
        "time_remaining_to_kickoff_at_publication_min": _min(ko, pub),
    }


def manifest_latency(horizon_records: list, *, kalshi_queried_at, context_frozen, packet_built_at) -> dict:
    """The manifest's block. Written before publication, so the publish-side metrics are measured at the packet
    build (`packet_built_at`) and labelled as such; the horizon capture record carries the publication-time values."""
    frz = snapshot_frozen_at(kalshi_queried_at, context_frozen)
    rows = []
    for r in horizon_records or []:
        m = publication_latency(trigger_utc=r.get("trigger_utc"), kickoff_utc=r.get("kickoff_utc"),
                                snapshot_frozen=frz, published_at=packet_built_at)
        rows.append({"horizon_id": r.get("horizon_id"), "trigger_utc": r.get("trigger_utc"),
                     "kickoff_utc": r.get("kickoff_utc"), **m})
    return {
        "latency_version": LATENCY_VERSION,
        "reporting_only": True,
        "snapshot_frozen_at": frz.isoformat() if frz else None,
        "components": {"kalshi_capture_queried_at": (_dt(kalshi_queried_at).isoformat()
                                                     if _dt(kalshi_queried_at) else None),
                       "context_frozen_at": _dt(context_frozen).isoformat() if _dt(context_frozen) else None},
        "packet_built_at": _dt(packet_built_at).isoformat() if _dt(packet_built_at) else None,
        "publish_side_measured_at": "PACKET_BUILD (publication is ~15s later; state/horizons.json records it)",
        "horizons": rows,
    }
