"""Wave-2 collection plumbing: the conductor's due rule, the collection-health classifier and the workflow wiring.
None of this may change what is captured, the windows, the cutoff, or anything the scorer reads."""
import importlib.util
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nfl_edge.sim import wave2_due as WD  # noqa: E402

UTC = timezone.utc
KO = datetime(2026, 10, 11, 17, 0, tzinfo=UTC)
GID = "2026_06_AAA_HHH"


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, path))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


H = _load("scripts/sim/wave2_collection_health.py", "w2health")
T = _load("tests/test_wave2_score.py", "w2score_tests")


# ------------------------------------------------------------------------------------------ frozen constants
def test_due_rule_constants_are_the_frozen_ones():
    from nfl_edge.sim import risk1, wave2_score as S
    runner = _load("scripts/sim/wave2_prospective.py", "w2runner")
    assert WD.WINDOWS == runner.WINDOWS == {"EARLY": (90, 240), "LATE": (30, 90)}
    assert WD.PROSPECTIVE_CUTOFF == risk1.PROSPECTIVE_CUTOFF == S.PROSPECTIVE_CUTOFF == "2026-10-05T16:14:02+00:00"
    assert H.FROZEN_COMPONENTS_SHA256 == S.FROZEN_COMPONENTS_SHA256
    assert H.ACCEPTED_RECORD_VERSIONS == S.ACCEPTED_RECORD_VERSIONS and runner.WAVE2_VERSION in H.ACCEPTED_RECORD_VERSIONS


def test_the_conductor_due_rule_agrees_with_the_capture_gate_minute_by_minute():
    runner = _load("scripts/sim/wave2_prospective.py", "w2runner2")
    sched = pd.DataFrame([{"game_id": GID, "season": 2026, "week": 6, "gameday": "2026-10-11", "gametime": "13:00"},
                          {"game_id": "2026_04_CCC_DDD", "season": 2026, "week": 4, "gameday": "2026-10-04", "gametime": "13:00"}])
    games = [{"game_id": GID, "kickoff_utc": KO}, {"game_id": "2026_04_CCC_DDD", "kickoff_utc": datetime(2026, 10, 4, 17, tzinfo=UTC)}]
    for m in range(0, 300):
        now = KO - timedelta(minutes=m)
        gate = {f"{g}:{v[0]}" for g, v in runner.due_games(sched, now, set()).items()}
        assert set(WD.due(games, now, set())) == gate, m
    assert WD.due(games, KO - timedelta(minutes=60), {(GID, "LATE")}) == []
    assert WD.due(games, KO - timedelta(minutes=60), {(GID, "EARLY")}) == [f"{GID}:LATE"]


# ------------------------------------------------------------------------------------------ conductor target
def test_the_conductor_dispatches_wave2_only_for_an_open_unrecorded_window():
    C = _load("scripts/handicap/horizon_conductor.py", "conductor")
    games = [{"game_id": GID, "kickoff_utc": KO, "game_type": "REG", "season": 2026, "week": 6,
              "away_team": "AAA", "home_team": "HHH", "gameday": "2026-10-11"}]
    calls = {"state": 0, "dispatch": []}

    def state():
        calls["state"] += 1
        return set()

    def run(now, seen=None):
        readers = {"WAVE2": (lambda: (calls.__setitem__("state", calls["state"] + 1), seen or set())[1])}
        return C.one_pass(["WAVE2"], games, "test", now, {}, state_readers=readers, active=lambda wf: 0,
                          dispatcher=lambda wf, ref: (calls["dispatch"].append(wf), (True, "ok"))[1])[0]

    line = run(KO - timedelta(minutes=600))
    assert line["decision"] == "wait" and line["due"] == [] and calls["state"] == 0, "nothing open -> market-data not listed"
    line = run(KO - timedelta(minutes=60))
    assert line["decision"] == "dispatch" and line["due"] == [f"{GID}:LATE"] and calls["dispatch"] == ["wave2-research.yml"]
    line = run(KO - timedelta(minutes=60), seen={(GID, "LATE")})
    assert line["decision"] == "wait" and line["due"] == []
    assert C.TARGETS["WAVE2"]["workflow"] == "wave2-research.yml"


