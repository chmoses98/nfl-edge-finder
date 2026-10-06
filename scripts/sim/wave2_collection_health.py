#!/usr/bin/env python3
"""WAVE-2 COLLECTION HEALTH -- is the prospective evidence being collected? (RESEARCH_ONLY; stdlib only)

    python3 scripts/sim/wave2_collection_health.py --market-data-ref origin/market-data --out data/ops/wave2_collection \\
        [--fail-on-recent-miss-hours 48]
    python3 scripts/sim/wave2_collection_health.py --validate-dir /tmp/rehearsal [--allow-dry-run]

Every capture window OWED by the schedule is classified -- never only the records that happen to exist, because a
missed window writes no record and counting records would report zero misses forever:

  per (post-cutoff game, EARLY | LATE):   CAPTURED / INVALID:<reason> / MISSED / OPEN / NOT_YET_OPEN /
                                          NOT_OWED_PRE_ACTIVATION (the window closed before the workflow was on main)
  per record file:                        WRITE_ONCE_COLLISION when two files claim one (game, window)
  per post-cutoff game (RISK1):           SCRIPT_CAPTURED / SCRIPT_CAPTURED_NO_FINGERPRINTS / SCRIPT_MISSING

INVALID reasons cover malformed records, incoherent arms, a stale components hash, a wrong schema version, a record
generated at or after kickoff, a dry-run record on market-data, missing arms or fields. A workflow failure or a
failed publication shows up here as MISSED (and in scripts/ops/workflow_outcomes.py as the failed run).

This reads prediction records and pregame GAME SCRIPT V2 captures only. It reads no outcome, scores nothing and
reports no metric: the registered comparisons are the frozen scorer's (scripts/sim/wave2_score.py), at the frozen
minimum samples. Exit 1 with --fail-on-recent-miss-hours N when anything owed in the last N hours is not CAPTURED.
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import os
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.sim import wave2_due as WD  # noqa: E402

HEALTH_VERSION = "wave2-collection-health-1.0.0"
# Frozen identities the records must carry (tested equal to nfl_edge/sim/wave2_score.py).
FROZEN_COMPONENTS_SHA256 = "353541d18e7e77f4cb06de4233f1b33ef0ff9772941c7792044f55a936ea7008"
ACCEPTED_RECORD_VERSIONS = ("wave2-prospective-1.1.0",)
ARMS = ("A0", "S1", "Q1", "A1", "M1")
# wave2-research.yml reached main in the merge of PR #113 (427911b, committer time). A window that closed before this
# instant was never owed to the workflow; it is reported, never hidden, as NOT_OWED_PRE_ACTIVATION.
ACTIVE_SINCE = "2026-10-06T02:53:04+00:00"
FINGERPRINT_WINDOW_H = 6.0
SIM_PREFIX = "data/shadow/sim/"


def _ts(x) -> datetime:
    return WD._ts(x)


# ------------------------------------------------------------------------------------------ record checks
def record_problems(doc: dict, name: str, *, allow_dry_run: bool = False, rehearsal: bool = False) -> list:
    """Integrity problems of one record file (empty list = valid). Prediction content only. `rehearsal` (a replay of
    a past cutoff into /tmp, never published) accepts dry_run records and skips ONLY the generated-before-kickoff
    check, which a replay can never pass; the feature cutoff must still precede kickoff."""
    allow_dry_run = allow_dry_run or rehearsal
    p = []
    nm = WD.parse_record_name(name)
    games = doc.get("games") or {}
    if nm is None:
        return ["unparseable file name"]
    if list(games) != [nm[0]]:
        p.append("file name game_id does not match the record's single game")
    if doc.get("research_only") is not True or doc.get("betting_authority") != "NONE":
        p.append("research_only / betting_authority NONE not declared")
    if doc.get("dry_run") and not allow_dry_run:
        p.append("dry-run record")
    if doc.get("wave2_version") not in ACCEPTED_RECORD_VERSIONS:
        p.append(f"schema version {doc.get('wave2_version')} not accepted")
    if (doc.get("inputs") or {}).get("components_sha256") != FROZEN_COMPONENTS_SHA256:
        p.append("stale or wrong components hash")
    if doc.get("prospective_cutoff") != WD.PROSPECTIVE_CUTOFF:
        p.append("wrong prospective cutoff")
    g = games.get(nm[0]) or {}
    if g.get("window") != nm[1]:
        p.append("window in file name does not match the record")
    if g.get("state") != "OK":
        p.append(f"capture state {g.get('state')}")
        return p
    try:
        ko = _ts(g["kickoff_utc"])
        if ko <= _ts(WD.PROSPECTIVE_CUTOFF):
            p.append("kickoff before the prospective cutoff")
        if not doc.get("generated_at") or (_ts(doc["generated_at"]) >= ko and not rehearsal):
            p.append("generated at or after kickoff")
        if not g.get("cutoff") or _ts(g["cutoff"]) >= ko:
            p.append("feature cutoff at or after kickoff")
        elif WD.window_at(ko, _ts(g["cutoff"])) != nm[1]:
            p.append("cutoff not inside the named window")
    except (KeyError, ValueError) as e:
        p.append(f"bad instants: {e}")
    parts = nm[0].split("_")
    if len(parts) == 4 and (g.get("away_team"), g.get("home_team")) != (parts[2], parts[3]):
        p.append("home / away teams do not match the game id")
    arms = g.get("arms") or {}
    for a in ARMS:
        if a not in arms:
            p.append(f"arm {a} missing")
    coh = g.get("coherence") or {}
    bad = [a for a in ARMS if coh.get(a) is not True]
    if bad:
        p.append("incoherent arm(s): " + ",".join(bad))
    if not g.get("avail_state"):
        p.append("avail_state missing")
    if not g.get("m1k_exact_margin_pmf"):
        p.append("m1k_exact_margin_pmf missing")
    for a in ("A0", "M1"):
        for k in ("margin_pmf", "total_pmf", "v2_cells"):
            if k not in (arms.get(a) or {}):
                p.append(f"{a}.{k} missing")
    if g.get("horizon") not in ("T0_INACTIVES", "T24"):
        p.append(f"unknown horizon {g.get('horizon')}")
    return p


# ------------------------------------------------------------------------------------------ sources
class GitSource:
    """Names and blobs from a git ref of market-data (a blob-less fetch is enough; blobs load on demand)."""

    def __init__(self, ref: str):
        self.ref = ref

    def names(self, prefix: str) -> list:
        r = subprocess.run(["git", "ls-tree", "-r", "--name-only", self.ref, prefix], cwd=ROOT, capture_output=True, text=True)
        return r.stdout.split()

    def read(self, path: str) -> bytes:
        return subprocess.run(["git", "show", f"{self.ref}:{path}"], cwd=ROOT, capture_output=True).stdout


class DirSource:
    def __init__(self, root: str):
        self.root = root

    def names(self, prefix: str) -> list:
        base = os.path.join(self.root, prefix)
        return sorted(os.path.relpath(p, self.root) for p in glob.glob(os.path.join(base, "**", "*"), recursive=True)
                      if os.path.isfile(p))

    def read(self, path: str) -> bytes:
        with open(os.path.join(self.root, path), "rb") as f:
            return f.read()


def _doc(src, path):
    try:
        return json.loads(gzip.decompress(src.read(path)))
    except Exception as e:  # noqa: BLE001 -- a malformed file is a finding, not a crash
        return {"_error": f"{type(e).__name__}: {e}"}


# ------------------------------------------------------------------------------------------ classification
def classify(games: list, src, now: datetime, *, active_since: str = ACTIVE_SINCE, allow_dry_run: bool = False,
             lookback_days: float = 200.0) -> dict:
    pc, act = _ts(WD.PROSPECTIVE_CUTOFF), _ts(active_since)
    names = [n for n in src.names(WD.RECORD_PREFIX) if WD.parse_record_name(n)]
    by_key = {}
    for n in names:
        gid, w, _ = WD.parse_record_name(n)
        by_key.setdefault((gid, w), []).append(n)
    windows, records = [], []
    for (gid, w), files in sorted(by_key.items()):
        for f in files:
            d = _doc(src, f)
            probs = [d["_error"]] if "_error" in d else record_problems(d, f, allow_dry_run=allow_dry_run)
            records.append({"path": f, "game_id": gid, "window": w, "valid": not probs, "problems": probs,
                            "generated_at": d.get("generated_at"),
                            "kickoff_utc": ((d.get("games") or {}).get(gid) or {}).get("kickoff_utc"),
                            "horizon": ((d.get("games") or {}).get(gid) or {}).get("horizon")})
    rec_by_key = {}
    for r in records:
        rec_by_key.setdefault((r["game_id"], r["window"]), []).append(r)
    horizon_lo = now - timedelta(days=lookback_days)
    for g in games or []:
        ko = g.get("kickoff_utc")
        if not ko or not g.get("game_id"):
            continue
        ko = _ts(ko)
        if ko <= pc or ko < horizon_lo:
            continue
        for w in WD.WINDOWS:
            opens, closes = WD.window_bounds(ko, w)
            rs = rec_by_key.get((g["game_id"], w), [])
            if len(rs) > 1:
                status = "WRITE_ONCE_COLLISION"
            elif rs:
                status = "CAPTURED" if rs[0]["valid"] else "INVALID:" + "; ".join(rs[0]["problems"])
            elif now < opens:
                status = "NOT_YET_OPEN"
            elif now < closes:
                status = "OPEN"
            elif closes <= act:
                status = "NOT_OWED_PRE_ACTIVATION"
            else:
                status = "MISSED"
            windows.append({"game_id": g["game_id"], "window": w, "kickoff_utc": ko.isoformat(), "opens": opens.isoformat(),
                            "closes": closes.isoformat(), "status": status, "files": [r["path"] for r in rs],
                            "horizon": rs[0]["horizon"] if len(rs) == 1 else None})
    known = {(w["game_id"], w["window"]) for w in windows}
    orphans = [r for r in records if (r["game_id"], r["window"]) not in known]
    return {"windows": windows, "records": records, "orphan_records": orphans}


def risk1_scripts(games: list, src, now: datetime, *, active_since: str = ACTIVE_SINCE, lookback_days: float = 8.0) -> list:
    """Per post-cutoff game whose kickoff has passed: was a GAME SCRIPT V2 capture generated before kickoff, and
    (after activation) does a capture within 6 h of kickoff carry world fingerprints? Pregame documents only."""
    pc, act = _ts(WD.PROSPECTIVE_CUTOFF), _ts(active_since)
    lo = now - timedelta(days=lookback_days)
    caps = [n for n in src.names(SIM_PREFIX) if n.endswith(".scripts_v2.json.gz")]
    games_past = [g for g in games or [] if g.get("kickoff_utc") and pc < _ts(g["kickoff_utc"]) <= now
                  and _ts(g["kickoff_utc"]) >= lo]
    if not games_past:
        return []
    per_game = {g["game_id"]: [] for g in games_past}
    for n in caps:
        run = os.path.basename(n)[:16]
        try:
            run_t = datetime.strptime(run, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if run_t < lo - timedelta(days=1):
            continue
        d = _doc(src, n)
        for gid, gd in (d.get("games") or {}).items():
            if gid in per_game and gd.get("state") == "OK" and gd.get("generated_at"):
                fp = sum(1 for c in gd.get("contracts") or [] if c.get("fingerprint"))
                per_game[gid].append({"path": n, "generated_at": gd["generated_at"], "contracts": len(gd.get("contracts") or []),
                                      "fingerprinted": fp})
    out = []
    for g in games_past:
        ko = _ts(g["kickoff_utc"])
        pre = sorted((c for c in per_game[g["game_id"]] if _ts(c["generated_at"]) < ko), key=lambda c: c["generated_at"])
        if not pre:
            status = "SCRIPT_MISSING"
        else:
            last = pre[-1]
            near = (ko - _ts(last["generated_at"])) <= timedelta(hours=FINGERPRINT_WINDOW_H)
            owed_fp = ko > act
            status = ("SCRIPT_CAPTURED" if (last["fingerprinted"] > 0 or not owed_fp) else
                      "SCRIPT_CAPTURED_NO_FINGERPRINTS" if near else "SCRIPT_CAPTURED_NOT_WITHIN_6H")
        out.append({"game_id": g["game_id"], "kickoff_utc": ko.isoformat(), "status": status,
                    "last_pre_kickoff_capture": pre[-1] if pre else None, "n_pre_kickoff_captures": len(pre)})
    return out


def summarize(res: dict, risk: list) -> dict:
    wc = Counter(w["status"].split(":")[0] for w in res["windows"])
    by_window = {w: Counter(x["status"].split(":")[0] for x in res["windows"] if x["window"] == w) for w in WD.WINDOWS}
    hz = Counter(x["horizon"] for x in res["windows"] if x["status"] == "CAPTURED" and x["window"] == "LATE")
    return {"windows": dict(wc), "by_window": {k: dict(v) for k, v in by_window.items()},
            "late_captured_by_horizon": dict(hz), "records": len(res["records"]),
            "invalid_records": sum(1 for r in res["records"] if not r["valid"]), "orphan_records": len(res["orphan_records"]),
            "risk1": dict(Counter(r["status"] for r in risk))}


def failures(res: dict, risk: list, now: datetime, hours: float) -> list:
    lo = now - timedelta(hours=hours)
    bad = [f"{w['game_id']} {w['window']}: {w['status']}" for w in res["windows"]
           if w["status"] not in ("CAPTURED", "OPEN", "NOT_YET_OPEN", "NOT_OWED_PRE_ACTIVATION") and _ts(w["closes"]) >= lo]
    bad += [f"{r['game_id']} RISK1: {r['status']}" for r in risk
            if r["status"] in ("SCRIPT_MISSING", "SCRIPT_CAPTURED_NO_FINGERPRINTS") and _ts(r["kickoff_utc"]) >= lo
            and _ts(r["kickoff_utc"]) > _ts(ACTIVE_SINCE)]
    bad += [f"{r['path']}: orphan record (no scheduled post-cutoff game)" for r in res["orphan_records"]]
    return bad


def table(res: dict, risk: list, now: datetime | None = None) -> str:
    """Games kicking off from 8 days ago to 4 days ahead (the JSON keeps every game)."""
    rows = ["| game | kickoff (UTC) | EARLY | LATE | RISK1 script |", "|---|---|---|---|---|"]
    by_game = {}
    for w in res["windows"]:
        if now is not None and not (now - timedelta(days=8) <= _ts(w["kickoff_utc"]) <= now + timedelta(days=4)):
            continue
        by_game.setdefault(w["game_id"], {"ko": w["kickoff_utc"]})[w["window"]] = w["status"]
    rk = {r["game_id"]: r["status"] for r in risk}
    for gid, v in sorted(by_game.items(), key=lambda kv: kv[1]["ko"]):
        rows.append(f"| {gid} | {v['ko'][:16]} | {v.get('EARLY', '')} | {v.get('LATE', '')} | {rk.get(gid, '-')} |")
    return "\n".join(rows) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data-ref", default=None)
    ap.add_argument("--records-root", default=None, help="a market-data checkout instead of a git ref")
    ap.add_argument("--validate-dir", default=None, help="validate every record under DIR/data/research/wave2 and exit")
    ap.add_argument("--allow-dry-run", action="store_true")
    ap.add_argument("--rehearsal", action="store_true", help="validate replayed dry-run records (see record_problems)")
    ap.add_argument("--out", default=None)
    ap.add_argument("--now", default=None)
    ap.add_argument("--fail-on-recent-miss-hours", type=float, default=None)
    a = ap.parse_args(argv)
    if a.validate_dir:
        src = DirSource(a.validate_dir)
        bad = 0
        for n in src.names(WD.RECORD_PREFIX):
            if not WD.parse_record_name(n):
                continue
            probs = record_problems(_doc(src, n), n, allow_dry_run=a.allow_dry_run, rehearsal=a.rehearsal)
            print(f"{'VALID' if not probs else 'INVALID'}  {n}" + (f"  {probs}" if probs else ""))
            bad += bool(probs)
        return 1 if bad else 0
    now = _ts(a.now) if a.now else datetime.now(timezone.utc)
    src = GitSource(a.market_data_ref) if a.market_data_ref else DirSource(a.records_root or ".")
    from nfl_edge.data.nfl_calendar import load_schedule
    games, sched_src = load_schedule(ROOT, allow_download=True)
    res = classify(games, src, now)
    risk = risk1_scripts(games, src, now)
    summ = summarize(res, risk)
    bad = failures(res, risk, now, a.fail_on_recent_miss_hours or 48.0)
    doc = {"health_version": HEALTH_VERSION, "at": now.isoformat(), "schedule_source": sched_src,
           "prospective_cutoff": WD.PROSPECTIVE_CUTOFF, "active_since": ACTIVE_SINCE, "research_only": True,
           "note": "collection integrity only: no outcome is read and no registered comparison is computed",
           "summary": summ, "recent_failures": bad, **res, "risk1": risk}
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        with open(os.path.join(a.out, f"wave2_collection_{now.strftime('%Y%m%dT%H%M%SZ')}.json"), "w") as f:
            json.dump(doc, f, indent=1, default=str)
    print(f"## Wave-2 collection health ({now.isoformat()[:16]}Z)\n")
    print("Summary: " + json.dumps(summ) + "\n")
    print(table(res, risk, now))
    if bad:
        print("**Not captured / invalid in the last window:**\n" + "\n".join(f"* {b}" for b in bad))
    return 1 if (bad and a.fail_on_recent_miss_hours is not None) else 0


if __name__ == "__main__":
    sys.exit(main())
