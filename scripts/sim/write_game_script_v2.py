#!/usr/bin/env python3
"""Render the GAME SCRIPT V2 / five-season study summaries from their JSON. One source of truth per number.

  baseline_5y.json + reproduction_2023_2025.json  -> BASELINE_5Y.md
  script_calibration_5y.json + validation_5y.json -> SCRIPT_CALIBRATION_5Y.md
  opponent_adjustment_ablation.json               -> OPPONENT_ADJUSTMENT_ABLATION.md
  validation_5y.json                              -> VALIDATION_5Y.md  (injury redistribution, weather)

tests/test_game_script_v2_results_consistency.py re-renders and compares, so a committed summary cannot drift from
its committed data. METHODOLOGY.md, LIMITATIONS.md and PREREGISTRATION.md are written by hand.

Usage: python scripts/sim/write_game_script_v2.py [--check]
"""
from __future__ import annotations
import argparse, json, os, sys
import numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
OUT = os.path.join(ROOT, "research", "game_script_v2")
FILES = ("BASELINE_5Y.md", "SCRIPT_CALIBRATION_5Y.md", "OPPONENT_ADJUSTMENT_ABLATION.md", "VALIDATION_5Y.md")
STATS = ["carries", "rush_yards", "targets", "receptions", "rec_yards", "attempts", "completions", "pass_yards", "pass_td", "any_td"]
HDR = "Generated from `{src}` by `scripts/sim/write_game_script_v2.py` -- do not edit by hand. **RESEARCH_ONLY: no betting authority.**"


def f(x, nd=3):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "—"
    return f"{x:.{nd}f}" if isinstance(x, (int, float)) and not isinstance(x, bool) else str(x)


def pct(x, nd=1):
    return "—" if x is None else f"{100 * x:.{nd}f}%"


def ci(d, nd=3, scale=1.0):
    if not d:
        return "—"
    return f"{d['mean'] * scale:.{nd}f} [{d['lo'] * scale:.{nd}f}, {d['hi'] * scale:.{nd}f}]"


def _load(name):
    p = os.path.join(OUT, name)
    return json.load(open(p)) if os.path.exists(p) else None


