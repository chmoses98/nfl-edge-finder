"""Bankroll evidence for stake authorization: available cash, total bankroll and existing exposure are three different numbers, and any of them can be missing.

WHAT IS KNOWN AND WHERE IT COMES FROM
-------------------------------------
* AVAILABLE CASH -- what the owner can put into new positions today. The only privacy-safe source in the owner's stack is the router's read-only balance
  delivery (kalshi-bet-router `publish-bankroll-nfl.yml`, docs/BANKROLL_DELIVERY.md section 7): the router reads the account balance (read-only), seals it with
  libsodium and writes it into THIS repository's Actions secret `KALSHI_BANKROLL_CONTEXT`, so a public repository never shows the amount. A workflow
  exposes it to this module as the environment variable of the same name, a JSON object:

      {"bankroll": <dollars>, "observedAt": "<ISO-8601 UTC>", "valueType": "KALSHI_AVAILABLE_CASH_BALANCE", "source": "...", "currency": "USD", ...}

  The delivery refuses readings older than 30 minutes and so does this module. `valueType` must be exactly KALSHI_AVAILABLE_CASH_BALANCE (not
  total portfolio value). An operator running the card by hand may pass a local JSON file with the same shape; the file is never committed.
* EXISTING EXPOSURE -- the cost of the owner's unsettled positions, from the owner's own fills in the handicap-data ledger (`card.owner_open_exposure`).
* TOTAL BANKROLL -- NOT read from anywhere. It is ESTIMATED as available cash + exposure at cost, and labelled an estimate. It feeds only the policy's optional
  fractional guards (3% per position, 10% per slate); the owner's 1U = $75, 1-5U rule does not depend on it.

FAIL CLOSED. With no usable evidence the result is `state != OK` and `authorizes_stakes` is False: the card still shows what it would price (as a
CANDIDATE) and says in words that no stake is authorized. A bankroll guard is never silently skipped, and a number nobody can date is never used.

PRIVACY. `public_view` carries the state and booleans only. Amounts exist in memory and in the private card; they are never in anything a public workflow
prints or commits.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

BANKROLL_VERSION = "bankroll-1.1.0"
ENV_CONTEXT = "KALSHI_BANKROLL_CONTEXT"
VALUE_TYPE = "KALSHI_AVAILABLE_CASH_BALANCE"
MAX_AGE_HOURS = 0.5           # the delivery's own freshness window: a balance older than 30 minutes is not evidence about now

OK, MISSING, STALE, INVALID = "OK", "MISSING", "STALE", "INVALID"


def _ts(v):
    if not v:
        return None
    try:
        d = datetime.fromisoformat(str(v).strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def load(as_of: datetime, *, env: dict | None = None, file_path: str | None = None, open_exposure_dollars: float | None = None,
         max_age_hours: float = MAX_AGE_HOURS) -> dict:
    env = os.environ if env is None else env
    src, raw = None, None
    if file_path:
        try:
            with open(file_path) as f:
                raw, src = f.read(), "local file (never committed)"
        except OSError as e:
            return _result(INVALID, [f"bankroll file unreadable: {type(e).__name__}"], None, None, None, open_exposure_dollars, as_of, None)
    elif (env.get(ENV_CONTEXT) or "").strip():
        raw, src = env[ENV_CONTEXT], "router balance delivery (sealed Actions secret)"
    else:
        return _result(MISSING, ["no bankroll evidence: the router balance delivery (" + ENV_CONTEXT + ") is not present and no local file was supplied"],
                       None, None, None, open_exposure_dollars, as_of, None)
    try:
        j = json.loads(raw)
        assert isinstance(j, dict)
    except (ValueError, AssertionError):
        return _result(INVALID, ["bankroll context is not a JSON object"], None, None, src, open_exposure_dollars, as_of, None)
    if j.get("valueType") != VALUE_TYPE:
        return _result(INVALID, [f"valueType is {j.get('valueType')!r}, not {VALUE_TYPE}: only AVAILABLE CASH may authorize stakes"], None, None, src, open_exposure_dollars, as_of, None)
    try:
        cash = float(j.get("bankroll"))
    except (TypeError, ValueError):
        return _result(INVALID, ["available cash is not a number"], None, None, src, open_exposure_dollars, as_of, None)
    at = _ts(j.get("observedAt"))
    if cash < 0 or cash != cash:
        return _result(INVALID, ["available cash is negative or not finite"], None, at, src, open_exposure_dollars, as_of, None)
    if at is None:
        return _result(INVALID, ["the balance carries no readable observedAt; an undated balance is not evidence about now"], cash, None, src, open_exposure_dollars, as_of, None)
    age = (as_of - at).total_seconds() / 3600.0
    if age < -0.1:
        return _result(INVALID, ["the balance is dated in the future"], cash, at, src, open_exposure_dollars, as_of, age)
    if age > max_age_hours:
        return _result(STALE, [f"the balance is {age * 60:.0f} min old (limit {max_age_hours * 60:.0f} min)"], cash, at, src, open_exposure_dollars, as_of, age)
    return _result(OK, [], cash, at, src, open_exposure_dollars, as_of, age)


def _result(state, reasons, cash, at, src, exposure, as_of, age) -> dict:
    total = None if (cash is None or state != OK) else round(cash + (exposure or 0.0), 2)
    return {"version": BANKROLL_VERSION, "state": state, "reasons": reasons, "available_cash": cash if state == OK else None,
            "balance_as_of": at.isoformat() if at else None, "age_hours": None if age is None else round(age, 2), "source": src,
            "open_exposure_at_cost": None if exposure is None else round(exposure, 2),
            "total_bankroll_estimate": total,
            "total_bankroll_basis": "ESTIMATE = available cash + unsettled owner positions at cost; not read from the venue" if total is not None else None,
            "authorizes_stakes": state == OK}


def stake_gate(bankroll: dict, line_dollars: list) -> dict:
    """Which lines (in priority order) fit in available cash. Lines are dollars in the order the card lists them; the first that does not fit and every one
    after it is refused -- the card never silently rescales a stake."""
    if not bankroll.get("authorizes_stakes"):
        return {"authorized": [False] * len(line_dollars), "reason": "NO STAKE AUTHORIZATION: " + "; ".join(bankroll.get("reasons") or ["bankroll evidence unavailable"])}
    cash = float(bankroll["available_cash"])
    spent, out = 0.0, []
    for d in line_dollars:
        ok = spent + d <= cash + 1e-9
        out.append(ok)
        if ok:
            spent += d
    return {"authorized": out, "committed_dollars": round(spent, 2),
            "reason": None if all(out) else "available cash does not cover every line; lines after the first that does not fit are not authorized"}


def public_view(bankroll: dict, line_dollars: list | None = None) -> dict:
    """Nothing in here is an amount."""
    g = stake_gate(bankroll, line_dollars or []) if line_dollars else None
    return {"state": bankroll["state"], "authorizes_stakes": bankroll["authorizes_stakes"], "source": bankroll.get("source"),
            "age_hours": bankroll.get("age_hours"), "reasons": bankroll.get("reasons"),
            "slate_covered_by_available_cash": None if g is None else all(g["authorized"])}
