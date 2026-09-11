from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tennis_edge.data import tennis_data as td
from tennis_edge.data.tennis_data import ImpliedProbabilityError, implied_probabilities, overround


# --- pure helpers -------------------------------------------------------------
def test_parse_round():
    assert td.parse_round("1st Round") == ("1st Round", 1, None)
    assert td.parse_round("4th Round") == ("4th Round", 4, None)
    assert td.parse_round("Quarterfinals") == ("Quarterfinals", None, 2)
    assert td.parse_round("Semifinals") == ("Semifinals", None, 1)
    assert td.parse_round("The Final") == ("The Final", None, 0)
    assert td.parse_round("Round Robin") == ("Round Robin", None, -1)
    assert td.parse_round(None) == (None, None, None)


def test_parse_td_date_forms():
    assert td.parse_td_date(pd.Timestamp("2024-01-15")) == date(2024, 1, 15)
    assert td.parse_td_date("15/01/2024") == date(2024, 1, 15)
    assert td.parse_td_date("2024-01-15") == date(2024, 1, 15)
    assert td.parse_td_date("garbage") is None
    assert td.parse_td_date(None) is None


def test_comment_outcome_and_court():
    assert td.comment_outcome("Completed") == "COMPLETED"
    assert td.comment_outcome("Retired") == "RETIRED"
    assert td.comment_outcome("Walkover") == "WALKOVER"
    assert td.comment_outcome("Disqualified") == "DEFAULT"
    assert td.comment_outcome(None) == "UNKNOWN"
    assert td.normalize_court("Indoor") == "Indoor" and td.normalize_court("outdoor") == "Outdoor"


def test_detect_odds_books_generic_pairs():
    cols = ["ATP", "Winner", "Loser", "W1", "L1", "B365W", "B365L", "B&WW", "B&WL", "PSW", "PSL", "MaxW", "MaxL", "AvgW", "AvgL", "CBW"]
    books = td.detect_odds_books(cols)
    assert [b for b, _, _ in books] == ["B365", "B&W", "PS", "Max", "Avg"]  # CBW without CBL is not a pair


# --- normalisation ------------------------------------------------------------
def test_normalize_tennis_data_frame(td_raw_frame):
    res = td.normalize_tennis_data(td_raw_frame, source_file="2024.xlsx.gz", season=2024)
    m = res.matches
    assert list(m.columns) == td.TD_COLUMNS
    assert len(m) + len(res.matches_quarantine) == 9
    assert len(m) == 7
    assert res.matches_quarantine["reason"].tolist() == [td.MISSING_NAME, td.BAD_RANK]
    r = m.iloc[0]
    assert r["td_key"] == "TD:ATP:2024:00000"
    assert r["tour"] == "ATP" and r["date"] == date(2024, 1, 15)
    assert r["tournament"] == "Australian Open" and r["location"] == "Melbourne"
    assert r["series_tier"] == "Grand Slam" and r["court"] == "Outdoor" and r["surface"] == "Hard"
    assert r["round"] == "1st Round" and r["round_ordinal"] == 1 and pd.isna(r["round_stage"])
    assert r["best_of"] == 5
    assert r["winner_name_td"] == "Federer R." and r["loser_name_td"] == "Nadal R."
    assert r["winner_rank"] == 1 and r["loser_rank"] == 2
    assert r["set_scores"] == [(7, 6), (3, 6), (6, 3), (6, 4)]
    assert r["sets_w"] == 3 and r["sets_l"] == 1 and r["games_w"] == 22
    assert r["outcome_type"] == "COMPLETED"
    assert m.iloc[1]["outcome_type"] == "RETIRED" and m.iloc[3]["outcome_type"] == "WALKOVER"
    assert m.iloc[3]["set_scores"] == []


def test_tidy_odds_and_quarantine(td_raw_frame):
    res = td.normalize_tennis_data(td_raw_frame, source_file="2024.xlsx.gz", season=2024)
    odds = res.odds
    assert list(odds.columns) == td.ODDS_COLUMNS
    assert set(odds["book"]) == {"B365", "PS", "Max", "Avg"}
    first = odds[(odds["td_key"] == "TD:ATP:2024:00000") & (odds["book"] == "B365")].iloc[0]
    assert (first["odds_winner"], first["odds_loser"]) == (1.5, 2.75)
    # one-sided PS quote on row 2 and B365W == 1.0 on row 3 are quarantined, not dropped
    q = res.odds_quarantine
    assert (q["reason"] == td.BAD_ODDS).all()
    assert {(k, b) for k, b in zip(q["td_key"], q["book"])} >= {("TD:ATP:2024:00002", "PS"), ("TD:ATP:2024:00003", "B365")}
    # rows with no quote at all for a book simply do not appear
    assert not ((odds["td_key"] == "TD:ATP:2024:00007") & (odds["book"] == "PS")).any()
    assert (odds["odds_winner"] > 1).all() and (odds["odds_loser"] > 1).all()


