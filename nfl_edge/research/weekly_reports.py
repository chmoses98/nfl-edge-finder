"""The three weekly research reports, rendered from evidence the pipeline computed. RESEARCH ONLY.

    BOARD_EDGE_DISCOVERY.md   what the full board taught: coverage, families, price bands (by ask AND by mid),
                              conditional patterns with every safeguard, ladders, preregistered tests, rejections
    SCRIPT_AUTOPSY.md         what kind of game happened, where in environment -> volume -> opportunity ->
                              efficiency reality left expectation, and which player misses better scripting could
                              plausibly have prevented
    THESIS_IMPROVEMENT.md     what to pay attention to before games, what should NOT change, the hypotheses under
                              test and the research tags for the coming week, the expression autopsy, limitations

Pure functions of their inputs: no clock, no randomness beyond the miner's fixed seeds, so the same evidence
renders the same bytes (pinned by test). Every number carries its sample; every report says it authorises
nothing.
"""
from __future__ import annotations

from collections import Counter

AUTHORITY_LINE = ("> RESEARCH ONLY. Nothing in this report selects, sizes, gates or authorises a wager, changes a model, "
                  "a threshold or a stake, or promotes any research arm. Patterns here are hypothesis-generating unless the "
                  "hypothesis registry says otherwise.")


def _n(x, nd=3):
    if x is None:
        return "—"
    try:
        return f"{float(x):.{nd}f}"
    except (TypeError, ValueError):
        return str(x)


def _pct(x, nd=1):
    return "—" if x is None else f"{100 * float(x):.{nd}f}%"


def _c(x):
    return "—" if x is None else f"{100 * float(x):+.1f}c"


def _ci(ci, scale=100.0, unit="c"):
    if not ci:
        return "—"
    return f"[{ci[0] * scale:+.1f}, {ci[1] * scale:+.1f}]{unit}"


