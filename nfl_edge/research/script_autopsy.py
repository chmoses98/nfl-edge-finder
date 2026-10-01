"""REALIZED GAME-SCRIPT AUTOPSY: why did the game that was played differ from the game that was expected -- and
did that difference cause the player projection misses? RESEARCH ONLY, deterministic, outcome-of-wager blind.

The question is not "did the projection miss" (the player autopsy answers that) but WHERE in the hierarchy

    GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY

reality left the expectation, and whether better game scripting could plausibly have prevented a miss.

EXPECTATIONS ARE NEVER REBUILT WITH HINDSIGHT. Each expected quantity carries its source, and only sources that
were frozen or knowable before kickoff are used:

    MARKET_LADDER        the board's own latest-pregame ladders (board-research): home margin, total, team
                         points, and a team's pass volume from its quarterback's pass-attempts ladder median
    SIM_SCRIPT           the simulation's game-script summary (nfl_edge/sim/script.py), Week 4 onward
    PRIOR_MEAN           the team's mean over games strictly earlier this season (all of last season in week 1),
                         from play-by-play -- a naive point-in-time baseline, not a model
    INCUMBENT_ANATOMY    the incumbent's frozen projected opportunity per player (player-anatomy corpus)

Weeks 1-3 have no frozen team-volume projection (the simulator persisted contract probabilities only), so their
team-volume expectation is MARKET_LADDER where a quarterback ladder exists and PRIOR_MEAN otherwise -- said so on
every row rather than reconstructed.

REALIZED SCRIPT LABELS are computed from the play-by-play score progression and the PREGAME market favourite and
total only. No label reads a wager, a position or whether anything we bought won (`realized_labels` has no
parameter that could carry one; pinned by test). Thresholds are named below.
"""
from __future__ import annotations

import math
from collections import Counter, defaultdict

SCRIPT_AUTOPSY_VERSION = "script-autopsy-1.0.0"

# label thresholds (points / plays), named once
BLOWOUT_MARGIN = 17          # |margin| entering Q4 (or final) at or above this is a blowout
EARLY_BLOWOUT_HALF = 14      # ... and if the halftime margin was already this large, an early one
ONE_SCORE = 8                # |margin| at every quarter end and at the final within this: competitive throughout
SHOOTOUT_OVER = 10           # total at least this far above the market total
LOW_SCORING_UNDER = 10       # total at least this far below
LOW_POSSESSION_PLAYS = 115   # combined offensive plays below this
HIGH_PASS_ATTEMPTS = 80      # combined pass attempts at or above this
RUN_CONTROL_RUSHES = 33      # winner's designed rushes at or above this, with a win by more than one score
VOLUME_OFF = math.log(1.25)  # a team-volume component is "off" beyond +/-25% (the player autopsy's own threshold)

LABELS = ("COMPETITIVE_THROUGHOUT", "FAVORITE_CONTROL", "UNDERDOG_CONTROL", "UPSET", "EARLY_BLOWOUT", "BLOWOUT",
          "LATE_COMEBACK", "SHOOTOUT", "LOW_SCORING", "LOW_POSSESSION", "HIGH_VOLUME_PASSING", "RUN_HEAVY_CONTROL")

# miss layers (the chain), in causal order
LAYER_AVAILABILITY = "AVAILABILITY"
LAYER_SCRIPT_VOLUME = "GAME_SCRIPT_DROVE_TEAM_VOLUME"
LAYER_TEAM_VOLUME = "TEAM_VOLUME_NOT_EXPLAINED_BY_SCRIPT"
LAYER_SHARE = "PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION"
LAYER_ROLE = "ROLE_UNCERTAINTY"
LAYER_EFFICIENCY = "EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION"
LAYER_VARIANCE = "VARIANCE_ONLY"
LAYER_NO_MISS = "NO_LARGE_MISS"
LAYER_INSUFFICIENT = "INSUFFICIENT_DATA"


def _f(x):
    try:
        return None if x is None else float(x)
    except (TypeError, ValueError):
        return None


