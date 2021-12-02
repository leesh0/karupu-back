from typing import BinaryIO, List, Optional

from app.db.table.karupu import Categories, Project, ProjectFeedback, User
from app.models.feedbacks import CreateFeedbackModel, UpdateFeedbackModel
from app.models.projects import ProjectCreateModel, ProjectUpdateModel
from app.services.aws.uploader import delete_images, upload_images
from strawberry.arguments import UNSET


class ProjectRepository:
    _project = Project

    @classmethod
    async def create(cls, body: ProjectCreateModel) -> Project:
        data_dict = body.dict(exclude_defaults=True)
        tags = data_dict.pop("tags", False)
        members = data_dict.pop("members", False)

        # uplaod icon file
        if data_dict.get("icon"):
            icon = data_dict["icon"]
            icon_url = (await upload_images([icon], path="project-thumbnails"))[0]
            data_dict["icon"] = icon_url

        obj = cls._project(**data_dict)
        await obj.save()

        if tags:
            await obj.add_tags(tags)

        if members:
            await obj.add_members(members)
        return obj

    @classmethod
    async def update(cls, body: ProjectUpdateModel) -> Project:
        update_dict = body.dict(exclude_defaults=True, exclude={"id"})
        og_project = await cls._project.get(id=body.id)

        tags = update_dict.pop("tags", False)
        members = update_dict.pop("members", False)

        # change icon if icon
        if update_dict.get("icon"):
            await delete_images([og_project.icon])
            new_icon = (await upload_images([update_dict.get("icon")], path="project-thumbnails"))[
                0
            ]
            update_dict["icon"] = new_icon

        await cls._project.filter(id=body.id).update(**update_dict)
        if tags:
            await og_project.edit_tags(tags)

        if members:
            await og_project.edit_members(members)

        obj = await cls._project.get(id=body.id)
        return obj

    @classmethod
    async def delete(cls, id: int) -> bool:
        try:
            await cls._project.filter(id=id).delete()
            return True
        except:
            return False

    @classmethod
    async def add_feedback(cls, feedback: CreateFeedbackModel) -> ProjectFeedback:
        feedback_body = feedback.dict(exclude_unset=True)
        og_feedback = ProjectFeedback(**feedback_body)
        await og_feedback.save()
        return og_feedback

    @classmethod
    async def edit_feedback(cls, feedback: UpdateFeedbackModel) -> ProjectFeedback:
        feedback_body = feedback.dict(exclude_unset=True, exclude={"id"})
        feedback = await ProjectFeedback().get(id=feedback.id)
        updated = await feedback.update_from_dict(feedback_body)
        return updated

    @classmethod
    async def delete_feedback(cls, id: str) -> bool:
        await ProjectFeedback.filter(id=id).delete()
        return True
