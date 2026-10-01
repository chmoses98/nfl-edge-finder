"""The full-board research table, the conditional miner and the preregistered board hypotheses.

Deterministic, no network, no market-data checkout: every input is synthetic and built here.
"""
import gzip
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.research import board as B                      # noqa: E402
from nfl_edge.research import board_hypotheses as BH          # noqa: E402
from nfl_edge.research import board_miner as M                # noqa: E402
from nfl_edge.research import hypothesis_registry_v2 as HR    # noqa: E402

KO = datetime(2026, 9, 20, 17, 0, tzinfo=timezone.utc)
GID = "2026_02_KC_BUF"


def game(gid=GID, week=2, ko=KO, home="BUF", away="KC"):
    return B.Game(gid, 2026, week, home, away, ko.date().isoformat(), ko.isoformat())


def q(ticker, t, yb, ya, *, gid=GID, run=None, status="active", family="SPREAD", team="BUF", thr=3.5, op=">",
      floor=3.5, series="KXNFLSPREAD", close_time=None, player=None, stat=None):
    nb, na = (round(1 - ya, 4), round(1 - yb, 4))
    return json.dumps({"run_id": run or t.strftime("%Y%m%dT%H%M%SZ"), "observed_at": t.isoformat(), "ticker": ticker,
                       "event_ticker": ticker.rsplit("-", 1)[0], "series_ticker": series, "family": family, "period": "FULL",
                       "stat": stat, "team": team, "player_name": None, "player_kalshi_id": player, "threshold": thr,
                       "operator": op, "floor_strike": floor, "game_id": gid, "status": status,
                       "yes_bid_dollars": f"{yb:.4f}", "yes_ask_dollars": f"{ya:.4f}", "no_bid_dollars": f"{nb:.4f}",
                       "no_ask_dollars": f"{na:.4f}", "volume_fp": "10", "open_interest_fp": "5", "liquidity_dollars": "100",
                       "last_price_dollars": "0.5", "close_time": close_time})


def manifest(t, series="KXNFLSPREAD", complete=True):
    return {"run_id": t.strftime("%Y%m%dT%H%M%SZ"), "series": {series: {"observed_at": t.isoformat(), "complete": complete, "n": 5}}}


def build(lines, manifests=(), games=None, last_seen=None):
    b = B.BoardBuilder(games or {GID: game()})
    for m in manifests:
        b.manifests.add(m)
    b.last_seen = last_seen or {}
    b.feed_quote_lines(lines)
    b.finalize()
    return b


# ------------------------------------------------------------------------------------------------ 1. leakage
def test_post_kickoff_rows_never_become_a_horizon_observation():
    t = "KXNFLSPREAD-26SEP20KCBUF-BUF3"
    lines = [q(t, KO - timedelta(hours=30), 0.40, 0.42), q(t, KO - timedelta(minutes=10), 0.50, 0.52),
             q(t, KO + timedelta(minutes=1), 0.90, 0.95), q(t, KO, 0.91, 0.96)]            # at and after kickoff
    b = build(lines, [manifest(KO - timedelta(minutes=5))])
    c = b.contracts[t]
    assert c.n_postgame == 2 and c.n_pregame == 2
    ob = b.observation(t, B.HORIZON_NAMES.index("latest_pregame"))
    assert ob["yes_ask"] == 0.52 and ob["obs_state"] == B.OBS_OK
    assert B._dt(ob["observed_at"]) < KO


def test_a_row_exactly_at_a_horizon_cutoff_belongs_to_the_later_horizon():
    """State at a cutoff is the last change STRICTLY before it (close.py's '< kickoff', generalised)."""
    t = "KXNFLSPREAD-26SEP20KCBUF-BUF3"
    cut6 = KO - timedelta(hours=6)
    b = build([q(t, KO - timedelta(hours=8), 0.30, 0.32), q(t, cut6, 0.60, 0.62)], [manifest(cut6 - timedelta(minutes=1))])
    i6 = B.HORIZON_NAMES.index("T-6h")
    assert b.observation(t, i6)["yes_ask"] == 0.32
    assert b.observation(t, B.HORIZON_NAMES.index("T-90m"))["yes_ask"] == 0.62


