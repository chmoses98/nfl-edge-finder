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


_PIPE_RE = re.compile(r"\|\s*(?:tail|head|grep)\b")


def _shell_has_pipefail(doc, job):
    for scope in (job, doc):
        sh = ((scope.get("defaults") or {}).get("run") or {}).get("shell", "")
        if "pipefail" in sh:
            return True
    return False


@pytest.mark.parametrize("path", WORKFLOWS, ids=[os.path.basename(p) for p in WORKFLOWS])
def test_piped_steps_require_pipefail(path):
    """A step that pipes a script into `tail` reports tail's exit status, not the script's.

    shadow-price.yml run 37 passed all eleven steps in 2m22s having priced nothing: every script it called
    could die and still return 0 through the pipe. A green run that did no work is worse than a red one,
    because nothing prompts anyone to look.
    """
    with open(path) as f:
        doc = yaml.safe_load(f)
    offenders = []
    for job_name, job in (doc.get("jobs") or {}).items():
        if _shell_has_pipefail(doc, job):
            continue
        for step in (job.get("steps") or []):
            run = step.get("run") or ""
            shell = step.get("shell", "")
            if _PIPE_RE.search(run) and "pipefail" not in shell and "pipefail" not in run:
                offenders.append(f"{job_name}/{step.get('name', '<unnamed>')}")
    assert not offenders, (
        f"{os.path.basename(path)}: steps pipe into tail/head/grep without pipefail, so a failing script "
        f"exits 0: {offenders}. Set `defaults: run: shell: bash -eo pipefail {{0}}`")


def test_steps_that_commit_have_a_git_identity_first():
    """`Publish shocks` ran before any `git config user.*` and died with 'Author identity unknown' --
    masked by a `|| echo ::warning::`, so shocks never published and the run still went green."""
    path = os.path.join(ROOT, ".github", "workflows", "shadow-price.yml")
    with open(path) as f:
        doc = yaml.safe_load(f)
    steps = doc["jobs"]["price"]["steps"]
    identity_at = next((i for i, s in enumerate(steps) if "git config user.name" in (s.get("run") or "")),
                       None)
    assert identity_at is not None, "no step configures a git identity"
    publishers = [i for i, s in enumerate(steps) if "publish_market_data" in (s.get("run") or "")]
    assert publishers, "no publishing step found"
    assert identity_at < min(publishers), (
        f"git identity is set at step {identity_at} but the first publish is at step {min(publishers)}")


def test_publish_failures_are_not_swallowed():
    path = os.path.join(ROOT, ".github", "workflows", "shadow-price.yml")
    src = open(path).read()
    assert "|| echo \"::warning::shock publish failed\"" not in src, \
        "a failed shock publish is masked as a warning; losing shocks silently is the failure mode"


def test_download_list_covers_what_the_pipeline_reads():
    """A workflow that runs ids.py must also download ff_playerids.

    ids.py reads data/raw/nflverse/ff_playerids/db_playerids.csv, but the fetch step's `--only` list omitted
    it, so ids.py raised FileNotFoundError on every run. With no pipefail that exception exited 0 and the
    step went green; the crosswalk was simply never rebuilt in CI.
    """
    path = os.path.join(ROOT, ".github", "workflows", "shadow-price.yml")
    with open(path) as f:
        doc = yaml.safe_load(f)
    for job_name, job in doc["jobs"].items():
        runs = [s.get("run") or "" for s in (job.get("steps") or [])]
        if not any("ids.py" in r for r in runs):
            continue
        only = ""
        for r in runs:
            m = re.search(r"nflverse_download\.py\s+--only\s+(\S+)", r)
            if m:
                only = m.group(1)
        assert "ff_playerids" in only.split(","), (
            f"{job_name} runs ids.py but --only is {only!r}; ids.py reads ff_playerids/db_playerids.csv")


def test_system_health_defaults_to_the_published_ledger():
    """`--ledger` must default to the published ledger under --md, not a local scratch directory.

    It previously defaulted to the repo's own gitignored data/shadow/ledger, so running the health report
    against a market-data worktree described the published capture and shocks alongside STALE LOCAL pricing:
    it reported shadow-0.3.0 as the current model on a day when shadow-0.4.0 had been published, and
    undercounted observations by 2,485. A health report that silently mixes two sources is worse than none.
    """
    src = open(os.path.join(ROOT, "scripts", "shadow", "system_health.py")).read()
    assert 'ap.add_argument("--ledger", default=os.path.join(ROOT' not in src, \
        "--ledger must not default to the local repo path"
    assert 'os.path.join(a.md, "data", "shadow", "ledger")' in src, \
        "--ledger should default to the published ledger under --md"


def _installed_packages(doc) -> set:
    """Every package any `pip install` step in the workflow installs."""
    out = set()
    for _, run in _run_blocks(doc):
        for m in re.finditer(r"pip\s+install\s+([^\n|&;]+)", run):
            for tok in m.group(1).split():
                if tok.startswith("-"):
                    continue
                if tok.startswith("requirements") or tok.endswith(".txt"):
                    out.add("*")           # a requirements file: treat as covering everything
                    continue
                out.add(tok.split("==")[0].split(">=")[0].strip().lower())
    return out


@pytest.mark.parametrize("path", WORKFLOWS, ids=[os.path.basename(p) for p in WORKFLOWS])
def test_workflows_install_what_their_scripts_import(path):
    """A workflow that calls a script importing polars, and never installs polars, fails at run time only.

    postgame-settle.yml shipped without an install step. Its first live scheduled run (34438883025) passed the
    gate, downloaded the schedule, the player statistics and the identities, and then died on `import polars`
    inside settle_games.py -- after the cheap part had proved there was a real game waiting to be settled.
    Nothing here looked at the relationship between the scripts a workflow runs and the packages it installs,
    so nothing caught it. Every other workflow that touches the scientific stack already installs it; this
    test is what makes that a rule rather than a habit.

    The walk is transitive on purpose: `settle_games.py` does not import polars itself. It reaches it through
    nfl_edge.settlement.nflverse_results, which is exactly the shape that reading the top of the file misses.
    """
    from test_ci_dependencies import PIP_NAME, reachable_third_party

    with open(path) as f:
        doc = yaml.safe_load(f)

    scripts = sorted({os.path.join(ROOT, s)
                      for _, run in _run_blocks(doc) for s in _SCRIPT_RE.findall(run)
                      if os.path.exists(os.path.join(ROOT, s))})
    if not scripts:
        pytest.skip("this workflow runs no repository scripts")

    installed = _installed_packages(doc)
    if "*" in installed:
        return                             # installs a requirements file; covered by test_ci_dependencies

    missing = []
    for pkg, sources in sorted(reachable_third_party(scripts, precise=True).items()):
        pip = PIP_NAME.get(pkg, pkg)
        if pip.lower() not in installed:
            missing.append(f"{pip} (reached from {', '.join(sorted(sources)[:3])})")
    assert not missing, (
        f"{os.path.basename(path)} runs scripts that import packages it never installs, so the step dies at "
        f"run time with ModuleNotFoundError:\n  " + "\n  ".join(missing))
