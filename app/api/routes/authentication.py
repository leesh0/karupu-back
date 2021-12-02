import datetime
from typing import Optional
from urllib.parse import parse_qs, urlparse

from app.api.utils.request import get_google_profile
from app.core.config import get_app_settings
from app.db.table.auth import SocialAccount, User
from app.resources.strings import CANNOT_VERIFY_TOKEN, EMAIL_EXISTED, EMAIL_NOT_VERIFIED
from fastapi import APIRouter, Depends, exceptions, status
from fastapi_jwt_auth import AuthJWT
from google.auth.transport import requests
from google.oauth2.id_token import verify_oauth2_token
from pydantic import BaseModel

router = APIRouter()
settings = get_app_settings()


class DevLoginRequest(BaseModel):
    id_token: Optional[str]
    access_token: Optional[str]


class LoginRequest(BaseModel):
    id_token: str
    access_token: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str


url = settings.GOOGLE_URL
url = url.replace("google#", "google?")


@router.post("/login", response_model=LoginResponse)
async def google_login(req: LoginRequest, Authorize: AuthJWT = Depends()) -> LoginResponse:
    """
    Login API
    """
    if settings.app_env == "dev":
        data = parse_qs(urlparse(url).query)
        google_id_token = data["id_token"][0]
        google_access_token = data["access_token"][0]
    else:
        google_id_token = req.id_token
        google_access_token = req.access_token

    try:
        auth_info = verify_oauth2_token(google_id_token, requests.Request())
    except Exception:
        raise exceptions.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=CANNOT_VERIFY_TOKEN
        )

    if not auth_info.get("email_verified"):
        raise exceptions.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=EMAIL_NOT_VERIFIED
        )

    user_sub = auth_info.get("sub")

    # check social account
    social_account = await SocialAccount.filter(acc_key=f"google#{user_sub}").first()
    if not social_account:
        profile = await get_google_profile(google_access_token)

        email_user = await User.filter(email=profile["email"]).exists()
        if email_user:
            raise exceptions.HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=EMAIL_EXISTED
            )
        user = User(email=profile["email"], avatar=profile["picture"], nickname=profile["name"])
        await user.save()
        social_account = await SocialAccount(
            provider="google", user=user, acc_key=f"google#{user_sub}", data=profile
        ).save()
    else:
        user = await User.filter(id=social_account.user_id).get()

    # Create Tokens
    access_token = Authorize.create_access_token(subject=user.id)
    refresh_token = Authorize.create_refresh_token(subject=user.id)

    # Set Cookies
    Authorize.set_access_cookies(access_token)
    Authorize.set_refresh_cookies(refresh_token)

    return LoginResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh")
async def refresh(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()

    signed_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=signed_user)
    Authorize.set_access_cookies(new_access_token)

    await User.filter(id=signed_user).update(last_logged_in=datetime.datetime.now())
    return {"access_token": new_access_token}


@router.delete("/logout")
def logout(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    Authorize.unset_jwt_cookies()
    return {"msg": "success"}


@router.post("/user")
async def get_user(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    signed_user = Authorize.get_jwt_subject()
    current_user = await User.filter(id=signed_user).first()
    return {"user": current_user}
