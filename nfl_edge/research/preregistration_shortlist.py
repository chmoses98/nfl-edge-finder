"""SHORTLIST FOR OWNER REVIEW: which discovery candidates a person might choose to preregister.

Stage A (the discovery pool) holds every mined slice; hundreds of them, each HYPOTHESIS_GENERATING. Stage B
(preregistered tests) must be DELIBERATELY chosen, because every member widens the Bonferroni family and costs
every other test power. This module does the tedious part of that choice by rule, and nothing else:

    it READS discovery candidates (their frozen `generation_evidence`), applies the fixed rules below, and returns
    a ranked list with the reason each one qualifies -- or the reason it did not.

It writes no registry line, preregisters nothing, promotes nothing and suggests no status. A shortlisted
candidate is still a discovery candidate: not a test, not a finding. The owner preregisters one with
`scripts/research/preregister_candidate_v2.py`, before the first kickoff of its test window, or not at all.

THE RULES (`SHORTLIST_RULES`, versioned; deterministic; generation evidence only):

  1. Stage A only: GENERATED, a LOCALIZED_SLICE, no stage defects.
  2. Synchronized PROSPECTIVE_FROZEN evidence only (the only admissible basis for a model-vs-market slice).
  3. One model arm: a slice pooling arms describes none of them.
  4. >= 16 independent games (the WATCH floor) behind the paired outcomes.
  5. |effect| / clustered SE clears the SEARCH-ADJUSTED bar: Bonferroni over `candidate_slices_considered`,
     the number of slices searched in the candidate's generation week (K = 422 -> |z| >= 3.85). A slice that
     only looks unusual because 422 were looked at does not qualify.
  6. CLV agrees with the Brier effect: model-better-than-market (effect < 0) needs mean CLV > 0; market-better
     (effect > 0) needs mean CLV < 0. Missing CLV disqualifies.
  7. At most one per (model arm, family), and one per identical row set: the crossed slices overlap (arm x
     family x horizon sits inside arm x family), and two segmentations can name the very same rows
     (market_family == TEAM_TOTAL and stat_family == team_points), so near-duplicates of one pattern are not
     offered as separate choices. The largest |z| is kept; the rest are listed as `near_duplicates_not_offered`.
  8. The proposed confirmatory window starts after BOTH the generation window and the report week, and ends
     inside the window fixed at registration (week 18 at the latest). No remaining week -> not offered.

Executable economics are reported as recorded (fee-adjusted P&L per contract, or UNAVAILABLE); they are not a
rule, because an entry-at-ask P&L on one generation week is itself a hypothesis-generating number.
"""
from __future__ import annotations

import math
from statistics import NormalDist

from nfl_edge.research import hypothesis_registry_v2 as HR

SHORTLIST_VERSION = "prereg-shortlist-1.0.0"
MAX_MARKDOWN_ROWS = 10
SHORTLIST_RULES = {
    "version": SHORTLIST_VERSION,
    "stage": HR.STAGE_DISCOVERY,
    "kind": HR.KIND_SLICE,
    "evidence_basis": "SYNCHRONIZED PROSPECTIVE_FROZEN rows only",
    "single_model_arm": True,
    "min_independent_games": 16,
    "search_correction": {"method": "BONFERRONI", "over": "candidate_slices_considered (slices searched in the generation week)",
                          "alpha_family": 0.05, "two_sided": True},
    "clv_must_agree_with_brier_effect": True,
    "one_per": "(model_arm, family)",
    "window": "first week after both the generation window and the report week, through the registered window's end",
    "evidence_used": "generation evidence as frozen in the registry; later weeks are never used to choose",
}
LABEL = "SHORTLISTED_FOR_OWNER_REVIEW (not preregistered; not a test)"


def search_adjusted_z(k: int, alpha_family: float = 0.05) -> float:
    """Two-sided Bonferroni critical |z| over k searched slices."""
    k = max(int(k or 1), 1)
    return NormalDist().inv_cdf(1 - alpha_family / (2 * k))


def _p_two_sided(z: float) -> float:
    return 2 * (1 - NormalDist().cdf(abs(z)))


