# -*- coding: utf-8 -*-
"""
@create: 2021-10-18 23:19:55.

@author: name

@desc: 文件功能描述
"""

from typing import Optional
from typing import Sequence
from typing import Tuple

from ..utils.logger import LoggingMixin

# from airflow.utils.session import provide_session
# from airflow.www.utils import CustomSQLAInterface

EXISTING_ROLES = {
    "Admin",
    "User",
    "Public",
}


class DocOcrSecurityManager(LoggingMixin):
    """DocOcrSecurityManager."""

    # USER_PERMISSIONS = [
    #     (permissions.ACTION_CAN_EDIT, permissions.RESOURCE_DAG),
    #     (permissions.ACTION_CAN_DELETE, permissions.RESOURCE_DAG),
    #     (permissions.ACTION_CAN_CREATE, permissions.RESOURCE_TASK_INSTANCE),
    #     (permissions.ACTION_CAN_EDIT, permissions.RESOURCE_TASK_INSTANCE),
    #     (permissions.ACTION_CAN_DELETE, permissions.RESOURCE_TASK_INSTANCE),
    #     (permissions.ACTION_CAN_CREATE, permissions.RESOURCE_DAG_RUN),
    #     (permissions.ACTION_CAN_EDIT, permissions.RESOURCE_DAG_RUN),
    #     (permissions.ACTION_CAN_DELETE, permissions.RESOURCE_DAG_RUN),
    # ]

    # ROLE_CONFIGS = [
    #     {"role": "Public", "perms": []},
    #     {"role": "Viewer", "perms": VIEWER_PERMISSIONS},
    #     {
    #         "role": "User",
    #         "perms": VIEWER_PERMISSIONS + USER_PERMISSIONS,
    #     },
    #     {
    #         "role": "Op",
    #         "perms": VIEWER_PERMISSIONS + USER_PERMISSIONS + OP_PERMISSIONS,
    #     },
    #     {
    #         "role": "Admin",
    #         "perms": VIEWER_PERMISSIONS
    #         + USER_PERMISSIONS
    #         + OP_PERMISSIONS
    #         + ADMIN_PERMISSIONS,
    #     },
    # ]

    # def __init__(self, appbuilder):
    #     super().__init__(appbuilder)

    #     # Go and fix up the SQLAInterface used from the stock one to our subclass.
    #     # This is needed to support the "hack" where we had to edit
    #     # FieldConverter.conversion_table in place in airflow.www.utils
    #     for attr in dir(self):
    #         if not attr.endswith("view"):
    #             continue
    #         view = getattr(self, attr, None)
    #         if not view or not getattr(view, "datamodel", None):
    #             continue
    #         view.datamodel = CustomSQLAInterface(view.datamodel.obj)
    #     self.perms = None

    def has_access(self, permission, resource, user=None) -> bool:
        """has_access."""
        # if not user:
        #     user = g.user

        # if user.is_anonymous:
        #     user.roles = self.get_user_roles(user)

        has_access = True
        # has_access = self._has_view_access(user, permission, resource)
        return has_access

    def check_authorization(
        self,
        perms: Optional[Sequence[Tuple[str, str]]] = None,
        dag_id: Optional[str] = None,
    ) -> bool:
        """检查登录权限.

        Checks that the logged in user has the specified permissions.
        """
        if not perms:
            return True

        for perm in perms:
            if not self.has_access(*perm):
                return False

        return True
