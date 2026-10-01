"""THE FULL-BOARD RETROSPECTIVE RESEARCH TABLE: every eligible pregame NFL Kalshi contract, at every canonical
horizon, joined to its settlement, its fee, its ladder and its game environment. RESEARCH ONLY.

Why a third table. The arm evaluations cover the five full-game families the incumbent prices (3,665 latest-
pregame contracts, Weeks 1-3); the Shadow v2 research export is one row per (projection, ARM, snapshot) and is
built per week before the week has settled. Neither answers "what did the whole BOARD teach us", which is a
question about the MARKET, not about one of our models: one row per CONTRACT per HORIZON, whatever we priced.

SOURCES (all read-only, all already immutable on `market-data`):

    capture quotes      data/kalshi/capture/<day>/<run>.quotes.jsonl     the RAW SNAPSHOTS (change-suppressed)
    capture manifests   data/kalshi/capture/<day>/<run>.manifest.json    per-series completeness + instants
    capture state       data/kalshi/capture/state.json                    last run each ticker was seen open
    discovery           data/kalshi/discovery/<run>/markets/*.json        static terms + the exchange's settlement
    nflverse            schedules, player stats, snap counts, play-by-play (period scores)

HORIZONS. The repo's canonical set: T-24h, T-6h, T-90m, T-30m and latest_pregame. The observation at a horizon
is the contract's state at that INSTANT -- the last price change strictly before the cutoff -- confirmed by the
same rule the canonical close uses (`nfl_edge/evaluation/close.py`, close-2.1.0): the last capture run strictly
before the cutoff that fetched the contract's series and in which the contract was still open. latest_pregame
IS that rule with cutoff = kickoff, so the latest-pregame row of a contract is its canonical close. One
observation per contract per horizon, never a repeated snapshot; quality tiers are cut on the confirmation age
exactly as the close's are, and an observation confirmed more than 24 hours earlier is not an observation.

Repeated snapshots are not independent observations: they stay in the capture (raw) and are counted per contract
(`n_pregame_snapshots`), but only the five canonical horizons become rows.

SETTLEMENT. Football first, through the production engines: `settle_v2.settle_projection` on the question the
production semantics engine reads from the market (`semantics.question_from_market` over the discovery record),
which itself defers to the incumbent `settle.settle_observation` for player statistics. A contract that engine
refuses is never given a payout from football; when the EXCHANGE has terminally settled it, the row carries the
exchange's result in a separate tier (`settlement_source = EXCHANGE_TERMINAL`) and the canonical analysis keeps
the two tiers apart. A football settlement that the exchange contradicts is flagged, never overwritten.

NOTHING HERE HAS AUTHORITY. The table feeds research reports and RUN NFL context tags; it is not read by the
pricer, the gates, the risk policy, the preflight or the staking code, and a test pins that.

MEMORY. One streaming pass over the capture in run order. Per contract the builder keeps one compact last-row
tuple and at most five horizon tuples; rows of games outside the requested weeks are rejected by a substring
test before any JSON is parsed. Output rows are assembled one game at a time and written as they are built.
"""
from __future__ import annotations

import bisect
import gzip
import json
import math
import os
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

BOARD_VERSION = "board-research-1.0.0"

HORIZONS = (("T-24h", 24 * 60), ("T-6h", 6 * 60), ("T-90m", 90), ("T-30m", 30), ("latest_pregame", 0))
HORIZON_NAMES = tuple(h for h, _ in HORIZONS)
PRIMARY_HORIZON = "latest_pregame"

# confirmation-age tiers: the canonical close's own (close.py), named once here for the horizon generalisation
TIER_EXCELLENT_S = 20 * 60
TIER_GOOD_S = 90 * 60
TIER_STALE_S = 24 * 3600
EXCELLENT, GOOD, STALE, MISSING = "EXCELLENT", "GOOD", "STALE", "MISSING"
STATUS_OPEN = ("active", "open", None, "")
TERMINAL_STATUSES = ("finalized", "settled")

# observation states (one per contract x horizon)
OBS_OK = "OBSERVED"
OBS_NOT_LISTED = "NOT_LISTED_YET"              # no quote row strictly before the cutoff
OBS_NOT_OPEN = "NOT_OPEN_AT_HORIZON"           # last row before the cutoff is not an open market, or close_time passed
OBS_UNCONFIRMED = "UNCONFIRMED_AT_HORIZON"     # no capture run confirms the price within 24h of the cutoff

# settlement tiers
SRC_FOOTBALL = "FOOTBALL_PROVEN"
SRC_EXCHANGE = "EXCHANGE_TERMINAL"
SRC_NONE = "UNSETTLED"

# Fixed research bands. Named once; a change is a visible edit, never a tuning.
PRICE_BANDS = tuple(round(x / 10, 1) for x in range(11))           # 0-10c ... 90-100c
SPREAD_BANDS = ((3.0, "fav<3"), (7.0, "fav3-7"), (10.0, "fav7-10"), (float("inf"), "fav10+"))
TOTAL_BANDS = ((41.0, "total<41"), (45.0, "total41-45"), (49.0, "total45-49"), (float("inf"), "total49+"))
TEAM_TOTAL_BANDS = ((17.0, "tt<17"), (21.0, "tt17-21"), (24.0, "tt21-24"), (27.0, "tt24-27"), (float("inf"), "tt27+"))
MOVE_BANDS = ((-0.05, "down>5c"), (-0.02, "down2-5c"), (0.02, "flat"), (0.05, "up2-5c"), (float("inf"), "up>5c"))
DISAGREEMENT_BANDS = ((0.02, "<2pp"), (0.05, "2-5pp"), (0.10, "5-10pp"), (float("inf"), ">10pp"))
GAME_FAMILIES = ("GAME_WINNER", "SPREAD", "TOTAL", "TEAM_TOTAL", "BOTH_TEAMS_SCORE_N")


# ------------------------------------------------------------------------------------------------------ small
def _f(x):
    try:
        return None if x is None or x == "" else float(x)
    except (TypeError, ValueError):
        return None


