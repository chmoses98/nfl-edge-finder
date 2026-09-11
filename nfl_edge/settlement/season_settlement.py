"""SEASON SETTLEMENT: deterministic payout for wins-through-week, division winner and playoff qualification.

These three families carried probabilities with no settlement branch (readiness R07). The requirement is not
that they settle during week 1 -- none of them can -- but that every probability written today has a
deterministic future settlement path that cannot be satisfied by guessing.

The hard part is that two of them are decided by the NFL's tie-breaking procedure, which this repo deliberately
does NOT reproduce (the season engine's tie-break is approximate, which is exactly why its projections are
LIKELY and shadow-only). Settlement therefore never runs a tie-break. It reads the league's own output:

    TEAM_WINS_BY_WEEK   the team's own regular-season games through week W. No tie-break exists. The only
                        judgement is what a TIE is worth, and the rules text does not pin it -- so both
                        readings (a tie is 0 wins / a tie is half a win) are evaluated and the contract settles
                        only where they agree. Settlement can also be reached EARLY, whenever every remaining
                        game through W is irrelevant: the achievable win total is bounded below by the wins
                        already proven and above by those wins plus every game still to play, and when the
                        comparison is constant across that whole interval the answer is already determined.

    DIVISION_WINNER     derived from the POSTSEASON BRACKET, not from standings arithmetic. By rule the four
                        division winners of a conference take seeds 1-4, the wild-card round is played at the
                        higher seed's home field, and seeds 1-4 are exactly {wild-card hosts} + {bye teams}.
                        The league applies its own tie-breakers when it seeds the bracket; reading the bracket
                        back is reading the official answer. The derivation is refused unless the bracket is
                        structurally complete (exactly eight division winners, four per conference) and unless
                        each derived winner is tied-for-best on W-L-T inside its own division -- a division
                        winner with a beaten record is proof that the bracket was misread.

    MAKE_PLAYOFFS       a team that appears anywhere in the postseason bracket has qualified: proven YES. A
                        team absent from a STRUCTURALLY COMPLETE bracket (12 or 14 participants, split evenly
                        by conference) is proven eliminated: NO. Anything else is refused. Standings are never
                        consulted, so a team cannot be declared out because its record looks bad.

Every branch fails closed: an incomplete schedule, an unfinished game, an ambiguous tie, a bracket that is not
yet fully determined or that contradicts the records all REFUSE with a named reason and the evidence attached.
Nothing here is ever settled by inference, and no branch can be reached before the evidence exists.

Rule version: season-settle-1.0.0.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from nfl_edge.settlement.results import FINAL

SEASON_SETTLE_VERSION = "season-settle-1.0.0"

# The eight divisions. Held here so settlement never imports the projection engine; a test pins the two maps
# together so they cannot drift apart.
DIVISIONS = {
    "AFC_EAST": ("BUF", "MIA", "NE", "NYJ"), "AFC_NORTH": ("BAL", "CIN", "CLE", "PIT"),
    "AFC_SOUTH": ("HOU", "IND", "JAX", "TEN"), "AFC_WEST": ("DEN", "KC", "LAC", "LV"),
    "NFC_EAST": ("DAL", "NYG", "PHI", "WAS"), "NFC_NORTH": ("CHI", "DET", "GB", "MIN"),
    "NFC_SOUTH": ("ATL", "CAR", "NO", "TB"), "NFC_WEST": ("ARI", "LA", "SEA", "SF"),
}
TEAM_DIVISION = {t: d for d, ts in DIVISIONS.items() for t in ts}
TEAM_CONFERENCE = {t: d.split("_")[0] for t, d in TEAM_DIVISION.items()}

POSTSEASON_TYPES = ("WC", "WILDCARD", "DIV", "CON", "SB")
WILD_CARD = ("WC", "WILDCARD")
# Structural invariants of the bracket. Both playoff formats satisfy them: 12 participants with 4 wild-card
# hosts and 4 byes (through 2019), 14 with 6 hosts and 2 byes (2020 on). Division winners are 8 either way.
VALID_PARTICIPANT_COUNTS = (12, 14)
DIVISION_WINNERS_TOTAL = 8
DIVISION_WINNERS_PER_CONFERENCE = 4

R_NO_SCHEDULE = "no regular-season games for this team and season in the result book"
R_SCHEDULE_INCOMPLETE = "the schedule through the stated week is not complete enough to count wins"
R_GAMES_PENDING = "games through the stated week are not final and the answer is not yet determined"
R_TIE_AMBIGUOUS = "the team has a tie and the rules text does not pin what a tie is worth"
R_NO_WEEK = "the contract does not state the week the wins are counted through"
R_BRACKET_INCOMPLETE = "the postseason bracket is not yet structurally complete"
R_BRACKET_CONTRADICTS = "the derived bracket contradicts the regular-season records"
R_UNKNOWN_TEAM = "team is not one of the 32 franchises"


def _teamkey(t):
    return (t or "").strip().upper() or None


@dataclass
class TeamSeason:
    """One team's regular season: every scheduled game, which are proven final, and the wins so far."""
    team: str
    season: int
    games: list = field(default_factory=list)          # GameResult, ordered by week

    def through(self, week: int) -> list:
        return [g for g in self.games if g.week is not None and g.week <= week]

    def record_through(self, week: int) -> dict:
        sched = self.through(week)
        final = [g for g in sched if g.status == FINAL]
        wins = sum(1 for g in final if (g.margin_for(self.team) or 0) > 0)
        ties = sum(1 for g in final if g.margin_for(self.team) == 0)
        losses = len(final) - wins - ties
        return {"team": self.team, "season": self.season, "through_week": week, "scheduled": len(sched),
                "final": len(final), "pending": len(sched) - len(final), "wins": wins, "losses": losses, "ties": ties,
                "pending_game_ids": [g.game_id for g in sched if g.status != FINAL]}


