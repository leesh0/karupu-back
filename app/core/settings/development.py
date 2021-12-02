import logging

from app.core.settings.app import AppSettings
from app.core.settings.base import AppEnvTypes


class DevAppSettings(AppSettings):
    app_env: AppEnvTypes = AppEnvTypes.dev
    debug: bool = True

    title: str = "Dev Karupu"

    logging_level: int = logging.DEBUG

    db_logging: bool = True

    class Config(AppSettings.Config):
        env_file = "dev.env"
