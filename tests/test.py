from timeit import timeit

from cachetools.func import ttl_cache


class OptDataLoader:
    def __init__(self, load_class) -> None:
        if not getattr(load_class, "loader"):
            raise AttributeError("loader not found")
        else:
            self.load_class = load_class

    @ttl_cache(maxsize=None, ttl=10)
    def opt(self, **kwargs):
        print("AAA")
        return self.load_class(**kwargs).loader


class TestLoader:
    def __init__(self, sq: str) -> None:
        self.sq = sq

    def loader(self, idx):
        print(idx)


loader = OptDataLoader(load_class=TestLoader)

for i in range(1000):
    loader.opt(sq=i % 5)
