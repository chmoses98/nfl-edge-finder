"""DATA_PLAYER_V5: the point-in-time quarterback resolver, its propagation through V4's structure, and V3 / V4 frozen.

The resolver tests are pure (no data): every rule of nfl_edge/context/qb_resolution.py, and every way evidence from
after the cutoff -- a later chart, an inactive list published later, a postgame observation -- could leak in.

The propagation tests use a small synthetic league run through the REAL pipeline (EWMA -> v2 -> v3 -> v4 features ->
V5 quarterback identity), in which each team carries a starter and a clearly worse backup: when the starter is out the
backup plays, the team throws less, and the receivers catch fewer and shorter passes. A prospective slate is then
built exactly as production builds it, once with the starter available and once with him listed OUT, so the only
difference between the two is the injury report the resolver reads.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import pytest

from nfl_edge.context import qb_resolution as QR
from nfl_edge.context.role import DepthChartBook
from nfl_edge.engines.player import abstention as AB
from nfl_edge.engines.player import data_dist as DD
from nfl_edge.engines.player import hybrid_dist as HD
from nfl_edge.engines.player import v4 as V4
from nfl_edge.engines.player import v5 as V5
from nfl_edge.engines.player.features_v2 import add_v2_features
from nfl_edge.engines.player.features_v3 import add_v3_features
from nfl_edge.engines.player.v4 import features as F4
from nfl_edge.engines.player.v4 import model as M
from nfl_edge.engines.player.v4.volume import team_game_table
from nfl_edge.engines.player.v5 import model as M5
from nfl_edge.engines.player.v5 import prospective as PV5
from nfl_edge.engines.player.v5 import qb_features as QF
from nfl_edge.research import player_distributions as pdist
from nfl_edge.shadow.prospective import build_prospective_rows

CUT = datetime(2026, 9, 20, 15, 30, tzinfo=timezone.utc)
KICK = CUT + timedelta(minutes=90)


def _ev(g, status, source=QR.SRC_INJURY_REPORT, at=CUT - timedelta(hours=20), cls=None):
    return QR.QbEvidence(g, status, source, at, cls)


def _res(chart=("QB1", "QB2", "QB3"), evidence=(), **kw):
    return QR.resolve_team_qb(team="ATL", chart_qbs=list(chart), cutoff=kw.pop("cutoff", CUT), evidence=evidence,
                              kickoff=kw.pop("kickoff", KICK), **kw)


# ------------------------------------------------------------------------------------------------ resolver: rules
def test_available_qb1_is_kept_with_high_certainty():
    for ev in ((), (_ev("QB1", "Probable"),), (_ev("QB1", "EXPECTED_ACTIVE", QR.SRC_AVAILABILITY),), (_ev("QB1", None),)):
        r = _res(evidence=ev)
        assert (r["effective_projected_qb"], r["qb_resolution_reason"], r["qb_resolution_certainty"]) == ("QB1", QR.CHART_QB1_AVAILABLE, QR.HIGH)
        assert r["depth_chart_qb1"] == "QB1" and r["qb_availability_state"] == QR.AVAILABLE and not r["qb_dependent_abstain"]


def test_out_or_ir_qb1_promotes_the_next_charted_qb_with_medium_certainty():
    for status, src in (("Out", QR.SRC_INJURY_REPORT), ("OUT", QR.SRC_AVAILABILITY), ("EXPECTED_OUT", QR.SRC_AVAILABILITY),
                        ("Injured Reserve", QR.SRC_AVAILABILITY), ("RES", QR.SRC_AVAILABILITY)):
        r = _res(evidence=[_ev("QB1", status, src)])
        assert r["effective_projected_qb"] == "QB2" and r["qb_resolution_reason"] == QR.QB1_OUT_PROMOTED_NEXT
        assert r["qb_resolution_certainty"] == QR.MEDIUM and r["depth_chart_qb1"] == "QB1" and r["promoted_over"] == ["QB1"]
        assert r["qb_availability_state"] == QR.OUT and not r["qb_dependent_abstain"]


def test_an_official_inactive_list_at_the_cutoff_makes_the_promotion_high_certainty():
    r = _res(evidence=[_ev("QB1", "INACTIVE_CONFIRMED", QR.SRC_OFFICIAL_INACTIVES, at=KICK - timedelta(minutes=95))])
    assert r["effective_projected_qb"] == "QB2" and r["qb_resolution_certainty"] == QR.HIGH
    assert r["qb_availability_state"] == QR.INACTIVE


def test_the_promotion_skips_a_backup_who_is_himself_out_and_abstains_when_nobody_is_left():
    r = _res(evidence=[_ev("QB1", "Out"), _ev("QB2", "Out")])
    assert r["effective_projected_qb"] == "QB3" and r["promoted_over"] == ["QB1", "QB2"]
    none = _res(chart=("QB1", "QB2"), evidence=[_ev("QB1", "Out"), _ev("QB2", "Out")])
    assert none["effective_projected_qb"] is None and none["qb_resolution_reason"] == QR.QB1_OUT_NO_ELIGIBLE_BACKUP
    assert none["qb_dependent_abstain"] and none["qb_resolution_certainty"] == "UNKNOWN"
    # the promoted QB is himself Questionable: promoted, but LOW certainty
    q = _res(evidence=[_ev("QB1", "Out"), _ev("QB2", "Questionable")])
    assert q["effective_projected_qb"] == "QB2" and q["qb_resolution_certainty"] == QR.LOW


def test_doubtful_abstains_questionable_retains_low_unknown_retains_low():
    d = _res(evidence=[_ev("QB1", "Doubtful")])
    assert d["effective_projected_qb"] == "QB1" and d["qb_resolution_reason"] == QR.QB1_DOUBTFUL_ABSTAIN
    assert d["qb_dependent_abstain"] and d["qb_resolution_certainty"] == QR.LOW
    q = _res(evidence=[_ev("QB1", "Questionable")])
    assert q["effective_projected_qb"] == "QB1" and q["qb_resolution_reason"] == QR.QB1_QUESTIONABLE_RETAINED
    assert q["qb_resolution_certainty"] == QR.LOW and not q["qb_dependent_abstain"]
    # no injury report and no availability capture at the cutoff: not listed is NOT healthy
    u = _res(status_known=False)
    assert u["effective_projected_qb"] == "QB1" and u["qb_resolution_reason"] == QR.QB1_STATUS_UNKNOWN_RETAINED
    assert u["qb_availability_state"] == QR.UNKNOWN and u["qb_resolution_certainty"] == QR.LOW
    # an unrecognised status string is UNKNOWN, never AVAILABLE; a known reading from another source wins over it
    assert QR.normalize_status("weird") == QR.UNKNOWN
    assert _res(evidence=[_ev("QB1", "weird"), _ev("QB1", "Out", QR.SRC_AVAILABILITY)])["effective_projected_qb"] == "QB2"


def test_the_most_severe_reading_across_sources_wins():
    r = _res(evidence=[_ev("QB1", "Questionable"), _ev("QB1", "OUT", QR.SRC_AVAILABILITY)])
    assert r["effective_projected_qb"] == "QB2"
    r = _res(evidence=[_ev("QB1", "Doubtful"), _ev("QB1", "EXPECTED_ACTIVE", QR.SRC_AVAILABILITY)])
    assert r["qb_resolution_reason"] == QR.QB1_DOUBTFUL_ABSTAIN


def test_no_chart_qb1_abstains():
    r = _res(chart=())
    assert r["effective_projected_qb"] is None and r["qb_resolution_reason"] == QR.NO_CHART_QB1 and r["qb_dependent_abstain"]


# ------------------------------------------------------------------------------------------------ resolver: leakage
def test_an_inactive_list_is_used_only_once_it_existed():
    later = _ev("QB1", "INACTIVE_CONFIRMED", QR.SRC_OFFICIAL_INACTIVES, at=CUT + timedelta(minutes=5))
    r = _res(evidence=[later])
    assert r["effective_projected_qb"] == "QB1" and r["qb_resolution_reason"] == QR.CHART_QB1_AVAILABLE
    assert r["evidence_rejected"] and "after the cutoff" in r["evidence_rejected"][0]["reason"]
    # the same list seen from a later cutoff (still pregame) is admissible
    assert _res(evidence=[later], cutoff=CUT + timedelta(minutes=10))["effective_projected_qb"] == "QB2"
    # an official list with no capture time cannot be shown to have existed at the cutoff
    blind = _res(evidence=[_ev("QB1", "INACTIVE_CONFIRMED", QR.SRC_OFFICIAL_INACTIVES, at=None)])
    assert blind["effective_projected_qb"] == "QB1" and "without a capture time" in blind["evidence_rejected"][0]["reason"]


def test_postgame_knowledge_is_never_used():
    # observed after kickoff (e.g. who actually started), even from a cutoff after the game
    post = _ev("QB1", "INACTIVE_CONFIRMED", QR.SRC_OFFICIAL_INACTIVES, at=KICK + timedelta(hours=3))
    r = _res(evidence=[post], cutoff=KICK + timedelta(hours=4))
    assert r["effective_projected_qb"] == "QB1" and "at or after kickoff" in r["evidence_rejected"][0]["reason"]
    tagged = _ev("QB1", "Out", QR.SRC_AVAILABILITY, at=CUT - timedelta(hours=1), cls=QR.POSTGAME_OBSERVATION)
    assert _res(evidence=[tagged])["effective_projected_qb"] == "QB1"
    # the resolver has no argument through which a realised starter could enter
    import inspect
    assert set(inspect.signature(QR.resolve_team_qb).parameters) == {"team", "chart_qbs", "cutoff", "evidence", "chart_vintage",
                                                                   "kickoff", "status_known"}


def test_a_chart_newer_than_the_cutoff_is_refused_and_the_book_never_reads_one():
    r = _res(chart_vintage=CUT + timedelta(hours=1))
    assert r["qb_resolution_reason"] == QR.CHART_AFTER_CUTOFF_REFUSED and r["effective_projected_qb"] is None and r["qb_dependent_abstain"]
    # the book: a chart scraped after the cutoff that demotes QB1 is not visible at the cutoff
    rows = []
    for dt, order in (("2026-09-15T12:00:00Z", ("A", "B")), ("2026-09-21T12:00:00Z", ("B", "A"))):
        for rank, g in enumerate(order, start=1):
            rows.append({"dt": dt, "team": "ATL", "player_name": g, "espn_id": g, "gsis_id": g, "pos_abb": "QB", "pos_slot": 1, "pos_rank": rank})
    book = DepthChartBook.from_frame(pd.DataFrame(rows), CUT)
    assert book.qb1("ATL") == "A" and book.vintage["ATL"] == "2026-09-15T12:00:00Z"
    ok = QR.resolve_team_qb(team="ATL", chart_qbs=[e.gsis_id for e in book.by_team["ATL"]["QB"]], cutoff=CUT,
                            chart_vintage=book.vintage["ATL"], kickoff=KICK)
    assert ok["effective_projected_qb"] == "A"


def test_is_qb_dependent():
    assert QR.is_qb_dependent("passing_yards", "QB") and QR.is_qb_dependent("rushing_yards", "QB")
    assert QR.is_qb_dependent("receptions", "RB") and QR.is_qb_dependent("receiving_yards", "WR")
    assert QR.is_qb_dependent("touchdowns", "TE") and not QR.is_qb_dependent("touchdowns", "RB")
    assert not QR.is_qb_dependent("rushing_yards", "RB") and not QR.is_qb_dependent(None, "QB")


# ------------------------------------------------------------------------------------------------ production evidence
class _Ctx:
    pass


class _Av:
    def __init__(self, state):
        self.state = state


class _Book:
    def __init__(self, by):
        self.by_gsis = by
        self.source_meta = {"sleeper": {"retrieved_at": (CUT - timedelta(minutes=30)).isoformat()}}


def _week2_book():
    rows = []
    for team, qbs in (("ATL", ("00-penix", "00-cousins")), ("KC", ("00-mahomes", "00-backup"))):
        for rank, g in enumerate(qbs, start=1):
            rows.append({"dt": "2026-09-18T12:00:00Z", "team": team, "player_name": g.split("-")[1].title(), "espn_id": g, "gsis_id": g,
                         "pos_abb": "QB", "pos_slot": 1, "pos_rank": rank})
    return DepthChartBook.from_frame(pd.DataFrame(rows), CUT)


def test_production_evidence_reads_the_point_in_time_injury_vintage_availability_and_inactives():
    from nfl_edge.shadow_v2.inactives import InactivesBook
    book = _week2_book()
    ctx = _Ctx()
    ctx.depth = {"book": book}
    ctx.injuries = {"rows": {("00-penix", 2): {"report_status": "Out"}, ("00-penix", 1): {"report_status": None}},
                    "meta": {"retrieved_at": (CUT - timedelta(hours=30)).isoformat()}, "no_vintage_at_cutoff": False}
    ctx.inactives = None
    res = PV5.resolve_slate([("ATL", "g1", 2), ("KC", "g2", 2)], ctx=ctx, avail=None, kick={"g1": KICK, "g2": KICK}, cutoff=CUT)
    assert res[("ATL", "g1")]["effective_projected_qb"] == "00-cousins" and res[("ATL", "g1")]["depth_chart_qb1"] == "00-penix"
    assert res[("KC", "g2")]["qb_resolution_reason"] == QR.CHART_QB1_AVAILABLE
    # the report's row for ANOTHER week is not evidence about this game
    assert PV5.resolve_slate([("ATL", "g1", 1)], ctx=ctx, avail=None, kick={"g1": KICK}, cutoff=CUT)[("ATL", "g1")]["effective_projected_qb"] == "00-penix"
    # no injury vintage at the cutoff: the availability capture still counts; without either the state is UNKNOWN
    ctx.injuries = {"rows": {}, "no_vintage_at_cutoff": True, "meta": {}}
    r = PV5.resolve_slate([("KC", "g2", 2)], ctx=ctx, avail=None, kick={"g2": KICK}, cutoff=CUT)[("KC", "g2")]
    assert r["qb_resolution_reason"] == QR.QB1_STATUS_UNKNOWN_RETAINED
    r = PV5.resolve_slate([("KC", "g2", 2)], ctx=ctx, avail=_Book({"00-mahomes": _Av("DOUBTFUL")}), kick={"g2": KICK}, cutoff=CUT)[("KC", "g2")]
    assert r["qb_resolution_reason"] == QR.QB1_DOUBTFUL_ABSTAIN
    # official inactives, matched by the charted name, only as the loader handed them over (observed pregame)
    obs = (KICK - timedelta(minutes=80)).isoformat()
    ctx.inactives = InactivesBook([{"game_id": "g2", "observed_at": obs, "usable": True,
                                    "rows": [{"game_id": "g2", "player_name": "Mahomes", "observed_at": obs, "espn_id": "x"}]}])
    healthy = _Book({"00-backup": _Av("EXPECTED_ACTIVE")})
    early = PV5.resolve_slate([("KC", "g2", 2)], ctx=ctx, avail=healthy, kick={"g2": KICK}, cutoff=CUT)[("KC", "g2")]
    assert early["effective_projected_qb"] == "00-mahomes"                  # the list post-dates this cutoff
    late = PV5.resolve_slate([("KC", "g2", 2)], ctx=ctx, avail=healthy, kick={"g2": KICK}, cutoff=KICK - timedelta(minutes=60))[("KC", "g2")]
    assert late["effective_projected_qb"] == "00-backup" and late["qb_resolution_certainty"] == QR.HIGH


# ------------------------------------------------------------------------------------------------ synthetic league
ROLES = [("QB1", "QB", 1.00, 0.00, 0.10), ("RB1", "RB", 0.65, 0.12, 0.62), ("RB2", "RB", 0.35, 0.05, 0.25),
         ("WR1", "WR", 0.92, 0.27, 0.0), ("WR2", "WR", 0.85, 0.20, 0.0), ("WR3", "WR", 0.60, 0.12, 0.0), ("TE1", "TE", 0.80, 0.16, 0.0)]


def qb_league(seed=11, n_teams=12, seasons=(2013, 2014, 2015, 2016)):
    """Each team: a starter (QB1) and a clearly worse backup (QB2) who plays only when QB1 is OUT (18% of games). With
    the backup the team throws ~7 fewer passes and completes fewer, shorter ones."""
    rng = np.random.default_rng(seed)
    teams = [f"T{i:02d}" for i in range(n_teams)]
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
                    backup = rng.random() < 0.18
                    cmp_p, ypc, ypr_m, cr = (0.55, 9.0, 8.5, 0.56) if backup else (0.67, 11.5, 11.5, 0.70)
                    pa = max(15, int(rng.normal(36 - (7 if backup else 0) + 0.3 * (total - 45) - 0.2 * sp_team, 4)))
                    ra = max(12, int(rng.normal(26 + 0.25 * sp_team, 4)))
                    snaps = pa + ra + int(rng.integers(0, 5))
                    status.append({"season": s, "week": w, "team": team, "player_id": f"{team}_QB1", "report": "OUT" if backup else None, "roster": "ACT"})
                    status.append({"season": s, "week": w, "team": team, "player_id": f"{team}_QB2", "report": None, "roster": "ACT"})
                    for role, pos, snap, ts, cs in ROLES:
                        pid = f"{team}_{role}"
                        if role == "QB1" and backup:
                            pid = f"{team}_QB2"
                        if pos != "QB":
                            status.append({"season": s, "week": w, "team": team, "player_id": pid, "report": None, "roster": "ACT"})
                        tg = int(rng.binomial(pa, min(ts, 0.9))) if pos != "QB" else 0
                        rec = int(rng.binomial(tg, cr))
                        car = int(rng.binomial(ra, min(cs, 0.95)))
                        comp = int(rng.binomial(pa, cmp_p)) if pos == "QB" else 0
                        rows.append({"player_id": pid, "player_display_name": pid, "position": pos, "season": s, "week": w, "game_id": gid,
                                     "team": team, "opponent_team": opp, "completions": comp, "attempts": pa if pos == "QB" else 0,
                                     "passing_yards": int(comp * rng.normal(ypc, 1.5)) if pos == "QB" else 0,
                                     "passing_tds": int(rng.poisson(1.6 if not backup else 0.8)) if pos == "QB" else 0,
                                     "passing_interceptions": int(rng.poisson(0.6 if not backup else 1.1)) if pos == "QB" else 0,
                                     "carries": car, "rushing_yards": int(car * rng.normal(4.3, 1.2)), "rushing_tds": int(rng.poisson(0.02 * car)),
                                     "receptions": rec, "targets": tg, "receiving_yards": int(rec * max(2.0, rng.normal(ypr_m, 2.5))),
                                     "receiving_tds": int(rng.poisson(0.05 * rec)), "offense_snaps": max(1, int(round(snaps * min(snap, 1.0)))),
                                     "zero_row": False, "spread_line": spread, "total_line": total, "home": is_home, "spread_team": sp_team,
                                     "implied_total": (total + sp_team) / 2, "qb_starter": pos == "QB", "indoor": False})
    df = pd.DataFrame(rows)
    df["any_td"] = df["rushing_tds"] + df["receiving_tds"]
    df["touches"] = df["targets"] + df["carries"]
    st = pd.DataFrame(status).drop_duplicates(["season", "week", "team", "player_id"], keep="first")
    st["report"] = st["report"].astype("object")
    return df.sort_values(["player_id", "season", "week"]).reset_index(drop=True), st


def pipeline(combined, status):
    pro = combined["is_prospective"].fillna(False).astype(bool) if "is_prospective" in combined.columns else pd.Series(False, index=combined.index)
    priors = pdist.position_priors(combined[~pro], range(2013, 2014))
    d = pdist.add_ewma_features(combined, halflife=5.0, season_carry=0.5, shrink_k=3.0, priors=priors)
    d = add_v2_features(d, halflife=5.0, season_carry=0.5, shrink_k=3.0)
    d = add_v3_features(DD.ensure_columns(d))
    d = F4.add_recency_features(d)
    return F4.add_absence_features(d, F4.StatusBook(status))


@pytest.fixture(scope="module")
def qbl():
    df, st = qb_league()
    frame = QF.add_qb_identity_features(pipeline(df, st))
    teams = team_game_table(frame)
    b5 = M5.fit_bundle(frame, 2016, teams=teams, verbose=lambda *a: None)
    b4 = M.fit_bundle(frame, 2016, teams=teams, verbose=lambda *a: None)
    return {"df": df, "st": st, "b5": b5, "b4": b4}


def slate(qbl, qb1_report):
    """A prospective 2016 week-9 game for T00 built as production builds it, with QB1's injury report `qb1_report`."""
    df, st = qbl["df"], qbl["st"]
    wk = 9
    g = df[(df.season == 2016) & (df.week == wk) & (df.team == "T00")].iloc[0]
    hist = df[(df.season < 2016) | ((df.season == 2016) & (df.week < wk))]
    ups = []
    for team, opp, home in ((g.team, g.opponent_team, bool(g.home)), (g.opponent_team, g.team, not bool(g.home))):
        for role, pos, *_ in ROLES + [("QB2", "QB", 0, 0, 0)]:
            ups.append({"player_id": f"{team}_{role}", "player_display_name": f"{team}_{role}", "position": pos, "season": 2016, "week": wk,
                        "game_id": g.game_id, "team": team, "opponent_team": opp, "spread_line": g.spread_line, "total_line": g.total_line,
                        "home": home, "qb_starter": False, "indoor": False})
    up = pd.DataFrame(ups)
    s = st[~((st.season == 2016) & (st.week >= wk))].copy()
    extra = [{"season": 2016, "week": wk, "team": r.team, "player_id": r.player_id, "roster": "ACT",
              "report": (qb1_report if r.player_id == "T00_QB1" else None)} for r in up.itertuples()]
    s = pd.concat([s, pd.DataFrame(extra)], ignore_index=True)
    ev = [QR.QbEvidence("T00_QB1", qb1_report, QR.SRC_INJURY_REPORT, CUT - timedelta(hours=20))] if qb1_report else []
    res = {(t, g.game_id): QR.resolve_team_qb(team=t, chart_qbs=[f"{t}_QB1", f"{t}_QB2"], cutoff=CUT, kickoff=KICK,
                                              evidence=[e for e in ev if e.gsis_id.startswith(t)]) for t in (g.team, g.opponent_team)}
    starters = {k: v["effective_projected_qb"] for k, v in res.items()}
    up = QF.apply_starters(up, starters)
    comb = pipeline(build_prospective_rows(hist, up), s)
    comb = QF.add_qb_identity_features(comb, starters)
    teams = team_game_table(comb)
    feat = comb[comb.is_prospective == True].reset_index(drop=True)   # noqa: E712
    out = {}
    for name, b in (("v5", qbl["b5"]), ("v4", qbl["b4"])):
        I = b.intermediates(feat, teams)
        out[name] = {r["player_id"]: (r, b.distributions(r)) for r in I.to_dict("records")}
    return res, out


