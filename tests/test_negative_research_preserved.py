"""The conclusions this project reached the hard way, pinned so no later session can quietly undo them.

Negative results are the most valuable and the most fragile output this research program has. They cost
weeks, they are unglamorous, and every one of them is one plausible-looking edit away from being reversed by
somebody who did not run the study. A hardening session is exactly when that risk is highest: it touches the
write path, the fee engine and the scorecard, and any of those could reactivate a disabled feature or start
implying an edge the model has not demonstrated.

So this file asserts the SETTLED STATE. It is not testing behaviour; it is testing that nothing moved.

The decisions, from research/ and the frozen Week-1 artifacts:

  1. The independent game model does not beat contemporaneous Kalshi.
  2. Role features failed to transfer to the traded population (H-022) and are OFF by default.
  3. The tail calibrator is NOT deployed.
  4. Passive execution is rejected on core game markets by research/passive (Milestone K).
     NOT by H-019, which is the favourite/longshot hypothesis; H-023 is the prospective
     prop-book passive question and is also not the game-market result.
  5. Disagreement is not called edge, anywhere, in any label.
  6. No real-money validation has been earned.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(*parts):
    with open(os.path.join(ROOT, *parts)) as f:
        return f.read()


def load(*parts):
    return json.loads(read(*parts))


# ---- 2. role features are OFF by default -----------------------------------------------------------

def test_role_features_default_to_off():
    """H-022: validated on the full population, worth ~0 or negative on the contracts Kalshi lists."""
    src = read("nfl_edge", "shadow", "models.py")
    assert re.search(r'config\.get\(\s*["\']use_role_features["\']\s*,\s*False\s*\)', src), \
        "use_role_features must default to False; a truthy default silently re-enables H-022's failure"


def test_the_role_transfer_failure_is_still_registered():
    h = load("research", "hypothesis_registry", "H-20260904-022.json")
    assert h["status"] == "REGISTERED_PROSPECTIVE"
    assert "attenuate toward zero or reverse" in h["expected_direction"]
    assert "should NOT be assumed to survive" in h["expected_direction"]


def test_no_code_path_turns_role_features_on_by_default():
    """A default buried in a config file counts as turning them on."""
    for dirpath, _dirs, files in os.walk(os.path.join(ROOT, "config")):
        for fn in files:
            if not fn.endswith(".json"):
                continue
            with open(os.path.join(dirpath, fn)) as f:
                blob = f.read()
            assert '"use_role_features": true' not in blob.replace(" ", "").replace('":true', '": true'), \
                f"config/{fn} enables role features"


# ---- 3. the calibrator is not deployed -------------------------------------------------------------

def test_the_tail_calibrator_is_not_wired_into_the_shadow_pricer():
    """It exists, it is not used. The distinction is the whole point of H-022's third finding."""
    src = read("nfl_edge", "shadow", "models.py")
    assert "LadderCalibrator(" not in src, \
        "the shadow pricer must not instantiate the calibrator; it is not deployed"


def test_the_calibration_module_documents_why_it_is_not_deployed():
    src = read("nfl_edge", "pricing", "calibration.py")
    assert "tail_calibration" in src, "the calibrator must keep its provenance pointer"


# ---- 4. passive execution rejected -----------------------------------------------------------------

def test_the_passive_rejection_is_attributed_to_the_study_that_produced_it():
    """Governance hygiene, and it is not pedantry.

    Passive execution on core game markets was rejected by the execution/microstructure work in
    research/passive (Milestone K): 86.2% of decision-time books are one cent wide so no passive level
    exists, trade-at-level runs 3.6-26.7% against ~99% touch, and reachable orders lose while unreachable
    ones win.

    H-019 is the favourite/longshot hypothesis on underdog moneylines. H-023 is the PROSPECTIVE prop-book
    passive question, still open. Neither is the game-market passive result.

    Citing a settled negative result to a live prospective hypothesis is how a registry stops meaning
    anything: it makes a finished finding look open and an open question look decided.
    """
    h019 = load("research", "hypothesis_registry", "H-20260904-019.json")
    assert "underdog" in h019["target"] and "settlement rate" in h019["target"], \
        "H-019 is the favourite/longshot hypothesis"
    assert "passive" not in h019["target"].lower()

    h023 = load("research", "hypothesis_registry", "H-20260904-023.json")
    assert "passive" in h023["rationale"].lower() and "prop" in h023["target"].lower(), \
        "H-023 is the prospective PROP-book passive question"

    # Nothing in the codebase may credit the game-market passive rejection to H-019.
    offenders = []
    for sub in ("nfl_edge", "scripts", "docs", "tests"):
        base = os.path.join(ROOT, sub)
        for dirpath, _dirs, files in os.walk(base):
            if "hypothesis_registry" in dirpath:
                continue
            for fn in files:
                if not fn.endswith((".py", ".md")):
                    continue
                path = os.path.join(dirpath, fn)
                with open(path) as f:
                    for i, line in enumerate(f, 1):
                        low = line.lower()
                        if "h-019" in low and "passive" in low and "not" not in low:
                            offenders.append(f"{os.path.relpath(path, ROOT)}:{i}: {line.strip()[:100]}")
    assert not offenders, ("the game-market passive rejection is research/passive (Milestone K), not "
                           f"H-019: {offenders}")