# ------------------------------------------------------------------------------------------------ 2. one per horizon
def test_repeated_snapshots_collapse_to_one_observation_per_horizon():
    t = "KXNFLSPREAD-26SEP20KCBUF-BUF3"
    lines = [q(t, KO - timedelta(hours=40) + timedelta(minutes=10 * i), 0.40 + 0.001 * i, 0.42 + 0.001 * i) for i in range(200)]
    b = build(lines, [manifest(KO - timedelta(minutes=2))])
    rows = list(B.assemble_game(b, game(), {t: {"settled_yes": 1.0, "settlement_source": B.SRC_FOOTBALL, "binary_outcome": True}},
                                _Fees()))
    assert len(rows) == len(B.HORIZONS) and {r["horizon"] for r in rows} == set(B.HORIZON_NAMES)
    assert all(r["n_pregame_snapshots"] == 200 for r in rows)


def test_a_contract_listed_after_a_horizon_is_not_listed_there():
    t = "KXNFLSPREAD-26SEP20KCBUF-BUF3"
    b = build([q(t, KO - timedelta(hours=2), 0.4, 0.42)], [manifest(KO - timedelta(minutes=m)) for m in (100, 2)])
    assert b.observation(t, B.HORIZON_NAMES.index("T-24h"))["obs_state"] == B.OBS_NOT_LISTED
    assert b.observation(t, B.HORIZON_NAMES.index("T-90m"))["obs_state"] == B.OBS_OK


# ------------------------------------------------------------------------------------------------ confirmation = close rule
def test_confirmation_follows_the_close_rule(tmp_path):
    """latest_pregame IS the canonical close: same price row and same confirming run as close.CloseIndex."""
    from nfl_edge.evaluation.close import CloseIndex
    t = "KXNFLSPREAD-26SEP20KCBUF-BUF3"
    day = tmp_path / "2026-09-20"
    day.mkdir()
    rows = [q(t, KO - timedelta(hours=3), 0.44, 0.46), q(t, KO - timedelta(minutes=50), 0.47, 0.49)]
    (day / "20260920T160000Z.quotes.jsonl").write_text("\n".join(rows) + "\n")
    mans = [manifest(KO - timedelta(minutes=m)) for m in (180, 50, 12)] + [manifest(KO + timedelta(minutes=5))]
    for m in mans:
        (day / f"{m['run_id']}.manifest.json").write_text(json.dumps(m))
    ci = CloseIndex(str(tmp_path), GID, KO.isoformat(), days_back=3)
    close = ci.select(t, series_ticker="KXNFLSPREAD")
    b = build(rows, mans)
    ob = b.observation(t, B.HORIZON_NAMES.index("latest_pregame"))
    assert close["yes_ask"] == ob["yes_ask"] and close["yes_bid"] == ob["yes_bid"]
    assert B._dt(close["confirmed_at"]) == B._dt(ob["confirmed_at"])
    assert close["close_quality"] == ob["quality"] == B.EXCELLENT


def test_a_price_nobody_confirmed_for_a_day_is_not_an_observation():
    t = "KXNFLSPREAD-26SEP20KCBUF-BUF3"
    b = build([q(t, KO - timedelta(hours=50), 0.4, 0.42)], [manifest(KO - timedelta(hours=49))])
    ob = b.observation(t, B.HORIZON_NAMES.index("latest_pregame"))
    assert ob["obs_state"] == B.OBS_UNCONFIRMED and ob["quality"] == B.MISSING


def test_a_closed_market_is_not_open_at_the_horizon():
    t = "KXNFLSPREAD-26SEP20KCBUF-BUF3"
    b = build([q(t, KO - timedelta(hours=5), 0.4, 0.42, close_time=(KO - timedelta(hours=1)).isoformat())],
              [manifest(KO - timedelta(minutes=m)) for m in (100, 3)])
    assert b.observation(t, B.HORIZON_NAMES.index("latest_pregame"))["obs_state"] == B.OBS_NOT_OPEN
    assert b.observation(t, B.HORIZON_NAMES.index("T-90m"))["obs_state"] == B.OBS_OK


