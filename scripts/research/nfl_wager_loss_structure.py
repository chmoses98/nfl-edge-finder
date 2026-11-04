#!/usr/bin/env python3
"""NFL wager profitability postmortem (research; aggregate output only).

    python3 scripts/research/nfl_wager_loss_structure.py \
        --handicap-root /tmp/hd --closes-root /tmp/md/data/shadow/v2/closes \
        --schedule-csv /tmp/md/data/kalshi/capture/schedule_cache.csv \
        [--shadow-obs-dir DIR]  [--workers 2]  --out-public docs/research/nfl_wager_loss_structure_2026-11-04.json

Reads the owner's imported wagers and settlements (handicap-data ledger), the published canonical closes, the nflverse schedule and results
table, and optionally filtered SHADOW-model ledger observations (JSON or .jsonl.gz files; see scripts/research/fetch_shadow_obs.py).
The public output holds counts, ratios, z-scores and intervals only: no ticker, order id, game code, player or dollar amount. Nothing here
feeds a stake, a card, a threshold or a model.
"""
from __future__ import annotations

import argparse
import csv
import glob
import gzip
import json
import os
import sys
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts", "handicap"))

import actual_wager_postmortem as AWP  # noqa: E402
from nfl_edge.handicap import schedule_kickoffs as SK  # noqa: E402
from nfl_edge.handicap import settlement_amendments as AM  # noqa: E402
from nfl_edge.handicap import store  # noqa: E402
from nfl_edge.handicap import wager_diagnostics as WD  # noqa: E402
from nfl_edge.research import wager_loss_structure as L  # noqa: E402
from nfl_edge.research import wager_selection_rules as WR  # noqa: E402

LADDER_PREFIXES = ("KXNFLSPREAD-", "KXNFLTOTAL-", "KXNFLTEAMTOTAL-", "KXNFLGAME-")
SERIES_LABEL = {"KXNFLSPREAD": "game spread", "KXNFLTOTAL": "game total", "KXNFLTEAMTOTAL": "team total", "KXNFLGAME": "moneyline"}
LADDER_KEEP = ("ticker", "mid", "no_mid", "yes_bid", "yes_ask", "no_bid", "no_ask", "price_observed_at", "minutes_before_kickoff",
               "close_status", "close_quality")


def _ticker_of(line: str):
    i = line.rfind('"ticker":"')
    return line[i + 10:line.find('"', i + 10)] if i >= 0 else None


def read_wager_closes(closes_root: str, tickers) -> list:
    """Canonical close rows for the wagered tickers (same fields and semantics as actual_wager_postmortem.read_closes, but the
    ticker is taken from the line instead of testing every wagered ticker as a substring of every line)."""
    want = {t for t in tickers if t}
    rows = []
    for path in sorted(glob.glob(os.path.join(closes_root, "2026_*", "*.closes_v2.jsonl.gz"))):
        with gzip.open(path, "rt", encoding="utf-8") as h:
            for line in h:
                if _ticker_of(line) in want:
                    row = json.loads(line)
                    rows.append({k: row.get(k) for k in AWP.KEEP})
    return rows


def read_ladder_game(gdir: str) -> tuple:
    """One game's full-game ladder: per ticker the CLOSE_OK row with the latest observed price (a re-evaluated game has several batches)."""
    out: dict = {}
    batches = 0
    for path in sorted(glob.glob(os.path.join(gdir, "*.closes_v2.jsonl.gz"))):
        batches += 1
        with gzip.open(path, "rt", encoding="utf-8") as h:
            for line in h:
                tk = _ticker_of(line)
                if not tk or not tk.startswith(LADDER_PREFIXES):
                    continue
                row = json.loads(line)
                if row.get("close_status") != "CLOSE_OK":
                    continue
                k = {x: row.get(x) for x in LADDER_KEEP}
                prev = out.get(tk)
                if prev is None or (k["price_observed_at"] or "") > (prev["price_observed_at"] or ""):
                    out[tk] = k
    return os.path.basename(gdir), {"batches": batches, "rows": list(out.values())}


def _ladder_worker(gdir):
    return read_ladder_game(gdir)


def read_ladder(closes_root: str, workers: int = 1) -> dict:
    dirs = sorted(glob.glob(os.path.join(closes_root, "2026_*")))
    if workers > 1:
        from multiprocessing import Pool
        with Pool(workers) as p:
            res = p.map(_ladder_worker, dirs)
    else:
        res = [read_ladder_game(d) for d in dirs]
    return dict(res)


