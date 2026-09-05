#!/usr/bin/env python3
"""Refresh the opportunity usage tables so route and red-zone shares include the games just played.

Extracted from an inline `python3 -c` heredoc in shadow-price.yml. That heredoc's continuation lines sat at
column 0 inside a YAML block scalar, which made the whole workflow file unparseable -- 36 consecutive runs
failed instantly at parse time and the scheduled shadow pricing never ran at all. Workflow steps call a file.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.features.opportunity import build_usage  # noqa: E402

if __name__ == "__main__":
    seasons = list(range(2016, 2027))
    build_usage(seasons, out_dir=os.path.join(ROOT, "research", "opportunity"))
    print(f"opportunity usage rebuilt for {seasons[0]}-{seasons[-1]}")
