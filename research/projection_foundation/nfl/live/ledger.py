"""Incumbent forecasts for the live comparison: read-only views of the shadow ledger on the `market-data` branch.

The incumbent is `shadow-0.4.0` (data/shadow/ledger/<day>/<run>.shadow-0.4.0.observations.jsonl.gz): it prices Kalshi
contracts, so for a player-stat it holds P(X >= k) at the listed thresholds k (`model_event_probability`), NOT a pmf or a
mean. The mean of the same projection is frozen next to it in the player-anatomy corpus
(data/shadow/player_anatomy/<game_id>/anatomy-1.0.0.<run>.anatomy.jsonl.gz, `projected_stat_mean`), which the pricing
workflow writes from the incumbent's own code path and reconciles with the ledger row to 1e-9. Both are only READ here:
nothing is re-run, re-priced or written back; the ledger, the shadow-0.5.0 challenger and the disagreement diagnosis keep
running exactly as before.

What is archived (model_role "incumbent", model_id "shadow-0.4.0"): the mean from the anatomy and the ladder
{threshold: probability} from the ledger, `probs` empty (the incumbent publishes no pmf) -> MAE and rung-Brier scoring
only. Only the Kalshi-listed population has an incumbent forecast, and `targets`/`carries` ... see FAMILY below: the
incumbent has no `targets` contract, so that family is challenger-only.

shadow-0.5.0 (data/shadow/ledger_challenger/...) is ladder-only (no anatomy, hence no mean or pmf): it cannot be archived
as a forecast of its own. Its ladders for the same player-stats are attached to the incumbent record as `ladder_050` so
the rung-Brier comparison covers it too; this is reported, never scored as a mean.
"""
from __future__ import annotations

import gzip
import json
import os
import re
import subprocess
from collections import defaultdict
from datetime import datetime, timezone

from pf_core import availability as av

FAMILY = {"attempts": "passing_attempts", "completions": "completions", "passing_yards": "passing_yards",
          "passing_tds": "passing_tds", "receptions": "receptions", "receiving_yards": "receiving_yards",
          "carries": "carries", "rushing_yards": "rushing_yards", "touchdowns": "anytime_td"}
INCUMBENT = {"dir": "data/shadow/ledger", "model": "shadow-0.4.0", "role": "incumbent"}
CHALLENGER_050 = {"dir": "data/shadow/ledger_challenger", "model": "shadow-0.5.0", "role": "incumbent_challenger"}
ANATOMY_DIR = "data/shadow/player_anatomy"
RUN_RE = re.compile(r"^(\d{8}T\d{6}Z)\.(shadow-[\d.]+)\.observations\.jsonl\.gz$")


class GitReader:
    """Read blobs/trees of `market-data` lazily from a blobless fetch (only the blobs that are opened are downloaded)."""

    def __init__(self, repo: str = ".", ref: str = "origin/market-data"):
        self.repo, self.ref = repo, ref

    def fetch(self) -> None:
        """Blobless depth-1 fetch of market-data (trees only; a blob is downloaded when it is first read)."""
        for k, v in (("remote.origin.promisor", "true"), ("remote.origin.partialclonefilter", "blob:none")):
            subprocess.run(["git", "config", k, v], cwd=self.repo, check=True)
        subprocess.run(["git", "fetch", "--no-tags", "--depth=1", "--filter=blob:none", "origin", "market-data"],
                       cwd=self.repo, check=True, capture_output=True, text=True)
        self.ref = subprocess.run(["git", "rev-parse", "FETCH_HEAD"], cwd=self.repo, check=True, capture_output=True, text=True).stdout.strip()

    def ls(self, path: str) -> list[str]:
        r = subprocess.run(["git", "ls-tree", "--name-only", self.ref, path.rstrip("/") + "/"], cwd=self.repo,
                           capture_output=True, text=True)
        return sorted(os.path.basename(x) for x in r.stdout.splitlines() if x) if r.returncode == 0 else []

    def cat(self, path: str) -> bytes | None:
        r = subprocess.run(["git", "cat-file", "-p", f"{self.ref}:{path}"], cwd=self.repo, capture_output=True)
        return r.stdout if r.returncode == 0 else None


