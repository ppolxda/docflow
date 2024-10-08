# -*- coding: utf-8 -*-
"""
@create: 2021-08-20 09:34:40.

@author: name

@desc: s3接口
"""

import re
from base64 import b64encode
from datetime import date
from hashlib import md5
from typing import Optional
from uuid import uuid4

import filetype

from docflow.exceptions import ParamsError

from .base import S3BizClient
from .base import S3Client

EXTENSIONS = set(i.extension for i in filetype.TYPES) | set(["json"])
CACHE_RE = re.compile(r"^s3://.*?/cache/[0-9]{8}/(.*?)$")
# 's3://pdfocr/cache/20221225/e3e92c62956e976b13ca7097de4b04f3.pdf'


class S3UploadClient(S3BizClient):
    """临时文件上传."""

    TEMP_PATH = "cache"

    def __init__(
        self,
        s3cli: "S3Client",
        sign_expire: Optional[int] = None,
        bucket: Optional[str] = None,
        prefix: Optional[str] = None,
    ):
        """初始化函数."""
        super().__init__(s3cli, sign_expire, bucket)
        if prefix:
            self.prefix = prefix
        else:
            self.prefix = self.TEMP_PATH

    def is_cache_s3_key(self, s3_key):
        """检查是否是临时上传地址."""
        return CACHE_RE.match(s3_key)

    # ----------------------------------------------
    #        上传临时文件
    # ----------------------------------------------

    def __gen_temp_name(self, suffix: str, fname: Optional[str] = None):
        if suffix.startswith("."):
            suffix = suffix[1:]

        if suffix not in EXTENSIONS:
            raise ParamsError("filetype invaild")

        if fname is None:
            fname = str(uuid4())

        return self.make_s3_key(
            "/".join(
                [
                    self.prefix,
                    date.today().strftime("%Y%m%d"),
                    str(fname).replace("-", "") + "." + suffix,
                ]
            ),
        )

    def create_s3_object_by_hash(self, suffix: str, data: bytes):
        """根据文件id创建路径."""
        hashs = md5(data).hexdigest()
        s3_obj = self.create_s3_object_by_suffix(suffix, hashs)
        return s3_obj

    def create_s3_object_by_suffix(self, suffix: str, fname: Optional[str] = None):
        """创建临时目录."""
        s3_key = self.__gen_temp_name(suffix, fname)
        obj = self.s3cli.create_s3_object(s3_key)
        return obj

    async def put_file(
        self, data: bytes, froce: bool = False, filename: Optional[str] = None
    ):
        """上传临时文件, 并创建新的id."""
        content_type = filetype.guess(data)
        if content_type is None:
            raise ParamsError("filetype invaild")

        suffix = content_type.extension
        content_type = content_type.mime
        obj = self.create_s3_object_by_hash(suffix, data)

        # 检查是否下载过
        is_exist = await obj.is_exist_s3()
        if not froce and is_exist:
            return obj

        metadata = None
        if filename:
            metadata = {"filename": b64encode(filename.encode()).decode()}

        # 上传文件
        await obj.put_s3(data, content_type=content_type, metadata=metadata)
        return obj
