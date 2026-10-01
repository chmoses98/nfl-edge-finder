"""PREREGISTERED BOARD HYPOTHESES: the Weeks 1-3 research leads, written as tests a future week can pass or fail.

Weeks 1-3 are the DISCOVERY window. Every hypothesis here was formed from them (or from the owner's Weeks 1-3
review), is registered GENERATED with that window, and is preregistered -- thresholds frozen and hashed, the
evaluation plan written, the first test kickoff named -- before Week 4's first kickoff (2026-10-02T00:15Z,
PIT-CLE). Weeks 1-3 are never used again as evidence for them. A verdict needs the binding future window, the
minimum sample below, and an owner's `transition()`; this module only ever SUGGESTS.

Each hypothesis is DECLARATIVE: a filter over full-board side rows (`board_miner.side_rows`) plus a metric. The
spec is stored verbatim in the registry line (`locator`), so the future evaluation reads exactly what was
registered, and a later edit to this file cannot change what an old hypothesis meant: the evaluator runs the
registered locator, not the current constant.

Metrics (game-clustered bootstrap everywhere; games are the unit):

    MID_BIAS             mean(won - side mid)                       is the market's fair price biased here?
    RETURN_AT_ASK        mean(payout - ask - fee) per contract       is it exploitable after costs?
    MOVE_TOWARD_MODEL    share of moving contracts whose close moved toward DATA_ONLY's side of the T-24h mid
    PAIRED_RUNG          within a ladder: return(alternate rung) - return(main rung), same side
    PAIRED_EXPRESSION    within a game-team: return(TEAM_TOTAL main YES) - return(SPREAD main YES)
    EXCESS_BRIER_GAP     excess Brier of the mid (squared error minus the mid's own variance) LOW minus HIGH role

NO AUTHORITY. Nothing here reaches a gate, a stake, a threshold or RUN NFL's betting path. A SUPPORTED
hypothesis would be the start of a separate, owner-approved promotion project -- never an automatic rule.
"""
from __future__ import annotations

import math
from collections import defaultdict
from statistics import NormalDist

import numpy as np

from nfl_edge.research.board_miner import BOOTSTRAP_B, BOOTSTRAP_SEED, cluster_bootstrap_means, side_rows

HYPOTHESIS_KIND = "BOARD_CELL"
GENERATION_WINDOW = {"season": 2026, "week_lo": 1, "week_hi": 3}
FUTURE_WINDOW = {"season": 2026, "week_lo": 4, "week_hi": 18}
FIRST_TEST_KICKOFF_UTC = "2026-10-02T00:15:00+00:00"       # 2026_04_PIT_CLE
GAME_FAMILIES = ["GAME_WINNER", "SPREAD", "TOTAL", "TEAM_TOTAL", "BOTH_TEAMS_SCORE_N"]
YARDAGE = ["passing_yards", "rushing_yards", "receiving_yards"]

# Frozen evidence bar shared by every board hypothesis (hashed into each preregistration).
THRESHOLDS = {
    "unit": "game (game-clustered bootstrap, B=2000, seed 20261001)",
    "primary_horizon": "latest_pregame",
    "alpha_family": 0.10,
    "multiplicity": "Bonferroni across the board hypotheses under test (the family is Stage B/C only)",
    "min_future_games": 48,
    "min_future_weeks": 3,
    "min_future_contracts": 60,
    "supported_if": "the (1 - alpha_family/m) two-sided game-clustered interval of the metric excludes 0 on the registered side",
    "not_supported_if": "the same interval excludes 0 on the OTHER side, or the minimum sample is met and the point estimate is on the other side",
    "otherwise": "INCONCLUSIVE; keep testing inside the registered window",
    "verdict": "a suggestion only; the owner transitions the registry",
}

