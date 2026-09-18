"""Append-only projection store: write-once per (snapshot, arm); identical rerun no-op; contradiction fails closed.

Layout (parallel to the incumbent ledger and the three-arm corpus, never inside either):

    data/shadow/v2/projections/<day>/<snapshot_id>.<model_arm>.projections.jsonl.gz
    data/shadow/v2/projections/<day>/<snapshot_id>.<model_arm>.projections_manifest.json

`day` is the capture day of the snapshot (when the prediction was made). One file per arm per snapshot so
that adding an arm later adds a file and never rewrites one.
"""
from __future__ import annotations

import glob
import gzip
import hashlib
import json
import os
from datetime import datetime, timezone

from nfl_edge.projection.record import VOLATILE_FIELDS, content_hash

DIRNAME = os.path.join("shadow", "v2", "projections")


class ProjectionConflict(Exception):
    pass


def _day_of(snapshot_id: str) -> str:
    return snapshot_id[:4] + "-" + snapshot_id[4:6] + "-" + snapshot_id[6:8]


def read_rows(path: str) -> list:
    with gzip.open(path, "rt") as f:
        return [json.loads(line) for line in f if line.strip()]


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class ProjectionStore:
    def __init__(self, root: str):
        self.root = root

    def path(self, snapshot_id: str, model_arm: str) -> str:
        return os.path.join(self.root, _day_of(snapshot_id), f"{snapshot_id}.{model_arm}.projections.jsonl.gz")

    def manifest_path(self, snapshot_id: str, model_arm: str) -> str:
        return self.path(snapshot_id, model_arm).replace(".projections.jsonl.gz", ".projections_manifest.json")

    def plan(self, snapshot_id: str, model_arm: str, rows: list) -> dict:
        rows = [dict(r) for r in rows]
        for r in rows:
            if r.get("content_hash") != content_hash(r):
                raise ValueError(f"row {r.get('record_id')} carries a content hash that does not match its content")
        ids = [r["record_id"] for r in rows]
        if len(ids) != len(set(ids)):
            raise ProjectionConflict("duplicate record ids inside one snapshot")
        p = self.path(snapshot_id, model_arm)
        if not os.path.exists(p):
            return {"status": "NEW", "rows": rows, "conflicts": []}
        prev = {r["record_id"]: r for r in read_rows(p)}
        new = {r["record_id"]: r for r in rows}
        conflicts = []
        if set(prev) != set(new):
            conflicts.append(f"record set differs ({len(prev)} existing vs {len(new)} new)")
        for rid, r in new.items():
            if rid in prev and prev[rid].get("content_hash") != r["content_hash"]:
                diff = sorted(k for k in set(prev[rid]) | set(r) if k not in VOLATILE_FIELDS and k != "content_hash"
                              and prev[rid].get(k) != r.get(k))
                conflicts.append(f"{rid} differs in {diff[:8]}")
        return {"status": "CONFLICT" if conflicts else "NO_OP", "rows": rows, "conflicts": conflicts}

    def write(self, snapshot_id: str, model_arm: str, rows: list, manifest_extra: dict | None = None) -> dict:
        plan = self.plan(snapshot_id, model_arm, rows)
        if plan["status"] == "CONFLICT":
            raise ProjectionConflict("the same snapshot/arm would be rewritten with different content; nothing written:\n  "
                                     + "\n  ".join(plan["conflicts"][:20]))
        if plan["status"] == "NO_OP":
            man = json.load(open(self.manifest_path(snapshot_id, model_arm)))
            man["status"] = "NO_OP"
            return man
        p = self.path(snapshot_id, model_arm)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with gzip.GzipFile(p, "wb", mtime=0) as raw:
            for r in plan["rows"]:
                raw.write((json.dumps(r, separators=(",", ":"), sort_keys=True, default=str) + "\n").encode())
        by_state, by_family = {}, {}
        for r in plan["rows"]:
            by_state[r.get("support_state")] = by_state.get(r.get("support_state"), 0) + 1
            key = f"{r.get('market_family')}|{r.get('period')}"
            by_family[key] = by_family.get(key, 0) + 1
        man = {"status": "WRITTEN", "snapshot_id": snapshot_id, "model_arm": model_arm, "schema_version": plan["rows"][0].get("schema_version") if plan["rows"] else None,
               "written_at": datetime.now(timezone.utc).isoformat(), "n_rows": len(plan["rows"]),
               "by_support_state": by_state, "by_family": by_family, "file": os.path.basename(p), "sha256": _sha(p),
               "content_hashes_sha256": hashlib.sha256("\n".join(sorted(r["content_hash"] for r in plan["rows"])).encode()).hexdigest()}
        man.update(manifest_extra or {})
        with open(self.manifest_path(snapshot_id, model_arm), "w") as f:
            json.dump(man, f, indent=1, default=str)
        return man