def _dt(s):
    if not s:
        return None
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        try:
            d = datetime.strptime(str(s), "%Y%m%dT%H%M%SZ")
        except ValueError:
            return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _ts(s):
    d = _dt(s)
    return d.timestamp() if d else None


def _iso(ts):
    return None if ts is None else datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def band(v, bands, unknown="unknown"):
    v = _f(v)
    if v is None:
        return unknown
    for lim, name in bands:
        if v <= lim:
            return name
    return bands[-1][1]


def price_band(p) -> str:
    p = _f(p)
    if p is None:
        return "unknown"
    i = min(max(int(p * 10 + 1e-9), 0), 9)
    return f"{i * 10:02d}-{(i + 1) * 10:02d}c"


def quality_tier(age_s):
    if age_s is None:
        return MISSING
    if age_s <= TIER_EXCELLENT_S:
        return EXCELLENT
    if age_s <= TIER_GOOD_S:
        return GOOD
    if age_s <= TIER_STALE_S:
        return STALE
    return MISSING


# ------------------------------------------------------------------------------------------------------ games
class Game:
    __slots__ = ("game_id", "season", "week", "home", "away", "gameday", "kickoff", "ko_ts", "cutoffs")

    def __init__(self, game_id, season, week, home, away, gameday, kickoff_utc):
        self.game_id, self.season, self.week = game_id, int(season), int(week)
        self.home, self.away, self.gameday = home, away, gameday
        self.kickoff = _dt(kickoff_utc)
        self.ko_ts = self.kickoff.timestamp()
        self.cutoffs = tuple(self.ko_ts - m * 60.0 for _h, m in HORIZONS)   # aligned with HORIZONS


def games_from_schedule(schedule_games, *, season: int, weeks) -> dict:
    """Game objects for the requested weeks from `results.games_from_schedule_text` output (kickoff required)."""
    out = {}
    wk = set(int(w) for w in weeks)
    for g in schedule_games:
        if g.season == season and g.week in wk and g.kickoff_utc:
            out[g.game_id] = Game(g.game_id, g.season, g.week, g.home_team, g.away_team,
                                  g.kickoff_utc[:10], g.kickoff_utc)
    return out


# ------------------------------------------------------------------------------------------------------ manifests
class ManifestIndex:
    """Per series, the capture runs that fetched it, sorted by the series' own observation instant. The same
    information `close.CaptureRuns` scans linearly; indexed here because the board asks it ~250k times."""

    def __init__(self):
        self._by_series = defaultdict(list)       # series -> [(obs_ts, run_id, complete, partial_run)]
        self.n_manifests = 0
        self._sorted = False

    def add(self, manifest: dict):
        self.n_manifests += 1
        run_id = manifest.get("run_id")
        partial = bool(manifest.get("partial"))
        fin = manifest.get("finished_at")
        for series, s in (manifest.get("series") or {}).items():
            obs = _ts(s.get("observed_at")) or _ts(fin)
            if obs is None:
                continue
            self._by_series[series].append((obs, str(run_id), bool(s.get("complete")), partial))
        self._sorted = False

    def _sort(self):
        if not self._sorted:
            for v in self._by_series.values():
                v.sort()
            self._sorted = True

    def confirmation(self, series: str, cutoff_ts: float, last_seen_run: str | None = None):
        """(obs_ts, run_id, complete) of the last run strictly before the cutoff that fetched the series and
        did not post-date the contract's last sighting; None if there is none (close.py semantics)."""
        self._sort()
        rows = self._by_series.get(series)
        if not rows:
            return None
        i = bisect.bisect_left(rows, (cutoff_ts,)) - 1
        while i >= 0:
            obs, run_id, complete, _partial = rows[i]
            if last_seen_run is None or run_id <= last_seen_run:
                return obs, run_id, complete
            i -= 1
        return None


# ------------------------------------------------------------------------------------------------------ builder
# compact raw-snapshot tuple: (ts, run_id, status, yes_bid, yes_ask, no_bid, no_ask, volume, open_interest,
#                              liquidity, last_price, close_time_ts)
TS, RUN, STATUS, YB, YA, NB, NA, VOL, OI, LIQ, LAST, CLOSE_T = range(12)
STATIC_FIELDS = ("ticker", "event_ticker", "series_ticker", "family", "period", "stat", "team", "player_name",
                 "player_kalshi_id", "threshold", "operator", "floor_strike", "game_id", "strike_type", "cap_strike",
                 "custom_strike")


def compact(row: dict) -> tuple:
    return (_ts(row.get("observed_at")), row.get("run_id"), row.get("status"),
            _f(row.get("yes_bid_dollars")), _f(row.get("yes_ask_dollars")), _f(row.get("no_bid_dollars")),
            _f(row.get("no_ask_dollars")), _f(row.get("volume_fp")), _f(row.get("open_interest_fp")),
            _f(row.get("liquidity_dollars")), _f(row.get("last_price_dollars")), _ts(row.get("close_time")))


class Contract:
    __slots__ = ("static", "last", "first_ts", "n_pregame", "n_postgame", "n_out_of_order", "obs")

    def __init__(self, static):
        self.static = static
        self.last = None
        self.first_ts = None
        self.n_pregame = self.n_postgame = self.n_out_of_order = 0
        self.obs = [None] * len(HORIZONS)


