"""Contract -> Question: the generic threshold / range / event grammar every engine prices against.

WHY A SEPARATE LAYER
--------------------
The incumbent classifier (`nfl_edge/kalshi/classifier.py`) extracts family, threshold, operator and -- for the
winning-margin family -- `range_lo` / `range_hi`. The capture row schema then DROPS the range bounds, which is
exactly why 105 open margin-bucket contracts were captured, classified and never priced. This module is the fix
in the general form the mission asks for: every contract becomes a `Question` whose comparison is one of

    THRESHOLD   stat  op  k                (op in >=, >, <=, <)
    RANGE       lo <= stat <= hi           (inclusive both ends; hi None = open above)
    EVENT       a named discrete outcome   (team wins, tie, first to N, no touchdown, ...)
    COMPOSITE   every leg must be YES      (half/full double results, pre-packaged parlays)

and the statistic is a named FUNCTION of an engine's latent state (`margin:HOME`, `total`, `team_points:SEA`,
`min_team_points`, `abs_margin`, `receiving_yards`, `season_wins`, ...). The engine that owns the state answers
the question; the question never knows how.

EVIDENCE DISCIPLINE
-------------------
A question carries `semantic_confidence`:

    PROVEN     the rule is pinned by the contract's own rules text (or by the exhaustively verified ticker
               grammar of the family) AND the family catalog marks the (family, period) as proven
    LIKELY     the rule follows a verified grammar but this record carried no rules text / custom strike to
               confirm it (ticker-only parse), or the catalog marks the family LIKELY
    AMBIGUOUS  two sources of the rule disagree, or a boundary could be read two ways
    UNKNOWN    no rule could be extracted

Two independent readings are compared whenever both exist (ticker suffix vs custom strike vs rules text) and
a disagreement is AMBIGUOUS, never resolved by preference. The winning-margin buckets are the worked example:
the 2026 structure (`-KC7TO14`, custom strike "7 to 14", rules "between 7 and 14 points") and the 2025 archive
structure (`strike_type=between`, floor 7, cap 10, "either team", "(inclusive)") are both parsed, and both are
checked for partition consistency by `tests/test_semantics_questions.py`.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict

from nfl_edge.kalshi.classifier import KALSHI_TEAM_CODES, KALSHI_TO_NFLVERSE, MarketSemantics, classify

PROVEN, LIKELY, AMBIGUOUS, UNKNOWN = "PROVEN", "LIKELY", "AMBIGUOUS", "UNKNOWN"
THRESHOLD, RANGE, EVENT, COMPOSITE = "THRESHOLD", "RANGE", "EVENT", "COMPOSITE"

# engines
GAME, PERIOD, PLAYER, SEASON, JOINT, NONE = "GAME", "PERIOD", "PLAYER", "SEASON", "JOINT", "NONE"

_ORDER = {PROVEN: 3, LIKELY: 2, AMBIGUOUS: 1, UNKNOWN: 0}


def weakest(*confs):
    return min((c for c in confs if c is not None), key=lambda c: _ORDER[c], default=UNKNOWN)


@dataclass(frozen=True)
class Question:
    kind: str                              # THRESHOLD | RANGE | EVENT | COMPOSITE
    engine: str                            # GAME | PERIOD | PLAYER | SEASON | JOINT | NONE
    stat: str | None = None                # margin | total | team_points | min_team_points | abs_margin | <player stat> | ...
    period: str = "FULL"                   # FULL | 1H | 2H | 1Q..4Q | SEASON | WEEK
    subject: str | None = None             # nflverse team code, GSIS player id (resolved later) or None
    subject_kind: str | None = None        # team | player | none
    op: str | None = None                  # >= | > | <= | <
    k: float | None = None
    lo: float | None = None
    hi: float | None = None                # None = open above
    event: str | None = None               # WIN | TIE | RACE_FIRST | RACE_NONE | FIRST_TD_TEAM | NO_TD | ...
    legs: tuple = ()
    semantic_confidence: str = UNKNOWN
    overtime: str | None = None            # INCLUDED | EXCLUDED | NA
    tie_rule: str | None = None            # HALF_PAYOUT | TIE_LEG_YES | NA
    notes: tuple = ()

    def to_dict(self):
        d = asdict(self)
        d["legs"] = [l.to_dict() if isinstance(l, Question) else l for l in self.legs]
        d["notes"] = list(self.notes)
        return d

    @property
    def priceable(self) -> bool:
        return self.semantic_confidence == PROVEN and self.engine != NONE


# ------------------------------------------------------------------------------------------------------ helpers
_MARGIN_RANGE_TICKER = re.compile(r"^([A-Z]{2,3})(\d+)TO(\d+)$")
_MARGIN_PLUS_TICKER = re.compile(r"^([A-Z]{2,3})(\d+)PLUS$")
_WM_TEXT_RANGE = re.compile(r"^(\d+)\s*to\s*(\d+)$", re.I)
_WM_TEXT_PLUS = re.compile(r"^(\d+)\s*(?:\+|or more)$", re.I)
_RULES_BETWEEN = re.compile(r"between (\d+) and (\d+) points", re.I)
_RULES_ATLEAST = re.compile(r"of at least (\d+) points", re.I)
_RULES_EXACT0 = re.compile(r"exactly 0 points", re.I)
_RULES_INCLUSIVE = re.compile(r"\(inclusive\)", re.I)
_RULES_EITHER_RANGE = re.compile(r"winning margin (?:of )?between (\d+) (?:to|and) (\d+)", re.I)
_RULES_EITHER_ATLEAST = re.compile(r"win by at least (\d+)", re.I)


def _team(code):
    return KALSHI_TO_NFLVERSE.get(code, code) if code else None


def _margin_bucket_readings(sem: MarketSemantics, m: dict) -> list:
    """Every independent reading of a winning-margin contract's bounds: (source, team_kalshi, lo, hi, is_tie)."""
    readings = []
    suffix = sem.ticker[len(sem.event_ticker) + 1:] if sem.ticker.startswith(sem.event_ticker + "-") else ""
    teams = [t for t in (sem.away_kalshi, sem.home_kalshi) if t]
    # 1. ticker grammar (2026 structure)
    if suffix == "TIE":
        readings.append(("ticker", None, 0.0, 0.0, True))
    else:
        mm = _MARGIN_RANGE_TICKER.match(suffix)
        if mm and mm.group(1) in teams:
            readings.append(("ticker", mm.group(1), float(mm.group(2)), float(mm.group(3)), False))
        mm = _MARGIN_PLUS_TICKER.match(suffix)
        if mm and mm.group(1) in teams:
            readings.append(("ticker", mm.group(1), float(mm.group(2)), None, False))
    cs = m.get("custom_strike") if isinstance(m.get("custom_strike"), dict) else {}
    # 2. custom strike text (2026 structure)
    wm = (cs or {}).get("Winning Margin")
    if isinstance(wm, str):
        t = next((t for t in sorted(teams, key=len, reverse=True) if suffix.startswith(t)), None)
        if wm.strip().lower() == "tie":
            readings.append(("custom_strike", None, 0.0, 0.0, True))
        else:
            r = _WM_TEXT_RANGE.match(wm.strip())
            p = _WM_TEXT_PLUS.match(wm.strip())
            if r:
                readings.append(("custom_strike", t, float(r.group(1)), float(r.group(2)), False))
            elif p:
                readings.append(("custom_strike", t, float(p.group(1)), None, False))
    # 3. rules text (both structures)
    rules = m.get("rules_primary") or ""
    if rules:
        t = next((t for t in sorted(teams, key=len, reverse=True) if suffix.startswith(t)), None)
        if _RULES_EXACT0.search(rules):
            readings.append(("rules", None, 0.0, 0.0, True))
        elif _RULES_BETWEEN.search(rules):
            r = _RULES_BETWEEN.search(rules)
            readings.append(("rules", t, float(r.group(1)), float(r.group(2)), False))
        elif _RULES_ATLEAST.search(rules):
            r = _RULES_ATLEAST.search(rules)
            readings.append(("rules", t, float(r.group(1)), None, False))
        elif _RULES_EITHER_RANGE.search(rules):
            r = _RULES_EITHER_RANGE.search(rules)
            readings.append(("rules", "EITHER", float(r.group(1)), float(r.group(2)), False))
        elif _RULES_EITHER_ATLEAST.search(rules):
            r = _RULES_EITHER_ATLEAST.search(rules)
            readings.append(("rules", "EITHER", float(r.group(1)), None, False))
    # 4. strike fields (2025 structure: strike_type=between, floor, cap; cap 100 == open)
    if (m.get("strike_type") == "between") and m.get("floor_strike") is not None:
        lo = float(m["floor_strike"])
        cap = m.get("cap_strike")
        hi = None if cap is None or float(cap) >= 99 else float(cap)
        readings.append(("strike", "EITHER", lo, hi, False))
    return readings


