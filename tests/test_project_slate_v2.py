"""The v2 slate projector's gates: post-kickoff and hindsight refusals, shadow-only states, isolation from the incumbent."""
import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.projection import record as R                                                  # noqa: E402
from nfl_edge.projection.store import DIRNAME                                                 # noqa: E402
from nfl_edge.semantics import catalog as CAT                                                 # noqa: E402
from nfl_edge.semantics.questions import EVENT, GAME, NONE, PERIOD, PROVEN, LIKELY, AMBIGUOUS, THRESHOLD, Question  # noqa: E402


def _load():
    spec = importlib.util.spec_from_file_location("project_slate_v2", os.path.join(ROOT, "scripts", "shadow_v2", "project_slate_v2.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


P = _load()
ENTRY_PRICED = CAT.catalog_entry("TOTAL", "FULL")
ENTRY_PERIOD = CAT.catalog_entry("TOTAL", "1H")
Q_TOTAL = Question(kind=THRESHOLD, engine=GAME, stat="total", period="FULL", op=">=", k=45, semantic_confidence=PROVEN)
Q_1H = Question(kind=THRESHOLD, engine=PERIOD, stat="total", period="1H", op=">=", k=22, semantic_confidence=PROVEN)


def test_post_kickoff_observation_or_generation_never_carries_a_probability():
    st, reason, p, cv = P.support_state(Q_TOTAL, ENTRY_PRICED, pregame=False, confirmed=True, answer={"p_yes": 0.5}, generated_before_kickoff=True, allow_historical=False)
    assert st == R.POST_KICKOFF and p is None
    st, reason, p, cv = P.support_state(Q_TOTAL, ENTRY_PRICED, pregame=True, confirmed=True, answer={"p_yes": 0.5}, generated_before_kickoff=False, allow_historical=False)
    assert st == R.POST_KICKOFF and "hindsight" in reason and p is None
    st, *_ = P.support_state(Q_TOTAL, ENTRY_PRICED, pregame=True, confirmed=True, answer={"p_yes": 0.5}, generated_before_kickoff=False, allow_historical=True)
    assert st == R.PRICED, "an explicitly historical local run is allowed a probability, labelled HISTORICAL_RESEARCH by the caller"


def test_only_proven_semantics_on_a_validated_engine_is_priced_everything_else_is_shadow():
    assert P.support_state(Q_TOTAL, ENTRY_PRICED, pregame=True, confirmed=True, answer={"p_yes": 0.5}, generated_before_kickoff=True, allow_historical=False)[0] == R.PRICED
    st, reason, p, _ = P.support_state(Q_1H, ENTRY_PERIOD, pregame=True, confirmed=True, answer={"p_yes": 0.5, "validated": False}, generated_before_kickoff=True, allow_historical=False)
    assert st == R.PROJECTABLE_NOT_YET_VALIDATED and p == 0.5
    likely = Question(kind=THRESHOLD, engine=GAME, stat="total", period="FULL", op=">=", k=45, semantic_confidence=LIKELY)
    assert P.support_state(likely, ENTRY_PRICED, pregame=True, confirmed=True, answer={"p_yes": 0.5}, generated_before_kickoff=True, allow_historical=False)[0] == R.PROJECTABLE_NOT_YET_VALIDATED
    amb = Question(kind=THRESHOLD, engine=GAME, stat="total", period="FULL", op=">=", k=45, semantic_confidence=AMBIGUOUS, notes=("two readings",))
    st, reason, p, _ = P.support_state(amb, ENTRY_PRICED, pregame=True, confirmed=True, answer={"p_yes": 0.5}, generated_before_kickoff=True, allow_historical=False)
    assert st == R.SEMANTICS_AMBIGUOUS and p is None and "two readings" in reason
    none = Question(kind=EVENT, engine=NONE, event="COACH_FIRED", semantic_confidence=LIKELY)
    st, *_ = P.support_state(none, CAT.catalog_entry("COACH_FIRED", "EVENT"), pregame=True, confirmed=True, answer=None, generated_before_kickoff=True, allow_historical=False)
    assert st in (R.NON_FOOTBALL_MODEL, R.UNSUPPORTED, R.RESEARCH_REQUIRED, R.DATA_UNAVAILABLE)


def test_unconfirmed_series_and_engine_refusals_are_named_states_without_probabilities():
    st, reason, p, _ = P.support_state(Q_TOTAL, ENTRY_PRICED, pregame=True, confirmed=False, answer={"p_yes": 0.5}, generated_before_kickoff=True, allow_historical=False)
    assert st == R.STALE_MARKET and p is None
    st, reason, p, _ = P.support_state(Q_TOTAL, ENTRY_PRICED, pregame=True, confirmed=True, answer={"p_yes": None, "reason": "no env", "status": "DATA_UNAVAILABLE"}, generated_before_kickoff=True, allow_historical=False)
    assert st == R.DATA_UNAVAILABLE and reason == "no env"
    st, *_ = P.support_state(Q_TOTAL, ENTRY_PRICED, pregame=True, confirmed=True, answer={"p_yes": None, "status": "JOINT_MODEL_REQUIRED", "reason": "x"}, generated_before_kickoff=True, allow_historical=False)
    assert st == R.JOINT_MODEL_REQUIRED


def test_v2_writes_only_under_its_own_tree_and_never_imports_the_incumbent_pricer():
    assert DIRNAME.replace(os.sep, "/") == "shadow/v2/projections"
    src = open(os.path.join(ROOT, "scripts", "shadow_v2", "project_slate_v2.py")).read()
    assert "scripts.shadow.price_slate" not in src and "price_slate" not in src
    assert "data/shadow/ledger" not in src and "LedgerWriter" not in src
    for frozen in ("nfl_edge.handicap.gates", "nfl_edge.handicap.risk", "nfl_edge.handicap.preflight", "risk_policy.json", "nfl_edge.shadow.ledger"):
        assert frozen not in src, f"v2 must not import or read {frozen}"
    assert P.PLAYER_ARMS == ("DATA_PLAYER_DIST", "MARKET_PLAYER_DIST", "HYBRID_PLAYER_DIST")
