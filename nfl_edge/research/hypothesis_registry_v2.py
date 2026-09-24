"""APPEND-ONLY HYPOTHESIS REGISTRY v2 (Part 23).

`research/hypothesis_registry/v2/hypotheses.jsonl`: one JSON object per line, never rewritten. A hypothesis is
created GENERATED with the evidence window that produced it; every later change is a new line (a transition)
carrying the previous line's hash, so the history is the file. Statuses:

    GENERATED -> PREREGISTERED -> TESTING -> SUPPORTED | NOT_SUPPORTED | INCONCLUSIVE -> RETIRED

The rule that matters: a hypothesis generated from an evidence window can never be SUPPORTED (or NOT_SUPPORTED)
on that same window. `transition()` refuses a test window that overlaps the generation window. Week 1 slices
are HYPOTHESIS_GENERATING; the earliest confirmatory evidence is Week 2 or later.

WS3 HARDENING (localized-signal research). Non-overlap was necessary and not sufficient, so four more rules:

  * ORDER. A test window must come strictly AFTER the generation window (same season: its first week is later
    than the generation window's last; or a later season). A window before the pattern was cut is a hindcast.
  * BINDING. The future test window written at `add()` is the only window a later transition may use, or a
    sub-window of it. Choosing the window at verdict time, after watching the weeks, is refused.
  * PREREGISTRATION. `preregister()` writes the thresholds, the evaluation plan and the time it was made, and
    refuses when that time is not before the first test kickoff.
  * NO AUTOMATIC STATUS. `register_candidates()` only ever writes GENERATED lines; `evaluate_prospective()`
    writes nothing at all and returns a SUGGESTED status that nothing applies. A verdict is a person's
    `transition()` call. Nothing in this module can touch a model weight or a production-eligibility state.

THREE-STAGE GOVERNANCE. Every hypothesis sits in exactly one stage, DERIVED from its status and the evidence it
carries (`governance()`), never stored as a free-standing label someone could set:

  A. DISCOVERY_CANDIDATE -- GENERATED. Auto-mined (or hand-noted) patterns. HYPOTHESIS_GENERATING only: never
     a test, never in the multiplicity family, never given a suggested status. Hundreds of them cost the family
     nothing, because they are not in it.
  B. PREREGISTERED_TEST -- PREREGISTERED / TESTING, and ONLY with a complete preregistration record (frozen
     thresholds + their hash, evaluation plan, test window strictly after generation and inside the registered
     window, made before the first test kickoff). Deliberately selected by a person via `preregister()`.
  C. CONFIRMATORY_RESULT -- SUPPORTED / NOT_SUPPORTED / INCONCLUSIVE reached from Stage B with the future
     evidence recorded on the line (`result`). Still an owner's call; the code only ever suggests.
  RETIRED.

A status that claims Stage B or C without the record that earns it (a legacy bare transition) is reported as a
DISCOVERY_CANDIDATE with its `stage_defects` listed: it is neither in the family nor given a suggestion.
`transition()` now refuses such lines outright -- PREREGISTERED is reachable only through `preregister()`, and a
verdict only with its future evidence.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from datetime import datetime, timezone
from statistics import NormalDist

STATUSES = ("GENERATED", "PREREGISTERED", "TESTING", "SUPPORTED", "NOT_SUPPORTED", "INCONCLUSIVE", "RETIRED")
ALLOWED = {"GENERATED": {"PREREGISTERED", "RETIRED"}, "PREREGISTERED": {"TESTING", "RETIRED"}, "TESTING": {"SUPPORTED", "NOT_SUPPORTED", "INCONCLUSIVE", "RETIRED"},
           "SUPPORTED": {"RETIRED", "TESTING"}, "NOT_SUPPORTED": {"RETIRED", "TESTING"}, "INCONCLUSIVE": {"TESTING", "RETIRED"}, "RETIRED": set()}
REGISTRY_VERSION = "hypotheses-2.0.0"
SYNCHRONIZED = "SYNCHRONIZED"
# Brier differences live in [-1, 1], so a clustered standard error below this is floating-point residue from
# summing identical demeaned values -- not a measurement. Publishing it would imply a z of order 1e16.
SE_FLOOR = 1e-12
DEFAULT_PATH = os.path.join("research", "hypothesis_registry", "v2", "hypotheses.jsonl")

# Kinds of hypothesis the registry knows how to find future evidence for. Anything else is registered and
# reported, but evaluate_prospective() answers INCONCLUSIVE for it rather than guess where its evidence lives.
KIND_SLICE = "LOCALIZED_SLICE"                     # a scorecard_v3 slice (synchronized PROSPECTIVE_FROZEN only)
KIND_GAME_CENTRE = "GAME_CENTRE_DEVIATION"         # a challenger centre's deviation from the snapshot market
SUGGESTION_ONLY = "suggestion only; owner approval required"
UNDER_TEST = ("PREREGISTERED", "TESTING")
VERDICTS = ("SUPPORTED", "NOT_SUPPORTED", "INCONCLUSIVE")

# the three governance stages (+ RETIRED); see the module docstring and governance()
STAGE_DISCOVERY = "DISCOVERY_CANDIDATE"
STAGE_PREREGISTERED = "PREREGISTERED_TEST"
STAGE_CONFIRMATORY = "CONFIRMATORY_RESULT"
STAGE_RETIRED = "RETIRED"
STAGES = (STAGE_DISCOVERY, STAGE_PREREGISTERED, STAGE_CONFIRMATORY, STAGE_RETIRED)
FAMILY_STAGES = (STAGE_PREREGISTERED, STAGE_CONFIRMATORY)          # the only members of the multiplicity family
NOT_PREREGISTERED = ("not preregistered: discovery candidate (hypothesis-generating); future evidence is "
                     "descriptive only and no status is suggested")

# ======================================================================================================
# THE EVIDENCE BAR, WRITTEN DOWN BEFORE THE EVIDENCE
# ======================================================================================================
#
# Written on 2026-09-24, before the first Week-3 kickoff (2026-09-25T00:15Z) and before any settled Week-3
# game existed. The game floor is the production-eligibility WATCH floor (docs/PRODUCTION_ELIGIBILITY.md:
# >= 16 independent games), never lower. These are SUGGESTION thresholds, not verdicts: the three-arm verdict
# floor (arms/registry.py MIN_GAMES_FOR_VERDICT = 64) and the LIMITED / TRUSTED floors (48 / 128 games) still
# govern anything that would be relied on, and nothing here reads or writes them.
#
# What these thresholds can do: label a hypothesis's future evidence and SUGGEST a status. What they can never
# do: change a status (only transition(), called by a person, does that), touch a model weight, a feature, a
# gate, or a production-eligibility state. A suggestion is text in a report.
#
# Changing a value here after 2026-09-24 is a visible edit to a preregistration: the hypotheses preregistered
# against it carry a copy and its hash (`preregistration.thresholds_sha`), and the evaluation reads that frozen
# copy, never the constant as it later became.
PREREGISTERED_THRESHOLDS = {
    "version": "prereg-thresholds-1.0.0",
    "written_at_utc": "2026-09-24T05:00:00+00:00",
    "written_before": "the first Week-3 kickoff, 2026-09-25T00:15:00Z (no Week-3 outcome existed)",
    "independent_unit": "game",
    "generation_window_never_counts": True,
    "no_automatic_promotion": True,
    "confidence_level": 0.95,
    "multiple_comparisons": {
        "method": "BONFERRONI",
        "family": "every registered hypothesis in PREREGISTERED or TESTING status at evaluation time",
        "alpha_family": 0.05,
        "note": ("the per-hypothesis alpha is 0.05 / m, m = hypotheses under test; an interval used for a "
                 "suggestion is widened to that level (at m = 1 it is the ordinary 95% interval). Holm's "
                 "step-down is no less strict at its first rejection; Bonferroni is used because a suggestion "
                 "is read one hypothesis at a time. Secondary horizons, HYBRID (a derived arm) and GENERATED-only "
                 "slices are descriptive and are not members of the family."),
    },
    KIND_SLICE: {
        "metric": "model_minus_market_brier, game-clustered SE, synchronized PROSPECTIVE_FROZEN rows only",
        "min_new_independent_games": 16,          # = WATCH floor; below it the only suggestion is INCONCLUSIVE
        "min_paired_outcomes": 30,                # secondary: paired settled rows behind the effect
        "supported_suggestion": ("the multiplicity-adjusted CI of model-minus-market Brier excludes 0 on the "
                                 "generation effect's side AND the future effect has the generation effect's "
                                 "sign AND, for a model-beats-market hypothesis, mean CLV (mid, toward model) "
                                 ">= 0 (missing CLV -> INCONCLUSIVE)"),
        "not_supported_suggestion": ("the CI excludes 0 on the opposite side, OR the sign is reversed with at "
                                     "least min_new_independent_games new games"),
        "trend": {"persisting_min_ratio": 0.5,
                  "labels": {"PERSISTING": "same sign, |future| >= 0.5 x |generation|",
                             "WEAKENING": "same sign, |future| < 0.5 x |generation| (or exactly 0)",
                             "REVERSING": "opposite sign",
                             "INCONCLUSIVE": "fewer than min_new_independent_games new games, or no estimate"}},
    },
    KIND_GAME_CENTRE: {
        "unit": "one game per horizon view (a game counts once per horizon, never once per snapshot or contract)",
        "arm": "DATA_ONLY (primary). HYBRID_30_DATA is reported as derived: 0.3 x DATA_ONLY deviation, not independent",
        "meaningful_deviation_points": 1.0,       # |arm centre - snapshot market centre| >= 1.0 point
        "bands_reported": ["<=1", "1-2", "2-3", "3-5", ">5"],
        "denominator": ("toward + away only; unchanged (the market did not move) and no_close (no valid closing "
                        "centre) are shown separately and are never in the denominator"),
        "primary_horizon": "latest_pregame",
        "secondary_horizons": ["T-24h", "T-6h", "T-90m", "T-30m"],
        "min_directional_observations": 20,       # toward + away at the primary horizon, future window only
        "min_new_independent_games": 16,          # the WATCH floor applies here too
        "supported_suggestion": "multiplicity-adjusted Wilson lower bound of the toward rate > 0.5",
        "not_supported_suggestion": ("multiplicity-adjusted Wilson upper bound < 0.5, OR the toward rate is "
                                     "below 0.5 with at least min_directional_observations"),
        "trend": {"persisting_min_ratio": 0.5,
                  "effect": "toward_rate - 0.5, compared with the generation window's toward_rate - 0.5"},
    },
}


class RegistryError(ValueError):
    pass


def _line_hash(obj: dict) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()[:16]


def _finite(x) -> bool:
    """A number inference can actually be done with: not None, not NaN, not +/-inf.

    Checked explicitly because comparisons do not do it for you -- every ordering comparison against NaN is
    False, so `nan < SE_FLOOR` does not reject NaN and `nan > 0` does not either.
    """
    try:
        return x is not None and math.isfinite(float(x))
    except (TypeError, ValueError):
        return False


def _windows_overlap(a: dict, b: dict) -> bool:
    """Windows are {season, week_lo, week_hi} (inclusive). Different seasons never overlap."""
    if not a or not b or a.get("season") != b.get("season"):
        return False
    return not (int(a["week_hi"]) < int(b["week_lo"]) or int(b["week_hi"]) < int(a["week_lo"]))


def _window_after(generation: dict, test: dict) -> bool:
    """True only if EVERY week of `test` comes strictly after EVERY week of `generation`.

    Non-overlap was the old rule and it is not enough: a Week-5 pattern "tested" on Weeks 1-4 overlaps nothing
    and is still a hindcast -- the evidence already existed when the pattern was cut, so the test could have been
    chosen to agree with it. A prospective test must be LATER: a later season, or the same season starting after
    the generation window's last week. A window in an earlier season is never after.
    """
    if not generation or not test:
        return False
    gs, ts = int(generation["season"]), int(test["season"])
    if ts != gs:
        return ts > gs
    return int(test["week_lo"]) > int(generation["week_hi"])


def _window_contained(inner: dict, outer: dict) -> bool:
    """`inner` lies wholly inside `outer` (same season, inclusive bounds)."""
    if not inner or not outer or inner.get("season") != outer.get("season"):
        return False
    return int(outer["week_lo"]) <= int(inner["week_lo"]) <= int(inner["week_hi"]) <= int(outer["week_hi"])


def registered_future_window(row: dict) -> dict | None:
    """The future test window fixed when the hypothesis was ADDED. Binding for every later transition.

    Rows written before the window became binding carried the transition's window in `future_test_window`
    (transition() overwrote it); `registered_future_test_window` is the add-time copy and wins when present.
    """
    return row.get("registered_future_test_window") or row.get("future_test_window")


def _parse_ts(x) -> datetime:
    if isinstance(x, datetime):
        return x if x.tzinfo else x.replace(tzinfo=timezone.utc)
    t = datetime.fromisoformat(str(x).replace("Z", "+00:00"))
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


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


def _check_future_window(generation_window: dict, window: dict, *, what: str) -> None:
    if _windows_overlap(generation_window, window):
        raise RegistryError(f"evidence separation violated: the {what} overlaps the generation window; "
                            "evidence that generated a pattern can never confirm it")
    if not _window_after(generation_window, window):
        raise RegistryError(f"the {what} {window} does not come strictly AFTER the generation window "
                            f"{generation_window}; an earlier window is a hindcast, not a prospective test")


def add(*, hid: str, market_family: str, condition: str, direction: str, expected_mechanism: str, evaluation_metric: str, minimum_sample: int,
        generation_window: dict, future_test_window: dict | None, generated_by: str, effect_size: float | None = None, uncertainty: float | None = None,
        sample_size: int | None = None, game_count: int | None = None, candidate_slices_considered: int | None = None,
        hypothesis_kind: str | None = None, locator: dict | None = None, generation_evidence: dict | None = None,
        path: str = DEFAULT_PATH, now=None) -> dict:
    """Register a hypothesis as GENERATED. Refuses a future window that is not strictly after the generation window.

    The future test window given here is BINDING: it is copied to `registered_future_test_window` and every
    later PREREGISTERED / TESTING / verdict transition must use a window contained in it. Choosing the test
    window at transition time -- after the weeks in it have been watched -- is exactly the freedom a
    prospective test exists to remove.

    `hypothesis_kind` / `locator` say where future evidence for the hypothesis is read (a scorecard slice, a
    game-centre deviation view); `generation_evidence` carries the numbers that produced it, verbatim. All three
    are optional so older callers keep working.
    """
    if hid in current(path):
        raise RegistryError(f"{hid} already exists; transitions are new lines, not re-adds")
    if future_test_window:
        _check_future_window(generation_window, future_test_window, what="future test window")
    now = now or datetime.now(timezone.utc)
    row = {"registry_version": REGISTRY_VERSION, "id": hid, "created_at": _parse_ts(now).isoformat(), "status": "GENERATED", "evidence_type": "HYPOTHESIS_GENERATING",
           "market_family": market_family, "condition": condition, "direction": direction, "expected_mechanism": expected_mechanism,
           "evaluation_metric": evaluation_metric, "minimum_sample": minimum_sample, "generation_window": generation_window,
           "future_test_window": future_test_window, "registered_future_test_window": future_test_window,
           "generated_by": generated_by, "effect_size": effect_size, "uncertainty": uncertainty,
           "sample_size": sample_size, "game_count": game_count, "candidate_slices_considered": candidate_slices_considered, "previous_hash": None}
    if hypothesis_kind is not None:
        row["hypothesis_kind"] = hypothesis_kind
    if locator is not None:
        row["locator"] = locator
    if generation_evidence is not None:
        row["generation_evidence"] = generation_evidence
    return _append(path, row)


def _binding_window_check(cur: dict, win: dict, new_status: str) -> None:
    """A transition's test window: after the generation window AND inside the add-time future window (and inside
    the preregistered test window once there is one)."""
    _check_future_window(cur["generation_window"], win, what=f"{new_status} test window")
    registered = registered_future_window(cur)
    if registered and not _window_contained(win, registered):
        raise RegistryError(f"the {new_status} test window {win} is not contained in the future test window "
                            f"{registered} fixed when the hypothesis was registered; that window is binding")
    # once preregistered (by preregister() or a bare transition), the window chosen then binds every later step
    pre = (cur.get("preregistration") or {}).get("test_window") or (cur.get("test_window") if cur.get("status") != "GENERATED" else None)
    if pre and new_status != "PREREGISTERED" and not _window_contained(win, pre):
        raise RegistryError(f"the {new_status} test window {win} is not contained in the preregistered test "
                            f"window {pre}")


def transition(hid: str, new_status: str, *, note: str = "", test_window: dict | None = None, result: dict | None = None,
               extra: dict | None = None, path: str = DEFAULT_PATH, now=None) -> dict:
    """Append a status change. Nothing here is ever called automatically: every verdict is an owner's act.

    The window used is, in order: the one passed, the one already chosen (preregistration), the registered
    future window. It must come strictly after the generation window and sit inside the registered window.
    The registered window itself is never rewritten -- the window a transition used is recorded as
    `test_window` beside it.
    """
    cur = current(path).get(hid)
    if cur is None:
        raise RegistryError(f"unknown hypothesis {hid}")
    if new_status not in STATUSES or new_status not in ALLOWED[cur["status"]]:
        raise RegistryError(f"{cur['status']} -> {new_status} is not an allowed transition")
    # STAGE B IS EARNED, NOT DECLARED. A bare GENERATED -> PREREGISTERED line would carry no frozen thresholds,
    # no evaluation plan and no preregistration time -- a "test" whose bar could still be set after the games.
    if new_status == "PREREGISTERED" and not ((extra or {}).get("preregistration") or {}).get("thresholds"):
        raise RegistryError("PREREGISTERED is reachable only through preregister(): the thresholds, the evaluation "
                            "plan and the preregistration time must be frozen on the same line")
    # STAGE C IS A RESULT: a verdict line must carry the future evidence it was reached on.
    if new_status in VERDICTS and not result:
        raise RegistryError(f"{new_status} needs the future evidence it rests on (`result`); a verdict with no "
                            "recorded evidence is not a confirmatory result")
    win = test_window or cur.get("test_window") or registered_future_window(cur)
    if new_status in ("PREREGISTERED", "TESTING", "SUPPORTED", "NOT_SUPPORTED", "INCONCLUSIVE"):
        if not win:
            raise RegistryError(f"{new_status} needs a test window")
        _binding_window_check(cur, win, new_status)
    now = now or datetime.now(timezone.utc)
    row = {**cur, "status": new_status, "transitioned_at": _parse_ts(now).isoformat(), "note": note,
           "registered_future_test_window": registered_future_window(cur), "test_window": win,
           "result": result, "previous_hash": cur.get("line_hash"),
           "evidence_type": ("CONFIRMATORY" if new_status in ("SUPPORTED", "NOT_SUPPORTED", "INCONCLUSIVE") else ("PREREGISTERED_TEST" if new_status in ("PREREGISTERED", "TESTING") else cur.get("evidence_type")))}
    if extra:
        row.update(extra)
    row.pop("line_hash", None)
    return _append(path, row)


def thresholds_sha(thresholds: dict) -> str:
    return hashlib.sha256(json.dumps(thresholds, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()[:16]


def preregister(hid: str, *, test_window: dict, thresholds: dict, evaluation_plan: str | dict, preregistered_at=None,
                first_test_kickoff_utc=None, note: str = "", path: str = DEFAULT_PATH) -> dict:
    """GENERATED -> PREREGISTERED, with the record a preregistration needs to mean anything.

    What is written, and why each part is there:

      * `test_window` -- strictly after the generation window and inside the window fixed at registration;
      * `thresholds` (and their hash) -- the evidence bar, written down BEFORE any of the test games exist, so a
        verdict cannot be argued into place afterwards;
      * `evaluation_plan` -- the unit, the metric, the horizons, what is primary and what is only descriptive;
      * `preregistered_at` and `first_test_kickoff_utc` -- a preregistration made after the first test game
        kicked off could have been informed by it. When the kickoff is given, `preregistered_at` must be
        strictly earlier or the preregistration is refused.

    It does not move the hypothesis to TESTING and it does not evaluate anything.
    """
    cur = current(path).get(hid)
    if cur is None:
        raise RegistryError(f"unknown hypothesis {hid}")
    if cur["status"] != "GENERATED":
        raise RegistryError(f"only a GENERATED hypothesis can be preregistered; {hid} is {cur['status']}")
    if not test_window:
        raise RegistryError("a preregistration needs a test window")
    if not thresholds:
        raise RegistryError("a preregistration needs its evidence thresholds, written before the test games")
    at = _parse_ts(preregistered_at or datetime.now(timezone.utc))
    kick = None
    if first_test_kickoff_utc is not None:
        kick = _parse_ts(first_test_kickoff_utc)
        if at >= kick:
            raise RegistryError(f"preregistered_at {at.isoformat()} is not before the first test kickoff "
                                f"{kick.isoformat()}; a preregistration made after the test began is not one")
    record = {"test_window": test_window, "thresholds": thresholds, "thresholds_sha": thresholds_sha(thresholds),
              "evaluation_plan": evaluation_plan, "preregistered_at": at.isoformat(),
              "first_test_kickoff_utc": (kick.isoformat() if kick else None)}
    # the window check runs inside transition(); the preregistration record travels on the same line
    return transition(hid, "PREREGISTERED", note=note or "preregistered", test_window=test_window,
                      extra={"preregistration": record}, path=path, now=at)


# ======================================================================================================
# three-stage governance: the stage is DERIVED from status + evidence, never set
# ======================================================================================================

def preregistration_defects(row: dict) -> list:
    """What, if anything, is missing from a row's preregistration record. [] = a complete Stage-B record."""
    pre = row.get("preregistration") or {}
    if not pre:
        return ["NO_PREREGISTRATION_RECORD"]
    out = []
    th = pre.get("thresholds")
    if not th:
        out.append("NO_FROZEN_THRESHOLDS")
    elif pre.get("thresholds_sha") != thresholds_sha(th):
        out.append("THRESHOLDS_HASH_MISMATCH")
    if not pre.get("evaluation_plan"):
        out.append("NO_EVALUATION_PLAN")
    at = pre.get("preregistered_at")
    if not at:
        out.append("NO_PREREGISTRATION_TIME")
    tw, gen, reg = pre.get("test_window"), row.get("generation_window"), registered_future_window(row)
    if not tw:
        out.append("NO_TEST_WINDOW")
    elif not gen or _windows_overlap(gen, tw) or not _window_after(gen, tw):
        out.append("TEST_WINDOW_NOT_STRICTLY_AFTER_GENERATION")
    elif reg and not _window_contained(tw, reg):
        out.append("TEST_WINDOW_OUTSIDE_REGISTERED_WINDOW")
    kick = pre.get("first_test_kickoff_utc")
    if at and kick:
        try:
            if _parse_ts(at) >= _parse_ts(kick):
                out.append("PREREGISTERED_AT_OR_AFTER_FIRST_TEST_KICKOFF")
        except (TypeError, ValueError):
            out.append("PREREGISTRATION_TIME_UNPARSEABLE")
    return out


