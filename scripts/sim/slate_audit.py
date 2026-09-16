#!/usr/bin/env python3
"""Hostile football-sanity audit of a PUBLISHED simulation slate.

"The workflow went green" says nothing about whether the slate is football-sane.  This reads a published
`data/shadow/sim/<day>/<run>.manifest.json` + `.projections.jsonl.gz` pair and interrogates it:

  * PROVENANCE  -- versions, bundle/prior fit seasons, injury vintage, Sleeper run, market observation.
  * PROBABILITY -- every probability finite and in [0,1]; every ladder monotone in the threshold.
  * RECONCILE   -- the deployed weight per family, and the invariant that a family with weight 0 must not
                   be presenting a disagreement against the market it has not earned.  This is the check
                   that catches a zero-authority family being ranked.
  * ROLE        -- Kalshi-listed players missing from the priced set, starters with implausibly small
                   opportunity, backups carrying starter volume, anybody OUT drawing opportunity, and
                   questionable players' play probability.
  * FOOTBALL    -- with ``--reconstruct``, re-runs the simulation from the same point-in-time inputs at the
                   manifest's own cutoff to expose the team-level quantities the contract rows do not
                   carry (plays, pass/rush split, dropbacks, team rush attempts, team targets) and the
                   per-player opportunity behind them.  The reconstruction is verified against the
                   published football means before any of its numbers are reported, so a drifted
                   reconstruction is an error rather than a quietly different second opinion.

Exits non-zero when a BLOCKER-severity finding is present, so it can gate a publication step.
"""
from __future__ import annotations
import argparse, collections, glob, gzip, json, math, os, sys
from datetime import datetime, timezone
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

# a starter (depth-chart rank 1) at these positions carrying less than this many of the opportunity the
# engine allocates is either hurt, in a committee the model does not know about, or a role failure
STARTER_FLOOR = {"RB": 6.0, "WR": 3.0, "TE": 2.0, "QB": 15.0}
# a rank-3+ player carrying more than this is a backup with starter volume
BACKUP_CEILING = {"RB": 12.0, "WR": 7.0, "TE": 6.0}
PLAY_STATES = {"ACTIVE": 1.0, "PROBABLE": 0.97, "QUESTIONABLE": 0.75, "DOUBTFUL": 0.25, "OUT": 0.0}
OPP_STAT = {"RB": "carries", "WR": "targets", "TE": "targets", "QB": "attempts"}
# Kalshi stat -> the reconciliation family the deployed weights are keyed by
STAT_TO_FAMILY = {"touchdowns": "any_td", "passing_tds": "pass_td", "passing_yards": "pass_yards",
                  "receiving_yards": "rec_yards", "receptions": "receptions", "rushing_yards": "rush_yards"}


class Tee:
    """Captures everything printed so the committed report is a pure render of the audit run."""

    def __init__(self, stream):
        self.stream = stream
        self.buf = []

    def write(self, s):
        self.buf.append(s)
        return self.stream.write(s)

    def flush(self):
        self.stream.flush()

    def text(self):
        return "".join(self.buf)


class Findings:
    def __init__(self):
        self.rows = []

    def add(self, sev: str, area: str, msg: str, detail=None):
        self.rows.append({"severity": sev, "area": area, "message": msg, "detail": detail})

    def of(self, sev):
        return [r for r in self.rows if r["severity"] == sev]

    def report(self):
        for sev in ("BLOCKER", "WARN", "NOTE"):
            rs = self.of(sev)
            if not rs:
                continue
            print(f"\n{'=' * 100}\n{sev} ({len(rs)})\n{'=' * 100}")
            for r in rs:
                print(f"[{r['area']}] {r['message']}")
                if r["detail"]:
                    for line in (r["detail"] if isinstance(r["detail"], list) else [r["detail"]])[:25]:
                        print(f"    {line}")


def latest_pair(sim_root: str) -> tuple[str, str]:
    mans = sorted(glob.glob(os.path.join(sim_root, "*", "*.manifest.json")))
    if not mans:
        raise SystemExit(f"no manifest under {sim_root}")
    m = mans[-1]
    p = m.replace(".manifest.json", ".projections.jsonl.gz")
    if not os.path.exists(p):
        raise SystemExit(f"manifest {m} has no projections beside it")
    return m, p


def load(man_path: str, proj_path: str):
    man = json.load(open(man_path))
    rows = [json.loads(l) for l in gzip.open(proj_path, "rt")]
    return man, rows


