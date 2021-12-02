from typing import Any, List, Optional

from app.db.table.karupu import Categories, Project, ProjectFeedback, User
from app.models.base import GqlModel
from pydantic import UUID4, HttpUrl


class FeedbackBaseModel(GqlModel):
    rate_score: int
    body: str
    anon: bool = False


class CreateFeedbackModel(FeedbackBaseModel):
    project: Project
    parent: Optional[ProjectFeedback]
    user: User
    rate_score: int = 5


class UpdateFeedbackModel(FeedbackBaseModel):
    id: UUID4
    rate_score: Optional[int]
    body: Optional[str]
    anon: Optional[bool]
