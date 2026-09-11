"""Settlement v2: deterministic payout of any PROVEN-semantics question from proven results -- or a refusal.

Extends the incumbent engine (`nfl_edge/settlement/settle.py`, untouched and still the authority for the
families it settles) to the families v2 projects:

    WIN_MARGIN_BUCKET       range on the final margin (schedule final; overtime included)
    PERIOD markets          winner / spread / total / team total / both-score for 1H, 2H, 1Q..4Q (play-by-play quarter scores)
    HALF_FULL_RESULT        composite: 1H result (period book) AND full-game result (schedule final, tie leg)
    PLAYER_STAT             every stat the incumbent settles, plus rush_rec_yards (sum of two proven columns)
    SEASON_WINS             regular-season wins from the schedule once every game of the team's season is FINAL

Rules that hold for every branch: the payout is derived from the QUESTION on the record (the same one the
projection priced), evidence is attached, the same inputs give the same output (idempotent), and anything
unprovable is REFUSED with the reason. The active-never-snap scalar branch is delegated to the incumbent engine
(exchange value only); nothing here invents a price.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from nfl_edge.settlement import settle as S1
from nfl_edge.settlement.period_results import PeriodBook
from nfl_edge.settlement.results import FINAL, ResultBook

SETTLE_VERSION = "settle-2.0.0"
SETTLED = "SETTLED"
REFUSED_UNSUPPORTED = "REFUSED_UNSUPPORTED_FAMILY"
REFUSED_SEMANTICS = "REFUSED_AMBIGUOUS_SEMANTICS"
REFUSED_GAME = "REFUSED_GAME_IDENTITY"
REFUSED_NOT_FINAL = "REFUSED_GAME_NOT_FINAL"
REFUSED_PERIOD_UNAVAILABLE = "REFUSED_PERIOD_SCORES_UNAVAILABLE"
REFUSED_INCONSISTENT = "REFUSED_RESULT_INCONSISTENT"
REFUSED_TEAM = "REFUSED_TEAM_IDENTITY"
REFUSED_SEASON_INCOMPLETE = "REFUSED_SEASON_INCOMPLETE"
KIND_BINARY, KIND_TIE_SPLIT = "binary", "tie_split"


@dataclass
class Settlement:
    status: str
    settled_yes: float | None = None
    kind: str | None = None
    reason: str | None = None
    evidence: dict = field(default_factory=dict)
    version: str = SETTLE_VERSION

    @property
    def is_settled(self):
        return self.status == SETTLED

    def to_dict(self):
        return {"settlement_status": self.status, "settled_yes": self.settled_yes, "settlement_kind": self.kind, "settlement_reason": self.reason,
                "settlement_evidence": self.evidence, "settlement_rule_version": self.version}


def _refuse(status, reason, ev=None, **extra):
    e = dict(ev or {}); e.update(extra)
    return Settlement(status, reason=reason, evidence=e)


def _compare(x: float, q: dict) -> tuple[bool | None, str | None]:
    kind = q.get("kind")
    if kind == "THRESHOLD":
        op, k = q.get("op"), q.get("k")
        if k is None or op not in (">=", ">", "<=", "<"):
            return None, f"threshold question without a usable comparison ({op!r}, {k!r})"
        return {">=": x >= k, ">": x > k, "<=": x <= k, "<": x < k}[op], None
    if kind == "RANGE":
        lo, hi = q.get("lo"), q.get("hi")
        if lo is None:
            return None, "range question without a lower bound"
        return (x >= lo) and (hi is None or x <= hi), None
    return None, f"question kind {kind!r} is not a comparison"


def _score_stat(stat: str, subject: str | None, hs: float, aws: float, home: str, away: str):
    if stat == "margin":
        if subject == home:
            return hs - aws
        if subject == away:
            return aws - hs
        if subject is None:
            return hs - aws
        return None
    if stat == "total":
        return hs + aws
    if stat == "team_points":
        return hs if subject == home else (aws if subject == away else None)
    if stat == "min_team_points":
        return min(hs, aws)
    if stat == "max_team_points":
        return max(hs, aws)
    if stat == "abs_margin":
        return abs(hs - aws)
    return None


def _settle_score_question(q: dict, hs: float, aws: float, home: str, away: str, ev: dict, *, tie_rule: str | None) -> Settlement:
    kind = q.get("kind")
    if kind == "EVENT":
        m = hs - aws
        if q.get("event") == "TIE":
            return Settlement(SETTLED, 1.0 if m == 0 else 0.0, KIND_BINARY, "tie leg", ev)
        if q.get("event") == "WIN":
            x = _score_stat("margin", q.get("subject"), hs, aws, home, away)
            if x is None:
                return _refuse(REFUSED_TEAM, f"team {q.get('subject')!r} is not in the game", ev)
            if x == 0:
                if tie_rule == "HALF_PAYOUT":
                    return Settlement(SETTLED, 0.5, KIND_TIE_SPLIT, "tied: $0.50 per side", ev)
                return Settlement(SETTLED, 0.0, KIND_BINARY, "tied period: team strike NO", ev)
            return Settlement(SETTLED, 1.0 if x > 0 else 0.0, KIND_BINARY, f"margin for team {x:g}", ev)
        if q.get("event") == "BOTH_SCORE":
            return Settlement(SETTLED, 1.0 if (hs > 0 and aws > 0) else 0.0, KIND_BINARY, "both teams scored" if (hs > 0 and aws > 0) else "a team was held scoreless", ev)
        return _refuse(REFUSED_SEMANTICS, f"event {q.get('event')!r} has no score-based settlement", ev)
    x = _score_stat(q.get("stat"), q.get("subject"), hs, aws, home, away)
    if x is None:
        return _refuse(REFUSED_TEAM, f"statistic {q.get('stat')!r} for subject {q.get('subject')!r} is not defined on this game", ev)
    met, bad = _compare(x, q)
    if bad:
        return _refuse(REFUSED_SEMANTICS, bad, ev)
    ev = {**ev, "value": x, "comparison": f"{q.get('stat')}={x:g} {q.get('op') or 'in'} {q.get('k') if q.get('kind') == 'THRESHOLD' else [q.get('lo'), q.get('hi')]}"}
    return Settlement(SETTLED, 1.0 if met else 0.0, KIND_BINARY, ev["comparison"], ev)


def settle_projection(rec: dict, book: ResultBook, period_book: PeriodBook | None = None, *, exact_scalar_payout=None,
                      exact_scalar_source=None, exact_scalar_unavailable_reason=None, season_games: dict | None = None) -> Settlement:
    """Settle one projection record (its `question` field is the authority on what was priced)."""
    q = rec.get("question") or {}
    fam, period = rec.get("market_family"), rec.get("period") or "FULL"
    gid = rec.get("game_id")
    if rec.get("semantic_confidence") not in ("PROVEN", "LIKELY"):
        return _refuse(REFUSED_SEMANTICS, f"semantic confidence {rec.get('semantic_confidence')}: never settled by inference")
    # ---- player stats: the incumbent engine is the authority, extended with the summed stat
    if fam == "PLAYER_STAT":
        obs = {"family": "PLAYER_STAT", "period": period, "game_id": gid, "stat": rec.get("stat_family"), "player_id": rec.get("subject_id"),
               "player_name": rec.get("subject_name"), "threshold": q.get("k"), "operator": q.get("op"), "floor_strike": None, "direction": "YES"}
        if rec.get("stat_family") == "rush_rec_yards":
            return _settle_rush_rec(obs, book, exact_scalar_payout, exact_scalar_source, exact_scalar_unavailable_reason)
        s = S1.settle_observation(obs, book, exact_scalar_payout=exact_scalar_payout, exact_scalar_source=exact_scalar_source,
                                  exact_scalar_unavailable_reason=exact_scalar_unavailable_reason)
        return Settlement(s.status, s.settled_yes, s.kind, s.reason, s.evidence)
    # ---- season
    if fam in ("SEASON_WINS", "SEASON_WINS_EXACT"):
        return _settle_season_wins(rec, q, book, season_games)
    # ---- game-scoped families need a final game
    if not gid:
        return _refuse(REFUSED_GAME, "record did not join a scheduled game")
    g = book.games.get(gid)
    if g is None:
        return _refuse(REFUSED_GAME, f"{gid} not in the resolved schedule")
    if g.inconsistency:
        return _refuse(REFUSED_INCONSISTENT, g.inconsistency, g.evidence())
    if g.status != FINAL:
        return _refuse(REFUSED_NOT_FINAL, g.provisional_reason or f"{gid} has no proven final", g.evidence())
    verdict = book.final_verdict(gid) if hasattr(book, "final_verdict") else None
    if verdict is not None and verdict.contradictions:
        return _refuse(REFUSED_INCONSISTENT, "; ".join(verdict.contradictions), g.evidence())
    if verdict is not None and not verdict.proven:
        return _refuse(REFUSED_NOT_FINAL, f"{gid} looks final but nothing independent attests completion", g.evidence())
    home, away = g.home_team, g.away_team
    if fam in ("GAME_WINNER", "SPREAD", "TOTAL", "TEAM_TOTAL", "BOTH_TEAMS_SCORE_N", "WIN_MARGIN_BUCKET") and period == "FULL":
        ev = {"family": fam, "period": period, **g.evidence()}
        return _settle_score_question(q, float(g.home_score), float(g.away_score), home, away, ev, tie_rule=q.get("tie_rule"))
    if fam in ("PERIOD_WINNER", "SPREAD", "TOTAL", "TEAM_TOTAL", "BOTH_TEAMS_SCORE") and period in ("1H", "2H", "1Q", "2Q", "3Q", "4Q"):
        pr = period_book.get(gid) if period_book else None
        if pr is None or not pr.complete:
            return _refuse(REFUSED_PERIOD_UNAVAILABLE, f"no complete play-by-play quarter scores for {gid}", g.evidence())
        if pr.inconsistency:
            return _refuse(REFUSED_INCONSISTENT, pr.inconsistency, {**g.evidence(), **pr.evidence()})
        ev = {"family": fam, **pr.evidence(period)}
        return _settle_score_question(q, pr.period_points(period, "home"), pr.period_points(period, "away"), home, away, ev, tie_rule="TIE_LEG_YES")
    if fam == "HALF_FULL_RESULT":
        pr = period_book.get(gid) if period_book else None
        if pr is None or not pr.complete:
            return _refuse(REFUSED_PERIOD_UNAVAILABLE, f"no complete play-by-play quarter scores for {gid}", g.evidence())
        if pr.inconsistency:
            return _refuse(REFUSED_INCONSISTENT, pr.inconsistency, {**g.evidence(), **pr.evidence()})
        legs = q.get("legs") or []
        if len(legs) != 2:
            return _refuse(REFUSED_SEMANTICS, "half/full composite without two legs")
        r1 = _settle_score_question(legs[0], pr.period_points("1H", "home"), pr.period_points("1H", "away"), home, away, {"leg": "1H", **pr.evidence("1H")}, tie_rule="TIE_LEG_YES")
        r2 = _settle_score_question(legs[1], float(g.home_score), float(g.away_score), home, away, {"leg": "FULL", **g.evidence()}, tie_rule="TIE_LEG_YES")
        if not (r1.is_settled and r2.is_settled):
            return _refuse(REFUSED_SEMANTICS, f"a leg could not be settled: {r1.reason} / {r2.reason}")
        y = 1.0 if (r1.settled_yes == 1.0 and r2.settled_yes == 1.0) else 0.0
        return Settlement(SETTLED, y, KIND_BINARY, f"1H leg {r1.settled_yes:g}, full leg {r2.settled_yes:g}", {"legs": [r1.evidence, r2.evidence]})
    return _refuse(REFUSED_UNSUPPORTED, f"no settlement branch for {fam}/{period}")


def _settle_rush_rec(obs, book, exact_scalar_payout, exact_scalar_source, exact_scalar_unavailable_reason):
    """rushing_yards + receiving_yards: settle each proven column through the incumbent's participation logic."""
    a = S1.settle_observation({**obs, "stat": "rushing_yards"}, book, exact_scalar_payout=exact_scalar_payout, exact_scalar_source=exact_scalar_source,
                              exact_scalar_unavailable_reason=exact_scalar_unavailable_reason)
    if a.status != S1.SETTLED or a.kind != S1.KIND_BINARY:
        return Settlement(a.status, a.settled_yes, a.kind, a.reason, a.evidence)
    b = S1.settle_observation({**obs, "stat": "receiving_yards"}, book)
    if b.status != S1.SETTLED or b.kind != S1.KIND_BINARY:
        return Settlement(b.status, b.settled_yes, b.kind, b.reason, b.evidence)
    ry = a.evidence.get("stat_value"); cy = b.evidence.get("stat_value")
    if ry is None or cy is None:
        return _refuse(S1.REFUSED_STAT_UNAVAILABLE, "a component yardage column is missing", {"rush": a.evidence, "rec": b.evidence})
    total = float(ry) + float(cy)
    k, op = obs.get("threshold"), obs.get("operator")
    met = {">=": total >= k, ">": total > k}.get(op)
    if met is None:
        return _refuse(REFUSED_SEMANTICS, f"operator {op!r}", {"rush": a.evidence, "rec": b.evidence})
    return Settlement(SETTLED, 1.0 if met else 0.0, KIND_BINARY, f"rush {ry:g} + rec {cy:g} = {total:g} {op} {k}", {"rush": a.evidence, "rec": b.evidence, "total": total})


