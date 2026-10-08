"""The market side of the wall. RESEARCH ONLY. Never imported by the feature modules.

1. Game lines: nflverse schedule ``spread_line`` (POSITIVE = HOME favoured), ``total_line``, moneylines and
   the listed spread / total odds. A single near-close consensus with undocumented timing
   (``docs/KNOWN_LIMITATIONS.md`` #1): labelled ``CLOSING_UNTIMESTAMPED`` and never called executable.
   ``spread_home`` below is converted to the CFB convention (NEGATIVE = home favoured).

2. Kalshi player-prop ladders.
   * 2025: the backfill horizon archive (``data/kalshi/backfill/horizons`` on ``market-data``): settled markets
     with YES bid/ask snapshots at fixed horizons. PRIMARY CHECKPOINT (pre-registered): ``T-90m``. NO ask is
     not captured there and is taken as 1 - YES bid (stated, not hidden).
   * 2026: the prospective capture (``data/kalshi/capture`` on ``market-data``), aggregated to the LAST
     PREGAME executable quote per ticker with both asks captured. PRIMARY CHECKPOINT (pre-registered):
     ``LAST_PREGAME`` (minutes-to-kickoff recorded on every row; a close proxy, not T-90).
   * A rung's quote is valid when 0 < bid <= ask < 1 and ask - bid <= 0.10 (the repository's tradable-book
     convention). The ladder's MARKET MEDIAN is the threshold at which the interpolated P(stat >= t) crosses
     0.5 using valid mids; a ladder that never crosses 0.5 has no median (missing, never extrapolated).
   * Identity: Kalshi player -> GSIS by the repository's rule order (``scripts/kalshi/build_player_map.py``):
     normalised name + team in the season roster, then + jersey, then name unique in the roster; anything
     else is UNRESOLVED and dropped (counted). Display name alone is never the join key.
"""

from __future__ import annotations

import json
import math
import os
import re
from collections import defaultdict

import numpy as np
import pandas as pd
import polars as pl

from nfl_edge.data.ids import _norm_name
from nfl_edge.sim import data as D

NAME_ALIASES = {"hollywood brown": "marquise brown", "joshua palmer": "josh palmer"}  # build_player_map.py
TEAM_FIX = {"ARZ": "ARI", "BLT": "BAL", "CLV": "CLE", "HST": "HOU", "JAC": "JAX", "LAR": "LA", "WSH": "WAS"}
MAX_WIDTH = 0.10
STATS = ("passing_yards", "attempts", "completions", "carries", "rushing_yards", "receptions", "receiving_yards",
         "passing_tds", "interceptions", "rush_rec_yards")
#: Kalshi stat -> player_games column (official-count conventions, see nfl_edge/sim/data.py)
STAT_COLUMN = {"passing_yards": "pass_yards", "attempts": "attempts", "completions": "completions",
               "carries": "carries", "rushing_yards": "rush_yards", "receptions": "receptions",
               "receiving_yards": "rec_yards", "passing_tds": "pass_td", "interceptions": "ints"}


# ------------------------------------------------------------------------------------------- game lines
def game_lines(schedule: pd.DataFrame) -> pd.DataFrame:
    s = schedule
    out = pd.DataFrame({
        "game_id": s["game_id"],
        "spread_home": -s["spread_line"].astype(float),
        "total": s["total_line"].astype(float),
        "home_ml": s["home_moneyline"], "away_ml": s["away_moneyline"],
        "home_spread_odds": s["home_spread_odds"], "away_spread_odds": s["away_spread_odds"],
        "over_odds": s["over_odds"], "under_odds": s["under_odds"],
    })
    def nv(h, a):
        if pd.isna(h) or pd.isna(a) or h == 0 or a == 0:
            return None
        ih, ia = _impl(h), _impl(a)
        return ih / (ih + ia)
    out["ml_home_novig"] = [nv(h, a) for h, a in zip(out["home_ml"], out["away_ml"], strict=False)]
    out["line_timing"] = "CLOSING_UNTIMESTAMPED"
    return out


def _impl(odds: float) -> float:
    odds = float(odds)
    return 1.0 / (1.0 + (odds / 100.0 if odds > 0 else 100.0 / -odds))


