from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.db.table.karupu import Categories, User
from app.models.base import GqlModel
from pydantic import HttpUrl
from pydantic.main import BaseModel


class TeamPartModel(GqlModel):
    name: str
    desc: Optional[str]
    max_count: Optional[int]


class TeamBaseModel(GqlModel):
    title: str
    name: str
    slug: str
    readme: str
    thumbnail: Optional[Any]
    open: Optional[bool]
    tags: Optional[List[str]]


class TeamCreateModel(TeamBaseModel):
    user: User


class TeamUpdateModel(TeamBaseModel):
    id: UUID
    title: Optional[str]
    name: Optional[str]
    slug: Optional[str]
    readme: Optional[str]
