"""The deep-review dossier: one game's football research, assembled from the RUN NFL packet, with every feature labelled by what it is.

Three kinds of statement are kept apart on every line:

  MEASURED     computed from play-by-play, depth charts, injury reports, weather or the schedule (opponent-adjusted where the packet says so)
  SIMULATION   an output of the repository's simulation (market-centred, research)
  HYPOTHESIS   the analyst's reading; never produced here

and anything the packet does not carry is listed under UNAVAILABLE rather than implied. No coverage-scheme, blitz-rate, route-level
(boundary/slot), run-gap (inside/outside), pass-block/run-block grade, pass-rush-win-rate or defensive run-fit data is captured, so none of
those features is reported, estimated or alluded to. What IS measured at the tactical level is the quarterback's EPA clean versus under
pressure, the defence's sack and QB-hit rates, the offensive-line injury list, adjusted rush/pass splits, explosive rates, early-down EPA,
neutral-script pass-rate-over-expected, and (from the schedule) rest.

`triage` orders games for deep review. It is an ORDERING, not a screen: every game gets a terminal state in the card, and a low triage rank
never removes one.
"""
from __future__ import annotations

import csv
import io
import json
from statistics import mean

DOSSIER_VERSION = "dossier-1.0.0"

UNAVAILABLE = (
    "defensive coverage scheme (man/zone) and per-receiver coverage assignment",
    "blitz rate and pressure-by-package splits (only sack and QB-hit rates are captured)",
    "boundary versus slot receiver splits and route-level data (routes run, targets per route)",
    "inside versus outside run splits, gap and zone-scheme data; defensive run fits",
    "offensive-line pass-block and run-block grades, continuity, pass-rush win rate (only the injury list)",
    "snap counts per play and in-game substitution patterns (depth-chart order is a stated intention, not a snap share)",
    "travel distance and time-zone burden (rest days only)",
    "score-state paths, lead changes, red-zone trip counts, drive counts (not simulated)",
)

ADJ_PAIRS = (
    ("pass offence v pass defence", "off_db_epa", "def_db_epa"),
    ("run offence v run defence", "off_rush_epa", "def_rush_epa"),
    ("neutral-script efficiency", "off_epa_ng", "def_epa_ng"),
    ("early-down efficiency", "off_ed_epa", "def_ed_epa"),
    ("explosive plays", "off_explosive", "def_explosive"),
    ("sack rate", "off_sack_rate", "def_sack_rate"),
    ("success rate", "off_sr", "def_sr"),
)


def _g(d, *keys, default=None):
    for k in keys:
        if not isinstance(d, dict) or k not in d:
            return default
        d = d[k]
    return d


def schedule_row(schedule_text: str, game_id: str) -> dict | None:
    for r in csv.DictReader(io.StringIO(schedule_text)):
        if r.get("game_id") == game_id:
            return r
    return None


def slate_reference(packet: dict) -> dict:
    """Slate mean of the team ratings, the yardstick for 'above/below a typical team this week'."""
    rows = {}
    for g in packet.get("games", []):
        for t, prof in (g.get("team_profiles") or {}).items():
            rows[t] = prof
    keys = ("def_qb_hit_rate", "def_sack_rate", "off_sack_rate_allowed", "off_explosive_rate", "def_explosive_rate", "off_rz_epa", "off_proe_early_ng")
    ref = {}
    for k in keys:
        v = [x["season_split"][k] for x in rows.values() if isinstance(_g(x, "season_split", k), (int, float))]
        if v:
            ref[k] = round(mean(v), 4)
    ref["teams"] = len(rows)
    return ref


def _adjusted_pairs(off_team: dict, def_team: dict) -> list:
    out = []
    ao, ad = off_team.get("adjusted") or {}, def_team.get("adjusted") or {}
    for label, ok, dk in ADJ_PAIRS:
        o, d = ao.get(ok), ad.get(dk)
        if o is None or d is None:
            continue
        # Ratings come from y = off_t + def_opp (team_ratings.py): expected EPA = o + d, and a defence rating is EPA ALLOWED above average
        # (positive = worse defence). Sacks run the other way for the offence: more sacks allowed / generated is bad for it.
        adv = -(o + d) if label == "sack rate" else (o + d)
        out.append({"matchup": label, "offence_adjusted": o, "defence_adjusted": d, "advantage_to_offence": round(adv, 5)})
    return out


