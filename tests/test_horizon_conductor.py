"""The horizon conductor dispatches a freeze exactly when one is owed, never stacks a second run behind a running
one, and never re-sends the same horizons within the redispatch window."""
import importlib.util
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("_hc", os.path.join(ROOT, "scripts", "shadow_v2", "horizon_conductor_v2.py"))
HC = importlib.util.module_from_spec(spec); spec.loader.exec_module(HC)

NOW = datetime(2026, 9, 20, 11, 2, tzinfo=timezone.utc)
DUE = ["2026-REG-02|20260920T1700Z|T-360m"]


def test_dispatches_when_due_and_idle():
    go, why = HC.decide(DUE, {}, NOW, active_runs=0)
    assert go and "due" in why


def test_nothing_due_is_idle():
    assert HC.decide([], {}, NOW, 0) == (False, "nothing due")


def test_a_running_horizon_job_is_never_stacked():
    go, why = HC.decide(DUE, {}, NOW, active_runs=1)
    assert not go and "already queued or running" in why


def test_the_same_horizons_are_not_resent_inside_the_window_but_are_after_it():
    sent = {frozenset(DUE): NOW - timedelta(minutes=10)}
    assert not HC.decide(DUE, sent, NOW, 0)[0]
    sent = {frozenset(DUE): NOW - timedelta(minutes=HC.REDISPATCH_MIN + 1)}
    assert HC.decide(DUE, sent, NOW, 0)[0]
    # a different due set (a new horizon became due) is dispatched at once
    assert HC.decide(DUE + ["2026-REG-02|20260920T2005Z|T-360m"], {frozenset(DUE): NOW}, NOW, 0)[0]


def test_the_workflow_is_guarded_and_can_dispatch():
    y = open(os.path.join(ROOT, ".github", "workflows", "shadow-v2-horizon-conductor.yml")).read()
    assert "if: github.ref == 'refs/heads/main'" in y and "actions: write" in y and "cancel-in-progress: false" in y