# --------------------------------------------------------------------------------------------- the hypotheses
# filter keys: family_in, period, side, mid_lo/mid_hi (side mid), ask_lo/ask_hi, stat_in, move_band_in,
# role_certainty_in, player_disagreement_lo/hi (signed: model cv - mid, YES-side units)
BOARD_HYPOTHESES = [
    {"suffix": "B01", "title": "Full-game longshot YES underpriced at the mid",
     "market_family": "GAME_WINNER|SPREAD|TOTAL|TEAM_TOTAL|BOTH_TEAMS_SCORE_N",
     "condition": "full-game families, YES side, side mid in [0.10, 0.30) at latest pregame",
     "direction": "event rate exceeds the mid (MID_BIAS > 0)",
     "mechanism": "owner lead 1: residual-shaped tails of full-game ladders thinner than realised outcomes",
     "filter": {"family_in": GAME_FAMILIES, "period": "FULL", "side": "YES", "mid_lo": 0.10, "mid_hi": 0.30},
     "metric": "MID_BIAS", "sign": +1},
    {"suffix": "B02", "title": "Full-game YES at 60-70c overpriced at the mid",
     "market_family": "GAME_WINNER|SPREAD|TOTAL|TEAM_TOTAL|BOTH_TEAMS_SCORE_N",
     "condition": "full-game families, YES side, side mid in [0.60, 0.70) at latest pregame",
     "direction": "event rate below the mid (MID_BIAS < 0)",
     "mechanism": "owner lead 2: the mirror of B01 -- the favourite rung of a ladder carries the mass the tails lack",
     "filter": {"family_in": GAME_FAMILIES, "period": "FULL", "side": "YES", "mid_lo": 0.60, "mid_hi": 0.70},
     "metric": "MID_BIAS", "sign": -1},
    {"suffix": "B03", "title": "Sides priced 90c+ lose after fees",
     "market_family": "ALL",
     "condition": "any family, either side, ask in [0.90, 1.00) at latest pregame",
     "direction": "fee-adjusted return at the ask below zero",
     "mechanism": "owner lead 3: at 90c+ the fee and the half-spread exceed what the residual mispricing can pay",
     "filter": {"ask_lo": 0.90, "ask_hi": 1.0},
     "metric": "RETURN_AT_ASK", "sign": -1},
    {"suffix": "B04", "title": "Modest DATA_ONLY disagreement predicts movement toward it",
     "market_family": "GAME_WINNER|SPREAD|TOTAL|TEAM_TOTAL|BOTH_TEAMS_SCORE_N",
     "condition": "full-game families at T-24h with |DATA_ONLY probability - mid| in [2pp, 10pp)",
     "direction": "more contracts move toward DATA_ONLY's side by the close than away (share > 0.5)",
     "mechanism": "owner lead 4: football data carries information the T-24h market has not yet priced",
     "filter": {"family_in": GAME_FAMILIES, "period": "FULL", "horizon": "T-24h", "do_abs_lo": 0.02, "do_abs_hi": 0.10},
     "metric": "MOVE_TOWARD_MODEL", "sign": +1},
    {"suffix": "B05", "title": "Adjacent yardage rungs beat the main rung after fees",
     "market_family": "PLAYER_STAT",
     "condition": "player yardage ladders at latest pregame; YES side; rung adjacent to the main rung vs the main rung of the same ladder",
     "direction": "return(adjacent) - return(main) > 0",
     "mechanism": "owner lead 5: headline rungs attract the flow and the tighter pricing; neighbours may be priced lazily",
     "filter": {"stat_in": YARDAGE, "side": "YES"},
     "metric": "PAIRED_RUNG", "sign": +1},
    {"suffix": "B06", "title": "Team total beats spread as the expression of an offensive thesis",
     "market_family": "TEAM_TOTAL|SPREAD",
     "condition": "teams with market-implied points >= 24 at latest pregame: main TEAM_TOTAL YES vs main SPREAD YES of the same team",
     "direction": "return(team total) - return(spread) > 0",
     "mechanism": "owner lead 6 (LAR-DEN, LV-NO): an offence thesis does not need the opponent to be stopped; a spread does",
     "filter": {"team_implied_lo": 24.0},
     "metric": "PAIRED_EXPRESSION", "sign": +1},
    {"suffix": "B07", "title": "Uncertain roles are priced worse than certain roles",
     "market_family": "PLAYER_STAT",
     "condition": "player props at latest pregame with an incumbent projection; role certainty LOW vs HIGH (p_plays / usage-history proxy)",
     "direction": "excess Brier of the mid for LOW exceeds HIGH (gap > 0)",
     "mechanism": "owner lead 7 and the autopsy: 64% of meaningful projection misses are opportunity / team volume",
     "filter": {"family_in": ["PLAYER_STAT"], "side": "YES"},
     "metric": "EXCESS_BRIER_GAP", "sign": +1},
    {"suffix": "B08", "title": "Player-prop NO at 80c+ loses after fees",
     "market_family": "PLAYER_STAT",
     "condition": "player props, NO side, ask in [0.80, 1.00) at latest pregame",
     "direction": "fee-adjusted return at the ask below zero",
     "mechanism": "discovery: S02 PLAYER_STAT NO 80-90c -4.8c and 90-100c -2.2c per contract, negative in all three weeks",
     "filter": {"family_in": ["PLAYER_STAT"], "side": "NO", "ask_lo": 0.80, "ask_hi": 1.0},
     "metric": "RETURN_AT_ASK", "sign": -1},
    {"suffix": "B09", "title": "Player-prop YES longshots lose after fees",
     "market_family": "PLAYER_STAT",
     "condition": "player props, YES side, ask in (0, 0.10) at latest pregame",
     "direction": "fee-adjusted return at the ask below zero",
     "mechanism": "discovery: S02 PLAYER_STAT YES 0-10c -1.4c per contract, negative in all three weeks (longshot premium)",
     "filter": {"family_in": ["PLAYER_STAT"], "side": "YES", "ask_lo": 0.0, "ask_hi": 0.10},
     "metric": "RETURN_AT_ASK", "sign": -1},
    {"suffix": "B10", "title": "Chasing a pregame move loses",
     "market_family": "ALL",
     "condition": "contracts whose mid rose more than 5c from T-24h to latest pregame, YES side, ask in [0.10, 0.50)",
     "direction": "fee-adjusted return at the ask below zero",
     "mechanism": "discovery: S14 up>5c YES 10-50c lost 8-17c per contract in every week; late steam is already in the price",
     "filter": {"move_band_in": ["up>5c"], "side": "YES", "ask_lo": 0.10, "ask_hi": 0.50},
     "metric": "RETURN_AT_ASK", "sign": -1},
    {"suffix": "B11", "title": "A large incumbent player-model OVER view marks an underpriced YES",
     "market_family": "PLAYER_STAT",
     "condition": "player props at latest pregame, YES side, incumbent model contract value above the mid by more than 10pp",
     "direction": "event rate exceeds the mid (MID_BIAS > 0)",
     "mechanism": "research-only model disagreement as information: does the incumbent's over view carry anything the "
                  "market lacks? (discovery: QB attempts / completions rungs with the model >10pp over saw YES hit far "
                  "above the NO side's price)",
     "filter": {"family_in": ["PLAYER_STAT"], "side": "YES", "player_dis_lo": 0.10},
     "metric": "MID_BIAS", "sign": +1},
]