def _qb_pressure(game: dict, off: str, opp: str, ref: dict) -> dict:
    qbs = _g(game, "quarterbacks", off, default=[]) or []
    qb = next((q for q in qbs if q.get("depth_chart_order") == 1), qbs[0] if qbs else None)
    if not qb:
        return {"status": "UNAVAILABLE", "reason": "no quarterback profile"}
    prof = qb.get("profile") or {}
    up, cl, ov = prof.get("under_pressure") or {}, prof.get("clean_pocket") or {}, prof.get("overall") or {}
    opp_prof = _g(game, "team_profiles", opp, "season_split") or {}
    n = prof.get("dropbacks")
    return {"status": "PARTIAL", "kind": "MEASURED", "qb": qb.get("player"), "qb_status": qb.get("status"), "qb_injury": qb.get("injury_status"),
            "dropbacks": n, "insufficient_sample": prof.get("insufficient_sample"),
            "epa_per_dropback_clean": cl.get("epa_per_dropback"), "epa_per_dropback_under_pressure": up.get("epa_per_dropback"),
            "own_pressure_rate_proxy": ov.get("pressure_rate_proxy"),
            "opponent_qb_hit_rate": opp_prof.get("def_qb_hit_rate"), "opponent_sack_rate": opp_prof.get("def_sack_rate"),
            "slate_mean_qb_hit_rate": ref.get("def_qb_hit_rate"), "slate_mean_sack_rate": ref.get("def_sack_rate"),
            "reading": ("The opponent generates QB hits at "
                        + ("above" if (opp_prof.get("def_qb_hit_rate") or 0) > (ref.get("def_qb_hit_rate") or 0) else "or below")
                        + " the slate mean. The quarterback's clean-vs-pressured EPA gap is the exposure; pressured samples are small. "
                          "Blitz rate is NOT captured, so this cannot say the pressure comes from blitzing."),
            "caveat": "profile matched to the player by " + str(qb.get("profile_matched_by"))}


def _ol_injuries(game: dict, team: str) -> dict:
    ol = _g(game, "offensive_line", team) or {}
    lst = ol.get("injured_or_listed") or []
    out = [p for p in lst if str(p.get("state", "")).lower() in ("out", "injured reserve", "doubtful", "questionable")]
    return {"status": "PARTIAL", "kind": "MEASURED", "listed_not_active": [{"player": p["player"], "pos": p.get("position"), "state": p["state"]} for p in out],
            "n_not_active": len(out), "note": ol.get("note") or "No OL quality metric is captured."}


def _availability(game: dict) -> dict:
    recs = _g(game, "injuries", "records", default=[]) or []
    keep = ("QB", "RB", "WR", "TE", "OT", "OG", "G", "T", "C", "OL", "DE", "DT", "LB", "CB", "S", "DB", "DL", "EDGE")
    flagged = [r for r in recs if str(r.get("state", "")).lower() in ("out", "doubtful", "questionable", "injured reserve") and (r.get("position") in keep)]
    by_team: dict = {}
    for r in flagged:
        by_team.setdefault(r.get("team"), []).append({"player": r.get("player"), "pos": r.get("position"), "state": r.get("state"),
                                                       "new_since_previous_capture": r.get("new_since_previous_capture"),
                                                       "changed": r.get("changed_since_previous_capture"), "detail": r.get("detail"),
                                                       "report": r.get("espn_report_date")})
    return {"status": "AVAILABLE", "kind": "MEASURED", "capture": _g(game, "injuries", "summary", "capture_run_id"), "by_team": by_team}


def _team_volume(game: dict) -> dict:
    tv = _g(game, "game_script_inputs", "team_volume") or {}
    out = {}
    for t, v in tv.items():
        if not isinstance(v, dict):
            continue
        out[t] = {"plays_mean": _g(v, "plays", "mean"), "pass_rate_mean": _g(v, "pass_rate", "mean"), "pass_att_mean": _g(v, "pass_att", "mean"),
                  "by_final_margin": v.get("by_final_margin"), "target_concentration_hhi": v.get("target_concentration_hhi")}
    return {"status": "AVAILABLE" if out else "UNAVAILABLE", "kind": "SIMULATION", "teams": out,
            "label": "market-centred simulation output (research); not a measured rate"}


def _player_opportunity(game: dict, top: int = 5) -> dict:
    po = _g(game, "game_script_inputs", "player_opportunity") or {}
    names = {}
    for nm, d in (game.get("players") or {}).items():
        pid = _g(d, "meta", "player_id")
        if pid:
            names[pid] = nm
    out = {}
    for t, lst in po.items():
        if not isinstance(lst, list):
            continue
        ranked = sorted(lst, key=lambda r: -((_g(r, "targets", "mean") or 0) + (_g(r, "carries", "mean") or 0)))[:top]
        out[t] = [{"player": names.get(r.get("player"), r.get("player")), "pos": r.get("position"), "p_active": r.get("p_active"),
                   "targets_mean": _g(r, "targets", "mean"), "targets_range50": _g(r, "targets", "range_50"), "carries_mean": _g(r, "carries", "mean"),
                   "carries_range50": _g(r, "carries", "range_50"), "target_share": r.get("target_share"), "carry_share": r.get("carry_share"),
                   "opportunity_cv": r.get("opportunity_cv"), "role_uncertainty": r.get("role_uncertainty")} for r in ranked]
    return {"status": "AVAILABLE" if out else "UNAVAILABLE", "kind": "SIMULATION", "teams": out,
            "label": "simulated opportunity with its uncertainty; depth-chart order is a stated intention, not a measured snap share"}


