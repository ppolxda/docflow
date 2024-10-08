# -*- coding: utf-8 -*-
"""
@create: 2022-08-23 11:21:42.

@author: ppolxda

@desc: 接口签名
"""
import binascii
import hashlib
import json
from io import BytesIO
from typing import Iterable
from typing import List
from typing import Optional
from typing import Union

import requests
from PIL import Image
from pydantic import Field

from .predict_utils import BaseModel
from .predict_utils import download_file
from .predict_utils import image_to_bytes
from .predict_utils import logger
from .settings import settings


class WordSymbol(BaseModel):
    """WordSymbol."""

    x0: float = 0.00
    y0: float = 0.00
    x1: float = 0.00
    y1: float = 0.00
    text: str = ""
    label: str = ""
    iob: str = "iob"

    @property
    def center_x(self):
        """Center x."""
        return float((self.x0 + self.x1) / 2)

    @property
    def center_y(self):
        """Center y."""
        return float((self.y0 + self.y1) / 2)

    @property
    def bbox(self):
        """Center y."""
        return (self.x0, self.y0, self.x1, self.y1)

    def __hash__(self):
        """hash."""
        return hash((type(self),) + tuple(self.__dict__.values()))


def sign_image(image: bytes):
    """图片签名."""
    # 相互引用问题,采取懒加载
    if not settings.GOOGLE_API_WEB_SIGN_SALT:
        raise RuntimeError("GAPI_WEB_SIGN_SALT not set")

    # data = hashlib.md5(image).hexdigest()
    sign_data = hashlib.pbkdf2_hmac(
        "sha256", image, settings.GOOGLE_API_WEB_SIGN_SALT.encode(), 10
    )
    return binascii.b2a_hex(sign_data).decode()


def verify_image(image: bytes, sign: Union[str, bytes]):
    """图片签名."""
    if isinstance(sign, bytes):
        sign = sign.decode()
    return sign_image(image) == sign


# EntityAnnotation
# text_annotation.TextAnnotation


class Vertex(BaseModel):
    """BoundingPoint."""

    x: int = 0
    y: int = 0


class NormalizedVertex(BaseModel):
    """BoundingPoint."""

    x: float = 0
    y: float = 0


class BoundingPoly(BaseModel):
    """BoundingPoly.

    https://github.com/googleapis/python-vision/blob/177f373f3d83caf9c344f6a1b551734f30f5a942/google/cloud/vision_v1/types/geometry.py#L74
    """

    vertices: List[Vertex] = Field(default_factory=list)
    normalized_vertices: List[NormalizedVertex] = Field(default_factory=list)

    @property
    def x0(self):  # pylint: disable=invalid-name
        """x0."""
        return int(min(i.x for i in self.vertices))

    @property
    def x1(self):  # pylint: disable=invalid-name
        """x1."""
        return int(max(i.x for i in self.vertices))

    @property
    def y0(self):  # pylint: disable=invalid-name
        """y0."""
        return int(min(i.y for i in self.vertices))

    @property
    def y1(self):  # pylint: disable=invalid-name
        """y1."""
        return int(max(i.y for i in self.vertices))

    @property
    def center_x(self):  # pylint: disable=invalid-name
        """Center x."""
        return int((self.x0 + self.x1) / 2)

    @property
    def center_y(self):  # pylint: disable=invalid-name
        """Center y."""
        return int((self.y0 + self.y1) / 2)


class Property(BaseModel):
    """Property.

    https://github.com/googleapis/python-vision/blob/177f373f3d83caf9c344f6a1b551734f30f5a942/google/cloud/vision_v1/types/image_annotator.py#L419
    """

    name: str = ""
    value: str = ""
    uint64_value: int = 0


class EntityAnnotation(BaseModel):
    """EntityAnnotation.

    https://github.com/googleapis/python-vision/blob/177f373f3d83caf9c344f6a1b551734f30f5a942/google/cloud/vision_v1/types/image_annotator.py#L445
    """

    mid: str = ""
    locale: str = ""
    description: str = ""
    score: float = 0.00
    confidence: float = 0.00
    topicality: float = 0.00
    bounding_poly: BoundingPoly = Field(default_factory=BoundingPoly)
    properties: Property = Field(default_factory=Property)
    # locations: LocationInfo = ""


class DetectedLanguage(BaseModel):
    """DetectedLanguage."""

    language_code: str = ""
    confidence: float = 0.000


class TextProperty(BaseModel):
    r"""TextProperty.

    https://github.com/googleapis/python-vision/blob/177f373f3d83caf9c344f6a1b551734f30f5a942/google/cloud/vision_v1/types/text_annotation.py#L101
    """

    detected_languages: List[DetectedLanguage] = Field(default_factory=list)
    # detected_break = DetectedBreak = Field(default_factory=DetectedBreak)


class Symbol(BaseModel):
    """A single symbol representation.

    https://github.com/googleapis/python-vision/blob/177f373f3d83caf9c344f6a1b551734f30f5a942/google/cloud/vision_v1/types/text_annotation.py#L349
    """

    property: TextProperty = Field(default_factory=TextProperty)
    bounding_box: BoundingPoly = Field(default_factory=BoundingPoly)
    text: str = ""
    confidence: float = 0.00


class Word(BaseModel):
    """A word representation.

    https://github.com/googleapis/python-vision/blob/177f373f3d83caf9c344f6a1b551734f30f5a942/google/cloud/vision_v1/types/text_annotation.py#L302
    """

    property: TextProperty = Field(default_factory=TextProperty)
    bounding_box: BoundingPoly = Field(default_factory=BoundingPoly)
    symbols: List[Symbol] = Field(default_factory=list)
    confidence: float = 0.00


