#!/usr/bin/env python3
"""Explicit automation state for an automatic pipeline run, in the job summary and as one JSON line.

    python3 scripts/ops/automation_state.py postgame --summary "$GITHUB_STEP_SUMMARY" [--out state.json]

Reads the postgame-settle step outputs from the environment (GATE_WORK, SETTLE_STATUS, WRITTEN, DEFERRED,
ARMS_STATUS, AUTOPSY_STATUS, JOB_STATUS, INPUT_GAMES) and states one of WAITING_FOR_SOURCE / PARTIAL_COMPLETE /
COMPLETE / BLOCKED (nfl_edge/handicap/automation.classify_postgame). Reporting only: exit 0 always, so the state
line can never be the reason a run is red -- the run's own steps decide that.

    python3 scripts/ops/automation_state.py shadow-v2-settle --summary "$GITHUB_STEP_SUMMARY"

Reads SETTLE_STATUS, CLOSES_STATUS, INDEX_WRITTEN, EVIDENCE_PUBLISH, RESEARCH, RESEARCH_PUBLISH, JOB_STATUS and
states HEALTHY / DEGRADED / FAILED / NOT_APPLICABLE (classify_shadow_v2_settle). DEGRADED also prints a ::warning::.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.handicap.automation import classify_postgame, classify_shadow_v2_settle  # noqa: E402


def postgame_state(env) -> dict:
    st = classify_postgame(gate_work=env.get("GATE_WORK"), settle_status=env.get("SETTLE_STATUS"),
                           written=env.get("WRITTEN"), deferred=env.get("DEFERRED"),
                           arms_status=env.get("ARMS_STATUS"), autopsy_status=env.get("AUTOPSY_STATUS"),
                           job_status=env.get("JOB_STATUS"), named_games=bool((env.get("INPUT_GAMES") or "").strip()))
    return {"pipeline": "postgame-settle", "at": datetime.now(timezone.utc).isoformat(),
            "workflow_run_id": env.get("GITHUB_RUN_ID"), "event": env.get("GITHUB_EVENT_NAME"),
            "actor": env.get("GITHUB_TRIGGERING_ACTOR") or env.get("GITHUB_ACTOR"), **st}


def shadow_v2_settle_state(env) -> dict:
    st = classify_shadow_v2_settle(settle_status=env.get("SETTLE_STATUS"), closes_status=env.get("CLOSES_STATUS"),
                                   index_written=env.get("INDEX_WRITTEN"),
                                   evidence_publish=env.get("EVIDENCE_PUBLISH"), research=env.get("RESEARCH"),
                                   research_publish=env.get("RESEARCH_PUBLISH"), job_status=env.get("JOB_STATUS"))
    return {"pipeline": "shadow-v2-settle", "at": datetime.now(timezone.utc).isoformat(),
            "workflow_run_id": env.get("GITHUB_RUN_ID"), "event": env.get("GITHUB_EVENT_NAME"),
            "actor": env.get("GITHUB_TRIGGERING_ACTOR") or env.get("GITHUB_ACTOR"),
            "state": st["health"], **st}


PIPELINES = {"postgame": postgame_state, "shadow-v2-settle": shadow_v2_settle_state}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("pipeline", choices=sorted(PIPELINES))
    ap.add_argument("--summary", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    try:
        doc = PIPELINES[a.pipeline](os.environ)
    except Exception as e:  # noqa: BLE001 -- reporting only
        print(f"::warning::automation state could not be computed: {e}")
        return 0
    print(json.dumps(doc))
    if doc.get("health") == "DEGRADED":
        # A warning annotation, never a red run: DEGRADED means the primary product is done.
        print(f"::warning::{doc['pipeline']} DEGRADED: {doc['reason']}")
    if a.summary:
        with open(a.summary, "a") as f:
            f.write(f"\n### Automation state: **{doc['state']}**\n\n{doc['reason']}\n\n"
                    f"_event `{doc['event']}`, actor `{doc['actor']}`_\n")
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
        with open(a.out, "w") as f:
            json.dump(doc, f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
