"""CONDITIONAL BOARD-EDGE MINER: planned conditional pricing questions over the full-board table, with the
safeguards that keep thousands of correlated contracts from passing for evidence. RESEARCH ONLY.

What it is not. It does not search every interaction and rank by historical ROI. The questions are the PLANNED
SLICES below -- written down here, in code, before any number is computed, and the same for every week -- and
every cell of every slice is reported, including the ones that came out flat or negative. A cell can earn at
most CANDIDATE here, which means "worth a preregistered prospective test", never "bet it".

The unit of evidence. A Kalshi contract is a SIDE (YES or NO) bought at its executable ask. Every contract of a
game shares that game's script, every rung of a ladder shares one outcome, and every horizon of a contract is
the same contract, so:

  * games are the clustering unit: every interval is a game-clustered bootstrap (resample games, keep each
    game's contracts together), never a binomial over contracts;
  * each cell reports contracts AND distinct games, weeks and ladders, side by side;
  * one horizon per run of the miner (the primary is latest_pregame); horizons are never pooled;
  * week stability is a requirement, not a footnote: the mean by week, and the cell re-estimated with each
    week held out;
  * small cells are DESCRIPTIVE_ONLY and carry no label beyond that;
  * multiplicity: Benjamini-Hochberg over every non-descriptive cell of the whole family, and the count of
    cells the family would flag by chance alone is printed beside the count it did flag;
  * a binomial floor for rare outcomes: with fewer than 5 events (or non-events) the interval is never
    narrower than a Wilson interval with one effective observation per game (a cell that never paid out is not
    thereby certain);
  * shrinkage: each cell's mean return is shrunk toward zero by the empirical-Bayes ratio tau^2/(tau^2+se^2),
    tau^2 estimated across the slice's cells by the method of moments (zero when the spread is all noise).

Statuses (discovery only): DESCRIPTIVE_ONLY | NO_SIGNAL | UNSTABLE | NOT_SIGNIFICANT_AFTER_MULTIPLICITY |
CANDIDATE. PREREGISTERED / PROSPECTIVE_TESTING / SUPPORTED / REJECTED exist only in the hypothesis registry,
reached through `hypothesis_registry_v2.preregister` and an owner's verdict on future weeks.
"""
from __future__ import annotations

import math
from collections import Counter, defaultdict
from statistics import NormalDist

import numpy as np

from nfl_edge.research.board import price_band

MINER_VERSION = "board-miner-1.0.0"

# Evidence floors. Named once; a change is a visible edit to the rules, never a tuning.
MIN_GAMES = 20                 # distinct games behind a cell before it is more than descriptive
MIN_WEEKS = 2                  # distinct weeks
MIN_CONTRACTS = 40             # contract-sides
BOOTSTRAP_B = 2000
BOOTSTRAP_SEED = 20261001
BH_Q = 0.20                    # false-discovery rate for CANDIDATE across the family
RARE_EVENTS = 5                # below this many events (or non-events) the binomial floor also bounds the interval
CI_LEVEL = 0.95

DESCRIPTIVE_ONLY = "DESCRIPTIVE_ONLY"
NO_SIGNAL = "NO_SIGNAL"
UNSTABLE = "UNSTABLE"
NOT_SIG_MULT = "NOT_SIGNIFICANT_AFTER_MULTIPLICITY"
CANDIDATE = "CANDIDATE"

GAME_FAMILY_SET = ("GAME_WINNER", "SPREAD", "TOTAL", "TEAM_TOTAL", "BOTH_TEAMS_SCORE_N")

# ---------------------------------------------------------------------------------------------- planned slices
# (slice id, dimensions, row filter description, filter). Dimensions are fields of the side row (below).
def _is_player(r):
    return r["family"] == "PLAYER_STAT"


def _is_game_family(r):
    return r["family"] in GAME_FAMILY_SET and r["period"] == "FULL"


