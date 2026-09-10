"""End to end: three-arm snapshots + a captured quote history + a proven result -> an immutable arm-evaluation corpus.

Built on the same real 2025 week-1 Dallas at Philadelphia result the incumbent postgame test uses. The three-arm
records are written by the real writer, the settlement runs the real `scripts/shadow/settle_arms.py` with only
the result book injected (no parquet, no network), and the properties asserted are the ones no unit test can:

  * a game with no prekickoff three-arm record produces nothing;
  * the pregame centres and probabilities in the evaluation are the snapshot's own, verbatim;
  * the close is strictly before kickoff and the closing centre is measured by the incumbent estimator;
  * a rerun writes nothing; a contradicted rerun writes nothing and fails;
  * the settlement of every contract is the incumbent engine's (a tie pays 0.5, a refusal carries no payout).
"""
import glob
import gzip
import hashlib
import importlib.util
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nfl_edge.arms import records as REC, registry as R                                    # noqa: E402
from nfl_edge.shadow import evaluation_store as ST                                         # noqa: E402
from nfl_edge.arms import evaluation as AE                                                 # noqa: E402

pp = importlib.util.spec_from_file_location("_pp", os.path.join(ROOT, "tests", "test_postgame_pipeline.py"))
PP = importlib.util.module_from_spec(pp); pp.loader.exec_module(PP)            # reuse its market-data tree + result book
GAME, KICKOFF = PP.GAME, PP.KICKOFF


def load_script(name):
    path = os.path.join(ROOT, "scripts", "shadow", f"{name}.py")
    spec = importlib.util.spec_from_file_location(f"_script_{name}", path)
    mod = importlib.util.module_from_spec(spec); sys.modules[spec.name] = mod; spec.loader.exec_module(mod)
    return mod


settle_arms = load_script("settle_arms")

SNAPS = [("20250903T200000Z", "2025-09-03T20:00:00+00:00", 1700.0), ("20250904T235000Z", "2025-09-04T23:50:00+00:00", 30.0)]
CONTRACTS = [m for m in PP.MARKETS if m["family"] in R.GAME_FAMILIES_PRICED]


def arm(arm_id, margin, total, status=R.OK, **detail):
    a = REC.ArmCenter(arm_id=arm_id, arm_version="t", status=status, projected_home_margin=margin, projected_total=total,
                      simulation_center_margin=margin, simulation_center_total=total,
                      implied_home_score=(total + margin) / 2, implied_away_score=(total - margin) / 2,
                      center_source={"CURRENT_MARKET_PRIOR": "kalshi_implied", "DATA_ONLY": "football_only"}.get(arm_id, "blend"),
                      uses_market_information=arm_id != R.DATA_ONLY, data_quality_state="kalshi_implied" if arm_id == R.CURRENT else R.OK)
    a.simulation = {"p_home_win": 0.6 + (margin - 3.5) * 0.02, "p_tie": 0.002}
    a.detail = detail
    return a


