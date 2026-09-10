"""Render the three-arm scorecard, the player autopsy and the funnel as Markdown. Derived, regenerable, no authority."""
from __future__ import annotations

from nfl_edge.arms import registry as R
from nfl_edge.arms.scorecard import ARMS, INSUFFICIENT

SHORT = {R.CURRENT: "CURRENT", R.DATA_ONLY: "DATA_ONLY", R.HYBRID: "HYBRID_30"}


def _f(v, nd=3):
    if v is None:
        return "-"
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    return str(v)


def _ci(ci, nd=3):
    return "-" if not ci else f"[{ci[0]:.{nd}f}, {ci[1]:.{nd}f}]"


def _banner(sc) -> list:
    n = sc.get("headline_n_games", 0)
    ev = sc.get("headline_evidence")
    L = []
    if ev == INSUFFICIENT:
        L += [f"> **INSUFFICIENT EVIDENCE.** {n} distinct game(s) with a scored latest-pregame three-arm record; the "
              f"preregistered floor for any verdict is {R.MIN_GAMES_FOR_VERDICT} games. Every number below is a "
              "description of a small, correlated sample. There is no winning model here and this report will never "
              "print one after one slate.", ""]
    else:
        L += [f"> **Evidence accumulating** ({n} distinct games). Intervals are game-clustered; nothing here promotes, "
              "demotes, retunes or reweights anything. Promotion is a separate owner-approved project.", ""]
    return L


