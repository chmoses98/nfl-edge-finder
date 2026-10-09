"""A1B (addendum B): verified pregame inactives -- source snapshots, choice at the cutoff, identity, treatment,
write-once, qualification, scorer, conductor and health. Synthetic data only; no real game is labelled."""
import gzip
import hashlib
import importlib.util
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nfl_edge.sim import a1b as A, a1b_qualify as Q, a1b_score as SC, wave2_score as W  # noqa: E402

UTC = timezone.utc
KO = datetime(2026, 10, 18, 17, 0, tzinfo=UTC)
GAME = {"game_id": "2026_06_AAA_HHH", "event_id": "401999999", "kickoff_utc": KO, "home_team": "HHH", "away_team": "AAA"}


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, path))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


SN = _load("scripts/sim/a1b_snapshot.py", "a1b_snapshot_t")


def roster(inactive_ids, n_active=46, status=200):
    entries = [{"playerId": 1000 + i, "active": True} for i in range(n_active)]
    entries += [{"playerId": int(i), "active": False} for i in inactive_ids]
    return {"meta": {"status": status, "retrieved_at": None, "url": "u"}, "body": {"entries": entries} if status == 200 else None}


def snap(retrieved_at, home_ids, away_ids, *, home_status=200, away_status=200, run=None):
    comp = {"meta": {"status": 200}, "body": {"competitors": [{"id": "1", "homeAway": "home"}, {"id": "2", "homeAway": "away"}]}}
    rs = {"home": roster(home_ids, status=home_status), "away": roster(away_ids, status=away_status)}
    for r in rs.values():
        r["meta"]["retrieved_at"] = retrieved_at.isoformat()
    d = A.snapshot_document(GAME, comp, rs, run_id=run or retrieved_at.strftime("%Y%m%dT%H%M%SZ"))
    d["_path"], d["_sha256"] = "p", "s"
    return d


H7 = [str(500 + i) for i in range(7)]
A6 = [str(600 + i) for i in range(6)]


# ------------------------------------------------------------------------------------------ choice at the cutoff
def test_a_confirmed_list_available_before_the_cutoff_is_used():
    s = snap(KO - timedelta(minutes=85), H7, A6)
    got, why = A.choose_snapshot([s], KO - timedelta(minutes=60))
    assert got is s and why == "USABLE"


def test_information_arriving_after_the_cutoff_is_never_used():
    late = snap(KO - timedelta(minutes=50), H7, A6)
    got, why = A.choose_snapshot([late], KO - timedelta(minutes=60))
    assert got is None and why == "NO_SNAPSHOT_IN_WINDOW"


def test_a_snapshot_before_the_release_floor_is_not_the_inactive_list():
    early = snap(KO - timedelta(minutes=130), H7, A6)       # plausible counts, but too early to be the official list
    assert A.choose_snapshot([early], KO - timedelta(minutes=60))[0] is None


def test_the_latest_usable_snapshot_at_the_cutoff_wins():
    s1, s2 = snap(KO - timedelta(minutes=95), H7, A6), snap(KO - timedelta(minutes=70), H7[:6], A6)
    assert A.choose_snapshot([s1, s2], KO - timedelta(minutes=60))[0] is s2


def test_missing_source_and_source_failures_are_outages_not_empty_lists():
    s = snap(KO - timedelta(minutes=80), [], [], home_status=503, away_status=503)
    assert {t["reading"]["state"] for t in s["teams"].values()} == {A.OUTAGE}
    assert A.choose_snapshot([s], KO - timedelta(minutes=60)) == (None, "SOURCE_OUTAGE")
    f = A.fetch("http://x", opener=lambda url: (_ for _ in ()).throw(TimeoutError("slow")))
    assert f["body"] is None and f["meta"]["status"] is None and "TimeoutError" in f["meta"]["error"]
    assert A.parse_roster(f)["state"] == A.OUTAGE


def test_an_unpublished_or_implausible_list_is_not_usable():
    s0 = snap(KO - timedelta(minutes=80), [], A6)                   # 200 but nobody flagged
    assert s0["teams"]["home"]["reading"]["state"] == A.NOT_PUBLISHED
    s40 = snap(KO - timedelta(minutes=80), [str(700 + i) for i in range(40)], A6)
    assert s40["teams"]["home"]["reading"]["state"] == A.IMPLAUSIBLE
    assert A.choose_snapshot([s0, s40], KO - timedelta(minutes=60)) == (None, "NOT_PUBLISHED_OR_IMPLAUSIBLE")


