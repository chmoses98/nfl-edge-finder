"""Date-bounded, checkpointed closes recovery: window planning, resume, partial weeks, duplicates, failed publication,
provenance and idempotence. The pairing driver is replaced by tests/_stub_pair_closes.py; git, the sparse partial clone
and the atomic publish run for real against a local bare repo standing in for `market-data`."""
import gzip
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

import pytest

from nfl_edge.shadow import closes_recovery as R
from nfl_edge.shadow.quote_history import capture_days

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CLI = os.path.join(ROOT, "scripts", "shadow_v2", "recover_closes_v2.py")
STUB = os.path.join(ROOT, "tests", "_stub_pair_closes.py")
NOW = "2026-11-03T12:00:00+00:00"
GAMES = [("2026_05_AAA_BBB", "2026-10-11", "13:00"), ("2026_05_CCC_DDD", "2026-10-11", "16:25"),
         ("2026_05_EEE_FFF", "2026-10-12", "20:15"), ("2026_05_GGG_HHH", "2026-10-13", "20:15")]


def git(cwd, *args):
    return subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "-c", "commit.gpgsign=false", *args], cwd=cwd,
                          check=True, capture_output=True, text=True).stdout


@pytest.fixture
def env(tmp_path):
    origin, seed, repo = tmp_path / "origin.git", tmp_path / "seed", tmp_path / "repo"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    git(origin, "config", "uploadpack.allowFilter", "true")
    git(origin, "config", "uploadpack.allowAnySHA1InWant", "true")
    subprocess.run(["git", "clone", "-q", f"file://{origin}", str(seed)], check=True, capture_output=True)
    (seed / "README").write_text("main\n")
    git(seed, "add", "-A"); git(seed, "commit", "-q", "-m", "main"); git(seed, "push", "-q", "origin", "HEAD:main")
    git(seed, "checkout", "-q", "-b", "market-data")
    cap = seed / "data" / "kalshi" / "capture"
    for d in range(20, 31):                                    # Sep 20..30
        day = cap / f"2026-09-{d:02d}"; day.mkdir(parents=True)
        (day / "r.quotes.jsonl").write_text("q\n"); (day / "r.trades.jsonl").write_text("TRADES\n")
        (day / "r.manifest.json").write_text("{}"); (day / "r.openset.json").write_text("{}")
    for d in range(1, 14):
        day = cap / f"2026-10-{d:02d}"; day.mkdir(parents=True)
        (day / "r.quotes.jsonl").write_text("q\n"); (day / "r.trades.jsonl").write_text("TRADES\n")
        (day / "r.manifest.json").write_text("{}"); (day / "r.openset.json").write_text("{}")
    (cap / "state.json").write_text("{}")
    pj = seed / "data" / "shadow" / "v2" / "projections"
    for day in ["2026-09-12", "2026-09-28", "2026-10-02", "2026-10-11", "2026-10-13", "2026-10-20"]:
        (pj / day).mkdir(parents=True); (pj / day / "s.BOARD_V2.projections.jsonl.gz").write_bytes(b"x")
    (seed / "data" / "shadow" / "v2" / "projection_index").mkdir(parents=True)
    (seed / "data" / "shadow" / "v2" / "projection_index" / "keep.json").write_text("{}")
    git(seed, "add", "-A"); git(seed, "commit", "-q", "-m", "market-data"); git(seed, "push", "-q", "origin", "market-data")
    subprocess.run(["git", "clone", "-q", "-b", "main", f"file://{origin}", str(repo)], check=True, capture_output=True)
    sched = tmp_path / "games.csv"
    sched.write_text("game_id,season,week,game_type,gameday,gametime\n" +
                     "".join(f"{g},2026,5,REG,{d},{t}\n" for g, d, t in GAMES))
    return {"origin": origin, "seed": seed, "repo": repo, "sched": sched, "tmp": tmp_path}


def run(env, *extra, stub_env=None, weeks="5", now=NOW):
    e = {**os.environ, "RECOVERY_PAIR_SCRIPT": STUB, **(stub_env or {})}
    rd = env["tmp"] / "report"
    cmd = [sys.executable, CLI, "run", "--weeks", weeks, "--season", "2026", "--schedule", str(env["sched"]), "--repo", str(env["repo"]),
           "--workdir", str(env["tmp"] / "win"), "--stage", str(env["tmp"] / "stage"), "--report-dir", str(rd), "--now", now,
           "--chunk-games", "2", "--github-output", "", "--summary", "", *extra]
    r = subprocess.run(cmd, env=e, capture_output=True, text=True)
    rep = json.load(open(rd / "recovery_report.json")) if (rd / "recovery_report.json").exists() else None
    return r, rep


