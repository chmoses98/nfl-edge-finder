"""The report pipeline's fail-closed edges: what gets built, what refuses to build, what may be published.

`latest/` is a *replaced* tree that anyone can click to. That makes one failure mode dominant: a run that
half-worked, publishing this run's `slate.md` beside last run's `games/`, or a stale ledger wearing a fresh
`built_at`. So the rules are (a) a report is complete or it is not a report, (b) nothing incomplete is
published, and (c) the previous good report stays up with its OWN timestamp rather than inheriting the
failed run's.
"""
import gzip
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.handicap.report_outputs import report_paths, verify_report_outputs  # noqa: E402

BUILD = os.path.join(ROOT, "scripts", "handicap", "build_report.py")
PUBLISH = os.path.join(ROOT, "scripts", "ci", "publish_handicap_report.py")

PACKET = {
    "handicap_run_id": "20260909T060000Z", "packet_sha": "abc123", "season": 2026, "week": 1,
    "games": [{"game_id": "2026_01_NE_SEA"}, {"game_id": "2026_01_SF_LA"}],
}


def write_report(d, *, games=("2026_01_NE_SEA", "2026_01_SF_LA"), status="SUCCESS", size=4096,
                 manifest=True, slate=True):
    os.makedirs(os.path.join(d, "games"), exist_ok=True)
    if slate:
        open(os.path.join(d, "slate.md"), "w").write("# slate\n" + "x" * 2048)
    json.dump(PACKET, open(os.path.join(d, "packet.json"), "w"))
    for gid in games:
        open(os.path.join(d, "games", f"{gid}.md"), "w").write("y" * size)
    if manifest:
        json.dump({"report_status": status, "built_at": "2026-09-09T06:00:00+00:00",
                   "packet_sha": "abc123", "season": 2026, "week": 1,
                   "vintages": {"shadow_pricing": {}, "kalshi_capture": {}, "context": {}},
                   "sources": {}, "counts": {}},
                  open(os.path.join(d, "manifest.json"), "w"))
    return d


# ------------------------------------------------------------------- output paths and completeness

def test_output_paths_are_derived_from_the_packet():
    p = report_paths(PACKET)
    assert p["slate"] == "slate.md" and p["packet"] == "packet.json"
    assert p["games"] == ["games/2026_01_NE_SEA.md", "games/2026_01_SF_LA.md"]


def test_a_complete_report_verifies(tmp_path):
    assert verify_report_outputs(write_report(str(tmp_path)), PACKET) == []


def test_a_missing_game_file_is_not_a_report(tmp_path):
    write_report(str(tmp_path), games=("2026_01_NE_SEA",))
    problems = verify_report_outputs(str(tmp_path), PACKET)
    assert problems and "missing" in problems[0]
    assert "games/2026_01_SF_LA.md" in problems[0]


def test_a_truncated_game_file_is_not_a_report(tmp_path):
    write_report(str(tmp_path), size=10)
    assert any("under" in p for p in verify_report_outputs(str(tmp_path), PACKET))


def test_a_missing_slate_is_not_a_report(tmp_path):
    write_report(str(tmp_path), slate=False)
    assert any("slate.md is missing" in p for p in verify_report_outputs(str(tmp_path), PACKET))


def test_an_empty_slate_is_not_a_report(tmp_path):
    write_report(str(tmp_path))
    assert any("no games" in p for p in verify_report_outputs(str(tmp_path), {"games": []}))


# ------------------------------------------------------------------- publish-latest safety

def _publish(src, extra=()):
    return subprocess.run([sys.executable, PUBLISH, "--src", src, "--message", "test", *extra],
                          cwd=ROOT, text=True, capture_output=True)


def test_publishing_refuses_a_directory_with_no_manifest(tmp_path):
    write_report(str(tmp_path), manifest=False)
    r = _publish(str(tmp_path))
    assert r.returncode == 2 and "manifest.json" in r.stderr


def test_publishing_refuses_a_failed_report(tmp_path):
    write_report(str(tmp_path), status="FAILED")
    r = _publish(str(tmp_path))
    assert r.returncode == 2 and "FAILED" in r.stderr


def test_publishing_refuses_a_report_missing_its_slate(tmp_path):
    write_report(str(tmp_path), slate=False)
    r = _publish(str(tmp_path))
    assert r.returncode == 2 and "slate.md missing" in r.stderr


