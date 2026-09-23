"""UNIVERSAL SCORECARD v2: every settled projection of every engine on one set of proper scores.

Input rows are settled v2 projection records (a projection joined to a Settlement): p_yes, contract_value, mid,
yes_bid/yes_ask, settled_yes, engine, model_arm, market_family, period, stat_family, horizon_label,
identity_confidence, market_identification, availability_state, liquidity, quote_width, evidence_class.

Metrics (all on the CONTRACT VALUE against the settled payout unless named otherwise):
    brier, log_loss, n, base_rate; mean model-vs-market Brier difference with a GAME-CLUSTERED standard error
    (rows of one game are not independent; the cluster is the game, or the ticker's event when there is none);
    calibration (reliability bins, ECE); sharpness (mean |p - 0.5|); directional hit rate against the mid;
    market Brier on the mid for the same rows (the benchmark the model must beat); and the executable side:
    net EV of the trades the model's own probabilities would have taken at the ask, fees applied once.

Rows whose evidence_class is HISTORICAL_RESEARCH are NEVER pooled with PROSPECTIVE_FROZEN rows: the scorecard
is built per evidence class and the report labels each block.
"""
from __future__ import annotations

import math
from collections import defaultdict

SCORECARD_VERSION = "scorecard-2.0.0"
SEGMENTS = ("engine", "model_arm", "market_family", "period", "stat_family", "horizon_label", "identity_confidence",
            "market_identification", "availability_state", "liquidity_band", "width_band", "semantic_confidence", "support_state")
WIDTH_BANDS = ((0.02, "<=2c"), (0.05, "3-5c"), (0.10, "6-10c"), (float("inf"), ">10c"))
LIQUIDITY_BANDS = ((1e-9, "none"), (100.0, "<$100"), (1000.0, "$100-1k"), (float("inf"), ">$1k"))
EPS = 1e-6


def _f(x):
    try:
        return None if x is None else float(x)
    except (TypeError, ValueError):
        return None


def _band(v, bands):
    v = _f(v)
    if v is None:
        return "unknown"
    for lim, name in bands:
        if v <= lim:
            return name
    return bands[-1][1]


def _brier(p, y):
    return (p - y) ** 2


def _logloss(p, y):
    p = min(max(p, EPS), 1 - EPS)
    return -(y * math.log(p) + (1 - y) * math.log(1 - p))


def _cluster_mean_se(values: list, clusters: list) -> tuple[float | None, float | None, int]:
    """Mean of per-row values with a cluster-robust standard error (clusters = games)."""
    if not values:
        return None, None, 0
    n = len(values); mean = sum(values) / n
    by = defaultdict(list)
    for v, c in zip(values, clusters):
        by[c].append(v)
    G = len(by)
    if G < 2:
        return mean, None, G
    # cluster sums of residuals
    s = sum((sum(v - mean for v in vs)) ** 2 for vs in by.values())
    se = math.sqrt(s) / n * math.sqrt(G / (G - 1))
    return mean, se, G


def _calibration(pairs, width=0.1):
    bins = defaultdict(lambda: [0, 0.0, 0.0])
    for p, y in pairs:
        b = min(int(p / width), int(round(1 / width)) - 1)
        bins[b][0] += 1; bins[b][1] += p; bins[b][2] += y
    out, ece, n = [], 0.0, len(pairs)
    for b in sorted(bins):
        c, sp, sy = bins[b]
        out.append({"bin": f"{b*width:.1f}-{(b+1)*width:.1f}", "n": c, "mean_p": sp / c, "mean_y": sy / c})
        ece += c / n * abs(sp / c - sy / c)
    return {"bins": out, "ece": ece}