# ------------------------------------------------------------------------------------------ health classifier
def _games():
    return [{"game_id": GID, "kickoff_utc": KO}]


def test_health_classifies_every_owed_window_against_the_schedule(tmp_path):
    src = H.DirSource(str(tmp_path))
    act = (KO - timedelta(days=1)).isoformat()
    # nothing recorded, both windows closed after activation -> both MISSED (a miss writes no record)
    res = H.classify(_games(), src, KO + timedelta(hours=1), active_since=act)
    assert {w["window"]: w["status"] for w in res["windows"]} == {"EARLY": "MISSED", "LATE": "MISSED"}
    # windows that closed before the workflow existed are reported, not owed
    res = H.classify(_games(), src, KO + timedelta(hours=1), active_since=(KO + timedelta(minutes=10)).isoformat())
    assert {w["status"] for w in res["windows"]} == {"NOT_OWED_PRE_ACTIVATION"}
    # open / not yet open
    res = H.classify(_games(), src, KO - timedelta(minutes=100), active_since=act)
    assert {w["window"]: w["status"] for w in res["windows"]} == {"EARLY": "OPEN", "LATE": "NOT_YET_OPEN"}


def test_health_marks_a_valid_capture_and_names_every_integrity_failure(tmp_path):
    act = (KO - timedelta(days=1)).isoformat()
    T.write(tmp_path, GID, "LATE", KO - timedelta(minutes=60), KO)
    T.write(tmp_path, GID, "EARLY", KO - timedelta(minutes=150), KO, comps="0" * 64)
    res = H.classify(_games(), H.DirSource(str(tmp_path)), KO + timedelta(hours=1), active_since=act)
    st = {w["window"]: w["status"] for w in res["windows"]}
    assert st["LATE"] == "CAPTURED"
    assert st["EARLY"].startswith("INVALID:") and "stale or wrong components hash" in st["EARLY"]
    bad = H.failures(res, [], KO + timedelta(hours=1), 48)
    assert bad == [f"{GID} EARLY: {st['EARLY']}"]


@pytest.mark.parametrize("mutate, expect", [
    (lambda d, g: g["coherence"].__setitem__("S1", False), "incoherent arm(s): S1"),
    (lambda d, g: d.__setitem__("generated_at", "2026-10-11T17:05:00+00:00"), "generated at or after kickoff"),
    (lambda d, g: d.__setitem__("dry_run", True), "dry-run record"),
    (lambda d, g: d.__setitem__("wave2_version", "wave2-prospective-1.0.0"), "schema version wave2-prospective-1.0.0 not accepted"),
    (lambda d, g: g["arms"].pop("A1"), "arm A1 missing"),
    (lambda d, g: g.pop("avail_state"), "avail_state missing"),
    (lambda d, g: g["arms"]["M1"].pop("total_pmf"), "M1.total_pmf missing"),
    (lambda d, g: d.__setitem__("betting_authority", "FULL"), "research_only / betting_authority NONE not declared"),
])
def test_record_problems_names_each_defect(tmp_path, mutate, expect):
    import gzip
    p = T.write(tmp_path, GID, "LATE", KO - timedelta(minutes=60), KO)
    d = json.loads(gzip.decompress(open(p, "rb").read()))
    g = d["games"][GID]
    assert H.record_problems(d, p) == []
    mutate(d, g)
    assert expect in H.record_problems(d, p)


def test_health_detects_a_write_once_collision_and_orphan_records(tmp_path):
    act = (KO - timedelta(days=1)).isoformat()
    T.write(tmp_path, GID, "LATE", KO - timedelta(minutes=60), KO)
    T.write(tmp_path, GID, "LATE", KO - timedelta(minutes=45), KO)
    T.write(tmp_path, "2026_06_ZZZ_YYY", "LATE", KO - timedelta(minutes=60), KO)
    res = H.classify(_games(), H.DirSource(str(tmp_path)), KO + timedelta(hours=1), active_since=act)
    assert {w["window"]: w["status"] for w in res["windows"]}["LATE"] == "WRITE_ONCE_COLLISION"
    assert [r["game_id"] for r in res["orphan_records"]] == ["2026_06_ZZZ_YYY"]
    assert any("orphan" in b for b in H.failures(res, [], KO + timedelta(hours=1), 48))


