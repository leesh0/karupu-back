from dataclasses import field
from typing import List, Optional, Union
from uuid import UUID

import strawberry
from strawberry.arguments import UNSET
from strawberry.types import Info
from tortoise.expressions import Subquery
from tortoise.functions import Avg, Coalesce, Count, F
from tortoise.query_utils import Q

from app.db.repositories.projects import ProjectRepository
from app.db.table import karupu as models
from app.graphql.loaders.generator import GenLoader


@strawberry.type
class Tag:
    id: int
    slug: str
    text: str


@strawberry.experimental.pydantic.type(model=models.User.pydantic())
class User:
    id: strawberry.auto
    email: strawberry.auto
    avatar: strawberry.auto
    bio: strawberry.auto
    username: strawberry.auto
    nickname: strawberry.auto
    onboarded: strawberry.auto
    created_at: strawberry.auto
    last_logged_in: strawberry.auto
    is_staff: strawberry.Private[bool]
    is_admin: strawberry.Private[bool]


@strawberry.experimental.pydantic.type(model=models.Project.pydantic(), all_fields=True)
class Project:
    user_id: strawberry.Private[int]

    @strawberry.field
    async def rate_score(self, info: Info) -> float:
        return await GenLoader.loader(
            qs=models.Project.all().annotate(avg_score=Avg(Coalesce("feedbacks__rate_score", 0))),
            field="id",
            is_list=False,
            factory=lambda x: {"score": x.avg_score},
            return_model=lambda score: score,
        ).load(self.id)

    @strawberry.field
    async def tags(self, info: Info) -> List[Tag]:
        return await (
            GenLoader.loader(
                qs=models.ProjectTagManager.gql.select_related("tag"),
                field="project_id",
                is_list=True,
                factory=lambda x: x.tag.serialize(),
                return_model=lambda **kwargs: Tag(**kwargs),
            ).load(self.id)
        )

    @strawberry.field
    async def user(self, info: Info) -> "User":
        return await GenLoader.loader(return_model=User, qs=models.User).load(self.user_id)

    @strawberry.field
    async def members(self, info: Info) -> Optional[List["User"]]:
        return await GenLoader.loader(
            return_model=User,
            qs=models.ProjectMember.all().select_related("user"),
            is_list=True,
            field="project_id",
            factory=lambda x: x.user.serialize(),
        ).load(self.id)

    @strawberry.field
    async def feedbacks(self, info: Info) -> "List[ProjectFeedback]":
        return await GenLoader.loader(
            return_model=ProjectFeedback,
            qs=models.ProjectFeedback.filter(parent__isnull=True),
            is_list=True,
            field="id",
        ).load(self.id)


@strawberry.experimental.pydantic.type(model=models.ProjectFeedback.pydantic(), all_fields=True)
class ChildProjectFeedback:
    user_id: strawberry.Private[int]
    project_id: strawberry.Private[int]

    @strawberry.field
    async def user(self, info: Info) -> "User":
        return await GenLoader.loader(return_model=User, qs=models.User).load(self.user_id)

    @strawberry.field
    async def project(self, info: Info) -> "Project":
        return await GenLoader.loader(return_model=Project, qs=models.Project).load(
            self.project_id
        )


@strawberry.type
class ProjectFeedback(ChildProjectFeedback):
    @strawberry.field  # require pagination
    async def childs(self, info: Info) -> Optional[List["ChildProjectFeedback"]]:
        return await GenLoader.loader(
            return_model=ChildProjectFeedback,
            qs=models.ProjectFeedback,
            field="parent_id",
            is_list=True,
        ).load(self.id)
