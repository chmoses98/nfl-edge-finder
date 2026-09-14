#!/usr/bin/env python3
"""How many Airtable requests can scheduled polling possibly spend in a month? Computed, never estimated.

    python3 scripts/handicap/preflight_budget.py --market-data ../fees --season 2026

The Free Airtable plan allows 1,000 Web API requests per workspace per calendar month, and this leg must
leave most of that for the work that matters: terminal status writes, `Preflight Result`, `Approved
Payload`, ChatGPT's own request creation and result reads, the archival bridge, retries and tests. So
scheduled polling is capped at `MAX_MONTHLY_SCHEDULED_READS`, and the cap is enforced by a test rather than
promised by a comment.

THE SAME WINDOW FUNCTION AS THE RUNTIME GATE. This imports `preflight_window.windows`; it does not carry its
own copy of the arithmetic. A simulator that agreed with a comment instead of with the code would certify
a budget nobody is actually held to.

WHAT "MAXIMUM" MEANS. Every cron wake inside a merged window is counted as one Airtable GET -- the worst
case, where every single poll finds nothing and spends a request discovering it. A wake outside every window
is counted as zero, because the gate returns before any client is built. That the no-work poll really does
cost ONE request and not two is a separate claim, proved against the worker in
tests/test_preflight_schedule_gate.py rather than assumed here.
"""
import argparse
import os
import sys
from collections import Counter
from datetime import timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from nfl_edge.data import nfl_calendar as CAL          # noqa: E402
from nfl_edge.handicap import preflight_window as PW   # noqa: E402

# The cron cadence, as minutes-past-the-hour. Ten minutes, offset off :00 because the top of the hour is
# when every cron on GitHub fires at once and that queue is where scheduler lag comes from.
CRON_MINUTES = (7, 17, 27, 37, 47, 57)

# THE CEILING. 1,000/month on Free, minus at least 350 reserved for real work. Raising this number must be a
# deliberate, reviewed code change -- which is exactly why it is a constant here and asserted in CI.
MAX_MONTHLY_SCHEDULED_READS = 650
FREE_PLAN_MONTHLY_REQUESTS = 1000


def simulate(games: list, *, cron_minutes=CRON_MINUTES, **window_kw) -> dict:
    """Walk every cron slot the season spans and count how many land inside a polling window."""
    spans = PW.windows(games, **window_kw)
    if not spans:
        return {"months": {}, "worst_month": None, "worst_reads": 0, "windows": 0}

    lo = min(s for s, _ in spans).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    hi = max(e for _, e in spans) + timedelta(days=1)

    wakes, active = Counter(), Counter()
    # Walk hour by hour and test only the cron minutes; a minute-by-minute loop over a five-month season is
    # 200k iterations of nothing.
    t = lo
    idx, n = 0, len(spans)
    while t <= hi:
        month = f"{t.year}-{t.month:02d}"
        for minute in cron_minutes:
            slot = t.replace(minute=minute)
            wakes[month] += 1
            while idx < n and spans[idx][1] < slot:
                idx += 1
            if idx < n and spans[idx][0] <= slot <= spans[idx][1]:
                active[month] += 1
        t += timedelta(hours=1)

    months = {m: {"cron_wakes": wakes[m], "active_wakes": active[m],
                  "max_airtable_reads": active[m],
                  "headroom_to_free_plan": FREE_PLAN_MONTHLY_REQUESTS - active[m]}
              for m in sorted(wakes)}
    worst = max(months, key=lambda m: months[m]["max_airtable_reads"]) if months else None
    return {"months": months, "worst_month": worst,
            "worst_reads": months[worst]["max_airtable_reads"] if worst else 0,
            "windows": len(spans)}


def render(sim: dict) -> str:
    lines = [f"{'month':9} {'cron_wakes':>11} {'active_wakes':>13} {'max_airtable_reads':>19} "
             f"{'headroom_to_1000':>17}"]
    for month, row in sim["months"].items():
        lines.append(f"{month:9} {row['cron_wakes']:>11} {row['active_wakes']:>13} "
                     f"{row['max_airtable_reads']:>19} {row['headroom_to_free_plan']:>17}")
    lines.append("")
    lines.append(f"merged polling windows      : {sim['windows']}")
    lines.append(f"worst calendar month        : {sim['worst_month']}")
    lines.append(f"worst-month scheduled reads : {sim['worst_reads']}")
    lines.append(f"ceiling enforced by CI      : {MAX_MONTHLY_SCHEDULED_READS}")
    lines.append(f"reserved for real work      : "
                 f"{FREE_PLAN_MONTHLY_REQUESTS - MAX_MONTHLY_SCHEDULED_READS} minimum")
    lines.append(f"VERDICT                     : "
                 f"{'WITHIN BUDGET' if sim['worst_reads'] <= MAX_MONTHLY_SCHEDULED_READS else 'OVER BUDGET'}")
    return "\n".join(lines)


def certify(games: list, seasons) -> tuple:
    """Run the budget for each named season and report every month. Returns `(text, worst, ok)`.

    This is what CI runs against the CANONICAL market-data schedule. A synthetic fixture cannot stand in
    for it: the fixture would stay green at 400-something while a real schedule change pushed the actual
    polling windows past the ceiling, which is precisely the failure the ceiling exists to catch.
    """
    blocks, worst_overall, worst_season = [], 0, None
    for season in seasons:
        rows = [g for g in games if g.get("season") == season]
        if not rows:
            blocks.append(f"=== season {season}: NO GAMES IN THE CANONICAL SCHEDULE -- not certified ===")
            continue
        sim = simulate(rows)
        blocks.append(f"=== season {season}  ({len(rows)} games) ===")
        blocks.append(render(sim))
        blocks.append("")
        if sim["worst_reads"] > worst_overall:
            worst_overall, worst_season = sim["worst_reads"], season
    ok = worst_overall <= MAX_MONTHLY_SCHEDULED_READS
    blocks.append(f"WORST MONTH ACROSS ALL CERTIFIED SEASONS : {worst_overall} (season {worst_season})")
    blocks.append(f"CEILING                                  : {MAX_MONTHLY_SCHEDULED_READS}")
    blocks.append(f"HEADROOM TO THE FREE PLAN                : "
                  f"{FREE_PLAN_MONTHLY_REQUESTS - worst_overall}")
    blocks.append(f"RESULT                                   : {'PASS' if ok else 'FAIL'}")
    return "\n".join(blocks), worst_overall, ok


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--schedule", default=None)
    ap.add_argument("--market-data", default=None)
    ap.add_argument("--allow-download", action="store_true")
    ap.add_argument("--season", type=int, default=None, help="restrict to one season's games")
    ap.add_argument("--certify", default=None,
                    help="comma-separated seasons to certify against the ceiling, e.g. 2023,2024,2025,2026")
    a = ap.parse_args(argv)

    games, source = CAL.load_schedule(ROOT, market_data=a.market_data, path=a.schedule,
                                      allow_download=a.allow_download)
    print(f"schedule: {os.path.basename(str(source))}   games: {len(games)}")

    if a.certify:
        seasons = [int(s) for s in a.certify.split(",") if s.strip()]
        text, worst, ok = certify(games, seasons)
        print(text)
        return 0 if ok else 1

    if a.season:
        games = [g for g in games if g.get("season") == a.season]
    sim = simulate(games)
    print(render(sim))
    return 0 if sim["worst_reads"] <= MAX_MONTHLY_SCHEDULED_READS else 1


if __name__ == "__main__":
    raise SystemExit(main())
