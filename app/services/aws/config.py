import aioboto3
from app.core.config import get_app_settings

settings = get_app_settings()

session = aioboto3.Session(
    aws_access_key_id=settings.AWS_ACCESS_KEY,
    aws_secret_access_key=settings.AWS_SECRET_KEY,
    region_name=settings.AWS_REGION,
)
