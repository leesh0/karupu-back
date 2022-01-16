import logging

from pydantic import PostgresDsn, SecretStr

from app.core.settings.app import AppSettings
from app.core.settings.base import AppEnvTypes


class TestAppSettings(AppSettings):
    debug: bool = True
    app_env: AppEnvTypes = AppEnvTypes.test

    title: str = "Test Karupu"

    secret_key: SecretStr = SecretStr("test_app_karupu")

    database_url: PostgresDsn
    max_connection_count: int = 5
    min_connection_count: int = 5

    logging_level = logging.DEBUG

    db_logging: bool = False

    class Config(AppSettings.Config):
        env_file = "dev.env"
