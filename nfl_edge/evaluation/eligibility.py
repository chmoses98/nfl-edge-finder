"""PRODUCTION ELIGIBILITY: which model families may inform real handicapping, decided by evidence, not preference.

States (machine-readable, in increasing authority):

    DISABLED        a known defect makes the arm's output wrong by construction (registry below); never used
    RESEARCH_ONLY   displayed with a label, never an input: too little evidence, or evidence that it is worse
                    than the market
    WATCH           enough independent games to measure, and not measurably worse than the market; supporting
                    evidence only
    LIMITED         several weeks of synchronized prospective evidence, not worse than the market within
                    tolerance, calibrated, non-negative CLV; may inform a handicap alongside the market
    TRUSTED         a long prospective record that is BETTER THAN the market with statistical support and positive CLV;
                    may be relied on as primary evidence (still never an automatic bet)

THE UNIT OF EVIDENCE IS THE GAME. A week of player props is hundreds of thousands of rows -- every rung of every
ladder at every snapshot -- but only sixteen independent outcomes' worth of football. Every statistic here is
computed per game first (the mean Brier difference over that game's rows) and then across games, with the
standard error taken across games. Row counts are reported and never qualify anything.

Only PROSPECTIVE_FROZEN rows count, and only SYNCHRONIZED ones (the model read nothing newer than the market it
is scored against). The thresholds are written down here and in docs/PRODUCTION_ELIGIBILITY.md BEFORE any arm is
evaluated against them, and are not tuned to approve anything.
"""
from __future__ import annotations

import math
from collections import defaultdict

ELIGIBILITY_VERSION = "eligibility-1.0.0"
DISABLED, RESEARCH_ONLY, WATCH, LIMITED, TRUSTED = "DISABLED", "RESEARCH_ONLY", "WATCH", "LIMITED", "TRUSTED"
ORDER = (DISABLED, RESEARCH_ONLY, WATCH, LIMITED, TRUSTED)

# ---------------------------------------------------------------------------------------------- written policy
POLICY = {
    "min_games_watch": 16,          # one full slate of independent outcomes
    "min_games_limited": 48,        # ~three slates
    "min_weeks_limited": 3,
    "min_games_trusted": 128,       # ~eight slates
    "min_weeks_trusted": 8,
    "worse_z": 2.0,                 # game-level (model - market) Brier / SE above this = measurably worse
    "limited_max_upper": 0.002,     # LIMITED: the 95% upper bound of (model - market) Brier must be <= this
    "trusted_max_upper": 0.0,       # TRUSTED: the 95% upper bound must be < 0 (better than the market)
    "max_ece_limited": 0.03,
    "min_sync_share": 0.90,         # share of rows SYNCHRONIZED
    "min_close_quality_share": 0.90,  # share of rows whose close is EXCELLENT / GOOD
}

# Known defects: an arm listed here is DISABLED whatever its numbers say, with the reason and the evidence.
KNOWN_DEFECTS = {
    "DATA_PLAYER_DIST": ("input defect: target-season lines were blanked for point-in-time safety and the data arm read the "
                         "NaN implied total as 0 (design() nan_to_num), and current-season games were excluded from its "
                         "features. On the held-out 2025 rungs the first defect alone moves the arm from +0.0099 to +0.0383 "
                         "Brier vs the market (research/player_engine_v3/RESULTS.md). Superseded by DATA_PLAYER_V3."),
    "HYBRID_PLAYER_DIST": ("blends 30% of the defective DATA_PLAYER_DIST (see its entry); superseded by HYBRID_PLAYER_V3"),
}
# Arms that are research by construction until their promotion evidence exists, whatever a short sample shows.
RESEARCH_BY_DESIGN = {
    "DATA_PLAYER_V3": "new model version (data-player-dist-3.0.0); no prospective record yet",
    "HYBRID_PLAYER_V3": "new blend on DATA_PLAYER_V3; no prospective record yet",
    "DATA_PLAYER_V4": ("new model version (data-player-dist-4.0.0, structural snap/volume/allocation challenger); historical "
                       "evidence qualifies it for prospective collection only (research/player_engine_v4/RESULTS.md)"),
    "HYBRID_PLAYER_V4": "new blend on DATA_PLAYER_V4 (hybrid-player-dist-4.0.0); no prospective record yet",
}


def _clip(p):
    return min(max(float(p), 1e-4), 1 - 1e-4)


