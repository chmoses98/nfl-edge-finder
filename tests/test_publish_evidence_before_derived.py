"""A rejected push is not a publication, and a derived file must never be able to block the evidence.

Run 35681158381 settled all fourteen 2026 week-2 Sunday games, wrote 413,128 immutable settlement rows, paired
1,227,994 closes -- and published none of it, while reporting success:

    + git commit -q -m shadow v2 settlements 20260922T025718Z (413128 records) + closes 1227994
    push failed:  information.
    remote: error: File data/shadow/v2/research/2026_wk02.research.jsonl.gz is 160.92 MB; this exceeds
    remote: error: GitHub's file size limit of 100.00 MB
    ! [remote rejected]   market-data -> market-data (pre-receive hook declined)
    + git fetch origin market-data
    + git add -A -- data/shadow/v2
    no changes to publish

Three separate defects in those nine lines, and these tests pin all three:

  1. THE EVIDENCE RODE WITH THE DERIVED FILE. One commit carried both, so a derived, rebuildable export that
     had outgrown the remote's file limit took the week's write-once settlement evidence down with it.
  2. THE RESEARCH EXPORT HAD NO SIZE CEILING. One file per week, 88.6 MB through week 1, 160.92 MB once the
     Sunday slate was settled. Nothing in the pipeline knew 100 MB existed.
  3. THE PUBLISHER CALLED A REJECTED PUSH A SUCCESS. On the retry the commit was already made, so `git add`
     staged nothing, and the "nothing to do" early return fired on a branch sitting on an unpushed commit.
     The step exited 0 and the job went green with the corpus unchanged.
"""
from __future__ import annotations

import gzip
import json
import os
import subprocess
import sys

import pytest
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.evaluation import research_parts as RP                                     # noqa: E402

PUBLISHER = os.path.join(ROOT, "scripts", "ci", "publish_market_data.py")


