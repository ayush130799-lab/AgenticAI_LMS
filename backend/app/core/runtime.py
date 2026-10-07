import asyncio
import sys
from collections.abc import Coroutine
from typing import Any


def run_async(coro: Coroutine[Any, Any, Any]) -> Any:
    """asyncio.run() that works with psycopg's async driver on Windows.

    psycopg cannot run on Windows' default ProactorEventLoop, so use the
    selector loop there. Other platforms use the default loop.
    """
    if sys.platform == "win32":
        return asyncio.run(coro, loop_factory=asyncio.SelectorEventLoop)
    return asyncio.run(coro)
