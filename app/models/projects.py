from typing import Any, List, Optional

from pydantic import HttpUrl

from app.db.table.karupu import Categories, ProjectStatus, User
from app.models.base import GqlModel


class ProjectBaseModel(GqlModel):
    icon: Optional[Any]
    category: Categories
    status: ProjectStatus
    title: str
    desc: Optional[str]
    home_url: Optional[HttpUrl]
    repo_url: Optional[HttpUrl]
    readme: Optional[str]
    tags: Optional[List[str]]
    members: Optional[List[str]]
    images: Optional[List[Any]]


class ProjectCreateModel(ProjectBaseModel):
    user: User


class ProjectUpdateModel(ProjectBaseModel):
    id: int
    delete_image: Optional[str]
    category: Optional[Categories]
    status: Optional[ProjectStatus]
    title: Optional[str]
