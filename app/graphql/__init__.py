from app.graphql.schemas import mutations, queries
from strawberry import Schema
from strawberry.tools import merge_types

queries = merge_types("KarupuQuery", queries)
mutations = merge_types("KarupuMutation", mutations)

schema = Schema(query=queries, mutation=mutations)