class BoardBuilder:
    """One streaming pass over the capture. Feed quote files in run order (`feed_quote_lines`), manifests in any
    order (`manifests.add`), then call `finalize()`."""

    def __init__(self, games: dict):
        self.games = games
        self.contracts: dict[str, Contract] = {}
        self.manifests = ManifestIndex()
        self.last_seen: dict = {}
        self.needles = tuple(sorted({f"{g.season}_{g.week:02d}_" for g in games.values()}))
        self.stats = Counter()

    def feed_quote_lines(self, lines):
        games, contracts, needles = self.games, self.contracts, self.needles
        for line in lines:
            self.stats["lines"] += 1
            if not any(n in line for n in needles):
                continue
            try:
                row = json.loads(line)
            except ValueError:
                self.stats["unparseable_lines"] += 1
                continue
            g = games.get(row.get("game_id"))
            if g is None:
                continue
            t = row.get("ticker")
            q = compact(row)
            if q[TS] is None:
                self.stats["rows_without_observed_at"] += 1
                continue
            c = contracts.get(t)
            if c is None:
                c = contracts[t] = Contract({k: row.get(k) for k in STATIC_FIELDS})
            if q[TS] >= g.ko_ts:
                c.n_postgame += 1
                continue
            if c.last is not None and q[TS] < c.last[TS]:
                c.n_out_of_order += 1          # an older row arriving late can never be the state at a later cutoff
                continue
            # every horizon whose cutoff this row passes is fixed at the PREVIOUS state (strictly before cutoff)
            for i, cut in enumerate(g.cutoffs):
                if c.obs[i] is None and cut <= q[TS] and c.last is not None:
                    c.obs[i] = c.last
            if c.first_ts is None:
                c.first_ts = q[TS]
            c.last = q
            c.n_pregame += 1

    def finalize(self):
        """Horizons not passed by a later row take the last pregame row (it was still the state at the cutoff)."""
        for c in self.contracts.values():
            g = self.games[c.static["game_id"]]
            for i, cut in enumerate(g.cutoffs):
                if c.obs[i] is None and c.last is not None and c.last[TS] < cut:
                    c.obs[i] = c.last

    # ---- one observation record, with the close rule's confirmation --------------------------------
    def observation(self, ticker: str, h: int) -> dict:
        c = self.contracts[ticker]
        g = self.games[c.static["game_id"]]
        cut = g.cutoffs[h]
        q = c.obs[h]
        out = {"horizon": HORIZONS[h][0], "cutoff_at": _iso(cut)}
        if q is None:
            out["obs_state"] = OBS_NOT_LISTED
            out["obs_reason"] = ("first quote after this horizon" if c.first_ts is not None else "no pregame quote at all")
            return out
        series = c.static.get("series_ticker") or ticker.rsplit("-", 2)[0]
        conf = self.manifests.confirmation(series, cut, self.last_seen.get(ticker))
        conf_ts = conf[0] if conf else None
        age = (cut - conf_ts) if conf_ts is not None else None
        out.update({"observed_at": _iso(q[TS]), "run_id": q[RUN], "status": q[STATUS],
                    "price_age_min": round((cut - q[TS]) / 60.0, 2), "confirmed_at": _iso(conf_ts),
                    "confirm_run_id": conf[1] if conf else None, "series_complete": conf[2] if conf else None,
                    "confirm_age_min": round(age / 60.0, 2) if age is not None else None, "quality": quality_tier(age),
                    "yes_bid": q[YB], "yes_ask": q[YA], "no_bid": q[NB], "no_ask": q[NA], "volume": q[VOL],
                    "open_interest": q[OI], "liquidity": q[LIQ], "last_price": q[LAST]})
        yb, ya = q[YB], q[YA]
        out["mid"] = (yb + ya) / 2.0 if (yb is not None and ya is not None) else None
        out["width"] = (ya - yb) if (yb is not None and ya is not None) else None
        out["two_sided"] = bool(yb is not None and ya is not None and yb > 0.0 and ya < 1.0)
        if q[STATUS] not in STATUS_OPEN or (q[CLOSE_T] is not None and q[CLOSE_T] <= cut):
            out["obs_state"], out["obs_reason"] = OBS_NOT_OPEN, f"status {q[STATUS]!r} / close_time {_iso(q[CLOSE_T])}"
        elif out["quality"] == MISSING:
            out["obs_state"] = OBS_UNCONFIRMED
            out["obs_reason"] = "no capture run confirms this price within 24h of the cutoff" if conf else "series never confirmed before the cutoff"
        else:
            out["obs_state"], out["obs_reason"] = OBS_OK, None
        return out


# ------------------------------------------------------------------------------------------------------ fees
class FeeCache:
    """The committed fee schedule (`execution/fees.py`) applied at the OBSERVATION time, cached per
    (series, price in cents, window). Two numbers: the marginal per-contract fee of a large taker order (the raw
    quadratic, which a multi-contract order converges to through the accumulator) and the one-contract fee
    (rounded up to the cent, the worst case). Research returns use the marginal fee; both are on the row."""

    def __init__(self, schedule):
        self.schedule = schedule
        self._cache = {}

    def fee(self, series: str, price, as_of_ts: float) -> dict:
        p = _f(price)
        if p is None or not (0.0 < p < 1.0):
            return {"fee_marginal": None, "fee_one": None, "fee_state": "NO_PRICE"}
        as_of = datetime.fromtimestamp(as_of_ts, tz=timezone.utc)
        w = self.schedule.window_for(as_of) or {}
        key = (series, round(p, 4), w.get("effective_from"))
        hit = self._cache.get(key)
        if hit is not None:
            return hit
        big = self.schedule.taker_fee(p, 100.0, series, as_of=as_of)
        one = self.schedule.taker_fee(p, 1.0, series, as_of=as_of)
        out = {"fee_marginal": (big.amount / 100.0) if big.is_known else None,
               "fee_one": one.amount if one.is_known else None,
               "fee_state": big.state, "fee_window": w.get("effective_from")}
        self._cache[key] = out
        return out


# ------------------------------------------------------------------------------------------------------ settlement
def exchange_record(m: dict | None) -> dict:
    """The exchange's TERMINAL settlement from a discovery market record, or why there is none."""
    if not m:
        return {"exchange_state": "NOT_IN_DISCOVERY"}
    st, res = (m.get("status") or "").lower(), (m.get("result") or "").lower()
    if st not in TERMINAL_STATUSES:
        return {"exchange_state": f"NOT_TERMINAL:{st or 'unknown'}"}
    if res == "yes":
        return {"exchange_state": "TERMINAL", "exchange_yes": 1.0, "exchange_result": "yes"}
    if res == "no":
        return {"exchange_state": "TERMINAL", "exchange_yes": 0.0, "exchange_result": "no"}
    if res == "scalar":
        v = _f(m.get("settlement_value_dollars"))
        if v is not None and 0.0 <= v <= 1.0:
            return {"exchange_state": "TERMINAL", "exchange_yes": v, "exchange_result": "scalar"}
        return {"exchange_state": "TERMINAL_SCALAR_WITHOUT_VALUE"}
    return {"exchange_state": f"TERMINAL_RESULT_{res or 'EMPTY'}"}


