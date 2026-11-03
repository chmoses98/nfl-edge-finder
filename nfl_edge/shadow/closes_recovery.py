"""Date-bounded, checkpointed recovery of per-game canonical closes from the `market-data` branch.

WHY. `market-data` holds ~52 GB (capture quotes ~18 GB, trades ~12.6 GB, books ~4.3 GB, projections ~16 GB). The
settlement workflow fetched all of it to pair closes for a handful of games and timed out. A close for a game needs
only (pair_closes_v2.py / nfl_edge/evaluation/close.py):

    capture/<day>/*.quotes.jsonl       for days in [kickoff - 14 d, kickoff day]  (quote_history.capture_days; the capture is
                                       change-suppressed so the last pre-kickoff row can be days old)
    capture/<day>/*.manifest.json      for the same days (per-series confirmation instants, open-set run metadata)
    capture/*/*.openset.json           every day (a delta chain: it is replayed from the first anchor; 30 MB in all)
    capture/state.json                 last-seen run per ticker
    projections/<day>/*                the board snapshots that hold the game: from its first listing (about two weeks
                                       before kickoff) through its kickoff day
    projection_index/**                per-file index cache (small)

Never the trades, the books, the live ticks, the discovery tree, the other days' quotes or projections. This module
plans exactly that set from the schedule (kickoff times), materialises it with a blobless partial clone plus a
non-cone sparse checkout, and keeps a DURABLE, APPEND-ONLY, DIGESTED checkpoint per week on the branch so a completed
week is skipped (verified from tree metadata alone, no blob download) and an interrupted run resumes.

PROVENANCE IS NEVER REWRITTEN. A close is TRUE_CLOSE (EXCELLENT/GOOD), an earlier-quote PROXY (STALE) or MISSING, exactly
as nfl_edge/evaluation/close.py cut it. `audit_close_rows` re-checks every written row against the tier thresholds and
fails loudly if a proxy carries a true-close tier (or the reverse). A dry run produces a report labelled DRY_RUN and
can never produce a checkpoint (`build_checkpoint` refuses).

SHADOW / RESEARCH ONLY. Reads and writes evidence files; places no wagers, activates no model.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

from nfl_edge.evaluation import close as CL

SCHEMA = "closes-recovery-week-1"
BRANCH = "market-data"
CAPTURE = "data/kalshi/capture"
PROJ = "data/shadow/v2/projections"
PIDX = "data/shadow/v2/projection_index"
CLOSE_DIR = "data/shadow/v2/closes"
CLV_DIR = "data/shadow/v2/clv"
CHECKPOINT_DIR = "data/shadow/v2/recovery/closes_weeks"
CLOSE_SUFFIX, CLV_SUFFIX = "closes_v2", "clv_v2"

DAYS_BACK = 14           # quote_history.capture_days default used by pair_closes_v2.py
PROJ_LOOKBACK = 16       # a game is first on the board ~14 days ahead (measured: wk3 12 d, wk4 12 d, wk5 14 d); +2 d slack, then checked

TRUE_CLOSE, PROXY, MISSING, NOT_APPLICABLE = "TRUE_CLOSE", "EARLIER_QUOTE_PROXY", "MISSING", "NOT_APPLICABLE"
TIER_TO_KIND = {CL.EXCELLENT: TRUE_CLOSE, CL.GOOD: TRUE_CLOSE, CL.STALE: PROXY, CL.MISSING: MISSING, "NOT_APPLICABLE": NOT_APPLICABLE}


class RecoveryError(Exception):
    """Base: the run stops, nothing further is marked complete."""


class CheckpointConflict(RecoveryError):
    """A checkpoint or a published close record exists and disagrees with what this run would write."""


class ProvenanceViolation(RecoveryError):
    """A close record's quality tier contradicts its own age: a proxy posing as a true close, or the reverse."""


class WindowTooTight(RecoveryError):
    """A game is already on the board on the first projection day fetched: earlier snapshots would be missing."""


# ----------------------------------------------------------------------------------------------- schedule / window
@dataclass(frozen=True)
class Game:
    game_id: str
    kickoff: datetime