def test_source_timestamps_are_recorded_but_only_our_retrieval_instant_counts():
    s = snap(KO - timedelta(minutes=80), H7, A6)
    s["teams"]["home"]["fetch"]["source_headers"] = {"Last-Modified": "Sat, 01 Jan 2000 00:00:00 GMT"}
    assert A.snapshot_usable_at(s, KO - timedelta(minutes=60))
    s2 = dict(s, retrieved_at=None)
    assert not A.snapshot_usable_at(s2, KO - timedelta(minutes=60)), "no retrieval instant -> not provably pregame"


def test_a_snapshot_at_or_after_kickoff_is_refused_by_the_writer(tmp_path):
    s = snap(KO + timedelta(minutes=1), H7, A6)
    with pytest.raises(ValueError):
        SN.write_snapshot(str(tmp_path), s)


def test_duplicate_snapshot_attempts_are_refused(tmp_path):
    s = snap(KO - timedelta(minutes=80), H7, A6)
    p = SN.write_snapshot(str(tmp_path), s)
    with pytest.raises(FileExistsError):
        SN.write_snapshot(str(tmp_path), s)
    assert A.parse_name(p)[:2] == ("SRC", GAME["game_id"])


# ------------------------------------------------------------------------------------------ identity + treatment
def test_identity_mapping_fails_closed():
    s = snap(KO - timedelta(minutes=80), H7, A6)
    espn = {"H_qb": "500", "H_wr": "1001", "A_rb": "600", "A_te": "1002"}
    m = A.map_inactives(s, {"HHH": ["H_qb", "H_wr"], "AAA": ["A_rb", "A_te"]}, espn)
    assert m["HHH"]["inactive"] == {"H_qb"} and m["AAA"]["inactive"] == {"A_rb"} and all(v["usable"] for v in m.values())
    assert m["HHH"]["unmatched_inactive"] == 6, "inactive players absent from the projected roster change nothing"
    m2 = A.map_inactives(s, {"HHH": ["H_qb", "H_new"], "AAA": ["A_rb"]}, espn)
    assert not m2["HHH"]["usable"] and m2["HHH"]["unmapped_projected"] == ["H_new"]
    m3 = A.map_inactives(s, {"HHH": ["H_qb", "H_wr"], "AAA": ["A_rb"]}, {**espn, "H_wr": "500"})
    assert not m3["HHH"]["usable"] and m3["HHH"]["conflicting_ids"] == ["H_qb", "H_wr"]


def test_treatment_keeps_rows_and_never_invents_an_inactive():
    states = ["QUESTIONABLE", "QUESTIONABLE", "EXPECTED_ACTIVE", "EXPECTED_ACTIVE"]
    out = A.a1b_states(states, ["q_inactive", "q_active", "starter_inactive", "starter"], {"q_inactive", "starter_inactive"})
    assert out == ["INACTIVE_CONFIRMED", "EXPECTED_ACTIVE", "INACTIVE_CONFIRMED", "EXPECTED_ACTIVE"]
    from nfl_edge.settlement.availability import STATE_PLAY_RATES
    assert STATE_PLAY_RATES["INACTIVE_CONFIRMED"][0] == 0.0


# ------------------------------------------------------------------------------------------ due rules + conductor
def test_due_rules_snapshot_cadence_and_capture_window():
    g = [GAME]
    assert A.due(g, KO - timedelta(minutes=200), []) == {"snapshot": [], "capture": []}
    assert A.due(g, KO - timedelta(minutes=120), []) == {"snapshot": [GAME["game_id"]], "capture": []}
    recent = [f"{A.SRC_PREFIX}2026-10-18/{GAME['game_id']}.{(KO - timedelta(minutes=125)).strftime('%Y%m%dT%H%M%SZ')}.a1b_src.json.gz"]
    assert A.due(g, KO - timedelta(minutes=120), recent)["snapshot"] == [], "at most one snapshot per 10 minutes"
    assert A.due(g, KO - timedelta(minutes=60), [])["capture"] == [GAME["game_id"]]
    rec = [f"{A.REC_PREFIX}2026-10-18/{GAME['game_id']}.A1B.20261018T160000Z.a1b.json.gz"]
    assert A.due(g, KO - timedelta(minutes=60), rec)["capture"] == [], "one A1B record per game"
    assert A.due(g, KO + timedelta(minutes=1), [])["snapshot"] == [], "never after kickoff"
    old = dict(GAME, kickoff_utc=datetime(2026, 10, 5, 12, tzinfo=UTC))
    assert A.due([old], datetime(2026, 10, 5, 11, tzinfo=UTC), []) == {"snapshot": [], "capture": []}


