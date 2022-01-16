from cachetools.func import lru_cache
from strawberry.dataloader import DataLoader


class OptDataLoader:
    def __init__(self, load_class, cache=False) -> None:
        if not getattr(load_class, "loader"):
            raise AttributeError("loader not found")
        else:
            self.load_class = load_class
        self.cache = cache

    @lru_cache(maxsize=None)
    def opt(self, **kwargs):
        return DataLoader(load_fn=self.load_class(**kwargs).loader, cache=self.cache)


class OptLoaderBase:
    def __init__(self, **kwargs) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)

    async def loader(self, *args, **kwargs):
        raise NotImplementedError