def build_dossier(game: dict, ref: dict, sched_row: dict | None = None) -> dict:
    home, away = game["home_team"], game["away_team"]
    prof = game.get("team_profiles") or {}
    d = {
        "version": DOSSIER_VERSION, "game_id": game["game_id"], "kickoff_utc": game["kickoff_utc"], "home": home, "away": away,
        "venue": {"venue": game.get("venue"), "roof": game.get("roof"), "surface": game.get("surface"), "neutral_site": game.get("neutral_site")},
        "weather": {k: _g(game, "weather", k) for k in ("roof_status", "temperature_f", "wind", "precipitation_probability", "short_forecast", "material", "note")},
        "rest": ({"home_rest_days": sched_row.get("home_rest"), "away_rest_days": sched_row.get("away_rest"), "source": "nflverse schedule", "kind": "MEASURED"}
                 if sched_row else {"status": "UNAVAILABLE"}),
        "market": {"implied_home_margin_median": _g(game, "market_implied", "implied_home_margin_median"),
                   "implied_total_median": _g(game, "market_implied", "implied_total_median"),
                   "win_probability": _g(game, "market_implied", "win_probability"), "model_spread_incumbent": _g(game, "model_view", "model_spread"),
                   "note": "market mids are not executable; the incumbent spread is a disagreement, not an edge"},
        "team_matchups": {}, "sample": {}, "schedule_adjustment": {}, "qb_pressure": {}, "offensive_line": {}, "availability": _availability(game),
        "team_volume": _team_volume(game), "player_opportunity": _player_opportunity(game),
        "script_candidates": [{"cell": s["cell"], "label": s["label"], "probability": s["probability"]} for s in (_g(game, "game_script_v2", "primary_scripts") or [])],
        "key_questions": game.get("key_questions"), "unavailable": list(UNAVAILABLE),
    }
    for off, opp in ((home, away), (away, home)):
        po, pd_ = prof.get(off) or {}, prof.get(opp) or {}
        d["team_matchups"][f"{off} offence v {opp} defence"] = _adjusted_pairs(po, pd_)
        ss = po.get("season_split") or {}
        d["sample"][off] = {"games": ss.get("n_games"), "insufficient_sample": ss.get("insufficient_sample"), "basis": po.get("basis")}
        adj, raw = po.get("adjusted") or {}, ss
        d["schedule_adjustment"][off] = {
            "off_epa_raw": raw.get("off_epa_play"), "off_epa_adjusted": adj.get("off_epa"), "def_epa_raw": raw.get("def_epa_play"), "def_epa_adjusted": adj.get("def_epa"),
            "reading": "adjusted is the schedule-adjusted rating; a large gap between raw and adjusted means the ranking leans on who was played"}
        d["qb_pressure"][off] = _qb_pressure(game, off, opp, ref)
        qbp = d["qb_pressure"][off]
        # SOURCE CONFLICT: the quarterback block and the injury report are different sources. If the injury report lists the starter as
        # anything but active while the quarterback block calls him Active, the status is CONFLICTED and nothing downstream may price on it.
        listed = next((p for p in (d["availability"]["by_team"].get(off) or []) if p.get("pos") == "QB" and p.get("player") == qbp.get("qb")), None)
        if listed and str(qbp.get("qb_status") or "Active").lower() == "active" and str(listed["state"]).lower() != "active":
            qbp["qb_status"] = "CONFLICT"
            qbp["conflict"] = f"quarterback block: Active; injury report: {listed['state']} ({listed.get('report')})"
        d["offensive_line"][off] = _ol_injuries(game, off)
        d["team_matchups"][f"{off} PROE / pass-rate context"] = {
            "off_proe_early_neutral": ss.get("off_proe_early_ng"), "adjusted_off_proe": adj.get("off_proe"), "slate_mean_proe": ref.get("off_proe_early_ng"),
            "off_no_huddle_rate": ss.get("off_no_huddle_rate"), "off_plays_per_drive": ss.get("off_plays_per_drive"), "kind": "MEASURED"}
    return d


# ------------------------------------------------------------------------------------------------ triage