def test_publishing_refuses_a_directory_that_does_not_exist(tmp_path):
    assert _publish(str(tmp_path / "nope")).returncode == 2


def test_latest_is_replaced_whole_so_two_runs_are_never_mixed(tmp_path):
    """Run 1 has a game run 2 does not. After run 2, that file must be gone -- not left behind to be read
    as part of the newer report."""
    from scripts.ci import publish_handicap_report as P  # noqa: PLC0415
    wt = tmp_path / "wt"
    (wt / "latest" / "games").mkdir(parents=True)
    (wt / "latest" / "games" / "STALE.md").write_text("old")
    (wt / "latest" / "slate.md").write_text("old slate")
    src = write_report(str(tmp_path / "src"))
    P.stage(str(wt), src, json.load(open(os.path.join(src, "manifest.json"))), {"captured": {}})
    assert not (wt / "latest" / "games" / "STALE.md").exists()
    assert (wt / "latest" / "games" / "2026_01_NE_SEA.md").exists()
    assert (wt / "latest" / "slate.md").read_text().startswith("# slate")
    assert json.loads((wt / "state" / "horizons.json").read_text()) == {"captured": {}}
    assert (wt / "history" / "index.jsonl").exists()


def test_history_is_one_manifest_line_per_run_not_a_packet_copy(tmp_path):
    from scripts.ci import publish_handicap_report as P  # noqa: PLC0415
    wt = tmp_path / "wt"
    wt.mkdir()
    src = write_report(str(tmp_path / "src"))
    man = json.load(open(os.path.join(src, "manifest.json")))
    for _ in range(3):
        P.stage(str(wt), src, man, None)
    lines = (wt / "history" / "index.jsonl").read_text().strip().split("\n")
    assert len(lines) == 3
    row = json.loads(lines[0])
    assert row["packet_sha"] == "abc123" and "games" not in row


# ------------------------------------------------------------------- stale / missing data, fail closed

def _fake_market_data(tmp_path, *, written_at=None, rows=None):
    md = tmp_path / "md"
    day = md / "data" / "shadow" / "ledger" / "2026-09-09"
    day.mkdir(parents=True)
    stem = day / "20260909T000000Z.shadow-0.4.0"
    with gzip.open(str(stem) + ".observations.jsonl.gz", "wt") as f:
        for r in (rows if rows is not None else [{"season": 2026, "week": 1, "game_id": "2026_01_NE_SEA",
                                                  "ticker": "T"}]):
            f.write(json.dumps(r) + "\n")
    json.dump({"run_id": "20260909T000000Z", "model_version": "shadow-0.4.0",
               "written_at": (written_at or datetime.now(timezone.utc)).isoformat()},
              open(str(stem) + ".ledger_manifest.json", "w"))
    return str(md)


def _build(md, tmp_path, extra=()):
    return subprocess.run(
        [sys.executable, BUILD, "--market-data", md, "--out", str(tmp_path / "out"),
         "--season", "2026", "--week", "1", *extra],
        cwd=ROOT, text=True, capture_output=True)


def test_no_ledger_at_all_fails_closed(tmp_path):
    (tmp_path / "empty").mkdir()
    r = _build(str(tmp_path / "empty"), tmp_path)
    assert r.returncode == 2
    assert not (tmp_path / "out" / "manifest.json").exists()


def test_a_stale_ledger_fails_closed_rather_than_looking_current(tmp_path):
    md = _fake_market_data(tmp_path, written_at=datetime.now(timezone.utc) - timedelta(hours=5))
    r = _build(md, tmp_path, ["--max-ledger-age-min", "60"])
    assert r.returncode == 3, r.stderr
    assert "older than" in r.stderr or "old" in r.stderr
    assert not (tmp_path / "out" / "manifest.json").exists()


def test_a_fresh_ledger_passes_the_age_gate(tmp_path):
    """The same tree, dated now, gets past freshness -- so the refusal above is about age, not plumbing."""
    md = _fake_market_data(tmp_path, rows=[])
    r = _build(md, tmp_path, ["--max-ledger-age-min", "60"])
    assert r.returncode == 4, r.stderr        # no rows for the week: the NEXT gate, not the age one


def test_a_ledger_with_no_rows_for_the_week_fails_closed(tmp_path):
    md = _fake_market_data(tmp_path, rows=[{"season": 2026, "week": 9, "game_id": "x", "ticker": "T"}])
    r = _build(md, tmp_path)
    assert r.returncode == 4
    assert not (tmp_path / "out" / "manifest.json").exists()