# ------------------------------------------------------------------------------------------------ realized
def team_volume_from_pbp(plays: list) -> dict:
    """Per offence: plays, dropbacks, pass attempts, sacks, scrambles, designed rushes, kneels, QB designed runs.
    `plays` is a list of play-by-play dicts of ONE game."""
    out = defaultdict(lambda: Counter())
    passers = defaultdict(set)
    for p in plays:
        if p.get("posteam") and p.get("passer_player_id"):
            passers[p["posteam"]].add(p["passer_player_id"])
    for p in plays:
        t = p.get("posteam")
        if not t or p.get("play_type") not in ("pass", "run", "qb_kneel", "qb_spike"):
            continue
        c = out[t]
        c["plays"] += 1
        if (p.get("qb_dropback") or 0) == 1:
            c["dropbacks"] += 1
        if (p.get("pass_attempt") or 0) == 1 and (p.get("sack") or 0) != 1:
            c["pass_att"] += 1
        if (p.get("sack") or 0) == 1:
            c["sacks"] += 1
        if (p.get("qb_scramble") or 0) == 1:
            c["scrambles"] += 1
        if p.get("play_type") == "qb_kneel" or (p.get("qb_kneel") or 0) == 1:
            c["kneels"] += 1
        elif (p.get("rush_attempt") or 0) == 1 and (p.get("qb_scramble") or 0) != 1:
            c["designed_rush"] += 1
            if p.get("rusher_player_id") and p["rusher_player_id"] in passers[t]:
                c["qb_designed_runs"] += 1
    return {t: dict(c) for t, c in out.items()}


def game_flow(plays: list, home: str, away: str) -> dict:
    """Home margin at each quarter end and at the final, the largest lead each side held, and lead changes."""
    end = {}
    margins = []
    for p in plays:
        h, a, q = _f(p.get("total_home_score")), _f(p.get("total_away_score")), p.get("qtr")
        if h is None or a is None or q is None:
            continue
        m = h - a
        margins.append(m)
        end[int(q)] = (h, a)
    if not margins:
        return {}
    lead_changes, last_sign = 0, 0
    for m in margins:
        s = (m > 0) - (m < 0)
        if s and last_sign and s != last_sign:
            lead_changes += 1
        if s:
            last_sign = s
    q = {k: (v[0] - v[1]) for k, v in end.items()}
    fh, fa = end[max(end)]
    return {"margin_q1": q.get(1), "margin_half": q.get(2), "margin_q3": q.get(3), "final_home": fh, "final_away": fa,
            "final_margin": fh - fa, "final_total": fh + fa, "max_home_lead": max(0.0, max(margins)),
            "max_away_lead": max(0.0, -min(margins)), "lead_changes": lead_changes, "overtime": max(end) > 4}


def realized_labels(flow: dict, volume: dict, *, home: str, away: str, market_favorite: str | None,
                    market_total: float | None) -> list:
    """Deterministic script labels from the score progression, the realized volume and the PREGAME market
    favourite / total. Nothing about any wager is an input."""
    if not flow:
        return []
    lab = []
    fm = flow["final_margin"]
    qs = [flow.get("margin_q1"), flow.get("margin_half"), flow.get("margin_q3"), fm]
    if all(m is not None and abs(m) <= ONE_SCORE for m in qs):
        lab.append("COMPETITIVE_THROUGHOUT")
    q3 = flow.get("margin_q3")
    if (q3 is not None and abs(q3) >= BLOWOUT_MARGIN) or abs(fm) >= BLOWOUT_MARGIN:
        half = flow.get("margin_half")
        lab.append("EARLY_BLOWOUT" if (half is not None and abs(half) >= EARLY_BLOWOUT_HALF) else "BLOWOUT")
    if market_favorite in (home, away):
        fav_sign = 1 if market_favorite == home else -1
        if fm * fav_sign < 0:
            lab.append("UPSET")
            if q3 is not None and q3 * fav_sign < 0:
                lab.append("UNDERDOG_CONTROL")
        elif fm * fav_sign > ONE_SCORE and (flow.get("margin_half") or 0) * fav_sign > 0 and (q3 or 0) * fav_sign > 0:
            lab.append("FAVORITE_CONTROL")
    if q3 is not None and q3 != 0 and abs(q3) >= 7 and (fm == 0 or (fm > 0) != (q3 > 0)):
        lab.append("LATE_COMEBACK")
    if market_total is not None:
        if flow["final_total"] >= market_total + SHOOTOUT_OVER:
            lab.append("SHOOTOUT")
        elif flow["final_total"] <= market_total - LOW_SCORING_UNDER:
            lab.append("LOW_SCORING")
    vh, va = volume.get(home) or {}, volume.get(away) or {}
    if vh and va:
        if vh.get("plays", 0) + va.get("plays", 0) < LOW_POSSESSION_PLAYS:
            lab.append("LOW_POSSESSION")
        if vh.get("pass_att", 0) + va.get("pass_att", 0) >= HIGH_PASS_ATTEMPTS:
            lab.append("HIGH_VOLUME_PASSING")
        win = vh if fm > 0 else va if fm < 0 else None
        if win and abs(fm) > ONE_SCORE and win.get("designed_rush", 0) >= RUN_CONTROL_RUSHES:
            lab.append("RUN_HEAVY_CONTROL")
    return [l for l in LABELS if l in lab]


