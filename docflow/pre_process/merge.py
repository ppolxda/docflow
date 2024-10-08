# -*- coding: utf-8 -*-
"""
@create: 2023-01-06 14:14:59.

@author: name

@desc: 文件功能描述

元素倾斜度不大的前提下,按Y轴越小优先(误差一定容差内认为等高), 按X轴越小优先
在等高前提下寻找最接近自己的右手边元素进行文段合并
"""

import itertools
import numbers
from collections import defaultdict
from decimal import ROUND_HALF_UP
from decimal import Decimal
from operator import attrgetter
from operator import itemgetter
from typing import Iterable
from typing import List

from .ocrs.schemas import WordBoxSymbol
from .ocrs.schemas import WordSymbol

DEFAULT_X_TOLERANCE = 3
DEFAULT_Y_TOLERANCE = 3

DEFAULT_WORD_EXTRACTION_SETTINGS = dict(
    x_tolerance=DEFAULT_X_TOLERANCE,
    y_tolerance=DEFAULT_Y_TOLERANCE,
    keep_blank_chars=False,
    use_text_flow=False,
    horizontal_ltr=True,  # Should words be read left-to-right?
    vertical_ttb=True,  # Should vertical words be read top-to-bottom?
    extra_attrs=[],
)


def is_dataframe(collection):
    """检查是否是pandas DataFrame."""
    cls = collection.__class__
    name = ".".join([cls.__module__, cls.__name__])
    return name == "pandas.core.frame.DataFrame"


def to_list(collection):
    """转换为列表."""
    if is_dataframe(collection):
        return collection.to_dict("records")  # pragma: nocover
    else:
        return list(collection)


def _decimalize(v, q=None):
    """转换为固定精度对象."""
    # Convert int-like
    if isinstance(v, numbers.Integral):
        return Decimal(int(v))

    # Convert float-like
    elif isinstance(v, numbers.Real):
        if q is not None:
            return Decimal(repr(v)).quantize(Decimal(repr(q)), rounding=ROUND_HALF_UP)
        else:
            return Decimal(repr(v))
    else:
        raise ValueError(f"Cannot convert {v} to Decimal.")


def decimalize(v, q=None):
    """转换为固定精度对象."""
    # If already a decimal, just return itself
    if isinstance(v, Decimal):
        return v

    # If tuple/list passed, bulk-convert
    if isinstance(v, (tuple, list)):
        return type(v)(decimalize(x, q) for x in v)
    else:
        return _decimalize(v, q)


def cluster_list(xs, tolerance):
    """按间距分组."""
    tolerance = decimalize(tolerance)
    if tolerance == Decimal(0):
        return [[x] for x in sorted(xs)]
    if len(xs) < 2:
        return [[x] for x in sorted(xs)]
    groups = []
    xs = list(sorted(xs))
    current_group = [xs[0]]
    last = _decimalize(xs[0])
    for x in xs[1:]:
        x_ = _decimalize(x)
        assert isinstance(x_, Decimal) and isinstance(tolerance, Decimal)
        if x_ <= (last + tolerance):
            current_group.append(x)
        else:
            groups.append(current_group)
            current_group = [x]
        last = x_
    groups.append(current_group)
    return groups


def make_cluster_dict(values, tolerance):
    """创建按间距分组字典."""
    tolerance = decimalize(tolerance)
    clusters = cluster_list(set(values), tolerance)

    nested_tuples = [
        [(val, i) for val in value_cluster] for i, value_cluster in enumerate(clusters)
    ]

    cluster_dict = dict(itertools.chain(*nested_tuples))
    return cluster_dict


def cluster_objects(objs, attr, tolerance):
    """创建按间距分组字典."""
    if isinstance(attr, str):
        attr_getter = attrgetter(attr)
    else:
        attr_getter = attr

    objs = to_list(objs)
    values = map(attr_getter, objs)
    cluster_dict = make_cluster_dict(values, tolerance)

    get_0, get_1 = itemgetter(0), itemgetter(1)

    cluster_tuples = sorted(
        ((obj, cluster_dict.get(attr_getter(obj))) for obj in objs), key=get_1
    )

    grouped = itertools.groupby(cluster_tuples, key=get_1)

    clusters = [list(map(get_0, v)) for k, v in grouped]

    return clusters


def is_text_in_table(table: WordSymbol, word: WordSymbol):
    """中心点包含在方格内，代表文本在表格内."""
    x = (word.x0 + word.x1) / 2
    y = (word.top + word.bottom) / 2
    return table.top <= y and table.bottom >= y and table.x0 <= x and table.x1 >= x


