from typing import Any, List, Optional

from pydantic import HttpUrl

from app.db.table.karupu import Categories, ProjectStatus, User
from app.models.base import GqlModel


class ProjectBaseModel(GqlModel):
    icon: Optional[Any]
    category: Categories
    title: str
    status: Optional[ProjectStatus]
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
    status: Optional[ProjectStatus]
    title: Optional[str]
