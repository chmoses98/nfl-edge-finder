"""RESEARCH ONLY / RETROSPECTIVE. Re-derive the DATA_ONLY (data_only-1.0.0) centre for 2026_03_ATL_GB at the
T-30m capture from public nflverse files re-downloaded on 2026-09-26, through the unmodified production code
(nfl_edge.arms.data_only), then run COUNTERFACTUAL rating inputs to quantify how much of the centre comes from
ATL's 2026 offensive games played under a different starting QB. Nothing here is fed back into any model.

Point-in-time: the same final_game_ids_before(cutoff) rule as the snapshot, so the Week-3 game itself (present in
today's play-by-play file) is excluded exactly as it was at the capture.

Usage: python reproduce_data_only.py <repo_root_with_data/raw/nflverse> <out.json>
"""
import json, os, sys
from datetime import datetime

import polars as pl

from nfl_edge.arms import data_only as DO
from nfl_edge.data import silver as SV

CUTOFF = datetime.fromisoformat("2026-09-24T23:45:09.567920+00:00")   # T-30m market observation
GAME, HOME, AWAY = "2026_03_ATL_GB", "GB", "ATL"
RECORDED = {"margin": 7.135009442584407, "total": 42.90451514658339}


def main(root, out):
    hist = pl.concat([SV.team_game_from_pbp(s) for s in (2023, 2024, 2025)], how="diagonal_relaxed")
    cur = SV.team_game_from_pbp(2026)
    games = SV.load_games()
    rows = DO.prepare_team_games(hist, cur)
    art = DO.DataOnlyArtifact.load(os.path.join(root, "research", "three_arm", "data_only_artifact_2026.json"))
    allowed, cmeta = DO.final_game_ids_before(games, CUTOFF)
    mf, _ = DO.market_free_schedule(games)
    srow = [r for r in mf.to_dicts() if r["game_id"] == GAME][0]

    def run(label, rws, allowed_ids):
        ratings, meta = DO.ratings_at_cutoff(rws, 2026, allowed_ids)
        pj = DO.project_game(art, ratings, srow, HOME, AWAY)
        keep = {t: {k: round(v, 5) for k, v in ratings[t].items()} for t in (HOME, AWAY)}
        return {"label": label, "margin": pj["projected_home_margin"], "total": pj["projected_total"],
                "n_team_games": meta["n_team_games"], "ratings": keep}

    atl26 = [g for g in cur.filter(pl.col("team") == "ATL")["game_id"].to_list()]
    res = {"cutoff": CUTOFF.isoformat(), "cutoff_meta": cmeta, "recorded_at_T30": RECORDED,
           "atl_2026_games_in_ratings": sorted(g for g in atl26 if g in allowed)}
    res["reproduction"] = run("as-recorded inputs (re-downloaded)", rows, allowed)
    # CF1: drop ATL's 2026 OFFENSIVE team-game rows only (the Rush/Strand QB regime); keep ATL defence and all
    # opponents' rows. prepare_rows keys offence by `team`, so dropping team==ATL & season==2026 removes ATL's
    # offensive observations AND its defensive ones in the same row; to isolate offence we null the off_ metrics.
    off_cols = [c for c in rows.columns if c.startswith("off_")]
    mask = (pl.col("team") == "ATL") & (pl.col("season") == 2026)
    rows_cf1 = rows.with_columns([pl.when(mask).then(None).otherwise(pl.col(c)).alias(c) for c in off_cols])
    res["cf_drop_atl_2026_offence"] = run("ATL 2026 offensive metrics removed (prior-season carry only)", rows_cf1, allowed)
    # CF2: drop every 2026 row involving ATL (ATL offence rows AND opponents' rows vs ATL, i.e. ATL defence)
    rows_cf2 = rows.filter(~(((pl.col("team") == "ATL") | (pl.col("opp") == "ATL")) & (pl.col("season") == 2026)))
    res["cf_drop_atl_2026_all"] = run("all 2026 rows involving ATL removed (offence, defence, special teams)", rows_cf2, allowed)
    # CF3: preseason-only ratings (no 2026 games at all) -- the week-0 view
    allowed_pre = {g for g in allowed if not str(g).startswith("2026_")}
    res["cf_no_2026_games"] = run("no 2026 games (prior seasons x0.4 carry)", rows, allowed_pre)
    json.dump(res, open(out, "w"), indent=1, default=str)
    for k in ("reproduction", "cf_drop_atl_2026_offence", "cf_drop_atl_2026_all", "cf_no_2026_games"):
        print(k, round(res[k]["margin"], 3), round(res[k]["total"], 3), res[k]["n_team_games"])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])