def _margin_bucket_question(sem: MarketSemantics, m: dict) -> Question:
    readings = _margin_bucket_readings(sem, m)
    notes = []
    if not readings:
        return Question(RANGE, GAME, "margin", "FULL", semantic_confidence=UNKNOWN, notes=("no margin-bucket reading",))
    keys = {(r[1], r[2], r[3], r[4]) for r in readings}
    sources = {r[0] for r in readings}
    if len(keys) != 1:
        return Question(RANGE, GAME, "margin", "FULL", semantic_confidence=AMBIGUOUS,
                        notes=tuple(f"{r[0]}: team={r[1]} lo={r[2]} hi={r[3]} tie={r[4]}" for r in readings))
    team, lo, hi, is_tie = next(iter(keys))
    # confidence: proven when the rules text (or the exchange's own strike fields) confirmed the grammar;
    # a ticker-only or custom-strike-only reading is a verified grammar without this record's own evidence.
    conf = PROVEN if ("rules" in sources or "strike" in sources) else LIKELY
    if conf == LIKELY:
        notes.append("bounds read from the ticker/custom-strike grammar only; rules text not on this record")
    if is_tie:
        return Question(EVENT, GAME, "margin", "FULL", event="TIE", semantic_confidence=conf, overtime="INCLUDED",
                        tie_rule="TIE_LEG_YES", notes=tuple(notes))
    if team == "EITHER":
        return Question(RANGE, GAME, "abs_margin", "FULL", subject=None, subject_kind="none", lo=lo, hi=hi,
                        semantic_confidence=conf, overtime="INCLUDED", tie_rule="TIE_LEG_YES",
                        notes=tuple(notes + ["either team; inclusive bounds"]))
    if team is None:
        return Question(RANGE, GAME, "margin", "FULL", semantic_confidence=AMBIGUOUS, lo=lo, hi=hi,
                        notes=("margin bucket without a subject team",))
    return Question(RANGE, GAME, "margin", "FULL", subject=_team(team), subject_kind="team", lo=lo, hi=hi,
                    semantic_confidence=conf, overtime="INCLUDED", tie_rule="TIE_LEG_YES",
                    notes=tuple(notes + ["inclusive bounds; buckets 1-6 / 7-14 / 15+ partition the positive margins"]))


