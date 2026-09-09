"""The close is the last COMPLETE quote strictly BEFORE kickoff, or it does not exist.

Every other choice flatters us. A post-kickoff quote already knows part of the result, so CLV measured against
it would show the model anticipating moves it could not have anticipated -- the single most attractive way for
this corpus to become worthless while every number in it still looks plausible.
"""
import json
import os

from nfl_edge.shadow import evaluation as E
from nfl_edge.shadow.quote_history import (
    capture_days, kalshi_yes_payout, load_game_quotes, load_kalshi_settlements, normalise_quote,
)

GAME = "2026_01_NE_SEA"
KICKOFF = "2026-09-10T00:20:00+00:00"
TICKER = "KXNFLGAME-26SEP09NESEA-SEA"


def quote_row(day, hhmm, yes_bid="0.6100", yes_ask="0.6200", ticker=TICKER, game_id=GAME, **kw):
    row = {"run_id": f"{day.replace('-', '')}T{hhmm.replace(':', '')}00Z",
           "observed_at": f"{day}T{hhmm}:00+00:00", "ticker": ticker, "game_id": game_id,
           "event_ticker": "KXNFLGAME-26SEP09NESEA", "series_ticker": "KXNFLGAME",
           "yes_bid_dollars": yes_bid, "yes_ask_dollars": yes_ask, "no_bid_dollars": "0.3800",
           "no_ask_dollars": "0.3900", "last_price_dollars": "0.6200", "volume_fp": "2154461.85",
           "open_interest_fp": "1883286.74", "liquidity_dollars": "0.0000", "status": "active", "result": "",
           "kickoff_utc": KICKOFF}
    row.update(kw)
    return row


def write_capture(root, rows_by_day):
    for day, rows in rows_by_day.items():
        d = os.path.join(root, day)
        os.makedirs(d, exist_ok=True)
        by_run = {}
        for r in rows:
            by_run.setdefault(r["run_id"], []).append(r)
        for run, rs in by_run.items():
            with open(os.path.join(d, f"{run}.quotes.jsonl"), "w") as f:
                for r in rs:
                    # compact, exactly as scripts/kalshi/capture.py writes it
                    f.write(json.dumps(r, separators=(",", ":")) + "\n")


def test_the_close_is_the_last_complete_quote_before_kickoff(tmp_path):
    root = str(tmp_path / "capture")
    write_capture(root, {"2026-09-09": [
        quote_row("2026-09-09", "18:00", "0.5500", "0.5700"),
        quote_row("2026-09-09", "23:50", "0.6100", "0.6200"),     # the close: 30 minutes before kickoff
    ], "2026-09-10": [
        quote_row("2026-09-10", "00:30", "0.8000", "0.8100"),     # in-game, must never be chosen
        quote_row("2026-09-10", "03:59", "0.9900", "1.0000"),
    ]})
    by_ticker, stats = load_game_quotes(root, GAME, [TICKER], kickoff_utc=KICKOFF)
    kickoff_ts = normalise_quote(quote_row("2026-09-10", "00:20"))["observed_ts"]
    close = E.pick_close(by_ticker[TICKER], kickoff_ts)
    assert close["observed_at"] == "2026-09-09T23:50:00+00:00"
    assert close["yes_bid"] == 0.61 and close["mid"] == 0.615
    assert stats["rows_matched"] == 4, "post-kickoff rows are loaded, then refused as a close"


def test_a_game_with_only_post_kickoff_quotes_has_no_close(tmp_path):
    root = str(tmp_path / "capture")
    write_capture(root, {"2026-09-10": [quote_row("2026-09-10", "01:00", "0.8000", "0.8100")]})
    by_ticker, _ = load_game_quotes(root, GAME, [TICKER], kickoff_utc=KICKOFF)
    kickoff_ts = normalise_quote(quote_row("2026-09-10", "00:20"))["observed_ts"]
    assert E.pick_close(by_ticker.get(TICKER, []), kickoff_ts) is None


def test_an_incomplete_quote_is_not_a_close(tmp_path):
    root = str(tmp_path / "capture")
    write_capture(root, {"2026-09-09": [
        quote_row("2026-09-09", "20:00", "0.5500", "0.5700"),
        quote_row("2026-09-09", "23:55", None, "0.6200"),          # one side of the book only
    ]})
    by_ticker, _ = load_game_quotes(root, GAME, [TICKER], kickoff_utc=KICKOFF)
    kickoff_ts = normalise_quote(quote_row("2026-09-10", "00:20"))["observed_ts"]
    close = E.pick_close(by_ticker[TICKER], kickoff_ts)
    assert close["observed_at"] == "2026-09-09T20:00:00+00:00", "half a quote is not a close"