def tip_tree(env, *prefix):
    git(env["repo"], "fetch", "-q", "--depth=1", "--filter=blob:none", "origin", "+market-data:refs/remotes/origin/market-data")
    return R.ls_tree(str(env["repo"]), "origin/market-data", *(prefix or ("data",)))


def origin_tip(env):
    return git(env["origin"], "rev-parse", "market-data").strip()


# ---------------------------------------------------------------------------------------------- planning
def test_window_matches_the_driver_quote_bound_and_excludes_trades():
    games = [R.Game("2026_05_AAA_BBB", datetime(2026, 10, 11, 17, 0, tzinfo=timezone.utc))]
    win = R.window_for(games)
    assert win.capture_days[0] == "2026-09-27" and win.capture_days[-1] == "2026-10-11"
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        for day in ["2026-09-26", "2026-09-27", "2026-10-11", "2026-10-12"]:
            os.makedirs(os.path.join(d, day))
        want = [os.path.basename(x) for x in capture_days(d, "2026-10-11T17:00:00+00:00", 14)]
    assert [x for x in want if x in win.capture_days] == want and "2026-09-26" not in win.capture_days
    assert not R.selected("data/kalshi/capture/2026-10-01/r.trades.jsonl", win)
    assert not R.selected("data/kalshi/capture/2026-10-01/r.books.jsonl", win)
    assert R.selected("data/kalshi/capture/2026-10-01/r.quotes.jsonl", win)
    assert not R.selected("data/kalshi/capture/2026-10-15/r.quotes.jsonl", win)
    assert R.selected("data/kalshi/capture/2025-01-01/r.openset.json", win)


def test_parse_weeks():
    assert R.parse_weeks("5-8") == [5, 6, 7, 8] and R.parse_weeks("6, 5") == [5, 6]
    with pytest.raises(ValueError):
        R.parse_weeks("8-5")


def test_sparse_checkout_materialises_exactly_the_planned_files(env):
    games = R.load_week_games(str(env["sched"]), 2026, 5)
    win = R.window_for(games)
    R.fetch_tip(str(env["repo"]))
    m = R.materialise(str(env["repo"]), str(env["tmp"] / "win"), R.sparse_patterns(win))
    on_disk = {os.path.relpath(os.path.join(d, f), env["tmp"] / "win") for d, _s, fs in os.walk(env["tmp"] / "win") for f in fs if f != ".git"}
    tree = R.ls_tree(str(env["repo"]), "origin/market-data", "data")
    assert on_disk == {p for p in tree if R.selected(p, win)}
    assert not any("trades" in p for p in on_disk) and m["worktree_bytes"] > 0
    assert "data/shadow/v2/projections/2026-09-12/s.BOARD_V2.projections.jsonl.gz" not in on_disk
    assert "data/shadow/v2/projections/2026-10-20/s.BOARD_V2.projections.jsonl.gz" not in on_disk


# ---------------------------------------------------------------------------------------------- recovery
def test_full_week_publishes_games_then_checkpoint_and_rerun_is_a_noop(env):
    r, rep = run(env)
    assert r.returncode == 0, r.stdout + r.stderr
    w = rep["weeks"][0]
    assert w["status"] == "COMPLETE" and w["recovered"] is True
    tree = tip_tree(env)
    for g, _d, _t in GAMES:
        assert len(R.existing_batches(tree, g)["close"]) == 1 and len(R.existing_batches(tree, g)["clv"]) == 1
    cp_path = R.checkpoint_path(2026, 5)
    assert cp_path in tree
    cp = json.loads(git(env["repo"], "cat-file", "blob", tree[cp_path][0]))
    assert R.verify_checkpoint(cp, tree) == [] and cp["status"] == "COMPLETE" and cp["mode"] == "LIVE"
    tip = origin_tip(env)
    r2, rep2 = run(env, stub_env={"STUB_MODE": "fail_after_1"})         # a stub that would fail if it were ever called
    assert r2.returncode == 0 and rep2["weeks"][0]["status"] == "SKIPPED_COMPLETE"
    assert rep2["weeks"][0]["bytes_fetched"] == 0 and origin_tip(env) == tip, "an idempotent rerun must not touch the branch"


def test_interrupted_run_resumes_without_duplicates(env):
    r, rep = run(env, stub_env={"STUB_MODE": "fail_after_1"})
    assert r.returncode == 1 and "pair_closes_v2 exited 3" in r.stdout
    tree = tip_tree(env)
    assert R.checkpoint_path(2026, 5) not in tree, "nothing is complete after a failed chunk"
    assert not any(p.startswith(R.CHECKPOINT_DIR) for p in tree)
    r, rep = run(env)
    assert r.returncode == 0, r.stdout + r.stderr
    tree = tip_tree(env)
    assert rep["weeks"][0]["status"] == "COMPLETE" and R.checkpoint_path(2026, 5) in tree
    for g, _d, _t in GAMES:
        assert len(R.existing_batches(tree, g)["close"]) == 1, "a resumed run must not write a second batch"