class Accumulator:
    """Per (arm, family) per game sums, one row at a time. Serialisable, so weeks combine without the rows."""

    def __init__(self):
        self.g = defaultdict(lambda: defaultdict(float))    # (arm, family, game) -> sums
        self.meta = defaultdict(dict)                        # (arm, family, game) -> {"week": ...}

    def add(self, r):
        if r.get("evidence_class") != "PROSPECTIVE_FROZEN":
            return
        cv, y, mid, gid = r.get("contract_value"), r.get("settled_yes"), r.get("h_mid"), r.get("game_id")
        if cv is None or y is None or mid is None or not gid:
            return
        arm = r.get("model_arm") or "?"
        fams = [r.get("family_group") or "?", "ALL"]
        if r.get("abstention_state") == "PROJECTION_VALID":
            fams.append("ALL|VALID_ONLY")
        p, m, yy = _clip(cv), _clip(mid), float(y)
        bm, bk = (p - yy) ** 2, (m - yy) ** 2
        lm = -(yy * math.log(p) + (1 - yy) * math.log(1 - p)); lk = -(yy * math.log(m) + (1 - yy) * math.log(1 - m))
        for fam in fams:
            k = (arm, fam, gid)
            s = self.g[k]
            s["n"] += 1; s["bm"] += bm; s["bk"] += bk; s["lm"] += lm; s["lk"] += lk
            b = min(int(p * 10), 9)
            s[f"cp{b}"] += p; s[f"cy{b}"] += yy; s[f"cn{b}"] += 1
            if r.get("synchronization_state") == "SYNCHRONIZED":
                s["sync"] += 1
            if r.get("close_quality") in ("EXCELLENT", "GOOD"):
                s["close_good"] += 1
            clv = r.get("clv_mid_toward_model")
            if clv is not None:
                s["clv"] += float(clv); s["nclv"] += 1
            pnl = r.get("exec_pnl_net")
            if pnl is not None:
                s["pnl"] += float(pnl); s["npnl"] += 1
            if r.get("week") is not None:
                self.meta[k]["week"] = r.get("week")

    def to_json(self) -> list:
        return [{"arm": k[0], "family": k[1], "game_id": k[2], "week": self.meta[k].get("week"), **dict(v)} for k, v in self.g.items()]

    @classmethod
    def from_json(cls, rows: list) -> "Accumulator":
        acc = cls()
        for r in rows:
            k = (r["arm"], r["family"], r["game_id"])
            for kk, vv in r.items():
                if kk not in ("arm", "family", "game_id", "week"):
                    acc.g[k][kk] += float(vv)
            if r.get("week") is not None:
                acc.meta[k]["week"] = r["week"]
        return acc

    def merge(self, other: "Accumulator"):
        for k, v in other.g.items():
            for kk, vv in v.items():
                self.g[k][kk] += vv
            self.meta[k].update(other.meta.get(k, {}))
        return self


def _mean_se(xs):
    n = len(xs)
    if n == 0:
        return None, None
    m = sum(xs) / n
    if n < 2:
        return m, None
    var = sum((x - m) ** 2 for x in xs) / (n - 1)
    return m, math.sqrt(var / n)


def metrics(acc: Accumulator) -> dict:
    """(arm, family) -> game-level statistics."""
    by = defaultdict(list)
    for (arm, fam, gid), s in acc.g.items():
        by[(arm, fam)].append((gid, s, acc.meta.get((arm, fam, gid), {}).get("week")))
    out = {}
    for key, games in by.items():
        d = [s["bm"] / s["n"] - s["bk"] / s["n"] for _, s, _w in games if s["n"]]
        dl = [s["lm"] / s["n"] - s["lk"] / s["n"] for _, s, _w in games if s["n"]]
        clv = [s["clv"] / s["nclv"] for _, s, _w in games if s.get("nclv")]
        pnl = [s["pnl"] / s["npnl"] for _, s, _w in games if s.get("npnl")]
        n_rows = sum(s["n"] for _, s, _w in games)
        md, sd = _mean_se(d); ml, sl = _mean_se(dl); mc, sc = _mean_se(clv); mp, sp = _mean_se(pnl)
        # calibration over rows (descriptive): ECE across ten probability bins
        ece_num, ece_den = 0.0, 0.0
        for b in range(10):
            cn = sum(s.get(f"cn{b}", 0) for _, s, _w in games)
            if cn:
                cp = sum(s.get(f"cp{b}", 0) for _, s, _w in games) / cn
                cy = sum(s.get(f"cy{b}", 0) for _, s, _w in games) / cn
                ece_num += cn * abs(cp - cy); ece_den += cn
        brier_m = sum(s["bm"] for _, s, _w in games) / n_rows if n_rows else None
        brier_k = sum(s["bk"] for _, s, _w in games) / n_rows if n_rows else None
        out[key] = {"arm": key[0], "family": key[1], "n_games": len(d), "n_weeks": len({w for _, _, w in games if w is not None}),
                    "n_rows": int(n_rows), "brier_model": brier_m, "brier_market": brier_k,
                    "delta_brier_game_mean": md, "delta_brier_se": sd,
                    "delta_brier_upper95": (md + 1.96 * sd) if (md is not None and sd is not None) else None,
                    "z": (md / sd) if (md is not None and sd) else None,
                    "delta_logloss_game_mean": ml, "delta_logloss_se": sl,
                    "ece": (ece_num / ece_den) if ece_den else None,
                    "clv_game_mean": mc, "clv_se": sc, "pnl_net_game_mean": mp, "pnl_net_se": sp,
                    "sync_share": (sum(s.get("sync", 0) for _, s, _w in games) / n_rows) if n_rows else None,
                    "close_quality_share": (sum(s.get("close_good", 0) for _, s, _w in games) / n_rows) if n_rows else None}
    return out


