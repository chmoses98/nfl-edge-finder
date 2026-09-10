"""The player-anatomy corpus: read-only helpers over the frozen model, and strict reconciliation with the ledger."""
import hashlib
import os

import numpy as np
import pandas as pd

from nfl_edge.arms import player_anatomy as PA
from nfl_edge.research import player_distributions as pdist
from nfl_edge.shadow.models import StatModel

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def frame(n=800, seed=0):
    rng = np.random.default_rng(seed)
    tg = rng.gamma(4, 1.5, n)
    df = pd.DataFrame({"ewma_targets": tg, "ewma_receptions": tg * 0.65, "implied_total": rng.normal(23, 3, n),
                       "home": rng.integers(0, 2, n).astype(float), "shrink_w": rng.uniform(0.1, 0.9, n),
                       "catch_rate": np.clip(rng.normal(0.65, 0.08, n), 0.3, 0.95), "position": "WR", "season": 2024})
    df["targets"] = rng.poisson(np.clip(tg, 0.5, None)); df["receptions"] = rng.binomial(df["targets"], df["catch_rate"])
    return df


def fitted():
    spec = pdist.STAT_SPECS["receptions"]; tr = frame()
    mm = pdist.fit_mean_model(tr, spec, spec.col, spec.kind); om = pdist.fit_mean_model(tr, spec, spec.opp, "count")
    mu = pdist.predict_mean(mm, tr, spec, spec.col, pdist.MU_FLOOR[spec.kind]); muo = pdist.predict_mean(om, tr, spec, spec.opp, 0.1)
    fam = pdist.make_family("negbin", spec).fit(mu, muo, tr[spec.eff].to_numpy(), tr[spec.col].to_numpy(dtype=float))
    return StatModel("receptions", "negbin", mm, om, fam, np.arange(0, spec.grid_max + 1), len(tr), (2024, 2024))


def test_the_helpers_are_read_only_over_the_frozen_model_and_agree_with_survival():
    sm = fitted(); rows = frame(20, seed=1)
    grid, S, mu = sm.survival(rows)
    before = S.copy()
    im = PA.intermediates(sm, rows)
    grid2, S2, mu2 = sm.survival(rows)
    assert np.array_equal(S2, before) and np.array_equal(mu2, mu)
    assert np.array_equal(im["mu"], mu) and im["family"] == "negbin" and im["efficiency_feature"] == "catch_rate"
    assert np.array_equal(im["eff"], rows["catch_rate"].to_numpy()) and np.all(im["muo"] > 0)


def test_survival_quantiles_place_each_quantile_where_the_cdf_reaches_it():
    grid = np.arange(0, 6); S = np.array([1.0, 0.9, 0.6, 0.45, 0.2, 0.05])
    q = PA.survival_quantiles(grid, S)                    # CDF: 0.10, 0.40, 0.55, 0.80, 0.95, 1.00
    assert q["p05"] == 0 and q["p25"] == 1 and q["p50"] == 2 and q["p75"] == 3 and q["p95"] == 4


def test_reconciliation_is_strict_and_a_mismatch_is_never_ok():
    row = {"ledger_event_probability": 0.5, "ledger_contract_value": 0.49, "reproduced_event_probability": 0.5,
           "reproduced_contract_value": 0.49, "anatomy_status": PA.OK, "reason": None}
    assert PA.reconcile(dict(row))["anatomy_status"] == PA.OK
    off = PA.reconcile(dict(row, reproduced_contract_value=0.49 + 1e-6))
    assert off["anatomy_status"] == PA.MISMATCH and "differ" in off["reason"]
    missing = PA.reconcile(dict(row, reproduced_event_probability=None))
    assert missing["anatomy_status"] == PA.MISMATCH


def test_the_frozen_modules_are_imported_not_edited():
    """The anatomy reads the frozen pricer's constants; the frozen files themselves are pinned to main elsewhere."""
    src = open(os.path.join(ROOT, "nfl_edge", "arms", "player_anatomy.py")).read()
    assert "from nfl_edge.shadow.models import" in src and "from nfl_edge.research import player_distributions" in src
    assert PA.MODEL_VERSION_DEFAULT == "shadow-0.4.0"
    pricer = open(os.path.join(ROOT, "scripts", "shadow", "price_slate.py")).read()
    assert 'MODEL_VERSION_DEFAULT = "shadow-0.4.0"' in pricer
    assert PA.RECONCILE_TOL <= 1e-9


def test_a_mismatched_anatomy_row_is_not_autopsy_evidence():
    from nfl_edge.shadow import player_autopsy as AU
    from nfl_edge.settlement.results import ResultBook
    row = {"prediction_id": "p", "run_id": "r", "observed_at": "t", "minutes_to_kickoff": 30.0, "game_id": "G", "player_id": "x",
           "stat": "rushing_yards", "threshold": 50, "projected_stat_mean": 60.0, "projected_opportunity_mean": 15.0,
           "efficiency_decomposition": "opportunity_x_efficiency", "model_quantiles": {"p05": 20, "p25": 45, "p50": 60, "p75": 75, "p95": 100},
           "anatomy_status": PA.MISMATCH, "reason": "reproduced p differs"}
    r = AU.diagnose(row, ResultBook())
    assert r["classification"] == AU.INSUFFICIENT_DATA and "not authoritative" in r["evidence"][0]
