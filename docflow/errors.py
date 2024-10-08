# -*- coding: utf-8 -*-
"""
@create: 2021-10-18 22:45:36.

@author: name

@desc: fastapi 错误返回
"""

from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST
from starlette.status import HTTP_401_UNAUTHORIZED

InvalidCredentialsException = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED,
    detail="Invalid credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

DisabledUserException = HTTPException(
    status_code=HTTP_400_BAD_REQUEST,
    detail="User disabled",
    headers={"WWW-Authenticate": "Bearer"},
)

UserPasswordInvaildException = HTTPException(
    status_code=HTTP_400_BAD_REQUEST,
    detail="输入密码错误",
    headers={"WWW-Authenticate": "Bearer"},
)

ProviderInvaildException = HTTPException(
    status_code=HTTP_400_BAD_REQUEST,
    detail="当前用户用户名已被使用",
    headers={"WWW-Authenticate": "Bearer"},
)

PredictException = HTTPException(
    status_code=HTTP_400_BAD_REQUEST,
    detail="预测失败",
    # headers={"WWW-Authenticate": "Bearer"},
)

DownloadFileTypeException = HTTPException(
    status_code=HTTP_400_BAD_REQUEST,
    detail="加载文件失败，文件类型不正确",
    # headers={"WWW-Authenticate": "Bearer"},
)

DownloadFailedException = HTTPException(
    status_code=HTTP_400_BAD_REQUEST,
    detail="加载文件失败，对象已失效",
    # headers={"WWW-Authenticate": "Bearer"},
)

UploadFileNotSupportException = HTTPException(
    status_code=HTTP_400_BAD_REQUEST,
    detail="不受支持文件类型",
    # headers={"WWW-Authenticate": "Bearer"},
)

ObjectNotFoundException = HTTPException(
    status_code=HTTP_400_BAD_REQUEST,
    detail="检索对象不存在",
    # headers={"WWW-Authenticate": "Bearer"},
)


QueryTemplateNotSetException = HTTPException(
    status_code=HTTP_400_BAD_REQUEST,
    detail="未设置查询模板数据",
    # headers={"WWW-Authenticate": "Bearer"},
)

DocOcrTemplateNotSetLabelsException = HTTPException(
    status_code=HTTP_400_BAD_REQUEST,
    detail="未设置模板数据信息，必须设置4个以上标签",
    # headers={"WWW-Authenticate": "Bearer"},
)

DocOcrTemplateNotSetBoxsException = HTTPException(
    status_code=HTTP_400_BAD_REQUEST,
    detail="未设置模板数据信息，未能找到选中标签",
    # headers={"WWW-Authenticate": "Bearer"},
)

DocOcrTemplateNotHintLabelsException = HTTPException(
    status_code=HTTP_400_BAD_REQUEST,
    detail="未能匹配到特征信息",
    # headers={"WWW-Authenticate": "Bearer"},
)


DocOcrTemplateTrFailedException = HTTPException(
    status_code=HTTP_400_BAD_REQUEST,
    detail="未能识别任何文字",
    # headers={"WWW-Authenticate": "Bearer"},
)