def primary_label(labels: list) -> str:
    for l in ("EARLY_BLOWOUT", "BLOWOUT", "UPSET", "LATE_COMEBACK", "SHOOTOUT", "LOW_SCORING", "FAVORITE_CONTROL",
              "COMPETITIVE_THROUGHOUT"):
        if l in labels:
            return l
    return "UNREMARKABLE"


# ------------------------------------------------------------------------------------------------ expectations
def prior_means(volumes_by_game: dict, schedule: list, game_id: str, team: str) -> dict:
    """The team's mean realized volume over games strictly before this one this season (all last season in
    week 1). `volumes_by_game`: game_id -> team -> volume; `schedule`: [{game_id, season, week, home, away}]."""
    g = next((s for s in schedule if s["game_id"] == game_id), None)
    if g is None:
        return {"basis": "unknown game", "n": 0}
    prior = [s for s in schedule if s["season"] == g["season"] and s["week"] < g["week"] and team in (s["home"], s["away"])
             and s["game_id"] in volumes_by_game and team in volumes_by_game[s["game_id"]]]
    basis = "prior games this season"
    if not prior:
        prior = [s for s in schedule if s["season"] == g["season"] - 1 and team in (s["home"], s["away"])
                 and s["game_id"] in volumes_by_game and team in volumes_by_game[s["game_id"]]]
        basis = "all games last season"
    if not prior:
        return {"basis": basis, "n": 0}
    keys = ("plays", "dropbacks", "pass_att", "designed_rush", "sacks", "scrambles", "qb_designed_runs")
    out = {"basis": basis, "n": len(prior)}
    for k in keys:
        vals = [volumes_by_game[s["game_id"]][team].get(k, 0) for s in prior]
        out[k] = sum(vals) / len(vals)
    return out


def _lr(actual, expected):
    if actual is None or expected is None:
        return None
    return math.log((actual + 0.5) / (expected + 0.5))


def team_expectation(team: str, *, prior: dict, market_qb_attempts: float | None, sim_team: dict | None) -> dict:
    """The expected team volume and its SOURCE (sim > market ladder > prior mean, per quantity)."""
    out = {}
    if sim_team:
        v = sim_team.get("volume") or {}
        for k, sk in (("plays", "plays"), ("pass_att", "pass_att"), ("designed_rush", "designed_rush")):
            if (v.get(sk) or {}).get("mean") is not None:
                out[k] = {"value": v[sk]["mean"], "source": "SIM_SCRIPT"}
    if "pass_att" not in out and market_qb_attempts is not None:
        out["pass_att"] = {"value": market_qb_attempts, "source": "MARKET_LADDER (QB pass-attempts ladder median)"}
    for k in ("plays", "pass_att", "designed_rush"):
        if k not in out and prior.get(k) is not None:
            out[k] = {"value": prior[k], "source": f"PRIOR_MEAN ({prior['basis']}, n={prior['n']})"}
    return out


def script_explains(stat_volume: str, err_lr: float | None, team_margin: float | None, combined_plays: float | None) -> bool:
    """Would the realized game script, by the volume model's own mechanism, push this team volume in the
    direction it missed? Passing rises when trailing and falls when leading; rushing the reverse; all volume
    falls in a low-possession game."""
    if err_lr is None or abs(err_lr) <= VOLUME_OFF:
        return False
    if combined_plays is not None and combined_plays < LOW_POSSESSION_PLAYS and err_lr < 0:
        return True
    if team_margin is None:
        return False
    if stat_volume == "pass_att":
        return (team_margin <= -BLOWOUT_MARGIN + 3 and err_lr > 0) or (team_margin >= BLOWOUT_MARGIN - 3 and err_lr < 0)
    if stat_volume == "designed_rush":
        return (team_margin >= BLOWOUT_MARGIN - 3 and err_lr > 0) or (team_margin <= -BLOWOUT_MARGIN + 3 and err_lr < 0)
    return False


