"""Read-only Kalshi Trade API v2 client.

Design constraints (see docs/KALSHI_API_NOTES.md):
  * Public GET endpoints only. No auth, no order surface, no portfolio surface.
    Automatic execution is NOT authorized for this project.
  * Token-bucket rate limiting well under Kalshi's Basic tier (~20 reads/s):
    we default to 4 req/s and back off on HTTP 429 (which may lack Retry-After).
  * A failed fetch is never an empty result: paginate() returns (items, complete)
    and callers must treat complete=False as a partial universe.
  * Every response is stamped with retrieval time so bronze rows carry provenance.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone

BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
USER_AGENT = "nfl-edge-finder/0.1 (read-only research; github.com/chmoses98/nfl-edge-finder)"


class KalshiError(RuntimeError):
    def __init__(self, status: int | str, url: str, body: str = ""):
        super().__init__(f"Kalshi HTTP {status} for {url}: {body[:300]}")
        self.status = status
        self.url = url
        self.body = body


@dataclass
class ClientStats:
    requests: int = 0
    retries: int = 0
    http_429: int = 0
    http_5xx: int = 0
    failures: int = 0
    seconds_sleeping: float = 0.0
    by_path: dict = field(default_factory=dict)

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items()}


class KalshiClient:
    def __init__(self, base_url: str = BASE_URL, rps: float = 4.0, timeout: int = 30,
                 max_retries: int = 6, user_agent: str = USER_AGENT):
        self.base_url = base_url.rstrip("/")
        self.min_interval = 1.0 / rps
        self.timeout = timeout
        self.max_retries = max_retries
        self.user_agent = user_agent
        self._last = 0.0
        self._penalty = 0.0  # adaptive extra sleep after 429s
        self.stats = ClientStats()

    # ------------------------------------------------------------------ core
    def _throttle(self):
        wait = self.min_interval + self._penalty - (time.monotonic() - self._last)
        if wait > 0:
            time.sleep(wait)
            self.stats.seconds_sleeping += wait
        self._last = time.monotonic()

    def get(self, path: str, params: dict | None = None) -> dict:
        """GET a JSON endpoint. Returns the parsed body with `_meta` provenance."""
        q = {k: v for k, v in (params or {}).items() if v is not None}
        url = f"{self.base_url}/{path.lstrip('/')}"
        if q:
            url += "?" + urllib.parse.urlencode(q, doseq=True)
        key = path.split("?")[0]
        self.stats.by_path[key] = self.stats.by_path.get(key, 0) + 1
        last_err = None
        for attempt in range(self.max_retries + 1):
            self._throttle()
            self.stats.requests += 1
            req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": self.user_agent})
            t0 = time.time()
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    raw = r.read()
                    body = json.loads(raw) if raw else {}
                    if not isinstance(body, dict):
                        body = {"_value": body}
                    body["_meta"] = {
                        "url": url,
                        "retrieved_at": datetime.now(timezone.utc).isoformat(),
                        "latency_ms": int((time.time() - t0) * 1000),
                        "bytes": len(raw),
                    }
                    self._penalty = max(0.0, self._penalty * 0.7)
                    return body
            except urllib.error.HTTPError as e:
                text = ""
                try:
                    text = e.read().decode("utf-8", "replace")
                except Exception:
                    pass
                last_err = KalshiError(e.code, url, text)
                if e.code == 429:
                    self.stats.http_429 += 1
                    retry_after = e.headers.get("Retry-After")
                    sleep = min(float(retry_after), 15.0) if retry_after and retry_after.isdigit() else min(1.0 * (2 ** attempt), 15.0)
                    self._penalty = min(self._penalty + 0.25, 3.0)
                elif 500 <= e.code < 600:
                    self.stats.http_5xx += 1
                    sleep = min(1.0 * (2 ** attempt), 15.0)
                else:
                    self.stats.failures += 1
                    raise last_err
                self.stats.retries += 1
                time.sleep(sleep)
                self.stats.seconds_sleeping += sleep
            except (urllib.error.URLError, TimeoutError, ConnectionError, json.JSONDecodeError) as e:
                last_err = KalshiError("network", url, str(e))
                self.stats.retries += 1
                sleep = min(1.0 * (2 ** attempt), 15.0)
                time.sleep(sleep)
                self.stats.seconds_sleeping += sleep
        self.stats.failures += 1
        raise last_err  # type: ignore[misc]

    def try_get(self, path: str, params: dict | None = None) -> tuple[dict | None, str | None]:
        """GET that never raises: returns (body, None) or (None, error_string)."""
        try:
            return self.get(path, params), None
        except KalshiError as e:
            return None, f"{e.status}: {e.body[:200]}"

    def paginate(self, path: str, params: dict | None, key: str, limit: int = 200,
                 max_pages: int = 10_000) -> tuple[list, bool, dict]:
        """Follow `cursor` pagination. Returns (items, complete, info).

        complete=False means a page failed and the universe is PARTIAL. Callers
        must not treat a partial list as the full market universe (CFB lesson:
        an empty list on 429 silently dropped a third of the universe).
        """
        items: list = []
        cursor = None
        pages = 0
        info = {"pages": 0, "error": None}
        params = dict(params or {})
        params["limit"] = limit
        while pages < max_pages:
            if cursor:
                params["cursor"] = cursor
            try:
                body = self.get(path, params)
            except KalshiError as e:
                info["error"] = str(e)
                info["pages"] = pages
                return items, False, info
            pages += 1
            page_items = body.get(key) or []
            items.extend(page_items)
            cursor = body.get("cursor")
            if not cursor or not page_items:
                break
        info["pages"] = pages
        info["truncated_by_max_pages"] = pages >= max_pages
        return items, not info["truncated_by_max_pages"], info

    # ---------------------------------------------------------- convenience
    def exchange_status(self):
        return self.get("exchange/status")

    def series_list(self, category: str | None = None, include_product_metadata: bool = False, **kw):
        return self.paginate("series", {"category": category, "include_product_metadata": str(include_product_metadata).lower() if include_product_metadata else None}, "series", **kw)

    def series(self, ticker: str):
        return self.get(f"series/{ticker}")

    def events(self, series_ticker: str | None = None, status: str | None = None, with_nested_markets: bool = False, **kw):
        return self.paginate("events", {"series_ticker": series_ticker, "status": status,
                                        "with_nested_markets": "true" if with_nested_markets else None}, "events", **kw)

    def event(self, event_ticker: str, with_nested_markets: bool = True):
        return self.get(f"events/{event_ticker}", {"with_nested_markets": "true" if with_nested_markets else None})

    def markets(self, series_ticker: str | None = None, event_ticker: str | None = None, status: str | None = None,
                tickers: str | None = None, min_close_ts: int | None = None, max_close_ts: int | None = None, **kw):
        kw.setdefault("limit", 1000)
        return self.paginate("markets", {"series_ticker": series_ticker, "event_ticker": event_ticker, "status": status,
                                         "tickers": tickers, "min_close_ts": min_close_ts, "max_close_ts": max_close_ts}, "markets", **kw)

    def market(self, ticker: str):
        return self.get(f"markets/{ticker}")

    def orderbook(self, ticker: str, depth: int | None = None):
        return self.get(f"markets/{ticker}/orderbook", {"depth": depth})

    def trades(self, ticker: str | None = None, min_ts: int | None = None, max_ts: int | None = None, **kw):
        kw.setdefault("limit", 1000)
        return self.paginate("markets/trades", {"ticker": ticker, "min_ts": min_ts, "max_ts": max_ts}, "trades", **kw)

    def candlesticks(self, series_ticker: str, ticker: str, start_ts: int, end_ts: int, period_interval: int = 60):
        return self.get(f"series/{series_ticker}/markets/{ticker}/candlesticks",
                        {"start_ts": start_ts, "end_ts": end_ts, "period_interval": period_interval})

    # historical tier (archived data) --------------------------------------
    def historical_cutoff(self):
        return self.get("historical/cutoff")

    def historical_markets(self, series_ticker: str | None = None, event_ticker: str | None = None, **kw):
        kw.setdefault("limit", 1000)
        return self.paginate("historical/markets", {"series_ticker": series_ticker, "event_ticker": event_ticker}, "markets", **kw)

    def historical_market(self, ticker: str):
        return self.get(f"historical/markets/{ticker}")

    def historical_trades(self, ticker: str | None = None, min_ts: int | None = None, max_ts: int | None = None, **kw):
        kw.setdefault("limit", 1000)
        return self.paginate("historical/trades", {"ticker": ticker, "min_ts": min_ts, "max_ts": max_ts}, "trades", **kw)

    def historical_candlesticks(self, ticker: str, start_ts: int, end_ts: int, period_interval: int = 60):
        return self.get(f"historical/markets/{ticker}/candlesticks",
                        {"start_ts": start_ts, "end_ts": end_ts, "period_interval": period_interval})