def _period_of(sem: MarketSemantics) -> str:
    return sem.period or "FULL"


def _ot(period: str) -> str:
    if period == "FULL":
        return "INCLUDED"
    if period in ("1H", "1Q", "2Q", "3Q"):
        return "NA"
    return "EXCLUDED"         # 2H / 4Q: only the period's own points, overtime is not part of the 2nd half


def _threshold_conf(sem: MarketSemantics) -> str:
    return PROVEN if sem.confidence >= 0.95 else (LIKELY if sem.confidence >= 0.85 else AMBIGUOUS)


def _half_full_question(sem: MarketSemantics, m: dict) -> Question:
    cs = m.get("custom_strike") if isinstance(m.get("custom_strike"), dict) else {}
    r1, r2 = (cs or {}).get("1st Half Result"), (cs or {}).get("Fulltime Result")
    if not r1 or not r2:
        return Question(COMPOSITE, PERIOD, None, "1H", semantic_confidence=UNKNOWN, notes=("half/full legs not on this record",))
    teams = {k: v for k, v in ((sem.away_kalshi, sem.away_team), (sem.home_kalshi, sem.home_team)) if k}
    title_names = {}
    # the custom strike names cities ("Denver wins 1st Half"); the ticker suffix carries the codes (DENKC, TIEKC)
    suffix = sem.ticker[len(sem.event_ticker) + 1:]
    codes = []
    rest = suffix
    for _ in range(2):
        if rest.startswith("TIE"):
            codes.append("TIE"); rest = rest[3:]; continue
        t = next((t for t in sorted(teams, key=len, reverse=True) if t and rest.startswith(t)), None)
        if t is None:
            break
        codes.append(t); rest = rest[len(t):]
    if len(codes) != 2 or rest:
        return Question(COMPOSITE, PERIOD, None, "1H", semantic_confidence=AMBIGUOUS, notes=(f"half/full suffix {suffix!r} not parsed",))
    def leg(code, period):
        if code == "TIE":
            return Question(EVENT, PERIOD if period == "1H" else GAME, "margin", period, event="TIE",
                            semantic_confidence=PROVEN, overtime=_ot(period), tie_rule="TIE_LEG_YES")
        return Question(EVENT, PERIOD if period == "1H" else GAME, "margin", period, subject=teams[code], subject_kind="team",
                        event="WIN", semantic_confidence=PROVEN, overtime=_ot(period), tie_rule="TIE_LEG_YES")
    # cross-check the custom strike text against the codes: a tie leg must say Tie, a team leg must not
    ok1 = ("tie" in r1.lower()) == (codes[0] == "TIE")
    ok2 = ("tie" in r2.lower()) == (codes[1] == "TIE")
    conf = PROVEN if (ok1 and ok2) else AMBIGUOUS
    return Question(COMPOSITE, JOINT, None, "1H", legs=(leg(codes[0], "1H"), leg(codes[1], "FULL")),
                    semantic_confidence=conf, overtime="INCLUDED", tie_rule="TIE_LEG_YES",
                    notes=("both legs must be YES; the full-game leg includes overtime and a tied game pays the TIE leg, not $0.50",))


