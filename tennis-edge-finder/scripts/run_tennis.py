#!/usr/bin/env python3
"""RUN TENNIS -- price the entire active Kalshi tennis universe from one coherent distribution per match.

Pipeline (all fail-closed; every exclusion is listed with a reason in the coverage report):
  1. latest discovery snapshot -> every OPEN tennis market -> parse (family, subject, opponent, line, ...)
  2. freshest quote per ticker: latest capture quotes if present, else the discovery-time market record
  3. per event: both competitors' full names + Kalshi competitor UUIDs -> canonical player ids (exact
     normalised full-name match against the rating state of the tour; ambiguous/absent => UNMAPPED)
  4. competition text -> level / format (config/formats.json) / surface (canonical table lookup)
  5. ratings as of the state artifact: Elo (surface-blended) -> P(match); serve/return abilities -> (pa, pb);
     derivative markets priced from the DP distribution built from the Elo-implied point probabilities
     (consistent by construction), the structural distribution recorded alongside
  6. prices vs quotes: raw edge, fee-adjusted EV, breakeven ('bet up to'), data-quality grade
  7. append every priced market to the immutable ledger; write projections/latest.json (+ coverage) and the
     owner-facing REPORT.md. Real-money authority is OFF: recommendations are labelled HYPOTHETICAL.
"""
from __future__ import annotations

import argparse, glob, gzip, json, os, subprocess, sys
from collections import defaultdict
from datetime import datetime, timezone, date

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, PROJ)
from tennis_edge.kalshi.markets import parse_market  # noqa: E402
from tennis_edge.kalshi.families import FAMILIES  # noqa: E402
from tennis_edge.pricing.payoffs import price_market, check_consistency, PricingError  # noqa: E402
from tennis_edge.pricing.fees import FeeSchedule, expected_value, breakeven_price  # noqa: E402
from tennis_edge.pricing.competition import classify_competition, build_surface_lookup, lookup_surface  # noqa: E402
from tennis_edge.rules.formats import resolve_format, FormatResolutionError  # noqa: E402
from tennis_edge.sim.analytic import match_distribution, point_probs_from_match_prob, match_win_prob  # noqa: E402
from tennis_edge.models.elo import expected as elo_expected  # noqa: E402
from tennis_edge.models.state import load_state  # noqa: E402
from tennis_edge.models.quality import QualityInputs, data_quality  # noqa: E402
from tennis_edge.identity.kalshi_map import KalshiPlayerMapper  # noqa: E402
from tennis_edge.ledger.predictions import PredictionLedger  # noqa: E402
from tennis_edge.health.gates import _latest_discovery  # noqa: E402


def git_sha():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=PROJ, capture_output=True, text=True).stdout.strip()
    except Exception:
        return "unknown"


def load_open_markets(d):
    out = []
    for p in glob.glob(os.path.join(d, "markets", "*.json")):
        for m in json.load(open(p)).get("open", {}).get("markets") or []:
            out.append(m)
    return out


def latest_quotes(capture_root):
    """ticker -> freshest captured market record (from quotes streams); may be empty."""
    q = {}
    files = sorted(glob.glob(os.path.join(capture_root, "*", "*.quotes.jsonl.gz")) + glob.glob(os.path.join(capture_root, "*", "*.quotes.jsonl")))
    for f in files[-12:]:
        opener = gzip.open if f.endswith(".gz") else open
        with opener(f, "rt") as fh:
            for line in fh:
                r = json.loads(line)
                t = r.get("ticker")
                if t and (t not in q or r["captured_at"] > q[t]["captured_at"]):
                    q[t] = r
    return q


def fnum(x):
    try:
        v = float(x); return v if 0 < v < 1 else None
    except (TypeError, ValueError):
        return None