def context_id(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()[:16]


def sidecar_path(root: str, snapshot_id: str) -> str:
    return os.path.join(root, _day_of(snapshot_id), f"{snapshot_id}.contexts.json.gz")


def write_sidecar(root: str, snapshot_id: str, payload: dict) -> dict:
    """Write-once context sidecar for a snapshot: lineage, game contexts and player contexts keyed by content id.

    Records carry the ids; the research export joins them back. Identical content is a NO_OP; different content
    for the same snapshot is a CONFLICT (raised), never an overwrite.
    """
    p = sidecar_path(root, snapshot_id)
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    if os.path.exists(p):
        with gzip.open(p, "rb") as f:
            existing = f.read()
        if existing == body:
            return {"status": "NO_OP", "path": p}
        raise ProjectionConflict(f"context sidecar for {snapshot_id} already exists with different content: {p}")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with gzip.GzipFile(p, "wb", mtime=0) as raw:
        raw.write(body)
    return {"status": "WRITTEN", "path": p, "sha256": _sha(p), "bytes": os.path.getsize(p)}


def read_sidecars(roots, snapshot_ids=None) -> dict:
    """snapshot_id -> sidecar payload, across roots (first occurrence wins; identical by construction).

    `snapshot_ids` scopes the load to the snapshots a caller actually references. Without it every sidecar
    of every historical snapshot is decompressed into memory (about 10 MB each), which is what made the
    postgame drivers grow with the lifetime archive rather than with the game being processed.
    """
    if isinstance(roots, str):
        roots = [roots]
    want = None if snapshot_ids is None else set(snapshot_ids)
    out = {}
    for root in roots:
        for p in sorted(glob.glob(os.path.join(root, "*", "*.contexts.json.gz"))):
            sid = os.path.basename(p).split(".")[0]
            if sid in out or (want is not None and sid not in want):
                continue
            with gzip.open(p, "rt") as f:
                out[sid] = json.load(f)
    return out


class SidecarCache:
    """Sidecars loaded on demand, one snapshot at a time, with a small most-recently-used window.

    Projection files are one snapshot each, so a per-file stream touches one sidecar at a time; a window of two
    covers the boundary between files. `loads` counts real decompressions so a test can prove the cache never
    reads a snapshot nothing referenced.
    """

    def __init__(self, roots, *, max_items: int = 2):
        self.roots = [roots] if isinstance(roots, str) else list(roots)
        self.max_items = max(1, int(max_items))
        self._items: dict = {}
        self.loads, self.hits, self.misses = 0, 0, 0

    def get(self, snapshot_id: str | None) -> dict | None:
        if not snapshot_id:
            return None
        if snapshot_id in self._items:
            self.hits += 1
            v = self._items.pop(snapshot_id)
            self._items[snapshot_id] = v                       # move to the most-recent end
            return v
        found = None
        for root in self.roots:
            p = sidecar_path(root, snapshot_id)
            if os.path.exists(p):
                with gzip.open(p, "rt") as f:
                    found = json.load(f)
                self.loads += 1
                break
        if found is None:
            self.misses += 1
        self._items[snapshot_id] = found
        while len(self._items) > self.max_items:
            self._items.pop(next(iter(self._items)))
        return found

    def stats(self) -> dict:
        return {"sidecar_loads": self.loads, "sidecar_cache_hits": self.hits, "sidecar_missing": self.misses,
                "sidecar_window": self.max_items}


# ------------------------------------------------------------------------------------------------ streaming reads
#
# The postgame drivers used to call read_projections() over every historical file, materialising the lifetime
# archive (1.5M rows, ~8 KB each) before they knew which game they were settling. Everything below reads one
# record at a time straight from gzip, applies the caller's filters while streaming, and keeps only the record
# ids it has already yielded (so first-occurrence de-duplication is preserved without holding rows).


class ScanStats:
    """What a streaming read physically touched. `silently dropped` is provable only when these are reported."""

    __slots__ = ("files_scanned", "rows_read", "rows_prefiltered_out", "rows_parsed", "rows_filtered_out",
                 "rows_duplicate", "rows_yielded")

    def __init__(self):
        for k in self.__slots__:
            setattr(self, k, 0)

    def add(self, other: "ScanStats") -> "ScanStats":
        for k in self.__slots__:
            setattr(self, k, getattr(self, k) + getattr(other, k))
        return self

    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in self.__slots__}

    def reconciles(self) -> bool:
        """Every physically read line went exactly one way: rejected before parsing, rejected after parsing,
        found to be a duplicate, or yielded."""
        return self.rows_read == (self.rows_prefiltered_out + self.rows_filtered_out + self.rows_duplicate
                                  + self.rows_yielded)


