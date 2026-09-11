from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from tennis_edge.data import sackmann as sk
from tennis_edge.data.sources import read_csv_gz
from tests.conftest import FIXTURES


@pytest.fixture
def atp_main_raw() -> pd.DataFrame:
    return pd.read_csv(FIXTURES / "atp_matches_2024.csv", low_memory=False)


@pytest.fixture
def atp_main(atp_main_raw) -> sk.NormalizeResult:
    return sk.normalize_matches(atp_main_raw, "ATP", "atp_matches_2024.csv.gz", "main")


# --- pure helpers -------------------------------------------------------------
def test_normalize_surface():
    assert sk.normalize_surface("Hard") == "Hard"
    assert sk.normalize_surface("clay ") == "Clay"
    assert sk.normalize_surface("Grass") == "Grass"
    assert sk.normalize_surface("Carpet") == "Carpet"
    assert sk.normalize_surface("Moon") is None
    assert sk.normalize_surface(None) is None
    assert sk.normalize_surface(float("nan")) is None


def test_canonical_level_atp_and_wta():
    assert sk.canonical_level("G", "ATP") == (sk.GRAND_SLAM, True)
    assert sk.canonical_level("M", "ATP") == (sk.MASTERS_1000, True)
    assert sk.canonical_level("A", "ATP") == (sk.TOUR_500_250, True)
    assert sk.canonical_level("D", "ATP") == (sk.TEAM, True)
    assert sk.canonical_level("F", "ATP") == (sk.TOUR_FINALS, True)
    assert sk.canonical_level("C", "ATP") == (sk.CHALLENGER, True)
    assert sk.canonical_level("S", "ATP") == (sk.ITF, True)
    assert sk.canonical_level("PM", "WTA") == (sk.MASTERS_1000, True)
    assert sk.canonical_level("P", "WTA") == (sk.TOUR_500_250, True)
    assert sk.canonical_level("I", "WTA") == (sk.TOUR_500_250, True)
    assert sk.canonical_level("C", "WTA") == (sk.WTA_125, True)
    assert sk.canonical_level("W25", "WTA") == (sk.ITF, True)
    assert sk.canonical_level("W100", "WTA") == (sk.ITF, True)
    assert sk.canonical_level("T1", "WTA") == (sk.MASTERS_1000, True)
    assert sk.canonical_level("X", "ATP") == (sk.OTHER, False)
    assert sk.canonical_level(None, "ATP") == (sk.OTHER, False)


def test_is_qualifying_round_excludes_quarterfinal():
    assert sk.is_qualifying_round("Q1")
    assert sk.is_qualifying_round("Q3")
    assert not sk.is_qualifying_round("QF")
    assert not sk.is_qualifying_round("R32")
    assert not sk.is_qualifying_round(None)


def test_parse_tourney_date():
    assert sk.parse_tourney_date(20240115) == date(2024, 1, 15)
    assert sk.parse_tourney_date("20240115") == date(2024, 1, 15)
    assert sk.parse_tourney_date(20240115.0) == date(2024, 1, 15)
    assert sk.parse_tourney_date("2024ab15") is None
    assert sk.parse_tourney_date(20241340) is None
    assert sk.parse_tourney_date(None) is None


def test_infer_best_of():
    assert sk.infer_best_of("ATP", sk.GRAND_SLAM, False, date(2024, 1, 1)) == 5
    assert sk.infer_best_of("ATP", sk.GRAND_SLAM, True, date(2024, 1, 1)) == 3   # slam qualifying
    assert sk.infer_best_of("WTA", sk.GRAND_SLAM, False, date(2024, 1, 1)) == 3
    assert sk.infer_best_of("ATP", sk.TEAM, False, date(2018, 2, 2)) == 5
    assert sk.infer_best_of("ATP", sk.TEAM, False, date(2019, 2, 2)) == 3
    assert sk.infer_best_of("ATP", sk.MASTERS_1000, False, date(2024, 1, 1)) == 3


def test_team_key_is_order_independent():
    assert sk.team_key(100002, 100001) == "100001|100002"
    assert sk.team_key(100001, 100002) == "100001|100002"
    assert sk.team_key(None, 1) is None


# --- normalisation ------------------------------------------------------------
def test_normalize_keeps_every_row_and_all_columns(atp_main, atp_main_raw):
    df = atp_main.frame
    assert len(df) == len(atp_main_raw) == 14
    assert list(df.columns) == sk.CANONICAL_COLUMNS
    assert (df["tour"] == "ATP").all()
    assert (df["source_file"] == "atp_matches_2024.csv.gz").all()
    assert df["season"].iloc[0] == 2024


