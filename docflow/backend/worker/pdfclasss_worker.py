# -*- coding: utf-8 -*-
"""
@create: 2023-05-31 10:05:46.

@author: name

@desc: 文件分类
"""

import time
from typing import List

from docflow.backend.predict_transformers import Layoutlmv3ClassificationBertPredict
from docflow.backend.predict_transformers import Layoutlmv3ClassificationPredict
from conductor.client.http.models.task_exec_log import TaskExecLog
from conductor.client.worker.worker import Task
from conductor.client.worker.worker import TaskResult

from .base import ConductorWorker


class PdfclassBertPredictWorker(ConductorWorker):
    """PdfclassBertPredictWorker."""

    def load_module(self):
        """懒加载模型."""
        cli = getattr(self, "cli", None)
        if cli:
            return cli

        cli = Layoutlmv3ClassificationBertPredict()
        setattr(self, "cli", cli)
        return cli

    def execute_(
        self, task: Task, task_result: TaskResult, logs: List[TaskExecLog]
    ) -> TaskResult:
        """执行任务."""
        assert not logs
        assert isinstance(task.input_data, dict)

        url: str = task.input_data.get("url", "")
        ocr_s3: str = task.input_data.get("ocr_s3", "")
        label: str = task.input_data.get("label", "")
        if not url:
            raise TypeError("image url not set")

        task_id = task.task_id
        task_result.logs = logs

        label = self.async_run(self.predict(url, ocr_s3))
        logs.append(TaskExecLog(f"执行完成[{label}]", task_id, time.time()))
        task_result.add_output_data("label", label)
        return task_result

    async def predict(self, url: str, ocr_s3: str):
        """请求模型推理."""
        cli = self.load_module()
        label = await cli.predict(url, ocr_s3)
        return label


class PdfclassPredictWorker(PdfclassBertPredictWorker):
    """PdfclassPredictWorker."""

    def load_module(self):
        """懒加载模型."""
        cli = getattr(self, "cli", None)
        if cli:
            return cli

        cli = Layoutlmv3ClassificationPredict()
        setattr(self, "cli", cli)
        return cli