# --------------------------------------------------------------------------------------------- evaluation
def _match(s: dict, f: dict) -> bool:
    if "family_in" in f and s.get("family") not in f["family_in"]:
        return False
    if "period" in f and (s.get("period") or "FULL") != f["period"]:
        return False
    if "side" in f and s.get("side") != f["side"]:
        return False
    if "stat_in" in f and s.get("stat") not in f["stat_in"]:
        return False
    if "move_band_in" in f and s.get("move_band") not in f["move_band_in"]:
        return False
    sm = s.get("side_mid")
    if "mid_lo" in f and (sm is None or not (f["mid_lo"] <= sm < f["mid_hi"])):
        return False
    if "ask_lo" in f and not (f["ask_lo"] <= s["price"] < f["ask_hi"]):
        return False
    if "player_dis_hi" in f:
        d = s.get("player_disagreement")
        if d is None or not d < f["player_dis_hi"]:
            return False
    if "player_dis_lo" in f:
        d = s.get("player_disagreement")
        if d is None or not d > f["player_dis_lo"]:
            return False
    return True


def _boot(values, clusters, alpha=0.05):
    """Mean and a game-clustered (1 - alpha) interval."""
    if not values:
        return {"value": None, "ci": None, "n": 0, "n_games": 0}
    bs = cluster_bootstrap_means(values, [1.0] * len(values), clusters)
    v = float(np.mean(values))
    out = {"value": v, "n": len(values), "n_games": len(set(clusters))}
    if bs is None:
        out["ci"] = None
        return out
    # recompute quantiles at the requested level from the same replicate distribution
    vals, cl = np.asarray(values, float), np.asarray(clusters)
    ids, inv = np.unique(cl, return_inverse=True)
    G = len(ids)
    sv = np.bincount(inv, weights=vals, minlength=G)
    sn = np.bincount(inv, minlength=G).astype(float)
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    W = rng.multinomial(G, np.full(G, 1.0 / G), size=BOOTSTRAP_B).astype(float)
    tn = W @ sn
    m = (W @ sv)[tn > 0] / tn[tn > 0]
    out["ci"] = [float(np.quantile(m, alpha / 2)), float(np.quantile(m, 1 - alpha / 2))]
    out["se"] = float(m.std(ddof=1))
    return out