def test_partial_week_leaves_existing_records_untouched(env):
    seed = env["seed"]
    pre = seed / "data" / "shadow" / "v2" / "closes" / "2026_05_AAA_BBB"
    pre.mkdir(parents=True)
    f = pre / "close-2.1.0.20261012T000000Z.closes_v2.jsonl.gz"
    with gzip.open(f, "wt") as g:
        g.write(json.dumps({"ticker": "X", "close_quality": "STALE", "close_age_seconds": 20000.0, "close_id": "old"}) + "\n")
    git(seed, "add", "-A"); git(seed, "commit", "-q", "-m", "pre-existing"); git(seed, "push", "-q", "origin", "market-data")
    before = R.git_blob_sha1(str(f))
    r, rep = run(env)
    assert r.returncode == 0, r.stdout + r.stderr
    w = rep["weeks"][0]
    assert w["already_paired"] == ["2026_05_AAA_BBB"] and len(w["to_recover"]) == 3
    tree = tip_tree(env)
    assert tree[f"data/shadow/v2/closes/2026_05_AAA_BBB/{f.name}"][0] == before
    assert len(R.existing_batches(tree, "2026_05_AAA_BBB")["close"]) == 1
    cp = json.loads(git(env["repo"], "cat-file", "blob", tree[R.checkpoint_path(2026, 5)][0]))
    assert cp["games"]["2026_05_AAA_BBB"]["status"] == "PRE_EXISTING" and cp["games"]["2026_05_CCC_DDD"]["status"] == "RECOVERED"


def test_week_not_fully_kicked_off_is_never_marked_complete(env):
    r, rep = run(env, now="2026-10-12T00:00:00+00:00")
    assert r.returncode == 0
    w = rep["weeks"][0]
    assert w["status"] == "PARTIAL" and len(w["recovered_games_published"]) == 2 and len(w["not_kicked_off"]) == 2
    assert R.checkpoint_path(2026, 5) not in tip_tree(env)
    r, rep = run(env)                                                     # later: the rest is recovered, the first two stay as they were
    assert rep["weeks"][0]["status"] == "COMPLETE" and len(rep["weeks"][0]["to_recover"]) == 2


def test_dry_run_writes_nothing_and_is_never_reported_recovered(env):
    tip = origin_tip(env)
    r, rep = run(env, "--dry-run")
    assert r.returncode == 0, r.stdout + r.stderr
    w = rep["weeks"][0]
    assert w["status"] == "DRY_RUN_NOT_RECOVERED" and w["recovered"] is False and rep["mode"] == "DRY_RUN"
    assert origin_tip(env) == tip and not any(p.startswith(R.CHECKPOINT_DIR) for p in tip_tree(env))
    assert "recovered_games_published" in w and w["recovered_games_published"] == []
    with pytest.raises(R.RecoveryError):
        R.build_checkpoint(season=2026, week=5, games={}, window={}, mode="DRY_RUN", batch_id="x", scope={})


def test_failed_publication_marks_nothing_complete(env):
    hook = env["origin"] / "hooks" / "pre-receive"
    hook.write_text("#!/bin/sh\necho 'remote: error: pre-receive hook declined' >&2\nexit 1\n")
    hook.chmod(0o755)
    tip = origin_tip(env)
    r, rep = run(env)
    assert r.returncode == 1 and "RecoveryError" in r.stdout
    assert origin_tip(env) == tip
    assert rep["weeks"] == [] or rep["weeks"][0].get("status") != "COMPLETE"
    assert not any(p.startswith(R.CHECKPOINT_DIR) for p in tip_tree(env))


def test_conflicting_existing_record_fails_loudly_and_duplicates_are_refused(env, tmp_path):
    stage = tmp_path / "st"
    gid = "2026_05_AAA_BBB"
    d = stage / "data/shadow/v2/closes" / gid
    d.mkdir(parents=True)
    (d / "close-2.1.0.20261104T000000Z.closes_v2.jsonl.gz").write_bytes(b"ours")
    seed = env["seed"]
    other = seed / "data/shadow/v2/closes" / gid
    other.mkdir(parents=True)
    (other / "close-2.1.0.20261101T000000Z.closes_v2.jsonl.gz").write_bytes(b"theirs")
    git(seed, "add", "-A"); git(seed, "commit", "-q", "-m", "racer"); git(seed, "push", "-q", "origin", "market-data")
    tip = origin_tip(env)
    with pytest.raises(R.CheckpointConflict, match="exactly one"):
        R.publish_week(repo=str(env["repo"]), stage=str(stage), subdirs=[R.CLOSE_DIR, R.CLV_DIR], game_ids=[gid], message="m")
    assert origin_tip(env) == tip
    # same path, different bytes: refused, never overwritten
    (d / "close-2.1.0.20261104T000000Z.closes_v2.jsonl.gz").unlink()
    (d / "close-2.1.0.20261101T000000Z.closes_v2.jsonl.gz").write_bytes(b"changed")
    with pytest.raises(R.CheckpointConflict, match="different content"):
        R.publish_week(repo=str(env["repo"]), stage=str(stage), subdirs=[R.CLOSE_DIR, R.CLV_DIR], game_ids=[gid], message="m")
    # byte-identical: a no-op, no empty commit
    (d / "close-2.1.0.20261101T000000Z.closes_v2.jsonl.gz").write_bytes(b"theirs")
    res = R.publish_week(repo=str(env["repo"]), stage=str(stage), subdirs=[R.CLOSE_DIR, R.CLV_DIR], game_ids=[gid], message="m")
    assert res["status"] == "NO_CHANGE" and origin_tip(env) == tip


