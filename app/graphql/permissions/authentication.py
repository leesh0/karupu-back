from typing import Any

from app.resources import strings
from strawberry.permission import BasePermission
from strawberry.types import Info


class IsAuthenticated(BasePermission):
    message = strings.AUTHORIZATION_FAILED

    async def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        auth = info.context["auth"]
        await auth.get_current_user(required=True)
        return True
