from uuid import UUID

from app.db.table.karupu import Team
from app.models.teams import TeamCreateModel, TeamUpdateModel
from app.services.aws.uploader import delete_images, upload_images


class TeamRepository:
    _team = Team

    @classmethod
    async def create(cls, team: TeamCreateModel) -> Team:
        team_data = team.dict(exclude={"tags", "thumbnail"}, exclude_unset=True)
        if team.thumbnail:
            thumb_url = (await upload_images([team.thumbnail], path="team-thumbnails"))[0]
            team_data["thumbnail"] = thumb_url

        new_team = cls._team(**team_data)
        await new_team.save()

        if team.tags:
            await new_team.add_tags(team.tags)

        return new_team

    @classmethod
    async def update(cls, team: TeamUpdateModel) -> Team:
        team_data = team.dict(exclude={"tags", "thumbnail"}, exclude_unset=True)
        og_obj = await cls._team.get(id=team.id)

        if team.thumbnail:
            og_thumb = og_obj.thumbnail
            await delete_images([og_thumb])
            thumb_url = (await upload_images([team.thumbnail], path="team-thumbnails"))[0]

            team_data["thumbnail"] = thumb_url

        if team.tags:
            await og_obj.edit_tags(team.tags)

        updated_team = await og_obj.update_from_dict(team_data)

        return updated_team

    @classmethod
    async def delete(cls, team_id: UUID) -> bool:
        try:
            await cls._team.filter(id=team_id).delete()
            return True
        except:
            return False
