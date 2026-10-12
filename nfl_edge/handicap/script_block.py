"""GAME SCRIPT INPUTS for the RUN NFL packet, and HISTORICAL RESEARCH TAGS on its markets. CONTEXT ONLY.

Stdlib-only and read-only, like `sim_block`: the packet path must never import numpy or the research modules.

What it adds to each game, beside everything the packet already shows:

    MARKET BASELINE          the packet's own market-implied spread / total / score, and the game-line moves
    GAME ENVIRONMENT         the simulation's script summary (sim-script-1.x; 1.1.0 adds by_close_result) for the run the packet attached:
                             margin / total quantiles, one-score and blowout probabilities, the centre it used
    TEAM VOLUME              plays, pass attempts, designed rushes, dropbacks per team, and pass rate CONDITIONAL
                             on the final-margin bucket (the simulator's nearest valid proxy for score state)
    PLAYER OPPORTUNITY       targets / carries ranges, shares and an opportunity spread (role uncertainty)
    MODEL / MARKET           the existing largest disagreements, labelled research-only
    RESEARCH TAGS            which preregistered board hypotheses (research/hypothesis_registry/v2) a market
                             falls under right now -- e.g. PRICE_BUCKET_RESEARCH_CANDIDATE

THE TAGS HAVE NO AUTHORITY. They are computed after every other view, read by nothing on the gate, preflight,
risk, stake or evaluation path, and they cannot create a BET state, change an edge, a threshold, a stake or a
model probability (pinned by tests/test_run_nfl_script_context.py). A hypothesis under test is, by definition,
not evidence yet. Fail OPEN: a missing script file or registry yields an explicit UNAVAILABLE section; nothing
the packet already did depends on this module.
"""
from __future__ import annotations

import glob
import gzip
import json
import os

DIRNAME = os.path.join("data", "shadow", "sim")
REGISTRY = os.path.join("research", "hypothesis_registry", "v2", "hypotheses.jsonl")
UNDER_TEST = ("PREREGISTERED", "TESTING")
AUTHORITY = ("CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, "
             "a threshold, a stake or a model probability")

# tag category by the registered metric (and filter) of a board hypothesis
TAG_BY_METRIC = {"MID_BIAS": "PRICE_BUCKET_RESEARCH_CANDIDATE", "RETURN_AT_ASK": "PRICE_BUCKET_RESEARCH_CANDIDATE",
                 "PAIRED_RUNG": "LADDER_RESEARCH_CANDIDATE", "MOVE_TOWARD_MODEL": "DISAGREEMENT_RESEARCH_CANDIDATE",
                 "PAIRED_EXPRESSION": "EXPRESSION_RESEARCH_CANDIDATE", "EXCESS_BRIER_GAP": "ROLE_RESEARCH_CANDIDATE"}


def _f(x):
    try:
        return None if x is None or x == "" else float(x)
    except (TypeError, ValueError):
        return None


# ------------------------------------------------------------------------------------------------ loading
def load_scripts(roots, sim_manifest: dict | None) -> tuple[dict | None, str]:
    """The script summaries written by the SAME simulation run the packet attached (never another run's)."""
    if not sim_manifest or not sim_manifest.get("run_id"):
        return None, "no simulation run attached to this packet"
    run_id = sim_manifest["run_id"]
    for root in roots:
        for path in sorted(glob.glob(os.path.join(root, DIRNAME, "*", f"{run_id}.*.scripts.json.gz"))):
            try:
                with gzip.open(path, "rt") as f:
                    doc = json.load(f)
            except (OSError, ValueError) as e:
                return None, f"script file unreadable: {e}"
            return doc.get("games") or {}, os.path.basename(path)
    return None, f"simulation run {run_id} wrote no script summary (runs before sim-script-1.0.0 did not)"


def load_research_hypotheses(root: str) -> tuple[list, str]:
    """Board hypotheses currently under test (PREREGISTERED / TESTING), from the append-only registry."""
    path = os.path.join(root, REGISTRY)
    if not os.path.exists(path):
        return [], "no hypothesis registry"
    cur = {}
    try:
        with open(path) as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    cur[r["id"]] = r
    except (OSError, ValueError) as e:
        return [], f"registry unreadable: {e}"
    out = [r for r in cur.values() if r.get("status") in UNDER_TEST and (r.get("locator") or {}).get("kind") == "BOARD_CELL"]
    return sorted(out, key=lambda r: r["id"]), f"{len(out)} board hypotheses under test"