def governance(row: dict) -> dict:
    """{stage, defects, in_family}. The stage follows from status AND the record behind it:

        GENERATED                                   -> DISCOVERY_CANDIDATE
        PREREGISTERED / TESTING + complete record   -> PREREGISTERED_TEST
        verdict + complete record + result on line  -> CONFIRMATORY_RESULT
        RETIRED                                     -> RETIRED
        anything claiming B or C without its record -> DISCOVERY_CANDIDATE, defects listed
    """
    status = (row or {}).get("status")
    if status == "RETIRED":
        return {"stage": STAGE_RETIRED, "defects": [], "in_family": False}
    if status in UNDER_TEST or status in VERDICTS:
        d = preregistration_defects(row)
        if status in VERDICTS:
            if not row.get("result"):
                d.append("VERDICT_WITHOUT_RECORDED_FUTURE_EVIDENCE")
            tw, pre_tw = row.get("test_window"), (row.get("preregistration") or {}).get("test_window")
            if tw and pre_tw and not _window_contained(tw, pre_tw):
                d.append("VERDICT_WINDOW_OUTSIDE_PREREGISTERED_WINDOW")
        if d:
            return {"stage": STAGE_DISCOVERY, "defects": d, "in_family": False}
        st = STAGE_PREREGISTERED if status in UNDER_TEST else STAGE_CONFIRMATORY
        return {"stage": st, "defects": [], "in_family": True}
    if status == "GENERATED":
        return {"stage": STAGE_DISCOVERY, "defects": [], "in_family": False}
    return {"stage": STAGE_DISCOVERY, "defects": [f"UNKNOWN_STATUS_{status}"], "in_family": False}


