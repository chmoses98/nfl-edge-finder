"""NFL profitability postmortem from REAL records only: settled owner wagers, execution prices, published closes, the nflverse
schedule/results table, and (where it exists) the shadow-model ledger. RESEARCH ONLY: nothing here feeds a stake, a card or a model.

STANDARDS (each is enforced in code, not only stated)
    * Fees are counted once: stake = price * contracts + fees (`entry_cost` from the position lifecycle); pnl is net of fees.
    * Every interval is a 95% GAME-CLUSTERED bootstrap: positions on one game settle on one game state and are one observation.
    * "Fair-price null": a contract bought at price p pays with probability p; excess = contracts * (outcome - p). z is the
      cluster-robust (sandwich) statistic sum(excess) / sqrt(sum over games of excess_game^2). Fees are shown separately.
    * Multiple looks are Bonferroni-corrected over the family of cells tested in the same table. A cell chosen after seeing the
      result is a LEAD, never a finding (`label`).
    * True closes (the published canonical Kalshi close) and proxies are never mixed; a proxy is not computed here.
    * Predictive accuracy (Brier/log-loss against outcomes) is reported apart from profitability (return after price and fees).
    * No price, fill or probability is invented. The owner's wagers carry NO recorded model probability, thesis or recommendation id;
      the only model probabilities in the repository are the SHADOW model's point-in-time observations, which are joined by ticker
      and time and labelled as the shadow model's, never as the owner's.
"""
from __future__ import annotations

import math
import random
import re
from collections import defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import numpy as np

import nfl_edge.handicap.schedule_kickoffs as SK  # exact-module import: the report-isolation audit expands `from package import x` to the whole package

VERSION = "nfl-wager-loss-structure-1.0.0"
SEED = 20261104
_ET = ZoneInfo("America/New_York")
_MONTHS = SK._MONTHS


# ----------------------------------------------------------------------------------------------------------------- statistics

def norm_sf(z: float) -> float:
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def p_two_sided(z: float | None) -> float | None:
    return None if z is None else min(1.0, 2.0 * norm_sf(abs(z)))


def bonferroni_alpha(m: int, alpha: float = 0.05) -> float:
    return alpha / max(1, m)


def _clusters(rows: list, cluster, fields: tuple) -> np.ndarray:
    """(n_clusters, len(fields)) matrix of per-cluster sums. A row whose cluster is None is its own cluster."""
    acc: dict = defaultdict(lambda: np.zeros(len(fields)))
    for i, r in enumerate(rows):
        k = cluster(r)
        k = ("solo", i) if k in (None, "") else k
        acc[k] += np.array([float(r[f]) for f in fields])
    return np.array(list(acc.values())) if acc else np.zeros((0, len(fields)))


def boot_ratio(rows: list, num: str, den: str, *, cluster=lambda r: r.get("game_key"), n_boot: int = 4000, seed: int = SEED,
               alpha: float = 0.05) -> dict:
    """sum(num)/sum(den) with a 95% game-clustered percentile interval."""
    m = _clusters(rows, cluster, (num, den))
    if len(m) == 0 or m[:, 1].sum() == 0:
        return {"n": len(rows), "clusters": int(len(m)), "estimate": None, "lo95": None, "hi95": None}
    est = float(m[:, 0].sum() / m[:, 1].sum())
    if len(m) < 3:
        return {"n": len(rows), "clusters": int(len(m)), "estimate": round(est, 4), "lo95": None, "hi95": None}
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(m), size=(n_boot, len(m)))
    s = m[idx].sum(axis=1)
    ok = s[:, 1] != 0
    r = np.sort(s[ok, 0] / s[ok, 1])
    lo_i, hi_i = int((alpha / 2) * len(r)), min(len(r) - 1, int((1 - alpha / 2) * len(r)))
    return {"n": len(rows), "clusters": int(len(m)), "estimate": round(est, 4),
            "lo95": round(float(r[lo_i]), 4), "hi95": round(float(r[hi_i]), 4)}


def boot_mean(rows: list, val: str, *, cluster=lambda r: r.get("game_key"), n_boot: int = 4000, seed: int = SEED) -> dict:
    for r in rows:
        r["_one"] = 1.0
    out = boot_ratio(rows, val, "_one", cluster=cluster, n_boot=n_boot, seed=seed)
    for r in rows:
        r.pop("_one", None)
    return out


def fair_null(rows: list, *, cluster=lambda r: r.get("game_key")) -> dict:
    """Excess over the fair-price null for rows with `qty`, `price`, `outcome` (1 = the held side paid), `fees`.

    excess_i = qty * (outcome - price): zero in expectation if the price was the true probability. `z` is cluster-robust
    (sandwich, mean-zero under the null); `z_indep` is the textbook independent-bet z for comparison."""
    ok = [r for r in rows if r.get("outcome") is not None and r.get("price") is not None and r.get("qty")]
    if not ok:
        return {"n": 0}
    for r in ok:
        r["_ex"] = r["qty"] * (r["outcome"] - r["price"])
        r["_ex2"] = 0.0
    m = _clusters(ok, cluster, ("_ex",))
    ex = float(m.sum())
    var_c = float((m[:, 0] ** 2).sum())
    var_i = sum((r["qty"] ** 2) * r["price"] * (1 - r["price"]) for r in ok)
    fees = sum(r.get("fees") or 0.0 for r in ok)
    outlay = sum(r["qty"] * r["price"] + (r.get("fees") or 0.0) for r in ok)
    z = ex / math.sqrt(var_c) if var_c > 0 else None
    zi = ex / math.sqrt(var_i) if var_i > 0 else None
    # The normal approximation is invalid when fewer than 5 wins (or 5 losses) are expected: a cell of longshots with no wins has a
    # degenerate sandwich variance. Such cells get the exact Poisson-binomial win-count tail instead of a z.
    exp_w = sum(r["price"] for r in ok)
    approx_ok = exp_w >= 5 and (len(ok) - exp_w) >= 5
    wins = int(sum(1 for r in ok if r["outcome"]))
    tail_lo, tail_hi = _poisson_binomial_tails([r["price"] for r in ok], wins)
    if not approx_ok:
        z = zi = None
    for r in ok:
        r.pop("_ex", None)
        r.pop("_ex2", None)
    return {"n": len(ok), "clusters": int(len(m)), "excess_over_fair_per_outlay": round(ex / outlay, 4) if outlay else None,
            "fees_per_outlay": round(fees / outlay, 4) if outlay else None,
            "z_cluster": round(z, 2) if z is not None else None, "p_cluster": p_two_sided(z),
            "z_independent": round(zi, 2) if zi is not None else None, "normal_approximation_valid": approx_ok,
            "p_wins_at_or_below_observed_if_prices_fair": round(tail_lo, 5), "p_wins_at_or_above_observed_if_prices_fair": round(tail_hi, 5),
            "wins": wins, "expected_wins_at_prices": round(exp_w, 1)}


