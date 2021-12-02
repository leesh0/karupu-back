from app.core.config import get_app_settings
from tortoise import Tortoise

settings = get_app_settings()

TORTOISE_ORM = {
    "connections": {"default": settings.database_url},
    "apps": {
        "models": {
            "models": ["app.db.table.karupu", "app.db.table.auth", "aerich.models"],
            "default_connection": "default",
        }
    },
}


async def init_db():
    await Tortoise.init(
        db_url=settings.database_url,
        modules={"models": ["app.db.table.karupu", "app.db.table.auth"]},
    )
    await Tortoise.generate_schemas()


async def close_db():
    await Tortoise.close_connections()
