import gzip
from pathlib import Path

import pandas as pd
import pytest

from tennis_edge.data import sources
from tennis_edge.data.sources import (
    SourceError, latest_source_run, list_source_runs, read_csv_gz, read_excel_gz, read_manifest, year_from_filename,
)
from tests.conftest import RUN_ID


def test_latest_source_run_picks_newest_with_manifest(sources_root: Path):
    runs = list_source_runs(sources_root)
    assert [r.name for r in runs] == ["20240101T000000Z", RUN_ID]
    assert latest_source_run(sources_root).name == RUN_ID
    assert "not_a_run" not in {r.name for r in runs}


def test_latest_source_run_raises_when_empty(tmp_path: Path):
    with pytest.raises(SourceError):
        latest_source_run(tmp_path)
    with pytest.raises(SourceError):
        latest_source_run(tmp_path / "missing")


def test_default_root_points_at_project_data_sources():
    assert sources.DEFAULT_SOURCES_ROOT == sources.PROJECT_ROOT / "data" / "sources"
    assert (sources.PROJECT_ROOT / "pyproject.toml").is_file()


def test_read_manifest(run_dir: Path):
    m = read_manifest(run_dir)
    assert m["run_id"] == RUN_ID
    assert any(f["path"].endswith("atp_matches_2024.csv.gz") for f in m["files"])


def test_read_csv_gz_roundtrip(tmp_path: Path):
    p = tmp_path / "x.csv.gz"
    with gzip.open(p, "wt") as fh:
        fh.write("a,b\n1,x\n2,y\n")
    df = read_csv_gz(p)
    assert list(df.columns) == ["a", "b"]
    assert df["a"].tolist() == [1, 2]


def test_read_csv_plain_and_missing(tmp_path: Path):
    p = tmp_path / "plain.csv"
    p.write_text("a\n1\n")
    assert read_csv_gz(p)["a"].tolist() == [1]
    with pytest.raises(SourceError):
        read_csv_gz(tmp_path / "nope.csv.gz")


def test_read_csv_gz_bad_gzip(tmp_path: Path):
    p = tmp_path / "bad.csv.gz"
    p.write_bytes(b"this is not gzip")
    with pytest.raises(SourceError):
        read_csv_gz(p)


def test_read_excel_gz_xlsx(run_dir: Path):
    pytest.importorskip("openpyxl")
    p = run_dir / "tennis_data" / "atp" / "2024.xlsx.gz"
    if not p.exists():
        pytest.skip("xlsx fixture not built")
    df = read_excel_gz(p)
    assert isinstance(df, pd.DataFrame)
    assert "Winner" in df.columns and "B365W" in df.columns
    assert len(df) == 9


def test_read_excel_unsupported_extension(tmp_path: Path):
    p = tmp_path / "x.csv.gz"
    p.write_bytes(b"")
    with pytest.raises(SourceError):
        read_excel_gz(p)


def test_year_from_filename():
    assert year_from_filename("atp_matches_qual_chall_2024.csv.gz") == 2024
    assert year_from_filename(Path("/a/b/2019.xlsx.gz")) == 2019
    assert year_from_filename("atp_rankings_20s.csv.gz") is None
    assert year_from_filename("atp_players.csv.gz") is None