def _poisson_binomial_tails(ps: list, k: int) -> tuple:
    """(P(W <= k), P(W >= k)) for W = number of wins when each leg wins independently with its price."""
    dist = np.zeros(len(ps) + 1)
    dist[0] = 1.0
    for p in ps:
        dist[1:] = dist[1:] * (1 - p) + dist[:-1] * p
        dist[0] *= (1 - p)
    return float(dist[:k + 1].sum()), float(dist[k:].sum())


def label(p: float | None, m: int, n_cells: int | None = None) -> str:
    """PROVEN needs a pre-specified family; this repository's rule: after-the-fact cells are LEADS even when they clear Bonferroni."""
    if p is None:
        return "INSUFFICIENT"
    return "clears Bonferroni (still a LEAD: cell chosen after the result)" if p < bonferroni_alpha(m) else "does not clear Bonferroni"


# ----------------------------------------------------------------------------------------------------------------- tickers

_TEAM_SFX = re.compile(r"^([A-Z]{2,4}?)(\d+)$")


def parse_ticker(t: str | None) -> dict:
    parts = (t or "").split("-")
    series = parts[0] if parts else ""
    out = {"series": series, "game_code": parts[1] if len(parts) > 1 else None, "team": None, "line": None, "player": None}
    if series.startswith("KXMVE") or len(parts) < 3:
        return out
    tail = parts[2]
    if series in ("KXNFLSPREAD", "KXNFL1HSPREAD", "KXNFLTEAMTOTAL", "KXNFL1HTEAMTOTAL"):
        m = _TEAM_SFX.match(tail)
        if m:
            out["team"], out["line"] = SK.canon_team(m.group(1)), float(m.group(2))
    elif series in ("KXNFLTOTAL", "KXNFL1HTOTAL", "KXNFL1QTOTAL"):
        try:
            out["line"] = float(tail)
        except ValueError:
            pass
    elif series in ("KXNFLGAME", "KXNFL1H"):
        out["team"] = SK.canon_team(tail)
    else:
        out["player"] = tail
        try:
            out["line"] = float(parts[3]) if len(parts) > 3 else None
        except ValueError:
            pass
    return out


def canon_game_key(code: str | None) -> str | None:
    return SK.game_key_from_ticker_key(code) if code else None


# ----------------------------------------------------------------------------------------------------------------- schedule/results

def load_games(rows: list, season: int) -> dict:
    """{canonical game key -> game dict} from nflverse games rows (dicts). Scores are None until played."""
    out = {}
    for r in rows:
        if str(r.get("season")) != str(season):
            continue
        day = (r.get("gameday") or "").strip()
        clock = (r.get("gametime") or "").strip()
        away, home = SK.canon_team((r.get("away_team") or "").strip()), SK.canon_team((r.get("home_team") or "").strip())
        if not day or not away or not home:
            continue
        try:
            d = datetime.strptime(f"{day} {clock or '13:00'}", "%Y-%m-%d %H:%M").replace(tzinfo=_ET).date()
        except ValueError:
            continue

        def f(x):
            try:
                v = float(x)
                return v if math.isfinite(v) else None
            except (TypeError, ValueError):
                return None
        out[f"{d:%y}{_MONTHS[d.month - 1]}{d.day:02d}{away}{home}"] = {
            "week": int(r["week"]), "away": away, "home": home, "away_score": f(r.get("away_score")), "home_score": f(r.get("home_score")),
            "spread_line": f(r.get("spread_line")), "total_line": f(r.get("total_line")),
            "away_qb": (r.get("away_qb_name") or "").strip() or None, "home_qb": (r.get("home_qb_name") or "").strip() or None}
    return out


def outcome_yes(series: str, parsed: dict, game: dict | None) -> int | None:
    """1/0 for the YES side from final scores; None when scores or the market type are not derivable (period markets, props).

    Every full-game rung settles YES iff the quantity is >= the number in the ticker (the exchange's floor is N - 0.5)."""
    if not game or game.get("home_score") is None or game.get("away_score") is None:
        return None
    hs, as_ = game["home_score"], game["away_score"]
    n, team = parsed.get("line"), parsed.get("team")
    if series == "KXNFLSPREAD" and n is not None and team in (game["home"], game["away"]):
        margin = (hs - as_) if team == game["home"] else (as_ - hs)
        return int(margin >= n)
    if series == "KXNFLTOTAL" and n is not None:
        return int(hs + as_ >= n)
    if series == "KXNFLTEAMTOTAL" and n is not None and team in (game["home"], game["away"]):
        return int((hs if team == game["home"] else as_) >= n)
    if series == "KXNFLGAME" and team in (game["home"], game["away"]):
        if hs == as_:
            return None
        return int((hs > as_) == (team == game["home"]))
    return None


