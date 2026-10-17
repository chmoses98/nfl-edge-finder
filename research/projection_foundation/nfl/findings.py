"""Hand-written interpretation for RESULTS_NFL.md. Numbers that change with data are pulled from the results at render
time; numbers quoted from one-off development diagnostics are labelled with their source and window."""
from __future__ import annotations

from . import render as R


def _h(wf, fam, split="holdout"):
    return (wf.get("holdout", {}).get(fam) or {}).get(split) or {}


def _ci(d, nd=4):
    return R.ci(d, nd) if d else "n/a"


def bottom_line(summary, wf):
    fams = summary["families"]
    ready = [f["family"] for f in fams if f["readiness"] == "READY"]
    shadow = [f["family"] for f in fams if f["readiness"] == "SHADOW VALIDATION"]
    need = [f["family"] for f in fams if f["readiness"] == "NEEDS IMPROVEMENT"]
    beat_inc = [f for f in ("targets", "receptions", "receiving_yards", "carries", "rushing_yards", "passing_attempts", "completions",
                            "passing_yards", "passing_tds", "anytime_td") if _h(wf, f).get("vs_INC_0.4.0") and _h(wf, f)["vs_INC_0.4.0"]["ci95"][1] < 0]
    lose_inc = [f for f in ("passing_tds",) if _h(wf, f).get("vs_INC_0.4.0") and _h(wf, f)["vs_INC_0.4.0"]["ci95"][0] > 0]
    t = _h(wf, "targets")
    return "\n".join([
        f"- **Every frozen winner beat the season-average baseline on the untouched 2024-25 holdout** (13/13 families, game-clustered 95% CIs exclude 0). "
        f"Against the incumbent `shadow-0.4.0` replayed walk-forward with its own code, the frozen winners are significantly better in "
        f"{len(beat_inc)} of 10 player families ({', '.join(beat_inc)}), tied on passing yards, and **worse on passing TDs** ({', '.join(lose_inc) or 'none'}).",
        f"- Biggest gains are on opportunity: targets CRPS {t.get('crps', 0):.3f} vs {t.get('INC_0.4.0', {}).get('crps', 0):.3f} for shadow-0.4.0 "
        f"(holdout), driven by a LightGBM rung refitted every season and stacked with the structured opportunity x efficiency model.",
        "- Readiness: READY — " + (", ".join(ready) or "none") + "; SHADOW VALIDATION — " + (", ".join(shadow) or "none") +
        "; NEEDS IMPROVEMENT — " + (", ".join(need) or "none") + ".",
        "- Verified defects found and fixed before the freeze: (1) QB volume was under-projected ~5% because a QB's history included relief/"
        "garbage-time appearances (fixed with starts-only history + implied-total term); (2) players who play through a Questionable tag produce "
        "~7-12% below projection, and teammates listed OUT redistribute carries (not targets) — both now in the 'availability' rung.",
        "- Verified defects found AFTER the freeze (pre-registered, not adopted): a player's first games with a new team are over-projected "
        "14-37% on development (rushing yards +99% on 2022-23), and backup tiers (RB2+/TE2+/WR3+) are over-projected 7-18%. Dev-fitted corrections improve "
        "validation CRPS with CIs excluding 0; they wait for untouched data before adoption.",
        "- Distributions are calibrated: holdout 80% coverage 0.79-0.82 and PIT variance ratios 0.95-1.03 in every family. The gate's real value "
        "was catching two publication defects (pmf mean vs published mean; E/F extrapolation outside their training population), not "
        "flagging larger errors — REVIEW projections carry only ~4% higher CRPS on validation and none on holdout.",
        "- Nothing here is a betting claim: the foundation measures projection accuracy; betting authority is unchanged.",
    ])