def test_a_failed_build_writes_no_manifest_so_nothing_can_be_published(tmp_path):
    (tmp_path / "empty").mkdir()
    _build(str(tmp_path / "empty"), tmp_path)
    r = _publish(str(tmp_path / "out"))
    assert r.returncode == 2


def test_the_offseason_can_be_a_skip_rather_than_a_failure(tmp_path):
    md = _fake_market_data(tmp_path)
    sched = tmp_path / "games.csv"
    sched.write_text("game_id,season,game_type,week,gameday,weekday,gametime,away_team,home_team,result\n"
                     "2020_01_A_B,2020,REG,1,2020-09-13,Sunday,13:00,A,B,3\n")
    r = subprocess.run(
        [sys.executable, BUILD, "--market-data", md, "--out", str(tmp_path / "out"),
         "--schedule", str(sched), "--skip-if-no-slate"], cwd=ROOT, text=True, capture_output=True)
    assert r.returncode == 5
    assert "no active slate" in r.stderr
    r2 = subprocess.run(
        [sys.executable, BUILD, "--market-data", md, "--out", str(tmp_path / "out2"),
         "--schedule", str(sched)], cwd=ROOT, text=True, capture_output=True)
    assert r2.returncode == 6, "without --skip-if-no-slate an unresolvable week is a failure"


def test_an_unreadable_schedule_is_a_refusal_not_a_guessed_week(tmp_path):
    md = _fake_market_data(tmp_path)
    r = subprocess.run(
        [sys.executable, BUILD, "--market-data", md, "--out", str(tmp_path / "out"),
         "--schedule", str(tmp_path / "does-not-exist.csv")], cwd=ROOT, text=True, capture_output=True)
    assert r.returncode == 7
    assert "schedule" in r.stderr.lower()


# ------------------------------------------------------------------- the report branch does not bloat

def _git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True, check=True).stdout


def _repo_with_remote(tmp_path):
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    (repo / "README.md").write_text("code")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "init")
    _git(repo, "remote", "add", "origin", str(remote))
    _git(repo, "push", "-q", "-u", "origin", "main")
    return repo


def test_the_report_branch_stays_one_commit_however_often_it_publishes(tmp_path):
    """`latest/packet.json` is ~25MB. Committing a replacement every two hours through an NFL season is
    ~2GB of history per week -- the "hundreds of duplicate large packet snapshots" this design exists to
    avoid, arrived at by replacement instead of accumulation. Each publish rewrites the branch as a fresh
    root commit and carries the manifest index forward."""
    repo = _repo_with_remote(tmp_path)
    src = write_report(str(tmp_path / "src"))
    for i in range(3):
        man = json.load(open(os.path.join(src, "manifest.json")))
        man["built_at"] = f"2026-09-09T0{i}:00:00+00:00"
        json.dump(man, open(os.path.join(src, "manifest.json"), "w"))
        r = subprocess.run([sys.executable, PUBLISH, "--src", src, "--repo", str(repo),
                            "--message", f"publish {i}"], text=True, capture_output=True)
        assert r.returncode == 0, r.stdout + r.stderr

    _git(repo, "fetch", "-q", "origin", "handicap-reports")
    commits = _git(repo, "rev-list", "--count", "origin/handicap-reports").strip()
    assert commits == "1", f"the report branch accumulated {commits} commits of 25MB packets"

    files = _git(repo, "ls-tree", "-r", "--name-only", "origin/handicap-reports").split()
    assert "latest/slate.md" in files
    assert "latest/games/2026_01_NE_SEA.md" in files
    assert "history/index.jsonl" in files

    index = _git(repo, "show", "origin/handicap-reports:history/index.jsonl").strip().split("\n")
    assert len(index) == 3, "the manifest index did not survive the branch rewrite"
    assert [json.loads(x)["built_at"] for x in index] == [
        "2026-09-09T00:00:00+00:00", "2026-09-09T01:00:00+00:00", "2026-09-09T02:00:00+00:00"]


