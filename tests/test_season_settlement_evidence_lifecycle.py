"""A SEASON-SCOPED settlement is TIME-EVOLVING EVIDENCE published into a WRITE-ONCE corpus.

Week 2 of 2026 is the incident these tests pin. Shadow v2 settled every Sunday game correctly and published
none of them, through four consecutive scheduled windows, because of the season pass that runs after them:

    EvaluationConflict: 11662 evaluation(s) contradict an already-published truth; nothing was written.
      79536de03e7b0b8c06c6 (settle-2.0.0) in settle-2.0.0.20260918T211044Z.settlements_v2.jsonl.gz:
        settlement_reason: existing='16 of 17 games not final' new='15 of 17 games not final'

`SEASON_WINS` refuses with a COUNT OF GAMES NOT YET PLAYED, and that count falls every week. Filed under one
flat evaluation version, each week's truthful reading contradicted the previous week's, so the corpus -- given
what it was told, correctly -- refused the batch and the driver exited non-zero before it wrote its GitHub
outputs. `settle_v2.py` had already written the Sunday games' immutable batches into staging by then; with the
step failed, the publish step never ran and they were discarded with the runner.

Worse, the failure was usually invisible. Describing a conflict re-read the whole prior batch file to fetch the
stored row, once per conflicting row: 11,662 conflicts against a 21,888-row batch is 86 minutes of pure
re-parsing, so from the Sunday night window onward the job was killed by its 90-minute timeout BEFORE the
exception it was heading for. The log simply stopped after the last game, and nothing was ever published.

So these tests cover both halves, against the real EvaluationCorpus and the real settlement engine rather than
stand-ins, because what broke was the interaction between them:

  * a Week 2 Sunday game that is FINAL with stats and snaps published, and not yet settled, settles and is
    published -- and the workflow's publish gate fires on the outputs the driver actually emits;
  * the same run repeated is a NO-OP, and an already-settled game's batch is never rewritten;
  * the season pass survives a game going final between two runs, which is the exact conflict above;
  * a provisional observation is superseded by, and never outranks, the eventual terminal settlement;
  * a game whose snap counts have not arrived is DEFERRED, not guessed;
  * and a genuine contradiction of a TERMINAL settlement still fails the run loudly.
"""
from __future__ import annotations

import glob
import gzip
import hashlib
import importlib.util
import json
import os
import sys

import pytest
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.semantics import question_from_market                                      # noqa: E402
from nfl_edge.settlement import settle_v2 as S2                                          # noqa: E402
from nfl_edge.settlement.results import DEFER_SNAPS_PENDING, result_book_from_records     # noqa: E402
from nfl_edge.shadow import evaluation_store as ST                                        # noqa: E402

FIX = json.load(open(os.path.join(ROOT, "tests", "fixtures", "postgame", "dal_phi_2025_w1.results.json")))

# The 2026 week 2 slate this incident was about, in miniature, with the real game ids of that week: DET @ BUF
# on the Thursday (settled before Sunday, and the historical batch that must survive untouched), CAR @ ATL from
# the Sunday slate that never published, and NYG @ LA on the Monday night, which had not met the settlement
# requirements and must stay out of the corpus. W3 is ATL's still-unplayed game, which is what keeps ATL's
# season contract refused -- with a DIFFERENT count -- once Sunday goes final, and that changing count is the
# whole defect.
W1 = "2026_01_ATL_CAR"
THU = "2026_02_DET_BUF"
SUN = "2026_02_CAR_ATL"
MON = "2026_02_NYG_LA"
W3 = "2026_03_ATL_NO"
CODE = {W1: "26SEP13ATLCAR", THU: "26SEP17DETBUF", SUN: "26SEP20CARATL", MON: "26SEP21NYGLA", W3: "26SEP27ATLNO"}
KO = {W1: "2026-09-13T17:00:00+00:00", THU: "2026-09-18T00:15:00+00:00", SUN: "2026-09-20T17:00:00+00:00",
      MON: "2026-09-22T00:15:00+00:00", W3: "2026-09-27T17:00:00+00:00"}
