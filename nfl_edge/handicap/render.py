"""Render a handicap packet as Markdown for a reader who has to reason, not parse.

The JSON artifact keeps everything. This view keeps what a handicapper needs to form an opinion and points
at the JSON for the rest. Two editorial rules:

  * every model-vs-market number is labelled disagreement and shown next to the price you would actually pay;
  * anything missing is stated as missing. A blank is never left to look like a zero.
"""
from __future__ import annotations


def _pct(x, nd=1):
    return "--" if x is None else f"{100 * x:.{nd}f}"


def _num(x, nd=2):
    return "--" if x is None else f"{x:.{nd}f}"


def _sign(x, nd=3):
    return "--" if x is None else f"{x:+.{nd}f}"


def render_markdown(packet: dict, max_players_per_game: int = 8,
                    max_markets_per_game: int = 30, compact: bool = False) -> str:
    """The slate document. `compact=True` trims each game to what decides whether to open it in full.

    A full 16-game slate renders to ~370KB, which is not a document anyone -- human or model -- reads well.
    The workflow is: read the slate, pick from GAME PRIORITY, then open that game's own file.
    """
    L = []
    a = L.append
    s = packet["slate_summary"]
    a(f"# NFL HANDICAP PACKET — {packet['season']} Week {packet['week']}")
    a("")
    a(f"- run id: `{packet['handicap_run_id']}`  ·  packet sha: `{packet['packet_sha']}`")
    a(f"- built at: {packet['built_at']}  (all timestamps UTC)")
    a(f"- ledger: `{packet['sources']['ledger']}`  ·  model: `{packet['sources']['model_version']}`")
    a(f"- context captures: {packet['sources']['context_captures']}")
    a(f"- team-profile basis: **{packet['sources']['team_profile_basis']}**")
    a(f"- **REAL-MONEY STATUS: {packet['real_money_status']}**")
    a("")
    a("> This packet contains no recommendations. Every model-vs-market number is a *disagreement*, which is "
      "not an edge. The model has been shown redundant to the closing market on player props and behind it "
      "on game outcomes; it is here as structure and context, not as a superior forecast.")
    a("")

    # ---------------- slate summary ----------------
    a("## SLATE SUMMARY")
    a("")
    a(f"- games: **{s['games']}**")
    a(f"- markets listed this slate: **{s['markets_listed_slate']}**, model-supported: "
      f"**{s['markets_supported_slate']}**")
    a(f"- ledger support states (all weeks): `{s['ledger_support_states']}`")
    a("")
    L.extend(_slate_coverage_section(s))
    if s["major_skill_injuries_out"]:
        a(f"**Skill players ruled OUT ({len(s['major_skill_injuries_out'])})**")
        a("")
        for r in s["major_skill_injuries_out"][:15]:
            a(f"- {r['player']} ({r['position']}, {r['team']}) — {r['state']} · {r['game_id']}")
        a("")
    if s["new_or_changed_injuries"]:
        a(f"**New or changed since the previous capture ({len(s['new_or_changed_injuries'])})** — the most "
          "decision-relevant section on the page")
        a("")
        for r in s["new_or_changed_injuries"][:15]:
            prev = f" (was {r['previous_state']})" if r.get("previous_state") else " (new record)"
            a(f"- {r['player']} ({r['position']}, {r['team']}): **{r['state']}**{prev} · {r['game_id']}")
        a("")
    else:
        a("**New or changed injuries since the previous capture:** none.")
        a("")
    if s["weather_concerns"]:
        a("**Weather flagged material**")
        a("")
        for w in s["weather_concerns"]:
            a(f"- {w['game_id']}: wind {w['wind']}, precip {w['precip']}%")
        a("")
    if s["largest_market_moves"]:
        a("**Largest market moves since first capture**")
        a("")
        a("| ticker | game | family | move |")
        a("|---|---|---|---|")
        for m in s["largest_market_moves"][:10]:
            a(f"| `{m['ticker']}` | {m['game_id']} | {m['family']} | {_sign(m['move'])} |")
        a("")
    if s["largest_model_market_disagreements"]:
        a("**Largest model/market disagreements** — DISAGREEMENT ONLY, REQUIRES HANDICAP")
        a("")
        a("| market | who | line | mkt mid | YES ask | model | disagree |")
        a("|---|---|---|---|---|---|---|")
        for d in s["largest_model_market_disagreements"][:12]:
            a(f"| `{d['ticker']}` | {d.get('player_name') or d.get('family')} | {d.get('threshold')} | "
              f"{_num(d.get('mid'))} | {_num(d.get('yes_ask'))} | {_num(d.get('model_probability'))} | "
              f"{_sign(d.get('disagreement_vs_mid'))} |")
        a("")
    if s["highest_liquidity_markets"]:
        a("**Highest-liquidity markets**")
        a("")
        for m in s["highest_liquidity_markets"][:8]:
            a(f"- `{m['ticker']}` ({m['family']}, {m['game_id']}): volume {m['volume']:.0f}, "
              f"OI {m.get('open_interest') or 0:.0f}")
        a("")
    if s["blocking_data_issues"]:
        a("**BLOCKING data issues**")
        a("")
        for i in s["blocking_data_issues"]:
            a(f"- {i['game_id']}: `{i['code']}` — {i['detail']}")
        a("")

    a("### GAME PRIORITY FOR HANDICAP")
    a("")
    a(f"_{s['disclaimer']}_")
    a("")
    a("| # | game | score | why |")
    a("|---|---|---|---|")
    for g in s["game_priority_for_handicap"]:
        a(f"| {g['rank']} | {g['game_id']} | {g['priority_score']} | {'; '.join(g['reasons'])} |")
    a("")

    # ---------------- games ----------------
    if compact:
        a("> Each game below is summarised. Full detail -- complete market board, every player ladder, all "
          "best-expression groups -- is in that game's own file under `games/`.")
        a("")
    for g in packet["games"]:
        L.extend(_render_game(g, max_players_per_game, max_markets_per_game, compact=compact))
    a("")
    a("---")
    a("")
    a("## HOW TO USE THIS PACKET")
    a("")
    a("1. Handicap each game independently. The model's ranked disagreements are an input, not a shortlist.")
    a("2. For any thesis you form, check **BEST EXPRESSIONS** before choosing a contract — the largest "
      "disagreement is rarely the best payout for the risk.")
    a("3. Check **CORRELATION GROUPS** before sizing more than one position in a game.")
    a("4. Record every serious decision, including passes, via the recommendation ledger "
      "(`scripts/handicap/validate_recommendations.py`, then commit to the `handicap-data` branch).")
    return "\n".join(L)


