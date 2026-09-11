"""Load tennis-data.co.uk season workbooks (results + bookmaker odds) into a canonical frame.

Why a separate loader: tennis-data is the only free source of *closing odds*,
which is the benchmark any projection model has to beat.  It uses its own
naming ("Federer R."), its own round labels ("1st Round") and per-year
bookmaker columns, so the raw sheet is normalised here and linked to Sackmann
match keys later by ``tennis_edge.identity.players``.

Sheet layout (ATP; WTA replaces ``ATP`` with ``WTA`` and ``Series`` with ``Tier``)::

    ATP, Location, Tournament, Date, Series, Court, Surface, Round, Best of,
    Winner, Loser, WRank, LRank, WPts, LPts, W1, L1, ..., W5, L5, Wsets, Lsets,
    Comment, <book>W, <book>L, ..., MaxW, MaxL, AvgW, AvgL

Bookmaker pairs vary by season: CB, GB, IW, SB, B365, B&W, EX, PS, WP, UB, LB,
SJ, Max, Avg.  Pairs are detected generically (``<prefix>W`` + ``<prefix>L``)
so a new book in a future season is picked up without code changes.

Vig removal formulas are documented on ``implied_probabilities``.
"""
from __future__ import annotations

import logging
import math
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable, Optional

import numpy as np
import pandas as pd

from tennis_edge.data.sources import find_files, read_excel_gz, tennis_data_dir, year_from_filename
from tennis_edge.rules.score_parser import COMPLETED, DEFAULT, RETIRED, UNKNOWN, WALKOVER

log = logging.getLogger(__name__)

KNOWN_BOOKS = ("CB", "GB", "IW", "SB", "B365", "B&W", "EX", "PS", "WP", "UB", "LB", "SJ", "Max", "Avg")
AGGREGATE_BOOKS = ("Max", "Avg")

# Names that are not bookmaker odds even though they end in W/L.
_NOT_ODDS = {"W", "L"}

TD_COLUMNS = [
    "td_key", "tour", "source_file", "season", "tourney_no", "date", "tournament", "location", "series_tier",
    "court", "surface", "round", "round_ordinal", "round_stage", "best_of",
    "winner_name_td", "loser_name_td", "winner_rank", "loser_rank", "winner_pts", "loser_pts",
    "set_scores", "sets_w", "sets_l", "games_w", "games_l", "comment_raw", "outcome_type",
]
ODDS_COLUMNS = ["td_key", "book", "odds_winner", "odds_loser"]

# Quarantine reason codes (row-level)
MISSING_NAME = "MISSING_NAME"
BAD_DATE = "BAD_DATE"
BAD_RANK = "BAD_RANK"
SELF_MATCH = "SELF_MATCH"
# Quarantine reason codes (odds-level)
BAD_ODDS = "BAD_ODDS"

RANK_MAX = 5000

_ROUND_ORDINAL_RE = re.compile(r"^(\d)(?:st|nd|rd|th)\s+round$", re.IGNORECASE)
# ``round_stage`` = rounds *before the final* (F=0, SF=1, QF=2).  Numbered
# rounds need the draw size to be placed, so they only get ``round_ordinal``.
_ROUND_STAGE = {"the final": 0, "final": 0, "semifinals": 1, "semi-finals": 1, "quarterfinals": 2, "quarter-finals": 2,
                "round robin": -1}

_COMMENT_OUTCOME = {"completed": COMPLETED, "retired": RETIRED, "walkover": WALKOVER, "disqualified": DEFAULT,
                    "default": DEFAULT, "defaulted": DEFAULT}


class ImpliedProbabilityError(ValueError):
    """Raised for odds that cannot be converted (<= 1, NaN, non-finite)."""


# --- pure helpers -------------------------------------------------------------
def normalize_court(value: Any) -> Optional[str]:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    v = str(value).strip().lower()
    if v.startswith("in"):
        return "Indoor"
    if v.startswith("out"):
        return "Outdoor"
    return None


def normalize_surface(value: Any) -> Optional[str]:
    """Same vocabulary as the Sackmann loader so the two frames can be compared directly."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    v = str(value).strip().lower()
    for needle, canon in (("hard", "Hard"), ("clay", "Clay"), ("grass", "Grass"), ("carpet", "Carpet")):
        if needle in v:
            return canon
    return None


def parse_round(value: Any) -> tuple[Optional[str], Optional[int], Optional[int]]:
    """Return (round label, ordinal for 'Nth Round', stage-before-final for F/SF/QF/RR)."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None, None, None
    label = str(value).strip()
    key = label.lower()
    m = _ROUND_ORDINAL_RE.match(key)
    if m:
        return label, int(m.group(1)), None
    if key in _ROUND_STAGE:
        return label, None, _ROUND_STAGE[key]
    return label, None, None


