"""The Kalshi player map is built from EVERY row's schema, not the first hundred rows'.

`build_player_map.main()` ends in one `pl.DataFrame(rows)`. Five of those columns -- `kalshi_team_id`,
`team`, `jersey`, `gsis_id` and `method` -- are None for a player whose markets carried no team token and
whom no roster match resolved. Polars infers dtypes from the first `infer_schema_length` rows (default 100),
so a board whose first hundred players were all unresolved inferred Null for those columns and then refused
the first genuine value:

    ComputeError: could not append value: "8e52cc75-cba8-4373-9b62-b535b53b3be8" of type: str to the
                  builder; ... consider increasing `infer_schema_length`

That is not malformed data -- the identical rows in a different order build fine -- it is an inference
window, and it took down shadow-price, run-nfl-horizons and both shadow-v2 projection jobs at once.

These tests drive the REAL `main()` against a synthetic discovery board whose first 101 players are
unresolved and whose 102nd carries a team UUID and a roster match, with the module's ROOT redirected at a
tmp tree so nothing touches the repo's data/.
"""
import importlib.util
import json
import os
import sys

import polars as pl
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "scripts", "kalshi", "build_player_map.py")

SEASON = 2026
TEAM_UUID = "8e52cc75-cba8-4373-9b62-b535b53b3be8"   # the value production actually choked on
RESOLVED_NAME = "Davante Adams"
RESOLVED_GSIS = "00-0031381"
N_UNRESOLVED = 101                                    # strictly more than the default window of 100


def _load_module():
    spec = importlib.util.spec_from_file_location("build_player_map_under_test", SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _market(i, *, name, team_uuid, suffix):
    """One PLAYER_STAT market, shaped like the anytime-touchdown family the classifier already pins."""
    event = "KXNFLANYTD-26SEP13SEANE"
    cs = {"football_player": f"kalshi-player-{i:04d}"}
    if team_uuid is not None:
        cs["football_team"] = team_uuid
    return {"ticker": f"{event}-{suffix}", "event_ticker": event, "series_ticker": "KXNFLANYTD",
            "title": f"{name}: Anytime Touchdown", "strike_type": "structured", "custom_strike": cs}


def _board():
    """101 players with NO football_team, then one that has one. Order is the whole point."""
    ms = [_market(i, name=f"Unresolved Player{i:03d}", team_uuid=None, suffix=f"NEU{i:03d}")
          for i in range(N_UNRESOLVED)]
    ms.append(_market(N_UNRESOLVED, name=RESOLVED_NAME, team_uuid=TEAM_UUID, suffix="NEDADAMS17"))
    return ms


@pytest.fixture
def tree(tmp_path):
    """A tmp ROOT carrying the two nflverse tables main() reads, plus a discovery dir."""
    for p in ("data/raw/nflverse/rosters", "data/raw/nflverse/players", "data/silver",
              "discovery/markets"):
        os.makedirs(tmp_path / p, exist_ok=True)
    pl.DataFrame({"gsis_id": [RESOLVED_GSIS], "full_name": [RESOLVED_NAME], "team": ["NE"],
                  "jersey_number": [17], "position": ["WR"], "status": ["ACT"]}
                 ).write_parquet(tmp_path / f"data/raw/nflverse/rosters/roster_{SEASON}.parquet")
    pl.DataFrame({"gsis_id": [RESOLVED_GSIS], "display_name": [RESOLVED_NAME], "latest_team": ["NE"],
                  "position": ["WR"], "last_season": [SEASON], "jersey_number": [17]}
                 ).write_parquet(tmp_path / "data/raw/nflverse/players/players.parquet")
    json.dump({"KXNFLANYTD": {"markets": _board()}},
              open(tmp_path / "discovery/markets/board.json", "w"))
    return tmp_path


def _run(tree, monkeypatch):
    mod = _load_module()
    monkeypatch.setattr(mod, "ROOT", str(tree))
    monkeypatch.setattr(sys, "argv", ["build_player_map.py", "--discovery-dir", str(tree / "discovery"),
                                      "--season", str(SEASON)])
    mod.main()
    return pl.read_parquet(tree / "data/silver/kalshi_player_map.parquet")


def test_a_team_uuid_first_appearing_after_row_100_does_not_crash_the_build(tree, monkeypatch):
    """The exact production failure: the 102nd player is the first to carry a team UUID."""
    df = _run(tree, monkeypatch)
    assert df.height == N_UNRESOLVED + 1
    assert df.schema["kalshi_team_id"] == pl.Utf8


def test_the_late_uuid_survives_with_its_value_intact(tree, monkeypatch):
    """A schema fix that dropped or coerced the id would be worse than the crash it replaced."""
    df = _run(tree, monkeypatch)
    carried = df.filter(pl.col("kalshi_team_id").is_not_null())
    assert carried.height == 1
    assert carried["kalshi_team_id"][0] == TEAM_UUID          # byte-for-byte, not normalised
    assert carried["name"][0] == RESOLVED_NAME


def test_the_mapping_semantics_are_unchanged(tree, monkeypatch):
    """Same identity logic: the resolvable player resolves, the other 101 stay UNRESOLVED with a null id."""
    df = _run(tree, monkeypatch)
    hit = df.filter(pl.col("name") == RESOLVED_NAME)
    assert hit["gsis_id"][0] == RESOLVED_GSIS
    assert hit["status"][0] == "RESOLVED"
    assert hit["method"][0] == "name+team"
    assert hit["team"][0] == "NE"
    rest = df.filter(pl.col("name") != RESOLVED_NAME)
    assert rest.height == N_UNRESOLVED
    assert set(rest["status"].to_list()) == {"UNRESOLVED"}
    assert rest["gsis_id"].null_count() == N_UNRESOLVED
    assert rest["kalshi_team_id"].null_count() == N_UNRESOLVED
    # every player is present exactly once, keyed by the Kalshi id -- no row lost to the schema change
    assert df["kalshi_player_id"].n_unique() == N_UNRESOLVED + 1
    assert df["season"].to_list() == [SEASON] * (N_UNRESOLVED + 1)


def test_the_widened_inference_is_load_bearing():
    """Guards the guard.

    If the default window already accepted these rows, the fix would be decoration. It does not: the same
    rows raise under the default and build under `infer_schema_length=None`, and the same rows REORDERED
    build under the default too -- which is what makes this an inference bug and not malformed data.
    """
    rows = ([{"kalshi_player_id": f"p{i}", "kalshi_team_id": None, "name": f"P{i}"} for i in range(101)]
            + [{"kalshi_player_id": "p101", "kalshi_team_id": TEAM_UUID, "name": "P101"}])
    with pytest.raises(Exception, match="could not append value"):
        pl.DataFrame(rows)
    assert pl.DataFrame(rows, infer_schema_length=None)["kalshi_team_id"].drop_nulls().to_list() == [TEAM_UUID]
    assert pl.DataFrame([rows[-1]] + rows[:-1])["kalshi_team_id"].drop_nulls().to_list() == [TEAM_UUID]


def test_the_production_call_site_widens_inference():
    """The fix must live at the call site main() actually uses, not in a helper nothing calls."""
    src = open(SRC).read()
    assert "pl.DataFrame(rows, infer_schema_length=None)" in src
    assert "pl.DataFrame(rows)" not in src
