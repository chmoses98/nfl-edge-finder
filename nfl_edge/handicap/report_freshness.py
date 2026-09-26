"""Freshness gates for RUN NFL: is this report actually made of current data, or does it just look current?

`build_report.py` already refused a stale LEDGER. That is not the same question as whether the data is
current, and two ways past it were open:

* **The ledger's own age is not the market's age.** `price_slate.py` prices the newest Kalshi capture it can
  find; a ledger written sixty seconds ago from a capture taken ninety minutes ago has a perfect
  `written_at` and a stale market. The ledger manifest records which capture it priced -- `snapshot_run_id`
  is the capture manifest's `finished_at`, i.e. **when Kalshi was last successfully queried** -- so that is
  the timestamp the gate uses. It is deliberately not `minutes_since_price_change`, which measures when a
  price last MOVED and is a microstructure signal, not a staleness one.

* **A failed context capture was survivable.** A `force_fresh` run whose weather/injury capture died fell
  back to the newest published context, built happily, replaced `latest/` and marked a decision horizon
  captured. At T-30m that is the difference between "the inactive release is in this report" and "this
  report predates it and does not say so".

Both gates fail closed: no report, no publish, no horizon marked captured.

The context proof respects the capture's real semantics. `context_capture.py` is change-suppressed -- it
always writes `<run_id>.manifest.json`, and writes the ESPN/Sleeper blobs only when their content hash
changed. So the proof is that THIS run's manifest exists, retrieved everything it went for
(`failed_closed` empty), and is one of the captures the packet actually read. It is never a fabricated
timestamp on somebody else's file.
"""
from __future__ import annotations

import glob
import json
import os
from datetime import datetime, timezone

# Kalshi is polled roughly every ten minutes by the capture conductor. Thirty minutes is three missed
# passes: past that, a "fresh" report is quoting a market nobody has looked at recently.
DEFAULT_MAX_CAPTURE_AGE_MIN = 30.0


