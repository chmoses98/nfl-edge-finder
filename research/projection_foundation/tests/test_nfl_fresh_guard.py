"""Backup crons for the scheduled FRESH run: no duplicate rebuilds, saved-state compatibility, immutable archive, no backdating.

Also pins what the existing Thursday and Sunday refresh slots do, by executing the workflow's own `plan` step for every cron string.
"""
import ast
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

import pytest
import yaml

HERE = os.path.dirname(__file__)
PF_ROOT = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(PF_ROOT, "..", ".."))
sys.path.insert(0, os.path.join(PF_ROOT, "nfl", "live"))
import fresh_guard as FG  # noqa: E402  (stdlib only; imported by path exactly as the workflow runs it)

WORKFLOW = os.path.join(REPO, ".github", "workflows", "projection-foundation.yml")
ACTION = os.path.join(REPO, ".github", "actions", "nfl-pf-live", "action.yml")
NOW = datetime(2026, 10, 22, 14, 0, tzinfo=timezone.utc)          # Thursday 14:00 UTC, 49 min after the 13:11 slot


# ------------------------------------------------------------------------------------------ the guard against a real git archive
def _git(d, *args, when=None):
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    if when:
        env["GIT_COMMITTER_DATE"] = env["GIT_AUTHOR_DATE"] = when.isoformat()
    return subprocess.run(["git", "-C", str(d), *args], check=True, capture_output=True, text=True, env=env).stdout.strip()


def _archive(tmp_path, commits):
    """A projection-data archive; commits = [(subject, datetime)] oldest first. Each commit adds one file (additions only)."""
    d = tmp_path / "origin"
    d.mkdir()
    _git(d, "init", "-q", "-b", "projection-data")
    for i, (subject, when) in enumerate(commits):
        (d / f"f{i}.txt").write_text(str(i))
        _git(d, "add", "-A")
        _git(d, "commit", "-q", "-m", subject, when=when)
    return d


def _shallow_checkout(tmp_path, origin):
    """What ci.sh checkout produces: --depth 1 of projection-data."""
    dest = tmp_path / "archive"
    subprocess.run(["git", "clone", "-q", "--depth", "1", "--branch", "projection-data", f"file://{origin}", str(dest)], check=True)
    return dest


def h(hours):
    return NOW - timedelta(hours=hours)


FRESH = lambda t: f"nfl projection foundation fresh {t.strftime('%Y-%m-%dT%H:%MZ')}"        # noqa: E731
REFRESH = lambda t: f"nfl projection foundation refresh {t.strftime('%Y-%m-%dT%H:%MZ')}"    # noqa: E731
SETTLE = lambda t: f"nfl projection foundation settle {t.strftime('%Y-%m-%dT%H:%MZ')}"      # noqa: E731


def test_a_backup_skips_when_a_fresh_run_already_completed_even_with_newer_commits_on_top(tmp_path):
    origin = _archive(tmp_path, [(SETTLE(h(30)), h(30)), (FRESH(h(0.8)), h(0.8)), (REFRESH(h(0.3)), h(0.3))])
    d = _shallow_checkout(tmp_path, origin)
    assert _git(d, "rev-list", "--count", "HEAD") == "1"            # depth 1: the fresh commit is not even in the checkout
    r = FG.decide(str(d), NOW)
    assert r["skip"] is True and r["commit"] and "already completed" in r["reason"]


def test_a_backup_runs_when_no_fresh_run_completed_in_the_window(tmp_path):
    # the primary was dropped (or failed before its commit): only older fresh runs and newer refresh/settle commits exist
    origin = _archive(tmp_path, [(FRESH(h(19)), h(19)), (SETTLE(h(8)), h(8)), (REFRESH(h(2)), h(2))])
    d = _shallow_checkout(tmp_path, origin)
    r = FG.decide(str(d), NOW)
    assert r["skip"] is False and r["commit"] is None


