"""The scorecard must not conflate two quantities, two spaces, or two sample sizes.

Four ways an evaluation report lies without being wrong anywhere in particular:

  * it scores `model_contract_value` as if it were a probability, so a player prop's participation discount is
    charged to the football model;
  * it calls a squared error on a $0.07 scalar payout a "log loss";
  * it reports 9,830 repeated snapshots of 401 contracts as an n of 9,830;
  * it prints zeros for an empty corpus, which reads exactly like a measurement of zero.
"""
from nfl_edge.shadow import eval_scorecard as SC


def ev(pid="p", *, event_p=0.6, contract=0.6, mid=0.5, settled=1.0, kind="binary", status="SETTLED",
       close_mid=0.55, close_status="OK", family="TOTAL", week=1, horizon=">24h", ticker=None, game="G1",
       mtk=1700.0, observed_at="2025-09-03T20:00:00+00:00", exact=True, **kw):
    d = {"prediction_id": pid, "evaluation_version": "eval-1.0.0", "model_version": "shadow-0.4.0",
         "model_event_probability": event_p, "model_contract_value": contract, "mid_t": mid,
         "settled_yes": settled, "settlement_kind": kind, "settlement_status": status,
         "event_binary_valid": kind == "binary", "exact_payout_known": exact,
         "close_mid": close_mid, "close_status": close_status,
         "signed_clv_mid": (close_mid - mid) if close_mid is not None else None,
         "signed_clv_executable": 0.02, "movement": "toward", "family": family, "stat": None,
         "week": week, "game_id": game, "ticker": ticker or f"T-{pid}", "minutes_to_kickoff": mtk,
         "observed_at": observed_at, "horizon_band": horizon, "disagreement_band": "5-10%",
         "contract_value_band": "0.60-0.70", "event_probability_band": "0.60-0.70",
         "model_direction": "yes", "width_t": 0.02, "liquidity_t": 250.0,
         "availability_state": "EXPECTED_ACTIVE", "support_state": "SUPPORTED"}
    d.update(kw)
    return d


def snapshots(ticker, *, minutes, **kw):
    """The same contract observed at several horizons -- what the corpus actually holds."""
    return [ev(f"{ticker}-{int(m)}", ticker=ticker, mtk=float(m),
               observed_at=f"2025-09-0{1 + i}T00:00:00+00:00", **kw)
            for i, m in enumerate(minutes)]


# ---------------------------------------------------------------- empty
def test_an_empty_corpus_reports_no_numbers():
    sc = SC.build_scorecard([])
    assert sc["sample_units"]["raw"]["n_observations"] == 0
    report = SC.render_report(sc)
    assert "corpus is empty" in report
    assert "0.0000" not in report, "an empty corpus must not print numbers that read like measurements"


# ---------------------------------------------------------------- the two spaces
def test_event_probability_and_contract_value_are_scored_separately():
    """A player prop whose contract value sits below its event probability must not have the two swapped."""
    rows = [ev("a", event_p=0.80, contract=0.60, mid=0.55, settled=1.0, family="PLAYER_STAT")]
    sc = SC.build_scorecard(rows)
    view = sc["views"]["latest_pregame"]
    em = view["event_calibration"]["model_event_probability"]
    pm = view["contract_payout_quality"]["model_contract_value"]
    assert em["mean_predicted"] == 0.8, "the event block scores the EVENT probability"
    assert pm["mean_predicted_payout"] == 0.6, "the payout block scores the CONTRACT value"
    assert abs(em["brier"] - (0.8 - 1.0) ** 2) < 1e-9
    assert abs(pm["mean_squared_payout_error"] - (0.6 - 1.0) ** 2) < 1e-9
    assert em["brier"] != pm["mean_squared_payout_error"], (
        "if these were equal the two quantities would have been conflated")


def test_the_payout_block_never_reports_a_log_loss():
    rows = [ev("a", kind="scalar_exact", settled=0.07, contract=0.22, mid=0.20, event_p=0.31)]
    cp = SC.build_scorecard(rows)["views"]["latest_pregame"]["contract_payout_quality"]
    for block in ("model_contract_value", "market_at_snapshot"):
        assert "log_loss" not in cp[block], "a scalar payout is not a Bernoulli outcome"
        assert "brier" not in cp[block]
    assert cp["model_contract_value"]["mean_squared_payout_error"] is not None
    assert cp["by_settlement_kind"] == {"scalar_exact": 1}


