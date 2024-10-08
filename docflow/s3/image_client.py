# -*- coding: utf-8 -*-
"""
@create: 2021-07-22 20:47:05.

@author: name

@desc: s3接口
"""
from hashlib import md5
from typing import Optional

from .base import PutDataImage
from .base import S3BizClient
from .base import S3Client
from .base import S3ObjectImage
from .base import S3ObjectPathImage


class S3ObjectPathImagePage(S3ObjectPathImage):
    """S3ObjectPathImagePage."""

    # def __init__(self, mcli: MinioClientBase, s3_key: str):
    #     """初始化函数."""
    #     super().__init__(mcli, s3_key)

    def create_image_page_s3(self, page: int) -> S3ObjectImage:
        """转换图片缓存."""
        page_name = f"{page:03d}.png"
        return super().create_image_s3(page_name)

    def create_putdata_image_page_s3(self, page: int, data: bytes) -> PutDataImage:
        """转换图片缓存."""
        page_name = f"{page:03d}.png"
        return super().create_putdata_image_s3(page_name, data)


class S3ImageClient(S3BizClient):
    """临时文件搬运库."""

    DEFAULT_IMAGE_PATH = "imgs"

    def __init__(
        self,
        s3cli: S3Client,
        sign_expire: Optional[int] = None,
        bucket: Optional[str] = None,
        prefix: Optional[str] = None,
    ):
        """初始化函数."""
        super().__init__(s3cli, sign_expire, bucket)
        if prefix is None:
            self.image_path = self.DEFAULT_IMAGE_PATH
        else:
            self.image_path = prefix

    # ----------------------------------------------
    #        图片缓存管理
    # ----------------------------------------------

    def __make_image_path(self, hash_code: str, page: Optional[int] = None):
        """转换图片缓存."""
        path_ = "/".join([self.image_path, hash_code[:2], hash_code])
        if isinstance(page, int):
            return self.make_s3_key("/".join([path_, str(page) + ".png"]))
        else:
            return self.make_s3_key(path_ + "/")

    def make_image_s3_dir(self, hash_code: str):
        """创建缓存对象."""
        s3_key = self.__make_image_path(hash_code)
        return S3ObjectPathImagePage(self.s3cli, s3_key)


class S3ImageUrlClient(S3BizClient):
    """基于Url地址创建图片缓存.

    主要用于已知图像唯一地址，基于地址创建二次加公图片
    例如 图片缩略，图片大小尺寸，旋转图片缓存
    """

    DEFAULT_IMAGE_PATH = "process"

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
            self.image_path = self.DEFAULT_IMAGE_PATH
        else:
            self.image_path = path

    # ----------------------------------------------
    #        图片缓存管理
    # ----------------------------------------------

    def __make_image_path(self, url: str, suffix: str = ".png"):
        """转换图片缓存."""
        url_hash = md5(url.encode("utf8")).hexdigest()
        path_ = "/".join([self.image_path, str(url_hash) + suffix])
        return self.make_s3_key(path_)

    def make_image_s3_by_url(self, url: str):
        """创建缓存对象."""
        s3_key = self.__make_image_path(url)
        return S3ObjectImage(self.s3cli, s3_key)
