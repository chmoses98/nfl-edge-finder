"""CANONICAL CLOSE: the last complete valid pre-kickoff market observation of one exact contract, with provenance.

The capture is CHANGE-SUPPRESSED (scripts/kalshi/capture.py): a quote row is written only when the market's
fingerprint moved, so "the last row before kickoff" is the price's last CHANGE, not the last time the price was
looked at. Two instants therefore define a close and both are preserved:

    price_observed_at    the last written pre-kickoff row for the ticker (when the price last changed)
    confirmed_at         the last pre-kickoff capture run that fetched the ticker's series COMPLETELY and in which the
                         ticker was still open (the manifest's per-series `observed_at`; `state.last_seen[ticker]`
                         says the last run the ticker was seen open at all)

close_age_seconds is kickoff minus confirmed_at: how far before kickoff the price was last known to be the live
price. Quality tiers are cut on that age (thresholds below, deliberately named). The rule refuses, with a named
reason, anything that is not a strict pre-kickoff observation of the same contract: post-kickoff rows, rows with
a non-open status, a kickoff that moved after the projection, a capture stamped exactly at kickoff, an empty
side. It never infers a price from a neighbouring rung or a different contract.

Selection rule version: close-2.0.0.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
from datetime import datetime, timezone

from nfl_edge.shadow.quote_history import load_game_quotes

CLOSE_RULE_VERSION = "close-2.0.0"
EXCELLENT, GOOD, STALE, MISSING = "EXCELLENT", "GOOD", "STALE", "MISSING"
# tiers on close_age_seconds (kickoff - confirmation instant). Named once.
TIER_EXCELLENT_S = 20 * 60           # confirmed live within 20 minutes of kickoff
TIER_GOOD_S = 90 * 60                # within 90 minutes
TIER_STALE_S = 24 * 3600             # anything older than a day is not a close at all
HUGE_SPREAD = 0.30                   # a quote wider than 30c is preserved but flagged; CLV on it is segmentable, never hidden
STATUS_OPEN = ("active", "open", None, "")

CLV_CLOSE_MISSING = "CLV_CLOSE_MISSING"
R_NO_PREGAME_ROW = "no pre-kickoff quote row for this ticker"
R_NO_KICKOFF = "no kickoff to select a close against"
R_KICKOFF_MOVED = "kickoff moved after the projection; close refused (fail closed)"
R_STATUS = "last pre-kickoff row is not an open market"
R_ONE_SIDED = "one-sided quote: a side has no price"
R_TOO_OLD = "last confirmation older than the staleness ceiling"


def _dt(s):
    if not s:
        return None
    d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _f(x):
    try:
        return None if x in (None, "") else float(x)
    except (TypeError, ValueError):
        return None


def close_id(ticker: str, run_id: str | None, confirmed_at: str | None) -> str:
    return hashlib.sha256(f"{ticker}|{run_id}|{confirmed_at}|{CLOSE_RULE_VERSION}".encode()).hexdigest()[:20]


def quality_tier(age_s: float | None) -> str:
    if age_s is None:
        return MISSING
    if age_s <= TIER_EXCELLENT_S:
        return EXCELLENT
    if age_s <= TIER_GOOD_S:
        return GOOD
    if age_s <= TIER_STALE_S:
        return STALE
    return MISSING


class CaptureRuns:
    """Manifests (per-series confirmation instants) and the capture state (last run each ticker was seen open)."""

    def __init__(self, capture_root: str):
        self.root = capture_root
        self.manifests = {}                     # run_id -> manifest
        for p in sorted(glob.glob(os.path.join(capture_root, "*", "*.manifest.json"))):
            try:
                m = json.load(open(p))
            except (OSError, ValueError):
                continue
            self.manifests[m.get("run_id") or os.path.basename(p)[:16]] = m
        st = os.path.join(capture_root, "state.json")
        self.last_seen = {}
        if os.path.exists(st):
            try:
                self.last_seen = json.load(open(st)).get("last_seen") or {}
            except (OSError, ValueError):
                self.last_seen = {}

    def confirmation(self, ticker: str, series: str, kickoff: datetime) -> dict:
        """The last pre-kickoff run in which the series was fetched completely and the ticker was still open."""
        seen_run = self.last_seen.get(ticker)
        best = None
        for run_id in sorted(self.manifests):
            m = self.manifests[run_id]
            s = (m.get("series") or {}).get(series)
            if not s:
                continue
            obs = _dt(s.get("observed_at")) or _dt(m.get("finished_at"))
            if obs is None or obs >= kickoff:
                continue
            if seen_run and run_id > seen_run:
                continue                          # the ticker had already vanished from the open set
            if best is None or obs > best["confirmed_at_dt"]:
                best = {"run_id": run_id, "confirmed_at_dt": obs, "confirmed_at": obs.isoformat(), "complete": bool(s.get("complete")),
                        "tier": s.get("tier"), "n_in_series": s.get("n"), "partial_run": bool(m.get("partial"))}
        return best or {}


class CloseIndex:
    """Closes for every ticker of one game, built once from the capture (bounded to the game's days)."""

    def __init__(self, capture_root: str, game_id: str, kickoff_utc: str, *, runs: CaptureRuns | None = None, days_back: int = 14):
        self.game_id = game_id
        self.kickoff = _dt(kickoff_utc)
        self.runs = runs or CaptureRuns(capture_root)
        self.quotes, self.stats = load_game_quotes(capture_root, game_id, kickoff_utc=kickoff_utc, days_back=days_back)
        self._raw = {}
        # duplicates (the same run writing the same ticker twice) collapse to one row per (run_id, observed_at)
        for t, rows in self.quotes.items():
            seen = set(); keep = []
            for q in rows:
                k = (q.get("run_id"), q.get("observed_at"))
                if k in seen:
                    continue
                seen.add(k); keep.append(q)
            self.quotes[t] = keep

    def select(self, ticker: str, *, series_ticker: str | None = None, projection_kickoff_utc: str | None = None) -> dict:
        """The canonical close record for one exact ticker, or a refusal carrying CLV_CLOSE_MISSING and its reason."""
        base = {"ticker": ticker, "game_id": self.game_id, "close_rule_version": CLOSE_RULE_VERSION, "kickoff_utc": self.kickoff.isoformat() if self.kickoff else None,
                "close_status": CLV_CLOSE_MISSING, "close_reason": None, "close_quality": MISSING, "close_id": None, "flags": []}
        if self.kickoff is None:
            base["close_reason"] = R_NO_KICKOFF
            return base
        if projection_kickoff_utc and _dt(projection_kickoff_utc) != self.kickoff:
            base.update(close_reason=R_KICKOFF_MOVED, flags=["KICKOFF_CHANGED"], projection_kickoff_utc=projection_kickoff_utc)
            return base
        rows = [q for q in self.quotes.get(ticker, []) if q.get("observed_ts") is not None and datetime.fromtimestamp(q["observed_ts"], tz=timezone.utc) < self.kickoff]
        if not rows:
            n_post = len(self.quotes.get(ticker, []))
            base["close_reason"] = R_NO_PREGAME_ROW + (f" ({n_post} post-kickoff rows ignored)" if n_post else "")
            return base
        last = rows[-1]
        if last.get("status") not in STATUS_OPEN:
            base.update(close_reason=f"{R_STATUS}: status={last.get('status')!r}", flags=["NOT_OPEN_AT_LAST_ROW"])
            return base
        series = series_ticker or ticker.rsplit("-", 2)[0]
        conf = self.runs.confirmation(ticker, series, self.kickoff)
        confirmed_at = conf.get("confirmed_at") or last.get("observed_at")
        confirmed_dt = _dt(confirmed_at)
        age_s = (self.kickoff - confirmed_dt).total_seconds() if confirmed_dt else None
        price_age_s = (self.kickoff - datetime.fromtimestamp(last["observed_ts"], tz=timezone.utc)).total_seconds()
        flags = []
        if not conf:
            flags.append("NO_CONFIRMING_RUN")          # price row exists but no manifest proves a later complete fetch
        elif not conf.get("complete"):
            flags.append("SERIES_FETCH_INCOMPLETE")
        yb, ya, nb, na = last.get("yes_bid"), last.get("yes_ask"), last.get("no_bid"), last.get("no_ask")
        one_sided = (yb is None or ya is None or nb is None or na is None) or (yb is not None and yb <= 0.0 and na is not None and na >= 1.0) or (ya is not None and ya >= 1.0 and nb is not None and nb <= 0.0)
        if one_sided:
            flags.append("ONE_SIDED")
        if yb is not None and ya is not None and (ya - yb) > HUGE_SPREAD:
            flags.append("HUGE_SPREAD")
        if age_s is not None and age_s > TIER_STALE_S:
            base.update(close_reason=R_TOO_OLD, flags=flags + ["TOO_OLD"], close_age_seconds=age_s)
            return base
        tier = quality_tier(age_s)
        rec = {**base, "close_status": ("CLOSE_ONE_SIDED" if one_sided else "CLOSE_OK"), "close_reason": (R_ONE_SIDED if one_sided else None), "close_quality": tier,
               "close_id": close_id(ticker, conf.get("run_id") or last.get("run_id"), confirmed_at), "flags": flags,
               "close_source_snapshot": conf.get("run_id") or last.get("run_id"), "price_source_run": last.get("run_id"),
               "confirmed_at": confirmed_at, "price_observed_at": last.get("observed_at"),
               "close_age_seconds": age_s, "price_change_age_seconds": price_age_s,
               "minutes_before_kickoff": (age_s / 60.0) if age_s is not None else None,
               "yes_bid": yb, "yes_ask": ya, "no_bid": nb, "no_ask": na,
               "mid": last.get("mid"), "no_mid": ((nb + na) / 2.0 if (nb is not None and na is not None) else None),
               "quote_width": last.get("quote_width"), "volume": last.get("volume"), "open_interest": last.get("open_interest"),
               "liquidity": last.get("liquidity"), "last_price": last.get("last_price"),
               "capture_completeness": {"series_complete": conf.get("complete"), "partial_run": conf.get("partial_run"), "tier": conf.get("tier"), "n_in_series": conf.get("n_in_series")},
               "market_quality": {"status": last.get("status"), "n_pregame_rows": len(rows), "n_rows_total": len(self.quotes.get(ticker, []))}}
        return rec


def build_indexes(capture_root: str, games: dict, days_back: int = 14) -> dict:
    """games: game_id -> kickoff_utc. One CloseIndex per game; the CaptureRuns are shared."""
    runs = CaptureRuns(capture_root)
    return {gid: CloseIndex(capture_root, gid, ko, runs=runs, days_back=days_back) for gid, ko in games.items() if ko}