def _family_key(h: dict, ev: dict) -> tuple:
    loc = h.get("locator") or {}
    fam = ev.get("family_group") or f"{loc.get('segment')}={loc.get('value')}"
    return (ev.get("model_arm"), fam)


def _fingerprint(ev: dict, eff, se) -> tuple:
    """Two slices with the same arm, games, paired rows, effect and SE are the same rows under two names."""
    return (ev.get("model_arm"), ev.get("independent_games"), ev.get("paired_settled_rows"),
            round(float(eff), 12), round(float(se), 12))


def _economics(ev: dict) -> dict:
    e = ev.get("executable_pnl") or {}
    if e.get("state") == "AVAILABLE" and HR._finite(e.get("net_per_contract")) and (e.get("n_fee_known") or 0) > 0:
        return {"state": "AVAILABLE", "net_per_contract": e.get("net_per_contract"), "gross_per_contract": e.get("gross_per_contract"),
                "n_fee_known": e.get("n_fee_known"), "n_taken": e.get("n_taken"),
                "note": "generation week only; entry at the horizon ask, one contract, fee once; not proven EV"}
    return {"state": "UNAVAILABLE", "reason": e.get("reason") or "no valid fee-adjusted executable P&L was recorded"}


def assess(h: dict, *, report_season: int, report_week: int, rules: dict = SHORTLIST_RULES) -> dict:
    """One candidate against the rules: {"qualifies": bool, "reasons_failed": [...], "entry": {...} | None}."""
    gov = HR.governance(h)
    ev = h.get("generation_evidence") or {}
    fail = []
    kind = h.get("hypothesis_kind") or (h.get("locator") or {}).get("kind")
    if gov["stage"] != rules["stage"] or h.get("status") != "GENERATED" or gov["defects"]:
        fail.append("NOT_A_DISCOVERY_CANDIDATE")
    if kind != rules["kind"]:
        fail.append("NOT_A_LOCALIZED_SLICE")
    if ev.get("synchronization_basis") != HR.SYNCHRONIZED or ev.get("evidence_class") != "PROSPECTIVE_FROZEN":
        fail.append("NOT_SYNCHRONIZED_PROSPECTIVE_FROZEN")
    arms = ev.get("model_arms") or []
    if len(arms) != 1 or not ev.get("model_arm"):
        fail.append("POOLS_OR_LACKS_MODEL_ARM")
    games = int(ev.get("independent_games") or h.get("game_count") or 0)
    if games < int(rules["min_independent_games"]):
        fail.append("FEWER_THAN_MIN_INDEPENDENT_GAMES")
    eff = h.get("effect_size") if HR._finite(h.get("effect_size")) else ev.get("effect_size")
    se = h.get("uncertainty") if HR._finite(h.get("uncertainty")) else ev.get("uncertainty")
    k = h.get("candidate_slices_considered") or ev.get("candidate_slices_considered")
    z = z_req = None
    if not HR._finite(eff) or not HR._finite(se) or float(se) < HR.SE_FLOOR:
        fail.append("NO_FINITE_EFFECT_OR_SE")
    elif not k:
        fail.append("NO_SEARCH_DENOMINATOR")
    else:
        z = float(eff) / float(se)
        z_req = search_adjusted_z(int(k), rules["search_correction"]["alpha_family"])
        if abs(z) < z_req:
            fail.append("BELOW_SEARCH_ADJUSTED_BAR")
    clv = ev.get("mean_clv_mid")
    if not HR._finite(clv) or not (ev.get("n_clv_ok") or 0):
        fail.append("CLV_MISSING")
    elif HR._finite(eff) and not ((eff < 0 and clv > 0) or (eff > 0 and clv < 0)):
        fail.append("CLV_DISAGREES_WITH_BRIER_EFFECT")
    gen, reg = h.get("generation_window") or {}, HR.registered_future_window(h) or {}
    window = None
    if gen and reg and int(reg.get("season", -1)) == int(report_season):
        lo = max(int(gen["week_hi"]) + 1 if int(gen["season"]) == int(report_season) else 1, int(report_week) + 1, int(reg["week_lo"]))
        hi = int(reg["week_hi"])
        if lo <= hi:
            window = {"season": int(report_season), "week_lo": lo, "week_hi": hi}
    if window is None:
        fail.append("NO_REMAINING_CONFIRMATORY_WINDOW")
    if fail:
        return {"qualifies": False, "reasons_failed": fail, "entry": None}
    p = _p_two_sided(z)
    direction = "model Brier below market Brier" if eff < 0 else "market Brier below model Brier"
    reason = (f"{games} independent games >= {rules['min_independent_games']}; |z| {abs(z):.2f} >= {z_req:.2f} "
              f"(Bonferroni over {k} slices searched); mean CLV {clv:+.4f} agrees with the Brier effect; "
              f"single arm {ev.get('model_arm')}; synchronized PROSPECTIVE_FROZEN")
    entry = {"id": h.get("id"), "label": LABEL, "stage": HR.STAGE_DISCOVERY,
             "market_family": ev.get("family_group") or h.get("market_family"), "condition": h.get("condition"),
             "segment": (h.get("locator") or {}).get("segment"), "segment_value": (h.get("locator") or {}).get("value"),
             "model_arm": ev.get("model_arm"), "model_versions": ev.get("model_versions"), "horizon_label": ev.get("horizon_label"),
             "generation_window": gen, "generation_week": gen.get("week_hi"), "direction": direction,
             "independent_games": games, "paired_settled_rows": ev.get("paired_settled_rows"), "unique_contracts": ev.get("unique_contracts"),
             "effect_size": eff, "clustered_se": se, "ci95": [eff - 1.959963984540054 * se, eff + 1.959963984540054 * se],
             "z": z, "p_two_sided": p,
             "multiplicity": {"method": "BONFERRONI", "slices_searched": int(k), "z_required": z_req,
                              "p_bonferroni": min(1.0, p * int(k)),
                              "note": ("search correction for choosing this slice; if preregistered it joins the "
                                       "Stage B/C family and is tested at 0.05 / m on FUTURE games only")},
             "mean_clv_mid": clv, "se_clv_mid_clustered": ev.get("se_clv_mid_clustered"), "n_clv_ok": ev.get("n_clv_ok"),
             "positive_clv_rate": ev.get("positive_clv_rate"), "toward_close_rate": ev.get("market_toward_model_rate"),
             "executable_economics": _economics(ev),
             "proposed_confirmatory_window": window,
             "reason_qualifies": reason,
             "owner_action": (f"python3 scripts/research/preregister_candidate_v2.py --id '{h.get('id')}' "
                              f"--test-week-lo {window['week_lo']} --test-week-hi {window['week_hi']} "
                              "--first-test-kickoff <ISO kickoff of the first game in the window> --confirm")}
    return {"qualifies": True, "reasons_failed": [], "entry": entry}


