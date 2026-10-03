"""The research explorer (scripts/research_export.py) on a real slice of the week-4 inputs.

`tests/fixtures/research_export/` is the smallest real slice that exercises every explorer kind: the
2026-10-02 RUN NFL report (manifest, the PIT@CLE analysis shard with selected rows, packet.json with PIT@CLE's
research sections and every other game's team profiles), real handicap-data records, and market-data's
schedule cache (2025-2026), capture quote rows of six PIT@CLE tickers from eight runs, the incumbent scorecard
summary and the actual-wager postmortem (fields the exporters read). The v1 export runs first, exactly as in
the workflow, then the explorer is published beside it.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (ROOT, os.path.join(ROOT, "contract")):
    if p not in sys.path:
        sys.path.insert(0, p)

from edge_finder_contract import ids, packet as P, research as R, sync  # noqa: E402
from scripts import app_export, research_export as RE  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures", "research_export")
NOW = "2026-10-02T00:30:00Z"
GAME = "2026_04_PIT_CLE"

# The audit's capability matrix (scratchpad phase2 audit_nfl.md section 4 and section 10, 2026-10-03).
EXPECTED_CAPABILITIES = {
    "team_profiles": "PARTIAL", "player_profiles": "PARTIAL", "event_research": "PARTIAL",
    "team_metrics": "PARTIAL", "player_metrics": "RESEARCH", "team_game_logs": "PARTIAL",
    "player_game_logs": "RESEARCH", "historical_results": "VERIFIED", "opponents": "VERIFIED",
    "opponent_adjustment": "PARTIAL", "schedule_strength": "UNAVAILABLE", "recent_form_windows": "PARTIAL",
    "usage": "RESEARCH", "lineups": "PARTIAL", "injuries": "VERIFIED", "matchup_metrics": "PARTIAL",
    "projection_distributions": "PARTIAL", "raw_projections": "PARTIAL", "market_prices": "VERIFIED",
    "market_price_history": "VERIFIED", "advanced_stats": "PARTIAL", "situational_splits": "PARTIAL",
    "player_props": "VERIFIED", "team_props": "VERIFIED", "game_markets": "VERIFIED", "play_by_play": "UNAVAILABLE",
    "weather": "VERIFIED", "venue_effects": "UNAVAILABLE", "calibration": "VERIFIED", "historical_accuracy": "VERIFIED",
    "clv": "VERIFIED", "wager_history": "VERIFIED", "rankings": "PARTIAL", "time_series": "PARTIAL",
    "comparisons": "PARTIAL", "search": "VERIFIED",
}


def _publish(root: Path) -> Path:
    assert app_export.main(["--reports-dir", os.path.join(FIX, "report"), "--handicap-root", os.path.join(FIX, "handicap-data"),
                            "--market-data-root", os.path.join(FIX, "market-data"), "--out", str(root), "--now", NOW,
                            "--commit-sha", "deadbeef", "--workflow-run-id", "1"]) == 0
    assert _explore(root) == 0
    return root


def _explore(root: Path) -> int:
    return RE.main(["--reports-dir", os.path.join(FIX, "report"), "--market-data-root", os.path.join(FIX, "market-data"),
                    "--out", str(root)])


@pytest.fixture(scope="module")
def app(tmp_path_factory) -> Path:
    return _publish(tmp_path_factory.mktemp("research") / "app")


def _docs(root):
    return R.load_explorer(root)


def _v1(root, kind):
    return json.loads((root / f"{kind}.json").read_text())["items"]


def test_contract_untouched():
    assert sync.check() == []


# 1. verifies after the v1 export, same run, same generated_at
def test_explorer_verifies_and_describes_the_v1_publication(app):
    assert R.verify_explorer(app) == []
    index, docs = _docs(app)
    man = json.loads((app / "manifest.json").read_text())
    assert index["run_id"] == man["run_id"] and index["base_manifest_run_id"] == man["run_id"]
    assert all(d["run_id"] == man["run_id"] and d["generated_at"] == man["generated_at"] for d in docs.values())
    assert index["counts"]["teams"] == 32 and index["counts"]["market_history"] == 1
    assert index["counts"]["rankings"] > 0 and index["counts"]["series"] > 0 and index["counts"]["players"] > 0


# 2. determinism
def test_two_publishes_are_byte_identical(tmp_path):
    a, b = _publish(tmp_path / "a"), _publish(tmp_path / "b")
    assert R.digest_tree(a) == R.digest_tree(b)


# 3. every v1 event has research, every v1 participant a profile, with the v1 identities
def test_every_v1_event_and_participant_is_covered_with_the_same_ids(app):
    _, docs = _docs(app)
    for ev in _v1(app, "events"):
        er = docs[f"events/{ev['event_id']}.json"]
        assert er["event"] == ev
        for part in ev["participants"]:
            prof = docs[f"teams/{part['participant_id']}.json"]
            assert prof["entity"] == part, "the team profile is the v1 participant object, same prt_ id"
    pid = ids.participant_id("NFL", "PLAYER", "gsis_id", "00-0033537")       # Deshaun Watson (projected)
    assert f"players/{pid}.json" in docs
    market_players = {m["player_id"] for m in _v1(app, "markets") if m.get("player_id")}
    players = {d["entity"]["participant_id"] for d in docs.values() if d["kind"] == "entity_profile" and d["entity_type"] == "PLAYER"}
    assert players & market_players, "player profiles use the same gsis-derived ids as v1 market.player_id"


# 4. capability statuses equal the audit
def test_capability_statuses_match_the_audit(app):
    _, docs = _docs(app)
    got = {c["capability"]: c["status"] for c in docs["capabilities.json"]["items"]}
    assert got == EXPECTED_CAPABILITIES
    for c in docs["capabilities.json"]["items"]:
        if c["status"] in ("PARTIAL", "RESEARCH"):
            assert c["limitations"], c["capability"]
        if c["status"] == "UNAVAILABLE":
            assert c["reasons"] and not c["evidence"], c["capability"]
    assert docs["capabilities.json"]["audit_date"] == "2026-10-03"


# 5. a GAME packet validates and is complete
def test_game_packet_has_markets_evidence_and_nothing_missing(app):
    eid = ids.event_id("NFL", "nflverse_game_id", GAME)
    pk = P.build(app_root=app, scope_kind="GAME", event_id=eid)
    assert pk["quality"]["missing"] == []
    assert pk["markets"] and all(m["event_id"] == eid for m in pk["markets"])
    ev = next(e for e in _v1(app, "events") if e["event_id"] == eid)
    got = {e["entity_id"] for e in pk["evidence"]}
    assert {p["participant_id"] for p in ev["participants"]} <= got
    team_ev = next(e for e in pk["evidence"] if e["entity_id"] == ev["home_participant"])
    assert team_ev["observations"] and any(o["rank"] for o in team_ev["observations"])
    assert P.build(app_root=app, scope_kind="GAME", event_id=eid) == pk


# 6. no secrets
def test_no_secret_shaped_strings(app):
    assert R.no_secret_shaped_strings(app) == []


# 7. RESEARCH stays RESEARCH in profiles, distributions and the packet
def test_research_observations_keep_their_status(app):
    _, docs = _docs(app)
    registry = {m["metric_id"]: m for m in docs["metrics.json"]["items"]}
    research_ids = {mid for mid, m in registry.items() if m["quality"]["status"] == "RESEARCH"}
    assert met_in(research_ids, "sim_passing_yards") and met_in(research_ids, "proj_target_share")
    seen = 0
    for d in docs.values():
        if d["kind"] == "entity_profile":
            for o in d["metrics"] + [o for rows in d["splits"].values() for o in rows]:
                if o["metric_id"] in research_ids:
                    assert o["quality_status"] == "RESEARCH"
                    seen += 1
        if d["kind"] == "event_research":
            assert all(x["quality_status"] == "RESEARCH" for x in d["distributions"])
            assert all(p["research_only"] for p in d["projections"])
    assert seen
    eid = ids.event_id("NFL", "nflverse_game_id", GAME)
    pk = P.build(app_root=app, scope_kind="GAME", event_id=eid, max_chars=10_000_000)
    obs = [o for e in pk["evidence"] for o in e["observations"] if o["metric_id"] in research_ids]
    assert obs and all(o["quality_status"] == "RESEARCH" for o in obs)
    assert set(o["metric_id"] for o in obs) <= set(pk["quality"]["research_only_items"])


def met_in(ids_, slug):
    return f"met_nfl.{slug}" in ids_


# 8. a failing publish leaves the previous tree intact
def test_a_failed_publish_leaves_the_previous_tree(tmp_path, app):
    root = tmp_path / "app"
    shutil.copytree(app, root)
    before = R.digest_tree(root)
    inputs = RE.load_inputs(reports_dir=os.path.join(FIX, "report"), app_root=root,
                            market_data_root=os.path.join(FIX, "market-data"))
    docs = [d for d in RE.build_explorer(inputs, now=NOW) if d["kind"] != "metric_registry"]
    q = R.quality(status="VERIFIED", source="test", generated_at=NOW, production=False)
    with pytest.raises(R.ExplorerError):
        R.publish_explorer(app_root=root, sport="NFL", run_id=inputs["v1"]["manifest"]["run_id"], generated_at=NOW,
                           documents=docs, quality=q)
    assert R.digest_tree(root) == before and R.verify_explorer(root) == []
    # and through the CLI: a broken packet exits 1 and touches nothing
    bad = tmp_path / "report"
    shutil.copytree(os.path.join(FIX, "report"), bad)
    (bad / "packet.json").write_text("{not json")
    assert RE.main(["--reports-dir", str(bad), "--out", str(root)]) == 1
    assert R.digest_tree(root) == before
    assert not list(root.glob(".explorer-staging-*"))


def test_refuses_to_describe_a_failed_v1_export(tmp_path, app):
    root = tmp_path / "app"
    shutil.copytree(app, root)
    health = json.loads((root / "health.json").read_text())
    health["export_failed"] = True
    (root / "health.json").write_text(json.dumps(health))
    before = R.digest_tree(root)
    assert _explore(root) == 1
    assert R.digest_tree(root) == before


def test_budgets_and_links(app):
    limits = {"teams": 150_000, "players": 150_000, "events": 150_000, "market_history": 400_000}
    ex = app / "explorer"
    for sub, cap in limits.items():
        for f in (ex / sub).glob("*.json"):
            assert f.stat().st_size <= cap, f
    assert (ex / "index.json").stat().st_size <= 300_000 and (ex / "search_index.json").stat().st_size <= 300_000
    _, docs = _docs(app)
    eid = ids.event_id("NFL", "nflverse_game_id", GAME)
    er = docs[f"events/{eid}.json"]
    assert er["market_history_path"] == R.market_history_path(eid)
    assert er["matchup"] and er["players"] and er["context"]["injuries"] and er["context"]["weather"]
    for row in er["matchup"]:
        assert row["home"]["metric_id"] == row["away"]["metric_id"] == row["metric_id"]
    # series points link to published events only
    for d in docs.values():
        if d["kind"] == "time_series":
            for pt in d["points"]:
                assert pt["event_id"] and pt["opponent_id"]
                if pt["path"]:
                    assert pt["path"][len("explorer/"):] in docs


def test_market_history_is_compressed_capture_data(app):
    _, docs = _docs(app)
    mh = next(d for d in docs.values() if d["kind"] == "market_history")
    v1_markets = {m["market_id"] for m in _v1(app, "markets")}
    for s in mh["series"]:
        assert s["market_id"] in v1_markets
        ts = [p["captured_at"] for p in s["points"]]
        assert ts == sorted(ts) and all(p["source"].startswith("capture:") for p in s["points"])
    # a repeated fingerprint is a no-op (the capture only writes changes; forward fill)
    paths = sorted(str(p) for p in Path(FIX, "market-data").rglob("*.quotes.jsonl"))
    lines = [ln for p in paths for ln in open(p)]
    ticker = json.loads(lines[0])["ticker"]
    once = RE.collect_quote_history(paths, {ticker})
    twice = RE.collect_quote_history(paths + paths[-1:], {ticker})
    assert once == twice and once[ticker]


def test_the_workflows_run_the_explorer_right_after_the_app_export():
    import yaml

    for name in ("run-nfl.yml", "shadow-price.yml"):
        doc = yaml.safe_load(open(os.path.join(ROOT, ".github", "workflows", name)))
        steps = [s for job in doc["jobs"].values() for s in job["steps"]]
        at = next(i for i, s in enumerate(steps) if s.get("id") == "app_export")
        st = steps[at + 1]
        assert st.get("id") == "research_export" and "scripts/research_export.py" in st["run"]
        assert st.get("continue-on-error") is True and "app_export.outcome == 'success'" in st["if"]
        assert '--out "$RUNNER_TEMP/app_out/app/latest"' in st["run"] and "--market-data-root /tmp/md" in st["run"]
        publish_at = next(i for i, s in enumerate(steps) if "publish_handicap_report.py" in (s.get("run") or ""))
        assert publish_at > at + 1
        fail = next(s for s in steps if "research_export.outcome == 'failure'" in str(s.get("if")))
        assert "exit 1" in fail["run"]


def test_the_explorer_reaches_neither_the_bridge_nor_preflight_and_stays_stdlib_only():
    from nfl_edge.handicap.report_isolation import FORBIDDEN_MODULES, reachable_modules
    from test_ci_dependencies import reachable_third_party

    reached = reachable_modules(ROOT, ["scripts/research_export.py"])
    dotted = {rel[:-3].replace("/", ".") for rel in reached}
    assert not (dotted & (FORBIDDEN_MODULES - {"nfl_edge.handicap.store"})), sorted(dotted & FORBIDDEN_MODULES)
    assert reachable_third_party([os.path.join(ROOT, "scripts", "research_export.py")], precise=True) == {}
