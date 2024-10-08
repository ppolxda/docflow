# -*- coding: utf-8 -*-
"""
@create: 2023-02-03 15:04:47.

@author: name

@desc: 按文本上到下左到右合并文本格子
"""

import itertools
from collections import defaultdict
from copy import deepcopy
from operator import attrgetter
from operator import itemgetter
from typing import Callable
from typing import Iterator
from typing import List
from typing import Union

from .ocrs.schemas import WordBoxSymbol
from .ocrs.schemas import WordSymbol

DEFAULT_CHUNK = 2300
LINE_X_TOLERANCE = 38
LINE_Y_TOLERANCE = 8
LEFT_X_TOLERANCE = 10
LEFT_Y_TOLERANCE = 28
CENTER_X_TOLERANCE = 15
CENTER_Y_TOLERANCE = 20
RIGHT_X_TOLERANCE = 10
RIGHT_Y_TOLERANCE = 28


def create_block_bboxs(bboxs: List[WordSymbol]):
    """创建文本块."""
    assert bboxs
    return WordBoxSymbol(
        x0=float(min(i.x0 for i in bboxs)),
        x1=float(max(i.x1 for i in bboxs)),
        y0=float(min(i.y0 for i in bboxs)),
        y1=float(max(i.y1 for i in bboxs)),
        text="",
        label=bboxs[0].label,  # type: ignore
        childs=bboxs,
    )


def normalize_bbox(target_size, src_size, bbox):
    """normalize_bbox."""
    return [
        int(target_size[0] * bbox[0] / src_size[0]),
        int(target_size[1] * bbox[1] / src_size[1]),
        int(target_size[0] * bbox[2] / src_size[0]),
        int(target_size[1] * bbox[3] / src_size[1]),
    ]


def unnormalize_bbox(target_size, src_size, bbox):
    """unnormalize_bbox."""
    return normalize_bbox(src_size, target_size, bbox)


def normalize_word(target_size, src_size, bbox: WordSymbol):
    """normalize_bbox."""
    bbox_ = normalize_bbox(target_size, src_size, bbox.bbox)
    bbox.x0, bbox.y0, bbox.x1, bbox.y1 = bbox_
    return bbox


def unnormalize_word(target_size, src_size, bbox: WordSymbol):
    """normalize_bbox."""
    bbox_ = unnormalize_bbox(target_size, src_size, bbox.bbox)
    bbox.x0, bbox.y0, bbox.x1, bbox.y1 = bbox_
    return bbox


def cluster_list(xs, tolerance: int):
    """按间距分组."""
    if tolerance == 0 or len(xs) < 2:
        return [[x] for x in sorted(xs)]

    groups = []
    xs = list(sorted(xs))
    current_group = [xs[0]]  # type: ignore
    last = xs[0]  # type: ignore

    for x in xs[1:]:
        x_ = x
        assert isinstance(x_, (float, int)) and isinstance(tolerance, int)
        if x_ <= (last + tolerance):
            current_group.append(x)
        else:
            groups.append(current_group)
            current_group = [x]

        last = x_

    groups.append(current_group)
    return groups


def make_cluster_dict(values: Iterator[float], tolerance: int):
    """创建按间距分组字典."""
    clusters = cluster_list(set(values), tolerance)

    nested_tuples = [
        [(val, i) for val in value_cluster] for i, value_cluster in enumerate(clusters)
    ]

    cluster_dict = dict(itertools.chain(*nested_tuples))
    return cluster_dict


def cluster_objects(
    objs: List[WordSymbol], attr: Union[str, Callable[[object], WordSymbol]], tolerance
):
    """创建按间距分组字典."""
    if isinstance(attr, str):
        attr_getter = attrgetter(attr)
    else:
        attr_getter = attr

    values = map(attr_getter, objs)
    cluster_dict = make_cluster_dict(values, tolerance)

    get_0, get_1 = itemgetter(0), itemgetter(1)

    cluster_tuples = sorted(
        ((obj, cluster_dict.get(attr_getter(obj))) for obj in objs), key=get_1
    )

    grouped = itertools.groupby(cluster_tuples, key=get_1)
    clusters = [list(map(get_0, v)) for k, v in grouped]
    return clusters