def stage(row: dict) -> str:
    return governance(row)["stage"]


def multiplicity_family(hypotheses: dict) -> list:
    """Ids in the Bonferroni family: Stage B and Stage C members only. Discovery candidates never enter it --
    however many were mined -- and neither does a status that lacks the preregistration record behind it.

    The frozen prereg-thresholds-1.0.0 text names the family "every hypothesis in PREREGISTERED or TESTING
    status"; counting Stage C members as well can only make m larger (never smaller), so it is at least as strict
    as what was preregistered, and identical while no Stage-C result exists.
    """
    return sorted(hid for hid, h in (hypotheses or {}).items() if governance(h)["in_family"])


def audit_registry(rows: list) -> dict:
    """What an append-only registry file actually holds, line by line. Reads; writes nothing.

    Counts lines and ids by status, evidence type and derived stage; verifies every line's hash and that each
    transition chains to the id's previous line; lists every id whose latest status claims Stage B or C without
    the record that earns it (`improper`).
    """
    from collections import Counter
    latest, prev, breaks = {}, {}, []
    for i, r in enumerate(rows or []):
        want = {k: v for k, v in r.items() if k != "line_hash"}
        if _line_hash(want) != r.get("line_hash"):
            breaks.append({"line": i + 1, "id": r.get("id"), "reason": "LINE_HASH_MISMATCH"})
        if r.get("previous_hash") != prev.get(r.get("id")):
            breaks.append({"line": i + 1, "id": r.get("id"), "reason": "PREVIOUS_HASH_DOES_NOT_CHAIN"})
        prev[r.get("id")] = r.get("line_hash")
        latest[r.get("id")] = r
    gov = {hid: governance(r) for hid, r in latest.items()}
    return {"lines": len(rows or []), "ids": len(latest),
            "lines_by_status": dict(Counter(r.get("status") for r in rows or [])),
            "ids_by_status": dict(Counter(r.get("status") for r in latest.values())),
            "ids_by_evidence_type": dict(Counter(r.get("evidence_type") for r in latest.values())),
            "ids_by_stage": dict(Counter(g["stage"] for g in gov.values())),
            "ids_with_transitions": sorted(hid for hid, r in latest.items() if r.get("previous_hash")),
            "multiplicity_family": sorted(hid for hid, g in gov.items() if g["in_family"]),
            "improper": [{"id": hid, "status": latest[hid].get("status"), "defects": g["defects"]}
                         for hid, g in sorted(gov.items()) if g["defects"]],
            "hash_chain_ok": not breaks, "chain_breaks": breaks}


