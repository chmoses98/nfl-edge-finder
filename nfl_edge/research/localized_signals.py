"""LOCALIZED SIGNAL RESEARCH (WS3): what became of every registered hypothesis once its future evidence arrived.

A pattern cut from one week is a hypothesis, never a finding. This module answers, every week, the only
questions that can turn one into the other -- and answers them from FUTURE evidence only:

    1. which hypotheses were generated, and from which windows;
    2. which are PREREGISTERED / TESTING (the bar was written down before the test games existed);
    3. how many NEW independent games each has seen since it was generated -- the generation week never counts,
       and the week filter that enforces it lives in `evaluate_prospective`, not here;
    4. whether the effect is PERSISTING, WEAKENING, REVERSING, or still INCONCLUSIVE;
    5-7. its CLV, its outcomes and (where computable) its executable P&L on those new games;
    8. the status the preregistered thresholds would SUGGEST -- a suggestion only; owner approval required.

Two kinds of evidence feed it:

  * LOCALIZED_SLICE hypotheses (mined automatically from scorecard_v3, synchronized PROSPECTIVE_FROZEN only)
    read the same slice out of each later week's scorecard. Weeks hold disjoint games, so per-week clustered
    summaries pool exactly enough (variances add); the pooling rule is printed with every number.
  * GAME_CENTRE_DEVIATION hypotheses (preregistered by hand on main) read the three-arm arm report's
    `deviation_signal` for each later week, one game per horizon view.

THREE STAGES, NEVER MIXED (hypothesis_registry_v2.governance). The section is split so a mined slice can never
read like a test:

  * PREREGISTERED CONFIRMATORY TESTS -- Stage B (PREREGISTERED / TESTING with a frozen record) and Stage C
    (results). The only hypotheses in the Bonferroni family, the only ones given a suggested status.
  * DISCOVERY POOL (hypothesis-generating; not tests) -- Stage A. Top-N in markdown by generation |z|, the full
    list in JSON; generation numbers and descriptive later-week counts only, no status column, no suggestion.
  * SHORTLIST FOR OWNER REVIEW -- a rule-based list of discovery candidates a person might preregister
    (nfl_edge/research/preregistration_shortlist.py). Still not tests.

A governance header always states the slices searched, how many were generated, shortlisted, preregistered and
actively tested, and the multiplicity method, m and per-test alpha.

Everything here is DERIVED and DESCRIPTIVE: it reads registries and scorecards, writes a report and a JSON, and
changes no registry line, no model weight and no production-eligibility state.
"""
from __future__ import annotations

import glob
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone

from nfl_edge.research import hypothesis_registry_v2 as HR
from nfl_edge.research import preregistration_shortlist as PS

LOCALIZED_VERSION = "localized-signals-1.1.0"
SYNC_BUCKET = ("PROSPECTIVE_FROZEN", HR.SYNCHRONIZED)
MAX_DISCOVERY_ROWS = 10
MAX_GENERATED_ROWS = MAX_DISCOVERY_ROWS          # older name, kept for callers


# ------------------------------------------------------------------------------------------------ inputs
def load_hypotheses(paths) -> tuple[dict, list]:
    """Latest state per id across registries (the main-branch registry and the published automatic one).

    Hand-preregistered game-centre hypotheses are `H2-GC-*`, mined slices `HG-*`. An id CAN appear in both once
    an owner preregisters a mined slice (scripts/research/preregister_candidate_v2.py copies its GENERATED line
    verbatim into the committed registry and appends the preregistration there), while the automatic registry
    still holds only the GENERATED line. So on a collision the row further along the governance ladder wins --
    never a GENERATED line over a preregistration -- and between equals the later path wins. Every collision is
    reported, never hidden.
    """
    out, notes = {}, []
    for p in paths:
        if not p or not os.path.exists(p):
            continue
        try:
            cur = HR.current(p)
        except (OSError, ValueError) as exc:
            notes.append(f"{p}: unreadable ({type(exc).__name__})")
            continue
        for hid, row in cur.items():
            if hid in out:
                prev = out[hid]
                if _ladder(row) < _ladder(prev):
                    notes.append(f"{hid} appears in more than one registry; {prev['_registry_path']} ({prev.get('status')}) "
                                 f"kept over {p} ({row.get('status')})")
                    continue
                notes.append(f"{hid} appears in more than one registry; {p} ({row.get('status')}) wins")
            out[hid] = {**row, "_registry_path": p}
    return out, notes


