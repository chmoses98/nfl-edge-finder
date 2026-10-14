"""RESEARCH REFERENCE IMPLEMENTATION of the proposed `game_flow` block (NOT production code, not imported by anything).

G0c = the historical-trajectory baseline (G0: closing spread/total kernel over 2003..season-1 regular-season trajectories,
half-widths 6 and 9, season half-life 6, 10% wide-kernel floor) exponentially TILTED so its mean regulation margin and total
equal the published simulation's means: the halftime outlook then agrees with the final-score projection at the mean level.
G0c vs G0 (validated here on 4,128 games 2010-2025): primary metrics change by -0.6% to +0.15%, i.e. no loss.
"""
from __future__ import annotations
import numpy as np
from scripts.sim import gf_models as GM

VERSION = "game-flow-1.0.0"
BW = GM.BW["b3"]
GATES = {  # evidence-based display gates, see DISPLAY_GATES.md
    "halftime.margin_distribution": "DISPLAY", "halftime.total_distribution": "DISPLAY",
    "halftime.p_lead_7plus": "DISPLAY_WITH_CAUTION", "flow.p_lead_14plus_any_time": "DISPLAY_WITH_CAUTION",
    "flow.p_within_8_entering_q4": "RESEARCH_ONLY", "flow.p_comeback_10": "SUPPRESS", "flow.p_q4_lead_change": "SUPPRESS",
    "flow.scoring_drought": "SUPPRESS", "script.close_win_split": "SUPPRESS",
    "opportunity.plays_dropbacks_rush_pass_rate": "DISPLAY_WITH_CAUTION", "opportunity.drives": "SUPPRESS"}


def _q(p, grid, qs=(0.05, 0.25, 0.5, 0.75, 0.95)):
    c = np.cumsum(p); return {f"p{int(q * 100):02d}": float(grid[min(int(np.searchsorted(c, q)), len(grid) - 1)]) for q in qs}


def build(flow, spread_home, total_line, season, sim_mean_margin, sim_mean_total, centre):
    """flow: GM.flow_table(); centre: {'source','observed_at','minutes_to_kickoff'}; returns the contract block (dict)."""
    tr = flow[(flow.season >= GM.TRAIN_START) & (flow.season < season)]
    O = np.c_[tr[GM.OCOLS].to_numpy(float), tr.reg_m.to_numpy(float), tr.reg_t.to_numpy(float)]
    w = GM.kernel_weights(tr, spread_home, total_line, season, *BW)
    q = GM.tilt(O, w, np.array([sim_mean_margin, sim_mean_total]), [10, 11]); rec = GM.record_from(O[:, :10], q)
    gm, gt = np.arange(-50, 51), np.arange(0, 81); pm, pt, pe = rec["pm"], rec["pt"], rec["pe"]
    fav = None if spread_home == 0 else ("HOME" if spread_home > 0 else "AWAY")
    m = lambda p, g: float(p @ g)
    return {"version": VERSION, "state": "OK", "orientation": "home_minus_away; every *_home / *_away field is from that team's own side",
            "market_centre": {"spread_home": spread_home, "total": total_line, **centre, "favorite": fav},
            "evidence_class": "MARKET_DERIVED_CONDITIONAL", "independent_of_market": False, "ranking_eligible": False,
            "method": "historical trajectories matched on closing spread and total (2003..season-1 REG), tilted to the published simulation means",
            "training": {"seasons": [GM.TRAIN_START, season - 1], "games": int(len(tr)), "effective_sample": float(1 / np.sum(q ** 2))},
            "halftime": {"margin_home": {"mean": m(pm, gm), **_q(pm, gm)}, "total": {"mean": m(pt, gt), **_q(pt, gt)},
                         "p_lead_7plus_home": float(pe[4]), "p_lead_7plus_away": float(pe[5]), "p_tied_or_within_6": float(1 - pe[4] - pe[5])},
            "flow": {"p_lead_14plus_any_time": float(pe[1]), "p_within_8_entering_q4": float(pe[0])},
            "implied_final": {"p_home_win_regulation": float(q @ (O[:, 10] > 0)), "mean_margin": float(q @ O[:, 10]), "mean_total": float(q @ O[:, 11])},
            "gates": GATES}
