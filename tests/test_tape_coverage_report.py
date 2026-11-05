"""tape_coverage_report: legacy tape is 'not measured' (None) when trades/ was not restored, never a silent 0; unanchored markets are counted."""
import json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts", "kalshi"))
import tape_coverage_report as CR      # noqa: E402


def _seed(d, with_legacy):
    os.makedirs(os.path.join(d, "markets")); os.makedirs(os.path.join(d, "horizons"))
    open(os.path.join(d, "markets", "KXNFLGAME.jsonl"), "w").write(
        json.dumps({"ticker": "KXNFLGAME-A", "result": "yes"}) + "\n" + json.dumps({"ticker": "KXNFLGAME-B", "result": "no"}) + "\n")
    json.dump({"tickers": {}, "runs": [], "unanchored": {"KXNFLGAME-B": "no_kickoff_anchor"}}, open(os.path.join(d, "tape_state.json"), "w"))
    if with_legacy:
        os.makedirs(os.path.join(d, "trades", "KXNFLGAME"))
        open(os.path.join(d, "trades", "KXNFLGAME", "KXNFLGAME-A.jsonl"), "w").write("{}\n" * CR.CAP)


def test_legacy_not_measured_without_trades_dir(tmp_path):
    _seed(str(tmp_path), with_legacy=False)
    rep = CR.report(str(tmp_path)); e = rep["series"]["KXNFLGAME"]
    assert e["legacy_tape_files"] is None and e["legacy_tape_capped_at_10000"] is None and rep["totals"]["legacy_measured"] is False
    assert (e["unique_contracts"], e["settled"], e["recovered_tape_no_kickoff_anchor"]) == (2, 2, 1)
    assert "n/m" in CR.md(rep)


def test_legacy_measured_when_trades_dir_present(tmp_path):
    _seed(str(tmp_path), with_legacy=True)
    rep = CR.report(str(tmp_path)); e = rep["series"]["KXNFLGAME"]
    assert (e["legacy_tape_files"], e["legacy_tape_capped_at_10000"]) == (1, 1) and rep["totals"]["legacy_measured"] is True
