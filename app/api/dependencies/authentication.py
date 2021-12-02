from typing import Callable, Union

from app.core.config import get_app_settings
from app.db.table.karupu import User
from app.resources import strings
from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth import exceptions as jwt_exceptions
from starlette import status
from tortoise import exceptions as tot_exceptions

settings = get_app_settings()


class AuthCookie(AuthJWT):
    async def get_current_user(self):
        self.jwt_required()
        auth_user_id = self.get_jwt_subject()
        auth_user = await User.filter(id=auth_user_id).get_or_none()
        if not auth_user or not auth_user.onboarded:
            raise jwt_exceptions.AuthJWTException("user not found")
        return auth_user


def get_current_user(*, required: bool = True) -> Callable:
    return _get_current_user if required else _get_current_user_optional


async def _get_current_user(auth: AuthJWT = Depends()) -> User:
    try:
        auth.jwt_required()
        auth_user_id = auth.get_jwt_subject()
        auth_user = await User.get(id=auth_user_id)
        return auth_user
    except jwt_exceptions.AuthJWTException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=strings.AUTHORIZATION_FAILED
        )
    except tot_exceptions.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.USER_NOT_FOUND)


async def _get_current_user_optional(auth: AuthJWT = Depends()) -> Union[User, None]:
    try:
        auth.jwt_required()
        auth_user_id = auth.get_jwt_subject()
        auth_user = await User.get_or_none(id=auth_user_id)
        return auth_user
    except Exception:
        return None