# ----------------------------------------------------------------------------------------------------------------- historical margin model

def fit_margin_model(games: list, *, max_margin: int = 40) -> dict:
    """Key-number-aware distribution of the HOME margin given the closing spread line L (positive = home favoured, nflverse sign).

    margin ~ discretised Normal(L, s) with a per-integer multiplier w(m) = observed frequency / frequency the plain Normal gives, estimated
    on `games` (dicts with result, spread_line). The multiplier captures the 3/7/6/10/14 spikes. Returns the fitted parameters."""
    res = np.array([g["result"] for g in games], dtype=float)
    ln = np.array([g["spread_line"] for g in games], dtype=float)
    s = float(np.sqrt(np.mean((res - ln) ** 2)))
    ms = np.arange(-max_margin, max_margin + 1)
    obs = np.array([(res == m).sum() for m in ms], dtype=float)
    exp = np.zeros(len(ms))
    for L in ln:
        exp += _normal_pmf(ms, L, s)
    w = np.where(exp > 0, (obs + 1.0) / (exp + 1.0), 1.0)          # +1 shrinks sparse tails towards 1
    # signed-margin spikes are not symmetric in practice (home/away), but keep each side as observed; smooth the far tail
    far = np.abs(ms) > 28
    w[far] = 1.0
    return {"s": s, "ms": ms, "w": w, "n_games": len(games)}


def _normal_pmf(ms, L, s):
    from math import erf, sqrt
    cdf = lambda x: 0.5 * (1.0 + np.vectorize(erf)((x - L) / (s * sqrt(2.0))))
    return cdf(ms + 0.5) - cdf(ms - 0.5)


def margin_pmf(model: dict | None, L: float, *, key_adjusted: bool = True) -> np.ndarray:
    ms = model["ms"]
    p = _normal_pmf(ms, L, model["s"])
    if key_adjusted:
        p = p * model["w"]
    return p / p.sum()


def p_margin_ge(model: dict, L: float, k: float, *, side: str = "home", key_adjusted: bool = True) -> float:
    """P(team margin >= k) for the home team (side 'home', margin = home-away) or the away team."""
    p = margin_pmf(model, L, key_adjusted=key_adjusted)
    ms = model["ms"]
    if side == "home":
        return float(p[ms >= k].sum())
    return float(p[ms <= -k].sum())


def model_logloss(model: dict, games: list, *, key_adjusted: bool) -> dict:
    ll = []
    for g in games:
        p = margin_pmf(model, g["spread_line"], key_adjusted=key_adjusted)
        i = int(g["result"]) + model["ms"].max()
        if 0 <= i < len(p):
            ll.append(-math.log(max(p[i], 1e-9)))
    return {"n": len(ll), "mean_logloss": round(float(np.mean(ll)), 5)}


def holdout_margin_model(hist: list, train_max_season: int = 2022) -> dict:
    """Fit on seasons <= train_max_season, score on later seasons. Distribution fit only: predictive accuracy, not profit."""
    tr = [g for g in hist if g["season"] <= train_max_season]
    te = [g for g in hist if g["season"] > train_max_season]
    model = fit_margin_model(tr)
    a, b = model_logloss(model, te, key_adjusted=False), model_logloss(model, te, key_adjusted=True)
    # game-level paired difference, bootstrap by game
    d = []
    for g in te:
        pa = margin_pmf(model, g["spread_line"], key_adjusted=False)
        pb = margin_pmf(model, g["spread_line"], key_adjusted=True)
        i = int(g["result"]) + model["ms"].max()
        if 0 <= i < len(pa):
            d.append(math.log(max(pb[i], 1e-9)) - math.log(max(pa[i], 1e-9)))
    d = np.array(d)
    rng = np.random.default_rng(SEED)
    bs = np.sort(d[rng.integers(0, len(d), size=(4000, len(d)))].mean(axis=1)) if len(d) else np.array([0.0])
    return {"train_seasons": f"<= {train_max_season}", "train_games": len(tr), "test_games": len(te), "plain_normal": a, "key_adjusted": b,
            "gain_loglik_per_game": round(float(d.mean()), 5) if len(d) else None,
            "gain_ci95": [round(float(bs[int(0.025 * len(bs))]), 5), round(float(bs[int(0.975 * len(bs))]), 5)],
            "residual_sd": round(model["s"], 3)}, model


# ----------------------------------------------------------------------------------------------------------------- positions

def position_rows(facts: list, eps_by_id: dict, games: dict, *, unit: float = 75.0) -> list:
    """Flatten `wager_diagnostics.episode_facts` into the rows every cut here needs. All fields are copied from the ledger/lifecycle;
    nothing is estimated. `outcome` is 1 when a HELD-to-settlement position paid, 0 when it lost, None for cashouts/unsettled."""
    rows = []
    for f in facts:
        ep = eps_by_id.get(f["episode"]) or {}
        txs = ep.get("transactions") or []
        first = txs[0] if txs else {}
        pt = parse_ticker(f["ticker"])
        side = "YES" if f["direction"] == "LONG_YES" else "NO" if f["direction"] == "LONG_NO" else None
        gk = canon_game_key(pt["game_code"])
        outcome = None
        if f["held"] and f["gross"] is not None:
            outcome = 1 if f["gross"] > 0 else 0
        rows.append({
            "episode": f["episode"], "week": f["week"], "game_key": None if "KXMVE" in str(f["series"]) else (gk or f["game_key"]),
            "ticker": f["ticker"], "series": pt["series"], "family": f["family"], "side": side, "team": pt["team"], "line": pt["line"],
            "player": pt["player"], "price": f["avg_price"], "qty": f["qty"], "cost": f["cost"], "fees": f["fees"], "pnl": f["pnl"],
            "units": f["cost"] / unit if unit else None, "avg_price": f["avg_price"], "phase": f["phase"], "held": f["held"],
            "cashed_out": f["cashed_out"], "settled": f["settled"], "outcome": outcome, "gross": f["gross"],
            "clv": f["clv_per_contract"] if f["clv_source"] == "CANONICAL_CLOSE" else None,
            "t": first.get("executed_at") or "", "minutes_before_kickoff": f["entry_minutes_before_kickoff"],
            "game_code": pt["game_code"]})
    return rows


