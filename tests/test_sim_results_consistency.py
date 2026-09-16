"""A committed result summary must not be able to disagree with the committed data.

RESULTS.md once carried reconciliation numbers from an earlier touchdown-relocation implementation while
RECONCILIATION.md and reconciliation_weights.json carried the corrected, much smaller weights.  Both were
committed.  So the markdown is now a pure render of the JSON and this test re-renders and compares.
"""
import importlib.util
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
OUT = os.path.join(ROOT, "research", "simulation_engine")
_spec = importlib.util.spec_from_file_location("sim_write_results", os.path.join(ROOT, "scripts", "sim", "write_results.py"))
W = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(W)


@pytest.mark.parametrize("name", W.FILES)
def test_the_committed_summary_is_exactly_what_the_json_renders(name):
    rendered = W.render_all()
    if name not in rendered:
        pytest.skip(f"{name}'s source JSON is not in this checkout")
    path = os.path.join(OUT, name)
    assert os.path.exists(path), f"{name} has source JSON but was not rendered into the repo"
    assert open(path).read() == rendered[name], (
        f"{name} disagrees with its source JSON. Regenerate it: python scripts/sim/write_results.py")


def test_the_deployed_weights_in_the_markdown_are_the_weights_in_the_json():
    """The one number that actually changes behaviour, checked without going through the renderer."""
    import json
    wpath = os.path.join(OUT, "reconciliation_weights.json")
    mpath = os.path.join(OUT, "RECONCILIATION.md")
    if not (os.path.exists(wpath) and os.path.exists(mpath)):
        pytest.skip("no reconciliation artifacts in this checkout")
    weights = json.load(open(wpath))
    md = open(mpath).read()
    for stat, rec in (weights.get("fitted") or {}).items():
        w = rec.get("weight")
        assert f"**{w:.2f}**" in md, f"{stat}'s deployed weight {w} does not appear in RECONCILIATION.md"


def test_every_nonzero_weight_names_a_confirmation():
    import json
    wpath = os.path.join(OUT, "reconciliation_weights.json")
    if not os.path.exists(wpath):
        pytest.skip("no weights in this checkout")
    for stat, rec in (json.load(open(wpath)).get("fitted") or {}).items():
        if (rec.get("weight") or 0) > 0:
            assert rec.get("confirm") and rec["confirm"].get("z") is not None, \
                f"{stat} deploys a non-zero weight with no later-week confirmation recorded"
