"""The full per-game MARKET BOARD is the complete executable market universe for that game.

The 2026 week 2 DET @ BUF packet discovered 762 markets for the game. `games/2026_02_DET_BUF.md`
rendered 60 of them: the board sorted by volume and cut at `max_markets`, in the full per-game file as
well as in the compact slate. Both alternate-total rungs at the top of the ladder, every rung of both
team-total ladders and 85 of 92 alternate spreads were absent from the document, with nothing in the
document saying so -- a handicapper reading the game file could not see the ladder they were choosing
an expression from, and had no way to know the ladder continued.

So this file pins the exposure rule:

  * the compact slate summary may show only the most traded, and says so and where the rest is;
  * the full game file renders every listed market that has a real book;
  * the only row allowed to be absent from the full board is a `no_real_market` placeholder, which is
    counted in the document and kept in `packet.json`;
  * the accounting reconciles -- silently omitted is 0 -- and the rows are in ladder order, so the rungs
    of one ladder read together instead of being scattered by volume.
"""
import copy
import json
import os
import re
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.handicap.render import render_game_markdown, render_markdown  # noqa: E402

FIXTURE = os.path.join(ROOT, "tests", "fixtures", "handicap_game_sample.json")

# The four low-volume contracts tonight's report dropped, in the shape the packet carries them. They are
# regression evidence, not thresholds the renderer is allowed to know about: nothing in `render.py` may
# key on these numbers, and the assertions below are about exposure, not about these particular rungs.
EVIDENCE = [
    dict(ticker="KXNFLTOTAL-TESTGAME-69P5", family="TOTAL", period="FULL", stat="total_points",
         threshold=69.5, team=None, player_name=None, volume=12.0, open_interest=8.0),
    dict(ticker="KXNFLTOTAL-TESTGAME-72P5", family="TOTAL", period="FULL", stat="total_points",
         threshold=72.5, team=None, player_name=None, volume=9.0, open_interest=6.0),
    dict(ticker="KXNFLTEAMTOTAL-TESTGAME-BUF30P5", family="TEAM_TOTAL", period="FULL", stat="team_points",
         threshold=30.5, team="BUF", player_name=None, volume=15.0, open_interest=11.0),
    dict(ticker="KXNFLSPREAD-TESTGAME-DET13P5", family="SPREAD", period="FULL", stat="margin",
         threshold=13.5, team="DET", player_name=None, volume=7.0, open_interest=4.0),
]


def _market(**kw):
    m = {"ticker": None, "family": "PLAYER_STAT", "period": "FULL", "stat": "rush_yds", "threshold": None,
         "operator": ">=", "player_name": None, "player_id": None, "team": None,
         "yes_bid": 0.40, "yes_ask": 0.42, "no_bid": 0.58, "no_ask": 0.60, "mid": 0.41, "width": 0.02,
         "volume": 0.0, "open_interest": 0.0, "model_probability": 0.44,
         "disagreement_vs_mid": 0.03, "support_state": "SUPPORTED", "support_reason": None,
         "no_real_market": False, "flags": [], "movement": {"n_observations": 0}}
    m.update(kw)
    return m


@pytest.fixture(scope="module")
def game():
    """A game with more genuine markets than any cap, where the evidence rungs are the least traded."""
    with open(FIXTURE) as f:
        g = copy.deepcopy(json.load(f))
    markets = []
    # 70 heavily traded books, so a volume-ranked cap of 60 cannot reach the evidence rungs below
    for i in range(70):
        markets.append(_market(ticker=f"KXNFLPLAYER-TESTGAME-P{i:02d}", player_name=f"Player {i:02d}",
                               team="BUF" if i % 2 else "DET", threshold=float(20 + i),
                               volume=100000.0 - i, open_interest=90000.0 - i))
    for e in EVIDENCE:
        markets.append(_market(**e))
    # the one kind of row the board may hold back: a 0.00/0.99 placeholder with no volume and no interest
    markets.append(_market(ticker="KXNFLTOTAL-TESTGAME-PLACEHOLDER", family="TOTAL", stat="total_points",
                           threshold=99.0, yes_bid=0.0, yes_ask=0.99, no_bid=0.01, no_ask=1.0, width=0.99,
                           volume=0.0, open_interest=0.0, no_real_market=True,
                           support_state="UNSUPPORTED_MODEL", support_reason="no real market"))
    g["markets"] = markets
    return g