def _json_tokens(key: str, value) -> tuple:
    """The byte sequences a top-level `key: value` pair MUST contain in a line json.dumps wrote, in both
    separator styles. A line lacking every token of a group cannot hold that pair at the top level, so it can
    be rejected before json.loads. The reverse is not claimed: a token can match inside a nested block, and the
    parsed record decides. The filter is therefore a fast reject, never a fast accept."""
    v = json.dumps(value, separators=(",", ":"), sort_keys=True, default=str)
    k = json.dumps(key)
    return (f"{k}:{v}".encode(), f"{k}: {v}".encode())


def _prefilter_groups(game_ids=None, season=None, week=None) -> list:
    groups = []
    if game_ids:
        groups.append([t for g in sorted(game_ids) for t in _json_tokens("game_id", g)])
    if season is not None:
        groups.append(list(_json_tokens("season", season)))
    if week is not None:
        groups.append(list(_json_tokens("week", week)))
    return groups


def _passes_prefilter(line: bytes, groups: list) -> bool:
    for toks in groups:
        if not any(t in line for t in toks):
            return False
    return True


def projection_file_arm(path: str) -> str:
    return os.path.basename(path).split(".")[1]


def projection_file_day(path: str) -> str:
    return os.path.basename(os.path.dirname(path))


def iter_projection_files(roots, *, day_lo: str | None = None, day_hi: str | None = None, arms=None):
    """Every projection file under the roots, in the order read_projections() has always visited them."""
    if isinstance(roots, str):
        roots = [roots]
    for root in roots:
        for d in sorted(glob.glob(os.path.join(root, "*"))):
            day = os.path.basename(d)
            if not os.path.isdir(d) or (day_lo and day < day_lo) or (day_hi and day > day_hi):
                continue
            for path in sorted(glob.glob(os.path.join(d, "*.projections.jsonl.gz"))):
                if arms and projection_file_arm(path) not in arms:
                    continue
                yield path


def iter_projections(roots=None, *, day_lo: str | None = None, day_hi: str | None = None, game_ids=None, arms=None,
                     season: int | None = None, week: int | None = None, has_probability: bool | None = None,
                     files=None, stats: ScanStats | None = None, dedupe: bool = True):
    """Yield projection rows one at a time, straight from gzip, filtering while streaming.

    Filters: `game_ids`, `season`, `week` (record fields), `arms` and `day_lo` / `day_hi` (file name and
    directory), `has_probability` (True: p_yes present; False: refusals only). `files` names the exact files
    to read (in that order) instead of walking the roots -- the projection index supplies it so a game's
    stream opens only the files that hold the game. Rows are de-duplicated by record_id, first occurrence wins,
    exactly as read_projections() did; only the ids of yielded rows are retained, never the rows.
    """
    if files is None:
        files = iter_projection_files(roots, day_lo=day_lo, day_hi=day_hi, arms=arms)
    want = set(game_ids) if game_ids else None
    groups = _prefilter_groups(want, season, week)
    st = stats if stats is not None else ScanStats()
    seen = set()
    for path in files:
        st.files_scanned += 1
        with gzip.open(path, "rb") as f:
            for line in f:
                if not line.strip():
                    continue
                st.rows_read += 1
                if groups and not _passes_prefilter(line, groups):
                    st.rows_prefiltered_out += 1
                    continue
                r = json.loads(line)
                st.rows_parsed += 1
                if want is not None and r.get("game_id") not in want:
                    st.rows_filtered_out += 1
                    continue
                if season is not None and r.get("season") != season:
                    st.rows_filtered_out += 1
                    continue
                if week is not None and r.get("week") != week:
                    st.rows_filtered_out += 1
                    continue
                if has_probability is not None and (r.get("p_yes") is None) == bool(has_probability):
                    st.rows_filtered_out += 1
                    continue
                if dedupe:
                    rid = r["record_id"]
                    if rid in seen:
                        st.rows_duplicate += 1
                        continue
                    seen.add(rid)
                st.rows_yielded += 1
                yield r


