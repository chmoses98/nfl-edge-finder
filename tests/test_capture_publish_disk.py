"""Regression: NFL capture must not materialize the entire market-data branch.

On 2026-11-01 conductors repeatedly filled the hosted runner's disk while
checking out ~111k paths, leaving the last successful Kalshi capture on 10/28.
A new ledger from an old capture is not a recovery. This test protects the
physical data publishing path, not just a README promise.
"""
import os
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def steps(filename):
    path = os.path.join(ROOT, ".github", "workflows", filename)
    with open(path) as f:
        doc = yaml.safe_load(f)
    job = doc["jobs"]["conduct" if filename == "kalshi-conductor.yml" else "capture"]
    return "\n".join(step.get("run") or "" for step in job["steps"])


def test_conductor_fetches_blobless_and_publishes_only_capture_subtree():
    body = steps("kalshi-conductor.yml")
    assert "git fetch --depth=1 --filter=blob:none origin market-data" in body
    assert "publish_market_data.py --src data/kalshi/capture --sparse" in body
    assert "git worktree add -f" not in body
    assert '|| echo "::warning::publish failed' not in body
    assert "capture publish failed on pass" in body and "exit 1" in body


def test_manual_capture_uses_the_same_disk_safe_publisher():
    body = steps("kalshi-capture.yml")
    assert "git fetch --depth=1 --filter=blob:none origin market-data" in body
    assert "publish_market_data.py --src data/kalshi/capture --sparse" in body


def test_existing_publisher_still_uses_blobless_no_checkout_for_sparse_publishing():
    publisher = open(os.path.join(ROOT, "scripts", "ci", "publish_market_data.py")).read()
    assert '"--sparse"' in publisher
    assert '"--filter=blob:none"' in publisher
    assert '"--no-checkout"' in publisher
    assert '"sparse-checkout"' in publisher
