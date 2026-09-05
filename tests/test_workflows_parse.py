"""Every workflow file must parse.

shadow-price.yml carried an inline `python3 -c` heredoc whose continuation lines sat at column 0 inside a
YAML block scalar. The file was unparseable and 36 consecutive scheduled runs failed instantly -- the live
shadow pricing this project depends on had not run at all since it was introduced. Nothing in the test suite
looked at workflow files, so nothing caught it. This does.
"""
import glob
import os

import pytest
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOWS = sorted(glob.glob(os.path.join(ROOT, ".github", "workflows", "*.yml")))


def test_there_are_workflows_to_check():
    assert WORKFLOWS, "no workflow files found"


@pytest.mark.parametrize("path", WORKFLOWS, ids=[os.path.basename(p) for p in WORKFLOWS])
def test_workflow_parses(path):
    with open(path) as f:
        doc = yaml.safe_load(f)
    assert isinstance(doc, dict), f"{os.path.basename(path)} did not parse to a mapping"
    assert "jobs" in doc and doc["jobs"], f"{os.path.basename(path)} declares no jobs"


@pytest.mark.parametrize("path", WORKFLOWS, ids=[os.path.basename(p) for p in WORKFLOWS])
def test_no_inline_python_heredoc_in_run_blocks(path):
    """`python3 -c "` followed by unindented lines is what broke shadow-price.yml. Call a script instead."""
    src = open(path).read()
    assert 'python3 -c "' not in src, (
        f"{os.path.basename(path)} embeds a multi-line python -c heredoc in a YAML block scalar; "
        "put the code in scripts/ and call the file")
