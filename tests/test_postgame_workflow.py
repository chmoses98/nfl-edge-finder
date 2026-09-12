"""The postgame workflow's safety properties, checked as text because that is all a workflow is until it runs.

The general workflow tests (tests/test_workflows_parse.py) already prove every file parses, has pipefail where
it pipes, and calls scripts that exist. These are the properties specific to a job that publishes to an
immutable corpus:

  * the expensive steps are behind the cheap gate, or a 3-hourly poll downloads parquet to learn nothing;
  * nothing is published before it is validated;
  * the git identity exists before the first publish (the failure that silently lost shocks for days);
  * a conflict fails the run rather than being reported as a success with zero rows;
  * the job never writes to the ledger it reads.
"""
import os
import re

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, ".github", "workflows", "postgame-settle.yml")


def doc():
    with open(PATH) as f:
        return yaml.safe_load(f)


def steps():
    return doc()["jobs"]["settle"]["steps"]


def step_index(pattern):
    for i, s in enumerate(steps()):
        if re.search(pattern, (s.get("run") or "") + " " + str(s.get("uses") or "")):
            return i
    return None


def test_the_workflow_polls_on_a_schedule_and_can_be_run_by_hand():
    d = doc()
    on = d.get(True, d.get("on"))
    crons = [c["cron"] for c in on["schedule"]]
    assert crons == ["19 */3 * * *"], (
        "a 3-hourly poll settles a slate the same evening; the offset keeps it off the hour with every other job")
    assert "workflow_dispatch" in on
    inputs = on["workflow_dispatch"]["inputs"]
    assert {"games", "lookback_days", "dry_run"} <= set(inputs), "manual recovery needs to name games"


def test_the_job_has_concurrency_protection_and_pipefail():
    d = doc()
    assert d["concurrency"]["group"] == "postgame-settle"
    assert d["concurrency"]["cancel-in-progress"] is False, (
        "cancelling a run mid-publish would leave a batch written and unpublished")
    assert "pipefail" in d["defaults"]["run"]["shell"]


def test_expensive_steps_run_only_when_the_gate_found_work():
    """Otherwise every 3-hourly poll downloads player statistics to discover no game finished."""
    gated = []
    for s in steps():
        run = s.get("run") or ""
        if "stats_player" in run or "settle_games.py" in run:
            gated.append(s)
    assert gated, "the heavy steps were not found"
    for s in gated:
        cond = s.get("if") or ""
        assert "steps.gate.outputs.work" in cond, f"step {s.get('name')!r} is not behind the gate"


def test_the_gate_itself_downloads_only_the_schedule():
    gate = steps()[step_index("settle_gate.py")]
    assert "--only schedules" in gate["run"]
    assert "stats_player" not in gate["run"] and "pbp" not in gate["run"]


def test_nothing_is_published_before_it_is_validated():
    v = step_index("validate_evaluations.py")
    p = step_index("publish_market_data.py --src data/shadow/evaluations")
    assert v is not None and p is not None
    assert v < p, "validation must run before the publish, not after it"
    validate = steps()[v]
    assert "--market-data" in validate["run"], "the ledger's immutability is part of what is validated"
    assert "--require-rows" in validate["run"], "validating zero rows must not count as a pass"


def test_the_git_identity_is_configured_before_the_first_publish():
    identity = step_index("git config user.name")
    publishes = [i for i, s in enumerate(steps()) if "publish_market_data" in (s.get("run") or "")]
    assert identity is not None and publishes
    assert identity < min(publishes)


def test_the_publish_steps_are_reached_only_after_something_was_written():
    """Every publish is gated on the producing step (settle, arms or autopsy) having WRITTEN something."""
    for s in steps():
        if "publish_market_data" in (s.get("run") or ""):
            cond = s.get("if") or ""
            assert re.search(r"steps\.(settle|arms|autopsy)\.outputs\.status == 'WROTE'", cond), s.get("name")
            assert "dry_run" in cond, "a dry run must never publish"
            if "--src data/shadow/evaluations" in s["run"] or "--src data/shadow/scorecards" in s["run"]:
                assert "steps.settle.outputs.status == 'WROTE'" in cond


def test_a_conflict_fails_the_run():
    outcome = steps()[-1]
    assert outcome.get("if") == "always()"
    assert "CONFLICT" in outcome["run"] and "exit 1" in outcome["run"], (
        "a contradicted evaluation must fail the run, not be reported as a green no-op")


