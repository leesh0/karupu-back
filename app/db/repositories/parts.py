from app.db.table.karupu import Team, TeamMember, TeamPart
from app.models.parts import (
    MemberEntryModel,
    MemberIdModel,
    PartCreateModel,
    PartUpdateModel,
)
from tortoise.functions import Count


class TeamPartRepository:
    _part = TeamPart
    _member = TeamMember

    @classmethod
    async def create(cls, part: PartCreateModel) -> TeamPart:
        part_dict = part.dict(exclude_unset=True)
        check_team = await Team.exists(id=part.team_id)
        if not check_team:
            raise ValueError("team not found")

        part_obj = await TeamPart.create(**part_dict)
        return part_obj

    @classmethod
    async def update(cls, part: PartUpdateModel) -> TeamPart:
        part_dict = part.dict(exclude={"id"}, exclude_unset=True)
        part_og = await cls._part.get(id=part.id).annotate(members_count=Count("members"))

        if part.max_count and part_og.members_count > part.max_count:
            raise ValueError("max_count is over members count")

        updated_obj = await part_og.update_from_dict(part_dict)
        return updated_obj

    @classmethod
    async def delete(cls, part_id: int) -> bool:
        await cls._part.filter(id=part_id).delete()
        return True

    @classmethod
    async def entry_member(cls, member: MemberEntryModel) -> TeamMember:
        part_obj = await cls._part.get(id=member.part_id)
        member_dict = member.dict()

        created = await cls._member.create(**member_dict, team_id=part_obj.team_id)

        return created

    @classmethod
    async def accept_member(cls, member: MemberIdModel) -> bool:

        await cls._member.filter(id=member.id).update(accepted=True)

        return True

    @classmethod
    async def delete_member(cls, member: MemberIdModel) -> bool:

        await cls._member.filter(id=member.id).delete()

        return True