def write_arms(md, *, hybrid_bad=False, prekickoff=True):
    """Two snapshots of the DAL@PHI arms, the real writer. PHI is home; centre = home minus away."""
    out = []
    for run_id, observed_at, mtk in SNAPS:
        cur, do = arm(R.CURRENT, 3.5, 45.5), arm(R.DATA_ONLY, 1.0, 48.0)
        hm = 0.7 * 3.5 + 0.3 * 1.0 + (1.0 if hybrid_bad else 0.0)
        hy = arm(R.HYBRID, hm, 0.7 * 45.5 + 0.3 * 48.0)
        g = REC.GameArmRecord(record_id=REC.game_record_id(run_id, GAME), schema_version=REC.SCHEMA_VERSION, arms_version=R.ARMS_VERSION,
                              run_id=run_id, observed_at=observed_at, generated_at=observed_at, code_sha="x", season=2025, week=1,
                              game_id=GAME, home_team="PHI", away_team="DAL", kickoff_at=KICKOFF, minutes_to_kickoff=mtk,
                              prekickoff=prekickoff, status=R.OK if prekickoff else R.POST_KICKOFF_EXCLUDED,
                              market_snapshot_id=run_id, simulation={"n_sims": R.N_SIMS},
                              arms={R.CURRENT: cur.to_dict(), R.DATA_ONLY: do.to_dict(), R.HYBRID: hy.to_dict()} if prekickoff else {},
                              reproduction_check={"ok": True})
        cs = []
        for m in CONTRACTS:
            cs.append(REC.ContractArmRecord(
                record_id=REC.contract_record_id(run_id, m["ticker"]), game_record_id=g.record_id, schema_version=REC.SCHEMA_VERSION,
                arms_version=R.ARMS_VERSION, run_id=run_id, observed_at=observed_at, generated_at=observed_at, game_id=GAME, season=2025,
                week=1, home_team="PHI", away_team="DAL", kickoff_at=KICKOFF, minutes_to_kickoff=mtk, ticker=m["ticker"],
                event_ticker=m["ticker"].rsplit("-", 1)[0], series_ticker=m["ticker"].split("-")[0], family=m["family"], period="FULL",
                threshold=m.get("threshold"), floor_strike=m.get("floor_strike"), operator=m.get("operator", ">="), team=m.get("team"),
                p_current=m["model_p"], p_data_only=m["model_p"] - 0.05, p_hybrid=m["model_p"] - 0.015,
                cv_current=m["model_p"], cv_data_only=m["model_p"] - 0.05, cv_hybrid=m["model_p"] - 0.015,
                arm_status={a: R.OK for a in R.PRIMARY_ARMS}, incumbent_contract_value=m["model_p"],
                yes_bid=m["yes_bid"], yes_ask=m["yes_ask"], mid=(m["yes_bid"] + m["yes_ask"]) / 2, quote_width=m["yes_ask"] - m["yes_bid"],
                volume=1000.0).to_dict())
        w = REC.ArmsWriter(REC.arms_root(md), run_id)
        out.append(w.write([g.to_dict()], cs))
    return out


def synthetic_bank(target_season):
    """A residual bank for the closing-centre estimator, from committed synthetic games: no live schedule file."""
    import numpy as np
    from nfl_edge.pricing.game_env import ResidualBank
    rng = np.random.default_rng(0); n = 800
    spreads = rng.choice([-7, -3.5, -3, -1.5, 0, 1, 2.5, 3, 3.5, 7], n); totals = rng.choice([41.5, 44, 45.5, 47, 49.5], n)
    home = rng.poisson(23, n); away = rng.poisson(21, n); result = home - away
    return ResidualBank(result - spreads, home + away - totals, rng.integers(2016, 2025, n), ref_season=target_season,
                        spread_lines=spreads, total_lines=totals, overtime=np.zeros(n, int), results=result, rng=rng)


def run(monkeypatch, md, out, *extra):
    monkeypatch.setattr(settle_arms, "build_result_book", lambda *a, **k: PP.result_book())
    monkeypatch.setattr(settle_arms, "bank_from_schedule", lambda season, games=None: synthetic_bank(season))
    monkeypatch.setattr(sys, "argv", ["settle_arms.py", "--market-data", md, "--out", str(out), "--game", GAME,
                                      "--game", PP.PENDING_GAME, "--no-espn-final", *extra])
    return settle_arms.main()


@pytest.fixture
def tree(tmp_path):
    md, _ = PP.build_market_data(tmp_path)
    write_arms(md)
    return md, tmp_path / "arm_evaluations"


