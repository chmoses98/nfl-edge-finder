#!/usr/bin/env python3
"""Export the Edge Finder app payload (`app/latest`) from a RUN NFL report plus the handicap-data ledger.

    python3 scripts/app_export.py --reports-dir data/handicap_report --handicap-root /path/to/handicap-data \
        [--market-data-root /tmp/md] [--horizon-state state/horizons.json] --out <staging>/app/latest \
        [--now 2026-10-02T00:30:00Z] [--commit-sha X] [--workflow-run-id Y]

A PURE ADAPTER. It reads what the repository already publishes and re-expresses it in the vendored
`edge_finder_contract` objects (contract/edge_finder_contract/). It changes no model, no gate, no stake and
no authority:

    events        latest/manifest.json kickoffs + latest/analysis/games/<game_id>.json headers
                  (identity: nflverse game id, e.g. 2026_04_PIT_CLE; teams: nflverse 3-letter codes)
    markets       one per analysis row (one per executable Kalshi contract on the slate)
    model_prices  the INCUMBENT production shadow model (`incumbent.model_probability`) where it is
                  SUPPORTED; Shadow v2 and the coherent simulation ride along in `extensions` as research
    recommendations  the handicap-data decision ledger (RECOMMENDED / PASS / WATCHLIST / RESEARCH_ALERT);
                  test_only records are excluded, amendment chains collapsed, exactly as the repo's own readers do
    wagers        handicap-data imported_wagers (owner orders imported from the Kalshi router)
    settlements   handicap-data wager_settlements with the newest admissible economics amendment applied
    health        freshness of the Kalshi capture and the model against the report cadence

Never: the bridge, preflight, credentials, or any write to a data branch. The handicap-data checkout is read
with `nfl_edge.handicap.store` (read-only) and never written.

On any failure the exporter writes ONLY health.json (export_failed=True, the previous payload untouched) and
exits 1, so the workflow goes red without replacing a good payload with half of one.
"""
from __future__ import annotations

import argparse
import ast
import csv
import json
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "contract"))

from edge_finder_contract import board, build, freshness, health, ids, linkage, performance, publish, timeutil  # noqa: E402
# Module-form imports on purpose: the isolation walker (nfl_edge.handicap.report_isolation) treats
# `from nfl_edge.handicap import x` as reaching the whole package, and this script must provably reach only
# the ledger READER, the amendment view, the horizon clock and the ticker classifier.
import nfl_edge.handicap.horizons as horizons_mod  # noqa: E402
import nfl_edge.handicap.settlement_amendments as settlement_amendments  # noqa: E402
import nfl_edge.handicap.store as store  # noqa: E402
import nfl_edge.kalshi.classifier as classifier  # noqa: E402

SPORT = "NFL"
REPO = "chmoses98/nfl-edge-finder"
SOURCE_BRANCH = "handicap-reports"
BET_AUTHORITY = "MANUAL"            # ChatGPT -> ledger -> preflight gate -> the owner places by hand
EVENT_SOURCE = "nflverse_game_id"
TEAM_SOURCE = "nflverse_team"
PLAYER_SOURCE_GSIS = "gsis_id"
PLAYER_SOURCE_KALSHI = "kalshi_player_id"
WAGER_SOURCE = "KALSHI_ROUTER"
LEDGER_SOURCE = "handicap-data"
REPORT_SOURCE = "handicap-reports:latest/analysis"

# Report horizons are T-24h .. T-30m and the shadow cycle re-prices every two hours from an hourly capture, so
# a capture older than 30 minutes is aging and one older than three hours is stale. The model is the ledger
# snapshot the packet was priced from: fresh inside the two-hour cycle, stale after a day.
THRESHOLDS = {
    "market_data": freshness.Thresholds(30 * 60, 3 * 60 * 60),
    "model": freshness.Thresholds(2 * 60 * 60, 24 * 60 * 60),
    # The owner's wagers and their settlements arrive on a weekly cadence, not a polling one.
    "router": freshness.Thresholds(7 * 24 * 60 * 60, 14 * 24 * 60 * 60),
    "settlement": freshness.Thresholds(7 * 24 * 60 * 60, 14 * 24 * 60 * 60),
}

DECISION_STATUS = {"RECOMMENDED": "RECOMMENDED", "PASS": "PASS", "WATCHLIST": "WATCH",
                   "RESEARCH_ALERT": "RESEARCH_CANDIDATE"}
GAME_STATE_STATUS = {"PREGAME": "SCHEDULED"}
SETTLEMENT_RESULT = {"WON": "WON", "LOST": "LOST", "PUSH": "PUSH", "VOID": "VOID", "SCALAR": "SCALAR"}
OVER_FAMILIES = {"TOTAL", "TEAM_TOTAL", "PLAYER_STAT", "TEAM_STAT", "TOTAL_TD", "BOTH_TEAMS_SCORE_N",
                 "SEASON_PLAYER_STAT", "SEASON_WINS", "TEAM_WINS_BY_WEEK"}
MARKET_EXTENSION_KEYS = ("stat", "operator", "subject", "subject_kind", "bucket", "analysis_state", "executable",
                         "no_real_market", "width", "minutes_since_price_change")
