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
