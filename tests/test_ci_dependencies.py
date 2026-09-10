"""`requirements-test.txt` must list everything the suite transitively imports.

The first CI run of this suite passed locally and failed on the runner, twice, for the same class of reason:
a dependency that was present on the development machine and absent in CI. Once for `pyyaml`, imported at
module scope by `test_workflows_parse.py`; once for `pandas`, reached only through
`nfl_edge.research.player_distributions` from INSIDE a test body.

That second one is the dangerous shape. Reading the top of each test file does not find it, and a missing
dependency is not a skip -- it is a failure, or a collection error that takes a whole module's tests with it.
So the requirements file is derived by walking the import graph, and this test re-walks it and fails when the
file falls behind.

Why it matters more here than in most projects: this suite is what keeps every fail-closed gate honest, and
the ledger it protects is immutable. A defective record written while a gate silently went untested is
permanent.
"""
import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Packages that are not in the standard library and are not this project. Anything here that the graph
# reaches must appear in requirements-test.txt.
THIRD_PARTY = {"pandas", "numpy", "polars", "scipy", "pyarrow", "duckdb", "sklearn", "statsmodels",
               "yaml", "pytest"}
# pip name where it differs from the import name.
PIP_NAME = {"yaml": "pyyaml", "sklearn": "scikit-learn"}

LOCAL_ROOTS = ("nfl_edge", "scripts")


def _module_file(dotted: str) -> str | None:
    p = os.path.join(ROOT, dotted.replace(".", "/") + ".py")
    return p if os.path.exists(p) else None


def _package_files(dotted: str) -> list:
    d = os.path.join(ROOT, dotted.replace(".", "/"))
    if not os.path.isdir(d):
        return []
    return [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith(".py")]


def _precise_files(dotted: str, subnames) -> list:
    """Only the modules `from <dotted> import <subnames>` actually executes.

    The default walk queues every file in a package, which is the safe over-approximation for a requirements
    file -- installing a package nothing imports costs install time, missing one costs a failed run. It is the
    WRONG answer for "must this workflow install polars", because it charges a stdlib-only script for a
    sibling module it never touches. `scripts/handicap/preflight_airtable.py` imports
    nfl_edge.execution.{depth,quotes} and nothing else in that package, and is provably importable with numpy,
    pandas, polars, scipy and pyarrow all replaced by ImportError stubs.
    """
    f = _module_file(dotted)
    if f:
        return [f]
    d = os.path.join(ROOT, dotted.replace(".", "/"))
    if not os.path.isdir(d):
        return []
    out = [os.path.join(d, "__init__.py")] if os.path.exists(os.path.join(d, "__init__.py")) else []
    for n in subnames:                      # a name that is not a module is a function or class: no new file
        sub = os.path.join(d, n + ".py")
        if os.path.exists(sub):
            out.append(sub)
    return out


def reachable_third_party(roots=None, *, precise: bool = False) -> dict:
    """Third-party package -> the files that pull it in, over the graph rooted at `roots`.

    Defaults to every file in tests/. `tests/test_workflows_parse.py` passes the scripts a workflow invokes
    instead, so the same walk answers "what must CI install for this workflow" as well as "what must
    requirements-test.txt declare".
    """
    seen, found = set(), {}
    queue = list(roots) if roots is not None else [
        os.path.join(ROOT, "tests", f)
        for f in sorted(os.listdir(os.path.join(ROOT, "tests"))) if f.endswith(".py")]

    while queue:
        path = queue.pop()
        if path in seen or not os.path.exists(path):
            continue
        seen.add(path)
        try:
            tree = ast.parse(open(path).read())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names, subnames = [a.name for a in node.names], []
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                names, subnames = [node.module], [a.name for a in node.names]
            else:
                continue
            for name in names:
                top = name.split(".")[0]
                if top in THIRD_PARTY:
                    found.setdefault(top, set()).add(os.path.relpath(path, ROOT))
                elif top in LOCAL_ROOTS:
                    if precise:
                        queue.extend(_precise_files(name, subnames))
                    else:
                        f = _module_file(name)
                        queue.extend([f] if f else _package_files(name))
    return found


def declared() -> set:
    with open(os.path.join(ROOT, "requirements-test.txt")) as f:
        return {line.split("==")[0].split(">=")[0].strip().lower()
                for line in f if line.strip() and not line.startswith("#")}


def test_every_transitively_imported_package_is_declared():
    have = declared()
    missing = []
    for pkg, sources in sorted(reachable_third_party().items()):
        pip = PIP_NAME.get(pkg, pkg)
        if pip.lower() not in have:
            missing.append(f"{pip} (imported by {', '.join(sorted(sources)[:3])})")
    assert not missing, (
        "requirements-test.txt is missing packages the suite transitively imports, so CI will fail on them "
        "rather than skip them:\n  " + "\n  ".join(missing))


def test_the_requirements_file_does_not_carry_packages_the_suite_never_uses():
    """A dependency nobody imports is install time spent on nothing, and a claim that stops being true."""
    reachable = {PIP_NAME.get(p, p).lower() for p in reachable_third_party()}
    extra = sorted(declared() - reachable)
    assert not extra, f"requirements-test.txt lists unused packages: {extra}"


def test_the_hardening_modules_stay_stdlib_only():
    """The real-money path must never be blocked by a package resolution failure.

    schema, gates, quotes, fees, risk, store and the bridge are the modules that decide whether a bet is
    allowed to become canonical. They import nothing outside the standard library, so no dependency problem
    on any machine can be the reason a gate did not run.
    """
    modules = ["nfl_edge/handicap/schema.py", "nfl_edge/handicap/gates.py", "nfl_edge/handicap/risk.py",
               "nfl_edge/handicap/store.py", "nfl_edge/handicap/airtable_bridge.py",
               "nfl_edge/handicap/evaluate.py", "nfl_edge/handicap/scorecard.py",
               "nfl_edge/execution/quotes.py", "nfl_edge/execution/fees.py"]
    offenders = []
    for rel in modules:
        tree = ast.parse(open(os.path.join(ROOT, rel)).read())
        for node in ast.walk(tree):
            names = ([a.name for a in node.names] if isinstance(node, ast.Import)
                     else [node.module] if isinstance(node, ast.ImportFrom) and node.module else [])
            for name in names:
                if name.split(".")[0] in THIRD_PARTY:
                    offenders.append(f"{rel} imports {name}")
    assert not offenders, (
        "the real-money decision path gained a third-party dependency: " + "; ".join(offenders))


def test_every_declared_package_actually_imports_here():
    """A sanity check on the running environment, so a local pass means the same as a CI pass."""
    import importlib
    reverse = {v: k for k, v in PIP_NAME.items()}
    for pip in sorted(declared()):
        importlib.import_module(reverse.get(pip, pip))