def load_publisher():
    import importlib.util
    spec = importlib.util.spec_from_file_location("_publish_market_data", PUBLISHER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------ 1. the workflow publishes evidence first
def workflow():
    return yaml.safe_load(open(os.path.join(ROOT, ".github", "workflows", "shadow-v2-settle.yml")))


def step_names():
    return [s.get("name") for s in workflow()["jobs"]["settle"]["steps"]]


def test_the_immutable_batches_are_published_before_the_derived_rebuild():
    names = step_names()
    closes = next(i for i, n in enumerate(names) if n and n.startswith("Pair every kicked-off"))
    evidence = next(i for i, n in enumerate(names) if n and n.startswith("Publish the settlement"))
    research = next(i for i, n in enumerate(names) if n and n.startswith("Rebuild the research export"))
    assert closes < evidence < research, (
        "the settlement and close batches must be published BEFORE the research export is rebuilt; "
        f"order is {names}")


def test_the_derived_artifacts_are_published_in_their_own_step():
    steps = {s.get("name"): s for s in workflow()["jobs"]["settle"]["steps"]}
    derived = steps["Publish the research export, scorecard v3 and weekly report"]
    assert "steps.research.outcome" in derived["if"], derived["if"]
    evidence = steps["Publish the settlement, close and CLV batches, autopsies and scorecard"]
    # the evidence gate still keys off what the settle/closes drivers actually wrote, and nothing else
    assert "steps.settle.outputs.status" in evidence["if"] and "steps.closes.outputs.status" in evidence["if"]
    assert "research" not in evidence["if"], "the evidence publish must not depend on the derived rebuild"


# ------------------------------------------------------------------ 2. no published file exceeds the limit
def test_part_one_keeps_the_historical_name_so_published_weeks_are_not_renamed():
    assert RP.part_path("/r", "2026_wk02", "jsonl.gz", 1) == "/r/2026_wk02.research.jsonl.gz"
    assert RP.part_path("/r", "2026_wk02", "jsonl.gz", 2) == "/r/2026_wk02.research.part02.jsonl.gz"
    assert RP.part_path("/r", "2026_wk02", "parquet", 3) == "/r/2026_wk02.research.part03.parquet"


def test_a_week_written_before_the_split_still_reads_as_one_part(tmp_path):
    gzip.open(tmp_path / "2026_wk01.research.jsonl.gz", "wb").close()
    assert RP.parts(str(tmp_path), "2026_wk01", "jsonl.gz") == [str(tmp_path / "2026_wk01.research.jsonl.gz")]


def test_parts_are_returned_in_order_and_part_one_comes_first(tmp_path):
    for n in (1, 2, 3, 10, 11):
        gzip.open(RP.part_path(str(tmp_path), "2026_wk02", "jsonl.gz", n), "wb").close()
    got = [os.path.basename(p) for p in RP.parts(str(tmp_path), "2026_wk02", "jsonl.gz")]
    assert got == ["2026_wk02.research.jsonl.gz", "2026_wk02.research.part02.jsonl.gz",
                   "2026_wk02.research.part03.jsonl.gz", "2026_wk02.research.part10.jsonl.gz",
                   "2026_wk02.research.part11.jsonl.gz"]


def test_the_rolling_writer_splits_and_every_part_stays_under_the_remote_limit(tmp_path):
    """The real shape of the failure: rows that would have made one 160 MB file make several small ones,
    every row survives, and their order is preserved."""
    roll = RP.RollingWriter(str(tmp_path), "2026_wk02", "jsonl.gz",
                            open_part=lambda p: gzip.GzipFile(p, "wb", mtime=0),
                            close_part=lambda w: w.close(), budget=64 * 1024)
    import random
    rnd = random.Random(7)
    written = []
    for i in range(4000):
        # incompressible padding, so the part sizes on disk are what the budget is actually measuring
        row = {"record_id": f"r{i:05d}", "pad": "".join(rnd.choices("0123456789abcdef", k=300))}
        roll.w.write((json.dumps(row) + "\n").encode())
        written.append(row["record_id"])
        if i % 50 == 0:
            roll.maybe_roll()
    paths = roll.close()
    assert len(paths) > 1, "the budget should have forced a split"
    assert not RP.oversized(paths)
    assert all(os.path.getsize(p) < RP.GITHUB_FILE_LIMIT_BYTES for p in paths)
    read = [json.loads(l)["record_id"] for p in RP.parts(str(tmp_path), "2026_wk02", "jsonl.gz")
            for l in gzip.open(p, "rt") if l.strip()]
    assert read == written, "every row must survive the split, in order"


def test_the_parquet_sink_rolls_between_row_groups_and_keeps_every_row(tmp_path):
    """The parquet has no flush() and writes a row group straight to the file, so the same rolling rule has to
    work off a different writer entirely. 45 MB through week 1 and 77 MB after week 2: it is on the same path
    to the limit as the ndjson, just a week behind."""
    pa = pytest.importorskip("pyarrow")
    pq = pytest.importorskip("pyarrow.parquet")
    import random
    rnd = random.Random(11)
    schema = pa.schema([("record_id", pa.string()), ("pad", pa.string())])
    roll = RP.RollingWriter(str(tmp_path), "2026_wk02", "parquet",
                            open_part=lambda p: pq.ParquetWriter(p, schema),
                            close_part=lambda w: w.close(), budget=64 * 1024)
    written = []
    for g in range(12):
        rows = [{"record_id": f"r{g:02d}_{i:04d}", "pad": "".join(rnd.choices("0123456789abcdef", k=300))}
                for i in range(500)]
        roll.w.write_table(pa.Table.from_pylist(rows, schema=schema))
        written += [r["record_id"] for r in rows]
        roll.maybe_roll()
    paths = roll.close()
    assert len(paths) > 1, "the budget should have forced a split"
    assert not RP.oversized(paths)
    read = [v for p in RP.parts(str(tmp_path), "2026_wk02", "parquet")
            for v in pq.read_table(p).column("record_id").to_pylist()]
    assert read == written


def test_the_budget_leaves_real_headroom_under_the_hard_limit():
    """160.92 MB against a 100 MB limit is what this exists to prevent; a budget near the limit would not."""
    assert RP.PART_BUDGET_BYTES < RP.GITHUB_FILE_LIMIT_BYTES / 2
    assert RP.GITHUB_FILE_LIMIT_BYTES == 100 * 1024 * 1024


def test_oversized_names_the_file_a_remote_would_refuse(tmp_path):
    small, big = tmp_path / "a.gz", tmp_path / "b.gz"
    small.write_bytes(b"x")
    big.write_bytes(b"x" * RP.GITHUB_FILE_LIMIT_BYTES)
    assert RP.oversized([str(small), str(big)]) == [str(big)]


# ------------------------------------------------------------------ 3. a rejected push is never a success
def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True, check=True)