def build(hypotheses: dict, *, season: int, week: int, label: str, rules: dict = SHORTLIST_RULES) -> dict:
    """The shortlist document. Deterministic: the same registry state gives the same list in the same order."""
    from collections import Counter
    pool = {hid: h for hid, h in (hypotheses or {}).items() if HR.stage(h) == HR.STAGE_DISCOVERY}
    failed, kept = Counter(), []
    for hid in sorted(pool):
        a = assess(pool[hid], report_season=season, report_week=week, rules=rules)
        if a["qualifies"]:
            kept.append((pool[hid], a["entry"]))
        else:
            for r in a["reasons_failed"]:
                failed[r] += 1
    kept.sort(key=lambda he: (-(abs(he[1]["z"]) - he[1]["multiplicity"]["z_required"]), he[1]["id"]))
    seen, rows_seen, out, dups = {}, {}, [], []
    for h, e in kept:
        ev = h.get("generation_evidence") or {}
        key, fp = _family_key(h, ev), _fingerprint(ev, e["effect_size"], e["clustered_se"])
        if key in seen:
            dups.append({"id": e["id"], "reason": "SAME_ARM_AND_FAMILY", "kept": seen[key], "z": e["z"]})
            continue
        if fp in rows_seen:
            dups.append({"id": e["id"], "reason": "IDENTICAL_ROW_SET", "kept": rows_seen[fp], "z": e["z"]})
            continue
        seen[key], rows_seen[fp] = e["id"], e["id"]
        out.append(e)
    for i, e in enumerate(out, 1):
        e["rank"] = i
    return {"version": SHORTLIST_VERSION, "label": label, "season": season, "week": week, "rules": rules,
            "status_note": ("NOT TESTS. Nothing here is preregistered, promoted or suggested; the owner must "
                            "preregister a candidate (scripts/research/preregister_candidate_v2.py) before the "
                            "first kickoff of its window for it to become a Stage-B test"),
            "discovery_candidates_considered": len(pool), "qualifying_before_dedup": len(kept),
            "n_shortlisted": len(out), "shortlist": out, "near_duplicates_not_offered": dups,
            "not_qualifying_by_reason": dict(sorted(failed.items()))}