# ------------------------------------------------------------------------------------------------ board edge
def render_board_edge(doc: dict) -> str:
    L = []
    a = L.append
    a(f"# BOARD EDGE DISCOVERY — {doc['scope_title']}")
    a("")
    a(AUTHORITY_LINE)
    a("")
    a(f"_Inputs: {doc['inputs']}_")
    a("")
    cov = doc["coverage"]
    t = cov["total"]
    a("## 1. Coverage — what was and was not analysed")
    a("")
    a("| stage | contracts |")
    a("|---|---|")
    for s in cov["funnel_stages"]:
        a(f"| {s} | {t.get(s, 0):,} |")
    a("")
    a("Exclusions (every contract that left the funnel, by reason):")
    a("")
    for reason, n in list(t["exclusions"].items())[:40]:
        a(f"- {n:,} — {reason}")
    if len(t["exclusions"]) > 40:
        a(f"- … {len(t['exclusions']) - 40} further reasons in `board_coverage.json`")
    a("")
    uni = cov.get("discovery_universe") or {}
    if uni:
        a("Discovery universe: " + " · ".join(f"{k} {v['n']:,}" for k, v in uni.items()))
        a("")
    a("By week × family (primary horizon):")
    a("")
    a("| week | family | discovered | captured | football-settled | analysed |")
    a("|---|---|---|---|---|---|")
    for r in cov["by_week_family"]:
        if r["discovered"]:
            a(f"| {r['week']} | {r['family']} | {r['discovered']:,} | {r['captured_pregame']:,} | {r['football_settled']:,} | {r['analyzed_primary']:,} |")
    a("")
    m = doc["miner"]["latest_pregame"]
    a("## 2. How to read the cells")
    a("")
    a(f"Unit = one contract SIDE bought at its executable ask. **mid bias** = event rate − the side's mid (is the market's "
      f"fair price wrong?). **return** = payout − ask − fee per contract (is it exploitable after costs?). Intervals are "
      f"game-clustered bootstrap (B={m['floors']['bootstrap_B']}); rare-outcome cells also get a binomial floor. Cells with "
      f"< {m['floors']['min_games']} games, < {m['floors']['min_weeks']} weeks or < {m['floors']['min_contracts']} sides are "
      f"DESCRIPTIVE_ONLY. Multiplicity: Benjamini–Hochberg q ≤ {m['floors']['bh_q']} across all {m['n_cells_tested']} tested "
      f"cells (≈{m['expected_false_ci_exclusions_under_null']} would exclude zero by chance alone).")
    a("")
    a(f"Status counts at latest pregame: {', '.join(f'{k} {v}' for k, v in sorted(m['status_counts'].items()))}.")
    a("")
    a("## 3. Price bands")
    a("")
    for title, sid, dim in (("Five full-game families, YES side, binned by QUOTED MID (the owner's Weeks 1–3 framing)",
                             "S17_game_family_x_side_x_mid", "mid_band"),
                            ("Whole board, binned by the ASK actually paid", "S01_side_x_price", "price_band")):
        a(f"### {title}")
        a("")
        a("| side | band | sides | games | mean price/mid | event rate | mid bias (CI) | return (CI) | by week (event − price) | status |")
        a("|---|---|---|---|---|---|---|---|---|---|")
        for c in [c for c in m["cells"] if c["slice"] == sid]:
            d = c["dims"]
            if sid.startswith("S17") and d.get("side") != "YES":
                continue
            bw = " ".join(f"W{w}:{100 * (v['event_rate'] - v['mean_price']):+.1f}" for w, v in c["by_week"].items())
            a(f"| {d.get('side')} | {d.get(dim)} | {c['n_contracts']:,} | {c['n_games']} | "
              f"{_n(c['mean_side_mid'] if sid.startswith('S17') else c['mean_price'])} | {_n(c['event_rate'])} | "
              f"{_c(c.get('mid_bias'))} {_ci(c.get('mid_bias_ci'))} | {_c(c['mean_return'])} {_ci(c.get('ci'))} | {bw} | {c['status']} |")
        a("")
    a("## 4. Market families")
    a("")
    fam = {}
    for c in m["cells"]:
        if c["slice"] == "S02_family_x_side_x_price":
            f = c["dims"]["family"]
            agg = fam.setdefault(f, {"n": 0, "ret": 0.0, "won": 0.0, "mid": 0.0, "nmid": 0})
            agg["n"] += c["n_contracts"]; agg["ret"] += c["mean_return"] * c["n_contracts"]
    a("| family | contract-sides | mean return at the ask |")
    a("|---|---|---|")
    for f, v in sorted(fam.items(), key=lambda kv: -kv[1]["n"]):
        a(f"| {f} | {v['n']:,} | {_c(v['ret'] / v['n'] if v['n'] else None)} |")
    a("")
    a("## 5. Conditional patterns that survived every safeguard (CANDIDATE) — discovery only")
    a("")
    cands = sorted([c for c in m["cells"] if c["status"] == "CANDIDATE"], key=lambda c: c.get("q_bh") or 1)
    a(f"{len(cands)} CANDIDATE cells at latest pregame. Negative returns dominate: most survivors are COST "
      f"(half-spread + fee) or favourite–longshot effects, not hidden value. Mid bias says which are mispricing.")
    a("")
    a("| cell | sides | games | weeks | price | event | mid bias (CI) | return (CI) | q | by week |")
    a("|---|---|---|---|---|---|---|---|---|---|")
    for c in cands[:40]:
        bw = " ".join(f"W{w}:{100 * v['mean_return']:+.1f}" for w, v in c["by_week"].items())
        a(f"| `{c['cell_id']}` | {c['n_contracts']:,} | {c['n_games']} | {c['n_weeks']} | {_n(c['mean_price'])} | {_n(c['event_rate'])} | "
          f"{_c(c.get('mid_bias'))} {_ci(c.get('mid_bias_ci'))} | {_c(c['mean_return'])} {_ci(c.get('ci'))} | {_n(c.get('q_bh'))} | {bw} |")
    a("")
    unst = [c for c in m["cells"] if c["status"] == "UNSTABLE"]
    a(f"## 6. Patterns that did NOT survive (rejected in discovery)")
    a("")
    a(f"- UNSTABLE (a week or a held-out week flips the sign): {len(unst)} cells. Largest:")
    for c in sorted(unst, key=lambda c: abs(c["mean_return"]), reverse=True)[:12]:
        bw = " ".join(f"W{w}:{100 * v['mean_return']:+.1f}" for w, v in c["by_week"].items())
        a(f"  - `{c['cell_id']}` {_c(c['mean_return'])} ({c['n_games']} games) — {bw}")
    ns = m["status_counts"].get("NO_SIGNAL", 0)
    nm = m["status_counts"].get("NOT_SIGNIFICANT_AFTER_MULTIPLICITY", 0)
    a(f"- NO_SIGNAL (interval includes zero): {ns} cells. NOT_SIGNIFICANT_AFTER_MULTIPLICITY: {nm} cells.")
    a("")
    lad = doc.get("ladders") or {}
    a("## 7. Ladders (one ladder = one thesis)")
    a("")
    a(f"{lad.get('n_ladders', 0):,} ladders with ≥ 3 live rungs at latest pregame. {lad.get('caution', '')}.")
    a("")
    a("| family | ladders | best realised = main rung | best CLV = main rung | incoherent | a rung ≥ 2c under the ladder's own fair curve |")
    a("|---|---|---|---|---|---|")
    for f, v in (lad.get("by_family") or {}).items():
        a(f"| {f} | {v.get('ladders', 0)} | {_pct(v.get('share_best_realised_main'))} | {_pct(v.get('share_best_clv_main'))} | "
          f"{v.get('incoherent', 0)} | {v.get('coherence_gap_ge_2c', 0)} |")
    a("")
    a("## 8. Preregistered tests (discovery reading vs prospective reading)")
    a("")
    a("| id | hypothesis | metric | discovery (W1–3) | prospective weeks | prospective value (family CI) | games | suggested |")
    a("|---|---|---|---|---|---|---|---|")
    for h in doc["hypotheses"]:
        disc = h.get("discovery") or {}
        pr = h.get("prospective") or {}
        ev = pr.get("evaluation") or {}
        a(f"| {h['id']} | {h['title']} | {h['metric']} ({'+' if h['sign'] > 0 else '−'}) | {_n(disc.get('value'), 4)} "
          f"{_ci(disc.get('ci'), 1.0, '')} | {pr.get('weeks') or '—'} | {_n(ev.get('value'), 4)} {_ci(ev.get('ci_family'), 1.0, '')} | "
          f"{ev.get('n_games', '—')} | {(pr.get('suggestion') or {}).get('suggested_status', '—')} |")
    a("")
    a("_Suggested statuses are suggestions; only the owner transitions the registry. Weeks 1–3 are never evidence for "
      "these hypotheses._")
    a("")
    a("## 9. Patterns worth testing next (not registered)")
    a("")
    for c in cands[:10]:
        a(f"- `{c['cell_id']}` — a CANDIDATE in discovery; would need its own preregistration before any week it is "
          f"tested on (registering it now would make Weeks 1–3 its generation window).")
    a("")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------------------------ script autopsy
