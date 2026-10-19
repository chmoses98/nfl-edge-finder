"""The NFL distribution artifact: `projections/nfl/distributions/latest.json` (`sift.projection_distributions.v1`).

    python -m nfl.live.distributions_artifact --archive <projection-data checkout> [--check] [--summary-out FILE]

SIFT's Prop Explorer draws a projection's distribution from its published quantiles, and prices a line from the published line
probabilities. `projections/nfl/latest.json` (`sift.projections.v1`) carries the mean, median, p10/p90 and the study's three rungs but no
quantiles and no full ladder, so the Explorer said "no published distribution". The code that writes `latest.json` is recorded research
(append-only under the repository's guard) and is not edited here. This module is a NEW, separately versioned publication step that reads
what is already archived and writes a second artifact beside `latest.json`:

  projections/nfl/distributions/latest.json            rewritable view, the artifact for the newest `latest.json`
  projections/nfl/distributions/<YYYY-MM-DDTHHMMZ>.json.gz   write-once copy, only when the content changed

Source of truth: the player rows of `projections/nfl/latest.json` and, for each, the pmf archived write-once in `forecasts/nfl/` (the
challenger forecast the row was built from). For every row the artifact carries
  * `quantiles` p05 p10 p25 p50 p75 p90 p95  (smallest integer x with P(X <= x) >= level, from the pmf)
  * `survival`  P(X >= k) for every integer line with 0.001 <= P <= 0.999 for count families (the study's rungs always included); for
    yardage families only the rungs `latest.json` publishes,
all from that one pmf, and ONLY IF the pmf reproduces the published row: same mean (to its 3 published decimals), same median, p10 and p90,
every published threshold within its 4-decimal rounding, and the row's own quantiles, ladder and range cohere (`distribution.validate_row`).
A row that does not reproduce is left out and listed under `excluded` (readers say "no published distribution"); nothing is interpolated,
invented or patched. Nothing archived (forecasts, outcomes, settlements, corrections, availability) is read for writing or modified.
The artifact names the `generated_utc` of the `latest.json` it was built from; a reader must ignore it when that does not match.
"""
from __future__ import annotations

import argparse
import glob
import gzip
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PF_ROOT = os.path.dirname(os.path.dirname(HERE))
if PF_ROOT not in sys.path:
    sys.path.insert(0, PF_ROOT)

from pf_core import dists  # noqa: E402

from nfl.live import distribution as DI  # noqa: E402

SCHEMA = "sift.projection_distributions.v1"
SPORT = "NFL"
REL = os.path.join("projections", "nfl", "distributions")
VOLATILE = {"built_utc"}
PMF_SUM_TOL = 2e-4