def triage(game: dict, dossier: dict) -> dict:
    """An ORDERING score for deep review, with its reasons. Weights are stated; none is fitted.

    Surfaces where a handicapper has something to work with: material availability news, big price movement, a large gap between the
    schedule-adjusted ratings and the market, material weather, a rested-vs-short-week asymmetry, and a deep executable board."""
    pts, why = 0.0, []
    new_news = 0
    for team, lst in (dossier["availability"].get("by_team") or {}).items():
        for p in lst:
            if p.get("new_since_previous_capture") or p.get("changed"):
                new_news += 1
    if new_news:
        pts += min(3.0, 1.0 * new_news); why.append(f"{new_news} availability change(s) since the previous capture")
    qb_flags = [t for t, q in dossier["qb_pressure"].items() if q.get("qb_status") not in (None, "Active") or q.get("qb_injury")]
    if qb_flags:
        pts += 3.0; why.append("quarterback availability not clean for " + ", ".join(qb_flags))
    gap = None
    ms, mk = dossier["market"].get("model_spread_incumbent"), dossier["market"].get("implied_home_margin_median")
    if ms is not None and mk is not None:
        gap = abs(float(ms) + float(mk))                 # model_spread is the positive-home-favourite convention; implied median is home margin
        if gap >= 1.5:
            pts += 1.0; why.append(f"incumbent spread differs from the market by {gap:.1f} pts (a disagreement, not an edge)")
    adv = []
    for k, pairs in dossier["team_matchups"].items():
        if isinstance(pairs, list):
            adv += [abs(p["advantage_to_offence"]) for p in pairs if p["matchup"] in ("pass offence v pass defence", "run offence v run defence")]
    if adv and max(adv) >= 0.10:
        pts += 1.5; why.append(f"largest adjusted offence-v-defence gap {max(adv):.2f} EPA/play")
    if dossier["weather"].get("material"):
        pts += 1.5; why.append("material weather")
    r = dossier["rest"]
    try:
        if r.get("home_rest_days") and r.get("away_rest_days") and abs(int(r["home_rest_days"]) - int(r["away_rest_days"])) >= 3:
            pts += 1.0; why.append(f"rest differential {r['home_rest_days']} v {r['away_rest_days']} days")
    except (TypeError, ValueError):
        pass
    c = game.get("counts") or {}
    execs = (game.get("coverage") or {}).get("totals", {}).get("executable")
    if execs and execs > 400:
        pts += 0.5; why.append(f"{execs} executable contracts")
    lowsample = [t for t, s in dossier["sample"].items() if s.get("insufficient_sample")]
    if lowsample:
        pts -= 1.0; why.append("thin sample for " + ", ".join(lowsample))
    return {"game_id": game["game_id"], "score": round(pts, 2), "reasons": why, "model_gap_points": None if gap is None else round(gap, 2)}


# ================================================================================================ dossier v2: the analyst's working file
#
# `build_dossier` (above) holds the team-level football. `build_dossier_v2` adds what an analyst needs to take a game from "scanned" to "deeply reviewed":
# a stable-ID EVIDENCE INDEX (so a thesis can cite what it rests on and the card can check the citation), the PLAYER MARKETS of the game (every priced
# ladder with its rungs, the market-implied median, measured recent usage, simulated opportunity, opponent-allowed production, availability), the CONTRACT
# FAMILIES with how each can be priced, and a THESIS TEMPLATE. Nothing here proposes a shift or a probability.

DOSSIER_V2_VERSION = "dossier-2.0.0"

#: What a review must cite before it counts as deep. Scanning markets alone satisfies none of the football categories.
REQUIRED_CATEGORIES = (("team_matchup", 2), ("qb_ol", 1), ("availability", 1), ("environment", 1), ("scripts", 1))
PLAYER_EVIDENCE_CATEGORIES = ("player_opportunity", "player_usage", "opponent_allowed")
PLAYER_MIN_CITATIONS = 2


def _slug(s: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in str(s)).strip("_").lower()


def _ev(index: dict, id_: str, category: str, kind: str, text: str, *, adjusted=None, values=None):
    index[id_] = {"id": id_, "category": category, "kind": kind, "text": text, "opponent_adjusted": adjusted, "values": values}
    return id_


