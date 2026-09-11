"""Load Jeff Sackmann's ``tennis_atp`` / ``tennis_wta`` match files into one canonical frame.

Design choices (the "why")
--------------------------
* One canonical schema for every file kind (main tour, qualifying/challenger,
  futures, ITF) so that ratings can be trained on the whole pyramid and
  ``level_canonical`` is the single switch for "which tier am I looking at".
* Records are *never* silently dropped.  Rows that cannot be trusted are
  moved to a quarantine frame with a ``reason`` code so that data-quality
  regressions in upstream files are visible in the run summary.
* Walkovers / retirements stay in the clean frame with ``outcome_type`` set:
  whether they count for a rating or a market backtest is a modelling
  decision that belongs downstream, not in the loader.
* Everything is a pure function of (frame, tour, source_file); no module
  state, so the loader is trivially testable with synthetic fixtures.

Schema assumptions that must be checked against real data are marked
``ASSUMPTION`` in comments.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Optional

import numpy as np
import pandas as pd

from tennis_edge.data.sources import find_files, read_csv_gz, sackmann_dir, year_from_filename
from tennis_edge.rules.score_parser import ScoreParse, parse_score

log = logging.getLogger(__name__)

TOURS = ("ATP", "WTA")

# --- canonical level vocabulary ----------------------------------------------
GRAND_SLAM = "GRAND_SLAM"
TOUR_FINALS = "TOUR_FINALS"
MASTERS_1000 = "MASTERS_1000"
TOUR_500_250 = "TOUR_500_250"
TEAM = "TEAM"
CHALLENGER = "CHALLENGER"
WTA_125 = "WTA_125"
ITF = "ITF"
OLYMPICS = "OLYMPICS"
OTHER = "OTHER"
LEVELS = (GRAND_SLAM, TOUR_FINALS, MASTERS_1000, TOUR_500_250, TEAM, CHALLENGER, WTA_125, ITF, OLYMPICS, OTHER)

# ASSUMPTION: ATP 'O' (Olympics, used from 2021 files) and WTA 'W'/'CC' codes
# should be verified against the real files; unknown codes map to OTHER with a
# warning and ``level_raw`` preserved.
_LEVEL_MAP: dict[str, dict[str, str]] = {
    "ATP": {"G": GRAND_SLAM, "M": MASTERS_1000, "A": TOUR_500_250, "D": TEAM, "F": TOUR_FINALS,
            "C": CHALLENGER, "S": ITF, "O": OLYMPICS, "E": OTHER, "J": OTHER, "T": OTHER},
    "WTA": {"G": GRAND_SLAM, "PM": MASTERS_1000, "P": TOUR_500_250, "I": TOUR_500_250, "D": TEAM,
            "F": TOUR_FINALS, "C": WTA_125, "O": OLYMPICS, "E": OTHER, "J": OTHER,
            # ASSUMPTION: pre-2009 WTA tiers.  Tier I ~ today's 1000s; the rest ~ 500/250.
            "T1": MASTERS_1000, "T2": TOUR_500_250, "T3": TOUR_500_250, "T4": TOUR_500_250, "T5": TOUR_500_250},
}
# ITF levels in wta_matches_qual_itf files: "W15", "W25", "W100" (prize money in
# $k), older files use bare numbers like "10", "25", "50" or "$10K" style.
_ITF_LEVEL_RE = re.compile(r"^(?:W|WT|\$)?\d{1,3}K?$", re.IGNORECASE)

_SURFACE_MAP = {"hard": "Hard", "clay": "Clay", "grass": "Grass", "carpet": "Carpet"}

_QUAL_ROUND_RE = re.compile(r"^Q\d+$")  # Q1..Q4; NOT "QF" (quarter-final)

# File kinds -> filename patterns per tour.  ``{year}`` is filled by the loader.
# ASSUMPTION: the WTA repo has no doubles or futures files; ATP has no qual_itf.
FILE_PATTERNS: dict[str, dict[str, str]] = {
    "ATP": {"main": "atp_matches_{year}.csv.gz", "qual_chall": "atp_matches_qual_chall_{year}.csv.gz",
            "futures": "atp_matches_futures_{year}.csv.gz", "doubles": "atp_matches_doubles_{year}.csv.gz"},
    "WTA": {"main": "wta_matches_{year}.csv.gz", "qual_itf": "wta_matches_qual_itf_{year}.csv.gz"},
}
ALL_KINDS = ("main", "qual_chall", "futures", "qual_itf", "doubles")

SERVE_STAT_COLS = ["ace", "df", "svpt", "1stIn", "1stWon", "2ndWon", "SvGms", "bpSaved", "bpFaced"]
W_STATS = [f"w_{c}" for c in SERVE_STAT_COLS]
L_STATS = [f"l_{c}" for c in SERVE_STAT_COLS]

REQUIRED_SINGLES_COLS = ("tourney_id", "tourney_name", "tourney_date", "match_num", "winner_id", "loser_id", "score", "round")
REQUIRED_DOUBLES_COLS = ("tourney_id", "tourney_date", "match_num", "winner1_id", "winner2_id", "loser1_id", "loser2_id")

# Quarantine reason codes
MISSING_PLAYER_ID = "MISSING_PLAYER_ID"
SELF_MATCH = "SELF_MATCH"
BAD_DATE = "BAD_DATE"
IMPOSSIBLE_SCORE = "IMPOSSIBLE_SCORE"
DUPLICATE_MATCH_KEY = "DUPLICATE_MATCH_KEY"
BAD_RANK = "BAD_RANK"
QUARANTINE_REASONS = (MISSING_PLAYER_ID, SELF_MATCH, BAD_DATE, IMPOSSIBLE_SCORE, DUPLICATE_MATCH_KEY, BAD_RANK)

RANK_MAX = 5000

CANONICAL_COLUMNS = [
    "match_key", "tour", "source_file", "source_kind", "season",
    "tourney_id", "tourney_name", "surface", "indoor", "draw_size", "level_raw", "level_canonical",
    "is_qualifying", "tourney_date", "match_num", "round", "best_of", "best_of_inferred",
    "winner_id", "loser_id", "winner_name", "loser_name", "winner_hand", "loser_hand",
    "winner_ht", "loser_ht", "winner_ioc", "loser_ioc", "winner_age", "loser_age",
    "winner_rank", "loser_rank", "winner_rank_points", "loser_rank_points",
    "winner_seed", "winner_entry", "loser_seed", "loser_entry",
    "score_raw", "minutes", *W_STATS, *L_STATS,
    "sets_w", "sets_l", "games_w", "games_l", "set_scores", "completed", "outcome_type",
    "tiebreaks_played", "advantage_set", "parse_error", "parse_error_reason",
]


@dataclass
class NormalizeResult:
    """Output of ``normalize_matches``: the canonical frame plus non-fatal warnings."""

    frame: pd.DataFrame
    warnings: list[str] = field(default_factory=list)


# --- small pure helpers -------------------------------------------------------
def normalize_surface(value: Any) -> Optional[str]:
    """Map free-text surface to Hard/Clay/Grass/Carpet; None when unknown/blank."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    key = str(value).strip().lower()
    if not key or key in ("none", "nan", "unknown"):
        return None
    for needle, canon in _SURFACE_MAP.items():
        if needle in key:
            return canon
    return None