def test_the_conductor_dispatches_a1b_only_when_owed():
    C = _load("scripts/handicap/horizon_conductor.py", "conductor_a1b")
    calls = {"state": 0, "disp": []}

    def state():
        calls["state"] += 1
        return []

    def run(now):
        return C.one_pass(["A1B"], [dict(GAME, season=2026, week=6, game_type="REG", gameday="2026-10-18")], "t", now, {},
                          state_readers={"A1B": state}, active=lambda wf: 0,
                          dispatcher=lambda wf, ref: (calls["disp"].append(wf), (True, "ok"))[1])[0]
    assert run(KO - timedelta(minutes=600))["due"] == [] and calls["state"] == 0
    line = run(KO - timedelta(minutes=60))
    assert line["decision"] == "dispatch" and any(x.startswith("A1B:") for x in line["due"]) and calls["disp"] == ["a1b-research.yml"]


# ------------------------------------------------------------------------------------------ qualification
def _qual_set(n=24, *, echo=False, truth_off=False, late=False):
    games, snaps, truth = [], {}, {}
    espn = {}
    for i in range(n):
        ko = KO + timedelta(hours=i)
        g = {"game_id": f"2026_06_A{i:02d}_HHH", "kickoff_utc": ko, "home_team": "HHH", "away_team": f"A{i:02d}"}
        games.append(g)
        h = [str(10000 + 100 * i + k) for k in range(7)]; a = [str(20000 + 100 * i + k) for k in range(6)]
        for e in h + a:
            espn[e] = "G" + e
        def mk(m, hh, aa):
            global GAME
            gg = dict(GAME, game_id=g["game_id"], kickoff_utc=ko, away_team=g["away_team"])
            comp = {"meta": {"status": 200}, "body": {"competitors": [{"id": "1", "homeAway": "home"}, {"id": "2", "homeAway": "away"}]}}
            rs = {"home": roster(hh), "away": roster(aa)}
            t = ko - timedelta(minutes=m)
            for r in rs.values():
                r["meta"]["retrieved_at"] = t.isoformat()
            return A.snapshot_document(gg, comp, rs, run_id=t.strftime("%Y%m%dT%H%M%SZ"))
        early = mk(140, h if echo else [], a if echo else [])
        cut = mk(30 if late else 70, h, a)            # late: the list first appears only after the T-35 freeze
        last = mk(20 if late else 40, h, a)
        snaps[g["game_id"]] = [early, cut, last]
        truth[(g["game_id"], "HHH")] = {"G" + e for e in (h[:3] if truth_off else h)}
        truth[(g["game_id"], g["away_team"])] = {"G" + e for e in a}
    return games, snaps, truth, espn


def test_qualification_passes_only_when_every_criterion_holds():
    now = KO + timedelta(days=3)
    g, s, t, e = _qual_set()
    assert Q.evaluate(g, s, t, e, now=now)["decision"] == "QUALIFIED"
    assert Q.evaluate(*_qual_set(echo=True), now=now)["passed"]["QR"] is False, "a week-long roster echo is not a release"
    assert Q.evaluate(*_qual_set(truth_off=True), now=now)["passed"]["QT"] is False
    late = Q.evaluate(*_qual_set(late=True), now=now)
    assert late["decision"] == "BLOCKED" and late["passed"]["QA"] is False


def test_qualification_never_decides_on_an_incomplete_set():
    g, s, t, e = _qual_set(n=10)
    assert Q.evaluate(g, s, t, e, now=KO + timedelta(days=3))["decision"] == "AWAITING_GAMES"
    g, s, t, e = _qual_set()
    t.pop((g[5]["game_id"], "HHH"))
    assert Q.evaluate(g, s, t, e, now=KO + timedelta(days=3))["decision"] == "AWAITING_TRUTH"


def test_the_source_status_starts_qualifying_and_nothing_counts_yet():
    st = json.load(open(os.path.join(ROOT, "research", "game_script_v2", "wave2", "a1b", "SOURCE_STATUS.json")))
    assert st["status"] == "QUALIFYING" and st["qualified_at"] is None and st["betting_authority"] == "NONE"


