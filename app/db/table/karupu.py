import asyncio
import typing
from dataclasses import field
from email.policy import default
from enum import Enum

from slugify import slugify
from strawberry.file_uploads import Upload
from tortoise import fields

from app.db.table.auth import User
from app.db.table.base import GqlModel
from app.db.table.validators import URL_VALIDATOR
from app.resources import strings
from app.services.aws.uploader import delete_images, upload_images


class Categories(str, Enum):
    BOT: str = "Bot"
    WEB: str = "Webサービス"
    SNS: str = "SNS"
    GAME: str = "ゲーム"
    DESKTOP: str = "App/Desktop"
    MOBILE: str = "App/Mobile"
    OS: str = "OS"
    SECURITY: str = "Security"
    ETC: str = "etc"


class ProjectStatus(str, Enum):
    RELEASED: str = "Released"
    DEVELOPING: str = "Developing"
    WANTED: str = "Wanted"


class Tag(GqlModel):
    id = fields.IntField(pk=True)
    slug = fields.CharField(max_length=60)
    text = fields.CharField(max_length=30, unique=True)

    def __init__(self, text):
        slug = slugify(text, lower=True)
        super().__init__(text=text, slug=slug)

    def __str__(self):
        return self.text


class Project(GqlModel):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="projects"
    )
    icon = fields.TextField(default=None, null=True, validators=[URL_VALIDATOR])
    category: Categories = fields.CharEnumField(Categories, default=Categories.WEB)
    status: ProjectStatus = fields.CharEnumField(ProjectStatus, default=ProjectStatus.RELEASED)
    title = fields.CharField(max_length=100)
    desc = fields.CharField(max_length=400, default=None, null=True)
    home_url = fields.TextField(default=None, null=True, validators=[URL_VALIDATOR])
    repo_url = fields.TextField(default=None, null=True, validators=[URL_VALIDATOR])
    readme = fields.TextField(default=None, null=True)
    views = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    async def add_image(self, image):
        path = await upload_images([image], path="project-detail-images")
        save = await ProjectImage.create(ProjectImage(project=self, storage=path))
        return path

    async def add_images(self, images: typing.List):
        paths = await upload_images(images, path="project-detail-images")
        save = await ProjectImage.bulk_create(
            [ProjectImage(project=self, storage=path) for path in paths]
        )
        return paths

    async def delete_image(self, image_id):
        images = await ProjectImage.filter(id=image_id).all()
        if images:
            await delete_images([image.storage for image in images])
            return True
        else:
            raise ValueError(f"image id {image_id} not found.")

    async def add_tags(self, tags: typing.List[str]):
        tags_map = {tag: None for tag in tags}
        search_tags = await Tag.filter(text__in=tags_map.keys()).all()
        for stag in search_tags:
            tags_map[stag.text] = stag
        add_tags = [Tag(text=tag_text) for tag_text, tag_obj in tags_map.items() if not tag_obj]
        await Tag.bulk_create(add_tags)
        add_tags = [
            tag_obj
            for tag_obj in await Tag.filter(text__in=[add_tag.text for add_tag in add_tags])
        ]
        for _tag in add_tags:
            tags_map[_tag.text] = _tag
        await ProjectTagManager.bulk_create(
            [ProjectTagManager(project=self, tag=tag) for _, tag in tags_map.items()]
        )
        return True

    async def edit_tags(self, new_tags: typing.List[str]):
        all_tags = await ProjectTagManager.filter(project=self).all()
        to_delete = [tag.id for tag in all_tags if tag.text not in new_tags]
        to_add = [n_tag for n_tag in new_tags if n_tag not in [tag.text for tag in all_tags]]

        if to_delete:
            await ProjectTagManager.filter(tag_id__in=to_delete).delete()

        if to_add:
            await self.add_tags(to_add)

        return True

    async def add_members(self, usernames: typing.List[str]):
        usernames = set(usernames)
        users = await User.filter(username__in=usernames).all()
        if len(usernames) != len(users):
            raise ValueError(strings.USER_NOT_FOUND)

        to_create = [ProjectMember(project=self, user=user) for user in users]

        await ProjectMember.bulk_create(to_create)
        return True

    async def edit_members(self, usernames: typing.List[str]):
        og_members = (
            await ProjectMember.filter(project=self)
            .select_related("user")
            .all()
            .values("user__username")
        )

        to_delete = [og_member for og_member in og_members if og_member not in usernames]
        to_create = {username for username in usernames if username not in og_members}

        if to_delete:
            await ProjectMember.filter(user_username__in=to_delete).delete()

        if to_create:
            users = await User.filter(username__in=to_create).all()
            await ProjectMember.bulk_create(
                [ProjectMember(project=self, user=user) for user in users]
            )
        return True


class ProjectMember(GqlModel):
    id = fields.IntField(pk=True)
    project: fields.ForeignKeyRelation[Project] = fields.ForeignKeyField(
        "models.Project", related_name="members", on_delete="CASCADE"
    )
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="project_member", on_delete="CASCADE"
    )


class ProjectFeedback(GqlModel):
    id = fields.UUIDField(pk=True, index=True)
    project: fields.ForeignKeyRelation[Project] = fields.ForeignKeyField(
        "models.Project", related_name="feedbacks", on_delete="CASCADE"
    )
    parent: fields.ForeignKeyNullableRelation["ProjectFeedback"] = fields.ForeignKeyField(
        "models.ProjectFeedback", related_name="replies", null=True
    )
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="feedbacks"
    )
    rate_score = fields.IntField(default=0, null=True)
    body = fields.TextField(default=None, null=True)
    anon = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class ProjectTagManager(GqlModel):
    id = fields.IntField(pk=True)
    project: fields.ForeignKeyRelation[Project] = fields.ForeignKeyField(
        "models.Project", related_name="tags", on_delete="CASCADE"
    )
    tag: fields.ForeignKeyRelation[Tag] = fields.ForeignKeyField(
        "models.Tag", related_name="projects"
    )


class ProjectImage(GqlModel):
    id = fields.UUIDField(pk=True)
    project: fields.ForeignKeyRelation[Project] = fields.ForeignKeyField(
        "models.Project", related_name="images", on_delete="CASCADE"
    )
    storage = fields.TextField()
