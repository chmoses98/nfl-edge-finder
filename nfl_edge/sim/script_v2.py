"""GAME SCRIPT V2: a canonical, mutually exclusive script lattice over the SAME simulated rows that priced the
contracts, the script x market matrix, and thesis dependency between markets. RESEARCH_ONLY; no authority.

Every simulated row of a ``SimResult`` is one internally coherent world: a final margin and total, each team's
plays / pass rate / dropbacks / designed rushes on that row, and every player's opportunity and production on
that row. This module only SORTS those rows -- it draws no random number (pinned by test), so it can never
change a projection, and every probability it reports is a row count divided by the row count.

THE LATTICE (sim-script-2.0.0; preregistered in research/game_script_v2/PREREGISTRATION.md, section 2)

    control  x  scoring  =  nine cells, exhaustive and mutually exclusive

    control   FAVORITE_CONTROL  favourite-oriented final margin  >  ONE_SCORE (8)
              COMPETITIVE       within one score either way (ties included)
              UNDERDOG_CONTROL  favourite-oriented final margin  < -ONE_SCORE
    scoring   HIGH_SCORING      total >= centre total + SHOOTOUT_OVER (10)
              NORMAL_SCORING    otherwise
              LOW_SCORING       total <= centre total - LOW_SCORING_UNDER (10)

The favourite is read from the centre the simulation USED (``GameInput.spread_home``); a pick'em (centre 0) is
oriented on the home team and says "home"/"away". The thresholds are imported from
``nfl_edge.research.script_autopsy`` so predicted and realized definitions cannot drift, and realized games are
classified by the same functions (``cell_index`` / ``event_indicators``) applied to the realized outcome.

These are FINAL-STATE cells. The simulator draws no scoring sequence, so "controls" here means "won by more
than one score", not "led throughout": lead changes, time leading, early blowouts and late comebacks are not
simulated and are listed under ``not_simulated`` instead of being estimated.

PROVENANCE. The (margin, total) of every row is the market centre plus the incumbent's historical residual
bank. A script probability is therefore MARKET_CENTRED_GAME: a 62% favourite-control world says how the
market-centred distribution splits, not that the model found a football edge on the side.
"""
from __future__ import annotations

import numpy as np

from nfl_edge.research.script_autopsy import (BLOWOUT_MARGIN, HIGH_PASS_ATTEMPTS, LOW_POSSESSION_PLAYS,
                                              LOW_SCORING_UNDER, ONE_SCORE, RUN_CONTROL_RUSHES, SHOOTOUT_OVER)

SCRIPT_V2_VERSION = "sim-script-2.0.0"
PROVENANCE = "MARKET_CENTRED_GAME"
AUTHORITY = "RESEARCH_ONLY: no script, matrix or dependency number creates a BET state or changes an edge, a threshold, a stake or a probability"

CONTROL = ("FAVORITE_CONTROL", "COMPETITIVE", "UNDERDOG_CONTROL")
SCORING = ("HIGH_SCORING", "NORMAL_SCORING", "LOW_SCORING")
CELLS = tuple(f"{c}|{s}" for c in CONTROL for s in SCORING)
N_CELLS = len(CELLS)

MATERIAL_MASS = 0.10          # a script with at least this probability is "material"
THIN_ROWS = 200               # a cell with fewer rows reports P(cash | s) but never sets the floor
ROBUSTNESS_LEVELS = (0.50, 0.55, 0.60)
QS = (0.10, 0.50, 0.90)

EVENTS = ("one_score", "blowout_17", "favorite_wins", "favorite_controls", "upset", "shootout", "low_scoring",
          "low_possession", "high_volume_passing", "run_heavy_control")
FAVORITE_EVENTS = ("favorite_wins", "favorite_controls", "upset")
NOT_SIMULATED = ("lead changes", "time leading", "scoring sequence / quarter scores", "early blowout",
                 "late comeback", "red-zone trips", "routes and snaps", "drive counts")


