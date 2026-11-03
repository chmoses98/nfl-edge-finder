"""The recovery workflow stays partitioned (no raised timeouts), main-only, and a dry run cannot publish."""
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WF = open(os.path.join(ROOT, ".github", "workflows", "shadow-v2-closes-recovery.yml")).read()
SETTLE = open(os.path.join(ROOT, ".github", "workflows", "shadow-v2-settle.yml")).read()


def test_job_limit_not_raised_and_step_limit_below_it():
    job = int(re.search(r"^    timeout-minutes: (\d+)", WF, re.M).group(1))
    step = int(re.search(r"^        timeout-minutes: (\d+)", WF, re.M).group(1))
    assert job == 120 and step < job
    assert "timeout-minutes: 75" in SETTLE and "timeout-minutes: 120" in SETTLE      # the settle limits are untouched


def test_runs_from_main_only_and_never_fetches_the_whole_branch():
    assert "github.ref == 'refs/heads/main'" in WF
    assert "market_data_worktree.sh" not in WF and "git fetch --depth=1 origin market-data" not in WF
    assert "--dry-run" in WF and "inputs.dry_run" in WF


def test_dry_run_never_runs_the_coverage_publish_view():
    assert "!inputs.dry_run" in WF.split("Close coverage of what this run published")[1].split("upload-artifact")[0]
