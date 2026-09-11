from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from tennis_edge.data import sackmann as sk
from tennis_edge.data import tennis_data as td
from tennis_edge.identity import players as pl
from tests.conftest import FIXTURES


@pytest.fixture(scope="module")
def registry(run_dir: Path) -> pd.DataFrame:
    return pl.load_registry(run_dir / "sackmann" / "tennis_atp" / "atp_players.csv.gz", "ATP")


@pytest.fixture(scope="module")
def sackmann_matches(run_dir: Path) -> pd.DataFrame:
    frames, _ = sk.load_all(run_dir, tours=("ATP",), include=("main", "qual_chall"))
    return frames["matches"]


@pytest.fixture
def td_matches() -> pd.DataFrame:
    df = pd.read_csv(FIXTURES / "tennis_data_atp_2024.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return td.normalize_tennis_data(df, source_file="2024.xlsx.gz", season=2024).matches


# --- registry -----------------------------------------------------------------
def test_registry_columns_and_bad_rows_dropped(registry):
    assert list(registry.columns) == ["tour", *pl.REGISTRY_COLUMNS]
    assert len(registry) == 15  # ids are labels: alphanumeric ids (TML 'D875', fixture 'abc') are valid keys
    assert registry["player_id"].is_unique
    r = registry.set_index("player_id").loc["100001"]
    assert r["name_full"] == "Roger Federer" and r["name_norm"] == "roger federer"
    assert r["last_first_initial"] == "federer r"
    assert r["dob"] == date(1981, 8, 8) and r["ioc"] == "SUI" and r["height"] == 185
    assert r["wikidata_id"] == "Q1426"
    assert registry.set_index("player_id").loc["100013", "last_first_initial"] == "o connell c"
    assert registry.set_index("player_id").loc["100014", "name_norm"] == "felix auger aliassime"
    assert registry.set_index("player_id").loc["100012", "dob"] is None
    assert pd.isna(registry.set_index("player_id").loc["100007", "wikidata_id"])


def test_build_registry_requires_player_id():
    with pytest.raises(ValueError):
        pl.build_registry(pd.DataFrame({"name_first": ["a"]}), "ATP")


def test_alias_table(registry, sackmann_matches):
    aliases = pl.build_alias_table(registry, sackmann_matches)
    assert list(aliases.columns) == pl.ALIAS_COLUMNS
    fed = aliases[aliases["player_id"] == "100001"]
    assert set(fed["alias"]) == {"roger federer", "federer r"}
    assert set(aliases["alias_type"]) <= {"full", "last_initial", "match_name"}
    assert not aliases.duplicated().any()
    # two Kuznetsovs share the 'kuznetsov a' alias -> lookup is ambiguous, never silently resolved
    assert sorted(pl.registry_lookup(registry, aliases, "Kuznetsov A.")) == ["100011", "100012"]
    assert pl.registry_lookup(registry, aliases, "Federer R.") == ["100001"]
    assert pl.registry_lookup(registry, aliases, "Nobody X.") == []
    assert pl.registry_lookup(registry, aliases, None) == []


def test_alias_table_picks_up_match_spellings(registry):
    matches = pd.DataFrame({"winner_id": ["100001"], "winner_name": ["R. Federer"], "loser_id": ["100002"], "loser_name": ["Rafael Nadal"]})
    aliases = pl.build_alias_table(registry, matches)
    extra = aliases[aliases["alias_type"] == "match_name"]
    assert extra["alias"].tolist() == ["r federer"]  # 'rafael nadal' already known as 'full'


# --- scoring helpers ----------------------------------------------------------
def test_tournament_score():
    assert pl.tournament_score("Australian Open", "Melbourne", "Australian Open") == 1.0
    assert pl.tournament_score("BNP Paribas Open", "Indian Wells", "Indian Wells Masters") == 1.0
    assert pl.tournament_score("French Open", "Paris", "Roland Garros") == 1.0        # alias table
    assert pl.tournament_score("Mutua Madrid Open", "Madrid", "Madrid Masters") == 1.0  # location
    assert 0 < pl.tournament_score("Rolex Monte Carlo Masters", "Monte Carlo", "Monte Carlo Masters") <= 1.0
    assert pl.tournament_score("Australian Open", "Melbourne", "Canberra CH") == 0.0
    assert pl.tournament_score("Australian Open", "Melbourne", None) == 0.0


def test_round_score():
    assert pl.round_score(1, None, "R128", 128) == 1.0
    assert pl.round_score(1, None, "R32", 32) == 1.0
    assert pl.round_score(1, None, "R32", 28) == 1.0    # 28 draw with byes still uses R32
    assert pl.round_score(2, None, "R64", 128) == 1.0
    assert pl.round_score(None, 0, "F", 128) == 1.0
    assert pl.round_score(None, 2, "QF", 32) == 1.0
    assert pl.round_score(None, 2, "SF", 32) == 0.5
    assert pl.round_score(None, 0, "R32", 32) == 0.0
    assert pl.round_score(None, -1, "RR", 8) == 1.0
    assert pl.round_score(1, None, "Q1", 128) == 0.5     # unknown Sackmann stage
    assert pl.round_score(None, None, "F", 128) == 0.5   # unknown tennis-data round
    assert pl.round_score(1, None, "R32", None) == 0.5   # draw size unknown


def test_date_score_window():
    cfg = pl.LinkConfig()
    start = date(2024, 1, 15)
    assert pl.date_score(date(2024, 1, 15), start, "GRAND_SLAM", cfg) == 1.0
    assert pl.date_score(date(2024, 1, 28), start, "GRAND_SLAM", cfg) == 1.0
    assert pl.date_score(date(2024, 1, 13), start, "GRAND_SLAM", cfg) == pytest.approx(0.8)
    assert pl.date_score(date(2024, 1, 11), start, "GRAND_SLAM", cfg) is None       # before window
    assert pl.date_score(date(2024, 2, 10), start, "GRAND_SLAM", cfg) is None       # after window
    assert pl.date_score(date(2024, 1, 25), start, "TOUR_500_250", cfg) == pytest.approx(0.8)


# --- linking ------------------------------------------------------------------
def test_link_tennis_data_names(td_matches, sackmann_matches):
    links = pl.link_tennis_data_names(td_matches, sackmann_matches)
    assert list(links.columns) == pl.LINK_COLUMNS
    assert len(links) == len(td_matches)
    by = links.set_index("td_key")
    assert by.loc["TD:ATP:2024:00000", "status"] == pl.MATCHED
    assert by.loc["TD:ATP:2024:00000", "match_key"] == "ATP:2024-580:100"
    assert by.loc["TD:ATP:2024:00000", "confidence"] == 1.0
    assert by.loc["TD:ATP:2024:00000", "winner_id"] == "100001" and by.loc["TD:ATP:2024:00000", "loser_id"] == "100002"
    assert by.loc["TD:ATP:2024:00001", "match_key"] == "ATP:2024-580:102"   # retirement, 2nd round
    assert by.loc["TD:ATP:2024:00002", "match_key"] == "ATP:2024-580:101"
    assert by.loc["TD:ATP:2024:00003", "match_key"] == "ATP:2024-580:103"   # Zverev A. vs Zverev M.
    assert by.loc["TD:ATP:2024:00004", "match_key"] == "ATP:2024-M001:300"  # BNP Paribas Open -> Indian Wells
    assert by.loc["TD:ATP:2024:00004", "status"] == pl.MATCHED
    # Kwon vs "Kuznetsov A." fits both Andrey and Alexey in the same event -> AMBIGUOUS, never auto-accepted
    amb = by.loc["TD:ATP:2024:00005"]
    assert amb["status"] == pl.AMBIGUOUS and amb["n_candidates"] == 2
    assert amb["second_confidence"] >= 0.5 and amb["confidence"] > 0.8
    assert {amb["match_key"], amb["second_match_key"]} == {"ATP:2024-580:1", "ATP:2024-580:2"}
    # Sinner/Alcaraz do not exist in the Sackmann fixture
    un = by.loc["TD:ATP:2024:00006"]
    assert un["status"] == pl.UNMATCHED and un["n_candidates"] == 0 and un["match_key"] is None


def test_two_letter_initial_disambiguates(td_matches, sackmann_matches):
    row = td_matches[td_matches["td_key"] == "TD:ATP:2024:00005"].copy()
    row["loser_name_td"] = "Kuznetsov An."
    links = pl.link_tennis_data_names(row, sackmann_matches)
    r = links.iloc[0]
    assert r["status"] == pl.MATCHED and r["match_key"] == "ATP:2024-580:1"
    # the Canberra QF between the same players is rejected (different event, different round), not a runner-up
    assert r["n_candidates"] == 1 and r["second_match_key"] is None


def test_wrong_initial_is_not_matched(td_matches, sackmann_matches):
    row = td_matches[td_matches["td_key"] == "TD:ATP:2024:00000"].copy()
    row["winner_name_td"] = "Federer X."
    links = pl.link_tennis_data_names(row, sackmann_matches)
    assert links.iloc[0]["status"] == pl.UNMATCHED


def test_same_sackmann_match_claimed_twice_is_demoted(td_matches, sackmann_matches):
    dup = td_matches[td_matches["td_key"] == "TD:ATP:2024:00000"].copy()
    dup["td_key"] = "TD:ATP:2024:99999"
    both = pd.concat([td_matches, dup], ignore_index=True)
    links = pl.link_tennis_data_names(both, sackmann_matches).set_index("td_key")
    assert links.loc["TD:ATP:2024:00000", "status"] == pl.AMBIGUOUS
    assert links.loc["TD:ATP:2024:99999", "status"] == pl.AMBIGUOUS
    assert links.loc["TD:ATP:2024:00001", "status"] == pl.MATCHED


def test_link_thresholds_are_configurable(td_matches, sackmann_matches):
    cfg = pl.LinkConfig(match_threshold=0.99)
    links = pl.link_tennis_data_names(td_matches, sackmann_matches, cfg).set_index("td_key")
    assert links.loc["TD:ATP:2024:00000", "status"] == pl.MATCHED       # confidence exactly 1.0 > 0.99
    cfg2 = pl.LinkConfig(match_threshold=1.0)
    links2 = pl.link_tennis_data_names(td_matches, sackmann_matches, cfg2).set_index("td_key")
    assert links2.loc["TD:ATP:2024:00000", "status"] == pl.AMBIGUOUS


def test_link_empty_inputs(td_matches, sackmann_matches):
    empty = pl.link_tennis_data_names(td_matches.iloc[0:0], sackmann_matches)
    assert len(empty) == 0 and "status" in empty.columns
    none = pl.link_tennis_data_names(td_matches, sackmann_matches.iloc[0:0])
    assert len(none) == len(td_matches)


def test_link_requires_columns(sackmann_matches):
    with pytest.raises(ValueError):
        pl.link_tennis_data_names(pd.DataFrame({"td_key": ["x"]}), sackmann_matches)


def test_link_summary(td_matches, sackmann_matches):
    links = pl.link_tennis_data_names(td_matches, sackmann_matches)
    s = pl.link_summary(links)
    assert s["rows"] == 7
    assert s["by_status"] == {pl.MATCHED: 5, pl.AMBIGUOUS: 1, pl.UNMATCHED: 1}
    assert "p50" in s["confidence_quantiles"]
    assert pl.link_summary(links.iloc[0:0])["rows"] == 0
