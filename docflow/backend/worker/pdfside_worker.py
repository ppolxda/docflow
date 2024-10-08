# -*- coding: utf-8 -*-
"""
@create: 2023-05-31 10:05:46.

@author: name

@desc: 文件分类
"""

import time
from typing import List

from docflow.backend.predict_yolo import YoloDataProcess
from conductor.client.http.models.task_exec_log import TaskExecLog
from conductor.client.worker.worker import Task
from conductor.client.worker.worker import TaskResult

from .base import ConductorWorker


class PdfSidePredictWorker(ConductorWorker):
    """PdfSidePredictWorker."""

    def load_module(self):
        """懒加载模型."""
        cli = getattr(self, "cli", None)
        if cli:
            return cli

        cli = YoloDataProcess()
        setattr(self, "cli", cli)
        return cli

    def execute_(
        self, task: Task, task_result: TaskResult, logs: List[TaskExecLog]
    ) -> TaskResult:
        """执行任务."""
        assert not logs
        assert isinstance(task.input_data, dict)
        logs = []
        task_result.logs = logs

        task_id = task.task_id
        url: str = task.input_data.get("url", "")
        if not url:
            raise TypeError("image url not set")

        mode: str = task.input_data.get("mode", "rotate")
        rotate = self.async_run(self.predict(url, mode))
        logs.append(TaskExecLog(f"执行完成[{rotate}]", task_id, time.time()))
        task_result.add_output_data("rotate", rotate)
        return task_result

    async def predict(self, url: str, mode: str):
        """请求模型推理."""
        cli = self.load_module()
        if mode == "degree":
            rotate = await cli.degree_predict(url)
        else:
            rotate = await cli.predict(url)
        return rotate
