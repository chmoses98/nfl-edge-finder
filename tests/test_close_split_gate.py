"""The close-game split (`team_volume[TEAM].by_close_result`) is published only when the calibration artifact authorises it.

`research/game_script_v2/close_split_calibration.json` says DO NOT SHOW SPLIT (model - B1 Brier CI upper bound above the
bar). These tests pin that script_block and the research export both fail closed, independently of any other flag, and that
no other script probability moves.
"""
from __future__ import annotations

import copy
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (ROOT, os.path.join(ROOT, "contract")):
    if p not in sys.path:
        sys.path.insert(0, p)

from nfl_edge.handicap import script_block as SB  # noqa: E402
from scripts import research_export as RE  # noqa: E402

REL = os.path.join("research", "game_script_v2", "close_split_calibration.json")


def _root(tmp_path, content):
    """A repo root whose gate artifact holds ``content`` (a dict is JSON-encoded; a str is written verbatim; None = absent)."""
    path = tmp_path / REL
    path.parent.mkdir(parents=True)
    if content is not None:
        path.write_text(content if isinstance(content, str) else json.dumps(content))
    return str(tmp_path)


def _verdict(show=False, split=False, classes=True, **extra):
    return {"verdict": {"show_split": show, "split_no_worse_than_b1": split, "close_classes_no_worse_than_b1": classes}, **extra}


# ------------------------------------------------------------------------------------------------ the gate itself
def test_explicit_show_authorises(tmp_path):
    g = SB.close_split_gate(_root(tmp_path, _verdict(show=True, split=True, classes=True)))
    assert g["status"] == "SHOW" and g["displayable"] is True and len(g["artifact_sha256"]) == 64


def test_explicit_do_not_show_suppresses(tmp_path):
    g = SB.close_split_gate(_root(tmp_path, _verdict(show=False, split=False, classes=True)))
    assert g["status"] == "SUPPRESS" and g["displayable"] is False and "DO NOT SHOW SPLIT" in g["reason"]
    assert g["verdict"]["show_split"] is False


@pytest.mark.parametrize("content", [
    None,                                                       # missing artifact
    "{ not json",                                               # malformed JSON
    "[]", "null", "42",                                         # wrong top-level type
    {"verdict": None}, {"verdict": []}, {}, {"nothing": 1},     # no verdict object
    {"verdict": {"show_split": True}},                          # component flags missing
    {"verdict": {"show_split": "true", "split_no_worse_than_b1": "true", "close_classes_no_worse_than_b1": "true"}},  # strings
    {"verdict": {"show_split": 1, "split_no_worse_than_b1": 1, "close_classes_no_worse_than_b1": 1}},                 # truthy ints
    {"verdict": {"show_split": None, "split_no_worse_than_b1": True, "close_classes_no_worse_than_b1": True}},
    _verdict(show=True, split=False, classes=True),             # show contradicts its own components
    _verdict(show=True, split=True, classes=False),
], ids=lambda c: str(c)[:40])
def test_anything_but_an_explicit_consistent_show_fails_closed(tmp_path, content):
    g = SB.close_split_gate(_root(tmp_path, content))
    assert g["status"] == "SUPPRESS" and g["displayable"] is False and g["reason"]


def test_unreadable_artifact_fails_closed(tmp_path):
    root = _root(tmp_path, None)
    os.makedirs(tmp_path / REL)                                  # a directory where the file should be
    assert SB.close_split_gate(root)["displayable"] is False


def test_the_committed_artifact_matches_the_published_gate():
    with open(os.path.join(ROOT, REL)) as f:
        flag = json.load(f)["verdict"]["show_split"]
    g = SB.close_split_gate()
    assert g["displayable"] is (flag is True) and g["status"] == ("SHOW" if flag is True else "SUPPRESS")
    assert SB.calibration_gates()["version"] == SB.GATES_VERSION