def test_the_job_never_writes_to_the_ledger_or_the_capture():
    """A settle run reads the published ledger. Any publish of those paths from here would be a rewrite."""
    src = open(PATH).read()
    for path in ("--src data/shadow/ledger", "--src data/kalshi", "--src data/shocks"):
        assert path not in src, f"the postgame job must not publish {path}"
    assert "--src data/shadow/evaluations" in src and "--src data/shadow/scorecards" in src


def test_the_immutable_product_is_published_before_the_derived_report():
    evaluations = step_index(r"publish_market_data\.py --src data/shadow/evaluations")
    report = step_index("eval_report.py")
    scorecards = step_index(r"publish_market_data\.py --src data/shadow/scorecards")
    assert evaluations < report < scorecards, (
        "the corpus is the product; the scorecard is derived from it and can always be rebuilt")
    assert steps()[report].get("continue-on-error") is True, (
        "a report failure must not fail a run whose corpus is already published")
    assert steps()[evaluations].get("continue-on-error") is not True, (
        "a failure to publish the corpus is a real failure")


def test_the_run_reports_what_it_did_even_when_it_did_nothing():
    outcome = steps()[-1]["run"]
    for token in ("gate work=", "settle status=", "written=", "deferred="):
        assert token in outcome, token
    assert "::notice::" in outcome, "a no-work run should say so rather than looking like a failure"


def test_dispatch_inputs_never_reach_the_shell_as_interpolated_text():
    """A `${{ github.event.inputs.x }}` inside a run block is executed as shell text by whoever dispatches it."""
    for s in steps():
        run = s.get("run") or ""
        assert "github.event.inputs" not in run, (
            f"step {s.get('name')!r} interpolates a dispatch input into its script; pass it through `env:` and "
            "quote the variable instead")
    settle = steps()[step_index("settle_games.py")]
    assert set(settle.get("env") or {}) >= {"INPUT_GAMES", "INPUT_LOOKBACK", "INPUT_DRY_RUN"}


def test_the_argument_building_fragment_survives_set_e_with_no_inputs():
    """`[ x = y ] && arr+=(...)` returns 1 when the test fails, and `set -e` would kill the step for the
    ordinary case of an unset dry_run."""
    import subprocess
    run = steps()[step_index("settle_games.py")]["run"]
    fragment = run.split("python3")[0] + 'echo "ARGS=${ARGS[*]}"'
    for env in ({}, {"INPUT_GAMES": "2026_01_NE_SEA", "INPUT_DRY_RUN": "true"}):
        r = subprocess.run(["bash", "-eo", "pipefail", "-c", fragment], capture_output=True, text=True,
                           env={**env, "PATH": "/usr/bin:/bin"})
        assert r.returncode == 0, f"the fragment failed under set -e with env={env}: {r.stderr[:200]}"
    r = subprocess.run(["bash", "-eo", "pipefail", "-c", fragment], capture_output=True, text=True,
                       env={"INPUT_GAMES": "2026_01_NE_SEA 2026_01_SF_LA", "PATH": "/usr/bin:/bin"})
    assert "--game 2026_01_NE_SEA --game 2026_01_SF_LA" in r.stdout


def test_the_settle_step_documents_its_network_reads():
    """Two read-only network reads live in this step; a reader must not have to discover that from a traceback."""
    src = open(PATH).read()
    assert "ESPN" in src and "exact scalar payout" in src


def _gate_terms(cond: str) -> set:
    """The distinct work conditions a step's `if:` fires on: gate outputs, plus the dispatch-input escape."""
    terms = set(re.findall(r"steps\.gate\.outputs\.(\w+)\s*==\s*'true'", cond or ""))
    if re.search(r"github\.event\.inputs\.games\s*!=\s*''", cond or ""):
        terms.add("__dispatch_games__")
    return terms