def metric_block(rows: list) -> dict:
    """rows: settled records with contract_value, settled_yes; optional mid, yes_ask, game_id."""
    pairs, mpairs, diffs, clusters, hits, tie_kind = [], [], [], [], [], 0
    for r in rows:
        cv, y = _f(r.get("contract_value")), _f(r.get("settled_yes"))
        if cv is None or y is None:
            continue
        cl = r.get("game_id") or r.get("event_ticker") or r.get("ticker")
        pairs.append((cv, y)); clusters.append(cl)
        mid = _f(r.get("mid"))
        if mid is not None:
            mpairs.append((mid, y)); diffs.append(_brier(cv, y) - _brier(mid, y))
            if abs(cv - mid) > 1e-9:
                hits.append(1.0 if (cv > mid) == (y > mid) else 0.0)
        if r.get("settlement_kind") == "tie_split":
            tie_kind += 1
    if not pairs:
        return {"n": 0}
    n = len(pairs)
    out = {"n": n, "n_games": len(set(clusters)), "base_rate": sum(y for _, y in pairs) / n,
           "brier": sum(_brier(p, y) for p, y in pairs) / n, "log_loss": sum(_logloss(p, y) for p, y in pairs) / n,
           "sharpness": sum(abs(p - 0.5) for p, _ in pairs) / n, "calibration": _calibration(pairs), "n_tie_split": tie_kind}
    if mpairs:
        m = len(mpairs)
        out["market_n"] = m
        out["market_brier"] = sum(_brier(p, y) for p, y in mpairs) / m
        out["market_log_loss"] = sum(_logloss(p, y) for p, y in mpairs) / m
        mean, se, G = _cluster_mean_se(diffs, [c for c, r in zip(clusters, rows) if _f(r.get("mid")) is not None and _f(r.get("contract_value")) is not None and _f(r.get("settled_yes")) is not None])
        out["brier_minus_market"] = mean; out["brier_minus_market_se_clustered"] = se; out["clusters"] = G
        out["brier_minus_market_z"] = (mean / se) if (se and se > 0) else None
        out["directional_hit_rate"] = (sum(hits) / len(hits)) if hits else None
        out["n_directional"] = len(hits)
    return out


def executable_block(rows: list, schedule=None, as_of=None, *, edge_min: float = 0.05) -> dict:
    """What taking the model's own edges at the ASK would have paid, fees once. No mid anywhere."""
    from nfl_edge.execution import fees as F
    taken, pnl, unknown = 0, 0.0, 0
    for r in rows:
        cv, y = _f(r.get("contract_value")), _f(r.get("settled_yes"))
        ya, na = _f(r.get("yes_ask")), _f(r.get("no_ask"))
        if cv is None or y is None:
            continue
        side = None
        if ya is not None and 0 < ya < 1 and cv - ya >= edge_min:
            side, price, payout = "YES", ya, y
        elif na is not None and 0 < na < 1 and (1 - cv) - na >= edge_min:
            side, price, payout = "NO", na, 1.0 - y
        if side is None:
            continue
        fee = 0.0
        if schedule is not None:
            try:
                q = F.net_executable_ev(price, price, 1.0, schedule, series_ticker=r.get("series_ticker"), as_of=as_of)
                if not q.is_known:
                    unknown += 1; continue
                fee = -float(q.net_ev_dollars)
            except Exception:  # noqa: BLE001
                unknown += 1; continue
        taken += 1
        pnl += payout - price - fee
    return {"n_taken": taken, "pnl_per_contract": (pnl / taken) if taken else None, "pnl_total": pnl, "n_fee_unknown": unknown,
            "edge_min": edge_min, "note": "executable price = ask at observation; fee applied once per contract; no slippage model"}


def segment(rows, key, min_n=1):
    by = defaultdict(list)
    for r in rows:
        v = r.get(key)
        if key == "liquidity_band":
            v = _band(r.get("liquidity"), LIQUIDITY_BANDS)
        elif key == "width_band":
            v = _band(r.get("quote_width"), WIDTH_BANDS)
        by[str(v)].append(r)
    return {k: metric_block(v) for k, v in sorted(by.items()) if len(v) >= min_n}


