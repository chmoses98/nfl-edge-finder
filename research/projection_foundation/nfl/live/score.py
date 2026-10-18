"""Prospective scorecards (stage `score`): pf_core scorecard + NFL monitoring lines.

On top of `prospective.scorecard` (per-family MAE/bias/CRPS/80% coverage for every model, paired challenger-vs-incumbent,
drift alerts against the frozen holdout) this adds, for the SAME settled forecasts:

  segment_drift      bias of the frozen model in the segments the study found over-projected after the freeze - a
                     player's first 4 games with a new team (+14-37% on development), backup tiers RB2+/TE2+/WR3+ (+7-18%)
                     and rookies (+14-37% / +7-18% bands apply to the first two; rookies are monitored for the same
                     role-uncertainty reason). Per family: n, games, mean actual, bias (model - actual), relative bias,
                     game-clustered 95% CI. The pre-registered corrections are NOT adopted; this only monitors.
  incumbent_ladder   rung-Brier comparison of P(X >= k) at the incumbent's listed thresholds: challenger pmf vs shadow-0.4.0
                     vs shadow-0.5.0 (identical player-stats and outcomes; no prices involved).
  participation      DNP/void rate by the pre-game participation call and its certainty (validates the availability feed).
  gate               settled n and MAE by gate status.

Everything is research-only monitoring of projection accuracy; no market or disagreement quantity is touched.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

from pf_core import prospective as pr
from pf_core.metrics import cluster_bootstrap_diff

from nfl.live import SPORT

STUDY_EXPECTED = {"new_team_first4": "+14% to +37% (development, pre-registered, not adopted)",
                  "backup": "+7% to +18% (development, pre-registered, not adopted)",
                  "rookie": "monitored (no study band)"}
MIN_N = 30
WATCH_REL = 0.10


def _frames(archive: str, since_utc: str | None):
    s = pr.load_settlements(archive, SPORT)
    if s.empty:
        return s, pd.DataFrame()
    s = s[~s["void"].astype(bool)].copy()
    if since_utc:
        s = s[pd.to_datetime(s["game_start_utc"], utc=True) >= pd.to_datetime(since_utc, utc=True)]
    f = pr.load_forecasts(archive, SPORT)
    keep = [c for c in ("forecast_id", "segments", "position", "participation_certainty", "ladder", "ladder_050") if c in f.columns]
    return s, f[keep] if len(f) else pd.DataFrame()


def segment_drift(s: pd.DataFrame, f: pd.DataFrame) -> dict:
    out: dict = {"definition": {"new_team_first4": "first four games with the current team (had an earlier different team)",
                                "backup": "RB2+/TE2+/WR3+ by the team's EWMA target-per-attempt rank",
                                "rookie": "is_rookie (first NFL season)"},
                 "study_expected_bias": STUDY_EXPECTED, "families": {}, "pooled": {}}
    if s.empty or f.empty or "segments" not in f.columns:
        return out
    s = s.drop(columns=[c for c in ("segments",) if c in s.columns])
    m = s[s.model_role == "challenger"].merge(f[["forecast_id", "segments"]], on="forecast_id", how="left")
    m = m[m.segments.map(lambda x: isinstance(x, dict))]
    if m.empty:
        return out
    for k in ("new_team_first4", "backup", "rookie"):
        m[k] = m.segments.map(lambda d, k=k: bool(d.get(k)))
    m["none_of_the_three"] = ~(m.new_team_first4 | m.backup | m.rookie)
    rel_all: dict[str, list] = {}
    for fam, g in m.groupby("family"):
        for seg in ("new_team_first4", "backup", "rookie", "none_of_the_three"):
            x = g[g[seg]]
            if x.empty:
                continue
            mu, y = x["mean"].to_numpy(float), x["actual"].to_numpy(float)
            bias = float(np.mean(mu - y))
            row = {"n": int(len(x)), "games": int(x.game_id.nunique()), "mean_actual": float(y.mean()), "bias": bias,
                   "relative_bias": (bias / float(y.mean())) if y.mean() > 0 else None}
            if len(x) > 1:
                ci = cluster_bootstrap_diff(mu, y, x.game_id.to_numpy(), n_boot=500)["ci95"]
                row["bias_ci95"] = ci
            row["status"] = ("INSUFFICIENT" if len(x) < MIN_N else
                             "WATCH" if (row["relative_bias"] or 0) > WATCH_REL and seg != "none_of_the_three" else "OK")
            out["families"].setdefault(fam, {})[seg] = row
            if len(x) >= 1 and y.mean() > 0:
                rel_all.setdefault(seg, []).append((len(x), float(np.sum(mu - y)), float(np.sum(y))))
    for seg, v in rel_all.items():
        # pooled over families as a share of realised volume within family, averaged with family-n weights
        n = sum(a for a, _, _ in v)
        out["pooled"][seg] = {"n": int(n), "relative_bias": float(sum(a * (b / c) for a, b, c in v) / n) if n else None}
    return out


def incumbent_ladder(s: pd.DataFrame, f: pd.DataFrame) -> dict:
    """Brier of P(X>=k) at the incumbent's rungs for challenger / shadow-0.4.0 / shadow-0.5.0 on identical player-stats."""
    out: dict = {"families": {}, "note": "rungs are the incumbent's listed thresholds; Brier of event probabilities vs outcomes; "
                                          "no prices are used."}
    if s.empty or f.empty or "ladder" not in f.columns:
        return out
    if "ladder_050" not in f.columns:
        f = f.assign(ladder_050=None)
    inc = s[s.model_role == "incumbent"].merge(f[["forecast_id", "ladder", "ladder_050"]], on="forecast_id", how="left")
    ch = s[s.model_role == "challenger"]
    inc = inc[inc.ladder.map(lambda x: isinstance(x, dict))]
    if inc.empty or ch.empty:
        return out
    j = inc.merge(ch[["game_id", "entity_id", "family", "mean", "lo", "probs"]], on=["game_id", "entity_id", "family"], suffixes=("", "_ch"))
    rows = []
    for _, r in j.iterrows():
        probs = np.asarray(r.probs_ch, float)
        lo = int(r.lo_ch) if pd.notna(r.lo_ch) else 0
        for k, p_inc in r.ladder.items():
            kk = int(k)
            idx = kk - lo
            p_ch = float(probs[idx:].sum()) if len(probs) and 0 <= idx < len(probs) else (1.0 if len(probs) and idx < 0 else 0.0)
            y = float(r.actual >= kk)
            p050 = (r.ladder_050 or {}).get(k) if isinstance(r.ladder_050, dict) else None
            rows.append({"family": r.family, "game_id": r.game_id, "k": kk, "y": y, "ch": p_ch, "inc": float(p_inc),
                         "inc050": None if p050 is None else float(p050)})
    if not rows:
        return out
    d = pd.DataFrame(rows)
    for fam, g in d.groupby("family"):
        e = {"n_rungs": int(len(g)), "n_games": int(g.game_id.nunique()),
             "brier_challenger": float(((g.ch - g.y) ** 2).mean()), "brier_shadow_0_4_0": float(((g.inc - g.y) ** 2).mean())}
        e["challenger_minus_0_4_0"] = cluster_bootstrap_diff((g.ch - g.y) ** 2, (g.inc - g.y) ** 2, g.game_id.to_numpy(), n_boot=500)
        g5 = g[g.inc050.notna()]
        if len(g5) >= 1:
            e["n_rungs_050"] = int(len(g5))
            e["brier_shadow_0_5_0"] = float(((g5.inc050 - g5.y) ** 2).mean())
            e["brier_challenger_same_rungs"] = float(((g5.ch - g5.y) ** 2).mean())
        out["families"][fam] = e
    return out


