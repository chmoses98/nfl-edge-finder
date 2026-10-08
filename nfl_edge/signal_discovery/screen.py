"""Stage A exploration screen for NFL games (block A 2015-2019 only; the runner enforces it). RESEARCH ONLY.

Univariate associations of home-perspective features with the home ATS residual and home margin, game-level
features with the total residual and total points, and within-CONTROL-tier conditionals; BH q over the whole
screen. Nothing here is evidence: its only product is a short list of candidates frozen as set 2 and judged on
block B.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import numpy as np

from nfl_edge.signal_discovery import stats

METRICS = ("epa_play", "success_rate", "dropback_epa", "designed_rush_epa", "explosive_rate", "sack_rate", "td_per_drive",
           "early_epa", "explosive_pass_rate", "explosive_rush_rate", "points", "pressure_rate", "plays", "sec_per_play",
           "neutral_pass_rate", "neutral_proe")


def side_features(r: dict) -> dict[str, float | None]:
    out: dict[str, float | None] = {}
    for m in METRICS:
        out[f"net.{m}"] = r.get(f"net.{m}")
        ho, hd, ao, ad = (r.get(f"q_{s}_{u}.{m}") for s, u in (("home", "off"), ("home", "def"), ("away", "off"), ("away", "def")))
        if None not in (ho, ao):
            out[f"offdiff.{m}"] = ho - ao
        if None not in (hd, ad):
            out[f"defdiff.{m}"] = hd - ad
    for k in ("gap.margin", "baseline.home_margin", "raw.epa_net", "ctx.rest_diff"):
        out[k] = r.get(k)
    return out


def game_features(r: dict) -> dict[str, float | None]:
    out: dict[str, float | None] = {k: r.get(k) for k in ("env.plays", "env.sec_per_play", "env.neutral_pass_rate", "gap.total",
                                                           "baseline.total", "def_quality_sum.epa", "off_quality_sum.epa")}
    for m in METRICS:
        q = [r.get(f"q_{s}_{u}.{m}") for s in ("home", "away") for u in ("off", "def")]
        if None not in q:
            out[f"offsum.{m}"] = q[0] + q[2]
            out[f"defsum.{m}"] = q[1] + q[3]
    n = r.get("net.epa_play")
    out["abs_net.epa_play"] = abs(n) if n is not None else None
    return out


def _assoc(xs, ys, seasons) -> dict[str, Any] | None:
    x, y = np.asarray(xs, float), np.asarray(ys, float)
    if len(x) < 100 or float(x.std()) == 0:
        return None
    xz = (x - x.mean()) / x.std(ddof=1)
    res = stats.ols(y, np.column_stack([np.ones(len(x)), xz]))
    by = defaultdict(list)
    for s, a, b in zip(seasons, xz, y, strict=False):
        by[s].append((a, b))
    signs = []
    for pairs in by.values():
        if len(pairs) >= 50:
            a = np.asarray([p[0] for p in pairs])
            b = np.asarray([p[1] for p in pairs])
            if a.std() > 0:
                signs.append(np.sign(np.cov(a, b)[0, 1]))
    beta = res["beta"][1]
    return {"n": len(x), "beta_per_sd": beta, "z": res["z"][1], "p": res["p"][1],
            "seasons_same_sign": int(sum(1 for s in signs if s == np.sign(beta))), "seasons": len(signs)}


def screen(rows: list[dict]) -> dict[str, Any]:
    entries = []
    for feats_fn, targets, scope in ((side_features, {"home_ats_resid": "MARKET", "o.home_margin": "FOOTBALL"}, "SIDE"),
                                     (game_features, {"total_resid": "MARKET", "o.total_points": "FOOTBALL"}, "TOTAL")):
        fs = [feats_fn(r) for r in rows]
        for name in sorted({k for f in fs for k in f}):
            for tgt, layer in targets.items():
                xs, ys, ss = [], [], []
                for r, f in zip(rows, fs, strict=False):
                    x, y = f.get(name), r.get(tgt)
                    if x is not None and y is not None and x == x:
                        xs.append(x)
                        ys.append(y)
                        ss.append(r["season"])
                a = _assoc(xs, ys, ss)
                if a:
                    entries.append({"scope": scope, "feature": name, "target": tgt, "layer": layer, "kind": "UNIVARIATE", **a})
    for tier in ("MODERATE", "STRONG"):
        sub = [r for r in rows if r.get("control_strength") == tier and r.get("home_ats_resid") is not None]
        fs = [side_features(r) for r in sub]
        for name in sorted({k for f in fs for k in f}):
            xs, ys, ss = [], [], []
            for r, f in zip(sub, fs, strict=False):
                sg = 1.0 if r["control_side"] == "home" else -1.0
                x = f.get(name)
                if x is None or x != x:
                    continue
                xs.append(sg * x)
                ys.append(sg * r["home_ats_resid"])
                ss.append(r["season"])
            a = _assoc(xs, ys, ss)
            if a:
                entries.append({"scope": f"WITHIN_{tier}", "feature": name, "target": "control_side_ats_resid", "layer": "MARKET",
                                "kind": "CONDITIONAL", **a})
    q = stats.benjamini_hochberg([e["p"] for e in entries])
    for e, qq in zip(entries, q, strict=False):
        e["q_bh_whole_screen"] = qq
    market = sorted([e for e in entries if e["layer"] == "MARKET"], key=lambda e: e["p"])
    football = sorted([e for e in entries if e["layer"] == "FOOTBALL"], key=lambda e: e["p"])
    return {"associations_screened": len(entries), "market_associations": len(market),
            "market_q_lt_0_10": sum(1 for e in market if e["q_bh_whole_screen"] < 0.10),
            "market_q_lt_0_05": sum(1 for e in market if e["q_bh_whole_screen"] < 0.05),
            "top": {"market": market[:40], "football": football[:25]}, "all": entries}