def test_risk1_script_capture_health(tmp_path):
    import gzip
    d = tmp_path / "data" / "shadow" / "sim" / "2026-10-11"
    d.mkdir(parents=True)

    def cap(run, gen, fp):
        doc = {"games": {GID: {"state": "OK", "generated_at": gen.isoformat(),
                               "contracts": [{"ticker": "T1", **({"fingerprint": "abc"} if fp else {})}]}}}
        (d / f"{run}.sim-1.1.0.scripts_v2.json.gz").write_bytes(gzip.compress(json.dumps(doc).encode()))

    src = H.DirSource(str(tmp_path))
    now = KO + timedelta(hours=2)
    act = (KO - timedelta(days=1)).isoformat()
    assert H.risk1_scripts(_games(), src, now, active_since=act)[0]["status"] == "SCRIPT_MISSING"
    cap("20261011T150000Z", KO - timedelta(hours=1), fp=False)
    assert H.risk1_scripts(_games(), src, now, active_since=act)[0]["status"] == "SCRIPT_CAPTURED_NO_FINGERPRINTS"
    cap("20261011T153000Z", KO - timedelta(minutes=30), fp=True)
    cap("20261011T171000Z", KO + timedelta(minutes=10), fp=True)          # after kickoff: never the one used
    r = H.risk1_scripts(_games(), src, now, active_since=act)[0]
    assert r["status"] == "SCRIPT_CAPTURED" and r["last_pre_kickoff_capture"]["path"].endswith("153000Z.sim-1.1.0.scripts_v2.json.gz")


def test_health_reads_no_outcome_and_computes_no_metric():
    import ast
    tree = ast.parse(open(os.path.join(ROOT, "scripts", "sim", "wave2_collection_health.py")).read())
    tree.body = tree.body[1:]                                   # the module docstring may name what it does NOT do
    imported = {a.name for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom)) for a in n.names}
    imported |= {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
    code = ast.unparse(tree)
    assert not any("wave2_score" in m or "risk1" in m or "backtest" in m for m in imported), imported
    for k in ("player_games", "home_score", "away_score", "crps", "log_score", "brier", "primary_test", "realized_cash"):
        assert k not in code, k


# ------------------------------------------------------------------------------------------ workflow wiring
def test_workflow_wiring_keeps_the_frozen_design():
    import yaml
    w2 = yaml.safe_load(open(os.path.join(ROOT, ".github", "workflows", "wave2-research.yml")))
    on = w2.get("on", w2.get(True))
    assert on["schedule"] == [{"cron": "7,37 * * * *"}]
    steps = {s.get("name"): s for s in w2["jobs"]["capture"]["steps"]}
    pub = steps["Publish the write-once records"]
    assert "rehearsal" not in pub["if"] and "steps.due.outputs.due == 'true'" in pub["if"], "a rehearsal never publishes"
    reh = steps["Rehearsal capture (dry run, never published)"]["run"]
    assert "--dry-run" in reh and "/tmp/rehearsal" in reh and "publish_market_data" not in reh
    hc = open(os.path.join(ROOT, ".github", "workflows", "horizon-conductor.yml")).read()
    assert "RUN_NFL,THREE_ARM,WAVE2,POSTGAME" in hc
    wh = open(os.path.join(ROOT, ".github", "workflows", "workflow-health.yml")).read()
    assert "wave2_collection_health.py" in wh and "--fail-on-recent-miss-hours 48" in wh


def test_rehearsal_validation_waives_only_the_replay_timing(tmp_path):
    import gzip
    p = T.write(tmp_path, GID, "LATE", KO - timedelta(minutes=60), KO, dry=True)
    d = json.loads(gzip.decompress(open(p, "rb").read()))
    d["generated_at"] = (KO + timedelta(days=1)).isoformat()          # a replay runs long after the game
    assert H.record_problems(d, p) == ["dry-run record", "generated at or after kickoff"]
    assert H.record_problems(d, p, rehearsal=True) == []
    d["games"][GID]["cutoff"] = (KO + timedelta(minutes=5)).isoformat()   # the FEATURE cutoff is still enforced
    assert "feature cutoff at or after kickoff" in H.record_problems(d, p, rehearsal=True)
