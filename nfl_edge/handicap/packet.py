"""Build the canonical RUN NFL handicap packet for a slate.

The packet compresses a very large database into what a handicapper actually needs, while keeping pointers
back to the deeper artifacts. It is assembled from already-published artifacts rather than by re-running the
model, which makes it fast, deterministic and reproducible from the immutable record:

  shadow ledger observations  ->  every listed market, its quote, its model value, its support state
  market_implied.json.gz      ->  latent market distribution per player ladder (RESEARCH, not fair value)
  context captures            ->  injuries (ESPN + Sleeper), weather with vintage
  capture quote history       ->  market movement at OBSERVED horizons only
  silver team_game            ->  opponent-adjusted team profiles

Three rules run through the whole module and are worth stating once:

1. **Disagreement is never called edge.** Every model-vs-market field is labelled disagreement and carries
   the model's own uncertainty next to it.
2. **Nothing is interpolated into an observation.** A movement horizon that was never captured is reported
   as not observed, and distinguishes "our capture started after this horizon" from "this horizon has not
   happened yet".
3. **Unsupported markets are shown, not hidden.** The handicapper may reason qualitatively about a market the
   model cannot price. They are labelled with a granular reason so a missing model is never mistaken for a
   missing market.
"""
from __future__ import annotations

import glob
import gzip
import hashlib
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone

PACKET_SCHEMA_VERSION = "1.0.0"

# Movement horizons, in minutes before kickoff. Reported only where an observation exists.
MOVEMENT_HORIZONS_MIN = [72 * 60, 48 * 60, 24 * 60, 12 * 60, 6 * 60, 3 * 60, 90, 60, 30]

GAME_FAMILIES = {
    "GAME_WINNER", "SPREAD", "TOTAL", "TEAM_TOTAL", "WIN_MARGIN_BUCKET", "TOTAL_TD",
    "BOTH_TEAMS_SCORE", "BOTH_TEAMS_SCORE_N", "PERIOD_WINNER", "HALF_FULL_RESULT", "RACE_TO_N",
    "FIRST_TD_TEAM", "GAME_EVENT",
}
PLAYER_FAMILIES = {"PLAYER_STAT", "FIRST_TD_SCORER", "ANYTIME_TD"}

STALE_QUOTE_MIN = 240.0        # a quote unconfirmed for this long is flagged, not silently used

# A midpoint is only meaningful if there is a market around it. An untraded Kalshi book quotes 0.00/0.99,
# whose "midpoint" of 0.495 is an artefact of the quoting convention, not an opinion about football.
# Ranking model-vs-market disagreement without this filter puts those books at the top of the list every
# time -- session 2 hit the same artefact in the efficiency map and fixed it with a width cap there.
MAX_DISAGREEMENT_WIDTH = 0.15   # books wider than this are shown but never RANKED by disagreement
NO_REAL_MARKET_WIDTH = 0.25     # at or beyond this the midpoint is not treated as a price at all


def _f(x):
    try:
        v = float(x)
        return None if v != v else v
    except (TypeError, ValueError):
        return None


def _iso(ts):
    if not ts:
        return None
    try:
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except ValueError:
        return None


# ======================================================================================================
# loading
# ======================================================================================================

def load_latest_ledger(md_root: str):
    """Newest published shadow-ledger snapshot: rows, manifest, market-implied ladders."""
    obs = sorted(glob.glob(os.path.join(md_root, "data", "shadow", "ledger", "*", "*.observations.jsonl.gz")))
    if not obs:
        raise FileNotFoundError(
            f"no shadow ledger under {md_root}/data/shadow/ledger -- run scripts/shadow/price_slate.py first")
    path = obs[-1]
    rows = [json.loads(l) for l in gzip.open(path, "rt")]
    man_path = path.replace(".observations.jsonl.gz", ".ledger_manifest.json")
    manifest = json.load(open(man_path)) if os.path.exists(man_path) else {}
    run_id = os.path.basename(path).split(".")[0]
    mi_path = os.path.join(os.path.dirname(path), f"{run_id}.market_implied.json.gz")
    implied = json.load(gzip.open(mi_path, "rt")) if os.path.exists(mi_path) else {}
    return rows, manifest, implied, path


def load_context(md_root: str, n_recent: int = 2):
    """The two most recent context captures, so 'new since the previous run' is a real diff."""
    days = sorted(glob.glob(os.path.join(md_root, "data", "context", "*")))
    runs = []
    for d in days:
        for m in sorted(glob.glob(os.path.join(d, "*.manifest.json"))):
            runs.append(m[: -len(".manifest.json")])
    out = []
    for stem in runs[-n_recent:]:
        rec = {"run_id": os.path.basename(stem), "espn": None, "sleeper": None, "weather": []}
        for key, suffix in (("espn", ".espn_injuries.json"), ("sleeper", ".sleeper.json")):
            p = stem + suffix
            if os.path.exists(p):
                try:
                    rec[key] = json.load(open(p))
                except json.JSONDecodeError:
                    rec[key] = None
        wp = stem + ".weather.jsonl"
        if os.path.exists(wp):
            for line in open(wp):
                try:
                    rec["weather"].append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        out.append(rec)
    return out


def load_movement(md_root: str, tickers: set, max_files: int | None = None):
    """ticker -> [(observed_at, mid, yes_bid, yes_ask)] across the capture history.

    The capture is change-suppressed, so this series is the set of moments the price actually MOVED. That is
    exactly what a movement section wants, and it is why no horizon is ever interpolated.
    """
    files = sorted(glob.glob(os.path.join(md_root, "data", "kalshi", "capture", "*", "*.quotes.jsonl")))
    if max_files:
        files = files[-max_files:]
    series = defaultdict(list)
    for f in files:
        for line in open(f):
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = r.get("ticker")
            if t not in tickers:
                continue
            yb, ya = _f(r.get("yes_bid")), _f(r.get("yes_ask"))
            mid = (yb + ya) / 2.0 if (yb is not None and ya is not None) else None
            series[t].append((r.get("observed_at"), mid, yb, ya))
    for t in series:
        series[t].sort(key=lambda x: x[0] or "")
    return series, len(files)


# ======================================================================================================
# market layer
# ======================================================================================================

