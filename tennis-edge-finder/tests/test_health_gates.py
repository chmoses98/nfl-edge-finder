import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from datetime import datetime, timezone, timedelta
from tennis_edge.health import gates as G


def test_leakage_gate():
    t0 = datetime(2026, 9, 9, 18, 30, tzinfo=timezone.utc)
    rows = [{"prediction_id": "a", "match_id": "m", "generated_at_utc": (t0 - timedelta(hours=1)).isoformat()},
            {"prediction_id": "b", "match_id": "m", "generated_at_utc": (t0 + timedelta(minutes=1)).isoformat()}]
    r = G.gate_6_no_post_start_leakage(rows, {"m": (t0, t0)})
    assert r.status == "FAIL" and r.detail["violations"] == ["b"]
    r2 = G.gate_6_no_post_start_leakage(rows[:1], {"m": (None, t0)})
    assert r2.status == "PASS" and r2.detail["start_unknown_used_schedule"] == 1
    # unknown start entirely -> violation (fail closed)
    assert G.gate_6_no_post_start_leakage(rows[:1], {}).status == "FAIL"


def test_unknown_is_not_pass():
    for g in G.run_all():
        assert g.status in ("PASS", "FAIL", "UNKNOWN")
    assert G.gate_11_consistency(None).status == "UNKNOWN"
    assert G.gate_11_consistency([]).status == "PASS"
    assert G.gate_11_consistency(["x"]).status == "FAIL"
