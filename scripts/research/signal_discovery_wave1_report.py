#!/usr/bin/env python3
"""Render the NFL Wave 1 generated tables, signal registry and catalogs from the frozen evaluation reports.

Writes:
  docs/research/FOOTBALL_SIGNAL_DISCOVERY_WAVE1_TABLES.md
  docs/research/NFL_SIGNAL_CATALOG.md
  docs/research/NFL_PLAYER_PROP_SIGNAL_CATALOG.md
  research/signal_discovery_wave1/football_signal_registry.json   (football_signal_registry/1.0.0)
Status is copied from the mechanical rules; nothing is upgraded by hand; EDGE_CONFIRMED is never assigned.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "research" / "signal_discovery_wave1"
DOCS = ROOT / "docs" / "research"


def f(v, nd=3, pct=False, sign=True):
    if v is None:
        return "—"
    if pct:
        return f"{100 * v:.1f}%"
    return f"{v:+.{nd}f}" if sign else f"{v:.{nd}f}"


def game_tables(rep: dict, scr: dict) -> list[str]:
    L = ["## G1. Every game hypothesis (2015–2025; set-2 rows judged on block B in G2)", "",
         "| Id | Status | Football effect | q | Market effect | q | Holm p (market) | Name |", "|---|---|---|---|---|---|---|---|"]
    for s in rep["summary"]:
        fdr = rep["results"][s["id"]].get("fdr", {})
        L.append(f"| {s['id']} | {s['status']} | {f(s['football_effect'])} | {f(s['football_q'], sign=False)} | {f(s['market_effect'])} | "
                 f"{f(s['market_q'], sign=False)} | {f(fdr.get('market_p_holm'), sign=False)} | {s['name']} |")
    L += ["", "## G2. Set 2 on block B only", "", "| Id | Status | Market effect | q | n |", "|---|---|---|---|---|"]
    for s in rep["set2_block_b"]["summary"]:
        r = rep["set2_block_b"]["results"][s["id"]]
        L.append(f"| {s['id']} | {s['status']} | {f(s['market_effect'])} | {f(s['market_q'], sign=False)} | {(r.get('market') or {}).get('n')} |")
    L += ["", "## G3. Slope hypotheses: market residual detail", "",
          "| Id | n | β/SD | p | Block A β (p) | Block B β (p) | seasons expected sign | Follow \\|z\\|≥1: n, cover, ROI@−110 |", "|---|---|---|---|---|---|---|---|"]
    for sid, r in rep["results"].items():
        m = r.get("market") or {}
        if "beta_per_sd" not in m:
            continue
        b = m["blocks"]
        fr = m["follow_rule_abs_z_ge_1"]
        L.append(f"| {sid} | {m['n']} | {f(m['beta_per_sd'])} | {f(m['p'], sign=False)} | {f(b['A'].get('beta_per_sd'))} ({f(b['A'].get('p'), sign=False)}) | "
                 f"{f(b['B'].get('beta_per_sd'))} ({f(b['B'].get('p'), sign=False)}) | {f(m['share_seasons_expected_sign'], pct=True)} | "
                 f"{fr['n']}, {f(fr.get('cover_rate'), pct=True)}, {f(fr.get('roi_assumed_110'), pct=True)} |")
    L += ["", "## G4. Side / total hypotheses", "", "| Id | n | Win / lift | Market n | Cover or O/U hit | Mean resid (p) | ROI@−110 | ML win − implied | ML ROI |",
          "|---|---|---|---|---|---|---|---|---|"]
    for sid, r in rep["results"].items():
        blk = r.get("ATS") or r.get("TOTAL")
        if not blk:
            continue
        fb, ml = r["football"], r.get("ML") or {}
        L.append(f"| {sid} | {fb['n']} | {f(fb.get('win_rate'), pct=True) if 'win_rate' in fb else f(fb.get('lift_mean'), 2)} | {blk.get('n')} | "
                 f"{f(blk.get('cover_rate'), pct=True)} | {f(blk.get('mean_resid'), 2)} ({f(blk.get('resid_p'), sign=False)}) | {f(blk.get('roi_assumed_110'), pct=True)} | "
                 f"{f(ml.get('mean_resid_win_minus_implied'))} | {f(ml.get('roi_provider_odds'), pct=True)} |")
    ct = rep["deep_dive"]["control_tiers"]
    L += ["", "## G5. Efficiency-CONTROL tiers (|net EPA/play| ≥ 0.075 moderate, ≥ 0.115 strong)", "",
          "| Tier | n | Win | ATS W-L-P | Cover [95%] | Mean resid (p) | ROI@−110 | Mean spread (side) | ML n | Win − implied | ML ROI [95%] |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, v in ct.items():
        if not isinstance(v, dict) or "ATS" not in v:
            continue
        a, fb, m = v["ATS"], v["football"], v["ML"]
        L.append(f"| {k} | {fb['n']} | {f(fb['win_rate'], pct=True)} | {a['covers']}-{a['losses']}-{a['pushes']} | {f(a['cover_rate'], pct=True)} "
                 f"[{f(a['cover_ci'][0], pct=True)}, {f(a['cover_ci'][1], pct=True)}] | {f(a['mean_resid'], 2)} ({f(a['resid_p'], sign=False)}) | "
                 f"{f(a['roi_assumed_110'], pct=True)} | {f(a['mean_spread_s'], 1)} | {m.get('n')} | {f(m.get('mean_resid_win_minus_implied'))} | "
                 f"{f(m.get('roi_provider_odds'), pct=True)} [{f((m.get('roi_ci_boot') or [None])[0], pct=True)}, {f((m.get('roi_ci_boot') or [None, None])[1], pct=True)}] |")
    md = rep["deep_dive"]["market_disagreement"]
    L += ["", "## G6. Market disagreement regimes", "", "| Football | Market regime | n | Win | ATS cover | Mean resid (p) | ML implied | ML win | ML ROI |", "|---|---|---|---|---|---|---|---|---|"]
    for tier in ("CONTROL_STRONG", "CONTROL_MODERATE"):
        for reg, x in md[tier].items():
            a, m = x["ATS"], x["ML"]
            L.append(f"| {tier} | {reg} | {x['n']} | {f(x['win_rate'], pct=True)} | {f(a.get('cover_rate'), pct=True)} | {f(a.get('mean_resid'), 2)} ({f(a.get('resid_p'), sign=False)}) | "
                     f"{f(m.get('mean_novig_implied'), pct=True)} | {f(m.get('win_rate'), pct=True)} | {f(m.get('roi_provider_odds'), pct=True)} |")
    bd = md.get("baseline_vs_market_favourite_disagree")
    if bd:
        L += ["", f"Football baseline and closing spread disagree on the favourite in {bd['n']} games: football side won {f(bd['football_side_win_rate'], pct=True)} "
              f"(implied {f(bd['football_side_mean_novig_implied_2021plus'], pct=True)}); football side ATS {f(bd['football_side_ATS']['cover_rate'], pct=True)}, "
              f"mean resid {f(bd['football_side_ATS']['mean_resid'], 2)} (p {f(bd['football_side_ATS']['resid_p'], sign=False)})."]
    L += ["", "## G7. Walk-forward", ""]
    for k, v in rep["walk_forward"].items():
        a = v["aggregate"]
        L.append(f"* **{k}**: " + json.dumps({kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in a.items() if not isinstance(vv, dict)}))
        p = a.get("picks_abs_pred_ge_threshold")
        if p:
            L.append(f"  * picks: n {p.get('n')}, {p.get('covers')}-{p.get('losses')}-{p.get('pushes')}, cover {f(p.get('cover_rate'), pct=True)}, ROI@−110 {f(p.get('roi_assumed_110'), pct=True)} "
                     f"[{f((p.get('roi_ci_boot') or [None])[0], pct=True)}, {f((p.get('roi_ci_boot') or [None, None])[1], pct=True)}]")
        L.append("  * folds: " + "; ".join(f"{x['test_season']}: " + (f"r {x['oos_corr']:+.3f}, picks {x['picks'].get('n')} @ {f(x['picks'].get('cover_rate'), pct=True)}" if "oos_corr" in x
                                                                      else f"Δlogloss {x['logloss_market_plus_football'] - x['logloss_market_raw']:+.4f}") for x in v["folds"]))
    L += ["", "## G8. Stage A screen (block A 2015–2019; exploration only)", "",
          f"{scr['associations_screened']} associations; market q<0.05: {scr['market_q_lt_0_05']}; q<0.10: {scr['market_q_lt_0_10']}.", "",
          "| Scope | Feature | Target | n | β/SD | z | q |", "|---|---|---|---|---|---|---|"]
    for e in scr["top"]["market"][:15]:
        L.append(f"| {e['scope']} | {e['feature']} | {e['target']} | {e['n']} | {e['beta_per_sd']:+.3f} | {e['z']:+.2f} | {e['q_bh_whole_screen']:.3f} |")
    return L


def prop_tables(pr: dict) -> list[str]:
    L = ["", "## P1. Prop families: walk-forward accuracy (test seasons 2018–2026; MAE, lower is better)", "",
         "| Family | n | Players | Season avg | EWMA | Usage | Opportunity model | Gain vs best baseline [95% game-cluster] | Seasons model ahead | Gain w/o top-10 players | PI50 / PI80 coverage |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for fid, r in pr["families"].items():
        s = r["summary"]
        g = s["mae_gain_vs_best_baseline"]
        ahead = sum(1 for v in s["by_season_gain_vs_best"].values() if v is not None and v > 0)
        L.append(f"| {fid} | {s['n']} | {s['players']} | {s['mae.SEASON_AVG']:.2f} | {s['mae.EWMA']:.2f} | {s['mae.USAGE']:.2f} | {s['mae.MODEL']:.2f} | "
                 f"{g['mae_delta']:+.3f} ({g['rel_gain_pct']:+.1f}%) [{g['ci_game_cluster'][0]:+.3f}, {g['ci_game_cluster'][1]:+.3f}] vs {s['best_baseline']} | "
                 f"{ahead}/{len(s['by_season_gain_vs_best'])} | {s['gain_without_top10_players']:+.3f} | {s['pi50_coverage']:.2f} / {s['pi80_coverage']:.2f} |")
    groups = sorted({g for r in pr["families"].values() for g in r["summary"]["groups"]})
    L += ["", "## P2. Feature-group ablations (MAE gain when the group is included; + = helps; BH q over all 140 group tests)", "",
          "| Family | " + " | ".join(groups) + " |", "|---|" + "---|" * len(groups)]
    for fid, r in pr["families"].items():
        gs = r["summary"]["groups"]
        cells = []
        for g in groups:
            v = gs.get(g)
            if v is None:
                cells.append("·")
            else:
                mark = {"FOOTBALL_VALIDATED": "**", "DISCOVERY_ONLY": "*"}.get(v["status"], "")
                cells.append(f"{mark}{v['mae_delta']:+.3f}{mark} (q {v['q_bh_all_prop_groups']:.2f}, {v['seasons_positive']}/{v['seasons']})")
        L.append(f"| {fid} | " + " | ".join(cells) + " |")
    L += ["", "Bold = FOOTBALL_VALIDATED (q<0.05, gain>0, ≥60% seasons); italic = DISCOVERY_ONLY.", "",
          "## P3. Role stability: model gain over the best baseline by role class (MAE points)", "", "| Family | STABLE_ROLE | ROLE_CHANGE | INJURY_DEPENDENT |", "|---|---|---|---|"]
    for fid, r in pr["families"].items():
        br = r["summary"]["by_role"]
        L.append(f"| {fid} | " + " | ".join(f"{br[k]['mae_best_base'] - br[k]['mae_model']:+.3f} (n {br[k]['n']})" if k in br else "—"
                                          for k in ("STABLE_ROLE", "ROLE_CHANGE", "INJURY_DEPENDENT")) + " |")
    L += ["", "## P4. Kalshi ladders: residual vs line, information, economics", "",
          "Checkpoints: 2025 T-90m (YES bid/ask), 2026 LAST_PREGAME ≤ 24 h (both asks). Market median = interpolated 50% rung.", "",
          "| Family | Ladders (2025/2026) | Actual − median: mean / median [95%] | Share over median | MAE market / model | Resid ~ (model − market): β (p, q) | Model rule: n, win, ROI [95%] | Always-NO ROI [95%] (post hoc) | Always-YES ROI (post hoc) |",
          "|---|---|---|---|---|---|---|---|---|"]
    for fid, r in pr["families"].items():
        mk = r.get("market") or {}
        if mk.get("status") != "EVALUATED":
            L.append(f"| {fid} | {mk.get('ladders_matched', 0)} | {mk.get('status')} | | | | | | |")
            continue
        mr, g, e = mk["market_residual"], mk["residual_on_model_gap"], mk["economics"]
        an, ay = mk.get("always_NO_natural_rung_posthoc", {}), mk.get("always_YES_natural_rung_posthoc", {})
        bs = mk["by_season"]
        L.append(f"| {fid} | {bs.get('2025', bs.get(2025, 0))}/{bs.get('2026', bs.get(2026, 0))} | {mr['mean']:+.2f} / {mr['median']:+.2f} "
                 f"[{mr['ci_game_cluster'][0]:+.2f}, {mr['ci_game_cluster'][1]:+.2f}] | {mr['share_over_market_median']:.1%} | {mk['mae_market_median']:.2f} / {mk['mae_model_median']:.2f} | "
                 f"{g['beta']:+.3f} ({g['p']:.2f}, {g.get('q_bh_all_market_tests', 1):.2f}) | "
                 + (f"{e['n']}, {e['win_rate']:.1%}, {e['roi']:+.1%} [{e['roi_ci_boot'][0]:+.1%}, {e['roi_ci_boot'][1]:+.1%}]" if e.get("n") else "0")
                 + f" | {f(an.get('roi'), pct=True)} [{f((an.get('roi_ci_boot') or [None])[0], pct=True)}, {f((an.get('roi_ci_boot') or [None, None])[1], pct=True)}] | {f(ay.get('roi'), pct=True)} |")
    L += ["", "## P5. Signal features vs the line residual (β per SD of the group's lead feature; BH q over all market tests)", ""]
    for fid, r in pr["families"].items():
        sig = (r.get("market") or {}).get("signal_feature_vs_residual") or {}
        if sig:
            L.append(f"* **{fid}**: " + "; ".join(f"{k} {v['beta_per_sd']:+.2f} (p {v['p']:.3f}, q {v.get('q_bh_all_market_tests', 1):.2f})" for k, v in sig.items()))
    L += ["", "## P6. Game script → player volume (β per SD, % of the stat's mean, p; controls for the player's EWMA)", "",
          "| Stat | Pregame expected script | Pregame expected plays | Realised lead−trail share (post hoc) | Realised team plays (post hoc) |", "|---|---|---|---|---|"]
    for k, v in pr["game_script_effects"].items():
        def c(name):
            x = v.get(name)
            return "—" if not x else f"{x['beta_per_sd']:+.2f} ({x['pct_of_mean']:+.1f}%, p {x['p']:.3f})"
        L.append(f"| {k} | {c('pregame_expected_script')} | {c('pregame_expected_plays')} | {c('realised_lead_minus_trail_share')} | {c('realised_team_plays')} |")
    L += ["", "## P7. Correlation of out-of-sample residuals within a team-game", ""]
    for k, v in pr["correlations"].items():
        L.append(f"* {k}: r = {v['corr']:+.2f} (n {v['n_team_games']})")
    return L


def registry(rep: dict, pr: dict, set1: dict, set2: dict) -> dict:
    specs = {h["id"]: h for h in set1["game_hypotheses"] + set2["hypotheses"]}
    block_b = {s["id"]: s for s in rep["set2_block_b"]["summary"]}
    code_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    proto_sha = hashlib.sha256((DOCS / "FOOTBALL_SIGNAL_DISCOVERY_WAVE1_PROTOCOL.md").read_bytes()).hexdigest()
    lim = ["RETROSPECTIVE DISCOVERY / VALIDATION; nflverse 2015-2025 and the Kalshi 2025 archive were mined by earlier studies",
           "nflverse lines are an untimestamped near-close consensus; spread/total economics at standard -110"]
    sig = []
    for s in rep["summary"]:
        spec = specs[s["id"]]
        res = rep["results"].get(s["id"], {})
        status = block_b[s["id"]]["status"] if s["id"] in block_b else s["status"]
        sig.append({"signal_id": s["id"], "name": spec["name"], "sport": "NFL", "level": "GAME", "family": spec["family"],
                    "definition": {k: spec.get(k) for k in ("kind", "population", "side", "feature", "controls", "expected_sign", "direction") if spec.get(k) is not None},
                    "football_interpretation": spec["interpretation"], "status": status, "status_reasons": res.get("status_reasons"),
                    "market_families": spec.get("markets", []), "primary_market": spec.get("primary_market"),
                    "discovery_sample": {"set": 2 if s["id"].startswith("NFL-DSC") else 1},
                    "validation": {"football_effect": s["football_effect"], "football_q_bh": s["football_q"], "market_effect": s["market_effect"],
                                   "market_q_bh": s["market_q"], "block_b_only": block_b.get(s["id"])},
                    "economic_results": {k: {kk: (res.get(k) or {}).get(kk) for kk in ("n", "cover_rate", "roi_assumed_110", "roi_provider_odds", "roi_ci_boot")}
                                         for k in ("ATS", "ML", "TOTAL") if res.get(k)},
                    "prospective": {"status": "NOT_STARTED"}, "limitations": lim + ([spec["reason"]] if spec.get("reason") else []),
                    "protocol_sha": proto_sha, "hypothesis_set_sha": rep["set2_sha256"] if s["id"].startswith("NFL-DSC") else rep["set1_sha256"],
                    "evaluation_code_sha": rep["code_sha"], "code_sha": code_sha})
    for fid, r in pr["families"].items():
        s = r["summary"]
        mk = r.get("market") or {}
        for g, v in s["groups"].items():
            sig.append({"signal_id": f"NFL-PROP-{fid}-{g}", "name": f"{g} -> {fid}", "sport": "NFL", "level": "PLAYER", "family": g,
                        "definition": {"kind": "GROUP_ABLATION", "family": fid, "group": g}, "football_interpretation": "see NFL_PLAYER_PROP_SIGNAL_CATALOG.md",
                        "status": v["status"], "market_families": [f"KALSHI_{fid}"],
                        "validation": {"mae_delta": v["mae_delta"], "ci": v["ci_game_cluster"], "q_bh": v.get("q_bh_all_prop_groups"),
                                       "seasons_positive": v["seasons_positive"], "seasons": v["seasons"]},
                        "economic_results": {"market_residual_test": (mk.get("signal_feature_vs_residual") or {}).get(g)},
                        "prospective": {"status": "NOT_STARTED"},
                        "limitations": lim + ["conditional on the player appearing; Kalshi 2025 YES-side only; 2026 <= 5 weeks"],
                        "protocol_sha": proto_sha, "hypothesis_set_sha": rep["set1_sha256"], "code_sha": code_sha})
    return {"schema": "football_signal_registry/1.0.0", "sport": "NFL", "wave": "football-signal-discovery-wave1", "edge_confirmed_assigned": False,
            "signals": sig}


def catalogs(reg: dict, rep: dict, pr: dict) -> None:
    L = ["# NFL signal catalog (game level) — Football Signal Discovery Wave 1", "",
         "Generated by `scripts/research/signal_discovery_wave1_report.py`. Status = the mechanical rule (set 2: block B). Effects: SIDE = win-rate lift / "
         "mean ATS residual (points) or win − no-vig implied (ML); TOTAL = points; SLOPE = points per feature SD. Economics at standard −110 / listed "
         "moneyline odds. RETROSPECTIVE throughout.", "",
         "| Signal | Definition | Football logic | n | Football effect (q) | Market effect (q) | Market family | Economic result | Status |", "|---|---|---|---|---|---|---|---|---|"]
    for s in reg["signals"]:
        if s["level"] != "GAME":
            continue
        res = rep["results"].get(s["signal_id"], {})
        v = s["validation"]
        n = (res.get("football") or {}).get("n")
        econ = "; ".join(f"{k} n {x.get('n')}, ROI {f(x.get('roi_assumed_110') if x.get('roi_assumed_110') is not None else x.get('roi_provider_odds'), pct=True)}"
                         for k, x in s["economic_results"].items()) or "—"
        fr = (res.get("market") or {}).get("follow_rule_abs_z_ge_1")
        if fr:
            econ = f"follow \\|z\\|≥1: n {fr['n']}, cover {f(fr.get('cover_rate'), pct=True)}, ROI {f(fr.get('roi_assumed_110'), pct=True)}"
        d = ", ".join(f"{k}={json.dumps(x)}" for k, x in s["definition"].items())
        L.append(f"| **{s['signal_id']}** {s['name']} | `{d}` | {s['football_interpretation']} | {n} | {f(v['football_effect'])} ({f(v['football_q_bh'], sign=False)}) | "
                 f"{f(v['market_effect'])} ({f(v['market_q_bh'], sign=False)}) | {s['primary_market']} | {econ} | **{s['status']}** |")
    (DOCS / "NFL_SIGNAL_CATALOG.md").write_text("\n".join(L) + "\n")
    P = ["# NFL player-prop signal catalog — Football Signal Discovery Wave 1", "",
         "One row per (prop family × football signal group). Baseline = the best of season-average / EWMA / usage-only for that family. Incremental = "
         "out-of-sample MAE gain from including the group (walk-forward 2018–2026, game-cluster CI). Line residual = slope of (actual − Kalshi ladder "
         "median) on the group's lead feature. Economics are per family (pre-registered natural-rung rule), not per group. RETROSPECTIVE; Kalshi 2025 "
         "archive previously mined.", "",
         "| Signal ID | Position | Stat | Group | n | Baseline MAE (best) | Incremental MAE gain [95%] (q) | Line residual β/SD (q) | Family economics (model rule) | Stability (seasons +) | Concentration (family gain w/o top-10) | Status |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for fid, r in pr["families"].items():
        s = r["summary"]
        mk = r.get("market") or {}
        e = mk.get("economics") or {}
        econ = f"n {e['n']}, ROI {e['roi']:+.1%}" if e.get("n") else "—"
        best = min(s["mae.SEASON_AVG"], s["mae.EWMA"], s["mae.USAGE"])
        pos, stat = fid.split("_", 1)
        for g, v in s["groups"].items():
            lr = (mk.get("signal_feature_vs_residual") or {}).get(g)
            lrs = f"{lr['beta_per_sd']:+.2f} ({lr.get('q_bh_all_market_tests', 1):.2f})" if lr else "—"
            P.append(f"| NFL-PROP-{fid}-{g} | {pos} | {stat} | {g} | {v['n']} | {best:.2f} ({s['best_baseline']}) | "
                     f"{v['mae_delta']:+.3f} [{v['ci_game_cluster'][0]:+.3f}, {v['ci_game_cluster'][1]:+.3f}] ({v['q_bh_all_prop_groups']:.2f}) | {lrs} | {econ} | "
                     f"{v['seasons_positive']}/{v['seasons']} | {s['gain_without_top10_players']:+.3f} | **{v['status']}** |")
    (DOCS / "NFL_PLAYER_PROP_SIGNAL_CATALOG.md").write_text("\n".join(P) + "\n")


def main() -> int:
    rep = json.loads((BASE / "game_evaluation_report.json").read_text())
    pr = json.loads((BASE / "prop_evaluation_report.json").read_text())
    scr = json.loads((BASE / "stage_a_screen.json").read_text())
    set1 = json.loads((BASE / "hypotheses_set1.json").read_text())
    set2 = json.loads((BASE / "hypotheses_set2.json").read_text())
    head = ["# Football Signal Discovery Wave 1 (NFL) — generated tables", "",
            f"From `game_evaluation_report.json` (code `{rep['code_sha'][:8]}`, set 1 `{rep['set1_sha256'][:12]}`, set 2 `{rep['set2_sha256'][:12]}`) and "
            f"`prop_evaluation_report.json` (code `{pr['code_sha'][:8]}`). Do not edit: `python3 scripts/research/signal_discovery_wave1_report.py`.", "",
            f"Games: {rep['rows']} (2015–2025) with spread {rep['rows_with_spread']}, moneyline {rep['rows_with_ml']}; exclusions {rep['exclusions']}. "
            f"Prop group tests: {pr['hypotheses_tested_group_ablations']}; prop market tests: {pr['hypotheses_tested_market']}.", ""]
    (DOCS / "FOOTBALL_SIGNAL_DISCOVERY_WAVE1_TABLES.md").write_text("\n".join(head + game_tables(rep, scr) + prop_tables(pr)) + "\n")
    reg = registry(rep, pr, set1, set2)
    (BASE / "football_signal_registry.json").write_text(json.dumps(reg, indent=1, sort_keys=True, default=float))
    catalogs(reg, rep, pr)
    print(f"wrote tables, registry ({len(reg['signals'])} signals), catalogs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