def _evidence_from_base(d: dict) -> dict:
    ix: dict = {}
    for k, v in d["team_matchups"].items():
        if isinstance(v, list):
            off, _, rest = k.partition(" offence v ")
            for p in v:
                _ev(ix, f"TM:{off}>{rest.split(' ')[0]}:{_slug(p['matchup'])}", "team_matchup", "MEASURED",
                    f"{k}, {p['matchup']}: advantage to the offence {p['advantage_to_offence']:+.3f} (offence {p['offence_adjusted']:+.3f}, defence allowed {p['defence_adjusted']:+.3f}; schedule-adjusted)",
                    adjusted=True, values=p)
        else:
            team = k.split(" ")[0]
            _ev(ix, f"TM:{team}:proe", "team_matchup", "MEASURED",
                f"{team} neutral-script pass rate over expected {v['off_proe_early_neutral']} (adjusted {v['adjusted_off_proe']}; slate mean {v['slate_mean_proe']})", adjusted=False, values=v)
    for t, q in d["qb_pressure"].items():
        if q.get("status") != "UNAVAILABLE":
            _ev(ix, f"QB:{t}", "qb_ol", "MEASURED",
                f"{t} QB {q.get('qb')} ({q.get('qb_status')}): EPA/dropback clean {q.get('epa_per_dropback_clean')} vs under pressure {q.get('epa_per_dropback_under_pressure')} "
                f"({q.get('dropbacks')} dropbacks); opposing QB-hit rate {q.get('opponent_qb_hit_rate')}, sack rate {q.get('opponent_sack_rate')} (slate means {q.get('slate_mean_qb_hit_rate')}, {q.get('slate_mean_sack_rate')})"
                + (f". SOURCE CONFLICT: {q['conflict']}" if q.get("conflict") else ""), adjusted=False, values=q)
    for t, o in d["offensive_line"].items():
        _ev(ix, f"OL:{t}", "qb_ol", "MEASURED", f"{t} offensive line not active/listed: {[(p['player'], p['state']) for p in o['listed_not_active']] or 'none'}; no OL quality metric is captured", adjusted=None, values=o)
    for t, lst in (d["availability"].get("by_team") or {}).items():
        _ev(ix, f"AV:{t}", "availability", "MEASURED", f"{t} injury report (non-active): " + "; ".join(f"{p['player']} {p['pos']} {p['state']}" + (" NEW" if p.get("new_since_previous_capture") else "") for p in lst), adjusted=None, values=lst)
    r = d["rest"]
    if r.get("status") != "UNAVAILABLE":
        _ev(ix, "ENV:rest", "environment", "MEASURED", f"rest days: home {r.get('home_rest_days')}, away {r.get('away_rest_days')}", adjusted=None, values=r)
    _ev(ix, "ENV:weather", "environment", "MEASURED", f"venue {d['venue']}; weather {d['weather']}", adjusted=None, values=d["weather"])
    m = d["market"]
    _ev(ix, "ENV:market", "environment", "MEASURED", f"market centre (midpoints, not executable): home margin {m['implied_home_margin_median']}, total {m['implied_total_median']}, win probability {m['win_probability']}", adjusted=None, values=m)
    for t, v in (d["team_volume"].get("teams") or {}).items():
        _ev(ix, f"TV:{t}", "scripts", "SIMULATION", f"{t} simulated plays {v['plays_mean']}, pass rate {v['pass_rate_mean']}; by final margin: {v.get('by_final_margin')}", adjusted=None, values=v)
    for s in d["script_candidates"]:
        _ev(ix, f"SC:{_slug(s['cell'])}", "scripts", "SIMULATION", f"script {s['label']}: {s['probability']:.0%} (market-centred simulation, research)", adjusted=None, values=s)
    for t, lst in (d["player_opportunity"].get("teams") or {}).items():
        for p in lst:
            _ev(ix, f"PO:{t}:{_slug(p['player'])}", "player_opportunity", "SIMULATION",
                f"{p['player']} ({t} {p['pos']}) simulated targets {p['targets_mean']} (50% range {p['targets_range50']}), carries {p['carries_mean']}, p_active {p['p_active']}, role uncertainty {p['role_uncertainty']}",
                adjusted=None, values=p)
    return ix


def _market_ladders(rows: list, shard_family_counts: dict) -> dict:
    from nfl_edge.handicap import ladder_fair as LF
    ladders = LF.build_ladders(rows)
    out: dict = {}
    for key, lad in ladders.items():
        out[key] = lad
    return out