def market_row(r: dict) -> dict:
    """One market/rung as the packet presents it."""
    yb, ya = _f(r.get("yes_bid")), _f(r.get("yes_ask"))
    nb, na = _f(r.get("no_bid")), _f(r.get("no_ask"))
    mid = _f(r.get("mid"))
    mv = _f(r.get("model_contract_value"))
    out = {
        "ticker": r.get("ticker"),
        "family": r.get("family"),
        "period": r.get("period"),
        "stat": r.get("stat"),
        "threshold": _f(r.get("threshold")),
        "operator": r.get("operator"),
        "player_name": r.get("player_name"),
        "player_id": r.get("player_id"),
        "team": r.get("team"),
        "yes_bid": yb, "yes_ask": ya, "no_bid": nb, "no_ask": na,
        "mid": mid,
        "width": _f(r.get("quote_width")),
        "volume": _f(r.get("volume")),
        "open_interest": _f(r.get("open_interest")),
        "minutes_since_price_change": _f(r.get("minutes_since_price_change")),
        "minutes_to_kickoff": _f(r.get("minutes_to_kickoff")),
        "book_depth_yes": _f(r.get("book_depth_yes")),
        "book_depth_no": _f(r.get("book_depth_no")),
        "book_imbalance": _f(r.get("book_imbalance")),
        "support_state": r.get("support_state"),
        "support_reason": r.get("support_reason"),
        "availability_state": r.get("availability_state"),
        "p_plays": _f(r.get("p_plays")),
    }
    if mv is not None:
        out["model_probability"] = mv
        out["model_event_probability"] = _f(r.get("model_event_probability"))
        out["calibrated_probability"] = _f(r.get("calibrated_probability"))
        out["model_uncertainty"] = _f(r.get("model_uncertainty"))
        # Disagreement, never called edge. Executable variants use the price actually payable.
        out["disagreement_vs_mid"] = None if mid is None else round(mv - mid, 5)
        out["disagreement_yes_executable"] = None if ya is None else round(mv - ya, 5)
        out["disagreement_no_executable"] = None if na is None else round((1.0 - mv) - na, 5)
        out["disagreement_label"] = "DISAGREEMENT ONLY -- REQUIRES HANDICAP"
    # Is there a market here at all? Width plus traded interest, not width alone: a genuinely quiet but
    # real book can be wide, while a 0.00/0.99 book with zero volume and zero open interest is a placeholder.
    w = out["width"]
    vol, oi = out["volume"] or 0.0, out["open_interest"] or 0.0
    out["no_real_market"] = bool(
        w is not None and (w >= NO_REAL_MARKET_WIDTH or (w >= 0.10 and vol <= 0.0 and oi <= 0.0)))
    out["tradable_for_disagreement_ranking"] = bool(
        w is not None and w <= MAX_DISAGREEMENT_WIDTH and not out["no_real_market"])

    flags = []
    if out["no_real_market"]:
        flags.append(f"no real market: width {w:.2f}, volume {vol:.0f}, open interest {oi:.0f} -- "
                     "the midpoint is a quoting artefact, not a price")
    msc = out["minutes_since_price_change"]
    if msc is not None and msc > STALE_QUOTE_MIN:
        flags.append(f"quote unchanged {msc:.0f}m (change-suppressed capture: last MOVE, not staleness)")
    if yb is not None and ya is not None and (ya - yb) >= 0.10:
        flags.append(f"wide book {ya - yb:.2f}")
    if yb is not None and ya is not None and yb <= 0.0 and ya >= 1.0:
        flags.append("empty book")
    out["flags"] = flags
    return out


def movement_for(ticker: str, series: dict, kickoff, now) -> dict:
    """Observed movement only. Distinguishes 'not captured' from 'not yet reached'."""
    pts = series.get(ticker) or []
    parsed = [(_iso(ts), mid) for ts, mid, _, _ in pts if _iso(ts) and mid is not None]
    parsed.sort()
    out = {"n_observations": len(parsed), "horizons": {}}
    if not parsed:
        out["note"] = "no captured quote history for this ticker"
        return out
    first_ts, first_mid = parsed[0]
    out["first_observed"] = {"at": first_ts.isoformat(), "mid": first_mid,
                             "label": "first capture of this ticker, not the market open"}
    last_ts, last_mid = parsed[-1]
    out["current"] = {"at": last_ts.isoformat(), "mid": last_mid}
    out["total_move_since_first_capture"] = round(last_mid - first_mid, 5)
    if kickoff is None:
        return out
    for h in MOVEMENT_HORIZONS_MIN:
        cutoff = kickoff - timedelta(minutes=h)
        label = f"T-{h // 60}h" if h >= 60 and h % 60 == 0 else f"T-{h}m"
        if now < cutoff:
            out["horizons"][label] = {"observed": False, "reason": "horizon not yet reached"}
            continue
        prior = [(t, m) for t, m in parsed if t <= cutoff]
        if not prior:
            out["horizons"][label] = {"observed": False, "reason": "no capture before this horizon"}
            continue
        t, m = prior[-1]
        out["horizons"][label] = {"observed": True, "at": t.isoformat(), "mid": m,
                                  "move_to_current": round(last_mid - m, 5)}
    return out


# ======================================================================================================
# distributions reconstructed from the ledger ladders
# ======================================================================================================

def _survival_summary(points: list) -> dict:
    """points: [(threshold, P(stat >= threshold))]. Returns median / mean lower bound / rung probabilities.

    The mean is a LOWER BOUND, not a mean: a ladder is truncated at its highest listed rung, so the mass
    above it is unknown. Calling it a mean would be fake precision, so it is named for what it is.
    """
    pts = sorted({(float(k), float(p)) for k, p in points if k is not None and p is not None})
    if len(pts) < 2:
        return {"n_rungs": len(pts), "insufficient_ladder": True}
    ks = [k for k, _ in pts]
    ps = [p for _, p in pts]
    # enforce monotone non-increasing survival
    mono = list(ps)
    for i in range(1, len(mono)):
        mono[i] = min(mono[i], mono[i - 1])
    median = None
    for i in range(len(ks) - 1):
        a, b = mono[i], mono[i + 1]
        if a >= 0.5 >= b and a != b:
            median = ks[i] + (a - 0.5) / (a - b) * (ks[i + 1] - ks[i])
            break
    # E[X] >= sum over consecutive rungs of P(X>=k)*(k_next - k), anchored at the lowest rung
    lower = ks[0] * mono[0]
    for i in range(len(ks) - 1):
        lower += mono[i + 1] * (ks[i + 1] - ks[i])
    return {
        "n_rungs": len(pts),
        "insufficient_ladder": False,
        "median": None if median is None else round(median, 3),
        "mean_lower_bound": round(lower, 3),
        "highest_listed_rung": ks[-1],
        "thresholds": {str(k): round(p, 4) for k, p in zip(ks, mono)},
        "monotonicity_violations": sum(1 for a, b in zip(ps, ps[1:]) if b > a),
    }


