# -*- coding: utf-8 -*-
"""
@create: 2023-02-03 15:04:47.

@author: name

@desc: 按文本上到下左到右合并文本格子
"""

from operator import attrgetter
from typing import List

from .schemas import WordSymbol

DEFAULT_X_TOLERANCE = 15
DEFAULT_Y_TOLERANCE = 15


def line_(datas):
    """整理换行数据."""
    index = 0
    for r in range(len(datas) - 1):
        if datas[r].y1 <= datas[r + 1].y0:
            rrr = datas[index : r + 1]
            datas[index : r + 1] = sorted(rrr, key=lambda x: x.x0)
            index = r + 1
    # 每行切片排序
    if index:
        datas[index:] = sorted(datas[index:], key=lambda x: x.x0)
    else:
        datas = sorted(datas, key=lambda x: x.x0)
    return datas


def area_(datas, x_tolerance, y_tolerance):
    """分区."""
    assert isinstance(x_tolerance, int)
    index = 0
    results = []
    for r in range(len(datas) - 1):
        # y轴分区
        if datas[r + 1].y0 - datas[r].y0 >= y_tolerance:
            results.append(datas[index : r + 1])
            index = r + 1
    if index:
        results.append(datas[index:])
    else:
        results.append(datas)
    return results


def objects_to_bbox(objects):
    """转换对象到bbox结构."""
    return (
        min(map(attrgetter("x0"), objects)),
        min(map(attrgetter("y0"), objects)),
        max(map(attrgetter("x1"), objects)),
        max(map(attrgetter("y1"), objects)),
        list(map(attrgetter("text"), objects)),
        list(objects),
    )


def recombine_(datas, label):
    """重组数据."""
    labels = []
    for r in datas:
        x0_, y0_, x1_, y1_, text_, childs = objects_to_bbox(r)
        labels.append(
            WordSymbol(
                x0=x0_,
                y0=y0_,
                x1=x1_,
                y1=y1_,
                text=" ".join(text_),
                label=label,
                iob=childs[0].iob,
            )
        )
    return labels


def merge_block_(
    words: List[WordSymbol],
    x_tolerance=DEFAULT_X_TOLERANCE,
    y_tolerance=DEFAULT_Y_TOLERANCE,
):
    """合并文本块."""
    sorted_value = sorted(words, key=lambda x: (x.y0, x.x0))
    datas = line_(sorted_value)
    results = area_(datas, x_tolerance, y_tolerance)
    labels = recombine_(results, "")
    return labels


# def merge_block_(
#     words: Iterable[WordSymbol],
#     x_tolerance=DEFAULT_X_TOLERANCE,
#     y_tolerance=DEFAULT_Y_TOLERANCE,
# ):
#     """合并文本块."""
#     assert isinstance(x_tolerance, int)

#     groups_: DefaultDict[str, List[WordSymbol]] = defaultdict(list)

#     # label分组
#     for i in words:
#         groups_[i.label].append(i)

#     labels: List[WordBoxSymbol] = []
#     for label, value in groups_.items():
#         sorted_value = sorted(value, key=lambda x: (x.y0, x.x0))

#         if len(sorted_value) == 1:
#             labels = recombine_([sorted_value], label, labels)
#         else:
#             datas = line_(sorted_value)
#             results = area_(datas, x_tolerance, y_tolerance)
#             labels = recombine_(results, label, labels)

#     return labels
