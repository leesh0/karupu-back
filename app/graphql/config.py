from app.graphql.dependencies.authentication import AuthCookie
from app.graphql.loaders import contexts
from fastapi import Depends, Request, Response


class RequestInfo:
    def __init__(self, req: Request = None, res: Response = None):
        self.req = req


async def get_context(auth: AuthCookie = Depends(), request: RequestInfo = Depends()):
    return {"auth": auth, "depends": request, **contexts}