class DirReader:
    """Same interface over a plain directory (tests, recorded payloads)."""

    def __init__(self, root: str):
        self.root = root

    def fetch(self) -> None:
        pass

    def ls(self, path: str) -> list[str]:
        p = os.path.join(self.root, path)
        return sorted(os.listdir(p)) if os.path.isdir(p) else []

    def cat(self, path: str) -> bytes | None:
        p = os.path.join(self.root, path)
        return open(p, "rb").read() if os.path.isfile(p) else None


def _run_ts(run_id: str) -> datetime:
    return datetime.strptime(run_id, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)


def latest_run(reader, spec: dict, now_utc: str, lookback_days: int = 3) -> tuple[str, str] | None:
    """(run_id, path) of the newest ledger snapshot of this model whose run time is before `now`."""
    now = av._ts(now_utc)
    days = sorted(reader.ls(spec["dir"]), reverse=True)
    best = None
    for d in days[:lookback_days + 1]:
        for fn in reader.ls(f"{spec['dir']}/{d}"):
            m = RUN_RE.match(fn)
            if m and m.group(2) == spec["model"] and _run_ts(m.group(1)) < now:
                if best is None or m.group(1) > best[0]:
                    best = (m.group(1), f"{spec['dir']}/{d}/{fn}")
    return best


def _anatomy(reader, game_id: str, run_id: str) -> dict[tuple, dict]:
    """(player_id, stat) -> anatomy row from the newest anatomy snapshot of the game at or before the ledger run."""
    files = [f for f in reader.ls(f"{ANATOMY_DIR}/{game_id}") if f.endswith(".anatomy.jsonl.gz")]
    cands = []
    for f in files:
        m = re.search(r"\.(\d{8}T\d{6}Z)\.anatomy\.jsonl\.gz$", f)
        if m and m.group(1) <= run_id:
            cands.append((m.group(1), f))
    out: dict[tuple, dict] = {}
    if not cands:
        return out
    run, fn = max(cands)
    blob = reader.cat(f"{ANATOMY_DIR}/{game_id}/{fn}")
    if not blob:
        return out
    for line in gzip.decompress(blob).decode().splitlines():
        r = json.loads(line)
        if r.get("anatomy_status") == "OK" and r.get("projected_stat_mean") is not None:
            out[(r["player_id"], r["stat"])] = {**r, "_anatomy_run": run}
    return out


def _read_groups(reader, spec: dict, now_utc: str, game_ids: set[str]) -> tuple[dict, str | None, dict]:
    """{(game, player, stat): {"row": first row, "ladder": {threshold: P(X >= k)}}} from the newest snapshot before now."""
    run = latest_run(reader, spec, now_utc)
    stats = {"ledger_run": run[0] if run else None, "rungs": 0}
    if run is None:
        return {}, None, {**stats, "error": "no ledger snapshot before now"}
    blob = reader.cat(run[1])
    if blob is None:
        return {}, run[0], {**stats, "error": f"cannot read {run[1]}"}
    now = av._ts(now_utc)
    groups: dict[tuple, dict] = {}
    for line in gzip.decompress(blob).decode().splitlines():
        r = json.loads(line)
        if r.get("family") != "PLAYER_STAT" or r.get("support_state") != "SUPPORTED" or r.get("stat") not in FAMILY:
            continue
        if r.get("game_id") not in game_ids or r.get("operator") != ">=" or r.get("threshold") is None:
            continue
        ko = av._ts(r.get("kickoff_utc"))
        if ko is None or ko <= now:
            continue
        k = (r["game_id"], r["player_id"], r["stat"])
        g = groups.setdefault(k, {"row": r, "ladder": {}, "file": run[1]})
        g["ladder"][str(int(r["threshold"]))] = float(r["model_event_probability"])
        stats["rungs"] += 1
    return groups, run[0], stats


