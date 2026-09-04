#!/usr/bin/env python3
"""Build config/kalshi_nfl_series.json from a discovery run.

NFL membership rule: Kalshi's own series `tags` contains "Football" and the
ticker is not on the college/other exclusion list, OR the series ticker is in
an explicit include list. Every series gets a capture tier:

  FULL_MICROSTRUCTURE  quotes every run + order book + trade tape near kickoff
                       (single-game families: winner/spread/total/team total/props)
  LIGHT                quotes every run, no order book (season/futures with real liquidity)
  DAILY                one quote row per day (awards, coach markets, drafts, specials)
  NOT_CAPTURED         explicitly excluded with a reason (never silently)

The registry is REVIEWED CONFIG: discovery may propose additions (written to
`proposed_additions`) but capture only reads `series`. New series therefore
never vanish (they are captured at LIGHT tier as `unregistered`) and never
silently gain FULL tier without a human/agent looking at them.
"""
from __future__ import annotations
import argparse, json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.kalshi.classifier import SERIES_FAMILY, PERIOD_RE, NOT_NFL_PREFIXES, classify  # noqa

EXCLUDE_PREFIX = NOT_NFL_PREFIXES + ("KXFOOTBALL1001", "KXCFL", "KXUFL", "KXEPL", "KXCFB", "KXCFP", "KXGREYCUP", "KXNFLMENTION", "KXNFLCELEBRITYGAME",
                                     "KXNFLREDZONE", "KXNFLVIEW", "KXNFLREBOOT", "KXSORONDO", "KXBABYNAME", "KXRANKLIST", "KXDONATE", "KXCANIMAKETHIS",
                                     "KXEPLTEST", "KXALMVP", "KXNLMVP", "KXNHLMVP", "KXKXNCAAF", "KXCOACHOUTNCAAFB", "KXDEFHEISMAN", "KXCOLLEGE",
                                     "KXCONFREALIGNMENT", "KXNDJOINCONF", "KXSTARTNOTREDAME", "KXOLEMISS", "KXPAVIA", "KXCOACHOUTOLEMISS", "KXCOACHOUTUNC", "KXNEWCOACHUNC")
NFL_TITLE_RE = __import__("re").compile(r"(Pro Football|\bNFL\b|Super Bowl|Bears|Cowboys|Jaguars|Raiders|Patriots|Saints|Jets|Giants|Tyreek|McLaurin|Micah|Rodgers|Kelce|Rivers|Burrow|Tush Push)", __import__("re").I)
# college "Next Coach" series share the shape of NFL ones; only NFL teams are NFL
COLLEGE_COACH = ("KXARKCOACH", "KXAUBCOACH", "KXCALCOACH", "KXCCARCOACH", "KXCONNCOACH", "KXFLACOACH", "KXLSUCOACH", "KXMEMCOACH", "KXMICHCOACH",
                 "KXOKSTCOACH", "KXPSUCOACH", "KXSTANCOACH", "KXTENCOACH", "KXTULNCOACH", "KXUABCOACH", "KXUCLACOACH", "KXUKCOACH", "KXUNTCOACH",
                 "KXUSFCOACH", "KXVTCOACH", "KXCOORDANNOUNCE", "KXCOACHONDATE", "KX1HOMEGAME", "KX1STHOMEGAME", "KXSTADIUM")
FULL_FAMILIES = {"GAME_WINNER", "SPREAD", "TOTAL", "TEAM_TOTAL", "WIN_MARGIN_BUCKET", "PLAYER_STAT", "FIRST_TD_SCORER",
                 "FIRST_TD_TEAM", "TOTAL_TD", "PERIOD_WINNER", "HALF_FULL_RESULT", "BOTH_TEAMS_SCORE_N", "RACE_TO_N",
                 "BOTH_TEAMS_SCORE", "PERIOD_TD", "PLAYER_H2H", "TEAM_STAT", "GAME_STAT", "GAME_EVENT", "NEXT_TD_SCORER"}
LIGHT_FAMILIES = {"SEASON_WINS", "SEASON_WINS_EXACT", "SEASON_PLAYER_STAT", "SEASON_PLAYER_SPECIAL", "SEASON_LEADER", "SUPER_BOWL_WINNER",
                  "CONFERENCE_WINNER", "DIVISION_WINNER", "MAKE_PLAYOFFS", "TEAM_WINS_BY_WEEK", "WEEK_LEADER", "SEASON_FANTASY",
                  "SEASON_SEED", "SEASON_TEAM_EVENT", "SEASON_TEAM_H2H", "SEASON_DIVISION_STAT", "SEASON_TEAM_LEADER", "AWARD",
                  "PLAYER_AVAILABILITY", "PARLAY", "COMBO", "SEASON_MATCHUP", "SUPER_BOWL_MATCHUP", "WEEK_EVENT", "SEASON_DIVISION_ORDER"}