def _loop_bbox(bboxs_: Union[List[WordBoxSymbol], List[WordSymbol]]):
    for i in bboxs_:
        if isinstance(i, WordBoxSymbol):
            for j in i.childs:
                yield j
        else:
            yield i


def _is_new_horizontal_block(
    lines: List[WordSymbol], bbox: WordSymbol, x_tolerance: int
):
    """是否超出水平间距，作为新块处理."""
    if x_tolerance <= 0:
        return True

    last = lines[-1]  # type: ignore
    return abs(bbox.x0 - last.x1) > x_tolerance


def get_iou(bbox_x: WordSymbol, bbox_y: WordSymbol):
    """计算两个方框的重叠面积."""
    assert bbox_x.x0 < bbox_x.x1
    assert bbox_x.y0 < bbox_x.y1
    assert bbox_y.x0 < bbox_y.x1
    assert bbox_y.y0 < bbox_y.y1

    # determine the coordinates of the intersection rectangle
    x_left = max(bbox_x.x0, bbox_y.x0)
    y_top = max(bbox_x.y0, bbox_y.y0)
    x_right = min(bbox_x.x1, bbox_y.x1)
    y_bottom = min(bbox_x.y1, bbox_y.y1)

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    # The intersection of two axis-aligned bounding boxes is always an
    # axis-aligned bounding box
    intersection_area = (x_right - x_left) * (y_bottom - y_top)

    # compute the area of both AABBs
    bbox1_area = (bbox_x.x1 - bbox_x.x0) * (bbox_x.y1 - bbox_x.y0)
    bbox2_area = (bbox_y.x1 - bbox_y.x0) * (bbox_y.y1 - bbox_y.y0)
    union_area = bbox1_area + bbox2_area - intersection_area

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = intersection_area / union_area
    assert iou >= 0.0 and iou <= 1.0
    return iou


def _is_all_overlap_block(bbox_x: WordSymbol, bbox_y: WordSymbol):
    """是否包括文块."""
    return (
        bbox_x.x0 <= bbox_y.x0
        and bbox_x.y0 <= bbox_y.y0
        and bbox_x.x1 >= bbox_y.x1
        and bbox_x.y1 >= bbox_y.y1
    )


def _is_overlap_block(bbox_x: WordSymbol, bbox_y: WordSymbol):
    """是否包括文块."""
    # 是否完全包含
    if _is_all_overlap_block(bbox_x, bbox_y):
        return True

    # 检查重叠区域比例
    return get_iou(bbox_x, bbox_y) > 0.8


def _is_new_vertical_block(lines: List[WordSymbol], bbox: WordSymbol, y_tolerance: int):
    """是否超出垂直间距，作为新块处理."""
    if y_tolerance <= 0:
        return True

    last = lines[-1]  # type: ignore
    return abs(bbox.y0 - last.y1) > y_tolerance


def iter_split_block_group(
    boxes: List[WordSymbol],
    tolerance: int,
    mode="horizontal",
):
    """按列位置执行垂直方向分组分组."""
    if mode == "horizontal":
        sort_func = attrgetter("center_x")
        split_func = _is_new_horizontal_block
    elif mode == "vertical":
        sort_func = attrgetter("y0")
        split_func = _is_new_vertical_block
    else:
        raise TypeError("mode invaild")

    current_line = []
    for bbox in sorted(boxes, key=sort_func):
        # 检查是否起了一行
        if current_line and split_func(current_line, bbox, tolerance):
            yield create_block_bboxs([i for i in _loop_bbox(current_line)])
            current_line = [bbox]
        else:
            current_line.append(bbox)

    if current_line:
        yield create_block_bboxs([i for i in _loop_bbox(current_line)])


def merge_lines_group(
    boxes: Union[List[WordBoxSymbol], List[WordSymbol]],
    x_tolerance: int,
    y_tolerance: int,
):
    """行合并."""
    assert boxes and x_tolerance >= 0 and y_tolerance >= 0
    block_groups = []

    # 使用y1作为对齐条件，大部分文件底边对齐，包含符号字符
    for line_group in cluster_objects(list(boxes), "y1", y_tolerance):
        for block_group in iter_split_block_group(
            line_group, x_tolerance, "horizontal"
        ):
            block_groups.append(block_group)

    return block_groups


