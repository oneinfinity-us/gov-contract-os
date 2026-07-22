"""Small, polite HTTP client shared by all connectors.

Enforces: a clear User-Agent identifying this tool, a minimum delay between
requests to the same host, a request timeout, and retry with exponential
backoff for transient failures. This exists to be a good citizen when calling
PUBLIC procurement endpoints - it must never be used to bypass auth, CAPTCHA,
rate limits, or paywalls.
"""

from __future__ import annotations

import threading
import time
from urllib.parse import urlparse

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

USER_AGENT = (
    "gov-contract-os/0.1 public-procurement-monitor "
    "(+https://github.com/oneinfinity-us/gov-contract-os)"
)

DEFAULT_MIN_INTERVAL_SECONDS = 2.0
DEFAULT_TIMEOUT_SECONDS = 15.0


class RateLimiter:
    """Enforces a minimum delay between requests to the same host."""

    def __init__(self, min_interval_seconds: float = DEFAULT_MIN_INTERVAL_SECONDS) -> None:
        self._min_interval = min_interval_seconds
        self._last_request_at: dict[str, float] = {}
        self._lock = threading.Lock()

    def wait_for_slot(self, host: str) -> None:
        with self._lock:
            now = time.monotonic()
            last = self._last_request_at.get(host)
            if last is not None:
                elapsed = now - last
                if elapsed < self._min_interval:
                    time.sleep(self._min_interval - elapsed)
            self._last_request_at[host] = time.monotonic()


class PoliteHttpClient:
    """Thin httpx wrapper: per-host rate limit + timeout + retry/backoff."""

    def __init__(
        self,
        min_interval_seconds: float = DEFAULT_MIN_INTERVAL_SECONDS,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self._rate_limiter = RateLimiter(min_interval_seconds)
        self._client = httpx.Client(
            timeout=timeout_seconds,
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True,
        )

    def __enter__(self) -> PoliteHttpClient:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.TransportError, httpx.HTTPStatusError)),
    )
    def get(self, url: str, params: dict | None = None) -> httpx.Response:
        host = urlparse(url).netloc
        self._rate_limiter.wait_for_slot(host)
        response = self._client.get(url, params=params)
        response.raise_for_status()
        return response
