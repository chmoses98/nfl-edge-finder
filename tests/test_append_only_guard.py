"""The append-only guard, exercised against real git histories.

`schema.write_record` refuses to overwrite a path, which constrains code that goes through it and nothing
else. A `git commit --amend`, a force-push or a hand-edited JSON file all bypass it. This guard reads the
actual commit history, so a rewrite is DETECTED even where it was not PREVENTED -- which is the only
protection available until the server-side ruleset in docs/OPERATIONS.md is applied to the account.
"""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts", "handicap"))
import verify_append_only as V  # noqa: E402


def sh(cmd, cwd):
    subprocess.run(cmd, cwd=cwd, shell=True, check=True, capture_output=True, text=True)


@pytest.fixture
def ledger(tmp_path):
    root = tmp_path / "ledger"
    (root / "data" / "recommendations" / "2026" / "week_01").mkdir(parents=True)
    sh("git init -q && git config user.email t@t && git config user.name t", str(root))
    return root


def write(ledger, rid, **kw):
    p = ledger / "data" / "recommendations" / "2026" / "week_01" / f"{rid}.json"
    p.write_text(json.dumps({"recommendation_id": rid, "decision": "RECOMMENDED", **kw}, indent=1) + "\n")
    return p


def commit(ledger, msg="add"):
    sh(f"git add -A && git commit -q -m '{msg}'", str(ledger))


# ---- the clean case --------------------------------------------------------------------------------

def test_a_purely_additive_history_is_clean(ledger):
    for rid in ("rec_a", "rec_b", "rec_c"):
        write(ledger, rid)
        commit(ledger, f"add {rid}")
    assert V.scan_history(str(ledger)) == []
    assert V.scan_contents(str(ledger)) == []


def test_an_amendment_is_an_addition_not_an_edit(ledger):
    """A changed mind is a NEW record carrying `amends`. That is additive and must stay clean."""
    write(ledger, "rec_orig")
    commit(ledger)
    write(ledger, "rec_new", amends="rec_orig")
    commit(ledger)
    assert V.scan_history(str(ledger)) == []


# ---- the violations --------------------------------------------------------------------------------

def test_editing_a_recommendation_after_the_fact_is_caught(ledger):
    """The failure the whole branch exists to make impossible: improving a call after it settled."""
    write(ledger, "rec_a", bet_up_to_probability=0.58)
    commit(ledger)
    write(ledger, "rec_a", bet_up_to_probability=0.72)     # same path, better-looking number
    commit(ledger, "tidy up")

    v = V.scan_history(str(ledger))
    assert len(v) == 1
    assert v[0]["status"] == "M"
    assert v[0]["path"].endswith("rec_a.json")


def test_deleting_a_record_is_caught(ledger):
    write(ledger, "rec_a")
    commit(ledger)
    os.remove(ledger / "data" / "recommendations" / "2026" / "week_01" / "rec_a.json")
    commit(ledger, "remove")
    assert [x["status"] for x in V.scan_history(str(ledger))] == ["D"]


def test_renaming_a_record_is_caught(ledger):
    """A record's path is its identity. Moving it detaches the decision from its id."""
    write(ledger, "rec_a")
    commit(ledger)
    sh("git mv data/recommendations/2026/week_01/rec_a.json "
       "data/recommendations/2026/week_01/rec_z.json", str(ledger))
    commit(ledger, "rename")
    assert V.scan_history(str(ledger)), "a rename must be reported"


def test_a_rewrite_that_preserved_the_path_is_still_caught_by_content(ledger):
    """Belt and braces: even a history-clean tree is checked for filename/id disagreement."""
    write(ledger, "rec_a")
    commit(ledger)
    p = ledger / "data" / "recommendations" / "2026" / "week_01" / "rec_a.json"
    p.write_text(json.dumps({"recommendation_id": "rec_SOMETHING_ELSE"}) + "\n")
    problems = V.scan_contents(str(ledger))
    assert len(problems) == 1 and "filename claims" in problems[0]["problem"]


def test_unreadable_json_is_reported_rather_than_skipped(ledger):
    p = ledger / "data" / "recommendations" / "2026" / "week_01" / "rec_a.json"
    p.write_text("{not json")
    assert V.scan_contents(str(ledger))[0]["problem"].startswith("unreadable")


# ---- scope -----------------------------------------------------------------------------------------

def test_non_ledger_files_may_change_freely(ledger):
    """Documentation and tooling are not evidence. Only the record kinds are immutable."""
    (ledger / "README.md").write_text("v1\n")
    commit(ledger)
    (ledger / "README.md").write_text("v2\n")
    commit(ledger, "edit readme")
    assert V.scan_history(str(ledger)) == []


def test_every_record_kind_the_store_knows_about_is_covered():
    """A new record kind must not silently arrive outside the guard."""
    from nfl_edge.handicap import store
    uncovered = set(store.KINDS) - set(V.IMMUTABLE_KINDS)
    assert not uncovered, f"record kinds not covered by the append-only guard: {sorted(uncovered)}"
