"""Schema 1.1.0 freezes the player-projection intermediates the model really computes, and changes no price."""
import numpy as np
import pandas as pd

from nfl_edge.research import player_distributions as pdist
from nfl_edge.shadow.ledger import LEDGER_SCHEMA_VERSION, Observation
from nfl_edge.shadow.models import StatModel, survival_quantiles


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


def test_intermediates_are_the_quantities_survival_computes_and_survival_is_unchanged():
    sm = fitted(); rows = frame(20, seed=1)
    grid, S, mu = sm.survival(rows)
    before = S.copy()
    im = sm.intermediates(rows)
    grid2, S2, mu2 = sm.survival(rows)
    assert np.array_equal(S2, before) and np.array_equal(mu2, mu), "instrumentation must not touch the price path"
    assert np.array_equal(im["mu"], mu) and im["family"] == "negbin" and im["efficiency_feature"] == "catch_rate"
    assert im["muo"].shape == mu.shape and np.all(im["muo"] > 0)
    assert np.array_equal(im["eff"], rows["catch_rate"].to_numpy())


def test_survival_quantiles_place_the_median_where_the_cdf_crosses_one_half():
    grid = np.arange(0, 6); S = np.array([1.0, 0.9, 0.6, 0.45, 0.2, 0.05])   # P(Y>=g): CDF at g = 1 - S[g+1]
    q = survival_quantiles(grid, S)
    # CDF: 0.10, 0.40, 0.55, 0.80, 0.95, 1.00 -> the smallest grid value reaching each probability
    assert q["p05"] == 0 and q["p25"] == 1 and q["p50"] == 2 and q["p75"] == 3 and q["p95"] == 4


def test_new_fields_default_none_and_the_schema_version_advanced():
    assert LEDGER_SCHEMA_VERSION == "1.1.0"
    o = Observation(prediction_id="p", schema_version=LEDGER_SCHEMA_VERSION, run_id="r", observed_at="t", model_version="m",
                    model_artifact_sha="s", calibration_version="c", feature_cutoff="f", ticker="T", event_ticker=None, series_ticker=None,
                    family="PLAYER_STAT", period="FULL", stat="receptions", threshold=4, floor_strike=None, operator=">=")
    d = o.to_dict()
    for k in ("projected_stat_mean", "projected_opportunity_mean", "projected_efficiency", "distribution_family", "model_quantiles",
              "ewma_stat", "ewma_opportunity", "feature_n_prior", "implied_total_input", "p_active_no_snap", "fair_price_used"):
        assert k in d and d[k] is None
    assert d["model_event_probability"] is None and d["model_contract_value"] is None