# ------------------------------------------------------------------------------------------------ script_block output
def _script():
    close = lambda w, t, l: {"win1-6": {"share_of_rows": w}, "tie": {"share_of_rows": t}, "lose1-6": {"share_of_rows": l}}
    state = {"lead14+": {"share_of_rows": 0.3}, "within6": {"share_of_rows": 0.3}, "trail14+": {"share_of_rows": 0.4}}
    q = {"mean": 24.0, "p05": 10.0, "p25": 17.0, "p75": 31.0, "p95": 38.0}
    team = lambda: {"home": True, "volume": {"plays": q, "pass_rate": {**q, "mean": 0.58}}, "by_final_margin": copy.deepcopy(state),
                    "by_close_result": close(0.15, 0.0, 0.15), "players": []}
    return {"environment": {"home_margin": q, "total": q, "p_home_win": 0.61, "p_one_score": 0.44, "p_blowout_17plus": 0.2},
            "teams": {"PIT": team(), "CLE": team()}}


def _gsi(gates=None, script=None):
    return SB.game_script_inputs({"markets": []}, script or _script(), script_source="t", hypotheses_note="t", gates=gates)


def _gate(status, displayable):
    return {"version": SB.GATES_VERSION, "close_win_split": {"status": status, "displayable": displayable, "reason": "t", "artifact": "x",
                                                            "artifact_sha256": None, "verdict": None}}


def test_split_is_forwarded_only_when_authorised():
    shown = _gsi(_gate("SHOW", True))
    hidden = _gsi(_gate("SUPPRESS", False))
    assert "by_close_result" in shown["team_volume"]["PIT"] and "by_close_result" in shown["team_volume"]["CLE"]
    assert all("by_close_result" not in v for v in hidden["team_volume"].values())
    assert hidden["calibration_gates"]["close_win_split"]["displayable"] is False


@pytest.mark.parametrize("gates", [{}, {"close_win_split": {}}, {"close_win_split": {"displayable": "yes"}},
                                   {"close_win_split": {"status": "SHOW", "displayable": 1}}, {"close_win_split": None}])
def test_a_malformed_gate_never_authorises(gates):
    assert all("by_close_result" not in v for v in _gsi(gates)["team_volume"].values())


def test_default_gate_is_read_from_the_committed_artifact_and_blocks_today():
    out = _gsi(None)
    assert out["calibration_gates"]["close_win_split"]["status"] == SB.close_split_gate()["status"]
    if not SB.close_split_gate()["displayable"]:
        assert all("by_close_result" not in v for v in out["team_volume"].values())


def test_every_other_script_probability_is_unchanged_by_the_gate():
    shown, hidden = _gsi(_gate("SHOW", True)), _gsi(_gate("SUPPRESS", False))
    assert shown["game_environment"] == hidden["game_environment"]
    for team in ("PIT", "CLE"):
        a, b = dict(shown["team_volume"][team]), dict(hidden["team_volume"][team])
        a.pop("by_close_result")
        assert a == b and a["by_final_margin"]["within6"]["share_of_rows"] == 0.3
    assert shown["player_opportunity"] == hidden["player_opportunity"]


def test_no_script_still_publishes_the_gate():
    out = SB.game_script_inputs({"markets": []}, None, script_source="none", hypotheses_note="t", gates=_gate("SUPPRESS", False))
    assert out["state"] == "PARTIAL" and out["calibration_gates"]["close_win_split"]["displayable"] is False


# ------------------------------------------------------------------------------------------------ research export
def test_export_keeps_the_split_only_with_an_authorising_gate():
    shown = _gsi(_gate("SHOW", True))
    kept = RE.enforce_close_split_gate(shown)
    assert "by_close_result" in kept["team_volume"]["PIT"] and kept["calibration_gates"]["close_win_split"]["displayable"] is True


@pytest.mark.parametrize("mutate", ["legacy", "suppress", "tampered"])
def test_export_strips_the_split_for_legacy_suppressed_or_inconsistent_packets(mutate):
    gsi = _gsi(_gate("SHOW", True))                                        # a packet that still carries the split
    if mutate == "legacy":
        gsi.pop("calibration_gates")
    elif mutate == "suppress":
        gsi["calibration_gates"] = _gate("SUPPRESS", False)
    else:
        gsi["calibration_gates"] = _gate("SHOW", False)                    # status and displayable disagree
    out = RE.enforce_close_split_gate(gsi)
    assert all("by_close_result" not in v for v in out["team_volume"].values())
    g = out["calibration_gates"]["close_win_split"]
    assert g["status"] == "SUPPRESS" and g["displayable"] is False
    assert out["game_environment"] == gsi["game_environment"], "only the split is removed"
    assert "by_close_result" in gsi["team_volume"]["PIT"], "the packet itself is not mutated"
