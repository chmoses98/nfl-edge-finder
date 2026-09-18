"""The player crosswalk must build on a clean runner, or fail saying exactly which input is missing.

The first manual Shadow v2 settlement run died in its fetch step with polars' bare
`ValueError: cannot concat empty list`. The workflow downloaded players and ff_playerids but not `rosters`,
so `build_player_crosswalk` scanned data/raw/nflverse/rosters/roster_<season>.parquet, found nothing, and
handed an empty list to `pl.concat`. The message named neither the missing release nor the fetch flag, and
read like a settlement bug in the game being settled.

Two guards, at the two layers that each let it through:
  * ids.py raises RosterSourceMissing (a FileNotFoundError) naming the expected path and the download
    command, and never the generic concat error; and
  * every workflow that runs ids.py must download `rosters` (tests/test_workflows_parse.py).

The crosswalk is exercised here on synthetic nflverse-shaped files, so the tests need no network and no
gitignored data, and so the behaviour WITH rosters (source priority, provenance, conflict flags) is pinned
as well: hardening the bootstrap must not change what the crosswalk says.
"""
import csv
import os

import polars as pl
import pytest

from nfl_edge.data import ids


# ---------------------------------------------------------------------------------------------------------
# Synthetic nflverse download root
# ---------------------------------------------------------------------------------------------------------

PLAYERS = [
    # gsis, display, first, last, football, pos, group, birth, ht, wt, rookie, last, team, status, dy, dr, dp, college, esb, nfl, pfr, pff, otc, espn, smart
    ("00-0000001", "Josh Allen", "Josh", "Allen", "Josh", "QB", "QB", "1996-05-21", 77, 237, 2018, 2026, "BUF", "ACT",
     2018, 1, 7, "Wyoming", "ALL000001", "nfl-1", "AlleJo02", "pff-1", "otc-1", "espn-1", "smart-1"),
    ("00-0000002", "Amon-Ra St. Brown", "Amon-Ra", "St. Brown", "Amon-Ra", "WR", "WR", "1999-10-24", 72, 202, 2021, 2026,
     "DET", "ACT", 2021, 4, 112, "USC", "STB000002", "nfl-2", None, None, "otc-2", None, "smart-2"),
    ("00-0000003", "Retired Guy Jr.", "Retired", "Guy", "Retired", "RB", "RB", "1990-01-01", 70, 210, 2012, 2016,
     "DET", "RET", 2012, 3, 80, "Nowhere", "RET000003", "nfl-3", "GuyxRe00", "pff-3", None, "espn-3", None),
    (None, "No Gsis", "No", "Gsis", "No", "K", "SPEC", None, None, None, None, None, None, None,
     None, None, None, None, "NOG000000", None, None, None, None, None, None),
]
PLAYER_COLUMNS = ["gsis_id", "display_name", "first_name", "last_name", "football_name", "position", "position_group",
                  "birth_date", "height", "weight", "rookie_season", "last_season", "latest_team", "status",
                  "draft_year", "draft_round", "draft_pick", "college_name", "esb_id", "nfl_id", "pfr_id", "pff_id",
                  "otc_id", "espn_id", "smart_id"]

ROSTERS = {
    2025: [
        # season, gsis, espn, sportradar, yahoo, rotowire, pff, pfr, fantasy_data, sleeper, jersey, team
        (2025, "00-0000001", "espn-1", "sr-1", "y-1", "rw-1", "pff-1", "AlleJo02", "fd-1", "sl-1", 17, "BUF"),
        (2025, "00-0000002", "espn-2-old", "sr-2", "y-2", "rw-2", "pff-2", "StBrAm00", "fd-2", "sl-2", 14, "DET"),
        (2025, None, "espn-x", None, None, None, None, None, None, None, 99, "DET"),
    ],
    2026: [
        (2026, "00-0000001", "espn-1", "sr-1", "y-1", "rw-1", "pff-1", "AlleJo02", "fd-1", "sl-1", 17, "BUF"),
        (2026, "00-0000002", "espn-2", "sr-2", "y-2", "rw-2", "pff-2", "StBrAm00", "fd-2", "sl-2", 14, "DET"),
    ],
}

