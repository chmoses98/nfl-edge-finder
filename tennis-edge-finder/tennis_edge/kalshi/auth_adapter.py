"""Authenticated Kalshi access adapter (interface + request signing), DISABLED until credentials exist.

Kalshi's authenticated REST/WebSocket endpoints require an API key id and an RSA private key; requests carry
KALSHI-ACCESS-KEY, KALSHI-ACCESS-TIMESTAMP (ms) and KALSHI-ACCESS-SIGNATURE = base64(RSA-PSS-SHA256 over
timestamp + method + path). This module implements the signing and the read-only surface we would use
(full orderbook depth, WebSocket orderbook deltas/trades); it never exposes order placement.

Activation: set KALSHI_API_KEY_ID and KALSHI_PRIVATE_KEY_PATH; `AuthenticatedKalshi.available()` then returns
True. Without them every method raises AuthUnavailable (fail closed), and the public client remains the
production path. `cryptography` is imported lazily so the package is not a hard dependency.
"""
from __future__ import annotations

import base64
import os
import time


class AuthUnavailable(RuntimeError):
    pass


class AuthenticatedKalshi:
    def __init__(self, key_id: str | None = None, private_key_path: str | None = None, base_url: str = "https://api.elections.kalshi.com"):
        self.key_id = key_id or os.environ.get("KALSHI_API_KEY_ID")
        self.key_path = private_key_path or os.environ.get("KALSHI_PRIVATE_KEY_PATH")
        self.base_url = base_url
        self._key = None

    def available(self) -> bool:
        return bool(self.key_id and self.key_path and os.path.exists(self.key_path))

    def _load(self):
        if not self.available():
            raise AuthUnavailable("KALSHI_API_KEY_ID / KALSHI_PRIVATE_KEY_PATH not configured")
        if self._key is None:
            from cryptography.hazmat.primitives import serialization
            self._key = serialization.load_pem_private_key(open(self.key_path, "rb").read(), password=None)
        return self._key

    def headers(self, method: str, path: str) -> dict:
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding
        key = self._load()
        ts = str(int(time.time() * 1000))
        msg = (ts + method.upper() + path.split("?")[0]).encode()
        sig = key.sign(msg, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
        return {"KALSHI-ACCESS-KEY": self.key_id, "KALSHI-ACCESS-TIMESTAMP": ts, "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig).decode(), "Accept": "application/json"}

    # read-only surface we would use; order endpoints are intentionally absent
    def orderbook(self, ticker: str, depth: int = 50) -> dict:
        import json, urllib.request
        path = f"/trade-api/v2/markets/{ticker}/orderbook"
        req = urllib.request.Request(self.base_url + path + f"?depth={depth}", headers=self.headers("GET", path))
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
