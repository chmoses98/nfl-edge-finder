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