def settled(rows: list) -> list:
    return [r for r in rows if r["settled"] and r["pnl"] is not None]


def roi_block(rows: list, **kw) -> dict:
    s = settled(rows)
    b = boot_ratio(s, "pnl", "cost", **kw)
    gross = [dict(r, gpnl=(r["pnl"] + r["fees"])) for r in s]            # pnl + fees = result before fees (fees counted once)
    g = boot_ratio(gross, "gpnl", "cost", **kw)
    return {"positions": len(s), "games": b["clusters"], "roi": b["estimate"], "roi_lo95": b["lo95"], "roi_hi95": b["hi95"],
            "roi_before_fees": g["estimate"], "fees_per_outlay": round(sum(r["fees"] for r in s) / sum(r["cost"] for r in s), 4) if s else None,
            "win_rate": round(sum(1 for r in s if r["pnl"] > 0) / len(s), 4) if s else None,
            "mean_entry_price": round(float(np.mean([r["price"] for r in s if r["price"] is not None])), 4) if s else None}


def fair_block(rows: list) -> dict:
    held = [r for r in settled(rows) if r["held"] and r["outcome"] is not None]
    return fair_null(held)


def cut(rows: list, key, *, m_family: int | None = None) -> dict:
    groups: dict = defaultdict(list)
    for r in settled(rows):
        groups[key(r)].append(r)
    m = m_family or len(groups)
    out = {}
    for k, v in sorted(groups.items(), key=lambda kv: str(kv[0])):
        blk = roi_block(v)
        fb = fair_block(v)
        blk["fair_null"] = {x: fb.get(x) for x in ("n", "z_cluster", "p_cluster", "excess_over_fair_per_outlay", "wins", "expected_wins_at_prices",
                                                   "p_wins_at_or_below_observed_if_prices_fair", "p_wins_at_or_above_observed_if_prices_fair")}
        blk["label"] = label(fb.get("p_cluster"), m) if fb.get("n", 0) >= 20 else "INSUFFICIENT (fewer than 20 held positions)"
        out[str(k)] = blk
    return out


# ----------------------------------------------------------------------------------------------------------------- CLV (true closes only)

def clv_block(rows: list, *, n_boot: int = 4000) -> dict:
    pre = [r for r in rows if r["phase"] == "PRE_GAME"]
    obs = [r for r in pre if r["clv"] is not None]
    out = {"pregame_positions": len(pre), "with_true_close": len(obs), "coverage": round(len(obs) / len(pre), 4) if pre else None,
           "basis": "price-only: close mid of the held side minus the price paid; canonical published closes only (no capture proxy)"}
    if len(obs) >= 3:
        b = boot_mean(obs, "clv", n_boot=n_boot)
        out.update({"mean_per_contract": b["estimate"], "lo95": b["lo95"], "hi95": b["hi95"], "games": b["clusters"],
                    "share_positive": round(sum(r["clv"] > 0 for r in obs) / len(obs), 4)})
    for lab, fam in (("game_markets", lambda r: r["family"] in ("spread", "total", "team total", "moneyline", "first-half / quarter market")),
                     ("player_props_other", lambda r: r["family"] not in ("spread", "total", "team total", "moneyline",
                                                                          "first-half / quarter market", "parlay (multi-leg combo)"))):
        o = [r for r in obs if fam(r)]
        if len(o) >= 3:
            b = boot_mean(o, "clv", n_boot=n_boot)
            out[f"by_group_{lab}"] = {"n": len(o), "mean_per_contract": b["estimate"], "lo95": b["lo95"], "hi95": b["hi95"]}
    by_wk: dict = defaultdict(lambda: [0, 0])
    for r in pre:
        by_wk[r["week"]][0] += 1
        by_wk[r["week"]][1] += r["clv"] is not None
    out["coverage_by_week"] = {f"week {k}": {"pregame": v[0], "with_true_close": v[1]} for k, v in sorted(by_wk.items())}
    return out


# ----------------------------------------------------------------------------------------------------------------- selection-rule replay

