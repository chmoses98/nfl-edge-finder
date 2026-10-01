#!/usr/bin/env python3
"""The weekly research loop: BOARD EDGE DISCOVERY, SCRIPT AUTOPSY and THESIS IMPROVEMENT, per week and cumulative.

    python3 scripts/research/weekly_research.py --season 2026 --weeks 1,2,3 --board <dir with board_rows.wkNN.jsonl.gz> \\
        --market-data /tmp/md --out data/research/weekly/2026 [--handicap-ref origin/handicap-data]

Writes, for every week W in --weeks and for the cumulative scope (weeks lo..hi):

    <out>/week_WW/{BOARD_EDGE_DISCOVERY,SCRIPT_AUTOPSY,THESIS_IMPROVEMENT}.md + research.json
    <out>/cumulative_wkLO-HI/...  (same files)

Inputs are all derived or immutable: the full-board table (scripts/research/board_research.py), the published
player-autopsy and anatomy corpora, the three-arm evaluations, nflverse play-by-play / rosters, the owner's imported
wagers and settlements on handicap-data (read with `git show`, never written), and the hypothesis registry.
RESEARCH ONLY: nothing here reaches the betting path, and every report says so.
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import os
import subprocess
import sys
from collections import Counter, defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.research import board as B                                       # noqa: E402
from nfl_edge.research import board_hypotheses as BH                           # noqa: E402
from nfl_edge.research import board_miner as M                                 # noqa: E402
from nfl_edge.research import expression_autopsy as EA                         # noqa: E402
from nfl_edge.research import hypothesis_registry_v2 as HR                     # noqa: E402
from nfl_edge.research import script_autopsy as SA                             # noqa: E402
from nfl_edge.research import thesis as TH                                     # noqa: E402
from nfl_edge.research import weekly_reports as WR                             # noqa: E402
from nfl_edge.shadow import player_autopsy as PA                               # noqa: E402

FIELDS = B.SLIM_FIELDS + ("mid", "close_mid", "team_implied_points", "player_disagreement", "data_only_disagreement",
                          "return_yes", "return_no", "is_main_rung", "rung_offset", "obs_state", "two_sided", "player_name",
                          "env_home_margin", "env_total", "env_home_points", "env_away_points", "settlement_source")
LIMITATIONS = [
    "Weeks 1–3 are 48 games: every board pattern is hypothesis-generating; nothing is confirmatory before the preregistered window.",
    "The market mid is the benchmark; the board table settles from football only the families the production engines settle "
    "(the exchange-only tier is outside the canonical analysis).",
    "Weeks 1–3 have no frozen team-volume projection; their script autopsy compares against a QB pass-attempts ladder "
    "median or the team's prior-game mean. From Week 4 the simulation's script summary is the expectation.",
    "Script labels describe the final score progression; the simulator does not draw score-state paths (it reports pass "
    "rate conditional on the final margin as the nearest proxy).",
    "Thesis buckets of actual positions are INFERRED from what each contract pays on unless a thesis was recorded.",
    "The role-certainty proxy is P(plays) and the prior-game count from the incumbent's anatomy, not a role model.",
]


def log(*a):
    print(*a, flush=True)


def _git_source(repo: str, ref: str):
    import importlib.util
    spec = importlib.util.spec_from_file_location("_board_research_src", os.path.join(ROOT, "scripts", "research", "board_research.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.GitSource(repo, ref)


def git_json_files(ref: str, prefix: str, repo: str) -> list:
    """Every .json under `prefix` of `ref`, read from git objects (prefetched in batches; never checked out)."""
    try:
        src = _git_source(repo, ref)
        items = [(p, o) for p, o in src.ls(prefix) if p.endswith(".json")]
    except subprocess.CalledProcessError:
        return []
    src.prefetch(items)
    out = []
    for _p, data in src.stream(items):
        try:
            out.append(json.loads(data))
        except ValueError:
            continue
    return out


def load_board(board_dir: str, weeks) -> list:
    rows = []
    for w in weeks:
        p = os.path.join(board_dir, f"board_rows.wk{int(w):02d}.jsonl.gz")
        if os.path.exists(p):
            rows.extend(B.read_jsonl_gz(p, FIELDS))
        else:
            log(f"WARNING: no board rows for week {w} at {p}")
    return rows


def corpus(roots, suffix):
    out = []
    for r in roots:
        for p in sorted(glob.glob(os.path.join(r, "*", f"*.{suffix}.jsonl.gz"))):
            with gzip.open(p, "rt") as f:
                out.extend(json.loads(l) for l in f if l.strip())
    return out


def pbp_by_game(season: int):
    import polars as pl
    cols = ["game_id", "season", "week", "home_team", "away_team", "posteam", "qtr", "play_type", "pass_attempt", "rush_attempt",
            "qb_dropback", "qb_scramble", "sack", "qb_kneel", "total_home_score", "total_away_score", "passer_player_id", "rusher_player_id"]
    frames = []
    for y in (season - 1, season):
        p = os.path.join(ROOT, "data", "raw", "nflverse", "pbp", f"play_by_play_{y}.parquet")
        if os.path.exists(p):
            frames.append(pl.read_parquet(p, columns=cols))
    by = defaultdict(list)
    if frames:
        for r in pl.concat(frames, how="diagonal_relaxed").iter_rows(named=True):
            by[r["game_id"]].append(r)
    return by


def player_team_map(season: int) -> dict:
    import polars as pl
    p = os.path.join(ROOT, "data", "raw", "nflverse", "weekly_rosters", f"roster_weekly_{season}.parquet")
    if not os.path.exists(p):
        return {}
    t = pl.read_parquet(p, columns=["gsis_id", "team", "week"])
    out = {}
    for r in t.iter_rows(named=True):
        out[(r["gsis_id"], int(r["week"]))] = r["team"]
    return out


def market_by_game(rows, team_of) -> dict:
    mk, qb = defaultdict(dict), defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r.get("horizon") != "latest_pregame":
            continue
        m = mk[r["game_id"]]
        if not m:
            m.update(home_margin=r.get("env_home_margin"), total=r.get("env_total"), home_points=r.get("env_home_points"),
                     away_points=r.get("env_away_points"), favorite=r.get("env_favorite"))
        if r.get("family") == "PLAYER_STAT" and r.get("stat") == "attempts" and r.get("obs_state") == "OBSERVED" and r.get("two_sided") \
                and r.get("player_gsis_id"):
            t = team_of.get((r["player_gsis_id"], r["week"]))
            if t:
                qb[r["game_id"]][(t, r["player_gsis_id"])].append((r.get("rung_value"), r.get("mid")))
    for gid, d in qb.items():
        best = {}
        for (t, p), pts in d.items():
            med = B.median_from_survival(pts)
            if med is not None and (t not in best or len(pts) > best[t][1]):
                best[t] = (med, len(pts))
        mk[gid]["qb_attempts"] = {t: v[0] for t, v in best.items()}
    return mk


def autopsy_totals(can) -> dict:
    c = Counter(a["classification"] for a in can)
    n = len(can)
    meaningful = n - c.get("NO_LARGE_MISS", 0) - c.get("INSUFFICIENT_DATA", 0)
    rules = sorted({str(a.get("evaluation_version")) for a in can})
    return {"n": n, "classifications": dict(c.most_common()), "meaningful": meaningful,
            "share_opp_tv": ((c.get("OPPORTUNITY_MISS", 0) + c.get("TEAM_VOLUME_MISS", 0)) / meaningful) if meaningful else None,
            "share_eff": (c.get("EFFICIENCY_MISS", 0) / meaningful) if meaningful else None, "rule": ", ".join(rules)}


def recurring_failures(links, games) -> list:
    out = []
    mean = [l for l in links if l["miss_layer"] not in (SA.LAYER_NO_MISS, SA.LAYER_INSUFFICIENT)]
    by_stat = defaultdict(Counter)
    for l in mean:
        by_stat[l["stat"]][l["miss_layer"]] += 1
    for stat, c in sorted(by_stat.items(), key=lambda kv: -sum(kv[1].values()))[:6]:
        tot = sum(c.values())
        top, n = c.most_common(1)[0]
        out.append(f"{stat}: {tot} meaningful misses; the most common first-failing layer is {top} ({n}, {100 * n / tot:.0f}%).")
    dir_ = Counter()
    for g in games:
        for t, d in (g.get("teams") or {}).items():
            e = (d.get("volume_vs_expectation") or {}).get("pass_att") or {}
            if e.get("off"):
                dir_[("over" if e["log_ratio"] > 0 else "under", "trailing" if d["final_margin"] < 0 else "leading/tied")] += 1
    for (d, s), n in dir_.most_common(4):
        out.append(f"team pass attempts {d} expectation by > 25% while {s}: {n} team-games.")
    return out


def attention_lines(script_sum, aut, miner, hyps) -> list:
    L = []
    mm = max(1, script_sum["n_meaningful_misses"])
    lay = script_sum["miss_layers"]
    share = lay.get(SA.LAYER_SHARE, 0) + lay.get(SA.LAYER_ROLE, 0)
    nt = max(1, script_sum.get("n_meaningful_excluding_touchdowns") or 0)
    lt = script_sum.get("miss_layers_excluding_touchdowns") or {}
    L.append(f"WHO gets the ball matters more than how many plays there are: {100 * share / mm:.0f}% of meaningful player misses "
             f"were a player's share or an uncertain role with team volume on expectation; {100 * lay.get(SA.LAYER_SCRIPT_VOLUME, 0) / mm:.0f}% "
             f"were team volume a different game script explains. Anytime-TD props drive much of the share figure: without them, "
             f"share + role is {100 * (lt.get(SA.LAYER_SHARE, 0) + lt.get(SA.LAYER_ROLE, 0)) / nt:.0f}% and efficiency "
             f"{100 * lt.get(SA.LAYER_EFFICIENCY, 0) / nt:.0f}%. Check depth-chart, snap and target-share changes before props.")
    L.append(f"Efficiency explains {100 * lay.get(SA.LAYER_EFFICIENCY, 0) / mm:.0f}% of meaningful misses with opportunity on expectation: "
             "a yardage thesis that needs efficiency above the player's norm is the most fragile kind.")
    s01 = [c for c in miner["cells"] if c["slice"] == "S01_side_x_price"]
    loss = [c for c in s01 if c.get("ci") and c["ci"][1] < 0]
    L.append(f"Cost, not mispricing, is the default: buying at the ask lost in {len(loss)} of {len(s01)} side × price bands of the "
             "whole board after fees. A position needs a reason the mid is wrong, not just a view.")
    for h in hyps:
        if h["id"].endswith(("B04", "B11")):
            d = h.get("discovery") or {}
            L.append(f"{h['title']} ({h['id']}) was the strongest information lead in discovery "
                     f"({_fmt(d.get('value'))}, CI {_fmt_ci(d.get('ci'))}); it is under prospective test, not proven.")
    L.append("Treat a stack of positions on one thesis bucket (spread + QB attempts + several passing rungs) as ONE bet in sizing.")
    return L


def _fmt(x):
    return "—" if x is None else f"{x:+.3f}"


def _fmt_ci(ci):
    return "—" if not ci else f"[{ci[0]:+.3f}, {ci[1]:+.3f}]"


DO_NOT_CHANGE = [
    "The market prior. The CURRENT (market-centred) arm beats DATA_ONLY on margin and total MAE over Weeks 1–3; DATA_ONLY is a "
    "research signal and its disagreement only a context feature (three-arm experiment, no verdict before 64 games).",
    "Production model weights, staking limits, bankroll policy and betting authority: nothing in Weeks 1–3 supports a change, "
    "and every pattern here is discovery-only.",
    "The incumbent's price buckets as rules: the 10–20c full-game YES lead is not distinguishable from noise once clustered by "
    "game, and Week 3 showed none of it. It is preregistered (B01), not adopted.",
]


def build_scope(*, title, weeks, rows, cov, hyps_reg, n_under_test, can_all, games_all, links_all, expression_doc, autopsy_cov):
    wset = set(weeks)
    r = [x for x in rows if x.get("week") in wset]
    miner_lp = M.mine(r, horizon="latest_pregame", discovery_weeks=sorted(wset))
    miner_24 = M.mine(r, horizon="T-24h", discovery_weeks=sorted(wset))
    lad = M.ladder_report(r)
    hyps = []
    for row in hyps_reg:
        spec = BH.spec_from_registry(row)
        if not spec:
            continue
        disc = {k: (row.get("generation_evidence") or {}).get(k) for k in ("value", "ci", "n", "n_games", "by_week")}
        future = sorted(w for w in wset if w > BH.GENERATION_WINDOW["week_hi"])
        pr = BH.prospective(spec, rows, future_weeks=future, n_under_test=n_under_test) if future else None
        from nfl_edge.handicap.script_block import tag_for_locator
        hyps.append({"id": row["id"], "title": spec["title"], "metric": spec["metric"], "sign": spec["sign"],
                     "status": row.get("status"), "discovery": disc, "prospective": pr, "tag": tag_for_locator(row.get("locator"))})
    cov_scope = {**cov, "total": _cov_total(cov, wset), "by_week_family": [x for x in cov["by_week_family"] if _wk(x["week"]) in wset]}
    can = [a for a in can_all if a.get("week") in wset]
    games = [g for g in games_all if g.get("week") in wset]
    links = [l for l in links_all if l.get("week") in wset]
    ssum = SA.summarize(games, links)
    inputs = (f"board {B.BOARD_VERSION}, miner {M.MINER_VERSION}, script autopsy {SA.SCRIPT_AUTOPSY_VERSION}, weeks {sorted(wset)}; "
              f"board rows {len(r):,}")
    edge = {"scope_title": title, "inputs": inputs, "coverage": cov_scope, "miner": {"latest_pregame": miner_lp, "T-24h": _strip(miner_24)},
            "ladders": {k: v for k, v in lad.items() if k != "ladders"}, "hypotheses": hyps}
    script = {"scope_title": title, "script_summary": ssum, "games": games, "autopsy_totals": autopsy_totals(can),
              "recurring": recurring_failures(links, games), "autopsy_coverage": {w: c for w, c in autopsy_cov.items() if int(w) in wset}}
    ex = None
    if expression_doc:
        pos = [p for p in expression_doc["positions"] if p.get("week") in wset]
        if pos:
            ex = _expression_scope(expression_doc, pos)
    thesis = {"scope_title": title, "attention": attention_lines(ssum, autopsy_totals(can), miner_lp, hyps),
              "do_not_change": DO_NOT_CHANGE, "hypotheses": hyps, "expression": ex, "limitations": LIMITATIONS}
    return edge, script, thesis, ladder_detail(lad)


def ladder_detail(lad):
    return lad.get("ladders", [])


def _strip(m):
    return {k: v for k, v in m.items() if k != "cells"} | {"cells": [c for c in m["cells"] if c["status"] != "DESCRIPTIVE_ONLY"]}


def _wk(w):
    try:
        return int(w)
    except (TypeError, ValueError):
        return None


def _cov_total(cov, wset):
    tot = Counter()
    ex = Counter()
    for w, v in cov["by_week"].items():
        if _wk(w) in wset:
            tot.update({k: v.get(k, 0) for k in cov["funnel_stages"]})
            ex.update(v.get("exclusions") or {})
    return {**{k: tot.get(k, 0) for k in cov["funnel_stages"]}, "exclusions": dict(ex.most_common())}


def _expression_scope(doc, pos):
    cls = Counter(p["classification"] for p in pos)
    flags = Counter(f for p in pos for f in p["flags"])
    pnl = defaultdict(float)
    for p in pos:
        pnl[p["classification"]] += p.get("total_episode_pnl") or 0.0
    bks = {p["thesis_bucket"] for p in pos if p.get("thesis_bucket")}
    return {"n_positions": len(pos), "n_independent_theses": len(bks), "classifications": dict(cls.most_common()),
            "flags": dict(flags.most_common()), "pnl_by_classification": {k: round(v, 2) for k, v in pnl.items()},
            "buckets": [b for b in doc["buckets"] if b["bucket"] in bks], "caution": doc["caution"]}


def write_scope(out_dir, edge, script, thesis, ladders):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "BOARD_EDGE_DISCOVERY.md"), "w") as f:
        f.write(WR.render_board_edge(edge))
    with open(os.path.join(out_dir, "SCRIPT_AUTOPSY.md"), "w") as f:
        f.write(WR.render_script_autopsy(script))
    with open(os.path.join(out_dir, "THESIS_IMPROVEMENT.md"), "w") as f:
        f.write(WR.render_thesis(thesis))
    # mtime=0: a gzip header otherwise carries the wall clock, and a rebuild of the same evidence must be byte-identical
    payload = json.dumps({"board_edge": edge, "script_autopsy": script, "thesis_improvement": thesis, "ladders": ladders,
                          "betting_authorized": False}, default=str, sort_keys=True).encode()
    with open(os.path.join(out_dir, "research.json.gz"), "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as f:
        f.write(payload)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--season", type=int, default=2026)
    ap.add_argument("--weeks", default="1,2,3")
    ap.add_argument("--board", required=True)
    ap.add_argument("--market-data", default="")
    ap.add_argument("--autopsy-root", action="append", default=[])
    ap.add_argument("--handicap-ref", default="origin/handicap-data")
    ap.add_argument("--repo", default=ROOT)
    ap.add_argument("--registry", default=os.path.join(ROOT, HR.DEFAULT_PATH))
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "research", "weekly", "2026"))
    ap.add_argument("--no-per-week", action="store_true")
    a = ap.parse_args()
    weeks = sorted(int(w) for w in a.weeks.split(",") if w.strip())
    rows = load_board(a.board, weeks)
    cov = json.load(open(os.path.join(a.board, "board_coverage.json")))
    log(f"board rows {len(rows):,}")
    team_of = player_team_map(a.season)
    # autopsies (canonical) + anatomy coverage
    aroots = list(a.autopsy_root) + ([os.path.join(a.market_data, "data", "shadow", "player_autopsy")] if a.market_data else [])
    can_all = [x for x in PA.canonical_autopsies(corpus(aroots, PA.SUFFIX)) if x.get("season") == a.season and x.get("week") in set(weeks)]
    log(f"canonical autopsies {len(can_all):,}")
    # script autopsy
    pbp = pbp_by_game(a.season)
    vols = {g: SA.team_volume_from_pbp(p) for g, p in pbp.items()}
    sched = [{"game_id": g, "season": int(p[0]["season"]), "week": int(p[0]["week"]), "home": p[0]["home_team"], "away": p[0]["away_team"]}
             for g, p in pbp.items() if p]
    games = [s for s in sched if s["season"] == a.season and s["week"] in set(weeks)]
    mk = market_by_game(rows, team_of)
    sim_scripts = {}
    if a.market_data:
        for p in sorted(glob.glob(os.path.join(a.market_data, "data", "shadow", "sim", "*", "*.scripts.json.gz"))):
            try:
                doc = json.load(gzip.open(p, "rt"))
            except (OSError, ValueError):
                continue
            for gid, s in (doc.get("games") or {}).items():
                ko = s.get("kickoff_utc")
                if ko and (s.get("generated_at") or "") < ko:        # the latest pregame script per game
                    if gid not in sim_scripts or s["generated_at"] > sim_scripts[gid]["generated_at"]:
                        sim_scripts[gid] = s
    game_recs = SA.autopsy_games(games=games, pbp_by_game=pbp, volumes_by_game=vols, schedule=sched, market=mk, sim_scripts=sim_scripts)
    links = SA.connect_players(can_all, game_recs)
    # autopsy coverage per week
    from nfl_edge.settlement.results import games_from_schedule_text, load_schedule_text
    text, _ = load_schedule_text(ROOT)
    schedule = [{"game_id": g.game_id, "status": g.status, "week": g.week, "season": g.season} for g in games_from_schedule_text(text, seasons=[a.season])]
    # which games have an anatomy corpus at all (the gate's own test): an undiagnosed game without one was never
    # instrumented (e.g. the season opener predates the anatomy job) -- that is not a pending postgame job
    anat_dir = os.path.join(a.market_data, "data", "shadow", "player_anatomy") if a.market_data else None
    anatomy_games = ({g for g in os.listdir(anat_dir) if os.path.isdir(os.path.join(anat_dir, g))}
                     if anat_dir and os.path.isdir(anat_dir) else None)
    autopsy_cov = {}
    for w in weeks:
        sw = [g for g in schedule if g["week"] == w]
        autopsy_cov[str(w)] = PA.coverage_manifest(sw, None, [x for x in can_all if x.get("week") == w],
                                                   anatomy_games=anatomy_games)
    # expression autopsy of the actual positions
    expression_doc = None
    wag = [w for w in git_json_files(a.handicap_ref, f"data/imported_wagers/{a.season}", a.repo) if w.get("week") in set(weeks)]
    if wag:
        from nfl_edge.handicap import actual_wager_postmortem as AWP, position_lifecycle as PL
        st = {s["source_bet_key"]: s for s in git_json_files(a.handicap_ref, f"data/wager_settlements/{a.season}", a.repo)}
        eps = PL.build_episodes([AWP.wager_row(w, st.get(w["source_bet_key"]), None) for w in wag])
        latest = {r["ticker"]: r for r in rows if r.get("horizon") == "latest_pregame"}
        by_ladder = defaultdict(list)
        for r in latest.values():
            if r.get("ladder_id"):
                by_ladder[r["ladder_id"]].append(r)
        plinks = {(l["game_id"], l["player_id"], l["stat"]): l for l in links}
        pteam = {g: t for (g, w), t in team_of.items()}
        owner = {}
        for w in weeks:
            o, warns = TH.load_owner_file(a.repo, a.season, w)
            owner.update(o)
            for x in warns:
                log(f"thesis: {x}")
        expression_doc = EA.autopsy(eps, board_latest=latest, board_by_ladder=by_ladder, player_links=plinks, player_team=pteam,
                                    thesis_metadata=owner)
        log(f"expression autopsy: {expression_doc['n_positions']} positions, {expression_doc['n_independent_theses']} theses")
    reg = HR.current(a.registry)
    board_h = [r for r in reg.values() if (r.get("locator") or {}).get("kind") == BH.HYPOTHESIS_KIND]
    n_under = len(HR.multiplicity_family(reg)) or 1
    scopes = [] if a.no_per_week else [(f"{a.season} week {w}", [w], f"week_{w:02d}") for w in weeks]
    scopes.append((f"{a.season} weeks {weeks[0]}–{weeks[-1]} (cumulative)", weeks, f"cumulative_wk{weeks[0]:02d}-{weeks[-1]:02d}"))
    for title, ws, name in scopes:
        edge, script, thesis, lad = build_scope(title=title, weeks=ws, rows=rows, cov=cov, hyps_reg=sorted(board_h, key=lambda r: r["id"]),
                                                n_under_test=n_under, can_all=can_all, games_all=game_recs, links_all=links,
                                                expression_doc=expression_doc, autopsy_cov=autopsy_cov)
        write_scope(os.path.join(a.out, name), edge, script, thesis, lad)
        log(f"wrote {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
