"""Immutable three-arm forecast records: one game record and one contract record per (snapshot, game/contract).

Layout, parallel to the shadow ledger and never inside it:

    data/shadow/arms/<day>/<run_id>.<arms_version>.arm_games.jsonl.gz        one row per game, all three arms
    data/shadow/arms/<day>/<run_id>.<arms_version>.arm_contracts.jsonl.gz    one row per contract, all three arms
    data/shadow/arms/<day>/<run_id>.<arms_version>.arms_manifest.json
    data/shadow/arms/<day>/<run_id>.<arms_version>.funnel.json               the BET/WATCH/PASS accounting

Why one row carries all three arms: the experiment is PAIRED by construction. A row that holds the CURRENT,
DATA_ONLY and HYBRID answers to the same question, from the same draws, at the same instant, cannot later be
mis-joined into an unpaired comparison. A missing arm is a null with a reason in that row, never a missing row.

Identity and reruns: `record_id = sha1(run_id | game_id or ticker | arms_version)`. A rerun of the same
snapshot with the same code is a NO-OP (content-identical); a rerun that would write DIFFERENT content under
an existing identity is a CONFLICT and writes nothing. The wall-clock `generated_at` is excluded from the
content hash; everything that is a claim is inside it.
"""
from __future__ import annotations

import glob
import gzip
import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

from nfl_edge.arms import registry as R

ARMS_DIRNAME = "arms"
SCHEMA_VERSION = "1.0.0"
VOLATILE_FIELDS = ("generated_at",)


class ArmsConflict(Exception):
    """A rerun would write a different truth under an identity that already exists."""


def game_record_id(run_id: str, game_id: str, arms_version: str = R.ARMS_VERSION) -> str:
    return hashlib.sha1(f"{run_id}|{game_id}|{arms_version}".encode()).hexdigest()[:20]


def contract_record_id(run_id: str, ticker: str, arms_version: str = R.ARMS_VERSION) -> str:
    return hashlib.sha1(f"{run_id}|{ticker}|{arms_version}".encode()).hexdigest()[:20]


def content_hash(row: dict) -> str:
    payload = {k: v for k, v in row.items() if k not in VOLATILE_FIELDS and k != "content_hash"}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()[:20]


@dataclass
class ArmCenter:
    """One arm's answer for one game: the centre, where it came from, and whether it is usable."""
    arm_id: str
    arm_version: str
    status: str = R.OK                       # OK | DEGRADED | UNAVAILABLE
    unavailable_reason: str | None = None
    # the game centre, home-minus-away margin and total points (same sign convention as the incumbent)
    projected_home_margin: float | None = None
    projected_total: float | None = None
    # what was actually fed to the simulator (challengers are snapped to the half-point line grid)
    simulation_center_margin: float | None = None
    simulation_center_total: float | None = None
    implied_home_score: float | None = None
    implied_away_score: float | None = None
    center_source: str | None = None
    # research lineage
    feature_cutoff: dict = field(default_factory=dict)
    training_cutoff: str | None = None
    model_training_seasons: list = field(default_factory=list)
    model_artifact_sha: str | None = None
    input_data_manifest: dict = field(default_factory=dict)
    data_quality_state: str | None = None
    market_snapshot_id: str | None = None
    uses_market_information: bool | None = None
    # arm-specific detail (CURRENT: implied-line diagnostics; DATA_ONLY: features + attestation; HYBRID: blend)
    detail: dict = field(default_factory=dict)
    # simulation summary under this centre
    simulation: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


@dataclass
class GameArmRecord:
    record_id: str
    schema_version: str
    arms_version: str
    run_id: str
    observed_at: str
    generated_at: str
    code_sha: str | None
    season: int | None
    week: int | None
    game_id: str
    home_team: str | None
    away_team: str | None
    kickoff_at: str | None
    minutes_to_kickoff: float | None
    prekickoff: bool
    status: str                                    # OK | POST_KICKOFF_EXCLUDED | UNAVAILABLE
    status_reason: str | None = None
    market_snapshot_id: str | None = None
    incumbent_ledger_file: str | None = None
    incumbent_model_version: str | None = None
    incumbent_game_env_version: str | None = None
    simulation: dict = field(default_factory=dict)      # n_sims, seed key, crn version, bank fingerprint, uniform sha
    arms: dict = field(default_factory=dict)            # arm_id -> ArmCenter.to_dict()
    reproduction_check: dict = field(default_factory=dict)
    n_contracts_priced: int = 0
    n_contracts_skipped: int = 0
    contract_skip_reasons: dict = field(default_factory=dict)
    hybrid_weights: dict = field(default_factory=lambda: {"market": R.HYBRID_WEIGHT_MARKET, "data": R.HYBRID_WEIGHT_DATA})

    def to_dict(self):
        return asdict(self)


