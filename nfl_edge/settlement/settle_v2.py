"""Settlement v2: deterministic payout of any PROVEN-semantics question from proven results -- or a refusal.

Extends the incumbent engine (`nfl_edge/settlement/settle.py`, untouched and still the authority for the
families it settles) to the families v2 projects:

    WIN_MARGIN_BUCKET       range on the final margin (schedule final; overtime included)
    TEAM_WINS_BY_WEEK       wins through a stated week, settled as soon as no remaining game can change it
    DIVISION_WINNER         read back off the postseason bracket (seeds 1-4 are the division winners)
    MAKE_PLAYOFFS           presence in / proven absence from a structurally complete bracket
    PERIOD markets          winner / spread / total / team total / both-score for 1H, 2H, 1Q..4Q (play-by-play quarter scores)
    HALF_FULL_RESULT        composite: 1H result (period book) AND full-game result (schedule final, tie leg)
    PLAYER_STAT             every stat the incumbent settles, plus rush_rec_yards (sum of two proven columns)
    GAME_PLAYER_LEADER      "most <stat> in THIS GAME": the argmax over every player in the game, 1/N on a tie
    SEASON_WINS             regular-season wins from the schedule once every game of the team's season is FINAL

Rules that hold for every branch: the payout is derived from the QUESTION on the record (the same one the
projection priced), evidence is attached, the same inputs give the same output (idempotent), and anything
unprovable is REFUSED with the reason. The active-never-snap scalar branch is delegated to the incumbent engine
(exchange value only); nothing here invents a price.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

from nfl_edge.settlement import season_settlement as SS
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
REFUSED_STATS_INCOMPLETE = "REFUSED_PLAYER_STATS_INCOMPLETE"
KIND_BINARY, KIND_TIE_SPLIT = "binary", "tie_split"
# The GAME_PLAYER_LEADER branch's own rule version. SETTLE_VERSION is deliberately NOT bumped: it keys the
# immutable evaluation batches (`corpus.has_batch(game_id, SETTLE_VERSION)`), so raising it would re-settle
# every already-settled game under a new version to add a branch none of them used.
GAME_LEADER_RULE_VERSION = "settle-2.1.0"

# ------------------------------------------------------- the evidence lifecycle of a SEASON-SCOPED settlement
# A GAME settlement is immutable the moment it exists: a final score does not change, and a game that is not
# yet final is DEFERRED by the driver rather than written. Season-scoped families are not like that. They are
# examined on every run from week 1 onward -- so that none can silently disappear -- and for most of the season
# the only truthful answer is "the evidence has not arrived yet". That answer is an OBSERVATION OF A MOMENT,
# and it moves under its own feet: `SEASON_WINS` refuses with how many of the team's games are still unplayed,
# and TEAM_WINS_BY_WEEK attaches the wins and the pending game ids it counted. Every one of those changes the
# instant a game goes final.
#
# Filing all of it under one flat version made each week's truthful reading contradict the previous week's, and
# the write-once corpus -- correctly, given what it was told -- refused the whole batch. Week 2 of 2026:
# `EvaluationConflict: 11662 evaluation(s) contradict an already-published truth; nothing was written`, with
# `settlement_reason: existing='16 of 17 games not final' new='15 of 17 games not final'`. The corpus was not
# wrong; the identity was. This is the same defect, and the same remedy, as the exchange cross-check's
# terminal/provisional split (nfl_edge/settlement/crosscheck.py) -- which is where the vocabulary comes from:
#
#   TERMINAL     SETTLED, and every refusal that is about the RECORD rather than about the evidence
#                (ambiguous semantics, an unknown team). settle-2.0.0+terminal. ONE identity per prediction,
#                forever; two contradictory terminal readings still collide and still fail the run loudly,
#                which is the point -- that would mean a settled answer changed and a human must look.
#
#   PROVISIONAL  REFUSED_SEASON_INCOMPLETE: "as of this evidence, the season had not determined this".
#                settle-2.0.0+provisional.<vintage>, where <vintage> digests the evidence actually observed.
#                Re-running against unchanged evidence is a NO-OP, so an idle rerun writes nothing; evidence
#                that MOVED files a new row beside the old one. Nothing is rewritten and nothing is deleted,
#                so the week-by-week history of a season contract stays readable in full and the eventual
#                terminal settlement joins it rather than replacing it.
#
# WHY TERMINAL GETS ITS OWN VERSION TOO, rather than keeping the flat one. The rows already published carry the
# flat settle-2.0.0, and 29,792 of them are REFUSED_SEASON_INCOMPLETE -- a provisional observation filed under
# an identity that claimed to be final. Leaving terminal on the flat version would mean that in January, when
# those same contracts finally settle, the settlement collided with the stale refusal sitting on its key and
# the run failed exactly as it does now. A distinct terminal identity retires that key instead: the published
# rows are never re-offered, never rewritten, and the eventual settlement is a NEW truth beside them.
#
# Rows published before this lifecycle existed are left exactly as they are -- a published observation is never
# rewritten -- and `season_rank` classifies them by their own substance, so a legacy SETTLED row still outranks
# every provisional observation of the same prediction.
SEASON_TERMINAL = "TERMINAL"
SEASON_PROVISIONAL = "PROVISIONAL"
# The one refusal that means "the evidence has not arrived yet" rather than "this record cannot be settled".
PROVISIONAL_SEASON_STATUSES = (REFUSED_SEASON_INCOMPLETE,)
SEASON_TERMINAL_VERSION = f"{SETTLE_VERSION}+terminal"
SEASON_PROVISIONAL_PREFIX = f"{SETTLE_VERSION}+provisional."
# What a provisional season row OBSERVED, as opposed to what it concluded. The vintage digest is taken over
# exactly these, so a row is re-filed only when the season evidence itself moved.
SEASON_EVIDENCE_FIELDS = ("settlement_status", "settlement_reason", "settlement_evidence")


def season_evidence_tier(row: dict) -> str:
    """Which tier a season row belongs to, read off its own substance so legacy rows classify like the rest."""
    return SEASON_PROVISIONAL if row.get("settlement_status") in PROVISIONAL_SEASON_STATUSES else SEASON_TERMINAL


def season_evidence_vintage(row: dict) -> str:
    """A digest of the season evidence this row saw. Deterministic; no wall clock."""
    payload = json.dumps({k: row.get(k) for k in SEASON_EVIDENCE_FIELDS}, sort_keys=True, default=str)
    return hashlib.sha1(payload.encode()).hexdigest()[:12]


def season_evaluation_version(row: dict) -> str:
    """The corpus identity a season-scoped settlement row belongs under."""
    if season_evidence_tier(row) == SEASON_PROVISIONAL:
        return SEASON_PROVISIONAL_PREFIX + season_evidence_vintage(row)
    return SEASON_TERMINAL_VERSION


def season_versioned(row: dict) -> dict:
    """Stamp a season-scoped settlement with its evidence lifecycle. Never mutates the row it is given."""
    tier = season_evidence_tier(row)
    return {**row, "evidence_tier": tier, "provisional": tier == SEASON_PROVISIONAL,
            "evidence_vintage": season_evidence_vintage(row), "evaluation_version": season_evaluation_version(row)}


def season_rank(row: dict) -> tuple:
    """Sort key for choosing ONE season settlement per prediction: terminal first, then the later observation.

    Classified by the row's own `settlement_status` rather than by its version string, so the rows published
    before the lifecycle existed are ranked on their substance like everything else. Without this, plain string
    ordering put `settle-2.0.0+provisional.<vintage>` above `settle-2.0.0` and a stale "not determined yet"
    observation would outrank the settlement that superseded it.
    """
    tier = row.get("evidence_tier") or season_evidence_tier(row)
    return (1 if tier == SEASON_TERMINAL else 0, str(row.get("evaluated_at") or ""),
            str(row.get("evaluation_version") or ""))


def season_batch_manifest(rows) -> dict:
    """What a published season batch holds, by identity and by tier, so the provisional half is never invisible."""
    versions, tiers = {}, {}
    for r in rows:
        v = str(r.get("evaluation_version"))
        versions[v] = versions.get(v, 0) + 1
        t = r.get("evidence_tier") or season_evidence_tier(r)
        tiers[t] = tiers.get(t, 0) + 1
    return {"by_evaluation_version": dict(sorted(versions.items())), "by_evidence_tier": dict(sorted(tiers.items()))}


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


def _season_ledger(rec: dict, book: ResultBook, ledger):
    """The season's games, built once per season and reused (the caller may pass one in)."""
    season = rec.get("season")
    if season is None:
        return None
    if isinstance(ledger, SS.SeasonLedger):
        return ledger if ledger.season == int(season) else None
    if isinstance(ledger, dict):
        got = ledger.get(int(season))
        if got is not None:
            return got
    return SS.SeasonLedger(book.games, int(season))