def test_normalize_first_row_values(atp_main):
    r = atp_main.frame.iloc[0]
    assert r["match_key"] == "ATP:2024-580:100"
    assert r["level_canonical"] == sk.GRAND_SLAM and r["level_raw"] == "G"
    assert r["surface"] == "Hard" and r["indoor"] is None
    assert r["tourney_date"] == date(2024, 1, 15)
    assert r["best_of"] == 5 and not r["best_of_inferred"]
    assert r["is_qualifying"] is False or r["is_qualifying"] == False  # noqa: E712 - numpy bool
    assert (r["sets_w"], r["sets_l"]) == (3, 1)
    assert r["set_scores"] == [(7, 6), (3, 6), (6, 3), (6, 4)]
    assert r["completed"] and r["outcome_type"] == "COMPLETED"
    assert r["tiebreaks_played"] == 1
    assert r["winner_seed"] == "1" and r["loser_entry"] == "Q" and r["winner_entry"] is None
    assert r["w_ace"] == 12 and r["l_bpFaced"] == 10
    assert r["winner_rank"] == 1 and r["loser_rank_points"] == 8500


def test_best_of_inferred_when_missing(atp_main):
    df = atp_main.frame.set_index("match_key")
    row = df.loc["ATP:2024-580:101"].iloc[0]  # duplicated key -> first copy
    assert row["best_of"] == 5 and row["best_of_inferred"]
    davis = df.loc["ATP:2024-D001:1"]
    assert davis["best_of"] == 5 and davis["best_of_inferred"] and davis["level_canonical"] == sk.TEAM


def test_walkover_and_retirement_are_kept_with_outcome(atp_main):
    df = atp_main.frame.set_index("match_key")
    assert df.loc["ATP:2024-580:102", "outcome_type"] == "RETIRED"
    assert df.loc["ATP:2024-580:103", "outcome_type"] == "WALKOVER"
    assert df.loc["ATP:2024-580:103", "score_raw"] == "W/O"
    assert pd.isna(df.loc["ATP:2024-580:103", "minutes"])


def test_unknown_surface_and_level_are_warned_not_dropped(atp_main):
    df = atp_main.frame.set_index("match_key")
    row = df.loc["ATP:2024-9999:4"]
    assert row["surface"] is None
    assert row["level_canonical"] == sk.OTHER and row["level_raw"] == "X"
    assert row["indoor"] is True  # inferred from "Indoor" in the tournament name
    assert any("unrecognised surface" in w for w in atp_main.warnings)
    assert any("unknown tourney_level" in w for w in atp_main.warnings)


def test_match_tiebreak_score(atp_main):
    row = atp_main.frame.set_index("match_key").loc["ATP:2024-M001:300"]
    assert row["set_scores"] == [(4, 6), (6, 3), (10, 8)]
    assert row["completed"] and row["sets_w"] == 2


def test_normalize_requires_columns():
    with pytest.raises(ValueError):
        sk.normalize_matches(pd.DataFrame({"tourney_id": []}), "ATP", "x.csv")
    with pytest.raises(ValueError):
        sk.normalize_matches(pd.DataFrame(), "XYZ", "x.csv")


# --- validation ---------------------------------------------------------------
def test_validate_quarantines_with_reasons(atp_main):
    clean, q = sk.validate_matches(atp_main.frame)
    assert len(clean) + len(q) == 14
    assert len(clean) == 7 and len(q) == 7
    reasons = dict(zip(q["match_key"], q["reason"]))
    assert reasons["ATP:2024-580:104"] == sk.IMPOSSIBLE_SCORE
    assert reasons["ATP:2024-580:105"] == sk.SELF_MATCH
    assert reasons["ATP:2024-9999:1"] == sk.BAD_DATE
    assert reasons["ATP:2024-9999:2"] == sk.BAD_RANK
    assert reasons["ATP:2024-9999:3"] == sk.BAD_RANK
    assert reasons["ATP:2024-580:101"] == sk.DUPLICATE_MATCH_KEY
    assert sk.MISSING_PLAYER_ID in q["reason"].values
    assert "reasons" in q.columns
    assert set(clean.columns) == set(sk.CANONICAL_COLUMNS)


def test_duplicate_keeps_first_copy(atp_main):
    clean, q = sk.validate_matches(atp_main.frame)
    kept = clean.set_index("match_key").loc["ATP:2024-580:101"]
    assert kept["w_ace"] == 8  # first copy carries stats, the duplicate does not
    assert clean["match_key"].is_unique


def test_validate_cross_file_duplicates():
    main = sk.normalize_matches(pd.read_csv(FIXTURES / "atp_matches_2024.csv"), "ATP", "atp_matches_2024.csv.gz").frame
    qc = sk.normalize_matches(pd.read_csv(FIXTURES / "atp_matches_qual_chall_2024.csv"), "ATP", "atp_matches_qual_chall_2024.csv.gz", "qual_chall").frame
    seen: set[str] = set()
    sk.validate_matches(main, seen)
    clean2, q2 = sk.validate_matches(qc, seen)
    assert q2["reason"].tolist() == [sk.DUPLICATE_MATCH_KEY]
    assert q2["match_key"].tolist() == ["ATP:2024-580:100"]
    assert len(clean2) == 3


