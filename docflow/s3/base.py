# -*- coding: utf-8 -*-
"""
@create: 2021-07-22 20:47:05.

@author: name

@desc: s3接口
"""
import contextlib
import json
import logging
import os
from dataclasses import dataclass
from datetime import timedelta
from io import BytesIO
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Union
from urllib.parse import urlparse

import aioboto3
from aiobotocore.config import AioConfig
from botocore.exceptions import ClientError
from PIL import Image

from ..utils.fileutils import bytes_to_image
from ..utils.fileutils import image_to_bytes

DEFAULT_PUT_EXPIRES = timedelta(days=7)
DEFAULT_GET_EXPIRES = timedelta(days=7)

LOGGER = logging.getLogger()


def hook_not_such_key():
    """抓取NoSuchKey错误."""

    def wrapper(func):
        async def wrapper_call(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except ClientError as ex:
                assert isinstance(ex.response, dict)
                if ex.response.get("Error", {}).get("Code", "") in ["404"]:
                    return None
                raise ex

        return wrapper_call

    return wrapper


def parse_s3_key(s3_key):
    """解析一个S3连接."""
    if not s3_key.startswith("s3://") or "/" not in s3_key:
        raise TypeError(f"s3 url invaild, {s3_key}")

    s3_ = urlparse(s3_key)
    bucket = s3_.netloc
    object_id = s3_.path
    return bucket, object_id


def make_s3_key(bucket, object_id: str):
    """构建一个S3连接."""
    if not object_id.startswith("/"):
        object_id = "/" + object_id

    assert "/" in object_id and object_id.startswith("/")
    return f"s3://{bucket}{object_id}"


@dataclass
class PutData(object):
    """PutData."""

    obj: "S3Object"
    data: bytes


@dataclass
class PutDataImage(object):
    """PutData."""

    obj: "S3ObjectImage"
    data: Union[bytes, BytesIO, Image.Image]


@dataclass
class ImageObject:
    """图片对象."""

    file_name: str
    object_name: str
    object_url: str
    s3_key: str
    width: int
    height: int


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

    @contextlib.asynccontextmanager
    async def client(self):
        """创建客户端."""
        session = aioboto3.Session()
        async with session.client(
            "s3",
            region_name=self.region_name,
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            config=self.config,
        ) as s3cli:
            yield s3cli


class S3Object(object):
    """S3Object."""

    def __init__(self, s3cli: "S3Client", s3_key: str):
        """初始化函数."""
        assert s3_key.startswith("s3://")
        self.s3cli = s3cli
        self.s3_key = s3_key

    async def put_s3(
        self,
        data: bytes,
        content_type="application/octet-stream",
        metadata=None,
    ):
        """保存文件."""
        if metadata is None:
            metadata = {}

        bucket, object_id = parse_s3_key(self.s3_key)
        async with self.s3cli.create_client() as s3cli:
            r = await s3cli.put_object(
                Bucket=bucket,
                Key=object_id,
                Body=data,
                ContentType=content_type,
                Metadata=metadata,
            )
            return r

    async def put_s3_block(
        self,
        file_path: str = "",
    ):
        """分块上传文件."""
        bucket, object_id = parse_s3_key(self.s3_key)

        chunk_size = 10 * 1024 * 1024
        file_size = os.path.getsize(file_path)
        LOGGER.info(f"文件大小{file_size}")

        async with self.s3cli.create_client() as s3cli:
            r = await s3cli.create_multipart_upload(Bucket=bucket, Key=object_id)
            upload_id = r["UploadId"]

            try:
                part_number = 1
                offset = 0
                parts = []
                while offset < file_size:
                    # 读取块数据
                    with open(file_path, "rb") as file:
                        file.seek(offset)
                        data = file.read(chunk_size)

                    # 上传块
                    response = await s3cli.upload_part(
                        Bucket=bucket,
                        Key=object_id,
                        PartNumber=part_number,
                        UploadId=upload_id,
                        Body=data,
                    )
                    parts.append({"PartNumber": part_number, "ETag": response["ETag"]})
                    part_number += 1
                    offset += len(data)

                await s3cli.complete_multipart_upload(
                    Bucket=bucket,
                    Key=object_id,
                    UploadId=upload_id,
                    MultipartUpload={"Parts": parts},
                )

                LOGGER.info("Upload complete.")
            except Exception as e:
                LOGGER.info("Error: " + str(e))
                await s3cli.abort_multipart_upload(
                    Bucket=bucket, Key=object_id, UploadId=upload_id
                )

    @hook_not_such_key()
    async def get_s3(self) -> bytes:
        """获取数据."""
        bucket, object_id = parse_s3_key(self.s3_key)
        async with self.s3cli.create_client() as s3cli:
            rrr = await s3cli.get_object(Bucket=bucket, Key=object_id)
            data = await rrr["Body"].read()
            return data

    @hook_not_such_key()
    async def get_stat_s3(self) -> dict:
        """键值是否存在."""
        bucket, object_id = parse_s3_key(self.s3_key)
        async with self.s3cli.create_client() as s3cli:
            r = await s3cli.head_object(Bucket=bucket, Key=object_id)
            return r["Metadata"]

    async def is_exist_s3(self):
        """键值是否存在."""
        r = await self.get_stat_s3()
        return r

    async def presigned_post_s3(
        self,
        metadata: Optional[Dict[str, Any]] = None,
        expires: Optional[timedelta] = None,
    ):
        """签名一个S3连接."""
        bucket, object_id = parse_s3_key(self.s3_key)
        if object_id.startswith("/"):
            object_id = object_id[1:]

        if expires is None:
            expires = DEFAULT_PUT_EXPIRES

        if metadata is None:
            metadata = {}

        async with self.s3cli.create_client() as s3cli:
            r = await s3cli.generate_presigned_post(
                Bucket=bucket,
                Key=object_id,
                ExpiresIn=int(expires.total_seconds()),
                Fields=metadata,
                Conditions=[metadata],
            )
            return r["url"], r["fields"]

    async def presigned_put_s3(
        self,
        expires: Optional[timedelta] = None,
    ):
        """签名一个S3连接."""
        bucket, object_id = parse_s3_key(self.s3_key)
        if object_id.startswith("/"):
            object_id = object_id[1:]

        if expires is None:
            expires = DEFAULT_GET_EXPIRES

        async with self.s3cli.create_client() as s3cli:
            r = await s3cli.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": bucket,
                    "Key": object_id,
                },
                ExpiresIn=int(expires.total_seconds()),
            )
            return r

    async def presigned_get_s3(self, expires: Optional[timedelta] = None):
        """签名一个S3连接."""
        bucket, object_id = parse_s3_key(self.s3_key)
        if object_id.startswith("/"):
            object_id = object_id[1:]

        if expires is None:
            expires = DEFAULT_GET_EXPIRES

        async with self.s3cli.client.client() as s3cli:
            r = await s3cli.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": bucket,
                    "Key": object_id,
                },
                ExpiresIn=int(expires.total_seconds()),
            )
            return r

    async def delete_s3(self):
        """删除键值."""
        bucket, object_id = parse_s3_key(self.s3_key)
        async with self.s3cli.create_client() as s3cli:
            await s3cli.delete_object(
                Bucket=bucket,
                Key=object_id,
            )


