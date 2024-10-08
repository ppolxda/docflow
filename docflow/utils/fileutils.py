# -*- coding: utf-8 -*-
"""
@create: 2021-10-18 22:32:34.

@author: name

@desc: 图像工具类
"""
import math
import numbers
import os
import tempfile
from decimal import ROUND_HALF_UP
from decimal import Decimal
from functools import partial
from inspect import signature
from io import BytesIO
from pathlib import Path
from typing import Awaitable
from typing import Callable
from typing import List
from typing import Optional
from typing import TypeVar
from typing import Union

import filetype
import ghostscript
from fastapi import APIRouter
from fastapi import FastAPI
from PIL import Image

RT = TypeVar("RT")


def bytes_to_image(xxx: Union[bytes, BytesIO]):
    """图片转BytesIO."""
    if isinstance(xxx, BytesIO):
        xxx.seek(0)
        ccc = xxx
    elif isinstance(xxx, bytes):
        ccc = BytesIO(xxx)
        ccc.name = "test.png"
    else:
        raise TypeError("image invaild")
    return Image.open(ccc)


def image_to_bytes(xxx: Image.Image):
    """图片转BytesIO."""
    ccc = BytesIO()
    xxx.save(ccc, "png")
    ccc.seek(0)
    return ccc.read()


def get_content(data):
    """获取文件后缀."""
    if not isinstance(data, (bytes, BytesIO)):
        raise TypeError("filetype invaild")

    content_type = filetype.guess(data)
    if content_type is None:
        raise TypeError("filetype invaild")

    extension = content_type.extension
    content_type = content_type.mime
    return content_type, extension


def is_png_image(data):
    """是否是图片格式."""
    content_type, _ = get_content(data)
    return content_type == "image/png"


def is_image(data):
    """是否是图片格式."""
    if not isinstance(data, (bytes, BytesIO)):
        return False

    rtype = filetype.image_match(data)
    return rtype is not None


def is_pdf(data):
    """是否是PDF格式."""
    if not isinstance(data, (bytes, BytesIO)):
        return False

    rtype = filetype.guess(data)
    return rtype and rtype.extension == "pdf"


def is_word(data):
    """是否是word格式."""
    if not isinstance(data, (bytes, BytesIO)):
        return False

    rtype = filetype.guess(data)
    return rtype and (rtype.extension == "docx" or rtype.extension == "doc")


def is_json(data: bytes):
    """检查是否是json字符串."""
    if not data:
        return False

    try:
        data_str = data.decode()
    except Exception:
        return False

    data_str = data_str.strip()
    return data_str[0] in ["[", "{"] and data_str[-1] in ["]", "}"]


def resize_image(image: Image.Image, short_size=256):
    """图片缩放 - 主要生成缩略图."""
    min_side = min(image.width, image.height)
    zoom = short_size / min_side
    return image.resize((int(image.width * zoom), int(image.height * zoom)))


def pdf2png_with_ghostscript(
    pdf_data: Union[bytes, str], resolution=200, page: Optional[int] = None
):
    """转换图片."""
    args = [
        "pdf2png",
        "-dBATCH",
        "-dNOPAUSE",
        # "-dTextAlphaBits=4",
        "-sDEVICE=png16m",
        f"-r{resolution}",
    ]
    if page:
        args += [f"-sPageList={page}"]

    images: List[Image.Image] = []
    with tempfile.TemporaryDirectory() as path:
        path_ = Path(path)
        image_path = path_.joinpath("%03d.png")

        if isinstance(pdf_data, bytes):
            pdf_path = str(path_.joinpath("mypdf.pdf"))
            with open(pdf_path, "wb") as fs:
                fs.write(pdf_data)
        else:
            pdf_path = pdf_data

        args += [
            f"-sOutputFile={str(image_path)}",
            pdf_path,
        ]
        ghostscript.Ghostscript(*args)
        for image in sorted(path_.glob("*.png")):
            with open(image, "rb") as fs:
                ccc = BytesIO(fs.read())
                ccc.name = os.path.basename(image)
                images.append(Image.open(ccc))

    return images


def iter_page_image(pdf_buf: bytes, resolution: int = 150, thread_count=4):
    """PDF转图片.

    公式 https://pixelcalculator.com/en

    pixel = dpi * mm / 25.4 mm (1 in)
    dpi = pixel * 25.4 mm (1 in) / mm

    resolution = 200 dpi
    A4 = 210 × 297 mm
    A4 210 mm = 595.2 px
    """
    assert thread_count
    imgs = pdf2png_with_ghostscript(pdf_buf, resolution)
    return imgs


def pdf2image(pdf_buf: bytes, resolution: int = 150, thread_count=4):
    """PDF转图片.

    公式 https://pixelcalculator.com/en

    pixel = dpi * mm / 25.4 mm (1 in)
    dpi = pixel * 25.4 mm (1 in) / mm

    resolution = 200 dpi
    A4 = 210 × 297 mm
    A4 210 mm = 595.2 px
    """
    assert thread_count
    imgs = pdf2png_with_ghostscript(pdf_buf, resolution)
    return imgs


