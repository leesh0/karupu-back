from fastapi import APIRouter, Depends, UploadFile
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel, HttpUrl

from app.core.config import get_app_settings
from app.resources.strings import CANNOT_VERIFY_TOKEN, EMAIL_EXISTED, EMAIL_NOT_VERIFIED
from app.services.aws.uploader import upload_images

settings = get_app_settings()
router = APIRouter()


class UploadResponse(BaseModel):
    imageUrl: HttpUrl


@router.post("/project_body_image")
async def upload_project_body_image(
    file: UploadFile, Authorize: AuthJWT = Depends()
) -> UploadResponse:
    image_base_url = f"https://{settings.AWS_S3_BUCKET}.s3.amazonaws.com/"
    Authorize.jwt_refresh_token_required()
    path = await upload_images([file])
    return UploadResponse(imageUrl=f"{image_base_url}{path[0]}")