DP_COLUMNS = ["gsis_id", "mfl_id", "sportradar_id", "fantasypros_id", "pff_id", "sleeper_id", "nfl_id", "espn_id",
              "yahoo_id", "cbs_id", "pfr_id", "cfbref_id", "rotowire_id", "rotoworld_id", "ktc_id", "fantasy_data_id",
              "merge_name"]
DP_ROWS = [
    {"gsis_id": "00-0000001", "mfl_id": "mfl-1", "sportradar_id": "sr-1-dp", "pff_id": "pff-1", "sleeper_id": "sl-1",
     "espn_id": "espn-1", "pfr_id": "AlleJo02", "rotowire_id": "rw-1-dp", "merge_name": "josh allen"},
    {"gsis_id": "00-0000003", "mfl_id": "mfl-3", "sleeper_id": "sl-3-dp", "sportradar_id": "sr-3-dp",
     "pfr_id": "GuyxRe00", "merge_name": "retired guy"},
    {"gsis_id": "", "mfl_id": "mfl-orphan", "merge_name": "orphan"},
]


def _write_players(raw: str) -> None:
    os.makedirs(os.path.join(raw, "players"), exist_ok=True)
    pl.DataFrame([dict(zip(PLAYER_COLUMNS, row)) for row in PLAYERS], schema={
        **{c: pl.Utf8 for c in PLAYER_COLUMNS},
        "height": pl.Int64, "weight": pl.Int64, "rookie_season": pl.Int64, "last_season": pl.Int64,
        "draft_year": pl.Int64, "draft_round": pl.Int64, "draft_pick": pl.Int64,
    }).write_parquet(os.path.join(raw, "players", "players.parquet"))


def _write_rosters(raw: str, seasons) -> None:
    os.makedirs(os.path.join(raw, "rosters"), exist_ok=True)
    for s in seasons:
        pl.DataFrame([dict(zip(ids.ROSTER_COLUMNS, row)) for row in ROSTERS[s]], schema={
            **{c: pl.Utf8 for c in ids.ROSTER_COLUMNS}, "season": pl.Int64, "jersey_number": pl.Int64,
        }).write_parquet(os.path.join(raw, "rosters", f"roster_{s}.parquet"))