def football_settlement(static: dict, disc_market: dict | None, book, period_book, player_map: dict) -> dict:
    """Settle one contract from football evidence through the production engines, or refuse with the reason."""
    from nfl_edge.semantics.questions import question_from_market
    from nfl_edge.settlement import settle_v2 as S2
    from nfl_edge.shadow_v2.capture_io import static_market
    m = static_market(static, {static["ticker"]: disc_market} if disc_market else {})
    try:
        _sem, q = question_from_market(m)
    except Exception as e:  # noqa: BLE001 -- a parser fault is a refusal, never a crash of the table
        return {"settlement_status": "REFUSED_SEMANTICS", "settlement_reason": f"parser error: {e}",
                "semantic_confidence": "UNKNOWN", "question_kind": None, "question_engine": None}
    gsis = player_map.get(static.get("player_kalshi_id")) if static.get("player_kalshi_id") else None
    rec = {"question": q.to_dict(), "market_family": static.get("family"), "period": static.get("period") or "FULL",
           "game_id": static.get("game_id"), "semantic_confidence": q.semantic_confidence,
           "stat_family": static.get("stat"), "subject_id": gsis if static.get("family") == "PLAYER_STAT" else q.subject,
           "subject_name": static.get("player_name")}
    ex = exchange_record(disc_market)
    scalar = ex.get("exchange_yes") if ex.get("exchange_result") == "scalar" else None
    if static.get("family") == "PLAYER_STAT" and gsis is None:
        s_status, s_yes, s_kind, s_reason = "REFUSED_PLAYER_IDENTITY", None, None, "the Kalshi player was never resolved to a GSIS id"
    else:
        try:
            s = S2.settle_projection(rec, book, period_book, exact_scalar_payout=scalar,
                                     exact_scalar_source="discovery terminal record" if scalar is not None else None,
                                     exact_scalar_unavailable_reason=None if scalar is not None else ex.get("exchange_state"))
            s_status, s_yes, s_kind, s_reason = s.status, s.settled_yes, s.kind, s.reason
        except Exception as e:  # noqa: BLE001 -- refusal, not a crash
            s_status, s_yes, s_kind, s_reason = "REFUSED_ENGINE_ERROR", None, None, f"{type(e).__name__}: {e}"
    return {"settlement_status": s_status, "settled_yes_football": s_yes, "settlement_kind": s_kind,
            "settlement_reason": s_reason, "semantic_confidence": q.semantic_confidence,
            "question_kind": q.kind, "question_engine": q.engine, "question_stat": q.stat,
            "question_subject": q.subject, "question_op": q.op, "question_k": q.k, "question_lo": q.lo,
            "question_hi": q.hi, "player_gsis_id": gsis, **ex}


def resolve_settlement(fs: dict) -> dict:
    """Which payout the row carries and from which tier. A football refusal is never filled from a price; the
    exchange's terminal result fills it only in its own tier, and a disagreement is flagged, never resolved."""
    fy, ey = fs.get("settled_yes_football"), fs.get("exchange_yes")
    if fs.get("settlement_status") == "SETTLED" and fy is not None:
        agree = None if ey is None else abs(float(fy) - float(ey)) < 1e-9
        return {"settled_yes": float(fy), "settlement_source": SRC_FOOTBALL, "exchange_agrees": agree,
                "binary_outcome": fs.get("settlement_kind") == "binary"}
    if ey is not None:
        return {"settled_yes": float(ey), "settlement_source": SRC_EXCHANGE, "exchange_agrees": None,
                "binary_outcome": float(ey) in (0.0, 1.0)}
    return {"settled_yes": None, "settlement_source": SRC_NONE, "exchange_agrees": None, "binary_outcome": False}


# ------------------------------------------------------------------------------------------------------ ladders
def ladder_key(static: dict) -> tuple:
    """Contracts that are rungs of one continuous outcome: same game, family, period, subject and statistic."""
    return (static.get("game_id"), static.get("family"), static.get("period") or "FULL",
            static.get("team") or "", static.get("player_kalshi_id") or "", static.get("stat") or "")


def rung_value(static: dict):
    """The rung's strike on the ladder's own scale (threshold for '>=', floor for '>')."""
    if static.get("operator") == ">" and _f(static.get("floor_strike")) is not None:
        return _f(static.get("floor_strike"))
    return _f(static.get("threshold"))


def pav_decreasing(points):
    """Pool-adjacent-violators: the closest non-increasing sequence (survival curves never rise)."""
    blocks = []
    for x, y in sorted(points):
        blocks.append([x, x, y, 1.0])
        while len(blocks) > 1 and blocks[-2][2] < blocks[-1][2]:
            a, b = blocks[-2], blocks.pop()
            n = a[3] + b[3]
            a[2] = (a[2] * a[3] + b[2] * b[3]) / n
            a[1], a[3] = b[1], n
    out = []
    for lo, hi, y, n in blocks:
        xs = [x for x, _ in sorted(points) if lo <= x <= hi]
        out.extend((x, y) for x in xs)
    return out


def median_from_survival(points):
    """Where P(X >= x) (or > x) crosses 0.5, linearly interpolated over a monotone fit; None if it never does."""
    pts = pav_decreasing([(x, p) for x, p in points if x is not None and p is not None])
    if len(pts) < 2:
        return None
    for (x0, p0), (x1, p1) in zip(pts, pts[1:]):
        if p0 >= 0.5 >= p1 and p0 != p1:
            return x0 + (p0 - 0.5) * (x1 - x0) / (p0 - p1)
    return None


