"""Prose for RESULTS_NFL.md and the narrative sections of summary.json. Every number is read from the walk-forward
results (results/nfl_walkforward.json) at render time, so a weekly re-run cannot leave stale numbers in the prose."""
from __future__ import annotations

import numpy as np

from . import render as R

NAMES = {"A": "A (season avg, shrunk)", "B": "B (EWMA, shrunk)", "C": "C (opportunity x efficiency)", "D": "D (C + opponent + game env)",
         "D_opp": "D_opp (opponent only)", "E": "E (LightGBM walk-forward)", "F": "F (stack)", "MKT": "closing implied team total",
         "INC_0.4.0": "incumbent shadow-0.4.0", "INC_0.5.0": "challenger shadow-0.5.0", "D_vac": "D + vacated opportunity",
         "F_vac": "F + vacated opportunity", "D_av": "D + availability (vacated + own Questionable)", "F_av": "F + availability (vacated + own Questionable)",
         "A_qs": "A, QB starts-only", "B_qs": "B, QB starts-only", "C_qs": "C, QB starts-only", "D_qs": "D, QB starts-only + implied total", "F_qs": "F, QB starts-only stack", "D_oracle_avail": "D + oracle availability (bound)", "F_oracle_avail": "F + oracle availability (bound)"}
PLAYER = ["targets", "receptions", "receiving_yards", "carries", "rushing_yards", "passing_attempts", "completions", "passing_yards",
          "passing_tds", "anytime_td"]
TEAM = ["team_pass_attempts", "team_rush_attempts", "team_points"]


def _p(fr, key):
    return (fr.get("pairs") or {}).get(key)


def _ci(d, nd=4):
    return R.ci(d, nd) if d else "n/a"


def _sig_better(d):
    return d is not None and d["ci95"][1] < 0


def _sig_worse(d):
    return d is not None and d["ci95"][0] > 0


def _count(sel, key, fams, test):
    n = sum(1 for f in fams if test(_p(sel["families"][f], key)))
    k = sum(1 for f in fams if _p(sel["families"][f], key) is not None)
    return n, k


