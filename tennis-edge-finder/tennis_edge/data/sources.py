"""Locate and read raw source snapshots published by ``scripts/data/bootstrap_sources.py``.

Layout (one immutable run per acquisition; never overwritten)::

    data/sources/<run_id>/manifest.json
    data/sources/<run_id>/sackmann/tennis_atp/atp_matches_2024.csv.gz
    data/sources/<run_id>/sackmann/tennis_atp/atp_matches_qual_chall_2024.csv.gz
    data/sources/<run_id>/sackmann/tennis_atp/atp_matches_futures_2024.csv.gz
    data/sources/<run_id>/sackmann/tennis_atp/atp_matches_doubles_2019.csv.gz
    data/sources/<run_id>/sackmann/tennis_atp/atp_players.csv.gz
    data/sources/<run_id>/sackmann/tennis_atp/atp_rankings_20s.csv.gz
    data/sources/<run_id>/sackmann/tennis_atp/atp_rankings_current.csv.gz
    data/sources/<run_id>/sackmann/tennis_wta/wta_matches_2024.csv.gz
    data/sources/<run_id>/sackmann/tennis_wta/wta_matches_qual_itf_2024.csv.gz
    data/sources/<run_id>/sackmann/tennis_wta/wta_players.csv.gz
    data/sources/<run_id>/sackmann/tennis_wta/wta_rankings_20s.csv.gz
    data/sources/<run_id>/tennis_data/atp/2024.xlsx.gz   (or .xls.gz)
    data/sources/<run_id>/tennis_data/wta/2024.xlsx.gz

Why gzip-on-disk: the raw snapshots live on an orphan git branch and are
fetched into sandboxes without internet; compressing them keeps that branch
small.  Readers here decompress transparently so no caller ever has to know.
"""
from __future__ import annotations

import gzip
import io
import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Optional

import pandas as pd

log = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCES_ROOT = PROJECT_ROOT / "data" / "sources"

_RUN_ID_RE = re.compile(r"^\d{8}T\d{6}Z$")


class SourceError(RuntimeError):
    """Raised when a source run / file cannot be located or read."""


def _as_path(p: Optional[os.PathLike | str], default: Path) -> Path:
    return Path(p) if p is not None else default


def list_source_runs(root: Optional[os.PathLike | str] = None) -> list[Path]:
    """All run directories (containing ``manifest.json``) under ``root``, oldest first.

    Run ids are UTC timestamps (``YYYYMMDDTHHMMSSZ``) so lexical order is
    chronological; directories whose name does not look like a run id are
    still accepted (sorted by name) but logged, because a stray directory
    usually means someone copied data by hand.
    """
    root_path = _as_path(root, DEFAULT_SOURCES_ROOT)
    if not root_path.is_dir():
        return []
    runs = []
    for child in sorted(root_path.iterdir()):
        if not child.is_dir():
            continue
        if not (child / "manifest.json").is_file():
            log.debug("skipping %s: no manifest.json", child)
            continue
        if not _RUN_ID_RE.match(child.name):
            log.warning("source run %s does not follow the <YYYYMMDDTHHMMSSZ> naming convention", child.name)
        runs.append(child)
    return runs


def latest_source_run(root: Optional[os.PathLike | str] = None) -> Path:
    """Newest ``<root>/<run_id>/`` directory that contains a ``manifest.json``.

    Raises ``SourceError`` when no run exists, so callers fail loudly rather
    than silently processing an empty dataset.
    """
    runs = list_source_runs(root)
    if not runs:
        raise SourceError(f"no source runs with manifest.json under {_as_path(root, DEFAULT_SOURCES_ROOT)}")
    return runs[-1]


def read_manifest(run_dir: os.PathLike | str) -> dict[str, Any]:
    """Load ``manifest.json`` of a run (hashes, row counts, upstream commit SHAs)."""
    path = Path(run_dir) / "manifest.json"
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise SourceError(f"cannot read manifest {path}: {exc}") from exc


def _open_maybe_gz(path: Path) -> io.BufferedReader:
    if not path.is_file():
        raise SourceError(f"source file not found: {path}")
    if path.suffix == ".gz":
        return gzip.open(path, "rb")  # type: ignore[return-value]
    return open(path, "rb")


