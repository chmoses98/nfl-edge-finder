"""FIELD-BY-FIELD COVERAGE: what we actually know, per field, without a headline hiding it.

A single "99% of player context is known" number is worse than no number, because the fields that matter least
are the ones most likely to be present. This module reports every context field separately as KNOWN / UNKNOWN /
NOT_APPLICABLE, and refuses two specific ways of flattering the result:

    A STATE IS NOT A VALUE.  `injury_state = NOT_LISTED` is a perfectly correct answer -- the player is not on
    this week's report -- but it is not knowledge OF an injury status, and counting it as "known" turns an
    unpublished injury report into 100% coverage. Fields with that shape are reported three ways: the state is
    known, the value is present, and the gap between them is named.

    NOT_APPLICABLE IS NOT KNOWN.  Wind speed in a closed dome is not missing data and must not be counted as
    missing; nor may it be counted as known. It is NOT_APPLICABLE, and the denominator shrinks accordingly.

Each field declares how to read it, so the rules live next to the field rather than inside a caller.

Version: coverage-1.0.0.
"""
from __future__ import annotations

COVERAGE_VERSION = "coverage-1.0.0"
KNOWN, UNKNOWN, NOT_APPLICABLE = "KNOWN", "UNKNOWN", "NOT_APPLICABLE"
MISSING_VALUES = (None, "", "UNKNOWN", "NONE")


def _present(v):
    if v in MISSING_VALUES:
        return False
    if isinstance(v, float) and v != v:               # NaN
        return False
    return True


class Field:
    """One context field and how to read its absence.

    `block` is the record sub-dict it lives in; `na_when` marks the rows where the field cannot apply (a dome
    has no wind); `state_of` names a companion field whose value makes this one legitimately empty, so a
    published-but-empty report is separated from an unpublished one.
    """

    def __init__(self, name, block, key, *, na_when=None, state_of=None, empty_states=(), note=None):
        self.name, self.block, self.key = name, block, key
        self.na_when, self.state_of, self.empty_states, self.note = na_when, state_of, tuple(empty_states), note

    def classify(self, rec: dict) -> str:
        b = rec.get(self.block) or {}
        if self.na_when and self.na_when(rec, b):
            return NOT_APPLICABLE
        if _present(b.get(self.key)):
            return KNOWN
        if self.state_of and b.get(self.state_of) in self.empty_states:
            return NOT_APPLICABLE                      # legitimately empty: the state itself is the information
        return UNKNOWN


def _dome(rec, b):
    roof = (rec.get("game_context") or {}).get("roof") or b.get("roof")
    return str(roof or "").lower() in ("dome", "closed", "indoors", "indoor")


# The player-context fields Part O of the mission names, in its order, plus the ones v2 added this round.
PLAYER_FIELDS = [
    Field("injury_state", "player_context", "injury_state", note="LISTED / NOT_LISTED / UNKNOWN"),
    Field("injury_report_status", "player_context", "report_status", state_of="injury_state", empty_states=("NOT_LISTED",),
          note="NOT_APPLICABLE when the player is not on this week's report at all"),
    Field("practice_state", "player_context", "practice_status", state_of="injury_state", empty_states=("NOT_LISTED",)),
    Field("official_inactive_state", "player_context", "official_inactive_state",
          note="only ever INACTIVE_CONFIRMED or UNKNOWN; absence from the list is never evidence of activity"),
    Field("depth_chart", "player_context", "depth_chart_rank"),
    Field("qb_identity", "player_context", "qb_schedule"),
    Field("teammate_availability", "player_context", "teammates_out_or_doubtful"),
    Field("snap_estimate", "player_context", "snap_share"),
    Field("route_estimate", "player_context", "route_participation"),
    Field("target_share", "player_context", "target_share"),
    Field("carry_share", "player_context", "carry_share"),
    Field("red_zone_usage", "player_context", "red_zone_target_share"),
    Field("goal_line_usage", "player_context", "inside_5_carry_share"),
    Field("team_volume", "player_context", "team_pass_attempts"),
    Field("weather_state", "player_context", "weather_state"),
    Field("weather_wind", "player_context", "wind_mph", na_when=_dome),
    Field("weather_temperature", "player_context", "temperature_f", na_when=_dome),
    Field("market_ladder_state", "market_state", "ladder"),
    Field("trade_recency", "market_state", "last_trade_at"),
    Field("availability_state", "player_context", "availability_state"),
]