def _slate_coverage_section(s: dict) -> list:
    """**FULL-BOARD COVERAGE**, slate level: the one table that answers "did we scan everything?".

    It is deliberately the first thing under the slate summary. `markets_supported_slate` counts only the
    incumbent pricer, and reading it as coverage was how ~3,100 contracts with a legitimate Shadow v2
    research projection came to be reported as nothing but `UNSUPPORTED_MODEL`.
    """
    cov = s.get("coverage_matrix") or {}
    if not cov or not cov.get("totals"):
        return []
    L = []
    a = L.append
    t = cov["totals"]
    a("### FULL-BOARD COVERAGE")
    a("")
    a(f"_{s.get('coverage_contract', '')}_")
    a("")
    a("| bucket | contracts | meaning |")
    a("|---|---|---|")
    for b in ("A", "B", "C", "D", "-", "!"):
        rec = (cov.get("buckets") or {}).get(b) or {}
        a(f"| **{b}** | {rec.get('n', 0)} | {rec.get('meaning', '')} |")
    a("")
    a(f"- listed: **{t.get('listed', 0)}** · executable books: **{t.get('executable', 0)}**")
    a(f"- incumbent priced: **{t.get('incumbent_priced', 0)}** · coherent simulation: "
      f"**{t.get('coherent_sim', 0)}** · Shadow v2 research: **{t.get('shadow_v2', 0)}**")
    a(f"- manual handicap required: **{t.get('manual_research', 0)}** · research required: "
      f"**{t.get('research_required', 0)}**")
    a(f"- rules blocked: **{t.get('rules_blocked', 0)}** · identity blocked: "
      f"**{t.get('identity_blocked', 0)}** · non-football: **{t.get('non_football', 0)}**")
    a(f"- post-kickoff (stale): **{t.get('post_kickoff', 0)}**")
    a(f"- **silently omitted: {t.get('silently_omitted', 0)}** — this must be 0.")
    a("")
    if t.get("silently_omitted"):
        a("> **REPORTING INVARIANT VIOLATED** — a listed contract reached no accounting state. This "
          "document is not a complete scan of the market universe.")
        a("")
    cols = cov.get("columns") or ()
    a("| family / period | " + " | ".join(c.replace("_", " ") for c in cols) + " |")
    a("|---" * (len(cols) + 1) + "|")
    for key, row in sorted((cov.get("by_family") or {}).items(), key=lambda kv: -kv[1].get("listed", 0)):
        fam, _, per = key.partition("|")
        a(f"| {fam}{'/' + per if per else ''} | " + " | ".join(str(row.get(c, 0)) for c in cols) + " |")
    a("")
    a("_A Shadow v2 or coherent-simulation projection is RESEARCH. It is not validated, it is never mixed "
      "into the incumbent's probability or its disagreement ranking, and it reaches no recommendation, "
      "staking or preflight path._")
    a("")
    return L


def render_game_markdown(g: dict, max_players: int = 14, max_markets: int = 60) -> str:
    """One game, in full. This is the document to hand over when handicapping that game.

    In full means in full: the MARKET BOARD here carries every executable contract discovered for the game.
    `max_markets` is retained for call compatibility and no longer caps that board -- a 762-market game
    whose file showed the 60 most traded was the 2026 week 2 DET @ BUF reporting defect, see
    `_market_board_section`. It is the slate document, not this one, that may truncate.
    """
    head = [f"# {g['away_team']} @ {g['home_team']} — `{g['game_id']}`", "",
            "**DISAGREEMENT ONLY -- REQUIRES HANDICAP.** Every model-vs-market number in this document is a "
            "disagreement between two estimates. It is not an edge, not a selection and not a "
            "recommendation, and relabelling one as an edge is the single error this packet exists to "
            "prevent.", ""]
    return "\n".join(head + _render_game(g, max_players, None, compact=False)[3:])