def player_projection_blocks(rows: list, implied: dict, game_id: str) -> dict:
    """player -> stat -> {model distribution, market distribution, disagreement}."""
    by_player = defaultdict(lambda: defaultdict(list))
    meta = {}
    for r in rows:
        if r.get("family") not in PLAYER_FAMILIES or not r.get("player_name"):
            continue
        stat = r.get("stat") or r.get("family")
        by_player[r["player_name"]][stat].append(r)
        meta.setdefault(r["player_name"], {
            "player_id": r.get("player_id"),
            "player_kalshi_id": r.get("player_kalshi_id"),
            "team": r.get("team"),
            "availability_state": r.get("availability_state"),
            "p_plays": _f(r.get("p_plays")),
            "p_inactive": _f(r.get("p_inactive")),
        })
    out = {}
    for name, stats in by_player.items():
        blocks = {}
        for stat, rs in stats.items():
            model_pts = [(_f(r.get("threshold")), _f(r.get("model_contract_value"))) for r in rs]
            market_pts = [(_f(r.get("threshold")), _f(r.get("mid"))) for r in rs]
            model_pts = [(k, p) for k, p in model_pts if k is not None and p is not None]
            market_pts = [(k, p) for k, p in market_pts if k is not None and p is not None]
            blk = {
                "n_listed_rungs": len(rs),
                "supported_rungs": sum(1 for r in rs if r.get("support_state") == "SUPPORTED"),
                "model": _survival_summary(model_pts) if model_pts else {"insufficient_ladder": True},
                "market": _survival_summary(market_pts) if market_pts else {"insufficient_ladder": True},
            }
            kid = meta[name].get("player_kalshi_id")
            mi = implied.get(f"{kid}|{stat}|{game_id}") if kid else None
            if mi:
                blk["research_market_implied_distribution"] = {
                    "k": mi.get("k"), "p_monotone": mi.get("p_monotone"),
                    "implied_mean_lower_bound": mi.get("implied_mean_lower_bound"),
                    "median_width": mi.get("median_width"),
                    "label": "RESEARCH MARKET-IMPLIED DISTRIBUTION -- not executable fair value",
                }
            mm, km = blk["model"].get("median"), blk["market"].get("median")
            if mm is not None and km is not None:
                blk["median_disagreement"] = round(mm - km, 3)
                blk["disagreement_label"] = "DISAGREEMENT ONLY -- REQUIRES HANDICAP"
            blocks[stat] = blk
        out[name] = {"meta": meta[name], "stats": blocks}
    return out


def game_market_implied(rows: list, home: str, away: str, period: str = "FULL",
                        value_key: str = "mid") -> dict:
    """Market-implied spread / total from the SPREAD and TOTAL ladders in this game, for one period.

    Reconstructed from listed rungs rather than re-simulated, so it reflects exactly the prices in the
    packet. Labelled research: it is a latent quantity inferred from midpoints, not a tradable line.

    The `period` filter is not cosmetic. Kalshi lists FULL, 1H, 2H and all four quarters under the same
    SPREAD and TOTAL families; pooling them produced an "implied total" of 7.7 points, because quarter
    ladders sit on a completely different scale. Every ladder here is one period or it is meaningless.
    """
    out = {"label": ("RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable"
                     if value_key == "mid" else
                     "MODEL VIEW -- reconstructed from the model's own ladder, same estimator as the market"),
           "period": period, "value_key": value_key}
    spread_pts = defaultdict(list)
    total_pts = []
    for r in rows:
        if (r.get("period") or "FULL") != period:
            continue
        mid = _f(r.get(value_key))
        k = _f(r.get("threshold"))
        if mid is None or k is None:
            continue
        if r.get("family") == "SPREAD" and r.get("team"):
            spread_pts[r["team"]].append((k, mid))
        elif r.get("family") == "TOTAL":
            total_pts.append((k, mid))
    # signed home margin: home rung at strike s -> S(s); away rung at s -> S(-s) = 1 - quote
    pts = []
    for team, ps in spread_pts.items():
        for k, p in ps:
            pts.append((k, p) if team == home else (-k, 1.0 - p))
    if len(pts) >= 3:
        s = _survival_summary(pts)
        out["margin_distribution"] = s
        out["implied_home_margin_median"] = s.get("median")
        if s.get("median") is not None:
            out["implied_spread"] = round(-s["median"], 2)     # negative = home favoured, betting convention
    if len(total_pts) >= 3:
        t = _survival_summary(total_pts)
        out["total_distribution"] = t
        out["implied_total_median"] = t.get("median")
    win = [r for r in rows if r.get("family") == "GAME_WINNER" and (r.get("period") or "FULL") == period]
    for r in win:
        mid = _f(r.get(value_key))
        if mid is None:
            continue
        out.setdefault("win_probability", {})[r.get("team") or r.get("ticker")] = mid
    if out.get("implied_home_margin_median") is not None and out.get("implied_total_median") is not None:
        m, tt = out["implied_home_margin_median"], out["implied_total_median"]
        out["implied_score"] = {home: round((tt + m) / 2.0, 1), away: round((tt - m) / 2.0, 1)}
    return out


# ======================================================================================================
# context: injuries, roles, weather
# ======================================================================================================

def _espn_team_index():
    from nfl_edge.data.ids import TEAM_NAMES
    idx = {}
    for code, (city, nick) in TEAM_NAMES.items():
        idx[nick.lower()] = code
        idx[city.lower()] = code
        idx[f"{city} {nick}".lower()] = code
    # ESPN prints full display names; the Rams/Chargers share a city so match on the nickname too.
    idx["los angeles rams"] = "LA"
    idx["los angeles chargers"] = "LAC"
    return idx


def injury_state(context_runs: list, teams: set) -> dict:
    """Structured current injuries for the given teams, with a real diff against the previous capture.

    'New since the previous run' is computed by comparing the two most recent captures on (player, status).
    It is not a guess about when the news broke -- it is the first capture in which we OBSERVED the change,
    which is the only timing this data supports.
    """
    if not context_runs:
        return {"available": False, "reason": "no context captures found"}
    cur = context_runs[-1]
    prev = context_runs[-2] if len(context_runs) > 1 else None
    idx = _espn_team_index()

    def espn_rows(run):
        out = {}
        for r in ((run or {}).get("espn") or {}).get("injuries", []) or []:
            code = idx.get(str(r.get("team", "")).lower())
            if code not in teams:
                continue
            out[(code, r.get("name"))] = r
        return out

    def sleeper_rows(run):
        out = {}
        for p in (((run or {}).get("sleeper") or {}).get("players") or {}).values():
            code = p.get("team")
            if code not in teams:
                continue
            if p.get("injury_status") or p.get("practice_participation"):
                out[(code, p.get("full_name"))] = p
        return out

    cur_e, prev_e = espn_rows(cur), espn_rows(prev)
    cur_s, prev_s = sleeper_rows(cur), sleeper_rows(prev)

    by_team = defaultdict(list)
    for (code, name), r in cur_e.items():
        was = (prev_e.get((code, name)) or {}).get("status")
        now = r.get("status")
        sl = cur_s.get((code, name)) or {}
        rec = {
            "player": name,
            "position": r.get("position"),
            "state": now,
            "source": "espn",
            "first_seen_in_capture": cur["run_id"],
            "detail": r.get("detail") or r.get("injury"),
            "body_part": r.get("location") or sl.get("injury_body_part"),
            "return_date": r.get("return_date"),
            "comment": r.get("short_comment"),
            "espn_report_date": r.get("date"),
            "sleeper_status": sl.get("injury_status"),
            "practice": sl.get("practice_participation"),
            "changed_since_previous_capture": (prev is not None and was is not None and was != now),
            "previous_state": was,
            "new_since_previous_capture": (prev is not None and (code, name) not in prev_e),
        }
        # Confidence reflects agreement between two independent feeds, not our belief about the injury.
        # The two feeds use different vocabularies for the same fact -- ESPN "Injured Reserve" against
        # Sleeper "IR", ESPN "Out" against Sleeper "PUP"/"NA" -- so they are compared on a canonical
        # severity, not as strings. Comparing raw strings marked 29 of 50 agreeing records as conflicting.
        if sl.get("injury_status") and now:
            a, b = _canon_availability(now), _canon_availability(sl["injury_status"])
            rec["confidence"] = "high" if a == b else "conflicting"
            if a != b:
                rec["conflict"] = f"espn={now!r} ({a}) vs sleeper={sl['injury_status']!r} ({b})"
        else:
            rec["confidence"] = "single_source"
        rec["likely_role_impact"] = _role_impact(now, r.get("position"))
        by_team[code].append(rec)

    for code in by_team:
        by_team[code].sort(key=lambda x: (x["state"] != "Out", x["state"] != "Questionable", x["player"] or ""))
    return {
        "available": True,
        "capture_run_id": cur["run_id"],
        "previous_capture_run_id": prev["run_id"] if prev else None,
        "diff_basis": ("compared against the previous capture" if prev else
                       "NO PREVIOUS CAPTURE -- nothing can be marked new"),
        "by_team": dict(by_team),
    }