def family_of_series(ticker: str):
    fake = {"ticker": f"{ticker}-X-Y", "event_ticker": f"{ticker}-X", "series_ticker": ticker}
    return classify(fake).family


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--discovery-dir", required=True)
    ap.add_argument("--out", default=os.path.join(ROOT, "config", "kalshi_nfl_series.json"))
    a = ap.parse_args()
    series_all = json.load(open(os.path.join(a.discovery_dir, "series_all.json")))
    existing = json.load(open(a.out)) if os.path.exists(a.out) else {"series": {}}
    reg = {"generated_from": os.path.basename(a.discovery_dir.rstrip("/")), "series": dict(existing.get("series", {})), "proposed_additions": {}}
    counts = {}
    try:
        counts = {fn[:-5]: sum(v["n"] for v in json.load(open(os.path.join(a.discovery_dir, "markets", fn))).values())
                  for fn in os.listdir(os.path.join(a.discovery_dir, "markets"))}
    except FileNotFoundError:
        pass
    for s in series_all:
        t = s.get("ticker") or ""
        tags = s.get("tags") or []
        if t.startswith(EXCLUDE_PREFIX) or t in COLLEGE_COACH:
            continue
        is_nfl = t.startswith("KXNFL") or (("Football" in tags) and bool(NFL_TITLE_RE.search(s.get("title") or "")))
        is_nfl = is_nfl or t.startswith(("KXSB", "KXSUPERBOWL", "KXPERFORMSUPERBOWL", "KXHALFTIMESHOW", "KXFIRSTSUPERBOWLSONG", "KXLEADERNFL",
                                         "KXLEADERPINT", "KXNEXTTEAMNFL", "KXTRADEOFFNFL", "KXCOACHOUTNFL", "KXNEXTCOACHOUTNFL", "KXNEXTNFLCOACH",
                                         "KXWPMOTY", "KXSTARTINGQBWEEK1", "KXRECORDNFL", "KXTEAMSINSB", "KXNFCAFCSB", "KXTENNCOACH", "KXNYGCOACH",
                                         "KXATLCOACH", "KXSWIFTATTEND", "KXBRADY", "KXMCMADDEN", "KXESPYNFL", "KXRAINNOSB"))
        is_nfl = is_nfl and not t.startswith(("KXAFC", "KXNFC")) or t in ("KXAFC", "KXNFC")
        if not is_nfl:
            continue
        fam = family_of_series(t)
        if fam in FULL_FAMILIES:
            tier = "FULL_MICROSTRUCTURE"
        elif fam in LIGHT_FAMILIES:
            tier = "LIGHT"
        elif fam == "NOT_NFL":
            continue
        else:
            tier = "DAILY"
            if fam in ("NOT_NFL_OR_UNKNOWN", "UNKNOWN_NEEDS_CLASSIFICATION"):
                fam = "NFL_MISC_UNCLASSIFIED"
        rec = {"title": s.get("title"), "family": fam, "tier": tier, "tags": tags, "product_scope": (s.get("product_metadata") or {}).get("scope"),
               "fee_type": s.get("fee_type"), "fee_multiplier": s.get("fee_multiplier"), "markets_seen": counts.get(t, 0)}
        if t in reg["series"]:
            # keep reviewed tier, refresh metadata
            old = reg["series"][t]
            rec["tier"] = old.get("tier", tier)
            rec["reason"] = old.get("reason")
            reg["series"][t] = rec
        else:
            reg["series"][t] = rec if not existing.get("series") else None
            if existing.get("series"):
                reg["series"].pop(t)
                reg["proposed_additions"][t] = rec
    reg["series"] = dict(sorted(reg["series"].items()))
    json.dump(reg, open(a.out, "w"), indent=1)
    tiers = {}
    for t, r in reg["series"].items():
        tiers[r["tier"]] = tiers.get(r["tier"], 0) + 1
    print("registry:", len(reg["series"]), tiers, "proposed:", len(reg["proposed_additions"]))


if __name__ == "__main__":
    main()
