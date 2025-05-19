"""Simple in-process rate limiting utilities."""

from __future__ import annotations

import threading
import time
from collections.abc import Callable


class RateLimiter:
    """Token bucket style rate limiter."""

    def __init__(self, max_calls: int, period: float) -> None:
        if max_calls <= 0:
            raise ValueError("max_calls must be > 0")
        if period <= 0:
            raise ValueError("period must be > 0")
        self.max_calls = max_calls
        self.period = period
        self._lock = threading.Lock()
        self._timestamps: list[float] = []

    def acquire(self) -> None:
        """Block until a new call is permitted."""
        with self._lock:
            now = time.monotonic()
            # prune timestamps outside of the current window
            self._timestamps = [t for t in self._timestamps if now - t < self.period]
            if len(self._timestamps) >= self.max_calls:
                sleep_for = self.period - (now - self._timestamps[0])
                if sleep_for > 0:
                    time.sleep(sleep_for)
                now = time.monotonic()
                self._timestamps = [t for t in self._timestamps if now - t < self.period]
            self._timestamps.append(time.monotonic())

    def __call__(self, func: Callable) -> Callable:
        """Decorator form of :py:meth:`acquire`."""

        def wrapper(*args, **kwargs):
            self.acquire()
            return func(*args, **kwargs)

        return wrapper