SHADOW_V2_KEYS = ("engine", "p_yes", "support_state", "primary_arm", "provenance", "semantic_confidence")
COHERENT_KEYS = ("p_football", "p_market", "p_reconciled", "support_state", "ranked", "reconcile_weight",
                 "football_disagreement_vs_mid", "reconciled_disagreement_vs_mid")
REC_EXTENSION_KEYS = ("decision", "grade", "support_state", "support_reason", "model_version", "model_probability",
                      "proposed_stake", "recommended_stake", "availability_state", "primary_thesis",
                      "key_supporting_factors", "counterarguments", "uncertainties", "reasoning_tags",
                      "correlation_group", "amends", "market_timestamp", "minutes_to_kickoff")


class ExportError(RuntimeError):
    pass


# ----------------------------------------------------------------------------------------------- helpers

def _load(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _ts(value):
    """Aware timestamp or None; a naive value is refused at the contract boundary, never guessed."""
    if value in (None, ""):
        return None
    return timeutil.parse_ts(value)


def _iso(value):
    return timeutil.to_iso_or_none(value)


def _num(value):
    try:
        return None if value in (None, "") else float(value)
    except (TypeError, ValueError):
        return None


def _latest(stamps):
    real = [timeutil.parse_ts(s) for s in stamps if s]
    return max(real) if real else None


def team_names() -> dict:
    """`nfl_edge.data.ids.TEAM_NAMES` without importing the module (it imports polars at module scope)."""
    path = os.path.join(REPO_ROOT, "nfl_edge", "data", "ids.py")
    try:
        tree = ast.parse(open(path, encoding="utf-8").read())
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "TEAM_NAMES" for t in node.targets):
                return ast.literal_eval(node.value)
    except (OSError, SyntaxError, ValueError):
        pass
    return {}


def parse_game_id(game_id: str):
    """`2026_04_PIT_CLE` -> (season, week, away, home) or None."""
    parts = str(game_id or "").split("_")
    if len(parts) != 4 or not (parts[0].isdigit() and parts[1].isdigit()):
        return None
    return int(parts[0]), int(parts[1]), parts[2], parts[3]


