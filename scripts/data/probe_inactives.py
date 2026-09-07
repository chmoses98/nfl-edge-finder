#!/usr/bin/env python3
"""Probe candidate sources for an OFFICIAL gameday inactive list, and report what they actually deliver.

    python3 scripts/data/probe_inactives.py                 # upcoming + just-started games
    python3 scripts/data/probe_inactives.py --event 401671789
    python3 scripts/data/probe_inactives.py --json out.json

WHY A PROBE AND NOT A COLLECTOR
-------------------------------
`nfl_edge/settlement/availability.py` reserves an INACTIVE_CONFIRMED state for the official gameday inactive
list -- the 90-minutes-before-kickoff release that turns "Questionable" into a fact. Nothing populates it,
because no free source has been shown to deliver it reliably.

The tempting move is to write a scraper on the strength of a plausible-looking endpoint. That would be worse
than the gap it fills: an availability collector that silently returns nothing, or returns a full roster and
calls everyone active, feeds EXPECTED_ACTIVE into a prop gate that is specifically designed to fail closed on
uncertainty. A broken inactives feed does not degrade to "no information" -- it degrades to "everyone is
playing", which is the one answer that removes the protection.

So this is a PROBE. It reports, with evidence and timestamps, whether a candidate endpoint carries a real
participation signal and WHEN that signal appears relative to kickoff. Promoting a source to a collector is a
separate, deliberate decision that should be made from this probe's output across several game days, not from
one hopeful reading of an API listing.

It also has to run where the collectors run. ESPN and Kalshi are not reachable from every environment; this
probe is written for GitHub Actions, where the rest of the capture stack already talks to these hosts.

WHAT IT CHECKS
--------------
  espn_event_roster    sports.core.api.espn.com .../events/{id}/competitions/{id}/competitors/{team}/roster
                       Carries a per-athlete `active` flag. The question the probe answers is whether that
                       flag is a real gameday inactive designation or merely a roster-status echo -- which is
                       decided by whether it CHANGES in the 90 minutes before kickoff, and by whether the
                       count of inactive players lands in the plausible 5-9 per team range.

  espn_summary         site.api.espn.com .../summary?event={id}
                       Some sports expose an `inactives` block here. Reported if present.

Exit code is 0 whether or not a source works: this is a diagnostic, and "no usable source" is a result.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

UA = "nfl-edge-finder inactives probe (read-only research; github.com/chmoses98/nfl-edge-finder)"
SCOREBOARD = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
CORE = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl"
SUMMARY = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event={eid}"

# An NFL team declares 7 inactives on a normal gameday (5-9 with elevations and short weeks). A source
# reporting 0 or 40 is not reporting inactives, whatever it calls the field.
PLAUSIBLE_INACTIVES = (4, 12)


def get(url, timeout=45):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    t0 = datetime.now(timezone.utc)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
        meta = {"status": r.status if hasattr(r, "status") else 200, "bytes": len(body),
                "retrieved_at": t0.isoformat()}
        try:
            return json.loads(body), meta
        except ValueError:
            meta["error"] = "response was not JSON"
            return None, meta
    except urllib.error.HTTPError as e:
        return None, {"status": e.code, "error": str(e)[:200], "retrieved_at": t0.isoformat()}
    except Exception as e:                                   # noqa: BLE001 -- a probe never raises
        return None, {"status": None, "error": f"{type(e).__name__}: {str(e)[:200]}",
                      "retrieved_at": t0.isoformat()}


def scoreboard_events():
    """Events on the current scoreboard, with kickoff and minutes-to-kickoff."""
    j, meta = get(SCOREBOARD)
    if not j:
        return [], meta
    now = datetime.now(timezone.utc)
    out = []
    for ev in j.get("events", []) or []:
        try:
            ko = datetime.fromisoformat(str(ev.get("date")).replace("Z", "+00:00"))
        except (ValueError, TypeError):
            ko = None
        comp = (ev.get("competitions") or [{}])[0]
        out.append({
            "event_id": ev.get("id"),
            "name": ev.get("shortName"),
            "kickoff_utc": ko.isoformat() if ko else None,
            "minutes_to_kickoff": (round((ko - now).total_seconds() / 60.0, 1) if ko else None),
            "team_ids": [c.get("id") for c in (comp.get("competitors") or [])],
        })
    return out, meta


def probe_event_roster(event_id, team_id):
    """Does the per-event roster carry a usable inactive signal?

    The `active` flag alone proves nothing -- it may be a roster status that says the same thing all week.
    What makes it evidence is the COUNT: a team that lists 7 inactives out of a 53-man roster is reporting a
    gameday declaration, and a team that lists 0 is reporting something else.
    """
    url = f"{CORE}/events/{event_id}/competitions/{event_id}/competitors/{team_id}/roster"
    j, meta = get(url)
    result = {"source": "espn_event_roster", "url": url, "meta": meta}
    if not j:
        result["usable"] = False
        result["note"] = "endpoint did not return JSON"
        return result

    entries = j.get("entries") or j.get("items") or []
    flags = [e for e in entries if isinstance(e, dict) and "active" in e]
    inactive = [e for e in flags if e.get("active") is False]
    result.update({
        "n_entries": len(entries),
        "n_with_active_flag": len(flags),
        "n_inactive": len(inactive),
        "did_not_play_field_present": any("didNotPlay" in e for e in entries if isinstance(e, dict)),
    })
    lo, hi = PLAUSIBLE_INACTIVES
    result["usable"] = bool(flags) and lo <= len(inactive) <= hi
    result["note"] = (
        f"{len(inactive)} of {len(flags)} flagged inactive"
        + ("" if result["usable"] else
           f" -- outside the plausible {lo}-{hi} range for a gameday declaration, so this flag is probably "
           "a roster status rather than the inactive list"))
    return result


def probe_summary(event_id):
    url = SUMMARY.format(eid=event_id)
    j, meta = get(url)
    result = {"source": "espn_summary", "url": url, "meta": meta}
    if not j:
        result["usable"] = False
        return result
    block = j.get("inactives")
    result["inactives_block_present"] = block is not None
    if isinstance(block, list):
        counts = [len(t.get("athletes") or []) for t in block if isinstance(t, dict)]
        result["per_team_counts"] = counts
        lo, hi = PLAUSIBLE_INACTIVES
        result["usable"] = bool(counts) and all(lo <= c <= hi for c in counts)
        result["note"] = f"summary carries an inactives block with per-team counts {counts}"
    else:
        result["usable"] = False
        result["note"] = "no `inactives` block on this summary payload"
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--event", action="append", default=[],
                    help="probe a specific ESPN event id (repeatable)")
    ap.add_argument("--window-minutes", type=float, default=240.0,
                    help="probe scoreboard games within this many minutes of kickoff. Inactives drop at "
                         "T-90m, so a window that only looks earlier will always report 'no source'.")
    ap.add_argument("--json", help="write the full report here")
    a = ap.parse_args()

    report = {"probed_at": datetime.now(timezone.utc).isoformat(), "events": [], "conclusion": None}

    if a.event:
        events = [{"event_id": e, "name": e, "kickoff_utc": None, "minutes_to_kickoff": None,
                   "team_ids": []} for e in a.event]
        report["scoreboard"] = {"skipped": "explicit --event ids supplied"}
    else:
        events, meta = scoreboard_events()
        report["scoreboard"] = meta
        events = [e for e in events
                  if e["minutes_to_kickoff"] is not None
                  and -180 <= e["minutes_to_kickoff"] <= a.window_minutes]

    for ev in events:
        row = dict(ev, probes=[])
        row["probes"].append(probe_summary(ev["event_id"]))
        for team_id in (ev.get("team_ids") or []):
            row["probes"].append(probe_event_roster(ev["event_id"], team_id))
        report["events"].append(row)

    usable = [p for e in report["events"] for p in e["probes"] if p.get("usable")]
    if not report["events"]:
        report["conclusion"] = (
            "NO GAMES IN WINDOW. Inactives are released at T-90m, so this probe only produces evidence when "
            "run close to kickoff. Schedule it for Sunday 16:30-17:30 UTC to catch the 1pm ET slate.")
    elif usable:
        report["conclusion"] = (
            f"CANDIDATE FOUND: {len(usable)} probe(s) returned a plausible gameday inactive count. Do NOT "
            "promote to a collector on one observation -- confirm the signal appears only after T-90m and "
            "holds across several game days first.")
    else:
        report["conclusion"] = (
            "NO USABLE OFFICIAL INACTIVE SOURCE. Availability stays at its existing states and "
            "INACTIVE_CONFIRMED remains unpopulated. This is the honest outcome: the prop gates already fail "
            "closed on unresolved availability near kickoff, so the missing feed costs coverage, not safety.")

    text = json.dumps(report, indent=1)
    if a.json:
        os.makedirs(os.path.dirname(a.json) or ".", exist_ok=True)
        with open(a.json, "w") as f:
            f.write(text + "\n")
        print(f"wrote {a.json}")
    print(report["conclusion"])
    for e in report["events"]:
        for p in e["probes"]:
            print(f"  {e['name']:>12s}  {p['source']:<20s} usable={p.get('usable')}  {p.get('note', '')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