def _ts(x: str) -> datetime:
    d = datetime.fromisoformat(str(x).replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _strip(o):
    if isinstance(o, dict):
        return {k: _strip(v) for k, v in o.items() if k not in VOLATILE}
    if isinstance(o, list):
        return [_strip(v) for v in o]
    return o


def _family_kind(family: str, lo: int) -> str:
    """count / binary / yards. The study's own family table is authoritative; without it a floor at zero means a count."""
    try:
        from nfl import pipeline as P
        return P.PLAYER_FAMILIES[family]["kind"]
    except Exception:  # noqa: BLE001
        return "count" if lo >= 0 else "yards"


def load_forecasts(archive: str, until_utc: str) -> dict[tuple[str, str, str], dict]:
    """{(game_id, entity_id, family): the newest challenger forecast generated at or before `until_utc`}. Read-only."""
    cut = _ts(until_utc)
    best: dict[tuple[str, str, str], dict] = {}
    for path in sorted(glob.glob(os.path.join(archive, "forecasts", "nfl", "*", "*.jsonl.gz"))):
        with gzip.open(path, "rt") as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                if r.get("model_role") != "challenger" or r.get("sport") != SPORT or not r.get("probs"):
                    continue
                if _ts(r["generated_utc"]) > cut or _ts(r["generated_utc"]) >= _ts(r["game_start_utc"]):
                    continue
                k = (r["game_id"], r["entity_id"], r["family"])
                if k not in best or _ts(best[k]["generated_utc"]) < _ts(r["generated_utc"]):
                    best[k] = r
    return best


def build_row(pub: dict, rec: dict) -> tuple[dict | None, str | None]:
    """The artifact row for one published row and its archived forecast, or (None, why it was left out)."""
    p = np.asarray(rec["probs"], float)
    # the archive stores the pmf rounded to 7 decimals (a 330-point yards lattice sums to 0.9999855), so the sum is judged to that precision
    if not np.isfinite(p).all() or (p < 0).any() or abs(p.sum() - 1) > PMF_SUM_TOL:
        return None, "the archived pmf is not a probability distribution"
    d = dists.DistBatch(int(rec["lo"]), p[None, :])
    if d.coherence_violations().any():
        return None, "the archived pmf is not a probability distribution"
    # the published mean is rounded to 3 decimals; the archived pmf to 7 decimals per point, which moves a wide lattice's mean by up to
    # 5e-8 x points x |support|
    mean_tol = 6e-4 + 5e-8 * len(p) * (abs(int(rec["lo"])) + len(p))
    if abs(float(d.mean[0]) - float(pub["mean"])) > mean_tol:
        return None, f"the archived pmf's mean {float(d.mean[0]):.3f} is not the published mean {pub['mean']}"
    kind = _family_kind(pub["family"], int(rec["lo"]))
    study = {int(k): d.prob_ge(int(k)) for k in pub.get("thresholds", {})}
    surv = DI.row_thresholds(DI.survival_arrays(d, kind), study, 0)
    q = DI.row_quantiles(DI.quantile_arrays(d), 0)
    row = {"player_id": pub["player_id"], "family": pub["family"], "game_id": pub["game_id"], "forecast_id": rec["forecast_id"],
           "forecast_generated_utc": rec["generated_utc"], "mean": pub["mean"], "median": int(d.median[0]),
           "p10": int(d.quantile(0.1)[0]), "p90": int(d.quantile(0.9)[0]), "quantiles": q, "survival": surv,
           "support": [int(d.lo), int(d.lo) + int(d.P.shape[1]) - 1]}
    for ref in ("median", "p10", "p90"):
        if pub.get(ref) is not None and int(pub[ref]) != row[ref]:
            return None, f"the pmf's {ref} {row[ref]} is not the published {ref} {pub[ref]}"
    for k, v in (pub.get("thresholds") or {}).items():
        if abs(surv[str(int(k))] - float(v)) > DI.TOL + 5e-8 * len(p):
            return None, f"the pmf's P(X>={k}) {surv[str(int(k))]} is not the published {v}"
    problems = DI.validate_row({**row, "thresholds": surv})
    if problems:
        return None, "; ".join(problems[:2])
    return row, None


def build(archive: str) -> dict:
    """{"artifact": dict | None, "stats": {...}}. `artifact` is None when there is no projection document to describe."""
    lp = os.path.join(archive, "projections", "nfl", "latest.json")
    if not os.path.exists(lp):
        return {"artifact": None, "stats": {"note": "no projections/nfl/latest.json"}}
    doc = json.load(open(lp))
    if doc.get("schema") != "sift.projections.v1" or doc.get("sport") != SPORT or not isinstance(doc.get("players"), list):
        return {"artifact": None, "stats": {"note": "latest.json is not an NFL sift.projections.v1 document"}}
    forecasts = load_forecasts(archive, doc["generated_utc"])
    rows: list[dict] = []
    excluded: list[dict] = []
    for pub in doc["players"]:
        rec = forecasts.get((pub["game_id"], pub["player_id"], pub["family"]))
        if rec is None:
            excluded.append({"player_id": pub["player_id"], "family": pub["family"], "game_id": pub["game_id"], "why": "no archived forecast for this row"})
            continue
        row, why = build_row(pub, rec)
        if row is None:
            excluded.append({"player_id": pub["player_id"], "family": pub["family"], "game_id": pub["game_id"], "why": why})
        else:
            rows.append(row)
    rows.sort(key=lambda r: (r["game_id"], r["player_id"], r["family"]))
    art = {"schema": SCHEMA, "sport": SPORT, "contract": "research/projection_foundation/CONTRACT_DISTRIBUTIONS.md",
           "projection": {"schema": doc["schema"], "generated_utc": doc["generated_utc"], "data_asof_utc": doc.get("data_asof_utc"),
                          "model_version": (doc.get("model") or {}).get("version"), "players": len(doc["players"])},
           "distribution": DI.META, "built_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "rows": rows, "excluded": excluded}
    fams: dict[str, int] = {}
    for r in rows:
        fams[r["family"]] = fams.get(r["family"], 0) + 1
    return {"artifact": art, "stats": {"projection_generated_utc": doc["generated_utc"], "published_rows": len(doc["players"]), "rows": len(rows),
                                       "excluded": len(excluded), "by_family": fams, "excluded_why": [e["why"] for e in excluded][:5]}}


def write(archive: str, art: dict) -> dict:
    """latest.json (rewritable, never regresses to an older projection) and a write-once timestamped copy when the content changed."""
    d = os.path.join(archive, REL)
    os.makedirs(d, exist_ok=True)
    latest = os.path.join(d, "latest.json")
    prev = json.load(open(latest)) if os.path.exists(latest) else None
    if prev is not None and _ts(art["projection"]["generated_utc"]) < _ts(prev["projection"]["generated_utc"]):
        return {"written": False, "why": "a newer artifact exists (an older clock never regresses latest.json)"}
    if prev is not None and _strip(prev) == _strip(art):
        return {"written": False, "why": "unchanged"}
    stamp = _ts(art["projection"]["generated_utc"]).strftime("%Y-%m-%dT%H%MZ")
    copy = os.path.join(d, f"{stamp}.json.gz")
    if not os.path.exists(copy):      # write-once; mtime=0 keeps the bytes a pure function of the content
        with open(copy, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as gz:
            gz.write(json.dumps(art, sort_keys=True).encode())
    with open(latest, "w") as f:
        json.dump(art, f, indent=1, sort_keys=True)
    return {"written": True, "latest": os.path.relpath(latest, archive), "copy": os.path.relpath(copy, archive),
            "sha256": hashlib.sha256(json.dumps(_strip(art), sort_keys=True).encode()).hexdigest()[:16]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--archive", required=True)
    ap.add_argument("--check", action="store_true", help="build and validate, write nothing")
    ap.add_argument("--summary-out", default=None)
    a = ap.parse_args(argv)
    t0 = time.time()
    res = build(a.archive)
    out = dict(res["stats"])
    if res["artifact"] is None:
        print(f"distributions: nothing to publish ({out.get('note')})")
    else:
        out["write"] = {"written": False, "why": "--check"} if a.check else write(a.archive, res["artifact"])
        print(f"distributions: {out['rows']} of {out['published_rows']} rows ({out['excluded']} excluded) {out['by_family']}; {out['write']}")
        for e in res["artifact"]["excluded"][:8]:
            print(f"::warning::distribution excluded {e['player_id']} {e['family']}: {e['why']}")
    out["seconds"] = round(time.time() - t0, 2)
    if a.summary_out:
        with open(a.summary_out, "w") as f:
            json.dump(out, f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