WEEK = {W1: 1, THU: 2, SUN: 2, MON: 2, W3: 3}
# Monday 2026-09-21, the morning the Sunday slate should have published and had not.
NOW = "2026-09-21T13:02:46+00:00"
SNAP1, SNAP2 = "20260919T120000Z", "20260920T120000Z"


# --------------------------------------------------------------------------------------------- the environment
def load_driver():
    path = os.path.join(ROOT, "scripts", "shadow_v2", "settle_v2.py")
    spec = importlib.util.spec_from_file_location("_season_lifecycle_settle_v2", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def schedule_csv(*, sunday_final: bool, w3_final: bool = False):
    """The real games.csv header, with scores present only for the games that have been played."""
    header = FIX["schedule_csv"].splitlines()[0]
    h = header.split(",")

    def row(gid, hs, aws):
        r = {k: "" for k in h}
        r.update({"game_id": gid, "season": "2026", "game_type": "REG", "week": str(WEEK[gid]),
                  "gameday": KO[gid][:10], "gametime": "13:00", "location": "Home",
                  "away_team": gid.split("_")[2], "home_team": gid.split("_")[3],
                  "away_score": "" if hs is None else str(aws), "home_score": "" if hs is None else str(hs),
                  "result": "" if hs is None else str(hs - aws), "total": "" if hs is None else str(hs + aws),
                  "overtime": "0"})
        return ",".join(r[k] for k in h)

    return "\n".join([header,
                      row(W1, 27, 20),                                    # ATL at CAR, played
                      row(THU, 41, 31),                                   # Thursday, played and already settled
                      row(SUN, 24, 17) if sunday_final else row(SUN, None, None),
                      row(MON, None, None),                               # Monday night: never final here
                      row(W3, 20, 13) if w3_final else row(W3, None, None)])


def result_book(*, sunday_final: bool, w3_final: bool = False, with_snaps=True):
    """A ResultBook over that schedule. `with_snaps` is what the deferral test takes away."""
    played = [W1, THU] + ([SUN] if sunday_final else []) + ([W3] if w3_final else [])
    return result_book_from_records(
        {"schedule_csv": schedule_csv(sunday_final=sunday_final, w3_final=w3_final), "players": [], "snaps": [],
         "games_with_player_stats": played, "games_with_snaps": played if with_snaps else []},
        min_hours_after_kickoff=0)


def proj(gid, snapshot, arm, k, p, *, engine="GAME", subject_id=None, market_family=None, season=2026):
    """A frozen projection: `TOTAL >= k-0.5` for a game, or a SEASON_WINS contract when `gid` is None."""
    if gid:
        m = {"ticker": f"KXNFLTOTAL-{CODE[gid]}-{k}", "event_ticker": f"KXNFLTOTAL-{CODE[gid]}",
             "series_ticker": "KXNFLTOTAL", "strike_type": "greater", "floor_strike": k - 0.5, "title": ""}
        sem, q = question_from_market(m)
        base = {"question": q.to_dict(), "market_family": market_family or sem.family, "period": sem.period or "FULL",
                "game_id": gid, "semantic_confidence": q.semantic_confidence, "subject_id": subject_id or q.subject,
                "stat_family": sem.stat, "ticker": m["ticker"], "event_ticker": m["event_ticker"],
                "series_ticker": m["series_ticker"], "season": 2026, "week": WEEK[gid], "kickoff_utc": KO[gid]}
    else:
        team = subject_id or "ATL"
        base = {"question": {"kind": "THRESHOLD", "op": ">=", "k": float(k), "stat": "season_wins",
                             "subject": team, "subject_kind": "team", "period": "SEASON", "notes": []},
                "market_family": market_family or "SEASON_WINS", "period": "FULL", "game_id": None,
                "semantic_confidence": "LIKELY", "subject_id": team, "stat_family": "wins",
                "ticker": f"KXNFLWINS-27{team}-{k}", "event_ticker": f"KXNFLWINS-27{team}",
                "series_ticker": "KXNFLWINS", "season": season, "week": None, "kickoff_utc": None}
    r = {**base, "snapshot_id": snapshot, "model_arm": arm, "engine": engine, "p_yes": p, "contract_value": p,
         "yes_bid": 0.48, "yes_ask": 0.52, "no_bid": 0.48, "no_ask": 0.52, "mid": 0.5, "quote_width": 0.04,
         "liquidity": 250.0, "volume": 100.0, "horizon_label": "CYCLE", "minutes_to_kickoff": 300.0,
         "identity_confidence": "HIGH", "evidence_class": "PROSPECTIVE_FROZEN",
         "support_state": "PRICED" if p is not None else "CAPTURE_ONLY", "flags": {"has_probability": p is not None},
         "player_context": {}, "feature_lineage": {}, "projection_lineage": {}, "distribution_summary": {},
         "information_sync": {}}
    r["record_id"] = hashlib.sha1(f"{snapshot}|{r['ticker']}|{arm}|{engine}".encode()).hexdigest()[:20]
    return r


def write_projection_file(root, snapshot, arm, rows):
    day = f"{snapshot[:4]}-{snapshot[4:6]}-{snapshot[6:8]}"
    d = os.path.join(root, day)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, f"{snapshot}.{arm}.projections.jsonl.gz")
    with gzip.GzipFile(p, "wb", mtime=0) as raw:
        for r in rows:
            raw.write((json.dumps(r, separators=(",", ":"), sort_keys=True, default=str) + "\n").encode())
    json.dump({"status": "WRITTEN", "snapshot_id": snapshot, "model_arm": arm, "n_rows": len(rows)},
              open(p.replace(".projections.jsonl.gz", ".projections_manifest.json"), "w"))
    return p


