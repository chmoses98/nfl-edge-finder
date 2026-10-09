#!/usr/bin/env python3
"""Wave 2B (NFL): RB receptions market-mechanism study. RESEARCH ONLY. EXPLANATORY ONLY.

docs/research/RB_RECEPTIONS_MECHANISM_PROTOCOL.md (pre-registered at a5f18324).

    python scripts/research/rb_receptions_mechanism.py extract-quotes --market-data MD --out DIR   # stream capture -> DIR
    python scripts/research/rb_receptions_mechanism.py build   --market-data MD --quotes DIR        # populations + features
    python scripts/research/rb_receptions_mechanism.py analyze                                     # -> artifact + tables

`MD` is a blobless, sparse `market-data` checkout at 4f04927982a1 (the Wave-2A pin) with the KXNFL discovery run
20261008T163830Z, the 2025 horizon archive and the 2026 injury vintages checked out. Nothing is written to market-data
or to the Wave-2 prospective store; nothing here is a rule.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import json
import os
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from nfl_edge.signal_discovery import rb_mechanism as R  # noqa: E402
from nfl_edge.signal_discovery import wave2 as W  # noqa: E402

OUT = ROOT / "research" / "rb_receptions_mechanism"
WAVE2A = ROOT / "research" / "signal_discovery_wave2a"
MD_COMMIT = "4f04927982a1b1b9debbd3e1ea317f191e82cc25"
DISCOVERY_RUN = "20261008T163830Z"
STAT_COL = {"receptions": "receptions", "receiving_yards": "receiving_yards", "rushing_yards": "rushing_yards",
            "passing_yards": "passing_yards", "carries": "carries", "attempts": "attempts", "completions": "completions"}
TIMING_2026 = (("T-24h", 24 * 60), ("T-6h", 360), ("T-3h", 180), ("T-90m", 90), ("T-60m", 60))
TIMING_2025 = ("T-48h", "T-24h", "T-12h", "T-6h", "T-3h", "T-90m", "T-30m", "T-0")


# --------------------------------------------------------------------------- io


def _default(o):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return None if np.isnan(o) else float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, float) and np.isnan(o):
        return None
    return str(o)


def canonical(o) -> str:
    return json.dumps(o, sort_keys=True, separators=(",", ":"), default=_default)


def write_gz(path: Path, rows: list[dict]) -> str:
    R.assert_not_prospective(str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(canonical(r) + "\n" for r in rows).encode()
    with open(path, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as fh:
        fh.write(payload)
    return hashlib.sha256(payload).hexdigest()


def read_gz(path: Path) -> list[dict]:
    with gzip.open(path, "rt") as fh:
        return [json.loads(line) for line in fh]


def write_json(path: Path, doc) -> None:
    R.assert_not_prospective(str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=1, sort_keys=True, default=_default) + "\n")


def sha_file(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def code_sha() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:  # noqa: BLE001
        return None


def parse(s) -> datetime:
    d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def load_job():
    spec = importlib.util.spec_from_file_location("signal_lab_wave2", ROOT / "scripts" / "research" / "signal_lab_wave2.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --------------------------------------------------------------------------- extract quotes (capture -> filtered history)


def cmd_extract(a) -> int:
    """Stream every capture day's quotes/manifests from a blobless market-data clone; keep full-game player-stat rows
    of the seven stream stats. Batch-fetches blobs and deletes the fetched packs so disk stays bounded."""
    md, out = a.market_data, Path(a.out)
    R.assert_not_prospective(str(out))
    out.mkdir(parents=True, exist_ok=True)
    stats = set(STAT_COL)
    keep = ["run_id", "observed_at", "ticker", "series_ticker", "stat", "team", "player_name", "threshold", "game_id",
            "kickoff_utc", "yes_bid_dollars", "yes_ask_dollars", "no_bid_dollars", "no_ask_dollars", "last_price_dollars",
            "volume_fp", "open_interest_fp", "yes_bid_size_fp", "yes_ask_size_fp", "status"]

    def git(*args, inp=None):
        return subprocess.run(["git", "-C", md, *args], input=inp, capture_output=True, check=True).stdout

    days = [ln.split("\t")[1].rsplit("/", 1)[1] for ln in git("ls-tree", MD_COMMIT, "data/kalshi/capture/").decode().splitlines()
            if ln.split()[1] == "tree"]
    packdir = os.path.join(md, ".git", "objects", "pack")
    for day in days:
        dest = out / f"quotes_{day}.jsonl.gz"
        if dest.exists():
            continue
        ents = [ln.split() for ln in git("ls-tree", f"{MD_COMMIT}:data/kalshi/capture/{day}").decode().splitlines()]
        want = [(e[2], e[3]) for e in ents if e[3].endswith((".quotes.jsonl", ".manifest.json"))]
        before = set(os.listdir(packdir))
        git("-c", "fetch.negotiationAlgorithm=noop", "fetch", "origin", "--no-tags", "--no-write-fetch-head",
            "--recurse-submodules=no", "--filter=blob:none", "--stdin", inp=("\n".join(o for o, _ in want) + "\n").encode())
        with gzip.open(str(dest) + ".part", "wt") as fq, gzip.open(out / f"manifest_{day}.jsonl.gz", "wt") as fm:
            for oid, name in sorted(want, key=lambda x: x[1]):
                data = subprocess.run(["git", "-C", md, "cat-file", "blob", oid], capture_output=True, check=True).stdout
                if name.endswith(".manifest.json"):
                    d = json.loads(data)
                    ser = {k: v for k, v in (d.get("series") or {}).items() if k.startswith("KXNFL") and not k.startswith("KXNFLGAME")}
                    fm.write(json.dumps({"run_id": d.get("run_id"), "started_at": d.get("started_at"), "series": ser}) + "\n")
                    continue
                for line in data.splitlines():
                    if b'"PLAYER_STAT"' not in line:
                        continue
                    r = json.loads(line)
                    if r.get("family") == "PLAYER_STAT" and r.get("stat") in stats and r.get("period") in ("FULL", None):
                        fq.write(json.dumps({k: r.get(k) for k in keep}, separators=(",", ":")) + "\n")
        os.replace(str(dest) + ".part", dest)
        for p in set(os.listdir(packdir)) - before:
            os.remove(os.path.join(packdir, p))
        print(day, flush=True)
    return 0


def quote_history(qdir: Path, tickers: set[str]) -> dict[str, list[dict]]:
    """ticker -> pre-kickoff rows sorted by observed_at (float prices). Post-kickoff rows are dropped here."""
    hist: dict[str, list[dict]] = defaultdict(list)
    for p in sorted(qdir.glob("quotes_*.jsonl.gz")):
        with gzip.open(p, "rt") as fh:
            for line in fh:
                if '"ticker":"' not in line:
                    continue
                t = line.split('"ticker":"', 1)[1].split('"', 1)[0]
                if t not in tickers:
                    continue
                r = json.loads(line)
                if not r.get("kickoff_utc") or parse(r["observed_at"]) >= parse(r["kickoff_utc"]):
                    continue
                hist[t].append({"observed_at": r["observed_at"], "run_id": r["run_id"], "kickoff_utc": r["kickoff_utc"],
                                "status": r.get("status"),
                                **{k: R._f(r.get(f"{k}_dollars")) for k in ("yes_bid", "yes_ask", "no_bid", "no_ask", "last_price")},
                                "volume": R._f(r.get("volume_fp")), "open_interest": R._f(r.get("open_interest_fp")),
                                "yes_bid_size": R._f(r.get("yes_bid_size_fp")), "yes_ask_size": R._f(r.get("yes_ask_size_fp"))})
    for t in hist:
        hist[t].sort(key=lambda r: r["observed_at"])
    return dict(hist)


def quote_at(rows: list[dict], instant: datetime) -> dict | None:
    last = None
    for r in rows:
        if parse(r["observed_at"]) <= instant:
            last = r
        else:
            break
    if last is None or last.get("status") not in ("active", "open", None, ""):
        return None
    return last


# --------------------------------------------------------------------------- shared loaders


def fee_fn_for(series, as_of):
    from nfl_edge.execution.fees import load_fee_schedule

    fees = _FEES.setdefault("f", load_fee_schedule(str(ROOT)))

    def fee_fn(price):
        q = fees.taker_fee(price, 1.0, series, as_of=as_of)
        return (q.amount, q.state) if q.state == "KNOWN" and q.amount is not None else (None, q.state)

    return fee_fn


_FEES: dict = {}


def fees_for(series: str, as_of, yes_ask, no_ask) -> tuple[float | None, float | None]:
    fn = fee_fn_for(series, as_of)
    out = []
    for p in (yes_ask, no_ask):
        out.append(fn(p)[0] if p is not None and W.executable(p) else None)
    return out[0], out[1]


def exchange_archive(md: str) -> dict[str, dict]:
    base = Path(md) / "data" / "kalshi" / "discovery" / DISCOVERY_RUN / "markets"
    out = {}
    for p in sorted(base.glob("KXNFL*.json")):
        doc = json.loads(p.read_text())
        for m in (doc.get("settled") or {}).get("markets") or []:
            if m.get("ticker"):
                out[m["ticker"]] = m
    return out


def nfl_stats(season: int) -> pd.DataFrame:
    p = ROOT / "data" / "raw" / "nflverse" / "stats_player" / f"stats_player_week_{season}.parquet"
    return pd.read_parquet(p)


def schedule() -> pd.DataFrame:
    s = pd.read_csv(ROOT / "data" / "raw" / "nflverse" / "schedules" / "games.csv")
    return s


def roster_positions(season: int) -> dict[str, str]:
    r = pd.read_parquet(ROOT / "data" / "raw" / "nflverse" / "rosters" / f"roster_{season}.parquet", columns=["gsis_id", "position"])
    r = r[r["gsis_id"].notna()].drop_duplicates("gsis_id")
    return dict(zip(r["gsis_id"], r["position"], strict=True))


def player_games(seasons) -> pd.DataFrame:
    from nfl_edge.sim import data as D

    pg = pd.DataFrame(D.load("player_games", list(seasons)).to_dicts())
    s = schedule()[["game_id", "gameday", "gametime", "weekday"]]
    return pg.merge(s, on="game_id", how="left")


# --------------------------------------------------------------------------- pregame history features (strictly earlier games)


class History:
    """Per-player and per-team game history from nflverse player_games (REG + POST), keyed by game date."""

    def __init__(self, pg: pd.DataFrame):
        pg = pg.copy()
        if "team_targets" not in pg.columns:  # silver player_games carries no team total: sum the team's targets per game
            pg["team_targets"] = pg.groupby(["game_id", "team"])["targets"].transform("sum")
        pg["date"] = pd.to_datetime(pg["gameday"])
        pg["played"] = (pg["offense_snaps"].fillna(0) >= 1) | (pg["targets"].fillna(0) > 0) | (pg["carries"].fillna(0) > 0)
        self.pg = pg.sort_values(["date", "game_id"])
        self.by_player = {k: v for k, v in self.pg[self.pg["played"]].groupby("player_id")}
        self.team_games = self.pg.groupby(["team", "game_id"])["date"].first().reset_index().sort_values("date")

    def player_prior(self, pid: str, date: pd.Timestamp, n: int = 16) -> pd.DataFrame:
        d = self.by_player.get(pid)
        if d is None:
            return pd.DataFrame()
        d = d[(d["date"] < date) & (d["season_type"].isin(["REG", "POST"]) if "season_type" in d else True)]
        return d.tail(n)

    def features(self, pid: str, team: str, date: pd.Timestamp, t: float | None) -> dict[str, Any]:
        h = self.player_prior(pid, date, 16)
        rec = h["receptions"].fillna(0).astype(float).tolist() if len(h) else []
        tsh = (h["targets"].fillna(0) / h["team_targets"].replace(0, np.nan)).tolist() if len(h) and "team_targets" in h else []
        out: dict[str, Any] = {"n_hist": len(rec)}
        if rec:
            out.update({"last1": rec[-1], "last2": float(np.mean(rec[-2:])), "last3": float(np.mean(rec[-3:])),
                        "long16": float(np.mean(rec)), "median16": float(np.median(rec)),
                        "mode16": float(Counter(rec).most_common(1)[0][0]) if rec else None,
                        "sd16": float(np.std(rec, ddof=1)) if len(rec) > 1 else None,
                        "last_targets": float(h["targets"].fillna(0).iloc[-1]),
                        "last_target_share": None if not tsh or pd.isna(tsh[-1]) else float(tsh[-1]),
                        "target_share_sd6": float(np.nanstd(tsh[-6:], ddof=1)) if len([x for x in tsh[-6:] if not pd.isna(x)]) >= 3 else None})
            cur = h[h["season"] == h["season"].iloc[-1]] if len(h) else h
            out["season_to_date"] = float(cur["receptions"].fillna(0).mean()) if len(cur) else None
            if t is not None and len(rec) >= 6:
                out["phist_ge_t"] = float(np.mean([x >= t for x in rec]))
        # backfield over the team's prior three games
        tg = self.team_games[(self.team_games["team"] == team) & (self.team_games["date"] < date)].tail(3)
        rbs = self.pg[self.pg["game_id"].isin(tg["game_id"]) & (self.pg["team"] == team) & (self.pg["position"] == "RB")]
        if len(rbs):
            opp = (rbs["carries"].fillna(0) + rbs["targets"].fillna(0)).groupby(rbs["player_id"]).sum()
            tot = opp.sum()
            if tot > 0:
                share = (opp / tot).sort_values(ascending=False)
                out["backfield_top_share"] = float(share.iloc[0])
                out["player_backfield_share"] = float(share.get(pid, 0.0))
                out["backfield_teammates"] = [p for p, s in share.items() if p != pid and s >= 0.10]
        return out


# --------------------------------------------------------------------------- 2026 build


def p1_frozen_rows() -> tuple[dict[tuple, dict], dict[tuple, dict], list[dict]]:
    """P1 from the committed Wave-2A replay records: ELIGIBLE entries with a SETTLED settlement, keyed (game, player)."""
    recs = read_gz(WAVE2A / "replay_records_2026.jsonl.gz")
    ent, stl, obs = {}, {}, {}
    for d in recs:
        for r in d["rows"]:
            if r["signal_id"] != W.PROP_001:
                continue
            k = (d["game_id"], r.get("player_id"))
            if d["record"] == W.ENTRY and r["status"] == W.ELIGIBLE:
                ent[k] = {**r, "kickoff_utc": d["kickoff_utc"], "week": d["week"]}
            elif d["record"] == W.SETTLEMENT:
                stl[k] = r
            elif d["record"] == W.OBSERVATION:
                obs[k] = r
    return ent, stl, [{"game_id": k[0], **v} for k, v in sorted(obs.items())]


def build_2026(md: str, qdir: Path) -> dict[str, Any]:
    ent, stl, obs_rows = p1_frozen_rows()
    p1_keys = {k for k, v in stl.items() if v.get("status") == W.SETTLED and k in ent}
    base = {b["game_id"]: b for b in read_gz(WAVE2A / "baseline_ladders_2026.jsonl.gz")}
    exch = exchange_archive(md)
    pos = roster_positions(2026)
    st = nfl_stats(2026)
    st = st[st["season_type"] == "REG"] if "season_type" in st else st
    sched = schedule()
    sched26 = sched[sched["season"] == 2026].set_index("game_id")
    actual = {}
    for r in st.to_dict("records"):
        actual[(int(r["week"]), r["player_id"])] = r
    rows: list[dict] = []
    ladders: list[dict] = []
    checks = Counter()
    for gid, b in sorted(base.items()):
        g = sched26.loc[gid]
        week = int(g["week"])
        for key, rungs in sorted(b["ladders"].items()):
            pid, stat = key.split("|")
            team = rungs[0].get("team")
            opp = g["away_team"] if team == g["home_team"] else g["home_team"]
            position = pos.get(pid)
            nr = R.natural_and_rungs(rungs)
            if nr["natural"] is None or nr["market_median"] is None:
                checks[f"{stat}:NO_NATURAL_OR_MEDIAN"] += 1
                continue
            in_p1 = stat == "receptions" and (gid, pid) in p1_keys
            if in_p1:
                position = "RB"  # the frozen family position
                e = ent[(gid, pid)]
                if e["natural"]["ticker"] != nr["natural"]["ticker"] or abs(e["natural"]["mid"] - nr["natural"]["mid"]) > 1e-9:
                    raise R.MechanismIntegrityError(f"{gid} {pid}: natural rung differs from the frozen entry")
                if abs((e.get("market_median") or 0) - nr["market_median"]) > 1e-9:
                    raise R.MechanismIntegrityError(f"{gid} {pid}: market median differs from the frozen entry")
                checks["P1_natural_matches_frozen_entry"] += 1
            if stat == "receptions" and position in ("WR", "TE"):
                nat_pop = "P4"
            elif stat == "receptions" and in_p1:
                nat_pop = "P1"
            elif stat == "receptions":
                nat_pop = "RB_REC_OUTSIDE_FAMILY" if position == "RB" else f"REC_{position}"
            else:
                nat_pop = "P5"
            stat_row = actual.get((week, pid))
            act = None if stat_row is None else R._f(stat_row.get(STAT_COL[stat]))
            if act is None and stat_row is None:
                act_note = "NO_NFLVERSE_ROW"
            else:
                act_note = None
                act = 0.0 if act is None else act
            ladder_rec = {"game_id": gid, "player_id": pid, "stat": stat, "position": position, "pop": nat_pop,
                          "rungs": [(r["threshold"], (r["yes_bid"] + r["yes_ask"]) / 2) for r in nr["valid_rungs"]],
                          "rungs_C": [], "natural_t": nr["natural"]["threshold"], "n_rungs": nr["n_rungs"], "n_valid": nr["n_valid"]}
            for vr in nr["valid_rungs"]:
                reps = R.representations(vr["yes_bid"], vr["yes_ask"], vr.get("no_bid"), vr.get("no_ask"))
                ladder_rec["rungs_C"].append((vr["threshold"], reps["C_norm_mid"]))
                pops = []
                if vr["is_natural"]:
                    pops.append(nat_pop)
                if in_p1:
                    pops.append("P3")
                if not pops:
                    continue
                fy, fn = fees_for(vr["series"], vr.get("confirmed_at"), vr["yes_ask"], vr.get("no_ask"))
                ex = exch.get(vr["ticker"])
                row = {"season": 2026, "week": week, "game_id": gid, "kickoff_utc": b["kickoff_utc"], "player_id": pid,
                       "player_name": None, "team": team, "opp": opp, "position": position, "stat": stat, "series": vr["series"],
                       "ticker": vr["ticker"], "threshold": vr["threshold"], "offset": vr["offset"], "is_natural": vr["is_natural"],
                       "dist_half": vr["dist_half"], "n_rungs": nr["n_rungs"], "n_valid": nr["n_valid"],
                       "market_median": nr["market_median"], "natural_t": nr["natural"]["threshold"],
                       "yes_bid": vr["yes_bid"], "yes_ask": vr["yes_ask"], "no_bid": vr.get("no_bid"), "no_ask": vr.get("no_ask"),
                       "confirmed_at": vr.get("confirmed_at"), "price_basis": R.CAPTURED_NO_ASK, "fee_yes": fy, "fee_no": fn,
                       **reps}
                if ex is not None:
                    row["player_name"] = (ex.get("yes_sub_title") or "").split(":")[0] or None
                    row["rules_primary"] = ex.get("rules_primary")
                    row["strike_type"] = ex.get("strike_type")
                    row["floor_strike"] = ex.get("floor_strike")
                s = R.settle(row, ex, act)
                s["actual_note"] = act_note
                row.update(s)
                row.update(R.economics_row(row))
                row.update(R.residual_fields(row))
                for p in pops:
                    rows.append({**row, "pop": p})
            ladder_rec["y_by_t"] = {}
            ladder_rec["actual"] = act
            ladders.append(ladder_rec)
    # P1 cross-check with the frozen settlement economics
    for r in rows:
        if r["pop"] != "P1":
            continue
        s = stl[(r["game_id"], r["player_id"])]
        e = s["economics"]
        if abs(e["entry_price"] - r["no_ask"]) > 1e-9 or abs(e["fee"] - r["fee_no"]) > 1e-9:
            raise R.MechanismIntegrityError(f"{r['game_id']} {r['player_id']}: P1 NO ask/fee differs from the frozen settlement")
        if r.get("y") is None or (e["settlement_value"] > 0.5) != (r["y"] == 0):
            raise R.MechanismIntegrityError(f"{r['game_id']} {r['player_id']}: P1 settlement differs from the frozen settlement")
        r["frozen_actual"] = s.get("actual")
        checks["P1_settlement_matches_frozen"] += 1
    if checks["P1_settlement_matches_frozen"] != len(p1_keys):
        raise R.MechanismIntegrityError(f"P1 rows {checks['P1_settlement_matches_frozen']} != frozen settled {len(p1_keys)}")
    # attach per-rung outcomes to ladders (for monotonicity of realized hit rates)
    by_t = defaultdict(dict)
    for r in rows:
        if r["pop"] in ("P3",) or r["is_natural"]:
            by_t[(r["game_id"], r["player_id"], r["stat"])][r["threshold"]] = r.get("y")
    for lad in ladders:
        lad["y_by_t"] = {str(k): v for k, v in by_t.get((lad["game_id"], lad["player_id"], lad["stat"]), {}).items()}
    # quote history for P1/P3 tickers and every natural-rung control ticker
    tickers = {r["ticker"] for r in rows}
    hist = quote_history(qdir, tickers)
    for r in rows:
        h = hist.get(r["ticker"], [])
        ko = parse(r["kickoff_utc"])
        conf = parse(r["confirmed_at"]) if r.get("confirmed_at") else None
        r["checkpoint_age_min"] = (ko - conf).total_seconds() / 60 if conf else None
        at_conf = quote_at(h, conf) if conf else None
        if at_conf:
            r["staleness_min"] = (ko - parse(at_conf["observed_at"])).total_seconds() / 60
            for k in ("volume", "open_interest", "yes_bid_size", "yes_ask_size"):
                r[f"ckpt_{k}"] = at_conf.get(k)
            r["history_quote_matches_checkpoint"] = (at_conf.get("yes_bid") == r["yes_bid"] and at_conf.get("yes_ask") == r["yes_ask"])
        if r["pop"] in ("P1",):
            tl = {}
            if h:
                first = h[0]
                tl["earliest"] = {"at": first["observed_at"], "hours_before": (ko - parse(first["observed_at"])).total_seconds() / 3600,
                                  **{k: first.get(k) for k in ("yes_bid", "yes_ask", "no_bid", "no_ask")}}
            for lab, mins in TIMING_2026:
                q = quote_at(h, ko - timedelta(minutes=mins))
                tl[lab] = None if q is None else {k: q.get(k) for k in ("yes_bid", "yes_ask", "no_bid", "no_ask", "observed_at")}
            tl["checkpoint"] = {k: r[k] for k in ("yes_bid", "yes_ask", "no_bid", "no_ask")}
            r["timeline"] = tl
    hist_rows = [{"ticker": t, **q} for t in sorted(hist) for q in hist[t]]
    return {"rows": rows, "ladders": ladders, "checks": dict(checks), "obs": obs_rows, "quote_history": hist_rows,
            "p1_keys": sorted(p1_keys), "exchange_count": len(exch)}


def pregame_2026(md: str, keys: list[tuple[str, str]]) -> dict[tuple, dict]:
    """Re-run the frozen Wave-2 observe stage's pregame builder at kickoff - 300 min for the games of `keys`, and apply
    the frozen RB_receptions ridge (no refit). Returns (game_id, player_id) -> features."""
    from nfl_edge.signal_discovery import evaluate_props as EP
    from nfl_edge.signal_discovery import game_features as G
    from nfl_edge.signal_discovery.wave2_models import predict_prop

    J = load_job()
    frozen = W.load_frozen(ROOT)
    params = frozen["props"]["families"][W.RB_FAMILY]
    games = J.population_games(weeks=[1, 2, 3, 4, 5])
    want_games = {g for g, _ in keys}
    games = games[games["game_id"].isin(want_games)]
    mt = G.metric_table(range(2012, W.SEASON + 1))
    out: dict[tuple, dict] = {}
    for k, part in games.groupby("kickoff"):
        cutoff = (k - pd.Timedelta(minutes=300)).to_pydatetime()
        for week, wp in part.groupby("week"):
            gr, pr, meta, fams = J.pregame(int(week), wp["game_id"].tolist(), cutoff, md, mt)
            fam = fams[W.RB_FAMILY]
            for gid in wp["game_id"]:
                mine = pr[pr["game_id"] == gid]
                d = EP.family_rows(mine, fam)
                if d.empty:
                    continue
                pred = predict_prop(params, d)
                for r, p in zip(d.to_dict("records"), pred, strict=True):
                    out[(gid, r["player_id"])] = {
                        "cutoff": cutoff.isoformat(), "pred": float(p), "model_median": float(p) + params["median_offset"],
                        "role_stability": r.get("role_stability"), "inj_status": r.get("inj.status"),
                        "b_season": R._f(r.get("b_season.receptions")), "b_ewma": R._f(r.get("b_ewma.receptions")),
                        "b_usage": R._f(r.get("b_usage.receptions")), "n_prior": int(r["n_prior"]),
                        **{c: R._f(r.get(c)) for c in ("snap_share_s", "snap_share_l", "sh_target_s", "sh_target_l", "sh_carry_s",
                                                       "sh_carry_l", "last_sh_target", "last_snap_share", "ctx.expected_script",
                                                       "rt_catch_rate", "off_pass_att", "off_target_rate")},
                        "injury_vintage": (meta.get("injury_vintage") or {}).get("retrieved_at"),
                        "depth_chart_vintage": meta.get("depth_chart_vintage"),
                        "latest_history_game": meta.get("latest_history_game")}
            print("pregame", cutoff.isoformat(), list(wp["game_id"]), flush=True)
    return out


# --------------------------------------------------------------------------- 2025 build (Wave-1 archival basis)


def build_2025(md: str) -> dict[str, Any]:
    from nfl_edge.signal_discovery import evaluate_props as EP
    from nfl_edge.signal_discovery import markets as M

    set1 = json.loads((ROOT / "research" / "signal_discovery_wave1" / "hypotheses_set1.json").read_text())
    fams = {f["id"]: f for f in set1["prop_families"]}
    files = sorted(str(p) for p in (Path(md) / "data" / "kalshi" / "backfill" / "horizons").glob("[0-9].jsonl"))
    pf = pd.read_parquet(ROOT / "research" / "signal_discovery_wave1" / "player_features.parquet")
    pf = EP.add_baselines(pf, set1["prop_families"])
    p25 = pf[pf["season"] == 2025]
    fam = EP.family_rows(p25, fams[W.RB_FAMILY])
    elig = set(zip(fam["game_id"], fam["player_id"], strict=True))
    feat = {(r["game_id"], r["player_id"]): r for r in fam.to_dict("records")}
    actual = {(r.game_id, r.player_id): float(r.receptions) for r in p25.itertuples() if pd.notna(r.receptions)}
    oos = pd.read_parquet(ROOT / "research" / "signal_discovery_wave1" / "prop_oos_predictions.parquet")
    oos = oos[(oos["family"] == W.RB_FAMILY) & (oos["season"] == 2025)]
    oos_pred = {(r.game_id, r.player_id): float(r.pred) for r in oos.itertuples()}
    snaps_by_ticker: dict[str, dict] = {}
    for f in files:
        with open(f) as fh:
            for line in fh:
                if '"KXNFLREC"' not in line:
                    continue
                r = json.loads(line)
                if r.get("series") == "KXNFLREC":
                    snaps_by_ticker[r["ticker"]] = {"snaps": r.get("snaps") or {}, "result": r.get("result"),
                                                    "final_volume": r.get("final_volume"), "anchor_ts": r.get("anchor_ts"),
                                                    "player_name": r.get("player_name")}
    out: dict[str, Any] = {}
    for ckpt in ("T-90m", "T-0"):
        rungs = M.kalshi_2025(files, ckpt)
        rungs = rungs[rungs["season"] == 2025]
        rungs, idc = M.attach_identity(rungs)
        rungs = rungs[rungs["identity"].isin(W.ACCEPTED_IDENTITY)]
        by: dict[tuple, list] = defaultdict(list)
        for r in rungs[rungs["stat"] == "receptions"].to_dict("records"):
            by[(r["game_id"], r["gsis_id"])].append({**r, "no_bid": None})
        rows, ladders, status = [], [], Counter()
        for (gid, pid), rs in sorted(by.items()):
            if (gid, pid) not in actual:
                status["NOT_IN_PLAYER_ROWS"] += 1
                continue
            nr = R.natural_and_rungs(rs)
            if nr["natural"] is None or nr["market_median"] is None:
                status["NO_VALID_RUNG_OR_MEDIAN"] += 1
                continue
            status["LADDER_PRICED"] += 1
            y_act = actual[(gid, pid)]
            res_by_t = {float(r["threshold"]): r.get("result") for r in rs}
            in_p2 = (gid, pid) in elig
            ladders.append({"game_id": gid, "player_id": pid, "in_p2": in_p2, "natural_t": nr["natural"]["threshold"],
                            "rungs": [(v["threshold"], (v["yes_bid"] + v["yes_ask"]) / 2) for v in nr["valid_rungs"]],
                            "actual": y_act, "checkpoint": ckpt})
            if not in_p2:
                continue
            for vr in nr["valid_rungs"]:
                ya, yb = vr["yes_ask"], vr["yes_bid"]
                na = round(1 - yb, 6)
                fy, fn = fees_for("KXNFLREC", pd.Timestamp(rs[0]["kickoff_ts"], unit="s", tz="UTC").isoformat(), ya, na)
                reps = R.representations(yb, ya, None, None)
                reps["C_norm_mid"] = None
                exr = res_by_t.get(vr["threshold"])
                row = {"season": 2025, "week": int(rs[0]["week"]), "game_id": gid, "player_id": pid, "team": rs[0].get("team"),
                       "player_name": rs[0].get("player_name"), "position": "RB", "stat": "receptions", "ticker": vr["ticker"],
                       "threshold": vr["threshold"], "offset": vr["offset"], "is_natural": vr["is_natural"],
                       "dist_half": vr["dist_half"], "n_valid": nr["n_valid"], "n_rungs": nr["n_rungs"],
                       "market_median": nr["market_median"], "natural_t": nr["natural"]["threshold"], "yes_bid": yb, "yes_ask": ya,
                       "no_bid": None, "no_ask": na, "price_basis": R.RECONSTRUCTED_NO_ASK, "C_status": R.NOT_AVAILABLE_2025,
                       "fee_yes": fy, "fee_no": fn, "checkpoint": ckpt, "kickoff_ts": rs[0]["kickoff_ts"], **reps}
                ex = {"result": exr, "settlement_value_dollars": None} if exr in ("yes", "no") else None
                if ex is None:
                    row.update({"y": None, "settle_source": R.SETTLEMENT_UNAVAILABLE, "actual": y_act, "result": exr})
                    row["stat_agrees"] = None
                else:
                    row.update(R.settle(row, ex, y_act))
                row.update(R.economics_row(row))
                row.update(R.residual_fields(row))
                if vr["is_natural"]:
                    f = feat[(gid, pid)]
                    row.update({"pop": "P2", "role_stability": f.get("role_stability"), "b_season": R._f(f.get("b_season.receptions")),
                                "b_ewma": R._f(f.get("b_ewma.receptions")), "b_usage": R._f(f.get("b_usage.receptions")),
                                "sh_target_l": R._f(f.get("sh_target_l")), "sh_target_s": R._f(f.get("sh_target_s")),
                                "snap_share_l": R._f(f.get("snap_share_l")), "snap_share_s": R._f(f.get("snap_share_s")),
                                "last_sh_target": R._f(f.get("last_sh_target")), "inj_status": f.get("inj.status"),
                                "ctx.expected_script": R._f(f.get("ctx.expected_script")), "n_prior": int(f.get("n_prior") or 0),
                                "pred_oos_wave1": oos_pred.get((gid, pid))})
                    sn = snaps_by_ticker.get(vr["ticker"]) or {}
                    row["timeline"] = {h: (sn.get("snaps") or {}).get(h) for h in TIMING_2025}
                    row["final_volume"] = sn.get("final_volume")
                    rows.append(row)
                else:
                    rows.append({**row, "pop": "P2_ALL_RUNGS"})
                if vr["is_natural"]:
                    rows.append({**row, "pop": "P2_ALL_RUNGS", "timeline": None})
        out[ckpt] = {"rows": rows, "ladders": ladders, "status": dict(status), "identity": idc}
    return out


# --------------------------------------------------------------------------- historical RB corpus (2016-2025)


def history_corpus() -> list[dict]:
    """RB_receptions family rows 2016-2025 (Wave-1 player rows; players who appeared): baseline, recency and outcome.
    Used only for the dispersion (M5) and the 'justified' recency response (M14); never for the study sample."""
    from nfl_edge.signal_discovery import evaluate_props as EP

    set1 = json.loads((ROOT / "research" / "signal_discovery_wave1" / "hypotheses_set1.json").read_text())
    fams = {f["id"]: f for f in set1["prop_families"]}
    pf = pd.read_parquet(ROOT / "research" / "signal_discovery_wave1" / "player_features.parquet")
    pf = EP.add_baselines(pf, set1["prop_families"])
    pf = pf.sort_values(["player_id", "season", "week", "game_id"]).reset_index(drop=True)
    g = pf.groupby("player_id")["receptions"]
    pf["last1"] = g.shift(1)
    pf["long16"] = g.transform(lambda s: s.shift(1).rolling(16, min_periods=6).mean())
    fam = EP.family_rows(pf[(pf["season"] >= 2016) & (pf["season"] <= 2025)], fams[W.RB_FAMILY])
    fam = fam[fam["receptions"].notna()]
    return [{"game_id": r["game_id"], "player_id": r["player_id"], "season": int(r["season"]),
             "b_ewma": R._f(r["b_ewma.receptions"]), "b_usage": R._f(r["b_usage.receptions"]), "last1": R._f(r["last1"]),
             "long16": R._f(r["long16"]), "actual": float(r["receptions"])} for r in fam.to_dict("records")]


def context_features(rows: list[dict], season: int) -> None:
    """M8 / M13 / M16 descriptors: prior-season team and player profiles, the game's QB, lines and kickoff slot.
    Prior-season values only, except the game's pass-attempt leader (a role descriptor, pre-registered as such)."""
    prev = player_games([season - 1])
    cur = player_games([season])
    prev_reg = prev[prev["season_type"] == "REG"] if "season_type" in prev else prev
    rb = prev_reg[prev_reg["position"] == "RB"]
    team_rb_share = (rb.groupby("team")["targets"].sum() / prev_reg.groupby("team")["targets"].sum()).to_dict()
    opp_rb_allowed = (rb.groupby("opp")["receptions"].sum() / prev_reg.groupby("opp")["game_id"].nunique()).to_dict()
    qb = prev_reg[prev_reg["position"] == "QB"].groupby("player_id")[["attempts", "scrambles", "sacks_taken"]].sum()
    qb = qb[qb["attempts"] >= 200]
    qb_scr = (qb["scrambles"] / (qb["attempts"] + qb["scrambles"] + qb["sacks_taken"])).to_dict()
    scr_hi = float(np.quantile(list(qb_scr.values()), 2 / 3)) if qb_scr else None
    st = nfl_stats(season - 1)
    st = st[(st["season_type"] == "REG") & (st["position"] == "RB")]
    ppr = st.groupby("player_id")["fantasy_points_ppr"].sum().sort_values(ascending=False)
    ppr_rank = {p: i + 1 for i, p in enumerate(ppr.index)}
    rpg = (st.groupby("player_id")["receptions"].sum() / st.groupby("player_id")["week"].nunique()).to_dict()
    passer = cur[cur["attempts"].fillna(0) > 0].sort_values("attempts", ascending=False).drop_duplicates(["game_id", "team"])
    passer = {(r.game_id, r.team): r.player_id for r in passer.itertuples()}
    sched = schedule().set_index("game_id")
    for r in rows:
        g = sched.loc[r["game_id"]]
        home = r["team"] == g["home_team"]
        spread = R._f(g.get("spread_line"))
        total = R._f(g.get("total_line"))
        team_spread = None if spread is None else (spread if home else -spread)  # > 0: team favoured
        q = passer.get((r["game_id"], r["team"]))
        r.update({"ctx_team_fav_points": team_spread,
                  "ctx_team_implied_total": None if spread is None or total is None else total / 2 + team_spread / 2,
                  "ctx_prime_time": str(g.get("gametime") or "") >= "19:00" or g.get("weekday") in ("Thursday", "Monday"),
                  "ctx_weekday": g.get("weekday"), "ctx_gametime": g.get("gametime"),
                  "ctx_team_rb_target_share_prev": R._f(team_rb_share.get(r["team"])),
                  "ctx_opp_rb_rec_allowed_prev": R._f(opp_rb_allowed.get(r.get("opp") or (g["away_team"] if home else g["home_team"]))),
                  "ctx_game_qb": q, "ctx_qb_scramble_prev": R._f(qb_scr.get(q)),
                  "ctx_qb_mobile": None if q not in qb_scr or scr_hi is None else qb_scr[q] >= scr_hi,
                  "ctx_ppr_rank_prev": ppr_rank.get(r["player_id"]), "ctx_rec_per_game_prev": R._f(rpg.get(r["player_id"]))})
        if not r.get("opp"):
            r["opp"] = g["away_team"] if home else g["home_team"]