def infer_indoor(surface: Optional[str], tourney_name: Any) -> Optional[bool]:
    """Best-effort indoor flag.

    Sackmann carries no court column.  Carpet is always indoor, and a handful
    of tournaments carry "indoor" in their name; everything else is unknown
    (None) rather than a guessed False, because e.g. Paris-Bercy is an indoor
    hard court with no hint in the name.
    """
    if surface == "Carpet":
        return True
    name = str(tourney_name or "").lower()
    if "indoor" in name:
        return True
    return None


def canonical_level(level_raw: Any, tour: str) -> tuple[str, bool]:
    """Return (level_canonical, known) for one raw level code."""
    if level_raw is None or (isinstance(level_raw, float) and np.isnan(level_raw)):
        return OTHER, False
    code = str(level_raw).strip()
    mapped = _LEVEL_MAP.get(tour, {}).get(code.upper())
    if mapped is not None:
        return mapped, True
    if _ITF_LEVEL_RE.match(code):
        return ITF, True
    return OTHER, False


def parse_tourney_date(value: Any) -> Optional[date]:
    """``20240115`` (int/float/str) -> date; None when malformed."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    try:
        s = str(int(float(value)))
        if len(s) != 8:
            return None
        return date(int(s[:4]), int(s[4:6]), int(s[6:8]))
    except (ValueError, TypeError, OverflowError):
        return None


def is_qualifying_round(round_value: Any) -> bool:
    """Q1/Q2/Q3 are qualifying; 'QF' is a quarter-final and must not match."""
    if round_value is None:
        return False
    return bool(_QUAL_ROUND_RE.match(str(round_value).strip().upper()))


def infer_best_of(tour: str, level_canonical: str, is_qual: bool, tourney_date: Optional[date]) -> int:
    """Best-of when the source omits it.

    Five sets only for men's Grand Slam *main draw* (slam qualifying is
    best-of-3) and Davis Cup before the 2019 format change; everything else
    is best-of-3.
    """
    if tour == "ATP" and level_canonical == GRAND_SLAM and not is_qual:
        return 5
    if tour == "ATP" and level_canonical == TEAM and tourney_date is not None and tourney_date.year < 2019:
        return 5
    return 3


def _to_int_or_none(series: pd.Series) -> pd.Series:
    """Coerce to nullable Int64 (bad tokens -> <NA>)."""
    return pd.to_numeric(series, errors="coerce").round().astype("Int64")


def _to_float(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").astype("Float64")


def _to_str_or_none(series: pd.Series) -> pd.Series:
    """Object column of stripped strings with None for blanks (keeps seeds like '1' and entries like 'WC')."""
    out = series.astype("object").where(series.notna(), None)
    return out.map(lambda v: None if v is None else (str(v).strip() or None)).astype("object")


def _seed_to_str(series: pd.Series) -> pd.Series:
    """Seeds arrive as floats (1.0) in some files; render them as '1'."""
    def fmt(v: Any) -> Optional[str]:
        if v is None or (isinstance(v, float) and np.isnan(v)):
            return None
        if isinstance(v, (int, np.integer)):
            return str(int(v))
        if isinstance(v, (float, np.floating)) and float(v).is_integer():
            return str(int(v))
        s = str(v).strip()
        return s or None
    return series.map(fmt).astype("object")


def _score_frame(scores: Iterable[Any]) -> pd.DataFrame:
    """Vectorise ``parse_score`` over a column; memoised because scores repeat heavily."""
    cache: dict[str, ScoreParse] = {}
    rows = []
    for raw in scores:
        key = "" if raw is None or (isinstance(raw, float) and np.isnan(raw)) else str(raw)
        sp = cache.get(key)
        if sp is None:
            sp = parse_score(key)
            cache[key] = sp
        rows.append((sp.sets_w, sp.sets_l, sp.games_w, sp.games_l, list(sp.set_scores), sp.completed, sp.outcome_type,
                     sp.tiebreaks_played, sp.advantage_set, sp.parse_error, sp.error_reason))
    return pd.DataFrame(rows, columns=["sets_w", "sets_l", "games_w", "games_l", "set_scores", "completed", "outcome_type",
                                       "tiebreaks_played", "advantage_set", "parse_error", "parse_error_reason"])


def _check_columns(df: pd.DataFrame, required: Iterable[str], source_file: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{source_file}: missing required columns {missing}")


# --- singles normalisation ----------------------------------------------------
def normalize_matches(raw: pd.DataFrame, tour: str, source_file: str, source_kind: str = "main") -> NormalizeResult:
    """Map one raw Sackmann singles file to the canonical schema (no filtering here).

    Row order is preserved and every input row yields exactly one output row;
    validation (``validate_matches``) is a separate step so that callers can
    inspect the un-validated frame when debugging a bad upstream file.
    """
    tour = tour.upper()
    if tour not in TOURS:
        raise ValueError(f"tour must be one of {TOURS}, got {tour!r}")
    _check_columns(raw, REQUIRED_SINGLES_COLS, source_file)
    df = raw.reset_index(drop=True)
    n = len(df)
    warnings: list[str] = []

    def col(name: str) -> pd.Series:
        return df[name] if name in df.columns else pd.Series([None] * n, index=df.index, dtype="object")

    out = pd.DataFrame(index=df.index)
    out["tour"] = tour
    out["source_file"] = source_file
    out["source_kind"] = source_kind
    out["season"] = year_from_filename(source_file)

    out["tourney_id"] = _to_str_or_none(col("tourney_id"))
    out["tourney_name"] = _to_str_or_none(col("tourney_name"))
    out["match_num"] = _to_int_or_none(col("match_num"))
    out["match_key"] = [
        f"{tour}:{tid}:{mn}" if tid is not None and mn is not pd.NA else None
        for tid, mn in zip(out["tourney_id"], out["match_num"])
    ]

    out["surface"] = col("surface").map(normalize_surface).astype("object")
    unknown_surface = col("surface").notna() & out["surface"].isna()
    if unknown_surface.any():
        vals = sorted(set(map(str, col("surface")[unknown_surface])))
        warnings.append(f"{source_file}: {int(unknown_surface.sum())} rows with unrecognised surface {vals}")
    out["indoor"] = [infer_indoor(s, t) for s, t in zip(out["surface"], out["tourney_name"])]
    out["draw_size"] = _to_int_or_none(col("draw_size"))

    out["level_raw"] = _to_str_or_none(col("tourney_level"))
    levels = [canonical_level(v, tour) for v in out["level_raw"]]
    out["level_canonical"] = [lv for lv, _ in levels]
    unknown_levels = sorted({str(r) for r, (_, known) in zip(out["level_raw"], levels) if not known and r is not None})
    if unknown_levels:
        warnings.append(f"{source_file}: unknown tourney_level codes {unknown_levels} mapped to OTHER (level_raw preserved)")

    out["round"] = _to_str_or_none(col("round"))
    out["is_qualifying"] = out["round"].map(is_qualifying_round).astype(bool)
    out["tourney_date"] = col("tourney_date").map(parse_tourney_date).astype("object")

    best_of = _to_int_or_none(col("best_of"))
    inferred = [infer_best_of(tour, lv, q, d) for lv, q, d in zip(out["level_canonical"], out["is_qualifying"], out["tourney_date"])]
    out["best_of_inferred"] = best_of.isna().astype(bool)
    out["best_of"] = best_of.where(best_of.notna(), pd.array(inferred, dtype="Int64")).astype("Int64")

    for side in ("winner", "loser"):
        out[f"{side}_id"] = _to_int_or_none(col(f"{side}_id"))
        out[f"{side}_name"] = _to_str_or_none(col(f"{side}_name"))
        out[f"{side}_hand"] = _to_str_or_none(col(f"{side}_hand"))
        out[f"{side}_ht"] = _to_float(col(f"{side}_ht"))
        out[f"{side}_ioc"] = _to_str_or_none(col(f"{side}_ioc"))
        out[f"{side}_age"] = _to_float(col(f"{side}_age"))
        out[f"{side}_rank"] = _to_int_or_none(col(f"{side}_rank"))
        out[f"{side}_rank_points"] = _to_int_or_none(col(f"{side}_rank_points"))
        out[f"{side}_seed"] = _seed_to_str(col(f"{side}_seed"))
        out[f"{side}_entry"] = _to_str_or_none(col(f"{side}_entry"))

    out["score_raw"] = _to_str_or_none(col("score"))
    out["minutes"] = _to_float(col("minutes"))
    for c in W_STATS + L_STATS:
        out[c] = _to_float(col(c))

    parsed = _score_frame(out["score_raw"])
    for c in parsed.columns:
        out[c] = parsed[c].values

    out = out[CANONICAL_COLUMNS]
    for w in warnings:
        log.warning(w)
    return NormalizeResult(out, warnings)


# --- validation ---------------------------------------------------------------
def validate_matches(df: pd.DataFrame, seen_keys: Optional[set[str]] = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split a canonical frame into (clean, quarantine).

    Quarantine rows keep every canonical column and gain ``reason`` (primary
    code, first in the ``QUARANTINE_REASONS`` order) and ``reasons`` (all
    codes, ';'-joined).  ``seen_keys`` lets a multi-file load detect
    duplicates *across* files (e.g. a match present in both the main and the
    qual_chall file); it is mutated to include this frame's clean keys.
    """
    if seen_keys is None:
        seen_keys = set()
    reasons: list[list[str]] = [[] for _ in range(len(df))]

    def flag(mask: pd.Series, code: str) -> None:
        for pos in np.flatnonzero(mask.to_numpy(dtype=bool, na_value=False)):
            reasons[pos].append(code)

    flag(df["winner_id"].isna() | df["loser_id"].isna() | df["match_key"].isna(), MISSING_PLAYER_ID)
    flag(df["winner_id"].notna() & df["loser_id"].notna() & (df["winner_id"] == df["loser_id"]), SELF_MATCH)
    flag(df["tourney_date"].isna(), BAD_DATE)
    flag(df["parse_error"].astype(bool), IMPOSSIBLE_SCORE)
    for side in ("winner", "loser"):
        r = df[f"{side}_rank"]
        flag(r.notna() & ((r <= 0) | (r > RANK_MAX)), BAD_RANK)

    # Duplicates: first occurrence (in file order, across files via seen_keys) wins.
    dup_flags = np.zeros(len(df), dtype=bool)
    for pos, key in enumerate(df["match_key"]):
        if key is None or reasons[pos]:
            continue  # already quarantined rows do not claim a key
        if key in seen_keys:
            dup_flags[pos] = True
        else:
            seen_keys.add(key)
    for pos in np.flatnonzero(dup_flags):
        reasons[pos].append(DUPLICATE_MATCH_KEY)

    bad = np.array([bool(r) for r in reasons])
    clean = df.loc[~bad].reset_index(drop=True)
    quarantine = df.loc[bad].copy()
    quarantine["reason"] = [reasons[i][0] for i in np.flatnonzero(bad)]
    quarantine["reasons"] = [";".join(reasons[i]) for i in np.flatnonzero(bad)]
    quarantine = quarantine.reset_index(drop=True)
    if len(quarantine):
        counts = quarantine["reason"].value_counts().to_dict()
        log.warning("quarantined %d/%d rows: %s", len(quarantine), len(df), counts)
    return clean, quarantine


