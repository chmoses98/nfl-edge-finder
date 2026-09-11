"""APPEND-ONLY HYPOTHESIS REGISTRY v2 (Part 23).

`research/hypothesis_registry/v2/hypotheses.jsonl`: one JSON object per line, never rewritten. A hypothesis is
created GENERATED with the evidence window that produced it; every later change is a new line (a transition)
carrying the previous line's hash, so the history is the file. Statuses:

    GENERATED -> PREREGISTERED -> TESTING -> SUPPORTED | NOT_SUPPORTED | INCONCLUSIVE -> RETIRED

The rule that matters: a hypothesis generated from an evidence window can never be SUPPORTED (or NOT_SUPPORTED)
on that same window. `transition()` refuses a test window that overlaps the generation window. Week 1 slices
are HYPOTHESIS_GENERATING; the earliest confirmatory evidence is Week 2 or later.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone

STATUSES = ("GENERATED", "PREREGISTERED", "TESTING", "SUPPORTED", "NOT_SUPPORTED", "INCONCLUSIVE", "RETIRED")
ALLOWED = {"GENERATED": {"PREREGISTERED", "RETIRED"}, "PREREGISTERED": {"TESTING", "RETIRED"}, "TESTING": {"SUPPORTED", "NOT_SUPPORTED", "INCONCLUSIVE", "RETIRED"},
           "SUPPORTED": {"RETIRED", "TESTING"}, "NOT_SUPPORTED": {"RETIRED", "TESTING"}, "INCONCLUSIVE": {"TESTING", "RETIRED"}, "RETIRED": set()}
REGISTRY_VERSION = "hypotheses-2.0.0"
DEFAULT_PATH = os.path.join("research", "hypothesis_registry", "v2", "hypotheses.jsonl")


class RegistryError(ValueError):
    pass


def _line_hash(obj: dict) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()[:16]


def _windows_overlap(a: dict, b: dict) -> bool:
    """Windows are {season, week_lo, week_hi} (inclusive). Different seasons never overlap."""
    if not a or not b or a.get("season") != b.get("season"):
        return False
    return not (int(a["week_hi"]) < int(b["week_lo"]) or int(b["week_hi"]) < int(a["week_lo"]))


def load(path: str = DEFAULT_PATH) -> list:
    if not os.path.exists(path):
        return []
    return [json.loads(l) for l in open(path) if l.strip()]


def current(path: str = DEFAULT_PATH) -> dict:
    """Latest state per hypothesis id (last line wins; lines are never edited)."""
    out = {}
    for row in load(path):
        out[row["id"]] = row
    return out


def _append(path: str, row: dict) -> dict:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    row = dict(row); row["line_hash"] = _line_hash({k: v for k, v in row.items() if k != "line_hash"})
    with open(path, "a") as f:
        f.write(json.dumps(row, sort_keys=True, default=str) + "\n")
    return row


def add(*, hid: str, market_family: str, condition: str, direction: str, expected_mechanism: str, evaluation_metric: str, minimum_sample: int,
        generation_window: dict, future_test_window: dict | None, generated_by: str, effect_size: float | None = None, uncertainty: float | None = None,
        sample_size: int | None = None, game_count: int | None = None, candidate_slices_considered: int | None = None, path: str = DEFAULT_PATH, now=None) -> dict:
    if hid in current(path):
        raise RegistryError(f"{hid} already exists; transitions are new lines, not re-adds")
    if future_test_window and _windows_overlap(generation_window, future_test_window):
        raise RegistryError("the future test window overlaps the generation window; Week-1 evidence cannot confirm a Week-1 hypothesis")
    now = now or datetime.now(timezone.utc)
    return _append(path, {"registry_version": REGISTRY_VERSION, "id": hid, "created_at": now.isoformat(), "status": "GENERATED", "evidence_type": "HYPOTHESIS_GENERATING",
                          "market_family": market_family, "condition": condition, "direction": direction, "expected_mechanism": expected_mechanism,
                          "evaluation_metric": evaluation_metric, "minimum_sample": minimum_sample, "generation_window": generation_window,
                          "future_test_window": future_test_window, "generated_by": generated_by, "effect_size": effect_size, "uncertainty": uncertainty,
                          "sample_size": sample_size, "game_count": game_count, "candidate_slices_considered": candidate_slices_considered, "previous_hash": None})


def transition(hid: str, new_status: str, *, note: str = "", test_window: dict | None = None, result: dict | None = None, path: str = DEFAULT_PATH, now=None) -> dict:
    cur = current(path).get(hid)
    if cur is None:
        raise RegistryError(f"unknown hypothesis {hid}")
    if new_status not in STATUSES or new_status not in ALLOWED[cur["status"]]:
        raise RegistryError(f"{cur['status']} -> {new_status} is not an allowed transition")
    win = test_window or cur.get("future_test_window")
    if new_status in ("PREREGISTERED", "TESTING", "SUPPORTED", "NOT_SUPPORTED", "INCONCLUSIVE"):
        if not win:
            raise RegistryError(f"{new_status} needs a test window")
        if _windows_overlap(cur["generation_window"], win):
            raise RegistryError("evidence separation violated: the test window overlaps the generation window")
    now = now or datetime.now(timezone.utc)
    row = {**cur, "status": new_status, "transitioned_at": now.isoformat(), "note": note, "future_test_window": win, "result": result, "previous_hash": cur.get("line_hash"),
           "evidence_type": ("CONFIRMATORY" if new_status in ("SUPPORTED", "NOT_SUPPORTED", "INCONCLUSIVE") else ("PREREGISTERED_TEST" if new_status in ("PREREGISTERED", "TESTING") else cur.get("evidence_type")))}
    row.pop("line_hash", None)
    return _append(path, row)


def candidates_from_scorecard(sc: dict, *, season: int, week: int, min_n: int = 30, path_out: str | None = None) -> list:
    """Turn the largest-|effect| HYPOTHESIS_GENERATING slices of a scorecard into candidate hypotheses (NOT registered
    automatically -- written to a candidates file a person promotes)."""
    cands = []
    for cls, b in (sc.get("by_evidence_class") or {}).items():
        if cls != "PROSPECTIVE_FROZEN":
            continue
        considered = b.get("candidate_slices_considered")
        for seg, slices in (b.get("segments") or {}).items():
            for val, m in slices.items():
                o, c = m["outcome"], m["clv"]
                if m["n"] < min_n:
                    continue
                eff = o.get("model_minus_market_brier")
                if eff is None:
                    continue
                cands.append({"id": f"HG-{season}W{week:02d}-{seg}-{val}"[:80].replace(" ", "_"), "market_family": seg, "condition": f"{seg} == {val}",
                              "direction": ("model beats market" if eff < 0 else "market beats model"), "expected_mechanism": "unknown (pattern mined)",
                              "evaluation_metric": "model_minus_market_brier (clustered)", "effect_size": eff, "uncertainty": o.get("model_minus_market_se"),
                              "sample_size": m["n"], "game_count": m["n_games"], "candidate_slices_considered": considered, "mean_clv_mid": c.get("mean_clv_mid"),
                              "generation_window": {"season": season, "week_lo": week, "week_hi": week}, "future_test_window": {"season": season, "week_lo": week + 1, "week_hi": 18},
                              "evidence_type": "HYPOTHESIS_GENERATING", "status": "CANDIDATE_NOT_REGISTERED"})
    cands.sort(key=lambda x: -abs(x["effect_size"] / (x["uncertainty"] or 1.0)) if x["uncertainty"] else 0)
    if path_out:
        os.makedirs(os.path.dirname(path_out) or ".", exist_ok=True)
        json.dump(cands, open(path_out, "w"), indent=1, default=str)
    return cands
