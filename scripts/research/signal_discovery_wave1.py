#!/usr/bin/env python3
"""Football Signal Discovery Lab, Wave 1 -- NFL runner. RESEARCH ONLY.

Protocol: docs/research/FOOTBALL_SIGNAL_DISCOVERY_WAVE1_PROTOCOL.md

Stages:
  game-features    market-blind team ratings + game feature rows, every game 2015-2026 (strictly-earlier
                   games only; per-season ridge strengths from Y-2/Y-1) -> research/signal_discovery_wave1/
  player-features  point-in-time player opportunity features 2016-2026 (frozen priors from 2012-2015)
  freeze-set1      write the pre-registered hypothesis files and print their hashes
  screen           Stage A, block A seasons only (2015-2019)
  evaluate-game    locked evaluation of the game hypotheses (refuses unless hashes are in the protocol)
  evaluate-props   locked evaluation of the prop hypotheses
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import pandas as pd  # noqa: E402

from nfl_edge.signal_discovery import SIGNAL_DISCOVERY_VERSION  # noqa: E402

OUT = ROOT / "research" / "signal_discovery_wave1"
PROTOCOL_DOC = ROOT / "docs" / "research" / "FOOTBALL_SIGNAL_DISCOVERY_WAVE1_PROTOCOL.md"
GAME_SEASONS = list(range(2015, 2027))


def git_sha() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:  # pragma: no cover
        return None


def canon_sha(payload) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def frame_sha(df: pd.DataFrame) -> str:
    return hashlib.sha256(pd.util.hash_pandas_object(df.sort_index(axis=1), index=False).values.tobytes()).hexdigest()


def cmd_game_features(args) -> int:
    from nfl_edge.signal_discovery import game_features as G
    from nfl_edge.sim import data as D
    from nfl_edge.sim import opponent_adjust as OA

    t0 = time.time()
    mt = G.metric_table(range(2012, 2027))
    sched = pd.DataFrame(D.schedule().to_dicts())
    lambdas = {}
    for s in GAME_SEASONS:
        lambdas[s] = OA.select_lambdas(mt, s, metrics=G.METRICS)["lambdas"]
    rows = G.game_rows(mt, sched, GAME_SEASONS, lambdas)
    qbc = G.qb_change(sched[["game_id", "season", "week", "home_team", "away_team", "home_qb_id", "away_qb_id"]])
    rows = rows.merge(qbc.rename(columns={"team": "home_team", "qb_change": "ctx.home_qb_change"}), on=["game_id", "home_team"], how="left")
    rows = rows.merge(qbc.rename(columns={"team": "away_team", "qb_change": "ctx.away_qb_change"}), on=["game_id", "away_team"], how="left")
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "game_features.parquet"
    for c in rows.columns:
        if rows[c].dtype == object and rows[c].map(lambda v: isinstance(v, (list, dict))).any():
            rows[c] = rows[c].map(lambda v: json.dumps(v) if isinstance(v, (list, dict)) else v)
    rows.to_parquet(path, index=False)
    manifest = {"version": SIGNAL_DISCOVERY_VERSION, "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
                "code_sha": git_sha(), "rows": len(rows), "seasons": GAME_SEASONS, "frame_sha256": frame_sha(rows),
                "lambdas": {str(k): v for k, v in lambdas.items()}, "metrics": list(G.METRICS),
                "reads": "pbp (team-game metrics of strictly earlier games), participation, schedule identity/site/rest/"
                         "div/roof/realised QB ids; NO lines, NO odds, NO target result",
                "seconds": round(time.time() - t0, 1)}
    (OUT / "game_features_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
    print(json.dumps({k: v for k, v in manifest.items() if k != "lambdas"}, indent=1))
    return 0


SET1_FILE = OUT / "hypotheses_set1.json"
SET2_FILE = OUT / "hypotheses_set2.json"


def load_game_features() -> pd.DataFrame:
    m = json.loads((OUT / "game_features_manifest.json").read_text())
    gf = pd.read_parquet(OUT / "game_features.parquet")
    if frame_sha(gf) != m["frame_sha256"]:
        raise SystemExit("game feature table does not match its manifest; refusing")
    return gf


def thresholds_from(gf: pd.DataFrame) -> dict:
    """Outcome-blind tier thresholds from the distribution of the feature itself (rounded)."""
    a = gf["net.epa_play"].abs().dropna()
    r = lambda x: round(round(float(x) / 0.005) * 0.005, 3)  # noqa: E731
    npr = pd.concat([gf["mx_home.neutral_pass_rate"], gf["mx_away.neutral_pass_rate"]]).dropna()
    return {"closeness": r(a.quantile(0.20)), "control_moderate": r(a.quantile(0.60)), "control_strong": r(a.quantile(0.80)),
            "run_leaning_neutral_pass_rate": round(float(npr.median()), 3),
            "quantiles_note": "closeness ~P20, moderate ~P60, strong ~P80 of |net EPA/play|; run-leaning = below the median "
                              "adjusted neutral pass rate; all over 2015-2026 feature rows, no outcome read"}


def derive_flags(gf: pd.DataFrame, th: dict) -> list[dict]:
    """Pregame claims / flags from features only (market-blind, outcome-blind)."""
    out = []
    for r in gf.to_dict("records"):
        r = {k: (None if isinstance(v, float) and v != v else v) for k, v in r.items()}
        net = r.get("net.epa_play")
        r["control_side"] = r["control_strength"] = None
        if net is not None and abs(net) >= th["control_moderate"]:
            r["control_side"] = "home" if net > 0 else "away"
            r["control_strength"] = "STRONG" if abs(net) >= th["control_strong"] else "MODERATE"
        r["closeness"] = net is not None and abs(net) <= th["closeness"]
        qh, qa = r.get("q_home_def.epa_play"), r.get("q_away_def.epa_play")
        r["flag.def_suppression"] = qh is not None and qa is not None and qh >= 0.5 and qa >= 0.5
        cs = r["control_side"]
        npr = r.get(f"mx_{cs}.neutral_pass_rate") if cs else None
        r["flag.control_run_style"] = bool(cs) and npr is not None and npr <= th["run_leaning_neutral_pass_rate"]
        hr, ar = r.get("home_rest"), r.get("away_rest")
        r["flag.short_week_side"] = ("home" if hr is not None and ar is not None and hr <= 5 and ar >= 6 else
                                     "away" if hr is not None and ar is not None and ar <= 5 and hr >= 6 else None)
        r["flag.bye_side"] = ("home" if hr is not None and ar is not None and hr >= 13 and ar <= 8 else
                              "away" if hr is not None and ar is not None and ar >= 13 and hr <= 8 else None)
        hq, aq = bool(r.get("ctx.home_qb_change")), bool(r.get("ctx.away_qb_change"))
        r["flag.qb_change_side"] = "home" if hq and not aq else "away" if aq and not hq else None
        r["flag.indoor"] = r.get("roof") in ("dome", "closed")
        r["div_game"] = bool(r.get("div_game"))
        r["pace_claim"] = r["scoring_env_claim"] = None
        r["defensive_suppression_claim"] = r["flag.def_suppression"]
        r["disruption_sides"] = []
        r["finding_codes"] = []
        out.append(r)
    return out


def cmd_freeze_set1(args) -> int:
    from nfl_edge.signal_discovery import hypotheses as H

    gf = load_game_features()
    th = thresholds_from(gf)
    payload = {"set": 1, "version": SIGNAL_DISCOVERY_VERSION, "thresholds": th, "game_hypotheses": H.build_game_set1(th),
               "walk_forward": H.WALK_FORWARD, "status_rule": H.STATUS_RULE, "prop_families": H.PROP_FAMILIES,
               "prop_model": H.PROP_MODEL}
    SET1_FILE.write_text(json.dumps(payload, indent=2, sort_keys=True))
    print("set1 sha256", canon_sha(payload))
    print(json.dumps(th, indent=1))
    return 0


def cmd_freeze_set2(args) -> int:
    from nfl_edge.signal_discovery import hypotheses as H

    payload = {"set": 2, "version": SIGNAL_DISCOVERY_VERSION, "hypotheses": H.GAME_SET2, "decisive_block": "B"}
    SET2_FILE.write_text(json.dumps(payload, indent=2, sort_keys=True))
    print("set2 sha256", canon_sha(payload))
    return 0


def check_frozen(path: Path) -> dict:
    payload = json.loads(path.read_text())
    sha = canon_sha(payload)
    if not PROTOCOL_DOC.exists():
        raise SystemExit("protocol document missing; refusing")
    text = PROTOCOL_DOC.read_text()
    if "Status: **PRE-REGISTERED**" not in text or sha not in text:
        raise SystemExit(f"{path.name} sha {sha} not registered in the protocol; refusing")
    return payload


def _game_rows(seasons) -> tuple[list[dict], dict]:
    from nfl_edge.signal_discovery import markets as M
    from nfl_edge.signal_discovery.evaluate_game import build_rows
    from nfl_edge.signal_discovery.outcomes import load_outcomes
    from nfl_edge.sim import data as D

    set1 = check_frozen(SET1_FILE)
    gf = load_game_features()
    gf = gf[gf["season"].isin(seasons)]
    feats = derive_flags(gf, set1["thresholds"])
    sched = pd.DataFrame(D.schedule().to_dicts())
    sched = sched[sched["season"].isin(seasons)]
    lines = {r["game_id"]: r for r in M.game_lines(sched).to_dict("records")}
    outcomes = load_outcomes(sched, seasons)
    rows, excl = build_rows(feats, lines, outcomes)
    return rows, dict(excl)


def cmd_screen(args) -> int:
    from nfl_edge.signal_discovery.screen import screen

    set1 = check_frozen(SET1_FILE)
    block_a = set1["status_rule"]["blocks"]["A"]
    rows, excl = _game_rows(block_a)
    assert all(r["season"] in block_a for r in rows)
    rep = screen(rows)
    rep.update({"exclusions": excl, "seasons": block_a, "code_sha": git_sha()})
    (OUT / "stage_a_screen.json").write_text(json.dumps(rep, indent=1, sort_keys=True, default=float))
    for e in rep["top"]["market"][:30]:
        print(f"{e['scope'][:10]:<10} {e['feature'][:46]:<46} {e['target']:<15} n={e['n']} b={e['beta_per_sd']:+.3f} "
              f"z={e['z']:+.2f} q={e['q_bh_whole_screen']:.3f} ss={e.get('seasons_same_sign')}/{e.get('seasons')}")
    print({k: rep[k] for k in ("associations_screened", "market_q_lt_0_05", "market_q_lt_0_10")})
    return 0


def cmd_evaluate_game(args) -> int:
    from nfl_edge.signal_discovery import deep_dive
    from nfl_edge.signal_discovery.evaluate_game import evaluate_all, walk_forward

    set1 = check_frozen(SET1_FILE)
    set2 = check_frozen(SET2_FILE) if SET2_FILE.exists() else None
    seasons = list(range(2015, 2026))
    rows, excl = _game_rows(seasons)
    rule = set1["status_rule"]
    specs = list(set1["game_hypotheses"]) + ([dict(h, set=2) for h in set2["hypotheses"]] if set2 else [])
    ev = evaluate_all(rows, specs, rule)
    rep = {"version": SIGNAL_DISCOVERY_VERSION, "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
           "code_sha": git_sha(), "set1_sha256": canon_sha(set1), "set2_sha256": canon_sha(set2) if set2 else None,
           "seasons": seasons, "rows": len(rows), "rows_with_spread": sum(r["m.spread_home"] is not None for r in rows),
           "rows_with_ml": sum(r["m.ml_home_novig"] is not None for r in rows), "exclusions": excl, "seed": 20261008,
           "summary": ev["summary"], "results": {k: {kk: vv for kk, vv in v.items() if kk != "rows"} for k, v in ev["results"].items()},
           "walk_forward": {n: walk_forward(rows, n, sp) for n, sp in set1["walk_forward"].items()},
           "deep_dive": deep_dive.run(rows, ev["results"])}
    if set2:
        bb = [r for r in rows if r["season"] in rule["blocks"]["B"]]
        evb = evaluate_all(bb, [dict(h, set=2) for h in set2["hypotheses"]], rule)
        rep["set2_block_b"] = {"summary": evb["summary"], "results": {k: {kk: vv for kk, vv in v.items() if kk != "rows"} for k, v in evb["results"].items()}}
    (OUT / "game_evaluation_report.json").write_text(json.dumps(rep, indent=1, sort_keys=True, default=float))
    for s in ev["summary"]:
        f = lambda v: "  —  " if v is None else f"{v:+.3f}"  # noqa: E731
        print(f"{s['id']:<14} {s['status']:<20} f={f(s['football_effect'])} qf={f(s['football_q'])} m={f(s['market_effect'])} qm={f(s['market_q'])}  {s['name'][:58]}")
    return 0


def cmd_player_features(args) -> int:
    from nfl_edge.signal_discovery import player_features as P

    gf = load_game_features()
    pf = P.build(gf)
    keep = [c for c in pf.columns if not c.startswith("_")]
    pf = pf[keep]
    for c in pf.columns:
        if pf[c].dtype == object:
            pf[c] = pf[c].map(lambda v: json.dumps(v) if isinstance(v, (list, dict)) else v)
    pf.to_parquet(OUT / "player_features.parquet", index=False)
    m = {"rows": len(pf), "frame_sha256": frame_sha(pf), "code_sha": git_sha(), "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
         "role_stability": pf["role_stability"].value_counts().to_dict(), "positions": pf["position"].value_counts().to_dict()}
    (OUT / "player_features_manifest.json").write_text(json.dumps(m, indent=2, sort_keys=True, default=str))
    print(m)
    return 0


def cmd_evaluate_props(args) -> int:
    from nfl_edge.signal_discovery import evaluate_props as EP
    from nfl_edge.sim import data as D

    set1 = check_frozen(SET1_FILE)
    m = json.loads((OUT / "player_features_manifest.json").read_text())
    pf = pd.read_parquet(OUT / "player_features.parquet")
    if frame_sha(pf) != m["frame_sha256"]:
        raise SystemExit("player feature table does not match its manifest; refusing")
    fams = set1["prop_families"]
    spec = set1["prop_model"]
    pf = EP.add_baselines(pf, fams)
    ladders = pd.read_parquet(OUT / "prop_ladders.parquet")
    ladders["natural"] = ladders["natural"].map(lambda v: json.loads(v) if isinstance(v, str) else None)
    lad_meta = json.loads((OUT / "prop_ladders_manifest.json").read_text())
    if frame_sha(ladders.drop(columns=["natural"])) != lad_meta["frame_sha256"]:
        raise SystemExit("ladder table does not match its manifest; refusing")
    results, R_by = {}, {}
    for fam in fams:
        fspec = dict(spec)
        fspec["model_features"] = [f.replace("{stat}", fam["stat"]) for f in spec["model_features"]]
        wf = EP.walk_forward_family(pf, fam, fspec)
        if "rows" not in wf:
            results[fam["id"]] = {"summary": wf}
            continue
        R_by[fam["id"]] = wf["rows"]
        mk = EP.market_tests(wf["rows"], fam, ladders, pf, fspec)
        results[fam["id"]] = {"summary": wf["summary"], "market": mk}
        s = wf["summary"]
        print(f"{fam['id']:<16} n={s['n']:<6} MAE season={s['mae.SEASON_AVG']:.2f} ewma={s['mae.EWMA']:.2f} usage={s['mae.USAGE']:.2f} "
              f"model={s['mae.MODEL']:.2f} gain_vs_best={s['mae_gain_vs_best_baseline']['mae_delta']:+.3f} "
              f"pi80={s['pi80_coverage']:.2f} market_rows={mk.get('ladders_matched')}", flush=True)
    # FDR over every (family, group) ablation test
    from nfl_edge.signal_discovery import stats

    keys, ps = [], []
    for fid, r in results.items():
        for g, v in (r["summary"].get("groups") or {}).items():
            keys.append((fid, g))
            ps.append(v["p"])
    qs = stats.benjamini_hochberg(ps)
    for (fid, g), q in zip(keys, qs, strict=False):
        results[fid]["summary"]["groups"][g]["q_bh_all_prop_groups"] = q
        results[fid]["summary"]["groups"][g]["status"] = EP.status_for(results[fid], g, 1, q)
    mkeys, mps = [], []
    for fid, r in results.items():
        mk = r.get("market") or {}
        for g, v in (mk.get("signal_feature_vs_residual") or {}).items():
            mkeys.append((fid, g))
            mps.append(v["p"])
        if mk.get("residual_on_model_gap"):
            mkeys.append((fid, "MODEL_GAP"))
            mps.append(mk["residual_on_model_gap"]["p"])
    mqs = stats.benjamini_hochberg(mps)
    for (fid, g), q in zip(mkeys, mqs, strict=False):
        mk = results[fid]["market"]
        if g == "MODEL_GAP":
            mk["residual_on_model_gap"]["q_bh_all_market_tests"] = q
        else:
            mk["signal_feature_vs_residual"][g]["q_bh_all_market_tests"] = q
    tg = pd.DataFrame(D.load("team_games", list(range(2016, 2027))).to_dicts())
    rep = {"version": SIGNAL_DISCOVERY_VERSION, "generated_at": datetime.now(UTC).isoformat(timespec="seconds"), "code_sha": git_sha(),
           "set1_sha256": canon_sha(set1), "ladders": lad_meta, "families": results,
           "game_script_effects": EP.game_script_effects(pf, tg), "correlations": EP.correlations(R_by),
           "hypotheses_tested_group_ablations": len(ps), "hypotheses_tested_market": len(mps)}
    (OUT / "prop_evaluation_report.json").write_text(json.dumps(rep, indent=1, sort_keys=True, default=float))
    rows = pd.concat([v.assign(family=k) for k, v in R_by.items()], ignore_index=True)
    rows[["family", "game_id", "season", "week", "player_id", "team", "position", "role_stability", "pred"]].to_parquet(OUT / "prop_oos_predictions.parquet", index=False)
    return 0


def cmd_prop_ladders(args) -> int:
    """Market side: Kalshi player-prop rungs -> GSIS identity -> one ladder per (game, player, stat).

    Inputs (both derived from the ``market-data`` branch, recorded with SHA-256 in the manifest):
      --horizons  directory with data/kalshi/backfill/horizons/{0..5}.jsonl (2025 archive; checkpoint T-90m)
      --agg       pickle from scripts/research/signal_discovery_kalshi_quote_aggregate.py over
                  data/kalshi/capture/**.quotes.jsonl (2026; checkpoint LAST_PREGAME, kept only if <= 24 h before kickoff)
    """
    import glob
    import pickle

    from nfl_edge.signal_discovery import markets as M

    files = sorted(glob.glob(os.path.join(args.horizons, "*.jsonl")))
    r25 = M.kalshi_2025(files)
    agg = pickle.load(open(args.agg, "rb"))["T"]
    r26 = M.kalshi_2026(agg)
    stale = r26["minutes_to_kickoff"].isna() | (r26["minutes_to_kickoff"] > 1440)
    r26 = r26[~stale]
    rungs, idc = M.attach_identity(pd.concat([r25, r26], ignore_index=True))
    lad = M.ladders(rungs)
    lad["natural"] = lad["natural"].map(lambda v: json.dumps(v) if isinstance(v, dict) else None)
    lad.to_parquet(OUT / "prop_ladders.parquet", index=False)
    man = {"generated_at": datetime.now(UTC).isoformat(timespec="seconds"), "code_sha": git_sha(),
           "inputs": {os.path.basename(f): hashlib.sha256(open(f, "rb").read()).hexdigest() for f in files + [args.agg]},
           "market_data_branch_sha": args.market_data_sha, "rungs_2025": int(len(r25)), "rungs_2026": int(len(r26)),
           "rungs_2026_dropped_stale_gt_24h": int(stale.sum()), "identity": idc, "ladders": int(len(lad)),
           "ladders_with_median": int(lad["market_median"].notna().sum()),
           "checkpoints": {"2025": "T-90m (YES bid/ask; NO ask = 1 - YES bid)", "2026": "LAST_PREGAME <= 24h (both asks captured)"},
           "frame_sha256": frame_sha(lad.drop(columns=["natural"]))}
    (OUT / "prop_ladders_manifest.json").write_text(json.dumps(man, indent=2, sort_keys=True))
    print(json.dumps(man, indent=1))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("game-features", "freeze-set1", "freeze-set2", "screen", "evaluate-game", "player-features"):
        sub.add_parser(name)
    pl_ = sub.add_parser("prop-ladders")
    pl_.add_argument("--horizons", required=True)
    pl_.add_argument("--agg", required=True)
    pl_.add_argument("--market-data-sha", default=None)
    ep = sub.add_parser("evaluate-props")
    args = ap.parse_args()
    return {"game-features": cmd_game_features, "freeze-set1": cmd_freeze_set1, "freeze-set2": cmd_freeze_set2, "screen": cmd_screen,
            "evaluate-game": cmd_evaluate_game, "player-features": cmd_player_features,
            "evaluate-props": cmd_evaluate_props, "prop-ladders": cmd_prop_ladders}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
