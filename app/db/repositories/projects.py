from typing import Awaitable, BinaryIO, List, Optional, Union
from uuid import UUID

from aiocache import cached
from pypika import Field, PostgreSQLQuery, SQLLiteQuery, Table, Tables
from slugify import slugify
from strawberry.arguments import UNSET
from tortoise.expressions import F
from tortoise.functions import Avg, Coalesce, Count, Sum
from tortoise.query_utils import Q

from app.db.table.karupu import Categories, Project, ProjectFeedback, User
from app.models.feedbacks import CreateFeedbackModel, UpdateFeedbackModel
from app.models.projects import ProjectCreateModel, ProjectUpdateModel
from app.services.aws.uploader import delete_images, upload_images


class ProjectRepository:
    _project: Project = Project
    _feedback: ProjectFeedback = ProjectFeedback

    @classmethod
    @cached(ttl=60 * 10)  # 10min cached
    async def view(cls, id: int, ip: str):
        return await cls._project.filter(id=id).update(views=F("views") + 1)

    @classmethod
    async def get(cls, id: int, ip: str):
        cls.view(id, ip)
        return await cls._project.get_or_none(id=id)

    @classmethod
    def gets(cls, username: str = None, search=None, order_by="latest") -> Awaitable[Project]:
        base = cls._project.gql.get_queryset().distinct()
        base = base
        order = "-created_at"  # for latest
        if username:
            base = base.filter(Q(user__username=username) | Q(members__user__username=username))

        if search:
            base = base.filter(
                Q(title__icontains=search)
                | Q(desc__icontains=search)
                | Q(tags__tag__slug__icontains=slugify(search, lower=True))
            )

        if order_by and order_by != "latest":

            if order_by == "rank":
                order = "-views"

            if order_by == "score":
                base = base.annotate(score=Coalesce(Sum("feedbacks__rate_score"), 0))
                order = "-score"

        return base.order_by(order, "-created_at")

    @classmethod
    async def create(cls, body: ProjectCreateModel) -> Project:
        data_dict = body.dict(exclude_defaults=True)
        tags = data_dict.pop("tags", False)
        members = data_dict.pop("members", False)
        images = data_dict.pop("images", False)
        # uplaod icon file
        if data_dict.get("icon"):
            icon = data_dict["icon"]
            icon_url = (await upload_images([icon], path="project-thumbnails"))[0]
            data_dict["icon"] = icon_url

        obj: Project = cls._project(**data_dict)
        await obj.save()

        if images:
            await obj.add_images(images)

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
        images = update_dict.pop("images", False)
        delete_images = update_dict.pop("delete_images", False)

        # change icon if icon
        if update_dict.get("icon"):
            await delete_images([og_project.icon])
            new_icon = (await upload_images([update_dict.get("icon")], path="project-thumbnails"))[
                0
            ]
            update_dict["icon"] = new_icon

        await cls._project.filter(id=body.id).update(**update_dict)

        if images:
            await og_project.add_images(images)

        if delete_images:
            await og_project.delete_image(delete_images)

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

    @classmethod
    async def get_feedback(cls, id: UUID) -> ProjectFeedback:
        return await cls._feedback.get(id=id)

    @classmethod
    async def get_feedbacks(
        cls, pid: int, offset: int = 0, limit: int = 20
    ) -> List[ProjectFeedback]:
        return (
            await cls._feedback.filter(project_id=pid, parent=None)
            .offset(offset)
            .limit(limit)
            .all()
        )
