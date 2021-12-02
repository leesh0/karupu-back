from typing import List

import strawberry
from app.db.table import karupu as models
from app.graphql.types import Project
from strawberry.types import Info
from tortoise.expressions import F, Subquery


@strawberry.type
class Query:
    @strawberry.field
    async def project(self, id: int, info: Info) -> Project:
        return await info.context["project_loader"].load(id)

    @strawberry.field
    async def projects(self, info: Info, offset: int = 0, limit: int = 30) -> List[Project]:
        obj = await models.Project.all().offset(offset).limit(limit)

        return [Project(**p.serialize()) for p in obj]

    @strawberry.field
    async def test(self, info: Info) -> str:
        print("AA")
        return "AA"

    @strawberry.field
    async def test_create(self, info: Info) -> bool:
        sub = (
            models.Project.filter(user_id=F('project"."user_id'))
            .limit(4)
            .values_list("id", flat=True)
        )
        projects = await models.Project.filter(id__in=Subquery(sub))
        print(projects)
        return True

    @strawberry.field
    async def test_user(self, info: Info) -> int:
        user = models.User(email="test@test.com", onboarded=True, username="tester")
        await user.save()
        return user.id