def read_ledger(reader, spec: dict, now_utc: str, game_ids: set[str], with_anatomy: bool = True, ladders_050: dict | None = None) -> dict:
    """Incumbent forecast records for the given upcoming games from the newest ledger snapshot before `now`.

    Returns {"records": [...], "run_id": ..., "stats": {...}}. Records follow pf_core.prospective.FORECAST_FIELDS (+ extras)."""
    groups, run_id, stats = _read_groups(reader, spec, now_utc, game_ids)
    stats.update(player_stats=0, without_mean=0, no_anatomy_games=0)
    if not groups:
        return {"records": [], "run_id": run_id, "stats": stats}
    anat: dict[str, dict] = {}
    recs = []
    for (gid, pid, stat), g in groups.items():
        fam = FAMILY[stat]
        r = g["row"]
        stats["player_stats"] += 1
        mean = None
        extra = {}
        if fam == "anytime_td":
            mean = g["ladder"].get("1")                      # P(at least one TD) is the family's "mean" (Bernoulli)
        elif with_anatomy and spec["model"] == INCUMBENT["model"]:
            if gid not in anat:
                anat[gid] = _anatomy(reader, gid, run_id)
                if not anat[gid]:
                    stats["no_anatomy_games"] += 1
            a = anat[gid].get((pid, stat))
            if a is not None:
                mean = float(a["projected_stat_mean"])
                th = str(int(a["threshold"])) if a.get("threshold") is not None else None
                cons = (th in g["ladder"] and a.get("ledger_event_probability") is not None
                        and abs(float(a["ledger_event_probability"]) - g["ladder"][th]) < 0.005)
                extra = {"anatomy_run": a["_anatomy_run"], "mean_asof_utc": a.get("feature_cutoff"),
                         "anatomy_consistent_with_ledger": bool(cons), "distribution_family": a.get("distribution_family"),
                         "model_quantiles": a.get("model_quantiles"), "p_plays": a.get("p_plays")}
                stats["anatomy_consistent"] = stats.get("anatomy_consistent", 0) + int(cons)
        if mean is None:
            stats["without_mean"] += 1
            continue
        l050 = (ladders_050 or {}).get((gid, pid, stat))
        recs.append({
            "sport": "NFL", "family": fam, "model_id": spec["model"], "model_role": spec["role"], "model_version": spec["model"],
            "game_id": gid, "game_start_utc": r["kickoff_utc"], "entity_id": pid, "entity_name": r.get("player_name"),
            "team": r.get("team"), "generated_utc": av.iso(av._ts(r["feature_cutoff"])), "data_asof_utc": av.iso(av._ts(r["feature_cutoff"])),
            "mean": mean, "lo": 0, "probs": [], "gate_status": None, "participation": r.get("availability_state"),
            "readiness": None, "ladder": g["ladder"], "ledger_run": run_id, "ledger_file": g["file"],
            **({"ladder_050": l050["ladder"]} if l050 else {}), **extra})
    stats["records"] = len(recs)
    return {"records": recs, "run_id": run_id, "stats": stats}


def incumbent_forecasts(reader, now_utc: str, game_ids: set[str]) -> dict:
    """shadow-0.4.0 (role incumbent): anatomy mean + ledger ladder; shadow-0.5.0 ladders attached as `ladder_050`."""
    l050, run050, st050 = _read_groups(reader, CHALLENGER_050, now_utc, game_ids)
    inc = read_ledger(reader, INCUMBENT, now_utc, game_ids, ladders_050=l050)
    inc["stats"]["challenger_050_run"] = run050
    inc["stats"]["challenger_050_player_stats"] = len(l050)
    return inc
