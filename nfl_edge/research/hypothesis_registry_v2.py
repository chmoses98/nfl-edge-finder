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
SYNCHRONIZED = "SYNCHRONIZED"
# Brier differences live in [-1, 1], so a clustered standard error below this is floating-point residue from
# summing identical demeaned values -- not a measurement. Publishing it would imply a z of order 1e16.
SE_FLOOR = 1e-12
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
    automatically -- written to a candidates file a person promotes).

    `min_n` IS AN OUTCOME THRESHOLD, NOT A ROW THRESHOLD.

    It was applied to the slice's total row count, which includes probability-bearing rows that never settled
    and never can -- unresolved player identities, markets with no settlement branch. A slice of forty rows
    carrying four graded outcomes therefore cleared a threshold of thirty and was written out as
    `sample_size: 40, game_count: 40, uncertainty: 0.0`. Every one of those three numbers was false, and the
    last one reads to a human as certainty. For a programme hunting one- to two-point edges over a sharp
    market, that is manufactured evidence.

    So eligibility, the reported sample size, the game count and the uncertainty all come from the rows that
    actually carry the evidence the effect is computed from: `model_minus_market_n` is the paired set behind
    the effect, and `clusters` is the number of independent games those pairs fall into -- not the row count,
    which double-counts every extra contract on the same game. The slice's total row count is still reported,
    as `segment_rows_total`, because coverage is worth knowing; it just cannot qualify anything.

    A candidate also needs a usable uncertainty. Fewer than two clusters yields no standard error at all, and
    a standard error at or below `SE_FLOOR` means every paired difference in the slice was identical -- a
    degenerate estimate, not a precise one. Both are refused rather than published with an implied infinite z.
    """
    cands, refused = [], []
    # SYNCHRONIZED ROWS ONLY. A mined slice is a claim that the model knew something the market did not; if the
    # rows behind it also let the model read LATER information than the quote it is scored against, the slice
    # cannot distinguish the two, and "Doubtful players outperform the market" would mean nothing more than
    # "we saw the designation first". The synchronized bucket is the only admissible basis, and when it is
    # absent nothing is mined -- silence beats an uninterpretable candidate.
    buckets = ((sc.get("by_synchronization") or {}).get("PROSPECTIVE_FROZEN") or {})
    src = {"PROSPECTIVE_FROZEN": buckets[SYNCHRONIZED]} if SYNCHRONIZED in buckets else {}
    for cls, b in src.items():
        if cls != "PROSPECTIVE_FROZEN":
            continue
        considered = b.get("candidate_slices_considered")
        for seg, slices in (b.get("segments") or {}).items():
            for val, m in slices.items():
                o, c = m["outcome"], m["clv"]
                rows_total = m.get("segment_rows_total", m.get("n"))
                # the paired set the effect is actually computed from -- never the slice's row count
                n_eff = o.get("model_minus_market_n") or 0
                if n_eff < min_n:
                    refused.append({"slice": f"{seg}={val}", "reason": "INSUFFICIENT_OUTCOME_EVIDENCE",
                                    "outcome_n": n_eff, "segment_rows_total": rows_total, "min_n": min_n})
                    continue
                eff = o.get("model_minus_market_brier")
                if eff is None:
                    continue
                se, clusters = o.get("model_minus_market_se"), o.get("clusters") or 0
                if clusters < 2:
                    refused.append({"slice": f"{seg}={val}", "reason": "TOO_FEW_INDEPENDENT_GAMES",
                                    "outcome_n": n_eff, "clusters": clusters})
                    continue
                if se is None or se < SE_FLOOR:
                    refused.append({"slice": f"{seg}={val}", "reason": "NO_USABLE_UNCERTAINTY",
                                    "outcome_n": n_eff, "clusters": clusters, "se": se,
                                    "detail": "every paired difference in the slice was identical: a degenerate "
                                              "estimate, not a precise one"})
                    continue
                cands.append({"id": f"HG-{season}W{week:02d}-{seg}-{val}"[:80].replace(" ", "_"), "market_family": seg, "condition": f"{seg} == {val}",
                              "direction": ("model beats market" if eff < 0 else "market beats model"), "expected_mechanism": "unknown (pattern mined)",
                              "evaluation_metric": "model_minus_market_brier (clustered)", "effect_size": eff, "uncertainty": se,
                              "sample_size": n_eff, "game_count": clusters, "candidate_slices_considered": considered, "mean_clv_mid": c.get("mean_clv_mid"),
                              # both denominators travel with the candidate so the gap is never invisible again
                              "segment_rows_total": rows_total, "outcome_n": o.get("n"), "market_n": o.get("market_n"),
                              "model_minus_market_n": n_eff, "settled_game_count": o.get("settled_game_count"),
                              "minimum_sample": min_n, "sample_basis": "model_minus_market_n (paired settled outcomes)",
                              "game_count_basis": "clusters (independent games behind the paired outcomes)",
                              "generation_window": {"season": season, "week_lo": week, "week_hi": week}, "future_test_window": {"season": season, "week_lo": week + 1, "week_hi": 18},
                              "synchronization_basis": SYNCHRONIZED,
                              "evidence_type": "HYPOTHESIS_GENERATING", "status": "CANDIDATE_NOT_REGISTERED"})
    cands.sort(key=lambda x: -abs(x["effect_size"] / x["uncertainty"]))
    if path_out:
        os.makedirs(os.path.dirname(path_out) or ".", exist_ok=True)
        json.dump(cands, open(path_out, "w"), indent=1, default=str)
        # why a slice did NOT become a candidate is evidence too: it is what stops a later reader assuming
        # the mined set was the whole field.
        json.dump(refused, open(os.path.splitext(path_out)[0] + ".refused.json", "w"), indent=1, default=str)
    return cands
