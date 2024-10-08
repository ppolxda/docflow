# -*- coding: utf-8 -*-
"""
@create: 2022-09-08 09:29:12.

@author: ppolxda

@desc: 推理对象
"""

import glob
import os
import re
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import numpy as np
import torch
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from transformers import AutoTokenizer
from transformers import LayoutLMv3FeatureExtractor
from transformers import LayoutLMv3Processor
from transformers.models.auto.modeling_auto import AutoModelForSequenceClassification
from transformers.models.auto.modeling_auto import AutoModelForTokenClassification
from transformers.models.auto.processing_auto import AutoProcessor

from .google_ocr import WordSymbol
from .google_ocr import ocr_image
from .predict_utils import download_image
from .predict_utils import find_registry_path
from .settings import settings

# from .predict_utils import logger
# from .predict_utils import LAYOUTLMV3_MODULE

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # type: ignore # pylint: disable=no-member


def load_image(image_path):
    """load_image."""
    image = Image.open(image_path).convert("RGB")
    weight, height = image.size
    return image, (weight, height)


def normalize_bbox(bbox, size):
    """normalize_bbox."""
    return [
        int(1000 * bbox[0] / size[0]),
        int(1000 * bbox[1] / size[1]),
        int(1000 * bbox[2] / size[0]),
        int(1000 * bbox[3] / size[1]),
    ]


def unnormalize_box(bbox, width, height):
    """unnormalize_box."""
    return [
        width * (bbox[0] / 1000),
        height * (bbox[1] / 1000),
        width * (bbox[2] / 1000),
        height * (bbox[3] / 1000),
    ]


def iob_to_label(label):
    """iob_to_label."""
    label = label[2:]
    if not label:
        return "other"
    return label


def download_from_registry(src_path: str, dst_path: str):
    """从mlflow下载模型."""
    import mlflow  # pylint: disable=import-outside-toplevel

    if not os.path.isdir(dst_path):
        os.makedirs(dst_path, exist_ok=True)

    # 找到对应 checkpoint
    if src_path.startswith("runs:/"):
        search_path = os.path.join(
            dst_path, "checkpoint-*", "artifacts", "checkpoint-*"
        )
    else:
        search_path = os.path.join(dst_path, "artifacts", "checkpoint-*")

    paths = glob.glob(search_path)
    if paths:
        return paths[0]

    mlflow.pyfunc.load_model(src_path, dst_path=dst_path)
    return glob.glob(search_path)[0]


class LabelstudDocOcrDataProcess:
    """LabelstudDocOcrDataProcess."""

    def __init__(self):
        """初始化数据.

        labelstud_host: labelstud访问地址
        labelstud_token: labelstud授权token
        labelstud_class: labelstud分类模式(label|image-class)
        project_train: 训练数据集名称
        project_test: 测试数据集名称
        """

    def get_line_bbox(self, bboxs):
        """get_line_bbox."""
        x = [bboxs[i][j] for i in range(len(bboxs)) for j in range(0, len(bboxs[i]), 2)]
        y = [bboxs[i][j] for i in range(len(bboxs)) for j in range(1, len(bboxs[i]), 2)]
        x0, y0, x1, y1 = min(x), min(y), max(x), max(y)

        assert x1 >= x0 and y1 >= y0
        # bbox = [[x0, y0, x1, y1] for _ in range(len(bboxs))]
        return [[x0, y0, x1, y1]] * len(bboxs)

    async def generate_image_examples(
        self,
        file: Union[bytes, str, Image.Image],
        ocr_uri: Optional[str] = None,
        download_timeout: Optional[int] = None,
    ):
        """generate_examples.

        files: to see ./tests/data/export_data.json
        """
        if isinstance(file, Image.Image):
            image = file
        else:
            image = await download_image(file, download_timeout)

        # 如果字太多，放弃推理
        ocrdata = await ocr_image(image, ocr_uri, download_timeout)
        if not ocrdata:
            return {
                "tokens": [],
                "bboxes": [],
                "image": image,
            }

        size = image.size
        tokens, bboxes = [], []
        for word in ocrdata:
            bbox = normalize_bbox([word.x0, word.y0, word.x1, word.y1], size)
            if min(bbox) < 0 or max(bbox) > 1000:
                continue

            tokens.append(word.text)
            bboxes.append(bbox)

        return {
            "tokens": tokens,
            "bboxes": bboxes,
            "image": image,
        }


