# -*- coding: utf-8 -*-
"""
@create: 2022-11-17 15:32:13.

@author: ppolxda

@desc: 数据库基类
"""

from sqlalchemy.orm import declarative_base

# from sqlalchemy.orm import declared_attr
# from sqlalchemy import MetaData


def conv_dict(val):
    """转换字典."""
    # TODO - 临时解决方案，不是靠谱，并且性能差
    if isinstance(val, list):
        return [conv_dict(i) for i in val]
    elif isinstance(val, dict):
        return {key: conv_dict(_val) for key, _val in val.items()}
    elif isinstance(val, Base):
        return val.to_dict()
    elif b"\x00" == val:
        return False
    elif b"\x01" == val:
        return True
    else:
        return val


def to_dict(self, include=None, exclude=None):
    """转换字典."""
    if include is None:
        include = []

    if exclude is None:
        exclude = []

    return {
        c.key: conv_dict(getattr(self, c.key, None))
        for c in self.__mapper__._polymorphic_properties
        if not (exclude and c.key in exclude) and not (include and c.key not in include)
    }


# metadata = (
#     None
#     if not SQL_ALCHEMY_SCHEMA or SQL_ALCHEMY_SCHEMA.isspace()
#     else MetaData(schema=SQL_ALCHEMY_SCHEMA)
# )
Base = declarative_base()
setattr(Base, "to_dict", to_dict)
# Base.__dict__ = to_dict


# class IntEnum(sqlalchemy.types.TypeDecorator):
#     """IntEnum."""

#     impl = sqlalchemy.Integer

#     def __init__(self, enumtype, *args, **kwargs):
#         """构造函数."""
#         super().__init__(*args, **kwargs)
#         self._enumtype = enumtype

#     def process_bind_param(self, value, dialect):
#         """枚举转换."""
#         if isinstance(value, Enum):
#             return value.value
#         else:
#             return value

#     def process_result_value(self, value, dialect):
#         """IntEnum."""
#         return self._enumtype(value)