def _ladder(row: dict) -> int:
    """How far along the governance ladder a line is: GENERATED < PREREGISTERED < TESTING < verdict < RETIRED."""
    return HR.STATUSES.index(row.get("status")) if row.get("status") in HR.STATUSES else -1


def slice_week_entry(sc: dict | None, segment: str, value: str, season: int, week: int) -> dict | None:
    """One week's summary of one slice, from the SYNCHRONIZED PROSPECTIVE_FROZEN bucket and nowhere else."""
    if not sc:
        return None
    b = ((sc.get("by_synchronization") or {}).get(SYNC_BUCKET[0]) or {}).get(SYNC_BUCKET[1])
    if not b:
        return {"season": season, "week": week, "games": 0, "paired_n": 0, "effect": None, "se": None,
                "note": "no synchronized PROSPECTIVE_FROZEN bucket this week"}
    m = ((b.get("segments") or {}).get(segment) or {}).get(value)
    if not m:
        return {"season": season, "week": week, "games": 0, "paired_n": 0, "effect": None, "se": None,
                "note": "slice absent this week (no rows, or under the scorecard's per-slice row floor)"}
    o, c, e = m.get("outcome") or {}, m.get("clv") or {}, m.get("executable") or {}
    return {"season": season, "week": week, "games": o.get("clusters") or 0, "paired_n": o.get("model_minus_market_n") or 0,
            "effect": o.get("model_minus_market_brier"), "se": o.get("model_minus_market_se"),
            "brier_model": o.get("brier_model"), "brier_market": o.get("brier_market_horizon"),
            "mean_clv_mid": c.get("mean_clv_mid"), "n_clv_ok": c.get("n_clv_ok") or 0,
            "positive_clv_rate": c.get("positive_clv_rate"), "market_toward_model_rate": c.get("movement_toward_rate"),
            "pnl_net_per_contract": e.get("pnl_net_per_contract"), "n_fee_known": e.get("n_fee_known") or 0,
            "unique_contracts": m.get("n_unique_contracts"), "model_arms": m.get("model_arms")}


def gc_week_entry(signal: dict | None, arm: str, target: str, season: int, week: int) -> dict | None:
    """One week's game-centre counts for one arm and target, per horizon view."""
    if not signal or not signal.get("views"):
        return None
    hz = {}
    for view, per in signal["views"].items():
        b = (per.get(arm) or {}).get(target)
        if not b:
            continue
        sa, sc_ = b.get("share_closer_to_actual_than_snapshot_market"), b.get("share_closer_to_actual_than_close")
        hz[view] = {k: b.get(k) for k in ("n_games", "below_threshold", "toward", "away", "unchanged", "no_close",
                                          "no_view", "signed_close_move_sum", "signed_close_move_n",
                                          "n_with_actual", "n_with_close")}
        hz[view]["closer_snap_k"] = round(sa * (b.get("n_with_actual") or 0)) if sa is not None else 0
        hz[view]["closer_close_k"] = round(sc_ * (b.get("n_with_close") or 0)) if sc_ is not None else 0
    return {"season": season, "week": week, "horizons": hz}


def load_week_scorecards(roots, season: int, weeks) -> dict:
    """{(season, week): scorecard_v3} for the given weeks, first root holding the file wins."""
    out = {}
    for w in weeks:
        label = f"{season}_wk{int(w):02d}"
        for root in roots:
            p = os.path.join(root, f"{label}.scorecard_v3.json") if root else None
            if p and os.path.exists(p):
                try:
                    out[(season, int(w))] = json.load(open(p))
                    break
                except (OSError, ValueError):
                    continue
    return out


def load_gc_signals(arm_reports_root: str, season: int) -> tuple[dict, str | None]:
    """Per-week `deviation_signal` from the NEWEST arm-report batch that carries one.

    Arm reports are rebuilt whole from the evaluation corpus every run, so the newest batch holds every week.
    A batch written before the signal existed is skipped rather than read as "no evidence".
    """
    if not arm_reports_root or not os.path.isdir(arm_reports_root):
        return {}, None
    for batch in sorted(glob.glob(os.path.join(arm_reports_root, "*")), reverse=True):
        out = {}
        for p in sorted(glob.glob(os.path.join(batch, "week*.scorecard.json"))):
            m = re.search(r"week(\d+)\.scorecard\.json$", p)
            try:
                sc = json.load(open(p))
            except (OSError, ValueError):
                continue
            sig = sc.get("deviation_signal")
            if m and sig:
                out[(int(sc.get("season") or season), int(m.group(1)))] = sig
        if out:
            return out, batch
    return {}, None