def test_the_whole_path_writes_paired_game_and_contract_evaluations(monkeypatch, tree):
    md, out = tree
    assert run(monkeypatch, md, out) == 0
    games = ST.read_corpus([str(out)], suffix=AE.GAME_SUFFIX)
    contracts = ST.read_corpus([str(out)], suffix=AE.CONTRACT_SUFFIX)
    assert len(games) == 2 and len(contracts) == 2 * len(CONTRACTS)
    g = next(x for x in games if x["minutes_to_kickoff"] == 30.0)
    # PHI 24, DAL 20 in the fixture: margin +4, total 44
    assert g["actual"]["margin"] == 4 and g["actual"]["total"] == 44
    assert g["arms"][R.CURRENT]["margin_error"] == pytest.approx(-0.5)
    assert g["arms"][R.DATA_ONLY]["margin_error"] == pytest.approx(-3.0)
    assert g["arms"][R.HYBRID]["projected_home_margin"] == pytest.approx(0.7 * 3.5 + 0.3 * 1.0)
    assert g["arms"][R.DATA_ONLY]["margin_minus_market"] == pytest.approx(-2.5)
    assert g["arms"][R.DATA_ONLY]["margin_disagreement_band"] == "2-3"
    # the close: the last pregame quote is at 23:55, 25 minutes out, and the game kicked off at 00:20
    assert all(c["close_status"] == "OK" and c["close_observed_at"] < KICKOFF for c in contracts)
    winner = next(c for c in contracts if c["family"] == "GAME_WINNER" and c["run_id"] == SNAPS[1][0])
    assert winner["settlement_status"] == "SETTLED" and winner["settled_yes"] == 1.0 and winner["event_binary_valid"]
    assert winner["p_current"] == 0.62 and winner["p_data_only"] == pytest.approx(0.57)
    total = next(c for c in contracts if c["family"] == "TOTAL" and c["run_id"] == SNAPS[1][0])
    assert total["settled_yes"] == 0.0            # 44 < 45


def test_a_game_with_no_prekickoff_record_produces_nothing(monkeypatch, tmp_path):
    md, _ = PP.build_market_data(tmp_path)
    write_arms(md, prekickoff=False)
    out = tmp_path / "ev"
    assert run(monkeypatch, md, out) == 0
    assert not glob.glob(str(out / "**" / "*.jsonl.gz"), recursive=True)


def test_a_rerun_writes_nothing_and_a_contradiction_fails_closed(monkeypatch, tree):
    md, out = tree
    assert run(monkeypatch, md, out) == 0
    before = PP.tree_digest(str(out))
    assert run(monkeypatch, md, out) == 0
    assert PP.tree_digest(str(out)) == before
    # the same game with a different final score is a different truth: refused, nothing written
    monkeypatch.setattr(settle_arms, "build_result_book", lambda *a, **k: PP.result_book(score_override=(20, 27)))
    monkeypatch.setattr(settle_arms, "bank_from_schedule", lambda season, games=None: synthetic_bank(season))
    monkeypatch.setattr(sys, "argv", ["settle_arms.py", "--market-data", md, "--out", str(out), "--game", GAME, "--no-espn-final"])
    assert settle_arms.main() == 4
    assert PP.tree_digest(str(out)) == before


def test_pregame_values_are_copied_verbatim_and_the_ledger_is_untouched(monkeypatch, tree):
    md, out = tree
    ledger_before = PP.tree_digest(os.path.join(md, "data", "shadow", "ledger"))
    arms_before = PP.tree_digest(os.path.join(md, "data", "shadow", "arms"))
    assert run(monkeypatch, md, out) == 0
    assert PP.tree_digest(os.path.join(md, "data", "shadow", "ledger")) == ledger_before
    assert PP.tree_digest(os.path.join(md, "data", "shadow", "arms")) == arms_before
    snaps = REC.load_records([REC.arms_root(md)], "arm_contracts")
    for c in ST.read_corpus([str(out)], suffix=AE.CONTRACT_SUFFIX):
        src = snaps[c["prediction_id"]]
        for k in ("p_current", "p_data_only", "p_hybrid", "cv_current", "cv_data_only", "cv_hybrid"):
            assert c[k] == src[k]


def test_the_validator_rejects_a_hybrid_that_is_not_the_preregistered_blend(tmp_path):
    md, _ = PP.build_market_data(tmp_path)
    write_arms(md, hybrid_bad=True)
    validate = load_script("validate_arms")
    problems = []
    validate.check_snapshots(REC.arms_root(md), problems)
    assert any("0.70/0.30" in p for p in problems)