def participation_check(s_all: pd.DataFrame) -> dict:
    """Void (DNP) rate by the participation status published pre-game (challenger forecasts, players only)."""
    out: dict = {}
    if s_all.empty:
        return out
    c = s_all[(s_all.model_role == "challenger") & s_all.participation.notna() & (s_all.participation != "n/a")]
    c = c[c.entity_id.astype(str).str.startswith("00-")]
    for st, g in c.groupby("participation"):
        out[st] = {"n": int(len(g)), "dnp_rate": float(g["void"].astype(bool).mean())}
    return out


def gate_check(s: pd.DataFrame) -> dict:
    out = {}
    c = s[(s.model_role == "challenger") & s.gate_status.notna()] if not s.empty else s
    if c is None or c.empty:
        return out
    for st, g in c.groupby("gate_status"):
        out[st] = {"n": int(len(g)), "mae": float(np.mean(np.abs(g["mean"].astype(float) - g["actual"].astype(float))))}
    return out


def build_cards(archive: str, now_utc: str, summary: dict | None, capture_stats: dict | None = None) -> dict[str, dict]:
    ref = pr.reference_from_summary(summary or {})
    cards = {}
    for tag, days in (("daily", 7), ("weekly", 28), ("season", None)):
        card = pr.scorecard(SPORT, archive, ref, now_utc=now_utc, window_days=days, capture_stats=capture_stats)
        since = card["window"]["since_utc"]
        s, f = _frames(archive, since)
        s_all = pr.load_settlements(archive, SPORT)
        if since and not s_all.empty:
            s_all = s_all[pd.to_datetime(s_all["game_start_utc"], utc=True) >= pd.to_datetime(since, utc=True)]
        card["nfl"] = {"segment_drift": segment_drift(s, f), "incumbent_ladder": incumbent_ladder(s, f),
                       "participation_vs_dnp": participation_check(s_all), "gate_status": gate_check(s)}
        cards[tag] = card
    return cards


