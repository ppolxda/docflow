# -*- coding: utf-8 -*-
"""
@create: 2023-01-09 17:06:41.

@author: ppolxda

@desc: utils
"""

import asyncio
import random
import traceback
from asyncio.exceptions import TimeoutError  # pylint: disable=W0622
from typing import Optional

from aiohttp.client_exceptions import ClientConnectionError
from aiohttp.client_exceptions import ServerConnectionError
from aiohttp.client_exceptions import ServerTimeoutError
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from ..exceptions import HttpNetConnectionError
from ..settings import settings
from .logger import LOGGER


def hook_retry_network_error(max_retry: Optional[int] = None):
    """网络问题重试."""
    if max_retry is None:
        max_retry = settings.MAX_RETRY

    def _hook_retry_network_error(func):
        """网络问题重试."""

        async def wrap(self, *args, **kwargs):
            if "trycount" in kwargs:
                trycount = kwargs.pop("trycount")
            else:
                trycount = 0

            if trycount >= max_retry:
                LOGGER.error(
                    "网络请求不畅通，重试达到最大次数[%s][%s][%s]",
                    func.__name__,
                    getattr(self, "NAME", ""),
                    args,
                )
                raise HttpNetConnectionError(
                    f"网络请求不畅通，重试达到最大次数[{func.__name__}][{getattr(self, 'NAME', '')}][{args}]",
                    HTTP_500_INTERNAL_SERVER_ERROR,
                    "",
                )

            try:
                rsp = await func(self, *args, **kwargs)
            except (
                ClientConnectionError,
                ServerConnectionError,
                ServerTimeoutError,
                ConnectionError,
                TimeoutError,
            ) as ex:
                LOGGER.warning(
                    "请求失败重试[%s][%s][%s][%s][%s][重试:%s]",
                    func.__name__,
                    getattr(self, "NAME", ""),
                    type(ex),
                    args,
                    ex,
                    trycount,
                )
                await asyncio.sleep(
                    random.randint(
                        settings.MIN_RETRY_SLEEPTIME, settings.MAX_RETRY_SLEEPTIME
                    )
                )
                kwargs["trycount"] = trycount + 1
                rsp = await wrap(self, *args, **kwargs)
                return rsp
            except Exception as ex:
                LOGGER.warning(
                    "请求异常[%s][%s][%s][%s][%s][%s]",
                    func.__name__,
                    getattr(self, "NAME", ""),
                    type(ex),
                    args,
                    ex,
                    traceback.format_exc(),
                )
                raise ex

            return rsp

        return wrap

    return _hook_retry_network_error
