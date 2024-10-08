# -*- coding: utf-8 -*-
"""
@create: 2022-12-07 20:05:27.

@author: ppolxda

@desc: Amqp客户端
"""

import asyncio
import json
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from typing import Optional
from uuid import uuid4

import aio_pika
from aio_pika import DeliveryMode
from aio_pika.abc import AbstractChannel
from aio_pika.abc import AbstractExchange
from aio_pika.abc import AbstractRobustConnection
from aio_pika.abc import DateType

from docflow.models.pdfocr_enums import EnumExportDatasetsType

from .logger import LOGGER


class AMQPHandler:
    """AMQPHandler."""

    QUEUE_NAME = "pdfocr"

    def __init__(
        self,
        amqp_url: str,
        app_id: str,
        default_queue_name: str,
        queue_range=2,
        timeout=10,
    ):
        """构造函数."""
        self.app_id = app_id
        self.amqp_url = amqp_url
        self.queue_range = queue_range
        self.default_queue_name = default_queue_name
        self.connection_: Optional[AbstractRobustConnection] = None
        self.channel_: Optional[AbstractChannel] = None
        self.exchange_: Optional[AbstractExchange] = None
        self.timeout = timeout

    @property
    def connection(self) -> AbstractRobustConnection:
        """Amqp连接."""
        if not self.connection_:
            raise TypeError("module not init")
        return self.connection_

    @property
    def channel(self) -> AbstractChannel:
        """Amqp连接."""
        if not self.channel_:
            raise TypeError("module not init")
        return self.channel_

    @property
    def exchange(self) -> AbstractExchange:
        """Amqp连接."""
        if not self.exchange_:
            raise TypeError("module not init")
        return self.exchange_

    async def init(self):
        """初始化函数."""
        self.connection_ = await aio_pika.connect_robust(self.amqp_url)
        self.channel_ = await self.connection.channel(publisher_confirms=False)
        # await self.channel.set_qos(prefetch_count=100)
        self.exchange_ = await self.channel.declare_exchange(
            self.default_queue_name, aio_pika.ExchangeType.FANOUT, durable=True
        )
        for i in range(self.queue_range):
            queue = await self.channel.declare_queue(
                name=f"{self.default_queue_name}_{i}", durable=True
            )
            await queue.bind(self.exchange_)

    async def publish(
        self,
        data: dict,
        message_id=None,
        expiration: Optional[DateType] = None,
        timeout=None,
    ):
        """推送消息."""
        if message_id is None:
            message_id = str(uuid4())

        if timeout is None:
            timeout = self.timeout

        message_ = json.dumps(data)

        LOGGER.info("publish a")
        try:
            await asyncio.wait_for(
                self.exchange.publish(
                    aio_pika.Message(
                        message_.encode(),
                        app_id=self.app_id,
                        content_type="application/json",
                        message_id=message_id,
                        expiration=expiration,
                        delivery_mode=DeliveryMode.PERSISTENT,
                    ),
                    self.default_queue_name,
                    mandatory=False,
                    timeout=timeout,
                ),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            LOGGER.info("timeout!")
        finally:
            LOGGER.info("publish b")


@dataclass
class TaskAyncEvent:
    """WebhookEvent."""

    project_id: int = 0  # 关联项目id
    action: str = ""  # 事件类型
    service: str = ""  # 后端服务地址（测试用）
    payload: dict = field(default_factory=dict)  # 事件类型


class AMQPAynscTaskHandler:
    """异步任务."""

    QUEUE_NAME = "pdfocr"

    def __init__(
        self, client: AMQPHandler, service: str, domain: str, enable: bool = True
    ) -> None:
        """初始化."""
        self.client = client
        self.service = service
        self.domain = domain
        self.enable = enable

    async def create_summary_task(self, project_id: int, modify_uid: int):
        """创建异步任务."""
        if not self.enable:
            return

        task = TaskAyncEvent(
            project_id=project_id,
            action="TASK_SUMMARY",
            service=self.service,
            payload={
                "domain": self.domain,
                "project_id": project_id,
                "modify_uid": modify_uid,
            },
        )
        await self.client.publish(asdict(task))

    async def create_member_task(self, project_id: int, modify_uid: int):
        """创建异步任务."""
        if not self.enable:
            return

        task = TaskAyncEvent(
            project_id=project_id,
            action="TASK_MEMBER",
            service=self.service,
            payload={
                "domain": self.domain,
                "project_id": project_id,
                "modify_uid": modify_uid,
            },
        )
        await self.client.publish(asdict(task))

    async def create_export_task(
        self, project_id: int, datasets_type: EnumExportDatasetsType, export_id: int
    ):
        """创建异步导出任务."""
        if not self.enable:
            return

        task = TaskAyncEvent(
            project_id=project_id,
            action="TASK_EXPORT",
            service=self.service,
            payload={
                "domain": self.domain,
                "project_id": project_id,
                "datasets_type": datasets_type,
                "export_id": export_id,
            },
        )
        await self.client.publish(asdict(task))
