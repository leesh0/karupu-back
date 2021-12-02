from typing import Callable, Union

from app.core.config import get_app_settings
from app.db.table.karupu import User
from app.resources import strings
from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth import exceptions as jwt_exceptions
from starlette import status
from strawberry import exceptions as st_exceptions
from tortoise import exceptions as tot_exceptions

settings = get_app_settings()


class AuthCookie(AuthJWT):
    async def get_current_user(self, required=True) -> Union[User, None]:
        try:
            self.jwt_required()
            auth_user_id = self.get_jwt_subject()
            auth_user = await User.get(id=auth_user_id)
            return auth_user
        except jwt_exceptions.AuthJWTException:
            if required:
                raise jwt_exceptions.JWTDecodeError(
                    status_code=status.HTTP_400_BAD_REQUEST, message=strings.AUTHORIZATION_FAILED
                )
            else:
                return None
        except tot_exceptions.DoesNotExist:
            if required:
                raise Exception(message=strings.USER_NOT_FOUND)
            else:
                return None
        except:
            return None