# ------------------------------------------------------------------------------------------------ assembly
def _window_str(w) -> str:
    if not w:
        return "-"
    return f"{w.get('season')} W{w.get('week_lo')}" + ("" if w.get("week_lo") == w.get("week_hi") else f"-{w.get('week_hi')}")


def future_by_week(h: dict, *, slice_scorecards: dict, gc_signals: dict) -> list:
    """Per-week entries for one hypothesis. Every week available is handed over -- including the generation
    week -- because `evaluate_prospective` is where out-of-window weeks are dropped, and it lists them."""
    kind = h.get("hypothesis_kind") or (h.get("locator") or {}).get("kind")
    loc = h.get("locator") or {}
    out = []
    if kind == HR.KIND_SLICE and loc.get("segment") is not None:
        for (s, w), sc in sorted(slice_scorecards.items()):
            e = slice_week_entry(sc, loc["segment"], str(loc.get("value")), s, w)
            if e:
                out.append(e)
    elif kind == HR.KIND_GAME_CENTRE:
        for (s, w), sig in sorted(gc_signals.items()):
            e = gc_week_entry(sig, loc.get("arm") or "DATA_ONLY", loc.get("target") or "margin", s, w)
            if e:
                out.append(e)
    return out


def build(hypotheses: dict, *, season: int, week: int, label: str, slice_scorecards: dict | None = None,
          gc_signals: dict | None = None, gc_source: str | None = None, registry_notes: list | None = None,
          sources: list | None = None) -> dict:
    """The machine-readable LOCALIZED SIGNAL RESEARCH document for one weekly report."""
    slice_scorecards, gc_signals = slice_scorecards or {}, gc_signals or {}
    live = {k: v for k, v in hypotheses.items() if v.get("status") != "RETIRED"}
    gov = {k: HR.governance(v) for k, v in hypotheses.items()}
    # the Bonferroni family: Stage B and C only. However many slices were mined, they are not in it.
    family = HR.multiplicity_family(live)
    under = sorted(k for k in live if gov[k]["stage"] == HR.STAGE_PREREGISTERED)
    m = len(family)
    by_window = Counter()
    for v in hypotheses.values():
        by_window[(_window_str(v.get("generation_window")), v.get("hypothesis_kind") or (v.get("locator") or {}).get("kind") or "UNSPECIFIED")] += 1
    evals = []
    for hid in sorted(live):
        h = live[hid]
        fm = {"by_week": future_by_week(h, slice_scorecards=slice_scorecards, gc_signals=gc_signals)}
        ev = HR.evaluate_prospective(h, fm, n_under_test=max(m, 1))
        ev["generation_window_str"] = _window_str(h.get("generation_window"))
        ev["generation_evidence"] = h.get("generation_evidence")
        ev["generation_effect"] = h.get("effect_size")
        ev["condition"] = h.get("condition")
        ev["registry_path"] = h.get("_registry_path")
        ev["preregistered_at"] = (h.get("preregistration") or {}).get("preregistered_at")
        ge = h.get("generation_evidence") or {}
        ev["generation_z"] = ge.get("z") if HR._finite(ge.get("z")) else None
        ev["generation_games"] = ge.get("independent_games") or h.get("game_count")
        ev["model_arm"] = ge.get("model_arm") or (h.get("locator") or {}).get("arm")
        ev["candidate_slices_considered"] = h.get("candidate_slices_considered")
        evals.append(ev)
    gen_this_week = sorted(k for k, v in hypotheses.items()
                           if (v.get("generation_window") or {}).get("season") == season
                           and (v.get("generation_window") or {}).get("week_hi") == week)
    shortlist = PS.build(live, season=season, week=week, label=label)
    by_stage = Counter(g["stage"] for g in gov.values())
    searched = {}
    for k, v in hypotheses.items():
        if gov[k]["stage"] == HR.STAGE_DISCOVERY and v.get("candidate_slices_considered"):
            w = _window_str(v.get("generation_window"))
            searched[w] = max(searched.get(w, 0), int(v["candidate_slices_considered"]))
    ev_by_id = {e["id"]: e for e in evals}
    active = sorted(k for k in under if (ev_by_id.get(k) or {}).get("evaluated_weeks") or live[k].get("status") == "TESTING")
    mc = HR.multiplicity(max(m, 1))
    governance = {
        "candidate_slices_examined": sum(searched.values()), "candidate_slices_examined_by_window": dict(sorted(searched.items())),
        "n_discovery": by_stage.get(HR.STAGE_DISCOVERY, 0), "n_shortlisted": shortlist["n_shortlisted"],
        "n_preregistered": len(under), "n_actively_tested": len(active), "actively_tested": active,
        "n_confirmatory_results": by_stage.get(HR.STAGE_CONFIRMATORY, 0), "n_retired": by_stage.get(HR.STAGE_RETIRED, 0),
        "multiplicity": {"method": mc["method"], "m": m, "family": family, "alpha_family": mc["alpha_family"],
                         "alpha_per_test": mc["alpha_family"] / max(m, 1), "z_per_test": mc["z_adjusted"],
                         "members": "Stage B (PREREGISTERED_TEST) and Stage C (CONFIRMATORY_RESULT) only; discovery candidates never"},
        "stage_defects": [{"id": k, "status": hypotheses[k].get("status"), "defects": g["defects"]} for k, g in sorted(gov.items()) if g["defects"]],
        "stages": {"A": f"{HR.STAGE_DISCOVERY}: auto-mined, hypothesis-generating only, never confirmed",
                   "B": f"{HR.STAGE_PREREGISTERED}: deliberately selected; condition, direction, metric, window and thresholds frozen before the first test observation",
                   "C": f"{HR.STAGE_CONFIRMATORY}: future independent evidence under the preregistered rules; SUPPORTED / NOT_SUPPORTED / INCONCLUSIVE, {HR.SUGGESTION_ONLY}"}}
    return {"version": LOCALIZED_VERSION, "label": label, "season": season, "week": week,
            "generated_at": datetime.now(timezone.utc).isoformat(), "registry_sources": sources or [],
            "registry_notes": registry_notes or [],
            "n_hypotheses": len(hypotheses), "by_generation_window": [{"window": w, "kind": k, "n": n} for (w, k), n in sorted(by_window.items())],
            "generated_this_week": gen_this_week, "under_test": under, "n_under_test": m,
            "multiplicity_family": family, "governance": governance, "shortlist": shortlist,
            "multiple_comparisons": mc,
            "slice_weeks_available": sorted(f"{s} W{w}" for s, w in slice_scorecards),
            "game_centre_weeks_available": sorted(f"{s} W{w}" for s, w in gc_signals),
            "game_centre_source": gc_source, "evaluations": evals,
            "thresholds_version": HR.PREREGISTERED_THRESHOLDS["version"],
            "suggestion_note": HR.SUGGESTION_ONLY,
            "no_automatic_learning": ("nothing in this section changes a registry status, a model weight, a feature, a "
                                      "gate or a production-eligibility state; a suggested status is text")}


