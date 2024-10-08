# -*- coding: utf-8 -*-
"""
@create: 2021-07-22 20:47:05.

@author: name

@desc: s3接口
"""

from hashlib import md5
from typing import Optional

import filetype

from docflow import exceptions as err

from .base import S3BizClient
from .base import S3Client


class S3CacheClient(S3BizClient):
    """临时文件搬运库."""

    DEFAULT_PATH = "cache"

    def __init__(
        self,
        s3cli: S3Client,
        sign_expire: Optional[int] = None,
        bucket: Optional[str] = None,
        path: Optional[str] = None,
    ):
        """初始化函数."""
        super().__init__(s3cli, sign_expire, bucket)
        if path is None:
            self.prefix_path = self.DEFAULT_PATH
        else:
            self.prefix_path = path

    # ----------------------------------------------
    #        创建临时缓存
    # ----------------------------------------------

    def __make_s3_key(self, hash_code: str, suffix: str = "json"):
        """生成缓存的键值."""
        return self.make_s3_key(
            "/".join([self.prefix_path, hash_code[:2], hash_code + "." + suffix])
        )

    def make_json_s3_object(self, hash_code: str, suffix: str = "json"):
        """创建缓存对象."""
        s3_key = self.__make_s3_key(hash_code, suffix)
        return self.s3cli.create_s3_json(s3_key)

    # ----------------------------------------------
    #        上传任意文件类型
    # ----------------------------------------------

    def create_s3_object_by_hash(self, suffix: str, data: bytes):
        """根据文件id创建路径."""
        if suffix.startswith("."):
            suffix = suffix[1:]

        hashs = md5(data).hexdigest()
        hash_code = str(hashs).replace("-", "")
        s3_key = self.__make_s3_key(hash_code, suffix)
        obj = self.s3cli.create_s3_object(s3_key)
        return obj

    async def put_file(self, data: bytes, froce: bool = False):
        """上传临时文件, 并创建新的id."""
        content_type = filetype.guess(data)
        if content_type is None:
            raise err.ParamsError("filetype invaild")

        suffix = content_type.extension
        content_type = content_type.mime
        obj = self.create_s3_object_by_hash(suffix, data)

        # 检查是否下载过
        is_exist = await obj.is_exist_s3()
        if not froce and is_exist:
            return obj

        # 上传文件
        await obj.put_s3(data, content_type=content_type)
        return obj

    async def put_file_block(self, file_path: str, froce: bool = False):
        """分块上传文件."""
        # 防止读取大文件
        with open(file_path, "rb") as fs:
            data = fs.read(1024)

        content_type = filetype.guess(data)
        if content_type is None:
            raise err.ParamsError("FileType Invaild")

        suffix = content_type.extension
        content_type = content_type.mime
        obj = self.create_s3_object_by_hash(suffix, data)

        # 检查是否下载过
        is_exist = await obj.is_exist_s3()
        if not froce and is_exist:
            return obj

        await obj.put_s3_block(file_path)
        return obj