def _f(v, nd=4):
    return "-" if v is None else (f"{v:.{nd}f}" if isinstance(v, float) else str(v))


def render(doc: dict | None, max_rows: int = MAX_MARKDOWN_ROWS) -> list:
    L = ["### SHORTLIST FOR OWNER REVIEW (not tests; owner must preregister)", "",
         "**These are discovery candidates, not tests and not findings.** A rule picked them from the discovery pool "
         "for a person to consider; nothing has been preregistered, promoted or suggested. Only an owner's "
         "`scripts/research/preregister_candidate_v2.py` call, made before the first kickoff of the proposed window, "
         "turns one into a Stage-B test -- and each one added widens the multiplicity family.", ""]
    if not doc:
        return L + ["shortlist unavailable this run", ""]
    r = doc.get("rules") or {}
    sc = r.get("search_correction") or {}
    L += [f"rules {doc.get('version')}: Stage A LOCALIZED_SLICE, synchronized PROSPECTIVE_FROZEN, one model arm, "
          f">= {r.get('min_independent_games')} independent games, |effect| / clustered SE above the {sc.get('method')} "
          f"bar over the slices searched, CLV sign agreeing with the Brier effect, one per (model arm, family). "
          f"Considered {doc.get('discovery_candidates_considered')}; qualifying {doc.get('qualifying_before_dedup')}; "
          f"near-duplicates not offered {len(doc.get('near_duplicates_not_offered') or [])}; shortlisted {doc.get('n_shortlisted')}.", ""]
    rows = doc.get("shortlist") or []
    if not rows:
        L += ["no discovery candidate meets the shortlist rules", ""]
    else:
        L += ["| # | candidate | family / condition | arm (version) | gen week | games | effect ± clustered SE (95% CI) | |z| vs search bar (slices) | CLV mean / +rate / toward-close | executable (gen week) | proposed window |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        from nfl_edge.research.localized_signals import cell
        for e in rows[:max_rows]:
            ec = e["executable_economics"]
            econ = (f"net {_f(ec['net_per_contract'])} / contract (n {ec['n_fee_known']})" if ec["state"] == "AVAILABLE" else "UNAVAILABLE")
            w = e["proposed_confirmatory_window"]
            L.append(f"| {e['rank']} | {cell(e['id'])} | {cell(e['market_family'])}: {cell(e['condition'])} | {cell(e['model_arm'])} "
                     f"({cell(','.join(e.get('model_versions') or []) or '-')}) | W{e['generation_week']} | {e['independent_games']} | "
                     f"{_f(e['effect_size'])} ± {_f(e['clustered_se'])} ({_f(e['ci95'][0])}, {_f(e['ci95'][1])}) | "
                     f"{abs(e['z']):.2f} vs {e['multiplicity']['z_required']:.2f} ({e['multiplicity']['slices_searched']}) | "
                     f"{_f(e['mean_clv_mid'])} / {_f(e['positive_clv_rate'], 3)} / {_f(e['toward_close_rate'], 3)} | {econ} | "
                     f"{w['season']} W{w['week_lo']}-{w['week_hi']} |")
        if len(rows) > max_rows:
            L.append("")
            L.append(f"{len(rows) - max_rows} further shortlisted candidates are in `{doc.get('label')}.preregistration_shortlist.json`.")
        L.append("")
    if doc.get("not_qualifying_by_reason"):
        L += [f"not qualifying, by reason (a candidate can fail several): {doc['not_qualifying_by_reason']}", ""]
    return L