# ------------------------------------------------------------------------------------------ scorer
def _record(tmp_path, *, status="QUALIFIED", qualified_at="2026-10-12T00:00:00+00:00", state="OK", minutes=60, gid=None, run=None):
    gid = gid or GAME["game_id"]
    cutoff = KO - timedelta(minutes=minutes)
    pl = {"P1": {"team": "HHH", "targets": {"lo": 4, "p": [0.25, 0.5, 0.25]}}}
    g = {"window": "A1B", "kickoff_utc": KO.isoformat(), "cutoff": cutoff.isoformat(), "state": state,
         "source_qualification": {"status": status, "qualified_at": qualified_at},
         "arms": {"A0": {"players": pl}, "A1B": {"players": pl}} if state == "OK" else {}, "coherence": {"A0": True, "A1B": True},
         "avail_state": {"P1": "EXPECTED_ACTIVE"}, "a1b_state": {"P1": "EXPECTED_ACTIVE"}}
    if state != "OK":
        g["reason"] = "SOURCE_OUTAGE"
    run = run or cutoff.strftime("%Y%m%dT%H%M%SZ")
    doc = {"a1b_version": A.A1B_VERSION, "run_id": run, "generated_at": cutoff.isoformat(), "dry_run": False, "research_only": True,
           "betting_authority": "NONE", "inputs": {"components_sha256": W.FROZEN_COMPONENTS_SHA256}, "games": {gid: g}}
    d = tmp_path / A.REC_PREFIX / "2026-10-18"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{gid}.A1B.{run}.a1b.json.gz"
    raw = gzip.compress(json.dumps(doc).encode(), mtime=0)
    p.write_bytes(raw)
    return {"path": str(p), "sha256": hashlib.sha256(raw).hexdigest(), "doc": doc}


def test_scorer_counts_only_qualified_records_after_qualification(tmp_path):
    ok = _record(tmp_path)
    assert SC.candidates([ok])[0]["reason"] is None
    pre = _record(tmp_path / "b", status="QUALIFYING", qualified_at=None)
    assert "pipeline validation only" in SC.candidates([pre])[0]["reason"]
    before = _record(tmp_path / "c", qualified_at=(KO + timedelta(hours=1)).isoformat())
    assert "not QUALIFIED" in SC.candidates([before])[0]["reason"], "a game kicking off before qualification never counts"
    outside = _record(tmp_path / "d", minutes=100)
    assert SC.candidates([outside])[0]["reason"] == "cutoff outside (T-80, T-35]"
    miss = _record(tmp_path / "e", state="NO_USABLE_SOURCE")
    assert SC.candidates([miss])[0]["reason"].startswith("MISSING:NO_USABLE_SOURCE")


def test_scorer_refuses_collisions_and_stays_collecting_below_64(tmp_path):
    a, b = _record(tmp_path), _record(tmp_path / "x", run="20261018T153000Z")
    sel, coll = SC.select(SC.candidates([a, b]))
    assert sel == {} and coll == [GAME["game_id"]]
    out = SC.score([a], {GAME["game_id"]: {"status": "FINAL", "home_score": 1, "away_score": 0, "players": {"P1": {"targets": 5}}}})
    assert out["A1B"]["evidence_status"] == "COLLECTING" and out["A1B"]["promotion"] is None and SC.MIN_GAMES == 64
    assert out["research_only"] is True and out["betting_authority"] == "NONE" and out["not_pooled_with"] == "A1"


def test_scorer_never_reads_a1_records(tmp_path):
    assert SC.parse_record_name("data/research/wave2/2026-10-08/2026_05_TB_DAL.LATE.20261008T230216Z.wave2.json.gz") is None


# ------------------------------------------------------------------------------------------ integrity of everything else
def test_frozen_wave2_artifacts_are_unchanged():
    def sha(p):
        return hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest()
    assert sha("research/game_script_v2/wave2/PREREGISTRATION.md").startswith("2d4870e3")
    assert sha("research/game_script_v2/wave2/PREREGISTRATION_ADDENDUM.md").startswith("52d2100a")
    assert sha("research/game_script_v2/wave2/components_2026.json") == W.FROZEN_COMPONENTS_SHA256
    assert sha("nfl_edge/sim/wave2_score.py").startswith("f7a0596d")
    assert sha("research/game_script_v2/README.md") and os.popen(
        f"git -C {ROOT} hash-object research/game_script_v2/README.md").read().strip() == "0e1f863ca8a32c3ab4d23da7fb02ff133944db60"


def test_a1b_writes_only_under_its_own_prefix_and_carries_no_authority():
    assert A.SRC_PREFIX.startswith("data/research/wave2_a1b/") and A.REC_PREFIX.startswith("data/research/wave2_a1b/")
    src = open(os.path.join(ROOT, "scripts", "sim", "a1b_capture.py")).read()
    assert '"betting_authority": "NONE"' in src and '"research_only": True' in src and "data/research/wave2/" not in src
    for d in ("handicap", "pricing", "board", "evaluation"):
        base = os.path.join(ROOT, "nfl_edge", d)
        for f in (os.listdir(base) if os.path.isdir(base) else []):
            if f.endswith(".py"):
                text = open(os.path.join(base, f)).read()
                for key in ("a1b", "wave2_a1b", "A1B"):
                    assert key not in text, f"nfl_edge/{d}/{f} reads {key}"
