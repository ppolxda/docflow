# -*- coding: utf-8 -*-
"""
@create: 2023-06-09 03:45:49.

@author: ppolxda

@desc: 文件功能描述
"""
from typing import List
from typing import TypeVar

from fitz import Rect  # pylint: disable=import-error

from ..schemas import CellSymbol
from ..schemas import WordScoresSymbol

T = TypeVar("T", bound=WordScoresSymbol)  # Declare type variable


def sort_objects_by_score(objects: List[T], reverse=True):
    """Put any set of objects in order from high score to low score."""
    if reverse:
        sign = -1
    else:
        sign = 1

    return sorted(objects, key=lambda k: sign * k.scores)


def sort_objects_left_to_right(objs: List[T]):
    """Put the objects in order from left to right."""
    return sorted(objs, key=lambda k: k.x0 + k.x1)


def sort_objects_top_to_bottom(objs: List[T]):
    """Put the objects in order from top to bottom."""
    return sorted(objs, key=lambda k: k.y0 + k.y1)


def nms(
    objects: List[T],
    match_criteria="object2_overlap",
    match_threshold=0.05,
    keep_higher=True,
):
    """Customizable version of non-maxima suppression (NMS).

    使用最高评分的元素排序，过滤掉重叠元素

    Default behavior: If a lower-confidence object overlaps more than 5% of its area
    with a higher-confidence object, remove the lower-confidence object.

    objects: set of dicts; each object dict must have a 'bbox' and a 'score' field
    match_criteria: how to measure how much two objects "overlap"
    match_threshold: the cutoff for determining that overlap requires suppression of one object
    keep_higher: if True, keep the object with the higher metric; otherwise, keep the lower
    """
    if len(objects) == 0:
        return []

    objects = sort_objects_by_score(objects, reverse=keep_higher)

    num_objects = len(objects)
    suppression = [False for obj in objects]

    for object2_num in range(1, num_objects):
        object2_rect = Rect(objects[object2_num].bbox)
        object2_area = object2_rect.get_area()  # type: ignore
        for object1_num in range(object2_num):
            if not suppression[object1_num]:
                object1_rect = Rect(objects[object1_num].bbox)
                object1_area = object1_rect.get_area()  # type: ignore
                intersect_area = object1_rect.intersect(object2_rect).get_area()  # type: ignore
                try:
                    if match_criteria == "object1_overlap":
                        metric = intersect_area / object1_area
                    elif match_criteria == "object2_overlap":
                        metric = intersect_area / object2_area
                    elif match_criteria == "iou":
                        metric = intersect_area / (
                            object1_area + object2_area - intersect_area
                        )
                    else:
                        raise TypeError("match_criteria invaild")

                    if metric >= match_threshold:
                        suppression[object2_num] = True
                        break
                except Exception:
                    # Intended to recover from divide-by-zero
                    pass

    return [obj for idx, obj in enumerate(objects) if not suppression[idx]]


def padding_columns(
    columns: List[CellSymbol],
    threshold_x: int = 10,
    match_threshold: float = 0.25,
    padding_side: str = "right",
):
    """对齐表格列."""
    columns = nms(
        columns,
        match_criteria="object2_overlap",
        match_threshold=match_threshold,
        keep_higher=True,
    )
    if len(columns) <= 1:
        return columns

    columns.sort(key=lambda x: x.x0)
    y_min = min(columns, key=lambda x: x.y0)
    y_max = max(columns, key=lambda x: x.y1)
    columns[-1].y0 = y_min.y0
    columns[-1].y1 = y_max.y1

    for index, column in enumerate(columns[:-1]):
        column.y0 = y_min.y0
        column.y1 = y_max.y1

        # 如果单元格有重叠，采取缩进模式
        # 如果间距过小，采取对齐策略，如果间距超出范围采取填充处理
        spacing = abs(column.x1 - columns[index + 1].x0)
        if columns[index + 1].x0 < column.x1 or spacing < threshold_x:
            if padding_side == "right":
                columns[index + 1].x0 = column.x1
            elif padding_side == "left":
                column.x1 = columns[index + 1].x0
            else:
                raise TypeError("padding_side invaild")
            continue

        columns.append(
            CellSymbol(
                scores=0,
                label="table column",
                type="cell",
                row=0,
                row_span=0,
                col=0,
                col_span=0,
                x0=column.x1,
                y0=y_min.y0,
                x1=columns[index + 1].x0,
                y1=y_max.y1,
                text="",
                iob="",
                is_header=False,
            )
        )

    return columns


def padding_rows(
    rows: List[CellSymbol],
    threshold_x: int = 15,
    match_threshold: float = 0.3,
    padding_side: str = "right",
    is_header=False,
):
    """对齐表格列."""
    # columns = sorted(columns, key=lambda x: x.x0)
    rows = nms(
        rows,
        match_criteria="object2_overlap",
        match_threshold=match_threshold,
        keep_higher=True,
    )
    if len(rows) <= 1:
        return rows

    rows.sort(key=lambda x: x.y1)
    x_min = min(rows, key=lambda x: x.x0)
    x_max = max(rows, key=lambda x: x.x1)
    rows[-1].x0 = x_min.x0
    rows[-1].x1 = x_max.x1

    for index, row in enumerate(rows[:-1]):
        row.x0 = x_min.x0
        row.x1 = x_max.x1

        # 如果单元格有重叠，采取缩进模式
        # 如果间距过小，采取对齐策略，如果间距超出范围采取填充处理
        spacing = abs(row.y1 - rows[index + 1].y0)
        if rows[index + 1].y0 < row.y1 or spacing < threshold_x:
            if padding_side == "right":
                rows[index + 1].y0 = row.y1
            elif padding_side == "left":
                row.y1 = rows[index + 1].y0
            else:
                raise TypeError("padding_side invaild")
            continue

        rows.append(
            CellSymbol(
                scores=0,
                label="table column header" if is_header else "table row",
                type="cell",
                row=0,
                row_span=0,
                col=0,
                col_span=0,
                x0=x_min.x0,
                y0=row.y1,
                x1=x_max.x1,
                y1=rows[index + 1].y0,
                text="",
                iob="",
                is_header=False,
            )
        )

    return rows
