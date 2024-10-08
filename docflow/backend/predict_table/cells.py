# -*- coding: utf-8 -*-
"""
@create: 2023-05-25 01:18:26.

@author: ppolxda

@desc: 表格识别

TAG: https://github.com/microsoft/table-transformer/tree/main
"""

from copy import deepcopy
from typing import List

from fitz import Rect

from .merge_v3 import merge_block_
from .schemas import TabelInfo
from .schemas import WordSymbol
from .table_abc import CellSymbol


def sort_objects_y0(objs):
    """Put any set of objects in order from high score to low score."""
    return sorted(objs, key=lambda k: k.y0)


def sort_objects_x0(objs):
    """Put the objects in order from left to right."""
    return sorted(objs, key=lambda k: k.x0)


def align_columns(columns, bbox):
    """For every column, align the top and bottom boundaries to the final table bounding box."""
    for column in columns:
        column.y0 = bbox[1]
        column.y1 = bbox[3]
    return columns


def align_rows(rows, bbox):
    """For every row, align the left and right boundaries to the final table bounding box."""
    for row in rows:
        row.x0 = bbox[0]
        row.x1 = bbox[2]
    return rows


def objects_to_cells(cells: List[CellSymbol]) -> List[CellSymbol]:
    """单元格解析."""
    # TODO - 输出结果存在重叠方框，需要尝试NMS
    columns = [obj for obj in cells if obj.label == "table column"]
    rows = [obj for obj in cells if obj.label == "table row"]
    # headers = [obj for obj in cells if obj.label == "table column header"]

    rows = sort_objects_y0(rows)
    columns = sort_objects_x0(columns)

    row_rect, column_rect = Rect(), Rect()
    for row in rows:
        row_rect.include_rect((row.x0, row.y0, row.x1, row.y1))

    for col in columns:
        column_rect.include_rect((col.x0, col.y0, col.x1, col.y1))

    bbox = [column_rect[0], row_rect[1], column_rect[2], row_rect[3]]
    columns_ = align_columns(columns, bbox)
    rows_ = align_rows(rows, bbox)

    cells = []
    for col_number, col in enumerate(columns_):
        for row_number, row in enumerate(rows_):
            column_rect = Rect([col.x0, col.y0, col.x1, col.y1])
            row_rect = Rect([row.x0, row.y0, row.x1, row.y1])
            cell_rect = row_rect.intersect(column_rect)

            # 过滤不正确的格子
            if not (cell_rect[0] <= cell_rect[2] and cell_rect[1] <= cell_rect[3]):
                continue

            cells.append(
                CellSymbol(
                    scores=(col.scores + row.scores) / 2,
                    label="",
                    type="cell",
                    row=row_number + 1,
                    row_span=0,
                    col=col_number + 1,
                    col_span=0,
                    x0=cell_rect[0],
                    y0=cell_rect[1],
                    x1=cell_rect[2],
                    y1=cell_rect[3],
                    text="",
                    iob="",
                    is_header=False,
                )
            )
    return cells


def sort_objects_cells(cells: List[CellSymbol], max_row: int) -> List[CellSymbol]:
    """重新排列row/col."""
    cells.sort(key=lambda x: (x.x0, x.y0))

    for i in range(0, len(cells), max_row):
        col = 0
        row = 1
        for cell in cells[i : i + max_row]:
            cell.row = row
            cell.col = i // max_row + 1
            col += 1
            row += 1
    return cells


def padding_table_cells_text(
    words: List[WordSymbol], tables: List[TabelInfo]
) -> List[TabelInfo]:
    """ocr识别内容填充到单元格."""
    for table in tables:
        bboxs = []
        for cell in table.cells:
            combits = [
                word
                for word in words
                if cell.x0 <= word.center_x <= cell.x1
                and cell.y0 <= word.center_y <= cell.y1
            ]

            bbox = deepcopy(cell)

            if combits:
                combits = merge_block_(combits)
                cell.text = " ".join([combit.text for combit in combits])
                bbox.x0 = min(combit.x0 for combit in combits)
                bbox.y0 = min(combit.y0 for combit in combits)
                bbox.x1 = max(combit.x1 for combit in combits)
                bbox.y1 = max(combit.y1 for combit in combits)
                bbox.text = cell.text
                bboxs.append(bbox)
            else:
                bboxs.append(bbox)

        table.bbox_cells = bboxs
    return tables