def test_a_scalar_payout_is_excluded_from_event_calibration_but_scored_as_a_payout():
    rows = [ev("bin", kind="binary", settled=1.0), ev("sc", kind="scalar_exact", settled=0.07, contract=0.2)]
    view = SC.build_scorecard(rows)["views"]["latest_pregame"]
    assert view["event_calibration"]["n_event_realisations"] == 1
    assert view["event_calibration"]["excluded"]["no_binary_event_realisation"] == 1
    assert view["contract_payout_quality"]["n_exact_payouts"] == 2, (
        "both payouts are exactly known, so both are scored in contract space")


def test_a_settlement_without_an_exact_payout_is_excluded_from_payout_scoring_and_counted():
    rows = [ev("a"), ev("b", status="REFUSED_EXACT_SCALAR_PAYOUT_UNAVAILABLE", settled=None, kind=None,
                        exact=False, event_p=0.4, contract=0.3)]
    cp = SC.build_scorecard(rows)["views"]["latest_pregame"]["contract_payout_quality"]
    assert cp["n_exact_payouts"] == 1
    assert cp["excluded"]["not_settled"] == 1


def test_the_market_enters_the_event_table_only_where_the_two_spaces_coincide():
    rows = [ev("game", event_p=0.6, contract=0.6, family="GAME_WINNER"),
            ev("prop", event_p=0.8, contract=0.6, family="PLAYER_STAT")]
    ec = SC.build_scorecard(rows)["views"]["latest_pregame"]["event_calibration"]
    assert ec["n_event_realisations"] == 2
    assert ec["market_where_spaces_coincide"]["n_contracts"] == 1, (
        "a midpoint carries the participation discount, so it is not scored against a player's football event")
    assert ec["market_where_spaces_coincide"]["n"] == 1


def test_the_model_is_never_scored_without_the_market_beside_it():
    rows = [ev("a", event_p=0.7, contract=0.7, mid=0.5, settled=1.0),
            ev("b", event_p=0.3, contract=0.3, mid=0.5, settled=0.0)]
    cp = SC.build_scorecard(rows)["views"]["latest_pregame"]["contract_payout_quality"]
    assert cp["model_contract_value"]["n"] == cp["market_at_snapshot"]["n"] == 2
    assert cp["model_contract_value"]["mean_squared_payout_error"] < \
        cp["market_at_snapshot"]["mean_squared_payout_error"], "this model was right twice"
    assert cp["on_rows_with_a_usable_close"]["market_at_close"]["n"] == 2
    assert "market mid at close" in SC.render_report(SC.build_scorecard(rows))


# ---------------------------------------------------------------- sample units
def test_repeated_snapshots_do_not_inflate_the_contract_level_sample():
    rows = snapshots("KX-A", minutes=[1700, 380, 30]) + snapshots("KX-B", minutes=[1700, 380, 30])
    sc = SC.build_scorecard(rows)
    raw, con = sc["sample_units"]["raw"], sc["sample_units"]["latest_pregame"]
    assert raw["n_observations"] == 6 and raw["n_unique_contracts"] == 2
    assert con["n_observations"] == 2, "one row per contract"
    assert sc["primary_sample_unit"] == "latest_pregame"
    assert sc["views"]["latest_pregame"]["contract_payout_quality"]["model_contract_value"]["n"] == 2
    assert sc["views"]["raw"]["contract_payout_quality"]["model_contract_value"]["n"] == 6, (
        "the raw view keeps every observation, and is labelled as correlated diagnostics")
    assert "CORRELATED" in raw["note"]
    report = SC.render_report(sc)
    assert "No effective N is computed" in report


def test_no_effective_n_is_computed_anywhere():
    rows = snapshots("KX-A", minutes=[1700, 380, 30])
    sc = SC.build_scorecard(rows)
    blob = repr(sc).lower()
    assert "effective_n" not in blob and "effective n" not in blob


