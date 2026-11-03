"""shadow-v2-settle: the market-data worktree must fit, a dry run must publish nothing, and closes must be reported honestly.

Run 41513363507 (and, by their step state, runs 41476949203 and 41434693429) died inside the fetch step: the ~52 GB
market-data worktree does not fit on a runner's root filesystem even after scripts/ci/free_runner_disk.sh. These tests
pin the repair (the worktree is placed on the filesystem with room, behind a fail-closed size check), the `dry_run`
input that lets the workflow be validated without writing production data, and the true-close / proxy / missing split.
"""
import gzip
import importlib.util
import json
import os
import subprocess

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORKFLOW = os.path.join(ROOT, ".github", "workflows", "shadow-v2-settle.yml")
SCRIPT = os.path.join(ROOT, "scripts", "ci", "market_data_worktree.sh")


def _git(cwd, *args):
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", *args], cwd=cwd, check=True,
                   capture_output=True, text=True)


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    _git(r, "init", "-q", "-b", "main")
    _git(r, "commit", "-q", "--allow-empty", "-m", "init")
    _git(r, "checkout", "-q", "-b", "market-data")
    (r / "data").mkdir()
    (r / "data" / "x.txt").write_text("market data")
    _git(r, "add", "-A")
    _git(r, "commit", "-q", "-m", "md")
    _git(r, "checkout", "-q", "main")
    return r


def _run(repo, tmp_path, **env):
    e = {**os.environ, "MD_LINK": str(tmp_path / "link"), "MD_CANDIDATES": str(tmp_path / "disk"),
         "MD_REF": "market-data", "MD_MIN_FREE_GB": "0", **env}
    (tmp_path / "disk").mkdir(exist_ok=True)
    return subprocess.run(["bash", SCRIPT], cwd=repo, env=e, capture_output=True, text=True)


def test_the_worktree_lands_on_the_chosen_disk_and_is_reachable_at_the_link(repo, tmp_path):
    out = _run(repo, tmp_path)
    assert out.returncode == 0, out.stderr + out.stdout
    link = tmp_path / "link"
    assert link.is_symlink()
    assert (link / "data" / "x.txt").read_text() == "market data"
    # the bytes are on the candidate disk, not at the link's own location
    assert (tmp_path / "disk" / "md-worktree" / "data" / "x.txt").exists()


def test_a_rerun_over_a_previous_worktree_is_idempotent(repo, tmp_path):
    assert _run(repo, tmp_path).returncode == 0
    second = _run(repo, tmp_path)
    assert second.returncode == 0, second.stderr + second.stdout
    assert (tmp_path / "link" / "data" / "x.txt").exists()


def test_it_refuses_a_checkout_the_disk_cannot_hold_and_creates_nothing(repo, tmp_path):
    out = _run(repo, tmp_path, MD_MIN_FREE_GB="100000000")
    assert out.returncode == 3
    assert "Refusing to start a checkout" in out.stderr
    assert not (tmp_path / "link").exists()
    assert not (tmp_path / "disk" / "md-worktree").exists()


def test_it_refuses_when_no_candidate_exists(repo, tmp_path):
    e = {**os.environ, "MD_LINK": str(tmp_path / "link"), "MD_CANDIDATES": str(tmp_path / "nowhere"),
         "MD_REF": "market-data"}
    out = subprocess.run(["bash", SCRIPT], cwd=repo, env=e, capture_output=True, text=True)
    assert out.returncode == 2


# ----------------------------------------------------------------------------------------------- the workflow
def _wf():
    return open(WORKFLOW).read()


def test_the_workflow_places_the_worktree_with_the_helper_after_freeing_disk():
    y = _wf()
    free = y.find("bash scripts/ci/free_runner_disk.sh")
    fetch = y.find("git fetch --depth=1 origin market-data")
    place = y.find("bash scripts/ci/market_data_worktree.sh")
    assert 0 <= free < fetch < place
    assert "git worktree add -f /tmp/md" not in y          # the ~52 GB tree is never again placed on the root disk


def test_dry_run_is_a_boolean_input_that_defaults_to_false():
    import yaml
    doc = yaml.safe_load(open(WORKFLOW))
    on = doc.get("on", doc.get(True))
    inp = on["workflow_dispatch"]["inputs"]["dry_run"]
    assert inp["type"] == "boolean" and inp["default"] is False


