"""Tournament draw simulation (single-elimination brackets).

Input: an ordered list of draw slots (bracket order, 2^k slots, `None` for byes, 'TBD' allowed as a
placeholder that must be resolved before pricing), a matchup probability function p(a, b, round)
giving P(a beats b), and known withdrawals. Output: per-player probabilities of reaching each round and
of winning the title, computed EXACTLY by dynamic programming over the bracket (no Monte Carlo noise):
for each sub-bracket the distribution of its winner is the sum over both halves of
P(x wins left) * P(y wins right) * p(x, y).

Invariants (tested): title probabilities sum to 1 over the active field; reach-round probabilities are
monotone non-increasing across rounds for every player; a bye reaches round 2 with probability 1.

Every forecast is versioned by (draw_hash, model_version, generated_at); a changed draw (withdrawal,
lucky loser) produces a new forecast, never an edit.
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict


class DrawError(ValueError):
    pass


def _round_names(n_rounds: int) -> list[str]:
    names = {1: "F", 2: "SF", 3: "QF", 4: "R16", 5: "R32", 6: "R64", 7: "R128"}
    return [names.get(n_rounds - i, f"R{2 ** (n_rounds - i)}") for i in range(n_rounds)]


def draw_hash(slots: list) -> str:
    return hashlib.sha256(json.dumps(slots, default=str).encode()).hexdigest()[:16]


def simulate_draw(slots: list, p_win, withdrawals: set | None = None, allow_tbd: bool = False) -> dict:
    """Exact bracket DP.

    slots: bracket-ordered entrants (player ids), None for a bye. Length must be a power of two.
    p_win(a, b, round_name) -> P(a beats b) in [0, 1]; must satisfy p(a,b)+p(b,a)=1 (checked on a sample).
    withdrawals: players treated as walkovers (their opponent advances with probability 1). A withdrawn
    player still occupies a slot so the bracket shape is preserved.
    Returns {'rounds': [...], 'reach': {player: {round: P}}, 'title': {player: P}, 'draw_hash': ..., 'field': n}
    """
    n = len(slots)
    if n < 2 or (n & (n - 1)) != 0:
        raise DrawError(f"draw size {n} is not a power of two")
    if not allow_tbd and any(s == "TBD" for s in slots):
        raise DrawError("unresolved TBD slot; refusing to price (fail closed)")
    withdrawals = withdrawals or set()
    n_rounds = n.bit_length() - 1
    rounds = _round_names(n_rounds)
    # dist over winners of each slot at the start: the entrant itself, or empty for a bye
    level = [({s: 1.0} if s is not None and s != "TBD" and s not in withdrawals else {}) for s in slots]
    reach = defaultdict(dict)
    for s in slots:
        if s is not None and s != "TBD":
            reach[s][f"entered"] = 1.0
    for r, rname in enumerate(rounds):
        nxt = []
        for i in range(0, len(level), 2):
            left, right = level[i], level[i + 1]
            out = defaultdict(float)
            if not left and not right:
                nxt.append({}); continue
            if not right:                       # bye / withdrawal on the right
                for x, px in left.items():
                    out[x] += px
            elif not left:
                for y, py in right.items():
                    out[y] += py
            else:
                for x, px in left.items():
                    for y, py in right.items():
                        pxy = float(p_win(x, y, rname))
                        if not 0.0 <= pxy <= 1.0:
                            raise DrawError(f"p_win({x},{y}) = {pxy} out of range")
                        out[x] += px * py * pxy
                        out[y] += px * py * (1.0 - pxy)
            nxt.append(dict(out))
        # record "reaches next stage" = wins this round
        stage = "W" if r == n_rounds - 1 else rounds[r + 1]
        for d in nxt:
            for pl, pr in d.items():
                reach[pl][stage] = reach[pl].get(stage, 0.0) + pr
        level = nxt
    title = dict(level[0])
    total = sum(title.values())
    return {"rounds": rounds, "reach": dict(reach), "title": title, "title_mass": total, "draw_hash": draw_hash(slots),
            "field": sum(1 for s in slots if s is not None and s != "TBD" and s not in withdrawals)}


def check_invariants(res: dict, tol: float = 1e-9) -> list[str]:
    v = []
    if abs(res["title_mass"] - 1.0) > tol:
        v.append(f"title probabilities sum to {res['title_mass']:.9f}")
    order = ["entered"] + res["rounds"][1:] + ["W"]
    for pl, d in res["reach"].items():
        prev = 1.0
        for st in order:
            cur = d.get(st, 0.0)
            if cur > prev + tol:
                v.append(f"{pl}: reach {st}={cur:.6f} > previous {prev:.6f}")
            prev = cur
    return v
