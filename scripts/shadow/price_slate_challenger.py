#!/usr/bin/env python3
"""shadow-0.5.0 challenger pricer (RESEARCH / SHADOW ONLY). Runs the frozen incumbent pricer's code path with the
two mean-projection repairs of nfl_edge.shadow.challenger applied, under its own model version, writing its own ledger.

Usage: same arguments as scripts/shadow/price_slate.py (--model-version defaults to shadow-0.5.0)."""
from __future__ import annotations
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.arms import incumbent_center as IC          # noqa: E402
from nfl_edge.shadow import challenger as C               # noqa: E402


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--model-version" not in argv:
        argv += ["--model-version", C.CHALLENGER_VERSION]
    target = 2026
    if "--target-season" in argv:
        target = int(argv[argv.index("--target-season") + 1])
    P = IC.frozen_pricer()
    P._CHALLENGER_TARGET = target
    C.install(P)
    sys.argv = [sys.argv[0]] + argv
    return P.main()


if __name__ == "__main__":
    sys.exit(main())