_AVAILABILITY_CANON = {
    "out": "OUT", "injured reserve": "OUT", "ir": "OUT", "pup": "OUT", "na": "OUT",
    "suspension": "OUT", "sus": "OUT", "nfi": "OUT", "dnr": "OUT",
    "doubtful": "DOUBTFUL", "d": "DOUBTFUL",
    "questionable": "QUESTIONABLE", "q": "QUESTIONABLE", "limited participation": "QUESTIONABLE",
    "active": "ACTIVE", "": "ACTIVE",
}


def _canon_availability(s):
    """Collapse the two feeds' vocabularies onto one severity scale."""
    return _AVAILABILITY_CANON.get(str(s or "").strip().lower(), "UNKNOWN")


def _role_impact(status, position):
    s = _canon_availability(status)
    if s == "OUT":
        return "ruled out -- role redistributes to the depth chart behind him" if position in (
            "QB", "RB", "WR", "TE") else "ruled out"
    if s == "QUESTIONABLE":
        return "uncertain -- resolves at the inactive release, 90 minutes before kickoff"
    if s == "DOUBTFUL":
        return "unlikely to play"
    return "no expected impact"


def role_state(context_runs: list, teams: set) -> dict:
    """Expected roles from the Sleeper depth chart, which is the freshest role signal we capture.

    At Week 1 there is no current-season usage to lean on, so the depth chart carries more weight than it
    would in week 10 and the packet says so rather than implying measured snap shares exist.
    """
    if not context_runs:
        return {"available": False}
    cur = context_runs[-1]
    players = ((cur.get("sleeper") or {}).get("players") or {})
    by_team = defaultdict(lambda: defaultdict(list))
    for p in players.values():
        code, pos = p.get("team"), p.get("depth_chart_position") or p.get("position")
        if code not in teams or not pos or p.get("depth_chart_order") is None:
            continue
        if pos not in ("QB", "RB", "WR", "TE", "FB", "LWR", "RWR", "SWR"):
            continue
        by_team[code][pos].append({
            "player": p.get("full_name"),
            "depth_chart_order": p.get("depth_chart_order"),
            "position": p.get("position"),
            "status": p.get("status"),
            "injury_status": p.get("injury_status"),
        })
    out = {}
    for code, pos_map in by_team.items():
        out[code] = {pos: sorted(v, key=lambda x: x["depth_chart_order"])[:5] for pos, v in pos_map.items()}
    return {
        "available": bool(out),
        "capture_run_id": cur["run_id"],
        "source": "sleeper depth chart",
        "caveat": ("Depth-chart order is a stated intention, not a measured snap share. No 2026 snaps have "
                   "been played, so no in-season usage exists to confirm it."),
        "by_team": out,
    }


def weather_state(context_runs: list, game_id: str) -> dict:
    """Forecast for one game with its vintage, and whether it materially changed since the last capture."""
    def find(run):
        for w in (run or {}).get("weather", []):
            if w.get("game_id") == game_id:
                return w
        return None
    cur = find(context_runs[-1]) if context_runs else None
    prev = find(context_runs[-2]) if len(context_runs) > 1 else None
    if not cur:
        return {"available": False, "reason": "no weather row captured for this game"}
    roof = cur.get("roof")
    out = {
        "available": True,
        "roof": roof,
        "surface": cur.get("surface"),
        "stadium": cur.get("stadium_schedule") or cur.get("stadium_config"),
        "neutral_site": cur.get("neutral"),
        "forecast_vintage": (cur.get("nws") or {}).get("generated"),
        "forecast_updated": (cur.get("nws") or {}).get("updated"),
        "capture_run_id": context_runs[-1]["run_id"],
    }
    if roof in ("dome", "closed", "indoors"):
        out["material"] = False
        out["note"] = f"roof is {roof} -- weather is not a factor"
        return out
    per = _kickoff_period(cur)
    if per:
        out.update({
            "temperature_f": per.get("temperature"),
            "wind": per.get("windSpeed"),
            "wind_direction": per.get("windDirection"),
            "precipitation_probability": ((per.get("probabilityOfPrecipitation") or {}).get("value")),
            "short_forecast": per.get("shortForecast"),
            "period_start": per.get("startTime"),
        })
    if prev:
        pper = _kickoff_period(prev)
        if pper and per:
            out["previous"] = {"temperature_f": pper.get("temperature"), "wind": pper.get("windSpeed"),
                               "precipitation_probability": (pper.get("probabilityOfPrecipitation") or {}).get("value")}
            out["changed_since_previous_capture"] = (
                pper.get("windSpeed") != per.get("windSpeed")
                or pper.get("temperature") != per.get("temperature")
                or (pper.get("probabilityOfPrecipitation") or {}).get("value")
                != (per.get("probabilityOfPrecipitation") or {}).get("value"))
    out["material"] = _weather_material(out)
    return out


def _kickoff_period(w):
    """The NWS hourly period containing kickoff. Never the first period in the file."""
    ko = _iso(w.get("kickoff_utc"))
    periods = ((w.get("nws") or {}).get("periods") or [])
    if not ko or not periods:
        return None
    best = None
    for p in periods:
        st, en = _iso(p.get("startTime")), _iso(p.get("endTime"))
        if st and en and st <= ko < en:
            return p
        if st and (best is None or abs((st - ko).total_seconds()) < abs((_iso(best["startTime"]) - ko).total_seconds())):
            best = p
    return best


def _weather_material(w):
    """Wind is the only forecast variable with a defensible NFL scoring effect at typical magnitudes."""
    wind = str(w.get("wind") or "")
    mph = 0
    for tok in wind.replace("to", " ").split():
        if tok.isdigit():
            mph = max(mph, int(tok))
    pop = w.get("precipitation_probability") or 0
    if mph >= 15 or (pop and pop >= 60):
        return True
    return False