def design_text(summary):
    sp = summary["splits"]
    return "\n".join([
        f"- **Splits (chronological, frozen before evaluation):** development {sp['development']}; validation {sp['validation']}; "
        f"holdout {sp['holdout']}; {sp['check_2026']}; {sp['embargo']}. All tuning (shrinkage k, EWMA halflife, elasticities, stack weights, "
        "distribution parameters) uses development rows only; validation picks the model and the distribution family; the holdout was scored "
        "once, after `results/nfl_frozen_selection.json` had been committed (commit aba4cdc precedes the holdout run).",
        "- **Point-in-time features:** every feature at game g uses only games that kicked off earlier (pf_core.pit.lagged_features shifts within "
        "player/team; rolling ridge opponent ratings are refitted before every (season, week) block; positional priors are expanding means over "
        "earlier weeks). Pregame market context = closing spread/total from the nflverse schedule. `tests/test_nfl_pf.py` asserts that changing "
        "a game's outcome cannot change any feature of that game or earlier.",
        "- **Walk-forward:** A-D are formula models evaluated sequentially with frozen hyperparameters; E (LightGBM) is refitted before every "
        "season on all earlier seasons (2013+), so every 2016-2026 prediction is out-of-sample; F stacks B, C, D, E with non-negative weights "
        "fitted on development predictions (holdout uses the pre-declared refit on development + validation). The incumbents are refitted the "
        "same way (seasons 2016..T-1) with their own frozen code (`nfl/incumbent.py`, in-memory challenger swap, no file edits).",
        "- **Availability:** player metrics are conditional on participation (>= 1 offensive snap or a stat line), the prop-settlement "
        "convention (DNP = void). 'Did he play' is post-game, so it is never a feature; participation is modelled separately from the final "
        "injury designation (see Availability) and its effect quantified.",
        "- **Populations (point-in-time):** receiving families = RB/WR/TE averaging >= 2 targets over their previous 4 games played; "
        "rushing families = RBs averaging >= 4 carries; QB families = the scheduled starter; anytime TD = RB/WR/TE meeting either role rule. "
        "A player's first career game is outside these populations by construction (no history).",
        "- **Metrics:** MAE/RMSE/bias of the mean; CRPS and log score of the full integer distribution; randomised-PIT coverage; Brier at "
        "Kalshi-like rungs. Every comparison is paired on identical player-games with a game-clustered bootstrap (pf_core.metrics).",
    ])


def family_note(fam, wf):
    sel = wf["select"]["families"][fam]
    p = sel.get("pairs", {})
    notes = {
        "team_pass_attempts": "Team pass volume is barely spread-dependent in aggregate (2016-21: 34.0 attempts as a 7+ point dog vs 34.6 as a "
                              "7+ favourite); the gain comes from the schedule-adjusted opponent factor (D_opp - B "
                              f"{_ci(p.get('D_opp - B'))}) and the total.",
        "team_rush_attempts": f"Game script matters for rushing: 24.4 rush attempts as a 7+ dog vs 28.5 as a 7+ favourite (2016-21). D - D_opp {_ci(p.get('D - D_opp'))}.",
        "team_points": f"The closing implied total is the information: D (B x opponent x implied/B) has elasticity ~1.05 on the implied total; "
                       f"MKT - D {_ci(p.get('MKT - D'))}. Treat as a sanity anchor, not an independent forecast.",
        "targets": f"E (LightGBM) is the single best rung (E - D {_ci(p.get('E - D'))}); the opponent term adds nothing for targets "
                   f"(D - C {_ci(p.get('D - C'))}); the availability rung's gain is not significant for targets (F_av - F {_ci(p.get('F_av - F'))}) but is for receptions and receiving yards.",
        "receptions": f"Inherits targets; catch rate x opponent factor is a small gain (D - C {_ci(p.get('D - C'))}).",
        "receiving_yards": f"Opponent yards-per-target factor helps (D - C {_ci(p.get('D - C'))}); the stack beats E (F - E {_ci(p.get('F - E'))}).",
        "carries": f"Vacated carries from teammates listed OUT/DOUBTFUL is a real signal (D_vac - D {_ci(p.get('D_vac - D'))}), unlike targets.",
        "rushing_yards": f"Largest relative gain over the incumbent among yardage families; vacated carries D_vac - D {_ci(p.get('D_vac - D'))}.",
        "passing_attempts": f"QB starts-only fix: D_qs - D {_ci(p.get('D_qs - D'))}, F_qs - F {_ci(p.get('F_qs - F'))}. Validation gain over A is not significant (A is a strong baseline for QB volume).",
        "completions": f"QB starts-only fix: F_qs - F {_ci(p.get('F_qs - F'))}.",
        "passing_yards": f"QB starts-only + implied-total fix: D_qs - D {_ci(p.get('D_qs - D'))}; ties the incumbent (F_qs - INC {_ci(p.get('F_qs - INC_0.4.0'))}). "
                         "Remaining positive bias (+6 to +9 yards) tracks the 2022-25 league-wide fall in passing yards.",
        "passing_tds": f"No rung separates from the others (D_qs - D {_ci(p.get('D_qs - D'))}); the incumbent's OLS on implied total is better on holdout.",
        "anytime_td": f"All structured rungs are within noise of the incumbent's direct binary model (F_av vs incumbent {_ci(sel['models'][sel['best_model']].get('vs_incumbent'))}).",
    }
    return notes.get(fam, "")


