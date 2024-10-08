# -*- coding: utf-8 -*-
"""
@create: 2021-07-22 20:47:05.

@author: name

@desc: s3接口
"""

from typing import Optional
from urllib.parse import urlparse

from .base import S3Client as S3ClientBase
from .base import S3Session
from .cache_client import S3CacheClient
from .image_client import S3ImageClient
from .image_client import S3ImageUrlClient
from .upoload_client import S3UploadClient


class S3Client(object):
    """文件管理服务."""

    def __init__(
        self,
        s3cli: S3ClientBase,
        sign_expire: Optional[int] = None,
        bucket: Optional[str] = None,
    ):
        """初始化函数."""
        if bucket is None:
            bucket = "pdfocr_test"

        self.image = S3ImageClient(s3cli, sign_expire, bucket)
        self.direction = S3ImageClient(s3cli, sign_expire, bucket, "direction")
        self.thumbnail = S3ImageUrlClient(s3cli, sign_expire, bucket, "simgs")
        self.studio = S3ImageUrlClient(s3cli, sign_expire, bucket, "studio")
        self.history = S3ImageUrlClient(s3cli, sign_expire, bucket, "history")
        self.upload = S3UploadClient(s3cli, sign_expire, bucket)
        self.words = S3CacheClient(s3cli, sign_expire, bucket, "words")
        self.rotate = S3CacheClient(s3cli, sign_expire, bucket, "rotates")
        self.tasks = S3CacheClient(s3cli, sign_expire, bucket, "tasks")
        self.tables = S3CacheClient(s3cli, sign_expire, bucket, "tables")
        self.coco = S3CacheClient(s3cli, sign_expire, bucket, "coco")
        self.s3cli = s3cli
        self.bucket = bucket

    async def init_bucket(self):
        """初始化桶信息."""
        await self.s3cli.create_bucket_when_not_exists(self.bucket)
        await self.s3cli.create_bucket_lifecycle_when_not_exists(
            self.bucket,
            {
                "Rules": [
                    {
                        "ID": "rule_temp",
                        "Prefix": self.upload.TEMP_PATH + "/",
                        "Status": "Enabled",
                        "Expiration": {
                            "Days": 1,
                            # 'Date': datetime(2015, 1, 1),
                            # 'ExpiredObjectDeleteMarker': True|False
                        },
                    }
                ]
            },
        )

    async def clear_bucket(self):
        """清理桶数据."""
        async with self.s3cli.client.client() as s3cli:
            objs = await s3cli.list_objects_v2(Bucket=self.bucket)
            if not objs.get("Contents", []):
                return

            response = await s3cli.delete_objects(
                Bucket=self.bucket,
                Delete={
                    "Objects": [
                        {
                            "Key": i["Key"],
                        }
                        for i in objs["Contents"]
                    ],
                    "Quiet": True,
                },
            )
            return response

    @classmethod
    def from_config(
        cls,
        url,
        presign_expire: Optional[int] = None,
        bucket_name: Optional[str] = None,
    ):
        """创建客户端，构造函数."""
        url_ = urlparse(url)
        if url_.port:
            cli = S3Session(
                f"{url_.scheme}://{url_.hostname}:{url_.port}",
                url_.username,
                url_.password,
            )
        else:
            cli = S3Session(
                f"{url_.scheme}://{url_.hostname}", url_.username, url_.password
            )
        return cls(S3ClientBase(cli), presign_expire, bucket_name)


class S3ScpClient(object):
    """文件管理服务."""

    def __init__(
        self,
        s3cli: S3ClientBase,
        sign_expire: Optional[int] = None,
        bucket: Optional[str] = None,
    ):
        """初始化函数."""
        if bucket is None:
            bucket = "scpres_test"

        self.upload = S3UploadClient(s3cli, sign_expire, bucket, prefix="files")
        self.s3cli = s3cli
        self.bucket = bucket

    async def init_bucket(self):
        """初始化桶信息."""
        await self.s3cli.create_bucket_when_not_exists(self.bucket)

    @classmethod
    def from_config(
        cls,
        url,
        presign_expire: Optional[int] = None,
        bucket_name: Optional[str] = None,
    ):
        """创建客户端，构造函数."""
        url_ = urlparse(url)
        if url_.port:
            cli = S3Session(
                f"{url_.scheme}://{url_.hostname}:{url_.port}",
                url_.username,
                url_.password,
            )
        else:
            cli = S3Session(
                f"{url_.scheme}://{url_.hostname}", url_.username, url_.password
            )
        return cls(S3ClientBase(cli), presign_expire, bucket_name)
