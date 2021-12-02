from enum import Enum

from app.db.table.base import GqlModel
from tortoise import fields


class Providers(str, Enum):
    GOOGLE: str = "google"


class User(GqlModel):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=200, unique=True)
    avatar = fields.CharField(max_length=1000, default=None, null=True)
    bio = fields.CharField(max_length=300, default=None, null=True)
    username = fields.CharField(max_length=30, default=None, null=True)
    nickname = fields.CharField(max_length=30, default=None, null=True)
    onboarded = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    last_logged_in = fields.DatetimeField(auto_now=True)
    is_staff = fields.BooleanField(default=False)
    is_admin = fields.BooleanField(default=False)


class SocialAccount(GqlModel):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="social_accounts"
    )
    provider = fields.CharEnumField(Providers, description=Providers.GOOGLE)
    acc_key = fields.CharField(max_length=1000, unique=True)
    data = fields.JSONField(default={})