@pytest.fixture(scope="module")
def full_md(game):
    return render_game_markdown(game)


def _board(md):
    """The MARKET BOARD section only -- other sections quote tickers too."""
    after = md.split("### MARKET BOARD", 1)[1]
    return after.split("### SIMULATION LAYER", 1)[0]


def _board_tickers(md):
    return re.findall(r"^\| `([^`]+)`", _board(md), re.M)


def _slate(game, **kw):
    packet = {"schema_version": "1.0.0", "handicap_run_id": "x", "built_at": "2026-09-17T06:00:00+00:00",
              "season": 2026, "week": 2, "packet_sha": "abc", "games": [game],
              "sources": {"ledger": "l.jsonl.gz", "model_version": "shadow-0.4.0", "context_captures": ["c1"],
                          "capture_files_scanned_for_movement": 1, "team_profile_basis": "b",
                          "qb_profile_basis": 2025},
              "real_money_status": "NOT VALIDATED",
              "slate_summary": {"games": 1, "markets_listed_slate": len(game["markets"]),
                                "markets_supported_slate": 1, "markets_discovered_all_weeks": 1,
                                "ledger_support_states": {}, "new_or_changed_injuries": [],
                                "major_skill_injuries_out": [], "weather_concerns": [],
                                "largest_market_moves": [], "largest_model_market_disagreements": [],
                                "highest_liquidity_markets": [], "blocking_data_issues": [],
                                "game_priority_for_handicap": [{"rank": 1, "game_id": game["game_id"],
                                                                "priority_score": 1.0, "reasons": ["x"],
                                                                "kickoff_utc": game["kickoff_utc"]}],
                                "disclaimer": "not a bet ranking"}}
    return render_markdown(packet, **kw)


# ---------------------------------------------------------------- the defect itself

def test_the_compact_slate_may_omit_these_rows_entirely(game):
    """The compact slate is a triage document: it carries no per-game board at all and points at the file."""
    md = _slate(game, compact=True, max_markets_per_game=30)
    assert "### MARKET BOARD" not in md
    for e in EVIDENCE:
        assert e["ticker"] not in md
    assert f"games/{game['game_id']}.md" in md, "the slate must say where the complete board is"


def test_a_capped_slate_board_says_it_is_capped_and_where_the_rest_is(game):
    """The slate document renders a board only when it is not compact, and there it may still truncate."""
    md = _slate(game, compact=False, max_markets_per_game=30)
    tickers = _board_tickers(md)
    assert len(tickers) == 30, "a slate board given a cap is capped"
    board = _board(md)
    assert "most traded" in board
    assert "games/" in board, "a truncated board must say where the complete one is"
    real = sum(1 for m in game["markets"] if not m.get("no_real_market"))
    assert f"{real - 30} held back by this view's cap" in board
    assert "0 silently omitted" in board, "a declared cap is not a silent omission"
    # the low-volume rungs fall outside a volume-ranked cap -- which is why the game file may not cap
    assert not any(e["ticker"] in tickers for e in EVIDENCE)


def test_the_full_game_file_carries_every_low_volume_rung(full_md):
    tickers = _board_tickers(full_md)
    for e in EVIDENCE:
        assert e["ticker"] in tickers, (
            f"{e['ticker']} ({e['family']} {e['threshold']}, volume {e['volume']:.0f}) is a genuine "
            "listed book and is missing from the full game board")


def test_the_full_board_is_not_capped_at_sixty(full_md, game):
    real = [m for m in game["markets"] if not m.get("no_real_market")]
    tickers = _board_tickers(full_md)
    assert len(real) > 60, "the fixture must exceed the old cap for this test to mean anything"
    assert len(tickers) > 60
    assert len(tickers) == len(real)