# ------------------------------------------------------------------------------------------------ 3. fees
class _Sched:
    def __init__(self):
        self.calls = []

    def window_for(self, as_of):
        return {"effective_from": "2026-07-07T00:00:00+00:00"}

    def taker_fee(self, p, contracts, series, as_of=None):
        from decimal import ROUND_CEILING, Decimal
        self.calls.append((p, contracts, series, as_of))
        raw = 0.07 * contracts * p * (1 - p)
        amt = float(Decimal(str(raw)).quantize(Decimal("0.01"), rounding=ROUND_CEILING))
        return type("Q", (), {"amount": amt, "is_known": True, "state": "KNOWN"})()


class _Fees(B.FeeCache):
    def __init__(self):
        super().__init__(_Sched())


def test_fees_are_taken_from_the_schedule_at_the_observation_time():
    f = _Fees()
    at = KO - timedelta(hours=1)
    out = f.fee("KXNFLSPREAD", 0.35, at.timestamp())
    assert out["fee_one"] == 0.02, "one contract rounds up to the cent"
    assert out["fee_marginal"] == pytest.approx(0.0160, abs=1e-4), "100 contracts / 100 ~ the raw quadratic"
    assert f.schedule.calls[0][3] == at, "the fee is priced as of the observation, never wall clock"
    assert f.fee("KXNFLSPREAD", 1.0, at.timestamp())["fee_state"] == "NO_PRICE"


def test_the_real_committed_schedule_prices_a_known_fee():
    from nfl_edge.execution.fees import load_fee_schedule
    f = B.FeeCache(load_fee_schedule(ROOT))
    out = f.fee("KXNFLSPREAD", 0.5, datetime(2026, 9, 20, tzinfo=timezone.utc).timestamp())
    assert out["fee_state"] == "KNOWN" and 0.0 < out["fee_marginal"] <= out["fee_one"]


# ------------------------------------------------------------------------------------------------ 4. YES / NO
def test_yes_and_no_returns_pay_the_right_side():
    assert B.side_return(1.0, 0.40, 0.02) == pytest.approx(0.58)
    assert B.side_return(0.0, 0.40, 0.02) == pytest.approx(-0.42)
    assert B.side_return(None, 0.40, 0.02) is None and B.side_return(1.0, 1.0, 0.0) is None
    row = {"settled_yes": 0.0, "yes_ask": 0.30, "no_ask": 0.72, "fee_yes": 0.01, "fee_no": 0.01, "return_yes": -0.31,
           "return_no": 0.27, "mid": 0.29, **{k: None for k in ("clv_yes", "clv_no")}, "family": "SPREAD", "period": "FULL",
           "week": 2, "game_id": GID, "ticker": "T"}
    s = {x["side"]: x for x in M.side_rows([row])}
    assert s["YES"]["won"] == 0.0 and s["NO"]["won"] == 1.0
    assert s["NO"]["side_mid"] == pytest.approx(0.71) and s["NO"]["price"] == 0.72


# ------------------------------------------------------------------------------------------------ 5. ladders
def test_ladder_grouping_main_rung_and_offsets():
    st = lambda t, x: {"ticker": t, "game_id": GID, "family": "PLAYER_STAT", "period": "FULL", "team": None,  # noqa: E731
                       "player_kalshi_id": "p1", "stat": "receiving_yards", "operator": ">=", "threshold": x}
    ob = lambda m: {"obs_state": B.OBS_OK, "two_sided": True, "mid": m}  # noqa: E731
    at = [(st("A", 40), ob(0.80)), (st("B", 60), ob(0.52)), (st("C", 80), ob(0.30)), (st("D", 100), ob(0.12))]
    lad = B.ladder_structure(at)
    assert len({v["ladder_id"] for v in lad.values()}) == 1, "four thresholds of one player stat are ONE ladder"
    assert lad["B"]["is_main_rung"] and lad["B"]["rung_offset"] == 0
    assert lad["A"]["rung_offset"] == -1 and lad["D"]["rung_offset"] == 2 and lad["C"]["distance_from_main"] == 20
    assert B.median_from_survival([(40, 0.8), (60, 0.52), (80, 0.3)]) == pytest.approx(60 + 0.02 * 20 / 0.22)