def _slice_identity(seg: str, val: str, m: dict) -> dict:
    """Arm / family / horizon / version of a slice: parsed from a crossed segment, else read off the rows.

    A slice that pools rows of more than one model arm answers no question about any model -- "ctx_injury_state
    == LISTED outperforms the market" averaged over three arms describes none of them -- so `model_arms` travels with
    every slice and the miner refuses a pooled one (the crossed segments are where arm-specific slices live).
    """
    ident = {"model_arm": None, "family_group": None, "horizon_label": None}
    keys = seg.split("*")
    vals = val.split("|") if len(keys) > 1 else [val]
    if len(keys) == len(vals):
        for k, v in zip(keys, vals):
            if k in ident:
                ident[k] = v
    arms = m.get("model_arms")
    if ident["model_arm"] is None and arms and len(arms) == 1:
        ident["model_arm"] = arms[0]
    return {**ident, "model_arms": arms, "model_versions": m.get("model_versions")}


def candidates_from_scorecard(sc: dict, *, season: int, week: int, min_n: int = 30, min_games: int = 16,
                              path_out: str | None = None) -> list:
    """Turn the largest-|effect| HYPOTHESIS_GENERATING slices of a scorecard into candidate hypotheses.

    Candidates are written to a candidates file; `register_candidates()` adds them to the registry as GENERATED
    and nothing ever promotes them further automatically.

    THE PRIMARY GATE IS INDEPENDENT GAMES, NOT ROWS (WS3).

    docs/PRODUCTION_ELIGIBILITY.md: "row counts never qualify". A hundred contracts on four games are four
    observations of whatever happened in those games -- one blowout moves every total, every spread and every
    receiving line at once -- so the gate is `min_games` independent games behind the paired outcomes (default
    16, the WATCH floor), and the paired-outcome count `min_n` is kept as a SECONDARY gate beneath it.

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

    EVERY STATISTIC USED FOR INFERENCE MUST BE FINITE, and that is checked explicitly rather than left to a
    threshold comparison. `float('nan') < SE_FLOOR` is False, so a non-finite standard error sailed through
    the floor check and published a candidate whose effect and uncertainty were both `nan` -- junk that reads
    to a human as a result. NaN and +/-inf are refused on both the effect and its standard error.

    WHAT A CANDIDATE CARRIES (WS3): generation and future windows; independent games, paired settled rows and
    unique contracts; the effect with its game-clustered SE and 95% interval; mean CLV, positive-CLV rate and the
    market-toward-model rate; executable fee-adjusted P&L or an explicit UNAVAILABLE; the model arm, version,
    family and horizon; the synchronization basis; and `candidate_slices_considered`, the multiple-comparison
    denominator the candidate was selected from.
    """
    cands, refused = [], []
    # SYNCHRONIZED ROWS ONLY. A mined slice is a claim that the model knew something the market did not; if the
    # rows behind it also let the model read LATER information than the quote it is scored against, the slice
    # cannot distinguish the two, and "Doubtful players outperform the market" would mean nothing more than
    # "we saw the designation first". The synchronized bucket is the only admissible basis, and when it is
    # absent nothing is mined -- silence beats an uninterpretable candidate. The asynchronous buckets are never
    # read here, so they can never be pooled into a candidate.
    buckets = ((sc.get("by_synchronization") or {}).get("PROSPECTIVE_FROZEN") or {})
    src = {"PROSPECTIVE_FROZEN": buckets[SYNCHRONIZED]} if SYNCHRONIZED in buckets else {}
    for cls, b in src.items():
        if cls != "PROSPECTIVE_FROZEN":
            continue
        considered = b.get("candidate_slices_considered")
        for seg, slices in (b.get("segments") or {}).items():
            for val, m in slices.items():
                o, c = m["outcome"], m["clv"]
                e = m.get("executable") or {}
                rows_total = m.get("segment_rows_total", m.get("n"))
                # the paired set the effect is actually computed from -- never the slice's row count
                n_eff = o.get("model_minus_market_n") or 0
                clusters = o.get("clusters") or 0
                ident = _slice_identity(seg, val, m)
                if ident["model_arms"] and len(ident["model_arms"]) > 1:
                    refused.append({"slice": f"{seg}={val}", "reason": "POOLS_MODEL_ARMS",
                                    "model_arms": ident["model_arms"], "outcome_n": n_eff, "clusters": clusters,
                                    "detail": "a slice averaged over several model arms describes none of them; "
                                              "the model_arm*family_group segments carry the arm-specific slices"})
                    continue
                if clusters < min_games:
                    refused.append({"slice": f"{seg}={val}", "reason": "INSUFFICIENT_INDEPENDENT_GAMES",
                                    "outcome_n": n_eff, "clusters": clusters, "min_games": min_games,
                                    "segment_rows_total": rows_total})
                    continue
                if n_eff < min_n:
                    refused.append({"slice": f"{seg}={val}", "reason": "INSUFFICIENT_OUTCOME_EVIDENCE",
                                    "outcome_n": n_eff, "segment_rows_total": rows_total, "min_n": min_n})
                    continue
                eff = o.get("model_minus_market_brier")
                if not _finite(eff):
                    refused.append({"slice": f"{seg}={val}", "reason": "EFFECT_NOT_FINITE",
                                    "outcome_n": n_eff, "effect": repr(eff),
                                    "detail": "the effect estimate is missing or non-finite; nothing can be "
                                              "inferred from it"})
                    continue
                se = o.get("model_minus_market_se")
                if clusters < 2:
                    refused.append({"slice": f"{seg}={val}", "reason": "TOO_FEW_INDEPENDENT_GAMES",
                                    "outcome_n": n_eff, "clusters": clusters})
                    continue
                if not _finite(se):
                    refused.append({"slice": f"{seg}={val}", "reason": "UNCERTAINTY_NOT_FINITE",
                                    "outcome_n": n_eff, "clusters": clusters, "se": repr(se),
                                    "detail": "the standard error is missing or non-finite; a threshold "
                                              "comparison alone would not have rejected it"})
                    continue
                if se < SE_FLOOR:
                    refused.append({"slice": f"{seg}={val}", "reason": "NO_USABLE_UNCERTAINTY",
                                    "outcome_n": n_eff, "clusters": clusters, "se": se,
                                    "detail": "every paired difference in the slice was identical: a degenerate "
                                              "estimate, not a precise one"})
                    continue
                pnl_net = e.get("pnl_net_per_contract")
                pnl = ({"state": "AVAILABLE", "net_per_contract": pnl_net, "gross_per_contract": e.get("pnl_gross_per_contract"),
                        "n_fee_known": e.get("n_fee_known"), "n_taken": e.get("n_taken"),
                        "note": e.get("note")}
                       if _finite(pnl_net) and (e.get("n_fee_known") or 0) > 0 else
                       {"state": "UNAVAILABLE", "reason": ("no row carried a fee-adjusted executable P&L"
                                                           if e else "the slice carries no executable block")})
                cands.append({"id": f"HG-{season}W{week:02d}-{seg}-{val}"[:120].replace(" ", "_"), "market_family": seg, "condition": f"{seg} == {val}",
                              "segment": seg, "segment_value": val, "hypothesis_kind": KIND_SLICE,
                              "direction": ("model beats market" if eff < 0 else "market beats model"), "expected_mechanism": "unknown (pattern mined)",
                              "evaluation_metric": "model_minus_market_brier (clustered)", "effect_size": eff, "uncertainty": se,
                              "ci95": [eff - 1.96 * se, eff + 1.96 * se], "z": eff / se,
                              "sample_size": n_eff, "game_count": clusters, "candidate_slices_considered": considered,
                              "independent_games": clusters, "paired_settled_rows": n_eff,
                              "unique_contracts": m.get("n_unique_contracts"),
                              "mean_clv_mid": c.get("mean_clv_mid"), "se_clv_mid_clustered": c.get("se_clv_mid_clustered"),
                              "positive_clv_rate": c.get("positive_clv_rate"), "market_toward_model_rate": c.get("movement_toward_rate"),
                              "n_clv_ok": c.get("n_clv_ok"), "executable_pnl": pnl,
                              "model_arm": ident["model_arm"], "model_arms": ident["model_arms"], "model_versions": ident["model_versions"],
                              "family_group": ident["family_group"], "horizon_label": ident["horizon_label"],
                              # both denominators travel with the candidate so the gap is never invisible again
                              "segment_rows_total": rows_total, "outcome_n": o.get("n"), "market_n": o.get("market_n"),
                              "model_minus_market_n": n_eff, "settled_game_count": o.get("settled_game_count"),
                              "minimum_sample": min_n, "minimum_games": min_games,
                              "sample_basis": "model_minus_market_n (paired settled outcomes)",
                              "game_count_basis": "clusters (independent games behind the paired outcomes)",
                              "generation_window": {"season": season, "week_lo": week, "week_hi": week}, "future_test_window": {"season": season, "week_lo": week + 1, "week_hi": 18},
                              "synchronization_basis": SYNCHRONIZED, "evidence_class": "PROSPECTIVE_FROZEN",
                              "evidence_type": "HYPOTHESIS_GENERATING", "status": "CANDIDATE_NOT_REGISTERED",
                              "stage": STAGE_DISCOVERY})
    cands.sort(key=lambda x: -abs(x["effect_size"] / x["uncertainty"]))
    if path_out:
        os.makedirs(os.path.dirname(path_out) or ".", exist_ok=True)
        json.dump(cands, open(path_out, "w"), indent=1, default=str)
        # why a slice did NOT become a candidate is evidence too: it is what stops a later reader assuming
        # the mined set was the whole field.
        json.dump(refused, open(os.path.splitext(path_out)[0] + ".refused.json", "w"), indent=1, default=str)
    return cands


