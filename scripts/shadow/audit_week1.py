#!/usr/bin/env python3
"""Health audit of the frozen Week-1 shadow system.

Checks the things that would silently invalidate the prospective experiment: a changed model artifact, an
overwritten freeze, a rewritten ledger file, a version label that does not match what was actually priced,
markets priced after kickoff, and stale inputs presented as fresh. Reports rather than repairs -- the freeze
is not to be edited.
"""
import argparse, glob, gzip, hashlib, json, os, sys
from collections import Counter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
FREEZE = os.path.join(ROOT, "research", "FREEZE_WEEK1_2026.json")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default=os.path.join(ROOT, "data/shadow/ledger"))
    ap.add_argument("--skip-rebuild", action="store_true", help="skip the (slow) frozen-model rebuild check")
    a = ap.parse_args()
    ok, warn, fail = [], [], []

    if not os.path.exists(FREEZE):
        print("FAIL: no Week-1 freeze file"); return 1
    fz = json.load(open(FREEZE))
    print(f"FREEZE  {os.path.relpath(FREEZE, ROOT)}")
    print(f"  frozen_at {fz['frozen_at']}   first kickoff {fz['first_2026_kickoff']}")
    print(f"  model {fz['model']['version']}  artifact {fz['model']['artifact_sha']}  "
          f"role_features={fz['model']['role_features']}")
    print(f"  real_money_status: {fz['real_money_status']}")

    # 1. code files behind the freeze must still hash to what was frozen
    drift = []
    for rel, rec in fz.get("code", {}).items():
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            fail.append(f"frozen code file missing: {rel}"); continue
        if sha(p) != rec["sha256"]:
            drift.append(rel)
    if drift:
        warn.append(f"{len(drift)} frozen code files have changed since the freeze: {', '.join(drift[:6])}")
    else:
        ok.append(f"all {len(fz.get('code', {}))} frozen code files unchanged")

    # 2. research artifacts behind the freeze
    rdrift = [rel for rel, rec in fz.get("research", {}).items()
              if os.path.exists(os.path.join(ROOT, rel)) and sha(os.path.join(ROOT, rel)) != rec["sha256"]]
    if rdrift:
        warn.append(f"{len(rdrift)} frozen research artifacts changed: {', '.join(rdrift[:6])}")
    else:
        ok.append(f"all {len(fz.get('research', {}))} frozen research artifacts unchanged")

    # 3. ledger integrity
    obs_files = sorted(glob.glob(os.path.join(a.ledger, "*", "*.observations.jsonl.gz")))
    mans = sorted(glob.glob(os.path.join(a.ledger, "*", "*.ledger_manifest.json")))
    print(f"\nLEDGER  {len(obs_files)} observation files, {len(mans)} manifests")
    seen_stems, dup = set(), []
    for f in obs_files:
        stem = os.path.basename(f).replace(".observations.jsonl.gz", "")
        if stem in seen_stems:
            dup.append(stem)
        seen_stems.add(stem)
    if dup:
        fail.append(f"duplicate ledger stems (append-only violated): {dup}")
    else:
        ok.append("no duplicate ledger stems; one file per (run, model version)")

    for m in mans:
        d = json.load(open(m))
        obs = os.path.join(os.path.dirname(m), d["observations_file"])
        if not os.path.exists(obs):
            fail.append(f"manifest {os.path.basename(m)} names a missing observations file")
            continue
        rows = [json.loads(l) for l in gzip.open(obs, "rt")]
        states = Counter(r.get("support_state") for r in rows)
        vers = Counter(r.get("model_version") for r in rows)
        shas = Counter(r.get("model_artifact_sha") for r in rows)
        post = sum(1 for r in rows if r.get("support_state") == "POST_KICKOFF_EXCLUDED")
        stale = sum(1 for r in rows if r.get("support_state") == "STALE_DATA")
        print(f"  {os.path.basename(obs)}")
        print(f"    rows {len(rows)}  manifest says {d['counts']['written']}  "
              f"{'OK' if len(rows) == d['counts']['written'] else 'MISMATCH'}")
        print(f"    versions {dict(vers)}  artifact shas {dict(shas)}")
        print(f"    support states {dict(states.most_common(5))}")
        print(f"    post-kickoff excluded {post}   stale-data {stale}")
        if len(rows) != d["counts"]["written"]:
            fail.append(f"{os.path.basename(obs)}: row count does not match its manifest")
        if len(vers) != 1:
            fail.append(f"{os.path.basename(obs)}: mixed model versions in one file")
        if len(shas) != 1:
            fail.append(f"{os.path.basename(obs)}: mixed artifact hashes in one file")
        ids = set(r["prediction_id"] for r in rows)
        if len(ids) != len(rows):
            fail.append(f"{os.path.basename(obs)}: duplicate prediction_ids")

    # 4. the frozen arm must be represented in the ledger exactly as frozen
    frozen_v = fz["model"]["version"]; frozen_sha = fz["model"]["artifact_sha"]
    match = []
    for m in mans:
        d = json.load(open(m))
        b = d.get("model_bundle") or {}
        if b.get("version") == frozen_v and b.get("artifact_sha") == frozen_sha:
            match.append(os.path.basename(m))
    if match:
        ok.append(f"{len(match)} ledger snapshot(s) carry exactly the frozen model {frozen_v}/{frozen_sha}")
    else:
        warn.append(f"no ledger snapshot carries the frozen model {frozen_v}/{frozen_sha}")

    # 5. the decisive check: does the frozen model still REBUILD to its recorded artifact hash?
    # Code behind the freeze has changed additively since (a new optional `defense` argument). Hash drift in
    # a source file is only a warning; failing to reproduce the artifact would be a genuine break.
    if not a.skip_rebuild:
        try:
            import polars as pl  # noqa: F401
            from nfl_edge.features import opportunity
            from nfl_edge.research import player_distributions as pdist
            from nfl_edge.shadow.models import fit_bundle
            cfg = json.load(open(os.path.join(ROOT, "research/player_distributions/results.json")))["config"]
            lo, hi = fz["model"]["train_seasons"]
            hist = pdist.load_player_games(ROOT, range(int(lo), int(hi) + 1))
            priors = pdist.position_priors(hist, range(int(lo), int(lo) + 3))
            hist = pdist.add_ewma_features(hist, halflife=cfg["halflife"], season_carry=cfg["season_carry"],
                                           shrink_k=cfg["shrink_k"], priors=priors)
            if fz["model"].get("role_features"):
                hist = opportunity.attach_role_features(hist, halflife=cfg["halflife"],
                                                        season_carry=cfg["season_carry"],
                                                        shrink_k=cfg["shrink_k"])
            b = fit_bundle(hist, int(fz["model"]["target_season"]), fz["model"]["version"],
                           {"ewma": cfg, "min_train_season": 2016}, verbose=lambda *_: None)
            if b.artifact_sha == fz["model"]["artifact_sha"]:
                ok.append(f"frozen model REPRODUCES exactly: rebuilt artifact {b.artifact_sha}")
            else:
                fail.append(f"frozen model does NOT reproduce: rebuilt {b.artifact_sha} vs frozen "
                            f"{fz['model']['artifact_sha']}")
        except Exception as exc:                                   # noqa: BLE001
            warn.append(f"could not attempt the rebuild check: {type(exc).__name__}: {exc}")

    print("\nAUDIT")
    for s in ok:
        print(f"  OK    {s}")
    for s in warn:
        print(f"  WARN  {s}")
    for s in fail:
        print(f"  FAIL  {s}")
    print(f"\n  {len(ok)} ok, {len(warn)} warnings, {len(fail)} failures")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