def _player_stat_question(sem: MarketSemantics, m: dict) -> Question:
    conf = PROVEN if (sem.threshold is not None and sem.operator == ">=" and sem.player_kalshi_id) else (
        LIKELY if sem.threshold is not None and sem.operator == ">=" else AMBIGUOUS)
    notes = ["YES iff stat >= K (integer ladder; floor K-0.5, no push); active-never-snap settles at pregame fair price; inactive settles NO"]
    stat = sem.stat
    if stat == "touchdowns" and sem.threshold is None:
        return Question(THRESHOLD, PLAYER, stat, "FULL", subject=sem.player_kalshi_id, subject_kind="player", op=">=", k=1.0,
                        semantic_confidence=LIKELY, overtime="INCLUDED", notes=("anytime TD without a numeric strike: K=1 assumed",))
    return Question(THRESHOLD, PLAYER, stat, _period_of(sem), subject=sem.player_kalshi_id, subject_kind="player",
                    op=sem.operator, k=sem.threshold, semantic_confidence=conf, overtime="INCLUDED", notes=tuple(notes))


def _mve_legs(m: dict) -> list:
    """Pre-packaged parlay legs from the exchange's own `custom_strike` (Associated Markets / Sides)."""
    cs = m.get("custom_strike") if isinstance(m.get("custom_strike"), dict) else {}
    mk = (cs or {}).get("Associated Markets")
    sides = (cs or {}).get("Associated Market Sides")
    if not mk or not sides:
        legs = m.get("mve_selected_legs")
        if isinstance(legs, list) and legs:
            out = []
            for l in legs:
                if isinstance(l, dict) and l.get("market_ticker"):
                    out.append((l["market_ticker"], (l.get("side") or "yes").lower()))
            return out
        return []
    tickers = [t.strip() for t in str(mk).split(",")]
    ss = [s.strip().lower() for s in str(sides).split(",")]
    if len(tickers) != len(ss):
        return []
    out = []
    for t, s in zip(tickers, ss):
        # the exchange sometimes doubles the series prefix ("KXNFLTOTAL-KXNFLTOTAL-25DEC08PHILAC-41")
        parts = t.split("-")
        if len(parts) >= 2 and parts[0] == parts[1]:
            t = "-".join(parts[1:])
        out.append((t, s))
    return out


