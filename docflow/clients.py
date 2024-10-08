# -*- coding: utf-8 -*-
"""
@create: 2021-07-16 10:39:32.

@author: ppolxda

@desc: 外部客户端
"""
import json
from contextlib import contextmanager
from functools import lru_cache
from functools import partial
from functools import wraps
from inspect import signature
from io import BytesIO
from typing import Awaitable
from typing import Callable
from typing import Optional
from typing import TypeVar

import aiohttp
from aio_pika.abc import DateType
from fastapi import Request
from PIL import Image
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from .errors import DownloadFailedException
from .errors import DownloadFileTypeException
from .s3.s3_client import S3Client
from .settings import settings
from .utils.amqp_client import AMQPAynscTaskHandler
from .utils.amqp_client import AMQPHandler
from .utils.fileutils import is_image
from .utils.fileutils import is_json
from .utils.fileutils import is_pdf
from .utils.fileutils import is_word


@lru_cache()
def get_engine():
    """获取数据库连接池."""
    engine = create_engine(
        settings.DB_URI,
        pool_pre_ping=True,
        hide_parameters=not settings.PRINT_SQL,
        echo=settings.PRINT_SQL,
        isolation_level="READ COMMITTED",
        pool_size=settings.SQLALCHEMY_POOL_SIZE,
        pool_timeout=settings.SQLALCHEMY_POOL_TIMEOUT,
        pool_recycle=settings.SQLALCHEMY_POOL_RECYCLE,
        max_overflow=settings.SQLALCHEMY_MAX_OVERFLOW,
        future=True,
    )
    return engine


@lru_cache()
def get_sessionmaker():
    """获取数据库连接池."""
    engine = get_engine()
    return sessionmaker(
        autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
    )


@contextmanager
def get_db_sync():
    """获取数据库客户端."""
    session_maker = get_sessionmaker()
    if session_maker is None:
        raise RuntimeError("db not initialize")

    # session: Session = session_maker(
    #     # query_cls=AutoExpireAllQueryData
    # )
    with session_maker() as session:
        yield session
        session.commit()


def get_db(request: Request):
    """获取数据库客户端."""
    session_maker = get_sessionmaker()
    if session_maker is None:
        raise RuntimeError("db not initialize")

    with session_maker() as session:
        assert not request.state.db_session
        request.state.db_session = session
        yield session


@lru_cache()
def get_amqp():
    """获取数据库连接池."""
    return AMQPHandler(
        settings.AMQP_URI,
        settings.AMQP_APP_ID,
        settings.AMQP_APP_QUEUE_NAME,
        settings.AMQP_APP_QUEUE_RANGE,
        settings.AMQP_TIMEOUT,
    )


@lru_cache()
def get_amqp_async_task():
    """获取数据库连接池."""
    return AMQPAynscTaskHandler(
        AMQPHandler(
            settings.AMQP_URI,
            settings.AMQP_APP_ID,
            settings.AMQP_APP_QUEUE_NAME_ASYNC,
            settings.AMQP_APP_QUEUE_RANGE_ASYNC,
            settings.AMQP_TIMEOUT,
        ),
        settings.BACKEND_API if settings.BACKEND_API else "",
        settings.CONDUCTOR_WORKER_DOMAIN,
        settings.AMQP_ENABLED,
    )


async def publish_amqp_channel(
    message: dict,
    message_id: Optional[str] = None,
    expiration: Optional[DateType] = None,
    is_async_task: bool = False,
):
    """发布消息至AMQP."""
    if is_async_task:
        cli = get_amqp_async_task()
    else:
        cli = get_amqp()

    await cli.publish(message, message_id, expiration)


def find_field_idx(field: str, func: Callable[..., Awaitable]) -> int:
    """Find session index in function call parameter."""
    func_params = signature(func).parameters
    try:
        # func_params is an ordered dict -- this is the "recommended" way of getting the position
        session_args_idx = tuple(func_params).index(field)
    except ValueError as ex:
        raise ValueError(
            f"Function {func.__qualname__} has no `{field}` argument"
        ) from ex

    return session_args_idx


RT = TypeVar("RT")
find_db_idx = partial(find_field_idx, "session")


def provide_db(func: Callable[..., Awaitable[RT]]) -> Callable[..., Awaitable[RT]]:
    """参数动态注入装饰器."""
    session_args_idx = find_db_idx(func)

    @wraps(func)
    async def wrapper(*args, **kwargs) -> RT:
        if "session" in kwargs or session_args_idx < len(args):
            return await func(*args, **kwargs)
        else:
            with get_db_sync() as session:
                return await func(*args, session=session, **kwargs)

    return wrapper


@lru_cache()
def get_s3_remote_cli() -> S3Client:
    """获取全局远程minio客户端."""
    return S3Client.from_config(
        settings.S3_REMOTE_URI,
        bucket_name=settings.S3_BUCKET,
        presign_expire=settings.S3_SIGN_EXPIRE,
    )


