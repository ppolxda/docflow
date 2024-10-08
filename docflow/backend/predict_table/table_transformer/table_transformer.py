# -*- coding: utf-8 -*-
"""
@create: 2023-05-06 06:23:40.

@author: ppolxda

@desc: 表格识别
"""

from typing import List
from typing import Optional

import torch
from PIL import Image
from transformers import AutoImageProcessor
from transformers import AutoModelForObjectDetection

from ...predict_utils import find_registry_path
from ...settings import settings
from ..schemas import CellSymbol
from ..schemas import TabelInfo
from ..table_abc import TableDetectionBase
from ..table_abc import TableStructureBase
from .table_process import nms
from .table_process import padding_columns
from .table_process import padding_rows

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # type: ignore # pylint: disable=no-member


class TableTransformerBase(object):
    """表格基类."""

    def __init__(self, module_path):
        """初始化函数."""
        self.model_path = find_registry_path(module_path)
        self.image_processor = AutoImageProcessor.from_pretrained(self.model_path)
        self.model = AutoModelForObjectDetection.from_pretrained(self.model_path).to(
            device
        )

    def _predict(self, image: Image.Image):
        inputs = self.image_processor(images=image, return_tensors="pt")
        outputs = self.model(**inputs.to(device))  # type: ignore

        # convert outputs (bounding boxes and class logits) to COCO API
        target_sizes = [image.size[::-1]]
        results_ = self.image_processor.post_process_object_detection(
            outputs, threshold=0.6, target_sizes=target_sizes
        )
        for results in results_:
            for score, label, box in zip(  # type: ignore
                results["scores"], results["labels"], results["boxes"]
            ):
                label_ = self.model.config.id2label[label.item()]  # type: ignore
                yield score, label_, box


class TableTransformerDetection(TableTransformerBase, TableDetectionBase):
    """表格发现."""

    def __init__(self, module_path: Optional[str] = None):
        """初始化函数."""
        if module_path is None:
            module_path = (
                settings.TABLE_DETECTION_MODULE
                if settings.TABLE_DETECTION_MODULE
                else "microsoft/table-transformer-detection"
            )

        super().__init__(module_path)

    def predict(self, image: Image.Image) -> List[TabelInfo]:
        """推理表格位置."""
        rrr = []
        for score, __, box in self._predict(image):
            box = [round(i, 2) for i in box.tolist()]
            rrr.append(
                TabelInfo(
                    scores=score,
                    label="table",
                    type="table",
                    rows=0,
                    cols=0,
                    cells=[],
                    x0=box[0],
                    y0=box[1],
                    x1=box[2],
                    y1=box[3],
                    text="",
                    iob="",
                )
            )

        tables = nms(
            rrr,
            match_criteria="object2_overlap",
            match_threshold=0.5,
            keep_higher=True,
        )
        # assert len(tables) == len(rrr)
        return tables


class TableTransformerStructure(TableTransformerBase, TableStructureBase):
    """表格结构解析."""

    def __init__(self, module_path: Optional[str] = None):
        """初始化函数."""
        if module_path is None:
            module_path = (
                settings.TABLE_STRUCTURE_MODULE
                if settings.TABLE_STRUCTURE_MODULE
                else "microsoft/table-transformer-structure-recognition"
            )

        super().__init__(module_path)

    def predict(self, image: Image.Image, padding_cell=True) -> List[CellSymbol]:
        """推理表格位置."""
        cells: List[CellSymbol] = []
        for score, label, box in self._predict(image):
            if label == "table":
                continue

            box = [round(i, 2) for i in box.tolist()]
            cells.append(
                CellSymbol(
                    scores=score,
                    label=label,
                    type="cell",
                    row=0,
                    row_span=0,
                    col=0,
                    col_span=0,
                    x0=box[0],
                    y0=box[1],
                    x1=box[2],
                    y1=box[3],
                    text="",
                    iob="",
                    is_header=False,
                )
            )

        # 过滤暂时需要的字段
        rows = [i for i in cells if i.label == "table row"]
        columns = [i for i in cells if i.label == "table column"]
        headers = [i for i in cells if i.label == "table column header"]

        # 后处理单元格
        if padding_cell:
            rows = padding_rows(rows)
            headers = padding_rows(headers, is_header=True)
            columns = padding_columns(columns)

        return columns + rows + headers