def rule_replay(rows: list, rules: dict, *, split_week: int = 4, n_boot: int = 4000) -> dict:
    """Replay each rule on settled positions: TRAIN = weeks <= split_week, TEST = later weeks (chronological hold-out).

    Statistic: net dollars recovered by the rule as a share of the baseline outlay of the same slice (points of ROI), with a 95%
    game-clustered bootstrap. Parlays and fractional truncation are handled by the rule itself (linear scaling, see
    wager_selection_rules)."""
    s = settled(rows)
    out = {}
    m = len(rules)
    for name, rule in rules.items():
        after = {x["episode"]: x for x in rule([dict(r) for r in s])}
        per = []
        for r in s:
            a = after[r["episode"]]
            frac = (r["cost"] - a["cost"]) / r["cost"] if r["cost"] else 0.0
            # What the rule is worth BEFORE the result is known: if the price paid is the true probability, a position's expected net is
            # -fees, so removing a fraction saves frac * fees. Where a model edge is recorded on the position (`book_edge_key`: held-side
            # probability from the sportsbook line, key numbers included, minus price) the expected net is qty*edge - fees.
            exp_net = (r["qty"] * r["book_edge_key"] if r.get("book_edge_key") is not None else 0.0) - r["fees"]
            per.append(dict(r, delta=a["pnl"] - r["pnl"], removed=r["cost"] - a["cost"], kept_cost=a["cost"], kept_pnl=a["pnl"],
                            exp_recovery=-frac * exp_net))
        res = {}
        for lab, sel in (("train", [p for p in per if p["week"] <= split_week]), ("test", [p for p in per if p["week"] > split_week]),
                         ("all", per)):
            if not sel:
                continue
            b = boot_ratio(sel, "delta", "cost", n_boot=n_boot)
            exp_rec = sum(p["exp_recovery"] for p in sel) / sum(p["cost"] for p in sel)
            bb = boot_ratio(sel, "delta", "cost", n_boot=max(n_boot, 20000), alpha=bonferroni_alpha(m))
            kept = [p for p in sel if p["kept_cost"] > 1e-9]
            kroi = sum(p["kept_pnl"] for p in kept) / sum(p["kept_cost"] for p in kept) if kept else None
            res[lab] = {"positions": len(sel), "positions_touched": sum(1 for p in sel if p["removed"] > 1e-9),
                        "outlay_removed_share": round(sum(p["removed"] for p in sel) / sum(p["cost"] for p in sel), 4),
                        "baseline_roi": round(sum(p["pnl"] for p in sel) / sum(p["cost"] for p in sel), 4),
                        "retained_roi": round(kroi, 4) if kroi is not None else None,
                        "roi_points_recovered": b["estimate"],
                        "expected_recovery_points_before_the_result": round(exp_rec, 4), "lo95": b["lo95"], "hi95": b["hi95"], "games": b["clusters"],
                        "bonferroni_interval": [bb["lo95"], bb["hi95"]]}
        res["bonferroni_m"] = m
        out[name] = res
    return out


# ----------------------------------------------------------------------------------------------------------------- concentration

def game_axis_exposure(rows: list) -> dict:
    s = [r for r in settled(rows) if r["game_key"]]
    by: dict = defaultdict(list)
    for r in s:
        by[r["game_key"]].append(r)
    multi = {g: v for g, v in by.items() if len(v) >= 2}
    one = [r for g, v in by.items() if len(v) == 1 for r in v]
    many = [r for v in multi.values() for r in v]
    # axis: same game, same direction on the same quantity -> spread/ML on the same team, or total/team-total overs together
    def axis(r):
        if r["series"] in ("KXNFLSPREAD", "KXNFLGAME", "KXNFL1HSPREAD", "KXNFL1H"):
            return ("side", r["team"] if r["side"] == "YES" else "other")
        if r["series"] in ("KXNFLTOTAL", "KXNFLTEAMTOTAL", "KXNFL1HTOTAL", "KXNFL1HTEAMTOTAL", "KXNFL1QTOTAL"):
            return ("points", r["side"])
        return ("prop", r["player"])
    same_axis_games = 0
    for g, v in multi.items():
        c = defaultdict(int)
        for r in v:
            c[axis(r)] += 1
        if any(n >= 2 for n in c.values()):
            same_axis_games += 1
    return {"games_with_positions": len(by), "games_with_2plus_positions": len(multi), "games_with_same_axis_stacking": same_axis_games,
            "positions_in_multi_position_games": len(many), "positions_in_single_position_games": len(one),
            "roi_multi_position_games": roi_block(many) if many else None, "roi_single_position_games": roi_block(one) if one else None,
            "roi_single_vs_multi_note": "split by games, game-clustered; a lead only"}


def concentration_block(rows: list) -> dict:
    s = settled(rows)
    net = sum(r["pnl"] for r in s)
    by: dict = defaultdict(float)
    for r in s:
        by[r["game_key"] or f"solo-{r['episode']}"] += r["pnl"]
    worst = sorted(by.values())[:3]
    return {"net_pnl_negative": net < 0, "worst3_games_share_of_net_loss": round(sum(worst) / net, 4) if net < 0 else None,
            "largest_position_units": round(max(r["units"] for r in s), 2) if s else None}


# ----------------------------------------------------------------------------------------------------------------- ladder (market-wide, true closes)

def spread_rung_group(n: float) -> str:
    n = int(n)
    if n in (3, 7):
        return "key rung (3 or 7)"
    if n in (6, 10, 14):
        return "secondary key rung (6, 10, 14)"
    if n in (4, 8):
        return "just past 3 / 7 (4 or 8)"
    if n in (1, 2, 5):
        return "small rung (1, 2, 5)"
    return "other rung"


def fee_per_contract(p: float, coef: float = 0.07) -> float:
    """Approximate Kalshi taker fee per contract: coef * p * (1 - p). Order-level rounding is ignored, so this UNDERSTATES cost."""
    return coef * p * (1 - p)


def ladder_rows(close_rows: dict, games: dict, *, max_width: float = 0.10) -> list:
    """One row per (game, rung) that has a true two-sided close and a derivable outcome. Prices are the published canonical close
    (mid/bid/ask of the YES side, `no_ask` for the NO side); `kickoff-relative` age is carried so stale closes can be seen."""
    out = []
    for gid, blob in close_rows.items():
        for r in blob["rows"]:
            t = r["ticker"]
            pt = parse_ticker(t)
            gk = canon_game_key(pt["game_code"])
            g = games.get(gk)
            y = outcome_yes(pt["series"], pt, g)
            if y is None or r.get("mid") is None or r.get("yes_ask") is None or r.get("no_ask") is None or r.get("yes_bid") is None:
                continue
            width = r["yes_ask"] - r["yes_bid"]
            if width < 0 or width > max_width or not (0.02 <= r["mid"] <= 0.98):
                continue
            out.append({"game_key": gk, "week": g["week"], "series": pt["series"], "line": pt["line"], "team": pt["team"], "y": y,
                        "mid": r["mid"], "yes_ask": r["yes_ask"], "no_ask": r["no_ask"], "width": width, "ticker": t,
                        "minutes_before_kickoff": r.get("minutes_before_kickoff")})
    return out