def load_matches_file(path: Path | str, tour: str, source_kind: str = "main") -> NormalizeResult:
    """Read + normalise one singles file (validation is done by the caller)."""
    p = Path(path)
    raw = read_csv_gz(p)
    return normalize_matches(raw, tour, p.name, source_kind)


# --- doubles ------------------------------------------------------------------
DOUBLES_COLUMNS = [
    "match_key", "tour", "source_file", "season", "tourney_id", "tourney_name", "surface", "draw_size",
    "level_raw", "level_canonical", "tourney_date", "match_num", "round", "best_of", "best_of_inferred",
    "winner_team_key", "loser_team_key",
    "winner1_id", "winner2_id", "loser1_id", "loser2_id",
    "winner1_name", "winner2_name", "loser1_name", "loser2_name",
    "score_raw", "minutes", "sets_w", "sets_l", "games_w", "games_l", "set_scores", "completed", "outcome_type",
    "tiebreaks_played", "parse_error", "parse_error_reason",
]


def team_key(id_a: Any, id_b: Any) -> Optional[str]:
    """Order-independent team identifier ``'<lower_id>|<higher_id>'``; None if either id is missing."""
    if pd.isna(id_a) or pd.isna(id_b):
        return None
    a, b = int(id_a), int(id_b)
    lo, hi = (a, b) if a <= b else (b, a)
    return f"{lo}|{hi}"