def _mean(d):
    return float((np.arange(len(d.pmf)) * d.pmf).sum())


def test_v5_learns_what_a_quarterback_change_does(qbl):
    b = qbl["b5"]
    assert b.version == V5.VERSION and b.config["qb_identity"] is True
    pa = b.volume.pass_m.coefficients()
    assert pa["qb_new_starter"] < -2.0                                       # a backup start throws fewer passes
    assert b.rate[("ypr", "WR")].coefficients()["qb_ypa_delta"] > 0          # a worse passer -> shorter catches
    assert b.rate[("cr", "WR")].coefficients()["qb_cmp_delta"] > 0           # ... and fewer of them
    assert "qb_new_starter" not in qbl["b4"].volume.pass_m.cols              # V4 never sees it


def test_a_qb1_listed_out_propagates_through_the_whole_structure(qbl):
    ra, A = slate(qbl, None)
    rb, B = slate(qbl, "Out")
    assert ra[next(k for k in ra if k[0] == "T00")]["effective_projected_qb"] == "T00_QB1"
    assert rb[next(k for k in rb if k[0] == "T00")]["effective_projected_qb"] == "T00_QB2"
    a, b = A["v5"], B["v5"]
    # the starter flag and the passing population follow the resolved quarterback
    assert a["T00_QB1"][0]["qb_starter"] and not a["T00_QB2"][0]["qb_starter"]
    assert b["T00_QB2"][0]["qb_starter"] and not b["T00_QB1"][0]["qb_starter"]
    for st in ("attempts", "completions", "passing_yards", "passing_tds", "interceptions"):
        assert st in a["T00_QB1"][1] and st not in a["T00_QB2"][1]
        assert st in b["T00_QB2"][1] and st not in b["T00_QB1"][1]
    # team passing volume, and every pass-catcher's targets / receptions / yards
    assert b["T00_WR1"][0]["qb_new_starter"] == 1.0 and a["T00_WR1"][0]["qb_new_starter"] == 0.0
    assert b["T00_WR1"][0]["vol_pa"] < a["T00_WR1"][0]["vol_pa"] - 2.0
    for wr in ("T00_WR1", "T00_WR2", "T00_TE1"):
        assert b[wr][0]["mu_targets"] < a[wr][0]["mu_targets"]
        assert _mean(b[wr][1]["receptions"]) < _mean(a[wr][1]["receptions"])
        assert _mean(b[wr][1]["receiving_yards"]) < _mean(a[wr][1]["receiving_yards"])
    # the backup's passing projection is a backup's
    assert _mean(b["T00_QB2"][1]["passing_yards"]) < _mean(a["T00_QB1"][1]["passing_yards"])
    # the other team is untouched by T00's quarterback
    opp = next(p for p in a if not p.startswith("T00") and p.endswith("WR1"))
    assert a[opp][0]["qb_new_starter"] == b[opp][0]["qb_new_starter"] == 0.0