def holdout_note(wf):
    return ("The 2026 weeks 1-4 check (read-only; never tuned on) agrees in direction with the holdout for every player family; it is too small "
            "(124 QB starts, 743 receiving player-games) to be decisive on its own. Team rush attempts were worse than baseline on 2026 weeks 1-4 "
            "(not significant), the only sign flip.")


def errors_text(wf):
    c = wf.get("candidates_post_freeze", {})
    tb = c.get("tenure_bias", {})

    def row(fam, b, sp):
        for r in tb.get(fam, []):
            if r["games_with_team"] == b and r["split"] == sp:
                return f"{r['rel_bias']:+.0%} (n={r['n']})"
        return "n/a"

    def cand(cn, fam):
        v = (c.get(cn) or {}).get(fam)
        if not v:
            return "n/a"
        return f"all {_ci(v['val_crps_diff_all'])}, segment {_ci(v['val_crps_diff_segment'])}"
    return "\n".join([
        "Method: per-segment bias/MAE of the frozen winner on development + validation player-games (`pf_core.metrics.segment_table`), "
        "segments defined only from pregame information; causes tested on development, corrections validated on 2022-23.",
        "",
        "1. **QB history polluted by non-starts (verified, fixed pre-freeze).** 18% of QB rows are not the scheduled starter (6.5 attempts on "
        "average vs 33.1). On 2016-21 starts whose previous 4 games include a non-start, D projected 189.8 passing yards vs 209.9 realised "
        "(attempts 27.2 vs 31.4); with clean histories D still under-projected 237.7 vs 247.6, and the gap grew with the implied total "
        "(193 vs 193 at <=18 points, 263 vs 278 at 27+). Fix = starts-only history + implied-total elasticity (`nfl/qb_fix.py`).",
        "2. **Playing through a Questionable tag (verified, fixed pre-freeze).** Role players tagged Questionable who play realise 0.91x their "
        "projection (availability study, n=1,603); dev-fitted haircuts are 7-12% for receiving volume and 18% on the TD intensity.",
        "3. **Teammate absences (verified for carries, ruled out for targets).** Renormalising for teammates listed OUT/DOUBTFUL helps carries "
        "and rushing yards with CIs excluding 0 but not targets: target trees already re-allocate through recent role, and an 'oracle' using "
        "who actually sat (post-game) is no better — absent teammates' roles are already absorbed into the others' recent history.",
        "4. **First games with a new team (verified, NOT adopted — found after the freeze).** Over-projection by games with the current team, "
        f"development / validation: targets k=0 {row('targets', '0', 'dev')} / {row('targets', '0', 'val')}, k=1 {row('targets', '1', 'dev')} / {row('targets', '1', 'val')}; "
        f"receiving yards k=0 {row('receiving_yards', '0', 'dev')} / {row('receiving_yards', '0', 'val')}; rushing yards k=0 {row('rushing_yards', '0', 'dev')} / "
        f"{row('rushing_yards', '0', 'val')}; anytime TD k=0 {row('anytime_td', '0', 'dev')} / {row('anytime_td', '0', 'val')}. "
        f"Candidate C1 (tenure multipliers fitted on dev) on validation: targets {cand('C1', 'targets')}; rushing yards {cand('C1', 'rushing_yards')}.",
        f"5. **Backup tiers regress (verified, NOT adopted).** RB2+/TE2+ targets +13%/+16%, WR3+ +7%: players enter the population after a "
        f"hot stretch (>= 2 targets over 4 games) and regress. Candidate C2 on validation: targets {cand('C2', 'targets')}; receiving yards {cand('C2', 'receiving_yards')}.",
        "6. **Early season, rookies, QB changes: no material defect.** Weeks 1-3 bias +1% on targets (the incumbent's -11 to -14% early-season "
        "gap from mean_defect D2 does not exist in this design); rookies after their first game -2% to +1%; receivers after a QB change +3% "
        "targets / +6% receiving yards (minor).",
        "7. **Game script:** projections on 7+ point underdogs run +4-5% high on targets/receiving yards/passing yards; favourites are "
        "unbiased. Small, plausibly the spread effect being under-weighted at the player level.",
    ])