# ======================================================================================================
# automatic registration: GENERATED only, never anything else
# ======================================================================================================

def seed_registry(local_path: str, published_path: str | None) -> str:
    """Start the job's local registry from the published copy, so an append extends the history, never forks it.

    The automatic registry lives on `market-data` (data/shadow/v2/hypotheses/hypotheses.jsonl) and is published
    by copying the local staging tree over it. A job that appended to an EMPTY local file would therefore
    publish a registry holding only this week's lines -- every earlier line silently gone. So: if the local file
    does not exist yet and a published one does, copy it first. An existing local file is never overwritten
    (a re-run inside one job keeps its own appends).
    """
    if os.path.exists(local_path):
        return "LOCAL_EXISTS"
    if published_path and os.path.exists(published_path):
        os.makedirs(os.path.dirname(local_path) or ".", exist_ok=True)
        with open(published_path, "rb") as src, open(local_path, "wb") as dst:
            dst.write(src.read())
        return "SEEDED_FROM_PUBLISHED"
    return "NEW_REGISTRY"


def register_candidates(candidates: list, *, path: str = DEFAULT_PATH, now=None) -> dict:
    """Add mined candidates to the registry as GENERATED. Idempotent: an id already registered is skipped.

    This is the ONLY automatic write the registry receives, and it can only ever write a GENERATED line: it
    calls `add()` and never `transition()` or `preregister()`. A candidate's statistics are stored verbatim as
    its `generation_evidence`, so the numbers that produced it cannot later be restated.

    A candidate that `add()` refuses (a malformed or backward window) is reported under `refused`, never raised:
    one bad candidate must not cost the week its other registrations.

    Note what re-running a week does: the id carries the generation week, so a later, more fully settled run of
    the same week is SKIPPED, and the generation evidence stays as first registered. That is deliberate -- a
    registry line is never rewritten -- and harmless for inference, because the whole generation week is
    excluded from every future test whichever run registered it.
    """
    existing = current(path)
    out = {"added": [], "skipped_existing": [], "refused": []}
    for c in candidates or []:
        hid = c.get("id")
        if not hid:
            out["refused"].append({"id": None, "reason": "candidate has no id"})
            continue
        if hid in existing:
            out["skipped_existing"].append(hid)
            continue
        evidence = {k: c.get(k) for k in (
            "effect_size", "uncertainty", "ci95", "z", "independent_games", "paired_settled_rows", "unique_contracts",
            "mean_clv_mid", "se_clv_mid_clustered", "positive_clv_rate", "market_toward_model_rate", "n_clv_ok",
            "executable_pnl", "model_arm", "model_arms", "model_versions", "family_group", "horizon_label",
            "segment_rows_total", "outcome_n", "market_n", "settled_game_count", "synchronization_basis",
            "evidence_class", "candidate_slices_considered", "minimum_games", "minimum_sample")}
        try:
            row = add(hid=hid, market_family=c.get("market_family") or c.get("segment") or "?", condition=c.get("condition") or "?",
                      direction=c.get("direction") or "?", expected_mechanism=c.get("expected_mechanism") or "unknown (pattern mined)",
                      evaluation_metric=c.get("evaluation_metric") or "model_minus_market_brier (clustered)",
                      minimum_sample=int(c.get("minimum_sample") or 0), generation_window=c["generation_window"],
                      future_test_window=c.get("future_test_window"), generated_by="candidates_from_scorecard (automatic)",
                      effect_size=c.get("effect_size"), uncertainty=c.get("uncertainty"), sample_size=c.get("sample_size"),
                      game_count=c.get("game_count"), candidate_slices_considered=c.get("candidate_slices_considered"),
                      hypothesis_kind=c.get("hypothesis_kind") or KIND_SLICE,
                      locator={"kind": c.get("hypothesis_kind") or KIND_SLICE, "segment": c.get("segment"),
                               "value": c.get("segment_value"), "evidence_class": "PROSPECTIVE_FROZEN",
                               "synchronization": SYNCHRONIZED},
                      generation_evidence=evidence, path=path, now=now)
        except (RegistryError, KeyError, TypeError, ValueError) as exc:
            out["refused"].append({"id": hid, "reason": f"{type(exc).__name__}: {exc}"})
            continue
        existing[hid] = row
        out["added"].append(hid)
    return out


