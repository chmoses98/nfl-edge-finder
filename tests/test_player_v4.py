"""DATA_PLAYER_V4: snap, volume, allocation, redistribution, outcome distributions, abstention, versioning, storage.

The fixture is a small synthetic league run through the REAL feature pipeline (EWMA -> v2 -> v3 -> v4 features), so
these tests exercise the code production runs, not a mock of it. Its football is simple and known: each team has a
QB, two RBs, three WRs and a TE with fixed roles; some weeks WR1 or RB1 is listed OUT (and does not play), and the
vacated share is taken by the next man up -- exactly the mechanism V4 is meant to learn.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from nfl_edge.engines.player import abstention as AB
from nfl_edge.engines.player import data_dist as DD
from nfl_edge.engines.player import hybrid_dist as HD
from nfl_edge.engines.player.dist import LatticeDistribution
from nfl_edge.engines.player.features_v2 import add_v2_features
from nfl_edge.engines.player.features_v3 import add_v3_features
from nfl_edge.engines.player import v4 as V4
from nfl_edge.engines.player.v4 import features as F4
from nfl_edge.engines.player.v4 import model as M
from nfl_edge.engines.player.v4.snap import SnapModel
from nfl_edge.engines.player.v4.volume import VolumeModel, team_game_table
from nfl_edge.research import player_distributions as pdist

ROLES = [("QB1", "QB", 1.00, 0.00, 0.10), ("RB1", "RB", 0.65, 0.12, 0.62), ("RB2", "RB", 0.35, 0.05, 0.25),
         ("WR1", "WR", 0.92, 0.27, 0.0), ("WR2", "WR", 0.85, 0.20, 0.0), ("WR3", "WR", 0.60, 0.12, 0.0), ("TE1", "TE", 0.80, 0.16, 0.0)]


def synthetic_league(seed=7, n_teams=12, seasons=(2013, 2014, 2015, 2016)):
    rng = np.random.default_rng(seed)
    teams = [f"T{i:02d}" for i in range(n_teams)]
    pass_bias = {t: rng.normal(0, 4) for t in teams}
    rows, status = [], []
    for s in seasons:
        for w in range(1, 18):
            order = rng.permutation(teams)
            for i in range(0, n_teams, 2):
                home, away = order[i], order[i + 1]
                gid = f"{s}_{w:02d}_{away}_{home}"
                total = float(rng.normal(45, 4)); spread = float(rng.normal(0, 5))
                for team, opp, is_home in ((home, away, True), (away, home, False)):
                    sp_team = spread if is_home else -spread
                    it = (total + sp_team) / 2
                    pa = max(15, int(rng.normal(33 + pass_bias[team] + 0.3 * (total - 45) - 0.2 * sp_team, 5)))
                    ra = max(12, int(rng.normal(26 + 0.25 * sp_team, 4)))
                    snaps = pa + ra + int(rng.integers(0, 5))
                    out = set()
                    if rng.random() < 0.18:
                        out.add("WR1")
                    if rng.random() < 0.12:
                        out.add("RB1")
                    for role, pos, snap, ts, cs in ROLES:
                        pid = f"{team}_{role}"
                        if role in out:
                            status.append({"season": s, "week": w, "team": team, "player_id": pid, "report": "OUT", "roster": "ACT"})
                            continue
                        status.append({"season": s, "week": w, "team": team, "player_id": pid, "report": None, "roster": "ACT"})
                        sn, t_s, c_s = snap, ts, cs
                        if role == "WR2" and "WR1" in out:
                            t_s += 0.12
                        if role == "WR3" and "WR1" in out:
                            sn, t_s = 0.9, ts + 0.10
                        if role == "RB2" and "RB1" in out:
                            sn, c_s, t_s = 0.70, 0.60, 0.11
                        tg = int(rng.binomial(pa, min(t_s, 0.9))) if pos != "QB" else 0
                        rec = int(rng.binomial(tg, 0.66))
                        car = int(rng.binomial(ra, min(c_s, 0.95)))
                        comp = int(rng.binomial(pa, 0.64)) if pos == "QB" else 0
                        rows.append({"player_id": pid, "player_display_name": pid, "position": pos, "season": s, "week": w, "game_id": gid,
                                     "team": team, "opponent_team": opp, "completions": comp, "attempts": pa if pos == "QB" else 0,
                                     "passing_yards": int(comp * rng.normal(11, 2)) if pos == "QB" else 0,
                                     "passing_tds": int(rng.poisson(1.4)) if pos == "QB" else 0,
                                     "passing_interceptions": int(rng.poisson(0.7)) if pos == "QB" else 0,
                                     "carries": car, "rushing_yards": int(car * rng.normal(4.3, 1.2)), "rushing_tds": int(rng.poisson(0.02 * car)),
                                     "receptions": rec, "targets": tg, "receiving_yards": int(rec * max(2.0, rng.normal(11, 3))),
                                     "receiving_tds": int(rng.poisson(0.05 * rec)), "offense_snaps": max(1, int(round(snaps * min(sn, 1.0)))),
                                     "zero_row": False, "spread_line": spread, "total_line": total, "home": is_home, "spread_team": sp_team,
                                     "implied_total": it, "qb_starter": role == "QB1", "indoor": False})
    df = pd.DataFrame(rows)
    df["any_td"] = df["rushing_tds"] + df["receiving_tds"]
    df["touches"] = df["targets"] + df["carries"]
    df = df.sort_values(["player_id", "season", "week"]).reset_index(drop=True)
    st = pd.DataFrame(status)
    st["report"] = st["report"].astype("object")
    return df, st


def build_frame(df, st):
    priors = pdist.position_priors(df, range(2013, 2014))
    d = pdist.add_ewma_features(df, halflife=5.0, season_carry=0.5, shrink_k=3.0, priors=priors)
    d = add_v2_features(d, halflife=5.0, season_carry=0.5, shrink_k=3.0)
    d = add_v3_features(DD.ensure_columns(d))
    d = F4.add_recency_features(d)
    return F4.add_absence_features(d, F4.StatusBook(st))


@pytest.fixture(scope="module")
def league():
    df, st = synthetic_league()
    frame = build_frame(df, st)
    teams = team_game_table(frame)
    bundle = M.fit_bundle(frame, 2016, teams=teams, verbose=lambda *a: None)
    test = frame[frame.season == 2016]
    inter = bundle.intermediates(test, teams)
    return {"frame": frame, "teams": teams, "bundle": bundle, "inter": inter, "status": st}


# ------------------------------------------------------------------------------------------------ versioning
def test_v4_has_its_own_identity_and_never_reuses_a_v3_string():
    assert V4.VERSION == "data-player-dist-4.0.0" and V4.HYBRID_VERSION == "hybrid-player-dist-4.0.0"
    assert V4.VERSION not in DD.VERSION_BY_FEATURE_SET.values()
    assert V4.HYBRID_VERSION not in (HD.VERSION, HD.VERSION_V3)
    # v3 identity untouched
    assert DD.VERSION_BY_FEATURE_SET["v3"] == "data-player-dist-3.0.0" and HD.VERSION_V3 == "hybrid-player-dist-2.0.0"
    assert HD.V3_WEIGHT_MARKET == 0.85 and HD.V3_STRUCTURE == HD.MIXTURE


def test_v3_and_v4_arms_coexist_in_the_projector_without_collision():
    import scripts.shadow_v2.project_slate_v2 as P
    from nfl_edge.projection import record as R
    assert P.PLAYER_ARMS[:5] == ("DATA_PLAYER_DIST", "MARKET_PLAYER_DIST", "HYBRID_PLAYER_DIST", "DATA_PLAYER_V3", "HYBRID_PLAYER_V3")
    assert P.PLAYER_ARMS[5:7] == ("DATA_PLAYER_V4", "HYBRID_PLAYER_V4")
    ids = {R.record_id("snap", "T", arm, v, "lattice-1.0.0") for arm, v in
           (("DATA_PLAYER_V3", "data-player-dist-3.0.0"), ("DATA_PLAYER_V4", V4.VERSION), ("HYBRID_PLAYER_V4", V4.HYBRID_VERSION))}
    assert len(ids) == 3


# ------------------------------------------------------------------------------------------------ features
def test_absence_features_see_a_new_absence_and_who_absorbs_it(league):
    f = league["frame"]
    st = league["status"]
    outs = st[(st.report == "OUT") & st.player_id.str.endswith("WR1") & (st.season == 2016)]
    seen_new = seen_long = False
    for o in outs.itertuples():
        if o.week == 1:                   # a week-1 absence is an OFFSEASON departure (vac_off_same), tested elsewhere
            continue
        wk_rows = f[(f.team == o.team) & (f.season == 2016) & (f.week == o.week)]
        wr2 = wk_rows[wk_rows.player_id.str.endswith("WR2")].iloc[0]
        prev_out = ((st.player_id == o.player_id) & (st.season == 2016) & (st.week == o.week - 1) & (st.report == "OUT")).any()
        if prev_out:
            # WR1 also missed the previous game: a LONG absence is already inside everyone's recent shares
            seen_long = True
            assert wr2.vac_same_t == 0
            continue
        seen_new = True
        assert wr2.vac_same_t > 0.15 and 0 < wr2.self_frac_t < 1
        break
    assert seen_new
    rb1 = wk_rows[wk_rows.player_id.str.endswith("RB1")]
    if len(rb1):
        assert rb1.iloc[0].vac_same_t == 0 and rb1.iloc[0].vac_other_t > 0.15     # other group, not same


def test_status_book_unknown_is_not_healthy_and_overlay_wins_for_its_week():
    fr = pd.DataFrame([{"season": 2026, "week": 3, "team": "A", "player_id": "p", "report": "QUESTIONABLE", "roster": "ACT"}])
    sb = F4.StatusBook(fr, overrides={(2026, 3, "q"): "OUT"}, override_weeks=[(2026, 3)])
    assert sb.get(2026, 3, "A", "p")["questionable"] is False            # the file's week-3 report is NOT used
    assert sb.get(2026, 3, "A", "q")["ruled_out"] is True
    unk = F4.StatusBook(None).get(2026, 3, "B", "x")
    assert unk["known"] is False and unk["ruled_out"] is False


def test_missing_recency_falls_back_to_the_ewma_never_to_zero(league):
    f = league["frame"]
    first = f.sort_values(["season", "week"]).groupby("player_id").head(1)
    assert first["max4_snap_share"].notna().all() and (first["max4_snap_share"] == first["ewma_snap_share"]).all()


# ------------------------------------------------------------------------------------------------ snap model
def test_snap_starter_high_backup_low_and_backup_promoted_when_the_starter_is_out(league):
    I = league["inter"]
    wr1 = I[I.player_id.str.endswith("WR1")].snap_mean.mean()
    rb2 = I[I.player_id.str.endswith("RB2")]
    assert wr1 > 0.8
    promoted = rb2[rb2.vac_same_s > 0.3].snap_mean
    normal = rb2[rb2.vac_same_s == 0].snap_mean
    assert len(promoted) and promoted.mean() > normal.mean() + 0.1


def test_snap_uncertainty_is_a_valid_interval_and_wider_for_a_changed_role(league):
    I = league["inter"]
    assert ((I.snap_mean > 0) & (I.snap_mean < 1)).all()
    assert (I.snap_sd > 0).all()
    s = league["bundle"].snap.predict(league["frame"][league["frame"].season == 2016])
    assert ((s.snap_p10 <= s.snap_mean + 1e-9) & (s.snap_mean <= s.snap_p90 + 1e-9)).all()
    assert (s.snap_p10 >= 0).all() and (s.snap_p90 <= 1).all()
    rb2 = I[I.player_id.str.endswith("RB2")]
    assert rb2[rb2.vac_same_s > 0.3].snap_sd.mean() >= rb2[rb2.vac_same_s == 0].snap_sd.mean() * 0.9


def test_snap_ablation_reproduces_the_v3_implicit_estimate(league):
    f = league["frame"]
    m = SnapModel.fit(f[f.season < 2016], ablate=True)
    p = m.predict(f[f.season == 2016])
    base = f[f.season == 2016].ewma_snap_share.clip(0.005, 0.995)
    assert np.allclose(p.snap_mean.dropna(), base[p.snap_mean.notna()])


def test_questionable_or_new_player_is_less_certain_than_a_stable_starter():
    mk = pd.DataFrame({"ewma_snap_share": [0.9, 0.9], "last_snap_share": [0.9, 0.9], "last3_snap_share": [0.9, 0.9],
                       "max4_snap_share": [0.9, 0.9], "cur_mean_snap_share": [0.9, 0.9], "n_cur_season": [4, 0], "n_prior": [40, 0],
                       "changed_team": [0.0, 1.0], "self_new": [0.0, 1.0], "self_returning": [0.0, 0.0], "own_q": [0.0, 1.0],
                       "vac_same_s": [0.0, 0.0], "self_frac_s": [0.5, 0.0], "vac_off_same_s": [0.0, 0.0], "ret_same_s": [0.0, 0.0],
                       "n_active_same": [3, 3], "games_since_last": [1, np.nan], "position": ["WR", "WR"], "offense_snaps": [50, 50],
                       "snap_share": [0.9, 0.9], "qb_starter": [False, False]})
    tr = pd.concat([mk.assign(snap_share=np.clip(0.9 + np.random.default_rng(1).normal(0, 0.03, 2), 0, 1))] * 250, ignore_index=True)
    tr.loc[tr.index % 2 == 1, "snap_share"] = np.random.default_rng(2).uniform(0.2, 1.0, (tr.index % 2 == 1).sum())
    m = SnapModel.fit(tr)
    p = m.predict(mk)
    assert p.snap_sd.iloc[1] > p.snap_sd.iloc[0]


# ------------------------------------------------------------------------------------------------ volume
def test_volume_pass_heavy_team_high_total_and_game_script(league):
    T = league["teams"]
    vm = VolumeModel.fit(T, 2016)
    base = T[(T.season == 2016) & T.pa.notna()].head(40).copy()
    hi = base.assign(implied_total=base.implied_total + 6)
    fav = base.assign(spread_team=base.spread_team + 7)
    assert vm.predict(hi).vol_pa.mean() >= vm.predict(base).vol_pa.mean() - 1e-6
    assert vm.predict(fav).vol_ra.mean() > vm.predict(base).vol_ra.mean()
    heavy = base.assign(t_pa=base.t_pa + 8)
    assert vm.predict(heavy).vol_pa.mean() > vm.predict(base).vol_pa.mean()
    assert vm.sd_pa > 0 and vm.sd_ra > 0


def test_volume_ablation_is_the_team_ewma(league):
    T = league["teams"]
    vm = VolumeModel.fit(T, 2016, ablate=True)
    x = T[T.season == 2016].head(20)
    assert np.allclose(vm.predict(x).vol_pa, np.clip(x.t_pa, 12, 60))


# ------------------------------------------------------------------------------------------------ allocation
def test_shares_reconcile_and_wr2_gains_when_wr1_is_out(league):
    I = league["inter"]
    sums = I.groupby(["team", "game_id"]).share_t.sum()
    assert (sums <= 1.0 + 1e-9).all()
    assert (I.share_t >= 0).all() and (I.share_c >= 0).all()
    wr2 = I[I.player_id.str.endswith("WR2")]
    if (wr2.vac_same_t > 0.15).sum() < 3:
        pytest.skip("too few new WR1 absences in this draw")
    assert wr2[wr2.vac_same_t > 0.15].share_t.mean() > wr2[wr2.vac_same_t == 0].share_t.mean()


def test_multiple_absences_do_not_push_a_share_past_a_plausible_total(league):
    b = league["bundle"]
    I = league["inter"].copy()
    row = I[I.player_id.str.endswith("WR3")].head(1).copy()
    row = row.assign(vac_same_t=0.6, vac_same_s=1.5, self_frac_t=0.5, self_frac_s=0.5)
    out = b.intermediates(row.drop(columns=[c for c in row.columns if c.startswith(("snap_", "vol_", "share_", "mu_", "cv2_", "struct_",
                                                                                  "l_", "r_", "recon_"))]), league["teams"])
    assert 0 <= out.share_t.iloc[0] <= 0.7 and 0 < out.snap_mean.iloc[0] < 1


# ------------------------------------------------------------------------------------------------ outcome distributions
def _dists(league, suffix):
    b, I = league["bundle"], league["inter"]
    r = I[I.player_id.str.endswith(suffix)].iloc[0].to_dict()
    return r, b.distributions(r)


def test_distributions_are_valid_monotone_bounded_and_finite(league):
    for suffix in ("WR1", "RB1", "TE1", "QB1"):
        r, D = _dists(league, suffix)
        assert D, suffix
        for stat, d in D.items():
            ok, why = d.check_valid()
            assert ok, (suffix, stat, why)
            S = d.survival_curve()
            assert np.all(np.isfinite(S)) and S[0] == pytest.approx(1.0) and np.all(np.diff(S) <= 1e-9)
            assert 0 <= d.survival(d.n) <= 0.05          # tail goes to ~0 inside the grid


def test_receptions_follow_targets_and_catch_probability(league):
    b = league["bundle"]
    r, D = _dists(league, "WR1")
    more = dict(r, mu_targets=r["mu_targets"] * 1.5)
    sure = dict(r, r_cr=min(0.95, r["r_cr"] + 0.2))
    base = D["receptions"].mean()
    assert b.distributions(more, stats=["receptions"])["receptions"].mean() > base
    assert b.distributions(sure, stats=["receptions"])["receptions"].mean() > base
    ks = range(1, 12)
    lad = [D["receptions"].survival(k) for k in ks]
    assert all(a >= c for a, c in zip(lad, lad[1:]))


def test_yards_have_a_heavy_right_tail_from_the_compound_structure(league):
    r, D = _dists(league, "WR1")
    d = D["receiving_yards"]
    m, sd = d.mean(), np.sqrt(d.var())
    # a normal with the same mean/sd would put ~2.3% beyond +2 sd; the compound should put at least as much
    assert d.survival(m + 2 * sd) >= 0.015
    assert d.p_zero() > 0          # zero receptions -> zero yards


def test_uncertainty_propagation_widens_the_opportunity_distribution(league):
    b = league["bundle"]
    r, _ = _dists(league, "WR1")
    lo = b.distributions(dict(r, cv2_targets=0.01), stats=["receptions"])["receptions"]
    hi = b.distributions(dict(r, cv2_targets=0.30), stats=["receptions"])["receptions"]
    assert hi.var() > lo.var()


def test_every_stage_can_be_ablated_and_still_produce_valid_distributions(league):
    f, T = league["frame"], league["teams"]
    for cfg in ({"snap": False}, {"volume": False}, {"redistribution": False}, {"allocation": False}, {"propagate": False}, {"market_env": False}):
        b = M.fit_bundle(f, 2016, cfg, teams=T, verbose=lambda *a: None)
        I = b.intermediates(f[(f.season == 2016) & f.player_id.str.endswith("WR1")].head(3), T)
        for rr in I.to_dict("records"):
            for d in b.distributions(rr).values():
                assert d.check_valid()[0]


def test_bundle_identity_is_reproducible(league):
    f, T = league["frame"], league["teams"]
    a = M.fit_bundle(f, 2016, teams=T, verbose=lambda *x: None)
    assert a.artifact_sha == league["bundle"].artifact_sha and a.summary()["version"] == V4.VERSION


# ------------------------------------------------------------------------------------------------ abstention
def _inter(**kw):
    base = {"own_q": 0.0, "own_d": 0.0, "self_new": 0.0, "changed_team": 0.0, "self_returning": 0.0, "vac_same_t": 0.0, "vac_same_c": 0.0,
            "snap_sd": 0.08, "snap_mean": 0.8}
    base.update(kw)
    return base


def test_abstention_v4_states():
    ok = AB.decide_v4(_inter(), stat="receptions", p_model=0.52, p_market=0.50)
    assert ok["structural_state"] == AB.PROJECTION_VALID and ok["state"] == AB.ABSTAIN_MODEL_UNVALIDATED
    assert AB.decide_v4(_inter(self_new=1.0), stat="receptions", p_model=0.5, p_market=0.5)["state"] == AB.ABSTAIN_ROLE_UNCERTAIN
    assert AB.decide_v4(_inter(snap_sd=0.2), stat="receptions", p_model=0.5, p_market=0.5)["state"] == AB.ABSTAIN_SNAP_UNCERTAIN
    assert AB.decide_v4(_inter(own_q=1.0), stat="receptions", p_model=0.5, p_market=0.5)["state"] == AB.ABSTAIN_INJURY_UNCERTAIN
    # an UNKNOWN availability is uncertainty, never a clean bill of health
    assert AB.decide_v4(_inter(), stat="receptions", p_model=0.5, p_market=0.5, availability_state="UNKNOWN")["state"] == AB.ABSTAIN_INJURY_UNCERTAIN
    assert AB.decide_v4(_inter(vac_same_t=0.2), stat="receptions", p_model=0.5, p_market=0.5)["state"] == AB.ABSTAIN_TEAMMATE_SHOCK
    big = AB.decide_v4(_inter(), stat="receptions", p_model=0.70, p_market=0.50)
    assert big["large_disagreement"] and big["structural_state"] == AB.PROJECTION_LOW_CONFIDENCE and not big["production_eligible"]
    hy = AB.decide_v4(_inter(), stat="receptions", p_model=0.5, p_market=0.5, arm="HYBRID_PLAYER_V4", ladder_identification="UNDERIDENTIFIED")
    assert hy["state"] == AB.ABSTAIN_MARKET_INCOMPLETE
    qb = AB.decide_v4(_inter(), stat="passing_yards", p_model=0.5, p_market=0.5, qb_starter_known=False)
    assert qb["state"] == AB.ABSTAIN_VOLUME_UNCERTAIN


def test_large_nominal_edge_with_weak_role_is_less_trusted_not_more():
    weak = AB.decide_v4(_inter(self_returning=1.0), stat="receiving_yards", p_model=0.80, p_market=0.50)
    assert weak["state"] == AB.ABSTAIN_ROLE_UNCERTAIN and not weak["production_eligible"] and weak["large_disagreement"]


# ------------------------------------------------------------------------------------------------ hybrid
def test_hybrid_v4_weights_are_registered_and_never_below_the_market_floor():
    for stat in M.STATS:
        w = HD.v4_weight(stat)
        assert HD.V4_MIN_MARKET_WEIGHT <= w <= 1.0
    assert HD.V4_STRUCTURE == HD.MIXTURE


def test_hybrid_v4_refuses_without_a_market_and_blends_with_one():
    d = LatticeDistribution(np.array([0.2, 0.3, 0.3, 0.2]))
    m = LatticeDistribution(np.array([0.1, 0.2, 0.4, 0.3]))
    assert HD.hybrid(d, None, market_identification=None, w_market=HD.v4_weight("receptions"))["status"] == "UNAVAILABLE"
    h = HD.hybrid(d, m, market_identification="IDENTIFIED", w_market=HD.v4_weight("receptions"), structure=HD.V4_STRUCTURE)
    assert h["status"] == "OK" and h["dist"].check_valid()[0]


# ------------------------------------------------------------------------------------------------ lean storage
def _full_record():
    return {"record_id": "r1", "snapshot_id": "20260924T120000Z", "ticker": "KXNFLREC-X-1", "model_arm": "DATA_PLAYER_V4", "engine": "PLAYER",
            "engine_version": V4.VERSION, "distribution_version": "lattice-1.0.0", "evidence_class": "PROSPECTIVE_FROZEN",
            "market_family": "PLAYER_STAT", "stat_family": "receptions", "threshold": 4.0, "question": {"kind": "THRESHOLD", "k": 4.0},
            "game_id": "2026_03_A_B", "subject_id": "00-1", "p_yes": 0.41, "contract_value": 0.41, "yes_bid": 0.40, "yes_ask": 0.43, "mid": 0.415,
            "player_context": {"player_context_id": "pc1", "position": "WR", "availability_state": "EXPECTED_ACTIVE", "role_certainty": "HIGH",
                               "injury_state": "NOT_LISTED_AT_THIS_VINTAGE", "snap_share_ewma": 0.8, "teammates_out": ["x"] * 20},
            "game_context": {"game_context_id": "gc1", "roof": "dome", "weather": {"a": 1}},
            "market_state": {"last_trade_at": "t", "ladder": {"identification": "IDENTIFIED", "n_rungs_quoted": 6, "rungs": list(range(30))}, "series": "s"},
            "lineage": {"lineage_id": "L", "sidecar": "20260924T120000Z.contexts.json.gz", "engine_versions": {"a": "b"},
                        "point_in_time": {"data_cutoff": "c", "information_frontier": "f", "vintages": {"x": "y"}, "static": {"z": "w"}}},
            "information_sync": {"synchronization_state": "SYNCHRONIZED", "information_skew_seconds": 0.0},
            "data_quality": {"catalog_support": "SUPPORTED", "availability_sources": ["a", "b"]},
            "abstention": {"state": "ABSTAIN_MODEL_UNVALIDATED"}, "flags": {"has_probability": True}, "horizon_quality": {"horizon_quality": "ON_TIME"},
            "feature_lineage": {"snap_mean": 0.8}, "distribution_summary": {"mean": 4.1}}


def test_lean_record_is_smaller_keeps_every_field_the_readers_use_and_resolves_through_the_sidecar():
    import json
    from nfl_edge.evaluation import research_record as RR
    from nfl_edge.projection import lean as LEAN
    full = _full_record()
    ln = LEAN.lean(full)
    assert LEAN.is_lean(ln) and not LEAN.is_lean(full)
    assert len(json.dumps(ln)) < len(json.dumps(full))
    for k in ("record_id", "ticker", "question", "threshold", "p_yes", "contract_value", "abstention", "information_sync", "game_id", "subject_id"):
        assert ln[k] == full[k]
    assert ln["player_context"]["player_context_id"] == "pc1" and ln["game_context"] == {"game_context_id": "gc1"}
    assert "teammates_out" not in ln["player_context"] and ln["market_state"]["ladder"]["identification"] == "IDENTIFIED"
    assert ln["lineage"]["point_in_time"] == {"data_cutoff": "c", "information_frontier": "f"}
    sidecar = {"player_contexts": {"pc1": full["player_context"]}, "game_contexts": {"gc1": full["game_context"]}}
    a = RR.research_row(full, close=None, clv=None, settlement=None, autopsy=None, sidecar=sidecar)
    b = RR.research_row(ln, close=None, clv=None, settlement=None, autopsy=None, sidecar=sidecar)
    for k in ("ctx_role_certainty", "ctx_availability_state", "ctx_injury_state", "ladder_identification", "synchronization_state",
              "pit_data_cutoff", "pit_information_frontier", "abstention_state", "family_group", "contract_value", "player_position", "context_in_sidecar"):
        assert a[k] == b[k], k
    assert full["player_context"]["teammates_out"]                     # the input dict is never mutated


def test_a_lean_refusal_carries_its_reason_and_nothing_about_a_distribution():
    from nfl_edge.evaluation import research_record as RR
    from nfl_edge.projection import lean as LEAN
    r = dict(_full_record(), p_yes=None, contract_value=None, support_state="DATA_UNAVAILABLE", support_reason="outside population")
    ln = LEAN.lean(r)
    assert ln["support_reason"] == "outside population" and ln["support_state"] == "DATA_UNAVAILABLE" and ln["question"] == r["question"]
    assert "distribution_summary" not in ln and "player_context" not in ln and ln["storage"]["refusal"] is True
    row = RR.research_row(ln, close=None, clv=None, settlement=None, autopsy=None, sidecar=None)   # still a readable row
    assert row["support_state"] == "DATA_UNAVAILABLE" and row["p_yes"] is None and row["ticker"] == r["ticker"]


def test_the_hybrid_record_references_the_data_arms_intermediates_instead_of_copying_them():
    from nfl_edge.projection import lean as LEAN
    full = dict(_full_record(), model_arm="HYBRID_PLAYER_V4", feature_lineage={"snap_mean": 0.8, "vol_pa": 33.0, "p_plays": 0.97,
                                                                                 "availability_state": "EXPECTED_ACTIVE"})
    ln = LEAN.lean(full, intermediates=False)
    assert "snap_mean" not in ln["feature_lineage"] and ln["feature_lineage"]["p_plays"] == 0.97
    assert "DATA_PLAYER_V4" in ln["feature_lineage"]["intermediates"]


# ------------------------------------------------------------------------------------------------ RUN NFL
def _row(arm, p, **kw):
    r = {"ticker": "KXNFLREC-X-1", "model_arm": arm, "engine": "PLAYER", "engine_version": "e", "distribution_version": "lattice-1.0.0",
         "model_version": "shadow-v2-1.0.0", "schema_version": "projection-2.3.0", "evidence_class": "PROSPECTIVE_FROZEN",
         "snapshot_id": "20260924T120000Z", "observed_at": "2026-09-24T11:59:00+00:00", "data_cutoff": "2026-09-24T12:00:00+00:00",
         "market_family": "PLAYER_STAT", "period": "FULL", "stat_family": "receptions", "semantic_confidence": "PROVEN",
         "support_state": "PROJECTABLE_NOT_YET_VALIDATED", "p_yes": p, "contract_value": p, "mid": 0.40,
         "settlement_reachability": {"state": "DISPATCHABLE"}, "information_sync": {"synchronization_state": "SYNCHRONIZED"},
         "flags": {"betting_authorized": False, "has_probability": p is not None}}
    r.update(kw)
    return r


def test_run_nfl_shows_v4_as_research_beside_v3_and_never_gives_it_authority():
    import nfl_edge.handicap.shadow_v2_block as SV2
    doc = {"arms": {"BOARD_V2": "WATCH", "MARKET_PLAYER_DIST": "WATCH", "DATA_PLAYER_DIST": "DISABLED"},
           "families": {"MARKET_PLAYER_DIST|ALL": {"status": "WATCH", "reasons": ["16 games"]}}}
    arms = {"DATA_PLAYER_DIST": _row("DATA_PLAYER_DIST", 0.2), "MARKET_PLAYER_DIST": _row("MARKET_PLAYER_DIST", 0.41),
            "DATA_PLAYER_V3": _row("DATA_PLAYER_V3", 0.47), "HYBRID_PLAYER_V3": _row("HYBRID_PLAYER_V3", 0.42),
            "DATA_PLAYER_V4": _row("DATA_PLAYER_V4", 0.52, abstention={"state": "ABSTAIN_MODEL_UNVALIDATED"}),
            "HYBRID_PLAYER_V4": _row("HYBRID_PLAYER_V4", 0.43)}
    b = SV2.market_view(arms, {}, eligibility=doc)
    assert b["primary_arm"] == "DATA_PLAYER_V3"                                   # v4 is a challenger, not the primary slot
    v4 = b["other_arms"]["DATA_PLAYER_V4"]
    assert v4["p_yes"] == 0.52 and v4["eligibility"] == "RESEARCH_ONLY" and v4["abstention"] == "ABSTAIN_MODEL_UNVALIDATED"
    assert "market_derived" not in v4
    assert b["other_arms"]["HYBRID_PLAYER_V4"]["market_derived"] is True and b["other_arms"]["HYBRID_PLAYER_V4"]["eligibility"] == "RESEARCH_ONLY"
    assert b["other_arms"]["DATA_PLAYER_DIST"]["p_yes"] is None                   # disabled stays hidden
    assert b["other_arms"]["MARKET_PLAYER_DIST"]["eligibility"] == "WATCH"
    # a snapshot with no v3 row: v4 fills the independent slot, still research-only
    only4 = SV2.market_view({"DATA_PLAYER_V4": _row("DATA_PLAYER_V4", 0.52)}, {}, eligibility=doc)
    assert only4["primary_arm"] == "DATA_PLAYER_V4" and only4["eligibility"] == "RESEARCH_ONLY"


def test_packet_eligibility_without_a_document_lists_v4_as_research_only():
    from nfl_edge.handicap.packet import eligibility_summary
    s = eligibility_summary(None)
    assert s["arms"]["DATA_PLAYER_V4"] == "RESEARCH_ONLY" and s["arms"]["HYBRID_PLAYER_V4"] == "RESEARCH_ONLY"
    assert s["arms"]["DATA_PLAYER_DIST"] == "DISABLED"


def test_eligibility_keeps_v4_research_only_until_prospective_evidence_exists():
    from nfl_edge.evaluation import eligibility as EL
    assert "DATA_PLAYER_V4" in EL.RESEARCH_BY_DESIGN and "HYBRID_PLAYER_V4" in EL.RESEARCH_BY_DESIGN
    # a strong-looking short sample does not promote it
    m = {"arm": "DATA_PLAYER_V4", "family": "ALL", "n_games": 30, "n_weeks": 2, "delta_brier_game_mean": -0.01, "delta_brier_se": 0.001,
         "delta_brier_upper95": -0.008, "z": -10.0, "ece": 0.01, "clv_game_mean": 0.02, "clv_se": 0.001, "sync_share": 1.0,
         "close_quality_share": 1.0, "pnl_net_game_mean": 0.01, "pnl_net_se": 0.001}
    st, why = EL.decide(m)
    assert st == EL.RESEARCH_ONLY
    doc = EL.build(EL.Accumulator(), as_of="2026-09-24T00:00:00Z", sources=[])
    assert doc["arms"]["DATA_PLAYER_V4"] == "RESEARCH_ONLY" and doc["arms"]["HYBRID_PLAYER_V4"] == "RESEARCH_ONLY"
    assert EL.status_for({"arms": {}, "families": {}}, "DATA_PLAYER_V4", "player_receptions")["status"] == "RESEARCH_ONLY"


def test_a_lean_record_settles_exactly_like_the_full_record(monkeypatch):
    """Settlement reads the question and the contract identity; lean keeps all of it, so the observation handed to the
    incumbent settlement engine is identical."""
    from nfl_edge.projection import lean as LEAN
    from nfl_edge.settlement import settle_v2 as S2
    seen = []
    monkeypatch.setattr(S2.S1, "settle_observation", lambda obs, book, **kw: seen.append(obs) or S2.Settlement("SETTLED", True, "k", "r", {}))
    full = dict(_full_record(), period="FULL", semantic_confidence="PROVEN", subject_name="A Player",
                question={"kind": "THRESHOLD", "k": 4.0, "op": ">="}, yes_semantics="YES if the player records 4+ receptions")
    a = S2.settle_projection(full, book=None)
    b = S2.settle_projection(LEAN.lean(full), book=None)
    assert seen[0] == seen[1] and a == b


def test_lean_records_do_not_move_the_run_summarys_context_coverage():
    import scripts.shadow_v2.project_slate_v2 as P
    from nfl_edge.projection import lean as LEAN
    full = dict(_full_record(), player_context=dict(_full_record()["player_context"], depth_chart_rank=1, team_pass_attempts=33.0,
                                                     qb_depth_chart="00-9", weather_state="KNOWN", injury_report_maturity="MATURE"))
    assert P.context_coverage([full]) == P.context_coverage([LEAN.lean(full)])
    refused = dict(full, p_yes=None, contract_value=None, support_state="POST_KICKOFF")
    assert P.context_coverage([full, refused]) == P.context_coverage([LEAN.lean(full), LEAN.lean(refused)])