@dataclass
class ContractArmRecord:
    record_id: str
    game_record_id: str
    schema_version: str
    arms_version: str
    run_id: str
    observed_at: str
    generated_at: str
    game_id: str
    season: int | None
    week: int | None
    home_team: str | None
    away_team: str | None
    kickoff_at: str | None
    minutes_to_kickoff: float | None
    # contract identity and semantics, copied from the incumbent ledger row so settlement needs nothing else
    ticker: str
    event_ticker: str | None
    series_ticker: str | None
    family: str | None
    period: str | None
    threshold: float | None
    floor_strike: float | None
    operator: str | None
    team: str | None
    direction: str = "YES"
    # the three arms, event-probability space and contract-value space kept apart
    p_current: float | None = None
    p_data_only: float | None = None
    p_hybrid: float | None = None
    cv_current: float | None = None
    cv_data_only: float | None = None
    cv_hybrid: float | None = None
    arm_status: dict = field(default_factory=dict)          # arm_id -> OK | UNAVAILABLE | DEGRADED
    # the incumbent's OWN number for this ticker at this snapshot (its own draws), for the reproduction check
    incumbent_prediction_id: str | None = None
    incumbent_contract_value: float | None = None
    incumbent_event_probability: float | None = None
    # the market this snapshot saw. The midpoint is research-only: never executable, never fair value.
    yes_bid: float | None = None
    yes_ask: float | None = None
    no_bid: float | None = None
    no_ask: float | None = None
    mid: float | None = None
    quote_width: float | None = None
    volume: float | None = None
    open_interest: float | None = None
    liquidity: float | None = None
    book_depth_yes: float | None = None
    book_depth_no: float | None = None
    minutes_since_price_change: float | None = None

    def to_dict(self):
        return asdict(self)


def _day_of(run_id: str) -> str:
    return run_id[:4] + "-" + run_id[4:6] + "-" + run_id[6:8]


def stamp(row: dict) -> dict:
    row = dict(row)
    row["content_hash"] = content_hash(row)
    return row


def read_rows(path: str) -> list:
    with gzip.open(path, "rt") as f:
        return [json.loads(line) for line in f if line.strip()]


def _write_gz(path: str, rows: list):
    with gzip.GzipFile(path, "wb", mtime=0) as raw:
        for row in rows:
            raw.write((json.dumps(row, separators=(",", ":"), sort_keys=True, default=str) + "\n").encode())


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class ArmsWriter:
    """Write-once per (run_id, arms_version). Identical rerun -> NO_OP; different rerun -> ArmsConflict."""

    def __init__(self, root: str, run_id: str, arms_version: str = R.ARMS_VERSION):
        self.root, self.run_id, self.arms_version = root, run_id, arms_version
        self.dir = os.path.join(root, _day_of(run_id))
        self.stem = f"{run_id}.{arms_version}"
        self.games_path = os.path.join(self.dir, f"{self.stem}.arm_games.jsonl.gz")
        self.contracts_path = os.path.join(self.dir, f"{self.stem}.arm_contracts.jsonl.gz")
        self.manifest_path = os.path.join(self.dir, f"{self.stem}.arms_manifest.json")
        self.funnel_path = os.path.join(self.dir, f"{self.stem}.funnel.json")

    def plan(self, games: list, contracts: list) -> dict:
        games = [stamp(g) for g in games]
        contracts = [stamp(c) for c in contracts]
        ids = [g["record_id"] for g in games] + [c["record_id"] for c in contracts]
        if len(ids) != len(set(ids)):
            raise ArmsConflict("duplicate record ids inside one snapshot; the writer refuses to pick one")
        status = "NEW"
        conflicts = []
        if os.path.exists(self.games_path) or os.path.exists(self.contracts_path):
            status = "NO_OP"
            for path, rows in ((self.games_path, games), (self.contracts_path, contracts)):
                prev = {r["record_id"]: r for r in read_rows(path)} if os.path.exists(path) else {}
                new = {r["record_id"]: r for r in rows}
                if set(prev) != set(new):
                    conflicts.append(f"{os.path.basename(path)}: record set differs "
                                     f"({len(prev)} existing vs {len(new)} new)")
                    continue
                for rid, r in new.items():
                    if prev[rid].get("content_hash") != r["content_hash"]:
                        diff = sorted(k for k in set(prev[rid]) | set(r)
                                      if k not in VOLATILE_FIELDS and k != "content_hash" and prev[rid].get(k) != r.get(k))
                        conflicts.append(f"{os.path.basename(path)}: {rid} differs in {diff[:8]}")
            if conflicts:
                status = "CONFLICT"
        return {"status": status, "games": games, "contracts": contracts, "conflicts": conflicts}

    def write(self, games: list, contracts: list, manifest_extra: dict | None = None, funnel: dict | None = None) -> dict:
        plan = self.plan(games, contracts)
        if plan["status"] == "CONFLICT":
            raise ArmsConflict("the same snapshot would be rewritten with different content; nothing written:\n  "
                               + "\n  ".join(plan["conflicts"][:20]))
        if plan["status"] == "NO_OP":
            man = json.load(open(self.manifest_path)) if os.path.exists(self.manifest_path) else {}
            man["status"] = "NO_OP"
            return man
        os.makedirs(self.dir, exist_ok=True)
        _write_gz(self.games_path, plan["games"])
        _write_gz(self.contracts_path, plan["contracts"])
        by_status = {}
        for g in plan["games"]:
            by_status[g.get("status")] = by_status.get(g.get("status"), 0) + 1
        arm_states = {}
        for g in plan["games"]:
            for arm, a in (g.get("arms") or {}).items():
                arm_states.setdefault(arm, {})
                arm_states[arm][a.get("status")] = arm_states[arm].get(a.get("status"), 0) + 1
        man = {"status": "WRITTEN", "run_id": self.run_id, "arms_version": self.arms_version,
               "schema_version": SCHEMA_VERSION,
               "written_at": datetime.now(timezone.utc).isoformat(),
               "n_games": len(plan["games"]), "n_contracts": len(plan["contracts"]),
               "games_by_status": by_status, "arm_status_counts": arm_states,
               "arm_games_file": os.path.basename(self.games_path),
               "arm_contracts_file": os.path.basename(self.contracts_path),
               "arm_games_sha256": sha256_file(self.games_path),
               "arm_contracts_sha256": sha256_file(self.contracts_path),
               "content_hashes_sha256": hashlib.sha256("\n".join(sorted(
                   r["content_hash"] for r in plan["games"] + plan["contracts"])).encode()).hexdigest(),
               "preregistration": R.preregistration(), "preregistration_sha": R.preregistration_sha()}
        man.update(manifest_extra or {})
        with open(self.manifest_path, "w") as f:
            json.dump(man, f, indent=1, default=str)
        if funnel is not None:
            with open(self.funnel_path, "w") as f:
                json.dump(funnel, f, indent=1, default=str)
        return man


