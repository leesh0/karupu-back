from app.core.config import get_app_settings
from tortoise.contrib.fastapi import register_tortoise

settings = get_app_settings()


def db_register(app):
    return register_tortoise(
        app,
        db_url=settings.database_url,
        modules={"models": ["app.db.table.karupu", "app.db.table.auth"]},
        generate_schemas=True,
        add_exception_handlers=True,
    )
