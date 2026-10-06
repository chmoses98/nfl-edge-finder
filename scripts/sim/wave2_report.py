#!/usr/bin/env python3
"""Build the Wave-2 research artifacts (JSON) from the local development / diagnostic runs.

  s1     research/game_script_v2/wave2/S1_SHARE_DISPERSION.json
  q1     research/game_script_v2/wave2/Q1_QB_EXIT_TAIL.json
  a1     research/game_script_v2/wave2/A1_AVAILABILITY_HORIZONS.json
  risk1  research/game_script_v2/wave2/RISK1_SCRIPT_ROBUSTNESS.json

DEVELOPMENT = 2020 (each arm vs the incumbent on identical rows, bundle trained 2018-2019); CONTAMINATED_DIAGNOSTIC =
2021-2025 (vs the Wave-1 five-season baseline, the same incumbent code). Status words follow PREREGISTRATION.md
section 7 mechanically.

Usage: python scripts/sim/wave2_report.py {s1,q1,a1,risk1}
"""
from __future__ import annotations
import argparse, json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
import numpy as np
import pandas as pd
from nfl_edge.sim import five_year as FY, injury_validation as IV, training as T, wave2_eval as E

W2 = os.path.join(ROOT, "research", "game_script_v2", "wave2")
CACHE = os.path.join(ROOT, "data", "cache", "game_script_v2", "wave2")
DEV, DIAG = [2020], [2021, 2022, 2023, 2024, 2025]
A0_DEV, A0_DIAG = os.path.join(CACHE, "dev", "A0"), FY.DEFAULT_OUT


