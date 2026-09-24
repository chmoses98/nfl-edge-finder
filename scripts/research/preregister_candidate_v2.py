#!/usr/bin/env python3
"""OWNER TOOL: preregister ONE shortlisted discovery candidate as a Stage-B test. Append-only. Dry run by default.

    python3 scripts/research/preregister_candidate_v2.py \\
        --id 'HG-2026W02-...' \\
        --source-registry /tmp/md/data/shadow/v2/hypotheses/hypotheses.jsonl \\
        --shortlist /tmp/md/data/shadow/v2/reports/2026_wk03.preregistration_shortlist.json \\
        --test-week-lo 4 --test-week-hi 18 --first-test-kickoff 2026-10-02T00:15:00Z \\
        [--registry research/hypothesis_registry/v2/hypotheses.jsonl] [--confirm]

WHO RUNS THIS: a person. Nothing in the pipeline calls it; the weekly report only prints a SHORTLIST FOR OWNER
REVIEW. Choosing to test a slice is a decision -- every test added widens the Bonferroni family and costs every
other test power -- so it is made by hand, one candidate at a time, and it is recorded with who-ran-it's note.

WHAT IT DOES (with --confirm; without it, it prints what it would write and writes nothing):

  1. reads the candidate's GENERATED line from the source (automatic, published) registry;
  2. refuses unless it is still a Stage-A discovery candidate, and -- when --shortlist is given -- unless it is on
     that shortlist (the shortlist's proposed window must also contain the requested window);
  3. refuses when the preregistration time is not strictly before the first kickoff of the test window
     (`preregister()` enforces it too): a window whose first game has started has been observed;
  4. copies the GENERATED line VERBATIM (same bytes of content, same line_hash) into the committed registry if
     it is not already there, then appends the PREREGISTERED line through `preregister()`, carrying the frozen
     PREREGISTERED_THRESHOLDS, their hash and a written evaluation plan.

It never deletes or rewrites a line, never moves a hypothesis to TESTING or a verdict, and never touches a model
weight or a production-eligibility state. Re-running it for a candidate already preregistered writes nothing.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.research import hypothesis_registry_v2 as HR                        # noqa: E402


class Refused(SystemExit):
    def __init__(self, msg):
        super().__init__(f"REFUSED: {msg}")
        self.msg = msg


def evaluation_plan(h: dict, window: dict) -> dict:
    th = HR.PREREGISTERED_THRESHOLDS[HR.KIND_SLICE]
    loc = h.get("locator") or {}
    ge = h.get("generation_evidence") or {}
    return {"hypothesis": f"{h.get('condition')}: {h.get('direction')} (model-minus-market Brier keeps the generation sign)",
            "slice": {"segment": loc.get("segment"), "value": loc.get("value"), "model_arm": ge.get("model_arm"),
                      "model_versions": ge.get("model_versions"), "horizon_label": ge.get("horizon_label")},
            "unit": "game (clustered SE over independent games)",
            "metric": th["metric"], "evidence_basis": "synchronized PROSPECTIVE_FROZEN rows only",
            "test_window": window, "generation_window_never_counts": True,
            "generation_effect": h.get("effect_size"), "generation_se": h.get("uncertainty"),
            "slices_searched_at_generation": h.get("candidate_slices_considered"),
            "supported_suggestion": th["supported_suggestion"], "not_supported_suggestion": th["not_supported_suggestion"],
            "min_new_independent_games": th["min_new_independent_games"], "min_paired_outcomes": th["min_paired_outcomes"],
            "multiplicity": "Bonferroni over the Stage B/C family at evaluation time",
            "decision": HR.SUGGESTION_ONLY}


def _append_verbatim(path: str, row: dict) -> None:
    """The GENERATED line as it was published: same content, same line_hash, previous_hash None."""
    want = {k: v for k, v in row.items() if k != "line_hash"}
    if HR._line_hash(want) != row.get("line_hash"):
        raise Refused("the source line's hash does not verify; it will not be copied")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(row, sort_keys=True, default=str) + "\n")


def plan(a) -> dict:
    """Every check, no writes. Returns what --confirm would do."""
    src_lines = [r for r in HR.load(a.source_registry) if r.get("id") == a.id]
    if not src_lines:
        raise Refused(f"{a.id} is not in {a.source_registry}")
    src = src_lines[-1]
    target = HR.current(a.registry).get(a.id)
    if target is not None and HR.stage(target) != HR.STAGE_DISCOVERY:
        return {"id": a.id, "action": "NOTHING", "reason": f"already {target['status']} ({HR.stage(target)}) in {a.registry}"}
    if src.get("status") != "GENERATED" or HR.stage(src) != HR.STAGE_DISCOVERY:
        raise Refused(f"{a.id} is {src.get('status')} in the source registry; only a Stage-A GENERATED candidate can be preregistered")
    if target is not None and target.get("line_hash") != src_lines[0].get("line_hash"):
        raise Refused(f"{a.id} exists in {a.registry} with a different GENERATED line than the source; resolve by hand")
    window = {"season": int(a.season or src["generation_window"]["season"]), "week_lo": int(a.test_week_lo), "week_hi": int(a.test_week_hi)}
    if a.shortlist:
        doc = json.load(open(a.shortlist))
        entry = next((e for e in (doc or {}).get("shortlist") or [] if e.get("id") == a.id), None)
        if entry is None:
            raise Refused(f"{a.id} is not on the shortlist {a.shortlist}")
        prop = entry.get("proposed_confirmatory_window")
        if not HR._window_contained(window, prop):
            raise Refused(f"the requested window {window} is not inside the shortlist's proposed window {prop}")
    if not a.first_test_kickoff:
        raise Refused("--first-test-kickoff (ISO UTC kickoff of the first game in the test window) is required")
    now = HR._parse_ts(a.now) if a.now else datetime.now(timezone.utc)
    kick = HR._parse_ts(a.first_test_kickoff)
    if now >= kick:
        raise Refused(f"now {now.isoformat()} is not before the first test kickoff {kick.isoformat()}; the window has been observed")
    # the window checks preregister() will run, run here first so a dry run reports them
    HR._check_future_window(src["generation_window"], window, what="test window")
    reg = HR.registered_future_window(src)
    if reg and not HR._window_contained(window, reg):
        raise Refused(f"the test window {window} is not inside the window fixed at registration {reg}")
    return {"id": a.id, "action": "PREREGISTER", "copy_generated_line": target is None, "test_window": window,
            "preregistered_at": now.isoformat(), "first_test_kickoff_utc": kick.isoformat(),
            "thresholds_version": HR.PREREGISTERED_THRESHOLDS["version"],
            "thresholds_sha": HR.thresholds_sha(HR.PREREGISTERED_THRESHOLDS),
            "evaluation_plan": evaluation_plan(src, window), "_source_row": src, "_now": now}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--id", required=True)
    ap.add_argument("--source-registry", required=True, help="the automatic registry holding the GENERATED line (market-data copy)")
    ap.add_argument("--registry", default=os.path.join(ROOT, HR.DEFAULT_PATH), help="the committed registry the preregistration is appended to")
    ap.add_argument("--shortlist", default="", help="<label>.preregistration_shortlist.json; when given the candidate must be on it")
    ap.add_argument("--season", type=int, default=0)
    ap.add_argument("--test-week-lo", type=int, required=True)
    ap.add_argument("--test-week-hi", type=int, default=18)
    ap.add_argument("--first-test-kickoff", default="", help="ISO UTC kickoff of the first game in the test window")
    ap.add_argument("--now", default="", help="ISO time of the preregistration (default: now)")
    ap.add_argument("--note", default="preregistered by the owner from the SHORTLIST FOR OWNER REVIEW")
    ap.add_argument("--confirm", action="store_true", help="write; without it this is a dry run")
    a = ap.parse_args(argv)
    p = plan(a)
    shown = {k: v for k, v in p.items() if not k.startswith("_")}
    if p["action"] == "NOTHING" or not a.confirm:
        print(json.dumps({"dry_run": not a.confirm, **shown}, indent=1, default=str))
        return 0
    if p["copy_generated_line"]:
        _append_verbatim(a.registry, p["_source_row"])
    row = HR.preregister(a.id, test_window=p["test_window"], thresholds=HR.PREREGISTERED_THRESHOLDS,
                         evaluation_plan=p["evaluation_plan"], preregistered_at=p["_now"],
                         first_test_kickoff_utc=p["first_test_kickoff_utc"], note=a.note, path=a.registry)
    print(json.dumps({"wrote": a.id, "status": row["status"], "stage": HR.stage(row), "registry": a.registry,
                      "line_hash": row["line_hash"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