# ======================================================================================================
# prospective evaluation: PURE, writes nothing, applies nothing
# ======================================================================================================

def wilson(k: int, n: int, z: float = 1.959963984540054):
    """Wilson score interval for k successes of n. None when n == 0."""
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [max(0.0, centre - half), min(1.0, centre + half)]


def multiplicity(n_under_test: int, alpha_family: float = 0.05) -> dict:
    m = max(int(n_under_test or 1), 1)
    a = alpha_family / m
    return {"method": "BONFERRONI", "m": m, "alpha_family": alpha_family, "alpha_adjusted": a,
            "z_adjusted": NormalDist().inv_cdf(1 - a / 2), "z_95": NormalDist().inv_cdf(0.975)}


def _in_window(season, week, window) -> bool:
    return (window is not None and season is not None and week is not None and int(season) == int(window["season"])
            and int(window["week_lo"]) <= int(week) <= int(window["week_hi"]))


def _split_weeks(hypothesis: dict, by_week: list):
    """Keep only weeks inside the test window AND strictly after the generation window; say why others went."""
    gen = hypothesis.get("generation_window")
    test = (hypothesis.get("preregistration") or {}).get("test_window") or hypothesis.get("test_window") \
        if hypothesis.get("status") in UNDER_TEST + ("SUPPORTED", "NOT_SUPPORTED", "INCONCLUSIVE") else None
    window = test or registered_future_window(hypothesis)
    keep, excluded = [], []
    for w in by_week or []:
        s, wk = w.get("season"), w.get("week")
        one = {"season": s, "week_lo": wk, "week_hi": wk} if s is not None and wk is not None else None
        if one is None:
            excluded.append({"season": s, "week": wk, "reason": "WEEK_UNKNOWN"})
        elif gen and _windows_overlap(gen, one):
            excluded.append({"season": s, "week": wk, "reason": "GENERATION_WINDOW (can never count)"})
        elif gen and not _window_after(gen, one):
            excluded.append({"season": s, "week": wk, "reason": "BEFORE_GENERATION (hindcast)"})
        elif not _in_window(s, wk, window):
            excluded.append({"season": s, "week": wk, "reason": "OUTSIDE_TEST_WINDOW"})
        else:
            keep.append(w)
    return keep, excluded, window