# ======================================================================================================
# matchup, questions, expressions, correlation
# ======================================================================================================

MATCHUP_PAIRS = [
    ("pass offense vs pass defense", "off_db_epa", "def_db_epa"),
    ("run offense vs run defense", "off_rush_epa", "def_rush_epa"),
    ("early-down efficiency", "off_ed_epa", "def_ed_epa"),
    ("explosive plays", "off_explosive", "def_explosive"),
    ("overall efficiency", "off_epa", "def_epa"),
    ("neutral-script efficiency", "off_epa_ng", "def_epa_ng"),
    ("pass protection vs pass rush", "off_sack_rate", "def_sack_rate"),
]


def matchup_advantages(profiles: dict, home: str, away: str) -> dict:
    """Adjusted offence against adjusted defence, both directions.

    These are ratings differences, not predictions. A positive edge means one unit rated better than the
    other faced; whether the market has already priced it is exactly the question the handicapper answers.
    """
    hp, ap = profiles.get(home) or {}, profiles.get(away) or {}
    ha, aa = hp.get("adjusted") or {}, ap.get("adjusted") or {}
    if not ha or not aa:
        return {"available": False, "reason": "adjusted ratings unavailable for one or both teams"}
    out = {"available": True, "basis": (profiles.get("_meta") or {}).get("basis"), "pairs": []}
    for label, off_key, def_key in MATCHUP_PAIRS:
        for oteam, oprof, dteam, dprof in ((home, ha, away, aa), (away, aa, home, ha)):
            o, d = oprof.get(off_key), dprof.get(def_key)
            if o is None or d is None:
                continue
            # Defensive ratings are stored as points allowed above average: lower is better, so a good
            # defence (negative) reduces the offence's expected edge.
            edge = round(o - d, 5)
            if off_key == "off_sack_rate":
                edge = round(-(o) - d, 5)     # sacks allowed and sacks generated both hurt the offence
            out["pairs"].append({"matchup": label, "offense": oteam, "defense": dteam,
                                 "offense_rating": o, "defense_rating": d, "advantage_to_offense": edge})
    out["pairs"].sort(key=lambda x: -abs(x["advantage_to_offense"]))
    out["note"] = "Adjusted rating differences. NOT a claim that the market has mispriced them."
    return out


def key_questions(game: dict) -> list:
    """3-8 questions aimed at reasoning, not ranking.

    Generated from conditions actually detected in this game's data. The point is to make the handicapper
    confront the specific way this packet could be wrong, rather than to rank probabilities.
    """
    q = []
    inj = (game.get("injuries") or {}).get("records") or []
    out_players = [r for r in inj if _canon_availability(r.get("state")) == "OUT"
                   and r.get("position") in ("QB", "RB", "WR", "TE")]
    quest = [r for r in inj if _canon_availability(r.get("state")) == "QUESTIONABLE"
             and r.get("position") in ("QB", "RB", "WR", "TE")]
    for r in out_players[:2]:
        q.append(f"{r['player']} ({r['position']}, {r['team']}) is ruled out. Is the market's price on his "
                 f"replacement's usage already reflecting the redistributed role, or still anchored to a "
                 f"committee?")
    if quest:
        names = ", ".join(f"{r['player']} ({r['position']})" for r in quest[:3])
        q.append(f"{len(quest)} skill players are Questionable ({names}). These resolve at the inactive "
                 f"release 90 minutes before kickoff — is any current price worth taking before that, or is "
                 f"the option value of waiting larger than the move you expect?")
    w = game.get("weather") or {}
    if w.get("material"):
        q.append(f"Wind/precipitation is flagged material ({w.get('wind')}, "
                 f"{w.get('precipitation_probability')}% precip). Is that already in the total, and does the "
                 f"forecast vintage ({w.get('forecast_vintage')}) predate the last big market move?")
    elif w.get("changed_since_previous_capture"):
        q.append("The forecast changed since the previous capture but is not flagged material. Does the "
                 "market appear to have reacted to it anyway?")
    mv = game.get("largest_moves") or []
    if mv:
        m = mv[0]
        q.append(f"{m['ticker']} moved {m['move']:+.3f} since first capture. Is that move explained by "
                 f"public injury news already in this packet, or is it information we do not have?")
    dis = game.get("largest_disagreements") or []
    for d in dis[:2]:
        who = d.get("player_name") or d.get("family")
        q.append(f"The model disagrees by {d['disagreement_vs_mid']:+.3f} on {d['ticker']} ({who}). Is that "
                 f"a mean disagreement the market has historically handled better, or a genuine shape "
                 f"difference? Note the model was shown redundant to the market on player props.")
    lad = game.get("tail_rungs") or []
    if lad:
        t = lad[0]
        q.append(f"{t['ticker']} sits at a market price of {t['mid']:.2f} — a tail rung. The tail of the "
                 f"model's distribution is the least validated part of it. Is this rung relying on shape "
                 f"the model is known to miscalibrate?")
    gm = game.get("market_implied") or {}
    if gm.get("implied_spread") is not None and (game.get("model_view") or {}).get("model_spread") is not None:
        d = game["model_view"]["model_spread"] - gm["implied_spread"]
        if abs(d) >= 1.0:
            q.append(f"Model and market differ by {d:+.1f} points of spread. Does that come from one team's "
                     f"rating, from the total, or from a single ladder rung driving the reconstruction?")
    if not q:
        q.append("Nothing in this game is flagged. Is there a reason to have an opinion here at all, or is "
                 "the correct action to pass and preserve bankroll for a game with a live edge?")
    return q[:8]


# Thesis groups: markets that express the SAME underlying football view. Grouping them is what lets the
# handicapper pick the best payout for a thesis rather than the largest raw model disagreement.
def best_expressions(game: dict) -> list:
    markets = game.get("markets") or []
    home, away = game["home_team"], game["away_team"]
    groups = defaultdict(list)
    for m in markets:
        fam, team, stat = m.get("family"), m.get("team"), m.get("stat")
        if (m.get("period") or "FULL") != "FULL":
            continue
        for side_team in (home, away):
            if fam == "GAME_WINNER" and team == side_team:
                groups[f"{side_team}_WINS"].append(m)
            elif fam == "SPREAD" and team == side_team:
                groups[f"{side_team}_WINS"].append(m)
            elif fam == "TEAM_TOTAL" and team == side_team:
                groups[f"{side_team}_SCORES"].append(m)
        if fam == "TOTAL":
            groups["GAME_SCORING"].append(m)
        if fam == "TOTAL_TD":
            groups["GAME_SCORING"].append(m)
        if fam in PLAYER_FAMILIES and m.get("player_name"):
            groups[f"PLAYER::{m['player_name']}"].append(m)
    out = []
    for name, ms in sorted(groups.items()):
        if len(ms) < 2:
            continue
        ms = sorted(ms, key=lambda x: (x.get("family") or "", x.get("threshold") if x.get("threshold") is not None else 0))
        out.append({
            "thesis": name,
            "n_expressions": len(ms),
            "expressions": [{"ticker": m["ticker"], "family": m["family"], "stat": m.get("stat"),
                             "threshold": m.get("threshold"), "yes_ask": m.get("yes_ask"),
                             "no_ask": m.get("no_ask"), "mid": m.get("mid"),
                             "model_probability": m.get("model_probability"),
                             "disagreement_vs_mid": m.get("disagreement_vs_mid"),
                             "support_state": m.get("support_state")} for m in ms[:24]],
            "note": ("Same football thesis, different payouts. The largest model disagreement is NOT "
                     "automatically the best expression -- compare price, width and how much of the thesis "
                     "each contract actually requires."),
        })
    out.sort(key=lambda g: -g["n_expressions"])
    return out