def _write_ff_playerids(raw: str) -> None:
    os.makedirs(os.path.join(raw, "ff_playerids"), exist_ok=True)
    with open(os.path.join(raw, "ff_playerids", "db_playerids.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=DP_COLUMNS)
        w.writeheader()
        for row in DP_ROWS:
            w.writerow({c: row.get(c, "") for c in DP_COLUMNS})


@pytest.fixture
def clean_runner(tmp_path):
    """What shadow-v2-settle.yml's fetch step leaves on a fresh runner once it downloads rosters for 2025-2026."""
    raw = str(tmp_path / "nflverse")
    _write_players(raw)
    _write_rosters(raw, [2025, 2026])
    _write_ff_playerids(raw)
    return raw


@pytest.fixture
def runner_without_rosters(tmp_path):
    """The failed run: players and ff_playerids present, the rosters release never fetched."""
    raw = str(tmp_path / "nflverse")
    _write_players(raw)
    _write_ff_playerids(raw)
    return raw


# ---------------------------------------------------------------------------------------------------------
# A clean runner with the rosters release builds the crosswalk
# ---------------------------------------------------------------------------------------------------------

def test_a_clean_runner_with_2025_and_2026_rosters_builds_the_crosswalk(clean_runner):
    x = ids.build_player_crosswalk(clean_runner)
    assert x["gsis_id"].to_list() == ["00-0000001", "00-0000002", "00-0000003"], "one row per GSIS id, no null ids"
    assert ids.roster_files(clean_runner) == [os.path.join(clean_runner, "rosters", f"roster_{s}.parquet")
                                              for s in (2025, 2026)]
    # the settlement path (nflverse_results.pfr_to_gsis) reads exactly these two columns
    assert dict(zip(x["pfr_id"].to_list(), x["gsis_id"].to_list())) == {
        "AlleJo02": "00-0000001", "StBrAm00": "00-0000002", "GuyxRe00": "00-0000003"}


def test_the_latest_roster_season_wins_for_roster_attributes(clean_runner):
    x = ids.build_player_crosswalk(clean_runner).filter(pl.col("gsis_id") == "00-0000002").row(0, named=True)
    assert x["season_roster"] == 2026
    assert x["espn_id_roster"] == "espn-2", "2025 said espn-2-old; the 2026 row is the latest and must win"
    assert x["jersey_number_roster"] == 14 and x["team_roster"] == "DET"


def test_roster_rows_without_a_gsis_id_are_dropped(clean_runner):
    x = ids.build_player_crosswalk(clean_runner)
    assert x.filter(pl.col("gsis_id").is_null()).height == 0
    assert "espn-x" not in x["espn_id"].to_list()


# ---------------------------------------------------------------------------------------------------------
# An empty roster source fails clearly, never as `pl.concat([])`
# ---------------------------------------------------------------------------------------------------------

def test_a_missing_rosters_directory_raises_a_purpose_built_error(runner_without_rosters):
    with pytest.raises(ids.RosterSourceMissing) as exc:
        ids.build_player_crosswalk(runner_without_rosters)
    msg = str(exc.value)
    assert "cannot concat empty list" not in msg
    assert os.path.join(runner_without_rosters, "rosters") in msg, "the error must name the expected path"
    assert "roster_<season>.parquet" in msg
    assert "--only rosters" in msg, "the error must say how to fetch the missing release"
    assert "does not exist" in msg


def test_an_empty_rosters_directory_raises_the_same_error(runner_without_rosters):
    os.makedirs(os.path.join(runner_without_rosters, "rosters"))
    with pytest.raises(ids.RosterSourceMissing, match="exists but is empty"):
        ids.build_player_crosswalk(runner_without_rosters)


def test_a_roster_file_outside_the_scanned_seasons_does_not_count(runner_without_rosters):
    """roster_2015.parquet is not in ROSTER_SEASONS; the scan must say so rather than find nothing and crash."""
    os.makedirs(os.path.join(runner_without_rosters, "rosters"))
    open(os.path.join(runner_without_rosters, "rosters", "roster_2015.parquet"), "wb").close()
    with pytest.raises(ids.RosterSourceMissing, match="2016-2026"):
        ids.build_player_crosswalk(runner_without_rosters)


def test_the_roster_error_is_a_filenotfounderror_so_the_workflow_step_exits_nonzero():
    """The fetch step pipes ids.py into tail under pipefail; an exception must be an exception, not a warning."""
    assert issubclass(ids.RosterSourceMissing, FileNotFoundError)


def test_the_generic_concat_error_cannot_be_reached_from_an_empty_roster_scan(runner_without_rosters):
    """Whatever the exception type, it is never polars' message: that is the regression."""
    try:
        ids.build_player_crosswalk(runner_without_rosters)
    except ValueError as exc:                                 # RosterSourceMissing is not a ValueError
        pytest.fail(f"empty roster scan leaked a generic ValueError: {exc}")
    except ids.RosterSourceMissing:
        pass


def test_a_missing_players_file_is_still_reported_as_a_missing_file(tmp_path):
    """Roster hardening must not mask the sibling input: with rosters present and players absent, the
    failure names players.parquet, exactly as before."""
    raw = str(tmp_path / "nflverse")
    _write_rosters(raw, [2026])
    _write_ff_playerids(raw)
    with pytest.raises(Exception) as exc:
        ids.build_player_crosswalk(raw)
    assert not isinstance(exc.value, ids.RosterSourceMissing)
    assert "players.parquet" in str(exc.value)


# ---------------------------------------------------------------------------------------------------------
# With roster data present, identity resolution is unchanged
# ---------------------------------------------------------------------------------------------------------

def test_source_priority_and_provenance_are_unchanged(clean_runner):
    """players.parquet beats the roster, which beats dynastyprocess; the `_src` column says which won."""
    x = ids.build_player_crosswalk(clean_runner)
    allen = x.filter(pl.col("gsis_id") == "00-0000001").row(0, named=True)
    brown = x.filter(pl.col("gsis_id") == "00-0000002").row(0, named=True)
    guy = x.filter(pl.col("gsis_id") == "00-0000003").row(0, named=True)
    # players first
    assert (allen["espn_id"], allen["espn_id_src"]) == ("espn-1", "espn_id_players")
    assert (allen["pfr_id"], allen["pfr_id_src"]) == ("AlleJo02", "pfr_id_players")
    # roster before dynastyprocess
    assert (allen["sportradar_id"], allen["sportradar_id_src"]) == ("sr-1", "sportradar_id_roster")
    assert (allen["rotowire_id"], allen["rotowire_id_src"]) == ("rw-1", "rotowire_id_roster")
    assert (brown["espn_id"], brown["espn_id_src"]) == ("espn-2", "espn_id_roster")
    assert (brown["pfr_id"], brown["pfr_id_src"]) == ("StBrAm00", "pfr_id_roster")
    assert (brown["sleeper_id"], brown["sleeper_id_src"]) == ("sl-2", "sleeper_id_roster")
    # dynastyprocess when nothing else has it
    assert (guy["sleeper_id"], guy["sleeper_id_src"]) == ("sl-3-dp", "sleeper_id_dp")
    assert (guy["sportradar_id"], guy["sportradar_id_src"]) == ("sr-3-dp", "sportradar_id_dp")
    assert guy["espn_id"] == "espn-3" and guy["espn_id_src"] == "espn_id_players"
    # nothing anywhere stays null with no provenance
    assert brown["yahoo_id"] == "y-2" and guy["yahoo_id"] is None and guy["yahoo_id_src"] is None


def test_conflict_flags_and_name_keys_are_unchanged(clean_runner):
    x = ids.build_player_crosswalk(clean_runner)
    by = {r["gsis_id"]: r for r in x.to_dicts()}
    assert by["00-0000001"]["espn_id_conflict"] is False and by["00-0000001"]["pfr_id_conflict"] is False
    # the roster disagrees with nobody for St. Brown (players has no espn/pfr), so no conflict is flagged
    assert by["00-0000002"]["espn_id_conflict"] is False and by["00-0000002"]["pfr_id_conflict"] is False
    assert by["00-0000001"]["name_key"] == "josh allen"
    assert by["00-0000002"]["name_key"] == "amonra st brown"
    assert by["00-0000003"]["name_key"] == "retired guy", "suffixes are stripped"


def test_a_real_disagreement_between_players_and_roster_is_flagged(clean_runner):
    """Provenance is the point of the crosswalk: a differing id from two sources must surface, not be coalesced away."""
    f = os.path.join(clean_runner, "rosters", "roster_2026.parquet")
    r = pl.read_parquet(f).with_columns(
        pl.when(pl.col("gsis_id") == "00-0000001").then(pl.lit("espn-1-other")).otherwise(pl.col("espn_id")).alias("espn_id"))
    r.write_parquet(f)
    allen = ids.build_player_crosswalk(clean_runner).filter(pl.col("gsis_id") == "00-0000001").row(0, named=True)
    assert allen["espn_id_conflict"] is True
    assert allen["espn_id"] == "espn-1" and allen["espn_id_src"] == "espn_id_players", "players still wins"


def test_the_default_raw_root_is_the_repo_download_directory():
    """The workflow calls ids.py with no arguments; the default must be the directory nflverse_download.py fills."""
    assert ids.RAW == os.path.join(ids.ROOT, "data", "raw", "nflverse")
    assert ids.build_player_crosswalk.__defaults__ == (ids.RAW,)


def test_dynastyprocess_rows_without_a_gsis_id_are_ignored(clean_runner):
    x = ids.build_player_crosswalk(clean_runner)
    assert "mfl-orphan" not in x["mfl_id_dp"].to_list()