# ------------------------------------------------------------------------------------------------ rendering
def _f(v, nd=4):
    return "-" if v is None else (f"{v:.{nd}f}" if isinstance(v, float) else str(v))


def cell(v) -> str:
    """A markdown table cell: crossed-slice values ('arm|family') and conditions ('|x - y|') carry pipes."""
    return str(v).replace("|", "\\|")


def _row(ev) -> str:
    """One Stage B/C row: future evidence under the frozen rules, and the SUGGESTED status."""
    met = ev.get("metrics") or {}
    if ev.get("kind") == HR.KIND_GAME_CENTRE:
        p = (met.get("horizons") or {}).get(ev.get("primary_horizon") or "latest_pregame") or {}
        clv = f"close move toward arm {_f(p.get('mean_signed_close_move_points'), 2)} pts"
        outc = (f"toward {p.get('toward', 0)}/{p.get('directional', 0)} = {_f(p.get('toward_rate'), 3)} "
                f"(unchanged {p.get('unchanged', 0)}, no close {p.get('no_close', 0)}, below 1pt {p.get('below_threshold', 0)}); "
                f"closer than snap mkt {_f(p.get('share_closer_to_actual_than_snapshot_market'), 3)}")
        pnl = "n/a (a centre, not a contract)"
    else:
        clv = (f"mean {_f(met.get('mean_clv_mid'))} (n {met.get('n_clv_ok', 0)}), +rate {_f(met.get('positive_clv_rate'), 3)}, "
               f"toward {_f(met.get('market_toward_model_rate'), 3)}") if met else "-"
        outc = (f"model-market {_f(met.get('effect'))} ± {_f(met.get('se'))} (gen {_f(ev.get('generation_effect'))})") if met else "-"
        pnl = (_f(met.get("pnl_net_per_contract")) + f" (n {met.get('n_fee_known', 0)})") if met and met.get("n_fee_known") else "UNAVAILABLE"
    wk = ", ".join(f"W{w}" for _s, w in ev.get("evaluated_weeks") or []) or "none yet"
    excl = "; ".join(f"W{x['week']} {x['reason'].split(' ')[0]}" for x in ev.get("excluded_weeks") or [])
    sug = ev.get("suggested_status") or "none"
    return (f"| {cell(ev.get('id'))} | {ev.get('stage')} ({ev.get('status_now')}) | {ev.get('generation_window_str')} | {ev.get('new_independent_games')} "
            f"({wk}{'; excluded ' + excl if excl else ''}) | {ev.get('trend')} ({ev.get('direction_so_far')}) | {clv} | {outc} | {pnl} | "
            f"{sug} — {ev.get('suggestion_reason') or ''} |")