def test_v4_is_blind_to_the_same_change_except_the_flag(qbl):
    _, A = slate(qbl, None)
    _, B = slate(qbl, "Out")
    # V4 (same frame, its own stages): the receivers' environment does not know who throws -- the #89 defect V5 fixes
    a, b = A["v4"]["T00_WR1"], B["v4"]["T00_WR1"]
    assert abs(a[0]["r_ypr"] - b[0]["r_ypr"]) < 1e-9 and abs(a[0]["r_cr"] - b[0]["r_cr"]) < 1e-9


def test_quarterback_identity_features_are_point_in_time():
    df, st = qb_league(n_teams=4, seasons=(2013, 2014))
    f = QF.team_game_qb_features(df)
    # realised starters: the backup's games are flagged new, the starter's return the next week is flagged new again
    t = df[(df.team == "T00") & (df.position == "QB")].sort_values(["season", "week"])
    first_backup = t[t.player_id == "T00_QB2"].iloc[0]
    row = f[(f.team == "T00") & (f.game_id == first_backup.game_id)].iloc[0]
    assert row.qb_projected_id == "T00_QB2" and row.qb_new_starter == 1.0 and row.qb_ypa_delta < 0
    # a QB's rates at a game use only strictly prior games: his own game's yards never enter
    h = QF.QbHistory(df)
    y0 = h.rates("T00_QB1", int(t.iloc[0].season), int(t.iloc[0].week))
    assert y0[0] == pytest.approx(QF.PRIOR_YPA) and y0[2] == 0.0
    # an override names the projected starter of a game; a game with no resolved QB is unknown (NaN), never zero
    g = t.iloc[5].game_id
    o = QF.team_game_qb_features(df, {("T00", g): None})
    assert np.isnan(o[(o.team == "T00") & (o.game_id == g)].iloc[0].qb_new_starter)