def normalize_doubles(raw: pd.DataFrame, tour: str, source_file: str) -> NormalizeResult:
    """Canonical doubles frame.  Kept separate from singles: different keys, different models.

    ``match_key`` is prefixed ``<tour>-DBL`` so that concatenating singles and
    doubles frames can never collide on the (tourney_id, match_num) pair.
    """
    tour = tour.upper()
    _check_columns(raw, REQUIRED_DOUBLES_COLS, source_file)
    df = raw.reset_index(drop=True)
    n = len(df)
    warnings: list[str] = []

    def col(name: str) -> pd.Series:
        return df[name] if name in df.columns else pd.Series([None] * n, index=df.index, dtype="object")

    out = pd.DataFrame(index=df.index)
    out["tour"] = tour
    out["source_file"] = source_file
    out["season"] = year_from_filename(source_file)
    out["tourney_id"] = _to_str_or_none(col("tourney_id"))
    out["tourney_name"] = _to_str_or_none(col("tourney_name"))
    out["surface"] = col("surface").map(normalize_surface).astype("object")
    out["draw_size"] = _to_int_or_none(col("draw_size"))
    out["level_raw"] = _to_str_or_none(col("tourney_level"))
    out["level_canonical"] = [canonical_level(v, tour)[0] for v in out["level_raw"]]
    out["tourney_date"] = col("tourney_date").map(parse_tourney_date).astype("object")
    out["match_num"] = _to_int_or_none(col("match_num"))
    out["match_key"] = [
        f"{tour}-DBL:{tid}:{mn}" if tid is not None and mn is not pd.NA else None
        for tid, mn in zip(out["tourney_id"], out["match_num"])
    ]
    out["round"] = _to_str_or_none(col("round"))
    best_of = _to_int_or_none(col("best_of"))
    out["best_of_inferred"] = best_of.isna().astype(bool)
    out["best_of"] = best_of.fillna(3).astype("Int64")  # doubles is best-of-3 (slams included since 2000s)
    for p in ("winner1", "winner2", "loser1", "loser2"):
        out[f"{p}_id"] = _to_int_or_none(col(f"{p}_id"))
        out[f"{p}_name"] = _to_str_or_none(col(f"{p}_name"))
    out["winner_team_key"] = [team_key(a, b) for a, b in zip(out["winner1_id"], out["winner2_id"])]
    out["loser_team_key"] = [team_key(a, b) for a, b in zip(out["loser1_id"], out["loser2_id"])]
    out["score_raw"] = _to_str_or_none(col("score"))
    out["minutes"] = _to_float(col("minutes"))
    parsed = _score_frame(out["score_raw"])
    for c in ("sets_w", "sets_l", "games_w", "games_l", "set_scores", "completed", "outcome_type", "tiebreaks_played", "parse_error", "parse_error_reason"):
        out[c] = parsed[c].values
    return NormalizeResult(out[DOUBLES_COLUMNS], warnings)


