# -*- coding: utf-8 -*-
"""
@create: 2023-05-25 01:18:26.

@author: ppolxda

@desc: 表格识别
"""

from typing import List
from typing import Optional
from typing import Tuple

from PIL import Image

from ..google_ocr import ocr_image
from .cells import objects_to_cells
from .cells import padding_table_cells_text
from .table_abc import CellSymbol
from .table_abc import TabelInfo
from .table_abc import TableDetectionBase
from .table_abc import TableStructureBase


class TableStructurePredict:
    """表格结构推理."""

    def __init__(
        self,
        detection: TableDetectionBase,
        structure: TableStructureBase,
        paddings: Optional[Tuple[int, int, int, int]] = None,
    ):
        """初始化函数."""
        if (
            not paddings
            or len(paddings) != 4
            or any(not isinstance(i, (int, float)) for i in paddings)
        ):
            raise TypeError("paddings format error")

        self.detection = detection
        self.structure = structure
        self.paddings = paddings

    async def predict(
        self,
        image: Image.Image,
        ocr_uri: Optional[str] = None,
        fix_table_boxs: bool = True,
        padding_cell: bool = True,
        download_timeout: Optional[int] = None,
        without_detection: bool = False,
    ) -> List[TabelInfo]:
        """推理表格单元格."""
        ocrdata = await ocr_image(image, ocr_uri, download_timeout)
        tables = self.predict_tables(
            image, fix_table_boxs, padding_cell, without_detection=without_detection
        )
        tables = padding_table_cells_text(ocrdata, tables)
        return tables

    def predict_tables(
        self,
        image: Image.Image,
        fix_table_boxs: bool = True,
        padding_cell: bool = True,
        without_detection: bool = False,
    ) -> List[TabelInfo]:
        """推理表格位置."""
        if without_detection:
            tables = [TabelInfo.from_image(image)]
        else:
            tables = self.predict_detection(image)
            if not tables:
                return []

        def _clip(val, _max):
            return min(max(val, 0), _max)

        for table in tables:
            table.x0 -= self.paddings[0]
            table.y0 -= self.paddings[1]
            table.x1 += self.paddings[2]
            table.y1 += self.paddings[3]

            # 避免超出范围
            table.x0 = _clip(table.x0, image.size[0])
            table.y0 = _clip(table.y0, image.size[1])
            table.x1 = _clip(table.x1, image.size[0])
            table.y1 = _clip(table.y1, image.size[1])

            crop_image = image.crop(
                (int(table.x0), int(table.y0), int(table.x1), int(table.y1))
            )

            # 推理结构
            cells = self.predict_strucrture(crop_image, padding_cell)
            if not cells:
                continue

            # 裁剪前相对坐标计算
            for cell in cells:
                cell.x0 += table.x0
                cell.y0 += table.y0
                cell.x1 += table.x0
                cell.y1 += table.y0

            # 需要根据行列数据重算单元格
            table.cells = objects_to_cells(cells)

            # 基于单元格重新计算表单
            if fix_table_boxs and table.cells:
                table.x0 = min(i.x0 for i in table.cells)
                table.y0 = min(i.y0 for i in table.cells)
                table.x1 = max(i.x1 for i in table.cells)
                table.y1 = max(i.y1 for i in table.cells)

        return [i for i in tables if i.cells]

    def predict_strucrture(
        self, image: Image.Image, padding_cell=True
    ) -> List[CellSymbol]:
        """推理表格位置.

        image: 图片对象
        tables: 表格对象 TableDetectionBase
        """
        return self.structure.predict(image, padding_cell)

    def predict_detection(self, image: Image.Image) -> List[TabelInfo]:
        """推理表格位置."""
        return self.detection.predict(image)