def read_csv_gz(path: os.PathLike | str, **read_csv_kwargs: Any) -> pd.DataFrame:
    """Read a (gzip-compressed or plain) CSV into a DataFrame.

    Defaults: ``low_memory=False`` because Sackmann files mix numeric and text
    in seed/entry columns and chunked dtype inference produces spurious
    warnings; ``encoding_errors='replace'`` because a handful of historical
    player names are not valid UTF-8 and we would rather keep the row with a
    replacement character than lose it.
    """
    p = Path(path)
    kwargs: dict[str, Any] = {"low_memory": False, "encoding": "utf-8", "encoding_errors": "replace"}
    kwargs.update(read_csv_kwargs)
    with _open_maybe_gz(p) as fh:
        try:
            return pd.read_csv(fh, **kwargs)
        except (pd.errors.ParserError, UnicodeDecodeError, gzip.BadGzipFile, EOFError) as exc:
            raise SourceError(f"cannot parse CSV {p}: {exc}") from exc


def _excel_engine_for(path: Path) -> str:
    """Pick openpyxl for .xlsx and xlrd for legacy .xls, importing lazily.

    Both are optional dependencies; a clear error beats an ImportError from
    deep inside pandas.
    """
    stem = path.name[:-3] if path.name.endswith(".gz") else path.name
    ext = Path(stem).suffix.lower()
    if ext in (".xlsx", ".xlsm"):
        try:
            import openpyxl  # noqa: F401
        except ImportError as exc:
            raise SourceError("reading .xlsx requires 'openpyxl' (pip install openpyxl)") from exc
        return "openpyxl"
    if ext == ".xls":
        try:
            import xlrd  # noqa: F401
        except ImportError as exc:
            raise SourceError("reading .xls requires 'xlrd' (pip install xlrd)") from exc
        return "xlrd"
    raise SourceError(f"unsupported spreadsheet extension {ext!r} for {path}")


def read_excel_gz(path: os.PathLike | str, sheet_name: int | str | None = 0, **read_excel_kwargs: Any) -> pd.DataFrame | dict[str, pd.DataFrame]:
    """Read a (gzip-compressed or plain) Excel workbook.

    ``sheet_name=None`` returns a dict of all sheets, mirroring pandas.  The
    whole file is decompressed into memory: season workbooks are ~1 MB, so
    simplicity wins over streaming.
    """
    p = Path(path)
    engine = _excel_engine_for(p)
    with _open_maybe_gz(p) as fh:
        data = fh.read()
    try:
        return pd.read_excel(io.BytesIO(data), sheet_name=sheet_name, engine=engine, **read_excel_kwargs)
    except Exception as exc:  # noqa: BLE001 - openpyxl/xlrd raise many unrelated types
        raise SourceError(f"cannot parse spreadsheet {p}: {exc}") from exc


# --- path helpers for the known layout ----------------------------------------
def sackmann_dir(run_dir: os.PathLike | str, tour: str) -> Path:
    """``<run>/sackmann/tennis_atp`` or ``.../tennis_wta``."""
    tour_l = tour.lower()
    if tour_l not in ("atp", "wta"):
        raise ValueError(f"tour must be ATP or WTA, got {tour!r}")
    return Path(run_dir) / "sackmann" / f"tennis_{tour_l}"


def tennis_data_dir(run_dir: os.PathLike | str, tour: str) -> Path:
    """``<run>/tennis_data/atp`` or ``.../wta``."""
    tour_l = tour.lower()
    if tour_l not in ("atp", "wta"):
        raise ValueError(f"tour must be ATP or WTA, got {tour!r}")
    return Path(run_dir) / "tennis_data" / tour_l


def find_files(directory: os.PathLike | str, pattern: str) -> list[Path]:
    """Sorted glob within one directory; empty list (not an error) when the directory is absent."""
    d = Path(directory)
    if not d.is_dir():
        return []
    return sorted(d.glob(pattern))


def year_from_filename(path: os.PathLike | str) -> Optional[int]:
    """Extract a 4-digit season year from names like ``atp_matches_2024.csv.gz`` or ``2024.xlsx.gz``."""
    m = re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)", Path(path).name)
    return int(m.group(1)) if m else None