def _parlay_question(sem: MarketSemantics, m: dict) -> Question:
    legs = _mve_legs(m)
    if not legs:
        return Question(COMPOSITE, JOINT, None, "FULL", semantic_confidence=UNKNOWN, notes=("no parsable legs on this record",))
    qs = []
    for ticker, side in legs:
        # the leg's strike is in its ticker suffix (K); the exchange lists ladder legs as floor K-0.5, strike "greater"
        k = None
        mm = re.search(r"-(\d+)$", ticker)
        if mm:
            k = float(mm.group(1))
        leg_market = {"ticker": ticker, "event_ticker": ticker.rsplit("-", 1)[0], "series_ticker": ticker.split("-")[0],
                      "title": "", "strike_type": "greater" if k is not None else None,
                      "floor_strike": (k - 0.5) if k is not None else None}
        leg_sem = classify(leg_market)
        lq = contract_question(leg_sem, leg_market)
        if side == "no":
            lq = Question(lq.kind, lq.engine, lq.stat, lq.period, lq.subject, lq.subject_kind, lq.op, lq.k, lq.lo, lq.hi, lq.event,
                          lq.legs, weakest(lq.semantic_confidence, LIKELY), lq.overtime, lq.tie_rule,
                          lq.notes + ("NO side of the leg: the complement",))
            lq = _negate(lq)
        qs.append(lq)
    conf = weakest(*[q.semantic_confidence for q in qs])
    return Question(COMPOSITE, JOINT, None, "FULL", legs=tuple(qs), semantic_confidence=conf,
                    notes=("every leg must resolve YES; legs share a game and are NOT independent",))


def _negate(q: Question) -> Question:
    if q.kind == THRESHOLD and q.op in (">=", ">", "<=", "<"):
        flip = {">=": "<", ">": "<=", "<=": ">", "<": ">="}[q.op]
        return Question(q.kind, q.engine, q.stat, q.period, q.subject, q.subject_kind, flip, q.k, None, None, None, (),
                        q.semantic_confidence, q.overtime, q.tie_rule, q.notes)
    return Question(q.kind, q.engine, q.stat, q.period, q.subject, q.subject_kind, q.op, q.k, q.lo, q.hi,
                    f"NOT_{q.event}" if q.event else None, q.legs, weakest(q.semantic_confidence, AMBIGUOUS),
                    q.overtime, q.tie_rule, q.notes + ("negation of a non-threshold leg is not a proven rule",))