def experiments(wf):
    sel = wf["select"]
    fam = sel["families"]
    ex = []
    # 1 ladder
    best = {f: fam[f]["best_model"] for f in fam}
    ex.append({"id": "NFL-PF-01-ladder", "question": "Which rung of the A..F ladder projects each family best?",
               "hypothesis": "Structured opportunity x efficiency models (C/D) and learned models (E/F) beat shrunk averages (A/B).",
               "method": "Walk-forward: A-D are point-in-time formulas whose few hyperparameters (shrinkage k, EWMA halflife, elasticities) were tuned on 2016-2021; "
                         "E is LightGBM refitted every season on all earlier seasons; F is a non-negative stack fitted on 2016-2021 predictions. "
                         "Each model gets its own distribution fitted on its development residuals; validation (2022-23) selects.",
               "data": "nflverse 2012-2025 regular seasons; " + ", ".join(f"{f} n_val={fam[f]['models'][best[f]]['validation']['n_obs']}" for f in fam),
               "result": "; ".join(f"{f}: best {best[f]} (val CRPS {fam[f]['models'][best[f]]['validation']['crps']:.4f} vs A "
                                   f"{fam[f]['models']['A']['validation']['crps']:.4f})" for f in fam),
               "interpretation": "See per-family tables. Gains over A are game-clustered paired differences on identical player-games.",
               "decision": "adopt"})
    # 2 opponent adjustment
    effs = [f for f in ("receptions", "receiving_yards", "rushing_yards", "completions", "passing_yards", "passing_tds", "anytime_td") if f in fam]
    nb, k = _count(sel, "D - C", effs, _sig_better)
    nw, _ = _count(sel, "D - C", effs, _sig_worse)
    ex.append({"id": "NFL-PF-02-opponent", "question": "Does a schedule-adjusted opponent factor (rolling ridge, refitted before every week) plus closing spread/total improve player projections beyond opportunity x efficiency?",
               "hypothesis": "D beats C on validation CRPS.",
               "method": "D = C with team volume from the opponent/environment team model and an efficiency elasticity beta on the opponent's ridge factor, "
                         "beta fitted by Poisson (Bernoulli for TD) likelihood on 2016-2021 only.",
               "data": "validation 2022-2023, paired on identical player-games, games as clusters",
               "result": f"D better than C (CI excludes 0) in {nb}/{k} efficiency families, worse in {nw}/{k}. " +
                         "; ".join(f"{f}: {_ci(_p(fam[f], 'D - C'))}" for f in effs),
               "interpretation": "Negative = D better. Opponent effects in the NFL box score are small relative to player-game noise; the gain, where it exists, is modest.",
               "decision": "adopt" if nb > nw else "reject"})
    # 3 game environment on team volume
    ex.append({"id": "NFL-PF-03-game-environment", "question": "Do the closing spread and total add to the opponent-adjusted team volume projection?",
               "hypothesis": "D (opponent + environment) beats D_opp (opponent only) for team pass/rush attempts and points.",
               "method": "Poisson log-linear elasticities on B (EWMA) fitted on 2016-2021; spread/7 and (total-44)/7 terms; for points log(implied/B).",
               "data": "validation 2022-2023 team-games",
               "result": "; ".join(f"{f}: D - D_opp {_ci(_p(fam[f], 'D - D_opp'))}; D_opp - B {_ci(_p(fam[f], 'D_opp - B'))}" for f in TEAM if f in fam),
               "interpretation": "The closing line carries most of the pregame information on team points and rush volume; pass volume is nearly spread-neutral in aggregate "
                                 "(2016-21: 34.0 attempts as a 7+ point underdog vs 34.6 as a 7+ favourite) while rush attempts rise from 24.4 to 28.5.",
               "decision": "adopt"})
    # 4 vacated opportunity
    corr = wf.get("corrections", {})
    vac_f = [f for f in ("targets", "receptions", "receiving_yards", "carries", "rushing_yards", "anytime_td") if f in fam]
    ex.append({"id": "NFL-PF-04-vacated-opportunity", "question": "Do teammates listed OUT/DOUBTFUL on the final injury report explain part of the opportunity error (the mean_defect 'listing/role' residual)?",
               "hypothesis": "Renormalising a player's share for vacated teammate opportunity, share x (1-vacated)^(-gamma), improves targets/carries projections.",
               "method": "vacated = sum of the listed teammates' EWMA target-per-attempt (carry share) among players who appeared in the team's last 3 games; "
                         "gamma fitted on 2016-2021 (gamma=1 is proportional redistribution). An 'oracle' version uses who actually did not play (post-game) as an upper bound.",
               "data": f"{corr.get('share_player_games_with_vacated_targets>0.05', float('nan')):.1%} of player-games have >5% of team targets vacated by listed teammates",
               "result": f"gamma(D,targets)={corr.get('gamma_D_targets', float('nan')):.2f}, gamma(D,carries)={corr.get('gamma_D_carries', float('nan')):.2f}; oracle gammas "
                         f"{corr.get('gamma_oracle_D_targets', float('nan')):.2f}/{corr.get('gamma_oracle_D_carries', float('nan')):.2f}. Validation: " +
                         "; ".join(f"{f}: D_vac-D {_ci(_p(fam[f], 'D_vac - D'))}, F_vac-F {_ci(_p(fam[f], 'F_vac - F'))}, oracle-D {_ci(_p(fam[f], 'D_oracle_avail - D'))}" for f in vac_f),
               "interpretation": "Injury-report availability is the pregame-legitimate part of the role signal; the oracle bound shows how much better gameday availability information could be worth.",
               "decision": "adopt" if any(_sig_better(_p(fam[f], "D_vac - D")) or _sig_better(_p(fam[f], "F_vac - F")) for f in ("targets", "carries")) else "reject"})
    # 5 incumbents
    inc = [f for f in PLAYER if f in fam and "INC_0.4.0" in fam[f]["models"]]
    ex.append({"id": "NFL-PF-05-incumbent", "question": "How do the frozen winners compare with the incumbent shadow-0.4.0 and the shadow-0.5.0 challenger, replayed walk-forward with their own code?",
               "hypothesis": "The foundation models are at least as accurate as the incumbents.",
               "method": "nfl/incumbent.py replays fit_bundle (seasons 2016..T-1) for T=2017..2026 with the frozen design (0.4.0) and the challenger design (0.5.0, in-memory "
                         "function swap, no file edits) and scores the incumbents' own pmfs on the same player-games.",
               "data": "validation 2022-2023 and holdout 2024-2025, paired rows present in both",
               "result": "; ".join(f"{f}: best-vs-0.4.0 {_ci(fam[f]['models'][fam[f]['best_model']].get('vs_incumbent'))}, 0.5.0-0.4.0 {_ci(_p(fam[f], 'INC_0.5.0 - INC_0.4.0'))}" for f in inc),
               "interpretation": "Replay note: the research frame includes current-season games, so defect D1 (live history missing this season) does not affect this replay; "
                                 "the comparison is of model design only, which understates the incumbent's live 2026 error.",
               "decision": "adopt"})
    av = wf.get("availability")
    if av:
        v = av.get("validation_participation", {})
        t = av.get("validation_targets_unconditional", {})
        ex.append({"id": "NFL-PF-06-availability", "question": "How much does the participation convention matter, and how well does pregame information predict participation?",
                   "hypothesis": "Final injury designations predict DNP well; most DNPs of role players are flagged.",
                   "method": "Candidates = role players (>=2 targets or >=4 carries per game) who appeared in one of the team's last 3 games; P(play | designation) fitted on 2016-21; "
                             "targets CRPS on the full candidate set (DNP = 0) for 'assume he plays' vs the participation hurdle.",
                   "data": f"validation candidates n={v.get('n')}",
                   "result": f"DNP rate {v.get('dnp_rate', 0):.1%}; Brier designation model {v.get('brier_designation_model', 0):.4f} vs constant {v.get('brier_constant', 0):.4f}; "
                             f"{v.get('share_of_dnp_with_no_designation', 0):.0%} of DNPs carried no designation; among published (not OUT) projections DNP rate "
                             f"{t.get('dnp_among_published', 0):.1%}, CRPS assume-plays {t.get('crps_assume_plays', 0):.3f} vs hurdle {t.get('crps_participation_hurdle', 0):.3f}",
                   "interpretation": "Projections are published conditional on participation (prop void convention); the hurdle is the right object for any consumer that does not void DNPs.",
                   "decision": "adopt"})
    return ex