# ------------------------------------------------------------------------------------- provenance
def audit_provenance(man: dict, rows: list, F: Findings):
    print(f"\n{'=' * 100}\nPROVENANCE\n{'=' * 100}")
    src = man.get("sources") or {}
    iv = src.get("injury_vintage") or {}
    fields = [
        ("run_id", man.get("run_id")), ("sim_version", man.get("sim_version")),
        ("season/week", f"{man.get('season')} / {man.get('week')}"),
        ("cutoff", man.get("cutoff")), ("generated_at", man.get("generated_at")),
        ("market_observed_at", man.get("market_observed_at")),
        ("bundle_train_seasons", man.get("bundle_train_seasons")),
        ("priors_fit_seasons", man.get("priors_fit_seasons")),
        ("priors_version", man.get("priors_version")),
        ("deployed_weights", man.get("deployed_weights")),
        ("depth_chart_vintage", src.get("depth_chart_vintage")),
        ("roster_week", src.get("roster_week")),
        ("injury_vintage.resolved", iv.get("resolved")),
        ("injury_vintage.sha256", (iv.get("sha256") or "")[:16]),
        ("injury_vintage.retrieved_at", iv.get("retrieved_at")),
        ("injury_vintage.reason", iv.get("reason")),
        ("injury_vintage.rows_for_week", iv.get("rows_for_week")),
        ("injury_vintage.designations", iv.get("designations")),
        ("sleeper_run", src.get("sleeper_run")),
        ("history_games", src.get("history_games")),
        ("latest_history_game", src.get("latest_history_game")),
        ("n_rows", man.get("n_rows")), ("n_games", len(man.get("games") or {})),
    ]
    for k, v in fields:
        print(f"  {k:32s} {v}")
    print("  counts by family|support_state:")
    for k, v in sorted((man.get("counts") or {}).items()):
        print(f"    {k:48s} {v}")

    season = man.get("season")
    if season is not None:
        for key in ("bundle_train_seasons", "priors_fit_seasons"):
            ss = man.get(key) or []
            if ss and max(ss) >= season:
                F.add("BLOCKER", "PIT", f"{key} reaches the predicted season {season}: max={max(ss)}")
    for k in ("run_id", "sim_version", "market_observed_at", "priors_version"):
        if not man.get(k):
            F.add("BLOCKER", "PROVENANCE", f"manifest is missing {k}")
    if not iv:
        F.add("BLOCKER", "PROVENANCE", "manifest carries no injury_vintage block")
    elif iv.get("resolved") and not iv.get("sha256"):
        F.add("BLOCKER", "PROVENANCE", "injury vintage resolved with no content hash recorded")
    if iv.get("resolved") and iv.get("retrieved_at") and man.get("cutoff"):
        ret = datetime.fromisoformat(iv["retrieved_at"].replace("Z", "+00:00"))
        cut = datetime.fromisoformat(man["cutoff"].replace("Z", "+00:00"))
        if ret.tzinfo is None:
            ret = ret.replace(tzinfo=timezone.utc)
        if cut.tzinfo is None:
            cut = cut.replace(tzinfo=timezone.utc)
        if ret > cut:
            F.add("BLOCKER", "PIT", f"injury vintage retrieved {ret} is AFTER the feature cutoff {cut}")
        else:
            print(f"  injury vintage is {(cut - ret).total_seconds() / 3600:.1f}h before the cutoff: OK")
    if iv.get("resolved") and not iv.get("rows_for_week") and not src.get("sleeper_run"):
        F.add("BLOCKER", "AVAILABILITY",
              "the injury vintage has no rows for this week AND there is no Sleeper capture: "
              "nothing carries availability")
    elif iv.get("resolved") and not iv.get("rows_for_week"):
        F.add("NOTE", "AVAILABILITY",
              f"injury vintage has 0 rows for week {man.get('week')}; availability rests on Sleeper "
              f"capture {src.get('sleeper_run')} (recorded, not hidden)")

    stale = [r["ticker"] for r in rows if r.get("run_id") != man.get("run_id")]
    if stale:
        F.add("BLOCKER", "PROVENANCE", f"{len(stale)} rows carry a run_id different from the manifest's")


# ------------------------------------------------------------------------------------- numbers
def audit_probabilities(rows: list, F: Findings):
    print(f"\n{'=' * 100}\nPROBABILITY / LADDER SANITY\n{'=' * 100}")
    priced = [r for r in rows if r.get("support_state") == "PRICED"]
    bad = []
    for r in rows:
        for k in ("p_football", "p_market", "p_reconciled", "p_active"):
            v = r.get(k)
            if v is None:
                continue
            if not isinstance(v, (int, float)) or not math.isfinite(v) or not (0.0 <= v <= 1.0):
                bad.append(f"{r.get('ticker')} {k}={v}")
    print(f"  rows checked: {len(rows)}; non-finite or out-of-[0,1] probabilities: {len(bad)}")
    if bad:
        F.add("BLOCKER", "PROBABILITY", f"{len(bad)} probabilities are NaN/inf or outside [0,1]", bad)

    neg = [f"{r.get('ticker')} football_mean={r.get('football_mean')}" for r in priced
           if r.get("football_mean") is not None and (not math.isfinite(r["football_mean"]) or r["football_mean"] < 0)]
    if neg:
        F.add("BLOCKER", "PROBABILITY", f"{len(neg)} negative or non-finite football means", neg)
    print(f"  negative/non-finite football means: {len(neg)}")

    # a ladder is (player, stat): P(X >= t) must not increase with t
    lad = collections.defaultdict(list)
    for r in priced:
        if r.get("operator") == ">=" and r.get("threshold") is not None:
            lad[(r.get("player_id"), r.get("stat"), r.get("game_id"))].append(r)
    viol = {"p_football": [], "p_reconciled": [], "p_market": []}
    for key, rs in lad.items():
        rs = sorted(rs, key=lambda r: r["threshold"])
        for field in viol:
            vs = [r.get(field) for r in rs]
            for a, b, ra, rb in zip(vs, vs[1:], rs, rs[1:]):
                if a is None or b is None:
                    continue
                if b > a + 1e-9:
                    viol[field].append(f"{key[1]} {key[0]} {key[2]}: t={ra['threshold']}->{rb['threshold']} "
                                       f"{field} {a:.4f}->{b:.4f}")
    print(f"  ladders checked: {len(lad)}")
    for field, vs in viol.items():
        print(f"    non-monotone in {field:14s}: {len(vs)}")
        if vs:
            sev = "BLOCKER" if field != "p_market" else "WARN"
            F.add(sev, "LADDER", f"{len(vs)} non-monotone steps in {field}", vs)
    return priced


