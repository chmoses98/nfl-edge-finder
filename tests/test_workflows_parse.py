"""Every workflow file must parse.

shadow-price.yml carried an inline `python3 -c` heredoc whose continuation lines sat at column 0 inside a
YAML block scalar. The file was unparseable and 36 consecutive scheduled runs failed instantly -- the live
shadow pricing this project depends on had not run at all since it was introduced. Nothing in the test suite
looked at workflow files, so nothing caught it. This does.
"""
import glob
import re
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


def _run_blocks(doc):
    for job in (doc.get("jobs") or {}).values():
        for step in (job.get("steps") or []):
            run = step.get("run")
            if run:
                yield step.get("name", "<unnamed>"), run


_SCRIPT_RE = re.compile(r"python3?\s+((?:scripts|nfl_edge)/[\w./-]+\.py)")


@pytest.mark.parametrize("path", WORKFLOWS, ids=[os.path.basename(p) for p in WORKFLOWS])
def test_referenced_scripts_exist(path):
    """A workflow that calls a script that was renamed or never committed fails only at run time.

    The heredoc bug hid behind exactly this: the extracted script had to exist for the fix to be real.
    """
    with open(path) as f:
        doc = yaml.safe_load(f)
    missing = []
    for name, run in _run_blocks(doc):
        for script in _SCRIPT_RE.findall(run):
            if not os.path.exists(os.path.join(ROOT, script)):
                missing.append(f"step {name!r} calls missing {script}")
    assert not missing, f"{os.path.basename(path)}: " + "; ".join(missing)


def test_shadow_price_does_not_pin_a_stale_model_version():
    """The dispatch input defaulted to shadow-0.2.0 while the pricer default was shadow-0.4.0, so every
    manual run would have stamped the immutable ledger with a version two releases stale. Blank means the
    pricer decides, in one place."""
    path = os.path.join(ROOT, ".github", "workflows", "shadow-price.yml")
    with open(path) as f:
        doc = yaml.safe_load(f)
    on = doc.get(True, doc.get("on"))
    default = ((on["workflow_dispatch"] or {}).get("inputs") or {})["model_version"].get("default")
    assert not default, (
        f"model_version dispatch default is {default!r}; leave it blank so scripts/shadow/price_slate.py "
        "MODEL_VERSION_DEFAULT is the single source of truth")
