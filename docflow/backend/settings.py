# -*- coding: utf-8 -*-
"""
@create: 2021-07-16 10:39:32.

@author: ppolxda

@desc: 数据库Session
"""
import os

from pydantic import BaseSettings
from pydantic.networks import HttpUrl
from sqlalchemy.engine.url import make_url

PROD = os.environ.get("PROD", "")


class Settings(BaseSettings):
    """配置项."""

    # 设置是否开启Swagger在线文档
    PRINT_SQL: bool = bool(os.environ.get("PRINT_SQL", "false") == "true")
    IS_DEBUG: bool = bool(os.environ.get("IS_DEBUG", "false") == "true")
    SHOW_DOC: bool = bool(os.environ.get("SHOW_DOC", "false") == "true")
    BACKEND_MODE: str = "all"

    # ----------------------------------------------
    #        授权认证
    # ----------------------------------------------

    PWD_SECRET: str = "sdfgkjh980dgfuh89jnksdnkjf"
    AUTH_SECRET: str = "dijkhndsiusdfhihsduiafhiu"
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
    PREDICT_TIMEOUT: int = 5 * 60  # 预测模型超时事件
    TASK_EXPIRE_TTL: int = 2 * 60  # 任务锁时长

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
    AMQP_POOL_SIZE = 5
    AMQP_POOL_TIMEOUT = 30
    AMQP_POOL_RECYCLE = 1800
    AMQP_MAX_OVERFLOW = 10

    # ----------------------------------------------
    #        OCR接口
    # ----------------------------------------------

    OCR_API: str = HttpUrl("http://localhost:8089", scheme="http")  # type: ignore
    OCR_TIMEOUT: int = 5 * 60

    # ----------------------------------------------
    #        GOOGLE OCR识别接口
    # ----------------------------------------------

    GOOGLE_API: str = HttpUrl("http://8.210.121.25:20000/gapi", scheme="http")  # type: ignore
    GOOGLE_API_TIMEOUT: int = 30 * 60
    GOOGLE_API_WEB_SIGN_SALT: str = ""

    # ----------------------------------------------
    #        工作流组件接口
    # ----------------------------------------------

    CONDUCTOR_API: str = HttpUrl("http://127.0.0.1:8080", scheme="http")  # type: ignore
    CONDUCTOR_API_TIMEOUT: int = 5 * 60
    CONDUCTOR_WORKER_QUEUE_NAME: str = ""
    CONDUCTOR_WORKER_INTERVAL: float = 1
    CONDUCTOR_WORKER_DOMAIN_AI: str = ""
    CONDUCTOR_WORKER_DEBUG: bool = False

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
    WORD_LIMIT: int = 2048

    # ----------------------------------------------
    #        默认预测模型接口
    # ----------------------------------------------

    KEYINFO_MODULE: str = "modules/keyinfo"
    PDFCLASS_MODULE: str = "modules/pdfclassification"
    PDFCLASS_BERT_MODULE: str = "modules/pdfbertclassification"
    PDFSIDE_MODULE: str = "modules/pdfside"
    TABLE_STRUCTURE_MODULE: str = "modules/tabletransformer_structure"
    TABLE_DETECTION_MODULE: str = "modules/tabletransformer_detection"

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

        env_file = "_".join([".env", PROD]) if PROD else ".env"
        env_file_encoding = "utf-8"


settings = Settings()