def surface_rating(rec, surface, w_max=0.5, n_half=20.0):
    r = rec["elo"]
    if surface and surface in rec.get("surfaces", {}):
        rs, ns = rec["surfaces"][surface]
        w = w_max * ns / (ns + n_half)
        return (1 - w) * r + w * rs
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--discovery", default=None)
    ap.add_argument("--capture", default=os.path.join(PROJ, "data", "kalshi", "capture"))
    ap.add_argument("--out", default=os.path.join(PROJ, "data", "research", "projections"))
    ap.add_argument("--ledger", default=os.path.join(PROJ, "data", "research", "ledger"))
    ap.add_argument("--no-ledger", action="store_true")
    a = ap.parse_args()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    d = a.discovery or _latest_discovery()
    if not d:
        raise SystemExit("no discovery snapshot; run scripts/kalshi/discover_tennis.py on a machine that can reach Kalshi")
    disc_summary = json.load(open(os.path.join(d, "summary.json")))
    states = {}
    for tour in ("ATP", "WTA"):
        p = os.path.join(PROJ, "data", "processed", f"ratings_{tour}.json")
        if os.path.exists(p):
            states[tour] = load_state(p)
    if not states:
        raise SystemExit("no rating state: run python -m tennis_edge.models.state --tour ATP/WTA")
    mapper = KalshiPlayerMapper(states)
    matches = pd.read_parquet(os.path.join(PROJ, "data", "processed", "matches.parquet"), columns=["tourney_name", "surface", "season"])
    surf_lookup = build_surface_lookup(matches)
    quotes = latest_quotes(a.capture)
    markets = load_open_markets(d)
    fee_types = {}
    for p in glob.glob(os.path.join(d, "series_detail", "*.json")):
        s = json.load(open(p)).get("series") or {}
        if s.get("ticker"):
            fee_types[s["ticker"]] = FeeSchedule(s.get("fee_type", "quadratic"), float(s.get("fee_multiplier") or 1))
    ledger = None if a.no_ledger else PredictionLedger(a.ledger)
    sha = git_sha()

    # ACTIVE universe: discovery's open markets, intersected with the tickers still open in the freshest capture pass
    # when that pass is < 45 min old (discovery snapshots are hours old; many of its 'open' markets are in play).
    capture_fresh = False
    if quotes:
        newest = max(r["captured_at"] for r in quotes.values())
        capture_fresh = (datetime.now(timezone.utc) - datetime.fromisoformat(newest)).total_seconds() < 45 * 60
    now = datetime.now(timezone.utc)
    parsed = {}; by_event = defaultdict(list); coverage = defaultdict(int); excluded = []
    for m in markets:
        pm = parse_market(m)
        parsed[pm.ticker] = (pm, m)
        coverage["active"] += 1
        if capture_fresh and pm.ticker not in quotes:
            coverage["closed_since_discovery"] += 1; excluded.append({"ticker": pm.ticker, "stage": "lifecycle", "reason": "not open in the freshest capture pass (closed/settled since discovery)"}); continue
        # PREGAME POLICY: refuse anything at or past its nominal start; for ITF/Challenger series the nominal
        # occurrence_datetime is NOT a start time (it usually falls after the market closes), so those rows are
        # additionally flagged start_basis=NOMINAL_UNRELIABLE and never actionable until first-ball truth exists.
        sched = m.get("occurrence_datetime") or m.get("expected_expiration_time")
        secs = _secs(sched)
        if secs is None or secs <= 300:
            coverage["past_nominal_start"] += 1; excluded.append({"ticker": pm.ticker, "stage": "pregame", "reason": f"nominal start {sched} is <= 5 min away or past (no first-ball truth available)"}); continue
        if pm.status == "UNPARSED":
            coverage["unparsed"] += 1; excluded.append({"ticker": pm.ticker, "stage": "parse", "reason": pm.reason}); continue
        if pm.status == "UNSUPPORTED_FAMILY" or not pm.projectable:
            coverage["unsupported_family"] += 1; excluded.append({"ticker": pm.ticker, "stage": "family", "reason": f"{pm.family}: {FAMILIES[pm.family].get('note', 'not priced')}"}); continue
        if pm.scope != "MATCH":
            coverage["tournament_scope_not_priced_tonight"] += 1; excluded.append({"ticker": pm.ticker, "stage": "scope", "reason": f"{pm.family}: draw simulation needs a draw feed (not wired)"}); continue
        by_event[pm.event_ticker].append(pm)

    projections = []; consistency_violations = []; projected_tickers = []
    today = date.today()
    for ev, pms in by_event.items():
        # competitors: full names per side from any market whose subject side is known
        names = {True: None, False: None}; comp_ids = {True: None, False: None}
        for pm in pms:
            if pm.subject and pm.subject_is_a is not None:
                names[pm.subject_is_a] = names[pm.subject_is_a] or pm.subject
                comp_ids[pm.subject_is_a] = comp_ids[pm.subject_is_a] or pm.competitor_id
        head = pms[0]
        info = classify_competition(head.competition, head.tour)
        tour = info["tour"]
        reason = None
        is_doubles = info["discipline"] != "singles" or head.discipline != "singles"
        if is_doubles:
            dres = price_doubles_event(ev, pms, names, comp_ids, info, tour, states, mapper, today, quotes, parsed, fee_types, disc_summary, sha, ledger)
            if dres["ok"]:
                projections.extend(dres["rows"]); projected_tickers.extend(r["ticker"] for r in dres["rows"]); coverage["projected_doubles"] += len(dres["rows"])
            else:
                for pm in pms:
                    coverage["excluded_event"] += 1; excluded.append({"ticker": pm.ticker, "stage": "doubles", "reason": dres["reason"]})
            continue
        if tour not in states:
            reason = f"tour {tour} has no rating state"
        elif not names[True] or not names[False]:
            reason = "could not recover both competitors' full names from the event's markets"
        if reason:
            for pm in pms:
                coverage["excluded_event"] += 1; excluded.append({"ticker": pm.ticker, "stage": "event", "reason": reason})
            continue
        maps = {side: mapper.resolve(tour, names[side], comp_ids[side], today) for side in (True, False)}
        if any(mp["status"] != "MAPPED" for mp in maps.values()):
            for pm in pms:
                coverage["unmapped_player"] += 1
                excluded.append({"ticker": pm.ticker, "stage": "identity", "reason": "; ".join(f"{names[s]}: {maps[s]['status']} ({maps[s].get('reason', '')})" for s in (True, False) if maps[s]["status"] != "MAPPED")})
            continue
        try:
            fmt = resolve_format(tour, info["level"], head.year or today.year, info["competition"] if info["level"] == "GRAND_SLAM" else None, "singles")
        except FormatResolutionError as e:
            for pm in pms:
                coverage["format_unresolved"] += 1; excluded.append({"ticker": pm.ticker, "stage": "format", "reason": str(e)})
            continue
        surface, surface_src = lookup_surface(head.competition, info["surface_hint"], surf_lookup)
        st = states[tour]
        ra_rec, rb_rec = st["players"][maps[True]["player_id"]], st["players"][maps[False]["player_id"]]
        ra, rb = surface_rating(ra_rec, surface), surface_rating(rb_rec, surface)
        p_elo_bo3 = elo_expected(ra, rb)
        # Elo is fitted on match outcomes across formats; translate to point probabilities on a bo3 basis, then
        # re-derive the match probability under the actual format (bo5 amplifies the favourite)
        spw = st["baselines"].get(f"{tour}|{surface}", None) or (0.64 if tour == "ATP" else 0.57)
        from tennis_edge.rules.formats import TOUR_SINGLES_BO3
        import math
        # structural serve/return probabilities
        base = math.log(spw / (1 - spw))
        sr_pa = 1 / (1 + math.exp(-(base + ra_rec["sr_s"] - rb_rec["sr_r"])))
        sr_pb = 1 - 1 / (1 + math.exp(-(base + rb_rec["sr_s"] - ra_rec["sr_r"])))
        p_sr_bo3 = match_win_prob(sr_pa, sr_pb, TOUR_SINGLES_BO3)
        p_sr = match_win_prob(sr_pa, sr_pb, fmt)
        # ENSEMBLE = logit average of Elo and structural on a bo3 basis (research/market_benchmark/RESULTS_SR_ATP.md:
        # the average beats either component walk-forward); it is the model fair value. Point probabilities are
        # inverted from the ensemble so every derivative market is priced from ONE coherent distribution.
        sr_ok = min(ra_rec["sr_points"], rb_rec["sr_points"]) >= 1000
        if sr_ok:
            z = 0.5 * math.log(p_elo_bo3 / (1 - p_elo_bo3)) + 0.5 * math.log(p_sr_bo3 / (1 - p_sr_bo3))
            p_ens_bo3 = 1 / (1 + math.exp(-z))
        else:
            p_ens_bo3 = p_elo_bo3   # no serve evidence: structural is prior-only, fall back to Elo
        pa, pb = point_probs_from_match_prob(p_ens_bo3, 2 * spw, TOUR_SINGLES_BO3)
        dist = match_distribution(pa, pb, fmt)
        p_elo_fmt = match_win_prob(*point_probs_from_match_prob(p_elo_bo3, 2 * spw, TOUR_SINGLES_BO3), fmt)
        days_a = (today - date.fromisoformat(ra_rec["last_date"][:10])).days if ra_rec.get("last_date") and ra_rec["last_date"] != "None" else None
        days_b = (today - date.fromisoformat(rb_rec["last_date"][:10])).days if rb_rec.get("last_date") and rb_rec["last_date"] != "None" else None
        q = data_quality(QualityInputs(ra_rec["n"], rb_rec["n"], ra_rec["sr_points"], rb_rec["sr_points"], days_a, days_b,
                                       1.0 if surface else 0.5, min(maps[True]["confidence"], maps[False]["confidence"]), True))
        prices = []; pm_by = {}
        for pm in pms:
            try:
                pr = price_market(pm, dist)
            except PricingError as e:
                coverage["pricing_error"] += 1; excluded.append({"ticker": pm.ticker, "stage": "pricing", "reason": str(e)}); continue
            prices.append(pr); pm_by[pm.ticker] = pm
        v = check_consistency(prices, pm_by)
        if v:
            consistency_violations += [f"{ev}: {x}" for x in v]
        for pr in prices:
            pm = pm_by[pr.ticker]; raw = parsed[pr.ticker][1]
            qrec = quotes.get(pr.ticker) or raw
            yes_bid, yes_ask, no_bid, no_ask = (fnum(qrec.get(k)) for k in ("yes_bid_dollars", "yes_ask_dollars", "no_bid_dollars", "no_ask_dollars"))
            quote_src = "capture" if pr.ticker in quotes else "discovery_record"
            sched = raw.get("occurrence_datetime") or raw.get("expected_expiration_time")
            fee = fee_types.get(pm.series_ticker, FeeSchedule())
            evs = expected_value(pr.fair_yes, yes_ask, no_ask, 100, fee)
            best = max(evs, key=lambda e: e.ev_per_contract_after_fees) if evs else None
            row = {"match_id": ev, "ticker": pr.ticker, "family": pr.family, "event_ticker": ev, "series_ticker": pm.series_ticker,
                   "player_a": names[True], "player_b": names[False], "player_a_id": maps[True]["player_id"], "player_b_id": maps[False]["player_id"],
                   "tour": tour, "level": info["level"], "competition": head.competition, "round": head.round, "format": fmt.name, "surface": surface, "surface_source": surface_src,
                   "subject": pm.subject, "line": pm.line, "set_index": pm.set_index, "exact_score": pm.exact_score,
                   "model_version": st["model_version"], "ratings_as_of": st["as_of_date"], "git_sha": sha, "feature_snapshot_id": f"ratings:{st.get('matches_sha256', '')[:12]}",
                   "data_source_versions": {"discovery": disc_summary["run_id"], "ratings_built_at": st["built_at"]},
                   "models": {"ELO": _orient(p_elo_fmt, pm) if pr.family == "MATCH_WINNER" else None,
                              "STRUCTURAL": _orient(p_sr, pm) if pr.family == "MATCH_WINNER" else None,
                              "ENSEMBLE": _orient(dist.p_match, pm) if pr.family == "MATCH_WINNER" else None,
                              "ELO_DP_FAIR": pr.fair_yes, "MARKET_MID": (0.5 * (yes_bid + yes_ask)) if (yes_bid and yes_ask) else None,
                              "HYBRID_MARKET_MODEL": None},
                   "inputs": {"elo_a": ra, "elo_b": rb, "pa": pa, "pb": pb, "sr_pa": sr_pa, "sr_pb": sr_pb, "spw_baseline": spw, "p_elo_bo3": p_elo_bo3, "p_sr_bo3": p_sr_bo3, "p_ensemble_bo3": p_ens_bo3, "structural_used": sr_ok},
                   "quality": q, "market_quote": {"yes_bid": yes_bid, "yes_ask": yes_ask, "no_bid": no_bid, "no_ask": no_ask, "source": quote_src, "quote_ts": qrec.get("captured_at") or disc_summary["started_at"],
                                                  "volume": qrec.get("volume_fp"), "open_interest": qrec.get("open_interest_fp"), "liquidity": qrec.get("liquidity_dollars")},
                   "scheduled_start": sched, "seconds_to_scheduled_start": _secs(sched),
                   "start_basis": "SCHEDULED" if info["level"] in ("GRAND_SLAM", "MASTERS_1000", "TOUR_500_250", "TOUR_FINALS", "OLYMPICS", "TEAM") else "NOMINAL_UNRELIABLE",
                   "ev": {"best_side": best.side if best else None, "price": best.price if best else None, "raw_edge": best.raw_edge if best else None,
                          "fee_per_contract": best.fee_per_contract if best else None, "ev_after_fees": best.ev_per_contract_after_fees if best else None,
                          "bet_up_to": breakeven_price(best.fair, fee) if best else None},
                   "notes": pr.notes, "conditional_yes": pr.conditional_yes, "p_played": pr.p_played,
                   "authority": "RESEARCH_ONLY_NO_REAL_MONEY"}
            projections.append(row); projected_tickers.append(pr.ticker)
            if ledger is not None:
                ledger.append(dict(row))
    mapper.save_cache()
    coverage["projected"] = len(projected_tickers)
    os.makedirs(a.out, exist_ok=True)
    out = {"run_id": run_id, "generated_at": datetime.now(timezone.utc).isoformat(), "discovery_run": disc_summary["run_id"], "git_sha": sha,
           "coverage": dict(coverage), "projected_tickers": projected_tickers, "consistency_violations": consistency_violations,
           "excluded": excluded, "projections": projections, "authority": "RESEARCH_ONLY_NO_REAL_MONEY"}
    json.dump(out, open(os.path.join(a.out, f"{run_id}.json"), "w"), indent=0, default=str)
    json.dump({k: v for k, v in out.items() if k != "projections"}, open(os.path.join(a.out, "latest.json"), "w"), indent=0, default=str)
    write_report(out, os.path.join(a.out, f"REPORT_{run_id}.md"))
    print(json.dumps({"run_id": run_id, "coverage": dict(coverage), "consistency_violations": len(consistency_violations)}, indent=1))
    return 0


