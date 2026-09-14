"""The Airtable budget is enforced here, not promised in a comment.

The owner's workspace is on the Free Airtable plan: 1,000 Web API requests per calendar month, shared with
everything else this project does. Scheduled preflight polling is capped at 650 of those, reserving at least
350 for the work that actually matters -- terminal status writes, `Preflight Result`, `Approved Payload`,
ChatGPT's own request creation and result reads, the archival bridge, retries and manual fallbacks.

Three things have to hold, and a comment can establish none of them:

  * the simulator and the runtime gate compute windows with the SAME function, so the certified budget is
    the budget the deployed code actually produces;
  * the worst calendar month of a real season stays at or below 650;
  * a scheduled wake OUTSIDE every window costs zero Airtable requests, and an ACTIVE no-work wake costs
    at most ONE -- because 650 "reads" means nothing if each read is secretly two HTTP requests.

The last one is deliberately proved against the worker and the bridge rather than assumed by the simulator.
"""
import ast
import inspect
import os
import sys
from datetime import timedelta

import pytest
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts", "handicap"))

from nfl_edge.handicap import airtable_bridge as AB     # noqa: E402
import preflight_budget as BUDGET                       # noqa: E402
import preflight_airtable as PA                         # noqa: E402

from test_preflight_schedule_gate import game, sched   # noqa: E402

# THE CEILING. Written here as a literal as well as imported, so raising the constant in the simulator
# without a reviewed change to this file fails the build.
CEILING = 650


def _season(rows_per_week=16):
    """A synthetic but realistically shaped season: a Thursday, a full Sunday and a Monday, 18 weeks."""
    rows, day = [], None
    from datetime import date
    start = date(2026, 9, 10)                     # a Thursday
    for week in range(18):
        thu = start + timedelta(weeks=week)
        sun, mon = thu + timedelta(days=3), thu + timedelta(days=4)
        rows.append(game(f"thu{week}", thu.isoformat(), "20:20", week=week + 1))
        for i in range(rows_per_week - 3):
            rows.append(game(f"sun{week}_{i}", sun.isoformat(), "13:00", week=week + 1))
        rows.append(game(f"late{week}", sun.isoformat(), "16:25", week=week + 1))
        rows.append(game(f"snf{week}", sun.isoformat(), "20:20", week=week + 1))
        rows.append(game(f"mnf{week}", mon.isoformat(), "20:15", week=week + 1))
        day = mon
    assert day
    return sched(rows)


# ---- one window function, used by both ---------------------------------------------------------------

