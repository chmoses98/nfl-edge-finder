"""OWNER ACTUAL PLACED WAGERS: a weekly postmortem. ACCOUNTING, not model evidence.

Every wager in `imported_wagers` was placed by the owner and recommended by nothing in this repository. This
module adds up what those wagers staked, paid in fees, returned and netted, by week, by market family and by
game -- and, where the market's own canonical close exists, what the close said about the price paid (CLV).
It is kept structurally apart from every simulated or model economics figure: nothing here reads a projection,
and nothing that measures a model may read this (see `wager_settlements`).

WHAT IS NEVER DONE HERE
-----------------------
* No figure is inferred. A settlement whose return the exchange did not establish stays UNESTABLISHED, and a
  week containing one gets no headline total -- the established subset is shown, labelled as a subset.
* No close is inferred. CLV uses the canonical close (`nfl_edge.evaluation.close`, rule close-2.x) of the EXACT
  contract, as published under `data/shadow/v2/closes/`. A contract the capture never closed is
  NO_CANONICAL_CLOSE; a one-sided or stale close is reported as such and excluded from CLV means.
* CLV is per contract on the side HELD: YES uses the close YES mid, NO the close NO mid, minus the price paid.
  Fees are not in CLV; they are in net profit and loss, where the exchange put them.
* Small samples are small. The report prints counts beside every rate and makes no claim of profitability.
"""
from __future__ import annotations

import math

POSTMORTEM_VERSION = "actual-wager-postmortem-1.0.0"

HEADER = (
    "OWNER ACTUAL PLACED WAGERS -- ACCOUNTING ONLY. Every wager here was placed by the owner and recommended by "
    "nothing in this repository. These are real-money facts about a bankroll, not evidence about any model, and "
    "they are never used to train or tune one. Counts are small; no rate below establishes an edge."
)

CLOSE_USABLE = ("CLOSE_OK",)
USABLE_QUALITY = ("EXCELLENT", "GOOD")

#: Kalshi NFL series -> the family label the research report uses, where the mapping is unambiguous. Anything
#: else is reported under its own series name rather than guessed into a family.
SERIES_FAMILY = {
    "KXNFLGAME": "game_winner",
    "KXNFLSPREAD": "spread",
    "KXNFLTOTAL": "total",
    "KXNFLTEAMTOTAL": "team_total",
}


def _num(x):
    if isinstance(x, bool) or x is None:
        return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def family_of(ticker: str | None) -> str:
    series = (ticker or "").split("-", 1)[0]
    return SERIES_FAMILY.get(series, f"series:{series or 'UNKNOWN'}")


def event_of(ticker: str | None) -> str:
    parts = (ticker or "").split("-")
    return "-".join(parts[:2]) if len(parts) >= 2 else (ticker or "UNKNOWN")


def closes_by_ticker(close_rows) -> dict:
    """ticker -> the canonical close row. The same contract closes once; rows repeated per model arm/horizon are
    collapsed, and a ticker whose rows DISAGREE about the close is marked rather than resolved by picking one."""
    out: dict = {}
    for row in close_rows or ():
        t = row.get("ticker")
        if not t:
            continue
        prev = out.get(t)
        if prev is None:
            out[t] = dict(row)
            continue
        if prev.get("close_id") != row.get("close_id") and prev.get("close_status") != "CLOSE_CONFLICT":
            if (prev.get("mid"), prev.get("no_mid")) != (row.get("mid"), row.get("no_mid")):
                out[t] = {"ticker": t, "game_id": prev.get("game_id"), "close_status": "CLOSE_CONFLICT",
                          "close_reason": "two canonical close records for one contract disagree"}
    return out