def render_game_rows(rows) -> list:
    """The prominent per-game table: CURRENT vs DATA_ONLY vs HYBRID centres, actual, snapshot market and close."""
    L = ["| game | kickoff | T-min | arm | margin | total | actual margin | actual total | mkt@snap margin/total | close margin/total |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (str(r.get("kickoff_at")), str(r.get("game_id")))):
        act, mk, cl = r.get("actual") or {}, r.get("market_at_snapshot") or {}, r.get("close") or {}
        for i, arm in enumerate(ARMS):
            a = (r.get("arms") or {}).get(arm) or {}
            L.append(f"| {r.get('game_id') if i == 0 else ''} | {str(r.get('kickoff_at'))[:16] if i == 0 else ''} | "
                     f"{_f(r.get('minutes_to_kickoff'), 0) if i == 0 else ''} | {SHORT[arm]} | "
                     f"{_f(a.get('projected_home_margin'), 2) if a.get('status') != R.UNAVAILABLE else a.get('status')} | "
                     f"{_f(a.get('projected_total'), 2) if a.get('status') != R.UNAVAILABLE else '-'} | "
                     f"{_f(act.get('margin'), 0) if i == 0 else ''} | {_f(act.get('total'), 0) if i == 0 else ''} | "
                     f"{(_f(mk.get('margin'), 1) + '/' + _f(mk.get('total'), 1) + ' (' + str(mk.get('source')) + ')') if i == 0 else ''} | "
                     f"{(_f(cl.get('margin'), 1) + '/' + _f(cl.get('total'), 1) + ' (' + str(cl.get('status')) + ')') if i == 0 else ''} |")
    return L


def _center_table(blk) -> list:
    L = ["| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for arm in ARMS:
        m = blk["arms"].get(arm) or {}
        if not m.get("n_games"):
            L.append(f"| {SHORT[arm]} | 0 | - | - | - | - | - | - | - | - |  (excluded/unavailable: {m.get('excluded', m.get('excluded_not_usable', 0))})")
            continue
        L.append(f"| {SHORT[arm]} | {m['n_games']} | {m.get('n_weeks')} | {_f(m['margin']['mae'], 2)} | {_f(m['margin']['rmse'], 2)} | "
                 f"{_f(m['margin']['bias'], 2)} | {_f(m['total']['mae'], 2)} | {_f(m['total']['rmse'], 2)} | {_f(m['total']['bias'], 2)} | "
                 f"{_f((m.get('home_win') or {}).get('brier'))} |")
    for key, label in (("market_at_snapshot", "market at snapshot"), ("market_at_close", "market at close")):
        m = blk.get(key) or {}
        if m.get("n_games"):
            L.append(f"| {label} | {m['n_games']} | {m.get('n_weeks')} | {_f(m['margin']['mae'], 2)} | {_f(m['margin']['rmse'], 2)} | "
                     f"{_f(m['margin']['bias'], 2)} | {_f(m['total']['mae'], 2)} | {_f(m['total']['rmse'], 2)} | {_f(m['total']['bias'], 2)} | - |")
    return L


def _paired_table(pairs) -> list:
    L = ["| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |",
         "|---|---|---|---|---|---|---|---|"]
    for p in pairs:
        for q in ("margin", "total"):
            d = p.get(q) or {}
            L.append(f"| {SHORT.get(p['arm'], p['arm'])} vs {SHORT.get(p['versus'], p['versus'])} | {p.get('n_games', 0)} | {q} | "
                     f"{_f(d.get('mean_diff_abs_error'))} | {_f(d.get('se'))} | {_ci(d.get('ci95'))} | "
                     f"{_f(d.get('share_a_closer') if 'share_a_closer' in d else d.get('share_arm_closer'))} | {p.get('evidence')} |")
    return L


def render_scorecard(sc: dict, *, title: str, game_rows: list | None = None) -> str:
    L = [f"# {title}", "", *_banner(sc)]
    su = sc["sample_units"]
    L += ["## Sample units (games)", "", "| unit | rows | games | weeks | note |", "|---|---|---|---|---|"]
    for k, v in su.items():
        L.append(f"| {k} | {v.get('n_rows')} | {v.get('n_games')} | {v.get('n_weeks')} | {v.get('note') or v.get('selection_rule') or ''} |")
    L += ["", "Raw rows are repeated snapshots of the same games and are never a sample size. The primary unit is "
          "`latest_pregame` (one row per game); the canonical horizons are one row per game per horizon.", ""]
    if game_rows:
        L += ["## Game centres, per game (latest pregame snapshot)", "", *render_game_rows(game_rows), ""]
    for unit in ["latest_pregame"] + [R.HORIZON_LABELS[h] for h in R.PRIMARY_HORIZONS_MIN]:
        blk = sc["games"].get(unit)
        if not blk:
            continue
        L += [f"## Game-centre accuracy — {unit} ({blk['n_games']} games, {blk['n_weeks']} weeks; {blk['evidence']})", "",
              *_center_table(blk), "", "### Paired differences (negative favours the first arm)", "",
              *_paired_table(blk["paired"]), "", "### Against the market centre, same games", "",
              *_paired_table(blk["paired_vs_market_at_snapshot"] + blk["paired_vs_close"]), ""]
        L += ["### Information addition: did the deviation from the snapshot market point toward the close?", "",
              "| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for arm, mv in blk["movement"].items():
            for q in ("margin", "total"):
                m = mv[q]; c = m["counts"]
                L.append(f"| {SHORT[arm]} | {q} | {mv.get('n_games')} | {c.get('toward', 0)} | {c.get('away', 0)} | {c.get('unchanged', 0)} | "
                         f"{c.get('no_close', 0)} | {_f(m.get('toward_share'))} | {_f(m.get('closer_than_market_share'))} | {_f(m.get('mean_abs_deviation_from_market'), 2)} |")
        L += ["", "### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)", "",
              "| arm | quantity | band | games | arm MAE | market MAE | toward share |", "|---|---|---|---|---|---|---|"]
        for arm, bt in blk["disagreement_bands"].items():
            for q in ("margin", "total"):
                for band, b in bt[q].items():
                    L.append(f"| {SHORT[arm]} | {q} | {band} | {b.get('n_games', 0)} | {_f(b.get(f'{q}_mae_arm'), 2)} | {_f(b.get(f'{q}_mae_market'), 2)} | {_f(b.get('toward_share'))} |")
        L += ["", f"Centre source at snapshot: {blk['by_center_source']}; DATA_ONLY quality states: "
              f"{blk['by_data_quality_state'].get(R.DATA_ONLY)}; close centre status: {blk['close_center_status']}.", ""]
    for unit in ["latest_pregame"] + [R.HORIZON_LABELS[h] for h in R.PRIMARY_HORIZONS_MIN]:
        blk = sc["contracts"].get(unit)
        if not blk or not blk.get("n_rows"):
            continue
        L += [f"## Contract pricing — {unit} ({blk['n_unique_contracts']} contracts, {blk['n_games']} games; {blk['evidence']})", "",
              "Event space (binary settlements only) and contract space (exact payouts) are separate tables.", "",
              "| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for arm in ARMS:
            m = blk["arms"][arm]; e, p = m["event"], m["payout"]
            L.append(f"| {SHORT[arm]} | {e.get('n_rows', 0)} | {_f(e.get('brier'), 4)} | {_f(e.get('log_loss'), 4)} | {_f(e.get('mean_predicted'))} | "
                     f"{_f(e.get('actual_rate'))} | {p.get('n_rows', 0)} | {_f(p.get('mse'), 4)} | {_f(p.get('market_at_snapshot_mse'), 4)} | {_f(p.get('market_at_close_mse'), 4)} |")
        L += ["", "### Paired contract differences (game-clustered bootstrap; negative favours the first arm)", "",
              "| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |", "|---|---|---|---|---|---|---|---|"]
        for p in blk["paired"]:
            e, py = p["event"], p["payout"]
            L.append(f"| {SHORT[p['arm']]} vs {SHORT[p['versus']]} | {e['n_contracts']} | {e['n_games']} | {_f(e['brier_diff'].get('mean'), 5)} | "
                     f"{_ci(e['brier_diff'].get('ci95'), 5)} | {_f(py['mse_diff'].get('mean'), 5)} | {_ci(py['mse_diff'].get('ci95'), 5)} | {p['evidence']} |")
        for p in blk["paired_vs_market"]:
            m = p["mse_diff"]
            L.append(f"| {SHORT[p['arm']]} vs {p['versus']} | {p['n_contracts']} | {p['n_games']} | - | - | {_f(m.get('mean'), 5)} | {_ci(m.get('ci95'), 5)} | {p['evidence']} |")
        L += ["", f"Families: {blk['by_family']}; settlement: {blk['by_settlement_status']}; close: {blk['by_close_status']}.", ""]
        cal = blk["calibration"].get(R.CURRENT) or []
        if cal:
            L += ["### Calibration by predicted-probability decile (event space)", "", "| band | " + " | ".join(f"{SHORT[a]} n / predicted / actual" for a in ARMS) + " |", "|---|" + "---|" * len(ARMS)]
            bands = sorted({c["band"] for a in ARMS for c in blk["calibration"].get(a) or []})
            for band in bands:
                cells = []
                for a in ARMS:
                    c = next((x for x in blk["calibration"].get(a) or [] if x["band"] == band), None)
                    cells.append("-" if not c else f"{c['n']} / {_f(c['mean_predicted'])} / {_f(c['actual_rate'])}")
                L.append(f"| {band} | " + " | ".join(cells) + " |")
            L.append("")
    L += ["## Reading this report", "",
          f"Preregistration {sc.get('preregistration_sha')} ({R.HYPOTHESIS_ID}): arms {', '.join(SHORT[a] for a in ARMS)}; hybrid "
          f"{R.HYBRID_WEIGHT_MARKET:.2f} market / {R.HYBRID_WEIGHT_DATA:.2f} data; horizons "
          f"{', '.join(R.HORIZON_LABELS[h] for h in R.PRIMARY_HORIZONS_MIN)}; verdict floor {R.MIN_GAMES_FOR_VERDICT} games.",
          "The sample size is games (and contracts within games), never snapshots. The historical closing line beat this "
          "football model in every season on record; the open question is the earlier horizons, and only the accumulated "
          "prospective record answers it. No challenger has betting authority.", ""]
    return "\n".join(L)


def render_funnel(funnels: list) -> str:
    """funnels: list of funnel dicts (one per snapshot). Aggregated counts plus the newest snapshot's detail."""
    if not funnels:
        return "## Decision funnel\n\nNo funnel accounting is available for this period.\n"
    L = ["## Decision funnel (BET / WATCH / PASS accounting of the existing gates; no authority)", "",
         f"{len(funnels)} snapshot(s). A contract's terminal state is where it left the existing gate sequence when the "
         "model's own contract value stands in for a handicap. BET here means every mechanical gate the preflight "
         "applies would pass; it is still not a recommendation (that needs a human handicap and the signed preflight).", ""]
    latest = funnels[-1]
    L += [f"### Newest snapshot {latest.get('run_id')} ({latest.get('n_markets')} markets)", "", "| stage | markets |", "|---|---|"]
    for s in latest.get("stages") or []:
        L.append(f"| {s['stage']} | {s['n']} |")
    L += ["", f"Terminal states: {latest.get('terminal_states')}", "", "| family | BET | WATCH | PASS |", "|---|---|---|---|"]
    for fam, d in (latest.get("by_family") or {}).items():
        L.append(f"| {fam} | {d.get('BET', 0)} | {d.get('WATCH', 0)} | {d.get('PASS', 0)} |")
    L += ["", "| rejection reason | n |", "|---|---|"]
    for r in (latest.get("top_rejection_reasons") or [])[:15]:
        L.append(f"| {r['reason']} | {r['n']} |")
    L += ["", "WATCH rows carry the highest executable price at which one contract still has net EV > 0 under the committed fee "
          f"schedule (`watch_ceiling`). Not replayed: {latest.get('not_replayed')}.", ""]
    if len(funnels) > 1:
        agg = {}
        for f in funnels:
            for k, v in (f.get("terminal_states") or {}).items():
                agg[k] = agg.get(k, 0) + v
        L += [f"Across all {len(funnels)} snapshots (repeated markets counted per snapshot): {agg}.", ""]
    return "\n".join(L)


def render_autopsy(rows: list, *, limit: int = 40) -> str:
    L = ["## Player projection autopsy (largest standardised misses; diagnosis, never a model change)", ""]
    if not rows:
        return "\n".join(L + ["No settled, instrumented player projections in this period.", ""])
    L += [f"{len(rows)} player-stat-game projections diagnosed. Ranked by |robust z| of the actual inside the fitted distribution "
          "(cross-statistic), ties by game and player. Classification is deterministic from the recorded intermediates.", "",
          "| game | player | stat | mean | q05–q95 | actual | z | pct | proj opp | act opp | proj eff | act eff | avail | played | model vs market | class |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows[:limit]:
        L.append(f"| {r.get('game_id')} | {r.get('player_name')} | {r.get('stat')} | {_f(r.get('projected_stat_mean'), 1)} | "
                 f"{_f((r.get('model_quantiles') or {}).get('p05'), 0)}–{_f((r.get('model_quantiles') or {}).get('p95'), 0)} | "
                 f"{_f(r.get('actual_stat'), 0)} | {_f(r.get('robust_z'), 2)} | {_f(r.get('percentile'), 2)} | "
                 f"{_f(r.get('projected_opportunity'), 1)} | {_f(r.get('actual_opportunity'), 0)} | {_f(r.get('projected_efficiency'), 2)} | "
                 f"{_f(r.get('actual_efficiency'), 2)} | {r.get('availability_state')} | {r.get('played')} | "
                 f"{_f(r.get('model_vs_market_payout_error_diff'), 3)} | {r.get('classification')} |")
    from collections import Counter
    c = Counter(r.get("classification") for r in rows)
    L += ["", f"Classification counts over every diagnosed projection: {dict(c)}.",
          f"Missing usage (no snap table or stats row): {sum(1 for r in rows if r.get('usage_missing'))}.", ""]
    return "\n".join(L)
