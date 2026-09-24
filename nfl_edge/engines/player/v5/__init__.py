"""DATA_PLAYER_V5: DATA_PLAYER_V4's structure with ONE changed input layer -- a point-in-time, availability-aware
projected starting quarterback (nfl_edge/context/qb_resolution.py) that propagates through the structure.

V4 (data-player-dist-4.0.0, player-inputs-4.0.0) takes QB1 from the depth chart even when that QB is Out
(docs/KNOWN_LIMITATIONS.md #89), and its inputs cannot change in the middle of its prospective collection. V5 is a
separate, versioned arm: nothing in this package edits V4's fitted state, its records or its inputs, and V4's own code
is reused by parameter (`model.fit_bundle(config={"qb_identity": True}, version=...)`), never copied. See
docs/PLAYER_V5.md.
"""
VERSION = "data-player-dist-5.0.0"
INPUTS_VERSION = "player-inputs-5.0.0"
HYBRID_VERSION = "hybrid-player-dist-5.0.0"
