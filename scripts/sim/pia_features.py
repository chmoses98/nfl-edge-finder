"""Historical Personnel Intelligence Championship (RESEARCH_ONLY): point-in-time QB-quality and personnel feature table.

One chronological pass per table; every value for a team-game uses only information from strictly earlier games, plus
(a) the starting-QB identity that games.csv carries (public about 90 minutes before kickoff, the closing-line horizon) and
(b) the CERTIFIED final weekly injury report (nfl_edge.availability_pit.loaders.injuries_certified: row-level date_modified
before kickoff - 90 min; REG seasons 2010-2024).  Healthy scratches / the game-day inactive list are NOT used (the repo's own
certification rejects weekly_rosters INA as a pregame source).
League constants are frozen from seasons <= 2012, which precede every evaluated season.
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd
import polars as pl
from nfl_edge.sim import data as D
from nfl_edge.availability_pit import loaders as L
from scripts.sim import gsdl_features as GF

ROOT = D.ROOT
CACHE = os.path.join(ROOT, "data", "cache", "pia")
DECAY_QB, CARRY_QB, K_DB = 0.5 ** (1 / 16.0), 0.7, 150.0
DECAY_T, CARRY_T = 0.5 ** (1 / 8.0), 0.5
GROUPS = {"OL": (["T", "G", "C", "OL"], 5, "off"), "WR": (["WR"], 3, "off"), "TE": (["TE"], 1, "off"), "RB": (["RB", "FB"], 1, "off"),
          "DL": (["DE", "DT", "NT", "DL"], 4, "def"), "LB": (["LB", "ILB", "OLB", "MLB"], 3, "def"), "CB": (["CB"], 3, "def"), "S": (["FS", "SS", "S", "SAF", "DB"], 2, "def")}
ABSENT_P = {"Out": 1.0, "Doubtful": 0.9, "Questionable": 0.25}      # fixed a-priori constants, not fitted
MIN_PCT, WINDOW, MIN_SEASON_GAMES = 0.35, 8, 3


def _qb_pbp(season: int) -> pd.DataFrame:
    path = os.path.join(D.RAW, "pbp", f"play_by_play_{season}.parquet")
    d = pl.read_parquet(path, columns=["game_id", "posteam", "qb_dropback", "epa", "passer_player_id", "sack", "qb_hit", "season_type"])
    d = d.filter(pl.col("posteam").is_not_null() & (pl.col("qb_dropback").fill_null(0) == 1) & pl.col("passer_player_id").is_not_null()
                 & pl.col("season_type").is_in(["REG", "POST"]))
    d = d.with_columns(pl.col("posteam").replace(D.TEAM_FIX).alias("team"))
    return (d.group_by(["game_id", "team", "passer_player_id"]).agg([pl.len().alias("db"), pl.col("epa").sum().alias("epa"),
            (pl.col("sack").fill_null(0) == 1).sum().alias("sacks")]).to_pandas())


def qb_table(seasons, q=None) -> pd.DataFrame:
    """(game_id, team) -> starter-quality features from strictly earlier games.  ``q`` (tests only) overrides the pbp table."""
    os.makedirs(CACHE, exist_ok=True); path = os.path.join(CACHE, f"qb_{min(seasons)}_{max(seasons)}.parquet")
    override = q is not None
    if os.path.exists(path) and not override:
        return pd.read_parquet(path)
    q = pd.concat([_qb_pbp(s) for s in seasons], ignore_index=True) if q is None else q
    sch = GF.schedule_frame(); sch = sch[sch.season.isin(seasons) & sch.game_type.isin(["REG", "WC", "DIV", "CON", "SB"])].sort_values(["season", "week", "gameday", "game_id"])
    p_qb = q.loc[q.game_id.str[:4].astype(int) <= 2012, "epa"].sum() / q.loc[q.game_id.str[:4].astype(int) <= 2012, "db"].sum()
    p_sack = q.loc[q.game_id.str[:4].astype(int) <= 2012, "sacks"].sum() / q.loc[q.game_id.str[:4].astype(int) <= 2012, "db"].sum()
    qg = {k: v for k, v in q.groupby("game_id")}
    qbs, defs, teams, tdb = {}, {}, {}, {}          # decayed sums keyed by qb id / defence / team; tdb = last games' dropbacks by passer
    rows = []

    def read(state, key, season, carry):
        s = state.get(key)
        if s is None:
            return np.zeros(4), None
        v, last = s
        if season != last:
            v = v * carry ** max(1, season - last)
        return v, last

    for r in sch.itertuples(index=False):
        sea = int(r.season); gq = qg.get(r.game_id)
        feats = {}
        for side, qid, tm, opp in (("h", r.home_qb_id, r.home_team, r.away_team), ("a", r.away_qb_id, r.away_team, r.home_team)):
            v, _ = read(qbs, qid, sea, CARRY_QB) if isinstance(qid, str) else (np.zeros(4), None)
            t, _ = read(teams, tm, sea, CARRY_T)
            f = {"qb_adj_epa": (v[0] + p_qb * K_DB) / (v[1] + K_DB), "qb_eff_db": v[1], "qb_sack_rate": (v[2] + p_sack * 60.0) / (v[1] + 60.0),
                 "qb_exp": np.log1p(v[3]), "team_qb_adj": (t[0] + p_qb * K_DB) / (t[1] + K_DB)}
            f["qb_drop"] = f["qb_adj_epa"] - f["team_qb_adj"]
            # share of the team's recent dropbacks taken by this passer (backup-start detector): from per-team dropback sums
            hl = tdb.get(tm, [])[-8:]; tot = sum(sum(d_.values()) for d_ in hl)
            f["qb_share_recent"] = (sum(d_.get(qid, 0) for d_ in hl) / tot) if (isinstance(qid, str) and tot > 100) else np.nan
            f["backup_start"] = float(f["qb_share_recent"] < 0.30) if f["qb_share_recent"] == f["qb_share_recent"] else np.nan
            feats[side] = f
        for side, tm in (("h", r.home_team), ("a", r.away_team)):
            rows.append({"game_id": r.game_id, "team": tm, **feats[side]})
        if gq is not None:                                   # update states AFTER both sides' features are recorded
            for side, tm, opp in (("h", r.home_team, r.away_team), ("a", r.away_team, r.home_team)):
                g = gq[gq.team == tm]
                if g.empty:
                    continue
                dprior, _ = read(defs, opp, sea, CARRY_T)
                d_epa = (dprior[0] + p_qb * 140.0) / (dprior[1] + 140.0)
                tot_db = g.db.sum()
                for x in g.itertuples(index=False):
                    adj = x.epa - x.db * (d_epa - p_qb)
                    v, _ = read(qbs, x.passer_player_id, sea, CARRY_QB)
                    qbs[x.passer_player_id] = (v * DECAY_QB + np.array([adj, x.db, x.sacks, 1.0 if x.db >= 10 else 0.0]), sea)
                t, _ = read(teams, tm, sea, CARRY_T); teams[tm] = (t * DECAY_T + np.array([(g.epa.sum() - tot_db * (d_epa - p_qb)), tot_db, 0, 0]), sea)
                tdb.setdefault(tm, []).append({x.passer_player_id: x.db for x in g.itertuples(index=False)})
            for side, tm, opp in (("h", r.home_team, r.away_team), ("a", r.away_team, r.home_team)):
                g = gq[gq.team == tm]
                if g.empty:
                    continue
                dd, _ = read(defs, opp, sea, CARRY_T); defs[opp] = (dd * DECAY_T + np.array([g.epa.sum(), g.db.sum(), 0, 0]), sea)
    out = pd.DataFrame(rows)
    if override:
        return out
    out.to_parquet(path); return out


def _snaps(seasons) -> pd.DataFrame:
    s = pd.concat([pd.read_parquet(os.path.join(D.RAW, "snap_counts", f"snap_counts_{y}.parquet")) for y in seasons], ignore_index=True)
    s = s[s.game_type == "REG"].copy(); s["team"] = s["team"].replace(D.TEAM_FIX)
    pl_ = pd.read_parquet(os.path.join(D.RAW, "players", "players.parquet"), columns=["gsis_id", "pfr_id"]).dropna().drop_duplicates("pfr_id")
    s = s.merge(pl_.rename(columns={"pfr_id": "pfr_player_id"}), on="pfr_player_id", how="left")
    s["pct"] = np.where(s["offense_pct"] > 0, s["offense_pct"], s["defense_pct"])
    s["side"] = np.where(s["offense_pct"] > 0, "off", np.where(s["defense_pct"] > 0, "def", "st"))
    return s


def personnel_table(seasons, sn=None, inj=None) -> tuple[pd.DataFrame, dict]:
    """Per team-game: expected-starter absence (certified Out / Doubtful / Questionable), lineup continuity."""
    os.makedirs(CACHE, exist_ok=True); path = os.path.join(CACHE, f"pers_{min(seasons)}_{max(seasons)}.parquet")
    cov_path = path.replace(".parquet", "_cov.json")
    override = sn is not None
    if os.path.exists(path) and not override:
        import json
        return pd.read_parquet(path), json.load(open(cov_path))
    if override:
        rep = {}
    else:
        sn = _snaps(seasons); inj, rep = L.injuries_certified(ROOT, [s for s in seasons if s >= 2010], game_type="REG")
    inj = inj[inj.report_status.isin(ABSENT_P)]; ab = {(r.game_id, r.team, r.gsis_id): ABSENT_P[r.report_status] for r in inj.itertuples(index=False)}
    cov = {"snap_rows": int(len(sn)), "snap_rows_gsis_mapped": float(sn.gsis_id.notna().mean()),
           "snap_pct_weighted_mapped": float(((sn.pct.fillna(0)) * sn.gsis_id.notna()).sum() / sn.pct.fillna(0).sum()),
           "injury_rows_certified": int(len(inj)), "injury_refusals": rep.get("refused", {})}
    sn = sn[sn.side != "st"]
    group_of = {p: g for g, (ps, k, side) in GROUPS.items() for p in ps}
    sn["grp"] = sn["position"].map(group_of); sn = sn[sn.grp.notna()]
    games = (sn[["game_id", "season", "week", "team"]].drop_duplicates().sort_values(["team", "season", "week"]))
    by_game = {k: v for k, v in sn.groupby(["game_id", "team"])}
    rows = []
    for team, tg in games.groupby("team"):
        hist = []                                                  # list of (season, game_id) in order
        for r in tg.itertuples(index=False):
            same = [h for h in hist if h[0] == r.season][-WINDOW:]
            rec = {"game_id": r.game_id, "team": team, "n_prior_season_games": len(same)}
            if len(same) >= MIN_SEASON_GAMES:
                u = {}                                             # (gsis, grp) -> mean pct over appearances in window
                for _, gid in same:
                    for x in by_game[(gid, team)].itertuples(index=False):
                        if x.gsis_id == x.gsis_id and x.pct > 0:
                            u.setdefault((x.gsis_id, x.grp), []).append(x.pct)
                u = {k: float(np.mean(v)) for k, v in u.items()}
                tot_abs = {"off": 0.0, "def": 0.0}; n_abs = 0.0
                for g, (ps, k, side) in GROUPS.items():
                    cand = sorted(((v, key[0]) for key, v in u.items() if key[1] == g and v >= MIN_PCT), reverse=True)[:k]
                    den = sum(v for v, _ in cand)
                    loss = sum(v * ab.get((r.game_id, team, pid), 0.0) for v, pid in cand)
                    rec[f"lost_{g}"] = loss / den if den > 0 else np.nan
                    rec[f"nstart_{g}"] = len(cand); tot_abs[side] += loss; n_abs += sum(ab.get((r.game_id, team, pid), 0.0) for _, pid in cand)
                rec["abs_n_total"] = n_abs
                # lineup continuity: overlap of top-5 OL (offence) and top-11 defenders between consecutive prior games
                def top(gid, grps, n, col):
                    d = by_game[(gid, team)]; d = d[d.grp.isin(grps)].sort_values("pct", ascending=False)
                    return set(d.gsis_id.dropna().head(n))
                ids = [g_ for _, g_ in same][-5:]
                if len(ids) >= 3:
                    ol = [top(g_, ["OL"], 5, "pct") for g_ in ids]; de = [top(g_, ["DL", "LB", "CB", "S"], 11, "pct") for g_ in ids]
                    rec["cont_OL"] = float(np.mean([len(a & b) / 5 for a, b in zip(ol[:-1], ol[1:])]))
                    rec["cont_DEF"] = float(np.mean([len(a & b) / 11 for a, b in zip(de[:-1], de[1:])]))
            rows.append(rec); hist.append((r.season, r.game_id))
    out = pd.DataFrame(rows)
    if override:
        return out, cov
    out.to_parquet(path)
    import json; json.dump(cov, open(cov_path, "w"), indent=1, default=str)
    return out, cov