def inside_bbox(bbox: WordSymbol, objs: List[WordSymbol]) -> List[WordSymbol]:
    """中心点包含在方格内，代表文本在表格内."""
    matching = [obj for obj in objs if is_text_in_table(bbox, obj)]
    return matching


# class MerageExtractor(object):
#     def iter_sort_words(self, words: List[WordSymbol]) -> List[WordSymbol]:
#         return words


def objects_to_bbox(objects):
    """转换对象到bbox结构."""
    return (
        min(map(attrgetter("x0"), objects)),
        min(map(attrgetter("top"), objects)),
        max(map(attrgetter("x1"), objects)),
        max(map(attrgetter("bottom"), objects)),
        list(map(attrgetter("text"), objects)),
        list(set(filter(lambda x: x.strip(), map(attrgetter("label"), objects)))),
        "B" if "B" in list(map(attrgetter("iob"), objects)) else "I",
    )


def merge_boxs(ordered_chars: List[WordSymbol]):
    """合并格子."""
    # labels 格式可能会出错
    x0, top, x1, bottom, words, labels, iob = objects_to_bbox(ordered_chars)
    word = WordBoxSymbol(
        **{
            "label": ",".join(labels),
            "text": " ".join(words),
            "x0": x0,
            "x1": x1,
            "y0": top,
            "y1": bottom,
            "iob": iob,
            "childs": ordered_chars,
        }
    )
    return word


class LineExtractor(object):
    """LineExtractor."""

    def __init__(self, **settings):
        """构造函数."""
        self.x_tolerance = max(settings.get("x_tolerance", DEFAULT_X_TOLERANCE), 0)
        self.y_tolerance = max(settings.get("y_tolerance", DEFAULT_Y_TOLERANCE), 0)
        self.keep_blank_chars = settings.get("keep_blank_chars", False)
        self.use_text_flow = settings.get("use_text_flow", False)
        self.horizontal_ltr = settings.get("horizontal_ltr", True)
        self.vertical_ttb = settings.get("vertical_ttb", True)
        self.extra_attrs = settings.get("extra_attrs", [])

    def merge_lines(self, ordered_chars: List[WordSymbol]):
        """合并行."""
        return merge_boxs(ordered_chars)

    def word_begins_new_line(
        self, current_words: List[WordSymbol], next_word: WordSymbol
    ):
        """word_begins_new_line."""
        if self.x_tolerance <= 0 or next_word.iob == "B":
            return True

        # 重算合并后的方格大小
        (
            word_x0,
            _,
            word_x1,
            _,
            _,
            _,
            _,
        ) = objects_to_bbox(current_words)

        # 如果是左右相邻，两高度偏差不大
        # 或者坐标完全包含
        # Y轴已根据容错值分组，这边只判断横轴
        return not (
            (
                abs(next_word.x0 - word_x1) < self.x_tolerance
                # and abs(next_word.top - word_top) < self.y_tolerance
            )
            or (
                abs(next_word.x1 - word_x0) < self.x_tolerance
                # and abs(next_word.top - word_top) < self.y_tolerance
            )
        )

    def word_begins_new_box(
        self, current_words: List[WordSymbol], next_word: WordSymbol
    ):
        """word_begins_new_line."""
        if self.x_tolerance <= 0 or next_word.iob == "B":
            return True

        # 重算合并后的方格大小
        (
            word_x0,
            _,
            word_x1,
            _,
            _,
            _,
            _,
        ) = objects_to_bbox(current_words)

        # 如果是左右相邻，两高度偏差不大
        # 或者坐标完全包含
        # Y轴已根据容错值分组，这边只判断横轴
        return not (
            (
                abs(next_word.x0 - word_x1) < self.x_tolerance
                # and abs(next_word.top - word_top) < self.y_tolerance
            )
            or (
                abs(next_word.x1 - word_x0) < self.x_tolerance
                # and abs(next_word.top - word_top) < self.y_tolerance
            )
        )

    def iter_words_to_lines(self, words: Iterable[WordSymbol]):
        """iter_words_to_lines."""
        current_line = []
        for word in sorted(words, key=lambda x: x.x0):
            # 如果是空白行是否保留
            if not self.keep_blank_chars and word.text.isspace():
                if current_line:
                    yield current_line
                    current_line = []

            # 检查是否起了一行
            elif current_line and self.word_begins_new_line(current_line, word):
                yield current_line
                current_line = [word]

            # 合并作为一行
            else:
                current_line.append(word)

        if current_line:
            yield current_line

    def iter_extract(self, words: Iterable[WordSymbol]):
        """iter_extract."""
        for char_group in cluster_objects(list(words), "bottom", self.y_tolerance):
            # for line_group in cluster_objects(char_group, "x0", self.x_tolerance):
            for word_chars in self.iter_words_to_lines(char_group):
                yield self.merge_lines(word_chars)

    def extract(self, words: Iterable[WordSymbol]):
        """extract."""
        return list(self.iter_extract(words))