def test_a_non_monotone_ladder_is_fitted_and_flagged():
    fit = B.pav_decreasing([(1, 0.6), (2, 0.7), (3, 0.2)])
    assert [x for x, _ in fit] == [1, 2, 3] and [y for _, y in fit] == pytest.approx([0.65, 0.65, 0.2])
    st = lambda t, x: {"ticker": t, "game_id": GID, "family": "TOTAL", "period": "FULL", "team": None,  # noqa: E731
                       "player_kalshi_id": None, "stat": "total_points", "operator": ">=", "threshold": x}
    ob = lambda m: {"obs_state": B.OBS_OK, "two_sided": True, "mid": m}  # noqa: E731
    lad = B.ladder_structure([(st("A", 40), ob(0.6)), (st("B", 44), ob(0.7)), (st("C", 48), ob(0.3))])
    assert lad["A"]["ladder_monotone_violations"] == 1


def test_game_environment_uses_both_teams_spread_ladders_and_never_the_closing_consensus():
    g = game()
    st = lambda t, fam, team, x: {"ticker": t, "family": fam, "period": "FULL", "team": team, "operator": ">", "floor_strike": x, "threshold": x}  # noqa: E731
    ob = lambda m: {"obs_state": B.OBS_OK, "two_sided": True, "mid": m}  # noqa: E731
    at = [(st("a", "SPREAD", "BUF", 1.5), ob(0.62)), (st("b", "SPREAD", "BUF", 4.5), ob(0.45)),
          (st("c", "SPREAD", "KC", 1.5), ob(0.30)), (st("d", "TOTAL", None, 44.5), ob(0.55)), (st("e", "TOTAL", None, 48.5), ob(0.40))]
    env = B.game_environment(at, g)
    assert env["env_favorite"] == "BUF" and 2.5 < env["env_home_margin"] < 4.5
    assert 44.5 < env["env_total"] < 48.5 and env["env_source"] == "board ladder medians"
    assert B.game_environment([], g)["env_source"] == "UNAVAILABLE"


# ------------------------------------------------------------------------------------------------ 6/7. settlement tiers
def test_settlement_tiers_never_mix_and_disagreement_is_flagged():
    fs = {"settlement_status": "SETTLED", "settled_yes_football": 1.0, "settlement_kind": "binary", "exchange_yes": 1.0}
    assert B.resolve_settlement(fs) == {"settled_yes": 1.0, "settlement_source": B.SRC_FOOTBALL, "exchange_agrees": True, "binary_outcome": True}
    fs = {"settlement_status": "SETTLED", "settled_yes_football": 0.0, "settlement_kind": "binary", "exchange_yes": 1.0}
    assert B.resolve_settlement(fs)["exchange_agrees"] is False and B.resolve_settlement(fs)["settled_yes"] == 0.0, (
        "football is the settlement; the exchange's contradiction is a flag, never an overwrite")
    fs = {"settlement_status": "REFUSED_UNSUPPORTED_FAMILY", "settled_yes_football": None, "exchange_yes": 0.0}
    assert B.resolve_settlement(fs)["settlement_source"] == B.SRC_EXCHANGE
    assert B.resolve_settlement({"settlement_status": "REFUSED_X"})["settlement_source"] == B.SRC_NONE


def test_exchange_record_requires_a_terminal_status():
    assert B.exchange_record({"status": "determined", "result": "yes"})["exchange_state"].startswith("NOT_TERMINAL")
    assert B.exchange_record({"status": "finalized", "result": "no"})["exchange_yes"] == 0.0
    assert B.exchange_record({"status": "settled", "result": "scalar", "settlement_value_dollars": "0.37"})["exchange_yes"] == 0.37
    assert B.exchange_record({"status": "finalized", "result": "scalar"})["exchange_state"] == "TERMINAL_SCALAR_WITHOUT_VALUE"