# ------------------------------------------------------------------------------------------------------ main
def contract_question(sem: MarketSemantics, m: dict | None = None) -> Question:
    """The question a classified contract asks, with its engine and its semantic confidence.

    `m` is the raw market record when available (rules text, custom strike, strike fields); without it the
    reading is from the ticker grammar and the classifier output only, which caps confidence at LIKELY for the
    families whose bounds live outside the ticker.
    """
    m = m or {}
    fam, period = sem.family, _period_of(sem)
    if fam == "GAME_WINNER":
        if sem.is_tie_leg:
            return Question(EVENT, GAME, "margin", "FULL", event="TIE", semantic_confidence=PROVEN, overtime="INCLUDED", tie_rule="HALF_PAYOUT",
                            notes=("game-winner TIE leg",))
        return Question(EVENT, GAME, "margin", "FULL", subject=sem.team, subject_kind="team", event="WIN",
                        semantic_confidence=PROVEN if sem.team else AMBIGUOUS, overtime="INCLUDED", tie_rule="HALF_PAYOUT",
                        notes=("tie pays $0.50 to both sides",))
    if fam == "PERIOD_WINNER":
        eng = PERIOD
        if sem.is_tie_leg:
            return Question(EVENT, eng, "margin", period, event="TIE", semantic_confidence=PROVEN, overtime=_ot(period), tie_rule="TIE_LEG_YES")
        return Question(EVENT, eng, "margin", period, subject=sem.team, subject_kind="team", event="WIN",
                        semantic_confidence=PROVEN if sem.team else AMBIGUOUS, overtime=_ot(period), tie_rule="TIE_LEG_YES",
                        notes=("tied period: team strikes NO, TIE strike YES",))
    if fam == "SPREAD":
        eng = GAME if period == "FULL" else PERIOD
        conf = PROVEN if (sem.team and sem.floor_strike is not None and sem.strike_type in ("greater", None)) else AMBIGUOUS
        if sem.floor_strike is not None and float(sem.floor_strike) % 1 == 0:
            conf = weakest(conf, LIKELY)          # integer floor with "more than": exactly-the-floor loses, but pushes are unusual here
        return Question(THRESHOLD, eng, "margin", period, subject=sem.team, subject_kind="team", op=">", k=sem.floor_strike,
                        semantic_confidence=conf, overtime=_ot(period), tie_rule="NA",
                        notes=("YES iff team margin > floor (x.5 floor: no push)",))
    if fam == "TOTAL":
        eng = GAME if period == "FULL" else PERIOD
        return Question(THRESHOLD, eng, "total", period, op=">=", k=sem.threshold,
                        semantic_confidence=PROVEN if sem.threshold is not None else AMBIGUOUS, overtime=_ot(period), tie_rule="NA",
                        notes=("YES iff total points >= K (floor K-0.5)",))
    if fam == "TEAM_TOTAL":
        eng = GAME if period == "FULL" else PERIOD
        return Question(THRESHOLD, eng, "team_points", period, subject=sem.team, subject_kind="team", op=">=", k=sem.threshold,
                        semantic_confidence=PROVEN if (sem.team and sem.threshold is not None) else AMBIGUOUS, overtime=_ot(period), tie_rule="NA")
    if fam == "WIN_MARGIN_BUCKET":
        return _margin_bucket_question(sem, m)
    if fam == "BOTH_TEAMS_SCORE_N":
        return Question(THRESHOLD, GAME, "min_team_points", "FULL", op=">=", k=sem.threshold,
                        semantic_confidence=PROVEN if sem.threshold is not None else AMBIGUOUS, overtime="INCLUDED", tie_rule="NA",
                        notes=("both teams score >= K  <=>  min(team points) >= K",))
    if fam == "BOTH_TEAMS_SCORE":
        return Question(EVENT, PERIOD, "min_team_points", period, event="BOTH_SCORE", semantic_confidence=PROVEN, overtime=_ot(period),
                        notes=("both teams score at least one point in the period",))
    if fam == "TOTAL_TD":
        return Question(THRESHOLD, GAME, "total_touchdowns", "FULL", op=">=", k=sem.threshold,
                        semantic_confidence=LIKELY if sem.threshold is not None else AMBIGUOUS, overtime="INCLUDED",
                        notes=("all touchdowns by both teams incl. overtime; count is not a function of the final score",))
    if fam == "RACE_TO_N":
        if sem.is_none_leg:
            return Question(EVENT, GAME, "race", "FULL", event="RACE_NONE", k=sem.threshold, semantic_confidence=PROVEN, overtime="INCLUDED",
                            notes=("neither team reaches N",))
        return Question(EVENT, GAME, "race", "FULL", subject=sem.team, subject_kind="team", event="RACE_FIRST", k=sem.threshold,
                        semantic_confidence=PROVEN if (sem.team and sem.threshold) else AMBIGUOUS, overtime="INCLUDED",
                        notes=("first to N points, incl. overtime; needs the scoring ORDER, not the final score",))
    if fam == "FIRST_TD_TEAM":
        if sem.player_kalshi_id:
            return Question(EVENT, PLAYER, "first_td", "FULL", subject=sem.player_kalshi_id, subject_kind="player",
                            event="FIRST_TEAM_TD_SCORER", semantic_confidence=LIKELY, overtime="INCLUDED",
                            notes=("player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity",))
        if sem.is_none_leg:
            return Question(EVENT, GAME, "first_td", "FULL", event="NO_TD", semantic_confidence=PROVEN, overtime="INCLUDED")
        return Question(EVENT, GAME, "first_td", "FULL", subject=sem.team, subject_kind="team", event="FIRST_TD_TEAM",
                        semantic_confidence=PROVEN if sem.team else AMBIGUOUS, overtime="INCLUDED",
                        notes=("all touchdowns count incl. defensive/special teams and overtime",))
    if fam in ("FIRST_TD_SCORER", "NEXT_TD_SCORER"):
        if sem.is_none_leg:
            return Question(EVENT, GAME, "first_td", "FULL", event="NO_TD", semantic_confidence=PROVEN, overtime="INCLUDED")
        return Question(EVENT, PLAYER, "first_td", "FULL", subject=sem.player_kalshi_id, subject_kind="player",
                        event="FIRST_TD_SCORER" if fam == "FIRST_TD_SCORER" else "NEXT_TD_SCORER",
                        semantic_confidence=LIKELY if sem.player_kalshi_id else AMBIGUOUS, overtime="INCLUDED",
                        notes=("scoring order; player strikes carry the active/no-snap fair-price clause",))
    if fam == "PLAYER_STAT":
        cs_ = m.get("custom_strike") if isinstance(m.get("custom_strike"), dict) else None
        if cs_ is not None and "football_player" not in cs_ and "football_team" in cs_ and sem.team:
            # a team-level ladder listed under a player-stat series (KXNFLFG "San Francisco: 4+ Field Goals")
            return Question(THRESHOLD, NONE, f"team_{sem.stat}", period, subject=sem.team, subject_kind="team", op=sem.operator, k=sem.threshold,
                            semantic_confidence=LIKELY if sem.threshold is not None else AMBIGUOUS, overtime="INCLUDED",
                            notes=("team-level statistic under a player-stat series; no engine yet",))
        return _player_stat_question(sem, m)
    if fam == "HALF_FULL_RESULT":
        return _half_full_question(sem, m)
    if fam in ("PARLAY", "COMBO"):
        return _parlay_question(sem, m)
    if fam == "SEASON_WINS":
        return Question(THRESHOLD, SEASON, "season_wins", "SEASON", subject=sem.team, subject_kind="team", op=">=", k=sem.threshold,
                        semantic_confidence=LIKELY if (sem.team and sem.threshold is not None) else AMBIGUOUS,
                        notes=("regular-season wins >= K; tie handling (a tie is not a win) LIKELY, not pinned by rules text",))
    if fam == "SEASON_WINS_EXACT":
        return Question(EVENT, SEASON, "season_wins", "SEASON", subject=sem.team, subject_kind="team", event="EXACT_WINS", k=sem.threshold,
                        semantic_confidence=LIKELY if sem.team else AMBIGUOUS)
    if fam == "TEAM_WINS_BY_WEEK":
        wk = next((n for n in sem.notes if n.startswith("through_week=")), None)
        return Question(THRESHOLD, SEASON, "wins_through_week", "SEASON", subject=sem.team, subject_kind="team", op=">=", k=sem.threshold,
                        semantic_confidence=LIKELY if (sem.team and sem.threshold is not None and wk) else AMBIGUOUS,
                        notes=((wk or "week unparsed"),))
    if fam in ("MAKE_PLAYOFFS", "DIVISION_WINNER", "CONFERENCE_WINNER", "SUPER_BOWL_WINNER", "SEASON_SEED") and not sem.team:
        suffix = sem.ticker.rsplit("-", 1)[-1]
        if suffix in KALSHI_TEAM_CODES:
            sem = MarketSemantics(**{**sem.to_dict(), "team_kalshi": suffix, "team": _team(suffix)})
    if fam == "MAKE_PLAYOFFS":
        return Question(EVENT, SEASON, "playoffs", "SEASON", subject=sem.team, subject_kind="team", event="MAKE_PLAYOFFS",
                        semantic_confidence=LIKELY if sem.team else AMBIGUOUS, notes=("tie-breakers approximate",))
    if fam == "DIVISION_WINNER":
        return Question(EVENT, SEASON, "division", "SEASON", subject=sem.team, subject_kind="team", event="DIVISION_WINNER",
                        semantic_confidence=LIKELY if sem.team else AMBIGUOUS, notes=("tie-breakers approximate",))
    if fam == "CONFERENCE_WINNER":
        return Question(EVENT, SEASON, "conference", "SEASON", subject=sem.team, subject_kind="team", event="CONFERENCE_WINNER",
                        semantic_confidence=LIKELY if sem.team else AMBIGUOUS)
    if fam == "SUPER_BOWL_WINNER":
        return Question(EVENT, SEASON, "super_bowl", "SEASON", subject=sem.team, subject_kind="team", event="SUPER_BOWL_WINNER",
                        semantic_confidence=LIKELY if sem.team else AMBIGUOUS)
    if fam == "SEASON_SEED":
        return Question(EVENT, SEASON, "seed", "SEASON", subject=sem.team, subject_kind="team", event="SEED",
                        semantic_confidence=AMBIGUOUS, notes=("seed number and conference must be read from the event ticker; tie-breakers approximate",))
    if fam == "SEASON_PLAYER_STAT":
        return Question(THRESHOLD, NONE, sem.stat, "SEASON", subject=sem.player_kalshi_id, subject_kind="player", op=">=", k=sem.threshold,
                        semantic_confidence=LIKELY if (sem.threshold is not None and sem.player_kalshi_id) else AMBIGUOUS,
                        notes=("season aggregate of a player statistic; no engine yet (needs a games-played model)",))
    if fam in ("TEAM_STAT", "GAME_STAT", "GAME_EVENT", "PLAYER_H2H", "WEEK_LEADER", "SEASON_LEADER",
               "SEASON_FANTASY", "SEASON_PLAYER_SPECIAL", "SEASON_TEAM_EVENT", "SEASON_TEAM_H2H", "SEASON_DIVISION_STAT",
               "SEASON_TEAM_LEADER", "SEASON_MATCHUP", "SUPER_BOWL_MATCHUP", "SEASON_DIVISION_ORDER", "SEASON_SPECIAL",
               "WEEK_EVENT", "PLAYER_AVAILABILITY", "PERIOD_TD", "FIRST_TD_TIME"):
        return Question(EVENT, NONE, sem.stat, period, semantic_confidence=LIKELY if sem.confidence >= 0.6 else UNKNOWN,
                        notes=("family has no engine yet; rule read from the title",))
    if fam in ("AWARD", "DRAFT", "COACH_EVENT", "TRANSACTION_EVENT", "PLAYER_ROLE_EVENT", "NFL_BUSINESS_EVENT", "SUPER_BOWL_EVENT"):
        return Question(EVENT, NONE, None, period, semantic_confidence=LIKELY, notes=("non-football / news event",))
    if fam in ("NOT_NFL", "NOT_NFL_OR_UNKNOWN"):
        return Question(EVENT, NONE, None, period, semantic_confidence=UNKNOWN, notes=("not an NFL contract",))
    return Question(EVENT, NONE, None, period, semantic_confidence=UNKNOWN, notes=(f"family {fam} has no question grammar",))


def question_from_market(m: dict) -> tuple[MarketSemantics, Question]:
    sem = classify(m)
    return sem, contract_question(sem, m)