VOLUME_FOR_STAT = {"passing_yards": "pass_att", "completions": "pass_att", "attempts": "pass_att", "passing_tds": "pass_att",
                   "interceptions": "pass_att", "receiving_yards": "pass_att", "receptions": "pass_att",
                   "rushing_yards": "designed_rush", "carries": "designed_rush", "touchdowns": "plays", "rush_rec_yards": "plays"}


def miss_layer(aut: dict, *, team_err_lr: float | None, explained: bool, role_low: bool) -> str:
    """The first layer of the hierarchy that left expectation, for one canonical player autopsy record."""
    c = aut.get("classification")
    if c == "INSUFFICIENT_DATA":
        return LAYER_INSUFFICIENT
    if c == "AVAILABILITY_MISS":
        return LAYER_AVAILABILITY
    if c == "NO_LARGE_MISS":
        return LAYER_NO_MISS
    if c in ("TEAM_VOLUME_MISS", "OPPORTUNITY_MISS"):
        off = team_err_lr is not None and abs(team_err_lr) > VOLUME_OFF
        opp = _f(aut.get("opportunity_log_ratio"))
        same_dir = off and opp is not None and (team_err_lr > 0) == (opp > 0)
        if same_dir and explained:
            return LAYER_SCRIPT_VOLUME
        if same_dir:
            return LAYER_TEAM_VOLUME
        return LAYER_ROLE if role_low else LAYER_SHARE
    if c == "EFFICIENCY_MISS":
        return LAYER_EFFICIENCY
    return LAYER_VARIANCE


# ------------------------------------------------------------------------------------------------ assembly
def autopsy_games(*, games: list, pbp_by_game: dict, volumes_by_game: dict, schedule: list, market: dict,
                  sim_scripts: dict | None = None) -> list:
    """One realized-script record per game. `market[game_id]` = {home_margin, total, home_points, away_points,
    favorite, qb_attempts: {team: median}} from the board's latest-pregame ladders."""
    out = []
    for g in games:
        gid, home, away = g["game_id"], g["home"], g["away"]
        plays = pbp_by_game.get(gid) or []
        flow = game_flow(plays, home, away)
        vol = volumes_by_game.get(gid) or {}
        mk = market.get(gid) or {}
        rec = {"script_autopsy_version": SCRIPT_AUTOPSY_VERSION, "game_id": gid, "season": g["season"], "week": g["week"],
               "home": home, "away": away, "status": "OK" if flow and vol else "NO_PLAY_BY_PLAY", "flow": flow, "volume": vol,
               "market": {k: mk.get(k) for k in ("home_margin", "total", "home_points", "away_points", "favorite")}}
        if not flow:
            out.append(rec)
            continue
        labels = realized_labels(flow, vol, home=home, away=away, market_favorite=mk.get("favorite"), market_total=mk.get("total"))
        rec["labels"], rec["primary_label"] = labels, primary_label(labels)
        rec["errors"] = {"margin": (flow["final_margin"] - mk["home_margin"]) if mk.get("home_margin") is not None else None,
                         "total": (flow["final_total"] - mk["total"]) if mk.get("total") is not None else None,
                         "home_points": (flow["final_home"] - mk["home_points"]) if mk.get("home_points") is not None else None,
                         "away_points": (flow["final_away"] - mk["away_points"]) if mk.get("away_points") is not None else None}
        teams = {}
        combined = sum((vol.get(t) or {}).get("plays", 0) for t in (home, away)) or None
        for t in (home, away):
            pri = prior_means(volumes_by_game, schedule, gid, t)
            exp = team_expectation(t, prior=pri, market_qb_attempts=(mk.get("qb_attempts") or {}).get(t),
                                   sim_team=((sim_scripts or {}).get(gid) or {}).get("teams", {}).get(t))
            act = vol.get(t) or {}
            margin_t = flow["final_margin"] if t == home else -flow["final_margin"]
            errs = {}
            for k, e in exp.items():
                lr = _lr(act.get(k), e["value"])
                errs[k] = {"expected": round(e["value"], 2), "actual": act.get(k), "log_ratio": lr, "source": e["source"],
                           "off": lr is not None and abs(lr) > VOLUME_OFF,
                           "script_explains": script_explains(k, lr, margin_t, combined)}
            teams[t] = {"final_margin": margin_t, "volume_vs_expectation": errs, "prior": pri}
        rec["teams"] = teams
        rec["combined_plays"] = combined
        out.append(rec)
    return out