# ------------------------------------------------------------------------------------------------ tags
def _side_view(m: dict, side: str) -> dict:
    mid = _f(m.get("mid"))
    ask = _f(m.get("yes_ask") if side == "YES" else m.get("no_ask"))
    side_mid = None if mid is None else (mid if side == "YES" else 1.0 - mid)
    model = _f(m.get("model_probability"))
    return {"family": m.get("family"), "period": m.get("period") or "FULL", "stat": m.get("stat"), "side": side,
            "price": ask, "side_mid": side_mid,
            "player_disagreement": (model - mid) if (model is not None and mid is not None and m.get("family") == "PLAYER_STAT") else None,
            "move": _f((m.get("movement") or {}).get("total_move_since_first_capture"))}


def _match(s: dict, f: dict) -> bool:
    """The registered locator filter, applied to a LIVE quote. Mirrors board_hypotheses._match for the keys a
    packet market can answer; a key the packet cannot answer means no tag (never a guess)."""
    if "horizon" in f and f["horizon"] != "latest_pregame":
        return False
    if "family_in" in f and s["family"] not in f["family_in"]:
        return False
    if "period" in f and s["period"] != f["period"]:
        return False
    if "side" in f and s["side"] != f["side"]:
        return False
    if "stat_in" in f and s["stat"] not in f["stat_in"]:
        return False
    if "mid_lo" in f and (s["side_mid"] is None or not (f["mid_lo"] <= s["side_mid"] < f["mid_hi"])):
        return False
    if "ask_lo" in f and (s["price"] is None or not (f["ask_lo"] <= s["price"] < f["ask_hi"])):
        return False
    if "player_dis_lo" in f and (s["player_disagreement"] is None or not s["player_disagreement"] > f["player_dis_lo"]):
        return False
    if "player_dis_hi" in f and (s["player_disagreement"] is None or not s["player_disagreement"] < f["player_dis_hi"]):
        return False
    if "move_band_in" in f:
        mv = s["move"]
        if mv is None or not ("up>5c" in f["move_band_in"] and mv > 0.05):
            return False
    if any(k in f for k in ("do_abs_lo", "team_implied_lo")):
        return False                       # needs inputs the packet row does not carry: never tagged here
    return True


def tag_for_locator(loc: dict) -> str | None:
    """The research-tag category of a registered board hypothesis (one function for the packet and the reports)."""
    f = (loc or {}).get("filter") or {}
    if "move_band_in" in f:
        return "MOVEMENT_RESEARCH_CANDIDATE"
    if "player_dis_lo" in f or "player_dis_hi" in f:
        return "DISAGREEMENT_RESEARCH_CANDIDATE"
    return TAG_BY_METRIC.get((loc or {}).get("metric"))


def market_tags(m: dict, hypotheses: list) -> list:
    """Research tags for one market row: [{tag, hypothesis, side, title, status}]. Context only."""
    out = []
    for h in hypotheses:
        loc = h.get("locator") or {}
        f = loc.get("filter")
        if not isinstance(f, dict) or not f:
            continue                       # a locator without a filter means nothing; it never tags everything
        tag = tag_for_locator(loc)
        if tag is None or loc.get("metric") in ("PAIRED_RUNG", "PAIRED_EXPRESSION", "EXCESS_BRIER_GAP", "MOVE_TOWARD_MODEL"):
            continue                       # paired / game-level metrics have no single-contract reading
        for side in ("YES", "NO"):
            if _match(_side_view(m, side), f):
                out.append({"tag": tag, "hypothesis": h["id"], "side": side, "title": loc.get("title"),
                            "status": h.get("status"), "direction": h.get("direction"), "authority": "NONE (context only)"})
    return out


# ------------------------------------------------------------------------------------------------ the section
def _rng(d: dict | None, lo="p25", hi="p75", nd=1):
    if not d:
        return None
    return {"mean": round(d.get("mean"), nd) if d.get("mean") is not None else None,
            "range_50": [d.get(lo), d.get(hi)], "range_90": [d.get("p05"), d.get("p95")]}