def parse_td_date(value: Any) -> Optional[date]:
    """Excel dates arrive as Timestamp/datetime; older files sometimes as 'dd/mm/yyyy' text."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.date() if not pd.isna(value) else None
    if isinstance(value, date):
        return value
    s = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    ts = pd.to_datetime(s, errors="coerce", dayfirst=True)
    return None if pd.isna(ts) else ts.date()


def comment_outcome(value: Any) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return UNKNOWN
    return _COMMENT_OUTCOME.get(str(value).strip().lower(), UNKNOWN)


def detect_odds_books(columns: Iterable[str]) -> list[tuple[str, str, str]]:
    """Return [(book, winner_col, loser_col)] for every ``<prefix>W``/``<prefix>L`` pair present."""
    cols = list(columns)
    colset = set(cols)
    pairs = []
    for c in cols:
        if not isinstance(c, str) or not c.endswith("W") or c in _NOT_ODDS:
            continue
        prefix = c[:-1]
        if not prefix or prefix + "L" not in colset:
            continue
        pairs.append((prefix, c, prefix + "L"))
    unknown = [p for p, _, _ in pairs if p not in KNOWN_BOOKS]
    if unknown:
        log.warning("unrecognised bookmaker columns %s (kept; add to KNOWN_BOOKS if legitimate)", unknown)
    return pairs


def _tour_from_columns(columns: Iterable[str]) -> Optional[str]:
    cols = set(columns)
    if "ATP" in cols:
        return "ATP"
    if "WTA" in cols:
        return "WTA"
    return None


def _to_int(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").round().astype("Int64")


def _to_str(series: pd.Series) -> pd.Series:
    return series.map(lambda v: None if v is None or (isinstance(v, float) and np.isnan(v)) else (str(v).strip() or None)).astype("object")


def _set_scores(df: pd.DataFrame) -> list[list[tuple[int, int]]]:
    """Collect W1/L1..W5/L5 into per-row lists, stopping at the first empty set."""
    out: list[list[tuple[int, int]]] = []
    pairs = [(f"W{i}", f"L{i}") for i in range(1, 6) if f"W{i}" in df.columns and f"L{i}" in df.columns]
    w_cols = [pd.to_numeric(df[w], errors="coerce") for w, _ in pairs]
    l_cols = [pd.to_numeric(df[l], errors="coerce") for _, l in pairs]
    for i in range(len(df)):
        sets: list[tuple[int, int]] = []
        for w, l in zip(w_cols, l_cols):  # noqa: E741
            wv, lv = w.iloc[i], l.iloc[i]
            if pd.isna(wv) or pd.isna(lv):
                break
            sets.append((int(wv), int(lv)))
        out.append(sets)
    return out


# --- normalisation ------------------------------------------------------------
@dataclass
class TennisDataResult:
    """Canonical rows, tidy odds, both quarantines and the warnings collected on the way."""

    matches: pd.DataFrame
    odds: pd.DataFrame
    matches_quarantine: pd.DataFrame
    odds_quarantine: pd.DataFrame
    warnings: list[str] = field(default_factory=list)


def normalize_tennis_data(raw: pd.DataFrame, tour: Optional[str] = None, source_file: str = "",
                          season: Optional[int] = None) -> TennisDataResult:
    """Map one season sheet to the canonical frame + tidy odds table.

    ``td_key`` is ``TD:<tour>:<season>:<row>`` where ``row`` is the 0-based
    sheet row: deterministic for a given published file and immune to two
    players meeting twice on one date.
    """
    warnings: list[str] = []
    tour = (tour or _tour_from_columns(raw.columns) or "").upper()
    if tour not in ("ATP", "WTA"):
        raise ValueError(f"cannot determine tour for {source_file!r}: no ATP/WTA column and no tour given")
    df = raw.reset_index(drop=True)
    df.columns = [str(c).strip() for c in df.columns]
    n = len(df)

    def col(name: str) -> pd.Series:
        return df[name] if name in df.columns else pd.Series([None] * n, index=df.index, dtype="object")

    if season is None:
        season = year_from_filename(source_file)
    dates = col("Date").map(parse_td_date)
    if season is None:
        years = [d.year for d in dates if d is not None]
        season = max(set(years), key=years.count) if years else None

    out = pd.DataFrame(index=df.index)
    out["td_key"] = [f"TD:{tour}:{season}:{i:05d}" for i in range(n)]
    out["tour"] = tour
    out["source_file"] = source_file
    out["season"] = season
    out["tourney_no"] = _to_int(col(tour))
    out["date"] = dates.astype("object")
    out["tournament"] = _to_str(col("Tournament"))
    out["location"] = _to_str(col("Location"))
    out["series_tier"] = _to_str(col("Series") if "Series" in df.columns else col("Tier"))
    out["court"] = col("Court").map(normalize_court).astype("object")
    out["surface"] = col("Surface").map(normalize_surface).astype("object")
    rounds = [parse_round(v) for v in col("Round")]
    out["round"] = [r[0] for r in rounds]
    out["round_ordinal"] = pd.array([r[1] for r in rounds], dtype="Int64")
    out["round_stage"] = pd.array([r[2] for r in rounds], dtype="Int64")
    out["best_of"] = _to_int(col("Best of"))
    out["winner_name_td"] = _to_str(col("Winner"))
    out["loser_name_td"] = _to_str(col("Loser"))
    out["winner_rank"] = _to_int(col("WRank"))
    out["loser_rank"] = _to_int(col("LRank"))
    out["winner_pts"] = _to_int(col("WPts"))
    out["loser_pts"] = _to_int(col("LPts"))
    sets = _set_scores(df)
    out["set_scores"] = sets
    out["sets_w"] = _to_int(col("Wsets"))
    out["sets_l"] = _to_int(col("Lsets"))
    out["games_w"] = [sum(w for w, _ in s) for s in sets]
    out["games_l"] = [sum(l for _, l in s) for s in sets]
    out["comment_raw"] = _to_str(col("Comment"))
    out["outcome_type"] = out["comment_raw"].map(comment_outcome)
    unknown_comments = sorted({str(c) for c, o in zip(out["comment_raw"], out["outcome_type"]) if o == UNKNOWN and c is not None})
    if unknown_comments:
        warnings.append(f"{source_file}: unrecognised Comment values {unknown_comments} -> outcome UNKNOWN")

    unknown_surface = col("Surface").notna() & out["surface"].isna()
    if unknown_surface.any():
        warnings.append(f"{source_file}: {int(unknown_surface.sum())} rows with unrecognised Surface")

    out = out[TD_COLUMNS]
    clean, quarantine = validate_tennis_data(out)
    odds, odds_q = tidy_odds(df, out["td_key"], detect_odds_books(df.columns))
    for w in warnings:
        log.warning(w)
    return TennisDataResult(clean, odds, quarantine, odds_q, warnings)


def validate_tennis_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Row-level validation; quarantine keeps every column + ``reason``/``reasons``."""
    reasons: list[list[str]] = [[] for _ in range(len(df))]

    def flag(mask: pd.Series, code: str) -> None:
        for pos in np.flatnonzero(mask.to_numpy(dtype=bool, na_value=False)):
            reasons[pos].append(code)

    flag(df["winner_name_td"].isna() | df["loser_name_td"].isna(), MISSING_NAME)
    same = df["winner_name_td"].notna() & (df["winner_name_td"].str.lower() == df["loser_name_td"].str.lower())
    flag(same, SELF_MATCH)
    flag(df["date"].isna(), BAD_DATE)
    for side in ("winner", "loser"):
        r = df[f"{side}_rank"]
        flag(r.notna() & ((r <= 0) | (r > RANK_MAX)), BAD_RANK)
    bad = np.array([bool(r) for r in reasons], dtype=bool) if len(df) else np.zeros(0, dtype=bool)
    clean = df.loc[~bad].reset_index(drop=True)
    quarantine = df.loc[bad].copy()
    quarantine["reason"] = [reasons[i][0] for i in np.flatnonzero(bad)]
    quarantine["reasons"] = [";".join(reasons[i]) for i in np.flatnonzero(bad)]
    if len(quarantine):
        log.warning("tennis-data: quarantined %d/%d rows: %s", len(quarantine), len(df), quarantine["reason"].value_counts().to_dict())
    return clean, quarantine.reset_index(drop=True)


