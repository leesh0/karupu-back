from dataclasses import field
from typing import List, Optional, Union
from uuid import UUID

import strawberry
from app.db.table import karupu as models
from strawberry.types import Info
from tortoise.expressions import Subquery


@strawberry.type
class TagItem:
    text: str


@strawberry.type
class Tag:
    tag: TagItem


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

    @strawberry.field  # require pagination
    async def projects(self, info: Info) -> Optional[List["Project"]]:
        return await info.context["user_projects_loader"].load(self.id, info)


@strawberry.experimental.pydantic.type(model=models.Project.pydantic(), all_fields=True)
class Project:
    user_id: strawberry.Private[int]

    @strawberry.field
    async def tags(self, info: Info) -> Optional[List[str]]:
        return await info.context["project_tags_loader"].load(self.id)

    @strawberry.field
    async def user(self, info: Info) -> "User":
        return await info.context["user_loader"].load(self.user_id)

    @strawberry.field
    async def members(self, info: Info) -> Optional[List["User"]]:
        return await info.context["project_member_loader"].load(self.id)


@strawberry.experimental.pydantic.type(model=models.ProjectFeedback.pydantic(), all_fields=True)
class ProjectFeedback:
    user_id: strawberry.Private[int]
    project_id: strawberry.Private[int]
    parent_id: strawberry.Private[str]

    @strawberry.field
    async def user(self, info: Info) -> "User":
        return await info.context["user_loader"].load(self.user_id)

    @strawberry.field
    async def project(self, info: Info) -> "Project":
        return await info.context["project_loader"].load(self.project_id)

    @strawberry.field  # require pagination
    async def childs(self, info: Info) -> Optional[List["ChildProjectFeedback"]]:
        return await info.context["child_feedback_loader"].load(self.id)


@strawberry.experimental.pydantic.type(model=models.ProjectFeedback.pydantic(), all_fields=True)
class ChildProjectFeedback:
    user_id: strawberry.Private[int]
    project_id: strawberry.Private[int]

    @strawberry.field
    async def user(self, info: Info) -> "User":
        return await info.context["user_loader"].load(self.user_id)

    @strawberry.field
    async def project(self, info: Info) -> "Project":
        return await info.context["project_loader"].load(self.project_id)


@strawberry.experimental.pydantic.type(model=models.TeamMember.pydantic(), all_fields=True)
class TeamMember:
    team_id: strawberry.Private[UUID]
    part_id: strawberry.Private[UUID]
    user_id: strawberry.Private[int]

    @strawberry.field
    async def user(self, info: Info) -> "User":
        return await info.context["user_loader"].load(self.user_id)

    @strawberry.field
    async def team(self, info: Info) -> "Team":
        return await info.context["team_loader"].load(self.team_id)

    @strawberry.field
    async def part(self, info: Info) -> "TeamPart":
        return await info.context["part_loader"].load(self.part_id)


@strawberry.experimental.pydantic.type(model=models.TeamPart.pydantic(), all_fields=True)
class TeamPart:
    team_id: strawberry.Private[UUID]

    @strawberry.field
    async def team(self, info: Info) -> "Team":
        return await info.context["team_loader"].load(self.team_id)

    @strawberry.field
    async def members(self, info: Info) -> "List[User]":
        return await info.context["part_member_loader"].load(self.id)


@strawberry.experimental.pydantic.type(model=models.Team.pydantic(), all_fields=True)
class Team:
    user_id: strawberry.Private[int]

    @strawberry.field
    async def tags(self, info: Info) -> Optional[List[str]]:
        return await info.context["team_tags_loader"].load(self.id)

    @strawberry.field
    async def parts(self, info: Info) -> "List[TeamPart]":
        return await info.context["team_part_loader"].load(self.id)

    @strawberry.field
    async def user(self, info: Info) -> "User":
        return await info.context["user_loader"].load(self.user_id)
