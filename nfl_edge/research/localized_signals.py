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

LOCALIZED_VERSION = "localized-signals-1.0.0"
SYNC_BUCKET = ("PROSPECTIVE_FROZEN", HR.SYNCHRONIZED)
MAX_GENERATED_ROWS = 25


# ------------------------------------------------------------------------------------------------ inputs
def load_hypotheses(paths) -> tuple[dict, list]:
    """Latest state per id across registries (the main-branch registry and the published automatic one).

    The two never share ids: hand-preregistered game-centre hypotheses are `H2-GC-*`, mined slices `HG-*`.
    Should an id appear in both, the later path wins and the collision is reported, never hidden.
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
                notes.append(f"{hid} appears in more than one registry; {p} wins")
            out[hid] = {**row, "_registry_path": p}
    return out, notes


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
    under = sorted(k for k, v in live.items() if v.get("status") in HR.UNDER_TEST)
    m = len(under)
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
        evals.append(ev)
    gen_this_week = sorted(k for k, v in hypotheses.items()
                           if (v.get("generation_window") or {}).get("season") == season
                           and (v.get("generation_window") or {}).get("week_hi") == week)
    return {"version": LOCALIZED_VERSION, "label": label, "season": season, "week": week,
            "generated_at": datetime.now(timezone.utc).isoformat(), "registry_sources": sources or [],
            "registry_notes": registry_notes or [],
            "n_hypotheses": len(hypotheses), "by_generation_window": [{"window": w, "kind": k, "n": n} for (w, k), n in sorted(by_window.items())],
            "generated_this_week": gen_this_week, "under_test": under, "n_under_test": m,
            "multiple_comparisons": HR.multiplicity(max(m, 1)),
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
    return (f"| {cell(ev.get('id'))} | {ev.get('status_now')} | {ev.get('generation_window_str')} | {ev.get('new_independent_games')} "
            f"({wk}{'; excluded ' + excl if excl else ''}) | {ev.get('trend')} ({ev.get('direction_so_far')}) | {clv} | {outc} | {pnl} | "
            f"{sug} — {ev.get('suggestion_reason') or ''} |")


def render(doc: dict | None) -> list:
    """Markdown lines for the weekly report. Renders with no registry, no scorecards and no arm report."""
    L = ["## LOCALIZED SIGNAL RESEARCH", "",
         "**Every status below is a suggestion only; owner approval required.** A hypothesis generated from a week "
         "can never be confirmed on that week: only NEW independent games (unit = game) from weeks strictly after "
         "the generation window and inside the registered test window count, and each excluded week is listed. "
         "Nothing here changes a registry status, a model weight or a production-eligibility state.", ""]
    if not doc:
        return L + ["localized-signal inputs unavailable this run (no registry was readable)", ""]
    mc = doc.get("multiple_comparisons") or {}
    L += [f"registries: {', '.join(doc.get('registry_sources') or []) or 'none'}; thresholds {doc.get('thresholds_version')}; "
          f"slice weeks available {doc.get('slice_weeks_available') or []}; game-centre weeks available "
          f"{doc.get('game_centre_weeks_available') or []} (source {doc.get('game_centre_source') or 'none: see the arm report LOCALIZED SIGNAL (GAME CENTRE) section'})", ""]
    for n in doc.get("registry_notes") or []:
        L.append(f"- registry note: {n}")
    L += ["### 1. Hypotheses generated, by generation window", ""]
    if doc.get("by_generation_window"):
        L += ["| generation window | kind | n |", "|---|---|---|"] + [f"| {r['window']} | {r['kind']} | {r['n']} |" for r in doc["by_generation_window"]]
    else:
        L.append("no hypotheses registered yet")
    L += ["", f"generated from this week ({doc.get('label')}): {len(doc.get('generated_this_week') or [])} — HYPOTHESIS_GENERATING only", ""]
    L += ["### 2. Preregistered / testing", ""]
    evs = doc.get("evaluations") or []
    under = [e for e in evs if e.get("status_now") in HR.UNDER_TEST]
    if under:
        L += ["| hypothesis | status | test window | preregistered at | condition |", "|---|---|---|---|---|"]
        for e in under:
            L.append(f"| {cell(e['id'])} | {e['status_now']} | {_window_str(e.get('test_window_used'))} | {e.get('preregistered_at') or '-'} | {cell(e.get('condition'))} |")
    else:
        L.append("none")
    L += ["", f"multiple comparisons: {mc.get('method')} over m = {mc.get('m')} hypotheses under test -> per-hypothesis alpha "
          f"{_f(mc.get('alpha_adjusted'))} (z {_f(mc.get('z_adjusted'), 3)}). Mined slices were selected from "
          "`candidate_slices_considered` slices each; that denominator travels with every candidate.", ""]
    L += ["### 3-8. New independent games, trend, CLV, outcomes, executable P&L, suggested status", "",
          "| hypothesis | status | generated | new games (weeks) | trend (direction so far) | CLV | outcomes | exec P&L net | suggested status (suggestion only; owner approval required) |",
          "|---|---|---|---|---|---|---|---|---|"]
    gen = sorted([e for e in evs if e.get("status_now") not in HR.UNDER_TEST],
                 key=lambda e: (-(e.get("new_independent_games") or 0), str(e.get("id"))))
    for e in under + gen[:MAX_GENERATED_ROWS]:
        L.append(_row(e))
    if not evs:
        L.append("| - | - | - | - | - | - | - | - | - |")
    if len(gen) > MAX_GENERATED_ROWS:
        L.append("")
        L.append(f"{len(gen) - MAX_GENERATED_ROWS} further GENERATED hypotheses are in `{doc.get('label')}.localized_signals.json`.")
    L += ["", "Trend: PERSISTING = same sign and at least half the generation effect; WEAKENING = same sign, smaller; "
          "REVERSING = opposite sign; INCONCLUSIVE = below the preregistered game floor (the descriptive direction is in "
          "brackets). GENERATED hypotheses were never preregistered, so their future evidence is descriptive and "
          "they carry no suggestion.", ""]
    return L