def _parse_run_stamp(run_id):
    """`20260909T060120Z` -> aware UTC datetime, or None."""
    try:
        return datetime.strptime(str(run_id), "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


#: How far back a caller-supplied freeze reference may lie. A fresh RUN NFL build freezes its pricing inputs ~12
#: minutes before the gate runs; anything much older than that is not a freeze of THIS build, and the gate falls
#: back to measuring at build time (the stricter reading) rather than trusting it.
MAX_FREEZE_REFERENCE_AGE_MIN = 60.0


def capture_vintage(ledger_manifest: dict, now: datetime, reference: datetime | None = None) -> dict:
    """When Kalshi was last successfully queried for the snapshot this ledger was priced from.

    `age_min` is always the age at BUILD time (`now`). A fresh RUN NFL build also passes `reference`: the instant it
    refreshed market-data and froze its pricing inputs. The gate then measures the capture at that freeze
    (`gate_age_min`), because the ~11 minutes of pricing and packet build that follow cannot make the market the
    packet quotes any older -- they make the PACKET later, which the latency metrics report separately. Measured at
    build time, a capture that landed on schedule could be refused for how long our own build took, and a refused
    T-30m horizon has no retry window. Both ages and the reference are recorded; nothing is inferred.

    A reference that is unparseable, in the future, before the capture itself, or older than
    MAX_FREEZE_REFERENCE_AGE_MIN is ignored and the gate measures at build time -- doubt resolves to the stricter
    reading, never the looser one.
    """
    man = ledger_manifest or {}
    run_id = man.get("snapshot_run_id")
    ts = _parse_run_stamp(run_id)
    age_now = None if ts is None else round((now - ts).total_seconds() / 60.0, 1)
    out = {
        "snapshot_run_id": run_id,
        "queried_at": ts.isoformat() if ts else None,
        "age_min": age_now,
        "basis": ("ledger manifest snapshot_run_id -- the capture manifest's finished_at, i.e. when the "
                  "Kalshi poll completed; not the time since a price last moved"),
    }
    ref = reference if (reference is None or reference.tzinfo) else reference.replace(tzinfo=timezone.utc)
    why = None
    if ref is not None:
        if ref > now:
            why = "freeze reference is in the future"
        elif (now - ref).total_seconds() / 60.0 > MAX_FREEZE_REFERENCE_AGE_MIN:
            why = f"freeze reference is more than {MAX_FREEZE_REFERENCE_AGE_MIN:.0f}m before the build"
        elif ts is not None and ts > ref:
            why = "the capture completed after the stated freeze, so the reference cannot be this build's freeze"
    if ref is not None and why is None and ts is not None:
        out.update(age_reference="PRICING_INPUT_FREEZE", age_reference_at=ref.isoformat(),
                   age_at_freeze_min=round((ref - ts).total_seconds() / 60.0, 1))
        out["gate_age_min"] = out["age_at_freeze_min"]
    else:
        out.update(age_reference="BUILD_TIME", age_reference_at=now.isoformat(), gate_age_min=age_now)
        if why:
            out["age_reference_rejected"] = why
    return out


def check_capture_age(vintage: dict, max_age_min) -> str | None:
    """Reason to refuse, or None. An unknown vintage is a refusal, not a pass."""
    if max_age_min is None:
        return None
    v = vintage or {}
    age = v.get("gate_age_min", v.get("age_min"))
    if age is None:
        return ("the ledger does not record which Kalshi capture it was priced from, so market freshness "
                "cannot be established (limit was "
                f"{float(max_age_min):.0f}m); refusing rather than assuming it is current")
    if age > float(max_age_min):
        when = (f"{age:.0f}m before this build froze its pricing inputs ({v.get('age_reference_at')})"
                if v.get("age_reference") == "PRICING_INPUT_FREEZE" else f"{age:.0f}m ago")
        return (f"the Kalshi capture this ledger was priced from completed {when} "
                f"({v.get('snapshot_run_id')}), over the {float(max_age_min):.0f}m limit; "
                "the ledger is fresh but the market it quotes is not")
    return None


def find_context_run(md_root: str, run_id: str) -> dict:
    """Locate one context capture's manifest under the tree the packet reads."""
    if not run_id:
        return {"found": False, "reason": "no context run id was supplied"}
    hits = sorted(glob.glob(os.path.join(md_root, "data", "context", "*", f"{run_id}.manifest.json")))
    if not hits:
        return {"found": False, "run_id": run_id,
                "reason": (f"context capture {run_id} wrote no manifest under {md_root}/data/context -- "
                           "the capture did not complete, or its output never reached the tree the packet "
                           "reads")}
    try:
        man = json.load(open(hits[0]))
    except (OSError, json.JSONDecodeError) as e:
        return {"found": False, "run_id": run_id, "reason": f"context manifest {run_id} is unreadable: {e}"}
    return {"found": True, "run_id": run_id, "path": hits[0],
            "failed_closed": man.get("failed_closed") or [],
            "sources": sorted((man.get("sources") or {}).keys())}


def check_fresh_context(md_root: str, run_id: str, *, now: datetime | None = None,
                        max_age_min: float | None = None) -> str | None:
    """Reason to refuse a force_fresh run, or None. Checked BEFORE the packet is built."""
    rec = find_context_run(md_root, run_id)
    if not rec.get("found"):
        return rec.get("reason")
    if rec.get("failed_closed"):
        return (f"context capture {run_id} failed closed on {rec['failed_closed']}; a fresh run must not "
                "quietly fall back to older weather, injuries or availability")
    if max_age_min is not None and now is not None:
        ts = _parse_run_stamp(run_id)
        if ts is None:
            return f"context capture id {run_id!r} is not a UTC run stamp; its age cannot be established"
        age = (now - ts).total_seconds() / 60.0
        if age > max_age_min:
            return (f"context capture {run_id} is {age:.0f}m old, over the {max_age_min:.0f}m limit for a "
                    "fresh run")
    return None


def check_context_reached_packet(run_id: str, packet_sources: dict) -> str | None:
    """Reason to refuse, or None. Checked AFTER the build: did the packet actually read this capture?"""
    if not run_id:
        return None
    used = list((packet_sources or {}).get("context_captures") or [])
    if run_id not in used:
        return (f"the packet was built from context captures {used}, which does not include this run's "
                f"fresh capture {run_id}; the report would carry older context while claiming to be fresh")
    return None
