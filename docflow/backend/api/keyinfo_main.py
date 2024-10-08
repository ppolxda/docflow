# -*- coding: utf-8 -*-
"""
@create: 2022-12-13 14:24:32.

@author: name

@desc: 文件功能描述
"""
import logging
import traceback
from io import BytesIO
from typing import List

import click
import uvicorn
from fastapi import FastAPI
from fastapi import Request
from fastapi import applications
from fastapi.datastructures import UploadFile
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.param_functions import File
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
from pydantic import Field
from pydantic.fields import Undefined
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from ..predict_transformers import Layoutlmv3Predict
from ..predict_transformers import WordSymbol
from ..predict_utils import BaseModel

LOGGER = logging.getLogger()


def swagger_monkey_patch(*args, **kwargs):
    """Fastapi文档CDN更换 monkey_patch."""
    return get_swagger_ui_html(
        *args,
        **kwargs,
        swagger_js_url="https://petstore.swagger.io/swagger-ui-bundle.js",
        swagger_css_url="https://petstore.swagger.io/swagger-ui.css",
    )


class PredictImageRequest(BaseModel):
    """PredictImageRequest."""

    url: str = Field("", title="文件地址")
    label: str = Field("", title="标签")
    ocr_s3: str = Field("", title="OCR识别结果S3地址")


class PredictImageResponse(PredictImageRequest):
    """临时文件对象信息."""

    tokens: List[WordSymbol] = Field(default_factory=list, title="推理关键信息")


app = FastAPI()
cli = Layoutlmv3Predict()
applications.get_swagger_ui_html = swagger_monkey_patch  # type: ignore


@app.exception_handler(Exception)
async def all_exception_handler(request: Request, exc: Exception):
    """异常捕获."""
    LOGGER.error(
        "unknow_error[%s]%s - %s", request.url.path, exc, traceback.format_exc()
    )
    return JSONResponse(
        {
            "error": str(exc),
        },
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
    )


@app.post("/predict/fields", response_model=PredictImageResponse)
async def get_model(req: PredictImageRequest):
    """请求模型推理."""
    _, tokens = await cli.predict(req.url, req.ocr_s3)
    return PredictImageResponse(
        url=req.url,
        label=req.label,
        ocr_s3=req.ocr_s3,
        tokens=[i for i in tokens if i.label != "other"],
    )


@app.post("/predict/fields/uplaod/image")
async def get_model_uplpad_(
    file: UploadFile = File(Undefined, description="PDF上传"),
):
    """请求模型推理."""
    data = await file.read()

    image, __ = await cli.predict_and_draw_box(data)

    data_ = BytesIO()
    image.save(data_, format="png")
    data_.seek(0)
    return StreamingResponse(data_, media_type="image/png")


@click.command()
@click.option("--port", default=5000, help="端口")
@click.option("--host", default="0.0.0.0", help="绑定地址范围")
def main(port, host):
    """主函数."""
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
