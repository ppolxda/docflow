# -*- coding: utf-8 -*-
"""
@create: 2021-10-18 22:29:59.

@author: name

@desc: Sqlalchemy to pydantic
"""

from typing import Any
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union

from pydantic import BaseConfig
from pydantic import Field
from pydantic import create_model
from pydantic.fields import FieldInfo
from sqlalchemy import Column
from sqlalchemy.orm import Query
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnClause
from sqlalchemy.sql.elements import Label

from docflow.schemas import BaseModel


class OrmConfig(BaseConfig):
    """OrmConfig."""

    orm_mode = True


def _columns(sql: Union[Select, Query]):
    # sqlalchemy 2.0 will use selected_columns
    if hasattr(sql, "selected_columns"):
        return sql.selected_columns  # type: ignore

    if hasattr(sql, "columns"):
        return sql.columns  # type: ignore

    raise TypeError("Could not found columns")


def __column_to_field(
    column: Union[Column, Label, ColumnClause],
) -> Tuple[Any, FieldInfo]:
    default = None
    python_type: Optional[type] = None

    impl = getattr(column.type, "impl", None)
    if impl:
        python_type = getattr(impl, "python_type", None)
    elif hasattr(column.type, "python_type"):
        python_type = column.type.python_type

    assert python_type, f"Could not infer python_type for {column}"

    if isinstance(column, Column) and column.default is None and not column.nullable:
        default = ...

    comment = getattr(column, "comment", None)

    return (
        python_type,
        Field(description=str(comment) if comment else "", default=default),
    )


# def sqlalchemy_to_pydantic(
#     db_model: Type,
#     *,
#     config: Type = OrmConfig,
#     exclude: Container[str] = [],
# ) -> Type[BaseModel]:
#     """Sqlalchemy to pydantic."""
#     mapper = inspect(db_model)
#     fields = {}
#     for attr in mapper.attrs:
#         if isinstance(attr, ColumnProperty):
#             if attr.columns:
#                 name = attr.key
#                 if name in exclude:
#                     continue
#                 column = attr.columns[0]
#                 fields[name] = __column_to_field(column)

#     pydantic_model = create_model(db_model.__name__, __base__=BaseModel, **fields)
#     return pydantic_model


def sqlalchemy_select_to_pydantic(
    module_name: str,
    sql: Union[Select, Query],
    *,
    config: Type = OrmConfig,
) -> Type[BaseModel]:
    """Select to pydantic."""
    fields = {}
    # sqlalchemy 2.0 will use selected_columns
    columns = _columns(sql)

    for column in columns:
        # sql function has not column name
        if not isinstance(column, (ColumnClause, Label)):
            continue

        name = str(column.key)
        fields[name] = __column_to_field(column)

    pydantic_model = create_model(module_name, __base__=BaseModel, **fields)
    return pydantic_model
