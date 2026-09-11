"""UNIVERSAL CLV: how the market moved between a frozen horizon observation and the canonical close, per concept.

SIGN CONVENTION (the only one; pinned by tests/test_clv_v2.py; stated in every report):

    POSITIVE CLV = the market subsequently moved TOWARD the side the frozen model would have bought.

The side is decided ONLY from information frozen at the horizon: model contract value vs the horizon midpoint.
If the model preferred YES, CLV is measured on YES prices (a rising YES price is positive); if it preferred NO,
CLV is measured on NO prices (a rising NO price is positive). If the model held no view (|cv - mid| <= NO_VIEW_TOL)
every "toward the model" quantity is None and the raw moves are still recorded.

Concepts, each kept separately (none is "the" CLV):

    A  move_yes_mid        close_yes_mid  - horizon_yes_mid        raw, signed by YES
    B  move_no_mid         close_no_mid   - horizon_no_mid         raw, signed by NO
    C  move_yes_ask        close_yes_ask  - horizon_yes_ask        executable YES side
    D  move_no_ask         close_no_ask   - horizon_no_ask         executable NO side
    E  model_to_close      model_cv       - close_yes_mid          was the model ahead of the eventual consensus (YES units)
    F  entry_to_close      close mid of the model's side - horizon ASK of the model's side (what a taker paid vs where it closed)
    G  fee-aware entry     entry ask, entry fee per contract (committed schedule, applied once), break-even = ask + fee,
                           close executable price (the ask of the same side at the close) and close mid, all preserved

clv_mid_toward_model  = move of the model's side's MID, signed so positive = toward the model (research quantity)
clv_exec_toward_model = F above (economic quantity; still pre-fee)
clv_net_of_fee        = F minus the entry fee per contract (economic, fee once, no slippage model)

CLV IS NOT PROFIT. It is an intermediate signal about who moved toward whom; profitability needs calibration,
execution, fees, liquidity, sample and prospective validation (docs/SHADOW_V2.md §CLV).
"""
from __future__ import annotations

CLV_VERSION = "clv-2.0.0"
SIGN_CONVENTION = "POSITIVE = the market subsequently moved toward the side the frozen model would have bought"
NO_VIEW_TOL = 1e-9
YES, NO, NO_VIEW = "YES", "NO", "NO_VIEW"


def _f(x):
    try:
        return None if x is None else float(x)
    except (TypeError, ValueError):
        return None


def _sub(a, b):
    return None if (a is None or b is None) else a - b


def model_side(contract_value, horizon_yes_mid, tol: float = NO_VIEW_TOL) -> str:
    cv, m = _f(contract_value), _f(horizon_yes_mid)
    if cv is None or m is None:
        return NO_VIEW
    d = cv - m
    if abs(d) <= tol:
        return NO_VIEW
    return YES if d > 0 else NO


def entry_fee_per_contract(schedule, price, series_ticker, as_of) -> dict:
    """Taker entry fee per contract at `price` through the committed schedule; UNKNOWN never becomes zero."""
    if schedule is None or price is None or not (0.0 < price < 1.0):
        return {"fee": None, "state": "UNKNOWN", "reason": "no schedule or no executable price"}
    try:
        from nfl_edge.execution import fees as F
        q = F.net_executable_ev(price, price, 1.0, schedule, series_ticker=series_ticker, as_of=as_of)
        if not q.is_known:
            return {"fee": None, "state": q.state, "reason": q.reason}
        return {"fee": -float(q.net_ev_dollars), "state": "KNOWN", "reason": None}
    except Exception as e:  # noqa: BLE001
        return {"fee": None, "state": "UNKNOWN", "reason": str(e)[:120]}


