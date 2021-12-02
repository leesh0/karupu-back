from typing import Any, List, Optional

from app.db.table.karupu import Categories, User
from app.models.base import GqlModel
from pydantic import HttpUrl


class ProjectBaseModel(GqlModel):
    icon: Optional[Any]
    category: Categories
    title: str
    desc: Optional[str]
    home_url: Optional[HttpUrl]
    repo_url: Optional[HttpUrl]
    readme: Optional[str]
    tags: Optional[List[str]]
    members: Optional[List[str]]


class ProjectCreateModel(ProjectBaseModel):
    user: User


class ProjectUpdateModel(ProjectBaseModel):
    id: int
    category: Optional[Categories]
    title: Optional[str]