def connect_players(canonical_autopsies: list, game_records: list, *, role_low=None) -> list:
    """Attach the team-volume and script context to every canonical player autopsy and assign its miss layer."""
    by_game = {g["game_id"]: g for g in game_records}
    role_low = role_low or (lambda a: (_f(a.get("p_plays")) is not None and _f(a.get("p_plays")) < 0.75)
                            or (_f(a.get("feature_n_prior")) is not None and _f(a.get("feature_n_prior")) < 4))
    out = []
    for a in canonical_autopsies:
        g = by_game.get(a.get("game_id")) or {}
        t = (g.get("teams") or {}).get(a.get("team")) or {}
        vk = VOLUME_FOR_STAT.get(a.get("stat"), "plays")
        ve = (t.get("volume_vs_expectation") or {}).get(vk) or {}
        lr, expl = ve.get("log_ratio"), bool(ve.get("script_explains"))
        layer = miss_layer(a, team_err_lr=lr, explained=expl, role_low=bool(role_low(a)))
        out.append({"game_id": a.get("game_id"), "week": a.get("week"), "team": a.get("team"), "player_id": a.get("player_id"),
                    "player_name": a.get("player_name"), "stat": a.get("stat"), "classification": a.get("classification"),
                    "robust_z": a.get("robust_z"), "large_miss": a.get("large_miss"),
                    "opportunity_log_ratio": a.get("opportunity_log_ratio"), "efficiency_log_ratio": a.get("efficiency_log_ratio"),
                    "team_volume_key": vk, "team_volume_log_ratio": lr, "team_volume_source": ve.get("source"),
                    "script_explains_team_volume": expl, "game_primary_label": g.get("primary_label"),
                    "game_labels": g.get("labels"), "miss_layer": layer,
                    "better_game_script_could_have_helped": layer == LAYER_SCRIPT_VOLUME})
    return out


def summarize(game_records: list, player_links: list) -> dict:
    labels = Counter(l for g in game_records for l in (g.get("labels") or []))
    prim = Counter(g.get("primary_label") for g in game_records if g.get("status") == "OK")
    layers = Counter(p["miss_layer"] for p in player_links)
    meaningful = [p for p in player_links if p["miss_layer"] not in (LAYER_NO_MISS, LAYER_INSUFFICIENT)]
    by_label = defaultdict(Counter)
    for p in meaningful:
        by_label[p.get("game_primary_label")][p["miss_layer"]] += 1
    vol_off = Counter()
    vol_dir = Counter()
    for g in game_records:
        for t, d in (g.get("teams") or {}).items():
            for k, e in (d.get("volume_vs_expectation") or {}).items():
                if e.get("off"):
                    vol_off[k] += 1
                    vol_dir[(k, "over" if e["log_ratio"] > 0 else "under", "script-explained" if e["script_explains"] else "not-explained")] += 1
    errs = [g["errors"] for g in game_records if g.get("errors")]
    def mae(k):
        v = [abs(e[k]) for e in errs if e.get(k) is not None]
        return (sum(v) / len(v)) if v else None
    # SENSITIVITY: anytime-touchdown props are lumpy, and their "opportunity" is total touches, so nearly all of their
    # variation reads as share. Their weight in the layer mix is reported, never hidden inside it.
    no_td = [p for p in meaningful if p.get("stat") != "touchdowns"]
    layers_no_td = Counter(p["miss_layer"] for p in no_td)
    return {"n_games": len(game_records), "n_games_ok": sum(1 for g in game_records if g.get("status") == "OK"),
            "n_meaningful_excluding_touchdowns": len(no_td),
            "miss_layers_excluding_touchdowns": dict(layers_no_td.most_common()),
            "label_counts": dict(labels.most_common()), "primary_label_counts": dict(prim.most_common()),
            "market_mae": {"margin": mae("margin"), "total": mae("total"), "home_points": mae("home_points"), "away_points": mae("away_points")},
            "team_volume_off_counts": dict(vol_off), "team_volume_off_by_direction": {"|".join(k): v for k, v in vol_dir.most_common()},
            "n_player_units": len(player_links), "miss_layers": dict(layers.most_common()),
            "n_meaningful_misses": len(meaningful),
            "share_script_could_have_helped": (sum(1 for p in meaningful if p["better_game_script_could_have_helped"]) / len(meaningful)) if meaningful else None,
            "meaningful_layers_by_primary_label": {k: dict(v) for k, v in by_label.items()}}