PLANNED_SLICES = (
    ("S01_side_x_price", ("side", "price_band"), "every analysed contract-side", None),
    ("S02_family_x_side_x_price", ("family", "side", "price_band"), "every analysed contract-side", None),
    ("S03_family_x_side_x_rung", ("family", "side", "rung_offset_band"), "contracts on a ladder with a main rung", lambda r: r["rung_offset_band"] != "unknown"),
    ("S04_rung_x_price_x_side", ("rung_offset_band", "price_band", "side"), "contracts on a ladder with a main rung", lambda r: r["rung_offset_band"] != "unknown"),
    ("S05_family_x_side_x_total_env", ("family", "side", "env_total_band"), "full-game environment known", lambda r: r["env_total_band"] != "unknown"),
    ("S06_teamtotal_x_role_x_side", ("team_role", "side", "price_band"), "TEAM_TOTAL, team favourite/underdog known", lambda r: r["family"] == "TEAM_TOTAL" and r["team_role"] in ("FAVORITE", "UNDERDOG")),
    ("S07_spread_x_magnitude_x_role", ("env_spread_band", "team_role", "side"), "SPREAD, full game", lambda r: r["family"] == "SPREAD" and r["period"] == "FULL" and r["team_role"] in ("FAVORITE", "UNDERDOG")),
    ("S08_player_stat_x_side_x_price", ("stat", "side", "price_band"), "player props", _is_player),
    ("S09_player_stat_x_role_certainty", ("stat", "role_certainty", "side"), "player props with an incumbent projection", lambda r: _is_player(r) and r["role_certainty"] not in ("UNKNOWN", "n/a")),
    ("S10_player_stat_x_total_env", ("stat", "env_total_band", "side"), "player props, game environment known (script proxy)", lambda r: _is_player(r) and r["env_total_band"] != "unknown"),
    ("S11_player_position_x_stat", ("position", "stat", "side"), "player props with a resolved position", lambda r: _is_player(r) and r["position"]),
    ("S12_price_x_data_only_disagreement", ("data_only_disagreement_band", "side", "price_band"), "game families with a DATA_ONLY reading", lambda r: _is_game_family(r) and r["data_only_disagreement_band"] != "unknown"),
    ("S13_player_disagreement_x_side", ("stat", "player_disagreement_band", "side"), "player props with an incumbent projection", lambda r: _is_player(r) and r["player_disagreement_band"] != "unknown"),
    ("S14_move_x_side_x_price", ("move_band", "side", "price_band"), "contracts with a T-24h mid (movement since T-24h)", lambda r: r["move_band"] != "unknown"),
    ("S15_availability_x_side", ("availability_state", "stat", "side"), "player props with an availability state", lambda r: _is_player(r) and r["availability_state"]),
    ("S16_period_family_x_side_x_price", ("subfamily", "side", "price_band"), "period / derivative game markets", lambda r: r["period"] != "FULL" or r["family"] not in GAME_FAMILY_SET + ("PLAYER_STAT",)),
    # The owner's Weeks 1-3 leads were stated in QUOTED PROBABILITY (the mid), not in the ask paid; binning by
    # the ask moves a 14.7c-mid contract into the 20c band. These two slices state the leads in their own terms.
    ("S17_game_family_x_side_x_mid", ("side", "mid_band"), "five full-game families (the arm-evaluated set)", _is_game_family),
    ("S18_family_x_side_x_mid", ("family", "side", "mid_band"), "every analysed contract-side", None),
)


# ---------------------------------------------------------------------------------------------- side rows
def side_rows(rows):
    """One row per (contract, side) with an executable ask: the side's price, fee, payout, return and CLV."""
    for r in rows:
        y = r.get("settled_yes")
        if y is None:
            continue
        for side in ("YES", "NO"):
            ask = r.get("yes_ask") if side == "YES" else r.get("no_ask")
            fee = r.get("fee_yes") if side == "YES" else r.get("fee_no")
            ret = r.get("return_yes") if side == "YES" else r.get("return_no")
            if ask is None or not (0.0 < ask < 1.0) or fee is None or ret is None:
                continue
            won = float(y) if side == "YES" else 1.0 - float(y)
            mid = r.get("mid")
            side_mid = None if mid is None else (float(mid) if side == "YES" else 1.0 - float(mid))
            yield {**{k: r.get(k) for k in ("season", "week", "game_id", "ticker", "family", "period", "stat", "subfamily",
                                            "position", "env_spread_band", "env_total_band", "team_role", "role_certainty",
                                            "availability_state", "data_only_disagreement_band", "player_disagreement_band",
                                            "move_band", "rung_offset_band", "ladder_id", "horizon")},
                   "player_disagreement": r.get("player_disagreement"),
                   "side": side, "price": float(ask), "fee": float(fee), "won": won, "ret": float(ret),
                   "price_band": price_band(ask), "clv": r.get("clv_yes") if side == "YES" else r.get("clv_no"),
                   "side_mid": side_mid, "mid_band": price_band(side_mid)}


