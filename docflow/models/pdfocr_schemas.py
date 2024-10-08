# -*- coding: utf-8 -*-
"""
Gen schemas.

@author: test

@desc: schemas define
"""

import datetime
import typing
from decimal import Decimal

from pydantic import Field

from ..schemas import BaseModel
from . import pdfocr_enums as enums


def default_date():
    """默认日期工厂."""
    return datetime.date(1900, 1, 1)


def default_datetime():
    """默认时间工厂."""
    return datetime.date(1900, 1, 1)


class SysUserSchemaKey(BaseModel):
    """SysUserSchemaKey."""

    user_id: int = Field(0, title="用户id")  # noqa


class SysUserSchemaCreate(BaseModel):
    """SysUserSchemaCreate."""

    username: str = Field("", title="登录账号")  # noqa
    password: str = Field("", title="登录密码")  # noqa
    email: str = Field("", title="邮箱")  # noqa
    phone: str = Field("", title="手机号码")  # noqa
    name: str = Field("", title="用户名")  # noqa
    is_super: bool = Field(False, title="是否超级管理员")  # noqa
    is_disabled: bool = Field(False, title="是否停用")  # noqa
    last_login: datetime.datetime = Field(
        default_factory=default_datetime, title="最后登录时间"
    )  # noqa
    login_count: int = Field(0, title="登录次数")  # noqa
    fail_login_count: int = Field(0, title="登录失败次数")  # noqa
    icon: str = Field("", title="图标路径")  # noqa
    external_id: str = Field("", title="用户外部标识")  # noqa
    oauth_flag: str = Field("", title="OAuth标识")  # noqa


class SysUserSchemaCreateIgnore(BaseModel):
    """SysUserSchemaCreateIgnore."""


class SysUserSchema(SysUserSchemaKey, SysUserSchemaCreate, SysUserSchemaCreateIgnore):  # noqa
    """SysUserSchema."""


class SysUserSchemaModify(SysUserSchemaKey):
    """SysUserSchemaModify."""


class SysUserSchemaDelete(BaseModel):
    """SysUserSchemaDelete."""

    ids: typing.List[SysUserSchemaKey]
    include_children: bool = Field(False, title="是否包含子类")


class SysUserSchemaInsert(SysUserSchemaCreate, SysUserSchemaCreateIgnore):  # noqa
    """SysUserSchema."""


class SysApplicationsSchemaKey(BaseModel):
    """SysApplicationsSchemaKey."""

    app_key: str = Field("", title="应用标识")  # noqa


class SysApplicationsSchemaCreate(BaseModel):
    """SysApplicationsSchemaCreate."""

    app_name: str = Field("", title="应用名称")  # noqa
    app_secret: str = Field("", title="应用密钥")  # noqa
    app_scopes: typing.List[str] = Field(default_factory=list, title="应用权限")  # noqa
    user_id: int = Field(0, title="用户id")  # noqa


class SysApplicationsSchemaCreateIgnore(BaseModel):
    """SysApplicationsSchemaCreateIgnore."""


class SysApplicationsSchema(
    SysApplicationsSchemaKey,
    SysApplicationsSchemaCreate,
    SysApplicationsSchemaCreateIgnore,
):  # noqa
    """SysApplicationsSchema."""


class SysApplicationsSchemaModify(SysApplicationsSchemaKey):
    """SysApplicationsSchemaModify."""


class SysApplicationsSchemaDelete(BaseModel):
    """SysApplicationsSchemaDelete."""

    ids: typing.List[SysApplicationsSchemaKey]
    include_children: bool = Field(False, title="是否包含子类")


class SysApplicationsSchemaInsert(
    SysApplicationsSchemaCreate, SysApplicationsSchemaCreateIgnore
):  # noqa
    """SysApplicationsSchema."""


class OrganizationSchemaKey(BaseModel):
    """OrganizationSchemaKey."""

    organization_id: int = Field(0, title="机构id")  # noqa


class OrganizationSchemaCreate(BaseModel):
    """OrganizationSchemaCreate."""

    name: str = Field("", title="机构名称")  # noqa
    token: str = Field("", title="授权令牌")  # noqa


class OrganizationSchemaCreateIgnore(BaseModel):
    """OrganizationSchemaCreateIgnore."""


class OrganizationSchema(
    OrganizationSchemaKey, OrganizationSchemaCreate, OrganizationSchemaCreateIgnore
):  # noqa
    """OrganizationSchema."""


class OrganizationSchemaModify(OrganizationSchemaKey):
    """OrganizationSchemaModify."""


class OrganizationSchemaDelete(BaseModel):
    """OrganizationSchemaDelete."""

    ids: typing.List[OrganizationSchemaKey]
    include_children: bool = Field(False, title="是否包含子类")


class OrganizationSchemaInsert(
    OrganizationSchemaCreate, OrganizationSchemaCreateIgnore
):  # noqa
    """OrganizationSchema."""


class OrganizationMemberSchemaKey(BaseModel):
    """OrganizationMemberSchemaKey."""

    organization_id: int = Field(0, title="机构id")  # noqa
    user_id: int = Field(0, title="用户id")  # noqa


class OrganizationMemberSchemaCreate(BaseModel):
    """OrganizationMemberSchemaCreate."""


class OrganizationMemberSchemaCreateIgnore(BaseModel):
    """OrganizationMemberSchemaCreateIgnore."""


class OrganizationMemberSchema(
    OrganizationMemberSchemaKey,
    OrganizationMemberSchemaCreate,
    OrganizationMemberSchemaCreateIgnore,
):  # noqa
    """OrganizationMemberSchema."""


class OrganizationMemberSchemaModify(OrganizationMemberSchemaKey):
    """OrganizationMemberSchemaModify."""


class OrganizationMemberSchemaDelete(BaseModel):
    """OrganizationMemberSchemaDelete."""

    ids: typing.List[OrganizationMemberSchemaKey]
    include_children: bool = Field(False, title="是否包含子类")


class OrganizationMemberSchemaInsert(
    OrganizationMemberSchemaCreate, OrganizationMemberSchemaCreateIgnore
):  # noqa
    """OrganizationMemberSchema."""