class SeasonLedger:
    """Every game of one season, split into the regular season by team and the postseason bracket.

    `locations` maps game_id -> the schedule's `location` column when it is available; a wild-card game at a
    neutral site would break the "the host is the higher seed" rule the division derivation rests on, so a
    neutral postseason game that is not the Super Bowl refuses the derivation rather than being ignored.
    """

    def __init__(self, games, season: int, *, locations: dict | None = None):
        self.season = int(season)
        self.locations = locations or {}
        rows = list(games.values()) if isinstance(games, dict) else list(games)
        self.all = [g for g in rows if g.season == self.season]
        self.regular = [g for g in self.all if (g.game_type or "REG").upper() == "REG"]
        self.postseason = [g for g in self.all if (g.game_type or "").upper() in POSTSEASON_TYPES
                           and _teamkey(g.home_team) and _teamkey(g.away_team)]
        self.by_team: dict = {}
        for g in self.regular:
            for t in (_teamkey(g.home_team), _teamkey(g.away_team)):
                if t:
                    self.by_team.setdefault(t, TeamSeason(t, self.season)).games.append(g)
        for ts in self.by_team.values():
            ts.games.sort(key=lambda g: (g.week if g.week is not None else 99, g.game_id or ""))
        self.last_regular_week = max((g.week for g in self.regular if g.week is not None), default=None)

    # ---------------------------------------------------------------- regular season
    def schedule_complete_through(self, team: str, week: int) -> tuple[bool, str | None, dict]:
        """A team plays every week of the regular season except exactly one bye, so the count of scheduled
        games through week W is W or W-1 -- any other count means the schedule text is truncated or filtered."""
        ts = self.by_team.get(team)
        if ts is None or not ts.games:
            return False, R_NO_SCHEDULE, {"team": team, "season": self.season}
        w = min(week, self.last_regular_week) if self.last_regular_week else week
        n = len(ts.through(w))
        ev = {"weeks_counted": w, "games_scheduled_through_week": n, "expected": [w - 1, w],
              "last_regular_week_in_schedule": self.last_regular_week}
        if n not in (w, w - 1):
            return False, f"{R_SCHEDULE_INCOMPLETE}: {n} games listed through week {w}, expected {w - 1} or {w}", ev
        return True, None, ev

    # ---------------------------------------------------------------- postseason bracket
    def bracket(self) -> dict:
        """Qualification and division winners read back off the league's own bracket."""
        post = self.postseason
        participants, wc_hosts, wc_teams, neutral_wc = set(), set(), set(), []
        for g in post:
            h, a = _teamkey(g.home_team), _teamkey(g.away_team)
            participants.update({h, a})
            if (g.game_type or "").upper() in WILD_CARD:
                loc = (self.locations.get(g.game_id) or "").strip().lower()
                if loc and loc != "home":
                    neutral_wc.append(g.game_id)
                wc_hosts.add(h)
                wc_teams.update({h, a})
        byes = participants - wc_teams
        winners = wc_hosts | byes
        unknown = sorted(t for t in participants if t not in TEAM_CONFERENCE)
        by_conf: dict = {}
        for t in participants:
            by_conf.setdefault(TEAM_CONFERENCE.get(t, "?"), set()).add(t)
        win_by_conf: dict = {}
        for t in winners:
            win_by_conf.setdefault(TEAM_CONFERENCE.get(t, "?"), set()).add(t)
        ev = {"season": self.season, "postseason_games": len(post), "participants": sorted(participants),
              "wild_card_hosts": sorted(wc_hosts), "bye_teams": sorted(byes), "derived_division_winners": sorted(winners),
              "participants_by_conference": {c: sorted(v) for c, v in sorted(by_conf.items())},
              "division_winners_by_conference": {c: sorted(v) for c, v in sorted(win_by_conf.items())},
              "neutral_site_wild_card_games": neutral_wc, "unknown_teams": unknown,
              "derivation": "seeds 1-4 of each conference are its division winners; the wild-card round is played at the higher seed's home field, so seeds 1-4 == {wild-card hosts} + {bye teams}"}
        # ---- structural completeness
        qual_ok, qual_why = True, None
        if len(participants) not in VALID_PARTICIPANT_COUNTS:
            qual_ok, qual_why = False, f"{R_BRACKET_INCOMPLETE}: {len(participants)} participants, expected one of {list(VALID_PARTICIPANT_COUNTS)}"
        elif unknown:
            qual_ok, qual_why = False, f"{R_UNKNOWN_TEAM}: {unknown}"
        elif sorted(len(v) for v in by_conf.values()) != [len(participants) // 2, len(participants) // 2]:
            qual_ok, qual_why = False, f"{R_BRACKET_INCOMPLETE}: participants are not split evenly by conference"
        div_ok, div_why = qual_ok, qual_why
        if div_ok:
            if neutral_wc:
                div_ok, div_why = False, f"wild-card game(s) at a neutral site ({neutral_wc}): the host is not proof of the higher seed"
            elif len(winners) != DIVISION_WINNERS_TOTAL:
                div_ok, div_why = False, f"{R_BRACKET_INCOMPLETE}: {len(winners)} division winners derived, expected {DIVISION_WINNERS_TOTAL}"
            elif any(len(v) != DIVISION_WINNERS_PER_CONFERENCE for v in win_by_conf.values()) or len(win_by_conf) != 2:
                div_ok, div_why = False, f"{R_BRACKET_INCOMPLETE}: division winners are not {DIVISION_WINNERS_PER_CONFERENCE} per conference"
            elif len({TEAM_DIVISION.get(t) for t in winners}) != DIVISION_WINNERS_TOTAL:
                div_ok, div_why = False, f"{R_BRACKET_CONTRADICTS}: two derived winners share a division"
        if div_ok:
            bad = self._records_contradict(winners)
            if bad:
                div_ok, div_why = False, f"{R_BRACKET_CONTRADICTS}: {bad}"
        ev.update(qualification_complete=qual_ok, qualification_reason=qual_why,
                  division_winners_complete=div_ok, division_reason=div_why)
        return ev

    def _records_contradict(self, winners) -> str | None:
        """A division winner is at worst tied for the best W-L-T in its own division. If it is beaten outright
        the bracket was misread -- say so rather than settling something wrong."""
        pts = {}
        for team, ts in self.by_team.items():
            r = ts.record_through(self.last_regular_week or 99)
            if r["pending"]:
                return None                                      # regular season unfinished: no record check possible
            pts[team] = (r["wins"] + 0.5 * r["ties"], r["final"])
        for w in winners:
            div = TEAM_DIVISION.get(w)
            mine = pts.get(w)
            if div is None or mine is None:
                return None
            for rival in DIVISIONS[div]:
                other = pts.get(rival)
                if other is None:
                    return None
                if other[0] > mine[0]:
                    return f"{w} is the derived {div} winner but {rival} finished with a better record ({other[0]:g} vs {mine[0]:g})"
        return None


# ---------------------------------------------------------------------------------------------- settlement
def week_from_question(q: dict) -> int | None:
    """TEAM_WINS_BY_WEEK carries the week in the question's notes as `through_week=N`."""
    for n in (q.get("notes") or ()):
        s = str(n)
        if s.startswith("through_week="):
            try:
                return int(s.split("=", 1)[1])
            except ValueError:
                return None
    return None


def _compare(x: float, q: dict):
    op, k = q.get("op"), q.get("k")
    if q.get("kind") == "EVENT" and q.get("event") == "EXACT_WINS":
        return (x == k) if k is not None else None
    if k is None or op not in (">=", ">", "<=", "<"):
        return None
    return {">=": x >= k, ">": x > k, "<=": x <= k, "<": x < k}[op]


def settle_wins_through_week(team: str, season: int, q: dict, ledger: SeasonLedger) -> dict:
    """`wins through week W >= K`, settled as soon as the answer cannot change.

    The final win total lies in [wins_now, wins_now + half-credit for ties + every game still to play]. The
    comparison is monotone in the win total, so evaluating it at both ends of that interval decides it: equal
    at both ends means the answer is already fixed whatever happens, different means it is genuinely open.
    """
    team = _teamkey(team)
    week = week_from_question(q)
    if week is None:
        return {"status": "REFUSED", "reason": R_NO_WEEK, "evidence": {"question_notes": list(q.get("notes") or ())}}
    if team not in TEAM_DIVISION:
        return {"status": "REFUSED", "reason": f"{R_UNKNOWN_TEAM}: {team!r}", "evidence": {}}
    ok, why, sched_ev = ledger.schedule_complete_through(team, week)
    if not ok:
        return {"status": "REFUSED", "reason": why, "evidence": sched_ev}
    ts = ledger.by_team[team]
    w = min(week, ledger.last_regular_week) if ledger.last_regular_week else week
    r = ts.record_through(w)
    lo = float(r["wins"])                                     # ties worth nothing, every pending game lost
    hi = float(r["wins"]) + 0.5 * r["ties"] + r["pending"]     # ties worth half, every pending game won
    ev = {**r, **sched_ev, "win_total_lower_bound": lo, "win_total_upper_bound": hi,
          "tie_readings": ["a tie is not a win", "a tie is half a win"], "rule_version": SEASON_SETTLE_VERSION,
          "source": "nflverse schedules/games.csv regular-season finals"}
    a, b = _compare(lo, q), _compare(hi, q)
    if a is None or b is None:
        return {"status": "REFUSED", "reason": f"question is not a usable comparison (op={q.get('op')!r}, k={q.get('k')!r})", "evidence": ev}
    if a != b:
        if r["pending"]:
            return {"status": "REFUSED", "reason": f"{R_GAMES_PENDING}: {r['pending']} of {r['scheduled']} through week {w}", "evidence": ev}
        return {"status": "REFUSED", "reason": f"{R_TIE_AMBIGUOUS}: {r['ties']} tie(s); the two readings disagree", "evidence": ev}
    return {"status": "SETTLED", "settled_yes": 1.0 if a else 0.0,
            "reason": f"wins through week {w} in [{lo:g}, {hi:g}] under both tie readings; {'YES' if a else 'NO'} either way",
            "evidence": ev}


def settle_make_playoffs(team: str, season: int, ledger: SeasonLedger) -> dict:
    team = _teamkey(team)
    if team not in TEAM_DIVISION:
        return {"status": "REFUSED", "reason": f"{R_UNKNOWN_TEAM}: {team!r}", "evidence": {}}
    b = ledger.bracket()
    ev = {**b, "rule_version": SEASON_SETTLE_VERSION, "source": "nflverse schedules/games.csv postseason games"}
    if team in set(b["participants"]):
        games = [g.game_id for g in ledger.postseason if team in (_teamkey(g.home_team), _teamkey(g.away_team))]
        return {"status": "SETTLED", "settled_yes": 1.0, "reason": f"{team} appears in the postseason bracket ({len(games)} game(s))",
                "evidence": {**ev, "team_postseason_games": games}}
    if not b["qualification_complete"]:
        return {"status": "REFUSED", "reason": b["qualification_reason"] or R_BRACKET_INCOMPLETE, "evidence": ev}
    return {"status": "SETTLED", "settled_yes": 0.0,
            "reason": f"{team} is absent from a complete {len(b['participants'])}-team postseason bracket", "evidence": ev}


def settle_division_winner(team: str, season: int, ledger: SeasonLedger) -> dict:
    team = _teamkey(team)
    if team not in TEAM_DIVISION:
        return {"status": "REFUSED", "reason": f"{R_UNKNOWN_TEAM}: {team!r}", "evidence": {}}
    b = ledger.bracket()
    ev = {**b, "rule_version": SEASON_SETTLE_VERSION, "team_division": TEAM_DIVISION[team],
          "source": "nflverse schedules/games.csv postseason bracket (seeds 1-4 are the division winners)"}
    if not b["division_winners_complete"]:
        return {"status": "REFUSED", "reason": b["division_reason"] or R_BRACKET_INCOMPLETE, "evidence": ev}
    won = team in set(b["derived_division_winners"])
    return {"status": "SETTLED", "settled_yes": 1.0 if won else 0.0,
            "reason": f"{team} {'is' if won else 'is not'} among the eight derived division winners", "evidence": ev}
