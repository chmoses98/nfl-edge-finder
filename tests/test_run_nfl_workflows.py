"""The RUN NFL trigger architecture, asserted against the YAML rather than against a description of it.

Four things have to be true for "RUN NFL" to be an operational workflow rather than a script somebody runs:

1. `Actions -> RUN NFL -> Run workflow` with every field blank must work. If a required input creeps in, or
   a default week gets hard-coded, the workflow silently becomes an expert tool again.
2. The automatic refresh must ride on the shadow-pricing cycle, which has already paid for the expensive
   inputs, and must see the ledger THAT CYCLE wrote -- not the one published two hours earlier.
3. The horizon conductor must be cheap when it has nothing to do, and must not consume a horizon before the
   build that satisfies it has succeeded.
4. Every successful run must leave the report somewhere a person can click: an artifact and `latest/`.
"""
import os
import re

import pytest
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WF = os.path.join(ROOT, ".github", "workflows")


def wf(name):
    with open(os.path.join(WF, name)) as f:
        return yaml.safe_load(f)


def on(doc):
    return doc.get(True, doc.get("on"))


def steps(doc, job=None):
    jobs = doc.get("jobs") or {}
    for jname, j in jobs.items():
        if job and jname != job:
            continue
        for s in (j.get("steps") or []):
            yield s


def runs(doc, job=None):
    return [s.get("run") or "" for s in steps(doc, job)]


# ------------------------------------------------------------------ 1. the manual experience

def test_run_nfl_exists_and_is_manually_dispatchable():
    d = wf("run-nfl.yml")
    assert d["name"] == "RUN NFL"
    assert "workflow_dispatch" in on(d)


def test_every_manual_input_is_optional():
    """The normal user must not have to know the current NFL week."""
    inputs = (on(wf("run-nfl.yml"))["workflow_dispatch"] or {}).get("inputs") or {}
    required = [k for k, v in inputs.items() if (v or {}).get("required")]
    assert required == [], f"RUN NFL requires manual input for {required}"
    assert set(inputs) >= {"season", "week", "game_id", "force_fresh"}
    assert inputs["season"].get("default") in ("", None)
    assert inputs["week"].get("default") in ("", None)
    assert inputs["force_fresh"].get("default") is True


def test_a_blank_week_is_resolved_and_never_defaulted():
    """`run_nfl.py --week` defaults to 1. A workflow that passed a literal week would be that bug again."""
    d = wf("run-nfl.yml")
    src = "\n".join(runs(d))
    assert "resolve_active_week.py" in src
    assert not re.search(r"--week\s+1\b", src), "a literal week is hard-coded into the workflow"
    assert "--week ${{ steps.week.outputs.week }}" in src


def test_run_nfl_is_callable_by_other_workflows():
    d = wf("run-nfl.yml")
    call = on(d)["workflow_call"]
    assert set((call or {}).get("inputs") or {}) >= {"season", "week", "force_fresh", "trigger",
                                                     "horizon_ids"}


def test_a_pinned_game_id_still_builds_the_whole_slate():
    src = "\n".join(runs(wf("run-nfl.yml")))
    assert "--focus-game-id" in src, "game_id must be a focus, not a filter"
    assert "--only-game" not in src and "--game-id " not in src


def test_the_fresh_path_rebuilds_the_state_the_packet_is_made_of():
    """force_fresh must actually mean fresh: new context, new local pricing, latest captures."""
    d = wf("run-nfl.yml")
    fresh = [s for s in steps(d) if "force_fresh" in str(s.get("if", ""))]
    body = "\n".join(s.get("run") or "" for s in fresh)
    assert "context_capture.py" in body
    assert "price_slate.py" in body
    assert "build_player_map.py" in body
    assert fresh, "no step is conditioned on force_fresh"


def test_a_fresh_run_refuses_to_fall_back_to_the_published_ledger():
    """If the copy of the freshly priced snapshot into the market-data tree silently matched nothing, the
    packet would build from the older PUBLISHED ledger and still be labelled fresh. An age limit makes that
    a failure rather than a lie."""
    build = next(s for s in steps(wf("run-nfl.yml")) if "build_report.py" in (s.get("run") or ""))
    body = build["run"]
    assert "--max-ledger-age-min" in body
    assert "force_fresh" in body, "the age limit is not tied to force_fresh"