def read_projections(roots, *, day_lo: str | None = None, day_hi: str | None = None, game_ids=None, arms=None) -> list:
    """Every projection row under the roots, de-duplicated by record_id (first occurrence wins; identical by construction).

    Materialises the whole selection: fine for a bounded root (a test tree, one day's staging), wrong for the
    lifetime archive. Drivers stream with iter_projections() and the index instead.
    """
    return list(iter_projections(roots, day_lo=day_lo, day_hi=day_hi, game_ids=game_ids, arms=arms))


# ------------------------------------------------------------------------------------------------ the index
#
# One small JSON per projection file, derived from it and keyed by its sha256, saying which games the file holds
# (with row and probability counts, the first kickoff / season / week seen) and how many rows carry no game.
# A driver consults it to open only the files that can hold the game it is processing. Every index file is a
# pure function of an immutable projection file, so it is write-once and can be published beside the corpus
# (data/shadow/v2/projection_index) and reused by the next run; a file whose sha changed is re-indexed.

INDEX_VERSION = "projection-index-1.0.0+reachability-1.0.0"     # per-game counts depend on reachability's rules
INDEX_DIRNAME = "projection_index"


def index_file_path(index_root: str, projection_path: str) -> str:
    name = os.path.basename(projection_path).replace(".projections.jsonl.gz", ".projections_index.json")
    return os.path.join(index_root, projection_file_day(projection_path), name)


def needs_player_tables(r: dict) -> bool:
    """Would settling this record need the player statistic tables? Exactly the settlement driver's test: a
    probability-carrying, dispatchable, non-season record of the PLAYER engine (nfl_edge.settlement.reachability).
    Counted per game at index time so a driver can decide readiness without re-reading the game."""
    from nfl_edge.settlement import reachability as RE
    if r.get("p_yes") is None or r.get("engine") != "PLAYER":
        return False
    rr = RE.reachability(r)
    return rr["state"] == RE.DISPATCHABLE and rr["scope"] != RE.SEASON


def build_file_index(path: str, *, sha: str | None = None) -> dict:
    """Parse one projection file once and summarise it per game. Memory: one row at a time plus the summary."""
    games: dict = {}
    no_game = {"n": 0, "prob": 0}
    n = 0
    with gzip.open(path, "rb") as f:
        for line in f:
            if not line.strip():
                continue
            n += 1
            r = json.loads(line)
            gid = r.get("game_id")
            prob = r.get("p_yes") is not None
            if not gid:
                no_game["n"] += 1
                no_game["prob"] += int(prob)
                continue
            g = games.get(gid)
            if g is None:
                g = games[gid] = {"n": 0, "prob": 0, "player_prob": 0, "kickoff_utc": None, "season": None, "week": None}
            g["n"] += 1
            g["prob"] += int(prob)
            g["player_prob"] += int(needs_player_tables(r))
            if g["kickoff_utc"] is None and r.get("kickoff_utc"):
                g["kickoff_utc"] = r.get("kickoff_utc")
            if g["season"] is None and r.get("season") is not None:
                g["season"] = r.get("season")
            if g["week"] is None and r.get("week") is not None:
                g["week"] = r.get("week")
    return {"index_version": INDEX_VERSION, "file": os.path.basename(path), "day": projection_file_day(path),
            "model_arm": projection_file_arm(path), "sha256": sha or _sha(path), "n_rows": n,
            "games": dict(sorted(games.items())), "no_game": no_game}


