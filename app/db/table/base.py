from collections import defaultdict
from copy import copy
from typing import Any, Dict, Iterable, Type, Union

from pydantic import BaseModel
from pypika import Table
from pypika.functions import Count
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.manager import Manager
from tortoise.models import MODEL, MetaInfo, Model
from tortoise.queryset import AwaitableQuery, CountQuery, QuerySet, RawSQLQuery


class GqlCountQuery(CountQuery):
    def __init__(self, field=None, distinct=False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.field = field
        self.distict = distinct

    def _make_query(self) -> None:
        self.query = copy(self.model._meta.basequery)
        self.resolve_filters(
            model=self.model,
            q_objects=self.q_objects,
            annotations=self.annotations,
            custom_filters=self.custom_filters,
        )

        count_obj = Count("*")
        if self.field:
            field_p = self.field.split("__")
            if len(field_p) > 1:
                table = Table("__".join(field_p[:-1]))
                self.field = field_p[-1]
            else:
                table = Table(self.model.table_name())
            count_obj = Count(getattr(table, self.field))
        if self.distict:
            count_obj = count_obj.distinct()

        self.query._select_other(count_obj)

        if self.force_indexes:
            self.query._force_indexes = []
            self.query = self.query.force_index(*self.force_indexes)
        if self.use_indexes:
            self.query._use_indexes = []
            self.query = self.query.use_index(*self.use_indexes)

    async def _execute(self) -> int:
        _, result = await self._db.execute_query(str(self.query))
        count = list(dict(result[0]).values())[0]
        return count


class GqlRawQuerySet(RawSQLQuery):
    def __init__(self, model: Type[MODEL], db, sql: str, custom_fields: Iterable = None):
        super(GqlRawQuerySet.__bases__[0], self).__init__(model)
        self._sql = sql
        self._db = db
        self._custom_fields = custom_fields

    async def _execute(self) -> Any:
        instance_list = await self._db.executor_class(
            model=self.model,
            db=self._db,
        ).execute_select(self.query, custom_fields=self._custom_fields)
        return instance_list


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

    def raw(self, sql: str, custom_fields: Iterable = None) -> "RawSQLQuery":
        return GqlRawQuerySet(model=self.model, db=self._db, sql=sql, custom_fields=custom_fields)

    def total_count(self, field=None) -> "GqlCountQuery":
        if not field:
            field = self.model._meta.db_pk_column
        return GqlCountQuery(
            db=self._db,
            model=self.model,
            q_objects=self._q_objects,
            annotations=self._annotations,
            custom_filters=self._custom_filters,
            limit=self._limit,
            offset=self._offset,
            force_indexes=self._force_indexes,
            use_indexes=self._use_indexes,
            field=field,
            distinct=self._distinct,
        )


class GqlManager(Manager):
    def get_queryset(self) -> GqlQuerySet:
        return GqlQuerySet(self._model)


class GqlMetaInfo(MetaInfo):
    def __init__(self, meta: "Model.Meta") -> None:
        super().__init__(meta)
        self.manager = GqlManager()


class GqlModel(Model):
    _meta = GqlMetaInfo(None)

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
    def table_name(cls):
        return cls._meta.db_table

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

    @classmethod
    def raw(cls, sql: str, custom_fields: Iterable = None):
        return cls.gql.get_queryset().raw(sql, custom_fields)

    class Meta:
        manager = GqlManager()
