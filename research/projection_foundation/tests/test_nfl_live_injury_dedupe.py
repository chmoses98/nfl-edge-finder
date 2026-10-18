"""The live availability rung gets one injury designation per player (fix for scheduled run 39127871523)."""
import os
import sys

import pandas as pd

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, ".."))

from nfl.live import availability as LA  # noqa: E402
from nfl.live import injury_dedupe as ID  # noqa: E402
from nfl.live import project as LP  # noqa: E402

ORIG_TABLE = LA.injury_table                                     # before any test applies the patch

BASE = dict(sport="NFL", event_id="g", event_start_utc="2026-10-18T17:00:00Z", entity_name="X", team="SEA",
            captured_utc="2026-10-18T15:30:00Z", source="s")
OVERLAP = {("g", "p1", "injury"): {**BASE, "entity_id": "p1", "kind": "injury", "status": "QUESTIONABLE", "certainty": "REPORTED"},
           ("g", "p1", "roster"): {**BASE, "entity_id": "p1", "kind": "roster", "status": "INACTIVE", "certainty": "CONFIRMED"},
           ("g", "p2", "injury"): {**BASE, "entity_id": "p2", "kind": "injury", "status": "DOUBTFUL", "certainty": "REPORTED"}}


def test_the_unpatched_table_names_a_player_twice_when_sources_overlap():
    """Reproduces the failure: an injury designation and a CONFIRMED inactive list both name p1."""
    t = ORIG_TABLE(OVERLAP, 2026, 7)
    assert t.gsis_id.duplicated().any()


def test_dedupe_keeps_the_most_severe_and_leaves_unique_tables_untouched():
    inj = pd.DataFrame({"season": [2026, 2026, 2026, 2025], "week": [7, 7, 7, 7], "gsis_id": ["p1", "p1", "p2", "p1"],
                        "team": ["SEA"] * 4, "report_status": ["Questionable", "Out", "Doubtful", "Questionable"],
                        "game_type": ["REG"] * 4, "practice_status": [None] * 4})
    d = ID.dedupe(inj)
    assert not d.duplicated(ID.KEYS).any() and len(d) == 3
    assert d.set_index(["season", "gsis_id"]).report_status.to_dict() == {
        (2026, "p1"): "Out", (2026, "p2"): "Doubtful", (2025, "p1"): "Questionable"}
    uniq = inj.iloc[[1, 2, 3]].reset_index(drop=True)
    assert ID.dedupe(uniq) is uniq


def test_apply_patches_the_live_path_and_the_designation_join_keeps_its_length():
    ID.apply()
    ID.apply()                                                   # idempotent
    t = LA.injury_table(OVERLAP, 2026, 7)
    assert len(t) == 2 and dict(zip(t.gsis_id, t.report_status)) == {"p1": "Out", "p2": "Doubtful"}
    assert "injury_dedupe" in LP._live_inj.__code__.co_filename
    pf = pd.DataFrame({"season": [2026] * 3, "week": [7] * 3, "player_id": ["p1", "p2", "p3"]})
    inj2 = t.rename(columns={"gsis_id": "player_id"})[["season", "week", "player_id", "report_status"]]
    des = pf.merge(inj2, on=["season", "week", "player_id"], how="left").report_status
    assert len(des) == len(pf) and list(des.fillna("None")) == ["Out", "Doubtful", "None"]


def test_the_workflow_runs_the_patched_entry_point():
    root = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    action = open(os.path.join(root, ".github", "actions", "nfl-pf-live", "action.yml")).read()
    assert "python3 -m nfl.live.main " in action and "python3 -m nfl.live.run " not in action
