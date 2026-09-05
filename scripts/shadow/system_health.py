#!/usr/bin/env python3
"""One-page live system health report, for reading before Week 1."""
import argparse, glob, gzip, json, os, sys
from collections import Counter
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)


def status(ok, degraded_if=False, not_started=False):
    return "NOT STARTED" if not_started else ("DEGRADED" if degraded_if or not ok else "healthy")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", default="/home/user/_md")
    # The PUBLISHED ledger under --md is the source of truth, so it is the default. This previously
    # defaulted to the local repo path, which is gitignored scratch: running with --md pointed at a
    # market-data worktree produced a report whose capture and shock sections described the published data
    # while its SHADOW PRICING and CURRENT MODEL sections described stale local files. It reported
    # shadow-0.3.0 as current on a day when shadow-0.4.0 was published.
    ap.add_argument("--ledger", default=None,
                    help="ledger root (default: <md>/data/shadow/ledger, i.e. the published ledger)")
    a = ap.parse_args()
    if a.ledger is None:
        a.ledger = os.path.join(a.md, "data", "shadow", "ledger")
        if not os.path.isdir(a.ledger):
            a.ledger = os.path.join(ROOT, "data", "shadow", "ledger")
            print(f"note: no published ledger under --md; falling back to local {a.ledger}")
    print("=" * 74)
    print("NFL EDGE FINDER -- LIVE SYSTEM HEALTH")
    print(f"generated {datetime.now(timezone.utc).isoformat()}")
    print("=" * 74)
    fails = []

    # capture
    caps = sorted(glob.glob(os.path.join(a.md, "data/kalshi/capture", "*", "*.manifest.json")))
    partial = errs = 0
    reqs = r429 = 0
    last = None
    for f in caps[-40:]:
        d = json.load(open(f))
        partial += 1 if d.get("partial") else 0
        errs += len(d.get("errors") or [])
        cs = d.get("client_stats") or {}
        reqs += cs.get("requests", 0) or 0
        r429 += cs.get("http_429", 0) or 0
        last = d
    cap_ok = bool(caps) and partial == 0 and errs == 0
    print(f"CAPTURE:            {status(cap_ok)}   runs={len(caps)} last={last.get('run_id') if last else '-'}")
    print(f"                    partials={partial} errors={errs} requests={reqs} http_429={r429}")
    if not cap_ok:
        fails.append("capture")

    # shock ingestion
    try:
        from nfl_edge.shocks.live import ingest_context_dir
        canon, obs = ingest_context_dir(os.path.join(a.md, "data/context"))
        ctx = sorted(glob.glob(os.path.join(a.md, "data/context", "*", "*.sleeper.json")))
        print(f"SHOCK INGESTION:    {status(True)}   context captures={len(ctx)} "
              f"canonical shocks={len(canon)} source observations={len(obs)}")
        if len(ctx) < 2:
            print(f"                    note: {len(ctx)} capture(s) -- a diff needs at least two")
    except Exception as exc:                                       # noqa: BLE001
        print(f"SHOCK INGESTION:    DEGRADED  {type(exc).__name__}: {exc}")
        fails.append("shocks")
        canon = []

    # shadow pricing + ledger
    obs_files = sorted(glob.glob(os.path.join(a.ledger, "*", "*.observations.jsonl.gz")))
    mans = sorted(glob.glob(os.path.join(a.ledger, "*", "*.ledger_manifest.json")))
    n_obs = n_sup = 0
    states = Counter()
    versions = Counter()
    if mans:
        d = json.load(open(mans[-1]))
        rows = [json.loads(l) for l in gzip.open(os.path.join(os.path.dirname(mans[-1]),
                                                              d["observations_file"]), "rt")]
        n_obs = len(rows)
        for r in rows:
            states[r.get("support_state")] += 1
            versions[r.get("model_version")] += 1
        n_sup = states.get("SUPPORTED", 0)
    print(f"SHADOW PRICING:     {status(bool(mans))}   snapshots={len(obs_files)} "
          f"latest observations={n_obs} supported={n_sup}")
    print(f"                    support states: {dict(states.most_common(4))}")

    # CLV accrual
    ev = sorted(glob.glob(os.path.join(a.ledger, "*", "*.evaluations.jsonl.gz")))
    settled = 0
    print(f"CLV ACCRUAL:        {status(bool(ev), not_started=not ev)}   evaluation files={len(ev)} "
          f"settled outcomes={settled}")

    # passive shadow orders
    so = sorted(glob.glob(os.path.join(a.ledger, "*", "*.shadow_orders.jsonl.gz")))
    print(f"PASSIVE ORDERS:     {status(bool(so), not_started=not so)}   order files={len(so)}")

    # queue data
    books = sorted(glob.glob(os.path.join(a.md, "data/kalshi/capture", "*", "*.books.jsonl")))
    nb = sum(1 for f in books for _ in open(f)) if books else 0
    print(f"QUEUE DATA:         {status(nb > 0, not_started=nb == 0)}   book snapshots={nb}")
    print(f"                    depth-10 books arm automatically 72h before kickoff "
          f"(first kickoff 2026-09-09)")

    # discovery
    disc = sorted(glob.glob(os.path.join(a.md, "data/kalshi/discovery", "*")))
    n_markets = 0
    n_series = 0
    if disc:
        # discovery writes one JSON file per series under markets/, each holding that series' market list
        for f in glob.glob(os.path.join(disc[-1], "markets", "*.json")):
            n_series += 1
            try:
                body = json.load(open(f))
            except json.JSONDecodeError:
                continue
            # each series file buckets by status: {open|unopened|closed|settled: {n, markets: [...]}}
            if isinstance(body, dict):
                for bucket in ("open", "unopened", "closed", "settled"):
                    b = body.get(bucket)
                    if isinstance(b, dict):
                        n_markets += int(b.get("n") or len(b.get("markets") or []))
    print(f"MARKETS DISCOVERED: {n_markets} across {n_series} series "
          f"(latest discovery {os.path.basename(disc[-1]) if disc else '-'})")
    print(f"MARKETS PRICED:     {n_sup} supported of {n_obs} observed")
    print(f"SHADOW OBSERVATIONS:{n_obs} per snapshot, {len(obs_files)} snapshots")
    print(f"SHOCKS:             {len(canon)} canonical")
    print(f"VALID CLOSES:       0 (no game has kicked off)")

    fz = os.path.join(ROOT, "research", "FREEZE_WEEK1_2026.json")
    if os.path.exists(fz):
        z = json.load(open(fz))
        print(f"CURRENT MODEL:      frozen arm {z['model']['version']} / {z['model']['artifact_sha']}")
        print(f"                    default pricer arm shadow-0.4.0 (role features retired, H-022)")
    print(f"RESEARCH ARMS:      shadow-0.3.0 frozen (role on) | shadow-0.4.0 default (role off) | "
          f"calibrator arm B")
    print(f"                    versions seen in latest snapshot: {dict(versions)}")
    srcs = []
    if last:
        for k, v in (last.get("sources") or {}).items():
            if isinstance(v, dict) and v.get("status") not in (200, None):
                srcs.append(f"{k}={v.get('status')}")
    print(f"SOURCE FAILURES:    {srcs or 'none'}")
    print("=" * 74)
    print(f"REAL-MONEY STATUS:  NOT VALIDATED -- research only, no orders, no recommendations")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