@pytest.mark.parametrize("age_h, expect", [(5.9, True), (6.1, False)])
def test_the_window_edge(tmp_path, age_h, expect):
    origin = _archive(tmp_path, [(FRESH(h(age_h)), h(age_h))])
    assert FG.decide(str(_shallow_checkout(tmp_path, origin)), NOW)["skip"] is expect


def test_slots_are_far_enough_apart_that_one_slot_never_suppresses_the_next():
    """Saturday 13:11 -> Sunday 08:11 is the closest pair of fresh slots: 19 h, well outside the 6 h window."""
    gaps = [datetime(2026, 10, 24, 8, 11) - datetime(2026, 10, 23, 13, 11), datetime(2026, 10, 25, 8, 11) - datetime(2026, 10, 24, 13, 11)]
    assert min(gaps) > timedelta(hours=6) * 3


def test_only_a_real_fresh_commit_counts(tmp_path):
    origin = _archive(tmp_path, [("nfl projection foundation fresher", h(1)), ("fresh", h(1)), ("nfl projection foundation fresh 2026-10-22",
                                                                                                  h(1)), (REFRESH(h(0.5)), h(0.5))])
    assert FG.decide(str(origin), NOW)["skip"] is False


def test_a_commit_from_the_future_does_not_count(tmp_path):
    t = NOW + timedelta(hours=2)
    origin = _archive(tmp_path, [(FRESH(t), t)])
    assert FG.decide(str(origin), NOW)["skip"] is False