def wager_row(wager: dict, settlement: dict | None, close: dict | None) -> dict:
    side = wager.get("side")
    price = _num(wager.get("actual_price"))
    contracts = _num(wager.get("contracts"))
    row = {
        "imported_wager_id": wager.get("imported_wager_id"), "source_bet_key": wager.get("source_bet_key"),
        "season": wager.get("season"), "week": wager.get("week"), "game_date": wager.get("game_date"),
        "game": (close or {}).get("game_id") or event_of(wager.get("market_ticker")),
        "family": family_of(wager.get("market_ticker")), "market_ticker": wager.get("market_ticker"),
        "side": side, "contracts": contracts, "execution_price": price,
        "stake": _num(wager.get("stake")), "fees": _num(wager.get("fees_paid")),
        "fees_are_estimated": bool(wager.get("fees_are_estimated")),
        "settlement_state": "PENDING", "result": None, "gross_return": None, "net_profit_loss": None,
        "pl_state": "PENDING",
    }
    if settlement and settlement.get("settlement_status") == "SETTLED":
        row["settlement_state"] = "SETTLED"
        row["result"] = settlement.get("result")
        row["gross_return"] = _num(settlement.get("gross_return"))
        row["net_profit_loss"] = _num(settlement.get("net_profit_loss"))
        row["pl_state"] = "ESTABLISHED" if row["net_profit_loss"] is not None else "UNESTABLISHED"
        # The router's net is gross - stake - settlement fee, and `stake` already carries the ENTRY fee. The
        # settlement fee is therefore exactly what the three exchange figures leave over -- recovered, not guessed.
        if row["pl_state"] == "ESTABLISHED" and row["gross_return"] is not None and row["stake"] is not None:
            row["settlement_fee"] = round(row["gross_return"] - row["stake"] - row["net_profit_loss"], 6)
        if row["pl_state"] == "UNESTABLISHED":
            row["pl_refusals"] = list(settlement.get("refusals") or [])

    # CLV on the side held, against the canonical close of this exact contract.
    if close is None:
        row.update(clv_state="NO_CANONICAL_CLOSE", clv_per_contract=None, close_price=None, close_quality=None)
    elif close.get("close_status") not in CLOSE_USABLE:
        row.update(clv_state=str(close.get("close_status") or "CLOSE_MISSING"), clv_per_contract=None,
                   close_price=None, close_quality=close.get("close_quality"),
                   close_reason=close.get("close_reason"))
    else:
        held = _num(close.get("mid")) if side == "YES" else _num(close.get("no_mid")) if side == "NO" else None
        quality = close.get("close_quality")
        if held is None or price is None:
            row.update(clv_state="CLOSE_PRICE_UNAVAILABLE_FOR_SIDE", clv_per_contract=None, close_price=held,
                       close_quality=quality)
        else:
            clv = round(held - price, 6)
            row.update(clv_state=("CLV_VALID" if quality in USABLE_QUALITY else f"CLV_{quality}_CLOSE"),
                       clv_per_contract=clv, close_price=held, close_quality=quality,
                       clv_dollars=(round(clv * contracts, 6) if contracts is not None else None))
    return row


def reconcile_fees(rows: list) -> None:
    """FEE RECONCILIATION, from exchange figures alone. Mutates `rows`, adding `fee_reconciliation` and
    `net_fee_reconciled`.

    The router states net = gross - stake - settlement fee, where `stake` already includes the entry fee the
    exchange charged on the order's fills, and "settlement fee" is Kalshi's settlement `fee_cost`. In every
    2026 week 1-2 NFL position that fee equals, to the cent, the entry fees already inside the stakes of the
    owner's orders on that market -- the order's own for a single-order position, the SUM of both legs' for a
    YES+NO pair (6.1786 = 1.9152 + 4.2634; 33.4065 = 31.1955 + 2.2110). A payout-time fee could not equal the
    trading fee on positions that paid nothing. The evidence says `fee_cost` is the position's cumulative
    trading fee, so the recorded net subtracts it a second time.

    Nothing is rewritten: the recorded net stays exactly as filed. Where -- and only where -- the recovered
    settlement fee equals the sum of the entry fees of every owner order on that market, the reconciled net is
    gross - stake (state FEE_EQUALS_ENTRY_FEES). Anything else is UNRECONCILED and gets no reconciled figure.
    """
    by_market: dict = {}
    for r in rows:
        by_market.setdefault(r.get("market_ticker"), []).append(r)
    for r in rows:
        if r.get("pl_state") != "ESTABLISHED" or r.get("settlement_fee") is None:
            r["fee_reconciliation"] = "NOT_APPLICABLE"
            r["net_fee_reconciled"] = None
            continue
        entry_on_market = sum((x.get("fees") or 0.0) for x in by_market.get(r.get("market_ticker"), []))
        if abs(r["settlement_fee"] - entry_on_market) <= 1e-4:
            r["fee_reconciliation"] = "FEE_EQUALS_ENTRY_FEES"
            r["net_fee_reconciled"] = round(r["gross_return"] - r["stake"], 6)
        else:
            r["fee_reconciliation"] = "UNRECONCILED"
            r["net_fee_reconciled"] = None