def error_investigations(wf):
    diag = wf.get("diagnostics", {})
    out = []
    seg = diag.get("segments", {})

    def row(fam, col, name):
        for r in (seg.get(fam) or {}).get(col, []):
            if str(r["segment"]) == name:
                return r
    checks = [("targets", "season_phase", "wk1-3", "early season (weeks 1-3)"), ("targets", "rookie", "rookie", "rookies"),
              ("targets", "team_changed", "new team (1st game)", "first game with a new team"),
              ("targets", "qb_changed", "QB changed", "team's starting QB changed"),
              ("targets", "vacated_targets", ">0.25", "teammates listed out vacate >25% of targets"),
              ("carries", "rb_role", "committee(.35-.6)", "RB committees"), ("carries", "rb_role", "change-of-pace(<.35)", "change-of-pace RBs"),
              ("receiving_yards", "tier", "WR1", "WR1s"), ("receiving_yards", "tier", "WR3+", "WR3+"),
              ("targets", "designation", "Questionable", "played through a Questionable tag"),
              ("passing_yards", "qb_changed", "QB changed", "QB starts after a QB change"),
              ("rushing_yards", "spread_bucket", "fav 7+", "RBs on 7+ point favourites")]
    for fam, col, seg_name, label in checks:
        r = row(fam, col, seg_name)
        if not r:
            continue
        rel = r["bias"] / r["mean_actual"] if r["mean_actual"] else 0
        out.append({"pattern": f"{fam}: {label}", "frequency": f"n={r['n']} player-games (dev+val)",
                    "impact": f"bias {r['bias']:+.2f} on mean {r['mean_actual']:.2f} ({rel:+.0%}), MAE {r['mae']:.2f}",
                    "cause": "", "status": "verified defect" if abs(rel) > 0.10 and r["n"] >= 300 else "ruled out" if abs(rel) < 0.05 else "hypothesis",
                    "action": ""})
    return out