def game_script_inputs(game: dict, script: dict | None, *, script_source: str, hypotheses_note: str) -> dict:
    """The GAME SCRIPT INPUTS section of one game. Always returns a dict; UNAVAILABLE parts say why."""
    mi = game.get("market_implied") or {}
    line_moves = [m for m in (game.get("largest_moves") or []) if m.get("family") in ("SPREAD", "TOTAL", "TEAM_TOTAL", "GAME_WINNER")][:6]
    out = {"authority": AUTHORITY,
           "hierarchy": "GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION",
           "market_baseline": {"spread_home": mi.get("implied_spread"), "total": mi.get("implied_total_median"),
                               "score": mi.get("implied_score"), "win_probability": mi.get("win_probability"),
                               "game_line_moves": line_moves},
           "script_source": script_source, "research_tags_source": hypotheses_note}
    if not script:
        out["state"] = "PARTIAL"
        out["game_environment"] = out["team_volume"] = out["player_opportunity"] = {"state": "UNAVAILABLE", "reason": script_source}
    else:
        out["state"] = "OK"
        env = script.get("environment") or {}
        out["game_environment"] = {"home_margin": _rng(env.get("home_margin")), "total": _rng(env.get("total")),
                                   "home_points": _rng(env.get("home_points")), "away_points": _rng(env.get("away_points")),
                                   "p_home_win": env.get("p_home_win"), "p_tie": env.get("p_tie"), "p_one_score": env.get("p_one_score"),
                                   "p_blowout_17plus": env.get("p_blowout_17plus"),
                                   "p_total_10_over_centre": env.get("p_total_10_over_centre"),
                                   "p_total_10_under_centre": env.get("p_total_10_under_centre"),
                                   "centre": env.get("centre"), "score_state": env.get("score_state_paths")}
        tv, po = {}, {}
        for team, t in (script.get("teams") or {}).items():
            v = t.get("volume") or {}
            tv[team] = {"plays": _rng(v.get("plays")), "pass_att": _rng(v.get("pass_att")), "designed_rush": _rng(v.get("designed_rush")),
                        "dropbacks": _rng(v.get("dropbacks")), "scrambles": _rng(v.get("scrambles")),
                        "pass_rate": _rng(v.get("pass_rate"), nd=3), "by_final_margin": t.get("by_final_margin"),
                        "by_close_result": t.get("by_close_result"),
                        "target_concentration_hhi": t.get("target_concentration_hhi")}
            po[team] = [{"player": p.get("name") or p.get("player_id"), "position": p.get("position"), "p_active": p.get("p_active"),
                         "targets": _rng(p.get("targets")), "carries": _rng(p.get("carries")),
                         "target_share": (p.get("target_share") or {}).get("mean"), "carry_share": (p.get("carry_share") or {}).get("mean"),
                         "opportunity_cv": p.get("opportunity_cv"),
                         "role_uncertainty": ("HIGH" if (p.get("opportunity_cv") or 0) >= 0.6 or (p.get("p_active") or 1) < 0.8
                                              else "LOW" if (p.get("opportunity_cv") or 1) < 0.35 else "MEDIUM")}
                        for p in (t.get("players") or [])]
        out["team_volume"], out["player_opportunity"] = tv, po
        out["not_simulated"] = script.get("not_simulated")
    out["model_market_disagreement"] = {"research_only": True,
                                        "largest": [{k: d.get(k) for k in ("ticker", "player_name", "stat", "threshold", "mid",
                                                                           "model_probability", "disagreement_vs_mid")}
                                                    for d in (game.get("largest_disagreements") or [])[:5]]}
    tags = {}
    for m in game.get("markets") or []:
        for t in m.get("research_tags") or []:
            k = (t["tag"], t["hypothesis"], t["side"])
            tags.setdefault(k, {"tag": t["tag"], "hypothesis": t["hypothesis"], "side": t["side"], "title": t["title"], "n_markets": 0, "examples": []})
            tags[k]["n_markets"] += 1
            if len(tags[k]["examples"]) < 3:
                tags[k]["examples"].append(m.get("ticker"))
    out["historical_research_tags"] = sorted(tags.values(), key=lambda t: (t["tag"], t["hypothesis"], t["side"]))
    return out


# ------------------------------------------------------------------------------------- GAME SCRIPT V2
V2_AUTHORITY = ("RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred "
                "simulation; they create no BET state and change no edge, threshold, stake or probability")
V2_PROVENANCE_NOTE = ("MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a "
                      "favourite-control share is not a football edge on the side")
V2_MAX_CANDIDATES = 12


def load_scripts_v2(roots, sim_manifest: dict | None) -> tuple[dict | None, str]:
    """GAME SCRIPT V2 documents written by the SAME simulation run the packet attached (never another run's)."""
    if not sim_manifest or not sim_manifest.get("run_id"):
        return None, "no simulation run attached to this packet"
    run_id = sim_manifest["run_id"]
    for root in roots:
        for path in sorted(glob.glob(os.path.join(root, DIRNAME, "*", f"{run_id}.*.scripts_v2.json.gz"))):
            try:
                with gzip.open(path, "rt") as f:
                    doc = json.load(f)
            except (OSError, ValueError) as e:
                return None, f"GAME SCRIPT V2 file unreadable: {e}"
            return doc.get("games") or {}, os.path.basename(path)
    return None, f"simulation run {run_id} wrote no GAME SCRIPT V2 file (runs before it existed did not)"