def test_the_dependency_install_covers_every_heavy_path_not_just_incumbent_settlement():
    """The install must fire whenever ANY step that needs the scientific stack fires.

    Two pieces of history meet in this one condition. The install step exists because run 34438883025 passed
    the gate, downloaded everything, and died on `import polars` inside settle_games.py. It was written when
    `work` was the only work state the gate reported. The three-arm experiment then added two INDEPENDENT
    ones -- `arms_work` and `autopsy_work` -- each driving its own step: settle_arms.py reaches numpy and
    polars, player_autopsy.py reaches polars. A run where a game has frozen arm snapshots to evaluate but
    nothing left to settle sets `arms_work` and not `work`, so an install still gated on `work` alone would
    reproduce the identical ModuleNotFoundError one step further down.

    So the rule is not "the install step exists" but "the install step's condition is implied by every heavy
    step's condition". Anything else is a run that installs nothing and then imports polars.
    """
    heavy_needs = {}
    for s in steps():
        run = s.get("run") or ""
        scripts = [m for m in re.findall(r"python3?\s+((?:scripts|nfl_edge)/[\w./-]+\.py)", run)]
        if not scripts or "pip install" in run:
            continue
        for script in scripts:
            if script in ("scripts/shadow/settle_gate.py", "scripts/data/nflverse_download.py",
                          "scripts/ci/publish_market_data.py"):
                continue                    # the cheap gate, the downloader and the publisher are stdlib-only
            heavy_needs.setdefault(s.get("name", "<unnamed>"), set()).update(_gate_terms(s.get("if")))

    install = next((s for s in steps() if "pip install" in (s.get("run") or "")), None)
    assert install is not None, "postgame-settle.yml installs nothing; the first live run died on import polars"
    covered = _gate_terms(install.get("if"))
    assert covered, "the install step is unconditional or its condition is unrecognised"

    uncovered = {name: sorted(t - covered) for name, t in heavy_needs.items() if t - covered}
    assert not uncovered, (
        "these steps run scripts that need the scientific stack under conditions the install step does not "
        f"cover, so they would die with ModuleNotFoundError: {uncovered}. Install condition covers {sorted(covered)}")
    for token in ("work", "arms_work", "autopsy_work"):
        assert token in covered, f"the install step ignores the gate's {token!r} work state"


def test_an_idle_poll_still_installs_nothing():
    """The cheap-idle-poll property is the reason the install sits behind the gate rather than at the top."""
    install = next(s for s in steps() if "pip install" in (s.get("run") or ""))
    cond = install.get("if") or ""
    assert cond, "an unconditional install makes every 3-hourly no-work poll pay for the scientific stack"
    assert "steps.gate.outputs" in cond, "the install must key off the gate, not run always"
    gate_at = step_index("settle_gate.py")
    install_at = next(i for i, s in enumerate(steps()) if "pip install" in (s.get("run") or ""))
    assert gate_at < install_at, "the install must come after the gate has decided there is work"


# --------------------------------------------------------------------- the redundant automatic trigger
#
# NE-SEA settled only because a human dispatched this workflow, so a second automatic trigger was added. These
# tests exist because that trigger introduces a THIRD event class into conditions that were written when there
# were two, and a `workflow_run` delivery that quietly behaved like a dispatch naming games -- or like a
# dry run -- would either do heavy work on every upstream completion or silently stop publishing.

import subprocess

import pytest

UPSTREAM = "Shadow Pricing (full universe)"


def _num(v):
    """GitHub's loose-equality coercion: null and '' are 0, booleans are 0/1, other strings parse or are NaN."""
    if v is None or v == "":
        return 0.0
    if isinstance(v, bool):
        return 1.0 if v else 0.0
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(v)
    except ValueError:
        return float("nan")


def _loose_eq(a, b):
    if type(a) is type(b) and isinstance(a, str):
        return a == b
    x, y = _num(a), _num(b)
    return not (x != x or y != y) and x == y          # NaN equals nothing, including itself


_TOKEN = re.compile(r"\s*(\(|\)|\|\||&&|==|!=|'[^']*'|[A-Za-z_][\w.\-]*\(\)|[A-Za-z_][\w.]*)")