def _discovery_row(ev) -> str:
    """One Stage A row: what generated it, and how many later games have been SEEN. No status, no suggestion."""
    ge = ev.get("generation_evidence") or {}
    if ev.get("kind") == HR.KIND_SLICE:
        gen = f"{_f(ev.get('generation_effect'))} ± {_f(ge.get('uncertainty'))}"
    else:
        gen = "see registry"
    z = ev.get("generation_z")
    return (f"| {cell(ev.get('id'))} | {ev.get('generation_window_str')} | {cell(ev.get('model_arm') or '-')} | {cell(ev.get('condition'))} | "
            f"{_f(ev.get('generation_games'))} | {gen} | {'-' if z is None else f'{z:.2f}'} | {_f(ev.get('candidate_slices_considered'))} | "
            f"{ev.get('new_independent_games')} |")


def render_governance(doc: dict) -> list:
    g = doc.get("governance") or {}
    mc = g.get("multiplicity") or {}
    by_w = g.get("candidate_slices_examined_by_window") or {}
    L = ["### GOVERNANCE: three stages", "",
         "Stage A DISCOVERY POOL: auto-mined candidates, hypothesis-generating only, never confirmed. "
         "Stage B PREREGISTERED TEST SET: deliberately selected by the owner; condition, direction, metric, window and "
         "thresholds frozen before the first test observation. Stage C CONFIRMATORY RESULT: future independent evidence "
         "under the preregistered rules only (SUPPORTED / NOT_SUPPORTED / INCONCLUSIVE; suggestion only; owner applies).", "",
         "| governance | count |", "|---|---|",
         f"| candidate slices examined (search denominator) | {g.get('candidate_slices_examined', 0)}"
         f"{' (' + ', '.join(f'{w}: {n}' for w, n in by_w.items()) + ')' if by_w else ''} |",
         f"| generated (Stage A discovery candidates; not tests) | {g.get('n_discovery', 0)} |",
         f"| shortlisted for owner review (still Stage A; not preregistered) | {g.get('n_shortlisted', 0)} |",
         f"| preregistered (Stage B) | {g.get('n_preregistered', 0)} |",
         f"| actively tested (Stage B with a future week evaluated, or TESTING) | {g.get('n_actively_tested', 0)} |",
         f"| confirmatory results (Stage C) | {g.get('n_confirmatory_results', 0)} |",
         f"| retired | {g.get('n_retired', 0)} |",
         f"| multiplicity | {mc.get('method')} over m = {mc.get('m')} (Stage B/C members only) -> per-test alpha "
         f"{_f(mc.get('alpha_per_test'))} (z {_f(mc.get('z_per_test'), 3)}) |", ""]
    for d in g.get("stage_defects") or []:
        L.append(f"- stage defect: {cell(d['id'])} is {d['status']} without its record ({', '.join(d['defects'])}); "
                 "treated as a discovery candidate, outside the family, no suggestion")
    if g.get("stage_defects"):
        L.append("")
    return L


