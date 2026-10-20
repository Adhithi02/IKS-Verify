from collections.abc import Coroutine
from typing import Any, TypeVar

T = TypeVar("T")


def run_immediately(coroutine: Coroutine[Any, Any, T]) -> T:
    """Run a coroutine that is guaranteed not to perform asynchronous I/O.

    Mock-pipeline unit tests use deterministic local doubles. Driving those
    coroutines directly keeps them portable in constrained Windows sandboxes
    where creating an asyncio event-loop socketpair is disallowed. Tests that
    exercise the ASGI HTTP boundary still use httpx and a real event loop.
    """
    try:
        coroutine.send(None)
    except StopIteration as complete:
        return complete.value
    coroutine.close()
    raise AssertionError("This unit-test coroutine unexpectedly required an event loop")