def _sim_projection_section(sv: dict, *, compact: bool, max_rows: int) -> list:
    """**COHERENT SIMULATION — PLAYER PROJECTIONS**: the current projection system's own distributions.

    Two rules, both learnt the hard way on the 2026 week 2 DET @ BUF report:

    * **The full game file never truncates this table.**  It used to render `pp[:max_players * 3]` -- 42 rows
      at `max_players=14` -- and that game had 57.  Fifteen priced player/stat projections, Jahmyr Gibbs's
      rushing yards among them, were absent from the document with nothing saying so.  A compact slate
      summary may still cap the table, and says so and where the rest is; the game file may not.
    * **The median shown is the simulation's own.**  `football median` is `LatticeDistribution.quantile(0.50)`
      on the pmf that priced the ladder, not a crossing point read off the listed rungs.
    """
    L = []
    a = L.append
    a("### COHERENT SIMULATION — PLAYER PROJECTIONS")
    a("")
    if not sv.get("run_id"):
        a("_No simulation projections at or before this build; the board carries the incumbent only. "
          "This is the absence of a simulation run, not the absence of a projection._")
        a("")
        return L
    pp = sv.get("player_projections") or []
    cov = sv.get("coverage") or {}
    a(f"**This is the current projection system (sim-1.x, run `{sv.get('run_id')}`).** Every number below is "
      "read off the coherent simulation's own distribution for that player and statistic: one simulated "
      "football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. "
      "`football median` is that distribution's own p50.")
    a("")
    if sv.get("distribution_quantiles_available") is False:
        a("> **This simulation artifact predates sim-1.1.0 and does not report distribution quantiles.** The "
          "median and quartile columns read `n/a` for those rows. That is the artifact not carrying the "
          "field -- it is not the simulation lacking a projection, and no median has been inferred for it.")
        a("")
    shown = pp if not (compact and len(pp) > max_rows) else pp[:max_rows]
    if not pp:
        a("_This simulation run priced no player/stat market in this game. The coverage accounting below says "
          "why, market group by market group._")
    else:
        if len(shown) < len(pp):
            a(f"> **TRUNCATED: {len(shown)} of {len(pp)} projection rows shown.** This is the compact slate "
              f"summary. The complete table, with every row, is in this game's own file under `games/`.")
            a("")
        a("| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | "
          "market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |")
        a("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for x in shown:
            q = (lambda v: _num(v, 1)) if x.get("distribution_quantiles_available") else (lambda v: "n/a")
            who = x.get("player_name") or x.get("player_id") or x.get("player_kalshi_id") or "?"
            a(f"| {who} | {x.get('team')} | {x.get('stat')} | {_num(x.get('football_mean'), 1)} | "
              f"{q(x.get('football_p50'))} | {q(x.get('football_p25'))} | {q(x.get('football_p75'))} | "
              f"{q(x.get('football_p05'))} | {q(x.get('football_p95'))} | "
              f"{_num(x.get('market_mean'), 1)} | {q(x.get('market_p50'))} | "
              f"{_num(x.get('final_mean'), 1)} | {q(x.get('final_p50'))} | "
              f"{_num(x.get('reconcile_weight'))} | {_num(x.get('p_active'))} | {x.get('n_rungs')} | "
              f"{x.get('support_state') or '--'} |")
        a("")
        a(f"_{len(shown)} of {sv.get('simulation_projection_rows_total', len(pp))} simulation player/stat "
          "projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under "
          "`simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS "
          "the market's._")
    a("")
    # ---------------- coverage accounting: the count that has to add up
    if cov and compact:
        a(f"_Simulation coverage: {cov.get('simulated_and_exposed')} of "
          f"{cov.get('player_stat_groups_listed')} listed player/stat groups simulated and exposed, "
          f"{len(cov.get('unsupported_or_refused') or [])} refused with a reason, silently missing "
          f"{cov.get('silently_missing')}. The full accounting is in this game's own file under `games/`._")
        a("")
    elif cov:
        a("**SIMULATION COVERAGE — every listed FULL-period player/stat market group**")
        a("")
        buckets = cov.get("buckets") or {}
        a("| bucket | groups |")
        a("|---|---|")
        for k, v in buckets.items():
            a(f"| {k} | {v} |")
        a("")
        a(f"- listed FULL-period player/stat groups: **{cov.get('player_stat_groups_listed')}** "
          f"(denominator: {cov.get('denominator')})")
        a(f"- simulated and exposed above: **{cov.get('simulated_and_exposed')}**")
        a(f"- simulation projection rows total: **{sv.get('simulation_projection_rows_total')}** · "
          f"rendered here: **{len(shown)}**")
        a(f"- **silently missing: {cov.get('silently_missing')}** (must be 0 — a group is either shown with "
          "its distribution summary or refused with a reason)")
        a("")
        ref = cov.get("unsupported_or_refused") or []
        if ref:
            a(f"_{len(ref)} group(s) not exposed above, each with its reason. A refusal is a statement, not a "
              "gap: the market is listed, and the simulation either would not price it or never saw it._")
            a("")
            a("| player | team | stat | state | reason | rungs |")
            a("|---|---|---|---|---|---|")
            for r in ref:
                a(f"| {r.get('player')} | {r.get('team')} | {r.get('stat')} | {r.get('state')} | "
                  f"{r.get('reason') or '--'} | {r.get('n_rungs')} |")
            a("")
        for r in cov.get("silently_missing_detail") or []:
            a(f"> **INVARIANT VIOLATED** — {r.get('player')} {r.get('stat')} was priced by the simulation and "
              "is neither exposed above nor refused with a reason. Treat this report as incomplete.")
            a("")
    return L


def _legacy_incumbent_section(g: dict, *, max_players: int, compact: bool) -> list:
    """**LEGACY INCUMBENT PROJECTIONS — DIAGNOSTIC ONLY.**

    This table used to be called "PLAYER PROJECTIONS vs MARKET" and sat ABOVE the simulation, which made the
    incumbent shadow ledger's ladder-derived median look like the current model's projection.  Its median is
    the point where the incumbent's OWN listed ladder crosses 0.50, so a ladder that never crosses 0.50 has
    no median at all -- and on the 2026 week 2 DET @ BUF report that produced a blank beside Jahmyr Gibbs's
    rushing yards while the coherent simulation had him at a football mean of 95.1.  A blank here has never
    meant the current system lacks a projection, and the heading now says so.
    """
    L = []
    a = L.append
    players = g.get("players") or {}
    ranked = sorted(players.items(),
                    key=lambda kv: -sum(b.get("supported_rungs", 0) for b in kv[1]["stats"].values()))
    if not ranked:
        return L
    a("### LEGACY INCUMBENT PROJECTIONS — DIAGNOSTIC ONLY")
    a("")
    a("> **This is NOT the current coherent simulation.** It is the legacy incumbent model (`shadow-0.4.x`), "
      "kept for historical comparison and diagnostics. It must not override sim-1.x, and it must not be read "
      "as the current projection system — that table is **COHERENT SIMULATION — PLAYER PROJECTIONS** above.")
    a(">")
    a("> The `legacy ladder median` below is derived from where the incumbent's own listed ladder crosses "
      "0.50. A ladder that never crosses 0.50 has no such median and the cell is blank. **A blank here does "
      "not mean sim-1.x lacks a projection for that player and statistic** — check the coherent simulation "
      "table above, which reports its distribution's actual p50.")
    a("")
    a("_`mean_lower_bound` is a LOWER BOUND, not a mean: a ladder is truncated at its top rung._")
    a("")
    for name, blk in ranked[:(4 if compact else max_players)]:
        meta = blk["meta"]
        a(f"**{name}** ({meta.get('team')}) — availability {meta.get('availability_state')}, "
          f"P(plays) {_num(meta.get('p_plays'))}")
        a("")
        a("| stat | rungs | legacy ladder median | market median | legacy E≥ | market E≥ | disagree |")
        a("|---|---|---|---|---|---|---|")
        for stat, b in sorted(blk["stats"].items()):
            mm, km = b.get("model") or {}, b.get("market") or {}
            a(f"| {stat} | {b['n_listed_rungs']} ({b['supported_rungs']} sup) | "
              f"{_num(mm.get('median'),1)} | {_num(km.get('median'),1)} | "
              f"{_num(mm.get('mean_lower_bound'),1)} | {_num(km.get('mean_lower_bound'),1)} | "
              f"{_sign(b.get('median_disagreement'),1)} |")
        a("")
    if compact and len(ranked) > 4:
        a(f"_TRUNCATED: 4 of {len(ranked)} legacy diagnostic players shown; the complete legacy table is in "
          "this game's own file under `games/`._")
        a("")
    return L


def _ladder_sort_key(m: dict) -> tuple:
    """Ladder order: family, period, team, player, stat, threshold, ticker.

    A board sorted by volume scatters the rungs of one ladder through the document, which is precisely the
    comparison a handicapper is making when choosing how to express a thesis. Sorted this way, every rung of
    a total, a team total, a spread or a player ladder reads as one block. A row with no threshold sorts
    after the numbered rungs of its group rather than in the middle of them, and the ticker breaks ties, so
    the ordering is total and the document is byte-stable between renders of the same packet.
    """
    t = m.get("threshold")
    numbered = isinstance(t, (int, float)) and not isinstance(t, bool)
    return ((m.get("family") or ""), (m.get("period") or ""), (m.get("team") or ""),
            (m.get("player_name") or ""), (m.get("stat") or ""),
            (0, float(t)) if numbered else (1, 0.0), (m.get("ticker") or ""))


def _board_row(m: dict) -> str:
    """One market, one board row. Separate from the section so the rendered set can be read back from it.

    The completeness check below identifies what was rendered by parsing the ticker out of these rows,
    which is the only reading that matches what a handicapper sees. A row builder that returned nothing for
    a market would shrink the board silently; instead it shows up as an unexpected omission.

    THREE MODEL COLUMNS, NEVER ONE. `incumbent` is the validated pricer's probability or its refusal;
    `shadow v2` is the Shadow v2 research projection for this exact ticker, from the arm that is an
    independent football view of the question; `state` is the one accounting state the contract terminates
    in. A row that reads `UNSUPPORTED_MODEL` in the incumbent column and carries a number in the Shadow v2
    column is exactly the case this report used to hide: the incumbent does not price it, and the
    repository nevertheless holds a legitimate research projection for it.

    The Shadow v2 number is never merged into `model` and never enters `disagree`, which stays the
    incumbent's own disagreement against the mid.
    """
    if not m.get("ticker"):
        return ""      # no identity, no row: it is reported as unaccountable rather than rendered as None
    who = m.get("player_name") or m.get("team") or ""
    line = f"{who} {m.get('stat') or ''} {m.get('threshold') if m.get('threshold') is not None else ''}".strip()
    sv2 = m.get("shadow_v2") or {}
    v2p = _num(sv2.get("p_yes")) if sv2.get("p_yes") is not None else "--"
    v2s = sv2.get("support_state") or ("no v2 row" if not sv2 else "--")
    state = (m.get("analysis") or {}).get("analysis_state") or "UNACCOUNTED"
    return (f"| `{m['ticker']}` | {m['family']}{'/' + m['period'] if m.get('period') else ''} | {line} | "
            f"{_num(m.get('yes_bid'))}/{_num(m.get('yes_ask'))} | {_num(m.get('no_bid'))}/{_num(m.get('no_ask'))} | "
            f"{_num(m.get('width'))} | {_num(m.get('volume'),0)} | {_num(m.get('open_interest'),0)} | "
            f"{_num(m.get('model_probability'))} | {_sign(m.get('disagreement_vs_mid'))} | {m['support_state']} | "
            f"{v2p} | {v2s} | {state} |")


def _row_identity(row: str):
    """The ticker a rendered board row actually carries, or None if the row does not identify a contract."""
    parts = row.split("`")
    return parts[1] if len(parts) > 2 and parts[1] else None


def _coverage_section(g: dict, *, compact: bool) -> list:
    """**COVERAGE**: what happened to every contract listed for this game.

    RUN NFL's contract is that every executable Kalshi contract for an unstarted game is examined and
    accounted for. `UNSUPPORTED_MODEL` is a statement about one model, never a reason to hide a contract.
    This table is how a reader checks that claim without doing arithmetic: every listed contract appears in
    exactly one accounting state, the states are grouped into the four operator buckets, and
    `silently omitted` must be **0**.
    """
    cov = g.get("coverage") or {}
    if not cov:
        return []
    L, a = [], None
    a = L.append
    a("### COVERAGE — EVERY LISTED CONTRACT, ACCOUNTED FOR")
    a("")
    t = cov.get("totals") or {}
    a(f"_{t.get('listed', 0)} contracts listed · {t.get('executable', 0)} with a real two-sided book · "
      f"**{t.get('silently_omitted', 0)} silently omitted**._")
    a("")
    buckets = cov.get("buckets") or {}
    a("| bucket | contracts | meaning |")
    a("|---|---|---|")
    for b in ("A", "B", "C", "D", "-", "!"):
        rec = buckets.get(b) or {}
        a(f"| **{b}** | {rec.get('n', 0)} | {rec.get('meaning', '')} |")
    a("")
    if (buckets.get("!") or {}).get("n"):
        a("> **REPORTING INVARIANT VIOLATED** — a listed contract reached no accounting state. Treat this "
          "document as an incomplete scan of the market universe.")
        a("")
    a("_A: the incumbent validated pricer answered. B: a research model answered — the coherent game "
      "simulation or Shadow v2 — and a research answer authorises nothing. C: nothing automated answered, "
      "but the question is pinned, the subject is identified and this packet carries the team profiles, "
      "injuries, roles, weather and market ladder a handicapper needs — so handicap it by hand. D: an "
      "explicit PASS, with the reason on the row in `packet.json`._")
    a("")
    if compact:
        return L
    cols = cov.get("columns") or ()
    a("| family / period | " + " | ".join(c.replace("_", " ") for c in cols) + " |")
    a("|---" * (len(cols) + 1) + "|")
    for key, row in sorted((cov.get("by_family") or {}).items(), key=lambda kv: -kv[1].get("listed", 0)):
        fam, _, per = key.partition("|")
        a(f"| {fam}{'/' + per if per else ''} | " + " | ".join(str(row.get(c, 0)) for c in cols) + " |")
    a("")
    return L


def _shadow_v2_section(g: dict, *, compact: bool) -> list:
    """**SHADOW V2 RESEARCH VIEW**: the projections the incumbent has no opinion about.

    Shadow v2 already held a research projection for thousands of contracts this report printed as
    `UNSUPPORTED_MODEL` and nothing else -- on the 2026 week 2 board, every 1H / 2H / 1Q-4Q spread, total,
    team total, period winner and both-teams-score contract. They are joined here by canonical ticker
    identity, never by title.

    Nothing in this section is validated. A `PROJECTABLE_NOT_YET_VALIDATED` state is printed as
    `PROJECTABLE_NOT_YET_VALIDATED`, no number here reaches recommendation, staking or preflight, and the
    market-derived player arms are labelled as such rather than presented as an independent football view.
    """
    sv2 = g.get("shadow_v2") or {}
    if not sv2:
        return []
    L = []
    a = L.append
    a("### SHADOW V2 RESEARCH VIEW (NOT VALIDATED — AUTHORISES NOTHING)")
    a("")
    a(f"_snapshot `{sv2.get('snapshot_id')}` · arms {', '.join(sv2.get('arms_present') or []) or 'none'} · "
      f"{sv2.get('with_v2_row', 0)} of {sv2.get('listed_contracts', 0)} listed contracts carry a v2 row · "
      f"{sv2.get('projected', 0)} carry a research projection · {sv2.get('not_in_snapshot', 0)} not in the "
      f"snapshot._")
    a("")
    if sv2.get("not_in_snapshot"):
        a(f"_{sv2['not_in_snapshot']} listed contract(s) have no Shadow v2 row at all: {sv2.get('not_in_snapshot_reason')}. "
          "They are accounted for in COVERAGE above, never dropped._")
        a("")
    by_engine = sv2.get("by_engine") or {}
    if by_engine:
        a("| v2 engine | projected | refused |")
        a("|---|---|---|")
        for eng in sorted(by_engine):
            rec = by_engine[eng]
            a(f"| {eng} | {rec.get('projected', 0)} | {rec.get('refused', 0)} |")
        a("")
    states = sv2.get("counts_by_support_state") or {}
    if states:
        a("_support states: " + ", ".join(f"`{k}` {v}" for k, v in states.items()) + "._")
        a("")
    a(f"_{sv2.get('authority')}_")
    a("")
    a("_Per-contract Shadow v2 probabilities, engine versions, snapshot, cutoff and evidence class are on "
      "every row of the MARKET BOARD below and in `packet.json` under each market's `shadow_v2` block._")
    a("")
    return L


def _market_board_section(g: dict, *, max_markets=None) -> list:
    """**MARKET BOARD**: in the game file, every executable contract discovered for that game.

    The 2026 week 2 DET @ BUF report listed 762 markets and rendered 60 of them. The board was sorted by
    volume and cut at `max_markets` in the full per-game file as well as in the compact slate, so genuinely
    traded alternate-total rungs, most of both team-total ladders and a long tail of alternate spreads were
    absent from the document with nothing saying so. Liquidity decided what a handicapper was allowed to
    see, which defeats the purpose of the report: the whole point is to inspect the complete available
    universe and pick the best expression of a football thesis.

    Two rules now:

    * **The full game file never truncates this table.** It passes `max_markets=None` and every listed
      market with a real book is rendered. The slate document, which is a triage view and says so, may
      still pass a cap; a capped board states that it is capped and points at the game file for the rest.
    * **Only a `no_real_market` book may be off the table.** That is a 0.00/0.99-style quote carrying no
      volume and no open interest, whose midpoint is a quoting artefact rather than a price. Those stay in
      `packet.json` with their flag, and the accounting line counts them.

    The accounting line reconciles the document against the packet **by ticker identity, not by
    arithmetic**. Four sets are built in separate passes -- every listed ticker, the tickers actually
    parsed back out of the rendered rows, the tickers classified `no_real_market`, and the tickers this
    view explicitly withheld at its cap -- and

        unexpected = listed - rendered - placeholders - cap_withheld

    is what the line reports as silently omitted. **It must be 0**: a market is either on the board, named
    as a placeholder, or named as held back by a declared cap. Anything else names the missing tickers
    under REPORTING INVARIANT VIOLATED rather than letting the document read as complete. Counting lengths
    instead (`listed - rendered - suppressed - capped`) is forced to zero by how those counts are derived
    and would never fire.

    Ticker identity is checked too, in both directions: a ticker listed twice in `packet.json`, or a row
    rendered twice, is reported rather than allowed to pad the rendered count so that a genuine omission
    reconciles. A listed market with no ticker at all cannot be accounted for and says so.

    Liquidity is preserved as information, not as a filter: volume, open interest and width are columns.
    """
    L = []
    a = L.append
    a("### MARKET BOARD")
    a("")
    listed = g["markets"]
    # Identity, not arithmetic. `listed - rendered - placeholders - cap-withheld` counted with lengths is
    # algebraically forced to zero by the way the counts are derived, so it could never have caught the
    # defect it claims to guard. These are sets of ticker ids, built from separate passes, and the rendered
    # set is read back out of the row text the reader will actually see.
    listed_ids, seen, duplicate_ids, unidentified = set(), set(), [], 0
    for m in listed:
        t = m.get("ticker")
        if not t:
            unidentified += 1
            continue
        if t in seen:
            duplicate_ids.append(t)
        seen.add(t)
        listed_ids.add(t)
    placeholder_ids = {m.get("ticker") for m in listed if m.get("no_real_market") and m.get("ticker")}
    board = [m for m in listed if not m.get("no_real_market")]
    capped_view = max_markets is not None and len(board) > max_markets
    if capped_view:
        board.sort(key=lambda m: (-(m.get("volume") or 0), m.get("family") or ""))
        shown, withheld = board[:max_markets], board[max_markets:]
    else:
        board.sort(key=_ladder_sort_key)
        shown, withheld = board, []
    rows = []
    for m in shown:
        row = _board_row(m)
        if row:
            rows.append(row)
    rendered_ids = {t for t in (_row_identity(r) for r in rows) if t}
    cap_withheld_ids = {m.get("ticker") for m in withheld if m.get("ticker")}
    unexpected = sorted(listed_ids - rendered_ids - placeholder_ids - cap_withheld_ids)
    duplicate_rows = len(rows) - len(rendered_ids)
    suppressed, capped = len(placeholder_ids), len(cap_withheld_ids)
    cap_note = f" · {capped} held back by this view's cap" if capped_view else ""
    a(f"_{len(listed)} markets listed · {len(rows)} executable books rendered · {suppressed} "
      f"no-real-market placeholders suppressed{cap_note} · {len(unexpected)} silently omitted._")
    a("")
    if capped_view:
        a(f"_This is a truncated slate view. Showing the {len(rows)} most traded of {len(board)} "
          "executable books, ordered by volume. **The complete executable board for this game, every rung "
          "of every ladder, is in this game's own file under `games/`** -- nothing below is a statement "
          "about what exists._")
    else:
        a("_**This is the complete executable board**: every market listed for this game that has a real "
          "book, with none held back for being thinly traded. Rows are in ladder order -- family, period, "
          "team, player, stat, threshold, ticker -- so the rungs of one ladder read together and can be "
          "compared. Volume, open interest and width are shown as information; they do not decide what "
          "appears._")
    a("")
    if suppressed:
        a(f"_{suppressed} book(s) are held off the table as `no_real_market`: a 0.00/0.99-style quote with "
          "no volume and no open interest, where the midpoint is a quoting artefact and not a price you "
          "could pay. Every one of them is in `packet.json` under this game's `markets`, flagged and with "
          "its reason. They are the only kind of row allowed to be absent from the board above._")
        a("")
    if unexpected:
        ex = ", ".join(f"`{t}`" for t in unexpected[:8])
        more = f" and {len(unexpected) - 8} more" if len(unexpected) > 8 else ""
        a(f"> **REPORTING INVARIANT VIOLATED** — {len(unexpected)} listed market(s) are neither rendered "
          "below, nor classified as a no-real-market placeholder, nor named as held back by this view's "
          f"cap: {ex}{more}. Treat this report as an incomplete view of the market universe and read "
          "`packet.json` for those tickers.")
        a("")
    if duplicate_ids or duplicate_rows:
        ex = ", ".join(f"`{t}`" for t in sorted(set(duplicate_ids))[:8]) or "none in the packet"
        a(f"> **REPORTING INVARIANT VIOLATED** — ticker identity is not unique. A ticker identifies one "
          f"contract exactly once in a game's `markets`: {len(duplicate_ids)} duplicate listing(s) "
          f"({ex}) and {duplicate_rows} duplicate row(s) on the board. Counts in this document cannot be "
          "reconciled against the packet while a ticker appears twice, and a duplicated row must not be "
          "read as coverage of a second contract.")
        a("")
    if unidentified:
        a(f"> **REPORTING INVARIANT VIOLATED** — {unidentified} listed market(s) carry no ticker and cannot "
          "be identified, rendered or accounted for. Treat this report as an incomplete view of the market "
          "universe.")
        a("")
    a("| ticker | family | line | YES bid/ask | NO bid/ask | width | vol | OI | incumbent | disagree | "
      "incumbent state | shadow v2 | v2 state | accounting state |")
    a("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    L.extend(rows)
    a("")
    return L


def _render_game(g: dict, max_players: int, max_markets=None, compact: bool = False) -> list:
    L = []
    a = L.append
    a("")
    a("---")
    a("")
    a(f"## {g['away_team']} @ {g['home_team']} — `{g['game_id']}`")
    a("")
    a(f"- kickoff: {g['kickoff_utc']} ({_num(g['minutes_to_kickoff'], 0)} minutes away) · state "
      f"**{g['game_state']}**")
    a(f"- venue: {g.get('venue') or 'unknown'} · roof {g.get('roof')} · surface {g.get('surface')}")
    c = g["counts"]
    a(f"- markets: {c['markets_listed']} listed across {c['families']} families — {c['supported']} supported, "
      f"{c['unsupported_model']} no model, {c['unsupported_rules']} rules unresolved, "
      f"{c['mapping_unknown']} identity unresolved")
    if g["data_health"]:
        a("")
        a("**Data health**")
        a("")
        for f in g["data_health"]:
            a(f"- `{f['code']}` ({f['severity']}) — {f['detail']}")
    a("")

    mi, mo = g["market_implied"], g["model_view"]
    a("### MARKET-IMPLIED vs MODEL")
    a("")
    a("| | market (research-implied) | model |")
    a("|---|---|---|")
    a(f"| spread (home) | {_num(mi.get('implied_spread'))} | {_num(mo.get('model_spread'))} |")
    a(f"| total | {_num(mi.get('implied_total_median'))} | {_num(mo.get('model_total'))} |")
    hs = (mi.get("implied_score") or {})
    ms = (mo.get("model_score") or {})
    a(f"| score | {g['home_team']} {_num(hs.get(g['home_team']),1)} – {g['away_team']} "
      f"{_num(hs.get(g['away_team']),1)} | {g['home_team']} {_num(ms.get(g['home_team']),1)} – "
      f"{g['away_team']} {_num(ms.get(g['away_team']),1)} |")
    wp, mwp = (mi.get("win_probability") or {}), (mo.get("model_win_probability") or {})
    a(f"| win prob {g['home_team']} | {_pct(wp.get(g['home_team']))}% | {_pct(mwp.get(g['home_team']))}% |")
    a("")
    a(f"_{mi.get('label')}_")
    a("")
    if g.get("market_implied_by_period"):
        a("Period market-implied: " + " · ".join(
            f"**{p}** spread {_num(v.get('implied_spread'))} / total {_num(v.get('implied_total_median'))}"
            for p, v in g["market_implied_by_period"].items()))
        a("")

    # injuries
    recs = g["injuries"]["records"]
    # Order by handicapping relevance, not alphabetically. A punter on IR and a starting running back on IR
    # are not equally interesting, and an unsorted list buries the second under the first.
    _POS_RANK = {"QB": 0, "RB": 1, "WR": 1, "TE": 1, "T": 2, "G": 2, "C": 2, "OT": 2, "OG": 2, "OL": 2}

    def _relevance(r):
        return (_POS_RANK.get((r.get("position") or "").upper(), 3), r.get("player") or "")

    out = sorted([r for r in recs
                  if str(r.get("state", "")).lower() in ("out", "injured reserve", "suspension")], key=_relevance)
    q = sorted([r for r in recs
                if str(r.get("state", "")).lower() in ("questionable", "doubtful")], key=_relevance)
    a("### INJURIES / AVAILABILITY")
    a("")
    a(f"_{g['injuries']['summary'].get('diff_basis')}_")
    a("")
    if out:
        a(f"**Out / IR ({len(out)})**")
        a("")
        shown = 8 if compact else 14
        for r in out[:shown]:
            flag = " · **NEW**" if r.get("new_since_previous_capture") else (
                f" · **CHANGED from {r['previous_state']}**" if r.get("changed_since_previous_capture") else "")
            a(f"- {r['player']} ({r['position']}, {r['team']}) — {r['state']} "
              f"[{r.get('confidence')}]{flag} — {r.get('likely_role_impact')}")
        if len(out) > shown:
            a(f"- _...and {len(out) - shown} more (mostly non-skill positions); full list in the game file_")
        a("")
    if q:
        a(f"**Questionable / Doubtful ({len(q)})** — resolves at the inactive release, T−90m")
        a("")
        for r in q[:(8 if compact else 14)]:
            a(f"- {r['player']} ({r['position']}, {r['team']}) — {r['state']} [{r.get('confidence')}]"
              + (f" · practice: {r['practice']}" if r.get("practice") else ""))
        a("")
    if not out and not q:
        a("No Out/Questionable records captured for either team.")
        a("")

    # weather
    w = g["weather"]
    a("### WEATHER")
    a("")
    if not w.get("available"):
        a(f"Not available — {w.get('reason')}")
    elif w.get("material") is False and w.get("note"):
        a(w["note"])
    else:
        a(f"- {w.get('short_forecast')} · {w.get('temperature_f')}°F · wind {w.get('wind')} "
          f"{w.get('wind_direction') or ''} · precip {w.get('precipitation_probability')}%")
        a(f"- forecast vintage {w.get('forecast_vintage')} · material: **{w.get('material')}**")
        if w.get("changed_since_previous_capture"):
            a(f"- **changed since previous capture** (was {w.get('previous')})")
    a("")

    if compact:
        # The compact slate may cap this table -- and must say that it has, and where the rest is.  It may
        # not be silent about it, and it may not be the only place the rows exist.
        L.extend(_sim_projection_section(g.get("simulation") or {}, compact=True, max_rows=max_players))
        d = g.get("largest_disagreements") or []
        if d:
            a("### TOP DISAGREEMENTS (tradable books only)")
            a("")
            a("| market | who | line | mkt mid | YES ask | model | disagree |")
            a("|---|---|---|---|---|---|---|")
            for x in d[:6]:
                a(f"| `{x['ticker']}` | {x.get('player_name') or x.get('family')} | {x.get('threshold')} | "
                  f"{_num(x.get('mid'))} | {_num(x.get('yes_ask'))} | {_num(x.get('model_probability'))} | "
                  f"{_sign(x.get('disagreement_vs_mid'))} |")
            a("")
        drb = g.get("disagreement_ranking_basis") or {}
        a(f"_Ranked {drb.get('ranked_markets')} tradable markets; {drb.get('excluded_untradable')} excluded "
          f"as untradable._")
        a("")
        a("### KEY QUESTIONS FOR THE HANDICAPPER")
        a("")
        for i, q in enumerate(g["key_questions"], 1):
            a(f"{i}. {q}")
        a("")
        a(f"_Full board, player ladders, best expressions and correlation groups: `games/{g['game_id']}.md`_")
        a("")
        return L

    # quarterbacks
    a("### QUARTERBACKS")
    a("")
    for team, entries in (g.get("quarterbacks") or {}).items():
        if not entries:
            a(f"**{team}** — no depth-chart QB captured")
            continue
        for e in entries:
            prof = e.get("profile") or {}
            ov = (prof.get("overall") or {})
            pr = (prof.get("under_pressure") or {})
            cl = (prof.get("clean_pocket") or {})
            tag = "QB1" if e.get("depth_chart_order") == 1 else f"QB{e.get('depth_chart_order')}"
            a(f"**{team} {tag}: {e['player']}** — status {e.get('status')}"
              + (f", injury {e['injury_status']}" if e.get("injury_status") else "")
              + f" · availability confidence {e.get('availability_confidence')}")
            if not prof:
                a(f"  - no play-by-play profile: {e.get('note')}")
            elif prof.get("insufficient_sample"):
                a(f"  - only {prof.get('dropbacks')} prior dropbacks — rates suppressed as noise")
            else:
                a(f"  - {prof.get('dropbacks')} dropbacks ({prof.get('basis_season')}): "
                  f"EPA/db {_sign(ov.get('epa_per_dropback'))}, SR {_pct(ov.get('success_rate'))}%, "
                  f"CPOE {_num(ov.get('cpoe'))}, aDOT {_num(ov.get('adot'),1)}, "
                  f"sack rate {_pct(ov.get('sack_rate'))}%, INT rate {_pct(ov.get('int_rate'),2)}%")
                a(f"  - pressured EPA/db {_sign(pr.get('epa_per_dropback'))} vs clean "
                  f"{_sign(cl.get('epa_per_dropback'))}")
        a("")

    # OL
    a("### OFFENSIVE LINE")
    a("")
    for team, ol in (g.get("offensive_line") or {}).items():
        if ol["n_listed"]:
            a(f"**{team}** — {ol['n_listed']} linemen on the report: " +
              ", ".join(f"{x['player']} ({x['state']})" for x in ol["injured_or_listed"][:6]))
        else:
            a(f"**{team}** — no offensive linemen on the injury report")
    a("")
    a(f"_{(g.get('offensive_line') or {}).get(g['home_team'], {}).get('note', '')}_")
    a("")

    # team profiles
    a("### TEAM STRENGTH (opponent-adjusted)")
    a("")
    a("| team | off EPA | def EPA | off dropback | def dropback | off rush | def rush | explosive |")
    a("|---|---|---|---|---|---|---|---|")
    for t, p in (g.get("team_profiles") or {}).items():
        adj = (p or {}).get("adjusted") or {}
        a(f"| {t} | {_sign(adj.get('off_epa'))} | {_sign(adj.get('def_epa'))} | "
          f"{_sign(adj.get('off_db_epa'))} | {_sign(adj.get('def_db_epa'))} | "
          f"{_sign(adj.get('off_rush_epa'))} | {_sign(adj.get('def_rush_epa'))} | "
          f"{_sign(adj.get('off_explosive'))} |")
    a("")
    basis = ((g.get("team_profiles") or {}).get(g["home_team"]) or {}).get("basis")
    a(f"_basis: {basis}. Negative defensive numbers are good (points allowed below average)._")
    a("")

    # matchup
    m = g.get("matchup") or {}
    if m.get("available"):
        a("### MATCHUP ADVANTAGES")
        a("")
        a("| matchup | offense | defense | advantage |")
        a("|---|---|---|---|")
        for p in m["pairs"][:8]:
            a(f"| {p['matchup']} | {p['offense']} | {p['defense']} | {_sign(p['advantage_to_offense'])} |")
        a("")
        a(f"_{m['note']}_")
        a("")

    # roles
    roles = (g.get("roles") or {}).get("by_team") or {}
    if roles:
        a("### DEPTH CHART / EXPECTED ROLES")
        a("")
        for t in sorted(roles):
            bits = []
            for pos in ("QB", "RB", "WR", "TE"):
                lst = roles[t].get(pos) or []
                if lst:
                    bits.append(f"**{pos}**: " + ", ".join(
                        f"{x['player']}{'*' if x.get('injury_status') else ''}" for x in lst[:4]))
            a(f"- **{t}** — " + " · ".join(bits))
        a("")
        a(f"_{(g.get('roles') or {}).get('caveat')}  (* = carries an injury designation)_")
        a("")

    # the CURRENT player projection system, first: the coherent simulation's own distributions
    L.extend(_sim_projection_section(g.get("simulation") or {}, compact=compact, max_rows=max_players * 3))

    # the incumbent, second and unmistakably labelled: it is a diagnostic, not the current projection
    L.extend(_legacy_incumbent_section(g, max_players=max_players, compact=compact))

    # WHAT WAS SCANNED, before what it says: the accounting comes first so a reader knows the board below
    # is the whole board and knows what happened to every contract on it.
    L.extend(_coverage_section(g, compact=compact))

    # the Shadow v2 research layer: the projections the incumbent has no opinion about
    L.extend(_shadow_v2_section(g, compact=compact))

    # markets -- with max_markets None (what the game file passes) this is the complete executable board
    L.extend(_market_board_section(g, max_markets=max_markets))
    drb = g.get("disagreement_ranking_basis") or {}
    a(f"_Disagreement ranking used {drb.get('ranked_markets')} markets; "
      f"{drb.get('excluded_untradable')} excluded as untradable (width > {drb.get('max_width_ranked')} or "
      f"an untraded book). {drb.get('note')}_")
    a("")

    # the simulation layer (shadow): football-only, market and reconciled side by side
    sv = g.get("simulation") or {}
    a("### SIMULATION LAYER (shadow, sim-1.x) — MARKET-LEVEL RECONCILIATION")
    a("")
    if sv.get("run_id"):
        c = sv.get("center") or {}
        a(f"_run {sv.get('run_id')} · generated {sv.get('generated_at')} · centre {c.get('source')} "
          f"(home {_num(c.get('spread_home'), 1)}, total {_num(c.get('total'), 1)}) · "
          f"{', '.join(f'{k} {v}' for k, v in sorted((sv.get('counts_by_support_state') or {}).items()))}_")
        a("")
        a(sv.get("note") or "")
        a("")
        rd = sv.get("largest_reconciled_disagreements") or []
        if rd:
            a("| market | line | mkt mid | football | reconciled | w | vs mid | football mean | market mean | final mean |")
            a("|---|---|---|---|---|---|---|---|---|---|")
            for x in rd[:15]:
                a(f"| `{x['ticker']}` | {x.get('stat') or ''} {x.get('threshold') if x.get('threshold') is not None else ''} | "
                  f"{_num(x.get('mid'))} | {_num(x.get('p_football'))} | {_num(x.get('p_reconciled'))} | {_num(x.get('reconcile_weight'))} | "
                  f"{_sign(x.get('disagreement_vs_mid'))} | {_num(x.get('football_mean'),1)} | {_num(x.get('market_mean'),1)} | "
                  f"{_num(x.get('final_mean'),1)} |")
        else:
            a("_No reconciled (validated-weight) disagreement in this game; football-only probabilities are on the board rows._")
        a("")
        a("_The per-player/stat distribution summaries for this simulation are in **COHERENT SIMULATION — "
          "PLAYER PROJECTIONS** above; this section is the market-level reconciliation only._")
    else:
        a("_No simulation projections at or before this build; the board carries the incumbent only._")
    a("")

    # ranked disagreements -- the same numbers as the board, ordered, and labelled for what they are
    dis = g.get("largest_disagreements") or []
    a("### LARGEST MODEL/MARKET DISAGREEMENTS")
    a("")
    a("**DISAGREEMENT ONLY -- REQUIRES HANDICAP.** Ranked by size, not by attractiveness. A large "
      "disagreement most often means the model is missing something the market knows.")
    a("")
    if dis:
        a("| market | who | line | mkt mid | YES ask | NO ask | model | vs mid | vs YES ask | vs NO ask |")
        a("|---|---|---|---|---|---|---|---|---|---|")
        for x in dis[:20]:
            a(f"| `{x['ticker']}` | {x.get('player_name') or x.get('family')} | "
              f"{x.get('stat') or ''} {x.get('threshold') if x.get('threshold') is not None else ''} | "
              f"{_num(x.get('mid'))} | {_num(x.get('yes_ask'))} | {_num(x.get('no_ask'))} | "
              f"{_num(x.get('model_probability'))} | {_sign(x.get('disagreement_vs_mid'))} | "
              f"{_sign(x.get('disagreement_yes_executable'))} | "
              f"{_sign(x.get('disagreement_no_executable'))} |")
    else:
        a("_No tradable market in this game carries a model view; nothing can be ranked._")
    a("")

    # movement -- observed horizons only, never interpolated
    a("### MOVEMENT")
    a("")
    moves = [m for m in g["markets"] if (m.get("movement") or {}).get("n_observations")]
    moves.sort(key=lambda m: -abs((m["movement"].get("total_move_since_first_capture") or 0.0)))
    if not moves:
        a("_No captured quote history covers this game's tickers. Movement is reported only where an "
          "observation exists; nothing here is interpolated._")
    else:
        a(f"_{len(moves)} of {len(g['markets'])} tickers have captured quote history. A horizon with no "
          "capture is shown as unobserved rather than filled in, and 'not yet reached' is distinguished "
          "from 'never captured'._")
        a("")
        hs = [h for h in ("T-24h", "T-6h", "T-3h", "T-90m", "T-1h", "T-30m")]
        a("| ticker | family | first | now | total move | " + " | ".join(hs) + " |")
        a("|---|---|---|---|---|" + "---|" * len(hs))
        for m in moves[:20]:
            mv = m["movement"]
            cells = []
            for h in hs:
                rec = (mv.get("horizons") or {}).get(h) or {}
                cells.append(_sign(rec.get("move_to_current")) if rec.get("observed") else "—")
            a(f"| `{m['ticker']}` | {m['family']}{'/' + m['period'] if m.get('period') else ''} | "
              f"{_num((mv.get('first_observed') or {}).get('mid'))} | "
              f"{_num((mv.get('current') or {}).get('mid'))} | "
              f"{_sign(mv.get('total_move_since_first_capture'))} | " + " | ".join(cells) + " |")
    a("")

    # unsupported markets -- shown, with the reason, never hidden
    unsupported = [m for m in g["markets"] if m.get("support_state") != "SUPPORTED"]
    a("### UNSUPPORTED MARKETS — WHY")
    a("")
    if not unsupported:
        a("_Every listed market in this game carries a model view._")
    else:
        by_reason = {}
        for m in unsupported:
            key = (m.get("support_state"), m.get("support_reason") or "no reason recorded")
            by_reason.setdefault(key, []).append(m)
        a(f"_{len(unsupported)} of {len(g['markets'])} listed markets carry no model view. They are shown, "
          "not hidden: a missing model is not a missing market, and these remain available to a "
          "qualitative handicap._")
        a("")
        a("| state | reason | markets | examples |")
        a("|---|---|---|---|")
        for (state, reason), ms in sorted(by_reason.items(), key=lambda kv: -len(kv[1])):
            ex = ", ".join(f"`{m['ticker']}`" for m in ms[:3])
            a(f"| {state} | {reason} | {len(ms)} | {ex} |")
    a("")

    # best expressions
    if g.get("best_expressions"):
        a("### BEST EXPRESSIONS (same thesis, different payouts)")
        a("")
        for grp in g["best_expressions"][:6]:
            a(f"**{grp['thesis']}** — {grp['n_expressions']} expressions")
            a("")
            a("| ticker | family | line | YES ask | NO ask | model | disagree |")
            a("|---|---|---|---|---|---|---|")
            for e in grp["expressions"][:10]:
                a(f"| `{e['ticker']}` | {e['family']} | {e.get('stat') or ''} "
                  f"{e.get('threshold') if e.get('threshold') is not None else ''} | "
                  f"{_num(e.get('yes_ask'))} | {_num(e.get('no_ask'))} | "
                  f"{_num(e.get('model_probability'))} | {_sign(e.get('disagreement_vs_mid'))} |")
            a("")
        a(f"_{g['best_expressions'][0]['note']}_")
        a("")

    # correlation
    a("### CORRELATION GROUPS")
    a("")
    for cg in g.get("correlation_groups", []):
        a(f"- `{cg['correlation_group']}` ({cg['direction']}, {cg['strength']}): "
          f"{', '.join(cg['members'])} — {cg['note']}")
    a("")

    a("### KEY QUESTIONS FOR THE HANDICAPPER")
    a("")
    for i, q in enumerate(g["key_questions"], 1):
        a(f"{i}. {q}")
    a("")
    return L