def test_an_unmapped_player_is_refused_for_identity_not_guessed():
    static = {"ticker": "KXNFLRECYDS-26SEP20KCBUF-X-60", "event_ticker": "E", "series_ticker": "KXNFLRECYDS", "family": "PLAYER_STAT",
              "period": "FULL", "stat": "receiving_yards", "team": None, "player_name": "X", "player_kalshi_id": "unmapped-id",
              "threshold": 60, "operator": ">=", "floor_strike": None, "game_id": GID}
    out = B.football_settlement(static, None, book=None, period_book=None, player_map={})
    assert out["settlement_status"] in ("REFUSED_PLAYER_IDENTITY", "REFUSED_SEMANTICS") and out["settled_yes_football"] is None


# ------------------------------------------------------------------------------------------------ 8. exclusions / funnel
def _row(**kw):
    base = {"week": 2, "family": "SPREAD", "horizon": "latest_pregame", "n_pregame_snapshots": 3, "settled_yes": 1.0,
            "settlement_source": B.SRC_FOOTBALL, "settlement_status": "SETTLED", "binary_outcome": True, "obs_state": B.OBS_OK,
            "yes_ask": 0.4, "no_ask": 0.62, "fee_yes": 0.01, "fee_no": 0.01, "exchange_agrees": True, "subfamily": "SPREAD:FULL"}
    base.update(kw)
    base["analysis_state"], base["exclusion_reason"] = B.analysis_state(base)
    return base


def test_every_exclusion_has_a_reason_and_the_funnel_loses_nothing():
    rows = [_row(), _row(obs_state=B.OBS_NOT_LISTED), _row(settlement_source=B.SRC_EXCHANGE, settlement_status="REFUSED_UNSUPPORTED_FAMILY"),
            _row(settlement_source=B.SRC_NONE, settled_yes=None, settlement_status="REFUSED_X"), _row(exchange_agrees=False),
            _row(binary_outcome=False), _row(fee_yes=None, fee_no=None), _row(n_pregame_snapshots=0, obs_state=B.OBS_NOT_LISTED)]
    for r in rows:
        assert (r["analysis_state"] == B.ANALYZED) == (r["exclusion_reason"] is None)
    f = B.CoverageFunnel()
    for r in rows:
        f.add_row(r)
    f.add_discovered_only(2, "SPREAD", "captured_pregame: never captured")
    d = f.to_dict()["total"]
    assert d["discovered"] == 9 and d["analyzed_primary"] == 1
    assert sum(d["exclusions"].values()) == d["discovered"] - d["analyzed_primary"], "every lost contract carries a reason"


# ------------------------------------------------------------------------------------------------ 9. clustering
def _side(game_id, week, won, price=0.40, fee=0.01, **kw):
    r = {"game_id": game_id, "week": week, "won": won, "price": price, "fee": fee, "ret": won - price - fee, "ladder_id": f"L{game_id}",
         "clv": None, "side_mid": price - 0.01}
    r.update(kw)
    return r


def test_contract_count_never_masquerades_as_independent_evidence():
    rows = [_side("G1", 1, 1.0) for _ in range(500)]
    st = M.cell_stats(rows)
    assert st["n_contracts"] == 500 and st["n_games"] == 1 and st["bootstrap"] is None
    assert M.label(st) == M.DESCRIPTIVE_ONLY, "500 rungs of one game are one observation"