EXECUTION_FIELDS = [
    Field("yes_ask", "__root__", "yes_ask"),
    Field("no_ask", "__root__", "no_ask"),
    Field("yes_bid", "__root__", "yes_bid"),
    Field("no_bid", "__root__", "no_bid"),
    Field("quote_width", "__root__", "quote_width"),
    Field("volume", "__root__", "volume"),
    Field("open_interest", "__root__", "open_interest"),
    Field("top_level_quantity", "depth", "top_size"),
    Field("book_depth", "depth", "levels"),
    Field("size_adjusted_execution", "depth", "vwap10"),
    Field("trade_recency", "market_state", "last_trade_at"),
]


def _get_block(rec, name):
    return rec if name == "__root__" else (rec.get(name) or {})


def audit(records, fields=None, *, label: str = "player_context") -> dict:
    """Per-field KNOWN / UNKNOWN / NOT_APPLICABLE over a set of records."""
    fields = fields or PLAYER_FIELDS
    rows = []
    for f in fields:
        counts = {KNOWN: 0, UNKNOWN: 0, NOT_APPLICABLE: 0}
        for rec in records:
            b = _get_block(rec, f.block)
            if f.na_when and f.na_when(rec, b):
                counts[NOT_APPLICABLE] += 1
                continue
            if _present(b.get(f.key)):
                counts[KNOWN] += 1
            elif f.state_of and b.get(f.state_of) in f.empty_states:
                counts[NOT_APPLICABLE] += 1
            else:
                counts[UNKNOWN] += 1
        applicable = counts[KNOWN] + counts[UNKNOWN]
        rows.append({"field": f.name, **counts, "applicable": applicable,
                     "known_pct": round(100.0 * counts[KNOWN] / applicable, 1) if applicable else None,
                     "note": f.note})
    worst = sorted((r for r in rows if r["known_pct"] is not None), key=lambda r: r["known_pct"])[:5]
    return {"coverage_version": COVERAGE_VERSION, "label": label, "n_records": len(records), "fields": rows,
            "weakest_fields": [{"field": r["field"], "known_pct": r["known_pct"]} for r in worst],
            "fields_below_50_pct": sorted(r["field"] for r in rows if (r["known_pct"] or 100) < 50)}


def state_breakdown(records, block: str, key: str) -> dict:
    out = {}
    for rec in records:
        v = _get_block(rec, block).get(key)
        out[str(v)] = out.get(str(v), 0) + 1
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


def depth_coverage(records, *, band_key="disagreement_band") -> dict:
    """Depth coverage overall AND by disagreement band, so any selection effect is visible, not assumed away.

    The capture priority deliberately ignores the model's own view, but that is a claim, and a claim about
    selection bias should be measurable rather than asserted. If depth coverage varies strongly across
    disagreement bands, the depth-conditional research is compromised and this is where it shows.
    """
    by_state, by_reason, by_band = {}, {}, {}
    for rec in records:
        d = rec.get("depth") or {}
        st = d.get("state") or "NONE"
        by_state[st] = by_state.get(st, 0) + 1
        if st == "DEPTH_NOT_CAPTURED":
            by_reason[d.get("why") or "UNKNOWN"] = by_reason.get(d.get("why") or "UNKNOWN", 0) + 1
        band = rec.get(band_key) or _band(rec)
        b = by_band.setdefault(band, {"n": 0, "captured": 0})
        b["n"] += 1
        if st in ("DEPTH_CAPTURED", "DEPTH_STALE"):
            b["captured"] += 1
    for b in by_band.values():
        b["captured_pct"] = round(100.0 * b["captured"] / b["n"], 1) if b["n"] else None
    n = len(records)
    cap = by_state.get("DEPTH_CAPTURED", 0) + by_state.get("DEPTH_STALE", 0)
    return {"coverage_version": COVERAGE_VERSION, "n_records": n, "captured": cap,
            "captured_pct": round(100.0 * cap / n, 1) if n else None, "by_state": by_state,
            "not_captured_reasons": by_reason, "by_disagreement_band": dict(sorted(by_band.items())),
            "selection_check": "depth coverage by disagreement band; a strong gradient would mean the depth "
                               "sample is selected by the quantity under study"}


def _band(rec):
    cv, mid = rec.get("contract_value"), rec.get("mid")
    if cv is None or mid is None:
        return "NO_VIEW"
    d = abs(cv - mid) * 100.0
    for lim, name in ((0.5, "0-0.5pp"), (1, "0.5-1pp"), (2, "1-2pp"), (3, "2-3pp"), (5, "3-5pp"), (10, "5-10pp")):
        if d <= lim:
            return name
    return ">10pp"