def test_fails_open_when_the_history_cannot_be_read(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    _git(empty, "init", "-q", "-b", "projection-data")                   # the orphan archive of a first-ever run: no commits
    assert FG.decide(str(empty), NOW)["skip"] is False
    notgit = tmp_path / "notgit"
    notgit.mkdir()
    assert FG.decide(str(notgit), NOW)["skip"] is False                  # not a repository at all: run


def test_the_guard_is_read_only_on_the_archive(tmp_path):
    origin = _archive(tmp_path, [(FRESH(h(1)), h(1)), (REFRESH(h(0.2)), h(0.2))])
    d = _shallow_checkout(tmp_path, origin)
    before = (_git(d, "rev-parse", "HEAD"), _git(d, "status", "--porcelain"), sorted(p.name for p in d.iterdir()))
    FG.decide(str(d), NOW)
    FG.decide(str(d), NOW)
    assert (_git(d, "rev-parse", "HEAD"), _git(d, "status", "--porcelain"), sorted(p.name for p in d.iterdir())) == before


def test_cli_writes_the_skip_output_the_workflow_reads(tmp_path):
    origin = _archive(tmp_path, [(FRESH(h(1)), h(1))])
    out = tmp_path / "gh_output"
    r = subprocess.run([sys.executable, os.path.join(PF_ROOT, "nfl", "live", "fresh_guard.py"), "--archive", str(origin), "--now", NOW.isoformat(),
                        "--window-hours", "6", "--github-output", str(out)], capture_output=True, text=True)
    assert r.returncode == 0 and out.read_text() == "skip=true\n" and "::notice::" in r.stdout


def test_the_guard_uses_only_the_standard_library_and_only_read_only_git_commands():
    src = open(os.path.join(PF_ROOT, "nfl", "live", "fresh_guard.py")).read()
    mods = {n.names[0].name.split(".")[0] if isinstance(n, ast.Import) else (n.module or "").split(".")[0]
            for n in ast.walk(ast.parse(src)) if isinstance(n, (ast.Import, ast.ImportFrom))}
    assert mods <= {"argparse", "re", "subprocess", "sys", "datetime", "__future__"}, mods      # no pf_core, no nfl.*, no pandas
    git_subcommands = set(re.findall(r'_git\(archive, "([a-z-]+)"', src))
    assert git_subcommands == {"rev-parse", "fetch", "log"}, git_subcommands                      # never add/commit/push/reset/checkout
    assert "open(" not in src.replace('open(a.github_output, "a")', "")                          # writes nothing but the step output


# ------------------------------------------------------------------------------------------ the workflow
wf = yaml.safe_load(open(WORKFLOW))
CRONS = [c["cron"] for c in wf[True]["schedule"]]                      # PyYAML reads the key `on` as True
LIVE_STEPS = wf["jobs"]["live"]["steps"]
PLAN = next(s for s in LIVE_STEPS if s.get("id") == "plan")


def plan_mode(schedule):
    out = os.path.join(os.environ.get("TMPDIR", "/tmp"), f"gh_out_{os.getpid()}")
    open(out, "w").close()
    env = {**os.environ, "SCHEDULE": schedule, "IN_MODE": "", "IN_DRY": "", "GITHUB_OUTPUT": out}
    subprocess.run(["bash", "-eo", "pipefail", "-c", PLAN["run"]], check=True, env=env, capture_output=True)
    got = dict(l.split("=", 1) for l in open(out).read().split())
    os.remove(out)
    return got["mode"]


MONTHS = "9-12,1-2"
FRESH_PRIMARY = {f"11 13 * {MONTHS} 4": "Thu 13:11", f"11 13 * {MONTHS} 6": "Sat 13:11", f"11 8 * {MONTHS} 0": "Sun 08:11"}
FRESH_BACKUP = {f"36 13 * {MONTHS} 4": "Thu 13:36", f"36 13 * {MONTHS} 6": "Sat 13:36", f"36 8 * {MONTHS} 0": "Sun 08:36"}
SETTLE_SLOTS = {f"23 15 * {MONTHS} 2", f"23 15 * {MONTHS} 3"}
# the refresh slots ~70 min before the kickoff windows, each with its backup 12 minutes later
REFRESH_PAIRS = [("3 23", "15 23", 4), ("20 12", "32 12", 0), ("52 15", "4 16", 0), ("2 19", "14 19", 0), ("12 23", "24 23", 0), ("3 23", "15 23", 1)]


def test_every_fresh_slot_has_exactly_one_backup_25_minutes_later_and_it_runs_the_fresh_mode():
    for primary in FRESH_PRIMARY:
        m, hr, dom, mon, dow = primary.split()
        backup = f"{(int(m) + 25) % 60} {hr if int(m) + 25 < 60 else int(hr) + 1} {dom} {mon} {dow}"
        assert backup in FRESH_BACKUP, (primary, backup)
        assert CRONS.count(primary) == 1 and CRONS.count(backup) == 1
        assert plan_mode(primary) == "fresh" and plan_mode(backup) == "fresh"


def test_the_existing_thursday_and_sunday_refresh_slots_still_run_in_refresh_mode_with_their_backups():
    for a, b, dow in REFRESH_PAIRS:
        for t in (a, b):
            cron = f"{t} * {MONTHS} {dow}"
            assert cron in CRONS, cron
            assert plan_mode(cron) == "refresh", cron
    thu_tnf = [f"3 23 * {MONTHS} 4", f"15 23 * {MONTHS} 4"]
    assert all(plan_mode(c) == "refresh" for c in thu_tnf)


def test_settle_slots_and_the_schedule_as_a_whole():
    assert {plan_mode(c) for c in SETTLE_SLOTS} == {"settle"}
    fresh = set(FRESH_PRIMARY) | set(FRESH_BACKUP)
    refresh = {f"{t} * {MONTHS} {dow}" for a, b, dow in REFRESH_PAIRS for t in (a, b)}
    assert set(CRONS) == fresh | refresh | SETTLE_SLOTS and len(CRONS) == len(set(CRONS))        # nothing unexplained, no duplicate cron


def test_manual_dispatch_always_runs_what_it_was_asked_to():
    env = {**os.environ, "SCHEDULE": "", "IN_MODE": "fresh", "IN_DRY": "false", "GITHUB_OUTPUT": "/dev/stdout"}
    assert "mode=fresh" in subprocess.run(["bash", "-c", PLAN["run"]], env=env, capture_output=True, text=True).stdout
    guard = next(s for s in LIVE_STEPS if s.get("id") == "guard")
    assert "github.event_name == 'schedule'" in guard["if"]                                       # a dispatch is never guarded


def test_the_guard_runs_after_the_archive_checkout_and_before_anything_that_builds_or_writes():
    ids = [s.get("id") or s.get("name", "") for s in LIVE_STEPS]
    iguard = ids.index("guard")
    checkout = next(i for i, s in enumerate(LIVE_STEPS) if "ci.sh checkout" in s.get("run", ""))
    live = ids.index("live")
    commit = next(i for i, s in enumerate(LIVE_STEPS) if "ci.sh push" in s.get("run", ""))
    assert checkout < iguard < live < commit
    guard = LIVE_STEPS[iguard]
    assert guard["if"] == "github.event_name == 'schedule' && steps.plan.outputs.mode == 'fresh'"
    assert "fresh_guard.py" in guard["run"] and "--github-output" in guard["run"]
    # a skip stops the heavy action AND the commit; both still run when the guard did not run or said false
    assert LIVE_STEPS[live]["if"] == "steps.guard.outputs.skip != 'true'"
    assert "steps.guard.outputs.skip != 'true'" in LIVE_STEPS[commit]["if"] and "dry != 'true'" in LIVE_STEPS[commit]["if"]


def test_the_pull_request_dry_run_is_not_guarded():
    pr = wf["jobs"]["pr-dry-run"]["steps"]
    assert not any(s.get("id") == "guard" for s in pr)
    assert all("skip" not in str(s.get("if", "")) for s in pr)


# ------------------------------------------------------------------------------------------ saved-state compatibility and the action
def test_nothing_this_change_adds_is_part_of_the_saved_state_fingerprint():
    src = open(os.path.join(PF_ROOT, "nfl", "live", "state.py")).read()
    code = ast.literal_eval(re.search(r"STATE_CODE = (\[.*?\])\n", src, re.S).group(1))
    assert code and not any(p.startswith(("nfl/live/", "../", ".github")) for p in code)
    assert "nfl/live/fresh_guard.py" not in code
    # and the cache keys in the action (what makes a saved state reusable) are untouched by the workflow change
    act = open(ACTION).read()
    assert "nfl-pf-state-${{ hashFiles('research/projection_foundation/requirements-pf.txt') }}-restore-${{ github.run_id }}" in act


def test_refresh_still_reuses_only_and_fresh_still_rebuilds_everything():
    act = open(ACTION).read()
    assert re.search(r"fresh\)\s+STAGES=all;\s+POLICY=fresh", act)
    assert re.search(r"refresh\)\s+STAGES=capture,project,publish,guard;\s+POLICY=reuse-only", act)
    assert re.search(r"settle\)\s+STAGES=results,settle,score,guard;\s+POLICY=reuse", act)


# ------------------------------------------------------------------------------------------ overlap
def test_a_backup_can_never_overlap_a_running_original_fresh_run():
    """One concurrency group for every scheduled and dispatched run, and a running run is never cancelled: the backup is queued
    behind the original and starts only after it finished (then the guard sees its commit and skips). Pull requests have their own
    group, so a PR dry run neither blocks nor is blocked by the live chain."""
    c = wf["concurrency"]
    assert c["cancel-in-progress"] is False
    live_group = re.sub(r"\$\{\{.*?\}\}", "<expr>", c["group"])
    assert live_group == "projection-foundation-nfl-<expr>" and "|| 'live'" in c["group"] and "'pull_request'" in c["group"]
    # every job that can write the archive is in this workflow (so it is under this one group); no other workflow pushes projection-data
    others = [f for f in os.listdir(os.path.dirname(WORKFLOW)) if f.endswith(".yml") and f != "projection-foundation.yml"]
    for f in others:
        assert "projection-data" not in open(os.path.join(os.path.dirname(WORKFLOW), f)).read(), f
    # and no job in the workflow overrides the group
    assert not any("concurrency" in j for j in wf["jobs"].values())
