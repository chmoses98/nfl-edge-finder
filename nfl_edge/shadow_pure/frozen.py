"""The frozen-model guard: PURE_PLAYER_V1's code must be byte-identical to what the preregistered study evaluated."""
from __future__ import annotations

import hashlib
import os

from nfl_edge.shadow_pure import PURE_V1_CODE_SHA256

PKG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "engines", "player", "pure_v1")
# the generic estimator the package imports (nfl_edge/engines/player/v4/linear.py) is part of the frozen code
DEPS = (os.path.join(os.path.dirname(PKG), "v4", "linear.py"),)


class FrozenModelChanged(RuntimeError):
    pass


def code_files() -> list[str]:
    files = sorted(os.path.join(PKG, f) for f in os.listdir(PKG) if f.endswith(".py"))
    return files + list(DEPS)


def code_sha256() -> str:
    h = hashlib.sha256()
    root = os.path.dirname(os.path.dirname(PKG))
    for f in code_files():
        h.update(os.path.relpath(f, root).replace(os.sep, "/").encode() + b"\0")
        with open(f, "rb") as fh:
            h.update(hashlib.sha256(fh.read()).hexdigest().encode() + b"\n")
    return h.hexdigest()


def assert_frozen() -> str:
    got = code_sha256()
    if got != PURE_V1_CODE_SHA256:
        raise FrozenModelChanged(f"PURE_PLAYER_V1 code sha256 {got} != frozen {PURE_V1_CODE_SHA256}; a changed model "
                                 "is a new version (PURE_PLAYER_V1_x), never a silent edit of the collected arm")
    return "sha256:" + got
