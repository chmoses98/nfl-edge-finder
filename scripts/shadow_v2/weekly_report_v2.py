#!/usr/bin/env python3
"""WEEKLY SHADOW RESEARCH REPORT + COVERAGE HEALTH GATE for one week of shadow-v2 evidence. No bet recommendations.

    python3 scripts/shadow_v2/weekly_report_v2.py --market-data /tmp/md --research data/shadow/v2/research --season 2026 --week 1 \
        [--board data/shadow/v2/board] [--horizons data/shadow/v2/horizons] --out data/shadow/v2/reports

Reads the derived research table (research_export_v2.py), the retained board rows, the horizon markers and the
projection run summaries. Every subgroup table is labelled HYPOTHESIS_GENERATING. The health block gives raw
counts and percentages for board capture, horizons, projection, settlement, close pairing, CLV, player context and
autopsy coverage so incompleteness cannot be missed.
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.evaluation import scorecard_v3 as S3                                      # noqa: E402
from nfl_edge.evaluation.clv import SIGN_CONVENTION                                     # noqa: E402
from nfl_edge.projection import horizons as HZ                                          # noqa: E402

REPORT_VERSION = "weekly-report-1.0.0"


def _f(v, nd=4):
    return "-" if v is None else (f"{v:.{nd}f}" if isinstance(v, float) else str(v))


def pct(n, d):
    return round(100.0 * n / d, 1) if d else None


def load_rows(path):
    with gzip.open(path, "rt") as f:
        return [json.loads(l) for l in f if l.strip()]


def health(rows: list, board_rows: list, markers: list, season: int, week: int) -> dict:
    with_p = [r for r in rows if r.get("contract_value") is not None]
    kicked = [r for r in with_p if r.get("kickoff_utc") and datetime.fromisoformat(r["kickoff_utc"]) < datetime.now(timezone.utc)]
    settleable = [r for r in with_p if r.get("flag_settlement_supported")]
    player_p = [r for r in with_p if r.get("engine") == "PLAYER"]
    nfl_board = [b for b in board_rows if "NFL_BOARD" in (b.get("stages") or [])]
    captured = [b for b in nfl_board if "CAPTURED" in (b.get("stages") or [])]
    quoted = [b for b in nfl_board if b.get("quoted")]
    hz = Counter()
    for m in markers:
        hz[m.get("status")] += 1
    per_h = Counter(r.get("horizon_label") for r in with_p)
    hq = Counter(r.get("horizon_quality") for r in with_p if r.get("horizon_label") not in (None, "CYCLE"))
    return {"season": season, "week": week,
            "BOARD_CAPTURE_COVERAGE": {"nfl_board_contracts": len(nfl_board), "captured": len(captured), "quoted_at_retention": len(quoted), "pct_captured": pct(len(captured), len(nfl_board))},
            "PROJECTION_COVERAGE": {"records": len(rows), "has_probability": len(with_p), "pct_of_records": pct(len(with_p), len(rows)), "contracts_with_probability": len({r["ticker"] for r in with_p}),
                                    "contracts_total": len({r["ticker"] for r in rows}), "pct_contracts": pct(len({r["ticker"] for r in with_p}), len({r["ticker"] for r in rows}))},
            "HORIZON_COMPLETENESS": {"records_by_horizon": dict(per_h), "quality": dict(hq), "markers": dict(hz), "missed_markers": hz.get("MISSED", 0)},
            "SETTLEMENT_COVERAGE": {"probability_rows": len(with_p), "settleable_rows": len(settleable), "pct_settleable": pct(len(settleable), len(with_p)),
                                    "settled_rows": sum(1 for r in with_p if r.get("settled_yes") is not None), "refused": dict(Counter(r.get("settlement_status") for r in with_p if r.get("settlement_status") and r.get("settled_yes") is None)),
                                    "pct_settled_of_kicked_off": pct(sum(1 for r in kicked if r.get("settled_yes") is not None), len(kicked))},
            "CLOSE_PAIRING_COVERAGE": {"kicked_off_rows": len(kicked), "close_ok": sum(1 for r in kicked if r.get("close_status") == "CLOSE_OK"), "close_one_sided": sum(1 for r in kicked if r.get("close_status") == "CLOSE_ONE_SIDED"),
                                       "close_missing": sum(1 for r in kicked if r.get("close_status") in (None, "CLV_CLOSE_MISSING")), "pct_paired": pct(sum(1 for r in kicked if r.get("close_status") in ("CLOSE_OK", "CLOSE_ONE_SIDED")), len(kicked)),
                                       "by_quality": dict(Counter(r.get("close_quality") for r in kicked)), "missing_reasons": dict(Counter(r.get("close_reason") for r in kicked if r.get("close_status") in (None, "CLV_CLOSE_MISSING")).most_common(8))},
            "CLV_COVERAGE": {"kicked_off_rows": len(kicked), "clv_ok": sum(1 for r in kicked if r.get("clv_status") == "CLV_OK"), "pct_clv": pct(sum(1 for r in kicked if r.get("clv_status") == "CLV_OK"), len(kicked)),
                             "no_view": sum(1 for r in kicked if r.get("clv_status") == "NO_VIEW")},
            "PLAYER_CONTEXT_COVERAGE": {"player_probability_rows": len(player_p), "injury_known_pct": pct(sum(1 for r in player_p if r.get("ctx_injury_state") in ("LISTED", "NOT_LISTED")), len(player_p)),
                                        "depth_chart_known_pct": pct(sum(1 for r in player_p if r.get("ctx_depth_chart_rank") is not None), len(player_p)),
                                        "availability_known_pct": pct(sum(1 for r in player_p if r.get("ctx_availability_state") not in (None, "UNKNOWN")), len(player_p)),
                                        "weather_known_pct": pct(sum(1 for r in player_p if r.get("ctx_weather_state") == "KNOWN"), len(player_p))},
            "AUTOPSY_COVERAGE": {"data_arm_settled": sum(1 for r in with_p if r.get("model_arm") == "DATA_PLAYER_DIST" and r.get("settled_yes") is not None),
                                 "autopsied": sum(1 for r in with_p if r.get("autopsy_classification")), "by_class": dict(Counter(r.get("autopsy_classification") for r in with_p if r.get("autopsy_classification")))},
            "UNSUPPORTED_RETENTION": {"board_rows_retained": len(board_rows), "unsupported_states": dict(Counter(b.get("terminal_state") for b in nfl_board if b.get("terminal_state") not in ("PRICED", "PROJECTABLE_NOT_YET_VALIDATED")))}}


def render(sc: dict, h: dict, rows: list, label: str) -> str:
    L = [f"# Weekly shadow research report — {label}", "", f"report {REPORT_VERSION}; generated {datetime.now(timezone.utc).isoformat()}", "",
         "**RESEARCH ONLY. No bet recommendations. Every subgroup table below is HYPOTHESIS_GENERATING; Week-1 patterns cannot be confirmed on Week 1.**", "",
         f"**CLV sign convention:** {SIGN_CONVENTION}. Positive CLV is not proven positive EV (calibration, execution, fees, liquidity, sample and prospective validation are all still required).", ""]
    L += ["## Coverage health", "", "| gate | counts | % |", "|---|---|---|"]
    for k in ("BOARD_CAPTURE_COVERAGE", "PROJECTION_COVERAGE", "HORIZON_COMPLETENESS", "SETTLEMENT_COVERAGE", "CLOSE_PAIRING_COVERAGE", "CLV_COVERAGE", "PLAYER_CONTEXT_COVERAGE", "AUTOPSY_COVERAGE", "UNSUPPORTED_RETENTION"):
        v = h[k]; pcts = {kk: vv for kk, vv in v.items() if "pct" in kk}
        counts = {kk: vv for kk, vv in v.items() if "pct" not in kk}
        L.append(f"| {k} | {json.dumps(counts, default=str)[:300]} | {json.dumps(pcts)} |")
    L += ["", "## Horizon health", "", f"records by horizon: {h['HORIZON_COMPLETENESS']['records_by_horizon']}; quality: {h['HORIZON_COMPLETENESS']['quality']}; markers: {h['HORIZON_COMPLETENESS']['markers']}", ""]
    sy = sc.get("synchronization") or {}
    if sy:
        L += ["## Market/model synchronization", "",
              "A row is SYNCHRONIZED when every model input was observable at or before the market cutoff it is "
              "scored against. When it is not, a disagreement may be newer information rather than better "
              "modelling, so the two are counted and scored separately and never pooled into an edge claim.", "",
              f"counts: {json.dumps(sy.get('counts') or {}, default=str)}", "",
              f"carrying a probability: {json.dumps(sy.get('with_probability') or {}, default=str)}", "",
              f"skew seconds: median {sy.get('skew_seconds', {}).get('median')}, max {sy.get('skew_seconds', {}).get('max')}", "",
              f"**Edge claims may be read only from `{sy.get('synchronized_edge_basis')}`.**", ""]
        for st, b in sorted((sc.get("by_synchronization") or {}).get("PROSPECTIVE_FROZEN", {}).items()):
            o = b["overall"]["outcome"]
            L += [f"* `{st}`: {b['n_with_probability']} rows with a probability; settled {o.get('n', 0)}; "
                  f"model-market {_f(o.get('model_minus_market_brier'))} ± {_f(o.get('model_minus_market_se'))}"]
        L += [""]
    for cls, b in sc["by_evidence_class"].items():
        o, c = b["overall"]["outcome"], b["overall"]["clv"]
        L += [f"## {cls}: model vs market vs close (DESCRIPTIVE)", "", f"settled {o.get('n', 0)} rows / {o.get('n_games', 0)} games; Brier model {_f(o.get('brier_model'))}, market@horizon {_f(o.get('brier_market_horizon'))}, market@close {_f(o.get('brier_market_close'))}; "
              f"model-market {_f(o.get('model_minus_market_brier'))} ± {_f(o.get('model_minus_market_se'))}; model-close {_f(o.get('model_minus_close_brier'))} ± {_f(o.get('model_minus_close_se'))}", "",
              f"CLV: ok {c['n_clv_ok']}, close missing {c['n_close_missing']}, no view {c['n_no_view']}; mean {_f(c.get('mean_clv_mid'))} ± {_f(c.get('se_clv_mid_clustered'))}, median {_f(c.get('median_clv_mid'))}, +rate {_f(c.get('positive_clv_rate'), 3)}, toward-rate {_f(c.get('movement_toward_rate'), 3)}", ""]
        for seg in ("model_arm", "family_group", "horizon_label", "disagreement_band", "close_quality", "horizon_quality", "ctx_availability_state", "ladder_identification", "width_band"):
            s = b["segments"].get(seg) or {}
            if not s:
                continue
            L += [f"### by {seg} (HYPOTHESIS_GENERATING)", "", "| value | n | games | Brier model | market@h | model-market ± se | model-close | mean CLV | +CLV | toward | P&L net |", "|---|---|---|---|---|---|---|---|---|---|---|"]
            for k, m in s.items():
                o2, c2, e2 = m["outcome"], m["clv"], m["executable"]
                L.append(f"| {k} | {m['n']} | {m['n_games']} | {_f(o2.get('brier_model'))} | {_f(o2.get('brier_market_horizon'))} | {_f(o2.get('model_minus_market_brier'))} ± {_f(o2.get('model_minus_market_se'))} | {_f(o2.get('model_minus_close_brier'))} | {_f(c2.get('mean_clv_mid'))} | {_f(c2.get('positive_clv_rate'), 3)} | {_f(c2.get('movement_toward_rate'), 3)} | {_f(e2.get('pnl_net_per_contract'))} |")
            L.append("")
        if b["arm_by_family"]:
            L += ["### which arm best predicted outcome / close / movement, per family (HYPOTHESIS_GENERATING)", "", "| family | outcome | close | movement |", "|---|---|---|---|"]
            for fam, v in sorted(b["arm_by_family"].items()):
                L.append(f"| {fam} | {v['best_outcome_arm']} | {v['best_close_arm']} | {v['best_movement_arm']} |")
            L.append("")
        L.append(f"candidate slices considered: {b['candidate_slices_considered']}")
        L.append("")
    au = h["AUTOPSY_COVERAGE"]["by_class"]
    L += ["## Player autopsy (DESCRIPTIVE)", "", ("| class | n |\n|---|---|\n" + "\n".join(f"| {k} | {v} |" for k, v in sorted(au.items(), key=lambda x: -x[1]))) if au else "no settled DATA-arm rows yet", ""]
    dq = []
    hc = h["HORIZON_COMPLETENESS"]
    if hc.get("missed_markers"):
        dq.append(f"{hc['missed_markers']} horizon markers MISSED")
    if (hc.get("quality") or {}).get("LATE_DEGRADED"):
        dq.append(f"{hc['quality']['LATE_DEGRADED']} probability rows at LATE_DEGRADED horizons")
    cp = h["CLOSE_PAIRING_COVERAGE"]
    if cp.get("close_missing"):
        dq.append(f"{cp['close_missing']} kicked-off rows without a valid close: {cp.get('missing_reasons')}")
    pc = h["PLAYER_CONTEXT_COVERAGE"]
    for k in ("availability_known_pct", "weather_known_pct", "injury_known_pct"):
        if (pc.get(k) or 0) < 50:
            dq.append(f"player context {k} = {pc.get(k)}%")
    if h["SETTLEMENT_COVERAGE"].get("refused"):
        dq.append(f"settlement refusals: {h['SETTLEMENT_COVERAGE']['refused']}")
    L += ["## Data quality (what makes this week's evidence weaker)", ""] + ([f"- {d}" for d in dq] or ["- nothing flagged by the gate"]) + [""]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", required=True)
    ap.add_argument("--research", default=os.path.join(ROOT, "data", "shadow", "v2", "research"))
    ap.add_argument("--board", default="")
    ap.add_argument("--horizons", default="")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "shadow", "v2", "reports"))
    ap.add_argument("--season", type=int, default=2026)
    ap.add_argument("--week", type=int, required=True)
    a = ap.parse_args(argv)
    label = f"{a.season}_wk{a.week:02d}"
    md = os.path.join(a.market_data, "data", "shadow", "v2")
    path = os.path.join(a.research, f"{label}.research.jsonl.gz")
    if not os.path.exists(path):
        path = os.path.join(md, "research", f"{label}.research.jsonl.gz")
    rows = load_rows(path) if os.path.exists(path) else []
    board_rows = []
    for root in [a.board, os.path.join(md, "board")]:
        if root and os.path.isdir(root):
            fs = sorted(glob.glob(os.path.join(root, "*.board.jsonl.gz")))
            if fs:
                board_rows = load_rows(fs[-1]); break
    markers = []
    for root in [a.horizons, os.path.join(md, "horizons")]:
        if root and os.path.isdir(root):
            for p in glob.glob(os.path.join(root, "*.json")):
                try:
                    markers.append(json.load(open(p)))
                except (OSError, ValueError):
                    pass
    sc = S3.build(rows)
    h = health(rows, board_rows, markers, a.season, a.week)
    os.makedirs(a.out, exist_ok=True)
    json.dump(h, open(os.path.join(a.out, f"{label}.health.json"), "w"), indent=1, default=str)
    open(os.path.join(a.out, f"{label}.WEEKLY_REPORT.md"), "w").write(render(sc, h, rows, label))
    print(json.dumps({k: v for k, v in h.items() if k not in ("season", "week")}, indent=1, default=str)[:4000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