def read_schedule(market_data_root) -> dict:
    """game_id -> {kickoff_utc, final} from market-data's schedule_cache.csv (nflverse schedule, ET times)."""
    if not market_data_root:
        return {}
    path = os.path.join(market_data_root, "data", "kalshi", "capture", "schedule_cache.csv")
    if not os.path.exists(path):
        return {}
    try:
        from zoneinfo import ZoneInfo
        eastern = ZoneInfo("America/New_York")
    except Exception:  # noqa: BLE001 -- no tz database: the schedule cannot be placed in UTC honestly
        return {}
    out = {}
    with open(path, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            gid = row.get("game_id")
            if not gid:
                continue
            kickoff = None
            if row.get("gameday") and row.get("gametime"):
                try:
                    local = datetime.strptime(f"{row['gameday']} {row['gametime']}", "%Y-%m-%d %H:%M")
                    kickoff = local.replace(tzinfo=eastern).astimezone(timezone.utc)
                except ValueError:
                    kickoff = None
            out[gid] = {"kickoff_utc": kickoff, "final": bool((row.get("result") or "").strip())}
    return out


# ----------------------------------------------------------------------------------------------- the report

def load_report(reports_dir: str) -> dict:
    manifest_path = os.path.join(reports_dir, "manifest.json")
    if not os.path.exists(manifest_path):
        raise ExportError(f"{reports_dir} has no manifest.json; not a RUN NFL report")
    manifest = _load(manifest_path)
    if manifest.get("report_status") != "SUCCESS":
        raise ExportError(f"report_status is {manifest.get('report_status')!r}; only a SUCCESS report is exported")
    analysis_path = os.path.join(reports_dir, "analysis", "manifest.json")
    if not os.path.exists(analysis_path):
        raise ExportError("analysis/manifest.json missing from the report")
    analysis = _load(analysis_path)
    shards = []
    for entry in sorted(analysis.get("games") or [], key=lambda g: g.get("game_id") or ""):
        path = os.path.join(reports_dir, "analysis", entry.get("path") or f"games/{entry['game_id']}.json")
        if not os.path.exists(path):
            raise ExportError(f"analysis shard missing: {path}")
        shards.append(_load(path))
    return {"manifest": manifest, "analysis": analysis, "shards": shards}


def report_vintages(manifest: dict) -> dict:
    v = manifest.get("vintages") or {}
    kalshi = (v.get("kalshi_capture") or {}).get("queried_at")
    ledger = (v.get("shadow_pricing") or {}).get("written_at")
    context = (v.get("context") or {}).get("captured_at")
    simulation = (v.get("simulation") or {}).get("generated_at")
    built_at = manifest.get("built_at")
    if not built_at:
        raise ExportError("manifest.built_at missing")
    return {
        "built_at": _ts(built_at),
        "kalshi": _ts(kalshi),
        "model": _ts(ledger) or _ts(built_at),
        "context": _ts(context),
        "simulation": _ts(simulation),
    }


# ----------------------------------------------------------------------------------------------- builders

class Exporter:
    def __init__(self, *, reports_dir, handicap_root, market_data_root, horizon_state, now, commit_sha,
                 workflow_run_id):
        self.reports_dir = reports_dir
        self.handicap_root = handicap_root
        self.market_data_root = market_data_root
        self.horizon_state_path = horizon_state
        self.now = now
        self.commit_sha_override = commit_sha
        self.workflow_run_id_override = workflow_run_id
        self.warnings: list[str] = []
        self.team_names = team_names()
        self.events: dict[str, dict] = {}
        self.event_meta: dict[str, dict] = {}
        self.markets: dict[str, dict] = {}
        self.model_prices: list[dict] = []
        self.theses: list[dict] = []
        self.recommendations: list[dict] = []
        self.wagers: list[dict] = []
        self.settlements: list[dict] = []
        self.clv: dict[str, float] = {}
        self.schedule = read_schedule(market_data_root)

    # ---- identities ---------------------------------------------------------------------------------------
    def team_participant(self, code: str) -> dict:
        city, nick = self.team_names.get(code, (None, None))
        display = f"{city} {nick}" if city and nick else code
        return build.participant(sport=SPORT, participant_type="TEAM", source=TEAM_SOURCE, source_id=code,
                                 display_name=display, short_name=code)

    def player_participant_id(self, row: dict):
        if row.get("player_id"):
            return ids.participant_id(SPORT, "PLAYER", PLAYER_SOURCE_GSIS, row["player_id"])
        if row.get("kalshi_player_id"):
            return ids.participant_id(SPORT, "PLAYER", PLAYER_SOURCE_KALSHI, row["kalshi_player_id"])
        return None

    def event_id_for_game(self, game_id: str) -> str:
        return ids.event_id(SPORT, EVENT_SOURCE, game_id)

    # ---- events -------------------------------------------------------------------------------------------
    def add_board_event(self, shard: dict, kickoff_entry: dict, v: dict, manifest: dict) -> dict:
        game_id = shard["game_id"]
        away, home = shard["away_team"], shard["home_team"]
        parts = [self.team_participant(away), self.team_participant(home)]
        kickoff = _ts(shard.get("kickoff_utc") or kickoff_entry.get("kickoff_utc"))
        if kickoff is None:
            raise ExportError(f"{game_id}: no kickoff_utc in the report")
        state = shard.get("game_state") or kickoff_entry.get("game_state")
        coverage = ((shard.get("coverage") or {}).get("buckets") or {})
        ev = build.event(
            sport=SPORT, source=EVENT_SOURCE, source_id=game_id, start_time_utc=kickoff, participants=parts,
            home_participant=parts[1]["participant_id"], away_participant=parts[0]["participant_id"],
            league="NFL", season=str(shard.get("season") or manifest.get("season")),
            competition=f"{manifest.get('season')} {manifest.get('season_type') or 'REG'} week {manifest.get('week')}",
            status=GAME_STATE_STATUS.get(state, "UNKNOWN"),
            start_time_source="nflverse_schedule", start_time_confidence="SCHEDULED",
            source_ids={"slate_id": manifest.get("slate_id"), "away_team": away, "home_team": home},
            schedule_updated_at=v["context"], last_updated_at=v["built_at"],
            extensions={"week": shard.get("week") or manifest.get("week"),
                        "season_type": manifest.get("season_type"), "game_state": state,
                        "on_board": True,
                        "bucket_counts": {k: int(b.get("n") or 0) for k, b in coverage.items()} if coverage else {}},
        )
        self.events[ev["event_id"]] = ev
        self.event_meta[ev["event_id"]] = {"game_id": game_id, "away": away, "home": home, "shard": shard}
        return ev

    def ensure_offboard_event(self, game_id: str, *, kickoff_hint=None, game_date=None) -> str | None:
        """An event a ledger record refers to that is not on the current board (a past week, usually)."""
        parsed = parse_game_id(game_id)
        if parsed is None:
            return None
        eid = self.event_id_for_game(game_id)
        if eid in self.events:
            return eid
        season, week, away, home = parsed
        sched = self.schedule.get(game_id) or {}
        kickoff, source, confidence = None, None, None
        if sched.get("kickoff_utc"):
            kickoff, source, confidence = sched["kickoff_utc"], "nflverse_schedule", "SCHEDULED"
        elif kickoff_hint is not None:
            kickoff, source, confidence = _ts(kickoff_hint), "handicap_ledger_kickoff", "SCHEDULED"
        elif game_date:
            kickoff = datetime.strptime(str(game_date), "%Y-%m-%d").replace(tzinfo=timezone.utc)
            source, confidence = "kalshi_ticker_game_date", "PLACEHOLDER"
        if kickoff is None:
            return None
        if sched.get("final"):
            status = "FINAL"
        elif kickoff > self.now:
            status = "SCHEDULED"
        else:
            status = "UNKNOWN"
        parts = [self.team_participant(away), self.team_participant(home)]
        ev = build.event(
            sport=SPORT, source=EVENT_SOURCE, source_id=game_id, start_time_utc=kickoff, participants=parts,
            home_participant=parts[1]["participant_id"], away_participant=parts[0]["participant_id"],
            league="NFL", season=str(season), competition=f"{season} week {week}", status=status,
            start_time_source=source, start_time_confidence=confidence,
            source_ids={"away_team": away, "home_team": home},
            last_updated_at=self.now,
            extensions={"week": week, "on_board": False, "game_date": game_date},
        )
        self.events[eid] = ev
        self.event_meta[eid] = {"game_id": game_id, "away": away, "home": home, "shard": None}
        return eid

    # ---- markets and model prices --------------------------------------------------------------------------
    def add_row(self, row: dict, event: dict, meta: dict, v: dict, run_id: str, model_version) -> None:
        ticker = (row.get("ticker") or "").strip().upper()
        if not ticker:
            return
        if ticker in self.markets:
            self.warnings.append(f"duplicate ticker on the board: {ticker}")
            return
        sem = classifier.classify({"ticker": ticker})
        family = row.get("family") or sem.family
        subject, kind = row.get("subject"), row.get("subject_kind")
        side, participant_id, player_id = None, None, None
        if kind == "team" and subject:
            side = "HOME" if subject == meta["home"] else "AWAY" if subject == meta["away"] else "PARTICIPANT"
            participant_id = ids.participant_id(SPORT, "TEAM", TEAM_SOURCE, subject)
        elif kind == "player" or row.get("player_id") or row.get("kalshi_player_id"):
            player_id = self.player_participant_id(row)
            side = "PARTICIPANT"
        if row.get("operator") in (">=", ">") and family in OVER_FAMILIES:
            side = "OVER"
        incumbent = row.get("incumbent") or {}
        shadow = row.get("shadow_v2") or {}
        extensions = {k: row.get(k) for k in MARKET_EXTENSION_KEYS}
        for k in ("width", "minutes_since_price_change"):
            if isinstance(extensions.get(k), float):
                extensions[k] = round(extensions[k], 4)
        extensions["incumbent_support_state"] = incumbent.get("support_state")
        extensions["shadow_v2_p_yes"] = shadow.get("p_yes")
        if row.get("player_id"):
            extensions["gsis_id"] = row["player_id"]
        if row.get("kalshi_player_id"):
            extensions["kalshi_player_id"] = row["kalshi_player_id"]
        market = build.market(
            sport=SPORT, kalshi_ticker=ticker, market_family=family, yes_description=row.get("yes_meaning") or ticker,
            source=REPORT_SOURCE, event_id=event["event_id"], kalshi_event_ticker=sem.event_ticker,
            kalshi_series_ticker=sem.series_ticker, period=row.get("period"), participant_id=participant_id,
            player_id=player_id, side=side, threshold=row.get("threshold"),
            yes_bid=row.get("yes_bid"), yes_ask=row.get("yes_ask"), no_bid=row.get("no_bid"), no_ask=row.get("no_ask"),
            market_probability=row.get("mid"), volume=row.get("volume"), open_interest=row.get("open_interest"),
            market_status="OPEN", captured_at=v["kalshi"],
            raw_market_reference=f"analysis/games/{meta['game_id']}.json", extensions=extensions,
        )
        self.markets[ticker] = market
        p = incumbent.get("model_probability")
        if p is None:
            return
        supported = incumbent.get("support_state") == "SUPPORTED"
        coherent = row.get("coherent_simulation") or {}
        self.model_prices.append(build.model_price(
            run_id=run_id, market_id=market["market_id"], fair_probability=p, generated_at=v["model"],
            event_id=event["event_id"], model_version=model_version, uncertainty=incumbent.get("model_uncertainty"),
            market_probability=row.get("mid"), inputs_as_of=v["kalshi"],
            freshness_status=freshness.status_for(v["kalshi"], now=self.now, thresholds=THRESHOLDS["market_data"]),
            data_quality_status="OK" if supported else "UNSUPPORTED", support_status=incumbent.get("support_state"),
            extensions={
                "disagreement_vs_mid": incumbent.get("disagreement_vs_mid"),
                "support_reason": incumbent.get("support_reason"),
                "analysis_state": row.get("analysis_state"), "bucket": row.get("bucket"),
                "shadow_v2": {k: shadow.get(k) for k in SHADOW_V2_KEYS} if shadow else None,
                "coherent_simulation": {k: coherent.get(k) for k in COHERENT_KEYS} if coherent else None,
            },
        ))

    def add_thesis(self, event: dict, shard: dict, run_id: str, v: dict) -> None:
        """No prose is generated here: the per-game document the packet already wrote is the thesis, and the
        app is pointed at it. `summary` stays null rather than becoming a sentence nobody wrote."""
        coverage = ((shard.get("coverage") or {}).get("buckets") or {})
        self.theses.append(build.thesis(
            sport=SPORT, run_id=run_id, event_id=event["event_id"], generated_at=v["built_at"], summary=None,
            evidence={"game_document": f"latest/games/{shard['game_id']}.md",
                      "analysis_shard": f"latest/analysis/games/{shard['game_id']}.json",
                      "bucket_counts": {k: int(b.get("n") or 0) for k, b in coverage.items()},
                      "authority": "research only; the packet recommends nothing"},
        ))

    # ---- the ledger: recommendations ----------------------------------------------------------------------
    def market_stub(self, ticker: str, *, family, yes_description, event_id, settled: bool) -> dict:
        ticker = ticker.strip().upper()
        if ticker not in self.markets:
            self.markets[ticker] = build.market_stub(
                sport=SPORT, kalshi_ticker=ticker, market_family=family or "unknown",
                yes_description=yes_description, event_id=event_id, source=LEDGER_SOURCE,
                market_status="SETTLED" if settled else "UNKNOWN")
        return self.markets[ticker]

    def add_recommendations(self, run_id: str) -> None:
        if not self.handicap_root:
            return
        records = store.latest_amendment_chain(store.read_kind(self.handicap_root, "recommendations"))
        for r in sorted(records, key=lambda x: (x.get("created_at") or "", x["recommendation_id"])):
            decision = r.get("decision")
            if decision not in DECISION_STATUS:
                self.warnings.append(f"recommendation {r['recommendation_id']}: unknown decision {decision!r}")
                continue
            side = (r.get("side") or "YES").upper()
            if side not in ("YES", "NO"):
                self.warnings.append(f"recommendation {r['recommendation_id']}: side {side!r} is not YES/NO")
                continue
            game_id = r.get("game_id")
            eid = self.ensure_offboard_event(game_id, kickoff_hint=r.get("kickoff_utc")) if game_id else None
            if eid is None:
                self.warnings.append(f"recommendation {r['recommendation_id']}: no event for game_id {game_id!r}")
                continue
            event = self.events[eid]
            market = self.market_stub(r["market_ticker"], family=r.get("market_family"),
                                      yes_description=f"YES on {r['market_ticker']}", event_id=eid,
                                      settled=event["status"] == "FINAL")
            ask = r.get("yes_ask") if side == "YES" else r.get("no_ask")
            mid = _num(r.get("mid"))
            current_probability = None if mid is None else (mid if side == "YES" else round(1.0 - mid, 6))
            fair = _num(r.get("probability_mid"))
            edge = round(fair - float(ask), 6) if fair is not None and ask is not None else None
            status = DECISION_STATUS[decision]
            research = status == "RESEARCH_CANDIDATE"
            self.recommendations.append(build.recommendation(
                sport=SPORT, source_repo=REPO, event_id=eid, market_id=market["market_id"], run_id=run_id,
                selection=side, market_description=market["yes_description"], created_at=r["created_at"],
                status=status, authority="RESEARCH_ONLY" if research else BET_AUTHORITY, research_only=research,
                native_id=r["recommendation_id"], current_probability=current_probability, current_price=ask,
                fair_probability=fair, edge=edge, bet_up_to_probability=r.get("bet_up_to_probability"),
                bet_up_to_price=r.get("bet_up_to_probability"), confidence=r.get("grade"),
                stake_dollars=r.get("recommended_stake"), bankroll_basis=r.get("bankroll_snapshot"),
                expires_at=r.get("kickoff_utc"),
                data_freshness=freshness.status_for(r.get("market_timestamp") or r.get("created_at"), now=self.now,
                                                    component="recommendations"),
                lineup_status=r.get("availability_state"),
                source_ids={"recommendation_id": r["recommendation_id"], "handicap_run_id": r.get("handicap_run_id"),
                            "packet_sha": r.get("packet_sha"), "game_id": game_id, "market_ticker": r["market_ticker"]},
                extensions={**{k: r.get(k) for k in REC_EXTENSION_KEYS},
                            "probability_low": r.get("probability_low"), "probability_high": r.get("probability_high"),
                            "frozen_quote": {k: r.get(k) for k in ("yes_bid", "yes_ask", "no_bid", "no_ask", "mid")},
                            "superseded_ids": r.get("_superseded_ids") or []},
            ))

    # ---- the ledger: wagers and settlements ---------------------------------------------------------------
    def add_wagers(self, run_id: str) -> None:
        if not self.handicap_root:
            return
        wagers = store.read_kind(self.handicap_root, "imported_wagers")
        settlements = store.read_kind(self.handicap_root, "wager_settlements")
        amendments = settlement_amendments.read_amendments(self.handicap_root)
        self.clv = self.read_clv()
        by_key: dict[str, dict] = {}
        for s in settlements:
            key = s.get("source_bet_key")
            if key in by_key:
                self.warnings.append(f"two settlements for source_bet_key {key}; keeping the first")
                continue
            by_key[key] = settlement_amendments.canonical_settlement(s, amendments.get(s.get("settlement_id"), []))

        postmortem_game = self.read_postmortem_games()
        pending = []
        for w in sorted(wagers, key=lambda x: (x.get("executed_at") or "", x["imported_wager_id"])):
            ticker = (w.get("market_ticker") or "").strip().upper()
            sem = classifier.classify({"ticker": ticker})
            game_id = None
            if sem.away_team and sem.home_team and w.get("season") is not None and w.get("week") is not None:
                game_id = f"{int(w['season'])}_{int(w['week']):02d}_{sem.away_team}_{sem.home_team}"
            elif postmortem_game.get(w.get("source_bet_key")):
                game_id = postmortem_game[w["source_bet_key"]]
            eid = self.ensure_offboard_event(game_id, game_date=w.get("game_date")) if game_id else None
            settled = by_key.get(w.get("source_bet_key"))
            event_final = eid is not None and self.events[eid]["status"] == "FINAL"
            market = self.market_stub(ticker, family=sem.family, yes_description=sem.yes_meaning or f"YES on {ticker}",
                                      event_id=eid, settled=event_final or settled is not None)
            wager = build.wager(
                sport=SPORT, kalshi_ticker=ticker, selection=(w.get("side") or "").upper(), contracts=w["contracts"],
                stake=w["stake"], average_price=w.get("actual_price"), placed_at=w["executed_at"], source=WAGER_SOURCE,
                destination_repo=REPO, source_bet_key=w.get("source_bet_key"), native_id=w["imported_wager_id"],
                event_id=eid, side=w.get("execution_action"), fees=w.get("fees_paid"),
                settlement_status="PENDING",
                source_ids={"imported_wager_id": w["imported_wager_id"], "import_batch_id": w.get("import_batch_id"),
                            "game_id": game_id, "game_date": w.get("game_date")},
                extensions={"fee_state": w.get("fee_state"), "fees_are_estimated": w.get("fees_are_estimated"),
                            "entry_method": w.get("entry_method"), "season": w.get("season"), "week": w.get("week"),
                            "game_date": w.get("game_date"), "venue": w.get("venue")},
            )
            pending.append((wager, settled, market))

        model_prices = self.model_prices
        recs = self.recommendations
        market_list = list(self.markets.values())
        for wager, settled, market in pending:
            wager = linkage.apply_links(wager, model_prices, recs, market_list)
            if settled is not None:
                stl = self.build_settlement(wager, market, settled)
                self.settlements.append(stl)
                wager["settlement_id"] = stl["settlement_id"]
                wager["settlement_status"] = "SETTLED"
                wager["payout"] = stl["gross_payout"]
                wager["profit_loss"] = stl["net_pnl"]
            self.wagers.append(wager)

    def build_settlement(self, wager: dict, market: dict, s: dict) -> dict:
        raw = s.get("result")
        result = SETTLEMENT_RESULT.get(str(raw).upper(), "UNKNOWN") if raw else "UNKNOWN"
        refusals = list(s.get("refusals") or [])
        if result == "UNKNOWN" and not refusals:
            refusals.append(f"settlement result {raw!r} is not one this export maps")
        winning = None
        if result == "WON":
            winning = wager["selection"]
        elif result == "LOST":
            winning = "NO" if wager["selection"] == "YES" else "YES"
        confirmed = (s.get("settlement_status") or "").upper() == "SETTLED"
        ext = {"economics_version": s.get("economics_version"),
               "recorded_economics_version": s.get("recorded_economics_version"),
               "amendment_status": s.get("amendment_status"), "amendment_id": s.get("amendment_id"),
               "settlement_status": s.get("settlement_status"), "venue": s.get("venue")}
        if s.get("amendment_status") == "AMENDED":
            ext["recorded_net_profit_loss"] = s.get("recorded_net_profit_loss")
        return build.settlement(
            wager_id=wager["wager_id"], market_id=market["market_id"], result=result, settled_at=s["settled_at"],
            source=f"{LEDGER_SOURCE}:wager_settlements",
            verification_status="EXCHANGE_CONFIRMED" if confirmed else "UNVERIFIED", winning_side=winning,
            gross_payout=s.get("gross_return"), fees=None, net_pnl=s.get("net_profit_loss"), refusals=refusals,
            source_ids={"settlement_id": s.get("settlement_id"), "source_bet_key": s.get("source_bet_key")},
            extensions=ext,
        )

    def postmortem_files(self) -> list[str]:
        if not self.market_data_root:
            return []
        base = os.path.join(self.market_data_root, "data", "handicap", "actual_wagers")
        if not os.path.isdir(base):
            return []
        out = []
        for season in sorted(os.listdir(base)):
            p = os.path.join(base, season, "season.actual_wagers.json")
            if os.path.exists(p):
                out.append(p)
        return out

    def read_clv(self) -> dict:
        """source_bet_key -> CLV dollars, only where the repo's own postmortem established it (CLV_VALID)."""
        out = {}
        for path in self.postmortem_files():
            for w in (_load(path).get("wagers") or []):
                if w.get("clv_state") == "CLV_VALID" and w.get("clv_dollars") is not None and w.get("source_bet_key"):
                    out[w["source_bet_key"]] = float(w["clv_dollars"])
        return out

    def read_postmortem_games(self) -> dict:
        out = {}
        for path in self.postmortem_files():
            for w in (_load(path).get("wagers") or []):
                if w.get("source_bet_key") and w.get("game"):
                    out[w["source_bet_key"]] = w["game"]
        return out

    # ---- schedule of the next decision horizon --------------------------------------------------------------
    def next_scheduled_run(self, manifest: dict):
        state = {}
        if self.horizon_state_path and os.path.exists(self.horizon_state_path):
            try:
                state = _load(self.horizon_state_path)
            except (OSError, ValueError):
                state = {}
        games = [{"game_id": k.get("game_id"), "kickoff_utc": k.get("kickoff_utc")} for k in manifest.get("kickoffs") or []]
        if not games or not manifest.get("slate_id"):
            return None
        try:
            due = horizons_mod.due_horizons(manifest["slate_id"], games, self.now, state)
        except Exception:  # noqa: BLE001 -- a schedule hint, never a reason to fail the export
            return None
        if due.get("due"):
            return self.now
        nxt = due.get("next_pending")
        return _ts(nxt["trigger_utc"]) if nxt else None

    # ---- assemble -----------------------------------------------------------------------------------------
    def run(self) -> dict:
        report = load_report(self.reports_dir)
        manifest, analysis, shards = report["manifest"], report["analysis"], report["shards"]
        v = report_vintages(manifest)
        sources = manifest.get("sources") or {}
        model_version = manifest.get("model_version") or ((analysis.get("models") or {}).get("incumbent") or {}).get("model_version")
        commit_sha = self.commit_sha_override or sources.get("main_sha")
        workflow_run_id = self.workflow_run_id_override or sources.get("workflow_run_id")

        run_doc = build.run(
            sport=SPORT, repo=REPO, completed_at=v["built_at"],
            scope=f"{manifest.get('season')} {manifest.get('season_type') or 'REG'} week {manifest.get('week')} slate {manifest.get('slate_id')}",
            status="SUCCESS", native_run_id=manifest.get("handicap_run_id"), commit_sha=commit_sha,
            workflow_run_id=workflow_run_id, model_version=model_version,
            events_requested=len(manifest.get("kickoffs") or []),
            data_sources=["handicap-reports:latest", LEDGER_SOURCE] + (["market-data"] if self.market_data_root else []),
            input_freshness={"kalshi": v["kalshi"], "shadow_pricing": v["model"], "context": v["context"],
                             "simulation": v["simulation"]},
            source_ids={"slate_id": manifest.get("slate_id"), "packet_sha": manifest.get("packet_sha"),
                        "market_data_sha": sources.get("market_data_sha")},
        )
        run_id = run_doc["run_id"]

        kickoffs = {k.get("game_id"): k for k in manifest.get("kickoffs") or []}
        for shard in shards:
            event = self.add_board_event(shard, kickoffs.get(shard["game_id"], {}), v, manifest)
            meta = self.event_meta[event["event_id"]]
            for row in sorted(shard.get("rows") or [], key=lambda r: r.get("ticker") or ""):
                self.add_row(row, event, meta, v, run_id, model_version)
            self.add_thesis(event, shard, run_id, v)
        self.add_recommendations(run_id)
        self.add_wagers(run_id)

        events = sorted(self.events.values(), key=lambda e: (e["start_time_utc"], e["event_id"]))
        markets = [self.markets[t] for t in sorted(self.markets)]
        run_doc["events_processed"] = len([e for e in events if e["extensions"].get("on_board")])
        run_doc["markets_discovered"] = len([m for m in markets if m["source"] == REPORT_SOURCE])
        run_doc["markets_priced"] = len(self.model_prices)
        run_doc["recommendations_created"] = len(self.recommendations)
        run_doc["warnings"] = list(self.warnings)

        health_doc = health.build_health(
            sport=SPORT, run_id=run_id, bet_authority=BET_AUTHORITY, last_market_capture=v["kalshi"],
            last_model_generated=v["model"], last_successful_run=self.now, payload_run_id=run_id,
            payload_available=True, export_failed=False, commit_sha=commit_sha,
            next_scheduled_run=self.next_scheduled_run(manifest),
            router_as_of=_latest([w["placed_at"] for w in self.wagers]),
            settlement_as_of=_latest([s["settled_at"] for s in self.settlements]),
            model_required=True, thresholds=THRESHOLDS, warnings=self.warnings, errors=[], now=self.now,
            generated_at=self.now,
        )
        board_doc = board.build_board(sport=SPORT, run_id=run_id, generated_at=self.now, events=events, markets=markets,
                                      model_prices=self.model_prices, recommendations=self.recommendations,
                                      wagers=self.wagers, health=health_doc, thresholds=THRESHOLDS, now=self.now)
        perf_doc = performance.build_performance(
            sport=SPORT, run_id=run_id, generated_at=self.now, wagers=self.wagers, settlements=self.settlements,
            markets=markets, recommendations=self.recommendations, bankroll_history=[], bankroll_basis=None,
            clv_values={w["wager_id"]: self.clv[w["source_bet_key"]] for w in self.wagers
                        if w.get("source_bet_key") in self.clv},
            notes=["Owner wagers imported from the Kalshi router (handicap-data imported_wagers); accounting only, "
                   "recommended by nothing in this repository.",
                   "Settlement economics follow the newest admissible amendment (router-settlement-economics.v2 "
                   "where filed); CLV only where the actual-wager postmortem established it."],
        )
        kalshi_status = freshness.status_for(v["kalshi"], now=self.now, thresholds=THRESHOLDS["market_data"])
        documents = {
            "events": build.collection("events", SPORT, run_id, self.now, events),
            "markets": build.collection("markets", SPORT, run_id, self.now, markets),
            "model_prices": build.collection("model_prices", SPORT, run_id, self.now, self.model_prices),
            "recommendations": build.collection("recommendations", SPORT, run_id, self.now, self.recommendations),
            "theses": build.collection("theses", SPORT, run_id, self.now, self.theses),
            "wagers": build.collection("wagers", SPORT, run_id, self.now, self.wagers),
            "settlements": build.collection("settlements", SPORT, run_id, self.now, self.settlements),
            "runs": build.collection("runs", SPORT, run_id, self.now, [run_doc]),
            "board": board_doc,
            "performance": perf_doc,
        }
        for ev in events:
            meta = self.event_meta[ev["event_id"]]
            shard = meta.get("shard") or {}
            context = {"game_state": shard.get("game_state"), "coverage": (shard.get("coverage") or {}).get("buckets"),
                       "capture": shard.get("capture"), "on_board": bool(shard)}
            documents[f"event_detail/{ev['event_id']}"] = board.build_event_detail(
                sport=SPORT, run_id=run_id, generated_at=self.now, event=ev, markets=markets,
                model_prices=self.model_prices, recommendations=self.recommendations, theses=self.theses,
                wagers=self.wagers, settlements=self.settlements, context=context, price_history=[],
                data_freshness=kalshi_status)
        return {
            "run_id": run_id, "documents": documents, "health": health_doc, "commit_sha": commit_sha,
            "model_version": model_version,
            "freshness": {
                "kalshi": {"as_of": _iso(v["kalshi"]), "status": kalshi_status},
                "model": {"as_of": _iso(v["model"]),
                          "status": freshness.status_for(v["model"], now=self.now, thresholds=THRESHOLDS["model"])},
                "context": {"as_of": _iso(v["context"]),
                            "status": freshness.status_for(v["context"], now=self.now, thresholds=THRESHOLDS["model"])},
            },
            "counts": {"events": len(events), "markets": len(markets), "model_prices": len(self.model_prices),
                       "recommendations": len(self.recommendations), "wagers": len(self.wagers),
                       "settlements": len(self.settlements)},
        }


# ----------------------------------------------------------------------------------------------- failure path

def write_failure_health(out: Path, exc: BaseException, now, commit_sha, reports_dir) -> dict:
    previous = None
    try:
        previous = publish.read_manifest(out)
    except (OSError, ValueError):
        previous = None
    last_capture = last_model = None
    try:
        v = report_vintages(_load(os.path.join(reports_dir, "manifest.json")))
        last_capture, last_model = v["kalshi"], v["model"]
    except Exception:  # noqa: BLE001 -- the report may be the thing that is broken
        pass
    run_id = (previous or {}).get("run_id") or ids.run_id(SPORT, REPO, None, generated_at=timeutil.to_iso(now))
    doc = health.build_health(
        sport=SPORT, run_id=run_id, bet_authority=BET_AUTHORITY, last_market_capture=last_capture,
        last_model_generated=last_model, last_successful_run=(previous or {}).get("generated_at"),
        payload_run_id=(previous or {}).get("run_id"), payload_available=previous is not None, export_failed=True,
        commit_sha=commit_sha or (previous or {}).get("commit_sha"), model_required=True, thresholds=THRESHOLDS,
        errors=[f"{type(exc).__name__}: {exc}"], now=now, generated_at=now,
    )
    publish.write_health_only(out, doc)
    return doc


# ----------------------------------------------------------------------------------------------- CLI

def export(args) -> int:
    now = _ts(args.now) if args.now else timeutil.now_utc().replace(microsecond=0)
    out = Path(args.out)
    try:
        ex = Exporter(reports_dir=args.reports_dir, handicap_root=args.handicap_root,
                      market_data_root=args.market_data_root, horizon_state=args.horizon_state, now=now,
                      commit_sha=args.commit_sha, workflow_run_id=args.workflow_run_id)
        result = ex.run()
        publish.publish(root=out, sport=SPORT, run_id=result["run_id"], generated_at=now,
                        documents=result["documents"], source_repo=REPO, source_branch=args.source_branch,
                        commit_sha=result["commit_sha"], model_version=result["model_version"], status="SUCCESS",
                        freshness=result["freshness"], warnings=ex.warnings, health=result["health"])
    except Exception as exc:  # noqa: BLE001 -- every failure becomes a red health file, never a half payload
        traceback.print_exc()
        doc = write_failure_health(out, exc, now, args.commit_sha, args.reports_dir)
        print(f"APP EXPORT FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        print(f"health.json written ({doc['overall_status']}); payload left as it was", file=sys.stderr)
        return 1
    counts = result["counts"]
    print(f"app export published to {out}: run {result['run_id']} health {result['health']['overall_status']} "
          + " ".join(f"{k}={v}" for k, v in counts.items()))
    if ex.warnings:
        print(f"{len(ex.warnings)} warning(s); first: {ex.warnings[0]}")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write(f"\n### Edge Finder app export\n\n`app/latest` run `{result['run_id']}` -- health "
                     f"**{result['health']['overall_status']}**; " + ", ".join(f"{k} {v}" for k, v in counts.items())
                     + "\n\n")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="export the Edge Finder app payload from a RUN NFL report")
    ap.add_argument("--reports-dir", "--data-root", dest="reports_dir",
                    default=os.path.join(REPO_ROOT, "data", "handicap_report"),
                    help="a verified RUN NFL report directory (the staged latest/: manifest.json + analysis/)")
    ap.add_argument("--handicap-root", default=None, help="a read-only checkout of the handicap-data branch")
    ap.add_argument("--market-data-root", default=None,
                    help="optional market-data checkout (schedule cache for past weeks, actual-wager CLV)")
    ap.add_argument("--horizon-state", default=None, help="state/horizons.json, for next_scheduled_run")
    ap.add_argument("--out", required=True, help="the app root to publish into (app/latest)")
    ap.add_argument("--now", default=None, help="aware ISO timestamp; fixes generated_at for deterministic output")
    ap.add_argument("--commit-sha", default=None)
    ap.add_argument("--workflow-run-id", default=None)
    ap.add_argument("--source-branch", default=SOURCE_BRANCH)
    args = ap.parse_args(argv)
    return export(args)


if __name__ == "__main__":
    sys.exit(main())
