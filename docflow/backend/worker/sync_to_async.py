# -*- coding: utf-8 -*-
"""
@create: 2023-08-09 18:11:22.

@author: ppolxda

@desc: 同步转异步运行
"""
import asyncio
import logging
import os
import threading
import traceback
from contextlib import contextmanager
from typing import List
from typing import Optional

LOGGER = logging.getLogger()
_lock = None
_loop: List[Optional[asyncio.AbstractEventLoop]] = [
    None
]  # global event loop for any non-async instance
iothread: List[Optional[threading.Thread]] = [None]  # dedicated fsspec IO thread


def get_lock():
    """Allocate or return a threading lock.

    The lock is allocated on first use to allow setting one lock per forked process.
    """
    global _lock
    if not _lock:
        _lock = threading.Lock()
    return _lock


@contextmanager
def _selector_policy():
    original_policy = asyncio.get_event_loop_policy()
    try:
        if os.name == "nt" and hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        yield
    finally:
        asyncio.set_event_loop_policy(original_policy)


def get_loop():
    """Create or return the default fsspec IO loop.

    The loop will be running on a separate thread.
    """
    if _loop[0] is None:
        with get_lock():
            # repeat the check just in case the loop got filled between the
            # previous two calls from another thread
            if _loop[0] is None:
                with _selector_policy():
                    _loop[0] = asyncio.new_event_loop()
                thread = threading.Thread(target=_loop[0].run_forever, name="fsspecIO")
                thread.daemon = True
                thread.start()
                iothread[0] = thread
    return _loop[0]


async def _runner(event, coro, result, timeout=None):
    timeout = timeout if timeout else None  # convert 0 or 0.0 to None
    if timeout is not None:
        coro = asyncio.wait_for(coro, timeout=timeout)
    try:
        result[0] = await coro
    except Exception as ex:
        LOGGER.warning("运行异常：%s %s", ex, traceback.format_exc())
        result[0] = ex
    finally:
        event.set()
        LOGGER.info("运行结束结果集为：%s %s", coro.__qualname__, True if result[0] else False)


def sync(loop, async_callback, timeout=None):
    """Make loop run coroutine until it returns. Runs in other thread.

    Examples
    --------
    >>> fsspec.asyn.sync(fsspec.asyn.get_loop(), func, *args,
                         timeout=timeout, **kwargs)
    """
    timeout = timeout if timeout else None  # convert 0 or 0.0 to None
    # NB: if the loop is not running *yet*, it is OK to submit work
    # and we will wait for it
    if loop is None or loop.is_closed():
        raise RuntimeError("Loop is not running")
    try:
        loop0 = asyncio.events.get_running_loop()
        if loop0 is loop:
            raise NotImplementedError("Calling sync() from within a running loop")
    except RuntimeError:
        pass
    coro = async_callback
    result = [None]
    event = threading.Event()
    asyncio.run_coroutine_threadsafe(_runner(event, coro, result, timeout), loop)
    while True:
        # this loops allows thread to get interrupted
        if event.wait(1):
            break
        if timeout is not None:
            timeout -= 1
            if timeout < 0:
                raise TimeoutError

    return_result = result[0]
    if isinstance(return_result, asyncio.TimeoutError):
        # suppress asyncio.TimeoutError, raise FSTimeoutError
        raise TimeoutError from return_result  # type: ignore
    elif isinstance(return_result, BaseException):
        raise return_result  # type: ignore pylint: disable=raising-bad-type
    else:
        return return_result
