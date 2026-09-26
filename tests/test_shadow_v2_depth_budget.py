"""The depth sweep's request budget must finish, publish included, inside the job limit.

Runs 36256548555 and 36266598972 timed out at 40 minutes: 5000 requests at 3 req/s (~28 min) plus the
market-data fetch and publish. A timeout loses the whole sweep, because publishing is the last step."""
import os

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_the_default_budget_at_the_configured_rate_leaves_room_for_fetch_and_publish():
    wf = yaml.safe_load(open(os.path.join(ROOT, ".github", "workflows", "shadow-v2-depth.yml")))
    job = wf["jobs"]["depth"]
    sweep = next(s for s in job["steps"] if "capture_depth_v2.py" in (s.get("run") or ""))["run"]
    budget = int(sweep.split("github.event.inputs.budget || ")[1].split(" ")[0].rstrip("}"))
    rps = float(sweep.split("--rps ")[1].split()[0])
    assert int(wf[True]["workflow_dispatch"]["inputs"]["budget"]["default"]) == budget
    fetch_and_publish_min = 12
    assert budget / rps / 60 + fetch_and_publish_min <= int(job["timeout-minutes"]) - 5