def targets_bias_text(wf):
    return ("research/mean_defect found shadow-0.4.0 under-projecting targets 11-14% in weeks 1-6 and a residual under-prediction on the "
            "*listed* (Kalshi) population. On the uncontaminated population used here the frozen model shows realised/projected 0.96-1.00 in "
            "weeks 1-6 of 2016-21 and 0.98-1.00 in 2026 weeks 1-4 at every usage tier — no early-season opportunity deficit. The direction "
            "is the opposite at low usage (EWMA < 3: realised/projected 0.87-0.96), i.e. regression of fringe players, not missing opportunity. "
            "So the remaining listed-population gap in mean_defect is a listing-selection effect (the exchange lists players whose role the "
            "box-score history has not yet caught up with), consistent with that study's conclusion; it is not a defect of an "
            "opportunity model on representative data. Remedy: a pregame role signal (depth chart vintages, route participation) — see priorities.")


def opponent_text(summary, wf):
    oa = summary["opponent_adjustment"]
    rows = []
    for r in oa["results"]:
        rows.append({"family": r["family"], "comparison": r["comparison"], "validation CRPS diff": _ci(r["crps_diff"])})
    el = oa.get("elasticities", {})
    erows = [{"family": f, "factors": ", ".join(map(str, v.get("factors") or [])), "beta (dev)": ", ".join(f"{b:+.2f}" for b in (v.get("beta") or []))}
             for f, v in el.items()]
    return (oa["summary"] + " Negative = adjusted model better.\n\n" + R.md_table(rows, ["family", "comparison", "validation CRPS diff"]) +
            "\n\nFitted elasticities (1.0 = full pass-through of the schedule-adjusted factor; 0 = no effect):\n\n" +
            R.md_table(erows, ["family", "factors", "beta (dev)"]) +
            "\n\nReading: at the team level the opponent adjustment is worth ~0.5-1% CRPS on volume and the closing line carries most of the "
            "points signal. At the player level, opponent efficiency factors help receiving yards and rushing yards modestly and do nothing "
            "for targets; elasticities well below 1 say raw opponent splits over-state matchup effects even after schedule adjustment.")


def opportunity_text(summary, wf):
    rows = []
    for r in summary["opportunity"]["results"]:
        rows.append({"family": r["family"], "best": r["best"], "val MAE": round(r["mae"], 3), "val bias": round(r["bias"], 3),
                     "corr(pred, actual)": round(r["corr"], 3), "val CRPS": round(r["crps"], 4), "vs A": _ci(r.get("vs_A"))})
    return (R.md_table(rows, list(rows[0].keys())) + "\n\nTeam volume is projected to within ~6 pass attempts and ~5.5 rush attempts MAE; "
            "the team volume x share decomposition (C) on its own is no better than a player EWMA (B) for targets, but it is what lets the "
            "game environment and opponent enter (D), and as a stack component it carries 15-50% weight.")


def calibration_text(summary, wf):
    return ("Distribution choice (validation CRPS, fitted on development residuals): NB with mean-binned dispersion wins for targets and "
            "receptions; an empirical ratio (quantile-mapped residual ratios by mean bin) wins for receiving/rushing yards, carries, QB counts "
            "and passing TDs; Bernoulli for anytime TD. The discretised normal never wins for yards (it misses the right skew). Over/under-"
            "confidence on the holdout is small: PIT variance ratios 0.95-1.03 (slightly under-confident where < 1). Role-specific tails "
            "(validation): WR1 100+ receiving yards projected 17.0% vs 19.9% realised (under-confident at the top), workhorse RBs 100+ rushing "
            "24.7% vs 17.8% (over-confident, n=219), backup TEs/RBs at high rungs slightly over-confident (1-2 pp). "
            "Projections publish the pmf's own mean: for empirical-ratio families the raw model mean and the pmf mean differ by >5% for "
            "16-32% of rows (mostly low volume), and the pmf mean is the more accurate of the two (receiving yards MAE 21.01 vs 21.11).")


