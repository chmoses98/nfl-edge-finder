"""Role context: the depth chart is read point in time, a player's placement is his best OFFENSIVE one, the order
inside a position group is derived, and role certainty is conservative.

Fixtures are shaped exactly like the two nflverse formats (2025+ ESPN rows with `dt`; <= 2024 weekly rows with
`depth_team`), built in memory -- no network, no parquet on disk.
"""
import os
import sys
from datetime import datetime, timezone

import polars as pl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nfl_edge.context import role as RO                                           # noqa: E402
from nfl_edge.shadow_v2 import context as CX                                      # noqa: E402

T0 = "2026-09-16T06:02:02Z"       # Wednesday chart
T1 = "2026-09-19T06:02:02Z"       # Saturday chart (a promotion happened)
T2 = "2026-09-21T06:02:02Z"       # after the Sunday games -- must never be read by a Saturday cutoff


def espn_rows():
    rows = []

    def add(dt, name, gsis, abb, slot, rank, team="KC"):
        rows.append({"dt": dt, "team": team, "player_name": name, "espn_id": gsis[-4:], "gsis_id": gsis, "pos_grp_id": "x",
                     "pos_grp": "x", "pos_id": "x", "pos_name": abb, "pos_abb": abb, "pos_slot": slot, "pos_rank": rank})
    for dt in (T0, T1, T2):
        add(dt, "QB One", "00-QB1", "QB", 9, 1); add(dt, "QB Two", "00-QB2", "QB", 9, 2)
        # the starting receiver also returns kicks: rows AFTER his WR row, which the old map let overwrite him
        add(dt, "Wide One", "00-WR1", "WR", 1, 1); add(dt, "Wide One", "00-WR1", "KR", 20, 1); add(dt, "Wide One", "00-WR1", "PR", 21, 2)
        add(dt, "Wide Two", "00-WR2", "WR", 2, 2); add(dt, "Slot Guy", "00-WR3", "WR", 8, 3); add(dt, "Wide Four", "00-WR4", "WR", 1, 4)
        add(dt, "Tight End", "00-TE1", "TE", 10, 1)
        add(dt, "Left Tackle", "00-LT", "LT", 5, 1)                 # not a skill position: ignored
        if dt == T0:
            add(dt, "Back One", "00-RB1", "RB", 11, 1); add(dt, "Back Two", "00-RB2", "RB", 11, 2)
        else:                                                        # RB2 promoted on Saturday
            add(dt, "Back Two", "00-RB2", "RB", 11, 1); add(dt, "Back One", "00-RB1", "RB", 11, 2)
        if dt == T2:
            add(dt, "Late Signing", "00-LATE", "WR", 2, 1)            # a post-cutoff fact
    return pl.DataFrame(rows)


def test_the_chart_is_the_newest_at_or_before_the_cutoff_and_never_a_later_one():
    sat = RO.DepthChartBook.from_frame(espn_rows(), datetime(2026, 9, 20, 17, 0, tzinfo=timezone.utc))
    assert sat.vintage["KC"] == T1
    assert sat.entry("00-RB2").group_rank == 1 and sat.entry("00-RB1").group_rank == 2
    assert sat.entry("00-LATE") is None                              # dated after the cutoff
    wed = RO.DepthChartBook.from_frame(espn_rows(), datetime(2026, 9, 17, 0, 0, tzinfo=timezone.utc))
    assert wed.entry("00-RB1").group_rank == 1
    before = RO.DepthChartBook.from_frame(espn_rows(), datetime(2026, 9, 1, tzinfo=timezone.utc))
    assert not before.entries and before.reason


def test_a_kick_returner_keeps_his_offensive_placement():
    b = RO.DepthChartBook.from_frame(espn_rows(), datetime(2026, 9, 20, tzinfo=timezone.utc))
    e = b.entry("00-WR1")
    assert (e.group, e.group_rank, e.pos_abb) == ("WR", 1, "WR")
    assert b.entry("00-LT") is None
    assert b.qb1("KC") == "00-QB1"
    assert [x.gsis_id for x in b.by_team["KC"]["WR"]] == ["00-WR1", "00-WR2", "00-WR3", "00-WR4"]
    assert RO.role_class(b.entry("00-WR3"), "WR") == "WR_SLOT_STARTER"
    assert RO.role_class(b.entry("00-WR2"), "WR") == "WR2"
    assert RO.role_class(b.entry("00-WR4"), "WR") == "WR_ROTATIONAL"


def test_the_legacy_weekly_format_is_read_for_its_own_week():
    rows = []
    for wk, order in ((4, ["00-A", "00-B"]), (5, ["00-B", "00-A"])):
        for i, g in enumerate(order, start=1):
            rows.append({"season": 2024, "club_code": "KC", "week": wk, "game_type": "REG", "depth_team": str(i), "gsis_id": g,
                         "position": "RB", "depth_position": "RB", "full_name": g, "formation": "Offense"})
    b = RO.DepthChartBook.from_frame(pl.DataFrame(rows), None, season=2024, week=4)
    assert b.entry("00-A").group_rank == 1 and b.vintage["KC"] == "2024-W04"
    b5 = RO.DepthChartBook.from_frame(pl.DataFrame(rows), None, season=2024, week=5)
    assert b5.entry("00-B").group_rank == 1


