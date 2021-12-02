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


class MemberAcceptModel(GqlModel):
    part_id: UUID
    id: UUID