def effective_counts(rs: list) -> dict:
    """Physical evidence rows vs effective predictions (see _ClassAcc.season_best); the batch twin of the accumulator."""
    best, n_game, n_game_settled = {}, 0, 0
    for r in rs:
        ok = _f(r.get("settled_yes")) is not None and _f(r.get("contract_value")) is not None
        if r.get("evidence_tier") is not None and r.get("prediction_id"):
            rank = (1 if r.get("evidence_tier") == "TERMINAL" else 0, str(r.get("evaluated_at") or ""))
            cur = best.get(r["prediction_id"])
            if cur is None or rank > cur[0]:
                best[r["prediction_id"]] = (rank, ok)
        else:
            n_game += 1; n_game_settled += int(ok)
    n_eff = n_game + len(best)
    n_eff_settled = n_game_settled + sum(1 for (_rk, ok) in best.values() if ok)
    return {"n_evidence_rows": len(rs), "n_effective_predictions": n_eff, "n_settled_effective": n_eff_settled,
            "n_unresolved_effective": n_eff - n_eff_settled, "n_superseded_provisional_rows": len(rs) - n_eff}


def build_scorecard(rows: list, *, schedule=None, as_of=None, min_segment_n: int = 5) -> dict:
    by_class = defaultdict(list)
    for r in rows:
        by_class[r.get("evidence_class") or "UNKNOWN"].append(r)
    out = {"version": SCORECARD_VERSION, "n_rows": len(rows), "by_evidence_class": {}}
    for cls, rs in by_class.items():
        settled = [r for r in rs if _f(r.get("settled_yes")) is not None and _f(r.get("contract_value")) is not None]
        block = {"n_settled": len(settled), "n_unsettled": len(rs) - len(settled), **effective_counts(rs), "overall": metric_block(settled),
                 "executable": executable_block(settled, schedule, as_of), "segments": {k: segment(settled, k, min_segment_n) for k in SEGMENTS}}
        # arm-vs-arm on the same contracts (paired), per stat family
        block["paired_arms"] = paired_arms(settled)
        out["by_evidence_class"][cls] = block
    return out


def paired_arms(rows: list) -> dict:
    """Brier per arm on exactly the contracts every arm priced (same snapshot + ticker), by stat family."""
    by_key = defaultdict(dict)
    for r in rows:
        by_key[(r.get("snapshot_id"), r.get("ticker"))][r.get("model_arm")] = r
    arms = sorted({r.get("model_arm") for r in rows if r.get("model_arm")})
    out = {}
    for fam_key in sorted({(r.get("engine"), r.get("stat_family") or r.get("market_family")) for r in rows}):
        common = [d for d in by_key.values() if all(a in d for a in arms) and (next(iter(d.values())).get("engine"), next(iter(d.values())).get("stat_family") or next(iter(d.values())).get("market_family")) == fam_key]
        if len(common) < 5 or len(arms) < 2:
            continue
        res = {"n": len(common)}
        for a in arms:
            res[a] = sum(_brier(_f(d[a]["contract_value"]), _f(d[a]["settled_yes"])) for d in common) / len(common)
        mids = [d[arms[0]] for d in common if _f(d[arms[0]].get("mid")) is not None]
        if mids:
            res["market_mid"] = sum(_brier(_f(d["mid"]), _f(d["settled_yes"])) for d in mids) / len(mids)
        out["/".join(str(x) for x in fam_key)] = res
    return out


# --------------------------------------------------------------------------------------------- streaming build
#
# build_scorecard() above is the definition. The accumulator below computes the same scorecard one row at a
# time so the settlement driver can rebuild it from the WHOLE corpus without holding the corpus: every sum,
# bin and cluster total is carried incrementally, bounded by the number of segments, games and arms rather
# than by the number of rows. tests/test_postgame_memory_v2.py asserts the two agree.


