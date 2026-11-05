#!/usr/bin/env python3
"""Run the walk-forward distribution evaluation and write an aggregate-only JSON (no owner data is read)."""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from nfl_edge.postmortem import dist_eval  # noqa: E402


def _clean(o):
    import numpy as np
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    return o


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="research/postmortem_2026-11-02/distribution_eval.json")
    ap.add_argument("--no-incumbent", action="store_true")
    a = ap.parse_args(argv)
    rep = dist_eval.run(with_incumbent=not a.no_incumbent)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(_clean(rep), f, indent=1, sort_keys=True)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
