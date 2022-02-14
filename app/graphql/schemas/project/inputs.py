from typing import Any, List, Optional

import strawberry
from strawberry.arguments import UNSET
from strawberry.file_uploads import Upload


@strawberry.input
class ProjectsInput:
    category: str
    title: str
    status: Optional[str] = UNSET
    icon: Optional[Upload] = UNSET
    desc: Optional[str] = UNSET
    home_url: Optional[str] = UNSET
    repo_url: Optional[str] = UNSET
    readme: Optional[str] = UNSET
    members: Optional[List[str]] = UNSET
    tags: Optional[List[str]] = UNSET


@strawberry.input
class ProjectsUpdateInput(ProjectsInput):
    category: Optional[str] = UNSET
    status: Optional[str] = UNSET
    title: Optional[str] = UNSET


@strawberry.input
class ProjectFeedbackInput:
    rate_score: int
    body: str
    anon: Optional[bool] = UNSET
    parent: Optional[str] = UNSET


@strawberry.input
class ProjectFeedbackUpdateInput:
    rate_score: Optional[int] = UNSET
    body: Optional[str] = UNSET
    anon: Optional[bool] = UNSET