def game_environment(rows_at_h: list, game: Game) -> dict:
    """Market-implied environment at one horizon from the board's own FULL-game ladders: home margin (spread
    ladders of both teams + nothing else), total, and each team's points. Ladder medians over two-sided mids;
    no consensus-line fallback, because the schedule's line is a CLOSING number and would leak into earlier
    horizons."""
    margin_pts, total_pts, tt = [], [], {game.home: [], game.away: []}
    for st, ob in rows_at_h:
        if (st.get("period") or "FULL") != "FULL" or ob.get("obs_state") != OBS_OK or not ob.get("two_sided"):
            continue
        fam, x, p = st.get("family"), rung_value(st), ob.get("mid")
        if x is None or p is None:
            continue
        if fam == "SPREAD" and st.get("team") in (game.home, game.away):
            margin_pts.append((x, p) if st["team"] == game.home else (-x, 1.0 - p))
        elif fam == "TOTAL":
            total_pts.append((x, p))
        elif fam == "TEAM_TOTAL" and st.get("team") in tt:
            tt[st["team"]].append((x, p))
    m = median_from_survival(margin_pts)
    t = median_from_survival(total_pts)
    th, ta = median_from_survival(tt[game.home]), median_from_survival(tt[game.away])
    if th is None and m is not None and t is not None:
        th = (t + m) / 2.0
    if ta is None and m is not None and t is not None:
        ta = (t - m) / 2.0
    fav = None if m is None or abs(m) < 1e-9 else (game.home if m > 0 else game.away)
    return {"env_home_margin": m, "env_total": t, "env_home_points": th, "env_away_points": ta, "env_favorite": fav,
            "env_spread_abs": abs(m) if m is not None else None, "env_spread_band": band(abs(m) if m is not None else None, SPREAD_BANDS),
            "env_total_band": band(t, TOTAL_BANDS), "env_source": "board ladder medians" if (m is not None or t is not None) else "UNAVAILABLE",
            "env_n_spread_rungs": len(margin_pts), "env_n_total_rungs": len(total_pts)}


def ladder_structure(rows_at_h: list) -> dict:
    """ticker -> {ladder id, rung index, number of rungs, main rung, distance from main line} at one horizon.
    The main ("headline") rung is the two-sided rung whose mid is closest to 0.5."""
    groups = defaultdict(list)
    for st, ob in rows_at_h:
        groups[ladder_key(st)].append((st, ob))
    out = {}
    for key, rs in groups.items():
        rungs = sorted(((rung_value(st), st["ticker"], ob) for st, ob in rs), key=lambda r: (r[0] is None, r[0] or 0.0, r[1]))
        live = [r for r in rungs if r[0] is not None and r[2].get("obs_state") == OBS_OK and r[2].get("two_sided") and r[2].get("mid") is not None]
        main = min(live, key=lambda r: (abs(r[2]["mid"] - 0.5), r[0])) if live else None
        lid = "|".join(str(k) for k in key)
        mids = [(r[0], r[2]["mid"]) for r in live]
        viol = sum(1 for (x0, p0), (x1, p1) in zip(mids, mids[1:]) if p1 > p0 + 1e-9)
        for i, (x, t, ob) in enumerate(rungs):
            d = (x - main[0]) if (main is not None and x is not None) else None
            out[t] = {"ladder_id": lid, "ladder_n_rungs": len(rungs), "ladder_n_live_rungs": len(live), "rung_index": i,
                      "main_rung_threshold": main[0] if main else None, "is_main_rung": bool(main and t == main[1]),
                      "distance_from_main": d,
                      "rung_offset": (i - next(j for j, r in enumerate(rungs) if r[1] == main[1])) if main else None,
                      "ladder_monotone_violations": viol}
    return out


def rung_offset_band(off) -> str:
    if off is None:
        return "unknown"
    if off == 0:
        return "main"
    if abs(off) == 1:
        return "adjacent+1" if off > 0 else "adjacent-1"
    return "far+" if off > 0 else "far-"


# ------------------------------------------------------------------------------------------------------ role / context
def role_certainty(p_plays, n_prior) -> str:
    """A transparent proxy, not a model: HIGH needs P(plays) >= 0.9 and >= 8 prior games of usage history;
    LOW is P(plays) < 0.75 or < 4 prior games; MEDIUM otherwise; UNKNOWN without the inputs."""
    p, n = _f(p_plays), _f(n_prior)
    if p is None and n is None:
        return "UNKNOWN"
    if (p is not None and p < 0.75) or (n is not None and n < 4):
        return "LOW"
    if (p is not None and p >= 0.9) and (n is not None and n >= 8):
        return "HIGH"
    return "MEDIUM"


class TimedIndex:
    """key -> rows sorted by an information instant; `at_or_before(key, cutoff)` = latest row strictly before
    the cutoff. Used for the research-context joins so a T-24h row never sees a T-30m model reading."""

    def __init__(self):
        self._d = defaultdict(list)

    def add(self, key, ts, payload):
        if ts is not None:
            self._d[key].append((ts, payload))

    def freeze(self):
        for v in self._d.values():
            v.sort(key=lambda r: r[0])
        return self

    def before(self, key, cutoff_ts):
        rows = self._d.get(key)
        if not rows:
            return None
        i = bisect.bisect_left(rows, (cutoff_ts,)) - 1
        while i >= 0 and rows[i][0] >= cutoff_ts:
            i -= 1
        return rows[i][1] if i >= 0 else None


def arm_contract_index(rows) -> TimedIndex:
    """ticker -> the three-arm probabilities known at each snapshot (observation AND snapshot generation must
    precede the cutoff; the arm record's run time is its generation)."""
    ix = TimedIndex()
    for r in rows:
        if (r.get("arm_status") or {}).get("DATA_ONLY") != "OK":
            continue
        ts = max(t for t in (_ts(r.get("observed_at")), _ts(r.get("run_id"))) if t is not None) if (r.get("observed_at") or r.get("run_id")) else None
        ix.add(r.get("ticker"), ts, {"p_data_only": r.get("p_data_only"), "p_hybrid": r.get("p_hybrid"), "p_current": r.get("p_current")})
    return ix.freeze()


