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


def render_game_markdown(g: dict, max_players: int = 14, max_markets: int = 60) -> str:
    """One game, in full. This is the document to hand over when handicapping that game."""
    head = [f"# {g['away_team']} @ {g['home_team']} — `{g['game_id']}`", "",
            "_Full detail. Every model-vs-market number is a disagreement, not an edge._"]
    return "\n".join(head + _render_game(g, max_players, max_markets, compact=False)[3:])


def _render_game(g: dict, max_players: int, max_markets: int, compact: bool = False) -> list:
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

    # players
    players = g.get("players") or {}
    ranked = sorted(players.items(),
                    key=lambda kv: -sum(b.get("supported_rungs", 0) for b in kv[1]["stats"].values()))
    if ranked:
        a("### PLAYER PROJECTIONS vs MARKET")
        a("")
        a("_Model median and market median from the same listed ladder. `mean_lower_bound` is a LOWER BOUND, "
          "not a mean: a ladder is truncated at its top rung._")
        a("")
        for name, blk in ranked[:(4 if compact else max_players)]:
            meta = blk["meta"]
            a(f"**{name}** ({meta.get('team')}) — availability {meta.get('availability_state')}, "
              f"P(plays) {_num(meta.get('p_plays'))}")
            a("")
            a("| stat | rungs | model median | market median | model E≥ | market E≥ | disagree |")
            a("|---|---|---|---|---|---|---|")
            for stat, b in sorted(blk["stats"].items()):
                mm, km = b.get("model") or {}, b.get("market") or {}
                a(f"| {stat} | {b['n_listed_rungs']} ({b['supported_rungs']} sup) | "
                  f"{_num(mm.get('median'),1)} | {_num(km.get('median'),1)} | "
                  f"{_num(mm.get('mean_lower_bound'),1)} | {_num(km.get('mean_lower_bound'),1)} | "
                  f"{_sign(b.get('median_disagreement'),1)} |")
            a("")

    # markets
    a("### MARKET BOARD")
    a("")
    board = [m for m in g["markets"] if not m.get("no_real_market")]
    board.sort(key=lambda m: (-(m.get("volume") or 0), m.get("family") or ""))
    a(f"_{len(g['markets'])} markets listed; {len(g['markets']) - len(board)} suppressed as untraded "
      f"0.00/0.99 books (present in the JSON). Showing the {min(max_markets, len(board))} most traded._")
    a("")
    a("| ticker | family | line | YES bid/ask | NO bid/ask | width | vol | model | disagree | state |")
    a("|---|---|---|---|---|---|---|---|---|---|")
    for m in board[:max_markets]:
        who = m.get("player_name") or m.get("team") or ""
        line = f"{who} {m.get('stat') or ''} {m.get('threshold') if m.get('threshold') is not None else ''}".strip()
        a(f"| `{m['ticker']}` | {m['family']}{'/' + m['period'] if m.get('period') else ''} | {line} | "
          f"{_num(m.get('yes_bid'))}/{_num(m.get('yes_ask'))} | {_num(m.get('no_bid'))}/{_num(m.get('no_ask'))} | "
          f"{_num(m.get('width'))} | {_num(m.get('volume'),0)} | {_num(m.get('model_probability'))} | "
          f"{_sign(m.get('disagreement_vs_mid'))} | {m['support_state']} |")
    a("")
    drb = g.get("disagreement_ranking_basis") or {}
    a(f"_Disagreement ranking used {drb.get('ranked_markets')} markets; "
      f"{drb.get('excluded_untradable')} excluded as untradable (width > {drb.get('max_width_ranked')} or "
      f"an untraded book). {drb.get('note')}_")
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
