# -*- coding: utf-8 -*-
"""
@create: 2021-07-16 10:39:32.

@author: ppolxda

@desc: 数据库Session
"""

import os
import re
from dataclasses import dataclass
from typing import Optional

from pydantic import BaseSettings
from pydantic.networks import HttpUrl
from sqlalchemy.engine.url import make_url

# from .pre_process.ocrs import EnumOcrMode

PROD = os.getenv("PROD", "")


@dataclass
class OAuthProvider:
    """社交登录提供者信息."""

    provider: str
    client_id: str
    secret: str


class Settings(BaseSettings):
    """配置项."""

    # 设置是否开启Swagger在线文档
    PRINT_SQL: bool = bool(os.environ.get("PRINT_SQL", "false") == "true")
    IS_DEBUG: bool = bool(os.environ.get("IS_DEBUG", "false") == "true")
    SHOW_DOC: bool = bool(os.environ.get("SHOW_DOC", "false") == "true")
    BACKEND_MODE: str = "all"
    DISABLED_GUEST: bool = False
    IMAGE_RESOLUTION: int = 150

    # ----------------------------------------------
    #        授权认证
    # ----------------------------------------------

    PWD_SECRET: str = ""
    AUTH_SECRET: str = ""
    DOC_SECRET: str = ""
    AUTH_TOKEN_URL: str = "/auth/login"
    AUTH_TOKEN_EXPIRES: int = 60
    DEFAULTH_ORGANIZATION_NAME: str = "默认机构"

    # ----------------------------------------------
    #        虚拟路径
    # ----------------------------------------------

    ROOT_PATH: str = ""
    ROOT_PATH_IN_SERVERS: bool = False

    # ----------------------------------------------
    #        超时设置
    # ----------------------------------------------

    # Redis连接配置
    REDIS_URI: str = "redis://localhost:6379/1"

    MAX_RETRY: int = 5  # 重试次数
    OCR_MAX_RETRY: int = 10  # 重试次数
    MIN_RETRY_SLEEPTIME: int = 1  # 最小重试延时
    MAX_RETRY_SLEEPTIME: int = 3  # 最大重试延时
    DOWNLOAD_TIMEOUT: int = 5 * 60  # 下载pdf超时时间
    WEBHOOK_TIMEOUT: int = 5 * 60  # 发送webhook 超时时间
    WEBHOOK_MAX_RETRY: int = 5  # 发送webhook 最大重试次数
    PREDICT_TIMEOUT: int = 5 * 60  # 预测模型超时事件
    TASK_EXPIRE_TTL: int = 2 * 60  # 任务锁时长
    PDF2IMAGE_THRED_COUNT: int = 4  # PDF转换图片线程数
    MAX_INDEX_SIZE: int = 10000  # 最大索引查询大小

    # ----------------------------------------------
    #        S3设置
    # ----------------------------------------------

    S3_REMOTE_URI: str = "http://minioadmin:minioadmin@localhost:9000"
    S3_LOCAL_URI: str = "http://minioadmin:minioadmin@localhost:9000"
    S3_BUCKET: str = "pdfocr"
    S3_SIGN_EXPIRE: int = 3 * 60

    # ----------------------------------------------
    #        请求限制
    # ----------------------------------------------

    MAX_INT: int = 100000000
    MAX_LONG: int = 100000000
    MAX_DOUBLE: int = 100000000
    MAX_LENGTH: int = 128

    # ----------------------------------------------
    #        关系数据库相关配置结束
    # ----------------------------------------------

    # postgres连接池配置
    DB_URI: str = "postgresql+psycopg2://xpdf:xpdf@localhost:5432/pdfocr"
    SQLALCHEMY_POOL_SIZE = 5
    SQLALCHEMY_POOL_TIMEOUT = 30
    SQLALCHEMY_POOL_RECYCLE = 1800
    SQLALCHEMY_MAX_OVERFLOW = 10

    # ----------------------------------------------
    #        消息中间件
    # ----------------------------------------------

    # AMQP连接池配置
    AMQP_ENABLED: bool = True
    AMQP_URI: str = "amqp://guest:guest@localhost/"
    AMQP_APP_ID: str = "ocr"
    AMQP_APP_QUEUE_NAME: str = "pdfocr"
    AMQP_APP_QUEUE_NAME_ASYNC: str = "pdfocr_async"
    AMQP_APP_QUEUE_RANGE: int = 3
    AMQP_APP_QUEUE_RANGE_ASYNC: int = 2
    AMQP_TIMEOUT: int = 10
    AMQP_POOL_SIZE = 5
    AMQP_POOL_TIMEOUT = 30
    AMQP_POOL_RECYCLE = 1800
    AMQP_MAX_OVERFLOW = 10

    # ----------------------------------------------
    #        OCR接口
    # ----------------------------------------------

    OCR_API: str = HttpUrl("http://localhost:8089", scheme="http")  # type: ignore
    OCR_TIMEOUT: int = 5 * 60
    OCR_COMPRESS: int = 70
    OCR_MODE: str = "DocOcrv2"

    # ----------------------------------------------
    #        GOOGLE OCR识别接口
    # ----------------------------------------------

    GOOGLE_API: str = HttpUrl("http://8.210.121.25:20000/gapi", scheme="http")  # type: ignore
    GOOGLE_API_TIMEOUT: int = 30 * 60
    GOOGLE_API_WEB_SIGN_SALT: str = ""

    # ----------------------------------------------
    #        Microsoft OCR识别接口
    # ----------------------------------------------

    MICROSOFT_API: str = HttpUrl("http://localhost:5003", scheme="http")  # type: ignore
    MICROSOFT_TIMEOUT: int = 5 * 60

    # ----------------------------------------------
    #        工作流组件接口
    # ----------------------------------------------

    CONDUCTOR_API: str = HttpUrl("http://127.0.0.1:8080", scheme="http")  # type: ignore
    CONDUCTOR_API_TIMEOUT: int = 5 * 60
    CONDUCTOR_WORKER_QUEUE_NAME: str = ""
    CONDUCTOR_WORKER_INTERVAL: float = 1
    CONDUCTOR_WORKER_DOMAIN: str = ""

    # ----------------------------------------------
    #        请求后端地址
    # ----------------------------------------------

    BACKEND_API: str = HttpUrl("http://127.0.0.1:21110", scheme="http")  # type: ignore
    BACKEND_API_TIMEOUT: int = 30 * 60

    # ----------------------------------------------
    #        默认预测模型接口
    # ----------------------------------------------

    PDFCLASS_API: str = ""
    KEYINFO_API: str = ""

    # ----------------------------------------------
    #        ES 索引引擎地址
    # ----------------------------------------------

    ELASTICSEARCH_MODE: str = "ES6"
    ELASTICSEARCH_PREFIX: str = "field-index"
    ELASTICSEARCH_API: str = HttpUrl("http://127.0.0.1:9200", scheme="http")  # type: ignore
    ELASTICSEARCH_REFRESH_IMMEDIATELY: bool = False

    # ----------------------------------------------
    #        OAuth 三方授权登录
    # ----------------------------------------------

    # OAUTH_AUTHORIZATION_URL: str = ""
    # OAUTH_REDIRECT_URL: str = ""
    # OAUTH_CLIENT_ID: str = ""
    OAUTH_SECRET: str = ""
    OAUTH_CHECK_PROVIDER: bool = True

    # ----------------------------------------------
    #        NanoNets表格预测模型
    # ----------------------------------------------

    BASIC_AUTH: str = ""
    MODEL_ID: str = ""
    NANONETS_APIS: str = ""

    # ----------------------------------------------
    #        图像旋转识别
    # ----------------------------------------------

    ROTATE_API: str = HttpUrl("http://localhost:5002", scheme="http")  # type: ignore
    ROTATE_TIMEOUT: int = 60

    # ----------------------------------------------
    #        Word转换Pdf
    # ----------------------------------------------
    TRANSFORM_API: str = HttpUrl("http://localhost:9011", scheme="http")  # type: ignore
    TRANSFORM_TIMEOUT: int = 60

    # ----------------------------------------------
    #        Label Studio Config
    # ----------------------------------------------
    STUDIO_API: str = HttpUrl("http://localhost:8080", scheme="http")  # type: ignore
    STUDIO_AUTHORIZATION: str = ""
    STUDIO_TIMEOUT: int = 60 * 3

    # 开启协程数量控制
    SEMAPHORE: int = 100

    # 图片均值
    DEFAULT_CHUNK: int = 2400
    oauth_secretst: Optional[dict] = None

    def oauth_secrets(self) -> dict:
        """授权密钥组."""
        secrets = self.oauth_secretst
        if secrets is not None:
            return secrets

        secrets = re.findall(r"(.*?):(.*?):(.*?)(?:$|,)", self.OAUTH_SECRET)
        secrets = {
            vals[1]: OAuthProvider(provider=vals[0], client_id=vals[1], secret=vals[2])
            for vals in secrets
        }
        self.oauth_secretst = secrets
        return secrets

    def get_oauth_secrets_by_client_id(self, client_id) -> Optional[OAuthProvider]:
        """授权密钥组."""
        secrets = self.oauth_secrets()
        return secrets.get(client_id, None)

    def format_print(self):
        """格式化配置打印."""
        # await database.connect()
        log = ["--------------------------------------"]
        for key, val in self.dict().items():
            if key in ["S3_ROOT_PASSWORD", "AUTH_SECRET", "PWD_SECRET"]:
                continue

            if key.endswith("_URI"):
                log.append(f"[{key:23s}]: {repr(make_url(val))}")
            else:
                log.append(f"[{key:23s}]: {val}")

        log.append("--------------------------------------")
        return log

    class Config:
        """从指定的配置文件（local、dev、prod）中读取环境变量."""

        env_file = "_".join([".env.", PROD]) if PROD else ".env"
        env_file_encoding = "utf-8"


settings = Settings()
