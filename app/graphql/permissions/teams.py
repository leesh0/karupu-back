from typing import Any, Awaitable, Union

from app.db.table import karupu as models
from app.resources import strings
from strawberry.permission import BasePermission
from strawberry.types import Info


class IsTeamLeader(BasePermission):
    message = strings.TEAM_YOUR_NOT_LEADER

    async def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        auth = info.context["auth"]
        req_user = await auth.get_current_user(required=True)
        team_id = kwargs.get("teamId")
        part_id = kwargs.get("partId")
        member_id = kwargs.get("memberId")

        if team_id:
            is_team_leader = await models.Team.filter(id=team_id, user=req_user).exists()
        elif part_id:
            is_team_leader = await models.TeamPart.filter(id=part_id, team__user=req_user).exists()
        elif member_id:
            is_team_leader = await models.TeamMember.filter(
                id=member_id, team__user=req_user
            ).exists()
        else:
            return False
        return bool(is_team_leader)


class IsNotTeamMember(BasePermission):
    message = strings.YOU_ARE_ALREADY_TEAM_MEMBER

    async def has_permission(
        self, source: Any, info: Info, **kwargs
    ) -> Union[bool, Awaitable[bool]]:
        auth = info.context["auth"]
        req_user = await auth.get_current_user(required=True)

        team_id = kwargs.get("teamId")
        part_id = kwargs.get("partId")

        if team_id:
            is_team_member = await models.TeamMember.filter(
                user=req_user, team_id=team_id
            ).exists()
        elif part_id:
            team_obj = await models.TeamPart.filter(id=part_id).get_or_none()
            if team_obj:
                is_team_member = await models.TeamMember.filter(
                    user=req_user, team_id=team_obj.team_id
                ).exists()
            else:
                return False
        else:
            return False

        return not is_team_member