def _dump(name, obj):
    obj = {k: v for k, v in obj.items() if not k.startswith("_")}
    json.dump(obj, open(os.path.join(W2, name), "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    print("wrote", name)


def _strip(rep):
    return {k: v for k, v in rep.items() if not k.startswith("_")}


def role_instability(season: int) -> pd.Series:
    """Team-game mean |short - long half-life target share| of the three largest prior target shares (pregame)."""
    fr = T.assemble(range(2016, season + 1), verbose=lambda *x: None, priors=T.fit_priors_for(season))
    e = fr["eligible"]; e = e[e["season"] == season].copy()
    e["_l"] = e["sh_target_l"].fillna(0)
    e = e.sort_values("_l", ascending=False).groupby(["game_id", "team"]).head(3)
    return (e["sh_target_s"] - e["sh_target_l"]).abs().groupby([e["game_id"], e["team"]]).mean()


# ---------------------------------------------------------------------------------------------- S1
def s1():
    sel = json.load(open(os.path.join(CACHE, "s1_dev.json")))
    stats = E.S1_STATS + E.Q1_STATS + E.OTHER_STATS
    dev = E.arm_report(A0_DEV, os.path.join(CACHE, "dev", "S1"), DEV, stats, "S1")
    diag = E.arm_report(A0_DIAG, os.path.join(CACHE, "diag", "S1"), DIAG, stats, "S1")
    st = dev["pooled"]["stats"]
    # PREREGISTRATION section 2 (all five move toward uniform; CRPS not worse) and section 7 (chi-square falls for >= 3 of 5)
    chi_fall = sum(st[s]["chi2_arm"] < st[s]["chi2_a0"] for s in E.S1_STATS)
    edge = lambda r, k: abs(r[f"low_decile_{k}"] + r[f"high_decile_{k}"] - 0.2)
    edge_fall = sum(edge(st[s], "arm") < edge(st[s], "a0") for s in E.S1_STATS)
    crps_ok = all(st[s]["rel_crps"] <= 0 for s in E.S1_STATS)
    mae_ok = all(st[s]["mae_arm"] / st[s]["mae_a0"] - 1 <= 0.005 for s in E.S1_STATS)
    mech = {"chi2_falls_count_of_5": int(chi_fall), "edge_bin_mass_toward_0.20_count_of_5": int(edge_fall),
            "section7_chi2_falls_for_at_least_3": chi_fall >= 3, "section2_all_five_toward_uniform": chi_fall == 5 and edge_fall == 5,
            "crps_of_each_of_the_five_not_worse": bool(crps_ok), "mae_of_the_five_within_0.5pct": bool(mae_ok)}
    # subgroups on the contaminated diagnostic (descriptive)
    flags = pd.concat([IV.populations(y, A0_DIAG)[0] for y in DIAG], ignore_index=True)
    role = pd.concat([role_instability(y) for y in DIAG])
    sub = E.subgroup_tables(diag["_rows"], flags=flags, role=role)
    ms = E.min_sample(E.per_game_effect(dev["_rows"], "S1"))
    passed_dev = all(f["status"] == "SELECTED" for f in sel["families"].values()) and all(
        mech[k] for k in ("section7_chi2_falls_for_at_least_3", "section2_all_five_toward_uniform", "crps_of_each_of_the_five_not_worse"))
    diag_ok = diag["pooled"]["primary"]["mean"] <= 0
    status = "PROSPECTIVE_CHALLENGER" if passed_dev and diag_ok else ("DIAGNOSTIC_FAIL" if passed_dev else "REJECTED_AT_DEVELOPMENT")
    comps = json.load(open(os.path.join(W2, "components_2026.json")))
    _dump("S1_SHARE_DISPERSION.json", {
        "arm": "S1", "status": status, "evidence": {"development": DEV, "contaminated_diagnostic": DIAG},
        "selection": {k: {kk: v.get(kk) for kk in ("selected", "status", "incumbent_alpha_moment", "mean_loglik_2020", "S1_0_minus_incumbent",
                                                   "S1_1_minus_S1_0", "S1_1_minus_incumbent", "coefficients", "alpha_S1_1_2020_quantiles")}
                      | {"S1_0_alpha_ml": float(np.exp(v["S1-0"]["b0"]))} for k, v in sel["families"].items()},
        "development_mechanism_check": {"by_stat": dev["pooled"]["stats"], "primary": dev["pooled"]["primary"], "criteria": mech},
        "contaminated_diagnostic": {"by_season": {y: _strip(v) for y, v in diag["by_season"].items()}, "pooled": diag["pooled"], "subgroups": sub},
        "minimum_prospective_sample": ms,
        "frozen_2026_components": {k: {"form": v["form"], "base_alpha": float(np.exp(v["b0"])), "train_seasons": v["train_seasons"]}
                                   for k, v in comps["S1"].items()}})


# ---------------------------------------------------------------------------------------------- Q1
def regime_bands(sel) -> dict:
    """90% posterior-predictive band of each regime's 2020 count under the selected 2018-2019 model (Q1-0: a beta-binomial
    from the training counts with a flat Dirichlet prior); the plain binomial band is reported alongside."""
    from scipy import stats
    tr, ob = sel["regime_frequency"]["train"], sel["regime_frequency"]["2020"]
    N, n = sum(tr), sum(ob)
    out = {}
    for i, lab in enumerate(("FULL", "PARTIAL", "LOW")):
        bb, bi = stats.betabinom(n, tr[i] + 1, N - tr[i] + 2), stats.binom(n, tr[i] / N)
        lo, hi = int(bb.ppf(0.05)), int(bb.ppf(0.95))
        out[lab] = {"observed_2020": int(ob[i]), "train": int(tr[i]), "band90": [lo, hi], "binomial_band90": [int(bi.ppf(0.05)), int(bi.ppf(0.95))],
                    "inside": bool(lo <= ob[i] <= hi)}
    return out


def q1_findings(st, bands, dev, diag) -> list:
    b = bands["PARTIAL"]
    return [
        f"The section-7 mechanism check fails: 2020 had {b['observed_2020']} PARTIAL games against a 90% predictive band of "
        f"{b['band90'][0]}-{b['band90'][1]} from 2018-2019, so the regime model fitted on the development seasons did not "
        "describe the development hold-out season. This alone makes Q1 REJECTED_AT_DEVELOPMENT; the rule is applied as written.",
        "Ambiguity (recorded, not resolved in Q1's favour): PREREGISTRATION section 3 names the lower-decile check as the "
        "mechanism check and section 7 names the regime-frequency check; both are required here because relaxing either "
        "after seeing 2020 would be choosing the gate from the outcome.",
        f"The lower-decile check itself passes: P(rPIT < 0.10) for attempts moves {st['attempts']['low_decile_a0']:.3f} -> "
        f"{st['attempts']['low_decile_arm']:.3f}, completions {st['completions']['low_decile_a0']:.3f} -> "
        f"{st['completions']['low_decile_arm']:.3f}, passing yards {st['pass_yards']['low_decile_a0']:.3f} -> "
        f"{st['pass_yards']['low_decile_arm']:.3f}, with CRPS better; but the 2020 primary interval includes zero "
        f"({dev['pooled']['primary']['mean']:+.4f} [{dev['pooled']['primary']['lo']:+.4f}, {dev['pooled']['primary']['hi']:+.4f}]).",
        f"Negative: the mean overshoots. Attempts bias moves {st['attempts']['bias_a0']:+.2f} -> {st['attempts']['bias_arm']:+.2f} and "
        f"MAE worsens {100 * (st['attempts']['mae_arm'] / st['attempts']['mae_a0'] - 1):+.2f}% (passing yards "
        f"{100 * (st['pass_yards']['mae_arm'] / st['pass_yards']['mae_a0'] - 1):+.2f}%): an unconditional exit mixture moves "
        "mass from every starter, not from the ones who will leave.",
        f"Diagnostic 2025 is the one season where the primary is worse "
        f"({diag['by_season']['2025']['primary']['mean']:+.4f}); 2025 is the season with daily depth charts, where the "
        "incumbent identified the starter best.",
        "A conditional (feature-based) regime model did not beat the unconditional frequencies on 2020 log loss; the "
        "fixed feature list does not identify exits in advance at this sample size.",
    ]


def q1():
    sel = json.load(open(os.path.join(CACHE, "q1_dev.json")))
    stats = E.Q1_STATS + ("pass_td",) + E.S1_STATS
    dev = E.arm_report(A0_DEV, os.path.join(CACHE, "dev", "Q1"), DEV, stats, "Q1")
    diag = E.arm_report(A0_DIAG, os.path.join(CACHE, "diag", "Q1"), DIAG, stats, "Q1")
    st = dev["pooled"]["stats"]
    toward = all(abs(st[s]["low_decile_arm"] - 0.1) < abs(st[s]["low_decile_a0"] - 0.1) for s in E.Q1_STATS)
    crps_ok = all(st[s]["rel_crps"] <= 0.005 for s in E.Q1_STATS)
    receivers = {s: {"rel_crps": st[s]["rel_crps"], "bias_a0": st[s]["bias_a0"], "bias_arm": st[s]["bias_arm"]} for s in E.S1_STATS if s in st}
    bands = regime_bands(sel)
    mech = {"section3_lower_decile_moves_toward_0.10_for_all_three": bool(toward), "section3_crps_of_the_three_within_0.5pct": bool(crps_ok),
            "section7_regime_frequencies_inside_90pct_predictive_bands": all(b["inside"] for b in bands.values()), "regime_bands_2020": bands}
    ms = E.min_sample(E.per_game_effect(dev["_rows"], "Q1"))
    passed_dev = all(mech[k] for k in ("section3_lower_decile_moves_toward_0.10_for_all_three", "section3_crps_of_the_three_within_0.5pct",
                                       "section7_regime_frequencies_inside_90pct_predictive_bands"))
    diag_ok = diag["pooled"]["primary"]["mean"] <= 0
    status = "PROSPECTIVE_CHALLENGER" if passed_dev and diag_ok else ("DIAGNOSTIC_FAIL" if passed_dev else "REJECTED_AT_DEVELOPMENT")
    _dump("Q1_QB_EXIT_TAIL.json", {
        "arm": "Q1", "status": status, "evidence": {"development": DEV, "contaminated_diagnostic": DIAG},
        "selection": {k: sel[k] for k in ("selected", "log_loss_2020", "conditional_minus_unconditional", "unconditional_minus_incumbent_implied",
                                          "regime_frequency", "identification_error_rate", "exit_partial_rate", "incumbent_implied_regime_frequency",
                                          "n_train", "n_score")},
        "regime_quantiles_unconditional": {k: v[::20] for k, v in sel["model_unconditional"]["regime_quantiles"].items()},
        "development_mechanism_check": {"by_stat": st, "primary_delta_lower_decile_error": dev["pooled"]["primary"], "criteria": mech,
                                        "receivers_downstream": receivers},
        "contaminated_diagnostic": {"by_season": {y: _strip(v) for y, v in diag["by_season"].items()}, "pooled": diag["pooled"]},
        "minimum_prospective_sample": ms,
        "findings": q1_findings(st, bands, dev, diag),
        "note": ("receivers' targets do not depend on which quarterback throws; their row-level draws differ only for the team simulated "
                 "second (numpy's binomial in the incumbent QB touchdown split consumes a p-dependent number of draws)")})


# ---------------------------------------------------------------------------------------------- A1
def _with_questionable(base_dir):
    def f(d, y):
        el = pd.read_parquet(os.path.join(base_dir, f"eligible_{y}.parquet"))
        q = el[el["avail_state"] == "QUESTIONABLE"][["game_id", "player_id"]].assign(questionable=True)
        d = d.merge(q, on=["game_id", "player_id"], how="left")
        d["questionable"] = d["questionable"].fillna(False).astype(bool)
        tq = d[d["questionable"]][["game_id", "team"]].drop_duplicates().assign(team_has_q=True)
        d = d.merge(tq, on=["game_id", "team"], how="left")
        d["teammate_of_q"] = d["team_has_q"].fillna(False).astype(bool) & ~d["questionable"]
        return d
    return f


def a1_findings(out) -> list:
    dv, dg = out["development"]["T0_INACTIVES"], out["contaminated_diagnostic"]["T0_INACTIVES"]
    q, qd = dv["questionable_players"], dg["questionable_players"]
    mae = lambda r: 100 * (r["mae_arm"] / r["mae_a0"] - 1)
    worst = max(qd, key=lambda s: mae(qd[s]))
    return [
        "The incumbent historical backtest discounts a QUESTIONABLE player's participation even though the game-day inactive "
        "list (which it also uses) already shows the player is active; at T0_INACTIVES that second discount is removed. Questionable "
        f"players' bias moves from {q['targets']['bias_a0']:+.2f} to {q['targets']['bias_arm']:+.2f} targets and "
        f"{q['carries']['bias_a0']:+.2f} to {q['carries']['bias_arm']:+.2f} carries in 2020; relative CRPS of the five "
        f"is {min(100 * r['rel_crps'] for r in q.values()):+.1f}% to {max(100 * r['rel_crps'] for r in q.values()):+.1f}%.",
        f"Negative: the correction overshoots for yardage. Diagnostic {worst} MAE {mae(qd[worst]):+.2f}% (bias "
        f"{qd[worst]['bias_a0']:+.2f} -> {qd[worst]['bias_arm']:+.2f}); a questionable player who is active still plays somewhat "
        "less than an unlisted one, so EXPECTED_ACTIVE is not the end state -- but no intermediate discount was "
        "preregistered and none is fitted here.",
        f"The diagnostic effect shrinks over time and its 2022-2025 intervals include zero "
        f"(2025: {dg['by_season_primary']['2025']['mean']:+.3f} [{dg['by_season_primary']['2025']['lo']:+.3f}, "
        f"{dg['by_season_primary']['2025']['hi']:+.3f}]).",
        "T24 has worse CRPS than the incumbent's mixed horizon on every questionable-player statistic and on teammates (it no longer knows "
        "who is inactive). It is still optimistic: it is scored on the incumbent's rows, i.e. players who were active, so "
        "the players it wrongly projects as playing (inactive, actual zero) are not in the paired population.",
    ]


def a1():
    stats = ("carries", "targets", "receptions", "rec_yards", "rush_yards")
    out = {"arm": "A1", "horizons": ["T0_GAMEDAY_INACTIVES_WITH_Q_DISCOUNT (incumbent historical backtest, relabelled)", "T0_INACTIVES", "T24"],
           "evidence": {"development": DEV, "contaminated_diagnostic": DIAG}}
    for name, phase_dirs in (("development", (A0_DEV, "dev", DEV)), ("contaminated_diagnostic", (A0_DIAG, "diag", DIAG))):
        base, ph, seasons = phase_dirs
        t0 = E.arm_report(base, os.path.join(CACHE, ph, "A1T0"), seasons, stats, "A1", extra=_with_questionable(base))
        t24 = E.arm_report(base, os.path.join(CACHE, ph, "A1T24"), seasons, stats, "A1", extra=_with_questionable(base))
        blk = {}
        for lab, rep in (("T0_INACTIVES", t0), ("T24", t24)):
            D = rep["_rows"]
            blk[lab] = {"questionable_players": E.stat_table(D[D["questionable"]]), "teammates_of_questionable": E.stat_table(D[D["teammate_of_q"]]),
                        "everyone_else": E.stat_table(D[~D["questionable"] & ~D["teammate_of_q"]]), "primary_delta_abs_bias": rep["pooled"]["primary"],
                        "by_season_primary": {y: v["primary"] for y, v in rep["by_season"].items()}}
            if name == "development" and lab == "T0_INACTIVES":
                out["minimum_prospective_sample"] = E.min_sample(E.per_game_effect(D, "A1"))
        out[name] = blk
    dq = out["development"]["T0_INACTIVES"]
    teammate_ok = all(v["rel_crps"] <= 0.005 for v in dq["teammates_of_questionable"].values())
    passed = dq["primary_delta_abs_bias"]["mean"] < 0 and teammate_ok
    diag_ok = out["contaminated_diagnostic"]["T0_INACTIVES"]["primary_delta_abs_bias"]["mean"] <= 0
    out["development_mechanism_check"] = {"questionable_bias_moves_toward_zero": dq["primary_delta_abs_bias"]["mean"] < 0,
                                         "questionable_bias_interval_excludes_zero": dq["primary_delta_abs_bias"]["hi"] < 0, "teammates_crps_within_0.5pct": teammate_ok}
    out["status"] = "PROSPECTIVE_CHALLENGER" if passed and diag_ok else ("DIAGNOSTIC_FAIL" if passed else "REJECTED_AT_DEVELOPMENT")
    out["findings"] = a1_findings(out)
    out["note"] = ("T24 is the honest earlier-horizon accuracy and is never described as the T0 number; prospective records can claim "
                   "T0_INACTIVES only after the inactive release with game-day statuses observed in a roster retrieved before the cutoff")
    _dump("A1_AVAILABILITY_HORIZONS.json", out)


# ---------------------------------------------------------------------------------------------- RISK1
def risk1(md_ref="origin/market-data"):
    import subprocess
    from nfl_edge.sim import risk1 as R
    pw = json.load(open(os.path.join(CACHE, "risk1_power.json")))
    names = subprocess.run(["git", "ls-tree", "-r", "--name-only", md_ref, "data/shadow/sim"], capture_output=True, text=True, cwd=ROOT).stdout.split()
    caps = sorted(n for n in names if n.endswith(".scripts_v2.json.gz"))
    after = [n for n in caps if os.path.basename(n)[:16] >= "20261005T161402Z"]
    _dump("RISK1_SCRIPT_ROBUSTNESS.json", {
        "item": "RISK1", "version": R.RISK1_VERSION, "status": "COLLECTING", "prospective_cutoff": R.PROSPECTIVE_CUTOFF,
        "authority": "NONE: RISK1 never changes a probability, a stake or an authority",
        "capture": {"source": "shadow-price cycle on main (GAME SCRIPT V2 document + projection rows, write-once on market-data)",
                    "captures_seen_at_build": len(caps), "captures_after_cutoff_at_build": len(after),
                    "fingerprints": "frozen within 6 h of kickoff once the Wave-2 branch is on main",
                    "listing_ref": md_ref},
        "minimum_prospective_sample": {"n_games": pw["n_games_required"], "n_weeks_at_16": pw["n_weeks_required_at_16"],
                                       "per_game_contrast_sd": pw["per_game_contrast_sd"], "minimal_effect": pw["minimal_effect"],
                                       "source": pw["evidence"], "n_contracts_in_study": pw["n_contracts"],
                                       "underpowered_at_one_season": pw["underpowered_at_one_season"]},
        "development_contrast_2020": {"per_game_contrast_mean": pw["per_game_contrast_mean"],
                                      "note": "synthetic prices equal the simulated probability; this sets the sample size and is NOT evidence"},
        "primary_test": "logistic(outcome ~ logit(mid) + logit(p_model) + z(measure) + family) per measure, game-clustered bootstrap, Holm over 4",
        "measures": [m for m, _ in R.MEASURES], "thesis_jaccard_threshold": R.THESIS_JACCARD,
        "results": None})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["s1", "q1", "a1", "risk1"])
    a = ap.parse_args()
    {"s1": s1, "q1": q1, "a1": a1, "risk1": risk1}[a.cmd]()


if __name__ == "__main__":
    main()