def price_doubles_event(ev, pms, names, comp_ids, info, tour, states, mapper, today, quotes, parsed, fee_types, disc_summary, sha, ledger):
    """MATCH_WINNER only, DoublesBaseline on the four players' singles Elo (documented prior, unvalidated):
    quality grade capped at C, authority RESEARCH_ONLY, never actionable."""
    from tennis_edge.doubles.model import DoublesBaseline
    from tennis_edge.rules.formats import resolve_format, FormatResolutionError
    if not names.get(True) or not names.get(False):
        return {"ok": False, "reason": "doubles: could not recover both team names"}
    teams = {}
    for side in (True, False):
        parts = [x.strip() for x in names[side].split("/")]
        if len(parts) != 2:
            return {"ok": False, "reason": f"doubles: team name not a pair: {names[side]!r}"}
        ids = []
        for nm in parts:
            t_try = [tour] if tour in states else list(states)
            if tour == "MIXED":
                t_try = ["ATP", "WTA"]
            hit = None
            for tt in t_try:
                r = mapper.resolve(tt, nm, None, today)
                if r["status"] == "MAPPED":
                    hit = (tt, r["player_id"]); break
            if not hit:
                return {"ok": False, "reason": f"doubles: player {nm!r} unmapped/ambiguous in {t_try}"}
            ids.append(hit)
        teams[side] = ids
    singles = {pid: states[tt]["players"][pid]["elo"] for side in teams for tt, pid in teams[side]}
    model = DoublesBaseline(singles_elo=singles)
    pred = model.predict(tuple(pid for _, pid in teams[True]), tuple(pid for _, pid in teams[False]))
    try:
        fmt = resolve_format("ATP" if tour == "MIXED" else tour, info["level"], today.year, info["competition"] if info["level"] == "GRAND_SLAM" else None, "mixed" if tour == "MIXED" else "doubles")
    except FormatResolutionError as e:
        return {"ok": False, "reason": f"doubles format: {e}"}
    rows = []
    for pm in pms:
        if pm.family != "MATCH_WINNER":
            continue
        fair = pred["p_a"] if pm.subject_is_a else 1 - pred["p_a"]
        raw = parsed[pm.ticker][1]; qrec = quotes.get(pm.ticker) or raw
        yes_bid, yes_ask, no_bid, no_ask = (fnum(qrec.get(k)) for k in ("yes_bid_dollars", "yes_ask_dollars", "no_bid_dollars", "no_ask_dollars"))
        fee = fee_types.get(pm.series_ticker, FeeSchedule()); evs = expected_value(fair, yes_ask, no_ask, 100, fee)
        best = max(evs, key=lambda e: e.ev_per_contract_after_fees) if evs else None
        sched = raw.get("occurrence_datetime") or raw.get("expected_expiration_time")
        row = {"match_id": ev, "ticker": pm.ticker, "family": pm.family, "event_ticker": ev, "series_ticker": pm.series_ticker,
               "player_a": names[True], "player_b": names[False], "player_a_id": "|".join(pid for _, pid in teams[True]), "player_b_id": "|".join(pid for _, pid in teams[False]),
               "tour": tour, "level": info["level"], "competition": pm.competition, "round": pm.round, "format": fmt.name, "surface": None, "surface_source": "n/a",
               "subject": pm.subject, "line": None, "set_index": None, "exact_score": None, "model_version": "doubles_baseline_prior_v0", "ratings_as_of": min(states[t]["as_of_date"] for t in states),
               "git_sha": sha, "feature_snapshot_id": "doubles_prior", "data_source_versions": {"discovery": disc_summary["run_id"]},
               "models": {"ELO": None, "STRUCTURAL": None, "ENSEMBLE": None, "ELO_DP_FAIR": fair, "MARKET_MID": (0.5 * (yes_bid + yes_ask)) if (yes_bid and yes_ask) else None, "HYBRID_MARKET_MODEL": None, "DOUBLES_BASELINE": fair},
               "inputs": {"rating_a": pred["rating_a"], "rating_b": pred["rating_b"], "basis_a": pred["basis_a"], "basis_b": pred["basis_b"]},
               "quality": {"data_quality_score": 0.3, "grade": "C", "pillars": {"note": "doubles baseline prior; unvalidated"}},
               "market_quote": {"yes_bid": yes_bid, "yes_ask": yes_ask, "no_bid": no_bid, "no_ask": no_ask, "source": "capture" if pm.ticker in quotes else "discovery_record", "quote_ts": qrec.get("captured_at") or disc_summary["started_at"],
                                "volume": qrec.get("volume_fp"), "open_interest": qrec.get("open_interest_fp"), "liquidity": qrec.get("liquidity_dollars")},
               "scheduled_start": sched, "seconds_to_scheduled_start": _secs(sched),
               "ev": {"best_side": best.side if best else None, "price": best.price if best else None, "raw_edge": best.raw_edge if best else None, "fee_per_contract": best.fee_per_contract if best else None,
                      "ev_after_fees": best.ev_per_contract_after_fees if best else None, "bet_up_to": breakeven_price(best.fair, fee) if best else None},
               "notes": pred["note"], "conditional_yes": None, "p_played": None, "authority": "RESEARCH_ONLY_NO_REAL_MONEY"}
        rows.append(row)
        if ledger is not None:
            ledger.append(dict(row))
    return {"ok": True, "rows": rows}