def parse_weeks(spec: str) -> list[int]:
    """'5-8' -> [5,6,7,8]; '5,7' -> [5,7]; '6' -> [6]."""
    out: list[int] = []
    for part in str(spec).replace(" ", "").split(","):
        if not part:
            continue
        m = re.fullmatch(r"(\d+)-(\d+)", part)
        if m:
            lo, hi = int(m.group(1)), int(m.group(2))
            if hi < lo:
                raise ValueError(f"week range {part!r} runs backwards")
            out += list(range(lo, hi + 1))
        elif part.isdigit():
            out.append(int(part))
        else:
            raise ValueError(f"cannot read week spec {part!r}")
    if not out:
        raise ValueError("no weeks given")
    return sorted(dict.fromkeys(out))


def load_week_games(schedule_csv: str, season: int, week: int) -> list[Game]:
    """Regular-season games of one week with their UTC kickoff (nflverse publishes gameday/gametime in US Eastern)."""
    from nfl_edge.data.nfl_calendar import kickoff_utc
    games = []
    with open(schedule_csv, newline="") as f:
        for row in csv.DictReader(f):
            if str(row.get("season")) != str(season) or str(row.get("week")) != str(week):
                continue
            if (row.get("game_type") or "REG") != "REG":
                continue
            ko = kickoff_utc((row.get("gameday") or "").strip(), (row.get("gametime") or "").strip())
            if ko is None:
                raise RecoveryError(f"{row.get('game_id')}: no kickoff in the schedule; a close cannot be bounded without one")
            games.append(Game(row["game_id"], ko))
    return sorted(games, key=lambda g: (g.kickoff, g.game_id))


@dataclass(frozen=True)
class Window:
    capture_days: tuple
    projection_days: tuple

    def to_dict(self):
        return {"capture_days": [self.capture_days[0], self.capture_days[-1]] if self.capture_days else [],
                "projection_days": [self.projection_days[0], self.projection_days[-1]] if self.projection_days else [],
                "n_capture_days": len(self.capture_days), "n_projection_days": len(self.projection_days)}


def _days(lo: date, hi: date):
    d = lo
    while d <= hi:
        yield d.isoformat()
        d += timedelta(days=1)


def window_for(games, *, days_back: int = DAYS_BACK, proj_lookback: int = PROJ_LOOKBACK) -> Window:
    cap, proj = set(), set()
    for g in games:
        ko = g.kickoff.astimezone(timezone.utc)
        # identical to quote_history.capture_days: lo = (ko - days_back).date(), hi = ko.date()
        cap.update(_days((ko - timedelta(days=days_back)).date(), ko.date()))
        proj.update(_days((ko - timedelta(days=proj_lookback)).date(), ko.date()))
    return Window(tuple(sorted(cap)), tuple(sorted(proj)))


def sparse_patterns(win: Window) -> list[str]:
    pats = [f"/{CAPTURE}/state.json", f"/{CAPTURE}/*/*.openset.json", f"/{PIDX}/"]
    for d in win.capture_days:
        pats += [f"/{CAPTURE}/{d}/*.quotes.jsonl", f"/{CAPTURE}/{d}/*.manifest.json"]
    for d in win.projection_days:
        pats.append(f"/{PROJ}/{d}/")
    return pats


_CAP = re.compile(rf"^{re.escape(CAPTURE)}/(\d{{4}}-\d{{2}}-\d{{2}})/([^/]+)$")
_PRJ = re.compile(rf"^{re.escape(PROJ)}/(\d{{4}}-\d{{2}}-\d{{2}})/[^/]+$")


def selected(path: str, win: Window) -> bool:
    """Does the sparse pattern set (sparse_patterns) include this tree path? Used to size the plan from tree metadata."""
    if path == f"{CAPTURE}/state.json" or path.startswith(PIDX + "/"):
        return True
    m = _CAP.match(path)
    if m:
        day, name = m.groups()
        if name.endswith(".openset.json"):
            return True
        return day in win.capture_days and name.endswith((".quotes.jsonl", ".manifest.json"))
    m = _PRJ.match(path)
    return bool(m and m.group(1) in win.projection_days)


# ----------------------------------------------------------------------------------------------- git plumbing
def git(*args, cwd, check=True, input=None, env=None):
    r = subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True, input=input, env=env, check=False)
    if check and r.returncode != 0:
        raise RecoveryError(f"git {' '.join(args[:3])} failed ({r.returncode}): {(r.stderr or r.stdout)[-600:]}")
    return r