class Layoutlmv3Predict(object):
    """Layoutlmv3Predict."""

    def __init__(self, dst_path: Optional[str] = None):
        """初始化函数.

        model_uri = "models:/ocr/1"
        model_uri = "runs:/bf7c270dc20c4d2498893bfbd979600f/checkpoint-10000"
        """
        if dst_path is None:
            dst_path = settings.KEYINFO_MODULE

        self.dst_path = dst_path
        self.model_path = find_registry_path(dst_path)
        self.process = LabelstudDocOcrDataProcess()
        self.processor = AutoProcessor.from_pretrained(self.model_path, apply_ocr=False)
        self.loaded_model = AutoModelForTokenClassification.from_pretrained(
            self.model_path
        ).to(device)

    @staticmethod
    def compare_boxes(x, y):
        """比较方格."""
        bbox1 = np.array([c for c in x])
        bbox2 = np.array([c for c in y])
        equal = np.array_equal(bbox1, bbox2)
        return equal

    async def predict(
        self,
        image_uri: Union[str, bytes],
        ocr_uri: Optional[str] = None,
        download_timeout=None,
    ) -> Tuple[Image.Image, List[WordSymbol]]:
        """推理数据.

        model_uri = "models:/ocr/1"
        model_uri = "runs:/bf7c270dc20c4d2498893bfbd979600f/checkpoint-10000"
        """
        example = await self.process.generate_image_examples(
            image_uri, ocr_uri, download_timeout
        )
        boxes, words, image = example["bboxes"], example["tokens"], example["image"]
        if not words or len(words) > settings.WORD_LIMIT:
            return image, []

        stride = 256
        image = image.convert("RGB")
        encoding = self.processor(
            image,
            words,
            boxes=boxes,
            return_offsets_mapping=True,
            return_overflowing_tokens=True,
            truncation=True,
            padding="max_length",
            stride=stride,  # 128 容易发生标签错误
            max_length=512,
            return_tensors="np",
        ).convert_to_tensors("pt")
        # page_size = len(encoding.encodings) if encoding.encodings else 0
        offset_mapping = encoding.pop("offset_mapping")
        encoding.pop("overflow_to_sample_mapping")

        with torch.no_grad():
            encoding = encoding.to(device)
            outputs = self.loaded_model(**encoding)

        logits = outputs.logits
        predictions = logits.argmax(-1).squeeze().tolist()
        token_boxes = encoding.bbox.squeeze().tolist()
        width, height = image.size
        id2label = self.loaded_model.config.id2label
        page_size = len(encoding.encodings) if encoding.encodings else 0
        predictions = predictions if page_size > 1 else [predictions]
        token_boxes = token_boxes if page_size > 1 else [token_boxes]

        true_predictions = []
        for i, (pred, box, mapped) in enumerate(
            zip(predictions, token_boxes, offset_mapping)
        ):
            is_subword = np.array(mapped.squeeze().tolist())[:, 0] != 0
            assert len(pred) == len(box)
            datas = [
                (
                    id2label[pred_][0],
                    iob_to_label(id2label[pred_]),
                    unnormalize_box(box_, width, height),
                )
                for idx, (pred_, box_) in enumerate(zip(pred, box))
                if (not is_subword[idx])
            ]
            if i == 0:
                true_predictions += datas
            else:
                true_predictions += datas[1 + stride - sum(is_subword[: 1 + stride]) :]

        tokens = [
            WordSymbol(
                x0=box[0],
                y0=box[1],
                x1=box[2],
                y1=box[3],
                text=next(
                    (
                        word
                        for word, oldbox in zip(words, boxes)  # type: ignore
                        if self.compare_boxes(
                            box, unnormalize_box(oldbox, width, height)
                        )
                    ),
                    "",
                ),
                label=prediction,
                iob=iob,
            )
            for iob, prediction, box in true_predictions
            if any(box) and prediction != "other"  # 存在全部0的方框，采取过滤操作
        ]
        return image, list(set(tokens))

    async def predict_and_draw_box(self, image_uri: Union[str, bytes]):
        """识别并绘制图片测试用.

        model_uri = "models:/ocr/1"
        model_uri = "runs:/bf7c270dc20c4d2498893bfbd979600f/checkpoint-10000"
        """
        image, tokens = await self.predict(image_uri)
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        for token in tokens:
            draw.rectangle(token.bbox, outline="red")
            draw.text(
                (token.bbox[0] + 10, token.bbox[1] - 10),
                text=token.label,
                fill="red",
                font=font,
            )

        return image, tokens