def validate_doubles(df: pd.DataFrame, seen_keys: Optional[set[str]] = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Doubles validation: same reason codes; a team playing itself or sharing a player is SELF_MATCH."""
    if seen_keys is None:
        seen_keys = set()
    reasons: list[list[str]] = [[] for _ in range(len(df))]

    def flag(mask: pd.Series, code: str) -> None:
        for pos in np.flatnonzero(mask.to_numpy(dtype=bool, na_value=False)):
            reasons[pos].append(code)

    flag(df["winner_team_key"].isna() | df["loser_team_key"].isna() | df["match_key"].isna(), MISSING_PLAYER_ID)
    overlap = [
        (wk is not None and lk is not None) and bool(set(wk.split("|")) & set(lk.split("|")) or wk == lk)
        for wk, lk in zip(df["winner_team_key"], df["loser_team_key"])
    ]
    flag(pd.Series(overlap, index=df.index), SELF_MATCH)
    flag(df["tourney_date"].isna(), BAD_DATE)
    flag(df["parse_error"].astype(bool), IMPOSSIBLE_SCORE)
    dup = np.zeros(len(df), dtype=bool)
    for pos, key in enumerate(df["match_key"]):
        if key is None or reasons[pos]:
            continue
        if key in seen_keys:
            dup[pos] = True
        else:
            seen_keys.add(key)
    for pos in np.flatnonzero(dup):
        reasons[pos].append(DUPLICATE_MATCH_KEY)
    bad = np.array([bool(r) for r in reasons])
    clean = df.loc[~bad].reset_index(drop=True)
    quarantine = df.loc[bad].copy()
    quarantine["reason"] = [reasons[i][0] for i in np.flatnonzero(bad)]
    quarantine["reasons"] = [";".join(reasons[i]) for i in np.flatnonzero(bad)]
    return clean, quarantine.reset_index(drop=True)


# --- orchestration ------------------------------------------------------------
def discover_match_files(run_dir: Path | str, tour: str, include: Iterable[str] = ALL_KINDS,
                         years: Optional[Iterable[int]] = None) -> list[tuple[str, int, Path]]:
    """List (kind, year, path) for the requested tour/kinds/years, sorted by year then kind."""
    tour = tour.upper()
    years_set = set(years) if years is not None else None
    found: list[tuple[str, int, Path]] = []
    d = sackmann_dir(run_dir, tour)
    for kind in include:
        pattern = FILE_PATTERNS.get(tour, {}).get(kind)
        if pattern is None:
            continue  # kind not published for this tour (e.g. WTA doubles)
        for path in find_files(d, pattern.format(year="*")):
            year = year_from_filename(path)
            if year is None:
                log.warning("cannot determine season year from %s; skipping", path)
                continue
            if years_set is not None and year not in years_set:
                continue
            found.append((kind, year, path))
    return sorted(found, key=lambda t: (t[1], ALL_KINDS.index(t[0])))


def _empty_frame(columns: list[str], extra: Iterable[str] = ()) -> pd.DataFrame:
    return pd.DataFrame({c: pd.Series(dtype="object") for c in [*columns, *extra]})


def load_all(run_dir: Path | str, tours: Iterable[str] = TOURS, years: Optional[Iterable[int]] = None,
             include: Iterable[str] = ALL_KINDS) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    """Load every requested Sackmann match file under ``run_dir``.

    Returns ``(frames, summary)`` where ``frames`` has keys ``matches``,
    ``matches_quarantine``, ``doubles``, ``doubles_quarantine`` and
    ``summary`` records per-file row counts, quarantine counts by reason and
    the collected warnings, so a pipeline run can be audited without re-reading
    the raw files.
    """
    include = tuple(include)
    singles_clean: list[pd.DataFrame] = []
    singles_q: list[pd.DataFrame] = []
    doubles_clean: list[pd.DataFrame] = []
    doubles_q: list[pd.DataFrame] = []
    summary: dict[str, Any] = {"run_dir": str(run_dir), "files": [], "warnings": [], "errors": [],
                               "quarantine_by_reason": {}, "doubles_quarantine_by_reason": {}}
    seen_singles: set[str] = set()
    seen_doubles: set[str] = set()

    for tour in tours:
        tour = tour.upper()
        for kind, year, path in discover_match_files(run_dir, tour, include, years):
            try:
                if kind == "doubles":
                    res = normalize_doubles(read_csv_gz(path), tour, path.name)
                    clean, quarantine = validate_doubles(res.frame, seen_doubles)
                    doubles_clean.append(clean)
                    doubles_q.append(quarantine)
                else:
                    res = load_matches_file(path, tour, kind)
                    clean, quarantine = validate_matches(res.frame, seen_singles)
                    singles_clean.append(clean)
                    singles_q.append(quarantine)
            except Exception as exc:  # noqa: BLE001 - one bad file must not abort the whole load
                log.error("failed to load %s: %s", path, exc)
                summary["errors"].append({"file": str(path), "error": str(exc)})
                continue
            summary["files"].append({"tour": tour, "kind": kind, "year": year, "file": path.name,
                                     "rows": int(len(res.frame)), "clean": int(len(clean)), "quarantined": int(len(quarantine)),
                                     "quarantine_reasons": quarantine["reason"].value_counts().to_dict() if len(quarantine) else {}})
            summary["warnings"].extend(res.warnings)

    matches = pd.concat(singles_clean, ignore_index=True) if singles_clean else _empty_frame(CANONICAL_COLUMNS)
    matches_q = pd.concat(singles_q, ignore_index=True) if singles_q else _empty_frame(CANONICAL_COLUMNS, ["reason", "reasons"])
    doubles = pd.concat(doubles_clean, ignore_index=True) if doubles_clean else _empty_frame(DOUBLES_COLUMNS)
    doubles_q = pd.concat(doubles_q, ignore_index=True) if doubles_q else _empty_frame(DOUBLES_COLUMNS, ["reason", "reasons"])

    summary["quarantine_by_reason"] = matches_q["reason"].value_counts().to_dict() if len(matches_q) else {}
    summary["doubles_quarantine_by_reason"] = doubles_q["reason"].value_counts().to_dict() if len(doubles_q) else {}
    summary["rows"] = {"matches": int(len(matches)), "matches_quarantine": int(len(matches_q)),
                       "doubles": int(len(doubles)), "doubles_quarantine": int(len(doubles_q))}
    if not summary["files"]:
        log.warning("no Sackmann match files found under %s for tours=%s include=%s", run_dir, list(tours), include)
    return ({"matches": matches, "matches_quarantine": matches_q, "doubles": doubles, "doubles_quarantine": doubles_q}, summary)
