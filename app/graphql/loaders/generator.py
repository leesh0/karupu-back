from functools import lru_cache
from typing import Callable, TypeVar

from strawberry.dataloader import DataLoader

from app.db.table.base import GqlQuerySet

T = TypeVar("T")


class GenLoader:
    @classmethod
    @lru_cache(maxsize=None)
    def loader(
        cls,
        return_model: Callable,
        qs: GqlQuerySet,
        field="id",
        is_list=False,
        factory=lambda x: x.serialize(),
    ):
        async def load_fn(ids):
            gql_type = return_model

            if not is_list:
                objs = await qs.in_bulk(id_list=ids, field_name=field)
                return [gql_type(**factory(objs[_id])) for _id in ids]
            else:
                objs = await qs.list_in_bulk(id_list=ids, field_name=field)
                return [[gql_type(**factory(obj)) for obj in objs[_id]] for _id in ids]

        return DataLoader(load_fn=load_fn, cache=False)