def test_the_latest_pregame_view_takes_the_freshest_provably_pregame_row():
    rows = snapshots("KX-A", minutes=[1700, 380, 30])
    rows.append(ev("post", ticker="KX-A", mtk=-45.0))            # in-game: never selectable
    rows.append(ev("unknown", ticker="KX-A", mtk=None))          # unknown horizon: not provably pregame
    sel, meta = SC.latest_pregame_view(rows)
    assert len(sel) == 1 and sel[0]["minutes_to_kickoff"] == 30.0
    assert meta["rows_not_provably_pregame_excluded"] == 2
    assert "smallest positive minutes_to_kickoff" in meta["selection_rule"]


def test_the_latest_pregame_selection_is_deterministic_under_ties():
    a = ev("z-pred", ticker="KX-A", mtk=30.0, observed_at="2025-09-04T00:00:00+00:00")
    b = ev("a-pred", ticker="KX-A", mtk=30.0, observed_at="2025-09-04T00:00:00+00:00")
    first = SC.latest_pregame_view([a, b])[0][0]["prediction_id"]
    second = SC.latest_pregame_view([b, a])[0][0]["prediction_id"]
    assert first == second == "a-pred", "ties break on (observed_at, prediction_id), whatever the input order"


# ---------------------------------------------------------------- horizons
def test_a_horizon_takes_the_freshest_snapshot_at_or_before_it():
    rows = snapshots("KX-A", minutes=[1500, 400, 100, 20])
    sel, meta = SC.horizon_view(rows, 90.0)
    assert len(sel) == 1
    assert sel[0]["minutes_to_kickoff"] == 100.0, (
        "the 20-minute snapshot knows things T-90m did not, so it can never represent T-90m")
    assert meta["actual_minutes_to_kickoff"]["median"] == 100.0


def test_a_horizon_with_no_close_enough_snapshot_is_unavailable_not_forced():
    """The explicit ask: do not silently call a five-hour-old observation T-90m."""
    rows = snapshots("KX-A", minutes=[1500, 300])               # nothing between 300 and 90
    sel, meta = SC.horizon_view(rows, 90.0, tolerance=120.0)
    assert sel == [] and meta["n_unavailable"] == 1
    assert meta["unavailable_examples"][0]["nearest_minutes_to_kickoff"] == 300.0
    assert meta["unavailable_examples"][0]["gap_minutes"] == 210.0
    assert meta["tolerance_minutes"] == 120.0


def test_every_selected_horizon_row_reports_its_real_distance_to_kickoff():
    rows = snapshots("KX-A", minutes=[1500, 400, 100, 20]) + snapshots("KX-B", minutes=[1500, 380, 150])
    sc = SC.build_scorecard(rows)
    for label in ("T-24h", "T-6h", "T-90m", "T-30m"):
        h = sc["horizons"][label]
        assert "actual_minutes_to_kickoff" in h and "n_unavailable" in h
        assert h["target_minutes"] > 0 and h["tolerance_minutes"] == SC.HORIZON_TOLERANCE_MINUTES
    t90 = sc["horizons"]["T-90m"]
    assert t90["actual_minutes_to_kickoff"]["min"] == 100.0 and t90["actual_minutes_to_kickoff"]["max"] == 150.0
    assert sc["horizons"]["latest pregame"]["n_observations"] == 2
    report = SC.render_report(sc)
    assert "Canonical horizons" in report and "actual minutes to kickoff" in report


def test_a_horizon_is_one_row_per_contract():
    rows = snapshots("KX-A", minutes=[400, 200, 100]) + snapshots("KX-B", minutes=[400, 200, 100])
    sel, meta = SC.horizon_view(rows, 90.0)
    assert len(sel) == 2 and meta["n_contracts_considered"] == 2
    assert {r["ticker"] for r in sel} == {"KX-A", "KX-B"}


