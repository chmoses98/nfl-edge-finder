import json, os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pytest
from tennis_edge.ledger.predictions import PredictionLedger, LedgerError

ROW = {"match_id": "m1", "ticker": "KXATPMATCH-26SEP09ZVEVAN-ZVE", "family": "MATCH_WINNER", "model_version": "elo-v0", "git_sha": "abc",
       "feature_snapshot_id": "fs1", "data_source_versions": {"sackmann": "x"}, "models": {"elo": 0.6, "market": 0.62},
       "quality": {"data_quality_score": 0.8}, "scheduled_start": "2026-09-09T18:30:00+00:00", "market_quote": {"yes_bid": 0.6, "yes_ask": 0.63}}


def test_append_only_and_chain():
    with tempfile.TemporaryDirectory() as d:
        L = PredictionLedger(d)
        r1 = L.append(dict(ROW, prediction_id="p1"))
        r2 = L.append(dict(ROW, prediction_id="p2"))
        assert r2["prev_hash"] == r1["row_hash"] and L.verify_chain() == []
        with pytest.raises(LedgerError):
            L.append(dict(ROW, prediction_id="p1"))
        with pytest.raises(LedgerError):
            L.append({"match_id": "x"})
        # tamper -> detected
        fn = [f for f in os.listdir(d) if f.endswith(".jsonl")][0]
        lines = open(os.path.join(d, fn)).read().splitlines()
        row = json.loads(lines[0]); row["models"]["elo"] = 0.9
        lines[0] = json.dumps(row, separators=(",", ":"))
        open(os.path.join(d, fn), "w").write("\n".join(lines) + "\n")
        assert any("modified" in v for v in L.verify_chain())
