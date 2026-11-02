"""A successful report is NOT automatically current when read days later."""
from datetime import datetime, timedelta, timezone
from nfl_edge.handicap.report_freshness import published_report_status

NOW = datetime(2026, 11, 1, 18, 0, tzinfo=timezone.utc)


def report(built, captured):
    return {"report_status": "SUCCESS", "built_at": built.isoformat(),
            "vintages": {"kalshi_capture": {"queried_at": captured.isoformat(),
                                             "age_at_freeze_min": 5.0,
                                             "gate_age_min": 5.0}}}


def test_read_time_status_rejects_stale_report_even_if_built_as_success():
    m = report(NOW - timedelta(days=5), NOW - timedelta(days=5, minutes=10))
    assert m["report_status"] == "SUCCESS"
    assert m["vintages"]["kalshi_capture"]["gate_age_min"] == 5.0
    status = published_report_status(m, NOW)
    assert status["status"] == "STALE_RESEARCH"
    assert not status["can_use_as_current_research"]
    assert len(status["problems"]) == 2


def test_fresh_report_with_stale_underlying_market_is_rejected():
    status = published_report_status(report(NOW - timedelta(minutes=15),
                                            NOW - timedelta(hours=4)), NOW)
    assert not status["can_use_as_current_research"]
    assert any("Kalshi capture" in problem for problem in status["problems"])


def test_current_report_passes_as_research_only_not_a_quote():
    status = published_report_status(report(NOW - timedelta(minutes=30),
                                            NOW - timedelta(minutes=50)), NOW)
    assert status["status"] == "CURRENT_RESEARCH"
    assert status["can_use_as_current_research"]
    assert "not an executable Kalshi quote" in status["note"]


def test_missing_vintage_is_not_assumed_current():
    m = report(NOW, NOW)
    m["vintages"] = {}
    assert not published_report_status(m, NOW)["can_use_as_current_research"]


def test_future_timestamps_are_not_current():
    status = published_report_status(report(NOW + timedelta(minutes=2), NOW), NOW)
    assert not status["can_use_as_current_research"]


def test_future_or_naive_decision_clock_refused():
    try:
        published_report_status(report(NOW, NOW), NOW.replace(tzinfo=None))
        assert False, "must reject naive clock"
    except ValueError:
        pass