def correlation_groups(game: dict) -> list:
    """Qualitative correlation tags.

    No quantitative correlation matrix exists for these contracts, and inventing one would be worse than
    saying so. What is provided is the grouping and direction, which is what staking needs to avoid
    accidentally taking the same bet four times.
    """
    gid = game["game_id"]
    groups = [
        {"correlation_group": f"{gid}::SCORING_UP", "direction": "same",
         "strength": "strong (qualitative)",
         "members": ["game total over", "either team total over", "QB passing yards over",
                     "receiver yards/receptions over", "anytime TD yes", "total TDs over"],
         "note": "These rise and fall together with game scoring and pace."},
        {"correlation_group": f"{gid}::{game['home_team']}_SIDE", "direction": "same",
         "strength": "strong (qualitative)",
         "members": [f"{game['home_team']} moneyline", f"{game['home_team']} spread",
                     f"{game['home_team']} team total over", f"{game['home_team']} player props over"],
         "note": "Team-side markets share the same game-script risk."},
        {"correlation_group": f"{gid}::GAME_SCRIPT_OPPOSED", "direction": "opposed",
         "strength": "moderate (qualitative)",
         "members": ["favourite rushing volume over", "favourite passing volume over"],
         "note": "A team that leads runs more and throws less; volume props on the same team can conflict."},
    ]
    return groups


# ======================================================================================================
# assembly
# ======================================================================================================

def _health_flags(game_rows: list, weather: dict, injuries: dict, now, kickoff) -> list:
    """Granular fail-closed reasons. One bad prop never invalidates a whole game."""
    flags = []
    if kickoff and now >= kickoff:
        flags.append({"code": "GAME_STARTED", "severity": "block",
                      "detail": "kickoff has passed; this is not a pregame packet"})
    if not game_rows:
        flags.append({"code": "NO_MARKETS", "severity": "block", "detail": "no markets joined this game"})
        return flags
    stale = [r for r in game_rows
             if (_f(r.get("minutes_since_price_change")) or 0) > STALE_QUOTE_MIN]
    if len(stale) > 0.5 * len(game_rows):
        flags.append({"code": "MOSTLY_UNCHANGED_QUOTES", "severity": "warn",
                      "detail": f"{len(stale)}/{len(game_rows)} quotes unchanged >{STALE_QUOTE_MIN:.0f}m. "
                                "The capture is change-suppressed, so this means the price has not MOVED, "
                                "not that the feed is broken."})
    noquote = [r for r in game_rows if _f(r.get("mid")) is None]
    if noquote:
        flags.append({"code": "QUOTE_MISSING", "severity": "warn",
                      "detail": f"{len(noquote)} markets carry no usable quote"})
    unresolved = [r for r in game_rows if r.get("support_state") == "UNSUPPORTED_IDENTITY"]
    if unresolved:
        flags.append({"code": "MAPPING_UNKNOWN", "severity": "warn",
                      "detail": f"{len(unresolved)} player markets have an unresolved Kalshi->GSIS identity; "
                                "they are shown but carry no model view"})
    rules = [r for r in game_rows if r.get("support_state") == "UNSUPPORTED_RULES"]
    if rules:
        flags.append({"code": "SETTLEMENT_SEMANTICS_UNRESOLVED", "severity": "warn",
                      "detail": f"{len(rules)} markets have unestablished settlement semantics"})
    if not weather.get("available"):
        flags.append({"code": "WEATHER_MISSING", "severity": "warn",
                      "detail": weather.get("reason", "no forecast captured")})
    if not injuries.get("available"):
        flags.append({"code": "INJURY_STATE_MISSING", "severity": "warn", "detail": "no context capture"})
    elif injuries.get("previous_capture_run_id") is None:
        flags.append({"code": "NO_INJURY_DIFF", "severity": "warn",
                      "detail": "only one context capture exists; nothing can be marked new"})
    shas = {r.get("model_artifact_sha") for r in game_rows if r.get("model_artifact_sha")}
    if len(shas) > 1:
        flags.append({"code": "ARTIFACT_MISMATCH", "severity": "block",
                      "detail": f"more than one model artifact in one game: {sorted(shas)}"})
    return flags