# ---------------------------------------------------------------- CLV and segments
def test_rows_without_a_usable_close_are_excluded_from_clv_and_counted():
    rows = [ev("a", close_mid=0.55), ev("b", close_status="MISSING_CLOSE", close_mid=None, signed_clv_mid=None),
            ev("c", close_status="OK_STALE", close_mid=0.6)]
    clv = SC.build_scorecard(rows)["views"]["latest_pregame"]["clv"]
    assert clv["n"] == 1 and clv["excluded_no_usable_close"] == 2
    assert clv["on_stale_closes"]["n"] == 1, "a stale close is reported in its own block rather than discarded"


def test_when_every_close_is_stale_the_movement_is_still_reported_somewhere():
    rows = [ev(f"p{i}", close_status="OK_STALE", close_mid=0.6) for i in range(5)]
    sc = SC.build_scorecard(rows)
    assert sc["views"]["latest_pregame"]["clv"]["n"] == 0
    assert sc["views"]["latest_pregame"]["clv"]["on_stale_closes"]["n"] == 5
    report = SC.render_report(sc)
    assert "no headline CLV is reported" in report and "breached the staleness budget" in report


def test_movement_never_folds_unchanged_or_no_view_into_a_direction():
    rows = [ev("a", movement="toward"), ev("b", movement="away"), ev("c", movement="unchanged"),
            ev("d", movement="no_view")]
    clv = SC.build_scorecard(rows)["views"]["latest_pregame"]["clv"]
    assert clv["counts"] == {"away": 1, "no_view": 1, "toward": 1, "unchanged": 1}
    assert clv["n_directional"] == 2 and clv["toward_share_of_directional"] == 0.5


def test_event_calibration_buckets_report_predicted_against_actual():
    rows = [ev(f"p{i}", event_p=0.65, contract=0.65, mid=0.6, settled=1.0 if i < 7 else 0.0) for i in range(10)]
    table = SC.build_scorecard(rows)["views"]["latest_pregame"]["event_calibration"][
        "calibration_by_event_probability"]
    assert len(table) == 1
    assert table[0]["band"] == "0.60-0.70" and table[0]["n"] == 10
    assert table[0]["mean_event_probability"] == 0.65 and table[0]["actual_event_rate"] == 0.7


def test_every_requested_segmentation_is_present_and_computed_on_contracts():
    rows = (snapshots("KX-A", minutes=[400, 100], family="PLAYER_STAT", stat="receiving_yards") +
            snapshots("KX-B", minutes=[400, 100], family="TOTAL", week=2))
    seg = SC.build_scorecard(rows)["segments"]
    for label in ("family", "player statistic", "contract value band", "event probability band",
                  "disagreement band", "model direction", "time to kickoff", "model version", "week", "game",
                  "quote width band", "liquidity band", "availability state"):
        assert label in seg, label
    assert set(seg["family"]) == {"PLAYER_STAT", "TOTAL"}
    assert seg["family"]["TOTAL"]["n_contracts"] == 1, "segments count contracts, not snapshots"


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
    rows = [ev("a", status="REFUSED_UNSUPPORTED_FAMILY", settled=None, kind=None, exact=False,
               family="TOTAL_TD")]
    seg = SC.build_scorecard(rows)["segments"]["family"]["TOTAL_TD"]
    assert seg["n_contracts"] == 1 and seg["n_event_realisations"] == 0 and seg["n_exact_payouts"] == 0
    assert seg["event_brier"] is None and seg["model_payout_mse"] is None, (
        "no score is invented for a segment with nothing settled"
    )


def test_the_report_states_that_the_sample_size_is_contracts_not_observations():
    rows = snapshots("KX-A", minutes=[1700, 380, 30])
    report = SC.render_report(SC.build_scorecard(rows))
    assert "Nothing here promotes a model change" in report
    assert "CONTRACT count, not the observation" in report
    assert "not evidence" in report


def test_log_loss_is_finite_even_at_a_confident_miss():
    rows = [ev("a", event_p=1.0, contract=1.0, settled=0.0), ev("b", event_p=0.0, contract=0.0, settled=1.0)]
    m = SC.build_scorecard(rows)["views"]["latest_pregame"]["event_calibration"]["model_event_probability"]
    assert m["brier"] == 1.0 and 0 < m["log_loss"] < 100