def clv_record(proj: dict, close: dict | None, *, schedule=None, as_of=None) -> dict:
    """proj: a projection record (horizon market + model); close: a close record from close.py (or None)."""
    h_yb, h_ya, h_nb, h_na = _f(proj.get("yes_bid")), _f(proj.get("yes_ask")), _f(proj.get("no_bid")), _f(proj.get("no_ask"))
    h_mid = (h_yb + h_ya) / 2.0 if (h_yb is not None and h_ya is not None) else None
    h_no_mid = (h_nb + h_na) / 2.0 if (h_nb is not None and h_na is not None) else None
    cv = _f(proj.get("contract_value"))
    side = model_side(cv, h_mid)
    out = {"clv_version": CLV_VERSION, "sign_convention": SIGN_CONVENTION, "record_id": proj.get("record_id"), "ticker": proj.get("ticker"),
           "model_arm": proj.get("model_arm"), "horizon_label": proj.get("horizon_label"), "model_side": side,
           "horizon_yes_mid": h_mid, "horizon_no_mid": h_no_mid, "horizon_yes_ask": h_ya, "horizon_no_ask": h_na, "model_contract_value": cv,
           "disagreement_pp": (None if (cv is None or h_mid is None) else 100.0 * (cv - h_mid)),
           "clv_status": None, "close_id": None, "close_quality": None, "close_age_seconds": None}
    if not close or close.get("close_status") not in ("CLOSE_OK", "CLOSE_ONE_SIDED"):
        out.update(clv_status="CLV_CLOSE_MISSING", close_reason=(close or {}).get("close_reason"), close_quality=(close or {}).get("close_quality", "MISSING"))
        return out
    c_yb, c_ya, c_nb, c_na = _f(close.get("yes_bid")), _f(close.get("yes_ask")), _f(close.get("no_bid")), _f(close.get("no_ask"))
    c_mid, c_no_mid = _f(close.get("mid")), _f(close.get("no_mid"))
    out.update(close_id=close.get("close_id"), close_quality=close.get("close_quality"), close_age_seconds=close.get("close_age_seconds"),
               close_yes_mid=c_mid, close_no_mid=c_no_mid, close_yes_ask=c_ya, close_no_ask=c_na, close_yes_bid=c_yb, close_no_bid=c_nb,
               # A-D raw moves
               move_yes_mid=_sub(c_mid, h_mid), move_no_mid=_sub(c_no_mid, h_no_mid), move_yes_ask=_sub(c_ya, h_ya), move_no_ask=_sub(c_na, h_na),
               # E
               model_to_close=_sub(cv, c_mid), model_to_horizon=_sub(cv, h_mid),
               model_closer_than_horizon=(None if (cv is None or c_mid is None or h_mid is None) else abs(cv - c_mid) < abs(h_mid - c_mid) - 1e-12))
    # F/G on the model's side, signed toward the model
    if side == NO_VIEW:
        out.update(clv_status="NO_VIEW", clv_mid_toward_model=None, clv_exec_toward_model=None, clv_net_of_fee=None, movement="no_view")
        return out
    if side == YES:
        entry_ask, close_mid_side, close_ask_side, h_mid_side = h_ya, c_mid, c_ya, h_mid
    else:
        entry_ask, close_mid_side, close_ask_side, h_mid_side = h_na, c_no_mid, c_na, h_no_mid
    mid_move = _sub(close_mid_side, h_mid_side)
    out["clv_mid_toward_model"] = mid_move
    out["movement"] = "unchanged" if mid_move is None or abs(mid_move) <= NO_VIEW_TOL else ("toward" if mid_move > 0 else "away")
    out["entry_executable_price"] = entry_ask
    out["clv_exec_toward_model"] = _sub(close_mid_side, entry_ask)
    out["close_executable_price_same_side"] = close_ask_side
    fee = entry_fee_per_contract(schedule, entry_ask, proj.get("series_ticker"), as_of)
    out["entry_fee_per_contract"] = fee["fee"]; out["entry_fee_state"] = fee["state"]
    out["entry_break_even"] = (entry_ask + fee["fee"]) if (entry_ask is not None and fee["fee"] is not None) else None
    out["clv_net_of_fee"] = (out["clv_exec_toward_model"] - fee["fee"]) if (out["clv_exec_toward_model"] is not None and fee["fee"] is not None) else None
    out["clv_status"] = "CLV_OK" if (entry_ask is not None and close_mid_side is not None) else "CLV_SIDE_UNPRICED"
    return out


def summarize(records: list) -> dict:
    """Descriptive summary of CLV records (mean / median / positive rate / n), by the fields the caller grouped on."""
    vals = [r["clv_mid_toward_model"] for r in records if r.get("clv_status") == "CLV_OK" and r.get("clv_mid_toward_model") is not None]
    ex = [r["clv_exec_toward_model"] for r in records if r.get("clv_status") == "CLV_OK" and r.get("clv_exec_toward_model") is not None]
    net = [r["clv_net_of_fee"] for r in records if r.get("clv_status") == "CLV_OK" and r.get("clv_net_of_fee") is not None]
    def stats(xs):
        if not xs:
            return {"n": 0}
        s = sorted(xs)
        return {"n": len(xs), "mean": sum(xs) / len(xs), "median": s[len(s) // 2], "positive_rate": sum(1 for x in xs if x > 0) / len(xs),
                "p10": s[int(0.1 * (len(s) - 1))], "p90": s[int(0.9 * (len(s) - 1))]}
    return {"sign_convention": SIGN_CONVENTION, "n_records": len(records),
            "n_close_missing": sum(1 for r in records if r.get("clv_status") == "CLV_CLOSE_MISSING"),
            "n_no_view": sum(1 for r in records if r.get("clv_status") == "NO_VIEW"),
            "mid_toward_model": stats(vals), "exec_toward_model": stats(ex), "net_of_fee": stats(net),
            "movement": {k: sum(1 for r in records if r.get("movement") == k) for k in ("toward", "away", "unchanged", "no_view")}}