# ------------------------------------------------------------------------------------------------ V3 / V4 frozen
# Digests of V3 and V4 on tests/test_player_v4.synthetic_league, computed with the code at main 50a62fb (before V5
# existed): the V4 bundle sha and every distribution's pmf (rounded to 1e-10), and the V3 bundle's likewise. V5
# parameterises V4's model and volume code; with V4's own config those must reproduce main exactly.
V4_GOLDEN = ("d9708c10a51bcdc5", "afed200591c71016907596ad3d9ae8a150bbcae7f87d026f444eb6168de6f390")
V3_GOLDEN = ("907c1f8fd55cba83", "429a9b36a6519a7aa01278b14607b03cfdaab0f60e7a88dac561af49790a071f")


def test_v4_and_v3_outputs_are_byte_identical_to_main():
    import test_player_v4 as T4
    df, st = T4.synthetic_league()
    frame = T4.build_frame(df, st)
    teams = team_game_table(frame)
    b = M.fit_bundle(frame, 2016, teams=teams, verbose=lambda *a: None)
    h = hashlib.sha256()
    for r in b.intermediates(frame[frame.season == 2016], teams).to_dict("records"):
        for s, d in sorted(b.distributions(r).items()):
            h.update(f"{r['player_id']}|{r['game_id']}|{s}|".encode() + np.round(np.asarray(d.pmf, float), 10).tobytes())
    assert (b.artifact_sha, h.hexdigest()) == V4_GOLDEN and b.version == V4.VERSION and "qb_identity" not in b.config
    bb = DD.fit_bundle(frame[frame.season < 2016], 2016, feature_set="v3", stats=["receptions", "receiving_yards", "passing_yards", "carries"],
                       verbose=lambda *a: None)
    te = frame[frame.season == 2016]
    h3 = hashlib.sha256()
    for stat, m in sorted(bb.models.items()):
        rows = te[pdist.population_mask(te, m.spec.pop)]
        for (p, g), d in zip(zip(rows.player_id, rows.game_id), m.distributions(rows)):
            h3.update(f"{p}|{g}|{stat}|".encode() + np.round(np.asarray(d.pmf, float), 10).tobytes())
    assert (bb.artifact_sha, h3.hexdigest()) == V3_GOLDEN