# --------------------------------------------------------------------------------------------- baseline
def _player_table(rec, L, pooled=False):
    L += ["| statistic | n | games | MAE | naive MAE | Δ% vs naive | RMSE | bias | CRPS | cover50 | cover90 | ladder Brier | randomized-PIT χ² (df 9) |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for st in STATS:
        r = rec["player"].get(st)
        if not r:
            continue
        L.append(f"| {st} | {r['n']} | {r['n_games']} | {f(r['mae'])} | {f(r.get('baseline_mae'))} | {f(r.get('mae_vs_baseline_pct'), 1)} | "
                 f"{f(r['rmse'])} | {f(r['bias'])} | {f(r['crps'])} | {f(r['cover50'])} | {f(r['cover90'])} | {f(r.get('ladder_brier'), 4)} | "
                 f"{f(r['randomized_pit']['chi2'], 1)} |")
    L.append("")


def render_baseline(b: dict) -> str:
    m = b["meta"]
    L = ["# Five-season baseline of the frozen incumbent simulation (2021-2025)", "",
         HDR.format(src="baseline_5y.json"), "",
         f"Reproduce: `{m['command']}` (equivalent to `{m['equivalent_to']}`), then "
         "`python scripts/sim/game_script_v2_report.py baseline`. Starting point: `main` at "
         f"`{m['start_main_sha']}`. {m['n_sims']:,} simulated rows per game; game-clustered bootstrap "
         f"({m['bootstrap']['resamples']} resamples, seed {m['bootstrap']['seed']}).", "",
         "Walk-forward exactly as the incumbent: for evaluation season Y the shrinkage priors are fitted on 2016..Y-1, the "
         "frames are rebuilt for Y, the bundle is fitted on 2018..Y-1 (2016-17 warm the EWMAs), every completed game of Y is "
         "simulated with the consensus CLOSING line as the market centre, and every (game, player, statistic) row is scored "
         "against the box score. Nothing was tuned on these results.", "",
         "## Evidence classes", "", "| season | class | games | simulated | skipped | coherence failures | bundle trained on | priors fitted on |",
         "|---|---|---|---|---|---|---|---|"]
    for y, r in b["by_season"].items():
        run = r["run"]
        L.append(f"| {y} | {r['evidence_class']} | {run['games']} | {run['games_simulated']} | {len(run['skipped'])} | "
                 f"{run['coherence_failures']} | {min(r['train_seasons'])}-{max(r['train_seasons'])} | "
                 f"{min(r['priors_fit_seasons'])}-{max(r['priors_fit_seasons'])} |")
    L += ["", "2022 has 284 games: the cancelled Week 17 BUF @ CIN game is not in the nflverse schedule (never played; not an "
          "exclusion). 2021-2022 are a RETROSPECTIVE CHALLENGE set -- never scored by this layer before, but every design choice "
          "was available when they were run. Nothing here is prospective evidence.", "",
          "## Reproduction of the committed 2023-2025 run", "", b["reproduction"]["diagnosis"], "",
          "| season | bundle components that moved | other_share committed → reproduced (carry / target) | team stats that moved | max |rel. change| MAE / CRPS / cover90 |",
          "|---|---|---|---|---|"]
    for y, r in b["reproduction"]["seasons"].items():
        o = r["other_share"]; mx = r["max_abs_rel_change"]
        L.append(f"| {y} | {', '.join(r['components_differing'])} | {f(o['committed']['carry'], 4)} / {f(o['committed']['target'], 4)} → "
                 f"{f(o['reproduced']['carry'], 4)} / {f(o['reproduced']['target'], 4)} | {', '.join(r['team_stats_differing'])} | "
                 f"{pct(mx['mae'], 2)} / {pct(mx['crps'], 2)} / {pct(mx['cover90'], 2)} |")
    L += ["", "`sim_version` differs only because the committed bundles predate the additive sim-1.1.0 label. The 2023 and 2024 "
          "seasons of the five-season run below are bit-identical to an unmodified-code reproduction (same bundle, same "
          "evaluation), which shows the GAME SCRIPT V2 hook and the research-arm plumbing change nothing.", ""]
    L += ["## Player projections by season", "",
          "Rows are `backtest.evaluate`'s scored population (predictive mean above a per-statistic floor). Coverage counts an "
          "integer outcome on the interval endpoint as covered, so it overstates calibration for small counts; the randomized "
          "PIT χ² (10 bins; 16.9 is the 5% critical value at df 9) is the honest uniformity check.", ""]
    for y, r in b["by_season"].items():
        L += [f"### {y} ({r['evidence_class']})", ""]
        _player_table(r, L)
        if r.get("evaluate_mismatches"):
            L += [f"**WARNING:** {len(r['evaluate_mismatches'])} numbers differ from `backtest.evaluate`.", ""]
    L += ["### Pooled 2021-2025 (game-clustered 95% intervals)", ""]
    _player_table(b["pooled"], L, pooled=True)
    L += ["| statistic | MAE [95% CI] | MAE − naive MAE [95% CI] | CRPS [95% CI] | cover50 [95% CI] | cover90 [95% CI] |", "|---|---|---|---|---|---|"]
    for st in STATS:
        r = b["pooled"]["player"].get(st)
        if not r:
            continue
        c = r["ci"]
        L.append(f"| {st} | {ci(c['ae'])} | {ci(c.get('mae_minus_baseline'))} | {ci(c['crps'])} | {ci(c['in50'])} | {ci(c['in90'])} |")
    L += ["", "## Calibration shape (pooled randomized PIT)", "",
          "Bin heights relative to uniform (1.00). Shape is read by a fixed rule: OVER-DISPERSED (forecast too wide) when the two "
          "edge bins average below 0.8 and the middle four above 1.1; UNDER-DISPERSED when BOTH edge bins exceed 1.15; "
          "LEFT-TAIL HEAVY / RIGHT-TAIL HEAVY when the lowest / highest bin exceeds 1.25; otherwise NEAR-UNIFORM.", "",
          "| statistic | PIT bins (relative) | P(PIT < 0.05) | P(PIT > 0.95) | χ² | shape |", "|---|---|---|---|---|---|"]
    for st in STATS:
        r = b["pooled"]["player"].get(st)
        if not r:
            continue
        h = np.asarray(r["randomized_pit"]["hist"], float); h = 10 * h / h.sum()
        edge, mid = (h[0] + h[-1]) / 2, h[3:7].mean()
        shape = ("OVER-DISPERSED" if edge < 0.8 and mid > 1.1 else "UNDER-DISPERSED" if min(h[0], h[-1]) > 1.15 else
                 "LEFT-TAIL HEAVY" if h[0] > 1.25 else "RIGHT-TAIL HEAVY" if h[-1] > 1.25 else "NEAR-UNIFORM")
        L.append(f"| {st} | {' '.join(f'{x:.2f}' for x in h)} | {f(r['randomized_pit']['share_below_0.05'])} | "
                 f"{f(r['randomized_pit']['share_above_0.95'])} | {f(r['randomized_pit']['chi2'], 1)} | {shape} |")
    L += ["", "## Season-to-season instability (CRPS)", "", "| statistic | " + " | ".join(b["by_season"]) + " | max/min |",
          "|---|" + "---|" * (len(b["by_season"]) + 1)]
    for st in STATS:
        xs = [b["by_season"][y]["player"].get(st, {}).get("crps") for y in b["by_season"]]
        ok = [x for x in xs if x is not None]
        L.append(f"| {st} | " + " | ".join(f(x) for x in xs) + f" | {f(max(ok) / min(ok), 3) if ok else '—'} |")
    L += ["", "## Team level", "", "| season | " + " | ".join(f"{s} CRPS / cover90" for s in ("plays", "pass_att", "rush_att", "dropbacks", "points")) + " |",
          "|---|---|---|---|---|---|"]
    for y, r in list(b["by_season"].items()) + [("pooled", b["pooled"])]:
        L.append(f"| {y} | " + " | ".join(f"{f(r['team'][s].get('crps'))} / {f(r['team'][s].get('cover90'))}" for s in ("plays", "pass_att", "rush_att", "dropbacks", "points")) + " |")
    L += ["", "## Eligibility and missing data", "",
          "| season | eligible rows | team-games with a set | questionable | no prior history | no depth-chart rank | realized carries / targets / attempts covered | players with touches outside the set | sim QB1 = leading passer |",
          "|---|---|---|---|---|---|---|---|---|"]
    for y, r in b["by_season"].items():
        e = r["eligibility"]; c = e["realized_volume_covered_by_eligible_set"]; q = r["qb_identification"]
        L.append(f"| {y} | {e['eligible_rows']} | {e['team_games_with_eligible_set']} / {e['team_games_in_season']} | "
                 f"{e['avail_state_counts'].get('QUESTIONABLE', 0)} | {e['eligible_with_no_prior_history']} | {e['eligible_without_depth_chart_rank']} | "
                 f"{pct(c['designed_carries'])} / {pct(c['targets'])} / {pct(c['pass_attempts'])} | {e['players_with_touches_not_in_eligible_set']} | "
                 f"{q['sim_qb1_is_actual_starter']}/{q['team_games']} ({pct(q['rate'])}) |")
    L += ["", "## Where the error is (decomposition)", "",
          "Sequential substitution along TEAM VOLUME -> PLAYER SHARE -> EFFICIENCY per player-game: component errors are "
          "`C·s·e − μ`, `c·e − C·s·e`, `y − c·e` (C team volume, c player opportunity, s expected share, e expected "
          "per-opportunity yield). Shares of the summed squared error; the remainder is covariance.", "",
          "| season | statistic | n | team volume | player share | efficiency | covariance |", "|---|---|---|---|---|---|---|"]
    for y, r in b["by_season"].items():
        for st, d in r["decomposition"].items():
            v = d["variance_share"]
            L.append(f"| {y} | {st} | {d['n']} | {pct(v['team_volume'], 0)} | {pct(v['player_share'], 0)} | {pct(v['efficiency'], 0)} | {pct(d['covariance_share'], 0)} |")
    L += ["", "Player share is the largest component for receptions and rushing yards in every season; for passing yards it is the "
          "starter's share of team attempts, i.e. starter identification and in-game exits. Efficiency covariates were already "
          "shown not to move rushing efficiency (`research/simulation_engine/RUSHING_ABLATION.md`).", ""]
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------------------ calibration
def render_calibration(c: dict, v: dict | None) -> str:
    cells = c["cells"]
    L = ["# GAME SCRIPT V2: five-season script calibration (2021-2025)", "",
         HDR.format(src="script_calibration_5y.json" + (" and validation_5y.json" if v else "")), "",
         "Reproduce: `python scripts/sim/script_backtest.py` after the five-season walk-forward. Every game's nine-cell "
         "distribution comes from the SAME simulated rows that were scored in `BASELINE_5Y.md`; the realized game is classified "
         "by the same function with the same centre. Baselines are fitted on training seasons only (2016..Y-1): B0 = "
         "unconditional cell frequencies, B1 = frequencies within the absolute closing-spread bucket. "
         f"Provenance: **{c['meta']['provenance']}** -- {c['meta']['note']}.", "",
         f"## Verdict: **{c['verdict']['verdict']}**", ""]
    for k, x in c["verdict"]["conditions"].items():
        L.append(f"- {k}: **{x}**")
    L += ["", "## Multiclass scores", "",
          "| season | games | Brier model / B0 / B1 | model − B0 [95% CI] | model − B1 [95% CI] | log loss model / B0 / B1 | top-script p | top-script hit | entropy | ECE model (null 95%) |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for y, s in list(c["by_season"].items()) + [("pooled", c["pooled"])]:
        L.append(f"| {y} | {s['n_games']} | {f(s['model']['brier'], 4)} / {f(s['B0']['brier'], 4)} / {f(s['B1']['brier'], 4)} | "
                 f"{ci(s['brier_model_minus_B0'], 4)} | {ci(s['brier_model_minus_B1'], 4)} | "
                 f"{f(s['model']['log_loss'], 4)} / {f(s['B0']['log_loss'], 4)} / {f(s['B1']['log_loss'], 4)} | {f(s['model']['top_p'])} | "
                 f"{f(s['model']['top_hit'])} | {f(s['model']['entropy'])} | {f(s['model']['reliability']['ece'], 4)} ({f(s['ece_null']['p95'], 4)}) |")
    L += ["", "## Predicted vs realized frequency by cell (pooled)", "", "| cell | model | realized | B0 | B1 |", "|---|---|---|---|---|"]
    for k in cells:
        r = c["pooled"]["by_cell"][k]
        L.append(f"| {k.replace('|', ' / ')} | {pct(r['predicted'])} | {pct(r['realized'])} | {pct(r['B0'])} | {pct(r['B1'])} |")
    L += ["", "## Reliability (pooled, one-vs-rest over all nine cells)", "", "| bin | n | mean p | realized |", "|---|---|---|---|"]
    for b in c["pooled"]["model"]["reliability"]["bins"]:
        if b["n"]:
            L.append(f"| {b['bin'][0]:.1f}-{b['bin'][1]:.1f} | {b['n']} | {f(b['mean_p'])} | {f(b['freq'])} |")
    L += ["", "## Marginal events (Brier; pooled, game-clustered 95% CI)", "",
          "| event | n | mean p | rate | Brier model | Brier B0 | Brier B1 | model − B0 | model − B1 |", "|---|---|---|---|---|---|---|---|---|"]
    for e, r in c["pooled"]["events"].items():
        L.append(f"| {e} | {r['n']} | {f(r['mean_p'])} | {f(r['rate'])} | {f(r['brier_model'], 4)} | {f(r['brier_B0'], 4)} | {f(r['brier_B1'], 4)} | "
                 f"{ci(r['model_minus_B0'], 4)} | {ci(r['model_minus_B1'], 4)} |")
    L += ["", "Calibration in the large (pooled): mean forecast − realized rate, in binomial standard errors of the rate.", "",
          "| event | mean p − rate | z |", "|---|---|---|"]
    for e, r in c["pooled"]["events"].items():
        se = (max(r["rate"] * (1 - r["rate"]), 1e-12) / r["n"]) ** 0.5
        L.append(f"| {e} | {r['mean_p'] - r['rate']:+.4f} | {(r['mean_p'] - r['rate']) / se:+.1f} |")
    L += ["", "Per season (model − B1 Brier, mean):", "", "| event | " + " | ".join(c["by_season"]) + " |", "|---|" + "---|" * len(c["by_season"])]
    for e in c["pooled"]["events"]:
        L.append(f"| {e} | " + " | ".join(f(c["by_season"][y]["events"].get(e, {}).get("model_minus_B1", {}).get("mean"), 4) for y in c["by_season"]) + " |")
    L += ["", "Favourite events exclude pick'em games (no favourite); volume events use the play-by-play team-game table. "
          "The nine cells and the score events are a test of the market centre plus the residual bank; low_possession, "
          "high_volume_passing and run_heavy_control also test the volume model.", ""]
    ms = c.get("margin_shape")
    if ms:
        L += ["## POST-HOC: the shape of the simulated final margin", "",
              f"**{ms['status']}** -- not preregistered; examined because `one_score` was under-forecast in every season. The "
              "(margin, total) of every simulated row is the market centre plus a historical residual drawn from the incumbent's "
              "`pricing/game_env.ResidualBank`. Adding a residual to the target spread is translation-invariant, so the NFL's "
              "key-number structure (final margins of exactly 3 and 7) is smeared into the 9-16 band. This concerns the incumbent's "
              "game-environment shape, which this study does not change; a key-number-aware margin model is a separate, to-be-"
              "preregistered research item.", "",
              "| |m| | predicted (pooled) | realized (pooled) ± SE | " + " | ".join(f"{y} pred / real" for y in ms["by_season"]) + " |",
              "|---|---|---|" + "---|" * len(ms["by_season"])]
        for j, r in enumerate(ms["pooled"]["rows"]):
            L.append(f"| {r['band']} | {pct(r['predicted'])} | {pct(r['realized'])} ± {pct(r['realized_se'])} | " +
                     " | ".join(f"{pct(ms['by_season'][y]['rows'][j]['predicted'], 0)} / {pct(ms['by_season'][y]['rows'][j]['realized'], 0)}"
                                for y in ms["by_season"]) + " |")
        L.append("")
    if v:
        sp = v["score_path"]
        L += ["## Score-path research arm P1 (preregistered; not part of GAME SCRIPT V2)", "",
              f"**Verdict: {sp['verdict']['verdict']}.** P1 averages, over the simulated rows, a kernel conditional of each path "
              "event on the row's final margin and scoring cell (training games only); the baseline is the training frequency in the "
              f"signed closing-spread bucket. {sp['n_path_games']} games with quarter scores; {sp['pbp_final_mismatch_games']} where the "
              "play-by-play running score's final differs from the schedule final (kept and counted).", "",
              "| target | metric | P1 | baseline | P1 − baseline [95% CI] | beats baseline |", "|---|---|---|---|---|---|"]
        for t, r in sp["pooled"].items():
            L.append(f"| {t} | {r['metric']} | {f(r['arm'], 4)} | {f(r['baseline'], 4)} | {ci(r['arm_minus_baseline'], 4)} | "
                     f"{sp['verdict']['beats_baseline_by_target'][t]} |")
        L += ["", "Lead changes, time leading, early blowouts and late comebacks therefore stay `not_simulated` in GAME SCRIPT V2.", ""]
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------------------------- ablation
def render_ablation(a: dict) -> str:
    L = ["# Opponent-adjusted team ratings: walk-forward ablation (2021-2025)", "",
         HDR.format(src="opponent_adjustment_ablation.json"), "",
         "Reproduce: `python scripts/sim/oppadj_ablation.py features`, `python scripts/sim/oppadj_ablation.py run --arm <ARM> "
         "--seasons <Y>` for every arm and season, then `python scripts/sim/game_script_v2_report.py ablation`. Design and the "
         "promotion rule: `PREREGISTRATION.md` sections 5-6 (stage 1) and the stage-2 addendum (R1).", "",
         f"Comparison is {a['meta']['population']}; intervals are game-clustered ({a['meta']['bootstrap']['resamples']} resamples). "
         f"Primary summary = mean over the eight statistics of `CRPS_arm / CRPS_A0 − 1` (negative is better); material = "
         f"{a['meta']['material_threshold']:+.3f}.", "", "## Arms", ""]
    for k, spec in a["arm_specs"].items():
        L.append(f"- **{k}** — " + "; ".join(f"`{kk}`: {', '.join(vv) if isinstance(vv, list) else vv}" for kk, vv in spec.items()))
    L += ["", "## Verdicts", "", "| arm | " + " | ".join(next(iter(a["arms"].values())).get("by_season", {}).keys()) + " | pooled [95% CI] | stats improved | verdict |",
          "|---|" + "---|" * (len(next(iter(a["arms"].values())).get("by_season", {})) + 3)]
    for k, r in a["arms"].items():
        if r.get("verdict") == "NOT_RUN":
            L.append(f"| {k} | NOT RUN: {r['reason']} |"); continue
        p = r["pooled"]
        L.append(f"| {k} | " + " | ".join(f"{100 * s['primary']:+.2f}%" for s in r["by_season"].values()) +
                 f" | {100 * p['primary']:+.2f}% [{100 * p['primary_lo']:+.2f}, {100 * p['primary_hi']:+.2f}] | {len(r['stats_improved_pooled'])}/8 | **{r['verdict']}** |")
    L += ["", "## Promotion criteria by arm", ""]
    crit_names = list(next(r for r in a["arms"].values() if "criteria" in r)["criteria"])
    L += ["| arm | " + " | ".join(crit_names) + " |", "|---|" + "---|" * len(crit_names)]
    for k, r in a["arms"].items():
        if "criteria" in r:
            L.append(f"| {k} | " + " | ".join(str(r["criteria"][c]) for c in crit_names) + " |")
    L += ["", "## Pooled relative CRPS change by statistic", "", "| arm | " + " | ".join(BR_STATS) + " | calibration Δ (SE) |", "|---|" + "---|" * (len(BR_STATS) + 1)]
    for k, r in a["arms"].items():
        if "pooled" in r:
            p = r["pooled"]
            L.append(f"| {k} | " + " | ".join(f"{100 * p['by_stat'][s]:+.2f}%" for s in BR_STATS) +
                     f" | {p['calibration_delta']:+.4f} ({p['calibration_delta_se']:.4f}) |")
    L += ["", "## Team-level CRPS (pooled over seasons, mean of season values)", "", "| arm | plays | pass_att | rush_att | dropbacks | targets |", "|---|---|---|---|---|---|"]
    for k, by in a["team_crps"].items():
        L.append(f"| {k} | " + " | ".join(f(np.mean([by[y][s] for y in by])) for s in ("plays", "pass_att", "rush_att", "dropbacks", "targets")) + " |")
    L += ["", "## Primitive diagnostic: do the adjusted ratings predict next week's team metric better?", "",
          "One-week-ahead RMSE of the realized team-game metric from the adjusted matchup `mx` versus the unadjusted pair (same "
          "window and weights, no opponent model); `Δ MSE` = adjusted − unadjusted with a game-clustered 95% CI. Not a promotion "
          "criterion: a better rating that does not improve the simulated distributions is not deployed.", "",
          "| season | metric | λ | RMSE adjusted | RMSE unadjusted | Δ MSE [95% CI] |", "|---|---|---|---|---|---|"]
    for y, d in a["features"].items():
        lam = d["lambda_selection"]["lambdas"]
        for mtr, r in d["primitive"].items():
            L.append(f"| {y} | {mtr} | {lam[mtr]:g} | {f(r['rmse_adjusted'], 4)} | {f(r['rmse_unadjusted'], 4)} | {ci(r['mse_diff_by_game'], 5)} |")
    L.append("")
    return "\n".join(L) + "\n"


BR_STATS = ["carries", "rush_yards", "targets", "receptions", "rec_yards", "attempts", "completions", "pass_yards"]


# ---------------------------------------------------------------------------------------------- validation
def render_validation(v: dict) -> str:
    iv = v["injury_redistribution"]; w = v["weather"]
    L = ["# Five-season validation: injury redistribution and weather", "", HDR.format(src="validation_5y.json"), "",
         "Reproduce: `python scripts/sim/game_script_v2_report.py validation`.", "",
         "## Injury / availability redistribution (preregistration section 9)", "", iv["note"] + ".", "",
         "`TEAMMATE_OF_OUT_STARTER` is the registered population (depth-chart-1 RB/WR/TE designated Out/Doubtful). "
         "`TEAMMATE_OF_UNAVAILABLE_STARTER` is a POST-HOC broadening to any absence, added because the historical eligible "
         "set is the game-day active list and most absences carry no designation.", "",
         "| season | dc1 RB/WR/TE unavailable, by reason | team-games with dc1 unavailable | with 2+ of dc1-2 unavailable |", "|---|---|---|---|"]
    for y, r in iv["by_season"].items():
        u = r["unavailability"]
        L.append(f"| {y} | " + ", ".join(f"{k} {x}" for k, x in u["dc1_unavailable_by_reason"].items()) +
                 f" | {u['team_games_with_dc1_unavailable']} | {u['team_games_with_2plus_unavailable']} |")
    for st in ("carries", "targets"):
        L += ["", f"### {st} (pooled 2021-2025)", "", "| population | n | games | bias (pred − actual) [95% CI] | MAE | CRPS | cover50 | cover90 [95% CI] |",
              "|---|---|---|---|---|---|---|---|"]
        for pop, r in iv["pooled"][st].items():
            if not r.get("n"):
                L.append(f"| {pop} | 0 | | | | | | |"); continue
            c = r.get("ci") or {}
            L.append(f"| {pop} | {r['n']} | {r['n_games']} | {ci(c.get('err')) if c else f(r['bias'])} | {f(r['mae'])} | {f(r['crps'])} | "
                     f"{f(r['cover50'])} | {ci(c.get('in90')) if c else f(r['cover90'])} |")
    h = w["historical"]; p = w["prospective_2026"]
    L += ["", "## Weather", "", f"### Historical: {h['status']} ({min(h['seasons'])}-{max(h['seasons'])}, outdoor stadiums)", "", h["caveat"] + ".", "",
          f"{h['n_outdoor_games']} outdoor games, {h['n_with_observed_wind']} with an observed wind reading.", "",
          "| observed wind (mph) | games | total − closing total [95% CI] |", "|---|---|---|"]
    for k, r in h["wind"].items():
        L.append(f"| {k} | {r['n']} | {ci(r, 2) if 'lo' in r else f(r.get('mean'), 2)} |")
    L += ["", "| observed temperature | games | total − closing total [95% CI] |", "|---|---|---|"]
    for k, r in h["temp"].items():
        L.append(f"| {k} | {r['n']} | {ci(r, 2) if 'lo' in r else f(r.get('mean'), 2)} |")
    if h.get("combined_pass_att_resid_vs_sim_mean"):
        L += ["", "| observed wind (mph) | games 2021-2025 | combined pass attempts − simulation mean [95% CI] |", "|---|---|---|"]
        for k, r in h["combined_pass_att_resid_vs_sim_mean"].items():
            L.append(f"| {k} | {r['n']} | {ci(r, 2) if 'lo' in r else f(r.get('mean'), 2)} |")
    L += ["", "None of these rows may fit or promote a predictive feature.", "", f"### Prospective 2026: {p['status']}", "",
          f"Completed 2026 games: {p['completed_games']}; with a point-in-time kickoff forecast (newest vintage retrieved at or before "
          f"kickoff): {p['with_pit_forecast']} (median lead {f(p['lead_hours_of_selected_vintage']['median'], 1)} h); outdoors with a "
          f"forecast: {p['outdoor_with_forecast']}; qualifying for W1/W2 (forecast wind ≥ 15 mph, outdoors): {p['w1_w2_qualifying_games']}. "
          f"Readout: {p['readout']}. GAME SCRIPT V2 shows the forecast with `weather_model_status = NOT_IN_MODEL`.", ""]
    return "\n".join(L) + "\n"


def render_all() -> dict:
    out = {}
    b, c, a, v = _load("baseline_5y.json"), _load("script_calibration_5y.json"), _load("opponent_adjustment_ablation.json"), _load("validation_5y.json")
    if b:
        out["BASELINE_5Y.md"] = render_baseline(b)
    if c:
        out["SCRIPT_CALIBRATION_5Y.md"] = render_calibration(c, v)
    if a:
        out["OPPONENT_ADJUSTMENT_ABLATION.md"] = render_ablation(a)
    if v:
        out["VALIDATION_5Y.md"] = render_validation(v)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    bad = []
    for name, text in render_all().items():
        p = os.path.join(OUT, name)
        if a.check:
            if not os.path.exists(p) or open(p).read() != text:
                bad.append(name)
        else:
            open(p, "w").write(text); print("wrote", name)
    if a.check:
        print("stale:" if bad else "all committed summaries match their JSON", *bad)
        raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