def summarise(rows: list) -> dict:
    n = len(rows)
    settled = [r for r in rows if r["settlement_state"] == "SETTLED"]
    est = [r for r in settled if r["pl_state"] == "ESTABLISHED"]
    won = sum(1 for r in settled if r["result"] == "WON")
    lost = sum(1 for r in settled if r["result"] == "LOST")
    stake_all = sum(r["stake"] or 0.0 for r in rows)
    fees_all = sum(r["fees"] or 0.0 for r in rows)
    stake_est = sum(r["stake"] or 0.0 for r in est)
    gross_est = sum(r["gross_return"] or 0.0 for r in est)
    net_est = sum(r["net_profit_loss"] or 0.0 for r in est)
    valid_clv = [r["clv_per_contract"] for r in rows if r.get("clv_state") == "CLV_VALID"]
    clv_states: dict = {}
    for r in rows:
        clv_states[r.get("clv_state")] = clv_states.get(r.get("clv_state"), 0) + 1
    complete = bool(rows) and len(est) == n
    recon = [r for r in est if r.get("fee_reconciliation") == "FEE_EQUALS_ENTRY_FEES"]
    recon_complete = complete and len(recon) == len(est)
    net_recon = sum(r["net_fee_reconciled"] for r in recon)
    return {
        "wagers": n, "settled": len(settled), "pending": n - len(settled), "won": won, "lost": lost,
        "other_result": len(settled) - won - lost,
        "pl_established": len(est), "pl_unestablished": len(settled) - len(est),
        "stake": round(stake_all, 4), "fees": round(fees_all, 4),
        "settlement_fees_established": round(sum(r.get("settlement_fee") or 0.0 for r in est), 4),
        # Headline economics only when EVERY wager in scope is settled with an established figure.
        "complete": complete,
        "gross_return": round(gross_est, 4) if complete else None,
        "net_profit_loss": round(net_est, 4) if complete else None,
        "roi": (round(net_est / stake_est, 6) if complete and stake_est > 0 else None),
        # The recorded net as filed, and beside it the fee-reconciled net (see reconcile_fees). Never merged.
        "fee_reconciled": {"wagers": len(recon), "complete": recon_complete,
                           "net_profit_loss": round(net_recon, 4) if recon_complete else None,
                           "roi": (round(net_recon / stake_est, 6) if recon_complete and stake_est > 0 else None),
                           "double_counted_fees": (round(net_recon - net_est, 4) if recon_complete else None)},
        "established_subset": {"wagers": len(est), "stake": round(stake_est, 4), "gross_return": round(gross_est, 4),
                               "net_profit_loss": round(net_est, 4),
                               "roi": round(net_est / stake_est, 6) if stake_est > 0 else None},
        "clv": {"valid": len(valid_clv),
                "mean_per_contract": round(sum(valid_clv) / len(valid_clv), 6) if valid_clv else None,
                "positive_rate": round(sum(1 for v in valid_clv if v > 0) / len(valid_clv), 4) if valid_clv else None,
                "states": dict(sorted(clv_states.items(), key=lambda kv: str(kv[0])))},
    }


def build(wagers: list, settlements: list, close_rows, *, season: int, week: int | None = None) -> dict:
    by_key = {s.get("source_bet_key"): s for s in settlements or () if s.get("source_bet_key")}
    closes = closes_by_ticker(close_rows)
    rows = [wager_row(w, by_key.get(w.get("source_bet_key")), closes.get(w.get("market_ticker")))
            for w in wagers if w.get("season") == season and (week is None or w.get("week") == week)]
    rows.sort(key=lambda r: (r["week"] or 0, r["game_date"] or "", r["market_ticker"] or "", r["imported_wager_id"] or ""))
    reconcile_fees(rows)

    def group(key):
        out = {}
        for r in rows:
            out.setdefault(str(r[key]), []).append(r)
        return {k: summarise(v) for k, v in sorted(out.items())}

    return {"postmortem_version": POSTMORTEM_VERSION, "season": season, "week": week, "header": HEADER,
            "totals": summarise(rows), "by_week": group("week"), "by_family": group("family"),
            "by_game": group("game"), "wagers": rows}