class _MetricAcc:
    """metric_block(), incrementally. Sums are accumulated in row order, so the means come out identical."""

    __slots__ = ("n", "sum_y", "sum_brier", "sum_ll", "sum_sharp", "bins", "tie", "m", "sum_brier_m", "sum_ll_m",
                 "diff_sum", "diff_by_cluster", "hits_sum", "hits_n", "clusters")

    def __init__(self):
        self.n = self.tie = self.m = self.hits_n = 0
        self.sum_y = self.sum_brier = self.sum_ll = self.sum_sharp = 0.0
        self.sum_brier_m = self.sum_ll_m = self.diff_sum = self.hits_sum = 0.0
        self.bins = {}
        self.diff_by_cluster = {}
        self.clusters = set()

    def add(self, r: dict):
        cv, y = _f(r.get("contract_value")), _f(r.get("settled_yes"))
        if cv is None or y is None:
            return
        cl = r.get("game_id") or r.get("event_ticker") or r.get("ticker")
        self.n += 1
        self.sum_y += y
        self.sum_brier += _brier(cv, y)
        self.sum_ll += _logloss(cv, y)
        self.sum_sharp += abs(cv - 0.5)
        self.clusters.add(cl)
        b = min(int(cv / 0.1), int(round(1 / 0.1)) - 1)
        cnt = self.bins.get(b)
        if cnt is None:
            cnt = self.bins[b] = [0, 0.0, 0.0]
        cnt[0] += 1; cnt[1] += cv; cnt[2] += y
        mid = _f(r.get("mid"))
        if mid is not None:
            self.m += 1
            self.sum_brier_m += _brier(mid, y)
            self.sum_ll_m += _logloss(mid, y)
            d = _brier(cv, y) - _brier(mid, y)
            self.diff_sum += d
            c = self.diff_by_cluster.get(cl)
            if c is None:
                c = self.diff_by_cluster[cl] = [0.0, 0]
            c[0] += d; c[1] += 1
            if abs(cv - mid) > 1e-9:
                self.hits_n += 1
                self.hits_sum += 1.0 if (cv > mid) == (y > mid) else 0.0
        if r.get("settlement_kind") == "tie_split":
            self.tie += 1

    def finish(self) -> dict:
        if not self.n:
            return {"n": 0}
        n = self.n
        bins, ece = [], 0.0
        for b in sorted(self.bins):
            c, sp, sy = self.bins[b]
            bins.append({"bin": f"{b*0.1:.1f}-{(b+1)*0.1:.1f}", "n": c, "mean_p": sp / c, "mean_y": sy / c})
            ece += c / n * abs(sp / c - sy / c)
        out = {"n": n, "n_games": len(self.clusters), "base_rate": self.sum_y / n, "brier": self.sum_brier / n,
               "log_loss": self.sum_ll / n, "sharpness": self.sum_sharp / n, "calibration": {"bins": bins, "ece": ece},
               "n_tie_split": self.tie}
        if self.m:
            m = self.m
            out["market_n"] = m
            out["market_brier"] = self.sum_brier_m / m
            out["market_log_loss"] = self.sum_ll_m / m
            mean = self.diff_sum / m
            G = len(self.diff_by_cluster)
            if G < 2:
                se = None
            else:
                s = sum((tot - cnt * mean) ** 2 for tot, cnt in self.diff_by_cluster.values())
                se = math.sqrt(s) / m * math.sqrt(G / (G - 1))
            out["brier_minus_market"] = mean; out["brier_minus_market_se_clustered"] = se; out["clusters"] = G
            out["brier_minus_market_z"] = (mean / se) if (se and se > 0) else None
            out["directional_hit_rate"] = (self.hits_sum / self.hits_n) if self.hits_n else None
            out["n_directional"] = self.hits_n
        return out


class _ExecAcc:
    """executable_block(), incrementally."""

    __slots__ = ("taken", "pnl", "unknown", "schedule", "as_of", "edge_min")

    def __init__(self, schedule=None, as_of=None, edge_min: float = 0.05):
        self.taken, self.pnl, self.unknown = 0, 0.0, 0
        self.schedule, self.as_of, self.edge_min = schedule, as_of, edge_min

    def add(self, r: dict):
        from nfl_edge.execution import fees as F
        cv, y = _f(r.get("contract_value")), _f(r.get("settled_yes"))
        ya, na = _f(r.get("yes_ask")), _f(r.get("no_ask"))
        if cv is None or y is None:
            return
        side = None
        if ya is not None and 0 < ya < 1 and cv - ya >= self.edge_min:
            side, price, payout = "YES", ya, y
        elif na is not None and 0 < na < 1 and (1 - cv) - na >= self.edge_min:
            side, price, payout = "NO", na, 1.0 - y
        if side is None:
            return
        fee = 0.0
        if self.schedule is not None:
            try:
                q = F.net_executable_ev(price, price, 1.0, self.schedule, series_ticker=r.get("series_ticker"), as_of=self.as_of)
                if not q.is_known:
                    self.unknown += 1; return
                fee = -float(q.net_ev_dollars)
            except Exception:  # noqa: BLE001
                self.unknown += 1; return
        self.taken += 1
        self.pnl += payout - price - fee

    def finish(self) -> dict:
        return {"n_taken": self.taken, "pnl_per_contract": (self.pnl / self.taken) if self.taken else None, "pnl_total": self.pnl,
                "n_fee_unknown": self.unknown, "edge_min": self.edge_min,
                "note": "executable price = ask at observation; fee applied once per contract; no slippage model"}


