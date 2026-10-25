"""HISTORICAL STRATEGY REPLAY: five ways of choosing a Kalshi full-game contract, replayed on settled history at an
EXECUTABLE price, after the Kalshi taker fee, with game-clustered uncertainty. RESEARCH ONLY. Nothing here promotes a model,
reads the owner's account, or has any authority over the pricer, the gates, the risk policy or staking.

THE QUESTION. Does any simple rule beat the market after fees, out of sample? The rules are:

    A  MARKET BASELINE      buy the cheapest side priced 0.60-0.85, per game-line family. Uses no football at all: it is
                            the control for the favourite-longshot pattern and for fee/spread drag.
    B  MODEL DISAGREEMENT   BOARD_V2's p_yes minus ask minus fee >= 5c. 2026 only (BOARD_V2 has no earlier history).
    C  MATCHUP-INFORMED     point-in-time opponent-adjusted EPA ratings (team_ratings.py) -> a rating-implied home margin
                            -> compared with the margin the market's own spread ladder implies. If |gap| >= 2.5 points,
                            buy the spread-ladder rung nearest the market's centre on the side the ratings favour.
    D  SCRIPT-ROBUST        C's gap, capped, becomes a shift of the market centre; the best-expression engine
                            (nfl_edge/handicap/expression.py over fairvalue.py, injected as `Context.engine`) chooses ANY full-game contract by
                            conservative edge per payoff-sd, requiring a win in >= 3 of the nine game scripts.
    E  CONSERVATIVE VALUE   D's pick, but only if its conservative net edge is >= 2.0c per contract and the book is <= 6c wide.

WHAT MAKES THE NUMBERS TRUSTWORTHY (every item is tested in tests/test_strategy_replay.py)

  * POINT IN TIME. A decision is made at a horizon (T-90m primary, T-24h robustness). Every quote it reads has an
    observation timestamp <= the decision timestamp; ratings are fitted on games from strictly EARLIER weeks; the rating->margin
    map is fitted on seasons strictly before the season being tested; the residual bank behind D/E holds only games played on an
    earlier date; BOARD_V2 probabilities must have been generated at or before the decision. `assert_point_in_time` is the
    tripwire. Decisions are computed from a `board` that carries no outcome and no closing price; outcomes live in a separate
    ledger that is only joined AFTER every decision is fixed.
  * EXECUTABLE PRICES. The side bought is paid at its ask (YES -> yes ask, NO -> 1 - yes bid). A midpoint is never a fill. A
    book must be two-sided, at most 10c wide (E: 6c) and its latest quote at most 30 minutes old.
  * FEES from config/kalshi_fee_schedule.json through `fees.FeeSchedule.taker_fee` (marginal fee of a 100-lot, per contract).
  * ONE OBSERVATION PER GAME. A game's contracts share one outcome. Each strategy places at most one flat unit per game and
    family; across families a game's unit is split equally among its picks. Intervals are bootstrap over GAMES.
  * PRE-REGISTERED PARAMETERS. Every threshold is a constant below, frozen on 2026-10-25 BEFORE the first replay was run. Any
    grid reported elsewhere is a POST-HOC sensitivity table and says so.

No wall clock, no network, no unseeded randomness in this module.
"""
from __future__ import annotations

import csv
import gzip
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import numpy as np

from nfl_edge.execution import fees as F
import nfl_edge.handicap.fairvalue as FV
from nfl_edge.pricing.game_env import ResidualBank
from nfl_edge.research import board as BD
from nfl_edge.research.board_miner import cluster_bootstrap_means, wilson

REPLAY_VERSION = "strategy-replay-1.0.0"

# ======================================================================================================
# PRE-REGISTERED CONSTANTS -- frozen 2026-10-25, before any strategy was replayed on any data.
# ======================================================================================================
SEED = 20261025
BOOTSTRAP_B = 4000
PRIMARY_HORIZON = "T-90m"
ROBUSTNESS_HORIZON = "T-24h"
HORIZON_MIN = {"T-24h": 24 * 60, "T-6h": 6 * 60, "T-90m": 90, "T-30m": 30}

MAX_WIDTH = 0.10             # a book wider than 10c is not a price
MAX_AGE_MIN = 30.0           # the quote used must have been confirmed within 30 minutes of the decision
MIN_ASK, MAX_ASK = 0.05, 0.95   # no 1-4c lottery tickets and no 96-99c "free money"; both are fee/rounding artefacts

A_BAND = (0.60, 0.85)        # strategy A: the side bought has an ask in this band
B_MIN_NET_EDGE = 0.05        # strategy B: model p - ask - fee >= 5c
B_MAX_PROJECTION_AGE_MIN = 240.0   # a BOARD_V2 projection older than 4h at the decision is not used
C_MIN_GAP = 2.5              # strategy C: |rating margin - market margin| >= 2.5 points
D_GAP_CAP = 5.0              # strategy D: the thesis shift is the gap capped at +-5 points ...
D_SHIFT_LOW_FRAC = 0.5       # ... as a RANGE [0.5 * gap, 1.0 * gap]; the low end is the conservative one
D_MIN_WIN_SCRIPTS = 3        # strategy D: the contract must win in >= 3 of the nine scripts
E_MIN_NET_EDGE = 0.02        # strategy E: conservative net edge >= 2.0c per contract (== expression.MIN_NET_EDGE)
E_MAX_WIDTH = 0.06           # strategy E: book <= 6c wide

RATING_HYPERPARAMS = {"halflife_games": 10.0, "season_carry": 0.4, "ridge": 4.0}   # the repo's DATA_ONLY research values
RATING_COLUMN = "off_epa_play"
RATING_SEASONS_BACK = 3      # team_ratings.snapshot_ratings' own window
MARGIN_MAP_SEASONS_BACK = 3  # the rating->margin map is fitted on the three seasons before the tested season
MIN_RATING_ROWS = 40

DEV_LAST_WEEK_2025 = 9       # 2025 weeks 1-9 are the development block; everything after is the held-out test
BLOCK_DEV, BLOCK_OOS_2025, BLOCK_OOS_2026 = "DEV_2025_wk1_9", "OOS_2025_wk10plus", "OOS_2026_wk1_5"
BLOCK_OOS = "OOS_pooled"
BLOCK_ALL_2025 = "ALL_2025"

FAMILIES = ("GAME_WINNER", "SPREAD", "TOTAL", "TEAM_TOTAL")
FAMILY_LABEL = {"GAME_WINNER": "moneyline", "SPREAD": "spread", "TOTAL": "total", "TEAM_TOTAL": "team total"}
SERIES_FAMILY = {"KXNFLGAME": "GAME_WINNER", "KXNFLSPREAD": "SPREAD", "KXNFLTOTAL": "TOTAL", "KXNFLTEAMTOTAL": "TEAM_TOTAL"}
STRATEGIES = ("A", "B", "C", "D", "E")
CONTROLS = ("C_INVERSE",)

