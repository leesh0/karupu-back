from typing import Any

from strawberry.permission import BasePermission
from strawberry.types import Info

from app.core.config import get_app_settings
from app.resources import strings

settings = get_app_settings()


class IsAuthenticated(BasePermission):
    message = strings.AUTHORIZATION_FAILED

    async def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        if settings.app_env == "dev":
            return True
        auth = info.context["auth"]
        await auth.get_current_user(required=True)
        return True
