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

THREE SOURCES, ALL OF THEM ACTUALLY READ
----------------------------------------
config/kalshi_fee_schedule.json documents a three-source hierarchy: the regulatory Fee Schedule, per-series
metadata, and `GET /series/fee_changes`. A hierarchy whose third source is never ingested is a documented
intention, not a control, so this script reads that endpoint too and preserves each announced change with its
scheduled effective timestamp. Two distinct failures are then detectable rather than merely describable:

    the venue has CHANGED something we already model          -> series metadata diff
    the venue has ANNOUNCED a change we do not yet model      -> fee_changes not covered by any window

The snapshot is append-only and dated, so the freshness of the schedule at any past decision is answerable
from the ledger rather than from memory: nfl_edge/execution/fees.FeeSchedule.verification reads these files
and the pre-trade gate refuses to price real money against a schedule that has gone unchecked.

It does NOT edit the registry or the schedule. A fee regime change is a fact that deserves a human look
before it silently alters every historical comparison, so the script reports and the operator commits a
reviewed NEW effective window; existing windows are never rewritten.

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

from nfl_edge.execution import fees as FEES         # noqa: E402
from nfl_edge.kalshi.client import KalshiClient      # noqa: E402


def _iso(t):
    if not t:
        return None
    dt = datetime.fromisoformat(str(t).replace("Z", "+00:00"))
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def fetch_fee_changes(client) -> dict:
    """`GET /series/fee_changes`, preserved with its scheduled effective timestamps.

    Every field the endpoint returns is kept, not just the ones we know how to read today: the reason this
    source exists is to tell us about a change we have not thought of, and filtering it through today's
    understanding is how such a change gets missed.
    """
    out = {"source": "GET /series/fee_changes", "retrieved_at": datetime.now(timezone.utc).isoformat(),
           "changes": [], "error": None}
    try:
        body = client.series_fee_changes()
    except Exception as e:                              # noqa: BLE001 -- reported, never fatal
        out["error"] = f"{type(e).__name__}: {str(e)[:300]}"
        return out
    if isinstance(body, list):
        raw = body
    elif isinstance(body, dict):
        raw = next((body[k] for k in ("fee_changes", "series_fee_changes", "changes") if body.get(k)), None)
        if raw is None and body and all(isinstance(v, dict) for v in body.values()):
            # A bare object keyed by series ticker. Accepted because the shape of this endpoint is the one
            # thing here we have not been able to confirm against the live API, and refusing an unexpected
            # but unambiguous shape would silently un-ingest the source this exists to ingest.
            raw = [dict(v, series_ticker=k) for k, v in body.items()]
    else:
        raw = None
    if isinstance(raw, dict):
        raw = [dict(v, series_ticker=k) if isinstance(v, dict) else v for k, v in raw.items()]
    for ch in raw or []:
        if isinstance(ch, dict):
            out["changes"].append(ch)
    return out

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
    ap.add_argument("--as-of", default=None,
                    help="evaluate schedule freshness at this ISO timestamp instead of now (diagnostics)")
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

    # ---- the third source: announced, scheduled changes -------------------------------------------
    snapshot["fee_changes"] = fetch_fee_changes(client)
    schedule = FEES.load_fee_schedule(ROOT)
    at = _iso(a.as_of) or now
    snapshot["schedule_verification"] = schedule.verification(
        None, at, FEES.FeeObservations(a.out) if a.out else None)

    # A change is UNMODELLED when the committed schedule carries no window starting at its effective time.
    # That is true whether the change is already live (which blocks real recommendations now) or still in
    # the future (which is a deadline, and is reported as one).
    unmodelled = []
    for ch in snapshot["fee_changes"].get("changes") or []:
        eff = FEES._change_effective(ch)
        if eff is None:
            unmodelled.append(dict(ch, status="UNDATED"))
            continue
        if any(FEES._iso(w.get("effective_from")) == eff for w in schedule.windows):
            continue
        unmodelled.append(dict(ch, status="LIVE" if eff <= at else "SCHEDULED"))
    snapshot["unmodelled_changes"] = unmodelled

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
    if unmodelled:
        print(f"\n{len(unmodelled)} announced fee change(s) are NOT covered by any window in "
              "config/kalshi_fee_schedule.json:")
        for ch in unmodelled[:20]:
            print(f"  [{ch.get('status')}] {ch.get('series_ticker')} effective "
                  f"{FEES._change_effective(ch) or '<undated>'}")
    print(f"schedule verification: {snapshot['schedule_verification']['state']} -- "
          f"{snapshot['schedule_verification'].get('reason')}")

    if a.check and unmodelled:
        print("\nKALSHI HAS ANNOUNCED A FEE CHANGE THIS REPOSITORY DOES NOT MODEL. Add a reviewed window "
              "to config/kalshi_fee_schedule.json with the announced effective_from, and close the current "
              "window's effective_to at the same instant. Do NOT edit the existing window in place: every "
              "past decision must keep being priced with the schedule that was in force when it was made.",
              file=sys.stderr)
        return 1
    if a.check and snapshot["schedule_verification"]["state"] != FEES.VERIFIED:
        print(f"\nFEE SCHEDULE IS {snapshot['schedule_verification']['state']}: "
              f"{snapshot['schedule_verification'].get('reason')}", file=sys.stderr)
        return 1
    if a.check and snapshot["errors"]:
        print(f"\n{len(snapshot['errors'])} series could not be read; the check is inconclusive rather than "
              "clean.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
