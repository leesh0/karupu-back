import asyncio
from io import BytesIO
from typing import IO, List, Sequence, Union
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from PIL import Image

from app.core.config import AppEnvTypes, get_app_settings
from app.services.aws.config import session

settings = get_app_settings()


AWS_BASE_URL = f"https://{settings.AWS_S3_BUCKET}.s3.amazonaws.com/"


def image_validator(file):
    file_max_size = 8 * 1e6  # 8mb
    if len(file.read()) > file_max_size:
        raise HTTPException(status_code=400, detail="file size over")
    try:
        Image.open(file).verify()
        return True
    except Exception:
        raise HTTPException(status_code=400, detail="no image")


def to_jpg(file):
    f = BytesIO()
    im = Image.open(file)
    rgb_im = im.convert("RGB")
    rgb_im.save(f, format="JPEG")
    f.seek(0)
    return f


async def to_io(file):
    f = BytesIO()
    f.write(await file.read())
    f.seek(0)
    return f


def get_s3_url(path):
    return f"https://{settings.AWS_S3_BUCKET}.s3.amazonaws.com/{path}"


async def upload_images(files: Sequence[Union[IO, UploadFile]], path="images"):
    base_url = f"https://{settings.AWS_S3_BUCKET}.s3.amazonaws.com/"

    async with session.client("s3") as s3:
        try:
            fnames = [f"{path}/{uuid4()}.{file.filename.split('.')[-1]}" for file in files]
            if settings.app_env != AppEnvTypes.prod:
                return [base_url + fname for fname in fnames]
            freads = await asyncio.gather(*[file.read() for file in files])
            upload_futures = [
                s3.upload_fileobj(
                    BytesIO(file),
                    "karupu",
                    name,
                )
                for name, file in zip(fnames, freads)
            ]
            await asyncio.gather(*upload_futures)

        except Exception as e:
            raise e

        return fnames


async def delete_images(urls: List[str]):
    async with session.client("s3") as s3:
        try:
            deletes = [s3.delete_object(Bucket="karupu", key=delete_key) for delete_key in urls]
            await asyncio.gather(*deletes)
        except Exception:
            pass

    return True
