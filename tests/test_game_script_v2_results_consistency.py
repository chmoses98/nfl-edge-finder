"""The committed GAME SCRIPT V2 / five-season summaries must be exactly what their committed JSON renders, and the
committed numbers must respect the invariants the study claims (no silent exclusions, zero coherence failures,
script probabilities that sum to one, evidence classes that never call a retrospective season prospective)."""
import importlib.util
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
OUT = os.path.join(ROOT, "research", "game_script_v2")
_spec = importlib.util.spec_from_file_location("gsv2_write", os.path.join(ROOT, "scripts", "sim", "write_game_script_v2.py"))
W = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(W)


def _load(name):
    p = os.path.join(OUT, name)
    if not os.path.exists(p):
        pytest.skip(f"{name} is not in this checkout")
    return json.load(open(p))


@pytest.mark.parametrize("name", W.FILES)
def test_the_committed_summary_is_exactly_what_the_json_renders(name):
    rendered = W.render_all()
    if name not in rendered:
        pytest.skip(f"{name}'s source JSON is not in this checkout")
    path = os.path.join(OUT, name)
    assert os.path.exists(path), f"{name} has source JSON but was not rendered into the repo"
    assert open(path).read() == rendered[name], f"{name} disagrees with its JSON: python scripts/sim/write_game_script_v2.py"


def test_no_silent_exclusions_and_no_coherence_failures():
    b = _load("baseline_5y.json")
    assert sorted(b["by_season"]) == ["2021", "2022", "2023", "2024", "2025"]
    for y, r in b["by_season"].items():
        run = r["run"]
        assert run["games_simulated"] + len(run["skipped"]) == run["games"], y
        assert run["skipped"] == [] and run["coherence_failures"] == 0, y
        assert r["evaluate_mismatches"] == [], f"{y}: the pooled report scores a different population from evaluate"
        assert max(r["train_seasons"]) < int(y) and max(r["priors_fit_seasons"]) < int(y), y


def test_evidence_classes_never_call_a_retrospective_season_prospective():
    b = _load("baseline_5y.json")
    cls = b["meta"]["evidence_class"]
    assert cls["2021"] == cls["2022"] == "RETROSPECTIVE_CHALLENGE"
    assert all(cls[y] == "RETROSPECTIVE_DEVELOPMENT" for y in ("2023", "2024", "2025"))
    assert not any("PROSPECTIVE" in v and "RETROSPECTIVE" not in v for v in cls.values())


def test_script_calibration_covers_every_simulated_game():
    b = _load("baseline_5y.json"); c = _load("script_calibration_5y.json")
    for y, s in c["by_season"].items():
        assert s["n_games"] + s["missing_realized"] == b["by_season"][y]["run"]["games_simulated"], y
        assert s["centre_is_close"] == s["n_games"], f"{y}: a script centre is not the game's closing line"
    by_cell = c["pooled"]["by_cell"]
    assert abs(sum(v["predicted"] for v in by_cell.values()) - 1) < 1e-9
    assert abs(sum(v["realized"] for v in by_cell.values()) - 1) < 1e-9
    assert c["verdict"]["verdict"] in ("READY_FOR_PROSPECTIVE_RESEARCH", "NEEDS_MORE_WORK", "REJECTED")


def test_every_registered_arm_is_reported_with_a_verdict():
    a = _load("opponent_adjustment_ablation.json")
    assert set(a["arms"]) == {"A1", "A2", "A3", "A4", "A5", "R1"}
    for k, r in a["arms"].items():
        assert r["verdict"] in ("PROMOTABLE", "REJECTED"), (k, r.get("verdict"))
        assert sorted(r["by_season"]) == ["2021", "2022", "2023", "2024", "2025"]
        assert all(s["rows_missing_in_arm"] == 0 for s in r["by_season"].values()), k