def render_script_autopsy(doc: dict) -> str:
    L = []
    a = L.append
    s = doc["script_summary"]
    a(f"# SCRIPT AUTOPSY — {doc['scope_title']}")
    a("")
    a(AUTHORITY_LINE)
    a("")
    a("Hierarchy: GAME ENVIRONMENT → TEAM VOLUME → PLAYER OPPORTUNITY → EFFICIENCY. Expectations are frozen or "
      "point-in-time only: the board's latest-pregame ladders, the simulation's script summary from Week 4, the "
      "team's prior-game mean, the incumbent's frozen projected opportunity. Weeks 1–3 have no frozen team-volume "
      "projection; their team-volume expectation is a QB pass-attempts ladder or the prior mean, and says so.")
    a("")
    a("## 1. Game-centre errors (market at latest pregame vs final)")
    a("")
    mae = s["market_mae"]
    a(f"{s['n_games_ok']} games. Market MAE — margin {_n(mae['margin'], 2)}, total {_n(mae['total'], 2)}, "
      f"home points {_n(mae['home_points'], 2)}, away points {_n(mae['away_points'], 2)}.")
    a("")
    a("## 2. What kind of games were played")
    a("")
    a("| label | games |")
    a("|---|---|")
    for k, v in s["label_counts"].items():
        a(f"| {k} | {v} |")
    a("")
    a("_Labels read the play-by-play score progression and the PREGAME market favourite / total only; no label reads a wager._")
    a("")
    a("| game | primary script | labels | final | market margin / total | margin err | total err | plays H/A | pass att H/A |")
    a("|---|---|---|---|---|---|---|---|---|")
    for g in doc["games"]:
        if g.get("status") != "OK":
            a(f"| {g['game_id']} | {g.get('status')} | | | | | | | |")
            continue
        f, mk, e, v = g["flow"], g["market"], g["errors"], g["volume"]
        a(f"| {g['game_id']} | {g['primary_label']} | {', '.join(g['labels'])} | {int(f['final_home'])}-{int(f['final_away'])} | "
          f"{_n(mk.get('home_margin'), 1)} / {_n(mk.get('total'), 1)} | {_n(e.get('margin'), 1)} | {_n(e.get('total'), 1)} | "
          f"{(v.get(g['home']) or {}).get('plays', '—')}/{(v.get(g['away']) or {}).get('plays', '—')} | "
          f"{(v.get(g['home']) or {}).get('pass_att', '—')}/{(v.get(g['away']) or {}).get('pass_att', '—')} |")
    a("")
    a("## 3. Team-volume errors (beyond ±25%)")
    a("")
    for k, v in s["team_volume_off_by_direction"].items():
        a(f"- {k}: {v}")
    a("")
    a("## 4. Player projection misses, by the layer that left expectation first")
    a("")
    aut = doc["autopsy_totals"]
    a(f"{aut['n']:,} canonical player-stat units (one per game × player × statistic, autopsy rule {aut['rule']}). "
      f"Classification: " + ", ".join(f"{k} {v}" for k, v in aut["classifications"].items()) + ".")
    a("")
    a(f"Of {aut['meaningful']:,} meaningful misses (excluding NO_LARGE_MISS and INSUFFICIENT_DATA): OPPORTUNITY + "
      f"TEAM_VOLUME {_pct(aut['share_opp_tv'])}, EFFICIENCY {_pct(aut['share_eff'])}.")
    a("")
    a("| miss layer | units | share of meaningful misses |")
    a("|---|---|---|")
    mm = max(1, s["n_meaningful_misses"])
    for k, v in s["miss_layers"].items():
        a(f"| {k} | {v:,} | {_pct(v / mm) if k not in ('NO_LARGE_MISS', 'INSUFFICIENT_DATA') else '—'} |")
    a("")
    a(f"**Would better game scripting plausibly have prevented the miss?** For {_pct(s['share_script_could_have_helped'])} "
      f"of meaningful misses: the team's volume missed in the miss's direction AND the realized script (a big lead or "
      f"deficit, or a low-possession game) explains it by the volume model's own mechanism. The largest layer is a "
      f"player's SHARE with team volume on expectation — who got the ball, not how many plays there were.")
    a("")
    nt = s.get("n_meaningful_excluding_touchdowns") or 0
    if nt:
        lt = s.get("miss_layers_excluding_touchdowns") or {}
        a(f"**Sensitivity — excluding anytime-touchdown props** ({nt:,} meaningful misses; a TD prop's opportunity is total "
          f"touches, so almost all of its variation reads as share): " +
          ", ".join(f"{k} {100 * v / nt:.0f}%" for k, v in lt.items()) + ".")
        a("")
    a("| primary script | " + " | ".join(k for k in ("PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION", "EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION",
                                                     "TEAM_VOLUME_NOT_EXPLAINED_BY_SCRIPT", "GAME_SCRIPT_DROVE_TEAM_VOLUME",
                                                     "ROLE_UNCERTAINTY", "AVAILABILITY", "VARIANCE_ONLY")) + " |")
    a("|---" * 8 + "|")
    for lab, d in sorted(s["meaningful_layers_by_primary_label"].items(), key=lambda kv: -sum(kv[1].values())):
        a(f"| {lab} | " + " | ".join(str(d.get(k, 0)) for k in ("PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION",
                                                                 "EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION",
                                                                 "TEAM_VOLUME_NOT_EXPLAINED_BY_SCRIPT", "GAME_SCRIPT_DROVE_TEAM_VOLUME",
                                                                 "ROLE_UNCERTAINTY", "AVAILABILITY", "VARIANCE_ONLY")) + " |")
    a("")
    a("## 5. Recurring failure modes")
    a("")
    for line in doc.get("recurring") or []:
        a(f"- {line}")
    a("")
    a("## 6. Autopsy coverage")
    a("")
    for w, cv in sorted((doc.get("autopsy_coverage") or {}).items()):
        a(f"- week {w}: expected {cv['expected_games']} games, diagnosed {cv['diagnosed_games']}, excluded {cv['excluded_games']} "
          f"({'; '.join(sorted({g['game_id'] + ': ' + g['exclusion_reason'] for g in cv['games'] if not g['included']})) or 'none'}).")
    a("")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------------------------ thesis improvement
