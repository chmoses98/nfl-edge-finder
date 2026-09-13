"""Horizon freezing for SHADOW v2: T-24h, T-6h, T-90m, T-30m for every supportable family, plus the cycle.

Reuses the report conductor's due-horizon rule (`nfl_edge/handicap/horizons.due_horizons`: kickoff clusters,
late-is-captured, after-kickoff-is-MISSED) and the three-arm conductor's append-only marker files, under its
own marker directory so the v2 record never touches the live experiment's markers:

    data/shadow/v2/horizons/<slate>__<cluster>__T-<n>m.json

Every projection row written for a horizon records `horizon_label`, `horizon_target_min` and
`horizon_lateness_min` -- the actual snapshot's distance from the intended instant. A MISSED horizon is never
reconstructed: `label_snapshot` refuses to label a capture observed after kickoff, and a horizon whose trigger
was never served before kickoff has no marker and no rows, which is what MISSED means in the accounting.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from nfl_edge.handicap.horizons import HORIZONS_MIN, cluster_kickoffs, due_horizons, parse_horizon_id

MARKER_DIR = os.path.join("shadow", "v2", "horizons")
LABELS = {1440: "T-24h", 360: "T-6h", 90: "T-90m", 30: "T-30m"}
CYCLE = "CYCLE"


def marker_name(horizon_id: str) -> str:
    return horizon_id.replace("|", "__") + ".json"


def horizon_id_of(name: str) -> str:
    return name[:-5].replace("__", "|") if name.endswith(".json") else name


def captured_state(marker_names) -> dict:
    return {"captured": {horizon_id_of(os.path.basename(n)): {"status": "CAPTURED"} for n in marker_names if str(n).endswith(".json")}}


def due(slate_id: str, games: list, now: datetime, marker_names) -> dict:
    return due_horizons(slate_id, games, now, captured_state(marker_names), horizons_min=HORIZONS_MIN)


def label_snapshot(observed_at: datetime, kickoff: datetime, horizon_id: str | None) -> dict:
    """The horizon fields for one row. Refuses (raises) a snapshot observed at or after kickoff."""
    if observed_at >= kickoff:
        raise ValueError("a snapshot observed at or after kickoff cannot be labelled with a pregame horizon")
    mtk = (kickoff - observed_at).total_seconds() / 60.0
    if not horizon_id:
        return {"horizon_label": CYCLE, "horizon_target_min": None, "horizon_lateness_min": None, "horizon_id": None,
                "minutes_to_kickoff": mtk}
    h = parse_horizon_id(horizon_id)
    trigger = datetime.fromisoformat(h["trigger_utc"])
    return {"horizon_label": LABELS.get(h["horizon_min"], f"T-{h['horizon_min']}m"), "horizon_target_min": float(h["horizon_min"]),
            "horizon_lateness_min": (observed_at - trigger).total_seconds() / 60.0, "horizon_id": horizon_id,
            "minutes_to_kickoff": mtk}


def write_markers(root: str, horizon_ids, *, snapshot_id: str, status: str, now: datetime | None = None) -> list:
    now = now or datetime.now(timezone.utc)
    d = os.path.join(root, MARKER_DIR)
    os.makedirs(d, exist_ok=True)
    out = []
    for hid in [h.strip() for h in horizon_ids if h and h.strip()]:
        p = os.path.join(d, marker_name(hid))
        if os.path.exists(p):
            out.append(p)
            continue
        with open(p, "w") as f:
            json.dump({"horizon_id": hid, "captured_at": now.isoformat(), "snapshot_id": snapshot_id, "status": status}, f, indent=1)
        out.append(p)
    return out


def missed_report(slate_id: str, games: list, now: datetime, marker_names) -> dict:
    """What was missed, for the accounting: horizons whose kickoff passed with no marker."""
    d = due(slate_id, games, now, marker_names)
    return {"missed": d["missed"], "n_missed": len(d["missed"]), "n_captured": len(captured_state(marker_names)["captured"]),
            "clusters": cluster_kickoffs(games)}