def gh_expr(expr: str, ctx: dict):
    """Evaluate the restricted GitHub expression grammar this workflow actually uses.

    Only `==`, `!=`, `&&`, `||`, parentheses, single-quoted literals, context paths and `always()` appear, so a
    real parser is unnecessary -- but the COERCION has to be GitHub's, because the whole safety argument rests
    on `github.event.inputs.games != ''` being FALSE when inputs is null (0 == 0) while
    `github.event.inputs.dry_run != 'true'` is TRUE (0 != NaN). Getting that backwards is the bug this catches.
    """
    toks, i = [], 0
    while i < len(expr):
        m = _TOKEN.match(expr, i)
        if not m:
            raise AssertionError(f"unsupported expression syntax at {expr[i:]!r} in {expr!r}")
        toks.append(m.group(1))
        i = m.end()
    pos = 0

    def peek():
        return toks[pos] if pos < len(toks) else None

    def value(tok):
        if tok.startswith("'"):
            return tok[1:-1]
        if tok == "always()":
            return True
        cur = ctx
        for part in tok.split("."):
            if not isinstance(cur, dict):
                return None
            cur = cur.get(part)
        return cur

    def primary():
        nonlocal pos
        if peek() == "(":
            pos += 1
            v = disjunction()
            assert toks[pos] == ")", f"unbalanced parentheses in {expr!r}"
            pos += 1
            return v
        tok = toks[pos]; pos += 1
        return value(tok)

    def comparison():
        nonlocal pos
        left = primary()
        if peek() in ("==", "!="):
            op = toks[pos]; pos += 1
            right = primary()
            eq = _loose_eq(left, right)
            return eq if op == "==" else not eq
        return bool(left) if not isinstance(left, str) else left != ""

    def conjunction():
        nonlocal pos
        v = comparison()
        while peek() == "&&":
            pos += 1
            v = comparison() and v
        return v

    def disjunction():
        nonlocal pos
        v = conjunction()
        while peek() == "||":
            pos += 1
            v = conjunction() or v
        return v

    out = disjunction()
    assert pos == len(toks), f"trailing tokens in {expr!r}"
    return out


def ctx_for(event, *, conclusion="success", branch="main", games="", lookback="", dry_run=""):
    """`github` context as GitHub builds it. schedule and workflow_run carry NO inputs object at all."""
    c = {"event_name": event, "event": {}}
    if event == "workflow_dispatch":
        c["event"]["inputs"] = {"games": games, "lookback_days": lookback, "dry_run": dry_run}
    if event == "workflow_run":
        c["event"]["workflow_run"] = {"conclusion": conclusion, "head_branch": branch}
    return {"github": c}


def job_if():
    return doc()["jobs"]["settle"]["if"]


def step_conditions():
    return [(s.get("name", "<unnamed>"), s["if"]) for s in steps() if s.get("if")]


def outs(work="false", arms="false", autopsy="false", settle="", arms_st="", autopsy_st=""):
    return {"steps": {"gate": {"outputs": {"work": work, "arms_work": arms, "autopsy_work": autopsy}},
                      "settle": {"outputs": {"status": settle}},
                      "arms": {"outputs": {"status": arms_st}},
                      "autopsy": {"outputs": {"status": autopsy_st}}}}


def evaluate(cond, event_ctx, step_outputs):
    return gh_expr(cond, {**event_ctx, **step_outputs})


# -- sanity: the evaluator reproduces the two coercions the safety argument depends on
def test_the_expression_evaluator_matches_githubs_coercion_rules():
    null = ctx_for("schedule")
    assert gh_expr("github.event.inputs.games != ''", null) is False, (
        "null inputs must NOT look like a dispatch that named games")
    assert gh_expr("github.event.inputs.dry_run != 'true'", null) is True, (
        "null inputs must NOT look like a dry run, or a scheduled run would stop publishing")
    named = ctx_for("workflow_dispatch", games="2026_01_NE_SEA")
    assert gh_expr("github.event.inputs.games != ''", named) is True


# ---------------------------------------------------------------- A, B, C, D: the trigger surface
def test_A_the_scheduled_trigger_is_unchanged_and_still_starts_the_job():
    on = doc().get(True, doc().get("on"))
    assert [c["cron"] for c in on["schedule"]] == ["19 */3 * * *"], "the cron stays the fallback"
    assert evaluate(job_if(), ctx_for("schedule"), outs()) is True


def test_B_workflow_dispatch_is_unchanged_and_still_starts_the_job():
    on = doc().get(True, doc().get("on"))
    assert {"games", "lookback_days", "dry_run"} <= set(on["workflow_dispatch"]["inputs"])
    assert evaluate(job_if(), ctx_for("workflow_dispatch"), outs()) is True
    assert evaluate(job_if(), ctx_for("workflow_dispatch", games="2026_01_NE_SEA"), outs()) is True


def test_C_a_successful_upstream_run_on_main_reaches_the_cheap_gate():
    on = doc().get(True, doc().get("on"))
    wr = on["workflow_run"]
    assert wr["workflows"] == [UPSTREAM], "the upstream is the pregame pricer, named exactly"
    assert wr["types"] == ["completed"]
    assert wr["branches"] == ["main"]
    assert evaluate(job_if(), ctx_for("workflow_run"), outs()) is True
    gate = next(s for s in steps() if "settle_gate.py" in (s.get("run") or ""))
    assert "if" not in gate, "the gate must run unconditionally; it is what decides whether anything else does"