def availability_text(wf):
    av = wf.get("availability") or {}
    v = av.get("validation_participation", {})
    t = av.get("validation_targets_unconditional", {})
    d = av.get("dev_play_rate_by_designation", {})
    pt = av.get("played_through_designation_bias", {}).get("Questionable", {})
    return "\n".join([
        "Convention: player projections are conditional on participation (DNP = void, as props settle). 'Played' is never a feature.",
        f"- Role-player candidates (pregame-definable) miss {v.get('dnp_rate', 0):.1%} of games (validation). Final designations predict it: "
        f"P(play) Out {d.get('Out', {}).get('p_play', 0):.3f}, Doubtful {d.get('Doubtful', {}).get('p_play', 0):.3f}, "
        f"Questionable {d.get('Questionable', {}).get('p_play', 0):.3f}, none {d.get('None', {}).get('p_play', 0):.3f} (development); "
        f"Brier {v.get('brier_designation_model', 0):.4f} vs {v.get('brier_constant', 0):.4f} for a constant.",
        f"- But {v.get('share_of_dnp_with_no_designation', 0):.0%} of DNPs carry no designation (IR moves, releases, healthy scratches, "
        "demotions): the weekly injury report alone cannot produce an unconditional projection. Weekly roster status would catch IR moves but "
        "its snapshot time is unknown (retrospective), so it is used only for the forward candidate list.",
        f"- Effect of the convention on targets (validation, projections published for everyone not listed OUT, DNP scored as 0): "
        f"{t.get('dnp_among_published', 0):.1%} of published projections would be voids; assuming participation gives CRPS "
        f"{t.get('crps_assume_plays', 0):.3f} and bias {t.get('bias_assume_plays', 0):+.2f}, the participation hurdle gives "
        f"{t.get('crps_participation_hurdle', 0):.3f} and {t.get('bias_hurdle', 0):+.2f}. Consumers that do not void DNPs must use the hurdle.",
        f"- Conditional bias: players who play through a Questionable tag realise {pt.get('ratio_actual_to_proj', 0):.2f}x projection "
        f"(n={pt.get('n', 0)}); adopted as the own-designation term of the availability rung.",
    ])


def gate_text(wf):
    g = wf.get("gate") or {}
    pv = g.get("pooled", {}).get("validation", {})
    ph = g.get("pooled", {}).get("holdout", {})
    nv = (g.get("naive_model_mean_validation") or {}).get("pooled", {}).get("validation", {})
    tr = g.get("team_reconciliation", {}).get("validation", {})
    rows = []
    for fam, v in g.get("by_family", {}).items():
        e = v["validation"]["error_by_status"]
        eh = v.get("holdout", {}).get("error_by_status", {})
        rows.append({"family": fam, "PASS n": e.get("PASS", {}).get("n", 0), "REVIEW n": e.get("REVIEW", {}).get("n", 0),
                     "BLOCK n": e.get("BLOCK", {}).get("n", 0), "REVIEW rel CRPS (val)": round(e.get("REVIEW", {}).get("rel_crps", float("nan")), 2),
                     "REVIEW rel CRPS (holdout)": round(eh.get("REVIEW", {}).get("rel_crps", float("nan")), 2),
                     "checks (val)": ", ".join(f"{k}" for k in v["validation"]["summary"]["check_counts"])})
    return "\n".join([
        "Every validation and holdout projection of the frozen winners was run through `pf_core.gate.evaluate` with role-aware inputs "
        "(own last-8 opportunity and stat history, opponent games this season, final injury designation, the pmf and its rungs). "
        "Relative CRPS = CRPS / family mean CRPS (1.0 = average).",
        "",
        f"- Status rates (published = pmf mean): validation PASS {pv.get('PASS', {}).get('share', 0):.1%} / REVIEW {pv.get('REVIEW', {}).get('share', 0):.1%} "
        f"/ BLOCK {pv.get('BLOCK', {}).get('share', 0):.1%}; holdout PASS {ph.get('PASS', {}).get('share', 0):.1%} / REVIEW {ph.get('REVIEW', {}).get('share', 0):.1%}.",
        f"- Does REVIEW mean larger error? Barely: relative CRPS REVIEW {pv.get('REVIEW', {}).get('rel_crps', 0):.2f} vs PASS {pv.get('PASS', {}).get('rel_crps', 0):.2f} "
        f"on validation, {ph.get('REVIEW', {}).get('rel_crps', 0):.2f} vs {ph.get('PASS', {}).get('rel_crps', 0):.2f} on holdout. The role/confidence "
        "checks are informative for QBs (REVIEW rel CRPS 1.1-1.3) and targets (1.15) but not for the yardage families, where thin-history players "
        "are also low-volume players with small absolute errors. Verdict: as an error predictor the gate is weak; it should not be sold as one.",
        f"- What the gate did catch: with the raw model mean published, {nv.get('BLOCK', {}).get('share', 0):.1%} of validation projections were BLOCKed "
        "for 'distribution mean disagrees with published mean' (empirical-ratio pmfs do not preserve the model mean at low volume). Fixed by "
        "publishing the pmf's moments. Team reconciliation caught E/F extrapolating outside their training population: applying the frozen "
        f"carries model to every participant summed to {tr.get('naive_frozen_model_for_all_participants', {}).get('carries_ratio', 0):.2f}x the team's rush "
        f"attempts (BLOCK in {tr.get('naive_frozen_model_for_all_participants', {}).get('carries_status', {}).get('BLOCK', 0)} of {tr.get('n_team_games', 0)} team-games). "
        f"Population-aware sums (frozen model inside the population, B outside) reconcile at {tr.get('targets', {}).get('mean_ratio_proj', 0):.2f}x (targets) "
        f"and {tr.get('carries', {}).get('mean_ratio_proj', 0):.2f}x (carries) vs realised {tr.get('targets', {}).get('mean_ratio_actual', 0):.2f}/"
        f"{tr.get('carries', {}).get('mean_ratio_actual', 0):.2f}. Rule adopted: E/F are never published outside their training population.",
        "",
        R.md_table(rows, list(rows[0].keys())) if rows else "",
    ])


