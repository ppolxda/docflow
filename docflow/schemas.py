# -*- coding: utf-8 -*-
"""
@create: 2022-07-22 17:48:08.

@author: name

@desc: Base Model
"""
from datetime import date
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any
from typing import Generic
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import TypeVar

import pydantic
from humps.main import camelize
from pydantic import Field
from pydantic import generics
from pydantic.typing import is_namedtuple
from pydantic.utils import sequence_like

DataT = TypeVar("DataT")
PageType = List[int]
SortType = List[List[str]]
RspData = TypeVar("RspData", bound=pydantic.BaseModel)
RspTotal = TypeVar("RspTotal", bound=pydantic.BaseModel)


def default_date():
    """默认日期工厂."""
    return date(1900, 1, 1)


def default_datetime():
    """默认时间工厂."""
    return datetime(1900, 1, 1)


class EnumQuerySort(str, Enum):
    """排序枚举."""

    ASC = "asc"
    DESC = "desc"


class BaseModel(pydantic.BaseModel):
    """BaseModel."""

    @classmethod
    def _get_dict_value(cls, val) -> Any:
        if isinstance(val, dict):
            return {
                k_: cls._get_dict_value(v_)
                for k_, v_ in val.items()
                if k_ not in ["_sa_instance_state"]
            }

        elif sequence_like(val):
            seq_args = (cls._get_dict_value(v_) for v_ in val)
            return (
                val.__class__(*seq_args)
                if is_namedtuple(val.__class__)
                else val.__class__(seq_args)
            )

        elif isinstance(val, Enum):
            return val.value
        elif isinstance(val, Decimal):
            return float(val)
        elif isinstance(val, date):
            return str(val)
        else:
            return val

    @classmethod
    def _iter_dict(cls, data: dict):
        for (
            field_key,
            v,
        ) in data.items():
            if field_key in ["_sa_instance_state"]:
                continue

            v = cls._get_dict_value(v)
            yield field_key, v

    def to_raw_dict(
        self,
        *,
        include=None,
        exclude=None,
        by_alias: bool = False,
        skip_defaults: Optional[bool] = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ):
        """统一转换方法."""
        rrr = self.dict(
            # to_dict=True,
            by_alias=by_alias,
            include=include,
            exclude=exclude,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )
        return dict(self._iter_dict(rrr))

    class Config:
        """Config."""

        orm_mode = True
        alias_generator = camelize
        allow_population_by_field_name = True
        # use_enum_values = True


class GenericModel(generics.GenericModel):
    """GenericModel."""

    class Config:
        """Config."""

        alias_generator = camelize
        allow_population_by_field_name = True
        # use_enum_values = True


class ErrorResponse(BaseModel):
    """Error Response."""

    error: str = Field(title="Error message")


class SucessResponse(BaseModel):
    """Sucess Response."""


class DataResponse(ErrorResponse, GenericModel, Generic[DataT]):
    """Data Response."""

    data: DataT = Field(title="Data")

    @classmethod
    def __concrete_name__(cls: Type[Any], params: Tuple[Type[Any], ...]) -> str:
        """__concrete_name__."""
        return f"{params[0].__name__.title()}Response"


class ListResponse(ErrorResponse, GenericModel, Generic[DataT]):
    """List Response."""

    data: List[DataT] = Field(title="Data")

    @classmethod
    def __concrete_name__(cls: Type[Any], params: Tuple[Type[Any], ...]) -> str:
        """__concrete_name__."""
        return f"{params[0].__name__.title()}Response"


class QueryEmptyTotalSchemas(BaseModel):
    """QueryEmptyTotalSchemas."""


class QueryRequest(BaseModel):
    """QueryRequest."""

    where: dict = Field(default_factory=dict, title="查询条件")
    sort: SortType = Field(default_factory=list, title="查询排序")
    page: PageType = Field(default_factory=list, title="查询分页")

    # @property
    # def decamelize_sort(self):
    #     """decamelize_sort."""
    #     return list(map(lambda x: (decamelize(x[0]), x[1]), self.sort))


class SearchRequest(BaseModel):
    """SearchRequest."""

    query: str = Field("", title="查询条件")
    # sort: SortType = Field(default_factory=list, title="查询排序")
    page: PageType = Field(default_factory=list, title="查询分页")


class QueryTotalResponse(GenericModel, Generic[RspData, RspTotal]):
    """QueryTotalResponse."""

    total: RspTotal = Field(default_factory=dict, title="query field sum total")
    count: int = Field(0, title="query count total")
    data: List[RspData] = Field(default_factory=list, title="query result")

    @classmethod
    def __concrete_name__(cls: Type[Any], params: Tuple[Type[Any], ...]) -> str:
        """类名构造."""
        return f"QueryTotalResponse«{params[0].__name__}, {params[1].__name__}»"  # type: ignore


class QueryResponse(QueryTotalResponse[RspData, QueryEmptyTotalSchemas]):
    """QueryResponse."""

    @classmethod
    def __concrete_name__(cls: Type[Any], params: Tuple[Type[Any], ...]) -> str:
        """类名构造."""
        return f"QueryResponse«{params[0].__name__}»"
