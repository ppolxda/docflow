# -*- coding: utf-8 -*-
"""
@create: 2021-10-18 23:01:07.

@author: name

@desc: 异常集合
"""


class DocOcrError(Exception):
    """模块基准异常."""


class QueryParamsError(DocOcrError):
    """查询请求参数异常."""


class ParamsError(DocOcrError):
    """请求参数异常."""


class NotFoundError(DocOcrError):
    """对象不存在异常."""


class PermissionsError(DocOcrError):
    """访问权限不足."""


class PermissionsStatusError(DocOcrError):
    """请求状态受限."""


class DuplicateError(DocOcrError):
    """字段冲突异常."""


class TaskLockError(DocOcrError):
    """任务锁已生效."""


class DocOcrInputError(DocOcrError):
    """DocOcrInputError."""


class DocOcrCurdError(DocOcrInputError):
    """关于CURD内部报错."""


class DocOcrClientError(DocOcrCurdError):
    """关于识别接口的错误."""


class ImageRotateError(DocOcrCurdError):
    """关于识别接口的错误."""


class HttpRequestError(DocOcrError):
    """外部HTTP请求类错误."""

    def __init__(self, message, code, context) -> None:
        """构造函数."""
        super().__init__(message)
        self.code = code
        self.context = context


class HttpNetConnectionError(HttpRequestError):
    """外部HTTP请求类错误."""


class WorkflowError(HttpRequestError):
    """工作流错误."""


class PredictError(HttpRequestError):
    """预测推理错误."""


class WordTransforError(DocOcrError):
    """word转换pdf接口错误."""


class TaskExportError(DocOcrError):
    """任务导出错误."""


class TaskExportStatusError(TaskExportError):
    """当前状态禁止操作该接口."""