def test_a_game_that_leaves_the_slate_leaves_the_published_report(tmp_path):
    """Two runs must never be mixed: last run's game file has to be gone, not merely superseded."""
    repo = _repo_with_remote(tmp_path)
    first = write_report(str(tmp_path / "a"), games=("2026_01_NE_SEA", "2026_01_SF_LA"))
    assert subprocess.run([sys.executable, PUBLISH, "--src", first, "--repo", str(repo),
                           "--message", "first"], capture_output=True).returncode == 0
    second = str(tmp_path / "b")
    json.dump({**PACKET, "games": [{"game_id": "2026_01_NE_SEA"}]},
              open(os.path.join(write_report(second, games=("2026_01_NE_SEA",)), "packet.json"), "w"))
    assert subprocess.run([sys.executable, PUBLISH, "--src", second, "--repo", str(repo),
                           "--message", "second"], capture_output=True).returncode == 0
    _git(repo, "fetch", "-q", "origin", "handicap-reports")
    files = _git(repo, "ls-tree", "-r", "--name-only", "origin/handicap-reports").split()
    assert "latest/games/2026_01_NE_SEA.md" in files
    assert "latest/games/2026_01_SF_LA.md" not in files


def test_the_horizon_state_survives_a_publish_that_does_not_supply_one(tmp_path):
    """The 2-hourly cycle publishes with no horizon state. It must not wipe the conductor's record."""
    repo = _repo_with_remote(tmp_path)
    src = write_report(str(tmp_path / "src"))
    state = tmp_path / "hz.json"
    state.write_text(json.dumps({"captured": {"2026-REG-01|20260913T1700Z|T-90m": {"status": "CAPTURED"}}}))
    assert subprocess.run([sys.executable, PUBLISH, "--src", src, "--repo", str(repo),
                           "--horizon-state", str(state), "--message", "horizon run"],
                          capture_output=True).returncode == 0
    assert subprocess.run([sys.executable, PUBLISH, "--src", src, "--repo", str(repo),
                           "--message", "shadow cycle"], capture_output=True).returncode == 0
    _git(repo, "fetch", "-q", "origin", "handicap-reports")
    carried = json.loads(_git(repo, "show", "origin/handicap-reports:state/horizons.json"))
    assert "2026-REG-01|20260913T1700Z|T-90m" in carried["captured"], (
        "a shadow-cycle publish erased the horizon capture record, so every horizon would fire again")


# ------------------------------------------------------------------- freshness gates, end to end

def _md_with_capture(tmp_path, *, snapshot=None, written=None, rows=None, context_run=None,
                     context_failed=()):
    """A market-data tree whose ledger names the Kalshi capture it was priced from."""
    md = tmp_path / "md"
    day = md / "data" / "shadow" / "ledger" / "2026-09-09"
    day.mkdir(parents=True)
    stem = day / "20260909T000000Z.shadow-0.4.0"
    with gzip.open(str(stem) + ".observations.jsonl.gz", "wt") as f:
        for r in (rows if rows is not None else [{"season": 2026, "week": 1, "game_id": "2026_01_NE_SEA",
                                                  "ticker": "T"}]):
            f.write(json.dumps(r) + "\n")
    now = datetime.now(timezone.utc)
    man = {"run_id": "20260909T000000Z", "model_version": "shadow-0.4.0",
           "written_at": (written or now).isoformat()}
    if snapshot is not None:
        man["snapshot_run_id"] = snapshot.strftime("%Y%m%dT%H%M%SZ")
    json.dump(man, open(str(stem) + ".ledger_manifest.json", "w"))
    if context_run:
        cd = md / "data" / "context" / "2026-09-09"
        cd.mkdir(parents=True)
        json.dump({"run_id": context_run, "sources": {}, "failed_closed": list(context_failed)},
                  open(cd / f"{context_run}.manifest.json", "w"))
    return str(md)


def test_a_fresh_ledger_priced_from_a_stale_kalshi_capture_is_refused(tmp_path):
    """The gate the ledger-age check could not see: written_at is seconds old, the market is 90m old."""
    now = datetime.now(timezone.utc)
    md = _md_with_capture(tmp_path, snapshot=now - timedelta(minutes=90), written=now)
    r = _build(md, tmp_path, ["--max-ledger-age-min", "45", "--max-capture-age-min", "30"])
    assert r.returncode == 9, r.stderr
    assert "the ledger is fresh but the market it quotes is not" in r.stderr
    assert not (tmp_path / "out" / "manifest.json").exists()


