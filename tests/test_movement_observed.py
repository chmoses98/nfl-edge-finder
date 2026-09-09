"""MOVEMENT reported real numbers, or nothing. It had been reporting nothing, silently, for every ticker.

Two independent defects, both invisible:

1. `load_movement` read `yes_bid` / `yes_ask`. The capture writes `yes_bid_dollars` / `yes_ask_dollars`.
   Every mid was therefore `None`, every series was discarded, and every market's movement block said
   "no captured quote history for this ticker" -- while the packet's own manifest reported 676 capture
   files scanned. A section that is always empty reads as "the market has not moved", which is a claim,
   and it was never true.

2. With that fixed, the first observation of a newly listed contract is an EMPTY book (0.00/0.00) and then
   a placeholder 0.00/0.99 whose midpoint of 0.495 is a quoting convention. Measuring "movement" from
   there produced a +0.77 headline move on an untraded ladder rung -- and it went straight into the
   handicap priority ranking. The disagreement ranking already refuses those books; movement now uses the
   same definition of "a real market".
"""
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.handicap.packet import load_movement, movement_for  # noqa: E402

KICKOFF = datetime(2026, 9, 10, 0, 20, tzinfo=timezone.utc)
NOW = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)
TICKER = "KXNFLGAME-26SEP09NESEA-SEA"