def read_shadow_obs(path: str | None, tickers) -> dict:
    out: dict = defaultdict(list)
    if not path or not os.path.isdir(path):
        return out
    want = set(tickers)
    for f in sorted(glob.glob(os.path.join(path, "*"))):
        if f.endswith(".json"):
            with open(f, encoding="utf-8") as h:
                rows = json.load(h)
        elif f.endswith(".jsonl.gz"):
            with gzip.open(f, "rt", encoding="utf-8") as h:
                rows = [json.loads(x) for x in h]
        else:
            continue
        for o in rows:
            if o.get("ticker") in want:
                out[o["ticker"]].append({k: o.get(k) for k in ("feature_cutoff", "support_state", "model_event_probability", "mid", "family")})
    return out


def read_schedule(path: str) -> list:
    with open(path, encoding="utf-8") as h:
        return list(csv.DictReader(h))


def hist_games(sched_rows: list, before: int) -> list:
    out = []
    for r in sched_rows:
        try:
            if int(r["season"]) < before and r.get("result") not in ("", None) and r.get("spread_line") not in ("", None):
                out.append({"season": int(r["season"]), "result": float(r["result"]), "spread_line": float(r["spread_line"])})
        except (TypeError, ValueError):
            continue
    return out


def month_split(rows: list) -> dict:
    return {"weeks 1-4": L.roi_block([r for r in rows if r["week"] <= 4]), "weeks 5-8": L.roi_block([r for r in rows if r["week"] > 4])}