def build_dossier_v2(game: dict, ref: dict, sched_row, shard_rows: list, stats=None, snaps=None, week: int | None = None) -> dict:
    from nfl_edge.handicap import ladder_fair as LF
    from nfl_edge.handicap import usage as US
    d = build_dossier(game, ref, sched_row)
    home, away, gid = game["home_team"], game["away_team"], game["game_id"]
    week = week or game.get("week")
    ix = _evidence_from_base(d)

    # ---- contract families: what exists, what is executable, and how each can be priced
    fam: dict = {}
    for r in shard_rows:
        k = f"{r['family']}|{r.get('period') or 'FULL'}"
        b = fam.setdefault(k, {"listed": 0, "executable": 0})
        b["listed"] += 1
        b["executable"] += 1 if r.get("executable") else 0
    ladders = LF.build_ladders(shard_rows)
    ladder_fams = {}
    for key, lad in ladders.items():
        if lad.ok:
            ladder_fams.setdefault(f"{key[0]}|{key[1]}", 0)
            ladder_fams[f"{key[0]}|{key[1]}"] += 1
    from nfl_edge.handicap import fairvalue as FV
    for k, b in fam.items():
        f_, per = k.split("|")
        if f_ in FV.DERIVABLE and per == "FULL":
            b["how_priced"] = "DERIVED from the market-centred simulation shifted by a thesis `shift` range (full-game margin/total)"
        elif k in ladder_fams:
            b["how_priced"] = f"LADDER SHIFT: {ladder_fams[k]} ladder(s) with >= {LF.MIN_RUNGS} usable rungs; price with a thesis `ladder_shifts` entry (units of the quantity)"
        else:
            b["how_priced"] = "DECLARED fair range only (no ladder, or fewer than 3 usable rungs); cannot be ranked without one"
        _ev(ix, f"FAM:{k}", "markets", "MEASURED", f"{k}: {b['listed']} listed, {b['executable']} executable; {b['how_priced']}", adjusted=None, values=b)
    d["contract_families"] = dict(sorted(fam.items()))

    # ---- player markets
    names = {}
    for nm, pd_ in (game.get("players") or {}).items():
        meta = (pd_ or {}).get("meta") or {}
        names[nm] = {"player_id": meta.get("player_id"), "team": meta.get("team"), "p_active": meta.get("p_plays") or meta.get("p_active"),
                     "availability_state": meta.get("availability_state")}
    inj = {}
    for r in (game.get("injuries") or {}).get("records", []):
        inj[r.get("player")] = r.get("state")
    pos_of = {}
    if stats is not None:
        for row in stats[stats["week"] < (week or 99)].drop_duplicates("player_id").itertuples():
            pos_of[row.player_id] = row.position
    pm_players: dict = {}
    for r in shard_rows:
        if r["family"] != "PLAYER_STAT" or r.get("subject") is None:
            continue
        nm = r["subject"]
        meta = names.get(nm, {})
        P = pm_players.setdefault(nm, {"player": nm, "player_id": r.get("player_id") or meta.get("player_id"), "team": meta.get("team"), "stats": {}})
        P["stats"].setdefault(r["stat"], []).append(r)
    po_teams = (d["player_opportunity"].get("teams") or {})
    opp_of = {home: away, away: home}
    allowed_cache: dict = {}
    players_out = []
    for nm, P in pm_players.items():
        team, pid = P["team"], P["player_id"]
        pos = pos_of.get(pid)
        usage = US.player_usage(stats, snaps, pid, nm, team, week or 99) if stats is not None else {"state": "UNAVAILABLE", "reason": "player-week table not loaded"}
        opp = opp_of.get(team)
        allowed = None
        if opp and stats is not None and pos in US.POS_GROUP:
            if opp not in allowed_cache:
                allowed_cache[opp] = US.allowed_to_position(stats, opp, week or 99)
            grp = US.POS_GROUP[pos]
            allowed = {"opponent": opp, "position_group": grp, "basis": allowed_cache[opp].get("basis"),
                       "per_game": (allowed_cache[opp].get("groups") or {}).get(grp)}
        sim = next((x for x in (po_teams.get(team) or []) if x["player"] == nm), None)
        stats_out = []
        for stat, rs in sorted(P["stats"].items()):
            lad = ladders.get(LF.ladder_key(rs[0]))
            rungs = sorted(({"threshold": r["threshold"], "yes_ask": r.get("yes_ask"), "no_ask": r.get("no_ask"), "mid": r.get("mid"), "width": r.get("width"),
                             "volume": r.get("volume"), "executable": r.get("executable"), "ticker": r["ticker"]} for r in rs), key=lambda x: x["threshold"])
            inc = [x.get("incumbent") or {} for x in rs]
            gaps = [abs(i["disagreement_vs_mid"]) for i in inc if i.get("disagreement_vs_mid") is not None]
            stats_out.append({"stat": stat, "operator": rs[0].get("operator"), "rungs": rungs, "usable_rungs": lad.n if lad else 0,
                              "market_median": None if not lad else (None if lad.median() is None else round(lad.median(), 2)),
                              "rung_spacing": None if not lad else lad.spacing, "ladder_shift_priceable": bool(lad and lad.ok),
                              "executable_rungs": sum(1 for r in rs if r.get("executable")),
                              "incumbent_max_abs_gap_to_mid": round(max(gaps), 3) if gaps else None,
                              "incumbent_label": "DISAGREEMENT ONLY -- not an edge; the incumbent is behind the closing market on player props" if gaps else None})
        availability = inj.get(nm) or meta_state(names.get(nm, {}))
        players_out.append({"player": nm, "player_id": pid, "team": team, "position": pos, "availability": availability,
                            "simulated_opportunity": sim, "measured_usage": usage, "opponent_allowed": allowed, "stats": stats_out})
        if usage.get("state") == "OK":
            _ev(ix, f"US:{_slug(nm)}", "player_usage", "MEASURED",
                f"{nm} last 4 weeks {usage['weeks_last4']}: {usage['per_game_last4']}; target share {usage['target_share_last4']}, carry share {usage['carry_share_last4']}, offense snap % {usage['offense_snap_pct_last4']}", adjusted=False, values=usage)
        if allowed and allowed.get("per_game"):
            _ev(ix, f"DEF:{allowed['opponent']}:{allowed['position_group']}", "opponent_allowed", "MEASURED",
                f"{allowed['opponent']} defence allows to {allowed['position_group']}s per game (index vs league mean): " +
                ", ".join(f"{c} {v['allowed_per_game']} ({v['index']}x)" for c, v in allowed["per_game"].items() if c in ("targets", "receptions", "receiving_yards", "carries", "rushing_yards", "attempts", "completions", "passing_yards")),
                adjusted=False, values=allowed)
        for s in stats_out:
            if s["usable_rungs"] >= LF.MIN_RUNGS:
                _ev(ix, f"PM:{_slug(nm)}:{s['stat']}", "markets", "MEASURED",
                    f"{nm} {s['stat']} ladder: {s['usable_rungs']} usable rungs, market median {s['market_median']}, {s['executable_rungs']} executable", adjusted=None,
                    values={k: s[k] for k in ("market_median", "usable_rungs", "executable_rungs", "rung_spacing")})
    players_out.sort(key=lambda p: (-(sum(s["executable_rungs"] for s in p["stats"])), p["player"]))
    d["player_markets"] = {"players": players_out, "n_players": len(players_out), "n_ladders": sum(len(p["stats"]) for p in players_out),
                           "n_priceable_ladders": sum(1 for p in players_out for s in p["stats"] if s["ladder_shift_priceable"]),
                           "note": "Every priced player ladder is listed with its rungs. Price one with a thesis `ladder_shifts` entry; the engine will not choose a shift."}
    d["unavailable"] = list(UNAVAILABLE)
    d["evidence_index"] = ix
    d["evidence_ids_by_category"] = {}
    for e in ix.values():
        d["evidence_ids_by_category"].setdefault(e["category"], []).append(e["id"])
    d["review_requirements"] = {
        "football_categories": {c: n for c, n in REQUIRED_CATEGORIES},
        "player_evidence": f">= {PLAYER_MIN_CITATIONS} ids from {PLAYER_EVIDENCE_CATEGORIES}, or player_markets_reason (>= 40 chars) saying why no player market is viable",
        "markets": "cite >= 1 FAM:* id for a game-line family and >= 1 for PLAYER_STAT|FULL (or player_markets_reason)",
        "reasoning": ">= 120 characters of the analyst's own reasoning",
        "note": "Scanning markets does not satisfy these. A review that cites nothing from a category is recorded NOT_REVIEWED.",
    }
    d["thesis_template"] = {
        "thesis_id": f"{gid}::T1", "game_id": gid, "statement": "", "short_reason": "", "drivers": ["SIDE_OR_ENVIRONMENT_KEY"],
        "evidence_ids": [], "evidence_notes": {"hypotheses": []},
        "shift": {"home_margin": [None, None], "total": [None, None], "basis": ""},
        "ladder_shifts": [{"selector": {"family": "PLAYER_STAT", "subject": "<player>", "stat": "receptions", "period": "FULL"}, "shift": [None, None],
                           "unit": "units of the stat; positive = more than the market has it", "basis": "", "evidence_ids": [],
                           "script_results": {"FAVORITE_CONTROL": "WIN|MIXED|LOSE", "COMPETITIVE": "WIN|MIXED|LOSE", "UNDERDOG_CONTROL": "WIN|MIXED|LOSE"},
                           "usage": {"projected_opportunity": "", "recent_usage": "", "role_stability": "", "teammate_context": ""}}],
        "candidates": [], "challenge": {"fail_modes": ["", ""], "market_already_priced": "", "matchup_check": "", "uncertainties": [""]}, "corroborations": [],
    }
    d["version_v2"] = DOSSIER_V2_VERSION
    return d