def arm_game_index(rows) -> TimedIndex:
    ix = TimedIndex()
    for r in rows:
        arms = r.get("arms") or {}
        do = arms.get("DATA_ONLY") or {}
        if do.get("status") != "OK":
            continue
        ts = max(t for t in (_ts(r.get("observed_at")), _ts(r.get("run_id"))) if t is not None) if (r.get("observed_at") or r.get("run_id")) else None
        hy = arms.get("HYBRID_30_DATA") or {}
        ix.add(r.get("game_id"), ts, {"data_only_margin_minus_market": do.get("margin_minus_market"),
                                      "data_only_total_minus_market": do.get("total_minus_market"),
                                      "hybrid_margin_minus_market": hy.get("margin_minus_market"),
                                      "hybrid_total_minus_market": hy.get("total_minus_market")})
    return ix.freeze()


def anatomy_index(rows) -> TimedIndex:
    """ticker -> the incumbent player projection known before the cutoff. Only rows COMPUTED before kickoff
    (player_autopsy.generated_pregame) are admitted, for the reason autopsy-1.1.0 gives."""
    from nfl_edge.shadow.pregame_time import generated_at, generated_pregame
    ix = TimedIndex()
    for r in rows:
        if r.get("anatomy_status", "OK") != "OK" or not generated_pregame(r):
            continue
        ts = max(t for t in (_ts(r.get("observed_at")), generated_at(r).timestamp()) if t is not None)
        ix.add(r.get("ticker"), ts, {"model_cv": r.get("ledger_contract_value", r.get("model_contract_value")),
                                     "p_plays": r.get("p_plays"), "availability_state": r.get("availability_state"),
                                     "feature_n_prior": r.get("feature_n_prior"),
                                     "proj_opportunity": r.get("projected_opportunity_mean"),
                                     "proj_stat_mean": r.get("projected_stat_mean"),
                                     "proj_p50": (r.get("model_quantiles") or {}).get("p50")})
    return ix.freeze()


# ------------------------------------------------------------------------------------------------------ rows
def side_return(settled_yes, ask, fee):
    """Fee-adjusted hypothetical return of one contract bought at the ask (payout - price - fee), None when any
    input is missing. Not profit: no size, no fill risk, no CLV claim."""
    if settled_yes is None or ask is None or fee is None or not (0.0 < ask < 1.0):
        return None
    return float(settled_yes) - float(ask) - float(fee)