def _fam_key(r: dict) -> tuple:
    return (r.get("engine"), r.get("stat_family") or r.get("market_family"))


class _PairedAcc:
    """paired_arms(), folded one game at a time.

    A (snapshot, ticker) key never spans two games, so the per-key arm table only has to live for the game being
    read. `arms` is the set of arms among ALL settled rows of the class, which is only known at the end, so each
    game is folded with the arms seen so far and remembers which; if the final set differs, those games are
    re-read through the driver's `reread(game_id)` callback and folded again. In practice every game carries
    every arm and the callback is never used, but the result is exact either way.
    """

    __slots__ = ("arms", "fams", "by_key", "sums", "folded_with", "pending_game")

    def __init__(self):
        self.arms, self.fams = set(), set()
        self.by_key = {}                                    # (snapshot, ticker) -> {arm: (cv, y, mid, fam_key)}
        self.sums = {}                                      # game -> fam_key -> [n, {arm: brier_sum}, m_n, m_sum]
        self.folded_with = {}                               # game -> frozenset(arms) used at fold time
        self.pending_game = None

    def add(self, r: dict, game: str):
        arm = r.get("model_arm")
        if arm:
            self.arms.add(arm)
        self.fams.add(_fam_key(r))
        d = self.by_key.get((r.get("snapshot_id"), r.get("ticker")))
        if d is None:
            d = self.by_key[(r.get("snapshot_id"), r.get("ticker"))] = {}
        d[arm] = (_f(r.get("contract_value")), _f(r.get("settled_yes")), _f(r.get("mid")), _fam_key(r))
        self.pending_game = game

    def end_game(self, game: str):
        arms = sorted(self.arms)
        table = self.sums.setdefault(game, {})
        table.clear()
        if len(arms) >= 2:
            first = arms[0]
            for d in self.by_key.values():
                if not all(a in d for a in arms):
                    continue
                fk = next(iter(d.values()))[3]
                t = table.get(fk)
                if t is None:
                    t = table[fk] = [0, {a: 0.0 for a in arms}, 0, 0.0]
                t[0] += 1
                for a in arms:
                    cv, y, _mid, _fk = d[a]
                    t[1][a] += _brier(cv, y)
                cv0, y0, mid0, _ = d[first]
                if mid0 is not None:
                    t[2] += 1
                    t[3] += _brier(mid0, y0)
        self.folded_with[game] = frozenset(arms)
        self.by_key = {}
        self.pending_game = None

    def finish(self, reread=None) -> dict:
        if self.pending_game is not None:
            self.end_game(self.pending_game)
        final = frozenset(self.arms)
        stale = [g for g, a in self.folded_with.items() if a != final]
        if stale:
            if reread is None:
                raise RuntimeError(f"paired-arm fold is stale for {len(stale)} game(s) and no reread callback was given")
            for g in stale:
                self.by_key = {}
                for r in reread(g):
                    self.add(r, g)
                self.end_game(g)
        arms = sorted(self.arms)
        out = {}
        if len(arms) < 2:
            return out
        for fk in sorted(self.fams, key=lambda k: tuple(str(x) for x in k)):
            n, per_arm, m_n, m_sum = 0, {a: 0.0 for a in arms}, 0, 0.0
            for table in self.sums.values():
                t = table.get(fk)
                if not t:
                    continue
                n += t[0]; m_n += t[2]; m_sum += t[3]
                for a in arms:
                    per_arm[a] += t[1][a]
            if n < 5:
                continue
            res = {"n": n}
            for a in arms:
                res[a] = per_arm[a] / n
            if m_n:
                res["market_mid"] = m_sum / m_n
            out["/".join(str(x) for x in fk)] = res
        return out


