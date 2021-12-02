from typing import Any, List, Optional

import strawberry
from strawberry.arguments import UNSET
from strawberry.file_uploads import Upload


@strawberry.input
class TeamInput:
    title: str
    name: str
    readme: str
    thumbnail: Optional[Upload] = UNSET
    open: Optional[bool] = UNSET
    tags: Optional[List[str]] = UNSET


@strawberry.input
class TeamUpdateInput(TeamInput):
    title: Optional[str] = UNSET
    name: Optional[str] = UNSET
    readme: Optional[str] = UNSET


@strawberry.input
class PartInput:
    name: str
    desc: Optional[str] = UNSET
    max_count: Optional[int] = UNSET


@strawberry.input
class PartUpdateInput(PartInput):
    name: Optional[str] = UNSET
