#!/usr/bin/env python3
"""Capture live Kalshi per-series fee metadata, so the fee engine is traceable rather than remembered.

    python3 scripts/kalshi/capture_fee_metadata.py --out /home/user/_market_data_wt
    python3 scripts/kalshi/capture_fee_metadata.py --check         # compare live vs the committed registry

`config/kalshi_nfl_series.json` records each series' `fee_type` and `fee_multiplier` as the API reported them
WHEN THE REGISTRY WAS BUILT. That is provenance with an expiry date: Kalshi can change a series' fee regime,
and a stale multiplier silently under-charges every net-EV calculation that uses it -- in the direction that
makes trades look better than they are.

This script re-reads those fields from the live API and writes a dated, append-only snapshot to the
market-data branch:

    data/kalshi/fees/<YYYY-MM-DD>.json

and, with `--check`, prints a diff against the committed registry and exits non-zero when they disagree, so
a fee change surfaces as a failed job rather than as a quietly wrong number six weeks later.

It does NOT edit the registry. A fee regime change is a fact that deserves a human look before it silently
alters every historical comparison, so the script reports and the operator commits.

Read-only, public GET endpoints only, consistent with the rest of the Kalshi client: this project has no
order surface and no authorisation for automatic execution.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.kalshi.client import KalshiClient      # noqa: E402

REG_PATH = os.path.join(ROOT, "config", "kalshi_nfl_series.json")
FEE_FIELDS = ("fee_type", "fee_multiplier", "maker_fee_multiplier", "maker_base_fee", "settlement_fee")


def load_registry() -> dict:
    with open(REG_PATH) as f:
        return json.load(f)["series"]


def fetch_series(client, ticker: str) -> tuple[dict | None, str | None]:
    """Fee-relevant fields for one series. Unknown field names are captured too, not filtered out.

    `maker_fee_multiplier` does not exist in the API today -- that is precisely why the maker cost is carried
    as UNKNOWN. Requesting it anyway means the day Kalshi starts publishing it, this snapshot picks it up
    without a code change, and the diff makes it impossible to miss.
    """
    try:
        body = client.series(ticker)
    except Exception as e:                              # noqa: BLE001 -- one bad series is not a failed run
        return None, f"{type(e).__name__}: {str(e)[:200]}"
    s = body.get("series", body) if isinstance(body, dict) else {}
    if not isinstance(s, dict):
        return None, "unexpected response shape"
    out = {k: s.get(k) for k in FEE_FIELDS if k in s}
    # Anything else that mentions a fee: the point of this snapshot is to notice a field we do not yet know
    # to look for.
    out.update({k: v for k, v in s.items() if "fee" in k.lower() and k not in out})
    return out, None


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", help="market-data checkout; the snapshot lands under data/kalshi/fees/")
    ap.add_argument("--check", action="store_true",
                    help="diff live metadata against the committed registry and exit 1 on any difference")
    ap.add_argument("--rps", type=float, default=4.0)
    ap.add_argument("--only-captured", action="store_true", default=True,
                    help="skip NOT_CAPTURED series; they cannot carry a recommendation")
    a = ap.parse_args()

    reg = load_registry()
    tickers = [t for t, r in reg.items()
               if not (a.only_captured and r.get("tier") == "NOT_CAPTURED")]
    client = KalshiClient(rps=a.rps)

    now = datetime.now(timezone.utc)
    snapshot = {"retrieved_at": now.isoformat(), "n_series": len(tickers), "series": {}, "errors": {}}
    diffs = []

    for t in tickers:
        live, err = fetch_series(client, t)
        if err:
            snapshot["errors"][t] = err
            continue
        snapshot["series"][t] = live
        committed = reg.get(t) or {}
        for field in ("fee_type", "fee_multiplier"):
            if field in live and live[field] != committed.get(field):
                diffs.append({"series": t, "field": field,
                              "committed": committed.get(field), "live": live[field]})
        for field in live:
            if field not in ("fee_type", "fee_multiplier") and live[field] is not None:
                diffs.append({"series": t, "field": field, "committed": "<not in registry>",
                              "live": live[field], "note": "a fee field we were not previously capturing"})

    snapshot["differences"] = diffs
    snapshot["client_stats"] = client.stats.to_dict()

    if a.out:
        path = os.path.join(a.out, "data", "kalshi", "fees", f"{now.strftime('%Y-%m-%d')}.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(snapshot, f, indent=1, sort_keys=True)
            f.write("\n")
        print(f"wrote {path}")

    print(f"{len(snapshot['series'])}/{len(tickers)} series read, {len(snapshot['errors'])} errors, "
          f"{len(diffs)} difference(s) against the committed registry")
    for d in diffs[:40]:
        print(f"  {d['series']}.{d['field']}: committed={d['committed']!r} live={d['live']!r}")
    if len(diffs) > 40:
        print(f"  ... and {len(diffs) - 40} more")

    if a.check and diffs:
        print("\nFEE METADATA HAS CHANGED. config/kalshi_nfl_series.json is stale, so every net-EV number "
              "computed from it is wrong. Review the diff above and commit an updated registry; do NOT "
              "record a real recommendation against a fee regime we know we are no longer modelling.",
              file=sys.stderr)
        return 1
    if a.check and snapshot["errors"]:
        print(f"\n{len(snapshot['errors'])} series could not be read; the check is inconclusive rather than "
              "clean.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