# ---------------------------------------------------------------------------------------------- statistics
def cluster_bootstrap_means(values, prices, clusters, *, B=BOOTSTRAP_B, seed=BOOTSTRAP_SEED):
    """Game-clustered bootstrap of (mean return, ROI). Each replicate draws games with replacement and keeps
    every contract of a drawn game. Vectorised: per-game sums times a multinomial weight matrix."""
    v, p, c = np.asarray(values, float), np.asarray(prices, float), np.asarray(clusters)
    ids, inv = np.unique(c, return_inverse=True)
    G = len(ids)
    sv = np.bincount(inv, weights=v, minlength=G)
    sp = np.bincount(inv, weights=p, minlength=G)
    sn = np.bincount(inv, minlength=G).astype(float)
    if G < 2:
        return None
    rng = np.random.default_rng(seed)
    W = rng.multinomial(G, np.full(G, 1.0 / G), size=B).astype(float)
    tot_n, tot_v, tot_p = W @ sn, W @ sv, W @ sp
    ok = tot_n > 0
    mean = tot_v[ok] / tot_n[ok]
    roi = tot_v[ok] / tot_p[ok]
    lo, hi = (1 - CI_LEVEL) / 2, 1 - (1 - CI_LEVEL) / 2
    return {"se": float(mean.std(ddof=1)), "ci": [float(np.quantile(mean, lo)), float(np.quantile(mean, hi))],
            "roi_ci": [float(np.quantile(roi, lo)), float(np.quantile(roi, hi))], "B": B, "seed": seed, "unit": "game"}


def wilson(k, n, z=1.959963984540054):
    if n <= 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [c - h, c + h]


def bh_qvalues(pvals: list) -> list:
    """Benjamini-Hochberg q-values (monotone), in input order."""
    m = len(pvals)
    if not m:
        return []
    order = sorted(range(m), key=lambda i: pvals[i])
    q = [0.0] * m
    prev = 1.0
    for rank in range(m, 0, -1):
        i = order[rank - 1]
        prev = min(prev, pvals[i] * m / rank)
        q[i] = prev
    return q