def test_a_stale_close_is_reported_as_stale_and_still_used(tmp_path):
    """The repo's policy is an hour. Beyond it the close is flagged, not silently treated as fresh, and not
    silently discarded either -- both would hide the same fact."""
    root = str(tmp_path / "capture")
    write_capture(root, {"2026-09-08": [quote_row("2026-09-08", "12:00", "0.5000", "0.5200")]})
    by_ticker, _ = load_game_quotes(root, GAME, [TICKER], kickoff_utc=KICKOFF)
    kickoff_ts = normalise_quote(quote_row("2026-09-10", "00:20"))["observed_ts"]
    close = E.pick_close(by_ticker[TICKER], kickoff_ts)
    ev = E.evaluate({"prediction_id": "p", "run_id": "r", "ticker": TICKER, "model_version": "v",
                     "yes_bid": 0.50, "yes_ask": 0.54, "model_contract_value": 0.60,
                     "kickoff_utc": KICKOFF}, close, kickoff_ts=kickoff_ts)
    assert ev.close_status == E.CLOSE_OK_STALE and ev.close_is_stale is True
    assert ev.close_mid == 0.51 and ev.signed_clv_mid is not None
    assert "staleness budget" in ev.notes


def test_a_fresh_close_is_ok_and_its_minutes_to_kickoff_are_positive(tmp_path):
    kickoff_ts = normalise_quote(quote_row("2026-09-10", "00:20"))["observed_ts"]
    close = normalise_quote(quote_row("2026-09-09", "23:50", "0.6100", "0.6200"))
    ev = E.evaluate({"prediction_id": "p", "run_id": "r", "ticker": TICKER, "model_version": "v",
                     "yes_bid": 0.55, "yes_ask": 0.57, "model_contract_value": 0.70,
                     "kickoff_utc": KICKOFF}, close, kickoff_ts=kickoff_ts)
    assert ev.close_status == E.CLOSE_OK and ev.close_is_stale is False
    assert 29.0 < ev.close_minutes_to_kickoff < 31.0
    assert ev.movement == "toward" and ev.signed_clv_mid > 0


def test_missing_close_is_recorded_and_no_clv_is_invented():
    ev = E.evaluate({"prediction_id": "p", "run_id": "r", "ticker": TICKER, "model_version": "v",
                     "yes_bid": 0.55, "yes_ask": 0.57, "model_contract_value": 0.70}, None)
    assert ev.close_status == E.MISSING_CLOSE
    assert ev.close_mid is None and ev.signed_clv_mid is None and ev.signed_clv_executable is None
    assert ev.movement is None


def test_only_the_days_that_could_hold_a_pregame_quote_are_scanned(tmp_path):
    root = str(tmp_path / "capture")
    for day in ("2026-08-01", "2026-09-08", "2026-09-09", "2026-09-10", "2026-09-15"):
        os.makedirs(os.path.join(root, day), exist_ok=True)
    days = [os.path.basename(d) for d in capture_days(root, KICKOFF, days_back=14)]
    assert days == ["2026-09-08", "2026-09-09", "2026-09-10"], (
        "a day after the kickoff day cannot hold a pregame quote, and a day five weeks earlier cannot hold the "
        "LAST one before it")


def test_quotes_are_filtered_by_the_captures_own_game_id(tmp_path):
    """No ticker-naming convention is trusted: a convention that silently stops matching loses quotes."""
    root = str(tmp_path / "capture")
    write_capture(root, {"2026-09-09": [
        quote_row("2026-09-09", "20:00"),
        quote_row("2026-09-09", "20:00", ticker="KXNFLGAME-26SEP13CHICAR-CHI", game_id="2026_01_CHI_CAR"),
    ]})
    by_ticker, _ = load_game_quotes(root, GAME, kickoff_utc=KICKOFF)
    assert list(by_ticker) == [TICKER]


def test_kalshis_own_settlement_is_read_from_post_game_captures_only(tmp_path):
    root = str(tmp_path / "capture")
    write_capture(root, {
        "2026-09-09": [quote_row("2026-09-09", "23:50")],
        "2026-09-10": [quote_row("2026-09-10", "05:00", status="finalized", result="yes")],
    })
    got = load_kalshi_settlements(root, GAME, [TICKER], kickoff_utc=KICKOFF)
    assert got[TICKER]["result"] == "yes" and got[TICKER]["status"] == "finalized"
    assert kalshi_yes_payout(got[TICKER]) == (1.0, "binary")
    assert kalshi_yes_payout({"result": "scalar"}) == (None, "scalar"), (
        "the capture schema carries no scalar value, so none is invented")
    assert load_kalshi_settlements(root, GAME, [TICKER], kickoff_utc=None) == {}
