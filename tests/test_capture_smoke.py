"""Offline smoke test of the capture pipeline using a fake client and real fixture markets."""
import json, os, sys, importlib, types
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIX = json.load(open(os.path.join(ROOT, "tests", "fixtures", "kalshi_market_samples.json")))


class FakeClient:
    def __init__(self, **kw):
        self.stats = types.SimpleNamespace(to_dict=lambda: {"requests": 0}, requests=0)
    def markets(self, series_ticker=None, status=None, **kw):
        items = [dict(m, status="active") for m in FIX if m["ticker"].startswith(series_ticker + "-")]
        return items, True, {"pages": 1}
    def try_get(self, path, params=None):
        return {"orderbook_fp": {"yes_dollars": [["0.40", "10"]], "no_dollars": [["0.58", "5"]]}}, None
    def trades(self, **kw):
        return [{"ticker": "KXNFLGAME-26SEP14DENKC-KC", "created_time": "2026-09-04T00:00:00Z", "yes_price_dollars": "0.6", "count_fp": "1"}], True, {}


def test_capture_runs_offline(tmp_path, monkeypatch):
    sys.path.insert(0, ROOT)
    import scripts.kalshi.capture as cap
    monkeypatch.setattr(cap, "KalshiClient", FakeClient)
    monkeypatch.setattr(cap, "OUT_ROOT", str(tmp_path / "capture"))
    monkeypatch.setattr(cap, "load_schedule", lambda p: ({("2026-09-14", "DEN", "KC"): {"kickoff_utc": "2099-09-15T00:15:00+00:00", "game_id": "2026_01_DEN_KC", "season": "2026", "week": "1"}}, "fake"))
    monkeypatch.setattr(sys, "argv", ["capture.py", "--force-daily"])
    rc = cap.main()
    assert rc == 0
    day = next(p for p in (tmp_path / "capture").iterdir() if p.is_dir())
    files = sorted(f.name for f in day.iterdir())
    assert any(f.endswith(".quotes.jsonl") for f in files) and any(f.endswith(".manifest.json") for f in files)
    quotes = [json.loads(l) for f in day.glob("*.quotes.jsonl") for l in open(f)]
    assert quotes and all(q["changed"] for q in quotes)
    kc = [q for q in quotes if q["ticker"] == "KXNFLSPREAD-26SEP14DENKC-KC8"][0]
    assert kc["game_id"] == "2026_01_DEN_KC" and kc["pregame"] is True and kc["team"] == "KC" and kc["floor_strike"] == 7.5
    state = json.load(open(tmp_path / "capture" / "state.json"))
    assert len(state["fingerprints"]) == len(quotes)
    # second run: nothing changed -> no quotes file written, unchanged counted
    monkeypatch.setattr(sys, "argv", ["capture.py"])
    rc = cap.main()
    manifests = sorted(day.glob("*.manifest.json"))
    m2 = json.load(open(manifests[-1]))
    assert m2["quotes_written"] == 0 and m2["quotes_unchanged"] > 0