def merge_aligned_group(
    boxes: List[WordBoxSymbol], x_tolerance: int, y_tolerance: int, aligned_with="left"
):
    """左对齐合并."""
    assert boxes and x_tolerance >= 0 and y_tolerance >= 0

    # 方便代码阅读，翻译枚举
    if aligned_with == "left":
        aligned_with = "x0"
    elif aligned_with == "right":
        aligned_with = "x1"
    elif aligned_with == "center":
        aligned_with = "center_x"
    else:
        raise TypeError("aligned_with invaild")

    block_groups = []

    for columns_group in cluster_objects(list(boxes), aligned_with, x_tolerance):
        for block_group in iter_split_block_group(
            columns_group, y_tolerance, "vertical"
        ):
            block_groups.append(block_group)

    return block_groups


def merge_overlap_group(boxes: List[WordBoxSymbol]):
    """递归检查合并包含块."""
    for x, y in itertools.combinations(boxes, 2):
        if not (_is_overlap_block(x, y) or _is_overlap_block(y, x)):
            continue

        boxes.remove(x)
        boxes.remove(y)

        merge = create_block_bboxs(x.childs + y.childs)
        return merge_overlap_group([merge] + boxes)

    return boxes


def merge_block_text(boxes: List[WordBoxSymbol], y_tolerance: int):
    """递归检查合并包含块."""
    bboxes_ = []
    for bbox in boxes:
        # 同行合并
        lines = []
        for line_group in cluster_objects(list(bbox.childs), "y1", y_tolerance):
            line = create_block_bboxs(sorted(line_group, key=lambda x: x.center_x))
            line.text = " ".join(i.text for i in line.childs)
            lines.append(line)

        # 不同行合并列
        bbox_ = create_block_bboxs(sorted(lines, key=lambda x: x.center_y))
        bbox_.text = "\n".join(i.text for i in bbox_.childs)
        bbox_.childs = [j for i in bbox_.childs for j in i.childs]  # type: ignore
        bboxes_.append(bbox_)

    return bboxes_


def merge_block(words: List[WordBoxSymbol], width: int, height: int):
    """合并文本块."""
    target_long_side = DEFAULT_CHUNK
    image_size = (width, height)
    long_side = max(height, width)

    # 计算缩放比例
    scale = target_long_side / long_side
    if long_side == height:
        target_size = (int(width * scale), target_long_side)
    else:
        target_size = (target_long_side, int(height * scale))

    # 序列化到指定宽度
    words_ = deepcopy(words)
    words_iter = map(lambda x: normalize_word(target_size, image_size, x), words_)

    # 按标签分组
    words_label = defaultdict(list)
    for i in words_iter:
        words_label[i.label].append(i)

    # 合并文本块
    block_map = map(merge_block_, words_label.values())

    # 反序列化宽度
    block = [unnormalize_word(target_size, image_size, x) for i in block_map for x in i]
    return block


def merge_block_(words: List[WordSymbol]):
    """合并文本块."""
    # 行合并，相邻模块合并
    line_x_tolerance = LINE_X_TOLERANCE
    line_y_tolerance = LINE_Y_TOLERANCE
    block_groups = merge_lines_group(words, line_x_tolerance, line_y_tolerance)
    # return block_groups

    # 左对齐合并
    left_x_tolerance = LEFT_X_TOLERANCE
    left_y_tolerance = LEFT_Y_TOLERANCE
    left_block_groups = merge_aligned_group(
        block_groups, left_x_tolerance, left_y_tolerance, "left"
    )
    # return left_block_groups

    # 居中对齐合并
    center_x_tolerance = CENTER_X_TOLERANCE
    center_y_tolerance = CENTER_Y_TOLERANCE
    center_block_groups = merge_aligned_group(
        left_block_groups, center_y_tolerance, center_x_tolerance, "center"
    )
    # return center_block_groups

    # 右对齐合并
    right_x_tolerance = RIGHT_X_TOLERANCE
    right_y_tolerance = RIGHT_Y_TOLERANCE
    right_block_groups = merge_aligned_group(
        center_block_groups, right_y_tolerance, right_x_tolerance, "right"
    )
    # return right_block_groups

    # 包含合并
    contain_block_groups = merge_overlap_group(right_block_groups)
    # return contain_block_groups

    # 包含合并
    block_texts = merge_block_text(contain_block_groups, line_y_tolerance)
    return block_texts
