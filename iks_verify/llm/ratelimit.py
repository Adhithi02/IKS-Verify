import asyncio
import random
import time
from collections import deque
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


class RateLimiter:
    def __init__(
        self,
        requests_per_minute: int,
        tokens_per_minute: int,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        if requests_per_minute < 1 or tokens_per_minute < 1:
            raise ValueError("Rate limits must be positive")
        self.requests_per_minute = requests_per_minute
        self.tokens_per_minute = tokens_per_minute
        self.clock = clock
        self.sleep = sleep
        self.events: deque[tuple[float, int]] = deque()

    async def acquire(self, estimated_tokens: int = 0) -> None:
        if estimated_tokens > self.tokens_per_minute:
            raise ValueError("Single request exceeds configured token-per-minute limit")
        while True:
            now = self.clock()
            while self.events and now - self.events[0][0] >= 60:
                self.events.popleft()
            used = sum(tokens for _, tokens in self.events)
            if (
                len(self.events) < self.requests_per_minute
                and used + estimated_tokens <= self.tokens_per_minute
            ):
                self.events.append((now, estimated_tokens))
                return

            delays: list[float] = []
            if len(self.events) >= self.requests_per_minute:
                delays.append(self.events[0][0] + 60 - now)
            if used + estimated_tokens > self.tokens_per_minute:
                released = used
                for timestamp, tokens in self.events:
                    released -= tokens
                    if released + estimated_tokens <= self.tokens_per_minute:
                        delays.append(timestamp + 60 - now)
                        break
            await self.sleep(max(0.05, min(delays)))


async def with_backoff(
    call: Callable[[], Awaitable[T]],
    attempts: int = 4,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    jitter: Callable[[], float] = random.random,
) -> T:
    for attempt in range(attempts):
        try:
            return await call()
        except Exception as error:
            if "429" not in str(error) and "quota" not in str(error).lower():
                raise
            if attempt == attempts - 1:
                raise
            await sleep((2**attempt) + jitter() * 0.25)
    raise RuntimeError("unreachable")