def test_only_a_no_real_market_row_may_be_absent_from_the_board(full_md, game):
    rendered = set(_board_tickers(full_md))
    listed = {m["ticker"] for m in game["markets"]}
    absent = listed - rendered
    assert absent == {m["ticker"] for m in game["markets"] if m.get("no_real_market")}, (
        "a market is off the executable board for a reason other than being a placeholder book")
    assert absent, "the fixture must carry a placeholder for this test to mean anything"


def test_the_accounting_reconciles_and_reports_no_silent_omission(full_md, game):
    listed = len(game["markets"])
    suppressed = sum(1 for m in game["markets"] if m.get("no_real_market"))
    rendered = len(_board_tickers(full_md))
    line = next(l for l in _board(full_md).splitlines() if "silently omitted" in l)
    assert f"{listed} markets listed" in line
    assert f"{rendered} executable books rendered" in line
    assert f"{suppressed} no-real-market placeholders suppressed" in line
    assert "0 silently omitted" in line
    assert rendered + suppressed == listed
    assert "INVARIANT VIOLATED" not in full_md


def test_the_suppressed_placeholders_are_explained_and_kept_in_the_json(full_md):
    board = _board(full_md)
    assert "no_real_market" in board and "packet.json" in board
    assert "quoting artefact" in board


def test_the_full_board_says_it_is_complete_and_never_says_most_traded(full_md):
    board = _board(full_md)
    assert "complete executable board" in board
    assert "most traded" not in board, (
        "the truncation wording belongs to the compact view only; in the game file it is a false claim")


# ---------------------------------------------------------------- ladder order, not volume order

def test_rows_are_in_ladder_order_so_a_ladder_reads_as_one_block(full_md, game):
    """Every rung of a ladder is contiguous and ascending, rather than scattered by liquidity."""
    rows = _board_tickers(full_md)
    by_ticker = {m["ticker"]: m for m in game["markets"]}
    seen, order = [], []
    for t in rows:
        m = by_ticker[t]
        key = (m.get("family"), m.get("period"), m.get("team"), m.get("player_name"), m.get("stat"))
        if not order or order[-1] != key:
            assert key not in seen, f"ladder {key} is split across the board"
            seen.append(key)
            order.append(key)
    for key in seen:
        rungs = [by_ticker[t]["threshold"] for t in rows
                 if (by_ticker[t].get("family"), by_ticker[t].get("period"), by_ticker[t].get("team"),
                     by_ticker[t].get("player_name"), by_ticker[t].get("stat")) == key
                 and by_ticker[t]["threshold"] is not None]
        assert rungs == sorted(rungs), f"ladder {key} is not in threshold order: {rungs}"


def test_the_full_board_is_byte_stable_between_renders(game):
    assert render_game_markdown(copy.deepcopy(game)) == render_game_markdown(copy.deepcopy(game))


def test_liquidity_stays_visible_as_columns(full_md, game):
    header = next(l for l in _board(full_md).splitlines() if l.startswith("| ticker |"))
    for col in ("width", "vol", "OI"):
        assert f"| {col} |" in header, f"{col} must remain a column: liquidity is information, not a filter"
    least = min((m for m in game["markets"] if not m.get("no_real_market")), key=lambda m: m["volume"])
    row = next(l for l in _board(full_md).splitlines() if l.startswith(f"| `{least['ticker']}`"))
    assert f"| {least['volume']:.0f} |" in row and f"| {least['open_interest']:.0f} |" in row


def test_the_game_file_cannot_be_capped_by_a_caller(game):
    """`max_markets` survives on the signature for compatibility; it may not silently re-break the file."""
    real = [m for m in game["markets"] if not m.get("no_real_market")]
    assert len(_board_tickers(render_game_markdown(game, max_markets=5))) == len(real)


def test_the_shipped_fixture_game_reconciles_too(game):
    """The invariant is a property of the renderer, not of the constructed fixture above."""
    with open(FIXTURE) as f:
        real_game = json.load(f)
    md = render_game_markdown(real_game)
    listed = len(real_game["markets"])
    suppressed = sum(1 for m in real_game["markets"] if m.get("no_real_market"))
    assert len(_board_tickers(md)) == listed - suppressed
    assert "0 silently omitted" in _board(md)
    assert "INVARIANT VIOLATED" not in md
