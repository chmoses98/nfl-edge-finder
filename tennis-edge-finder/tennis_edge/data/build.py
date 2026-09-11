"""Assemble the canonical historical match table from every acquired source snapshot, with provenance.

Source priority for the SAME match (dedupe key: tour, tourney_date, normalised winner/loser names, round):
  1. sackmann fork/upstream snapshot (schema of record; numeric Sackmann ids)
  2. TML-Database (ATP main tour 1968-2026; ATP-site alphanumeric ids)
  3. mirror TML challenger files (ATP Challenger 2000-2026)
Player ids from different id systems are never merged by this builder: rows carry `id_system`
('sackmann' | 'tml') and identity resolution across systems is a separate, confidence-scored step
(tennis_edge.identity). Ratings are therefore built PER id_system unless a verified crosswalk exists.

Outputs (data/processed/):
  matches.parquet           clean singles matches, all tours/levels, provenance columns
  matches_quarantine.parquet
  build_manifest.json       per-source counts, run ids, hashes, dedupe stats
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import re
from datetime import datetime, timezone

import pandas as pd

from tennis_edge.data.sackmann import normalize_matches, validate_matches, CANONICAL_COLUMNS
from tennis_edge.data.sources import read_csv_gz
from tennis_edge.identity.names import normalize_name

PROJ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SOURCES = os.path.join(PROJ, "data", "sources")
PROCESSED = os.path.join(PROJ, "data", "processed")


def _runs():
    return sorted(d for d in glob.glob(os.path.join(SOURCES, "*")) if os.path.isdir(d))


def locate(sub: str) -> str | None:
    """Latest source run directory that contains `sub` (relative path)."""
    for r in reversed(_runs()):
        if os.path.exists(os.path.join(r, sub)):
            return r
    return None


def _load_group(paths, tour, kind, id_system, source_label, seen):
    clean_parts, q_parts, counts = [], [], {}
    for p in sorted(paths):
        m = re.search(r"(\d{4})", os.path.basename(p))
        raw = read_csv_gz(p)
        res = normalize_matches(raw, tour, os.path.basename(p), kind)
        clean, q = validate_matches(res.frame, seen)
        clean = clean.assign(id_system=id_system, source_label=source_label, source_path=os.path.relpath(p, PROJ))
        q = q.assign(id_system=id_system, source_label=source_label, source_path=os.path.relpath(p, PROJ))
        clean_parts.append(clean); q_parts.append(q)
        counts[os.path.basename(p)] = {"raw": int(len(raw)), "clean": int(len(clean)), "quarantine": int(len(q))}
    return clean_parts, q_parts, counts


def build(min_year: int = 1990, write: bool = True) -> dict:
    manifest = {"built_at": datetime.now(timezone.utc).isoformat(), "sources": {}, "min_year": min_year}
    clean_all, q_all = [], []
    # 1. Sackmann snapshots (fork or upstream)
    for tour, kinds in (("ATP", ["atp_matches_{y}", "atp_matches_qual_chall_{y}", "atp_matches_futures_{y}"]),
                        ("WTA", ["wta_matches_{y}", "wta_matches_qual_itf_{y}"])):
        run = locate(f"sackmann/tennis_{tour.lower()}")
        if not run:
            manifest["sources"][f"sackmann_{tour}"] = {"status": "ABSENT"}
            continue
        base = os.path.join(run, f"sackmann/tennis_{tour.lower()}")
        for kind_pat in kinds:
            kind = "main" if kind_pat.endswith("matches_{y}") else ("qual_chall" if "qual_chall" in kind_pat else "futures" if "futures" in kind_pat else "qual_itf")
            pat = re.compile("^" + re.escape(kind_pat).replace(r"\{y\}", r"(\d{4})") + r"\.csv\.gz$")
            paths = [p for p in glob.glob(os.path.join(base, "*.csv.gz"))
                     if (mm := pat.match(os.path.basename(p))) and int(mm.group(1)) >= min_year]
            seen = set()
            c, q, counts = _load_group(paths, tour, kind, "sackmann", f"sackmann_{tour}_{kind}", seen)
            clean_all += c; q_all += q
            manifest["sources"][f"sackmann_{tour}_{kind}"] = {"status": "OK", "run": os.path.basename(run), "files": counts}
    # 2. TML ATP main tour
    run = locate("tml")
    if run:
        paths = [p for p in glob.glob(os.path.join(run, "tml", "*.csv.gz")) if (mm := re.match(r"(\d{4})\.csv\.gz$", os.path.basename(p))) and int(mm.group(1)) >= min_year]
        c, q, counts = _load_group(paths, "ATP", "main", "tml", "tml_ATP_main", set())
        clean_all += c; q_all += q
        manifest["sources"]["tml_ATP_main"] = {"status": "OK", "run": os.path.basename(run), "files": counts}
    else:
        manifest["sources"]["tml_ATP_main"] = {"status": "ABSENT"}
    # 3. TML challenger files from the mirror
    run = locate("tennis_data_mirrors/gmalbert__tennis-predictions/tml-data")
    if run:
        paths = [p for p in glob.glob(os.path.join(run, "tennis_data_mirrors/gmalbert__tennis-predictions/tml-data", "*_challenger.csv.gz"))
                 if int(re.match(r"(\d{4})", os.path.basename(p)).group(1)) >= min_year]
        c, q, counts = _load_group(paths, "ATP", "qual_chall", "tml", "tml_ATP_challenger", set())
        clean_all += c; q_all += q
        manifest["sources"]["tml_ATP_challenger"] = {"status": "OK", "run": os.path.basename(run), "files": counts}
    else:
        manifest["sources"]["tml_ATP_challenger"] = {"status": "ABSENT"}

    if not clean_all:
        raise SystemExit("no sources found")
    df = pd.concat(clean_all, ignore_index=True)
    q = pd.concat(q_all, ignore_index=True) if q_all else pd.DataFrame(columns=CANONICAL_COLUMNS + ["reason", "reasons"])
    # cross-source dedupe: same tour/date/round/normalised names -> keep highest-priority source
    prio = {"sackmann": 0, "tml": 1}
    df["_wn"] = df["winner_name"].map(lambda x: normalize_name(x) if x else "")
    df["_ln"] = df["loser_name"].map(lambda x: normalize_name(x) if x else "")
    df["_prio"] = df["id_system"].map(prio)
    df["dedupe_key"] = df["tour"] + "|" + df["tourney_date"].astype(str) + "|" + df["round"].astype(str) + "|" + df["_wn"] + "|" + df["_ln"]
    df = df.sort_values(["dedupe_key", "_prio"], kind="mergesort")
    dups = df.duplicated("dedupe_key", keep="first")
    manifest["cross_source_duplicates_dropped"] = int(dups.sum())
    df = df.loc[~dups].drop(columns=["_wn", "_ln", "_prio"]).reset_index(drop=True)
    df["season"] = df["tourney_date"].map(lambda d: d.year if d is not None else None)
    manifest["rows"] = int(len(df)); manifest["quarantine_rows"] = int(len(q))
    manifest["by_tour_level"] = {f"{k[0]}|{k[1]}": int(v) for k, v in df.groupby(["tour", "level_canonical"]).size().items()}
    manifest["by_id_system"] = {k: int(v) for k, v in df["id_system"].value_counts().items()}
    manifest["seasons"] = {k: int(v) for k, v in df["season"].value_counts().sort_index().items()}
    if write:
        os.makedirs(PROCESSED, exist_ok=True)
        df2 = df.copy(); df2["set_scores"] = df2["set_scores"].map(json.dumps)
        q2 = q.copy()
        if "set_scores" in q2:
            q2["set_scores"] = q2["set_scores"].map(json.dumps)
        df2.to_parquet(os.path.join(PROCESSED, "matches.parquet"), index=False)
        q2.to_parquet(os.path.join(PROCESSED, "matches_quarantine.parquet"), index=False)
        manifest["matches_sha256"] = hashlib.sha256(open(os.path.join(PROCESSED, "matches.parquet"), "rb").read()).hexdigest()
        json.dump(manifest, open(os.path.join(PROCESSED, "build_manifest.json"), "w"), indent=1, default=str)
    return manifest


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.ERROR)
    m = build()
    print(json.dumps({k: v for k, v in m.items() if k != "sources"}, indent=1, default=str))
    for k, v in m["sources"].items():
        print(k, v.get("status"), sum(f["clean"] for f in v.get("files", {}).values()) if v.get("files") else "")
