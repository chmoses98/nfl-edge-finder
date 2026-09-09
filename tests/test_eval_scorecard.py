"""The scorecard must compare, must exclude what it cannot score, and must never print a number it did not measure.

Three ways an evaluation report lies without being wrong anywhere in particular:

  * it scores the model alone, so a Brier of 0.19 looks like an achievement instead of a number needing a
    comparison;
  * it folds non-binary payouts (a tied game at $0.50, a scratched player at the pregame fair price) into the
    calibration, moving it for reasons that have nothing to do with forecasting;
  * it prints zeros for an empty corpus, which reads exactly like a measurement of zero.
"""
from nfl_edge.shadow import eval_scorecard as SC


def ev(pid="p", *, model_p=0.6, mid=0.5, settled=1.0, kind="binary", status="SETTLED", close_mid=0.55,
       close_status="OK", family="TOTAL", week=1, horizon=">24h", **kw):
    d = {"prediction_id": pid, "evaluation_version": "eval-1.0.0", "model_version": "shadow-0.4.0",
         "model_p": model_p, "mid_t": mid, "settled_yes": settled, "settlement_kind": kind,
         "settlement_status": status, "close_mid": close_mid, "close_status": close_status,
         "signed_clv_mid": (close_mid - mid) if close_mid is not None else None,
         "signed_clv_executable": 0.02, "movement": "toward", "family": family, "stat": None,
         "week": week, "game_id": "2025_01_DAL_PHI", "horizon_band": horizon, "disagreement_band": "5-10%",
         "probability_band": "0.60-0.70", "model_direction": "yes", "width_t": 0.02, "liquidity_t": 250.0,
         "availability_state": "EXPECTED_ACTIVE", "support_state": "SUPPORTED"}
    d.update(kw)
    return d


def test_an_empty_corpus_reports_no_numbers():
    sc = SC.build_scorecard([])
    assert sc["n_evaluations"] == 0 and sc["calibration"] == []
    report = SC.render_report(sc)
    assert "corpus is empty" in report
    assert "0.0000" not in report, "an empty corpus must not print numbers that read like measurements"


def test_the_model_is_never_scored_without_the_market_beside_it():
    rows = [ev("a", model_p=0.7, mid=0.5, settled=1.0), ev("b", model_p=0.3, mid=0.5, settled=0.0)]
    mv = SC.build_scorecard(rows)["model_vs_market"]
    assert mv["model"]["n"] == mv["market_at_snapshot"]["n"] == 2
    assert mv["model"]["brier"] < mv["market_at_snapshot"]["brier"], "this model was right twice"
    sub = mv["on_rows_with_a_usable_close"]
    assert sub["n"] == 2 and sub["market_at_close"]["n"] == 2
    assert "market mid at close" in SC.render_report(SC.build_scorecard(rows))


def test_non_binary_settlements_are_excluded_from_calibration_and_counted():
    rows = [ev("a"), ev("b", kind="tie_split", settled=0.5),
            ev("c", kind="scalar_fair_price", settled=0.12),
            ev("d", status="REFUSED_PARTICIPATION_UNPROVEN", settled=None, kind=None)]
    sc = SC.build_scorecard(rows)
    assert sc["model_vs_market"]["n_binary_settled"] == 1
    assert sc["excluded_from_calibration"]["non_binary_settlement"] == 2
    assert sc["excluded_from_calibration"]["not_settled"] == 1
    assert sc["counts"]["by_settlement_kind"] == {"binary": 1, "scalar_fair_price": 1, "tie_split": 1}


def test_rows_without_a_usable_close_are_excluded_from_clv_and_counted():
    rows = [ev("a", close_mid=0.55), ev("b", close_status="MISSING_CLOSE", close_mid=None, signed_clv_mid=None),
            ev("c", close_status="OK_STALE", close_mid=0.6)]
    clv = SC.build_scorecard(rows)["clv"]
    assert clv["n"] == 1 and clv["excluded_no_usable_close"] == 2, (
        "a stale close is kept out of the headline CLV number")
    assert clv["on_stale_closes"]["n"] == 1, "and is reported in its own block rather than discarded"


