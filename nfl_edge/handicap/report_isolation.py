"""Static proof that the RUN NFL report path never touches Airtable, preflight or the recommendation ledger.

The whole architecture rests on one separation:

    RUN NFL          unlimited, read-only research. Evidence. No money, no Airtable, no automation runs.
    PREFLIGHT NFL    explicit real-money candidate validation. That is where Airtable begins.

A separation that is only a convention decays. Someone adds a convenient "log the run to Airtable" call to a
shared helper, the report path imports that helper, and now every two-hourly research build burns Airtable
automation runs and can write to the base. So the separation is a test: walk the import graph from each
entry point of the report path and assert that nothing reachable knows what Airtable is.

Used by `tests/test_run_nfl_isolation.py` and by `scripts/ci/assert_no_airtable.py`, which runs the same
check inside the workflow so the proof appears in the log of every report run.
"""
from __future__ import annotations

import ast
import os
import re

# Entry points that make up the report path.
REPORT_ENTRY_POINTS = [
    "scripts/handicap/run_nfl.py",
    "scripts/handicap/build_report.py",
    "scripts/handicap/resolve_active_week.py",
    "scripts/handicap/horizon_gate.py",
    "scripts/handicap/mark_horizons.py",
    "scripts/ci/publish_handicap_report.py",
]

LOCAL_ROOTS = ("nfl_edge", "scripts")

# Modules the report path must never reach. Reaching one is not itself a call, but it is the only way a call
# can happen, so the import is the line worth defending.
FORBIDDEN_MODULES = {
    "nfl_edge.handicap.airtable_bridge",
    "nfl_edge.handicap.preflight",
    "nfl_edge.handicap.approval",
    "nfl_edge.handicap.risk",
    "nfl_edge.handicap.gates",
    "nfl_edge.handicap.store",
}

# Names of scripts the report path must never shell out to.
FORBIDDEN_SCRIPTS = (
    "preflight_airtable.py", "preflight_candidate.py", "sync_airtable.py",
    "validate_recommendations.py",
)

# Executable tells, checked against real code only -- string literals that are not docstrings, and
# identifiers. Prose is deliberately exempt: `render.py` tells the handicapper what to do downstream
# ("commit to the handicap-data branch"), which is documentation of a later, separate act, not a call.
_AIRTABLE_ENDPOINT = re.compile(r"api\.airtable\.com")
_AIRTABLE_ENV = re.compile(r"\bAIRTABLE_[A-Z_]+")
_AIRTABLE_WORD = re.compile(r"airtable", re.I)
_PREFLIGHT_STATUS = re.compile(r"PREFLIGHT_REQUESTED|READY_FOR_SYNC")


def _docstring_nodes(tree) -> set:
    """id() of every Constant node that is a module/class/function docstring."""
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", None) or []
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
                    and isinstance(body[0].value.value, str):
                out.add(id(body[0].value))
    return out


def code_violations(rel: str, src: str) -> list:
    """Executable references to Airtable / preflight / the recommendation writers in one file."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    docstrings = _docstring_nodes(tree)
    # A script name is a CALL only inside subprocess/os.exec. `render.py` prints
    # "scripts/handicap/validate_recommendations.py" as guidance to the handicapper for a later, separate
    # act; that is documentation in an output document, not this path invoking the recommendation writer.
    exec_strings = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            dotted = ""
            while isinstance(fn, ast.Attribute):
                dotted = fn.attr + "." + dotted
                fn = fn.value
            if isinstance(fn, ast.Name):
                dotted = fn.id + "." + dotted
            if dotted.startswith(("subprocess.", "os.system", "os.exec", "os.spawn", "os.popen")):
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                        exec_strings.add(id(sub))
    found = []

    def at(node):
        return f"{rel}:{getattr(node, 'lineno', 0)}"

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            # `from nfl_edge.handicap import airtable_bridge` names the forbidden module in the alias, not
            # in `node.module`. Check both, or the most natural way to write the import is the one that
            # slips through.
            names = [node.module] + [f"{node.module}.{al.name}" for al in node.names]
        else:
            names = []
        for name in names:
            if name in FORBIDDEN_MODULES or _AIRTABLE_WORD.search(name):
                found.append(f"{at(node)} imports {name}")

        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docstrings:
            v = node.value
            if _AIRTABLE_ENDPOINT.search(v):
                found.append(f"{at(node)} builds an Airtable API URL ({v[:60]!r})")
            if _AIRTABLE_ENV.search(v):
                found.append(f"{at(node)} names an Airtable credential ({v[:60]!r})")
            if _PREFLIGHT_STATUS.search(v):
                found.append(f"{at(node)} uses a preflight/sync handshake status ({v[:60]!r})")
            if id(node) in exec_strings:
                for script in FORBIDDEN_SCRIPTS:
                    if script in v:
                        found.append(f"{at(node)} shells out to {script}")
        if isinstance(node, ast.Attribute) and _AIRTABLE_WORD.search(node.attr):
            found.append(f"{at(node)} uses attribute {node.attr}")
        if isinstance(node, ast.Name) and _AIRTABLE_WORD.search(node.id):
            found.append(f"{at(node)} uses name {node.id}")
    return found


def _module_file(root: str, dotted: str):
    p = os.path.join(root, dotted.replace(".", "/") + ".py")
    return p if os.path.exists(p) else None


def _package_files(root: str, dotted: str) -> list:
    d = os.path.join(root, dotted.replace(".", "/"))
    if not os.path.isdir(d):
        return []
    return [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith(".py")]


def reachable_modules(root: str, entry_points=None) -> dict:
    """Every project file reachable by import from the report entry points -> who pulled it in."""
    entry_points = entry_points or REPORT_ENTRY_POINTS
    seen, by_importer = set(), {}
    queue = [(os.path.join(root, e), "<entry point>") for e in entry_points]
    while queue:
        path, importer = queue.pop()
        if not os.path.exists(path):
            raise FileNotFoundError(f"report entry point missing: {path}")
        if path in seen:
            continue
        seen.add(path)
        by_importer[os.path.relpath(path, root)] = importer
        try:
            tree = ast.parse(open(path).read())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                names = [node.module]
            else:
                continue
            for name in names:
                if name.split(".")[0] not in LOCAL_ROOTS:
                    continue
                f = _module_file(root, name)
                for nxt in ([f] if f else _package_files(root, name)):
                    queue.append((nxt, os.path.relpath(path, root)))
    return by_importer


def audit(root: str, entry_points=None) -> dict:
    """Return `{"files": [...], "violations": [...]}` for the report path."""
    reached = reachable_modules(root, entry_points)
    violations = []
    for rel, importer in sorted(reached.items()):
        dotted = rel[:-3].replace("/", ".")
        if dotted in FORBIDDEN_MODULES:
            violations.append(f"{rel} is reachable from the report path (imported by {importer})")
        violations.extend(code_violations(rel, open(os.path.join(root, rel)).read()))
    return {"files": sorted(reached), "violations": violations}