class Paragraph(BaseModel):
    """Paragraph.

    https://github.com/googleapis/python-vision/blob/177f373f3d83caf9c344f6a1b551734f30f5a942/google/cloud/vision_v1/types/text_annotation.py#L254
    """

    property: TextProperty = Field(default_factory=TextProperty)
    bounding_box: BoundingPoly = Field(default_factory=BoundingPoly)
    words: List[Word] = Field(default_factory=list)
    confidence: float = 0.00


class Block(BaseModel):
    """Block.

    https://github.com/googleapis/python-vision/blob/177f373f3d83caf9c344f6a1b551734f30f5a942/google/cloud/vision_v1/types/text_annotation.py#L177
    """

    property: TextProperty = Field(default_factory=TextProperty)
    bounding_box: BoundingPoly = Field(default_factory=BoundingPoly)
    paragraphs: List[Paragraph] = Field(default_factory=list)
    block_type: str = ""  # TEXT | TABLE | PICTURE | RULER | BARCODE
    confidence: float = 0.00


class Pages(BaseModel):
    """FullPages.

    https://github.com/googleapis/python-vision/blob/177f373f3d83caf9c344f6a1b551734f30f5a942/google/cloud/vision_v1/types/text_annotation.py#L134
    """

    property: TextProperty = Field(default_factory=TextProperty)
    width: int = 0
    height: int = 0
    blocks: List[Block] = Field(default_factory=list)
    confidence: float = 0.00


class TextAnnotation(BaseModel):
    """TextAnnotation.

    https://github.com/googleapis/python-vision/blob/177f373f3d83caf9c344f6a1b551734f30f5a942/google/cloud/vision_v1/types/text_annotation.py#L34
    """

    text: str = ""
    pages: List[Pages] = Field(default_factory=list)


class OcrData(BaseModel):
    """OcrData."""

    text_annotations: List[EntityAnnotation] = Field(default_factory=list)
    full_text_annotation: TextAnnotation = Field(default_factory=TextAnnotation)


def iter_conv_google2symbol(gocrs: OcrData) -> Iterable[WordSymbol]:
    """转换google结构到内部简化结构."""
    for text in gocrs.text_annotations[1:]:
        yield WordSymbol(
            x0=float(text.bounding_poly.x0),
            x1=float(text.bounding_poly.x1),
            y0=float(text.bounding_poly.y0),
            y1=float(text.bounding_poly.y1),
            text=text.description.strip(),
            label="",
        )


async def ocr_image(
    image: Image.Image,
    ocr_uri: Optional[str] = None,
    download_timeout: Optional[int] = None,
) -> List[WordSymbol]:
    """获取S3OCR缓存."""
    if ocr_uri and isinstance(ocr_uri, str):
        ocrdata = await load_s3_cache(ocr_uri, download_timeout)
        if not ocrdata:
            return await ocr_image(image, "", download_timeout)
    else:
        buffer = image_to_bytes(image)
        ocrdata = await api.ocr_image(buffer)

    if not ocrdata:
        # raise TypeError("未能加载到OCR数据")
        return []

    return ocrdata


async def load_s3_cache(
    ocr_uri: str, download_timeout: Optional[int] = None
) -> List[WordSymbol]:
    """获取S3OCR缓存."""
    rrr = []
    try:
        data = await download_file(ocr_uri, download_timeout)
        data = json.loads(data)
        rrr = [WordSymbol(**i) for i in data["words"]]
    except Exception as ex:
        logger.warning("下载S3缓存失败[%s]%s", ex, ocr_uri)
        return []
    else:
        return rrr


class GoogleOcrApi(object):
    """GoogleOcrApi."""

    def __init__(
        self,
        api_host: Optional[str] = None,
        default_timeout: Optional[int] = None,
    ):
        """初始化函数."""
        # 相互引用问题,采取懒加载
        if api_host is None:
            api_host = settings.GOOGLE_API

        if default_timeout is None:
            default_timeout = settings.GOOGLE_API_TIMEOUT

        self.api_host = api_host
        self.default_timeout = default_timeout

    async def ocr_image(
        self, image: Union[bytes, str], timeout: Optional[int] = None
    ) -> List[WordSymbol]:
        """识别图片.

        http://8.210.121.25:20000/gapi/docs#/default/read_file_ocr_post
        """
        rrr = await self.ocr_image_to_word(image, timeout)
        return [i for i in iter_conv_google2symbol(rrr)]

    async def ocr_image_to_word(
        self, image: Union[bytes, str], timeout: Optional[int] = None
    ) -> OcrData:
        """识别图片.

        http://8.210.121.25:20000/gapi/docs#/default/read_file_ocr_post
        """
        if timeout is None:
            timeout = self.default_timeout

        if isinstance(image, str):
            image_data = await download_file(image)
        else:
            image_data = image

        url = self.api_host + "/ocr"
        rrr = requests.post(
            url,
            files={
                "files": BytesIO(image_data),
            },
            data={
                "sign": sign_image(image_data),
            },
            timeout=timeout,
        )
        logger.debug(
            "google ocr[%s][%s]",
            rrr.status_code,
            image if not isinstance(image, bytes) else "",
        )
        if rrr.status_code != 200:
            raise TypeError(f"[{self.api_host}]请求识别失败[{rrr.status_code}]")

        data = rrr.json()
        return OcrData(**data)


api = GoogleOcrApi()