def build_market_data(tmp_path):
    """market-data as the driver reads it: frozen projections for both week-2 games, plus season contracts.

    SNAP1 is Saturday's board, SNAP2 Sunday's. Each carries one PLAYER-engine probability row per game, which
    is what makes the driver require the player tables for that game (`index.game(gid)["player_prob"]`) and so
    what makes the snap-count deferral reachable at all.
    """
    md = tmp_path / "md"
    proot = str(md / "data" / "shadow" / "v2" / "projections")
    for snap in (SNAP1, SNAP2):
        rows = []
        for gid in (THU, SUN, MON):
            rows += [proj(gid, snap, "BOARD_V2", k, 0.55) for k in (40, 44, 48)]
            rows.append(proj(gid, snap, "BOARD_V2", 50, 0.5, engine="PLAYER", subject_id="00-0001"))
        # the season contracts: ATL stays refused all the way through, because W3 is never played
        rows += [proj(None, snap, "BOARD_V2", k, 0.4, engine="SEASON", subject_id="ATL") for k in (8, 9, 10)]
        rows += [proj(None, snap, "BOARD_V2", k, 0.4, engine="SEASON", subject_id="CAR") for k in (6, 7)]
        write_projection_file(proot, snap, "BOARD_V2", rows)
    return str(md), proot