# ------------------------------------------------------------------------------------------ the lattice
def orientation(spread_home: float) -> dict:
    """Favourite orientation from the centre the simulation used. sign = +1 orients on home, -1 on away."""
    s = float(spread_home)
    if not np.isfinite(s):
        raise ValueError("the centre spread is not finite")
    if s > 0:
        return {"sign": 1, "pickem": False, "favorite": "HOME"}
    if s < 0:
        return {"sign": -1, "pickem": False, "favorite": "AWAY"}
    return {"sign": 1, "pickem": True, "favorite": None}


def control_index(fav_margin) -> np.ndarray:
    fm = np.asarray(fav_margin, float)
    return np.where(fm > ONE_SCORE, 0, np.where(fm < -ONE_SCORE, 2, 1)).astype(np.int8)


def scoring_index(total, centre_total: float) -> np.ndarray:
    t = np.asarray(total, float)
    return np.where(t >= centre_total + SHOOTOUT_OVER, 0, np.where(t <= centre_total - LOW_SCORING_UNDER, 2, 1)).astype(np.int8)


def cell_index(margin, total, spread_home: float, total_line: float) -> np.ndarray:
    """Cell id in [0, 9) for each row (or for a realized game: pass length-1 arrays). One function for both."""
    o = orientation(spread_home)
    if not np.isfinite(float(total_line)):
        raise ValueError("the centre total is not finite")
    return (control_index(o["sign"] * np.asarray(margin, float)) * 3 + scoring_index(total, float(total_line))).astype(np.int8)


def classify(margin: float, total: float, spread_home: float, total_line: float) -> str:
    """The realized cell of one game -- the same function the simulated rows go through."""
    return CELLS[int(cell_index(np.array([margin]), np.array([total]), spread_home, total_line)[0])]


def cell_probabilities(cells: np.ndarray) -> np.ndarray:
    c = np.asarray(cells)
    if c.size == 0:
        raise ValueError("no rows")
    return np.bincount(c.astype(np.int64), minlength=N_CELLS)[:N_CELLS] / c.size


# ------------------------------------------------------------------------------------- marginal events
def event_indicators(margin, total, spread_home: float, total_line: float, *, home_plays=None, away_plays=None,
                     home_pass_att=None, away_pass_att=None, home_designed=None, away_designed=None) -> dict:
    """Boolean arrays (or None when not applicable / inputs absent) for the preregistered marginal events.
    The same function labels the simulated rows and the realized game."""
    m = np.asarray(margin, float); t = np.asarray(total, float)
    o = orientation(spread_home)
    fm = o["sign"] * m
    out = {"one_score": np.abs(m) <= ONE_SCORE, "blowout_17": np.abs(m) >= BLOWOUT_MARGIN,
           "shootout": t >= total_line + SHOOTOUT_OVER, "low_scoring": t <= total_line - LOW_SCORING_UNDER}
    if o["pickem"]:
        out.update({k: None for k in FAVORITE_EVENTS})
    else:
        out.update({"favorite_wins": fm > 0, "favorite_controls": fm > ONE_SCORE, "upset": fm < 0})
    if home_plays is not None and away_plays is not None:
        out["low_possession"] = (np.asarray(home_plays, float) + np.asarray(away_plays, float)) < LOW_POSSESSION_PLAYS
    else:
        out["low_possession"] = None
    if home_pass_att is not None and away_pass_att is not None:
        out["high_volume_passing"] = (np.asarray(home_pass_att, float) + np.asarray(away_pass_att, float)) >= HIGH_PASS_ATTEMPTS
    else:
        out["high_volume_passing"] = None
    if home_designed is not None and away_designed is not None:
        win = np.where(m > 0, np.asarray(home_designed, float), np.where(m < 0, np.asarray(away_designed, float), 0.0))
        out["run_heavy_control"] = (np.abs(m) > ONE_SCORE) & (win >= RUN_CONTROL_RUSHES)
    else:
        out["run_heavy_control"] = None
    return {k: out[k] for k in EVENTS}


def _team_arrays(res, gi):
    H = res.team.get(gi.home.team) or {}; A = res.team.get(gi.away.team) or {}
    return H, A


def sim_events(res, gi) -> dict:
    H, A = _team_arrays(res, gi)
    return event_indicators(res.margin, res.total, gi.spread_home, gi.total_line,
                            home_plays=H.get("plays"), away_plays=A.get("plays"),
                            home_pass_att=H.get("pass_att"), away_pass_att=A.get("pass_att"),
                            home_designed=H.get("designed_rush"), away_designed=A.get("designed_rush"))


