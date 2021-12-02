from cachetools.func import ttl_cache
from strawberry.dataloader import DataLoader


class OptDataLoader:
    def __init__(self, load_class) -> None:
        if not getattr(load_class, "loader"):
            raise AttributeError("loader not found")
        else:
            self.load_class = load_class

    @ttl_cache(maxsize=None, ttl=10)
    def opt(self, **kwargs):
        return DataLoader(self.load_class(**kwargs).loader)
