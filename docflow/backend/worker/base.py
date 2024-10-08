# -*- coding: utf-8 -*-
"""
@create: 2023-05-29 17:34:30.

@author: ppolxda

@desc: conductor 工作者封装
"""

import abc
import json
import time
from typing import List

import requests
from docflow.backend.settings import settings
from conductor.client.automator.task_handler import WorkerInterface
from conductor.client.http.models.task_exec_log import TaskExecLog
from conductor.client.worker.worker import Task
from conductor.client.worker.worker import TaskResult
from conductor.client.worker.worker import TaskResultStatus

from .sync_to_async import get_loop
from .sync_to_async import sync


class ConductorWorker(WorkerInterface):
    """PredictPythonWorker."""

    def async_run(self, async_callback):
        """异步执行."""
        loop = get_loop()
        tokens = sync(loop, async_callback)
        return tokens

    def get_polling_interval_in_seconds(self) -> float:
        """拉取消息延时."""
        return settings.CONDUCTOR_WORKER_INTERVAL

    def get_domain(self):
        """配置隔离域Domain."""
        return (
            settings.CONDUCTOR_WORKER_DOMAIN_AI
            if settings.CONDUCTOR_WORKER_DOMAIN_AI
            else None
        )

    def execute(self, task: Task) -> TaskResult:
        """执行任务."""
        assert isinstance(task.input_data, dict)
        logs = []
        task_result: TaskResult = self.get_task_result_from_task(task)
        task_id = task.task_id
        task_result.logs = logs
        try:
            self.execute_(task, task_result, logs)
        except Exception as ex:  # pylint: disable=broad-except
            logs.append(TaskExecLog(str(ex), task_id, time.time()))
            task_result.logs = logs
            task_result.reason_for_incompletion = str(ex)
            task_result.status = TaskResultStatus.FAILED
            return task_result
        else:
            task_result.status = TaskResultStatus.COMPLETED
            return task_result

    @abc.abstractmethod
    def execute_(
        self, task: Task, task_result: TaskResult, logs: List[TaskExecLog]
    ) -> TaskResult:
        """执行任务."""
        raise NotImplementedError

    def put_s3_result(self, url: str, data: dict):
        """回写结果集."""
        rsp_put = requests.put(
            url,
            data=json.dumps(data),
            headers={
                "Content-Type": "application/json",
            },
            timeout=settings.CONDUCTOR_API_TIMEOUT,
        )
        if rsp_put.status_code != 200:
            raise TypeError("写入结果文件失败")
