"""RESEARCH ONLY. Pull the five owner-traded ATL@GB contracts out of the four archived horizon packets
(Actions artifacts run-nfl-2026-w03-{35937741435,36040075511,36069483473,36074571204}) into one JSON.
Usage: python extract_traded_markets.py <dir containing t24/ t6/ t90/ t30/ unzipped artifacts> <out.json>"""
import json, os, sys

TICKERS = ["KXNFLPASSYDS-26SEP24ATLGB-GBJLOVE10-275", "KXNFLRSHYDS-26SEP24ATLGB-GBKJOHNSON26-30",
           "KXNFLRECYDS-26SEP24ATLGB-ATLDLONDON5-60", "KXNFL1HTEAMTOTAL-26SEP24ATLGB-ATL10", "KXNFLGAME-26SEP24ATLGB-GB"]
HZ = {"T-24h": "t24", "T-6h": "t6", "T-90m": "t90", "T-30m": "t30"}


def pick(m):
    sim = m.get("simulation") or {}
    v2 = m.get("shadow_v2") or {}
    oa = v2.get("other_arms") or {}
    return {"mid": m.get("mid"), "yes_bid": m.get("yes_bid"), "yes_ask": m.get("yes_ask"),
            "support_state": m.get("support_state"), "support_reason": m.get("support_reason"),
            "legacy_incumbent_p": m.get("model_probability"), "p_plays": m.get("p_plays"),
            "sim_p_football": sim.get("p_football"), "sim_p_reconciled": sim.get("p_reconciled"),
            "sim_support": sim.get("support_state"), "sim_football_mean": sim.get("football_mean"),
            "sim_market_mean": sim.get("market_mean"), "sim_football_p50": sim.get("football_p50"),
            "v2_primary_arm": v2.get("primary_arm"), "v2_primary_p": v2.get("p_yes"), "v2_support": v2.get("support_state"),
            "v2_arms": {k: (a.get("p_yes"), a.get("state"), bool(a.get("market_derived"))) for k, a in oa.items()},
            "movement_first_observed": ((m.get("movement") or {}).get("first_observed") or {}).get("mid")}


def main(d, out):
    res = {}
    for h, sub in HZ.items():
        p = json.load(open(os.path.join(d, sub, "packet.json")))
        g = [x for x in p["games"] if x["game_id"] == "2026_03_ATL_GB"][0]
        ms = {m["ticker"]: m for m in g["markets"]}
        for t in TICKERS:
            res.setdefault(t, {})[h] = pick(ms[t]) if t in ms else {"status": "NOT_LISTED_IN_PACKET"}
    json.dump(res, open(out, "w"), indent=1)
    for t, hs in res.items():
        print(t)
        for h, r in hs.items():
            print(f"  {h}: mid={r.get('mid')} legacy={r.get('legacy_incumbent_p') and round(r['legacy_incumbent_p'],3)} "
                  f"sim_fb={r.get('sim_p_football')} sim_rec={r.get('sim_p_reconciled') and round(r['sim_p_reconciled'],3)} "
                  f"v2[{r.get('v2_primary_arm')}]={r.get('v2_primary_p') and round(r['v2_primary_p'],3)} "
                  f"arms={ {k:(v[0] and round(v[0],3), v[1][:12]) for k,v in (r.get('v2_arms') or {}).items()} } "
                  f"fbmean={r.get('sim_football_mean')} mktmean={r.get('sim_market_mean')} sup={r.get('support_state')}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
