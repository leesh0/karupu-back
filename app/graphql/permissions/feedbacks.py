from typing import Any

from app.db.table.karupu import Project, ProjectFeedback
from app.resources import strings
from strawberry.permission import BasePermission
from strawberry.types import Info


class IsFeedbackAuthor(BasePermission):
    message = strings.PROJECT_YOUR_NOT_AUTHOR

    async def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        auth = info.context["auth"]
        req_user = await auth.get_current_user(required=True)
        feedback_id = kwargs.get("feedbackId")

        feedback_ob = await ProjectFeedback(id=feedback_id, user=req_user).get_or_none()
        if feedback_ob:
            return True
        else:
            return False