def _orient(p_a, pm):
    return p_a if pm.subject_is_a else 1 - p_a


def _secs(sched):
    if not sched:
        return None
    try:
        return (datetime.fromisoformat(sched.replace("Z", "+00:00")) - datetime.now(timezone.utc)).total_seconds()
    except Exception:
        return None


def write_report(out, path):
    L = [f"# RUN TENNIS -- {out['run_id']}", "", "**Authority: RESEARCH ONLY. No real-money recommendations. Every line below is a hypothetical model-vs-quote comparison.**", "",
         f"Discovery snapshot: {out['discovery_run']} | git {out['git_sha'][:10]}", "", "## Coverage", "", "| stage | count |", "|---|---|"]
    for k, v in out["coverage"].items():
        L.append(f"| {k} | {v} |")
    L += ["", f"Consistency violations: {len(out['consistency_violations'])}", ""]
    rows = [r for r in out["projections"] if r["ev"]["ev_after_fees"] is not None]
    def actionable(r):
        mq = r["market_quote"]
        try:
            liq = float(mq.get("liquidity") or 0)
        except (TypeError, ValueError):
            liq = 0.0
        two_sided = mq.get("yes_bid") is not None and mq.get("yes_ask") is not None
        spread = (mq["yes_ask"] - mq["yes_bid"]) if two_sided else 1.0
        return two_sided and spread <= 0.10 and liq > 0 and r["quality"]["grade"] in ("A", "B") and r.get("start_basis") == "SCHEDULED" and (r.get("seconds_to_scheduled_start") or 0) > 900
    act = [r for r in rows if actionable(r)]; act.sort(key=lambda r: -(r["ev"]["ev_after_fees"] or -1))
    rows.sort(key=lambda r: -(r["ev"]["ev_after_fees"] or -1))
    L += ["## Actionability-filtered opportunities (two-sided quote, spread <= 10c, liquidity > 0, quality A/B)", "",
          f"{len(act)} of {len(rows)} priced markets pass the actionability filter. HYPOTHETICAL: no model has beaten the market benchmark; treat as research candidates, not bets.", "",
          "| match | market | side | price | fair | raw edge | EV after fees | bet up to | quality | why / risk |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in act[:25]:
        why = f"Elo {r['inputs']['elo_a']:.0f} vs {r['inputs']['elo_b']:.0f} ({r['surface'] or 'surface?'}); Elo p={r['models']['ELO']:.2f}, SR p={r['models']['STRUCTURAL']:.2f}, ens={r['models']['ENSEMBLE']:.2f}" if r["models"].get("STRUCTURAL") is not None else (f"DP from ensemble point probs pa={r['inputs']['pa']:.3f} pb={r['inputs']['pb']:.3f}" if 'pa' in r['inputs'] else f"doubles baseline {r['inputs'].get('rating_a', 0):.0f} vs {r['inputs'].get('rating_b', 0):.0f} (unvalidated prior)")
        risk = f"quote {r['market_quote']['source']} @ {r['market_quote']['quote_ts'][:16]}; liq {r['market_quote']['liquidity']}; grade {r['quality']['grade']}"
        fair = r['models']['ELO_DP_FAIR'] if r['ev']['best_side'] == 'YES' else 1 - r['models']['ELO_DP_FAIR']
        L.append(f"| {r['player_a']} vs {r['player_b']} ({r['competition']} {r['round']}) | {r['family']} {r['ticker']} | {r['ev']['best_side']} | {r['ev']['price']:.2f} | {fair:.3f} | {r['ev']['raw_edge']:+.3f} | {r['ev']['ev_after_fees']:+.3f} | {r['ev']['bet_up_to']:.2f} | {r['quality']['grade']} | {why} / {risk} |")
    L += ["", "## All priced markets by raw disagreement (unfiltered; most are illiquid or stale quotes -> PASS)", "",
          "| match | market | side | price | fair | raw edge | EV after fees | bet up to | quality | why / risk |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows[:40]:
        why = f"Elo {r['inputs']['elo_a']:.0f} vs {r['inputs']['elo_b']:.0f} ({r['surface'] or 'surface?'}); Elo p={r['models']['ELO']:.2f}, SR p={r['models']['STRUCTURAL']:.2f}, ens={r['models']['ENSEMBLE']:.2f}" if r["models"].get("STRUCTURAL") is not None else (f"DP from ensemble point probs pa={r['inputs']['pa']:.3f} pb={r['inputs']['pb']:.3f}" if 'pa' in r['inputs'] else f"doubles baseline {r['inputs'].get('rating_a', 0):.0f} vs {r['inputs'].get('rating_b', 0):.0f} (unvalidated prior)")
        risk = f"quote {r['market_quote']['source']}; liq {r['market_quote']['liquidity']}; grade {r['quality']['grade']}"
        L.append(f"| {r['player_a']} vs {r['player_b']} ({r['competition']} {r['round']}) | {r['family']} {r['ticker']} | {r['ev']['best_side']} | {r['ev']['price']:.2f} | {r['ev']['best_side'] == 'YES' and r['models']['ELO_DP_FAIR'] or 1 - r['models']['ELO_DP_FAIR']:.3f} | {r['ev']['raw_edge']:+.3f} | {r['ev']['ev_after_fees']:+.3f} | {r['ev']['bet_up_to']:.2f} | {r['quality']['grade']} | {why} / {risk} |")
    L += ["", "## Exclusions (first 60)", "", "| ticker | stage | reason |", "|---|---|---|"]
    for e in out["excluded"][:60]:
        L.append(f"| {e['ticker']} | {e['stage']} | {e['reason'][:120]} |")
    open(path, "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    sys.exit(main())