def american_to_decimal(odds: float) -> float:
    odds = float(odds)
    return 1.0 + (odds / 100.0 if odds > 0 else 100.0 / -odds)


# ------------------------------------------------------------------------------------------- identity
def _roster(season: int) -> pd.DataFrame:
    p = os.path.join(D.RAW, "rosters", f"roster_{season}.parquet")
    r = pl.read_parquet(p).select(["gsis_id", "full_name", "team", "jersey_number", "position"]).filter(pl.col("gsis_id").is_not_null())
    r = pd.DataFrame(r.to_dicts())
    r["name_key"] = r["full_name"].map(_norm_name)
    r["team"] = r["team"].replace(TEAM_FIX)
    return r


class Resolver:
    def __init__(self, season: int):
        self.r = _roster(season)
        self.by_name = defaultdict(list)
        for _, x in self.r.iterrows():
            self.by_name[x["name_key"]].append(x)
        self.cache: dict = {}

    def resolve(self, name: str, team: str | None, jersey: int | None) -> tuple[str | None, str]:
        k = (name, team, jersey)
        if k in self.cache:
            return self.cache[k]
        key = _norm_name(name or "")
        key = NAME_ALIASES.get(key, key)
        cand = self.by_name.get(key, [])
        out = (None, "UNRESOLVED")
        if team:
            c2 = [c for c in cand if c["team"] == team]
            if len(c2) == 1:
                out = (c2[0]["gsis_id"], "RESOLVED_NAME_TEAM")
            elif len(c2) > 1 and jersey is not None:
                c3 = [c for c in c2 if c["jersey_number"] is not None and int(c["jersey_number"]) == jersey]
                if len(c3) == 1:
                    out = (c3[0]["gsis_id"], "RESOLVED_NAME_TEAM_JERSEY")
        if out[0] is None and len(cand) == 1:
            out = (cand[0]["gsis_id"], "RESOLVED_NAME_UNIQUE")
        self.cache[k] = out
        return out


_JERSEY = re.compile(r"(\d+)$")


def _jersey_from_ticker(ticker: str) -> int | None:
    # e.g. KXNFLREC-26FEB08SEANE-SEAGHOLANI36-1 -> 36
    parts = ticker.split("-")
    if len(parts) < 3:
        return None
    m = _JERSEY.search(parts[2])
    return int(m.group(1)) if m else None


# ------------------------------------------------------------------------------------------- ladders
def _valid(bid, ask) -> bool:
    return bid is not None and ask is not None and 0 < bid <= ask < 1 and (ask - bid) <= MAX_WIDTH


def ladder_median(rungs: list[tuple[float, float]]) -> float | None:
    """rungs: (threshold t meaning stat >= t, P(YES) mid). Interpolated t where P crosses 0.5."""
    pts = sorted(rungs)
    for (t1, p1), (t2, p2) in zip(pts, pts[1:], strict=False):
        if p1 >= 0.5 >= p2 and p1 != p2:
            return t1 + (p1 - 0.5) / (p1 - p2) * (t2 - t1)
    return None


def kalshi_2025(horizon_files: list[str], checkpoint: str = "T-90m") -> pd.DataFrame:
    """One row per settled player-stat RUNG at the checkpoint (YES bid/ask; NO ask = 1 - YES bid)."""
    rows = []
    for f in horizon_files:
        with open(f) as fh:
            for line in fh:
                r = json.loads(line)
                if r.get("family") != "PLAYER_STAT" or r.get("stat") not in STATS or r.get("period") not in (None, "FULL"):
                    continue
                snap = (r.get("snaps") or {}).get(checkpoint) or {}
                if r.get("season") is None or r.get("week") is None or r.get("game_id") is None:
                    continue  # unmapped to an nflverse game: dropped (counted by the caller via ticker totals)
                rows.append({"ticker": r["ticker"], "season": int(r["season"]), "week": int(r["week"]), "game_id": r["game_id"],
                             "stat": r["stat"], "team": TEAM_FIX.get(r.get("team"), r.get("team")), "player_name": r.get("player_name"),
                             "kalshi_player_id": r.get("player_kalshi_id"), "threshold": float(r["threshold"]),
                             "operator": r.get("operator"), "result": r.get("result"), "yes_bid": snap.get("bid"),
                             "yes_ask": snap.get("ask"), "no_ask": (1 - snap["bid"]) if snap.get("bid") is not None else None,
                             "checkpoint": checkpoint, "quote_age_min": snap.get("age_min"),
                             "kickoff_ts": r.get("anchor_ts"), "source": "KALSHI_2025_HORIZON_ARCHIVE"})
    return pd.DataFrame(rows)