def test_h019_remains_registered_and_unresolved():
    """Separately: H-019 itself is still an open prospective hypothesis and must stay one."""
    h = load("research", "hypothesis_registry", "H-20260904-019.json")
    assert h["status"] == "REGISTERED_PROSPECTIVE"
    assert h["oos_result"] is None


def test_h023_remains_registered_and_unresolved():
    h = load("research", "hypothesis_registry", "H-20260904-023.json")
    assert h["status"] == "REGISTERED_PROSPECTIVE"
    assert h["oos_result"] is None


def test_the_headline_markets_still_charge_a_maker_fee():
    """The fact that made passive entry unattractive. If it changed, research/passive needs re-running."""
    reg = load("config", "kalshi_nfl_series.json")["series"]
    for s in ("KXNFLGAME", "KXNFLSPREAD", "KXNFLTOTAL"):
        assert reg[s]["fee_type"] == "quadratic_with_maker_fees", \
            f"{s} no longer charges a maker fee; the passive study's premise has changed"


def test_the_frozen_passive_fee_sweep_is_unchanged():
    """The study's published numbers must keep reproducing exactly after this session's fee rewrite."""
    from nfl_edge.execution.fees import MAKER_FEE_SWEEP
    assert MAKER_FEE_SWEEP == (0.0, 0.0025, 0.005, 0.01)


# ---- 5. disagreement is never called edge ----------------------------------------------------------

def test_the_packet_labels_disagreement_as_disagreement():
    src = read("nfl_edge", "handicap", "packet.py")
    assert "DISAGREEMENT ONLY -- REQUIRES HANDICAP" in src
    assert "disagreement_vs_mid" in src and "disagreement_yes_executable" in src


def test_no_module_names_a_model_minus_market_quantity_edge():
    """`edge` as a variable name for model-minus-market is how a disagreement becomes a claim."""
    offenders = []
    for sub in ("nfl_edge/handicap", "nfl_edge/shadow", "nfl_edge/execution"):
        for dirpath, _dirs, files in os.walk(os.path.join(ROOT, sub)):
            for fn in files:
                if not fn.endswith(".py"):
                    continue
                path = os.path.join(dirpath, fn)
                with open(path) as f:
                    for i, line in enumerate(f, 1):
                        if re.search(r"\b(model_edge|edge_vs_market|market_edge)\b", line):
                            offenders.append(f"{os.path.relpath(path, ROOT)}:{i}")
    assert not offenders, f"model-minus-market must not be named 'edge': {offenders}"


def test_gross_edge_is_scoped_to_transaction_cost_arithmetic_only():
    """`gross_edge` is legitimate: it is fair-minus-price INSIDE the cost calculation, and it says so."""
    src = read("nfl_edge", "execution", "fees.py")
    assert "fair probability minus the price actually payable" in src
    assert "gross_edge" not in read("nfl_edge", "handicap", "packet.py"), \
        "the packet must not carry a field named gross_edge; that vocabulary belongs to the cost layer"


# ---- 6. no real-money validation has been earned ---------------------------------------------------

def test_the_week1_freeze_still_says_real_money_is_not_validated():
    f = load("research", "FREEZE_WEEK1_2026.json")
    assert f["real_money_status"].startswith("NOT VALIDATED")
    assert "no real-money authorization" in f["real_money_status"]


def test_no_module_claims_the_model_has_demonstrated_an_edge():
    banned = re.compile(r"(model (has|is) (a |an )?(proven|demonstrated|validated) edge"
                        r"|beats the market|profitable strategy)", re.I)
    hits = []
    for sub in ("nfl_edge", "scripts"):
        for dirpath, _dirs, files in os.walk(os.path.join(ROOT, sub)):
            for fn in files:
                if not fn.endswith(".py"):
                    continue
                path = os.path.join(dirpath, fn)
                with open(path) as f:
                    for i, line in enumerate(f, 1):
                        if banned.search(line):
                            hits.append(f"{os.path.relpath(path, ROOT)}:{i}: {line.strip()[:90]}")
    assert not hits, f"code implies a demonstrated edge: {hits}"


