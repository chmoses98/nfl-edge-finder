#!/usr/bin/env python3
"""Acquire raw historical tennis sources on a machine with open internet (GitHub Actions runner).

The development sandbox has an egress allowlist that blocks github.com raw content, tennis-data.co.uk
and every tennis site, so the raw snapshots are fetched here, hashed, gzip-compressed, manifested
and published to the orphan `tennis-data` branch, from which any environment can `git fetch` them.

Sources (all free; licence details in docs/DATA_SOURCES.md):
  * JeffSackmann/tennis_atp   (CC BY-NC-SA 4.0)  matches 1968-, qual/chall, futures, doubles, rankings, players
  * JeffSackmann/tennis_wta   (CC BY-NC-SA 4.0)  matches, qual/itf, rankings, players
  * JeffSackmann/tennis_MatchChartingProject (CC BY-NC-SA 4.0) -- overview/serve stat files only
  * tennis-data.co.uk         (free for personal use)  ATP 2000-, WTA 2007-: results + bookmaker odds

Output: <out>/<run_id>/... plus manifest.json with sha256, bytes, rows (for csv), source commit SHAs.
Never overwrites an existing run directory.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone

UA = "tennis-edge-finder/0.1 (research data acquisition; github.com/chmoses98/nfl-edge-finder)"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def gz_copy(src, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(src, "rb") as fi, gzip.open(dest, "wb", compresslevel=6) as fo:
        shutil.copyfileobj(fi, fo)


def count_rows(path):
    n = 0
    with open(path, "rb") as f:
        for _ in f:
            n += 1
    return max(n - 1, 0)


def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), r.status


def clone_repo(owner, repo, work):
    dest = os.path.join(work, repo)
    if os.path.exists(dest):
        shutil.rmtree(dest)
    subprocess.run(["git", "clone", "--depth", "1", f"https://github.com/{owner}/{repo}.git", dest], check=True)
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=dest, capture_output=True, text=True, check=True).stdout.strip()
    date = subprocess.run(["git", "log", "-1", "--format=%cI"], cwd=dest, capture_output=True, text=True, check=True).stdout.strip()
    return dest, sha, date


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ap.add_argument("--work", default=None)
    ap.add_argument("--skip-mcp", action="store_true")
    ap.add_argument("--tennis-data-years", default="2000-2026")
    a = ap.parse_args()
    proj = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = os.path.join(a.out or os.path.join(proj, "data", "sources"), run_id)
    if os.path.exists(out):
        raise SystemExit(f"refusing to overwrite {out}")
    os.makedirs(out)
    work = a.work or os.path.join(proj, "data", "cache", "bootstrap_work")
    os.makedirs(work, exist_ok=True)
    manifest = {"run_id": run_id, "started_at": datetime.now(timezone.utc).isoformat(), "sources": {}, "files": [], "failures": []}

    def add_file(source, rel_src_name, local_path, dest_rel, extra=None):
        dest = os.path.join(out, dest_rel)
        gz_copy(local_path, dest)
        rec = {"source": source, "name": rel_src_name, "path": dest_rel, "sha256_raw": sha256(local_path),
               "bytes_raw": os.path.getsize(local_path), "bytes_gz": os.path.getsize(dest)}
        if local_path.endswith(".csv"):
            rec["rows"] = count_rows(local_path)
        if extra:
            rec.update(extra)
        manifest["files"].append(rec)

    # ---- Sackmann repos
    repos = [("JeffSackmann", "tennis_atp", None), ("JeffSackmann", "tennis_wta", None)]
    if not a.skip_mcp:
        repos.append(("JeffSackmann", "tennis_MatchChartingProject",
                      lambda fn: fn.endswith(("-matches.csv", "-stats-Overview.csv", "-stats-ServeBasics.csv", "-stats-ReturnOutcomes.csv", "-stats-KeyPointsServe.csv", "-stats-KeyPointsReturn.csv"))))
    for owner, repo, keep in repos:
        try:
            dest, sha, date = clone_repo(owner, repo, work)
            manifest["sources"][repo] = {"url": f"https://github.com/{owner}/{repo}", "commit": sha, "commit_date": date,
                                         "licence": "CC BY-NC-SA 4.0 (per repo README)", "retrieved_at": datetime.now(timezone.utc).isoformat()}
            n = 0
            for fn in sorted(os.listdir(dest)):
                p = os.path.join(dest, fn)
                if not os.path.isfile(p) or not fn.endswith((".csv", ".txt", ".md")):
                    continue
                if keep and not keep(fn) and not fn.endswith((".md", ".txt")):
                    continue
                add_file(repo, fn, p, f"sackmann/{repo}/{fn}.gz")
                n += 1
            manifest["sources"][repo]["files"] = n
            print(f"{repo}: {n} files @ {sha[:10]}", flush=True)
        except Exception as e:  # noqa: BLE001
            manifest["failures"].append({"source": repo, "error": str(e)[:300]})
            print(f"FAILED {repo}: {e}", flush=True)

    # ---- tennis-data.co.uk (results + bookmaker odds)
    y0, y1 = [int(x) for x in a.tennis_data_years.split("-")]
    td = {"url": "http://www.tennis-data.co.uk/", "licence": "free download; site terms: personal/non-commercial use; attribution",
          "retrieved_at": datetime.now(timezone.utc).isoformat(), "files": 0}
    manifest["sources"]["tennis_data_co_uk"] = td
    for tour, suffix in (("atp", ""), ("wta", "w")):
        for y in range(y0, y1 + 1):
            got = False
            for ext in ("xlsx", "xls"):
                url = f"http://www.tennis-data.co.uk/{y}{suffix}/{y}.{ext}"
                try:
                    data, status = fetch(url)
                    if status != 200 or len(data) < 2000:
                        continue
                    local = os.path.join(work, f"td_{tour}_{y}.{ext}")
                    with open(local, "wb") as f:
                        f.write(data)
                    add_file("tennis_data_co_uk", f"{y}{suffix}/{y}.{ext}", local, f"tennis_data/{tour}/{y}.{ext}.gz", {"tour": tour, "year": y, "url": url})
                    td["files"] += 1
                    got = True
                    break
                except Exception as e:  # noqa: BLE001
                    last = str(e)[:200]
            if not got:
                manifest["failures"].append({"source": "tennis_data_co_uk", "tour": tour, "year": y, "error": locals().get("last", "no file")})
    for extra_url, name in (("http://www.tennis-data.co.uk/notes.txt", "notes.txt"),):
        try:
            data, status = fetch(extra_url)
            local = os.path.join(work, name)
            open(local, "wb").write(data)
            add_file("tennis_data_co_uk", name, local, f"tennis_data/{name}.gz")
        except Exception as e:  # noqa: BLE001
            manifest["failures"].append({"source": "tennis_data_co_uk", "file": name, "error": str(e)[:200]})

    manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
    manifest["total_bytes_gz"] = sum(f["bytes_gz"] for f in manifest["files"])
    with open(os.path.join(out, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    print(json.dumps({k: v for k, v in manifest.items() if k != "files"}, indent=1))
    return 0 if not manifest["failures"] else 2


if __name__ == "__main__":
    sys.exit(main())
