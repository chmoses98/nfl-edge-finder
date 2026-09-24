"""OWNER ACTUAL PLACED WAGERS: risk and concentration. GOVERNANCE REPORTING, not model evidence, not sizing.

Reads the per-wager rows `actual_wager_postmortem.build` produces and says where the owner's money sat: which
wagers were really one exposure, how much of the period's stake each exposure carried, and how much of the
period's result it explains. It never changes, recommends or caps a stake -- `risk.py` is the pre-trade policy;
this is the after-the-fact audit of what was actually placed.

WHICH NET FIGURE
----------------
Every P&L figure here goes through ONE accessor, `net_figure`, which prefers `net_canonical` (reserved for the
accounting amendments that will name a canonical net), then `net_fee_reconciled` (gross - stake, where the
exchange's own figures prove the settlement fee was the entry fee counted twice), then `net_profit_loss` (the
router's figure as filed). The period is reported on the most-preferred basis that EVERY wager in scope has
(`primary`); every other available basis is reported beside it, never merged into it.

EXPOSURE GROUPING (deterministic; different tickers do not mean diversified)
--------------------------------------------------------------------------
Kalshi tickers are SERIES-EVENT[-SUBJECT[-RUNG]], e.g. KXNFLSPREAD-26SEP20INDKC-KC5.

* GAME     -- the event code's game (26SEP20INDKC), labelled with the canonical game_id when a close gave one.
* MARKET   -- the identical ticker.
* LADDER   -- the same underlying variable: series + event, plus the subject for subject ladders. Every spread
              rung of one game (KC5, IND3: one margin), every total rung (61, 70: one points total), both sides
              of one game-winner market, one team's team-total rungs (BAL29, BAL32), and one player's rungs of
              one stat (…-BALDHENRY22-80, …-BALDHENRY22-100) are each ONE ladder.
* PLAYER   -- where the subject parses as TEAM + NAME + JERSEY with TEAM one of the event's two teams.
* CLUSTER  -- the correlated exposure: wagers joined (transitively) by any of the rules in `LINK_RULES`.
              Links never cross games. By default EVERY same-game pair is linked (`same_game_linked_families`
              = None): every market on one game settles on the same game state, and a reviewer who wants to
              argue two same-game wagers are independent has to narrow that tuple explicitly.

WHAT IS NEVER DONE HERE
-----------------------
* No bankroll is guessed. A share of starting bankroll is stated only when bankroll evidence is passed in;
  otherwise the state is NOT_AVAILABLE. (The router's bankroll is a secret; the handicap-data
  `bankroll_snapshot` fields belong to synthetic TEST_ONLY recommendations, not to the owner's account.)
* No claim of skill. The decomposition is an accounting identity with caveats, not an attribution model.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass

RISK_VERSION = "wager-risk-1.0.0"

#: The single preference order for "the net figure to use". The first basis a row has wins.
NET_BASES = ("net_canonical", "net_fee_reconciled", "net_profit_loss")

#: Series whose single-segment subject is a TEAM whose rungs form a ladder (BAL29, BAL32 -> BAL).
TEAM_SUBJECT_SERIES = ("KXNFLTEAMTOTAL",)

LINK_RULES = {
    "SAME_MARKET": "identical market ticker (two orders on one contract are one exposure)",
    "OPPOSING_POSITION_PAIR": "YES and NO held on the identical market ticker",
    "SAME_LADDER": "different rungs of one underlying variable (same series + event [+ subject])",
    "SAME_GAME_CORRELATED": "same game, both families in `same_game_linked_families` (default: every family; "
                            "spread, game winner, team total, totals and player props on one game all settle on "
                            "one game state)",
}


@dataclass(frozen=True)
class RiskThresholds:
    """Warning thresholds, as shares of the scope's total stake. Strictly greater-than fires.

    Defaults are the repository's own PILOT risk policy (config/risk_policy.json) read as shares of its slate
    cap of 12 units, so the audit of what was placed uses the same yardstick the pre-trade policy would have:

      concentration_high_share      0.25   a correlation group may carry 3u of a 12u slate
      single_game_dominates_share   1/3    a game may carry 4u of a 12u slate
      correlated_exposure_high_share 1/6   a single position may carry 2u of 12u; a MULTI-leg cluster above
                                           that is correlation doing what one position was not allowed to do
      correlated_min_wagers         2      a "correlated" cluster has at least two legs
      opposing_pair_min_share       0.0    any YES+NO pair on one market is flagged
    """
    concentration_high_share: float = 0.25
    correlated_exposure_high_share: float = 1.0 / 6.0
    correlated_min_wagers: int = 2
    single_game_dominates_share: float = 1.0 / 3.0
    opposing_pair_min_share: float = 0.0
    #: None = every family is linked within a game. A tuple narrows SAME_GAME_CORRELATED to those families.
    same_game_linked_families: tuple | None = None


DEFAULT_THRESHOLDS = RiskThresholds()

DECOMPOSITION_CAVEATS = (
    "Entry quality, outcome variance and sizing CANNOT be perfectly separated. The split below is an accounting "
    "identity, not a causal attribution: net = CLV$ + outcome residual - friction, where CLV$ = contracts x "
    "(canonical close price of the side held - price paid), outcome residual = gross return - contracts x close "
    "price (what the result paid beyond what the close priced), and friction is the remainder (fees and, on the "
    "recorded basis, the settlement fee).",
    "The canonical close is itself an estimate (a mid, at one moment). A YES+NO pair's legs offset each other's "
    "residuals by construction, so a pair's outcome residual says nothing about the game.",
    "Sizing/concentration is shown as the cluster's share of stake beside its share of net P&L; a large loss share "
    "on a large stake share is what concentration does whether or not the entry was good.",
    "One or two weeks of wagers is far too few to establish skill or its absence. Nothing here does.",
)


# ------------------------------------------------------------------------------------------ small helpers

def _num(x):
    if isinstance(x, bool) or x is None:
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _r(v, n=4):
    return None if v is None else round(v, n) + 0.0          # + 0.0: never print a negative zero


def net_figure(row: dict, bases=NET_BASES) -> tuple:
    """THE accessor for the net figure to use: (value, basis) from the first basis in `bases` the row has,
    else (None, None). Every P&L number in this module goes through here."""
    for b in bases:
        v = _num(row.get(b))
        if v is not None:
            return v, b
    return None, None


# ------------------------------------------------------------------------------------------ ticker parsing

_EVENT = re.compile(r"^(\d{2}[A-Z]{3}\d{2})([A-Z]+)$")
_PLAYER_TAIL = re.compile(r"^([A-Z]{3,})(\d{1,2})$")


def parse_ticker(ticker: str | None) -> dict:
    """Deterministic, lossless split of a Kalshi ticker into the keys exposure is grouped by."""
    t = ticker or ""
    parts = t.split("-") if t else []
    series = parts[0] if parts else "UNKNOWN"
    event = parts[1] if len(parts) >= 2 else (t or "UNKNOWN")
    rest = parts[2:]
    m = _EVENT.match(event)
    teams = m.group(2) if m else ""
    subject = rest[0] if rest else None

    player = player_team = None
    if subject and teams:
        for n in (3, 2):                              # three-letter team codes first (LAC before LA)
            team = subject[:n]
            if len(team) == n and (teams.startswith(team) or teams.endswith(team)):
                tail = _PLAYER_TAIL.match(subject[n:])
                if tail:
                    player, player_team = subject, team
                    break

    if len(rest) >= 2:
        ladder = f"{series}-{event}-{subject}"
    elif len(rest) == 1 and series in TEAM_SUBJECT_SERIES:
        ladder = f"{series}-{event}-{re.sub(r'[^A-Z]', '', subject)}"
    elif len(parts) >= 2:
        ladder = f"{series}-{event}"
    else:
        ladder = t or "UNKNOWN"
    return {"series": series, "event": event, "game_key": event, "subject": subject, "ladder": ladder,
            "player": player, "player_team": player_team}


# ------------------------------------------------------------------------------------------ clustering

def _clusters(rows: list, parsed: list, th: RiskThresholds) -> tuple:
    """Union-find over wagers; returns (cluster index per row, link rules per cluster root)."""
    parent = list(range(len(rows)))
    links: dict = {}
    pending: list = []

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j, rule):
        a, b = find(i), find(j)
        if a != b:
            parent[max(a, b)] = min(a, b)
        pending.append((i, rule))

    linked = th.same_game_linked_families
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            pi, pj = parsed[i], parsed[j]
            if pi["game_key"] != pj["game_key"]:
                continue
            ti, tj = rows[i].get("market_ticker"), rows[j].get("market_ticker")
            if ti and ti == tj:
                union(i, j, "SAME_MARKET")
                if {rows[i].get("side"), rows[j].get("side")} == {"YES", "NO"}:
                    union(i, j, "OPPOSING_POSITION_PAIR")
            elif pi["ladder"] == pj["ladder"]:
                union(i, j, "SAME_LADDER")
            if ti != tj and (linked is None or (rows[i].get("family") in linked and rows[j].get("family") in linked)):
                union(i, j, "SAME_GAME_CORRELATED")
    for i, rule in pending:
        links.setdefault(find(i), set()).add(rule)
    return [find(i) for i in range(len(rows))], links


# ------------------------------------------------------------------------------------------ aggregation

def _basis_status(rows: list) -> dict:
    out = {}
    for b in NET_BASES:
        have = sum(1 for r in rows if net_figure(r, (b,))[0] is not None)
        if have:
            out[b] = {"wagers": have, "complete": have == len(rows)}
    return out


def _primary_basis(status: dict, n: int) -> str | None:
    for b in NET_BASES:
        if b in status and status[b]["complete"] and n:
            return b
    return None


def _group(rows, keyfn, label_of, total_stake, bases, totals_pl):
    buckets: dict = {}
    for r in rows:
        k = keyfn(r)
        if k is None:
            continue
        buckets.setdefault(k, []).append(r)
    out = []
    for k, rs in buckets.items():
        stake = sum(_num(r.get("stake")) or 0.0 for r in rs)
        pl, complete, share_pl = {}, {}, {}
        for b in bases:
            vals = [net_figure(r, (b,))[0] for r in rs]
            known = [v for v in vals if v is not None]
            pl[b] = _r(sum(known)) if known else None
            complete[b] = len(known) == len(rs)
            tot = totals_pl.get(b)
            share_pl[b] = (_r(sum(known) / tot, 6) if known and tot not in (None, 0) else None)
        out.append({"key": k, "label": label_of(k, rs), "wagers": len(rs), "stake": _r(stake),
                    "stake_share": _r(stake / total_stake, 6) if total_stake > 0 else None,
                    "bankroll_share": None, "net": pl, "net_complete": complete, "share_of_net": share_pl,
                    "wager_ids": sorted(str(r.get("imported_wager_id")) for r in rs)})
    out.sort(key=lambda g: (-(g["stake"] or 0.0), str(g["key"])))
    return out


def game_label(key, rows) -> str:
    """The canonical game_id a close gave any of these rows (they share one event), else the event code."""
    canon = sorted({str(r.get("game")) for r in rows if r.get("game") and "-" not in str(r.get("game"))})
    return canon[0] if canon else key


def _clv_dollars(r):
    v = _num(r.get("clv_dollars"))
    if v is not None:
        return v
    c, n = _num(r.get("clv_per_contract")), _num(r.get("contracts"))
    return c * n if c is not None and n is not None else None


def _decompose(cluster, rs, primary):
    clv_valid = [r for r in rs if r.get("clv_state") == "CLV_VALID" and _clv_dollars(r) is not None]
    clv_d = sum(_clv_dollars(r) for r in clv_valid)
    contracts = sum(_num(r.get("contracts")) or 0.0 for r in clv_valid)
    residual_ok = all(_num(r.get("gross_return")) is not None and _num(r.get("close_price")) is not None
                      and _num(r.get("contracts")) is not None for r in rs)
    residual = (sum(_num(r["gross_return"]) - _num(r["contracts"]) * _num(r["close_price"]) for r in rs)
                if residual_ok else None)
    net_vals = [net_figure(r, (primary,))[0] for r in rs] if primary else []
    net = sum(net_vals) if net_vals and all(v is not None for v in net_vals) else None
    clv_complete = len(clv_valid) == len(rs)
    friction = (clv_d + residual - net) if (net is not None and residual is not None and clv_complete) else None
    mean = clv_d / contracts if clv_valid and contracts else None
    return {
        "cluster": cluster["key"], "label": cluster["label"], "wagers": len(rs),
        "sizing": {"stake": cluster["stake"], "stake_share": cluster["stake_share"],
                   "share_of_net": cluster["share_of_net"].get(primary) if primary else None},
        "entry_quality": {"clv_valid": len(clv_valid), "clv_dollars": _r(clv_d) if clv_valid else None,
                          "mean_clv_per_contract": _r(mean, 6),
                          "sign": (None if mean is None else "POSITIVE" if mean > 0 else "NEGATIVE" if mean < 0
                                   else "ZERO")},
        "outcome_variance": {"residual_vs_close": _r(residual),
                             "results": sorted(str(r.get("result") or r.get("settlement_state")) for r in rs)},
        "friction": _r(friction), "net": _r(net), "basis": primary,
    }


def _pairs(rows: list) -> list:
    by_market: dict = {}
    for r in rows:
        by_market.setdefault(r.get("market_ticker"), []).append(r)
    out = []
    for t, rs in sorted(by_market.items(), key=lambda kv: str(kv[0])):
        yes = [r for r in rs if r.get("side") == "YES"]
        no = [r for r in rs if r.get("side") == "NO"]
        if not (t and yes and no):
            continue
        cy = sum(_num(r.get("contracts")) or 0.0 for r in yes)
        cn = sum(_num(r.get("contracts")) or 0.0 for r in no)
        py = sum((_num(r.get("contracts")) or 0.0) * (_num(r.get("execution_price")) or 0.0) for r in yes) / cy if cy else None
        pn = sum((_num(r.get("contracts")) or 0.0) * (_num(r.get("execution_price")) or 0.0) for r in no) / cn if cn else None
        matched = min(cy, cn)
        combined = (py + pn) if py is not None and pn is not None else None
        out.append({"market_ticker": t, "wagers": len(rs), "yes_contracts": _r(cy), "no_contracts": _r(cn),
                    "matched_contracts": _r(matched), "combined_price_per_matched_contract": _r(combined, 6),
                    # One YES and one NO on the same contract pay exactly 1.00 together whatever happens, so the
                    # matched part's result is fixed at entry: matched x (1 - combined price), before fees.
                    "locked_pl_before_fees": _r(matched * (1.0 - combined)) if combined is not None else None,
                    "stake": _r(sum(_num(r.get("stake")) or 0.0 for r in rs)),
                    "wager_ids": sorted(str(r.get("imported_wager_id")) for r in rs)})
    return out


def assess(rows: list, *, thresholds: RiskThresholds = DEFAULT_THRESHOLDS, bankroll: dict | None = None) -> dict:
    """The risk block for one scope (a week, or a season) of postmortem wager rows. Pure; never mutates rows.

    `bankroll`, if given, must be evidence: {"starting_bankroll": <positive number>, "source": <where it came
    from>}. Anything else leaves every bankroll share NOT_AVAILABLE."""
    th = thresholds
    rows = sorted(rows or [], key=lambda r: (str(r.get("market_ticker")), str(r.get("side")),
                                             str(r.get("imported_wager_id"))))
    parsed = [parse_ticker(r.get("market_ticker")) for r in rows]
    pid = {id(r): p for r, p in zip(rows, parsed)}
    total_stake = sum(_num(r.get("stake")) or 0.0 for r in rows)

    status = _basis_status(rows)
    primary = _primary_basis(status, len(rows))
    bases = [b for b in NET_BASES if b in status]
    totals_pl = {}
    for b in bases:
        vals = [net_figure(r, (b,))[0] for r in rows]
        totals_pl[b] = sum(v for v in vals if v is not None)
    totals_net = {b: {"net": _r(totals_pl[b]), "complete": status[b]["complete"], "wagers": status[b]["wagers"],
                      "roi": _r(totals_pl[b] / total_stake, 6) if status[b]["complete"] and total_stake > 0 else None}
                  for b in bases}

    br = None
    if bankroll and (_num(bankroll.get("starting_bankroll")) or 0) > 0 and bankroll.get("source"):
        br = _num(bankroll["starting_bankroll"])
        bankroll_block = {"state": "AVAILABLE", "starting_bankroll": br, "source": str(bankroll["source"])}
    else:
        bankroll_block = {"state": "NOT_AVAILABLE",
                          "reason": "no readable starting-bankroll evidence for the owner's account (the router's "
                                    "bankroll is a secret; nothing is guessed)"}

    cidx, clinks = _clusters(rows, parsed, th)
    cluster_of = {id(r): c for r, c in zip(rows, cidx)}
    # Deterministic cluster ids: game label + ordinal of the cluster's first (sorted) ticker within the game.
    game_labels = {g: game_label(g, [r for r in rows if pid[id(r)]["game_key"] == g])
                   for g in {p["game_key"] for p in parsed}}
    roots_by_game: dict = {}
    for r, c in zip(rows, cidx):
        roots_by_game.setdefault(pid[id(r)]["game_key"], [])
        if c not in roots_by_game[pid[id(r)]["game_key"]]:
            roots_by_game[pid[id(r)]["game_key"]].append(c)
    cluster_name = {}
    for g, roots in roots_by_game.items():
        lbl = game_labels[g]
        for n, c in enumerate(roots, 1):
            cluster_name[c] = f"{lbl}#{n}"

    def grouped(keyfn, label=lambda k, rs: k):
        return _group(rows, keyfn, label, total_stake, bases, totals_pl)

    groups = {
        "cluster": grouped(lambda r: cluster_name[cluster_of[id(r)]]),
        "game": grouped(lambda r: pid[id(r)]["game_key"], game_label),
        "market": grouped(lambda r: r.get("market_ticker") or "UNKNOWN"),
        "ladder": grouped(lambda r: pid[id(r)]["ladder"]),
        "family": grouped(lambda r: r.get("family") or "UNKNOWN"),
        "player": grouped(lambda r: pid[id(r)]["player"]),
    }
    root_by_name = {v: k for k, v in cluster_name.items()}
    for c in groups["cluster"]:
        c["links"] = sorted(clinks.get(root_by_name[c["key"]], ()))
    if br:
        for gs in groups.values():
            for g in gs:
                g["bankroll_share"] = _r(g["stake"] / br, 6)

    wager_list = sorted(
        ({"imported_wager_id": r.get("imported_wager_id"), "market_ticker": r.get("market_ticker"),
          "side": r.get("side"), "game": game_labels[pid[id(r)]["game_key"]],
          "ladder": pid[id(r)]["ladder"], "player": pid[id(r)]["player"],
          "cluster": cluster_name[cluster_of[id(r)]], "stake": _r(_num(r.get("stake"))),
          "stake_share": _r((_num(r.get("stake")) or 0.0) / total_stake, 6) if total_stake > 0 else None,
          "net": _r(net_figure(r, (primary,))[0]) if primary else None} for r in rows),
        key=lambda w: (-(w["stake"] or 0.0), str(w["imported_wager_id"])))

    def top(items, key="key"):
        if not items:
            return None
        g = items[0]
        return {"key": g.get(key), "label": g.get("label", g.get(key)), "stake": g["stake"],
                "stake_share": g["stake_share"], "bankroll_share": (_r(g["stake"] / br, 6) if br else None)}

    largest = {"wager": top(wager_list, "imported_wager_id"), "game": top(groups["game"]),
               "market": top(groups["market"]), "ladder": top(groups["ladder"]),
               "cluster": top(groups["cluster"]), "player": top(groups["player"])}
    if largest["wager"]:
        largest["wager"]["label"] = wager_list[0]["market_ticker"]

    pairs = _pairs(rows)
    warnings = []
    for c in groups["cluster"]:
        s = c["stake_share"] or 0.0
        if s > th.concentration_high_share:
            warnings.append({"code": "CONCENTRATION_HIGH", "subject": c["key"], "value": s,
                             "threshold": th.concentration_high_share,
                             "detail": f"one correlated cluster carries {s:.1%} of the scope's stake"})
        if c["wagers"] >= th.correlated_min_wagers and s > th.correlated_exposure_high_share:
            warnings.append({"code": "CORRELATED_EXPOSURE_HIGH", "subject": c["key"], "value": s,
                             "threshold": th.correlated_exposure_high_share,
                             "detail": f"{c['wagers']} linked legs ({', '.join(c['links'])}) carry {s:.1%} of stake"})
    for p in pairs:
        s = (p["stake"] or 0.0) / total_stake if total_stake > 0 else 0.0
        if s > th.opposing_pair_min_share:
            warnings.append({"code": "OPPOSING_POSITION_PAIR", "subject": p["market_ticker"], "value": _r(s, 6),
                             "threshold": th.opposing_pair_min_share,
                             "detail": (f"YES and NO on one contract; {p['matched_contracts']} matched contracts "
                                        f"at a combined {p['combined_price_per_matched_contract']} per contract fix "
                                        f"that part's result at entry")})
    for g in groups["game"]:
        s = g["stake_share"] or 0.0
        if s > th.single_game_dominates_share:
            warnings.append({"code": "SINGLE_GAME_DOMINATES_WEEK", "subject": g["label"], "value": s,
                             "threshold": th.single_game_dominates_share,
                             "detail": f"one game carries {s:.1%} of the scope's stake"})
    order = ("CONCENTRATION_HIGH", "CORRELATED_EXPOSURE_HIGH", "OPPOSING_POSITION_PAIR", "SINGLE_GAME_DOMINATES_WEEK")
    warnings.sort(key=lambda w: (order.index(w["code"]), -w["value"], str(w["subject"])))
    for w in warnings:
        w["value"] = _r(w["value"], 6)
        w["threshold"] = _r(w["threshold"], 6)

    by_cluster_rows: dict = {}
    for r in rows:
        by_cluster_rows.setdefault(cluster_name[cluster_of[id(r)]], []).append(r)
    decomposition = [_decompose(c, by_cluster_rows[c["key"]], primary) for c in groups["cluster"]]

    return {
        "risk_version": RISK_VERSION, "wagers": len(rows),
        "thresholds": asdict(th), "link_rules": dict(LINK_RULES),
        "net_basis": {"preference": list(NET_BASES), "primary": primary, "available": status,
                      "note": ("P&L below is on the primary basis (the most-preferred one every wager has); other "
                               "bases are shown beside it, never merged." if primary else
                               "No net basis covers every wager in scope; P&L figures are for the wagers that "
                               "have one and are labelled incomplete.")},
        "bankroll": bankroll_block,
        "totals": {"stake": _r(total_stake), "net": totals_net},
        "largest": largest, "groups": groups, "wager_exposure": wager_list,
        "opposing_pairs": pairs, "warnings": warnings,
        "warning_counts": {c: sum(1 for w in warnings if w["code"] == c) for c in order},
        "decomposition": decomposition, "decomposition_caveats": list(DECOMPOSITION_CAVEATS),
    }


# ------------------------------------------------------------------------------------------ rendering

def _money(v):
    return "—" if v is None else f"{v:,.2f}"


def _pct(v):
    return "—" if v is None else f"{100.0 * v:.1f}%"


def render_section(risk: dict) -> list:
    """Markdown lines for the RISK & CONCENTRATION section of the postmortem document."""
    if not risk:
        return []
    L = ["## RISK & CONCENTRATION", "",
         "Governance reporting only: where the placed stake sat and how much of the result each exposure explains. "
         "Nothing here changes, recommends or caps a stake. Different tickers are not diversification: wagers are "
         "grouped by game, market, ladder (one underlying variable) and correlated cluster.", ""]
    nb = risk["net_basis"]
    primary = nb["primary"]
    t = risk["totals"]
    L.append(f"Net basis: **{primary or 'NONE COMPLETE'}** (preference {' > '.join(nb['preference'])}). {nb['note']}")
    L.append("")
    L.extend(["| basis | wagers with figure | complete | stake | net P&L | ROI |", "|---|---|---|---|---|---|"])
    for b, v in t["net"].items():
        L.append(f"| {b}{' (primary)' if b == primary else ''} | {v['wagers']} | {'yes' if v['complete'] else 'NO'} | "
                 f"{_money(t['stake'])} | {_money(v['net'])} | {_pct(v['roi'])} |")
    bk = risk["bankroll"]
    L.extend(["", f"Share of starting bankroll: {bk['state']}"
              + (f" (starting bankroll {_money(bk['starting_bankroll'])}, source: {bk['source']})." if bk["state"] ==
                 "AVAILABLE" else f" — {bk['reason']}."), ""])

    L.extend(["### Warnings", ""])
    if risk["warnings"]:
        L.extend(["| code | subject | value | threshold | detail |", "|---|---|---|---|---|"])
        for w in risk["warnings"]:
            L.append(f"| {w['code']} | {w['subject']} | {_pct(w['value'])} | > {_pct(w['threshold'])} | {w['detail']} |")
    else:
        L.append("None at the configured thresholds.")
    L.append("")

    L.extend(["### Largest exposures", "", "| exposure | which | stake | % of scope stake | % of bankroll |",
              "|---|---|---|---|---|"])
    for k, v in risk["largest"].items():
        if v is None:
            L.append(f"| {k} | none parsable | — | — | — |")
        else:
            L.append(f"| {k} | {v['label']} | {_money(v['stake'])} | {_pct(v['stake_share'])} | "
                     f"{_pct(v['bankroll_share']) if v['bankroll_share'] is not None else bk['state']} |")
    L.append("")

    bases = list(t["net"].keys())

    def table(title, key, extra_links=False):
        hdr = "| group | wagers | stake | % stake |" + "".join(f" net ({b}) | % of net ({b}) |" for b in bases)
        if extra_links:
            hdr += " links |"
        L.extend([f"### {title}", "", hdr, "|" + "---|" * (hdr.count("|") - 1)])
        for g in risk["groups"][key]:
            line = f"| {g['label']} | {g['wagers']} | {_money(g['stake'])} | {_pct(g['stake_share'])} |"
            for b in bases:
                inc = "" if g["net_complete"].get(b) else " (partial)"
                line += f" {_money(g['net'].get(b))}{inc} | {_pct(g['share_of_net'].get(b))} |"
            if extra_links:
                line += f" {', '.join(g.get('links') or []) or 'single wager'} |"
            L.append(line)
        L.append("")

    L.append("`% of net` is the group's net divided by the scope's net on that basis: when the scope lost, it is "
             "the group's share of the total loss (a winning group shows a negative share); shares sum to 100%.")
    L.append("")
    table("By correlated cluster", "cluster", extra_links=True)
    table("By game", "game")
    table("By market family", "family")
    table("By ladder (underlying variable)", "ladder")
    table("By market", "market")
    if risk["groups"]["player"]:
        table("By player (parsable player props; not a partition of stake)", "player")

    if risk["opposing_pairs"]:
        L.extend(["### Opposing positions (YES + NO on one contract)", "",
                  "| market | YES contracts | NO contracts | matched | combined price | locked P&L before fees | stake |",
                  "|---|---|---|---|---|---|---|"])
        for p in risk["opposing_pairs"]:
            L.append(f"| {p['market_ticker']} | {p['yes_contracts']} | {p['no_contracts']} | {p['matched_contracts']} | "
                     f"{p['combined_price_per_matched_contract']} | {_money(p['locked_pl_before_fees'])} | "
                     f"{_money(p['stake'])} |")
        L.append("")

    L.extend(["### Decomposition: entry quality, outcome variance, sizing", ""])
    L.extend(f"* {c}" for c in risk["decomposition_caveats"])
    L.extend(["", f"| cluster | wagers | % stake | % of net ({primary}) | CLV valid | CLV$ | mean CLV/contract | "
                  f"sign | outcome residual vs close | friction | net ({primary}) |",
              "|---|---|---|---|---|---|---|---|---|---|---|"])
    for d in risk["decomposition"]:
        e, o, s = d["entry_quality"], d["outcome_variance"], d["sizing"]
        mc = "—" if e["mean_clv_per_contract"] is None else format(e["mean_clv_per_contract"], "+.4f")
        L.append(f"| {d['label']} | {d['wagers']} | {_pct(s['stake_share'])} | {_pct(s['share_of_net'])} | "
                 f"{e['clv_valid']} | {_money(e['clv_dollars'])} | {mc} | {e['sign'] or '—'} | "
                 f"{_money(o['residual_vs_close'])} | {_money(d['friction'])} | {_money(d['net'])} |")
    L.append("")

    th = risk["thresholds"]
    L.extend(["### Rules and thresholds", ""])
    L.extend(f"* {k}: {v}" for k, v in risk["link_rules"].items())
    L.append(f"* Thresholds (share of scope stake, strictly greater fires): CONCENTRATION_HIGH > "
             f"{_pct(th['concentration_high_share'])} for one cluster; CORRELATED_EXPOSURE_HIGH > "
             f"{_pct(th['correlated_exposure_high_share'])} for a cluster of ≥ {th['correlated_min_wagers']} legs; "
             f"SINGLE_GAME_DOMINATES_WEEK > {_pct(th['single_game_dominates_share'])} for one game; "
             f"OPPOSING_POSITION_PAIR for any YES+NO pair above {_pct(th['opposing_pair_min_share'])}. "
             f"Same-game linked families: {'every family' if th['same_game_linked_families'] is None else ', '.join(th['same_game_linked_families'])}.")
    L.append("")
    return L