def cell_stats(rows: list) -> dict:
    n = len(rows)
    games = [r["game_id"] for r in rows]
    weeks = sorted({r["week"] for r in rows})
    ret = [r["ret"] for r in rows]
    price = [r["price"] + r["fee"] for r in rows]
    won = sum(r["won"] for r in rows)
    mean_price = sum(r["price"] for r in rows) / n
    out = {"n_contracts": n, "n_games": len(set(games)), "n_weeks": len(weeks), "weeks": weeks,
           "n_ladders": len({r["ladder_id"] for r in rows if r.get("ladder_id")}),
           "mean_price": mean_price, "mean_fee": sum(r["fee"] for r in rows) / n,
           "event_rate": won / n, "calibration_diff": won / n - mean_price,
           "mean_return": sum(ret) / n, "roi": sum(ret) / sum(price) if sum(price) > 0 else None,
           "event_rate_wilson_naive": wilson(won, n)}
    clv = [r["clv"] for r in rows if r.get("clv") is not None]
    out["mean_clv"] = (sum(clv) / len(clv)) if clv else None
    out["n_clv"] = len(clv)
    byw = defaultdict(list)
    for r in rows:
        byw[r["week"]].append(r)
    out["by_week"] = {str(w): {"n": len(v), "n_games": len({x["game_id"] for x in v}), "mean_return": sum(x["ret"] for x in v) / len(v),
                               "event_rate": sum(x["won"] for x in v) / len(v), "mean_price": sum(x["price"] for x in v) / len(v)}
                      for w, v in sorted(byw.items())}
    out["leave_one_week_out"] = {str(w): (sum(x["ret"] for x in rows if x["week"] != w) / max(1, sum(1 for x in rows if x["week"] != w)))
                                 for w in weeks} if len(weeks) > 1 else {}
    bs = cluster_bootstrap_means(ret, price, games)
    out["bootstrap"] = bs
    # BINOMIAL FLOOR. Resampling games cannot reveal uncertainty that the sample never shows: a cell whose
    # contracts all lost (0 of 62 interceptions at 7c) has bootstrap returns that differ only by price, and a
    # razor-thin interval around -7c. The event rate is still uncertain, so the return interval is also cut from
    # a Wilson interval on the event rate with ONE effective observation per distinct game (the most
    # conservative design effect) minus the mean cost, and the WIDER of the two intervals is the cell's.
    g = out["n_games"]
    k = won
    rare = k < RARE_EVENTS or (n - k) < RARE_EVENTS
    wb = wilson(out["event_rate"] * g, g) if rare else None
    cost = sum(r["price"] + r["fee"] for r in rows) / n
    out["binomial_floor_applied"] = bool(rare)
    out["binomial_floor_ci"] = [wb[0] - cost, wb[1] - cost] if wb else None
    if bs:
        lo, hi = bs["ci"]
        if wb:
            lo, hi = min(lo, wb[0] - cost), max(hi, wb[1] - cost)
        out["ci"] = [lo, hi]
        # a symmetric normal reading of the combined interval for the multiplicity step
        se = max(bs["se"], (hi - lo) / (2 * 1.959963984540054))
        out["se_combined"] = se
        z = out["mean_return"] / se if se > 0 else None
        out["z_cluster"] = z
        out["p_cluster"] = (2 * (1 - NormalDist().cdf(abs(z)))) if z is not None else None
    else:
        out["ci"] = None
        out["z_cluster"] = out["p_cluster"] = None
    # MID BIAS: is the market's own fair price wrong here, cost aside? event rate minus the side's mid, with the
    # same game-clustered bootstrap. A cell can lose at the ask (spread + fee) with no mid bias at all -- that is
    # COST, not mispricing -- and the two readings are reported side by side so they are never confused.
    mm = [(r["won"] - r["side_mid"], r["game_id"]) for r in rows if r.get("side_mid") is not None]
    if len(mm) >= 2:
        vals, gl = [m[0] for m in mm], [m[1] for m in mm]
        bm = cluster_bootstrap_means(vals, [1.0] * len(vals), gl)
        out["mid_bias"] = sum(vals) / len(vals)
        out["mid_bias_ci"] = bm["ci"] if bm else None
        out["mean_side_mid"] = sum(r["side_mid"] for r in rows if r.get("side_mid") is not None) / len(mm)
        out["half_spread_plus_fee"] = (sum(r["price"] + r["fee"] for r in rows if r.get("side_mid") is not None) / len(mm)) - out["mean_side_mid"]
    else:
        out["mid_bias"] = out["mid_bias_ci"] = out["mean_side_mid"] = out["half_spread_plus_fee"] = None
    ci = out.get("mid_bias_ci")
    out["mid_bias_reading"] = ("NO_MID_DATA" if ci is None else "MID_UNDERPRICES_SIDE" if ci[0] > 0 else
                               "MID_OVERPRICES_SIDE" if ci[1] < 0 else "MID_CALIBRATED_WITHIN_NOISE")
    return out


def label(cell: dict) -> str:
    if cell["n_games"] < MIN_GAMES or cell["n_weeks"] < MIN_WEEKS or cell["n_contracts"] < MIN_CONTRACTS or cell.get("p_cluster") is None \
            or cell.get("ci") is None:
        return DESCRIPTIVE_ONLY
    lo, hi = cell["ci"]
    if lo <= 0 <= hi:
        return NO_SIGNAL
    sign = 1 if cell["mean_return"] > 0 else -1
    if any((wk["mean_return"] > 0) != (sign > 0) for wk in cell["by_week"].values()) or \
            any((v > 0) != (sign > 0) for v in cell["leave_one_week_out"].values()):
        return UNSTABLE
    if cell.get("q_bh") is None or cell["q_bh"] > BH_Q:
        return NOT_SIG_MULT
    return CANDIDATE