def test_every_publish_step_is_skipped_on_a_dry_run():
    import yaml
    doc = yaml.safe_load(open(WORKFLOW))
    steps = doc["jobs"]["settle"]["steps"]
    publishers = [s for s in steps if "publish_market_data.py" in (s.get("run") or "")]
    assert len(publishers) == 4                                      # closes, evidence, scorecard, research
    for s in publishers:
        assert "!inputs.dry_run" in str(s.get("if")), s["name"]


def test_the_main_guard_is_untouched():
    import yaml
    doc = yaml.safe_load(open(WORKFLOW))
    assert doc["jobs"]["settle"]["if"] == "github.ref == 'refs/heads/main'"


# ------------------------------------------------------------------------------------------------- closes
def _coverage():
    spec = importlib.util.spec_from_file_location("close_coverage", os.path.join(ROOT, "scripts", "shadow_v2", "close_coverage.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_tiers_map_to_true_close_proxy_and_missing_and_unknown_is_never_a_true_close():
    cc = _coverage()
    assert cc.classify({"close_quality": "EXCELLENT"}) == cc.TRUE_CLOSE
    assert cc.classify({"close_quality": "GOOD"}) == cc.TRUE_CLOSE
    assert cc.classify({"close_quality": "STALE"}) == cc.PROXY
    assert cc.classify({"close_quality": "MISSING"}) == cc.MISSING
    assert cc.classify({"close_quality": "NOT_APPLICABLE"}) == cc.NOT_APPLICABLE
    assert cc.classify({}) == cc.MISSING
    assert cc.classify({"close_quality": "something new"}) == cc.MISSING


def test_coverage_counts_by_week_and_excludes_season_markets():
    cc = _coverage()
    rows = [{"game_id": "2026_05_A_B", "close_quality": "EXCELLENT"},
            {"game_id": "2026_05_A_B", "close_quality": "STALE"},
            {"game_id": "2026_06_C_D", "close_quality": "MISSING"},
            {"game_id": None, "close_quality": "NOT_APPLICABLE"},
            {"game_id": "weird", "close_quality": "GOOD"}]
    rep = cc.coverage(rows)
    assert rep["weeks"]["05"] == {"records": 2, "TRUE_CLOSE": 1, "EARLIER_QUOTE_PROXY": 1, "MISSING": 0, "true_close_share": 0.5}
    assert rep["weeks"]["06"]["MISSING"] == 1
    assert rep["weeks"]["unknown"]["TRUE_CLOSE"] == 1
    assert rep["total"]["records"] == 4                               # the season market is not counted
    assert rep["total"]["true_close_share"] == 0.5


def test_coverage_reads_gzip_batches_from_disk(tmp_path):
    cc = _coverage()
    d = tmp_path / "2026_07_X_Y"
    d.mkdir()
    with gzip.open(d / "close-2.1.0.b1.closes_v2.jsonl.gz", "wt") as fh:
        fh.write(json.dumps({"game_id": "2026_07_X_Y", "close_quality": "GOOD"}) + "\n")
        fh.write(json.dumps({"game_id": "2026_07_X_Y", "close_quality": "MISSING"}) + "\n")
    rep = cc.coverage(cc.iter_rows(str(tmp_path)))
    assert rep["weeks"]["07"]["records"] == 2 and rep["weeks"]["07"]["TRUE_CLOSE"] == 1
    assert "| 07 |" in cc.markdown(rep)


# ------------------------------------------------------------------------------------------ fetch time budget
def test_the_market_data_fetch_has_room_and_the_closes_are_published_before_the_job_limit():
    """The ~52 GB fetch is bandwidth-bound: 14.5, ~22 and then 40+ min (run 41688588424 was killed at 40 with nothing logged).

    The job limit is deliberately not raised (workflow header), so the property that must hold is evidence-first: the fetch, the
    closes step and the closes publish fit the job limit, and the closes publish BEFORE settlement starts.
    """
    import yaml
    doc = yaml.safe_load(open(WORKFLOW))
    job = doc["jobs"]["settle"]
    steps = {s.get("id"): s for s in job["steps"] if s.get("id")}
    assert steps["fetch"]["timeout-minutes"] >= 75
    assert job["timeout-minutes"] == 120                                   # not raised
    evidence_first = sum(steps[i]["timeout-minutes"] for i in ("fetch", "closes", "publish_closes"))
    assert evidence_first <= job["timeout-minutes"], evidence_first
    order = [s.get("id") for s in job["steps"] if s.get("id")]
    assert order.index("publish_closes") < order.index("settle")           # closes are out before settlement starts