def evaluate(spec: dict, rows: list, *, weeks=None, alpha: float = 0.05) -> dict:
    """The metric of one hypothesis over full-board rows (all horizons), restricted to `weeks`."""
    wk = set(weeks) if weeks else None
    rows = [r for r in rows if wk is None or r.get("week") in wk]
    f, metric = spec["filter"], spec["metric"]
    hz = f.get("horizon", "latest_pregame")
    at_h = [r for r in rows if r.get("horizon") == hz and r.get("analysis_state") == "ANALYZED"]
    vals, cl, wks = [], [], []
    if metric in ("MID_BIAS", "RETURN_AT_ASK"):
        for s in side_rows(at_h):
            if not _match(s, f):
                continue
            if metric == "MID_BIAS":
                if s.get("side_mid") is None:
                    continue
                vals.append(s["won"] - s["side_mid"])
            else:
                vals.append(s["ret"])
            cl.append(s["game_id"]); wks.append(s["week"])
    elif metric == "MOVE_TOWARD_MODEL":
        for r in at_h:
            if r.get("family") not in f["family_in"] or (r.get("period") or "FULL") != f["period"]:
                continue
            d, mid, cm = r.get("data_only_disagreement"), r.get("mid"), r.get("close_mid")
            if d is None or mid is None or cm is None or not (f["do_abs_lo"] <= abs(d) < f["do_abs_hi"]):
                continue
            mv = cm - mid
            if abs(mv) < 0.005:
                continue                                  # no move: neither toward nor away
            vals.append(1.0 if (mv > 0) == (d > 0) else 0.0)
            cl.append(r["game_id"]); wks.append(r["week"])
        out = _boot([v - 0.5 for v in vals], cl, alpha)
        out["share_toward"] = (out["value"] + 0.5) if out["value"] is not None else None
        return _finish(out, wks, vals=[v - 0.5 for v in vals], clusters=cl, weeks_all=wks)
    elif metric == "PAIRED_RUNG":
        lad = defaultdict(dict)
        for r in at_h:
            if r.get("family") != "PLAYER_STAT" or r.get("stat") not in f["stat_in"] or r.get("return_yes") is None:
                continue
            off = r.get("rung_offset")
            if off == 0:
                lad[r["ladder_id"]]["main"] = r
            elif off in (-1, 1):
                lad[r["ladder_id"]].setdefault("adj", []).append(r)
        for lid, d in lad.items():
            if "main" not in d or not d.get("adj"):
                continue
            adj = sum(a["return_yes"] for a in d["adj"]) / len(d["adj"])
            vals.append(adj - d["main"]["return_yes"])
            cl.append(d["main"]["game_id"]); wks.append(d["main"]["week"])
    elif metric == "PAIRED_EXPRESSION":
        pairs = defaultdict(dict)
        for r in at_h:
            if not r.get("is_main_rung") or (r.get("period") or "FULL") != "FULL" or r.get("return_yes") is None:
                continue
            tip = r.get("team_implied_points")
            if tip is None or tip < f["team_implied_lo"] or r.get("family") not in ("TEAM_TOTAL", "SPREAD"):
                continue
            pairs[(r["game_id"], r.get("team"))][r["family"]] = r
        for (gid, team), d in pairs.items():
            if "TEAM_TOTAL" in d and "SPREAD" in d:
                vals.append(d["TEAM_TOTAL"]["return_yes"] - d["SPREAD"]["return_yes"])
                cl.append(gid); wks.append(d["SPREAD"]["week"])
    elif metric == "EXCESS_BRIER_GAP":
        lo, hi = [], []
        for r in at_h:
            if r.get("family") != "PLAYER_STAT" or r.get("mid") is None or r.get("settled_yes") is None:
                continue
            m, y = r["mid"], r["settled_yes"]
            x = (y - m) ** 2 - m * (1 - m)
            if r.get("role_certainty") == "LOW":
                lo.append((x, r["game_id"], r["week"]))
            elif r.get("role_certainty") == "HIGH":
                hi.append((x, r["game_id"], r["week"]))
        if lo and hi:
            # per game: mean LOW excess minus mean HIGH excess, for games holding both (a paired, game-level gap)
            gl, gh = defaultdict(list), defaultdict(list)
            gw = {}
            for x, g, w in lo:
                gl[g].append(x); gw[g] = w
            for x, g, w in hi:
                gh[g].append(x); gw[g] = w
            for g in sorted(set(gl) & set(gh)):
                vals.append(sum(gl[g]) / len(gl[g]) - sum(gh[g]) / len(gh[g]))
                cl.append(g); wks.append(gw[g])
    out = _boot(vals, cl, alpha)
    return _finish(out, wks, vals=vals, clusters=cl, weeks_all=wks)


