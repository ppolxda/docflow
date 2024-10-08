# -*- coding: utf-8 -*-
"""
@create: 2022-12-13 14:24:32.

@author: name

@desc: 文件功能描述
"""

import base64
import logging
import traceback
from io import BytesIO
from typing import List
from typing import Optional

import click
import uvicorn
from docflow.backend.predict_table.schemas import TabelInfo
from docflow.backend.predict_table.table_transformer import TableTransformerDetection
from docflow.backend.predict_table.table_transformer import TableTransformerStructure
from docflow.backend.predict_table.tables import TableStructurePredict
from docflow.backend.predict_utils import BaseModel
from docflow.backend.predict_utils import download_image
from fastapi import FastAPI
from fastapi import Query
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
from PIL import Image
from PIL import ImageDraw
from pydantic import Field
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

LOGGER = logging.getLogger()


class PredictImageRequest(BaseModel):
    """PredictImageRequest."""

    url: Optional[str] = Field("", title="文件地址")
    base64: Optional[str] = Field("", title="文件Base64地址")
    label: str = Field("", title="标签")
    ocr_s3: str = Field("", title="OCR识别结果S3地址")
    without_detection: bool = Field(False, title="不执行表格发现")


class PredictImageResponse(BaseModel):
    """表格识别."""

    predict_tables: List[TabelInfo] = Field(
        default_factory=list, title="表格识别结果(OCR)"
    )


app = FastAPI()
tts = TableTransformerStructure()
ttd = TableTransformerDetection()
table_predict = TableStructurePredict(ttd, tts, (5, 5, 5, 5))


def draw_box_without_text(image: Image.Image, tokens, fill: bool = False):
    """识别并绘制图片测试用."""
    draw = ImageDraw.Draw(image, "RGBA")
    for token in tokens:
        if fill:
            draw.rectangle(token.bbox, fill=(66, 185, 100, 64))
        else:
            draw.rectangle(token.bbox, outline="red")
    return image


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


@app.post("/predict/tables", response_model=PredictImageResponse)
async def get_ocr_tables(
    req: PredictImageRequest,
):
    """ocr识别内容填充单元格."""
    if req.url:
        image = await download_image(req.url)
    elif req.base64:
        image = await download_image(base64.b64decode(req.base64.encode()))
    else:
        raise TypeError("无效请求")

    tables = await table_predict.predict(
        image, req.ocr_s3, without_detection=req.without_detection
    )
    resp = PredictImageResponse(predict_tables=tables)
    return resp


@app.post("/predict/tables/image")
async def get_model_uplpad_(
    req: PredictImageRequest,
    mode: str = Query("table"),
):
    """请求模型推理."""
    if req.url:
        image = await download_image(req.url)
    elif req.base64:
        image = await download_image(base64.b64decode(req.base64.encode()))
    else:
        raise TypeError("无效请求")

    tables = await table_predict.predict(
        image, req.ocr_s3, without_detection=req.without_detection
    )
    if mode == "table":
        image = draw_box_without_text(image, tables)
    elif mode == "cell":
        image = draw_box_without_text(
            image, [i for table in tables for i in table.cells]
        )
    elif mode == "bbox":
        image = draw_box_without_text(
            image, [i for table in tables for i in table.bbox_cells]
        )
    else:
        raise TypeError("invaild mode")

    data_ = BytesIO()
    image.save(data_, format="png")
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