def ladder_calibration(rows: list, key, *, min_n: int = 30) -> dict:
    """Mean (outcome - mid) by group: positive = YES underpriced at the close mid. Also the return of buying the cheaper-to-cross
    side at its ask, net of the approximate fee, per dollar staked. Game-clustered 95% intervals; Bonferroni over the groups."""
    groups: dict = defaultdict(list)
    for r in rows:
        groups[key(r)].append(r)
    m = len(groups)
    out = {}
    for k, v in sorted(groups.items(), key=lambda kv: str(kv[0])):
        if len(v) < min_n:
            out[str(k)] = {"n": len(v), "label": "INSUFFICIENT"}
            continue
        for r in v:
            r["_d"] = r["y"] - r["mid"]
            ya, na = r["yes_ask"], r["no_ask"]
            r["_yes_pnl"] = r["y"] - ya - fee_per_contract(ya)
            r["_yes_cost"] = ya + fee_per_contract(ya)
            r["_no_pnl"] = (1 - r["y"]) - na - fee_per_contract(na)
            r["_no_cost"] = na + fee_per_contract(na)
        d = boot_mean(v, "_d")
        yb = boot_ratio(v, "_yes_pnl", "_yes_cost")
        nb = boot_ratio(v, "_no_pnl", "_no_cost")
        z = None
        mc = _clusters(v, lambda r: r["game_key"], ("_d",))
        if len(mc) > 2 and (mc[:, 0] ** 2).sum() > 0:
            z = float(mc[:, 0].sum() / math.sqrt((mc[:, 0] ** 2).sum()))
        out[str(k)] = {"n": len(v), "games": d["clusters"], "mean_outcome_minus_mid": d["estimate"], "lo95": d["lo95"], "hi95": d["hi95"],
                       "z_cluster": round(z, 2) if z is not None else None, "p": p_two_sided(z),
                       "buy_yes_at_ask_roi": yb["estimate"], "buy_yes_lo95": yb["lo95"], "buy_yes_hi95": yb["hi95"],
                       "buy_no_at_ask_roi": nb["estimate"], "buy_no_lo95": nb["lo95"], "buy_no_hi95": nb["hi95"],
                       "mean_width": round(float(np.mean([r["width"] for r in v])), 4),
                       "label": label(p_two_sided(z), m)}
        for r in v:
            for c in ("_d", "_yes_pnl", "_yes_cost", "_no_pnl", "_no_cost"):
                r.pop(c, None)
    return out


def market_vs_book(rows: list, games: dict, model: dict) -> list:
    """For spread rungs only: the key-number-aware probability implied by the sportsbook closing line (nflverse `spread_line`) next to the
    Kalshi close mid. The sportsbook line is a CLOSE of a different market, not a Kalshi price and not point-in-time at the owner's fill."""
    out = []
    for r in rows:
        if r["series"] != "KXNFLSPREAD":
            continue
        g = games.get(r["game_key"])
        if not g or g.get("spread_line") is None or r["team"] not in (g["home"], g["away"]):
            continue
        side = "home" if r["team"] == g["home"] else "away"
        L = g["spread_line"]
        # model is in HOME-margin space with positive L = home favoured; the away team's margin >= k is home margin <= -k
        p_k = p_margin_ge(model, L, r["line"], side=side, key_adjusted=True)
        p_n = p_margin_ge(model, L, r["line"], side=side, key_adjusted=False)
        out.append(dict(r, p_book_key=p_k, p_book_normal=p_n))
    return out


def qb_change_flags(games: dict) -> dict:
    """{(game_key, team) -> True if the starting QB differs from that team's previous game's starter}. 2026 games in week order."""
    last: dict = {}
    out = {}
    for gk, g in sorted(games.items(), key=lambda kv: (kv[1]["week"], kv[0])):
        for team, qb in ((g["away"], g["away_qb"]), (g["home"], g["home_qb"])):
            prev = last.get(team)
            out[(gk, team)] = (prev is not None and qb is not None and prev != qb)
            if qb:
                last[team] = qb
    return out


# ----------------------------------------------------------------------------------------------------------------- shadow model join

def shadow_join(rows: list, obs_by_ticker: dict, *, max_age_hours: float = 6.0) -> list:
    """Point-in-time join of the SHADOW model's recorded probability to a position: the latest observation of that ticker whose
    `feature_cutoff` is at or before the position's first fill, no older than `max_age_hours`, with support_state SUPPORTED and a non-null
    probability. Returns the matched rows with p_side (shadow model probability that the HELD side pays) and the observation's own mid."""
    out = []
    for r in rows:
        if not r["t"] or r["side"] is None:
            continue
        try:
            t0 = datetime.fromisoformat(r["t"].replace("Z", "+00:00"))
        except ValueError:
            continue
        best = None
        for o in obs_by_ticker.get(r["ticker"], ()):
            try:
                fc = datetime.fromisoformat(o["feature_cutoff"].replace("Z", "+00:00"))
            except (KeyError, ValueError, AttributeError):
                continue
            if fc > t0 or (t0 - fc).total_seconds() > max_age_hours * 3600:
                continue
            if o.get("support_state") != "SUPPORTED" or o.get("model_event_probability") is None or o.get("mid") is None:
                continue
            if best is None or fc > best[0]:
                best = (fc, o)
        if best is None:
            continue
        o = best[1]
        p = float(o["model_event_probability"])
        out.append(dict(r, p_side=p if r["side"] == "YES" else 1 - p, mid_side=float(o["mid"]) if r["side"] == "YES" else 1 - float(o["mid"]),
                        p_yes=p, mid_yes=float(o["mid"]), model_family=o.get("family"), obs_age_min=round((t0 - best[0]).total_seconds() / 60, 1)))
    return out


