"""Append-only horizon markers for the three-arm conductor, on market-data.

`nfl_edge.handicap.horizons` decides which decision horizons are due; its capture state for the report path lives
on `handicap-reports` and is rewritten on every publish. `market-data` is append-only, so this conductor records
a captured horizon as ONE NEW FILE named after the horizon id:

    data/shadow/arms/horizons/<slate>__<cluster>__T-<n>m.json

The gate needs only the file NAMES to know what is captured, which a blobless fetch of the branch provides in
seconds. A marker is written only after the snapshot was written or found already written; a failed build
leaves the horizon due for the next wake, exactly as the report conductor does.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

MARKER_DIR = "horizons"


def marker_name(horizon_id: str) -> str:
    return horizon_id.replace("|", "__") + ".json"


def horizon_id_of(marker_filename: str) -> str:
    return marker_filename[:-5].replace("__", "|") if marker_filename.endswith(".json") else marker_filename


def captured_state(marker_names) -> dict:
    """The `state` dict `due_horizons` expects, from marker file names alone."""
    return {"captured": {horizon_id_of(os.path.basename(n)): {"status": "CAPTURED"} for n in marker_names
                         if str(n).endswith(".json")}}


def write_markers(arms_root: str, horizon_ids, *, run_id: str, status: str, now: datetime | None = None) -> list:
    now = now or datetime.now(timezone.utc)
    d = os.path.join(arms_root, MARKER_DIR)
    os.makedirs(d, exist_ok=True)
    out = []
    for hid in [h.strip() for h in horizon_ids if h and h.strip()]:
        path = os.path.join(d, marker_name(hid))
        if os.path.exists(path):
            out.append(path)
            continue                      # append-only: an existing marker is never rewritten
        with open(path, "w") as f:
            json.dump({"horizon_id": hid, "captured_at": now.isoformat(), "snapshot_run_id": run_id,
                       "snapshot_status": status}, f, indent=1)
        out.append(path)
    return out
