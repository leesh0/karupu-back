from typing import Any

from app.db.table.karupu import Project
from app.resources import strings
from strawberry.permission import BasePermission
from strawberry.types import Info


class IsProjectAuthor(BasePermission):
    message = strings.PROJECT_YOUR_NOT_AUTHOR

    async def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        auth = info.context["auth"]
        req_user = await auth.get_current_user(required=True)
        project_id = kwargs.get("id")

        project_ob = await Project.get_or_none(id=project_id, user=req_user)
        if project_ob:
            return True
        else:
            return False