def test_a_manual_run_does_not_publish_a_duplicate_canonical_ledger():
    """A research question must not append to the immutable shadow ledger."""
    src = "\n".join(runs(wf("run-nfl.yml")))
    assert "publish_market_data.py" not in src


def test_the_fresh_local_snapshot_is_the_one_the_packet_reads():
    src = "\n".join(runs(wf("run-nfl.yml")))
    assert "/tmp/md/data/shadow/ledger" in src, (
        "price_slate writes locally; without copying it under --market-data the packet still reads the "
        "published (older) snapshot and the 'fresh' run is not fresh")


# ------------------------------------------------------------------ 2. the automatic cadence

def test_shadow_pricing_still_runs_every_two_hours():
    assert on(wf("shadow-price.yml"))["schedule"] == [{"cron": "37 */2 * * *"}]


def test_the_report_is_built_inside_the_shadow_pricing_cycle():
    """Not a second expensive job: this one already has the nflverse inputs and the newest ledger."""
    d = wf("shadow-price.yml")
    assert any("build_report.py" in r for r in runs(d))


def test_the_shadow_cycle_shows_the_packet_builder_the_ledger_it_just_wrote():
    d = wf("shadow-price.yml")
    names = [s.get("name", "") for s in steps(d)]
    body = [s.get("run") or "" for s in steps(d)]
    price_at = next(i for i, r in enumerate(body) if "price_slate.py" in r)
    copy_at = next(i for i, r in enumerate(body) if "/tmp/md/data/shadow/ledger" in r)
    build_at = next(i for i, r in enumerate(body) if "build_report.py" in r)
    assert price_at < copy_at < build_at, f"ordering wrong in {names}"


def test_a_report_failure_cannot_fail_the_pricing_job():
    """The ledger is the product of that job and is already published by then."""
    d = wf("shadow-price.yml")
    for s in steps(d):
        run = s.get("run") or ""
        if any(k in run for k in ("build_report.py", "publish_handicap_report.py",
                                  "resolve_active_week.py")):
            assert s.get("continue-on-error") is True, f"step {s.get('name')!r} can fail the pricing job"


def test_the_shadow_cycle_report_refuses_a_stale_ledger():
    src = "\n".join(runs(wf("shadow-price.yml")))
    assert "--max-ledger-age-min" in src, (
        "the cycle builds from the snapshot it just priced; without an age limit a failed pricing step "
        "would silently produce a report from a two-hour-old ledger")


# ------------------------------------------------------------------ 3. the horizon conductor

def test_the_conductor_wakes_often_and_is_cheap():
    d = wf("run-nfl-horizons.yml")
    cron = on(d)["schedule"][0]["cron"]
    assert cron.startswith("*/"), cron
    assert int(cron.split()[0].lstrip("*/")) <= 15
    gate = d["jobs"]["gate"]
    assert not any("pip install" in (s.get("run") or "") for s in (gate.get("steps") or [])), (
        "the gate installs dependencies on every wake; the calendar and horizon modules are stdlib-only "
        "so that a wake with nothing to do costs seconds")


def test_the_expensive_path_runs_only_when_a_horizon_is_due():
    d = wf("run-nfl-horizons.yml")
    report = d["jobs"]["report"]
    assert "needs.gate.outputs.should_run == 'true'" in report["if"]
    assert report["uses"].endswith("run-nfl.yml"), "the conductor must reuse the RUN NFL workflow"
    assert report["with"]["force_fresh"] is True, "a horizon snapshot that rerenders an old ledger is not one"
    assert report["with"]["trigger"] == "horizon"


def test_horizons_are_marked_captured_only_after_a_successful_build():
    d = wf("run-nfl.yml")
    mark = next(s for s in steps(d) if "mark_horizons.py" in (s.get("run") or ""))
    assert "report_status == 'SUCCESS'" in mark["if"], (
        "marking a horizon captured before the build succeeded deletes a decision moment on every flaky "
        "runner")


def test_the_conductor_passes_the_horizon_ids_through():
    d = wf("run-nfl-horizons.yml")
    assert d["jobs"]["report"]["with"]["horizon_ids"] == "${{ needs.gate.outputs.horizon_ids }}"


# ------------------------------------------------------------------ 4. seeing the report

