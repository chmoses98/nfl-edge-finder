"""A research row reduced to the fields the week-level statistics read, in a fixed-slot object.

The research export and the weekly report build the scorecard v3, the coverage health block and the export
summary over EVERY research row of a week. A full research row is a dict of ~150 keys, several kilobytes as
Python objects; a week is a million of them, so holding them is what made the postgame path scale with the
archive. Those statistics read a few dozen scalar fields. `slim()` copies exactly those into a `__slots__`
object that answers `.get()` / `[]` / `in` like the dict did, so `scorecard_v3.build()`, `weekly_report_v2.health()`
and the export summary run UNCHANGED over the slim rows, and a test proves the two agree.

Strings are interned through one small table so the same state label is one object across a million rows.
"""
from __future__ import annotations

from nfl_edge.evaluation import scorecard_v3 as S3

# What scorecard_v3.build / render, weekly_report_v2.health and research_export_v2's summary read off a row.
_SCORECARD = ("settled_yes", "contract_value", "game_id", "ticker", "h_mid", "c_mid", "clv_status",
              "clv_mid_toward_model", "clv_exec_toward_model", "clv_net_of_fee", "movement",
              "model_closer_than_horizon", "exec_pnl_gross", "exec_pnl_net", "h_width", "h_liquidity",
              "evidence_class", "information_skew_seconds", "family_group")
_HEALTH = ("kickoff_utc", "flag_settlement_supported", "settlement_status", "close_status", "close_reason",
           "ctx_depth_chart_rank", "ctx_weather_state", "autopsy_classification", "record_id", "snapshot_id")
_EXPORT = ("depth_pair_state", "depth_pair_reason", "depth_pair_horizon_quality", "depth_pair_age_min")
SLIM_FIELDS = tuple(dict.fromkeys(_SCORECARD + tuple(S3.SEGMENTS) + _HEALTH + _EXPORT))

_MISSING = object()


class SlimRow:
    __slots__ = SLIM_FIELDS

    def get(self, key, default=None):
        v = getattr(self, key, _MISSING) if key in _SLOTS else _MISSING
        return default if v is _MISSING else v

    def __getitem__(self, key):
        if key not in _SLOTS:
            raise KeyError(key)
        return getattr(self, key)

    def __contains__(self, key):
        return key in _SLOTS

    def keys(self):
        return SLIM_FIELDS

    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in SLIM_FIELDS}


_SLOTS = frozenset(SLIM_FIELDS)


class Interner:
    """One object per distinct string value; unbounded in principle, a few hundred entries in practice."""

    def __init__(self):
        self._t: dict = {}

    def __call__(self, v):
        if isinstance(v, str):
            got = self._t.get(v)
            if got is None:
                got = self._t[v] = v
            return got
        return v


def slim(row: dict, intern: Interner | None = None) -> SlimRow:
    s = SlimRow()
    for k in SLIM_FIELDS:
        v = row.get(k)
        setattr(s, k, intern(v) if intern is not None else v)
    return s