def shadow_block(matched: list, eligible: int) -> dict:
    ok = [r for r in matched if r["outcome"] is not None]
    out = {"positions_eligible_game_or_prop_markets": eligible, "matched_to_shadow_observation": len(matched), "matched_and_held_to_settlement": len(ok),
           "coverage": round(len(matched) / eligible, 4) if eligible else None,
           "provenance": "SHADOW model probabilities (point-in-time, latest observation at or before the first fill). NOT the owner's probabilities: "
                         "the owner's wagers carry no recorded model number, thesis or recommendation id."}
    if len(ok) < 10:
        out["label"] = "INSUFFICIENT"
        return out
    for r in ok:
        r["_bm"] = (r["p_side"] - r["outcome"]) ** 2
        r["_bk"] = (r["mid_side"] - r["outcome"]) ** 2
        r["_dd"] = r["_bm"] - r["_bk"]                       # shadow Brier minus market Brier (negative = model better)
        r["_edge"] = r["p_side"] - r["price"]                # shadow edge over the price actually paid
    d = boot_mean(ok, "_dd")
    out["predictive_accuracy"] = {"brier_shadow_minus_market_mid": d["estimate"], "lo95": d["lo95"], "hi95": d["hi95"],
                                  "mean_brier_shadow": round(float(np.mean([r["_bm"] for r in ok])), 4),
                                  "mean_brier_market_mid": round(float(np.mean([r["_bk"] for r in ok])), 4)}
    agree = [r for r in ok if r["_edge"] > 0]
    disagree = [r for r in ok if r["_edge"] <= 0]
    out["shadow_agreement_with_owner_side"] = {"agree_positive_edge_over_price_paid": len(agree), "disagree": len(disagree)}
    for name, grp in (("agree", agree), ("disagree", disagree)):
        if len(grp) >= 5:
            fb = fair_null(grp)
            out[f"profitability_when_shadow_{name}s"] = {"roi": roi_block(grp)["roi"], "roi_lo95": roi_block(grp)["roi_lo95"],
                                                         "roi_hi95": roi_block(grp)["roi_hi95"], "n": len(grp),
                                                         "fair_null_z": fb.get("z_cluster"), "mean_shadow_edge": round(float(np.mean([r["_edge"] for r in grp])), 4)}
    edges = np.array([r["_edge"] for r in ok])
    ex = np.array([r["outcome"] - r["price"] for r in ok])
    out["edge_vs_realised_excess"] = {"corr": round(float(np.corrcoef(edges, ex)[0, 1]), 3) if edges.std() > 0 and ex.std() > 0 else None,
                                      "mean_claimed_edge": round(float(edges.mean()), 4), "mean_realised_excess": round(float(ex.mean()), 4),
                                      "note": "claimed edge is the shadow model's; realised excess is outcome minus price paid (before fees)"}
    out["label"] = "INSUFFICIENT" if len(ok) < 60 else "LEAD"
    for r in ok:
        for c in ("_bm", "_bk", "_dd", "_edge"):
            r.pop(c, None)
    return out


# ----------------------------------------------------------------------------------------------------------------- selection vs structure

LADDER_SERIES = ("KXNFLSPREAD", "KXNFLTOTAL", "KXNFLTEAMTOTAL", "KXNFLGAME")


def selection_vs_structure(rows: list, ladder: list, *, band: float = 0.05, min_control: int = 15) -> dict:
    """Split the owner's pre-fee result on full-game markets into STRUCTURE (what any taker of that series, side and price band earned at
    the published closes, excluding the owner's own game) and SELECTION (the owner's result minus that control).

    owner_i   = qty * (outcome - price paid)                    held-to-settlement positions only; before fees
    control_i = qty * mean over ladder rows r of the same series/side, held-side mid within +-band of the price paid, other games:
                (outcome_r - ask_r)                              the ask is what a taker pays at the close, so the spread is inside
    selection_i = owner_i - control_i
    The control is built from CLOSE prices while the owner paid fill-time prices (mostly the last hour), so structure is approximate; its
    sampling error is not propagated (the interval is over the owner's games only)."""
    by_key: dict = defaultdict(list)
    for r in ladder:
        for side in ("YES", "NO"):
            mid_s = r["mid"] if side == "YES" else 1 - r["mid"]
            ask_s = r["yes_ask"] if side == "YES" else r["no_ask"]
            y_s = r["y"] if side == "YES" else 1 - r["y"]
            by_key[(r["series"], side)].append((mid_s, y_s - ask_s, r["game_key"]))
    used = []
    for p in settled(rows):
        if p["series"] not in LADDER_SERIES or not p["held"] or p["outcome"] is None or p["price"] is None or p["side"] is None:
            continue
        ctrl = [d for (m, d, g) in by_key.get((p["series"], p["side"]), ()) if abs(m - p["price"]) <= band and g != p["game_key"]]
        if len(ctrl) < min_control:
            continue
        c = float(np.mean(ctrl))
        used.append(dict(p, owner_ex=p["qty"] * (p["outcome"] - p["price"]), ctrl_ex=p["qty"] * c, n_ctrl=len(ctrl),
                         sel_ex=p["qty"] * (p["outcome"] - p["price"] - c)))
    if not used:
        return {"n": 0}
    out = {"n": len(used), "games": len({u["game_key"] for u in used}), "median_control_rows": int(np.median([u["n_ctrl"] for u in used]))}
    for name, f in (("owner_excess_before_fees", "owner_ex"), ("selection_excess", "sel_ex")):
        b = boot_ratio(used, f, "cost")
        out[name + "_per_outlay"] = {"estimate": b["estimate"], "lo95": b["lo95"], "hi95": b["hi95"]}
    # The control is a market-wide average whose own sampling error is NOT propagated here; its interval is in the ladder section.
    out["structure_control_excess_per_outlay"] = {"estimate": boot_ratio(used, "ctrl_ex", "cost")["estimate"], "interval": "see ladder section"}
    out["reading"] = ("owner = structure + selection. Structure is what a buyer of the same series/side/price band earned at the closes "
                      "(includes crossing the book, excludes fees). Selection is what is left to the owner's choice of game and rung.")
    return out