def test_the_same_tree_with_a_fresh_capture_gets_past_the_gate(tmp_path):
    """So the refusal above is about the capture, not about plumbing."""
    now = datetime.now(timezone.utc)
    md = _md_with_capture(tmp_path, snapshot=now - timedelta(minutes=5), written=now, rows=[])
    r = _build(md, tmp_path, ["--max-ledger-age-min", "45", "--max-capture-age-min", "30"])
    assert r.returncode == 4, r.stderr        # no rows for the week: a LATER gate, not the capture one


def test_a_ledger_that_does_not_name_its_capture_is_refused(tmp_path):
    """'I could not check' must never resolve to 'it is fine'."""
    md = _md_with_capture(tmp_path, snapshot=None, written=datetime.now(timezone.utc))
    r = _build(md, tmp_path, ["--max-capture-age-min", "30"])
    assert r.returncode == 9
    assert "cannot be established" in r.stderr


def test_a_force_fresh_run_fails_when_its_context_capture_produced_nothing(tmp_path):
    """A dead capture must not fall back to older published context and still be called fresh."""
    now = datetime.now(timezone.utc)
    md = _md_with_capture(tmp_path, snapshot=now, written=now)
    r = _build(md, tmp_path, ["--require-context-run-id", "20260909T115900Z"])
    assert r.returncode == 10, r.stderr
    assert "wrote no manifest" in r.stderr
    assert not (tmp_path / "out" / "manifest.json").exists()


def test_a_force_fresh_run_fails_when_its_context_capture_failed_closed(tmp_path):
    now = datetime.now(timezone.utc)
    md = _md_with_capture(tmp_path, snapshot=now, written=now, context_run="20260909T115900Z",
                          context_failed=["espn injuries unavailable"])
    r = _build(md, tmp_path, ["--require-context-run-id", "20260909T115900Z"])
    assert r.returncode == 10, r.stderr
    assert "failed closed" in r.stderr
    assert not (tmp_path / "out" / "manifest.json").exists()


def test_a_refused_run_cannot_publish_or_mark_a_horizon(tmp_path):
    """Both downstream effects hang off manifest.json, which a refusal never writes."""
    now = datetime.now(timezone.utc)
    md = _md_with_capture(tmp_path, snapshot=now - timedelta(minutes=90), written=now)
    _build(md, tmp_path, ["--max-capture-age-min", "30"])
    assert _publish(str(tmp_path / "out")).returncode == 2


# ------------------------------------------------------------------- latest/ never moves backward

def _report_with_ledger(d, written, **kw):
    write_report(d, **kw)
    man = json.load(open(os.path.join(d, "manifest.json")))
    man["built_at"] = written
    man["vintages"] = {"shadow_pricing": {"written_at": written}, "kalshi_capture": {}, "context": {}}
    json.dump(man, open(os.path.join(d, "manifest.json"), "w"))
    return d


def test_latest_never_regresses_to_an_older_ledger_snapshot(tmp_path):
    """The shadow cycle and the horizon conductor are in different concurrency groups and can overlap.
    A cycle that started before a T-30m horizon run but finished after it must not roll latest/ back to
    the older market -- at the worst possible moment. --force-with-lease protects the other job's COMMIT;
    it says nothing about whether our CONTENT is older."""
    repo = _repo_with_remote(tmp_path)
    newer = _report_with_ledger(str(tmp_path / "new"), "2026-09-13T15:35:00+00:00")
    older = _report_with_ledger(str(tmp_path / "old"), "2026-09-13T14:37:00+00:00")
    assert subprocess.run([sys.executable, PUBLISH, "--src", newer, "--repo", str(repo),
                           "--message", "horizon T-30m"], capture_output=True).returncode == 0
    r = subprocess.run([sys.executable, PUBLISH, "--src", older, "--repo", str(repo),
                        "--message", "shadow cycle, finished later"], text=True, capture_output=True)
    assert r.returncode == 0, r.stderr
    assert "does not move backward" in r.stdout

    _git(repo, "fetch", "-q", "origin", "handicap-reports")
    published = json.loads(_git(repo, "show", "origin/handicap-reports:latest/manifest.json"))
    assert published["vintages"]["shadow_pricing"]["written_at"] == "2026-09-13T15:35:00+00:00"