def ls_tree(cwd: str, ref: str, *prefixes: str) -> dict:
    """{path: (blob_sha1, 0)} for every blob under the prefixes at `ref`.

    Trees only, never blobs. `git ls-tree -l` is deliberately NOT used: in a blobless clone it must know each blob's size
    and so downloads every blob it lists (measured: it began pulling the capture quotes). Sizes come from the fetch itself.
    """
    out = git("ls-tree", "-r", "-z", ref, "--", *prefixes, cwd=cwd).stdout
    res = {}
    for rec in out.split("\0"):
        if not rec:
            continue
        meta, path = rec.split("\t", 1)
        _mode, typ, sha = meta.split()
        if typ == "blob":
            res[path] = (sha, 0)
    return res


def dir_size(path: str) -> int:
    n = 0
    for root, _d, files in os.walk(path):
        for f in files:
            try:
                n += os.lstat(os.path.join(root, f)).st_size
            except OSError:
                pass
    return n


def fetch_tip(repo: str, *, branch: str = BRANCH) -> str:
    """Trees of the branch tip, no blobs (depth 1, blob:none): seconds and a few MB, whatever the branch weighs."""
    git("fetch", "-q", "--depth=1", "--filter=blob:none", "--no-tags", "origin", f"+{branch}:refs/remotes/origin/{branch}", cwd=repo)
    return git("rev-parse", f"origin/{branch}", cwd=repo).stdout.strip()


def materialise(repo: str, wt: str, patterns: list[str], *, branch: str = BRANCH) -> dict:
    """Sparse worktree of the blobless tip holding exactly `patterns`; only those blobs are downloaded.

    Worktrees share the repo's remote and credentials (the checkout action's), exactly as publish_market_data.py
    --sparse does. Re-entrant: the sparse set is replaced for the next week, so the previous week's files leave the
    worktree (their packed objects stay in .git and are never fetched twice).
    Returns measurements: seconds, .git growth in bytes (what came over the wire, compressed), worktree bytes.
    """
    t0 = time.time()
    gitdir = os.path.join(repo, ".git")
    before = dir_size(gitdir)
    fetch_tip(repo, branch=branch)
    t_meta = time.time() - t0
    if not os.path.isdir(wt):
        git("worktree", "prune", cwd=repo)
        git("worktree", "add", "--no-checkout", "-f", "--detach", wt, f"origin/{branch}", cwd=repo)
    git("sparse-checkout", "set", "--no-cone", "--stdin", cwd=wt, input="\n".join(patterns) + "\n")
    t1 = time.time()
    git("checkout", "-q", "-f", "--detach", f"origin/{branch}", cwd=wt)
    t_blobs = time.time() - t1
    return {"tree_fetch_seconds": round(t_meta, 1), "blob_checkout_seconds": round(t_blobs, 1),
            "git_dir_bytes_added": dir_size(gitdir) - before, "worktree_bytes": dir_size(os.path.join(wt, "data")) if os.path.isdir(os.path.join(wt, "data")) else 0,
            "seconds": round(time.time() - t0, 1)}


# ----------------------------------------------------------------------------------------------- record audit
def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha1(path: str) -> str:
    """The id git gives this file's content, computed without git (so it can be compared with ls-tree)."""
    size = os.path.getsize(path)
    h = hashlib.sha1(f"blob {size}\0".encode())
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def kind_of(row: dict) -> str:
    """TRUE_CLOSE / PROXY / MISSING by the written tier. An unrecognised tier is MISSING, never TRUE_CLOSE."""
    return TIER_TO_KIND.get(str(row.get("close_quality") or "").upper(), MISSING)


def audit_close_rows(path: str) -> dict:
    """Re-derive each row's provenance from its own age and fail loudly if the written tier contradicts it.

    Returns {rows, rows_by_kind, tickers_by_kind}. A proxy (STALE, older than 90 minutes) must never carry an
    EXCELLENT/GOOD tier; a true close must be within 90 minutes; MISSING must carry no price.
    """
    rows_by_kind, ticker_kind, n = Counter(), {}, 0
    with gzip.open(path, "rt") as fh:
        for line in fh:
            if not line.strip():
                continue
            r = json.loads(line)
            n += 1
            q = str(r.get("close_quality") or "").upper()
            kind = kind_of(r)
            age = r.get("close_age_seconds")
            if kind == TRUE_CLOSE and (age is None or age > CL.TIER_GOOD_S):
                raise ProvenanceViolation(f"{path}: {r.get('ticker')} is tiered {q} with close age {age} s (> {CL.TIER_GOOD_S} s): a proxy posing as a true close")
            if kind == PROXY and (age is None or age <= CL.TIER_GOOD_S or age > CL.TIER_STALE_S):
                raise ProvenanceViolation(f"{path}: {r.get('ticker')} is tiered STALE with close age {age} s outside ({CL.TIER_GOOD_S}, {CL.TIER_STALE_S}]")
            if kind == MISSING and (r.get("close_id") or r.get("yes_bid") is not None or r.get("yes_ask") is not None):
                raise ProvenanceViolation(f"{path}: {r.get('ticker')} is MISSING but carries a close id or a price")
            rows_by_kind[kind] += 1
            t = r.get("ticker")
            if t is not None and t not in ticker_kind:
                ticker_kind[t] = kind
    return {"rows": n, "rows_by_kind": dict(rows_by_kind), "tickers_by_kind": dict(Counter(ticker_kind.values()))}


