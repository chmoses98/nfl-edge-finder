"""The incumbent capture must plan exactly what it planned before shadow v2 existed.

`scripts/kalshi/capture.py` runs the live Sunday experiment, and `kalshi-capture.yml` is dispatch-driven with no
branch condition -- so anything this branch changes unconditionally in that file takes effect on the first
dispatch after merge, mid-experiment. A pre-week audit found exactly that: the branch had replaced main's
"closest kickoff first" book ordering with a four-tier priority, which under the 2,500-book cap changes WHICH
books the running experiment captures.

These tests pin the boundary. `MAIN_RULE` below is main's ordering, transcribed from
`git show 7d07368:scripts/kalshi/capture.py`:

    book_candidates.append((minutes_to_kick, m["ticker"], row["pregame"]))
    book_candidates.sort()
    for minutes_to_kick, ticker, pregame in book_candidates[: a.max_books]:

so the incumbent plan is the first `max_books` of the candidates sorted by (minutes to kickoff, ticker).
"""
import importlib.util
import os
import random
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def _capture():
    spec = importlib.util.spec_from_file_location("kalshi_capture", os.path.join(ROOT, "scripts", "kalshi", "capture.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


CAP = _capture()


def MAIN_RULE(candidates, max_books):
    """main's plan, verbatim in behaviour: sort (minutes_to_kickoff, ticker, pregame), take the first N."""
    ordered = sorted((mtk, tk, pg) for mtk, _vol, tk, pg in candidates)
    return [tk for _mtk, tk, _pg in ordered[:max_books]]


def fixture(n=400, seed=11):
    """A board that exercises every tier the v2 rule distinguishes: near/far x traded/untraded."""
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        mtk = rnd.choice([rnd.uniform(0, 360), rnd.uniform(360, 2000)])
        vol = rnd.choice([0.0, 0.0, rnd.uniform(1, 5000)])
        out.append((round(mtk, 1), vol, f"KXNFL-T{i:04d}", mtk > 0))
    return out


# ------------------------------------------------------------------- the incumbent plan is byte-for-byte main's
@pytest.mark.parametrize("max_books", [1, 25, 250, 2500])
def test_incumbent_planning_matches_main_exactly(max_books):
    cands = fixture()
    req, _dropped = CAP.plan_book_requests(cands, max_books, v2=False)
    assert [tk for _k, _mtk, tk, _pg in req] == MAIN_RULE(cands, max_books)


def test_incumbent_planning_is_identical_across_many_boards():
    for seed in range(25):
        cands = fixture(n=300, seed=seed)
        req, _ = CAP.plan_book_requests(cands, 120, v2=False)
        assert [tk for _k, _mtk, tk, _pg in req] == MAIN_RULE(cands, 120), f"board {seed} diverged from main"


def test_the_incumbent_request_ORDER_matches_not_merely_the_set():
    """A different order is a different API request sequence and a different rate-limit profile."""
    cands = fixture(n=150, seed=7)
    req, _ = CAP.plan_book_requests(cands, 150, v2=False)
    assert [tk for _k, _mtk, tk, _pg in req] == MAIN_RULE(cands, 150)


# ---------------------------------------------------------------- the v2 rule is real, and it is gated off
def test_the_v2_rule_genuinely_differs_so_the_gate_is_load_bearing():
    cands = fixture(n=400, seed=3)
    inc, _ = CAP.plan_book_requests(cands, 120, v2=False)
    v2, _ = CAP.plan_book_requests(cands, 120, v2=True)
    assert [t for _k, _m, t, _p in inc] != [t for _k, _m, t, _p in v2], \
        "if the two plans were identical this gate would be pointless -- and the audit finding unreal"
    v2_set = {t for _k, _m, t, _p in v2}
    near_traded = {tk for mtk, vol, tk, _pg in cands if mtk <= 360.0 and vol > 0}
    assert near_traded <= v2_set, "v2 promises near-kickoff traded contracts first; it must actually deliver them"


def test_the_gate_is_off_unless_something_explicitly_turns_it_on(monkeypatch):
    monkeypatch.delenv(CAP.V2_ENV, raising=False)
    assert CAP.v2_capture_enabled() is False
    assert CAP.v2_capture_enabled(False) is False
    assert CAP.v2_capture_enabled(True) is True
    for v in ("1", "true", "TRUE", "yes", "on"):
        monkeypatch.setenv(CAP.V2_ENV, v)
        assert CAP.v2_capture_enabled() is True, f"{v!r} should enable v2"
    for v in ("", "0", "false", "no", "off", "maybe"):
        monkeypatch.setenv(CAP.V2_ENV, v)
        assert CAP.v2_capture_enabled() is False, f"{v!r} must not enable v2"


def test_the_incumbent_workflow_does_not_turn_v2_on():
    """The one place that could flip the live experiment: prove nothing in it does."""
    wf = open(os.path.join(ROOT, ".github", "workflows", "kalshi-capture.yml")).read()
    assert "--v2-capture" not in wf
    assert CAP.V2_ENV not in wf


def test_no_v2_only_dependency_is_reachable_from_the_incumbent_plan():
    """Incumbent planning must not depend on the provisional registry or the semantics engine."""
    cands = fixture(n=50, seed=1)
    req, dropped = CAP.plan_book_requests(cands, 20, v2=False)
    assert len(req) == 20 and len(dropped) == 30
    assert all(isinstance(k, tuple) and len(k) == 2 for k, _m, _t, _p in req), \
        "the incumbent sort key must stay (minutes_to_kickoff, ticker) with no tier component"
