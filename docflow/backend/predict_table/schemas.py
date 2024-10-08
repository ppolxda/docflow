# -*- coding: utf-8 -*-
"""
@create: InsertDatetimeString(Ctrl+Shift+I).

@author: ppolxda

@desc: 文件功能描述
"""

from typing import List

from PIL import Image
from pydantic import BaseModel
from pydantic import Field

from ..google_ocr import WordSymbol


class WordScoresSymbol(WordSymbol):
    """表格识别评分."""

    scores: float = Field(0, title="准确度")


class CellSymbol(WordScoresSymbol):
    """表格识别."""

    label: str = ""
    type: str = "cell"
    row: int = Field(0, title="表行号")
    col: int = Field(0, title="表列号")
    row_span: int = Field(0, title="表合并号")
    col_span: int = Field(0, title="表合并号")
    is_header: bool = Field(False, title="是否是标题")


class TabelInfo(WordScoresSymbol):
    """表格识别."""

    label: str = "table"
    type: str = "table"
    rows: int = Field(0, title="行数")
    cols: int = Field(0, title="列数")
    cells: List[CellSymbol] = Field(default_factory=list, title="表格内容")
    bbox_cells: List[CellSymbol] = Field(default_factory=list, title="文本表格内容")

    @classmethod
    def from_image(cls, image: Image.Image):
        """基于图片尺寸创建表格对象."""
        return TabelInfo(
            scores=0,
            label="table",
            type="table",
            rows=0,
            cols=0,
            cells=[],
            x0=0,
            y0=0,
            x1=image.width,
            y1=image.height,
            text="",
            iob="",
        )


class TablePredictData(BaseModel):
    """表格识别."""

    predict_tables: List[TabelInfo] = Field(
        default_factory=list, title="表格识别结果(OCR)"
    )