class _ClassAcc:
    __slots__ = ("n_rows", "n_settled", "overall", "exec", "segments", "paired", "season_best", "n_game_rows", "n_game_settled")

    def __init__(self, schedule, as_of):
        self.n_rows = self.n_settled = 0
        # EFFECTIVE IDENTITY. A season contract's "not decided yet" is filed once per evidence vintage (every run
        # until the season decides it), so the physical corpus holds many rows per prediction and n_rows -
        # n_settled counted every superseded vintage as an unsettled prediction. Game rows are one per
        # prediction; season rows keep only their best (terminal over provisional, then latest) per prediction.
        self.season_best = {}
        self.n_game_rows = self.n_game_settled = 0
        self.overall = _MetricAcc()
        self.exec = _ExecAcc(schedule, as_of)
        self.segments = {k: {} for k in SEGMENTS}
        self.paired = _PairedAcc()


class ScorecardAccumulator:
    """build_scorecard(), one row at a time. Feed rows game by game and call end_game() between games."""

    def __init__(self, *, schedule=None, as_of=None, min_segment_n: int = 5):
        self.schedule, self.as_of, self.min_segment_n = schedule, as_of, min_segment_n
        self.n_rows = 0
        self.by_class: dict = {}
        self._game = None

    def add(self, r: dict, game: str | None = None):
        game = game if game is not None else (r.get("game_id") or "SEASON")
        if self._game is not None and game != self._game:
            self.end_game()
        self._game = game
        self.n_rows += 1
        cls = r.get("evidence_class") or "UNKNOWN"
        c = self.by_class.get(cls)
        if c is None:
            c = self.by_class[cls] = _ClassAcc(self.schedule, self.as_of)
        c.n_rows += 1
        settled_ok = _f(r.get("settled_yes")) is not None and _f(r.get("contract_value")) is not None
        if r.get("evidence_tier") is not None and r.get("prediction_id"):
            rank = (1 if r.get("evidence_tier") == "TERMINAL" else 0, str(r.get("evaluated_at") or ""))
            cur = c.season_best.get(r["prediction_id"])
            if cur is None or rank > cur[0]:
                c.season_best[r["prediction_id"]] = (rank, settled_ok)
        else:
            c.n_game_rows += 1
            c.n_game_settled += int(settled_ok)
        if not settled_ok:
            return
        c.n_settled += 1
        c.overall.add(r)
        c.exec.add(r)
        for key in SEGMENTS:
            v = r.get(key)
            if key == "liquidity_band":
                v = _band(r.get("liquidity"), LIQUIDITY_BANDS)
            elif key == "width_band":
                v = _band(r.get("quote_width"), WIDTH_BANDS)
            seg = c.segments[key]
            m = seg.get(str(v))
            if m is None:
                m = seg[str(v)] = [_MetricAcc(), 0]
            m[0].add(r)
            m[1] += 1
        c.paired.add(r, game)

    def end_game(self):
        if self._game is None:
            return
        for c in self.by_class.values():
            if c.paired.pending_game is not None:
                c.paired.end_game(self._game)
        self._game = None

    def finish(self, reread=None) -> dict:
        """`reread(game_id)` yields that game's corpus rows again; only needed if an evidence class gained an
        arm after some games were folded (see _PairedAcc)."""
        self.end_game()
        out = {"version": SCORECARD_VERSION, "n_rows": self.n_rows, "by_evidence_class": {}}
        for cls, c in self.by_class.items():
            n_eff = c.n_game_rows + len(c.season_best)
            n_eff_settled = c.n_game_settled + sum(1 for (_rk, ok) in c.season_best.values() if ok)
            block = {"n_settled": c.n_settled, "n_unsettled": c.n_rows - c.n_settled,
                     # physical rows vs effective predictions: n_unsettled above counts every provisional season
                     # vintage; these count each prediction once, at its best evidence
                     "n_evidence_rows": c.n_rows, "n_effective_predictions": n_eff, "n_settled_effective": n_eff_settled,
                     "n_unresolved_effective": n_eff - n_eff_settled,
                     "n_superseded_provisional_rows": c.n_rows - n_eff,
                     "overall": c.overall.finish(),
                     "executable": c.exec.finish(),
                     "segments": {k: {v: m.finish() for v, (m, cnt) in sorted(c.segments[k].items()) if cnt >= self.min_segment_n}
                                  for k in SEGMENTS}}
            scoped = None
            if reread is not None:
                def scoped(g, _cls=cls):
                    return (r for r in reread(g) if (r.get("evidence_class") or "UNKNOWN") == _cls
                            and _f(r.get("settled_yes")) is not None and _f(r.get("contract_value")) is not None)
            block["paired_arms"] = c.paired.finish(scoped)
            out["by_evidence_class"][cls] = block
        return out


