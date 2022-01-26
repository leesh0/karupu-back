from typing import Generic, List, Optional, Sequence, TypeVar

import strawberry
from aiocache import cached
from strawberry.types import Info
from tortoise.functions import Count

from app.db.table.base import GqlModel, GqlQuerySet
from app.helpers import RuntimeGeneric

T = TypeVar("T")


@strawberry.type
class Pagination(RuntimeGeneric, Generic[T]):
    count: Optional[int] = None
    items: List[T] = None

    @classmethod
    async def paginate(cls, data: GqlQuerySet, offset: int = 0, limit: int = 30):
        total_count = await data.total_count()
        rscs = await data.offset(offset).limit(limit)
        if not isinstance(rscs, list) and rscs:
            rscs = [rscs]
        elif not rscs:
            rscs = []

        gql_type = cls.__args__[0]

        items = [gql_type(**rsc.serialize()) for rsc in rscs]
        return cls(count=total_count, items=items)
