# -*- coding: utf-8 -*-
"""
@create: 2023-05-06 06:39:43.

@author: ppolxda

@desc: 文件功能描述
"""

from abc import ABC
from abc import abstractmethod
from typing import List

from PIL import Image

from .schemas import CellSymbol
from .schemas import TabelInfo


class TableDetectionBase(ABC):
    """表格发现抽线类."""

    @abstractmethod
    def predict(self, image: Image.Image) -> List[TabelInfo]:
        """推理表格位置."""
        raise NotImplementedError


class TableStructureBase(ABC):
    """表格结构识别抽线类."""

    @abstractmethod
    def predict(self, image: Image.Image, padding_cell=True) -> List[CellSymbol]:
        """推理表格位置.

        image: 图片对象
        tables: 表格对象 TableDetectionBase
        """
        raise NotImplementedError