@pytest.fixture
def origin_and_repo(tmp_path):
    """A real bare remote and a real clone, so the publisher's git usage is exercised, not imitated.

    The clone stays on `main` and `market-data` lives only on the remote, exactly as it does on a runner: the
    publisher checks the data branch out into its OWN worktree, and git refuses that if the branch is already
    checked out somewhere else.
    """
    origin, repo = tmp_path / "origin.git", tmp_path / "repo"
    subprocess.run(["git", "init", "-q", "--bare", str(origin)], check=True)
    subprocess.run(["git", "clone", "-q", str(origin), str(repo)], check=True)
    for k, v in (("user.name", "t"), ("user.email", "t@e"), ("commit.gpgsign", "false")):
        git("config", k, v, cwd=repo)
    (repo / "seed").write_text("seed\n")
    git("add", "-A", cwd=repo)
    git("commit", "-q", "-m", "seed", cwd=repo)
    git("branch", "-M", "main", cwd=repo)
    git("push", "-q", "-u", "origin", "main", cwd=repo)
    git("push", "-q", "origin", "main:market-data", cwd=repo)
    src = repo / "data" / "shadow" / "v2"
    src.mkdir(parents=True)
    (src / "settlements.txt").write_text("413128 rows\n")
    return origin, repo


def run_publisher(repo, *, extra=()):
    r = subprocess.run([sys.executable, PUBLISHER, "--src", "data/shadow/v2", "--message", "publish", *extra],
                       cwd=repo, text=True, capture_output=True)
    return r


def test_a_clean_publish_reaches_the_remote(origin_and_repo):
    origin, repo = origin_and_repo
    r = run_publisher(repo)
    assert r.returncode == 0, r.stdout + r.stderr
    listed = subprocess.run(["git", "ls-tree", "-r", "--name-only", "market-data"], cwd=origin,
                            text=True, capture_output=True).stdout
    assert "data/shadow/v2/settlements.txt" in listed


def test_a_rerun_with_nothing_new_is_a_no_op_and_still_succeeds(origin_and_repo):
    _origin, repo = origin_and_repo
    assert run_publisher(repo).returncode == 0
    r = run_publisher(repo)
    assert r.returncode == 0 and "no changes to publish" in r.stdout


def test_a_push_the_remote_refuses_fails_the_step_instead_of_reporting_success(origin_and_repo):
    """THE REGRESSION. A pre-receive hook rejects the push, exactly as GitHub's 100 MB check did. The publisher
    must exit non-zero: a green step over an unchanged corpus is how a whole Sunday slate went missing."""
    origin, repo = origin_and_repo
    hook = origin / "hooks" / "pre-receive"
    hook.parent.mkdir(exist_ok=True)
    hook.write_text("#!/bin/sh\n"
                    "echo 'remote: error: File data/shadow/v2/research/2026_wk02.research.jsonl.gz is 160.92 MB;"
                    " this exceeds GitHub'\\''s file size limit of 100.00 MB' >&2\n"
                    "echo 'remote: error: GH001: Large files detected.' >&2\n"
                    "exit 1\n")
    hook.chmod(0o755)
    r = run_publisher(repo, extra=("--attempts", "2"))
    assert r.returncode != 0, f"a rejected push reported success:\n{r.stdout}"
    assert "no changes to publish" not in r.stdout, "the rejected commit was mistaken for nothing to do"
    assert "100" in r.stdout or "file size" in r.stdout.lower() or "REFUSED" in r.stdout
    # and the remote really is unchanged, which is what the exit code now tells the truth about
    listed = subprocess.run(["git", "ls-tree", "-r", "--name-only", "market-data"], cwd=origin,
                            text=True, capture_output=True).stdout
    assert "data/shadow/v2/settlements.txt" not in listed


def test_a_hopeless_rejection_is_not_retried_eight_times(origin_and_repo):
    """A racing publisher is worth retrying; a file the server will not accept is not."""
    mod = load_publisher()
    assert mod.rejected_for_good("remote: error: GH001: Large files detected.")
    assert mod.rejected_for_good("! [remote rejected] market-data (pre-receive hook declined)")
    assert mod.rejected_for_good("File x is 160.92 MB; this exceeds GitHub's file size limit of 100.00 MB")
    # a genuine race must still be retried
    assert mod.rejected_for_good("Updates were rejected because the remote contains work that you do not have") is None
    assert mod.rejected_for_good("") is None


def test_unpushed_counts_the_commits_the_remote_does_not_have(origin_and_repo):
    _origin, repo = origin_and_repo
    mod = load_publisher()
    assert mod.unpushed(str(repo), "main") == 0
    (repo / "another").write_text("x\n")
    git("add", "-A", cwd=repo)
    git("commit", "-q", "-m", "local only", cwd=repo)
    assert mod.unpushed(str(repo), "main") == 1, "an unpushed commit must never read as nothing to publish"
