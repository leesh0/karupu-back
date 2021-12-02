from collections import defaultdict
from typing import Any, Dict, Iterable, Type, Union

from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.manager import Manager
from tortoise.models import MODEL, MetaInfo, Model
from tortoise.queryset import QuerySet


class GqlQuerySet(QuerySet):
    async def list_in_bulk(
        self, id_list: Iterable[Union[str, int]], field_name: str
    ) -> Dict[Any, MODEL]:
        obj_map = defaultdict(list)
        objs = await self.filter(**{f"{field_name}__in": id_list})
        for obj in objs:
            map_key = getattr(obj, field_name)
            obj_map[map_key].append(obj)
        return obj_map

    async def values_in_bulk(
        self, id_list: Iterable[Union[str, int]], idx: str, v: str
    ) -> Dict[Any, Any]:
        obj_map = defa


class GqlManager(Manager):
    def get_queryset(self) -> GqlQuerySet:
        return GqlQuerySet(self._model)


class GqlModel(Model):

    gql: GqlQuerySet = GqlManager()

    @classmethod
    def pydantic(cls):
        return pydantic_model_creator(cls)

    def serialize(self):
        hide_fields = self._meta.fk_fields.union(self._meta.backward_fk_fields)
        return {
            field: getattr(self, field) for field in self._meta.fields if field not in hide_fields
        }

    def fit(self, model: BaseModel) -> BaseModel:
        model_fields = model.__dict__.keys()
        return model(**{field: getattr(self, field, None) for field in model_fields})

    @classmethod
    async def list_in_bulk(
        cls: Type[MODEL], id_list: Iterable[Union[str, int]], field_name: str = "pk"
    ) -> Dict[str, MODEL]:
        """
        Return a dictionary mapping each of the given IDs to the object with
        that ID. If `id_list` isn't provided, evaluate the entire QuerySet.

        :param id_list: A list of field values
        :param field_name: Must be a unique field
        """
        return await cls.gql.list_in_bulk(id_list, field_name)

    class Meta:
        manager = GqlManager()
