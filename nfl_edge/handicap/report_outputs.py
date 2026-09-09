"""What a complete RUN NFL report looks like on disk, and how to prove one is complete.

Kept apart from the workflow wrapper so the *definition* of a complete report is a testable function rather
than a sequence of shell steps nobody runs locally. Publishing is gated on it: a run that produced fifteen
game files for a sixteen-game slate has not produced a report, and the previous good `latest/` is a better
answer than a plausible incomplete one.
"""
from __future__ import annotations

import os

# A game document that renders correctly is tens of kilobytes. Anything this small is a truncated write or
# an exception caught somewhere it should not have been.
MIN_GAME_FILE_BYTES = 512


def report_paths(packet: dict) -> dict:
    """The relative paths a successful build must have produced for this packet."""
    game_ids = [g["game_id"] for g in packet.get("games") or []]
    return {
        "slate": "slate.md",
        "packet": "packet.json",
        "manifest": "manifest.json",
        "games": [f"games/{gid}.md" for gid in game_ids],
    }


def game_file_path(out_dir: str, game_id: str) -> str:
    return os.path.join(out_dir, "games", f"{game_id}.md")


def verify_report_outputs(out_dir: str, packet: dict, *, min_game_bytes: int = MIN_GAME_FILE_BYTES) -> list:
    """Return the reasons this directory is not a publishable report. Empty list means it is."""
    problems = []
    paths = report_paths(packet)
    for key in ("slate", "packet"):
        if not os.path.exists(os.path.join(out_dir, paths[key])):
            problems.append(f"{paths[key]} is missing")
    if not packet.get("games"):
        problems.append("the packet contains no games")
    missing = [rel for rel in paths["games"] if not os.path.exists(os.path.join(out_dir, rel))]
    if missing:
        problems.append(f"{len(missing)} game file(s) missing: {sorted(missing)[:5]}")
    small = [rel for rel in paths["games"]
             if os.path.exists(os.path.join(out_dir, rel))
             and os.path.getsize(os.path.join(out_dir, rel)) < min_game_bytes]
    if small:
        problems.append(f"{len(small)} game file(s) under {min_game_bytes}B: {sorted(small)[:5]}")
    return problems