class S3ObjectJson(S3Object):
    """S3ObjectJson."""

    async def put_json_s3(self, json_data: dict):
        """缩略图生成保存."""
        data = json.dumps(json_data).encode()
        r = await self.put_s3(data, content_type="application/json")
        return r

    async def get_json_s3(self, defval=None):
        """获取数据."""
        data = await self.get_s3()
        if not data:
            return defval

        return json.loads(data)


class S3ObjectImage(S3Object):
    """S3ObjectJson."""

    async def put_image_s3(self, image_data: Union[bytes, BytesIO, Image.Image]):
        """缩略图生成保存."""
        if isinstance(image_data, BytesIO):
            _image = bytes_to_image(image_data)
        elif isinstance(image_data, Image.Image):
            _image = image_data
        else:
            _image = bytes_to_image(image_data)

        _height = _image.height
        _width = _image.width

        _data = image_to_bytes(_image)
        r = await self.put_s3(
            _data,
            content_type="image/png",
            metadata={
                "height": str(_height),
                "width": str(_width),
            },
        )
        return r

    async def get_image_s3(self, defval=None):
        """获取数据."""
        data = await self.get_s3()
        if not data:
            return defval

        return bytes_to_image(data)


class S3ObjectPath(object):
    """S3ObjectPath.

    目录暂时只考虑一层目录
    """

    def __init__(self, s3cli: "S3Client", s3_key: str):
        """初始化函数."""
        if s3_key.endswith("/"):
            s3_key = s3_key[:-1]

        self.s3cli = s3cli
        self.s3_key = s3_key

    async def delete_dir_s3(self, limit=100):
        """删除整个目录."""
        bucket, object_id = parse_s3_key(self.s3_key)
        async with self.s3cli.create_client() as s3cli:
            objs = await s3cli.list_objects_v2(Bucket=bucket, Prefix=object_id)
            if not objs.get("Contents", []):
                return

            if len(objs["Contents"]) > limit:
                raise TypeError("delete to many")

            response = await s3cli.delete_objects(
                Bucket=bucket,
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

    def create_object_s3(self, object_id: str):
        """创建上传对象."""
        if object_id.endswith("/"):
            object_id = object_id[:-1]

        s3_key = "/".join([self.s3_key, object_id])
        return S3Object(self.s3cli, s3_key)

    def create_putdata_s3(self, object_id: str, data: bytes):
        """创建上传对象."""
        assert object_id and data
        obj = self.create_object_s3(object_id)
        return PutData(obj=obj, data=data)

    async def list_objects_s3(self):
        """获取对象列表."""
        bucket, object_id = parse_s3_key(self.s3_key)
        async with self.s3cli.create_client() as s3cli:
            if object_id.startswith("/"):
                object_id = object_id[1:]

            objs = await s3cli.list_objects_v2(Bucket=bucket, Prefix=object_id)
            if not objs.get("Contents", []):
                return

            for i in objs["Contents"]:
                yield bucket, i

    async def multi_put_s3(self, datas: Union[List[PutData], Iterator[PutData]]):
        """上传PDF图片缓存."""
        await self.delete_dir_s3()

        if not datas:
            return

        return [await i.obj.put_s3(i.data) for i in datas]


class S3ObjectPathImage(S3ObjectPath):
    """S3ObjectPathImage.

    目录暂时只考虑一层目录
    """

    def create_image_s3(self, object_id: str) -> S3ObjectImage:
        """创建上传对象."""
        if object_id.endswith("/"):
            object_id = object_id[:-1]

        s3_key = "/".join([self.s3_key, object_id])
        return S3ObjectImage(self.s3cli, s3_key)

    def create_putdata_image_s3(
        self, object_id: str, data: Union[bytes, BytesIO, Image.Image]
    ) -> PutDataImage:
        """创建上传对象."""
        assert object_id and data
        obj = self.create_image_s3(object_id)
        return PutDataImage(obj=obj, data=data)

    async def list_images_s3(self, expires: Optional[int] = None):
        """删除源图缓存集合."""
        if expires is None:
            expires = int(DEFAULT_GET_EXPIRES.total_seconds())

        expires_ = timedelta(seconds=float(expires))

        async for bucket, x in self.list_objects_s3():
            key = x.get("Key", "")
            if not key:
                continue

            s3_key = make_s3_key(bucket, key)
            s3_obj = self.s3cli.create_s3_image(s3_key)

            # 切换后性能低，需要提供
            url = await s3_obj.presigned_get_s3(expires_)
            metadata = await s3_obj.get_stat_s3()

            yield ImageObject(
                **{
                    "file_name": os.path.basename(key),
                    "object_name": key,
                    "object_url": url,
                    "s3_key": make_s3_key(self.s3cli.bucket, key),
                    "height": int(metadata.get("X-Amz-Meta-Height", 0))
                    if metadata
                    else 0,
                    "width": int(metadata.get("X-Amz-Meta-Width", 0))
                    if metadata
                    else 0,
                }
            )

    async def multi_put_images_s3(
        self, datas: Union[List[PutDataImage], Iterator[PutDataImage]]
    ):
        """上传PDF图片缓存."""
        await self.delete_dir_s3()

        if not datas:
            return

        return [await i.obj.put_image_s3(i.data) for i in datas]


class S3BizClient(object):
    """S3Object."""

    def __init__(
        self,
        s3cli: "S3Client",
        sign_expire: Optional[int] = None,
        bucket: Optional[str] = None,
    ):
        """初始化函数."""
        if bucket is None:
            bucket = "pdfocr"

        if sign_expire is None:
            sign_expire = 30 * 60

        self.s3cli = s3cli
        self.bucket = bucket
        self.sign_expire = sign_expire

    def make_s3_key(self, object_id: str):
        """构建一个S3连接."""
        return make_s3_key(self.bucket, object_id)


class S3Client(object):
    """文件管理服务."""

    def __init__(
        self,
        client: S3Session,
        bucket: Optional[str] = None,
    ):
        """初始化函数."""
        if bucket is None:
            bucket = "pdfocr"

        self.client = client
        self.bucket = bucket
        self.create_client = self.client.client

    def create_s3_json(self, s3_key: str):
        """构建S3JSON对象."""
        assert s3_key.startswith("s3://")
        return S3ObjectJson(self, s3_key)

    def create_s3_object(self, s3_key: str):
        """构建S3对象."""
        assert s3_key.startswith("s3://")
        return S3Object(self, s3_key)

    def create_s3_image(self, s3_key: str):
        """构建S3图像对象."""
        assert s3_key.startswith("s3://")
        return S3ObjectImage(self, s3_key)

    def create_s3_dir(self, s3_key: str):
        """构建S3图像对象."""
        assert s3_key.startswith("s3://")
        return S3ObjectPath(self, s3_key)

    async def create_bucket_when_not_exists(self, bucket: str):
        """如果桶不存在创建桶."""
        async with self.client.client() as s3cli:
            try:
                await s3cli.head_bucket(Bucket=bucket)
            except ClientError as ex:
                assert isinstance(ex.response, dict)
                if ex.response.get("Error", {}).get("Code", "") in [
                    "NoSuchKey",
                ] or ex.response.get("Error", {}).get("Message", "") in [
                    "Not Found",
                ]:
                    await s3cli.create_bucket(Bucket=bucket)
                    return True
                raise ex
            return False

    async def create_bucket_lifecycle_when_not_exists(self, bucket: str, lifecycle):
        """如果桶不存在创建桶."""
        async with self.client.client() as s3cli:
            try:
                await s3cli.get_bucket_lifecycle(Bucket=bucket)
            except ClientError as ex:
                assert isinstance(ex.response, dict)
                if ex.response.get("Error", {}).get("Code", "") in [
                    "NoSuchKey",
                    "NoSuchLifecycleConfiguration",
                ] or ex.response.get("Error", {}).get("Message", "") in [
                    "Not Found",
                ]:
                    await s3cli.put_bucket_lifecycle(
                        Bucket=bucket, LifecycleConfiguration=lifecycle
                    )
                    return True
                raise ex
            return False

    async def presigned_post_s3(self, s3_key, expires: Optional[timedelta] = None):
        """签名一个S3连接."""
        bucket, object_id = parse_s3_key(s3_key)
        if object_id.startswith("/"):
            object_id = object_id[1:]

        if expires is None:
            expires = DEFAULT_PUT_EXPIRES

        async with self.client.client() as s3cli:
            r = await s3cli.generate_presigned_post(
                Bucket=bucket, Key=object_id, ExpiresIn=int(expires.total_seconds())
            )
            return r["url"], r["fields"]

    async def presigned_get_s3(
        self, s3_key, expires: Optional[timedelta] = None
    ) -> str:
        """签名一个S3连接."""
        r = await self.presigned_get_s3_batch(iter([s3_key]), expires)
        return r[0]

    async def presigned_get_s3_batch(
        self, s3_keys: Iterator[str], expires: Optional[timedelta] = None
    ) -> List[str]:
        """签名一个S3连接."""
        if expires is None:
            expires = DEFAULT_GET_EXPIRES

        async with self.client.client() as s3cli:
            urls = []
            for s3_key in s3_keys:
                if not s3_key.startswith("s3://"):
                    urls.append(s3_key)
                    continue

                bucket, object_id = parse_s3_key(s3_key)
                if object_id.startswith("/"):
                    object_id = object_id[1:]

                r = await s3cli.generate_presigned_url(
                    ClientMethod="get_object",
                    Params={
                        "Bucket": bucket,
                        "Key": object_id,
                    },
                    ExpiresIn=int(expires.total_seconds()),
                )
                urls.append(r)

            return urls