# ----------------------------------------------------------------------------------------------- checkpoint
def checkpoint_path(season: int, week: int) -> str:
    return f"{CHECKPOINT_DIR}/{season}_wk{week:02d}.json"


def _canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()


def checkpoint_digest(body: dict) -> str:
    return hashlib.sha256(_canon({k: v for k, v in body.items() if k != "digest_sha256"})).hexdigest()


def build_checkpoint(*, season: int, week: int, games: dict, window: dict, mode: str, batch_id: str, scope: dict) -> dict:
    """The per-week completion record. Refuses anything but a LIVE run: a dry run is never 'recovered'."""
    if mode != "LIVE":
        raise RecoveryError(f"refusing to build a completion checkpoint for a {mode} run: only published data is recovered data")
    body = {"schema": SCHEMA, "season": season, "week": week, "status": "COMPLETE", "mode": mode,
            "close_rule_version": CL.CLOSE_RULE_VERSION, "batch_id": batch_id, "scope": scope, "window": window,
            "games": {g: games[g] for g in sorted(games)}}
    body["digest_sha256"] = checkpoint_digest(body)
    return body


def verify_checkpoint(cp: dict, tree: dict) -> list[str]:
    """Problems found in a checkpoint against the branch's tree metadata (blob ids), or [] when it holds."""
    problems = []
    if cp.get("schema") != SCHEMA:
        problems.append(f"unknown schema {cp.get('schema')!r}")
    if cp.get("digest_sha256") != checkpoint_digest(cp):
        problems.append("checkpoint digest does not match its content")
    if cp.get("status") != "COMPLETE" or cp.get("mode") != "LIVE":
        problems.append(f"checkpoint is {cp.get('status')}/{cp.get('mode')}, not COMPLETE/LIVE")
    for gid, g in (cp.get("games") or {}).items():
        for key, d in (("close", CLOSE_DIR), ("clv", CLV_DIR)):
            f = g.get(key)
            if not f:
                continue
            ent = tree.get(f"{d}/{gid}/{f['file']}")
            if ent is None:
                problems.append(f"{gid}: {key} batch {f['file']} is not on the branch")
            elif ent[0] != f["git_blob_sha1"]:
                problems.append(f"{gid}: {key} batch {f['file']} differs from the checkpointed content")
    return problems


def existing_batches(tree: dict, game_id: str) -> dict:
    """{'close': [files], 'clv': [files]} already on the branch for one game (any rule version)."""
    out = {"close": [], "clv": []}
    for key, d, suf in (("close", CLOSE_DIR, CLOSE_SUFFIX), ("clv", CLV_DIR, CLV_SUFFIX)):
        pre = f"{d}/{game_id}/"
        out[key] = sorted(p[len(pre):] for p in tree if p.startswith(pre) and p.endswith(f".{suf}.jsonl.gz"))
    return out


def file_record(path: str, rows: int | None = None) -> dict:
    rec = {"file": os.path.basename(path), "sha256": _sha256(path), "git_blob_sha1": git_blob_sha1(path), "bytes": os.path.getsize(path)}
    if rows is not None:
        rec["rows"] = rows
    return rec