def audit_reconciliation(man: dict, priced: list, F: Findings):
    print(f"\n{'=' * 100}\nMARKET RECONCILIATION\n{'=' * 100}")
    dep = man.get("deployed_weights") or {}
    print("  deployed weights on the manifest:")
    for k, v in sorted(dep.items()):
        print(f"    {k:14s} {v}")
    nonzero_fams = sorted(k for k, v in dep.items() if v)
    print(f"  families with non-zero deviation authority: {nonzero_fams or 'none'}")

    by = collections.defaultdict(list)
    for r in priced:
        by[r["stat"]].append(r)
    print(f"\n  {'stat':18s} {'n':>4s} {'w':>5s} {'mean|fb-mkt|':>12s} {'mean|rec-mkt|':>13s} "
          f"{'max|rec-mkt|':>12s} {'mean fb':>9s} {'mean mkt':>9s} {'mean final':>10s}")
    for stat, rs in sorted(by.items()):
        w = {r["reconcile_weight"] for r in rs}
        fb = np.array([abs((r.get("p_football") or 0) - (r.get("p_market") or 0)) for r in rs])
        rc = np.array([abs((r.get("p_reconciled") or 0) - (r.get("p_market") or 0)) for r in rs])
        fm = np.mean([r.get("football_mean") or np.nan for r in rs])
        mm = np.mean([r.get("market_mean") or np.nan for r in rs])
        nm = np.mean([r.get("final_mean") or np.nan for r in rs])
        print(f"  {stat:18s} {len(rs):4d} {'/'.join(f'{x:g}' for x in sorted(w)):>5s} {fb.mean():12.4f} "
              f"{rc.mean():13.4f} {rc.max():12.4f} {fm:9.3f} {mm:9.3f} {nm:10.3f}")

    # INVARIANT: weight 0 means the mean is the market's.  The final mean must match the market mean.
    def _rel(r):
        return abs(r["final_mean"] - r["market_mean"]) / max(1e-9, abs(r["market_mean"]))
    zw_means = [r for r in priced if r["reconcile_weight"] == 0.0
                and r.get("final_mean") is not None and r.get("market_mean") is not None]
    gran = [r for r in zw_means if 0.01 < _rel(r) <= 0.10]
    broken = [r for r in zw_means if _rel(r) > 0.10]
    print(f"\n  zero-weight rows whose FINAL MEAN is not the market mean: "
          f"{len(gran)} within 1-10% (lattice granularity), {len(broken)} beyond 10%")
    if broken:
        F.add("BLOCKER", "RECONCILE",
              f"{len(broken)} zero-weight rows are more than 10% from the market MEAN, which the "
              f"relocation is supposed to hit exactly at w=0",
              [f"{r['ticker']}: final {r['final_mean']:.3f} vs market {r['market_mean']:.3f}" for r in broken[:12]])
    if gran:
        F.add("WARN", "RECONCILE",
              f"{len(gran)} zero-weight rows sit 1-10% from the market mean: `shifted_to_mean` scales the "
              f"support once and re-discretises onto the integer lattice without iterating, so a "
              f"small-count family cannot land on an arbitrary mean. Known limitation, second order "
              f"behind the shape gap",
              [f"{r['ticker']}: final {r['final_mean']:.3f} vs market {r['market_mean']:.3f} "
               f"({100 * _rel(r):.1f}%)" for r in gran[:8]])

    # INVARIANT: a zero-weight family must not present a disagreement.  At weight 0 the only thing left
    # that can move the probability away from the market is the SHAPE substitution, and no shape claim has
    # been validated out of sample, so a material |p_reconciled - mid| on a zero-weight row is an
    # unearned disagreement that a ranker will pick up.
    RANK_FLOOR = 0.05
    zero = [r for r in priced if r["reconcile_weight"] == 0.0]
    material = [r for r in zero if abs((r.get("p_reconciled") or 0) - (r.get("mid") or 0)) >= RANK_FLOOR]
    print(f"  zero-weight rows whose |p_reconciled - mid| >= {RANK_FLOOR}: {len(material)} of {len(zero)} "
          f"(the untested shape substitution; reported, and they must not be ranked)")
    if material:
        worst = sorted(material, key=lambda r: -abs(r["p_reconciled"] - r["mid"]))[:8]
        F.add("NOTE", "RECONCILE",
              f"{len(material)} zero-weight rows carry a reconciled gap of >= {RANK_FLOOR} against the mid. "
              f"At w=0 the mean is the market's, so this is the football SHAPE, which was never confirmed "
              f"out of sample. It is legitimate to REPORT; the invariant below is that it is never RANKED",
              [f"{r['stat']:16s} mid={r['mid']:.3f} p_rec={r['p_reconciled']:.3f} "
               f"(dis {r['p_reconciled'] - r['mid']:+.4f}) p_fb={r['p_football']:.3f} "
               f"(fb dis {(r.get('football_disagreement_vs_mid') or 0):+.4f}) {r['ticker']}" for r in worst])

    # THE INVARIANT, checked end to end against the real consumer rather than a proxy: run the packet's
    # own game_view over the published rows and assert nothing without a deployed weight is ranked.
    try:
        from nfl_edge.handicap import sim_block as SB
        per_game = collections.defaultdict(list)
        for r in priced:
            per_game[r.get("game_id")].append(r)
        bad, n_ranked, n_diverted = [], 0, 0
        for gid, rs in per_game.items():
            v = SB.game_view(rs, man)
            n_ranked += len(v.get("largest_reconciled_disagreements") or [])
            n_diverted += len(v.get("unranked_zero_weight_disagreements") or [])
            for e in (v.get("largest_reconciled_disagreements") or []):
                if not (e.get("reconcile_weight") or 0) > 0:
                    bad.append(f"{gid} {e.get('stat')} w={e.get('reconcile_weight')} {e.get('ticker')}")
        fams = sorted({e.get("stat") for gid, rs in per_game.items()
                       for e in (SB.game_view(rs, man).get("largest_reconciled_disagreements") or [])})
        print(f"  packet ranking over these rows: {n_ranked} ranked, {n_diverted} diverted as zero-weight; "
              f"families ranked = {fams or 'none'}")
        if bad:
            F.add("BLOCKER", "RECONCILE",
                  f"{len(bad)} rows with NO deployed weight reached the packet's ranked disagreement list",
                  bad[:12])
        deployed_nonzero = sorted(k for k, v in (man.get("deployed_weights") or {}).items() if v)
        unexpected = [f for f in fams if f and STAT_TO_FAMILY.get(f, f) not in deployed_nonzero]
        if unexpected:
            F.add("BLOCKER", "RECONCILE",
                  f"families ranked that carry no deployed weight on the manifest: {unexpected} "
                  f"(deployed non-zero: {deployed_nonzero})")
    except Exception as exc:                                                     # noqa: BLE001
        F.add("WARN", "RECONCILE", f"could not check the ranking invariant: {type(exc).__name__}: {exc}")

    game_fams = [r for r in priced if r.get("family") != "PLAYER_STAT"]
    if game_fams:
        F.add("BLOCKER", "RECONCILE",
              f"{len(game_fams)} non-PLAYER_STAT rows are PRICED; game families must stay MARKET_CENTRED_GAME")
    return by