@pytest.mark.parametrize("conclusion", ["failure", "cancelled", "skipped", "timed_out", "action_required", None])
def test_D_an_unsuccessful_upstream_run_does_not_run_settlement(conclusion):
    """`types: [completed]` delivers failures and cancellations too, so the conclusion is checked explicitly."""
    assert evaluate(job_if(), ctx_for("workflow_run", conclusion=conclusion), outs()) is False


def test_D_an_upstream_run_on_another_branch_does_not_run_settlement():
    assert evaluate(job_if(), ctx_for("workflow_run", branch="claude/some-feature"), outs()) is False


# ---------------------------------------------------------------- E, F: cost and behaviour of an event run
HEAVY = ("nflverse_download.py --only stats_player", "pip install", "settle_games.py")


def heavy_steps():
    out = []
    for s in steps():
        run = s.get("run") or ""
        if any(h in run for h in HEAVY) and s.get("if"):
            out.append((s.get("name", "<unnamed>"), s["if"]))
    return out


def test_E_an_event_driven_run_with_no_work_installs_and_downloads_nothing():
    idle = outs()                       # gate found no work of any kind
    ran = [n for n, c in heavy_steps() if evaluate(c, ctx_for("workflow_run"), idle)]
    assert ran == [], f"an idle upstream completion would have run heavy steps: {ran}"
    # and it costs exactly what an idle poll costs, because the two events evaluate identically
    assert [evaluate(c, ctx_for("schedule"), idle) for _, c in heavy_steps()] == \
           [evaluate(c, ctx_for("workflow_run"), idle) for _, c in heavy_steps()]


def test_F_an_event_driven_run_with_work_follows_the_normal_settlement_path():
    busy = outs(work="true")
    ran = {n for n, c in heavy_steps() if evaluate(c, ctx_for("workflow_run"), busy)}
    assert len(ran) == len(heavy_steps()), f"a settleable game must reach every heavy step, reached {ran}"
    wrote = outs(work="true", settle="WROTE")
    published = [s.get("name") for s in steps()
                 if s.get("if") and "publish_market_data.py" in (s.get("run") or "")
                 and evaluate(s["if"], ctx_for("workflow_run"), wrote)]
    assert any("evaluation" in (n or "").lower() for n in published), (
        "an event-driven run that settled a game must publish it exactly as a scheduled run would")


def test_the_event_classes_that_carry_no_inputs_are_indistinguishable_everywhere():
    """The whole safety argument in one assertion.

    `schedule` and `workflow_run` both leave `github.event.inputs` null, and no STEP condition mentions
    `github.event_name`, so no step can tell them apart. Adding the trigger therefore cannot change what a
    scheduled run does -- and if someone later adds an event_name test to a step, this fails.
    """
    for name, cond in step_conditions():
        assert "github.event_name" not in cond, (
            f"step {name!r} branches on the event name; schedule and workflow_run must stay interchangeable")
    for st in (outs(), outs(work="true"), outs(work="true", settle="WROTE"),
               outs(arms="true", arms_st="WROTE"), outs(autopsy="true", autopsy_st="WROTE")):
        for name, cond in step_conditions():
            assert evaluate(cond, ctx_for("schedule"), st) == evaluate(cond, ctx_for("workflow_run"), st), \
                f"step {name!r} behaves differently under workflow_run than under schedule"


def test_an_automatic_event_never_looks_like_a_dry_run_or_a_named_dispatch():
    for event in ("schedule", "workflow_run"):
        c = ctx_for(event)
        assert gh_expr("github.event.inputs.games != ''", c) is False
        assert gh_expr("github.event.inputs.dry_run != 'true'", c) is True
    env = next(s for s in steps() if "settle_games.py" in (s.get("run") or ""))["env"]
    assert env["INPUT_GAMES"] == "${{ github.event.inputs.games }}"
    assert "${{" not in env["INPUT_GAMES"].replace("${{ github.event.inputs.games }}", ""), "no other interpolation"