def test_rare_outcomes_get_the_binomial_floor():
    # 0 of 60 contracts at 7c, but over only 30 games: resampling games shows almost no uncertainty, the event rate
    # still does. Wilson(0 of 30) reaches ~11%, above the ~8c cost, so the cell is not proven overpriced.
    rows = [_side(f"G{i % 30}", 1 + i % 3, 0.0, price=0.07) for i in range(60)]
    st = M.cell_stats(rows)
    assert st["binomial_floor_applied"] and st["ci"][1] > 0 > st["ci"][0]
    assert st["bootstrap"]["ci"][1] < 0, "the bootstrap alone would have called it certain"
    assert M.label(st) != M.CANDIDATE
    # with real outcome variation the floor does not apply
    varied = [_side(f"G{i % 30}", 1 + i % 3, float(i % 2), price=0.45) for i in range(60)]
    assert M.cell_stats(varied)["binomial_floor_applied"] is False


def test_benjamini_hochberg_is_monotone_and_bounded():
    q = M.bh_qvalues([0.001, 0.04, 0.03, 0.5])
    assert q[0] <= q[2] <= q[1] <= q[3] <= 1.0


def test_the_miner_labels_every_cell_and_promotes_nothing():
    rows = []
    for g in range(30):
        for t in range(4):
            rows.append({"season": 2026, "week": 1 + g % 3, "game_id": f"G{g}", "ticker": f"T{g}-{t}", "family": "SPREAD", "period": "FULL",
                         "stat": None, "subfamily": "SPREAD:FULL", "position": None, "env_spread_band": "fav3-7", "env_total_band": "total41-45",
                         "team_role": "FAVORITE", "role_certainty": "n/a", "availability_state": None, "data_only_disagreement_band": "unknown",
                         "player_disagreement_band": "unknown", "move_band": "unknown", "rung_offset_band": "main", "ladder_id": f"L{g}",
                         "horizon": "latest_pregame", "analysis_state": "ANALYZED", "settled_yes": float((g + t) % 2), "yes_ask": 0.5,
                         "no_ask": 0.52, "fee_yes": 0.0175, "fee_no": 0.0175, "return_yes": float((g + t) % 2) - 0.5175,
                         "return_no": 1 - float((g + t) % 2) - 0.5375, "clv_yes": None, "clv_no": None, "mid": 0.49,
                         "player_disagreement": None})
    res = M.mine(rows, horizon="latest_pregame", discovery_weeks=[1, 2, 3])
    assert res["betting_authorized"] is False and res["n_cells"] == len(res["cells"])
    assert all(c["status"] in (M.DESCRIPTIVE_ONLY, M.NO_SIGNAL, M.UNSTABLE, M.NOT_SIG_MULT, M.CANDIDATE) for c in res["cells"])
    assert "SUPPORTED" not in {c["status"] for c in res["cells"]}
    assert res["evidence_class"].startswith("HYPOTHESIS_GENERATING")


# ------------------------------------------------------------------------------------------------ 10. discovery vs prospective
def test_the_prospective_evaluation_never_reads_the_discovery_weeks():
    spec = BH.BOARD_HYPOTHESES[0]
    out = BH.prospective(spec, [], future_weeks=[1, 2, 3], n_under_test=13)
    assert out["weeks"] == [] and out["suggestion"]["suggested_status"] == "INCONCLUSIVE"


def test_the_registry_refuses_a_board_test_window_that_overlaps_discovery(tmp_path):
    path = str(tmp_path / "h.jsonl")
    spec = BH.BOARD_HYPOTHESES[0]
    HR.add(hid="H-T-B01", market_family="X", condition="c", direction="d", expected_mechanism="m", evaluation_metric="e",
           minimum_sample=48, generation_window=BH.GENERATION_WINDOW, future_test_window=BH.FUTURE_WINDOW, generated_by="t",
           hypothesis_kind=BH.HYPOTHESIS_KIND, locator=BH.locator(spec), path=path)
    with pytest.raises(HR.RegistryError):
        HR.preregister("H-T-B01", test_window={"season": 2026, "week_lo": 3, "week_hi": 6}, thresholds=BH.THRESHOLDS,
                       evaluation_plan="p", path=path)
    with pytest.raises(HR.RegistryError):
        HR.preregister("H-T-B01", test_window=BH.FUTURE_WINDOW, thresholds=BH.THRESHOLDS, evaluation_plan="p",
                       preregistered_at="2026-10-02T01:00:00+00:00", first_test_kickoff_utc=BH.FIRST_TEST_KICKOFF_UTC, path=path)