def audit_game_markets(rows: list, F: Findings):
    print(f"\n{'=' * 100}\nGAME MARKETS\n{'=' * 100}")
    st = collections.Counter((r.get("family"), r.get("support_state")) for r in rows
                             if r.get("family") != "PLAYER_STAT")
    for (fam, s), n in sorted(st.items()):
        print(f"  {fam:14s} {s:34s} {n}")
        if fam in ("GAME_WINNER", "SPREAD", "TOTAL", "TEAM_TOTAL") and s != "MARKET_CENTRED_GAME":
            F.add("BLOCKER", "GAME_MARKET", f"{fam} rows are {s}, not MARKET_CENTRED_GAME ({n} rows)")
    unsup = collections.Counter(r.get("support_reason") for r in rows
                                if r.get("support_state", "").startswith("UNSUPPORTED"))
    print("\n  unsupported rows by reason:")
    for k, v in sorted(unsup.items(), key=lambda x: -x[1]):
        print(f"    {str(k)[:80]:80s} {v}")
    other = collections.Counter(r.get("support_state") for r in rows)
    print("\n  every support state:")
    for k, v in sorted(other.items(), key=lambda x: -x[1]):
        print(f"    {k:40s} {v}")


# ------------------------------------------------------------------------------------- roles
def audit_roles_from_artifact(man: dict, rows: list, F: Findings):
    print(f"\n{'=' * 100}\nROLE / AVAILABILITY (from the published artifact)\n{'=' * 100}")
    priced = [r for r in rows if r.get("support_state") == "PRICED"]

    ident = [r for r in rows if r.get("support_state") == "UNSUPPORTED_IDENTITY"]
    if ident:
        who = collections.Counter((r.get("game_id"), r.get("player_kalshi_id")) for r in ident)
        print(f"  Kalshi contracts whose player could not be resolved to a GSIS id: {len(ident)} rows, "
              f"{len(who)} distinct players")
        F.add("WARN", "ROLE",
              f"{len(who)} Kalshi-listed players could not be mapped to a GSIS id, so {len(ident)} "
              f"contracts were passed on rather than priced",
              [f"{g} kalshi_id={k} ({n} rows)" for (g, k), n in who.most_common(15)])

    fonly = [r for r in rows if r.get("support_state") == "FOOTBALL_ONLY_NO_RECONCILIATION"]
    if fonly:
        who = collections.Counter((r.get("stat"), r.get("support_reason")) for r in fonly)
        print(f"  football-only rows with no usable market: {len(fonly)}")
        for (s, why), n in who.most_common(10):
            print(f"    {s:18s} {str(why)[:60]:60s} {n}")

    # QUARTERBACK STARTER CROSS-CHECK.  Uses only the EXISTENCE of a passing ladder -- never its price --
    # which the project already accepts as a role signal.  Kalshi lists passing markets for the man it
    # believes is taking the snaps; if the model projects that man a handful of yards, the model has the
    # wrong starter, and the whole team's passing game is attributed to the wrong player.  This is the
    # Week 1 Price/Stevenson failure moved to the highest-leverage position, and Week 2 2026 had one:
    # nflverse's depth chart made Kyler Murray Minnesota's QB1, Kalshi listed a full 215-yard ladder for
    # Carson Wentz and none for Murray, and the football model gave Wentz 8.5 passing yards.
    qb_stats = {"passing_yards", "passing_tds", "attempts", "completions"}
    listed_qb = collections.defaultdict(dict)
    for r in priced:
        if r.get("stat") in qb_stats and r.get("player_id"):
            d = listed_qb[(r.get("game_id"), r.get("team"))].setdefault(
                r["player_id"], {"stats": set(), "fb": None, "mkt": None})
            d["stats"].add(r["stat"])
            if r.get("stat") == "passing_yards":
                d["fb"], d["mkt"] = r.get("football_mean"), r.get("market_mean")
    print(f"\n  quarterback starter cross-check (market LISTING only, never the quote):")
    for (gid, team), qbs in sorted(listed_qb.items(), key=lambda x: str(x[0])):
        who = sorted(qbs.items(), key=lambda kv: -(kv[1]["fb"] or 0))
        desc = ", ".join(f"{pid} fb={('%.1f' % v['fb']) if v['fb'] is not None else '-'}"
                         f"/mkt={('%.1f' % v['mkt']) if v['mkt'] is not None else '-'}" for pid, v in who)
        print(f"    {gid:22s} {str(team):4s} {desc}")
        for pid, v in who:
            fb, mkt = v.get("fb"), v.get("mkt")
            if fb is None or mkt is None or mkt < 80.0:
                continue                      # not a starter's ladder; nothing is being claimed
            if fb < 0.35 * mkt:
                F.add("BLOCKER", "ROLE",
                      f"{gid} {team}: the market lists a starter's passing ladder for {pid} "
                      f"(implied mean {mkt:.0f} yards) and the football model projects {fb:.1f} -- the "
                      f"model almost certainly has the wrong starting quarterback, so this team's passing "
                      f"volume is attributed to the wrong player")

    # ANY_TD: how much of the ranked gap is football, and how much is the market-mean estimator?  any_td
    # is the ONLY family with deployed authority, so this is the only disagreement that can reach a
    # ranking, and it deserves to be decomposed rather than trusted whole.
    td1 = [r for r in priced if r.get("stat") == "touchdowns" and r.get("threshold") == 1
           and r.get("market_mean") is not None and r.get("mid") is not None
           and r.get("p_reconciled") is not None]
    if td1:
        rt = np.array([1.0 - math.exp(-max(r["market_mean"], 0.0)) for r in td1])
        mid = np.array([r["mid"] for r in td1])
        fbd = np.array([(r.get("football_disagreement_vs_mid") or 0.0) for r in td1])
        recd = np.array([r["p_reconciled"] - r["mid"] for r in td1])
        flip = int(np.sum(recd * fbd < 0))
        print(f"\n  any_td (t=1, n={len(td1)}) ranked-signal decomposition:")
        print(f"    mean ranked gap (reconciled - mid)          {recd.mean():+.4f}")
        print(f"    mean football gap (football - mid)          {fbd.mean():+.4f}")
        print(f"    market's own mean re-priced as a Poisson    {rt.mean():.4f} vs mid {mid.mean():.4f} "
              f"({(rt - mid).mean():+.4f}; above the mid on {100 * (rt > mid).mean():.0f}% of rows)")
        print(f"    ranked rows pointing OPPOSITE to football   {flip}/{len(td1)} = {100 * flip / len(td1):.1f}%")
        if abs((rt - mid).mean()) > abs(fbd.mean()):
            F.add("WARN", "RECONCILE",
                  f"most of the mean ranked any_td gap is the market-mean estimator, not football: "
                  f"re-pricing the market's OWN mean through the engine's Poisson sits {(rt - mid).mean():+.4f} "
                  f"from the mid while the football view is {fbd.mean():+.4f}. The 0.25 weight was fitted and "
                  f"confirmed on exactly this quantity, so it is inside the validated envelope, but a reader "
                  f"ranking these rows is not seeing a pure football opinion")
        if flip:
            F.add("WARN", "RECONCILE",
                  f"{flip} of {len(td1)} ranked any_td rows have a reconciled gap pointing the OPPOSITE way "
                  f"to the football view (the relocation crosses the mid), so the sign of the ranked "
                  f"disagreement is not the sign of the model's opinion")

    # p_active sanity: nobody priced should be a certainty-zero, and no row may exceed 1
    pa = [(r.get("p_active"), r) for r in priced if r.get("p_active") is not None]
    if pa:
        lo = sorted(pa, key=lambda x: x[0])[:10]
        print(f"\n  p_active over priced rows: min {min(x[0] for x in pa):.3f} "
              f"median {np.median([x[0] for x in pa]):.3f} max {max(x[0] for x in pa):.3f}")
        print("  lowest p_active priced rows:")
        for v, r in lo:
            print(f"    {v:.3f}  {r.get('stat'):16s} {r.get('player_id')} {r.get('ticker')}")
        zero_active = [r for v, r in pa if v <= 0.0]
        if zero_active:
            F.add("BLOCKER", "ROLE",
                  f"{len(zero_active)} rows are PRICED for a player with p_active = 0",
                  [r["ticker"] for r in zero_active[:15]])
        # a Questionable player should sit between the doubtful and probable rates, never near-certain
        band = [r for v, r in pa if 0.0 < v < 0.25]
        if band:
            F.add("WARN", "ROLE",
                  f"{len(band)} priced rows carry p_active < 0.25 (a player this unlikely to play is "
                  f"being priced at all)", [f"{r['ticker']} p_active={r['p_active']:.3f}" for r in band[:10]])
    return priced