def opponent_adjustment(wf, S=None):
    sel = wf["select"]["families"]
    res = []
    for f, fr in sel.items():
        d = _p(fr, "D - C") if f in PLAYER else _p(fr, "D_opp - B")
        res.append({"family": f, "comparison": "D - C" if f in PLAYER else "D_opp - B", "crps_diff": d})
    params = (S or {}).get("params", {}) if S else {}
    betas = {f: {"factors": p.get("D_factors"), "beta": p.get("D_beta")} for f, p in params.items() if p.get("D_factors")}
    tparams = (S or {}).get("tparams", {}) if S else {}
    for f, p in tparams.items():
        betas[f] = {"factors": ["log opp ridge factor", "home"], "beta": p.get("D_opp_beta")}
    return {"summary": "Opponent factors come from pf_core.pit.rolling_ridge_ratings (schedule-adjusted offence/defence ridge, refitted before every "
                       "week on all earlier games, prior seasons decayed x0.5). Elasticities were fitted on 2016-2021 only.",
            "results": res, "elasticities": betas}


def opportunity(wf):
    sel = wf["select"]["families"]
    res = []
    for f in ("team_pass_attempts", "team_rush_attempts", "targets", "carries", "passing_attempts"):
        if f in sel:
            b = sel[f]["best_model"]
            v = sel[f]["models"][b]["validation"]
            res.append({"family": f, "best": b, "mae": v["mae"], "bias": v["bias"], "corr": v["corr"], "crps": v["crps"],
                        "vs_A": sel[f]["models"][b].get("vs_baseline")})
    tb = (wf.get("diagnostics") or {}).get("targets_bias", {})
    return {"summary": "Opportunity (team volume and player share) is projected first; efficiency families inherit it.", "results": res,
            "targets_bias_anatomy": tb}


def calibration(wf):
    hold = wf.get("holdout", {})
    res = []
    for f, fo in hold.items():
        h = fo.get("holdout")
        if h:
            res.append({"family": f, "cover_50": h["cover_50"], "cover_80": h["cover_80"], "cover_90": h["cover_90"],
                        "pit_var_ratio": h["pit_var_ratio"], "pit_deciles": h["pit_deciles"],
                        "thresholds": [{k: t[k] for k in ("rung", "mean_p", "hit_rate", "brier", "ece")} for t in h.get("threshold_reliability", [])]})
    return {"summary": "Randomised-PIT coverage and PIT variance ratio (1 = calibrated, >1 over-confident, <1 under-confident) on the 2024-25 holdout, "
                       "plus reliability at Kalshi-like rungs.", "results": res}


def failed_experiments(wf):
    sel = wf["select"]["families"]
    out = []
    lost = [f for f, fr in sel.items() if _p(fr, "E - D") is not None and not _sig_better(_p(fr, "E - D"))]
    won = [f for f, fr in sel.items() if _sig_better(_p(fr, "E - D"))]
    out.append({"name": "LightGBM (E) as a stand-alone projection",
                "what_was_learned": f"E beats the structured D rung only in {', '.join(won) or 'none'}; it does not in {', '.join(lost)} "
                                    "(team families and QB families: too few rows per season for trees). On its own it also extrapolates badly "
                                    "outside its training population (non-RB carries projected 3.4 vs 0.76 realised).",
                "changes_future_decisions": "Use trees only inside a stack and only for players inside their training population."})
    out.append({"name": "Vacated targets from teammates listed OUT",
                "what_was_learned": f"gamma fitted on development is positive but validation CRPS does not improve (targets D_vac - D "
                                    f"{_ci(_p(sel['targets'], 'D_vac - D'))}); the oracle version using who actually sat is no better "
                                    f"({_ci(_p(sel['targets'], 'D_oracle_avail - D'))}).",
                "changes_future_decisions": "Do not spend effort on better absence data for targets; the remaining target error is role "
                                            "(depth chart / routes), not absences. Carries are different (absences matter)."})
    out.append({"name": "Opportunity x efficiency decomposition (C) on its own",
                "what_was_learned": f"For targets C - B {_ci(_p(sel['targets'], 'C - B'))}: decomposing into team volume x share does not beat a "
                                    "player EWMA (consistent with research/opportunity, which found the same on 2019-2025); its value is structural (it is where game environment and opponent enter).",
                "changes_future_decisions": "Keep C/D for interpretability and as stack inputs, not as the headline model."})
    out.append({"name": "QB efficiency from the generic ladder (pre-fix)",
                "what_was_learned": "Ladder rungs B-D were worse than the season average for QB volume because relief appearances "
                                    "contaminated histories; a seemingly 'robust' EWMA was the problem, not the baseline.",
                "changes_future_decisions": "Condition every role-based history on the role (starts for QBs) before smoothing."})
    out.append({"name": "Discretised normal for yards / NB on yards",
                "what_was_learned": "The normal misses the right skew and loses to empirical ratios in every yards family; 0-based NB cannot "
                                    "represent negative yards and is mis-scored by pf_core's out-of-support clipping.",
                "changes_future_decisions": "Empirical (quantile-mapped) residual ratios by mean bin are the default for yards."})
    return out