def test_the_late_older_run_is_still_recorded_in_history(tmp_path):
    """It ran, and any horizon it satisfied is genuinely satisfied -- by a fresher report. Dropping the
    record would make the horizon fire again on the next wake for no benefit."""
    repo = _repo_with_remote(tmp_path)
    newer = _report_with_ledger(str(tmp_path / "new"), "2026-09-13T15:35:00+00:00")
    older = _report_with_ledger(str(tmp_path / "old"), "2026-09-13T14:37:00+00:00")
    state = tmp_path / "hz.json"
    state.write_text(json.dumps({"captured": {"2026-REG-01|20260913T1700Z|T-90m": {"status": "CAPTURED"}}}))
    subprocess.run([sys.executable, PUBLISH, "--src", newer, "--repo", str(repo), "--message", "new"],
                   capture_output=True, check=True)
    subprocess.run([sys.executable, PUBLISH, "--src", older, "--repo", str(repo), "--message", "old",
                    "--horizon-state", str(state)], capture_output=True, check=True)
    _git(repo, "fetch", "-q", "origin", "handicap-reports")
    index = _git(repo, "show", "origin/handicap-reports:history/index.jsonl").strip().split("\n")
    assert len(index) == 2, "the superseded run vanished from the history index"
    carried = json.loads(_git(repo, "show", "origin/handicap-reports:state/horizons.json"))
    assert "2026-REG-01|20260913T1700Z|T-90m" in carried["captured"]


def test_a_newer_report_replaces_latest_normally(tmp_path):
    """The guard must not become a ratchet that blocks ordinary refreshes."""
    repo = _repo_with_remote(tmp_path)
    older = _report_with_ledger(str(tmp_path / "old"), "2026-09-13T14:37:00+00:00")
    newer = _report_with_ledger(str(tmp_path / "new"), "2026-09-13T16:37:00+00:00")
    subprocess.run([sys.executable, PUBLISH, "--src", older, "--repo", str(repo), "--message", "a"],
                   capture_output=True, check=True)
    subprocess.run([sys.executable, PUBLISH, "--src", newer, "--repo", str(repo), "--message", "b"],
                   capture_output=True, check=True)
    _git(repo, "fetch", "-q", "origin", "handicap-reports")
    published = json.loads(_git(repo, "show", "origin/handicap-reports:latest/manifest.json"))
    assert published["vintages"]["shadow_pricing"]["written_at"] == "2026-09-13T16:37:00+00:00"


def test_an_equally_fresh_report_still_publishes(tmp_path):
    """Two runs off the same ledger snapshot: the later one wins, as before. Only strictly older is
    refused, so a re-render of the same snapshot is not blocked."""
    repo = _repo_with_remote(tmp_path)
    a = _report_with_ledger(str(tmp_path / "a"), "2026-09-13T14:37:00+00:00")
    b = _report_with_ledger(str(tmp_path / "b"), "2026-09-13T14:37:00+00:00",
                            games=("2026_01_NE_SEA", "2026_01_SF_LA"))
    subprocess.run([sys.executable, PUBLISH, "--src", a, "--repo", str(repo), "--message", "a"],
                   capture_output=True, check=True)
    r = subprocess.run([sys.executable, PUBLISH, "--src", b, "--repo", str(repo), "--message", "b"],
                       text=True, capture_output=True)
    assert r.returncode == 0
    assert "does not move backward" not in r.stdout


# ------------------------------------------------------------------- monotonicity on CRITICAL SOURCES

def _report_with_vintages(d, *, ledger, market=None, context=None, **kw):
    """A report whose manifest carries the evidence vintages, not just the artifact time."""
    write_report(d, **kw)
    man = json.load(open(os.path.join(d, "manifest.json")))
    man["built_at"] = ledger
    man["vintages"] = {
        "shadow_pricing": {"written_at": ledger},
        "kalshi_capture": ({"queried_at": market} if market else {}),
        "context": ({"captured_at": context} if context else {}),
    }
    json.dump(man, open(os.path.join(d, "manifest.json"), "w"))
    return d


def _publish_repo(repo, src, message, extra=()):
    return subprocess.run([sys.executable, PUBLISH, "--src", src, "--repo", str(repo),
                           "--message", message, *extra], text=True, capture_output=True)


def _published(repo):
    _git(repo, "fetch", "-q", "origin", "handicap-reports")
    return json.loads(_git(repo, "show", "origin/handicap-reports:latest/manifest.json"))


T = "2026-09-13T%s:00+00:00".__mod__