def build_game(game_id, rows, *, profiles, qb_profiles, context_runs, movement, now, implied):
    home = next((r.get("home_team") for r in rows if r.get("home_team")), None)
    away = next((r.get("away_team") for r in rows if r.get("away_team")), None)
    kickoff = _iso(next((r.get("kickoff_utc") for r in rows if r.get("kickoff_utc")), None))
    teams = {t for t in (home, away) if t}

    markets = [market_row(r) for r in rows]
    for m, r in zip(markets, rows):
        m["movement"] = movement_for(m["ticker"], movement, kickoff, now) if movement else None

    weather = weather_state(context_runs, game_id)
    inj_all = injury_state(context_runs, teams)
    inj_records = []
    for t in sorted(teams):
        for rec in (inj_all.get("by_team") or {}).get(t, []):
            rec = dict(rec); rec["team"] = t
            inj_records.append(rec)
    roles = role_state(context_runs, teams)

    market_view = game_market_implied(rows, home, away, "FULL", "mid")
    model_view = game_market_implied(rows, home, away, "FULL", "model_contract_value")
    periods = {}
    for per in ("1H", "2H", "1Q", "2Q", "3Q", "4Q"):
        pv = game_market_implied(rows, home, away, per, "mid")
        if pv.get("implied_total_median") is not None or pv.get("implied_spread") is not None:
            periods[per] = {k: v for k, v in pv.items() if "distribution" not in k}

    supported = [m for m in markets if m.get("model_probability") is not None]
    rankable = [m for m in supported
                if m.get("disagreement_vs_mid") is not None and m.get("tradable_for_disagreement_ranking")]
    excluded_wide = [m for m in supported
                     if m.get("disagreement_vs_mid") is not None
                     and not m.get("tradable_for_disagreement_ranking")]
    disagreements = sorted(rankable, key=lambda m: -abs(m["disagreement_vs_mid"]))
    moves = []
    for m in markets:
        mv = (m.get("movement") or {}).get("total_move_since_first_capture")
        if mv is not None and abs(mv) > 0:
            moves.append({"ticker": m["ticker"], "family": m["family"], "move": mv,
                          "player_name": m.get("player_name")})
    moves.sort(key=lambda x: -abs(x["move"]))
    tails = sorted([m for m in rankable if m.get("mid") is not None
                    and (m["mid"] <= 0.12 or m["mid"] >= 0.88)],
                   key=lambda m: -abs(m.get("disagreement_vs_mid") or 0))

    mv_ver = next((r.get("model_version") for r in rows if r.get("model_version")), None)
    sha = next((r.get("model_artifact_sha") for r in rows if r.get("model_artifact_sha")), None)
    cutoff = next((r.get("feature_cutoff") for r in rows if r.get("feature_cutoff")), None)

    game = {
        "game_id": game_id,
        "season": next((r.get("season") for r in rows if r.get("season")), None),
        "week": next((r.get("week") for r in rows if r.get("week")), None),
        "kickoff_utc": kickoff.isoformat() if kickoff else None,
        "kickoff_timezone": "UTC (all packet timestamps are UTC)",
        "minutes_to_kickoff": (None if not kickoff else round((kickoff - now).total_seconds() / 60.0, 1)),
        "home_team": home, "away_team": away,
        "venue": weather.get("stadium"),
        "roof": weather.get("roof"), "surface": weather.get("surface"),
        "neutral_site": weather.get("neutral_site"),
        "game_state": "PREGAME" if (kickoff and now < kickoff) else "STARTED_OR_UNKNOWN",
        "data_freshness": {
            "packet_built_at": now.isoformat(),
            "ledger_feature_cutoff": cutoff,
            "context_capture": (context_runs[-1]["run_id"] if context_runs else None),
            "previous_context_capture": (context_runs[-2]["run_id"] if len(context_runs) > 1 else None),
        },
        "counts": {
            "markets_listed": len(markets),
            "supported": sum(1 for m in markets if m["support_state"] == "SUPPORTED"),
            "unsupported_model": sum(1 for m in markets if m["support_state"] == "UNSUPPORTED_MODEL"),
            "unsupported_rules": sum(1 for m in markets if m["support_state"] == "UNSUPPORTED_RULES"),
            "mapping_unknown": sum(1 for m in markets if m["support_state"] == "UNSUPPORTED_IDENTITY"),
            "families": len({m["family"] for m in markets}),
        },
        "market_implied": market_view,
        "market_implied_by_period": periods,
        "model_view": {
            "model_version": mv_ver, "artifact_hash": sha, "feature_cutoff": cutoff,
            "model_spread": model_view.get("implied_spread"),
            "model_total": model_view.get("implied_total_median"),
            "model_score": model_view.get("implied_score"),
            "model_win_probability": model_view.get("win_probability"),
            "reconstruction": model_view.get("label"),
            "caveat": ("The model has been shown redundant to the closing market on player props and behind "
                       "it on game outcomes. Treat it as structure, not as a superior forecast."),
        },
        "team_profiles": {t: profiles.get(t) for t in sorted(teams)},
        "quarterbacks": _qb_section(roles, qb_profiles, teams),
        "offensive_line": _ol_section(inj_records, teams),
        "roles": roles,
        "injuries": {"summary": {k: v for k, v in inj_all.items() if k != "by_team"},
                     "records": inj_records},
        "weather": weather,
        "matchup": matchup_advantages(profiles, home, away),
        "players": player_projection_blocks(rows, implied, game_id),
        "markets": markets,
        "largest_disagreements": [
            {k: m.get(k) for k in ("ticker", "family", "stat", "player_name", "threshold", "mid",
                                   "yes_ask", "no_ask", "model_probability", "disagreement_vs_mid",
                                   "disagreement_yes_executable", "disagreement_no_executable",
                                   "model_uncertainty")}
            for m in disagreements[:25]],
        "disagreement_ranking_basis": {
            "ranked_markets": len(rankable),
            "excluded_untradable": len(excluded_wide),
            "max_width_ranked": MAX_DISAGREEMENT_WIDTH,
            "note": ("Markets wider than the cap, and untraded 0.00/0.99 books, are present in `markets` "
                     "but never ranked -- their midpoint is a quoting artefact. Without this filter the top "
                     "of every disagreement list is a book nobody has traded."),
        },
        "widest_excluded_examples": [
            {k: m.get(k) for k in ("ticker", "player_name", "stat", "threshold", "width", "volume",
                                   "mid", "model_probability")}
            for m in sorted(excluded_wide, key=lambda m: -(m.get("width") or 0))[:5]],
        "largest_moves": moves[:15],
        "tail_rungs": [{k: m.get(k) for k in ("ticker", "player_name", "stat", "threshold", "mid",
                                              "model_probability", "disagreement_vs_mid")}
                       for m in tails[:10]],
        "data_health": _health_flags(rows, weather, inj_all, now, kickoff),
    }
    game["best_expressions"] = best_expressions(game)
    game["correlation_groups"] = correlation_groups(game)
    game["key_questions"] = key_questions(game)
    return game


def _qb_section(roles, qb_profiles, teams):
    out = {}
    for t in sorted(teams):
        depth = ((roles.get("by_team") or {}).get(t) or {}).get("QB") or []
        entries = []
        for d in depth[:2]:
            name = d.get("player")
            match = None
            if name:
                last = name.split()[-1].lower()
                first = name.split()[0][:1].lower()
                for pid, p in qb_profiles.items():
                    if pid == "_meta" or not isinstance(p, dict) or not p.get("name"):
                        continue
                    nm = p["name"].lower()
                    if nm.endswith(last) and nm.startswith(first):
                        match = p
                        break
            entries.append({
                "player": name,
                "depth_chart_order": d.get("depth_chart_order"),
                "status": d.get("status"),
                "injury_status": d.get("injury_status"),
                "availability_confidence": ("high" if not d.get("injury_status") else "uncertain"),
                "profile": match,
                "profile_matched_by": ("name heuristic" if match else None),
                "note": (None if match else
                         "no play-by-play profile matched -- rookie, new name spelling, or no prior dropbacks"),
            })
        out[t] = entries
    return out


def _ol_section(inj_records, teams):
    """OL availability only. No pass-block win rate exists in our sources and none is invented."""
    OL = {"T", "G", "C", "OL", "OT", "OG"}
    out = {}
    for t in sorted(teams):
        hurt = [r for r in inj_records if r.get("team") == t and (r.get("position") or "") in OL]
        out[t] = {
            "injured_or_listed": [{k: r.get(k) for k in ("player", "position", "state", "detail",
                                                         "likely_role_impact")} for r in hurt],
            "n_listed": len(hurt),
            "detailed_metrics_available": False,
            "note": ("We capture no pass-block or run-block grades and no snap-level continuity, so no "
                     "OL quality metric is reported. Team-level sack rate allowed and pressure proxies are "
                     "in the team profile; they conflate line, quarterback and scheme."),
        }
    return out


