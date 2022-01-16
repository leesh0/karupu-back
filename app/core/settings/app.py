import logging
import sys
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger
from pydantic import PostgresDsn, SecretStr

from app.core.logging import InterceptDBHandler, InterceptHandler
from app.core.settings.base import BaseAppSettings


class AppSettings(BaseAppSettings):
    # settings for debug & openapi
    debug: bool = False
    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "Karupu API"
    version: str = "0.0.0"

    # settings for Database
    database_url: PostgresDsn
    max_connection_count: int = 10
    min_connection_count: int = 10

    # settings for URL
    api_prefix: str = "/api"

    # settings for AWS
    AWS_ACCESS_KEY: str
    AWS_SECRET_KEY: str
    AWS_REGION: str
    AWS_S3_BUCKET: str = "karupu"

    # settings for Authentication
    GOOGLE_CLIENT_ID: str
    GOOGLE_SECRET: str
    GOOGLE_URL: Optional[str] = None
    SECRET: SecretStr
    authjwt_secret_key: str
    authjwt_token_location: set = {"cookies"}
    authjwt_cookie_csrf_protect: bool = False

    # settings for CORS
    allowed_hosts: List[str] = ["*"]

    # settings for logger
    logging_level: int = logging.INFO
    loggers: Tuple[str, str] = ("uvicorn.asgi", "uvicorn.access")

    db_logging: bool = False
    db_logging_level: int = logging.DEBUG
    db_loggers: set = {"tortoise"}
    db_logging_fmt: logging.Formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    class Config:
        validate_assignment = True

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        return {
            "debug": self.debug,
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "version": self.version,
        }

    def configure_logging(self) -> None:
        logging.getLogger().handlers = [InterceptHandler()]
        for logger_name in self.loggers:
            logging_logger = logging.getLogger(logger_name)
            logging_logger.handlers = [InterceptHandler(level=self.logging_level)]

        if self.db_logging:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.DEBUG)
            handler.setFormatter(self.db_logging_fmt)
            for db_logger in self.db_loggers:
                logging_logger = logging.getLogger(db_logger)
                logging_logger.setLevel(logging.DEBUG)
                logging_logger.addHandler(handler)

        logger.configure(handlers=[{"sink": sys.stderr, "level": self.logging_level}])