def _finish(out, wks, *, vals, clusters, weeks_all):
    byw = defaultdict(list)
    for v, w in zip(vals, weeks_all):
        byw[w].append(v)
    out["n_weeks"] = len(byw)
    out["by_week"] = {str(w): {"n": len(v), "value": sum(v) / len(v)} for w, v in sorted(byw.items())}
    return out


def suggest(spec: dict, ev: dict, *, n_under_test: int, thresholds: dict = THRESHOLDS) -> dict:
    """SUGGESTED status for future evidence. Writes nothing; the owner decides."""
    alpha = thresholds["alpha_family"] / max(1, n_under_test)
    sign = spec["sign"]
    enough = (ev.get("n_games", 0) >= thresholds["min_future_games"] and ev.get("n_weeks", 0) >= thresholds["min_future_weeks"]
              and ev.get("n", 0) >= thresholds["min_future_contracts"])
    ci = ev.get("ci_family")
    v = ev.get("value")
    if not enough or ci is None or v is None:
        status = "INCONCLUSIVE"
        why = "minimum future sample not reached" if not enough else "no estimate"
    elif (ci[0] > 0 and sign > 0) or (ci[1] < 0 and sign < 0):
        status, why = "SUPPORTED", f"family-adjusted interval excludes 0 on the registered side (alpha {alpha:.4f})"
    elif (ci[0] > 0 and sign < 0) or (ci[1] < 0 and sign > 0) or (v * sign < 0):
        status, why = "NOT_SUPPORTED", "interval or point estimate on the other side"
    else:
        status, why = "INCONCLUSIVE", "interval includes 0"
    return {"suggested_status": status, "reason": why, "alpha_per_test": alpha, "enough_sample": enough,
            "suggestion_only": "owner approval required; nothing here changes a model, gate, stake or authority"}


def prospective(spec: dict, rows: list, *, future_weeks, n_under_test: int) -> dict:
    """Future-window evaluation of one registered hypothesis (weeks after the generation window only)."""
    gen_hi = GENERATION_WINDOW["week_hi"]
    weeks = sorted(w for w in future_weeks if w > gen_hi)
    if not weeks:
        return {"weeks": [], "evaluation": None, "suggestion": {"suggested_status": "INCONCLUSIVE", "reason": "no future week yet"}}
    alpha = THRESHOLDS["alpha_family"] / max(1, n_under_test)
    ev = evaluate(spec, rows, weeks=weeks)
    evf = evaluate(spec, rows, weeks=weeks, alpha=alpha)
    ev["ci_family"] = evf.get("ci")
    return {"weeks": weeks, "evaluation": ev, "suggestion": suggest(spec, ev, n_under_test=n_under_test)}


def hypothesis_id(spec: dict) -> str:
    return f"H-20261001-{spec['suffix']}"


def locator(spec: dict) -> dict:
    return {"kind": HYPOTHESIS_KIND, "filter": spec["filter"], "metric": spec["metric"], "sign": spec["sign"],
            "title": spec["title"], "evaluator": "nfl_edge.research.board_hypotheses.evaluate"}


def spec_from_registry(row: dict) -> dict | None:
    """The spec a REGISTERED hypothesis means: its own locator, never the current constant."""
    loc = row.get("locator") or {}
    if loc.get("kind") != HYPOTHESIS_KIND:
        return None
    return {"suffix": row["id"].rsplit("-", 1)[-1], "title": loc.get("title"), "filter": loc["filter"],
            "metric": loc["metric"], "sign": loc["sign"]}