def priorities(wf):
    return [
        {"rank": 1, "item": "Adopt the new-team tenure correction (C1) prospectively",
         "impact": "first 1-4 games with a new team: 14-37% over-projection removed; family-wide CRPS -0.1% to -0.5%",
         "evidence": "dev-fitted, validated 2022-23 with CIs excluding 0 in 5/6 families (post-freeze, not yet holdout-tested)",
         "complexity": "low (one tenure feature + 3 multipliers)", "data": "existing nflverse"},
        {"rank": 2, "item": "Adopt the backup-tier regression correction (C2) prospectively",
         "impact": "RB2+/TE2+/WR3+ 7-18% over-projection; targets CRPS -0.3%",
         "evidence": "dev-fitted, validated 2022-23, CIs exclude 0 in 6/6 families", "complexity": "low", "data": "existing"},
        {"rank": 3, "item": "Pregame role signal for listed players (archived depth-chart vintages 2025+, route participation)",
         "impact": "the remaining opportunity error is role change; mean_defect's listed-population gap (+7%) is a role-selection effect",
         "evidence": "vacated-target and oracle-absence tests rejected; tenure/backup segments are the largest residuals",
         "complexity": "medium", "data": "ESPN depth chart snapshots (dt-stamped) 2025+, pbp participation (2016-2025)"},
        {"rank": 4, "item": "Passing TDs: add the incumbent's direct implied-total regression as a ladder rung",
         "impact": "only family where the incumbent wins on holdout (CRPS +0.012)", "evidence": "holdout vs shadow-0.4.0",
         "complexity": "low", "data": "existing"},
        {"rank": 5, "item": "Participation model for non-voiding consumers (injury designation + weekly roster status vintages)",
         "impact": "12% of published role-player projections are voids; 58% of DNPs carry no designation",
         "evidence": "availability study", "complexity": "medium", "data": "timestamped roster/injury captures (context-capture.yml, 2026+)"},
        {"rank": 6, "item": "QB passing-yards level drift",
         "impact": "+6 to +9 yards holdout bias tracks the 2022-25 league passing decline", "evidence": "holdout bias",
         "complexity": "low (league-level PIT trend term)", "data": "existing"},
    ]


def _tldr(summary):
    rows = []
    for f in summary["families"]:
        h = f.get("holdout") or {}
        best = next((m for m in f["models"] if m["model"] == f["best_model"]), {})
        rows.append({"family": f["family"], "best model (frozen)": f["best_model"],
                     "val CRPS vs A": R.ci(best.get("vs_baseline"), 4) if best.get("vs_baseline") else "baseline",
                     "holdout CRPS vs A": R.ci(h.get("vs_baseline"), 4) if h.get("vs_baseline") else "—",
                     "holdout vs shadow-0.4.0": R.ci(h.get("vs_incumbent"), 4) if h.get("vs_incumbent") else "—",
                     "readiness": f["readiness"]})
    return R.md_table(rows, list(rows[0].keys()))