class Layoutlmv3ClassificationPredict(object):
    """Layoutlmv3ClassificationPredict."""

    def __init__(self, dst_path: Optional[str] = None):
        """构造函数."""
        if dst_path is None:
            dst_path = settings.PDFCLASS_MODULE

        self.dst_path = dst_path
        self.model_path = find_registry_path(dst_path)
        self.loaded_model = AutoModelForSequenceClassification.from_pretrained(
            self.model_path
        ).to(device)
        feature_extractor = LayoutLMv3FeatureExtractor(apply_ocr=False)
        tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.process = LabelstudDocOcrDataProcess()
        self.processor = LayoutLMv3Processor(feature_extractor, tokenizer)

    async def predict(
        self,
        image_uri: Union[str, bytes, Image.Image],
        ocr_uri: Optional[str] = None,
        download_timeout=None,
    ) -> str:
        """推理数据.

        model_uri = "models:/ocr/1"
        model_uri = "runs:/bf7c270dc20c4d2498893bfbd979600f/checkpoint-10000"
        """
        example = await self.process.generate_image_examples(
            image_uri, ocr_uri, download_timeout
        )
        boxes, words, image = example["bboxes"], example["tokens"], example["image"]
        if not words or len(words) > settings.WORD_LIMIT:
            return "FT_NULL"

        image = image.convert("RGB")
        encoding = self.processor(
            image,
            words,
            boxes=boxes,
            return_tensors="pt",
            truncation=True,
            padding="max_length",
            max_length=512,
        )
        encoding = encoding.to(device)
        outputs = self.loaded_model(**encoding)
        logits = outputs.logits
        predicted_class_idx = logits.argmax(-1).item()
        return self.loaded_model.config.id2label[predicted_class_idx]


class Layoutlmv3ClassificationBertPredict(object):
    """Layoutlmv3ClassificationBertPredict."""

    # LABELS = Layoutlmv3ClassificationPredict.LABELS

    def __init__(self, dst_path: Optional[str] = None):
        """构造函数."""
        if dst_path is None:
            dst_path = settings.PDFCLASS_BERT_MODULE

        self.dst_path = dst_path
        self.model_path = find_registry_path(dst_path)
        self.loaded_model = AutoModelForSequenceClassification.from_pretrained(
            self.model_path
        ).to(device)
        self.process = LabelstudDocOcrDataProcess()
        self.processor = AutoProcessor.from_pretrained(self.model_path)

    def clean_text(self, text):
        """数据清理."""
        text = text.lower()
        text = re.sub(r"[^a-zA-Z?.!,¿]+", " ", text)
        text = re.sub(r"http\S+", "", text)
        html = re.compile(r"<.*?>")
        text = html.sub(r"", text)
        punctuations = "@#!?+&*[]-%.:/();$=><|{}^" + "'`" + "_"
        for i in punctuations:
            text = text.replace(i, "")  # Removing punctuations

        emoji_pattern = re.compile(
            "["
            "\U0001f600-\U0001f64f"  # emoticons
            "\U0001f300-\U0001f5ff"  # symbols & pictographs
            "\U0001f680-\U0001f6ff"  # transport & map symbols
            "\U0001f1e0-\U0001f1ff"  # flags (iOS)
            "\U00002702-\U000027b0"
            "\U000024c2-\U0001f251"
            "]+",
            flags=re.UNICODE,
        )
        text = emoji_pattern.sub(r"", text)  # Removing emojis
        return text

    async def predict(
        self,
        image_uri: Union[str, bytes, Image.Image],
        ocr_uri: Optional[str] = None,
        download_timeout=None,
    ) -> str:
        """推理数据.

        model_uri = "models:/ocr/1"
        model_uri = "runs:/bf7c270dc20c4d2498893bfbd979600f/checkpoint-10000"
        """
        example = await self.process.generate_image_examples(
            image_uri, ocr_uri, download_timeout
        )
        _, words, image = example["bboxes"], example["tokens"], example["image"]
        if not words or len(words) > settings.WORD_LIMIT:
            return "FT_NULL"

        image = image.convert("RGB")
        encoding = self.processor(
            self.clean_text(" ".join(words)),
            return_tensors="pt",
            truncation=True,
            padding="max_length",
            max_length=512,
        )
        encoding = encoding.to(device)
        outputs = self.loaded_model(**encoding)
        logits = outputs.logits
        predicted_class_idx = logits.argmax(-1).item()
        return self.loaded_model.config.id2label[predicted_class_idx]
