"""The per-game file is the REAL report, rendered by the canonical renderer — not a simplified stand-in.

`games/<game_id>.md` is what a handicapper actually reads, and the temptation when automating report
delivery is to emit a tidy summary instead. A tidy summary is a different document: it drops the
unsupported markets (so a missing model looks like a missing market), drops movement (so "no move" and
"never captured" become the same thing), and drops the label that stops a disagreement being read as an
edge.

So this file pins the sections and the language against a real slate's game, rendered through
`render_game_markdown` — the same function `run_nfl.py` calls.
"""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.handicap.render import render_game_markdown, render_markdown  # noqa: E402

FIXTURE = os.path.join(ROOT, "tests", "fixtures", "handicap_game_sample.json")


@pytest.fixture(scope="module")
def game():
    with open(FIXTURE) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def md(game):
    return render_game_markdown(game)


REQUIRED_SECTIONS = [
    "MARKET-IMPLIED vs MODEL",
    "INJURIES / AVAILABILITY",
    "WEATHER",
    "QUARTERBACKS",
    "OFFENSIVE LINE",
    "TEAM STRENGTH",
    "MATCHUP ADVANTAGES",
    "DEPTH CHART / EXPECTED ROLES",
    "PLAYER PROJECTIONS vs MARKET",
    "MARKET BOARD",
    "LARGEST MODEL/MARKET DISAGREEMENTS",
    "MOVEMENT",
    "UNSUPPORTED MARKETS",
    "BEST EXPRESSIONS",
    "CORRELATION GROUPS",
    "KEY QUESTIONS FOR THE HANDICAPPER",
]


@pytest.mark.parametrize("section", REQUIRED_SECTIONS)
def test_the_game_file_carries_every_section_the_packet_supports(md, section):
    assert f"### {section}" in md or section in md


def test_the_header_facts_are_present(md):
    for token in ("kickoff:", "venue:", "state **", "markets:", "Data health"):
        assert token in md, token


def test_market_and_model_views_are_shown_side_by_side(md):
    for row in ("spread (home)", "total", "score", "win prob"):
        assert row in md
    assert "market (research-implied)" in md and "| model |" in md
    assert "Period market-implied" in md, "period markets are missing"


def test_the_board_shows_executable_prices_not_only_midpoints(md):
    assert "YES bid/ask" in md and "NO bid/ask" in md


def test_a_disagreement_is_never_relabelled_an_edge(md):
    """The canonical language, verbatim, at the top of the document and over the ranked table."""
    assert md.count("DISAGREEMENT ONLY -- REQUIRES HANDICAP") >= 2
    assert "not an edge" in md
    # The word "edge" must never be used to describe a model/market difference.
    for line in md.split("\n"):
        if "edge" in line.lower() and "not an edge" not in line and "acknowledg" not in line.lower():
            assert "hedge" in line.lower() or "knowledge" in line.lower(), (
                f"a model/market difference is described as an edge: {line!r}")


def test_unsupported_markets_are_shown_with_their_reason(md, game):
    unsupported = [m for m in game["markets"] if m["support_state"] != "SUPPORTED"]
    if not unsupported:
        pytest.skip("the trimmed fixture has no unsupported markets")
    assert "| state | reason | markets | examples |" in md
    assert any(m["support_reason"] in md for m in unsupported), (
        "unsupported markets are listed without the granular reason, so a missing model reads as a "
        "missing market")


def test_movement_names_the_observed_horizons(md):
    assert "### MOVEMENT" in md
    assert "T-24h" in md


def test_the_document_is_a_full_report_not_a_summary(md):
    assert len(md) > 10000, "the game file is suspiciously short for a full report"


def test_the_slate_document_keeps_the_canonical_label_too(game):
    packet = {"schema_version": "1.0.0", "handicap_run_id": "x", "built_at": "2026-09-09T06:00:00+00:00",
              "season": 2026, "week": 1, "packet_sha": "abc", "games": [game],
              "sources": {"ledger": "l.jsonl.gz", "model_version": "shadow-0.4.0",
                          "context_captures": ["c1"], "capture_files_scanned_for_movement": 1,
                          "team_profile_basis": "b", "qb_profile_basis": 2025},
              "real_money_status": "NOT VALIDATED",
              "slate_summary": {"games": 1, "markets_listed_slate": 1, "markets_supported_slate": 1,
                                "markets_discovered_all_weeks": 1, "ledger_support_states": {},
                                "new_or_changed_injuries": [], "major_skill_injuries_out": [],
                                "weather_concerns": [], "largest_market_moves": [],
                                "largest_model_market_disagreements": [
                                    dict(d, game_id=game["game_id"])
                                    for d in game["largest_disagreements"][:3]],
                                "highest_liquidity_markets": [],
                                "blocking_data_issues": [], "game_priority_for_handicap": [
                                    {"rank": 1, "game_id": game["game_id"], "priority_score": 1.0,
                                     "reasons": ["x"], "kickoff_utc": game["kickoff_utc"]}],
                                "disclaimer": "not a bet ranking"}}
    out = render_markdown(packet, compact=True)
    assert "DISAGREEMENT ONLY" in out
    assert "not a bet ranking" in out.lower() or "NOT a bet ranking" in out