def decide(m: dict, policy: dict = POLICY) -> tuple[str, list]:
    """One status + every reason, from the metrics of one (arm, family)."""
    arm = m["arm"]
    if arm in KNOWN_DEFECTS:
        return DISABLED, [KNOWN_DEFECTS[arm]]
    why = []
    g, w = m["n_games"], m["n_weeks"]
    md, up, z = m["delta_brier_game_mean"], m["delta_brier_upper95"], m["z"]
    if g < policy["min_games_watch"]:
        return RESEARCH_ONLY, [f"{g} independent games < {policy['min_games_watch']} needed to measure"]
    if z is not None and z > policy["worse_z"]:
        return RESEARCH_ONLY, [f"measurably worse than the market: game-level Brier delta {md:+.4f} (z {z:+.1f})"]
    if arm in RESEARCH_BY_DESIGN and (g < policy["min_games_limited"] or w < policy["min_weeks_limited"]):
        return RESEARCH_ONLY, [RESEARCH_BY_DESIGN[arm]]
    status = WATCH
    why.append(f"{g} games over {w} week(s); Brier delta {md:+.4f} (upper95 {up:+.4f})" if up is not None else f"{g} games")
    quality_ok = ((m.get("sync_share") or 0) >= policy["min_sync_share"]
                  and (m.get("close_quality_share") or 0) >= policy["min_close_quality_share"])
    if not quality_ok:
        why.append("evidence quality below policy (synchronization or close quality)")
        return status, why
    lim = (g >= policy["min_games_limited"] and w >= policy["min_weeks_limited"] and up is not None and up <= policy["limited_max_upper"]
           and (m.get("ece") is not None and m["ece"] <= policy["max_ece_limited"]) and (m.get("clv_game_mean") or 0) >= 0)
    if not lim:
        why.append(f"not LIMITED: needs >= {policy['min_games_limited']} games / {policy['min_weeks_limited']} weeks, upper95 <= "
                   f"{policy['limited_max_upper']}, ECE <= {policy['max_ece_limited']}, CLV >= 0")
        return status, why
    status = LIMITED
    tr = (g >= policy["min_games_trusted"] and w >= policy["min_weeks_trusted"] and up < policy["trusted_max_upper"]
          and m.get("clv_se") is not None and (m["clv_game_mean"] - 1.96 * m["clv_se"]) > 0
          and (m.get("pnl_net_game_mean") or -1) >= 0)
    if tr:
        return TRUSTED, why + ["better than the market with statistical support, positive CLV and non-negative net P&L"]
    why.append("not TRUSTED: needs a significant Brier improvement, CLV > 0 with support, non-negative net P&L over "
               f">= {policy['min_games_trusted']} games / {policy['min_weeks_trusted']} weeks")
    return status, why


def build(acc: Accumulator, *, as_of: str, sources: list, policy: dict = POLICY) -> dict:
    ms = metrics(acc)
    fam = {}
    for key, m in sorted(ms.items()):
        st, why = decide(m, policy)
        fam[f"{key[0]}|{key[1]}"] = {**m, "status": st, "reasons": why}
    arms = {k.split("|")[0]: v["status"] for k, v in fam.items() if k.endswith("|ALL")}
    for arm in list(KNOWN_DEFECTS) + list(RESEARCH_BY_DESIGN):
        arms.setdefault(arm, DISABLED if arm in KNOWN_DEFECTS else RESEARCH_ONLY)
    return {"eligibility_version": ELIGIBILITY_VERSION, "as_of": as_of, "policy": policy, "sources": sources,
            "unit_of_evidence": "game (per-game mean of the row-level Brier difference; SE across games)",
            "evidence_filter": "PROSPECTIVE_FROZEN rows with a settled outcome and a horizon mid",
            "known_defects": KNOWN_DEFECTS, "research_by_design": RESEARCH_BY_DESIGN,
            "arms": arms, "families": fam}


def status_for(doc: dict | None, arm: str, family: str | None = None) -> dict:
    """The status a consumer should apply to one projection. Unknown -> RESEARCH_ONLY, never TRUSTED."""
    if not doc:
        base = DISABLED if arm in KNOWN_DEFECTS else RESEARCH_ONLY
        return {"status": base, "reason": KNOWN_DEFECTS.get(arm) or "no eligibility document available"}
    fams = doc.get("families") or {}
    f = fams.get(f"{arm}|{family}") if family else None
    a = fams.get(f"{arm}|ALL")
    chosen = f or a
    if chosen is None:
        st = (doc.get("arms") or {}).get(arm) or (DISABLED if arm in KNOWN_DEFECTS else RESEARCH_ONLY)
        return {"status": st, "reason": KNOWN_DEFECTS.get(arm) or RESEARCH_BY_DESIGN.get(arm) or "no evidence for this arm/family"}
    # a family can never exceed its arm
    st = chosen["status"]
    if a is not None and ORDER.index(a["status"]) < ORDER.index(st):
        st = a["status"]
    return {"status": st, "reason": "; ".join(chosen.get("reasons") or []), "n_games": chosen.get("n_games"),
            "delta_brier": chosen.get("delta_brier_game_mean"), "delta_brier_se": chosen.get("delta_brier_se")}
