# -*- coding: utf-8 -*-
"""
@create: 2022-07-22 17:48:08.

@author: name

@desc: Base Model
"""

from typing import List

from docflow.schemas import BaseModel
from docflow.schemas import Field


class WordSymbol(BaseModel):
    """WordSymbol."""

    x0: float = 0.00
    y0: float = 0.00
    x1: float = 0.00
    y1: float = 0.00
    text: str = ""
    label: str = ""
    iob: str = ""
    type: str = "field"

    @property
    def top(self):
        """Center x."""
        return self.y0

    @property
    def bottom(self):
        """Center x."""
        return self.y1

    @property
    def center_x(self):
        """Center x."""
        return int((self.x0 + self.x1) / 2)

    @property
    def center_y(self):
        """Center y."""
        return int((self.y0 + self.y1) / 2)

    @property
    def bbox(self):
        """Center y."""
        return (self.x0, self.y0, self.x1, self.y1)

    @property
    def width(self):
        """Center y."""
        return self.x1 - self.x0

    @property
    def height(self):
        """Center y."""
        return self.y1 - self.y0

    @property
    def coco_bbox(self):
        """Coco Point - x, y, width, height."""
        return [self.x0, self.y0, self.width, self.height]

    def __hash__(self):
        """hash."""
        return hash((type(self),) + tuple(self.__dict__.values()))


class WordBoxSymbol(WordSymbol):
    """MergeWord."""

    childs: List[WordSymbol] = Field(default_factory=list, title="OCR识别结果")