def assemble_game(builder: BoardBuilder, game: Game, settlements: dict, fees: FeeCache, *, positions=None,
                  arm_contracts: TimedIndex | None = None, arm_games: TimedIndex | None = None,
                  anatomy: TimedIndex | None = None, player_map: dict | None = None):
    """Yield the research rows (one per contract x horizon) of one game, in a deterministic order."""
    positions, player_map = positions or {}, player_map or {}
    tickers = sorted(t for t, c in builder.contracts.items() if c.static.get("game_id") == game.game_id)
    obs = {t: [builder.observation(t, h) for h in range(len(HORIZONS))] for t in tickers}
    close = {t: obs[t][-1] for t in tickers}
    t24 = {t: obs[t][0] for t in tickers}
    for h, (hname, _m) in enumerate(HORIZONS):
        cut = game.cutoffs[h]
        at_h = [(builder.contracts[t].static, obs[t][h]) for t in tickers]
        env = game_environment(at_h, game)
        lad = ladder_structure(at_h)
        ag = arm_games.before(game.game_id, cut) if arm_games else None
        for t in tickers:
            st, ob, c = builder.contracts[t].static, obs[t][h], builder.contracts[t]
            s = settlements.get(t) or {}
            team = st.get("team")
            gsis = player_map.get(st.get("player_kalshi_id")) if st.get("player_kalshi_id") else None
            ptm = None
            if st.get("family") == "PLAYER_STAT":
                ptm = team
            row = {"board_version": BOARD_VERSION, "season": game.season, "week": game.week, "game_id": game.game_id,
                   "home_team": game.home, "away_team": game.away, "kickoff_utc": game.kickoff.isoformat(),
                   "ticker": t, "event_ticker": st.get("event_ticker"), "series_ticker": st.get("series_ticker"),
                   "family": st.get("family"), "period": st.get("period") or "FULL", "stat": st.get("stat"),
                   "team": team, "player_name": st.get("player_name"), "player_kalshi_id": st.get("player_kalshi_id"),
                   "player_gsis_id": gsis, "position": positions.get(gsis) if gsis else None,
                   "threshold": _f(st.get("threshold")), "operator": st.get("operator"), "floor_strike": _f(st.get("floor_strike")),
                   "rung_value": rung_value(st), "yes_semantics": "YES pays $1 if the contract's event happens; NO pays $1 otherwise",
                   "subfamily": f"{st.get('family')}:{st.get('period') or 'FULL'}" + (f":{st.get('stat')}" if st.get("stat") else ""),
                   "minutes_to_kickoff": HORIZONS[h][1], "n_pregame_snapshots": c.n_pregame, "n_postgame_rows_ignored": c.n_postgame,
                   **{k: v for k, v in ob.items()}}
            row["price_band_yes"] = price_band(ob.get("yes_ask"))
            row["price_band_no"] = price_band(ob.get("no_ask"))
            row["price_band_mid"] = price_band(ob.get("mid"))
            # fees at the observation instant, both sides
            obs_ts = _ts(ob.get("observed_at")) or cut
            fy = fees.fee(st.get("series_ticker"), ob.get("yes_ask"), obs_ts)
            fn = fees.fee(st.get("series_ticker"), ob.get("no_ask"), obs_ts)
            row.update({"fee_yes": fy["fee_marginal"], "fee_yes_one_contract": fy["fee_one"], "fee_state_yes": fy["fee_state"],
                        "fee_no": fn["fee_marginal"], "fee_no_one_contract": fn["fee_one"], "fee_state_no": fn["fee_state"],
                        "fee_window": fy.get("fee_window") or fn.get("fee_window")})
            # settlement
            row.update({k: s.get(k) for k in ("settlement_status", "settlement_kind", "settlement_reason", "semantic_confidence",
                                               "question_kind", "question_engine", "exchange_state", "exchange_result",
                                               "settled_yes", "settlement_source", "exchange_agrees", "binary_outcome")})
            y = row["settled_yes"]
            row["return_yes"] = side_return(y, ob.get("yes_ask"), row["fee_yes"])
            row["return_no"] = side_return(None if y is None else 1.0 - y, ob.get("no_ask"), row["fee_no"])
            # close and movement (the close is the latest_pregame observation of the same ticker)
            cl, op = close[t], t24[t]
            row["close_mid"] = cl.get("mid") if cl.get("obs_state") == OBS_OK else None
            row["close_quality"] = cl.get("quality")
            row["clv_yes"] = (row["close_mid"] - ob["yes_ask"]) if (hname != PRIMARY_HORIZON and row["close_mid"] is not None and ob.get("yes_ask") is not None) else None
            row["clv_no"] = ((1.0 - row["close_mid"]) - ob["no_ask"]) if (hname != PRIMARY_HORIZON and row["close_mid"] is not None and ob.get("no_ask") is not None) else None
            m0 = op.get("mid") if op.get("obs_state") == OBS_OK else None
            row["move_since_t24h"] = (ob["mid"] - m0) if (h > 0 and m0 is not None and ob.get("mid") is not None) else None
            row["move_band"] = band(row["move_since_t24h"], MOVE_BANDS)
            # ladder + environment
            row.update(lad.get(t, {}))
            row["rung_offset_band"] = rung_offset_band(row.get("rung_offset"))
            row.update(env)
            subj_team = team if team in (game.home, game.away) else None
            if subj_team is None and st.get("family") == "PLAYER_STAT":
                subj_team = None   # player team is not on the capture row; filled from the anatomy below when known
            row["subject_team"] = subj_team
            row["team_role"] = ("FAVORITE" if env["env_favorite"] == subj_team else "UNDERDOG") if (subj_team and env["env_favorite"]) else ("PICK" if subj_team and env["env_home_margin"] is not None else "n/a")
            if subj_team and env["env_home_points"] is not None:
                tp = env["env_home_points"] if subj_team == game.home else env["env_away_points"]
                row["team_implied_points"] = tp
                row["team_implied_band"] = band(tp, TEAM_TOTAL_BANDS)
            else:
                row["team_implied_points"], row["team_implied_band"] = None, "unknown"
            # research context: model disagreement (research-only)
            if ag:
                row.update(ag)
            ac = arm_contracts.before(t, cut) if arm_contracts else None
            mid = ob.get("mid")
            if ac and mid is not None:
                row["p_data_only"], row["p_hybrid"] = ac.get("p_data_only"), ac.get("p_hybrid")
                row["data_only_disagreement"] = (ac["p_data_only"] - mid) if ac.get("p_data_only") is not None else None
                row["hybrid_disagreement"] = (ac["p_hybrid"] - mid) if ac.get("p_hybrid") is not None else None
            row["data_only_disagreement_band"] = band(abs(row["data_only_disagreement"]) if row.get("data_only_disagreement") is not None else None, DISAGREEMENT_BANDS)
            an = anatomy.before(t, cut) if anatomy else None
            if an:
                row["player_model_cv"] = an.get("model_cv")
                row["player_disagreement"] = (an["model_cv"] - mid) if (an.get("model_cv") is not None and mid is not None) else None
                row.update({"p_plays": an.get("p_plays"), "availability_state": an.get("availability_state"),
                            "feature_n_prior": an.get("feature_n_prior"), "proj_opportunity": an.get("proj_opportunity"),
                            "proj_stat_mean": an.get("proj_stat_mean"), "proj_p50": an.get("proj_p50")})
            row["player_disagreement_band"] = band(abs(row["player_disagreement"]) if row.get("player_disagreement") is not None else None, DISAGREEMENT_BANDS)
            row["role_certainty"] = role_certainty(row.get("p_plays"), row.get("feature_n_prior")) if st.get("family") == "PLAYER_STAT" else "n/a"
            # data-quality flags
            flags = []
            if ob.get("obs_state") == OBS_OK and not ob.get("two_sided"):
                flags.append("ONE_SIDED")
            if ob.get("width") is not None and ob["width"] > 0.30:
                flags.append("HUGE_SPREAD")
            if ob.get("quality") == STALE:
                flags.append("STALE_CONFIRMATION")
            if row.get("ladder_monotone_violations"):
                flags.append("LADDER_NONMONOTONE")
            if row["exchange_agrees"] is False:
                flags.append("EXCHANGE_CONTRADICTS_FOOTBALL")
            row["quality_flags"] = flags
            row["analysis_state"], row["exclusion_reason"] = analysis_state(row)
            row["betting_authorized"] = False
            yield row


# ------------------------------------------------------------------------------------------------------ eligibility
ANALYZED = "ANALYZED"


def analysis_state(row: dict) -> tuple[str, str | None]:
    """The FIRST funnel stage a contract-horizon fails, or ANALYZED. Ordered as the coverage funnel."""
    if row.get("obs_state") == OBS_NOT_LISTED:
        return "EXCLUDED", "not listed / no pregame quote by this horizon"
    if row.get("obs_state") == OBS_NOT_OPEN:
        return "EXCLUDED", "market not open at this horizon"
    if row.get("obs_state") == OBS_UNCONFIRMED:
        return "EXCLUDED", "price not confirmed within 24h of the horizon"
    if row.get("settlement_source") == SRC_NONE:
        return "EXCLUDED", f"unsettled: {row.get('settlement_status') or 'no settlement'}"
    if row.get("settlement_source") == SRC_EXCHANGE:
        return "EXCHANGE_ONLY", "football settlement unsupported; exchange terminal result only (separate tier)"
    if row.get("exchange_agrees") is False:
        return "EXCLUDED", "football settlement contradicted by the exchange's terminal result (flagged, never resolved)"
    if not row.get("binary_outcome"):
        return "EXCLUDED", "non-binary payout (tie split / scalar): excluded from event-rate analysis"
    if row.get("yes_ask") is None and row.get("no_ask") is None:
        return "EXCLUDED", "no executable quote on either side"
    if row.get("fee_yes") is None and row.get("fee_no") is None:
        return "EXCLUDED", "fee schedule unknown for this series/time"
    return ANALYZED, None


