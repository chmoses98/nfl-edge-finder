"""The canonical game file must represent the CURRENT projection system faithfully and completely.

These tests exist because of one report: `handicap-reports/latest/games/2026_02_DET_BUF.md`, 2026 week 2.
Jahmyr Gibbs's rushing yards appeared there with a model median of `--` against a market median of ~87.8,
and a handicapper reading that document would conclude the projection system had no view on the single
most-traded player prop in the game.  It had one: the coherent simulation put his football mean at 95.1.
Three independent defects stacked up.

1. The table labelled "PLAYER PROJECTIONS vs MARKET" was the LEGACY incumbent ladder-derived model, sat
   ABOVE the simulation, and was the natural thing to read as "the model".  Its median is where the
   incumbent's own listed ladder crosses 0.50; that ladder topped out at 0.4647 on its lowest rung, so
   there was no crossing and the cell was blank.
2. The simulation exported a football mean and sd and no quantiles at all, although `LatticeDistribution`
   had computed p05/p25/p50/p75/p95 all along -- so there was no median to show even where one was wanted.
3. The simulation's own projection table was rendered `pp[:max_players * 3]` -- 42 rows.  DET @ BUF had 57.
   Gibbs's rushing yards was row 47.  Fifteen priced projections were absent from the document, with
   nothing in the document saying so.

Each test below fails on the code as it stood before that was fixed.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nfl_edge.engines.player.dist import LatticeDistribution        # noqa: E402
from nfl_edge.handicap import packet as PK, sim_block               # noqa: E402
from nfl_edge.handicap.render import render_game_markdown, render_markdown  # noqa: E402
from nfl_edge.pricing.game_env import ResidualBank                  # noqa: E402
from nfl_edge.sim import prospective as PR                          # noqa: E402
import sim_fixtures as FX                                           # noqa: E402

GAME_FIXTURE = os.path.join(ROOT, "tests", "fixtures", "handicap_game_sample.json")


@pytest.fixture(scope="module")
def bundle_and_frames():
    return FX.synthetic_bundle(seed=1)


@pytest.fixture(scope="module")
def bank():
    rng = np.random.default_rng(3)
    n = 600
    return ResidualBank(rng.normal(0, 13, n), rng.normal(0, 13, n), np.repeat([2020, 2021, 2022], n // 3),
                        ref_season=2023,
                        spread_lines=np.where(rng.random(n) < 0.5, 3.0, 2.5),
                        total_lines=np.where(rng.random(n) < 0.5, 44.0, 44.5),
                        overtime=rng.random(n) < 0.06, results=rng.normal(0, 13, n),
                        rng=np.random.default_rng(1))


# ===================================================================================== A: the actual median
def test_the_exported_summary_is_the_distributions_own(
):
    """`distribution_fields` reports the distribution, it does not re-estimate it.

    Every quantile must be `LatticeDistribution.quantile(q)` on the same pmf that prices the ladder, and the
    median must be `quantile(0.5)` EXACTLY -- not a ladder crossing, not an interpolation, not a normal
    approximation off the mean and sd.
    """
    rng = np.random.default_rng(7)
    d = LatticeDistribution.from_samples(np.clip(rng.normal(95, 40, 40000), 0, None), 300)
    out = PR.distribution_fields("football", d)
    assert set(out) == {f"football_{k}" for k in ("mean", "sd", "p05", "p25", "p50", "p75", "p95")}
    assert out["football_p50"] == pytest.approx(d.quantile(0.5), abs=0.0), "the median must BE quantile(0.50)"
    for q in ("p05", "p25", "p50", "p75", "p95"):
        assert out[f"football_{q}"] == pytest.approx(d.quantile(float(f"0.{q[1:]}")), abs=0.0)
    assert out["football_mean"] == pytest.approx(d.mean(), abs=0.0)
    assert out["football_sd"] == pytest.approx(float(np.sqrt(d.var())), abs=0.0)
    # the quantiles must actually order, or something is estimating rather than reading
    vals = [out[f"football_{q}"] for q in ("p05", "p25", "p50", "p75", "p95")]
    assert vals == sorted(vals) and vals[0] < vals[-1]
    # and a distribution that is not there yields the keys with None -- never a missing key
    none = PR.distribution_fields("football", None)
    assert set(none) == set(out) and set(none.values()) == {None}


def test_prospective_pricing_persists_the_quantiles_on_every_priced_row(bundle_and_frames, bank, monkeypatch):
    """End to end through the real pricing path: a priced player/stat row carries the summary."""
    b, tf, pf = bundle_and_frames
    gi = FX.game_input(tf, pf)
    monkeypatch.setattr(PR.I, "historical_bank", lambda season: bank)
    pid = gi.home.players[gi.home.players["position"] == "QB"]["player_id"].iloc[0]
    ledger = [{"game_id": gi.game_id, "family": "PLAYER_STAT", "period": "FULL", "stat": "passing_yards",
               "player_kalshi_id": "K1", "player_name": "Test Quarterback", "threshold": float(k),
               "ticker": f"PY-{k}", "yes_bid": 0.48, "yes_ask": 0.52, "mid": 0.50, "operator": ">="}
              for k in (150, 200, 250, 300)]
    slate = {"games": {gi.game_id: {"input": gi, "kickoff": None, "center_diag": {}}}}
    rows = PR.price_slate(slate, ledger, b, None, n_sims=1500, run_id="r",
                          observed_at="2026-09-16T00:00:00Z",
                          generated_at=datetime(2026, 9, 16, tzinfo=timezone.utc),
                          player_map={"K1": pid}, verbose=lambda *a: None)
    priced = [r for r in rows if r["support_state"] in sim_block.EXPOSABLE_STATES]
    assert priced, "the fixture must price at least one row for the assertion to mean anything"
    for r in priced:
        for f in ("football_mean", "football_sd", "football_p05", "football_p25", "football_p50",
                  "football_p75", "football_p95", "final_p50"):
            assert r.get(f) is not None, f"{f} missing from a priced row"
        assert r["football_p05"] <= r["football_p50"] <= r["football_p95"]
        # identity travels with the row, for the human label and for provenance
        assert r["player_name"] == "Test Quarterback"
        assert r["player_id"] == pid and r["player_kalshi_id"] == "K1"


# ============================================================== B: the Gibbs-class failure, reproduced
def _gibbs_class_rows():
    """A supported RB rushing-yards ladder whose INCUMBENT model probabilities never reach 0.50.

    These are the real 2026 week 2 DET @ BUF numbers: fifteen listed rungs, every one SUPPORTED, the
    incumbent's own highest probability 0.4647 at the lowest rung.  The ladder-derived median cannot exist.
    """
    mids = [0.805, 0.730, 0.640, 0.550, 0.470, 0.375, 0.305, 0.250, 0.190, 0.160, 0.115, 0.080, 0.070, 0.045, 0.040]
    model = [0.4647, 0.3772, 0.2876, 0.2213, 0.1679, 0.1336, 0.0975, 0.0746, 0.0552, 0.0438, 0.0316, 0.0198,
             0.0141, 0.0090, 0.0062]
    ks = list(range(50, 200, 10))
    return [{"ticker": f"RY-{k}", "family": "PLAYER_STAT", "period": "FULL", "stat": "rushing_yards",
             "player_name": "Jahmyr Gibbs", "player_id": "00-0039139",
             "player_kalshi_id": "96025d7c-6dc9-4d2c-9f98-4d96bef50096", "team": "DET",
             "threshold": float(k), "operator": ">=", "mid": m, "model_contract_value": p,
             "support_state": "SUPPORTED", "availability_state": "ACTIVE", "p_plays": 0.98}
            for k, m, p in zip(ks, mids, model)]


def test_a_legacy_ladder_with_no_crossing_has_no_median_and_that_is_the_legacy_tables_problem():
    """The negative control: the legacy block really cannot produce a median for this ladder."""
    blocks = PK.player_projection_blocks(_gibbs_class_rows(), {}, "2026_02_DET_BUF")
    blk = blocks["Jahmyr Gibbs"]["stats"]["rushing_yards"]
    assert blk["supported_rungs"] == 15, "every rung is supported -- this is not a data gap"
    assert blk["model"]["median"] is None, "the incumbent ladder never crosses 0.50, so it has no median"
    assert blk["market"]["median"] is not None, "the MARKET ladder does cross, which is why the row looked broken"


def test_the_simulation_still_exposes_a_football_median_for_the_gibbs_class_row():
    """A failure of the OLD ladder-derived median must never make the CURRENT simulator look absent.

    The simulation's median comes from its own distribution, so it exists whatever the incumbent's ladder
    does -- and the game file must show it.
    """
    d = LatticeDistribution.from_samples(
        np.clip(np.random.default_rng(11).normal(95, 45, 40000), 0, None), 300)
    sim_rows = [dict(r, support_state="PRICED", support_reason=None, p_football=0.5, p_reconciled=0.5,
                     reconcile_weight=0.0, mid=r["mid"], market_mean=93.0, market_p50=90.0,
                     final_mean=93.0, final_p50=90.0, p_active=0.98, n_sims=20000,
                     **PR.distribution_fields("football", d))
                for r in _gibbs_class_rows()]
    view = sim_block.game_view(sim_rows, {"sim_version": "sim-1.1.0", "run_id": "r"})
    proj = view["player_projections"]
    assert len(proj) == 1
    row = proj[0]
    assert row["football_p50"] is not None and row["football_p50"] == pytest.approx(d.quantile(0.5))
    assert row["football_mean"] == pytest.approx(d.mean())
    assert row["distribution_quantiles_available"] is True
    assert row["player_name"] == "Jahmyr Gibbs", "the table must read as a name, not a GSIS id"
    assert row["player_id"] == "00-0039139" and row["player_kalshi_id"].startswith("96025d7c")

    game = _game_with(sim_rows, legacy_rows=_gibbs_class_rows())
    md = render_game_markdown(game)
    # the coherent simulation's row for the very stat the legacy table left blank
    sim_line = _row_for(md, "COHERENT SIMULATION", "Jahmyr Gibbs", "rushing_yards")
    assert sim_line, "the simulation's rushing-yards projection is missing from the game file"
    assert f"{d.quantile(0.5):.1f}" in sim_line, f"the football median is not in the row: {sim_line}"
    # and the legacy table's blank is explicitly disarmed
    assert "blank here does not mean sim-1.x lacks a projection" in md


# ========================================================== C: the full game file may not truncate
def _sim_row(team, pid, name, stat, k, mean, d=None):
    fields = PR.distribution_fields("football", d) if d is not None else {
        "football_mean": mean, "football_sd": 1.0, "football_p05": mean * 0.5, "football_p25": mean * 0.8,
        "football_p50": mean, "football_p75": mean * 1.2, "football_p95": mean * 1.6}
    return {"ticker": f"{pid}-{stat}-{k}", "family": "PLAYER_STAT", "period": "FULL", "stat": stat,
            "team": team, "player_id": pid, "player_kalshi_id": f"K-{pid}", "player_name": name,
            "threshold": float(k), "operator": ">=", "mid": 0.5, "support_state": "PRICED",
            "support_reason": None, "p_football": 0.5, "p_reconciled": 0.5, "reconcile_weight": 0.25,
            "market_mean": mean, "market_p50": mean, "final_mean": mean, "final_p50": mean,
            "p_active": 0.97, **fields}


def _many_sim_rows(n_groups=60):
    """`n_groups` distinct (player, stat) projections -- comfortably past the old 42-row cap."""
    stats = ["rushing_yards", "receiving_yards", "receptions", "carries", "touchdowns", "passing_yards"]
    rows = []
    for i in range(n_groups):
        stat = stats[i % len(stats)]
        pid = f"00-{i:07d}"
        rows += [_sim_row("DET" if i % 2 else "BUF", pid, f"Player {i:02d}", stat, k, 10.0 + i)
                 for k in (1, 2, 3)]
    return rows


def _game_with(sim_rows, legacy_rows=None, names=None, listed=None):
    with open(GAME_FIXTURE) as f:
        g = json.load(f)
    g["simulation"] = sim_block.game_view(sim_rows, {"sim_version": "sim-1.1.0", "run_id": "r"},
                                          names=names, listed=listed)
    if legacy_rows is not None:
        g["players"] = PK.player_projection_blocks(legacy_rows, {}, g["game_id"])
    return g


def _sim_section(md):
    """The COHERENT SIMULATION section only, up to whatever heading comes next."""
    i = md.index("### COHERENT SIMULATION")
    nxt = re.search(r"^#{2,3} ", md[i + 5:], re.M)
    return md[i:i + 5 + nxt.start()] if nxt else md[i:]


def _projection_rows(md):
    """The data rows of the coherent-simulation projection table (not the coverage tables)."""
    seg = _sim_section(md)
    stop = seg.index("**SIMULATION COVERAGE") if "**SIMULATION COVERAGE" in seg else len(seg)
    return [l for l in seg[:stop].split("\n")
            if l.startswith("| ") and not l.startswith("|---") and "| player | team | stat |" not in l]


def _row_for(md, section, who, stat):
    seg = _sim_section(md) if section == "COHERENT SIMULATION" else md
    for l in seg.split("\n"):
        if l.startswith(f"| {who} |") and f"| {stat} |" in l:
            return l
    return None


def test_the_full_game_file_renders_every_exposable_projection_row():
    """Reintroducing `pp[:max_players * 3]` fails here: 60 groups, 42 would be rendered, 18 would vanish."""
    rows = _many_sim_rows(60)
    game = _game_with(rows)
    expected = game["simulation"]["player_projections"]
    assert len(expected) == 60, "the fixture must exceed the old 42-row cap to mean anything"
    md = render_game_markdown(game)
    rendered = _projection_rows(md)
    assert len(rendered) == len(expected), (
        f"the full game file rendered {len(rendered)} of {len(expected)} simulation projection rows")
    for x in expected:
        assert _row_for(md, "COHERENT SIMULATION", x["player_name"], x["stat"]), \
            f"{x['player_name']} {x['stat']} is missing from the full game file"
    # the LAST row specifically -- a cap always takes the tail
    last = expected[-1]
    assert _row_for(md, "COHERENT SIMULATION", last["player_name"], last["stat"]), "the final row was dropped"
    # and the file says the counts match, in the document itself
    assert f"simulation projection rows total: **{len(expected)}** · rendered here: **{len(expected)}**" in md
    assert "silently missing: 0" in md
    assert "TRUNCATED" not in _sim_section(md), "a full game file must never truncate this table"


def test_the_full_game_file_shows_the_distribution_summary_columns():
    """The columns a handicapper was promised, by name, so "model median" can never be ambiguous again."""
    md = render_game_markdown(_game_with(_many_sim_rows(3)))
    for col in ("football mean", "football median (p50)", "p25", "p75", "p05", "p95", "market mean",
                "market median", "reconciled mean", "reconciled median", "P(active)", "rungs", "support"):
        assert f"| {col} |" in md or col in _sim_section(md), col


# ============================================== D: the compact slate may truncate, and must say so
def _slate_packet(game):
    return {"schema_version": PK.PACKET_SCHEMA_VERSION, "handicap_run_id": "x", "packet_sha": "abc",
            "built_at": "2026-09-17T18:46:06+00:00", "season": 2026, "week": 2, "games": [game],
            "sources": {"ledger": "l.jsonl.gz", "model_version": "shadow-0.4.0", "context_captures": ["c1"],
                        "capture_files_scanned_for_movement": 1, "team_profile_basis": "b",
                        "qb_profile_basis": 2025},
            "real_money_status": "NOT VALIDATED",
            "slate_summary": {"games": 1, "markets_listed_slate": 1, "markets_supported_slate": 1,
                              "markets_discovered_all_weeks": 1, "ledger_support_states": {},
                              "new_or_changed_injuries": [], "major_skill_injuries_out": [],
                              "weather_concerns": [], "largest_market_moves": [],
                              "largest_model_market_disagreements": [], "highest_liquidity_markets": [],
                              "blocking_data_issues": [],
                              "game_priority_for_handicap": [{"rank": 1, "game_id": game["game_id"],
                                                              "priority_score": 1.0, "reasons": ["x"],
                                                              "kickoff_utc": game["kickoff_utc"]}],
                              "disclaimer": "not a bet ranking"}}


def test_the_compact_slate_may_truncate_but_must_say_so_and_point_at_the_game_file():
    rows = _many_sim_rows(60)
    game = _game_with(rows)
    total = len(game["simulation"]["player_projections"])
    slate = render_markdown(_slate_packet(game), max_players_per_game=8, compact=True)
    shown = len([l for l in _sim_section(slate).split("\n")
                 if l.startswith("| ") and not l.startswith("|---") and "| player | team | stat |" not in l])
    assert shown < total, "this test is meaningless unless the compact slate actually truncates"
    assert f"TRUNCATED: {shown} of {total} projection rows shown" in slate
    assert "in this game's own file under `games/`" in slate
    # ... and the game file carries the complete set
    full = render_game_markdown(game)
    assert len(_projection_rows(full)) == total


# ================================================== E: legacy must never wear the current model's name
def test_the_legacy_incumbent_table_cannot_pass_for_the_current_model():
    md = render_game_markdown(_game_with(_many_sim_rows(5), legacy_rows=_gibbs_class_rows()))
    assert "### LEGACY INCUMBENT PROJECTIONS — DIAGNOSTIC ONLY" in md
    assert "### PLAYER PROJECTIONS vs MARKET" not in md, \
        "the legacy table must not carry a generic heading that reads as the current projection system"
    assert "### COHERENT SIMULATION — PLAYER PROJECTIONS" in md
    # the coherent simulation is PRIMARY: it comes first
    assert md.index("### COHERENT SIMULATION") < md.index("### LEGACY INCUMBENT")
    # the four things the legacy heading has to say
    for claim in ("This is NOT the current coherent simulation",
                  "historical comparison and diagnostics",
                  "must not override sim-1.x",
                  "blank here does not mean sim-1.x lacks a projection"):
        assert claim in md, claim
    # the legacy median column is named for what it is
    assert "legacy ladder median" in md and "| model median |" not in md
    # and the current table says, in the document, that it is the current one
    assert "This is the current projection system (sim-1.x" in md


# ====================================================================== F: coverage conservation
def test_every_listed_player_stat_group_lands_in_exactly_one_coverage_bucket():
    """A synthetic board with one group per refusal state, plus priced ones. Nothing may be lost."""
    priced = _many_sim_rows(4)
    refused = [
        # an unsupported statistic: identity resolved, no simulated stat
        {"ticker": "U1", "family": "PLAYER_STAT", "period": "FULL", "stat": "longest_rush", "team": "DET",
         "player_id": "00-1000001", "player_kalshi_id": "KU1", "player_name": "Unsupported Stat",
         "support_state": "UNSUPPORTED_STAT", "support_reason": "no simulated statistic for longest_rush"},
        # an unmapped player: the Kalshi id never resolved to a GSIS id
        {"ticker": "U2", "family": "PLAYER_STAT", "period": "FULL", "stat": "rushing_yards", "team": "BUF",
         "player_id": None, "player_kalshi_id": "KU2", "player_name": "Unmapped Player",
         "support_state": "UNSUPPORTED_IDENTITY", "support_reason": "Kalshi player id not resolved to GSIS"},
        # not in the point-in-time eligible set
        {"ticker": "U3", "family": "PLAYER_STAT", "period": "FULL", "stat": "receptions", "team": "DET",
         "player_id": "00-1000003", "player_kalshi_id": "KU3", "player_name": "Inactive Player",
         "support_state": "NOT_ELIGIBLE", "support_reason": "player not in the eligible set"},
        # a contract rule the pricer will not price
        {"ticker": "U4", "family": "PLAYER_STAT", "period": "FULL", "stat": "receiving_yards", "team": "BUF",
         "player_id": "00-1000004", "player_kalshi_id": "KU4", "player_name": "Odd Operator",
         "support_state": "UNSUPPORTED_RULES", "support_reason": "operator between"},
        # the game's own identities did not hold
        {"ticker": "U5", "family": "PLAYER_STAT", "period": "FULL", "stat": "carries", "team": "DET",
         "player_id": "00-1000005", "player_kalshi_id": "KU5", "player_name": "Incoherent Game",
         "support_state": "UNSUPPORTED_COHERENCE", "support_reason": "simulated game violates an identity"},
    ]
    # a game-family row, which is not a player/stat group and must not be counted as one
    game_family = [{"ticker": "TOT-44", "family": "TOTAL", "period": "FULL", "threshold": 44.0,
                    "support_state": "MARKET_CENTRED_GAME", "mid": 0.5, "p_football": 0.5}]
    rows = priced + refused + game_family
    view = sim_block.game_view(rows, {"sim_version": "sim-1.1.0", "run_id": "r"})
    cov = view["coverage"]

    groups = {(r.get("player_id") or r.get("player_kalshi_id"), r.get("stat"))
              for r in rows if r["family"] == "PLAYER_STAT"}
    assert cov["player_stat_groups_listed"] == len(groups) == 9
    assert sum(cov["buckets"].values()) == cov["player_stat_groups_listed"], \
        "a group counted twice or not at all"
    assert cov["buckets"]["SIMULATED_AND_EXPOSED"] == 4 == view["simulation_projection_rows_total"]
    for state in ("UNSUPPORTED_STAT", "UNSUPPORTED_IDENTITY", "NOT_ELIGIBLE", "UNSUPPORTED_RULES",
                  "UNSUPPORTED_COHERENCE"):
        assert cov["buckets"][state] == 1, state
    assert cov["silently_missing"] == 0 and not cov["silently_missing_detail"]
    # every refusal carries its reason, so a missing model never reads as a missing market
    assert len(cov["unsupported_or_refused"]) == 5
    assert all(r["reason"] for r in cov["unsupported_or_refused"])

    # and the document reports the same accounting, including each refusal and its reason
    md = render_game_markdown(_game_with(rows))
    assert "**SIMULATION COVERAGE — every listed FULL-period player/stat market group**" in md
    assert "listed FULL-period player/stat groups: **9**" in md
    assert "silently missing: 0" in md
    for r in refused:
        assert r["player_name"] in md and r["support_reason"] in md, r["ticker"]


def test_a_listed_group_the_simulation_run_never_saw_is_accounted_for_too():
    """The denominator is the LISTED board, not the rows the run happened to produce.

    2026 week 2: 897 listed FULL-period player/stat groups across the slate, 313 of which the attached
    simulation run produced no row for at all -- PIT @ NE alone had 144 listed player/stat markets with no
    sim row, including 74 receptions rungs, a statistic the same run priced in other games. Counting
    coverage over the sim rows can only ever count what the run produced, so those 313 groups were invisible
    to the accounting as well as to the table. They are listed markets; the report has to say so.
    """
    priced = _many_sim_rows(2)                       # 2 groups the run priced
    listed = [dict(r, family="PLAYER_STAT", period="FULL") for r in priced]
    listed += [{"ticker": "NEW-1", "family": "PLAYER_STAT", "period": "FULL", "stat": "receptions",
                "player_name": "Listed After The Run", "team": "BUF"},
               {"ticker": "NEW-2", "family": "PLAYER_STAT", "period": "FULL", "stat": "receptions",
                "player_name": "Listed After The Run", "team": "BUF"},
               {"ticker": "FFP-1", "family": "PLAYER_STAT", "period": "FULL", "stat": "fantasy_points",
                "player_name": "Never Priced", "team": "DET"}]
    view = sim_block.game_view(priced, {"sim_version": "sim-1.1.0", "run_id": "r"}, listed=listed)
    cov = view["coverage"]
    assert cov["denominator"] == "listed market board"
    assert cov["player_stat_groups_listed"] == 4, "2 priced groups + 2 groups the run never saw"
    assert cov["buckets"]["SIMULATED_AND_EXPOSED"] == 2
    assert cov["buckets"]["NOT_IN_SIMULATION_RUN"] == 2
    assert sum(cov["buckets"].values()) == cov["player_stat_groups_listed"]
    assert cov["silently_missing"] == 0
    # both are named, with the reason, in the document
    md = render_game_markdown(_game_with(priced, listed=listed))
    assert "Listed After The Run" in md and "Never Priced" in md
    assert "NOT_IN_SIMULATION_RUN" in md
    assert "no row in the attached simulation run" in md
    # a group the run never saw must not be counted as one the run refused on football grounds
    assert cov["buckets"]["UNSUPPORTED_STAT"] == 0


def test_a_priced_group_that_never_reached_the_table_is_reported_not_lost():
    """The guard itself: if a priced group ever stops being exposed, the report must say so loudly."""
    rows = _many_sim_rows(2)
    cov = sim_block.coverage(rows, projected_keys=set())          # nothing exposed
    assert cov["silently_missing"] == 2 and cov["buckets"]["EXPOSABLE_BUT_NOT_EXPOSED"] == 2
    assert sum(cov["buckets"].values()) == cov["player_stat_groups_listed"]


# ============================================= Phase 8: an old artifact is read honestly, never patched
def test_a_pre_sim_1_1_0_artifact_reports_its_quantiles_as_unavailable_rather_than_inventing_one():
    """Old sim artifacts are immutable and carry no quantiles. Do not fabricate a median for them."""
    old = [{k: v for k, v in r.items()
            if not k.startswith(("football_p", "market_p50", "final_p50"))} for r in _many_sim_rows(2)]
    assert all("football_p50" not in r for r in old)
    view = sim_block.game_view(old, {"sim_version": "sim-1.0.0", "run_id": "r"})
    for p in view["player_projections"]:
        assert p["distribution_quantiles_available"] is False
        assert p["football_p50"] is None, "a median must never be inferred for an artifact that has none"
        assert p["football_mean"] is not None, "the fields the old artifact DOES carry are still reported"
    assert view["distribution_quantiles_available"] is False
    md = render_game_markdown(_game_with(old))
    assert "predates sim-1.1.0 and does not report distribution quantiles" in md
    assert "no median has been inferred for it" in md
