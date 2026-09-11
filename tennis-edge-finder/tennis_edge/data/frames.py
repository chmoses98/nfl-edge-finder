"""Small helpers for building canonical frames under pandas >= 3 semantics.

Why: pandas 3 infers the ``str`` dtype for any list/map result containing
strings, and represents missing values there as ``NaN``.  Our canonical
frames promise plain ``None`` for "unknown" in text/date/flag columns so that
``value is None`` checks and JSON serialisation behave, and so that a missing
tourney_id can never be stringified into a key like ``"ATP:nan:5"``.  The
only construction that preserves ``None`` is an explicit object-dtype Series,
which is what ``object_series`` does.
"""
from __future__ import annotations

from typing import Any, Iterable, Optional

import numpy as np
import pandas as pd


def is_missing(value: Any) -> bool:
    """True for None, NaN, NaT and pd.NA; False for everything else (including '' and 0)."""
    if value is None or value is pd.NA or value is pd.NaT:
        return True
    if isinstance(value, (float, np.floating)):
        return bool(np.isnan(value))
    return False


def object_series(values: Iterable[Any], index: Optional[pd.Index] = None) -> pd.Series:
    """Object-dtype Series that keeps ``None`` as ``None`` (no str/NaN inference)."""
    vals = list(values)
    return pd.Series(vals, index=index if index is not None else pd.RangeIndex(len(vals)), dtype="object")


def clean_text(value: Any) -> Optional[str]:
    """Stripped string or None for missing/blank."""
    if is_missing(value):
        return None
    s = str(value).strip()
    return s or None


def text_column(series: pd.Series) -> pd.Series:
    """Object column of ``clean_text`` values aligned to ``series.index``."""
    return object_series((clean_text(v) for v in series), series.index)