def test_v4_stage_features_are_exactly_v4s_without_the_flag(qbl):
    b4 = qbl["b4"]
    assert b4.volume.pass_m.cols == ["t_pa", "t_rate", "o_pa_allowed", "implied_total", "spread_team", "home_f", "indoor_f", "qb_changed_recent"]
    assert b4.rate[("ypr", "WR")].cols == ["p_ypr", "ewma_team_ypa", "implied_total"]
    assert b4.rate[("cr", "WR")].cols == ["p_cr", "implied_total", "log_n_prior"]
    assert b4.rate[("attempts", "QB")].cols == ["vol_pa", "ewma_attempts", "snap_mean", "qb_changed_recent", "implied_total", "spread_team"]


# ------------------------------------------------------------------------------------------------ identity / abstention
def test_v5_versions_are_new_and_unique():
    assert (V5.VERSION, V5.HYBRID_VERSION, V5.INPUTS_VERSION) == ("data-player-dist-5.0.0", "hybrid-player-dist-5.0.0", "player-inputs-5.0.0")
    taken = {V4.VERSION, V4.HYBRID_VERSION, V4.INPUTS_VERSION, DD.VERSION, HD.VERSION, HD.VERSION_V3, HD.VERSION_V4,
             *DD.VERSION_BY_FEATURE_SET.values()}
    assert not {V5.VERSION, V5.HYBRID_VERSION, V5.INPUTS_VERSION} & taken
    assert HD.VERSION_V5 == V5.HYBRID_VERSION and HD.v5_weight("receptions") == HD.v4_weight("receptions") == 0.85
    # V4's identity is untouched
    assert (V4.VERSION, V4.HYBRID_VERSION, V4.INPUTS_VERSION) == ("data-player-dist-4.0.0", "hybrid-player-dist-4.0.0", "player-inputs-4.0.0")