def render(doc: dict | None) -> list:
    """Markdown lines for the weekly report. Renders with no registry, no scorecards and no arm report."""
    L = ["## LOCALIZED SIGNAL RESEARCH", "",
         "**Every status below is a suggestion only; owner approval required.** A hypothesis generated from a week "
         "can never be confirmed on that week: only NEW independent games (unit = game) from weeks strictly after "
         "the generation window and inside the registered test window count, and each excluded week is listed. "
         "Nothing here changes a registry status, a model weight or a production-eligibility state.", ""]
    if not doc:
        return L + ["localized-signal inputs unavailable this run (no registry was readable)", ""]
    L += render_governance(doc)
    L += [f"registries: {', '.join(doc.get('registry_sources') or []) or 'none'}; thresholds {doc.get('thresholds_version')}; "
          f"slice weeks available {doc.get('slice_weeks_available') or []}; game-centre weeks available "
          f"{doc.get('game_centre_weeks_available') or []} (source {doc.get('game_centre_source') or 'none: see the arm report LOCALIZED SIGNAL (GAME CENTRE) section'})", ""]
    for n in doc.get("registry_notes") or []:
        L.append(f"- registry note: {n}")
    evs = doc.get("evaluations") or []
    tests = [e for e in evs if e.get("stage") in HR.FAMILY_STAGES]
    disc = [e for e in evs if e.get("stage") == HR.STAGE_DISCOVERY]
    mc = doc.get("multiple_comparisons") or {}

    # ---------------------------------------------------------------- Stage B / C
    L += ["### PREREGISTERED CONFIRMATORY TESTS", "",
          "Stage B (preregistered) and Stage C (results) only: the members of the multiplicity family, and the only "
          "hypotheses given a suggested status.", ""]
    if tests:
        L += ["| hypothesis | stage (status) | test window | preregistered at | condition |", "|---|---|---|---|---|"]
        for e in tests:
            L.append(f"| {cell(e['id'])} | {e['stage']} ({e['status_now']}) | {_window_str(e.get('test_window_used'))} | "
                     f"{e.get('preregistered_at') or '-'} | {cell(e.get('condition'))} |")
        L += ["", f"multiple comparisons: {mc.get('method')} over m = {mc.get('m')} Stage B/C hypotheses -> per-test alpha "
              f"{_f(mc.get('alpha_adjusted'))} (z {_f(mc.get('z_adjusted'), 3)}). Discovery candidates are not in the family.", "",
              "| hypothesis | stage (status) | generated | new games (weeks) | trend (direction so far) | CLV | outcomes | exec P&L net | suggested status (suggestion only; owner approval required) |",
              "|---|---|---|---|---|---|---|---|---|"]
        L += [_row(e) for e in tests]
        L += ["", "Trend: PERSISTING = same sign and at least half the generation effect; WEAKENING = same sign, smaller; "
              "REVERSING = opposite sign; INCONCLUSIVE = below the preregistered game floor (the descriptive direction is in "
              "brackets).", ""]
    else:
        L += ["none preregistered", ""]

    # ---------------------------------------------------------------- Stage A
    L += ["### DISCOVERY POOL (hypothesis-generating; not tests)", "",
          "**Not tests. Not findings. Not in the multiplicity family, and given no status.** Each row is a pattern mined "
          "from the week shown, selected from the slices searched that week. Later-week games are counted for "
          "information only; nothing here can be confirmed unless an owner preregisters it first.", ""]
    if doc.get("by_generation_window"):
        L += ["| generation window | kind | n |", "|---|---|---|"] + [f"| {r['window']} | {r['kind']} | {r['n']} |" for r in doc["by_generation_window"]]
    else:
        L.append("no hypotheses registered yet")
    L += ["", f"generated from this week ({doc.get('label')}): {len(doc.get('generated_this_week') or [])} — HYPOTHESIS_GENERATING only", ""]
    if disc:
        top = sorted(disc, key=lambda e: (-(abs(e["generation_z"]) if e.get("generation_z") is not None else -1), str(e.get("id"))))
        L += [f"top {min(len(top), MAX_DISCOVERY_ROWS)} of {len(top)} by generation |z| (descriptive; the full list is in "
              f"`{doc.get('label')}.localized_signals.json`):", "",
              "| discovery candidate | generated | arm | condition | gen games | gen effect ± SE | gen z | slices searched | later games seen (descriptive) |",
              "|---|---|---|---|---|---|---|---|---|"]
        L += [_discovery_row(e) for e in top[:MAX_DISCOVERY_ROWS]]
        if len(top) > MAX_DISCOVERY_ROWS:
            L += ["", f"{len(top) - MAX_DISCOVERY_ROWS} further discovery candidates are in `{doc.get('label')}.localized_signals.json`."]
        L.append("")

    # ---------------------------------------------------------------- shortlist
    L += PS.render(doc.get("shortlist"))
    return L