def shrink(cells: list):
    """Empirical-Bayes shrinkage of mean return toward 0 within one slice (method-of-moments tau^2)."""
    usable = [c for c in cells if c.get("se_combined")]
    if len(usable) < 3:
        for c in cells:
            c["shrunk_mean_return"] = None
        return
    m2 = sum(c["mean_return"] ** 2 for c in usable) / len(usable)
    s2 = sum(c["se_combined"] ** 2 for c in usable) / len(usable)
    tau2 = max(0.0, m2 - s2)
    for c in cells:
        if c.get("se_combined"):
            se2 = c["se_combined"] ** 2
            c["shrunk_mean_return"] = c["mean_return"] * (tau2 / (tau2 + se2)) if (tau2 + se2) > 0 else 0.0
        else:
            c["shrunk_mean_return"] = None
    for c in cells:
        c["slice_tau2"] = tau2


# ---------------------------------------------------------------------------------------------- the miner
def mine(rows, *, horizon: str, discovery_weeks) -> dict:
    """Every planned slice over the analysed rows of one horizon. Returns every cell, labelled."""
    sides = [s for s in side_rows(r for r in rows if r.get("horizon") == horizon and r.get("analysis_state") == "ANALYZED")]
    slices = []
    all_cells = []
    for sid, dims, scope, flt in PLANNED_SLICES:
        sub = [s for s in sides if flt is None or flt(s)]
        groups = defaultdict(list)
        for s in sub:
            groups[tuple(str(s.get(d)) for d in dims)].append(s)
        cells = []
        for key in sorted(groups):
            st = cell_stats(groups[key])
            st.update({"slice": sid, "dims": dict(zip(dims, key)), "cell_id": f"{sid}|" + "|".join(f"{d}={v}" for d, v in zip(dims, key))})
            cells.append(st)
        shrink(cells)
        slices.append({"slice": sid, "dims": list(dims), "scope": scope, "n_side_rows": len(sub), "n_cells": len(cells)})
        all_cells.extend(cells)
    tested = [c for c in all_cells if not (c["n_games"] < MIN_GAMES or c["n_weeks"] < MIN_WEEKS or c["n_contracts"] < MIN_CONTRACTS)
              and c.get("p_cluster") is not None]
    q = bh_qvalues([c["p_cluster"] for c in tested])
    for c, qq in zip(tested, q):
        c["q_bh"] = qq
    for c in all_cells:
        c.setdefault("q_bh", None)
        c["status"] = label(c)
        c["horizon"] = horizon
    counts = Counter(c["status"] for c in all_cells)
    n_tested = len(tested)
    return {"miner_version": MINER_VERSION, "horizon": horizon, "discovery_weeks": sorted(discovery_weeks),
            "evidence_class": "HYPOTHESIS_GENERATING (discovery window; never confirmatory)",
            "floors": {"min_games": MIN_GAMES, "min_weeks": MIN_WEEKS, "min_contracts": MIN_CONTRACTS, "bh_q": BH_Q,
                       "bootstrap_B": BOOTSTRAP_B, "ci_level": CI_LEVEL},
            "n_side_rows": len(sides), "slices": slices, "n_cells": len(all_cells), "n_cells_tested": n_tested,
            "expected_false_ci_exclusions_under_null": round(0.05 * n_tested, 1),
            "status_counts": dict(counts), "cells": all_cells, "betting_authorized": False}


