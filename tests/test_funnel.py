"""The BET/WATCH/PASS funnel replays the existing gates and changes nothing."""
import os
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from nfl_edge.execution import fees as F                                                       # noqa: E402
from nfl_edge.shadow import funnel as FN                                                        # noqa: E402

SCHEDULE = F.load_fee_schedule(ROOT)
AS_OF = datetime(2026, 9, 12, 17, 0, tzinfo=timezone.utc)


def row(ticker="KXNFLGAME-26SEP13AH-H", family="GAME_WINNER", cv=0.60, yes_bid=0.50, yes_ask=0.52, game_id="G", support="SUPPORTED",
        width=None, volume=100.0, oi=50.0, **kw):
    r = {"ticker": ticker, "family": family, "game_id": game_id, "support_state": support, "support_reason": None,
         "model_contract_value": cv, "yes_bid": yes_bid, "yes_ask": yes_ask, "no_bid": 1 - yes_ask, "no_ask": 1 - yes_bid,
         "quote_width": (yes_ask - yes_bid) if width is None else width, "volume": volume, "open_interest": oi, "quality_flags": [],
         "minutes_to_kickoff": 1000.0}
    r.update(kw)
    return r


def test_every_contract_exits_exactly_once_and_stages_are_monotone():
    rows = [row(), row(ticker="B", game_id=None), row(ticker="C", support="UNSUPPORTED_MODEL"), row(ticker="D", cv=0.40),
            row(ticker="E", width=0.30), row(ticker="F", cv=0.53, yes_ask=0.52, yes_bid=0.50)]
    f = FN.build_funnel(rows, {"KXNFLGAME-26SEP13AH-H": {"book_depth_yes": 500.0, "book_depth_no": 500.0}}, SCHEDULE, as_of=AS_OF)
    assert sum(f["terminal_states"].values()) == len(rows)
    ns = [s["n"] for s in f["stages"]]
    assert ns == sorted(ns, reverse=True) and ns[0] == len(rows)
    assert f["terminal_states"]["BET"] == 1 and f["authority"].startswith("NONE")


def test_bet_and_watch_reconcile_with_the_preflight_net_ev_arithmetic():
    """A BET has net EV > 0 at the ask under the SAME function the gate uses; a WATCH does not, and carries the ceiling."""
    bet = FN.classify(row(), {"book_depth_yes": 500.0, "book_depth_no": 500.0}, SCHEDULE, AS_OF)
    assert bet["state"] == FN.BET
    nev = F.net_executable_ev(bet["fair"], bet["executable_ask"], 1.0, SCHEDULE, series_ticker="KXNFLGAME", as_of=AS_OF)
    assert nev.net_ev_dollars > 0
    watch = FN.classify(row(cv=0.53, yes_ask=0.52, yes_bid=0.50), {"book_depth_yes": 500.0, "book_depth_no": 500.0}, SCHEDULE, AS_OF)
    assert watch["state"] == FN.WATCH and watch["watch_ceiling"] is not None and watch["watch_ceiling"] < watch["executable_ask"]
    nev = F.net_executable_ev(watch["fair"], watch["executable_ask"], 1.0, SCHEDULE, series_ticker="KXNFLGAME", as_of=AS_OF)
    assert nev.net_ev_dollars <= 0
    at_ceiling = F.net_executable_ev(watch["fair"], watch["watch_ceiling"], 1.0, SCHEDULE, series_ticker="KXNFLGAME", as_of=AS_OF)
    assert at_ceiling.net_ev_dollars > 0


def test_the_funnel_takes_the_executable_side_never_the_mid():
    no_side = FN.classify(row(cv=0.30, yes_bid=0.50, yes_ask=0.52), {"book_depth_yes": 1.0, "book_depth_no": 1.0}, SCHEDULE, AS_OF)
    assert no_side["side"] == "NO" and no_side["executable_ask"] == 0.5 and no_side["fair"] == 0.7


def test_an_unobserved_book_fails_closed():
    c = FN.classify(row(), None, SCHEDULE, AS_OF)
    assert c["state"] == FN.PASS and c["stage_reached"] == "executable_price" and "no order book" in c["reasons"][0]


def test_player_availability_rules_are_the_schemas():
    r = row(ticker="KXNFLRECYDS-26SEP13AH-P-50", family="PLAYER_STAT", availability_state="UNKNOWN")
    assert FN.classify(r, {"book_depth_yes": 1.0}, SCHEDULE, AS_OF)["reasons"] == ["availability unknown"]
    r = row(ticker="KXNFLRECYDS-26SEP13AH-P-50", family="PLAYER_STAT", availability_state="QUESTIONABLE", minutes_to_kickoff=60.0)
    assert "unresolved inside T-90m" in FN.classify(r, {"book_depth_yes": 1.0}, SCHEDULE, AS_OF)["reasons"][0]
    r = row(ticker="KXNFLRECYDS-26SEP13AH-P-50", family="PLAYER_STAT", availability_state="EXPECTED_ACTIVE", availability_stale_minutes=1000.0)
    assert "stale" in FN.classify(r, {"book_depth_yes": 1.0}, SCHEDULE, AS_OF)["reasons"][0]


def test_the_funnel_and_the_arms_are_unreachable_from_the_report_and_gate_paths():
    """The recommendation policy is untouched: nothing on the packet/gate side imports the experiment."""
    from nfl_edge.handicap.report_isolation import reachable_modules
    reached = reachable_modules(ROOT)
    assert not any(m.startswith("nfl_edge/arms/") or m.endswith("funnel.py") or m.endswith("player_autopsy.py") for m in reached)
    for name in ("gates.py", "risk.py", "schema.py", "preflight.py", "packet.py"):
        src = open(os.path.join(ROOT, "nfl_edge", "handicap", name)).read()
        assert "nfl_edge.arms" not in src and "funnel" not in src and "player_autopsy" not in src
