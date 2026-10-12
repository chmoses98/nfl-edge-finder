"""`publish_market_data.py --sparse`: publish a folder without materialising the whole market-data branch.

market-data holds ~52 GB in ~81k files (2026-10). The default publisher checks the whole branch out into its own
worktree; in a job that fetched market-data blobless (the PURE shadow collector, scripts/shadow_pure/
checkout_market_data.sh) that checkout lazily downloads every blob and cannot finish inside the job's timeout.
`--sparse` checks out only `--src`, so the publish costs what it adds -- and still rebases and retries on a race.
"""
from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLISHER = os.path.join(ROOT, "scripts", "ci", "publish_market_data.py")


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True, check=True)


def _setup(tmp_path):
    origin, repo, other = tmp_path / "origin.git", tmp_path / "repo", tmp_path / "other"
    subprocess.run(["git", "init", "-q", "--bare", str(origin)], check=True)
    git("config", "uploadpack.allowFilter", "true", cwd=origin)
    git("config", "uploadpack.allowAnySHA1InWant", "true", cwd=origin)
    subprocess.run(["git", "clone", "-q", str(origin), str(other)], check=True)
    for k, v in (("user.name", "t"), ("user.email", "t@e"), ("commit.gpgsign", "false")):
        git("config", k, v, cwd=other)
    (other / "seed").write_text("seed\n")
    git("add", "-A", cwd=other)
    git("commit", "-q", "-m", "seed", cwd=other)
    git("branch", "-M", "main", cwd=other)
    git("push", "-q", "-u", "origin", "main", cwd=other)
    git("checkout", "-q", "-b", "market-data", cwd=other)
    big = other / "data" / "kalshi" / "capture"
    big.mkdir(parents=True)
    (big / "quotes.jsonl").write_text("x" * 200_000)
    old = other / "data" / "shadow_pure" / "nfl" / "manifests"
    old.mkdir(parents=True)
    (old / "a.manifest.json").write_text("{}\n")
    git("add", "-A", cwd=other)
    git("commit", "-q", "-m", "market data", cwd=other)
    git("push", "-q", "origin", "market-data", cwd=other)
    subprocess.run(["git", "clone", "-q", "-b", "main", f"file://{origin}", str(repo)], check=True)
    for k, v in (("user.name", "t"), ("user.email", "t@e"), ("commit.gpgsign", "false")):
        git("config", k, v, cwd=repo)
    src = repo / "data" / "shadow_pure" / "nfl" / "projections"
    src.mkdir(parents=True)
    (src / "run1.jsonl.gz").write_bytes(b"new")
    return origin, repo, other


def test_sparse_publish_adds_only_new_files_without_checking_out_the_rest(tmp_path):
    origin, repo, _other = _setup(tmp_path)
    r = subprocess.run([sys.executable, PUBLISHER, "--src", "data/shadow_pure", "--message", "pure", "--sparse"],
                       cwd=repo, text=True, capture_output=True)
    assert r.returncode == 0, r.stdout + r.stderr
    wt = tmp_path / "_market_data_wt"
    on_disk = {os.path.relpath(os.path.join(d, f), wt) for d, _s, fs in os.walk(wt) if ".git" not in d for f in fs}
    assert not any(p.startswith("data/kalshi") for p in on_disk), on_disk     # never materialised
    tree = git("ls-tree", "-r", "--name-only", "market-data", cwd=origin).stdout.split()
    assert {"data/kalshi/capture/quotes.jsonl", "data/shadow_pure/nfl/manifests/a.manifest.json",
            "data/shadow_pure/nfl/projections/run1.jsonl.gz"} <= set(tree)
    changed = git("diff", "--name-status", "market-data~1", "market-data", cwd=origin).stdout.split("\n")
    assert [c for c in changed if c] == ["A\tdata/shadow_pure/nfl/projections/run1.jsonl.gz"]


def test_sparse_publish_retries_a_push_race_and_keeps_the_other_writer(tmp_path):
    origin, repo, other = _setup(tmp_path)
    marker = origin / "raced-once"
    hook = origin / "hooks" / "pre-receive"
    hook.parent.mkdir(exist_ok=True)
    (other / "data" / "kalshi" / "capture" / "racer.jsonl").write_text("racer\n")
    git("add", "-A", cwd=other)
    git("commit", "-q", "-m", "racer", cwd=other)
    git("push", "-q", "origin", "HEAD:refs/heads/racer", cwd=other)
    # the first push loses the ref to a concurrent writer (moved from outside the push quarantine)
    hook.write_text("#!/bin/sh\n"
                    f"if [ ! -e '{marker}' ]; then\n  touch '{marker}'\n"
                    "  env -u GIT_QUARANTINE_PATH -u GIT_OBJECT_DIRECTORY -u GIT_ALTERNATE_OBJECT_DIRECTORIES \\\n"
                    "      git update-ref refs/heads/market-data refs/heads/racer\nfi\nexit 0\n")
    hook.chmod(0o755)
    r = subprocess.run([sys.executable, PUBLISHER, "--src", "data/shadow_pure", "--message", "pure", "--sparse"],
                       cwd=repo, text=True, capture_output=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert marker.exists(), "the race was never staged"
    tree = set(git("ls-tree", "-r", "--name-only", "market-data", cwd=origin).stdout.split())
    assert {"data/kalshi/capture/racer.jsonl", "data/shadow_pure/nfl/projections/run1.jsonl.gz"} <= tree