def limitations_text():
    return "\n".join([
        "- Injury designations carry no timestamp in nflverse (rebuilt in place); they are treated as near-pregame (final Friday report). "
        "A timestamped vintage exists only from the 2026 context capture. In the forward file, players on the week's report without a final "
        "designation yet are marked 'Pending' and gated REVIEW.",
        "- Conditional-on-participation evaluation: a consumer that does not void DNPs must use the participation hurdle (Availability section).",
        "- No route participation / personnel data was used (not downloaded); prior repo research found route share helps raw-EWMA targets.",
        "- The incumbent replay uses the research frame (current-season games included), so it measures the incumbent's design, not the live "
        "D1 history defect; its 2026 live error was larger (research/mean_defect). Incumbent pmfs live on 0..grid_max and were left-padded "
        "to the family support so negative-yard games are scored correctly.",
        "- pf_core issue (reported, not edited): `DistBatch._index` clips outcomes outside the support to the boundary, so `crps`/`logpmf` "
        "understate the loss of out-of-support outcomes (e.g. y=-5 on a 0-based pmf is scored as y=0; y above the support loses the lattice "
        "points beyond it). Worked around here by supports down to -20/-30 for yards, by dropping 0-based NB from the yards candidates, and by "
        "left-padding the incumbents' pmfs.",
        "- pf_core 1.0.0 look-ahead (reported by the coordinator; pf_core not edited): `models.group_prior_pit`'s default fallback and "
        "`pit.rolling_opponent_allowed`'s NaN league fill use the whole-sample mean. This study never calls rolling_opponent_allowed; every "
        "group_prior_pit call now passes an explicit warm-up-only (2012-2015) fallback. Audit of the committed run: the fallback was hit only by "
        "328 warm-up rows (2012 week 1, each position's first block) and by no development, validation or holdout row, so no reported number "
        "depends on it. The same audit found one whole-sample constant in this study's own code: the team-level C rung shrank pass rate toward "
        "the all-seasons mean (0.578; warm-up-only 0.582). C has zero weight in all three frozen team stacks and was never selected, so frozen "
        "winners and holdout numbers are unaffected; the team C rows in the tables carry this negligible look-ahead. Fixed in code for "
        "subsequent runs.",
        "- Selection used the minimum validation CRPS among 6-12 candidates per family; several winners beat the runner-up by less than the "
        "CI width (see per-family tables). The holdout is the honest estimate.",
        "- 2026 weeks >= 5 are the untouched market holdout and are never scored here; forward projections for them are archived by the workflow.",
    ])
