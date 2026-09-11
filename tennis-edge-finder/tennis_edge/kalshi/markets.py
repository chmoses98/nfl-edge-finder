"""Parse raw Kalshi tennis market records into canonical payoff definitions.

Everything the payoff needs is recovered from the RAW record (rules_primary, strike fields, ticker,
custom_strike competitor ids). Nothing is inferred from UI labels alone: the rules text is the
contract. A record the parser cannot fully understand yields status UNPARSED with a reason and is
counted by health gate TENNIS-2/3 -- it is never silently dropped.

Verified grammar (165k markets, 2026-09-11 discovery):
  MATCH_WINNER      rules: "If <A> wins the <a> vs <b> professional tennis match in the <year> <competition> <round>
                    after a ball has been played, then ..."; custom_strike.tennis_competitor = Kalshi competitor UUID
  SET_WINNER        "If <A> wins set <n> in the <A> vs <B> professional tennis match in the <comp>, ..." ticker ...-<n>-<CODE>
  EXACT_SET_SCORE   "... by a set score of <x>-<y>" ticker ...-<CODE><x><y>
  GAME_SPREAD       "If the game differential in favor of <A> across the full match is above <line> games in the <A> vs <B> ..."  floor_strike=line
  TOTAL_GAMES       "If the number of completed games in the full match is above <line> in the <A> vs <B> ..." floor_strike
  TOTAL_SETS        "If above <line> sets are played in the <A> vs <B> ..." floor_strike
  SET_SPREAD        "If <A> wins by over <line> sets in the <A> vs <B> ..." floor_strike
  PLAYER_ACES       "If <A> records at least <n> total match aces in the full match of the <A> vs <B> ..."
  GAME_WINNER_INPLAY "If <A> wins game <g> in set <s> in the <A> vs <B> ..."
  TOURNAMENT_WINNER "If <A> wins the <year> <competition> professional tennis tournament" / "... Championship"
  ROUND_ADVANCE     "If <A> qualifies for the <Round> at the <year> <competition> tennis tournament"
Doubles competitors appear as "<P1> / <P2>" with custom_strike.tennis_doubles_competitor.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict

from tennis_edge.kalshi.families import SERIES, FAMILIES

ROUND_WORDS = {
    "final": "F", "finals": "F", "semifinal": "SF", "semifinals": "SF", "quarterfinal": "QF", "quarterfinals": "QF",
    "round of 16": "R16", "round of 32": "R32", "round of 64": "R64", "round of 128": "R128", "round of 8": "QF",
    "round of 4": "SF", "round of 2": "F", "1st round": "R1", "2nd round": "R2", "3rd round": "R3", "4th round": "R4",
    "round 1": "R1", "round 2": "R2", "round 3": "R3", "round 4": "R4", "round robin": "RR", "group stage": "RR",
    "qualification round 1": "Q1", "qualification round 2": "Q2", "qualification round 3": "Q3", "qualification final": "Q3",
    "qualifying round 1": "Q1", "qualifying round 2": "Q2", "qualifying round 3": "Q3", "round": "UNK",
}
_ROUND_RE = re.compile(r"(?P<comp>.*?)\s*(?P<round>" + "|".join(sorted((re.escape(k) for k in ROUND_WORDS), key=len, reverse=True)) + r")\s*$", re.I)

_VS_MATCH = r"(?P<a>.+?) vs (?P<b>.+?) (?:women's |men's )?(?:professional|exhibition) tennis match in the (?P<year>\d{4}) (?P<comp>.+?)"
RE_MATCH_WINNER = re.compile(r"^If (?P<who>.+?) wins the " + _VS_MATCH + r"(?: after a ball has been played)?, then the market resolves to Yes", re.I)
RE_SET_WINNER = re.compile(r"^If (?P<who>.+?) wins set (?P<n>\d+) in the " + _VS_MATCH + r", then", re.I)
RE_EXACT = re.compile(r"^If (?P<who>.+?) wins the " + _VS_MATCH + r" by a set score of (?P<x>\d)-(?P<y>\d), then", re.I)
RE_GSPREAD = re.compile(r"^If the game differential in favor of (?P<who>.+?) across the full match is above (?P<line>[\d.]+) games in the " + _VS_MATCH + r", then", re.I)
RE_GTOTAL = re.compile(r"^If the number of completed games in the full match is above (?P<line>[\d.]+) in the " + _VS_MATCH + r", then", re.I)
RE_STOTAL = re.compile(r"^If above (?P<line>[\d.]+) sets are played in the " + _VS_MATCH + r", then", re.I)
RE_SSPREAD = re.compile(r"^If (?P<who>.+?) wins by over (?P<line>[\d.]+) sets in the " + _VS_MATCH + r", then", re.I)
RE_ACES = re.compile(r"^If (?P<who>.+?) records at least (?P<n>\d+) total match aces in the full match of the " + _VS_MATCH + r", then", re.I)
RE_GAME_INPLAY = re.compile(r"^If (?P<who>.+?) wins game (?P<g>\d+) in set (?P<s>\d+) in the " + _VS_MATCH + r", then", re.I)
RE_TIEBREAK = re.compile(r"^If (?:a|any) tiebreak (?:occurs|is played) in the " + _VS_MATCH, re.I)
# legacy (2025) grammars, still present in the archive tier
RE_MATCH_SCHEDULED = re.compile(r"^If (?P<who>.+?) wins the (?P<a>.+?) vs (?P<b>.+?) (?:women's |men's )?(?:professional|exhibition) tennis match originally scheduled (?:for|on) (?P<date>[A-Z][a-z]{2} \d{1,2}, (?P<year>\d{4}))(?: after a ball has been played)?, then", re.I)
RE_ADVANCES_PAST = re.compile(r"^If (?P<who>.+?) advances past the (?P<round>.+?) in the (?P<year>\d{4}) (?P<comp>.+?)(?: professional tennis tournament)?, then", re.I)
RE_WINS_FINAL = re.compile(r"^If (?P<who>.+?) wins the final in the (?P<year>\d{4}) (?P<comp>.+?) professional tennis tournament, then", re.I)
RE_IS_WINNER_OF = re.compile(r"^If (?P<who>.+?) is a (?P<year>\d{4}) winner of the (?P<round>.+?) of (?P<comp>.+?), then", re.I)
RE_STOTAL_LEGACY = re.compile(r"^If the " + _VS_MATCH + r" ends in (?:over|above) (?P<line>[\d.]+) sets, then", re.I)
RE_ELIMINATED = re.compile(r"^If (?P<who>.+?) is eliminated in the (?P<round>.+?) in the (?P<year>\d{4}) (?P<comp>.+?) tournament, then", re.I)
RE_TOURN_WIN = re.compile(r"^If (?P<who>.+?) wins the (?:(?P<year>\d{4}) )?(?P<comp>.+?)(?: professional tennis tournament| Championship| singles tennis tournament)?, then", re.I)
RE_ADVANCE = re.compile(r"^If (?P<who>.+?) qualifies for the (?P<round>.+?) at the (?P<year>\d{4}) (?P<comp>.+?) tennis tournament, then", re.I)


@dataclass
class ParsedMarket:
    ticker: str
    series_ticker: str
    event_ticker: str
    family: str = "UNKNOWN"
    status: str = "UNPARSED"          # PARSED | UNPARSED | UNSUPPORTED_FAMILY
    reason: str = ""
    tour: str = ""
    level: str = ""
    discipline: str = ""
    scope: str = ""
    projectable: bool = False
    # match scope
    player_a: str = ""                 # first-listed competitor in "a vs b" (rules text order)
    player_b: str = ""
    subject: str = ""                  # competitor the YES payoff is about (full name from rules)
    subject_is_a: bool | None = None
    competitor_id: str = ""            # Kalshi tennis_competitor / tennis_doubles_competitor UUID
    year: int | None = None
    competition: str = ""              # e.g. "US Open Men Singles"
    round: str = ""                    # canonical round code
    line: float | None = None          # threshold for spreads/totals/aces
    set_index: int | None = None
    exact_score: tuple[int, int] | None = None
    game_index: int | None = None
    # settlement semantics preserved verbatim
    ball_played_clause: bool = False
    rules_primary: str = ""
    raw_strike: dict = field(default_factory=dict)
    legacy_grammar: str = ""
    opponent_unknown: bool = False

    def to_dict(self):
        return asdict(self)


def _round_split(comp_round: str) -> tuple[str, str]:
    m = _ROUND_RE.match(comp_round.strip())
    if not m:
        return comp_round.strip(), ""
    return m.group("comp").strip(" ,-"), ROUND_WORDS[m.group("round").lower()]


def _name_tokens(x: str) -> set[str]:
    import unicodedata
    x = unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode()
    x = re.sub(r"[\'\u2019.]", "", x.lower())
    toks = re.split(r"[\s/\-]+", x)
    long = {t for t in toks if len(t) >= 3}
    return long if long else {t for t in toks if t}


def _who_is(who: str, a: str, b: str) -> bool | None:
    """Does the payoff subject `who` (full names) refer to competitor a (abbreviated in the rules text)?

    Token containment: every >=3-letter token of the abbreviated side must appear among the tokens of
    the full-name subject. Returns None when both or neither side fits (the caller then relies on the
    ticker-code side, and fails closed if that is unavailable too).
    """
    w = _name_tokens(who)
    ta, tb = _name_tokens(a), _name_tokens(b)
    fa = bool(ta) and ta <= w
    fb = bool(tb) and tb <= w
    if fa and not fb:
        return True
    if fb and not fa:
        return False
    return None


_EVENT_CODE_RE = re.compile(r"^\d\d(?:[A-Z]{3}\d\d)?(?P<code>[A-Z][A-Z0-9]*)$")


def side_from_ticker(ticker: str, event_ticker: str) -> bool | None:
    """Which side of the event the market subject is, from the ticker grammar.

    Event tickers for match markets are <SERIES>-<YYMONDD><CODE_A><CODE_B>[dup digit]; the market suffix is
    <CODE_subject>[strike digits]. Singles codes are 3 letters, doubles codes 6 (3+3). Returns True if the
    subject is the first-listed competitor, False if the second, None if the grammar does not apply.
    """
    try:
        ev_tail = event_ticker.split("-", 1)[1]
    except IndexError:
        return None
    m = _EVENT_CODE_RE.match(ev_tail)
    if not m:
        return None
    raw_code = m.group("code")
    code = re.sub(r"\d", "", raw_code)
    raw_suffix = ticker[len(event_ticker) + 1:] if ticker.startswith(event_ticker + "-") else ticker.rsplit("-", 1)[-1]
    raw_suffix = raw_suffix.split("-")[-1] if raw_suffix else ""
    suffix = re.sub(r"[^A-Z]", "", raw_suffix)
    if not suffix or len(suffix) >= len(code):
        return None
    half = len(code) // 2
    if len(code) % 2 == 0 and code[:half] == code[half:] == suffix:
        # same-surname pairing (e.g. WANWAN2): the exchange appends the duplicate digit to the SECOND
        # competitor's code, so a digit-free suffix is the first competitor.
        return not bool(re.search(r"\d$", raw_suffix))
    starts, ends = code.startswith(suffix), code.endswith(suffix)
    if starts and not ends:
        return True
    if ends and not starts:
        return False
    return None


def parse_market(m: dict) -> ParsedMarket:
    t = m.get("ticker") or ""
    s_tk = m.get("series_ticker") or t.split("-")[0]
    pm = ParsedMarket(ticker=t, series_ticker=s_tk, event_ticker=m.get("event_ticker") or "")
    rp = (m.get("rules_primary") or "").strip()
    pm.rules_primary = rp
    pm.ball_played_clause = "after a ball has been played" in rp.lower()
    cs = m.get("custom_strike") or {}
    pm.raw_strike = {k: m.get(k) for k in ("strike_type", "floor_strike", "cap_strike") if m.get(k) is not None}
    pm.competitor_id = cs.get("tennis_competitor") or cs.get("tennis_doubles_competitor") or ""
    fam = SERIES.get(s_tk)
    if fam is None:
        pm.reason = f"unknown series {s_tk}"
        return pm
    pm.family, pm.tour, pm.level, pm.discipline = fam
    pm.scope = FAMILIES[pm.family]["scope"]
    pm.projectable = FAMILIES[pm.family]["projectable"]
    if not pm.projectable:
        pm.status = "UNSUPPORTED_FAMILY"
        pm.reason = FAMILIES[pm.family].get("note", "family not priced by the match/draw engine")
    if not rp:
        pm.status = "UNPARSED"; pm.reason = "empty rules_primary"; return pm

    def fill_match(g):
        pm.player_a, pm.player_b = g["a"].strip(), g["b"].strip()
        pm.year = int(g["year"])
        pm.competition, pm.round = _round_split(g["comp"])
        if "who" in g.groupdict() and g["who"]:
            pm.subject = g["who"].strip()
            by_name = _who_is(pm.subject, pm.player_a, pm.player_b)
            by_code = side_from_ticker(pm.ticker, pm.event_ticker)
            if by_code is not None and by_name is not None and by_code != by_name:
                raise ValueError(f"ticker code side ({by_code}) disagrees with name side ({by_name}) for {pm.subject!r}")
            pm.subject_is_a = by_code if by_code is not None else by_name

    fam = pm.family
    try:
        if fam == "MATCH_WINNER":
            g = RE_MATCH_WINNER.match(rp)
            if g:
                fill_match(g)
            elif RE_MATCH_SCHEDULED.match(rp):
                g = RE_MATCH_SCHEDULED.match(rp)
                pm.player_a, pm.player_b = g["a"].strip(), g["b"].strip(); pm.year = int(g["year"])
                pm.subject = g["who"].strip(); pm.competition = ""; pm.round = ""
                by_code = side_from_ticker(pm.ticker, pm.event_ticker)
                pm.subject_is_a = by_code if by_code is not None else _who_is(pm.subject, pm.player_a, pm.player_b)
                pm.legacy_grammar = "scheduled_for"
            elif RE_ADVANCES_PAST.match(rp) or RE_WINS_FINAL.match(rp) or RE_IS_WINNER_OF.match(rp):
                g = RE_ADVANCES_PAST.match(rp) or RE_WINS_FINAL.match(rp) or RE_IS_WINNER_OF.match(rp)
                pm.subject = g["who"].strip(); pm.year = int(g["year"]); pm.competition = g["comp"].strip()
                rd = g.groupdict().get("round") or "final"
                pm.round = ROUND_WORDS.get(rd.lower(), rd)
                pm.subject_is_a = side_from_ticker(pm.ticker, pm.event_ticker)
                pm.legacy_grammar = "round_advance_as_match"
                if pm.subject_is_a is None:
                    raise ValueError("legacy match grammar: side not recoverable from ticker")
                pm.player_a = pm.subject if pm.subject_is_a else ""
                pm.player_b = "" if pm.subject_is_a else pm.subject
                pm.opponent_unknown = True
            else:
                raise ValueError("match-winner rules text not recognised")
        elif fam == "SET_WINNER":
            g = RE_SET_WINNER.match(rp)
            if not g:
                raise ValueError("set-winner rules text not recognised")
            fill_match(g); pm.set_index = int(g["n"])
        elif fam == "EXACT_SET_SCORE":
            g = RE_EXACT.match(rp)
            if not g:
                raise ValueError("exact-score rules text not recognised")
            fill_match(g); pm.exact_score = (int(g["x"]), int(g["y"]))
        elif fam == "GAME_SPREAD":
            g = RE_GSPREAD.match(rp)
            if not g:
                raise ValueError("game-spread rules text not recognised")
            fill_match(g); pm.line = float(g["line"])
            fs = m.get("floor_strike")
            if fs is not None and abs(float(fs) - pm.line) > 1e-9:
                raise ValueError(f"floor_strike {fs} disagrees with rules line {pm.line}")
        elif fam == "TOTAL_GAMES":
            g = RE_GTOTAL.match(rp)
            if not g:
                raise ValueError("total-games rules text not recognised")
            fill_match(g); pm.line = float(g["line"])
            fs = m.get("floor_strike")
            if fs is not None and abs(float(fs) - pm.line) > 1e-9:
                raise ValueError(f"floor_strike {fs} disagrees with rules line {pm.line}")
        elif fam == "TOTAL_SETS":
            g = RE_STOTAL.match(rp) or RE_STOTAL_LEGACY.match(rp)
            if not g:
                raise ValueError("total-sets rules text not recognised")
            fill_match(g); pm.line = float(g["line"])
        elif fam == "SET_SPREAD":
            g = RE_SSPREAD.match(rp)
            if not g:
                raise ValueError("set-spread rules text not recognised")
            fill_match(g); pm.line = float(g["line"])
        elif fam == "PLAYER_ACES":
            g = RE_ACES.match(rp)
            if not g:
                raise ValueError("aces rules text not recognised")
            fill_match(g); pm.line = float(g["n"]) - 0.5
        elif fam == "GAME_WINNER_INPLAY":
            g = RE_GAME_INPLAY.match(rp)
            if not g:
                raise ValueError("game-winner rules text not recognised")
            fill_match(g); pm.set_index = int(g["s"]); pm.game_index = int(g["g"])
        elif fam == "TIEBREAK_OCCURS":
            g = RE_TIEBREAK.match(rp)
            if not g:
                raise ValueError("tiebreak rules text not recognised")
            fill_match(g)
        elif fam == "TOURNAMENT_WINNER":
            g = RE_IS_WINNER_OF.match(rp) or RE_ADVANCES_PAST.match(rp) or RE_WINS_FINAL.match(rp)
            if g:
                # tournament-named series (KXATPMAD, KXFOMEN, ...) carried per-match markets in 2025
                pm.family = "MATCH_WINNER"; pm.scope = "MATCH"; pm.projectable = True
                pm.subject = g["who"].strip(); pm.year = int(g["year"]); pm.competition = g["comp"].strip()
                rd = g.groupdict().get("round") or "final"
                pm.round = ROUND_WORDS.get(rd.lower(), rd)
                pm.subject_is_a = side_from_ticker(pm.ticker, pm.event_ticker)
                pm.legacy_grammar = "round_advance_as_match"
                if pm.subject_is_a is None:
                    raise ValueError("legacy match grammar: side not recoverable from ticker")
                pm.player_a = pm.subject if pm.subject_is_a else ""
                pm.player_b = "" if pm.subject_is_a else pm.subject
                pm.opponent_unknown = True
            else:
                g = RE_TOURN_WIN.match(rp)
                if not g:
                    raise ValueError("tournament-winner rules text not recognised")
                pm.subject = g["who"].strip(); pm.year = int(g["year"]) if g["year"] else None
                pm.competition = g["comp"].strip()
        elif fam == "ROUND_OF_ELIMINATION":
            g = RE_ELIMINATED.match(rp)
            if not g:
                raise ValueError("elimination rules text not recognised")
            pm.subject = g["who"].strip(); pm.year = int(g["year"]); pm.competition = g["comp"].strip()
            pm.round = ROUND_WORDS.get(g["round"].lower(), g["round"])
        elif fam == "ROUND_ADVANCE":
            g = RE_ADVANCE.match(rp)
            if not g:
                raise ValueError("advance rules text not recognised")
            pm.subject = g["who"].strip(); pm.year = int(g["year"]); pm.competition = g["comp"].strip()
            pm.round = ROUND_WORDS.get(g["round"].lower(), g["round"])
        else:
            # unsupported family: keep status/reason set above, but harvest a subject where cheap
            mm = re.match(r"^If (?P<who>.+?) (wins|records|qualifies|is)", rp)
            if mm:
                pm.subject = mm.group("who").strip()
            return pm
        if pm.status != "UNSUPPORTED_FAMILY":
            if pm.scope == "MATCH" and pm.subject and pm.subject_is_a is None and not pm.opponent_unknown:
                raise ValueError(f"cannot map subject {pm.subject!r} onto {pm.player_a!r}/{pm.player_b!r}")
            pm.status = "PARSED"
    except ValueError as e:
        pm.status = "UNPARSED"; pm.reason = str(e)
    return pm