def meta_state(m: dict):
    return m.get("availability_state")


def submission_template(packet: dict, unstarted: list) -> dict:
    """The analyst's working file: one review skeleton per unstarted game, in review order, and an empty thesis list."""
    cats = [c for c, _ in REQUIRED_CATEGORIES] + list(PLAYER_EVIDENCE_CATEGORIES) + ["markets"]
    return {"submission_version": "1", "analyst": "", "packet_sha": packet.get("packet_sha"), "created_at": "",
            "reviews": [{"game_id": r["game_id"], "matchup": r["matchup"], "kickoff_utc": r["kickoff_utc"], "verdict": "THESIS | REJECTED | INSUFFICIENT_DATA",
                         "coverage": {c: [] for c in cats}, "player_markets_reason": "", "reasoning": "", "missing": []} for r in unstarted],
            "theses": [], "_how": "See ANALYST_GUIDE.md. Delete this key. Every game needs a review record; a game without one is NOT_REVIEWED."}


ANALYST_GUIDE = """# Analyst guide: from dossier to card

The card never decides which football theses deserve betting consideration. You do. The code prices, challenges and sizes what you submit and refuses what
does not hold; it never invents a shift, a probability or a script.

## For every unstarted game (dossiers/<GAME>.json, one file per game)
1. Read the dossier: team matchup advantages (opponent-adjusted where marked), QB/offensive-line status, availability, environment, scripts, the
   player-market section (measured usage, opponent-allowed production, market ladders) and `contract_families` (how each family can be priced).
2. Write ONE review record in the submission file (`submission_template.json`): `verdict` is THESIS, REJECTED or INSUFFICIENT_DATA, and `coverage` lists the
   evidence ids (the keys of `evidence_index`) you actually used in each category. The check resolves every id against the dossier; a record that cites nothing
   from a category does not qualify and the game is recorded NOT_REVIEWED, exactly as if you had only scanned the markets.
3. `reasoning` is yours: >= 120 characters of why. INSUFFICIENT_DATA needs a named missing/conflicting item (>= 20 characters) and at least one cited id.

## A thesis (only for verdict THESIS)
Start from `thesis_template` in the game's dossier. State the football claim, cite `evidence_ids`, then give SHIFTS as ranges:
* `shift`: full-game home-margin and total shift ranges (points) from the market centre. Prices every derivable full-game contract on both sides.
* `ladder_shifts`: for player-stat, period and alternate ladders: `selector` (family, subject, stat, period), `shift` range in units of the stat (positive = more
  than the market has it), `basis`, `evidence_ids`, `script_results` (WIN/MIXED/LOSE for FAVORITE_CONTROL, COMPETITIVE, UNDERDOG_CONTROL) and `usage`
  (projected_opportunity, recent_usage, role_stability, teammate_context).
* `candidates`: contracts you want priced with a fair range you declare yourself (`fair.low/high` = probability the side you buy wins, with a `basis`).
* `challenge`: fail_modes (>= 2), market_already_priced, matchup_check.
Ranges must be honest ranges. The card widens them by a measured noise buffer and requires a 2.0 cent net edge at the conservative end after fees. A thesis too small to
trade after fees is a PASS; that is a correct outcome.

## Submit
Commit the file to a branch / PR, or paste it into a GitHub issue titled `NFL CARD`; the workflow `nfl-thesis-card.yml` runs only for the repository owner's issues.
"""