def rating_split(cf_path, art_path, out_path):
    """Split the margin contribution of each metric into the four team-rating components:
    d_f = GB_off + ATL_def - ATL_off - GB_def, contribution = beta/xs * component. Exact (linear)."""
    d = json.load(open(cf_path)); art = json.load(open(art_path))
    mm = art["margin_model"]; feats = art["margin_features"]
    out = {}
    for k in ("reproduction", "cf_drop_atl_2026_offence"):
        R_ = d[k]["ratings"]; tab = {}
        for f, b, s in zip(feats, mm["beta"], mm["xs"]):
            if not f.startswith("d_"):
                continue
            m = f[2:]; c = b / s
            tab[m] = {"GB_off": c * R_["GB"][f"off_{m}"], "ATL_def": c * R_["ATL"][f"def_{m}"],
                      "ATL_off": -c * R_["ATL"][f"off_{m}"], "GB_def": -c * R_["GB"][f"def_{m}"]}
        tot = {side: sum(v[side] for v in tab.values()) for side in ("GB_off", "ATL_def", "ATL_off", "GB_def")}
        out[k] = {"by_metric": tab, "by_side": tot}
    json.dump(out, open(out_path, "w"), indent=1)
    return out


def sra_diagnostic(root, out_path, weights=(1.0, 0.5, 0.25, 0.0)):
    """RETROSPECTIVE / GENERATION EVIDENCE ONLY. DATA_ONLY_SRA (starter-regime-0.1.0) on ATL@GB at the T-30m cutoff
    for a grid of w_regime values. Projected starters are the QBs the pregame evidence named at the cutoff
    (ESPN 2026-09-21T20:39Z: Penix named ATL starter; Sleeper chart QB1 Penix, no designation from 2026-09-23T11:49Z;
    GB: Love, chart QB1, no designation). Only ATL and GB receive a projected starter here; every other team is
    unadjusted (no projection supplied) -- recorded. Nothing in this grid may select w_regime."""
    from nfl_edge.research import starter_regime as SR
    hist = pl.concat([SV.team_game_from_pbp(s) for s in (2023, 2024, 2025)], how="diagonal_relaxed")
    cur = SV.team_game_from_pbp(2026)
    games = SV.load_games()
    rows = DO.prepare_team_games(hist, cur)
    art = DO.DataOnlyArtifact.load(os.path.join(root, "research", "three_arm", "data_only_artifact_2026.json"))
    allowed, _ = DO.final_game_ids_before(games, CUTOFF)
    pbp = pl.concat([pl.read_parquet(os.path.join(root, "data", "raw", "nflverse", "pbp", f"play_by_play_{s}.parquet"),
                                     columns=["game_id", "posteam", "qb_dropback", "passer_player_id", "passer_player_name", "season"])
                     for s in (2023, 2024, 2025, 2026)], how="diagonal_relaxed")
    starters = SR.starters_from_pbp(pbp, allowed)
    ids = {n: pbp.filter(pl.col("passer_player_name") == n)["passer_player_id"].drop_nulls().unique().to_list()
           for n in ("M.Penix", "J.Love")}
    proj = {"ATL": ids["M.Penix"][0], "GB": ids["J.Love"][0]}
    mf, _ = DO.market_free_schedule(games)
    srow = [r for r in mf.to_dicts() if r["game_id"] == GAME][0]
    res = {"model_id": SR.MODEL_ID, "version": SR.VERSION, "authority": SR.AUTHORITY,
           "evidence_class": "RETROSPECTIVE_GENERATION_DIAGNOSTIC_NOT_VALIDATION", "projected_starters": proj,
           "grid": []}
    for w in weights:
        allowed_prior = {g for g in allowed}
        rows_prior = rows.filter(pl.col("game_id").is_in(list(allowed_prior)) & (pl.col("season") >= 2026 - DO.RATING_SEASONS_BACK))
        ratings, meta = SR.ratings_at_cutoff_sra(rows_prior, 2026, allowed_prior, starters, proj, w,
                                                 DO.RATING_METRICS, DO.RATING_HYPERPARAMS)
        pj = DO.project_game(art, ratings, srow, HOME, AWAY)
        dw = meta["audit"]["downweighted"]
        res["grid"].append({"w_regime": w, "margin": pj["projected_home_margin"], "total": pj["projected_total"],
                            "atl_rows_downweighted": sorted(dw.get("ATL", [])), "gb_rows_downweighted": sorted(dw.get("GB", []))})
        print("w", w, round(pj["projected_home_margin"], 3), round(pj["projected_total"], 3),
              "ATL dw", len(dw.get("ATL", [])), "GB dw", len(dw.get("GB", [])))
    json.dump(res, open(out_path, "w"), indent=1)
    return res