def _scenario(tmp_path, published_kw, incoming_kw, names=("2026_01_NE_SEA",)):
    repo = _repo_with_remote(tmp_path)
    first = _report_with_vintages(str(tmp_path / "pub"), games=names, **published_kw)
    assert _publish_repo(repo, first, "published").returncode == 0
    second = _report_with_vintages(str(tmp_path / "inc"), games=names, **incoming_kw)
    r = _publish_repo(repo, second, "incoming")
    assert r.returncode == 0, r.stderr
    return repo, r


# The reference case from review: every field the old guard looked at says "newer".
PUBLISHED_T30 = {"ledger": T("15:35"), "market": T("15:30"), "context": T("15:34")}


def test_A_a_newer_ledger_priced_from_an_older_kalshi_capture_cannot_replace_latest(tmp_path):
    """The defect the ledger-time guard could not see. written_at 15:40 > 15:35, and the market it quotes
    is 25 minutes older than what is already published."""
    repo, r = _scenario(tmp_path, PUBLISHED_T30,
                        {"ledger": T("15:40"), "market": T("15:05"), "context": T("15:36")})
    assert "does not move backward" in r.stdout
    assert "Kalshi capture" in r.stdout
    assert _published(repo)["vintages"]["kalshi_capture"]["queried_at"] == T("15:30")


def test_B_a_newer_ledger_and_market_but_older_context_cannot_replace_latest(tmp_path):
    """Market is fine; the injuries, weather and availability in it are 44 minutes staler."""
    repo, r = _scenario(tmp_path, PUBLISHED_T30,
                        {"ledger": T("15:40"), "market": T("15:31"), "context": T("14:50")})
    assert "does not move backward" in r.stdout
    assert "context capture confirmation" in r.stdout
    assert _published(repo)["vintages"]["context"]["captured_at"] == T("15:34")


def test_C_the_same_kalshi_capture_with_newer_context_replaces_latest(tmp_path):
    """A re-render off the same market with a newer injury confirmation is a strict improvement."""
    repo, r = _scenario(tmp_path, PUBLISHED_T30,
                        {"ledger": T("15:45"), "market": T("15:30"), "context": T("15:44")})
    assert "does not move backward" not in r.stdout
    assert _published(repo)["vintages"]["context"]["captured_at"] == T("15:44")


def test_D_a_newer_kalshi_capture_with_the_same_context_replaces_latest(tmp_path):
    repo, r = _scenario(tmp_path, PUBLISHED_T30,
                        {"ledger": T("15:45"), "market": T("15:44"), "context": T("15:34")})
    assert "does not move backward" not in r.stdout
    assert _published(repo)["vintages"]["kalshi_capture"]["queried_at"] == T("15:44")


def test_E_newer_everywhere_is_an_ordinary_replacement(tmp_path):
    repo, r = _scenario(tmp_path, PUBLISHED_T30,
                        {"ledger": T("16:40"), "market": T("16:35"), "context": T("16:34")})
    assert "does not move backward" not in r.stdout
    assert _published(repo)["vintages"]["shadow_pricing"]["written_at"] == T("16:40")


def test_F_a_blocked_replacement_is_still_recorded_and_keeps_horizon_state(tmp_path):
    """The run happened and any horizon it satisfied IS satisfied -- by the fresher report already up.
    Dropping either would make the horizon fire again for no benefit."""
    repo = _repo_with_remote(tmp_path)
    first = _report_with_vintages(str(tmp_path / "pub"), **PUBLISHED_T30)
    assert _publish_repo(repo, first, "T-30m horizon").returncode == 0
    state = tmp_path / "hz.json"
    state.write_text(json.dumps({"captured": {"2026-REG-01|20260913T1700Z|T-30m": {"status": "CAPTURED"}}}))
    stale = _report_with_vintages(str(tmp_path / "inc"),
                                  ledger=T("15:40"), market=T("15:05"), context=T("14:50"))
    r = _publish_repo(repo, stale, "shadow cycle, finished later", ["--horizon-state", str(state)])
    assert r.returncode == 0, "a superseded run must succeed, not fail the workflow"
    assert "does not move backward" in r.stdout

    _git(repo, "fetch", "-q", "origin", "handicap-reports")
    index = _git(repo, "show", "origin/handicap-reports:history/index.jsonl").strip().split("\n")
    assert len(index) == 2, "the superseded run vanished from the history index"
    carried = json.loads(_git(repo, "show", "origin/handicap-reports:state/horizons.json"))
    assert "2026-REG-01|20260913T1700Z|T-30m" in carried["captured"]
    assert _published(repo)["vintages"]["kalshi_capture"]["queried_at"] == T("15:30")