#: the literal values above, pinned by a test so a later edit is a visible change to the pre-registration
PREREGISTERED = {
    "frozen_on": "2026-10-25", "seed": SEED, "primary_horizon": PRIMARY_HORIZON, "robustness_horizon": ROBUSTNESS_HORIZON,
    "max_width": MAX_WIDTH, "max_age_min": MAX_AGE_MIN, "ask_band": [MIN_ASK, MAX_ASK], "A_band": list(A_BAND),
    "B_min_net_edge": B_MIN_NET_EDGE, "B_max_projection_age_min": B_MAX_PROJECTION_AGE_MIN, "C_min_gap": C_MIN_GAP,
    "D_gap_cap": D_GAP_CAP, "D_shift_low_frac": D_SHIFT_LOW_FRAC, "D_min_win_scripts": D_MIN_WIN_SCRIPTS,
    "E_min_net_edge": E_MIN_NET_EDGE, "E_max_width": E_MAX_WIDTH, "rating_hyperparams": RATING_HYPERPARAMS,
    "rating_column": RATING_COLUMN, "margin_map_seasons_back": MARGIN_MAP_SEASONS_BACK, "dev_last_week_2025": DEV_LAST_WEEK_2025,
    "bootstrap_B": BOOTSTRAP_B,
}


class PointInTimeViolation(RuntimeError):
    """A feature carried a timestamp later than the decision it fed."""


# ======================================================================================================
# time and schedule
# ======================================================================================================
_ET = ZoneInfo("America/New_York")
TEAM_FIX = {"OAK": "LV", "SD": "LAC", "STL": "LA", "ARZ": "ARI", "AZ": "ARI", "BLT": "BAL", "CLV": "CLE", "HST": "HOU", "JAC": "JAX",
            "SL": "LA", "LAR": "LA", "WSH": "WAS"}


