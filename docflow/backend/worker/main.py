# -*- coding: utf-8 -*-
"""
@create: 2023-05-29 17:44:59.

@author: ppolxda

@desc: conductor 工作者
"""
import logging
from logging import config
from typing import List

import click
import torch.multiprocessing as mp
from conductor.client.automator.task_handler import MetricsSettings
from conductor.client.automator.task_handler import TaskHandler
from conductor.client.automator.task_handler import TaskRunner
from conductor.client.configuration.configuration import Configuration
from conductor.client.worker.worker_interface import WorkerInterface

from ..settings import settings
from .keyinfo_worker import KeyinfoPredictWorker
from .pdfclasss_worker import PdfclassBertPredictWorker
from .pdfclasss_worker import PdfclassPredictWorker
from .pdfside_worker import PdfSidePredictWorker
from .table_worker import TableTransformerPredictWorker

LOGGER = logging.getLogger()


class TorchTaskHandler(TaskHandler):
    """TorchTaskHandler."""

    def __create_task_runner_process(  # pylint: disable=unused-private-member
        self,
        worker: WorkerInterface,
        configuration: Configuration,
        metrics_settings: MetricsSettings,
    ) -> None:
        task_runner = TaskRunner(worker, configuration, metrics_settings)
        process = mp.Process(target=task_runner.run)
        self.task_runner_processes.append(process)


@click.command()
@click.option("--logging_conf", default="./logging.conf", help="日志配置")
def main(logging_conf):
    """主函数."""
    config.fileConfig(logging_conf, disable_existing_loggers=True)
    mp.set_start_method("spawn", force=True)

    workers: List[WorkerInterface] = [
        PdfSidePredictWorker(task_definition_name="worker_图像方向识别"),
        KeyinfoPredictWorker(task_definition_name="worker_图片关键信息识别"),
        PdfclassPredictWorker(task_definition_name="worker_图片类型识别"),
        PdfclassBertPredictWorker(task_definition_name="worker_图片类型识别Bert"),
        TableTransformerPredictWorker(task_definition_name="worker_表格识别"),
    ]
    capi = settings.CONDUCTOR_API
    if capi.endswith("/"):
        capi = capi[:-1]

    LOGGER.info("service start with %s", capi)

    configuration = Configuration(
        server_api_url=capi + "/api", debug=settings.CONDUCTOR_WORKER_DEBUG
    )
    with TorchTaskHandler(workers, configuration) as task_handler:
        task_handler.start_processes()
        task_handler.join_processes()


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
