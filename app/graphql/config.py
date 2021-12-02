from app.graphql.dependencies.authentication import AuthCookie
from app.graphql.loaders import contexts
from fastapi import Depends


async def get_context(auth: AuthCookie = Depends()):
    return {"auth": auth, **contexts}