def test_nothing_places_or_automates_a_wager():
    """The Kalshi client is read-only and has no order surface. That is a standing constraint."""
    src = read("nfl_edge", "kalshi", "client.py")
    assert "No auth, no order surface" in src
    for banned in ("create_order", "place_order", "def order(", "portfolio/orders"):
        assert banned not in src, f"the client gained an order surface: {banned}"


# ---- 7 & 8. frozen artifacts and the no-backfill rule ----------------------------------------------

def test_the_freeze_files_forbid_their_own_overwrite():
    for name in ("FREEZE_WEEK1_2026.json", "FREEZE_2026-09-04.json"):
        f = load("research", name)
        assert "never an overwrite" in f["rule"], f"{name} lost its no-overwrite rule"


def test_the_week1_freeze_still_describes_the_model_it_froze():
    f = load("research", "FREEZE_WEEK1_2026.json")
    assert f["model"]["version"] == "shadow-0.3.0"
    assert f["model"]["artifact_sha"] == "76facd384b51e817", \
        "the frozen Week-1 artifact hash changed; the frozen predictions no longer reproduce"
    assert f["frozen_at"] < f["first_2026_kickoff"], "the freeze must predate the first 2026 kickoff"


def test_the_anti_backfill_rule_still_binds():
    """No reconstructed historical picks. The bridge judges every payload against Airtable's createdTime."""
    from nfl_edge.handicap import airtable_bridge as AB
    assert AB.MAX_HANDICAP_LEAD.total_seconds() <= 24 * 3600, \
        "the backward tolerance must stay at 24h or tighter, or backfill becomes possible"
    assert "The anti-backfill rule" in read("nfl_edge", "handicap", "airtable_bridge.py")


def test_pass_is_still_a_first_class_decision():
    from nfl_edge.handicap import schema as S
    assert S.PASS in S.DECISIONS
    for tag in ("MARKET_ALREADY_PRICED", "PRICE_TOO_EXPENSIVE", "AWAIT_INACTIVE_RELEASE"):
        assert tag in S.CORE_REASONING_TAGS
    assert "PASS records are carried through the same pipeline" in read("nfl_edge", "handicap",
                                                                        "scorecard.py")


def test_the_new_gates_did_not_make_pass_harder_to_record():
    """Tightening RECOMMENDED must not have tightened PASS. Cheap passes are the control group."""
    from nfl_edge.handicap import schema as S
    minimal_pass = {
        "recommendation_id": "rec_p", "created_at": "2026-09-07T00:00:00+00:00",
        "handicap_run_id": "r", "market_ticker": "KXNFLGAME-26SEP09NESEA-SEA",
        "decision": S.PASS, "side": "YES", "grade": "PASS",
        "primary_thesis": "the price already reflects the news",
    }
    assert S.validate_recommendation(minimal_pass) == []


def test_no_frozen_week1_code_artifact_was_modified_by_later_work():
    """The Week-1 freeze names the exact modules its predictions were produced by.

    Those predictions are scored against THAT model. Editing any of the named files -- even harmlessly, even
    for a hardening session -- would mean the frozen predictions no longer reproduce from the frozen code,
    and the freeze would be a claim rather than a fact. A later change requires a NEW freeze file.

    Compared against the merge-base with the default branch, so the test asks "did this line of work touch
    them", which is the question, rather than "have they ever changed".
    """
    import subprocess
    f = load("research", "FREEZE_WEEK1_2026.json")
    frozen = list(f["code"])

    base = subprocess.run(["git", "merge-base", "HEAD", "origin/main"],
                          cwd=ROOT, capture_output=True, text=True)
    if base.returncode != 0:
        import pytest
        pytest.skip("no origin/main to compare against in this checkout")
    changed = subprocess.run(["git", "diff", "--name-only", f"{base.stdout.strip()}..HEAD"],
                             cwd=ROOT, capture_output=True, text=True).stdout.split()
    touched = sorted(set(frozen) & set(changed))
    assert not touched, (
        f"frozen Week-1 code artifacts were modified: {touched}. The frozen predictions are scored against "
        "this exact code; a change requires a new freeze file, never an edit to these.")