def _inter(**kw):
    base = {"own_q": 0.0, "own_d": 0.0, "self_new": 0.0, "changed_team": 0.0, "self_returning": 0.0, "vac_same_t": 0.0, "vac_same_c": 0.0,
            "snap_sd": 0.08, "snap_mean": 0.8, "pgroup": "WR", "effective_projected_qb": "QB1", "qb_dependent_abstain": False,
            "qb_resolution_reason": QR.CHART_QB1_AVAILABLE, "qb_availability_state": QR.AVAILABLE}
    base.update(kw)
    return base


def test_abstention_v5_adds_only_the_quarterback_reason():
    ok = AB.decide_v5(_inter(), stat="receptions", p_model=0.52, p_market=0.50)
    v4 = AB.decide_v4(_inter(), stat="receptions", p_model=0.52, p_market=0.50)
    assert ok["state"] == v4["state"] == AB.ABSTAIN_MODEL_UNVALIDATED and ok["structural_state"] == AB.PROJECTION_VALID
    d = _inter(qb_dependent_abstain=True, qb_resolution_reason=QR.QB1_DOUBTFUL_ABSTAIN, qb_availability_state=QR.DOUBTFUL)
    wr = AB.decide_v5(d, stat="receptions", p_model=0.5, p_market=0.5)
    assert wr["state"] == AB.ABSTAIN_QB_UNCERTAIN and wr["structural_state"] == AB.ABSTAIN_QB_UNCERTAIN
    assert "QB1_DOUBTFUL_ABSTAIN" in wr["reasons"][0] and wr["qb_resolution"]["qb_resolution_reason"] == QR.QB1_DOUBTFUL_ABSTAIN
    # an RB's rushing is not a quarterback-dependent projection
    assert AB.decide_v5({**d, "pgroup": "RB"}, stat="rushing_yards", p_model=0.5, p_market=0.5)["structural_state"] == AB.PROJECTION_VALID
    # earlier structural reasons keep their precedence
    assert AB.decide_v5({**d, "self_new": 1.0}, stat="receptions", p_model=0.5, p_market=0.5)["state"] == AB.ABSTAIN_ROLE_UNCERTAIN
    # no resolved QB at all: a QB statistic is volume-uncertain exactly as V4 says it
    q = AB.decide_v5(_inter(pgroup="QB", effective_projected_qb=None), stat="passing_yards", p_model=0.5, p_market=0.5)
    assert q["state"] == AB.ABSTAIN_VOLUME_UNCERTAIN