class ProjectionIndex:
    """Which projection files hold which games, built once per run and cached per file by content hash."""

    def __init__(self, roots, *, index_roots=(), write_root: str | None = None, day_lo: str | None = None,
                 day_hi: str | None = None, arms=None):
        self.roots = [roots] if isinstance(roots, str) else list(roots)
        self.index_roots = [r for r in ([write_root] + list(index_roots or ())) if r]
        self.write_root = write_root
        self.entries: dict = {}                                 # projection path -> index entry, in read order
        self.built, self.reused, self.written = 0, 0, 0
        for path in iter_projection_files(self.roots, day_lo=day_lo, day_hi=day_hi, arms=arms):
            sha = _sha(path)
            entry = self._cached(path, sha)
            if entry is None:
                entry = build_file_index(path, sha=sha)
                self.built += 1
                if self.write_root:
                    ip = index_file_path(self.write_root, path)
                    if not os.path.exists(ip):
                        os.makedirs(os.path.dirname(ip), exist_ok=True)
                        with open(ip, "w") as f:
                            json.dump(entry, f, indent=1, sort_keys=True)
                        self.written += 1
            else:
                self.reused += 1
            self.entries[path] = entry
        self._by_game: dict = {}
        for path, e in self.entries.items():
            for gid, g in e["games"].items():
                cur = self._by_game.get(gid)
                if cur is None:
                    cur = self._by_game[gid] = {"n": 0, "prob": 0, "player_prob": 0, "files": [], "kickoff_utc": None,
                                                "season": None, "week": None, "arms": set()}
                cur["n"] += g["n"]
                cur["prob"] += g["prob"]
                cur["player_prob"] += g.get("player_prob", 0)
                cur["files"].append(path)
                cur["arms"].add(e.get("model_arm") or projection_file_arm(path))
                for k in ("kickoff_utc", "season", "week"):
                    if cur[k] is None and g.get(k) is not None:
                        cur[k] = g[k]

    def _cached(self, path: str, sha: str) -> dict | None:
        for root in self.index_roots:
            ip = index_file_path(root, path)
            if not os.path.exists(ip):
                continue
            try:
                with open(ip) as f:
                    e = json.load(f)
            except (OSError, ValueError):
                continue
            if e.get("index_version") == INDEX_VERSION and e.get("sha256") == sha:
                return e
        return None

    # ---- queries
    def games(self) -> dict:
        return self._by_game

    def game(self, game_id: str) -> dict | None:
        return self._by_game.get(game_id)

    def files_for_game(self, game_id: str) -> list:
        g = self._by_game.get(game_id)
        return list(g["files"]) if g else []

    def files_for_games(self, game_ids) -> list:
        want = set(game_ids)
        return [p for p, e in self.entries.items() if any(g in want for g in e["games"])]

    def files_with_no_game_rows(self, *, prob_only: bool = False) -> list:
        key = "prob" if prob_only else "n"
        return [p for p, e in self.entries.items() if e["no_game"][key] > 0]

    def rows_total(self) -> int:
        return sum(e["n_rows"] for e in self.entries.values())

    def summary(self) -> dict:
        return {"index_version": INDEX_VERSION, "files": len(self.entries), "files_indexed_this_run": self.built,
                "files_index_reused": self.reused, "index_files_written": self.written,
                "rows_total": self.rows_total(), "games": len(self._by_game),
                "no_game_rows": sum(e["no_game"]["n"] for e in self.entries.values()),
                "no_game_probability_rows": sum(e["no_game"]["prob"] for e in self.entries.values())}


def verify(roots) -> dict:
    problems, n = [], 0
    if isinstance(roots, str):
        roots = [roots]
    for root in roots:
        for path in sorted(glob.glob(os.path.join(root, "*", "*.projections.jsonl.gz"))):
            rows = read_rows(path)
            n += len(rows)
            seen = set()
            for r in rows:
                if r.get("content_hash") != content_hash(r):
                    problems.append(f"{path}: {r.get('record_id')} content hash mismatch")
                if r.get("record_id") in seen:
                    problems.append(f"{path}: duplicate {r.get('record_id')}")
                seen.add(r.get("record_id"))
            mp = path.replace(".projections.jsonl.gz", ".projections_manifest.json")
            if not os.path.exists(mp):
                problems.append(f"{path}: no manifest")
            else:
                man = json.load(open(mp))
                if man.get("sha256") != _sha(path):
                    problems.append(f"{path}: sha256 differs from manifest")
                if man.get("n_rows") != len(rows):
                    problems.append(f"{path}: manifest says {man.get('n_rows')} rows, file holds {len(rows)}")
    return {"rows": n, "problems": problems, "ok": not problems}
