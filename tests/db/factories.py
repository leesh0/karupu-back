from app.models.teams import TeamCreateModel

import factory


class TeamFactory(factory.Factory):
    title = factory.Faker("sentence")
    name = factory.Faker("name")
    slug = factory.Faker("slug")
    readme = factory.Faker("paragraph")
    thumbnail = factory.Faker("image_url")
    open = True
    tags = factory.List([factory.Sequence(lambda n: "test" + f"{n}{_}") for _ in range(3)])
    user = None

    class Meta:
        model = TeamCreateModel
