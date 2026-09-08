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


# The DOCUMENTED response shape, first. The array key and the timestamp key are both specific and neither
# was being read before -- so the endpoint was called and its answer discarded, which is worse than not
# calling it, because the registry then looks checked.
#
#   { "series_fee_change_arr": [
#       {"id": "...", "series_ticker": "...", "fee_type": "...",
#        "fee_multiplier": ..., "scheduled_ts": "..."} ] }
FEE_CHANGE_ARRAY_KEYS = ("series_fee_change_arr",          # documented
                         "fee_changes", "series_fee_changes", "changes")   # defensive


def fetch_fee_changes(client, show_historical: bool = True) -> dict:
    """`GET /series/fee_changes?show_historical=true`, preserved with its scheduled effective timestamps.

    Every field the endpoint returns is kept, not just the ones we know how to read today: the reason this
    source exists is to tell us about a change we have not thought of, and filtering it through today's
    understanding is how such a change gets missed.

    `parsed` is the field that matters operationally. A response we could not read is NOT "no changes" --
    it is "we do not know", and `FeeSchedule.verification` refuses to report VERIFIED on that basis.
    """
    out = {"source": "GET /series/fee_changes", "show_historical": bool(show_historical),
           "retrieved_at": datetime.now(timezone.utc).isoformat(),
           "changes": [], "error": None, "parsed": False, "shape": None}
    try:
        body = client.series_fee_changes(show_historical=show_historical)
    except Exception as e:                              # noqa: BLE001 -- reported, never fatal
        out["error"] = f"{type(e).__name__}: {str(e)[:300]}"
        return out

    raw = None
    if isinstance(body, list):
        raw, out["shape"] = body, "bare array"
    elif isinstance(body, dict):
        for key in FEE_CHANGE_ARRAY_KEYS:
            if key in body and isinstance(body[key], list):
                raw, out["shape"] = body[key], key
                break
        if raw is None and body and all(isinstance(v, dict) for v in body.values()):
            # A bare object keyed by series ticker. Kept as a defensive shape only.
            raw = [dict(v, series_ticker=k) for k, v in body.items()]
            out["shape"] = "series-keyed object"

    if raw is None:
        out["error"] = (f"unrecognised /series/fee_changes response shape; top-level keys "
                        f"{sorted(body)[:12] if isinstance(body, dict) else type(body).__name__}. "
                        "Treated as INCONCLUSIVE, never as 'no changes'.")
        return out

    for ch in raw:
        if isinstance(ch, dict):
            out["changes"].append(ch)
    out["parsed"] = True
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

    # Every announced change is classified against the window in force at `at` -- see
    # FeeSchedule.classify_changes. `show_historical=true` means this feed carries changes from years back,
    # and a change that PREDATES the applicable reviewed window was superseded by it: the window is the
    # later, human-checked statement of the same regime. Treating those as permanent blockers made every
    # historical announcement a standing failure, which is noise, and noise is how a real one gets missed.
    #
    # The raw feed is written to the observation untouched either way. Nothing here deletes evidence.
    classified = schedule.classify_changes(snapshot["fee_changes"].get("changes") or [], at)
    for kind, changes in classified.items():
        snapshot[kind] = changes

    # ACTIONABLE = the ones a human has to do something about. Live ones block real recommendations now;
    # upcoming ones need a reviewed future window before their effective time; undated ones cannot be
    # placed in time at all, so they are never assumed harmless. Superseded ones are not here, and that is
    # the fix. The key keeps its name so existing readers of the observation keep working.
    #
    # SCOPED TO SERIES THIS REPOSITORY PRICES, plus exchange-wide announcements that carry no series at
    # all. The feed covers all of Kalshi -- crypto perps, weather, indices -- and a fee change on a series
    # no gate will ever quote cannot make one of our net-EV numbers wrong. The decision gate is already
    # per-series for exactly this reason (`verification(series, ...)`), so a health job that failed
    # exchange-wide would be permanently red for reasons no bet can touch, and a permanently red check is
    # one nobody reads. Everything is still classified and written to the observation; only the FAILURE
    # set is scoped, and adding a series to the registry brings its changes into scope immediately.
    def in_scope(ch):
        t = ch.get("series_ticker")
        return t is None or t in reg

    unmodelled = ([dict(ch, status="LIVE") for ch in classified[FEES.CHANGE_LIVE_UNMODELLED] if in_scope(ch)]
                  + [dict(ch, status="SCHEDULED")
                     for ch in classified[FEES.CHANGE_UPCOMING_UNMODELLED] if in_scope(ch)]
                  + [dict(ch, status="UNDATED") for ch in classified[FEES.CHANGE_UNDATED] if in_scope(ch)])
    snapshot["unmodelled_changes"] = unmodelled
    snapshot["out_of_registry_unmodelled_changes"] = [
        ch for kind in (FEES.CHANGE_LIVE_UNMODELLED, FEES.CHANGE_UPCOMING_UNMODELLED, FEES.CHANGE_UNDATED)
        for ch in classified[kind] if not in_scope(ch)]

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
    window = schedule.window_for(at) or {}
    print(f"\nannounced fee changes against window {window.get('window_id')} "
          f"(effective_from {window.get('effective_from')}), classified at {at.isoformat()}:")
    for kind in (FEES.CHANGE_COVERED, FEES.CHANGE_SUPERSEDED, FEES.CHANGE_LIVE_UNMODELLED,
                 FEES.CHANGE_UPCOMING_UNMODELLED, FEES.CHANGE_UNDATED):
        n = len(classified[kind])
        mine = len([ch for ch in classified[kind] if in_scope(ch)])
        print(f"  {n:4d}  {kind}  ({mine} on series this repository prices)")
    print(f"  {len(snapshot['out_of_registry_unmodelled_changes']):4d}  actionable but OUT OF REGISTRY "
          "(recorded, not failed on)")
    if unmodelled:
        print(f"\n{len(unmodelled)} announced fee change(s) are ACTIONABLE -- in force or upcoming under "
              "the applicable window, and not covered by any window in config/kalshi_fee_schedule.json:")
        for ch in unmodelled[:20]:
            print(f"  [{ch.get('status')}] {ch.get('series_ticker')} effective "
                  f"{FEES._change_effective(ch) or '<undated>'}")
        if len(unmodelled) > 20:
            print(f"  ... and {len(unmodelled) - 20} more")
    fc = snapshot["fee_changes"]
    print(f"fee_changes: {len(fc['changes'])} change(s) via {fc.get('shape')} "
          f"(show_historical={fc.get('show_historical')}, parsed={fc.get('parsed')})"
          + (f" ERROR: {fc['error']}" if fc.get("error") else ""))
    print(f"schedule verification: {snapshot['schedule_verification']['state']} -- "
          f"{snapshot['schedule_verification'].get('reason')}")

    if a.check and not snapshot["fee_changes"].get("parsed"):
        print("\nTHE /series/fee_changes RESPONSE COULD NOT BE READ: "
              f"{snapshot['fee_changes'].get('error')}\n"
              "This is INCONCLUSIVE, not 'no changes announced'. The third source in the fee hierarchy is "
              "the only one that can warn us before a schedule stops being right, so a run that could not "
              "read it does not refresh the schedule's verification and must not pass.", file=sys.stderr)
        return 1
    if a.check and unmodelled:
        live = len(classified[FEES.CHANGE_LIVE_UNMODELLED])
        soon = len(classified[FEES.CHANGE_UPCOMING_UNMODELLED])
        undated = len(classified[FEES.CHANGE_UNDATED])
        print(f"\nKALSHI HAS ANNOUNCED A FEE CHANGE THIS REPOSITORY DOES NOT MODEL: {live} already in "
              f"force under the applicable window, {soon} upcoming, {undated} undated. Add a reviewed "
              "window to config/kalshi_fee_schedule.json with the announced effective_from, and close the "
              "current window's effective_to at the same instant. Do NOT edit the existing window in "
              "place: every past decision must keep being priced with the schedule that was in force when "
              "it was made.\n"
              "A change that predates the applicable window is NOT listed here: a later reviewed window "
              "supersedes it. It stays in the observation as evidence.", file=sys.stderr)
        return 1
    # `schedule_verification` above is deliberately EXCHANGE-WIDE (series=None): it is the raw evidence,
    # and it reads PENDING_CHANGE whenever any Kalshi series anywhere has an unreviewed live change. That
    # question is answered, and scoped, by `unmodelled` above -- so here we fail only on the states that
    # are about the committed schedule itself and cannot be scoped away: no applicable window, or one
    # nobody has confirmed inside the policy window.
    state = snapshot["schedule_verification"]["state"]
    if a.check and state not in (FEES.VERIFIED, FEES.PENDING_CHANGE):
        print(f"\nFEE SCHEDULE IS {state}: {snapshot['schedule_verification'].get('reason')}",
              file=sys.stderr)
        return 1
    if a.check and snapshot["errors"]:
        print(f"\n{len(snapshot['errors'])} series could not be read; the check is inconclusive rather than "
              "clean.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
