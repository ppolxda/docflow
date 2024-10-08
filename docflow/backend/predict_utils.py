# -*- coding: utf-8 -*-
"""
@create: 2022-12-12 16:15:26.

@author: ppolxda

@desc: 推理工具类
"""

import contextlib
import glob
import logging
import os
from io import BytesIO
from typing import Optional
from typing import Union
from urllib.parse import urlparse

import aioboto3
import aiohttp
import filetype
import pydantic
from aiobotocore.config import AioConfig
from humps import camelize
from PIL import Image

from .settings import settings

logger = logging.getLogger()


class S3Session:
    """S3Session."""

    def __init__(
        self,
        endpoint_url,
        aws_access_key_id,
        aws_secret_access_key,
        region_name="us-east-1",
    ) -> None:
        """初始化函数."""
        self.endpoint_url = endpoint_url
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.config = AioConfig(signature_version="s3v4")
        self.session = aioboto3.Session()

    @contextlib.asynccontextmanager
    async def client(self):
        """创建客户端."""
        async with self.session.client(
            "s3",
            region_name=self.region_name,
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            config=self.config,
        ) as s3cli:
            yield s3cli


url_ = urlparse(settings.S3_LOCAL_URI)
s3client = S3Session(
    f"{url_.scheme}://{url_.hostname}:{url_.port}", url_.username, url_.password
)


def is_image(data):
    """是否是图片格式."""
    if not isinstance(data, (bytes, BytesIO)):
        return False

    rtype = filetype.image_match(data)
    return rtype is not None


def is_vaild_download_url(url: str) -> bool:
    """检查是否是有效路径."""
    return (
        url.startswith("http://")
        or url.startswith("https://")
        or url.startswith("file://")
    )


async def download_file(url: Union[str, bytes], timeout: Optional[int] = None) -> bytes:
    """获取文件路径."""
    if not timeout:
        timeout = settings.DOWNLOAD_TIMEOUT

    if isinstance(url, bytes):
        return url

    # 签名重新下载
    if url.startswith("s3://"):
        s3_ = urlparse(url)
        bucket = s3_.netloc
        object_id = s3_.path
        async with s3client.client() as s3cli:
            url = await s3cli.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": bucket,
                    "Key": object_id,
                },
                ExpiresIn=180,
            )

    if not is_vaild_download_url(url):
        raise TypeError("download error")

    # 只允许open用于测试
    if url.startswith("http://") or url.startswith("https://"):
        ttt = aiohttp.ClientTimeout(total=timeout)  # type: ignore
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=ttt) as rrr:
                data = await rrr.read()
    else:
        raise TypeError("url invaild")

    if b"NoSuchKey" in data or b"<Error>" in data:
        raise TypeError("rsp error")
    return data


async def download_image(
    url: Union[str, bytes], download_timeout: Optional[int] = None
) -> Image.Image:
    """下载文件."""
    data = await download_file(url, download_timeout)
    data_ = BytesIO(data)
    image = Image.open(data_).convert("RGB")
    return image


def image_to_bytes(xxx: Image.Image):
    """图片转BytesIO."""
    ccc = BytesIO()
    xxx.save(ccc, "png")
    ccc.seek(0)
    return ccc.read()


def find_registry_path(dst_path: str):
    """查找模型发布路径."""
    if not os.path.isdir(dst_path):
        os.makedirs(dst_path, exist_ok=True)

    paths_ = [
        os.path.join(dst_path, "checkpoint-*", "artifacts", "checkpoint-*"),
        os.path.join(dst_path, "artifacts", "checkpoint-*"),
        os.path.join(dst_path, "artifacts", "**", "best.pt"),
    ]
    for i in paths_:
        paths = glob.glob(i, recursive=True)
        if paths:
            return paths[0]

    # raise TypeError(f"find_registry_path failed {dst_path}")
    return dst_path


# def download_from_registry(src_path: str, dst_path: str):
#     """从mlflow下载模型."""
#     import mlflow

#     paths = glob.glob(search_path)
#     if paths:
#         return paths[0]

#     mlflow.pyfunc.load_model(src_path, dst_path=dst_path)
#     return glob.glob(search_path)[0]


class BaseModel(pydantic.BaseModel):
    """BaseModel."""

    class Config:
        """Config."""

        orm_mode = True
        alias_generator = camelize
        allow_population_by_field_name = True
        # use_enum_values = True