def test_the_simulator_and_the_runtime_gate_share_one_window_function():
    """Two copies of this arithmetic would certify a budget the deployed code is not held to."""
    src = inspect.getsource(BUDGET)
    tree = ast.parse(src)
    calls = {n.func.attr for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    assert "windows" in calls, "the simulator must call preflight_window.windows"
    # ...and must not carry its own lead-time arithmetic.
    for banned in ("PRIMARY_LEAD", "SECONDARY_LEAD", "CLOSE_LEAD"):
        assert f"{banned}_MIN =" not in src, f"the simulator redefines {banned}_MIN"


def test_the_cadence_is_ten_minutes():
    assert len(BUDGET.CRON_MINUTES) == 6
    gaps = {b - a for a, b in zip(BUDGET.CRON_MINUTES, BUDGET.CRON_MINUTES[1:])}
    assert gaps == {10}, BUDGET.CRON_MINUTES
    assert 0 not in BUDGET.CRON_MINUTES, "stay off the congested top of the hour"


def test_the_cron_in_the_workflow_matches_the_simulated_cadence():
    wf = yaml.safe_load(open(os.path.join(ROOT, ".github", "workflows", "preflight.yml")))
    crons = [c["cron"] for c in (wf.get("on") or wf.get(True))["schedule"]]
    assert len(crons) == 1
    minutes = tuple(int(m) for m in crons[0].split()[0].split(","))
    assert minutes == tuple(BUDGET.CRON_MINUTES), \
        "the simulated cadence must be the deployed cadence, or the budget certifies nothing"


# ---- the ceiling ---------------------------------------------------------------------------------------

def test_the_ceiling_constant_has_not_been_quietly_raised():
    assert BUDGET.MAX_MONTHLY_SCHEDULED_READS == CEILING
    assert BUDGET.FREE_PLAN_MONTHLY_REQUESTS == 1000
    assert BUDGET.FREE_PLAN_MONTHLY_REQUESTS - BUDGET.MAX_MONTHLY_SCHEDULED_READS >= 350


def test_a_realistically_shaped_season_stays_within_the_ceiling():
    sim = BUDGET.simulate(_season())
    assert sim["months"], "the simulation produced no months"
    for month, row in sim["months"].items():
        assert row["max_airtable_reads"] <= CEILING, (
            f"{month} would spend {row['max_airtable_reads']} scheduled Airtable reads, over the {CEILING} "
            f"ceiling. Widen the cadence or narrow the windows -- do not raise the ceiling.")
    assert sim["worst_reads"] <= CEILING


def test_every_month_is_reported_individually():
    sim = BUDGET.simulate(_season())
    for row in sim["months"].values():
        for key in ("cron_wakes", "active_wakes", "max_airtable_reads", "headroom_to_free_plan"):
            assert key in row
        assert row["active_wakes"] <= row["cron_wakes"]
        assert row["headroom_to_free_plan"] == 1000 - row["max_airtable_reads"]


def test_the_rendered_table_states_the_verdict():
    text = BUDGET.render(BUDGET.simulate(_season()))
    assert "worst calendar month" in text and "WITHIN BUDGET" in text


# ---- the CANONICAL schedule gate ---------------------------------------------------------------------
#
# The synthetic season below is right for shape and mutation testing and WRONG as the acceptance gate: it
# would sit at 400-something forever while a real schedule change pushed the actual polling windows past the
# ceiling. So CI runs the real simulator against the same market-data CSV the production gate reads, and
# these tests pin that wiring so it cannot be quietly dropped.

def _tests_workflow():
    return yaml.safe_load(open(os.path.join(ROOT, ".github", "workflows", "tests.yml")))


def test_ci_fetches_the_same_canonical_schedule_the_production_gate_reads():
    steps = _tests_workflow()["jobs"]["pytest"]["steps"]
    checkout = [s for s in steps
                if str(s.get("uses", "")).startswith("actions/checkout")
                and (s.get("with") or {}).get("ref") == "market-data"]
    assert len(checkout) == 1, "CI must sparse-fetch the canonical schedule from market-data"
    with_ = checkout[0]["with"]
    assert "data/kalshi/capture/schedule_cache.csv" in with_["sparse-checkout"]
    assert with_["sparse-checkout-cone-mode"] is False
    # The same file the runtime gate is pointed at by .github/workflows/preflight.yml.
    pre = yaml.safe_load(open(os.path.join(ROOT, ".github", "workflows", "preflight.yml")))
    gate_checkout = [s for s in pre["jobs"]["schedule_gate"]["steps"]
                     if (s.get("with") or {}).get("ref") == "market-data"]
    assert "data/kalshi/capture/schedule_cache.csv" in gate_checkout[0]["with"]["sparse-checkout"]


def test_ci_runs_the_real_simulator_and_certifies_every_reported_season():
    runs = " ".join(s.get("run") or "" for s in _tests_workflow()["jobs"]["pytest"]["steps"])
    assert "scripts/handicap/preflight_budget.py" in runs, "CI must call the production simulator"
    assert "--certify" in runs
    for season in (2023, 2024, 2025, 2026):
        assert str(season) in runs, f"season {season} is reported but not certified"
    # No budget arithmetic in YAML -- the ceiling lives in one place and CI fails on the exit code.
    assert str(CEILING) not in runs, "the ceiling must not be restated in the workflow"


def test_certify_reports_every_month_and_names_the_worst():
    text, worst, ok = BUDGET.certify(_season(), [2026])
    assert ok and worst <= CEILING
    assert "WORST MONTH ACROSS ALL CERTIFIED SEASONS" in text
    assert "RESULT" in text and "PASS" in text
    assert "ceiling enforced by CI" in text


def test_certify_fails_when_a_real_schedule_would_exceed_the_ceiling():
    """THE POINT OF THE CANONICAL GATE: a denser schedule must turn CI red, not pass unnoticed.

    Three clusters every single day is not a plausible NFL season -- it is the shape of the failure the gate
    exists to catch, where a schedule change quietly multiplies the windows.
    """
    from datetime import date                                          # noqa: PLC0415
    rows = []
    for d in range(40):
        day = (date(2026, 9, 1) + timedelta(days=d)).isoformat()
        rows += [game(f"a{d}_{i}", day, "13:00", season=2026) for i in range(3)]
        rows += [game(f"b{d}", day, "17:00", season=2026), game(f"c{d}", day, "20:30", season=2026)]
    text, worst, ok = BUDGET.certify(sched(rows), [2026])
    assert worst > CEILING, f"the dense schedule only reached {worst}"
    assert ok is False and "FAIL" in text


def _dense_csv(tmp_path):
    """A schedule dense enough to blow the ceiling: three clusters every day for forty days."""
    from datetime import date                                          # noqa: PLC0415
    from test_preflight_schedule_gate import CSV_HEAD                  # noqa: PLC0415
    rows = []
    for d in range(40):
        day = (date(2026, 9, 1) + timedelta(days=d)).isoformat()
        rows += [game(f"a{d}_{i}", day, "13:00", season=2026) for i in range(3)]
        rows += [game(f"b{d}", day, "17:00", season=2026), game(f"c{d}", day, "20:30", season=2026)]
    csv = tmp_path / "dense.csv"
    csv.write_text(CSV_HEAD + "".join(rows))
    return csv


def _run_certify(csv, season="2026"):
    import subprocess                                                  # noqa: PLC0415
    script = os.path.join(ROOT, "scripts", "handicap", "preflight_budget.py")
    return subprocess.run([sys.executable, script, "--schedule", str(csv), "--certify", season],
                          capture_output=True, text=True)


def test_the_certify_CLI_exits_non_zero_when_the_budget_is_blown(tmp_path):
    """Found by mutation: `certify()` returning ok=False proves nothing if `main()` still exits 0.

    CI fails on the EXIT CODE, so the exit code is what has to be tested -- end to end, through argparse
    and the real schedule loader, exactly as the workflow invokes it.
    """
    r = _run_certify(_dense_csv(tmp_path))
    assert r.returncode == 1, f"a blown budget must fail CI; got exit {r.returncode}"
    assert "FAIL" in r.stdout


def test_the_certify_CLI_exits_zero_within_budget(tmp_path):
    """The control. An exit code that is always 1 would be exactly as useless as one always 0."""
    from test_preflight_schedule_gate import CSV_HEAD                  # noqa: PLC0415
    csv = tmp_path / "ok.csv"
    csv.write_text(CSV_HEAD + game("g1", "2026-09-13", "13:00", season=2026))
    r = _run_certify(csv)
    assert r.returncode == 0, r.stdout
    assert "PASS" in r.stdout


def test_a_season_missing_from_the_schedule_is_reported_not_silently_skipped():
    text, _worst, ok = BUDGET.certify(_season(), [1999])
    assert "NO GAMES IN THE CANONICAL SCHEDULE" in text
    assert ok is True, "an absent season is not a budget failure, but it must be visible"


# ---- the mutation: prove the assertion can actually fail ----------------------------------------------

@pytest.mark.parametrize("kw,label", [
    ({"primary_lead_min": 60 * 14, "secondary_lead_min": 60 * 14}, "14-hour windows"),
    ({"primary_lead_min": 60 * 24, "secondary_lead_min": 60 * 24}, "all-day windows"),
])
def test_widening_the_windows_far_enough_breaks_the_budget(kw, label):
    """A ceiling that cannot fail is not a ceiling. This proves the CI assertion has teeth."""
    sim = BUDGET.simulate(_season(), **kw)
    assert sim["worst_reads"] > CEILING, (
        f"{label} should have blown the {CEILING} budget but produced {sim['worst_reads']}")


def test_a_faster_cadence_also_breaks_the_budget():
    sim = BUDGET.simulate(_season(), cron_minutes=tuple(range(60)))   # every minute
    assert sim["worst_reads"] > CEILING


# ---- what a "read" costs ------------------------------------------------------------------------------

class _CountingClient:
    """Counts Airtable Web API requests the way the real client would: one per list call."""

    def __init__(self, rows=()):
        self.rows, self.requests = list(rows), 0

    def list_by_status(self, status, sport=AB.SPORT_NFL):
        self.requests += 1
        return [r for r in self.rows if r["fields"].get(AB.F_STATUS) == status]

    def write_fields(self, updates, **kw):      # pragma: no cover - not reached with zero rows
        self.requests += 1


def test_an_active_no_work_poll_costs_exactly_one_airtable_request():
    """650 'reads' would be a lie if each cost two HTTP requests. It costs one."""
    client = _CountingClient([])
    assert PA.run(client, ledger_root=ROOT, signing_key=b"k") == 0
    assert client.requests == 1, f"an ACTIVE no-work poll made {client.requests} Airtable requests"


def test_the_server_side_filter_still_carries_both_canonical_terms():
    """One request stays one request because AIRTABLE does the filtering, not us.

    Checked against the URL the client actually builds rather than against its source text -- an earlier
    version of this test looked for the field VALUES ("Sport", "Status") in source that legitimately spells
    them as constants, which proved nothing either way.
    """
    seen = {}

    class _Resp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return b'{"records": []}'

    def opener(req, timeout=None):
        seen["url"] = req.full_url
        return _Resp()

    client = AB.AirtableClient("tok", opener=opener)
    assert client.list_by_status(AB.STATUS_PREFLIGHT_REQUESTED, sport=AB.SPORT_NFL) == []
    url = seen["url"]
    assert "filterByFormula" in url
    from urllib.parse import parse_qs, unquote, urlparse                # noqa: PLC0415
    formula = parse_qs(urlparse(url).query)["filterByFormula"][0]
    assert AB.F_SPORT in unquote(formula) and AB.F_STATUS in unquote(formula), formula
    assert AB.SPORT_NFL in formula and AB.STATUS_PREFLIGHT_REQUESTED in formula


def test_an_outside_window_wake_costs_zero_airtable_requests():
    """The gate returns before any client exists -- it has no token and imports no bridge."""
    gate_src = open(os.path.join(ROOT, "scripts", "handicap", "preflight_window_gate.py")).read()
    tree = ast.parse(gate_src)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".")[-1])
            imported.update(a.name for a in node.names)
        elif isinstance(node, ast.Import):
            imported.update(a.name.split(".")[-1] for a in node.names)
    assert "airtable_bridge" not in imported and "AB" not in imported, \
        "the gate imports the Airtable bridge; an inactive wake could then spend a request"
    assert "preflight_window" in imported or "PW" in imported
