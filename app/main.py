from fastapi import Depends, FastAPI
from fastapi_jwt_auth import AuthJWT
from starlette.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from app.api.routes import authentication
from app.core.config import get_app_settings
from app.db.register import db_register
from app.graphql import schema
from app.graphql.config import get_context


def get_application() -> FastAPI:
    settings = get_app_settings()

    settings.configure_logging()

    application = FastAPI(**settings.fastapi_kwargs)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    graphql_app = GraphQLRouter(schema, context_getter=get_context)

    application.include_router(authentication.router, prefix="/auth")
    application.include_router(graphql_app, prefix="/graphql")
    application.add_websocket_route("/graphql", graphql_app)

    db_register(application)

    @AuthJWT.load_config
    def get_config():
        return settings

    return application


app = get_application()
