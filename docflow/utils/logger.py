# -*- coding: utf-8 -*-
"""
@create: 2021-10-18 23:03:47.

@author: name

@desc: 日志帮助对象
"""
import logging

LOGGER = logging.getLogger("uvicorn.main")
ERROR_LOGGER = logging.getLogger("uvicorn.error")


class LoggingMixin:
    """LoggingMixin."""

    @property
    def log(
        self,
    ) -> logging.Logger:
        """获取日志对象."""
        return LOGGER
        # try:
        #     # FIXME: LoggingMixin should have a default _log field.
        #     return self._log  # type: ignore
        # except AttributeError:
        #     self._log = logging.getLogger(
        #         self.__class__.__module__ + "." + self.__class__.__name__
        #     )
        #     return self._log