# --------------------------------------------------------------------------------------- summaries
def _q(a) -> dict | None:
    a = np.asarray(a, float)
    if a.size == 0:
        return None
    out = {"mean": round(float(a.mean()), 3)}
    for q in QS:
        out[f"p{int(q * 100):02d}"] = round(float(np.quantile(a, q)), 3)
    return out


def _names(ti) -> dict:
    df = getattr(ti, "players", None)
    if df is None or not hasattr(df, "columns") or "player_id" not in df.columns:
        return {}
    out = {}
    for _, r in df.iterrows():
        out[r["player_id"]] = {"name": r.get("player_name"), "position": r.get("position")}
    return out


def _major_players(res, team: str, k: int) -> list:
    """The team's players with the largest expected opportunity (targets + carries + pass attempts) over all rows."""
    cand = []
    for pid, P in res.player.items():
        if P.get("team") != team or str(pid).startswith("OTHER"):
            continue
        opp = np.asarray(P.get("targets", 0), float) + np.asarray(P.get("carries", 0), float) + np.asarray(P.get("attempts", 0), float)
        cand.append((float(opp.mean()), pid))
    cand.sort(key=lambda x: (-x[0], x[1]))
    return [pid for m, pid in cand[:k] if m >= 0.5]


def _labels(cell: str, o: dict, home: str, away: str, centre_total: float, margin_q: dict | None, total_q: dict | None) -> dict:
    """Human-readable text generated FROM the cell definition and the cell's own quantiles."""
    ctrl, scor = cell.split("|")
    if o["pickem"]:
        fav, dog, fav_word, dog_word = home, away, "home", "away"
    else:
        fav, dog = (home, away) if o["favorite"] == "HOME" else (away, home)
        fav_word, dog_word = "favourite", "underdog"
    fmed = None if margin_q is None else o["sign"] * margin_q["p50"]
    tmed = None if total_q is None else total_q["p50"]
    if ctrl == "FAVORITE_CONTROL":
        c_short, c_long = f"{fav_word} controls", f"{fav} ({fav_word}) wins by more than one score"
    elif ctrl == "UNDERDOG_CONTROL":
        c_short, c_long = f"{dog_word} controls", f"{dog} ({dog_word}) wins by more than one score"
    else:
        c_short, c_long = "competitive", f"final margin within one score ({ONE_SCORE} points) either way"
    if scor == "HIGH_SCORING":
        s_short, s_long = "high scoring", f"total {centre_total + SHOOTOUT_OVER:g}+ (centre {centre_total:g})"
    elif scor == "LOW_SCORING":
        s_short, s_long = "low scoring", f"total {centre_total - LOW_SCORING_UNDER:g} or fewer (centre {centre_total:g})"
    else:
        s_short, s_long = "normal scoring", f"total within 10 of the centre {centre_total:g}"
    detail = []
    if fmed is not None:
        detail.append(f"median {('home' if o['pickem'] else fav_word)}-oriented margin {fmed:+g}")
    if tmed is not None:
        detail.append(f"median total {tmed:g}")
    return {"short": f"{c_short} / {s_short}", "long": f"{c_long}; {s_long}" + (f" ({', '.join(detail)})" if detail else "")}