def kalshi_2026(agg: dict) -> pd.DataFrame:
    """One row per player-stat rung, LAST_PREGAME executable quote (both asks captured)."""
    rows = []
    for t, a in agg.items():
        if a.get("family") != "PLAYER_STAT" or a.get("stat") not in STATS:
            continue
        q = a.get("last_pre_q")
        if not q or not a.get("game_id"):
            continue
        ya, na, yb, nb, mtk = q
        season, week = int(a["game_id"][:4]), int(a["game_id"][5:7])
        rows.append({"ticker": t, "season": season, "week": week, "game_id": a["game_id"], "stat": a["stat"],
                     "team": TEAM_FIX.get(a.get("team"), a.get("team")), "player_name": a.get("player_name"),
                     "kalshi_player_id": a.get("player_kalshi_id"), "threshold": float(a["threshold"]) if a.get("threshold") is not None else None,
                     "operator": a.get("operator"), "result": None, "yes_bid": yb, "yes_ask": ya, "no_ask": na, "no_bid": nb,
                     "checkpoint": "LAST_PREGAME", "minutes_to_kickoff": mtk, "kickoff_utc": a.get("kickoff_utc"),
                     "source": "KALSHI_2026_PROSPECTIVE_CAPTURE"})
    return pd.DataFrame(rows)


def attach_identity(rungs: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    out, counts = [], defaultdict(int)
    for season, part in rungs.groupby("season"):
        res = Resolver(int(season))
        ids, how = [], []
        for _, r in part.iterrows():
            g, h = res.resolve(r["player_name"], r["team"], _jersey_from_ticker(r["ticker"]))
            ids.append(g)
            how.append(h)
        part = part.assign(gsis_id=ids, identity=how)
        out.append(part)
    df = pd.concat(out, ignore_index=True) if out else rungs
    for h, n in df.groupby("identity")["ticker"].nunique().items():
        counts[h] = int(n)
    return df, dict(counts)


def ladders(rungs: pd.DataFrame) -> pd.DataFrame:
    """One row per (game, player, stat): market median from valid mids, the natural (closest-to-50%) rung and its
    executable asks. Missing stays missing."""
    rows = []
    key = ["season", "week", "game_id", "gsis_id", "stat"]
    for k, g in rungs[rungs["gsis_id"].notna() & (rungs["operator"].isin([">=", None]) | rungs["operator"].isna())].groupby(key):
        valid = [(t, (b + a) / 2) for t, b, a in zip(g["threshold"], g["yes_bid"], g["yes_ask"], strict=False) if _valid(b, a)]
        med = ladder_median(valid) if valid else None
        nat = None
        if valid:
            t_nat, p_nat = min(valid, key=lambda x: abs(x[1] - 0.5))
            r = g[g["threshold"] == t_nat].iloc[0]
            nat = {"threshold": t_nat, "mid": p_nat, "yes_ask": r["yes_ask"], "no_ask": r["no_ask"], "result": r.get("result"),
                   "ticker": r["ticker"]}
        rows.append({**dict(zip(key, k, strict=False)), "rungs": len(g), "valid_rungs": len(valid), "market_median": med,
                     "natural": nat, "checkpoint": g["checkpoint"].iloc[0], "source": g["source"].iloc[0]})
    return pd.DataFrame(rows)


def kalshi_fee(price: float) -> float:
    """Taker fee per contract at price p: ceil to the cent of 0.07 p (1-p) (the repository's research convention)."""
    return math.ceil(round(0.07 * price * (1 - price) * 100, 6)) / 100.0


def nan_to_none(x):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else x
