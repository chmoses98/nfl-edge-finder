"""Workflow entry point: `nfl.live.run` with the live fixes applied (see nfl/live/injury_dedupe.py).

    python -m nfl.live.main <the same arguments as python -m nfl.live.run>
"""
from __future__ import annotations

import sys

from . import injury_dedupe
from . import run as RUN

injury_dedupe.apply()

if __name__ == "__main__":
    sys.exit(RUN.main())
