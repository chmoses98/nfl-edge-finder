"""A small synthetic world for the RUN NFL card tests: a schedule history, a one-game packet, its analysis shard, a manifest."""
import csv
import io
import json
import os
from datetime import datetime, timedelta, timezone

import numpy as np

from nfl_edge.handicap import fairvalue as FV

AS_OF = datetime(2026, 10, 25, 9, 0, tzinfo=timezone.utc)
GAME = "2026_07_AAA_BBB"
KICK = AS_OF + timedelta(hours=4)
CENTER = (-3.0, 44.5)             # home (BBB) margin, total: BBB is a 3-point underdog


def schedule_text(n_seasons=10, per=200, seed=3):
    rng = np.random.default_rng(seed)
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["game_id", "season", "game_type", "week", "gameday", "gametime", "away_team", "home_team", "result", "spread_line", "total", "total_line", "overtime",
                "home_rest", "away_rest"])
    for s in range(2016, 2016 + n_seasons):
        for i in range(per):
            spread = float(rng.choice([-7, -3.5, -3, -1.5, 0, 1, 2.5, 3, 3.5, 7]))
            tl = float(rng.choice([41.5, 44, 45.5, 47, 49.5]))
            res = int(round(spread + rng.normal(0, 13)))
            tot = int(round(tl + rng.normal(0, 10)))
            w.writerow([f"{s}_{i:03d}", s, "REG", 1 + i % 18, f"{s}-09-10", "13:00", "XXX", "YYY", res, spread, tot, tl, int(rng.random() < 0.06), 7, 7])
    w.writerow([GAME, 2026, "REG", 7, "2026-10-25", "13:00", "AAA", "BBB", "", CENTER[0] * -1, "", CENTER[1], "", 7, 10])
    return out.getvalue()


def _row(ticker, fam, subject, thr, p, per="FULL", stat=None, meaning="", width=0.02):
    ask = min(0.99, round(p + width / 2, 2))
    bid = max(0.01, round(p - width / 2, 2))
    return {"ticker": ticker, "family": fam, "subject": subject, "subject_kind": "team", "threshold": thr, "operator": ">", "period": per, "stat": stat,
            "yes_bid": bid, "yes_ask": ask, "no_bid": round(1 - ask, 2), "no_ask": round(1 - bid, 2), "mid": round(p, 3), "width": round(ask - bid, 3), "executable": True,
            "no_real_market": False, "volume": 5000.0, "open_interest": 5000.0, "minutes_since_price_change": 3.0, "yes_meaning": meaning,
            "analysis_state": "MODEL_PRICED", "incumbent": {"support_state": "UNSUPPORTED_MODEL", "model_probability": None}}


