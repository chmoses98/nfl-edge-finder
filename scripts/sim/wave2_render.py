#!/usr/bin/env python3
"""Render research/game_script_v2/wave2/*.md from their JSON (RESEARCH_ONLY).

  python scripts/sim/wave2_render.py           write every report whose JSON exists
  python scripts/sim/wave2_render.py --check   exit 1 if any committed report differs from its JSON rendering
"""
from __future__ import annotations
import argparse, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.sim import wave2_render as R

W2 = os.path.join(ROOT, "research", "game_script_v2", "wave2")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    bad = 0
    for name in R.RENDERERS:
        js = os.path.join(W2, name + ".json")
        if not os.path.exists(js):
            continue
        md, text = os.path.join(W2, name + ".md"), R.render_file(js)
        if a.check:
            if not os.path.exists(md) or open(md).read() != text:
                print("STALE", name + ".md"); bad += 1
        else:
            open(md, "w").write(text); print("wrote", name + ".md")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
