# -*- coding: utf-8 -*-
"""
@create: 2022-12-13 14:24:32.

@author: name

@desc: 文件功能描述
"""
import logging
import traceback
from io import BytesIO

import click
import uvicorn
from fastapi import FastAPI
from fastapi import Request
from fastapi.datastructures import UploadFile
from fastapi.param_functions import File
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
from PIL import Image
from pydantic import Field
from pydantic.fields import Undefined
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from ..predict_utils import BaseModel
from ..predict_yolo import YoloDataProcess

LOGGER = logging.getLogger()

cli = YoloDataProcess()


class PredictImageRequest(BaseModel):
    """PredictImageRequest."""

    url: str = Field("", title="文件地址")
    ocr_s3: str = Field("", title="OCR识别结果S3地址")


class PredictImageResponse(PredictImageRequest):
    """临时文件对象信息."""

    rotate: float = Field(0.0, title="预测旋转")


class PredictImageRotateResponse(BaseModel):
    """临时文件对象信息."""

    rotate: float = Field(0.0, title="预测旋转")


def rotate_image(image: Image.Image, rotate: float):
    """旋转图片."""
    if rotate == 0:
        return image

    return image.rotate(
        rotate,
        fillcolor=(0, 0, 0),
        expand=True,
    )


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


@app.post("/predict/rotate", response_model=PredictImageResponse)
async def get_model(req: PredictImageRequest):
    """请求模型推理."""
    label = await cli.predict(req.url, req.ocr_s3)
    return PredictImageResponse(url=req.url, ocr_s3=req.ocr_s3, rotate=label)


@app.post("/predict/rotate/uplaod", response_model=PredictImageRotateResponse)
async def get_model_uplpad(
    file: UploadFile = File(Undefined, description="PDF上传"),
):
    """请求模型推理."""
    data = await file.read()
    rotate = await cli.predict(data)
    return PredictImageRotateResponse(rotate=rotate)


@app.post("/predict/rotate/uplaod/image")
async def get_model_uplpad_(
    file: UploadFile = File(Undefined, description="PDF上传"),
):
    """请求模型推理."""
    data = await file.read()
    rotate = await cli.predict(data)

    data_ = BytesIO(data)
    data_.name = "test.png"
    img = rotate_image(Image.open(data_, formats=["png", "jpeg"]), -1 * rotate)
    data_.seek(0)
    img.save(data_)
    data_.seek(0)
    return StreamingResponse(data_, media_type="image/png")


@click.command()
@click.option("--port", default=5000, help="端口")
@click.option("--host", default="127.0.0.1", help="绑定地址范围")
def main(port, host):
    """主函数."""
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