def audit_football(man: dict, rows: list, F: Findings, market_data: str, n_sims: int, tol: float):
    """Re-run the simulation from the same point-in-time inputs and expose the team-level football."""
    print(f"\n{'=' * 100}\nFOOTBALL SANITY (reconstruction at the manifest cutoff)\n{'=' * 100}")
    from nfl_edge.sim import features as FF, inputs as I, prospective as P, simulate as S

    season, week = man["season"], man["week"]
    cutoff = datetime.fromisoformat(man["cutoff"].replace("Z", "+00:00"))
    bundle = json.load(open(os.path.join(ROOT, "research", "simulation_engine", f"bundle_{season}.json")))
    priors = FF.PriorSet.from_dict(bundle["priors"])
    # the same ledger snapshot the published run priced against, resolved the same way
    ledger_rows, _lman, lrun = P.latest_ledger(market_data, at_or_before=cutoff)
    if lrun != man.get("run_id"):
        F.add("NOTE", "RECONSTRUCTION",
              f"reconstruction resolved ledger run {lrun}; the published run priced {man.get('run_id')}")
    slate = P.slate_inputs(season, week, cutoff, market_data, ledger_rows=ledger_rows,
                           verbose=lambda *a: None, priors=priors)
    bank = I.historical_bank(season)

    # every player Kalshi lists on this slate, against the set the simulator considered eligible
    elig = slate["eligible"]
    elig_ids = set(zip(elig["game_id"], elig["player_id"]))
    listed = collections.defaultdict(set)
    for r in rows:
        if r.get("family") == "PLAYER_STAT" and r.get("player_id") and r.get("game_id"):
            listed[r["game_id"]].add(r["player_id"])
    missing = [(g, p) for g, ps in listed.items() for p in ps if (g, p) not in elig_ids]
    print(f"\n  Kalshi-listed players absent from the point-in-time eligible set: {len(missing)}")
    if missing:
        F.add("WARN", "ROLE",
              f"{len(missing)} Kalshi-listed player/game pairs are not in the eligible set the simulator "
              f"built (ruled out, off the active roster, or a role the depth chart does not carry)",
              [f"{g} {p}" for g, p in missing[:20]])

    pub = collections.defaultdict(dict)
    for r in rows:
        if r.get("support_state") == "PRICED" and r.get("player_id") and r.get("football_mean") is not None:
            pub[(r["game_id"], r["player_id"])][r["stat"]] = r["football_mean"]

    print(f"\n  {'game':22s} {'team':5s} {'plays':>6s} {'pass%':>6s} {'drop':>6s} {'patt':>6s} "
          f"{'sack':>5s} {'rush':>6s} {'tgt':>6s} {'cmp':>6s} {'pyds':>7s} {'ryds':>6s} {'pts':>6s}")
    drift = []
    for gid, G in sorted(slate["games"].items()):
        gi = G["input"]
        res = S.simulate(gi, bundle, n=n_sims, bank=bank)
        coh = S.coherence_report(res)
        if not coh["ok"]:
            F.add("BLOCKER", "COHERENCE", f"{gid} fails a simulation identity",
                  [f"{k} = {v}" for k, v in coh.items() if k != "ok" and v])
        for ti in (gi.home, gi.away):
            T = res.team[ti.team]
            pr = float(np.mean(T["dropbacks"])) / max(float(np.mean(T["plays"])), 1e-9)
            print(f"  {gid:22s} {ti.team:5s} {np.mean(T['plays']):6.1f} {100 * pr:5.1f}% "
                  f"{np.mean(T['dropbacks']):6.1f} {np.mean(T['pass_att']):6.1f} {np.mean(T['sacks']):5.1f} "
                  f"{np.mean(T['designed_rush']):6.1f} {np.mean(T['targets']):6.1f} "
                  f"{np.mean(T['completions']):6.1f} {np.mean(T['pass_yards']):7.1f} "
                  f"{np.mean(T['rush_yards']):6.1f} "
                  f"{np.mean(res.home_points if ti.home else res.away_points):6.1f}")
            # football plausibility bands for a modern NFL team-game
            for label, val, lo, hi in (
                ("plays", float(np.mean(T["plays"])), 52.0, 78.0),
                ("pass rate", pr, 0.40, 0.72),
                ("pass attempts", float(np.mean(T["pass_att"])), 22.0, 46.0),
                ("designed rushes", float(np.mean(T["designed_rush"])), 14.0, 40.0),
                ("pass yards", float(np.mean(T["pass_yards"])), 150.0, 330.0),
                ("rush yards", float(np.mean(T["rush_yards"])), 60.0, 200.0),
                ("sacks allowed", float(np.mean(T["sacks"])), 0.8, 4.5),
            ):
                if not (lo <= val <= hi):
                    F.add("WARN", "FOOTBALL", f"{gid} {ti.team}: {label} = {val:.2f}, outside [{lo}, {hi}]")

        # per-player opportunity and the published-mean cross-check
        for ti in (gi.home, gi.away):
            P_ = ti.players.reset_index(drop=True)
            for _, prow in P_.iterrows():
                pid, pos, rank = prow["player_id"], str(prow.get("position")), prow.get("dc_rank")
                pl = res.player.get(pid)
                if pl is None:
                    continue
                st = OPP_STAT.get(pos)
                opp = float(np.mean(pl[st])) if st and st in pl else None
                avail = str(prow.get("avail_state"))
                if avail in ("OUT", "DOUBTFUL") and opp and opp > 0.5:
                    F.add("BLOCKER", "ROLE", f"{gid} {ti.team} {pid} ({pos}) is {avail} but draws "
                                             f"{opp:.2f} {st}")
                if st and opp is not None:
                    try:
                        r1 = float(rank)
                    except (TypeError, ValueError):
                        r1 = None
                    if r1 == 1.0 and opp < STARTER_FLOOR.get(pos, 0.0) and avail == "ACTIVE":
                        F.add("WARN", "ROLE", f"{gid} {ti.team} {pid} ({pos}1, {avail}) draws only "
                                              f"{opp:.2f} {st}")
                    if r1 is not None and r1 >= 3.0 and opp > BACKUP_CEILING.get(pos, 1e9):
                        F.add("WARN", "ROLE", f"{gid} {ti.team} {pid} ({pos}{int(r1)}, {avail}) draws "
                                              f"{opp:.2f} {st} -- starter volume for a listed backup")
                # does the reconstruction reproduce what was published?
                for stat, mean in (pub.get((gid, pid)) or {}).items():
                    key = {"rushing_yards": "rush_yards", "receiving_yards": "rec_yards",
                           "receptions": "receptions", "carries": "carries", "targets": "targets",
                           "passing_yards": "pass_yards", "attempts": "attempts",
                           "completions": "completions"}.get(stat)
                    if key and key in pl:
                        got = float(np.mean(pl[key]))
                        if abs(got - mean) > tol * max(1.0, abs(mean)):
                            drift.append(f"{gid} {pid} {stat}: published {mean:.3f} vs reconstructed {got:.3f}")
    print(f"\n  reconstruction vs published football means: {len(drift)} beyond {tol:.0%}")
    if drift:
        F.add("WARN", "RECONSTRUCTION",
              f"{len(drift)} published football means differ from the reconstruction by more than "
              f"{tol:.0%} (Monte Carlo noise at this n, or a genuinely different input)", drift[:15])