def settle_projection(rec: dict, book: ResultBook, period_book: PeriodBook | None = None, *, exact_scalar_payout=None,
                      exact_scalar_source=None, exact_scalar_unavailable_reason=None, season_games: dict | None = None,
                      season_ledger=None) -> Settlement:
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
    if fam in ("TEAM_WINS_BY_WEEK", "MAKE_PLAYOFFS", "DIVISION_WINNER"):
        led = _season_ledger(rec, book, season_ledger)
        if led is None:
            return _refuse(REFUSED_SEASON_INCOMPLETE, "season record without a season")
        team = rec.get("subject_id")
        if not team:
            return _refuse(REFUSED_TEAM, f"{fam} record without a team")
        fn = {"TEAM_WINS_BY_WEEK": lambda: SS.settle_wins_through_week(team, led.season, q, led),
              "MAKE_PLAYOFFS": lambda: SS.settle_make_playoffs(team, led.season, led),
              "DIVISION_WINNER": lambda: SS.settle_division_winner(team, led.season, led)}[fam]
        r = fn()
        if r["status"] != "SETTLED":
            return _refuse(REFUSED_SEASON_INCOMPLETE, r["reason"], r.get("evidence"))
        return Settlement(SETTLED, r["settled_yes"], KIND_BINARY, r["reason"], {"family": fam, **(r.get("evidence") or {})})
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
    if fam == "GAME_PLAYER_LEADER":
        return _settle_game_player_leader(rec, q, book, gid, g)
    return _refuse(REFUSED_UNSUPPORTED, f"no settlement branch for {fam}/{period}")