def page2image(pdf_buf: bytes, page=0, resolution: int = 100, thread_count=4):
    """指定页码PDF转图片."""
    assert thread_count
    imgs = pdf2png_with_ghostscript(pdf_buf, resolution, page=page)
    return imgs[0]  # type: ignore


def _decimalize(v, q=None):
    """数字转换Decimal结构."""
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
    """数字转换Decimal列表结构."""
    # If already a decimal, just return itself
    if type(v) == Decimal:
        return v

    # If tuple/list passed, bulk-convert
    if isinstance(v, (tuple, list)):
        return type(v)(decimalize(x, q) for x in v)
    else:
        return _decimalize(v, q)


def find_field_idx(field: str, func: Callable[..., Awaitable]) -> int:
    """Find session index in function call parameter."""
    func_params = signature(func).parameters
    try:
        # func_params is an ordered dict -- this is the "recommended" way of getting the position
        session_args_idx = tuple(func_params).index(field)
    except ValueError:
        raise ValueError(
            f"Function {func.__qualname__} has no `{field}` argument"
        ) from None

    return session_args_idx


def field_getter(field, func):
    """参数提取函数."""
    find_idx = partial(find_field_idx, field)
    try:
        arg_index = find_idx(func)
    except ValueError:
        arg_index = -1

    def get_field(*args, **kwargs):
        """获取字段."""
        if field in kwargs:
            return kwargs[field]
        elif arg_index >= 0 and arg_index < len(args):
            return args[arg_index]  # type: ignore
        else:
            return None

    return get_field


def update_schema_name(
    app: Union[FastAPI, APIRouter], function: Callable, name: str
) -> None:
    """补丁修复文档.

    Updates the Pydantic schema name for a FastAPI function that takes
    in a fastapi.UploadFile = File(...) or bytes = File(...).

    This is a known issue that was reported on FastAPI#1442 in which
    the schema for file upload routes were auto-generated with no
    customization options. This renames the auto-generated schema to
    something more useful and clear.

    Args:
        app: The FastAPI application to modify.
        function: The function object to modify.
        name: The new name of the schema.
    """
    for route in app.routes:
        if route.endpoint is function:  # type: ignore
            route.body_field.type_.__name__ = name  # type: ignore
            break


def rotate_image(image: Image.Image, rotate: float):
    """旋转图片."""
    if rotate == 0:
        return image

    return image.rotate(
        rotate,
        fillcolor=(0, 0, 0),
        expand=True,
    )


def rotated_transform(width, height, angle: float):
    """旋转重新计算图片长款.

    代码来自于PIL库
    """
    angle = angle % 360.0
    www, hhh = width, height
    post_trans = (0, 0)
    rotn_center = (www / 2.0, hhh / 2.0)

    angle = -math.radians(angle)
    matrix = [
        round(math.cos(angle), 15),
        round(math.sin(angle), 15),
        0.0,
        round(-math.sin(angle), 15),
        round(math.cos(angle), 15),
        0.0,
    ]

    def transform(x, y, matrix):
        (a, b, c, d, e, f) = matrix
        return a * x + b * y + c, d * x + e * y + f

    matrix[2], matrix[5] = transform(
        -rotn_center[0] - post_trans[0], -rotn_center[1] - post_trans[1], matrix
    )
    matrix[2] += rotn_center[0]
    matrix[5] += rotn_center[1]

    # calculate output size
    xxx = []
    yyy = []
    for x, y in ((0, 0), (www, 0), (www, hhh), (0, hhh)):
        x, y = transform(x, y, matrix)
        xxx.append(x)
        yyy.append(y)

    nww = math.ceil(max(xxx)) - math.floor(min(xxx))  # type: ignore
    nhh = math.ceil(max(yyy)) - math.floor(min(yyy))  # type: ignore

    # We multiply a translation matrix from the right.  Because of its
    # special form, this is the same as taking the image of the
    # translation vector as new translation vector.
    matrix[2], matrix[5] = transform(-(nww - www) / 2.0, -(nhh - hhh) / 2.0, matrix)
    return nww, nhh


def rotated_transform_padding(width, height, angle: float):
    """获取小角度宽高."""
    approach, __ = get_rotate_side(angle)
    new_width, new_height = rotated_transform(width, height, angle)
    if approach in [90, 270]:
        new_width, new_height = new_height, new_width
    return new_width, new_height


def get_rotate_side(rotate: float):
    """获取AI图片的大角度和小角度."""
    approach = min([0, 90, 180, 270], key=lambda x: abs(x - rotate))
    rotate = rotate - approach
    return approach, rotate


def cache_field(name: str):
    """本地对象懒创建装饰器."""

    def warp(func):
        def cache(self, *args, **kwargs):
            """获取缓存."""
            if args or kwargs:
                _args = hash(args + (object(),) + tuple(sorted(kwargs.items())))
                name_ = "_".join([name, str(_args)])
            else:
                name_ = name

            if hasattr(self, name_):
                return getattr(self, name_)

            rrr = func(self, *args, **kwargs)
            if rrr:
                setattr(self, name_, rrr)
            return rrr

        return cache

    return warp