@lru_cache()
def get_s3_local_cli() -> S3Client:
    """获取全局本地minio客户端."""
    cli = S3Client.from_config(
        settings.S3_LOCAL_URI,
        bucket_name=settings.S3_BUCKET,
        presign_expire=settings.S3_SIGN_EXPIRE,
    )
    return cli


def is_vaild_download_url(url: str) -> bool:
    """检查是否是有效路径."""
    return (
        url.startswith("http://")
        or url.startswith("https://")
        or url.startswith("file://")
    )


async def download_file(url: str, timeout: Optional[int] = None) -> bytes:
    """获取文件路径."""
    if not timeout:
        timeout = settings.DOWNLOAD_TIMEOUT

    # 签名重新下载
    if url.startswith("s3://"):
        cli = get_s3_local_cli()
        url = await cli.s3cli.presigned_get_s3(url)

    if not is_vaild_download_url(url):
        raise DownloadFailedException

    # 只允许open用于测试
    if settings.IS_DEBUG and url.startswith("file://"):
        with open(url[len("file://") :], "rb") as fss:
            data = fss.read()
            return data
    elif url.startswith("http://") or url.startswith("https://"):
        ttt = aiohttp.ClientTimeout(total=timeout)  # type: ignore
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=ttt) as rrr:
                data = await rrr.read()
    else:
        raise TypeError("url invaild")

    if b"NoSuchKey" in data or b"<Error>" in data:
        raise DownloadFailedException
    return data


async def download_file_save(
    session,
    url: str,
    dir_path: str,
    timeout: Optional[int] = None,
):
    """下载保存(节约内存)."""
    if not timeout:
        timeout = settings.DOWNLOAD_TIMEOUT

    # 签名重新下载
    if url.startswith("s3://"):
        cli = get_s3_local_cli()
        url = await cli.s3cli.presigned_get_s3(url)

    if not is_vaild_download_url(url):
        raise DownloadFailedException

    # Debug测试
    if settings.IS_DEBUG and url.startswith("file://"):
        with open(url[len("file://") :], "rb") as fss:
            data = fss.read()
            return data
    elif url.startswith("http://") or url.startswith("https://"):
        async with session.get(
            url, timeout=aiohttp.ClientTimeout(total=timeout)
        ) as rrr:
            with open(dir_path, "wb") as fs:
                async for chunk in rrr.content.iter_chunked(1024):
                    fs.write(chunk)
    else:
        raise TypeError("url invaild")


async def download_excel(
    url: str, timeout: Optional[int] = None, check_suffix=False
) -> bytes:
    """下载表格."""
    if check_suffix and not (
        url.split("?")[-1].lower().endswith(".xls")
        or url.split("?")[-1].lower().endswith(".xlsx")
    ):
        raise DownloadFileTypeException

    data = await download_file(url, timeout)
    if not data:
        raise DownloadFileTypeException
    return data


async def download_image(url: str, timeout: Optional[int] = None) -> bytes:
    """下载图片."""
    data = await download_file(url, timeout)
    if not data or not is_image(data):
        raise DownloadFileTypeException
    return data


async def download_image_to_pil(url: str, timeout: Optional[int] = None) -> Image.Image:
    """下载图片."""
    data = await download_image(url, timeout)
    return Image.open(BytesIO(data))


def lazy_download_image_to_pil(url, timeout: Optional[int] = None, copy: bool = False):
    """延时下载图片，用于性能提升."""
    _image: Optional[Image.Image] = None

    async def wrapper_call():
        nonlocal _image

        if _image is not None:
            if copy:
                return _image.copy()
            else:
                return _image

        _image = await download_image_to_pil(url, timeout)
        return _image

    return wrapper_call


async def download_pdf(
    url: str, timeout: Optional[int] = None, check_suffix=False
) -> bytes:
    """下载PDF."""
    if check_suffix and not url.split("?")[-1].lower().endswith(".pdf"):
        raise DownloadFileTypeException

    data = await download_file(url, timeout)
    if not data or not is_pdf(data):
        raise DownloadFileTypeException
    return data


async def download_word(
    url: str, timeout: Optional[int] = None, check_suffix=False
) -> bytes:
    """下载WORD."""
    if check_suffix and not (
        url.split("?")[-1].lower().endswith(".doc")
        or url.split("?")[-1].lower().endswith(".docx")
    ):
        raise DownloadFileTypeException

    data = await download_file(url, timeout)
    if not data or not is_word(data):
        raise DownloadFileTypeException
    return data


async def download_json(url: str, timeout: Optional[int] = None, check_suffix=False):
    """下载PDF."""
    if check_suffix and not url.split("?")[-1].lower().endswith(".json"):
        raise DownloadFileTypeException

    data = await download_file(url, timeout)
    if not data or not is_json(data):
        raise DownloadFileTypeException
    return json.loads(data)
