#!/usr/bin/env python3
"""Run RUN NFL's fresh context capture CONCURRENTLY with the market-data fetch, without changing what it captures.

    python3 scripts/handicap/concurrent_context.py start --dir /tmp/ctx          # runs scripts/data/context_capture.py
    python3 scripts/handicap/concurrent_context.py wait --dir /tmp/ctx --tree-state /tmp/md/data/context/state.json

WHY. Profiled on the week-3 horizon builds (36257597988, 36268362044): the context capture (~4.5-5.8 min, almost
all of it sequential NWS/Open-Meteo calls with a 0.5s courtesy sleep) ran strictly AFTER the ~5 minute market-data
fetch, although it reads nothing from market-data except `data/context/state.json` -- the change-suppression cache.
Running the two at once takes ~4.5 minutes off every fresh build and freezes the context closer to the trigger.

WHAT MUST NOT CHANGE. The capture is the same script with the same inputs. Its only market-data input, state.json,
is fetched ahead of the tree (GitHub contents API) and saved as `--state`; `wait` then compares it with the
state.json of the tree the job actually fetched. Equal -> the capture had exactly the input it would have had when
run sequentially, so its output is the one the sequential job would have produced. Different, or the background
capture never started, or it hung -> `wait` says so (exit 3/4) and the workflow re-runs the capture sequentially,
exactly as before this existed. A capture that FAILED keeps failing the run (its own exit code), as before.

Exit codes of `wait`
  0   background capture finished OK with the same state.json the tree holds
  3   STATE_MISMATCH -- rerun sequentially
  4   NOT_STARTED / TIMED_OUT (process group killed) -- rerun sequentially
  n   the capture's own nonzero exit code (e.g. 2 = a source failed closed) -- the run fails, as before
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time

STATE_MISMATCH, NOT_STARTED = 3, 4
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CAPTURE = os.path.join(ROOT, "scripts", "data", "context_capture.py")


def _load_state(path: str | None):
    """state.json as data; a missing file is `{}` -- the same fallback the sequential step uses."""
    if not path or not os.path.exists(path):
        return {}
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None                                # unreadable: never equal to anything


def start(d: str, cmd: list, env=None) -> int:
    os.makedirs(d, exist_ok=True)
    for name in ("rc", "pid"):
        try:
            os.remove(os.path.join(d, name))
        except FileNotFoundError:
            pass
    script = " ".join(_q(c) for c in cmd) + f'; echo $? > {_q(os.path.join(d, "rc.tmp"))}; ' \
             f'mv {_q(os.path.join(d, "rc.tmp"))} {_q(os.path.join(d, "rc"))}'
    with open(os.path.join(d, "capture.log"), "wb") as log, open(os.devnull, "rb") as nul:
        p = subprocess.Popen(["bash", "-c", script], stdout=log, stderr=subprocess.STDOUT, stdin=nul,
                             start_new_session=True, env=env)
    with open(os.path.join(d, "pid"), "w") as f:
        f.write(str(p.pid))
    print(f"background context capture started (pid {p.pid}); log {os.path.join(d, 'capture.log')}")
    return 0


def _q(s: str) -> str:
    import shlex
    return shlex.quote(str(s))


def wait(d: str, *, tree_state: str | None, used_state: str | None, timeout_s: float, poll_s: float = 2.0) -> int:
    pid_path, rc_path = os.path.join(d, "pid"), os.path.join(d, "rc")
    if not os.path.exists(pid_path):
        print("NOT_STARTED: no background capture was started; run it sequentially")
        return NOT_STARTED
    deadline = time.time() + timeout_s
    while not os.path.exists(rc_path):
        if time.time() > deadline:
            try:
                os.killpg(int(open(pid_path).read().strip()), signal.SIGTERM)
            except (OSError, ValueError):
                pass
            print(f"TIMED_OUT: the background capture did not finish within {timeout_s / 60:.0f} min; killed; "
                  "run it sequentially")
            return NOT_STARTED
        time.sleep(poll_s)
    try:
        rc = int(open(rc_path).read().strip() or "1")
    except ValueError:
        rc = 1
    log = os.path.join(d, "capture.log")
    if os.path.exists(log):
        tail = open(log, errors="replace").read().splitlines()[-5:]
        print("\n".join(tail))
    if rc != 0:
        print(f"the background context capture exited {rc}")
        return rc
    used, tree = _load_state(used_state), _load_state(tree_state)
    if used is None or tree is None or used != tree:
        print("STATE_MISMATCH: the state.json the background capture used differs from the fetched tree's; "
              "run it sequentially so the capture has exactly the sequential input")
        return STATE_MISMATCH
    print("background context capture finished with the same state.json the fetched tree holds")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start")
    s.add_argument("--dir", required=True)
    s.add_argument("argv", nargs=argparse.REMAINDER)
    w = sub.add_parser("wait")
    w.add_argument("--dir", required=True)
    w.add_argument("--tree-state", required=True, help="state.json in the fetched market-data tree (may be absent)")
    w.add_argument("--used-state", default=None, help="the state.json the background capture was given")
    w.add_argument("--timeout-min", type=float, default=20.0)
    a = ap.parse_args(argv)
    if a.cmd == "start":
        cmd = a.argv[1:] if a.argv and a.argv[0] == "--" else a.argv
        return start(a.dir, cmd or [sys.executable, CAPTURE])
    return wait(a.dir, tree_state=a.tree_state, used_state=a.used_state or os.path.join(a.dir, "state.used.json"),
                timeout_s=a.timeout_min * 60)


if __name__ == "__main__":
    sys.exit(main())
