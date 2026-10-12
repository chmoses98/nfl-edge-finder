"""shadow-v2-project.yml must be able to publish what it projected (incident 2026-10-06 .. 2026-10-11).

From 2026-10-06 06:09Z every scheduled run of `Shadow v2 projections (full board)` projected the whole board,
verified it (run 38165258720: 350,482 records, 0 problems) and then died in its LAST step, "Publish the immutable
projection records and the run summary":

    + git worktree add -f /home/runner/work/nfl-edge-finder/_market_data_wt origin/market-data
    fatal: cannot create directory at 'data/shadow/evaluations/2026_01_NE_SEA': No space left on device

`publish_market_data.py` checks out its own FULL market-data worktree (../_market_data_wt), and the job still held
the full /tmp/md checkout from its fetch step. Two full copies of the ~52 GB branch plus the nflverse inputs no
longer fit on a hosted runner (86 GB free, 116 GB after scripts/ci/free_runner_disk.sh). Some runs lost the runner
outright and kept no log (38095061154). The last run that reached market-data was 37383124815 (2026-10-05 22:32Z),
so no DATA_PLAYER_V4 / V5 projection record is newer than that.

These tests walk the workflow's steps in order and track the full market-data checkouts on disk, the same way the
runner fills up, so they fail on the pre-fix workflow and pass on the fixed one.
"""
import os
import re

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW = os.path.join(ROOT, ".github", "workflows", "shadow-v2-project.yml")
PUBLISHER_WT = "_market_data_wt"          # publish_market_data.py: os.path.join(dirname(repo), "_market_data_wt")
# Commands that run scripts/ci/publish_market_data.py, which first replaces its own checkout and then adds one.
PUBLISH_CALLS = ("scripts/ci/publish_market_data.py", "scripts/shadow_v2/publish_vintages.py")


def _steps():
    with open(WORKFLOW) as f:
        doc = yaml.safe_load(f)
    return doc["jobs"]["project"]["steps"]


def _commands(step):
    """The shell commands of a step: comment lines dropped, continuation lines joined, `&&` chains split."""
    text = re.sub(r"\\\n\s*", " ", step.get("run") or "")
    out = []
    for line in text.splitlines():
        if line.strip().startswith("#"):
            continue
        out.extend(c.strip() for c in line.split("&&") if c.strip())
    return out


def _worktree_add_path(cmd):
    """The path of a FULL `git worktree add ... origin/market-data`, or None (a --no-checkout one costs ~nothing)."""
    if "git worktree add" not in cmd or "origin/market-data" not in cmd or "--no-checkout" in cmd:
        return None
    return [a for a in cmd.split()[3:] if not a.startswith("-")][0]


def _removed_path(cmd):
    """`rm -rf X` / `git worktree remove [--force] X` (the command before any `|| fallback`) -> X, else None."""
    head = cmd.split("||")[0].strip().split()
    if head[:2] == ["rm", "-rf"] or head[:3] == ["git", "worktree", "remove"]:
        args = [a for a in head[2:] if not a.startswith("-") and a != "remove"]
        return args[0] if args else None
    return None


def simulate():
    """Walk the job's steps in order. For every publisher call: how many full market-data checkouts are on disk
    while it runs. Also fails if a step reads a checkout after it was removed."""
    live, removed, peaks = set(), set(), []
    freed_before_fetch, fetched = None, False
    for step in _steps():
        for cmd in _commands(step):
            if "free_runner_disk.sh" in cmd and freed_before_fetch is None:
                freed_before_fetch = not fetched
            if "git fetch" in cmd and "market-data" in cmd:
                fetched = True
            gone, add = _removed_path(cmd), _worktree_add_path(cmd)
            if gone:
                if gone in live:
                    live.discard(gone)
                    removed.add(gone)
                continue
            for p in removed:
                assert p not in cmd or p == add, f"step {step.get('name')!r} reads {p} after removing it: {cmd}"
            if add:
                live.add(add)
                removed.discard(add)
            if any(c in cmd for c in PUBLISH_CALLS):
                during = len(live - {PUBLISHER_WT}) + 1     # it rmtree()s its old checkout, then adds a full one
                peaks.append((step.get("name"), cmd, during, step.get("continue-on-error", False)))
                live.add(PUBLISHER_WT)                      # and leaves it on disk afterwards
    return peaks, freed_before_fetch


def _final_publish(peaks):
    finals = [p for p in peaks if "publish_market_data.py --src data/shadow/v2" in p[1]]
    assert len(finals) == 1, f"expected exactly one projection publish, found {len(finals)}"
    return finals[0]


def test_the_projection_publish_never_needs_two_full_market_data_checkouts():
    name, cmd, during, _ = _final_publish(simulate()[0])
    assert during == 1, (
        f"{name!r} runs with {during} full market-data checkouts on the runner at once; two no longer fit "
        "(No space left on device, runs 37422242678 .. 38165258720). Remove /tmp/md before publishing.")


def test_the_projection_publish_still_fails_loudly():
    """The fix makes the publish fit; it must not make a failed publish look green."""
    _, _, _, soft = _final_publish(simulate()[0])
    assert soft is False


def test_the_job_frees_runner_disk_before_the_market_data_worktree():
    _, freed_before_fetch = simulate()
    assert freed_before_fetch is True


def test_the_vintages_are_published_while_tmp_md_still_exists():
    """publish_vintages.py reads /tmp/md to recognise content already published (a vintage is never re-dated), so
    the scratch checkout may only go after it."""
    peaks, _ = simulate()
    vint = [p for p in peaks if "publish_vintages.py --market-data /tmp/md" in p[1]]
    assert len(vint) == 1 and peaks.index(vint[0]) < peaks.index(_final_publish(peaks))


def test_the_job_timeout_leaves_room_for_the_publish():
    """Runs reach the final publish ~46 min in (38165258720: 45.3 min) and the last green run took 49.5 min
    (37383124815). The fix adds the disk step, the /tmp/md removal and a vintage publish that now succeeds, so the
    old 60-minute limit would turn the disk failure into a timeout (38075890276, 38028268249 already read as
    TIMED_OUT: a runner out of disk hangs in the publish step until the limit)."""
    with open(WORKFLOW) as f:
        job = yaml.safe_load(f)["jobs"]["project"]
    assert job["timeout-minutes"] >= 75
