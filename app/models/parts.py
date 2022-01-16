from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.db.table.karupu import Categories, User
from app.models.base import GqlModel
from pydantic import HttpUrl


class PartBaseModel(GqlModel):
    name: str
    desc: Optional[str]
    max_count: Optional[int]


class PartCreateModel(PartBaseModel):
    team_id: UUID


class PartUpdateModel(PartBaseModel):
    id: UUID


class MemberEntryModel(GqlModel):
    part_id: UUID
    user_id: int


class MemberIdModel(GqlModel):
    id: UUID