def _trend(gen_effect, fut_effect, enough: bool, ratio: float) -> tuple:
    """(trend, direction_so_far). `trend` is conservative (INCONCLUSIVE below the game floor);
    `direction_so_far` is the same comparison stated descriptively whatever the sample."""
    if not _finite(gen_effect) or not _finite(fut_effect) or gen_effect == 0:
        return "INCONCLUSIVE", "NO_ESTIMATE"
    if (fut_effect > 0) != (gen_effect > 0) and fut_effect != 0:
        d = "REVERSING"
    elif abs(fut_effect) >= ratio * abs(gen_effect):
        d = "PERSISTING"
    else:
        d = "WEAKENING"
    return (d if enough else "INCONCLUSIVE"), d


def _combine_slice_weeks(weeks: list) -> dict:
    """Pool per-week slice summaries. Weeks hold disjoint games, so the clustered variances add:
    mean = sum(n_w mean_w) / N, Var = sum((n_w / N)^2 se_w^2). CLV and P&L are pooled the same way by their
    own counts. Exact up to each week's small-sample factor; stated in the output."""
    N = sum(int(w.get("paired_n") or 0) for w in weeks if _finite(w.get("effect")))
    games = sum(int(w.get("games") or 0) for w in weeks)
    out = {"new_independent_games": games, "paired_settled_rows": N, "weeks": [(w.get("season"), w.get("week")) for w in weeks],
           "effect": None, "se": None, "pooling": "per-week game-clustered summaries; weeks hold disjoint games, variances add"}
    if N:
        eff = sum(int(w["paired_n"]) * float(w["effect"]) for w in weeks if _finite(w.get("effect")) and w.get("paired_n"))
        out["effect"] = eff / N
        ses = [(int(w["paired_n"]) / N, w.get("se")) for w in weeks if _finite(w.get("effect")) and w.get("paired_n")]
        if all(_finite(se) for _, se in ses):
            out["se"] = math.sqrt(sum((f * float(se)) ** 2 for f, se in ses))

    def pooled(key, nkey):
        xs = [(int(w.get(nkey) or 0), w.get(key)) for w in weeks if _finite(w.get(key)) and (w.get(nkey) or 0) > 0]
        n = sum(k for k, _ in xs)
        return (sum(k * float(v) for k, v in xs) / n, n) if n else (None, 0)
    out["mean_clv_mid"], out["n_clv_ok"] = pooled("mean_clv_mid", "n_clv_ok")
    out["positive_clv_rate"], _ = pooled("positive_clv_rate", "n_clv_ok")
    out["market_toward_model_rate"], _ = pooled("market_toward_model_rate", "n_clv_ok")
    out["pnl_net_per_contract"], out["n_fee_known"] = pooled("pnl_net_per_contract", "n_fee_known")
    out["brier_model"], _ = pooled("brier_model", "paired_n")
    out["brier_market"], _ = pooled("brier_market", "paired_n")
    return out


def _combine_gc_weeks(weeks: list) -> dict:
    """Sum per-week game-centre counts per horizon. A game appears in exactly one week, so counts add."""
    hz = {}
    for w in weeks:
        for h, c in (w.get("horizons") or {}).items():
            acc = hz.setdefault(h, {"n_games": 0, "below_threshold": 0, "toward": 0, "away": 0, "unchanged": 0,
                                    "no_close": 0, "no_view": 0, "signed_close_move_sum": 0.0, "signed_close_move_n": 0})
            for k in ("n_games", "below_threshold", "toward", "away", "unchanged", "no_close", "no_view", "signed_close_move_n",
                      "closer_snap_k", "n_with_actual", "closer_close_k", "n_with_close"):
                acc.setdefault(k, 0)
                acc[k] += int(c.get(k) or 0)
            acc["signed_close_move_sum"] += float(c.get("signed_close_move_sum") or 0.0)
    for acc in hz.values():
        d = acc["toward"] + acc["away"]
        acc["directional"] = d
        acc["toward_rate"] = acc["toward"] / d if d else None
        acc["mean_signed_close_move_points"] = (acc["signed_close_move_sum"] / acc["signed_close_move_n"]
                                                if acc["signed_close_move_n"] else None)
        acc["share_closer_to_actual_than_snapshot_market"] = (acc["closer_snap_k"] / acc["n_with_actual"]) if acc.get("n_with_actual") else None
        acc["share_closer_to_actual_than_close"] = (acc["closer_close_k"] / acc["n_with_close"]) if acc.get("n_with_close") else None
    return hz


