# -*- coding: utf-8 -*-
"""
Gen models.

@author: models

@desc: models define
"""

from datetime import date
from datetime import datetime
from decimal import Decimal
from typing import List
from typing import Union

import sqlalchemy as sa
from sqlalchemy import ARRAY
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import UniqueConstraint
from sqlalchemy import text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column  # type: ignore
from sqlalchemy.sql import func

from . import pdfocr_enums as enums
from .base import Base

# pylint: disable=line-too-long


def default_date():
    """默认日期工厂类."""
    return date(1900, 1, 1)


def default_datetime():
    """默认时间工厂类."""
    return datetime(1900, 1, 1)


class SysUserModel(Base):
    """SysUserModel."""

    __tablename__ = "sys_user"
    created_at: Mapped[datetime] = mapped_column(
        "created_at",
        sa.DateTime,
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )  # type: ignore
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at",
        sa.TIMESTAMP,
        server_default=func.now(),
        nullable=False,
        onupdate=func.current_timestamp(),
        comment="更新时间",
    )  # type: ignore
    user_id: Mapped[int] = mapped_column(
        "user_id",
        sa.Integer,
        comment="用户id",
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )  # type: ignore
    username: Mapped[str] = mapped_column(
        "username",
        sa.String(32),
        default=str,
        server_default="",
        comment="登录账号",
        nullable=False,
    )  # type: ignore
    password: Mapped[str] = mapped_column(
        "password",
        sa.String(128),
        default=str,
        server_default="",
        comment="登录密码",
        nullable=False,
    )  # type: ignore
    email: Mapped[str] = mapped_column(
        "email",
        sa.String(32),
        default=str,
        server_default="",
        comment="邮箱",
        nullable=False,
    )  # type: ignore
    phone: Mapped[str] = mapped_column(
        "phone",
        sa.String(24),
        default=str,
        server_default="",
        comment="手机号码",
        nullable=False,
    )  # type: ignore
    name: Mapped[str] = mapped_column(
        "name",
        sa.String(128),
        default=str,
        server_default="",
        comment="用户名",
        nullable=False,
    )  # type: ignore
    is_super: Mapped[bool] = mapped_column(
        "is_super",
        sa.Boolean,
        default=bool,
        server_default="false",
        comment="是否超级管理员",
        nullable=False,
    )  # type: ignore
    is_disabled: Mapped[bool] = mapped_column(
        "is_disabled",
        sa.Boolean,
        default=bool,
        server_default="false",
        comment="是否停用",
        nullable=False,
    )  # type: ignore
    last_login: Mapped[datetime] = mapped_column(
        "last_login",
        sa.DateTime,
        default=default_datetime,
        server_default="1900-01-01",
        comment="最后登录时间",
        nullable=False,
    )  # type: ignore
    login_count: Mapped[int] = mapped_column(
        "login_count",
        sa.Integer,
        default=int,
        server_default="0",
        comment="登录次数",
        nullable=False,
    )  # type: ignore
    fail_login_count: Mapped[int] = mapped_column(
        "fail_login_count",
        sa.Integer,
        default=int,
        server_default="0",
        comment="登录失败次数",
        nullable=False,
    )  # type: ignore
    icon: Mapped[str] = mapped_column(
        "icon",
        sa.String(256),
        default=str,
        server_default="",
        comment="图标路径",
        nullable=False,
    )  # type: ignore
    external_id: Mapped[str] = mapped_column(
        "external_id",
        sa.String(64),
        default=str,
        server_default="",
        comment="用户外部标识",
        nullable=False,
    )  # type: ignore
    oauth_flag: Mapped[str] = mapped_column(
        "oauth_flag",
        sa.String(16),
        default=str,
        server_default="",
        comment="OAuth标识",
        nullable=False,
    )  # type: ignore
    __table_args__ = (
        Index("idx_u_username_index", username),  # type: ignore
        Index("idx_u_email_index", email),  # type: ignore
        Index("idx_u_phone_index", phone),  # type: ignore
    )


class OrganizationModel(Base):
    """OrganizationModel."""

    __tablename__ = "organization"
    created_at: Mapped[datetime] = mapped_column(
        "created_at",
        sa.DateTime,
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )  # type: ignore
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at",
        sa.TIMESTAMP,
        server_default=func.now(),
        nullable=False,
        onupdate=func.current_timestamp(),
        comment="更新时间",
    )  # type: ignore
    organization_id: Mapped[int] = mapped_column(
        "organization_id",
        sa.Integer,
        comment="机构id",
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )  # type: ignore
    name: Mapped[str] = mapped_column(
        "name",
        sa.String(64),
        default=str,
        server_default="",
        comment="机构名称",
        nullable=False,
    )  # type: ignore
    token: Mapped[str] = mapped_column(
        "token",
        sa.String(64),
        default=str,
        server_default="",
        comment="授权令牌",
        nullable=False,
    )  # type: ignore
    __table_args__ = (UniqueConstraint(token, name="idx_token_unique"),)  # type: ignore


class OrganizationMemberModel(Base):
    """OrganizationMemberModel."""

    __tablename__ = "organization_member"
    created_at: Mapped[datetime] = mapped_column(
        "created_at",
        sa.DateTime,
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )  # type: ignore
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at",
        sa.TIMESTAMP,
        server_default=func.now(),
        nullable=False,
        onupdate=func.current_timestamp(),
        comment="更新时间",
    )  # type: ignore
    organization_id: Mapped[int] = mapped_column(
        "organization_id",
        sa.Integer,
        ForeignKey(
            "organization.organization_id",
            name="fdx_orgin_foreign",
            onupdate="NO ACTION",
            ondelete="NO ACTION",
        ),
        default=int,
        server_default="0",
        comment="机构id",
        primary_key=True,
        nullable=False,
    )  # type: ignore
    user_id: Mapped[int] = mapped_column(
        "user_id",
        sa.Integer,
        ForeignKey(
            "sys_user.user_id",
            name="fdx_userid_foreign",
            onupdate="NO ACTION",
            ondelete="NO ACTION",
        ),
        default=int,
        server_default="0",
        comment="用户id",
        primary_key=True,
        nullable=False,
    )  # type: ignore