def test_role_certainty_is_conservative():
    b = RO.DepthChartBook.from_frame(espn_rows(), datetime(2026, 9, 20, 17, 0, tzinfo=timezone.utc))
    # chart and usage agree, played for this team this season -> HIGH
    hi = RO.assess(b, gsis_id="00-WR1", team="KC", position="WR", recent_snap_share=0.86, n_current_season_games=1, last_team="KC")
    assert hi["role_certainty"] == RO.HIGH and hi["role_class"] == "WR1" and hi["depth_chart_vintage"] == T1
    # no current-season game yet -> MEDIUM, never HIGH
    assert RO.assess(b, gsis_id="00-WR1", team="KC", position="WR", recent_snap_share=0.86, n_current_season_games=0)["role_certainty"] == RO.MEDIUM
    # a charted starter who has been playing a quarter of the snaps: chart and usage disagree -> LOW
    lo = RO.assess(b, gsis_id="00-RB2", team="KC", position="RB", recent_snap_share=0.25, n_current_season_games=1, last_team="KC")
    assert lo["role_certainty"] == RO.LOW and any("snap share" in r for r in lo["role_reasons"])
    # changed teams -> LOW
    assert RO.assess(b, gsis_id="00-TE1", team="KC", position="TE", recent_snap_share=0.8, n_current_season_games=1,
                     last_team="BUF")["role_certainty"] == RO.LOW
    # a teammate ahead of him is Out: the role is about to change -> LOW, flagged
    ch = RO.assess(b, gsis_id="00-WR2", team="KC", position="WR", recent_snap_share=0.8, n_current_season_games=1, last_team="KC",
                   teammate_status={"00-WR1": "Out"})
    assert ch["role_certainty"] == RO.LOW and ch["role_change_pending"] and ch["blocking_teammates"] == ["00-WR1"]
    # neither a chart nor any usage -> UNKNOWN; usage without a chart -> LOW
    assert RO.assess(b, gsis_id="00-NOBODY", team="KC", position="WR")["role_certainty"] == RO.UNKNOWN
    assert RO.assess(b, gsis_id="00-NOBODY", team="KC", position="WR", recent_snap_share=0.5)["role_certainty"] == RO.LOW


def test_injury_knowledge_counts_mature_absence_and_nothing_weaker():
    assert CX.injury_knowledge("LISTED", "PARTIAL") == CX.INJURY_DESIGNATION_KNOWN
    assert CX.injury_knowledge("NOT_LISTED_AT_THIS_VINTAGE", "MATURE") == CX.INJURY_NO_DESIGNATION
    assert CX.injury_knowledge("NOT_LISTED_AT_THIS_VINTAGE", "PARTIAL") == CX.INJURY_WEAK
    for st in ("REPORT_NOT_AVAILABLE", "SOURCE_UNAVAILABLE", "UNKNOWN", None):
        assert CX.injury_knowledge(st, "MATURE") == CX.INJURY_UNKNOWN


def test_the_context_source_builds_a_role_block_from_the_real_loader(tmp_path):
    root = tmp_path
    p = root / "data" / "raw" / "nflverse" / "depth_charts"
    p.mkdir(parents=True)
    espn_rows().write_parquet(p / "depth_charts_2026.parquet")
    src = CX.ContextSources(str(root), str(root / "md"), 2026, datetime(2026, 9, 20, 17, 0, tzinfo=timezone.utc), log=lambda *a: None)
    assert src.depth["vintage"] == T1 and src.depth["rank"]["00-WR1"] == ("WR", 1)
    dep = src.depth_block("00-WR1", "KC")
    assert dep["state"] == "LISTED" and dep["position"] == "WR" and dep["rank"] == 1 and dep["team_qb1"] == "00-QB1"
    # the slot receiver: ESPN rank 3 in the group, derived group order 3, and his KR row never leaks in
    assert src.depth_block("00-WR3", "KC")["rank"] == 3 and src.depth_block("00-WR3", "KC")["group_rank"] == 3
    role = src.role_block(gsis="00-WR1", team="KC", week=2, position="WR", feat_row={"last_snap_share": 0.9, "n_cur_season": 1,
                                                                                         "last_team": "KC"}, availability_state="EXPECTED_ACTIVE")
    assert role["role_certainty"] == RO.HIGH and role["depth_chart_state"] == "LISTED"
    # the ledger records the vintage it used, so the record can re-check its own compliance later
    assert any(u.name == "depth_charts" and u.vintage is not None for u in src.ledger.uses)