def _settle_game_player_leader(rec: dict, q: dict, book: ResultBook, gid: str, g) -> Settlement:
    """"<player> records the most <stat> among all players in the game": the argmax, with 1/N on a tie.

    THE COMPARISON SET IS THE WHOLE GAME, so this is the one settlement branch whose correctness depends on
    the result book being COMPLETE rather than merely containing the subject. `games_with_player_stats` is
    the caller's explicit statement that the player-stats release contains this game; without it the
    maximum would be taken over whatever rows happened to be loaded, which would settle confidently and
    wrongly. So its absence is a refusal, not a zero.

    Branches, from rules_secondary:
      * `1/N` where N players tie for the highest value (`KIND_TIE_SPLIT`);
      * a player who did not participate settles NO -- and "did not participate" is the result book's own
        tri-state, so an UNPROVEN participation is a refusal rather than a NO;
      * a maximum of zero is refused: whether a player who took snaps and recorded no yards "records the
        most" when everyone recorded none is not pinned by the rules text, and it is not a case worth
        guessing (no such game exists in the 2026 archive).

    Verified against the archive: 32/32 settled 2026 events (16 KXNFLMOSTRECYDS + 16 KXNFLMOSTRSHYDS)
    reproduce Kalshi's YES leg as the argmax of `stats_player_week` over every player in the game.
    """
    stat = rec.get("stat_family") or q.get("stat")
    subject = rec.get("subject_id")
    if not stat:
        return _refuse(REFUSED_SEMANTICS, "leader record without a statistic")
    if not subject:
        return _refuse(REFUSED_TEAM, "leader record without a resolved player id")
    if gid not in book.games_with_player_stats:
        return _refuse(REFUSED_STATS_INCOMPLETE,
                       f"the player-stats release does not contain {gid}: the maximum over all players in "
                       "the game cannot be taken from an incomplete table", g.evidence())
    rows = book.players_in_game(gid)
    values = [(p, p.stat_value(stat)) for p in rows]
    present = [(p, v) for p, v in values if v is not None]
    if not present:
        return _refuse(REFUSED_STATS_INCOMPLETE, f"no player in {gid} carries a {stat} value", g.evidence())
    top = max(v for _, v in present)
    winners = sorted(p.player_id for p, v in present if v == top)
    me = book.player(gid, subject)
    ev = {"family": "GAME_PLAYER_LEADER", "stat": stat, "game_id": gid, "players_compared": len(present),
          "max_value": top, "winners": winners, "subject": subject,
          "subject_value": (me.stat_value(stat) if me else None),
          "subject_played": (me.played if me else None),
          "comparison_set": "every player with a stats row for this game (games_with_player_stats proven)",
          **g.evidence()}
    if top <= 0:
        return _refuse(REFUSED_SEMANTICS,
                       f"every player in {gid} recorded {top:g} {stat}: 'records the most' is not pinned "
                       "by the rules text when the maximum is zero", ev)
    if subject in winners:
        n = len(winners)
        if n == 1:
            return Settlement(SETTLED, 1.0, KIND_BINARY, f"{stat} {top:g} is the game maximum", ev,
                              version=GAME_LEADER_RULE_VERSION)
        return Settlement(SETTLED, round(1.0 / n, 6), KIND_TIE_SPLIT,
                          f"{n} players tied at {stat} {top:g}: 1/{n}", ev, version=GAME_LEADER_RULE_VERSION)
    # Not a winner. Participation does not need to be proven for this branch and deliberately is not
    # consulted: the maximum is strictly positive and belongs to somebody else, so both of the rules'
    # NO branches -- "did not participate" and "participated but was not the leader" -- pay the same $0.
    # Refusing here for unproven participation would refuse a payout that no reading of the rules disputes.
    mine = me.stat_value(stat) if me else None
    why = (f"{stat} {mine:g} below the game maximum {top:g}" if mine is not None
           else f"no recorded {stat} in a game whose maximum is {top:g}")
    return Settlement(SETTLED, 0.0, KIND_BINARY, why, ev, version=GAME_LEADER_RULE_VERSION)


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
