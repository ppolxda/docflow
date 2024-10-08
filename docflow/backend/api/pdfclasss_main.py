# -*- coding: utf-8 -*-
"""
@create: 2022-12-13 14:24:32.

@author: name

@desc: 文件功能描述
"""
import logging
import traceback

import click
import uvicorn
from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import Field
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

# from ..predict_utils import PDFCLASS_MODE
# from ..predict_transformers import Layoutlmv3ClassificationPredict
from ..predict_transformers import Layoutlmv3ClassificationBertPredict
from ..predict_utils import BaseModel

LOGGER = logging.getLogger()

cli = Layoutlmv3ClassificationBertPredict()


class PredictImageRequest(BaseModel):
    """PredictImageRequest."""

    url: str = Field("", title="文件地址")
    ocr_s3: str = Field("", title="OCR识别结果S3地址")


class PredictImageResponse(PredictImageRequest):
    """临时文件对象信息."""

    label: str = Field("", title="文件大小")


app = FastAPI()


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


@app.post("/predict/classification", response_model=PredictImageResponse)
async def get_model(req: PredictImageRequest):
    """请求模型推理."""
    label = await cli.predict(req.url, req.ocr_s3)
    return PredictImageResponse(url=req.url, ocr_s3=req.ocr_s3, label=label)


@click.command()
@click.option("--port", default=5000, help="端口")
@click.option("--host", default="127.0.0.1", help="绑定地址范围")
def main(port, host):
    """主函数."""
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
