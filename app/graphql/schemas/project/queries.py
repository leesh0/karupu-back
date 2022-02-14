from collections import defaultdict
from typing import List, Optional, Union

import strawberry
from strawberry.arguments import UNSET
from strawberry.types import Info
from tortoise.expressions import F, Subquery
from tortoise.functions import Count, Q
from tortoise.query_utils import Prefetch

from app.db.repositories.projects import ProjectCreateModel, ProjectRepository
from app.db.table import karupu as models
from app.graphql.types import Project, ProjectFeedback
from app.graphql.wrappers.pagination import Pagination
from tests.utils import get_random_image


@strawberry.type
class Query:
    @strawberry.field
    async def project(self, id: int, info: Info) -> Project:
        req_ip = info.context["depends"].req.client.host
        pj = await ProjectRepository.get(id, req_ip)
        return Project(**pj.serialize())

    @strawberry.field
    async def projects(
        self,
        info: Info,
        username: Optional[str] = None,
        search: Optional[str] = None,
        order_by: str = "latest",
        offset: int = 0,
        limit: int = 30,
    ) -> Pagination[Project]:
        options = {"username": username, "search": search, "order_by": order_by}
        query = ProjectRepository.gets(**options)
        return await Pagination[Project].paginate(query, offset=offset, limit=limit)
