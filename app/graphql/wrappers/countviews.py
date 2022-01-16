from typing import Generic, List, Optional, Sequence, TypeVar

import strawberry
from strawberry.types import Info
from tortoise.functions import Count

from app.db.table.base import GqlModel

T = TypeVar("T")


@strawberry.type
class Counted(Generic[T]):
    count: Optional[int] = None
    items: List[T] = None
    
    @classmethod
    async def counting(cls, model:GqlModel, relation:str):
        bw_fields = model._meta.backward_fk_fields
        
        if relation not in bw_fields:
            raise ValueError(f"{model} has no {relation} field.")
        
        