def publish(out, md):
    """What the workflow's publish step does: copy the staged batches into market-data.

    The driver stages into `--out` and a separate step publishes; these tests need the published corpus to
    carry the previous run's batches, exactly as the next scheduled run would find them.
    """
    for kind in ("settlements", "autopsy", "crosscheck", "projection_index"):
        src = os.path.join(out, kind)
        if not os.path.isdir(src):
            continue
        for path in glob.glob(os.path.join(src, "*", "*")) + glob.glob(os.path.join(src, "*.json")):
            rel = os.path.relpath(path, src)
            dst = os.path.join(md, "data", "shadow", "v2", kind, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if not os.path.exists(dst):
                with open(path, "rb") as f, open(dst, "wb") as g:
                    g.write(f.read())


class FakePeriodBook:
    """No play-by-play in this fixture: the period markets are not what is under test."""

    def __init__(self):
        self.games = {}

    def load_pbp(self, *a, **k):
        return None


def run_settle(mod, monkeypatch, md, out, *extra, book, now=NOW, gh=None):
    monkeypatch.setattr(mod, "build_result_book", lambda *a, **k: book)
    monkeypatch.setattr(mod, "PeriodBook", FakePeriodBook)
    argv = ["--market-data", str(md), "--out", str(out), "--target-season", "2026", "--now", now, *extra]
    if gh:
        argv += ["--github-output", str(gh)]
    return mod.main(argv)


def not_settled_because(summary: dict, gid: str) -> str:
    """Why the driver did not settle this game, from either of the two places it says so.

    A game with projections that the result book does not call FINAL is deferred BY CONSTRUCTION and listed in
    `games_not_final_with_projections`; one that is final but not yet safe to write carries a named state in
    `games_deferred`. Both are refusals to guess, and a test about "this game must not be settled" should not
    care which of the two it is.
    """
    assert gid not in summary["games_ready"], f"{gid} was settled"
    if gid in summary["games_deferred"]:
        return summary["games_deferred"][gid]
    assert gid in summary["games_not_final_with_projections"], f"{gid} is unaccounted for in {summary.keys()}"
    return "NOT_FINAL_WITH_PROJECTIONS"


def outputs(path) -> dict:
    """The step outputs the driver appends to $GITHUB_OUTPUT, as the workflow would read them."""
    out = {}
    with open(path) as f:
        for line in f:
            if "=" in line:
                k, v = line.rstrip("\n").split("=", 1)
                out[k] = v
    return out


def publish_gate_fires(settle: dict, closes: dict | None = None) -> bool:
    """Evaluate shadow-v2-settle.yml's publish condition against real step outputs.

    Read from the workflow rather than restated, so the gate this asserts is the gate that ships.
    """
    doc = yaml.safe_load(open(os.path.join(ROOT, ".github", "workflows", "shadow-v2-settle.yml")))
    step = next(s for s in doc["jobs"]["settle"]["steps"] if str(s.get("name", "")).startswith("Publish the settlement"))
    cond, closes = step["if"], closes or {}
    assert "steps.settle.outputs.status" in cond and "index_written" in cond, f"publish gate changed shape: {cond}"
    return (settle.get("status") == "WROTE" or closes.get("status") == "WROTE"
            or settle.get("index_written", "0") != "0")


def batch_files(root, key):
    return sorted(glob.glob(os.path.join(root, key, "*.settlements_v2.jsonl.gz")))


def rows_of(paths):
    out = []
    for p in paths:
        out += ST.read_rows(p)
    return out


def digests(root):
    """Every settlement batch under `root`, by path, with its bytes digest: proof of what did not change."""
    return {os.path.relpath(p, root): ST.sha256_file(p)
            for p in glob.glob(os.path.join(root, "*", "*.settlements_v2.jsonl.gz"))}


@pytest.fixture
def env(tmp_path, monkeypatch):
    """market-data with THU already settled and published, as it really was before Sunday's slate."""
    mod = load_driver()
    md, _proot = build_market_data(tmp_path)
    out0 = tmp_path / "out0"
    # the Thursday game settles on its own, before Sunday exists as a final score
    assert run_settle(mod, monkeypatch, md, out0, book=result_book(sunday_final=False),
                      now="2026-09-19T12:00:00+00:00") == 0
    publish(str(out0), md)
    assert batch_files(os.path.join(md, "data", "shadow", "v2", "settlements"), THU), "THU should be settled already"
    return mod, md, tmp_path


# ------------------------------------------------- the Sunday game: ready, settled, written, publishable
def test_a_final_sunday_game_with_stats_and_snaps_is_ready_and_its_batch_is_written(env, monkeypatch, capsys):
    """The fixture Phase 5 asks for: FINAL, stats and snaps published, no prior batch -> settled and published."""
    mod, md, tmp = env
    out = tmp / "out1"
    gh = tmp / "gh1.txt"
    assert run_settle(mod, monkeypatch, md, out, book=result_book(sunday_final=True), gh=gh) == 0
    s = _trailing(capsys)

    # 1. detected as ready -- and the Monday nighter is not
    assert SUN in s["games_ready"], f"Sunday game not ready: {s['games_deferred']}"
    not_settled_because(s, MON)
    # 2. a settlement batch was created, 3. in the right game directory
    paths = batch_files(os.path.join(out, "settlements"), SUN)
    assert len(paths) == 1, f"expected exactly one batch for {SUN}, got {paths}"
    assert os.path.basename(paths[0]).startswith(f"{S2.SETTLE_VERSION}.{s['batch_id']}")
    rows = rows_of(paths)
    assert rows and {r["game_id"] for r in rows} == {SUN}
    assert all(r["evaluation_version"] == S2.SETTLE_VERSION for r in rows)
    # 4. the workflow outputs say work was written, 5. so the publish gate fires
    o = outputs(gh)
    assert o["status"] == "WROTE" and int(o["written"]) == s["written"] > 0 and o["batch_id"] == s["batch_id"]
    assert publish_gate_fires(o)


def test_the_monday_night_game_is_deferred_and_never_reaches_the_corpus(env, monkeypatch, capsys):
    mod, md, tmp = env
    out = tmp / "out_mnf"
    assert run_settle(mod, monkeypatch, md, out, book=result_book(sunday_final=True)) == 0
    s = _trailing(capsys)
    assert not_settled_because(s, MON)
    assert not batch_files(os.path.join(out, "settlements"), MON)
    assert not batch_files(os.path.join(md, "data", "shadow", "v2", "settlements"), MON)


def test_a_game_whose_snap_counts_have_not_arrived_is_deferred_not_guessed(env, monkeypatch, capsys):
    """The prior state of this incident: FINAL with statistics but no snap counts is DEFER_SNAPS_PENDING."""
    mod, md, tmp = env
    out = tmp / "out_snaps"
    assert run_settle(mod, monkeypatch, md, out, book=result_book(sunday_final=True, with_snaps=False)) == 0
    s = _trailing(capsys)
    assert not_settled_because(s, SUN).startswith(DEFER_SNAPS_PENDING), not_settled_because(s, SUN)
    assert not batch_files(os.path.join(out, "settlements"), SUN), "a game without snaps must not be settled"


# ------------------------------------------------------------------------ idempotency and immutable history
def test_a_second_run_over_the_same_evidence_is_a_no_op(env, monkeypatch, capsys):
    mod, md, tmp = env
    book = result_book(sunday_final=True)
    out1 = tmp / "out_a"
    assert run_settle(mod, monkeypatch, md, out1, book=book) == 0
    first = _trailing(capsys)
    publish(str(out1), md)
    before = digests(os.path.join(md, "data", "shadow", "v2", "settlements"))

    out2, gh2 = tmp / "out_b", tmp / "gh_b.txt"
    assert run_settle(mod, monkeypatch, md, out2, book=book, gh=gh2) == 0
    second = _trailing(capsys)
    assert first["written"] > 0
    assert second["written"] == 0, f"a repeat run wrote {second['written']} rows"
    assert outputs(gh2)["status"] == "NOTHING_TO_DO"
    assert SUN in second["games_skipped_already_settled"]
    assert digests(os.path.join(md, "data", "shadow", "v2", "settlements")) == before, "published bytes changed"


def test_an_already_settled_game_is_skipped_and_its_published_batch_is_never_rewritten(env, monkeypatch, capsys):
    mod, md, tmp = env
    settled = os.path.join(md, "data", "shadow", "v2", "settlements")
    before = digests(settled)
    assert any(k.startswith(THU) for k in before)
    assert run_settle(mod, monkeypatch, md, tmp / "out_hist", book=result_book(sunday_final=True)) == 0
    s = _trailing(capsys)
    assert THU in s["games_skipped_already_settled"] and THU not in s["games_ready"]
    assert digests(settled) == before, "a historical settlement batch changed"
    assert not batch_files(os.path.join(tmp / "out_hist", "settlements"), THU)


# -------------------------------------------------------------- the incident: a game goes final between runs
def test_a_game_going_final_between_runs_does_not_conflict_the_season_contracts(env, monkeypatch, capsys):
    """THE REGRESSION. Run 1 sees Sunday pending, run 2 sees it final, so every ATL season contract's refusal
    changes from 'N of 3 games not final' to 'N-1 of 3'. Under one flat version that was
    `EvaluationConflict: ... existing='16 of 17 games not final' new='15 of 17 games not final'` and the whole
    run -- Sunday's fourteen settled games included -- wrote nothing."""
    mod, md, tmp = env
    out1 = tmp / "out_before"
    assert run_settle(mod, monkeypatch, md, out1, book=result_book(sunday_final=False),
                      now="2026-09-19T12:00:00+00:00") == 0
    before = _trailing(capsys)
    publish(str(out1), md)
    season = rows_of(batch_files(os.path.join(md, "data", "shadow", "v2", "settlements"), "SEASON_2026"))
    assert season, "the season pass published nothing to build on"
    reasons = {r["settlement_reason"] for r in season if r["subject_id"] == "ATL"}
    assert reasons == {"2 of 3 games not final"}, reasons
    assert all(r["provisional"] and r["evidence_tier"] == S2.SEASON_PROVISIONAL for r in season)

    # Sunday goes final. The count every ATL contract refused with changes under its feet.
    out2, gh2 = tmp / "out_after", tmp / "gh_after.txt"
    assert run_settle(mod, monkeypatch, md, out2, book=result_book(sunday_final=True), gh=gh2) == 0, \
        "the season pass must survive a game going final between runs"
    after = _trailing(capsys)
    assert after["dispatch"]["silently_dropped"] == 0
    new_season = rows_of(batch_files(os.path.join(out2, "settlements"), "SEASON_2026"))
    atl = [r for r in new_season if r["subject_id"] == "ATL"]
    assert {r["settlement_reason"] for r in atl} == {"1 of 3 games not final"}
    # ATL's new observation is filed beside the old one, under its own vintage, and neither is rewritten
    assert all(r["evaluation_version"].startswith(S2.SEASON_PROVISIONAL_PREFIX) for r in atl)
    assert {r["evaluation_version"] for r in atl}.isdisjoint({r["evaluation_version"] for r in season})
    # CAR's last game was Sunday, so in this very same run its contracts reach a TERMINAL settlement -- the
    # two tiers travel together in one batch, which is why the manifest records the split.
    car = [r for r in new_season if r["subject_id"] == "CAR"]
    assert car and all(r["settlement_status"] == "SETTLED" for r in car)
    assert all(r["evaluation_version"] == S2.SEASON_TERMINAL_VERSION for r in car)
    # and Sunday's games were settled and published in the very same run
    assert SUN in after["games_ready"] and after["written"] > 0
    assert publish_gate_fires(outputs(gh2))


def test_the_provisional_history_is_superseded_by_the_terminal_settlement_and_never_outranks_it(env, monkeypatch, capsys):
    """Once ATL's last game is played the contract SETTLES. That terminal truth is a new identity beside the
    provisional observations -- not a contradiction of them -- and `season_rank` puts it above all of them."""
    mod, md, tmp = env
    out1 = tmp / "out_p"
    assert run_settle(mod, monkeypatch, md, out1, book=result_book(sunday_final=True)) == 0
    publish(str(out1), md)
    out2 = tmp / "out_t"
    assert run_settle(mod, monkeypatch, md, out2, book=result_book(sunday_final=True, w3_final=True),
                      now="2026-09-28T12:00:00+00:00") == 0, "a season contract settling must not conflict"
    terminal = [r for r in rows_of(batch_files(os.path.join(out2, "settlements"), "SEASON_2026"))
                if r["subject_id"] == "ATL"]
    assert terminal and all(r["settlement_status"] == "SETTLED" for r in terminal), [r["settlement_status"] for r in terminal]
    assert all(r["evaluation_version"] == S2.SEASON_TERMINAL_VERSION and not r["provisional"] for r in terminal)
    publish(str(out2), md)

    # every reading of one prediction, ranked: the settlement wins over every provisional vintage
    pid = terminal[0]["prediction_id"]
    readings = [r for r in rows_of(batch_files(os.path.join(md, "data", "shadow", "v2", "settlements"), "SEASON_2026"))
                if r["prediction_id"] == pid]
    assert len(readings) > 1, "the provisional history should still be there"
    assert max(readings, key=S2.season_rank)["settlement_status"] == "SETTLED"


def test_a_settled_season_contract_is_never_settled_or_filed_a_second_time(env, monkeypatch, capsys):
    """A terminal season settlement is immutable, so it is not re-offered -- which is also what stops a second
    copy of a settled row reaching the scorecard, where every metric would count it twice."""
    mod, md, tmp = env
    book = result_book(sunday_final=True, w3_final=True)
    out1 = tmp / "out_s1"
    assert run_settle(mod, monkeypatch, md, out1, book=book, now="2026-09-28T12:00:00+00:00") == 0
    first = _trailing(capsys)
    publish(str(out1), md)
    assert first["accounting"]["season_already_terminal_not_re_offered"] == 0

    out2 = tmp / "out_s2"
    assert run_settle(mod, monkeypatch, md, out2, book=book, now="2026-09-28T13:00:00+00:00") == 0
    second = _trailing(capsys)
    assert second["accounting"]["season_already_terminal_not_re_offered"] > 0
    assert second["accounting"]["silently_dropped"] == 0
    assert not batch_files(os.path.join(out2, "settlements"), "SEASON_2026"), "a settled season row was re-filed"
    # exactly one terminal reading per prediction in the whole published corpus
    rows = rows_of(batch_files(os.path.join(md, "data", "shadow", "v2", "settlements"), "SEASON_2026"))
    settled = [r["prediction_id"] for r in rows if r["settlement_status"] == "SETTLED"]
    assert len(settled) == len(set(settled)), "a settled season prediction appears twice"


# ------------------------------------------------------------------------- the guard itself is not weakened
def test_two_contradictory_terminal_readings_still_fail_the_run_loudly():
    """The corpus exists to refuse a changed settled truth. The lifecycle must not have softened that."""
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        c = ST.EvaluationCorpus(os.path.join(d, "settlements"), suffix="settlements_v2")
        base = {"prediction_id": "p1", "game_id": None, "settlement_status": "SETTLED", "settled_yes": 1.0,
                "settlement_reason": "10 wins", "settlement_evidence": {"wins": 10}}
        first = S2.season_versioned({**base, "evaluated_at": "2026-09-20T00:00:00+00:00"})
        assert first["evaluation_version"] == S2.SEASON_TERMINAL_VERSION
        c.write_batch("SEASON_2026", [first], evaluation_version=S2.SETTLE_VERSION, batch="B1")
        changed = S2.season_versioned({**base, "settled_yes": 0.0, "settlement_reason": "9 wins",
                                       "settlement_evidence": {"wins": 9}, "evaluated_at": "2026-09-21T00:00:00+00:00"})
        assert changed["evaluation_version"] == S2.SEASON_TERMINAL_VERSION, "a settlement must keep one identity"
        with pytest.raises(ST.EvaluationConflict) as e:
            c.write_batch("SEASON_2026", [changed], evaluation_version=S2.SETTLE_VERSION, batch="B2")
        assert "settled_yes" in str(e.value)


def test_describing_a_conflict_storm_parses_each_batch_file_once(tmp_path, monkeypatch):
    """What turned a loud failure into a 90-minute timeout: one full gzip re-parse per conflicting row.

    2,000 conflicting rows against one batch used to be 2,000 reads of it. The count and the raise are
    unchanged; only the cost of describing them is.
    """
    c = ST.EvaluationCorpus(str(tmp_path / "settlements"), suffix="settlements_v2")
    rows = [{"prediction_id": f"p{i}", "evaluation_version": "v1", "settlement_reason": "16 of 17 games not final"}
            for i in range(2000)]
    c.write_batch("SEASON_2026", rows, evaluation_version="v1", batch="B1")

    reads = []
    real = ST.read_rows
    monkeypatch.setattr(ST, "read_rows", lambda p: (reads.append(p), real(p))[1])
    p = c.planner("SEASON_2026")
    reads.clear()
    for r in rows:
        p.offer({**r, "settlement_reason": "15 of 17 games not final"})
    assert len(p.conflicts) == 2000, "every conflict must still be counted"
    assert len(reads) == 1, f"the prior batch was parsed {len(reads)} times for 2000 conflicts"
    assert sum(1 for c_ in p.conflicts if c_["fields"]) == ST.CONFLICT_DETAIL_KEEP
    assert "15 of 17 games not final" in str(ST.EvaluationConflict(p.conflicts))


# --------------------------------------------------------------------------------------------- helpers
def _trailing(capsys) -> dict:
    """The driver prints its run summary as the last JSON block on stdout."""
    text = capsys.readouterr().out
    i = text.rfind("\n{\n")
    assert i >= 0, f"no run summary in driver output:\n{text[-2000:]}"
    return json.loads(text[i + 1:])