def build_packet(md_root: str, root: str, season: int, week: int, *, movement_files=None,
                 now=None) -> dict:
    """The full slate packet."""
    from nfl_edge.handicap.teamprofile import build_profiles, build_qb_profiles
    now = now or datetime.now(timezone.utc)
    rows, manifest, implied, ledger_path = load_latest_ledger(md_root)
    slate = [r for r in rows if r.get("season") == season and r.get("week") == week and r.get("game_id")]
    if not slate:
        raise ValueError(f"no ledger rows for season {season} week {week}")

    by_game = defaultdict(list)
    for r in slate:
        by_game[r["game_id"]].append(r)

    context_runs = load_context(md_root, 2)
    profiles = build_profiles(root, season, week)
    qb_profiles = build_qb_profiles(root, season, week)
    tickers = {r["ticker"] for r in slate}
    movement, n_move_files = load_movement(md_root, tickers, max_files=movement_files)

    games = []
    for gid in sorted(by_game, key=lambda g: (
            _iso(next((r.get("kickoff_utc") for r in by_game[g] if r.get("kickoff_utc")), None))
            or datetime.max.replace(tzinfo=timezone.utc), g)):
        games.append(build_game(gid, by_game[gid], profiles=profiles, qb_profiles=qb_profiles,
                                context_runs=context_runs, movement=movement, now=now, implied=implied))

    packet = {
        "schema_version": PACKET_SCHEMA_VERSION,
        "handicap_run_id": now.strftime("%Y%m%dT%H%M%SZ"),
        "built_at": now.isoformat(),
        "season": season, "week": week,
        "sources": {
            "ledger": os.path.basename(ledger_path),
            "ledger_run_id": manifest.get("run_id"),
            "model_version": manifest.get("model_version"),
            "snapshot_run_id": manifest.get("snapshot_run_id"),
            "context_captures": [c["run_id"] for c in context_runs],
            "capture_files_scanned_for_movement": n_move_files,
            "team_profile_basis": (profiles.get("_meta") or {}).get("basis"),
            "qb_profile_basis": (qb_profiles.get("_meta") or {}).get("basis_season"),
        },
        "real_money_status": "NOT VALIDATED -- this packet recommends nothing and authorises nothing",
        "slate_summary": slate_summary(games, rows, manifest),
        "games": games,
    }
    packet["packet_sha"] = hashlib.sha1(
        json.dumps(packet, sort_keys=True, default=str).encode()).hexdigest()[:20]
    return packet


def slate_summary(games: list, all_rows: list, manifest: dict) -> dict:
    new_inj, major_inj, weather_flags = [], [], []
    for g in games:
        for r in g["injuries"]["records"]:
            if r.get("new_since_previous_capture") or r.get("changed_since_previous_capture"):
                new_inj.append({"game_id": g["game_id"], **{k: r.get(k) for k in
                                ("player", "team", "position", "state", "previous_state")}})
            if _canon_availability(r.get("state")) == "OUT" and r.get("position") in ("QB", "RB", "WR", "TE"):
                major_inj.append({"game_id": g["game_id"], **{k: r.get(k) for k in
                                  ("player", "team", "position", "state")}})
        if (g.get("weather") or {}).get("material"):
            weather_flags.append({"game_id": g["game_id"], "wind": g["weather"].get("wind"),
                                  "precip": g["weather"].get("precipitation_probability")})

    moves = [dict(m, game_id=g["game_id"]) for g in games for m in g["largest_moves"]]
    moves.sort(key=lambda x: -abs(x["move"]))
    dis = [dict(d, game_id=g["game_id"]) for g in games for d in g["largest_disagreements"]]
    dis.sort(key=lambda x: -abs(x.get("disagreement_vs_mid") or 0))
    liq = [{"ticker": m["ticker"], "game_id": g["game_id"], "family": m["family"],
            "volume": m.get("volume"), "open_interest": m.get("open_interest")}
           for g in games for m in g["markets"] if m.get("volume")]
    liq.sort(key=lambda x: -(x["volume"] or 0))

    issues = []
    for g in games:
        for fl in g["data_health"]:
            if fl["severity"] == "block":
                issues.append({"game_id": g["game_id"], **fl})

    return {
        "games": len(games),
        "markets_listed_slate": sum(g["counts"]["markets_listed"] for g in games),
        "markets_supported_slate": sum(g["counts"]["supported"] for g in games),
        "markets_discovered_all_weeks": len(all_rows),
        "ledger_support_states": manifest.get("by_support_state"),
        "new_or_changed_injuries": new_inj[:40],
        "major_skill_injuries_out": major_inj[:40],
        "weather_concerns": weather_flags,
        "largest_market_moves": moves[:15],
        "largest_model_market_disagreements": dis[:20],
        "highest_liquidity_markets": liq[:15],
        "blocking_data_issues": issues,
        "game_priority_for_handicap": game_priority(games),
        "disclaimer": ("Priority ranks where deeper review may be most useful. It is NOT a bet ranking and "
                       "carries no expectation that these games contain value."),
    }


def game_priority(games: list) -> list:
    """Where a human/AI review is most likely to add something. Explicitly not a bet ranking."""
    scored = []
    for g in games:
        reasons, score = [], 0.0
        n_new = sum(1 for r in g["injuries"]["records"]
                    if r.get("new_since_previous_capture") or r.get("changed_since_previous_capture"))
        if n_new:
            score += 2.0 * min(n_new, 4); reasons.append(f"{n_new} new/changed injury records")
        n_out = sum(1 for r in g["injuries"]["records"]
                    if _canon_availability(r.get("state")) == "OUT" and r.get("position") in ("QB", "RB", "WR", "TE"))
        if n_out:
            score += 1.5 * min(n_out, 4); reasons.append(f"{n_out} skill players ruled out (role change)")
        if (g.get("weather") or {}).get("material"):
            score += 3.0; reasons.append("material weather")
        elif (g.get("weather") or {}).get("changed_since_previous_capture"):
            score += 1.0; reasons.append("forecast changed")
        if g["largest_moves"]:
            mx = abs(g["largest_moves"][0]["move"])
            if mx >= 0.03:
                score += min(4.0, mx * 40); reasons.append(f"largest market move {mx:.3f}")
        if g["largest_disagreements"]:
            md = abs(g["largest_disagreements"][0].get("disagreement_vs_mid") or 0)
            if md >= 0.05:
                score += min(4.0, md * 20); reasons.append(f"largest model disagreement {md:.3f}")
        nprops = sum(1 for m in g["markets"] if m["family"] in PLAYER_FAMILIES and m["support_state"] == "SUPPORTED")
        if nprops >= 40:
            score += 1.5; reasons.append(f"{nprops} supported player-prop rungs")
        if any(f["severity"] == "block" for f in g["data_health"]):
            reasons.append("BLOCKING data issue -- review before trusting anything here")
        scored.append({"game_id": g["game_id"], "priority_score": round(score, 2),
                       "reasons": reasons or ["nothing flagged"],
                       "kickoff_utc": g["kickoff_utc"]})
    scored.sort(key=lambda x: -x["priority_score"])
    for i, s in enumerate(scored, 1):
        s["rank"] = i
    return scored