def script_v2_summary(res, gi, coherence: dict | None = None, *, top_players: int = 6, weather: dict | None = None) -> dict:
    """The nine-cell script distribution of one simulated game, every cell's own state, and the marginal events.
    Pure function of the SimResult: no random number, no mutation."""
    margin = np.asarray(res.margin, float); total = np.asarray(res.total, float)
    n = int(margin.size)
    o = orientation(gi.spread_home)
    cells = cell_index(margin, total, gi.spread_home, gi.total_line)
    probs = cell_probabilities(cells)
    H, A = _team_arrays(res, gi)
    home, away = gi.home.team, gi.away.team
    names = {**_names(gi.home), **_names(gi.away)}
    majors = {home: _major_players(res, home, top_players), away: _major_players(res, away, top_players)}
    vol_keys = ("plays", "pass_att", "dropbacks", "designed_rush", "pass_rate", "targets")
    cell_out = []
    for k, name in enumerate(CELLS):
        msk = cells == k
        cnt = int(msk.sum())
        rec = {"cell": name, "probability": float(probs[k]), "n_rows": cnt, "thin": cnt < THIN_ROWS,
               "material": bool(probs[k] >= MATERIAL_MASS)}
        if cnt == 0:
            rec["labels"] = _labels(name, o, home, away, gi.total_line, None, None)
            cell_out.append(rec)
            continue
        mq, tq = _q(margin[msk]), _q(total[msk])
        rec["labels"] = _labels(name, o, home, away, gi.total_line, mq, tq)
        rec.update({"home_points": _q(np.asarray(res.home_points)[msk]), "away_points": _q(np.asarray(res.away_points)[msk]),
                    "home_margin": mq, "total": tq})
        teams = {}
        for team, T in ((home, H), (away, A)):
            tv = {key: _q(np.asarray(T[key])[msk]) for key in vol_keys if key in T}
            pls = []
            tgt_shares = []
            tt = np.asarray(T.get("targets", np.zeros(n)), float)[msk]
            for pid in majors[team]:
                P = res.player[pid]
                tg = np.asarray(P.get("targets", 0), float)[msk]; ca = np.asarray(P.get("carries", 0), float)[msk]
                prow = {"player_id": pid, **names.get(pid, {}), "targets": _q(tg), "carries": _q(ca)}
                if "attempts" in P:
                    prow["pass_attempts"] = _q(np.asarray(P["attempts"], float)[msk])
                opp = tg + ca
                prow["opportunity_cv"] = round(float(opp.std() / opp.mean()), 3) if opp.mean() > 0 else None
                prow["p_active"] = round(float(np.asarray(P.get("active", np.ones(n)), bool)[msk].mean()), 4)
                if tt.sum() > 0:
                    sh = float(tg.sum() / tt.sum())
                    prow["target_share"] = round(sh, 4)
                pls.append(prow)
            for pid, P in res.player.items():
                if P.get("team") == team and tt.sum() > 0:
                    tgt_shares.append(float(np.asarray(P.get("targets", 0), float)[msk].sum() / tt.sum()))
            tv["target_concentration_hhi"] = round(float(sum(s * s for s in tgt_shares)), 4) if tgt_shares else None
            tv["major_players"] = pls
            teams[team] = tv
        rec["teams"] = teams
        cell_out.append(rec)
    ev = sim_events(res, gi)
    events = {k: (None if v is None else round(float(np.mean(v)), 4)) for k, v in ev.items()}
    ranked = sorted(cell_out, key=lambda c: (-c["probability"], CELLS.index(c["cell"])))
    primary = [{"cell": c["cell"], "label": c["labels"]["short"], "probability": round(c["probability"], 4)} for c in ranked]
    return {"script_v2_version": SCRIPT_V2_VERSION, "game_id": res.game_id, "n_rows": n, "provenance": PROVENANCE,
            "authority": AUTHORITY, "betting_authorized": False, "rng_draws": 0,
            "orientation": {"favorite": (None if o["pickem"] else (home if o["favorite"] == "HOME" else away)),
                            "pickem": o["pickem"], "home": home, "away": away},
            "centre": {"home_margin": gi.spread_home, "total": gi.total_line, "source": gi.center_source},
            "thresholds": {"one_score": ONE_SCORE, "blowout": BLOWOUT_MARGIN, "shootout_over": SHOOTOUT_OVER,
                           "low_scoring_under": LOW_SCORING_UNDER, "low_possession_plays": LOW_POSSESSION_PLAYS,
                           "high_pass_attempts": HIGH_PASS_ATTEMPTS, "run_control_rushes": RUN_CONTROL_RUSHES},
            "cells": cell_out, "probability_sum": float(probs.sum()), "primary_scripts": primary,
            "marginal_events": events, "not_simulated": list(NOT_SIMULATED),
            "coherence_ok": None if coherence is None else bool(coherence.get("ok")),
            "weather": weather_block(weather)}