def evaluate_prospective(hypothesis: dict, future_metrics: dict | None, *, n_under_test: int | None = None) -> dict:
    """Describe a hypothesis's FUTURE evidence and suggest -- never apply -- a status.

    PURE. It reads the hypothesis dict and the metrics it is handed and returns a new dict; it opens no file,
    writes no registry line and changes no status. The weekly report prints what it returns; a person decides.

    `future_metrics = {"by_week": [...]}` -- one entry per settled week, never pre-pooled, so this function can
    itself drop every week that is not strictly after the generation window and inside the test window. The
    generation week therefore cannot count however the caller assembled its input: it is removed here and
    listed under `excluded_weeks`.

      LOCALIZED_SLICE week:  {season, week, games, paired_n, effect, se, mean_clv_mid, n_clv_ok,
                              positive_clv_rate, market_toward_model_rate, pnl_net_per_contract, n_fee_known}
      GAME_CENTRE week:      {season, week, horizons: {label: {n_games, below_threshold, toward, away,
                              unchanged, no_close, signed_close_move_sum, signed_close_move_n}}}

    Only a Stage-B hypothesis (`governance()`: PREREGISTERED / TESTING with a complete preregistration record)
    is judged, against the thresholds frozen in its own record. A DISCOVERY_CANDIDATE -- GENERATED, or a status
    claiming Stage B without the record -- has no preregistered bar: its future evidence is DESCRIPTIVE and its
    suggestion is None, whatever that evidence looks like. `n_under_test` is the Stage B/C family size
    (`multiplicity_family`); a discovery candidate never enlarges it.
    """
    h = hypothesis or {}
    kind = h.get("hypothesis_kind") or (h.get("locator") or {}).get("kind")
    pre = h.get("preregistration") or {}
    th_all = pre.get("thresholds") or PREREGISTERED_THRESHOLDS
    th = th_all.get(kind) or {}
    mc = multiplicity(n_under_test or 1, (th_all.get("multiple_comparisons") or {}).get("alpha_family", 0.05))
    keep, excluded, window = _split_weeks(h, (future_metrics or {}).get("by_week") or [])
    status = h.get("status")
    gov = governance(h)
    judged = gov["stage"] == STAGE_PREREGISTERED
    out = {"id": h.get("id"), "kind": kind, "status_now": status, "stage": gov["stage"], "stage_defects": gov["defects"],
           "in_multiplicity_family": gov["in_family"], "generation_window": h.get("generation_window"),
           "test_window_used": window, "evaluated_weeks": [(w.get("season"), w.get("week")) for w in keep],
           "excluded_weeks": excluded, "new_independent_games": 0, "metrics": None,
           "trend": "INCONCLUSIVE", "direction_so_far": "NO_ESTIMATE",
           "suggested_status": None, "suggestion_reason": None, "suggestion_is_binding": False,
           "suggestion_note": SUGGESTION_ONLY, "multiple_comparisons": mc,
           "thresholds_version": th_all.get("version"), "thresholds_sha": pre.get("thresholds_sha"),
           "preregistered": gov["in_family"]}
    ge = h.get("generation_evidence") or {}
    if kind == KIND_SLICE:
        met = _combine_slice_weeks(keep)
        out["metrics"] = met
        games = met["new_independent_games"]
        out["new_independent_games"] = games
        min_g, min_n = int(th.get("min_new_independent_games", 16)), int(th.get("min_paired_outcomes", 30))
        gen_eff = h.get("effect_size") if _finite(h.get("effect_size")) else ge.get("effect_size")
        enough = games >= min_g and met["paired_settled_rows"] >= min_n
        ratio = float((th.get("trend") or {}).get("persisting_min_ratio", 0.5))
        out["trend"], out["direction_so_far"] = _trend(gen_eff, met["effect"], enough, ratio)
        if _finite(met["effect"]) and _finite(met["se"]):
            z = mc["z_adjusted"]
            met["ci95"] = [met["effect"] - mc["z_95"] * met["se"], met["effect"] + mc["z_95"] * met["se"]]
            met["ci_adjusted"] = [met["effect"] - z * met["se"], met["effect"] + z * met["se"]]
        if not judged:
            out["suggestion_reason"] = _no_suggestion_reason(gov, status)
            return out
        if not enough:
            out["suggested_status"] = "INCONCLUSIVE"
            out["suggestion_reason"] = f"{games} new games / {met['paired_settled_rows']} paired outcomes; floor {min_g} / {min_n}"
            return out
        lo, hi = (met.get("ci_adjusted") or [None, None])
        if lo is None or not _finite(gen_eff):
            out["suggested_status"], out["suggestion_reason"] = "INCONCLUSIVE", "no finite future estimate"
            return out
        same_sign = (met["effect"] < 0) == (gen_eff < 0) and met["effect"] != 0
        favourable_excl = hi < 0 if gen_eff < 0 else lo > 0
        unfavourable_excl = lo > 0 if gen_eff < 0 else hi < 0
        if unfavourable_excl or not same_sign:
            out["suggested_status"] = "NOT_SUPPORTED"
            out["suggestion_reason"] = ("adjusted CI excludes 0 against the hypothesis" if unfavourable_excl
                                        else f"sign reversed with {games} new games")
        elif favourable_excl:
            if gen_eff < 0 and not _finite(met.get("mean_clv_mid")):
                out["suggested_status"], out["suggestion_reason"] = "INCONCLUSIVE", "effect clears the bar but CLV is missing"
            elif gen_eff < 0 and met["mean_clv_mid"] < 0:
                out["suggested_status"], out["suggestion_reason"] = "INCONCLUSIVE", "effect clears the bar but mean CLV < 0"
            else:
                out["suggested_status"] = "SUPPORTED"
                out["suggestion_reason"] = "adjusted CI excludes 0 on the hypothesis's side, same sign" + (", CLV >= 0" if gen_eff < 0 else "")
        else:
            out["suggested_status"], out["suggestion_reason"] = "INCONCLUSIVE", "adjusted CI includes 0"
        return out
    if kind == KIND_GAME_CENTRE:
        hz = _combine_gc_weeks(keep)
        out["metrics"] = {"horizons": hz}
        loc = h.get("locator") or {}
        primary = loc.get("primary_horizon") or th.get("primary_horizon") or "latest_pregame"
        p = hz.get(primary) or {}
        games = int(p.get("n_games") or 0)
        out["new_independent_games"] = games
        out["primary_horizon"] = primary
        d = int(p.get("directional") or 0)
        min_d, min_g = int(th.get("min_directional_observations", 20)), int(th.get("min_new_independent_games", 16))
        for hv in hz.values():
            dd = hv["directional"]
            hv["wilson95"] = wilson(hv["toward"], dd, mc["z_95"]) if dd else None
            hv["wilson_adjusted"] = wilson(hv["toward"], dd, mc["z_adjusted"]) if dd else None
        gen_rate = ((ge.get("horizons") or {}).get(primary) or {}).get("toward_rate")
        fut_rate = p.get("toward_rate")
        enough = d >= min_d and games >= min_g
        ratio = float((th.get("trend") or {}).get("persisting_min_ratio", 0.5))
        out["trend"], out["direction_so_far"] = _trend(None if gen_rate is None else gen_rate - 0.5,
                                                       None if fut_rate is None else fut_rate - 0.5, enough, ratio)
        if not judged:
            out["suggestion_reason"] = _no_suggestion_reason(gov, status)
            return out
        if not enough:
            out["suggested_status"] = "INCONCLUSIVE"
            out["suggestion_reason"] = f"{d} directional observations over {games} new games at {primary}; floor {min_d} / {min_g}"
            return out
        lo, hi = p["wilson_adjusted"]
        if lo > 0.5:
            out["suggested_status"], out["suggestion_reason"] = "SUPPORTED", f"adjusted Wilson lower bound {lo:.3f} > 0.5"
        elif hi < 0.5 or fut_rate < 0.5:
            out["suggested_status"] = "NOT_SUPPORTED"
            out["suggestion_reason"] = (f"adjusted Wilson upper bound {hi:.3f} < 0.5" if hi < 0.5
                                        else f"toward rate {fut_rate:.3f} < 0.5 with {d} directional observations")
        else:
            out["suggested_status"], out["suggestion_reason"] = "INCONCLUSIVE", f"adjusted Wilson interval [{lo:.3f}, {hi:.3f}] includes 0.5"
        return out
    out["suggestion_reason"] = (f"unknown hypothesis kind {kind!r}: no evidence locator" if judged
                                else _no_suggestion_reason(gov, status))
    if judged:
        out["suggested_status"] = "INCONCLUSIVE"
    return out


def _no_suggestion_reason(gov: dict, status) -> str:
    if gov["stage"] == STAGE_DISCOVERY:
        return NOT_PREREGISTERED + (f" (status {status} lacks its record: {', '.join(gov['defects'])})" if gov["defects"] else "")
    return f"status {status} ({gov['stage']}): no suggestion computed"