def test_registered_board_hypotheses_are_complete_stage_b_records():
    cur = HR.current()
    board = {h: r for h, r in cur.items() if (r.get("locator") or {}).get("kind") == BH.HYPOTHESIS_KIND}
    assert len(board) == len(BH.BOARD_HYPOTHESES)
    for hid, row in board.items():
        assert HR.governance(row)["stage"] == HR.STAGE_PREREGISTERED and not HR.preregistration_defects(row)
        assert row["generation_window"] == BH.GENERATION_WINDOW
        assert HR._parse_ts(row["preregistration"]["preregistered_at"]) < HR._parse_ts(BH.FIRST_TEST_KICKOFF_UTC)
        assert BH.spec_from_registry(row)["filter"] == row["locator"]["filter"], "the registered locator, not the constant"


def test_a_suggestion_is_only_a_suggestion():
    spec = BH.BOARD_HYPOTHESES[2]                      # B03, sign -1
    ev = {"n": 500, "n_games": 60, "n_weeks": 4, "value": -0.03, "ci_family": [-0.05, -0.01]}
    s = BH.suggest(spec, ev, n_under_test=13)
    assert s["suggested_status"] == "SUPPORTED" and "owner approval" in s["suggestion_only"]
    ev["n_games"] = 10
    assert BH.suggest(spec, ev, n_under_test=13)["suggested_status"] == "INCONCLUSIVE"


# ------------------------------------------------------------------------------------------------ 11. no authority
def test_board_rows_carry_no_betting_authority():
    t = "KXNFLSPREAD-26SEP20KCBUF-BUF3"
    b = build([q(t, KO - timedelta(hours=2), 0.4, 0.42)], [manifest(KO - timedelta(minutes=2))])
    rows = list(B.assemble_game(b, game(), {}, _Fees()))
    assert rows and all(r["betting_authorized"] is False for r in rows)


def test_the_betting_path_cannot_import_the_board_research():
    import ast
    targets = ("nfl_edge.research.board", "nfl_edge.research.board_miner", "nfl_edge.research.board_hypotheses")
    for rel in ("nfl_edge/handicap/gates.py", "nfl_edge/handicap/risk.py", "nfl_edge/handicap/wager_risk.py",
                "nfl_edge/handicap/preflight.py", "nfl_edge/handicap/approval.py", "nfl_edge/handicap/evaluate.py"):
        tree = ast.parse(open(os.path.join(ROOT, rel)).read())
        mods = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module} | \
               {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        assert not any(m.startswith(t) for m in mods for t in targets), f"{rel} imports board research"


# ------------------------------------------------------------------------------------------------ 17. streaming
def test_other_weeks_are_rejected_before_any_json_is_parsed():
    b = B.BoardBuilder({GID: game()})
    b.feed_quote_lines(['{"game_id":"2026_05_X_Y", this is not json', "not json at all", q("T", KO - timedelta(hours=1), 0.4, 0.42)])
    assert b.stats["unparseable_lines"] == 0 and b.stats["lines"] == 3 and len(b.contracts) == 1


def test_out_of_order_rows_cannot_rewrite_a_later_state():
    t = "KXNFLSPREAD-26SEP20KCBUF-BUF3"
    b = build([q(t, KO - timedelta(hours=1), 0.5, 0.52), q(t, KO - timedelta(hours=3), 0.1, 0.12)], [manifest(KO - timedelta(minutes=2))])
    assert b.contracts[t].n_out_of_order == 1
    assert b.observation(t, B.HORIZON_NAMES.index("latest_pregame"))["yes_ask"] == 0.52


def test_jsonl_round_trip_with_field_selection(tmp_path):
    p = str(tmp_path / "x.jsonl.gz")
    assert B.write_jsonl_gz(p, [{"a": 1, "b": 2}, {"a": 3, "b": 4}]) == 2
    assert list(B.read_jsonl_gz(p, ("a",))) == [{"a": 1}, {"a": 3}]
