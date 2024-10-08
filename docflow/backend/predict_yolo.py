# -*- coding: utf-8 -*-
"""
@create: 2022-09-08 09:29:12.

@author: ppolxda

@desc: 推理对象
"""

from typing import Optional
from typing import Union

import cv2
import numpy as np
import torch
from numpy import amax
from numpy import amin
from PIL import Image
from scipy.ndimage import filters
from scipy.ndimage import interpolation
from ultralytics import YOLO
from ultralytics.utils import callbacks

from .predict_utils import download_image
from .predict_utils import find_registry_path
from .settings import settings

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # type: ignore # pylint: disable=no-member

# monkey path 禁用yolo回调，避免服务无法连接被阻塞
callbacks.add_integration_callbacks = lambda x: x


def resize_image(img, scale, max_scale=None):
    """调整图像大小."""
    fff = float(scale) / min(img.shape[0], img.shape[1])
    if max_scale is not None and fff * max(img.shape[0], img.shape[1]) > max_scale:
        fff = float(max_scale) / max(img.shape[0], img.shape[1])
    return cv2.resize(img, (0, 0), fx=fff, fy=fff)  # pylint: disable=no-member


def estimate_skew_angle(raw, angle_range=None):
    """估计图像文字偏转角度.

    angle_range: 角度估计区间
    """
    if not (isinstance(angle_range, list) and len(angle_range) == 2):
        angle_range = [-5, 5]

    raw = resize_image(raw, scale=600, max_scale=900)
    image = raw - amin(raw)  # type: ignore
    image = image / amax(image)
    mmm = interpolation.zoom(image, 0.5)
    mmm = filters.percentile_filter(mmm, 80, size=(20, 2))
    mmm = filters.percentile_filter(mmm, 80, size=(2, 20))
    mmm = interpolation.zoom(mmm, 1.0 / 0.5)
    # w,h = image.shape[1],image.shape[0]
    weight, height = (
        min(image.shape[1], mmm.shape[1]),
        min(image.shape[0], mmm.shape[0]),
    )
    flat = np.clip(image[:height, :weight] - mmm[:height, :weight] + 1, 0, 1)
    dd0, dd1 = flat.shape
    oo0, oo1 = int(0.1 * dd0), int(0.1 * dd1)
    flat = amax(flat) - flat
    flat -= amin(flat)
    est = flat[oo0 : dd0 - oo0, oo1 : dd1 - oo1]
    angles = range(angle_range[0], angle_range[1])

    estimates = []
    for angle in angles:
        roest = interpolation.rotate(est, angle, order=0, mode="constant")
        val = np.mean(roest, axis=1)
        val = np.var(val)
        estimates.append((val, angle))

    _, angle = max(estimates)
    return angle


def eval_angle(img, angle_range=None):
    """估计图片文字的偏移角度."""
    degree = estimate_skew_angle(np.array(img.convert("L")), angle_range=angle_range)
    if degree != 0:
        img = img.rotate(
            degree,
            center=(img.size[0] / 2, img.size[1] / 2),
            expand=1,
            # fillcolor=(0, 0, 0),
            fillcolor=(255, 255, 255),
        )
    return img, degree


class YoloDataProcess:
    """YoloDataProcess."""

    def __init__(self, dst_path: Optional[str] = None):
        """初始化数据."""
        if dst_path is None:
            dst_path = settings.PDFSIDE_MODULE

        self.dst_path = dst_path
        self.model_path = find_registry_path(dst_path)
        self.model = YOLO(self.model_path)

    async def degree_predict(
        self,
        image_uri: Union[bytes, str, Image.Image],
        download_timeout=None,
    ) -> float:
        """generate_examples.

        files: to see ./tests/data/export_data.json
        """
        if isinstance(image_uri, Image.Image):
            image = image_uri
        else:
            image = await download_image(image_uri, download_timeout)

        degree = estimate_skew_angle(np.array(image.convert("L")))
        return -1 * degree

    async def predict(
        self,
        image_uri: Union[bytes, str, Image.Image],
        download_timeout=None,
    ) -> float:
        """generate_examples.

        files: to see ./tests/data/export_data.json
        """
        if isinstance(image_uri, Image.Image):
            image = image_uri
        else:
            image = await download_image(image_uri, download_timeout)

        results = self.model(image, device=device)
        rotate = results[0].names[
            int(results[0].probs.data.argsort(0, descending=True)[:1].tolist()[0])
        ]
        rotate = float(rotate)
        img = image.rotate(
            -1 * rotate,
            expand=True,
            center=(image.size[0] / 2, image.size[1] / 2),
            # fillcolor=(0, 0, 0),
            fillcolor=(255, 255, 255),
        )
        degree = estimate_skew_angle(np.array(img.convert("L")))
        return rotate - degree