class BlockExtractor(object):
    """BlockExtractor."""

    def __init__(self, **settings):
        """构造函数."""
        self.x_tolerance = max(settings.get("x_tolerance", DEFAULT_X_TOLERANCE), 0)
        self.y_tolerance = max(settings.get("y_tolerance", DEFAULT_Y_TOLERANCE), 0)
        self.keep_blank_chars = settings.get("keep_blank_chars", False)
        self.use_text_flow = settings.get("use_text_flow", False)
        self.horizontal_ltr = settings.get("horizontal_ltr", True)
        self.vertical_ttb = settings.get("vertical_ttb", True)
        self.extra_attrs = settings.get("extra_attrs", [])

    def merge_lines(self, ordered_chars: List[WordSymbol]):
        """合并行."""
        x0, top, x1, bottom, words, labels, iob = objects_to_bbox(
            sorted(ordered_chars, key=lambda x: x.x0)
        )
        word = WordBoxSymbol(
            **{
                "label": ",".join(labels),
                "text": " ".join(words),
                "x0": x0,
                "x1": x1,
                "y0": top,
                "y1": bottom,
                "iob": iob,
            }
        )
        return word

    def word_begins_new_line(
        self, current_words: List[WordSymbol], next_word: WordSymbol
    ):
        """word_begins_new_line."""
        if self.x_tolerance <= 0 or next_word.iob == "B":
            return True

        # 重算合并后的方格大小
        (
            _,
            word_y0,
            _,
            word_y1,
            _,
            _,
            _,
        ) = objects_to_bbox(current_words)

        # 如果是左右相邻，两高度偏差不大
        # 或者坐标完全包含
        # Y轴已根据容错值分组，这边只判断横轴
        return not (
            (
                abs(next_word.bottom - word_y1) < self.y_tolerance
                # and abs(next_word.top - word_top) < self.y_tolerance
            )
            or (
                abs(next_word.top - word_y0) < self.y_tolerance
                # and abs(next_word.top - word_top) < self.y_tolerance
            )
        )

    def iter_words_to_block(self, words: Iterable[WordSymbol]):
        """iter_words_to_block."""
        current_line = []
        for word in sorted(words, key=lambda x: x.bottom):
            # 如果是空白行是否保
            if not self.keep_blank_chars and word.text.isspace():
                if current_line:
                    yield current_line
                    current_line = []

            # 检查是否起了一行
            elif current_line and self.word_begins_new_line(current_line, word):
                yield current_line
                current_line = [word]

            # 合并作为一行
            else:
                current_line.append(word)

        if current_line:
            yield current_line

    def iter_extract(self, words: Iterable[WordSymbol]):
        """iter_extract."""
        # 算法假定左对齐文本未相同块
        for char_group in cluster_objects(list(words), "x0", self.x_tolerance):
            # for line_group in cluster_objects(char_group, "x0", self.x_tolerance):
            for word_chars in self.iter_words_to_block(char_group):
                yield self.merge_lines(word_chars)

    def extract(self, words: Iterable[WordSymbol]):
        """extract."""
        return list(self.iter_extract(words))


def extract_lines(words: Iterable[WordSymbol], **kwargs):
    """横向合并."""
    settings = dict(DEFAULT_WORD_EXTRACTION_SETTINGS)
    settings.update(kwargs)
    return LineExtractor(**settings).extract(words)


def extract_block(words: Iterable[WordSymbol], **kwargs):
    """纵向合并."""
    settings = dict(DEFAULT_WORD_EXTRACTION_SETTINGS)
    settings.update(kwargs)
    return BlockExtractor(**settings).extract(words)


def merge_block(
    words: Iterable[WordSymbol],
    x_tolerance=DEFAULT_X_TOLERANCE,
    y_tolerance=DEFAULT_Y_TOLERANCE,
) -> List[WordBoxSymbol]:
    """合并放个."""
    groups = defaultdict(list)
    for token in words:
        groups[token.label].append(token)

    lines = [
        extract_block(
            extract_lines(
                val,
                x_tolerance=x_tolerance,
                y_tolerance=y_tolerance,
            ),
            x_tolerance=y_tolerance,
            y_tolerance=x_tolerance,
        )
        for key, val in groups.items()
        if key.lower() != "other"
    ]
    return list(itertools.chain(*lines))
