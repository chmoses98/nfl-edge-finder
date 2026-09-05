"""Shadow orders are paper-only and must fail closed on anything unresolved."""
from datetime import datetime, timedelta, timezone

from nfl_edge.execution.shadow_orders import ShadowOrder, propose_order

NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)


def q(**kw):
    d = {"ticker": "KXNFLGAME-X", "game_id": "g", "yes_bid": 0.40, "yes_ask": 0.46,
         "observed_at": (NOW - timedelta(seconds=30)).isoformat(), "minutes_to_kickoff": 120,
         "support_state": "SUPPORTED"}
    d.update(kw)
    return d


def call(quote, p=0.55, **kw):
    kw.setdefault("model_version", "shadow-0.4.0")
    kw.setdefault("model_artifact_sha", "abc")
    kw.setdefault("expected_artifact_sha", "abc")
    kw.setdefault("hypothesis_id", "H-20260904-023")
    return propose_order(quote, p, now=NOW, **kw)


def test_a_valid_candidate_produces_a_paper_order():
    r = call(q())
    assert r["ok"] and isinstance(r["order"], ShadowOrder)
    assert r["order"].side == "yes" and r["order"].limit_price == 0.41
    assert r["order"].status == "OPEN"
    assert not hasattr(r["order"], "filled")


def test_refuses_after_kickoff():
    assert call(q(minutes_to_kickoff=0))["reason"] == "MARKET_STARTED"
    assert call(q(minutes_to_kickoff=-5))["reason"] == "MARKET_STARTED"


def test_refuses_stale_quotes():
    old = (NOW - timedelta(minutes=30)).isoformat()
    assert call(q(observed_at=old))["reason"] == "STALE_CRITICAL_DATA"


def test_refuses_invalid_timestamp():
    assert call(q(observed_at="not-a-time"))["reason"] == "QUOTE_TIMESTAMP_INVALID"
    assert call(q(observed_at=None))["reason"] == "QUOTE_TIMESTAMP_INVALID"


def test_refuses_incomplete_book():
    assert call(q(yes_bid=None))["reason"] == "ORDER_BOOK_INCOMPLETE"
    assert call(q(yes_bid=0.0, yes_ask=1.0))["reason"] == "ORDER_BOOK_INCOMPLETE"


def test_refuses_unresolved_settlement_semantics():
    assert call(q(support_state="UNSUPPORTED_RULES"))["reason"] == "SETTLEMENT_SEMANTICS_UNRESOLVED"


def test_refuses_unresolved_player_identity():
    assert call(q(player_kalshi_id="uuid", player_resolved=False))["reason"] == "PLAYER_IDENTITY_UNRESOLVED"


def test_refuses_on_model_artifact_mismatch():
    assert call(q(), model_artifact_sha="other")["reason"] == "MODEL_ARTIFACT_MISMATCH"


def test_refuses_when_there_is_no_passive_level():
    r = call(q(yes_bid=0.45, yes_ask=0.46))          # one-cent book: improving would cross
    assert r["ok"] is True and r["order"].level_name == "join_bid"
    tight = call(q(yes_bid=0.50, yes_ask=0.51), p=0.99)
    assert tight["ok"] and tight["order"].level_name == "join_bid"


def test_refuses_when_the_model_has_no_view():
    assert call(q(), p=0.43)["reason"] == "NO_MODEL_VIEW"
    assert call(q(), p=None)["reason"] == "NO_MODEL_VIEW"


def test_queue_ahead_is_recorded_when_a_book_snapshot_exists():
    r = call(q(), book={"size_at_level": {0.41: 250.0}})
    assert r["order"].queue_ahead == 250.0
    assert call(q())["order"].queue_ahead is None, "absent book must leave queue unknown, not zero"
