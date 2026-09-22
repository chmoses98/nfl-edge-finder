"""The research export's per-week files, split into parts the remote will accept.

GitHub refuses ANY file over 100 MB, at the pre-receive hook, after the whole push has been uploaded. The
research export writes one row per frozen projection for the week, so its `<label>.research.jsonl.gz` grows
with the slate. Through week 2 it was 88.6 MB -- under the limit, and nothing said how close it was. Settling
the fourteen week-2 Sunday games took it to 160.92 MB, and the push that carried the entire Sunday slate was
rejected:

    remote: error: File data/shadow/v2/research/2026_wk02.research.jsonl.gz is 160.92 MB; this exceeds
    remote: error: GitHub's file size limit of 100.00 MB
    ! [remote rejected] market-data -> market-data (pre-receive hook declined)

One oversized DERIVED file therefore blocked 413,128 rows of immutable settlement evidence, because both rode
in one commit. The workflow publishes the evidence first now, and these files are written in parts.

PART 1 KEEPS THE HISTORICAL NAME. `<label>.research.jsonl.gz` is part one and `<label>.research.partNN.<ext>`
is the overflow, so a reader that knows only the old name still finds the first part, every already-published
week keeps the path it was published under, and nothing has to be renamed or deleted on a branch whose whole
point is that published files do not change. `parts()` is the reader: it returns part one and then every
overflow part in order, and a week that never overflowed is exactly one file, as before.

The budget is well under the hard limit. A part is closed once it REACHES the budget, so the part that carries
it is the budget plus whatever the rows in flight add; the headroom absorbs that, and gzip's own buffering,
without ever approaching 100 MB.
"""
from __future__ import annotations

import glob
import os
import re

GITHUB_FILE_LIMIT_BYTES = 100 * 1024 * 1024
PART_BUDGET_BYTES = 48 * 1024 * 1024
_PART_RE = re.compile(r"\.part(\d+)\.")


def part_path(out: str, label: str, ext: str, n: int) -> str:
    """Part `n` (1-based) of `<label>.research.<ext>`. Part 1 is the historical, un-suffixed name."""
    stem = f"{label}.research"
    return os.path.join(out, f"{stem}.{ext}" if n <= 1 else f"{stem}.part{n:02d}.{ext}")


def parts(root: str, label: str, ext: str) -> list:
    """Every part of one week's export under `root`, part one first. Empty when the week is not there."""
    first = part_path(root, label, ext, 1)
    rest = sorted(glob.glob(os.path.join(root, f"{label}.research.part*.{ext}")),
                  key=lambda p: int(m.group(1)) if (m := _PART_RE.search(os.path.basename(p))) else 0)
    return ([first] if os.path.exists(first) else []) + rest


def oversized(paths) -> list:
    """The paths a remote would refuse. Checked before publishing, so the report names the file, not the push."""
    return [p for p in paths if os.path.exists(p) and os.path.getsize(p) >= GITHUB_FILE_LIMIT_BYTES]


class RollingWriter:
    """A write sink that rolls to the next part once the current one reaches the budget.

    `open_part(path)` makes the underlying writer and `close_part(w)` closes it, so the same rolling rule
    serves the gzipped ndjson and the parquet without either knowing about the other. The size is read from
    the file on disk, which lags what has been handed to a compressor -- that is what the headroom is for.
    """

    def __init__(self, out: str, label: str, ext: str, *, open_part, close_part, budget: int = PART_BUDGET_BYTES):
        self.out, self.label, self.ext = out, label, ext
        self._open, self._close = open_part, close_part
        self.budget = budget
        self.n = 0
        self.paths: list = []
        self.w = None
        self._roll()

    def _roll(self):
        if self.w is not None:
            self._close(self.w)
        self.n += 1
        path = part_path(self.out, self.label, self.ext, self.n)
        self.paths.append(path)
        self.w = self._open(path)

    def maybe_roll(self):
        """Close this part and start the next one if the current file has reached the budget.

        The compressor is flushed first. Without that, the bytes sit in gzip's buffer and the file on disk
        reads far smaller than what has actually been written -- which would let a part sail past the budget
        and land exactly where this started, on a file the remote refuses.
        """
        flush = getattr(self.w, "flush", None)
        if callable(flush):
            try:
                flush()
            except (OSError, ValueError):
                pass
        try:
            size = os.path.getsize(self.paths[-1])
        except OSError:
            return
        if size >= self.budget:
            self._roll()

    def close(self) -> list:
        if self.w is not None:
            self._close(self.w)
            self.w = None
        # a trailing part that never received a row is not published
        self.paths = [p for p in self.paths if os.path.exists(p) and os.path.getsize(p) > 0]
        return self.paths
