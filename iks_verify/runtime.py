"""Small runtime adaptations for supported Windows environments."""
from __future__ import annotations

import asyncio
import socket
import sys


def configure_event_loop() -> None:
    """Install a Windows loop that works in regular and AppContainer terminals.

    CPython's Windows socketpair fallback creates a temporary TCP listener and
    calls ``accept``. Some restricted terminals disallow that local accept,
    causing an apparent startup hang. A connected UDP pair provides asyncio's
    one-byte cross-thread wake-up channel without a listener. This project does
    not depend on Proactor-only APIs, so the selector implementation is safe
    for the API and command-line entry points.
    """
    if sys.platform != "win32":
        return

    class WindowsUdpSelectorLoop(asyncio.SelectorEventLoop):
        def _make_self_pipe(self) -> None:
            self._ssock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._ssock.bind(("127.0.0.1", 0))
            self._csock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._csock.connect(self._ssock.getsockname())
            self._ssock.setblocking(False)
            self._csock.setblocking(False)
            self._internal_fds += 1
            self._add_reader(self._ssock.fileno(), self._read_from_self)

    class WindowsUdpSelectorPolicy(asyncio.WindowsSelectorEventLoopPolicy):
        _loop_factory = WindowsUdpSelectorLoop

    asyncio.set_event_loop_policy(WindowsUdpSelectorPolicy())