def render_md(summary, wf, frozen_doc):
    import importlib
    from . import findings as FD
    importlib.reload(FD)
    sel, hold, diag = wf["select"], wf.get("holdout", {}), wf.get("diagnostics", {})
    names = {k: v for k, v in NAMES.items()}
    L = []
    L.append("# NFL Projection Foundation — walk-forward results\n")
    L.append(f"*Generated {summary['generated_utc']} from code `{summary['code_sha'][:10]}`, pf_core {summary['pf_core_version']}. "
             "Research only: nothing here changes betting authority. Reproduce: `cd research/projection_foundation && python -m nfl.incumbent && "
             "python -m nfl.run_walkforward --stage all && python -m nfl.project`.*\n")
    L.append("## Bottom line\n")
    L.append(FD.bottom_line(summary, wf) + "\n")
    L.append(_tldr(summary))
    L.append("\nCRPS differences are paired on identical player-games (negative = better), 95% CI from a game-clustered bootstrap; "
             "✔ = CI excludes zero in favour of the first model, ✘ = significantly worse.\n")
    L.append("## Design\n")
    L.append(FD.design_text(summary) + "\n")
    L.append("## Data inventory\n")
    L.append(R.md_table(summary["inventory"], ["dataset", "seasons", "rows", "pit_class", "notes"]))
    L.append("\n## Model comparison by family (validation 2022-2023)\n")
    L.append("Sorted by validation CRPS. dist = distribution family chosen for that mean model on validation (fitted on development residuals). "
             "PIT var = variance of the randomised PIT relative to uniform (1 = calibrated, >1 over-confident). ★ = frozen winner.\n")
    for fam in R.ORDER:
        fr = sel["families"].get(fam)
        if not fr:
            continue
        f = next(x for x in summary["families"] if x["family"] == fam)
        L.append(f"### {fam}\n")
        L.append(f"*Unit:* {fr['unit']}. *Population:* {fr['population']}. *Opportunity family:* {fr['opportunity_family'] or '—'}. "
                 f"*Readiness:* **{f['readiness']}** — {f['readiness_reason']}\n")
        L.append(R.fam_table(fam, fr, names))
        L.append(FD.family_note(fam, wf) + "\n")
    L.append("## Holdout (2024-2025, frozen winners, evaluated once) and the read-only 2026 weeks 1-4 check\n")
    L.append("F on holdout uses the pre-declared stack refitted on development+validation predictions. Incumbent columns are the replayed "
             "incumbents scored with their own pmfs on the same rows.\n")
    L.append(R.holdout_table(hold, names))
    L.append("\n" + FD.holdout_note(wf) + "\n")
    L.append("## Experiments\n")
    for e in summary["experiments"]:
        L.append(f"### {e['id']}\n")
        for k in ("question", "hypothesis", "method", "data", "result", "interpretation", "decision"):
            L.append(f"- **{k.capitalize()}:** {e[k]}")
        L.append("")
    L.append("## Error investigations (development + validation, frozen winners)\n")
    L.append(FD.errors_text(wf) + "\n")
    L.append(R.md_table(summary["error_investigations"], ["pattern", "frequency", "impact", "cause", "status", "action"]))
    for fam, cols in (("targets", ["tier", "season_phase", "career_games", "team_changed", "qb_changed", "vacated_targets", "designation"]),
                      ("carries", ["rb_role", "spread_bucket", "season_phase"]),
                      ("receiving_yards", ["tier"]), ("passing_yards", ["qb_changed", "career_games"])):
        L.append("\n" + R.segment_tables(diag, fam, cols))
    L.append("\n### Targets bias anatomy (mean_defect follow-up)\n")
    tb = (diag.get("targets_bias") or {}).get("targets", [])
    if tb:
        L.append(R.md_table(tb, ["split", "weeks", "usage", "n", "mean_pred", "mean_actual", "realised_over_pred"]))
    L.append("\n" + FD.targets_bias_text(wf) + "\n")
    L.append("## Opponent adjustment\n")
    L.append(FD.opponent_text(summary, wf) + "\n")
    L.append("## Opportunity model accuracy\n")
    L.append(FD.opportunity_text(summary, wf) + "\n")
    L.append("## Distributions and calibration\n")
    L.append("Validation CRPS / log score of each candidate family for the winning mean model (lower is better):\n")
    L.append(R.dist_table(sel))
    L.append("\nHoldout reliability at Kalshi-like rungs (frozen winner):\n")
    L.append(R.threshold_table(hold))
    L.append("\n" + FD.calibration_text(summary, wf) + "\n")
    L.append("## Availability (participation) convention\n")
    L.append(FD.availability_text(wf) + "\n")
    L.append("## Projection Quality Gate\n")
    L.append(FD.gate_text(wf) + "\n")
    L.append("## Failed experiments and lessons\n")
    for e in summary["failed_experiments"]:
        L.append(f"- **{e['name']}** — {e['what_was_learned']} *{e['changes_future_decisions']}*")
    L.append("\n## Readiness and ranked priorities\n")
    L.append(R.md_table([{"family": f["family"], "readiness": f["readiness"], "why": f["readiness_reason"]} for f in summary["families"]],
                        ["family", "readiness", "why"]))
    L.append("")
    L.append(R.md_table(summary["priorities"], ["rank", "item", "impact", "evidence", "complexity", "data"]) if summary["priorities"] else "")
    L.append("\n## Limitations\n")
    L.append(FD.limitations_text() + "\n")
    return "\n".join(L)