BRIEF_ORDER = (("team_matchup", "Team matchup (advantage to the offence; schedule-adjusted where marked)"), ("qb_ol", "Quarterback and offensive line"),
               ("availability", "Availability"), ("environment", "Environment and market centre"), ("scripts", "Game scripts and team volume"),
               ("player_opportunity", "Simulated player opportunity (research, context only)"), ("player_usage", "Measured player usage (last four games, share of team)"),
               ("opponent_allowed", "Production the opponent allows to each position group (RAW, not schedule-adjusted)"),
               ("markets", "Contract families and player ladders (id -> how it can be priced)"))
BRIEF_MAX_ITEM = 420


def brief_markdown(d: dict) -> str:
    """The dossier as ONE readable page (~10 KB) for an analyst who cannot ingest the 300 KB JSON: every line starts with the evidence id to cite."""
    ix = d.get("evidence_index") or {}
    by = d.get("evidence_ids_by_category") or {}
    L = [f"# {d.get('away')} @ {d.get('home')} — {d.get('game_id')}", "", f"Kickoff {d.get('kickoff_utc')} UTC. Cite evidence by the id in backticks. Full detail: `dossiers/{d.get('game_id')}.json`.", ""]
    kq = d.get("key_questions") or []
    if kq:
        L += ["## Questions the data raises", ""] + [f"* {q if isinstance(q, str) else json.dumps(q)}" for q in kq[:8]] + [""]
    for cat, title in BRIEF_ORDER:
        ids = by.get(cat) or []
        if not ids:
            L += [f"## {title}", "", "*(no evidence of this kind in the dossier)*", ""]
            continue
        L += [f"## {title}", ""]
        shown = ids if cat != "markets" else [i for i in ids if i.startswith("FAM:") and "|FULL" in i] + [i for i in ids if i.startswith("PM:")]
        for i in shown[:140]:
            e = ix[i]
            t = e["text"] if len(e["text"]) <= BRIEF_MAX_ITEM else e["text"][:BRIEF_MAX_ITEM - 1] + "…"
            L.append(f"* `{i}` — {t}" + ("" if e.get("opponent_adjusted") is None else (" [adjusted]" if e["opponent_adjusted"] else " [RAW]")))
        if cat == "markets" and len(ids) > len(shown):
            L.append(f"* (+{len(ids) - len(shown)} period/other families: see `contract_families` in the JSON; price them with `ladder_shifts` or declare a fair range)")
        L.append("")
    L += ["## Not captured", "", "; ".join(d.get("unavailable") or []), ""]
    return "\n".join(L)