def stage_game(out_dir: str, game_id: str) -> dict:
    """Describe the batches pair_closes_v2 staged for one game under out_dir (audited), or {} when it staged none."""
    res = {}
    for key, d, suf in (("close", "closes", CLOSE_SUFFIX), ("clv", "clv", CLV_SUFFIX)):
        files = sorted(f for f in (os.listdir(os.path.join(out_dir, d, game_id)) if os.path.isdir(os.path.join(out_dir, d, game_id)) else [])
                       if f.endswith(f".{suf}.jsonl.gz"))
        if len(files) > 1:
            raise CheckpointConflict(f"{game_id}: {len(files)} {key} batches staged ({files}); a game holds exactly one")
        if files:
            p = os.path.join(out_dir, d, game_id, files[0])
            audit = audit_close_rows(p) if key == "close" else None
            res[key] = file_record(p, audit["rows"] if audit else None)
            if audit:
                res["audit"] = audit
    return res


# ----------------------------------------------------------------------------------------------- publish (atomic, conflict-checked)
def publish_week(*, repo: str, stage: str, subdirs: list[str], game_ids: list[str], message: str, branch: str = BRANCH,
                 attempts: int = 6, wt: str | None = None) -> dict:
    """ONE commit holding the week's close/CLV batches AND its checkpoint; pushed or not at all.

    `stage` is laid out like the branch (stage/data/shadow/v2/...); `subdirs` are the branch paths it adds to.
    Before every push attempt (including after a lost race) the branch tip is re-read and every game this commit
    would write is checked: a DIFFERENT close/CLV batch already on the branch for the same game, or a different
    file at a path this commit writes, raises CheckpointConflict -- nothing is overwritten, nothing duplicated.
    A byte-identical file already present is a no-op; a projection-index entry already present is kept (write-once).
    """
    wt = wt or os.path.join(os.path.dirname(os.path.abspath(repo)), "_recovery_publish_wt")
    if os.path.isdir(wt):
        git("worktree", "remove", "--force", wt, cwd=repo, check=False)
        shutil.rmtree(wt, ignore_errors=True)
    git("worktree", "prune", cwd=repo)
    staged = {}
    for root, _d, files in os.walk(stage):
        for fn in files:
            if not fn.endswith(".part"):
                full = os.path.join(root, fn)
                staged[os.path.relpath(full, stage)] = full
    last = ""
    for attempt in range(1, attempts + 1):
        fetch_tip(repo, branch=branch)
        tip = ls_tree(repo, f"origin/{branch}", *subdirs)
        todo = {}
        for rel, full in staged.items():
            have = tip.get(rel)
            if have is None:
                todo[rel] = full
            elif rel.startswith(PIDX + "/"):
                continue
            elif have[0] != git_blob_sha1(full):
                raise CheckpointConflict(f"{rel} already exists on {branch} with different content; refusing to overwrite or duplicate it")
        for gid in game_ids:
            have = existing_batches(tip, gid)
            ours = existing_batches({rel: 1 for rel in staged}, gid)
            for key in ("close", "clv"):
                extra = sorted(set(have[key]) - set(ours[key]))
                if extra:
                    raise CheckpointConflict(f"{gid}: {key} batch {extra} already on {branch} next to ours {ours[key]}; a game holds exactly one")
        if not todo:
            return {"status": "NO_CHANGE", "attempts": attempt}
        if not os.path.isdir(wt):
            git("worktree", "add", "--no-checkout", "-f", "--detach", wt, f"origin/{branch}", cwd=repo)
        git("sparse-checkout", "set", "--no-cone", "--stdin", cwd=wt, input="\n".join(f"/{s.strip('/')}/" for s in subdirs) + "\n")
        git("checkout", "-q", "-f", "--detach", f"origin/{branch}", cwd=wt)
        for rel, full in todo.items():
            os.makedirs(os.path.dirname(os.path.join(wt, rel)), exist_ok=True)
            shutil.copy2(full, os.path.join(wt, rel))
        git("add", "-A", "--", *subdirs, cwd=wt)
        git("commit", "-q", "-m", message, cwd=wt)
        r = git("push", "-q", "origin", f"HEAD:refs/heads/{branch}", cwd=wt, check=False)
        if r.returncode == 0:
            res = {"status": "PUBLISHED", "attempts": attempt, "commit": git("rev-parse", "HEAD", cwd=wt).stdout.strip()}
            git("worktree", "remove", "--force", wt, cwd=repo, check=False)
            return res
        last = (r.stderr or "")[-400:]
        low = last.lower()
        if ("gh001" in low and "error" in low) or "exceeds github" in low or "pre-receive hook declined" in low or "permission denied" in low:
            raise RecoveryError(f"push refused for good: {last}")
        time.sleep(min(2 * attempt, 10))
    raise RecoveryError(f"publication failed after {attempts} attempts; nothing is marked complete: {last}")