def tidy_odds(df: pd.DataFrame, td_keys: pd.Series, books: list[tuple[str, str, str]]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Long table (td_key, book, odds_winner, odds_loser) of *observed* quotes.

    A missing quote is not a record, so rows where both odds are blank are
    simply absent; rows where a quote exists but is unusable (<= 1, or only
    one side present) go to the odds quarantine with reason ``BAD_ODDS``.
    """
    frames = []
    for book, wcol, lcol in books:
        part = pd.DataFrame({"td_key": td_keys.values, "book": book,
                             "odds_winner": pd.to_numeric(df[wcol], errors="coerce").astype(float),
                             "odds_loser": pd.to_numeric(df[lcol], errors="coerce").astype(float)})
        frames.append(part)
    if not frames:
        empty = pd.DataFrame({c: pd.Series(dtype="object") for c in ODDS_COLUMNS})
        return empty, empty.assign(reason=pd.Series(dtype="object"))
    odds = pd.concat(frames, ignore_index=True)
    observed = odds["odds_winner"].notna() | odds["odds_loser"].notna()
    odds = odds.loc[observed].reset_index(drop=True)
    valid = odds["odds_winner"].notna() & odds["odds_loser"].notna() & (odds["odds_winner"] > 1.0) & (odds["odds_loser"] > 1.0)
    quarantine = odds.loc[~valid].copy()
    quarantine["reason"] = BAD_ODDS
    if len(quarantine):
        log.warning("tennis-data odds: %d unusable quotes quarantined", len(quarantine))
    return odds.loc[valid].reset_index(drop=True)[ODDS_COLUMNS], quarantine.reset_index(drop=True)


# --- vig removal --------------------------------------------------------------
def _check_odds(odds_w: float, odds_l: float) -> tuple[float, float]:
    try:
        ow, ol = float(odds_w), float(odds_l)
    except (TypeError, ValueError) as exc:
        raise ImpliedProbabilityError(f"odds must be numeric, got {odds_w!r}, {odds_l!r}") from exc
    if not (math.isfinite(ow) and math.isfinite(ol)) or ow <= 1.0 or ol <= 1.0:
        raise ImpliedProbabilityError(f"decimal odds must be finite and > 1, got {ow}, {ol}")
    return ow, ol


def overround(odds_w: float, odds_l: float) -> float:
    """Book's total implied probability ``1/o_w + 1/o_l`` (> 1 means vig)."""
    ow, ol = _check_odds(odds_w, odds_l)
    return 1.0 / ow + 1.0 / ol


def _bisect(fn, lo: float, hi: float, tol: float = 1e-12, max_iter: int = 200) -> float:
    """Root of a monotone ``fn`` on [lo, hi] with fn(lo) and fn(hi) of opposite sign."""
    f_lo = fn(lo)
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        f_mid = fn(mid)
        if abs(f_mid) < tol or (hi - lo) < tol:
            return mid
        if (f_mid > 0) == (f_lo > 0):
            lo, f_lo = mid, f_mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def implied_probabilities(odds_w: float, odds_l: float, method: str = "proportional") -> tuple[float, float]:
    """Convert two-way decimal odds to vig-free probabilities ``(p_w, p_l)``.

    With ``q_i = 1 / o_i`` and ``Q = q_w + q_l`` (the overround):

    * ``proportional`` (basic normalisation): ``p_i = q_i / Q``.  Removes the
      margin evenly; ignores favourite-longshot bias.
    * ``power``: ``p_i = q_i ** k`` with ``k`` solved so ``sum p_i = 1``
      (Vovk & Zhdanov / Clarke).  ``k > 1`` when ``Q > 1``; shrinks longshots more
      than favourites.
    * ``shin``: Shin (1993) insider-trading model.  For insider fraction ``z``,
      ``p_i = (sqrt(z^2 + 4 (1 - z) q_i^2 / Q) - z) / (2 (1 - z))`` and ``z`` is
      solved by bisection on ``[0, 1)`` so that ``sum p_i = 1``.  Produces a
      higher favourite probability than proportional, correcting the
      longshot bias documented in betting markets.

    Raises ``ImpliedProbabilityError`` for unusable odds or an unknown method.
    """
    ow, ol = _check_odds(odds_w, odds_l)
    q = np.array([1.0 / ow, 1.0 / ol])
    big_q = float(q.sum())
    method = method.lower()
    if method == "proportional":
        p = q / big_q
    elif method == "power":
        k = _bisect(lambda k: float(np.sum(q ** k)) - 1.0, 1e-6, 100.0)
        p = q ** k
    elif method == "shin":
        def excess(z: float) -> float:
            return float(np.sum((np.sqrt(z * z + 4.0 * (1.0 - z) * q * q / big_q) - z) / (2.0 * (1.0 - z)))) - 1.0
        if big_q <= 1.0:
            z = 0.0  # no margin: Shin degenerates to plain normalisation
        else:
            z = _bisect(excess, 0.0, 1.0 - 1e-9)
        p = (np.sqrt(z * z + 4.0 * (1.0 - z) * q * q / big_q) - z) / (2.0 * (1.0 - z))
        p = p / p.sum()  # absorb bisection residual so the pair sums to exactly 1
    else:
        raise ImpliedProbabilityError(f"unknown method {method!r}; use proportional | power | shin")
    return float(p[0]), float(p[1])


def add_implied_probabilities(odds: pd.DataFrame, method: str = "proportional") -> pd.DataFrame:
    """Return the tidy odds table with ``p_winner``, ``p_loser``, ``overround`` columns added."""
    if len(odds) == 0:
        return odds.assign(p_winner=pd.Series(dtype=float), p_loser=pd.Series(dtype=float), overround=pd.Series(dtype=float))
    probs = [implied_probabilities(w, l, method) for w, l in zip(odds["odds_winner"], odds["odds_loser"])]
    out = odds.copy()
    out["p_winner"] = [p[0] for p in probs]
    out["p_loser"] = [p[1] for p in probs]
    out["overround"] = 1.0 / out["odds_winner"] + 1.0 / out["odds_loser"]
    return out


# --- orchestration ------------------------------------------------------------
def load_tennis_data_file(path: Path | str, tour: Optional[str] = None) -> TennisDataResult:
    """Read one ``<year>.xlsx.gz`` / ``<year>.xls.gz`` workbook (first sheet) and normalise it."""
    p = Path(path)
    raw = read_excel_gz(p, sheet_name=0)
    assert isinstance(raw, pd.DataFrame)
    return normalize_tennis_data(raw, tour=tour, source_file=p.name, season=year_from_filename(p))


def load_all(run_dir: Path | str, tours: Iterable[str] = ("ATP", "WTA"), years: Optional[Iterable[int]] = None
             ) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    """Load all tennis-data workbooks under ``run_dir``; returns (frames, summary) like the Sackmann loader."""
    years_set = set(years) if years is not None else None
    parts: dict[str, list[pd.DataFrame]] = {"matches": [], "odds": [], "matches_quarantine": [], "odds_quarantine": []}
    summary: dict[str, Any] = {"run_dir": str(run_dir), "files": [], "warnings": [], "errors": []}
    for tour in tours:
        tour = tour.upper()
        files = find_files(tennis_data_dir(run_dir, tour), "*.xlsx.gz") + find_files(tennis_data_dir(run_dir, tour), "*.xls.gz")
        for path in sorted(files):
            year = year_from_filename(path)
            if years_set is not None and year not in years_set:
                continue
            try:
                res = load_tennis_data_file(path, tour)
            except Exception as exc:  # noqa: BLE001 - keep going, report in summary
                log.error("failed to load %s: %s", path, exc)
                summary["errors"].append({"file": str(path), "error": str(exc)})
                continue
            parts["matches"].append(res.matches)
            parts["odds"].append(res.odds)
            parts["matches_quarantine"].append(res.matches_quarantine)
            parts["odds_quarantine"].append(res.odds_quarantine)
            summary["files"].append({"tour": tour, "year": year, "file": path.name, "rows": int(len(res.matches) + len(res.matches_quarantine)),
                                     "clean": int(len(res.matches)), "quarantined": int(len(res.matches_quarantine)),
                                     "odds_quotes": int(len(res.odds)), "odds_quarantined": int(len(res.odds_quarantine))})
            summary["warnings"].extend(res.warnings)
    frames = {}
    for key, lst in parts.items():
        if lst:
            frames[key] = pd.concat(lst, ignore_index=True)
        else:
            cols = TD_COLUMNS if key.startswith("matches") else ODDS_COLUMNS
            frames[key] = pd.DataFrame({c: pd.Series(dtype="object") for c in cols})
    summary["rows"] = {k: int(len(v)) for k, v in frames.items()}
    if not summary["files"]:
        log.warning("no tennis-data workbooks found under %s", run_dir)
    return frames, summary
