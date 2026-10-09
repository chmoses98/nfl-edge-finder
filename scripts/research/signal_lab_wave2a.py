#!/usr/bin/env python3
"""Football Signal Discovery Lab, Wave 2A (NFL): retrospective replay of the frozen Wave-2 streams. RESEARCH ONLY.

docs/research/FOOTBALL_SIGNAL_DISCOVERY_WAVE2A_PROTOCOL.md.

    python scripts/research/signal_lab_wave2a.py replay  --market-data MD --scratch DIR   # 2026 weeks 1-5
    python scripts/research/signal_lab_wave2a.py report  --scratch DIR                   # -> research/signal_discovery_wave2a
    python scripts/research/signal_lab_wave2a.py history --market-data MD                # 2025 / Wave-1 characterisation

`replay` runs the Wave-2 job's own stage functions (scripts/research/signal_lab_wave2.py) unchanged, game by game:
observe at kickoff - 300 min, enter at kickoff + 5 min, settle at kickoff + 8 days. Records go to DIR (scratch),
never to market-data. Kalshi's API is unreachable from the replay environment, so the job's live settlement fetch
reads the exchange's own settled-market records from the market-data discovery archive instead (labelled).
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from nfl_edge.signal_discovery import wave2 as W  # noqa: E402
from nfl_edge.signal_discovery import wave2a as A  # noqa: E402

OUT = ROOT / "research" / "signal_discovery_wave2a"
DISCOVERY_RUN = "20261008T163830Z"
STREAM_SERIES_PREFIX = "KXNFL"


def load_job():
    spec = importlib.util.spec_from_file_location("signal_lab_wave2", ROOT / "scripts" / "research" / "signal_lab_wave2.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def code_sha() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:  # noqa: BLE001
        return None


def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=_default)


def _default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return None if np.isnan(o) else float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return str(o)


def write_gz_jsonl(path: Path, rows: list[dict[str, Any]]) -> str:
    A.assert_not_prospective_publish(str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(canonical(r) + "\n" for r in rows).encode()
    with open(path, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as fh:
        fh.write(payload)
    return hashlib.sha256(payload).hexdigest()


def write_json(path: Path, doc: Any) -> None:
    A.assert_not_prospective_publish(str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=1, sort_keys=True, default=_default) + "\n")


# --------------------------------------------------------------------------- exchange results (offline)


class ArchiveSettlements:
    """The exchange's own settled-market records (`result`, `settlement_value_dollars`, status) from a market-data
    discovery run: the same objects `GET /markets?status=settled` returns, stored by the daily discovery job."""

    def __init__(self, market_data: str, run: str = DISCOVERY_RUN):
        self.run = run
        self.by_ticker: dict[str, dict] = {}
        base = Path(market_data) / "data" / "kalshi" / "discovery" / run / "markets"
        for p in sorted(base.glob(f"{STREAM_SERIES_PREFIX}*.json")):
            doc = json.loads(p.read_text())
            for m in (doc.get("settled") or {}).get("markets") or []:
                if m.get("ticker"):
                    self.by_ticker[m["ticker"]] = m

    def fetch_game_settlements(self, client, event_tickers, tickers=None, *, verbose=None):
        from nfl_edge.settlement import kalshi_settlement as KS

        found = {t: self.by_ticker[t] for t in (tickers or ()) if t in self.by_ticker}
        for t, m in self.by_ticker.items():
            if t.rsplit("-", 1)[0] in set(event_tickers or ()):
                found.setdefault(t, m)
        return KS.FetchOutcome(markets=list(found.values()), meta=[{"source": A.SETTLEMENT_SOURCE_ARCHIVE, "run": self.run}],
                               complete=True, errors=0)


class _NoClient:
    def __init__(self, *a, **k):
        pass


# --------------------------------------------------------------------------- replay


def _memo_metric_table():
    from nfl_edge.signal_discovery import game_features as G

    original = G.metric_table
    cache: dict = {}

    def memo(seasons):
        key = tuple(seasons)
        if key not in cache:
            cache[key] = original(seasons)
        return cache[key]

    G.metric_table = memo


def baseline_ladders(J, md: str, g, kickoff) -> dict[str, Any]:
    """DESCRIPTIVE ONLY: every stream-stat player ladder of the game at LAST_VALID_PREKICK_QUOTE_24H, with each valid
    rung's captured quotes -- the same close-2.1.0 selection and identity rule as the frozen entry stage -- for the
    ALWAYS_NO / ALWAYS_YES baselines. Never an input to a frozen row."""
    from nfl_edge.evaluation import close as CL
    from nfl_edge.evaluation import openset as OS
    from nfl_edge.signal_discovery.markets import TEAM_FIX, Resolver, _jersey_from_ticker

    capture_root = os.path.join(md, "data", "kalshi", "capture")
    runs = _RUNS.setdefault(capture_root, CL.CaptureRuns(capture_root))
    led = _LED.setdefault(capture_root, OS.OpenSetLedger(capture_root))
    res = _RES.setdefault(W.SEASON, Resolver(W.SEASON))
    meta = J.capture_meta(capture_root, g.game_id, kickoff)
    ci = CL.CloseIndex(capture_root, g.game_id, J.iso(kickoff), runs=runs, days_back=7, openset=led if led.runs else None)
    ladders: dict[str, list[dict]] = defaultdict(list)
    for t, m in meta.items():
        if m.get("family") != "PLAYER_STAT" or m.get("period") not in ("FULL", None) or m.get("operator") not in (">=", None):
            continue
        if m.get("stat") not in W.STREAM_KALSHI_STATS:
            continue
        team = TEAM_FIX.get(m.get("team"), m.get("team"))
        gsis, how = res.resolve(m.get("player_name"), team, _jersey_from_ticker(t))
        if how not in W.ACCEPTED_IDENTITY:
            continue
        c = ci.select(t, series_ticker=m.get("series_ticker"))
        if not W.prop_checkpoint_ok(c, kickoff.timestamp()):
            continue
        ladders[f"{gsis}|{m['stat']}"].append(
            {"ticker": t, "threshold": m.get("threshold"), "series": m.get("series_ticker"), "team": team,
             "yes_bid": c.get("yes_bid"), "yes_ask": c.get("yes_ask"), "no_bid": c.get("no_bid"), "no_ask": c.get("no_ask"),
             "confirmed_at": c.get("confirmed_at")}
        )
    return {"game_id": g.game_id, "kickoff_utc": J.iso(kickoff), "ladders": dict(ladders)}


def completed(J, games: pd.DataFrame) -> pd.DataFrame:
    """Games that have been played (a final score exists). Week-5 games after 2026-10-08 had not been played when the
    replay ran: they belong to neither the replay nor the prospective population. Completion only -- no score value
    is read for membership."""
    s = pd.read_csv(J.GAMES_CSV)
    done = set(s.loc[s["home_score"].notna(), "game_id"])
    return games[games["game_id"].isin(done)].reset_index(drop=True)


_RUNS: dict = {}
_LED: dict = {}
_RES: dict = {}


def cmd_replay(a) -> int:
    J = load_job()
    frozen = W.load_frozen(ROOT)
    md = str(Path(a.market_data).resolve())
    scratch = Path(a.scratch).resolve()
    out = scratch / "records"
    A.assert_not_prospective_publish(str(out))
    if str(out).startswith(md):
        raise A.ReplayIntegrityError("replay records may not be written inside the market-data checkout")
    weeks = [int(w) for w in a.weeks.split(",")]
    games = completed(J, J.population_games(weeks=weeks))
    if a.only:
        games = games[games["game_id"].isin(a.only.split(","))].reset_index(drop=True)
    _memo_metric_table()
    have: set[str] = set()
    stages = set(a.stages.split(","))
    log: dict[str, Any] = {"weeks": weeks, "games": len(games), "observe": [], "enter": [], "settle": []}
    if "observe" in stages:
        for k, part in games.groupby("kickoff"):
            now = (k - pd.Timedelta(minutes=A.OBSERVE_MINUTES_BEFORE)).to_pydatetime()
            ids = part["game_id"].tolist()
            res = J.stage_observe(now, games, ids, md, out, have, frozen)
            log["observe"].append({"kickoff": J.iso(k.to_pydatetime()), "now": J.iso(now), "ids": ids, **res})
            print("observe", J.iso(now), ids, res, flush=True)
    if "enter" in stages:
        bdir = scratch / "baselines"
        bdir.mkdir(parents=True, exist_ok=True)
        for g in games.itertuples():
            kickoff = g.kickoff.to_pydatetime()
            now = kickoff + timedelta(minutes=A.ENTER_MINUTES_AFTER)
            res = J.stage_enter(now, games, [g.game_id], md, out, have, frozen)
            (bdir / f"{g.game_id}.json").write_text(json.dumps(baseline_ladders(J, md, g, kickoff), default=_default))
            log["enter"].append({"game_id": g.game_id, **res})
            print("enter", g.game_id, res, flush=True)
    if "settle" in stages:
        from nfl_edge.kalshi import client as KC
        from nfl_edge.settlement import kalshi_settlement as KS

        arch = ArchiveSettlements(md)
        KS.fetch_game_settlements = arch.fetch_game_settlements
        KC.KalshiClient = _NoClient
        for g in games.itertuples():
            now = g.kickoff.to_pydatetime() + timedelta(days=A.SETTLE_DAYS_AFTER)
            res = J.stage_settle(now, games, [g.game_id], md, out, have, frozen, fetch_exchange=True)
            log["settle"].append({"game_id": g.game_id, **res})
            print("settle", g.game_id, res, flush=True)
        log["exchange_archive"] = {"run": arch.run, "settled_markets": len(arch.by_ticker)}
    log["code_sha"] = code_sha()
    log["market_data_sha"] = subprocess.run(["git", "-C", md, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    (scratch / f"replay_log_{'_'.join(sorted(stages))}.json").write_text(json.dumps(log, indent=1, default=_default))
    return 0


# --------------------------------------------------------------------------- report


def _records(scratch: Path) -> dict[str, dict[str, dict]]:
    out: dict[str, dict[str, dict]] = {k: {} for k in W.RECORD_DIRS}
    for kind, sub in W.RECORD_DIRS.items():
        for p in sorted((scratch / "records" / W.RECORD_PREFIX / sub / str(W.SEASON)).glob("*.json")):
            d = json.loads(p.read_text())
            out[kind][d["game_id"]] = d
    return out


def _fee_fn_for(series, as_of):
    from nfl_edge.execution.fees import load_fee_schedule

    fees = _FEES.setdefault("f", load_fee_schedule(str(ROOT)))

    def fee_fn(price):
        q = fees.taker_fee(price, 1.0, series, as_of=as_of)
        return (q.amount, q.state) if q.state == "KNOWN" and q.amount is not None else (None, q.state)

    return fee_fn


_FEES: dict = {}


def _player_stats() -> pd.DataFrame:
    from nfl_edge.sim import data as D

    pg = pd.DataFrame(D.load("player_games", [W.SEASON]).to_dicts())
    return pg


def prop001_rows(recs, games) -> list[dict[str, Any]]:
    out = []
    week = dict(zip(games["game_id"], games["week"], strict=True))
    for gid, d in recs[W.SETTLEMENT].items():
        for r in d["rows"]:
            if r["signal_id"] != W.PROP_001 or r["status"] != W.SETTLED:
                continue
            e = r.get("economics") or {}
            if not e.get("available"):
                continue
            c = r.get("contract") or {}
            out.append({"game_id": gid, "week": int(week[gid]), "player_id": r["player_id"], "team": r.get("team"),
                        "threshold": c.get("threshold"), "price": e["entry_price"], "fee": e["fee"], "outlay": e["outlay"],
                        "pnl": e["fee_adjusted_pnl"], "win": e["settlement_value"] > 0.5, "actual": r.get("actual"),
                        "settlement_source": r.get("settlement_source"), "ticker": c.get("ticker")})
    return out


def baselines_prop001(scratch: Path, recs, games, pg: pd.DataFrame) -> dict[str, Any]:
    """Descriptive comparators on the same settled games (protocol section 3)."""
    week = dict(zip(games["game_id"], games["week"], strict=True))
    played = {(r["game_id"], r["player_id"]): r for r in pg.to_dict("records") if (r.get("offense_snaps") or 0) >= 1}
    eligible = {(gid, r["player_id"]) for gid, d in recs[W.ENTRY].items() for r in d["rows"]
                if r["signal_id"] == W.PROP_001 and r["status"] == W.ELIGIBLE}
    yes_nat, no_nat_wrte, no_nat_all, rb_family_rungs = [], [], [], []
    pos = {r["player_id"]: r.get("position") for r in pg.to_dict("records")}
    for p in sorted((scratch / "baselines").glob("*.json")):
        b = json.loads(p.read_text())
        gid = b["game_id"]
        for key, rungs in b["ladders"].items():
            pid, stat = key.split("|")
            pl = played.get((gid, pid))
            if pl is None:
                continue  # comparator rows settle by stat only for players who played
            col = {"receptions": "receptions", "receiving_yards": "rec_yards", "rushing_yards": "rush_yards",
                   "passing_yards": "pass_yards", "carries": "carries", "attempts": "attempts", "completions": "completions"}[stat]
            actual = float(pl.get(col) or 0.0)
            fee_fn = _fee_fn_for(rungs[0]["series"], rungs[0].get("confirmed_at"))
            lad = W.ladder(rungs)
            nat = lad["natural"]
            base = {"game_id": gid, "week": int(week[gid]), "player_id": pid, "team": rungs[0].get("team"), "stat": stat,
                    "position": pos.get(pid)}
            if nat is not None and lad["market_median"] is not None:
                for side, bucket in (("no", None), ("yes", None)):
                    c = W.contract(nat, side, fee_fn)
                    if c["status"] != W.ELIGIBLE:
                        continue
                    win = W.contract_pays_by_stat(c, actual)
                    row = {**base, "price": c["ask"], "fee": c["fee"], "outlay": c["ask"] + c["fee"], "win": win,
                           "pnl": (1.0 if win else 0.0) - c["ask"] - c["fee"], "threshold": c["threshold"]}
                    if side == "no":
                        no_nat_all.append(row)
                        if stat == "receptions" and pos.get(pid) in ("WR", "TE"):
                            no_nat_wrte.append(row)
                    elif (gid, pid) in eligible and stat == "receptions":
                        yes_nat.append(row)
            if (gid, pid) in eligible and stat == "receptions":
                for x in A.no_every_valid_rung(rungs, actual, fee_fn):
                    rb_family_rungs.append({**base, **x})
    return {
        "ALWAYS_NO_EVERY_VALID_RUNG_same_player_games": A.economics_summary(rb_family_rungs),
        "ALWAYS_YES_NATURAL_RUNG_same_player_games": A.economics_summary(yes_nat),
        "ALWAYS_NO_NATURAL_RUNG_WR_TE_receptions": A.economics_summary(no_nat_wrte),
        "ALWAYS_NO_NATURAL_RUNG_all_stream_stats": A.economics_summary(no_nat_all),
        "ALWAYS_NO_NATURAL_RUNG_all_stream_stats_by_stat": {
            s: A.economics_summary([r for r in no_nat_all if r["stat"] == s]) for s in sorted({r["stat"] for r in no_nat_all})
        },
        "note": "DESCRIPTIVE comparators on played players (settled by nflverse stat); never a rule.",
    }


def structure_prop001(recs, scratch: Path) -> list[dict[str, Any]]:
    """Market structure of every frozen PROP-001 entry: both asks, spread, ask sum, threshold, model vs threshold."""
    out = []
    obs_model = {}
    for gid, d in recs[W.OBSERVATION].items():
        for r in d["rows"]:
            if r["signal_id"] == W.PROP_002 and r.get("stat") == "receptions" and r.get("position") == "RB":
                obs_model[(gid, r["player_id"])] = r.get("model_median")
    for gid, d in recs[W.ENTRY].items():
        for r in d["rows"]:
            if r["signal_id"] != W.PROP_001 or r["status"] != W.ELIGIBLE:
                continue
            n = r.get("natural") or {}
            ya, na, yb = n.get("yes_ask"), n.get("no_ask"), n.get("yes_bid")
            out.append({"game_id": gid, "player_id": r["player_id"], "threshold": n.get("threshold"), "yes_ask": ya, "no_ask": na,
                        "yes_bid": yb, "no_bid": n.get("no_bid"), "spread": None if None in (ya, yb) else round(ya - yb, 4),
                        "ask_sum": None if None in (ya, na) else round(ya + na, 4), "mid": n.get("mid"),
                        "market_median": r.get("market_median"), "b_season": None})
    return out


def cmd_report(a) -> int:
    J = load_job()
    scratch = Path(a.scratch).resolve()
    recs = _records(scratch)
    games = completed(J, J.population_games(weeks=list(A.REPLAY_WEEKS)))
    pg = _player_stats()
    week = dict(zip(games["game_id"], games["week"], strict=True))
    # ---- flatten every record row with labels
    flat = []
    for kind in (W.OBSERVATION, W.ENTRY, W.SETTLEMENT):
        for gid, d in sorted(recs[kind].items()):
            for r in d["rows"]:
                row = {k: v for k, v in r.items() if k not in ("ladder",)}
                row.update({"record": kind, "game_id": gid, "week": int(week[gid]), "kickoff_utc": d["kickoff_utc"],
                            "generated_at": d["generated_at"], "evidence_label": A.EVIDENCE_2026,
                            "independence": A.INDEPENDENCE.get(r["signal_id"]),
                            "replay_exclusion": A.exclusion(r["status"], r.get("reason"))})
                if kind == W.SETTLEMENT and r.get("settlement_source") == "EXCHANGE":
                    row["settlement_source"] = A.SETTLEMENT_SOURCE_ARCHIVE
                flat.append(row)
    for r in flat:
        if r["record"] == W.OBSERVATION and r["generated_at"] >= r["kickoff_utc"]:
            raise A.ReplayIntegrityError(f"{r['game_id']}: observation generated at/after kickoff")
    obs_meta = {gid: d.get("pregame_inputs") or {} for gid, d in recs[W.OBSERVATION].items()}
    # ---- PROP-001
    p1 = prop001_rows(recs, games)
    econ1 = A.economics_summary(p1)
    # ---- PROP-002
    p2 = []
    for gid, d in recs[W.SETTLEMENT].items():
        for r in d["rows"]:
            if r["signal_id"] == W.PROP_002 and r["status"] == W.SETTLED:
                p2.append({**r, "game_id": gid, "week": int(week[gid])})
    pair = A.paired_summary(p2)
    units = pair.get("units") or []
    # ---- GAME-001
    p3, all_centre = [], []
    for gid, d in recs[W.SETTLEMENT].items():
        for r in d["rows"]:
            if r["signal_id"] == W.GAME_001 and r["status"] == W.SETTLED:
                p3.append({**r, "game_id": gid, "week": int(week[gid])})
    sched = pd.read_csv(J.GAMES_CSV)
    sched = sched[(sched["season"] == W.SEASON)].set_index("game_id")
    for gid, d in recs[W.ENTRY].items():
        for r in d["rows"]:
            if r["signal_id"] != W.GAME_001 or r.get("market_implied_total") is None or r.get("prediction") is None:
                continue
            s = sched.loc[gid]
            if pd.isna(s["home_score"]):
                continue
            total = float(s["home_score"]) + float(s["away_score"])
            p = r["prediction"]
            side = "OVER" if p > 0 else "UNDER"
            sign = 1.0 if p > 0 else -1.0
            all_centre.append({"game_id": gid, "week": int(week[gid]), "prediction": p, "side": side,
                               "market_implied_total": r["market_implied_total"], "actual_total": total,
                               "signed_residual": sign * (total - r["market_implied_total"]),
                               "qualifies": abs(p) >= W.TOTAL_THRESHOLD})
    s3 = A.signed_summary([{**r, "side": r["side"]} for r in p3])
    econ3 = A.economics_summary([
        {"game_id": r["game_id"], "pnl": r["economics"]["fee_adjusted_pnl"], "outlay": r["economics"]["outlay"],
         "win": r["economics"]["settlement_value"] > 0.5, "price": r["economics"]["entry_price"], "fee": r["economics"]["fee"]}
        for r in p3 if (r.get("economics") or {}).get("available")])
    report = {
        "schema": "nfl_signal_lab_wave2a_report/1.0.0",
        "version": A.VERSION,
        "evidence_label": A.EVIDENCE_2026,
        "kind": "RETROSPECTIVE replay of the frozen Wave-2 rules on 2026 REG weeks 1-5. Not prospective; never pooled.",
        "code_sha": code_sha(),
        "pins": {"candidates_sha256": W.CANDIDATES_SHA256, "wf_total_sha256": W.WF_TOTAL_SHA256,
                 "prop_models_sha256": W.PROP_MODELS_SHA256, "classifier_sha256": W.CLASSIFIER_SHA256,
                 "wave2_protocol_sha256": hashlib.sha256((ROOT / "docs/research/FOOTBALL_SIGNAL_DISCOVERY_WAVE2_PROTOCOL.md").read_bytes()).hexdigest(),
                 "wave2a_protocol_sha256": hashlib.sha256((ROOT / "docs/research/FOOTBALL_SIGNAL_DISCOVERY_WAVE2A_PROTOCOL.md").read_bytes()).hexdigest()},
        "replay_logs": {p.name: json.loads(p.read_text()).get("market_data_sha") for p in sorted(scratch.glob("replay_log_*.json"))},
        "seed": W.SEED,
        "n_boot": W.N_BOOT,
        "games": {k: len(v) for k, v in recs.items()},
        "record_status_counts": dict(Counter(f"{r['signal_id']}|{r['record']}|{r['status']}|{r.get('reason')}" for r in flat)),
        "exclusions": dict(Counter(f"{r['signal_id']}|{r['record']}|{r['replay_exclusion']}" for r in flat if r["replay_exclusion"])),
        "pregame_inputs": {gid: {"cutoff": m.get("cutoff"), "injury_vintage": m.get("injury_vintage"),
                                 "depth_chart_vintage": m.get("depth_chart_vintage"), "latest_history_game": m.get("latest_history_game")}
                           for gid, m in sorted(obs_meta.items())},
        "streams": {
            W.PROP_001: {
                "independence": A.INDEPENDENCE[W.PROP_001],
                "frozen_rule": "RB_receptions family, natural rung (valid 0<bid<=ask<1, width<=0.10, min |mid-0.5|, tie lowest threshold), NO at captured NO ask, LAST_VALID_PREKICK_QUOTE_24H",
                "economics": econ1,
                "frozen_summarize": W.summarize(W.PROP_001, [{**r, "game_id": r["game_id"]} for d in recs[W.SETTLEMENT].values() for r in d["rows"]]),
                "concentration": A.concentration_roi(p1),
                "by_threshold": A.roi_by(p1, "threshold"),
                "by_price_bucket": A.roi_by([{**r, "bucket": f"{int(r['price'] * 10) / 10:.1f}"} for r in p1], "bucket"),
                "settlement_sources": dict(Counter(r["settlement_source"] for r in p1)),
                "clv_note": "the checkpoint IS the canonical close (close-2.1.0): CLV is 0 by construction and not informative",
                "baselines": baselines_prop001(scratch, recs, games, pg),
                "replay_verdict": A.classify_prop001(econ1),
                "rows": p1,
            },
            W.PROP_002: {
                "independence": A.INDEPENDENCE[W.PROP_002],
                **{k: v for k, v in pair.items() if k != "units"},
                "by_family": {f: {k: v for k, v in A.paired_summary([r for r in p2 if r["family"] == f]).items() if k != "units"}
                              for f in sorted({r["family"] for r in p2})},
                "by_position": {f: {k: v for k, v in A.paired_summary([r for r in p2 if r["position"] == f]).items() if k != "units"}
                                for f in sorted({r["position"] for r in p2})},
                "by_week": {str(w): {k: v for k, v in A.paired_summary([r for r in p2 if r["week"] == w]).items() if k != "units"}
                            for w in sorted({r["week"] for r in p2})},
                "without_top5_players": A.paired_without(units, "player_id", 5),
                "without_top_team": A.paired_without(units, "team", 1),
                "top_player_share": (max(Counter(u["player_id"] for u in units).values()) / len(units)) if units else None,
                "secondary_economics": _role_econ(recs),
                "replay_verdict": A.classify_prop002(pair) if units else "INSUFFICIENT_REPLAY_DATA",
                "rows": p2,
            },
            W.GAME_001: {
                "independence": A.INDEPENDENCE[W.GAME_001],
                "qualified": s3,
                "economics": econ3,
                "all_games_with_centre": A.signed_summary(all_centre),
                "all_games_rows": sorted(all_centre, key=lambda r: (r["week"], r["game_id"])),
                "replay_verdict": A.classify_game001(s3) if p3 else "INSUFFICIENT_REPLAY_DATA",
                "rows": p3,
            },
        },
        "prospective": {sid: {"status": W.PROSPECTIVE_TRACKING, "n": W.NO_SETTLED_SAMPLE} for sid in W.STREAMS},
        "structure_prop001": structure_prop001(recs, scratch),
    }
    write_gz_jsonl(OUT / "replay_rows_2026.jsonl.gz", flat)
    write_json(OUT / "replay_report_2026.json", report)
    for sid in W.STREAMS:
        print(sid, report["streams"][sid]["replay_verdict"])
    print(json.dumps({"p1": {k: econ1.get(k) for k in ("n", "roi", "roi_ci95_game_cluster", "win_rate")},
                      "p2": {k: pair.get(k) for k in ("n_player_games", "mean_d", "ci95_game_cluster", "model_mae", "market_mae")},
                      "p3": s3, "p3_econ": {k: econ3.get(k) for k in ("n", "roi")}}, default=_default, indent=1))
    return 0


def _role_econ(recs) -> dict[str, Any]:
    rows = []
    for gid, d in recs[W.SETTLEMENT].items():
        for r in d["rows"]:
            if r["signal_id"] != W.PROP_002 or r["status"] != W.SETTLED:
                continue
            c = r.get("contract") or {}
            if c.get("status") != W.ELIGIBLE:
                continue
            win = W.contract_pays_by_stat(c, float(r["actual"]))
            rows.append({"game_id": gid, "price": c["ask"], "fee": c["fee"], "outlay": c["ask"] + c["fee"], "win": win,
                         "pnl": (1.0 if win else 0.0) - c["ask"] - c["fee"], "side": c["contract_side"]})
    return {"rule": "the Wave-1 pre-registered side rule already in the frozen job (natural rung; model median vs threshold +-10%); "
                    "settled by the nflverse stat of a player who played; SECONDARY, never a new rule",
            **A.economics_summary(rows), "sides": dict(Counter(r["side"] for r in rows))}


# --------------------------------------------------------------------------- history (2025 / Wave-1 corpus)


def cmd_history(a) -> int:
    from nfl_edge.signal_discovery import evaluate_props as EP
    from nfl_edge.signal_discovery import markets as M

    md = Path(a.market_data)
    set1 = json.loads((ROOT / "research" / "signal_discovery_wave1" / "hypotheses_set1.json").read_text())
    fams = {f["id"]: f for f in set1["prop_families"]}
    files = sorted(str(p) for p in (md / "data" / "kalshi" / "backfill" / "horizons").glob("[0-9].jsonl"))
    out: dict[str, Any] = {"schema": "nfl_signal_lab_wave2a_history/1.0.0", "version": A.VERSION, "code_sha": code_sha(),
                           "evidence_label": A.EVIDENCE_HISTORY, "horizon_files": {Path(f).name: hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in files}}
    pf = pd.read_parquet(ROOT / "research" / "signal_discovery_wave1" / "player_features.parquet")
    pf = EP.add_baselines(pf, set1["prop_families"])
    fam = EP.family_rows(pf[pf["season"] == 2025], fams[W.RB_FAMILY])
    elig = set(zip(fam["game_id"], fam["player_id"], strict=True))
    actual = {(r.game_id, r.player_id): float(r.receptions) for r in pf[pf["season"] == 2025].itertuples() if pd.notna(r.receptions)}
    pos = {(r.game_id, r.player_id): r.position for r in pf[pf["season"] == 2025].itertuples()}
    res = {}
    for ckpt in ("T-90m", "T-0"):
        rungs = M.kalshi_2025(files, ckpt)
        rungs = rungs[rungs["season"] == 2025]
        rungs, idc = M.attach_identity(rungs)
        rungs = rungs[rungs["identity"].isin(W.ACCEPTED_IDENTITY)]
        by: dict[tuple, list] = defaultdict(list)
        for r in rungs[rungs["stat"] == "receptions"].to_dict("records"):
            by[(r["game_id"], r["gsis_id"])].append({**r, "no_bid": None})
        frozen_rows, every_rung, wrte, yes_rows = [], [], [], []
        status = Counter()
        for (gid, pid), rs in sorted(by.items()):
            lad = W.ladder(rs)
            nat = lad["natural"]
            if (gid, pid) not in actual:
                status["NOT_IN_PLAYER_ROWS"] += 1
                continue
            y = actual[(gid, pid)]
            wk = int(rs[0]["week"])
            fee_fn = _fee_fn_for("KXNFLREC", rs[0].get("kickoff_ts") and pd.Timestamp(rs[0]["kickoff_ts"], unit="s", tz="UTC").isoformat())
            base = {"game_id": gid, "player_id": pid, "team": rs[0].get("team"), "week": wk}
            if nat is None or lad["market_median"] is None:
                status["NO_VALID_RUNG_OR_MEDIAN"] += 1
                continue
            res_by_t = {float(r["threshold"]): r.get("result") for r in rs}
            for side, bucket in (("no", "no"), ("yes", "yes")):
                c = W.contract(nat, side, fee_fn)
                if c["status"] != W.ELIGIBLE:
                    status[f"{side}:{c['status']}:{c.get('reason')}"] += 1
                    continue
                exch = res_by_t.get(float(c["threshold"]))
                if exch in ("yes", "no"):
                    yes_pay = 1.0 if exch == "yes" else 0.0
                    value = W.contract_value_by_exchange(c, yes_pay)
                else:
                    value = 1.0 if W.contract_pays_by_stat(c, y) else 0.0
                row = {**base, "threshold": c["threshold"], "price": c["ask"], "fee": c["fee"], "outlay": c["ask"] + c["fee"],
                       "win": value > 0.5, "pnl": value - c["ask"] - c["fee"]}
                if side == "no" and (gid, pid) in elig:
                    frozen_rows.append(row)
                    for x in A.no_every_valid_rung(rs, y, fee_fn):
                        every_rung.append({**base, **x})
                elif side == "no" and pos.get((gid, pid)) in ("WR", "TE"):
                    wrte.append(row)
                elif side == "yes" and (gid, pid) in elig:
                    yes_rows.append(row)
            status["LADDER_PRICED"] += 1
        res[ckpt] = {
            "checkpoint": ckpt,
            "exact_rule_status": A.HISTORICAL_REPLAY_UNAVAILABLE,
            "why": "the 2025 archive holds YES bid/ask candles at fixed horizons only: no captured NO ask (NO ask = 1 - YES bid "
                   "here, the Wave-1 basis) and no LAST_VALID_PREKICK_QUOTE_24H; family membership uses the Wave-1 player rows "
                   "(players who appeared)",
            "identity": idc,
            "ladder_status": dict(status),
            "frozen_natural_rung_NO_rb_family": A.economics_summary(frozen_rows),
            "frozen_concentration": A.concentration_roi(frozen_rows),
            "by_threshold": A.roi_by(frozen_rows, "threshold"),
            "by_price_bucket": A.roi_by([{**r, "bucket": f"{int(r['price'] * 10) / 10:.1f}"} for r in frozen_rows], "bucket"),
            "ALWAYS_NO_EVERY_VALID_RUNG_same_player_games": A.economics_summary(every_rung),
            "ALWAYS_YES_NATURAL_RUNG_same_player_games": A.economics_summary(yes_rows),
            "ALWAYS_NO_NATURAL_RUNG_WR_TE_receptions": A.economics_summary(wrte),
        }
    out[W.PROP_001] = res
    # ROLE_CHANGE: every historical class used the final weekly injury file
    rc = pf[(pf["role_stability"] == "ROLE_CHANGE") & (pf["season"] <= 2025)]
    out[W.PROP_002] = {"role_change_rows_2016_2025": int(len(rc)), "by_season": rc.groupby("season").size().to_dict(),
                       "status": A.INJURY_VINTAGE_UNAVAILABLE,
                       "why": "no timestamped injury vintage exists before 2026-09-13; Wave-1 classes used the final weekly report (NEAR_PIT). "
                              "Under the Wave-2A safety rule none of these rows is a valid historical ROLE_CHANGE replay."}
    # WF-TOTAL: the Wave-1 folds as published (reproducibility)
    ge = json.loads((ROOT / "research" / "signal_discovery_wave1" / "game_evaluation_report.json").read_text())
    wf = ge["walk_forward"]["WF-TOTAL"]
    out[W.GAME_001] = {"evidence_label": A.EVIDENCE_HISTORY, "basis": "nflverse consensus close, untimestamped, assumed -110",
                       "aggregate_picks": wf["aggregate"]["picks_abs_pred_ge_threshold"],
                       "by_season": {f["test_season"]: {k: f["picks"].get(k) for k in ("n", "covers", "losses", "pushes", "cover_rate", "mean_resid", "roi_assumed_110")}
                                     for f in wf["folds"]}}
    write_json(OUT / "history_report.json", out)
    print(json.dumps({ck: {k: v for k, v in r.items() if k in ("ladder_status",)} | {"frozen": {k: r["frozen_natural_rung_NO_rb_family"].get(k) for k in ("n", "roi", "roi_ci95_game_cluster")},
                      "every_rung": {k: r["ALWAYS_NO_EVERY_VALID_RUNG_same_player_games"].get(k) for k in ("n", "roi")}} for ck, r in res.items()}, indent=1, default=_default))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("replay")
    r.add_argument("--market-data", required=True)
    r.add_argument("--scratch", required=True)
    r.add_argument("--weeks", default=",".join(str(w) for w in A.REPLAY_WEEKS))
    r.add_argument("--stages", default="observe,enter,settle")
    r.add_argument("--only", default=None)
    rp = sub.add_parser("report")
    rp.add_argument("--scratch", required=True)
    h = sub.add_parser("history")
    h.add_argument("--market-data", required=True)
    a = ap.parse_args(argv)
    return {"replay": cmd_replay, "report": cmd_report, "history": cmd_history}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