def render_thesis(doc: dict) -> str:
    L = []
    a = L.append
    a(f"# THESIS IMPROVEMENT — {doc['scope_title']}")
    a("")
    a(AUTHORITY_LINE)
    a("")
    a("## 1. Pay attention to, before the games")
    a("")
    for line in doc["attention"]:
        a(f"- {line}")
    a("")
    a("## 2. What should NOT change")
    a("")
    for line in doc["do_not_change"]:
        a(f"- {line}")
    a("")
    a("## 3. Hypotheses under test (preregistered; context only)")
    a("")
    for h in doc["hypotheses"]:
        pr = (h.get("prospective") or {}).get("suggestion") or {}
        a(f"- **{h['id']}** {h['title']} — {h['status']}; tag `{h.get('tag') or '—'}`; prospective: "
          f"{pr.get('suggested_status', 'no future week yet')}")
    a("")
    a("## 4. Research tags for the coming week")
    a("")
    a("RUN NFL marks markets that fall under a hypothesis above with its tag (PRICE_BUCKET_RESEARCH_CANDIDATE, "
      "DISAGREEMENT_RESEARCH_CANDIDATE, MOVEMENT_RESEARCH_CANDIDATE …). A tag means \"this is the kind of contract a "
      "test is watching\". It is not evidence and changes no state, edge, threshold or stake.")
    a("")
    ex = doc.get("expression")
    a("## 5. Expression autopsy of the actual positions")
    a("")
    if not ex:
        a("No actual-wager episodes in scope.")
    else:
        a(f"{ex['n_positions']} position episodes (orders folded into positions; a cashout is the same position closing) "
          f"expressing **{ex['n_independent_theses']} inferred theses**.")
        a("")
        a("| classification | positions | P&L |")
        a("|---|---|---|")
        for k, v in ex["classifications"].items():
            a(f"| {k} | {v} | {_n(ex['pnl_by_classification'].get(k), 2)} |")
        a("")
        a("Flags: " + (", ".join(f"{k} {v}" for k, v in ex["flags"].items()) or "none") + ".")
        a("")
        a("| thesis bucket | positions | script | stake | P&L | types |")
        a("|---|---|---|---|---|---|")
        for b in ex["buckets"]:
            if b["positions"] >= 2 or b["script"] != "SCRIPT_UNJUDGEABLE":
                a(f"| `{b['bucket']}` | {b['positions']}{' ⚠ stack' if b['correlated_stack'] else ''} | {b['script']} | "
                  f"{_n(b['stake'], 2)} | {_n(b['pnl'], 2)} | {', '.join(b['thesis_types'])} |")
        a("")
        a(f"_{ex['caution']}._")
    a("")
    a("## 6. Limitations")
    a("")
    for line in doc["limitations"]:
        a(f"- {line}")
    a("")
    return "\n".join(L) + "\n"
