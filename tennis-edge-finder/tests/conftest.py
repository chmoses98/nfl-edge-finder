"""Shared fixtures: build a fake ``data/sources/<run_id>/`` tree from the plain-text CSVs in tests/fixtures.

Plain CSVs are kept in the repo (reviewable diffs); gzip/xlsx packaging
happens here at test time so the fixtures mirror exactly what the GitHub
Actions bootstrap job publishes.
"""
from __future__ import annotations

import gzip
import io
import json
import shutil
from pathlib import Path

import pandas as pd
import pytest

FIXTURES = Path(__file__).parent / "fixtures"
RUN_ID = "20240901T000000Z"

# fixture csv -> published relative path inside the run directory
SACKMANN_FILES = {
    "atp_matches_2024.csv": "sackmann/tennis_atp/atp_matches_2024.csv.gz",
    "atp_matches_qual_chall_2024.csv": "sackmann/tennis_atp/atp_matches_qual_chall_2024.csv.gz",
    "atp_matches_doubles_2024.csv": "sackmann/tennis_atp/atp_matches_doubles_2024.csv.gz",
    "atp_players.csv": "sackmann/tennis_atp/atp_players.csv.gz",
    "wta_matches_2024.csv": "sackmann/tennis_wta/wta_matches_2024.csv.gz",
    "wta_matches_qual_itf_2024.csv": "sackmann/tennis_wta/wta_matches_qual_itf_2024.csv.gz",
}
TENNIS_DATA_FILES = {"tennis_data_atp_2024.csv": "tennis_data/atp/2024.xlsx.gz"}


def gzip_file(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(src, "rb") as fi, gzip.open(dest, "wb") as fo:
        shutil.copyfileobj(fi, fo)


def tennis_data_frame(csv_path: Path) -> pd.DataFrame:
    """Load the fixture CSV with the dtypes an Excel sheet would carry (real dates, numeric odds)."""
    df = pd.read_csv(csv_path)
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def write_xlsx_gz(df: pd.DataFrame, dest: Path, sheet_name: str = "2024") -> None:
    openpyxl = pytest.importorskip("openpyxl")  # noqa: F841 - skip the caller when unavailable
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xw:
        df.to_excel(xw, sheet_name=sheet_name, index=False)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(dest, "wb") as fo:
        fo.write(buf.getvalue())


def build_run_dir(root: Path, run_id: str = RUN_ID, with_tennis_data: bool = True) -> Path:
    run = root / run_id
    files = []
    for src_name, rel in SACKMANN_FILES.items():
        gzip_file(FIXTURES / src_name, run / rel)
        files.append({"source": "sackmann", "path": rel})
    if with_tennis_data:
        for src_name, rel in TENNIS_DATA_FILES.items():
            try:
                write_xlsx_gz(tennis_data_frame(FIXTURES / src_name), run / rel)
                files.append({"source": "tennis_data_co_uk", "path": rel})
            except pytest.skip.Exception:
                pass  # openpyxl missing: Sackmann part of the run is still usable
    (run / "manifest.json").write_text(json.dumps({"run_id": run_id, "files": files}))
    return run


@pytest.fixture(scope="session")
def sources_root(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("sources")
    build_run_dir(root, "20240101T000000Z", with_tennis_data=False)  # an older run
    build_run_dir(root, RUN_ID)
    (root / "not_a_run").mkdir()  # directory without manifest must be ignored
    return root


@pytest.fixture(scope="session")
def run_dir(sources_root: Path) -> Path:
    return sources_root / RUN_ID


@pytest.fixture
def td_raw_frame() -> pd.DataFrame:
    return tennis_data_frame(FIXTURES / "tennis_data_atp_2024.csv")