def _money(v):
    return "—" if v is None else f"{v:,.2f}"


def _pct(v):
    return "—" if v is None else f"{100.0 * v:.1f}%"


def render(doc: dict) -> str:
    scope = f"season {doc['season']}" + (f", week {doc['week']}" if doc.get("week") is not None else "")
    L = [f"# Owner actual placed wagers — {scope}", "", f"> {doc['header']}", ""]

    def table(title, groups):
        L.extend([f"## {title}", "",
                  "| group | wagers | W | L | pending | P&L unestablished | stake | fees | gross return | net P&L | ROI | "
                  "CLV valid | mean CLV/contract | CLV>0 | no close |",
                  "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"])
        for name, s in groups.items():
            no_close = sum(v for k, v in s["clv"]["states"].items() if k != "CLV_VALID")
            L.append(f"| {name} | {s['wagers']} | {s['won']} | {s['lost']} | {s['pending']} | {s['pl_unestablished']} | "
                     f"{_money(s['stake'])} | {_money(s['fees'])} | {_money(s['gross_return'])} | "
                     f"{_money(s['net_profit_loss'])} | {_pct(s['roi'])} | {s['clv']['valid']} | "
                     f"{'—' if s['clv']['mean_per_contract'] is None else format(s['clv']['mean_per_contract'], '+.4f')} | "
                     f"{_pct(s['clv']['positive_rate'])} | {no_close} |")
        L.append("")

    t = doc["totals"]
    L.extend(["Stake is contracts x execution price PLUS the entry fee the exchange charged on the fills; `fees` is "
              "that entry fee. Net P&L is the router's settlement figure: gross return - stake - settlement fee "
              f"(settlement fees on established wagers: {_money(t['settlement_fees_established'])}). CLV is per "
              "contract on the side held, against the canonical close of the exact contract, excluding fees.", ""])
    table("Totals", {"all": t})
    fr = t["fee_reconciled"]
    L.append("FEE RECONCILIATION (a finding, not a rewrite). Kalshi's settlement `fee_cost` equals, to the cent, the "
             "entry fees already inside the stakes on every reconciled position, so the recorded net subtracts the "
             "trading fee twice. Recorded net stays as filed; the reconciled net is gross - stake where the exchange's "
             f"own figures prove that equality ({fr['wagers']} of {t['pl_established']} established wagers). "
             + (f"Fee-reconciled net P&L: {_money(fr['net_profit_loss'])} (ROI {_pct(fr['roi'])}); fees counted twice "
                f"in the recorded figure: {_money(fr['double_counted_fees'])}." if fr["complete"]
                else "Not every established wager reconciles, so no fee-reconciled total is stated."))
    L.append("")
    if not t["complete"]:
        es = t["established_subset"]
        L.append(f"Headline gross/net/ROI withheld: {t['pending']} pending and {t['pl_unestablished']} settled with an "
                 f"unestablished figure. ESTABLISHED SUBSET ONLY ({es['wagers']} of {t['wagers']} wagers, not the "
                 f"period's P&L): stake {_money(es['stake'])}, gross {_money(es['gross_return'])}, net "
                 f"{_money(es['net_profit_loss'])}, ROI {_pct(es['roi'])}.")
        L.append("")
    table("By week", doc["by_week"])
    table("By market family", doc["by_family"])
    table("By game", doc["by_game"])
    L.extend(["## Wagers", "", "| week | game | family | side | contracts | price | stake | fees | result | gross | "
              "net | close | CLV/contract | CLV state |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"])
    for r in doc["wagers"]:
        L.append(f"| {r['week']} | {r['game']} | {r['family']} | {r['side']} | {r['contracts']} | {r['execution_price']} | "
                 f"{_money(r['stake'])} | {_money(r['fees'])} | {r['result'] or r['settlement_state']} | "
                 f"{_money(r['gross_return'])} | {_money(r['net_profit_loss'])} | "
                 f"{'—' if r.get('close_price') is None else r['close_price']} | "
                 f"{'—' if r.get('clv_per_contract') is None else format(r['clv_per_contract'], '+.4f')} | {r['clv_state']} |")
    L.append("")
    return "\n".join(L)
