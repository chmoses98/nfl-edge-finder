"""Invariant checks of the proposed contract over every 2021-2025 REG game (research only)."""
import json, os, sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.getcwd())
import numpy as np, pandas as pd
from scripts.sim import gf_models as GM
from scripts.sim.hmac_run import load as hload
from research.game_flow_integration import reference_impl as R
fl = GM.flow_table(); a1 = hload("A1")[["game_id", "mean_m", "mean_t"]].set_index("game_id"); bad = {k: 0 for k in ("pmf_norm", "lead_masses", "lead14_lt_tail", "mean_mismatch", "sign", "low_neff", "prob_range")}
n = 0; neff = []; ex = None; maxdm = 0.0
for Y in range(2021, 2026):
    for r in fl[(fl.season == Y) & fl.game_id.isin(a1.index)].itertuples():
        mm, mt = a1.loc[r.game_id, "mean_m"], a1.loc[r.game_id, "mean_t"]
        b = R.build(fl, float(r.spread_line), float(r.total_line), Y, float(mm), float(mt), {"source": "consensus_line", "observed_at": None, "minutes_to_kickoff": 0})
        n += 1; h = b["halftime"]; neff.append(b["training"]["effective_sample"]); maxdm = max(maxdm, abs(b["implied_final"]["mean_margin"] - mm))
        bad["lead_masses"] += int(not (0 <= h["p_lead_7plus_home"] + h["p_lead_7plus_away"] <= 1 + 1e-9))
        bad["prob_range"] += int(not all(0 <= x <= 1 for x in (h["p_lead_7plus_home"], h["p_lead_7plus_away"], b["flow"]["p_lead_14plus_any_time"], b["flow"]["p_within_8_entering_q4"])))
        bad["mean_mismatch"] += int(abs(b["implied_final"]["mean_margin"] - mm) > 0.05 or abs(b["implied_final"]["mean_total"] - mt) > 0.05)
        bad["sign"] += int(r.spread_line != 0 and np.sign(h["margin_home"]["mean"]) != np.sign(r.spread_line))
        bad["low_neff"] += int(b["training"]["effective_sample"] < 100)
        bad["lead14_lt_tail"] += int(b["flow"]["p_lead_14plus_any_time"] < 0.0)
        if ex is None and Y == 2025:
            ex = b
out = {"games_checked": n, "violations": bad, "effective_sample": {"min": float(min(neff)), "median": float(np.median(neff))}, "max_abs_final_mean_margin_error_vs_sim": maxdm}
json.dump(out, open("research/game_flow_integration/contract_validation.json", "w"), indent=1); json.dump(ex, open("research/game_flow_integration/example_payload.json", "w"), indent=1); print(out)