def test_corrupted_checkpoint_is_refused_not_trusted(env):
    r, _rep = run(env)
    assert r.returncode == 0
    seed = env["seed"]
    git(seed, "pull", "-q", "origin", "market-data")
    p = seed / R.checkpoint_path(2026, 5)
    cp = json.loads(p.read_text())
    cp["games"]["2026_05_AAA_BBB"]["close"]["bytes"] = 1                  # content changed, digest not
    p.write_text(json.dumps(cp))
    git(seed, "add", "-A"); git(seed, "commit", "-q", "-m", "tamper"); git(seed, "push", "-q", "origin", "market-data")
    r, _rep = run(env)
    assert r.returncode == 1 and "does not verify" in r.stdout


# ---------------------------------------------------------------------------------------------- provenance
def test_proxy_and_true_close_are_kept_apart_in_the_checkpoint(env):
    r, rep = run(env)
    assert r.returncode == 0, r.stdout + r.stderr
    tree = tip_tree(env)
    cp = json.loads(git(env["repo"], "cat-file", "blob", tree[R.checkpoint_path(2026, 5)][0]))
    g = cp["games"]["2026_05_CCC_DDD"]
    assert g["rows_by_kind"] == {R.TRUE_CLOSE: 4, R.PROXY: 2, R.MISSING: 2}
    assert g["tickers_by_kind"] == {R.TRUE_CLOSE: 2, R.PROXY: 1, R.MISSING: 1}  # stub: tickers T0..T3 -> E,G,S,M (first row decides)
    w = rep["weeks"][0]
    assert w["rows_by_kind_recovered"][R.PROXY] == 8 and w["rows_by_kind_recovered"][R.TRUE_CLOSE] == 16


def test_a_proxy_posing_as_a_true_close_is_refused_before_publication(env):
    tip = origin_tip(env)
    r, _rep = run(env, stub_env={"STUB_MODE": "proxy_as_true"})
    assert r.returncode == 1 and "ProvenanceViolation" in r.stdout and "proxy posing as a true close" in r.stdout
    assert origin_tip(env) == tip


def test_audit_rejects_missing_with_a_price(tmp_path):
    p = tmp_path / "x.closes_v2.jsonl.gz"
    with gzip.open(p, "wt") as g:
        g.write(json.dumps({"ticker": "T", "close_quality": "MISSING", "yes_bid": 0.5}) + "\n")
    with pytest.raises(R.ProvenanceViolation):
        R.audit_close_rows(str(p))
    with gzip.open(p, "wt") as g:
        g.write(json.dumps({"ticker": "T", "close_quality": "WEIRD"}) + "\n")
    assert R.audit_close_rows(str(p))["rows_by_kind"] == {R.MISSING: 1}      # unknown tier -> MISSING, never TRUE_CLOSE


def test_game_without_projections_is_recorded_not_invented(env):
    with open(env["sched"], "a") as f:
        f.write("2026_05_ZZZ_NOP,2026,5,REG,2026-10-12,13:00\n")
    r, rep = run(env)
    assert r.returncode == 0, r.stdout + r.stderr
    tree = tip_tree(env)
    cp = json.loads(git(env["repo"], "cat-file", "blob", tree[R.checkpoint_path(2026, 5)][0]))
    assert cp["games"]["2026_05_ZZZ_NOP"]["status"] == "NO_PROJECTIONS"
    assert R.existing_batches(tree, "2026_05_ZZZ_NOP") == {"close": [], "clv": []}


def test_listing_the_tree_downloads_no_blobs(env):
    repo = str(env["repo"])
    R.fetch_tip(repo)
    before = git(repo, "count-objects", "-v")
    tree = R.ls_tree(repo, "origin/market-data", "data")
    after = git(repo, "count-objects", "-v")
    assert len(tree) > 50 and before == after, "ls-tree must be answered from trees alone (no promisor fetch of blobs)"