@pytest.mark.parametrize("name", ["run-nfl.yml", "shadow-price.yml"])
def test_a_successful_run_uploads_an_artifact_with_a_findable_name(name):
    d = wf(name)
    up = [s for s in steps(d) if str(s.get("uses", "")).startswith("actions/upload-artifact")]
    assert up, f"{name} uploads no report artifact"
    a = up[0]["with"]
    assert a["name"].startswith("run-nfl-")
    assert "${{ github.run_id }}" in a["name"]
    assert "week_padded" in a["name"]
    assert int(a["retention-days"]) >= 30
    assert a["if-no-files-found"] == "error"


@pytest.mark.parametrize("name", ["run-nfl.yml", "shadow-price.yml"])
def test_a_successful_run_publishes_the_browsable_latest_report(name):
    d = wf(name)
    pub = next(s for s in steps(d) if "publish_handicap_report.py" in (s.get("run") or ""))
    assert "SUCCESS" in str(pub.get("if")), "a failed build must not replace latest/"


@pytest.mark.parametrize("name", ["run-nfl.yml", "run-nfl-horizons.yml"])
def test_the_report_workflows_can_write_the_report_branch(name):
    assert (wf(name).get("permissions") or {}).get("contents") == "write"


def test_run_nfl_serialises_with_itself():
    assert (wf("run-nfl.yml").get("concurrency") or {}).get("cancel-in-progress") is False


# ------------------------------------------------------------------ 5. freshness hardening

def test_run_nfl_builds_from_canonical_main():
    """RUN NFL's contract is "current production main + current market-data". A plain checkout builds
    whatever ref the dispatch was launched from, so a report from an experimental branch would be
    indistinguishable from a canonical one: same artifact name, same latest/, same manifest."""
    checkout = next(s for s in steps(wf("run-nfl.yml"))
                    if str(s.get("uses", "")).startswith("actions/checkout"))
    assert (checkout.get("with") or {}).get("ref") == "main", (
        "run-nfl.yml checkout is not pinned to main")


def test_the_test_workflow_still_builds_the_branch_under_review():
    """Pinning production to main must not stop CI from testing the code being changed."""
    checkout = next(s for s in steps(wf("tests.yml"))
                    if str(s.get("uses", "")).startswith("actions/checkout"))
    assert "ref" not in (checkout.get("with") or {}), (
        "tests.yml pins a ref, so a PR would be tested against main rather than against itself")


def test_the_fresh_context_capture_can_fail_the_run():
    """continue-on-error here meant a force_fresh run could lose its context capture, fall back to older
    published weather/injuries, build, replace latest/ and mark a decision horizon captured."""
    ctx = next(s for s in steps(wf("run-nfl.yml")) if "context_capture.py" in (s.get("run") or ""))
    assert ctx.get("continue-on-error") is not True, (
        "the fresh context capture is continue-on-error, so a failed capture still produces a 'fresh' report")


def test_the_fresh_context_run_id_is_proved_to_have_reached_the_packet():
    ctx = next(s for s in steps(wf("run-nfl.yml")) if "context_capture.py" in (s.get("run") or ""))
    assert "context_run_id=" in ctx["run"], "the capture does not export the run id it produced"
    build = next(s for s in steps(wf("run-nfl.yml")) if "build_report.py" in (s.get("run") or ""))
    assert "--require-context-run-id" in build["run"]
    assert "steps.context.outputs.context_run_id" in build["run"]


def test_fresh_and_horizon_builds_gate_the_kalshi_capture_age():
    """A fresh LEDGER is not a fresh MARKET: price_slate prices the newest capture it can find, so a
    ledger written a minute ago can quote a Kalshi poll from an hour ago."""
    build = next(s for s in steps(wf("run-nfl.yml")) if "build_report.py" in (s.get("run") or ""))
    assert "--max-capture-age-min 30" in build["run"]
    assert "force_fresh" in build["run"], "the capture gate is not tied to the fresh path"


def test_the_shadow_cycle_gates_capture_age_without_failing_the_pricing_job():
    d = wf("shadow-price.yml")
    build = next(s for s in steps(d) if "build_report.py" in (s.get("run") or ""))
    assert "--max-capture-age-min" in build["run"]
    assert build.get("continue-on-error") is True, (
        "a stale report capture must not fail the canonical pricing job; the ledger is its product")


def test_the_horizon_path_inherits_the_fresh_gates():
    """The conductor calls run-nfl.yml with force_fresh, so it gets the same capture and context gates."""
    report = wf("run-nfl-horizons.yml")["jobs"]["report"]
    assert report["with"]["force_fresh"] is True