def weather_block(weather: dict | None) -> dict:
    """Current (point-in-time) weather is shown for interpretation; it never alters a simulated probability."""
    base = {"weather_model_status": "NOT_IN_MODEL",
            "note": "weather does not enter the simulation; shown for manual/contextual interpretation only"}
    if not weather:
        return {**base, "state": "UNAVAILABLE"}
    keep = ("roof", "retrieved_at", "lead_hours", "forecast_hour", "temperature_2m", "wind_speed_10m", "wind_gusts_10m",
            "precipitation_probability", "precipitation", "source_file")
    return {**base, "state": "FORECAST_AT_CUTOFF", **{k: weather.get(k) for k in keep}}


# ------------------------------------------------------------------------------------- contracts
# Exactly the pricer's semantics (sim.prospective.price_slate); tests pin mean(cash) == p_football.
GAME_FAMILIES = ("GAME_WINNER", "SPREAD", "TOTAL", "TEAM_TOTAL")


def contract_cash(contract: dict, res, gi, player_map: dict | None = None) -> tuple[np.ndarray | None, str, str | None]:
    """Per-row cash value (0, 0.5 or 1) of one contract on the simulated rows, or (None, support_state, reason).

    A contract the simulation cannot settle is REFUSED with a reason; nothing is guessed."""
    from nfl_edge.sim.prospective import GRID_MAX, STAT_MAP
    fam = contract.get("family")
    if contract.get("period") not in ("FULL", None):
        return None, "UNSUPPORTED_PERIOD", f"period {contract.get('period')} is not simulated"
    team = contract.get("team")
    if fam in GAME_FAMILIES and fam != "TOTAL" and team not in (gi.home.team, gi.away.team):
        return None, "UNSUPPORTED_IDENTITY", f"team {team!r} is not in {gi.game_id}"
    m = np.asarray(res.margin, float)
    if fam == "GAME_WINNER":
        win = m > 0 if team == gi.home.team else m < 0
        return win.astype(float) + 0.5 * (m == 0), "MARKET_CENTRED_GAME", None
    if fam == "SPREAD":
        if contract.get("floor_strike") is None:
            return None, "UNSUPPORTED_RULES", "spread contract without floor_strike"
        x = m if team == gi.home.team else -m
        return (x > float(contract["floor_strike"])).astype(float), "MARKET_CENTRED_GAME", None
    if fam == "TOTAL":
        if contract.get("threshold") is None:
            return None, "UNSUPPORTED_RULES", "total contract without threshold"
        return (np.asarray(res.total, float) >= float(contract["threshold"])).astype(float), "MARKET_CENTRED_GAME", None
    if fam == "TEAM_TOTAL":
        if contract.get("threshold") is None:
            return None, "UNSUPPORTED_RULES", "team-total contract without threshold"
        x = np.asarray(res.home_points if team == gi.home.team else res.away_points, float)
        return (x >= float(contract["threshold"])).astype(float), "MARKET_CENTRED_GAME", None
    if fam == "PLAYER_STAT":
        st = STAT_MAP.get(contract.get("stat"))
        if st is None:
            return None, "UNSUPPORTED_STAT", f"no simulated statistic for {contract.get('stat')}"
        gs = contract.get("player_id") or (player_map or {}).get(contract.get("player_kalshi_id"))
        if not gs:
            return None, "UNSUPPORTED_IDENTITY", "player not resolved to a GSIS id"
        if gs not in res.player:
            return None, "NOT_ELIGIBLE", "player not in the point-in-time eligible set"
        if contract.get("operator") != ">=" or contract.get("threshold") is None:
            return None, "UNSUPPORTED_RULES", f"operator {contract.get('operator')}"
        if st not in res.player[gs]:
            return None, "UNSUPPORTED_STAT", f"{st} is not simulated for this player"
        x = np.clip(np.round(np.asarray(res.player[gs][st], float)), 0, GRID_MAX[st]).astype(int)
        kk = int(np.ceil(float(contract["threshold"]) - 1e-12))
        if kk <= 0:
            return np.ones(x.size), "SIMULATED", None
        if kk > GRID_MAX[st]:
            return np.zeros(x.size), "SIMULATED", None
        return (x >= kk).astype(float), "SIMULATED", None
    return None, "UNSUPPORTED_FAMILY", f"family {fam} is not settled from the simulated rows"