def render_nfl_markdown(card: dict) -> str:
    n = card.get("nfl") or {}
    L = ["", "### NFL monitoring lines (research only; pre-registered corrections are NOT adopted)", ""]
    sd = n.get("segment_drift", {})
    if sd.get("families"):
        L += ["| Stat | Segment | n (games) | Mean actual | Bias (model - actual) | Relative | 95% CI | Status | Study (dev) |",
              "|---|---|---|---|---|---|---|---|---|"]
        for fam, segs in sorted(sd["families"].items()):
            for seg, r in segs.items():
                ci = r.get("bias_ci95")
                rel = r.get("relative_bias")
                L.append(f"| {fam} | {seg} | {r['n']} ({r['games']}) | {r['mean_actual']:.2f} | {r['bias']:+.3f} | "
                         f"{'—' if rel is None else f'{rel:+.1%}'} | {'—' if not ci else f'[{ci[0]:+.2f}, {ci[1]:+.2f}]'} | {r['status']} | "
                         f"{sd['study_expected_bias'].get(seg, '')} |")
        if sd.get("pooled"):
            L += ["", "Pooled relative bias (family-n weighted): " +
                  "; ".join(f"{k} {v['relative_bias']:+.1%} (n={v['n']})" for k, v in sd["pooled"].items() if v["relative_bias"] is not None)]
    else:
        L.append("_No settled forecasts with segment tags yet._")
    il = n.get("incumbent_ladder", {}).get("families", {})
    if il:
        L += ["", "**Rung Brier at the incumbent's listed thresholds (lower is better)**", "",
              "| Stat | rungs (games) | challenger | shadow-0.4.0 | diff (95% CI) | shadow-0.5.0 | challenger (same rungs) |", "|---|---|---|---|---|---|---|"]
        for fam, e in sorted(il.items()):
            d = e["challenger_minus_0_4_0"]
            L.append(f"| {fam} | {e['n_rungs']} ({e['n_games']}) | {e['brier_challenger']:.4f} | {e['brier_shadow_0_4_0']:.4f} | "
                     f"{d['mean_diff']:+.4f} [{d['ci95'][0]:+.4f}, {d['ci95'][1]:+.4f}] | "
                     f"{'—' if 'brier_shadow_0_5_0' not in e else format(e['brier_shadow_0_5_0'], '.4f')} | "
                     f"{'—' if 'brier_challenger_same_rungs' not in e else format(e['brier_challenger_same_rungs'], '.4f')} |")
    pv = n.get("participation_vs_dnp", {})
    if pv:
        L += ["", "**DNP (void) rate by pre-game participation call**: " + "; ".join(f"{k} {v['dnp_rate']:.1%} (n={v['n']})" for k, v in sorted(pv.items()))]
    gs = n.get("gate_status", {})
    if gs:
        L += ["", "**Settled by gate status**: " + "; ".join(f"{k} n={v['n']} MAE={v['mae']:.3f}" for k, v in sorted(gs.items()))]
    cs = card.get("capture", {})
    if cs.get("availability_coverage") is not None:
        L += ["", f"**Availability capture** (last run): mean coverage {cs.get('availability_coverage')}, "
                  f"participation calls {cs.get('participation_status')}"]
    return "\n".join(L) + "\n"


def write_cards(cards: dict[str, dict], archive: str) -> dict:
    paths = {}
    for tag, card in cards.items():
        p = pr.write_scorecard(card, archive, tag=tag)
        md = os.path.join(os.path.dirname(p), f"{tag}.md")
        with open(md, "a") as f:
            f.write(render_nfl_markdown(card))
        paths[tag] = p
    return paths