def test_tour_detection_from_columns(td_raw_frame):
    wta = td_raw_frame.rename(columns={"ATP": "WTA", "Series": "Tier"})
    res = td.normalize_tennis_data(wta, source_file="2024.xlsx.gz")
    assert (res.matches["tour"] == "WTA").all()
    assert res.matches["series_tier"].iloc[0] == "Grand Slam"
    assert res.matches["td_key"].iloc[0].startswith("TD:WTA:2024:")
    with pytest.raises(ValueError):
        td.normalize_tennis_data(td_raw_frame.drop(columns=["ATP"]), source_file="x")


def test_load_from_workbook(run_dir: Path):
    pytest.importorskip("openpyxl")
    p = run_dir / "tennis_data" / "atp" / "2024.xlsx.gz"
    if not p.exists():
        pytest.skip("xlsx fixture not built")
    res = td.load_tennis_data_file(p)
    assert res.matches["season"].iloc[0] == 2024
    assert res.matches["date"].iloc[0] == date(2024, 1, 15)
    frames, summary = td.load_all(run_dir)
    assert summary["files"][0]["file"] == "2024.xlsx.gz"
    assert len(frames["matches"]) == 7 and len(frames["odds"]) > 0
    assert summary["rows"]["matches_quarantine"] == 2


def test_load_all_empty(tmp_path: Path):
    frames, summary = td.load_all(tmp_path)
    assert summary["files"] == [] and len(frames["matches"]) == 0


# --- implied probabilities ----------------------------------------------------
def test_proportional_known_case():
    p_w, p_l = implied_probabilities(1.50, 2.75, "proportional")
    assert round(p_w, 3) == 0.647 and round(p_l, 3) == 0.353
    assert abs(p_w + p_l - 1) < 1e-12


@pytest.mark.parametrize("method", ["proportional", "power", "shin"])
def test_methods_sum_to_one_and_order(method):
    for ow, ol in [(1.5, 2.75), (1.05, 12.0), (1.9, 1.9), (3.4, 1.33)]:
        p_w, p_l = implied_probabilities(ow, ol, method)
        assert abs(p_w + p_l - 1) < 1e-9
        assert 0 < p_w < 1 and 0 < p_l < 1
        assert (p_w > p_l) == (ow < ol) or ow == ol


def test_shin_and_power_favour_the_favourite():
    for ow, ol in [(1.5, 2.75), (1.05, 12.0), (1.3, 3.5)]:
        prop = implied_probabilities(ow, ol, "proportional")
        shin = implied_probabilities(ow, ol, "shin")
        power = implied_probabilities(ow, ol, "power")
        assert shin[0] >= prop[0] - 1e-12
        assert power[0] >= prop[0] - 1e-12


def test_shin_even_odds_symmetric():
    p_w, p_l = implied_probabilities(1.9, 1.9, "shin")
    assert abs(p_w - 0.5) < 1e-9 and abs(p_l - 0.5) < 1e-9


def test_no_vig_returns_raw_probabilities():
    for method in ("proportional", "power", "shin"):
        p_w, p_l = implied_probabilities(2.0, 2.0, method)
        assert abs(p_w - 0.5) < 1e-9
    p_w, _ = implied_probabilities(4.0, 4 / 3, "shin")
    assert abs(p_w - 0.25) < 1e-9


def test_overround_and_errors():
    assert abs(overround(1.5, 2.75) - (1 / 1.5 + 1 / 2.75)) < 1e-12
    for bad in [(1.0, 2.0), (0.9, 3.0), (float("nan"), 2.0), (np.inf, 2.0), ("x", 2.0)]:
        with pytest.raises(ImpliedProbabilityError):
            implied_probabilities(*bad)
    with pytest.raises(ImpliedProbabilityError):
        implied_probabilities(1.5, 2.5, "magic")


def test_add_implied_probabilities_frame():
    odds = pd.DataFrame({"td_key": ["a", "b"], "book": ["B365", "PS"], "odds_winner": [1.5, 2.0], "odds_loser": [2.75, 1.8]})
    out = td.add_implied_probabilities(odds, "shin")
    assert {"p_winner", "p_loser", "overround"} <= set(out.columns)
    assert np.allclose(out["p_winner"] + out["p_loser"], 1.0)
    assert td.add_implied_probabilities(odds.iloc[0:0]).empty