def _settle_season_wins(rec, q, book, season_games):
    team, season = rec.get("subject_id"), rec.get("season")
    if not team or season is None:
        return _refuse(REFUSED_TEAM, "season-wins record without team or season")
    games = [g for g in book.games.values() if g.season == season and g.game_type == "REG" and team in (g.home_team, g.away_team)]
    if not games:
        return _refuse(REFUSED_SEASON_INCOMPLETE, f"no regular-season games for {team} {season} in the result book")
    if any(g.status != FINAL for g in games):
        return _refuse(REFUSED_SEASON_INCOMPLETE, f"{sum(1 for g in games if g.status != FINAL)} of {len(games)} games not final")
    wins = sum(1 for g in games if (g.margin_for(team) or 0) > 0)
    ties = sum(1 for g in games if g.margin_for(team) == 0)
    ev = {"team": team, "season": season, "games": len(games), "wins": wins, "ties": ties, "note": "a tie is not a win (LIKELY, not pinned by rules text)"}
    if q.get("kind") == "EVENT" and q.get("event") == "EXACT_WINS":
        return Settlement(SETTLED, 1.0 if wins == q.get("k") else 0.0, KIND_BINARY, f"{wins} wins", ev)
    met, bad = _compare(float(wins), q)
    if bad:
        return _refuse(REFUSED_SEMANTICS, bad, ev)
    return Settlement(SETTLED, 1.0 if met else 0.0, KIND_BINARY, f"{wins} wins", ev)