def owner_book_edge(rows: list, games: dict, model: dict) -> dict:
    """The owner's spread buys priced against the sportsbook closing line, with and without the key-number structure.

    edge_key  = key-number-aware probability that the held side pays - price paid
    edge_norm = plain-Normal probability - price paid
    A normal-approximation fair value sees a phantom edge wherever the rung sits just past a key number; the key-aware one does not."""
    sp = [r for r in settled(rows) if r["series"] == "KXNFLSPREAD" and r["side"] and r["price"] is not None]
    mv = market_vs_book(sp, games, model)
    for r in mv:
        pk, pn = r["p_book_key"], r["p_book_normal"]
        r["edge_key"] = (pk if r["side"] == "YES" else 1 - pk) - r["price"]
        r["edge_norm"] = (pn if r["side"] == "YES" else 1 - pn) - r["price"]
    if not mv:
        return {"n": 0}
    return {"n": len(mv), "mean_edge_key_aware": boot_mean(mv, "edge_key"), "mean_edge_plain_normal": boot_mean(mv, "edge_norm"),
            "basis": "sportsbook consensus CLOSING line (nflverse spread_line), not a Kalshi price and not point-in-time at the fill"}


def rung_concentration(rows: list, ladder: list, rungs=(4, 8), band=(0.4, 0.6)) -> dict:
    """Share of the owner's spread positions on rungs just past a key number vs the share of all near-50c ladder rungs there."""
    sp = [r for r in settled(rows) if r["series"] == "KXNFLSPREAD" and r["line"] is not None]
    base = [r for r in ladder if r["series"] == "KXNFLSPREAD" and band[0] <= r["mid"] <= band[1]]
    if not sp or not base:
        return {"n_owner": len(sp), "n_ladder": len(base)}
    o = sum(1 for r in sp if int(r["line"]) in rungs) / len(sp)
    b = sum(1 for r in base if int(r["line"]) in rungs) / len(base)
    # exact binomial tail of >= k owner positions at base rate b
    k, n = sum(1 for r in sp if int(r["line"]) in rungs), len(sp)
    tail = sum(math.comb(n, i) * b ** i * (1 - b) ** (n - i) for i in range(k, n + 1))
    return {"n_owner": n, "owner_share_on_rungs": round(o, 4), "n_ladder_rungs_near_50c": len(base), "ladder_share_on_rungs": round(b, 4),
            "binomial_tail_p_one_sided": round(tail, 5), "rungs": list(rungs)}


def annotate_book_edge(rows: list, games: dict, model: dict) -> int:
    """Set `book_edge_key` / `book_edge_norm` (held-side probability from the sportsbook closing line minus the price paid) in place on every
    settled full-game spread position. Returns how many were annotated."""
    n = 0
    for r in rows:
        if r["series"] != "KXNFLSPREAD" or r["side"] is None or r["price"] is None or r["line"] is None:
            continue
        g = games.get(r["game_key"])
        if not g or g.get("spread_line") is None or r["team"] not in (g["home"], g["away"]):
            continue
        side = "home" if r["team"] == g["home"] else "away"
        pk = p_margin_ge(model, g["spread_line"], r["line"], side=side, key_adjusted=True)
        pn = p_margin_ge(model, g["spread_line"], r["line"], side=side, key_adjusted=False)
        r["book_edge_key"] = (pk if r["side"] == "YES" else 1 - pk) - r["price"]
        r["book_edge_norm"] = (pn if r["side"] == "YES" else 1 - pn) - r["price"]
        n += 1
    return n


def breakeven_block(rows: list, key) -> dict:
    """Fee-inclusive breakeven hit rate: a held contract bought at price p with fee f per contract needs to win with probability p + f
    just to return its stake. Compared with the realised win rate. Fees counted once (the entry fee inside `cost`)."""
    groups: dict = defaultdict(list)
    for r in settled(rows):
        if r["held"] and r["qty"] and r["price"] is not None:
            groups[key(r)].append(r)
    out = {}
    for k, v in sorted(groups.items(), key=lambda kv: str(kv[0])):
        qty = sum(r["qty"] for r in v)
        fee_pc = sum(r["fees"] for r in v) / qty
        px = sum(r["price"] * r["qty"] for r in v) / qty
        out[str(k)] = {"positions": len(v), "contract_weighted_price": round(px, 4), "fee_per_contract": round(fee_pc, 4),
                       "breakeven_hit_rate": round(px + fee_pc, 4), "fee_share_of_price": round(fee_pc / px, 4),
                       "realised_contract_weighted_hit_rate": round(sum(r["outcome"] * r["qty"] for r in v) / qty, 4)}
    return out