# ------------------------------------------------------------------------------------------------------ coverage
FUNNEL = ("discovered", "mapped_to_game", "captured_pregame", "settled_any_source", "football_settled",
          "price_at_primary_horizon", "executable_quote", "fee_known", "analyzed_primary")


class CoverageFunnel:
    """Contract-level funnel per (week, family) at the PRIMARY horizon, with exclusion reasons at every stage.
    A contract leaves the funnel at the first stage it fails; nothing is ever dropped without a reason."""

    def __init__(self):
        self.counts = defaultdict(Counter)        # (week, family) -> stage -> n
        self.reasons = defaultdict(Counter)       # (week, family) -> reason -> n
        self.horizon_states = defaultdict(Counter)
        self.universe = defaultdict(Counter)       # category -> family -> n (the whole discovery universe)

    def add_discovered_only(self, week, family, reason):
        k = (week, family)
        self.counts[k]["discovered"] += 1
        self.counts[k]["mapped_to_game"] += 1
        self.reasons[k][reason] += 1

    def add_universe(self, category: str, family):
        """Every discovery market, by where it sits relative to the requested weeks (accounting, not analysis)."""
        self.universe[category][family or "UNKNOWN"] += 1

    def add_row(self, row: dict):
        k = (row["week"], row["family"])
        self.horizon_states[(row["week"], row["horizon"])][row["analysis_state"]] += 1
        if row["horizon"] != PRIMARY_HORIZON:
            return
        c = self.counts[k]
        c["discovered"] += 1
        c["mapped_to_game"] += 1
        stage_ok = [("captured_pregame", row.get("n_pregame_snapshots", 0) > 0, "never quoted before kickoff"),
                    ("settled_any_source", row.get("settled_yes") is not None,
                     f"no settlement from football ({row.get('settlement_status')}) or exchange ({row.get('exchange_state')})"),
                    ("football_settled", row.get("settlement_source") == SRC_FOOTBALL,
                     f"exchange-only tier: {row.get('settlement_status')} [{row.get('subfamily')}]"),
                    ("price_at_primary_horizon", row.get("obs_state") == OBS_OK, f"{row.get('obs_state')}: {row.get('obs_reason')}"),
                    ("executable_quote", row.get("yes_ask") is not None or row.get("no_ask") is not None, "no executable quote"),
                    ("fee_known", row.get("fee_yes") is not None or row.get("fee_no") is not None, "fee unknown"),
                    ("analyzed_primary", row.get("analysis_state") == ANALYZED, row.get("exclusion_reason") or "")]
        for stage, ok, why in stage_ok:
            if not ok:
                self.reasons[k][f"{stage}: {why}"] += 1
                return
            c[stage] += 1

    def to_dict(self) -> dict:
        weeks = sorted({str(w) for (w, _f) in self.counts})
        out = {"funnel_stages": list(FUNNEL), "by_week_family": [], "by_week": {}, "total": {}, "horizon_states": {}}
        tot = Counter()
        for (w, fam) in sorted(self.counts, key=lambda k: (str(k[0]), str(k[1]))):
            c = self.counts[(w, fam)]
            out["by_week_family"].append({"week": w, "family": fam, **{s: c.get(s, 0) for s in FUNNEL},
                                          "exclusions": dict(self.reasons[(w, fam)].most_common())})
        for w in weeks:
            wc = Counter()
            wr = Counter()
            for (ww, fam), c in self.counts.items():
                if str(ww) == w:
                    wc.update(c)
                    wr.update(self.reasons[(ww, fam)])
            out["by_week"][w] = {**{s: wc.get(s, 0) for s in FUNNEL}, "exclusions": dict(wr.most_common())}
            tot.update(wc)
        allr = Counter()
        for r in self.reasons.values():
            allr.update(r)
        out["total"] = {**{s: tot.get(s, 0) for s in FUNNEL}, "exclusions": dict(allr.most_common())}
        out["discovery_universe"] = {cat: {"n": sum(c.values()), "by_family": dict(c.most_common())}
                                     for cat, c in sorted(self.universe.items())}
        out["horizon_states"] = {f"{w}|{h}": dict(c) for (w, h), c in sorted(self.horizon_states.items(), key=lambda kv: (str(kv[0][0]), kv[0][1]))}
        return out


# ------------------------------------------------------------------------------------------------------ io
SLIM_FIELDS = ("season", "week", "game_id", "ticker", "family", "period", "stat", "subfamily", "team", "player_gsis_id",
               "position", "horizon", "analysis_state", "yes_ask", "no_ask", "mid", "fee_yes", "fee_no", "settled_yes",
               "return_yes", "return_no", "clv_yes", "clv_no", "price_band_yes", "price_band_no", "rung_value",
               "ladder_id", "rung_offset", "rung_offset_band", "is_main_rung", "distance_from_main", "ladder_n_live_rungs",
               "env_spread_band", "env_total_band", "env_favorite", "team_role", "team_implied_band", "role_certainty",
               "availability_state", "data_only_disagreement", "data_only_disagreement_band", "player_disagreement",
               "player_disagreement_band", "move_since_t24h", "move_band", "settlement_source", "binary_outcome",
               "quality", "width", "liquidity", "volume")


def write_jsonl_gz(path: str, rows):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    n = 0
    with gzip.open(path, "wt") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            n += 1
    return n


def read_jsonl_gz(path: str, fields=None):
    with gzip.open(path, "rt") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                yield {k: r.get(k) for k in fields} if fields else r
