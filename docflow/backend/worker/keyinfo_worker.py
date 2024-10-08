# -*- coding: utf-8 -*-
"""
@create: 2023-05-31 10:05:41.

@author: name

@desc: 关键信息提取
"""

from typing import List

from docflow.backend.predict_transformers import Layoutlmv3Predict
from conductor.client.http.models.task_exec_log import TaskExecLog
from conductor.client.worker.worker import Task
from conductor.client.worker.worker import TaskResult

from .base import ConductorWorker


class KeyinfoPredictWorker(ConductorWorker):
    """KeyinfoPredictWorker."""

    def load_module(self):
        """懒加载模型."""
        cli = getattr(self, "cli", None)
        if cli:
            return cli

        cli = Layoutlmv3Predict()
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
        if not ocr_s3:
            raise TypeError("ocr_s3 not set")

        label: str = task.input_data.get("label", "")
        if not url:
            raise TypeError("image url not set")

        out_s3: str = task.input_data.get("out_s3", "")
        tokens = self.async_run(self.predict(url, ocr_s3, label))
        if out_s3:
            self.put_s3_result(out_s3, {"tokens": tokens})
        else:
            task_result.add_output_data("tokens", tokens)
        return task_result

    async def predict(self, url: str, ocr_s3: str, label: str):
        """请求模型推理."""
        cli = self.load_module()
        _, tokens = await cli.predict(url, ocr_s3)
        return [i.dict() for i in tokens]