def test_qual_chall_flags():
    qc = sk.normalize_matches(pd.read_csv(FIXTURES / "atp_matches_qual_chall_2024.csv"), "ATP", "atp_matches_qual_chall_2024.csv.gz", "qual_chall").frame
    by = qc.set_index("match_key")
    assert by.loc["ATP:2024-580:1", "is_qualifying"]
    assert by.loc["ATP:2024-580:1", "best_of"] == 3 and by.loc["ATP:2024-580:1", "best_of_inferred"]
    assert not by.loc["ATP:2024-C001:1", "is_qualifying"]  # QF
    assert by.loc["ATP:2024-C001:1", "level_canonical"] == sk.CHALLENGER
    assert by.loc["ATP:2024-C001:1", "tiebreaks_played"] == 3


def test_wta_levels_and_best_of():
    wta = sk.normalize_matches(pd.read_csv(FIXTURES / "wta_matches_2024.csv"), "WTA", "wta_matches_2024.csv.gz").frame
    assert wta["level_canonical"].tolist() == [sk.GRAND_SLAM, sk.MASTERS_1000, sk.TOUR_500_250]
    assert wta["best_of"].tolist() == [3, 3, 3] and wta["best_of_inferred"].tolist() == [True, False, False]
    itf = sk.normalize_matches(pd.read_csv(FIXTURES / "wta_matches_qual_itf_2024.csv"), "WTA", "wta_matches_qual_itf_2024.csv.gz", "qual_itf").frame
    assert itf["level_canonical"].tolist() == [sk.ITF, sk.GRAND_SLAM, sk.WTA_125]
    assert itf["is_qualifying"].tolist() == [False, True, False]


# --- doubles ------------------------------------------------------------------
def test_doubles_team_keys_and_validation():
    raw = pd.read_csv(FIXTURES / "atp_matches_doubles_2024.csv")
    res = sk.normalize_doubles(raw, "ATP", "atp_matches_doubles_2024.csv.gz")
    df = res.frame
    assert list(df.columns) == sk.DOUBLES_COLUMNS
    assert df["match_key"].tolist() == ["ATP-DBL:2024-580:1", "ATP-DBL:2024-580:2", "ATP-DBL:2024-580:3"]
    assert df["winner_team_key"].tolist() == ["100001|100002", "100001|100002", "100001|100002"]
    assert df["loser_team_key"].iloc[0] == "100003|100004"
    assert df["set_scores"].iloc[0] == [(6, 4), (3, 6), (10, 8)]
    clean, q = sk.validate_doubles(df)
    assert len(clean) == 2 and q["reason"].tolist() == [sk.SELF_MATCH]


# --- orchestration ------------------------------------------------------------
def test_discover_match_files(run_dir: Path):
    found = sk.discover_match_files(run_dir, "ATP")
    assert [(k, y) for k, y, _ in found] == [("main", 2024), ("qual_chall", 2024), ("doubles", 2024)]
    assert sk.discover_match_files(run_dir, "ATP", include=("main",), years=[2023]) == []
    assert [k for k, _, _ in sk.discover_match_files(run_dir, "WTA")] == ["main", "qual_itf"]


def test_load_all(run_dir: Path):
    frames, summary = sk.load_all(run_dir)
    assert set(frames) == {"matches", "matches_quarantine", "doubles", "doubles_quarantine"}
    assert len(summary["files"]) == 5
    assert summary["errors"] == []
    m, q = frames["matches"], frames["matches_quarantine"]
    # ATP main 7 clean + qual_chall 3 (1 cross-file dup) + WTA 3 + WTA qual_itf 3
    assert len(m) == 16
    assert len(q) == 8
    assert m["match_key"].is_unique
    assert set(m["tour"]) == {"ATP", "WTA"}
    assert summary["quarantine_by_reason"][sk.DUPLICATE_MATCH_KEY] == 2
    assert summary["rows"]["doubles"] == 2 and summary["rows"]["doubles_quarantine"] == 1
    per_file = {f["file"]: f for f in summary["files"]}
    assert per_file["atp_matches_2024.csv.gz"]["rows"] == 14
    assert per_file["atp_matches_2024.csv.gz"]["quarantined"] == 7
    assert any("unknown tourney_level" in w for w in summary["warnings"])


def test_load_all_filters(run_dir: Path):
    frames, summary = sk.load_all(run_dir, tours=("WTA",), include=("main",))
    assert len(summary["files"]) == 1
    assert len(frames["matches"]) == 3
    assert len(frames["doubles"]) == 0


def test_load_all_empty_dir(tmp_path: Path):
    frames, summary = sk.load_all(tmp_path)
    assert summary["files"] == []
    assert len(frames["matches"]) == 0
    assert list(frames["matches"].columns) == sk.CANONICAL_COLUMNS


def test_load_matches_file_reads_gz(run_dir: Path):
    p = run_dir / "sackmann" / "tennis_atp" / "atp_matches_2024.csv.gz"
    assert len(read_csv_gz(p)) == 14
    res = sk.load_matches_file(p, "ATP")
    assert res.frame["source_file"].iloc[0] == "atp_matches_2024.csv.gz"
