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


BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36",
    "Accept": "*/*", "Accept-Language": "en-GB,en;q=0.9", "Referer": "http://www.tennis-data.co.uk/alldata.php",
}


def fetch(url, timeout=60, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), r.status


def fetch_retry(url, attempts=3, headers=None, timeout=60):
    import time as _t
    last = None
    for i in range(attempts):
        try:
            return fetch(url, timeout=timeout, headers=headers)
        except Exception as e:  # noqa: BLE001
            last = e
            _t.sleep(2 * (i + 1))
    raise last


def clone_repo(owner, repo, work, branch="master"):
    """Obtain a public repo snapshot WITHOUT git credentials.

    Primary: the codeload zip archive over plain HTTPS (no auth header can leak in). Fallback: git clone
    with terminal prompts disabled and the credential helper cleared, run from a directory OUTSIDE the
    checked-out project so the Actions token stored in the project's repo-local git config cannot be
    attached to a request for someone else's repository (that produced
    'could not read Username for https://github.com' on the first run).
    """
    import zipfile
    dest = os.path.join(work, repo)
    if os.path.exists(dest):
        shutil.rmtree(dest)
    last = None
    for br in (branch, "main"):
        url = f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{br}"
        for attempt in range(3):
            try:
                data, status = fetch(url, timeout=300)
                if status != 200 or len(data) < 1000:
                    raise RuntimeError(f"status {status} bytes {len(data)}")
                zpath = os.path.join(work, f"{repo}.zip")
                with open(zpath, "wb") as f:
                    f.write(data)
                with zipfile.ZipFile(zpath) as z:
                    top = z.namelist()[0].split("/")[0]
                    z.extractall(work)
                os.replace(os.path.join(work, top), dest)
                os.remove(zpath)
                sha = f"zip:{br}:{hashlib.sha256(data).hexdigest()[:16]}"
                # the zip archive carries no commit metadata; record the retrieval time instead
                return dest, sha, datetime.now(timezone.utc).isoformat()
            except Exception as e:  # noqa: BLE001
                last = e
                import time as _t
                _t.sleep(3 * (attempt + 1))
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    outside = os.path.join(os.environ.get("RUNNER_TEMP", "/tmp"), "tef_clone")
    os.makedirs(outside, exist_ok=True)
    tmp = os.path.join(outside, repo)
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    r = subprocess.run(["git", "-c", "credential.helper=", "clone", "--depth", "1", f"https://github.com/{owner}/{repo}.git", tmp],
                       cwd=outside, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"zip failed ({last}); git clone failed: {r.stderr[-300:]}")
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp, capture_output=True, text=True, check=True).stdout.strip()
    date = subprocess.run(["git", "log", "-1", "--format=%cI"], cwd=tmp, capture_output=True, text=True, check=True).stdout.strip()
    shutil.move(tmp, dest)
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
            for scheme, ext in (("https", "xlsx"), ("https", "xls"), ("http", "xlsx"), ("http", "xls")):
                url = f"{scheme}://www.tennis-data.co.uk/{y}{suffix}/{y}.{ext}"
                try:
                    data, status = fetch_retry(url, attempts=2, headers=BROWSER_HEADERS)
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

    # ---- tennis-data mirrors on GitHub (lower authority: third-party copies). Only used to fill years the
    # primary site did not serve; provenance is recorded per file so the registry can rank them.
    if td["files"] < (y1 - y0 + 1):
        import re as _re
        for owner, repo in (("0xsimulacra", "MLT"), ("gmalbert", "tennis-predictions")):
            try:
                dest, sha, date = clone_repo(owner, repo, work)
                n = 0
                for root, _dirs, files in os.walk(dest):
                    for fn in files:
                        m = _re.search(r"(20\d\d)", fn)
                        if not m or not fn.lower().endswith((".xlsx", ".xls", ".csv")):
                            continue
                        rel = os.path.relpath(os.path.join(root, fn), dest)
                        add_file(f"mirror:{owner}/{repo}", rel, os.path.join(root, fn), f"tennis_data_mirrors/{owner}__{repo}/{rel}.gz",
                                 {"year_guess": int(m.group(1)), "authority": "MIRROR"})
                        n += 1
                manifest["sources"][f"mirror:{owner}/{repo}"] = {"url": f"https://github.com/{owner}/{repo}", "commit": sha, "commit_date": date,
                                                                  "files": n, "authority": "MIRROR", "note": "third-party copy of tennis-data.co.uk files; verify against primary when reachable"}
                print(f"mirror {owner}/{repo}: {n} files", flush=True)
            except Exception as e:  # noqa: BLE001
                manifest["failures"].append({"source": f"mirror:{owner}/{repo}", "error": str(e)[:300]})

    manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
    manifest["total_bytes_gz"] = sum(f["bytes_gz"] for f in manifest["files"])
    with open(os.path.join(out, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    print(json.dumps({k: v for k, v in manifest.items() if k != "files"}, indent=1))
    return 0 if not manifest["failures"] else 2


if __name__ == "__main__":
    sys.exit(main())