def capture(tmp_path, rows, day="2026-09-08", run="20260908T120000Z"):
    d = tmp_path / "data" / "kalshi" / "capture" / day
    d.mkdir(parents=True, exist_ok=True)
    with open(d / f"{run}.quotes.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return str(tmp_path)


def q(ts, bid, ask, ticker=TICKER):
    return {"ticker": ticker, "observed_at": ts, "yes_bid_dollars": bid, "yes_ask_dollars": ask}


def test_the_capture_field_names_are_the_ones_that_are_read(tmp_path):
    """The regression: dollar-denominated fields must produce a mid."""
    md = capture(tmp_path, [q("2026-09-08T12:00:00+00:00", 0.60, 0.62)])
    series, n_files = load_movement(md, {TICKER})
    assert n_files == 1
    assert series[TICKER] == [("2026-09-08T12:00:00+00:00", 0.61, 0.60, 0.62)]


def test_a_legacy_undollared_row_still_parses():
    """Older capture rows used the bare names. Reading both keeps historical files usable."""
    from nfl_edge.handicap.packet import _f  # noqa: PLC0415
    assert _f("0.6") == 0.6


def test_movement_reports_the_horizons_it_actually_observed(tmp_path):
    md = capture(tmp_path, [
        q("2026-09-07T00:00:00+00:00", 0.60, 0.62),      # T-48h
        q("2026-09-08T00:00:00+00:00", 0.63, 0.65),      # T-24h
        q("2026-09-09T11:00:00+00:00", 0.66, 0.68),      # current
    ])
    series, _ = load_movement(md, {TICKER})
    mv = movement_for(TICKER, series, KICKOFF, NOW)
    assert mv["n_observations"] == 3
    assert mv["horizons"]["T-24h"]["observed"] is True
    assert mv["horizons"]["T-24h"]["move_to_current"] == 0.03
    assert mv["total_move_since_first_capture"] == 0.06
    # A horizon in the future is stated as such, never interpolated.
    assert mv["horizons"]["T-30m"] == {"observed": False, "reason": "horizon not yet reached"}


def test_an_empty_book_is_not_a_price_of_zero(tmp_path):
    md = capture(tmp_path, [
        q("2026-09-06T00:00:00+00:00", 0.0, 0.0),        # contract listed, nobody quoting
        q("2026-09-08T00:00:00+00:00", 0.60, 0.62),
        q("2026-09-09T11:00:00+00:00", 0.63, 0.65),
    ])
    series, _ = load_movement(md, {TICKER})
    mv = movement_for(TICKER, series, KICKOFF, NOW)
    assert mv["n_observations"] == 2
    assert mv["n_excluded_no_real_market"] == 1
    assert mv["total_move_since_first_capture"] == 0.03, "movement measured from an unquoted book"


def test_a_placeholder_000_099_book_is_not_a_price_of_half(tmp_path):
    md = capture(tmp_path, [
        q("2026-09-06T00:00:00+00:00", 0.0, 0.99),       # midpoint 0.495 is a quoting convention
        q("2026-09-08T00:00:00+00:00", 0.75, 0.77),
        q("2026-09-09T11:00:00+00:00", 0.76, 0.78),
    ])
    series, _ = load_movement(md, {TICKER})
    mv = movement_for(TICKER, series, KICKOFF, NOW)
    assert mv["n_observations"] == 2
    assert mv["total_move_since_first_capture"] == 0.01, (
        "a ladder rung that was never quoted would report a +0.27 'move' and top the priority ranking")


def test_a_ticker_with_only_artefact_observations_says_so(tmp_path):
    md = capture(tmp_path, [q("2026-09-06T00:00:00+00:00", 0.0, 0.99)])
    series, _ = load_movement(md, {TICKER})
    mv = movement_for(TICKER, series, KICKOFF, NOW)
    assert mv["n_observations"] == 0
    assert "real market" in mv["note"]


def test_a_ticker_with_no_history_is_distinguished_from_one_with_only_artefacts(tmp_path):
    md = capture(tmp_path, [q("2026-09-06T00:00:00+00:00", 0.5, 0.52, ticker="OTHER")])
    series, _ = load_movement(md, {TICKER})
    mv = movement_for(TICKER, series, KICKOFF, NOW)
    assert mv["n_observations"] == 0
    assert mv["note"] == "no captured quote history for this ticker"


def test_a_horizon_never_captured_is_not_confused_with_one_not_yet_reached(tmp_path):
    md = capture(tmp_path, [q("2026-09-09T11:00:00+00:00", 0.60, 0.62)])
    series, _ = load_movement(md, {TICKER})
    mv = movement_for(TICKER, series, KICKOFF, NOW)
    assert mv["horizons"]["T-24h"]["reason"] == "no capture before this horizon"
    assert mv["horizons"]["T-30m"]["reason"] == "horizon not yet reached"


# --------------------------------------------------------------------------- change-suppressed context

def _ctx(tmp_path, run_id, *, day="2026-09-09", espn=None, sleeper=None, failed=()):
    """One context capture. The real capture writes the manifest ALWAYS and the blobs only on change."""
    import json as _json
    d = tmp_path / "data" / "context" / day
    d.mkdir(parents=True, exist_ok=True)
    _json.dump({"run_id": run_id, "sources": {}, "failed_closed": list(failed)},
               open(d / f"{run_id}.manifest.json", "w"))
    if espn is not None:
        _json.dump({"run_id": run_id, "injuries": espn}, open(d / f"{run_id}.espn_injuries.json", "w"))
    if sleeper is not None:
        _json.dump({"run_id": run_id, "players": sleeper}, open(d / f"{run_id}.sleeper.json", "w"))
    open(d / f"{run_id}.weather.jsonl", "w").close()
    return str(tmp_path)


INJ = [{"team": "Seattle Seahawks", "name": "A Player", "position": "RB", "status": "Out"}]


def test_a_change_suppressed_capture_does_not_blank_the_injury_section(tmp_path):
    """`context_capture.py` writes the ESPN blob only when its content hash changed, and the manifest
    always. Reading only the newest run's own files therefore yielded NO injuries at all, for every game,
    reported as available -- two captures in this project's own history are shaped exactly that way, and a
    packet built at either moment would have said "no injuries" about a slate that had fifteen.
    """
    from nfl_edge.handicap.packet import injury_state, load_context  # noqa: PLC0415
    md = _ctx(tmp_path, "20260909T040000Z", espn=INJ, sleeper={})
    _ctx(tmp_path, "20260909T100000Z")            # identical content -> no blob written
    _ctx(tmp_path, "20260909T110000Z")            # still identical
    runs = load_context(md, 2)
    assert [r["run_id"] for r in runs] == ["20260909T100000Z", "20260909T110000Z"]
    state = injury_state(runs, {"SEA"})
    assert sum(len(v) for v in (state.get("by_team") or {}).values()) == 1, (
        "a suppressed capture blanked the injuries")


def test_the_carried_vintage_is_reported_not_faked(tmp_path):
    """Suppression means 're-confirmed now', so both timestamps are kept: when the content was WRITTEN and
    when it was last CONFIRMED. Nothing is stamped with a time it did not happen."""
    from nfl_edge.handicap.packet import injury_state, load_context  # noqa: PLC0415
    md = _ctx(tmp_path, "20260909T040000Z", espn=INJ, sleeper={})
    _ctx(tmp_path, "20260909T110000Z")
    runs = load_context(md, 2)
    cur = runs[-1]
    assert cur["run_id"] == "20260909T110000Z"
    assert cur["espn_vintage"] == "20260909T040000Z"
    assert cur["espn_carried_forward"] is True
    src = injury_state(runs, {"SEA"})["sources"]
    assert src["espn"]["content_vintage"] == "20260909T040000Z"
    assert src["espn"]["carried_forward_unchanged"] is True


def test_a_capture_that_wrote_its_own_blob_is_not_marked_carried(tmp_path):
    from nfl_edge.handicap.packet import load_context  # noqa: PLC0415
    md = _ctx(tmp_path, "20260909T040000Z", espn=INJ, sleeper={})
    _ctx(tmp_path, "20260909T110000Z", espn=INJ + [
        {"team": "New England Patriots", "name": "B Player", "position": "WR", "status": "Out"}],
        sleeper={})
    runs = load_context(md, 2)
    assert runs[-1]["espn_carried_forward"] is False
    assert runs[-1]["espn_vintage"] == "20260909T110000Z"


def test_a_capture_that_failed_closed_is_visible_in_the_packet(tmp_path):
    from nfl_edge.handicap.packet import injury_state, load_context  # noqa: PLC0415
    md = _ctx(tmp_path, "20260909T040000Z", espn=INJ, sleeper={})
    _ctx(tmp_path, "20260909T110000Z", failed=["espn injuries unavailable"])
    state = injury_state(load_context(md, 2), {"SEA"})
    assert state["sources"]["capture_failed_closed"] == ["espn injuries unavailable"]


def test_no_blob_anywhere_is_still_reported_honestly(tmp_path):
    from nfl_edge.handicap.packet import load_context  # noqa: PLC0415
    md = _ctx(tmp_path, "20260909T110000Z")
    runs = load_context(md, 2)
    assert runs[-1]["espn"] is None
    assert runs[-1]["espn_vintage"] is None
    assert runs[-1]["espn_carried_forward"] is False