def build_run(tmp_path, *, cap_age_min=5.0, kick=KICK, invariants_ok=True, player=False):
    """Writes packet.json + analysis/manifest.json + analysis/games/<id>.json under tmp_path and returns the loaded run."""
    bank, _ = FV.bank_from_schedule(schedule_text(), 2026)
    gs = FV.GameSim(bank, "BBB", "AAA", CENTER[0], CENTER[1])
    sim = gs.draw(0, 0)
    rows = []
    for k in range(-14, 15):
        thr = k + 0.5
        p = float(np.mean(sim["margin"] > thr))
        if 0.04 < p < 0.96:
            rows.append(_row(f"KXNFLSPREAD-26OCT25AAABBB-BBB{k}", "SPREAD", "BBB", thr, p, stat="margin", meaning=f"YES iff BBB margin (FULL) > {thr}"))
            rows.append(_row(f"KXNFLSPREAD-26OCT25AAABBB-AAA{-k}", "SPREAD", "AAA", -thr, 1 - float(np.mean(sim["margin"] > thr)) - 0.0 if False else float(np.mean(-sim["margin"] > -thr)),
                             stat="margin", meaning=f"YES iff AAA margin (FULL) > {-thr}"))
    for t in range(36, 54):
        p = float(np.mean(sim["total"] >= t))
        if 0.05 < p < 0.95:
            rows.append(_row(f"KXNFLTOTAL-26OCT25AAABBB-{t}", "TOTAL", None, float(t), p, stat="total_points", meaning=f"YES iff total_points (FULL) >= {t}.0"))
    rows.append(_row("KXNFLGAME-26OCT25AAABBB-BBB", "GAME_WINNER", "BBB", None, float(np.mean(sim["margin"] > 0)), meaning="YES iff team margin > 0 (FULL) [subject: BBB]", width=0.02))
    rows.append(_row("KXNFLGAME-26OCT25AAABBB-AAA", "GAME_WINNER", "AAA", None, float(np.mean(sim["margin"] < 0)), meaning="YES iff team margin > 0 (FULL) [subject: AAA]", width=0.02))
    rows.append(_row("KXNFL1HSPREAD-26OCT25AAABBB-AAA3", "SPREAD", "AAA", 2.5, 0.5, per="1H", stat="margin", meaning="YES iff AAA margin (1H) > 2.5"))
    if player:
        r = _row("KXNFLRECYDS-26OCT25AAABBB-AAAWR1-60", "PLAYER_STAT", "A Receiver", 60.0, 0.5, stat="receiving_yards", meaning="YES iff A Receiver receiving_yards (FULL) >= 60.0")
        rows.append(r)
    cap = AS_OF - timedelta(minutes=cap_age_min)
    markets = [{"ticker": r["ticker"], "movement": {"total_move_since_first_capture": 0.0}, "book_depth_yes": 500000.0, "book_depth_no": 500000.0} for r in rows]
    game = {"game_id": GAME, "season": 2026, "week": 7, "kickoff_utc": kick.isoformat(), "home_team": "BBB", "away_team": "AAA", "venue": "X", "roof": "dome", "surface": "turf",
            "neutral_site": False, "data_freshness": {"ledger_feature_cutoff": cap.isoformat(), "context_capture": "c1", "packet_built_at": cap.isoformat()},
            "market_implied": {"implied_home_margin_median": CENTER[0], "implied_total_median": CENTER[1], "win_probability": {"AAA": 0.6, "BBB": 0.4}},
            "model_view": {"model_spread": 3.0}, "team_profiles": {}, "quarterbacks": {}, "offensive_line": {}, "injuries": {"records": [], "summary": {}},
            "weather": {"material": False}, "simulation": {"center": {"spread_home": CENTER[0], "total": CENTER[1]}}, "markets": markets,
            "game_script_inputs": {}, "game_script_v2": {"primary_scripts": []}, "coverage": {"totals": {"executable": len(rows)}}, "key_questions": []}
    packet = {"schema_version": "1", "handicap_run_id": "r1", "built_at": cap.isoformat(), "season": 2026, "week": 7, "packet_sha": "sha-test", "games": [game],
              "production_eligibility": {"families": {}}, "real_money_status": "NOT VALIDATED"}
    manifest = {"invariants": {"rows_total_equals_packet_markets_listed": invariants_ok, "no_duplicate_tickers": True, "zero_silently_omitted": True},
                "counts": {"rows_total": len(rows)}, "coverage_matrix": {"totals": {"silently_omitted": 0}}}
    os.makedirs(os.path.join(tmp_path, "analysis", "games"), exist_ok=True)
    json.dump(packet, open(os.path.join(tmp_path, "packet.json"), "w"))
    json.dump(manifest, open(os.path.join(tmp_path, "analysis", "manifest.json"), "w"))
    json.dump({"game_id": GAME, "home_team": "BBB", "away_team": "AAA", "rows": rows}, open(os.path.join(tmp_path, "analysis", "games", f"{GAME}.json"), "w"))
    from nfl_edge.handicap import card as C
    return C.load_reports(str(tmp_path))


def thesis(shift_margin=(2.0, 4.0), shift_total=(-0.5, 0.5), **kw):
    t = {"thesis_id": f"{GAME}::T1", "game_id": GAME, "statement": "BBB is better than the market has it.", "drivers": ["BBB_SIDE"],
         "shift": {"home_margin": list(shift_margin), "total": list(shift_total)},
         "evidence": {"measured": [{"claim": "adjusted pass offence +0.10", "opponent_adjusted": True, "market_unmoved": False}], "simulation": [], "hypotheses": []},
         "challenge": {"fail_modes": ["a", "b"], "market_already_priced": "the price has not moved", "matchup_check": "adjusted ratings, 6 games", "uncertainties": ["range"]}}
    t.update(kw)
    return t