def test_a_report_that_stops_recording_a_source_cannot_replace_one_that_does(tmp_path):
    """Non-regression has to be shown, not assumed, once there is a baseline to show it against."""
    repo, r = _scenario(tmp_path, PUBLISHED_T30, {"ledger": T("16:40")})
    assert "non-regression cannot be shown" in r.stdout
    assert _published(repo)["vintages"]["kalshi_capture"]["queried_at"] == T("15:30")


def test_a_legacy_published_report_without_source_vintages_does_not_freeze_the_branch(tmp_path):
    """`handicap-reports` already carries a report published before these fields existed. A guard that
    refused everything it could not compare would leave it stuck there forever."""
    repo, r = _scenario(tmp_path, {"ledger": T("15:35")},
                        {"ledger": T("15:40"), "market": T("15:38"), "context": T("15:37")})
    assert "does not move backward" not in r.stdout
    assert _published(repo)["vintages"]["kalshi_capture"]["queried_at"] == T("15:38")


def test_the_ledger_time_only_breaks_a_tie_between_identical_sources(tmp_path):
    """Same market, same context, older ledger: a re-render from a staler derived artifact adds nothing."""
    repo, r = _scenario(tmp_path, PUBLISHED_T30,
                        {"ledger": T("15:20"), "market": T("15:30"), "context": T("15:34")})
    assert "the critical sources are unchanged" in r.stdout
    assert _published(repo)["vintages"]["shadow_pricing"]["written_at"] == T("15:35")


def test_an_older_ledger_does_not_block_strictly_fresher_evidence(tmp_path):
    """The tie-break must not outrank the critical sources it is subordinate to."""
    repo, r = _scenario(tmp_path, PUBLISHED_T30,
                        {"ledger": T("15:20"), "market": T("15:44"), "context": T("15:44")})
    assert "does not move backward" not in r.stdout
    assert _published(repo)["vintages"]["kalshi_capture"]["queried_at"] == T("15:44")


def test_the_source_vintages_fall_back_to_the_run_stamp_forms():
    """`queried_at` and `captured_at` are the primary keys; `snapshot_run_id` and the last `captures_used`
    entry are the same instants in run-stamp form and stand in when a manifest carries only those."""
    sys.path.insert(0, os.path.join(ROOT, "scripts", "ci"))
    from publish_handicap_report import source_vintages  # noqa: PLC0415

    v = source_vintages({"vintages": {
        "kalshi_capture": {"snapshot_run_id": "20260913T153000Z"},
        "context": {"captures_used": ["20260913T140000Z", "20260913T153400Z"]},
        "shadow_pricing": {"written_at": "2026-09-13T15:35:00+00:00"}}})
    assert v["market"].isoformat() == "2026-09-13T15:30:00+00:00"
    assert v["context"].isoformat() == "2026-09-13T15:34:00+00:00"
    assert v["ledger"].isoformat() == "2026-09-13T15:35:00+00:00"


def test_change_suppressed_content_vintage_is_never_the_freshness_marker():
    """A run that re-confirmed byte-identical injuries writes no blob and carries an OLDER content
    vintage while being strictly newer confirmation. Ranking on it would treat a fresh re-confirmation as
    a regression and refuse to publish it."""
    sys.path.insert(0, os.path.join(ROOT, "scripts", "ci"))
    from publish_handicap_report import source_vintages, would_regress  # noqa: PLC0415

    def man(confirmed, content):
        return {"vintages": {"kalshi_capture": {"queried_at": "2026-09-13T15:30:00+00:00"},
                             "context": {"captured_at": confirmed},
                             "shadow_pricing": {"written_at": confirmed}},
                "injuries_content_vintage": content}

    published = man("2026-09-13T15:34:00+00:00", "2026-09-13T15:34:00+00:00")
    # Newer confirmation, older content hash vintage because nothing changed.
    incoming = man("2026-09-13T15:50:00+00:00", "2026-09-13T04:00:00+00:00")
    assert source_vintages(incoming)["context"].isoformat() == "2026-09-13T15:50:00+00:00"
    assert would_regress(incoming, published) is None
