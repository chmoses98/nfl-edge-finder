"""The strategy replay cannot see the future, cannot fill at a midpoint, cannot count one game many times, and cannot be tuned
on its own test set -- provably, on synthetic data, without touching the network or a data branch."""
import copy
import inspect
import math
import os
from datetime import date, datetime, timedelta, timezone

import numpy as np
import polars as pl
import pytest

from nfl_edge.execution import fees as F
from nfl_edge.handicap import expression as EX
from nfl_edge.research import strategy_replay as SR

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T0 = 1_760_000_000.0                      # a decision timestamp (arbitrary, 2025-10)


@pytest.fixture(scope="module")
def fee_book():
    return SR.FeeBook(F.load_fee_schedule(ROOT))


# ------------------------------------------------------------------------------------------------ synthetic world
def _phi(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def synth_world(seed=0, seasons=(2022, 2023, 2024, 2025), weeks=10):
    """8 teams; team_game rows with the silver columns the ratings solver reads; a matching schedule with results."""
    rng = np.random.default_rng(seed)
    teams = list("ABCDEFGH")
    strength = {t: rng.normal(0, 0.1) for t in teams}
    rows, sched = [], {}
    for s in seasons:
        for w in range(1, weeks + 1):
            order = list(teams); rng.shuffle(order)
            gd = date(s, 9, 1) + timedelta(days=7 * (w - 1))
            kts = datetime(gd.year, gd.month, gd.day, 17, 0, tzinfo=timezone.utc).timestamp()
            for i in range(0, 8, 2):
                h, a = order[i], order[i + 1]
                gid = f"{s}_{w:02d}_{a}_{h}"
                diff = strength[h] - strength[a] + 0.03
                margin = float(np.round(40 * diff + rng.normal(0, 12)))
                if margin == 0:
                    margin = 1.0
                sched[gid] = {"game_id": gid, "season": s, "week": w, "game_type": "REG", "gameday": gd.isoformat(), "kickoff_ts": kts,
                              "home": h, "away": a, "home_score": 24 + margin / 2, "away_score": 24 - margin / 2, "result": margin,
                              "total": 48.0, "spread_line": float(np.round(40 * diff * 2) / 2), "total_line": 45.5, "overtime": 0, "neutral": False}
                for team, opp, is_home in ((h, a, True), (a, h, False)):
                    base = strength[team] - strength[opp] + (0.03 if is_home else -0.03)
                    rows.append({"season": s, "week": w, "game_id": gid, "team": team, "opp": opp, "is_home": is_home, "season_type": "REG",
                                 "off_epa_play": base + rng.normal(0, 0.15), "off_explosive_passes": int(rng.poisson(5)),
                                 "off_explosive_runs": int(rng.poisson(3)), "off_plays": 60, "off_sacks": int(rng.poisson(2)),
                                 "off_dropbacks": 35, "off_turnovers": int(rng.poisson(1.3))})
    return pl.DataFrame(rows), sched


def add_bank_games(sched, n_per_season=270, seasons=range(2016, 2026), seed=5):
    """Extra historical games (not in team_game) so the residual bank has a population."""
    rng = np.random.default_rng(seed)
    out = dict(sched)
    for s in seasons:
        for i in range(n_per_season):
            sl = float(np.round(rng.normal(0, 5) * 2) / 2)
            m = float(np.round(sl + rng.normal(0, 13)))
            t = float(np.round(45 + rng.normal(0, 10)))
            gid = f"bank_{s}_{i}"
            gd = date(s, 9, 1) + timedelta(days=int(i % 120))
            out[gid] = {"game_id": gid, "season": s, "week": 1 + i % 18, "game_type": "REG", "gameday": gd.isoformat(), "kickoff_ts": None,
                        "home": "X", "away": "Y", "home_score": None, "away_score": None, "result": m, "total": t,
                        "spread_line": sl, "total_line": 45.5, "overtime": 0, "neutral": False}
    return out


def synth_board(centre=-3.0, total=44.5, sd=13.0, *, home="H", away="V", season=2025, week=12, gameday="2025-11-23", width=0.02,
                decision_ts=T0, age=5.0, game_id="2025_12_V_H", obs_lag=300.0):
    """A coherent set of full-game rows around a market centre (home margin `centre`)."""
    rows = []

    def add(ticker, fam, subj, thr, p):
        p = min(max(p, 0.03), 0.97)
        bid = round(p - width / 2, 2)
        ask = round(bid + width, 2)
        rows.append(SR.make_row(ticker=ticker, family=fam, subject=subj, threshold=thr, bid=bid, ask=ask, obs_ts=decision_ts - obs_lag,
                                age_min=age, volume=10.0, game_id=game_id))

    add("KXNFLGAME-X-H", "GAME_WINNER", home, None, 1 - _phi((0.5 - centre) / sd))
    add("KXNFLGAME-X-V", "GAME_WINNER", away, None, _phi((-0.5 - centre) / sd))
    for x in (1.5, 2.5, 3.5, 4.5, 6.5, 7.5, 9.5, 10.5, 13.5):
        add(f"KXNFLSPREAD-X-H{x}", "SPREAD", home, x, 1 - _phi((x - centre) / sd))
        add(f"KXNFLSPREAD-X-V{x}", "SPREAD", away, x, _phi((-x - centre) / sd))
    for thr in (37, 40, 43, 46, 49, 52):
        add(f"KXNFLTOTAL-X-{thr}", "TOTAL", None, float(thr), 1 - _phi((thr - 0.5 - total) / 10.0))
    for team, c in ((home, (total + centre) / 2), (away, (total - centre) / 2)):
        for thr in (17, 20, 23, 26):
            add(f"KXNFLTEAMTOTAL-X-{team}{thr}", "TEAM_TOTAL", team, float(thr), 1 - _phi((thr - 0.5 - c) / 7.0))
    meta = {"game_id": game_id, "season": season, "week": week, "gameday": gameday, "home": home, "away": away, "kickoff_ts": decision_ts + 5400}
    return SR.make_board(meta, "T-90m", rows, decision_ts)


class StubCtx(SR.Context):
    """A Context whose rating-implied margin is fixed (the ratings themselves are tested separately)."""

    def __init__(self, m_r, *args, **kw):
        super().__init__(*args, **kw)
        self._m_r = m_r

    def rating_margin(self, board):
        return self._m_r, {"last_used_ts": board["decision_ts"] - 86400.0}


@pytest.fixture(scope="module")
def world():
    return synth_world()


@pytest.fixture(scope="module")
def stub_ctx_factory(fee_book, world):
    _tg, sched = world
    sched = add_bank_games(sched)

    def make(m_r, draws=4000):
        return StubCtx(m_r, fee_book=fee_book, sched=sched, rating_book=object(), draws=draws, engine=EX)

    return make


# ------------------------------------------------------------------------------------------------ pre-registration
def test_the_preregistered_parameters_are_the_ones_written_down_before_the_run():
    assert SR.PREREGISTERED["frozen_on"] == "2026-10-25"
    assert (SR.A_BAND, SR.B_MIN_NET_EDGE, SR.C_MIN_GAP, SR.D_GAP_CAP, SR.D_SHIFT_LOW_FRAC, SR.D_MIN_WIN_SCRIPTS) == ((0.60, 0.85), 0.05, 2.5, 5.0, 0.5, 3)
    assert (SR.E_MIN_NET_EDGE, SR.E_MAX_WIDTH, SR.MAX_WIDTH, SR.MAX_AGE_MIN, SR.PRIMARY_HORIZON, SR.ROBUSTNESS_HORIZON) == (0.02, 0.06, 0.10, 30.0, "T-90m", "T-24h")
    assert SR.RATING_HYPERPARAMS == {"halflife_games": 10.0, "season_carry": 0.4, "ridge": 4.0}
    assert SR.SEED == 20261025 and SR.DEV_LAST_WEEK_2025 == 9
    assert SR.E_MIN_NET_EDGE == EX.MIN_NET_EDGE


def test_the_split_is_chronological_and_the_map_trains_only_on_earlier_seasons():
    assert SR.blocks_for(2025, 9) == [SR.BLOCK_DEV, SR.BLOCK_ALL_2025]
    assert SR.blocks_for(2025, 10) == [SR.BLOCK_OOS_2025, SR.BLOCK_OOS, SR.BLOCK_ALL_2025]
    assert SR.blocks_for(2025, 22) == [SR.BLOCK_OOS_2025, SR.BLOCK_OOS, SR.BLOCK_ALL_2025]
    assert SR.blocks_for(2026, 3) == [SR.BLOCK_OOS_2026, SR.BLOCK_OOS]
    assert SR.blocks_for(2024, 3) == []
    for s in (2025, 2026):
        assert max(SR.train_seasons_for(s)) == s - 1 and len(SR.train_seasons_for(s)) == SR.MARGIN_MAP_SEASONS_BACK


# ------------------------------------------------------------------------------------------------ executable prices and fees
def test_fee_comes_from_the_schedule_not_a_hardcoded_formula(fee_book):
    ts = T0
    sched = fee_book.schedule
    for p in (0.15, 0.40, 0.62, 0.85):
        for series in ("KXNFLGAME", "KXNFLSPREAD", "KXNFLTOTAL", "KXNFLTEAMTOTAL"):
            q = sched.taker_fee(p, 100.0, series, as_of=SR.utc(ts))
            assert q.is_known
            assert fee_book.marginal(series, p, ts) == pytest.approx(q.amount / 100.0)
            assert fee_book.marginal(series, p, ts) == pytest.approx(0.07 * p * (1 - p), abs=0.0051)
    assert fee_book.one_contract("KXNFLGAME", 0.40, ts) == pytest.approx(0.02)       # one contract rounds UP to the cent


def test_a_book_is_executable_only_if_two_sided_tight_and_fresh():
    ok = SR.make_row(ticker="KXNFLGAME-X-H", family="GAME_WINNER", subject="H", threshold=None, bid=0.60, ask=0.65, obs_ts=T0, age_min=10.0)
    assert ok["executable"] and ok["no_ask"] == pytest.approx(0.40) and ok["no_bid"] == pytest.approx(0.35)
    assert not SR.make_row(ticker="t", family="SPREAD", subject="H", threshold=2.5, bid=0.50, ask=0.62, obs_ts=T0, age_min=1.0)["executable"]   # 12c wide
    assert not SR.make_row(ticker="t", family="SPREAD", subject="H", threshold=2.5, bid=0.0, ask=0.62, obs_ts=T0, age_min=1.0)["executable"]    # no bid
    assert not SR.make_row(ticker="t", family="SPREAD", subject="H", threshold=2.5, bid=0.50, ask=1.0, obs_ts=T0, age_min=1.0)["executable"]    # no ask
    assert not SR.make_row(ticker="t", family="SPREAD", subject="H", threshold=2.5, bid=0.60, ask=0.62, obs_ts=T0, age_min=45.0)["executable"]  # stale
    assert SR.make_row(ticker="t", family="SPREAD", subject="H", threshold=2.5, bid=0.55, ask=0.65, obs_ts=T0, age_min=1.0)["executable"]       # exactly 10c


def test_fills_are_at_the_ask_of_the_side_bought_never_the_midpoint(fee_book, stub_ctx_factory):
    ctx = stub_ctx_factory(0.0)
    yes = SR.make_row(ticker="KXNFLGAME-X-H", family="GAME_WINNER", subject="H", threshold=None, bid=0.60, ask=0.66, obs_ts=T0 - 60, age_min=1.0, game_id="g")
    no = SR.make_row(ticker="KXNFLGAME-X-V", family="GAME_WINNER", subject="V", threshold=None, bid=0.30, ask=0.36, obs_ts=T0 - 60, age_min=1.0, game_id="g")
    board = SR.make_board({"game_id": "g", "season": 2025, "week": 12, "gameday": "2025-11-23", "home": "H", "away": "V", "kickoff_ts": T0 + 5400},
                          "T-90m", [yes, no], T0)
    picks = SR.decide_A(board, ctx)
    assert len(picks) == 1
    p = picks[0]
    assert p["side"] == "NO" and p["ticker"] == "KXNFLGAME-X-V" or p["side"] == "YES"
    row = yes if p["ticker"] == yes["ticker"] else no
    expected_ask = row["yes_ask"] if p["side"] == "YES" else 1.0 - row["yes_bid"]
    assert p["ask"] == pytest.approx(expected_ask) and p["ask"] != pytest.approx(row["mid"])
    settled = SR.settle_pick(p, {"outcome": {p["ticker"]: 1.0 if p["side"] == "YES" else 0.0}, "ref": {}})
    assert settled["won"] == 1.0 and settled["ret"] == pytest.approx(1.0 - p["ask"] - p["fee"])
    lost = SR.settle_pick(p, {"outcome": {p["ticker"]: 0.0 if p["side"] == "YES" else 1.0}, "ref": {}})
    assert lost["ret"] == pytest.approx(-(p["ask"] + p["fee"]))


def test_strategy_A_buys_the_cheapest_side_in_the_band_and_nothing_outside_it(stub_ctx_factory):
    ctx = stub_ctx_factory(0.0)
    board = synth_board(centre=-6.0)
    picks = SR.decide_A(board, ctx)
    assert picks and len({p["family"] for p in picks}) == len(picks)                      # at most one per family
    for p in picks:
        assert SR.A_BAND[0] - 1e-9 <= p["ask"] <= SR.A_BAND[1] + 1e-9
        in_band = [a for r, s, a in SR.eligible_sides(board) if r["family"] == p["family"] and SR.A_BAND[0] - 1e-9 <= a <= SR.A_BAND[1] + 1e-9]
        assert p["ask"] == pytest.approx(min(in_band))
    # a board with nothing priced in the band -> no bet
    flat = synth_board(centre=0.0, sd=60.0)
    assert [p for p in SR.decide_A(flat, ctx) if not (SR.A_BAND[0] <= p["ask"] <= SR.A_BAND[1])] == []


# ------------------------------------------------------------------------------------------------ point in time
def test_tripwire_fails_if_any_quote_is_stamped_after_the_decision(stub_ctx_factory):
    board = synth_board()
    SR.assert_point_in_time(board)                                                       # clean board passes
    bad = copy.deepcopy(board)
    bad["rows"][3]["obs_ts"] = bad["decision_ts"] + 1.0
    with pytest.raises(SR.PointInTimeViolation):
        SR.assert_point_in_time(bad)
    with pytest.raises(SR.PointInTimeViolation):
        SR.decide_game(bad, stub_ctx_factory(3.0), ("A",))
    with pytest.raises(SR.PointInTimeViolation):
        SR.assert_point_in_time(board, [("ratings_last_game", board["decision_ts"] + 60)])


def test_tripwire_fails_if_a_pick_carries_a_future_feature(stub_ctx_factory):
    ctx = stub_ctx_factory(3.0)
    board = synth_board()
    row = board["rows"][0]
    with pytest.raises(SR.PointInTimeViolation):
        SR.make_pick("A", board, row, "YES", ctx, [row["obs_ts"], board["decision_ts"] + 10.0])


def test_the_loader_refuses_a_snapshot_stamped_after_the_decision():
    ko = 1_760_000_000.0
    mk = lambda ts: {"ticker": "KXNFLGAME-X-H", "series": "KXNFLGAME", "family": "GAME_WINNER", "period": "FULL", "team": "H", "threshold": None,
                     "game_id": "g1", "anchor_ts": ko, "anchor_kind": "kickoff", "result": "yes",
                     "snaps": {"T-90m": {"bid": 0.6, "ask": 0.62, "ts": ts, "age_min": 0.0, "vol": 1, "book_empty": False}}}
    sched = {"g1": {"game_id": "g1", "season": 2025, "week": 1, "gameday": "2025-09-07", "home": "H", "away": "V", "kickoff_ts": ko}}
    st = {}
    boards, _ = SR.build_boards_2025([mk(ko - 5400 + 1)], sched, "T-90m", st)           # one second late
    assert boards == {} and st["dropped_quote_after_decision"] == 1
    boards, _ = SR.build_boards_2025([mk(ko - 5400)], sched, "T-90m", {})
    assert list(boards) == ["g1"] and boards["g1"]["decision_ts"] == ko - 5400


def test_rows_anchored_on_the_close_time_are_excluded_not_trusted():
    r = {"ticker": "KXNFLGAME-X-H", "series": "KXNFLGAME", "family": "GAME_WINNER", "period": "FULL", "team": "H", "threshold": None,
         "game_id": "g1", "anchor_ts": 1.0, "anchor_kind": "close_time", "result": "yes", "snaps": {}}
    st = {}
    boards, ledger = SR.build_boards_2025([r], {"g1": {"game_id": "g1"}}, "T-90m", st)
    assert boards == {} and ledger == {} and st["dropped_no_kickoff_anchor"] == 1


def test_ratings_for_a_week_ignore_that_week_and_everything_after(world):
    tg, sched = world
    rb = SR.RatingBook(tg, sched)
    snap = rb.snapshot(2025, 6)
    assert snap["last_used_season_week"] < [2025, 6]
    future = tg.with_columns(pl.when((pl.col("season") > 2025) | ((pl.col("season") == 2025) & (pl.col("week") >= 6)))
                             .then(pl.col("off_epa_play") + 7.0).otherwise(pl.col("off_epa_play")).alias("off_epa_play"))
    snap2 = SR.RatingBook(future, sched).snapshot(2025, 6)
    assert snap["ratings"] == snap2["ratings"] and snap["hfa"] == snap2["hfa"]
    # ... and dropping the future rows altogether changes nothing either
    only_past = tg.filter((pl.col("season") < 2025) | ((pl.col("season") == 2025) & (pl.col("week") < 6)))
    assert SR.RatingBook(only_past, sched).snapshot(2025, 6)["ratings"] == snap["ratings"]
    # a snapshot DOES move when an EARLIER week changes (the test has power)
    earlier = tg.with_columns(pl.when((pl.col("season") == 2025) & (pl.col("week") == 5)).then(pl.col("off_epa_play") + 7.0)
                              .otherwise(pl.col("off_epa_play")).alias("off_epa_play"))
    assert SR.RatingBook(earlier, sched).snapshot(2025, 6)["ratings"] != snap["ratings"]
    assert snap["last_used_ts"] < min(g["kickoff_ts"] for g in sched.values() if g["season"] == 2025 and g["week"] == 6)


def test_the_margin_map_for_a_season_uses_only_earlier_seasons(world, fee_book):
    tg, sched = world

    def fit(s):
        return SR.Context(fee_book=fee_book, sched=s, rating_book=SR.RatingBook(tg, s)).margin_map(2025)

    base = fit(sched)
    later = copy.deepcopy(sched)
    for g in later.values():
        if g["season"] >= 2025:
            g["result"] = -g["result"] + 3.0
    assert fit(later) == base                                                            # 2025 results cannot move the 2025 map
    earlier = copy.deepcopy(sched)
    for g in earlier.values():
        if g["season"] == 2024:
            g["result"] = -g["result"]
    assert fit(earlier) != base                                                          # 2024 results can (the test has power)


def test_the_residual_bank_holds_only_games_played_on_an_earlier_date(world, fee_book):
    _tg, sched = world
    sched = add_bank_games(sched)
    ctx = SR.Context(fee_book=fee_book, sched=sched, rating_book=None)
    base = ctx.bank(2025, "2025-09-15")
    n = len(base.m)
    mutated = copy.deepcopy(sched)
    for g in mutated.values():
        if g["gameday"] >= "2025-09-15" and g["game_type"] == "REG":
            g["result"] = 99.0
    ctx2 = SR.Context(fee_book=fee_book, sched=mutated, rating_book=None)
    assert np.array_equal(ctx2.bank(2025, "2025-09-15").m, base.m) and n > 500
    assert len(ctx2.bank(2025, "2026-01-01").m) > n                                       # a later date sees more history


def test_a_boards_decision_inputs_carry_no_outcome_and_no_closing_price():
    board = synth_board()
    forbidden = {"y", "outcome", "result", "settled", "settled_yes", "won", "ref", "clv", "close", "close_mid", "kickoff_result"}
    assert not (set(board) & forbidden)
    for r in board["rows"]:
        assert not (set(r) & forbidden)
    assert "ledger" not in inspect.signature(SR.decide_game).parameters
    assert "ledger" not in inspect.signature(SR.decide_C).parameters
    assert "ledger" not in inspect.signature(SR.decide_DE).parameters


# ------------------------------------------------------------------------------------------------ no peeking at outcomes
def test_shuffling_future_settlements_cannot_change_a_single_decision(stub_ctx_factory):
    ctx = stub_ctx_factory(2.5)
    proj_rows = []
    boards, ledger = {}, {}
    rng = np.random.default_rng(3)
    for i, centre in enumerate((-6.0, -3.0, 1.0, 4.5, -9.5)):
        gid = f"2025_{12 + i}_V_H"
        b = synth_board(centre=centre, game_id=gid, week=12 + i)
        boards[gid] = b
        ledger[gid] = {"outcome": {r["ticker"]: float(rng.random() < 0.5) for r in b["rows"]},
                       "ref": {r["ticker"]: {"T-30m": r["mid"], "KO": r["mid"]} for r in b["rows"]}}
        for r in b["rows"]:
            proj_rows.append({"ticker": r["ticker"], "p_yes": min(0.95, max(0.05, r["mid"] + 0.09)), "support_state": "PRICED", "evidence_class": "PROSPECTIVE_FROZEN",
                              "generated_at": SR.utc(b["decision_ts"] - 1800).isoformat()})
    ctx.projections = SR.ProjectionIndex(proj_rows)
    base = SR.replay(boards, ledger, ctx)
    assert sum(len(v) for v in base["decisions"].values() for v in v.values()) > 0
    for seed in (1, 2, 3):
        shuf = copy.deepcopy(ledger)
        r2 = np.random.default_rng(seed)
        for gid, lg in shuf.items():
            keys = list(lg["outcome"])
            vals = [lg["outcome"][k] for k in keys]
            r2.shuffle(vals)
            lg["outcome"] = dict(zip(keys, vals))
        other = SR.replay(boards, shuf, ctx)
        assert other["decisions"] == base["decisions"]                                   # identical decisions ...
    flipped = copy.deepcopy(ledger)
    for lg in flipped.values():
        lg["outcome"] = {k: 1.0 - v for k, v in lg["outcome"].items()}
    out = SR.replay(boards, flipped, ctx)
    assert out["decisions"] == base["decisions"]
    ra = sum(p["ret"] for p in base["picks"]["A"]); rb = sum(p["ret"] for p in out["picks"]["A"])
    assert ra != rb                                                                      # ... but the settled returns do move


def test_future_projections_are_invisible_and_stale_ones_are_not_used():
    ix = SR.ProjectionIndex([
        {"ticker": "T", "p_yes": 0.40, "support_state": "PRICED", "evidence_class": "PROSPECTIVE_FROZEN", "generated_at": SR.utc(T0 - 3600).isoformat()},
        {"ticker": "T", "p_yes": 0.90, "support_state": "PRICED", "evidence_class": "PROSPECTIVE_FROZEN", "generated_at": SR.utc(T0 + 1).isoformat()},
        {"ticker": "U", "p_yes": 0.55, "support_state": "PROJECTABLE_NOT_YET_VALIDATED", "evidence_class": "PROSPECTIVE_FROZEN", "generated_at": SR.utc(T0 - 60).isoformat()},
        {"ticker": "S", "p_yes": 0.55, "support_state": "PRICED", "evidence_class": "PROSPECTIVE_FROZEN", "generated_at": SR.utc(T0 - 3 * 86400).isoformat()},
        {"ticker": "R", "p_yes": 0.55, "support_state": "PRICED", "evidence_class": "RETROSPECTIVE", "generated_at": SR.utc(T0 - 60).isoformat()},
    ])
    assert ix.lookup("T", T0)["p_yes"] == 0.40                                           # the projection generated one second later is not seen
    assert ix.lookup("T", T0 + 5)["p_yes"] == 0.90
    assert ix.lookup("U", T0) is None and ix.lookup("U", T0, ("PRICED", "PROJECTABLE_NOT_YET_VALIDATED")) is not None
    assert ix.lookup("S", T0) is None and ix.lookup("R", T0) is None


# ------------------------------------------------------------------------------------------------ strategies B and C
def test_strategy_B_requires_the_pre_registered_net_edge_and_may_buy_NO(stub_ctx_factory):
    ctx = stub_ctx_factory(0.0)
    board = synth_board(centre=-3.0)
    rows = {r["ticker"]: r for r in board["rows"]}
    t_yes, t_no = "KXNFLSPREAD-X-H2.5", "KXNFLSPREAD-X-V3.5"
    proj = [{"ticker": t_yes, "p_yes": rows[t_yes]["yes_ask"] + 0.12, "support_state": "PRICED", "evidence_class": "PROSPECTIVE_FROZEN",
             "generated_at": SR.utc(T0 - 600).isoformat()},
            {"ticker": t_no, "p_yes": rows[t_no]["yes_bid"] - 0.15, "support_state": "PRICED", "evidence_class": "PROSPECTIVE_FROZEN",
             "generated_at": SR.utc(T0 - 600).isoformat()},
            {"ticker": "KXNFLTOTAL-X-43", "p_yes": rows["KXNFLTOTAL-X-43"]["yes_ask"] + 0.03, "support_state": "PRICED",
             "evidence_class": "PROSPECTIVE_FROZEN", "generated_at": SR.utc(T0 - 600).isoformat()}]
    ctx.projections = SR.ProjectionIndex(proj)
    picks = SR.decide_B(board, ctx)
    spread = [p for p in picks if p["family"] == "SPREAD"]
    assert len(spread) == 1                                                              # one per family
    assert all(p["model_edge"] >= SR.B_MIN_NET_EDGE - 1e-9 for p in picks)
    assert not [p for p in picks if p["family"] == "TOTAL"]                              # a 3c disagreement is below the 5c bar once the fee is paid
    for p in picks:
        assert max(p["features_ts"]) <= board["decision_ts"]
    assert SR.decide_B(board, stub_ctx_factory(0.0)) == []                              # no projections -> no bet


def test_strategy_C_buys_the_side_the_ratings_favour_only_past_the_gap_threshold(stub_ctx_factory):
    board = synth_board(centre=-3.0)
    env = SR.ladder_env(board["rows"], "H", "V")
    assert env["home_margin"] == pytest.approx(-3.0, abs=0.35)
    assert env["total"] == pytest.approx(44.5, abs=0.8)
    # ratings like the HOME team 4 points more than the market does
    up = SR.decide_C(board, stub_ctx_factory(env["home_margin"] + 4.0))
    assert up["gap"] == pytest.approx(4.0) and len(up["C"]) == 1
    p = up["C"][0]
    row = next(r for r in board["rows"] if r["ticker"] == p["ticker"])
    assert row["family"] == "SPREAD" and (row["subject"] == "H") == (p["side"] == "YES")   # home-up: home YES or away NO
    # ... and the inverse control is the other side of the same contract
    assert up["C_INVERSE"][0]["ticker"] == p["ticker"] and up["C_INVERSE"][0]["side"] != p["side"]
    down = SR.decide_C(board, stub_ctx_factory(env["home_margin"] - 4.0))
    q = down["C"][0]
    qrow = next(r for r in board["rows"] if r["ticker"] == q["ticker"])
    assert (qrow["subject"] == "V") == (q["side"] == "YES")                              # away-up: away YES or home NO
    below = SR.decide_C(board, stub_ctx_factory(env["home_margin"] + 2.4))
    assert below["C"] == [] and below["skip"] == "GAP_BELOW_THRESHOLD"
    edge = SR.decide_C(board, stub_ctx_factory(env["home_margin"] + 2.5))
    assert len(edge["C"]) == 1                                                           # the threshold is inclusive
    # the rung chosen is the one nearest the market's main line
    chosen = abs(p["mid_side"] - 0.5)
    assert all(chosen <= abs(SR.side_mid(r, s) - 0.5) + 1e-9 for r, s, a in SR._direction_sides(board, "H", "V", True))


def test_strategies_D_and_E_choose_from_the_engine_and_E_is_a_stricter_subset_of_D(stub_ctx_factory):
    ctx = stub_ctx_factory(0.0, draws=6000)
    board = synth_board(centre=-3.0)
    env = SR.ladder_env(board["rows"], "H", "V")
    seen_d = 0
    for gap in (6.0, -6.0, 3.0):
        ctx._m_r = env["home_margin"] + gap
        c = SR.decide_C(board, ctx)
        de = SR.decide_DE(board, ctx, c)
        if de["D"]:
            seen_d += 1
            d = de["D"][0]
            assert d["winning_scripts"] >= SR.D_MIN_WIN_SCRIPTS and d["net_edge_low"] > 0
            assert SR.MIN_ASK <= d["ask"] <= SR.MAX_ASK
            assert max(d["features_ts"]) <= board["decision_ts"]
            assert d["shift_margin"][0] * d["shift_margin"][1] >= 0 and max(map(abs, d["shift_margin"])) <= SR.D_GAP_CAP + 1e-9
        if de["E"]:
            e = de["E"][0]
            assert (e["ticker"], e["side"]) == (de["D"][0]["ticker"], de["D"][0]["side"])
            assert e["net_edge_low"] >= SR.E_MIN_NET_EDGE - 1e-9 and e["width"] <= SR.E_MAX_WIDTH + 1e-9
    ctx._m_r = env["home_margin"] + 1.0
    none = SR.decide_DE(board, ctx, SR.decide_C(board, ctx))
    assert none["D"] == [] and none["E"] == [] and none["skip"] == "GAP_BELOW_THRESHOLD"
    # the thesis shift is the capped gap, as a range whose low end is the conservative half
    assert SR.thesis_shift(9.0)["home_margin"] == (2.5, 5.0) and SR.thesis_shift(-9.0)["home_margin"] == (-5.0, -2.5)
    assert SR.thesis_shift(3.0)["total"] == (0.0, 0.0)


def test_the_engine_contract_definitions_reproduce_settlement_from_the_score():
    board = synth_board()
    sched = {"2025_12_V_H": {"home_score": 27.0, "away_score": 20.0}}
    ledger = {"2025_12_V_H": {"outcome": {}, "ref": {}}}
    m, t, h, a = 7.0, 47.0, 27.0, 20.0
    for r in board["rows"]:
        if r["family"] == "GAME_WINNER":
            y = float((m > 0) if r["subject"] == "H" else (m < 0))
        elif r["family"] == "SPREAD":
            y = float((m if r["subject"] == "H" else -m) > r["threshold"])
        elif r["family"] == "TOTAL":
            y = float(t >= r["threshold"])
        else:
            y = float((h if r["subject"] == "H" else a) >= r["threshold"])
        ledger["2025_12_V_H"]["outcome"][r["ticker"]] = y
    chk = SR.check_settlement_semantics({"2025_12_V_H": board}, ledger, sched)
    assert chk["checked"] == len(board["rows"]) and chk["mismatched"] == 0
    ledger["2025_12_V_H"]["outcome"]["KXNFLSPREAD-X-H6.5"] = 0.0                          # a deliberately wrong settlement is caught
    assert SR.check_settlement_semantics({"2025_12_V_H": board}, ledger, sched)["mismatched"] == 1


# ------------------------------------------------------------------------------------------------ statistics
def _settled(gid, family, ask, fee, won, **kw):
    p = {"game_id": gid, "family": family, "ask": ask, "fee": fee, "won": won, "outlay": ask + fee, "ret": won - ask - fee, "gross_ret": won - ask,
         "clv_30m": kw.get("clv_30m"), "clv_ko": kw.get("clv_ko"), "season": 2025, "week": 12}
    return p


def test_a_game_is_one_observation_no_matter_how_many_contracts_it_has():
    picks = [_settled("g1", "SPREAD", 0.5, 0.02, 1.0), _settled("g1", "TOTAL", 0.5, 0.02, 1.0), _settled("g1", "GAME_WINNER", 0.7, 0.02, 1.0),
             _settled("g1", "TEAM_TOTAL", 0.6, 0.02, 1.0), _settled("g2", "SPREAD", 0.5, 0.02, 0.0)]
    obs = SR.per_game(picks)
    assert [o["game_id"] for o in obs] == ["g1", "g2"] and obs[0]["n_picks"] == 4
    assert obs[0]["ret"] == pytest.approx(np.mean([p["ret"] for p in picks[:4]]))        # the unit is split, not multiplied
    s = SR.summarize(obs, B=500)
    assert s["n_games"] == 2
    many = [_settled(f"g{i}", "SPREAD", 0.5, 0.02, float(i % 2)) for i in range(40)]
    s = SR.summarize(SR.per_game(many), B=500)
    assert s["n_games"] == 40 and s["roi"] == pytest.approx(-0.02 / 0.52, abs=1e-4)
    assert s["roi_ci95"][0] < s["roi"] < s["roi_ci95"][1]


def test_the_bootstrap_is_clustered_by_game_and_deterministic():
    picks = [_settled(f"g{i}", "SPREAD", 0.4 + 0.01 * (i % 7), 0.0, float(i % 3 == 0)) for i in range(30)]
    a = SR.summarize(SR.per_game(picks), B=800)
    b = SR.summarize(SR.per_game(picks), B=800)
    assert a == b
    c = SR.summarize(SR.per_game(picks), B=800, seed=SR.SEED + 1)
    assert a["roi"] == c["roi"] and a["roi_ci95"] is not None
    assert SR.bootstrap_roi_positive(SR.per_game(picks), B=800) == SR.bootstrap_roi_positive(SR.per_game(picks), B=800)


def test_clv_is_measured_on_the_side_bought_against_the_later_mid():
    pick = {"ticker": "t", "side": "NO", "ask": 0.40, "fee": 0.02}
    s = SR.settle_pick(pick, {"outcome": {"t": 0.0}, "ref": {"t": {"T-30m": 0.55, "KO": None}}})
    assert s["clv_30m"] == pytest.approx((1 - 0.55) - 0.40) and s["clv_ko"] is None and s["won"] == 1.0
    assert SR.settle_pick(pick, {"outcome": {}, "ref": {}}) is None                      # no settlement -> not scored


def test_evaluate_reports_games_not_contracts_and_splits_the_blocks():
    boards = {"g1": synth_board(game_id="g1", week=5), "g2": synth_board(game_id="g2", week=12)}
    boards["g1"]["season"] = boards["g2"]["season"] = 2025
    settled = {"A": [dict(_settled("g1", "SPREAD", 0.5, 0.02, 1.0), week=5), dict(_settled("g1", "TOTAL", 0.5, 0.02, 0.0), week=5),
                     dict(_settled("g2", "SPREAD", 0.5, 0.02, 1.0), week=12)]}
    ev = SR.evaluate(settled, boards, B=200)
    assert ev[SR.BLOCK_DEV]["A"]["ALL"]["n_games"] == 1 and ev[SR.BLOCK_DEV]["A"]["ALL"]["n_picks"] == 2
    assert ev[SR.BLOCK_OOS]["A"]["ALL"]["n_games"] == 1 and ev[SR.BLOCK_ALL_2025]["A"]["ALL"]["n_games"] == 2
    assert ev[SR.BLOCK_DEV]["A"]["SPREAD"]["n_games"] == 1 and ev[SR.BLOCK_DEV]["A"]["TEAM_TOTAL"]["n_games"] == 0


def test_replay_runs_end_to_end_on_a_synthetic_season(stub_ctx_factory):
    ctx = stub_ctx_factory(3.0)
    boards, ledger = {}, {}
    rng = np.random.default_rng(11)
    for i in range(6):
        gid = f"2025_{11 + i}_V_H"
        b = synth_board(centre=float(rng.normal(-2, 4)), game_id=gid, week=11 + i, gameday=f"2025-11-{10 + i}")
        boards[gid] = b
        ledger[gid] = {"outcome": {r["ticker"]: float(rng.random() < r["mid"]) for r in b["rows"]}, "ref": {}}
    res = SR.replay(boards, ledger, ctx, strategies=("A", "C", "D", "E"))
    ev = SR.evaluate(res["picks"], boards, B=200)
    assert ev[SR.BLOCK_OOS]["A"]["ALL"]["n_games"] > 0
    for s in ("A", "C", "D", "E", "C_INVERSE"):
        assert ev[SR.BLOCK_OOS][s]["ALL"]["n_games"] <= len(boards)
