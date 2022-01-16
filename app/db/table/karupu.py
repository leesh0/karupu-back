import asyncio
import typing
from enum import Enum

from app.db.table.auth import User
from app.db.table.base import GqlModel
from app.db.table.validators import URL_VALIDATOR
from app.resources import strings
from app.services.aws.uploader import delete_images, upload_images
from slugify import slugify
from strawberry.file_uploads import Upload
from tortoise import fields


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


class TeamsCategory(str, Enum):
    PLANNER: str = "企画"
    DESIGNER: str = "デザイン"
    FRONTEND: str = "frontend"
    BACKEND: str = "backend"
    MOBILE: str = "mobile"
    ETC: str = "etc"


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
    title = fields.CharField(max_length=100)
    desc = fields.CharField(max_length=400, default=None, null=True)
    home_url = fields.TextField(default=None, null=True, validators=[URL_VALIDATOR])
    repo_url = fields.TextField(default=None, null=True, validators=[URL_VALIDATOR])
    readme = fields.TextField(default=None, null=True)
    views = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

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


class Team(GqlModel):
    id = fields.UUIDField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="teams"
    )
    title = fields.CharField(max_length=300)
    name = fields.CharField(max_length=200)
    slug = fields.CharField(max_length=1000)
    thumbnail = fields.TextField(default=None, null=True)
    open = fields.BooleanField(default=True)
    readme = fields.TextField()
    views = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)

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
        await TeamTagManager.bulk_create(
            [TeamTagManager(team=self, tag=tag) for _, tag in tags_map.items()]
        )
        return True

    async def edit_tags(self, new_tags: typing.List[str]):
        all_tags = await TeamTagManager.filter(team=self).select_related("tag").all()
        to_delete = [tag.id for tag in all_tags if tag.tag.text not in new_tags]
        to_add = [n_tag for n_tag in new_tags if n_tag not in [tag.tag.text for tag in all_tags]]

        if to_delete:
            await TeamTagManager.filter(tag_id__in=to_delete).delete()
        if to_add:
            await self.add_tags(to_add)

        return True


class TeamTagManager(GqlModel):
    id = fields.IntField(pk=True)
    team: fields.ForeignKeyRelation[Team] = fields.ForeignKeyField(
        "models.Team", related_name="tags", on_delete="CASCADE"
    )
    tag: fields.ForeignKeyRelation[Tag] = fields.ForeignKeyField(
        "models.Tag", related_name="teams", on_delete=fields.SET_NULL, null=True
    )


class TeamPart(GqlModel):
    id = fields.UUIDField(pk=True)
    team: fields.ForeignKeyRelation[Team] = fields.ForeignKeyField(
        "models.Team", related_name="parts", on_delete="CASCADE"
    )
    name = fields.CharField(max_length=100)
    desc = fields.CharField(max_length=300, default=None, null=True)
    max_count = fields.IntField(default=1)


class TeamMember(GqlModel):
    id = fields.UUIDField(pk=True)
    team: fields.ForeignKeyRelation[Team] = fields.ForeignKeyField(
        "models.Team", related_name="members", on_delete="CASCADE"
    )
    part: fields.ForeignKeyRelation["TeamPart"] = fields.ForeignKeyField(
        "models.TeamPart", related_name="members", on_delete="CASCADE"
    )
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="parts"
    )
    accepted = fields.BooleanField(default=False)