def market_matrix(cash: np.ndarray, cells: np.ndarray) -> dict:
    """P(cash), P(cash | s) for every cell, contributions, floor, robustness and concentration."""
    c = np.asarray(cash, float); s = np.asarray(cells).astype(np.int64)
    if c.shape != s.shape:
        raise ValueError("cash and cells must be the same simulated rows")
    n = c.size
    p = float(c.mean())
    counts = np.bincount(s, minlength=N_CELLS)[:N_CELLS]
    sums = np.bincount(s, weights=c, minlength=N_CELLS)[:N_CELLS]
    rows, recon = [], 0.0
    for k in range(N_CELLS):
        ps = counts[k] / n
        pc = (sums[k] / counts[k]) if counts[k] else None
        contrib = sums[k] / n
        recon += contrib
        rows.append({"cell": CELLS[k], "p_script": float(ps), "n_rows": int(counts[k]),
                     "p_cash_given_script": None if pc is None else float(pc), "contribution": float(contrib),
                     "material": bool(ps >= MATERIAL_MASS), "thin": bool(counts[k] < THIN_ROWS)})
    floor_rows = [r for r in rows if r["material"] and not r["thin"]]
    rob = {f"{q:.2f}": float(sum(r["p_script"] for r in rows if r["p_cash_given_script"] is not None and r["p_cash_given_script"] >= q))
           for q in ROBUSTNESS_LEVELS}
    fail = float(sum(r["p_script"] for r in rows if r["p_cash_given_script"] is not None and r["p_cash_given_script"] < 0.50))
    hhi = float(sum((r["contribution"] / p) ** 2 for r in rows)) if p > 0 else None
    return {"p_cash": p, "by_script": rows,
            "major_script_floor": min((r["p_cash_given_script"] for r in floor_rows), default=None),
            "script_robustness": rob, "failure_script_mass": fail, "win_contribution_hhi": hhi,
            "reconciliation_error": float(abs(recon - p))}


def script_market_matrix(res, gi, contracts: list, player_map: dict | None = None) -> dict:
    """The matrix for every contract, refused ones included with their reason; plus the cash rows for dependency."""
    cells = cell_index(res.margin, res.total, gi.spread_home, gi.total_line)
    out, cash = [], {}
    for c in contracts:
        key = c.get("ticker") or c.get("id")
        v, state, why = contract_cash(c, res, gi, player_map)
        rec = {"ticker": key, "family": c.get("family"), "team": c.get("team"), "stat": c.get("stat"),
               "player_name": c.get("player_name"), "threshold": c.get("threshold"), "floor_strike": c.get("floor_strike"),
               "support_state": state, "support_reason": why}
        if v is not None:
            rec.update(market_matrix(v, cells))
            cash[key] = v
        out.append(rec)
    return {"script_v2_version": SCRIPT_V2_VERSION, "game_id": res.game_id, "cells": list(CELLS), "provenance": PROVENANCE,
            "authority": AUTHORITY, "contracts": out, "_cash": cash}


# ------------------------------------------------------------------------------------ thesis dependency
def pair_dependency(a: np.ndarray, b: np.ndarray) -> dict:
    a = np.asarray(a, float); b = np.asarray(b, float)
    if a.shape != b.shape:
        raise ValueError("both markets must be read on the same simulated rows")
    pa, pb = float(a.mean()), float(b.mean())
    joint = float((a * b).mean())
    sa, sb = float(a.std()), float(b.std())
    corr = float(((a - pa) * (b - pb)).mean() / (sa * sb)) if sa > 0 and sb > 0 else None
    union = float((a + b - a * b).mean())
    return {"p_a": pa, "p_b": pb, "joint_cash": joint, "cash_correlation": corr,
            "p_a_given_b": joint / pb if pb > 0 else None, "p_b_given_a": joint / pa if pa > 0 else None,
            "shared_failure_mass": float(((1 - a) * (1 - b)).mean()),
            "lift": joint / (pa * pb) if pa > 0 and pb > 0 else None,
            "jaccard_winning_rows": joint / union if union > 0 else None}


