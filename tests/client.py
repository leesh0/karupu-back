from datetime import timedelta

from app.main import get_application
from fastapi_jwt_auth import AuthJWT
from httpx import AsyncClient


def get_client(admin=True) -> AsyncClient:
    _token = AuthJWT().create_access_token(
        subject=1 if admin else 2, expires_time=timedelta(days=7)
    )
    _refresh_token = AuthJWT().create_refresh_token(
        subject=1 if admin else 2, expires_time=timedelta(days=7)
    )
    return AsyncClient(
        app=get_application(),
        cookies={"access_token_cookie": _token, "refresh_token_cookie": _refresh_token},
        base_url="http://test",
    )
