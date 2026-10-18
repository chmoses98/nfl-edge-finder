"""One injury designation per player for the live availability rung (additive fix; research/ is append-only).

Scheduled run 39127871523 (2026-10-18 12:34Z) failed in the project stage with
`IndexError: ... size of axis is 89459 but size of corresponding boolean axis is 89458`. Once the London game's
official inactive list was posted, a player both injury-listed OUT and on the CONFIRMED inactive list got two rows from
`availability.injury_table`; `diagnostics._vacated` left-joins that table onto the player frame, so his player-game was
duplicated (and he would be counted twice in teammates' vacated opportunity).

`apply()` wraps the two live functions so the table handed to the availability rung holds one row per
(season, week, player), keeping the most severe designation. With unique keys (the whole nflverse history: 0 duplicate
keys in 75,303 rows) the tables pass through untouched, so the study's numbers do not change. No file in the
walk-forward state fingerprint is touched, so a saved state stays valid.

Entry point used by the workflow:  python -m nfl.live.main <the same arguments as nfl.live.run>
"""
from __future__ import annotations

import pandas as pd

SEVERITY = {"Out": 4, "Doubtful": 3, "Questionable": 2, "Probable": 1, "Note": 0}
KEYS = ["season", "week", "gsis_id"]


def dedupe(inj: pd.DataFrame) -> pd.DataFrame:
    """Most severe designation per (season, week, player); the same object back when keys are already unique."""
    if inj is None or inj.empty or not inj.duplicated(KEYS).any():
        return inj
    rank = inj.report_status.map(SEVERITY).fillna(-1)
    out = inj.assign(_r=rank).sort_values("_r", ascending=False, kind="stable").drop_duplicates(KEYS)
    return out.drop(columns="_r").sort_index().reset_index(drop=True)


_APPLIED = False


def apply() -> None:
    """Patch nfl.live.availability.injury_table and nfl.live.project._live_inj (idempotent)."""
    global _APPLIED
    if _APPLIED:
        return
    from . import availability as LA
    from . import project as LP

    orig_table, orig_live = LA.injury_table, LP._live_inj

    def injury_table(latest, season, week):
        return dedupe(orig_table(latest, season, week))

    def _live_inj(rows_latest, season, week):
        return dedupe(orig_live(rows_latest, season, week))

    injury_table.__doc__ = (orig_table.__doc__ or "") + "\n    (one row per player: nfl.live.injury_dedupe)"
    LA.injury_table = injury_table
    LP._live_inj = _live_inj
    _APPLIED = True