# --------------------------------------------------------------------------- build command


def cmd_build(a) -> int:
    md = str(Path(a.market_data).resolve())
    b26 = build_2026(md, Path(a.quotes))
    hist = History(player_games(range(2023, 2027)))
    sched = schedule().set_index("game_id")
    p1 = [r for r in b26["rows"] if r["pop"] == "P1"]
    pre = pregame_2026(md, [(r["game_id"], r["player_id"]) for r in p1])
    # observe-stage reproduction check against the committed frozen observation rows
    obs = {(o["game_id"], o["player_id"]): o for o in b26["obs"] if o.get("player_id")}
    repro = Counter()
    for k, o in obs.items():
        p = pre.get(k)
        if p is None:
            repro["frozen_obs_missing_in_rebuild"] += 1
            continue
        same = (o.get("role_stability") == p["role_stability"] and abs((o.get("b_season") or 0) - (p["b_season"] or 0)) < 1e-6
                and abs((o.get("sh_target_l") or 0) - (p["sh_target_l"] or 0)) < 1e-6)
        repro["match" if same else "differs"] += 1
    for r in b26["rows"]:
        if r["position"] != "RB" or r["stat"] != "receptions":
            continue
        g = sched.loc[r["game_id"]]
        date = pd.Timestamp(g["gameday"])
        r.update({f"h_{k}": v for k, v in hist.features(r["player_id"], r["team"], date, r["threshold"]).items()})
        p = pre.get((r["game_id"], r["player_id"]))
        if p:
            r.update({f"pre_{k}": v for k, v in p.items()})
    b25 = build_2025(md)
    hist25 = History(player_games(range(2022, 2026)))
    for ck in b25:
        for r in b25[ck]["rows"]:
            if r["pop"] != "P2":
                continue
            g = sched.loc[r["game_id"]]
            r.update({f"h_{k}": v for k, v in hist25.features(r["player_id"], r["team"], pd.Timestamp(g["gameday"]), r["threshold"]).items()})
    context_features([r for r in b26["rows"] if r["pop"] in ("P1", "P3")], 2026)
    context_features([r for ck in b25 for r in b25[ck]["rows"] if r["pop"] == "P2"], 2025)
    corpus = history_corpus()
    OUT.mkdir(parents=True, exist_ok=True)
    hashes = {
        "rows_2026": write_gz(OUT / "rows_2026.jsonl.gz", b26["rows"]),
        "ladders_2026": write_gz(OUT / "ladders_2026.jsonl.gz", b26["ladders"]),
        "rows_2025": write_gz(OUT / "rows_2025.jsonl.gz", [{**r, "checkpoint": ck} for ck in b25 for r in b25[ck]["rows"]]),
        "ladders_2025": write_gz(OUT / "ladders_2025.jsonl.gz", [l for ck in b25 for l in b25[ck]["ladders"]]),
        "quote_history_2026": write_gz(OUT / "quote_history_2026.jsonl.gz", b26["quote_history"]),
        "rb_history_2016_2025": write_gz(OUT / "rb_history_2016_2025.jsonl.gz", corpus),
    }
    meta = {"code_sha": code_sha(), "market_data_commit": MD_COMMIT, "discovery_run": DISCOVERY_RUN,
            "exchange_settled_markets": b26["exchange_count"], "checks_2026": b26["checks"], "observe_reproduction": dict(repro),
            "status_2025": {ck: b25[ck]["status"] for ck in b25}, "identity_2025": {ck: b25[ck]["identity"] for ck in b25},
            "hashes": hashes, "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "nflverse_manifest_tail": _nflverse_manifest()}
    write_json(OUT / "build_manifest.json", meta)
    print(json.dumps({k: meta[k] for k in ("checks_2026", "observe_reproduction", "status_2025")}, indent=1, default=_default))
    return 0


def _nflverse_manifest() -> dict[str, Any]:
    p = ROOT / "data" / "raw" / "nflverse" / "_manifest.jsonl"
    out = {}
    if p.exists():
        for line in p.read_text().splitlines():
            r = json.loads(line)
            if any(s in r["path"] for s in ("stats_player_week_2026", "stats_player_week_2025", "games.csv", "roster_2026",
                                            "depth_charts_2026", "snap_counts_2026", "play_by_play_2026")):
                out[r["path"]] = {"retrieved_at": r.get("retrieved_at"), "sha256": r.get("sha256")}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("extract-quotes")
    e.add_argument("--market-data", required=True)
    e.add_argument("--out", required=True)
    b = sub.add_parser("build")
    b.add_argument("--market-data", required=True)
    b.add_argument("--quotes", required=True)
    sub.add_parser("analyze")
    a = ap.parse_args(argv)
    if a.cmd == "analyze":
        spec = importlib.util.spec_from_file_location("rb_mech_analyze", Path(__file__).with_name("rb_receptions_mechanism_analyze.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.main()
    return {"extract-quotes": cmd_extract, "build": cmd_build}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
