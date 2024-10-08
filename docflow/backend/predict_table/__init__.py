# -*- coding: utf-8 -*-
"""
@create: 2023-05-06 06:39:17.

@author: ppolxda

@desc: 表格识别工厂
"""

from enum import Enum

from .table_transformer import TableTransformerStructure


class EnumTableStructure(str, Enum):
    """表格识别枚举."""

    TABLE_TRANSFORMER = "TABLE_TRANSFORMER"


def table_structure_factory(mode: EnumTableStructure, *args, **kwargs):
    """表格识别工厂."""
    if mode == EnumTableStructure.TABLE_TRANSFORMER:
        return TableTransformerStructure(*args, **kwargs)
    else:
        raise TypeError("mode invaild")