def _v2_candidates(game: dict, doc: dict) -> list:
    """The markets the view details: the game's ranked reconciled disagreements, then each game line's headline rung."""
    have = {c["ticker"]: c for c in doc.get("contracts") or [] if c.get("p_cash") is not None}
    out = []
    for d in ((game.get("simulation") or {}).get("largest_reconciled_disagreements") or []):
        if d.get("ticker") in have and d["ticker"] not in out:
            out.append(d["ticker"])
    for t in (doc.get("dependency") or {}).get("headline_markets") or []:
        if t in have and have[t].get("family") in ("GAME_WINNER", "SPREAD", "TOTAL", "TEAM_TOTAL") and t not in out:
            out.append(t)
    return out[:V2_MAX_CANDIDATES]


def game_script_v2_view(game: dict, doc: dict | None, *, source: str) -> dict:
    """PRIMARY PLAUSIBLE SCRIPTS, per-candidate MODEL / MARKET, SCRIPT ROBUSTNESS, SCRIPT MATRIX and THESIS
    DEPENDENCY for one game. Numbers only -- no adjective grades a market. Always returns a dict."""
    out = {"authority": V2_AUTHORITY, "provenance": V2_PROVENANCE_NOTE, "source": source}
    if not doc:
        return {**out, "state": "UNAVAILABLE", "reason": source}
    if doc.get("state") != "OK":
        return {**out, "state": doc.get("state") or "UNAVAILABLE", "reason": doc.get("reason") or doc.get("state")}
    s = doc.get("summary") or {}
    cells = s.get("cells") or []
    ranked = sorted(cells, key=lambda c: -(c.get("probability") or 0))
    primary = [{"cell": c["cell"], "label": (c.get("labels") or {}).get("short"), "detail": (c.get("labels") or {}).get("long"),
                "probability": c.get("probability")} for c in ranked[:5]]
    other = 1.0 - sum(p["probability"] or 0 for p in primary)
    labels = {c["cell"]: (c.get("labels") or {}).get("short") for c in cells}
    by_ticker = {m.get("ticker"): m for m in game.get("markets") or []}
    contracts = {c["ticker"]: c for c in doc.get("contracts") or []}
    pairs = (doc.get("dependency") or {}).get("pairs") or []
    cand = []
    for t in _v2_candidates(game, doc):
        c = contracts[t]; m = by_ticker.get(t) or {}; sim = m.get("simulation") or {}
        w = _f(sim.get("reconcile_weight"))
        matrix = [{"cell": cell, "label": labels.get(cell), "p_script": p, "p_cash_given_script": pc}
                  for cell, p, pc in zip(doc.get("cells") or [], doc.get("p_script") or [], c.get("p_cash_given_script") or [])]
        dep = [p for p in pairs if t in (p.get("a"), p.get("b"))][:3]
        cand.append({"ticker": t, "family": c.get("family"), "player_name": c.get("player_name"), "stat": c.get("stat"),
                     "threshold": c.get("threshold") if c.get("threshold") is not None else c.get("floor_strike"),
                     "football_probability": c.get("p_cash"), "market_probability": _f(m.get("mid")),
                     "reconciled_probability": _f(sim.get("p_reconciled")) if (w or 0) > 0 else None,
                     "reconciled_note": None if (w or 0) > 0 else "not validated for this family (deployed weight 0) -- not shown",
                     "script_robustness": c.get("script_robustness"), "major_script_floor": c.get("major_script_floor"),
                     "failure_script_mass": c.get("failure_script_mass"), "win_contribution_hhi": c.get("win_contribution_hhi"),
                     "matrix": matrix,
                     "dependency": [{"with": p["b"] if p["a"] == t else p["a"], "cash_correlation": p.get("cash_correlation"),
                                     "joint_cash": p.get("joint_cash"), "jaccard_winning_rows": p.get("jaccard_winning_rows"),
                                     "shared_failure_mass": p.get("shared_failure_mass")} for p in dep]})
    return {**out, "state": "OK", "primary_scripts": primary, "other_probability": round(other, 4),
            "marginal_events": s.get("marginal_events"), "not_simulated": s.get("not_simulated"),
            "weather": s.get("weather"), "orientation": s.get("orientation"), "centre": s.get("centre"),
            "candidates": cand, "n_contracts_with_matrix": sum(1 for c in contracts.values() if c.get("p_cash") is not None),
            "n_dependency_pairs": (doc.get("dependency") or {}).get("n_pairs_above_threshold", len(pairs)),
            "n_dependency_pairs_listed": len(pairs)}