def arms_root(market_data: str) -> str:
    return os.path.join(market_data, "data", "shadow", ARMS_DIRNAME)


def snapshot_files(roots, kind: str, day_lo: str | None = None, day_hi: str | None = None) -> list:
    """kind: 'arm_games' | 'arm_contracts'. Bounded by capture day like the settle job's ledger scan."""
    if isinstance(roots, str):
        roots = [roots]
    out = []
    for root in roots:
        for d in sorted(glob.glob(os.path.join(root, "*"))):
            day = os.path.basename(d)
            if not os.path.isdir(d) or (day_lo and day < day_lo) or (day_hi and day > day_hi):
                continue
            out.extend(sorted(glob.glob(os.path.join(d, f"*.{kind}.jsonl.gz"))))
    return out


def load_records(roots, kind: str, game_ids=None, day_lo=None, day_hi=None) -> dict:
    """record_id -> row, de-duplicated across roots (the first occurrence wins; identical by construction)."""
    want = set(game_ids) if game_ids else None
    out = {}
    for path in snapshot_files(roots, kind, day_lo, day_hi):
        for row in read_rows(path):
            if want is not None and row.get("game_id") not in want:
                continue
            out.setdefault(row["record_id"], row)
    return out


def verify_snapshots(roots) -> dict:
    """Re-derive every manifest's checksums and every row's content hash. Used before publishing."""
    problems, n_files, n_rows = [], 0, 0
    for path in snapshot_files(roots, "arm_games") + snapshot_files(roots, "arm_contracts"):
        n_files += 1
        kind = "arm_games" if path.endswith(".arm_games.jsonl.gz") else "arm_contracts"
        man_path = path.replace(f".{kind}.jsonl.gz", ".arms_manifest.json")
        rows = read_rows(path)
        n_rows += len(rows)
        seen = set()
        for r in rows:
            if r.get("content_hash") != content_hash(r):
                problems.append(f"{path}: {r.get('record_id')} content hash does not match its content")
            if r.get("record_id") in seen:
                problems.append(f"{path}: duplicate record_id {r.get('record_id')}")
            seen.add(r.get("record_id"))
        if not os.path.exists(man_path):
            problems.append(f"{path}: no manifest alongside the snapshot")
            continue
        man = json.load(open(man_path))
        key = f"{kind}_sha256"
        if man.get(key) and man[key] != sha256_file(path):
            problems.append(f"{path}: sha256 does not match the manifest")
        n_key = "n_games" if kind == "arm_games" else "n_contracts"
        if man.get(n_key) is not None and man[n_key] != len(rows):
            problems.append(f"{path}: manifest says {man[n_key]} rows, file holds {len(rows)}")
    return {"files": n_files, "rows": n_rows, "problems": problems, "ok": not problems}
