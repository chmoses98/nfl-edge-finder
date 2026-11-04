#!/usr/bin/env python3
"""Fetch the shadow-ledger observation files that cover the owner's fills, keeping only the wagered tickers (small JSON out).

    python3 scripts/research/fetch_shadow_obs.py --handicap-root /tmp/hd --out /tmp/shadow_obs

For each imported wager the latest ledger run at or before the fill (and no more than 6 hours older) is downloaded from the `market-data`
branch with the GitHub CLI (`gh api`), filtered to the wagered tickers, and written to --out. READ-ONLY on GitHub; nothing is published.
The shadow ledger is the SHADOW model's record, not the owner's: see nfl_edge/research/wager_loss_structure.py.
"""
from __future__ import annotations

import argparse
import gzip
import io
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.handicap import store  # noqa: E402

REPO = "chmoses98/nfl-edge-finder"


def gh_json(path: str):
    out = subprocess.run(["gh", "api", f"repos/{REPO}/contents/{path}?ref=market-data"], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--handicap-root", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--season", type=int, default=2026)
    a = ap.parse_args(argv)
    wagers = store.read_kind(a.handicap_root, "imported_wagers", season=a.season)
    tickers = {w["market_ticker"] for w in wagers if w.get("market_ticker")}
    runs = []
    for day in gh_json("data/shadow/ledger"):
        for f in gh_json(f"data/shadow/ledger/{day['name']}"):
            m = re.match(r"(\d{8}T\d{6}Z)\..*observations\.jsonl\.gz$", f["name"])
            if m:
                runs.append((datetime.strptime(m.group(1), "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc), f"{day['name']}/{f['name']}"))
    runs.sort()
    need = set()
    for w in wagers:
        try:
            t = datetime.strptime(w["executed_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        except (KeyError, ValueError):
            continue
        prior = [r for r in runs if r[0] <= t]
        if prior and (t - prior[-1][0]).total_seconds() < 6 * 3600:
            need.add(prior[-1][1])
    os.makedirs(a.out, exist_ok=True)
    for rel in sorted(need):
        dest = os.path.join(a.out, rel.replace("/", "_") + ".json")
        if os.path.exists(dest):
            continue
        raw = subprocess.run(["gh", "api", "-H", "Accept: application/vnd.github.raw", f"repos/{REPO}/contents/data/shadow/ledger/{rel}?ref=market-data"],
                             capture_output=True, check=True).stdout
        keep = [r for r in (json.loads(x) for x in gzip.open(io.BytesIO(raw), "rt")) if r.get("ticker") in tickers]
        with open(dest, "w", encoding="utf-8") as h:
            json.dump(keep, h)
    print(f"{len(need)} ledger runs cover {len(wagers)} wagers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
