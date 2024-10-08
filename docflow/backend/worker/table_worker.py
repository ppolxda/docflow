# -*- coding: utf-8 -*-
"""
@create: 2023-05-31 10:05:46.

@author: name

@desc: 文件分类
"""

import time
from typing import List

from docflow.backend.predict_table.table_transformer import TableTransformerDetection
from docflow.backend.predict_table.table_transformer import TableTransformerStructure
from docflow.backend.predict_table.tables import TableStructurePredict
from docflow.backend.predict_utils import download_image
from conductor.client.http.models.task_exec_log import TaskExecLog
from conductor.client.worker.worker import Task
from conductor.client.worker.worker import TaskResult

from .base import ConductorWorker


class TableTransformerPredictWorker(ConductorWorker):
    """TableTtransformerPredictWorker."""

    def load_module(self):
        """懒加载模型."""
        cli = getattr(self, "cli", None)
        if cli:
            return cli

        tts = TableTransformerStructure()
        ttd = TableTransformerDetection()
        cli = TableStructurePredict(ttd, tts, (5, 5, 5, 5))
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

        ocr_s3: str = task.input_data.get("ocr_s3", "")
        if not ocr_s3:
            raise TypeError("ocr_s3 not set")

        # 推理表格
        out_s3: str = task.input_data.get("out_s3", "")
        # tables = self.async_run(self.predict(url, ocr_s3))
        tables = []

        logs.append(TaskExecLog("执行完成", task_id, time.time()))
        if out_s3:
            self.put_s3_result(out_s3, {"predict_tables": tables})
        else:
            task_result.add_output_data("predict_tables", tables)
        return task_result

    async def predict(self, url: str, ocr_s3: str):
        """请求模型推理."""
        cli = self.load_module()
        image = await download_image(url)
        tables = await cli.predict(image, ocr_s3, fix_table_boxs=True)
        return [i.dict() for i in tables]
