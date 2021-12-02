import strawberry
from app.graphql.types import User
from strawberry.types import Info


@strawberry.type
class Query:
    @strawberry.field
    async def user(self, id: int, info: Info) -> User:
        return await info.context["user_loader"].load(id)