def test_when_every_close_is_stale_the_movement_is_still_reported_somewhere():
    """A run made hours before kickoff has nothing but stale closes. Losing all of it would hide real movement."""
    rows = [ev(f"p{i}", close_status="OK_STALE", close_mid=0.6) for i in range(5)]
    sc = SC.build_scorecard(rows)
    assert sc["clv"]["n"] == 0
    assert sc["clv"]["on_stale_closes"]["n"] == 5
    report = SC.render_report(sc)
    assert "no headline CLV is reported" in report and "breached the staleness budget" in report


def test_calibration_buckets_report_predicted_against_actual():
    rows = [ev(f"p{i}", model_p=0.65, mid=0.6, settled=1.0 if i < 7 else 0.0) for i in range(10)]
    table = SC.build_scorecard(rows)["calibration"]
    assert len(table) == 1
    row = table[0]
    assert row["band"] == "0.60-0.70" and row["n"] == 10
    assert row["mean_model_p"] == 0.65 and row["actual_rate"] == 0.7
    assert row["mean_market_mid"] == 0.6


def test_movement_never_folds_unchanged_or_no_view_into_a_direction():
    rows = [ev("a", movement="toward"), ev("b", movement="away"), ev("c", movement="unchanged"),
            ev("d", movement="no_view")]
    clv = SC.build_scorecard(rows)["clv"]
    assert clv["counts"] == {"away": 1, "no_view": 1, "toward": 1, "unchanged": 1}
    assert clv["n_directional"] == 2 and clv["toward_share_of_directional"] == 0.5


def test_every_requested_segmentation_is_present():
    rows = [ev("a", family="PLAYER_STAT", stat="receiving_yards", horizon="<30m"),
            ev("b", family="TOTAL", horizon=">24h", week=2)]
    seg = SC.build_scorecard(rows)["segments"]
    for label in ("family", "player statistic", "model probability band", "disagreement band",
                  "model direction", "time to kickoff", "model version", "week", "game",
                  "quote width band", "liquidity band", "availability state"):
        assert label in seg, label
    assert set(seg["family"]) == {"PLAYER_STAT", "TOTAL"}
    assert set(seg["time to kickoff"]) == {"<30m", ">24h"}
    assert seg["family"]["TOTAL"]["clv"]["n"] == 1


def test_the_bands_are_the_ones_the_research_question_asks_for():
    from nfl_edge.shadow.evaluation import disagreement_band, horizon_band
    assert [disagreement_band(x) for x in (0.01, 0.04, 0.07, 0.15, 0.4)] == \
        ["<3%", "3-5%", "5-10%", "10-20%", "20%+"]
    assert [horizon_band(x) for x in (10, 45, 200, 700, 3000)] == \
        ["<30m", "30-90m", "90m-6h", "6-24h", ">24h"]
    assert disagreement_band(None) is None and horizon_band(None) is None
    assert SC.width_band(0.01) == "<=2c" and SC.width_band(0.3) == ">10c"
    assert SC.liquidity_band(0.0) == "none" and SC.liquidity_band(5000) == ">$1k"


def test_a_segment_with_no_scoreable_row_reports_its_size_and_no_metrics():
    rows = [ev("a", status="REFUSED_UNSUPPORTED_FAMILY", settled=None, kind=None, family="TOTAL_TD")]
    seg = SC.build_scorecard(rows)["segments"]["family"]["TOTAL_TD"]
    assert seg["n"] == 1 and seg["n_binary_settled"] == 0
    assert seg["model"] == {"n": 0}, "no Brier score is invented for a segment with nothing settled"


def test_the_report_states_that_one_week_is_not_evidence():
    rows = [ev("a")]
    report = SC.render_report(SC.build_scorecard(rows))
    assert "Nothing here promotes a model change" in report
    assert "not evidence" in report


def test_log_loss_is_finite_even_at_a_confident_miss():
    rows = [ev("a", model_p=1.0, settled=0.0), ev("b", model_p=0.0, settled=1.0)]
    m = SC.build_scorecard(rows)["model_vs_market"]["model"]
    assert m["brier"] == 1.0 and m["log_loss"] > 0 and m["log_loss"] < 100
