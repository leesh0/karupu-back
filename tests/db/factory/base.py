import asyncio
from typing import Callable

from faker.factory import Factory

Faker = Factory.create
faker = Faker(locale="ja-jp")
faker.seed(0)


class Gen:
    def __init__(self, provider: str, key=None, **kwargs) -> None:
        self._provider = provider
        self._key = key
        self._kwargs = kwargs

    def __call__(self):
        call = getattr(faker, self._provider)
        if self._key:
            return call(**self._kwargs)[self._key]
        else:
            return call(**self._kwargs)


class Factory:
    class Meta:
        model: object

    @classmethod
    def _fields_map(cls) -> dict:
        return {k: v for k, v in cls.__dict__.items() if not k.startswith("_")}

    @classmethod
    def _loader(cls):
        return {k: v() if isinstance(v, Callable) else v for k, v in cls._fields_map().items()}

    @classmethod
    async def _load_and_save(cls, **kwargs):
        loaded: dict = cls._loader()

        if kwargs:
            for k, v in kwargs.items():
                loaded[k] = v

        model = cls.Meta.model
        save_model = model(**loaded)

        await save_model.save()
        return save_model

    @classmethod
    async def create(cls, n=1, **kwargs):
        tasks = [cls._load_and_save(**kwargs) for i in range(n)]
        result = await asyncio.gather(*tasks)

        if n == 1:
            return result[0]
        else:
            return result