def dependency_matrix(cash: dict) -> dict:
    """Symmetric pairwise dependency over markets of ONE game, plus the pairs sorted by cash correlation."""
    keys = sorted(cash)
    k = len(keys)
    corr = [[None] * k for _ in range(k)]
    pairs = []
    for i in range(k):
        corr[i][i] = 1.0 if float(np.std(cash[keys[i]])) > 0 else None
        for j in range(i + 1, k):
            d = pair_dependency(cash[keys[i]], cash[keys[j]])
            corr[i][j] = corr[j][i] = d["cash_correlation"]
            pairs.append({"a": keys[i], "b": keys[j], **d})
    pairs.sort(key=lambda r: -(r["cash_correlation"] if r["cash_correlation"] is not None else -2.0))
    return {"markets": keys, "cash_correlation": corr, "pairs": pairs, "authority": AUTHORITY}


# ------------------------------------------------------------------------------- the per-game document
MIN_ABS_CORR = 0.30           # dependency pairs reported (descriptive filter, no authority)
MAX_PAIRS = 50


def _ladder_key(c: dict) -> tuple:
    return (c.get("family"), c.get("team"), c.get("stat"), c.get("player_kalshi_id") or c.get("player_id"))


def game_document(res, gi, coherence: dict, contracts: list, player_map: dict | None = None, *, weather: dict | None = None) -> dict:
    """GAME SCRIPT V2 for one simulated game: the lattice, every contract's script matrix, and thesis dependency
    among the headline rung of each ladder (the rung whose simulated probability is nearest 0.50). A game that
    failed coherence gets no script numbers at all -- the preregistered gate is zero coherence failures."""
    if not (coherence or {}).get("ok"):
        return {"script_v2_version": SCRIPT_V2_VERSION, "game_id": res.game_id, "state": "UNSUPPORTED_COHERENCE",
                "authority": AUTHORITY, "betting_authorized": False}
    summary = script_v2_summary(res, gi, coherence, weather=weather)
    mx = script_market_matrix(res, gi, contracts, player_map)
    cash = mx.pop("_cash")
    compact = []
    for c in mx["contracts"]:
        rec = {k: c.get(k) for k in ("ticker", "family", "team", "stat", "player_name", "threshold", "floor_strike",
                                     "support_state", "support_reason")}
        if "p_cash" in c:
            rec.update({"p_cash": round(c["p_cash"], 5),
                        "p_cash_given_script": [None if r["p_cash_given_script"] is None else round(r["p_cash_given_script"], 4)
                                                for r in c["by_script"]],
                        "major_script_floor": None if c["major_script_floor"] is None else round(c["major_script_floor"], 4),
                        "script_robustness": {k: round(v, 4) for k, v in c["script_robustness"].items()},
                        "failure_script_mass": round(c["failure_script_mass"], 4),
                        "win_contribution_hhi": None if c["win_contribution_hhi"] is None else round(c["win_contribution_hhi"], 4),
                        "reconciliation_error": c["reconciliation_error"]})
        compact.append(rec)
    by_ladder = {}
    for c in contracts:
        key = c.get("ticker") or c.get("id")
        if key in cash:
            p = float(cash[key].mean())
            k = _ladder_key(c)
            if k not in by_ladder or abs(p - 0.5) < abs(by_ladder[k][1] - 0.5):
                by_ladder[k] = (key, p)
    head = {key: cash[key] for key, _ in by_ladder.values()}
    dep = dependency_matrix(head)
    pairs = [{k: (round(v, 4) if isinstance(v, float) else v) for k, v in p.items()} for p in dep["pairs"]
             if p["cash_correlation"] is not None and abs(p["cash_correlation"]) >= MIN_ABS_CORR][:MAX_PAIRS]
    return {"script_v2_version": SCRIPT_V2_VERSION, "game_id": res.game_id, "state": "OK", "authority": AUTHORITY,
            "betting_authorized": False, "provenance": PROVENANCE, "summary": summary, "cells": list(CELLS),
            "p_script": [c["probability"] for c in summary["cells"]], "contracts": compact,
            "dependency": {"headline_markets": sorted(head), "pairs": pairs, "min_abs_corr": MIN_ABS_CORR,
                           "note": "pairs among each ladder's headline rung, |cash correlation| >= 0.30; descriptive, no staking consequence"}}