def _num(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(v) else v


def iso_ts(s):
    """ISO-8601 (or None) -> epoch seconds (UTC)."""
    if not s:
        return None
    d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    return (d if d.tzinfo else d.replace(tzinfo=timezone.utc)).timestamp()


def _et_date(ts) -> str:
    """The game's LOCAL (Eastern) calendar date, the same convention as the schedule's `gameday`."""
    return datetime.fromtimestamp(float(ts), tz=_ET).date().isoformat() if ts is not None else ""


def utc(ts: float) -> datetime:
    return datetime.fromtimestamp(float(ts), tz=timezone.utc)


def read_schedule(path: str) -> dict:
    """nflverse games.csv -> {game_id: row}. Team codes are normalised to the modern codes."""
    out = {}
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            try:
                season, week = int(r["season"]), int(r["week"])
            except (KeyError, TypeError, ValueError):
                continue
            ot = _num(r.get("overtime"))
            gd, gt = r.get("gameday") or "", (r.get("gametime") or "").strip() or "13:00"
            try:
                kts = datetime.strptime(f"{gd} {gt}", "%Y-%m-%d %H:%M").replace(tzinfo=_ET).timestamp()
            except ValueError:
                kts = None
            out[r["game_id"]] = {
                "game_id": r["game_id"], "season": season, "week": week, "game_type": r.get("game_type"), "gameday": gd,
                "kickoff_ts": kts, "home": TEAM_FIX.get(r["home_team"], r["home_team"]), "away": TEAM_FIX.get(r["away_team"], r["away_team"]),
                "home_score": _num(r.get("home_score")), "away_score": _num(r.get("away_score")), "result": _num(r.get("result")),
                "total": _num(r.get("total")), "spread_line": _num(r.get("spread_line")), "total_line": _num(r.get("total_line")),
                "overtime": int(ot) if ot is not None else 0, "neutral": (r.get("location") or "").strip().lower() == "neutral"}
    return out


# ======================================================================================================
# fees
# ======================================================================================================
class FeeBook:
    """Per-contract taker fee from the committed schedule, priced at the DECISION timestamp.

    `marginal` is the fee per contract of a 100-lot (the raw quadratic rounded to the cent over the order, which is what a
    multi-contract order converges to). `one_contract` is the worst case (a single contract rounded up to the cent)."""

    def __init__(self, schedule):
        self.schedule = schedule
        self._cache: dict = {}

    def _fee(self, series, price, as_of_ts, contracts):
        as_of = utc(as_of_ts)
        w = self.schedule.window_for(as_of) or {}
        key = (series, round(float(price), 4), contracts, w.get("effective_from"))
        if key not in self._cache:
            q = self.schedule.taker_fee(float(price), contracts, series, as_of=as_of)
            if not q.is_known:
                raise F.FeeStateError(f"fee for {series} at {price} is {q.state}: {q.reason}")
            self._cache[key] = q.amount / contracts
        return self._cache[key]

    def marginal(self, series, price, as_of_ts):
        return self._fee(series, price, as_of_ts, 100.0)

    def one_contract(self, series, price, as_of_ts):
        return self._fee(series, price, as_of_ts, 1.0)


# ======================================================================================================
# rows and boards
# ======================================================================================================
def series_of(ticker: str) -> str:
    return str(ticker).split("-", 1)[0]


def make_row(*, ticker, family, subject, threshold, bid, ask, obs_ts, age_min, volume=None, game_id=None):
    """One contract's top of book at a decision. `executable` is the single gate every strategy shares."""
    ok = (bid is not None and ask is not None and obs_ts is not None and age_min is not None
          and 0.01 <= bid < ask <= 0.99 and round(ask - bid, 4) <= MAX_WIDTH and age_min <= MAX_AGE_MIN)
    row = {"ticker": ticker, "series": series_of(ticker), "family": family, "period": "FULL", "subject": subject,
           "threshold": threshold, "game_id": game_id, "obs_ts": obs_ts, "age_min": age_min, "volume": volume,
           "yes_bid": bid, "yes_ask": ask, "executable": bool(ok), "no_real_market": False,
           "yes_meaning": f"{family} {subject or ''} {threshold if threshold is not None else ''}".strip()}
    if bid is not None and ask is not None:
        row.update(no_bid=round(1.0 - ask, 6), no_ask=round(1.0 - bid, 6), width=round(ask - bid, 6), mid=(bid + ask) / 2.0)
    else:
        row.update(no_bid=None, no_ask=None, width=None, mid=None)
    # the rung on the market's own scale (P(margin > x) for a spread, P(total > x) for a total / team total)
    if family == "SPREAD":
        row["rung"] = threshold
    elif family in ("TOTAL", "TEAM_TOTAL") and threshold is not None:
        row["rung"] = float(threshold) - 0.5
    else:
        row["rung"] = None
    return row


def make_board(meta: dict, horizon: str, rows: list, decision_ts: float) -> dict:
    return {"game_id": meta["game_id"], "season": meta["season"], "week": meta["week"], "gameday": meta["gameday"], "home": meta["home"],
            "away": meta["away"], "kickoff_ts": meta["kickoff_ts"], "horizon": horizon, "decision_ts": float(decision_ts),
            "rows": sorted(rows, key=lambda r: r["ticker"])}


def assert_point_in_time(board: dict, extra_ts=()):
    """THE TRIPWIRE. Every feature timestamp must be <= the decision timestamp. Raises PointInTimeViolation otherwise."""
    d = board["decision_ts"]
    for r in board["rows"]:
        if r.get("obs_ts") is not None and r["obs_ts"] > d + 1e-6:
            raise PointInTimeViolation(f"{board['game_id']} {r['ticker']}: quote observed at {r['obs_ts']} is after the decision {d}")
    for name, ts in extra_ts:
        if ts is not None and ts > d + 1e-6:
            raise PointInTimeViolation(f"{board['game_id']}: feature {name} stamped {ts} is after the decision {d}")


def block_of(season: int, week: int):
    if season == 2025:
        return BLOCK_DEV if week <= DEV_LAST_WEEK_2025 else BLOCK_OOS_2025
    if season == 2026:
        return BLOCK_OOS_2026
    return None


def blocks_for(season: int, week: int) -> list:
    b = block_of(season, week)
    out = [b] if b else []
    if b in (BLOCK_OOS_2025, BLOCK_OOS_2026):
        out.append(BLOCK_OOS)
    if season == 2025:
        out.append(BLOCK_ALL_2025)
    return out


def _good_ref_mid(bid, ask, age_min):
    if bid is None or ask is None or age_min is None or age_min > MAX_AGE_MIN:
        return None
    if not (0.01 <= bid < ask <= 0.99) or round(ask - bid, 4) > MAX_WIDTH:
        return None
    return (bid + ask) / 2.0


# ----------------------------------------------------------------------------------------- 2025 (backfill horizons)
def build_boards_2025(rows_iter, sched: dict, horizon: str, stats: dict | None = None):
    """2025 season: backfill/horizons rows -> ({game_id: board}, {game_id: ledger}).

    A snapshot is the book at the CLOSE of its candle period (`ts` = end_period_ts), so `ts` is the observation time. Rows
    anchored on the market's close time (no real kickoff) are excluded: their "T-0" is after the game."""
    st = stats if stats is not None else {}
    by_game: dict = defaultdict(list)
    ledger: dict = {}
    for r in rows_iter:
        fam = SERIES_FAMILY.get(r.get("series"))
        if fam is None or r.get("period") != "FULL":
            continue
        if r.get("anchor_kind") != "kickoff":
            st["dropped_no_kickoff_anchor"] = st.get("dropped_no_kickoff_anchor", 0) + 1
            continue
        if r.get("result") not in ("yes", "no"):
            st["dropped_unsettled"] = st.get("dropped_unsettled", 0) + 1
            continue
        gid = r.get("game_id")
        meta = sched.get(gid)
        if meta is None:
            st["dropped_game_not_in_schedule"] = st.get("dropped_game_not_in_schedule", 0) + 1
            continue
        ko = float(r["anchor_ts"])
        decision_ts = ko - HORIZON_MIN[horizon] * 60.0
        snaps = r.get("snaps") or {}
        lg = ledger.setdefault(gid, {"outcome": {}, "ref": {}})
        lg["outcome"][r["ticker"]] = 1.0 if r["result"] == "yes" else 0.0
        refs = {}
        for key, hz in (("T-30m", "T-30m"), ("KO", "T-0")):
            s = snaps.get(hz)
            if s and not s.get("book_empty"):
                refs[key] = _good_ref_mid(s.get("bid"), s.get("ask"), s.get("age_min"))
        lg["ref"][r["ticker"]] = refs
        s = snaps.get(horizon)
        if not s:
            st["no_snapshot_at_horizon"] = st.get("no_snapshot_at_horizon", 0) + 1
            continue
        if s.get("book_empty") or s.get("bid") is None or s.get("ask") is None:
            st["empty_or_null_book"] = st.get("empty_or_null_book", 0) + 1
            continue
        if s["ts"] is None or float(s["ts"]) > decision_ts + 1e-6:
            st["dropped_quote_after_decision"] = st.get("dropped_quote_after_decision", 0) + 1
            continue
        row = make_row(ticker=r["ticker"], family=fam, subject=r.get("team"), threshold=_num(r.get("threshold")), bid=float(s["bid"]),
                       ask=float(s["ask"]), obs_ts=float(s["ts"]), age_min=_num(s.get("age_min")), volume=_num(s.get("vol")), game_id=gid)
        if not row["executable"]:
            st["not_executable"] = st.get("not_executable", 0) + 1
        by_game[gid].append((row, ko))
    boards = {}
    for gid, items in by_game.items():
        meta = dict(sched[gid])
        meta["kickoff_ts"] = items[0][1]
        boards[gid] = make_board(meta, horizon, [x[0] for x in items], items[0][1] - HORIZON_MIN[horizon] * 60.0)
    return boards, ledger


# ----------------------------------------------------------------------------------------- 2026 (board research table)
def build_boards_2026(rows_iter, horizon: str, stats: dict | None = None):
    """2026: the model-free board table -> ({game_id: board}, {game_id: ledger}).

    `confirmed_at` (the capture run that last confirmed the book was still standing) is the observation time and
    `confirm_age_min` the staleness; `observed_at` is only the last price CHANGE and is often much older than the book."""
    st = stats if stats is not None else {}
    by_game: dict = defaultdict(list)
    meta: dict = {}
    ledger: dict = {}
    for r in rows_iter:
        fam = r.get("family")
        if fam not in FAMILIES or (r.get("period") or "FULL") != "FULL":
            continue
        gid = r.get("game_id")
        hz = r.get("horizon")
        lg = ledger.setdefault(gid, {"outcome": {}, "ref": {}})
        if hz == horizon:
            meta[gid] = {"game_id": gid, "season": int(r["season"]), "week": int(r["week"]), "gameday": _et_date(iso_ts(r.get("kickoff_utc"))),
                         "home": r.get("home_team"), "away": r.get("away_team"), "kickoff_ts": iso_ts(r.get("kickoff_utc"))}
        if r.get("settlement_status") == "SETTLED" and r.get("settled_yes") is not None:
            lg["outcome"][r["ticker"]] = float(r["settled_yes"])
        if hz in ("T-30m", "latest_pregame"):
            ok = r.get("obs_state") == "OBSERVED" and r.get("two_sided")
            mid = _good_ref_mid(_num(r.get("yes_bid")), _num(r.get("yes_ask")), _num(r.get("confirm_age_min"))) if ok else None
            lg["ref"].setdefault(r["ticker"], {})["T-30m" if hz == "T-30m" else "KO"] = mid
        if hz != horizon:
            continue
        if r.get("obs_state") != "OBSERVED":
            st["not_observed"] = st.get("not_observed", 0) + 1
            continue
        bid, ask = _num(r.get("yes_bid")), _num(r.get("yes_ask"))
        obs_ts, cutoff = iso_ts(r.get("confirmed_at") or r.get("observed_at")), iso_ts(r.get("cutoff_at"))
        if obs_ts is None or cutoff is None or obs_ts > cutoff + 1e-6:
            st["dropped_quote_after_decision"] = st.get("dropped_quote_after_decision", 0) + 1
            continue
        subj = r.get("subject_team") or r.get("team")
        row = make_row(ticker=r["ticker"], family=fam, subject=subj, threshold=_num(r.get("threshold")), bid=bid, ask=ask, obs_ts=obs_ts,
                       age_min=_num(r.get("confirm_age_min")), volume=_num(r.get("volume")), game_id=gid)
        if not row["executable"]:
            st["not_executable"] = st.get("not_executable", 0) + 1
        by_game[gid].append((row, cutoff))
    boards = {}
    for gid, items in by_game.items():
        boards[gid] = make_board(meta[gid], horizon, [x[0] for x in items], items[0][1])
    return boards, ledger


def merge_ledgers(*ledgers) -> dict:
    out: dict = {}
    for lg in ledgers:
        for gid, v in lg.items():
            o = out.setdefault(gid, {"outcome": {}, "ref": {}})
            o["outcome"].update(v["outcome"])
            for t, refs in v["ref"].items():
                o["ref"].setdefault(t, {}).update(refs)
    return out


# ======================================================================================================
# ratings, margin map, market centre
# ======================================================================================================
class RatingBook:
    """Point-in-time opponent-adjusted EPA ratings. A snapshot for (season, week) uses team-games from STRICTLY earlier weeks."""

    def __init__(self, team_game, sched: dict):
        from nfl_edge.research.team_ratings import prepare_rows
        self.rows = prepare_rows(team_game)
        self._ts = {}
        for g in sched.values():
            if g["kickoff_ts"] is not None:
                self._ts[g["game_id"]] = g["kickoff_ts"]
        self._cache: dict = {}

    def snapshot(self, season: int, week: int):
        import polars as pl
        from nfl_edge.research.team_ratings import solve_ratings
        key = (int(season), int(week))
        if key in self._cache:
            return self._cache[key]
        r = self.rows
        prior = r.filter(((pl.col("season") < season) | ((pl.col("season") == season) & (pl.col("week") < week)))
                         & (pl.col("season") >= season - RATING_SEASONS_BACK))
        out = None
        if prior.height >= MIN_RATING_ROWS:
            sol = solve_ratings(prior, RATING_COLUMN, cur_season=season, **RATING_HYPERPARAMS)
            if sol:
                gids = prior["game_id"].unique().to_list()
                last_ts = max((self._ts.get(g, 0.0) for g in gids), default=None)
                last_sw = prior.select(["season", "week"]).unique().sort(["season", "week"]).tail(1).row(0)
                out = {"season": season, "week": week, "ratings": sol["ratings"], "hfa": sol["hfa"], "n": sol["n"],
                       "last_used_ts": last_ts, "last_used_season_week": [int(last_sw[0]), int(last_sw[1])]}
        self._cache[key] = out
        return out

    @staticmethod
    def epa_diff(snap, home: str, away: str):
        """Expected home-minus-away EPA/play from the ratings (excluding home field): (o_h + d_a) - (o_a + d_h).
        The defence rating is EPA ALLOWED above average, so POSITIVE = WORSE defence and it is ADDED to the opposing offence."""
        if snap is None or home not in snap["ratings"] or away not in snap["ratings"]:
            return None
        oh, dh = snap["ratings"][home]
        oa, da = snap["ratings"][away]
        return (oh + da) - (oa + dh)


def fit_margin_map(samples):
    """OLS (no intercept) of the home margin on [EPA diff, non-neutral-site indicator]. samples: (diff, nonneutral, margin)."""
    X = np.array([[d, n] for d, n, _ in samples], float)
    y = np.array([m for _, _, m in samples], float)
    if len(y) < 50:
        return None
    A = X.T @ X + np.diag([1e-6, 1e-6])
    b = np.linalg.solve(A, X.T @ y)
    resid = y - X @ b
    return {"b_epa": float(b[0]), "hfa_points": float(b[1]), "n": int(len(y)), "rmse": float(np.sqrt(np.mean(resid ** 2))),
            "r2": float(1.0 - resid.var() / y.var()) if y.var() > 0 else None}


def train_seasons_for(season: int) -> tuple:
    return tuple(range(season - MARGIN_MAP_SEASONS_BACK, season))


class Context:
    """Everything a decision may read. It holds NO outcomes of the games being decided: the schedule's results are only reached
    through `margin_map` (seasons strictly before the tested season) and `bank` (games on an earlier date)."""

    def __init__(self, *, fee_book: FeeBook, sched: dict, rating_book: RatingBook | None = None, projections=None, draws: int = FV.DEFAULT_DRAWS,
                 engine=None):
        # `engine` is the best-expression module (nfl_edge.handicap.expression), INJECTED by the caller: this package is reachable from the
        # RUN NFL report path and may not import it (its import graph reaches the risk/store modules).
        self.fees, self.sched, self.ratings, self.projections, self.draws = fee_book, sched, rating_book, projections, draws
        self.engine = engine
        self._maps: dict = {}
        self._banks: dict = {}

    # -- rating -> margin map, fitted on earlier seasons only
    def margin_map(self, season: int):
        if season in self._maps:
            return self._maps[season]
        samples = []
        train = set(train_seasons_for(season))
        for g in self.sched.values():
            if g["season"] not in train or g["result"] is None:
                continue
            assert g["season"] < season
            d = RatingBook.epa_diff(self.ratings.snapshot(g["season"], g["week"]), g["home"], g["away"])
            if d is not None:
                samples.append((d, 0.0 if g["neutral"] else 1.0, g["result"]))
        self._maps[season] = fit_margin_map(samples)
        return self._maps[season]

    def rating_margin(self, board: dict):
        """(rating-implied home margin in points, the ratings snapshot) for a board's game, or (None, None)."""
        snap = self.ratings.snapshot(board["season"], board["week"])
        mp = self.margin_map(board["season"])
        d = RatingBook.epa_diff(snap, board["home"], board["away"])
        if snap is None or mp is None or d is None:
            return None, snap
        neutral = self.sched.get(board["game_id"], {}).get("neutral", False)
        return mp["b_epa"] * d + (0.0 if neutral else mp["hfa_points"]), snap

    # -- residual bank, built from games on an EARLIER DATE only
    def bank(self, season: int, gameday: str) -> ResidualBank:
        key = (season, gameday)
        if key not in self._banks:
            marg, tot, seas, sl, tl, ot, res = [], [], [], [], [], [], []
            for g in self.sched.values():
                if (g["game_type"] != "REG" or g["season"] < FV.BANK_SEASON_LO or g["result"] is None or g["spread_line"] is None
                        or g["total"] is None or g["total_line"] is None or not (g["gameday"] < gameday)):
                    continue
                marg.append(g["result"] - g["spread_line"]); tot.append(g["total"] - g["total_line"]); seas.append(float(g["season"]))
                sl.append(g["spread_line"]); tl.append(g["total_line"]); ot.append(g["overtime"]); res.append(g["result"])
            if len(marg) < 500:
                raise ValueError(f"only {len(marg)} bank games before {gameday}")
            self._banks[key] = ResidualBank(marg, tot, seas, ref_season=season, spread_lines=sl, total_lines=tl, overtime=ot, results=res,
                                            halflife=FV.BANK_HALFLIFE, rng=np.random.default_rng(FV.BANK_SEED))
        return self._banks[key]


def ladder_env(rows: list, home: str, away: str) -> dict:
    """The market's own centre from its executable ladders: home margin (spread rungs of both teams) and total (total rungs).
    Median of a monotone fit of the mid survival curve (the board's `median_from_survival`); no closing line is used."""
    mp, tp = [], []
    for r in rows:
        if not r["executable"] or r["rung"] is None:
            continue
        if r["family"] == "SPREAD" and r["subject"] in (home, away):
            mp.append((r["rung"], r["mid"]) if r["subject"] == home else (-r["rung"], 1.0 - r["mid"]))
        elif r["family"] == "TOTAL":
            tp.append((r["rung"], r["mid"]))
    return {"home_margin": BD.median_from_survival(mp), "total": BD.median_from_survival(tp), "n_spread_rungs": len(mp), "n_total_rungs": len(tp)}


# ======================================================================================================
# picks
# ======================================================================================================
def side_price(row: dict, side: str):
    return (row["yes_ask"], row["yes_bid"]) if side == "YES" else (row["no_ask"], row["no_bid"])


def side_mid(row: dict, side: str):
    return row["mid"] if side == "YES" else 1.0 - row["mid"]


def eligible_sides(board: dict, max_width: float = MAX_WIDTH):
    """(row, side, ask) for every executable contract side whose ask is in the tradable band."""
    for r in board["rows"]:
        if not r["executable"] or r["width"] > max_width + 1e-9:
            continue
        for side in ("YES", "NO"):
            ask = side_price(r, side)[0]
            if ask is not None and MIN_ASK - 1e-9 <= ask <= MAX_ASK + 1e-9:
                yield r, side, ask


def make_pick(strategy, board, row, side, ctx, features_ts, **extra) -> dict:
    ask, _ = side_price(row, side)
    fee = ctx.fees.marginal(row["series"], ask, board["decision_ts"])
    pick = {"strategy": strategy, "game_id": board["game_id"], "season": board["season"], "week": board["week"], "horizon": board["horizon"],
            "family": row["family"], "ticker": row["ticker"], "side": side, "ask": float(ask), "fee": float(fee), "mid_side": side_mid(row, side),
            "width": row["width"], "decision_ts": board["decision_ts"], "features_ts": [t for t in features_ts if t is not None]}
    pick.update(extra)
    # the tripwire runs on every pick: whatever fed it was stamped at or before the decision
    if pick["features_ts"] and max(pick["features_ts"]) > board["decision_ts"] + 1e-6:
        raise PointInTimeViolation(f"{board['game_id']} {strategy}: feature stamped {max(pick['features_ts'])} after decision {board['decision_ts']}")
    return pick


def decide_A(board, ctx, band=A_BAND) -> list:
    """Cheapest executable side priced in the band, one per family. Uses nothing but the book."""
    picks = []
    for fam in FAMILIES:
        cands = [(ask, r["ticker"], side, r) for r, side, ask in eligible_sides(board) if r["family"] == fam and band[0] - 1e-9 <= ask <= band[1] + 1e-9]
        if cands:
            ask, _t, side, r = min(cands, key=lambda c: (c[0], c[1], c[2]))
            picks.append(make_pick("A", board, r, side, ctx, [r["obs_ts"]]))
    return picks


def decide_B(board, ctx, min_edge=B_MIN_NET_EDGE, support=("PRICED",)) -> list:
    """BOARD_V2 disagreement: best side per family with p - ask - fee >= min_edge. 2026 only (needs `ctx.projections`)."""
    if ctx.projections is None:
        return []
    picks = []
    best: dict = {}
    for r, side, ask in eligible_sides(board):
        proj = ctx.projections.lookup(r["ticker"], board["decision_ts"], support)
        if proj is None:
            continue
        p = proj["p_yes"] if side == "YES" else 1.0 - proj["p_yes"]
        fee = ctx.fees.marginal(r["series"], ask, board["decision_ts"])
        edge = p - ask - fee
        if edge >= min_edge - 1e-12:
            k = (edge, -ask, r["ticker"], side)
            if r["family"] not in best or k > best[r["family"]][0]:
                best[r["family"]] = (k, r, side, proj, edge)
    for fam in FAMILIES:
        if fam in best:
            _k, r, side, proj, edge = best[fam]
            picks.append(make_pick("B", board, r, side, ctx, [r["obs_ts"], proj["generated_ts"]], model_p_yes=proj["p_yes"], model_edge=edge,
                                   support_state=proj["support_state"]))
    return picks


def _direction_sides(board, home, away, up_home: bool):
    """Spread (row, side, ask) whose event is 'home margin above a rung' (up_home) or 'home margin below a rung'."""
    for r, side, ask in eligible_sides(board):
        if r["family"] != "SPREAD" or r["subject"] not in (home, away):
            continue
        home_up = (r["subject"] == home) == (side == "YES")
        if home_up == up_home:
            yield r, side, ask


def decide_C(board, ctx, min_gap=C_MIN_GAP) -> dict:
    """Ratings vs the market's spread ladder. Returns {'gap', 'env', 'C', 'C_INVERSE', 'skip'} (picks are lists of 0 or 1)."""
    out = {"gap": None, "env": None, "C": [], "C_INVERSE": [], "skip": None, "snap": None}
    m_r, snap = ctx.rating_margin(board)
    out["snap"] = snap
    if m_r is None:
        out["skip"] = "NO_RATINGS"
        return out
    env = ladder_env(board["rows"], board["home"], board["away"])
    out["env"] = env
    if env["home_margin"] is None:
        out["skip"] = "NO_MARKET_CENTRE"
        return out
    gap = m_r - env["home_margin"]
    out["gap"] = gap
    if abs(gap) < min_gap:
        out["skip"] = "GAP_BELOW_THRESHOLD"
        return out
    cands = list(_direction_sides(board, board["home"], board["away"], up_home=gap > 0))
    if not cands:
        out["skip"] = "NO_SPREAD_RUNG"
        return out
    # the rung whose side-mid is nearest 50% (the market's main line); ties -> lower ticker
    ask, r, side = min(((a, rr, s) for rr, s, a in cands), key=lambda c: (abs(side_mid(c[1], c[2]) - 0.5), c[1]["ticker"], c[2]))
    fts = [r["obs_ts"], snap["last_used_ts"] if snap else None]
    out["C"] = [make_pick("C", board, r, side, ctx, fts, gap=gap, market_margin=env["home_margin"], rating_margin=m_r)]
    other = "NO" if side == "YES" else "YES"
    if side_price(r, other)[0] is not None and MIN_ASK <= side_price(r, other)[0] <= MAX_ASK:
        out["C_INVERSE"] = [make_pick("C_INVERSE", board, r, other, ctx, fts, gap=gap)]
    return out


def thesis_shift(gap: float) -> dict:
    g = max(-D_GAP_CAP, min(D_GAP_CAP, gap))
    lo, hi = sorted((D_SHIFT_LOW_FRAC * g, g))
    return {"home_margin": (round(lo, 4), round(hi, 4)), "total": (0.0, 0.0)}


def decide_DE(board, ctx, c_result: dict) -> dict:
    """D and E from C's thesis. Returns {'D': [pick], 'E': [pick], 'skip': reason|None, 'noise': ..., 'n_scanned': n}."""
    out = {"D": [], "E": [], "skip": None, "n_scanned": 0, "n_candidates": 0}
    gap, env, snap = c_result["gap"], c_result["env"], c_result["snap"]
    if c_result["skip"] in ("NO_RATINGS", "NO_MARKET_CENTRE") or gap is None:
        out["skip"] = c_result["skip"]
        return out
    if abs(gap) < C_MIN_GAP:
        out["skip"] = "GAP_BELOW_THRESHOLD"
        return out
    if env["total"] is None:
        out["skip"] = "NO_TOTAL_CENTRE"
        return out
    EX = ctx.engine
    if EX is None:
        out["skip"] = "NO_ENGINE"
        return out
    home, away = board["home"], board["away"]
    rows = [r for r in board["rows"] if r["executable"] and MIN_ASK - 1e-9 <= r["yes_ask"] <= 1 - MIN_ASK + 1e-9]
    bank = ctx.bank(board["season"], board["gameday"])
    gsim = FV.GameSim(bank, home, away, env["home_margin"], env["total"], draws=ctx.draws)
    noise = FV.baseline_check(rows, gsim.draw(0, 0), home, away)
    shift = thesis_shift(gap)
    as_of = utc(board["decision_ts"])
    evals = EX.scan_derivable(rows, gsim, shift, noise, ctx.fees.schedule, as_of, home, away)
    out["n_scanned"] = len(evals)
    by_ticker = {r["ticker"]: r for r in rows}
    cands = []
    for e in evals:
        r = by_ticker.get(e["ticker"])
        if r is None or not e.get("executable") or e.get("status") == "NO_DEFENSIBLE_FAIR_ESTIMATE":
            continue
        ask = e["ask"]
        if ask is None or not (MIN_ASK - 1e-9 <= ask <= MAX_ASK + 1e-9):
            continue
        nel = e.get("net_edge_low")
        rr = EX.risk_reward(e)
        if nel is None or rr is None or nel <= 0.0:
            continue
        if (e.get("scripts") or {}).get("winning_scripts", 0) < D_MIN_WIN_SCRIPTS:
            continue
        cands.append((rr, -e["width"], e["ticker"], e["side"], e, r))
    out["n_candidates"] = len(cands)
    if not cands:
        out["skip"] = "NO_EXPRESSION_CLEARS_D"
        return out
    rr, _w, _t, side, e, r = max(cands, key=lambda c: (c[0], c[1], c[2], c[3]))
    fts = [r["obs_ts"], snap["last_used_ts"] if snap else None]
    info = dict(gap=gap, shift_margin=list(shift["home_margin"]), net_edge_low=e["net_edge_low"], fair_low=e.get("fair_low"), fair_high=e.get("fair_high"),
                edge_per_sd=e.get("edge_per_sd"), winning_scripts=e["scripts"]["winning_scripts"], expression_family=r["family"])
    out["D"] = [make_pick("D", board, r, side, ctx, fts, **info)]
    if e["net_edge_low"] >= E_MIN_NET_EDGE - 1e-12 and r["width"] <= E_MAX_WIDTH + 1e-9:
        out["E"] = [make_pick("E", board, r, side, ctx, fts, **info)]
    return out


def decide_game(board: dict, ctx: Context, strategies=STRATEGIES) -> dict:
    """All strategies' picks for one board. NEVER receives an outcome. -> {'picks': {name: [pick]}, 'diag': {...}}"""
    assert_point_in_time(board)
    picks = {s: [] for s in tuple(strategies) + CONTROLS}
    diag = {}
    if "A" in strategies:
        picks["A"] = decide_A(board, ctx)
    if "B" in strategies:
        picks["B"] = decide_B(board, ctx)
    if any(s in strategies for s in ("C", "D", "E")) and ctx.ratings is not None:
        c = decide_C(board, ctx)
        diag["C"] = {k: c[k] for k in ("gap", "skip")} | {"env": c["env"]}
        if "C" in strategies:
            picks["C"], picks["C_INVERSE"] = c["C"], c["C_INVERSE"]
        if "D" in strategies or "E" in strategies:
            de = decide_DE(board, ctx, c)
            picks["D"], picks["E"] = de["D"], de["E"]
            diag["DE"] = {k: de[k] for k in ("skip", "n_scanned", "n_candidates")}
    for plist in picks.values():
        for p in plist:
            assert_point_in_time(board, [("pick_feature", t) for t in p["features_ts"]])
    return {"picks": picks, "diag": diag}


# ======================================================================================================
# settlement (AFTER the decisions) and statistics
# ======================================================================================================
def settle_pick(pick: dict, ledger_game: dict | None) -> dict | None:
    """Join the outcome and the closing references to a pick that is already fixed. None if the contract has no settled outcome."""
    if ledger_game is None or pick["ticker"] not in ledger_game["outcome"]:
        return None
    y = ledger_game["outcome"][pick["ticker"]]
    won = y if pick["side"] == "YES" else 1.0 - y
    refs = ledger_game["ref"].get(pick["ticker"], {})
    out = dict(pick)
    outlay = pick["ask"] + pick["fee"]
    out.update(won=won, outlay=outlay, ret=won - outlay, gross_ret=won - pick["ask"])
    for k in ("T-30m", "KO"):
        m = refs.get(k)
        out["clv_" + ("30m" if k == "T-30m" else "ko")] = None if m is None else (m if pick["side"] == "YES" else 1.0 - m) - pick["ask"]
    return out


def per_game(settled: list) -> list:
    """ONE observation per game: the game's unit stake is split equally across its picks (<= one per family)."""
    by: dict = defaultdict(list)
    for p in settled:
        by[p["game_id"]].append(p)
    obs = []
    for gid in sorted(by):
        ps = by[gid]
        k = len(ps)
        clv30 = [p["clv_30m"] for p in ps if p.get("clv_30m") is not None]
        clvko = [p["clv_ko"] for p in ps if p.get("clv_ko") is not None]
        obs.append({"game_id": gid, "n_picks": k, "ret": sum(p["ret"] for p in ps) / k, "outlay": sum(p["outlay"] for p in ps) / k,
                    "gross": sum(p["gross_ret"] for p in ps) / k, "ask": sum(p["ask"] for p in ps) / k, "fee": sum(p["fee"] for p in ps) / k,
                    "won": sum(p["won"] for p in ps) / k, "clv_30m": float(np.mean(clv30)) if clv30 else None,
                    "clv_ko": float(np.mean(clvko)) if clvko else None})
    return obs


def _mean_ci(vals, clusters, B, seed):
    v = np.asarray(vals, float)
    if len(v) < 2:
        return None
    b = cluster_bootstrap_means(v, np.ones_like(v), clusters, B=B, seed=seed)
    return None if b is None else [round(b["ci"][0], 5), round(b["ci"][1], 5)]


def summarize(obs: list, *, B: int = BOOTSTRAP_B, seed: int = SEED, n_eligible: int | None = None) -> dict:
    """ROI, mean return per unit, hit rate and CLV with game-clustered bootstrap intervals (one row of `obs` per game)."""
    n = len(obs)
    out = {"n_games": n, "n_games_eligible": n_eligible}
    if n == 0:
        return out
    ret = np.array([o["ret"] for o in obs]); outl = np.array([o["outlay"] for o in obs]); gross = np.array([o["gross"] for o in obs])
    ids = [o["game_id"] for o in obs]
    out.update(roi=round(float(ret.sum() / outl.sum()), 5), mean_return=round(float(ret.mean()), 5), gross_roi=round(float((gross).sum() / (outl - np.array([o["fee"] for o in obs])).sum()), 5),
               hit_rate=round(float(np.mean([o["won"] for o in obs])), 4), mean_ask=round(float(np.mean([o["ask"] for o in obs])), 4),
               mean_fee=round(float(np.mean([o["fee"] for o in obs])), 5), mean_outlay=round(float(outl.mean()), 4))
    b = cluster_bootstrap_means(ret, outl, ids, B=B, seed=seed)
    if b:
        out.update(roi_ci95=[round(b["roi_ci"][0], 5), round(b["roi_ci"][1], 5)], mean_return_ci95=[round(b["ci"][0], 5), round(b["ci"][1], 5)],
                   se_mean_return=round(b["se"], 5), prob_roi_positive=None)
    out["hit_rate_wilson95"] = [round(x, 4) for x in wilson(sum(o["won"] for o in obs), n)] if n else None
    for k in ("clv_30m", "clv_ko"):
        vals = [(o[k], o["game_id"]) for o in obs if o.get(k) is not None]
        out[k] = {"n": len(vals), "mean": round(float(np.mean([v for v, _ in vals])), 5) if vals else None,
                  "ci95": _mean_ci([v for v, _ in vals], [g for _, g in vals], B, seed) if vals else None}
    return out


def bootstrap_roi_positive(obs: list, *, B: int = BOOTSTRAP_B, seed: int = SEED):
    """Share of game-bootstrap replicates with ROI > 0 (a descriptive tail probability, not a p-value)."""
    n = len(obs)
    if n < 2:
        return None
    ret = np.array([o["ret"] for o in obs]); outl = np.array([o["outlay"] for o in obs])
    rng = np.random.default_rng(seed)
    W = rng.multinomial(n, np.full(n, 1.0 / n), size=B).astype(float)
    num, den = W @ ret, W @ outl
    return round(float(np.mean(num / den > 0)), 4)


# ======================================================================================================
# BOARD_V2 projections (strategy B) -- point-in-time lookup
# ======================================================================================================
class ProjectionIndex:
    """BOARD_V2 game-line projections by ticker, looked up as the LATEST one generated at or before the decision."""

    def __init__(self, rows):
        self._by: dict = defaultdict(list)
        for r in rows:
            gen = iso_ts(r.get("generated_at"))
            if gen is None or r.get("p_yes") is None or r.get("evidence_class") != "PROSPECTIVE_FROZEN":
                continue
            self._by[r["ticker"]].append((gen, r))
        for v in self._by.values():
            v.sort(key=lambda x: x[0])

    def lookup(self, ticker, decision_ts, support=("PRICED",), max_age_min=B_MAX_PROJECTION_AGE_MIN):
        best = None
        for gen, r in self._by.get(ticker, ()):
            if gen > decision_ts + 1e-6:
                break
            if r.get("support_state") in support:
                best = (gen, r)
        if best is None or (decision_ts - best[0]) / 60.0 > max_age_min:
            return None
        return {"p_yes": float(best[1]["p_yes"]), "generated_ts": best[0], "support_state": best[1].get("support_state"),
                "age_min": (decision_ts - best[0]) / 60.0}


def compact_projection(r: dict):
    """A BOARD_V2 projection record -> the few fields the replay uses (game-line FULL families with a probability)."""
    if r.get("market_family") not in FAMILIES or r.get("period") != "FULL" or r.get("p_yes") is None:
        return None
    ms = r.get("market_state") or {}
    out = {k: r.get(k) for k in ("ticker", "game_id", "market_family", "p_yes", "p_yes_low", "p_yes_high", "support_state", "generated_at",
                                 "data_cutoff", "horizon_label", "evidence_class", "yes_bid", "yes_ask", "observed_at", "snapshot_id", "model_arm")}
    out["yes_ask_size"], out["yes_bid_size"] = ms.get("yes_ask_size"), ms.get("yes_bid_size")
    return out


# ======================================================================================================
# the replay driver
# ======================================================================================================
def replay(boards: dict, ledger: dict, ctx: Context, strategies=STRATEGIES, *, progress=None) -> dict:
    """Decide every board FIRST (no ledger in sight), then settle. -> {'picks': {strategy: [settled]}, 'diag': {game: ...}}"""
    decided = {}
    for i, gid in enumerate(sorted(boards)):
        decided[gid] = decide_game(boards[gid], ctx, strategies)
        if progress and i % 25 == 0:
            progress(i, len(boards))
    settled: dict = {s: [] for s in tuple(strategies) + CONTROLS}
    unsettled = 0
    for gid, d in decided.items():
        for s, plist in d["picks"].items():
            for p in plist:
                sp = settle_pick(p, ledger.get(gid))
                if sp is None:
                    unsettled += 1
                else:
                    settled[s].append(sp)
    return {"picks": settled, "diag": {gid: d["diag"] for gid, d in decided.items()}, "unsettled_picks": unsettled,
            "decisions": {gid: {s: [(p["ticker"], p["side"]) for p in pl] for s, pl in d["picks"].items()} for gid, d in decided.items()}}


def evaluate(settled_by_strategy: dict, boards: dict, *, B=BOOTSTRAP_B, seed=SEED, with_tail=True) -> dict:
    """{block: {strategy: {family|'ALL': summary}}} from settled picks."""
    out: dict = {}
    eligible = defaultdict(lambda: defaultdict(set))       # block -> family -> games with a board having an executable row of the family
    for gid, b in boards.items():
        for blk in blocks_for(b["season"], b["week"]):
            eligible[blk]["ALL"].add(gid)
            for fam in {r["family"] for r in b["rows"] if r["executable"]}:
                eligible[blk][fam].add(gid)
    for strat, plist in settled_by_strategy.items():
        for blk in sorted(eligible):
            in_blk = [p for p in plist if blk in blocks_for(p["season"], p["week"])]
            cells = {}
            for fam in ("ALL",) + FAMILIES:
                sub = in_blk if fam == "ALL" else [p for p in in_blk if p["family"] == fam]
                obs = per_game(sub)
                cell = summarize(obs, B=B, seed=seed, n_eligible=len(eligible[blk][fam]))
                cell["n_picks"] = len(sub)
                if with_tail and obs:
                    cell["prob_roi_positive"] = bootstrap_roi_positive(obs, B=B, seed=seed)
                cells[fam] = cell
            out.setdefault(blk, {})[strat] = cells
    return out


# ======================================================================================================
# diagnostics
# ======================================================================================================
def check_settlement_semantics(boards: dict, ledger: dict, sched: dict) -> dict:
    """Does the engine's contract definition (fairvalue.contract_event) reproduce Kalshi's settlement from the final score?"""
    n = bad = skipped = 0
    for gid, b in boards.items():
        g = sched.get(gid)
        lg = ledger.get(gid)
        if not g or g["home_score"] is None or lg is None:
            skipped += 1
            continue
        m = g["home_score"] - g["away_score"]
        t = g["home_score"] + g["away_score"]
        sim = {"margin": np.array([m]), "total": np.array([t]), "home": np.array([g["home_score"]]), "away": np.array([g["away_score"]])}
        for r in b["rows"]:
            if r["ticker"] not in lg["outcome"]:
                continue
            ev, _ = FV.contract_event(r, sim, b["home"], b["away"])
            if ev is None:
                skipped += 1
                continue
            n += 1
            bad += int(float(ev[0]) != lg["outcome"][r["ticker"]])
    return {"checked": n, "mismatched": bad, "skipped": skipped}


def information_test(ctx: Context, seasons, *, min_gap=C_MIN_GAP) -> dict:
    """DESCRIPTIVE (not executable): do the ratings carry information beyond the CLOSING spread? For each season, the map is fitted on
    the three seasons before it, and the gap (rating margin - closing spread_line) is regressed on the result's miss of that line.
    Uses the schedule's closing line, which is only legitimate here because nothing is traded on it."""
    out = {}
    for season in seasons:
        mp = ctx.margin_map(season)
        xs, ys, hit = [], [], []
        for g in ctx.sched.values():
            if g["season"] != season or g["result"] is None or g["spread_line"] is None:
                continue
            d = RatingBook.epa_diff(ctx.ratings.snapshot(g["season"], g["week"]), g["home"], g["away"])
            if d is None or mp is None:
                continue
            m_r = mp["b_epa"] * d + (0.0 if g["neutral"] else mp["hfa_points"])
            gap = m_r - g["spread_line"]
            miss = g["result"] - g["spread_line"]
            xs.append(gap); ys.append(miss)
            if abs(gap) >= min_gap and miss != 0:
                hit.append(1.0 if (gap > 0) == (miss > 0) else 0.0)
        x, y = np.array(xs), np.array(ys)
        if len(x) < 30:
            out[str(season)] = {"n_games": int(len(x))}
            continue
        beta = float((x * y).sum() / (x * x).sum())
        resid = y - beta * x
        se = float(np.sqrt((x ** 2 * resid ** 2).sum()) / (x * x).sum())      # heteroskedasticity-robust, one row per game
        out[str(season)] = {"n_games": int(len(x)), "slope_of_miss_on_gap": round(beta, 4), "se": round(se, 4),
                            "corr": round(float(np.corrcoef(x, y)[0, 1]), 4), "n_big_gap_games": len(hit),
                            "big_gap_cover_rate": round(float(np.mean(hit)), 4) if hit else None,
                            "big_gap_cover_wilson95": [round(v, 4) for v in wilson(sum(hit), len(hit))] if hit else None,
                            "map_train_seasons": list(train_seasons_for(season)), "map": mp}
    return out


def read_jsonl(path):
    op = gzip.open if str(path).endswith(".gz") else open
    with op(path, "rt") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)
