# -*- coding: utf-8 -*-
"""
@create: 2021-10-18 22:40:49.

@author: name

@desc: 用户认证模块
"""

from contextlib import contextmanager
from datetime import timedelta
from typing import List
from typing import Optional

from fastapi import Request
from fastapi.security import SecurityScopes
from fastapi_login import LoginManager
from pydantic import BaseModel as BaseModelBase
from pydantic import Field
from starlette.exceptions import HTTPException

from docflow.clients import get_sessionmaker
from docflow.models.pdfocr_models import OrganizationMemberModel
from docflow.models.pdfocr_models import SysUserModel
from docflow.schemas import BaseModel
from docflow.utils.fileutils import cache_field
from docflow.utils.logger import LoggingMixin

from ..settings import settings


class UserSession(BaseModel):
    """UserSession."""

    user_id: int = Field(0, title="用户id")
    username: str = Field("", title="登录账号")
    password: str = Field("", title="登录密码")
    email: str = Field("", title="邮箱")
    telephone: str = Field("", title="手机号码")
    is_super: bool = Field(False, title="是否超级管理员")
    is_disabled: bool = Field(False, title="是否停用")
    scopes: List[str] = Field(default_factory=list, title="权限值")
    fresh: bool = Field(False, title="token是否刷新过")
    orgids: List[int] = Field(False, title="机构id清单")
    oauth_flag: str = Field("", title="OAuth标识")


class UserToken(BaseModelBase):
    """UserToken."""

    access_token: str = Field("", title="访问token")
    token_type: str = Field("", title="token类型")
    oauth_flag: str = Field("", title="OAuth标识")


# 支持来宾用户
class GuestLoginManager(LoginManager, LoggingMixin):
    """来宾用户管理类."""

    # 来宾用户
    GUEST = UserSession(
        user_id=2,
        username="guest",
        password="",
        email="guest@guest.com",
        telephone="guest",
        is_super=False,
        is_disabled=False,
        fresh=False,
        scopes=["me"],
        orgids=[],
        oauth_flag="",
    )

    def __init__(self, *args, **kwargs):
        """构造函数."""
        super().__init__(*args, **kwargs)
        self._user_callback = self.load_user

    def _get_payload(self, token: str):
        if not token:
            return {"sub": "guest"}

        return super()._get_payload(token)

    def encrypt_password(self, plain_password, salt):
        """加密密码."""
        return self.pwd_context.hash(salt + plain_password)

    def verify_password(self, plain_password, hashed_password, salt):
        """验证密码."""
        return self.pwd_context.verify(salt + plain_password, hashed_password)

    # async def load_user_scopes(self, session: Session, user_id: int) -> List[str]:
    #     result = await db.execute(
    #         select(UserRoleModel.filter_by(user_id=user_id),
    #     )
    #     roles = result.scalars()
    #     return [

    #         for i in
    #     ]

    async def create_guest_user(self):
        """懒创建来宾用户."""
        from docflow.curd.users.users_curd import usercurd

        session_maker = get_sessionmaker()
        with session_maker() as conn:
            rrr = await usercurd.create_guest_user(conn)
            conn.commit()
            return rrr

    # @auth.user_loader
    async def load_user(
        self, username: str, clean_pwd=True, session=None
    ) -> Optional[UserSession]:
        """加载用户信息."""
        if not username or username == "guest":
            username = "guest"
            if settings.DISABLED_GUEST:
                raise self._not_authenticated_exception

        @contextmanager
        def _make_session():
            if session:
                yield session
                return

            session_maker = get_sessionmaker()
            with session_maker() as conn:
                yield conn

        with _make_session() as conn:
            rrr = conn.query(SysUserModel).filter_by(username=username)
            user = rrr.first()
            if not user:
                # 懒创建用户不存在创建来宾用户
                if username == "guest":
                    await self.create_guest_user()
                    rrr = await self.load_user(username, clean_pwd)
                    return rrr
                return None

            # 机构权限
            orgids = conn.query(OrganizationMemberModel).filter_by(user_id=user.user_id)
            orgids = [i.organization_id for i in orgids.all()]

            rrr = UserSession(
                **{
                    **user.to_dict(),
                    "orgids": orgids,
                    "scopes": [],
                    "fresh": False,
                }
            )
            if clean_pwd:
                rrr.password = ""

            # TODO - 写死权限 DocOcr 权限问题，后面需要统一考虑，另外加载方式应该为局域网加载避免性能问题
            rrr.scopes += ["me", "DocOcr"]
            rrr.scopes = list(set(rrr.scopes))
            return rrr

    def has_scopes(self, token: str, required_scopes: SecurityScopes):
        """是否具有接口权限."""
        try:
            payload = self._get_payload(token)
        except Exception:
            return False

        scopes = payload.get("scopes", [])
        if any(scope not in scopes for scope in required_scopes.scopes):
            return False

        return True

    async def _get_token(self, request: Request):
        try:
            token = await super()._get_token(request)
        except HTTPException:
            # TODO - 临时做法，如果程序没有私钥，无法签发
            return self.create_access_token_by_guest()
        else:
            return token

    def refresh_access_token_by_user(self, user: UserSession, expires=None):
        """刷新访问TOKEN."""
        if expires is None:
            expires = settings.AUTH_TOKEN_EXPIRES

        return self.create_access_token(
            data=dict(
                uid=user.user_id,
                sub=user.username,
                scopes=user.scopes,
                fresh=False,
            ),
            expires=timedelta(minutes=expires),
        )

    def create_access_token_by_user(self, user: UserSession, expires=None):
        """创建访问TOKEN."""
        if expires is None:
            expires = settings.AUTH_TOKEN_EXPIRES

        return self.create_access_token(
            data=dict(
                uid=user.user_id,
                sub=user.username,
                scopes=user.scopes,
                fresh=True,
            ),
            expires=timedelta(minutes=expires),
        )

    @cache_field("__guest_token")
    def create_access_token_by_guest(self):
        """创建来宾访问TOKEN."""
        return self.create_access_token_by_user(self.GUEST, expires=24 * 60 * 60 * 60)

    async def __call__(self, request: Request, security_scopes: SecurityScopes):  # pylint: disable=signature-differs
        """检查请求."""
        user = await super().__call__(
            request, security_scopes if security_scopes else SecurityScopes()
        )
        token = await self._get_token(request)
        if token and user:
            payload = self._get_payload(token)
            user.fresh = payload.get("fresh", False)
        return user


auth_mrg = GuestLoginManager(
    settings.AUTH_SECRET,
    token_url=settings.AUTH_TOKEN_URL,
    use_cookie=False,
    scopes={
        "me": "读取用户基础信息",
    },
)