def test_blank_lookback_still_defaults_to_ten_days_for_every_event():
    """`${INPUT_LOOKBACK:-10}` is what makes an automatic run look back as far as a dispatched one."""
    for s in steps():
        run = s.get("run") or ""
        if "--lookback-days" in run:
            assert '"${INPUT_LOOKBACK:-10}"' in run, f"step {s.get('name')!r} lost its lookback default"
    r = subprocess.run(["bash", "-eo", "pipefail", "-c", 'echo "${INPUT_LOOKBACK:-10}"'],
                       capture_output=True, text=True, env={"PATH": os.environ["PATH"], "INPUT_LOOKBACK": ""})
    assert r.returncode == 0 and r.stdout.strip() == "10"


# ---------------------------------------------------------------- G, H, I: duplicates are harmless
def test_G_and_I_concurrency_still_serialises_duplicate_triggers():
    d = doc()
    assert d["concurrency"]["group"] == "postgame-settle", (
        "one group for every event class, or a cron run and an upstream-triggered run overlap")
    assert d["concurrency"]["cancel-in-progress"] is False, (
        "cancelling the loser mid-publish would leave a batch written and unpublished; it must queue instead")


def test_G_a_duplicate_trigger_cannot_publish_without_writing_and_validating_first():
    names = [s.get("name", "") for s in steps()]
    pub = [i for i, s in enumerate(steps()) if "publish_market_data.py" in (s.get("run") or "")]
    val = [i for i, s in enumerate(steps()) if "validate_evaluations.py" in (s.get("run") or "")]
    assert val and pub and min(val) < min(pub), "validation must precede the first publish"
    for i in pub:
        cond = steps()[i].get("if", "")
        assert "outputs.status == 'WROTE'" in cond, (
            f"publish step {names[i]!r} is not gated on something actually having been written")
    # a second trigger that wrote nothing evaluates every publish step to false
    for i in pub:
        assert evaluate(steps()[i]["if"], ctx_for("workflow_run"), outs(work="true", settle="NO_OP")) is False


def test_H_an_already_evaluated_game_makes_the_settlement_step_a_no_op():
    """The gate is the only thing that decides, and it decides from the published corpus.

    Proven live rather than only here: run 34529337863 (schedule, 20:56Z) started 32 minutes after run
    34525867725 published the NE-SEA batch, reported `work=false`, and skipped the settle step and every
    publishing step.
    """
    settle = next(s for s in steps() if "settle_games.py" in (s.get("run") or ""))
    assert evaluate(settle["if"], ctx_for("workflow_run"), outs(work="false")) is False
    assert evaluate(settle["if"], ctx_for("schedule"), outs(work="false")) is False


def test_the_upstream_workflow_exists_and_cannot_be_triggered_by_this_one():
    """A workflow_run pair that pointed at each other would ping-pong forever."""
    up = os.path.join(ROOT, ".github", "workflows", "shadow-price.yml")
    assert os.path.exists(up)
    with open(up) as f:
        upstream = yaml.safe_load(f)
    assert upstream["name"] == UPSTREAM, "the trigger names the upstream by its `name:`, not its filename"
    on_up = upstream.get(True, upstream.get("on"))
    assert "workflow_run" not in on_up, "the upstream must not be triggered by a workflow, or the two loop"
    assert "push" not in (doc().get(True, doc().get("on"))), (
        "this workflow must never trigger on a push: it publishes to market-data, which would re-trigger it")


# ---------------------------------------------------------------- J: nothing scientific moved
FROZEN = ("nfl_edge/model", "nfl_edge/pricing", "nfl_edge/handicap/risk.py", "nfl_edge/handicap/gates.py",
          "nfl_edge/settlement/settle.py", "nfl_edge/settlement/semantics.py", "nfl_edge/shadow/pricer.py",
          "scripts/shadow/settle_arms.py", "scripts/shadow/three_arm_snapshot.py", "research/")


def _changed_against_main():
    r = subprocess.run(["git", "diff", "--name-status", "origin/main...HEAD"],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        return None
    out = []
    for line in r.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            out.append((parts[0][:1], parts[-1]))
    return out


def test_J_no_model_risk_or_experiment_file_is_touched_by_this_change():
    changed = _changed_against_main()
    if changed is None:
        pytest.skip("origin/main is not fetched here")
    # A NEW study under research/ (its own results.json + RESULTS.md) is what research/ is for (docs/ARCHITECTURE.md);
    # the hazard this guard exists for is rewriting a RECORDED result or touching the model / risk / settlement code.
    offenders = [p for status, p in changed for f in FROZEN
                 if p.startswith(f) and not (f == "research/" and status == "A")]
    assert not offenders, f"trigger reliability work must not touch the scientific path: {offenders}"
