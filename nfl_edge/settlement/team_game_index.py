"""(game, team) -> that team's player rows in a ResultBook, built once instead of scanned per call.

The autopsy asks three questions of one (game, team) per record - the team's pass attempts / carries, its offensive
snap count, its attempts by passer - and each answered them by walking EVERY player row the book holds (two seasons,
tens of thousands of rows). Measured on real 2026_06_SEA_DEN rows: 57 ms per autopsy, 52 of it in that scan; the
settlement of the same row costs 0.17 ms. A game of 14,000 autopsies is therefore ~15 minutes of scanning the same
immutable table, which is what made one large game take 23 minutes of a 120-minute job.

This module changes NO answer. The index preserves the book's iteration order within each (game, team), so every sum
and maximum is taken over the same values in the same order as before, and rows are looked up from the book at call
time (a replaced row is seen). The index is rebuilt if the number of player rows changed since it was built.
"""
from __future__ import annotations

from collections import defaultdict


def team_game_items(book, game_id: str, team: str) -> list:
    """[(player_id, PlayerGameResult)] for one team in one game, in the book's own order."""
    cached = getattr(book, "_team_game_keys", None)
    if cached is None or cached[0] != len(book.players):
        by = defaultdict(list)
        for key, pr in book.players.items():
            by[(key[0], pr.team)].append(key)
        cached = (len(book.players), by)
        try:
            book._team_game_keys = cached
        except AttributeError:                       # a book that refuses new attributes just pays the old cost
            return [(k[1], book.players[k]) for k in cached[1].get((game_id, team), ())]
    return [(k[1], book.players[k]) for k in cached[1].get((game_id, team), ())]