# ---------------------------------------------------------------------------------------------- ladders
def ladder_report(rows, *, horizon: str = "latest_pregame", entry_horizon: str = "T-24h") -> dict:
    """Ladder-level research (Phase M): one ladder = one continuous-outcome thesis, many rungs.

    Per ladder: rungs, the main rung, the best REALISED rung (fee-adjusted, YES side), the rung whose ask sat
    furthest BELOW the ladder's own monotone (PAV) fair curve (an internal-coherence reading that needs no model),
    the best entry-to-close CLV rung from `entry_horizon`, the tail steepness around the main rung, monotone
    violations. Aggregated by family: how often the main rung vs an alternate rung was the best realised and the
    best CLV rung -- with the caution that the realised winner of a ladder is ONE draw of one outcome."""
    from nfl_edge.research.board import pav_decreasing
    by = defaultdict(lambda: defaultdict(dict))
    for r in rows:
        if r.get("ladder_id") and r.get("horizon") in (horizon, entry_horizon) and r.get("settled_yes") is not None \
                and r.get("settlement_source") == "FOOTBALL_PROVEN":
            by[r["ladder_id"]][r["ticker"]][r["horizon"]] = r
    out_ladders = []
    agg = defaultdict(Counter)
    for lid, tick in by.items():
        rungs = []
        for t, hs in tick.items():
            h = hs.get(horizon)
            if not h or h.get("obs_state") != "OBSERVED" or h.get("rung_value") is None:
                continue
            e = hs.get(entry_horizon)
            clv = (h["mid"] - e["yes_ask"]) if (e and e.get("yes_ask") is not None and h.get("mid") is not None and e.get("obs_state") == "OBSERVED") else None
            rungs.append({"ticker": t, "x": h["rung_value"], "mid": h.get("mid"), "yes_ask": h.get("yes_ask"),
                          "ret_yes": h.get("return_yes"), "main": bool(h.get("is_main_rung")), "clv_yes_from_entry": clv,
                          "family": h["family"], "game_id": h["game_id"], "week": h["week"], "two_sided": h.get("two_sided")})
        live = [r for r in rungs if r["two_sided"] and r["mid"] is not None]
        if len(live) < 3:
            continue
        live.sort(key=lambda r: r["x"])
        fair = dict(pav_decreasing([(r["x"], r["mid"]) for r in live]))
        for r in live:
            r["fair"] = fair.get(r["x"])
            r["ask_below_fair"] = (r["fair"] - r["yes_ask"]) if (r["fair"] is not None and r["yes_ask"] is not None) else None
        main = next((r for r in live if r["main"]), None)
        with_ret = [r for r in live if r["ret_yes"] is not None]
        best_real = max(with_ret, key=lambda r: (r["ret_yes"], -abs(r["x"] - (main["x"] if main else r["x"])))) if with_ret else None
        best_coh = max(live, key=lambda r: (r["ask_below_fair"] if r["ask_below_fair"] is not None else -9))
        with_clv = [r for r in live if r["clv_yes_from_entry"] is not None]
        best_clv = max(with_clv, key=lambda r: r["clv_yes_from_entry"]) if with_clv else None
        slope = None
        if main:
            i = live.index(main)
            if 0 < i < len(live) - 1 and live[i + 1]["x"] != live[i - 1]["x"]:
                slope = (live[i - 1]["mid"] - live[i + 1]["mid"]) / (live[i + 1]["x"] - live[i - 1]["x"])
        viol = sum(1 for a, b in zip(live, live[1:]) if b["mid"] > a["mid"] + 1e-9)
        fam = live[0]["family"]
        rec = {"ladder_id": lid, "family": fam, "game_id": live[0]["game_id"], "week": live[0]["week"], "n_live_rungs": len(live),
               "main_rung": main["x"] if main else None, "best_realised_rung": best_real["x"] if best_real else None,
               "best_realised_is_main": bool(best_real and main and best_real["ticker"] == main["ticker"]),
               "best_coherence_rung": best_coh["x"], "best_coherence_gap": best_coh["ask_below_fair"],
               "best_clv_rung": best_clv["x"] if best_clv else None,
               "best_clv_is_main": bool(best_clv and main and best_clv["ticker"] == main["ticker"]),
               "tail_slope_per_unit": slope, "monotone_violations": viol,
               "coherent": viol == 0}
        out_ladders.append(rec)
        a = agg[fam]
        a["ladders"] += 1
        a["best_realised_is_main"] += int(rec["best_realised_is_main"])
        a["best_clv_is_main"] += int(rec["best_clv_is_main"])
        a["with_clv"] += int(best_clv is not None)
        a["incoherent"] += int(viol > 0)
        a["coherence_gap_ge_2c"] += int((best_coh["ask_below_fair"] or 0) >= 0.02)
    summary = {fam: {**dict(c), "share_best_realised_main": c["best_realised_is_main"] / c["ladders"] if c["ladders"] else None,
                     "share_best_clv_main": c["best_clv_is_main"] / c["with_clv"] if c["with_clv"] else None}
               for fam, c in sorted(agg.items())}
    return {"horizon": horizon, "entry_horizon": entry_horizon, "n_ladders": len(out_ladders), "by_family": summary,
            "ladders": sorted(out_ladders, key=lambda r: (r["week"], r["game_id"], r["ladder_id"])),
            "caution": "a ladder's realised best rung is one draw of one outcome; read the by-family shares across many "
                       "ladders, never one ladder's winner"}