def build_report(doc: dict, sched_rows: list, ladder_raw: dict, obs: dict, *, season: int = 2026, n_boot: int = 4000) -> dict:
    eps = (doc.get("position_lifecycle") or {}).get("episodes") or []
    facts = [WD.episode_facts(e) for e in eps]
    for f in facts:                                         # series names never reach the public output
        if str(f["family"]).startswith("other ("):
            f["family"] = "other player market"
    games = L.load_games(sched_rows, season)
    rows = L.position_rows(facts, {e["position_episode_id"]: e for e in eps}, games)
    s = L.settled(rows)
    unresolved = sum(1 for r in rows if r["game_key"] and r["game_key"] not in games)

    # outcome check: scores vs the ledger's own settlements
    agree = tot = 0
    for r in s:
        if r["outcome"] is None or not r["game_key"]:
            continue
        pt = L.parse_ticker(r["ticker"])
        y = L.outcome_yes(pt["series"], pt, games.get(r["game_key"]))
        if y is not None:
            tot += 1
            agree += int((r["outcome"] if r["side"] == "YES" else 1 - r["outcome"]) == y)

    hist = hist_games(sched_rows, season)
    if len(hist) >= 500:
        margin_rep, model = L.holdout_margin_model(hist)
        full_model = L.fit_margin_model(hist)
    else:                                                    # not enough history to fit or validate a margin distribution
        margin_rep, model, full_model = {"state": "INSUFFICIENT_HISTORY", "games": len(hist)}, None, None
    ladder = L.ladder_rows(ladder_raw, games)
    spreads = [r for r in ladder if r["series"] == "KXNFLSPREAD"]
    near50 = lambda r: 0.4 <= r["mid"] <= 0.6                                        # noqa: E731

    mvl = L.market_vs_book(spreads, games, full_model) if full_model else []
    for r in mvl:
        r["bk"], r["bn"], r["bm"] = (r["p_book_key"] - r["y"]) ** 2, (r["p_book_normal"] - r["y"]) ** 2, (r["mid"] - r["y"]) ** 2
        r["d_key_vs_mid"], r["d_norm_vs_mid"], r["d_key_vs_norm"] = r["bk"] - r["bm"], r["bn"] - r["bm"], r["bk"] - r["bn"]
        r["gap_norm"], r["gap_key"] = r["p_book_normal"] - r["mid"], r["p_book_key"] - r["mid"]
    rung_g = lambda r: L.spread_rung_group(r["line"])                                # noqa: E731

    def book_vs_market(grp):
        return {"n": len(grp), **{k: L.boot_mean(grp, k) for k in ("bk", "bn", "bm", "d_key_vs_mid", "d_norm_vs_mid", "d_key_vs_norm",
                                                                   "gap_norm", "gap_key")}}
    kn = {"all spread rungs": book_vs_market(mvl)} if mvl else {}
    for g in sorted({rung_g(r) for r in mvl}):
        kn[g] = book_vs_market([r for r in mvl if rung_g(r) == g])

    # sportsbook-line reference for the owner's spread buys
    ob = L.owner_book_edge(rows, games, full_model) if full_model else {"n": 0}

    annotated = L.annotate_book_edge(rows, games, full_model) if full_model else 0

    # QB change flag (starter differs from that team's previous game)
    qb = L.qb_change_flags(games)
    qbrows = []
    for r in s:
        if r["series"] in ("KXNFLSPREAD", "KXNFLTEAMTOTAL", "KXNFLGAME") and r["game_key"] in games and r["team"]:
            qbrows.append(dict(r, qb_change=bool(qb.get((r["game_key"], r["team"])))))

    eligible = [r for r in s if r["series"] in L.LADDER_SERIES or r["player"]]
    matched = L.shadow_join(eligible, obs)

    rep = {
        "version": L.VERSION, "season": season,
        "data": {
            "orders": (doc.get("totals") or {}).get("wagers"), "settled_orders": (doc.get("totals") or {}).get("settled"),
            "independent_positions": len(rows), "settled_positions_with_established_pnl": len(s),
            "weeks": sorted({r["week"] for r in rows}), "unresolved_game_keys": unresolved,
            "games_with_a_position": len({r["game_key"] for r in s if r["game_key"]}),
            "derived_outcome_vs_settlement": {"compared": tot, "agree": agree},
            "ladder": {"games_with_published_closes": len(ladder_raw), "rungs_used": len(ladder), "games": len({r["game_key"] for r in ladder}),
                       "filters": "CLOSE_OK, two-sided, width <= 10c, close mid in [0.02, 0.98], outcome derivable from final scores"},
            "model_probability_recorded_with_owner_wagers": False,
            "provenance": "All fills are owner fills. No thesis, model probability, recommendation id or usage projection is recorded with any of them.",
        },
        "headline": {**L.roi_block(rows), "fair_price_null_held_positions": L.fair_block(rows),
                     "chronological_split": month_split(rows)},
        "clv_true_closes_price_only": L.clv_block(rows, n_boot=n_boot),
        "fee_inclusive_breakeven": {
            "by_entry_price": L.breakeven_block(rows, lambda r: WD._bucket(r["price"], WD.PRICE_BUCKETS)),
            "by_family_group": L.breakeven_block(rows, lambda r: ("game markets" if r["family"] in WR.GAME_MARKETS else
                                                                  "parlay" if r["family"] == WR.PARLAY else "player props / other"))},
        "by_week": L.cut(rows, lambda r: f"week {r['week']}"),
        "by_market_family": L.cut(rows, lambda r: r["family"]),
        "by_family_group": L.cut(rows, lambda r: ("game markets" if r["family"] in WR.GAME_MARKETS else
                                                  "parlay" if r["family"] == WR.PARLAY else "player props / other")),
        "by_entry_price": L.cut(rows, lambda r: WD._bucket(r["price"], WD.PRICE_BUCKETS)),
        "by_entry_timing": L.cut(rows, lambda r: ("live" if r["phase"] == "LIVE" else "parlay / unknown" if r["phase"] == "UNKNOWN" else
                                                  WD._bucket(r["minutes_before_kickoff"], WD.TIMING_BUCKETS))),
        "by_stake_size": L.cut(rows, lambda r: WD._bucket(r["units"], WD.STAKE_BUCKETS)),
        "spread": {
            "side": L.cut([r for r in rows if r["series"] == "KXNFLSPREAD"], lambda r: r["side"]),
            "rung": L.cut([r for r in rows if r["series"] == "KXNFLSPREAD"], lambda r: L.spread_rung_group(r["line"])),
            "chronological": L.cut([r for r in rows if r["series"] == "KXNFLSPREAD"], lambda r: "weeks 1-4" if r["week"] <= 4 else "weeks 5-8"),
            "rung_concentration": L.rung_concentration(rows, ladder),
            "owner_vs_sportsbook_closing_line": ob,
        },
        "totals_and_team_totals": L.cut([r for r in rows if r["series"] in ("KXNFLTOTAL", "KXNFLTEAMTOTAL")],
                                        lambda r: ("team total" if r["series"] == "KXNFLTEAMTOTAL" else "game total", r["side"])),
        "key_numbers": {
            "historical_margin_model_holdout": margin_rep,
            "kalshi_spread_ladder_vs_sportsbook_line": kn,
            "ladder_calibration_by_rung_group": L.ladder_calibration(spreads, rung_g),
        },
        "ladder_market_wide": {
            "by_series": L.ladder_calibration([r for r in ladder if r["series"] != "KXNFLGAME"], lambda r: SERIES_LABEL.get(r["series"], "other")),
            "moneyline_note": "moneyline rungs come in complementary pairs (the two teams' mids sum to 1), so mean(outcome - mid) is zero by construction; excluded",
            "spread_yes_side_near_50c": L.ladder_calibration([r for r in spreads if near50(r)], lambda r: "all"),
            "spread_near_50c_by_period": L.ladder_calibration([r for r in spreads if near50(r)],
                                                              lambda r: "weeks 1-4" if r["week"] <= 4 else "weeks 5-8"),
            "team_total_near_50c": L.ladder_calibration([r for r in ladder if r["series"] == "KXNFLTEAMTOTAL" and near50(r)], lambda r: "all"),
            "game_total_near_50c": L.ladder_calibration([r for r in ladder if r["series"] == "KXNFLTOTAL" and near50(r)], lambda r: "all"),
            "scope": "every published-close rung of every game with published closes, not only what the owner traded; taker ask, approximate fee",
        },
        "selection_vs_structure": {
            "all_full_game_markets": L.selection_vs_structure(rows, ladder),
            "spread": L.selection_vs_structure([r for r in rows if r["series"] == "KXNFLSPREAD"], ladder),
            "team_total": L.selection_vs_structure([r for r in rows if r["series"] == "KXNFLTEAMTOTAL"], ladder),
        },
        "shadow_model_join": L.shadow_block(matched, len(eligible)),
        "correlated_exposure": {"game_axis": L.game_axis_exposure(rows), "concentration": L.concentration_block(rows)},
        "qb_change": {"flagged_team_games_2026": sum(qb.values()),
                      "positions_on_a_team_whose_qb_changed": L.cut(qbrows, lambda r: "QB changed" if r["qb_change"] else "same QB")},
        "selection_rules_replay": L.rule_replay(rows, WR.RULES, n_boot=n_boot),
        "spread_positions_with_book_edge": annotated,
        "redaction": "counts, ratios, z-scores and intervals only; no ticker, order id, game code, player or dollar figure",
    }
    return rep


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--handicap-root", required=True)
    ap.add_argument("--closes-root", required=True)
    ap.add_argument("--schedule-csv", required=True)
    ap.add_argument("--shadow-obs-dir", default=None)
    ap.add_argument("--season", type=int, default=2026)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--n-boot", type=int, default=4000)
    ap.add_argument("--doc-cache", default=None, help="private path: cache the rebuilt lifecycle document (contains dollars and tickers; never commit)")
    ap.add_argument("--ladder-cache", default=None, help="private path: cache the extracted ladder")
    ap.add_argument("--out-public", required=True)
    a = ap.parse_args(argv)

    sched_rows = read_schedule(a.schedule_csv)
    if a.doc_cache and os.path.exists(a.doc_cache):
        with open(a.doc_cache, encoding="utf-8") as h:
            doc = json.load(h)
    else:
        wagers = store.read_kind(a.handicap_root, "imported_wagers", season=a.season)
        settlements = store.read_kind(a.handicap_root, "wager_settlements", season=a.season)
        closes = read_wager_closes(a.closes_root, [w.get("market_ticker") for w in wagers])
        with open(a.schedule_csv, encoding="utf-8") as h:
            sched = SK.kickoffs_from_schedule(h.read(), a.season)
        doc = AWP.build(wagers, settlements, closes, season=a.season, amendments=AM.read_amendments(a.handicap_root),
                        quote_at=None, schedule_kickoffs=sched)
        if a.doc_cache:
            with open(a.doc_cache, "w", encoding="utf-8") as h:
                json.dump(doc, h, default=str)
    if a.ladder_cache and os.path.exists(a.ladder_cache):
        with open(a.ladder_cache, encoding="utf-8") as h:
            ladder_raw = json.load(h)
    else:
        ladder_raw = read_ladder(a.closes_root, a.workers)
        if a.ladder_cache:
            with open(a.ladder_cache, "w", encoding="utf-8") as h:
                json.dump(ladder_raw, h)
    tickers = [e.get("market_ticker") for e in (doc.get("position_lifecycle") or {}).get("episodes") or []]
    obs = read_shadow_obs(a.shadow_obs_dir, tickers)
    rep = build_report(doc, sched_rows, ladder_raw, obs, season=a.season, n_boot=a.n_boot)
    text = json.dumps(rep, indent=1, sort_keys=True, default=str)
    if "KX" in text:
        print("refusing to write: a ticker-like string reached the public output", file=sys.stderr)
        return 3
    os.makedirs(os.path.dirname(os.path.abspath(a.out_public)), exist_ok=True)
    with open(a.out_public, "w") as h:
        h.write(text + "\n")
    h = rep["headline"]
    print(f"positions {rep['data']['independent_positions']}, roi {h['roi']} [{h['roi_lo95']}, {h['roi_hi95']}], "
          f"games {h['games']}, true-close coverage {rep['clv_true_closes_price_only']['coverage']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
