"""The shadow ledger is the only honest record of what was predicted before kickoff.

Its value depends entirely on being append-only and traceable. If a snapshot can be silently rewritten, or
two different models can produce the same prediction_id, then a disappointing prediction can be quietly
replaced by a better one and nobody -- including us -- could tell afterwards.
"""
import gzip
import json

import pytest

from nfl_edge.shadow.ledger import LedgerWriter, Observation, prediction_id


def obs(ticker="KXNFLGAME-X-Y", run_id="20260904T120000Z", model_version="shadow-9.9.9",
        calibration_version="cal-1", support_state="SUPPORTED", family="GAME_WINNER"):
    return Observation(
        prediction_id=prediction_id(run_id, ticker, model_version, calibration_version),
        schema_version="1", run_id=run_id, observed_at="2026-09-04T12:00:00Z",
        model_version=model_version, model_artifact_sha="deadbeef", calibration_version=calibration_version,
        feature_cutoff="2026-09-04T12:00:00Z", ticker=ticker, event_ticker=None, series_ticker=None,
        family=family, period="FULL", stat=None, threshold=None, floor_strike=None, operator=None,
        support_state=support_state)


def test_prediction_id_is_stable_for_the_same_inputs():
    a = prediction_id("run", "TICK", "m", "c")
    b = prediction_id("run", "TICK", "m", "c")
    assert a == b


@pytest.mark.parametrize("field,changed", [("run_id", "OTHER"), ("ticker", "OTHER"),
                                           ("model_version", "OTHER"), ("calibration_version", "OTHER")])
def test_every_lineage_component_changes_the_prediction_id(field, changed):
    base = dict(run_id="run", ticker="TICK", model_version="m", calibration_version="c")
    a = prediction_id(**base)
    base[field] = changed
    assert prediction_id(**base) != a, f"{field} does not participate in the prediction id"


def test_a_run_file_is_never_reopened_for_writing(tmp_path):
    w = LedgerWriter(str(tmp_path), "20260904T120000Z", model_version="shadow-9.9.9")
    w.write(obs())
    w.close()
    with pytest.raises(FileExistsError):
        LedgerWriter(str(tmp_path), "20260904T120000Z", model_version="shadow-9.9.9")


def test_a_different_model_version_writes_a_separate_file_rather_than_colliding(tmp_path):
    """Re-pricing the same snapshot with a changed model is legitimate and must not overwrite the old one."""
    w1 = LedgerWriter(str(tmp_path), "20260904T120000Z", model_version="shadow-0.2.0")
    w1.write(obs(model_version="shadow-0.2.0")); m1 = w1.close()
    w2 = LedgerWriter(str(tmp_path), "20260904T120000Z", model_version="shadow-0.3.0")
    w2.write(obs(model_version="shadow-0.3.0")); m2 = w2.close()
    assert m1["observations_file"] != m2["observations_file"]
    assert "shadow-0.2.0" in m1["observations_file"] and "shadow-0.3.0" in m2["observations_file"]


def test_duplicate_predictions_are_dropped_not_written_twice(tmp_path):
    w = LedgerWriter(str(tmp_path), "20260904T120000Z", model_version="m")
    assert w.write(obs()) is True
    assert w.write(obs()) is False
    man = w.close()
    assert man["counts"] == {"written": 1, "duplicate": 1}
    lines = gzip.open(w.path, "rt").read().strip().splitlines()
    assert len(lines) == 1


def test_unsupported_observations_are_recorded_rather_than_dropped(tmp_path):
    """Failing closed means writing down what was refused and why -- not producing a shorter file."""
    w = LedgerWriter(str(tmp_path), "20260904T120000Z", model_version="m")
    w.write(obs(ticker="A", support_state="SUPPORTED"))
    w.write(obs(ticker="B", support_state="UNSUPPORTED_MODEL"))
    w.write(obs(ticker="C", support_state="UNSUPPORTED_RULES"))
    man = w.close()
    assert man["counts"]["written"] == 3
    assert man["by_support_state"] == {"SUPPORTED": 1, "UNSUPPORTED_MODEL": 1, "UNSUPPORTED_RULES": 1}


def test_every_written_row_carries_its_full_lineage(tmp_path):
    w = LedgerWriter(str(tmp_path), "20260904T120000Z", model_version="shadow-9.9.9")
    w.write(obs())
    w.close()
    row = json.loads(gzip.open(w.path, "rt").readline())
    for f in ("prediction_id", "run_id", "model_version", "model_artifact_sha", "calibration_version",
              "feature_cutoff", "ticker", "support_state", "schema_version", "observed_at"):
        assert row.get(f) not in (None, ""), f"{f} missing from a ledger row"


def test_the_manifest_names_the_file_it_describes(tmp_path):
    import os
    w = LedgerWriter(str(tmp_path), "20260904T120000Z", model_version="m")
    w.write(obs())
    man = w.close()
    assert man["observations_file"] == os.path.basename(w.path)
    assert man["model_version"] == "m"