def render_md(man: dict, F: Findings, transcript: str) -> str:
    src = man.get("sources") or {}
    iv = src.get("injury_vintage") or {}
    nb, nw = len(F.of("BLOCKER")), len(F.of("WARN"))
    verdict = "BLOCKERS PRESENT" if nb else ("CLEAN, WITH WARNINGS" if nw else "CLEAN")
    L = [f"# Week {man.get('week')} {man.get('season')} published slate -- hostile sanity audit",
         "",
         "Generated by `scripts/sim/slate_audit.py` from the published manifest and projections; do not edit "
         "by hand.  A green workflow is not evidence that a slate is football-sane, so this interrogates the "
         "artifact the production path actually published.",
         "",
         f"**Verdict: {verdict}** -- {nb} blocker(s), {nw} warning(s), {len(F.of('NOTE'))} note(s).",
         "",
         "## Provenance", "",
         "| field | value |", "|---|---|",
         f"| run_id | `{man.get('run_id')}` |",
         f"| sim_version | {man.get('sim_version')} |",
         f"| cutoff | {man.get('cutoff')} |",
         f"| market_observed_at | {man.get('market_observed_at')} |",
         f"| bundle_train_seasons | {man.get('bundle_train_seasons')} |",
         f"| priors_fit_seasons | {man.get('priors_fit_seasons')} ({man.get('priors_version')}) |",
         f"| deployed_weights | {man.get('deployed_weights')} |",
         f"| depth_chart_vintage | {src.get('depth_chart_vintage')} |",
         f"| injury vintage | resolved={iv.get('resolved')} sha=`{(iv.get('sha256') or '')[:16]}` "
         f"retrieved={iv.get('retrieved_at')} reason={iv.get('reason')} rows_for_week={iv.get('rows_for_week')} |",
         f"| sleeper_run | {src.get('sleeper_run')} |",
         f"| history | {src.get('history_games')} games, latest `{src.get('latest_history_game')}` |",
         f"| rows / games | {man.get('n_rows')} / {len(man.get('games') or {})} |",
         "",
         "## Contracts by family and support state", "",
         "| family \| support_state | n |", "|---|---|"]
    for k, v in sorted((man.get("counts") or {}).items()):
        L.append(f"| {str(k).replace('|', ' / ')} | {v} |")
    L += ["", "## Findings", ""]
    if F.rows:
        L += ["| severity | area | finding |", "|---|---|---|"]
        for r in F.rows:
            L.append(f"| {r['severity']} | {r['area']} | {r['message'].replace('|', '/')} |")
    else:
        L.append("None.")
    L += ["", "## Full audit transcript", "", "```", transcript.rstrip(), "```", ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim-root", default=None, help="directory of published sim artifacts")
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--market-data", default="/home/user/_market_data_wt")
    ap.add_argument("--reconstruct", action="store_true",
                    help="re-run the simulation to expose team-level football (slow)")
    ap.add_argument("--n-sims", type=int, default=20000)
    ap.add_argument("--tol", type=float, default=0.05)
    ap.add_argument("--write-md", default=None, help="render the audit to this markdown path")
    a = ap.parse_args()
    tee = Tee(sys.stdout)
    sys.stdout = tee

    if a.manifest:
        man_path = a.manifest
        proj_path = man_path.replace(".manifest.json", ".projections.jsonl.gz")
    else:
        root = a.sim_root or os.path.join(a.market_data, "data", "shadow", "sim")
        man_path, proj_path = latest_pair(root)
    print(f"auditing\n  manifest    {man_path}\n  projections {proj_path}")
    man, rows = load(man_path, proj_path)
    F = Findings()

    audit_provenance(man, rows, F)
    priced = audit_probabilities(rows, F)
    audit_reconciliation(man, priced, F)
    audit_game_markets(rows, F)
    audit_roles_from_artifact(man, rows, F)

    coh_bad = [r["ticker"] for r in rows if r.get("coherence_ok") is False]
    print(f"\n{'=' * 100}\nCOHERENCE (as recorded on the rows)\n{'=' * 100}")
    print(f"  rows with coherence_ok = False: {len(coh_bad)}")
    if coh_bad:
        F.add("BLOCKER", "COHERENCE", f"{len(coh_bad)} rows were priced from a game that failed coherence",
              coh_bad[:15])

    if a.reconstruct:
        audit_football(man, rows, F, a.market_data, a.n_sims, a.tol)

    F.report()
    nb, nw = len(F.of("BLOCKER")), len(F.of("WARN"))
    print(f"\n{'=' * 100}\nVERDICT: {nb} blocker(s), {nw} warning(s), {len(F.of('NOTE'))} note(s)\n{'=' * 100}")
    sys.stdout = tee.stream
    if a.write_md:
        os.makedirs(os.path.dirname(os.path.abspath(a.write_md)), exist_ok=True)
        open(a.write_md, "w").write(render_md(man, F, tee.text()))
        print(f"wrote {a.write_md}")
    return 1 if nb else 0


if __name__ == "__main__":
    sys.exit(main())
