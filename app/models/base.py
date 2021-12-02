from pydantic import BaseModel


class GqlModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        orm_mode = True
