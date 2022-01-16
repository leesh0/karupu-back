from uuid import UUID

import strawberry
from app.db.repositories.parts import TeamPartRepository
from app.db.repositories.teams import TeamRepository
from app.graphql.permissions.authentication import IsAuthenticated
from app.graphql.permissions.teams import IsNotTeamMember, IsTeamLeader
from app.graphql.schemas.teams.inputs import (
    PartInput,
    PartUpdateInput,
    TeamInput,
    TeamUpdateInput,
)
from app.graphql.types import Team, TeamMember, TeamPart
from app.graphql.utils import input_dict
from app.models.parts import (
    MemberEntryModel,
    MemberIdModel,
    PartCreateModel,
    PartUpdateModel,
)
from app.models.teams import TeamCreateModel, TeamUpdateModel
from slugify import slugify
from strawberry.types import Info


@strawberry.type
class Mutation:
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def add_team(self, team: TeamInput, info: Info) -> Team:
        auth = info.context["auth"]
        current_user = await auth.get_current_user()
        team_dict = input_dict(team)
        team_slug = slugify(team.name, lower=True)
        create_model = TeamCreateModel(user=current_user, slug=team_slug, **team_dict)

        created = await TeamRepository.create(create_model)

        return Team(**created.serialize())

    @strawberry.mutation(permission_classes=[IsAuthenticated, IsTeamLeader])
    async def edit_team(self, team_id: UUID, team: TeamUpdateInput, info: Info) -> Team:
        team_dict = input_dict(team)

        update_model = TeamUpdateModel(id=team_id, **team_dict)

        updated = await TeamRepository.update(update_model)

        return Team(**updated.serialize())

    @strawberry.mutation(permission_classes=[IsAuthenticated, IsTeamLeader])
    async def delete_team(self, team_id: UUID) -> bool:
        return await TeamRepository.delete(team_id)

    @strawberry.mutation(permission_classes=[IsAuthenticated, IsTeamLeader])
    async def add_part(self, team_id: UUID, part: PartInput, info: Info) -> TeamPart:
        part_dict = input_dict(part)

        create_model = PartCreateModel(team_id=team_id, **part_dict)

        created = await TeamPartRepository.create(create_model)

        return TeamPart(**created.serialize())

    @strawberry.mutation(permission_classes=[IsAuthenticated, IsTeamLeader])
    async def edit_part(self, part_id: UUID, part: PartUpdateInput, info: Info) -> TeamPart:
        part_dict = input_dict(part)

        update_model = PartUpdateModel(id=part_id, **part_dict)

        updated = await TeamPartRepository.update(update_model)

        return TeamPart(**updated.serialize())

    @strawberry.mutation(permission_classes=[IsAuthenticated, IsTeamLeader])
    async def delete_part(self, part_id: UUID, info: Info) -> bool:
        return await TeamPartRepository.delete(part_id=part_id)

    @strawberry.mutation(permission_classes=[IsAuthenticated, IsNotTeamMember])
    async def entry_member(self, part_id: UUID, info: Info) -> bool:
        auth = info.context["auth"]
        current_user = await auth.get_current_user()

        create_model = MemberEntryModel(part_id=part_id, user_id=current_user.id)

        created = await TeamPartRepository.entry_member(create_model)

        return bool(created)

    @strawberry.mutation(permission_classes=[IsAuthenticated, IsTeamLeader])
    async def accept_member(self, member_id: UUID, info: Info) -> bool:
        return await TeamPartRepository.accept_member(MemberIdModel(id=member_id))

    @strawberry.mutation(permission_classes=[IsAuthenticated, IsTeamLeader])
    async def delete_member(self, member_id: UUID, info: Info) -> bool:
        return await TeamPartRepository.delete_member(MemberIdModel(id=member_id))