def _fmt(v, nd=4):
    return "-" if v is None else (f"{v:.{nd}f}" if isinstance(v, float) else str(v))


def render(sc: dict, title="Shadow v2 scorecard") -> str:
    L = [f"# {title}", "", f"scorecard {sc['version']}; rows {sc['n_rows']}", ""]
    for cls, b in sc["by_evidence_class"].items():
        o = b["overall"]
        L += [f"## Evidence class: {cls}", "",
              (f"effective predictions {b['n_effective_predictions']}: settled {b['n_settled_effective']}, unresolved "
               f"{b['n_unresolved_effective']}; evidence rows {b['n_evidence_rows']} (superseded provisional season vintages "
               f"{b['n_superseded_provisional_rows']})" if "n_effective_predictions" in b else
               f"settled {b['n_settled']}, unsettled {b['n_unsettled']}"), ""]
        if o.get("n"):
            L += ["| metric | model | market (mid) |", "|---|---|---|",
                  f"| n | {o['n']} | {o.get('market_n', '-')} |", f"| Brier | {_fmt(o['brier'])} | {_fmt(o.get('market_brier'))} |",
                  f"| log loss | {_fmt(o['log_loss'])} | {_fmt(o.get('market_log_loss'))} |",
                  f"| Brier - market (clustered by game) | {_fmt(o.get('brier_minus_market'))} ± {_fmt(o.get('brier_minus_market_se_clustered'))} (z {_fmt(o.get('brier_minus_market_z'), 2)}) | |",
                  f"| ECE | {_fmt(o['calibration']['ece'])} | |", f"| sharpness | {_fmt(o['sharpness'])} | |",
                  f"| directional hit rate vs mid | {_fmt(o.get('directional_hit_rate'))} (n={o.get('n_directional')}) | |", ""]
            e = b["executable"]
            L += [f"executable (ask, fees once, edge >= {e['edge_min']}): taken {e['n_taken']}, P&L/contract {_fmt(e['pnl_per_contract'])}, fee-unknown {e['n_fee_unknown']}", ""]
            for seg in ("engine", "model_arm", "market_family", "stat_family", "horizon_label", "market_identification", "availability_state", "liquidity_band"):
                s = b["segments"].get(seg) or {}
                if not s:
                    continue
                L += [f"### by {seg}", "", "| value | n | Brier | market | diff ± se (z) |", "|---|---|---|---|---|"]
                for k, m in s.items():
                    L.append(f"| {k} | {m.get('n')} | {_fmt(m.get('brier'))} | {_fmt(m.get('market_brier'))} | {_fmt(m.get('brier_minus_market'))} ± {_fmt(m.get('brier_minus_market_se_clustered'))} ({_fmt(m.get('brier_minus_market_z'), 2)}) |")
                L.append("")
            if b["paired_arms"]:
                L += ["### paired arms (same contracts)", ""]
                for k, m in b["paired_arms"].items():
                    L.append(f"- {k}: n={m['n']}; " + ", ".join(f"{a} {_fmt(v)}" for a, v in m.items() if a != "n"))
                L.append("")
        else:
            L += ["no settled rows", ""]
    return "\n".join(L)
